"""The corpus's first rule, defended where it was actually broken.

"Unjudged is not passed" is the discipline this project states above all others, and an
adversarial audit found `mcp_server/core.check_measurements` breaking it in its own core:
a fault whose every test ERRORED was appended to nothing — not present, not clear, not
unjudged — and vanished from the summary counts too. To a caller that reads exactly like a
fault that passed.

The bug was fixed and, for a while, not pinned. These tests exist because that fix had no
test at all, which is the same class of gap as the bug.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(ROOT, "mcp_server") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "mcp_server"))


@pytest.fixture(scope="module")
def core_mod():
    import core
    return core


def _every_reported_id(result):
    return ({f["fault"] for f in result["faults_present"]}
            | {f["fault"] for f in result["faults_clear"]}
            | {f["fault"] for f in result["could_not_judge"]})


def test_a_fault_whose_test_errors_is_reported_not_dropped(core_mod):
    """A division by zero in a fault's own expression must not delete the fault.

    `rail_clear_run_length: 0` makes baluster-spacing-as-fence's expression raise. Every
    measurement it asked for was supplied, so there is nothing to put under
    need_measurements — which is exactly the hole the fault used to fall through.
    """
    r = core_mod.check_measurements(
        {"baluster_solid_width_total": 5, "rail_clear_run_length": 0})
    assert "baluster-spacing-as-fence" in _every_reported_id(r), (
        "a fault whose test errored vanished from every list — it reads as clear")

    row = next(f for f in r["could_not_judge"]
               if f["fault"] == "baluster-spacing-as-fence")
    assert row.get("errors"), "the fault is listed but does not say why it could not judge"
    assert any("division by zero" in e for e in row["errors"])


def test_the_summary_counts_the_fault_it_could_not_judge(core_mod):
    """Dropping it silently also under-counted `unjudged`, so the summary agreed with the
    omission instead of contradicting it."""
    r = core_mod.check_measurements(
        {"baluster_solid_width_total": 5, "rail_clear_run_length": 0})
    assert r["summary"]["unjudged"] == len(r["could_not_judge"])
    assert r["summary"]["unjudged"] > 0


def test_could_not_judge_is_never_truncated(core_mod):
    """"Unjudged is not passed" degrades into "the first forty unjudged are not passed"
    the moment this list is cut. build/plan_check.py already worked around the truncation
    by passing limit=10**6; the tool should not need the workaround."""
    r = core_mod.check_measurements({"shutter_leaf_width_in": 12}, limit=5)
    assert len(r["could_not_judge"]) == r["summary"]["unjudged"]
    assert len(r["could_not_judge"]) > 5, (
        "expected more unjudged faults than the limit, or this test proves nothing")


def test_an_uncomparable_result_is_a_judgment_not_a_crash(core_mod):
    """The threshold comparison sat outside the guarded path, so a value that will not
    compare raised out of check_measurements, through check_plan, and became a 500 from
    /api/plan/evaluate rather than something the corpus could not judge."""
    out = core_mod._eval_test(
        {"expression": "a", "direction": "at-least", "threshold": 3}, {"a": "not-a-number"})
    assert out["status"] == "error", out
    assert "does not compare" in out["detail"]
