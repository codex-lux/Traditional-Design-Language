"""The AI rail — an Anthropic agent loop over the same 24 tools the MCP server
exposes, streamed to the browser as SSE. The behaviours are the product, not the
wrapper: every claim cites its record, the tool trace is visible, refusals are
content, and every turn ends by saying what could not be evaluated.

The model marks structure with literal tags the client renders as typed cards:
  [[cite:kind:id]]                inline citation, validated before streaming
  <unjudged>…</unjudged>          what these tool calls could not evaluate (required)
  <question cite="…">…</question> a judgment put back to the human
  <refusal reason="…">…</refusal> a refusal, at the same weight as a result
"""
import json
import os
import re

from . import citations, corpus, tools

MODEL = os.environ.get("WORKBENCH_MODEL", "claude-sonnet-4-5")
MAX_TOOL_ROUNDS = 8
MAX_RESULT_BYTES = 20_000

_client_factory = None  # test seam: rail tests inject a fake transport


def set_client_factory(fn):
    global _client_factory
    _client_factory = fn


def _client():
    if _client_factory:
        return _client_factory()
    import anthropic
    return anthropic.Anthropic()


SYSTEM = """You are the rail of the Traditional Design Language workbench — a design
partner beside the canvas, driving 24 tools over a corpus that encodes traditional
architecture as an executable language. The user is a plan-development lead at a
production builder: fluent in plans, framing, cost and code; not in classical
proportion. Be specific, dimensioned, and dry. Show your arithmetic. Never scold —
of 209 fault causes in this corpus, exactly one is ignorance.

Hard rules, none negotiable:
1. Every quantitative or factual claim about the corpus carries an inline citation:
   [[cite:kind:id]] where kind is one of style, slot, kit, fault, room, grouping,
   massing, parti, pack, candidate, finding, plan, constraint. Cite the record you
   actually read. Example: "porch depth reads 5 ft against a 7 ft rule
   [[cite:fault:porch-too-shallow-to-inhabit]]".
2. Unjudged is not passed. tdl_check_measurements, tdl_check_style_constraints and
   tdl_check_plan all separate failed from could-not-evaluate. Tell the human which
   is which, every time. End EVERY answer with an <unjudged>…</unjudged> block naming
   what the calls you just made could not evaluate, drawn from their actual
   could_not_judge / constraint_summary fields — "Nothing was left unjudged by these
   calls." is a legal value; an invented list is not.
3. Judgment slots are the point, not a gap. When a rule is flagged judgment:true or
   scope:judgment, put the question to the human inside
   <question cite="constraint:...">…</question> rather than inventing a number.
4. Refuse out loud. When the corpus has no place for what was asked — a room the
   parti cannot hold, a style with no native parti asked to be composed natively —
   answer inside <refusal reason="…">…</refusal>, stating what would change it.
   A refusal is the system working, not failing.
5. Never call a plan good. The corpus can say what is wrong; it cannot say what is
   alive. Rank, compare, and state trades — do not endorse.
6. Check EXCEPTION_FOR_THIS_STYLE before repeating a rule at a client: several
   styles legitimately do what is a fault everywhere else.
7. Progressive disclosure: ask tools for the sections you need, not everything.
   Prefer several narrow calls over one broad one.

The corpus overview follows; do not re-fetch it with tdl_overview unless asked to
re-orient.

"""


def _context_block(ctx):
    if not ctx:
        return ""
    parts = []
    if ctx.get("surface"):
        parts.append(f"The user is looking at the {ctx['surface']} surface.")
    if ctx.get("plan"):
        parts.append("Current plan record on the bench:\n" + json.dumps(ctx["plan"])[:6000])
    if ctx.get("last_eval"):
        ev = ctx["last_eval"]
        keep = {k: ev.get(k) for k in ("counts", "constraint_summary", "fault_summary") if isinstance(ev, dict)}
        parts.append("Latest validator summary:\n" + json.dumps(keep))
    if ctx.get("candidate_summaries"):
        parts.append("Current candidate set:\n" + json.dumps(ctx["candidate_summaries"])[:4000])
    return "\n\n".join(parts)


def _sse(event, data):
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


CITE_RE = re.compile(r"\[\[cite:([a-z]+:[A-Za-z0-9_-]+(?:#[A-Za-z0-9_-]+)?)\]\]")
TAG_RE = re.compile(
    r"<unjudged>(.*?)</unjudged>"
    r"|<question(?:\s+cite=\"([^\"]*)\")?\s*>(.*?)</question>"
    r"|<refusal(?:\s+reason=\"([^\"]*)\")?\s*>(.*?)</refusal>",
    re.S)


def _emit_text(buf, ctx):
    """Split accumulated model text into typed SSE events, validating citations."""
    events = []
    cites, dropped = [], []

    def clean_cites(text):
        def repl(m):
            ref = m.group(1)
            ok, why = citations.validate(ref, ctx)
            if ok:
                cites.append(ref)
                return f"«{ref}»"
            dropped.append({"ref": ref, "why": why})
            return ref.split(":", 1)[1]
        return CITE_RE.sub(repl, text)

    pos = 0
    for m in TAG_RE.finditer(buf):
        before = buf[pos:m.start()].strip()
        if before:
            events.append(("text", {"text": clean_cites(before)}))
        if m.group(1) is not None:
            events.append(("unjudged", {"text": clean_cites(m.group(1).strip())}))
        elif m.group(3) is not None:
            q = {"text": clean_cites(m.group(3).strip())}
            if m.group(2):
                ok, _ = citations.validate(m.group(2), ctx)
                if ok:
                    q["cite"] = m.group(2)
            events.append(("question", q))
        elif m.group(5) is not None:
            events.append(("refusal", {"text": clean_cites(m.group(5).strip()),
                                       "reason": m.group(4) or ""}))
        pos = m.end()
    tail = buf[pos:].strip()
    if tail:
        events.append(("text", {"text": clean_cites(tail)}))
    if cites:
        events.append(("cites", {"refs": list(dict.fromkeys(cites))}))
    if dropped:
        events.append(("cites_dropped", {"dropped": dropped}))
    return events


def stream_turn(body):
    """Generator of SSE lines for one rail turn. The client owns conversation state
    and replays prior turns; we run the tool loop to completion server-side."""
    if not (os.environ.get("ANTHROPIC_API_KEY") or _client_factory):
        yield _sse("error", {"error": "no ANTHROPIC_API_KEY attached — the rail is off",
                             "honest": True})
        return

    ctx = body.get("context") or {}
    messages = list(body.get("messages") or [])
    ctx_block = _context_block(ctx)
    if ctx_block and messages:
        last = messages[-1]
        if last.get("role") == "user" and isinstance(last.get("content"), str):
            messages[-1] = {"role": "user",
                            "content": last["content"] + "\n\n[context]\n" + ctx_block}

    system = SYSTEM + json.dumps(corpus.core.overview(), ensure_ascii=False)
    tool_defs = tools.tool_definitions()
    client = _client()
    yield _sse("turn_start", {"model": MODEL})

    try:
        for _round in range(MAX_TOOL_ROUNDS + 1):
            resp = client.messages.create(
                model=MODEL, max_tokens=2000, system=system,
                messages=messages, tools=tool_defs)
            text_parts, tool_uses = [], []
            for block in resp.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            if resp.stop_reason == "tool_use" and _round < MAX_TOOL_ROUNDS:
                results = []
                for tu in tool_uses:
                    args_summary = ", ".join(f"{k}={v}" for k, v in list((tu.input or {}).items())[:3])
                    yield _sse("tool_call", {"tool": tu.name, "detail": args_summary[:120]})
                    out = tools.run_tool(tu.name, tu.input)
                    if len(out) > MAX_RESULT_BYTES:
                        out = out[:MAX_RESULT_BYTES] + (
                            '\n…TRUNCATED at 20KB. Narrow the call: ask for fewer sections, '
                            'a lower limit, or one id at a time.')
                    yield _sse("tool_done", {"tool": tu.name, "bytes": len(out)})
                    results.append({"type": "tool_result", "tool_use_id": tu.id, "content": out})
                messages.append({"role": "assistant", "content": resp.content})
                messages.append({"role": "user", "content": results})
                continue

            buf = "".join(text_parts)
            for event, data in _emit_text(buf, ctx):
                yield _sse(event, data)
            break
        else:
            yield _sse("error", {"error": "tool-round cap reached"})
    except Exception as e:
        yield _sse("error", {"error": f"{type(e).__name__}: {str(e)[:300]}"})
    yield _sse("turn_end", {})
