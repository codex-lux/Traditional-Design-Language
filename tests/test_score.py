"""The composite score, pinned.

WHY THIS FILE EXISTS. The published figure was a demerit total -- 100 a fatal, 8 a serious,
1 a minor, less 20 a point of style fidelity -- shown in the workbench under a 26px numeral
labelled SCORE. It was LOWER IS BETTER, had no ceiling, and its magnitude tracked how many
times a plan happened to be checked rather than how good it was: 36 on one brief and 208 on
another for plans of comparable merit. Every reader took the biggest number for the winner.
It is now a weighted composite out of 100, higher is better, each axis a share of its own
denominator. These tests hold the four properties that make that honest rather than merely
prettier: the weights are a hundred, nothing is scored twice or dropped silently, an axis
with no evidence loses its weight instead of passing, and a fatal forfeits rather than
averages away.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _brief(name):
    with open(os.path.join(ROOT, "briefs", f"{name}.json")) as f:
        return json.load(f)


class TestTheWeights:
    def test_the_axes_are_a_hundred(self, compose_module):
        assert sum(w for _, w, _ in compose_module.SCORE_AXES) == 100

    def test_every_axis_says_what_it_measures(self, compose_module):
        """The weights are editorial. An editorial number with no stated basis is exactly
        what the corpus calls a silent judgment."""
        for name, weight, what in compose_module.SCORE_AXES:
            assert what and len(what) > 20, f"{name} carries no statement of what it measures"

    def test_exactly_one_layer_is_deliberately_unscored(self, compose_module):
        """The code layer, and only the code layer. plan_check.py's own note calls code
        findings advisory and jurisdictional, so scoring a house on them would be scoring it
        against a jurisdiction nobody named. Any OTHER layer mapping to None would be a
        finding quietly excused."""
        unscored = [k for k, v in compose_module.SCORE_LAYERS.items() if v is None]
        assert unscored == ["code"]


class TestNothingIsDroppedSilently:
    def test_every_layer_the_validator_emitted_is_classified(self, compose_module):
        """A new layer in plan_check.py must not quietly stop counting toward the score.
        compose() reports any it does not recognise on the record rather than ignoring it."""
        result = compose_module.compose(_brief("family-georgian"))
        for c in result["candidates"]:
            assert c["score_unclassified_layers"] == [], (
                f'{c["parti_name"]} carries findings in {c["score_unclassified_layers"]}, '
                f"which no axis scores — add them to SCORE_LAYERS or say why they are exempt")

    def test_the_axes_sum_to_the_score(self, compose_module):
        """The published arithmetic is the arithmetic, not an illustration of it."""
        result = compose_module.compose(_brief("family-georgian"))
        for c in result["candidates"]:
            earned = sum(a["points"] for a in c["score_axes"] if a["points"] is not None)
            weight = sum(a["weight"] for a in c["score_axes"] if a["points"] is not None)
            assert abs(100 * earned / weight - c["score"]) < 0.2, c["parti_name"]


class TestUnjudgedIsNotPassed:
    def test_an_axis_with_no_evidence_loses_its_weight(self, compose_module):
        """Neither a zero nor a pass. The dropped weight is reported so a score taken over
        94 points of evidence cannot be read as one taken over 100."""
        result = compose_module.compose(_brief("family-georgian"))
        for c in result["candidates"]:
            assert c["score_weight_evaluated"] + c["score_weight_unevaluated"] == 100
            for a in c["score_axes"]:
                if a["share"] is None:
                    assert a["points"] is None and a["note"], a["axis"]

    def test_unjudged_faults_are_outside_the_fraction_not_inside_it(self, compose_module):
        """The dangerous direction is unjudged reported as passed. This brief's candidates
        each carry ~129 faults the corpus could not judge against ~76 it could; counting the
        unjudged as clear would put every solecisms axis over 90%."""
        result = compose_module.compose(_brief("family-georgian"))
        for c in result["candidates"]:
            ax = next(a for a in c["score_axes"] if a["axis"] == "solecisms")
            assert ax["unjudged"] > 0, "expected unjudged faults on this brief"
            assert ax["of"] == ax["clean"] + ax["flagged"], (
                f'{c["parti_name"]}: the solecisms denominator is not what was judged')


class TestAFatalForfeits:
    def test_a_fatal_finding_withholds_the_score_and_says_why(self, compose_module):
        """A fatal is a thing that is wrong, not a thing that is worse. Scored directly
        rather than fished out of compose(), which correctly does not return this candidate
        at all -- see tests/test_composer.py for why it places fifth."""
        brief = _brief("family-georgian")
        plan, _log, parti = compose_module.instantiate("centre-passage-single-pile", brief)
        res = compose_module.PC.check(plan)
        assert res["counts"].get("fatal", 0) >= 1, "this parti is pinned as carrying fatals"
        fp = compose_module.footprint(plan, parti)
        card = compose_module.score_candidate(res, plan, brief, 7.0, fp, 0.0, 0.12)
        assert card["score"] is None
        assert "fatal" in card["score_forfeit"]
        assert card["score_axes"], "the axes are still measured on a forfeited candidate"

    def test_a_forfeited_candidate_is_still_measured_on_every_axis(self, compose_module):
        brief = _brief("family-georgian")
        plan, _log, parti = compose_module.instantiate("centre-passage-single-pile", brief)
        res = compose_module.PC.check(plan)
        fp = compose_module.footprint(plan, parti)
        card = compose_module.score_candidate(res, plan, brief, 7.0, fp, 0.0, 0.12)
        assert len(card["score_axes"]) == len(compose_module.SCORE_AXES)


class TestTheOrderIsWhatItSays:
    def test_returned_fatal_free_first_then_highest_score(self, compose_module):
        for name in ("family-georgian", "bungalow-small"):
            cands = compose_module.compose(_brief(name))["candidates"]
            keys = [(c["counts"].get("fatal", 0),
                     -(c["score"] if c["score"] is not None else -1e9)) for c in cands]
            assert keys == sorted(keys), f"{name} is not returned in the order it claims"

    def test_the_score_is_a_hundred_at_most(self, compose_module):
        """The property the demerit total could not have: a ceiling, so the number can be
        read on its own rather than only against the other three columns."""
        for name in ("family-georgian", "bungalow-small"):
            for c in compose_module.compose(_brief(name))["candidates"]:
                if c["score"] is None: continue
                assert 0 <= c["score"] <= 100, f'{name}/{c["parti_name"]}: {c["score"]}'
