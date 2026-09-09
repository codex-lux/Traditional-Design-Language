#!/usr/bin/env python3
"""The wall assembly a plan is built of — ONE reading, for every caller.

`construction/wall-assemblies.json` states three thicknesses per `construction_type`:
exterior, bearing-interior and partition, each a typical range whose `authority.strength` is
`conventional` and not `documented`. `wall_thickness()` reads the plan's own
`declared.construction_type` against it and returns the midpoints.

**THIS MODULE EXISTS BECAUSE THE DRAWING NEEDS THE NUMBER AND `structure.py` CANNOT GIVE IT.**
The function lived in `structure.py`, which loads `plan_check.py` and `geometry.py` at module
level — and `geometry.py` calls `openings.stair_pass`, so anything in the placement or drawing
path that reached for `structure` would close an import cycle. WP-9.6 met exactly this and
answered it exactly this way, moving the storey derivation into `build/storeys.py`; its own
header states the rule this file follows: **it is a LEAF and must stay one. Nothing here may
import a sibling.**

`structure.py` re-exports `wall_thickness`, `load_construction` and
`DEFAULT_CONSTRUCTION_TYPE` under their old names, so every existing caller and
`tests/test_structure.py` keep working and there is exactly ONE implementation.

**The default is stated, never silent.** A plan that declares no `construction_type` gets
`platform-frame` WITH a `note` saying so, and every consumer is expected to print it — the
plan sheet does, in its title block. "Unjudged is not passed" applied to a wall: a house drawn
at a thickness nobody declared must say whose thickness it is.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_CONSTRUCTION_TYPE = "platform-frame"

_CONSTRUCTION = None


def load_construction():
    """The wall and floor catalogues, read once per process.

    WP-7.4 cached this. It was two file reads and two JSON parses per call, which was fine
    while every caller was once-per-plan -- and `geometry._span_charge` now calls `span_check`
    inside a 250-candidate loop, so `geometry_cp._score` and the candidate loop between them
    were re-reading static catalogue files hundreds of times per solve. Every consumer treats
    the result as read-only (checked: no assignment into `construction[...]` anywhere in the
    tree), so one shared dict is safe; do not mutate it."""
    global _CONSTRUCTION
    if _CONSTRUCTION is None:
        assemblies = {a["id"]: a for a in
                      json.load(open(f"{ROOT}/construction/wall-assemblies.json"))["assemblies"]}
        floor = json.load(open(f"{ROOT}/construction/floor-structure.json"))
        _CONSTRUCTION = {"assemblies": assemblies, "floor": floor}
    return _CONSTRUCTION


def _mid(rng):
    return (rng[0] + rng[1]) / 2.0 if isinstance(rng, list) else float(rng)


def wall_thickness(plan, construction=None):
    """Reads plan.declared.construction_type (the element slot every plan already has access
    to -- see elements/slots.json). Falls back to DEFAULT_CONSTRUCTION_TYPE with an explicit
    note when the plan declares nothing, rather than silently picking a number -- 'unjudged is
    not passed' applied to structure."""
    construction = construction or load_construction()
    declared = (plan.get("declared") or {}).get("construction_type")
    used_default = declared is None
    ctype = declared or DEFAULT_CONSTRUCTION_TYPE
    a = construction["assemblies"].get(ctype)
    if not a:
        a = construction["assemblies"][DEFAULT_CONSTRUCTION_TYPE]
        note = (f"construction_type '{ctype}' is not in construction/wall-assemblies.json; "
                f"fell back to {DEFAULT_CONSTRUCTION_TYPE}.")
        ctype = DEFAULT_CONSTRUCTION_TYPE
    else:
        note = ("No construction_type declared on this plan; assumed platform-frame."
                if used_default else None)
    return {
        "construction_type": ctype, "bearing": a["bearing"],
        "exterior_in": round(_mid(a["exterior_thickness_in"]), 2),
        "bearing_interior_in": round(_mid(a["bearing_interior_thickness_in"]), 2),
        "partition_in": round(_mid(a["partition_thickness_in"]), 2),
        "note": note,
    }
