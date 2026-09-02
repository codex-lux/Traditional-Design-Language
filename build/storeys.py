#!/usr/bin/env python3
"""Storey height from the ceiling height a plan states — ONE derivation, for every caller.

`proportions/modules/storey-graduation.json` says it in its own words: **"Dimension the
STOREY, not the ceiling."** Its `ceiling_height_rule` is `module - part * 1.25` with
`part = module / 12`, so a finished ceiling is `storey * (1 - 1.25/12)` and the storey is
recovered by dividing. The deduction is joist, subfloor, finish floor and ceiling — the pack's
own note calls it "a bit over 12 in on the default", and it is NOT a constant: at an 11 ft
ceiling it is 15.35 in, at 8.5 ft it is 11.86 in.

**This module exists because two callers each had their own answer and neither knew.**
`structure.py` inverted the pack rule, as above. `openings.py::stair_pass` wrote
`storey_in = (ch + 1.0) * 12.0` -- a flat twelve inches of floor assembly, invented -- beside
`ch = ground.get("floor_to_ceiling_ft") or 9.0`, a second invented number for the case where
the record is silent. On `plans/tidewater-georgian-careful.json` (an 11 ft ceiling) that is
144.0 in against the derived 147.3, which is 20 risers against 21: two records of one stair,
in one house, disagreeing by a step.

It is a LEAF and must stay one. `structure.py` loads `geometry.py`, which calls
`openings.stair_pass`, so `openings` importing `structure` would close a cycle. Nothing here
may import a sibling.

The fraction below is a TRANSCRIPTION of the pack's expression, not a read of it, and the
citation is the guard: `tests/test_storeys.py` holds it against the pack's own
`ceiling_height_rule` so the two cannot drift.
"""
from __future__ import annotations

# storey-graduation.json, derived_rules[ceiling_height_rule]: "module - part * 1.25",
# with invariant part = module / 12. Transcribed, and pinned against the pack by a test.
STOREY_CEILING_FRACTION = 1.0 - 1.25 / 12.0


_RISER_DIVISOR = None


def riser_divisor_in(root=None):
    """The acceptable riser, READ from storey-graduation.json rather than transcribed.

    That pack's `stair_type` rule is `ceil(module / D)` and D is the number: 7.25 until
    2 Sep 2026, 7.5 after Lucas ruled on it. It had been a bare literal in TWO Python files
    (`openings.py` and `structure.py`), each with a comment naming the pack it was copied
    from -- so moving the pack would have moved neither. This reads the expression and
    REFUSES on any shape it does not recognise, because a divisor silently defaulting to a
    stale number is the failure this replaces.
    """
    global _RISER_DIVISOR
    if _RISER_DIVISOR is None:
        import json, os, re
        here = root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pack = json.load(open(os.path.join(here, "proportions", "modules",
                                           "storey-graduation.json"), encoding="utf-8"))
        rule = next((r for r in pack.get("derived_rules", [])
                     if r.get("target_slot") == "stair_type"), None)
        if rule is None:
            raise ValueError("storey-graduation.json has no stair_type rule to read the "
                             "riser divisor from")
        m = re.fullmatch(r"ceil\(module / ([0-9.]+)\)", (rule.get("expression") or "").strip())
        if not m:
            raise ValueError("storey-graduation.json's stair_type expression is %r, which "
                             "this reader does not recognise; it expects "
                             "'ceil(module / <number>)'. Update build/storeys.py in the same "
                             "commit as the pack." % rule.get("expression"))
        _RISER_DIVISOR = float(m.group(1))
    return _RISER_DIVISOR


def storey_heights(plan):
    """Per level: the stated ceiling, the storey it implies, and the floor depth between.

    A level that states no ceiling — on the level or on any of its rooms — gets
    `storey_height_ft: None` and says so. **That is the honest answer and callers must
    handle it**: the number it replaced was an invented 9.0 ft, which is the OQ 52 class
    (a generator supplying a figure where the record is silent). No shipped plan takes
    this branch today — all 16 state a ground ceiling — so it is written for the plan
    that does not.
    """
    out = []
    for lv in plan.get("levels", []):
        ceiling_ft = lv.get("floor_to_ceiling_ft")
        if ceiling_ft is None:
            rooms_ceilings = [r.get("ceiling_ft") for r in lv.get("rooms", []) if r.get("ceiling_ft")]
            ceiling_ft = max(rooms_ceilings) if rooms_ceilings else None
        if ceiling_ft is None:
            out.append({"id": lv.get("id"), "index": lv.get("index"), "ceiling_ft": None,
                        "storey_height_ft": None, "floor_structure_depth_in": None,
                        "note": "No ceiling height stated on this level -- unjudged."})
            continue
        storey_ft = ceiling_ft / STOREY_CEILING_FRACTION
        out.append({
            "id": lv.get("id"), "index": lv.get("index"), "ceiling_ft": ceiling_ft,
            "storey_height_ft": round(storey_ft, 3),
            "floor_structure_depth_in": round((storey_ft - ceiling_ft) * 12, 2),
        })
    return out


def ground_storey_in(plan):
    """Floor-to-floor of the ground storey in INCHES, or None where the record is silent."""
    for s in storey_heights(plan):
        if (s.get("index") or 0) == 0:
            h = s.get("storey_height_ft")
            return round(h * 12.0, 4) if h else None
    return None
