"""WP-14.3 -- a fatal from an instrument the corpus has convicted reports and does not disqualify.

Ruled 20 September 2026, the second of Phase 14's two rulings. The finding is emitted in FULL,
at fatal severity, with its figure; only `disqualified` and `compose._sort_key`'s primary key
stop reading it.

THE DIRECTION THAT MATTERS IS THE ONE THAT KEEPS A HOUSE HONEST. *Unjudged is not passed* cuts
both ways, and the failure this file exists to catch is not "a convicted fatal still
disqualifies" -- it is the excusal QUIETLY WIDENING until a house looks clean. So the assertions
below are, in order of importance: the finding is still there and still fatal; the warrant is
two-part and an entry with only half of it excuses nothing; and the corpus-wide effect is ONE
finding, pinned by NAME rather than by count so that a fixed instrument cannot be cancelled by a
newly excused one.
"""
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CS = _load("critic_suspects_t", "build/critic_suspects.py")
PC = _load("plan_check_t", "build/plan_check.py")
GEO = _load("geometry_t", "build/geometry.py")
CO = _load("compose_t", "build/compose.py")

# The one convicted fatal in the shipped corpus, measured at WP-14.3 and pinned BY NAME.
# A count here would let a second excusal appear as a first one is fixed.
THE_ONE = ("good-03-parlor-drawing-room-house", "column-without-entasis", "cs-parallel-shaft")


@pytest.fixture(scope="module")
def good03():
    plan = json.load(open(os.path.join(ROOT, "plans", "reference", THE_ONE[0] + ".json")))
    return PC.check(GEO.solve(plan, engine="heuristic"))


class TestTheWarrantIsTwoPart:
    def test_an_entry_with_a_basis_and_no_question_excuses_nothing(self):
        """The gate, and the reason the `question` field is optional.

        A basis says the GENERATOR admits the measurement is its own; a question says the
        CORPUS has taken a position on it. Blocking a move needs the first. Removing a
        disqualification needs both, so `cs-stair-at-the-band-edge` -- a perfectly good
        editorial suspect with a verified basis and no question -- must NOT be convicted.
        Without this, `convicted()` is `editorial()` under a second name."""
        ed = {e["id"] for e in CS.editorial()}
        conv = {e["id"] for e in CS.convicted()}
        assert conv < ed, ("convicted() must be a STRICT subset of editorial(); if every "
                           "editorial entry excuses a verdict the gate is not a gate")
        assert "cs-stair-at-the-band-edge" in ed - conv, (
            "the entry with a basis and no question must keep its move block and excuse no "
            "verdict -- if it has since gained a question, re-cut this test onto whichever "
            "entry has not, and if none has, say so rather than deleting the assertion")

    def test_convicts_matches_the_pair_and_not_the_fault_alone(self):
        """A fault may carry several tests and only the one the corpus convicted is excused.

        Matching on the fault alone would excuse every test that fault ever fires, which is a
        much larger licence than the one that was ruled."""
        e = next(x for x in CS.convicted())
        assert CS.convicts({"layer": "fault", "fault": e["fault"],
                            "expression": e["expression"]})["id"] == e["id"]
        assert CS.convicts({"layer": "fault", "fault": e["fault"],
                            "expression": "some_other_measurement * 2"}) is None, (
            "matching on the fault alone excuses tests the corpus never convicted")
        assert CS.convicts({"layer": "drawn", "fault": e["fault"],
                            "expression": e["expression"]}) is None, (
            "only a fault-layer finding can be excused by a fault-layer conviction")

    def test_the_named_list_is_not_the_ast_heuristic(self):
        """The ruling says a NAMED LIST, never a heuristic.

        `why_suspect` also returns the two AST instruments' hits, over 41 ratcheted literal
        names and 6 ratios -- a population that can grow without anyone ruling on it. Measured
        at WP-14.3 the two happen to agree on the shipped corpus at one fatal each, and that
        agreement is a property of today's corpus rather than a reason to take the wider one.
        This asserts they are different FUNCTIONS, which is what stops a later reader
        'simplifying' one into the other."""
        names = CS.suspect_names()
        assert len(names) > len(CS.convicted()), (
            "the AST instruments name far more measurements than the convicted list; if that "
            "is no longer true, re-derive before assuming the heuristic is safe to use")
        f = {"layer": "fault", "fault": "one-bay-symmetry-break",
             "expression": "count_of_openings_without_a_mirror_twin_about_the_facade_centreline"}
        assert CS.convicts(f) is None, (
            "one-bay-symmetry-break reads the plan's PLACED openings since WP-13.3 and is not "
            "convicted; excusing it would clear the only fatal on the composer's own returned "
            "leader, which is exactly the flattering direction this ruling must not become")


class TestTheFindingIsStillThere:
    def test_a_convicted_fatal_is_emitted_in_full_at_fatal_severity(self, good03):
        """The half of the ruling that is easy to lose: it REPORTS.

        An excusal implemented by dropping or downgrading the finding would be the
        fake-unjudged direction, which this corpus treats as exactly as dishonest as a fake
        pass. The row must be in `findings`, at `fatal`, carrying its figure."""
        rows = [f for f in good03["findings"]
                if f.get("fault") == THE_ONE[1] and f["severity"] == "fatal"]
        assert len(rows) == 1, f"expected the convicted fatal to still be reported; got {rows}"
        assert "1.0 against" in rows[0]["statement"], (
            "the finding must carry its own figure -- an excused fatal a reader cannot check "
            "is worse than one that disqualifies")

    def test_the_count_still_counts_it(self, good03):
        """`counts.fatal` is unchanged. Only the VERDICT stops reading it.

        If the count moved, every other reader of `counts` -- the critique, the revision
        loop's key, the bench -- would silently follow, and the excusal would stop being a
        statement about disqualification and become a statement about the house."""
        assert good03["counts"]["fatal"] == 8, (
            "re-derive per plan before re-pinning: this is the raw fatal count and the "
            "excusal must not touch it")


class TestWhatTheVerdictDoes:
    def _card(self, res, plan):
        brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
        return CO.score_candidate(res, plan, brief, 0.0, {"notes": []}, 0.0, 0.1)

    def test_the_convicted_fatal_leaves_the_disqualifying_count(self, good03):
        plan = json.load(open(os.path.join(ROOT, "plans", "reference", THE_ONE[0] + ".json")))
        card = self._card(good03, plan)
        assert card["fatal_excused"] == 1
        assert card["fatal_disqualifying"] == good03["counts"]["fatal"] - 1
        assert THE_ONE[2] in json.dumps(card["fatal_excused_rows"]), \
            "the row must name the suspect that excused it, so the reader can go and read it"
        assert "does not disqualify" in card["fatal_excused_because"], \
            "the excusal must be stated in words, not left to be inferred from two integers"

    def test_a_plan_with_seven_other_fatals_is_still_disqualified(self, good03):
        """THE ASSERTION THAT KEEPS THIS HONEST.

        The excusal removes one finding from a verdict, not the verdict. If this ever goes
        green because the plan reached zero, re-derive WHY before believing it."""
        plan = json.load(open(os.path.join(ROOT, "plans", "reference", THE_ONE[0] + ".json")))
        assert self._card(good03, plan)["disqualified"] is True

    def test_a_house_whose_ONLY_fatal_is_convicted_is_NOT_disqualified(self, good03):
        """THE RULING ITSELF, AND IT HAD TO BE DRIVEN.

        No plan in this corpus has a convicted fatal as its ONLY fatal -- `good-03` has seven
        others -- so on every shipped record `bool(fatal)` and `bool(disqualifying)` return the
        same answer and the whole ruling is unobservable. Found by mutation: restoring
        `disqualified = bool(fatal)` left all ten tests in this file GREEN.

        That is WP-11.15's rule exactly -- *a fixture where both branches return the same
        number guards neither* -- and the branch it leaves unguarded here is the one the
        package exists for. So the state is DRIVEN: a result carrying the convicted fatal and
        nothing else. The premise is asserted first, because if a shipped plan ever does reach
        this state by itself the fixture stops being the only route and a reader should know."""
        plan = json.load(open(os.path.join(ROOT, "plans", "reference", THE_ONE[0] + ".json")))
        conv = good03["fatal_on_a_convicted_instrument"]
        assert len(conv) == 1, "the fixture needs exactly one convicted row to isolate"
        assert good03["counts"]["fatal"] > 1, (
            "PREMISE: this plan carries other fatals, which is why the branch has to be "
            "driven. If it no longer does, this test is no longer the only route and the "
            "corpus-wide test below should be saying so too.")

        keep = {f["id"] for f in conv}
        res = dict(good03)
        res["findings"] = [f for f in good03["findings"]
                           if f["severity"] != "fatal" or f.get("id") in keep]
        res["counts"] = dict(good03["counts"], fatal=1)

        card = self._card(res, plan)
        assert card["fatal_excused"] == 1
        assert card["fatal_disqualifying"] == 0
        assert card["disqualified"] is False, (
            "a house whose only fatal rests on an instrument the corpus has convicted must NOT "
            "be disqualified -- that is the whole of the 20 Sep ruling")
        assert "disqualified_because" not in card,             "nothing may explain a disqualification that did not happen"
        assert "does not disqualify" in card["fatal_excused_because"],             "and the reader must still be told the fatal is there and why it was not counted"

    def test_could_not_evaluate_is_not_zero_excused(self, good03):
        """Three states, and the third is the one a two-state reader loses.

        `plan_check` returns None when `critic_suspects` will not load. None must NOT read as
        'nothing is convicted' -- that is a claim -- so nothing is excused and the reason is
        published."""
        plan = json.load(open(os.path.join(ROOT, "plans", "reference", THE_ONE[0] + ".json")))
        res = dict(good03)
        res["fatal_on_a_convicted_instrument"] = None
        card = self._card(res, plan)
        assert card["fatal_excused"] == 0
        assert card["fatal_disqualifying"] == res["counts"]["fatal"], \
            "an unjudged sweep must excuse nothing"
        assert "unjudged, not passed" in card["fatal_excused_unjudged"]

    def test_the_ordering_and_the_verdict_cannot_disagree(self):
        """`_sort_key` reads the disqualifying count, not the raw one.

        Two numbers deciding one candidate's fate is Phase 14's own defect; this is the same
        defect one layer up, and it is asserted rather than left to a comment."""
        src = open(os.path.join(ROOT, "build", "compose.py"), encoding="utf-8").read()
        key = src.split("_sort_key = lambda")[1].split("\n\n")[0]
        assert "fatal_disqualifying" in key, \
            "the ordering must read the same count the verdict does"


class TestTheCorpusWideEffect:
    def test_exactly_one_fatal_in_the_shipped_corpus_is_excused_and_it_is_named(self):
        """RATCHETED BY NAME, NEVER BY COUNT.

        A count would let a newly excused fatal cancel a fixed one and read as no change. This
        asserts the identity of the set, so either direction of movement is visible: a new
        excusal fails here, and so does the disappearance of this one.

        Measured at WP-14.3, `engine="heuristic"` (deterministic): 1 of 158 fatals across the
        sixteen shipped plans, and 0 of 16 plans change disqualification status. The ruling is
        executed and it buys almost nothing, because these houses' fatals are overwhelmingly
        the placement's -- which is the finding, not a disappointment."""
        import glob
        got = set()
        for fn in sorted(glob.glob(os.path.join(ROOT, "plans", "*.json"))) + \
                sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))):
            res = PC.check(GEO.solve(json.load(open(fn)), engine="heuristic"))
            for r in res.get("fatal_on_a_convicted_instrument") or []:
                got.add((os.path.basename(fn)[:-5], r["fault"], r["suspect"]))
        assert got == {THE_ONE}, (
            f"the excused set moved: {sorted(got)}. Re-derive per plan and name what changed; "
            f"a NEW row here is the excusal widening, which is the direction that makes a "
            f"house look clean, and a MISSING row means the instrument was fixed or the "
            f"question was settled -- opposite causes that a count cannot tell apart.")
