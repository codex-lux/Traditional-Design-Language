#!/usr/bin/env python3
"""Export the drawing set as layered DXF (WP-5.1). The drawing is a render of the
data — the same records the SVG renderers draw from, emitted as measured CAD
linework a drafter can open. Model space is in INCHES (record feet x 12,
$INSUNITS=1, architectural units), model y is north, one DXF file per sheet.

What the DXF carries, and where — the judgment this file rests on:

  * GEOMETRY comes from geometry. Room rectangles, the footprint, window and
    door linework, bay grid, lot and setback lines are drawn entities on TDL-*
    layers, at true size.
  * FACTS OF RECORD ride on the entities they describe, the way a real sheet
    carries its schedules and general notes: each room polyline carries its own
    record (minus solved geometry) as XDATA under appid "TDL"; the plan's
    non-room facts (style, massing, groupings, context, site, declared,
    measurements, adjacencies…) ride on a TDL-META marker at the origin.
    Nothing is invented on import, and nothing rides hidden — every carried
    fact is also legible on the sheet or in the record it was drawn from.
  * The drawn window/door entities carry short cross-reference headers, and
    build/import_dxf.py REFUSES when drawing and carried record disagree —
    the linework validates the data rather than decorating it.

Layer scheme (plan sheet; Ln = level index):
  TDL-META            marker point carrying the plan-level record
  TDL-TITLE           title text (name, style, bays, relaxation count)
  TDL-SITE            lot line and buildable envelope
  TDL-GRID            bay lines
  TDL-Ln-WALL         exterior boundary of the level
  TDL-Ln-ROOM         one closed polyline per room (carries the room record)
  TDL-Ln-WINDOW       window opening lines on exterior walls, true width
  TDL-Ln-DOOR         door opening + quarter-circle swing at shared walls
  TDL-Ln-ANNO         room names and dimensions

Section / roof / elevation sheets are linework-only renders of their records
(TDL-SECT-*, TDL-ROOF-*, TDL-ELEV-* layers); the plan sheet is the one that
round-trips, because the plan record is the IR.

Honest refusals: without ezdxf installed every entry point returns
{"error": "could not export: …", "unexported": True} — the OQ 35 pattern —
and `selftest` exits 3, which check_all.py reports as COULD NOT EVALUATE,
never as passed.

    python3 build/export_dxf.py plans/tidewater-georgian-careful.json --outdir dist/dxf
    python3 build/export_dxf.py selftest
"""
import argparse
import copy
import json
import math
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

APPID = "TDL"
IN = 12.0                      # record feet -> drawing inches
TEXT_H = 8.0                   # annotation text height, inches
TITLE_H = 14.0

REFUSAL = {"error": "could not export: the ezdxf package is not installed "
                    "(pip install ezdxf). Nothing was written.",
           # "refusal" marks COULD-NOT-EVALUATE (missing optional dep) apart
           # from a real failure — only this earns exit 3 / HTTP 501; a plan
           # the solver could not place is a FAILURE and must say so
           "unexported": True, "refusal": True}


def _ezdxf():
    try:
        import ezdxf
        return ezdxf
    except ImportError:
        return None


def _new_doc(ezdxf):
    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 1        # inches
    doc.header["$LUNITS"] = 4          # architectural units
    doc.header["$MEASUREMENT"] = 0     # imperial
    if APPID not in doc.appids:
        doc.appids.add(APPID)
    return doc


def _layer(doc, name, color=7, linetype=None):
    if name not in doc.layers:
        attribs = {"color": color}
        if linetype and linetype in doc.linetypes:
            attribs["linetype"] = linetype
        doc.layers.add(name, **attribs)
    return name


def _xdata(entity, header, payload=None, chunk=200):
    """Attach a TDL header string and an optional JSON payload as XDATA. The
    payload is chunked because a single XDATA string is capped at 255 bytes."""
    tags = [(1000, header)]
    if payload is not None:
        s = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        for i in range(0, len(s), chunk):
            tags.append((1000, s[i:i + chunk]))
    entity.set_xdata(APPID, tags)


def _text(msp, layer, text, x, y, h=TEXT_H, align_end=False):
    t = msp.add_text(text, dxfattribs={"layer": layer, "height": h})
    t.set_placement((x, y))
    return t


# ------------------------------------------------------------------ plan sheet

def _solved_copy(plan, parti=None, candidates=250):
    """Return (original, solved). The original is what the XDATA carries; the
    solved deepcopy is what gets drawn. A plan whose rooms already carry
    geometry (a workbench bench plan) is drawn as it stands."""
    has_geometry = any("geometry" in r for lv in plan.get("levels", []) for r in lv["rooms"])
    if has_geometry:
        return plan, plan
    GEO = _mod("geometry", f"{ROOT}/build/geometry.py")
    # The sheet is a DERIVATION of the record, drawn the same way the workbench draws it.
    # That premise is the whole rule and it did not change; what changed is what the
    # workbench draws with. This said "the heuristic" until WP-6.4, and by then the bench
    # had been on `auto` since WP-6.3 -- so an export shipped a placement the reader had
    # never seen. `_placed` in workbench/server/corpus.py hands this function an already
    # placed record for every user-facing export, and `has_geometry` above returns it
    # untouched; this branch is the CLI and library path, and it takes the same engine the
    # bench does.
    solved = GEO.solve(copy.deepcopy(plan), parti, candidates, engine="auto")
    if "error" in solved:
        return plan, solved
    return plan, solved


# room-record keys that are solver output, never authored — stripped from what
# the XDATA carries so the round-trip returns the authored record
_SOLVED_ROOM_KEYS = ("geometry", "fixture_layout")
_SOLVED_PLAN_KEYS = ("footprint", "geometry_report", "stair", "opening_report")
# WP-6.2 put solver output INSIDE the openings for the first time. Until then everything the
# placement wrote lived in keys of its own — `geometry` on a room, `footprint` on the plan —
# and stripping the top level was enough. A door now carries the wall and the position the
# placement gave it, or the reason it could not be placed, and those are as much solver
# output as a rectangle is: leaving them in the XDATA made the round-trip return a record
# the author never wrote. Caught by tests/test_export.py, which asserts the rebuilt record
# deep-equals the authored one.
# and the two are NOT the same list. A window has always declared its own `wall` — that is
# an authored fact and stripping it lost it — while a door had no wall at all until 0.3.0,
# so on a door `wall` is placement output. The distinction cost one round-trip failure to
# find and is worth the two constants.
_SOLVED_DOOR_KEYS = ("wall", "position_ft", "positions_ft", "hinge", "swing_into", "unplaced")
_SOLVED_WINDOW_KEYS = ("position_ft", "positions_ft", "unplaced")


def _room_record(room):
    out = {k: v for k, v in room.items()
           if k not in _SOLVED_ROOM_KEYS and not k.startswith("_")}
    for key, drop in (("doors", _SOLVED_DOOR_KEYS), ("windows", _SOLVED_WINDOW_KEYS)):
        if key in out:
            out[key] = [{k: v for k, v in o.items() if k not in drop} for o in out[key]]
    return out


def _plan_meta(plan):
    meta = {k: v for k, v in plan.items() if k != "levels" and k not in _SOLVED_PLAN_KEYS}
    meta["levels_meta"] = [{k: v for k, v in lv.items() if k != "rooms"}
                           for lv in plan.get("levels", [])]
    return meta


def export_plan_dxf(plan, path, parti=None, candidates=250):
    ezdxf = _ezdxf()
    if ezdxf is None:
        return dict(REFUSAL)
    original, solved = _solved_copy(plan, parti, candidates)
    if "error" in solved:
        return {"error": solved["error"], "unexported": True}

    doc = _new_doc(ezdxf)
    msp = doc.modelspace()
    fp = solved.get("footprint", {})
    W, H = fp.get("width_ft", 40) * IN, fp.get("depth_ft", 30) * IN

    # plan-level record on a marker at the origin
    meta_layer = _layer(doc, "TDL-META", color=8)
    marker = msp.add_point((0, 0), dxfattribs={"layer": meta_layer})
    _xdata(marker, "TDL::plan-meta", _plan_meta(original))

    # title
    title_layer = _layer(doc, "TDL-TITLE", color=7)
    gr = solved.get("geometry_report", {})
    rl = gr.get("relaxations", {})
    _text(msp, title_layer, original.get("name", original.get("id", "plan")), 0, H + 4 * TITLE_H, h=TITLE_H)
    _text(msp, title_layer,
          f"{original.get('style','')} - {fp.get('bays','?')} BAYS OF {fp.get('bay_module_ft','?')} FT - "
          f"{fp.get('width_ft','?')} x {fp.get('depth_ft','?')} FT - {fp.get('area_sf','?')} SF GROSS",
          0, H + 2.5 * TITLE_H, h=TEXT_H)
    _text(msp, title_layer,
          f"{rl.get('count', 0)} CUT(S) OFF THE BAY LINE"
          + (f", WORST {rl.get('max_off_grid_ft')} FT" if rl.get("count") else ""),
          0, H + 1.2 * TITLE_H, h=TEXT_H)
    inf = gr.get("infeasible")
    if inf:
        # the SVG carries this header; the drafter-facing sheet must too — a
        # least-bad relaxation exported without the label reads as measured
        _text(msp, title_layer,
              f"INFEASIBLE AS DECLARED — {len(inf.get('conflicts', []))} CONFLICT(S) "
              f"PROVEN; THIS DRAWING IS THE LEAST-BAD RELAXATION",
              0, H + 5.5 * TITLE_H, h=TEXT_H)

    # site: lot + buildable envelope (same fallbacks as render_plan.py)
    site = solved.get("site") or {}
    ctx = solved.get("context") or {}
    lot_w = site.get("lot_width_ft", ctx.get("lot_width_ft"))
    lot_d = site.get("lot_depth_ft", ctx.get("lot_depth_ft"))
    if lot_w and lot_d:
        site_layer = _layer(doc, "TDL-SITE", color=8, linetype="DASHED")
        ss = site.get("setback_side_ft")
        x_off = ss if ss is not None else max(0.0, (lot_w - W / IN) / 2)
        sf = site.get("setback_front_ft") or 0.0
        sr = site.get("setback_rear_ft")
        lw, ld = lot_w * IN, lot_d * IN
        x0, y0 = -x_off * IN, -sf * IN
        msp.add_lwpolyline([(x0, y0), (x0 + lw, y0), (x0 + lw, y0 + ld), (x0, y0 + ld)],
                           close=True, dxfattribs={"layer": site_layer})
        ss_in = (ss if ss is not None else x_off) * IN
        sr_in = (sr if sr is not None else max(0.0, lot_d - sf - H / IN)) * IN
        msp.add_lwpolyline([(x0 + ss_in, 0), (x0 + lw - ss_in, 0),
                            (x0 + lw - ss_in, y0 + ld - sr_in), (x0 + ss_in, y0 + ld - sr_in)],
                           close=True, dxfattribs={"layer": site_layer})

    # bay grid
    bm = (fp.get("bay_module_ft") or 10) * IN
    grid_layer = _layer(doc, "TDL-GRID", color=8, linetype="DASHED")
    b = bm
    while b < W - 0.1:
        msp.add_line((b, 0), (b, H), dxfattribs={"layer": grid_layer})
        b += bm

    levels = [lv for lv in solved["levels"] if any("geometry" in r for r in lv["rooms"])]
    doors_not_drawn = []
    for lv in levels:
        n = lv.get("index", 0)
        wall_layer = _layer(doc, f"TDL-L{n}-WALL", color=7)
        room_layer = _layer(doc, f"TDL-L{n}-ROOM", color=8)
        win_layer = _layer(doc, f"TDL-L{n}-WINDOW", color=2)
        door_layer = _layer(doc, f"TDL-L{n}-DOOR", color=3)
        anno_layer = _layer(doc, f"TDL-L{n}-ANNO", color=9)

        msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True,
                           dxfattribs={"layer": wall_layer})

        for seq, r in enumerate(lv["rooms"]):
            g = r.get("geometry")
            if not g:
                # an outdoor / unplaced room still rides on the sheet as record:
                # a marker at the origin corner, never an invented rectangle
                m = msp.add_point((0, -2 * TEXT_H * (seq + 1)), dxfattribs={"layer": room_layer})
                _xdata(m, f"TDL::room-unplaced::L{n}::{seq}", _room_record(r))
                continue
            x, y = g["x_ft"] * IN, g["y_ft"] * IN
            w, h = g["width_ft"] * IN, g["depth_ft"] * IN
            poly = msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                                      close=True, dxfattribs={"layer": room_layer})
            _xdata(poly, f"TDL::room::L{n}::{seq}", _room_record(r))
            nm = r.get("name") or r["id"]
            _text(msp, anno_layer, nm, x + w / 2 - len(nm) * TEXT_H * 0.35, y + h / 2 + 2)
            _text(msp, anno_layer, f"{g['width_ft']} x {g['depth_ft']} FT - {g['area_sf']} SF",
                  x + w / 2 - 40, y + h / 2 - TEXT_H - 4, h=TEXT_H * 0.75)

            # windows: true opening width (the SVG shrinks to 0.9x for legibility;
            # a measured drawing does not), evenly spaced by the render convention
            Wft, Hft = W / IN, H / IN
            for wi, win in enumerate(r.get("windows") or []):
                wall = win.get("wall")
                cnt = win.get("count") or 1
                ww = (win.get("width_ft") or 3) * IN
                for k in range(cnt):
                    t = (k + 1) / (cnt + 1)
                    line = None
                    if wall == "S" and g["y_ft"] <= 0.6:
                        cx = x + w * t
                        line = msp.add_line((cx - ww / 2, 0), (cx + ww / 2, 0),
                                            dxfattribs={"layer": win_layer})
                    elif wall == "N" and g["y_ft"] + g["depth_ft"] >= Hft - 0.6:
                        cx = x + w * t
                        line = msp.add_line((cx - ww / 2, H), (cx + ww / 2, H),
                                            dxfattribs={"layer": win_layer})
                    elif wall == "W" and g["x_ft"] <= 0.6:
                        cy = y + h * t
                        line = msp.add_line((0, cy - ww / 2), (0, cy + ww / 2),
                                            dxfattribs={"layer": win_layer})
                    elif wall == "E" and g["x_ft"] + g["width_ft"] >= Wft - 0.6:
                        cy = y + h * t
                        line = msp.add_line((W, cy - ww / 2), (W, cy + ww / 2),
                                            dxfattribs={"layer": win_layer})
                    if line is not None:
                        _xdata(line, f"TDL::window::L{n}::{r['id']}::{wi}::{k+1}/{cnt}")

        # doors where two placed rooms share a wall — drawn once per pair, the
        # opening at the door's own recorded width (the SVG uses a fixed 3 ft)
        idx = {r["id"]: r.get("geometry") for r in lv["rooms"] if r.get("geometry")}
        RP = _mod("render_plan", f"{ROOT}/build/render_plan.py")
        drawn = set()
        for r in lv["rooms"]:
            a = idx.get(r["id"])
            if not a:
                continue
            for di, d in enumerate(r.get("doors") or []):
                to = d["to"]
                key = tuple(sorted((r["id"], to)))
                if to == "exterior" or to not in idx or key in drawn:
                    continue
                drawn.add(key)
                # WP-6.1: measured against THIS door's leaf and its jambs, not the flat
                # 3.2 ft the draw test used to apply to every door alike. A closet door
                # narrower than 3.2 ft is now exported rather than listed as undrawable,
                # which is the export half of OQ 41/63.
                seg = RP._shared(a, idx[to], width_ft=(d.get("width_ft") or RP.DEFAULT_DOOR_FT))
                if not seg:
                    # a declared door the placement gives no wall wide enough to hold —
                    # stated, never silently omitted
                    doors_not_drawn.append(f"L{n} {r['id']}-{to}")
                    continue
                (px, py), horiz = seg
                dw = (d.get("width_ft") or 3.0) * IN / 2
                px, py = px * IN, py * IN
                if horiz:
                    line = msp.add_line((px - dw, py), (px + dw, py), dxfattribs={"layer": door_layer})
                    msp.add_arc((px - dw, py), 2 * dw, 0, 90, dxfattribs={"layer": door_layer})
                else:
                    line = msp.add_line((px, py - dw), (px, py + dw), dxfattribs={"layer": door_layer})
                    msp.add_arc((px, py - dw), 2 * dw, 0, 90, dxfattribs={"layer": door_layer})
                _xdata(line, f"TDL::door::L{n}::{r['id']}::{di}")

    if doors_not_drawn:
        _text(msp, _layer(doc, "TDL-TITLE", color=7),
              f"{len(doors_not_drawn)} DECLARED DOOR(S) WITHOUT A DRAWABLE SHARED WALL — "
              f"IN THE RECORD, NOT THE LINEWORK", 0, -3 * TITLE_H, h=TEXT_H)
    doc.saveas(path)
    fpr = solved.get("footprint", {})
    out = {"path": path, "sheets": "plan", "levels": len(levels),
           "footprint_ft": [fpr.get("width_ft"), fpr.get("depth_ft")]}
    if doors_not_drawn:
        out["doors_not_drawn"] = doors_not_drawn
    return out


# --------------------------------------------------------------- section sheet

def export_section_dxf(section, path):
    ezdxf = _ezdxf()
    if ezdxf is None:
        return dict(REFUSAL)
    doc = _new_doc(ezdxf)
    msp = doc.modelspace()
    fp = section["footprint"]
    span = min(fp["width_ft"], fp["depth_ft"]) * IN
    roof = section["roof"]

    grade = _layer(doc, "TDL-SECT-GRADE", color=7)
    wall = _layer(doc, "TDL-SECT-WALL", color=7)
    floor = _layer(doc, "TDL-SECT-FLOOR", color=8)
    rf = _layer(doc, "TDL-SECT-ROOF", color=2)
    anno = _layer(doc, "TDL-SECT-ANNO", color=9)

    msp.add_line((-24, 0), (span + 24, 0), dxfattribs={"layer": grade})
    eave = roof["grade_to_eave_ft"] * IN
    msp.add_line((0, 0), (0, eave), dxfattribs={"layer": wall})
    msp.add_line((span, 0), (span, eave), dxfattribs={"layer": wall})

    storeys = sorted([s for s in section["storeys"]
                      if s.get("storey_height_ft") is not None and (s.get("index") or 0) >= 0],
                     key=lambda s: s["index"])
    for st in storeys:
        f = st.get("grade_to_floor_ft")
        if f is None:
            continue
        msp.add_line((0, f * IN), (span, f * IN), dxfattribs={"layer": floor})
        _text(msp, anno, f"{st['id']}: CEILING {st['ceiling_ft']} FT, STOREY {st['storey_height_ft']} FT",
              8, (f + st["storey_height_ft"] / 2) * IN)

    _text(msp, anno, f"EAVE {roof['grade_to_eave_ft']} FT", span + 16, eave)
    ridge_ft = roof.get("grade_to_ridge_ft")
    if ridge_ft is not None:
        msp.add_lwpolyline([(0, eave), (span / 2, ridge_ft * IN), (span, eave)],
                           dxfattribs={"layer": rf})
        _text(msp, anno, f"RIDGE {ridge_ft} FT - {roof['roof_pitch_rise_per_12']}:12 ({roof['pitch_source']})",
              span / 2 - 60, ridge_ft * IN + TEXT_H)
    else:
        msp.add_line((0, eave), (span, eave), dxfattribs={"layer": rf})
        _text(msp, anno, f"RIDGE UNJUDGED - {(roof.get('note') or '')[:80]}", 0, eave + 2 * TEXT_H)
    _text(msp, anno, f"{section.get('plan_id','')} - SECTION - {section.get('style','')} - "
                     f"{section['wall']['construction_type']}", 0, -4 * TEXT_H)
    doc.saveas(path)
    return {"path": path, "sheets": "section"}


# ------------------------------------------------------------------ roof sheet

_ROOF_LAYERS = {"eave": ("TDL-ROOF-EAVE", 7), "ridge": ("TDL-ROOF-RIDGE", 2),
                "hip": ("TDL-ROOF-HIP", 8), "gambrel-break": ("TDL-ROOF-BREAK", 3),
                "cross-ridge": ("TDL-ROOF-CROSS", 2)}


def export_roof_dxf(roof, path):
    ezdxf = _ezdxf()
    if ezdxf is None:
        return dict(REFUSAL)
    doc = _new_doc(ezdxf)
    msp = doc.modelspace()
    anno = _layer(doc, "TDL-ROOF-ANNO", color=9)
    for ln in roof["outline"]:
        name, color = _ROOF_LAYERS.get(ln["kind"], ("TDL-ROOF-EAVE", 7))
        layer = _layer(doc, name, color=color)
        msp.add_line((ln["x1"] * IN, ln["y1"] * IN), (ln["x2"] * IN, ln["y2"] * IN),
                     dxfattribs={"layer": layer})
    chim = _layer(doc, "TDL-ROOF-CHIMNEY", color=1)
    for c in roof.get("chimneys", {}).get("positions", []):
        msp.add_circle((c["x_ft"] * IN, c["y_ft"] * IN), 18.0, dxfattribs={"layer": chim})
    m = roof["main"]
    pitch = f"{m['pitch_rise_per_12']}:12" if m.get("pitch_rise_per_12") else "PITCH UNJUDGED"
    _text(msp, anno, f"{roof.get('plan_id','')} - ROOF PLAN - {roof.get('style','')} - "
                     f"{m.get('form','')} - {pitch}", 0, -4 * TEXT_H)
    doc.saveas(path)
    return {"path": path, "sheets": "roof"}


# ------------------------------------------------------------- elevation sheet

def export_elevation_dxf(elev, path, face=None):
    ezdxf = _ezdxf()
    if ezdxf is None:
        return dict(REFUSAL)
    if not elev.get("applicable", True):
        # the generator's own scope gate: outside the classical-front family this
        # is a refusal, not a guessed facade — same as render_elevation.py
        return {"error": f"elevation not applicable: {elev.get('note','')}",
                "refusal": True, "style": elev.get("style")}
    face = face or elev["entrance_face"]
    front = elev["faces"][face]
    fp = elev["footprint"]
    span = (fp["width_ft"] if face in ("S", "N") else fp["depth_ft"]) * IN
    section, roof = elev["section"], elev["roof_record"]
    ground = next(s for s in section["storeys"] if s.get("index") == 0)
    upper = next((s for s in section["storeys"] if s.get("index") == 1), ground)
    gw, uw = elev["storey_windows"][0], elev["storey_windows"][1]
    cornice = elev["eave_cornice"]

    doc = _new_doc(ezdxf)
    msp = doc.modelspace()
    wall = _layer(doc, "TDL-ELEV-WALL", color=7)
    grade = _layer(doc, "TDL-ELEV-GRADE", color=7)
    opening = _layer(doc, "TDL-ELEV-OPENING", color=2)
    sash = _layer(doc, "TDL-ELEV-SASH", color=8)
    cor = _layer(doc, "TDL-ELEV-CORNICE", color=3)
    rf = _layer(doc, "TDL-ELEV-ROOF", color=7)
    anno = _layer(doc, "TDL-ELEV-ANNO", color=9)

    top_of_wall = roof["main"]["grade_to_eave_ft"] * IN
    true_eave = elev["grade_to_true_eave_in"]
    cornice_band = true_eave - top_of_wall

    msp.add_line((-24, 0), (span + 24, 0), dxfattribs={"layer": grade})
    msp.add_lwpolyline([(0, 0), (span, 0), (span, top_of_wall), (0, top_of_wall)],
                       close=True, dxfattribs={"layer": wall})
    # frieze + cornice band, at the projection the record actually states rather than a
    # hardcoded six inches either side
    cornice = elev["eave_cornice"]
    band_proj = cornice.get("envelope_projection_in") or cornice.get("cornice_projection_in") or 6.0
    msp.add_lwpolyline([(-band_proj, top_of_wall), (span + band_proj, top_of_wall),
                        (span + band_proj, true_eave), (-band_proj, true_eave)],
                       close=True, dxfattribs={"layer": cor})

    # WP-5.11: THE CORNICE PROFILE ITSELF, AND THE ANSWER TO "DO WE NEED CAD FOR THIS".
    #
    # This file used to export the entire cornice as one closed rectangle plus a text note
    # saying how many members it had. That was not a limitation of DXF. It was that no layer of
    # this corpus held the moulding as GEOMETRY, so there was nothing for any format to carry --
    # a CAD or BIM layer bolted on underneath would have had exactly the same rectangle to
    # export, because a format serialises what is modelled and cannot invent what is not.
    #
    # build/profiles.py constructs the profile once, from the pack's own members, and this walks
    # the same segments the SVG sheet draws. Circular arcs survive exactly, as bulges -- a bulge
    # IS an arc, so the cornice in the CAD file is the same curve as the cornice on the sheet
    # and not a polygon approximating it. Elliptical quarters flatten at a stated tolerance.
    # The detail is drawn at full size beside the elevation, the way it would be on a sheet.
    members = cornice.get("members") or []
    if members:
        PROF = _mod("profiles", f"{ROOT}/build/profiles.py")
        prof_layer = _layer(doc, "TDL-ELEV-CORNICE-PROFILE", color=7)
        naked = cornice.get("frieze_naked_in") or 0.0
        from_axis = cornice.get("entablature_projection_datum",
                                cornice.get("projection_datum")) == "axis"
        sil = PROF.silhouette(members, naked_at=naked, from_axis=from_axis)
        ox, oy = span + 48.0, top_of_wall      # the detail stands clear of the elevation
        pts = PROF.dxf_points(sil["segments"], sil["start"])
        msp.add_lwpolyline([(ox + (x - naked), oy + y, 0.0, 0.0, b) for x, y, b in pts],
                           format="xyseb", close=True, dxfattribs={"layer": prof_layer})
        _text(msp, anno, f"EAVE CORNICE PROFILE - {len(members)} MEMBERS, FULL SIZE",
              ox, oy - 14)
        _text(msp, anno,
              f"RELIEF {round(cornice.get('order_relief_beyond_frieze_in') or 0, 2)} IN"
              + (f"; ENVELOPE RULE SAYS {round(band_proj, 2)} IN - BOTH SOURCED, SEE OQ"
                 if abs((cornice.get('order_relief_beyond_frieze_in') or 0) - band_proj) > 0.5 else ""),
              ox, oy - 26)

    # roof silhouette from roof.py's own elevation profile, shifted by the band
    profile = [(x * IN, h * IN + cornice_band) for x, h in roof["elevation_profiles"][face]]
    msp.add_lwpolyline(profile, dxfattribs={"layer": rf})

    floor1, floor2 = ground["grade_to_floor_ft"] * IN, upper["grade_to_floor_ft"] * IN

    def _win(cx_in, floor_in, wrec):
        sill = floor_in + wrec["sill_height_above_floor_in"]
        head = floor_in + wrec["head_height_above_floor_in"]
        ww = wrec["opening_width_in"]
        x0, x1 = cx_in - ww / 2, cx_in + ww / 2
        msp.add_lwpolyline([(x0, sill), (x1, sill), (x1, head), (x0, head)],
                           close=True, dxfattribs={"layer": opening})
        for i in range(1, wrec["lights_across"]):
            gx = x0 + ww * i / wrec["lights_across"]
            msp.add_line((gx, sill), (gx, head), dxfattribs={"layer": sash})
        lights_high = wrec["lights_high_per_sash"] * 2
        for j in range(1, lights_high):
            gy = sill + (head - sill) * j / lights_high
            msp.add_line((x0, gy), (x1, gy), dxfattribs={"layer": sash})

    ent = elev["entrance"]
    for cx_ft, kind in zip(front["centres_ft"], front["kinds"]):
        cx = cx_ft * IN
        # A BLIND BAY CARRIES NO OPENING AT EITHER STOREY (OQ 85). The bay holds its place in the
        # rhythm and a chimney stack stands on its axis, so there is nothing to draw. Missed when
        # the blind bay was introduced: this loop read `if door ... else window`, so `blind` fell
        # into the else and the CAD file drew the very collision the SVG had just stopped drawing
        # -- two surfaces disagreeing about one record, which is the class this package exists to
        # close. The selftest could not see it: it round-trips FINDINGS, not geometry.
        if kind == "blind":
            continue
        if kind == "door" and face == elev["entrance_face"]:
            dw, dh = ent["door_leaf_width_in"], ent["door_leaf_height_in"]
            x0, x1 = cx - dw / 2, cx + dw / 2
            msp.add_lwpolyline([(x0, floor1), (x1, floor1), (x1, floor1 + dh), (x0, floor1 + dh)],
                               close=True, dxfattribs={"layer": opening})
            cw = ent["casing_width_in"]
            eh = ent.get("entablature_height_in") or ent["surround_height_above_opening_in"]
            msp.add_lwpolyline([(x0 - cw, floor1), (x1 + cw, floor1),
                                (x1 + cw, floor1 + dh + eh), (x0 - cw, floor1 + dh + eh)],
                               close=True, dxfattribs={"layer": sash})
        else:
            _win(cx, floor1, gw)
        _win(cx, floor2, uw)

    m = roof["main"]
    pitch = f"{m['pitch_rise_per_12']}:12" if m.get("pitch_rise_per_12") else "PITCH UNJUDGED"
    _text(msp, anno, f"{elev.get('plan_id','')} - {face} ELEVATION - {elev.get('style','')} - "
                     f"{front['count']} BAYS - {m.get('form','')} {pitch} - "
                     f"CORNICE {cornice['cornice_height_in']} IN ({cornice['member_count']} MEMBERS)",
          0, -4 * TEXT_H)
    doc.saveas(path)
    return {"path": path, "sheets": f"elevation-{face}"}


# --------------------------------------------------------------------- driver

def export_all(plan, outdir, parti=None, candidates=250, face=None):
    """The full DXF set for one plan record: plan, section, roof, elevation.
    Refusals (missing library, non-applicable elevation) are returned in the
    result per sheet, stated, never collapsed into silence."""
    if _ezdxf() is None:
        return dict(REFUSAL)
    os.makedirs(outdir, exist_ok=True)
    pid = plan.get("id", "plan")
    out = {"plan_id": pid, "sheets": {}}

    out["sheets"]["plan"] = export_plan_dxf(plan, os.path.join(outdir, f"{pid}-plan.dxf"),
                                            parti, candidates)
    ST = _mod("structure", f"{ROOT}/build/structure.py")
    section = ST.build_section(copy.deepcopy(plan), parti)
    if "error" in section:
        out["sheets"]["section"] = {"error": section["error"], "unexported": True}
        return out
    out["sheets"]["section"] = export_section_dxf(section, os.path.join(outdir, f"{pid}-section.dxf"))

    RF = _mod("roof", f"{ROOT}/build/roof.py")
    roof = RF.build_roof(copy.deepcopy(plan), parti, section=section)
    if "error" in roof:
        out["sheets"]["roof"] = {"error": roof["error"], "unexported": True}
    else:
        out["sheets"]["roof"] = export_roof_dxf(roof, os.path.join(outdir, f"{pid}-roof.dxf"))

    EL = _mod("elevation", f"{ROOT}/build/elevation.py")
    elev = EL.build_elevation(copy.deepcopy(plan), parti,
                              section=section, roof=None if "error" in roof else roof)
    if "error" in elev:
        out["sheets"]["elevation"] = {"error": elev["error"], "unexported": True}
    else:
        res = export_elevation_dxf(elev, os.path.join(outdir,
                                   f"{pid}-elevation-{face or elev.get('entrance_face','S')}.dxf"), face)
        out["sheets"]["elevation"] = res
    return out


# -------------------------------------------------------------------- selftest

SELFTEST_PLANS = ["plans/spec-builder-colonial.json", "plans/tidewater-georgian-careful.json"]


def selftest():
    """Round-trip both check plans: record -> DXF -> record -> validator, and the
    findings must be identical. Exit 3 (COULD NOT EVALUATE) without ezdxf."""
    if _ezdxf() is None:
        print("COULD NOT EVALUATE: the ezdxf package is not installed (pip install ezdxf). "
              "The DXF export was not exercised — this is not a pass.")
        return 3
    import tempfile
    IMP = _mod("import_dxf", f"{ROOT}/build/import_dxf.py")
    PC = _mod("plan_check", f"{ROOT}/build/plan_check.py")
    C = PC.load_corpus()
    failures = 0
    for rel in SELFTEST_PLANS:
        plan = json.load(open(os.path.join(ROOT, rel)))
        with tempfile.TemporaryDirectory() as td:
            out = export_all(copy.deepcopy(plan), td)
            bad = {k: v for k, v in out.get("sheets", {}).items() if "error" in v and not v.get("refusal")}
            if "error" in out or bad:
                print(f"  FAIL {rel}: export errors: {out.get('error') or bad}")
                failures += 1
                continue
            back = IMP.read_plan_dxf(out["sheets"]["plan"]["path"])
            if "error" in back:
                print(f"  FAIL {rel}: import refused: {back['error']}")
                failures += 1
                continue
            f0 = PC.check(copy.deepcopy(plan), C)
            f1 = PC.check(back["plan"], C)
            a = json.dumps(f0, sort_keys=True, default=str)
            b = json.dumps(f1, sort_keys=True, default=str)
            if a != b:
                print(f"  FAIL {rel}: round-trip findings differ")
                failures += 1
                continue
            print(f"  OK   {rel}: {len(out['sheets'])} sheets, round-trip findings identical "
                  f"({len(f1.get('findings', []))} findings)")
    if failures:
        print(f"\n{failures} selftest failure(s).")
        return 1
    print("\nexport_dxf selftest: all round-trips identical.")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--parti")
    ap.add_argument("--outdir", default=os.path.join(ROOT, "dist", "dxf"))
    ap.add_argument("--face")
    ap.add_argument("--candidates", type=int, default=250)
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    parti = json.load(open(f"{ROOT}/partis/{a.parti}.json")) if a.parti else None
    out = export_all(plan, a.outdir, parti, a.candidates, a.face)
    if "error" in out:
        print(f"  ! {out['error']}")
        sys.exit(3 if out.get("refusal") else 1)
    print(f"\n  {plan.get('name', plan.get('id'))}")
    for kind, res in out["sheets"].items():
        if "error" in res:
            tag = "refused" if res.get("refusal") else "unexported"
            print(f"  {kind}: {tag} — {res['error'][:140]}")
        else:
            print(f"  {kind}: wrote {res['path']}")
    print()


if __name__ == "__main__":
    main()
