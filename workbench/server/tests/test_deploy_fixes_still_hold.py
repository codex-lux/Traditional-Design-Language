"""The 25 August deployment audit found three ways in. This proves all three are still shut.

Re-verification rather than re-audit: each of these was reproduced, fixed and written up in
docs/deployment.md. What had never been established is whether the SUITE would notice if a
fix were undone — and for one of the three it would not have.

Each assertion here was mutation-checked: the fix was removed, the test was confirmed to
fail, and the fix was restored.
"""
import os

import pytest

from workbench.server import app as app_mod
from workbench.server import auth, mcp_mount


# ---------------------------------------------------------------- 1. the SPA catch-all

def test_the_spa_catch_all_stays_inside_its_own_directory():
    """The one the suite did NOT cover, which is why this file exists.

    The catch-all sits outside the auth gate on purpose — the password screen has to load —
    and it used to do FileResponse(os.path.join(APP_DIST, path)) with no confinement, which
    served any file the process could read to anyone. It was fixed on 25 Aug. Deleting that
    fix today leaves all 142 tests passing.

    What the audit ALSO established, because severity should be measured rather than
    assumed: over real HTTP the traversal is currently blocked anyway, one layer up. uvicorn
    normalises `../` out of the path before routing, and percent-encoded separators do not
    survive into the matched path either — ../../../CLAUDE.md, ..%2f.., %2e%2e/ and
    ....// were all tried against a running server with the fix removed, and all were
    blocked. So the confinement is defence in depth, not the only thing between the internet
    and the filesystem.

    It is still worth keeping and worth testing, because what protects it today is another
    layer's implementation detail: a different ASGI server, or a proxy that forwards a raw
    path, changes the answer. So the test calls the handler directly, which is where the
    property actually lives.
    """
    if not os.path.isdir(app_mod.APP_DIST):
        pytest.skip("needs a built frontend — the catch-all only mounts when dist/ exists")
    root = os.path.realpath(app_mod.APP_DIST)
    for escape in ("../../../CLAUDE.md", "../../../../etc/passwd",
                   "../../STATE-OF-THE-PROJECT.md"):
        resp = app_mod.spa(escape)
        served = os.path.realpath(getattr(resp, "path", ""))
        assert served == os.path.join(root, "index.html") or served.startswith(root + os.sep), (
            f"spa({escape!r}) served {served}, outside {root}")


def test_the_spa_catch_all_still_serves_a_real_asset():
    """Confinement not bought by breaking the shell."""
    if not os.path.isdir(app_mod.APP_DIST):
        pytest.skip("needs a built frontend")
    resp = app_mod.spa("index.html")
    assert os.path.realpath(resp.path).startswith(os.path.realpath(app_mod.APP_DIST))


# ---------------------------------------------------------------- 2. the forged proxy header

def test_the_cloudflare_header_is_not_believed_by_default(monkeypatch):
    """`curl -H 'Cf-Access-Authenticated-User-Email: anyone'` returned the whole corpus and
    all 27 tools. The header means something only when Access is in front, because Access
    overwrites whatever the caller sent."""
    monkeypatch.delenv("WORKBENCH_TRUST_PROXY_AUTH", raising=False)
    assert auth.trust_proxy_auth() is False

    class Req:
        headers = {"cf-access-authenticated-user-email": "attacker@example.com"}

    assert auth.access_email(Req()) == "", "a header the caller chose is being read as identity"


def test_the_header_is_believed_only_when_explicitly_trusted(monkeypatch):
    monkeypatch.setenv("WORKBENCH_TRUST_PROXY_AUTH", "1")

    class Req:
        headers = {"cf-access-authenticated-user-email": "real@example.com"}

    assert auth.access_email(Req()) == "real@example.com"


# ---------------------------------------------------------------- 3. credentials in health

def test_a_datastore_url_never_becomes_an_allowed_host(monkeypatch):
    """The environment scan that finds the platform's hostname read
    RAILWAY_DATABASE_URL=postgres://admin:hunter2@db.internal:5432/tdl as the "hostname"
    admin:hunter2@db.internal:5432 — and /api/health, ungated for the platform healthcheck,
    printed the allowlist."""
    for var, val in [
        ("RAILWAY_DATABASE_URL", "postgres://admin:hunter2@db.internal:5432/tdl"),
        ("RAILWAY_REDIS_URL", "redis://:swordfish@cache.internal:6379"),
        ("RAILWAY_SECRET_URL", "https://user:pw@secrets.internal"),
    ]:
        monkeypatch.setenv(var, val)
    hosts = mcp_mount.allowed_hosts()
    joined = " ".join(hosts)
    for leak in ("hunter2", "swordfish", "pw@", "admin:", "db.internal", "cache.internal"):
        assert leak not in joined, f"{leak!r} reached the MCP allowlist via {hosts}"


def test_userinfo_is_stripped_even_from_a_legitimate_host():
    """The second line of that defence, independent of the key allowlist."""
    assert mcp_mount._hostname("https://user:secret@tdl.up.railway.app/x") \
        == "tdl.up.railway.app"


def test_the_metered_tool_set_is_pinned_even_where_the_mcp_sdk_is_absent():
    """WP-9.4. test_mcp_http.py pins mcp_mount.METERED against an independent literal -- and
    skips whole at import without the SDK, so for a package it held three tools against a
    set of five and was green everywhere the SDK was missing. The literal lives in
    metered_args.py now and this test needs no SDK."""
    from workbench.server import mcp_mount
    from .metered_args import METERED_MIN_ARGS
    assert set(METERED_MIN_ARGS) == mcp_mount.METERED


def test_an_unmetered_tool_never_reaches_a_heavy_core_function():
    """mcp_mount.METERED says which five tools reach the heavy core functions and that the
    other 21 are lookups -- a declaration about what the code DOES, held only against a
    list (the session's audit). Read the tool bodies through the AST: every `tdl_*` not in
    METERED must call none of the heavy functions, directly or by attribute."""
    import ast
    from workbench.server import mcp_mount
    ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    HEAVY = {"compose", "place_plan", "critique_plan", "revise_plan", "check_plan"}
    tree = ast.parse(open(os.path.join(ROOT, "mcp_server", "server.py"), encoding="utf-8").read())
    tools = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("tdl_")}
    assert len(tools) == 27
    for name, fn in tools.items():
        called = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                f = node.func
                called.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None))
        heavy = called & HEAVY
        if name in mcp_mount.METERED:
            assert heavy, f"{name} is metered and calls no heavy function"
        else:
            assert not heavy, f"{name} is not metered and calls {heavy}"
