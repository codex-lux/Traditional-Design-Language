"""The composer's set budget is a REAL ceiling (R12, ruled by Lucas 30 Oct 2026), and its pieces
are held one by one -- the Phase 17 audit's findings 4, 5 and 53.

Finding 4: the per-candidate share cap (`1.5 x BUDGET_COMPOSE_S`) had no test that could fail --
the only spy test stated a 90 s budget, whose share is at most 30 -- and the comment beside the
budget still said each first placement was "up to a 25 s proof" with a worst case of "candidates x
~35 s". Under R12 the share is a pure function (`candidate_share`), the first placement is asked
under it (`placement_time_limit_s`), and `revise(..., reserve_round=True)` begins a round, a retry
or the reclaim only where what is left can hold one -- refusing and SAYING one that cannot.

Finding 5: `SET_BUDGET_MAX_S` is a second spelling of `core.REVISE_MAX_BUDGET_S`, and the comment's
guarantee -- a derived budget "can never exceed one a caller is allowed to state" -- was held by
nothing. `core` loads the composer, so the join is a test and not an import.

Finding 53: `tdl_compose` let no caller state a budget, so every MCP compose took the derived one,
and its docstring said nothing of it.
"""
import inspect
import json
import os
import sys
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, ROOT)
import modcache  # noqa: E402

CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
G = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
RV = modcache.load("revise", os.path.join(ROOT, "build", "revise.py"))
from mcp_server import core  # noqa: E402


# --------------------------------------------------------------------- finding 4: the share
def test_the_share_is_capped_at_a_placement_and_a_half():
    cap = 1.5 * G.BUDGET_COMPOSE_S
    assert cap == 90.0, "the premise: the cap is 1.5 x the compose per-placement budget"
    # the derived budget for four candidates, over four: the cap binds (140 uncapped)
    assert CO.candidate_share(CO.set_budget_s(4), 4) == cap
    assert CO.candidate_share(420.0, 2) == cap                 # 210 uncapped
    # and an uncapped case, so a cap at a constant cannot pass for the share
    assert CO.candidate_share(90.0, 3) == 30.0
    # never under a second where a second is left; never more than is left
    assert CO.candidate_share(0.5, 3) == 0.5
    assert CO.candidate_share(2.0, 4) == 1.0
    assert CO.candidate_share(None, 3) is None


def test_the_first_placement_is_asked_under_its_share():
    assert CO.placement_time_limit_s(None) == G.BUDGET_COMPOSE_S, "no budget: the compose budget"
    assert CO.placement_time_limit_s(30.0) == 30.0, "a share under a placement bounds it (R12)"
    assert CO.placement_time_limit_s(90.0) == G.BUDGET_COMPOSE_S, "a share over it does not raise it"
    assert CO.placement_time_limit_s(0.2) == 1.0, "never asked under a second"


def test_the_set_loop_and_the_named_diagram_read_the_one_share():
    # one spelling: the set loop and the appended named diagram both call `candidate_share`, and the
    # inline `max(remaining / ...)` arithmetic is gone from compose()
    src = inspect.getsource(CO.compose)
    assert src.count("candidate_share(") >= 2, "the set loop and the named diagram read the share"
    assert "remaining / (n_out" not in src, "a second spelling of the share in compose()"
    assert "1.5 * _GEO.BUDGET_COMPOSE_S" not in src, "the cap is spelled in candidate_share alone"
    assert "time_limit_s=_GEO.BUDGET_COMPOSE_S" not in src, (
        "a first placement asked under the whole compose budget whatever its share (R12)")
    assert "reserve_round=" in src, "the loop is asked to refuse a round it cannot fit"


def test_the_derived_budget_for_four_candidates_is_560_and_600_binds_from_five():
    # the audit's (b): the report compared a 592 s run to the 600 s ceiling; for four candidates the
    # derived figure is 560 s and 600 binds only from five
    assert CO.set_budget_s(4) == 560.0
    assert CO.set_budget_s(5) == CO.SET_BUDGET_MAX_S == 600.0


# --------------------------------------------------------------------- finding 5: the join
def test_a_derived_budget_never_exceeds_one_a_caller_may_state():
    assert CO.SET_BUDGET_MAX_S <= core.REVISE_MAX_BUDGET_S, (
        "the composer's bound on a DERIVED budget exceeds the bound on a STATED one")
    for c in range(1, core.COMPOSE_MAX_CANDIDATES + 1):
        assert CO.set_budget_s(c) <= core.REVISE_MAX_BUDGET_S, c


# --------------------------------------------------------- R12: a round that cannot fit is refused
class _Clock:
    """A clock for `revise` alone: it advances only when the stub critique says a solve ran, so the
    reservation is decided on figures this test states rather than on the machine's speed."""
    def __init__(self):
        self.t = 0.0

    def perf_counter(self):
        return self.t


def _drive(monkeypatch, reserve, budget, solve_s=10.0):
    clock = _Clock()
    monkeypatch.setattr(RV, "time", types.SimpleNamespace(perf_counter=clock.perf_counter))
    calls = []
    orig = RV.CR.critique

    def crit(p, **kw):
        calls.append(kw.get("time_limit_s"))
        out = orig(p, **kw)
        clock.t += solve_s                   # every placement costs `solve_s` on revise's clock
        return out
    monkeypatch.setattr(RV.CR, "critique", crit)
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"), encoding="utf-8"))
    out = RV.revise(plan, rounds=2, engine="heuristic", budget_s=budget, place=True,
                    time_limit_s=5.0, reserve_round=reserve)
    return out, calls


def test_a_round_that_cannot_fit_in_what_is_left_is_refused_and_said(monkeypatch):
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    # first placement 10 s of a 15 s budget: 5 s left and a round re-places at up to 10 s
    out, calls = _drive(monkeypatch, reserve=True, budget=15.0)
    rep = out["report"]
    br = rep.get("budget_refused")
    assert br and br["what"] == "round", rep.get("stop_reason")
    assert rep["stop_reason"] == "budget" and len(calls) == 1, "no round was begun"
    assert br["elapsed_s"] + br["round_cost_s"] > br["budget_s"] >= br["elapsed_s"]
    assert "refused rather than begun past the budget" in br["why"]


def test_without_the_reservation_the_same_round_is_begun(monkeypatch):
    # the control: the loop as every other caller has it begins the round the reservation refuses
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    out, calls = _drive(monkeypatch, reserve=False, budget=15.0)
    rep = out["report"]
    assert "budget_refused" not in rep
    assert not (rep["stop_reason"] == "budget" and len(calls) == 1), (rep["stop_reason"], len(calls))


def test_a_round_that_fits_is_begun_under_the_reservation(monkeypatch):
    # 10 s of a 25 s budget: a 10 s round fits, so the reservation refuses nothing at round 1
    monkeypatch.setattr(G, "_SOLVE_CACHE", {})
    out, calls = _drive(monkeypatch, reserve=True, budget=25.0)
    rep = out["report"]
    assert not (rep.get("budget_refused") and rep["budget_refused"]["what"] == "round"
                and len(calls) == 1), rep.get("budget_refused")


def test_the_prover_engines_reserve_their_time_limit_however_fast_the_first_solve():
    # on an engine that runs the prover a round may run to its limit after a move, so the reserved
    # cost is never under `time_limit_s`; on the search it is the measured first placement
    src = inspect.getsource(RV.revise)
    assert 'max(first_placement_s, 0.0 if engine == "heuristic" else float(time_limit_s))' in src


# ----------------------------------------------------------------- finding 53: tdl_compose's budget
def test_tdl_compose_forwards_a_stated_budget_and_omits_none(monkeypatch):
    pytest.importorskip("mcp")
    from mcp_server import server
    got = {}
    monkeypatch.setattr(server, "_metered", lambda name: None)
    monkeypatch.setattr(server.core, "compose", lambda *a, **kw: got.update(kw) or {"candidates": []})
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json"), encoding="utf-8"))
    server.tdl_compose(brief, revise_budget_s=120.0)
    assert got["revise_budget_s"] == 120.0
    got.clear()
    server.tdl_compose(brief)
    assert got["revise_budget_s"] is None, "an omitted budget reaches the composer as None (derived)"


def test_tdl_compose_states_its_budget_and_the_pool_fill_in_its_own_words():
    src = open(os.path.join(ROOT, "mcp_server", "server.py"), encoding="utf-8").read()
    i = src.index("def tdl_compose(")
    j = src.index("@mcp.tool()", i)
    body = src[i:j]
    assert "revise_budget_s: float | None = None" in body
    assert "revise_budget_s=revise_budget_s" in body, "the stated budget is forwarded"
    # `stopped_by` since the audit's finding 26: the tool says which bound left a diagram unreached
    for words in ("revise_budget_s", "560 s", "pool_fill", "not refused", "drawable where judged",
                  "stopped_by", "appended_as_named"):
        assert words in body, words


def test_core_bounds_a_stated_budget_and_passes_none_through(monkeypatch):
    got = {}

    class FakeComposer:
        def check_brief_refs(self, brief):
            return None

        def compose(self, brief, candidates, **kw):
            got.update(kw)
            return {"candidates": []}
    monkeypatch.setattr(core, "_composer", lambda: FakeComposer())
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json"), encoding="utf-8"))
    core.compose(brief, revise_budget_s=10 ** 6)
    assert got["revise_budget_s"] == core.REVISE_MAX_BUDGET_S
    got.clear()
    core.compose(brief)
    assert got["revise_budget_s"] is None
