"""A failed job and a failed assistant turn leave a traceback in the server's log (DR-05).

Review of 27 Nov 2026. Each of these `except` blocks told the READER what went wrong, in a
string cut at a few hundred characters, and told the operator nothing: no log line and no
traceback, on a server that also runs uvicorn at `warning` and so writes no access log. A compose
that failed for every reader looked, from outside the browser, like a quiet afternoon.
"""
import logging

import pytest

from workbench.server import jobs, rail


def _failed(caplog, logger):
    return [r for r in caplog.records
            if r.name == logger and r.levelno >= logging.ERROR and r.exc_info]


def test_a_failed_compose_is_logged_with_its_traceback(caplog, monkeypatch):
    def broken():
        raise RuntimeError("the composer fell over")
    monkeypatch.setattr(jobs.core, "_composer", broken)
    job = jobs.Job({"style": "craftsman", "target_area_sf": 1800}, 1)
    monkeypatch.setitem(jobs._JOBS, job.id, job)
    with caplog.at_level(logging.ERROR, logger="tdl.jobs"):
        jobs._run(job)
    assert job.status == "error" and "fell over" in job.error      # the reader is still told
    recs = _failed(caplog, "tdl.jobs")
    assert len(recs) == 1, "a failed compose left no error record with a traceback"
    assert job.id in recs[0].getMessage() and recs[0].exc_info[0] is RuntimeError


def test_a_failed_revise_is_logged_with_its_traceback(caplog, monkeypatch):
    def broken(*a, **k):
        raise RuntimeError("the loop fell over")
    monkeypatch.setattr(jobs.core, "revise_plan", broken)
    job = jobs.Job(None, None, {}, kind="revise", plan={"id": "x", "levels": []})
    monkeypatch.setitem(jobs._JOBS, job.id, job)
    with caplog.at_level(logging.ERROR, logger="tdl.jobs"):
        jobs._run(job)
    assert job.status == "error"
    recs = _failed(caplog, "tdl.jobs")
    assert len(recs) == 1 and job.id in recs[0].getMessage()


class _Broken:
    class messages:                                    # noqa: N801 -- the SDK's own attribute name
        @staticmethod
        def create(**_kw):
            raise RuntimeError("the API call fell over")


@pytest.fixture
def broken_rail():
    rail.set_client_factory(lambda: _Broken())
    yield
    rail.set_client_factory(None)


def test_a_failed_assistant_turn_is_logged_and_the_reader_is_still_told(caplog, broken_rail):
    secret_words = "the reader's own question, which is not the log's to keep"
    with caplog.at_level(logging.ERROR, logger="tdl.rail"):
        lines = list(rail.stream_turn({"messages": [{"role": "user", "content": secret_words}]}))
    assert any("event: error" in l and "fell over" in l for l in lines)
    recs = _failed(caplog, "tdl.rail")
    assert len(recs) == 1, "a failed assistant turn left no error record with a traceback"
    assert secret_words not in caplog.text, "the reader's message was written to the log"


def test_a_stream_that_dies_outside_its_own_handler_is_logged(caplog):
    import asyncio

    def dies():
        yield "event: turn_start\ndata: {}\n\n"
        raise RuntimeError("the generator fell over")

    async def drain():
        return [line async for line in jobs.bridge_sync_stream(dies, poll_s=0.001)]

    with caplog.at_level(logging.ERROR, logger="tdl.rail"):
        lines = asyncio.run(drain())
    assert any("event: error" in l for l in lines)
    assert len(_failed(caplog, "tdl.rail")) == 1
