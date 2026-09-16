#!/usr/bin/env python3
"""The type's facts, verified on a PLACED record -- one reader for either engine's output.

**A LEAF, on `build/stacking.py`'s and `build/storeys.py`'s precedent, and it must stay one.**
`geometry.py` loads `plan_check.py` at import time and `structure.py` loads `geometry.py`. This
module is written onto `geometry_report.type_facts` from `geometry._disclose`, which BOTH record
writers call, and it is read back by `build/disclosures.py` for the plate and the bench and will
be read by `plan_check`'s drawn layer -- readers on different rungs of that one import ladder, so
a sibling import here closes a cycle. Everything it needs is on the record it is handed.

WHY IT EXISTS (WP-13.2, Phase 13 "the coherent sheet"). Lucas read the Tidewater sheet off the
prover and saw a powder room open to the drawing room along its south side. The cause is
`geometry_cp.COVERAGE = 0.97`, a FLOOR: 26.5 sf of the ground floor and 48.8 sf of the upper is
floor inside no room, and `wall_bands` draws an interior wall only where two rooms SHARE an edge,
so no wall is drawn across the hole. Nothing on the record said so. This module states the first
of the type's facts, TILING, as a measurement on the record; WP-13.3 makes it HARD on the prover
and adds the rest of the ruled precedence (declared stacks, bearing continuity, the hearth on
its flue), each under this same key as held / downgraded / unjudged.

HOW THE RESIDUAL VOID IS MEASURED. Each massing block is rasterised at `STEP_FT`, every room
rectangle on the level is painted onto it clipped to the block, and what is left unpainted is
floor nobody declared. It is the same raster `tests/test_sheet_coherence.py::_uncovered` reads,
cell for cell, so the gate and the record cannot count differently. A reserved void (OQ 55: a
courtyard, a piazza) is a room the record NAMES, drawn open on purpose, and it paints like any
other room -- this fact is about floor no record accounts for. The unpainted cells are then
grouped into connected strips and each strip is reported as its bounding rectangle with its own
area, so a reader can find the hole on the plate rather than being handed a total.

WHICH BLOCKS ARE JUDGED ON WHICH LEVEL. An element with no rooms on a level has no floor on that
level (WP-11.9's rule, spelled in `elements.elements_on_level`, which a leaf may not import), so
a block is judged on a level only where some room's rectangle has its CENTRE inside it. Without
that, the upper level of a house with a single-storey wing would report the whole wing as
residual void, which is WP-11.15's phantom-storey defect arriving one layer over.

UNJUDGED IS NOT PASSED. A record with no footprint, or with no placed level, gets `None` under
`tiling` rather than a zero: a zero here would read as "every level tiles its block" about a
house that was never placed.

THE OTHER THREE FACTS, AND HOW A LEAF JUDGES THEM (WP-13.3). `report(plan)` is called with the
plan alone, from a line in `geometry._disclose` this package may not touch, so nothing can be
injected and nothing may be imported. Each fact is judged from what the RECORD carries where the
record already carries the one spelling's verdict, and from arithmetic held to the one spelling
by a test where it does not:

  stacks   the verdict is READ off `geometry_report.stacking` -- `build/stacking.py`'s own
           `judge`, written by `_disclose` one line before this block, so the leaf re-derives
           nothing about kept and broken; what it adds is the containment FRACTION per claim,
           the number a reader wants beside the verdict.
  bearing  the capacity half is READ off `geometry_report.span_capacity.over_capacity`, which
           both record writers derive through `structure.span_check` and nothing else; the
           continuity half -- every upper bearing line stands on a ground bearing line -- is
           measured here, with `structure.wall_lines`' shared-edge test and
           `structure.bearing_lines`' grid test TRANSCRIBED beside the constants that name them,
           and `tests/test_typefacts.py` holds the transcription to the original on every
           shipped plan, line for line.
  hearth   each stated fire's room edge on its element's face, on a wall the massing puts a
           flue on. Which walls those are is `hearths.HEARTH_RULES`' table, transcribed as
           `FLUE_WALLS` and held to it by a test; the massing is read from
           `massings/catalog.json` directly, the way every other leaf in `build/` reads its
           own data file rather than reaching through a sibling.

Every fact answers in THREE states -- `held`, `downgraded`, `unjudged` -- and a fact the record
cannot state is `unjudged` with its reason, never `held`. `report()["status"]` is the four
verdicts in one place, which is what a refusal to draw (WP-13.4) reads.
"""
from __future__ import annotations

import json
import os
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The raster quantum. 0.1 ft is what the gate rasterises at; one cell is 0.01 sf, so a strip
# between two rooms is measured to the inch and a total is good to a tenth of a square foot.
STEP_FT = 0.1

# The residual void at or under which a level is said to TILE: the gate's own figure
# (`test_every_level_tiles_its_block`, `u > 0.05`) and `disclosures.TILED_SF`. Above it the
# tiling fact is DOWNGRADED and every strip is named, whatever floor the prover was asked for.
TILING_TOL_SF = 0.05

# TRANSCRIBED FROM `build/structure.py`, WHICH THIS LEAF MAY NOT IMPORT, AND HELD TO IT BY
# `tests/test_typefacts.py` (the defaults are read off the originals' own signatures there, and
# the line sets are compared on every shipped plan). Two rooms share a wall where their facing
# edges are within SHARED_EDGE_TOL_FT and the overlap along the wall exceeds MIN_SHARED_RUN_FT
# (`structure._shared_segment`); an interior wall is BEARING where its position is within
# BEARING_GRID_TOL_FT of a multiple of the bay module (`structure.bearing_lines`).
SHARED_EDGE_TOL_FT = 0.4
MIN_SHARED_RUN_FT = 1.0
BEARING_GRID_TOL_FT = 0.75

# The gate's figure for a breast standing on the block face its wall names
# (`test_every_hearth_breast_stands_on_a_wall_a_stack_stands_on`, `abs(face - block_face) > 0.1`).
HEARTH_FACE_TOL_FT = 0.1

# TRANSCRIBED FROM `hearths.HEARTH_RULES` -- which walls of the block a massing's `hearth` value
# puts a flue on -- and held to that table by a test, so a row added there and not here fails
# the build rather than silently making a fire unjudged. A value absent from this table is a
# massing this file does not read (a compound like "gable-end-paired or central-stack" is a
# statement about a type that admits both), and every fire under it is UNJUDGED by name.
FLUE_WALLS = {
    "gable-end-paired": ("E", "W"),
    "gable-end": ("E", "W"),
    "end": ("E", "W"),
    "central-stack": (),
    "central": (),
    "party-wall": ("E", "W"),
}
MASSING_CATALOG = os.path.join(ROOT, "massings", "catalog.json")

HELD, DOWNGRADED, UNJUDGED = "held", "downgraded", "unjudged"


def _blocks(plan):
    """The massing blocks a placement tiles, as `(x, y, w, h, name)`: `footprint.blocks` where
    the placer wrote them (`geometry.blocks_record`), else the one rectangle `(0, 0, W, H)`.
    Empty where the record has no footprint at all."""
    fp = plan.get("footprint") or {}
    out = []
    for b in (fp.get("blocks") or []):
        try:
            out.append((float(b["x_ft"]), float(b["y_ft"]), float(b["width_ft"]),
                        float(b["depth_ft"]), str(b.get("role") or b.get("id") or "block")))
        except (KeyError, TypeError, ValueError):
            continue
    if out:
        return out
    W, H = fp.get("width_ft"), fp.get("depth_ft")
    if W and H:
        return [(0.0, 0.0, float(W), float(H), "main")]
    return []


def _rect(room):
    g = (room or {}).get("geometry")
    if not g:
        return None
    try:
        return (float(g["x_ft"]), float(g["y_ft"]), float(g["width_ft"]), float(g["depth_ft"]))
    except (KeyError, TypeError, ValueError):
        return None


def _centre_inside(rect, block):
    cx, cy = rect[0] + rect[2] / 2.0, rect[1] + rect[3] / 2.0
    bx, by, bw, bh = block[:4]
    return bx <= cx <= bx + bw and by <= cy <= by + bh


def uncovered(rects, block, step=STEP_FT):
    """Square feet of `block` inside no rectangle of `rects`, and the strips it lies in.

    Returns `(area_sf, strips)`; each strip is `{x_ft, y_ft, width_ft, depth_ft, area_sf}`, the
    bounding rectangle of one connected run of unpainted cells (4-connected) with the cells'
    own area, which is what a reader needs to find it on the plate. The rasterisation is the
    gate's own, rounding each edge to the nearest cell, so the two agree to the cell."""
    bx, by, bw, bh = block[:4]
    nx, ny = int(round(bw / step)), int(round(bh / step))
    if nx <= 0 or ny <= 0:
        return 0.0, []
    cov = bytearray(nx * ny)
    for (x, y, w, h) in rects:
        x0, y0 = int(round((x - bx) / step)), int(round((y - by) / step))
        x1, y1 = int(round((x + w - bx) / step)), int(round((y + h - by) / step))
        for yy in range(max(0, y0), min(ny, y1)):
            row = yy * nx
            for xx in range(max(0, x0), min(nx, x1)):
                cov[row + xx] = 1
    cell = step * step
    strips = []
    seen = bytearray(nx * ny)
    total = 0
    for start in range(nx * ny):
        if cov[start] or seen[start]:
            continue
        # one connected strip: flood from this cell over unpainted, unseen neighbours
        q = deque([start])
        seen[start] = 1
        n = 0
        xlo = xhi = start % nx
        ylo = yhi = start // nx
        while q:
            i = q.popleft()
            n += 1
            ix, iy = i % nx, i // nx
            xlo, xhi = min(xlo, ix), max(xhi, ix)
            ylo, yhi = min(ylo, iy), max(yhi, iy)
            for j in ((i - 1) if ix > 0 else -1, (i + 1) if ix < nx - 1 else -1,
                      (i - nx) if iy > 0 else -1, (i + nx) if iy < ny - 1 else -1):
                if j >= 0 and not cov[j] and not seen[j]:
                    seen[j] = 1
                    q.append(j)
        total += n
        strips.append({"x_ft": round(bx + xlo * step, 2), "y_ft": round(by + ylo * step, 2),
                       "width_ft": round((xhi - xlo + 1) * step, 2),
                       "depth_ft": round((yhi - ylo + 1) * step, 2),
                       "area_sf": round(n * cell, 2)})
    strips.sort(key=lambda s: -s["area_sf"])
    return round(total * cell, 2), strips


def tiling(plan, step=STEP_FT):
    """Per placed level, the square feet of the level's massing block(s) inside no room
    rectangle, and the strips. `None` where there is nothing to judge -- no footprint, or no
    level carrying a placed room -- because a zero there would be a pass about a house that was
    never placed."""
    blocks = _blocks(plan)
    if not blocks:
        return None
    levels_out = []
    for i, lv in enumerate(plan.get("levels") or []):
        rects = [r for r in (_rect(rm) for rm in (lv.get("rooms") or [])) if r]
        if not rects:
            continue
        idx = lv.get("index")
        row = {"level": i if idx is None else idx, "id": lv.get("id"), "blocks": [],
               "uncovered_sf": 0.0}
        for blk in blocks:
            if not any(_centre_inside(r, blk) for r in rects):
                continue           # no room stands in this element on this level: no floor here
            sf, strips = uncovered(rects, blk, step)
            row["blocks"].append({"block": blk[4], "x_ft": blk[0], "y_ft": blk[1],
                                  "width_ft": blk[2], "depth_ft": blk[3],
                                  "rooms": sum(1 for r in rects if _centre_inside(r, blk)),
                                  "uncovered_sf": sf, "strips": strips})
            row["uncovered_sf"] = round(row["uncovered_sf"] + sf, 2)
        if row["blocks"]:
            levels_out.append(row)
    if not levels_out:
        return None
    total = round(sum(lv["uncovered_sf"] for lv in levels_out), 2)
    return {"step_ft": step, "levels": levels_out, "uncovered_sf": total,
            "note": ("Square feet of each placed level's massing block(s) lying inside no room "
                     "rectangle, rasterised at the stated step -- the same raster the gate reads. "
                     "A reserved void paints as a room; this is floor no record accounts for. "
                     + ("Every judged level tiles its block." if total == 0 else
                        f"{total} sf in all, in {sum(len(b['strips']) for lv in levels_out for b in lv['blocks'])} "
                        f"strip(s), each located."))}


def _level_index(i, lv):
    idx = lv.get("index")
    return i if idx is None else idx


def _placed_rects(plan):
    """`{level index: {room id: (x, y, w, h)}}` over every room carrying a rectangle -- the
    reserved voids included, because a stack may land on one and a bearing wall may bound one;
    readers that must leave them out do so by name."""
    out = {}
    for i, lv in enumerate(plan.get("levels") or []):
        idx = _level_index(i, lv)
        for rm in (lv.get("rooms") or []):
            r = _rect(rm)
            if r:
                out.setdefault(idx, {})[rm["id"]] = r
    return out


# ------------------------------------------------------------------ declared stacks
def _containment(a, b):
    """`(shared_sf, fraction of the SMALLER rectangle inside the larger)` -- the number
    `stacking.lands` compares against its own threshold; the threshold and the verdict stay
    there and are read off the record here."""
    ix = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    iy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    shared = max(0.0, ix) * max(0.0, iy)
    smaller = min(a[2] * a[3], b[2] * b[3])
    return round(shared, 2), (round(shared / smaller, 4) if smaller > 0 else None)


def stacks(plan):
    """Every `stacks_over` claim, with the verdict `build/stacking.py` wrote and the containment
    fraction beside it.

    THE VERDICT IS READ, NOT RE-DERIVED: `geometry_report.stacking` is `stacking.judge`'s own
    kept / broken / unjudged, written by `geometry._disclose` one line before this block, and a
    second transcription of `lands` here is how the search, the critic and the verifier would
    come to disagree about one stair. A record carrying no tally is UNJUDGED with that reason;
    a record declaring no stack is UNJUDGED with that one; nothing is held by absence."""
    tally = (plan.get("geometry_report") or {}).get("stacking")
    if not isinstance(tally, dict) or "kept" not in tally or "broken" not in tally:
        return {"status": UNJUDGED, "claims": [], "unjudged": [],
                "detail": ("the record carries no stacking tally (`geometry_report.stacking`), "
                           "so no claim can be judged here -- the verdict is stacking.judge's "
                           "and this leaf does not re-derive it")}
    rects = _placed_rects(plan)
    rows = []
    for verdict, entries in (("kept", tally.get("kept") or []), ("broken", tally.get("broken") or [])):
        for e in entries:
            lvl = e.get("level")
            a = (rects.get(lvl) or {}).get(e.get("room"))
            b = ((rects.get(lvl - 1) or {}).get(e.get("over")) if isinstance(lvl, int) else None)
            shared, frac = _containment(a, b) if a and b else (None, None)
            rows.append({"room": e.get("room"), "over": e.get("over"), "level": lvl,
                         "verdict": verdict, "shared_sf": shared, "fraction": frac})
    unjudged = [{"room": e.get("room"), "over": e.get("over"), "reason": e.get("reason")}
                for e in (tally.get("unjudged") or [])]
    broken = [r for r in rows if r["verdict"] == "broken"]
    kept = [r for r in rows if r["verdict"] == "kept"]
    if broken:
        status = DOWNGRADED
        detail = (f"{len(broken)} of {len(rows)} judged declared stack(s) are drawn clear of the "
                  f"room they name: " + "; ".join(
                      f"{r['room']} over {r['over']} at "
                      f"{(r['fraction'] or 0) * 100:.0f}% of the smaller room" for r in broken))
    elif kept:
        status = HELD
        detail = (f"every judged declared stack lands ({len(kept)} of {len(kept)}); "
                  f"{len(unjudged)} could not be judged")
    elif unjudged:
        status = UNJUDGED
        detail = (f"{len(unjudged)} declared stack(s) and none could be judged: "
                  + "; ".join(f"{u['room']} over {u['over']}: {u['reason']}" for u in unjudged))
    else:
        status = UNJUDGED
        detail = "this record declares no vertical stack, so there is nothing to hold"
    return {"status": status, "claims": rows, "unjudged": unjudged, "detail": detail}


# ------------------------------------------------------------------ bearing continuity
def _interior_lines(rects):
    """`{(axis, position)}` of the interior wall lines two placed rooms SHARE -- the test
    `structure._shared_segment` makes, transcribed (its tolerances are the named constants
    above and a test holds the line sets to the original on every shipped plan)."""
    ids = list(rects)
    out = set()
    for i, a in enumerate(ids):
        ax, ay, aw, ah = rects[a]
        for b in ids[i + 1:]:
            bx, by, bw, bh = rects[b]
            if abs((ax + aw) - bx) <= SHARED_EDGE_TOL_FT or abs((bx + bw) - ax) <= SHARED_EDGE_TOL_FT:
                x = bx if abs((ax + aw) - bx) <= SHARED_EDGE_TOL_FT else ax
                lo, hi = max(ay, by), min(ay + ah, by + bh)
                if hi - lo > MIN_SHARED_RUN_FT:
                    out.add(("x", round(x, 2)))
            if abs((ay + ah) - by) <= SHARED_EDGE_TOL_FT or abs((by + bh) - ay) <= SHARED_EDGE_TOL_FT:
                y = by if abs((ay + ah) - by) <= SHARED_EDGE_TOL_FT else ay
                lo, hi = max(ax, bx), min(ax + aw, bx + bw)
                if hi - lo > MIN_SHARED_RUN_FT:
                    out.add(("y", round(y, 2)))
    return out


def on_bay_grid(position_ft, bay_ft, tol=BEARING_GRID_TOL_FT):
    """`structure.bearing_lines`' own test, transcribed: an interior wall is bearing where it
    falls within `tol` of a multiple of the bay module."""
    return abs((position_ft / bay_ft) - round(position_ft / bay_ft)) * bay_ft <= tol


def bearing_lines(plan):
    """`{level index: sorted [(axis, position)]}` of the interior BEARING lines on each placed
    level, per massing element, reserved voids left out as the gate leaves them out. `None`
    where the record states no bay module or no block."""
    fp = plan.get("footprint") or {}
    bay = fp.get("bay_module_ft")
    blocks = _blocks(plan)
    if not bay or not blocks:
        return None
    out = {}
    for i, lv in enumerate(plan.get("levels") or []):
        idx = _level_index(i, lv)
        rooms = {rm["id"]: _rect(rm) for rm in (lv.get("rooms") or [])
                 if _rect(rm) and not (rm.get("geometry") or {}).get("void")}
        if not rooms:
            continue
        lines = set()
        for blk in blocks:
            here = {rid: r for rid, r in rooms.items() if _centre_inside(r, blk)}
            if not here:
                continue
            for axis, pos in _interior_lines(here):
                if on_bay_grid(pos, float(bay)):
                    lines.add((axis, pos))
        out[idx] = sorted(lines)
    return out


def bearing(plan):
    """Bearing continuity and span capacity, as the type states them and the gate reads them.

    CONTINUITY is measured here: every interior bearing line of the upper placed level stands
    within BEARING_GRID_TOL_FT of a ground bearing line on the same axis, and the upper level
    carries at least one -- an upper floor with none is one clear span of the whole block.
    CAPACITY is READ off `geometry_report.span_capacity.over_capacity`, which both record
    writers derive through `structure.span_check` and nothing else; `None` there is the
    catalogue being unreadable and is unjudged, never clear. A one-level house has no
    continuity to judge and says so.

    THE TWO HALVES ARE MEASURED ALIKE AND DECIDE DIFFERENTLY (ruled 16 Sep 2026). The
    returned `status` -- the thing WP-13.4's refusal reads -- is CONTINUITY's alone. Capacity
    is reported in `halves`, in `capacity_status`, in `spans_over_capacity` and in `detail`,
    and refuses nothing. `capacity_refuses` is on the row so a reader need not infer it."""
    lines = bearing_lines(plan)
    fp = plan.get("footprint") or {}
    over = ((plan.get("geometry_report") or {}).get("span_capacity") or {}).get("over_capacity")
    halves = {}
    detail = []
    if lines is None:
        halves["continuity"] = UNJUDGED
        detail.append("the record states no bay module or no block, so no bearing line can be read")
        unsupported, upper_lines, ground_lines = [], [], []
    else:
        placed = sorted(lines)
        if len(placed) < 2:
            halves["continuity"] = UNJUDGED
            detail.append("one placed level: there is no upper floor whose walls must continue down")
            unsupported, upper_lines, ground_lines = [], [], lines.get(placed[0], []) if placed else []
        else:
            g, u = placed[0], placed[1]
            ground_lines, upper_lines = lines[g], lines[u]
            unsupported = []
            for axis, pos in upper_lines:
                near = min((abs(pos - p) for a, p in ground_lines if a == axis), default=None)
                if near is None or near > BEARING_GRID_TOL_FT:
                    unsupported.append({"axis": axis, "position_ft": pos,
                                        "nearest_ground_ft": None if near is None else round(near, 2)})
            if not upper_lines:
                halves["continuity"] = DOWNGRADED
                detail.append(f"the upper floor carries no bearing line at all (ground has "
                              f"{len(ground_lines)}): every upper wall is a partition and the "
                              f"floor is one clear span")
            elif unsupported:
                halves["continuity"] = DOWNGRADED
                detail.append(f"{len(unsupported)} of {len(upper_lines)} upper bearing line(s) "
                              f"stand on no ground bearing line: " + "; ".join(
                                  f"{s['axis']}={s['position_ft']:g} ft" for s in unsupported))
            else:
                halves["continuity"] = HELD
                detail.append(f"every one of the {len(upper_lines)} upper bearing line(s) stands "
                              f"on a ground bearing line, within {BEARING_GRID_TOL_FT} ft")
    if over is None:
        halves["capacity"] = UNJUDGED
        detail.append("no span count on the record (`geometry_report.span_capacity`): the "
                      "framing catalogue was unreadable or the record was not placed by an engine")
    elif over:
        halves["capacity"] = DOWNGRADED
        detail.append(f"{over} clear span(s) exceed the capacity the framing tradition states "
                      f"(structure.span_check's own count)")
    else:
        halves["capacity"] = HELD
        detail.append("every clear span between bearing lines is within its framing capacity")
    # THE STATUS IS CONTINUITY'S ALONE -- RULED BY LUCAS, 16 SEP 2026: "capacity shouldn't
    # refuse a drawing -- continuity only".
    #
    # This returned DOWNGRADED if EITHER half was, so one over-capacity span refused a whole
    # sheet. Measured before the ruling was asked for, over the 16 shipped plan records and the
    # 21 partis instantiated against their own first native style: the capacity half alone
    # refused 33 of those 37. The 15 Sep precedence list names "bearing CONTINUITY on the bay
    # grid" and never capacity; `plan_check` grades an over-capacity span SERIOUS and not fatal
    # on the corpus's own words -- `structure.span_check`'s note asks for an intermediate
    # support or an engineered member, which is a floor framed differently and not a plan that
    # cannot be walked; and WP-11.12 put that distinction on the record in as many words.
    #
    # CAPACITY IS STILL MEASURED AND STILL REPORTED. It stays in `halves`, in `detail` and in
    # `spans_over_capacity`, and every surface that prints this fact prints it, because a fact
    # that stops DECIDING must not stop being SAID -- an unreported over-capacity span is the
    # fake-pass shape this corpus names first. What changed is only what refuses.
    #
    # An UNJUDGED continuity (a one-level house, or a record stating no bay module) leaves the
    # fact UNJUDGED even where capacity is downgraded: unjudged is not passed, and under
    # WP-13.4's contract it is not refused either.
    status = halves["continuity"]
    return {"status": status, "halves": halves, "bearing_lines": lines,
            "unsupported_upper_lines": unsupported, "spans_over_capacity": over,
            "capacity_status": halves["capacity"],
            "capacity_refuses": False,
            "grid_tol_ft": BEARING_GRID_TOL_FT, "detail": "; ".join(detail)}


# ------------------------------------------------------------------ the hearth on its flue
def flue_walls_of(plan):
    """`(walls, why)`: the block faces the plan's massing puts a flue on, or `(None, reason)`.
    Three reasons, as `hearths.flue_walls` gives them: no massing named, the massing states no
    hearth, or it states a form this table does not read."""
    mid = plan.get("massing")
    if not mid:
        return None, ("this plan names no massing, so there is no statement about where its "
                      "stacks stand")
    try:
        rows = json.load(open(MASSING_CATALOG, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"massings/catalog.json could not be read: {e.__class__.__name__}"
    m = next((r for r in rows if r.get("id") == mid), None)
    if m is None:
        return None, f"the massing {mid!r} is not in massings/catalog.json"
    stated = m.get("hearth")
    if not isinstance(stated, str):
        return None, f"the massing {mid!r} states no `hearth` at all"
    key = stated.strip().lower()
    if key not in FLUE_WALLS:
        return None, (f"the massing states hearth {stated!r}, which this file does not read: a "
                      f"compound is a statement about a type that admits both arrangements")
    return FLUE_WALLS[key], None


def hearth(plan):
    """Each stated fire's room edge on its element's face, on a wall the massing puts a flue on.

    A fire on a wall the massing puts no flue on -- a north hearth under paired gable stacks,
    any hearth under a central stack -- is UNJUDGED here by name: the prover pins nothing for
    it and `plan_check`'s hearth layer already reports it. A fire whose declared wall the
    placement put inboard of the face is DOWNGRADED with the figure. The shared flue (two
    centred breasts on one shaft) is not this fact's question and is not judged here."""
    walls, why = flue_walls_of(plan)
    blocks = _blocks(plan)
    rows = []
    for i, lv in enumerate(plan.get("levels") or []):
        idx = _level_index(i, lv)
        for rm in (lv.get("rooms") or []):
            fires = rm.get("hearth") or []
            if not fires:
                continue
            r = _rect(rm)
            for n, h in enumerate(fires):
                wall = (h.get("wall") or "").upper()
                row = {"level": idx, "room": rm["id"], "index": n, "wall": wall}
                if r is None:
                    row.update(verdict=UNJUDGED, why="the room is not placed")
                elif walls is None:
                    row.update(verdict=UNJUDGED, why=why)
                elif wall not in walls:
                    row.update(verdict=UNJUDGED,
                               why=(f"the massing puts its flues on {'/'.join(walls) or 'no exterior wall'}, "
                                    f"not on the {wall or 'unnamed'} wall this fire names, so the "
                                    f"prover pins nothing for it"))
                else:
                    blk = next((b for b in blocks if _centre_inside(r, b)), None)
                    if blk is None:
                        row.update(verdict=UNJUDGED, why="the room stands in no massing element")
                    else:
                        bx, by, bw, bh = blk[:4]
                        inboard = {"W": r[0] - bx, "E": (bx + bw) - (r[0] + r[2]),
                                   "S": r[1] - by, "N": (by + bh) - (r[1] + r[3])}[wall]
                        row["inboard_ft"] = round(inboard, 2)
                        if abs(inboard) <= HEARTH_FACE_TOL_FT:
                            row["verdict"] = HELD
                        else:
                            row.update(verdict=DOWNGRADED,
                                       why=(f"the placement puts this room's {wall} wall "
                                            f"{inboard:.2f} ft inboard of the element's {wall} "
                                            f"face: no exterior wall carries its flue"))
                rows.append(row)
    judged = [r for r in rows if r["verdict"] != UNJUDGED]
    bad = [r for r in rows if r["verdict"] == DOWNGRADED]
    if bad:
        status = DOWNGRADED
        detail = (f"{len(bad)} of {len(judged)} judged fire(s) stand off their flue wall: "
                  + "; ".join(f"{r['room']} {r['wall']} {r['inboard_ft']:g} ft inboard" for r in bad))
    elif judged:
        status = HELD
        detail = (f"every judged fire ({len(judged)}) stands on its flue wall; "
                  f"{len(rows) - len(judged)} unjudged")
    elif rows:
        status = UNJUDGED
        detail = ("this record states fires and none could be judged: "
                  + "; ".join(f"{r['room']} {r['wall'] or '?'}: {r['why']}" for r in rows))
    else:
        status = UNJUDGED
        detail = "this record states no hearth, so there is nothing to hold"
    return {"status": status, "flue_walls": list(walls) if walls else None,
            "massing_unreadable": why, "fires": rows, "detail": detail}


# ------------------------------------------------------------------ the block on the record
def tiling_status(t):
    """The tiling measurement's verdict: `None` (nothing to judge) is UNJUDGED; any judged
    level with more than TILING_TOL_SF of floor inside no room is DOWNGRADED, and the strips
    are already named on the measurement; otherwise HELD."""
    if t is None:
        return UNJUDGED
    worst = max((lv.get("uncovered_sf") or 0.0) for lv in t.get("levels") or []) \
        if t.get("levels") else 0.0
    return DOWNGRADED if worst > TILING_TOL_SF else HELD


def report(plan):
    """The block `geometry_report.type_facts` carries, written by `geometry._disclose` for both
    record writers: the four facts of the type (WP-13.3) and `status`, the four verdicts in one
    place, each `held`, `downgraded` or `unjudged`."""
    t = tiling(plan)
    ts = tiling_status(t)
    if t is not None:
        t["status"] = ts
        t["tolerance_sf"] = TILING_TOL_SF
    s, b, h = stacks(plan), bearing(plan), hearth(plan)
    status = {"tiling": ts, "stacks": s["status"], "bearing": b["status"], "hearth": h["status"]}
    down = sorted(k for k, v in status.items() if v == DOWNGRADED)
    unj = sorted(k for k, v in status.items() if v == UNJUDGED)
    return {"tiling": t, "stacks": s, "bearing": b, "hearth": h, "status": status,
            "note": ("The type's facts, measured on the placed record, each held, downgraded or "
                     "unjudged -- and unjudged is never held. `tiling` is the residual void per "
                     "placed level (`null` means it could not be evaluated); `stacks` reads "
                     "stacking.judge's verdict and adds the containment fraction; `bearing` "
                     "measures continuity and reads structure.span_check's count; `hearth` holds "
                     "each stated fire's wall to its element's face. "
                     + (f"DOWNGRADED: {', '.join(down)}. " if down else "No fact is downgraded. ")
                     + (f"Unjudged: {', '.join(unj)}." if unj else ""))}
