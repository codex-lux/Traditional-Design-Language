"""Pins WP-2.4, the site layer -- see docs/site.md and PLAN-OF-ACTION.md's own acceptance
criterion: 'A brief with a 30 ft lot never receives a five-bay candidate; the Charleston piazza
constraint is evaluated; the render shows the lot.'

Each class below maps to one clause of that criterion, plus the mechanism it rests on
(schema, derive_constraint_vars, and the kit-slot consumption the brief separately asks for).
"""
import json
import os
import subprocess

import pytest

from conftest import ROOT, load_plan, minimal_plan

BRIEFS = os.path.join(ROOT, "briefs")


def _brief(name):
    with open(os.path.join(BRIEFS, f"{name}.json")) as f:
        return json.load(f)


class TestSiteSchema:
    """schema/plan.schema.json and schema/brief.schema.json both gained a `site` object
    (WP-2.4) additive to, not replacing, the pre-existing context.lot_width_ft/lot_depth_ft/
    entrance_faces -- see the `site` property's own description for why."""

    def test_plan_with_full_site_object_validates(self):
        plan = minimal_plan([{"id": "r1", "type": "living-room", "width_ft": 14, "length_ft": 16}])
        plan["site"] = {
            "street_bearing_deg": 158, "setback_front_ft": 25, "setback_side_ft": 5,
            "setback_rear_ft": 15, "slope_direction_deg": 90, "cross_slope_pct": 4.0,
            "prevailing_summer_wind_deg": 210, "piazza_bearing_deg": 225,
            "party_wall_condition": "freestanding", "note": "test",
        }
        proc = subprocess.run(
            ["python3", "-c",
             "import json, jsonschema\n"
             "schema = json.load(open('schema/plan.schema.json'))\n"
             "plan = json.load(open('/dev/stdin'))\n"
             "jsonschema.validate(plan, schema)\n"
             "print('OK')\n"],
            cwd=ROOT, input=json.dumps(plan), capture_output=True, text=True,
        )
        assert proc.returncode == 0 and proc.stdout.strip() == "OK", proc.stdout + proc.stderr

    def test_unknown_site_property_is_rejected(self):
        plan = minimal_plan([{"id": "r1", "type": "living-room", "width_ft": 14, "length_ft": 16}])
        plan["site"] = {"lot_width_ft": 40}  # belongs in context, not site -- see the description
        proc = subprocess.run(
            ["python3", "-c",
             "import json, jsonschema, sys\n"
             "schema = json.load(open('schema/plan.schema.json'))\n"
             "plan = json.load(open('/dev/stdin'))\n"
             "try:\n"
             "    jsonschema.validate(plan, schema)\n"
             "    print('VALID')\n"
             "except Exception:\n"
             "    print('REJECTED')\n"],
            cwd=ROOT, input=json.dumps(plan), capture_output=True, text=True,
        )
        assert proc.stdout.strip() == "REJECTED", proc.stdout + proc.stderr

    def test_brief_schema_also_has_a_site_object(self):
        schema = json.load(open(os.path.join(ROOT, "schema", "brief.schema.json")))
        assert "site" in schema["properties"]
        assert schema["properties"]["site"]["additionalProperties"] is False

    def test_party_wall_condition_enum_matches_plan_of_action_wording(self):
        """'freestanding / party wall / row' (PLAN-OF-ACTION.md, WP-2.4) -- the enum spells
        the middle case out as one-side/both-sides rather than collapsing it, which is a
        refinement, not a contradiction; pin that 'freestanding' and 'row' at least are
        exactly as named."""
        schema = json.load(open(os.path.join(ROOT, "schema", "plan.schema.json")))
        enum = schema["properties"]["site"]["properties"]["party_wall_condition"]["enum"]
        assert "freestanding" in enum and "row" in enum


class TestConstraintVocabularyAndDerivation:
    """build/constraint_vocabulary.py's site scope gained the fields WP-2.4's brief names that
    weren't already there (setback_side_ft, setback_rear_ft, slope_direction_deg,
    prevailing_summer_wind_deg); build/plan_check.py's derive_constraint_vars now reads all of
    `plan.site` straight through, the same unjudged-unless-stated discipline context already
    got in WP-1.2."""

    def test_new_site_vocabulary_entries_present(self, constraint_vocabulary_module):
        for name in ("setback_side_ft", "setback_rear_ft", "slope_direction_deg", "prevailing_summer_wind_deg"):
            assert name in constraint_vocabulary_module.VOCABULARY
            assert constraint_vocabulary_module.VOCABULARY[name]["scope"] == "site"

    def test_derive_constraint_vars_reads_plan_site(self, plan_check_module):
        plan = minimal_plan([{"id": "r1", "type": "living-room", "width_ft": 14, "length_ft": 16}])
        plan["site"] = {"piazza_bearing_deg": 210, "cross_slope_pct": 13.0}
        v = plan_check_module.derive_constraint_vars(plan)
        assert v["piazza_bearing_deg"] == 210
        assert v["cross_slope_pct"] == 13.0

    def test_site_note_field_is_not_smuggled_in_as_a_variable(self, plan_check_module):
        """`site.note` is free text, not a constraint variable -- it must not leak into the
        namespace a test.expression evaluates against."""
        plan = minimal_plan([{"id": "r1", "type": "living-room", "width_ft": 14, "length_ft": 16}])
        plan["site"] = {"note": "some prose", "cross_slope_pct": 5.0}
        v = plan_check_module.derive_constraint_vars(plan)
        assert "note" not in v


class TestSiteScopeConstraintsEvaluate:
    """The acceptance criterion's own example: 'the Charleston piazza constraint is evaluated.'
    charleston-georgian.c01 and pennsylvania-bank-house.c01 are the two site-scope constraints
    the corpus has actually migrated (WP-1.1) with a `test` -- both were unjudged before this
    package because nothing fed `context`/`site` data into the namespace derive_constraint_vars
    builds. Now they are judged, in both directions (present and clear)."""

    def test_charleston_piazza_bearing_clears_when_within_45_degrees_of_southwest(self, plan_check_module, corpus):
        plan = minimal_plan([{"id": "r1", "type": "living-room", "width_ft": 14, "length_ft": 16}],
                             style="charleston-georgian")
        plan["site"] = {"piazza_bearing_deg": 210}  # 15 degrees off 225 (SW) -- within the 45-degree band
        result = plan_check_module.check(plan, corpus)
        assert result["constraint_summary"]["clear"] >= 1
        ids = [f.get("rule") for f in result["findings"]]
        assert "charleston-georgian.c01" not in ids

    def test_charleston_piazza_bearing_fails_when_facing_away_from_southwest(self, plan_check_module, corpus):
        plan = minimal_plan([{"id": "r1", "type": "living-room", "width_ft": 14, "length_ft": 16}],
                             style="charleston-georgian")
        plan["site"] = {"piazza_bearing_deg": 45}  # due northeast -- 180 degrees off SW
        result = plan_check_module.check(plan, corpus)
        hit = [f for f in result["findings"] if f.get("rule") == "charleston-georgian.c01"]
        assert hit, "the piazza-bearing constraint should fire when the piazza faces away from southwest"
        assert hit[0]["severity"] == "serious"  # hard constraint -> CONSTRAINT_SEV["hard"]

    def test_bank_house_cross_slope_evaluates_from_site(self, plan_check_module, corpus):
        plan = minimal_plan([{"id": "r1", "type": "living-room", "width_ft": 14, "length_ft": 16}],
                             style="pennsylvania-bank-house")
        plan["site"] = {"cross_slope_pct": 5.0}  # well under the required 12.5%
        result = plan_check_module.check(plan, corpus)
        hit = [f for f in result["findings"] if f.get("rule") == "pennsylvania-bank-house.c01"]
        assert hit, "a bank house on a nearly flat lot should fail its own defining constraint"

    def test_bank_house_with_no_site_data_stays_unjudged_not_passed(self, plan_check_module, corpus):
        plan = minimal_plan([{"id": "r1", "type": "living-room", "width_ft": 14, "length_ft": 16}],
                             style="pennsylvania-bank-house")
        result = plan_check_module.check(plan, corpus)
        assert result["constraint_summary"]["unjudged"] >= 1


class TestComposerHonoursLotWidth:
    """PLAN-OF-ACTION.md's own example: 'a 24 ft town-house parti for a 30 ft lot; not a
    five-bay Georgian on a 40 ft lot.' family-georgian's brief already carries a 120 ft lot
    (unconstraining); these tests override it with a genuinely narrow one."""

    def test_lot_usable_width_subtracts_side_setbacks(self, compose_module):
        plan = {"site": {"lot_width_ft": 40, "setback_side_ft": 5}}
        assert compose_module.lot_usable_width_ft(plan) == 30

    def test_lot_usable_width_falls_back_to_context_when_site_absent(self, compose_module):
        plan = {"context": {"lot_width_ft": 50}}
        assert compose_module.lot_usable_width_ft(plan) == 50

    def test_lot_usable_width_is_none_when_no_lot_stated(self, compose_module):
        assert compose_module.lot_usable_width_ft({}) is None

    def test_no_candidate_exceeds_the_lots_usable_width(self, compose_module):
        """The direct acceptance test: every candidate compose() actually returns must fit
        inside lot_width_ft minus side setbacks -- never merely score worse."""
        brief = _brief("family-georgian")
        brief["site"] = {"lot_width_ft": 40, "setback_side_ft": 5}
        usable = 30
        result = compose_module.compose(brief)
        assert result["candidates"], "expected at least one candidate to still fit a 30 ft usable lot"
        for c in result["candidates"]:
            assert c["footprint"]["footprint_ft"][0] <= usable + 1e-6, \
                f"{c['parti_name']} footprint {c['footprint']['footprint_ft'][0]} ft exceeds the 30 ft usable lot"

    def test_five_part_palladian_never_reaches_its_usual_seven_bays_on_this_lot(self, compose_module):
        brief = _brief("family-georgian")
        brief["site"] = {"lot_width_ft": 40, "setback_side_ft": 5}
        result = compose_module.compose(brief)
        five_part = [c for c in result["candidates"] if c["parti"] == "five-part-palladian"]
        # The presence guard its two neighbours already have. Without it this test goes
        # silently green the moment the ranking stops returning this parti — and the scoring
        # change of 26 Aug 2026 moves rankings, which is exactly the circumstance that turns
        # a loop over an empty list into a passing test that checks nothing.
        assert five_part, (
            "five-part-palladian is no longer returned for this brief, so this test is "
            "asserting nothing. Re-pick the parti or the lot rather than leaving it green.")
        for c in five_part:
            assert c["footprint"]["bays"] <= 3, "9 ft bays x 3 = 27 ft is the most this 30 ft usable lot can hold"

    def test_a_parti_that_cannot_reach_even_three_bays_is_dropped_not_merely_outscored(self, compose_module):
        """foursquare-quadrant's bay module is 13 ft; 3 bays needs 39 ft, which a 30 ft usable
        lot cannot hold at all -- it must not appear anywhere in candidates, and must be named
        in dropped_lot_infeasible so the drop is not silent."""
        brief = _brief("family-georgian")
        brief["site"] = {"lot_width_ft": 40, "setback_side_ft": 5}
        result = compose_module.compose(brief, candidates=8)
        assert all(c["parti"] != "foursquare-quadrant" for c in result["candidates"])
        dropped_ids = [d["parti"] for d in result.get("dropped_lot_infeasible", [])]
        assert "foursquare-quadrant" in dropped_ids

    def test_side_hall_townhouse_fits_a_30_ft_lot_at_its_natural_three_bays(self, compose_module):
        """The brief's own illustrative case: an 8 ft bay module x 3 = 24 ft, comfortably
        inside a 30 ft usable lot with no capping needed at all."""
        brief = _brief("family-georgian")
        brief["site"] = {"lot_width_ft": 40, "setback_side_ft": 5}
        result = compose_module.compose(brief, candidates=8)
        townhouse = [c for c in result["candidates"] if c["parti"] == "side-hall-townhouse"]
        assert townhouse, "expected the side-hall townhouse to survive a 30 ft usable lot"
        assert townhouse[0]["footprint"]["footprint_ft"][0] == 24

    def test_wide_lot_is_unconstrained_exactly_as_before_this_package(self, compose_module):
        """family-georgian's own brief already carries a 120 ft lot -- confirms the lot-width
        package did not change behaviour when the lot was never the binding constraint (no
        candidate is dropped as lot-infeasible). Which parti ranks first is a SEPARATE question
        this test does not pin -- WP-3.2's elevation layer changed that answer for reasons that
        have nothing to do with lot width (see tests/test_composer.py's own module docstring for
        the trace); re-pinning it here would duplicate that test and tie an unrelated finding to
        the wrong package."""
        result = compose_module.compose(_brief("family-georgian"))
        assert not result.get("dropped_lot_infeasible")


class TestGeometrySolverHonoursLotWidth:
    """compose.py's own footprint() is a quick estimate; build/geometry.py's solve() is the
    placement that actually gets rendered, and it derives bay count independently from the
    massing's pile depth -- so it needs its own lot cap, or a plan that 'fit the lot' in
    compose.py's estimate could still be solved wider than its own lot right here."""

    def test_solved_footprint_never_exceeds_lot_usable_width(self, geometry_module, compose_module):
        brief = _brief("family-georgian")
        brief["site"] = {"lot_width_ft": 40, "setback_side_ft": 5}
        result = compose_module.compose(brief, candidates=8)
        townhouse = next(c for c in result["candidates"] if c["parti"] == "side-hall-townhouse")
        parti = compose_module.PARTIS["side-hall-townhouse"]
        out = geometry_module.solve(townhouse["plan"], parti, candidates=40, engine="heuristic")
        assert "error" not in out
        assert out["footprint"]["width_ft"] <= 30 + 1e-6

    def test_unchanged_when_plan_has_no_site_data(self, geometry_module):
        """The shipped Tidewater plan carries no `site` object (WP-2.4 added `site`; this plan
        predates it), only a generously wide context.lot_width_ft (140 ft) that this parti was
        never going to reach anyway -- solve() must behave exactly as it did before this
        package (test_geometry.py's own relaxation-count pin depends on this)."""
        plan = load_plan("tidewater-georgian-careful")
        assert plan.get("site") is None
        # engine pinned: these are the slicer's own numbers (the relaxation pin
        # below, which has read 11, then 9, then 7 as three packages moved it) — on
        # hardware fast enough for CP-SAT to finish inside the default budget, the
        # default engine would return CP's different count
        result = geometry_module.solve(plan, engine="heuristic")
        assert result["geometry_report"]["lot_capped"] is False
        # 7, moved from 9 by WP-7.4. The span term charges an over-capacity clear span, and the only way the slicer can create a bearing line is to cut ON the bay module -- so a term aimed at structure pulls cuts onto the grid, and a cut on the grid is not a relaxation. Measured on this plan with the two terms off and on: 9 -> 7 here and 7 -> 4 on spec-builder-colonial. It is an improvement and it is still a number that must not move BY ACCIDENT. Previously: 9, moved from 11 by WP-7.1 (OQ 76). The upper level is now sliced against the ground layout instead of blind, so an upper cut lands on a wall below where one is within tolerance — and a cut that lands on a wall below is not a compromise, because a relaxation is defined in geometry.py's own prose as a joist run that does not land on a bearing wall. The code had approximated that as 'misses the bay module', and 18 of 30 ground wall lines are themselves off the bay grid. Measured corpus-wide on 14 composed plans: relaxations 96 -> 76, transfer beams 166 -> 109.
        assert result["geometry_report"]["relaxations"]["count"] == 7

    def test_lot_too_narrow_for_even_two_bays_errors_honestly(self, geometry_module):
        plan = {
            "id": "impossible", "name": "Impossible", "style": "tidewater-georgian",
            "massing": "centre-passage-single-pile", "context": {}, "site": {"lot_width_ft": 12},
            "levels": [{"id": "ground", "index": 0, "rooms": [
                {"id": "lr", "type": "living-room", "width_ft": 14, "length_ft": 16}]}],
        }
        parti = {"scaling": {"bay_module_ft": 10, "max_bay_count": 5}}
        out = geometry_module.solve(plan, parti, engine="heuristic")
        assert "error" in out and "too narrow" in out["error"]


class TestRenderShowsTheLot:
    """PLAN-OF-ACTION.md's third acceptance clause: 'the render shows the lot.'"""

    def test_svg_includes_lot_boundary_and_dimensions_when_site_present(self, geometry_module, compose_module):
        brief = _brief("family-georgian")
        brief["site"] = {"lot_width_ft": 40, "lot_depth_ft": 140, "setback_side_ft": 5,
                          "setback_front_ft": 25, "setback_rear_ft": 15, "street_bearing_deg": 158}
        result = compose_module.compose(brief, candidates=8)
        townhouse = next(c for c in result["candidates"] if c["parti"] == "side-hall-townhouse")
        parti = compose_module.PARTIS["side-hall-townhouse"]
        out = geometry_module.solve(townhouse["plan"], parti, candidates=40, engine="heuristic")
        import importlib.util
        spec = importlib.util.spec_from_file_location("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
        rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)
        path = rp.render(out, "/tmp/wp24_render_test.svg")
        svg = open(path).read()
        assert "LOT 40" in svg
        assert "STREET BEARS 158" in svg

    def test_svg_has_no_lot_markup_when_no_site_data(self, geometry_module):
        """Backward compatibility: a plan with no lot data renders exactly as it did before
        this package -- no lot rectangle, no street-bearing caption."""
        plan = load_plan("tidewater-georgian-careful")
        out = geometry_module.solve(plan, engine="heuristic")
        import importlib.util
        spec = importlib.util.spec_from_file_location("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
        rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)
        path = rp.render(out, "/tmp/wp24_render_test_no_site.svg")
        svg = open(path).read()
        assert "LOT " not in svg
        assert "STREET BEARS" not in svg
        assert "NORTH IS UP" in svg


class TestSiteAndSettlementSlotConsumption:
    """'Consume the seven site-and-settlement slots where a kit specifies them.' Five of the
    seven are `binding: specified` variant slots and canonical_choices() -- generic across
    every slot group, predating this package -- already folds a single canonical variant into
    plan['declared']; this package added site_kit_log() for the two that are not variant-
    shaped (orientation_rule's editorial parameters, and setback_rule's deliberate `open`),
    which would otherwise leave the kit's own site data with no trace in the composer's output
    at all."""

    def test_canonical_choices_already_covers_five_of_seven_site_slots(self, compose_module):
        d = compose_module.canonical_choices("georgian-colonial-american")
        for sid in ("street_relationship", "outbuilding_types", "fence_wall",
                    "landscape_idiom", "grade_relationship"):
            assert sid in d, f"{sid} should have a canonical value for georgian-colonial-american"

    def test_site_kit_log_surfaces_orientation_rule_prose(self, compose_module):
        log = compose_module.site_kit_log("georgian-colonial-american")
        assert any("orientation_rule" in line for line in log)

    def test_site_kit_log_surfaces_open_setback_rule(self, compose_module):
        log = compose_module.site_kit_log("georgian-colonial-american")
        assert any("setback_rule" in line and "open" in line for line in log)

    def test_site_kit_log_is_empty_for_a_style_with_no_site_slot_data(self, compose_module):
        """Most styles' kits specify nothing under the site group at all yet (only
        georgian-colonial-american does, with tidewater-georgian inheriting two of the seven
        via `extends`) -- site_kit_log must not invent anything for the rest."""
        log = compose_module.site_kit_log("greek-revival-american")
        assert log == []

    def test_instantiate_includes_site_kit_log_in_the_decision_log(self, compose_module):
        brief = _brief("family-georgian")  # style: tidewater-georgian, inherits grade_relationship/orientation_rule
        plan, log, parti = compose_module.instantiate("centre-passage-single-pile", brief)
        assert any("orientation_rule" in line for line in log)
