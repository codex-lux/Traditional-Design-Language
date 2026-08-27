"""Pins WP-3.3, roof geometry -- see docs/structure.md's roof section and PLAN-OF-ACTION.md's own
WP-3.3 acceptance text ('Roof plan SVG for both shipped plans; wing ridges step down; pitch
within the style band; chimney positions satisfy the Tidewater constraint').

Neither shipped reference plan actually carries a dependency-and-hyphen wing, a gambrel roof, or
a dormer -- both are a plain side-gable four-over-four. Where the acceptance text names a
behaviour those plans do not exercise (the wing step-down, the Cape eave check, the gambrel
break, dormer rhythm), this file pins it two ways: a direct unit test against hand-built or
style-substituted input (exercising the real code path), plus an honest 'not applicable' check
against the actual shipped plans -- the same disclosure discipline WP-3.1's framing_basis finding
and WP-2.2's dining-room finding both used, rather than silently claiming end-to-end coverage a
plan does not actually provide.
"""
import json
import math
import os

from conftest import ROOT, load_plan


def _tidewater_section(roof_module, style=None, groupings=None, roof_form=None):
    plan = load_plan("tidewater-georgian-careful")
    if style is not None:
        plan["style"] = style
    if groupings is not None:
        plan["groupings"] = groupings
    if roof_form is not None:
        plan["declared"]["roof_form"] = roof_form
    section = roof_module.ST.build_section(plan)
    return plan, section


class TestRoofForm:
    def test_declared_form_is_used(self, roof_module):
        plan = load_plan("tidewater-georgian-careful")
        massing = roof_module._massing(plan["massing"])
        form, note = roof_module.roof_form_for(plan, massing)
        assert form == "side-gable"
        assert note is None   # declared and matches the massing's own roof_default -- no note needed

    def test_undeclared_falls_back_to_massing_default_with_a_note(self, roof_module):
        plan = load_plan("tidewater-georgian-careful")
        plan["declared"] = {k: v for k, v in plan["declared"].items() if k != "roof_form"}
        massing = roof_module._massing(plan["massing"])
        form, note = roof_module.roof_form_for(plan, massing)
        assert form == massing["roof_default"][0]
        assert note is not None and "No roof_form declared" in note

    def test_declared_form_outside_the_massing_default_list_is_noted_not_rejected(self, roof_module):
        plan = load_plan("tidewater-georgian-careful")
        plan["declared"]["roof_form"] = "mansard"   # not in four-over-four's own roof_default
        massing = roof_module._massing(plan["massing"])
        form, note = roof_module.roof_form_for(plan, massing)
        assert form == "mansard"
        assert note is not None and "not in massing" in note


class TestMainRoofSideGable:
    def test_reuses_structures_own_eave_and_ridge_height(self, roof_module):
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        assert main["grade_to_eave_ft"] == section["roof"]["grade_to_eave_ft"]
        assert main["ridge"]["grade_to_ridge_ft"] == section["roof"]["grade_to_ridge_ft"]

    def test_ridge_runs_the_full_width_axis_x(self, roof_module):
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        fp = section["footprint"]
        assert main["ridge"]["axis"] == "x"
        assert main["ridge"]["from_ft"] == 0.0
        assert main["ridge"]["to_ft"] == fp["width_ft"]

    def test_pitch_matches_the_style_constraint_band(self, roof_module):
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        assert main["pitch_source"] == "tidewater-georgian.c02"
        assert 7.0 <= main["pitch_rise_per_12"] <= 9.0


class TestMainRoofHip:
    def test_hip_ridge_height_matches_the_single_pitch_estimate(self, roof_module):
        """A symmetric hip and a symmetric gable roof over the same footprint and pitch share
        the same ridge HEIGHT -- only the outline differs. Confirms main_roof() reuses
        structure.py's number rather than silently recomputing a different one for hip."""
        plan, section = _tidewater_section(roof_module, roof_form="hip")
        main = roof_module.main_roof(plan, section, plan["style"])
        assert main["ridge"]["grade_to_ridge_ft"] == section["roof"]["grade_to_ridge_ft"]

    def test_hip_ridge_is_shorter_than_the_gable_ridge_by_the_depth(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="hip")
        main = roof_module.main_roof(plan, section, plan["style"])
        fp = section["footprint"]
        ridge_len = main["ridge"]["to_ft"] - main["ridge"]["from_ft"]
        assert math.isclose(ridge_len, fp["width_ft"] - fp["depth_ft"], rel_tol=1e-6)

    def test_four_hip_lines_run_corner_to_ridge_endpoint(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="hip")
        main = roof_module.main_roof(plan, section, plan["style"])
        assert len(main["hip_lines"]) == 4
        fp = section["footprint"]
        corners = {(0.0, 0.0), (fp["width_ft"], 0.0), (fp["width_ft"], fp["depth_ft"]), (0.0, fp["depth_ft"])}
        line_starts = {(h["x1"], h["y1"]) for h in main["hip_lines"]}
        assert line_starts == corners


class TestMainRoofGambrel:
    def test_recomputes_a_ridge_height_that_differs_from_the_single_pitch_estimate(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="gambrel")
        main = roof_module.main_roof(plan, section, plan["style"])
        assert main["ridge"]["grade_to_ridge_ft"] != section["roof"]["grade_to_ridge_ft"]
        assert main["note"] is not None and "Recomputed" in main["note"]

    def test_prefers_a_styles_own_migrated_gambrel_constraint_over_the_family_default(self, roof_module):
        geo = roof_module._style_gambrel_geometry("dutch-colonial-american")
        assert geo["lower_source"] == "dutch-colonial-american.c03"
        assert geo["lower_slope_deg"] == 66.0   # midpoint of that constraint's own 60-72 band

    def test_falls_back_to_the_family_default_band_for_a_style_with_no_migrated_constraint(self, roof_module):
        geo = roof_module._style_gambrel_geometry("tidewater-georgian")
        assert geo["lower_source"].startswith("default")
        assert geo["lower_slope_deg"] == roof_module.GAMBREL_LOWER_SLOPE_DEFAULT_DEG

    def test_gambrel_break_check_passes_on_this_files_own_computed_geometry(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="gambrel")
        main = roof_module.main_roof(plan, section, plan["style"])
        gb = roof_module.gambrel_break_check(main)
        assert gb["applicable"] is True
        assert gb["diff_ok"] is True and gb["break_ok"] is True

    def test_gambrel_break_check_not_applicable_to_a_gable_roof(self, roof_module):
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        assert roof_module.gambrel_break_check(main)["applicable"] is False


class TestMainRoofCrossGable:
    def test_cross_ridge_is_centred_and_shorter_than_the_bay_module_or_footprint(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="cross-gable")
        main = roof_module.main_roof(plan, section, plan["style"])
        cross = main["cross"]
        assert cross["width_ft"] <= section["footprint"].get("bay_module_ft", 10.0)
        assert cross["grade_to_ridge_ft"] > main["grade_to_eave_ft"]
        assert "no valley geometry" in cross["note"]


class TestUnmodelledForm:
    def test_unknown_roof_form_leaves_ridge_unjudged_not_invented(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="catslide")
        main = roof_module.main_roof(plan, section, plan["style"])
        assert "ridge" not in main
        assert main["grade_to_eave_ft"] is not None
        assert "not modelled" in main["note"]


class TestChimneyPositions:
    def test_tidewater_gable_end_chimneys_satisfy_its_own_constraint(self, roof_module):
        """The acceptance text's own literal case: 'chimney positions satisfy the Tidewater
        constraint' -- tidewater-georgian.c01, chimney_height_above_ridge_ft >= 6."""
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        ch = roof_module.chimney_positions(plan, plan["style"], section, main)
        assert ch["applicable"] is True
        assert len(ch["positions"]) == 2
        assert ch["style_check"]["constraint_id"] == "tidewater-georgian.c01"
        assert ch["style_check"]["ok"] is True
        for pos in ch["positions"]:
            assert pos["height_above_ridge_ft"] >= 6.0

    def test_chimneys_sit_on_the_two_gable_end_walls(self, roof_module):
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        ch = roof_module.chimney_positions(plan, plan["style"], section, main)
        fp = section["footprint"]
        xs = sorted(p["x_ft"] for p in ch["positions"])
        assert xs == [0.0, fp["width_ft"]]

    def test_hip_form_flags_no_gable_end_wall_rather_than_placing_wrongly(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="hip")
        main = roof_module.main_roof(plan, section, plan["style"])
        ch = roof_module.chimney_positions(plan, plan["style"], section, main)
        assert ch["positions"] == []
        assert ch["applicable"] is True
        assert "no full gable-end wall" in ch["note"]

    def test_falls_back_to_the_massings_hearth_field_when_the_kit_slot_is_empty(self, roof_module, corpus):
        """colonial-revival's own chimney kit slot is status: empty -- spec-builder-colonial.json's
        style. The massing (four-over-four, hearth 'gable-end-paired') is the fallback source."""
        assert corpus["kits"]["colonial-revival"]["slots"]["chimney"]["status"] == "empty"
        plan = load_plan("spec-builder-colonial")
        section = roof_module.ST.build_section(plan)
        main = roof_module.main_roof(plan, section, plan["style"])
        ch = roof_module.chimney_positions(plan, plan["style"], section, main)
        assert ch["source"] is not None and "hearth" in ch["source"]

    def test_no_source_at_all_is_unjudged(self, roof_module):
        plan, section = _tidewater_section(roof_module)
        plan["massing"] = "no-such-massing-xyz"
        main = roof_module.main_roof(plan, section, plan["style"])
        ch = roof_module.chimney_positions(plan, "no-such-style-xyz", section, main)
        assert ch["applicable"] is False
        assert ch["source"] is None


class TestWingStepDown:
    def test_not_applicable_without_the_grouping(self, roof_module):
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        w = roof_module.wing_step_down(plan, section, main)
        assert w["applicable"] is False

    def test_band_is_read_from_the_grouping_file_not_hardcoded(self, roof_module):
        """Regression precedent from structure.py's graduation_check() bug: the 0.6-0.8 band
        must come from groupings/dependency-and-hyphen.json's own internal_rules, not a copy."""
        grp = json.load(open(os.path.join(ROOT, "groupings", "dependency-and-hyphen.json")))
        ridge_rule = next(r for r in grp["internal_rules"] if r.get("test", "").startswith("dependency_ridge_ft"))
        band = roof_module._parse_prose_between(ridge_rule["test"])
        assert band == (0.6, 0.8)

    def test_wing_ridge_steps_down_inside_the_bands_own_band(self, roof_module):
        """The acceptance text's own literal case: 'wing ridges step down'."""
        plan, section = _tidewater_section(roof_module, groupings=["dependency-and-hyphen"])
        main = roof_module.main_roof(plan, section, plan["style"])
        w = roof_module.wing_step_down(plan, section, main)
        assert w["applicable"] is True and w["computed"] is True
        assert w["wing_ridge_grade_ft"] < w["main_ridge_grade_ft"]
        assert w["ratio_band"][0] <= w["ratio"] <= w["ratio_band"][1]
        assert w["ok"] is True

    def test_hyphen_length_is_read_from_the_grouping_too(self, roof_module):
        plan, section = _tidewater_section(roof_module, groupings=["dependency-and-hyphen"])
        main = roof_module.main_roof(plan, section, plan["style"])
        w = roof_module.wing_step_down(plan, section, main)
        assert 12.0 <= w["hyphen_length_ft"] <= 20.0

    def test_neither_shipped_plan_actually_carries_the_grouping(self):
        """Honest disclosure, not a bug: the wing step-down path above is real and tested, but
        does not run end-to-end against either shipped reference plan."""
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = load_plan(name)
            assert "dependency-and-hyphen" not in (plan.get("groupings") or [])


class TestCapeEaveCheck:
    def test_not_applicable_to_a_non_cape_style(self, roof_module):
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        assert roof_module.cape_eave_check(plan["style"], section, main)["applicable"] is False

    def test_fatal_styles_are_read_from_the_fault_records_own_severity_by_style(self, roof_module):
        fault = json.load(open(os.path.join(ROOT, "faults", "raised-cape-eave.json")))
        fatal = {e["style"] for e in fault["severity_by_style"] if e["severity"] == "fatal"}
        assert fatal == {"cape-cod-colonial", "cape-cod-revival"}

    def test_a_real_two_storey_georgian_eave_fails_the_cape_band(self, roof_module):
        """Style-substitution case: this file's own storey heights (a full two-storey masonry
        Georgian) obviously blow through a Cape's tight 96-114in eave band when the style is
        swapped to cape-cod-colonial -- confirms the check actually catches a violation."""
        plan, section = _tidewater_section(roof_module, style="cape-cod-colonial")
        main = roof_module.main_roof(plan, section, plan["style"])
        cape = roof_module.cape_eave_check(plan["style"], section, main)
        assert cape["applicable"] is True and cape["computed"] is True
        assert cape["ok"] is False

    def test_a_genuine_cape_eave_height_passes(self, roof_module):
        section = {"footprint": {"width_ft": 30.0, "depth_ft": 24.0, "bay_module_ft": 10.0},
                   "storeys": [{"index": 0, "grade_to_floor_ft": 2.0, "storey_height_ft": 8.0}],
                   "roof": {"grade_to_eave_ft": 10.5}}
        main = {"grade_to_eave_ft": 10.5, "pitch_rise_per_12": 10.5, "form": "side-gable"}
        cape = roof_module.cape_eave_check("cape-cod-colonial", section, main)
        assert cape["ok"] is True and cape["pitch_ok"] is True


class TestDormerRhythm:
    """REWRITTEN 27 Aug 2026 (WP-5.9), and the rewrite is the finding.

    These three tests reached dormer_rhythm_check by writing `plan["declared_dormers"] = [...]`
    -- a key no schema ever defined, that no record in the corpus carried, and that the function
    had invented for itself because no field authored a dormer. So the tests passed against a
    code path nothing could reach, and the check returned not-applicable on every real plan. A
    guard that constructs its own input out of thin air proves the arithmetic and nothing about
    the corpus; this is the same shape as WP-5.7's TestSegTo, which pinned the control points of
    curves that had degenerated to straight lines.

    `declared.dormer` exists now, so they are written against it -- including the state the old
    ones could not express at all, which is a house that STATES it has none.
    """

    def test_a_record_that_says_nothing_is_not_a_record_that_says_none(self, roof_module):
        """The distinction the whole field exists for. Both shipped plans now DECLARE none, so
        the silent state has to be built by removing the declaration."""
        plan, section = _tidewater_section(roof_module)
        plan["declared"].pop("dormer", None)
        main = roof_module.main_roof(plan, section, plan["style"])
        d = roof_module.dormer_rhythm_check(plan, section, main)
        assert d["applicable"] is False and d["stated"] is False
        assert "dormer_count" not in d, "a house nobody asked about has no count, not a count of 0"

    def test_a_stated_none_is_judged_and_reports_no_ratio(self, roof_module):
        """A measured zero: applicable, stated, count 0 -- and `ok` is None, not True. Zero
        dormers is not a rhythm that passed; it is no rhythm. Reporting True here is how a
        refusal becomes a pass, which is the collapse this corpus least survives."""
        plan, section = _tidewater_section(roof_module)
        assert plan["declared"]["dormer"] == "none"      # as shipped
        main = roof_module.main_roof(plan, section, plan["style"])
        d = roof_module.dormer_rhythm_check(plan, section, main)
        assert d["applicable"] is True and d["stated"] is True
        assert d["dormer_count"] == 0
        assert d["ratio"] is None and d["ok"] is None

    def test_a_footprint_with_no_bay_module_leaves_the_count_UNJUDGED(self, roof_module):
        """REWRITTEN 28 Aug 2026 by this package's own adversarial audit, and the rewrite is the
        finding. The two tests here computed the expected bay count with `int(width_ft //
        (bay_module_ft or 10.0))` — `roof.py:509` copied verbatim into the test — and
        `bay_module_ft` is ABSENT on this footprint, so both sides fell back to the same invented
        10.0 and the assertion could not fail.

        It was hiding a live cross-layer disagreement. The roof got 6 bays from that constant; the
        facade pack lays this front out as FIVE. At `{"count": 6}` the roof reported `ratio 1.0,
        ok True` while `plan_check` convicted the same house on 5 of 6 centred. Two records built
        from different rules that nothing compared — OQ 85's own thesis, one layer up, shipped
        inside the package that closed OQ 85. The roof no longer invents a module: the bay rhythm
        belongs to the facade layer, and where the footprint states none this is unjudged."""
        plan, section = _tidewater_section(roof_module)
        assert not section["footprint"].get("bay_module_ft"), (
            "this footprint now states a bay module — the premise of this test has changed")
        plan["declared"]["dormer"] = {"count": 6}
        main = roof_module.main_roof(plan, section, plan["style"])
        d = roof_module.dormer_rhythm_check(plan, section, main)
        assert d["applicable"] is True and d["dormer_count"] == 6
        assert d["bay_count"] is None and d["ratio"] is None and d["ok"] is None, (
            "the roof answered from a bay module the footprint does not state")
        assert "facade layer" in d["note"]

    def test_it_judges_where_the_footprint_actually_states_a_module(self, roof_module):
        """Not merely unjudged everywhere — the check still works on a record that carries the
        figure. Asserted with a module that makes the answer FALSE, so the test cannot pass by
        the code always returning None."""
        import copy
        plan, section = _tidewater_section(roof_module)
        section = copy.deepcopy(section)
        section["footprint"]["bay_module_ft"] = 12.516      # 62.58 / 5 -> four whole bays
        plan["declared"]["dormer"] = {"count": 6}
        main = roof_module.main_roof(plan, section, plan["style"])
        d = roof_module.dormer_rhythm_check(plan, section, main)
        assert d["bay_count"] == 4 and d["on_bay_count"] == 4
        assert d["ok"] is False and d["ratio"] < 1.0

    def test_the_roof_and_the_elevation_agree_or_the_roof_declines(self, roof_module):
        """The invariant the circular version could not state. Wherever the roof DOES publish a
        bay count, it must be the one the facade layer lays out — otherwise the corpus holds two
        answers to one question and the fault layer picks the other one."""
        import json as _j
        import os as _os
        e = __import__("elevation")
        root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = _j.load(open(_os.path.join(root, "plans", f"{pid}.json")))
            section = roof_module.ST.build_section(plan)
            p2 = dict(plan, declared=dict(plan["declared"], dormer={"count": 3}))
            main = roof_module.main_roof(p2, section, p2["style"])
            d = roof_module.dormer_rhythm_check(p2, section, main)
            if d.get("bay_count") is None:
                continue                       # declined, which is the honest half
            elev = e.build_elevation(p2)
            front = elev["faces"][elev["entrance_face"]]["count"]
            assert d["bay_count"] == front, (
                f"{pid}: the roof says {d['bay_count']} bays and the elevation lays out {front}")

    def test_neither_shipped_plan_has_an_attic_a_dormer_would_light(self):
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = load_plan(name)
            assert [lv["id"] for lv in plan["levels"]] == ["ground", "upper"]   # no attic level


class TestRoofOutlineAndElevationProfiles:
    def test_outline_has_four_eave_lines_and_a_ridge(self, roof_module):
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        outline = roof_module.roof_outline(section, main)
        kinds = [l["kind"] for l in outline]
        assert kinds.count("eave") == 4
        assert kinds.count("ridge") == 1

    def test_hip_outline_adds_four_hip_lines(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="hip")
        main = roof_module.main_roof(plan, section, plan["style"])
        outline = roof_module.roof_outline(section, main)
        assert [l["kind"] for l in outline].count("hip") == 4

    def test_gable_end_face_is_a_triangle_peaking_at_ridge_height(self, roof_module):
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        profile = roof_module.elevation_profile(section, main, "E")   # E/W are the gable ends on side-gable
        heights = [p[1] for p in profile]
        assert len(profile) == 3
        assert heights[1] == main["ridge"]["grade_to_ridge_ft"]
        assert heights[0] == heights[2] == main["grade_to_eave_ft"]

    def test_long_face_of_a_simple_gable_reaches_the_ridge(self, roof_module):
        """REWRITTEN 27 Aug 2026 (WP-5.9). This test asserted the opposite -- that the long face is
        a flat eave line of two points -- and it was pinning a bug.

        The code it guarded carried the comment "ridge is behind the near roof plane, not
        visible", which is a PERSPECTIVE argument applied to an ORTHOGRAPHIC projection. In
        parallel projection the near plane slopes away from the viewer and maps to a full-width
        band from the eave up to the ridge; the ridge is the top edge of the drawing, at its true
        height. Every front elevation this corpus drew of a side-gable house was short by the
        whole roof -- 14.22 ft on the Tidewater reference plan.

        The test passed for three work packages because it agreed with the code. A guard written
        from the same misunderstanding as the thing it guards is not a guard, and this is the
        second one of those found in two days (see tests/test_profiles.py's receding member)."""
        plan, section = _tidewater_section(roof_module)
        main = roof_module.main_roof(plan, section, plan["style"])
        profile = roof_module.elevation_profile(section, main, "S")
        assert len(profile) == 4, "a roof plane is an area, not a line along its bottom edge"
        heights = [p[1] for p in profile]
        assert heights[0] == heights[-1] == main["grade_to_eave_ft"]
        assert heights[1] == heights[2] == main["ridge"]["grade_to_ridge_ft"]
        # and it is a RECTANGLE: the ridge runs the full width, unlike a hip's, which runs in
        xs = [p[0] for p in profile]
        assert xs[1] == xs[0] and xs[2] == xs[3], "a side-gable front is not a trapezoid"

    def test_hip_long_face_is_a_trapezoid(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="hip")
        main = roof_module.main_roof(plan, section, plan["style"])
        profile = roof_module.elevation_profile(section, main, "S")
        heights = [p[1] for p in profile]
        assert len(profile) == 4
        assert heights[0] == heights[-1] == main["grade_to_eave_ft"]
        assert heights[1] == heights[2] == main["ridge"]["grade_to_ridge_ft"]

    def test_gambrel_long_face_shows_the_break(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="gambrel")
        main = roof_module.main_roof(plan, section, plan["style"])
        profile = roof_module.elevation_profile(section, main, "S")
        heights = [p[1] for p in profile]
        assert len(profile) == 4
        assert heights[1] == heights[2] == main["gambrel"]["break_grade_to_ft"]

    def test_unjudged_ridge_gives_a_flat_profile_on_every_face(self, roof_module):
        plan, section = _tidewater_section(roof_module, roof_form="catslide")
        main = roof_module.main_roof(plan, section, plan["style"])
        for wall in roof_module.FACES:
            profile = roof_module.elevation_profile(section, main, wall)
            assert len(profile) == 2
            assert profile[0][1] == profile[1][1] == main["grade_to_eave_ft"]


class TestBuildRoofEndToEnd:
    """Exercises the acceptance criterion's own named plans."""

    def test_tidewater_plan_pitch_within_the_style_band(self, roof_module):
        plan = load_plan("tidewater-georgian-careful")
        roof = roof_module.build_roof(plan)
        assert "error" not in roof
        assert 7.0 <= roof["main"]["pitch_rise_per_12"] <= 9.0

    def test_tidewater_plan_chimneys_satisfy_the_style_constraint(self, roof_module):
        plan = load_plan("tidewater-georgian-careful")
        roof = roof_module.build_roof(plan)
        assert roof["chimneys"]["style_check"]["ok"] is True

    def test_both_shipped_plans_produce_a_complete_roof_record(self, roof_module):
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = load_plan(name)
            roof = roof_module.build_roof(plan)
            assert "error" not in roof
            assert roof["main"]["grade_to_eave_ft"] > 0
            assert len(roof["outline"]) >= 5   # 4 eave lines + at least a ridge
            assert set(roof["elevation_profiles"].keys()) == set(roof_module.FACES)


class TestRenderRoof:
    def test_both_shipped_plans_render_a_valid_svg(self, roof_module, render_roof_module, tmp_path):
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = load_plan(name)
            roof = roof_module.build_roof(plan)
            out = tmp_path / f"{name}-roof.svg"
            render_roof_module.render_roof(roof, str(out))
            text = out.read_text()
            assert text.startswith("<svg")
            assert "ROOF PLAN" in text

    def test_hip_roof_renders_hip_lines(self, roof_module, render_roof_module, tmp_path):
        plan = load_plan("tidewater-georgian-careful")
        plan["declared"]["roof_form"] = "hip"
        roof = roof_module.build_roof(plan)
        out = tmp_path / "hip-roof.svg"
        render_roof_module.render_roof(roof, str(out))
        assert 'class="hp"' in out.read_text()

    def test_chimneys_render_as_markers(self, roof_module, render_roof_module, tmp_path):
        plan = load_plan("tidewater-georgian-careful")
        roof = roof_module.build_roof(plan)
        out = tmp_path / "chimneys.svg"
        render_roof_module.render_roof(roof, str(out))
        assert 'class="chm"' in out.read_text()
