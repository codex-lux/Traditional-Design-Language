"""WP-9.3 -- the critique and the loop reach the bench.

Three routes: POST /api/plan/critique (synchronous, the analyst), POST /api/plan/revise (a job
on the compose pool, one `round` event per round) and GET /api/jobs/{id}/plan (the revised
record, placement stripped, report kept). Each test is named for the defect it forbids.
"""
import inspect
import json
import os
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


def test_the_round_event_is_built_from_the_record_and_never_edits_it():
    """revise() appends the round record to its report BEFORE firing on_round; a callback
    that popped keys off it would edit the report the job later returns. The event is a
    new dict: mutate it and the record is untouched."""
    from workbench.server import jobs
    src = inspect.getsource(jobs._run_revise)
    assert ".pop(" not in src and "del rnd" not in src
    assert re.search(r'"opened_n":\s*len\(rnd\.get\("opened"\)', src)


def test_strip_plans_is_one_rule_for_both_job_kinds():
    from workbench.server import jobs
    compose_like = {"candidates": [{"plan": {"levels": [{"rooms": [1, 2]}]}, "score": 1}]}
    revise_like = {"plan": {"levels": [{"rooms": [1, 2, 3]}]}, "report": {}}
    a = jobs._strip_plans(compose_like)
    b = jobs._strip_plans(revise_like)
    assert "plan" not in a["candidates"][0] and a["candidates"][0]["plan_rooms"] == 2
    assert "plan" not in b and b["plan_rooms"] == 3
    assert "plan" in revise_like, "strip works on a copy, never on the job's own result"
