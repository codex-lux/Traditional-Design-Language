"""Every response carries the browser-side protections (review of 27 Nov 2026, DR-04).

The server sent none: no frame policy, no `nosniff`, no referrer policy, no HSTS and no content
security policy. The app is a signed-in single page that injects server-drawn SVG in three places,
and a stored XSS was found through one of them in September, so a policy behind the escaping is
not decoration.
"""
import asyncio

from workbench.server import app as appmod


def test_an_api_response_carries_the_fixed_headers(client):
    r = client.get("/api/health")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert r.headers["cross-origin-opener-policy"] == "same-origin"


def test_a_refusal_by_the_gate_carries_them_too(client, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PASSWORD", "set")
    client.cookies.clear()
    r = client.get("/api/overview")
    assert r.status_code == 401
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"


def test_hsts_is_sent_over_https_and_never_over_http(client):
    from fastapi.testclient import TestClient
    assert "strict-transport-security" not in client.get("/api/health").headers
    secure = TestClient(appmod.app, base_url="https://testserver")
    assert secure.get("/api/health").headers["strict-transport-security"].startswith("max-age=")


def _through(headers_in, scheme="http"):
    """Run the middleware over a one-response app and return the headers that leave."""
    async def inner(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": list(headers_in)})
        await send({"type": "http.response.body", "body": b""})
    sent = []

    async def send(message):
        sent.append(message)
    asyncio.run(appmod.SecurityHeaders(inner)({"type": "http", "scheme": scheme, "path": "/"},
                                              None, send))
    return {k.decode().lower(): v.decode() for k, v in sent[0]["headers"]}


def test_a_page_carries_a_content_security_policy_and_json_does_not():
    page = _through([(b"content-type", b"text/html; charset=utf-8")])
    csp = page["content-security-policy"]
    for directive in ("default-src 'self'", "script-src 'self'", "object-src 'none'",
                      "frame-ancestors 'none'", "base-uri 'self'"):
        assert directive in csp, f"{directive} is missing from: {csp}"
    assert "'unsafe-eval'" not in csp
    assert "script-src 'self' 'unsafe-inline'" not in csp
    assert "content-security-policy" not in _through([(b"content-type", b"application/json")])


def test_a_policy_a_route_set_itself_is_kept():
    """`CorpusStatic` sandboxes the generated plates; the stricter policy must survive."""
    out = _through([(b"content-type", b"text/html"),
                    (b"content-security-policy", b"sandbox; default-src 'none'"),
                    (b"x-content-type-options", b"nosniff")])
    assert out["content-security-policy"] == "sandbox; default-src 'none'"


def test_the_shell_itself_is_served_with_the_policy(client):
    import os
    import pytest
    if not os.path.isdir(appmod.APP_DIST):
        pytest.skip("COULD NOT EVALUATE: no built app at workbench/app/dist, so no shell is served")
    r = client.get("/")
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]
