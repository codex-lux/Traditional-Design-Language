"""THE JOINT PROOF (ruled by Lucas, 26 Nov 2026, asked and answered as its own act).

The line grid made the prover's hard steps DECIDE, and on the stock Georgian brief six of fourteen
composed diagrams came back INFEASIBLE at every depth the prover tries, most in under four seconds
-- under a card reading "not proven: out of time", a retry at twice the time, and a pool-fill slot
each. Ruled:

  * such a refusal READS AS PROVEN and is NOT RETRIED;
  * a pool diagram proven impossible does NOT count against the pool-fill's cap.

What these hold: the verdict is read off the record's own structure and never guessed; the per-fact
classes do not move (no single fact was refuted alone); a verdict that is not the proof -- a step
out of time, a depth never reached, a record from before the field -- never reads as one; and the
composer's two decisions follow from the class and the flag. The records are HAND-BUILT, because
the subject is what each reader does with the verdict, not what the prover answers.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

TF = modcache.load("typefacts", os.path.join(ROOT, "build", "typefacts.py"))
CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
RV = modcache.load("revise", os.path.join(ROOT, "build", "revise.py"))
GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))


def _record(verdict, engine="cp-sat", where="solver", carried=True):
    """A placed record whose stacks are measured broken and whose prover says `verdict` of every
    type fact held together -- on the solver block, or on `cp_run` where a fallback was drawn."""
    af = None if verdict is None else {"verdict": verdict, "steps": []}
    solver = {"engine": engine, "status": "FEASIBLE",
              "facts": {"stack": {"status": "downgraded", "downgraded": ["L1 landing"],
                                  "carried": ["L1 landing"] if carried else [],
                                  "proven": [] if carried else ["L1 landing"]}}}
    if where == "solver":
        solver["all_facts"] = af
    else:
        solver["cp_run"] = {"workers": 1, "workers_available": 1, "mode": "ladder",
                            "status": "UNKNOWN", "all_facts": af}
    return {"geometry_report": {"solver": solver, "type_facts": {
        "status": {"tiling": "held", "stacks": "downgraded", "bearing": "held", "hearth": "unjudged"},
        "stacks": {"claims": [{"room": "landing", "over": "hall", "verdict": "broken"}]}}}}


def test_the_verdict_is_read_off_structure_and_an_unknown_word_is_not_a_verdict():
    assert TF.all_facts_verdict(_record(TF.ALL_FACTS_PROVEN_IMPOSSIBLE)) == TF.ALL_FACTS_PROVEN_IMPOSSIBLE
    assert TF.all_facts_verdict(_record(TF.ALL_FACTS_PROVEN_IMPOSSIBLE, where="cp_run")) \
        == TF.ALL_FACTS_PROVEN_IMPOSSIBLE
    assert TF.all_facts_verdict(_record(None)) is None
    assert TF.all_facts_verdict({"geometry_report": {"solver": {"all_facts": {"verdict": "impossible"}}}}) is None
    assert TF.all_facts_verdict({"geometry_report": {"solver": {"all_facts": "proven-impossible"}}}) is None
    assert TF.all_facts_verdict({}) is None
    assert set(TF.ALL_FACTS_VERDICTS) == {"held", "proven-impossible", "undecided"}


def test_a_joint_proof_reads_as_proven_and_the_fact_alone_keeps_its_own_class():
    ref = TF.refusal(_record(TF.ALL_FACTS_PROVEN_IMPOSSIBLE))
    assert ref["jointly_proven"] is True
    assert ref["class"] == TF.PROVEN and ref["proven"] is True
    # NO SINGLE FACT WAS REFUTED ALONE: the stack was carried, and its own class still says so
    assert ref["classes"] == {"stacks": TF.UNDECIDED}
    assert ref["lines"][-1] == TF.JOINT_PROOF_LINE
    assert "ruled order" in TF.JOINT_PROOF_LINE and "not a proof about that one fact" in TF.JOINT_PROOF_LINE
    assert ref["kind"] == TF.KIND_DOWNGRADED and ref["facts"] == ["stacks"]


@pytest.mark.parametrize("verdict", [TF.ALL_FACTS_UNDECIDED, TF.ALL_FACTS_HELD, None])
def test_anything_short_of_the_proof_changes_nothing(verdict):
    """A step out of time, a depth never reached, a record from before the field: the refusal is
    exactly the one it was -- UNDECIDED, not proven, and no line about a proof."""
    ref = TF.refusal(_record(verdict))
    assert ref["jointly_proven"] is False
    assert ref["class"] == TF.UNDECIDED and ref["proven"] is False
    assert TF.JOINT_PROOF_LINE not in ref["lines"]


def test_a_fallback_drawn_after_the_proof_is_proven_too_and_its_facts_stay_the_searchs():
    """Where the ladder ends unsolved after the hard steps proved the house impossible, the search
    draws the record and `cp_run` carries the verdict. The refusal is PROVEN -- the proof is about
    the house, whoever drew this arrangement -- and each fact's own class is still SEARCH."""
    ref = TF.refusal(_record(TF.ALL_FACTS_PROVEN_IMPOSSIBLE, engine="heuristic", where="cp_run"))
    assert ref["class"] == TF.PROVEN and ref["jointly_proven"] is True
    assert ref["classes"] == {"stacks": TF.SEARCH}
    plain = TF.refusal(_record(TF.ALL_FACTS_UNDECIDED, engine="heuristic", where="cp_run"))
    assert plain["class"] == TF.SEARCH and plain["jointly_proven"] is False


def test_a_fact_proven_alone_is_not_called_jointly_proven_without_the_verdict():
    ref = TF.refusal(_record(TF.ALL_FACTS_UNDECIDED, carried=False))
    assert ref["class"] == TF.PROVEN and ref["jointly_proven"] is False


def test_nothing_refused_is_nothing_said_whatever_the_verdict():
    rec = _record(TF.ALL_FACTS_PROVEN_IMPOSSIBLE)
    rec["geometry_report"]["type_facts"]["status"]["stacks"] = "held"
    assert TF.refusal(rec) is None


# ------------------------------------------------------------- the composer's two decisions
def test_a_joint_proof_is_not_retried_and_an_undecided_refusal_still_is():
    """The retry gates on the refusal's class, so the ruling's second half follows from its first:
    more time cannot move a proof. The control is the same record without the proof."""
    for verdict, retried in ((TF.ALL_FACTS_PROVEN_IMPOSSIBLE, False), (TF.ALL_FACTS_UNDECIDED, True)):
        ref = TF.refusal(_record(verdict))
        d = CO.retry_decision({"refused": ref, "nativity": "native"}, "auto", 600.0, 60.0)
        assert d["retry"] is retried, (verdict, d)
        if not retried:
            assert "proven" in d["why"] and "more time cannot move a proof" in d["why"], d["why"]


def test_a_joint_proof_may_still_be_repaired():
    """A changed record is exactly what can move a proof (the repair's own ruling, 19 Nov 2026)."""
    rec = _record(TF.ALL_FACTS_PROVEN_IMPOSSIBLE)
    ref = TF.refusal(rec)
    d = CO.repair_decision({"refused": ref, "nativity": "native"}, rec, "auto", 600.0, 60.0)
    assert d["repair"] is True and d["facts"] == ["stacks"], d


def _card(ref):
    return {"parti": "x", "parti_name": "X", "refused": ref,
            "revision": {"stop_reason": "no-rounds", "placement_time_limit_s": 60.0}}


def test_the_passed_over_entry_says_proven_and_carries_the_flag():
    joint = CO.passed_over_entry(_card(TF.refusal(_record(TF.ALL_FACTS_PROVEN_IMPOSSIBLE))))
    assert joint["standing"] == "refused" and joint["jointly_proven"] is True and joint["proven"] is True
    assert "proven: the type's facts cannot all hold together as composed" in joint["why"]
    plain = CO.passed_over_entry(_card(TF.refusal(_record(TF.ALL_FACTS_UNDECIDED))))
    assert plain["jointly_proven"] is False and plain["proven"] is False and "proven" not in plain["why"]
    # PROVEN BY ANOTHER ROUTE is proven all the same: a fact refuted alone (or a record carrying
    # a proven infeasibility, as the composed octagon's does) reads `proven` and not `jointly`
    alone = CO.passed_over_entry(_card(TF.refusal(_record(TF.ALL_FACTS_UNDECIDED, carried=False))))
    assert alone["proven"] is True and alone["jointly_proven"] is False and alone["why"].endswith("(proven)")


# ------------------------------------------------- the pool-fill's cap, driven over a real compose
def _compose(monkeypatch, jointly, candidates=2, proven=None):
    """Compose with every placement REFUSED, each refusal proven or not as stated (the spy
    pattern of `tests/test_pool_fill.py`: the composer's own loop, the placer's verdict stated).
    `proven` defaults to `jointly`; stated apart, it is a refusal proven by another route."""
    proven = jointly if proven is None else proven
    placed = []
    orig = RV.revise

    def spy(plan, **kw):
        out = orig(plan, **kw)
        if kw.get("place"):
            placed.append(str(plan.get("id", "")))
            out["plan"].setdefault("geometry_report", {})["refused"] = {
                "kind": "type-fact-downgraded", "facts": ["tiling"], "conflicts": [], "lines": [],
                "class": TF.PROVEN if proven else TF.UNDECIDED, "proven": bool(proven),
                "jointly_proven": bool(jointly)}
        return out
    monkeypatch.setattr(RV, "revise", spy)
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json"), encoding="utf-8"))
    res = CO.compose(brief, candidates=candidates, revise=True, revise_rounds=0,
                     revise_engine="heuristic", revise_budget_s=600)
    return res, placed


def test_a_pool_diagram_proven_impossible_does_not_use_a_slot_of_the_cap(monkeypatch):
    """The cap bounds placements that cost a placement. Where every pool diagram is proven
    impossible the fill runs to the END OF THE POOL, names each, and says how many did not count;
    where none is, the same compose stops at the cap exactly as it always has."""
    res, _ = _compose(monkeypatch, jointly=False)
    pf = res["pool_fill"]
    assert pf["placed_from_pool"] == CO.POOL_FILL_PLACEMENTS and pf["stopped_by"] == "cap", pf
    assert pf["proven_not_counted"] == 0 and pf["not_reached"], pf
    monkeypatch.undo()

    res2, _ = _compose(monkeypatch, jointly=True)
    pf2 = res2["pool_fill"]
    n_pool = len(pf["passed_over"]) + len(pf["not_reached"])
    assert n_pool > CO.POOL_FILL_PLACEMENTS, "premise: the pool is deeper than the cap"
    assert pf2["placed_from_pool"] == n_pool and pf2["stopped_by"] == "pool", pf2
    assert pf2["proven_not_counted"] == n_pool and pf2["not_reached"] == [], pf2
    assert all(p["jointly_proven"] for p in pf2["passed_over"])
    line = CO.pool_fill_line(pf2, 2)
    assert f"{n_pool} of the refused were PROVEN" in line and "did not count against the cap" in line, line
    assert "PROVEN" not in CO.pool_fill_line(pf, 2)
    monkeypatch.undo()

    # proven by another route (not jointly) is free of the cap too: the ruling is "proven impossible"
    res3, _ = _compose(monkeypatch, jointly=False, proven=True)
    pf3 = res3["pool_fill"]
    assert pf3["proven_not_counted"] == n_pool and pf3["stopped_by"] == "pool", pf3
    assert not any(p["jointly_proven"] for p in pf3["passed_over"]) and all(p["proven"] for p in pf3["passed_over"])
