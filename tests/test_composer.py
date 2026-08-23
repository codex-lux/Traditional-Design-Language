"""Pins the composer's ranking — see docs/compose.md and the 23 Aug review's
finding that a fix to the `via` adjacency rule 'moved the single-pile Georgian
to first place.' A scoring regression that silently drops it back to fourth is
exactly what this test protects against.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _brief(name):
    with open(os.path.join(ROOT, "briefs", f"{name}.json")) as f:
        return json.load(f)


class TestFamilyGeorgianBrief:
    def test_single_pile_centre_passage_ranks_first(self, compose_module):
        result = compose_module.compose(_brief("family-georgian"))
        assert result["candidates"][0]["parti_name"] == "Centre Passage, Single Pile"

    def test_top_candidate_has_zero_fatal(self, compose_module):
        result = compose_module.compose(_brief("family-georgian"))
        top = result["candidates"][0]
        assert top["counts"].get("fatal", 0) == 0

    def test_returns_four_contrasting_candidates_never_one(self, compose_module):
        """Decision not to undo #10: the composer returns N contrasting
        candidates and never calls a plan 'good.'"""
        result = compose_module.compose(_brief("family-georgian"))
        assert len(result["candidates"]) == 4
        partis = {c["parti_name"] for c in result["candidates"]}
        assert len(partis) == 4, "candidates must be genuinely different partis, not near-duplicates"

    def test_every_candidate_states_what_it_trades_away(self, compose_module):
        """The honest part, per docs/compose.md: 'every diagram gives something
        up.'"""
        result = compose_module.compose(_brief("family-georgian"))
        for c in result["candidates"]:
            assert c.get("trades_away"), f"{c['parti_name']} has no trades_away statement"


class TestBungalowBrief:
    def test_open_linear_bungalow_ranks_first_with_zero_fatal(self, compose_module):
        result = compose_module.compose(_brief("bungalow-small"))
        top = result["candidates"][0]
        assert top["parti_name"] == "Bungalow, Open and Linear"
        assert top["counts"].get("fatal", 0) == 0
