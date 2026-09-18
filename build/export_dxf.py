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

# WP-12.2: the opening rectangle and the loop around it are `elevation.opening_rects`,
# read here rather than transcribed a second time.
EL = _mod("elevation", f"{ROOT}/build/elevation.py")

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

def _forward(res):
    """Pass a refusal (or a plain error) up without flattening it to its sentence (WP-13.4).

    Four sites in this file rewrapped `{"error": res["error"], "unexported": True}` and dropped
    the conflict set with everything else. Named rather than inlined because there are four of
    them, which is how the first one came to be copied."""
    return {k: v for k, v in res.items()
            if k in ("error", "refused_placement", "unsolved")}


def _solved_copy(plan, parti=None, candidates=250):
    """Return (original, solved). The original is what the XDATA carries; the
    solved deepcopy is what gets drawn. A plan whose rooms already carry
    geometry (a workbench bench plan) is drawn as it stands.

    **AND A REFUSED PLACEMENT IS NOT DRAWN (WP-13.4).** Lucas ruled 15 Sep 2026 that a
    placement breaking a hard fact of the type is refused rather than drawn; a CAD file is a
    surface a reader takes away and builds from, so it is refused here exactly as the sheet is.
    BOTH paths are judged, because they are two different ways in: the short circuit above
    (a record a client already had placed, which never reached a record writer, so nothing had
    decided whether it may be drawn) and this file's own `GEO.solve` for the CLI and library
    path. `typefacts.judge` is the same one spelling `geometry._disclose` and
    `workbench/server/corpus._placed` call -- nothing here re-derives the verdict.

    The refusal is returned in the `solved` position, because every caller already tests
    `"error" in solved`; it carries `refused_placement` beside the sentence so the reason
    survives the frame rather than being flattened."""
    TF = _mod("typefacts", f"{ROOT}/build/typefacts.py")
    has_geometry = any("geometry" in r for lv in plan.get("levels", []) for r in lv["rooms"])
    if has_geometry:
        try:
            ref = TF.judge(plan)
        except Exception as exc:                    # unjudged, and unjudged does not refuse
            return plan, {"error": f"the placement this record carries could not be judged: "
                                   f"{type(exc).__name__}: {str(exc)[:200]}", "unsolved": True}
        if ref:
            return plan, _refused(ref)
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
    ref = (solved.get("geometry_report") or {}).get("refused")
    if ref:
        return plan, _refused(ref)
    return plan, solved


def _refused(ref):
    """One sentence and the typed verdict, in the shape every caller of `_solved_copy`
    already reads. Deliberately NOT keyed `refusal`: `workbench/server/app.py` maps that key
    to a 501, which is the honest answer for a missing ezdxf and a lie about a refused house."""
    return {"error": ("This placement is REFUSED and no drawing is exported: the type's own "
                      "facts do not hold on it. " + " ".join(ref.get("lines") or [])),
            "refused_placement": ref, "unexported": True, "unsolved": True}


# The keys a placement writes, and that the XDATA must NOT carry so the round-trip returns
# the authored record, are spelled ONCE, in build/openings.py (WP-9.1) — the pass that
# writes them owns the list, and build/revise.py strips a record with the same function
# before re-placing it. They lived here alone until Phase 9. The window/door asymmetry is
# real and is explained beside the constants: a window's `wall` is authored, a door's is
# placement output. tests/test_export.py refuses a second spelling of any of the four.
_OP = _mod("openings", f"{ROOT}/build/openings.py")
_SOLVED_ROOM_KEYS = _OP.PLACEMENT_ROOM_KEYS
_SOLVED_PLAN_KEYS = _OP.PLACEMENT_PLAN_KEYS
_SOLVED_DOOR_KEYS = _OP.PLACEMENT_DOOR_KEYS
_SOLVED_WINDOW_KEYS = _OP.PLACEMENT_WINDOW_KEYS


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
    # WP-9.2: a `revision_report` is authored history and rides in the record, but a six-round
    # report with attribution runs past the ~16 KB AutoCAD caps XDATA at per entity, and a
    # marker that silently truncated it would be a record that lied. The SUMMARY travels,
    # under its own name, and the note states what did not.
    rep = meta.pop("revision_report", None)
    if rep:
        meta["revision_summary"] = {**(rep.get("summary") or {}),
                                    "stop_reason": rep.get("stop_reason"), "mode": rep.get("mode"),
                                    "note": ("the full revision_report -- every round, move, basis and "
                                             "attribution -- is on the plan record and is NOT carried in "
                                             "this DXF; XDATA is capped near 16 KB per entity")}
    return meta


def export_plan_dxf(plan, path, parti=None, candidates=250):
    ezdxf = _ezdxf()
    if ezdxf is None:
        return dict(REFUSAL)
    original, solved = _solved_copy(plan, parti, candidates)
    if "error" in solved:
        # FORWARDED, NOT FLATTENED (WP-13.4). This read `{"error": solved["error"], ...}`
        # and dropped everything else, so a refusal computed one frame down arrived at the
        # route as a sentence with no conflict set -- the same rewrap defect
        # `corpus.drawing` carried at four call sites. A refusal is content: it names what
        # could not hold, and the reader it is for is one frame up.
        return dict(_forward(solved), unexported=True)

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

        # Interior doors -- ONE derivation, WP-13.2. Until Phase 13 this loop re-derived each
        # door from `RP._shared` and drew ONE quarter-circle per pair, `add_arc((px - dw, py),
        # 2*dw, 0, 90)`: hinged at the west or south jamb and swept 0 -> 90 degrees whatever the
        # record said, one arc for a pair of leaves. It read neither the hinge nor
        # `swing_positive`, so every leaf whose record swings negative was drawn into the wrong
        # room, and every pair was drawn as one leaf of twice the radius -- the gate measured
        # 7 of 13 leaves wrong on the search sheet and 15 of 24 on the prover's. The SVG, the
        # gate and this file read `RP.derive_openings` now, which is the one spelling of where
        # a door is and which way it goes, called the way `render_plan.render()` calls it (the
        # level's placed appendages, each room's own massing element) so the DXF is the SVG's
        # door and not a cousin: on the reference plan the bare call is one leaf short, the
        # breakfast-terrace door, which exists only once the terrace's rectangle is handed in.
        # A door the derivation cannot draw is in `undrawable` WITH its reason and reaches
        # `doors_not_drawn`, never silently skipped -- the width check that lived here (WP-6.1,
        # the leaf and its jambs) is `required_wall_ft` inside the derivation.
        RP = _mod("render_plan", f"{ROOT}/build/render_plan.py")
        op = RP.openings_of_level(solved, lv, n)     # the sheet's own derivation, one spelling
        for u in op["undrawable"]:
            if u["to"] == "exterior":
                # This exporter has never drawn an exterior door, drawable or not (`to ==
                # "exterior"` was `continue`d over since WP-5.1), so the banner's "without a
                # drawable shared wall" is about interior pairs. That exterior doors are absent
                # from the DXF is a pre-existing gap outside this package, recorded in its report.
                continue
            doors_not_drawn.append(f"L{n} {u['from']}-{u['to']}: {u.get('reason', '')}".rstrip(": "))
        rooms_by_id = {r["id"]: r for r in lv["rooms"]}
        for d in op["interior"]:
            # the XDATA header names the door by its index in the FROM room's own list, which
            # is what `import_dxf.read_plan_dxf` cross-checks against the carried record
            frm = rooms_by_id[d["from"]]
            di = next((i for i, dd in enumerate(frm.get("doors") or []) if dd.get("to") == d["to"]), None)
            if di is None:      # cannot happen by construction; a wrong index would pass the importer silently
                raise RuntimeError(f"derive_openings drew {d['from']}-{d['to']} from no declared door")
            horiz = d["horiz"]
            px, py = (d["pos_ft"], d["at_ft"]) if horiz else (d["at_ft"], d["pos_ft"])
            px, py = px * IN, py * IN
            dw = d["width_ft"] * IN / 2
            if horiz:
                line = msp.add_line((px - dw, py), (px + dw, py), dxfattribs={"layer": door_layer})
            else:
                line = msp.add_line((px, py - dw), (px, py + dw), dxfattribs={"layer": door_layer})
            _xdata(line, f"TDL::door::L{n}::{d['from']}::{di}")
            # THE LEAVES. A cased opening, a pocket, a garage or a bulkhead door has no swing
            # and gets no arc -- the SVG's `_door` draws those as jambs or a line, and an arc
            # here would be a leaf the record does not state. A single leaf is hinged on the
            # LOW jamb at the opening's full width; a pair is two leaves of half the width, one
            # on each jamb, meeting at the centre. Each leaf runs the quarter-circle from its
            # CLOSED position (along the wall, toward the far end of its run) to its OPEN one
            # (across the wall, on the side `swing_positive` names: +y off a horizontal wall,
            # +x off a vertical one). ezdxf arcs run counter-clockwise from start to end, so the
            # two angles are ordered to make the quarter between them the leaf's own. Model y is
            # north here and there is no flip, which is why the angles are the record's and not
            # the SVG's.
            if d["type"] in RP.LEAFLESS:
                continue
            open_deg = (90 if d["swing_positive"] else 270) if horiz else (0 if d["swing_positive"] else 180)
            if d["type"] == "double":
                leaves = ([((px - dw, py), dw, 0), ((px + dw, py), dw, 180)] if horiz
                          else [((px, py - dw), dw, 90), ((px, py + dw), dw, 270)])
            elif (d.get("hinge") or "low") == "high":
                # the record's jamb (WP-13.2): "high" hangs the leaf from the east or north jamb
                leaves = [((px + dw, py), 2 * dw, 180)] if horiz else [((px, py + dw), 2 * dw, 270)]
            else:
                leaves = [((px - dw, py), 2 * dw, 0)] if horiz else [((px, py - dw), 2 * dw, 90)]
            for (hx, hy), r, closed_deg in leaves:
                start, end = ((closed_deg, open_deg) if (open_deg - closed_deg) % 360 == 90
                              else (open_deg, closed_deg))
                msp.add_arc((hx, hy), r, start, end, dxfattribs={"layer": door_layer})
                # the leaf itself, hinge to tip, as the SVG draws it beside the arc
                tip = (hx + r * math.cos(math.radians(open_deg)), hy + r * math.sin(math.radians(open_deg)))
                msp.add_line((hx, hy), tip, dxfattribs={"layer": door_layer})

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
    # WP-12.2: the two storey window records are NOT read here any more. `opening_rects` reads
    # them, and each rectangle carries its own back under `record`, so this file cannot come to
    # disagree with the SVG about which storey a bay's opening belongs to.
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


    def _win(r):
        """WP-12.2: the rectangle is HANDED here, from `elevation.opening_rects`, and is no
        longer worked out a second time. This file and `render_elevation.py` had the same four
        numbers and the same loop written out separately, which is how the CAD file went on
        drawing a window through a chimney after the SVG had learned not to (OQ 85)."""
        wrec = r["record"]
        sill, head = r["sill_in"], r["head_in"]
        x0, x1 = r["x0_in"], r["x1_in"]
        ww = r["width_in"]
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
    # WP-12.2: ONE LOOP, in `elevation.opening_rects` — the blind-bay skip, the
    # door-at-the-entrance-face branch and the two storeys. The comment below is kept because
    # the defect it records is the reason this loop is no longer written twice.
    for r in EL.opening_rects(elev, face)["rects"]:
        # A BLIND BAY CARRIES NO OPENING AT EITHER STOREY (OQ 85). The bay holds its place in the
        # rhythm and a chimney stack stands on its axis, so there is nothing to draw. Missed when
        # the blind bay was introduced: this loop read `if door ... else window`, so `blind` fell
        # into the else and the CAD file drew the very collision the SVG had just stopped drawing
        # -- two surfaces disagreeing about one record, which is the class this package exists to
        # close. The selftest could not see it: it round-trips FINDINGS, not geometry.
        if r["kind"] == "door":
            # THE FLOOR IS THE RECTANGLE'S OWN SILL, not a `ground["grade_to_floor_ft"] * IN`
            # computed a second time at the top of this function. It is the same number by
            # derivation and reading it twice is how the two stop being the same number.
            sill, head = r["sill_in"], r["head_in"]
            x0, x1 = r["x0_in"], r["x1_in"]
            msp.add_lwpolyline([(x0, sill), (x1, sill), (x1, head), (x0, head)],
                               close=True, dxfattribs={"layer": opening})
            # THE DOORCASE DRESSES THE ENTRANCE AND NOTHING ELSE (WP-13.3, the lead's pass). A
            # door rect is any placed exterior door on this face since the elevation began
            # drawing the plan's placed openings -- the Tidewater plan seats three on its N wall
            # -- and only the rect carrying `entrance` is the composition's subject. The SVG
            # (`render_elevation._entrance`) read that flag from the day it existed; this loop
            # went on dressing every door with the casing and the sidelights, so the CAD file
            # drew a back door as a doorcase. One condition, the same one the SVG tests.
            if not r.get("entrance"):
                continue
            cw = ent["casing_width_in"]
            eh = ent.get("entablature_height_in") or ent["surround_height_above_opening_in"]
            msp.add_lwpolyline([(x0 - cw, sill), (x1 + cw, sill),
                                (x1 + cw, head + eh), (x0 - cw, head + eh)],
                               close=True, dxfattribs={"layer": sash})
            continue
        _win(r)

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
        out["sheets"]["section"] = dict(_forward(section), unexported=True)
        return out
    out["sheets"]["section"] = export_section_dxf(section, os.path.join(outdir, f"{pid}-section.dxf"))

    RF = _mod("roof", f"{ROOT}/build/roof.py")
    roof = RF.build_roof(copy.deepcopy(plan), parti, section=section)
    if "error" in roof:
        out["sheets"]["roof"] = dict(_forward(roof), unexported=True)
    else:
        out["sheets"]["roof"] = export_roof_dxf(roof, os.path.join(outdir, f"{pid}-roof.dxf"))

    EL = _mod("elevation", f"{ROOT}/build/elevation.py")
    elev = EL.build_elevation(copy.deepcopy(plan), parti,
                              section=section, roof=None if "error" in roof else roof)
    if "error" in elev:
        out["sheets"]["elevation"] = dict(_forward(elev), unexported=True)
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
    unevaluated = 0
    for rel in SELFTEST_PLANS:
        plan = json.load(open(os.path.join(ROOT, rel)))
        with tempfile.TemporaryDirectory() as td:
            out = export_all(copy.deepcopy(plan), td)
            # A REFUSED PLACEMENT IS COULD-NOT-EVALUATE AND IS NEITHER A PASS NOR A FAILURE
            # (WP-13.4, 16 Sep 2026). This filter read `v.get("refusal")`, which is this file's
            # MISSING-LIBRARY marker and has been since WP-5.1 -- the placement refusal is
            # `refused_placement`, and the contract says so in as many words because `refusal`
            # is what `app.py` maps to a 501. So the moment the exporter learned to refuse, both
            # shipped plans came back as export ERRORS and this selftest failed the build for a
            # reason that says nothing about a round trip: when there is no DXF, the round trip
            # was not exercised at all. Reported by name with the refusal's own sentences, and
            # the two states are counted apart -- collapsing an unjudged into a failure is the
            # same dishonesty as collapsing it into a pass, in the other direction.
            sheets = out.get("sheets", {})
            refused = {k: v for k, v in sheets.items() if v.get("refused_placement")}
            bad = {k: v for k, v in sheets.items()
                   if "error" in v and not v.get("refusal") and not v.get("refused_placement")}
            if "error" in out or bad:
                print(f"  FAIL {rel}: export errors: {out.get('error') or bad}")
                failures += 1
                continue
            if refused:
                why = next(iter(refused.values()))["refused_placement"]
                print(f"  COULD NOT EVALUATE {rel}: the placement is refused for "
                      f"{', '.join(why.get('facts') or ['an unnamed fact'])}, so "
                      f"{len(refused)} sheet(s) were not drawn and the round trip was not "
                      f"exercised. This is not a pass.")
                unevaluated += 1
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
    if unevaluated:
        print(f"\nCOULD NOT EVALUATE: {unevaluated} of {len(SELFTEST_PLANS)} plan(s) are "
              f"refused and were not round-tripped. This is not a pass.")
        return 3
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
