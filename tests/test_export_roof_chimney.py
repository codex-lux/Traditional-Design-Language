"""The roof DXF's chimney layer, read back (WP-14.6's second audit, W5).

WP-14.6 put one square under every stack -- `roof.py` carries the placement's own `plan_rect_ft`
and every surface draws it (census V17 and F1) -- and `export_dxf.export_roof_dxf` writes that
square to `TDL-ROOF-CHIMNEY` as a closed polyline, or a POINT where the record seats no square.
Nothing read the layer back. Measured before this file existed: writing every stack as a point,
and drawing an unseated stack as an 18 in circle nobody states, both left `tests/test_export.py`,
`tests/test_export_doors.py` and the census's DXF rows (X1, X2) green -- they read the ELEVATION's
DXF, and this is the ROOF's.

So the layer is held to the record it was written from:

- each seated stack is ONE closed polyline whose corners are its `plan_rect_ft`, in inches, to
  0.05 in;
- a stack the record seats on no square is a POINT at its own position, and never a shape;
- nothing on the layer is a CIRCLE, because no record states a round stack.

Without `ezdxf` the exporter refuses (`export_dxf.REFUSAL`) and every test here is SKIPPED, which is
COULD NOT EVALUATE and not a pass -- the skip names the library.
"""
import copy
import json
import os
import sys

import pytest

ezdxf = pytest.importorskip("ezdxf", reason="the roof DXF cannot be written or read without ezdxf")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache as mc  # noqa: E402

LAYER = "TDL-ROOF-CHIMNEY"
TOL_IN = 0.05


def _m(name):
    return mc.load(name, os.path.join(ROOT, "build", name + ".py"))


@pytest.fixture(scope="module")
def roof():
    """The Tidewater record's roof, built on its own placement the way the census builds it."""
    G, ST, RF = _m("geometry"), _m("structure"), _m("roof")
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    placed = G.solve(copy.deepcopy(plan), engine="heuristic")
    sec = ST.build_section(placed, None, geometry_result=placed)
    assert "error" not in sec, sec
    rf = RF.build_roof(placed, None, section=sec)
    assert "error" not in rf, rf
    return rf


def _positions(rf):
    return ((rf.get("chimneys") or {}).get("positions")) or []


def _layer(rf, tmp_path, name="roof.dxf"):
    path = str(tmp_path / name)
    got = _m("export_dxf").export_roof_dxf(rf, path)
    assert not (isinstance(got, dict) and got.get("error")), got
    return [e for e in ezdxf.readfile(path).modelspace() if e.dxf.layer == LAYER]


def _corners(rect_ft):
    x0, y0, x1, y1 = rect_ft
    return sorted((round(x * 12.0, 3), round(y * 12.0, 3)) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


def _matches(poly, rect_ft):
    pts = sorted((p[0], p[1]) for p in poly.get_points("xy"))
    want = _corners(rect_ft)
    return len(pts) == 4 and all(abs(a[0] - b[0]) <= TOL_IN and abs(a[1] - b[1]) <= TOL_IN
                                 for a, b in zip(pts, want))


def test_the_premise_the_record_seats_its_stacks_on_squares(roof):
    seated = [c for c in _positions(roof) if c.get("stack_plan_in") and c.get("plan_rect_ft")]
    assert len(seated) >= 2, (
        "the premise: the Tidewater roof seats at least two stacks on the placement's own squares "
        "(%s); if it seats none, this file reads nothing and must be re-pointed at a record that does"
        % _positions(roof))


def test_each_seated_stack_is_one_closed_square_at_its_own_plan_rect(roof, tmp_path):
    ents = _layer(roof, tmp_path)
    assert len(ents) == len(_positions(roof)), (
        "%d entities on %s for %d stacks: one mark per stack" % (len(ents), LAYER, len(_positions(roof))))
    polys = [e for e in ents if e.dxftype() == "LWPOLYLINE"]
    assert all(p.closed for p in polys), "a stack's square is drawn open"
    for c in _positions(roof):
        if not (c.get("stack_plan_in") and c.get("plan_rect_ft")):
            continue
        hits = [p for p in polys if _matches(p, c["plan_rect_ft"])]
        assert len(hits) == 1, (
            "the stack on %s is drawn by %d closed polyline(s) at its corners %s, not one; the layer "
            "holds %s" % (c["plan_rect_ft"], len(hits), _corners(c["plan_rect_ft"]),
                          [sorted(p.get_points("xy")) for p in polys]))


def test_nothing_on_the_layer_is_a_circle(roof, tmp_path):
    kinds = sorted({e.dxftype() for e in _layer(roof, tmp_path)})
    assert "CIRCLE" not in kinds, kinds


def test_a_stack_seated_on_no_square_is_a_point_at_its_own_position(roof, tmp_path):
    """DRIVEN: every stack the corpus's roofs draw today is seated, so the point branch is reached
    by nothing shipped. One position loses its square; it must be written as a POINT where the
    record puts the stack -- never a shape of a size no record states -- and its seated neighbour
    must still be its square."""
    rf = copy.deepcopy(roof)
    pos = _positions(rf)
    assert len(pos) >= 2 and all(c.get("plan_rect_ft") for c in pos), "the premise: every stack is seated"
    lost = pos[0]
    del lost["plan_rect_ft"]
    ents = _layer(rf, tmp_path, "unseated.dxf")
    kinds = sorted(e.dxftype() for e in ents)
    assert "CIRCLE" not in kinds, kinds
    points = [e for e in ents if e.dxftype() == "POINT"]
    assert len(points) == 1, kinds
    x, y = points[0].dxf.location[0], points[0].dxf.location[1]
    assert abs(x - lost["x_ft"] * 12.0) <= TOL_IN and abs(y - lost["y_ft"] * 12.0) <= TOL_IN, (
        (x, y), (lost["x_ft"] * 12.0, lost["y_ft"] * 12.0))
    polys = [e for e in ents if e.dxftype() == "LWPOLYLINE"]
    assert len(polys) == len(pos) - 1 and all(
        any(_matches(p, c["plan_rect_ft"]) for p in polys) for c in pos[1:]), kinds
