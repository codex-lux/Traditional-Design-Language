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
