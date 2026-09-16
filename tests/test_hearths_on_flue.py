"""WP-13.2 -- the fire stands on its flue, the plan's stacks are the roof's stacks, and no
window stands in a chimney breast.

Three things the gate (`tests/test_sheet_coherence.py`) measured on `840c7f1` and this package
answers, each with the figure it was measured at:

  * `threshold.hearth_pass` put the plan's two stack squares at the mid-depth of each end wall
    from the RECTANGLE alone and recorded `hearth_rooms: NOT READ`, while `roof.py` stood its
    chimneys over the plan's stated flues -- one building, two records, the west chimney 5.4 ft
    apart and the east 7.3. The plan's squares are placed FROM the stated flues now
    (`hearths.flues`, roof.py's rule moved into the leaf) and the roof READS the plan's record.
  * `hearths.breast` drew the fire on the room's declared wall wherever the room landed: on the
    CP-SAT sheet the drawing and dining rooms' declared W walls were released and their breasts
    stood 19 and 25 ft inboard of the west face with no flue behind them. A breast on a wall the
    placement did not put on the element's boundary is REFUSED, with the reason `openings.py`
    gives a window in the same position, and the plate draws nothing for it.
  * The breast's centre, a lone window's position and the flue axis all defaulted to the room's
    mid-wall, so the dining and library sashes were drawn 100% inside their own breasts and the
    west stack overlapped a window by 0.79 ft. The breasts and the stacks are placed first and
    their runs reserved, with the corpus's own minimum solid as the pier, before a sash is
    seated.

Every figure here is `engine="heuristic"`, which is deterministic (CLAUDE.md, WP-9.6). The
refusals the corpus cannot reach -- a released wall, a flue with no fire on any boundary wall,
a hearth record that cannot be read -- are DRIVEN by hand, on WP-11.10's rule that a guard which
runs only where the bug cannot occur is not a guard.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

HE = modcache.load("hearths", os.path.join(ROOT, "build", "hearths.py"))
TH = modcache.load("threshold", os.path.join(ROOT, "build", "threshold.py"))
OP = modcache.load("openings", os.path.join(ROOT, "build", "openings.py"))
GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
RF = modcache.load("roof", os.path.join(ROOT, "build", "roof.py"))
ST = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))
RP = modcache.load("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))

TIDEWATER = os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")


@pytest.fixture(scope="module")
def C():
    return PC.load_corpus()


@pytest.fixture(scope="module")
def placed():
    """The shipped record read as the ONE-ELEMENT house it was until WP-13.5, on the search
    engine, placed ONCE for the module.

    **EVERY TEST IN THIS FILE IS ABOUT THE HEARTH MACHINERY AND NEEDS A HOUSE WITH TWO
    STACKS.** Until WP-13.5 the shipped record was that house: the drawing room and the dining
    room stood on the west gable, the library on the east, and the plan drew two squares on two
    stated flues. WP-13.5 moved the service programme into the dependency that record declares,
    and on THIS engine the 45 ft main block that remains does not keep the two principal rooms
    against the west wall -- each is drawn 4.95 ft inboard of it, so neither fire has an
    exterior wall to carry its flue and `hearths.breast` refuses both, by name and with the
    reason. The west stack is not drawn.

    That is a real cost of the container and it is NOT hidden here: it is asserted, on the
    SHIPPED record, by `test_the_shipped_record_now_draws_ONE_stack_and_says_why` below, which
    is also the premise for this strip. What these tests measure is the machinery -- a breast
    on a boundary is drawn, a breast off one is refused with its reason, the roof reads the
    plan's flues rather than recomputing them -- and the machinery needs a record that reaches
    all of its branches. On `engine="cp"` the drawing room's fire still holds and only the
    dining room's is inboard (2 of 3), so this is one engine's placement rather than a fact
    about the record."""
    GEO._SOLVE_CACHE.clear()
    d = json.load(open(TIDEWATER, encoding="utf-8"))
    for lv in d.get("levels", []):
        for r in lv.get("rooms", []):
            r.pop("block", None)
            r.pop("hyphen", None)
    return GEO.solve(d, None, 250, engine="heuristic")


@pytest.fixture(scope="module")
def shipped():
    """The record AS SHIPPED, container and all, placed once."""
    GEO._SOLVE_CACHE.clear()
    return GEO.solve(json.load(open(TIDEWATER, encoding="utf-8")), None, 250, engine="heuristic")


def test_the_shipped_record_now_draws_ONE_stack_and_says_why(shipped):
    """THE COST OF WP-13.5's CONTAINER ON THIS SHEET, ASSERTED RATHER THAN LEFT TO A COMMENT,
    and the premise of the `placed` fixture above.

    With the service programme in the dependency, the main block is 45 ft wide and this engine
    draws the drawing room and the dining room 4.95 ft inboard of its west face. A fire whose
    room does not reach an exterior wall has no flue, so `hearths.breast` refuses it -- and the
    refusal is the honest kind: it names the wall, the distance, and the fact that an interior
    stack is NOT invented in its place. The east stack, whose library does reach the east wall,
    is unaffected.

    If a later package puts those two rooms back on the gable, this test goes red and the
    `placed` fixture above stops needing its strip. That is the right direction and it should
    be loud."""
    st = {s["flue"] for s in shipped["hearths"]["stacks"]}
    assert st == {"east-stack"}, (
        "the shipped Tidewater sheet drew TWO stacks before WP-13.5 and draws one now; if it "
        "draws two again the fixture above no longer needs its strip")
    un = shipped["hearths"]["unplaced"]
    breasts = [u for u in un if u.get("rule") == "hearths.breast"]
    assert {u["room"] for u in breasts} == {"drawing", "dining"}, breasts
    for u in breasts:
        why = u["reason"]
        assert "no exterior wall carries its flue" in why, why
        assert "a fire with no flue is not drawn" in why, why
        assert "interior stack is not modelled" in why, (
            "the refusal must say an interior stack is not invented in its place")
    # AND THE STACK ITSELF IS REFUSED ON ITS OWN ACCOUNT, not merely absent: a stack over no
    # fire is not placed (WP-11.4), and the record says so where a reader will look.
    stack = [u for u in un if u.get("flue") == "west-stack"]
    assert len(stack) == 1 and "no fire for its stack to stand over" in stack[0]["reason"]
    # the drawn-false breasts still carry their rectangle, so a later reader can see WHERE the
    # fire would have been: 4.95 ft inboard of the element's west face.
    off = [b for b in shipped["hearths"]["breasts"] if not b["drawn"]]
    assert {b["room"] for b in off} == {"drawing", "dining"}
    assert all(b["judged"] and round(b["x_ft"], 2) == 4.95 for b in off), off


def _room(plan, rid, level=0):
    return next(r for r in plan["levels"][level]["rooms"] if r["id"] == rid)


def _bounds(plan):
    fp = plan["footprint"]
    return (0.0, 0.0, fp["width_ft"], fp["depth_ft"])


# ------------------------------------------------------------------ the breast is judged
class TestTheBreastOnAReleasedWall:
    def test_a_breast_off_the_boundary_is_refused_and_measured(self, placed):
        """The CP-SAT case, driven: the drawing room's declared W wall 19 ft inboard. Refused,
        in the words `openings.py` uses for a window there, and STILL CARRYING the rectangle
        the declared wall would have given it, so the refusal is a figure and not a count."""
        r = copy.deepcopy(_room(placed, "drawing"))
        r["geometry"]["x_ft"] = 19.0
        b = HE.breast(r, r["hearth"][0], bounds=_bounds(placed))
        assert b["undrawable"] is True
        assert b["unplaced"]["reason"] == "the placement puts this room on no such boundary wall"
        assert b["unplaced"]["declared_wall"] == "W"
        assert b["unplaced"]["have"]["inboard_ft"] == 19.0
        assert "W" not in b["unplaced"]["have"]["walls_on_the_boundary"]
        assert b["x_ft"] == 19.0, "the would-be rectangle travels with the refusal"
        assert "no flue" in b["why"] and "not drawn" in b["why"]
        assert "interior stack is not modelled" in b["why"], (
            "the refusal must say an interior stack is not invented in its place")

    def test_a_breast_on_the_boundary_is_drawn_and_carries_no_refusal(self, placed):
        r = _room(placed, "drawing")
        b = HE.breast(r, r["hearth"][0], bounds=_bounds(placed))
        assert not b.get("undrawable") and "unplaced" not in b
        assert b["x_ft"] == 0 and b["wall"] == "W"

    def test_without_bounds_the_rectangle_is_returned_unjudged(self, placed):
        """The two-argument call is what the gate, the scene and `render_plan` make: it cannot
        know the element's boundary, so it judges nothing and refuses nothing -- the rectangle,
        exactly as before WP-13.2. The verdict on a placed plan is READ from
        `plan.hearths.breasts`, where `hearth_pass` wrote it with the same function."""
        r = copy.deepcopy(_room(placed, "drawing"))
        r["geometry"]["x_ft"] = 19.0
        b = HE.breast(r, r["hearth"][0])
        assert "undrawable" not in b and "unplaced" not in b
        assert b["x_ft"] == 19.0

    def test_it_is_the_same_boundary_reader_a_window_uses(self):
        """ONE spelling of "is this wall on the outside": `elements.boundary_walls`, which
        `openings._boundary_walls` moved its body into (WP-11.9). A breast and a window on one
        wall cannot then answer differently."""
        src = open(os.path.join(ROOT, "build", "hearths.py"), encoding="utf-8").read()
        assert ".boundary_walls(" in src
        assert "x <= bx + tol" not in src and "x + w >= bx + bw" not in src, (
            "hearths.py restates the boundary test instead of reading elements.boundary_walls")


# ------------------------------------------------------------------ the placement layer's verdict
class TestHearthPassJudgesEveryBreast:
    def test_the_shipped_record_draws_all_three_on_the_search_engine(self, placed):
        h = placed["hearths"]
        assert h["placed_from"] == "stated-hearths"
        rows = h["breasts"]
        assert [(r["room"], r["drawn"], r["judged"]) for r in rows] == [
            ("drawing", True, True), ("dining", True, True), ("library", True, True)]
        assert h["unplaced"] == []
        assert placed["opening_report"]["hearths_refused"] == 0

    def test_a_released_wall_is_refused_in_the_record_and_on_the_plate(self, placed, C, tmp_path):
        """Driven: the drawing room moved 19 ft inboard on the placed record, then judged again.
        The verdict is in `breasts`, the refusal in `unplaced` with its rule, the west flue is
        served by the dining room alone, and BOTH registers of the plate draw no fireplace for
        it -- the working register carries a dashed ghost with the reason, the presentation
        register nothing but the record."""
        p = copy.deepcopy(placed)
        _room(p, "drawing")["geometry"]["x_ft"] = 19.0
        rep = {}
        TH.hearth_pass(p, C, rep)
        h = p["hearths"]
        row = next(r for r in h["breasts"] if r["room"] == "drawing")
        assert row["drawn"] is False and row["judged"] is True
        assert row["unplaced"]["have"]["inboard_ft"] == 19.0
        ref = [u for u in h["unplaced"] if u.get("room") == "drawing"]
        assert len(ref) == 1 and ref[0]["rule"] == "hearths.breast"
        assert ref[0]["reason"] == row["why"]
        fl = next(f for f in h["flues"] if f["flue"] == "west-stack")
        assert fl["serves"] == ["dining"] and fl["stated"] == ["drawing", "dining"]
        assert fl["position_ft"] == 20.965, "the flue stands at its one served fire"
        wk = str(tmp_path / "working.svg")
        RP.render(p, wk, register="working")
        svg = open(wk, encoding="utf-8").read()
        assert svg.count("fireplace,") == 2, "two fires drawn, the refused one not"
        assert 'data-hearth-refused="drawing"' in svg
        assert "fireplace NOT DRAWN" in svg and "no flue" in svg
        pr = str(tmp_path / "presentation.svg")
        RP.render(p, pr, register="presentation")
        svg2 = open(pr, encoding="utf-8").read()
        assert svg2.count("fireplace,") == 2
        assert "data-hearth-refused" not in svg2, "the presentation register draws nothing for it"

    def test_the_reason_is_read_from_the_record_and_not_rederived_by_the_plate(self, placed, tmp_path):
        """The plate reads `plan.hearths.breasts`; it does not judge. Strip the verdict rows
        and the same released room is drawn again, which is the pre-WP-13.2 behaviour and is
        what proves the renderer holds one judge rather than a second one."""
        p = copy.deepcopy(placed)
        _room(p, "drawing")["geometry"]["x_ft"] = 19.0
        p["hearths"]["breasts"] = []
        out = str(tmp_path / "unjudged.svg")
        RP.render(p, out, register="working")
        svg = open(out, encoding="utf-8").read()
        assert svg.count("fireplace,") == 3
        assert "data-hearth-refused" not in svg

    def test_a_hearth_in_an_unplaced_room_is_a_stated_refusal(self, placed, C):
        p = copy.deepcopy(placed)
        _room(p, "library").pop("geometry")
        TH.hearth_pass(p, C, {})
        row = next(r for r in p["hearths"]["breasts"] if r["room"] == "library")
        assert row["drawn"] is False and "not placed" in row["why"]
        assert any(u.get("room") == "library" for u in p["hearths"]["unplaced"])


# ------------------------------------------------------------------ one stack per flue
class TestThePlansStacksAreTheRoofsStacks:
    def test_the_squares_stand_on_the_stated_flues_at_the_mean_of_their_fires(self, placed):
        """Before this package: both squares at the mid-depth of the end wall, 19.085 ft, from
        the rectangle. Now: the west square at the mean of the drawing and dining rooms' axes
        (7.465 and 20.965 -> 14.215) and the east at the library's (11.765)."""
        h = placed["hearths"]
        by = {s["flue"]: s for s in h["stacks"]}
        assert set(by) == {"west-stack", "east-stack"}
        w, e = by["west-stack"], by["east-stack"]
        assert w["wall"] == "W" and e["wall"] == "E"
        assert abs((w["y_ft"] + w["depth_ft"] / 2) - (7.465 + 20.965) / 2) < 0.002
        assert abs((e["y_ft"] + e["depth_ft"] / 2) - 11.765) < 0.002
        assert w["serves"] == ["drawing", "dining"] and e["serves"] == ["library"]
        D = placed["footprint"]["depth_ft"]
        for s in h["stacks"]:
            assert abs(s["y_ft"] + s["depth_ft"] / 2 - D / 2) > 4.0, (
                "a square still stands on the centre line of the end wall")
        assert [s["wall"] for s in h["stacks"]] == ["W", "E"], "the order the old record wrote"

    def test_the_roof_reads_the_plans_record_rather_than_deriving_its_own(self, placed):
        ch = RF.build_roof(copy.deepcopy(placed), section=ST.build_section(placed))["chimneys"]
        assert ch["from_stated_hearths"] is True
        assert "plan.hearths.flues" in ch["note"]
        # IN THE ROOF'S OWN FRAME. The first version of this test asserted the roof's y EQUAL
        # to the flue's `position_ft`, and that equality was the defect: the flue is a plan
        # coordinate (from the clear inside face) and the roof record is outside-to-outside,
        # so an equal number is a stack one wall thickness short of its fire on the roof plate,
        # the elevation and the scene. The gate's stacks-equal-roof row measured it at 1.3 ft
        # on both engines the moment the plan side read the same record.
        sec = ST.build_section(placed)
        t = sec["wall"]["exterior_in"] / 12.0
        roof_y = sorted(round(c["y_ft"], 2) for c in ch["positions"])
        plan_y = sorted(round(f["position_ft"] + t, 2) for f in placed["hearths"]["flues"])
        assert roof_y == plan_y, (roof_y, plan_y)
        assert all(abs(c["y_ft"] - f["position_ft"]) > 1.0
                   for c, f in zip(sorted(ch["positions"], key=lambda c: c["y_ft"]),
                                   sorted(placed["hearths"]["flues"], key=lambda f: f["position_ft"]))), \
            "the roof wrote the plan coordinate into its own frame verbatim again"
        assert len(ch["positions"]) == len(placed["hearths"]["stacks"]) == 2

    def test_a_flue_moved_in_the_record_moves_the_roof(self, placed):
        """The proof that the roof READS rather than recomputes: edit the plan's own flue
        record and the roof follows it. A roof deriving from the hearths would not."""
        p = copy.deepcopy(placed)
        fl = next(f for f in p["hearths"]["flues"] if f["flue"] == "east-stack")
        fl["position_ft"] = 3.0
        sec = ST.build_section(p)
        t = sec["wall"]["exterior_in"] / 12.0
        ch = RF.build_roof(p, section=sec)["chimneys"]
        assert any(abs(c["y_ft"] - (3.0 + t)) < 0.01 for c in ch["positions"]), \
            [c["y_ft"] for c in ch["positions"]]

    def test_the_gather_is_disclosed_where_one_stack_serves_two_fires_apart(self, placed):
        """THE FIGURE THIS PACKAGE CANNOT CLOSE, STATED AS ONE. The record puts the drawing and
        dining rooms' fires on one flue; both breasts default to the centre of their own end
        wall (the schema's rule for an absent `position_ft`), 13.5 ft apart on this placement;
        a 22 in square at the flue's mean stands behind neither. It is not moved and not doubled
        (`build/hearths.py`'s docstring says why); it is written on the stack and on each
        breast row, so the plate's reader and the gate's are told the same number."""
        h = placed["hearths"]
        w = next(s for s in h["stacks"] if s["flue"] == "west-stack")
        assert w["behind"] == []
        assert set(w["gathered"]) == {"drawing", "dining"}
        assert all(3.0 < g < 4.0 for g in w["gathered"].values()), w["gathered"]
        e = next(s for s in h["stacks"] if s["flue"] == "east-stack")
        assert e["behind"] == ["library"] and e["gathered"] == {}
        rows = {r["room"]: r["flue_stack"] for r in h["breasts"]}
        assert rows["library"] == {"behind": True, "gathered_ft": 0.0}
        assert rows["drawing"]["behind"] is False and rows["drawing"]["gathered_ft"] == w["gathered"]["drawing"]

    def test_a_flue_with_no_fire_on_any_boundary_wall_is_refused_and_the_roof_omits_it(self, placed, C):
        """Driven: both west fires released. The west flue has no fire to stand over, so no
        square is placed for it and the roof -- reading the plan -- stands one chimney, naming
        the refused flue and its reason. A stack over no fire is what WP-11.4 removes."""
        p = copy.deepcopy(placed)
        _room(p, "drawing")["geometry"]["x_ft"] = 19.0
        _room(p, "dining")["geometry"]["x_ft"] = 25.0
        TH.hearth_pass(p, C, {})
        h = p["hearths"]
        assert [f["flue"] for f in h["flues"]] == ["east-stack"]
        assert [s["flue"] for s in h["stacks"]] == ["east-stack"]
        ref = [u for u in h["unplaced"] if u.get("flue") == "west-stack"]
        assert len(ref) == 1 and "no fire for its stack" in ref[0]["reason"]
        assert ref[0]["rule"] == "hearths.flues"
        ch = RF.build_roof(p, section=ST.build_section(p))["chimneys"]
        assert len(ch["positions"]) == 1
        assert "flue 'west-stack' NOT placed" in ch["note"]

    def test_a_plan_that_states_no_hearth_keeps_the_centre_line_and_says_so(self, C):
        p = json.load(open(TIDEWATER, encoding="utf-8"))
        for lv in p["levels"]:
            for r in lv["rooms"]:
                r.pop("hearth", None)
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, None, 250, engine="heuristic")
        h = p["hearths"]
        assert h["placed_from"] == "centre-line" and h["flues"] == [] and h["breasts"] == []
        D = p["footprint"]["depth_ft"]
        assert len(h["stacks"]) == 2
        for s in h["stacks"]:
            assert abs(s["y_ft"] + s["depth_ft"] / 2 - D / 2) < 0.002
            assert s["flue"] is None and s["serves"] == []
        sec = ST.build_section(p)
        ch = RF.build_roof(p, section=sec)["chimneys"]
        assert "states no hearth" in ch["note"] and "not a house with no fires" in ch["note"]
        # THE ROOF'S CENTRE LINE IS NOT THE PLAN'S, BY EXACTLY ONE WALL THICKNESS. The roof lays
        # its plan over the OUTSIDE footprint (40.75 ft deep here) and the placement over the
        # CLEAR one (38.17), so the same rule -- `gable_end_points`, one function -- gives
        # 20.38 to the roof and 19.09 to the plan. That is
        # `oq/the-roof-record-and-the-plan-record-do-not-share-an-origin`, measured here so a
        # reader of the gate's "plan stacks = roof stacks" row knows what its residue is; it is
        # asserted as the offset it is, never absorbed into the tolerance.
        D_out = sec["footprint"]["depth_ft"]
        t = sec["wall"]["exterior_in"] / 12.0
        assert abs((D_out - D) - 2 * t) < 0.01, (D_out, D, t)
        assert sorted(round(c["y_ft"], 2) for c in ch["positions"]) == [round(D_out / 2, 2)] * 2

    def test_the_rule_is_spelled_once_and_roof_py_no_longer_groups_by_flue(self):
        src = open(os.path.join(ROOT, "build", "roof.py"), encoding="utf-8").read()
        assert "by_flue" not in src, "roof.py carries its own grouping of hearths by flue again"
        assert "sum(a[\"position_ft\"]" not in src, "roof.py averages hearth axes itself again"
        assert 'hr.get("flues")' in src or "hr.get('flues')" in src

    def test_an_unreadable_hearth_is_recorded_by_the_placer_and_republished_by_the_roof(self, monkeypatch):
        """WP-11.4's fourth state, moved with the reading: the placement layer is the one
        reader now, so the failure is caught THERE (`hearths_unreadable`, squares on the centre
        line) and the roof republishes it rather than deriving anything -- never "this record
        states no hearth" about a record carrying three."""
        def boom(plan, C):
            raise ValueError("a hearth wall nobody wrote down")
        monkeypatch.setattr(HE, "stack_axes", boom)
        p = json.load(open(TIDEWATER, encoding="utf-8"))
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, None, 250, engine="heuristic")
        h = p["hearths"]
        assert h["hearths_unreadable"] and "a hearth wall nobody wrote down" in h["hearths_unreadable"]
        assert h["placed_from"] == "centre-line" and h["breasts"] == []
        ch = RF.build_roof(p, section=ST.build_section(p))["chimneys"]
        assert ch.get("hearths_unreadable")
        assert "COULD NOT BE READ" in ch["note"]
        assert "a hearth wall nobody wrote down" in ch["note"]
        assert "states no hearth" not in ch["note"]
        assert not ch.get("from_stated_hearths")


# ------------------------------------------------------------------ the windows keep clear
def _placed_units(room, wall):
    out = []
    for w in room.get("windows") or []:
        if w.get("wall") == wall:
            out += [(p, w.get("width_ft") or 3.0) for p in (w.get("positions_ft") or [])]
    return out


class TestNoSashInTheBreast:
    def test_every_placed_sash_keeps_the_pier_clear_of_its_rooms_breast(self, placed):
        """Read from the RECORD's `positions_ft`, which is what the placer wrote; the drawn
        list `derive_openings` returns is the gate's business. Before: the dining and library
        sashes 100% inside their breasts, the drawing room's two 49% each."""
        checked = 0
        for row in placed["hearths"]["breasts"]:
            if not row["drawn"]:
                continue
            r = _room(placed, row["room"])
            lo, hi = row["y_ft"], row["y_ft"] + row["depth_ft"]
            for p, ww in _placed_units(r, row["wall"]):
                checked += 1
                gap = max(lo - (p + ww / 2), (p - ww / 2) - hi)
                assert gap >= OP.MASONRY_PIER_FT, (row["room"], p, gap)
        assert checked >= 2, "no sash on a breast wall was placed, so nothing was checked"

    def test_every_placed_sash_keeps_the_pier_clear_of_a_stack(self, placed):
        fp = placed["footprint"]
        W, H = fp["width_ft"], fp["depth_ft"]
        checked = 0
        for lv in placed["levels"]:
            for r in lv["rooms"]:
                rect = OP._rect(r)
                if not rect:
                    continue
                for sk in placed["hearths"]["stacks"]:
                    bw = OP._boundary_walls(rect, W, H)
                    if sk["wall"] not in bw:
                        continue
                    lo, hi = sk["y_ft"], sk["y_ft"] + sk["depth_ft"]
                    for p, ww in _placed_units(r, sk["wall"]):
                        checked += 1
                        gap = max(lo - (p + ww / 2), (p - ww / 2) - hi)
                        assert gap >= OP.MASONRY_PIER_FT, (r["id"], sk["flue"], p, gap)
        assert checked >= 3

    def test_a_sash_that_no_longer_fits_is_refused_by_name_and_the_count_is_kept(self, placed):
        """The dining room's W wall is 12.07 ft with a 4.76 ft breast at its centre: 2.65 ft of
        wall either side of the pier, and a 3.5 ft sash does not go. Refused, naming what
        took the wall, and the DECLARED count is untouched (WP-6.2's rule). The drawing room
        keeps one of its two."""
        dw = next(w for w in _room(placed, "dining")["windows"] if w["wall"] == "W")
        assert dw["count"] == 1 and "positions_ft" not in dw
        assert dw["unplaced"]["have"]["units_placed"] == 0
        assert "the chimney breast" in dw["unplaced"]["reason"]
        rw = next(w for w in _room(placed, "drawing")["windows"] if w["wall"] == "W")
        assert rw["count"] == 2 and len(rw["positions_ft"]) == 1
        assert rw["unplaced"]["have"]["units_placed"] == 1
        assert "the chimney breast" in rw["unplaced"]["reason"]
        assert placed["opening_report"]["windows_unplaced"] == 16, (
            "14 before this package; +1 drawing W, +1 dining W -- re-derive before re-pinning")

    def test_the_pier_is_the_corpus_own_minimum_solid_and_one_quantum_of_the_record(self):
        """The pier beside a breast is editorial and is the same figure as beside a door --
        reused, not restated -- and the reserved run is widened by exactly the quantum a
        position is rounded to, so a rounded figure cannot land inside the pier."""
        assert OP.MASONRY_PIER_FT is OP.MIN_SOLID_FT
        assert OP._RECORD_QUANTUM_FT == 10 ** -3
        src = open(os.path.join(ROOT, "build", "openings.py"), encoding="utf-8").read()
        assert 'win["positions_ft"] = [round(p, 3) for p in placed]' in src, (
            "the window position is no longer written to three decimals; re-derive the quantum")

    def test_the_reservation_reads_the_verdict_and_reserves_nothing_for_a_refused_fire(self, placed):
        rooms = copy.deepcopy(placed["levels"][0]["rooms"])
        fp = placed["footprint"]
        W, H = fp["width_ft"], fp["depth_ft"]
        hearths = copy.deepcopy(placed["hearths"])
        occ = {}
        took = OP._reserve_masonry(rooms, occ, W, H, {}, hearths, 0)
        assert ("drawing", "W") in took and "the chimney breast" in took[("drawing", "W")]
        for row in hearths["breasts"]:
            if row["room"] == "drawing":
                row["drawn"] = False
        occ2 = {}
        took2 = OP._reserve_masonry(rooms, occ2, W, H, {}, hearths, 0)
        assert "the chimney breast" not in took2.get(("drawing", "W"), [])
        assert len(occ2.get(("drawing", "W"), [])) < len(occ.get(("drawing", "W"), []))

    def test_the_stack_is_reserved_on_every_level_it_passes_through(self, placed):
        """A stack rises through the house; the upper storey's gable rooms keep clear of it
        too. Driven on the upper level's rooms with the same stacks."""
        upper = next(lv for lv in placed["levels"] if lv.get("index") == 1)
        fp = placed["footprint"]
        W, H = fp["width_ft"], fp["depth_ft"]
        occ = {}
        took = OP._reserve_masonry(copy.deepcopy(upper["rooms"]), occ, W, H, {},
                                   placed["hearths"], 1)
        assert any("the chimney stack" in v for v in took.values()), (
            "no upper room stands on a wall a stack stands on -- the fixture does not exercise "
            "the branch")
        assert not any("the chimney breast" in v for v in took.values()), (
            "a ground-floor breast was reserved on the upper level")


# ------------------------------------------------------------------ the record validates
def test_the_placed_record_still_validates(placed):
    jsonschema = pytest.importorskip("jsonschema", reason="COULD NOT EVALUATE: no jsonschema")
    jsonschema.validate(placed, json.load(open(os.path.join(ROOT, "schema", "plan.schema.json"))))
