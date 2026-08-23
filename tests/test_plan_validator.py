"""Pins the plan validator's behaviour — see docs/plans.md.

Live counts as of 23 Aug 2026 (verified by running plan_check.py directly, not
copied from docs/plans.md's table, which had itself drifted by one 'serious'
finding on each shipped plan — 54 vs the actual 49 on Spec Builder Colonial,
19 vs the actual 18 on the careful Tidewater plan. If one of the exact counts
below needs to change because a rule legitimately changed, update docs/plans.md
in the same commit — that table drifting silently is exactly the failure mode
this suite exists to catch.
"""
from conftest import load_plan, minimal_plan


class TestShippedPlans:
    def test_spec_builder_colonial_counts(self, plan_check_module, corpus):
        plan = load_plan("spec-builder-colonial")
        result = plan_check_module.check(plan, corpus)
        assert result["counts"]["fatal"] == 3
        assert result["counts"]["serious"] == 49
        assert result["counts"]["minor"] == 51

    def test_spec_builder_colonial_three_named_fatals(self, plan_check_module, corpus):
        """The three fatals docs/plans.md names: the powder-room door off the
        dining room, the primary bedroom over the garage, and the half-width
        shutter."""
        plan = load_plan("spec-builder-colonial")
        result = plan_check_module.check(plan, corpus)
        fatals = [f["statement"] for f in result["findings"] if f["severity"] == "fatal"]
        assert len(fatals) == 3
        assert any("Dining Room" in s and "Powder Room" in s for s in fatals)
        assert any("Garage" in s and "Primary Bedroom" in s for s in fatals)
        assert any("Half-Width Shutter" in s or "half-width" in s.lower() for s in fatals)

    def test_tidewater_georgian_careful_counts(self, plan_check_module, corpus):
        plan = load_plan("tidewater-georgian-careful")
        result = plan_check_module.check(plan, corpus)
        assert result["counts"].get("fatal", 0) == 0
        assert result["counts"]["serious"] == 18
        assert result["counts"]["minor"] == 60


class TestAdjacencyMechanics:
    """The two subtleties docs/plans.md says 'earned their place by producing
    false positives on a correct plan': connection checked two hops through a
    hall, and circulation being rank-transparent."""

    def test_two_hop_through_circulation_satisfies_must_adjoin(self, plan_check_module, corpus):
        """powder-room's must_adjoin(entrance-hall, same-floor) is not a direct-door
        rule, so it is checked via types_near(), which reaches one hop further
        through a circulation room. A centre passage standing between the two
        satisfies it with no direct door."""
        rooms = [
            {"id": "pr", "type": "powder-room", "name": "Powder Room",
             "width_ft": 4, "length_ft": 6, "exterior_walls": [], "windows": [],
             "doors": [{"to": "cp", "width_ft": 2.5}]},
            {"id": "cp", "type": "centre-passage", "name": "Centre Passage",
             "width_ft": 10, "length_ft": 14, "exterior_walls": ["S"],
             "windows": [{"wall": "S", "width_ft": 3, "height_ft": 5, "count": 1}],
             "doors": [{"to": "pr", "width_ft": 2.5}, {"to": "eh", "width_ft": 3.5}]},
            {"id": "eh", "type": "entrance-hall", "name": "Entrance Hall",
             "width_ft": 10, "length_ft": 12, "exterior_walls": ["N"], "windows": [],
             "doors": [{"to": "cp", "width_ft": 3.5}, {"to": "exterior"}]},
        ]
        result = plan_check_module.check(minimal_plan(rooms), corpus)
        bad = [f for f in result["findings"]
               if f.get("room") == "pr" and "entrance hall" in f["statement"].lower()
               and f["layer"] in ("adjacency", "completeness")]
        assert bad == [], f"two-hop-through-circulation should satisfy the rule, got: {bad}"

    def test_room_present_but_unreachable_is_an_adjacency_defect(self, plan_check_module, corpus):
        """Contrast case for the above: the target room exists in the plan but
        is not within two hops, so this must be a genuine 'adjacency' failure —
        not silently passed, and not folded into 'completeness' (which is only
        for a room type the plan doesn't model at all)."""
        rooms = [
            {"id": "pr", "type": "powder-room", "name": "Powder Room",
             "width_ft": 4, "length_ft": 6, "exterior_walls": [], "windows": [],
             "doors": [{"to": "cp", "width_ft": 2.5}]},
            {"id": "cp", "type": "centre-passage", "name": "Centre Passage",
             "width_ft": 10, "length_ft": 14, "exterior_walls": ["S"],
             "windows": [{"wall": "S", "width_ft": 3, "height_ft": 5, "count": 1}],
             "doors": [{"to": "pr", "width_ft": 2.5}, {"to": "exterior", "width_ft": 3.5}]},
            {"id": "eh", "type": "entrance-hall", "name": "Entrance Hall (unreachable)",
             "width_ft": 10, "length_ft": 12, "exterior_walls": ["N"], "windows": [],
             "doors": [{"to": "exterior", "width_ft": 3.5}]},
        ]
        result = plan_check_module.check(minimal_plan(rooms), corpus)
        hit = [f for f in result["findings"]
               if f.get("room") == "pr" and "does not reach a entrance hall" in f["statement"].lower()]
        assert len(hit) == 1
        assert hit[0]["layer"] == "adjacency"
        assert hit[0]["severity"] == "serious"

    def test_absent_room_type_is_completeness_not_adjacency(self, plan_check_module, corpus):
        """A plan that simply doesn't model a room type ('absence is not
        failure', docs/plans.md) must not be scored the same as a plan that
        models the room and gets the connection wrong."""
        rooms = [
            {"id": "pr", "type": "powder-room", "name": "Powder Room",
             "width_ft": 4, "length_ft": 6, "exterior_walls": [], "windows": [],
             "doors": [{"to": "cp", "width_ft": 2.5}]},
            {"id": "cp", "type": "centre-passage", "name": "Centre Passage",
             "width_ft": 10, "length_ft": 14, "exterior_walls": ["S"],
             "windows": [{"wall": "S", "width_ft": 3, "height_ft": 5, "count": 1}],
             "doors": [{"to": "pr", "width_ft": 2.5}, {"to": "exterior", "width_ft": 3.5}]},
        ]
        result = plan_check_module.check(minimal_plan(rooms), corpus)
        hit = [f for f in result["findings"]
               if f.get("room") == "pr" and "entrance hall" in f["statement"].lower()]
        assert len(hit) == 1
        assert hit[0]["layer"] == "completeness"
        assert hit[0]["severity"] == "minor", "an absence must never outrank a genuine defect"

    def test_circulation_is_rank_transparent(self, plan_check_module, corpus):
        """entrance-hall (privacy rank 1, function_class threshold) directly
        door-connected to primary-bedroom (rank 5) must NOT trip the privacy
        gradient rule — a threshold/circulation room IS the buffer."""
        rooms = [
            {"id": "eh", "type": "entrance-hall", "name": "Entrance Hall",
             "width_ft": 8, "length_ft": 12, "exterior_walls": ["S"], "windows": [],
             "doors": [{"to": "pb", "width_ft": 3}, {"to": "exterior"}]},
            {"id": "pb", "type": "primary-bedroom", "name": "Primary Bedroom",
             "width_ft": 14, "length_ft": 16, "exterior_walls": ["N"],
             "windows": [{"wall": "N", "width_ft": 3, "height_ft": 5, "count": 2}],
             "doors": [{"to": "eh", "width_ft": 3}]},
        ]
        result = plan_check_module.check(minimal_plan(rooms), corpus)
        privacy_findings = [f for f in result["findings"] if f["layer"] == "privacy"]
        assert privacy_findings == []

    def test_non_circulation_direct_privacy_jump_is_flagged(self, plan_check_module, corpus):
        """Contrast case: dining-room (rank 2, non-circulation) direct-doored to
        primary-bedroom (rank 5) is a genuine 3-rank jump and must be flagged."""
        rooms = [
            {"id": "dr", "type": "dining-room", "name": "Dining Room",
             "width_ft": 14, "length_ft": 16, "exterior_walls": ["S"],
             "windows": [{"wall": "S", "width_ft": 3, "height_ft": 5, "count": 2}],
             "doors": [{"to": "pb", "width_ft": 3}]},
            {"id": "pb", "type": "primary-bedroom", "name": "Primary Bedroom",
             "width_ft": 14, "length_ft": 16, "exterior_walls": ["N"],
             "windows": [{"wall": "N", "width_ft": 3, "height_ft": 5, "count": 2}],
             "doors": [{"to": "dr", "width_ft": 3}]},
        ]
        result = plan_check_module.check(minimal_plan(rooms), corpus)
        privacy_findings = [f for f in result["findings"] if f["layer"] == "privacy"]
        assert len(privacy_findings) == 1
        assert "jumping 3 ranks" in privacy_findings[0]["statement"]

    def test_via_intermediary_satisfies_kitchen_dining_rule(self, plan_check_module, corpus):
        """The butler's pantry is not a failure to connect the kitchen to the
        dining room; it IS the connection — 'via' on the adjacency rule."""
        rooms = [
            {"id": "kit", "type": "kitchen", "name": "Kitchen", "width_ft": 14, "length_ft": 16,
             "exterior_walls": ["S"], "windows": [{"wall": "S", "width_ft": 3, "height_ft": 5, "count": 2}],
             "doors": [{"to": "bp", "width_ft": 3}]},
            {"id": "dr", "type": "dining-room", "name": "Dining Room", "width_ft": 14, "length_ft": 16,
             "exterior_walls": ["N"], "windows": [{"wall": "N", "width_ft": 3, "height_ft": 5, "count": 2}],
             "doors": [{"to": "bp", "width_ft": 3}]},
            {"id": "bp", "type": "butlers-pantry", "name": "Butlers Pantry", "width_ft": 6, "length_ft": 8,
             "exterior_walls": [], "windows": [],
             "doors": [{"to": "kit", "width_ft": 3}, {"to": "dr", "width_ft": 3}]},
        ]
        result = plan_check_module.check(minimal_plan(rooms), corpus)
        bad = [f for f in result["findings"]
               if f.get("room") == "kit" and "does not reach a dining room" in f["statement"].lower()]
        assert bad == []

    def test_no_via_intermediary_fails_kitchen_dining_rule(self, plan_check_module, corpus):
        """Contrast case: no butler's pantry, no direct door — the rule must fire."""
        rooms = [
            {"id": "kit", "type": "kitchen", "name": "Kitchen", "width_ft": 14, "length_ft": 16,
             "exterior_walls": ["S"], "windows": [{"wall": "S", "width_ft": 3, "height_ft": 5, "count": 2}],
             "doors": [{"to": "exterior", "width_ft": 3}]},
            {"id": "dr", "type": "dining-room", "name": "Dining Room", "width_ft": 14, "length_ft": 16,
             "exterior_walls": ["N"], "windows": [{"wall": "N", "width_ft": 3, "height_ft": 5, "count": 2}],
             "doors": [{"to": "exterior", "width_ft": 3}]},
        ]
        result = plan_check_module.check(minimal_plan(rooms), corpus)
        bad = [f for f in result["findings"]
               if f.get("room") == "kit" and "does not reach a dining room" in f["statement"].lower()]
        assert len(bad) == 1


class TestDaylight:
    """docs/plans.md: 'a room with glass on two opposite walls is lit from both
    ends and is only half as deep as it measures.' Without the correction, a
    correctly planned Georgian drawing room with windows on two walls fails
    its own rule."""

    def _room(self, two_ended):
        windows = [{"wall": "S", "width_ft": 4, "height_ft": 6, "count": 2}]
        if two_ended:
            windows.append({"wall": "N", "width_ft": 4, "height_ft": 6, "count": 2})
        return {
            "id": "dr", "type": "drawing-room", "name": "Drawing Room",
            "width_ft": 18, "length_ft": 30,
            "exterior_walls": ["S", "N"] if two_ended else ["S"],
            "window_head_ft": 9.33,
            "windows": windows,
            "doors": [{"to": "exterior", "width_ft": 3.5}],
        }

    def test_single_sided_deep_room_fails_its_own_daylight_rule(self, plan_check_module, corpus):
        result = plan_check_module.check(minimal_plan([self._room(two_ended=False)]), corpus)
        hits = [f for f in result["findings"] if f.get("room") == "dr" and f["layer"] == "daylight"]
        assert any("lit from one side" in f["statement"] for f in hits)

    def test_two_ended_room_is_halved_and_passes(self, plan_check_module, corpus):
        result = plan_check_module.check(minimal_plan([self._room(two_ended=True)]), corpus)
        hits = [f for f in result["findings"] if f.get("room") == "dr" and f["layer"] == "daylight"]
        assert hits == [], f"two-ended correction should clear the same room, got: {hits}"


class TestCompleteness:
    def test_completeness_findings_are_separated_from_defects(self, plan_check_module, corpus):
        plan = load_plan("spec-builder-colonial")
        result = plan_check_module.check(plan, corpus)
        completeness = [f for f in result["findings"] if f["layer"] == "completeness"]
        assert completeness, "expected at least one completeness finding on the spec-builder plan"
        assert all(f["severity"] == "minor" for f in completeness), \
            "completeness findings must never outrank a genuine defect by default (non-strict mode)"
