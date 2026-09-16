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
    check = core.check_plan(solved if solved is not None else plan, strict=strict)
    t1 = time.perf_counter()
    out = {"check": check, "timing_ms": {"check": round((t1 - t_place) * 1000)}}
    if place:
        out["timing_ms"]["place"] = round((t_place - t0) * 1000)
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
    out["rooms_meta"] = corpus.rooms_meta(plan)
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
