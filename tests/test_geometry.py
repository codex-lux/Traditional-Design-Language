"""Pins the geometry solver's spanning rule — see docs/geometry.md: 'a room
with exterior walls on OPPOSITE sides has to run the full depth or width...
which is exactly what a centre passage is, and why slicing it like any other
room produces a treemap instead of a plan.' Only circulation rooms span —
a porch with three exterior walls wants the south edge, not a slab through
the middle of the house.
"""
import pytest


class TestSpanningRule:
    def test_circulation_room_with_opposite_exterior_walls_spans(self, geometry_module):
        room = {"id": "cp", "type": "centre-passage", "exterior_walls": ["S", "N"]}
        result = geometry_module.spanning([room], "y")
        assert result is not None
        assert result["id"] == "cp"

    def test_circulation_room_with_one_exterior_wall_does_not_span(self, geometry_module):
        room = {"id": "cp", "type": "centre-passage", "exterior_walls": ["S"]}
        assert geometry_module.spanning([room], "y") is None

    def test_non_circulation_room_with_opposite_walls_does_not_span(self, geometry_module):
        """A porch is not circulation — even with walls on both opposite
        sides it must not become a slab through the house."""
        room = {"id": "porch", "type": "entry-porch", "exterior_walls": ["S", "N", "E"]}
        assert geometry_module.spanning([room], "y") is None

    def test_spans_on_x_axis_for_east_west_walls(self, geometry_module):
        room = {"id": "cp", "type": "centre-passage", "exterior_walls": ["E", "W"]}
        assert geometry_module.spanning([room], "x") is not None
        assert geometry_module.spanning([room], "y") is None


class TestSolveSmoke:
    """A minimal end-to-end check that solve() still runs on the shipped,
    carefully-composed Tidewater plan and returns dimensioned, placed rooms
    with every relaxation off the bay grid counted rather than silently
    absorbed — decision not to undo #11."""

    def test_solve_places_every_room_and_counts_relaxations(self, geometry_module):
        """Pins the current relaxation count (11, as of 23 Aug 2026 — the
        state-of-project review's narrative number of 10 had already drifted
        by one; this test protects the number that's actually live, and a
        deliberate change to the solver should update it in the same commit).
        WP-2.3 was that deliberate change: solve() now dispatches to the
        CP-SAT engine by default, so the 11 is pinned against the HEURISTIC
        engine explicitly — it is the slicer's own number, and the heuristic
        remains the labelled fallback and cross-check. tests/test_solver.py
        covers the CP engine's own properties.
        Both levels are solved and scored TOGETHER (decision #11) — this is
        what 'vertical_score' being present and nonzero-capable proves; an
        upper floor solved independently could not know about walls below."""
        import json
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plan = json.load(open(os.path.join(root, "plans", "tidewater-georgian-careful.json")))
        result = geometry_module.solve(plan, engine="heuristic")
        report = result["geometry_report"]
        # 7, moved from 9 by WP-7.4. The span term charges an over-capacity clear span, and the only way the slicer can create a bearing line is to cut ON the bay module -- so a term aimed at structure pulls cuts onto the grid, and a cut on the grid is not a relaxation. Measured on this plan with the two terms off and on: 9 -> 7 here and 7 -> 4 on spec-builder-colonial. It is an improvement and it is still a number that must not move BY ACCIDENT. Previously: 9, moved from 11 by WP-7.1 (OQ 95). The upper level is now sliced against the ground layout instead of blind, so an upper cut lands on a wall below where one is within tolerance — and a cut that lands on a wall below is not a compromise, because a relaxation is defined in geometry.py's own prose as a joist run that does not land on a bearing wall. The code had approximated that as 'misses the bay module', and 18 of 30 ground wall lines are themselves off the bay grid. Measured corpus-wide on 14 composed plans: relaxations 96 -> 76, transfer beams 166 -> 109.
        # STAYS 7. WP-9.4 measured a corrected clamp (geometry._clamp_cut) that would move it
        # to 8, and REFUSED it: the same change takes the entry porch's clear depth 6.0 -> 5.0
        # and re-fires `porch-nobody-can-sit-on`, which WP-7.4 had cleared. Read _clamp_cut's
        # docstring before trying it again -- the arithmetic there is right and the shipped
        # expression is wrong, and shipping the fix alone still makes the corpus worse.
        assert report["relaxations"]["count"] == 7
        assert "vertical_score" in report, "both levels must be scored together, not independently"
        placed_rooms = [
            r for lv in result["levels"] for r in lv["rooms"]
        ]
        unplaced = [r for r in placed_rooms if "geometry" not in r]
        # Outdoor rooms (a terrace, a porch modelled as open-air) are outside
        # the indoor bay-grid solve by design — is_indoor() filters them out.
        # Every INDOOR room must come back placed.
        unplaced_indoor = [r for r in unplaced if r["type"] != "terrace"]
        assert not unplaced_indoor, f"indoor rooms with no placed geometry: {unplaced_indoor}"
        assert len(placed_rooms) - len(unplaced) > 20, "expected the bulk of the plan to be placed"


class TestUnderBandIsReported:
    """OQ 54, ruled 24 Aug 2026. The search may trade a room's size against everything else it
    scores — that is what a heuristic is for — but the plan record still carries the room's
    DECLARED size and nothing downstream reads these coordinates, so the trade was invisible."""

    def test_the_spec_colonials_squeezed_dining_room_is_named(self, geometry_module):
        """The finding OQ 54 was raised about: 90 sf against a 122 sf band floor, on every seed,
        while the plan record still says 12 x 12."""
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plan = json.load(open(os.path.join(root, "plans", "spec-builder-colonial.json")))

        # engine="heuristic" EXPLICITLY. OQ 54 is a finding about the hill-climb: it charges a
        # flat 12 points for a room under its band and a candidate can win while paying it.
        # `solve()` defaults to CP-SAT since the 25 Aug merge, and the CP engine places this
        # dining room in band — so calling the default here stopped testing the thing the
        # question is about and started testing an engine that does not have the defect.
        out = geometry_module.solve(json.loads(json.dumps(plan)), engine="heuristic")
        ub = out["geometry_report"]["under_band"]
        # WP-7.4: THE DINING ROOM IS IN BAND NOW AND THE STAIR HALL IS NOT, so this asserts the
        # MECHANISM rather than the room. Measured on this plan with the two score terms off and
        # on: under_band 2 (entrance-hall, dining-room) -> 1 (stair-hall). OQ 54's own worked
        # example came right as a side effect of charging spans and stacks, which is worth
        # knowing and is not what this test exists to protect. What it protects is that the
        # hill-climb WILL trade a room below its own catalogue floor, and that the trade is
        # visible: named, measured against the floor it missed, and set beside the size the
        # record still declares. Naming a specific room pinned an accident.
        assert ub["count"] >= 1, (
            "the hill-climb reported no under-band room at all — investigate before "
            "celebrating; this engine has made that trade on this plan since OQ 54 was raised")
        for r in ub["rooms"]:
            assert r.get("type") and r.get("name"), r
            assert r["placed_sf"] < r["band_floor_sf"], r
            # the divergence OQ 54 is actually about: the record still says something else
            assert r.get("declared_sf"), r
            assert r.get("short_by_pct") and r.get("declared_short_by_pct") is not None, r
        # WP-7.4: the dining room is no longer the one squeezed on this plan, so asserting on
        # it by name would pin an outcome the terms just changed. What still holds is that the
        # room the hill-climb DOES squeeze is squeezed materially, not by a rounding.
        worst = max(ub["rooms"], key=lambda r: r["short_by_pct"])
        assert worst["short_by_pct"] >= 20, worst

        # And the good news, pinned so it cannot regress unnoticed: the CP engine does NOT make
        # this trade on the same record. That is the concrete difference between scoring a
        # room's minimum and enforcing it, on the plan the question was raised about.
        # THIS ASSERTION IS OUTSIDE THE CP GATE ON PURPOSE. An audit found it nested inside
        # `if solver.engine == "cp-sat"`, which meant that with no ortools, on a slower box, or
        # on a CP timeout, the whole test degraded to a shape check that could not detect the
        # WP-7.4 revert at all -- and the sibling test's own docstring records that CP on this
        # plan is wall-clock nondeterministic. It runs on the HEURISTIC result already computed
        # above, which is deterministic, and it is the one assertion here that fails on revert:
        # with the score terms off this plan's under-band set is {entrance-hall, dining-room}.
        assert "dining-room" not in {r["type"] for r in ub["rooms"]}, (
            "the dining room is under band again on the hill-climb; WP-7.4's score terms put "
            "it in band (under_band 2 -> 1, the stair hall taking its place) and something "
            "has undone that")
        # The CP half stays gated, because it genuinely cannot be evaluated without a solve --
        # and it reports COULD NOT EVALUATE rather than passing when the engine did not run.
        cp = geometry_module.solve(json.loads(json.dumps(plan)), engine="auto")
        cp_engine = (cp.get("geometry_report", {}).get("solver") or {}).get("engine")
        if cp_engine == "cp-sat":
            cp_names = {r["type"] for r in cp["geometry_report"]["under_band"]["rooms"]}
            assert "dining-room" not in cp_names, (
                "the CP engine used to place this room in band; if it no longer does, the "
                "room minimum has stopped being enforced")
        else:
            pytest.skip(f"CP did not run (engine={cp_engine!r}) — the CP half is unjudged here, "
                        f"not passed; the heuristic half above still ran")

    def test_a_layout_with_nothing_under_band_says_so_rather_than_going_quiet(self, geometry_module):
        rects = {0: {"a": (0.0, 0.0, 20.0, 20.0)}}
        prep = {0: [{"id": "a", "type": "parlor", "name": "Parlor"}]}
        assert geometry_module.under_band(rects, prep) == []
