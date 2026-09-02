"""The rail's agent loop, offline: a fake Anthropic transport drives one tool round,
and the SSE stream must carry the trace, the validated citations (with the invented
one downgraded), the unjudged block, and the typed question — in order."""
import json

from workbench.server import rail, tools


class _Block:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Resp:
    def __init__(self, content, stop):
        self.content, self.stop_reason = content, stop


class _FakeMessages:
    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def create(self, **kw):
        self.calls.append(kw)
        return self.script.pop(0)


class _FakeClient:
    def __init__(self, script):
        self.messages = _FakeMessages(script)


def _drain(body):
    events = []
    for line in rail.stream_turn(body):
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


def test_tool_registry_is_the_mcp_servers():
    defs = tools.tool_definitions()
    assert len(defs) == 26
    names = {d["name"] for d in defs}
    assert {"tdl_overview", "tdl_compose", "tdl_check_plan", "tdl_resolve_kit"} <= names
    # descriptions are the MCP server's own docstrings, not paraphrases
    over = next(d for d in defs if d["name"] == "tdl_overview")
    assert "START HERE" in over["description"]


def test_run_tool_executes_core():
    out = json.loads(tools.run_tool("tdl_find_style", {"query": "georgian", "limit": 1}))
    assert out["returned"] == 1


def test_rail_loop_events():
    script = [
        _Resp([_Block(type="tool_use", id="t1", name="tdl_find_faults",
                      input={"slot": "porch_depth", "limit": 2})], "tool_use"),
        _Resp([_Block(type="text", text=(
            "Reads 5 ft [[cite:fault:porch-too-shallow-to-inhabit]] and "
            "[[cite:fault:no-such-fault]].\n"
            '<question cite="constraint:c1">Is the separation real?</question>'
            "<unjudged>Two faults were beyond evaluation.</unjudged>"))], "end_turn"),
    ]
    rail.set_client_factory(lambda: _FakeClient(script))
    try:
        events = _drain({"messages": [{"role": "user", "content": "porch?"}]})
    finally:
        rail.set_client_factory(None)
    kinds = [e["event"] for e in events]
    assert kinds[0] == "turn_start" and kinds[-1] == "turn_end"
    assert kinds.index("tool_call") < kinds.index("tool_done") < kinds.index("text")
    cites = next(e for e in events if e["event"] == "cites")
    assert cites["data"]["refs"] == ["fault:porch-too-shallow-to-inhabit"]
    dropped = next(e for e in events if e["event"] == "cites_dropped")
    assert dropped["data"]["dropped"][0]["ref"] == "fault:no-such-fault"
    assert any(e["event"] == "unjudged" for e in events)
    assert any(e["event"] == "question" for e in events)


def test_rail_off_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    events = _drain({"messages": []})
    assert events[0]["event"] == "error"
    assert events[0]["data"]["honest"] is True
