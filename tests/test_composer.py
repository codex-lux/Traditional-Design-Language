"""Pins the composer's ranking — see docs/compose.md and the 23 Aug review's
finding that a fix to the `via` adjacency rule 'moved the single-pile Georgian
to first place.' A scoring regression that silently drops it back to fourth is
exactly what this test protects against.

UPDATED for WP-3.2 (the elevation generator): build/plan_check.py's own ELEVATION LAYER now
folds build/elevation.py's measurements into every plan_check.check() call, including the ones
build/compose.py runs internally to score candidates -- so a candidate's elevation (bay count,
cornice proportion, window composition) can now change its ranking where before only its room
plan could. Traced directly (not assumed): for family-georgian's own brief, the single-pile
Centre Passage candidate is a very wide, shallow massing (about 82.5 ft wide, 23 ft clear depth)
-- WP-3.2's own bay-grouping formula gives it a genuine 9-bay front, which faults/even-bay-
front.json's own secondary test calls out by name ("Nine-bay fronts are institutional, not
domestic"), and the same shallow depth against a tall Tidewater wall gives a real
roof-height-to-wall-height ratio under faults/truss-flattened-pitch.json's own 0.45 floor. Both
are genuine, previously-invisible proportion problems this parti actually has at this brief's
scale -- not a scoring bug, and not the same silent regression this file was originally written
to catch. See docs/reports/wp-3.2-elevation-generator.md's own 'What was found' for the full trace.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _brief(name):
    with open(os.path.join(ROOT, "briefs", f"{name}.json")) as f:
        return json.load(f)


class TestFamilyGeorgianBrief:
    def test_single_pile_centre_passage_now_carries_two_real_elevation_fatals(self, compose_module):
        """Confirms the two fatals traced in this file's own module docstring are still exactly
        even-bay-front and truss-flattened-pitch -- if this ever changes, the ranking test below
        needs re-tracing, not just re-pinning to whatever the new number happens to be.

        WP-4.5 widened compose()'s pick window from 6 partis to 12, which found four candidates
        with zero fatal on this brief -- so this two-fatal candidate correctly no longer appears
        in the returned top four. That is the window working, not a regression. The finding this
        test exists to pin is about the PARTI, not its rank, so it is now scored directly rather
        than fished out of a truncated list: the old `next(...)` raised StopIteration the moment
        the candidate placed fifth, which reads as a crash rather than as the pin it is."""
        brief = _brief("family-georgian")
        plan, _log, _parti = compose_module.instantiate("centre-passage-single-pile", brief)
        res = compose_module.PC.check(plan)
        single_pile = {"counts": res["counts"], "worst": res["findings"]}
        assert single_pile["counts"].get("fatal", 0) == 2
        rules = {w["statement"].split(":")[0] for w in single_pile["worst"] if w["severity"] == "fatal"}
        assert any("Front With No Centre" in r for r in rules)
        assert any("Truss Default" in r for r in rules)

    def test_side_hall_town_house_ranks_first(self, compose_module):
        result = compose_module.compose(_brief("family-georgian"))
        assert result["candidates"][0]["parti_name"] == "Side-Hall Town House"

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
