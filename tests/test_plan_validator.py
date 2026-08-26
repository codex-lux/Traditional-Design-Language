"""Pins the plan validator's behaviour — see docs/plans.md.

Live counts as of 23 Aug 2026 (verified by running plan_check.py directly, not
copied from docs/plans.md's table, which had itself drifted by one 'serious'
finding on each shipped plan — 54 vs the actual 49 on Spec Builder Colonial,
19 vs the actual 18 on the careful Tidewater plan. If one of the exact counts
below needs to change because a rule legitimately changed, update docs/plans.md
in the same commit — that table drifting silently is exactly the failure mode
this suite exists to catch.

RE-PINNED for WP-3.2 (the elevation generator, docs/reports/wp-3.2-elevation-generator.md): build/plan_check.py's
new ELEVATION LAYER folds build/elevation.py's own bay/window/cornice/roof measurements into
every check() call for a style within its scope (both shipped plans qualify -- colonial-revival
and tidewater-georgian are both in opening-proportion.json's and facade-classical.json's own
applies_to lists). That is a large amount of previously could_not_judge coverage becoming
evaluable for the first time, which is why serious/minor rose sharply on both plans, and why Spec
Builder Colonial picked up a fourth, genuine fatal: it declares window_opening_width_in (36 in)
but never declared a height, so window-squarer-than-the-style-permits could not evaluate before
-- the elevation layer now supplies a real generated height (setdefault, the plan's own width
still wins), and the resulting ratio (1.693) is honestly below the style's own 1.85 floor. Not a
new bug planted by this WP; an old one this WP made visible for the first time.
"""
from conftest import load_plan, minimal_plan


class TestShippedPlans:
    def test_spec_builder_colonial_counts(self, plan_check_module, corpus):
        plan = load_plan("spec-builder-colonial")
        result = plan_check_module.check(plan, corpus)
        assert result["counts"]["fatal"] == 4
        assert result["counts"]["serious"] == 70
        # 59 -> 57 on 24 Aug 2026 (OQ 59): centre-passage joined the entrance-hall EQUIVALENT
        # group, so two rooms opening off the passage stopped being reported as wanting an
        # entrance hall the plan does not model. It models one; it calls it a passage. Fatal
        # and serious are unmoved, which is what says this removed noise and not signal.
        # 57 -> 56 the same day (OQ 63): one more finding came from a secondary test written
        # for another style, and is no longer run against this one.
        # 56 -> 59 (OQ 43): substitution became directional, so a room the plan models under an
        # equivalent name now produces a real adjacency finding at the rule's own severity
        # instead of one minor "treats as equivalent" note. Fatal is unmoved at 4.
        assert result["counts"]["minor"] == 59

    def test_spec_builder_colonial_four_named_fatals(self, plan_check_module, corpus):
        """The three fatals docs/plans.md names (the powder-room door off the dining room, the
        primary bedroom over the garage, and the half-width shutter) plus a fourth WP-3.2 made
        newly evaluable: the plan's own declared window width (36 in, no declared height) against
        the elevation layer's own generated height -- ratio 1.693, below the style's 1.85 floor."""
        plan = load_plan("spec-builder-colonial")
        result = plan_check_module.check(plan, corpus)
        fatals = [f["statement"] for f in result["findings"] if f["severity"] == "fatal"]
        assert len(fatals) == 4
        assert any("Dining Room" in s and "Powder Room" in s for s in fatals)
        assert any("Garage" in s and "Primary Bedroom" in s for s in fatals)
        assert any("Half-Width Shutter" in s or "half-width" in s.lower() for s in fatals)
        assert any("Square Window" in s for s in fatals)

    def test_tidewater_georgian_careful_counts(self, plan_check_module, corpus):
        plan = load_plan("tidewater-georgian-careful")
        result = plan_check_module.check(plan, corpus)
        assert result["counts"].get("fatal", 0) == 0
        # 39 -> 38 on 24 Aug 2026 (OQ 63): a secondary test written for another style is no
        # longer run against this one. A test that is not for this house says nothing about it.
        # 38 -> 40 (OQ 43): two findings that were held at minor while substitution was
        # symmetric are now reported at the severity their own rule carries. Fatal stays 0.
        assert result["counts"]["serious"] == 40
        # 67 -> 64 on 24 Aug 2026, same cause as the spec Colonial above (OQ 59).
        # 64 -> 62 (OQ 43): two of the minors were the substitution running backwards -- a
        # general room offered where a specific one was asked for -- and are now reported as the
        # absence they are, or promoted to the severity their rule carries. Fatal stays 0.
        assert result["counts"]["minor"] == 62


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
            # RE-PINNED 24 Aug 2026 (OQ 59): this was a centre-passage, chosen as a room that
            # is emphatically not an entrance hall. It is one -- the front door opens into it
            # and every principal room opens off it -- and it joined plan_check's EQUIVALENT
            # group, so the fixture stopped testing what it was written to test. A back hall is
            # circulation and is genuinely not the entrance sequence, which is the property
            # these two tests actually need. The assertions are unchanged.
            {"id": "cp", "type": "back-hall", "name": "Back Hall",
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
            # RE-PINNED 24 Aug 2026 (OQ 59): this was a centre-passage, chosen as a room that
            # is emphatically not an entrance hall. It is one -- the front door opens into it
            # and every principal room opens off it -- and it joined plan_check's EQUIVALENT
            # group, so the fixture stopped testing what it was written to test. A back hall is
            # circulation and is genuinely not the entrance sequence, which is the property
            # these two tests actually need. The assertions are unchanged.
            {"id": "cp", "type": "back-hall", "name": "Back Hall",
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


class TestConstraintEvaluation:
    """WP-1.2: the STYLE LAYER now evaluates a migrated constraint's `test` object against
    plan.measurements (plus a small set of values derived from unambiguous plan structure,
    see plan_check.derive_constraint_vars) instead of only ever saying 'check by hand'.

    All exercised against georgian-colonial-american, whose 5 constraints (styles/
    georgian-colonial-american.json) are real WP-1.1 migration output: c01 bay_count
    one-of, c02 roof_pitch_rise_per_12 between 8-10 (hard), c03 no test (scope: judgment),
    c04 shutter_leaf_to_sash_ratio equals 0.5, c05 water_table_height_in between 24-36
    (soft) -- not synthetic fixtures.
    """

    def _plan(self, measurements=None):
        p = minimal_plan([])
        p["measurements"] = measurements or {}
        return p

    def test_constraint_summary_present_in_result(self, plan_check_module, corpus):
        result = plan_check_module.check(self._plan(), corpus)
        assert "constraint_summary" in result
        assert set(result["constraint_summary"]) == {"present", "clear", "unjudged"}

    def test_no_measurements_leaves_testable_constraints_unjudged(self, plan_check_module, corpus):
        result = plan_check_module.check(self._plan(), corpus)
        # c01, c02, c04, c05 all have a test and none of their variables are derivable from an
        # empty room list -- 'unjudged is not passed' means none of these may show as clear.
        assert result["constraint_summary"]["unjudged"] == 4
        assert result["constraint_summary"]["clear"] == 0
        assert result["constraint_summary"]["present"] == 0
        unjudged_msgs = [f["statement"] for f in result["findings"]
                          if f["layer"] == "style" and f["statement"].startswith("Cannot evaluate")]
        assert len(unjudged_msgs) == 4

    def test_hard_constraint_without_test_still_gets_check_by_hand(self, plan_check_module, corpus):
        """c03 (scope: judgment) has no test object at all -- pre-WP-1.2 behaviour for this
        case must be unchanged."""
        result = plan_check_module.check(self._plan(), corpus)
        hits = [f for f in result["findings"] if f.get("rule") == "georgian-colonial-american.c03"]
        assert len(hits) == 1
        assert hits[0]["severity"] == "info"
        assert hits[0]["statement"].startswith("Check by hand:")

    def test_hard_constraint_passes_within_range(self, plan_check_module, corpus):
        result = plan_check_module.check(self._plan({"roof_pitch_rise_per_12": 9}), corpus)
        hits = [f for f in result["findings"] if f.get("rule") == "georgian-colonial-american.c02"]
        assert hits == [], f"9:12 is within c02's 8-10 band and should clear silently, got: {hits}"
        assert result["constraint_summary"]["clear"] >= 1

    def test_hard_constraint_fails_outside_range_as_serious(self, plan_check_module, corpus):
        result = plan_check_module.check(self._plan({"roof_pitch_rise_per_12": 6}), corpus)
        hits = [f for f in result["findings"] if f.get("rule") == "georgian-colonial-american.c02"]
        assert len(hits) == 1
        assert hits[0]["severity"] == "serious"
        assert "8 and 10" in hits[0]["statement"] or "between 8" in hits[0]["statement"]
        assert result["constraint_summary"]["present"] >= 1

    def test_soft_constraint_maps_to_minor_not_serious(self, plan_check_module, corpus):
        """c05 is severity: soft. CONSTRAINT_SEV maps soft -> minor, distinct from the hard ->
        serious mapping c02 exercises above."""
        result = plan_check_module.check(self._plan({"water_table_height_in": 40}), corpus)
        hits = [f for f in result["findings"] if f.get("rule") == "georgian-colonial-american.c05"]
        assert len(hits) == 1
        assert hits[0]["severity"] == "minor"

    def test_one_of_constraint_evaluates(self, plan_check_module, corpus):
        result = plan_check_module.check(self._plan({"bay_count": 4}), corpus)
        hits = [f for f in result["findings"] if f.get("rule") == "georgian-colonial-american.c01"]
        assert len(hits) == 1 and hits[0]["severity"] == "serious"
        result_ok = plan_check_module.check(self._plan({"bay_count": 5}), corpus)
        assert not [f for f in result_ok["findings"] if f.get("rule") == "georgian-colonial-american.c01"]

    def test_centre_passage_width_is_derived_from_plan_structure(self, plan_check_module, corpus):
        """tidewater-georgian.c03 needs centre_passage_width_ft, which derive_constraint_vars
        reads directly off a ground-floor room of type centre-passage -- no plan.measurements
        entry required, unlike every other case in this class."""
        plan = load_plan("tidewater-georgian-careful")
        result = plan_check_module.check(plan, corpus)
        hits = [f for f in result["findings"] if f.get("rule") == "tidewater-georgian.c03"]
        assert hits == [], f"the shipped plan's 12ft passage is within c03's 10-14ft band: {hits}"
        assert result["constraint_summary"]["clear"] >= 1

    def test_deliberately_wrong_tidewater_pitch_fails_as_wp_1_2_acceptance_names_it(self, plan_check_module, corpus):
        """PLAN-OF-ACTION.md's own WP-1.2 acceptance criterion, verbatim: 'a deliberately wrong
        variant (pitch 12:12 on Tidewater) fails the pitch constraint.'"""
        plan = load_plan("tidewater-georgian-careful")
        plan["measurements"] = {"roof_pitch_rise_per_12": 12}
        result = plan_check_module.check(plan, corpus)
        hits = [f for f in result["findings"] if f.get("rule") == "tidewater-georgian.c02"]
        assert len(hits) == 1 and hits[0]["severity"] == "serious"

    def test_compose_score_already_counts_a_failed_hard_constraint(self, plan_check_module, corpus, compose_module):
        """PLAN-OF-ACTION.md asks WP-1.2 to 'teach compose.py to score constraint findings
        (fatal on a hard constraint present, the same 100/8/1 weights)'. compose.score() sums
        SEV_W over plan_check.check()'s own findings list with no constraint-specific code at
        all -- so a failed hard constraint (CONSTRAINT_SEV maps hard -> serious, SEV_W['serious']
        == 8) already moves the score the moment plan_check.py evaluates it. Nothing to add."""
        plan = {"id": "t", "name": "T", "style": "georgian-colonial-american",
                "massing": "centre-passage-single-pile", "groupings": [], "context": {},
                "levels": [{"id": "ground", "index": 0, "floor_to_ceiling_ft": 9, "rooms": []}],
                "adjacencies": [], "declared": {}}
        plan["measurements"] = {"roof_pitch_rise_per_12": 6}
        bad = compose_module.score(plan_check_module.check(plan, corpus))
        plan["measurements"] = {"roof_pitch_rise_per_12": 9}
        ok = compose_module.score(plan_check_module.check(plan, corpus))
        assert bad - ok == 8, "the failed roof-pitch constraint should cost exactly SEV_W['serious']"

    def test_derive_constraint_vars_ground_floor_only(self, plan_check_module):
        plan = load_plan("tidewater-georgian-careful")
        v = plan_check_module.derive_constraint_vars(plan)
        assert v["storey_count"] == 2
        assert v["centre_passage_width_ft"] == 12
        assert v["room_count_ground_floor"] == 14
        assert v["ceiling_height_ground_in"] == 132  # 11 ft ground-floor ceiling


class TestVerticalAdjacency:
    """OQ 57, ruled 24 Aug 2026. Adjacency was evaluated within a level only, which made two real
    arrangements unstateable and forced two workarounds that this change removes."""

    def _two_level(self, plan_check_module, upper_type, lower_type, relation_room):
        return {
            "id": "t", "name": "t", "style": "tudor", "massing": "h-plan-manor",
            "groupings": [], "context": {}, "adjacencies": [], "declared": {},
            "levels": [
                {"id": "ground", "index": 0, "floor_to_ceiling_ft": 10, "rooms": [
                    {"id": "low", "type": lower_type, "name": "Lower", "width_ft": 16,
                     "length_ft": 20, "doors": []}]},
                {"id": "upper", "index": 1, "floor_to_ceiling_ft": 9, "rooms": [
                    {"id": "up", "type": upper_type, "name": "Upper", "width_ft": 6,
                     "length_ft": 20, "doors": []}]},
            ]}

    def test_an_overlook_is_satisfied_by_the_hall_on_the_storey_below(self, plan_check_module, corpus):
        """The rule could never pass before: an overlook's defining relationship is that it is
        open to a double-height room BENEATH it, and adjacency did not span levels. It was held
        at 'preferred' with an apology on it so a right answer was not reported as a defect."""
        plan = self._two_level(plan_check_module, "overlook", "hall", "hall")
        res = plan_check_module.check(plan, corpus)
        assert not [f for f in res["findings"]
                    if "open to a hall" in f["statement"] and f["room"] == "up"]

    def test_an_overlook_with_nothing_below_it_is_reported(self, plan_check_module, corpus):
        plan = self._two_level(plan_check_module, "overlook", "bedroom", "hall")
        res = plan_check_module.check(plan, corpus)
        assert [f for f in res["findings"]
                if "storey below" in f["statement"] and f["room"] == "up"]

    def test_a_great_chamber_over_the_parlour_no_longer_trips_a_fatal(self, plan_check_module, corpus):
        """drawing-room's hard must_adjoin dining-room is a GROUND-FLOOR rule, and the great
        chamber of a Tudor house is a drawing room on the first floor whose dining room is a
        storey down. It used to be typed `library` purely to dodge this."""
        plan = self._two_level(plan_check_module, "drawing-room", "dining-room", "dining-room")
        res = plan_check_module.check(plan, corpus)
        assert not [f for f in res["findings"]
                    if f["severity"] == "fatal" and f["room"] == "up"
                    and "dining room" in f["statement"]]

    def test_the_h_plan_parti_types_its_great_chamber_as_what_it_is(self):
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        p = json.load(open(os.path.join(root, "partis", "great-hall-h-plan.json")))
        gc = next(r for r in p["rooms"] if r["id"] == "greatchamber")
        assert gc["type"] == "drawing-room", "the library workaround should be gone"


class TestTheAliasGroupsAreDocumented:
    """OQ 26, ruled 24 Aug 2026. The substitution table is validator data in the same sense a
    fault is — it changes results, and WP-0.3 found a fixture passing for the wrong reason
    through it — but it existed only as an unexplained list in the source. It is documented in
    docs/plans.md now, and this pins the documentation to the code so the table cannot quietly
    go stale. Renamed from EQUIVALENT to SUBSTITUTES by OQ 43, when it stopped being a set of
    flat groups and became a directed map."""

    def test_every_room_in_the_substitution_table_appears_in_the_docs(self, plan_check_module):
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        doc = open(os.path.join(root, "docs", "plans.md")).read()
        assert "`SUBSTITUTES`" in doc, "docs/plans.md should describe the substitution table"
        for have, wants in plan_check_module.SUBSTITUTES.items():
            for room_type in {have} | set(wants):
                assert f"`{room_type}`" in doc, (
                    f"{room_type} is in plan_check.SUBSTITUTES but appears nowhere in "
                    f"docs/plans.md's table")

    def test_gallery_corridor_is_documented_as_an_entrance_hall_alias(self, plan_check_module):
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        doc = open(os.path.join(root, "docs", "plans.md")).read()
        assert "gallery-corridor" in doc and "entrance hall" in doc.lower()


class TestEquivalentRoomIsNotAbsent:
    """OQ 42 then OQ 43. OQ 42 corrected the SENTENCE and held the severity, because a symmetric
    substitution table would have turned 170 of these fatal across 87 styles. OQ 43 gave each
    pairing a direction, which is what made promoting them safe: of 542 such findings, 294 were
    the substitution running backwards -- a general room offered where a specific one was asked
    for -- and those return to honest absence. The 214 that remain are real, and they now land
    at the severity their own rule carries."""

    def test_an_equivalent_room_the_plan_models_is_reported_as_not_reached(self, plan_check_module, corpus):
        rooms = [
            {"id": "pr", "type": "powder-room", "name": "Powder Room",
             "width_ft": 4, "length_ft": 6, "exterior_walls": [], "windows": [],
             "doors": [{"to": "bh", "width_ft": 2.5}]},
            {"id": "bh", "type": "back-hall", "name": "Back Hall",
             "width_ft": 6, "length_ft": 12, "exterior_walls": [], "windows": [],
             "doors": [{"to": "pr", "width_ft": 2.5}]},
            {"id": "cp", "type": "centre-passage", "name": "Centre Passage",
             "width_ft": 10, "length_ft": 20, "exterior_walls": ["S"],
             "windows": [{"wall": "S", "width_ft": 3, "height_ft": 5, "count": 1}],
             "doors": [{"to": "exterior", "width_ft": 3.5}]},
        ]
        hits = [f for f in plan_check_module.check(minimal_plan(rooms), corpus)["findings"]
                if f.get("room") == "pr" and "entrance hall" in f["statement"].lower()]
        assert len(hits) == 1
        assert "the plan models none" not in hits[0]["statement"], hits[0]["statement"]
        assert hits[0]["layer"] == "adjacency"
        assert "models it as centre passage" in hits[0]["statement"], hits[0]["statement"]

    def test_the_substitution_running_backwards_is_absence_again(self, plan_check_module, corpus):
        """The half of OQ 43 that REMOVES findings. A plan with a plain bathroom does not model a
        primary bathroom, and telling a primary bedroom it fails to reach one it has is worse
        than telling it none is modelled."""
        rooms = [
            {"id": "pb", "type": "primary-bedroom", "name": "Primary Bedroom",
             "width_ft": 14, "length_ft": 16, "exterior_walls": ["N"],
             "windows": [{"wall": "N", "width_ft": 3, "height_ft": 5, "count": 2}],
             "doors": [{"to": "lg", "width_ft": 3}]},
            {"id": "ba", "type": "bathroom", "name": "Hall Bath",
             "width_ft": 6, "length_ft": 9, "exterior_walls": [], "windows": [],
             "doors": [{"to": "lg", "width_ft": 2.5}]},
            {"id": "lg", "type": "landing", "name": "Landing",
             "width_ft": 6, "length_ft": 10, "exterior_walls": [], "windows": [],
             "doors": [{"to": "pb", "width_ft": 3}, {"to": "ba", "width_ft": 2.5}]},
        ]
        hits = [f for f in plan_check_module.check(minimal_plan(rooms), corpus)["findings"]
                if f.get("room") == "pb" and "primary bathroom" in f["statement"].lower()]
        assert hits, "the rule should still fire"
        assert "the plan models none" in hits[0]["statement"], hits[0]["statement"]
        assert hits[0]["layer"] == "completeness"

    def test_substitution_runs_one_way_and_the_table_says_which(self, plan_check_module):
        m = plan_check_module
        assert m.satisfies("primary-bathroom", "bathroom")
        assert not m.satisfies("bathroom", "primary-bathroom")
        assert m.satisfies("walk-in-closet", "closet")
        assert not m.satisfies("closet", "walk-in-closet")
        # and the entrance-hall family is mutual on purpose, because whichever of them a plan
        # calls its entry, the front door opens into it
        assert m.satisfies("centre-passage", "entrance-hall")
        assert m.satisfies("entrance-hall", "centre-passage")

    def test_a_room_cannot_satisfy_its_own_rule_through_its_own_alias_group(self, plan_check_module, corpus):
        """Without this the kitchen's rule to adjoin a scullery was answered by the kitchen
        being a kitchen -- true of the alias group, nonsense as a statement about the plan."""
        rooms = [
            {"id": "k", "type": "kitchen", "name": "Kitchen",
             "width_ft": 12, "length_ft": 14, "exterior_walls": ["N"],
             "windows": [{"wall": "N", "width_ft": 3, "height_ft": 4, "count": 1}],
             "doors": [{"to": "exterior", "width_ft": 3}]},
        ]
        hits = [f for f in plan_check_module.check(minimal_plan(rooms), corpus)["findings"]
                if f.get("room") == "k" and "scullery" in f["statement"].lower()]
        if hits:
            assert "the plan models none" in hits[0]["statement"], hits[0]["statement"]

    def test_a_genuinely_absent_room_still_says_so(self, plan_check_module, corpus):
        rooms = [
            {"id": "pr", "type": "powder-room", "name": "Powder Room",
             "width_ft": 4, "length_ft": 6, "exterior_walls": [], "windows": [],
             "doors": [{"to": "bh", "width_ft": 2.5}]},
            {"id": "bh", "type": "back-hall", "name": "Back Hall",
             "width_ft": 6, "length_ft": 12, "exterior_walls": ["S"],
             "windows": [{"wall": "S", "width_ft": 3, "height_ft": 5, "count": 1}],
             "doors": [{"to": "pr", "width_ft": 2.5}, {"to": "exterior", "width_ft": 3.5}]},
        ]
        hit = next(f for f in plan_check_module.check(minimal_plan(rooms), corpus)["findings"]
                   if f.get("room") == "pr" and "entrance hall" in f["statement"].lower())
        assert "the plan models none" in hit["statement"]
