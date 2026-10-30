"""The audit of Phase 17 (30 Oct 2026), finding 36: the solve cache keyed on (plan, parti, candidates,
seed, engine, time limit) and nothing about the prover's workers -- and since WP-17.5 the prover's
formulation turns on them (one worker runs the assumption ladder, several the hard portfolio first)
and on whether the portfolio lock was free. Reproduced on 739ff29 with the two-storey fixture: solved
on one worker and then on four with no clear, the second came back a cache hit with no portfolio
line; and a solve made with the lock held was cached for every later request.

The key carries `portfolio_workers()` now, and a CP answer is not cached where the CP leg did not
decide (UNKNOWN is this machine's load at that moment) or ran on fewer workers than the box offered
(the lock was contended). Every test here gives the solves a private cache before it patches
anything they read.
"""
import copy
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

G = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
GC = G._mod("geometry_cp", os.path.join(ROOT, "build", "geometry_cp.py"))


def _two_storey():
    p = GC._feasible_fixture()
    p["massing"] = "four-over-four"
    p["levels"][0]["rooms"][2]["hearth"] = [{"wall": "W", "width_in": 40.0}]
    p["levels"].append({"id": "upper", "index": 1, "floor_to_ceiling_ft": 9, "rooms": [
        {"id": "landing", "type": "landing", "width_ft": 8, "length_ft": 12,
         "stacks_over": "hall", "doors": [{"to": "chamber"}, {"to": "chamber2"}]},
        {"id": "chamber", "type": "bedroom", "width_ft": 13, "length_ft": 16,
         "exterior_walls": ["S", "W"], "stacks_over": "parlor", "doors": [{"to": "landing"}]},
        {"id": "chamber2", "type": "bedroom", "width_ft": 12, "length_ft": 14,
         "exterior_walls": ["N"], "stacks_over": "kitchen", "doors": [{"to": "landing"}]},
        {"id": "bath", "type": "bathroom", "width_ft": 8, "length_ft": 10,
         "exterior_walls": ["N", "E"], "doors": [{"to": "landing"}]},
    ]})
    return p


def _cp(out):
    sv = (out.get("geometry_report") or {}).get("solver") or {}
    if "error" in out or sv.get("engine") != "cp-sat":
        pytest.skip(f"COULD NOT EVALUATE: the fixture did not place on the prover on this machine "
                    f"({out.get('error') or sv.get('reason')})")
    return sv


def test_a_one_worker_answer_is_not_served_to_a_four_worker_request(monkeypatch):
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    plan = _two_storey()
    monkeypatch.setattr(GC, "portfolio_workers", lambda *a, **k: 1)
    one = _cp(G.solve(copy.deepcopy(plan), None, 80, engine="cp", time_limit_s=40))
    assert one["workers"] == 1 and len(G._SOLVE_CACHE) == 1, "premise: a decided one-worker solve is cached"
    monkeypatch.setattr(GC, "portfolio_workers", lambda *a, **k: 4)
    four = _cp(G.solve(copy.deepcopy(plan), None, 80, engine="cp", time_limit_s=40))
    assert four["workers"] == 4, "the four-worker request was served the one-worker answer"
    assert any(r.startswith("portfolio (4 workers)") for r in four["downgrade_rounds"]), four["downgrade_rounds"]
    # and the same request again IS a hit: the key is not simply never matching
    again = G.solve(copy.deepcopy(plan), None, 80, engine="cp", time_limit_s=40)
    assert again["geometry_report"]["solver"]["downgrade_rounds"] == four["downgrade_rounds"]
    assert len(G._SOLVE_CACHE) == 2


def test_a_solve_made_while_the_portfolio_lock_is_held_is_not_cached(monkeypatch):
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    monkeypatch.setattr(GC, "portfolio_workers", lambda *a, **k: 4)
    assert GC._PORTFOLIO_LOCK.acquire(blocking=False), "premise: no other solve holds the lock"
    try:
        sv = _cp(G.solve(_two_storey(), None, 80, engine="cp", time_limit_s=40))
    finally:
        GC._PORTFOLIO_LOCK.release()
    assert (sv["workers"], sv["workers_available"]) == (1, 4), "premise: the solve ran contended"
    assert G._SOLVE_CACHE == {}, "a placement decided under contention outlives the contention"


def _unknown(*_a, **_k):
    return {"unsolved": True, "status": "UNKNOWN", "attempts": [],
            "workers": 4, "workers_available": 4, "mode": "ladder"}


def test_a_cp_unknown_is_never_cached_and_the_fallback_says_what_it_ran_on(monkeypatch):
    """The fallback built on an UNKNOWN is the search's, labelled; caching it would serve a
    statement about one moment's load to every later request, and so would caching the forced-cp
    error. The fallback record carries the CP leg's run, so an UNKNOWN on one worker reads apart
    from one on four."""
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    monkeypatch.setattr(GC, "solve_cp", _unknown)
    out = G.solve(_two_storey(), None, 80, engine="auto", time_limit_s=40)
    sv = out["geometry_report"]["solver"]
    assert sv["engine"] == "heuristic" and sv["fallback"] == "budget", sv
    assert sv["cp_run"] == {"workers": 4, "workers_available": 4, "mode": "ladder", "status": "UNKNOWN"}
    assert G._SOLVE_CACHE == {}, "an UNKNOWN's fallback was cached"
    err = G.solve(_two_storey(), None, 80, engine="cp", time_limit_s=40)
    assert err.get("unsolved") and "error" in err
    assert G._SOLVE_CACHE == {}, "a forced-cp UNKNOWN was cached"


def test_the_cacheable_rule_reads_the_cp_leg_in_three_states():
    assert G._cacheable({}) is True, "the heuristic, or no CP leg: cached as before"
    assert G._cacheable({"cp": {"decided": True, "workers": 4, "workers_available": 4}}) is True
    assert G._cacheable({"cp": {"decided": True, "workers": 1, "workers_available": 1}}) is True, (
        "one worker on a one-core box is not contention")
    assert G._cacheable({"cp": {"decided": True, "workers": 1, "workers_available": 4}}) is False
    assert G._cacheable({"cp": {"decided": False, "workers": 4, "workers_available": 4}}) is False


# THE SECOND AUDIT OF PHASE 17 (30 Oct 2026): "decided" meant only "not unsolved", so a FEASIBLE
# answer whose type facts were released on an UNKNOWN scout, or whose reinstatement pass never
# reached a pin, was cached -- reproduced on the shipped Tidewater record at a 3 s budget (attempts
# `5b r5 A:UNKNOWN`, "64 never reached", served again in 0.0 s). Both are read off structure now.

def _feasible_res(attempts, reinstatement=None):
    return {"best": {}, "solver": {"engine": "cp-sat", "status": "FEASIBLE", "attempts": attempts,
                                   "reinstatement": reinstatement or {}}}


def test_an_answer_reached_through_an_unknown_feasibility_attempt_is_undecided():
    clean = [("5b hard0 4w", "H:INFEASIBLE"), ("5b r0", "A:INFEASIBLE"), ("5b r1", "A:OPTIMAL"),
             ("polish-a", "B:FEASIBLE")]
    assert G._cp_undecided(_feasible_res(clean)) == [], "premise: a decided ladder reads decided"
    for unk in (("5b r5", "A:UNKNOWN"), ("5b hard0 4w", "H:UNKNOWN")):
        why = G._cp_undecided(_feasible_res(clean + [unk]))
        assert len(why) == 1 and unk[1] in why[0], (unk, why)
    # read and said not read: a restore or a polish that ran out is not this rule's
    assert G._cp_undecided(_feasible_res(clean + [("restore wall x", "R:UNKNOWN"),
                                                  ("polish-h", "B:UNKNOWN")])) == []
    # a list round-tripped through JSON reads the same as the prover's tuples
    assert G._cp_undecided(_feasible_res([["5b r5", "A:UNKNOWN"]]))


def test_pins_the_reinstatement_pass_never_reached_make_the_answer_undecided():
    counts = GC.reinstate_counts(
        pending=[("wall", 0, "a", "N"), ("stack", 1, "b"), ("hearth", 0, "c")],
        offered={("wall", 0, "a", "N")},
        still_down={("stack", 1, "b"), ("hearth", 0, "c")}, refuted=set())
    assert counts == {"pending": 3, "offered": 1, "restored": 1, "refuted": 0, "never_reached": 2}
    why = G._cp_undecided(_feasible_res([("5b r0", "A:OPTIMAL")], counts))
    assert why == ["the reinstatement pass never reached 2 released pin(s)"], why
    assert G._cp_undecided(_feasible_res([("5b r0", "A:OPTIMAL")],
                                         dict(counts, never_reached=0))) == []


def _mark_unknown_scout(sv):
    sv["attempts"].append(("5b r5", "A:UNKNOWN"))


def _mark_never_reached(sv):
    sv["reinstatement"] = {"pending": 3, "offered": 0, "restored": 0, "refuted": 0,
                           "never_reached": 3}


@pytest.mark.parametrize("mark", [_mark_unknown_scout, _mark_never_reached],
                         ids=["unknown-scout", "never-reached"])
def test_a_feasible_answer_the_clock_wrote_is_not_cached(monkeypatch, mark):
    """Driven, because whether a real solve meets an UNKNOWN is the machine's load: the real prover
    places the fixture, and the record it returns is given one undecided mark. The premise -- the
    same solve unmarked IS cached -- is asserted first, so a cache that never writes cannot pass."""
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    plan = _two_storey()
    real = GC.solve_cp
    seen = []

    def kept(*a, **k):
        res = real(*a, **k)
        seen.append(res)
        return res
    monkeypatch.setattr(GC, "solve_cp", kept)
    sv = _cp(G.solve(copy.deepcopy(plan), None, 80, engine="cp", time_limit_s=40))
    if G._cp_undecided(seen[-1]):
        pytest.skip("COULD NOT EVALUATE: the fixture's own solve met the clock on this machine "
                    f"({G._cp_undecided(seen[-1])})")
    assert sv["engine"] == "cp-sat" and len(G._SOLVE_CACHE) == 1, \
        "premise: the same solve, decided, is cached"
    # the counts are WIRED, and agree with the pass's own line: a real solve that ran the pass
    # carries them, so `never_reached` is not a field nobody writes
    line = [r for r in sv["downgrade_rounds"] if r.startswith(GC.REINSTATE_NOTE_PREFIX)]
    rein = sv.get("reinstatement") or {}
    assert bool(line) == bool(rein), (line, rein)
    if line:
        assert line[0].startswith(f"{GC.REINSTATE_NOTE_PREFIX}{rein['pending']} released"), (line, rein)
        assert rein["pending"] == rein["offered"] + rein["never_reached"], rein

    def marked(*a, **k):
        res = real(*a, **k)
        if "solver" in res:
            mark(res["solver"])
        return res
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    monkeypatch.setattr(GC, "solve_cp", marked)
    out = G.solve(copy.deepcopy(plan), None, 80, engine="cp", time_limit_s=40)
    assert _cp(out)["engine"] == "cp-sat"
    assert G._SOLVE_CACHE == {}, "an answer resting on the clock was cached as decided"
