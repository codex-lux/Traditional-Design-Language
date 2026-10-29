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
