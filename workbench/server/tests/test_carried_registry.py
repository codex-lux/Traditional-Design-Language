"""THE AUDIT OF PHASE 17 (30 Oct 2026), BLOCKING: A FORGED PLACEMENT WAS CARRIED.

`geometry.declared_digest` binds the DECLARED half only and is an unkeyed hash any client can
compute, so every key a placement wrote was the posting client's word. Deleting
`footprint.bay_module_ft` on a refused house (bad-04, bad-05, good-05, placed on the search) made
bearing read UNJUDGED, which never refuses: `POST /api/drawings/plan` answered 422 honestly and 200
with an svg forged. A forged `geometry_report.infeasible` printed "CP-SAT proved ..." with the
client's own lines.

The server now carries only a placement it produced itself (`corpus.remember_placement`, a bounded
registry of whole-record digests); anything else is re-solved. These tests hold that through the
reader (`corpus.carried`), through the route, and through the registry's own bounds -- and the
Drawing Set's separate calls draw one house (`corpus._placed`'s recent placements).
"""
import copy
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REFUSED_ON_THE_SEARCH = ("bad-04", "bad-05", "good-05")


def _geo():
    from mcp_server import core
    return core._mod("geometry", os.path.join(ROOT, "build", "geometry.py"))


def _ref_plan(prefix):
    d = os.path.join(ROOT, "plans", "reference")
    name = next(f for f in sorted(os.listdir(d)) if f.startswith(prefix))
    return json.load(open(os.path.join(d, name)))


def _server_placed(monkeypatch, prefix):
    from workbench.server import corpus
    geo = _geo()
    monkeypatch.setattr(geo, "_SOLVE_CACHE", {})
    out = geo.solve(copy.deepcopy(_ref_plan(prefix)), engine="heuristic")
    assert "error" not in out
    assert out["geometry_report"].get("refused"), f"the premise: {prefix} is refused on the search"
    corpus.remember_placement(out)
    return geo, out


def _stub_solve(monkeypatch, geo):
    calls = []

    def stub(*a, **kw):
        calls.append(kw.get("engine"))
        return {"error": "stub: this test asks whether a solve was called, not what it returns"}
    monkeypatch.setattr(geo, "solve", stub)
    return calls


def _forgeries(out):
    no_module = copy.deepcopy(out)
    no_module["footprint"].pop("bay_module_ft", None)
    no_fp = copy.deepcopy(out)
    no_fp.pop("footprint")
    proof = copy.deepcopy(out)
    proof["geometry_report"]["infeasible"] = {"proven": True,
                                              "conflicts": [{"about": "FORGED BY THE CLIENT"}]}
    return {"bay module deleted": no_module, "footprint deleted": no_fp,
            "proof of infeasibility forged": proof}


@pytest.mark.parametrize("prefix", REFUSED_ON_THE_SEARCH)
def test_a_forged_placement_is_not_carried_and_the_route_does_not_draw_it(client, monkeypatch, prefix):
    """The audit's reproduction, through the route. The server's own placement of a refused house
    is carried and answered 422 without a solve; every forgery of it is NOT carried and is placed
    afresh (stubbed here: the question is whether the posted rectangles are drawn, never what a
    solve returns), so no forged record reaches a 200 svg.
    Mutation: `carried()` without the `is_registered` test -- every forgery is carried, red."""
    from workbench.server import corpus
    geo, out = _server_placed(monkeypatch, prefix)
    corpus.forget_recent_placements()
    calls = _stub_solve(monkeypatch, geo)
    r = client.post("/api/drawings/plan", json={"plan": copy.deepcopy(out)})
    assert r.status_code == 422 and calls == [], (r.status_code, calls)
    for name, forged in _forgeries(out).items():
        assert geo.carries_its_own_placement(forged), f"the premise ({name}): the declared digest still matches"
        assert corpus.carried(forged)["state"] == corpus.NOT_CARRIED, name
        calls.clear()
        r = client.post("/api/drawings/plan", json={"plan": forged})
        assert calls == ["auto"], f"{name}: the forged record was not re-solved ({calls})"
        assert r.status_code != 200, f"{name}: a forged placement was drawn"
        assert "FORGED BY THE CLIENT" not in r.text, name


def test_the_registry_reads_the_whole_record_except_the_solver_block(monkeypatch):
    """A placement key edited by a client is a different record; the solver block is not part of the
    digest, because `carried()` and `_placed` rewrite it on the server's own records."""
    from workbench.server import corpus
    geo, out = _server_placed(monkeypatch, "bad-04")
    assert corpus.is_registered(out)
    for name, forged in _forgeries(out).items():
        assert not corpus.is_registered(forged), name
    moved = copy.deepcopy(out)
    g = next(r["geometry"] for lv in moved["levels"] for r in lv["rooms"] if r.get("geometry"))
    g["x_ft"] += 1.0
    assert not corpus.is_registered(moved), "a moved rectangle is not the server's placement"
    sv = copy.deepcopy(out)
    sv["geometry_report"]["solver"]["engine"] = "anything"
    assert corpus.is_registered(sv), "the solver block is the server's to rewrite and is not hashed"
    back = json.loads(json.dumps(out), parse_float=lambda s: int(float(s)) if float(s).is_integer() else float(s))
    assert corpus.is_registered(back), "the browser's round trip is not an edit"


def test_a_restart_empties_the_registry_and_the_record_is_re_solved(monkeypatch):
    from workbench.server import corpus
    geo, out = _server_placed(monkeypatch, "bad-04")
    assert corpus.carried(copy.deepcopy(out))["state"] == corpus.CARRIED
    corpus.forget_placements()
    assert corpus.carried(copy.deepcopy(out))["state"] == corpus.NOT_CARRIED, \
        "a placement produced before the restart is re-solved, the safe direction"


def test_the_registry_is_bounded(monkeypatch):
    from workbench.server import corpus
    monkeypatch.setattr(corpus, "REGISTRY_MAX", 3)
    corpus.forget_placements()
    recs = []
    for i in range(5):
        rec = {"id": f"r{i}", "levels": [{"rooms": [{"id": "a", "geometry": {"x_ft": i}}]}]}
        corpus.remember_placement(rec)
        recs.append(rec)
    assert len(corpus._REGISTRY) == 3
    assert not corpus.is_registered(recs[0]) and corpus.is_registered(recs[4])
    assert corpus.remember_placement({"id": "x", "levels": [{"rooms": [{"id": "a"}]}]}) is None, \
        "a record with no placement is not registered"


def test_carried_returns_a_registered_record(monkeypatch):
    """The record `carried()` returns has a re-derived tally and the server's own solver block, and is
    what a client posts back next: it is registered in turn, so the second open is carried too."""
    from workbench.server import corpus
    geo, out = _server_placed(monkeypatch, "bad-04")
    got = corpus.carried(copy.deepcopy(out))
    assert got["state"] == corpus.CARRIED
    corpus.forget_placements()
    corpus.remember_placement(out)
    rec = corpus.carried(copy.deepcopy(out))["record"]
    assert corpus.is_registered(rec)
    assert corpus.carried(copy.deepcopy(rec))["state"] == corpus.CARRIED


def test_the_drawing_sets_separate_calls_draw_one_house(monkeypatch):
    """The prover's audit: an UNKNOWN CP answer is no longer cached, so the scene and then the
    section and the bearing plate (each through `_placed`) re-solved the declared record and, under
    load, drew different houses under one input digest. The last placement `_placed` made of a
    declared record is handed to the next call.
    Mutation: skip `_recent_get` -- the second call solves again and draws another house, red."""
    from workbench.server import corpus
    from . import drawable
    geo = _geo()
    plan = drawable.drawable_plan()      # BEFORE the patch: finding it places records itself
    corpus.forget_recent_placements()
    real = geo.solve
    calls, n = [], {"i": 0}

    def varying(plan, *a, **kw):
        # a solver whose answer differs call to call, as the prover's does under load
        calls.append(kw.get("engine"))
        out = real(copy.deepcopy(plan), engine="heuristic")
        n["i"] += 1
        for lv in out["levels"]:
            for r in lv["rooms"]:
                if r.get("geometry"):
                    r["geometry"]["x_ft"] = round(r["geometry"]["x_ft"] + 0.001 * n["i"], 4)
        return out
    monkeypatch.setattr(geo, "solve", varying)
    a = corpus._placed(copy.deepcopy(plan), None, 250)
    b = corpus._placed(copy.deepcopy(plan), None, 250)
    assert "error" not in a and "error" not in b
    assert len(calls) == 1, f"the second sheet re-solved ({calls})"
    rects = lambda rec: [r.get("geometry") for lv in rec["levels"] for r in lv["rooms"]]  # noqa: E731
    assert rects(a) == rects(b), "two sheets of one set drew two houses"
    assert corpus.is_registered(b)
    other = corpus._placed(copy.deepcopy(plan), None, 60)
    assert len(calls) == 2 and "error" not in other, "a different width is a different request"
    corpus.forget_recent_placements()
    corpus._placed(copy.deepcopy(plan), None, 250)
    assert len(calls) == 3


def test_the_recent_placements_expire(monkeypatch):
    from workbench.server import corpus
    corpus.forget_recent_placements()
    corpus._recent_put(("k", None, 1), {"id": "x"})
    assert corpus._recent_get(("k", None, 1)) == {"id": "x"}
    monkeypatch.setattr(corpus, "RECENT_TTL_S", -1.0)
    assert corpus._recent_get(("k", None, 1)) is None


def test_a_compose_jobs_candidates_are_registered_before_a_reader_can_fetch_them(monkeypatch):
    """The compose job is where a candidate's placement comes from; registered in `jobs._run`, as
    the result is stored, and again as `candidate_plan` serves it.
    Mutation: drop `_remember_plans(result)` from the compose branch of `_run` -- red."""
    from workbench.server import corpus, jobs
    geo, out = _server_placed(monkeypatch, "bad-04")
    corpus.forget_placements()

    class StubComposer:
        @staticmethod
        def considered(brief, n):
            return ["p"]

        @staticmethod
        def compose(brief, n):
            return {"candidates": [{"parti": "p", "plan": copy.deepcopy(out)}]}
    monkeypatch.setattr(jobs.core, "_composer", lambda: StubComposer)
    job = jobs.Job({"style": "x"}, 1)
    with jobs._JOBS_LOCK:
        jobs._JOBS[job.id] = job
    try:
        jobs._run(job)
        assert job.status == "done", job.error
        assert corpus.is_registered(job.result["candidates"][0]["plan"]), \
            "a composed candidate is not one the server would carry"
        corpus.forget_placements()
        served = jobs.candidate_plan(job.id, 0)
        assert corpus.is_registered(served), "serving a candidate registers it again"
    finally:
        with jobs._JOBS_LOCK:
            jobs._JOBS.pop(job.id, None)


def test_the_critique_route_reuses_only_the_servers_own_placement(client, monkeypatch):
    """`/api/plan/critique` passes `trusted_placement=corpus.is_registered(plan)`; MCP callers pass
    nothing and are never trusted. Mutation: pass `trusted_placement=True` from the route -- red."""
    from workbench.server import corpus
    geo, out = _server_placed(monkeypatch, "bad-04")
    r = client.post("/api/plan/critique", json={"plan": copy.deepcopy(out), "engine": "heuristic"})
    assert r.status_code == 200, r.text[:300]
    assert r.json()["placement"]["reused"] is True and r.json()["engine"]["ran"] == "carried"
    forged = copy.deepcopy(out)
    forged["footprint"].pop("bay_module_ft", None)
    r = client.post("/api/plan/critique", json={"plan": forged, "engine": "heuristic"})
    assert r.status_code == 200, r.text[:300]
    assert r.json()["placement"]["reused"] is False, "a forged placement was reused by the critique"
    from mcp_server import core
    res = core.critique_plan(copy.deepcopy(out), engine="heuristic")
    assert res["placement"]["reused"] is False, "an MCP caller's placement is never trusted"


def test_a_carried_placement_names_the_parti_the_record_carries_not_the_one_asked_for(monkeypatch):
    """`_placed`'s carried branch wrote `drawn_by.parti` as the REQUESTED parti, which need not be
    the diagram that placed the house. Mutation: write the requested parti again -- red."""
    from workbench.server import corpus
    geo, out = _server_placed(monkeypatch, "bad-04")
    # bad-04 is refused, so `_placed` hands back the refusal and not the record: the record the
    # carried branch stamped is read off `carried` as it leaves
    seen = {}
    real_carried = corpus.carried

    def spy(plan):
        res = real_carried(plan)
        seen["rec"] = res.get("record")
        return res
    monkeypatch.setattr(corpus, "carried", spy)
    corpus._placed(copy.deepcopy(out), "centre-passage-double-pile", 250)
    db = seen["rec"]["geometry_report"]["solver"]["drawn_by"]
    assert db["engine_requested"] == "carried"
    assert db["parti"] == out.get("parti"), f"drawn_by names {db['parti']!r}, the parti asked for"


def test_a_job_followed_only_by_its_stream_is_touched_on_open_and_on_each_heartbeat(monkeypatch):
    """The tests auditor (30 Oct 2026). `events()` -- the path the app reads (EventSource) -- touches
    the job as the stream opens and on every heartbeat, so a queued job whose reader only watches
    the stream is not reaped (finding 29). Neither touch was guarded.
    Mutations: replace the open's `_touch(job_id)` with `_JOBS.get(job_id)` -- red; drop the
    heartbeat's `job.touched = time.time()` -- red."""
    import asyncio
    from workbench.server import jobs
    monkeypatch.setattr(jobs, "_POLL_S", 0.001)
    job = jobs.Job({"style": "x"}, 1)
    with jobs._JOBS_LOCK:
        jobs._JOBS[job.id] = job
    try:
        job.touched = 0.0
        jobs._put(job, "stage", {"stage": "queued"})

        async def drive():
            agen = jobs.events(job.id)
            first = await agen.__anext__()               # the stage event: no heartbeat yet
            assert "stage" in first
            opened = job.touched
            job.touched = 0.0
            beat = await asyncio.wait_for(agen.__anext__(), timeout=10)
            await agen.aclose()
            return opened, beat
        opened, beat = asyncio.run(drive())
        assert opened > 0.0, "opening the stream did not touch the job"
        assert beat.startswith(": heartbeat"), beat
        assert job.touched > 0.0, "a heartbeat did not touch the job"
    finally:
        with jobs._JOBS_LOCK:
            jobs._JOBS.pop(job.id, None)


def test_the_jobs_table_is_mutated_and_iterated_under_one_lock():
    """`_reap` iterated `_JOBS` while a concurrent `submit` inserted into it; both are under
    `_JOBS_LOCK` now. A thread holding the lock blocks a reap until it lets go.
    Mutation: drop the lock from `_reap` -- red."""
    import threading
    from workbench.server import jobs
    done = threading.Event()
    with jobs._JOBS_LOCK:
        t = threading.Thread(target=lambda: (jobs._reap(), done.set()))
        t.start()
        assert not done.wait(0.3), "a reap ran while another thread held the jobs lock"
    assert done.wait(5), "the reap never ran once the lock was free"
    t.join()


def test_evaluate_registers_the_placement_it_produced(monkeypatch):
    """Mutation: drop `corpus.remember_placement(solved)` after the solve in `evaluate` -- red."""
    from workbench.server import corpus, evaluate
    from . import drawable
    plan = drawable.drawable_plan()
    seen = []
    real = corpus.remember_placement
    monkeypatch.setattr(corpus, "remember_placement", lambda rec: seen.append(rec) or real(rec))
    evaluate.evaluate(copy.deepcopy(plan), place=True, engine="heuristic")
    assert any(any(rm.get("geometry") for lv in r.get("levels") or [] for rm in lv["rooms"])
               for r in seen), "the placement the bench solved is not registered"
