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
    t0 = time.perf_counter()
    check = core.check_plan(plan, strict=strict)
    t1 = time.perf_counter()
    out = {"check": check, "timing_ms": {"check": round((t1 - t0) * 1000)}}
    if "error" in check:
        return out
    # Per-room-type catalogue facts the overlays draw from (privacy rank, wet walls,
    # daylight multiplier). Joined here so the client never re-derives corpus data.
    D = core._data()
    meta = {}
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            t = r.get("type")
            if t and t not in meta:
                room = D["rooms"].get(t) or {}
                meta[t] = {
                    "function_class": room.get("function_class"),
                    "privacy_rank": room.get("privacy_rank"),
                    "plumbing": (room.get("servicing") or {}).get("plumbing"),
                    "daylight_multiplier": (room.get("daylight") or {}).get("depth_multiplier"),
                    # WP-6.2: the catalogue's own furniture, with the footprints and
                    # clearances it has always carried. The client could not draw a stair,
                    # a tub or a range because this dict did not ship them — 60 of 60 room
                    # records hold them and nothing downstream had ever seen one.
                    "furniture": [
                        {"item": f.get("item"), "footprint_in": f.get("footprint_in"),
                         "clearance_in": f.get("clearance_in"), "essential": f.get("essential")}
                        for f in (room.get("furniture") or [])
                        if f.get("footprint_in")
                    ],
                }
    out["rooms_meta"] = meta
    # check() (build/plan_check.py) now returns fault_unjudged beside fault_summary —
    # the could-not-judge detail, kept distinct from both failed and passed.
    out["fault_unjudged"] = check.get("fault_unjudged", [])
    # AND THE FOURTH STATE (WP-5.9). Forwarding only `fault_unjudged` left a not-applicable fault
    # in NO list on the bench -- which is the exact sentence core.check_measurements' own comment
    # gives for why the state was invented ("a fault absent from every list reads exactly like a
    # clear one"), relocated one API boundary out. Found 28 Aug 2026 by the WP-5.10 audit.
    out["fault_not_applicable"] = check.get("fault_not_applicable", [])
    if place:
        t2 = time.perf_counter()
        # place_plan deep-copies its input itself (geo.solve(copy_json(plan), …));
        # copying here too would serialize the record twice for nothing.
        placement = core.place_plan(plan, parti=parti, candidates=candidates,
                                    engine=engine)
        out["timing_ms"]["place"] = round((time.perf_counter() - t2) * 1000)
        if "error" in placement:
            out["placement_error"] = placement["error"]
        else:
            out["placement"] = placement
    return out
