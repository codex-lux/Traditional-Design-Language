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
import re
import os
import pytest
import math

from conftest import ROOT, load_plan


def _tidewater_elevation(elevation_module, style=None):
    plan = load_plan("tidewater-georgian-careful")
    if style is not None:
        plan["style"] = style
    return plan, elevation_module.build_elevation(plan)


def _stack_polys(text):
    """Every stack the sheet draws, as its outline's points in px. A stack is a POLYGON since
    WP-14.6 -- its foot follows the rake on a gable face -- and a reader that selected `<rect>`
    would read none on every sheet that draws one: the `class="ch"` lesson, one attribute over."""
    import re as _re
    return [[tuple(float(v) for v in pt.split(",")) for pt in pts.split()]
            for pts in _re.findall(r'<polygon class="ch[^"]*" points="([^"]+)"', text)]


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
    def test_tidewater_front_gets_the_bay_count_its_own_footprint_states(self, elevation_module):
        """FIVE AT WP-11.16, and the test is RENAMED rather than re-pinned under a name saying
        seven -- a `..._gets_seven_bays` over a 5 is this repository's own "until X lands" trap,
        and a name is the first thing a reader trusts.

        The cause is a record edit: `plans/tidewater-georgian-careful.json` declares 617 sf of
        service programme as a west dependency, so the main block is 45 ft wide instead of 63
        and its front carries five bays. `styles/tidewater-georgian.json` admits both in its own
        words -- *"Five or seven bays, unaccented, the centre marked only by the doorway"* -- so
        this is the house changing shape and not a rule breaking.

        AND THE COINCIDENCE THE PARAGRAPH BELOW WARNS ABOUT HAS GOT NARROWER, which is worth
        saying because it makes the corpus WEAKER for this join, not stronger: both shipped
        plans now read 5, so the two independent derivations agree at a single value across the
        whole corpus. Nothing holds them to each other; `tests/test_facade.py` drives them apart
        deliberately for that reason.

        SEVEN, moved from five by WP-11.2, and the move revealed that these two layers had
        been DISAGREEING. The elevation derives its own odd bay count from `facade-classical`'s
        window-grouping rule against the face's actual width; the plan derives its own from the
        area and (now) the massing. Before WP-11.2 the elevation said five and the footprint
        said six and no test compared them. The face is 63 ft now and both say seven, which
        `styles/tidewater-georgian.json` admits in its own words -- *"Five or seven bays,
        unaccented, the centre marked only by the doorway"*. That the two agree here is a
        coincidence of one plan and not a mechanism: nothing holds them to each other, which is
        worth knowing before trusting either. """ + \
        ""
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
        """RE-CUT 30 SEP 2026 (WP-16.4): the shipped record is dated 1765, and
        georgian-colonial-american forbids the sidelights for 1700-1780, so at its own date the
        pair is refused by the KIT and this test could no longer see the cap at all. The cap is
        a property of the bay and not of the date, so it is read at 1790, outside the ban, where
        the only thing that could still refuse the pair is the cap. The shipped date is held too,
        so a refusal that stopped naming its writer fails here as well."""
        plan = load_plan("tidewater-georgian-careful")
        assert (plan.get("context") or {}).get("date_of_representation") == 1765, (
            "the premise: the shipped Tidewater record is dated inside the kit's 1700-1780 ban")
        shipped = elevation_module.build_elevation(plan)["entrance"]
        assert shipped["sidelights_present"] is False
        assert shipped["sidelights_refused_by"]["writers"] == ["georgian-colonial-american"]
        assert shipped["sidelights_refused_by"]["date"] == 1765
        plan = load_plan("tidewater-georgian-careful")
        plan.setdefault("context", {})["date_of_representation"] = 1790
        released = elevation_module.build_elevation(plan)["entrance"]
        assert released["sidelights_present"] is True
        assert not released.get("sidelights_refused_by")

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

    # THE THREE FATALS THE PLACEMENT EARNS, AND THE MEASUREMENTS THAT CONVICT IT (WP-13.3).
    # Every one reads an opening the plan PLACED: the upper front carries four windows (an
    # even count), five of the seven ground openings have no mirror twin, and the nearest
    # upper window stands 48 in from a ground one. Until WP-13.3 all three read constants
    # derived from the RHYTHM -- "every upper bay stacks over its lower by construction" --
    # and the plan passed them by never being looked at. The names are pinned so that a
    # fatal from any OTHER measurement (one this generator invents) still fails this test.
    PLACEMENT_FATALS = {
        "even-bay-front": {"upper_floor_opening_count"},
        "one-bay-symmetry-break": {"count_of_openings_without_a_mirror_twin_about_the_facade_centreline",
                                   "width_of_the_largest_asymmetric_element_in"},
        "storeys-out-of-vertical-alignment": {
            "max_abs_offset_between_upper_and_lower_opening_centrelines_in",
            "upper_storey_opening_centres_matching_lower", "total_upper_storey_openings",
            "bay_count_on_the_principal_front"},
    }

    def test_careful_plan_trips_no_fatal_fault_of_the_generators_own_making(self, elevation_module):
        # This reproduces exactly what build/plan_check.py's own ELEVATION LAYER block does
        # (build the record, fold its measurements dict into core.check_measurements) -- the
        # same assertion the WP-3.2 verification runs made repeatedly while chasing each fatal
        # (window sill, gutter-as-cornice, storey alignment, cornice-that-is-a-fascia, roof
        # pitch rounding, pork-chop-return) to ground one at a time.
        #
        # RE-CUT AT WP-13.3, and the reason is the whole of that package: "storey alignment"
        # in the list above was chased to ground by SUPPLYING it -- a constant 0.0 offset and a
        # matching count equal to the bay count -- which was true of the rhythm and false of
        # the house. The elevation's openings are the plan's placed openings now, so the
        # measurements convict the PLACEMENT of exactly the incoherence Lucas read off the
        # sheet (the bays are not coordinated between floors), on the heuristic placement of
        # the declared record. Those fatals are the placement's and are named; what this test
        # still refuses is a fatal from a measurement this generator makes up.
        #
        # RE-CUT AT WP-16.1 (29 Sep 2026): ONE OF THE THREE IS A VERDICT AND TWO ARE UNJUDGED.
        # This front declares window units the placement did not draw, and R12 (ruled 29 Sep
        # 2026) makes an incomplete front unjudged for symmetry and alignment everywhere. The
        # elevation still MEASURES the mirror and the alignment (they stay on the record, and
        # are asserted below); it withholds their figures from the faults, and under R4 a fault
        # whose governing test could not run is could-not-evaluate. So `even-bay-front` is the
        # one fatal, and the other two are in the unjudged bucket for the withheld figures --
        # neither cleared, which is the direction WP-15.8 measured the old `_judge` taking.
        import core
        plan = load_plan("tidewater-georgian-careful")
        elev = elevation_module.build_elevation(plan)
        res = core.check_measurements(elev["measurements"], style=plan["style"], limit=1000)
        fatal = {f["fault"]: f for f in res["faults_present"] if f["severity"] == "fatal"}
        judged = {"even-bay-front"}
        assert set(fatal) == judged, (
            f"fatal faults {sorted(fatal)} against the one the placement earns on an "
            f"incomplete front {sorted(judged)}: a new one is a measurement to read, not a "
            f"number to pin")
        for fid, f in fatal.items():
            names = {r.get("expression") for r in f.get("results") or []}
            # every expression that convicted reads a placed-opening measurement by name
            assert all(any(n in e for n in self.PLACEMENT_FATALS[fid]) for e in names), (fid, names)
        assert elev["front"]["complete"]["complete"] is False, "the premise: an incomplete front"
        unj = {u["fault"]: u for u in res["could_not_judge"]}
        held = elev["front"]["withheld"]
        for fid in sorted(set(self.PLACEMENT_FATALS) - judged):
            assert fid in unj, (fid, "neither convicted nor unjudged: it has left every list")
            assert fid not in {c["fault"] for c in res["faults_clear"]}, fid
            assert set(unj[fid]["needs"]) & set(held), (fid, unj[fid]["needs"])
        m = elev["measurements"]
        assert m["upper_floor_opening_count"] % 2 == 0, "the even upper count is what convicts"
        # still measured, still on the record: the gate withholds and does not stop measuring
        assert elev["front"]["alignment"]["max_abs_offset_in"] > 2.0
        assert elev["front"]["mirror"]["unmatched"]
        assert "max_abs_offset_between_upper_and_lower_opening_centrelines_in" not in m
        assert "count_of_openings_without_a_mirror_twin_about_the_facade_centreline" not in m

    def test_the_three_fatals_are_the_placements_and_not_constants(self, elevation_module):
        """The control: hand the front a placement whose upper windows DO stand over the lower
        ones, mirrored, an odd count -- by driving the face record -- and the three fatals
        clear. A constant could not do that, which is what separates a measurement from one."""
        import core
        plan = load_plan("tidewater-georgian-careful")
        elev = elevation_module.build_elevation(plan)
        face = elev["entrance_face"]
        fa = elev["faces"][face]
        ground = [p for p in fa["placed"] if p["storey"] == "ground"]
        assert ground, "the fixture needs ground openings on the front"
        # an upper window over every ground opening, at the ground opening's own centre
        upper = []
        for i, p in enumerate(ground):
            q = dict(p, kind="window", storey="upper", level_index=1, entrance=False, n=i)
            upper.append(q)
        fa["placed"] = ground + upper
        # rebuild the record's own derived halves exactly as build_elevation does
        rects = elevation_module.opening_rects(elev, face)["rects"]
        lo = sorted(r["cx_in"] for r in rects if r["storey"] == "ground")
        up = sorted(r["cx_in"] for r in rects if r["storey"] == "upper")
        assert len(up) == len(lo) > 0
        elev["front"]["alignment"] = elevation_module.storey_alignment(
            lo, up, elevation_module.ALIGNMENT_TOL_IN)
        # the driven front is whole -- an upper window over every ground opening -- so the
        # R12 gate (WP-16.1) is driven open with it; the control is about the measurement
        elev["front"]["complete"] = {"complete": True, "why": None}
        m = elevation_module._derive_measurements(elev)
        assert m["max_abs_offset_between_upper_and_lower_opening_centrelines_in"] == 0.0
        assert m["upper_storey_opening_centres_matching_lower"] == len(up)
        assert m["upper_storey_windows_missing_or_off_alignment_over_a_lower_bay"] == 0
        res = core.check_measurements(m, style=plan["style"], limit=1000)
        fatal = {f["fault"] for f in res["faults_present"] if f["severity"] == "fatal"}
        assert "storeys-out-of-vertical-alignment" not in fatal, fatal

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
    fraction. WP-5.11 deleted the thing it pinned: those curves were hand-tuned approximations, and
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
    """WP-5.11 shipped a style fact hardcoded and attributed to a pack that does not contain it,
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
        # THE POSITIVE CONTROL, ON THE SAME SHEET CLASS AND IN THIS TEST (audit, 27 Sep 2026;
        # auditor D, F13b): the same house with its date draws its judged heads as arches, so a
        # renamed arch class turns this test red rather than making the negative half a pass.
        # Its only control used to live in another file, and run alone this test stayed green.
        dated = open(render_elevation_module.render_elevation(
            self._with(elevation_module), str(tmp_path / "d.svg"))).read()
        assert dated.count('class="arch') > 0, "the premise: the dated house draws its arches"
        assert 'class="arch' not in svg, "an unjudged head was drawn as a definite one"
        assert "WINDOW HEAD UNJUDGED" in svg

    def test_the_chimney_judgment_reaches_the_sheet(self, elevation_module,
                                                   render_elevation_module, tmp_path):
        """brick-course flags the stack width `judgment: true` -- "a mason will build 18 or 27
        and someone should decide". WP-5.11's comment, report and commit message all said the
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
        # The roof carries a line-weight class alongside its own now (WP-5.13), so match the TOKEN
        # rather than the whole attribute -- a pin on `class="rf"` exactly would fail every time
        # the roof moved a rung on the ladder without the roof having changed at all.
        assert 'class="rf' in text
        # THE SAME PIN, ONE LINE APART. The comment directly above says a pin on `class="rf"`
        # exactly would fail every time the roof moved a rung on the weight ladder without the
        # roof changing -- and then the next line pinned `class="ch"` exactly, which is what broke
        # when WP-5.13 gave the stack its own rung. Match the token.
        assert 'class="ch' in text   # tidewater-georgian-careful's own gable-end chimneys (WP-3.3)
        # And WHERE, because "a stack is on the sheet" was true of the version that drew it as a
        # bar floating in the sky at the top-left corner, 3 ft from the gable's front corner and
        # touching no roof (see WP-5.13's report, and OQ 80).
        polys = _stack_polys(text)
        assert len(polys) == 1, "one stack per gable end: the far one stands behind the near one"
        us = [x for x, _y in polys[0]]
        centre_ft = ((min(us) + max(us)) / 2.0 - 46.0) / 24.0
        y_ft = elev["roof_record"]["chimneys"]["positions"][0]["y_ft"]
        assert abs(centre_ft - y_ft) < 0.2, (
            f"stack drawn at {centre_ft:.2f} ft along the gable end; the record says {y_ft}")
        # FROM GRADE TO CAP (Phase 15, WP-15.5). This held the stack's foot to the RAKE, vertex by
        # vertex, from WP-14.6 until Lucas read the drawn Tidewater sheets: "the chimney continuing
        # all the way down to the ground rather than just stopping". The near stack stands outboard
        # of this gable wall, in FRONT of it, so nothing hides it and its foot is the ground the
        # sheet draws; the rake-foot vertices moved to the DRIVEN far-stack test below, which is
        # the one stack a gable face still draws above the roof line. Its top is held to the drawn
        # RIDGE -- the record's height above its own ridge -- so the cornice band the elevation
        # lifts the roof by (V19) cancels, and the foot to the drawn GROUND LINE, which the band
        # does not lift.
        roof = elev["roof_record"]
        ridge = roof["main"]["ridge"]
        c = min(roof["chimneys"]["positions"], key=lambda c: abs(c["y_ft"] - centre_ft))
        gy = float(re.search(r'<line class="gl[^"]*" x1="[^"]+" y1="([\d.]+)"', text).group(1))
        ridge_px = min(y for pts in re.findall(r'<polygon class="rf[^"]*" points="([^"]+)"', text)
                       for y in (float(pt.split(",")[1]) for pt in pts.split()))
        top_px = min(y for _x, y in polys[0])
        foot = [(x, y) for x, y in polys[0] if y > top_px + 1e-6]
        assert len(foot) >= 2 and all(abs(y - gy) < 0.1 for _x, y in foot), (
            f"the near stack's foot stands at {sorted({round(y, 1) for _x, y in foot})} px; the "
            f"ground line is at {gy}")
        assert abs((ridge_px - top_px) / 24.0 - (c["total_height_grade_ft"] - ridge["grade_to_ridge_ft"])) < 0.05
        # IN FRONT OF THE GABLE: drawn after the roof, so the wall and its rake do not paint over it
        assert text.index('<polygon class="ch') > text.index('<polygon class="rf'), (
            "the near stack is drawn before the gable it stands in front of")
        # and the sheet says what it drew and what it could not
        assert "EXTERIOR STACKS DRAWN FROM GRADE TO CAP" in text
        assert "NO RULE IN THIS CORPUS STATES THE BREAST" in text
        assert "ABOVE THE ROOF LINE ONLY" not in text, "a from-grade stack said to stop at the roof"
        # WP-5.13: and the roof is a closed plane now, not a line along its bottom edge.
        assert "<polygon" in text, "the roof is drawn as a polyline again"

    def test_the_stack_the_house_hides_stands_on_the_rake_it_rises_behind(
            self, elevation_module, render_elevation_module, tmp_path):
        """DRIVEN (WP-15.5). Once the near stack is drawn from grade it covers the far one, which
        stands on the same flue line at the other gable, so no shipped sheet draws a stack above
        the roof line any more -- and the rake-foot rule that WP-14.6 wrote (audit F13) would be
        guarded by nothing. Taking the near stack off the record leaves the far one visible from
        this face above the house, and its foot must follow the rake vertex by vertex: the check
        WP-14.6 held the near stack to, moved to the stack it is now true of. The rake is computed
        HERE from the roof's own pitch and ridge line, not from the profile reader the renderer
        uses. Read as a depth below the top, so the cornice band the elevation adds under its
        whole roof (`grade_to_true_eave_in`) cancels and is not asserted either way here."""
        import copy as _copy
        _plan, elev = _tidewater_elevation(elevation_module)
        elev = _copy.deepcopy(elev)
        roof = elev["roof_record"]
        W = elev["footprint"]["width_ft"]
        near = [c for c in roof["chimneys"]["positions"] if c["plan_rect_ft"][0] >= W - 1e-6]
        far = [c for c in roof["chimneys"]["positions"] if c["plan_rect_ft"][2] <= 1e-6]
        assert len(near) == 1 and len(far) == 1, "the premise: one stack outboard of each gable wall"
        roof["chimneys"]["positions"] = far
        out = tmp_path / "tidewater-E-far.svg"
        render_elevation_module.render_elevation(elev, str(out), face="E")
        text = out.read_text()
        polys = _stack_polys(text)
        assert len(polys) == 1, "the far stack, seen above the house"
        ridge = roof["main"]["ridge"]
        slope = roof["main"]["pitch_rise_per_12"] / 12.0
        c = far[0]
        top_px = min(y for _x, y in polys[0])
        foot = [(x, y) for x, y in polys[0] if y > top_px + 1e-6]
        assert len(foot) >= 2, "a foot of at least two vertices, one at each face of the stack"
        for x, y in foot:
            u = (x - 46.0) / 24.0
            rake = ridge["grade_to_ridge_ft"] - abs(u - ridge["position_ft"]) * slope
            want = c["total_height_grade_ft"] - min(rake, c["total_height_grade_ft"])
            assert abs((y - top_px) / 24.0 - want) < 0.03, (
                f"the stack's foot at {u:.2f} ft stands {(y - top_px) / 24.0:.2f} ft below its top; "
                f"the rake there leaves {want:.2f} ft of stack above the roof")
        # the premise that makes the vertex test a test of the RAKE and not of a level line: the
        # two faces of this stack meet the rake at different heights
        us = sorted((x - 46.0) / 24.0 for x, _y in foot)
        assert abs(abs(us[0] - ridge["position_ft"]) - abs(us[-1] - ridge["position_ft"])) > 1.0
        # and the sheet says why this one stops at the roof, and claims no stack from grade
        assert "STACKS DRAWN ABOVE THE ROOF LINE ONLY" in text
        assert "THE HOUSE HIDES THE REST" in text
        assert "FROM GRADE" not in text

    def test_long_face_of_a_side_gable_DOES_show_its_stacks(self, elevation_module, render_elevation_module, tmp_path):
        """REVERSED AND REWRITTEN 28 Aug 2026, and the reversal is a ruling rather than a slip.

        This test asserted `'class="ch"' not in text` — "the long faces should not draw a chimney
        that is not actually in that wall's plane", which was WP-3.3's finding and was right while
        `roof.py`'s long-face silhouette stopped at the eave: with no roof surface modelled there
        was nothing to say which part of a 47 ft stack clears the roof, so drawing any of it would
        have been inventing. OQ 80 closed that (WP-5.13): `elevation_profile` carries the near roof
        PLANE on a long face, because parallel projection fills the band from eave to ridge, and
        the front elevation draws both end stacks — which the kit calls "visible from a mile away
        and conclusive against New England".

        It was left green by an unrelated accident: the stack gained a weight rung, so the emitted
        class became `class="ch w-prof"` and the exact-string pin stopped matching anything. A
        NEGATIVE assertion whose selector breaks inverts into a tautology, and this one then sat
        in the same suite as `test_the_front_elevation_shows_both_end_stacks`, which asserts the
        opposite. Only the broken selector kept them from colliding. The audit that found it also
        found the identical stale pin fixed one test earlier in the same diff and not here.

        RE-CUT 27 Sep 2026 (Phase 15, WP-15.5): the stacks stand on the GROUND now. See below."""
        import json as _json
        plan, elev = _tidewater_elevation(elevation_module)
        out = tmp_path / "tidewater-S.svg"
        render_elevation_module.render_elevation(elev, str(out), face="S")
        text = out.read_text()
        polys = _stack_polys(text)
        assert len(polys) == 2, f"two gable-end stacks on the front, got {len(polys)}"
        boxes = sorted((min(x for x, _y in p), min(y for _x, y in p), max(x for x, _y in p),
                        max(y for _x, y in p)) for p in polys)
        assert boxes[1][0] - boxes[0][0] > 1000, "they are at opposite ends of the front, not stacked together"
        # FROM GRADE TO CAP, at the width the record states (Phase 15, WP-15.5). From WP-5.11 this
        # asserted ONLY THE PART ABOVE THE ROOF LINE -- first above the ridge, then (WP-14.6,
        # audit F3) above the rake at the stack's own depth -- on the evidence argument that no
        # record states the BREAST at an exterior stack's foot. Lucas read the drawn front: "the
        # chimney continuing all the way down to the ground rather than just stopping". An exterior
        # end stack stands wholly outboard of its gable wall, so nothing of the house hides it from
        # this face; the evidence argument decides its WIDTH (the stack's own square, the least the
        # mass can be) and not its height. Each foot is held to the ground line the sheet DRAWS and
        # each top to the drawn RIDGE, by the record's own height above its own ridge -- read off
        # the ink, so the cornice band the elevation lifts the roof by (V19) cancels.
        roof = elev["roof_record"]
        ridge = roof["main"]["ridge"]
        gl = re.search(r'<line class="gl[^"]*" x1="([\d.-]+)" y1="([\d.]+)" x2="([\d.-]+)"', text)
        gx1, gy, gx2 = float(gl.group(1)), float(gl.group(2)), float(gl.group(3))
        roof_pts = [tuple(float(v) for v in pt.split(","))
                    for pts in re.findall(r'<polygon class="rf[^"]*" points="([^"]+)"', text)
                    for pt in pts.split()]
        ridge_px = min(y for _x, y in roof_pts)
        frame = _json.loads(re.search(r"data-frame='([^']+)'", text).group(1))["plates"][0]
        ox = frame["origin_px"][0]
        W = elev["footprint"]["width_ft"]
        for c, (x0, y0, x1, y1) in zip(sorted(roof["chimneys"]["positions"], key=lambda c: c["x_ft"]), boxes):
            assert c.get("side") == "exterior", "the premise: these stacks stand outboard"
            sq = c["plan_rect_ft"]
            assert abs(y1 - gy) < 0.1, f"a stack's foot at {y1} px; the ground line is at {gy} px"
            assert abs((ridge_px - y0) / 24.0 - (c["total_height_grade_ft"] - ridge["grade_to_ridge_ft"])) < 0.05
            assert abs((x1 - x0) / 24.0 * 12.0 - elev["chimney_stack_plan_in"]) < 0.1, (
                f"stack drawn {(x1 - x0) / 24 * 12:.2f} in wide; the record says "
                f"{elev['chimney_stack_plan_in']} in")
            # WHERE along the face, read back through the frame the sheet states: outboard of the
            # wall, on the square the placement seats
            assert abs((x0 - ox) / 24.0 - sq[0]) < 0.01 and abs((x1 - ox) / 24.0 - sq[2]) < 0.01, (
                ((x0 - ox) / 24.0, (x1 - ox) / 24.0), sq)
            # the ground line runs past it: a stack standing at the end of a line that stops short
            # of it stands on nothing
            assert gx1 < x0 - 24.0 and gx2 > x1 + 24.0, (gx1, gx2, x0, x1)
        # ON THE CANVAS: the face shifts right by the stack's overhang, so nothing -- the stack or
        # the ground line past it -- is drawn off the sheet's left edge
        vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', text).group(1).split()]
        assert gx1 >= vb[0] and boxes[0][0] >= vb[0] and boxes[1][2] <= vb[0] + vb[2]
        # BEHIND THE FRONT: an exterior stack stands at the stack's own depth, 31 ft back here, and
        # the front's wall, its bands and its cornice are nearer the eye, so they are drawn after it
        first_stack = text.index('<polygon class="ch')
        for mark in ('<rect class="wf"', '<rect class="wt', '<polygon class="rf'):
            assert first_stack < text.index(mark), f"a stack drawn over the front's {mark}"
        # THE PREMISE THAT ORDER RESTS ON: the roof as recorded models no rake overhang, so its
        # drawn plane stops at the wall's ends and overlaps no outboard stack. Were one ever
        # modelled, a stack IN FRONT OF the ridge would stand in front of the roof behind it and
        # the order above would be wrong for it -- which is what this line exists to announce.
        assert min(x for x, _y in roof_pts) >= ox - 0.1 and max(x for x, _y in roof_pts) <= ox + W * 24.0 + 0.1, (
            "the long-face roof now reaches past the gable wall: decide the stack's order by its "
            "depth against the ridge before trusting the draw order above")
        assert text.count("EXTERIOR STACKS DRAWN FROM GRADE TO CAP") == 1
        assert "ABOVE THE ROOF LINE ONLY" not in text

    def test_an_interior_stack_is_hidden_up_to_the_highest_roof_in_front_of_it(
            self, elevation_module, render_elevation_module):
        """DRIVEN (WP-14.6). Every stack on every shipped plan stands OUTSIDE its gable wall, so
        `_stack_outline`'s interior branch -- a stack coming up through the roof, hidden by the
        plane between the eave and itself up to that plane's highest point -- is reached by no
        sheet, and a mutation ignoring the hider left the whole suite green. Two stacks on the
        Tidewater roof, one each side of the ridge, each seen from the face the ridge stands in
        front of: the foot is the RIDGE, computed here from the roof's own ridge record and not
        from the profile the renderer reads. And from the other face, where nothing higher stands
        in front, the foot is the rake at the stack's own near face."""
        _plan, elev = _tidewater_elevation(elevation_module)
        roof, fp = elev["roof_record"], elev["footprint"]
        ridge = roof["main"]["ridge"]
        rp, rh = ridge["position_ft"], ridge["grade_to_ridge_ft"]
        slope = roof["main"]["pitch_rise_per_12"] / 12.0
        rake = lambda t: rh - abs(t - rp) * slope            # noqa: E731
        top = rh + 8.0
        north = {"plan_rect_ft": [20.0, rp + 6.0, 21.833, rp + 7.833], "side": "interior",
                 "total_height_grade_ft": top}
        south = {"plan_rect_ft": [20.0, rp - 7.833, 21.833, rp - 6.0], "side": "interior",
                 "total_height_grade_ft": top}
        cases = (
            # (stack, face, the foot: the highest roof between that face's eave and the stack)
            (north, "S", rh),                                  # the ridge stands in front
            (south, "N", rh),
            (north, "N", rake(north["plan_rect_ft"][3])),      # only its own slope in front
            (south, "S", rake(south["plan_rect_ft"][1])),
        )
        for c, face, want in cases:
            got = render_elevation_module._stack_outline(face, c, roof, fp)
            assert "outline" in got, (face, got)
            foot = min(h for _u, h in got["outline"])
            assert abs(foot - want) < 0.01, (
                f"an interior stack at y {c['plan_rect_ft'][1]:.2f}-{c['plan_rect_ft'][3]:.2f} ft on "
                f"the {face} face: foot drawn at {foot:.2f} ft, the roof in front of it stands to "
                f"{want:.2f}")
        # the premise that makes the first two cases discriminate: the ridge stands well above
        # the stack's own slope, so a renderer ignoring what is in front draws the foot lower
        assert rh - rake(north["plan_rect_ft"][3]) > 3.0

    def test_unjudged_ridge_renders_a_flat_roofline_not_an_invented_pitch(self, elevation_module, render_elevation_module, tmp_path):
        plan = load_plan("spec-builder-colonial")
        elev = elevation_module.build_elevation(plan)
        assert elev["roof_record"]["main"].get("pitch_rise_per_12") is None   # colonial-revival carries no migrated pitch constraint (WP-3.3)
        out = tmp_path / "spec-builder-elevation.svg"
        render_elevation_module.render_elevation(elev, str(out))
        text = out.read_text()
        assert text.startswith("<svg")


def test_the_datums_sentence_is_the_conversion_the_code_makes(elevation_module):
    """WP-14.6, audit F14. The elevation record's `datum.conversion` was written out by hand as
    "u = clear span + t - along on N and W" and went on saying so after WP-13.3 unmirrored every
    face, so a reader converting by the record's own words put each N and W opening at the wrong
    end of its face. The sentence is read off `FACE_MIRRORED` now; here each face's words are held
    to what `face_u_ft` actually returns, whichever way the table is set. (Since WP-16.3 the
    mirrored clause names the face's OUTSIDE WIDTH, the axis the flip reflects about; on these
    round figures it is the clear span plus two walls exactly.)"""
    import re as _re
    EL = elevation_module
    words = EL.face_u_words()
    for face in EL.FACES:
        rule = next(r for r in words.split(";") if _re.search(r"\b%s\b" % face, r))
        mirrored = "outside width" in rule
        assert mirrored == EL.FACE_MIRRORED[face], (face, words)
        got = EL.face_u_ft(face, 10.0, 40.0, 30.0, 1.0)
        span = 40.0 if face in ("S", "N") else 30.0
        assert got == ((span + 1.0 - 10.0) if mirrored else 11.0), (face, got, words)
    _plan, elev = _tidewater_elevation(elevation_module)
    assert elev["datum"]["conversion"] == words
