"""A public bind with no gate is refused at start (deployment-readiness review, 27 Nov 2026, DR-01).

`auth.required()` is false when neither WORKBENCH_PASSWORD nor WORKBENCH_API_TOKEN is set, and
the server is then open by configuration. That is the local default and stays so. In a container
the Dockerfile sets WORKBENCH_HOST=0.0.0.0, so one forgotten variable served every /api route,
/mcp and the assistant -- the operator's Anthropic key -- to anyone, behind a printed note.
"""
import pytest

from workbench.server import __main__ as entry

GATES = ("WORKBENCH_PASSWORD", "WORKBENCH_API_TOKEN", "WORKBENCH_ALLOW_OPEN")


@pytest.fixture
def bare(monkeypatch):
    for name in GATES:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "10.0.0.5", "example.internal"])
def test_a_public_bind_with_no_gate_is_refused_and_says_what_to_set(bare, host):
    reason = entry.open_bind_refusal(host)
    assert reason, f"{host} with no password was allowed to start open"
    assert "WORKBENCH_PASSWORD" in reason and "WORKBENCH_ALLOW_OPEN" in reason


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "::1"])
def test_the_local_default_is_unchanged(bare, host):
    assert entry.open_bind_refusal(host) is None


@pytest.mark.parametrize("name", ["WORKBENCH_PASSWORD", "WORKBENCH_API_TOKEN"])
def test_either_gate_lets_a_public_bind_start(bare, name):
    bare.setenv(name, "set")
    assert entry.open_bind_refusal("0.0.0.0") is None


def test_open_on_purpose_is_expressible_and_only_by_a_yes(bare):
    bare.setenv("WORKBENCH_ALLOW_OPEN", "1")
    assert entry.open_bind_refusal("0.0.0.0") is None
    bare.setenv("WORKBENCH_ALLOW_OPEN", "0")
    assert entry.open_bind_refusal("0.0.0.0"), "a value that is not a yes opened the server"


def test_the_proxy_header_flag_is_not_a_gate(bare):
    """WORKBENCH_TRUST_PROXY_AUTH alone leaves `auth.required()` false: the server is still open."""
    bare.setenv("WORKBENCH_TRUST_PROXY_AUTH", "1")
    assert entry.open_bind_refusal("0.0.0.0")


def test_main_exits_before_it_binds_or_serves(bare, capsys):
    import uvicorn
    served = []
    bare.setattr(uvicorn, "run", lambda *a, **k: served.append((a, k)))
    bare.setattr(entry, "HOST", "0.0.0.0")
    bare.setattr(entry, "PORT", 0)
    with pytest.raises(SystemExit) as stop:
        entry.main()
    assert stop.value.code == 1
    assert not served, "the server was started on an open public bind"
    assert "WORKBENCH_PASSWORD" in capsys.readouterr().out


def test_main_still_serves_a_gated_public_bind(bare):
    import uvicorn
    served = []
    bare.setattr(uvicorn, "run", lambda *a, **k: served.append((a, k)))
    bare.setattr(entry, "HOST", "0.0.0.0")
    bare.setattr(entry, "PORT", 0)
    bare.setenv("WORKBENCH_PASSWORD", "set")
    entry.main()
    assert len(served) == 1 and served[0][1]["host"] == "0.0.0.0"
