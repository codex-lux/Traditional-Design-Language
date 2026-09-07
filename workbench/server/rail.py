"""The AI rail — an Anthropic agent loop over the same 27 tools the MCP server
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

from . import citations, corpus, limits, tools

def _env(name, default):
    """Read lazily. A module-level os.environ.get freezes at import — invisible to
    anything setting it afterwards, and untestable — which is the same trap auth.py's
    login-attempt cap fell into. docs/deployment.md lists all four of these as tunable."""
    return os.environ.get(name) or default


KEY_VAR = "ANTHROPIC_API_KEY"


def key():
    """The rail's credential, or None. Read at call time, never at import.

    Stripped, and the stripped value is what reaches the SDK. A key pasted with a trailing
    newline is truthy, so `bool(os.environ.get(...))` reported the rail ON — and then every
    turn failed, because a newline in a header value is not a legal header. The rail
    claiming it can answer and then not answering is the one collapse this project forbids
    everywhere else; it should not be reachable by a paste.
    """
    return (os.environ.get(KEY_VAR) or "").strip() or None


def model():
    return _env("WORKBENCH_MODEL", "claude-sonnet-5")


def effort():
    return _env("WORKBENCH_EFFORT", "medium")


def max_tokens():
    try:
        return int(_env("WORKBENCH_MAX_TOKENS", "8000"))
    except ValueError:
        return 8000


def max_tool_rounds():
    try:
        return int(_env("RAIL_MAX_TOOL_ROUNDS", "8"))
    except ValueError:
        return 8


# On this model family thinking runs adaptively unless told otherwise, and those tokens
# count against max_tokens — a 2000 ceiling (what this rail carried against the older
# model) risks truncating a turn mid-answer. effort() trades depth for spend; medium
# suits a rail that mostly dispatches tools and answers briefly. Each tool round is a
# separate billed request, so max_tool_rounds() is the per-turn cost multiplier.
MAX_RESULT_BYTES = 20_000

_client_factory = None  # test seam: rail tests inject a fake transport


def set_client_factory(fn):
    global _client_factory
    _client_factory = fn


_POOLED = {}          # api key -> the one client built for it


def _client():
    if _client_factory:
        return _client_factory()
    import anthropic
    # POOLED, keyed on the key. This used to construct a client per turn, and every
    # anthropic.Anthropic() builds its own httpx.Client with its own connection pool — so
    # each turn paid a fresh TCP handshake and TLS negotiation to api.anthropic.com before
    # its first token, and dropped the sockets to the garbage collector afterwards. The
    # eight tool rounds inside one turn already shared a client; nothing shared across
    # turns, which is the boundary a keep-alive is for.
    #
    # Keyed rather than a module singleton so a rotated key still takes effect: key() is
    # read from the environment at call time everywhere else in this file, deliberately,
    # and a cached client holding the old one would be the single reader disagreeing with
    # the rest — the exact collapse rail.key() exists to prevent.
    k = key()
    client = _POOLED.get(k)
    if client is None:
        # One entry, normally: the key comes from the environment, not from a request, so
        # nothing a caller does can grow this dict. A rotation in a live process strands the
        # old client's keep-alive sockets behind a strong reference, so close it on the way
        # out rather than leaving it to a GC that will never run for a module global.
        for stale_key, stale in list(_POOLED.items()):
            _POOLED.pop(stale_key, None)
            try:
                stale.close()
            except Exception:      # noqa: BLE001 — a client we are discarding anyway
                pass
        # The stripped key, not the raw variable the SDK would otherwise re-read for itself.
        client = _POOLED[k] = anthropic.Anthropic(api_key=k)
    return client


SYSTEM = """You are the rail of the Traditional Design Language workbench — a design
partner beside the canvas, driving 27 tools over a corpus that encodes traditional
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
   could_not_judge / constraint_summary / not_applicable fields (not_applicable is a
   FOURTH state: every test of that fault was preconditioned on a measurement this
   house does not meet, so none ran — the question does not arise, which is not a pass
   and not an unjudged either; name it as its own thing) — "Nothing was left unjudged by these
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
6. Check the exception key before repeating a rule at a client: several styles
   legitimately do what is a fault everywhere else. THREE keys, not one:
   EXCEPTION_FOR_THIS_STYLE (condition met, the licence holds),
   EXCEPTION_NOT_EARNED_BY_THIS_STYLE (condition refused, repeat the general rule),
   EXCEPTION_WHOSE_CONDITION_COULD_NOT_BE_JUDGED (undecidable from the style alone).
   The third belongs in your <unjudged> block under rule 2, not omitted.
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


# The id class comes from citations.py rather than being spelled again here. This regex used
# to carry its own copy WITHOUT the dot, so `[[cite:constraint:tidewater-georgian.c01]]` never
# matched, validate() never saw it, and all 660 constraint ids reached the reader as literal
# bracket syntax — not even downgraded to plain text, because the downgrade lives in repl()
# below and repl() was never called. Widening the client's parser (WP-5.6) could not fix that,
# because the client never received a citation to parse.
CITE_RE = re.compile(
    rf"\[\[cite:([a-z]+:[{citations.ID_CHARS}]+(?:#[{citations.FRAG_CHARS}]+)?)\]\]")
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


def stream_turn(body, identity=None):
    """Generator of SSE lines for one rail turn. The client owns conversation state
    and replays prior turns; we run the tool loop to completion server-side.

    Every refusal below leaves by the same door as the missing-key case: one `error`
    event carrying honest:true, which the client already treats as terminal. A rail that
    will not answer says why, in the same voice it uses for everything else it cannot do.

    `identity` is the rate-limit subject. None means unmetered — the CLI and the tests —
    but the shape checks apply either way, because those bound one request's cost rather
    than one caller's rate.
    """
    if not (key() or _client_factory):
        yield _sse("error", {"error": "no ANTHROPIC_API_KEY attached — the rail is off",
                             "honest": True})
        return

    refusal = limits.check_shape(body)
    if refusal is None and identity is not None:
        refusal = limits.check_rail(identity)
    if refusal:
        yield _sse("error", {"error": refusal, "honest": True, "limited": True})
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
    yield _sse("turn_start", {"model": model()})

    try:
        rounds = max_tool_rounds()
        for _round in range(rounds + 1):
            resp = client.messages.create(
                model=model(), max_tokens=max_tokens(), system=system,
                output_config={"effort": effort()},
                messages=messages, tools=tool_defs)
            text_parts, tool_uses = [], []
            for block in resp.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            if resp.stop_reason == "tool_use" and _round < rounds:
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
