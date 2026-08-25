"""The load-bearing parity test: what the workbench shows must be exactly what the
validator says. The HTTP evaluate result is compared against a direct in-process
plan_check.check() call, finding for finding."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

PLANS = ["tidewater-georgian-careful", "spec-builder-colonial"]


def _direct_check(plan, strict=False):
    import sys
    sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
    import core
    return core.check_plan(core.copy_json(plan), strict=strict)


def test_evaluate_parity(client):
    for name in PLANS:
        plan = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
        via_http = client.post("/api/plan/evaluate",
                               json={"plan": plan, "place": False}).json()["check"]
        direct = _direct_check(plan)
        assert via_http["counts"] == direct["counts"], name
        assert [f["statement"] for f in via_http["findings"]] == \
               [f["statement"] for f in direct["findings"]], name
        assert via_http["constraint_summary"] == direct["constraint_summary"], name


def test_fault_unjudged_present(client):
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    r = client.post("/api/plan/evaluate", json={"plan": plan, "place": False}).json()
    # unjudged is not passed: the could-not-judge list is present and matches the count
    assert isinstance(r["fault_unjudged"], list)
    assert len(r["fault_unjudged"]) == r["check"]["fault_summary"]["unjudged"]


def test_evaluate_places(client):
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    r = client.post("/api/plan/evaluate",
                    json={"plan": plan, "place": True, "candidates": 120}).json()
    p = r["placement"]
    assert p["footprint"]["bays"] >= 3
    assert len(p["rooms"]) > 10
    assert "relaxations" in p["geometry_report"]
    assert r["rooms_meta"]  # overlay metadata joined server-side


def test_compose_job_roundtrip(client):
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    job = client.post("/api/compose", json={"brief": brief, "candidates": 3}).json()
    import time
    for _ in range(120):
        j = client.get(f"/api/jobs/{job['job_id']}").json()
        if j["status"] in ("done", "error"):
            break
        time.sleep(0.5)
    assert j["status"] == "done"
    cands = j["result"]["candidates"]
    assert 1 <= len(cands) <= 3
    assert all("trades_away" in c and "why_this_diagram" in c for c in cands)
    plan = client.get(f"/api/jobs/{job['job_id']}/candidates/0/plan").json()
    assert plan["levels"]


def test_malformed_brief_fails_fast(client):
    r = client.post("/api/compose", json={"brief": {"style": "tidewater-georgian"}})
    assert r.status_code == 422  # target_area_sf missing → schema refusal, not a job
