"""WP-14.2 — ONE HOUSE, ONE VERDICT.

Lucas composed a Tidewater brief and got back two candidates, both stamped
`DISQUALIFIED -- 1 fatal finding`, over a line reading `drawn [13, 73, 103, 23]`. The two
numbers were readings of two different placements and nothing on the card said so:

  * `counts`, `disqualified` and every score axis came from `PC.check` on the candidate's
    record with its placement STRIPPED, and `plan_check.py:2593` then derives the elevation
    from a FRESH HEURISTIC PLACEMENT solved inside the critic -- a house that exists nowhere.
  * the `drawn [...]` key came from the revision loop, measured on the house the sheet draws.

Measured before the change, on `briefs/family-georgian.json` at `revise_engine="heuristic"`:
the loop took `side-hall-townhouse` from drawn [11, 55, 79, 22] to [1, 58, 83, 22] -- TEN
fatal findings -- and the card went on reading `fatal 1` and `DISQUALIFIED`, because the
number it read was one the loop never touched.

THE ASSERTION THAT CANNOT BE SATISFIED BY THE OLD CODE is the reconciliation below: the
candidate's `counts` must equal the first three entries of `drawn_key_after`, element for
element. That is not a pin on a figure -- both sides move with every placement -- it is the
statement that one house was judged once.

`revise=False` is deliberately NOT covered and is not an oversight: with no loop there is no
placement, the reading stays declared, and the candidate SAYS so through `verdict_basis`.
`result["selected_on"]` carries the same fact about the pool. See
`oq/the-opt-out-compose-still-judges-a-house-nobody-placed`.
"""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY_NAMES = ("fatal", "serious", "minor")


def _brief(name):
    with open(os.path.join(ROOT, "briefs", f"{name}.json")) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def revised(compose_module):
    """ONE compose, shared. `heuristic` by name rather than `auto`, because `auto` is CP-SAT
    under a wall clock and a test that reads a placement must not read a different one on a
    loaded machine."""
    return compose_module.compose(_brief("family-georgian"), candidates=2, revise=True,
                                  revise_engine="heuristic", revise_rounds=2,
                                  revise_budget_s=60.0)


class TestTheVerdictIsAboutTheHouseTheLoopWorkedOn:
    def test_every_revised_candidate_states_the_placement_its_counts_came_from(self, revised):
        for c in revised["candidates"]:
            assert c.get("verdict_basis") == "placement", (
                f"{c['parti']}: counts were taken on {c.get('verdict_basis')!r}. A revised "
                f"candidate has a placement in hand and its verdict must be of that house.")

    def test_the_counts_on_the_card_are_the_drawn_key_the_loop_reports(self, revised):
        for c in revised["candidates"]:
            after = c.get("drawn_key_after")
            assert after, f"{c['parti']}: no drawn key, so there is nothing to reconcile"
            card = [c["counts"].get(k, 0) for k in KEY_NAMES]
            assert card == list(after[:3]), (
                f"{c['parti']}: the card reads {card} and the loop reports {list(after[:3])}. "
                f"Two numbers on one card meaning two houses is the defect this file exists "
                f"for -- do NOT reconcile it by re-pinning either; find which reading moved.")

    def test_the_before_score_is_the_same_instrument_as_the_after_one(self, revised):
        """`score` and `score_before` must be two states of one house, never two instruments.

        `compose.py` stripped the placement precisely so that drawn findings would not enter
        the revised candidate's axes and not its earlier self's. That reason is answered
        rather than evaded: BOTH ends are now the placed reading, so the pair is still one
        instrument and it is a different one from the pair earlier reports published."""
        for c in revised["candidates"]:
            before = c.get("drawn_key_before")
            assert before, f"{c['parti']}: no before key"
            cb = [(c.get("counts_before") or {}).get(k, 0) for k in KEY_NAMES]
            assert cb == list(before[:3]), (
                f"{c['parti']}: counts_before {cb} against the loop's own before key "
                f"{list(before[:3])} -- score_before is being computed on another house.")

    def test_the_pool_was_selected_on_a_reading_the_result_names(self, revised):
        """Selection and verdict are different questions and the result says so. Placing every
        instantiated diagram to choose a few would pay for placements nobody sees, so the pool
        is ranked declared -- which is honest only while it is STATED."""
        assert revised.get("selected_on") == "declared"

    def test_the_disqualification_counts_the_same_fatals_the_card_prints(self, revised):
        for c in revised["candidates"]:
            fatal = c["counts"].get("fatal", 0)
            assert bool(c.get("disqualified")) is bool(fatal)
            if fatal:
                assert str(fatal) in (c.get("disqualified_because") or ""), (
                    f"{c['parti']}: the band says {c.get('disqualified_because')!r} over a "
                    f"card reading fatal {fatal}")
