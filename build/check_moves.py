#!/usr/bin/env python3
"""check_moves.py — hold the move registry (moves/registry.json) and its code (build/moves.py)
together, and every move to the corpus sentence it says it executes (WP-9.2).

  1. moves/registry.json against schema/move.schema.json
  2. every registered id has an apply function, and every apply function is registered
  3. every `basis` names a record that EXISTS and quotes a sentence that is really in it --
     check_openings.check_basis, the grammar's own verifier, reused rather than copied
  4. every `touches` path is on the closed allow-list below, and none is a placement key: a
     move that could write `geometry` is a move that could make the drawing say what the
     record does not
  5. every `answers.layer` is a layer plan_check emits, every `answers.fault` a fault that
     exists; a lever answers a critique class and nothing else
  6. editorial moves carry judgment: true; measured moves quote a record, not a report

    python3 build/check_moves.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LAYERS = {"plan", "room", "furniture", "daylight", "adjacency", "completeness", "circulation",
          "privacy", "servicing", "grouping", "code", "style", "fault", "drawn"}

# What a move may write. Declared fields only; the ruled authority (1 Sep 2026) admits room
# add/remove, door add/remove and window add/remove, and nothing a placement writes.
ALLOWED_TOUCHES = {
    "levels[].rooms[]", "levels[].rooms[].width_ft", "levels[].rooms[].length_ft",
    "levels[].rooms[].ceiling_ft", "levels[].rooms[].window_head_ft",
    "levels[].rooms[].windows[]", "levels[].rooms[].windows[].wall", "levels[].rooms[].windows[].count",
    "levels[].rooms[].windows[].width_ft", "levels[].rooms[].windows[].height_ft",
    "levels[].rooms[].doors[]", "levels[].rooms[].doors[].to",
    "levels[].floor_to_ceiling_ft",
    "declared.<slot>", "declared.shutter", "declared.dormer.count",
    "measurements.shutter_leaf_width_in", "measurements.window_opening_width_in",
}
PLACEMENT_WORDS = ("geometry", "footprint", "geometry_report", "opening_report", "stair",
                   "fixture_layout", "position_ft", "positions_ft", "hinge", "swing_into", "unplaced",
                   "exterior_walls", "stacks_over")


def _mod(name, path):
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


def main():
    CO = _mod("check_openings", os.path.join(ROOT, "build", "check_openings.py"))
    MV = _mod("moves", os.path.join(ROOT, "build", "moves.py"))
    rep = CO.Report()
    reg = json.load(open(os.path.join(ROOT, "moves", "registry.json"), encoding="utf-8"))

    # 1 -- schema
    try:
        import jsonschema
        schema = json.load(open(os.path.join(ROOT, "schema", "move.schema.json"), encoding="utf-8"))
        for e in sorted(jsonschema.Draft202012Validator(schema).iter_errors(reg), key=lambda e: list(e.path)):
            rep.err("moves/registry.json", f"schema: {'/'.join(str(p) for p in e.path)}: {e.message[:160]}")
    except ImportError:
        rep.warn("moves/registry.json", "jsonschema not installed; schema not checked")

    ids = [m["id"] for m in reg["moves"]]
    if len(ids) != len(set(ids)):
        rep.err("moves/registry.json", "duplicate move id")

    # 2 -- code and data agree
    for mid in ids:
        if mid not in MV.APPLY:
            rep.err(f"moves/registry.json[{mid}]", "registered and has no apply function in build/moves.py")
    for mid in MV.APPLY:
        if mid not in ids:
            rep.err(f"build/moves.py[{mid}]", "has an apply function and is not registered")

    faults = {f[:-5] for f in sorted(os.listdir(os.path.join(ROOT, "faults"))) if f.endswith(".json")}
    for m in reg["moves"]:
        where = f"moves/registry.json[{m['id']}]"
        # 3 -- the basis
        CO.check_basis(rep, m, source="moves/registry.json")
        # 4 -- touches
        for t in m["touches"]:
            if t not in ALLOWED_TOUCHES:
                rep.err(where, f"touches {t!r}, which is not on the allow-list")
            if any(w in t for w in PLACEMENT_WORDS):
                rep.err(where, f"touches {t!r}, a placement key -- a move may never write what the solver wrote")
        if m["requires"] == "lever" and m["touches"]:
            rep.err(where, "a lever touches nothing on the record")
        # 5 -- answers
        a = m["answers"]
        if "class" in a:
            if a["class"] != "placement" or m["requires"] != "lever":
                rep.err(where, "only a lever answers a critique class, and only `placement`")
        else:
            if a.get("layer") not in LAYERS:
                rep.err(where, f"answers layer {a.get('layer')!r}, which plan_check does not emit")
            if a.get("fault") and a["fault"] not in faults:
                rep.err(where, f"answers fault {a['fault']!r}, which does not exist")
        # 6 -- editorial is marked
        if m["kind"] == "editorial" and not m.get("judgment"):
            rep.err(where, "an editorial move must carry judgment: true")
        if m["kind"] == "measured" and m.get("judgment"):
            rep.warn(where, "a measured move carries judgment: true; say which it is")

    for r in reg["refusals"]:
        if r["id"] in ids:
            rep.err(f"moves/registry.json[refusals:{r['id']}]", "is both refused and registered")

    for w in rep.warnings:
        print(f"WARN  {w}")
    if rep.errors:
        print("\n".join(f"ERROR {e}" for e in rep.errors))
        print(f"\n{len(rep.errors)} error(s)")
        return 1
    print(f"OK -- {len(ids)} moves, each with an apply function and a basis the record really says; "
          f"{len(reg['refusals'])} refusals stated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
