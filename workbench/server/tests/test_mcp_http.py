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


@pytest.fixture(scope="session")
def live():
    """A client whose lifespan has actually run, with the bearer token configured.

    SESSION-scoped, and it has to be: `session_manager.run()` raises if entered twice on
    the same instance, so the lifespan may be entered exactly once per process. Module
    scope was not enough — a runner that interleaves modules (pytest-randomly, -xdist, a
    cross-file -k) tears the fixture down when it leaves this file and cannot re-enter it,
    turning seven tests into spurious errors. Session scope survives that. Env is set
    directly rather than through monkeypatch because that fixture is function-scoped.
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
    # Counted from the module the mount serves, so this fails if a tool disappears.
    # Asserting against mcp_mount's own literal would have been a constant compared with
    # itself — which is exactly what it was until the count was derived.
    from mcp_server import server as tdl_mcp
    live_tools = [n for n, v in vars(tdl_mcp).items()
                  if n.startswith("tdl_") and callable(v)]
    assert MCP_STATE["tools"] == len(live_tools) == 24


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


def test_a_pasted_url_is_normalised_to_a_hostname(monkeypatch):
    """The Host header carries no scheme, so an unparsed URL would never match and the
    endpoint would 421 with nothing obviously wrong."""
    monkeypatch.setenv("WORKBENCH_ALLOWED_HOSTS", "https://tdl.example.com/")
    assert "tdl.example.com" in mcp_mount.allowed_hosts()


@pytest.mark.parametrize("var", ["RAILWAY_PUBLIC_DOMAIN", "RAILWAY_STATIC_URL",
                                 "RAILWAY_SOMETHING_NEW_DOMAIN", "RENDER_EXTERNAL_URL"])
def test_platform_domain_is_discovered_without_configuration(monkeypatch, var):
    """Written without access to the platform's docs, so the scan matches by shape as
    well as by name — a variable this code has never heard of still has to work."""
    monkeypatch.delenv("WORKBENCH_ALLOWED_HOSTS", raising=False)
    monkeypatch.setenv(var, "tdl-production.up.railway.app")
    assert "tdl-production.up.railway.app" in mcp_mount.allowed_hosts()


def test_connection_strings_never_reach_the_allowlist(monkeypatch):
    """Regression for a credential leak introduced by scanning the environment wide.

    RAILWAY_DATABASE_URL=postgres://admin:hunter2@db.internal:5432/tdl parsed to the
    "hostname" admin:hunter2@db.internal:5432 — password included — which then went into
    the allowlist and out through /api/health, an ungated endpoint. Two independent
    defences, tested independently: the key is skipped, and the userinfo is stripped even
    if a key ever slips through.
    """
    monkeypatch.delenv("WORKBENCH_ALLOWED_HOSTS", raising=False)
    for var, val in [("RAILWAY_DATABASE_URL", "postgres://admin:hunter2@db.internal:5432/tdl"),
                     ("RAILWAY_REDIS_URL", "redis://default:pw@redis.internal:6379"),
                     ("RAILWAY_SECRET_URL", "https://user:pw@secret.example.com")]:
        monkeypatch.setenv(var, val)
    hosts = mcp_mount.allowed_hosts()
    joined = " ".join(hosts)
    assert "hunter2" not in joined and "@" not in joined, hosts
    assert not any("db.internal" in h or "redis.internal" in h for h in hosts), hosts


def test_userinfo_is_stripped_even_if_a_key_slips_through():
    """The second defence, exercised directly rather than through the key filter."""
    assert mcp_mount._hostname("postgres://admin:hunter2@db.internal:5432/tdl") \
        == "db.internal:5432"
    assert mcp_mount._hostname("https://tdl.up.railway.app/path?q=1") \
        == "tdl.up.railway.app"


def test_ungated_health_does_not_enumerate_hosts(live, monkeypatch):
    """/api/health is deliberately reachable without credentials, so it must not list
    hostnames — which can be internal service names."""
    import os
    saved = os.environ.get("WORKBENCH_PASSWORD")
    os.environ["WORKBENCH_PASSWORD"] = "pw"
    try:
        body = live.get("/api/health").json()
        assert "allowed_hosts" not in body["mcp"], body["mcp"]
        assert body["mcp"]["platform_host_detected"] in (True, False)
    finally:
        if saved is None:
            os.environ.pop("WORKBENCH_PASSWORD", None)
        else:
            os.environ["WORKBENCH_PASSWORD"] = saved


def test_platform_scan_ignores_values_that_are_not_hostnames(monkeypatch):
    """FLY_APP_NAME is a service name, not a host. Adding it would be noise at best."""
    monkeypatch.delenv("WORKBENCH_ALLOWED_HOSTS", raising=False)
    monkeypatch.setenv("FLY_APP_NAME", "my-app")
    assert "my-app" not in mcp_mount.allowed_hosts()


def test_local_dev_needs_no_configuration(monkeypatch):
    monkeypatch.delenv("WORKBENCH_ALLOWED_HOSTS", raising=False)
    for k in list(__import__("os").environ):
        if k.startswith(("RAILWAY_", "RENDER_", "FLY_")):
            monkeypatch.delenv(k, raising=False)
    assert mcp_mount.allowed_hosts() == ["127.0.0.1", "127.0.0.1:*", "localhost",
                                         "localhost:*", "[::1]", "[::1]:*"]


def test_host_header_is_enforced(live):
    """DNS-rebinding protection is armed; a host we never allowlisted is refused."""
    h = dict(HDRS, authorization="Bearer tok", host="evil.example.com")
    assert live.post("/mcp", json=INIT, headers=h).status_code == 421
