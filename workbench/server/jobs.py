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
            # `disqualified` and the fatal count ride WITH the score, never behind it. The
            # score is now a composite out of 100 that a disqualified candidate can top, and
            # the disqualification band the Candidate Set draws exists precisely because that
            # number cannot stand on its own — a progress line publishing it alone would put
            # the highest-looking figure on the screen next to a plan carrying two fatals.
            # `n` is ARRIVAL order, not rank: compose() has not sorted anything yet here.
            job.events.put({"event": "candidate", "data": {
                "n": len(done), "parti": summary.get("parti"),
                "parti_name": summary.get("parti_name"), "score": summary.get("score"),
                "disqualified": bool(summary.get("disqualified")),
                "fatal": (summary.get("counts") or {}).get("fatal", 0)}})

        # Detect the callback parameter by signature rather than catching
        # TypeError around the call — a genuine TypeError inside a working
        # compose() must surface once, not silently re-run the whole ~8s job.
        import inspect
        takes_callback = "on_candidate" in inspect.signature(composer.compose).parameters
        if takes_callback:
            result = composer.compose(job.brief, job.candidates, on_candidate=on_candidate)
        else:
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
    import os
    try:
        import jsonschema
    except ImportError:
        # an absent validator is an environment fact, never a verdict on the brief
        return {"error": "could not validate: the jsonschema package is not installed",
                "detail": "pip install -r workbench/requirements.txt"}
    try:
        schema = json.load(open(os.path.join(corpus.ROOT, "schema", "brief.schema.json")))
        jsonschema.validate(brief, schema)
    except jsonschema.ValidationError as e:
        return {"error": "brief does not match the brief schema", "detail": str(e)[:400],
                "hint": "the minimum is style and target_area_sf"}
    return None


def get(job_id):
    _reap()   # the TTL is enforced on every touch, not only on the next submit
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
    """Generator of SSE lines for one job.

    The per-job queue is single-consumer: whichever stream drains an event owns
    it. A second consumer (a reconnect, a second tab, React StrictMode's double
    mount) can therefore find the queue empty — so a finished job always closes
    with a synthetic terminal event from the job's own state, and a late attach
    on a finished job gets its result rather than a silent stream."""
    job = _JOBS.get(job_id)
    if not job:
        yield _sse("error", {"error": "unknown job"})
        return
    _reap()
    saw_terminal = False
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
            saw_terminal = True
            break
    if not saw_terminal and job.status in ("done", "error"):
        if job.status == "done" and job.result is not None:
            yield _sse("done", _strip_plans(job.result))
        else:
            yield _sse("error", {"error": job.error or "job failed"})


def _sse(event, data):
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _reap():
    now = time.time()
    for jid in [j for j, job in _JOBS.items() if now - job.created > TTL_S]:
        del _JOBS[jid]
