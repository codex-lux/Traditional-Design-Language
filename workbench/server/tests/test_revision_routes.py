"""WP-9.3 -- the critique and the loop reach the bench.

Three routes: POST /api/plan/critique (synchronous, the analyst), POST /api/plan/revise (a job
on the compose pool, one `round` event per round) and GET /api/jobs/{id}/plan (the revised
record, placement stripped, report kept). Each test is named for the defect it forbids.
"""
import inspect
import json
import os
import time
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _plan(pid="tidewater-georgian-careful"):
    return json.load(open(os.path.join(ROOT, "plans", f"{pid}.json"), encoding="utf-8"))


def _wait(client, job_id, tries=360):
    import time
    for _ in range(tries):
        j = client.get(f"/api/jobs/{job_id}").json()
        if j["status"] in ("done", "error"):
            return j
        time.sleep(0.5)
    return j


# ------------------------------------------------------------------ critique
def test_critique_route_is_the_analyst_the_cli_runs(client):
    """Parity with an in-process core.critique_plan on the search engine: same engine that
    ran, same key, same class counts. The solve cache makes the two placements one."""
    from workbench.server import corpus
    plan = _plan()
    r = client.post("/api/plan/critique",
                    json={"plan": plan, "engine": "heuristic", "candidates": 120}).json()
    direct = corpus.core.critique_plan(plan, engine="heuristic", candidates=120)
    assert r["engine"]["ran"] == direct["engine"]["ran"] == "heuristic"
    assert r["key"] == direct["key"]
    assert r["counts_by_class"] == direct["counts_by_class"]
    # the assessment carries finding ids, which is what the bench badges on
    for cls, items in r["assessment"].items():
        assert all(i.get("id") for i in items), cls
    # every non-info finding is in exactly one class or in could_not_evaluate
    assert set(r["assessment"]) == {"actionable", "placement", "critic_suspect", "architect", "advisory"}


def test_critique_route_refuses_a_bad_engine_a_missing_plan_and_a_bad_record(client):
    assert client.post("/api/plan/critique", json={"plan": _plan(), "engine": "cp-sat"}).status_code == 422
    assert client.post("/api/plan/critique", json={}).status_code == 422
    r = client.post("/api/plan/critique", json={"plan": {"id": "x", "style": "tidewater-georgian"}})
    assert r.status_code == 422
    assert "schema" in json.dumps(r.json()["detail"])


def test_both_new_routes_are_metered():
    """The only 'is it metered' test this suite has greps the route's source for the call
    (test_request_limits.test_dev_reload_is_metered); the same shape here."""
    from workbench.server import app as app_mod
    for fn in (app_mod.plan_critique, app_mod.plan_revise):
        src = inspect.getsource(fn)
        body = src.split('"""', 2)[-1] if src.count('"""') >= 2 else src
        assert "_heavy(request)" in body, fn.__name__


# ------------------------------------------------------------------ revise
def test_revise_job_round_trip_reports_rounds_and_hands_the_record_through_its_own_route(client):
    """The compose round-trip's shape: submit, poll, read. The `done` payload carries the
    report and a room count and NOT the plan; the record comes through /plan with its
    placement stripped and its revision_report kept; and a `round` event was put on the
    queue (which only a consumer drains, so the test can read it)."""
    from workbench.server import jobs
    job = client.post("/api/plan/revise",
                      json={"plan": _plan("spec-builder-colonial"), "engine": "heuristic",
                            "rounds": 1, "candidates": 120, "budget_s": 60}).json()
    assert "job_id" in job, job
    j = _wait(client, job["job_id"])
    assert j["status"] == "done", j
    res = j["result"]
    assert "report" in res and "plan_rooms" in res and "plan" not in res
    assert res["report"]["mode"] == "placed"
    assert res["report"]["summary"]["rounds"] >= 1
    plan = client.get(f"/api/jobs/{job['job_id']}/plan")
    assert plan.status_code == 200
    plan = plan.json()
    assert plan["revision_report"]["mode"] == "placed"
    assert not any("geometry" in r for lv in plan["levels"] for r in lv["rooms"]), \
        "the revised record must come back stripped: the bench re-solves what it loads"
    assert "footprint" not in plan and "geometry_report" not in plan
    # all FOUR strip tuples, not three (WP-9.4): a strip that forgot the doors passed
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    OP = modcache.load("openings", os.path.join(ROOT, "build", "openings.py"))
    for k in OP.PLACEMENT_PLAN_KEYS:
        assert k not in plan, k
    for lv in plan["levels"]:
        for r in lv["rooms"]:
            assert not (set(OP.PLACEMENT_ROOM_KEYS) & set(r)), (r["id"], set(OP.PLACEMENT_ROOM_KEYS) & set(r))
            for d in r.get("doors") or []:
                assert not (set(OP.PLACEMENT_DOOR_KEYS) & set(d)), (r["id"], d)
            for w in r.get("windows") or []:
                assert not (set(OP.PLACEMENT_WINDOW_KEYS) & set(w)), (r["id"], w)
    events = list(jobs._JOBS[job["job_id"]].events.queue)
    kinds = [e["event"] for e in events]
    assert "round" in kinds and kinds[-1] == "done", kinds
    rnd = next(e["data"] for e in events if e["event"] == "round")
    assert set(rnd) >= {"n", "engine", "accepted", "key_before", "key_after", "moves", "opened_n"}
    assert rnd["engine"] in ("heuristic", "cp-sat")
    for m in rnd["moves"]:
        assert set(m) >= {"move", "finding", "cleared"}
        assert "log" not in m and "lever" not in m, "the round event carries a summary, not the log"


def test_a_compose_job_has_no_revised_plan_and_an_unknown_job_is_404(client):
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    job = client.post("/api/compose", json={"brief": brief, "candidates": 1, "revise": False}).json()
    _wait(client, job["job_id"])
    assert client.get(f"/api/jobs/{job['job_id']}/plan").status_code == 404
    assert client.get("/api/jobs/nope/plan").status_code == 404


def test_revise_route_refuses_a_bad_engine_and_a_bad_record_before_a_job_exists(client):
    from workbench.server import jobs
    before = set(jobs._JOBS)
    assert client.post("/api/plan/revise", json={"plan": _plan(), "engine": "fast"}).status_code == 422
    assert client.post("/api/plan/revise", json={"plan": {"id": "x"}}).status_code == 422
    assert client.post("/api/plan/revise", json={}).status_code == 422
    assert set(jobs._JOBS) == before, "a refused submission must not leave a job behind"


def test_the_round_event_is_built_from_the_record_and_never_edits_it(client):
    """revise() appends the round record to its report BEFORE firing on_round; a callback
    that popped keys off it would edit the report the job later returns. The first version
    of this test grepped the source for two spellings of a mutation (`.pop(`, `del rnd`) --
    the technique test_sse_does_not_hold_threads.py records failing three times. Now the
    record is compared after the fact: every round in the report still carries the full
    move entries (log, basis, lever) the event summarises away, and the event carries none."""
    from workbench.server import jobs
    job = client.post("/api/plan/revise",
                      json={"plan": _plan("spec-builder-colonial"), "engine": "heuristic",
                            "rounds": 1, "candidates": 120, "budget_s": 60}).json()
    j = _wait(client, job["job_id"])
    assert j["status"] == "done", j
    report_rounds = jobs._JOBS[job["job_id"]].result["report"]["rounds"]
    events = [e["data"] for e in list(jobs._JOBS[job["job_id"]].events.queue) if e["event"] == "round"]
    assert len(events) == len(report_rounds) >= 1
    for ev, rd in zip(events, report_rounds):
        assert ev is not rd and ev["moves"] is not rd["moves"]
        assert len(ev["moves"]) == len(rd["moves"])
        for em, rm in zip(ev["moves"], rd["moves"]):
            assert "log" not in em and "lever" not in em
            assert ("log" in rm) or rm.get("refused"), "the report keeps the full entry"


def test_strip_plans_is_one_rule_for_both_job_kinds():
    from workbench.server import jobs
    compose_like = {"candidates": [{"plan": {"levels": [{"rooms": [1, 2]}]}, "score": 1}]}
    revise_like = {"plan": {"levels": [{"rooms": [1, 2, 3]}]}, "report": {}}
    a = jobs._strip_plans(compose_like)
    b = jobs._strip_plans(revise_like)
    assert "plan" not in a["candidates"][0] and a["candidates"][0]["plan_rooms"] == 2
    assert "plan" not in b and b["plan_rooms"] == 3
    assert "plan" in revise_like, "strip works on a copy, never on the job's own result"


def test_a_revise_job_always_has_a_budget_and_at_least_one_round(client, monkeypatch):
    """WP-9.4. The route's docstring promised a body could not ask for an unbounded job, and
    `budget_s` was optional: omitted, `revise()` saw None and ran eight rounds of proofs on the
    one-worker pool. A budget is always set now, and a revise of zero rounds is a critique."""
    from workbench.server import jobs
    seen = {}
    real = jobs.submit_revise

    def spy(plan, options=None):
        seen.update(options or {})
        return {"job_id": "spy"}
    monkeypatch.setattr(jobs, "submit_revise", spy)
    r = client.post("/api/plan/revise", json={"plan": _plan(), "engine": "heuristic", "rounds": 0})
    assert r.status_code == 200
    assert seen["budget_s"] == 120.0 and seen["rounds"] == 1
    seen.clear()
    client.post("/api/plan/revise", json={"plan": _plan(), "engine": "heuristic", "budget_s": 9999, "rounds": 99})
    assert seen["budget_s"] == 600.0 and seen["rounds"] == 8


def test_the_critique_route_coerces_place_as_the_evaluate_route_does(client, monkeypatch):
    from workbench.server import corpus
    seen = {}

    def spy(plan, **kw):
        seen.update(kw)
        return {"error": "spy"}
    monkeypatch.setattr(corpus.core, "critique_plan", spy)
    client.post("/api/plan/critique", json={"plan": _plan(), "place": "false"})
    assert seen["place"] is True, "a string is truthy and the route says so with a bool, as evaluate does"
    client.post("/api/plan/critique", json={"plan": _plan(), "place": False})
    assert seen["place"] is False


def test_both_new_routes_refuse_when_the_heavy_bucket_is_spent(client, monkeypatch):
    """The metering guard was a source grep for `_heavy(request)` that a comment satisfies
    (the session's audit). Spend the bucket and watch both routes answer 429."""
    from workbench.server import limits
    monkeypatch.setenv("HEAVY_CALLS_PER_HOUR", "1")
    limits.reset()
    r1 = client.post("/api/plan/critique", json={"plan": _plan(), "engine": "heuristic", "candidates": 10, "place": False})
    assert r1.status_code == 200, r1.text[:200]
    r2 = client.post("/api/plan/critique", json={"plan": _plan(), "engine": "heuristic", "candidates": 10, "place": False})
    r3 = client.post("/api/plan/revise", json={"plan": _plan(), "engine": "heuristic", "rounds": 1})
    assert r2.status_code == 429 and r3.status_code == 429, (r2.status_code, r3.status_code)
    limits.reset()


def test_the_round_event_carries_the_entrys_own_verdict(client):
    """The bench derived "applied" from the ABSENCE of a refusal (the session's audit); the
    event carries `accepted` now, and a refused entry carries its reason."""
    from workbench.server import jobs
    job = client.post("/api/plan/revise",
                      json={"plan": _plan("spec-builder-colonial"), "engine": "heuristic",
                            "rounds": 2, "candidates": 120, "budget_s": 60}).json()
    j = _wait(client, job["job_id"])
    assert j["status"] == "done", j
    events = [e["data"] for e in list(jobs._JOBS[job["job_id"]].events.queue) if e["event"] == "round"]
    entries = [m for ev in events for m in ev["moves"]]
    assert entries
    for m in entries:
        assert (m.get("accepted") is True) or m.get("refused") or m.get("refused_by_measurement"), m


# ------------------------------------------------------------------ the session's audit
def test_the_critique_route_never_hands_core_a_parti_record(client, monkeypatch):
    """The route's own refusal was unobservable: core.critique_plan refuses a record too, so
    dropping the route's isinstance left the parti test green (the session's audit). A spy
    on core asserts the route never called it with a dict at all."""
    from workbench.server import corpus, app as appmod
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    calls = []
    orig = corpus.core.critique_plan

    def spy(plan, **kw):
        calls.append(kw.get("parti"))
        return orig(plan, **kw)
    monkeypatch.setattr(corpus.core, "critique_plan", spy)
    r = client.post("/api/plan/critique", json={"plan": plan, "engine": "heuristic", "candidates": 1,
                                                "parti": {"scaling": {"bay_module_ft": 0}}})
    assert r.status_code == 422 and "a string" in json.dumps(r.json()["detail"])
    assert calls == [], "the route reached core with a parti record"


def test_a_full_queue_is_refused_with_503_and_a_retry_hint(client, monkeypatch):
    """The one-worker pool's queue was unbounded and every queued job held its submitted
    record: thirty 8 MB plans behind one long job (the session's audit)."""
    from workbench.server import jobs
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    fakes = [jobs.Job(None, None, {}, kind="revise", plan={}) for _ in range(jobs.MAX_QUEUED)]
    for j in fakes:
        jobs._JOBS[j.id] = j                 # status "queued", never submitted to the pool
    try:
        r = client.post("/api/plan/revise", json={"plan": plan, "engine": "heuristic", "candidates": 1, "rounds": 1})
        assert r.status_code == 503, r.text[:200]
        assert r.headers.get("retry-after") == "30" and r.json()["detail"]["queued"] == jobs.MAX_QUEUED
        brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
        r2 = client.post("/api/compose", json={"brief": brief, "candidates": 1})
        assert r2.status_code == 503
    finally:
        for j in fakes:
            jobs._JOBS.pop(j.id, None)


def test_a_reaped_job_does_not_run_and_a_done_revise_job_has_released_its_record(monkeypatch):
    from workbench.server import jobs
    job = jobs.Job(None, None, {}, kind="revise", plan={"levels": []})
    jobs._run(job)                           # never in _JOBS: reaped before its turn
    assert job.status == "error" and "expired" in job.error and job.result is None
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    res = jobs.submit_revise(plan, options={"engine": "heuristic", "candidates": 1, "rounds": 1, "budget_s": 5})
    jid = res["job_id"]
    for _ in range(600):
        if jobs._JOBS[jid].status in ("done", "error"):
            break
        time.sleep(0.2)
    j = jobs._JOBS[jid]
    assert j.status == "done", j.error
    assert j.plan is None, "the submitted record is held for the job's whole life"
    assert j.result["plan"]["revision_report"] is j.result["report"], "the report is stored twice"
