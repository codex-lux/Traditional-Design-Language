"""Pins the geometry solver's spanning rule — see docs/geometry.md: 'a room
with exterior walls on OPPOSITE sides has to run the full depth or width...
which is exactly what a centre passage is, and why slicing it like any other
room produces a treemap instead of a plan.' Only circulation rooms span —
a porch with three exterior walls wants the south edge, not a slab through
the middle of the house.
"""


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
        assert report["relaxations"]["count"] == 11
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
        assert ub["count"] >= 1
        names = {r["type"] for r in ub["rooms"]}
        assert "dining-room" in names
        dining = next(r for r in ub["rooms"] if r["type"] == "dining-room")
        assert dining["placed_sf"] < dining["band_floor_sf"]
        assert dining["short_by_pct"] >= 20

        # And the good news, pinned so it cannot regress unnoticed: the CP engine does NOT make
        # this trade on the same record. That is the concrete difference between scoring a
        # room's minimum and enforcing it, on the plan the question was raised about.
        cp = geometry_module.solve(json.loads(json.dumps(plan)), engine="auto")
        if (cp.get("geometry_report", {}).get("solver") or {}).get("engine") == "cp-sat":
            cp_names = {r["type"] for r in cp["geometry_report"]["under_band"]["rooms"]}
            assert "dining-room" not in cp_names, (
                "the CP engine used to place this room in band; if it no longer does, the "
                "room minimum has stopped being enforced")

    def test_a_layout_with_nothing_under_band_says_so_rather_than_going_quiet(self, geometry_module):
        rects = {0: {"a": (0.0, 0.0, 20.0, 20.0)}}
        prep = {0: [{"id": "a", "type": "parlor", "name": "Parlor"}]}
        assert geometry_module.under_band(rects, prep) == []
