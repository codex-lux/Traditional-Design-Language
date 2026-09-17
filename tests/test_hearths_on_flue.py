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
    """The shipped record read with its container tags STRIPPED, on the search engine, placed
    ONCE for the module.

    **EVERY TEST IN THIS FILE IS ABOUT THE HEARTH MACHINERY AND NEEDS A RECORD THAT REACHES
    EVERY BRANCH OF IT** -- a fire drawn on one gable, a fire drawn on the other, and a fire
    refused by name -- because the SHIPPED record no longer does: with the service programme in
    the dependency WP-13.5 tags, the 45 ft main block that remains keeps neither principal room
    against the west face on this engine, and both west fires were refused
    (`test_the_shipped_record_now_draws_ONE_stack_and_says_why` below asserts that cost on the
    shipped record, and is this strip's premise).

    **STRIPPING THE TAGS DOES NOT RESTORE THE PRE-WP-13.5 HOUSE, AND THIS DOCSTRING CLAIMED IT
    DID UNTIL 17 SEP 2026.** It read "the drawing room and the dining room stood on the west
    gable, the library on the east". At the merge of Phase 13 into the second Phase 11 line the
    CODE moved as well as the record -- main's WP-11.17 entrance front and WP-11.18 partition
    share -- so this one-element reading is a THIRD placement belonging to neither parent: the
    drawing room is drawn at x = 37.5 and its fire is refused, the dining room holds the west
    gable and the library the east. That is `conftest.as_one_element`'s own recorded lesson
    (CLAUDE.md, WP-13.5): a control that reverts SOME of an edit and is read as though it
    reverted all of it. The strip still reaches all three branches, which is what it is for, so
    the fixture stands; what was corrected is the account of why."""
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
    # AND IT DRAWS TWO AGAIN AT THE 17 SEP MERGE, WHICH IS THE DIRECTION THE DOCSTRING ABOVE
    # ASKED FOR AND THE REASON IT ASKED TO BE LOUD. Main's WP-11.17 entrance anchor and
    # WP-11.18 `partition` share re-place this ground floor, and the DINING room is back on the
    # block's west face -- so its fire has an exterior flue and `west-stack` is drawn, serving
    # `dining`, at (-3.125, 30.013). The DRAWING room is still 7.0 ft inboard and is still
    # refused, with the same honest reason: the wall, the distance, and no interior stack
    # invented in its place. So the cost WP-13.5 measured is half paid back, and the half that
    # remains is named rather than absorbed into a count.
    #
    # The test's own name is left as written -- this project leaves original text -- and the
    # assertion is what moved. Both stacks are named, so a fire gaining or losing a flue fails
    # here either way rather than a count of two passing on the wrong two.
    st = {s["flue"] for s in shipped["hearths"]["stacks"]}
    assert st == {"east-stack", "west-stack"}, (
        "the shipped Tidewater sheet drew ONE stack at WP-13.5 and TWO before it; it draws "
        f"{sorted(st)} now. A fire losing its flue is the placement getting worse and a third "
        "stack is a fire nobody has accounted for -- re-derive per room before moving this.")
    served = {s["flue"]: sorted(s.get("serves") or []) for s in shipped["hearths"]["stacks"]}
    assert served == {"west-stack": ["dining"], "east-stack": ["library"]}, (
        f"the stacks stand, and serve the wrong fires: {served}")
    un = shipped["hearths"]["unplaced"]
    breasts = [u for u in un if u.get("rule") == "hearths.breast"]
    assert {u["room"] for u in breasts} == {"drawing"}, (
        f"the refused fires are {sorted(u['room'] for u in breasts)}, not just the drawing "
        "room's. `dining` regained its flue at the merge; if it loses it again that is a "
        "placement regression and not a number to re-pin.")
    for u in breasts:
        why = u["reason"]
        assert "no exterior wall carries its flue" in why, why
        assert "a fire with no flue is not drawn" in why, why
        assert "interior stack is not modelled" in why, (
            "the refusal must say an interior stack is not invented in its place")
    # AND THE STACK ITSELF IS REFUSED ON ITS OWN ACCOUNT, not merely absent: a stack over no
    # fire is not placed (WP-11.4), and the record says so where a reader will look.
    #
    # THAT CLAUSE WAS ASSERTED HERE AND IS DRIVEN NOW, because the merge took its subject away.
    # With `dining` back on the west face the west stack HAS a fire, so no stack on this record
    # is refused -- and this was the ONE site in the tree reading that refusal, so leaving the
    # clause as an assertion about the shipped house would have deleted the rule's only guard.
    # It moves to `test_a_stated_flue_with_no_fire_is_refused_by_name` below, DRIVEN, on the
    # precedent this corpus sets for the blind bay (WP-12.2) and the terrace (WP-11.10).
    assert not [u for u in un if u.get("flue")], (
        f"a stated flue is refused on the shipped record: {[u.get('flue') for u in un if u.get('flue')]}. "
        "That is a fire losing its stack -- re-derive per room, and note that the DRIVEN guard "
        "below no longer needs to stand in for the corpus.")
    # the drawn-false breast still carries its rectangle, so a later reader can see WHERE the
    # fire would have been: 7.0 ft inboard of the element's west face, against another room.
    off = [b for b in shipped["hearths"]["breasts"] if not b["drawn"]]
    assert {b["room"] for b in off} == {"drawing"}, off
    assert all(b["judged"] and round(b["x_ft"], 2) == 7.0 for b in off), off


def test_a_stated_flue_with_no_fire_is_refused_by_name(shipped):
    """WP-11.4's rule, DRIVEN because the 17 Sep merge took its corpus instance away.

    A stack over no fire is not placed and the record says why. Until the merge the shipped
    Tidewater record exercised that on its west flue -- both west-wall fires were inboard, so
    the flue carried nothing -- and it was the ONLY site in the tree reading the refusal. Main's
    entrance anchor puts `dining` back on the west face, so the flue has a fire again and the
    branch is unreachable from all sixteen plans.

    Deleting the clause would have removed the rule's only guard on the strength of the corpus
    getting better, which is this repository's most-repeated way of going quiet. The state is
    stated instead: the same record with its dining hearth taken away, so the west flue is
    stated and serves nothing."""
    import copy
    q = copy.deepcopy(shipped)
    hit = 0
    for lv in q.get("levels") or []:
        for r in lv.get("rooms") or []:
            if r.get("id") == "dining" and r.get("hearth"):
                r.pop("hearth"); hit += 1
    assert hit == 1, (
        "the shipped record no longer states a dining hearth, so this drive does nothing -- "
        "re-cut it onto whichever room still shares the west flue")
    out = TH.hearth_pass(q, PC.load_corpus(), {})
    stack = [u for u in (out.get("unplaced") or []) if u.get("flue") == "west-stack"]
    assert len(stack) == 1, (
        f"the west flue carries no fire and is not refused: {out.get('unplaced')}")
    assert "no fire for its stack to stand over" in stack[0]["reason"], stack[0]
    assert not [x for x in (out.get("stacks") or []) if x.get("flue") == "west-stack"], (
        "a stack is drawn over no fire")
    # the CONTROL: the east flue still has its library fire and is still drawn, so the drive
    # removed one fire rather than breaking the pass.
    assert [x for x in (out.get("stacks") or []) if x.get("flue") == "east-stack"], out


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
        """THE SPECIMEN IS CHOSEN FROM THE READING AND NEVER NAMED. This read `drawing` until
        the merge of Phase 13 into the second Phase 11 line moved that room to x = 37.5 and
        its fire off the west face; a guard naming a room measures one placement, which is
        what WP-11.17 re-cut two facade tests for. Every breast the placement layer DREW is
        re-judged here through `HE.breast` itself, so the direct call and the placement layer
        cannot disagree about one wall."""
        drawn = [row for row in placed["hearths"]["breasts"] if row["drawn"]]
        assert len(drawn) >= 2, (
            "no breast on this placement stands on a boundary wall, so the drawn branch is "
            "not exercised -- re-pick the specimen from the reading, never skip")
        assert {row["wall"] for row in drawn} == {"W", "E"}, (
            "both gable ends must carry a drawn fire, or the strip exercises one branch twice")
        Wf = placed["footprint"]["width_ft"]
        for row in drawn:
            r = _room(placed, row["room"])
            b = HE.breast(r, r["hearth"][0], bounds=_bounds(placed))
            assert not b.get("undrawable") and "unplaced" not in b, (row["room"], b)
            assert b["wall"] == row["wall"]
            # The breast stands ON the face and projects into the room, so its near edge is
            # the face itself -- x for a W wall, x + the projection for an E one.
            near = b["x_ft"] if row["wall"] == "W" else b["x_ft"] + b["width_ft"]
            assert abs(near - (0.0 if row["wall"] == "W" else Wf)) < 0.01, (row["room"], near)

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
    def test_the_one_element_reading_draws_TWO_of_three_and_names_the_third(self, placed):
        """THE `placed` FIXTURE'S OWN PREMISE, RE-DERIVED AT THE MERGE OF PHASE 13 INTO THE
        SECOND PHASE 11 LINE (17 Sep 2026). It read all three drawn and no refusal; the merge
        moved the placement, the drawing room is drawn at x = 37.5, and its declared W wall is
        37.5 ft inboard of the element's west face. The REASON is asserted beside the census,
        so a refusal arriving for some other cause cannot pass here as this one."""
        h = placed["hearths"]
        assert h["placed_from"] == "stated-hearths"
        assert [(r["room"], r["drawn"], r["judged"]) for r in h["breasts"]] == [
            ("drawing", False, True), ("dining", True, True), ("library", True, True)]
        assert {r["wall"] for r in h["breasts"] if r["drawn"]} == {"W", "E"}
        assert [u["room"] for u in h["unplaced"]] == ["drawing"]
        assert h["unplaced"][0]["rule"] == "hearths.breast"
        row = next(r for r in h["breasts"] if r["room"] == "drawing")
        assert row["unplaced"]["needs"] == {"wall_on_the_element_boundary": "W"}
        assert row["unplaced"]["have"]["inboard_ft"] == 37.5
        assert placed["opening_report"]["hearths_refused"] == 1

    def test_a_released_wall_is_refused_in_the_record_and_on_the_plate(self, placed, tmp_path):
        """THE CORPUS REACHES THIS NOW AND THE DRIVE IS NO LONGER THE ONLY ROUTE. On this
        placement the drawing room's declared W wall is 37.5 ft inboard, so its fire is refused
        in the record and BOTH registers draw no fireplace for it -- the working register a
        dashed ghost with the reason, the presentation register nothing but the record.

        It used to move that same room 19 ft inboard by hand and assert the same thing. At the
        merge of Phase 13 into the second Phase 11 line that drive became a mutation which
        changes no state -- WP-11.15's *a fixture where both branches return the same number
        guards neither* -- so the FLIP is driven in the test below instead, on a fire this
        placement draws."""
        h = placed["hearths"]
        row = next(r for r in h["breasts"] if r["room"] == "drawing")
        assert row["drawn"] is False and row["judged"] is True
        assert row["unplaced"]["have"]["inboard_ft"] == 37.5
        ref = [u for u in h["unplaced"] if u.get("room") == "drawing"]
        assert len(ref) == 1 and ref[0]["rule"] == "hearths.breast"
        assert ref[0]["reason"] == row["why"]
        fl = next(f for f in h["flues"] if f["flue"] == "west-stack")
        assert fl["serves"] == ["dining"] and fl["stated"] == ["drawing", "dining"]
        g = _room(placed, "dining")["geometry"]
        assert abs(fl["position_ft"] - (g["y_ft"] + g["depth_ft"] / 2)) < 0.002, (
            "the flue stands at the axis of its one served fire")
        p = copy.deepcopy(placed)
        wk = str(tmp_path / "working.svg")
        RP.render(p, wk, register="working")
        svg = open(wk, encoding="utf-8").read()
        assert svg.count("fireplace,") == 2, "two fires drawn, the refused one not"
        assert 'data-hearth-refused="drawing"' in svg
        assert "fireplace NOT DRAWN" in svg and "no flue" in svg
        pr = str(tmp_path / "presentation.svg")
        RP.render(copy.deepcopy(placed), pr, register="presentation")
        svg2 = open(pr, encoding="utf-8").read()
        assert svg2.count("fireplace,") == 2
        assert "data-hearth-refused" not in svg2, "the presentation register draws nothing for it"

    def test_releasing_a_DRAWN_fire_flips_its_verdict(self, placed, C):
        """DRIVEN, and the half that proves the verdict is a property of the PLACEMENT rather
        than of the room's name: move the dining room -- whose fire this placement draws -- off
        the west face, and its breast is refused under the same rule while the library's,
        untouched, is not. Without this the strip would assert a refusal that is true of one
        room on one tree and never that the judge is looking at the geometry."""
        p = copy.deepcopy(placed)
        before = {r["room"]: r["drawn"] for r in p["hearths"]["breasts"]}
        assert before["dining"] is True and before["library"] is True, (
            "the fixture no longer draws the fire this drives -- re-pick it from the reading")
        _room(p, "dining")["geometry"]["x_ft"] = 21.0
        TH.hearth_pass(p, C, {})
        after = {r["room"]: r["drawn"] for r in p["hearths"]["breasts"]}
        assert after["dining"] is False and after["library"] is True
        u = next(u for u in p["hearths"]["unplaced"] if u.get("room") == "dining")
        assert u["rule"] == "hearths.breast" and "21.0 ft inboard" in u["reason"]

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
    def test_the_squares_stand_on_the_stated_flues_and_not_on_the_centre_line(self, placed):
        """Before WP-13.2: both squares at the mid-depth of the end wall, 19.085 ft, from the
        rectangle alone. Now each stands on its flue, at the axis of the fire that flue serves.
        The axes are DERIVED from the rooms here rather than pinned, because the merge of Phase
        13 into the second Phase 11 line moved them and a literal would have to be re-typed at
        every placement change without anything saying what it is.

        **THE MEAN OF TWO FIRES IS NOT EXERCISED HERE AND IT USED TO BE.** Until that merge the
        west flue served the drawing and dining rooms both and this test read their mean; on
        this placement the drawing room's fire is refused, so every flue serves exactly one
        fire and a mean over one number is that number. The mean is driven in
        `test_the_gather_is_disclosed_where_one_stack_serves_two_fires_apart` below, which also
        asserts that no shipped stack reaches it."""
        h = placed["hearths"]
        by = {s["flue"]: s for s in h["stacks"]}
        assert set(by) == {"west-stack", "east-stack"}
        w, e = by["west-stack"], by["east-stack"]
        assert w["wall"] == "W" and e["wall"] == "E"
        axis = {r["id"]: r["geometry"]["y_ft"] + r["geometry"]["depth_ft"] / 2
                for r in placed["levels"][0]["rooms"] if r.get("geometry")}
        assert abs((w["y_ft"] + w["depth_ft"] / 2) - axis["dining"]) < 0.002
        assert abs((e["y_ft"] + e["depth_ft"] / 2) - axis["library"]) < 0.002
        assert w["serves"] == ["dining"] and e["serves"] == ["library"]
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

    def test_the_gather_is_disclosed_where_one_stack_serves_two_fires_apart(self, placed, C):
        """THE FIGURE THIS PACKAGE CANNOT CLOSE, STATED AS ONE -- and DRIVEN, because no
        placement in this corpus reaches it any more.

        Where one flue carries two fires, both breasts default to the centre of their own end
        wall (the schema's rule for an absent `position_ft`) and a 22 in square at the flue's
        mean stands behind neither. The square is not moved and not doubled
        (`build/hearths.py`'s docstring says why); the gather is written on the stack AND on
        each breast row, so the plate's reader and the gate's are told the same number.

        Until the merge of Phase 13 into the second Phase 11 line the west flue of this very
        fixture carried the drawing and dining rooms both, and this was read off it. It no
        longer is, so the PREMISE is asserted and the state is built by hand -- WP-11.10's
        rule, met for the second time in this file."""
        assert all(len(s["serves"]) < 2 for s in placed["hearths"]["stacks"]), (
            "a shipped stack serves two fires again -- read this off the corpus rather than "
            "driving it, and say which placement changed")
        p = copy.deepcopy(placed)
        lv0 = p["levels"][0]
        # The drawing room takes the kitchen's rectangle on the west face. The kitchen states
        # no hearth, so nothing is lost and the level is still a tiling.
        _room(p, "drawing")["geometry"] = dict(_room(p, "kitchen")["geometry"])
        lv0["rooms"] = [r for r in lv0["rooms"] if r["id"] != "kitchen"]
        TH.hearth_pass(p, C, {})
        h = p["hearths"]
        fl = next(f for f in h["flues"] if f["flue"] == "west-stack")
        assert fl["serves"] == ["drawing", "dining"], "the drive did not put both fires on it"
        axis = {r["id"]: r["geometry"]["y_ft"] + r["geometry"]["depth_ft"] / 2
                for r in lv0["rooms"] if r.get("geometry")}
        assert abs(fl["position_ft"] - (axis["drawing"] + axis["dining"]) / 2) < 0.002, (
            "the flue is not at the mean of the two fires it serves")
        w = next(s for s in h["stacks"] if s["flue"] == "west-stack")
        assert w["behind"] == []
        assert set(w["gathered"]) == {"drawing", "dining"}
        # THE GATHER IS A FIGURE, NOT A FLAG: the clear gap between the square's own run and
        # each breast's, derived here rather than pinned.
        rows = {r["room"]: r for r in h["breasts"]}
        for rid, g in w["gathered"].items():
            b = rows[rid]
            lo, hi = b["y_ft"], b["y_ft"] + b["depth_ft"]
            gap = max(w["y_ft"] - hi, lo - (w["y_ft"] + w["depth_ft"]))
            assert abs(g - gap) < 0.01, (rid, g, gap)
            assert g > 0
        e = next(s for s in h["stacks"] if s["flue"] == "east-stack")
        assert e["behind"] == ["library"] and e["gathered"] == {}
        assert rows["library"]["flue_stack"] == {"behind": True, "gathered_ft": 0.0}
        assert rows["drawing"]["flue_stack"]["behind"] is False
        assert rows["drawing"]["flue_stack"]["gathered_ft"] == w["gathered"]["drawing"]

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

    def test_the_breast_takes_the_wall_and_the_sash_is_seated_BESIDE_it(self, placed):
        """THE CORPUS NO LONGER REFUSES A SASH FOR A BREAST, AND THAT IS A MEASUREMENT RATHER
        THAN A SILENCE. This read the dining room's 12.07 ft W wall, on which a 3.5 ft sash did
        not fit beside a 4.76 ft breast; the merge of Phase 13 into the second Phase 11 line
        drew that wall 20.17 ft long and it does fit. What is still exercised -- and is the
        package's actual subject -- is that the sash is MOVED off the breast's centre rather
        than drawn dead inside it. The refusal branch is DRIVEN below."""
        g = _room(placed, "dining")["geometry"]
        dw = next(w for w in _room(placed, "dining")["windows"] if w["wall"] == "W")
        assert dw["count"] == 1 and len(dw["positions_ft"] or []) == 1 and "unplaced" not in dw
        row = next(r for r in placed["hearths"]["breasts"] if r["room"] == "dining")
        lo, hi = row["y_ft"], row["y_ft"] + row["depth_ft"]
        assert abs((lo + hi) / 2 - (g["y_ft"] + g["depth_ft"] / 2)) < 0.01, (
            "the breast is no longer at the centre of its own wall, so a sash left where this "
            "pass would default it would not have been inside one -- re-derive the subject")
        pos = dw["positions_ft"][0]
        gap = max(lo - (pos + dw["width_ft"] / 2), (pos - dw["width_ft"] / 2) - hi)
        assert gap >= OP.MASONRY_PIER_FT, (pos, lo, hi, gap)
        assert not [w for lv in placed["levels"] for r in lv["rooms"]
                    for w in (r.get("windows") or [])
                    if "the chimney" in ((w.get("unplaced") or {}).get("reason") or "")], (
            "a sash is refused for masonry again -- re-derive the count and say which "
            "placement changed, rather than re-pinning the total below")
        assert placed["opening_report"]["windows_unplaced"] == 13, (
            "16 on this branch before the merge; re-derive, never re-pin")

    def test_a_sash_that_does_not_fit_beside_a_breast_is_refused_by_name_and_the_count_is_kept(self):
        """DRIVEN on a hand-built room, because no placement in this corpus leaves a wall too
        short for its own sash any more. A 12 ft wall with a 4.76 ft breast at its centre
        leaves 3.62 ft either side; the pier takes 1.0 of each and a 3.5 ft sash does not go.
        Refused NAMING what took the wall, and the DECLARED count is untouched (WP-6.2).

        THE CONTROL IS THE SECOND HALF: withdraw the breast and the same wall seats the same
        sash, so the refusal is the masonry's and not the wall's length. Without it this passes
        on a room that could never have held a window at all."""
        def _room_and_hearths(with_breast):
            r = {"id": "hearthroom", "type": "dining-room",
                 "geometry": {"x_ft": 0.0, "y_ft": 0.0, "width_ft": 14.0, "depth_ft": 12.0},
                 "windows": [{"wall": "W", "count": 1, "width_ft": 3.5}]}
            breasts = [{"level": 0, "room": "hearthroom", "wall": "W", "drawn": True,
                        "x_ft": 0.0, "y_ft": 3.62, "width_ft": 1.8, "depth_ft": 4.76}]
            return r, {"breasts": breasts if with_breast else [], "stacks": []}

        r, h = _room_and_hearths(True)
        rep = {"windows_unplaced": 0, "windows_placed": 0}
        OP._place_windows([r], {}, 14.0, 12.0, rep, None, h, 0)
        win = r["windows"][0]
        assert win["count"] == 1, "the declared count was overwritten by the placement outcome"
        assert "positions_ft" not in win
        assert win["unplaced"]["have"]["units_placed"] == 0
        assert "the chimney breast" in win["unplaced"]["reason"], win["unplaced"]
        assert rep["windows_unplaced"] == 1
        r2, h2 = _room_and_hearths(False)
        rep2 = {"windows_unplaced": 0, "windows_placed": 0}
        OP._place_windows([r2], {}, 14.0, 12.0, rep2, None, h2, 0)
        assert r2["windows"][0].get("positions_ft"), (
            "the control does not seat the sash, so the refusal above says nothing about the "
            "breast")
        assert rep2["windows_unplaced"] == 0

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
        """BOTH SPECIMENS ARE TAKEN FROM THE READING. This named `drawing` for the positive
        half until the merge of Phase 13 into the second Phase 11 line refused that fire -- at
        which point the assertion was about a room that reserves nothing either way, so
        withdrawing its verdict could not change anything and neither branch was guarded."""
        rooms = copy.deepcopy(placed["levels"][0]["rooms"])
        fp = placed["footprint"]
        W, H = fp["width_ft"], fp["depth_ft"]
        hearths = copy.deepcopy(placed["hearths"])
        drawn = [r for r in hearths["breasts"] if r["drawn"]]
        refused = [r for r in hearths["breasts"] if not r["drawn"]]
        assert drawn, "no breast is drawn on this placement, so nothing is reserved"
        assert refused, "no breast is refused on this placement, so the negative half is blind"
        key = (drawn[0]["room"], drawn[0]["wall"])
        occ = {}
        took = OP._reserve_masonry(rooms, occ, W, H, {}, hearths, 0)
        assert key in took and "the chimney breast" in took[key]
        rkey = (refused[0]["room"], refused[0]["wall"])
        assert "the chimney breast" not in took.get(rkey, []), (
            "a fire the pass REFUSED reserved its run; nothing is drawn there")
        drawn[0]["drawn"] = False
        occ2 = {}
        took2 = OP._reserve_masonry(rooms, occ2, W, H, {}, hearths, 0)
        assert "the chimney breast" not in took2.get(key, [])
        assert len(occ2.get(key, [])) < len(occ.get(key, []))

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
