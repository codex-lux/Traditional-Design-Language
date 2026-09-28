"""WHICH SIDE OF THE HOUSE A STACK STANDS ON (Phase 15, WP-15.8, the audit).

The elevation read a stack's relation to a face from the face's NAME: every exterior stack stood
"in front of" both long faces, and a stack at either long wall was "in the plane" of both. That was
true of every stack the corpus draws, which all stand at gable ends, and false of the one the placer
seats wherever a fire is stated. Auditor D moved the Tidewater dining fire to the rear (N) wall:

  the south front   drew the rear stack from grade to cap, through the house
  both gable faces  floated it at the eave past the corner, under "THEY STAND AT THE FAR END, SO
                    THE HOUSE HIDES THE REST", where nothing of the house stands in front of it

`elevation.stack_side` reads the wall off the square the placement seats and `stack_relation` says
how each face sees it. No shipped plan seats a stack on a long wall, so the case is DRIVEN, with the
premise asserted: the drive must seat a stack outboard of the rear wall.
"""
import json
import os
import re
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _L(n):
    return modcache.load(n, os.path.join(ROOT, "build", n + ".py"))


GEO, ST, RF, EL, RE = (_L(n) for n in ("geometry", "structure", "roof", "elevation",
                                       "render_elevation"))


def _elevation(plan):
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        placed = GEO.solve(plan, None, 250, engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved
    sec = ST.build_section(placed, None, geometry_result=placed)
    rf = RF.build_roof(placed, None, section=sec)
    return EL.build_elevation(placed, None, section=sec, roof=rf)


def _tidewater():
    with open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"), encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def shipped():
    return _elevation(_tidewater())


@pytest.fixture(scope="module")
def rear():
    """The dining room's stated fire moved to its N wall, on a flue of its own (auditor D's drive)."""
    plan = _tidewater()
    moved = 0
    for lv in plan["levels"]:
        for r in lv["rooms"]:
            if r["id"] == "dining":
                r["hearth"][0]["wall"] = "N"
                r["hearth"][0]["flue"] = "north-stack"
                moved += 1
    assert moved == 1, "the premise: the shipped record states the dining room's fire"
    el = _elevation(plan)
    fp = el["footprint"]
    north = [c for c in el["roof_record"]["chimneys"]["positions"]
             if EL.stack_side(c, fp) == "N"]
    assert len(north) == 1, ("the premise: the drive seats one stack outboard of the rear wall",
                             [c.get("plan_rect_ft") for c in el["roof_record"]["chimneys"]["positions"]])
    return el, north[0]


def _svg(el, face):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, f"{face}.svg")
        RE.render_elevation(el, out, face=face)
        return open(out, encoding="utf-8").read()


def _mark(el, face, stack):
    got = [mk for mk in EL.stack_marks(el, face)["marks"]
           if mk["stack"].get("plan_rect_ft") == stack.get("plan_rect_ft")]
    return got[0] if got else None


# ------------------------------------------------------------------ the reader
def test_the_side_is_read_off_the_square():
    fp = {"width_ft": 40.0, "depth_ft": 30.0}
    for rect, side in (([-2, 10, 0, 12], "W"), ([40, 10, 42, 12], "E"), ([10, -2, 12, 0], "S"),
                       ([10, 30, 12, 32], "N"), ([10, 10, 12, 12], "interior")):
        assert EL.stack_side({"plan_rect_ft": rect}, fp) == side, (rect, side)
    assert EL.stack_side({}, fp) is None


def test_each_face_sees_each_wall_one_way():
    for side in "NSEW":
        opp = {"N": "S", "S": "N", "E": "W", "W": "E"}[side]
        for face in "NSEW":
            want = "front" if face == side else "behind" if face == opp else "end"
            assert EL.stack_relation(face, side) == want, (face, side)
    assert EL.stack_relation("S", "interior") == EL.stack_relation("E", None) == "interior"


# ------------------------------------------------------------------ the shipped gable stacks
def test_a_gable_face_carries_its_own_stacks_axis_and_not_the_far_gables(shipped):
    """The Tidewater E and W faces each carried `[32.22, 32.22]`, the far gable's stack counted as
    standing in the near gable's plane. Each carries its own now, and a long face none."""
    fp = shipped["footprint"]
    positions = shipped["roof_record"]["chimneys"]["positions"]
    for face in "EW":
        own = [c for c in positions if EL.stack_side(c, fp) == face]
        assert own, ("the premise: a stack stands at the", face, "gable")
        assert len(shipped["faces"][face]["stack_axes_ft"]) == len(own), (
            face, shipped["faces"][face]["stack_axes_ft"])
    for face in "SN":
        assert shipped["faces"][face]["stack_axes_ft"] == [], face


# ------------------------------------------------------------------ the rear stack
def test_the_front_sees_the_rear_stack_above_the_ridge_only(rear):
    el, stack = rear
    mk = _mark(el, "S", stack)
    assert mk and not mk["from_grade"] and mk["relation"] == "behind", mk
    ridge = el["roof_record"]["main"]["ridge"]["grade_to_ridge_ft"]
    assert min(h for _u, h in mk["outline"]) == pytest.approx(ridge, abs=1e-6), mk["outline"]
    said = " ".join(_svg(el, "S").split())
    assert "THEY STAND BEHIND THE FAR WALL, SO THE HOUSE HIDES THEM UP TO THE RIDGE" in said


def test_its_own_wall_and_both_gables_see_it_from_the_ground(rear):
    el, stack = rear
    D = el["footprint"]["depth_ft"]
    for face, rel in (("N", "front"), ("E", "end"), ("W", "end")):
        mk = _mark(el, face, stack)
        assert mk and mk["from_grade"] and mk["relation"] == rel, (face, mk)
        assert min(h for _u, h in mk["outline"]) == 0.0, (face, mk["outline"])
        if face in "EW":
            # it stands beyond the corner, past the gable's own depth
            assert min(u for u, _h in mk["outline"]) >= D - 1e-6, (face, mk["outline"])
    said = " ".join(_svg(el, "E").split())
    assert "THEY STAND AT THE FAR END" not in said, "nothing of the house stands in front of it"


def test_a_stack_beside_the_face_is_drawn_behind_it_and_one_before_its_wall_in_front(rear):
    """The paint order follows the relation: a stack beyond the corner ("end") is drawn before the
    wall, so the face's projections at the corner stand over it; a stack in front of its own wall
    is drawn after it."""
    el, stack = rear
    assert _mark(el, "E", stack)["relation"] == "end"
    assert _mark(el, "N", stack)["relation"] == "front"
    for face in "EN":
        svg = _svg(el, face)
        wall = svg.index('class="wf"')
        polys = [m.start() for m in re.finditer(r'<polygon class="ch[ "]', svg)]
        marks = EL.stack_marks(el, face)["marks"]
        assert len(polys) == len(marks) >= 2, (face, len(polys), len(marks))
        want = sum(1 for mk in marks if mk["relation"] == "end")
        assert sum(p < wall for p in polys) == want, (face, want, polys, wall)


def test_no_front_window_is_refused_for_a_stack_forty_feet_behind_it(rear):
    el, stack = rear
    assert el["faces"]["S"]["stack_axes_ft"] == [], el["faces"]["S"]["stack_axes_ft"]
    assert not [x for x in EL.opening_rects(el, "S")["refused"] if x.get("cause") == "stack"]
    assert el["faces"]["N"]["stack_axes_ft"], "its own wall carries its axis"


# ------------------------------------------------------------------ the DXF, in the sheet's order
def test_the_dxf_draws_each_relation_in_the_sheets_order(rear):
    """The same four views in the CAD file (WP-15.8, commit 4). A stack beyond the corner is drawn
    before the wall, as the sheet paints it; one in front of its own wall after everything, over a
    mask of its own outline; one the house hides up to its ridge over nothing, with no mask. The
    shipped corpus seats no stack on a long wall, so the rear stack is the only place the long
    faces' two relations and the gables' "end" of a long-wall stack are drawn at all."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    DX = _L("export_dxf")
    el, stack = rear

    def _said(e):
        tags = [v for _c, v in e.get_xdata("TDL")]
        return json.loads("".join(tags[1:]))

    def _box(pts):
        return [round(f(p[i] for p in pts), 3) for i in (0, 1) for f in (min, max)]

    for face, rel in (("S", "behind"), ("N", "front"), ("E", "end"), ("W", "end")):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "e.dxf")
            assert "error" not in DX.export_elevation_dxf(el, path, face=face)
            msp = ezdxf.readfile(path).modelspace()
            at = {id(e): i for i, e in enumerate(msp)}
            (poly,) = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-STACK"
                       and _said(e).get("plan_rect_ft") == stack.get("plan_rect_ft")]
            said = _said(poly)
            assert said["relation"] == rel and said["from_grade"] == (rel != "behind"), (face, said)
            (wall,) = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-WALL"]
            assert (at[id(poly)] < at[id(wall)]) == (rel == "end"), (face, rel)
            own = [m for m in msp.query("WIPEOUT")
                   if _box([(v[0], v[1]) for v in m.boundary_path_wcs()]) == _box(poly.get_points())]
            assert len(own) == (1 if rel == "front" else 0), (face, rel, len(own))
            if own:
                later = [e for e in msp if e.dxf.layer not in ("TDL-ELEV-STACK", "TDL-ELEV-MASK",
                                                               "TDL-ELEV-ANNO")]
                assert max(at[id(e)] for e in later) < at[id(own[0])] < at[id(poly)], face
