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
    def test_it_names_five_layers_and_openings_is_not_one_of_them(self, placed):
        """The ruling's own check. `openings` was taught at WP-11.6 and left the list; the five
        that remain are named because they still read the main block as the whole building."""
        me = placed["geometry_report"]["multi_element"]
        assert me["elements"] == 2
        assert me["not_element_aware"] == ["structure", "vertical_score", "lot_cap",
                                           "plan_check.drawn", "export_ifc"]
        assert "openings" not in me["not_element_aware"]

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
