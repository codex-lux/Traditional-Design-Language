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
        Both levels are solved and scored TOGETHER (decision #11) — this is
        what 'vertical_score' being present and nonzero-capable proves; an
        upper floor solved independently could not know about walls below."""
        import json
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plan = json.load(open(os.path.join(root, "plans", "tidewater-georgian-careful.json")))
        result = geometry_module.solve(plan)
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
