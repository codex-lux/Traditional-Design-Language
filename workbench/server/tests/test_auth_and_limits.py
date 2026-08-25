"""The gate and the caps.

Two properties matter most here and are asserted directly rather than implied:

  * an unset password leaves the server open AND SAYS SO — the third state is never
    reported as the first;
  * an oversized turn is refused *before* the transport is touched, which is the only
    point at which refusing it saves anything.
"""
import json

import pytest

from workbench.server import auth, limits, rail


@pytest.fixture
def fresh_client():
    """A client built per test, so env set by monkeypatch is seen by the app."""
    from fastapi.testclient import TestClient
    from workbench.server.app import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_limits():
    limits.reset()
    yield
    limits.reset()


# ------------------------------------------------------------------ the gate

def test_open_by_default_and_says_so(fresh_client, monkeypatch):
    monkeypatch.delenv("WORKBENCH_PASSWORD", raising=False)
    monkeypatch.delenv("WORKBENCH_API_TOKEN", raising=False)
    assert fresh_client.get("/api/styles").status_code == 200
    state = fresh_client.get("/api/health").json()["auth"]
    assert state["required"] is False
    assert "open to anyone" in state["note"]


def test_password_gates_the_api(fresh_client, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    assert fresh_client.get("/api/styles").status_code == 401


def test_health_is_never_gated(fresh_client, monkeypatch):
    """Railway's healthcheck has no cookie. A gated /api/health fails every deploy."""
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    r = fresh_client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["auth"] == {"required": True, "bearer": False}


def test_login_then_through(fresh_client, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    monkeypatch.setenv("WORKBENCH_SECRET", "test-secret")
    assert fresh_client.post("/api/login", json={"password": "wrong"}).status_code == 401
    assert fresh_client.post("/api/login", json={"password": "hunter2"}).status_code == 200
    # the cookie the client kept is now sufficient
    assert fresh_client.get("/api/styles").status_code == 200


def test_bearer_token_for_non_browsers(fresh_client, monkeypatch):
    monkeypatch.setenv("WORKBENCH_API_TOKEN", "s3kr1t")
    assert fresh_client.get("/api/styles").status_code == 401
    r = fresh_client.get("/api/styles", headers={"authorization": "Bearer s3kr1t"})
    assert r.status_code == 200


def test_access_header_is_accepted(fresh_client, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    r = fresh_client.get("/api/styles",
                         headers={"cf-access-authenticated-user-email": "a@b.com"})
    assert r.status_code == 200


def test_login_attempts_are_throttled(fresh_client, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    monkeypatch.setenv("WORKBENCH_LOGIN_ATTEMPTS", "3")
    codes = [fresh_client.post("/api/login", json={"password": "no"}).status_code
             for _ in range(5)]
    assert codes[:3] == [401, 401, 401]
    assert codes[-1] == 429


def test_tampered_cookie_is_rejected():
    token = auth.mint("abc")
    assert auth.verify(token) == "abc"
    assert auth.verify(token[:-1] + ("0" if token[-1] != "0" else "1")) is None
    assert auth.verify("garbage") is None


def test_identity_prefers_access_email_over_address():
    class _Req:
        headers = {"cf-access-authenticated-user-email": "a@b.com",
                   "x-forwarded-for": "9.9.9.9"}
        cookies = {}
        client = None
    assert auth.identity(_Req()) == "access:a@b.com"


# ------------------------------------------------------------------ the caps

def test_take_window():
    assert limits.take("k", limit=2, window_s=60)[0] is True
    assert limits.take("k", limit=2, window_s=60)[0] is True
    ok, retry = limits.take("k", limit=2, window_s=60)
    assert ok is False and retry > 0


def test_limit_of_zero_is_off_not_deny():
    assert all(limits.take("z", limit=0, window_s=60)[0] for _ in range(50))


def _drain(body, identity=None):
    events = []
    for line in rail.stream_turn(body, identity=identity):
        for chunk in line.strip().split("\n\n"):
            ev = {}
            for ln in chunk.split("\n"):
                if ln.startswith("event: "):
                    ev["event"] = ln[7:]
                if ln.startswith("data: "):
                    ev["data"] = json.loads(ln[6:])
            if ev.get("event"):
                events.append(ev)
    return events


class _RecordingClient:
    """Records every create() so a test can assert none happened."""
    def __init__(self):
        self.calls = []
        outer = self

        class _M:
            def create(self, **kw):
                outer.calls.append(kw)
                raise AssertionError("the transport should not have been reached")
        self.messages = _M()


def test_oversized_history_refused_before_the_transport(monkeypatch):
    monkeypatch.setenv("RAIL_MAX_MESSAGES", "3")
    fake = _RecordingClient()
    rail.set_client_factory(lambda: fake)
    try:
        body = {"messages": [{"role": "user", "content": "hi"} for _ in range(10)]}
        events = _drain(body, identity="session:x")
    finally:
        rail.set_client_factory(None)

    assert fake.calls == [], "refusal must precede the first billed request"
    assert [e["event"] for e in events] == ["error"]
    assert events[0]["data"]["honest"] is True
    assert events[0]["data"]["limited"] is True
    assert "10 messages" in events[0]["data"]["error"]


def test_rate_limit_refuses_the_second_turn(monkeypatch):
    monkeypatch.setenv("RAIL_TURNS_PER_HOUR", "1")
    monkeypatch.setenv("RAIL_MAX_MESSAGES", "50")
    assert limits.check_rail("session:a") is None          # first turn allowed
    reason = limits.check_rail("session:a")                 # second refused
    assert reason and "turns an hour" in reason
    assert limits.check_rail("session:b") is None, "budgets are per identity"


def test_rate_limited_turn_never_reaches_the_transport(monkeypatch):
    monkeypatch.setenv("RAIL_TURNS_PER_HOUR", "1")
    limits.take("rail:session:x", limit=1, window_s=3600)   # spend the only turn
    fake = _RecordingClient()
    rail.set_client_factory(lambda: fake)
    try:
        events = _drain({"messages": [{"role": "user", "content": "hi"}]},
                        identity="session:x")
    finally:
        rail.set_client_factory(None)
    assert fake.calls == []
    assert events[0]["data"]["limited"] is True


def test_no_identity_means_unmetered_but_still_shape_checked(monkeypatch):
    """The CLI and the tests pass no identity; the size cap still applies to them."""
    monkeypatch.setenv("RAIL_TURNS_PER_HOUR", "1")
    monkeypatch.setenv("RAIL_MAX_MESSAGES", "2")
    fake = _RecordingClient()
    rail.set_client_factory(lambda: fake)
    try:
        events = _drain({"messages": [{"role": "user", "content": "x"}] * 5})
    finally:
        rail.set_client_factory(None)
    assert events[0]["data"]["limited"] is True
    assert fake.calls == []
