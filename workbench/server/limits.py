"""Caps on what the rail may spend, and on how fast anyone may ask for it.

The rail calls the Anthropic API with the operator's key on behalf of whoever is past
the password. Two different things need bounding, and only one of them is a rate:

  **How often** a caller may take a turn — a windowed counter per identity, plus a
  process-wide daily backstop so one shared password cannot become an open tap.

  **How large** a single turn may be — the sharper of the two. rail.stream_turn takes
  `messages` from the request body: the client owns conversation state and replays the
  whole history every turn. Nothing bounded that array, so one request could carry an
  arbitrarily long history and be billed for it before any per-turn limit noticed. The
  shape checks below run *before* the first API call, which is the only place they help.

None of this is a spend cap in dollars. It cannot be — the only true ceiling is the
budget set on the key in the Anthropic Console. These caps slow the rate of approach to
that ceiling and make one abusive caller bounded rather than unbounded. `docs/deployment.md`
says so plainly rather than letting the limiter imply a guarantee it does not give.
"""
import json
import os
import threading
import time

_LOCK = threading.Lock()
_WINDOWS = {}  # key -> [window_start, count]
_LAST_REAP = [0.0]
REAP_EVERY_S = 600


def _env_int(name, default):
    try:
        return int(os.environ.get(name, "") or default)
    except ValueError:
        return default


def rail_turns_per_hour():
    return _env_int("RAIL_TURNS_PER_HOUR", 20)


def rail_turns_per_day():
    return _env_int("RAIL_TURNS_PER_DAY", 200)


def rail_max_messages():
    return _env_int("RAIL_MAX_MESSAGES", 40)


def rail_max_chars():
    return _env_int("RAIL_MAX_CHARS", 200_000)


def _reap(now):
    """Drop windows that have fully elapsed, so the table cannot grow without bound."""
    if now - _LAST_REAP[0] < REAP_EVERY_S:
        return
    _LAST_REAP[0] = now
    for key in [k for k, (start, _) in _WINDOWS.items() if now - start > 86_400 * 2]:
        del _WINDOWS[key]


def take(key, limit, window_s):
    """Consume one unit against `key`. Returns (ok, retry_after_seconds).

    A limit of 0 or less means unlimited — the knob is off, not set to deny everything.
    """
    if limit <= 0:
        return True, 0
    now = time.time()
    with _LOCK:
        _reap(now)
        start, count = _WINDOWS.get(key, (now, 0))
        if now - start >= window_s:
            start, count = now, 0
        if count >= limit:
            return False, max(1, int(window_s - (now - start)))
        _WINDOWS[key] = (start, count + 1)
        return True, 0


def peek(key):
    """Current (count, window_start) for `key`, for tests and diagnostics."""
    with _LOCK:
        start, count = _WINDOWS.get(key, (0.0, 0))
        return count, start


def reset():
    """Drop all counters. Tests only."""
    with _LOCK:
        _WINDOWS.clear()
        _LAST_REAP[0] = 0.0


def check_shape(body):
    """Refuse an oversized turn before it costs anything. Returns a reason, or None."""
    messages = body.get("messages") or []
    max_messages = rail_max_messages()
    if max_messages > 0 and len(messages) > max_messages:
        return (f"this conversation is {len(messages)} messages and the rail accepts "
                f"{max_messages} — start a new one; the corpus does not remember turns, "
                f"so nothing is lost by doing so")
    max_chars = rail_max_chars()
    if max_chars > 0:
        try:
            size = len(json.dumps(messages))
        except (TypeError, ValueError):
            return "this conversation could not be measured, so the rail will not send it"
        if size > max_chars:
            return (f"this conversation is {size:,} characters and the rail accepts "
                    f"{max_chars:,} — start a new one")
    return None


def check_rail(identity):
    """Rate-check one rail turn. Returns a reason, or None. Consumes on success."""
    ok, retry = take(f"rail:{identity}", rail_turns_per_hour(), 3600)
    if not ok:
        return (f"the rail's limit of {rail_turns_per_hour()} turns an hour is reached "
                f"for this session — about {retry // 60 + 1} minutes until it resets")
    ok, retry = take("rail:__all__", rail_turns_per_day(), 86_400)
    if not ok:
        return (f"the rail's daily ceiling of {rail_turns_per_day()} turns across all "
                f"users is reached — it resets in about {retry // 3600 + 1} hours")
    return None


def state():
    """What /api/health reports about the caps in force."""
    return {"turns_per_hour": rail_turns_per_hour(),
            "turns_per_day": rail_turns_per_day(),
            "max_messages": rail_max_messages(),
            "max_chars": rail_max_chars()}
