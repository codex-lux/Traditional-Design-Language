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
    assert r.json()["auth"]["required"] is True


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


def test_forged_access_header_does_not_bypass_the_password(fresh_client, monkeypatch):
    """THE regression test for this module's worst bug.

    The first version trusted `Cf-Access-Authenticated-User-Email` unconditionally. On a
    bare deployment nothing strips it, so `curl -H 'Cf-Access-Authenticated-User-Email:
    anything'` walked straight past the password and returned the whole corpus. It is
    only an identity when a proxy is guaranteed to have overwritten whatever the caller
    sent — hence the explicit opt-in, and hence this test.
    """
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    monkeypatch.delenv("WORKBENCH_TRUST_PROXY_AUTH", raising=False)
    r = fresh_client.get("/api/styles",
                         headers={"cf-access-authenticated-user-email": "attacker@evil.com"})
    assert r.status_code == 401, "a forged proxy header must not authenticate"


def test_forged_access_header_does_not_bypass_the_gate_on_mcp(fresh_client, monkeypatch):
    """The same forgery against the agent endpoint, which the same middleware guards."""
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    monkeypatch.delenv("WORKBENCH_TRUST_PROXY_AUTH", raising=False)
    r = fresh_client.post("/mcp", json={},
                          headers={"cf-access-authenticated-user-email": "attacker@evil.com"})
    assert r.status_code == 401


def test_access_header_is_accepted_when_a_proxy_is_declared(fresh_client, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    monkeypatch.setenv("WORKBENCH_TRUST_PROXY_AUTH", "1")
    r = fresh_client.get("/api/styles",
                         headers={"cf-access-authenticated-user-email": "a@b.com"})
    assert r.status_code == 200


def test_health_reports_whether_the_proxy_header_is_trusted(fresh_client, monkeypatch):
    """An operator must be able to see which mode they are in without reading the code."""
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    monkeypatch.delenv("WORKBENCH_TRUST_PROXY_AUTH", raising=False)
    assert fresh_client.get("/api/health").json()["auth"]["trusts_proxy_header"] is False
    monkeypatch.setenv("WORKBENCH_TRUST_PROXY_AUTH", "true")
    assert fresh_client.get("/api/health").json()["auth"]["trusts_proxy_header"] is True


def test_identity_ignores_a_forged_access_header(monkeypatch):
    """Untrusted, the header must not mint rate-limit identities either."""
    monkeypatch.delenv("WORKBENCH_TRUST_PROXY_AUTH", raising=False)

    class _Req:
        headers = {"cf-access-authenticated-user-email": "a@b.com",
                   "x-forwarded-for": "9.9.9.9, 203.0.113.7"}
        cookies = {}
        client = None
    assert auth.identity(_Req()) == "addr:203.0.113.7"


def test_rate_limit_identity_uses_the_last_forwarded_hop(monkeypatch):
    """Each proxy APPENDS, so the last entry is the one our proxy wrote and the earlier
    ones are whatever the caller sent. Taking the first — which is what uvicorn's
    always-trust path does — would let a caller mint a new bucket per request by varying
    the header, and the rate limit would bound nothing."""
    monkeypatch.delenv("WORKBENCH_TRUST_PROXY_AUTH", raising=False)

    def addr(xff):
        class _Req:
            headers = {"x-forwarded-for": xff}
            client = None
        return auth.source_address(_Req())

    assert addr("9.9.9.9, 203.0.113.7") == "203.0.113.7"
    assert addr("9.9.9.9, 203.0.113.7") == addr("1.1.1.1, 203.0.113.7"), (
        "varying the client-supplied prefix must not change the bucket")


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


def test_identity_prefers_access_email_over_address(monkeypatch):
    """Only once a proxy is declared — see test_identity_ignores_a_forged_access_header
    for the untrusted case, which is the one that matters for security."""
    monkeypatch.setenv("WORKBENCH_TRUST_PROXY_AUTH", "1")

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


def test_shape_check_applies_even_without_an_identity(monkeypatch):
    """The size cap binds the CLI and the tests too, which pass no identity.

    Renamed: it used to claim it also proved "no identity means unmetered", and it did
    not — its own setup sends an oversized body, so check_shape short-circuits and
    check_rail is never consulted. Metering everyone would have passed it. That half is
    now test_unmetered_when_no_identity_is_given, which reaches it.
    """
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


# ------------------------------------------------ gaps an audit proved were uncovered
#
# Each test below was written after checking that removing the production line it defends
# left the whole suite green. They are here because "the tests pass" was not evidence.

def test_the_http_route_supplies_the_rail_identity(fresh_client, monkeypatch):
    """app.py must pass identity= into stream_turn, or the DEPLOYED rail is unmetered.

    The other rail tests call stream_turn directly and hand it an identity themselves, so
    deleting `identity=auth.identity(request)` from the route left every one of them
    passing while the live endpoint lost its per-caller cap entirely.
    """
    monkeypatch.delenv("WORKBENCH_PASSWORD", raising=False)
    monkeypatch.delenv("WORKBENCH_API_TOKEN", raising=False)
    monkeypatch.setenv("RAIL_TURNS_PER_HOUR", "1")
    limits.reset()

    seen = []
    real = rail.stream_turn

    def spy(body, identity=None):
        seen.append(identity)
        return real(body, identity=identity)

    monkeypatch.setattr(rail, "stream_turn", spy)
    fake = _RecordingClient()
    rail.set_client_factory(lambda: fake)
    try:
        fresh_client.post("/api/rail/messages",
                          json={"messages": [{"role": "user", "content": "hi"}]})
    finally:
        rail.set_client_factory(None)

    assert seen, "the route never called stream_turn"
    assert seen[0] is not None, "the route passed no identity — the rail is unmetered"
    assert seen[0].startswith(("addr:", "session:", "token:", "access:")), seen[0]


def test_rail_sends_the_model_and_effort_it_claims(monkeypatch):
    """The fake transport records create() kwargs and nothing asserted on them, so the
    model id, max_tokens and output_config could all be changed or deleted with the suite
    still green. On this model family thinking runs adaptively against max_tokens, so the
    effort setting is not cosmetic."""
    monkeypatch.delenv("WORKBENCH_MODEL", raising=False)
    monkeypatch.delenv("WORKBENCH_EFFORT", raising=False)
    monkeypatch.delenv("WORKBENCH_MAX_TOKENS", raising=False)

    class _Resp:
        content, stop_reason = [], "end_turn"

    class _Fake:
        def __init__(self):
            self.calls = []
            outer = self

            class _M:
                def create(self, **kw):
                    outer.calls.append(kw)
                    return _Resp()
            self.messages = _M()

    fake = _Fake()
    rail.set_client_factory(lambda: fake)
    try:
        list(rail.stream_turn({"messages": [{"role": "user", "content": "hi"}]}))
    finally:
        rail.set_client_factory(None)

    assert fake.calls, "no request was made"
    kw = fake.calls[0]
    assert kw["model"] == "claude-sonnet-5"
    assert kw["max_tokens"] == 8000
    assert kw["output_config"] == {"effort": "medium"}


def test_rail_env_overrides_reach_the_request(monkeypatch):
    """And they must be read lazily — a constant bound at import ignores them."""
    monkeypatch.setenv("WORKBENCH_EFFORT", "low")
    monkeypatch.setenv("WORKBENCH_MAX_TOKENS", "1234")
    assert rail.effort() == "low" and rail.max_tokens() == 1234


def test_rail_env_survives_an_empty_string(monkeypatch):
    """A blank field in a platform UI exports X="" — int("") used to raise at import and
    turn every rail turn into a 500 rather than an honest error event."""
    monkeypatch.setenv("WORKBENCH_MAX_TOKENS", "")
    monkeypatch.setenv("RAIL_MAX_TOOL_ROUNDS", "")
    monkeypatch.setenv("WORKBENCH_EFFORT", "")
    assert rail.max_tokens() == 8000
    assert rail.max_tool_rounds() == 8
    assert rail.effort() == "medium"


def test_char_cap_refuses_a_single_huge_message():
    """Only the message-COUNT branch was covered; the size branch could be deleted."""
    body = {"messages": [{"role": "user", "content": "x" * 300_000}]}
    reason = limits.check_shape(body)
    assert reason and "characters" in reason


def test_char_cap_counts_the_context_not_just_the_messages():
    """context rides into the prompt on every billed round and was uncounted."""
    body = {"messages": [{"role": "user", "content": "hi"}],
            "context": {"last_eval": {"blob": "y" * 300_000}}}
    reason = limits.check_shape(body)
    assert reason and "characters" in reason


def test_the_daily_backstop_is_real(monkeypatch):
    """rail:__all__ could be replaced with (True, 0) and nothing noticed."""
    monkeypatch.setenv("RAIL_TURNS_PER_HOUR", "0")     # per-identity cap off
    monkeypatch.setenv("RAIL_TURNS_PER_DAY", "2")
    limits.reset()
    assert limits.check_rail("a") is None
    assert limits.check_rail("b") is None
    reason = limits.check_rail("c")                     # a THIRD, different identity
    assert reason and "daily ceiling" in reason


def test_identity_distinguishes_a_bearer_caller(monkeypatch):
    """Without the token branch every API caller collapses into one addr: bucket."""
    monkeypatch.setenv("WORKBENCH_API_TOKEN", "tok")
    monkeypatch.delenv("WORKBENCH_TRUST_PROXY_AUTH", raising=False)

    class _Req:
        headers = {"authorization": "Bearer tok", "x-forwarded-for": "203.0.113.7"}
        cookies = {}
        client = None
    assert auth.identity(_Req()) == "token:api"


def test_unmetered_when_no_identity_is_given(monkeypatch):
    """The 'identity is None means unmetered' half, on its own.

    The original test bundled this with an oversized body, so check_shape short-circuited
    and check_rail was never consulted — metering everyone would have passed it.
    """
    monkeypatch.setenv("RAIL_TURNS_PER_HOUR", "1")
    monkeypatch.setenv("RAIL_MAX_MESSAGES", "50")
    limits.reset()
    fake = _RecordingClient()
    rail.set_client_factory(lambda: fake)
    body = {"messages": [{"role": "user", "content": "hi"}]}
    try:
        for _ in range(3):
            events = _drain(body)                       # no identity: never rate-limited
            assert not any(e["data"].get("limited") for e in events if e["event"] == "error")
    finally:
        rail.set_client_factory(None)
