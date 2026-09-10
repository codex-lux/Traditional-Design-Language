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
import time

from . import corpus

core = corpus.core


def evaluate(plan, strict=False, place=True, parti=None, candidates=250,
             engine="auto"):
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
    solved = None
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
    t_place = time.perf_counter()
    check = core.check_plan(solved if solved is not None else plan, strict=strict)
    t1 = time.perf_counter()
    out = {"check": check, "timing_ms": {"check": round((t1 - t_place) * 1000)}}
    if place:
        out["timing_ms"]["place"] = round((t_place - t0) * 1000)
    if "error" in check:
        return out
    # WP-12.5 lifted this into `corpus.rooms_meta`, because the scene route needs the same
    # dict for the Round's overlays and a second copy is how two surfaces of one house come
    # to disagree about which rooms are wet.
    out["rooms_meta"] = corpus.rooms_meta(plan)
    # check() (build/plan_check.py) now returns fault_unjudged beside fault_summary —
    # the could-not-judge detail, kept distinct from both failed and passed.
    out["fault_unjudged"] = check.get("fault_unjudged", [])
    # AND THE FOURTH STATE (WP-5.13). Forwarding only `fault_unjudged` left a not-applicable fault
    # in NO list on the bench -- which is the exact sentence core.check_measurements' own comment
    # gives for why the state was invented ("a fault absent from every list reads exactly like a
    # clear one"), relocated one API boundary out. Found 28 Aug 2026 by the WP-5.14 audit.
    out["fault_not_applicable"] = check.get("fault_not_applicable", [])
    if place:
        if solved is None:
            out["placement_error"] = placement_error
        else:
            out["placement"] = core.placement_summary(solved)
    return out
