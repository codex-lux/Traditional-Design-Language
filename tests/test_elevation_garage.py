"""A garage door is drawn as its opening, and no surface dresses it as the entrance (WP-14.3).

Census V6 found a 192 in garage door drawn as six raised panels. Chasing it found the panels were
the smaller half. `opening_rects` never carried the door's `type`, so the renderer's garage branch
could not fire. And on THREE reference plans (bad-02, bad-03, bad-07) the garage door is the
widest door on the entrance front, so it was the rect carrying `entrance`. The SVG, the DXF and
the scene each composed a Gibbs doorcase, two sidelights and a transom around it.

Every figure here is read off the plan record and off the drawn output, never off the elevation
record's own account of what it drew.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache as mc  # noqa: E402
import inkread as IR  # noqa: E402


def _m(name):
    return mc.load(name, os.path.join(ROOT, "build", name + ".py"))


PID = "bad-03-narrow-lot-townhome"


@pytest.fixture(scope="module")
def built():
    G, ST, RF, EL = _m("geometry"), _m("structure"), _m("roof"), _m("elevation")
    plan = json.load(open(os.path.join(ROOT, "plans", "reference", PID + ".json")))
    placed = G.solve(copy.deepcopy(plan), engine="heuristic")
    sec = ST.build_section(placed, None, geometry_result=placed)
    rf = RF.build_roof(placed, None, section=sec)
    el = EL.build_elevation(placed, None, section=sec, roof=rf)
    return plan, placed, sec, rf, el


def _garage(el):
    EL = _m("elevation")
    face = el["entrance_face"]
    return face, [r for r in EL.opening_rects(el, face)["rects"] if r["kind"] == "door"]


def test_the_premise_the_garage_door_is_the_entrance_on_this_plan(built):
    """If this plan grows a front door, every test below is about nothing; say so."""
    plan, _p, _s, _r, el = built
    stated = [d for lv in plan["levels"] for r in lv["rooms"] for d in r.get("doors") or []
              if d.get("to") == "exterior"]
    assert [d.get("type") for d in stated] == ["garage"], stated
    face, doors = _garage(el)
    assert [bool(r.get("entrance")) for r in doors] == [True]


def test_the_rect_carries_the_type_the_plan_states(built):
    _plan, _p, _s, _r, el = built
    _face, doors = _garage(el)
    assert doors[0]["type"] == "garage"


def test_the_plate_draws_the_opening_and_nothing_a_doorcase_is_made_of(built, tmp_path):
    _plan, _p, _s, _r, el = built
    RE = _m("render_elevation")
    face, doors = _garage(el)
    out = str(tmp_path / "e.svg")
    RE.render_elevation(el, out, face=face)
    ink = IR.Ink(open(out).read())
    pl = next(f for f in ink.frames() if f.get("proj") == "elevation")
    gx0 = IR.from_model(pl, doors[0]["x0_in"] / 12.0, 0)[0]
    gx1 = IR.from_model(pl, doors[0]["x1_in"] / 12.0, 0)[0]
    gyb = IR.from_model(pl, 0, doors[0]["sill_in"] / 12.0)[1]
    gyt = IR.from_model(pl, 0, doors[0]["head_in"] / 12.0)[1]

    def at_the_door(cls):
        """Rects of `cls` whose foot is the door's sill or head: what a doorcase, a sidelight
        and a transom stand on. An upper-storey window over the door stands on neither."""
        n = 0
        for it in ink.select("rect"):
            if cls not in it.classes:
                continue
            x, _y0, _x1, foot = it.bbox()
            if gx0 - 60 <= x <= gx1 + 60 and (abs(foot - gyb) < 0.6 or abs(foot - gyt) < 0.6):
                n += 1
        return n

    # the door is drawn, as its opening
    assert at_the_door("dr") == 1
    # no panels, no casing and no sidelight or transom glass around it
    # INSIDE THE LEAF, in both axes: the shutters of the window over the door carry panels of
    # the same class, and a census counting by x alone read them as the door's (WP-14.3)
    assert not [it for it in ink.select("rect") if "pnl" in it.classes
                and gx0 - 0.5 <= it.bbox()[0] and it.bbox()[2] <= gx1 + 0.5
                and gyt - 0.5 <= it.bbox()[1] and it.bbox()[3] <= gyb + 0.5], (
        "a garage door was drawn as a panelled leaf")
    # and the premise that makes the line above mean something: panels ARE drawn on this sheet,
    # so a selector that matched nothing would not pass for a door drawn plain
    assert [it for it in ink.select("rect") if "pnl" in it.classes]
    assert at_the_door("cs") == 0, "a doorcase was drawn around a garage door"
    assert at_the_door("op") == 0, "sidelight or transom glass was drawn beside a garage door"
    said = " ".join(t for t, _a, _i in ink.texts()).upper()
    assert "GARAGE DOOR DRAWN AS ITS OPENING" in said
    assert "ONLY DOOR IS A GARAGE DOOR" in said


def test_the_dxf_draws_what_the_plate_draws(built, tmp_path):
    ezdxf = pytest.importorskip("ezdxf")
    _plan, _p, _s, _r, el = built
    DX = _m("export_dxf")
    face, doors = _garage(el)
    path = str(tmp_path / "e.dxf")
    DX.export_elevation_dxf(el, path, face=face)
    x0, x1 = doors[0]["x0_in"], doors[0]["x1_in"]
    sill, head = doors[0]["sill_in"], doors[0]["head_in"]
    near = []
    for e in ezdxf.readfile(path).modelspace():
        if e.dxftype() == "LWPOLYLINE":
            xs, ys = zip(*[p[:2] for p in e.get_points("xy")])
            box = (min(xs), max(xs), min(ys), max(ys))
            if box == (x0, x1, sill, head):
                continue                                   # the door's own opening
            # a casing and a sidelight stand on the door's sill, a transom on its head
            if (x0 - 48 <= box[0] and box[1] <= x1 + 48
                    and (abs(box[2] - sill) < 0.5 or abs(box[2] - head) < 0.5)):
                near.append((e.dxf.layer,) + box)
    assert not near, ("the CAD file draws a doorcase, sidelight or transom above a garage door "
                      "the plate draws as its opening: %r" % near[:4])


def test_the_scene_refuses_the_doorcase_and_says_why(built):
    _plan, placed, sec, rf, el = built
    SC = _m("scene")
    scene = SC.build_scene(placed, sec, rf, el)
    assert not [s for s in scene["solids"] if s["class"] in ("surround", "entablature")]
    cannot = [c for c in scene["not_modelled"] if c["what"] == "the doorcase"]
    assert cannot and "garage door" in cannot[0]["why"]


def test_the_scene_dresses_the_door_carrying_entrance_and_not_the_first_door():
    """DRIVEN. On every shipped plan the entrance is the first door `opening_rects` emits on its
    face, so a function taking the first door and one taking the flagged door agree and neither
    is tested. A hand-built pair puts a back door first."""
    SC, EL = _m("scene"), _m("elevation")
    got = {}
    real = EL.opening_rects
    assert SC._mod("elevation") is EL, "the patch must reach the module the scene holds"

    def fake(elev, face):
        return {"rects": [
            {"id": "S-0-ground-back-door", "kind": "door", "storey": "ground", "entrance": None,
             "type": "swing", "x0_in": 12.0, "x1_in": 48.0, "sill_in": 24.0, "head_in": 104.0},
            {"id": "S-1-ground-front-door", "kind": "door", "storey": "ground",
             "entrance": {"x": 1}, "type": "swing",
             "x0_in": 200.0, "x1_in": 242.0, "sill_in": 24.0, "head_in": 104.0}],
            "refused": []}

    EL.opening_rects = fake
    try:
        states = SC._States()
        elev = {"entrance_face": "S", "entrance": {"casing_width_in": 6.0,
                                                   "entablature_height_in": 12.0,
                                                   "entablature_members": [],
                                                   "transom": {"drawn": False}}}
        section = {"footprint": {"width_ft": 40.0, "depth_ft": 30.0},
                   "wall": {"exterior_in": 12.0}, "storeys": [{"id": "ground", "index": 0}]}
        got["ids"] = [s["id"] for s in SC._entrance(elev, section, states)]
    finally:
        EL.opening_rects = real
    # the surround is drawn, so the function reached its door -- and it is the flagged one
    assert "S-1-ground-front-door-surround" in got["ids"], got
    assert not [i for i in got["ids"] if "back-door" in i], got
