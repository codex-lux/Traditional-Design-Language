"""Serving the 26 MCP tools over HTTP, from the same process as the workbench.

VISION.md §IX has two audiences reaching one corpus. WP-5.2 gave the human one an
interface; this gives the agent one an address. `mcp_server/server.py` is unchanged in
what it does — the same 26 tools over the same `core.py` — and does not know which
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
import contextvars
import os

# Set only while an HTTP /mcp request is in flight. tools.py now imports the SAME module
# object the mount serves, so a limiter installed on it also fired for the browser rail's
# tool calls — one shared bucket, and an agent exhausting it made the UI refuse. The cap
# is meant for the remote transport, so it asks whether it IS the remote transport.
_IN_MCP = contextvars.ContextVar("tdl_in_mcp", default=False)


# Names seen in the wild for "the public hostname of this service". The scan below also
# matches by shape, so this list is a floor rather than the whole net.
PLATFORM_DOMAIN_VARS = {
    "RAILWAY_PUBLIC_DOMAIN", "RAILWAY_STATIC_URL", "RAILWAY_SERVICE_DOMAIN",
    "RENDER_EXTERNAL_HOSTNAME", "RENDER_EXTERNAL_URL", "FLY_APP_NAME",
    "PUBLIC_DOMAIN", "PUBLIC_URL",
}


def _hostname(value):
    """A bare hostname from whatever the platform put in the variable.

    Platforms are inconsistent about this — some export a bare host, some a full URL —
    and the Host header never carries a scheme, so an unparsed 'https://x/' would simply
    never match and the endpoint would 421 with nothing obviously wrong. Same trap a
    person hits pasting a URL into WORKBENCH_ALLOWED_HOSTS.

    The userinfo strip is not cosmetic. A connection string like
    `postgres://admin:hunter2@db.internal:5432/tdl` otherwise yields the "hostname"
    `admin:hunter2@db.internal:5432`, password and all, which then travels into the
    allowlist and out again through whatever reports it.
    """
    v = (value or "").strip()
    if not v:
        return ""
    v = v.split("://", 1)[-1]          # drop any scheme
    v = v.split("/", 1)[0]             # drop any path
    v = v.split("?", 1)[0]             # drop any query
    if "@" in v:                       # drop any user:password@ — see the note above
        v = v.rsplit("@", 1)[1]
    return v.strip().rstrip(".")


# Variables whose values are connection strings or secrets rather than public hostnames.
# Matched as substrings of the KEY, so RAILWAY_DATABASE_URL and DATABASE_PRIVATE_URL both
# go. Scanning wide for the public host was the right call; scanning wide into datastore
# credentials was not, and the userinfo strip above is the second line of that defence.
_NEVER_SCAN = ("DATABASE", "POSTGRES", "PGDATA", "MYSQL", "MONGO", "REDIS", "AMQP",
               "RABBIT", "KAFKA", "ELASTIC", "S3", "SMTP", "SECRET", "PASSWORD",
               "PASSWD", "TOKEN", "APIKEY", "API_KEY", "PRIVATE", "CREDENTIAL", "DSN")


def _platform_hosts():
    """Hostnames the platform advertises for this service, discovered from the env.

    Deliberately a pattern scan rather than one variable name: this was written without
    access to the platform's docs (egress-blocked), so guessing a single name would be a
    coin flip that fails silently. Anything RAILWAY_*DOMAIN / RAILWAY_*URL — and the
    equivalents for a couple of other hosts — is treated as a candidate. A wrong guess
    costs one harmless extra entry in the allowlist; a missed one costs a 421 on every
    MCP call, so the asymmetry says scan wide.
    """
    found = []
    for key, value in os.environ.items():
        k = key.upper()
        if any(bad in k for bad in _NEVER_SCAN):
            continue
        if k in PLATFORM_DOMAIN_VARS or (
                k.startswith(("RAILWAY_", "RENDER_", "FLY_")) and
                (k.endswith("_DOMAIN") or k.endswith("_URL") or k.endswith("_HOSTNAME"))):
            h = _hostname(value)
            # A hostname, not a service id or a bare word — and never something still
            # carrying credentials or whitespace after parsing.
            if h and "." in h and "@" not in h and not any(c.isspace() for c in h):
                found.append(h)
    return found


def allowed_hosts():
    """Hosts this deployment answers to.

    Localhost always, so local development never needs configuring; then whatever the
    platform advertises; then anything stated by hand. The platform scan means
    WORKBENCH_ALLOWED_HOSTS is a fallback rather than a required step — and it dissolves
    the ordering trap, where the hostname only exists after the first deploy but the
    variable had to be set before it.
    """
    hosts = ["127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*", "[::1]", "[::1]:*"]
    stated = (os.environ.get("WORKBENCH_ALLOWED_HOSTS") or "").split(",")
    for h in _platform_hosts() + [_hostname(s) for s in stated]:
        if not h or h in hosts:
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
    # allowed_origins takes ORIGINS, which carry a scheme; allowed_hosts takes Host
    # headers, which never do. Passing the host list to both meant every request with an
    # Origin header was refused 403 — invisible to `claude mcp add`, which sends none,
    # and fatal to any browser-based MCP client.
    origins = [f"{scheme}://{h}" for h in hosts for scheme in ("https", "http")]
    security = TransportSecuritySettings(allowed_hosts=hosts, allowed_origins=origins)
    # NB: no host= argument. See point 4 in the module docstring.
    asgi = tdl_mcp.mcp.streamable_http_app(streamable_http_path="/",
                                           transport_security=security)
    tdl_mcp.set_limiter(_limiter)
    # Counted from the server, never written down. As a literal it was a constant the
    # test compared against itself: removing a tool from server.py left it reading 24.
    tool_count = sum(1 for n, v in vars(tdl_mcp).items()
                     if n.startswith("tdl_") and callable(v))
    return _mark_mcp(asgi), {"mounted": True, "path": "/mcp", "tools": tool_count,
                             "allowed_hosts": hosts, "allowed_origins": origins,
                             "metered": sorted(METERED)}


def _mark_mcp(asgi):
    """Flag the request as arriving over the remote transport, for _limiter."""
    async def wrapper(scope, receive, send):
        token = _IN_MCP.set(True)
        try:
            await asgi(scope, receive, send)
        finally:
            _IN_MCP.reset(token)
    return wrapper


# The only five tools that reach heavy core functions. tdl_place_plan runs a
# 250-candidate search and shares the single-worker pool jobs.py already serialises on;
# tdl_critique_plan places once and tdl_revise_plan places once per round (WP-9);
# the other 21 are corpus lookups and stay unmetered, so an agent following
# tdl_overview's progressive-disclosure advice is never throttled for reading.
METERED = {"tdl_check_plan", "tdl_compose", "tdl_place_plan", "tdl_critique_plan", "tdl_revise_plan"}


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
    if not _IN_MCP.get():
        # The browser rail calling the same function object. It has its own per-identity
        # caps (limits.check_rail) and its own cost profile; charging it to the remote
        # transport's bucket let either side starve the other.
        return None
    from . import limits
    per_hour = limits._env_int("MCP_HEAVY_CALLS_PER_HOUR", 60)
    ok, retry = limits.take("mcp:heavy", limit=per_hour, window_s=3600)
    if ok:
        return None
    return (f"this deployment allows {per_hour} calls an hour to the composing and "
            f"checking tools, and that is reached; about {retry // 60 + 1} minutes until "
            f"it resets. The read-only corpus tools are unaffected.")
