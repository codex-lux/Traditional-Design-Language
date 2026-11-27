"""EVERY CANDIDATE IS PLACED ONCE BEFORE ANY IS PLACED TWICE (26 Nov 2026).

`compose._revise_one` ran a candidate's first placement, its repair and its retry in one call, and
the repair and the retry are bounded by the SET's time, not the candidate's share. Measured on the
stock Georgian brief at one worker: two native diagrams the prover could not decide took a
placement, a repair and a 120 s retry each, the whole 560 s set; the living hall -- which holds
every type fact in four seconds -- was placed with what was left and handed to the search; and the
pool-fill, which holds the one house drawable where judged, stopped on `budget` having placed
nothing.

The passes are ordered now: first placements for the whole set, then the pool-fill, then the
repairs and retries on what is left. These hold the ORDER, off the composer's own calls to the
placed loop, with every verdict stated by a spy (the pattern of `tests/test_pool_fill.py`): the
subject is what the composer does with each answer, not what the placer answers.
"""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402
from conftest import stub_pool_probe  # noqa: E402

CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
RV = modcache.load("revise", os.path.join(ROOT, "build", "revise.py"))
TF = modcache.load("typefacts", os.path.join(ROOT, "build", "typefacts.py"))
GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))


def _brief():
    return json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json"), encoding="utf-8"))


def _ref(cls):
    return {"kind": "type-fact-downgraded", "facts": ["bearing"], "conflicts": [], "lines": [],
            "class": cls, "proven": cls == TF.PROVEN, "jointly_proven": False}


def _compose(monkeypatch, second_places=(), candidates=3, budget=600):
    """Every FIRST placement is refused UNDECIDED (so a native diagram's retry is wanted); a second
    placement of a parti in `second_places` is not refused, every other one is refused again.
    Returns (result, calls) with calls = [(parti, time_limit_s), ...] in the order placed."""
    calls = []
    orig = RV.revise

    def spy(plan, **kw):
        placing = bool(kw.get("place"))
        out = orig(plan, **dict(kw, engine="heuristic"))   # fast; the gates read the class
        if placing:
            pid = max((p for p in CO.PARTIS if str(plan.get("id", "")).startswith(p)), key=len)
            nth = sum(1 for p, _t in calls if p == pid)
            calls.append((pid, kw.get("time_limit_s")))
            gr = out["plan"].setdefault("geometry_report", {})
            gr["refused"] = (None if nth >= 1 and pid in second_places
                             else copy.deepcopy(_ref(TF.UNDECIDED)))
        return out
    stub_pool_probe(monkeypatch)      # the placer is a spy; so no real probe
    monkeypatch.setattr(RV, "revise", spy)
    res = CO.compose(_brief(), candidates=candidates, revise=True, revise_rounds=0,
                     revise_engine="auto", revise_budget_s=budget)
    return res, calls


def _first_repeat(calls):
    seen = set()
    for i, (pid, _t) in enumerate(calls):
        if pid in seen:
            return i
        seen.add(pid)
    return len(calls)


def test_every_candidate_and_the_pool_are_placed_once_before_any_is_placed_twice(monkeypatch):
    res, calls = _compose(monkeypatch)
    order = [p for p, _t in calls]
    k = _first_repeat(calls)
    firsts, seconds = order[:k], order[k:]
    assert seconds, "premise: a native diagram refused UNDECIDED is retried (nothing was placed twice)"
    asked = [c["parti"] for c in res["candidates"] if c.get("rank_before") is not None][:3]
    assert len(set(firsts)) == len(firsts)
    # the whole asked set AND the pool-fill's placements come before the first second act
    pf = res["pool_fill"]
    pool_placed = [p["parti"] for p in pf["passed_over"]] + pf["added"]
    assert pf["placed_from_pool"] == CO.POOL_FILL_PLACEMENTS and len(pool_placed) == pf["placed_from_pool"]
    assert set(pool_placed) <= set(firsts), (
        "a pool diagram was first placed AFTER a retry: the retries ran before the pool-fill")
    assert len(firsts) == 3 + CO.POOL_FILL_PLACEMENTS, (firsts, seconds)
    # only a NATIVE diagram is placed twice (the retry's ruled scope), and at a longer limit
    limits = {}
    for pid, t in calls:
        limits.setdefault(pid, []).append(t)
    for pid in set(seconds):
        assert CO.nativity(pid, _brief()["style"]) == "native", pid
        assert limits[pid][1] > limits[pid][0], (pid, limits[pid])
    assert asked and set(asked) <= set(firsts), (asked, firsts)


def test_a_deferred_card_ends_on_what_its_second_act_found_and_says_each_thing_once(monkeypatch):
    target = "centre-passage-double-pile"
    res, calls = _compose(monkeypatch, second_places={target})
    card = next(c for c in res["candidates"] if c["parti"] == target)
    assert [p for p, _t in calls].count(target) == 2
    assert card["retry"]["outcome"] == "placed" and CO.placement_standing(card) == "placed"
    assert "deferred" not in card["retry"]["why"], "a card that was retried still says it is waiting"
    said = [d for d in card["decisions"] if d.startswith("PLACEMENT REFUSED")]
    assert len(said) == 1, f"the first refusal is said {len(said)} times: {said}"
    assert sum(1 for d in card["decisions"] if d.startswith("RETRY PLACED")) == 1
    # the BEFORE fields are the declared pass's, not the first placement's re-score
    base = CO.compose(_brief(), candidates=3, revise=False)
    declared = next(c for c in base["candidates"] + [None] if c and c["parti"] == target) \
        if any(c["parti"] == target for c in base["candidates"]) else None
    if declared is not None:
        assert card["score_before"] == declared["score"]
        assert card["counts_before"] == declared["counts"]
    for c in res["candidates"]:
        assert "_first" not in c and not any(k.startswith("_") for k in c), sorted(c)


def test_a_second_act_the_budget_cannot_hold_says_not_begun_and_never_stays_deferred(monkeypatch):
    """With a set budget that cannot hold a retry, every native card's reason is the gate's own
    NOT BEGUN sentence; nothing is placed twice, and no card is left saying 'deferred'."""
    res, calls = _compose(monkeypatch, budget=GEO.BUDGET_COMPOSE_S + 5.0)
    assert _first_repeat(calls) == len(calls), "a retry ran inside a budget that cannot hold one"
    for c in res["candidates"]:
        r = c.get("retry")
        if not r:
            continue
        assert "deferred" not in r["why"], (c["parti"], r["why"])
        if c["nativity"] == "native":
            assert r["why"].startswith("RETRY NOT BEGUN"), (c["parti"], r["why"])
            assert any("RETRY NOT BEGUN" in d for d in c["decisions"]), c["parti"]


def test_a_pool_diagram_a_second_act_places_joins_the_set_and_leaves_passed_over(monkeypatch):
    """Every asked candidate and every pool diagram is refused at first; a native diagram in the
    POOL that its retry then places is added to the set like any pool diagram found drawable."""
    res0, calls0 = _compose(monkeypatch, candidates=2)
    monkeypatch.undo()
    pool_natives = [p["parti"] for p in res0["pool_fill"]["passed_over"]
                    if CO.nativity(p["parti"], _brief()["style"]) == "native"]
    if not pool_natives:
        import pytest
        pytest.skip("COULD NOT EVALUATE: the pool-fill places no native diagram on this brief at "
                    "two candidates, so no pool diagram is retried")
    target = pool_natives[0]
    res, _calls = _compose(monkeypatch, second_places={target}, candidates=2)
    pf = res["pool_fill"]
    assert target in pf["added"] and target in pf.get("added_after_a_second_act", []), pf
    assert target not in [p["parti"] for p in pf["passed_over"]]
    assert target in [c["parti"] for c in res["candidates"]]
