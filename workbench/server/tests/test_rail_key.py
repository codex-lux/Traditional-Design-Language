"""The rail's credential, and the reason it is off.

The bug these cover: a key was set as a platform variable, the panel said "No
ANTHROPIC_API_KEY is attached to the server", and every one of the ways that sentence can
be wrong — a name with a space in it, a value with a trailing newline, a project-level
variable the service never referenced, an installed-but-missing SDK — reported as the one
way it can be right. Off is now a reason, and the reason names the thing to change.
"""
import pytest

from workbench.server import rail


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Start from an environment with no credential and no platform markers, so a test
    asserting "off" is asserting about what it set rather than about the runner."""
    import os
    for name in list(os.environ):
        k = name.strip().upper()
        if ("ANTHROPIC" in k or "CLAUDE" in k or
                k.startswith(("RAILWAY_", "RENDER_", "FLY_", "HEROKU_", "KOYEB_"))):
            monkeypatch.delenv(name, raising=False)


def test_canonical_name_is_read(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-live")
    assert rail.key() == "sk-ant-live"
    assert rail._lookup()[0] == "ANTHROPIC_API_KEY"


def test_a_pasted_value_is_cleaned(monkeypatch):
    # A raw-editor paste: surrounding quotes and a trailing newline. The newline is the
    # dangerous half — it makes an invalid HTTP header, so the rail would report itself ON
    # and then fail every turn with an SDK error nobody can trace back to the paste.
    monkeypatch.setenv("ANTHROPIC_API_KEY", '"sk-ant-live"\n')
    assert rail.key() == "sk-ant-live"


def test_whitespace_in_the_variable_NAME_is_forgiven(monkeypatch):
    # Railway's raw editor stores `ANTHROPIC_API_KEY ` verbatim, and os.environ.get never
    # sees it again. This is the case that produced the report.
    monkeypatch.setenv("ANTHROPIC_API_KEY ", "sk-ant-live")
    monkeypatch.setattr(rail, "_sdk_missing", lambda: None)
    st = rail.state()
    assert rail.key() == "sk-ant-live"
    assert st["on"] is True and st["variable"] == "ANTHROPIC_API_KEY "
    # The variable list on screen shows both names identically, so the note quotes it.
    assert "'ANTHROPIC_API_KEY '" in st["note"]


def test_an_alias_works_and_says_it_is_an_alias(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_KEY", "sk-ant-live")
    monkeypatch.setattr(rail, "_sdk_missing", lambda: None)   # the SDK is optional here
    st = rail.state()
    assert st["on"] is True and st["variable"] == "ANTHROPIC_KEY"
    # A tolerance that hides what it forgave is the next person's lost afternoon.
    assert "canonical name is ANTHROPIC_API_KEY" in st["note"]


def test_the_canonical_name_beats_an_alias(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_KEY", "sk-ant-alias")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-canonical")
    assert rail.key() == "sk-ant-canonical"


def test_an_empty_variable_is_not_reported_as_a_missing_one(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
    st = rail.state()
    assert st["on"] is False
    assert "set but empty" in st["note"]


def test_a_typo_is_named_rather_than_guessed(monkeypatch):
    # A transposition reads as correct to the eye that typed it, which is why this is
    # detected by shape rather than by substring — and why it is REPORTED, never read.
    monkeypatch.setenv("ANTRHOPIC_API_KEY", "sk-ant-live")
    st = rail.state(disclose=True)
    assert st["on"] is False
    assert st["candidates"] == ["ANTRHOPIC_API_KEY"]
    assert "ANTRHOPIC_API_KEY" in st["note"]


def test_near_miss_names_are_not_disclosed_to_an_unauthorised_caller(monkeypatch):
    monkeypatch.setenv("ANTRHOPIC_API_KEY", "sk-ant-live")
    st = rail.state()
    assert "candidates" not in st
    assert "ANTRHOPIC_API_KEY" not in st["note"]   # the count, not the names
    assert "one variable name looks close" in st["note"]


def test_unrelated_variables_are_never_near_misses(monkeypatch):
    for name in ("WORKBENCH_API_TOKEN", "WORKBENCH_SECRET", "DATABASE_URL", "PORT"):
        monkeypatch.setenv(name, "x")
    assert rail._near_miss_names() == []


def test_a_legitimate_anthropic_variable_is_not_accused(monkeypatch):
    """ANTHROPIC_BASE_URL and ANTHROPIC_MODEL are real, unrelated variables. Naming one as
    a fumbled key sends an operator to fix a thing that is not broken — the same
    false-accusation failure check_partis guards against on the corpus side."""
    for name in ("ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL", "ANTHROPIC_SMALL_FAST_MODEL"):
        monkeypatch.setenv(name, "x")
    assert rail._near_miss_names() == []


def test_no_value_is_ever_reported(monkeypatch):
    monkeypatch.setenv("ANTRHOPIC_API_KEY", "sk-ant-SECRETVALUE")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-ALSOSECRET")
    st = rail.state(disclose=True)
    blob = repr(st)
    assert "SECRETVALUE" not in blob and "ALSOSECRET" not in blob


def test_on_a_platform_the_note_names_the_platform_trap(monkeypatch):
    monkeypatch.setenv("RAILWAY_PUBLIC_DOMAIN", "workbench.up.railway.app")
    monkeypatch.setenv("WORKBENCH_PASSWORD", "shibboleth")   # SOMETHING configured arrived
    st = rail.state()
    assert st["on"] is False
    # The commonest real cause: the variable exists, at project scope, and the service
    # never references it. "Set the key" is useless advice to someone who did.
    assert "THIS service" in st["note"] and "redeploy" in st["note"]


def test_an_empty_variable_set_is_not_reported_as_a_missing_key(monkeypatch):
    """The live report turned on this distinction. /api/health showed the platform's own
    variables arriving — mcp.allowed_hosts carried the generated domain, which is
    discovered from RAILWAY_* — while WORKBENCH_PASSWORD was absent at the same moment.
    Two unrelated variables missing at once is the whole configured set landing on another
    service or another environment, which is a different remedy from setting one key."""
    monkeypatch.setenv("RAILWAY_PUBLIC_DOMAIN", "workbench.up.railway.app")
    for name in rail._APP_VARS:
        monkeypatch.delenv(name, raising=False)
    st = rail.state()
    assert st["on"] is False
    assert "NOTHING configured reached this process" in st["note"]
    assert "different service or a different environment" in st["note"]
    # and the moment one real variable arrives, it is a key problem again, not a wiring one
    monkeypatch.setenv("WORKBENCH_SECRET", "s")
    assert "NOTHING configured" not in rail.state()["note"]


def test_PORT_alone_does_not_count_as_configuration(monkeypatch):
    """The platform injects PORT itself, so its presence proves nothing about whether
    anybody's configuration arrived. Counting it would silence the finding above."""
    monkeypatch.setenv("RAILWAY_PUBLIC_DOMAIN", "workbench.up.railway.app")
    monkeypatch.setenv("PORT", "8080")
    for name in rail._APP_VARS:
        monkeypatch.delenv(name, raising=False)
    assert "NOTHING configured reached this process" in rail.state()["note"]


def test_a_missing_sdk_is_not_a_missing_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-live")
    monkeypatch.setattr(rail, "_sdk_missing", lambda: "the `anthropic` package is not installed")
    st = rail.state()
    assert st["on"] is False
    assert "attached" in st["note"] and "anthropic" in st["note"]


def test_a_key_that_does_not_look_like_one_runs_anyway_and_says_so(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "hunter2")
    monkeypatch.setattr(rail, "_sdk_missing", lambda: None)
    st = rail.state()
    assert st["on"] is True            # a key prefix is Anthropic's to change, not ours
    assert "does not look like an Anthropic key" in st["note"]


def test_the_turn_refuses_with_the_reason_attached(monkeypatch):
    monkeypatch.setattr(rail, "_client_factory", None)
    events = list(rail.stream_turn({"messages": []}))
    blob = "".join(events)
    assert "event: error" in blob and '"honest": true' in blob
    # The refusal carries the diagnosis, not just "the rail is off".
    assert "ANTHROPIC_API_KEY" in blob


def test_an_empty_alias_is_also_reported_as_empty(monkeypatch):
    """Asked of every name the lookup accepts, not just the canonical one. A variable that
    exists and holds nothing is a different mistake from one that never arrived."""
    monkeypatch.setenv("ANTHROPIC_API_KEY ", '""')
    st = rail.state()
    assert st["on"] is False
    assert "set but empty" in st["note"] and "ANTHROPIC_API_KEY" in st["note"]
