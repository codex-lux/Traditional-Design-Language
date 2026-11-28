"""The assistant's fixed prefix is sent as a cached prefix, and what a turn cost is logged.

Deployment-readiness review, 27 Nov 2026 (DR-09). Every request of a turn re-sent the system
prompt and all the tool definitions -- measured at 42,338 characters -- at full input price, on
up to nine tool rounds, with no `cache_control` anywhere. Caching is a prefix match on bytes, so
these hold three things: the markers are where they must be, the prefix is byte-identical from
one request to the next (a marker over a prefix that moves is a surcharge, not a saving), and
the turn's usage is written down, because nothing here can prove a cache hit without a key.

NOT PROVED HERE: that the API serves a read. That needs a live, billed turn; the log line is how
an operator sees it (`cache_read` above zero from the second request of a turn).
"""
import json
import logging

from workbench.server import rail


class _Block:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Usage:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Resp:
    def __init__(self, content, stop, usage=None):
        self.content, self.stop_reason, self.usage = content, stop, usage


class _Client:
    def __init__(self, script):
        outer = self
        self.calls = []

        class _M:
            def create(self, **kw):
                # A copy of what was sent NOW: the loop appends to `messages` afterwards.
                outer.calls.append(json.loads(json.dumps(kw, default=lambda o: o.__dict__)))
                return script.pop(0)
        self.messages = _M()


def _turn(script, question="what is a water table?"):
    client = _Client(list(script))
    rail.set_client_factory(lambda: client)
    try:
        events = "".join(rail.stream_turn({"messages": [{"role": "user", "content": question}]}))
    finally:
        rail.set_client_factory(None)
    return client.calls, events


def _markers(node):
    """Every cache_control found on a content block, at any depth of a request."""
    if isinstance(node, dict):
        return ([node["cache_control"]] if "cache_control" in node else []) + \
               [m for k, v in node.items() if k != "cache_control" for m in _markers(v)]
    if isinstance(node, list):
        return [m for v in node for m in _markers(v)]
    return []


TOOL_ROUND = _Resp([_Block(type="tool_use", id="tu_1", name="tdl_overview", input={})], "tool_use",
                   _Usage(input_tokens=40, cache_creation_input_tokens=11000,
                          cache_read_input_tokens=0, output_tokens=30))
ANSWER = _Resp([_Block(type="text", text="A water table is a projecting course.")], "end_turn",
               _Usage(input_tokens=900, cache_creation_input_tokens=0,
                      cache_read_input_tokens=11000, output_tokens=60))


def test_the_system_prompt_is_one_block_marked_for_the_cache():
    calls, _ = _turn([ANSWER])
    system = calls[0]["system"]
    assert isinstance(system, list) and len(system) == 1, "a string system prompt cannot carry a marker"
    assert system[0]["type"] == "text" and len(system[0]["text"]) > 5000
    assert system[0]["cache_control"] == {"type": "ephemeral"}, (
        "tools render before system, so this one marker caches both")


def test_the_growing_conversation_is_cached_by_the_top_level_field():
    calls, _ = _turn([TOOL_ROUND, ANSWER])
    assert len(calls) == 2
    for kw in calls:
        assert kw["cache_control"] == {"type": "ephemeral"}
        placed = _markers({"system": kw["system"], "tools": kw["tools"], "messages": kw["messages"]})
        assert len(placed) == 1, f"one explicit marker and the automatic one; found {len(placed)} explicit"
        assert len(placed) + 1 <= 4, "the API takes four breakpoints a request"


def test_the_prefix_is_the_same_bytes_on_every_request_and_every_turn():
    first, _ = _turn([TOOL_ROUND, ANSWER])
    second, _ = _turn([ANSWER], question="and a belt course?")
    prefixes = [json.dumps({"tools": kw["tools"], "system": kw["system"]}, sort_keys=False)
                for kw in first + second]
    assert len(set(prefixes)) == 1, "the cached prefix moved between two requests"
    # And the settings that are part of the cache key do not vary within a turn.
    assert len({json.dumps([kw["model"], kw["output_config"]]) for kw in first}) == 1


def test_history_already_sent_is_resent_unchanged_inside_a_turn():
    """Round two must begin with round one's messages, byte for byte, or the tail never reads."""
    calls, _ = _turn([TOOL_ROUND, ANSWER])
    one, two = calls[0]["messages"], calls[1]["messages"]
    assert two[:len(one)] == one
    assert len(two) == len(one) + 2, "the assistant's tool call and its results, appended"


def test_what_the_turn_cost_is_logged_with_the_cache_figures(caplog):
    with caplog.at_level(logging.INFO, logger="tdl.rail"):
        _turn([TOOL_ROUND, ANSWER])
    lines = [r.getMessage() for r in caplog.records if r.name == "tdl.rail" and "usage" in r.getMessage()]
    assert len(lines) == 1, lines
    line = lines[0]
    for want in ("requests=2", "input=940", "cache_write=11000", "cache_read=11000", "output=90"):
        assert want in line, (want, line)


def test_a_response_with_no_usage_is_a_turn_and_not_a_crash(caplog):
    """The rail's other fakes return no usage; a provider could omit a field."""
    with caplog.at_level(logging.INFO, logger="tdl.rail"):
        calls, events = _turn([_Resp([_Block(type="text", text="ok")], "end_turn")])
    assert "event: turn_end" in events and "event: error" not in events
    assert any("requests=1" in r.getMessage() for r in caplog.records)
