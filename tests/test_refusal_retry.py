"""The composer retries an unproven refusal (ruled by Lucas, 30 Oct 2026).

A native diagram whose first placement is refused with an UNDECIDED or SEARCH class is placed once
more on the prover under a longer limit, inside the set's budget, and the second placement is
adopted only where it is not refused. PROVEN and MISMATCH are never retried; a borrowed or lineage
diagram is never retried; a compose that asked for the search by name is never retried; and a
retry the set's budget cannot hold is refused and SAID. Every branch says why on the card.

The gate is a pure function (`compose.retry_decision`) and is held directly; the wiring is driven
through a real `compose` with the refusal injected at the placement the revision loop returns, on
the search for speed -- the injected engine is the spy's, so the gate is exercised as it would be
on the prover.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
TF = modcache.load("typefacts", os.path.join(ROOT, "build", "typefacts.py"))
RV = modcache.load("revise", os.path.join(ROOT, "build", "revise.py"))


def _ref(cls):
    return {"kind": "type-fact-downgraded", "facts": ["stacks"], "conflicts": [], "lines": ["x"],
            "engine": "heuristic", "status": None, "classes": {"stacks": cls}, "class": cls,
            "proven": cls == TF.PROVEN}


class TestTheGate:
    def test_an_unproven_native_refusal_is_retried_at_twice_the_compose_budget(self):
        for cls in (TF.UNDECIDED, TF.SEARCH):
            d = CO.retry_decision({"refused": _ref(cls), "nativity": "native"}, "auto", None, 60.0)
            assert d["retry"] is True and d["limit_s"] == 120.0 and d["first_class"] == cls

    def test_a_proven_or_mismatched_refusal_is_not_retried_and_says_why(self):
        for cls, word in ((TF.PROVEN, "proof"), (TF.MISMATCH, "disagreeing")):
            d = CO.retry_decision({"refused": _ref(cls), "nativity": "native"}, "auto", None, 60.0)
            assert d["retry"] is False and word in d["why"]

    def test_a_refusal_stating_no_class_is_not_retried_and_not_called_proven(self):
        body = _ref(None)
        body.pop("class")
        d = CO.retry_decision({"refused": body, "nativity": "native"}, "auto", None, 60.0)
        assert d["retry"] is False and "does not say" in d["why"]

    def test_only_a_native_diagram_is_retried(self):
        for nat in ("borrowed", "lineage", None):
            d = CO.retry_decision({"refused": _ref(TF.UNDECIDED), "nativity": nat}, "auto", None, 60.0)
            assert d["retry"] is False and "native" in d["why"], nat

    def test_the_search_asked_by_name_is_not_retried(self):
        d = CO.retry_decision({"refused": _ref(TF.UNDECIDED), "nativity": "native"}, "heuristic",
                              None, 60.0)
        assert d["retry"] is False and "by name" in d["why"]

    def test_the_retry_is_bounded_by_the_set_and_refused_where_it_cannot_fit(self):
        card = {"refused": _ref(TF.UNDECIDED), "nativity": "native"}
        assert CO.retry_decision(card, "auto", 100.0, 60.0)["limit_s"] == 90.0
        d = CO.retry_decision(card, "auto", 50.0, 60.0)
        assert d["retry"] is False and d["why"].startswith("RETRY NOT BEGUN")

    def test_a_house_that_is_not_refused_is_not_retried(self):
        d = CO.retry_decision({"refused": None, "nativity": "native"}, "auto", None, 60.0)
        assert d["retry"] is False and d["why"] == "not refused"

    def test_the_retry_limit_differs_from_the_first_so_the_solve_cache_cannot_answer_it(self):
        """`geometry._SOLVE_CACHE` keys on the time limit: a retry at the first limit would be
        handed the refused placement back unchanged."""
        assert CO.RETRY_LIMIT_MULTIPLE > 1.0


def _brief():
    with open(os.path.join(ROOT, "briefs", "family-georgian.json")) as fh:
        return json.load(fh)


class TestTheComposerRetries:
    def _compose(self, compose_module, monkeypatch, first_class, second_refused):
        target = "centre-passage-double-pile"
        calls = []
        orig = RV.revise

        def spy(plan, **kw):
            # the declared pass (`compose.repair`) calls `revise` unplaced; only placements count
            is_target = str(plan.get("id", "")).startswith(target) and kw.get("place")
            kw = dict(kw, engine="heuristic")      # fast; the gate reads the class, not the engine
            out = orig(plan, **kw)
            if is_target:
                calls.append(kw.get("time_limit_s"))
                gr = out["plan"].setdefault("geometry_report", {})
                gr["refused"] = (copy.deepcopy(_ref(first_class)) if len(calls) == 1 else
                                 (copy.deepcopy(_ref(TF.UNDECIDED)) if second_refused else None))
            return out
        monkeypatch.setattr(RV, "revise", spy)
        res = compose_module.compose(_brief(), candidates=4, revise=True, revise_rounds=0,
                                     revise_engine="auto", revise_budget_s=600)
        card = next((c for c in res["candidates"] if c["parti"] == target), None)
        assert card is not None, ("the premise: the native centre-passage house is in the set",
                                  [c["parti"] for c in res["candidates"]])
        assert card.get("nativity") == "native", "the premise: it is native to the brief's style"
        return card, calls

    def test_an_undecided_refusal_is_retried_and_a_placed_second_attempt_replaces_it(
            self, compose_module, monkeypatch):
        card, calls = self._compose(compose_module, monkeypatch, TF.UNDECIDED, second_refused=False)
        assert len(calls) == 2, f"placed {len(calls)} time(s); the retry did not run"
        assert calls[1] > calls[0], "the retry was not given a longer limit"
        assert card["retry"]["outcome"] == "placed" and card["retry"]["first_class"] == TF.UNDECIDED
        assert CO.placement_standing(card) == "placed"
        assert any(d.startswith("RETRY PLACED") for d in card["decisions"])

    def test_a_retry_refused_again_keeps_the_first_and_says_so(self, compose_module, monkeypatch):
        card, calls = self._compose(compose_module, monkeypatch, TF.SEARCH, second_refused=True)
        assert len(calls) == 2
        assert card["retry"]["outcome"] == "refused"
        assert card["refused"]["class"] == TF.SEARCH, "the first placement is kept"
        assert any(d.startswith("RETRY REFUSED AGAIN") for d in card["decisions"])

    def test_a_proven_refusal_is_placed_once(self, compose_module, monkeypatch):
        card, calls = self._compose(compose_module, monkeypatch, TF.PROVEN, second_refused=False)
        assert len(calls) == 1
        assert card["retry"]["retry"] is False and card["retry"]["outcome"] is None
        assert CO.placement_standing(card) == "refused"
