"""THE IFC STANDS WHERE THE RECORD STANDS, AND CUTS THE OPENINGS THE PLAN SHEET DRAWS (audit, 27 Sep 2026).

Auditor D (F7), measured and reproduced: `export_ifc` spaced every declared window unit evenly along
its room's edge on the footprint's outer face and never read the placement -- over the twelve
drawable reference plans it cut 112 window units against the 57 the plan sheet draws, 55 of them
units the placer REFUSED -- and stood each interior door at the midpoint of `_shared`'s run, where a
door was drawn before WP-6.2: 10 of 84 somewhere the sheet does not draw them, the worst 4.23 ft
away. Writing the fix found a third: every opening box took its wall's thickness and stood on the
wall's INNER face, so it cut half the wall it was meant to pierce.

AND THEN A FOURTH, WHICH IS WHY EVERY POSITION HERE IS READ OFF THE PLACEMENT AND NOT THE PSET.
The first version of this file held the openings to the sheet through a `position_ft` property
the exporter writes beside each opening, and held each opening to its wall RELATIVE to the wall.
Both passed over a model in which every product stood at 3.2808 times its coordinate:
`geometry.edit_object_placement` reads its matrix as METRES by default and the exporter handed it
feet, so the Foyer of `spec-builder-colonial`, centred at (6.75, 27.72) ft, was written at
(22.13, 90.93). A property written from the same number as the placement agrees with the record
whatever the placement says, and a uniform scale cancels in any comparison of two placed things.
Every assertion below reads the ABSOLUTE placement, in the project's unit (feet), against the
record: the rooms, the storeys, and the windows and doors the sheet draws, each at its own place.

The premise that both window branches run -- some unit cut, some refused and carried as data -- is
asserted, because a sweep in which the placer refused nothing would not test the half of the fix
that matters most.
"""
import copy
import glob
import json
import os
import sys

import pytest

ios = pytest.importorskip("ifcopenshell", reason="COULD NOT EVALUATE: ifcopenshell is not installed")
import ifcopenshell.util.element as uel  # noqa: E402
import ifcopenshell.util.placement as upl  # noqa: E402
import ifcopenshell.util.unit as uun  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _L(n):
    return modcache.load(n, os.path.join(ROOT, "build", n + ".py"))


GEO, EI, RP, ST = _L("geometry"), _L("export_ifc"), _L("render_plan"), _L("structure")
PLANS = sorted(glob.glob(os.path.join(ROOT, "plans", "*.json"))
               + glob.glob(os.path.join(ROOT, "plans", "reference", "*.json")))
TOL = 0.01          # ft; every figure below is written at three decimals or better


@pytest.fixture(scope="module")
def models(tmp_path_factory):
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    out = {}
    try:
        for path in PLANS:
            with open(path, encoding="utf-8") as fh:
                plan = json.load(fh)
            placed = GEO.solve(copy.deepcopy(plan), None, 250, engine="heuristic")
            ifc = str(tmp_path_factory.mktemp("ifc") / "out.ifc")
            res = EI.export_ifc(copy.deepcopy(plan), ifc, geometry_result=placed)
            if "error" in res:
                continue
            sec = ST.build_section(copy.deepcopy(plan), None, geometry_result=placed)
            out[os.path.basename(path)[:-5]] = (placed, sec, ios.open(ifc))
    finally:
        GEO._SOLVE_CACHE = saved
    assert len(out) >= 10, sorted(out)
    return out


def _at(product):
    """The product's ABSOLUTE placement, in the project's own unit."""
    m = upl.get_local_placement(product.ObjectPlacement)
    return m[0][3], m[1][3], m[2][3]


def _z(sec):
    return {s["index"]: float(s["grade_to_floor_ft"]) for s in sec["storeys"]
            if s.get("grade_to_floor_ft") is not None}


def _levels(placed):
    for i, lv in enumerate(placed["levels"]):
        yield lv.get("index", i), RP.openings_of_level(placed, lv, i)


def test_the_model_is_in_feet(models):
    for pid, (_p, _s, g) in models.items():
        assert abs(uun.calculate_unit_scale(g) - 0.3048) < 1e-9, pid


def test_every_space_stands_on_its_rooms_own_rectangle(models):
    """The check that sees a scale: a room's centre is a number the record states outright."""
    n = 0
    for pid, (placed, sec, g) in sorted(models.items()):
        z = _z(sec)
        rooms = {(lv.get("index", i), r["id"]): r["geometry"]
                 for i, lv in enumerate(placed["levels"]) for r in lv["rooms"] if r.get("geometry")}
        for sp in g.by_type("IfcSpace"):
            ps = uel.get_psets(sp).get("TDL") or {}
            key = next((k for k in rooms if k[1] == ps.get("tdl_id")
                        and abs(z.get(k[0], 1e9) - _at(sp)[2]) < TOL), None)
            assert key, (pid, sp.Name, ps.get("tdl_id"), _at(sp))
            gm = rooms[key]
            x, y, _ = _at(sp)
            assert abs(x - (gm["x_ft"] + gm["width_ft"] / 2)) < TOL, (pid, sp.Name, x, gm)
            assert abs(y - (gm["y_ft"] + gm["depth_ft"] / 2)) < TOL, (pid, sp.Name, y, gm)
            n += 1
    assert n > 100


def test_every_storey_stands_at_its_own_elevation(models):
    """`Elevation` is written directly in the project unit; the placement went through the SI
    conversion. They are one number, and at 3.28 times they were two."""
    for pid, (_p, sec, g) in models.items():
        z = _z(sec)
        for s in g.by_type("IfcBuildingStorey"):
            assert abs(_at(s)[2] - s.Elevation) < TOL, (pid, s.Name, _at(s)[2], s.Elevation)
            assert any(abs(s.Elevation - v) < TOL for v in z.values()), (pid, s.Name)


def _unmatched(want, got):
    """Pair each expected (identity, x, y, z) with a placed one of the same identity within TOL,
    one to one. Rounding both to two places and comparing sets split a tie -- the sheet's 7.825
    against the model's 7.824999 -- so the comparison is by distance, never by a rounded key.
    Returns what is left over on each side."""
    got = list(got)
    left = []
    for w in want:
        i = next((i for i, g in enumerate(got) if g[0] == w[0]
                  and all(abs(a - b) < TOL for a, b in zip(g[1:], w[1:]))), None)
        if i is None:
            left.append(w)
        else:
            got.pop(i)
    return left, got


def _expected_windows(placed, sec):
    """Each window the sheet draws, at its place in the wall: along the wall at the sheet's
    `at_ft`, across it at the CENTRE of the exterior wall whose inner face is the sheet's
    `edge_ft` -- half the wall's thickness outward, the side the wall's own letter names."""
    t = sec["wall"]["exterior_in"] / 12.0
    z = _z(sec)
    out = []
    for idx, ops in _levels(placed):
        for w in ops["windows"]:
            across = w["edge_ft"] + (-t / 2 if w["wall"] in ("S", "W") else t / 2)
            x, y = (w["at_ft"], across) if w["wall"] in ("S", "N") else (across, w["at_ft"])
            out.append(((w["room"], w["wall"]), x, y, z[idx]))
    return out


def _ifc_windows(g, zs):
    cut, refused = [], 0
    for w in g.by_type("IfcWindow"):
        ps = uel.get_psets(w).get("TDL") or {}
        if ps.get("geometry_note"):
            refused += 1
            continue
        x, y, zz = _at(w)
        floor = max((v for v in zs if v <= zz + TOL), default=-1e9)
        cut.append(((ps["room"], ps["wall"]), x, y, floor))
    return cut, refused


def test_the_ifc_cuts_exactly_the_windows_the_sheet_draws_where_it_draws_them(models):
    cut = refused = 0
    for pid, (placed, sec, g) in sorted(models.items()):
        want = _expected_windows(placed, sec)
        got, n_ref = _ifc_windows(g, _z(sec).values())
        missing, extra = _unmatched(want, got)
        assert not missing and not extra, (pid, "sheet draws, model does not:", missing[:4],
                                           "model cuts, sheet does not:", extra[:4])
        cut += len(got)
        refused += n_ref
    assert cut > 0 and refused > 0, ("the premise: some unit cut and some carried as data", cut, refused)


def test_the_ifc_hangs_the_interior_doors_the_sheet_hangs_where_it_hangs_them(models):
    n = 0
    for pid, (placed, sec, g) in sorted(models.items()):
        z = _z(sec)
        want = []
        for idx, ops in _levels(placed):
            for e in ops["interior"]:
                px, py = (e["pos_ft"], e["at_ft"]) if e["horiz"] else (e["at_ft"], e["pos_ft"])
                want.append((tuple(sorted(e["pair"])), px, py, z[idx]))
        got = []
        for d in g.by_type("IfcDoor"):
            ps = uel.get_psets(d).get("TDL") or {}
            if ps.get("geometry_note"):
                continue
            x, y, zz = _at(d)
            got.append((tuple(sorted((ps["room"], ps["to"]))), x, y, zz))
        missing, extra = _unmatched(want, got)
        assert not missing and not extra, (pid, "sheet hangs, model does not:", missing[:4],
                                           "model hangs, sheet does not:", extra[:4])
        n += len(got)
    assert n > 0


def test_every_opening_stands_on_its_wall_s_centreline(models):
    """The box takes its wall's thickness; standing on the inner face it cut half the wall. Read
    relative to the wall, which a uniform scale would not disturb -- the absolute tests above are
    what see the scale, and this one is what sees the half-wall."""
    n = 0
    for pid, (_placed, _sec, g) in sorted(models.items()):
        for op in g.by_type("IfcOpeningElement"):
            wall = op.VoidsElements[0].RelatingBuildingElement
            ps = uel.get_psets(wall).get("TDL") or {}
            across = 1 if ps.get("axis") == "y" else 0      # a y-axis wall runs along x
            assert abs(_at(op)[across] - _at(wall)[across]) < 1e-6, (pid, op.Name, ps.get("wall"))
            n += 1
    assert n > 0
