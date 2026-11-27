"""Every request leaves one line and carries an id, and the server's own log lines are emitted.

Deployment-readiness review, 27 Nov 2026 (DR-07). uvicorn runs at `log_level="warning"`, so there
was no access log at all: a burst of failed sign-ins, a route answering 500, or a caller looping
on a heavy route left nothing behind. And `tdl.rail`'s usage line is INFO, which the root
logger's default drops, so it was written and never seen.

What this is not: an error tracker or an alert. Those are a service somebody has to choose.
"""
import asyncio
import io
import logging
import re

import pytest

from workbench.server import accesslog


def _lines(caplog):
    return [r.getMessage() for r in caplog.records if r.name == "tdl.access"]


@pytest.fixture
def access(caplog):
    with caplog.at_level(logging.INFO, logger="tdl.access"):
        yield caplog


def test_a_request_is_one_line_with_what_an_operator_needs(client, access):
    r = client.get("/api/styles?limit=3")
    lines = [l for l in _lines(access) if "/api/styles" in l]
    assert len(lines) == 1, lines
    line = lines[0]
    assert re.search(r"\bGET /api/styles (\d{3}) \d+ms\b", line), line
    assert f" {r.status_code} " in line
    assert f"id={r.headers['x-request-id']}" in line
    assert "limit" not in line, "a query string can carry what a caller typed; the path is enough"


def test_every_response_carries_an_id_and_two_requests_do_not_share_one(client):
    a, b = client.get("/api/health"), client.get("/api/health")
    ida, idb = a.headers["x-request-id"], b.headers["x-request-id"]
    assert re.fullmatch(r"[0-9a-f]{16}", ida) and ida != idb


def test_a_callers_own_id_is_kept_when_it_is_safe_to_print(client, access):
    r = client.get("/api/styles", headers={"X-Request-ID": "edge-7f3a.42"})
    assert r.headers["x-request-id"] == "edge-7f3a.42"
    assert any("id=edge-7f3a.42" in l for l in _lines(access))


@pytest.mark.parametrize("hostile", ["a b", "x" * 65, "id=1 status=200", "é", ""])
def test_an_id_that_could_forge_a_line_is_replaced(client, access, hostile):
    r = client.get("/api/styles", headers={"X-Request-ID": hostile.encode("utf-8")})
    got = r.headers["x-request-id"]
    assert re.fullmatch(r"[0-9a-f]{16}", got), got


def test_a_path_cannot_break_the_line(client, access):
    client.get("/api/styles/x%0Aforged%20200%201ms")
    lines = [l for l in _lines(access) if "forged" in l]
    assert len(lines) == 1 and "\n" not in lines[0] and "%0A" in lines[0], lines


def test_the_healthcheck_is_quiet_when_it_is_healthy_and_a_refusal_is_not(client, access, monkeypatch):
    client.get("/api/health")
    assert not [l for l in _lines(access) if "/api/health" in l], "a poll every few seconds is noise"
    monkeypatch.setenv("WORKBENCH_PASSWORD", "a-password-for-this-test")
    from fastapi.testclient import TestClient
    from workbench.server.app import app
    r = TestClient(app).get("/api/overview")
    assert r.status_code == 401
    assert any(re.search(r"GET /api/overview 401 ", l) for l in _lines(access))


def test_the_apps_own_bundle_is_quiet_when_it_loads_and_logged_when_it_is_missing(access):
    def answering(status):
        async def inner(scope, receive, send):
            await send({"type": "http.response.start", "status": status, "headers": []})
            await send({"type": "http.response.body", "body": b"", "more_body": False})
        return inner

    for status in (200, 304, 404):
        _sent, run = _drive(answering(status), b"/assets/index-abc.js")
        asyncio.run(run())
    lines = _lines(access)
    assert len(lines) == 1 and " 404 " in lines[0], lines
    _sent, run = _drive(answering(200), b"/assets-not-the-bundle")
    asyncio.run(run())
    assert len(_lines(access)) == 2, "only the bundle's own directory is quiet"


def _drive(inner, path=b"/x", headers=()):
    sent = []

    async def send(message):
        sent.append(message)

    scope = {"type": "http", "method": "GET", "path": path.decode(), "raw_path": path,
             "headers": list(headers), "client": ("203.0.113.9", 4242)}
    async def run():
        await accesslog.AccessLog(inner)(scope, None, send)
    return sent, run


def test_a_stream_is_one_line_written_when_it_ends(access):
    async def inner(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"a", "more_body": True})
        assert not _lines(access), "nothing is known about a stream until it has ended"
        await send({"type": "http.response.body", "body": b"b", "more_body": False})

    sent, run = _drive(inner, b"/api/jobs/j1/events")
    asyncio.run(run())
    lines = _lines(access)
    assert len(lines) == 1 and " 200 " in lines[0] and "203.0.113.9" in lines[0], lines


def test_a_handler_that_raises_is_logged_as_a_500_and_still_raises(access):
    async def inner(scope, receive, send):
        raise RuntimeError("boom")

    _sent, run = _drive(inner, b"/api/broken")
    with pytest.raises(RuntimeError):
        asyncio.run(run())
    lines = _lines(access)
    assert len(lines) == 1 and re.search(r"GET /api/broken 500 ", lines[0]), lines


def test_what_is_not_http_passes_through_untouched(access):
    seen = []

    async def inner(scope, receive, send):
        seen.append(scope["type"])

    asyncio.run(accesslog.AccessLog(inner)({"type": "lifespan"}, None, None))
    assert seen == ["lifespan"] and not _lines(access)


@pytest.fixture
def clean_tdl_logger():
    log = logging.getLogger("tdl")
    before = (list(log.handlers), log.level, log.propagate)
    log.handlers = []
    yield log
    log.handlers, log.propagate = before[0], before[2]
    log.setLevel(before[1])


def test_configure_makes_the_servers_info_lines_reach_the_stream(clean_tdl_logger, monkeypatch):
    monkeypatch.delenv("WORKBENCH_LOG_LEVEL", raising=False)
    out = io.StringIO()
    accesslog.configure(stream=out)
    logging.getLogger("tdl.rail").info("assistant turn usage: requests=2")
    logging.getLogger("tdl.jobs").error("compose job failed")
    text = out.getvalue()
    assert "assistant turn usage: requests=2" in text and "compose job failed" in text
    assert re.search(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\S* INFO tdl\.rail ", text, re.M), text


def test_configure_twice_does_not_print_every_line_twice(clean_tdl_logger, monkeypatch):
    monkeypatch.delenv("WORKBENCH_LOG_LEVEL", raising=False)
    out = io.StringIO()
    accesslog.configure(stream=out)
    accesslog.configure(stream=out)
    logging.getLogger("tdl.access").info("GET /x 200 1ms")
    assert out.getvalue().count("GET /x 200 1ms") == 1


def test_the_level_is_the_operators_and_a_word_it_cannot_read_is_info(clean_tdl_logger, monkeypatch):
    out = io.StringIO()
    monkeypatch.setenv("WORKBENCH_LOG_LEVEL", "warning")
    accesslog.configure(stream=out)
    logging.getLogger("tdl.access").info("quiet")
    logging.getLogger("tdl.jobs").error("loud")
    assert "quiet" not in out.getvalue() and "loud" in out.getvalue()
    monkeypatch.setenv("WORKBENCH_LOG_LEVEL", "chatty")
    assert accesslog.configure(stream=out) == logging.INFO


def test_the_entry_point_configures_it_and_the_middleware_is_outermost():
    import inspect
    from workbench.server import __main__ as entry
    from workbench.server.app import app
    src = inspect.getsource(entry.main)
    assert "accesslog.configure()" in src
    assert src.index("accesslog.configure()") < src.index("uvicorn.run("), "before the server starts"
    assert app.user_middleware[0].cls is accesslog.AccessLog, (
        "the last one added is outermost: it must see the status every other layer set")
