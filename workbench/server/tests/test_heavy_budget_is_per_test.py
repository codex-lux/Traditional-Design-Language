"""EVERY TEST STARTS WITH THE WHOLE HEAVY-CALL BUDGET (WP-14.6).

The limiter keeps its counters in the process and the suite's one TestClient is one identity, so
until `conftest._a_fresh_heavy_budget` a test's verdict depended on how many heavy calls the tests
before it had made: `test_a_parti_record_is_refused_not_used_as_the_template` was answered 429
where it asserts 422, on the phase's parent and again after WP-14.4 added calls ahead of it. The two
tests below run in the order they are written: the first spends the whole budget, and the second
fails if any of that spending reaches it.
"""
from workbench.server import limits

PROBE = "budget-probe"


def test_a_test_may_spend_the_whole_budget():
    for _ in range(limits.heavy_calls_per_hour()):
        assert limits.check_heavy(PROBE) is None
    assert limits.check_heavy(PROBE) is not None, "the premise: the budget is spent"


def test_and_the_next_test_starts_with_all_of_it():
    assert limits.peek(f"heavy:{PROBE}")[0] == 0, (
        "the heavy budget carried over from the test before -- a test's verdict would depend on "
        "the order the suite runs in")
