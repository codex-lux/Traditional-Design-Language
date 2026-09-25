"""Every read route answers with the expected top-level keys, and error paths are
honest 404s carrying core's own error dicts."""


def test_health(client):
    r = client.get("/api/health").json()
    assert r["ok"] is True and r["jsonschema"] is True
    assert r["counts"]["styles"] == 164


def test_health_is_never_cached(client):
    """This is the endpoint an operator refreshes to see whether a change took effect, and
    it carries no validators — a heuristically cached 200 answers with the state before the
    change and reads exactly like the change not working."""
    r = client.get("/api/health")
    assert "no-store" in r.headers.get("cache-control", "")


def test_health_states_the_session_both_ways_and_agrees_with_the_gate(monkeypatch):
    """WP-14.20. `/api/health` says whether THIS request carries a session, so a signed-out
    browser can show the Gate without asking a gated route to find out. The key is only honest if
    it is the gate's own answer, so every state is held against what the gate then DOES with the
    same client: `session` is true exactly where `/api/overview` does not answer 401. A key that
    read the cookie alone would call a bearer caller signed out; one that read nothing would call
    everybody signed in. Each state gets a fresh client, because a cookie left in the shared
    session-scoped `client` would reach every test after this one (OQ 69's shape)."""
    from fastapi.testclient import TestClient
    from workbench.server import auth, limits
    from workbench.server.app import app

    limits.reset()   # the one login below must not meet a throttle another file filled

    def state(c, **kw):
        h = c.get("/api/health", **kw)
        assert h.status_code == 200, "the health route is never gated"
        return h.json()["session"], c.get("/api/overview", **kw).status_code

    # an open server: every request passes, and `auth.required` beside it says why
    monkeypatch.delenv("WORKBENCH_PASSWORD", raising=False)
    monkeypatch.delenv("WORKBENCH_API_TOKEN", raising=False)
    c = TestClient(app)
    assert c.get("/api/health").json()["auth"]["required"] is False
    assert state(c) == (True, 200)

    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    monkeypatch.setenv("WORKBENCH_SECRET", "test-secret")
    c = TestClient(app)
    assert c.get("/api/health").json()["auth"]["required"] is True
    assert state(c) == (False, 401), "signed out: no session, and the gate refuses"
    assert c.post("/api/login", json={"password": "hunter2"}).status_code == 200
    assert state(c) == (True, 200), "signed in: a session, and the gate lets it through"

    forged = TestClient(app)
    forged.cookies.set(auth.COOKIE, "not-a-signed-session")
    assert state(forged) == (False, 401), "a cookie is not a session until it verifies"

    monkeypatch.setenv("WORKBENCH_API_TOKEN", "s3kr1t")
    bearer = TestClient(app)
    assert state(bearer, headers={"authorization": "Bearer s3kr1t"}) == (True, 200), (
        "a bearer caller passes the gate, so `session` must say so -- the gate's answer, "
        "not a second reading of the cookie")
    assert state(bearer, headers={"authorization": "Bearer wrong"}) == (False, 401)


def test_health_reports_the_rail_from_the_same_reading_the_turn_uses(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "  ")   # truthy to bool(), worth nothing
    assert client.get("/api/health").json()["rail"] is False


def test_overview_counts(client):
    c = client.get("/api/overview").json()["counts"]
    # 97, not 95: ontology 0.7.0 added `arch` (OQ 46) and `expressed_frame` (OQ 47) on the
    # Phase 4 branch, which merged 25 Aug 2026.
    # 210, not 209: WP-5.14 added `window-on-the-chimney-axis` (OQ 85) — the fault that
    # catches an opening drawn on a chimney stack's own axis, which is two records built
    # from different rules that nothing had ever compared.
    assert c["element_slots"] == 97 and c["faults"] == 210


def test_phylogeny_shape(client):
    g = client.get("/api/phylogeny").json()
    assert len(g["taxa"]) == 164
    assert all({"from", "to", "type", "inherits_kit"} <= set(e) for e in g["edges"][:5])
    carries = {e["type"] for e in g["edges"] if e["inherits_kit"]}
    assert "descends_from" in carries and "references" not in carries


def test_cascade(client):
    r = client.get("/api/kit/tidewater-georgian/cascade").json()
    assert r["cascade"][0]["id"] == "tidewater-georgian"
    assert r["cascade"][0]["distance"] == 0
    assert r["levels"] > 15  # the 29-level chain, self included


def test_kit_and_slot_detail(client):
    kit = client.get("/api/kit/tidewater-georgian").json()
    assert kit["slots_returned"] > 50
    row = client.get("/api/kit/georgian-colonial-american/slot/composition_parti").json()
    assert row["binding"] == "specified"
    # the four-rank ladder survives: full variants, not just canonical/forbidden ids
    assert any(v.get("status") == "canonical" for v in row["variants"])


def test_faults(client):
    r = client.get("/api/faults", params={"style": "georgian-colonial-american", "limit": 300}).json()
    assert r["matches"] > 100
    f = client.get("/api/faults/porch-too-shallow-to-inhabit",
                   params={"style": "georgian-colonial-american"}).json()
    assert f["for_this_style"]["exception"] is not None  # exceptions before rules
    assert set(f["fixes"]) == {"right", "cheap", "dishonest"}


def test_unknown_ids_are_404(client):
    assert client.get("/api/styles/not-a-style").status_code == 404
    assert client.get("/api/faults/not-a-fault").status_code == 404
    assert client.get("/api/kit/not-a-style/cascade").status_code == 404


def test_partis_gate(client):
    r = client.get("/api/partis", params={"style": "tidewater-georgian"}).json()
    assert r["count"] >= 1  # the style-switch demo depends on a native parti here


def test_example_plan_no_traversal(client):
    # traversal in the URL never reaches the handler. WHICH refusal you get depends on the
    # Starlette version -- older ones resolve the path to the SPA catch-all and serve
    # index.html, newer ones normalise it and 404 before any route matches -- so asserting
    # the mechanism pinned this test to a routing detail and it broke on a version bump
    # that had made the refusal STRICTER. What must hold either way is that the target
    # file's content is never served; that is what is asserted here.
    r = client.get("/api/plans/examples/../../CLAUDE.md")
    assert r.status_code in (200, 404)
    assert "working notes for Claude Code" not in r.text
    # and the handler itself strips any path a caller could smuggle in
    from fastapi import HTTPException
    from workbench.server.app import example_plan
    import pytest as _pytest
    with _pytest.raises(HTTPException):
        example_plan("../../CLAUDE.md")
    r = client.get("/api/plans/examples/tidewater-georgian-careful")
    assert r.status_code == 200 and r.json()["style"] == "tidewater-georgian"
