"""The ungated health route names no host (review of 27 Nov 2026, DR-06).

`/api/health` answers strangers on purpose, and its own comment says it "must not enumerate
hostnames". It withheld `allowed_hosts` and went on serving `allowed_origins`, which is the same
list with a scheme in front of each name.
"""
import pytest

from workbench.server import app as appmod


@pytest.fixture
def gated(monkeypatch):
    monkeypatch.setenv("WORKBENCH_PASSWORD", "a-password")
    monkeypatch.setenv("WORKBENCH_API_TOKEN", "a-token")
    monkeypatch.setitem(appmod.MCP_STATE, "allowed_hosts", ["svc.internal.example"])
    monkeypatch.setitem(appmod.MCP_STATE, "allowed_origins", ["https://svc.internal.example"])


def test_signed_out_the_body_names_no_host(client, gated):
    client.cookies.clear()
    r = client.get("/api/health")
    assert r.status_code == 200
    mcp = r.json()["mcp"]
    assert "allowed_hosts" not in mcp and "allowed_origins" not in mcp
    assert "svc.internal.example" not in r.text
    assert "platform_host_detected" in mcp, "the yes/no an operator needs is gone"


def test_signed_in_the_operator_still_sees_both_lists(client, gated):
    client.cookies.clear()
    mcp = client.get("/api/health", headers={"Authorization": "Bearer a-token"}).json()["mcp"]
    assert mcp["allowed_hosts"] == ["svc.internal.example"]
    assert mcp["allowed_origins"] == ["https://svc.internal.example"]
