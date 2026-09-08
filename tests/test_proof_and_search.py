"""WP-11.8 — the bench chooses, and says which.

`oq/a-proof-of-feasibility-is-not-a-proof-of-composition`, ruled 4 Sep 2026: **WP-6.3's principle
does not transfer.** A CP-SAT placement outranks a hill-climb placement on FEASIBILITY and on
nothing else. Where the compositional objective did not run, the bench draws both and labels both,
and the plate says which it drew and why.

**The measurement the package turns on, and it is why both numbers travel together.** On
`spec-builder-colonial` the search scores **592.3** against the proof's **789.3** — 197 points
better — and it buys those points by breaking **sixteen** declared facts the proof holds (0
against 16, judged against the same downgrade list). A disclosure offering only the demerit score
would tell the reader the search is the better house. It is not; it is the cheaper one, and
`hard_fact_violations`' own docstring says so: *"when the hill-climb 'outscores' the constrained
optimum, this is the number that says what the cheaper score actually bought."*
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
DISC = modcache.load("disclosures", os.path.join(ROOT, "build", "disclosures.py"))


def _fake_cp(objective, score=789.3, engine="cp-sat", pins=("L0 a N",)):
    """A solved record shaped like the CP path's, with the objective in the state under test.

    DRIVEN rather than taken from the corpus, and the reason is measured: whether a real solve
    leaves `objective` null depends on this machine's CP budget — `spec-builder-colonial` reaches
    phase A only and `tidewater-georgian-careful` times out into the heuristic entirely, and
    neither is stable enough to assert on. A fixture that IS the corpus would make these tests
    statements about a 25-second budget (WP-8.11's rule)."""
    return {"levels": [{"index": 0, "rooms": [{"id": "a", "type": "hall",
                                               "geometry": {"x_ft": 0, "y_ft": 0,
                                                            "width_ft": 10, "depth_ft": 10}}]}],
            "footprint": {"width_ft": 10, "depth_ft": 10},
            "geometry_report": {"score": score,
                                "solver": {"engine": engine, "objective": objective,
                                           "downgraded_wall_pins": list(pins)}}}


class TestTheAlternativeIsOfferedOnlyWhereTheObjectiveDidNotRun:
    def test_a_proof_whose_objective_RAN_is_offered_nothing(self):
        """There is nothing to offer against a placement every compositional term was evaluated
        on, and running a second solve to say so would be a cost with no reader."""
        out = _fake_cp(objective=376.1)
        GEO._offer_the_alternative(out, {"levels": []}, None, 250, 7)
        assert "alternative" not in out["geometry_report"]["solver"]

    def test_a_HEURISTIC_placement_is_offered_nothing(self):
        """The hill-climb's score IS its objective, summed over every candidate it looks at, so
        `objective: None` on that engine does not mean the composition went unevaluated. Reading
        the null without the engine would put this line on every heuristic sheet in the corpus."""
        out = _fake_cp(objective=None, engine="heuristic")
        GEO._offer_the_alternative(out, {"levels": []}, None, 250, 7)
        assert "alternative" not in out["geometry_report"]["solver"]

    def test_a_solve_that_fails_says_so_and_does_not_go_quiet(self, monkeypatch):
        out = _fake_cp(objective=None)
        monkeypatch.setattr(GEO, "solve_heuristic",
                            lambda *a, **k: {"error": "no ground level"})
        GEO._offer_the_alternative(out, {"levels": []}, None, 250, 7)
        alt = out["geometry_report"]["solver"]["alternative"]
        assert alt["verdict"] == "could-not-evaluate" and "no ground level" in alt["why"]

    def test_a_comparison_that_raises_says_so_and_does_not_go_quiet(self, monkeypatch):
        """`roof.py` wrapped its own reconciliation in a bare `except: pass` and then asserted
        there was nothing to stand over (WP-11.4). Not here."""
        out = _fake_cp(objective=None)
        monkeypatch.setattr(GEO, "solve_heuristic",
                            lambda *a, **k: {"levels": [], "geometry_report": {"score": 1.0}})
        monkeypatch.setattr(GEO, "_mod", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
        GEO._offer_the_alternative(out, {"levels": []}, None, 250, 7)
        alt = out["geometry_report"]["solver"]["alternative"]
        assert alt["verdict"] == "could-not-evaluate"
        assert "RuntimeError" in alt["why"] and "boom" in alt["why"]


class TestBothNumbersTravelTogether:
    """The ruling says *"with its demerit score"* and the demerit score alone misleads. This is
    the class that keeps the second number attached."""

    def test_the_offer_carries_the_score_AND_the_facts_broken_on_both_sides(self, monkeypatch):
        out = _fake_cp(objective=None, score=789.3)
        monkeypatch.setattr(GEO, "solve_heuristic",
                            lambda *a, **k: {"levels": [], "footprint": {},
                                             "geometry_report": {"score": 592.3}})
        GC = modcache.load("geometry_cp", os.path.join(ROOT, "build", "geometry_cp.py"))
        monkeypatch.setattr(GC, "hard_fact_violations",
                            lambda plan, out_, extra_downgraded=None: 16 if extra_downgraded else 0)
        GEO._offer_the_alternative(out, {"levels": []}, None, 250, 7)
        alt = out["geometry_report"]["solver"]["alternative"]
        assert alt["verdict"] == "offered"
        assert alt["score"] == 592.3 and alt["drawn_score"] == 789.3
        assert alt["hard_fact_violations"] == 16 and alt["drawn_hard_fact_violations"] == 0
        assert "not on its own a better house" in alt["why"]

    def test_the_search_is_judged_against_the_PROOFS_downgrade_list(self, monkeypatch):
        """A heuristic record carries no downgrade list of its own, and charging it for pins
        CP-SAT PROVED impossible would rig the comparison in the proof's favour.
        `hard_fact_violations` takes `extra_downgraded` for exactly this."""
        seen = {}
        out = _fake_cp(objective=None, pins=("L0 a N", "L0 a S"))
        monkeypatch.setattr(GEO, "solve_heuristic",
                            lambda *a, **k: {"levels": [], "footprint": {},
                                             "geometry_report": {"score": 1.0}})
        GC = modcache.load("geometry_cp", os.path.join(ROOT, "build", "geometry_cp.py"))

        def spy(plan, out_, extra_downgraded=None):
            seen.setdefault("calls", []).append(list(extra_downgraded or []))
            return 0
        monkeypatch.setattr(GC, "hard_fact_violations", spy)
        GEO._offer_the_alternative(out, {"levels": []}, None, 250, 7)
        assert ["L0 a N", "L0 a S"] in seen["calls"], seen

    def test_the_BANNER_prints_both_numbers(self):
        out = _fake_cp(objective=None)
        out["geometry_report"]["solver"]["alternative"] = {
            "verdict": "offered", "engine": "heuristic", "score": 592.3,
            "hard_fact_violations": 16, "drawn_score": 789.3,
            "drawn_hard_fact_violations": 0, "why": "x"}
        line = DISC.alternative_offered(out)
        assert line and line["id"] == "alternative"
        for n in ("592.3", "789.3", "16"):
            assert n in line["text"], line["text"]
        assert "NOT ON ITS OWN" in line["text"].upper()

    def test_the_banner_says_so_when_the_offer_could_not_be_computed(self):
        out = _fake_cp(objective=None)
        out["geometry_report"]["solver"]["alternative"] = {
            "verdict": "could-not-evaluate", "why": "the two placements could not be compared"}
        line = DISC.alternative_offered(out)
        assert line and "COULD NOT BE COMPUTED" in line["text"]

    def test_no_alternative_means_no_line(self):
        assert DISC.alternative_offered(_fake_cp(objective=376.1)) is None

    def test_the_line_is_in_the_banner_right_after_the_objective_line(self):
        """It is the second half of one disclosure: a reader told the composition was not
        evaluated, and not told what else is available, has been told half of it."""
        src = open(os.path.join(ROOT, "build", "disclosures.py")).read()
        assert "objective_not_run, alternative_offered" in src, \
            "the two lines must be emitted together and in that order"


class TestTheBenchRecordsWhatItDrewAndOnWhat:
    def test_placed_records_the_surface_the_engine_asked_for_and_the_inputs_digest(self):
        sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "corpus_wp118", os.path.join(ROOT, "workbench", "server", "corpus.py"))
        corpus = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(corpus)
        plan = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json")))
        GEO._SOLVE_CACHE.clear()
        out = corpus._placed(json.loads(json.dumps(plan)))
        d = out["geometry_report"]["solver"]["drawn_by"]
        assert d["surface"].endswith("_placed") and d["engine_requested"] == "auto"
        assert len(d["input_digest"]) == 12 and d["candidates"] == 250

    def test_the_digest_is_of_the_INPUT_and_two_different_records_differ(self):
        """Finding J6: two CP-SAT runs of one record agree to the foot, so when two sheets of
        "the same house" disagree, the INPUT differed — and the plate carried nothing that would
        let a reader tell. Digested before the solve, because the point is what was handed in."""
        sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "corpus_wp118b", os.path.join(ROOT, "workbench", "server", "corpus.py"))
        corpus = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(corpus)
        a = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json")))
        b = json.loads(json.dumps(a))
        b["style"] = "some-other-style"
        GEO._SOLVE_CACHE.clear()
        da = corpus._placed(json.loads(json.dumps(a)))["geometry_report"]["solver"]["drawn_by"]
        GEO._SOLVE_CACHE.clear()
        db = corpus._placed(b)["geometry_report"]["solver"]["drawn_by"]
        assert da["input_digest"] != db["input_digest"], (da, db)


class TestTheBenchParagraphSaysIt:
    """Read as TEXT, which is this repo's established idiom for holding the app to the corpus
    (`test_grammar_agreement.py` reads the JavaScript for the citation grammar). It has to be:
    the JSX is compiled by vite in CI and there is no `node_modules` here, so nothing local
    parses this file — the same asymmetry that made WP-5.7's first audit pass green locally and
    red in CI."""

    PATH = os.path.join(ROOT, "workbench", "app", "src", "surfaces", "PlanWorkbench.jsx")

    def test_it_no_longer_calls_an_unevaluated_composition_PROVED_full_stop(self):
        src = open(self.PATH).read()
        assert "proved feasible" in src, \
            "a CP placement outranks a hill-climb on FEASIBILITY and on nothing else"
        assert "Its composition was not evaluated." in src

    def test_it_reads_the_objective_from_the_record_rather_than_assuming_it_ran(self):
        src = open(self.PATH).read()
        assert "objectiveRan" in src
        assert "solver?.objective === null" in src and "=== undefined" in src, \
            "a missing key and a null must both count as did-not-run"

    def test_the_paragraph_carries_BOTH_numbers_for_BOTH_placements(self):
        """Four fields, and dropping any one of them leaves a sentence that misleads: the
        search's score without the facts it breaks reads as a better house."""
        src = open(self.PATH).read()
        for field in ("alternative.score", "alternative.drawn_score",
                      "alternative.hard_fact_violations",
                      "alternative.drawn_hard_fact_violations"):
            assert field in src, field
        assert "not\n                        on its own a better house" in src \
            or "on its own a better house" in src

    def test_no_figure_is_written_into_the_JSX(self):
        """CLAUDE.md's own trap: numbers written into JSX are not policed by `check_counts.py`,
        which is how the Kit's header claimed 95 slots against an ontology holding 97. Every
        number in this paragraph comes off the record."""
        src = open(self.PATH).read()
        for stale in ("592.3", "789.3", "16 declared fact"):
            assert stale not in src, stale
