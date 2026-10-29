"""WP-17.6, ruling 3 of 29 Oct 2026: a short set is FILLED FROM THE POOL.

Until this, the four candidates were chosen before any was placed and nothing tried for a drawable
house: on Lucas's brief four of four came back refused while nothing further down the ranked pool
was ever placed. Where fewer of the set may be drawn than were asked for, the placed loop places
down the pool -- at most `POOL_FILL_PLACEMENTS`, inside the set's budget -- and a candidate it finds
drawable joins the set. Every diagram placed and still refused is named with its reason, every one
the budget or the bound did not reach is named, and the set keeps the 16 Oct key (ruling 7).

The verdict on each placement is STATED by a spy over the real placed loop, on the search engine
with no rounds, because a real compose refuses or draws by the placer's lights and this file's
subject is what the composer does with each answer, not what the placer answers.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
RV = modcache.load("revise", os.path.join(ROOT, "build", "revise.py"))

REFUSED = {"kind": "type-fact-downgraded", "facts": ["stacks"], "conflicts": [], "lines": []}


def _brief():
    return json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json"), encoding="utf-8"))


def _compose(monkeypatch, drawable, candidates=2, revise=True, budget=600):
    """Compose with every placement's verdict stated: a parti in `drawable` may be drawn, every
    other one is refused. Returns the result and the partis placed, in order."""
    placed = []
    orig = RV.revise

    def spy(plan, **kw):
        out = orig(plan, **kw)
        if kw.get("place"):
            pid = max((p for p in CO.PARTIS if str(plan.get("id", "")).startswith(p)), key=len)
            placed.append(pid)
            gr = out["plan"].setdefault("geometry_report", {})
            gr["refused"] = None if pid in drawable else dict(REFUSED)
        return out
    monkeypatch.setattr(RV, "revise", spy)
    res = CO.compose(_brief(), candidates=candidates, revise=revise, revise_rounds=0,
                     revise_engine="heuristic", revise_budget_s=budget)
    return res, placed


_BASELINE = {}


def _baseline(monkeypatch):
    """The pool's order, learnt once with nothing drawable (a compose is the slow part of this
    file, and the order is the same for every test that reads it)."""
    if "v" not in _BASELINE:
        _BASELINE["v"] = _compose(monkeypatch, drawable=set())
        monkeypatch.undo()
    return _BASELINE["v"]


def test_a_set_with_nothing_drawable_places_down_the_pool_and_takes_what_it_finds(monkeypatch):
    # first learn the pool's order with nothing drawable, then make the third pool diagram drawable
    res0, placed0 = _baseline(monkeypatch)
    asked = placed0[:2]
    pool = placed0[2:]
    assert len(pool) == CO.POOL_FILL_PLACEMENTS, (
        f"with nothing drawable the loop places the whole bound: {placed0}")
    pf0 = res0["pool_fill"]
    assert pf0["added"] == [] and pf0["placed_from_pool"] == CO.POOL_FILL_PLACEMENTS
    assert [p["parti"] for p in pf0["passed_over"]] == pool
    assert all(p["why"] == "refused: stacks" for p in pf0["passed_over"])
    assert [c["parti"] for c in res0["candidates"]] and len(res0["candidates"]) == 2

    target = pool[2]
    res, placed = _compose(monkeypatch, drawable={target})
    pf = res["pool_fill"]
    assert placed[:2] == asked, "the set asked for is placed first, in rank order"
    assert pf["added"] == [target]
    # one drawable is not enough for a set of two: the loop keeps going to its bound, and every
    # diagram it placed and found refused, before the drawable one and after it, is named
    assert [p["parti"] for p in pf["passed_over"]] == [p for p in pool if p != target]
    assert pf["placed_from_pool"] == CO.POOL_FILL_PLACEMENTS
    assert len(placed) == 2 + CO.POOL_FILL_PLACEMENTS
    returned = [c["parti"] for c in res["candidates"]]
    assert set(returned) == set(asked) | {target}
    keys = [CO.rank_key(c) for c in res["candidates"]]
    assert keys == sorted(keys), "the filled set keeps the one key (ruling 7)"
    assert any("placed from further down the ranked pool" in ln for ln in res["how_to_read_this"])


def test_the_loop_stops_once_as_many_may_be_drawn_as_were_asked_for(monkeypatch):
    res0, placed0 = _baseline(monkeypatch)
    asked, pool = placed0[:2], placed0[2:]
    res, placed = _compose(monkeypatch, drawable={asked[0], pool[0]})
    assert placed == asked + pool[:1], "it stops the moment the set holds two drawable houses"
    assert res["pool_fill"]["added"] == [pool[0]] and res["pool_fill"]["not_reached"] == []


def test_a_set_that_may_all_be_drawn_places_nothing_more(monkeypatch):
    res0, placed0 = _baseline(monkeypatch)
    res, placed = _compose(monkeypatch, drawable=set(placed0))
    assert len(placed) == 2
    pf = res["pool_fill"]
    assert pf["placed_from_pool"] == 0 and pf["added"] == [] and pf["passed_over"] == []
    assert not any("further down the ranked pool" in ln for ln in res["how_to_read_this"])


def test_a_spent_budget_names_what_it_did_not_reach(monkeypatch):
    # a budget too small for anything past the set: the pool-fill does not start, and says so
    res, placed = _compose(monkeypatch, drawable=set(), budget=0.5)
    pf = res["pool_fill"]
    assert pf["placed_from_pool"] == 0
    assert pf["not_reached"], "a diagram the budget did not reach is named, never left out in silence"


def test_revise_false_places_nothing_and_says_nothing_about_a_pool(monkeypatch):
    res, placed = _compose(monkeypatch, drawable=set(), revise=False)
    assert placed == [] and "pool_fill" not in res
