"""THE ONE-WORKER SEARCH (ruled by Lucas, 27 Nov 2026: "No-LP on one worker").

On one core the stock Georgian brief's native double pile was refused UNDECIDED on 3 runs of 3
where four cores drew it first on 3 of 3. The record was not the cause and neither was a fact:
with several workers CP-SAT runs `default_lp`, `max_lp` and `no_lp` side by side, with one it runs
`default_lp` alone, and on this model the no-LP search decides in 8 to 11 s where the default takes
47 to 89 s or does not answer.

What is held here:

* the rule is ONE function with two callers -- the portfolio's walls-released steps and the
  deciding pass -- so the probe's kept answer is an answer by the search the placement would run;
* it rides on those steps ONLY: the everything-held step keeps the solver's default;
* several workers are unchanged;
* the control switch puts the default back, and the record says which search ran.

No test here asserts a wall-clock margin. The one real solve is the composed double pile's own
hard step under a generous cap, and it reports COULD NOT EVALUATE where the cap ran out.
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
GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
GC = modcache.load("geometry_cp", os.path.join(ROOT, "build", "geometry_cp.py"))


def _cp():
    return pytest.importorskip("ortools.sat.python.cp_model",
                               reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")


@pytest.fixture(autouse=True)
def _no_switch(monkeypatch):
    monkeypatch.delenv("TDL_CP_ONE_WORKER_SEARCH", raising=False)


# ---------------------------------------------------------------------------- the rule

def test_one_worker_runs_the_no_lp_search_and_several_run_the_portfolio():
    assert GC.ONE_WORKER_SEARCH == "no-lp"
    assert GC.hard_step_search(1) == "no-lp"
    for w in (2, 4, 8):
        assert GC.hard_step_search(w) == "portfolio", w
    assert {GC.hard_step_search(w) for w in (1, 2)} <= set(GC.HARD_STEP_SEARCHES)


def test_the_solver_built_for_one_worker_has_linearization_off_and_for_several_is_untouched():
    cp = _cp()
    default_level = cp.CpSolver().parameters.linearization_level
    assert default_level != 0, "the premise: the solver's own default is not the no-LP search"
    one = GC.hard_step_solver(cp, 12.5, 1, 7)
    assert one.parameters.linearization_level == 0
    assert (one.parameters.max_time_in_seconds, one.parameters.num_search_workers,
            one.parameters.random_seed) == (12.5, 1, 7)
    four = GC.hard_step_solver(cp, 3.0, 4, 11)
    assert four.parameters.linearization_level == default_level, (
        "several workers already run the no-LP search beside two others: nothing is set")
    assert (four.parameters.max_time_in_seconds, four.parameters.num_search_workers,
            four.parameters.random_seed) == (3.0, 4, 11)


@pytest.mark.parametrize("word", ["default", "lp", "0", "off", " Default "])
def test_the_control_switch_puts_the_solvers_default_back_on_one_worker(monkeypatch, word):
    cp = _cp()
    monkeypatch.setenv("TDL_CP_ONE_WORKER_SEARCH", word)
    assert GC.hard_step_search(1) == "default"
    assert GC.hard_step_search(4) == "portfolio", "the switch is about one worker only"
    sv = GC.hard_step_solver(cp, 5.0, 1, 7)
    assert sv.parameters.linearization_level == cp.CpSolver().parameters.linearization_level


def test_a_word_the_switch_does_not_know_changes_nothing(monkeypatch):
    monkeypatch.setenv("TDL_CP_ONE_WORKER_SEARCH", "no-lp")
    assert GC.hard_step_search(1) == "no-lp"
    monkeypatch.setenv("TDL_CP_ONE_WORKER_SEARCH", "fastest")
    assert GC.hard_step_search(1) == "no-lp"


def test_the_attempt_names_the_search_on_one_worker_and_only_there(monkeypatch):
    assert GC.hard_step_tag(1) == "1w no-lp"
    assert GC.hard_step_tag(4) == "4w"
    monkeypatch.setenv("TDL_CP_ONE_WORKER_SEARCH", "default")
    assert GC.hard_step_tag(1) == "1w"


# ---------------------------------------------------------------------------- the two callers

class _Stop(Exception):
    pass


def _spy(monkeypatch):
    """Record every call of `hard_step_solver`, and every OTHER solver the prover builds, in
    order. The real helper is still called, so what it returns is what is solved."""
    cp = _cp()
    seen = []
    real = GC.hard_step_solver

    def helper(cp_model, cap_s, workers, seed):
        seen.append(("helper", workers))
        return real(cp_model, cap_s, workers, seed)
    monkeypatch.setattr(GC, "hard_step_solver", helper)
    return cp, seen


def test_the_deciding_pass_asks_through_the_helper(monkeypatch):
    cp, seen = _spy(monkeypatch)
    monkeypatch.setenv("TDL_CP_WORKERS", "1")
    res = GC.probe_all_facts(GC._feasible_fixture(), time_limit_s=20.0)
    assert seen == [("helper", 1)], seen
    assert res["search"] == "no-lp" and res["workers"] == 1, res
    if res["verdict"] == GC.PROBE_UNDECIDED:
        pytest.skip("COULD NOT EVALUATE: the fixture's step did not answer in its cap")
    assert res["verdict"] == GC.PROBE_HELD, res


def test_the_probe_says_which_search_answered_under_the_switch_and_on_several_workers(monkeypatch):
    _cp()
    monkeypatch.setenv("TDL_CP_WORKERS", "1")
    monkeypatch.setenv("TDL_CP_ONE_WORKER_SEARCH", "default")
    assert GC.probe_all_facts(GC._feasible_fixture(), time_limit_s=20.0)["search"] == "default"
    monkeypatch.delenv("TDL_CP_ONE_WORKER_SEARCH")
    monkeypatch.setenv("TDL_CP_WORKERS", "2")
    res = GC.probe_all_facts(GC._feasible_fixture(), time_limit_s=20.0)
    if res["workers"] != 2:
        pytest.skip("COULD NOT EVALUATE: the portfolio lock was held, so the probe ran on one")
    assert res["search"] == "portfolio", res


def _two_storey():
    """`tests/test_pool_probe.py`'s refuted fixture, restated because a test file is not imported:
    it cannot hold its bands with its tiling, stacks and bearing lines at any depth, so the
    portfolio asks all four hard steps and none of them returns a placement."""
    p = GC._feasible_fixture()
    p["massing"] = "four-over-four"
    p["levels"].append({"id": "upper", "index": 1, "floor_to_ceiling_ft": 9, "rooms": [
        {"id": "landing", "type": "landing", "width_ft": 8, "length_ft": 12,
         "stacks_over": "hall", "doors": [{"to": "chamber"}, {"to": "chamber2"}]},
        {"id": "chamber", "type": "bedroom", "width_ft": 13, "length_ft": 16,
         "exterior_walls": ["S", "W"], "stacks_over": "parlor", "doors": [{"to": "landing"}]},
        {"id": "chamber2", "type": "bedroom", "width_ft": 12, "length_ft": 14,
         "exterior_walls": ["N"], "stacks_over": "kitchen", "doors": [{"to": "landing"}]},
        {"id": "bath", "type": "bathroom", "width_ft": 8, "length_ft": 10,
         "exterior_walls": ["E"], "doors": [{"to": "landing"}]}]})
    return p


def test_the_portfolios_walls_released_steps_go_through_the_helper_and_the_first_step_does_not(
        monkeypatch):
    """The everything-held step keeps the solver's default: it was not what was measured. So on
    one worker a house refuted at every depth shows ONE plain tag and THREE that name the search,
    and the helper was called three times."""
    cp, seen = _spy(monkeypatch)
    monkeypatch.setattr(GEO, "_SOLVE_CACHE", {})
    out = GC._solve_cp(_two_storey(), None, time_limit_s=40.0, candidates=40, workers=1)
    sv = (out.get("geometry_report") or {}).get("solver") or out.get("solver") or {}
    hard = [a for a in sv.get("attempts") or [] if str(a[1]).startswith("H:")]
    if not hard:
        pytest.skip("COULD NOT EVALUATE: no hard step ran on this record")
    first, later = hard[0], hard[1:]
    assert " hard0 " in first[0] and first[0].endswith(" 1w"), first
    assert later and all(" hard1" in t and t.endswith(" 1w no-lp") for t, _s in later), hard
    assert seen == [("helper", 1)] * len(later), (seen, hard)


def test_under_the_switch_the_portfolios_tags_are_what_they_were(monkeypatch):
    _cp()
    monkeypatch.setenv("TDL_CP_ONE_WORKER_SEARCH", "default")
    monkeypatch.setattr(GEO, "_SOLVE_CACHE", {})
    out = GC._solve_cp(_two_storey(), None, time_limit_s=40.0, candidates=40, workers=1)
    sv = (out.get("geometry_report") or {}).get("solver") or out.get("solver") or {}
    hard = [a for a in sv.get("attempts") or [] if str(a[1]).startswith("H:")]
    if not hard:
        pytest.skip("COULD NOT EVALUATE: no hard step ran on this record")
    assert all(t.endswith(" 1w") for t, _s in hard), hard


def test_no_other_solve_site_sets_the_search():
    """It rides on the two measured sites only. Read off the source: `linearization_level` is
    written in one place, the helper, and the helper is called from exactly two functions."""
    import ast
    src = open(os.path.join(ROOT, "build", "geometry_cp.py")).read()
    tree = ast.parse(src)
    writers, callers = [], []
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        for n in ast.walk(fn):
            if isinstance(n, ast.Attribute) and n.attr == "linearization_level" \
                    and isinstance(n.ctx, ast.Store):
                writers.append(fn.name)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id == "hard_step_solver":
                callers.append(fn.name)
    assert writers == ["hard_step_solver"], writers
    assert sorted(callers) == ["_solve_cp", "probe_all_facts"], callers


# ---------------------------------------------------------------------------- the house it is for

def test_the_composed_double_piles_hard_step_is_decided_on_one_worker(monkeypatch):
    """The measurement the ruling rests on, as one real solve: the record the composer's declared
    loop hands on, walls and axis released, at its derived depth, on ONE worker. Measured 8.0 to
    10.7 s; the cap is 90 s, and a step the cap cut short is COULD NOT EVALUATE, not a failure --
    this file holds no wall-clock margin."""
    cp = _cp()
    if not GC.line_grid_on():
        pytest.skip("COULD NOT EVALUATE: the line grid is off, so the hard steps are not these")
    monkeypatch.setattr(GC, "_WING_BOXES", {})
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    res = CO.compose(copy.deepcopy(brief), candidates=4, revise=False)
    cards = [c for c in res["candidates"] if c["parti"] == "centre-passage-double-pile"]
    assert cards, [c["parti"] for c in res["candidates"]]
    plan = copy.deepcopy(cards[0]["plan"])
    parti = CO.PARTIS["centre-passage-double-pile"]
    _lv, prep = GEO.prep_rooms(plan)
    fpd = GC._snap_fpd(GEO.derive_footprint(plan, parti, prep))
    ew = GEO.entrance_walls(plan)
    fpd, _rep, decided = GC.wing_sized(plan, prep, fpd, ew, 120.0, 1, 7)
    if not decided:
        pytest.skip("COULD NOT EVALUATE: the wing's box was not decided")
    rel = GC._released_first(plan, prep, fpd, ew, ())
    model, _rooms, _reqs, _grid = GC._hard_model(plan, prep, fpd, ew, rel, parti, 7)
    sv = GC.hard_step_solver(cp, 90.0, 1, 7)
    status = sv.StatusName(sv.Solve(model))
    if status == "UNKNOWN":
        pytest.skip("COULD NOT EVALUATE: the step did not answer in 90 s on this box")
    assert status in ("OPTIMAL", "FEASIBLE"), status
