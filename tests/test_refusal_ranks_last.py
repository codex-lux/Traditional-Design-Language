"""The composer ranks a refused house after a drawable one (ruled by Lucas, 16 Oct 2026).

`oq/the-composer-ranks-first-a-house-that-may-not-be-drawn` measured `compose` handing back, as
its first recommendation, a candidate the type's hard facts forbid drawing (WP-13.4), while a
drawable one stood second. Lucas ruled reading 1: within equal judged fatals, refused ranks last.

What these tests hold, and what each is for:

- `placement_standing` reads a card's placement as `refused`, `placed` or `unjudged`, and its
  table of cases is `tests/fixtures/candidate_standing.json`, the same table the workbench's
  `standingOf` is held to (`workbench/app/src/candidateSelection.test.mjs`). `refused` is `None`
  on a card for three reasons and one of them is a pass; a reader collapsing them is the fake
  pass this corpus names first.
- `rank_key` puts the standing AFTER the judged fatals and BEFORE the unjudged fatals and the
  score. Each of the three orderings that could be written instead is a different house first,
  and each is driven below by a pair of cards that only that ordering separates.
- the composer's own re-sort, after the placed loop, reads it. That is the one place the field
  exists, and the one line a pure test of `rank_key` cannot reach, so it is driven through a real
  `compose` with the refusal injected at the placement.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
RV = modcache.load("revise", os.path.join(ROOT, "build", "revise.py"))

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "candidate_standing.json")
REFUSED = {"kind": "type-fact-downgraded", "facts": ["stacks"], "conflicts": [], "lines": []}
PLACED = {"stop_reason": "converged"}


def _card(parti, *, fatal=0, unjudged=0, score=50.0, refused=None, revision=PLACED, demerits=0.0):
    return {"parti": parti, "counts": {"fatal": fatal}, "score": score, "demerits": demerits,
            "unjudged_fatal": [{"fault": f"f{i}", "name": f"f{i}"} for i in range(unjudged)],
            "refused": refused, "revision": revision}


def _order(cards):
    got = [c["parti"] for c in sorted(cards, key=CO.rank_key)]
    assert [c["parti"] for c in sorted(reversed(cards), key=CO.rank_key)] == got, (
        "the order depends on the order the cards arrived in")
    return got


# ---------------------------------------------------------------- the reading of a card

def _cases():
    with open(FIXTURE) as fh:
        return json.load(fh)["cases"]


class TestOneReadingOfAPlacementTwoLanguages:
    @pytest.mark.parametrize("case", _cases(), ids=lambda c: c["name"])
    def test_the_composer_reads_the_shared_table(self, case):
        assert CO.placement_standing(case["card"]) == case["standing"]

    def test_the_table_has_every_standing_and_more_than_one_unjudged_route(self):
        """A table with one `unjudged` row is a table that cannot tell the three nulls apart."""
        by = {}
        for c in _cases():
            by.setdefault(c["standing"], []).append(c["name"])
        assert set(by) == {"refused", "placed", "unjudged"}
        assert len(by["unjudged"]) >= 4, by["unjudged"]
        assert len(by["refused"]) >= 2 and len(by["placed"]) >= 2

    def test_the_unjudged_stop_reason_is_the_revision_loops_own_string(self):
        """Three copies of one string (revise, compose, the app) and no import between them. The
        loop's constant is the source; the composer's copy must equal it, and the loop must
        actually write it, or the composer would be matching a string nobody produces."""
        assert CO.PLACEMENT_UNJUDGED == RV.STOP_PLACEMENT_UNJUDGED
        src = open(os.path.join(ROOT, "build", "revise.py")).read()
        assert src.count('"placement-could-not-be-evaluated"') == 1, (
            "the literal is spelled once, in the constant; every other site reads the name")
        assert "stop = STOP_PLACEMENT_UNJUDGED" in src

    def test_the_standings_are_ranked_placed_then_unjudged_then_refused(self):
        assert CO.STANDING_RANK["placed"] < CO.STANDING_RANK["unjudged"] < CO.STANDING_RANK["refused"]
        assert set(CO.STANDING_RANK) == {"placed", "unjudged", "refused"}


# ---------------------------------------------------------------- the key

class TestRefusedRanksLastWithinEqualFatals:
    def test_a_refused_house_with_the_best_score_comes_after_a_drawable_one(self):
        """The ruling itself. The refused card has the higher score and the fewer unjudged
        fatals, so only the standing key can put the drawable one first."""
        got = _order([_card("refused-best", score=90.0, unjudged=0, refused=REFUSED),
                      _card("drawable-worse", score=40.0, unjudged=2)])
        assert got == ["drawable-worse", "refused-best"]

    def test_judged_fatals_are_still_the_first_key(self):
        """The ruling is 'within equal judged fatals'. A refused house with no fatal finding
        still stands above a drawable one carrying a fatal: WP-4.5's guarantee that a fatal
        plan never displaces a clean one is the one thing this key must not trade away."""
        got = _order([_card("drawable-fatal", fatal=1, score=99.0),
                      _card("refused-clean", fatal=0, score=1.0, refused=REFUSED)])
        assert got == ["refused-clean", "drawable-fatal"]

    def test_the_standing_is_ahead_of_the_unjudged_fatals(self):
        """R13 (29 Sep 2026) breaks a tie against a candidate with fatals nobody could judge. The
        refusal is ahead of it: a refused house with none must not lead a drawable one with
        one, or the first card is the screen the ruling exists to remove."""
        got = _order([_card("refused-no-unjudged", unjudged=0, score=60.0, refused=REFUSED),
                      _card("drawable-one-unjudged", unjudged=1, score=60.0)])
        assert got == ["drawable-one-unjudged", "refused-no-unjudged"]

    def test_unjudged_is_between_placed_and_refused_and_is_not_a_pass(self):
        """A candidate nobody placed (the set's budget did not reach it) may be refused on the
        bench. It does not outrank a house known to be drawable, and it does not trail one
        known to be refused: three tiers, because two would call it a pass or a failure."""
        got = _order([_card("refused", score=95.0, refused=REFUSED),
                      _card("unplaced", score=70.0, revision=None),
                      _card("placed", score=10.0)])
        assert got == ["placed", "unplaced", "refused"]

    def test_inside_one_standing_the_score_still_orders(self):
        got = _order([_card("a", score=10.0, refused=REFUSED), _card("b", score=30.0, refused=REFUSED),
                      _card("c", score=20.0), _card("d", score=40.0)])
        assert got == ["d", "c", "b", "a"]

    def test_a_set_nobody_placed_keeps_exactly_the_order_it_had(self):
        """Before the placed loop, and with `revise=False`, every card is unjudged and the new
        key is a constant: the slice the loop is handed, and every `revise=False` result, are
        ordered exactly as they were before this ruling."""
        cards = [_card("x", fatal=1, unjudged=1, score=30.0, revision=None),
                 _card("y", fatal=0, unjudged=2, score=10.0, revision=None),
                 _card("z", fatal=0, unjudged=0, score=20.0, revision=None)]

        def old(c):
            return (c["counts"]["fatal"], len(c["unjudged_fatal"]), -c["score"], c["demerits"], c["parti"])
        assert [c["parti"] for c in sorted(cards, key=CO.rank_key)] == [c["parti"] for c in sorted(cards, key=old)]

    def test_a_card_that_carries_no_standing_fields_at_all_still_ranks(self):
        """The declared pass writes `refused` as None and no `revision`; a bare card is the
        shape `test_fault_governing` hands the key and must not raise."""
        bare = {"parti": "bare", "counts": {"fatal": 0}, "score": 1.0, "demerits": 0.0}
        assert CO.rank_key(bare)[1] == CO.STANDING_RANK["unjudged"]


# ---------------------------------------------------------------- the composer's own sort

def _brief():
    with open(os.path.join(ROOT, "briefs", "family-georgian.json")) as fh:
        return json.load(fh)


class TestComposeReSortsOnTheRefusalItself:
    def test_the_best_scoring_candidate_is_refused_and_the_set_puts_it_last(self, compose_module, monkeypatch):
        """DRIVEN through `compose`'s real post-loop sort, because that is the one line where the
        field exists. The set is made equal on fatals at the scorer (the seam the existing
        ordering test uses: `res["counts"]` IS the dict compose binds as the card's own), the
        native centre-passage house is given the highest score and refused at the placement
        the revision loop returns, and every other house is stated drawable. Under a key that
        ignores `refused` it leads; under this one it is last."""
        target = "centre-passage-double-pile"
        real_score = compose_module.score_candidate

        def forced(res, plan, brief, fit, fp, miss, tol):
            res["counts"]["fatal"] = 0
            card = real_score(res, plan, brief, fit, fp, miss, tol)
            card["score"] = 99.0 if str(plan.get("id", "")).startswith(target) else 40.0
            return card
        monkeypatch.setattr(compose_module, "score_candidate", forced)

        orig = RV.revise

        def spy(plan, **kw):
            out = orig(plan, **kw)
            if kw.get("place"):
                # the real placements of this brief are mostly refused themselves (that is the
                # open question's finding), so the verdict is stated for every card: the target
                # refused, every other house drawable. The ranking is what is under test.
                gr = out["plan"].setdefault("geometry_report", {})
                gr["refused"] = (dict(REFUSED) if str(plan.get("id", "")).startswith(target) else None)
            return out
        monkeypatch.setattr(RV, "revise", spy)

        res = compose_module.compose(_brief(), candidates=4, revise=True, revise_rounds=0,
                                     revise_engine="heuristic", revise_budget_s=120)
        cands = res["candidates"]
        partis = [c["parti"] for c in cands]
        assert target in partis, f"the premise: the native house is in the set {partis}"
        assert len(cands) >= 3
        standings = [CO.placement_standing(c) for c in cands]
        assert standings[partis.index(target)] == "refused", (
            "the premise: the injected refusal reached the card the composer sorts")
        assert standings == sorted(standings, key=CO.STANDING_RANK.get), (
            f"a refused house came back above a drawable one: {list(zip(partis, standings))}")
        assert partis[-1] == target, f"the refused house with the best score is not last: {partis}"
        assert cands[0]["score"] <= 99.0 and cands[0]["parti"] != target

    def test_compose_sorts_on_the_one_key_before_and_after_the_loop(self, compose_module):
        """A source guard for the two lines a behavioural test cannot tell apart: one key,
        applied to the declared pass and again after the placed loop."""
        import inspect
        src = inspect.getsource(compose_module.compose)
        assert "_sort_key = rank_key" in src
        assert src.count("key=_sort_key") == 2
