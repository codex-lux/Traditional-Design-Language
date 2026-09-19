"""WP-11.6 — teaching the six layers below the placer that a house can be more than one
rectangle, in the order `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`
rules, measuring after each.

**The ruling's own check is a FALLING COUNT in the record**: `geometry_report.multi_element`
"names six layers today and must name five, then four, then none -- a falling count, in the
record, is how this ruling is checked rather than claimed". These tests hold the count AND the
underlying defect for each layer, so a name cannot be removed from the list without the layer
actually reading the element.

**The regression discipline the whole change is held to**: a plan declaring no second block must
place BYTE-IDENTICALLY. All sixteen plans in this corpus are one rectangle and two ship, so their
placements are the guard.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402
from conftest import untagged_reference_plan  # noqa: E402

GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
OP = modcache.load("openings", os.path.join(ROOT, "build", "openings.py"))


def _is_tagged(plan):
    """Does this record declare a massing element of its own? (WP-11.16.)

    One shipped plan does -- `tidewater-georgian-careful` -- and the sweeps below need to tell it
    from the other fifteen. `GEO.is_block_tag` is the ONE rule for whether a `block` field is an
    element id and is borrowed rather than re-spelled."""
    return any(GEO.is_block_tag(r.get("block"))
               for lv in (plan.get("levels") or []) for r in (lv.get("rooms") or []))


def _shipped_untagged():
    """`tidewater-georgian-careful` with WP-11.16's massing tags STRIPPED.

    THIS FILE USES THAT RECORD FOR TWO JOBS AND WP-11.16 SPLIT THEM. It is the base every
    multi-element fixture below is built from (tag some rooms `west-dependency` and solve), and
    it is the ONE-RECTANGLE CONTROL that half these tests assert is untouched. Both assumed the
    shipped record carried no `block` tag. It carries one now -- a `service` dependency and a
    hyphen -- so a fixture that tags rooms on top of it produces THREE elements where it means
    two (measured: `{'main', 'service', 'west-dependency'}` against `{'main', 'west-dependency'}`,
    and four CP models that were satisfiable came back INFEASIBLE), and every control asserting
    one rectangle was reading a house with a wing.

    Stripping is the same move `tests/test_check_plans.py`'s growth fixture takes and for the
    same reason: **a driven fixture must not inherit whatever the shipped record happens to
    declare** (WP-8.11). What this file tests is the element machinery, not this plan's tagging,
    and the two are independent.

    AND THE 17 SEP MERGE FOUND THIS FILE HOLDING TWO SPELLINGS OF ONE RULE. Main wrote the
    stripping out by hand here; this branch had already lifted it into
    `conftest.untagged_reference_plan` / `as_one_element`, which EIGHT fixtures share. Two
    readers of "what is a container" is how one comes to strip `hyphen` and the other not.
    It delegates now, and the 44 findings-digest and score literals below were re-derived across
    the change and did not move -- which is what says this is one spelling rather than a third."""
    return untagged_reference_plan("tidewater-georgian-careful")[0]


def _fixture():
    """The same tagging `test_geometry.py::_tagged_dependency_plan` uses, kept in step with it
    deliberately: two files measuring two different dependencies would be two houses."""
    p = _shipped_untagged()
    n = 0
    for r in p["levels"][0]["rooms"]:
        if r["type"] in ("kitchen", "pantry", "breakfast-room"):
            r["block"] = "west-dependency"
            r["exterior_walls"] = ["N", "S", "W"]
            n += 1
    assert n >= 2, "the reference plan's service room types have been renamed"
    return p


@pytest.fixture
def placed():
    GEO._SOLVE_CACHE.clear()
    p = _fixture()
    GEO.solve(p, engine="heuristic")
    return p


def _one_rectangle(name="tidewater-georgian-careful"):
    """A shipped record read as the ONE-ELEMENT house it used to be, with any container stripped.

    **EVERY "one rectangle" GUARD IN THIS FILE READS THIS, AND WP-13.5 IS WHY.** Until that
    package no plan in the corpus carried a `block` tag, so "the shipped Tidewater record" and
    "a one-element plan" were the same fixture and the tests below say both. WP-13.5 moved the
    service programme into the dependency that record declares, so they are two fixtures now.
    The PROPERTY each of these guards states -- what the placer, the section, the slab loop and
    the lot cap do with ONE element -- is unchanged and still worth guarding; what changed is
    which record demonstrates it. Stripping keeps the guard on the same house rather than
    swapping in another plan whose numbers would all have to be re-pinned.

    `test_the_shipped_record_really_carries_a_container` below asserts the premise, so the day
    the record loses its tags these fixtures cannot quietly become the old ones again.
    """
    q, _stripped = untagged_reference_plan(name)
    return q


def test_the_shipped_record_really_carries_a_container():
    """The premise of every `_one_rectangle(...)` call above and below. A strip that strips
    nothing leaves a fixture identical to a plain load, and every guard built on it would be
    passing for a reason that has stopped being true."""
    raw = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    tags = {r["id"] for lv in raw["levels"] for r in lv["rooms"] if r.get("block")}
    assert tags == {"kitchen", "pantry", "breakfast", "powder", "cellarstair", "backhall"}, tags
    assert any(r.get("hyphen") for lv in raw["levels"] for r in lv["rooms"])
    assert not any(r.get("block") for lv in _one_rectangle()["levels"] for r in lv["rooms"])


def dep_rooms(p):
    return {r["id"] for lv in p["levels"] if (lv.get("index") or 0) == 0
            for r in lv["rooms"] if r.get("block")}


class TestTheDisclosureFalls:
    def test_it_names_NO_LAYER_and_the_disclosure_survives_anyway(self, placed):
        """The ruling's own check, at the end of its own fall: "must name five, then four, then
        none". All six are taught. **The block does not vanish with the list**, and the facts
        that keep it are why -- the roof is still the main block's alone, and the abutment
        between two adjacent elements is nobody's rule.

        **ONE OF THE TWO SURVIVING FACTS DIED AT ITEM 4 AND THE NOTE HAD TO STOP SAYING IT.**
        It read `engine="cp"` REFUSES a multi-element plan, "so the engine that PROVES is
        unavailable"; the prover places each element in its own rectangle now, and a note
        claiming an engine is unavailable when it is available is the fake-unjudged direction,
        which this corpus treats as exactly as dishonest as a fake pass. The negative assertion
        below is what keeps that sentence from coming back."""
        me = placed["geometry_report"]["multi_element"]
        assert me["elements"] == 2
        assert me["not_element_aware"] == []
        assert "COULD NOT EVALUATE" not in me["note"], (
            "with nothing unjudged the note may not claim an unjudged state -- a fake unjudged "
            "is as dishonest in its own direction as a fake pass")
        assert "REFUSES a multi-element plan" not in me["note"], (
            "the prover places per element since WP-11.6 item 4; saying it refuses would be a "
            "false statement about the engine in the flattering direction")
        assert "places each element in its own rectangle" in me["note"]
        assert "roof" in me["note"]

    def test_a_one_rectangle_plan_discloses_NOTHING(self):
        """Every plan in this corpus is one rectangle. The disclosure exists for the record a
        caller supplies, and a plan with one element has nothing to disclose."""
        GEO._SOLVE_CACHE.clear()
        p = GEO.solve(_shipped_untagged(), engine="heuristic")
        assert p["geometry_report"].get("multi_element") is None
        assert (p["footprint"].get("blocks") or []) == []


class TestOpeningsReadsTheRoomsOwnElement:
    def test_envelopes_maps_a_tagged_room_to_its_dependency(self, placed):
        envs = OP.envelopes(placed)
        deps = dep_rooms(placed)
        assert deps and all(rid in envs for rid in deps)
        dep_el = next(b for b in placed["footprint"]["blocks"] if b["id"] != "main")
        want = (dep_el["x_ft"], dep_el["y_ft"],
                dep_el["x_ft"] + dep_el["width_ft"], dep_el["y_ft"] + dep_el["depth_ft"])
        for rid in deps:
            assert envs[rid] == want, rid

    def test_THE_JOIN_IS_THE_ROOMS_TAG_AND_NOT_A_ROOM_LIST_ON_THE_BLOCK(self, placed):
        """The first version read `b["rooms"]`. `blocks_record` writes id, role, x, y, width,
        depth and area and NO membership, so it found nothing on every plan and left all nine
        refusals in place while reporting success. Pinned, because a room list looks like the
        obvious join and is not there."""
        for b in placed["footprint"]["blocks"]:
            assert "rooms" not in b, (
                "blocks_record grew a room list; envelopes() may now read it, but this test is "
                "the record of why it does not")

    def test_a_one_rectangle_plan_gets_an_EMPTY_map_so_nothing_changes(self):
        p = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json")))
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        assert OP.envelopes(p) == {}, (
            "one element means every caller must fall back to the main block, which is what "
            "keeps the sixteen one-rectangle plans byte-identical by construction")

    def test_boundary_walls_tests_against_the_element_it_is_given(self):
        """The arithmetic itself, away from any plan. A room at x 0..10 in an element at
        x -41..-14 is on NEITHER of that element's faces and on both of a 0..10 one."""
        rect = (-41.0, 9.05, 17.7, 14.67)          # the fixture's kitchen
        el = (-41.0, 9.05, -14.0, 29.12)
        bw = OP._boundary_walls(rect, 63, 38.17, env=el)
        assert set(bw) == {"S", "W"}, bw
        # AND AGAINST THE MAIN BLOCK IT REPORTS `W`, WHICH IS WORSE THAN REPORTING NOTHING.
        # `x <= tol` is satisfied by any x at or west of 0.6, so a room 41 ft WEST of the house
        # tests as sitting on the house's west face. The old reading did not merely lose the
        # dependency's walls, it asserted one that is forty-one feet away -- which is how the
        # entry's "a window drawn fourteen feet from the room" arises. This assertion is the
        # correction of my own first draft, which claimed the old call returned nothing.
        assert OP._boundary_walls(rect, 63, 38.17) == {"W": (9.05, 23.72)}

    def test_the_refusals_are_GONE_and_a_driven_one_still_comes_back(self, placed):
        """**THE COUNT MOVED AGAIN AT ITEM 4 AND THIS TEST HAD TO CHANGE SHAPE.** It was 9 of 14
        dependency openings refused before layer 1 and 5 after, and it pinned the kitchen's north
        window as an honest refusal: the room's north edge stood 23.72 against its element's
        29.12, so it really did not reach that face. Item 4 found `derive_footprint` sizing the
        MAIN block from the whole building's programme, wing included -- 29% too large -- and
        sizing it from its own rooms re-proportioned the wing. **The kitchen now spans its
        element's full depth and all five remaining refusals are gone**, which leaves nothing for
        the old assertion to be honest about.

        A count of zero is exactly the reading this corpus distrusts, so the discrimination is
        DRIVEN instead: pull four feet off the kitchen's north face and `_boundary_walls` must
        stop naming N. Asserted on the arithmetic layer 1 changed rather than through `place()`,
        which re-solves."""
        deps = dep_rooms(placed)
        refused = [(r["id"], w["wall"]) for lv in placed["levels"] for r in lv["rooms"]
                   if r["id"] in deps for w in (r.get("windows") or []) if w.get("unplaced")]
        assert refused == [], refused
        kitchen = next(r for lv in placed["levels"] for r in lv["rooms"] if r["id"] == "kitchen")
        envs = OP.envelopes(placed)
        el = envs["kitchen"]
        assert set(OP._boundary_walls(OP._rect(kitchen), placed["footprint"]["width_ft"],
                                      placed["footprint"]["depth_ft"], env=el)) >= {"N", "S"}
        pulled = dict(kitchen, geometry=dict(kitchen["geometry"],
                                             depth_ft=kitchen["geometry"]["depth_ft"] - 4.0))
        walls = OP._boundary_walls(OP._rect(pulled), placed["footprint"]["width_ft"],
                                   placed["footprint"]["depth_ft"], env=el)
        assert "N" not in walls, (walls, "a room four feet off its element's face still reaches "
                                         "it -- the test is not reading the element")
        assert "S" in walls, walls

    def test_and_a_dependency_room_now_places_openings_AT_ALL(self, placed):
        """The headline. Before this, every opening on every dependency room was refused with
        'the placement puts this room on no such boundary wall' -- an instrument's refusal
        wearing a house's clothes."""
        deps = dep_rooms(placed)
        placed_ct = sum(
            1 for lv in placed["levels"] for r in lv["rooms"] if r["id"] in deps
            for w in (r.get("windows") or []) if not w.get("unplaced"))
        assert placed_ct >= 3, "no dependency window was placed at all"


ST = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))


class TestStructureIsPerElement:
    """Layer 2. Ruling 1: an element has its own envelope. `build_section` runs
    `wall_lines`/`bearing_lines`/`span_check` once per element over that element's own rooms, at
    that element's own origin."""

    def test_the_main_elements_wall_set_is_not_contaminated(self, placed):
        """Before: a dependency partition at x -23.3 entered the wall set of a 0-63 block, and
        `span_check` leaned the main block's floor on it."""
        sec = ST.build_section(placed)
        W = placed["footprint"]["width_ft"]
        bad = [w for lv in sec["levels"] for w in lv["walls"]
               if w.get("element") == "main" and w["axis"] == "x"
               and (w["position_ft"] < -0.01 or w["position_ft"] > W + 0.01)]
        assert bad == [], bad

    def test_the_dependency_has_its_own_two_envelope_walls(self, placed):
        """Before: 0 of 2. Its structure was unmodelled -- not wrong, ABSENT, which reads as a
        building with no walls rather than as a building nobody measured."""
        sec = ST.build_section(placed)
        el = next(b for b in placed["footprint"]["blocks"] if b["id"] != "main")
        xs = {round(w["position_ft"], 2) for lv in sec["levels"] for w in lv["walls"]
              if w.get("element") == el["id"] and w["axis"] == "x"}
        for face in (round(el["x_ft"], 2), round(el["x_ft"] + el["width_ft"], 2)):
            assert any(abs(x - face) < 0.51 for x in xs), (face, sorted(xs))

    def test_no_span_is_computed_across_the_gap(self, placed):
        """The entry's own words: "manufactures a clear span across the gap between the house and
        the dependency". It cannot now, because each element's `span_check` sees only its own
        bearing lines -- by construction rather than by a filter."""
        sec = ST.build_section(placed)
        gap = [s for lv in sec["levels"] for s in lv["spans"]
               if s["from_ft"] < -0.01 and s["to_ft"] > 0.01]
        assert gap == [], gap

    def test_AND_THE_DEPENDENCYS_OWN_SPANS_ARE_JUDGED_AND_FAIL(self, placed):
        """The shield lesson arriving exactly as the ruling predicted. Teaching openings made
        the dependency's windows real; teaching structure makes its spans real, and they are
        over capacity -- 27.0 ft and 20.07 ft against a 20 ft hand-framed cap. A silence became
        a finding, which is the whole point of modelling it."""
        sec = ST.build_section(placed)
        el = next(b for b in placed["footprint"]["blocks"] if b["id"] != "main")
        over = [s for lv in sec["levels"] for s in lv["spans_exceeding_capacity"]
                if s.get("element") == el["id"]]
        # RE-CUT AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026), AND THE SHIELD LESSON SURVIVES
        # IT. Main's point is that the dependency's structure stopped being a SILENCE -- its
        # walls, its bearing lines and its spans are computed against its own envelope. That
        # still holds and is asserted below. What no longer holds is that they FAIL: the other
        # branch's WP-11.13 gives a non-main element's box a derived grid allowance (its rooms
        # could not fit the inward-rounded box without one), which changes the dependency's depth
        # and takes its worst span inside the 20 ft cap.
        #
        # "It is over capacity" was the finding at the time and is not the invariant. Asserting
        # it would fail on a placement that had got better, which is the guard-pins-an-outcome
        # shape this corpus keeps re-cutting -- and it would also mean a dependency could only
        # pass this suite by being badly framed.
        walls = [w for lv in sec["levels"] for w in lv["walls"] if w.get("element") == el["id"]]
        spans = [s for lv in sec["levels"] for s in lv["spans"] if s.get("element") == el["id"]]
        assert walls, "the dependency has no walls of its own: its structure is unmodelled again"
        assert spans, "the dependency has walls but no spans: it is modelled and not judged"
        if over:
            assert max(s["span_ft"] for s in over) > 20.0

    def test_a_one_element_plan_carries_no_element_tag_at_all(self):
        """The byte-identity guard. Sixteen records have never needed one and must not grow one."""
        sec = ST.build_section(_shipped_untagged())
        assert all("element" not in w for lv in sec["levels"] for w in lv["walls"])
        assert all("element" not in s for lv in sec["levels"] for s in lv["spans"])
        # and the numbers this plan has always reported
        over = [s for lv in sec["levels"] for s in lv["spans_exceeding_capacity"]]
        # RE-DERIVED AT THE MERGE (8 Sep 2026): 53.94 -> 35.5 ft. Both branches changed the
        # placement, so the worst span on this fixture is neither parent's. What the line
        # is for -- the span is OVER the 20 ft capacity and therefore judged -- is
        # unchanged, and the capacity itself is untouched.
        # AND AGAIN AT WP-11.17: 35.5 -> 54.0 ft, ON THIS FIXTURE AND NOT ON THE SHIPPED PLAN.
        # `_shipped_untagged()` strips the tags, so this is the Tidewater record as ONE
        # rectangle -- 63 x 38.17 -- and the entrance anchor lays its porch on that 63 ft front,
        # which moves where the slicer is free to cut and takes one bay module off the grid.
        # The SHIPPED (tagged) record's worst span FELL over the same package, 45.0 -> 45.0 with
        # its four runs all shorter (`tests/test_span_findings.py` carries the charge, 130.5 ->
        # 119.7), and the corpus worst is unchanged at 60.0 ft on a plan the anchor does not
        # reach. The 20 ft capacity and `bearing_lines`' 0.75 ft tolerance are untouched.
        # AND AGAIN AT WP-11.18: 54.0 -> 63.0 ft, on this fixture and not on the shipped plan.
        # `partition`'s stated share stops at the closer side now, so the groups either side of
        # the porch cut are different sizes and the slicer's cuts move with them; on a 63 ft
        # front a worst span of 63.0 is the whole width, which is this fixture's own shape and
        # the reason it is a control rather than a house. The SHIPPED (tagged) record's worst
        # span is unchanged at 45.0 ft. The 20 ft capacity and `bearing_lines`' 0.75 ft
        # tolerance are untouched, and the span is still OVER it and therefore judged.
        assert round(max(s["span_ft"] for s in over), 2) == 63.0


def _forced(placed):
    """The fixture with the dependency's windows stripped of their placement.

    THE CONDITION HAS TO BE DRIVEN AND THAT IS THIS PACKAGE'S SHARPEST FINDING. `plan_check`'s
    landlocked test short-circuits at `if seated: continue` -- it runs ONLY on a room whose
    windows are all unplaced. Teaching `openings` at layer 1 seated the dependency's windows, so
    the count of "reaches no exterior wall" findings fell 2 -> 0 **while the `touches` arithmetic
    four lines below still read `fp_w`/`fp_h` and was still wrong**. A meter watching the finding
    would have crossed this layer off four commits early."""
    deps = dep_rooms(placed)
    forced = json.loads(json.dumps(placed))
    for lv in forced["levels"]:
        for r in lv["rooms"]:
            if r["id"] in deps:
                for w in (r.get("windows") or []):
                    w["unplaced"] = {"reason": "forced to reach the touches test"}
    return forced


class TestTheCriticReadsTheRoomsOwnElement:
    """Layer 5. Ruling 4: the drawn layer measures `touches` against the room's OWN element, and
    where a wall of that element faces the gap the finding says so in its own words."""

    def test_the_symptom_is_absent_as_shipped_and_that_is_NOT_the_evidence(self, placed):
        """Kept from when this class recorded the opposite. The symptom was gone from layer 1
        onward and the layer was still wrong; every other test here drives the condition."""
        c = PC.check(placed)
        assert not [f for f in c["findings"]
                    if "no exterior wall" in (f.get("statement") or "")
                    and f.get("room") in dep_rooms(placed)]

    def test_a_dependency_room_is_NO_LONGER_convicted_of_being_landlocked(self, placed):
        """The headline, and it is a false conviction removed rather than a check loosened: the
        kitchen sits on its own element's south and west faces and was told it was "drawn in the
        middle of the house"."""
        deps = dep_rooms(placed)
        c = PC.check(_forced(placed))
        convicted = {f["room"] for f in c["findings"]
                     if f.get("kind") == "drawn-landlocked" and f.get("room") in deps}
        assert convicted == set(), convicted

    def test_AND_THE_TWO_GENUINE_INTERIOR_ROOMS_ARE_STILL_CONVICTED(self, placed):
        """The control, and without it this is a loosening rather than a fix. A room that reads
        `[]` against the main block AND against its own element really is in the middle of the
        house, and must keep the finding the dependency rooms lost.

        **IT WAS TWO ROOMS AND IS ONE, AND THE REASON IS ITEM 4 RATHER THAN A WEAKER GUARD.**
        Sizing the main block from its own rooms took it from 63 x 38.17 to 45 x 41.4, and
        `chamber2` -- which had been drawn in the middle of an over-large block -- now reaches
        its east wall. It is not landlocked any more because it is not landlocked, which is
        what a smaller and honestly-sized block does. `stair` still is, on both readings."""
        c = PC.check(_forced(placed))
        still = {f["room"] for f in c["findings"] if f.get("kind") == "drawn-landlocked"}
        # RE-CUT AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026): the convicted room is
        # `chamber2` here, not `stair`. This docstring already records the set changing once for
        # exactly this reason -- "it was two rooms and is one ... because it is not landlocked,
        # which is what a smaller and honestly-sized block does" -- and the merged placement,
        # which is neither parent's, moves it again. NAMING A ROOM PINNED AN ACCIDENT; the two
        # properties this control exists for are unchanged and are what is asserted: a genuinely
        # interior room still carries the finding, and no dependency room does. Without the
        # first, the fix is a loosening.
        assert still, "no room is landlocked at all: the finding the dependency rooms lost has "\
                      "gone from every room, which is a loosening rather than a fix"
        assert not (still & dep_rooms(placed)), still

    def test_the_finding_it_takes_instead_NAMES_the_element(self, placed):
        deps = dep_rooms(placed)
        c = PC.check(_forced(placed))
        rows = [f for f in c["findings"]
                if f.get("kind") == "drawn-window-off-the-placed-wall" and f.get("room") in deps]
        assert {f["room"] for f in rows} >= {"kitchen", "breakfast"}, rows
        for f in rows:
            assert f.get("element") == "west-dependency", f
            assert "west-dependency element" in f["statement"], f["statement"]
        by = {f["room"]: sorted(f["lit_walls"]) for f in rows}
        # ITEM 4 MOVED THE KITCHEN'S ANSWER FROM ["S", "W"] TO ["N", "S", "W"]: with the main
        # block sized from its own rooms the wing is re-proportioned and the kitchen spans its
        # element's full depth, so it reaches the north face as well. The breakfast room is
        # unmoved. Both are still measured against the ELEMENT and both would be `[]` against
        # the main block, which is the thing under test.
        # AND THE 17 SEP MERGE MOVED THE BREAKFAST ROOM THE SAME WAY, FOR THE SAME REASON:
        # ["E", "S"] -> ["E", "N", "S"]. Main's WP-11.17 entrance anchor and WP-11.18
        # `partition` share re-proportion this fixture's wing again, and the breakfast room now
        # spans its element's full depth as the kitchen already did, so it reaches the north
        # face too. The KITCHEN is unmoved at ["N", "S", "W"]. Both are still measured against
        # the ELEMENT and both would be `[]` against the main block, which is the thing under
        # test and is what the two assertions above hold.
        assert by["kitchen"] == ["N", "S", "W"] and by["breakfast"] == ["E", "N", "S"], by

    def test_A_WALL_FACING_THE_GAP_IS_NAMED_exterior_to_the_weather_interior_to_the_view(
            self, placed):
        """Ruling 4's second half, and it is REACHABLE on this fixture rather than recorded as
        unreproduced: the breakfast room's east wall is the dependency's east face, which looks
        across the 14 ft hyphen gap at the main block. The kitchen's south and west faces look at
        open ground and take no note, which is what makes this a discrimination."""
        c = PC.check(_forced(placed))
        rows = {f["room"]: f for f in c["findings"]
                if f.get("kind") == "drawn-window-off-the-placed-wall"}
        b = rows["breakfast"]
        assert b["walls_across_a_gap"] == ["E"], b
        assert "exterior to the weather and interior to the view" in b["statement"]
        assert "look across the gap at the main element" in b["statement"]
        assert rows["kitchen"]["walls_across_a_gap"] == [], rows["kitchen"]
        assert "interior to the view" not in rows["kitchen"]["statement"]

    def test_faces_across_a_gap_REFUSES_A_DIAGONAL_NEIGHBOUR(self):
        """The ruling refuses the diagonal case rather than modelling it, and that refusal is one
        condition here: a face looking PAST the corner of another block is looking at the yard,
        so the perpendicular overlap is required. Away from any plan, because no placement this
        engine produces is diagonal."""
        el = (0.0, 0.0, 10.0, 10.0)
        beside = {"footprint": {"blocks": [
            {"id": "el", "x_ft": 0.0, "y_ft": 0.0, "width_ft": 10.0, "depth_ft": 10.0},
            {"id": "east", "x_ft": 20.0, "y_ft": 2.0, "width_ft": 10.0, "depth_ft": 6.0}]}}
        assert OP.faces_across_a_gap(beside, el) == {"E": "east"}
        diagonal = {"footprint": {"blocks": [
            {"id": "el", "x_ft": 0.0, "y_ft": 0.0, "width_ft": 10.0, "depth_ft": 10.0},
            {"id": "ne", "x_ft": 20.0, "y_ft": 20.0, "width_ft": 10.0, "depth_ft": 6.0}]}}
        assert OP.faces_across_a_gap(diagonal, el) == {}, (
            "a block past the corner is yard, not a gap this element looks across")

    def test_a_one_rectangle_plan_is_UNTOUCHED_finding_for_finding(self):
        """The regression discipline, at its strongest form: not a count but every finding's
        kind, room and statement. Measured identical on both shipped plans before and after.

        **RE-PINNED AT WP-11.7, AND THE TEST'S OWN MESSAGE SAYS TO SAY WHAT MOVED.** The facade
        layer joined `plan_check`'s drawn layer, which is where it belongs (everything it reads is
        a placement), so both digests move by exactly the facade rows and by nothing else --
        counted before re-pinning:

          `tidewater-georgian-careful`  4ec3f784caa5a095 -> de953067f3b99ad2, **13 new rows**:
              seven bays of the front with no opening and six rooms whose declared window count
              disagrees with the bays their front wall spans.
          `spec-builder-colonial`       433325b5299ea477 -> 5c76fc98f526d55a, **1 new row**:
              `facade-rhythm-unjudged`, because that record names no parti — one of the fifteen
              of sixteen that do not (`oq/fifteen-of-sixteen-plans-name-no-parti`).

        **The element claim this test was written for is untouched**, which is the thing to check
        before accepting a new digest: `envelopes` still returns `{}` below two elements, so no
        element-aware reading moved. A digest that moved by MORE than the rows a change accounts
        for is the failure this pin exists to catch, and the count is how you tell.

        **RE-PINNED AT WP-11.9, AND THIS PIN IS WHY THAT PACKAGE'S BUILD WAS RED.** WP-11.9 was
        committed while `check_all.py` was still at about 10% of the suite -- a stop hook asked
        for the commit -- and the run then failed here, forty-nine minutes in, on the Tidewater
        digest. **That is the mechanism working exactly as CLAUDE.md records it**: a package that
        commits before its build finishes learns what it broke from the build, and this pin is the
        thing that told it. Nothing was wrong with the change; the pin's whole job is to make a
        digest movement be ACCOUNTED FOR rather than accepted.

          `tidewater-georgian-careful`  de953067f3b99ad2 -> 70be99010403c9f3, 192 -> 208 rows
          `spec-builder-colonial`       5c76fc98f526d55a -> b5b33adeb258e516, 225 -> 238 rows

        Counted before re-pinning, and **every row is attributed**. Two rows LEAVE both plans and
        that is the sharper half of the movement:

          -2 on each: `centre-passage-core`'s "both ends of the passage have doors" and "the
             stair rises in the passage" stopped being handed to a reader because WP-11.9 gave
             each a `test`. On the Tidewater record BOTH EVALUATE AND PASS, so they emit nothing
             at all -- which is the package's own finding: the diagnosis's B4 is a defect of the
             DRAWING and not of the record.
          +9 / +5  aspect findings (6 unwanted + 3 avoided on the Tidewater plan; 4 + 1 on the
             spec Colonial), from `daylight.aspect` and `build/compass.py`.
          +1 / +1  the aspect census, which fires wherever any room was read.
          +8 / +7  grouping rules that had been emitting NOTHING. The no-test branch read
             `elif hard`, so every `strong` and `preferred` rule in the corpus was silent -- 28 of
             86 -- and a rule nobody executes and nobody is told about reads exactly like a rule
             that passed.
          +2 on the spec Colonial only: the two new tests reporting COULD NOT EVALUATE, because
             that record has an `entrance-hall` and no passage to measure. Not a pass.

        **The hand-off was also REWORDED** (`check by hand:` -> `check by hand (strong, no machine
        test):`), which moves seven more rows on each plan. Do not count those as removals: the
        first diff of this change read "+23 -7" and looked alarming until the rewording was
        normalised, and normalising it is what makes a REAL removal visible. Two real removals
        survived that normalisation and they are the two named above.

        **The element claim is STILL untouched.** No `element` key appears in any moved row and
        `envelopes` still returns `{}` below two elements; every row above comes from the room and
        grouping layers, which read no placement at all.

        **AND THE ACCOUNTING ABOVE IS NOW ASSERTED, NOT MERELY WRITTEN (audit, 7 Sep 2026).**
        A hash pin is a change detector and not a correctness proof: it cannot tell "the 16 rows
        I accounted for" from "14 I accounted for plus 2 I did not", and every number in the
        paragraphs above used to be prose beside an opaque digest. The row TOTAL and the
        per-layer histogram are pinned beside it now, so a movement names itself. In particular
        the `info` half -- the `elif hard` widening, +8 and +7 -- was pinned by no count anywhere
        in the suite and was visible only to the hash.

        **RE-PINNED ONCE MORE IN THAT SAME AUDIT, AND THE ROW COUNT IS WHY IT WAS SAFE.**

          `tidewater-georgian-careful`  70be99010403c9f3 -> 9da22729316445d4, 208 rows UNMOVED
          `spec-builder-colonial`       b5b33adeb258e516 -> 67e42551e7ffc356, 238 rows UNMOVED

        Two changes, both to fields inside existing rows and neither adding or removing one:
        the twelve grouping `F.add` calls gained a `kind` (18 rows on the Tidewater plan, 17 on
        the spec Colonial), which makes the grouping layer's findings machine-readable in the
        same way every other layer's already are; and the aspect census gained a clause naming
        rooms whose type has no record (1 row each). PROVED rather than asserted: undoing exactly
        those two edits on the live output -- clearing every `grouping-*` kind and stripping the
        census clause -- reproduces 70be99010403c9f3 and b5b33adeb258e516 BYTE FOR BYTE on both
        plans, so nothing else moved. That reconstruction is the only reason a digest change was
        accepted here at all.

        The `kind` was added in the same pass that put `kind` into the finding ID, and THAT half
        was reverted (`oq/a-findings-ordinal-is-not-an-identity`) after the full build found it
        breaking OQ 32's stated contract. This digest is over `(kind, room, statement)` and never
        over the id, so the revert does not move it -- checked, not assumed."""
        import hashlib
        import collections as _c
        for name, want, rows, hist in (
                # RE-DERIVED AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026). Both branches
                # changed the placement, so the findings this corpus produces are neither
                # parent's: 208 -> 210 rows and 238 -> 243, with the per-layer histogram
                # UNMOVED (13/18 and 11/17), which is what says the movement is placement and
                # not a layer going quiet. Old digests: 9da22729316445d4 / 67e42551e7ffc356.
                # RE-DERIVED AT WP-11.16 AND EVERY ROW ATTRIBUTED. That package did TWO things
                # to this record and only one of them is undone by `_shipped_untagged()`: it
                # tagged six rooms into a west dependency (undone here) AND it dropped the
                # direct `butlers`-`kitchen` door (not undone -- the door is gone from the
                # record, tags or no tags). So the stripped plan is 63 x 38.17 with its 7
                # relaxations back and its findings still moved, 210 -> 212.
                #
                # THE FOUR MOVED ROWS WERE DIFFED RATHER THAN COUNTED, because a net of +2 can
                # hide any number of substitutions:
                #   +/- `drawn cut-off kitchen` and `adjacency kitchen` -- the SAME two findings
                #     reworded, the butler's pantry dropping out of the kitchen's entered-from
                #     list. Net zero, and they are why the raw diff reads 4 lines for 2 rows.
                #   +  `servicing butlers` and `servicing kitchen`, both "is a wet room with no
                #     other wet room adjacent or below it". THESE ARE THE REAL +2, they are TRUE,
                #     and they are the reason the door was worth dropping: with it, the servicing
                #     layer called those two a wet pair, and on the TAGGED record that is a shared
                #     plumbing chase between two detached buildings 27 ft apart.
                #     `oq/the-servicing-layer-does-not-know-about-massing-elements`.
                # RE-DERIVED AT WP-11.17, AND BOTH PLANS MOVED FOR ONE REASON: that package
                # states the entrance front, and BOTH of these records name an entrance face
                # and carry a room that declares it, so both are re-placed. 212 -> 205 and
                # 243 -> 240. Every moved row is in the `drawn` layer -- diffed row by row, 22
                # in and 29 out on the Tidewater fixture, 3 in and 3 out on the spec Colonial --
                # and the per-layer histogram below is UNMOVED at 13/18 and 11/17, which is what
                # says a layer did not go quiet. Old digests: ff2d664a8216897f /
                # 024fa784786c2469.
                #
                # THE TIDEWATER ROW HERE IS THE UNTAGGED FIXTURE AND NOT THE SHIPPED RECORD.
                # `_shipped_untagged()` gives the anchor a 63 ft front to lay a 12 ft porch on,
                # which is a different house from the tagged 45 ft one the corpus ships; its
                # `drawn-entrance-severed` row is a property of that fixture and the shipped
                # record does not carry one (`tests/test_threshold_pass.py` asserts the flight
                # goes to the porch there).
                # AND AGAIN AT WP-11.18, WHOSE CAUSE IS `partition` RATHER THAN THE ANCHOR: a
                # STATED share stops at the closer side now instead of at the first overshoot,
                # and every plan whose record names an entrance face states one. 205 -> 209 and
                # 240 -> 235. Diffed row by row: 54 out / 58 in here and 35 out / 30 in on the
                # spec Colonial, every row in the `drawn` layer, and the two layers this class
                # watches are UNMOVED at 13/18 and 11/17 -- which is what says a layer did not go
                # quiet while the placement churned. The churn is dominated by
                # `drawn-vs-declared` (18 out / 19 in, 15 out / 13 in) and `drawn-furniture-fit`
                # (8/9, 10/10): the same rooms, re-measured, because the slicer's groups changed
                # size. Old digests: 9ecdca7453819879 / 81ddd6e8555cb1a5.
                # AND AGAIN AT THE 17 SEP MERGE OF PHASE 13 INTO THIS LINE, where the two
                # plans moved for DIFFERENT reasons and the diff is what says so. Tidewater
                # 209 -> 203: 47 rows out and 41 in, every one of them a `drawn`-layer kind
                # re-measuring on a placement that moved (`drawn-vs-declared` 15/19,
                # `drawn-furniture-fit` 4/4, `drawn-proportion-above-band` 4/4,
                # `span-over-capacity` 5/3, `unreachable` 4/2), plus `fault-present` 0/3.
                # The spec Colonial 235 -> 239 moved `fault-present` AND NOTHING ELSE, 1 out
                # and 5 in -- its placement is untouched across the merge, so the whole
                # movement there is Phase 13 supplying measurements the fault corpus could
                # not previously evaluate. The two layers this class watches are UNMOVED on
                # both plans at 13/18 and 11/17, which is the property being guarded and is
                # why this is a re-derivation rather than a bump. The three extra
                # `unreachable` rows on the SHIPPED (tagged) record are a different question
                # and are `oq/a-withdrawn-claim-still-steers-the-placer`.
                # Old digests: 6047f0ef36467dcc / 9b65c3a2dfa81377.
                # AND AGAIN AT WP-13.9, WHICH IS THE CHEAPEST MOVEMENT THIS PIN HAS EVER HAD
                # TO ATTRIBUTE and is a pure re-wording: the `unreachable` finding used to say
                # "the placement realised none of them" about EVERY stranded room, and it was
                # false wherever the room's declared doors had in fact been placed (the room is
                # cut off because its whole cluster is). Diffed row by row against a
                # `git archive` control that reproduces BOTH old digests to the character:
                # Tidewater **1 row out and 1 in**, the same room (`chamber3`), the same kind,
                # the sentence alone -- that room declares 2 doors and the placement realised
                # 1. The spec Colonial **5 out and 5 in**, the same five rooms (`dining`,
                # `foyer`, `kitchen`, `powder`, `stair`), every one of them a room that had
                # been told none of its doors were placed when some or all were. Row counts
                # UNMOVED at 203 and 239 and both watched layers unmoved at 13/18 and 11/17,
                # which is the property this class guards and is why this is a re-derivation
                # rather than a bump. Old digests: 24b6a6a640f637b8 / afa4d7a9c173615d.
                # AND ONCE MORE AT WP-13.9's ADVERSARIAL AUDIT, ON ONE PLAN AND ONE ROW, AND
                # THE ROW IS THE AUDIT'S OWN HEADLINE. The re-wording above replaced the false
                # sentence with `realised = max(0, declared - len(unplaced_pairs_for_this_room))`
                # -- which subtracts a deduplicated PAIR count from a RECORD count. A pair is
                # minted by whichever room declared the door, so a neighbour's unplaced door
                # was charged to this room: `spec-builder-colonial`'s Family Room declares two,
                # the kitchen one WAS placed, the stair's own unplaced `family` door put
                # ('family', 'stair') in the set, and the room was handed the very sentence
                # this change exists to remove. It counts the room's OWN unplaced flags now.
                # Diffed row by row against a `git archive` control of `c49f6ee` that
                # reproduces both digests to the character: Tidewater UNMOVED, spec Colonial
                # **1 row out and 1 in**, the same room, the same kind, the sentence alone.
                # Counts unmoved at 203 and 239 and both watched layers at 13/18 and 11/17.
                # Old digests: cf857d78072bf00c (unmoved) / 37018ccbc24734ff.
                ("tidewater-georgian-careful", "cf857d78072bf00c", 203,
                 {"daylight": 13, "grouping": 18}),
                ("spec-builder-colonial", "554b84e823b1c057", 239,
                 {"daylight": 11, "grouping": 17})):
            GEO._SOLVE_CACHE.clear()
            q = _shipped_untagged() if name == "tidewater-georgian-careful" \
                else json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
            GEO.solve(q, engine="heuristic")
            c = PC.check(q)
            got = hashlib.sha256(json.dumps(
                sorted((f.get("kind", ""), f.get("room", ""), f.get("statement", ""))
                       for f in c["findings"]), sort_keys=True).encode()).hexdigest()[:16]
            counts = _c.Counter(f["layer"] for f in c["findings"])
            assert len(c["findings"]) == rows, (
                f"{name}: {len(c['findings'])} findings against a pinned {rows}. The digest "
                f"below would have said only that SOMETHING moved; this says how many.")
            assert {k: counts[k] for k in hist} == hist, (
                f"{name}: the two layers this package moved now read "
                f"{ {k: counts[k] for k in hist} } against {hist}")
            assert got == want, (
                f"{name}: the drawn layer's findings moved on a ONE-RECTANGLE plan. "
                f"`envelopes` returns {{}} below two elements, so nothing about massing "
                f"elements may change this -- but note that the Tidewater record reaches this "
                f"test through `_shipped_untagged()`, which undoes its TAGS and not the other "
                f"edits WP-11.16 made to it. Diff the findings row by row and attribute every "
                f"one before re-pinning; a net count can hide any number of substitutions, and "
                f"it did here (4 rows moved for a net of 2).")


PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))


def _cross_element_claim():
    """A fixture that DRIVES the layer-3 defect: an upper bath declaring it stacks over a room
    that has been tagged into the dependency. Nothing in the corpus does this, and a fixture
    that waited for the corpus to do it would be measuring the corpus."""
    p = _fixture()
    next(r for r in p["levels"][1]["rooms"] if r["id"] == "primarybath")["stacks_over"] = "kitchen"
    return p


class TestVerticalScoreAcrossElements:
    """Layer 3, and the entry's own description of it was HALF WRONG."""

    def test_THE_SUPPORT_CREDIT_THE_ENTRY_NAMED_CANNOT_FIRE(self, placed):
        """The entry says an upper wall within 0.75 ft of a dependency wall line scores as
        continuing to a wall below. It cannot: `blocks_for` lays only level 0 into elements, so
        every upper room is inside the main block and every dependency line outside it. Measured
        rather than reasoned -- and pinned, so that if the placer ever lays an upper level into
        an element this goes red and the claim becomes real."""
        W = placed["footprint"]["width_ft"]
        g = {r["id"]: r["geometry"] for r in placed["levels"][0]["rooms"] if r.get("geometry")}
        u = {r["id"]: r["geometry"] for r in placed["levels"][1]["rooms"] if r.get("geometry")}
        gx = {round(v, 2) for gm in g.values()
              for v in (gm["x_ft"], gm["x_ft"] + gm["width_ft"])}
        dep_only = [x for x in gx if x < -0.01 or x > W + 0.01]
        assert dep_only, "the fixture has no dependency-only wall line at all"
        ux = {round(v, 2) for gm in u.values()
              for v in (gm["x_ft"], gm["x_ft"] + gm["width_ft"])}
        assert not [x for x in ux if any(abs(x - d) <= 0.75 for d in dep_only)], (
            "an upper edge is within tolerance of a dependency line -- the entry's support "
            "credit is reachable after all and must be fixed rather than recorded as unreachable")

    def test_a_cross_element_claim_is_UNJUDGED_and_not_charged(self):
        """What WAS reachable, and it is the opposite sign: a claim naming a room in another
        element was charged 40 points and told "is drawn clear of it", for a failure no
        placement could avoid."""
        p = _cross_element_claim()
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        notes = p["geometry_report"]["vertical"]
        hit = [n for n in notes if "Kitchen (Dependency)" in n]
        assert hit, notes
        assert "COULD NOT EVALUATE" in hit[0]
        assert "drawn clear of it" not in hit[0], (
            "an unjudged claim must not be phrased as a placement that went wrong")

    def test_and_the_charge_it_used_to_pay_is_gone(self):
        """40 points, measured: vertical_score 114 -> 74 on this fixture.

        RE-CUT AT WP-13.2. This compared the TOTAL vertical score of two different solves --
        the claim pointed at the dependency's kitchen against the claim pointed at the main
        block's butler's pantry -- and read the difference as the one claim's charge. Two
        solves are two placements, and the moment `stacking.lands` (containment) changed how
        much the OTHER claims on this fixture cost, the two winners diverged and the totals
        stopped saying anything about the claim under test (194.0 against 196.0). The property
        is asserted on ONE placement now: `vertical_score` re-run on the placed rectangles with
        the claim pointed at the dependency costs exactly what it costs with the claim absent
        (an unjudged claim is not charged), and pointed at a main-block room it costs `STACK_W`
        more exactly when that room is not landed on."""
        import copy as _copy
        p = _cross_element_claim()
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        ground = [r for lv in p["levels"] if lv.get("index", 0) == 0 for r in lv["rooms"]]
        upper = [r for lv in p["levels"] if lv.get("index", 0) == 1 for r in lv["rooms"]]
        g = {r["id"]: (r["geometry"]["x_ft"], r["geometry"]["y_ft"], r["geometry"]["width_ft"],
                       r["geometry"]["depth_ft"]) for r in ground if r.get("geometry")}
        u = {r["id"]: (r["geometry"]["x_ft"], r["geometry"]["y_ft"], r["geometry"]["width_ft"],
                       r["geometry"]["depth_ft"]) for r in upper if r.get("geometry")}
        bath = next(r for r in upper if r["id"] == "primarybath")
        assert bath["stacks_over"] == "kitchen" and "primarybath" in u and "butlers" in g
        s_unjudged, notes = GEO.vertical_score(g, u, ground, upper, p)
        assert any("COULD NOT EVALUATE" in n for n in notes), notes
        absent = _copy.deepcopy(upper)
        del next(r for r in absent if r["id"] == "primarybath")["stacks_over"]
        s_absent, _ = GEO.vertical_score(g, u, ground, absent, p)
        assert s_unjudged == s_absent, (
            f"the cross-element claim is still charged: {s_unjudged} with it against "
            f"{s_absent} without it")
        main = _copy.deepcopy(upper)
        next(r for r in main if r["id"] == "primarybath")["stacks_over"] = "butlers"
        s_main, _ = GEO.vertical_score(g, u, ground, main, p)
        _STK = modcache.load("stacking", os.path.join(ROOT, "build", "stacking.py"))
        want = 0.0 if _STK.lands(u["primarybath"], g["butlers"]) else GEO.STACK_W
        assert s_main - s_absent == want, (s_main, s_absent, want)

    def test_breaks_and_unjudged_are_TWO_LISTS_and_a_charge_reads_the_first(self):
        """`declared_stack_breaks` returns both states and `stack_breaks_only` is what a charge
        or a rejection may act on. A caller treating the full list as breaks would charge for an
        unjudged claim -- which is the defect this layer removed, arriving through the other
        door."""
        p = _cross_element_claim()
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        g = {r["id"]: (r["geometry"]["x_ft"], r["geometry"]["y_ft"],
                       r["geometry"]["width_ft"], r["geometry"]["depth_ft"])
             for r in p["levels"][0]["rooms"] if r.get("geometry")}
        u = {r["id"]: (r["geometry"]["x_ft"], r["geometry"]["y_ft"],
                       r["geometry"]["width_ft"], r["geometry"]["depth_ft"])
             for r in p["levels"][1]["rooms"] if r.get("geometry")}
        els = GEO.element_of(p, p["levels"][0]["rooms"])
        assert els and any(v != "main" for v in els.values())
        allc = GEO.declared_stack_breaks(g, u, p["levels"][1]["rooms"], els)
        only = GEO.stack_breaks_only(g, u, p["levels"][1]["rooms"], els)
        assert any(b.get("unjudged") for b in allc)
        assert all(not b.get("unjudged") for b in only)
        assert len(only) < len(allc)

    def test_element_of_is_EMPTY_on_every_plan_in_this_corpus(self):
        """The byte-identity guard, and the ordering trap it was written against: a first
        version read `footprint.blocks`, which `blocks_record` writes AFTER the search loop this
        map is used in, so it was empty exactly where the charge is decided."""
        p = _shipped_untagged()
        assert GEO.element_of(p, p["levels"][0]["rooms"]) == {}
        # AND THE SHIPPED RECORD IS NOT EMPTY ANY MORE, which is the half WP-13.5 added: the
        # name of this test was true of every plan until that package and is true of none of
        # the sixteen read raw. Both directions are asserted so neither can go quiet.
        raw = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        assert GEO.element_of(raw, raw["levels"][0]["rooms"]), \
            "the shipped record states a container since WP-13.5; the strip above is the fixture"
        # and non-empty on the fixture BEFORE any placement has written a blocks list
        f = _fixture()
        assert "blocks" not in (f.get("footprint") or {})
        assert GEO.element_of(f, f["levels"][0]["rooms"])


def _lot(lot, dep=True):
    """The fixture at a stated lot width. `dep=False` is the SAME plan with no tag at all --
    one rectangle, which is what every plan in this corpus is, and which is where layer 4's
    second finding lives."""
    p = _fixture() if dep else _shipped_untagged()
    p.setdefault("site", {}).update({"lot_width_ft": lot, "setback_side_ft": 0})
    return p


class TestTheLotCapIsOnTheBuiltExtent:
    """Layer 4. Ruling 2: "the hyphen is roofed ground; a building whose covered area overruns its
    lot has overrun it". The cap was on the MAIN BLOCK, so the flanking elements were free."""

    def test_the_flank_counts_the_hyphen_and_not_the_dependency_alone(self):
        """The ruling is about WHAT is measured, so the test is about what is measured. 41 ft is
        a 27 ft dependency plus the 14 ft hyphen gap, and a version that counted the dependency
        alone would read 27."""
        p = _fixture()
        _, prep = GEO.prep_rooms(p)
        bay = GEO.derive_footprint(p, None, prep)["bay"]
        els = GEO.flank_sizes(prep, bay)
        assert len(els) == 1 and els[0]["W"] == 27.0
        assert els[0]["gap"] == GEO.HYPHEN_DEFAULT_FT == 14.0
        assert GEO.flanking_extent_ft(prep, bay) == 41.0, (
            "the flank must be gap + width; 27.0 means the hyphen was left out, which is the "
            "one thing the ruling says explicitly")

    def test_flank_sizes_IS_THE_SPELLING_BLOCKS_FOR_READS(self, placed):
        """One function, two readers. A second transcription would let the cap and the placement
        disagree about how wide the house is -- the defect the cap exists to catch, one layer up."""
        _, prep = GEO.prep_rooms(placed)
        bay = placed["footprint"]["bay_module_ft"]
        sized = {e["id"]: e["W"] for e in GEO.flank_sizes(prep, bay)}
        drawn = {b["id"]: b["width_ft"] for b in placed["footprint"]["blocks"]
                 if b.get("role") == "dependency"}
        assert sized and sized == drawn, (sized, drawn)

    def test_the_cap_now_BITES_on_the_built_extent(self):
        """The headline. 104 ft of building on an 80 ft lot, and the main block was never
        touched because 63 ft of it fits inside 80."""
        GEO._SOLVE_CACHE.clear()
        p = _lot(80)
        GEO.solve(p, engine="heuristic")
        assert p["footprint"]["width_ft"] == 45, "the main block was not capped"
        L = p["geometry_report"]["lot"]
        assert L["built_extent_ft"] == 86.0 and L["flanking_ft"] == 41.0
        assert p["geometry_report"]["lot_capped"] is True

    def test_the_record_answers_in_THREE_states_and_never_two(self):
        """A plan with no lot is not told it fits. `lot_capped` alone was a boolean about the
        main block's bay count and it read `false` over a 104 ft extent on an 80 ft lot."""
        GEO._SOLVE_CACHE.clear()
        none = _shipped_untagged()
        none.pop("site", None)
        (none.get("context") or {}).pop("lot_width_ft", None)
        GEO.solve(none, engine="heuristic")
        L0 = none["geometry_report"]["lot"]
        assert L0["usable_width_ft"] is None and L0["over_ft"] is None
        assert "COULD NOT EVALUATE" in L0["note"]
        assert L0["built_extent_ft"], "the extent is a FACT and is reported with or without a lot"

        GEO._SOLVE_CACHE.clear()
        fits = _lot(140)
        GEO.solve(fits, engine="heuristic")
        assert fits["geometry_report"]["lot"]["over_ft"] == 0.0

        GEO._SOLVE_CACHE.clear()
        over = _lot(80)
        GEO.solve(over, engine="heuristic")
        assert over["geometry_report"]["lot"]["over_ft"] == 6.0

    def test_THE_PARITY_BUMP_MAY_NOT_CROSS_THE_LOT_and_this_is_ONE_RECTANGLE(self):
        """LAYER 4'S SECOND FINDING, AND IT IS NOT ABOUT MASSING ELEMENTS AT ALL. On a lot
        holding six bays the centre-bay bump built seven -- 63 ft on 60 ft, on a plan with no
        dependency, every plan in this corpus's own shape. Delete the clamp and this reads 7."""
        GEO._SOLVE_CACHE.clear()
        p = _lot(60, dep=False)
        fp = GEO.derive_footprint(p)
        assert fp["lot_maxbay"] == 6
        assert fp["bays"] == 6 and fp["W"] == 54, (fp["bays"], fp["W"])
        assert fp["W"] <= 60

    def test_and_bay_count_forced_even_FIRES_FOR_THE_FIRST_TIME(self):
        """The field's own comment says "today the only way here is a lot too narrow to hold the
        odd count", and that path was unreachable: the bump made the count odd whatever the lot
        said, so the refusal could not fire in the one case it names."""
        GEO._SOLVE_CACHE.clear()
        fp = GEO.derive_footprint(_lot(60, dep=False))
        assert fp["wants_centre_bay"] is True
        assert fp["bay_count_forced_even"] is True

    def test_the_residue_is_the_massings_own_floor_and_the_note_NAMES_it(self):
        """What the cap deliberately does NOT do. `start = max(mb["min"], from_area)` ignores the
        cap, so a five-bay diagram on a lot holding four builds five. Disclosed rather than
        ruled: nobody has said a lot outranks a diagram's floor."""
        GEO._SOLVE_CACHE.clear()
        p = _lot(36, dep=False)
        GEO.solve(p, engine="heuristic")
        L = p["geometry_report"]["lot"]
        assert L["over_ft"] == 9 and p["footprint"]["width_ft"] == 45
        assert "minimum of 5 bays" in L["note"] and "lot holds 4" in L["note"]
        assert "oq/a-lot-too-narrow-for-the-diagrams-own-minimum-bay-count" in L["note"], (
            "a residue with no question named is a number nobody will come back to")

    def test_A_LOT_THE_FLANK_HAS_EATEN_REFUSES_AND_SAYS_WHY(self):
        """`{"error": "lot too narrow: 50 ft cannot hold two bays"}` would be absurd about 50 ft
        and an 18 ft pair of bays. The refusal names the flank that actually ate the lot."""
        p = _lot(50)
        fp = GEO.derive_footprint(p)
        assert "error" in fp, fp.get("W")
        assert "flanking element" in fp["error"] and "41 ft" in fp["error"], fp["error"]

    def test_a_one_rectangle_plan_is_UNTOUCHED_by_all_of_it(self):
        """The regression discipline. Both shipped plans place identically -- and one of them,
        `spec-builder-colonial`, is lot-capped as shipped, so the cap itself is exercised."""
        # RE-DERIVED AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026), NOT BUMPED. This pinned
        # main's guarantee that teaching the layers about elements moved NO shipped
        # placement -- and it held for every package that made it. What arrived is the
        # OTHER Phase 11, which changed the placement itself (a band-first candidate key,
        # a span charge) exactly as this one did (its parti bay module, its stacking rule,
        # its candidate row). Two placement changes meeting cannot leave the placement
        # where either found it, and the other branch's `CORPUS_PLACEMENT_SHA` moved for
        # the same reason in the same commit. Old values: 685.3 / 592.3.
        # AND RE-DERIVED AGAIN AT WP-11.16, WITH THE TWO CAUSES SEPARATED. That package tagged
        # this record AND dropped a door, and `_shipped_untagged()` above undoes only the first:
        # the width comes back to 63 and the relaxation count to 7, so the TAGS really are gone,
        # and the score does not, because the `butlers`-`kitchen` door is gone from the record
        # whether or not its rooms carry a `block`. 775.2 -> 761.2 is the door, measured by
        # stripping. `spec-builder-colonial` was untouched by that package and unmoved here,
        # which was the control that said so -- AND IT IS NOT THAT CONTROL ANY MORE. WP-11.17
        # states the entrance front, that record names one, and its figures move with the
        # Tidewater's. The ten plans the entrance selector does NOT reach carry the control
        # now, in `tests/test_elements.py`'s corpus digests.
        for name, score, width, capped in (
                # RE-DERIVED AT WP-11.17 for the reason the note beside the other copy of these
                # figures gives: both records name an entrance face, so the anchor re-places
                # both and neither is the untouched control it was.
                # AND AGAIN AT WP-11.18 for the reason the other copy of these figures carries:
                # `partition`'s stated share stops at the closer side, which reaches exactly the
                # plans that name an entrance face. The WIDTH and the CAP -- what this test is
                # actually about -- are unmoved on both.
                # AND AGAIN AT THE 17 SEP MERGE, ON ONE PLAN OF THE TWO: Tidewater
                # 1017.2 -> 889.0 and the spec Colonial UNMOVED at 779.5, because only
                # the Tidewater placement moves across this merge. The WIDTH and the
                # CAP -- what this test is about -- are unmoved on BOTH, which is what
                # makes this a re-derivation of a number that rides along rather than a
                # re-pin of the property.
                ("tidewater-georgian-careful", 889.0, 63, False),
                ("spec-builder-colonial", 779.5, 50.0, True)):
            GEO._SOLVE_CACHE.clear()
            q = _shipped_untagged() if name == "tidewater-georgian-careful" \
                else json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
            GEO.solve(q, engine="heuristic")
            g = q["geometry_report"]
            # AND AT WP-11.17: 761.2 -> 864.1 on this untagged fixture, WHICH IS THE SCORE
            # RISING WHILE THE FINDINGS FALL. Stating the entrance front is a HARD statement --
            # the entry porch is placed against the S face before the guillotine runs -- so the
            # search chooses from a smaller pool and cannot reach the candidate it used to. On
            # the same fixture `plan_check` reads serious 67 -> 60 and minor 109 -> 108 across
            # that rise. This corpus already records the inverse shape (a minor count rising
            # while a house got materially better); READ THE FINDINGS BEFORE QUOTING THE KEY ON
            # A PLACEMENT CHANGE, in either direction. `spec-builder-colonial` moves too --
            # 830.1 -> 814.4 -- because its record also names an entrance face, so it is no
            # longer the untouched control it was for WP-11.16 and its figure is re-derived
            # rather than carried.
            assert round(g["score"], 1) == score, (name, g["score"])
            assert q["footprint"]["width_ft"] == width, (name, q["footprint"]["width_ft"])
            assert g["lot_capped"] is capped, name
            assert g["lot"]["flanking_ft"] == 0.0 and g["lot"]["over_ft"] == 0.0, name

    def test_THE_FLANK_IS_THE_PLACEMENTS_OWN_ARITHMETIC_on_a_three_element_house(self):
        """The strongest form of the guard, and the reason `flank_sizes` is one function: the cap
        computes the flank BEFORE the placement and the placement lays it out AFTER, so the two
        can be held against each other on the placement's own output. A dependency each side --
        three elements, 100 ft of building -- and `built_extent - main == flank` exactly.

        **THE TWO LITERALS MOVED AT ITEM 4 AND THE IDENTITY DID NOT**, which is the difference
        between a measurement and a guard. The main block was 63 ft while `derive_footprint`
        counted the wings' programme into it as well as beside it; sized from its own rooms it is
        45, so the building is 100 ft rather than 118. `flanking_ft` is unmoved at 55."""
        p = _shipped_untagged()
        for r in p["levels"][0]["rooms"]:
            if r["type"] in ("kitchen", "pantry"):
                r["block"] = "west-dependency"; r["exterior_walls"] = ["N", "S", "W"]
            elif r["type"] == "breakfast-room":
                r["block"] = "east-dependency"; r["exterior_walls"] = ["N", "S", "E"]
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        bl = p["footprint"]["blocks"]
        assert len(bl) == 3, [b["id"] for b in bl]
        lo = min(b["x_ft"] for b in bl)
        hi = max(b["x_ft"] + b["width_ft"] for b in bl)
        L = p["geometry_report"]["lot"]
        assert round(hi - lo, 2) == L["built_extent_ft"] == 100.0, (hi - lo, L)
        assert round(L["built_extent_ft"] - L["main_block_ft"], 2) == L["flanking_ft"] == 55.0, L


EI = modcache.load("export_ifc", os.path.join(ROOT, "build", "export_ifc.py"))
STRUCT = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))


def _boxes(p):
    sec = STRUCT.build_section(p, geometry_result=p)
    t = sec["wall"]["exterior_in"] / 12.0
    return sec, t, EI.slab_boxes(p, sec, t)


def _rooms_over_no_slab(p, boxes):
    off = []
    for lv in p["levels"]:
        idx = lv.get("index", 0)
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g:
                continue
            if not any(b["level"] == idx
                       and g["x_ft"] >= b["cx"] - b["width_ft"] / 2 - 0.01
                       and g["y_ft"] >= b["cy"] - b["depth_ft"] / 2 - 0.01
                       and g["x_ft"] + g["width_ft"] <= b["cx"] + b["width_ft"] / 2 + 0.01
                       and g["y_ft"] + g["depth_ft"] <= b["cy"] + b["depth_ft"] / 2 + 0.01
                       for b in boxes):
                off.append(r["id"])
    return sorted(off)


class TestTheIfcSlabIsPerElement:
    """Layer 6, the last. Ruling 1: `export_ifc` gets a slab per element.

    THE GEOMETRY IS A PURE FUNCTION AND THAT IS WHY THESE TESTS EXIST AT ALL. `ifcopenshell` is
    optional and absent here and in CI, so `export_ifc.py selftest` reports COULD NOT EVALUATE --
    a slab rule written inside the writer would have been "fixed" against a check that never runs.
    `slab_boxes` is arithmetic over the section and the blocks; only the entity emission needs the
    library."""

    def test_the_three_rooms_that_floated_are_over_a_slab(self, placed):
        """The headline, and it is the disclosure's own published baseline: the main slab spans
        x[-1.29, 64.29] and the kitchen, pantry and breakfast room sit at x[-41.0, -14.0]. Every
        `IfcSpace` is placed from its room's own ABSOLUTE rectangle, so all three floated clear of
        every slab in the model."""
        _, t, boxes = _boxes(placed)
        assert _rooms_over_no_slab(placed, boxes) == []
        dep = next(b for b in boxes if b["element"] != "main")
        el = next(b for b in placed["footprint"]["blocks"] if b["id"] != "main")
        assert dep["width_ft"] == pytest.approx(el["width_ft"] + 2 * t)
        assert dep["cx"] == pytest.approx(el["x_ft"] + el["width_ft"] / 2)

    def test_the_baseline_it_replaces_REALLY_FLOATED_THREE(self, placed):
        """The instrument, not the fix: the single main-block slab this replaced, reconstructed
        here, leaves exactly three rooms over nothing. Without this the '3 -> 0' above is one
        number with nothing to be measured against."""
        sec, t, _ = _boxes(placed)
        fp = sec["geometry"]["footprint"]
        W, D = fp["width_ft"], fp["depth_ft"]
        old = [{"level": st["index"], "element": "main",
                "width_ft": W + 2 * t, "depth_ft": D + 2 * t, "cx": W / 2, "cy": D / 2}
               for st in sec["storeys"] if st.get("storey_height_ft") is not None]
        assert _rooms_over_no_slab(placed, old) == ["breakfast", "kitchen", "pantry"]

    def test_a_dependency_gets_a_GROUND_slab_and_no_upper_one(self, placed):
        """Not an omission: `blocks_for` lays only level 0 into elements, so there is no upper
        floor over the dependency to carry. The function reads the rooms rather than crossing
        every element with every storey, which is what makes that true by construction."""
        _, _, boxes = _boxes(placed)
        by_level = {}
        for b in boxes:
            by_level.setdefault(b["level"], set()).add(b["element"])
        assert by_level[0] == {"main", "west-dependency"}, by_level
        assert by_level[1] == {"main"}, by_level

    def test_a_one_rectangle_plan_gets_THE_OLD_NUMBERS_EXACTLY(self):
        """The regression, stated as the arithmetic the single-slab loop did rather than as a
        pinned literal: one box per storey, `W + 2t` by `D + 2t`, centred on the main block."""
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            GEO._SOLVE_CACHE.clear()
            q = _shipped_untagged() if name == "tidewater-georgian-careful" \
                else json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
            GEO.solve(q, engine="heuristic")
            sec, t, boxes = _boxes(q)
            fp = sec["geometry"]["footprint"]
            W, D = fp["width_ft"], fp["depth_ft"]
            storeys = [st for st in sec["storeys"] if st.get("storey_height_ft") is not None
                       and (st.get("index") or 0) >= 0]
            assert len(boxes) == len(storeys), (name, boxes)
            for b in boxes:
                assert b["element"] == "main", (name, b)
                assert b["width_ft"] == pytest.approx(W + 2 * t)
                assert b["depth_ft"] == pytest.approx(D + 2 * t)
                assert b["cx"] == pytest.approx(W / 2) and b["cy"] == pytest.approx(D / 2)
            assert _rooms_over_no_slab(q, boxes) == [], name

    def test_a_block_tag_naming_no_element_falls_to_the_main_block(self, placed):
        """`is_block_tag`'s own conservative answer one layer up, not a new rule: a tag the placer
        did not build is read as the main block rather than raising or inventing a slab."""
        q = json.loads(json.dumps(placed))
        for lv in q["levels"]:
            for r in lv["rooms"]:
                if r.get("block"):
                    r["block"] = "an-element-nobody-placed"
        _, _, boxes = _boxes(q)
        assert {b["element"] for b in boxes} == {"main"}, boxes


def _hyphen_fixture(with_hyphen=True):
    """The package's own fixture plus a HYPHEN ROOM, which is the thing a cross-element door
    needs to exist at all.

    A DRIVEN FIXTURE, because the corpus does not exercise this (WP-8.11's rule). The
    re-authoring of `centre-passage-double-pile` that would have exercised it was measured and
    withdrawn -- three of the corpus's own hard room rules refuse it, in three different
    arrangements -- so the placer's half ships with a fixture that drives it rather than with a
    parti that happens to.

    AND IT DROPS `entrance_faces`, WHICH IS THAT SAME RULE MET A SECOND TIME (WP-11.17). This is
    built from the shipped Tidewater record, so it inherited `"S"` and an entry porch -- and
    WP-11.17 states the entrance front as an anchor of the same kind, laid FIRST, so the
    entrance anchor pre-empted the hyphen one and all four tests below stopped exercising the
    branch they name (`butlers` at x 28.5 instead of 0.00, its door through the hyphen
    unplaced). That ordering is the WP-11.17 ruling and is correct on a real record: the
    entrance is the fatal tier. It is wrong HERE, because this fixture's whole subject is the
    hyphen anchor, and a fixture that inherits whatever the shipped record happens to declare
    tests whatever that record happens to want. Dropping the field is what makes these four
    tests about `hyphen_anchors` again; the entrance anchor's own cost is measured on the
    shipped record, in `tests/test_threshold_pass.py` and the WP-11.17 report."""
    p = _fixture()
    p.get("context", {}).pop("entrance_faces", None)
    g = p["levels"][0]["rooms"]
    by = {r["id"]: r for r in g}
    for a, b in (("butlers", "kitchen"), ("kitchen", "butlers")):
        if not any(d.get("to") == b for d in (by[a].get("doors") or [])):
            by[a].setdefault("doors", []).append({"to": b, "width_ft": 2.8})
    if with_hyphen:
        g.append({"id": "hyphen", "type": "gallery-corridor", "name": "Hyphen",
                  "block": "west-dependency", "hyphen": True,
                  "width_ft": 8.0, "length_ft": 20.0, "ceiling_ft": 11.0,
                  "exterior_walls": ["N", "S"],
                  "doors": [{"to": "butlers", "width_ft": 3.0},
                            {"to": "kitchen", "width_ft": 3.0}]})
        for r in g:
            if r["id"] in ("butlers", "kitchen"):
                r.setdefault("doors", []).append({"to": "hyphen", "width_ft": 3.0})
    return p


def _cross_doors(p):
    """Doors between two massing ELEMENTS, and a room that takes no rectangle is in none.

    CORRECTED AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026), by the other branch's own
    correction of the identical mistake. Its WP-11.11 published "2 of 16 crossing pairs" and its
    WP-11.13 found the number is 1: the second pair was `breakfast <-> terrace`, and a TERRACE
    TAKES NO RECTANGLE -- it is an at-grade appendage placed outside the block, its room keeps no
    `geometry` by construction -- so it stands in no element and cannot cross a boundary between
    two. That branch recorded the instrument reading "no element" as "the main block" as the very
    defect its element work exists to remove.

    This instrument had the same flaw, and it surfaced here as `('breakfast', 'terrace'): False`
    -- a door correctly PLACED by the appendage pass being counted as a cross-element door that
    should have been refused. `stacking.takes_a_rectangle` is the filter both branches use.
    """
    _STK = modcache.load("stacking", os.path.join(ROOT, "build", "stacking.py"))
    _PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
    _CAT = (_PC.load_corpus() or {}).get("rooms") or {}
    takes = {r["id"]: _STK.takes_a_rectangle(r.get("type"), _CAT)
             for lv in p["levels"] for r in lv["rooms"]}
    els = {r["id"]: (r.get("block") or "main") for lv in p["levels"] for r in lv["rooms"]}
    out = {}
    for lv in p["levels"]:
        for r in lv["rooms"]:
            for d in (r.get("doors") or []):
                to = d.get("to")
                if not to or to == "exterior" or els.get(r["id"]) == els.get(to):
                    continue
                if not takes.get(r["id"], True) or not takes.get(to, True):
                    continue        # an appendage is in no element and crosses no boundary
                k = tuple(sorted((r["id"], to)))
                out[k] = out.get(k, False) or bool(d.get("unplaced"))
    return out


class TestTheFlankIsStatedRatherThanSearchedFor:
    """WP-11.6, the placer half of items 2-4. A door between two elements cannot be placed unless
    the two rooms share a wall, and nothing made them -- the seventh defect
    `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` records under item 3."""

    def test_hyphen_anchors_reads_the_door_graph_THROUGH_THE_LINK(self):
        p = _hyphen_fixture()
        _, prep = GEO.prep_rooms(p)
        fp = GEO.derive_footprint(p, None, prep)
        a = GEO.hyphen_anchors(p, GEO.blocks_for(p, fp, prep, 0), 0)
        assert set(a) == {"main", "west-dependency", "west-dependency-hyphen"}, a
        # Each element's own room that doors THROUGH THE LINK, on the face the link is beyond --
        # and SINCE WP-11.18 the band it must meet on that face, which is the neighbour's own
        # extent (`anchor_span`). A face alone says the pantry belongs on the west wall; it does
        # not say the pantry belongs OPPOSITE THE HYPHEN, and the door needs the second.
        # The band is read off the HYPHEN BLOCK's own rectangle rather than transcribed, so this
        # says what it means -- "the neighbour's own extent" -- instead of pinning two literals
        # that go stale the next time `blocks_for` moves a wing by a tenth of a foot.
        blocks = {b["id"]: b for b in GEO.blocks_for(p, fp, prep, 0)}
        hy = blocks["west-dependency-hyphen"]

        def band(el):
            o = blocks[el]["y"]
            return pytest.approx((hy["y"] - o, hy["y"] + hy["H"] - o), abs=0.01)

        assert list(a["main"]) == ["W"] and a["main"]["W"][0] == ["butlers"], a["main"]
        assert a["main"]["W"][1] == band("main"), a["main"]
        assert list(a["west-dependency"]) == ["E"], a["west-dependency"]
        assert a["west-dependency"]["E"][0] == ["kitchen"], a["west-dependency"]
        assert a["west-dependency"]["E"][1] == band("west-dependency"), a["west-dependency"]
        assert set(a["west-dependency-hyphen"]) == {"E", "W"}, a["west-dependency-hyphen"]
        # AND `butlers -> kitchen` PUT NOTHING HERE. That pair crosses open ground with no link
        # between them, and no laying of rooms can place it, so it is not an anchor: `butlers` is
        # on the list because it doors to the HYPHEN, and `backhall` and `cellarstair`, which
        # door only to the kitchen, are on no list at all.
        ids = a["main"]["W"][0]
        assert "backhall" not in ids and "cellarstair" not in ids, a["main"]

    def test_the_band_is_the_neighbours_own_extent_and_two_neighbours_give_NONE(self):
        """`anchor_span`, WP-11.18. The band is what `_partial_flank` positions the strip inside.

        THE TWO-NEIGHBOUR CASE IS REFUSED RATHER THAN RESOLVED, which is `entrance_anchors`' own
        discipline one field over: two elements past one face have two extents, and a union, an
        intersection or a midpoint would each be this reader inventing the answer the record does
        not give. A `None` band is the three-way draw the anchor has always taken -- unjudged,
        and not a pass."""
        A = (0.0, 0.0, 45.0, 37.24)
        assert GEO.anchor_span(A, (-7.0, 9.62, 0.0, 27.62), "W") == (9.62, 27.62)
        assert GEO.anchor_span(A, (45.0, 4.0, 60.0, 10.0), "E") == (4.0, 10.0)
        assert GEO.anchor_span(A, (12.0, 37.24, 30.0, 50.0), "N") == (12.0, 30.0)
        # clipped to the element's own face, never beyond it
        assert GEO.anchor_span(A, (-99.0, -5.0, 0.0, 99.0), "W") == (0.0, 37.24)
        # no overlap on that axis at all -- the diagonal `face_toward` already refuses
        assert GEO.anchor_span(A, (-7.0, 50.0, 0.0, 60.0), "W") is None

        plan = {"levels": [{"index": 0, "rooms": [
            {"id": "a", "block": "A", "doors": [{"to": "b"}, {"to": "c"}]},
            {"id": "b", "block": "B", "doors": [{"to": "a"}]},
            {"id": "c", "block": "C", "doors": [{"to": "a"}]}]}]}
        one = [{"id": "A", "role": "main", "x": 0, "y": 0, "W": 10, "H": 20, "rooms": ["a"]},
               {"id": "B", "role": "hyphen", "x": 10, "y": 2, "W": 6, "H": 6, "rooms": ["b"]}]
        assert GEO.hyphen_anchors(plan, one, 0)["A"] == {"E": (["a"], (2.0, 8.0))}
        two = one + [{"id": "C", "role": "hyphen", "x": 10, "y": 12, "W": 6, "H": 6,
                      "rooms": ["c"]}]
        assert GEO.hyphen_anchors(plan, two, 0)["A"] == {"E": (["a"], None)}, (
            "two neighbours beyond one face have two extents and the anchor may not pick one")

    def test_band_off_derives_the_position_and_falls_back_to_an_END_when_slabs_run_out(self):
        """`_band_off`, WP-11.18. No draw is taken when a band is stated.

        THE END POSITIONS ARE CANDIDATES AND NOT A REFUSAL, and that is the whole reason this is
        a function rather than one expression. A centred position needs a slab either side and
        each slab needs a room of its own, so on a rectangle with two rooms to spare the centre
        is not available -- and returning None there would hand the anchor back to a guillotine
        that does not know the band exists. The largest overlap wins; ties go to the position
        that needs fewer slabs."""
        along, L, floor_ = 37.24, 12.0, 4.95
        # Three rooms to spare: the band-centred position is affordable and is taken.
        off = GEO._band_off(along, L, floor_, (9.62, 27.62), 3)
        assert off == pytest.approx(12.62, abs=0.01), off
        assert min(27.62, off + L) - max(9.62, off) == pytest.approx(12.0, abs=0.01)
        # Two rooms: the centre needs three slabs, so an END is taken rather than nothing.
        off2 = GEO._band_off(along, L, floor_, (9.62, 27.62), 2)
        assert off2 in (0.0, pytest.approx(along - L, abs=0.01)), off2
        assert GEO._band_off(along, L, floor_, (9.62, 27.62), 1) is None, (
            "one room can fill one slab, and no one-slab position overlaps this band")
        # A band at one end: the clamp puts the anchor there and no draw is involved.
        assert GEO._band_off(along, L, floor_, (0.0, 6.0), 3) == 0.0
        # A band the rectangle cannot reach at all is a refusal, not a nearest guess.
        assert GEO._band_off(20.0, 6.0, 2.0, (40.0, 50.0), 3) is None

    def test_the_hosted_anchor_goes_in_the_rest_rectangle_that_stands_on_ITS_face(self):
        """`_host_for`, WP-11.18. A rectangle hosts the next anchor only where its own face IS
        the element's -- a rectangle one cut inside the envelope is a different wall.

        `B` IS OFFERED FIRST AND THAT IS THE CASE A FIRST VERSION MISSED: when `off` is 0 there
        is no `P` slab at all and `B` is what stands on the low face. WP-11.17's third reverted
        recovery considered only `P` and `R`, and its winning candidate had `off = 0` -- so the
        forcing never applied to the placement its number was read off."""
        el = (0.0, 0.0, 45.0, 37.24)
        rB, rP, rR = (16.5, 6.0, 12.0, 31.24), (0.0, 0.0, 16.5, 37.24), (28.5, 0.0, 16.5, 37.24)
        rects = (("B", rB), ("P", rP), ("R", rR))
        assert GEO._host_for("W", el, rects, 5) == "P"
        assert GEO._host_for("E", el, rects, 5) == "R"
        assert GEO._host_for("N", el, rects, 5) == "B", "B reaches the far face too"
        # `off = 0`: no P, and B is what stands on the west face.
        no_p = (("B", (0.0, 6.0, 12.0, 31.24)), ("P", None), ("R", (12.0, 0.0, 33.0, 37.24)))
        assert GEO._host_for("W", el, no_p, 4) == "B"
        # Too few rooms to leave one for every other slab -> no host, and the chain stops.
        assert GEO._host_for("W", el, rects, 2) is None

    def test_the_anchor_is_laid_ON_the_shared_face(self, placed=None):
        """The measurement. Before, `butlers` sat wherever the guillotine left it; the strip puts
        it at x0 = 0.00, which IS the main block's west face."""
        p = _hyphen_fixture()
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        g = {r["id"]: r["geometry"] for lv in p["levels"] for r in lv["rooms"] if r.get("geometry")}
        assert g["butlers"]["x_ft"] == pytest.approx(0.0, abs=0.05), g["butlers"]

    def test_AND_THE_DOOR_THROUGH_THE_HYPHEN_PLACES(self):
        """The point of all of it. `butlers -> hyphen` is the one door that crosses a gap with a
        link in it, and it is the one that places."""
        p = _hyphen_fixture()
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        cross = _cross_doors(p)
        assert cross[("butlers", "hyphen")] is False, cross

    def test_THE_SHIPPED_RECORD_DRAWS_ITS_PANTRY_AT_ITS_DECLARED_SIZE_ON_THE_BAND(self):
        """The subject of WP-11.18, on the one shipped record that carries two anchors.

        Three states of this room, and the middle one is why the first is not the bar:

            hyphen anchor alone (<= WP-11.16)   4.95 x 37.24 = 184 sf against a declared 84
            entrance anchor alone (WP-11.17)   16.50 x 10.24 = 169 sf, at the EAST end
            both stated (WP-11.18)              7.00 x 12.00 =  84 sf, on the west face

        The old strip met both neighbours BY BEING ENORMOUS -- spanning the whole depth, it could
        not miss -- which is the veranda defect `_partial_flank` exists to remove. This asserts
        the rectangle AND the overlap, because either alone can be right for the wrong reason: a
        room of the right size in the wrong place, or a room in the right place at twice its
        size."""
        q = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        GEO._SOLVE_CACHE.clear()
        GEO.solve(q, engine="heuristic")
        g = {r["id"]: r.get("geometry") for lv in q["levels"] for r in lv["rooms"]}
        b = g["butlers"]
        assert (b["width_ft"], b["depth_ft"]) == pytest.approx((7.0, 12.0), abs=0.01), b
        blocks = {x["id"]: x for x in q["footprint"]["blocks"]}
        main, hy = blocks["main"], blocks["service-hyphen"]
        assert b["x_ft"] == pytest.approx(main["x_ft"], abs=0.05), (
            "the pantry has left the main block's west face", b)
        share = min(b["y_ft"] + b["depth_ft"], hy["y_ft"] + hy["depth_ft"]) - \
            max(b["y_ft"], hy["y_ft"])
        assert share >= 3.5, (
            f"the pantry shares {share:.2f} ft of wall with the hyphen and the door needs 3.50 "
            f"(`openings.required_wall_ft`). The BAND is what puts it there -- three positions "
            f"were available on that face and two of them give 2.38 ft.")
        # and the door the whole package is about is DRAWN
        und = [d for lv in q["levels"] for r in lv["rooms"] for d in (r.get("doors") or [])
               if isinstance(d, dict) and d.get("unplaced")
               and {r["id"], d.get("to")} & {"butlers"}]
        assert und == [], [f"{d.get('to')}: {d['unplaced'].get('reason')}" for d in und]

    def test_a_door_across_OPEN_GROUND_still_does_not_place_and_should_not(self):
        """The control, and it is what keeps this a fix rather than a loosening. `backhall` and
        `kitchen` are doored to each other across 14 ft of yard with no link: a detached
        dependency IS detached, and drawing that door would be the lie.

        RE-POINTED AT WP-11.16, AND THE OLD PAIR IS GONE RATHER THAN MOVED. This named
        `butlers`-`kitchen`, and that package dropped that door from the record on grounds
        `rooms/butlers-pantry.json` has stated since OQ 59 -- in a Tidewater plantation house
        "the pantry is in the block and the kitchen is in another building", so a direct door
        between them is not a door this type has. `backhall`-`kitchen` is the same shape and
        still declared: the kitchen is tagged into the wing by `_fixture()`, the back hall is
        not, and no link joins them (the hyphen doors `butlers` and `kitchen`, not `backhall`).

        THE ASSERTION BELOW IS THE TEST'S WHOLE SUBJECT, so it is worth saying what True means
        here: `_cross_doors` reports UNPLACED, and unplaced is the right answer. A False would
        mean the placer had drawn a door across open ground."""
        p = _hyphen_fixture()
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        cross = _cross_doors(p)
        assert cross[("backhall", "kitchen")] is True, cross
        # and the linked pair still places, so this is a control and not a blanket refusal
        assert cross[("butlers", "hyphen")] is False, cross
        assert cross[("backhall", "kitchen")] is True, cross

    def test_without_a_hyphen_room_EVERY_cross_element_door_is_refused(self):
        """The before. Four of four, on the fixture the whole package has used."""
        p = _hyphen_fixture(with_hyphen=False)
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        cross = _cross_doors(p)
        assert cross and all(cross.values()), cross

    def test_when_off_is_ZERO_there_is_no_P_slab_and_B_is_what_stands_on_the_low_face(self):
        """The case WP-11.17's third reverted recovery missed, driven rather than reasoned.

        That attempt forced the pantry into a rest-rectangle and considered only `P` and `R` --
        and its winning candidate had `off = 0`, where there is no `P` at all. So the forcing
        never applied to the placement the number was read off, which is half of why that
        measurement was confounded (the other half was that it used the full-face strip).

        THE CORPUS CANNOT REACH THIS BRANCH -- on the shipped record the entrance anchor's draw
        gives a `P` slab -- so it is driven directly on a hand-built element with the rng seeded
        to the draw that makes `off` zero, which is WP-11.10's stated precedent for a guard
        against a record this corpus does not yet have. Measured both ways: with `B` offered the
        pantry lands at x = 0.00, the element's own west face; with `B` removed from the offer it
        lands at x = 36.00, which is a different wall of a different room."""
        import random

        def rooms():
            return [{"id": "porch", "_area": 72.0, "type": "entry-porch", "doors": []},
                    {"id": "butlers", "_area": 84.0, "type": "butlers-pantry", "doors": []},
                    {"id": "hall", "_area": 400.0, "type": "centre-passage", "doors": []},
                    {"id": "drawing", "_area": 396.0, "type": "drawing-room", "doors": []},
                    {"id": "dining", "_area": 320.0, "type": "dining-room", "doors": []},
                    {"id": "library", "_area": 270.0, "type": "library", "doors": []}]

        # seed 1 draws the low position, so `off` is 0 and there is no `P`
        assert random.Random(1).randrange(3) == 0, (
            "the seed no longer draws the low position; find one that does rather than "
            "dropping this test -- the branch it drives is unreachable from the corpus")
        out, relax = {}, []
        laid = GEO._partial_flank(rooms(), 0, 0, 45.0, 37.24, "S", ["porch"], 9.0, 2.5,
                                  random.Random(1), out, relax, 12.0, span=None,
                                  later=(("W", ["butlers"], (9.62, 27.62), 12.0),))
        assert laid and out["porch"][:2] == pytest.approx((0.0, 0.0), abs=0.01), out.get("porch")
        assert out["butlers"][0] == pytest.approx(0.0, abs=0.01), (
            "the hosted anchor is not on the element's west face. With `off` at 0 there is no "
            "`P` slab and `B` is the rectangle standing on that face, so this is `_host_for` no "
            "longer being offered `B`: measured, the pantry goes to x = 36.00 instead.")

    def test_a_STATED_share_stops_at_the_closer_side_and_a_DRAWN_one_is_untouched(self):
        """`partition(frac=)`, WP-11.18. The scoping is the whole of why this is safe.

        The growth loop runs `while acc < target`, so the room that CROSSES the target decides
        how far past it the group lands. Where the share is a coin flip that costs nothing -- the
        share simply moves. Where the share is STATED the caller has already chosen the
        rectangles and `slice_rect` tiles whatever it is handed, so an overshooting group is a
        stretched room and its neighbour is a shrunk one. Measured on the shipped record: a
        495.9 sf target took a 408 sf room AND a 396 sf room -- 804 into a 567.9 sf rectangle --
        and left the stair alone in the slab above, drawn 567.9 sf against 126 declared.

        THE DRAWN-SHARE PATH IS ASSERTED IDENTICAL, not merely left alone: `frac is None` is
        every caller this function had before `_partial_flank`, and the ten plans that state no
        entrance face are byte-identical because of it (`tests/test_elements.py`'s digests)."""
        import random

        def rooms():
            return [{"id": "a", "_area": 408.0, "type": "centre-passage", "doors": []},
                    {"id": "b", "_area": 396.0, "type": "drawing-room", "doors": []},
                    {"id": "c", "_area": 126.0, "type": "stair-hall", "doors": []}]

        # Stated share of 0.33 over 930 sf is 306.9: `a` alone is 101 sf over, `a` + `b` is 497
        # sf over. The closer side is `a` alone.
        lo, hi = GEO.partition(rooms(), "y", random.Random(3), frac=0.33)
        assert sum(r["_area"] for r in lo) == 408.0, [r["id"] for r in lo]
        assert sorted(r["id"] for r in hi) == ["b", "c"]
        # And the whole point: the group no longer crosses the target by more than it lands short
        for frac in (0.1, 0.25, 0.33, 0.5, 0.66, 0.9):
            lo, hi = GEO.partition(rooms(), "y", random.Random(11), frac=frac)
            tot = 930.0
            acc = sum(r["_area"] for r in lo)
            assert lo and hi
            assert abs(acc - tot * frac) <= abs(acc + hi[0]["_area"] - tot * frac) or len(lo) == 1

        # THE CONTROL. A drawn share takes the same draws in the same order it always did.
        for seed in range(12):
            a = GEO.partition(rooms(), "y", random.Random(seed))
            b = GEO.partition(rooms(), "y", random.Random(seed))
            assert [r["id"] for r in a[0]] == [r["id"] for r in b[0]]

    def test_flank_slice_REFUSES_rather_than_crushing_what_will_not_fit(self):
        """A first version took every anchor. On the re-authored parti that is the CENTRE
        PASSAGE and a butler's pantry, and stating a strip for both put the passage 5.85 ft
        OUTSIDE the main block and took the composed house from 11 fatal findings to 14. It takes
        the anchors that fit, smallest first, and refuses the rest."""
        rng = __import__("random").Random(7)
        rooms = [{"id": "big", "_area": 900.0, "type": "centre-passage",
                  "width_ft": 30, "length_ft": 30},
                 {"id": "small", "_area": 60.0, "type": "butlers-pantry",
                  "width_ft": 6, "length_ft": 10},
                 {"id": "rest", "_area": 400.0, "type": "drawing-room",
                  "width_ft": 20, "length_ft": 20}]
        out, relax = {}, []
        assert GEO.flank_slice(rooms, 0, 0, 40.0, 34.0, "E", ["big", "small"],
                               9.0, 2.5, rng, out, relax) is True
        # the small anchor is on the face; the big one was refused into the remainder
        assert out["small"][0] + out["small"][2] == pytest.approx(40.0, abs=0.05), out
        assert out["big"][0] + out["big"][2] < 40.0 - 0.05, out

    def test_face_toward_REFUSES_A_DIAGONAL_NEIGHBOUR(self):
        """The ruling refuses the diagonal case rather than modelling it, and it is refused here
        in the same one condition `faces_across_a_gap` uses: a block past the corner is yard."""
        plan = {"levels": [{"index": 0, "rooms": [
            {"id": "a", "block": "A", "doors": [{"to": "b"}]},
            {"id": "b", "block": "B", "doors": [{"to": "a"}]}]}]}
        beside = [{"id": "A", "role": "main", "x": 0, "y": 0, "W": 10, "H": 10, "rooms": ["a"]},
                  {"id": "B", "role": "hyphen", "x": 20, "y": 2, "W": 10, "H": 6, "rooms": ["b"]}]
        assert GEO.hyphen_anchors(plan, beside, 0)["A"] == {"E": (["a"], (2.0, 8.0))}
        diagonal = [{"id": "A", "role": "main", "x": 0, "y": 0, "W": 10, "H": 10, "rooms": ["a"]},
                    {"id": "B", "role": "hyphen", "x": 20, "y": 20, "W": 10, "H": 6, "rooms": ["b"]}]
        assert GEO.hyphen_anchors(plan, diagonal, 0) == {}, "a block past the corner is yard"
        # AND A NEIGHBOUR THAT IS NOT A LINK IS NOT AN ANCHOR, however squarely it sits beyond
        # the face: a door across open ground cannot be placed by moving a room to the edge.
        no_link = [{"id": "A", "role": "main", "x": 0, "y": 0, "W": 10, "H": 10, "rooms": ["a"]},
                   {"id": "B", "role": "dependency", "x": 20, "y": 2, "W": 10, "H": 6,
                    "rooms": ["b"]}]
        assert GEO.hyphen_anchors(plan, no_link, 0) == {}, no_link

    def test_a_one_rectangle_plan_gets_NO_ANCHORS_and_places_identically(self):
        """The regression. `hyphen_anchors` is `{}` below two elements, so the ordinary slice runs
        with the same rng draws it always did."""
        # RE-DERIVED AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026), NOT BUMPED. This pinned
        # main's guarantee that teaching the layers about elements moved NO shipped
        # placement -- and it held for every package that made it. What arrived is the
        # OTHER Phase 11, which changed the placement itself (a band-first candidate key,
        # a span charge) exactly as this one did (its parti bay module, its stacking rule,
        # its candidate row). Two placement changes meeting cannot leave the placement
        # where either found it, and the other branch's `CORPUS_PLACEMENT_SHA` moved for
        # the same reason in the same commit. Old values: 685.3 / 592.3.
        # AND RE-DERIVED AGAIN AT WP-11.16, WITH THE TWO CAUSES SEPARATED. That package tagged
        # this record AND dropped a door, and `_shipped_untagged()` above undoes only the first:
        # the width comes back to 63 and the relaxation count to 7, so the TAGS really are gone,
        # and the score does not, because the `butlers`-`kitchen` door is gone from the record
        # whether or not its rooms carry a `block`. 775.2 -> 761.2 is the door, measured by
        # stripping. `spec-builder-colonial` was untouched by that package and unmoved here,
        # which was the control that said so -- AND IT IS NOT THAT CONTROL ANY MORE. WP-11.17
        # states the entrance front, that record names one, and its figures move with the
        # Tidewater's. The ten plans the entrance selector does NOT reach carry the control
        # now, in `tests/test_elements.py`'s corpus digests.
        # AND AGAIN AT WP-11.18, WHERE THE CAUSE IS `partition` AND NOT THE ANCHOR. That package
        # made a STATED share stop at the closer side rather than at the first overshoot, which
        # reaches every plan whose record names an entrance face -- these two among them, and no
        # others. 864.1 -> 1017.2 here and 814.4 -> 779.5 on the spec Colonial, and the two go
        # OPPOSITE WAYS on the findings as well: this fixture reads serious 60 -> 70 and minor
        # 108 -> 103, the spec Colonial serious 105 -> 97 and minor 93 -> 97. Corpus-wide the
        # package is fatal 153 -> 145 and serious 712 -> 707; this fixture is a SYNTHETIC control
        # (the shipped record is tagged) and is one of the plans that pays.
        # AND AGAIN AT THE 17 SEP MERGE: 1017.2 -> 889.0 here, the spec Colonial unmoved at
        # 779.5, and the width unmoved on both -- only the Tidewater placement moves.
        for name, score, w in (("tidewater-georgian-careful", 889.0, 63),
                               ("spec-builder-colonial", 779.5, 50.0)):
            GEO._SOLVE_CACHE.clear()
            q = _shipped_untagged() if name == "tidewater-georgian-careful" \
                else json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
            _, prep = GEO.prep_rooms(q)
            fp = GEO.derive_footprint(q, None, prep)
            assert GEO.hyphen_anchors(q, GEO.blocks_for(q, fp, prep, 0), 0) == {}, name
            GEO.solve(q, engine="heuristic")
            # AND AT WP-11.17: 761.2 -> 864.1 on this untagged fixture, WHICH IS THE SCORE
            # RISING WHILE THE FINDINGS FALL. Stating the entrance front is a HARD statement --
            # the entry porch is placed against the S face before the guillotine runs -- so the
            # search chooses from a smaller pool and cannot reach the candidate it used to. On
            # the same fixture `plan_check` reads serious 67 -> 60 and minor 109 -> 108 across
            # that rise. This corpus already records the inverse shape (a minor count rising
            # while a house got materially better); READ THE FINDINGS BEFORE QUOTING THE KEY ON
            # A PLACEMENT CHANGE, in either direction. `spec-builder-colonial` moves too --
            # 830.1 -> 814.4 -- because its record also names an entrance face, so it is no
            # longer the untouched control it was for WP-11.16 and its figure is re-derived
            # rather than carried.
            assert round(q["geometry_report"]["score"], 1) == score, (name, q["geometry_report"]["score"])
            assert q["footprint"]["width_ft"] == w, name


CMP = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))


class TestTheGarageJoinsTheElementItsAnchorIsIn:
    """WP-11.6. `attach_garage` doors its mudroom onto the kitchen and, where there is one, the
    back hall. Once a diagram can state a service dependency, that kitchen may be in one -- and a
    door between two elements cannot be placed, measured 5 of 5. A mudroom in the main block
    doored to a kitchen in a wing is a door across open ground.

    DRIVEN, and it has to be: no parti in this corpus carries a `block` today, so this branch is
    unreachable from the data and a mutation deleting it left the whole suite green until this
    class existed. That is WP-8.11's rule -- a fixture that waits for the corpus to exercise a
    branch is measuring the corpus."""

    def _plan_with_a_tagged_kitchen(self):
        p = _shipped_untagged()
        for lv in p["levels"]:
            for r in lv["rooms"]:
                if r["type"] in ("kitchen", "back-hall"):
                    r["block"] = "west-dependency"
        for lv in p["levels"]:
            lv["rooms"] = [r for r in lv["rooms"] if r["type"] not in ("garage", "mudroom")]
        return p

    def test_the_mudroom_and_the_garage_take_the_kitchens_block(self):
        p = self._plan_with_a_tagged_kitchen()
        log = []
        CMP.attach_garage(p, {"context": {"garage_bays": 2}}, log)
        ground = next(lv for lv in p["levels"] if (lv.get("index") or 0) == 0)
        by = {r["id"]: r for r in ground["rooms"]}
        assert "garage" in by, log
        assert by["garage"].get("block") == "west-dependency", (by["garage"], log)
        assert by["garage-mudroom"].get("block") == "west-dependency", (by["garage-mudroom"], log)

    def test_and_an_UNTAGGED_kitchen_leaves_them_untagged(self):
        """The control, and the byte-identity guard for every plan in this corpus: no block on
        the anchor, no block on the garage."""
        p = _shipped_untagged()
        for lv in p["levels"]:
            lv["rooms"] = [r for r in lv["rooms"] if r["type"] not in ("garage", "mudroom")]
        log = []
        CMP.attach_garage(p, {"context": {"garage_bays": 2}}, log)
        ground = next(lv for lv in p["levels"] if (lv.get("index") or 0) == 0)
        by = {r["id"]: r for r in ground["rooms"]}
        assert "garage" in by, log
        assert "block" not in by["garage"], by["garage"]
        assert "block" not in by["garage-mudroom"], by["garage-mudroom"]


# ---------------------------------------------------------------------------------------------
# WP-11.6 item 4 — CP-SAT places per element.
#
# The engine that PROVES used to REFUSE a plan with a dependency, in `geometry._solve_uncached`,
# because `geometry_cp._build` gave every room `NewIntVar(0, Wi)` and `x + w <= Wi`: one
# rectangle, one non-negative coordinate space. `auto` fell back to the hill-climb naming the
# reason, so on exactly the plans whose composition most needs proving, the search carried the
# findings. `_boxes` gives each room its own element box.
#
# **THE REGRESSION GUARD IS THE MODEL ITSELF, NOT A PLACEMENT.** A CP solve of the Tidewater
# record takes ninety seconds on this machine, which is not a test; but the MODEL CP-SAT is
# handed is deterministic and free to build, and if it is identical the placement is identical
# whatever the solver does with its budget. `test_every_shipped_plan_maps_every_room_to_the_main
# _box` is the by-construction half and the proto comparison in the report is the measured one.
# ---------------------------------------------------------------------------------------------
CP = modcache.load("geometry_cp", os.path.join(ROOT, "build", "geometry_cp.py"))


def _cp_or_skip():
    pytest.importorskip("ortools", reason="the CP-SAT engine (WP-2.3) needs ortools")
    from ortools.sat.python import cp_model
    return cp_model


def _fixture_east():
    """The same three service rooms, in an EAST dependency. It exists because a west wing is at
    NEGATIVE x and therefore tests only the lower half of every bound — the main block's `Wi` is
    looser than the wing's own east face there, so a mutation replacing one with the other cannot
    be seen. Beyond the block, `Wi` is the tighter bound and the same mutation is fatal."""
    p = _shipped_untagged()
    n = 0
    for r in p["levels"][0]["rooms"]:
        if r["type"] in ("kitchen", "pantry", "breakfast-room"):
            r["block"] = "east-dependency"
            r["exterior_walls"] = ["N", "S", "E"]
            n += 1
    assert n >= 2, "the reference plan's service room types have been renamed"
    return p


def _prepped(p):
    levels, prep = GEO.prep_rooms(p)
    fpd = CP._snap_fpd(GEO.derive_footprint(p, None, prep))
    assert "error" not in fpd, fpd
    return levels, prep, fpd


class TestTheModelIsUnchangedOnOneRectangle:
    def test_every_shipped_plan_maps_every_room_to_the_main_box(self):
        """The by-construction claim, stated as an assertion rather than as a comment.

        Every expression in `_build` that used to spell `0` / `Wi` / `Hi` inline now reads the
        room's own box. If that box IS `(0, 0, Wi, Hi)` for every room of every shipped record,
        each of those expressions is arithmetically the one it replaced — which is why the
        sixteen one-rectangle placements did not have to be re-measured one solve at a time."""
        seen = 0
        tagged_seen = 0
        import glob
        for f in sorted(glob.glob(os.path.join(ROOT, "plans", "**", "*.json"), recursive=True)):
            p = json.load(open(f))
            if "levels" not in p:
                continue
            levels, prep = GEO.prep_rooms(p)
            fpd = GEO.derive_footprint(p, None, prep)
            if "error" in fpd:
                continue
            fpd = CP._snap_fpd(fpd)
            boxes, main = CP._boxes(p, prep, fpd)
            assert main == (0, 0, int(round(fpd["W"] * CP.U)), int(round(fpd["H"] * CP.U)))
            assert boxes, f
            # WP-11.16 TAGGED ONE SHIPPED PLAN, so this sweep has BOTH cases to make now and is
            # stronger for it: the fifteen one-rectangle records must map every room to the main
            # box, and the tagged one must NOT -- a sweep that silently skipped it would be
            # asserting the by-construction claim over a corpus chosen to satisfy it.
            if _is_tagged(p):
                tagged_seen += 1
                assert set(boxes.values()) != {main}, (
                    os.path.basename(f), "a tagged plan maps every room to the main box, so the "
                    "per-element boxes are not being read")
                continue
            for key, b in boxes.items():
                assert b == main, (os.path.basename(f), key, b, main)
            seen += 1
        assert seen >= 14, seen
        assert tagged_seen == 1, (
            f"{tagged_seen} shipped plan(s) carry a block tag; this sweep is written for exactly "
            f"one (WP-11.16) and both of its branches must stay exercised")

    def test_no_shipped_plan_gets_a_WIDENED_domain(self):
        """**THE REGRESSION GUARD OF THIS PACKAGE, AND IT WAS EARNED BY AN INSTRUMENT THAT COULD
        NOT FAIL.**

        Item 4 widened four variable domains so a wing's negative coordinates fit — and the
        first version widened them UNCONDITIONALLY, on the argument that a looser domain cannot
        change an answer. **A domain is an input to presolve, not a comment**, and the objective
        model moved on seven of the sixteen shipped records. It was published as byte-identical
        first, because the instrument saying so — a serialise-and-hash of `_build`'s proto —
        threw `AttributeError: no attribute 'SerializeToString'` on BOTH sides, so `diff`
        compared two identical tracebacks and reported no difference. An instrument that cannot
        fail is worse than a test that cannot fail, because its output is a number.

        `_wide` returns its arguments unchanged below two elements. The check is that no
        variable in the model carries the widened domain, computed here the way `_build`
        computes it rather than quoted, so it cannot drift."""
        cp_model = _cp_or_skip()
        import glob
        seen = 0
        tagged_seen = 0
        for f in sorted(glob.glob(os.path.join(ROOT, "plans", "**", "*.json"), recursive=True)):
            plan = json.load(open(f))
            if "levels" not in plan:
                continue
            levels, prep = GEO.prep_rooms(plan)
            fpd = GEO.derive_footprint(plan, None, prep)
            if "error" in fpd:
                continue
            fpd = CP._snap_fpd(fpd)
            boxes, main = CP._boxes(plan, prep, fpd)
            # THE TAGGED PLAN IS THE CONTROL, NOT AN EXCEPTION (WP-11.16). `_wide` widens only
            # above one element, so the one record that has a wing MUST carry widened domains --
            # which is the other half of this guard and could not be asserted until a shipped
            # plan had a wing. A sweep that merely skipped it would leave `_wide`'s live branch
            # untested on the corpus.
            if _is_tagged(plan):
                tagged_seen += 1
                assert set(boxes.values()) != {main}, os.path.basename(f)
                continue
            assert set(boxes.values()) == {main}, os.path.basename(f)
            ext = max([abs(c) for b in boxes.values() for c in b] + [main[2], main[3]]) * 2 + 1
            m, rooms, reqs = CP._build(plan, prep, fpd, GEO.entrance_walls(plan), objective=True)
            proto = m.Proto()
            assert len(proto.variables) > 100, (f, len(proto.variables))
            widened = [i for i, v in enumerate(proto.variables) if list(v.domain) == [-ext, ext]]
            assert not widened, (os.path.basename(f), len(widened),
                                 "a one-rectangle plan carries a widened domain — the model "
                                 "CP-SAT presolves is not the one it presolved before item 4")
            seen += 1
        assert seen >= 14, seen
        assert tagged_seen == 1, (
            f"{tagged_seen} shipped plan(s) carry a block tag; this sweep is written for exactly "
            f"one (WP-11.16)")

    def test_and_a_MULTI_element_plan_DOES_get_it(self):
        """The control. Without it the test above passes if `_wide` never widens at all, which
        would put the west wing's negative distances back in an infeasible domain."""
        _cp_or_skip()
        p = _fixture()
        levels, prep, fpd = _prepped(p)
        boxes, main = CP._boxes(p, prep, fpd)
        ext = max([abs(c) for b in boxes.values() for c in b] + [main[2], main[3]]) * 2 + 1
        m, rooms, reqs = CP._build(p, prep, fpd, GEO.entrance_walls(p), objective=True)
        widened = [v for v in m.Proto().variables if list(v.domain) == [-ext, ext]]
        assert widened, "no domain was widened on a plan with a wing"

    def test_the_main_block_is_sized_from_its_own_rooms_and_that_moves_nothing_here(self):
        """`derive_footprint` counted a dependency's programme into the main block AND laid the
        dependency beside it, so the wing's area was counted twice. With one element the two
        sums are the same sum, which is why no shipped record moved."""
        p = _shipped_untagged()
        levels, prep = GEO.prep_rooms(p)
        assert not any(GEO.is_block_tag(r.get("block")) for r in prep[0])
        a_all = sum(r["_area"] for r in prep[0])
        a_main = sum(r["_area"] for r in prep[0] if not GEO.is_block_tag(r.get("block")))
        assert a_all == a_main


class TestCPSATPlacesPerElement:
    def test_the_wing_gets_its_own_box_and_everyone_else_the_main_one(self):
        p = _fixture()
        levels, prep, fpd = _prepped(p)
        boxes, main = CP._boxes(p, prep, fpd)
        wing = {rid for lv in p["levels"] for r in lv["rooms"] if r.get("block")
                for rid in [r["id"]]}
        assert len(wing) >= 2, wing
        wing_boxes = {boxes[(0, rid)] for rid in wing}
        assert len(wing_boxes) == 1, wing_boxes
        wb = wing_boxes.pop()
        assert wb != main, (wb, main)
        assert wb[0] < 0, wb          # a west wing sits at negative x: the whole difficulty
        for (lvl, rid), b in boxes.items():
            if lvl == 0 and rid in wing:
                continue
            assert b == main, (lvl, rid, b)

    def test_the_UPPER_level_is_the_main_block_whatever_a_room_says(self):
        """`blocks_for` lays only level 0 into elements. Inventing a box for an upper room
        would be a drawn claim nobody placed — the per-element roof is the ruling's own
        unbuilt item."""
        p = _fixture()
        for r in p["levels"][1]["rooms"]:
            r["block"] = "west-dependency"
        levels, prep, fpd = _prepped(p)
        boxes, main = CP._boxes(p, prep, fpd)
        for r in prep.get(1, []):
            assert boxes[(1, r["id"])] == main, (r["id"], boxes[(1, r["id"])])

    def test_the_main_block_is_sized_from_the_main_blocks_own_programme(self):
        """The defect the prover surfaced and the search had absorbed in silence: the wing's
        area was counted into the main block AND laid beside it."""
        p = _fixture()
        levels, prep = GEO.prep_rooms(p)
        a_all = sum(r["_area"] for r in prep[0])
        a_main = sum(r["_area"] for r in prep[0] if not GEO.is_block_tag(r.get("block")))
        assert a_all - a_main > 300, (a_all, a_main)
        fpd = GEO.derive_footprint(p, None, prep)
        # the derived block holds the main-block programme, not the whole building's
        assert fpd["need"] == max(a_main, sum(r["_area"] for r in prep.get(1, [])))
        assert fpd["W"] * fpd["H"] < a_all, (fpd["W"], fpd["H"], a_all)

    def test_the_hard_model_is_SATISFIABLE_with_a_dependency(self):
        """The whole of item 4 in one assertion. Before it, this model was INFEASIBLE with
        every assumption dropped and no conflict to name — the interval END variables still
        carried `NewIntVar(0, Wi)`, which cannot hold a west wing's negative coordinate."""
        cp_model = _cp_or_skip()
        p = _fixture()
        levels, prep, fpd = _prepped(p)
        m, rooms, reqs = CP._build(p, prep, fpd, GEO.entrance_walls(p), objective=False)
        # ASSUMPTIONS CLEARED, which is the model `_extract_conflicts` reaches when it says
        # "the rooms cannot tile any footprint this parti and lot allow, EVEN WITH EVERY
        # DECLARED REQUIREMENT DROPPED". That is the sentence the interval-end bug produced,
        # and it is a statement about containment and no-overlap alone. The round loop's own
        # first pass is legitimately INFEASIBLE here -- it downgrades wall pins and retries --
        # so asserting on it would be asserting on the declared walls, not on this change.
        m.ClearAssumptions()
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = 30.0
        s.parameters.num_search_workers = 1
        s.parameters.random_seed = 7
        st = s.Solve(m)
        assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), s.StatusName(st)
        # and every wing room is drawn INSIDE its wing, which is what the refusal was about:
        # handed a dependency, the old engine placed its rooms inside the main block while
        # `footprint.blocks` went on describing an element somewhere else
        boxes, main = CP._boxes(p, prep, fpd)
        wing = [r for r in prep[0] if r.get("block")]
        assert wing
        for r in wing:
            bx0, by0, bx1, by1 = boxes[(0, r["id"])]
            v = rooms[(0, r["id"])]
            x, y = s.Value(v["x"]), s.Value(v["y"])
            w, h = s.Value(v["w"]), s.Value(v["h"])
            assert bx0 <= x and x + w <= bx1, (r["id"], x, w, bx0, bx1)
            assert by0 <= y and y + h <= by1, (r["id"], y, h, by0, by1)

    def test_a_door_across_open_ground_is_stated_and_is_NOT_an_infeasibility(self):
        """A detached dependency is detached. The door rule is a HARD abutment
        (`a.x + a.w == b.x`) — vacuous while every room shared one rectangle, real the moment
        the elements are — so left alone it would prove a buildable house impossible. The
        heuristic draws such a door `unplaced` with a reason; the prover says the same thing."""
        _cp_or_skip()
        p = _fixture()
        levels, prep, fpd = _prepped(p)
        m, rooms, reqs = CP._build(p, prep, fpd, GEO.entrance_walls(p), objective=False)
        gap = [n for n in reqs.notes if "elements that do not touch" in n]
        assert gap, sorted(reqs.notes)[:6]
        # and no such door is a requirement of the model
        assert not [t for _l, t, k, _key in reqs.lits
                    if k == "door" and "Kitchen (Dependency)" in t and "Back Hall" in t]

    def test_a_door_INSIDE_one_element_is_still_a_requirement(self):
        """The control. If the clause above refused every door the model would be trivially
        satisfiable and this class would prove nothing."""
        _cp_or_skip()
        p = _fixture()
        levels, prep, fpd = _prepped(p)
        m, rooms, reqs = CP._build(p, prep, fpd, GEO.entrance_walls(p), objective=False)
        doors = [t for _l, t, k, _key in reqs.lits if k == "door"]
        assert len(doors) >= 8, doors
        gap = [n for n in reqs.notes if "elements that do not touch" in n]
        assert len(gap) < len(doors), (len(gap), len(doors))

    def test_A_DOOR_THROUGH_THE_LINK_IS_STILL_A_HARD_REQUIREMENT(self):
        """**The claim that the hyphen's abutment needed no new constraint, measured rather than
        asserted.** The plan text called it "the seventh defect", to be added; `_build`'s door
        rule was already `a.x + a.w == b.x` with the two overlap bounds — a hard abutment,
        vacuous while every room shared one rectangle.

        On the hyphen fixture: the hyphen abuts BOTH the dependency and the main block, and the
        dependency abuts the main block not at all. So the door the link exists to carry is kept
        as a requirement, and the three doors that would have to cross open ground are stated as
        outside the model. **Without both halves this test is worthless**: if `_abuts` said
        everything touches, the model would prove a buildable house impossible; if it said
        nothing touches, no cross-element door would be a requirement anywhere and the hyphen
        would carry nothing."""
        _cp_or_skip()
        p = _hyphen_fixture()
        levels, prep, fpd = _prepped(p)
        boxes, main = CP._boxes(p, prep, fpd)
        by_el = {}
        for (lvl, rid), b in boxes.items():
            if lvl == 0:
                by_el.setdefault(b, []).append(rid)
        hyph = next(b for b, ids in by_el.items() if ids == ["hyphen"])
        dep = next(b for b, ids in by_el.items() if "kitchen" in ids)
        assert CP._abuts(hyph, dep) and CP._abuts(hyph, main), (hyph, dep, main)
        assert not CP._abuts(dep, main), (dep, main, "a detached dependency touches the house")
        m, rooms, reqs = CP._build(p, prep, fpd, GEO.entrance_walls(p), objective=False)
        kept = [t for _l, t, k, _key in reqs.lits
                if k == "door" and "Hyphen" in t and "Kitchen (Dependency)" in t]
        assert kept, [t for _l, t, k, _k in reqs.lits if k == "door" and "Hyphen" in t]
        stated = [n for n in reqs.notes if "elements that do not touch" in n]
        # 2 AT WP-11.16, from 3: the direct `butlers`-`kitchen` door was dropped from the
        # record, so there is one fewer declared crossing for the model to decline to model.
        #
        # AND A VACUITY NOTE, BECAUSE THIS COUNT IS NOW ONE DOOR FROM ZERO. The docstring above
        # says why both halves are needed -- `kept` proves `_abuts` does not say "nothing
        # touches", `stated` proves it does not say "everything touches". At 2 both still bite.
        # At 0 the second half would be vacuously satisfied and this test would quietly stop
        # proving the negative, so if a later package takes another crossing out of the record,
        # this fixture has to declare one of its own rather than have the number lowered again.
        #
        # BACK TO 3 AT THE 17 SEP MERGE, AND THE WARNING ABOVE IS WHY RATHER THAN DESPITE.
        # Both lines dropped that door from the record for the same reason; then this branch's
        # WP-13.5 did what the paragraph above asks -- `_hyphen_fixture` DECLARES the
        # `butlers`-`kitchen` crossing of its own, so the guard keeps three to state -- while
        # main lowered the literal to 2 instead. The merge carries the fixture AND the literal,
        # which is how a 3 met a 2. The fixture is the half the note demands and the literal is
        # the half it warns against, so the literal goes back up and the fixture stays.
        # Re-derived on the merged tree: Butler's Pantry, Back Hall (Hyphen) and Cellar Stair,
        # each against Kitchen (Dependency).
        assert len(stated) == 3, stated
        assert all("Kitchen (Dependency)" in n for n in stated), stated

    def test_abuts_is_a_shared_FACE_and_a_corner_is_not_one(self):
        assert CP._abuts((0, 0, 10, 10), (0, 0, 10, 10))          # the one-element case
        assert CP._abuts((0, 0, 10, 10), (10, 0, 20, 10))         # east face
        assert CP._abuts((0, 0, 10, 10), (-5, 2, 0, 8))           # west face, partial overlap
        assert CP._abuts((0, 0, 10, 10), (0, 10, 10, 20))         # north face
        assert not CP._abuts((0, 0, 10, 10), (14, 0, 20, 10))     # a gap
        assert not CP._abuts((0, 0, 10, 10), (10, 10, 20, 20))    # a corner is not a face
        assert not CP._abuts((0, 0, 10, 10), (10, 12, 20, 20))    # past the corner: yard

    def test_absorb_takes_an_origin_and_a_wing_room_cannot_grow_across_the_gap(self):
        """`_absorb`'s limits were `W`, `H` and a literal `0.0` — the main block and only the
        main block. Run over a west wing's rooms it grew them east across the gap into the
        house and west out through the wing's own wall."""
        wing = {"a": (-41.0, 10.0, 10.0, 20.0)}
        grown = CP._absorb(wing, 27.0, 20.0, x0=-41.0, y0=10.0)
        x, y, w, h = grown["a"]
        assert x >= -41.0 - 0.01, grown
        assert x + w <= -14.0 + 0.01, grown
        assert y >= 10.0 - 0.01 and y + h <= 30.0 + 0.01, grown
        # the control: the same rectangle at the origin grows to the frame it is given
        at_origin = CP._absorb({"a": (0.0, 0.0, 10.0, 20.0)}, 27.0, 20.0)
        assert at_origin["a"][2] > 10.0, at_origin

    def test_an_element_boundary_is_not_counted_as_an_interior_wall(self):
        """`_count_relaxations` measured every edge against the main block's frame, so a wing's
        own two flanks read as interior lines off the bay grid and every wall it has read as a
        compromise. The bay grid starts at the element's own origin for the same reason."""
        rects = {0: {"a": (-41.0, 10.0, 27.0, 20.0)}}
        boxes_ft = {(0, "a"): (-41.0, 10.0, -14.0, 30.0)}
        assert CP._count_relaxations(rects, 45.0, 41.0, 9.0, 2.5, boxes_ft=boxes_ft) == []
        # ...and read in the main block's frame instead, the same wing reports compromises
        blind = CP._count_relaxations(rects, 45.0, 41.0, 9.0, 2.5)
        assert blind, "the frame makes no difference — the guard is not reading what it thinks"


class TestTheDisclosureIsOnBOTHEngines:
    def test_the_cp_record_writer_attaches_the_multi_element_block(self):
        """It was attached in `write_record` only — which the heuristic uses and the CP path
        does not — so the one engine every multi-element plan was sent away from was the only
        one that disclosed anything about them."""
        # RE-CUT AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026). Main attached the disclosure
        # in BOTH record writers and counted two call sites; the other branch hit the identical
        # defect ("a disclosure wired into one record writer and not the other is no
        # disclosure") and fixed it by routing both writers through ONE `_disclose(plan)`, so a
        # third writer cannot be added and forgotten. Counting call sites now reads 1 and would
        # convict the stronger arrangement. The PROPERTY is what both fixes were for: the block
        # is on the record whichever writer produced it, so it is asserted that way -- and the
        # one-call-site consolidation is asserted too, so it cannot silently become two again.
        src = open(os.path.join(ROOT, "build", "geometry.py")).read()
        calls = [ln for ln in src.splitlines()
                 if "multi_element_disclosure(plan)" in ln and not ln.lstrip().startswith("def ")]
        assert len(calls) == 1, (calls, "there is one _disclose(); do not re-add a second writer")
        assert src.count("_disclose(plan)") >= 2, (
            "both record writers must route through _disclose(); a guarantee that holds on one "
            "engine is not one")

    def test_the_note_no_longer_says_the_prover_refuses_a_multi_element_plan(self):
        """With the refusal gone, that sentence would be a false statement about the engine —
        and a note claiming an engine is unavailable when it is available is the fake-unjudged
        direction, which this corpus treats as exactly as dishonest as a fake pass."""
        p = _fixture()
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        me = (p.get("geometry_report") or {}).get("multi_element")
        assert me and me["elements"] == 2, me
        assert "REFUSES a multi-element plan" not in me["note"], me["note"]
        assert "places each element in its own rectangle" in me["note"], me["note"]


class TestTheFourGuardsTheFirstMutationPassMISSED:
    """Four of fifteen mutations left the suite green on the first pass, and each is recorded
    here with what it proved was unguarded rather than with a looser assertion.

    They share one shape: the class above asserts that the tagged model is SATISFIABLE and that
    the solution it returns sits inside the wing. Satisfiability is a weak instrument -- a
    LOOSER model is still satisfiable, and a returned solution can happen to be contained -- so
    a mutation that only widens a bound passes it. Each test below drives the specific bound.
    """

    def test_containment_reads_the_ELEMENT_and_an_EAST_wing_is_what_proves_it(self):
        """M3: `x + w <= Wi` instead of `<= bx1`.

        **THE WEST-WING FIXTURE CANNOT TELL THE TWO APART, AND THE FIRST VERSION OF THIS TEST
        PASSED UNDER THE MUTATION FOR THE WRONG REASON.** A west wing sits at negative x, so the
        main block's bound is far LOOSER than its own and no legal placement violates it; forcing
        a wing room past its east face is refused all right, but by the coverage floor on the main
        block's rooms, which the intruding rectangle would have to overlap. The right answer from
        the wrong constraint is the shape this repository keeps meeting.

        An EAST wing is the discriminator: it stands beyond `Wi`, so `x + w <= Wi` is not looser
        there, it is UNSATISFIABLE — the whole model goes infeasible and the assertion below is
        the containment rule itself. A fixture that only ever tests one side of a bound has tested
        half of it."""
        cp_model = _cp_or_skip()
        p = _fixture_east()
        levels, prep, fpd = _prepped(p)
        boxes, main = CP._boxes(p, prep, fpd)
        east = [b for (lvl, rid), b in boxes.items() if b != main]
        assert east and east[0][0] > main[2], (east, main, "the wing is not east of the block")
        m, rooms, reqs = CP._build(p, prep, fpd, GEO.entrance_walls(p), objective=False)
        m.ClearAssumptions()
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = 30.0
        s.parameters.num_search_workers = 1
        s.parameters.random_seed = 7
        st = s.Solve(m)
        assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), (
            s.StatusName(st), "an east wing stands beyond the main block's width, so a "
                              "containment bound of Wi cannot hold it")
        for r in prep[0]:
            if not r.get("block"):
                continue
            bx0, by0, bx1, by1 = boxes[(0, r["id"])]
            v = rooms[(0, r["id"])]
            assert bx0 <= s.Value(v["x"]) and s.Value(v["x"]) + s.Value(v["w"]) <= bx1

    def test_the_DEPTH_bound_is_the_elements_too_and_the_corpus_cannot_reach_it(self, monkeypatch):
        """The x bound above has an east wing to prove it. The **y** bound has nothing: a
        dependency is centred on the main block's axis and is never deeper than it, so
        `y + h <= Hi` is always looser than `y + h <= by1` and a mutation swapping them leaves
        the suite green. Measured — M3b MISSED on the sweep that caught the other fourteen.

        So it is DRIVEN, exactly as layer 6's garage-element branch had to be: `blocks_for` is
        replaced with one returning a wing DEEPER than the main block, which is a state the
        placer could reach the day a dependency takes two storeys or a single-pile depth wider
        than the house. Under the main block's bound that wing's rooms cannot use their own
        southern half at all, and the coverage floor they owe it goes unsatisfiable."""
        cp_model = _cp_or_skip()
        p = _fixture()
        levels, prep, fpd = _prepped(p)
        real = GEO.blocks_for

        def deeper(plan, fp, prp, level=0):
            out = [dict(b) for b in real(plan, fp, prp, level)]
            for b in out:
                if b.get("role") != "main":
                    # south of the block and deeper than it: y runs past H on both sides
                    b["y"], b["H"] = -6.0, fp["H"] + 12.0
            return out

        monkeypatch.setattr(GEO, "blocks_for", deeper)
        boxes, main = CP._boxes(p, prep, fpd)
        wing = next(b for (lvl, rid), b in boxes.items() if b != main)
        assert wing[1] < main[1] and wing[3] > main[3], (wing, main)
        m, rooms, reqs = CP._build(p, prep, fpd, GEO.entrance_walls(p), objective=False)
        m.ClearAssumptions()
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = 30.0
        s.parameters.num_search_workers = 1
        s.parameters.random_seed = 7
        st = s.Solve(m)
        assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), (
            s.StatusName(st), "a wing deeper than the main block cannot be placed — the depth "
                              "bound is the main block's")
        for r in prep[0]:
            if not r.get("block"):
                continue
            v = rooms[(0, r["id"])]
            y, h = s.Value(v["y"]), s.Value(v["h"])
            assert wing[1] <= y and y + h <= wing[3], (r["id"], y, h, wing)

    def test_a_wing_rooms_declared_WEST_wall_is_its_ELEMENTS_west_face(self):
        """M4: the wall pins read `v["x"] == 0` again — the main block's west face, forty-one
        feet from the wing's. Assumed alone (the round loop's own idiom), the pin must put the
        room at the WING's edge. This is the mechanism behind the twelve downgrades falling to
        four: a service room's declared walls are the exposures of a wing."""
        cp_model = _cp_or_skip()
        p = _fixture()
        levels, prep, fpd = _prepped(p)
        boxes, main = CP._boxes(p, prep, fpd)
        rid = "kitchen"
        assert "W" in (next(r for r in prep[0] if r["id"] == rid).get("exterior_walls") or [])
        m, rooms, reqs = CP._build(p, prep, fpd, GEO.entrance_walls(p), objective=False)
        m.ClearAssumptions()
        # All three wing rooms take the SOFT branch here ("it protrudes", so it must reach at
        # least one of its declared walls), and a soft literal carries no `key` — hence the
        # selection by text. Soft is not weak: `AddBoolOr(touch)` is still a requirement, and
        # under the main block's reading it is an UNSATISFIABLE one, because the kitchen's x
        # runs -41..-14 and its y 10.66..30.73, so not one of the main block's four faces is
        # reachable. The status alone is the guard; the containment check below says which face.
        lits = [lit for lit, t, k, key in reqs.lits
                if k.startswith("wall") and t.startswith("Kitchen (Dependency)")]
        assert len(lits) == 1, [t for _l, t, k, _k in reqs.lits if k.startswith("wall")]
        m.AddAssumptions(lits)
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = 25.0
        s.parameters.num_search_workers = 1
        s.parameters.random_seed = 7
        st = s.Solve(m)
        assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), (
            s.StatusName(st), "the kitchen cannot reach any of its own declared walls — the "
                              "pins are on the main block, forty-one feet away")
        v = rooms[(0, rid)]
        x, y, w, h = (s.Value(v["x"]), s.Value(v["y"]), s.Value(v["w"]), s.Value(v["h"]))
        bx0, by0, bx1, by1 = boxes[(0, rid)]
        assert x == bx0 or y == by0 or y + h == by1, (x, y, h, boxes[(0, rid)])
        assert (bx0, by0, by1) != (main[0], main[1], main[3]), (
            "the wing's faces coincide with the main block's — the fixture cannot tell the two "
            "readings apart")

    def test_the_model_WITH_ITS_OBJECTIVE_builds_and_solves_on_a_wing(self):
        """M11: the bay-snap block measured every edge from the MAIN block's origin. `ev` has
        domain [0, span] and a west wing's edges are negative, so that is not a worse objective,
        it is an INFEASIBLE model — and every test above built `objective=False`, so the entire
        soft half of the model was unexercised on a multi-element plan.

        **THE ASSERTION IS `not INFEASIBLE` SINCE WP-13.5, AND THE REASON IS A MEASUREMENT.**
        It used to require OPTIMAL or FEASIBLE at 30 s on one worker, and that is a proxy: the
        defect M11 guards against makes the model UNSATISFIABLE, and UNKNOWN is a fact about the
        clock. WP-13.5 withdrew `hallbath stacks_over powder` from the record this fixture is
        built on, and that one soft term is the whole difference — isolated by restoring each of
        the package's two record edits alone, at 30 s and one worker:

            as shipped (WP-13.5)             UNKNOWN
            + the dropped door restored      UNKNOWN
            + the stack claim restored       FEASIBLE      <- this one
            + both restored (the old fixture) FEASIBLE

        The model is satisfiable either way and it is measured: one worker at 60 s FEASIBLE,
        one worker at 120 s FEASIBLE, four workers at 30 s FEASIBLE. So REMOVING a soft
        objective term made this model undecidable inside the old budget, which is WP-7.4's own
        recorded shape ("a new search term can be worse in the middle of its range than at
        either end") arriving from the other direction. The budget is NOT raised to bury that:
        UNKNOWN skips as COULD NOT EVALUATE with its own figures, and a decided solve still has
        to decide the right way."""
        cp_model = _cp_or_skip()
        p = _fixture()
        levels, prep, fpd = _prepped(p)
        m, rooms, reqs = CP._build(p, prep, fpd, GEO.entrance_walls(p), objective=True)
        m.ClearAssumptions()
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = 30.0
        s.parameters.num_search_workers = 1
        s.parameters.random_seed = 7
        st = s.Solve(m)
        # THE PROPERTY, and it is load-independent: M11's defect made the objective model
        # UNSATISFIABLE on a wing, and no budget makes an infeasible model feasible.
        assert st != cp_model.INFEASIBLE, (
            "the objective half of the model is INFEASIBLE on a multi-element plan — M11 is "
            "back: some soft term is measuring a wing's edge from the main block's origin")
        if st == cp_model.UNKNOWN:
            pytest.skip("COULD NOT EVALUATE — the objective model on this wing did not decide "
                        "in 30 s on one worker. It is satisfiable (60 s on one worker, or 30 s "
                        "on four, both FEASIBLE here); the assertion above is the one this test "
                        "is about and it held.")
        assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), s.StatusName(st)

    def test_a_wing_rooms_door_to_the_EXTERIOR_reaches_the_wings_envelope(self):
        """M15: the exterior-door rule read the main block's four faces. A wing room satisfies
        none of them, so the requirement becomes unsatisfiable — a door to the outside from a
        detached kitchen proving the house impossible."""
        cp_model = _cp_or_skip()
        p = _fixture()
        rid = None
        for lv in p["levels"]:
            for r in lv["rooms"]:
                if r.get("block") and rid is None:
                    rid = r["id"]
                    r.setdefault("doors", []).append({"to": "exterior"})
        assert rid
        levels, prep, fpd = _prepped(p)
        boxes, main = CP._boxes(p, prep, fpd)
        m, rooms, reqs = CP._build(p, prep, fpd, GEO.entrance_walls(p), objective=False)
        m.ClearAssumptions()
        lits = [lit for lit, t, k, key in reqs.lits
                if k == "door" and "door to the exterior" in t and rid in t.lower().replace(" ", "")
                or (k == "door" and "door to the exterior" in t)]
        assert lits, [t for _l, t, k, _k in reqs.lits if k == "door"]
        m.AddAssumptions(lits)
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = 25.0
        s.parameters.num_search_workers = 1
        s.parameters.random_seed = 7
        st = s.Solve(m)
        assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), (
            s.StatusName(st), "a wing room's door to the outside cannot be satisfied — the rule "
                              "is reading the main block's envelope")
        v = rooms[(0, rid)]
        bx0, by0, bx1, by1 = boxes[(0, rid)]
        x, y, w, h = (s.Value(v["x"]), s.Value(v["y"]), s.Value(v["w"]), s.Value(v["h"]))
        assert x == bx0 or x + w == bx1 or y == by0 or y + h == by1, (x, y, w, h, boxes[(0, rid)])

    def test_the_element_fill_is_the_elements_own_slack(self):
        """M14: `fill` sets each room's area CEILING and was the whole building's ratio, so a
        wing room was licensed to grow by a share of the main block. Inline in `_build` it was
        unreadable and a mutation putting the building's ratio back left the suite green."""
        p = _fixture()
        levels, prep, fpd = _prepped(p)
        boxes, main = CP._boxes(p, prep, fpd)
        fills = CP._element_fills(boxes, prep[0], 0)
        assert len(fills) == 2, fills
        wing_box = next(b for b in fills if b != main)
        building = (fpd["W"] * fpd["H"]) / sum(r["_area"] for r in prep[0])
        assert abs(fills[wing_box] - building) > 0.1, (fills, building,
            "the wing's slack and the building's coincide — the fixture cannot tell them apart")
        # the wing is sized from its own rooms, so its slack is close to 1.0 and its rooms take
        # the floor of the cap; the building's ratio would hand them a fifth as much again
        # 1.146 AT THE MERGE, AND THE CEILING MOVED FOR A STATED REASON (8 Sep 2026). The
        # other branch's WP-11.13 found a non-main element's box was sized to EXACTLY its
        # rooms' area (`H = need / W`, zero slack) while `_element_boxes` rounds both edges
        # of each axis INWARD, so the box the proving model works in was smaller than its
        # own contents and the plan was infeasible before a declared fact was read. The
        # allowance it added is DERIVED by solving `(W - 2g)(H - 2g) >= need`, not chosen,
        # and it is exactly what lifts this wing's fill from ~1.0 to 1.146. What the guard
        # is for is unchanged: the fill is the ELEMENT's own slack and not the building's,
        # which on this fixture is about 1.9 -- so the ceiling still separates them.
        assert 0.9 <= fills[wing_box] <= 1.25, fills[wing_box]

    def test_a_ONE_element_plan_gets_ONE_fill_and_it_is_the_buildings(self):
        """The control, and the byte-identity claim in its own right: with one element the
        function returns exactly the number the line it replaced computed."""
        p = _shipped_untagged()
        levels, prep, fpd = _prepped(p)
        boxes, main = CP._boxes(p, prep, fpd)
        fills = CP._element_fills(boxes, prep[0], 0)
        assert list(fills) == [main], fills
        assert abs(fills[main]
                   - (fpd["W"] * fpd["H"]) / sum(r["_area"] for r in prep[0])) < 1e-9
