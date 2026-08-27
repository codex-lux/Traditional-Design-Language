"""An SSE stream must not hold an anyio threadpool token for its lifetime.

Starlette wraps a SYNC iterator handed to StreamingResponse in `iterate_in_threadpool`,
which spends one anyio threadpool token per `next()`. That is harmless when `next()`
returns immediately. It is not harmless when `next()` blocks: `jobs.events` used to sit in
`job.events.get(timeout=1.0)`, so an open compose stream held a token for its ENTIRE life
rather than for the instant it took to produce a line.

The default limiter is 40 tokens for the whole application. So roughly forty readers
watching a compose starved every sync `def` endpoint in the server — including
`/api/health`, which is what the platform healthcheck polls, so the visible symptom would
have been the container restarting under load rather than anything pointing at SSE.

`test_health_survives_many_open_streams` is the one that measures the property end to end.
`test_jobs_events_is_an_async_generator` is the cheap structural guard that fails the moment
someone converts it back, because the end-to-end one needs a live server and will be skipped
in environments that cannot start one.
"""
import inspect

import pytest

from workbench.server import jobs


def test_jobs_events_is_an_async_generator():
    """If this is ever a plain `def` again, every open stream costs a thread."""
    assert inspect.isasyncgenfunction(jobs.events), (
        "jobs.events must be an async generator — a sync one is wrapped in "
        "iterate_in_threadpool and holds a threadpool token for the whole stream")


def test_the_event_loop_is_never_blocked_between_events():
    """The drain must be non-blocking, so the await between drains is the only wait.

    A `get(timeout=...)` here would still block the thread it runs on; `get_nowait` plus an
    `await asyncio.sleep` is what makes the difference, so pin the call rather than trusting
    the docstring above it.
    """
    # The DOCSTRING names the old blocking call, on purpose — so scan the code with the
    # docstring removed, or this test fails on the explanation of the bug it guards.
    src = inspect.getsource(jobs.events)
    doc = inspect.getdoc(jobs.events) or ""
    for line in doc.splitlines():
        src = src.replace(line, "")
    assert "get_nowait()" in src, "the queue drain must not block"
    assert "await asyncio.sleep" in src, "the wait between drains must yield the loop"
    assert "job.events.get(" not in src, "a blocking get is exactly the bug this closed"


def test_heartbeat_cadence_is_unchanged():
    """The fix must not have changed what a reader sees: still ~1 s between heartbeats."""
    assert jobs._POLL_S * jobs._HEARTBEAT_EVERY == pytest.approx(1.0), (
        "the heartbeat interval moved; readers and proxies both depend on it")
