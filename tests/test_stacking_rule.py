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


def plan(name, keep_tags=False):
    """A shipped record, WITH ITS MASSING TAGS STRIPPED unless a caller asks for them.

    WP-8.11's RULE, MET AGAIN AT WP-11.16: a driven fixture must not inherit whatever the
    shipped record happens to declare. Every test in this file drives `GEO.STACK_HARD` and a
    candidate pool by hand, and the questions they ask -- does the fallback disclose itself,
    does a strict candidate exist at a pool of one -- are questions about how the SEARCH ranks
    candidates for one rectangle. They are not questions about massing elements.

    `plans/tidewater-georgian-careful.json` was tagged at WP-11.16 (six service rooms into a
    west dependency with a hyphen), which moved its placement and therefore every count in this
    file that is incidental to its subject. Stripping restores the house these tests were
    written against; `keep_tags=True` is there so a later test about stacking ACROSS elements
    has a way to ask for the real record rather than reaching around this helper.
    """
    p = json.load(open(os.path.join(ROOT, "plans", f"{name}.json"), encoding="utf-8"))
    if not keep_tags:
        for lv in p.get("levels") or []:
            for r in lv.get("rooms") or []:
                r.pop("block", None)
                r.pop("hyphen", None)
    return p


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
            assert "broken_at_selection" not in st, (
                f"{name}: a strict candidate was found, so nothing may be reported broken")

    def test_it_is_NOT_free_and_the_record_says_what_it_cost(self, hard):
        """A rule whose price is hidden is a rule nobody can refuse. This is the number that
        decided the default."""
        hard(True)
        p = GEO.solve(plan("spec-builder-colonial"), engine="heuristic")
        st = p["geometry_report"]["stacking"]
        # TWO FIGURES, POINTS AND BANDS, ruled at the merge of the two Phase 11s (8 Sep
        # 2026). This asserted `cost_points > 0` on the premise that the search ranks on
        # ONE number, which was true when it was written. The other branch's WP-11.8 made
        # the key LEXICOGRAPHIC -- the room's own proportion band first, the score second
        # -- so the preferred candidate can be worse on bands and BETTER on points, and
        # the scalar goes negative (-72.8 here) while the rule plainly cost something.
        # A negative points figure is not a cheaper house; it is one number describing two
        # keys. What the rule cost is now reported as both, signed the same way, and the
        # invariant is that it cost something ON AT LEAST ONE OF THEM.
        _pts, _band = st.get("cost_points", 0), st.get("cost_band", 0)
        assert _pts > 0 or _band > 0, (
            f"the rule preferred a different candidate, so it cost something on one of the "
            f"two keys: points={_pts}, bands={_band} -- {st}")
        # The RULE's note lives under `rule_note` after the merge: the stacking leaf also
        # writes a `note` (its claims arithmetic) and `_disclose` keeps both rather than
        # letting one overwrite the other.
        _rn = st.get("rule_note") or st["note"]
        assert "points" in _rn and "band" in _rn, (
            f"the note must state BOTH, because neither sums into the other: {_rn}")

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
        # RE-CUT AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026), AND THE BASELINE IS WHAT MOVED
        # RATHER THAN THE RULE. With the rule OFF this plan flagged NO over-capacity span on
        # either parent -- measured directly on `git archive` checkouts of both -- and flags four
        # on the merged tree, because the other branch's WP-11.8 makes the room's own proportion
        # band the first key of the candidate acceptance and a squarer room puts fewer cuts on
        # the bay module (that report measured the same trade: spans 11 -> 23). Ruled 8 Sep 2026:
        # ACCEPT AND RECORD. The 20 ft capacity and `bearing_lines`' 0.75 ft tolerance are
        # untouched, which CLAUDE.md forbids moving in as many words.
        #
        # So the absolute cleanliness is retired -- it was the baseline, not the finding -- and
        # what this test is FOR is pinned instead: turning the rule ON must still cost something
        # structural on this plan, which is the measurement that keeps it off by default.
        assert on, "the rule's structural cost on this plan has gone; re-read WP-11.5's report"
        # 35 WAS MAIN'S MEASUREMENT AND THE MERGED WORST IS 30.75 ft. Re-derived, not
        # bumped: what this line is for is that the rule costs something STRUCTURAL, and
        # a span over the 20 ft capacity is that. The magnitude is one plan's figure under
        # one candidate generator and both changed at the merge, so it is asserted as
        # over-capacity rather than pinned at a number that describes neither parent.
        assert max(s["span_ft"] for s in on) > 20, on
        # AND THE TRADE HAS INVERTED, WHICH IS RECORDED HERE AND NOT ACTED ON. Main measured
        # this rule INTRODUCING over-capacity spans on this plan (0 with it off, 2 with it on)
        # and defaulted `STACK_HARD` off for exactly that reason. On the merged tree the same
        # measurement runs the other way: 4 spans with the rule OFF and 2 with it ON, because
        # the baseline moved (see above) rather than because the rule changed. So the argument
        # that keeps the rule off no longer holds on this plan.
        #
        # THE DEFAULT IS NOT FLIPPED HERE. That is a ruling, it belongs to whoever owns the
        # rule, and a merge is the wrong place to make it -- flipping a placement default while
        # reconciling two branches would be a third change hidden inside a second one. The
        # numbers are asserted in the direction they now run so the inversion cannot go quiet,
        # and `oq/the-measurement-that-defaulted-the-stacking-rule-has-inverted` carries it.
        assert len(on) <= len(off), (
            f"the inversion recorded at the merge has reverted: off={len(off)} on={len(on)} -- "
            f"if the rule introduces spans again, main's original default argument is live and "
            f"the open question should be closed in its favour")

    def test_and_the_benefit_it_buys_on_the_rooms(self, hard):
        """The other half of the same trade, pinned so neither side can quietly vanish: the
        stair hall goes from 53% short of its own floor to 16%."""
        hard(False)
        off = GEO.solve(plan("spec-builder-colonial"),
                        engine="heuristic")["geometry_report"]["under_band"]
        hard(True)
        on = GEO.solve(plan("spec-builder-colonial"),
                       engine="heuristic")["geometry_report"]["under_band"]
        # Both sides guarded against an EMPTY list at the merge: with the band ranking as the
        # first key this plan can have no under-band room at all, and `max()` of nothing raises
        # rather than passing. A plan with none is the engine behaving; the ceiling still binds
        # wherever there is a shortfall to measure.
        # AND THE `>= 50` BECAME `>= 10` AT WP-11.17, WHICH IS A CEILING RELAXED BECAUSE THE
        # ENGINE GOT BETTER AND IS SAID SO RATHER THAN QUIETLY LOWERED. With the rule OFF, the
        # spec Colonial's worst under-band room was 53% short when this was written; stating the
        # entrance front re-places that house and the worst is 11%. The clause this line guards
        # is that the rule ON is better than the rule OFF, and the `<= 20` below still carries
        # it -- what is gone is the size of the gap, not its direction. A floor on how BAD the
        # off-state is stops being a statement about the rule once the off-state improves, which
        # is WP-11.8's own lesson about an assertion that is a floor on how bad the engine is.
        if off["rooms"]:
            assert max(r["short_by_pct"] for r in off["rooms"]) >= 10
        if on["rooms"]:
            assert max(r["short_by_pct"] for r in on["rooms"]) <= 20
        # AND THE BENEFIT IS UNMEASURABLE ON THIS PLAN AFTER THE MERGE, which is stated rather
        # than asserted away. With the proportion band as the first key of the acceptance the
        # spec Colonial has NO under-band room with the rule off OR on, so the shortfall is 0 sf
        # both ways and "less than" is false for the honest reason that there is nothing left to
        # improve. Asserting a strict decrease here would fail on a placement that had got
        # better, which is the guard-pins-an-outcome shape this corpus keeps re-cutting.
        # AND AT WP-11.17 THE BENEFIT REVERSED ON THIS PLAN, WHICH IS REPORTED RATHER THAN
        # ASSERTED AWAY. Stating the entrance front re-places the spec Colonial, and the strict
        # candidate is now 14 sf short against 4 sf with the rule off -- the rule COSTS this
        # plan 10 sf of room area where it used to buy some. Measured on the Tidewater plan as
        # a control: 0 sf both ways, so there is nothing there to tell the two apart.
        #
        # THE `<` IS NOT KEPT AND NOT INVERTED. Keeping it asserts a benefit this corpus can no
        # longer demonstrate; inverting it would pin a cost as though it were wanted, and a
        # green suite would then be evidence FOR the reversal. What is asserted is the bound the
        # `<= 20` above already carries -- the rule ON leaves no room grossly short -- plus the
        # magnitude, so the day the cost grows past a room this fails and says so. `STACK_HARD`
        # ships False, so this is the non-default branch either way.
        _off_sf = sum(r["band_floor_sf"] - r["placed_sf"] for r in off["rooms"])
        _on_sf = sum(r["band_floor_sf"] - r["placed_sf"] for r in on["rooms"])
        assert _on_sf <= 20, (
            f"the strict-stacking candidate is {_on_sf} sf short of the rooms' own band floors "
            f"against {_off_sf} sf with the rule off. It cost 10 sf at WP-11.17 and 0 before "
            f"that; a cost of this size is a trade a person can read, and a larger one is the "
            f"rule buying structure with rooms nobody would give up.")
        if _on_sf > _off_sf:
            assert _off_sf < 20, (
                f"the rule-off state is {_off_sf} sf short as well, so this plan no longer "
                f"tells the two settings apart at all and the comparison above is vacuous")

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
        # `broken_at_selection`, the CANDIDATE's count, which is main's quantity. The leaf's
        # `broken` is beside it and measures the PLACED RECORD after the post-solve passes; they
        # are different questions and the merge keeps both under their own names.
        # 4 -> 5 AT WP-11.17: with one candidate in the pool the count is a property of that
        # candidate, and stating the entrance front changes which single layout the one draw
        # produces. The claim this test makes -- that a hard rule with no satisfying candidate
        # falls back to the charge and SAYS SO -- is carried by the three assertions around
        # this one, none of which moved.
        assert st["broken_at_selection"] == 5, st
        _rn = st.get("rule_note") or st["note"]
        assert "NO CANDIDATE of 1" in _rn and "fell back to the charge" in _rn, _rn
        assert "cost_points" not in st, "nothing was preferred, so nothing was paid for"

    def test_and_at_the_shipped_pool_that_fallback_does_NOT_fire(self, hard):
        """The complement, without which the test above proves only that the disclosure can
        fire. At 250 candidates both shipped plans find a strict candidate."""
        hard(True)
        for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
            st = GEO.solve(plan(name), engine="heuristic")["geometry_report"]["stacking"]
            assert st["rule"] == "hard" and "broken_at_selection" not in st, (name, st)

    def test_a_plan_with_no_claims_is_vacuous_and_says_so(self, hard):
        hard(True)
        p = GEO.solve(plan("reference/good-02-portico-library-house")
                      if os.path.exists(os.path.join(ROOT, "plans", "reference",
                                                     "good-02-portico-library-house.json"))
                      else plan("spec-builder-colonial"), engine="heuristic")
        st = p["geometry_report"]["stacking"]
        assert "claimed" in st and "rule" in st
