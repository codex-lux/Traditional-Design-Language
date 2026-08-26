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
import difflib
import json
import os
import re

from . import citations, corpus, limits, tools

def _env(name, default):
    """Read lazily. A module-level os.environ.get freezes at import — invisible to
    anything setting it afterwards, and untestable — which is the same trap auth.py's
    login-attempt cap fell into. docs/deployment.md lists all four of these as tunable."""
    return os.environ.get(name) or default


# ------------------------------------------------------------------ the credential
#
# The rail is off without a key, and "off" was reported as a bare false — true only of
# the one case where the variable is genuinely absent. Every other way a platform's
# variable editor mangles it (a trailing newline from a paste, surrounding quotes from a
# raw .env block, whitespace in the NAME, a near-miss spelling, a project-level variable
# the service never references) came out as the same dark panel with the same sentence
# telling the operator to do the thing they had already done. What follows reads the key
# tolerantly and then SAYS what it forgave: a tolerance that hides what it forgave is how
# the next person loses the same afternoon.
KEY_VAR = "ANTHROPIC_API_KEY"

# Read, but never silently: state() names which one was used and that it is not canonical.
KEY_ALIASES = ("ANTHROPIC_APIKEY", "ANTHROPIC_API_TOKEN", "ANTHROPIC_KEY", "CLAUDE_API_KEY")

# A name is a near miss if it says ANTHROPIC/CLAUDE at all, or if it is simply CLOSE to
# the canonical name. The substring test alone misses the commonest typo there is — a
# transposition, ANTRHOPIC_API_KEY — which is exactly the case an operator cannot see by
# rereading their own variable list, because it reads correctly to a human eye.
_NEAR_MISS = ("ANTHROPIC", "CLAUDE_API", "CLAUDE_KEY")
_NEAR_RATIO = 0.82
# ...but saying ANTHROPIC is not enough on its own. ANTHROPIC_BASE_URL is a legitimate,
# unrelated variable, and accusing it of being a fumbled key sends an operator to fix a
# thing that is not broken — the same false-accusation failure check_partis guards against
# on the corpus side. A name qualifies on the substring only if it also reads as a
# credential; anything else has to earn it by shape.
_CREDENTIAL_WORDS = ("KEY", "TOKEN", "SECRET", "CREDENTIAL")

# Every platform that injects a public hostname also injects a marker of its own. Seeing
# none of them means this process is not the deployed one — which is a different problem
# from a missing variable, and must not be reported as the same one.
_PLATFORM_MARKERS = ("RAILWAY_", "RENDER_", "FLY_", "HEROKU_", "KOYEB_", "DYNO")


def _clean(value):
    """A usable key from whatever the variable editor stored, or None.

    The newline strip is not cosmetic. A value pasted with a trailing newline sends an
    invalid HTTP header, so the rail would come up reporting itself ON and then fail
    every single turn with an SDK error nobody can map back to the paste.
    """
    if not isinstance(value, str):
        return None
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1].strip()
    return v or None


def _lookup():
    """(name-as-set, cleaned-key) for the rail's credential, or (None, None).

    The exact canonical name wins, then the aliases, then a scan matching on the STRIPPED
    name — Railway's raw variable editor will store `ANTHROPIC_API_KEY ` with the trailing
    space intact, and `os.environ.get` will never see it again.
    """
    names = (KEY_VAR,) + KEY_ALIASES
    for name in names:
        v = _clean(os.environ.get(name))
        if v:
            return name, v
    for raw_name, raw_value in os.environ.items():
        if raw_name.strip().upper() in names:
            v = _clean(raw_value)
            if v:
                return raw_name, v
    return None, None


def key():
    """The rail's credential, or None. Read at call time, never at import."""
    return _lookup()[1]


def _sdk_missing():
    try:
        import anthropic  # noqa: F401
    except ImportError as e:
        return f"the `{e.name or 'anthropic'}` package is not installed"
    return None


def _near_miss_names():
    """Environment variable NAMES that look like a fumbled attempt at the credential.

    Names only. The whole point is to let an operator see `ANTRHOPIC_API_KEY` sitting in
    their own variable list; printing any value would put a live key in a health response.
    """
    target = "".join(c for c in KEY_VAR if c.isalnum())
    found = []
    names = (KEY_VAR,) + KEY_ALIASES
    for raw_name in os.environ:
        k = raw_name.strip().upper()
        if k in names:
            continue
        flat = "".join(c for c in k if c.isalnum())
        says_anthropic = any(m in k for m in _NEAR_MISS)
        reads_as_credential = any(w in k for w in _CREDENTIAL_WORDS)
        close_by_shape = difflib.SequenceMatcher(None, flat, target).ratio() >= _NEAR_RATIO
        if (says_anthropic and reads_as_credential) or close_by_shape:
            found.append(raw_name)
    return sorted(found)


def _present_but_empty():
    """Names the lookup would have accepted that are set to nothing usable."""
    names = (KEY_VAR,) + KEY_ALIASES
    return sorted(raw for raw, value in os.environ.items()
                  if raw.strip().upper() in names and not _clean(value))


def _on_a_platform():
    return any(m in k.upper() for k in os.environ for m in _PLATFORM_MARKERS)


def state(disclose=False):
    """What /api/health reports about the rail. Off is never a bare false: the note names
    the one thing to change. `disclose` gates the near-miss NAMES on the caller being
    authorised, matching how allowed_hosts is handled — health is ungated, and an
    operator's own variable names are not for the open internet.
    """
    name, k = _lookup()
    # Quoted wherever it is printed: a name carrying whitespace is indistinguishable from
    # the canonical one in a variable list AND in a log line, which is the whole trap.
    shown = f"'{name}'" if name and name != name.strip() else name
    sdk = _sdk_missing()
    st = {"on": bool(k) and sdk is None, "variable": name, "note": None}
    misses = _near_miss_names()
    if disclose and misses:
        st["candidates"] = misses

    if k and sdk:
        st["note"] = (f"{shown} is attached, but {sdk} — the rail cannot run. "
                      f"pip install -r workbench/requirements.txt")
    elif k and name != KEY_VAR and name.strip().upper() == KEY_VAR:
        # The variable list shows `ANTHROPIC_API_KEY`; the stored name is `ANTHROPIC_API_KEY `
        # and nothing on screen distinguishes them. Quote it so the space is visible.
        st["note"] = (f"the variable name is stored as '{name}', not {KEY_VAR} — it carries "
                      f"whitespace or a case difference. The key was read anyway; rename it "
                      f"so this deployment does not depend on that.")
    elif k and name != KEY_VAR:
        st["note"] = (f"the key was read from {shown}. The canonical name is {KEY_VAR}; "
                      f"rename it so this deployment does not depend on a fallback.")
    elif k and not k.startswith("sk-ant-"):
        # Reported, not refused: key prefixes are Anthropic's to change, and refusing on
        # one would be this file deciding a thing it does not own. The turn will say so.
        st["note"] = (f"{shown} is attached but does not look like an Anthropic key "
                      f"(no sk-ant- prefix). If a turn fails on authentication, that is why.")
    elif _present_but_empty():
        # Asked of every name the lookup accepts, not just the canonical one: a variable
        # that exists and holds nothing is a different mistake from one that never
        # arrived, and telling someone to set what they have set is the whole bug here.
        st["note"] = (f"{', '.join(_present_but_empty())} is set but empty once quotes and "
                      f"whitespace are stripped — the variable exists with no key in it.")
    elif misses:
        n = len(misses)
        subject = ("one variable name looks close" if n == 1
                   else f"{n} variable names look close")
        st["note"] = (f"no {KEY_VAR} in this process, but {subject}" +
                      (f": {', '.join(misses)}" if disclose else "") +
                      f" — rename it to {KEY_VAR} exactly, with no spaces in the name.")
    elif _on_a_platform():
        st["note"] = (f"no {KEY_VAR} reached this process, though it is running on a "
                      f"platform. A project- or environment-level variable is NOT injected "
                      f"until the service references it: set {KEY_VAR} on THIS service's "
                      f"own Variables tab, in the environment the live domain points at, "
                      f"and redeploy.")
    else:
        st["note"] = f"no {KEY_VAR} in the environment — set it and restart."
    return st


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


def _client():
    if _client_factory:
        return _client_factory()
    import anthropic
    # Pass the CLEANED key rather than letting the SDK re-read the raw variable: the whole
    # point of _clean is that the raw one may carry a newline the header layer rejects.
    return anthropic.Anthropic(api_key=key())


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
    if not _client_factory:
        st = state(disclose=True)
        if not st["on"]:
            # The reason travels with the refusal. "The rail is off" without it is the
            # error message that sent an operator round the loop of re-setting a variable
            # that was already set.
            yield _sse("error", {"error": f"the rail is off — {st['note']}",
                                 "honest": True, "rail": st})
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
