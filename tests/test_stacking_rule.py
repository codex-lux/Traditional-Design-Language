"""WP-11.5 — declared stacking as a RULE rather than a charge, and why it ships defaulted off.

`geometry.STACK_HARD` is False on the shipped corpus, so every assertion here DRIVES it. That is
deliberate and it is WP-8.11's lesson: a fixture that exercises a gate the corpus happens to leave
in one state is green and vacuous the moment somebody flips it. These tests set the flag
explicitly and clear `_SOLVE_CACHE`, because the cache is keyed on call ARGUMENTS and a sweep over
a module constant otherwise measures the first value (WP-7.4).

The measurement that decided the default is in `docs/reports/wp-11.5-stacking-as-a-rule.md`: the
rule works and its cost at the shipped pool of 250 is a 40 ft clear span on a reference plan.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
ST = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))


def plan(name):
    return json.load(open(os.path.join(ROOT, "plans", f"{name}.json"), encoding="utf-8"))


@pytest.fixture
def hard():
    """Drive the flag and put it back, whatever the test does."""
    was = GEO.STACK_HARD

    def _set(value):
        GEO.STACK_HARD = value
        GEO._SOLVE_CACHE.clear()
    yield _set
    GEO.STACK_HARD = was
    GEO._SOLVE_CACHE.clear()


class TestTheShippedDefault:
    def test_it_is_OFF_and_the_reason_is_written_beside_it(self):
        """If somebody flips this, every number in WP-11.5's report and three test comments
        describe a corpus that no longer exists. The reason is a 40 ft clear span."""
        assert GEO.STACK_HARD is False
        src = open(os.path.join(ROOT, "build", "geometry.py"), encoding="utf-8").read()
        head = src[:src.index("STACK_HARD = False")]
        assert "40.0 ft" in head[-2000:], (
            "the default lost the measurement that set it; a bare False is a decision nobody "
            "can argue with")

    def test_off_means_the_charge_and_the_record_says_so(self, hard):
        hard(False)
        p = GEO.solve(plan("tidewater-georgian-careful"), engine="heuristic")
        st = p["geometry_report"]["stacking"]
        assert st["rule"] == "charge" and st["claimed"] == 0


class TestOneSpellingOfTheTest:
    """`declared_stack_breaks` is the ONE reader of a `stacks_over` claim against a placement.
    `vertical_score` charges from it and the search selects on it; a second transcription is
    the `openings.required_wall_ft` error in a new place."""

    def test_the_charge_and_the_selector_read_the_same_function(self):
        src = open(os.path.join(ROOT, "build", "geometry.py"), encoding="utf-8").read()
        assert src.count("def declared_stack_breaks(") == 1
        # the two callers, and no third spelling of the intersection test
        assert src.count("declared_stack_breaks(") >= 3, "charge, selector, definition"

    def test_a_claim_whose_target_is_not_below_is_UNJUDGED_not_broken(self):
        """UNJUDGED IS NOT PASSED, and it is not failed either. The generator cannot answer a
        claim whose target is not on the level below; counting it broken convicts a placement
        of something nobody could have placed."""
        g = {"parlour": (0.0, 0.0, 10.0, 10.0)}
        u = [{"id": "bath", "stacks_over": "kitchen"}]      # kitchen is not on the level below
        breaks = GEO.declared_stack_breaks(g, {"bath": (50.0, 50.0, 8.0, 8.0)}, u)
        assert breaks == []
        census = GEO.declared_stack_census(g, {"bath": (50.0, 50.0, 8.0, 8.0)}, u)
        assert census == {"claimed": 1, "judged": 0, "broken": 0, "satisfied": 0, "unjudged": 1}

    def test_a_real_break_is_reported_with_both_room_ids(self):
        g = {"kitchen": (0.0, 0.0, 10.0, 10.0)}
        u = [{"id": "bath", "stacks_over": "kitchen", "name": "Bath"}]
        assert GEO.declared_stack_breaks(g, {"bath": (0.0, 0.0, 8.0, 8.0)}, u) == []
        br = GEO.declared_stack_breaks(g, {"bath": (50.0, 50.0, 8.0, 8.0)}, u)
        assert br == [{"room": "bath", "over": "kitchen", "name": "Bath"}]

    def test_touching_edges_are_NOT_an_overlap(self):
        """Strict positive intersection, the same rule `plan_check`'s drawn layer uses. Two
        rectangles sharing an edge do not stack: a stack needs floor over floor, not a line."""
        g = {"kitchen": (0.0, 0.0, 10.0, 10.0)}
        u = [{"id": "bath", "stacks_over": "kitchen"}]
        assert GEO.declared_stack_breaks(g, {"bath": (10.0, 0.0, 8.0, 8.0)}, u)


class TestTheRuleWhenItIsOn:
    def test_it_satisfies_every_declared_claim_on_both_shipped_plans(self, hard):
        hard(True)
        for name, claims in (("tidewater-georgian-careful", 5), ("spec-builder-colonial", 2)):
            p = GEO.solve(plan(name), engine="heuristic")
            st = p["geometry_report"]["stacking"]
            assert st["claimed"] == claims and st["rule"] == "hard", (name, st)
            assert "broken" not in st, (
                f"{name}: a strict candidate was found, so nothing may be reported broken")

    def test_it_is_NOT_free_and_the_record_says_what_it_cost(self, hard):
        """A rule whose price is hidden is a rule nobody can refuse. This is the number that
        decided the default."""
        hard(True)
        p = GEO.solve(plan("spec-builder-colonial"), engine="heuristic")
        st = p["geometry_report"]["stacking"]
        assert st.get("cost_points", 0) > 0 and "points" in st["note"]

    def test_THE_COST_THAT_DECIDED_THE_DEFAULT_a_forty_foot_span(self, hard):
        """The measurement that keeps this rule off: on `spec-builder-colonial` the strict
        candidate introduces over-capacity clear spans where there were NONE. If this ever stops
        being true the rule can be reconsidered, and this test going red is the notice."""
        hard(False)
        off = [s for lv in ST.build_section(plan("spec-builder-colonial"))["levels"]
               for s in lv["spans_exceeding_capacity"]]
        hard(True)
        on = [s for lv in ST.build_section(plan("spec-builder-colonial"))["levels"]
              for s in lv["spans_exceeding_capacity"]]
        assert off == [], "the shipped plan flags none with the rule off"
        assert on, "the rule's structural cost on this plan has gone; re-read WP-11.5's report"
        assert max(s["span_ft"] for s in on) >= 35, on

    def test_and_the_benefit_it_buys_on_the_rooms(self, hard):
        """The other half of the same trade, pinned so neither side can quietly vanish: the
        stair hall goes from 53% short of its own floor to 16%."""
        hard(False)
        off = GEO.solve(plan("spec-builder-colonial"),
                        engine="heuristic")["geometry_report"]["under_band"]
        hard(True)
        on = GEO.solve(plan("spec-builder-colonial"),
                       engine="heuristic")["geometry_report"]["under_band"]
        assert max(r["short_by_pct"] for r in off["rooms"]) >= 50
        assert max(r["short_by_pct"] for r in on["rooms"]) <= 20
        assert (sum(r["band_floor_sf"] - r["placed_sf"] for r in on["rooms"])
                < sum(r["band_floor_sf"] - r["placed_sf"] for r in off["rooms"])), (
            "total shortfall was 46 sf with the rule off and 30 sf with it on")

    def test_THE_FALLBACK_IS_NOT_SILENT_AND_NOTHING_IN_THE_CORPUS_DRIVES_IT(self, hard):
        """THE ONE BLIND GUARD OF THIS PACKAGE, found by mutation and fixed the way WP-8.11
        says: with a DRIVEN fixture. Deleting the disclosure on the no-strict-candidate path
        left the suite green, because both shipped plans always find a strict candidate at 250
        and that branch never ran. A pool of ONE forces it.

        A hard rule that quietly becomes a charge is worse than the charge, because a reader
        then believes the claims were honoured. The note names the pool it searched, the number
        of claims it could not satisfy, and how many the winner breaks."""
        hard(True)
        p = GEO.solve(plan("tidewater-georgian-careful"), None, 1,
                      engine="heuristic", seed=2)
        st = p["geometry_report"]["stacking"]
        assert st["rule"] == "charge", "one candidate cannot be expected to satisfy five claims"
        assert st["claimed"] == 5
        assert st["broken"] == 4, st
        assert "NO CANDIDATE of 1" in st["note"] and "fell back to the charge" in st["note"]
        assert "cost_points" not in st, "nothing was preferred, so nothing was paid for"

    def test_and_at_the_shipped_pool_that_fallback_does_NOT_fire(self, hard):
        """The complement, without which the test above proves only that the disclosure can
        fire. At 250 candidates both shipped plans find a strict candidate."""
        hard(True)
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            st = GEO.solve(plan(name), engine="heuristic")["geometry_report"]["stacking"]
            assert st["rule"] == "hard" and "broken" not in st, (name, st)

    def test_a_plan_with_no_claims_is_vacuous_and_says_so(self, hard):
        hard(True)
        p = GEO.solve(plan("reference/good-02-portico-library-house")
                      if os.path.exists(os.path.join(ROOT, "plans", "reference",
                                                     "good-02-portico-library-house.json"))
                      else plan("spec-builder-colonial"), engine="heuristic")
        st = p["geometry_report"]["stacking"]
        assert "claimed" in st and "rule" in st
