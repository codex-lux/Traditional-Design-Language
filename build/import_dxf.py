#!/usr/bin/env python3
"""Read a TDL-emitted plan DXF back into a plan record (WP-5.1's round-trip).

Deliberately MINIMAL: this reads the layer and XDATA conventions
build/export_dxf.py writes — it is the fidelity check on that exporter, not a
general drafter-drawing importer (that is WP-5.5, which will generalize this).

The contract, stated in export_dxf.py's own header: geometry is drawn, facts
of record ride as XDATA on the entities they describe. This reader rebuilds
the record from the carried facts and then CROSS-CHECKS the drawn linework
against them — every drawn window leaf must name a carried window record and
be drawn at that record's own width; every drawn door must name a carried
door. Where drawing and record disagree it refuses with the disagreement
named, never guesses, never patches.

    python3 build/import_dxf.py dist/dxf/tidewater-georgian-careful-plan.dxf --out roundtrip.json
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPID = "TDL"
IN = 12.0

REFUSAL = {"error": "could not import: the ezdxf package is not installed "
                    "(pip install ezdxf).",
           "unimported": True}

_ROOM_RE = re.compile(r"^TDL::room(?:-unplaced)?::L(\d+)::(\d+)$")
_WIN_RE = re.compile(r"^TDL::window::L(\d+)::(.+)::(\d+)::(\d+)/(\d+)$")
_DOOR_RE = re.compile(r"^TDL::door::L(\d+)::(.+)::(\d+)$")


def _tdl_xdata(entity):
    """Return (header, payload_or_None) from an entity's TDL XDATA, or None."""
    try:
        tags = entity.get_xdata(APPID)
    except Exception:
        return None
    strings = [t.value for t in tags if t.code == 1000]
    if not strings or not strings[0].startswith("TDL::"):
        return None
    header = strings[0]
    payload = None
    if len(strings) > 1:
        try:
            payload = json.loads("".join(strings[1:]))
        except json.JSONDecodeError as e:
            return (header, {"__parse_error__": str(e)})
    return (header, payload)


def read_plan_dxf(path):
    try:
        import ezdxf
    except ImportError:
        return dict(REFUSAL)
    try:
        doc = ezdxf.readfile(path)
    except Exception as e:
        return {"error": f"could not read DXF: {type(e).__name__}: {e}", "unimported": True}
    msp = doc.modelspace()

    plan_meta = None
    rooms = {}          # (level_index, seq) -> room record
    drawn_windows = []  # (level, room_id, wi, k, n, drawn_length_in)
    drawn_doors = []    # (level, room_id, di)

    for e in msp:
        x = _tdl_xdata(e)
        if not x:
            continue
        header, payload = x
        if payload is not None and "__parse_error__" in (payload or {}):
            return {"error": f"carried record on '{header}' is not valid JSON: "
                             f"{payload['__parse_error__']}", "unimported": True}
        if header == "TDL::plan-meta":
            plan_meta = payload
            continue
        m = _ROOM_RE.match(header)
        if m:
            lvl, seq = int(m.group(1)), int(m.group(2))
            if payload is None:
                return {"error": f"room entity '{header}' carries no record", "unimported": True}
            if e.dxftype() == "LWPOLYLINE" and len(e) != 4:
                return {"error": f"room '{payload.get('id','?')}' is drawn with {len(e)} vertices, "
                                 f"not a rectangle — drawing and record disagree", "unimported": True}
            rooms[(lvl, seq)] = payload
            continue
        m = _WIN_RE.match(header)
        if m:
            lvl, rid, wi = int(m.group(1)), m.group(2), int(m.group(3))
            k, n = int(m.group(4)), int(m.group(5))
            s, t = e.dxf.start, e.dxf.end
            length = ((t[0] - s[0]) ** 2 + (t[1] - s[1]) ** 2) ** 0.5
            drawn_windows.append((lvl, rid, wi, k, n, length))
            continue
        m = _DOOR_RE.match(header)
        if m:
            drawn_doors.append((int(m.group(1)), m.group(2), int(m.group(3))))

    if plan_meta is None:
        return {"error": "no TDL::plan-meta marker — not a TDL-emitted plan DXF "
                         "(a general drafter-drawing importer is WP-5.5, not this reader)",
                "unimported": True}

    # ---- rebuild the record: plan meta + levels_meta skeleton + carried rooms
    levels_meta = plan_meta.pop("levels_meta", [])
    plan = dict(plan_meta)
    plan["levels"] = []
    by_level = {}
    for (lvl, seq), rec in rooms.items():
        by_level.setdefault(lvl, []).append((seq, rec))
    used = set()
    for i, lm in enumerate(levels_meta):
        idx = lm.get("index", i)
        lv = dict(lm)
        lv["rooms"] = [rec for _, rec in sorted(by_level.get(idx, []))]
        used.add(idx)
        plan["levels"].append(lv)
    orphan_levels = sorted(set(by_level) - used)
    if orphan_levels:
        return {"error": f"rooms drawn on level(s) {orphan_levels} that the carried "
                         f"plan record does not declare — drawing and record disagree",
                "unimported": True}

    # ---- cross-check the drawn linework against the carried records
    room_index = {}
    for lv in plan["levels"]:
        for r in lv["rooms"]:
            room_index[(lv.get("index", 0), r["id"])] = r
    checks = {"window_leaves": 0, "doors": 0}
    for lvl, rid, wi, k, n, length in drawn_windows:
        r = room_index.get((lvl, rid))
        if r is None:
            return {"error": f"window drawn for room '{rid}' (level {lvl}) that carries "
                             f"no record", "unimported": True}
        wins = r.get("windows") or []
        if wi >= len(wins):
            return {"error": f"window {wi} drawn for room '{rid}' but its record carries "
                             f"only {len(wins)} window(s)", "unimported": True}
        rec = wins[wi]
        if (rec.get("count") or 1) != n:
            return {"error": f"room '{rid}' window {wi}: drawn as leaf {k} of {n}, record "
                             f"says count {rec.get('count') or 1}", "unimported": True}
        want = (rec.get("width_ft") or 3) * IN
        if abs(length - want) > 0.51:
            return {"error": f"room '{rid}' window {wi}: drawn {length:.1f} in wide, record "
                             f"says {want:.1f} in — drawing and record disagree", "unimported": True}
        checks["window_leaves"] += 1
    for lvl, rid, di in drawn_doors:
        r = room_index.get((lvl, rid))
        if r is None or di >= len(r.get("doors") or []):
            return {"error": f"door {di} drawn for room '{rid}' (level {lvl}) with no "
                             f"matching record", "unimported": True}
        checks["doors"] += 1

    return {"plan": plan, "cross_checks": checks,
            "note": "record rebuilt from carried XDATA; drawn linework cross-checked "
                    "against it (this reader is scoped to TDL-emitted DXF — WP-5.5 "
                    "generalizes to drafter drawings)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dxf")
    ap.add_argument("--out")
    a = ap.parse_args()
    res = read_plan_dxf(a.dxf)
    if "error" in res:
        print(f"  ! {res['error']}")
        sys.exit(3 if res.get("unimported") and "ezdxf" in res["error"] else 1)
    plan = res["plan"]
    print(f"\n  {plan.get('name', plan.get('id'))}: {len(plan['levels'])} level(s), "
          f"{sum(len(l['rooms']) for l in plan['levels'])} rooms, "
          f"{res['cross_checks']['window_leaves']} window leaves and "
          f"{res['cross_checks']['doors']} doors cross-checked")
    if a.out:
        json.dump(plan, open(a.out, "w"), indent=1, ensure_ascii=False)
        print(f"  wrote {a.out}")
    print()


if __name__ == "__main__":
    main()
