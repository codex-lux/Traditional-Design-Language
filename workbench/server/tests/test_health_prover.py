"""`/api/health` says what the prover runs on (26 Nov 2026).

Lucas read a set come back wholly refused on the deployed server, and nothing could say whether
that server gave the prover one core or eight: the deploy's CPU count was an open item of the
infrastructure audit and no route reported it. The health route reads it through the prover's own
functions, so it is the number a solve would use and not a second reading of the cgroup.
"""
import pytest

pytest.importorskip("fastapi", reason="COULD NOT EVALUATE: the workbench server needs fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from workbench.server import app as server  # noqa: E402


def _health():
    return TestClient(server.app).get("/api/health").json()


def test_health_reports_the_provers_workers_and_the_line_grid(monkeypatch):
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
    monkeypatch.setenv("TDL_CP_WORKERS", "3")
    monkeypatch.delenv("TDL_CP_LINE_GRID", raising=False)
    p = _health()["prover"]
    assert p == {"available": True, "workers": 3, "line_grid": True}, p
    monkeypatch.setenv("TDL_CP_WORKERS", "1")
    monkeypatch.setenv("TDL_CP_LINE_GRID", "0")
    p = _health()["prover"]
    assert p == {"available": True, "workers": 1, "line_grid": False}, p


def test_it_is_the_provers_own_reading_and_not_a_second_one(monkeypatch):
    """The route calls `geometry_cp.portfolio_workers`: stated there, it is what health says."""
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
    gc = server.core._mod("geometry_cp", server.os.path.join(server.core.ROOT, "build", "geometry_cp.py"))
    monkeypatch.setattr(gc, "portfolio_workers", lambda *a, **k: 7)
    assert _health()["prover"]["workers"] == 7


def test_without_the_solver_health_claims_nothing_about_it(monkeypatch):
    import builtins
    real = builtins.__import__

    def no_ortools(name, *a, **k):
        if name.startswith("ortools"):
            raise ImportError("no ortools")
        return real(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", no_ortools)
    assert server._prover_state() == {"available": False}
