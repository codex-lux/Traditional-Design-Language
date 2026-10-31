"""A refusal says whose failure it is (ruled by Lucas, 30 Oct 2026).

Lucas composed a Tidewater brief and read "the brief or the parti is what changes" under the native
five-part Palladian, which the prover had run out of time on: the fallback search, told none of the
type's facts, drew the arrangement that failed. `build/drawability.py` had classified every release
since WP-17.0 (PROVEN / UNDECIDED / MISMATCH / SEARCH) and no surface printed the class.

What these tests hold:

- `typefacts.refusal_class` is the one spelling and `drawability._class_of` delegates to it;
- every refusal carries `classes`, `class` and `proven`, and only PROVEN is `proven`;
- the Python surfaces' sentence says "the brief or the parti" for PROVEN alone, and a refusal that
  states no class is never read as proven;
- the app's copy of the four class names is the leaf's;
- the bearing sentence says the capacity half does not refuse (ruled 16 Sep 2026);
- a card names every judged fatal (`compose.fatal_findings`).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

TF = modcache.load("typefacts", os.path.join(ROOT, "build", "typefacts.py"))
DR = modcache.load("drawability", os.path.join(ROOT, "build", "drawability.py"))
CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))


def _record(engine="cp-sat", facts=None, status=None, proven_infeasible=False):
    rep = {"type_facts": {"status": status or {"stacks": "downgraded"}},
           "solver": {"engine": engine, "status": "FEASIBLE", "facts": facts or {}}}
    if proven_infeasible:
        rep["infeasible"] = {"proven": True, "conflicts": ["a door and a wall"]}
    return {"geometry_report": rep}


class TestTheClass:
    def test_the_search_is_never_proven(self):
        p = _record(engine="heuristic")
        assert TF.refusal_class("stacks", p) == TF.SEARCH

    def test_a_proven_infeasibility_is_proven(self):
        p = _record(engine="heuristic", proven_infeasible=True)
        assert TF.refusal_class("stacks", p) == TF.PROVEN
        assert TF.refusal(p)["proven"] is True

    def test_a_carried_release_is_undecided_and_an_all_proven_one_is_proven(self):
        carried = _record(facts={"stack": {"status": "downgraded", "downgraded": ["a", "b"],
                                           "proven": ["a"], "carried": ["b"]}})
        assert TF.refusal_class("stacks", carried) == TF.UNDECIDED
        proven = _record(facts={"stack": {"status": "downgraded", "downgraded": ["a", "b"],
                                          "proven": ["a", "b"]}})
        assert TF.refusal_class("stacks", proven) == TF.PROVEN

    def test_a_fact_the_model_held_or_never_posed_is_a_mismatch(self):
        for st in ("held", "unjudged"):
            p = _record(facts={"stack": {"status": st}})
            assert TF.refusal_class("stacks", p) == TF.MISMATCH, st

    def test_one_unproven_fact_makes_the_whole_refusal_unproven(self):
        assert TF.overall_class({"stacks": TF.PROVEN, "bearing": TF.PROVEN}) == TF.PROVEN
        assert TF.overall_class({"stacks": TF.PROVEN, "bearing": TF.UNDECIDED}) == TF.UNDECIDED
        assert TF.overall_class({"stacks": TF.MISMATCH, "bearing": TF.UNDECIDED}) == TF.UNDECIDED
        assert TF.overall_class({"stacks": TF.SEARCH, "bearing": TF.UNDECIDED}) == TF.SEARCH
        assert TF.overall_class({}) is None
        assert TF.overall_class({}, proven_infeasible=True) == TF.PROVEN

    def test_the_refusal_carries_its_class(self):
        r = TF.refusal(_record(engine="heuristic", status={"stacks": "downgraded",
                                                            "bearing": "downgraded"}))
        assert r["classes"] == {"bearing": TF.SEARCH, "stacks": TF.SEARCH}
        assert r["class"] == TF.SEARCH and r["proven"] is False

    def test_the_instrument_reads_the_leafs_class(self):
        for p in (_record(engine="heuristic"), _record(proven_infeasible=True),
                  _record(facts={"stack": {"status": "held"}}),
                  _record(facts={"stack": {"status": "downgraded", "downgraded": ["a"],
                                           "carried": ["a"]}})):
            assert DR._class_of("stacks", p) == TF.refusal_class("stacks", p)
        assert "def refusal_class" not in open(os.path.join(ROOT, "build", "drawability.py")).read()


class TestWhatTheClassSays:
    def test_only_a_proven_refusal_says_the_brief_or_the_parti_must_change(self):
        for cls in TF.REFUSAL_CLASSES:
            said = "brief or the" in TF.class_sentence({"class": cls})
            assert said == (cls == TF.PROVEN), cls

    def test_a_refusal_stating_no_class_is_never_read_as_proven(self):
        for body in ({}, {"class": None}, {"class": "MAYBE"}, None):
            assert TF.class_sentence(body) == TF.CLASS_SENTENCE[None]
            assert "brief or the" not in TF.class_sentence(body)

    def test_no_python_surface_says_it_unconditionally(self):
        for rel in ("mcp_server/core.py", "workbench/server/corpus.py"):
            src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
            assert "class_sentence(" in src, rel
        core = open(os.path.join(ROOT, "mcp_server", "core.py"), encoding="utf-8").read()
        assert "the brief or the parti is what changes. No file was written." not in core

    def test_the_apps_class_names_are_the_leafs(self):
        js = open(os.path.join(ROOT, "workbench", "app", "src", "sheet", "refusal.js"),
                  encoding="utf-8").read()
        m = re.search(r"REFUSAL_CLASSES = Object\.freeze\(\[([^\]]*)\]\)", js)
        assert m, "refusal.js names its classes"
        assert tuple(re.findall(r"'([A-Z]+)'", m.group(1))) == TF.REFUSAL_CLASSES


class TestTheBearingSentence:
    def test_the_capacity_half_says_it_does_not_refuse(self):
        src = open(os.path.join(ROOT, "build", "typefacts.py"), encoding="utf-8").read()
        i = src.index("clear \"\n") if "clear \"\n" in src else src.index("span(s) exceed the capacity")
        window = src[i - 200:i + 200]
        assert "does not refuse" in window


class TestTheCardNamesItsFatals:
    def test_every_judged_fatal_is_named_and_nothing_else(self):
        res = {"findings": [{"id": "a", "severity": "fatal", "layer": "drawn", "statement": "A"},
                            {"id": "b", "severity": "serious", "layer": "drawn", "statement": "B"},
                            {"id": "c", "severity": "fatal", "layer": "fault", "statement": "C"}]}
        got = CO.fatal_findings(res)
        assert [f["id"] for f in got] == ["a", "c"]
        assert [f["statement"] for f in got] == ["A", "C"]
        assert CO.fatal_findings({}) == []

    def test_both_card_builders_carry_it(self):
        src = open(os.path.join(ROOT, "build", "compose.py"), encoding="utf-8").read()
        assert src.count('"fatal_findings": fatal_findings(') == 2
