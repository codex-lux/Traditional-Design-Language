"""Pins mcp_server/core.py's 'unjudged is not passed' guarantee — the
operating rule every checker and validator in this project must honour
(PLAN-OF-ACTION.md section 1): distinguish 'evaluated and failed', 'evaluated
and passed', and 'could not evaluate', and never collapse the third into the
second.
"""


class TestUnjudgedIsNotPassed:
    def test_missing_variable_returns_unjudged_not_passed(self, core_module):
        result = core_module.check_measurements(
            {"nonexistent_variable_xyz": 42}, style="georgian-colonial-american"
        )
        assert result["faults_present"] == []
        assert result["summary"]["present"] == 0
        assert result["summary"]["clear"] == 0
        assert result["summary"]["unjudged"] > 0
        assert result["could_not_judge"], "expected specific faults listed as could-not-judge"

    def test_relevant_passing_measurement_is_clear_not_unjudged(self, core_module):
        """Contrast case: a correctly-sized shutter (leaf width = half the
        sash width, at least 0.48) must show up as 'clear', not 'unjudged'."""
        result = core_module.check_measurements(
            {"shutter_leaf_width_in": 16, "window_opening_width_in": 32},
            style="colonial-revival",
        )
        assert result["summary"]["clear"] > 0

    def test_failing_measurement_is_present_not_unjudged(self, core_module):
        """The half-width-shutter case from the shipped spec-builder plan:
        0.33 against a required 0.48 must be 'present' (i.e. the fault fired),
        not merely 'unjudged'."""
        result = core_module.check_measurements(
            {"shutter_leaf_width_in": 10.67, "window_opening_width_in": 32},
            style="colonial-revival",
        )
        assert result["summary"]["present"] > 0
        names = [f["fault"] for f in result["faults_present"]]
        assert "shutter-half-width-leaf" in names


class TestCheckStyleConstraints:
    """WP-1.2: mcp_server/core.py's check_style_constraints -- the same present/clear/unjudged
    guarantee as check_measurements above, applied to a style's own migrated constraints
    (schema/constraint.schema.json) instead of the element-level fault corpus, so an MCP caller
    can evaluate a style's rules without building a whole plan record."""

    def test_unknown_style_reports_error_not_a_crash(self, core_module):
        result = core_module.check_style_constraints("not-a-real-style", {})
        assert "error" in result

    def test_no_measurements_leaves_testable_constraints_unjudged(self, core_module):
        result = core_module.check_style_constraints("georgian-colonial-american", {})
        assert result["summary"]["unjudged"] == 4
        assert result["summary"]["present"] == 0
        assert result["summary"]["clear"] == 0
        # c03 (scope: judgment) has no test at all -- it belongs under judgment_only, not
        # could_not_judge, since there's nothing to "not yet" evaluate.
        assert any(c["id"] == "georgian-colonial-american.c03" for c in result["judgment_only"])

    def test_passing_and_failing_roof_pitch(self, core_module):
        ok = core_module.check_style_constraints(
            "georgian-colonial-american", {"roof_pitch_rise_per_12": 9})
        assert any(c["id"] == "georgian-colonial-american.c02" for c in ok["constraints_clear"])
        bad = core_module.check_style_constraints(
            "georgian-colonial-american", {"roof_pitch_rise_per_12": 6})
        hit = next(c for c in bad["constraints_present"] if c["id"] == "georgian-colonial-american.c02")
        assert hit["value"] == 6
        assert hit["severity"] == "hard"

    def test_one_of_direction(self, core_module):
        bad = core_module.check_style_constraints("georgian-colonial-american", {"bay_count": 4})
        assert any(c["id"] == "georgian-colonial-american.c01" for c in bad["constraints_present"])
        ok = core_module.check_style_constraints("georgian-colonial-american", {"bay_count": 5})
        assert any(c["id"] == "georgian-colonial-american.c01" for c in ok["constraints_clear"])


class TestMeasurementVocabularyCoversConstraints:
    def test_default_includes_constraint_sourced_variables(self, core_module):
        result = core_module.measurement_vocabulary(style="georgian-colonial-american")
        assert "roof_pitch_rise_per_12" in result["variables"]
        assert "constraint" in result["variables"]["roof_pitch_rise_per_12"]["source"]

    def test_slot_filter_skips_constraint_pass(self, core_module):
        """slot has no meaning for a constraint -- passing one must not silently mix a
        slot-filtered fault list with an unfiltered constraint list."""
        result = core_module.measurement_vocabulary(slot="cornice", style="georgian-colonial-american")
        assert all("constraint" not in v["source"] for v in result["variables"].values())

    def test_include_constraints_false_omits_them(self, core_module):
        result = core_module.measurement_vocabulary(
            style="georgian-colonial-american", include_constraints=False)
        assert all("constraint" not in v["source"] for v in result["variables"].values())
