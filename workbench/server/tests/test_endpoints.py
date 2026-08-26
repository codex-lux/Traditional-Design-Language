"""Every read route answers with the expected top-level keys, and error paths are
honest 404s carrying core's own error dicts."""


def test_health(client):
    r = client.get("/api/health").json()
    assert r["ok"] is True and r["jsonschema"] is True
    assert r["counts"]["styles"] == 164


def test_health_says_why_the_rail_is_off(client, monkeypatch):
    """`rail` was a bare bool, so a dark panel could only say one thing and it was often
    the wrong thing. The reason travels with it now, and the two cannot disagree because
    both come from rail.state()."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = client.get("/api/health").json()
    assert r["rail"] is r["rail_state"]["on"]
    assert r["rail_state"]["note"]


def test_health_is_never_cached(client):
    """The endpoint an operator refreshes to see whether the variable they just set took
    effect. It carries no validators, so without this a heuristically cached 200 answers
    with the state before the fix — which reads exactly like the fix not working."""
    r = client.get("/api/health")
    assert "no-store" in r.headers.get("cache-control", "")


def test_health_does_not_enumerate_variable_names_to_the_open_internet(client, monkeypatch):
    """/api/health is ungated for the platform healthcheck, so an operator's own variable
    names are shown only to an authorised caller — the same rule as mcp.allowed_hosts."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("ANTRHOPIC_API_KEY", "sk-ant-never-printed")
    monkeypatch.setenv("WORKBENCH_PASSWORD", "shibboleth")   # makes the caller unauthorised
    body = client.get("/api/health").text
    assert "ANTRHOPIC_API_KEY" not in body and "sk-ant-never-printed" not in body


def test_overview_counts(client):
    c = client.get("/api/overview").json()["counts"]
    # 97, not 95: ontology 0.7.0 added `arch` (OQ 46) and `expressed_frame` (OQ 47) on the
    # Phase 4 branch, which merged 25 Aug 2026.
    assert c["element_slots"] == 97 and c["faults"] == 209


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
    # traversal in the URL never reaches the handler — starlette resolves it to the SPA
    # catch-all, which serves index.html, not the target file
    r = client.get("/api/plans/examples/../../CLAUDE.md")
    assert "text/html" in r.headers.get("content-type", "")
    assert "working notes for Claude Code" not in r.text
    # and the handler itself strips any path a caller could smuggle in
    from fastapi import HTTPException
    from workbench.server.app import example_plan
    import pytest as _pytest
    with _pytest.raises(HTTPException):
        example_plan("../../CLAUDE.md")
    r = client.get("/api/plans/examples/tidewater-georgian-careful")
    assert r.status_code == 200 and r.json()["style"] == "tidewater-georgian"
