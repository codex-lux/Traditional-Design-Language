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


def test_evaluate_parity_on_the_placed_record(client):
    """WP-9.1. With `place` on, the bench judges the SOLVED record -- the drawn layer runs and
    the elevation is of this placement -- and the findings it shows are exactly what
    plan_check says of that same record. The heuristic at seed 7 is deterministic and
    _SOLVE_CACHE keys on the record, so the two solves are one."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import core
    import modcache
    geo = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
    for name in PLANS:
        plan = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
        r = client.post("/api/plan/evaluate",
                        json={"plan": plan, "place": True, "engine": "heuristic"}).json()
        via_http = r["check"]
        solved = geo.solve(core.copy_json(plan), None, 250, engine="heuristic")
        direct = core.check_plan(solved)
        assert via_http["counts"] == direct["counts"], name
        assert [f["id"] for f in via_http["findings"]] == [f["id"] for f in direct["findings"]], name
        # the drawn layer RAN -- reverting evaluate to check the declared record fails here
        assert via_http["drawn_summary"]["evaluated"] is True, name
        assert via_http["elevation_summary"]["basis"] == "placement", name
        drawn = [f for f in via_http["findings"] if f["layer"] == "drawn"]
        assert drawn and all(f.get("engine") == "heuristic" for f in drawn), name
        # and the payload the sheet draws is the same building the findings judged
        assert r["placement"]["footprint"] == solved["footprint"], name


def test_fault_unjudged_present(client):
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    r = client.post("/api/plan/evaluate", json={"plan": plan, "place": False}).json()
    # unjudged is not passed: the could-not-judge list is present and matches the count
    assert isinstance(r["fault_unjudged"], list)
    assert len(r["fault_unjudged"]) == r["check"]["fault_summary"]["unjudged"]


def test_evaluate_places(client):
    """The route places, and the payload it returns is the one the sheet draws.

    WP-13.4 SPLIT THIS IN TWO AND THE SECOND HALF IS THE NEW ONE. It used to post the Tidewater
    record and read `r["placement"]`; under the 15 Sep ruling that record is refused, so the
    route answers 200 with `placement_refused` and NO placement, and asserting the old shape
    would have been asserting that the ruling had not landed. This half takes a record the
    ruling still lets a surface draw; `test_a_refused_record_gets_the_conflict_set_and_no_
    placement` below is the other half, and the two are kept apart because a suite where both
    could be satisfied by one response is a suite that has stopped distinguishing them.

    `len(p["rooms"]) > 10` went with the Tidewater record: it was a statement about a twelve-room
    house, not about the route. What the route owes is that every room in the payload is a
    PLACED room -- the payload is projected off rooms carrying geometry -- and that is asserted
    on any record."""
    from . import drawable
    plan = drawable.drawable_plan()
    r = client.post("/api/plan/evaluate",
                    json={"plan": plan, "place": True, "candidates": 120}).json()
    assert "placement_refused" not in r, r.get("placement_refused")
    p = r["placement"]
    assert p["footprint"]["bays"] >= 3
    assert p["rooms"] and all(rm.get("geometry") for rm in p["rooms"]), (
        "the payload carries a room with no rectangle: it is projected off placed rooms")
    assert "relaxations" in p["geometry_report"]
    assert r["rooms_meta"]  # overlay metadata joined server-side


def test_a_refused_record_gets_the_conflict_set_and_no_placement(client):
    """The ruling at this route: 200, `placement_refused`, and NOTHING to draw (WP-13.4).

    The bench draws the conflict set instead of a house, so the response must carry the reason
    and must NOT carry a placement -- a response with both would let a surface draw the refused
    placement while displaying the refusal beside it, which is the one outcome the ruling
    forbids. Driven off a shipped record the corpus refuses; the file skips rather than passing
    if the ruling ever stops refusing anything, because then this test is about nothing."""
    import pytest
    for name in PLANS:
        plan = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
        r = client.post("/api/plan/evaluate",
                        json={"plan": plan, "place": True, "candidates": 60}).json()
        if "placement_refused" not in r:
            continue
        ref = r["placement_refused"]
        assert "placement" not in r, (
            f"{name}: the route returned a refusal AND a placement -- a surface handed both "
            f"will draw the placement")
        assert ref["kind"] in ("infeasible", "type-fact-downgraded"), ref["kind"]
        assert ref["lines"] and all(isinstance(x, str) and x for x in ref["lines"]), (
            "a refusal is content: it names what could not hold, never a bare error")
        assert ref["facts"] or ref["kind"] == "infeasible"
        return
    pytest.skip("COULD NOT EVALUATE: neither shipped plan is refused on this tree, so there "
                "is no refusal for this test to be about")


def test_the_wall_drag_still_gets_a_working_sketch(client):
    """The ruling's one exemption, and it is named by ENGINE (WP-13.4).

    `PlanWorkbench.jsx` asks for the heuristic BY NAME on the drag path only. A drag that
    cannot see the rectangle it is dragging is not a drag, so that path still returns a
    placement -- marked `sketch`, carrying the refusal inside it, and refused by every export.
    `sketch` is written on EVERY heuristic evaluate and not only on a refused one, so a client
    cannot read its absence as a proof."""
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    r = client.post("/api/plan/evaluate",
                    json={"plan": plan, "place": True, "engine": "heuristic",
                          "candidates": 60}).json()
    assert "placement" in r, "the wall drag lost its sketch"
    sk = r["placement"].get("sketch")
    assert sk and sk["working"] is True and sk["reason"], (
        "a heuristic placement that does not say it is a working sketch is one a surface will "
        "print as a finished drawing")
    # and the SAME record on the default engine is refused with no placement, which is what
    # makes the exemption an exemption rather than the rule
    auto = client.post("/api/plan/evaluate",
                       json={"plan": plan, "place": True, "candidates": 60}).json()
    if "placement_refused" in auto:
        assert sk["refused"], (
            "the record is refused on the default engine and the drag's sketch says nothing "
            "about it -- the marking has to carry the reason or it is decoration")


def test_compose_job_roundtrip(client):
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    # The revision loop is on by default (WP-9.2) and on `auto` it asks CP-SAT for a proof
    # per candidate, ~25 s a solve; this is a round-trip test of the job plumbing, so it asks
    # for the bounded loop the corpus job runs and still checks the loop reported itself.
    job = client.post("/api/compose", json={"brief": brief, "candidates": 3,
                                            "revise_engine": "heuristic", "revise_rounds": 1}).json()
    import time
    for _ in range(240):
        j = client.get(f"/api/jobs/{job['job_id']}").json()
        if j["status"] in ("done", "error"):
            break
        time.sleep(0.5)
    assert j["status"] == "done"
    cands = j["result"]["candidates"]
    assert 1 <= len(cands) <= 3
    assert all("trades_away" in c and "why_this_diagram" in c for c in cands)
    # every returned candidate carries the loop's account of itself, and the pre-revision
    # score beside the post-revision one (the same instrument, twice)
    assert all("revision" in c and "score_before" in c for c in cands)
    plan = client.get(f"/api/jobs/{job['job_id']}/candidates/0/plan").json()
    assert plan["levels"]
    assert plan["revision_report"]["mode"] == "placed"


def test_malformed_brief_fails_fast(client):
    r = client.post("/api/compose", json={"brief": {"style": "tidewater-georgian"}})
    assert r.status_code == 422  # target_area_sf missing → schema refusal, not a job
