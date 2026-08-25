"""Compose jobs. compose() takes seconds, so it runs on a single worker thread and
reports through an event queue the SSE endpoint drains. Results (with full plans)
are held in memory for 30 minutes; the server holds no other state.
"""
import json
import queue
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from . import corpus

core = corpus.core

_JOBS = {}
_POOL = ThreadPoolExecutor(max_workers=1)
TTL_S = 30 * 60


class Job:
    def __init__(self, brief, candidates):
        self.id = uuid.uuid4().hex[:12]
        self.brief = brief
        self.candidates = candidates
        self.events = queue.Queue()
        self.status = "queued"
        self.result = None
        self.error = None
        self.created = time.time()


def _strip_plans(result):
    """The summary the Candidate Set shows; full plans stay server-side per job."""
    out = core.copy_json(result)
    for c in out.get("candidates", []):
        plan = c.pop("plan", None)
        c["plan_rooms"] = (sum(len(l["rooms"]) for l in plan["levels"]) if plan else None)
    return out


def _run(job):
    job.status = "running"
    job.events.put({"event": "stage", "data": {"stage": "seeding",
                    "note": "reading the brief, resolving partis native to the style"}})
    try:
        composer = core._composer()
        done = []

        def on_candidate(summary):
            done.append(summary)
            job.events.put({"event": "candidate", "data": {
                "n": len(done), "parti": summary.get("parti"),
                "parti_name": summary.get("parti_name"), "score": summary.get("score")}})

        try:
            result = composer.compose(job.brief, job.candidates, on_candidate=on_candidate)
        except TypeError:
            # composer without the callback parameter — indeterminate progress
            job.events.put({"event": "stage", "data": {"stage": "composing",
                            "note": "repairing candidates against the validator (~8 s)"}})
            result = composer.compose(job.brief, job.candidates)
        job.result = result
        job.status = "done"
        job.events.put({"event": "done", "data": _strip_plans(result)})
    except Exception as e:  # a failed compose is reported, never swallowed
        job.status = "error"
        job.error = str(e)[:500]
        job.events.put({"event": "error", "data": {"error": job.error}})


def submit(brief, candidates=4):
    # validate the brief immediately so a malformed one fails fast, not mid-job
    err = _validate_brief(brief)
    if err:
        return {"error": err["error"], "detail": err.get("detail"), "hint": err.get("hint")}
    _reap()
    job = Job(brief, candidates)
    _JOBS[job.id] = job
    _POOL.submit(_run, job)
    return {"job_id": job.id}


def _validate_brief(brief):
    import jsonschema
    import os
    try:
        schema = json.load(open(os.path.join(corpus.ROOT, "schema", "brief.schema.json")))
        jsonschema.validate(brief, schema)
    except jsonschema.ValidationError as e:
        return {"error": "brief does not match the brief schema", "detail": str(e)[:400],
                "hint": "the minimum is style and target_area_sf"}
    return None


def get(job_id):
    job = _JOBS.get(job_id)
    if not job:
        return None
    return {"job_id": job.id, "status": job.status, "error": job.error,
            "result": _strip_plans(job.result) if job.result else None}


def candidate_plan(job_id, n):
    job = _JOBS.get(job_id)
    if not job or not job.result:
        return None
    cands = job.result.get("candidates", [])
    if not (0 <= n < len(cands)):
        return None
    return cands[n].get("plan")


def events(job_id):
    """Generator of SSE lines for one job. Replays nothing; attach before submit races
    are avoided because submit() returns before the worker can finish seeding."""
    job = _JOBS.get(job_id)
    if not job:
        yield _sse("error", {"error": "unknown job"})
        return
    while True:
        if job.status in ("done", "error") and job.events.empty():
            break
        try:
            ev = job.events.get(timeout=1.0)
        except queue.Empty:
            yield ": heartbeat\n\n"
            continue
        yield _sse(ev["event"], ev["data"])
        if ev["event"] in ("done", "error"):
            break


def _sse(event, data):
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _reap():
    now = time.time()
    for jid in [j for j, job in _JOBS.items() if now - job.created > TTL_S]:
        del _JOBS[jid]
