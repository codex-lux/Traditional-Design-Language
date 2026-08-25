#!/usr/bin/env python3
"""Read a drafter's DXF into the makings of a plan record (WP-5.5).

This is the generalization WP-5.1's `import_dxf.py` refused to be. That reader
round-trips TDL's own emitted files, where every fact rides as XDATA; this one
faces an arbitrary drafter's drawing — unknown layers, unknown units, no TDL
conventions — and so it EXTRACTS CANDIDATES rather than producing a record
(the ruling: extract, then complete in the transcription form):

  * closed polylines become candidate room shapes (a non-rectangular one is
    taken as its bounding box and says so);
  * text entities inside a candidate become its name hint;
  * everything the drawing cannot state — room types, the style, ceilings,
    windows, doors — is a NAMED GAP for a human to fill in the workbench's
    Transcription surface. Nothing is guessed into a record.

A TDL-emitted file (it carries the TDL-META marker) short-circuits to
`import_dxf.read_plan_dxf` and comes back a complete record.

Units: $INSUNITS is trusted when it is stated and plausible; when the header
is silent or implausible the room-scale heuristic below scores each hypothesis
by how many candidate sides land in a plausible room range, and REFUSES to
pick when no hypothesis clearly wins — pass --units to state it. An inference
is always reported as an inference.

    python3 build/ingest_dxf.py drawing.dxf [--units ft|in|mm|cm|m] [--out draft.json]
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _mod(n, p):
    # Delegates to build/modcache.py — one module execution per process (OQ 28).
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(n, p)

REFUSAL = {"error": "could not ingest: the ezdxf package is not installed "
                    "(pip install ezdxf).",
           "unimported": True}

# $INSUNITS -> (name, factor to feet). Only units a building drawing plausibly uses.
INSUNITS = {1: ("in", 1 / 12.0), 2: ("ft", 1.0), 4: ("mm", 1 / 304.8),
            5: ("cm", 1 / 30.48), 6: ("m", 1 / 0.3048)}
UNIT_FACTORS = {name: f for name, f in INSUNITS.values()}

PLAUSIBLE_SIDE_FT = (4.0, 60.0)     # a candidate room side, in feet
KEEP_SIDE_FT = (3.0, 80.0)          # outside this after scaling, not a room


def _poly_area(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i][0], pts[i][1]
        x2, y2 = pts[(i + 1) % len(pts)][0], pts[(i + 1) % len(pts)][1]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def _closed_polys(msp):
    out = []
    for e in msp:
        t = e.dxftype()
        if t == "LWPOLYLINE" and e.closed:
            out.append((e.dxf.layer, [(p[0], p[1]) for p in e.get_points()]))
        elif t == "POLYLINE" and e.is_closed and not e.is_3d_polyline:
            out.append((e.dxf.layer, [(v.dxf.location[0], v.dxf.location[1])
                                      for v in e.vertices]))
    return out


def _texts(msp):
    out = []
    for e in msp:
        t = e.dxftype()
        if t == "TEXT":
            out.append({"text": e.dxf.text, "x": e.dxf.insert[0], "y": e.dxf.insert[1]})
        elif t == "MTEXT":
            out.append({"text": e.plain_text(), "x": e.dxf.insert[0], "y": e.dxf.insert[1]})
    return [t for t in out if (t["text"] or "").strip()]


def _score_units(polys, factor):
    """Fraction of candidate sides that land in the plausible room range under
    this unit hypothesis. The heuristic the module header promises to report."""
    sides = []
    for _, pts in polys:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        sides += [(max(xs) - min(xs)) * factor, (max(ys) - min(ys)) * factor]
    if not sides:
        return 0.0
    lo, hi = PLAUSIBLE_SIDE_FT
    return sum(1 for s in sides if lo <= s <= hi) / len(sides)


def _resolve_units(doc, polys, declared):
    """(factor_to_ft, report). Stated units are trusted when plausible; a silent
    or implausible header goes to the heuristic; ambiguity is a refusal to pick."""
    if declared:
        if declared not in UNIT_FACTORS:
            return None, {"error": f"unknown --units '{declared}' (know: {sorted(UNIT_FACTORS)})"}
        f = UNIT_FACTORS[declared]
        return f, {"units": declared, "basis": "stated by the caller",
                   "plausibility": round(_score_units(polys, f), 2)}
    ins = doc.header.get("$INSUNITS", 0)
    if ins in INSUNITS:
        name, f = INSUNITS[ins]
        score = _score_units(polys, f)
        rep = {"units": name, "basis": f"$INSUNITS={ins} in the file's own header",
               "plausibility": round(score, 2)}
        if score < 0.3:
            rep["note"] = (f"the header says {name} but only {score:.0%} of candidate sides "
                           f"land in a plausible room range at that unit — header trusted "
                           f"anyway; pass --units to override")
        return f, rep
    scores = {name: round(_score_units(polys, f), 2) for name, f in INSUNITS.values()}
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    if ranked and ranked[0][1] >= 0.5 and (len(ranked) < 2 or ranked[0][1] - ranked[1][1] >= 0.25):
        name = ranked[0][0]
        return UNIT_FACTORS[name], {"units": name, "basis": "inferred by the room-scale heuristic",
                                    "plausibility": ranked[0][1], "scores": scores,
                                    "note": "an inference, not a fact of the file — "
                                            "confirm or override with --units"}
    return None, {"error": "units are ambiguous: the header states none and no hypothesis "
                           "clearly wins the room-scale heuristic — pass --units",
                  "scores": scores}


def extract(path, units=None):
    """A drafter's DXF -> candidates + named gaps; a TDL-emitted one -> the record."""
    try:
        import ezdxf
        from ezdxf import recover
    except ImportError:
        return dict(REFUSAL)
    try:
        doc, auditor = recover.readfile(path)
    except Exception as e:
        return {"error": f"could not read DXF: {type(e).__name__}: {e}", "unimported": True}
    msp = doc.modelspace()

    # a TDL-emitted plan sheet is the complete record already — delegate
    if any(e.dxftype() == "POINT" and e.dxf.layer == "TDL-META" for e in msp):
        IM = _mod("import_dxf", f"{ROOT}/build/import_dxf.py")
        res = IM.read_plan_dxf(path)
        if "error" in res:
            return res
        return {"complete": True, "source": "tdl-dxf", "record": res["plan"],
                "cross_checks": res["cross_checks"]}

    polys = _closed_polys(msp)
    texts = _texts(msp)
    open_polys = sum(1 for e in msp if e.dxftype() == "LWPOLYLINE" and not e.closed)
    lines = sum(1 for e in msp if e.dxftype() == "LINE")

    if not polys:
        return {"error": "no closed polylines — nothing this extractor can offer as a room "
                         "candidate. Rooms drawn as separate LINE segments are not "
                         "reconstructed (stated in docs/ingestion.md); trace them in the "
                         "Transcription surface instead.",
                "unimported": True,
                "counts": {"lines": lines, "open_polylines": open_polys, "texts": len(texts)}}

    factor, units_report = _resolve_units(doc, polys, units)
    if factor is None:
        return {"error": units_report["error"], "unimported": True,
                "units": units_report, "counts": {"closed_polylines": len(polys)}}

    # candidates, scaled to feet, normalized to a SW origin
    raw = []
    for layer, pts in polys:
        xs = [p[0] * factor for p in pts]
        ys = [p[1] * factor for p in pts]
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        if not (KEEP_SIDE_FT[0] <= w <= KEEP_SIDE_FT[1] and KEEP_SIDE_FT[0] <= h <= KEEP_SIDE_FT[1]):
            continue
        area = _poly_area(list(zip(xs, ys)))
        rect = bool(area / (w * h) >= 0.9) if w * h > 0 else False
        raw.append({"layer": layer, "x": min(xs), "y": min(ys),
                    "w": round(w, 2), "h": round(h, 2),
                    "rectangular": rect,
                    "note": None if rect else
                            "non-rectangular source polyline — taken as its bounding box, "
                            "which overstates the room; redraw in the form if it matters"})
    dropped = len(polys) - len(raw)
    if not raw:
        return {"error": f"all {len(polys)} closed polylines fall outside a plausible room "
                         f"size at {units_report['units']} — wrong units, or not a floor plan",
                "unimported": True, "units": units_report}

    ox = min(r["x"] for r in raw)
    oy = min(r["y"] for r in raw)
    for r in raw:
        r["x"] = round(r["x"] - ox, 2)
        r["y"] = round(r["y"] - oy, 2)

    # name hints: text whose insert point falls inside exactly one candidate
    unmatched = []
    for t in texts:
        tx, ty = t["x"] * factor - ox, t["y"] * factor - oy
        hosts = [r for r in raw if r["x"] <= tx <= r["x"] + r["w"]
                 and r["y"] <= ty <= r["y"] + r["h"]]
        if len(hosts) == 1 and "name_hint" not in hosts[0]:
            hosts[0]["name_hint"] = t["text"].strip()
        else:
            unmatched.append(t["text"].strip())

    gaps = [
        "room types: a drawing does not state them — every candidate needs a type "
        "from the room catalog before it is a record",
        "style: a judgment, not an extraction — set it, and say why, in provenance",
        "levels and ceilings: candidates are one flat set; assign levels and "
        "floor_to_ceiling_ft",
        "windows and doors: not extracted from a drafter's linework — place them in "
        "the form",
    ]
    if dropped:
        gaps.append(f"{dropped} closed polyline(s) outside plausible room size were set aside")
    if open_polys or lines:
        gaps.append(f"{lines} LINE and {open_polys} open polyline entities were not "
                    f"interpreted (wall topology is not reconstructed — stated scope)")

    return {"complete": False, "source": "drafter-dxf", "units": units_report,
            "candidates": {"rooms": sorted(raw, key=lambda r: (-r["y"], r["x"])),
                           "texts_unmatched": unmatched},
            "gaps": gaps,
            "layers": sorted({r["layer"] for r in raw}),
            "counts": {"closed_polylines": len(polys), "kept": len(raw),
                       "dropped": dropped, "lines": lines,
                       "open_polylines": open_polys, "texts": len(texts)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dxf")
    ap.add_argument("--units", choices=sorted(UNIT_FACTORS))
    ap.add_argument("--out")
    a = ap.parse_args()
    res = extract(a.dxf, a.units)
    if "error" in res:
        print(f"  ! {res['error']}")
        if res.get("units", {}).get("scores"):
            print(f"    heuristic scores: {res['units']['scores']}")
        sys.exit(3 if res.get("unimported") and "ezdxf" in res.get("error", "") else 1)
    if res.get("complete"):
        p = res["record"]
        print(f"\n  TDL-emitted sheet: complete record '{p.get('id')}' "
              f"({sum(len(l['rooms']) for l in p['levels'])} rooms, cross-checked)")
    else:
        u = res["units"]
        print(f"\n  {res['counts']['kept']} room candidate(s) from "
              f"{res['counts']['closed_polylines']} closed polylines "
              f"(units {u['units']}, {u['basis']}, plausibility {u['plausibility']})")
        for r in res["candidates"]["rooms"]:
            hint = f"  “{r['name_hint']}”" if r.get("name_hint") else ""
            flag = "" if r["rectangular"] else "  [bounding box]"
            print(f"    {r['w']:6.1f} x {r['h']:5.1f} ft  @ ({r['x']}, {r['y']}){hint}{flag}")
        print("  gaps a human must fill before this is a record:")
        for g in res["gaps"]:
            print(f"    - {g}")
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, ensure_ascii=False)
        print(f"  wrote {a.out}")
    print()


if __name__ == "__main__":
    main()
