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
    def test_it_names_four_layers_and_the_two_taught_are_not_among_them(self, placed):
        """The ruling's own check. `openings` and `structure` were taught at WP-11.6 and left
        the list; the four that remain are named because they still read the main block as the
        whole building."""
        me = placed["geometry_report"]["multi_element"]
        assert me["elements"] == 2
        assert me["not_element_aware"] == ["vertical_score", "lot_cap",
                                           "plan_check.drawn", "export_ifc"]
        assert "openings" not in me["not_element_aware"]
        assert "structure" not in me["not_element_aware"]

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


class TestTheCriticIsNOTTaughtAndItsSYMPTOMWENTAWAYANYWAY:
    """THE FINDING OF THIS PACKAGE THAT A METER WOULD HAVE GOT WRONG.

    `plan_check`'s landlocked test short-circuits at `if seated: continue` -- it runs only on a
    room whose windows are ALL unplaced. Teaching `openings` seated the dependency's windows, so
    the count of "reaches no exterior wall" findings fell 2 -> 0 **while the `touches` arithmetic
    four lines below still read `fp_w`/`fp_h` and was still wrong**. A meter watching the finding
    would have reported layer 5 taught by accident. The probe drives the condition instead."""

    def test_the_symptom_is_absent_as_shipped(self, placed):
        c = PC.check(placed)
        assert not [f for f in c["findings"]
                    if "no exterior wall" in (f.get("statement") or "")
                    and f.get("room") in dep_rooms(placed)]

    def test_and_the_layer_is_STILL_WRONG_when_the_test_is_reached(self, placed):
        """Strip the placement from the dependency's windows and the test runs. It convicts a
        kitchen that sits on its own element's south and west faces."""
        deps = dep_rooms(placed)
        forced = json.loads(json.dumps(placed))
        for lv in forced["levels"]:
            for r in lv["rooms"]:
                if r["id"] in deps:
                    for w in (r.get("windows") or []):
                        w["unplaced"] = {"reason": "forced to reach the touches test"}
        c = PC.check(forced)
        convicted = {f["room"] for f in c["findings"]
                     if "no exterior wall" in (f.get("statement") or "") and f.get("room") in deps}
        assert convicted, (
            "the drawn layer stopped convicting dependency rooms -- if `touches` was taught to "
            "read the element, take `plan_check.drawn` out of the disclosure and delete this test")
        assert "plan_check.drawn" in placed["geometry_report"]["multi_element"][
            "not_element_aware"], "the disclosure must still name the layer this test convicts on"


PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
