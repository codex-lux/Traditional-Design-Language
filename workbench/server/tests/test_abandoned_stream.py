"""A reader who leaves stops the turn, and the worker thread ends.

Deployment-readiness review, 27 Nov 2026 (DR-16). `jobs.bridge_sync_stream` runs the assistant's
blocking generator on its own thread and hands its lines to the response. When the reader went
away -- a closed tab, a dropped connection -- the response stopped reading and the thread did
not stop producing: it ran the turn to the end, up to ten billed requests for nobody, and if
more than 64 lines were queued it blocked on a full queue for the life of the process.

A request already on the wire cannot be recalled; the SDK call is blocking. What stops is
everything after it: the generator is closed at its next line, so no further request is made.
"""
import asyncio
import logging
import threading
import time

from workbench.server import jobs, rail


def _wait(event, seconds=3.0):
    return event.wait(seconds)


def test_when_the_reader_leaves_the_source_is_closed_and_stops_being_pulled():
    pulled, closed = [], threading.Event()

    def source():
        try:
            for i in range(10_000):
                pulled.append(i)
                yield f"line {i}\n"
                time.sleep(0.002)
        finally:
            closed.set()

    async def read_two_and_leave():
        stream = jobs.bridge_sync_stream(source, poll_s=0.001)
        got = [await stream.__anext__(), await stream.__anext__()]
        await stream.aclose()
        return got

    assert asyncio.run(read_two_and_leave()) == ["line 0\n", "line 1\n"]
    assert _wait(closed), "the generator was never closed: the turn runs on for nobody"
    at_close = len(pulled)
    time.sleep(0.05)
    assert len(pulled) == at_close, "it was still being pulled after it was closed"
    assert at_close < 200, f"{at_close} lines were produced for a reader who left after two"


def test_a_full_queue_and_no_reader_does_not_hold_the_thread_for_ever():
    """More than 64 lines with nobody reading used to block `q.put` until the process died."""
    done = threading.Event()

    def flood():
        try:
            for i in range(5_000):
                yield "x\n"
        finally:
            done.set()

    async def read_one_and_leave():
        stream = jobs.bridge_sync_stream(flood, poll_s=0.001)
        await stream.__anext__()
        await asyncio.sleep(0.05)          # let the producer fill the queue and block
        await stream.aclose()

    before = threading.active_count()
    asyncio.run(read_one_and_leave())
    assert _wait(done), "the producer is still blocked on a queue nobody reads"
    deadline = time.monotonic() + 3
    while threading.active_count() > before and time.monotonic() < deadline:
        time.sleep(0.01)
    assert threading.active_count() <= before, "the worker thread outlived its stream"


def test_a_cancelled_response_is_a_reader_who_left():
    """Starlette cancels the task that is streaming; it does not call aclose() politely."""
    closed = threading.Event()

    def source():
        try:
            while True:
                yield "tick\n"
                time.sleep(0.002)
        finally:
            closed.set()

    async def scenario():
        async def consume():
            async for _ in jobs.bridge_sync_stream(source, poll_s=0.001):
                pass
        task = asyncio.ensure_future(consume())
        await asyncio.sleep(0.05)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        await asyncio.sleep(0)             # let the generator's own finalizer run

    asyncio.run(scenario())
    assert _wait(closed)


def test_a_stream_read_to_the_end_is_whole_and_in_order():
    def source():
        for i in range(300):               # more than the queue holds: backpressure, not loss
            yield i

    async def read_all():
        return [x async for x in jobs.bridge_sync_stream(source, poll_s=0.001)]

    assert asyncio.run(read_all()) == list(range(300))


class _Block:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Resp:
    def __init__(self, content, stop):
        self.content, self.stop_reason = content, stop


def test_an_abandoned_turn_makes_no_further_request_and_says_so_in_the_log(caplog):
    calls = []

    class _Client:
        class messages:                    # noqa: N801 -- the SDK's own attribute name
            @staticmethod
            def create(**kw):
                calls.append(1)
                return _Resp([_Block(type="tool_use", id=f"tu_{len(calls)}",
                                     name="tdl_overview", input={})], "tool_use")

    rail.set_client_factory(lambda: _Client)
    try:
        with caplog.at_level(logging.INFO, logger="tdl.rail"):
            turn = rail.stream_turn({"messages": [{"role": "user", "content": "hi"}]})
            seen = []
            for line in turn:
                seen.append(line)
                if "event: tool_call" in line:
                    break
            turn.close()                   # what the bridge does when the reader has gone
    finally:
        rail.set_client_factory(None)

    assert len(calls) == 1, f"{len(calls)} requests were made; the reader left during the first round"
    usage = [r.getMessage() for r in caplog.records if "usage" in r.getMessage()]
    assert len(usage) == 1 and "requests=1" in usage[0] and "abandoned" in usage[0], usage
