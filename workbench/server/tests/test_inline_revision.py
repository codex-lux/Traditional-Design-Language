"""WP-13.9 -- the corrective rounds run before the plan is surfaced.

Lucas read the bench's Tidewater sheet on 19 Sep 2026: sixty drawn findings, most of them the
`unreachable` fatal, beside a revision panel reporting nothing applied. Solving ran exactly one
`POST /api/plan/evaluate` and the loop was reached only by two chips submitting a job -- whose
record comes back stripped and is re-solved, so the sheet and the loop's key were two different
placements. The ruling: the explicit solve runs one or two rounds, on the engine that placed,
and returns the record the loop ended on with ITS OWN placement and findings.

Each test is named for the defect it forbids. The engine is asked for BY NAME throughout: the
proof path costs a 25 s solve per round and these are route tests, not a measurement of CP.
"""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _plan(pid="tidewater-georgian-careful"):
    return json.load(open(os.path.join(ROOT, "plans", f"{pid}.json"), encoding="utf-8"))


def _report(out):
    """The loop's account of itself, where the response carries it: ON THE RECORD. It used to
    ride twice -- the same 147,583 bytes as `out["revision"]` and again inside
    `revised_plan.revision_report`, 24.3% of a 606 KB response -- and the bench only ever read
    the second. One copy, read through one helper so a test cannot quietly start reading the
    other."""
    return out["revised_plan"]["revision_report"]


def _ev(client, **body):
    r = client.post("/api/plan/evaluate", json={"plan": _plan(), "engine": "heuristic", **body})
    assert r.status_code == 200, r.text
    return r.json()


def test_the_default_is_no_rounds_and_the_response_is_what_it_always_was(client):
    """The route's default is 0 and every caller that does not ask -- the CLI parity test, the
    wall drag, a script -- must be byte-identical to before this package. A revision that
    happened by default would be WP-9.3's refused per-edit critique arriving through a
    different door."""
    out = _ev(client)
    assert "revision" not in out
    assert "revised_plan" not in out
    assert "revise" not in out["timing_ms"]


def test_an_explicit_solve_runs_the_rounds_and_says_what_they_did(client):
    out = _ev(client, revise_rounds=2)
    assert "revised_plan" in out, out.keys()
    rep = _report(out)
    s = rep["summary"]
    assert s["rounds"] >= 1
    assert rep["surfaced"] == "with-its-own-placement"
    assert out["timing_ms"]["revise"] >= 0
    # the package's own subject: this plan's stranded rooms are answerable, so the rounds must
    # actually apply something. A loop that ran and did nothing is the state Lucas reported.
    assert s["moves_applied"] >= 1, rep["stop_reason"]
    # AND IT MUST BE THE MOVE THIS PACKAGE MADE REACHABLE (the adversarial audit of WP-13.9).
    # Restoring the pre-package `return engine != "cp-sat"` in `critique._is_placement` -- the
    # defect the report says four files denied in prose for eleven days -- left every test in
    # this file GREEN: `add-the-grammar-door` went 6 applications to ZERO, `moves_applied`
    # survived on six unrelated `widen-for-furniture` moves, and the fatal count still fell,
    # by one, on an incidental `light-the-far-end`. A route test that asserts a loop ran is
    # not a test that the loop does the thing the route exists for.
    applied = [m["move"] for rd in rep["rounds"]
               for m in rd.get("moves", []) if m.get("accepted")]
    assert "add-the-grammar-door" in applied, applied


def test_the_findings_are_of_the_record_the_loop_ended_on(client):
    """ONE BUILDING (WP-6.4). The whole reason this is inline rather than the job route: the
    fatal count on the response must be the revised record's, not the first pass's."""
    plain = _ev(client)
    revised = _ev(client, revise_rounds=2)
    assert revised["check"]["counts"].get("fatal", 0) < plain["check"]["counts"].get("fatal", 0)
    key_before = _report(revised)["summary"]["key_before"]
    key_after = _report(revised)["summary"]["key_after"]
    assert key_after[0] == revised["check"]["counts"].get("fatal", 0), (key_after, revised["check"]["counts"])
    assert key_before[0] == plain["check"]["counts"].get("fatal", 0)


def test_the_revised_record_comes_back_declared_and_carrying_its_report(client):
    """Stripped exactly as `jobs.revised_plan` strips it: a placement travels on `placement`,
    and two copies of one placement on one response is how two readers of one house come to
    disagree. `revision_report` survives the strip -- it IS the panel."""
    out = _ev(client, revise_rounds=2)
    rec = out["revised_plan"]
    assert "revision_report" in rec
    assert not any("geometry" in rm for lv in rec["levels"] for rm in lv["rooms"]), \
        "the revised record carried a second copy of the placement"
    assert "geometry_report" not in rec


def test_the_drawn_findings_name_the_engine_that_placed_the_revised_record(client):
    """A drawn row's engine tag is what the bench prints as 'on the searched placement'. After
    the rounds it must name the engine of the placement those findings were judged against."""
    out = _ev(client, revise_rounds=2)
    drawn = [f for f in out["check"]["findings"] if f["layer"] == "drawn"]
    assert drawn, "premise: this plan draws findings"
    assert {f.get("engine") for f in drawn} == {"heuristic"}


def test_the_interactive_path_may_not_buy_the_job_routes_budget():
    """WP-13.9's OWN ADVERSARIAL AUDIT. The first version bounded this route by
    `core.REVISE_MAX_ROUNDS` (8) and `core.REVISE_MAX_BUDGET_S` (600) -- the JOB route's
    numbers, for a queued worker nobody waits on. The loop tests its budget at the TOP of a
    round, so the true ceiling is budget plus one round, and a CP round costs about 35 s:
    one request could ask for roughly ELEVEN MINUTES of one core on the path a browser waits
    on, and the rate limiter's 60 calls an hour then buys about eleven hours of CPU per wall
    hour from one caller. The job route has a one-worker pool, a bounded queue and a 503; this
    has none of them, so it gets the interactive ceilings instead."""
    from mcp_server import core
    from workbench.server import app as A, evaluate as EV
    assert EV.INLINE_MAX_ROUNDS < core.REVISE_MAX_ROUNDS
    assert EV.inline_budget_ceiling() < core.REVISE_MAX_BUDGET_S
    assert A._revise_rounds({"revise_rounds": 8}) == EV.INLINE_MAX_ROUNDS
    assert A._revise_budget({"revise_budget_s": 600}) == EV.inline_budget_ceiling()
    # a caller may LOWER it
    assert A._revise_budget({"revise_budget_s": 5}) == 5.0


def test_the_ceiling_is_enforced_by_the_module_and_not_only_by_the_route(monkeypatch):
    """A ceiling a route owns is a ceiling another route can forget. `evaluate()` is reachable
    from a test, a script and any future route, so it clamps again -- driven by calling it
    with values past the ceiling and reading what the loop was actually asked for."""
    from workbench.server import evaluate as EV
    seen = {}

    def spy(plan, **kw):
        seen.update(kw)
        return {"report": {"summary": {"rounds": 0}}, "plan": plan}

    monkeypatch.setattr(EV.core, "revise_plan", spy)
    EV._revise_inline({"geometry_report": {"solver": {"engine": "heuristic"}}},
                      None, 99999, 99, 99999.0)
    assert seen["rounds"] == EV.INLINE_MAX_ROUNDS
    assert seen["candidates"] == EV.INLINE_MAX_CANDIDATES
    assert seen["budget_s"] == EV.inline_budget_ceiling()


def test_only_so_many_revising_solves_run_at_once_and_the_rest_are_declined_by_name(monkeypatch):
    """This endpoint is a sync `def`, so Starlette runs it in the anyio threadpool -- 40 tokens
    for the WHOLE application, `/api/health` included. Forty concurrent revising evaluates would
    hold every one of them and the platform healthcheck would queue behind an 11-minute loop,
    which reads as a dead container. A caller past the cap gets its SHEET with the rounds
    declined BY NAME: never a silent skip, which reads as a loop that found nothing to do."""
    from workbench.server import evaluate as EV
    held = []
    for _ in range(EV.INLINE_CONCURRENCY):
        assert EV._INLINE_SLOTS.acquire(blocking=False)
        held.append(True)
    try:
        rec, rev = EV._revise_inline({"geometry_report": {"solver": {"engine": "heuristic"}}},
                                     None, 250, 2, None)
        assert "declined" in rev, rev
        assert "revising solves" in rev["declined"]
        out = {}
        EV._attach_revision(out, rec, rev)
        assert out["revision_skipped"] == rev["declined"]
        assert "revision" not in out and "revised_plan" not in out
    finally:
        for _ in held:
            EV._INLINE_SLOTS.release()


def test_the_rounds_reader_bounds_and_refuses_what_it_cannot_read():
    """DRIVEN ON THE READER, and the reason is a blind guard this package caught in its own
    mutation sweep. The first version of this test posted `revise_rounds: 999` and asserted the
    report came back inside `core.REVISE_MAX_ROUNDS` -- which passes with the route's bound
    DELETED, because `core.revise_plan` bounds `rounds` itself before the loop ever runs. It
    was asserting the inner bound through the outer one, so it could not fail.

    What the route's own reader decides, and nothing else does: that 0 is expressible (a
    caller must be able to say "do not revise"), and that a value we cannot read means none
    rather than the default -- a caller who sent nonsense has not asked for a loop and must
    not be given minutes of one."""
    from workbench.server import app as A, evaluate as EV
    assert A._revise_rounds({}) == 0
    assert A._revise_rounds({"revise_rounds": 0}) == 0
    assert A._revise_rounds({"revise_rounds": 2}) == 2
    assert A._revise_rounds({"revise_rounds": 999}) == EV.INLINE_MAX_ROUNDS
    assert A._revise_rounds({"revise_rounds": -4}) == 0
    for bad in ("lots", None, [2], {}):
        assert A._revise_rounds({"revise_rounds": bad}) == 0, bad


def test_a_value_the_route_cannot_read_runs_no_rounds(client):
    """The behavioural half of the reader above, through the real route."""
    for bad in ("lots", None, [2]):
        assert "revision" not in _ev(client, revise_rounds=bad)


def test_the_budget_reader_bounds_and_defaults_to_the_interactive_ceiling():
    """`None` means `geometry.BUDGET_REVISE_INLINE_S` -- which is `_revise_inline`'s to
    supply, not the route's, so the reader must say None rather than reaching for a number
    and putting a second spelling of that ceiling in a second file."""
    from workbench.server import app as A, evaluate as EV
    assert A._revise_budget({}) is None
    assert A._revise_budget({"revise_budget_s": "nonsense"}) is None
    assert A._revise_budget({"revise_budget_s": 12}) == 12.0
    assert A._revise_budget({"revise_budget_s": 10 ** 6}) == EV.inline_budget_ceiling()
    assert A._revise_budget({"revise_budget_s": 0}) == 1.0


def test_a_loop_that_fails_still_returns_the_sheet(client, monkeypatch):
    """A loop that raises must not cost the reader the plan. Driven, because no shipped record
    reaches it -- and an untested except branch is a promise rather than a behaviour."""
    from workbench.server import evaluate as EV

    def boom(*_a, **_k):
        raise RuntimeError("the loop fell over")

    monkeypatch.setattr(EV.core, "revise_plan", boom)
    out = _ev(client, revise_rounds=2)
    assert "revision" not in out
    assert out["revision_error"].startswith("RuntimeError"), out["revision_error"]
    assert out["check"]["counts"], "the sheet must still land"
    assert "placement" in out or "placement_refused" in out


def test_the_wall_drags_own_path_is_untouched(client):
    """The drag asks for the hill-climb BY NAME behind a 400 ms debounce and sends no rounds.
    A gesture cannot wait for a loop any more than it can wait for a proof, and this asserts
    the route rather than the client's intention."""
    out = _ev(client)
    assert "revision" not in out and "revised_plan" not in out
    assert out["placement"]["sketch"]["working"] is True


def test_the_stranded_rooms_fall_through_the_route_and_not_only_in_the_loop(client):
    """The other half of the same guard, measured on the finding rather than on the move: the
    response the bench renders must carry FEWER `unreachable` fatals than the first pass. With
    the critic's pre-package reading restored this is 12 against 13 (one incidental clearance)
    rather than 6 against 13, so the two assertions bite on different margins."""
    def _stranded(out):
        return sum(1 for f in out["check"]["findings"] if f.get("kind") == "unreachable")
    plain, revised = _ev(client), _ev(client, revise_rounds=2)
    assert _stranded(plain) > 0, "premise: this record strands rooms on the search"
    assert _stranded(revised) < _stranded(plain), (_stranded(revised), _stranded(plain))


def test_the_inline_budget_is_this_modules_and_not_the_job_routes_default(monkeypatch):
    """THE CEILING THE PACKAGE DERIVES IS THE ONE THE LOOP GETS. `BUDGET_REVISE_INLINE_S`
    appeared in no assertion anywhere in the repository: dropping the default in
    `_revise_inline` (`budget_s=budget_s` alone) left 54 tests green, and `core.revise_plan`
    then applies its own `REVISE_DEFAULT_BUDGET_S` of 120 s -- quadrupling the ceiling on the
    one route a person waits on, which is exactly the "a ceiling that is not a ceiling is
    worse than none" defect `build/geometry.py` spends twenty-five lines deriving 30.0 to
    avoid. Read off the call rather than the clock, because the clock would pin the machine."""
    from workbench.server import evaluate as EV
    seen = {}

    def fake(plan, **kw):
        seen.update(kw)
        return {"plan": plan, "report": {"summary": {"rounds": 0, "moves_applied": 0},
                                         "rounds": [], "surfaced": kw.get("surfaced")}}

    monkeypatch.setattr(EV.core, "revise_plan", fake)
    ceiling = EV.inline_budget_ceiling()
    assert ceiling == 30.0, "the derived interactive ceiling moved; re-derive it, do not re-pin"

    EV.evaluate(_plan(), engine="heuristic", revise_rounds=2, candidates=8)
    assert seen["budget_s"] == ceiling, seen

    # and a caller asking for the JOB route's budget gets this module's ceiling, not theirs
    seen.clear()
    EV.evaluate(_plan(), engine="heuristic", revise_rounds=2, candidates=8, revise_budget_s=600.0)
    assert seen["budget_s"] == ceiling, seen

    # a caller asking for LESS keeps it: the ceiling is a maximum, never a floor
    seen.clear()
    EV.evaluate(_plan(), engine="heuristic", revise_rounds=2, candidates=8, revise_budget_s=5.0)
    assert seen["budget_s"] == 5.0, seen


def test_a_record_whose_schema_check_fails_still_carries_what_the_loop_did(client, monkeypatch):
    """WP-13.4's rule, one field over. The placement's own answer survives a schema error
    because the early return was moved BELOW `_attach_placement`; the revision has to survive
    it for the same reason, and moving `_attach_revision` under that early return left all ten
    tests in this file green. A reader told their record is malformed still deserves to know
    what the rounds did to it -- and on this route the revised record IS the one the error is
    about, so losing the panel loses the only account of why."""
    from workbench.server import evaluate as EV
    real = EV.core.check_plan
    monkeypatch.setattr(EV.core, "check_plan",
                        lambda p, **kw: {"error": "scripted: the placed record is malformed"})
    out = EV.evaluate(_plan(), engine="heuristic", revise_rounds=2, candidates=60)
    assert "error" in out["check"]
    assert "revised_plan" in out, out.keys()
    assert "revision_report" in out["revised_plan"]
    assert out["timing_ms"].get("revise") is not None
    monkeypatch.setattr(EV.core, "check_plan", real)


def test_the_overlays_read_the_record_the_findings_were_judged_against(monkeypatch):
    """`rooms_meta` feeds the sheet's analytic overlays and the Round's washes. The loop may
    drop an optional room, so reading the CALLER's unrevised document there puts the sheet's
    rooms and the sheet's washes one revision apart -- and reverting it to `plan` left 54
    tests green, because on the shipped corpus the loop does not change the room SET. Driven,
    for that reason: a room is removed by the scripted loop and the meta must follow it."""
    from workbench.server import evaluate as EV
    plan = _plan()
    gone = plan["levels"][0]["rooms"][-1]["id"]

    def fake(solved, parti, candidates, rounds, budget_s):
        trimmed = json.loads(json.dumps(solved))
        trimmed["levels"][0]["rooms"] = [r for r in trimmed["levels"][0]["rooms"] if r["id"] != gone]
        return trimmed, {"summary": {"rounds": 1, "moves_applied": 1}, "rounds": [],
                         "surfaced": "with-its-own-placement"}

    monkeypatch.setattr(EV, "_revise_inline", fake)
    out = EV.evaluate(plan, engine="heuristic", revise_rounds=2, candidates=8)
    meta = out["rooms_meta"]
    assert gone in EV.corpus.rooms_meta(plan), "premise: the room is in the unrevised record's meta"
    assert gone not in meta, "the overlays are one revision behind the sheet"


def test_the_report_rides_once_and_the_response_is_not_two_copies_of_it(client):
    """MEASURED on the shipped Tidewater record: the report is 147,583 bytes on a 606,771-byte
    response, and the first version of this package sent it TWICE -- as `out["revision"]` and
    again inside `revised_plan.revision_report` -- so a quarter of every revising solve was a
    copy the bench never read. `jobs.py` had already met this and says so in its own comment.
    Asserted by IDENTITY of content rather than by a byte budget, because a size ceiling would
    move with the corpus and this cannot: no other key of the response may serialise to the
    same thing as the report."""
    out = _ev(client, revise_rounds=2)
    rep = json.dumps(_report(out), sort_keys=True)
    assert len(rep) > 5000, "premise: the report is big enough for a second copy to matter"
    dup = [k for k, v in out.items()
           if k != "revised_plan" and json.dumps(v, sort_keys=True) == rep]
    assert not dup, f"the revision report is on the response twice, as {dup}"


def test_the_bench_does_not_re_upload_the_panel_it_was_handed():
    """The other end of the same measurement. `revision_report` is 91% of the revised record
    (147,583 of 162,651 bytes) and the bench re-POSTs its whole document on every debounced
    wall drag, so the panel went up the wire on every frame of a gesture -- to a route that
    does not read it. Asserted on the client's own source because there is no DOM here: the
    evaluate call strips it and the CAD export deliberately does NOT, since
    `build/export_dxf.py` turns it into the plate's `revision_summary` XDATA."""
    src = open(os.path.join(ROOT, "workbench", "app", "src", "api", "client.js"), encoding="utf-8").read()
    ev = [l for l in src.splitlines() if "'/api/plan/evaluate'" in l]
    assert ev and "withoutReport(plan)" in ev[0], ev
    cad = [l for l in src.splitlines() if "/api/export/" in l]
    assert cad and "withoutReport" not in cad[0], cad
    dxf = open(os.path.join(ROOT, "build", "export_dxf.py"), encoding="utf-8").read()
    assert 'meta.pop("revision_report"' in dxf, "the exporter stopped reading it; re-derive this rule"
