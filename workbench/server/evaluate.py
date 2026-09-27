"""POST /api/plan/evaluate — the Plan Workbench's one round-trip.

The client owns the plan record and sends the whole document per edit gesture.
The validator reads the record's *declared* fields, so a wall drag must already
have been written back to width_ft/length_ft before this is called.

WP-6.2 CHANGED THE SECOND HALF OF THIS PARAGRAPH, and the old text is kept here
because it was a stated position rather than an accident. It read: "placement is
solved separately and returned beside the findings, never fed into them
(plan_check does not read geometry output — a settled fact, not an oversight)."
That was OQ 54's ruling, and Lucas reopened it: while it held, the critic scored
the house the record DECLARED and the sheet drew the house the solver PLACED, so
a landing that misses its own stair, a kitchen drawn at 63% of its declared area,
and a bathroom no door reaches each produced no finding at all.

`plan_check` now carries a `drawn` layer — and ONLY that layer — which reads
placement. Every other layer stays geometry-blind, so a record nobody has placed
is still judged on what it declares and the drawn layer reports COULD NOT
EVALUATE rather than passing. That distinction is the whole of the change.
"""
import os
import threading
import time

from . import corpus

core = corpus.core


def evaluate(plan, strict=False, place=True, parti=None, candidates=250,
             engine="auto", revise_rounds=0, revise_budget_s=None):
    # WP-6.3 flipped this from "heuristic" to "auto" (CP-SAT where it can answer, the
    # hill-climb where it cannot, with the reason named in geometry_report.solver either
    # way). The old default was chosen for latency — this endpoint runs on a 400 ms
    # debounce behind every wall drag and a proof takes seconds — and the cost of it was
    # not visible until the openings became placeable and countable.
    #
    # MEASURED on plans/tidewater-georgian-careful.json, three runs each, deterministic:
    #   heuristic  20 openings placed, 11 unplaced, 3 rooms stranded (fatal), kitchen
    #              reachable only from outdoors
    #   auto/CP    30 openings placed,  1 unplaced (a door to a room the record puts on
    #              no level), 0 stranded, 0 fatal
    # The sheet a reader was looking at came from the weaker engine, and every access
    # defect they reported was an artefact of that. Latency is the right thing to spend
    # here and the wrong thing to spend it on was correctness.
    #
    # A caller that wants the fast path still asks for it BY NAME: the bench passes
    # engine="heuristic" on the drag path only, and every other way the record can change
    # takes this default. There is deliberately no settle-timer re-proof behind the drag —
    # it was tried and was worse, because a second render landing mid-gesture replaces the
    # handle element under the pointer and the drag dies. The next change to the record
    # gets the proof.
    # ONE BUILDING, JUDGED AND DRAWN (WP-9.1). Until Phase 9 this checked the DECLARED record
    # and then placed it separately, returning the placement beside findings that had never
    # seen it -- so the drawn layer (WP-6.2's whole point) reported "could not evaluate" on
    # every bench evaluate, and the word "drawn" appeared nowhere in the app. The record is
    # solved first now, the solved record is what plan_check judges (its drawn layer runs,
    # and its elevation is derived from THIS placement rather than a fresh heuristic one), and
    # `placement` is projected off the same object the sheet then draws. On a solver error the
    # declared record is judged as before and `placement_error` says why.
    t0 = time.perf_counter()
    # ALL THREE BOUND BEFORE THE BRANCH. `placement_error` was assigned only inside `if place:`
    # and read only inside it, which held until WP-13.4 lifted the three outcomes into one
    # function called from both return paths -- `place=False` then raised UnboundLocalError on
    # every evaluate that does not place, which is what `/api/plan/evaluate` does for the
    # declared-record checks. Caught by the suite and not by the package's own smoke run, which
    # exercised `place=True` only.
    solved = None
    refused = None
    placement_error = None
    if place:
        geo = core._mod("geometry", os.path.join(core.ROOT, "build", "geometry.py"))
        pt = core.load_parti(parti)
        # WP-11.8: the INTERACTIVE budget by name. This route is the one the infrastructure
        # audit measured as the whole server's bound, and a person is waiting on it behind a
        # 400 ms debounce -- so it does not take the batch default `solve()` now carries.
        cand = geo.solve(core.copy_json(plan), pt, candidates, engine=engine,
                         time_limit_s=geo.BUDGET_INTERACTIVE_S)
        if "error" in cand:
            placement_error = cand["error"]
        else:
            solved, placement_error = cand, None
            # THE VERDICT, READ OFF THE RECORD (WP-13.4). `geometry._disclose` wrote it
            # through `typefacts.judge`; nothing here re-derives "may this be drawn".
            refused = (cand.get("geometry_report") or {}).get("refused")
    t_place = time.perf_counter()
    # THE CORRECTIVE ROUNDS, BEFORE THE PLAN IS SURFACED (WP-13.9, ruled 19 Sep 2026).
    # See `_revise_inline` below for what this is and what it deliberately is not.
    revision = None
    if place and solved is not None and revise_rounds > 0:
        solved, revision = _revise_inline(solved, parti, candidates,
                                          revise_rounds, revise_budget_s)
        refused = (solved.get("geometry_report") or {}).get("refused")
    t_revise = time.perf_counter()
    check = core.check_plan(solved if solved is not None else plan, strict=strict)
    t1 = time.perf_counter()
    # THE EVALUATION NAMES ITS PLAN, AT THE TOP AND BEFORE THE EARLY RETURN BELOW (WP-14.20).
    # `plan_check` writes the id only on a COMPLETED check; `core.check_plan`'s two error payloads
    # carry none, and the early return that keeps `placement_refused` alive on a schema error is
    # exactly where the journey then could not tell which house the refusal was of -- so it read
    # "not yet evaluated" and offered the drawings and the export as ready links over a refused
    # house (`oq/an-evaluation-whose-check-errored-names-no-plan`, answer 1). The id is the
    # CALLER's document's: the revision loop re-places the record and keeps its id, and this route
    # answers for the document it was sent. `core.check_plan`'s own payload, which the MCP tool
    # serves, is untouched -- this is the workbench route, not the tool.
    out = {"plan": plan.get("id"),
           "check": check, "timing_ms": {"check": round((t1 - t_revise) * 1000)}}
    if place:
        out["timing_ms"]["place"] = round((t_place - t0) * 1000)
    if revision is not None:
        out["timing_ms"]["revise"] = round((t_revise - t_place) * 1000)
        _attach_revision(out, solved, revision)
    if "error" in check:
        # WP-13.4: THE PLACEMENT'S OWN ANSWER SURVIVES A SCHEMA ERROR. This early return sits
        # ABOVE the block that attached the placement, so a record failing `check_plan` came
        # back 200 with neither `placement` nor `placement_error` -- the shape WP-11.3 records
        # as a surface hanging on "placing..." for ever with nothing in a log. A refusal has to
        # travel the same way: a reader told their record is malformed still deserves to know
        # that the house was refused, and by what.
        _attach_placement(out, place, solved, placement_error, refused, engine)
        return out
    # WP-12.5 lifted this into `corpus.rooms_meta`, because the scene route needs the same
    # dict for the Round's overlays and a second copy is how two surfaces of one house come
    # to disagree about which rooms are wet.
    # AND IT READS THE RECORD THE FINDINGS WERE JUDGED AGAINST. The loop may add a door or
    # drop an optional room, so the meta the overlays draw from is the REVISED record's where
    # one exists -- the argument `plan` is the caller's unrevised document, and handing the
    # overlays that would put the sheet's rooms and the sheet's washes one revision apart.
    out["rooms_meta"] = corpus.rooms_meta(solved if revision is not None and solved is not None else plan)
    # check() (build/plan_check.py) now returns fault_unjudged beside fault_summary —
    # the could-not-judge detail, kept distinct from both failed and passed.
    out["fault_unjudged"] = check.get("fault_unjudged", [])
    # AND THE FOURTH STATE (WP-5.13). Forwarding only `fault_unjudged` left a not-applicable fault
    # in NO list on the bench -- which is the exact sentence core.check_measurements' own comment
    # gives for why the state was invented ("a fault absent from every list reads exactly like a
    # clear one"), relocated one API boundary out. Found 28 Aug 2026 by the WP-5.14 audit.
    out["fault_not_applicable"] = check.get("fault_not_applicable", [])
    _attach_placement(out, place, solved, placement_error, refused, engine)
    return out


# The WALL DRAG's own engine, by NAME. `PlanWorkbench.jsx` passes `engine="heuristic"` on the
# drag path and nothing else does (WP-6.3's own note: "the wall drag is the one caller that
# asks for the hill-climb by name"), so it is the discriminator the ruling needs rather than a
# proxy for one. Spelled once, here, so the two branches below cannot come to disagree.
SKETCH_ENGINE = "heuristic"

SKETCH_REASON = (
    "A WORKING SKETCH. This is the fast hill-climb the wall drag runs behind its 400 ms "
    "debounce, so that a handle stays under the pointer; it is not a placement anyone proved "
    "and it may not be exported. Where `refused` is present the type's own facts do not hold "
    "on it and no finished sheet, export or model is drawn from this record -- the next change "
    "that is not a drag takes the proof.")


def _attach_placement(out, place, solved, placement_error, refused, engine):
    """`placement`, `placement_error` or `placement_refused` -- exactly one of the three, in
    one function, called from BOTH return paths (WP-13.4).

    THE RULING, AND ITS ONE EXEMPTION. A refused placement reaches no user-facing surface, so
    this route answers 200 with `placement_refused` and NO `placement`: the bench draws the
    conflict set instead of a house. The exemption is the wall drag, which asks for the
    heuristic BY NAME -- a drag that cannot see the rectangle it is dragging is not a drag, so
    that one path still gets a `placement`, marked `sketch` with the refusal inside it. Every
    other route reads `geometry_report.refused` and refuses, and the export routes refuse a
    sketch for the reason a working drawing is not a contract drawing.

    `sketch` is written on EVERY heuristic evaluate and not only on a refused one, because a
    marking that appears only when something is wrong says nothing about the case where it is
    absent -- `refused` inside it is `null` where the type's facts hold."""
    if not place:
        return
    if solved is None:
        out["placement_error"] = placement_error
        return
    if refused and engine != SKETCH_ENGINE:
        out["placement_refused"] = refused
        return
    out["placement"] = core.placement_summary(solved)
    if engine == SKETCH_ENGINE:
        out["placement"]["sketch"] = {"working": True, "refused": refused,
                                      "reason": SKETCH_REASON}


# ------------------------------------------------- what the INTERACTIVE path may spend
# ADDED BY WP-13.9's OWN ADVERSARIAL AUDIT, which found the first version had put JOB-SHAPED
# WORK ON THE REQUEST PATH AND KEPT ONLY THE JOB'S CEILING. The route bounded `revise_rounds`
# by `core.REVISE_MAX_ROUNDS` (8) and `revise_budget_s` by `core.REVISE_MAX_BUDGET_S` (600) --
# the JOB route's numbers, chosen for a queue of one worker that nobody waits on. Measured by
# the audit on this tree: one request could ask for 8 rounds and 600 s, the loop tests its
# budget at the TOP of a round so the true ceiling is budget plus one round, and one CP round
# costs about 35 s -- **about 11 minutes of one core, on a route a browser waits on**, with
# the rate limiter's 60 calls an hour per identity then buying roughly eleven hours of CPU per
# wall hour from a single caller.
#
# The job route has a one-worker pool, a bounded queue, a 503 with `Retry-After`, an SSE
# stream and a result held for thirty minutes. This path has none of those and must therefore
# be bounded to what a person will actually wait through:
#
#   ROUNDS   the ruling's own number, two, and not the job's eight.
#   BUDGET   `geometry.BUDGET_REVISE_INLINE_S`, the constant DERIVED for this path, and never
#            the job's. A caller may LOWER it and may not raise it; raising it is what the job
#            route is for.
#   WIDTH    the search width the loop re-places at, capped at the default. `_candidates`
#            admits 2000, which is sized for ONE placement; the loop multiplies it by rounds
#            times moves.
#   AT ONCE  `INLINE_CONCURRENCY`. This endpoint is a sync `def`, so Starlette runs it in the
#            anyio threadpool -- 40 tokens for the WHOLE application, `/api/health` included
#            (`jobs.py` says so in its own comment). Forty concurrent revising evaluates hold
#            every token and the platform healthcheck queues behind them, which reads as a dead
#            container and takes every in-flight compose job with it on the restart. That is
#            the infrastructure audit's own measured failure (health 25 ms -> 1,021 ms behind
#            80 held tokens) re-created on a route that can now hold a token a thousand times
#            longer than the 338 ms it was measured at. Two at a time leaves 38 for everything
#            else, and a caller past the cap gets its SHEET with the rounds declined BY NAME --
#            never a silent skip, which would read as a loop that found nothing to do, and
#            never a 503, because the sheet is what was asked for and it is still correct.
INLINE_MAX_ROUNDS = 2
INLINE_MAX_CANDIDATES = 250
INLINE_CONCURRENCY = 2
_INLINE_SLOTS = threading.BoundedSemaphore(INLINE_CONCURRENCY)


def inline_budget_ceiling():
    """The interactive loop's ceiling, read from the ONE place that derives it. A second
    spelling here is how the route and the module come to disagree about what 30 s means."""
    geo = core._mod("geometry", os.path.join(core.ROOT, "build", "geometry.py"))
    return float(geo.BUDGET_REVISE_INLINE_S)


# --------------------------------------------------------------- the corrective rounds
# WP-13.9, RULED 19 SEP 2026. Lucas read the bench's Tidewater sheet -- sixty drawn findings,
# most of them the `unreachable` fatal -- beside a revision panel reading 0 rounds and 0 moves
# applied, and ruled: "there should be at least one or two steps of recursive self-improvement
# based on the criticisms identified before the plan is surfaced to the user."
#
# THIS SUPERSEDES WP-9.3's "a per-edit critique: deliberately not done. Evaluate stays at its
# measured cost" FOR THE EXPLICIT SOLVE ONLY. The distinction the bench already draws is the
# one that survives: a WALL DRAG asks for the hill-climb by name behind a 400 ms debounce and
# gets no rounds at all (a gesture cannot wait for a loop any more than it can wait for a
# proof), while a re-solve, a load and a paste are acts a person waits on deliberately. The
# route's default is 0, so every other caller -- the CLI parity test, the drag, the export
# paths -- is byte-identical to before.
#
# ONE BUILDING, AND THAT IS WHY THIS IS INLINE RATHER THAN THE JOB ROUTE. `/api/plan/revise`
# hands its record back STRIPPED and the bench re-solves it, so the sheet is one placement and
# the loop's key was measured on another -- which is what `RevisionPanel` means by "the two can
# differ", and what put sixty findings of a refused hill-climb placement beside a key proved on
# a different one. Here the loop's final PLACED record is what `check_plan` judges and what
# `placement_summary` is projected from, so WP-6.4's rule -- one drawing set is one building or
# it is nothing -- holds across the findings, the plate and the panel.
def _revise_inline(solved, parti, candidates, rounds, budget_s):
    """Run the loop on the placed record and return (record, report). Never raises: a loop
    that fails must not cost the reader the sheet, so the failure is recorded and the
    un-revised placement is returned."""
    geo = core._mod("geometry", os.path.join(core.ROOT, "build", "geometry.py"))
    ran = ((solved.get("geometry_report") or {}).get("solver") or {}).get("engine")
    # THE ENGINE THAT PLACED, NEVER `auto`. Two reasons, and the second is the sharper: a
    # round is judged by re-placing and comparing keys, so judging on an engine other than the
    # one that drew the sheet compares two houses (WP-9.2's own finding about declared moves on
    # the search); and `auto` would re-attempt the proof at 25 s inside EVERY round on a record
    # where it has just been measured to fall back, which is the reader's whole wait spent
    # re-learning what the solve above already reported.
    loop_engine = "cp" if ran == "cp-sat" else "heuristic"
    # THE CEILINGS ARE THIS MODULE'S, NOT THE CALLER'S. The route parses and this enforces, so
    # a caller that reaches `evaluate()` by any other path -- a test, a script, a future route
    # -- cannot buy the job's budget on the request thread either.
    rounds = max(1, min(INLINE_MAX_ROUNDS, int(rounds)))
    candidates = max(1, min(INLINE_MAX_CANDIDATES, int(candidates)))
    budget = min(float(budget_s), inline_budget_ceiling()) if budget_s else inline_budget_ceiling()
    if not _INLINE_SLOTS.acquire(blocking=False):
        # DECLINED BY NAME, and the sheet still lands. A silent skip here would be
        # indistinguishable from a loop that ran and found nothing to do, which is the exact
        # screen this package was written to remove.
        return solved, {"declined": (
            f"the server is already running {INLINE_CONCURRENCY} revising solves; this one was "
            f"placed and judged without corrective rounds. Press re-solve again, or use the "
            f"revise chips, which run as a queued job.")}
    try:
        res = core.revise_plan(
            solved, rounds=rounds, engine=loop_engine, candidates=candidates,
            place=True, include_plan=True, budget_s=budget,
            parti=parti, surfaced="with-its-own-placement",
            time_limit_s=geo.BUDGET_INTERACTIVE_S)
    except Exception as exc:                                  # noqa: BLE001 -- see docstring
        return solved, {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}
    finally:
        _INLINE_SLOTS.release()
    if "error" in res:
        return solved, {"error": res["error"]}
    # `revise()` carries the placement from its first critique onward, and that first critique
    # REUSES the placement solved above (`critique.has_placement`), so a loop that accepts
    # nothing costs one check and no solve at all.
    return res.get("plan") or solved, res["report"]


def _attach_revision(out, revised, revision):
    """What the loop did, on the response, ONCE. The revised DECLARED record rides so the bench
    can load it as one undo step, stripped exactly as `jobs.revised_plan` strips it -- and the
    report rides INSIDE it, as `revision_report`, which survives the strip (it is not in
    `openings.PLACEMENT_PLAN_KEYS`) and is what the panel reads.

    Two things are deliberately absent. The PLACEMENT, because it travels on `placement`,
    projected from the record the findings were judged against, and two copies of one placement
    on one response is how two readers of one house come to disagree. And a second copy of the
    REPORT: the first version set `out["revision"]` to the same object, measured at 147,583
    bytes on a 606,771-byte response, and the bench read only the one on the record."""
    if "declined" in revision:
        out["revision_skipped"] = revision["declined"]
        return
    if "error" in revision:
        out["revision_error"] = revision["error"]
        return
    op = core._mod("openings", os.path.join(core.ROOT, "build", "openings.py"))
    # ONE COPY, ON THE RECORD (WP-13.9's audit). The first version also set `out["revision"]`
    # to the same report, and MEASURED on the shipped Tidewater plan it is the same 147,583
    # bytes twice on a 606,771-byte response -- 24.3% of it, shipped to a bench that reads
    # `revised_plan.revision_report` and never looked at the other one. `jobs.py` had already
    # met this and says so in its own comment ("the report rode twice ... 87 KB each"); the
    # remedy there was to make them one object and the remedy here is to send one. A caller
    # asking what the rounds did reads the report where the job route also puts it.
    out["revised_plan"] = op.strip_placement(core.copy_json(revised))
