"""Serving the 24 MCP tools over HTTP, from the same process as the workbench.

VISION.md §IX has two audiences reaching one corpus. WP-5.2 gave the human one an
interface; this gives the agent one an address. `mcp_server/server.py` is unchanged in
what it does — the same 24 tools over the same `core.py` — and does not know which
transport it is answering on. Stdio keeps working exactly as it did.

Mounting rather than running a second service means one process, one origin, one auth
boundary and one copy of the 27 MB corpus in memory: `mcp_server/server.py` and
`workbench/server/corpus.py` both resolve `core` to the same top-level module.

Four things about the SDK that are easy to get wrong, each verified against the installed
version rather than taken from memory:

1. **The session manager is lazy.** `mcp.session_manager` raises until
   `streamable_http_app()` has been called, so the app is built at import time and the
   host lifespan reaches for the manager afterwards.
2. **A mounted sub-app's lifespan never runs.** The host app must enter
   `session_manager.run()` itself or every call fails with "Task group is not
   initialized". That happens in `app.py`'s lifespan.
3. **DNS-rebinding protection is armed at localhost by default**, so behind a real
   hostname the server answers `421 Misdirected Request` to everything until the host is
   allowlisted. `WORKBENCH_ALLOWED_HOSTS` does that.
4. **`host=` does not allowlist.** Passing a non-localhost `host=` merely disarms the
   protection and leaves every Host and Origin accepted. It is deliberately never passed
   here; `transport_security=` is the only control used.

The default path is `/mcp`, so mounting at `/mcp` would serve `/mcp/mcp` —
`streamable_http_path="/"` puts it back where clients expect it.
"""
import os


def allowed_hosts():
    """Hosts this deployment answers to. Localhost always; deployment hosts by env."""
    hosts = ["127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*", "[::1]", "[::1]:*"]
    for h in (os.environ.get("WORKBENCH_ALLOWED_HOSTS") or "").split(","):
        h = h.strip()
        if not h:
            continue
        hosts.append(h)
        if ":" not in h:
            hosts.append(f"{h}:*")   # the same host on any port, per the SDK's matching
    return hosts


def build():
    """Return (asgi_app, state). asgi_app is None when MCP is unavailable.

    Unavailable is a reported state, never a silent one — /api/health carries `state` so
    an operator can tell "the SDK is not installed" from "it is mounted and working",
    rather than finding out from a 404.
    """
    try:
        from mcp.server.transport_security import TransportSecuritySettings
    except ImportError as e:
        return None, {"mounted": False,
                      "note": f"{e.name} is not installed — the MCP endpoint is off. "
                              f"pip install -r workbench/requirements.txt"}
    try:
        from mcp_server import server as tdl_mcp
    except Exception as e:  # a broken corpus should not take the whole workbench down
        return None, {"mounted": False,
                      "note": f"mcp_server failed to import: {type(e).__name__}: {e}"}

    hosts = allowed_hosts()
    security = TransportSecuritySettings(allowed_hosts=hosts, allowed_origins=hosts)
    # NB: no host= argument. See point 4 in the module docstring.
    asgi = tdl_mcp.mcp.streamable_http_app(streamable_http_path="/",
                                           transport_security=security)
    tdl_mcp.set_limiter(_limiter)
    return asgi, {"mounted": True, "path": "/mcp", "tools": 24,
                  "allowed_hosts": hosts, "metered": sorted(METERED)}


# The only three tools that reach heavy core functions. tdl_place_plan runs a
# 250-candidate search and shares the single-worker pool jobs.py already serialises on;
# the other 21 are corpus lookups and stay unmetered, so an agent following
# tdl_overview's progressive-disclosure advice is never throttled for reading.
METERED = {"tdl_check_plan", "tdl_compose", "tdl_place_plan"}


def _limiter(tool_name):
    """Installed into mcp_server.server. Returns a refusal reason, or None to allow.

    Identity is per-process rather than per-caller: the MCP transport does not hand the
    tool function a request, and reaching for one through a context variable would couple
    mcp_server to this server's internals. A shared bucket is the honest cap here — it
    bounds total load on the single compose worker, which is the resource actually at
    risk. Named as a limitation in docs/deployment.md rather than dressed up as per-user.
    """
    if tool_name not in METERED:
        return None
    from . import limits
    per_hour = limits._env_int("MCP_HEAVY_CALLS_PER_HOUR", 60)
    ok, retry = limits.take("mcp:heavy", limit=per_hour, window_s=3600)
    if ok:
        return None
    return (f"this deployment allows {per_hour} calls an hour to the composing and "
            f"checking tools, and that is reached; about {retry // 60 + 1} minutes until "
            f"it resets. The read-only corpus tools are unaffected.")
