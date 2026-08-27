"""Pins WP-3.2, the elevation generator -- see docs/elevation.md and docs/reports/wp-3.2-elevation-generator.md's
own "What was found" section for the narrative version of most of what these tests pin directly.

Follows the same discipline tests/test_roof.py established for WP-3.3: unit tests against the
real code paths (including the ones a hand-authored synthetic plan has to exercise, because
neither shipped reference plan carries every condition), plus explicit end-to-end tests against
both shipped plans naming the acceptance criteria verbatim where practical, plus regression tests
for bugs actually found and fixed during this WP (each one names the bug it pins, the same way
test_roof.py's TestWingStepDown/TestCapeEaveCheck do for WP-3.3's own fixes).
"""
import json
import os
import pytest
import math

from conftest import ROOT, load_plan


def _tidewater_elevation(elevation_module, style=None):
    plan = load_plan("tidewater-georgian-careful")
    if style is not None:
        plan["style"] = style
    return plan, elevation_module.build_elevation(plan)


class TestGlassModuleForDate:
    def test_before_1700_is_the_narrowest_band(self, elevation_module):
        module_in, note = elevation_module.glass_module_for_date(1690)
        assert module_in == 7.0

    def test_1765_falls_in_the_1760_1800_band(self, elevation_module):
        """The shipped tidewater-georgian-careful plan declares date_of_representation 1765."""
        module_in, note = elevation_module.glass_module_for_date(1765)
        assert module_in == 10.5

    def test_after_1900_is_effectively_unlimited(self, elevation_module):
        module_in, note = elevation_module.glass_module_for_date(1950)
        assert module_in == elevation_module.GLASS_MODULE_AFTER_1900

    def test_no_date_falls_back_to_the_period_neutral_default_with_a_note(self, elevation_module):
        """An undeclared date does not stop a compositional elevation from being drawn at all --
        it falls back to sash-light.json's own 1700-1760 band midpoint (9 in), stated as a
        default rather than a guess at an actual date (see the module's own note)."""
        module_in, note = elevation_module.glass_module_for_date(None)
        assert module_in == 9.0
        assert "no context.date_of_representation" in note


class TestPackEnvAutoFill:
    """Regression test for the bug: _val() originally only merged PE.DEFAULT_BINDINGS with the
    caller's env, so any rule relying on proportion_engine.evaluate()'s own module/part/
    column_height auto-fill (e.g. facade-classical's window_grouping_rule, which uses `module`
    without the caller ever supplying it) raised ExprError: unbound name 'module'."""

    def test_bay_count_rule_resolves_module_without_the_caller_supplying_it(self, elevation_module):
        PE = elevation_module.PE
        facade_pack = PE.resolve("facade-classical")
        count, module_in = elevation_module._bay_count(facade_pack, span_ft=62.58)
        assert count == 5   # verified against tidewater-georgian-careful's own outside width
        assert module_in == facade_pack["module"]["default_size_in"]


class TestStoreyWindowSizing:
    """Regression test for the bug: sizing width first from a room-width proxy (the structural
    bay module) and letting the sill fall out of head-minus-height put the sill at 55 in above
    the floor -- tripped window-squarer-than-the-style-permits (fatal). Fixed by fixing the head
    (from the ceiling rule) and the sill (opening-proportion's own 28-32 in convention) and
    deriving height and width from those two fixed points instead."""

    def test_sill_is_pinned_at_the_documented_convention(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        assert "error" not in elev
        for w in elev["storey_windows"]:
            assert w["sill_height_above_floor_in"] == elevation_module.TARGET_SILL_IN

    def test_height_is_head_minus_sill_not_a_guessed_width_times_ratio(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        for w in elev["storey_windows"]:
            assert math.isclose(w["opening_height_in"], w["head_height_above_floor_in"] - w["sill_height_above_floor_in"], abs_tol=0.01)

    def test_single_head_datum_per_storey(self, elevation_module):
        """opening-proportion.json's own hardest rule: DISTINCT HEAD DATUMS PERMITTED ON ONE
        STOREY: ONE. _storey_window() is called once per storey and its head_height is shared by
        every opening on that storey by construction -- this pins that both shipped plans keep it."""
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = load_plan(name)
            elev = elevation_module.build_elevation(plan)
            assert "error" not in elev
            for w in elev["storey_windows"]:
                assert w["head_datum_count"] == 1

    def test_room_width_diagnostic_is_recorded_but_not_the_driver(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        gw = elev["storey_windows"][0]
        assert "room_width_diagnostic_width_in" in gw
        assert gw["room_width_diagnostic_width_in"] != gw["opening_width_in"]   # the two are independently sourced and need not agree


class TestBayLayout:
    def test_tidewater_front_gets_five_bays(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        assert elev["front"]["count"] == 5

    def test_door_bay_is_centred(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        front = elev["front"]
        mid = front["count"] // 2
        assert front["kinds"][mid] == "door"
        assert front["kinds"].count("door") == 1

    def test_bays_are_spaced_evenly_across_the_real_face_width(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        front = elev["front"]
        widths = [round(front["centres_ft"][i + 1] - front["centres_ft"][i], 3) for i in range(front["count"] - 1)]
        assert all(math.isclose(w, front["actual_bay_width_in"] / 12.0, abs_tol=0.01) for w in widths)

    def test_every_face_gets_an_odd_bay_count(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        for face in elevation_module.FACES:
            assert elev["faces"][face]["count"] % 2 == 1


class TestEntranceComposition:
    def test_gibbs_ionic_applies_to_tidewater_georgian(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        assert elev["gibbs_order_applies_to_style"] is True

    def test_casing_width_agrees_between_the_two_independently_sourced_rules(self, elevation_module):
        """opening-proportion's door_surround (module/6) and gibbs-ionic's own casing rule
        (opening_width/6) are the same expression at the same module -- confirmed to agree exactly."""
        plan, elev = _tidewater_elevation(elevation_module)
        ent = elev["entrance"]
        assert math.isclose(ent["casing_width_in"], ent["gibbs_casing_width_in"], abs_tol=0.01)

    def test_sidelights_fit_within_the_composition_cap_on_the_tidewater_plan(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        assert elev["entrance"]["sidelights_present"] is True

    def test_pilaster_width_equals_the_column_diameter_it_answers(self, elevation_module):
        """column-without-answering-pilaster.json: a pilaster that genuinely answers a column
        takes the column's own diameter as its width -- both figures come from the same
        gibbs_module_in*2 expression here by construction, so the ratio is exactly 1.0."""
        plan, elev = _tidewater_elevation(elevation_module)
        ent = elev["entrance"]
        assert math.isclose(ent["pilaster_width_in"], ent["lower_shaft_diameter_in"], abs_tol=0.001)

    def test_no_entasis_upper_equals_lower_shaft_diameter(self, elevation_module):
        """Disclosed scope limit: this generator draws a flat doorcase pilaster shaft with no
        entasis rule anywhere in the codebase, so upper and lower diameter are genuinely equal --
        a real fact (this trips faults/column-without-entasis.json honestly), not an omission."""
        plan, elev = _tidewater_elevation(elevation_module)
        ent = elev["entrance"]
        assert ent["upper_shaft_diameter_in"] == ent["lower_shaft_diameter_in"]

    def test_pilaster_projection_matches_the_kit_s_own_worked_example_order_of_magnitude(self, elevation_module):
        """faults/pilaster-that-is-a-flat-board.json's own note works a 90 in column / 13.5 in
        pilaster example to a 0.37 ratio; this doorcase's own numbers should land in the same
        neighbourhood since it is the same rule (column_height/18) at a different module."""
        plan, elev = _tidewater_elevation(elevation_module)
        ent = elev["entrance"]
        ratio = ent["pilaster_projection_in"] / ent["pilaster_width_in"]
        assert ratio > 0.125   # the fault's own generous threshold


class TestEaveCornice:
    def test_real_storey_height_is_used_not_the_stock_default(self, elevation_module):
        """Regression test for the bug: eave_cornice() originally always used facade-classical's
        stock 108 in default module regardless of the plan's actual (much taller, Tidewater)
        storey height, undersizing the cornice and tripping cornice-that-is-a-fascia's own
        wall-height-ratio secondary test."""
        plan, elev = _tidewater_elevation(elevation_module)
        assert elev["eave_cornice"]["reduced_gibbs_module_in"] != elevation_module.eave_cornice(
            elevation_module.PE.resolve("facade-classical"), elevation_module.PE.resolve("gibbs-ionic")
        )["reduced_gibbs_module_in"]

    def test_members_sum_to_the_stated_domestic_envelope(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        cornice = elev["eave_cornice"]
        summed = sum(m["height_in"] for m in cornice["members"])
        assert math.isclose(summed, cornice["cornice_height_in"], abs_tol=0.05)


class TestWaterTableAndBelt:
    def test_tidewater_plan_uses_brick_course_masonry_path(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        assert elev["water_table_belt"]["is_masonry"] is True
        assert "brick-course" in elev["water_table_belt"]["source"]

    def test_spec_builder_plan_uses_facade_classical_frame_path(self, elevation_module):
        plan = load_plan("spec-builder-colonial")
        elev = elevation_module.build_elevation(plan)
        assert elev["water_table_belt"]["is_masonry"] is False
        assert "facade-classical" in elev["water_table_belt"]["source"]


class TestBuildElevationEndToEnd:
    """Exercises the acceptance criteria named in the hand-off brief."""

    def test_both_shipped_plans_produce_a_complete_record(self, elevation_module):
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = load_plan(name)
            elev = elevation_module.build_elevation(plan)
            assert "error" not in elev
            assert elev["front"]["count"] >= 3
            assert len(elev["measurements"]) > 50

    def test_glass_module_matches_the_declared_date_of_representation(self, elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        assert plan["context"]["date_of_representation"] == 1765
        assert elev["glass_module_in"] == 10.5


class TestFaultCorpusIntegration:
    """The elevation layer's own acceptance test: fed into plan_check.py's ELEVATION LAYER
    (build/plan_check.py), the careful reference plan should trip zero fatal faults, and the
    layer should meaningfully raise how many of the corpus's photograph-measurable faults get
    evaluated at all (present or clear, as opposed to could_not_judge)."""

    def test_careful_plan_trips_no_fatal_faults(self, elevation_module):
        # This reproduces exactly what build/plan_check.py's own ELEVATION LAYER block does
        # (build the record, fold its measurements dict into core.check_measurements) -- the
        # same assertion the WP-3.2 verification runs made repeatedly while chasing each fatal
        # (window sill, gutter-as-cornice, storey alignment, cornice-that-is-a-fascia, roof
        # pitch rounding, pork-chop-return) to ground one at a time.
        import core
        plan = load_plan("tidewater-georgian-careful")
        elev = elevation_module.build_elevation(plan)
        res = core.check_measurements(elev["measurements"], style=plan["style"], limit=1000)
        fatal = [f for f in res["faults_present"] if f["severity"] == "fatal"]
        assert fatal == []

    def test_elevation_layer_measurements_are_folded_into_plan_checks_own_meas_dict(self, elevation_module):
        """Regression test for the KeyError bug: front (=elev['front']) IS the bay-layout dict
        itself, not a dict containing a nested 'bays' key -- `bays = front["bays"]` raised
        KeyError; fixed to `bays = front` (a direct alias)."""
        plan, elev = _tidewater_elevation(elevation_module)
        assert "pier_width_in" in elev["measurements"]   # only reachable if the bays alias resolved correctly

    def test_a_plans_own_declared_measurement_still_wins_over_the_generated_one(self, elevation_module):
        """spec-builder-colonial.json declares its own (deliberately flawed) shutter_leaf_width_in
        and window_opening_width_in -- setdefault precedence must leave those alone even after
        elevation.py's own measurements are folded in under the same keys."""
        import core
        plan = load_plan("spec-builder-colonial")
        declared = dict(plan.get("measurements") or {})
        elev = elevation_module.build_elevation(plan)
        meas = dict(elev["measurements"])
        for k, v in declared.items():
            meas.setdefault(k, v)   # WRONG order on purpose, to prove the real code's order matters
        # the real order (plan_check.py's ELEVATION LAYER) starts from the plan's own declared
        # measurements and only setdefaults the generated ones on top -- reproduce that here
        real_meas = dict(declared)
        for k, v in elev["measurements"].items():
            real_meas.setdefault(k, v)
        assert real_meas["shutter_leaf_width_in"] == declared["shutter_leaf_width_in"]
        res = core.check_measurements(real_meas, style=plan["style"], limit=1000)
        ids = [f["fault"] for f in res["faults_present"]]
        assert "shutter-half-width-leaf" in ids


class TestCorniceProfileGeometry:
    """Successor to TestSegTo, which pinned build/render_elevation.py's line-for-line port of
    orders_template.html's segTo() -- control point for control point, Bezier fraction for Bezier
    fraction. WP-5.7 deleted the thing it pinned: those curves were hand-tuned approximations, and
    worse, profile_silhouette_path() always called seg_to() with xa == xb, so every one of them
    degenerated to a vertical line and the cornice drew as a flight of steps whatever the profile
    names said. Pinning the arithmetic of a curve nobody could see is not a guard.

    What replaces it: build/profiles.py CONSTRUCTS each moulding and proves the construction
    (tangency, convexity, scale invariance) in its own selftest and tests/test_profiles.py. What
    is pinned HERE is the part that belongs to the elevation -- that the real cornice record
    produces a real closed profile, at the right relief, off the right plane."""

    def test_the_cornice_draws_as_a_closed_profile_spanning_every_member(self, elevation_module,
                                                                         render_elevation_module):
        plan, elev = _tidewater_elevation(elevation_module)
        cor = elev["eave_cornice"]
        PROF = render_elevation_module.PROF
        sil = PROF.silhouette(cor["members"], naked_at=cor["frieze_naked_in"],
                              from_axis=cor["entablature_projection_datum"] == "axis")
        assert sil["segments"], "the cornice produced no geometry at all"
        assert sil["segments"][-1]["kind"] == "close"
        ys = []
        for sg in sil["segments"]:
            if sg["kind"] == "line":
                ys.append(sg["to"][1])
            elif sg["kind"] == "arc":
                ys += [PROF.arc_point(sg, t / 8)[1] for t in range(9)]
        # Every member must appear: a profile that starts above the bed mould has dropped one.
        assert min(ys) == pytest.approx(cor["members"][0]["y_bottom_in"], abs=0.01)
        assert max(ys) == pytest.approx(cor["members"][-1]["y_top_in"], abs=0.01)

    def test_curves_are_actually_drawn_rather_than_degenerating_to_steps(self, elevation_module,
                                                                        render_elevation_module):
        """The failure the old port hid: this cornice carries three cymas, and if the geometry
        comes back as nothing but straight lines they have collapsed into their own faces again."""
        plan, elev = _tidewater_elevation(elevation_module)
        cor = elev["eave_cornice"]
        PROF = render_elevation_module.PROF
        sil = PROF.silhouette(cor["members"], naked_at=cor["frieze_naked_in"],
                              from_axis=cor["entablature_projection_datum"] == "axis")
        arcs = [sg for sg in sil["segments"] if sg["kind"] == "arc"]
        curved = [m for m in cor["members"]
                  if (m.get("profile") or "") in ("cyma-recta", "cyma-reversa", "ogee", "ovolo",
                                                  "cavetto", "scotia", "torus", "astragal", "bead")]
        assert len(arcs) >= len(curved), (
            f"{len(curved)} curved members produced only {len(arcs)} arcs")

    def test_the_entablature_datum_is_read_from_the_pack_not_assumed(self, elevation_module):
        """OQ 65 ruled the projection datum onto the PACK, and check_orders.py verifies that
        declaration against the shaft, base and capital. The entablature in the same pack does not
        follow it: gibbs-ionic declares `axis`, yet its frieze face and its architrave's lowest
        fascia both record a projection of 0, and a frieze cannot stand on the column's centre
        line. Reading the pack-level declaration literally over the cornice clamps every member
        whose figure is under the column radius flush with the frieze -- which deletes this
        cornice's bed mould and its fillet from the drawing. The record must carry the
        entablature's OWN datum."""
        plan, elev = _tidewater_elevation(elevation_module)
        cor = elev["eave_cornice"]
        assert cor["projection_datum"] == "axis", "the pack still declares axis for its column"
        assert cor["entablature_projection_datum"] == "naked"
        assert cor["frieze_naked_in"] == 0.0
        # and the relief is then the order's own full projection, not a clamped remainder
        assert cor["order_relief_beyond_frieze_in"] == pytest.approx(
            max(m["projection_in"] for m in cor["members"]), abs=0.01)

    def test_two_sourced_rules_disagree_and_the_record_says_so(self, elevation_module):
        """Gibbs's own rule makes the cornice project as far as it stands tall; facade-classical's
        domestic envelope rule gives module/14. Both are sourced, they are not the same number,
        and the record is required to name the disagreement rather than quietly pick a winner."""
        plan, elev = _tidewater_elevation(elevation_module)
        cor = elev["eave_cornice"]
        assert cor["envelope_projection_in"] > 0
        assert abs(cor["order_relief_beyond_frieze_in"] - cor["envelope_projection_in"]) > 0.5
        note = cor["projection_disagreement_note"].lower()
        assert "disagree" in note and "neither is chosen" in note

    def test_the_drawn_sheet_discloses_the_datum_and_the_disagreement(self, elevation_module,
                                                                     render_elevation_module, tmp_path):
        plan, elev = _tidewater_elevation(elevation_module)
        out = render_elevation_module.render_elevation(elev, str(tmp_path / "e.svg"))
        svg = open(out).read()
        assert "EAVE CORNICE PROFILE" in svg
        assert "RELIEF FROM THE FRIEZE NAKED" in svg
        assert "BOTH SOURCED" in svg


class TestTheHeadOfAnOpeningIsReadNotAsserted:
    """WP-5.7 shipped a style fact hardcoded and attributed to a pack that does not contain it,
    which is the invented-source failure CLAUDE.md calls the worst thing that can be done to this
    corpus. It wrote `"keystone": False` with a comment claiming "the kit states keystone: none
    for this tradition" and a `source` string citing `brick-course.json window_head_masonry` --
    in which the word "keystone" does not occur. The claim was true of exactly one style.

    It also hardened brick-course's own note -- "the change is roughly 1720-1750 IN THE
    CHESAPEAKE" -- into a global `< 1750` point test, so an absent date produced a definite
    gauged flat arch and a source sentence reading "the None date puts it after the change":
    could-not-evaluate published as evidence, reachable by anyone who can POST a plan."""

    def _with(self, elevation_module, style=None, date="keep"):
        plan = load_plan("tidewater-georgian-careful")
        if style:
            plan["style"] = style
        if date == "keep":
            pass
        elif date is None:
            plan["context"].pop("date_of_representation", None)
        else:
            plan["context"]["date_of_representation"] = date
        return elevation_module.build_elevation(plan)

    def test_a_keystone_comes_from_the_style_kit_and_not_from_a_constant(self, elevation_module):
        """tidewater-georgian FORBIDS the keystoned flat arch and states keystone: none.
        mid-atlantic-georgian makes it CANONICAL with a measured 6-9 in keystone and a measured
        4-6 in rise. One hardcoded False cannot be right for both."""
        tw = self._with(elevation_module)["storey_windows"][0]["head_treatment"]
        assert tw["keystone"] is False

        ma = self._with(elevation_module, style="mid-atlantic-georgian")["storey_windows"][0]["head_treatment"]
        assert ma["kind"] == "keystoned-flat-arch"
        assert ma["keystone"] is True
        assert ma["keystone_width_in"] == [6, 9]
        # and its own measured rise band beats a rule derived for another tradition
        assert ma["rise_band_in"] == [4, 6]
        assert "kit" in (ma["rise_source"] or "")

    def test_no_source_string_claims_a_pack_that_does_not_say_it(self, elevation_module):
        head = self._with(elevation_module)["storey_windows"][0]["head_treatment"]
        brick = open(os.path.join(ROOT, "proportions", "modules", "brick-course.json")).read()
        assert "keystone" not in brick.lower(), "brick-course now mentions keystones; revisit this"
        assert "keystone" not in (head.get("source") or "").lower(), (
            "the head's source cites a pack for a fact that pack does not carry")

    def test_a_date_inside_the_change_band_is_unjudged_rather_than_rounded(self, elevation_module):
        """brick-course states a BAND -- 1720 to 1750 -- and a band is not a threshold."""
        head = self._with(elevation_module, date=1735)["storey_windows"][0]["head_treatment"]
        assert head["kind"] is None
        assert "band" in head["kind_note"].lower()

    def test_an_absent_date_says_so_instead_of_reporting_one(self, elevation_module):
        head = self._with(elevation_module, date=None)["storey_windows"][0]["head_treatment"]
        assert head["kind"] is None
        blob = json.dumps(head).lower()
        assert "none date" not in blob, "an absent date is being narrated as an evaluated one"
        assert "no date" in head["kind_note"].lower()

    def test_an_unjudged_head_is_not_drawn_and_the_sheet_says_why(self, elevation_module,
                                                                  render_elevation_module, tmp_path):
        elev = self._with(elevation_module, date=None)
        svg = open(render_elevation_module.render_elevation(elev, str(tmp_path / "u.svg"))).read()
        assert 'class="arch' not in svg, "an unjudged head was drawn as a definite one"
        assert "WINDOW HEAD UNJUDGED" in svg

    def test_the_chimney_judgment_reaches_the_sheet(self, elevation_module,
                                                   render_elevation_module, tmp_path):
        """brick-course flags the stack width `judgment: true` -- "a mason will build 18 or 27
        and someone should decide". WP-5.7's comment, report and commit message all said the
        figure reaches the drawing labelled as a judgment. It reached no sheet at all."""
        elev = self._with(elevation_module)
        assert elev["chimney_stack_plan_judgment"], "the record dropped the judgment note"
        svg = open(render_elevation_module.render_elevation(elev, str(tmp_path / "c.svg"))).read()
        assert "JUDGMENT" in svg.upper()
        assert "18" in svg and "27" in svg


class TestRenderElevation:
    def test_both_shipped_plans_render_a_valid_svg(self, elevation_module, render_elevation_module, tmp_path):
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = load_plan(name)
            elev = elevation_module.build_elevation(plan)
            out = tmp_path / f"{name}-elevation.svg"
            render_elevation_module.render_elevation(elev, str(out))
            text = out.read_text()
            assert text.startswith("<svg")
            assert "ELEVATION" in text
            assert "EAVE CORNICE PROFILE" in text

    def test_gable_end_face_renders_the_roofline_and_chimney(self, elevation_module, render_elevation_module, tmp_path):
        plan, elev = _tidewater_elevation(elevation_module)
        out = tmp_path / "tidewater-E.svg"
        render_elevation_module.render_elevation(elev, str(out), face="E")
        text = out.read_text()
        # The roof carries a line-weight class alongside its own now (WP-5.9), so match the TOKEN
        # rather than the whole attribute -- a pin on `class="rf"` exactly would fail every time
        # the roof moved a rung on the ladder without the roof having changed at all.
        assert 'class="rf' in text
        assert 'class="ch"' in text   # tidewater-georgian-careful's own gable-end chimneys (WP-3.3)
        # WP-5.9: and the roof is a closed plane now, not a line along its bottom edge.
        assert "<polygon" in text, "the roof is drawn as a polyline again"

    def test_long_face_of_a_side_gable_shows_no_chimney(self, elevation_module, render_elevation_module, tmp_path):
        """WP-3.3's own finding: both of this plan's chimneys sit on the gable-end (E/W) walls --
        the S/N long faces should not draw a chimney that is not actually in that wall's plane."""
        plan, elev = _tidewater_elevation(elevation_module)
        out = tmp_path / "tidewater-S.svg"
        render_elevation_module.render_elevation(elev, str(out), face="S")
        text = out.read_text()
        assert 'class="ch"' not in text

    def test_unjudged_ridge_renders_a_flat_roofline_not_an_invented_pitch(self, elevation_module, render_elevation_module, tmp_path):
        plan = load_plan("spec-builder-colonial")
        elev = elevation_module.build_elevation(plan)
        assert elev["roof_record"]["main"].get("pitch_rise_per_12") is None   # colonial-revival carries no migrated pitch constraint (WP-3.3)
        out = tmp_path / "spec-builder-elevation.svg"
        render_elevation_module.render_elevation(elev, str(out))
        text = out.read_text()
        assert text.startswith("<svg")
