#!/usr/bin/env python3
"""The wall between two drawn windows, on every face of every shipped plan: an instrument, not a
test (WP-16.6).

WP-15.6 measured it once, on the sixteen shipped plans placed on the deterministic engine: 35
piers between two drawn windows on one storey of one face, 24 of them narrower than the wider
window beside them, 25 under sash-light's 1.4, and 12 exactly the placer's own foot. Those figures
lived in a report and a question file, and no later reader could re-derive them. This is the
instrument, committed beside `tests/fault_clears.py`, so the figure is a command and not a quote.

A PIER here is the wall between two WINDOW rectangles that stand next to each other on one storey
of one face, as `elevation.opening_rects` draws them: the next opening along the face is a window
too. A window beside a door is not a window pier, and is not counted. Each pier is measured two
ways, because the corpus measures it two ways:

  opening  -- edge of one opening to edge of the next, over the WIDER opening. This is the
              placer's own unit (`openings.MIN_SOLID_FT` is a solid between openings) and the
              unit of sash-light's `minimum_solid_between_openings` (`opening_width * 1.4`).
  glass    -- glass edge to glass edge, over the wider window's glass. This is the unit of
              `faults/pier-narrower-than-the-opening.json`, whose test note says "Measure glass
              edge to glass edge". The glass is what `elevation.sash_layout` leaves inside the
              jambs and stiles; a window whose sash is refused has no glass drawn, and its piers
              are COULD NOT EVALUATE on this reading, never a number.

    python3 tests/window_piers.py                  # the census, one line per plan
    python3 tests/window_piers.py --out X.json     # and every pier, written where told
    python3 tests/window_piers.py --root <tree>    # another checkout (a control)

It places each plan on the heuristic engine (deterministic, so a figure is a statement about the
code and not about the clock), writes nothing unless told where, and never inside a repository.
The name does not begin `test_`, so pytest does not collect it.
"""
import argparse
import glob
import json
import os
import sys

sys.dont_write_bytecode = True

FLOOR = 1.0       # the figures the census counts against are printed beside it, never applied
AIM = 1.4


def _glass(rect):
    """(left glass edge, right glass edge) in the face's inches, or None where no glass is drawn."""
    sash = rect.get("sash") or {}
    if not sash or sash.get("refused"):
        return None
    st = {m.get("side"): m for m in sash.get("members") or [] if m.get("kind") == "stile"}
    if "L" not in st or "R" not in st:
        return None
    return st["L"]["x1"], st["R"]["x0"]


def census(root):
    root = os.path.abspath(root)
    sys.path.insert(0, os.path.join(root, "build"))
    import modcache
    GEO = modcache.load("geometry", os.path.join(root, "build", "geometry.py"))
    ST = modcache.load("structure", os.path.join(root, "build", "structure.py"))
    EL = modcache.load("elevation", os.path.join(root, "build", "elevation.py"))
    here = os.getcwd()
    os.chdir(root)
    try:
        rows, per_plan = [], {}
        paths = sorted(glob.glob("plans/*.json")) + sorted(glob.glob("plans/reference/*.json"))
        for f in paths:
            pid = os.path.basename(f)[:-5]
            with open(f, encoding="utf-8") as fh:
                placed = GEO.solve(json.load(fh), engine="heuristic")
            sec = ST.build_section(placed, None, geometry_result=placed)
            if "error" in sec:
                per_plan[pid] = {"elevation": "none: " + str(sec["error"])[:80]}
                continue
            elev = EL.build_elevation(placed, None, section=sec)
            if "error" in elev:
                per_plan[pid] = {"elevation": "none: " + str(elev["error"])[:80]}
                continue
            n = 0
            for face in "SNEW":
                rects = EL.opening_rects(elev, face)["rects"]
                by_storey = {}
                for r in rects:
                    by_storey.setdefault(r["storey"], []).append(r)
                for storey, rs in sorted(by_storey.items(), key=lambda kv: str(kv[0])):
                    rs = sorted(rs, key=lambda r: r["x0_in"])
                    for a, b in zip(rs, rs[1:]):
                        if a["kind"] != "window" or b["kind"] != "window":
                            continue
                        n += 1
                        pier = b["x0_in"] - a["x1_in"]
                        wider = max(a["width_in"], b["width_in"])
                        ga, gb = _glass(a), _glass(b)
                        if ga and gb:
                            gpier = gb[0] - ga[1]
                            gwider = max(ga[1] - ga[0], gb[1] - gb[0])
                            glass = round(gpier / gwider, 4) if gwider > 0 else None
                        else:
                            glass = None
                        rows.append({
                            "plan": pid, "style": placed.get("style"), "face": face,
                            "storey": storey, "left": a["id"], "right": b["id"],
                            "same_room": a["room"] == b["room"],
                            "pier_in": round(pier, 3), "wider_in": round(wider, 3),
                            "opening_ratio": round(pier / wider, 4) if wider else None,
                            "glass_ratio": glass,
                            "glass_unjudged": None if glass is not None else
                            "a window of the pair draws no glass (its sash is refused)",
                        })
            per_plan[pid] = {"elevation": "drawn", "piers": n}
        return rows, per_plan
    finally:
        os.chdir(here)


def summary(rows):
    op = [r for r in rows if r["opening_ratio"] is not None]
    gl = [r for r in rows if r["glass_ratio"] is not None]
    return {
        "piers": len(rows),
        "opening_under_floor": sum(1 for r in op if r["opening_ratio"] < FLOOR - 1e-9),
        "opening_under_aim": sum(1 for r in op if r["opening_ratio"] < AIM - 1e-9),
        "exactly_12_in": sum(1 for r in rows if abs(r["pier_in"] - 12.0) < 1e-6),
        "glass_judged": len(gl),
        "glass_under_floor": sum(1 for r in gl if r["glass_ratio"] < FLOOR - 1e-9),
        "same_room": sum(1 for r in rows if r["same_room"]),
        "narrowest_opening_ratio": min((r["opening_ratio"] for r in op), default=None),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--out", help="write every pier as JSON here")
    a = ap.parse_args()
    rows, per_plan = census(a.root)
    for pid, v in per_plan.items():
        mine = [r for r in rows if r["plan"] == pid]
        under = sum(1 for r in mine if r["opening_ratio"] is not None and r["opening_ratio"] < FLOOR - 1e-9)
        print(f"{pid:42s} {v['elevation'][:40]:40s} piers {len(mine):3d}  under {FLOOR:g}x: {under}")
    s = summary(rows)
    print()
    for k, v in s.items():
        print(f"{k:26s} {v}")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump({"summary": s, "rows": rows, "plans": per_plan}, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
