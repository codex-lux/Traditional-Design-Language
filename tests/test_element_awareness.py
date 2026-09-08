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

GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
OP = modcache.load("openings", os.path.join(ROOT, "build", "openings.py"))


def _fixture():
    """The same tagging `test_geometry.py::_tagged_dependency_plan` uses, kept in step with it
    deliberately: two files measuring two different dependencies would be two houses."""
    p = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
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
        p = GEO.solve(json.load(open(os.path.join(
            ROOT, "plans", "tidewater-georgian-careful.json"))), engine="heuristic")
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
        sec = ST.build_section(json.load(open(os.path.join(
            ROOT, "plans", "tidewater-georgian-careful.json"))))
        assert all("element" not in w for lv in sec["levels"] for w in lv["walls"])
        assert all("element" not in s for lv in sec["levels"] for s in lv["spans"])
        # and the numbers this plan has always reported
        over = [s for lv in sec["levels"] for s in lv["spans_exceeding_capacity"]]
        # RE-DERIVED AT THE MERGE (8 Sep 2026): 53.94 -> 35.5 ft. Both branches changed the
        # placement, so the worst span on this fixture is neither parent's. What the line
        # is for -- the span is OVER the 20 ft capacity and therefore judged -- is
        # unchanged, and the capacity itself is untouched.
        assert round(max(s["span_ft"] for s in over), 2) == 35.5


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
        assert by["kitchen"] == ["N", "S", "W"] and by["breakfast"] == ["E", "S"], by

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
                ("tidewater-georgian-careful", "b8faf56908995542", 210,
                 {"daylight": 13, "grouping": 18}),
                ("spec-builder-colonial", "024fa784786c2469", 243,
                 {"daylight": 11, "grouping": 17})):
            GEO._SOLVE_CACHE.clear()
            q = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
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
                f"`envelopes` returns {{}} below two elements, so nothing here may change; "
                f"re-measure before re-pinning and say what moved.")


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
        """40 points, measured: vertical_score 114 -> 74 on this fixture."""
        p = _cross_element_claim()
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        with_unjudged = p["geometry_report"]["vertical_score"]
        # the same fixture with the claim naming a MAIN-block room is charged as before
        q = _fixture()
        next(r for r in q["levels"][1]["rooms"]
             if r["id"] == "primarybath")["stacks_over"] = "butlers"
        GEO._SOLVE_CACHE.clear()
        GEO.solve(q, engine="heuristic")
        assert q["geometry_report"]["vertical_score"] > with_unjudged, (
            "the cross-element claim must cost less than a real break, or it is still charged")

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
        p = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        assert GEO.element_of(p, p["levels"][0]["rooms"]) == {}
        # and non-empty on the fixture BEFORE any placement has written a blocks list
        f = _fixture()
        assert "blocks" not in (f.get("footprint") or {})
        assert GEO.element_of(f, f["levels"][0]["rooms"])


def _lot(lot, dep=True):
    """The fixture at a stated lot width. `dep=False` is the SAME plan with no tag at all --
    one rectangle, which is what every plan in this corpus is, and which is where layer 4's
    second finding lives."""
    p = _fixture() if dep else json.load(open(os.path.join(
        ROOT, "plans", "tidewater-georgian-careful.json")))
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
        none = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
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
        for name, score, width, capped in (
                ("tidewater-georgian-careful", 775.2, 63, False),
                ("spec-builder-colonial", 830.1, 50.0, True)):
            GEO._SOLVE_CACHE.clear()
            q = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
            GEO.solve(q, engine="heuristic")
            g = q["geometry_report"]
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
        p = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
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
            q = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
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
    parti that happens to."""
    p = _fixture()
    g = p["levels"][0]["rooms"]
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
        # Each element's own room that doors THROUGH THE LINK, on the face the link is beyond.
        assert a["main"] == {"W": ["butlers"]}, a["main"]
        assert a["west-dependency"] == {"E": ["kitchen"]}, a["west-dependency"]
        assert set(a["west-dependency-hyphen"]) == {"E", "W"}, a["west-dependency-hyphen"]
        # AND `butlers -> kitchen` PUT NOTHING HERE. That pair crosses open ground with no link
        # between them, and no laying of rooms can place it, so it is not an anchor: `butlers` is
        # on the list because it doors to the HYPHEN, and `backhall` and `cellarstair`, which
        # door only to the kitchen, are on no list at all.
        assert "backhall" not in a["main"]["W"] and "cellarstair" not in a["main"]["W"], a["main"]

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

    def test_a_door_across_OPEN_GROUND_still_does_not_place_and_should_not(self):
        """The control, and it is what keeps this a fix rather than a loosening. `butlers` and
        `kitchen` are doored to each other across 14 ft of yard with no link: a detached
        dependency IS detached, and drawing that door would be the lie."""
        p = _hyphen_fixture()
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        cross = _cross_doors(p)
        assert cross[("butlers", "kitchen")] is True, cross
        assert cross[("backhall", "kitchen")] is True, cross

    def test_without_a_hyphen_room_EVERY_cross_element_door_is_refused(self):
        """The before. Four of four, on the fixture the whole package has used."""
        p = _hyphen_fixture(with_hyphen=False)
        GEO._SOLVE_CACHE.clear()
        GEO.solve(p, engine="heuristic")
        cross = _cross_doors(p)
        assert cross and all(cross.values()), cross

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
        assert GEO.hyphen_anchors(plan, beside, 0)["A"] == {"E": ["a"]}
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
        for name, score, w in (("tidewater-georgian-careful", 775.2, 63),
                               ("spec-builder-colonial", 830.1, 50.0)):
            GEO._SOLVE_CACHE.clear()
            q = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
            _, prep = GEO.prep_rooms(q)
            fp = GEO.derive_footprint(q, None, prep)
            assert GEO.hyphen_anchors(q, GEO.blocks_for(q, fp, prep, 0), 0) == {}, name
            GEO.solve(q, engine="heuristic")
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
        p = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
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
        p = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
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
    p = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
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
            for key, b in boxes.items():
                assert b == main, (os.path.basename(f), key, b, main)
            seen += 1
        assert seen >= 14, seen

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
        p = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
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
        soft half of the model was unexercised on a multi-element plan."""
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
        p = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        levels, prep, fpd = _prepped(p)
        boxes, main = CP._boxes(p, prep, fpd)
        fills = CP._element_fills(boxes, prep[0], 0)
        assert list(fills) == [main], fills
        assert abs(fills[main]
                   - (fpd["W"] * fpd["H"]) / sum(r["_area"] for r in prep[0])) < 1e-9
