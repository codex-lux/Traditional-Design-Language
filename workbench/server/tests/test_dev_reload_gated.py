"""`POST /api/dev/reload` answers on a developer's machine and not in a deployment.

Deployment-readiness review, 27 Nov 2026 (DR-13). The route drops every parsed corpus cache so
an on-disk edit is seen (OQ 28: explicit, never a file-watcher). In the image the corpus is
baked in and cannot change, so there the route did one thing: let a signed-in caller force a
600 ms re-parse. It is gated on the bind the process was started for, which is the same fact
`__main__.open_bind_refusal` reads, and one variable says otherwise in either direction.
"""
import pytest

from workbench.server import app as appmod


@pytest.fixture
def env(monkeypatch):
    for var in ("WORKBENCH_HOST", "WORKBENCH_DEV_RELOAD"):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


def test_on_the_local_default_it_answers(client, env):
    assert appmod.dev_reload_enabled() is True
    assert client.post("/api/dev/reload").status_code == 200


def test_on_a_public_bind_it_is_not_there(client, env):
    env.setenv("WORKBENCH_HOST", "0.0.0.0")
    assert appmod.dev_reload_enabled() is False
    r = client.post("/api/dev/reload")
    assert r.status_code == 404, "the image binds 0.0.0.0, and its corpus cannot change"
    assert client.get("/api/health").status_code == 200, "and nothing else went with it"


def test_the_variable_says_otherwise_in_both_directions(client, env):
    env.setenv("WORKBENCH_HOST", "0.0.0.0")
    env.setenv("WORKBENCH_DEV_RELOAD", "1")
    assert client.post("/api/dev/reload").status_code == 200
    env.delenv("WORKBENCH_HOST")
    env.setenv("WORKBENCH_DEV_RELOAD", "0")
    assert client.post("/api/dev/reload").status_code == 404


def test_an_unreadable_value_is_the_default_for_the_bind_and_never_on_by_accident(env):
    env.setenv("WORKBENCH_HOST", "0.0.0.0")
    env.setenv("WORKBENCH_DEV_RELOAD", "maybe")
    assert appmod.dev_reload_enabled() is False


def test_it_reads_the_same_loopback_list_the_start_refusal_reads():
    from workbench.server import __main__ as entry
    for host in entry.LOOPBACK:
        assert appmod._loopback_bind(host) is True, host
    assert appmod._loopback_bind("0.0.0.0") is False


def test_a_refused_reload_is_not_metered(client, env, monkeypatch):
    """A 404 must cost the caller's heavy budget nothing: the route is not there."""
    env.setenv("WORKBENCH_HOST", "0.0.0.0")
    spent = []
    monkeypatch.setattr(appmod, "_heavy", lambda request: spent.append(1))
    assert client.post("/api/dev/reload").status_code == 404
    assert spent == []
