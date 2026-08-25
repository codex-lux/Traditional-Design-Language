"""The 24 tools over HTTP.

Four things here are regressions waiting to happen, and each cost real debugging once:

  * **bare `/mcp`.** Starlette's `Mount("/mcp")` compiles to `^/mcp(?P<path>/.*)$` and does
    not match a path with no trailing slash — the request fell through to the SPA
    catch-all and answered `405 allow=GET` to a POST. Clients are handed `.../mcp`.
  * **the lifespan.** A mounted sub-app's own lifespan never runs; without the host app
    entering `session_manager.run()` every call raises "Task group is not initialized".
    These tests use `with TestClient(app)` precisely so the lifespan runs.
  * **DNS-rebinding protection.** Armed at localhost by default, so a real deployment
    hostname answers 421 to everything until allowlisted.
  * **metering scope.** Only the three heavy tools are capped; capping the 21 lookups
    would throttle exactly the progressive disclosure `tdl_overview` tells agents to do.
"""
import json

import pytest

from workbench.server import limits, mcp_mount

pytest.importorskip("mcp")

INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "test", "version": "0"}}}
HDRS = {"content-type": "application/json",
        "accept": "application/json, text/event-stream"}


def _body(r):
    """The endpoint may answer as JSON or as a one-event SSE stream."""
    text = r.text
    if text.lstrip().startswith("event:"):
        text = [ln[6:] for ln in text.splitlines() if ln.startswith("data: ")][0]
    return json.loads(text)


@pytest.fixture(scope="module")
def live():
    """A client whose lifespan has actually run, with the bearer token configured.

    MODULE-scoped, and it has to be: `session_manager.run()` raises if entered twice on
    the same instance, so the lifespan may be entered exactly once per process. That is
    also true of the deployed server — one process, one lifespan — but it means these
    tests share a client and must not depend on ordering. Env is set directly rather than
    through monkeypatch because that fixture is function-scoped.
    """
    import os
    from fastapi.testclient import TestClient
    from workbench.server.app import app

    saved = {k: os.environ.get(k) for k in ("WORKBENCH_API_TOKEN", "WORKBENCH_PASSWORD")}
    os.environ["WORKBENCH_API_TOKEN"] = "tok"
    os.environ.pop("WORKBENCH_PASSWORD", None)
    try:
        # base_url matters: TestClient's default Host is "testserver", which the
        # transport's DNS-rebinding protection correctly refuses with 421. Using a real
        # loopback host exercises the allowlist the way a local client does.
        with TestClient(app, base_url="http://127.0.0.1") as c:
            yield c
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@pytest.fixture(autouse=True)
def _clear_limits():
    limits.reset()
    yield
    limits.reset()


def _session(live):
    h = dict(HDRS, authorization="Bearer tok")
    r = live.post("/mcp", json=INIT, headers=h)
    assert r.status_code == 200, r.text
    proto = _body(r)["result"]["protocolVersion"]
    h["mcp-session-id"] = r.headers["mcp-session-id"]
    h["mcp-protocol-version"] = proto
    live.post("/mcp", json={"jsonrpc": "2.0", "method": "notifications/initialized"},
              headers=h)
    return h


def _call(live, h, name, args, i=99):
    r = live.post("/mcp", json={"jsonrpc": "2.0", "id": i, "method": "tools/call",
                                "params": {"name": name, "arguments": args}}, headers=h)
    return json.loads(_body(r)["result"]["content"][0]["text"])


def test_mcp_is_mounted():
    """Reads the state app.py built at import. Calling mcp_mount.build() again would
    create a SECOND session manager on the same MCPServer instance while the mounted app
    still holds the first — the lifespan then starts the wrong one and every request
    raises 'Task group is not initialized'. Build once per process."""
    from workbench.server.app import MCP_STATE
    assert MCP_STATE["mounted"] is True
    assert MCP_STATE["tools"] == 24
    assert set(MCP_STATE["metered"]) == mcp_mount.METERED


def test_bearer_is_required(live):
    assert live.post("/mcp", json=INIT, headers=HDRS).status_code == 401


def test_bare_mcp_path_works(live):
    """No trailing slash — this is the URL clients are given."""
    r = live.post("/mcp", json=INIT, headers=dict(HDRS, authorization="Bearer tok"))
    assert r.status_code == 200
    assert _body(r)["result"]["serverInfo"]["name"] == "traditional-design-language"


def test_all_24_tools_are_served(live):
    h = _session(live)
    r = live.post("/mcp", json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                  headers=h)
    names = [t["name"] for t in _body(r)["result"]["tools"]]
    assert len(names) == 24
    assert "tdl_overview" in names and "tdl_place_plan" in names


def test_a_real_tool_call_returns_corpus_data(live):
    h = _session(live)
    out = _call(live, h, "tdl_get_style", {"style_id": "tidewater-georgian"})
    assert "cascade" in out and "defining_characteristics" in out


def test_heavy_tools_are_capped_and_refuse_honestly(live, monkeypatch):
    monkeypatch.setenv("MCP_HEAVY_CALLS_PER_HOUR", "1")
    limits.reset()
    h = _session(live)
    with open("plans/tidewater-georgian-careful.json") as f:
        plan = json.load(f)

    first = _call(live, h, "tdl_check_plan", {"plan": plan}, 3)
    assert not first.get("refused"), "the first call is within the cap"

    second = _call(live, h, "tdl_check_plan", {"plan": plan}, 4)
    assert second["refused"] is True
    assert "reached" in second["reason"]
    # The refusal must not read as a verdict about the plan.
    assert "Nothing was evaluated" in second["note"]


def test_read_only_tools_are_never_capped(live, monkeypatch):
    monkeypatch.setenv("MCP_HEAVY_CALLS_PER_HOUR", "1")
    limits.reset()
    limits.take("mcp:heavy", limit=1, window_s=3600)   # spend the whole heavy budget
    h = _session(live)
    for i in range(4):
        out = _call(live, h, "tdl_overview", {}, 10 + i)
        assert not out.get("refused"), "corpus lookups must stay unmetered"


def test_allowed_hosts_includes_env_and_any_port(monkeypatch):
    monkeypatch.setenv("WORKBENCH_ALLOWED_HOSTS", "tdl.example.com, other.test")
    hosts = mcp_mount.allowed_hosts()
    assert "tdl.example.com" in hosts and "tdl.example.com:*" in hosts
    assert "other.test" in hosts
    assert "127.0.0.1" in hosts, "localhost must keep working for local dev"


def test_host_header_is_enforced(live):
    """DNS-rebinding protection is armed; a host we never allowlisted is refused."""
    h = dict(HDRS, authorization="Bearer tok", host="evil.example.com")
    assert live.post("/mcp", json=INIT, headers=h).status_code == 421
