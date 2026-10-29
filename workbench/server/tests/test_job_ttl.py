"""WP-17.6: a job's TTL is counted from when it FINISHED, never from when it was submitted.

A compose now places up to eight houses at a minute's budget each. Counted from submission, a job
that waited its turn behind another and then ran for ten minutes was reaped from `_JOBS` while its
reader was still waiting for the result -- indistinguishable, from the surface, from a compose that
never answered. A RUNNING job is never reaped; a queued one is reaped from its submission."""
from workbench.server import jobs


def _job(status, created_ago, finished_ago=None, now=10_000.0):
    j = jobs.Job({"id": "b"}, 1)
    j.status = status
    j.created = now - created_ago
    j.finished = None if finished_ago is None else now - finished_ago
    return j


def test_a_running_job_is_never_reapable_however_old():
    assert jobs._age_s(_job("running", jobs.TTL_S * 10), 10_000.0) is None


def test_a_finished_job_ages_from_its_finish_not_its_submission():
    j = _job("done", created_ago=jobs.TTL_S + 600, finished_ago=60)
    assert jobs._age_s(j, 10_000.0) == 60


def test_a_queued_job_ages_from_its_submission():
    assert jobs._age_s(_job("queued", 120), 10_000.0) == 120


def test_reap_keeps_a_long_job_and_drops_a_stale_one(monkeypatch):
    now = 1_000_000.0
    monkeypatch.setattr(jobs.time, "time", lambda: now)
    long_run = _job("running", jobs.TTL_S * 3, now=now)
    fresh_done = _job("done", jobs.TTL_S * 3, finished_ago=30, now=now)
    stale_done = _job("error", jobs.TTL_S * 3, finished_ago=jobs.TTL_S + 1, now=now)
    stale_queue = _job("queued", jobs.TTL_S + 1, now=now)
    js = [long_run, fresh_done, stale_done, stale_queue]
    try:
        for j in js:
            jobs._JOBS[j.id] = j
        jobs._reap()
        assert long_run.id in jobs._JOBS and fresh_done.id in jobs._JOBS
        assert stale_done.id not in jobs._JOBS and stale_queue.id not in jobs._JOBS
    finally:
        for j in js:
            jobs._JOBS.pop(j.id, None)


def test_every_terminal_transition_stamps_the_finish():
    """A path that sets `done` or `error` without `finished` falls back to `created`, which is the
    defect this file guards: read the source so a new terminal branch cannot forget the stamp."""
    import inspect, re
    src = inspect.getsource(jobs)
    terminal = re.findall(r'^( +)job\.status = "(?:done|error)"\n\1job\.finished = time\.time\(\)$', src, re.M)
    bare = re.findall(r'job\.status = "(?:done|error)"', src)
    assert bare and len(terminal) == len(bare), (len(terminal), len(bare))
