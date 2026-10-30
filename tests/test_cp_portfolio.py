"""WP-17.5: the prover can decide. Assumption literals force CP-SAT onto one sequential worker, and
on the composed two-storey houses a fact-holding placement that four workers find in seconds was
never reached on one. Every fact is posed HARD on a worker portfolio first; the assumption ladder
runs only where that does not decide, for its conflict cores.

These hold the worker count the portfolio reads, its override, and that one solve at a time takes
it -- two portfolio solves on one box would each take every core and both lose.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("geometry_cp_pf", ROOT / "build" / "geometry_cp.py")
GC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GC)


def test_the_override_wins_and_is_floored_at_one(monkeypatch):
    monkeypatch.setenv("TDL_CP_WORKERS", "3")
    assert GC.portfolio_workers() == 3
    monkeypatch.setenv("TDL_CP_WORKERS", "0")
    assert GC.portfolio_workers() == 1, "an override of 0 is one worker, never none"
    monkeypatch.setenv("TDL_CP_WORKERS", "not-a-number")
    assert 1 <= GC.portfolio_workers() <= GC.PORTFOLIO_MAX_WORKERS


def test_the_cgroup_quota_bounds_the_workers_and_not_the_hosts_cores(monkeypatch, tmp_path):
    monkeypatch.delenv("TDL_CP_WORKERS", raising=False)
    import builtins
    real_open = builtins.open
    quota = tmp_path / "cpu.max"

    def fake_open(path, *a, **k):
        if str(path) == "/sys/fs/cgroup/cpu.max":
            return real_open(quota, *a, **k)
        return real_open(path, *a, **k)
    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.setattr(GC.os, "sched_getaffinity", lambda _pid: set(range(16)))
    quota.write_text("200000 100000\n")
    assert GC.portfolio_workers() == 2, "a 2-CPU quota on a 16-core host is two workers"
    quota.write_text("150000 100000\n")
    assert GC.portfolio_workers() == 2, "a fractional quota rounds up"
    quota.write_text("max 100000\n")
    assert GC.portfolio_workers() == min(16, GC.PORTFOLIO_MAX_WORKERS), "no quota: the affinity, capped"


def test_one_solve_holds_the_portfolio_and_a_concurrent_one_runs_on_one_worker(monkeypatch):
    seen = []
    monkeypatch.setattr(GC, "portfolio_workers", lambda: 4)
    monkeypatch.setattr(GC, "_solve_cp", lambda *a, workers=1, **k: seen.append(workers) or {"ok": workers})
    assert GC.solve_cp({}, None) == {"ok": 4}
    assert GC._PORTFOLIO_LOCK.acquire(blocking=False)
    try:
        assert GC.solve_cp({}, None) == {"ok": 1}, "the lock is held: this solve takes one worker"
    finally:
        GC._PORTFOLIO_LOCK.release()
    assert seen == [4, 1]
    monkeypatch.setattr(GC, "portfolio_workers", lambda: 1)
    assert GC.solve_cp({}, None) == {"ok": 1}


def test_the_solver_report_names_the_portfolio_and_its_workers():
    import inspect
    src = inspect.getsource(GC._solve_cp)
    assert 'f"portfolio ({workers} workers): every type fact HELD"' in src
    assert "undecided or infeasible with every" in src
    assert "_harden(m_, q_)" in src, "the portfolio poses every fact HARD"


def test_a_wing_grows_with_the_house_and_stays_centred():
    """Ruling 4's third part with decision 11: where the prover grows the main block's depth before
    compromising a room, each dependency grows by the same even step, never past the main block,
    and stays exactly centred. Without it the composed centre passage's wing held 306 sf of rooms in
    an 18 x 17 ft box at every depth the prover tried."""
    import sys
    sys.path.insert(0, str(ROOT / "build"))
    import modcache
    CO = modcache.load("compose", str(ROOT / "build" / "compose.py"))
    G = modcache.load("geometry", str(ROOT / "build" / "geometry.py"))
    brief = {"id": "t", "style": "tidewater-georgian", "target_area_sf": 3200, "bedrooms": 4}
    plan, _log, p = CO.instantiate("centre-passage-double-pile", brief)
    _levels, prep = G.prep_rooms(plan)
    fpd = GC._snap_fpd(G.derive_footprint(plan, p, prep))
    base = {e["id"]: e for e in G.blocks_for(plan, fpd, prep, 0)}
    deps = [k for k, e in base.items() if e["role"] == "dependency"]
    assert deps, "the premise: the composed double pile has a service wing"
    grown = {e["id"]: e for e in G.blocks_for(plan, dict(fpd, H=fpd["H"] + 4, flank_grow_ft=4), prep, 0)}
    for k in deps:
        assert grown[k]["H"] == min(base[k]["H"] + 4, fpd["H"] + 4), (base[k], grown[k])
        assert grown[k]["y"] == (fpd["H"] + 4 - grown[k]["H"]) / 2, "exactly centred on the grown block"
    capped = {e["id"]: e for e in G.blocks_for(plan, dict(fpd, H=fpd["H"] + 2, flank_grow_ft=200), prep, 0)}
    assert all(capped[k]["H"] <= fpd["H"] + 2 for k in deps), "never deeper than the main block"
