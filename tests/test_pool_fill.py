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


# ------------------------------------------------------------------------------------------------
# THE PHASE 17 AUDIT, FINDINGS 1 AND 31, AND R10 (ruled 30 Oct 2026). The fill counted a candidate
# as drawable on `revision is not None and not refused` -- a second spelling of standing -- so a
# loop whose first placement could NOT BE EVALUATED (`refused` None, nothing judged) counted toward
# `have`, could stop the fill, and was added as found. Every spy card above carries stop_reason
# 'no-rounds' and `refused` None or a refusal, so the two spellings agreed on every one of them: a
# fixture where both branches return the same answer guards neither. These state a THIRD verdict.
def _compose3(monkeypatch, drawable, unjudged, candidates=2, brief=None):
    """`_compose` with a third verdict: a parti in `unjudged` is a loop whose first placement could
    not be evaluated (stop_reason PLACEMENT_UNJUDGED, no geometry_report, so `refused` None)."""
    placed = []
    orig = RV.revise

    def spy(plan, **kw):
        out = orig(plan, **kw)
        if kw.get("place"):
            pid = max((p for p in CO.PARTIS if str(plan.get("id", "")).startswith(p)), key=len)
            placed.append(pid)
            if pid in unjudged:
                out["report"]["stop_reason"] = RV.STOP_PLACEMENT_UNJUDGED
                out["report"]["placement_unjudged"] = "unsolved"
                out["plan"].pop("geometry_report", None)
            else:
                gr = out["plan"].setdefault("geometry_report", {})
                gr["refused"] = None if pid in drawable else dict(REFUSED)
        return out
    monkeypatch.setattr(RV, "revise", spy)
    res = CO.compose(brief or _brief(), candidates=candidates, revise=True, revise_rounds=0,
                     revise_engine="heuristic", revise_budget_s=600)
    return res, placed


def test_a_placement_that_could_not_be_evaluated_is_not_counted_drawable(monkeypatch):
    res0, placed0 = _baseline(monkeypatch)
    asked, pool = placed0[:2], placed0[2:]
    # one asked candidate may be drawn; the first pool diagram could not be judged; the second is
    # drawable. The old spelling counted the unjudged one, stopped the fill at two, and added it.
    res, placed = _compose3(monkeypatch, drawable={asked[0], pool[1]}, unjudged={pool[0]})
    pf = res["pool_fill"]
    assert pool[0] not in pf["added"], "an unjudged placement was added to the set as drawable"
    assert pf["added"] == [pool[1]], "the fill went on past it to the drawable diagram"
    assert placed == asked + pool[:2]
    entry = next(p for p in pf["passed_over"] if p["parti"] == pool[0])
    assert entry["standing"] == "unjudged"
    assert "could not be evaluated" in entry["why"] and "refused" not in entry["why"]
    assert pool[0] not in [c["parti"] for c in res["candidates"]], "the unjudged diagram is not returned"
    line = next(ln for ln in res["how_to_read_this"] if "further down the ranked pool" in ln)
    assert "1 whose placement could not be judged" in line and "0 still refused" in line, line
    # R10: both counts, over the returned set, every compose that placed
    dr = res["drawability"]
    assert dr["returned"] == 3 and dr["not_refused"] == 2, dr
    assert any(ln.startswith("Of the 3 candidate(s) returned, 2 not refused")
               for ln in res["how_to_read_this"])


def test_a_named_diagram_returned_anyway_is_counted_apart_and_the_asked_count_is_the_asked(monkeypatch):
    # finding 6: the appended-named line said "among the {len(returned) - 1} candidate(s) asked
    # for", which counts a pool-filled house as asked; and the named diagram the fill had placed
    # and not taken sat in `passed_over` uncounted apart while it was returned
    res0, placed0 = _baseline(monkeypatch)
    asked, pool = placed0[:2], placed0[2:]
    brief = _brief()
    brief["parti"] = pool[1]
    res, placed = _compose3(monkeypatch, drawable={pool[0]}, unjudged=set(), brief=brief)
    assert res["named_parti"]["appended"] is True
    line = next(ln for ln in res["how_to_read_this"] if ln.startswith(f"The brief named {pool[1]}."))
    assert "among the 2 candidate(s) asked for (and the 1 the pool-fill added)" in line, line
    entry = next(p for p in res["pool_fill"]["passed_over"] if p["parti"] == pool[1])
    assert entry.get("appended_as_named") is True
    pline = next(ln for ln in res["how_to_read_this"] if "further down the ranked pool" in ln)
    assert "returned anyway as the diagram the brief named" in pline, pline


# --- the pure halves, driven on cards this test writes (milliseconds, no compose) ---------------
def _card(parti, refused=None, stop="no-rounds", revision=True, unjudged_reason=None, drawability=None):
    rv = None if not revision else {"stop_reason": stop, "placement_unjudged": unjudged_reason}
    return {"parti": parti, "parti_name": parti.title(), "refused": refused, "revision": rv,
            "drawability": drawability}


def test_the_passed_over_reason_is_in_the_terms_of_the_standing():
    ref = CO.passed_over_entry(_card("a", refused=dict(REFUSED)))
    assert ref["standing"] == "refused" and ref["why"] == "refused: stacks"
    unj = CO.passed_over_entry(_card("b", stop=CO.PLACEMENT_UNJUDGED, unjudged_reason="unsolved"))
    assert unj["standing"] == "unjudged"
    assert unj["why"] == "its placement could not be evaluated: unsolved"
    odd = CO.passed_over_entry(_card("c", refused={"kind": "not-a-kind-anyone-wrote"}))
    assert odd["standing"] == "unjudged" and "could not be read" in odd["why"]
    wrapped = CO.passed_over_entry(_card("d", refused={"refused_placement": dict(REFUSED)}))
    assert wrapped["standing"] == "refused" and wrapped["why"] == "refused: stacks"


def test_set_drawability_gives_two_counts_and_names_each_unjudged_fact():
    cards = [_card("a", drawability={"where_judged": True, "drawable": False, "unjudged": ["hearth"]}),
             _card("b", drawability={"where_judged": False, "drawable": False, "unjudged": ["hearth"]}),
             _card("c", refused=dict(REFUSED), drawability={"where_judged": False, "unjudged": []}),
             _card("d", stop=CO.PLACEMENT_UNJUDGED)]
    d = CO.set_drawability(cards)
    assert d == {"returned": 4, "not_refused": 2, "drawable_where_judged": 1,
                 "unjudged_facts": {"hearth": 2}}
    line = CO.drawability_line(d)
    assert "2 not refused, 1 drawable where judged (hearth unjudged on 2)" in line
    assert "not counted as held" in line


def test_a_card_counts_drawable_where_judged_off_the_instruments_verdict_and_not_its_strict_flag(monkeypatch):
    """Integrating the audit's batches (30 Oct 2026): batch D's card read `assess()["drawable"]`,
    which batch B made the STRICT state. No composed house reaches it while none states a fire, so
    every set read "0 drawable where judged" over houses the instrument calls drawable where judged.
    Driven on `assess` itself, for each of the four verdicts."""
    DR = CO._mod("drawability", os.path.join(ROOT, "build", "drawability.py"))
    plan = {"id": "x", "geometry_report": {"solver": {}},
            "levels": [{"index": 0, "rooms": [{"id": "r", "geometry": {"x": 0, "y": 0, "w": 1, "h": 1}}]}]}
    want = {DR.DRAWABLE: True, DR.DRAWABLE_WHERE_JUDGED: True, DR.NOT_DRAWABLE: False,
            DR.COULD_NOT_EVALUATE: False}
    for verdict, where in want.items():
        fake = {"verdict": verdict, "drawable": verdict == DR.DRAWABLE,
                "unjudged": ["hearth"] if verdict == DR.DRAWABLE_WHERE_JUDGED else []}
        monkeypatch.setattr(DR, "assess", lambda p, _f=fake: dict(_f))
        card = CO.card_drawability(plan)
        assert card["verdict"] == verdict and card["where_judged"] is where, (verdict, card)
    assert card["unjudged"] == []
    monkeypatch.setattr(DR, "assess", lambda p: {"verdict": DR.DRAWABLE_WHERE_JUDGED, "drawable": False,
                                                 "unjudged": ["hearth", "continuity_whole_run"]})
    card = CO.card_drawability(plan)
    assert card["unjudged"] == ["hearth", "continuity_whole_run"], "the instrument's list, unrenamed"
    d = CO.set_drawability([{"parti": "a", "refused": None, "revision": {"stop_reason": "no-rounds"},
                             "drawability": card}])
    assert d["drawable_where_judged"] == 1, d


def test_the_pool_fill_line_counts_refused_and_unjudged_apart():
    pf = {"placed_from_pool": 3, "added": ["x"],
          "passed_over": [{"parti": "a", "standing": "refused"}, {"parti": "b", "standing": "unjudged"}]}
    line = CO.pool_fill_line(pf, 2)
    assert "1 placed and not refused and added to the set (x)" in line
    assert "1 still refused, 1 whose placement could not be judged" in line
    assert "drawable and added" not in line, "the fill takes 'not refused', which is not 'drawable'"
