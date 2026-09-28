"""THE WALL BESIDE THE ENTRANCE DOORCASE (Phase 15, WP-15.6).

Lucas, of the drawn Tidewater front (27 Sep 2026): "there's still no concept of how close windows can
be to doors". The placer reserved the entrance door's LEAF and a foot either side and nothing else;
the elevation then drew the doorcase round that leaf -- the casing each side, and the sidelights where
they fit -- so the centre passage's south window stood 12 in from the leaf and 4.98 in from the
casing, and the sidelights that would have stood there were refused for standing over it.
facade-classical states two sentences about exactly this, in its rule for the entrance composition's
width: "It is not allowed to touch the flanking windows", and "The residual wall each side of the
entrance composition should not fall below about half the ordinary pier".

`build/doorcase.py` is the one spelling of the composition's width, which door is the entrance, the
bay a parti states and the floor; the placer reserves the run and its floor before it seats a window
(`openings._reserve_doorcase`), and the elevation measures the wall it draws and says what it could
not judge (`elevation.doorcase_piers`, `doorcase_pier_notes`). These tests hold the placer's run to the
elevation's drawn doorcase, the transcribed fraction to the pack's sentence, and each verdict to a
state it is driven into -- no shipped plan reaches `short` or `touches` any more, which is the fix.

Expectations are derived from the records and the pack, never written as room names or positions.
"""
import copy
import glob
import json
import os
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _L(n):
    return modcache.load(n, os.path.join(ROOT, "build", n + ".py"))


GEO, ST, RF, EL, RE, OP, DC, PE = (_L(n) for n in (
    "geometry", "structure", "roof", "elevation", "render_elevation", "openings", "doorcase",
    "proportion_engine"))

RULE_SENTENCES = ("It is not allowed to touch the flanking windows",
                  "should not fall below about half the ordinary pier")


def _plans():
    return (sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))
            + sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))))


def _solve(path):
    with open(path, encoding="utf-8") as fh:
        plan = json.load(fh)
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        return GEO.solve(plan, None, 250, engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved


def _elevation(placed):
    sec = ST.build_section(placed, None, geometry_result=placed)
    if "error" in sec:
        return None
    rf = RF.build_roof(placed, None, section=sec)
    if "error" in rf:
        return None
    el = EL.build_elevation(placed, None, section=sec, roof=rf)
    if "error" in el or not el.get("applicable", True):
        return None
    return el


@pytest.fixture(scope="module")
def corpus():
    out = {}
    for p in _plans():
        placed = _solve(p)
        out[os.path.basename(p)[:-5]] = (placed, _elevation(placed))
    assert len(out) == 16, "the premise: the sixteen shipped plans"
    return out


def _svg(el, face):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, f"{face}.svg")
        RE.render_elevation(el, out, face=face)
        return open(out, encoding="utf-8").read()


def _said(svg):
    import re
    return [" ".join(t.split()) for t in re.findall(r'<text class="dm"[^>]*>([^<]*)</text>', svg)]


def _composition_rule():
    fac = PE.resolve("facade-classical")
    return next(r for r in fac["derived_rules"] if r["target_slot"] == "door_surround"
                and r.get("dimension") == "entrance_composition_total_width")


def _ordinary_pier_in(bay_ft, window_in):
    """The ordinary pier, read out of the pack HERE -- `module - opening_width` at one bay -- so the
    floor these tests expect is not the function they test."""
    fac = PE.resolve("facade-classical")
    rule = next(r for r in fac["derived_rules"] if r["target_slot"] == "window_grouping_rule"
                and r.get("dimension") == "pier_width")
    env = dict(PE.DEFAULT_BINDINGS, module=bay_ft * 12.0, opening_width=window_in)
    return float(PE.evaluate_expr(rule["expression"], env))


# ------------------------------------------------------------------ the rule, as the pack states it
def test_the_fraction_is_the_packs_own_sentence():
    rule = _composition_rule()
    words = " ".join(str(rule.get(k) or "") for k in ("authority_note", "note"))
    for s in RULE_SENTENCES:
        assert s in words, (s, "facade-classical no longer says this; re-read the pack")
    # "about half": the one prose figure, transcribed once in the leaf
    assert DC.RESIDUAL_FRACTION_OF_THE_ORDINARY_PIER == 0.5


def test_the_floor_is_half_the_ordinary_pier_at_the_windows_own_width():
    fac = PE.resolve("facade-classical")
    for bay, w in ((9.0, 42.0), (9.0, 36.0), (12.17, 42.0)):
        got = DC.residual_pier_ft(fac, bay, w / 12.0) * 12.0
        assert got == pytest.approx(0.5 * _ordinary_pier_in(bay, w), abs=1e-9), (bay, w)
    # and the two widths differ, so a floor read at the wrong width cannot pass by coincidence
    assert DC.residual_pier_ft(fac, 9.0, 3.5) != DC.residual_pier_ft(fac, 9.0, 3.0)


def test_a_bay_is_judged_only_where_a_parti_states_it():
    rec = {"footprint": {"bay_module_ft": 9.0},
           "geometry_report": {"bay_module": {"ft": 9.0, "stated_by": "centre-passage-double-pile"}}}
    assert DC.stated_bay_ft(rec) == (9.0, None)
    default = copy.deepcopy(rec)
    default["geometry_report"]["bay_module"]["stated_by"] = None
    assert DC.stated_bay_ft(default) == (None, DC.UNSTATED_BAY)
    silent = copy.deepcopy(rec)
    del silent["geometry_report"]["bay_module"]
    bay, why = DC.stated_bay_ft(silent)
    assert bay is None and "does not say who states" in why
    none = {"footprint": {}, "geometry_report": rec["geometry_report"]}
    bay, why = DC.stated_bay_ft(none)
    assert bay is None and "states no bay module" in why


# ------------------------------------------------------------------ the placer and the elevation agree
def test_the_placer_reserves_the_door_the_elevation_dresses(corpus):
    reserved = 0
    for pid, (placed, el) in corpus.items():
        rec = (placed.get("opening_report") or {}).get("doorcase")
        assert rec is not None, (pid, "the placer states a verdict on every placed plan")
        if el is None:
            assert not rec["reserved"], (pid, "no elevation is drawn, so no doorcase is reserved")
            continue
        face = el["entrance_face"]
        ents = [p for p in el["faces"][face]["placed"] if p.get("entrance")]
        dressed = [p for p in ents if "garage" not in str(p.get("type") or "").lower()]
        if not dressed:
            assert not rec["reserved"], (pid, rec)
            if ents:
                assert "garage" in rec["why"], (pid, rec["why"])
            continue
        assert rec["reserved"], (pid, rec)
        reserved += 1
        (p,) = dressed
        assert (rec["room"], rec["wall"]) == (p["room"], face), (pid, rec, p)
        assert rec["position_ft"] == pytest.approx(p["along_ft"], abs=1e-3), (pid, rec, p)
    assert reserved >= 2, "the premise: both shipped reference plans dress a doorcase"


def test_the_reserved_run_is_the_doorcase_the_elevation_draws(corpus):
    """The placer composes the run from the same leaf and `doorcase.composition` the elevation
    draws it with; held here through their OUTPUTS -- the run on the placer's record against the
    drawn outline in the face's own frame -- so a placer that left out the sidelights, or read a
    different leaf, is caught by the drawing and not by re-reading the arithmetic."""
    seen = 0
    for pid, (placed, el) in corpus.items():
        rec = (placed.get("opening_report") or {}).get("doorcase") or {}
        if not rec.get("reserved"):
            continue
        got = EL.doorcase_piers(el, rec["wall"])
        assert got, (pid, "a reserved doorcase is a drawn one")
        t_in = el["section"]["wall"]["exterior_in"]
        lo, hi = (v * 12.0 + t_in for v in rec["run_ft"])
        assert got["doorcase_in"][0] == pytest.approx(lo, abs=0.05), (pid, got["doorcase_in"], lo)
        assert got["doorcase_in"][1] == pytest.approx(hi, abs=0.05), (pid, got["doorcase_in"], hi)
        seen += 1
    assert seen >= 2


def test_no_window_is_seated_inside_the_run_or_its_floor(corpus):
    """Every placed window on the entrance wall stands clear of the run by the floor where the bay
    is stated, and by the placer's own solid where it is not -- in EVERY room on that wall.

    It read only the rooms the RUN touches until WP-15.8, and so could not see the defect it was
    written against one room over: the floor reaches past the run into the next room's wall, and
    the placer had recorded only the rooms the run touched (`test_the_floor_reaches_the_window_in_
    the_next_room`).

    AND IT STILL CANNOT SEE THAT DEFECT ON THE SHIPPED CORPUS, which the sentence above implied it
    could (the audit of WP-15.8's own diff, auditor G): with the placer's fix reverted this sweep
    stays green, because no shipped window on a flanking room stands within the floor's reach.
    It is a property check over what ships; the driven test named above is the one that holds the
    fix."""
    fac = PE.resolve("facade-classical")
    checked = 0
    for pid, (placed, _el) in corpus.items():
        rec = (placed.get("opening_report") or {}).get("doorcase") or {}
        if not rec.get("reserved"):
            continue
        bay, _why = DC.stated_bay_ft(placed)
        lo, hi = rec["run_ft"]
        for lv in placed["levels"]:
            if lv.get("index", 0) != 0:
                continue
            for r in lv["rooms"]:
                for w in r.get("windows") or []:
                    if w.get("wall") != rec["wall"]:
                        continue
                    width = w.get("width_ft") or 3.0
                    need = OP.MIN_SOLID_FT
                    if bay:
                        need = max(need, DC.residual_pier_ft(fac, bay, width))
                    for c in w.get("positions_ft") or []:
                        clear = max(lo - (c + width / 2), (c - width / 2) - hi)
                        assert clear >= need - 1e-6, (pid, r["id"], c, clear, need)
                        checked += 1
    assert checked >= 1, "the premise: a window stands beside a reserved doorcase"


def test_the_tidewater_passage_window_keeps_half_the_ordinary_pier(corpus):
    """The case Lucas saw. 4.98 in on the parent of this package; the floor is half of one 9 ft bay
    less the window's own 42 in, read out of the pack here."""
    placed, el = corpus["tidewater-georgian-careful"]
    got = EL.doorcase_piers(el, el["entrance_face"])
    judged = [s for s in got["sides"] if s["verdict"] not in ("not_applicable",)]
    assert judged, got
    bay, _ = DC.stated_bay_ft(placed)
    assert bay, "the premise: the Tidewater parti states its bay"
    for s in judged:
        floor = 0.5 * _ordinary_pier_in(bay, s["neighbour"]["width_in"])
        assert s["verdict"] == "agrees", s
        assert s["floor_in"] == pytest.approx(floor, abs=1e-3), (s, floor)
        assert s["clear_in"] >= floor - EL.PIER_TOL_IN, (s, floor)
    # and the sidelights the window used to stand on are drawn again
    rects = EL.opening_rects(el, el["entrance_face"])["rects"]
    (ent,) = [r for r in rects if r.get("entrance")]
    assert ent.get("sidelights_drawn") and not ent.get("sidelights_refused"), ent


def test_a_window_with_no_run_left_beside_the_doorcase_is_refused_by_name():
    """DRIVEN: a room whose entrance wall holds the doorcase and nothing else. The window is not
    narrowed or moved past the room: it is unplaced, and the reason names the doorcase."""
    room = {"id": "hall", "geometry": {"x_ft": 0.0, "y_ft": 0.0, "width_ft": 9.0, "depth_ft": 12.0},
            "windows": [{"wall": "S", "count": 1, "width_ft": 3.0}]}
    report = {"windows_placed": 0, "windows_unplaced": 0}
    dc = {"wall": "S", "lo": 2.0, "hi": 7.0, "rooms": {"hall"}, "bay_ft": None, "facade_pack": None}
    OP._place_windows([room], {}, 30.0, 30.0, report, doorcase=dc)
    win = room["windows"][0]
    assert win.get("unplaced") and "the entrance doorcase" in win["unplaced"]["reason"], win
    assert report["windows_unplaced"] == 1 and report["windows_placed"] == 0
    # the control: the same room with no doorcase seats the window
    room2 = copy.deepcopy(room)
    room2["windows"][0].pop("unplaced", None)
    report2 = {"windows_placed": 0, "windows_unplaced": 0}
    OP._place_windows([room2], {}, 30.0, 30.0, report2)
    assert report2["windows_placed"] == 1, room2


def _flanked(parlor_w, third=None, win_w=3.5, rear=False):
    """An 8 ft hall whose entrance door stands at 4 ft, a parlor `parlor_w` wide beside it on the
    same face with a window `win_w` wide, optionally a third room further along (auditor M's probe,
    WP-15.8), and optionally a window in the hall's own rear (N) wall."""
    hall = {"id": "hall", "geometry": {"x_ft": 0.0, "y_ft": 0.0, "width_ft": 8.0, "depth_ft": 16.0},
            "doors": [{"to": "exterior", "wall": "S", "position_ft": 4.0, "width_ft": 3.5}]}
    if rear:
        hall["windows"] = [{"wall": "N", "count": 1, "width_ft": 3.0}]
    parlor = {"id": "parlor",
              "geometry": {"x_ft": 8.0, "y_ft": 0.0, "width_ft": parlor_w, "depth_ft": 16.0},
              "windows": [{"wall": "S", "count": 1, "width_ft": win_w}]}
    rooms, W = [hall, parlor], 8.0 + parlor_w
    if third:
        rooms.append({"id": "closet",
                      "geometry": {"x_ft": W, "y_ft": 0.0, "width_ft": third, "depth_ft": 16.0},
                      "windows": [{"wall": "S", "count": 1, "width_ft": 3.5}]})
        W += third
    plan = {"style": "tidewater-georgian", "context": {"entrance_faces": "S"},
            "levels": [{"index": 0, "floor_to_ceiling_ft": 11.0, "rooms": rooms}],
            "footprint": {"bay_module_ft": 9.0},
            "geometry_report": {"bay_module": {"ft": 9.0, "stated_by": "a-parti"}}}
    envs = {r["id"]: (0.0, 0.0, W, 16.0) for r in rooms}
    report = {"windows_placed": 0, "windows_unplaced": 0}
    dc = OP._reserve_doorcase(plan, rooms, W, 16.0, envs, report, 0)
    OP._place_windows(rooms, {}, W, 16.0, report, envs, doorcase=dc)
    return report, {r["id"]: r for r in rooms}


def test_the_floor_reaches_the_window_in_the_next_room():
    """DRIVEN (WP-15.8): the keep-out is the doorcase run PLUS half the ordinary pier, so it reaches
    past the run into the next room's wall. The placer recorded only the rooms the RUN touched and
    seated this parlor's sash 11.95 in from the doorcase against a floor of 33 in. A parlor too
    narrow to hold its window clear of the floor refuses it by name; a wide one seats it clear."""
    floor_ft = 0.5 * _ordinary_pier_in(9.0, 42.0) / 12.0
    report, rooms = _flanked(4.5)
    rec = report["doorcase"]
    assert rec["rooms_touched"] == ["hall"] and rec["run_ft"][1] < 8.0, \
        ("the premise: the run itself stops short of the parlor", rec)
    w = rooms["parlor"]["windows"][0]
    assert w.get("unplaced") and not w.get("positions_ft"), w
    assert "the entrance doorcase" in w["unplaced"]["reason"], w
    report, rooms = _flanked(9.0)
    (c,) = rooms["parlor"]["windows"][0]["positions_ft"]
    clear = (c - 1.75) - report["doorcase"]["run_ft"][1]
    assert clear >= floor_ft - 1e-6, (clear * 12.0, floor_ft * 12.0)


def test_a_room_the_band_does_not_reach_is_not_told_the_doorcase_took_its_wall():
    """The control for the widening: a room further down the face, whose wall is too short for its
    window, is refused for that and not for a doorcase whose band ends in the parlor."""
    _report, rooms = _flanked(9.0, third=2.5)
    w = rooms["closet"]["windows"][0]
    assert w.get("unplaced") and "doorcase" not in w["unplaced"]["reason"], w
    assert w["unplaced"]["reason"] == "the wall is shorter than the window", w


def test_the_floor_is_taken_at_the_windows_own_width_and_not_the_door_leafs():
    """D03 (WP-15.8's audit, auditor M): the residual floor taken at the DOOR LEAF's width passed,
    because every judged doorcase in the corpus has a 42 in leaf beside a 42 in window. Driven with a
    30 in window: half the ordinary pier is 39 in at its own width and 33 in at the leaf's, and the
    placer seats the window against the band, so a floor taken at the wrong width seats it 6 in
    nearer than the rule allows."""
    own = 0.5 * _ordinary_pier_in(9.0, 30.0)
    leafs = 0.5 * _ordinary_pier_in(9.0, 42.0)
    assert own - leafs > 5.0, ("the premise: the two widths ask for different floors", own, leafs)
    report, rooms = _flanked(6.0, win_w=2.5)
    (c,) = rooms["parlor"]["windows"][0]["positions_ft"]
    clear_in = ((c - 1.25) - report["doorcase"]["run_ft"][1]) * 12.0
    assert clear_in >= own - 1e-3, (clear_in, own, leafs)


def test_the_keep_out_is_on_the_entrance_wall_and_no_other():
    """D01 (auditor M): the band applied on every wall of a room the doorcase touches passed. The
    hall's own rear window stands on the N wall, well inside the band's run along the face, and is
    seated; the band is a statement about the entrance wall only."""
    report, rooms = _flanked(9.0, rear=True)
    assert "hall" in report["doorcase"]["rooms_touched"], report["doorcase"]
    w = rooms["hall"]["windows"][0]
    assert w.get("positions_ft") and not w.get("unplaced"), w


def test_a_door_on_another_elements_face_is_not_the_entrance():
    """DRIVEN: no shipped plan sets a wing within the placer's 0.6 ft of the main front, so the
    elevation's element test decides nothing on the corpus. A wing set back 0.3 ft carries a door
    wider than the main block's: the elevation refuses it as another element's (its face is 0.3 ft
    off the main block's, against 0.01), so the placer must not dress it either. The control is the
    same wing built flush with the front, which is on the main block's face by the elevation's own
    test and is dressed by both."""
    def plan_with(wing_y):
        hall = {"id": "hall", "geometry": {"x_ft": 0.0, "y_ft": 0.0, "width_ft": 24.0, "depth_ft": 16.0},
                "doors": [{"to": "exterior", "wall": "S", "position_ft": 12.0, "width_ft": 3.5}]}
        shed = {"id": "shed", "geometry": {"x_ft": -10.0, "y_ft": wing_y, "width_ft": 9.0, "depth_ft": 12.0},
                "doors": [{"to": "exterior", "wall": "S", "position_ft": -5.5, "width_ft": 4.0}]}
        plan = {"style": "tidewater-georgian", "context": {"entrance_faces": "S"},
                "levels": [{"index": 0, "floor_to_ceiling_ft": 11.0, "rooms": [hall, shed]}],
                "footprint": {"bay_module_ft": 9.0},
                "geometry_report": {"bay_module": {"ft": 9.0, "stated_by": "a-parti"}}}
        envs = {"hall": (0.0, 0.0, 24.0, 16.0), "shed": (-10.0, wing_y, -1.0, wing_y + 12.0)}
        return plan, envs

    plan, envs = plan_with(0.3)
    report = {}
    OP._reserve_doorcase(plan, plan["levels"][0]["rooms"], 24.0, 16.0, envs, report, 0)
    assert report["doorcase"]["reserved"] and report["doorcase"]["room"] == "hall", report
    plan, envs = plan_with(0.0)
    report = {}
    OP._reserve_doorcase(plan, plan["levels"][0]["rooms"], 24.0, 16.0, envs, report, 0)
    assert report["doorcase"]["room"] == "shed", report


# ------------------------------------------------------------------ what the sheet and the DXF say
def _move_window(el, face, to_clear_in):
    """DRIVE the flanking window back toward the doorcase until the wall between them is
    `to_clear_in` (negative stands it over the casing), shifting every field the rect is read from."""
    rects = EL.opening_rects(el, face)["rects"]
    (ent,) = [r for r in rects if r.get("entrance")]
    cas = ent["entrance"]["casing_width_in"]
    placed = [p for p in el["faces"][face]["placed"] if p["kind"] == "window"
              and p["storey"] == ent["storey"] and p["cx_in"] < ent["cx_in"]]
    p = max(placed, key=lambda q: q["cx_in"])
    target = ent["x0_in"] - cas - to_clear_in - p["width_in"] / 2.0
    d_in = target - p["cx_in"]
    p["cx_in"] += d_in
    p["u_ft"] = round(p["u_ft"] + d_in / 12.0, 4)
    p["along_ft"] += d_in / 12.0
    return p


def test_a_short_side_is_measured_and_said_on_the_sheet_and_in_the_dxf(corpus):
    _placed, el0 = corpus["tidewater-georgian-careful"]
    el = copy.deepcopy(el0)
    face = el["entrance_face"]
    p = _move_window(el, face, 5.0)
    got = EL.doorcase_piers(el, face)
    short = [s for s in got["sides"] if s["verdict"] == "short"]
    assert short and short[0]["neighbour"]["room"] == p["room"], got
    assert short[0]["clear_in"] == pytest.approx(5.0, abs=0.01), short
    notes = EL.doorcase_pier_notes(el, face)
    assert notes and notes[0].startswith("THE WALL BESIDE THE DOORCASE IS 5.0") and "ON THE LEFT" in notes[0]
    said = _said(_svg(el, face))
    assert notes[0] in said
    ezdxf = pytest.importorskip("ezdxf")
    DX = _L("export_dxf")
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "e.dxf")
        DX.export_elevation_dxf(el, path, face=face)
        # the notes are MTEXT since WP-15.8, broken to the drawing's width: a break reads as a space
        texts = [e.dxf.text if e.dxftype() == "TEXT" else e.plain_text().replace("\n", " ")
                 for e in ezdxf.readfile(path).modelspace().query("TEXT MTEXT")]
    assert notes[0] in texts


def test_a_doorcase_over_a_window_is_said_to_touch_it(corpus):
    _placed, el0 = corpus["tidewater-georgian-careful"]
    el = copy.deepcopy(el0)
    face = el["entrance_face"]
    _move_window(el, face, -2.0)
    got = EL.doorcase_piers(el, face)
    assert any(s["verdict"] == "touches" for s in got["sides"]), got
    notes = EL.doorcase_pier_notes(el, face)
    assert any(n.startswith("THE DOORCASE TOUCHES THE") and "ON THE LEFT" in n for n in notes), notes
    assert any(n.startswith("THE DOORCASE TOUCHES") for n in _said(_svg(el, face)))


def _move_window_right(el, face, to_clear_in):
    """The flanking window driven round to the doorcase's RIGHT, `to_clear_in` clear of its casing."""
    rects = EL.opening_rects(el, face)["rects"]
    (ent,) = [r for r in rects if r.get("entrance")]
    cas = ent["entrance"]["casing_width_in"]
    p = max((q for q in el["faces"][face]["placed"] if q["kind"] == "window"
             and q["storey"] == ent["storey"] and q["cx_in"] < ent["cx_in"]), key=lambda q: q["cx_in"])
    d_in = (ent["x1_in"] + cas + to_clear_in + p["width_in"] / 2.0) - p["cx_in"]
    p["cx_in"] += d_in
    p["u_ft"] = round(p["u_ft"] + d_in / 12.0, 4)
    p["along_ft"] += d_in / 12.0
    return p


def test_a_short_side_on_the_right_is_measured_the_right_way_round(corpus):
    """D11 (auditor M): every judged doorcase in the corpus has its window on the LEFT and a door on
    its right, so a right-hand clearance with its sign flipped -- which calls a window 5 in clear
    one standing 5 in over the casing, and prints a false TOUCHES -- passed. Driven."""
    _placed, el0 = corpus["tidewater-georgian-careful"]
    el = copy.deepcopy(el0)
    face = el["entrance_face"]
    p = _move_window_right(el, face, 5.0)
    (right,) = [s for s in EL.doorcase_piers(el, face)["sides"] if s["side"] == "right"]
    assert right["neighbour"]["room"] == p["room"], ("the premise: the window is nearest", right)
    assert right["verdict"] == "short" and right["clear_in"] == pytest.approx(5.0, abs=0.01), right
    notes = EL.doorcase_pier_notes(el, face)
    assert any("ON THE RIGHT" in n and n.startswith("THE WALL BESIDE THE DOORCASE IS 5.0") for n in notes)
    assert not any(n.startswith("THE DOORCASE TOUCHES") for n in notes), notes


def test_a_window_that_meets_the_doorcase_exactly_touches_it(corpus):
    """D08 (auditor M): the boundary moved below zero passed, because the only touching case driven
    stood the window 2 in OVER the casing. A window meeting the casing with no wall between them
    touches it: "not allowed to touch" has no floor to fall short of."""
    _placed, el0 = corpus["tidewater-georgian-careful"]
    el = copy.deepcopy(el0)
    face = el["entrance_face"]
    _move_window(el, face, 0.0)
    (left,) = [s for s in EL.doorcase_piers(el, face)["sides"] if s["side"] == "left"]
    assert left["clear_in"] == pytest.approx(0.0, abs=0.01) and left["verdict"] == "touches", left


def test_the_wall_is_measured_to_the_nearest_window_and_not_the_farthest(corpus):
    """D07 (auditor M): measuring to the FARTHEST window on the left passed, because the Tidewater
    front draws one window to the left of its doorcase (the drawing room's and the library's are
    refused). A second window is set further along, and the side is still the nearer one's."""
    _placed, el0 = corpus["tidewater-georgian-careful"]
    el = copy.deepcopy(el0)
    face = el["entrance_face"]
    near = _move_window(el, face, 5.0)
    far = copy.deepcopy(near)
    far["cx_in"] -= 60.0
    far["u_ft"] = round(far["u_ft"] - 5.0, 4)
    far["along_ft"] -= 5.0
    far["room"] = "far-" + str(near["room"])
    el["faces"][face]["placed"].append(far)
    rooms = [r.get("room") for r in EL.opening_rects(el, face)["rects"] if r["kind"] == "window"]
    assert far["room"] in rooms and near["room"] in rooms, ("the premise: both are drawn", rooms)
    (left,) = [s for s in EL.doorcase_piers(el, face)["sides"] if s["side"] == "left"]
    assert left["neighbour"]["room"] == near["room"], left
    assert left["verdict"] == "short" and left["clear_in"] == pytest.approx(5.0, abs=0.01), left


def test_the_floor_is_not_judged_where_no_parti_states_the_bay_and_the_sheet_says_so(corpus):
    placed, el = corpus["spec-builder-colonial"]
    assert DC.stated_bay_ft(placed)[0] is None, "the premise: no parti states this plan's bay"
    rec = placed["opening_report"]["doorcase"]
    assert rec["reserved"] and rec["residual"].startswith("NOT JUDGED"), rec
    face = el["entrance_face"]
    got = EL.doorcase_piers(el, face)
    assert any(s["verdict"] == "unjudged" for s in got["sides"]), got
    line = "THE WALL BESIDE THE DOORCASE IS NOT JUDGED — " + DC.UNSTATED_BAY.upper()
    assert EL.doorcase_pier_notes(el, face) == [line]
    assert _said(_svg(el, face)).count(line) == 1
    for f in EL.FACES:
        if f != face:
            assert not any(t.startswith("THE WALL BESIDE THE DOORCASE") for t in _said(_svg(el, f))), f
    ezdxf = pytest.importorskip("ezdxf")
    DX = _L("export_dxf")
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "e.dxf")
        DX.export_elevation_dxf(el, path, face=face)
        # the notes are MTEXT since WP-15.8, broken to the drawing's width: a break reads as a space
        texts = [e.dxf.text if e.dxftype() == "TEXT" else e.plain_text().replace("\n", " ")
                 for e in ezdxf.readfile(path).modelspace().query("TEXT MTEXT")]
    assert line in texts


def test_a_side_the_rule_does_not_reach_says_nothing(corpus):
    """A door or a corner beside the doorcase is not a flanking window: measured, not judged, not
    said. The Tidewater doorcase has the porch door on one side; the spec Colonial's has its corner."""
    kinds = set()
    for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
        _placed, el = corpus[pid]
        for s in EL.doorcase_piers(el, el["entrance_face"])["sides"]:
            if s["verdict"] == "not_applicable":
                assert s["clear_in"] is not None, (pid, s)
                kinds.add("corner" if s["neighbour"] is None else s["neighbour"]["kind"])
    assert kinds == {"corner", "door"}, kinds
    # the Tidewater front's one judged side agrees and its other is a door: nothing to say
    _placed, el = corpus["tidewater-georgian-careful"]
    face = el["entrance_face"]
    assert EL.doorcase_pier_notes(el, face) == []
    assert not any(t.startswith(("THE WALL BESIDE THE DOORCASE", "THE DOORCASE TOUCHES"))
                   for t in _said(_svg(el, face)))
