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
    def test_it_names_ONE_layer_and_the_five_taught_are_not_among_them(self, placed):
        """The ruling's own check. Five layers were taught at WP-11.6 and left the list; the one
        that remains is named because it still reads the main block as the whole building."""
        me = placed["geometry_report"]["multi_element"]
        assert me["elements"] == 2
        assert me["not_element_aware"] == ["export_ifc"]
        for taught in ("openings", "structure", "vertical_score", "lot_cap",
                       "plan_check.drawn"):
            assert taught not in me["not_element_aware"], taught

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

    def test_the_refusals_that_remain_are_HONEST(self, placed):
        """9 of 14 dependency openings were refused before and 5 after, and the difference has
        to be a real one. The kitchen's north edge is 23.72 against its element's 29.12: it does
        not reach that face and the refusal is correct."""
        deps = dep_rooms(placed)
        kitchen = next(r for lv in placed["levels"] for r in lv["rooms"] if r["id"] == "kitchen")
        by_wall = {w["wall"]: w for w in kitchen["windows"]}
        assert not by_wall["S"].get("unplaced"), "the kitchen IS on its element's south face"
        assert by_wall["N"].get("unplaced"), "and is NOT on its north face"
        g = kitchen["geometry"]
        el = next(b for b in placed["footprint"]["blocks"] if b["id"] != "main")
        assert g["y_ft"] + g["depth_ft"] < el["y_ft"] + el["depth_ft"] - 1.0, (
            "the refusal must rest on the geometry, not on a coincidence")

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
        assert over, "the dependency's structure is unmodelled again"
        assert max(s["span_ft"] for s in over) > 20.0

    def test_a_one_element_plan_carries_no_element_tag_at_all(self):
        """The byte-identity guard. Sixteen records have never needed one and must not grow one."""
        sec = ST.build_section(json.load(open(os.path.join(
            ROOT, "plans", "tidewater-georgian-careful.json"))))
        assert all("element" not in w for lv in sec["levels"] for w in lv["walls"])
        assert all("element" not in s for lv in sec["levels"] for s in lv["spans"])
        # and the numbers this plan has always reported
        over = [s for lv in sec["levels"] for s in lv["spans_exceeding_capacity"]]
        assert round(max(s["span_ft"] for s in over), 2) == 53.94


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
        """The control, and without it this is a loosening rather than a fix. `chamber2` and
        `stair` read `[]` against the main block AND against their own element -- they really are
        in the middle of the house -- so they must keep the finding the dependency rooms lost."""
        c = PC.check(_forced(placed))
        still = {f["room"] for f in c["findings"] if f.get("kind") == "drawn-landlocked"}
        assert {"chamber2", "stair"} <= still, still

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
        assert by["kitchen"] == ["S", "W"] and by["breakfast"] == ["E", "S"], by

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
        kind, room and statement. Measured identical on both shipped plans before and after."""
        import hashlib
        for name, want in (("tidewater-georgian-careful", "4ec3f784caa5a095"),
                           ("spec-builder-colonial", "433325b5299ea477")):
            GEO._SOLVE_CACHE.clear()
            q = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
            GEO.solve(q, engine="heuristic")
            c = PC.check(q)
            got = hashlib.sha256(json.dumps(
                sorted((f.get("kind", ""), f.get("room", ""), f.get("statement", ""))
                       for f in c["findings"]), sort_keys=True).encode()).hexdigest()[:16]
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
        for name, score, width, capped in (
                ("tidewater-georgian-careful", 685.3, 63, False),
                ("spec-builder-colonial", 592.3, 50.0, True)):
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
        three elements, 118 ft of building -- and `built_extent - main == flank` exactly."""
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
        assert round(hi - lo, 2) == L["built_extent_ft"] == 118.0, (hi - lo, L)
        assert round(L["built_extent_ft"] - L["main_block_ft"], 2) == L["flanking_ft"] == 55.0, L
