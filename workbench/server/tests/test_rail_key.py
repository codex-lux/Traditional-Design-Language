"""The rail's credential, read once and reported honestly.

Both cases here are the same failure in different clothes: the rail says it can answer and
then cannot. `bool(os.environ.get(...))` is true of a key with a trailing newline, and a
newline is not a legal header value — so the panel came up live and every turn died. And
/api/health, the endpoint an operator refreshes to see whether a change took effect,
carried no cache headers while the client's `fresh: true` skipped only its own map.
"""
from workbench.server import rail


def test_a_pasted_newline_does_not_produce_a_rail_that_says_it_is_on(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-live\n")
    assert rail.key() == "sk-ant-live"        # and this is what reaches the SDK


def test_a_whitespace_only_variable_is_no_key(monkeypatch):
    # Truthy to bool(), and worth nothing. The rail must not report itself available.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
    assert rail.key() is None


def test_the_turn_refuses_on_the_same_reading_the_panel_shows(monkeypatch):
    """One reader. Two would eventually disagree, and the one the browser believes would be
    the one that never runs a turn."""
    monkeypatch.setattr(rail, "_client_factory", None)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
    assert rail.key() is None
    events = "".join(rail.stream_turn({"messages": []}))
    assert "event: error" in events and '"honest": true' in events
