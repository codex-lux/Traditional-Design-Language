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
"""
from __future__ import annotations

from collections import deque

# The raster quantum. 0.1 ft is what the gate rasterises at; one cell is 0.01 sf, so a strip
# between two rooms is measured to the inch and a total is good to a tenth of a square foot.
STEP_FT = 0.1


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


def report(plan):
    """The block `geometry_report.type_facts` carries, written by `geometry._disclose` for both
    record writers. One fact today; WP-13.3 adds the rest under the same key."""
    return {"tiling": tiling(plan),
            "note": ("The type's facts, measured on the placed record. `tiling` is the residual "
                     "void per placed level; `null` means it could not be evaluated, never that "
                     "it passed.")}
