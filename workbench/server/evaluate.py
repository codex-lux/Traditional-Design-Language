"""POST /api/plan/evaluate — the Plan Workbench's one round-trip.

The client owns the plan record and sends the whole document per edit gesture.
The validator reads the record's *declared* fields, so a wall drag must already
have been written back to width_ft/length_ft before this is called; placement
is solved separately and returned beside the findings, never fed into them
(plan_check does not read geometry output — a settled fact, not an oversight).
"""
import time

from . import corpus

core = corpus.core


def evaluate(plan, strict=False, place=True, parti=None, candidates=250):
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
                }
    out["rooms_meta"] = meta
    # check() (build/plan_check.py) now returns fault_unjudged beside fault_summary —
    # the could-not-judge detail, kept distinct from both failed and passed.
    out["fault_unjudged"] = check.get("fault_unjudged", [])
    if place:
        t2 = time.perf_counter()
        placement = core.place_plan(core.copy_json(plan), parti=parti, candidates=candidates)
        out["timing_ms"]["place"] = round((time.perf_counter() - t2) * 1000)
        if "error" in placement:
            out["placement_error"] = placement["error"]
        else:
            out["placement"] = placement
    return out
