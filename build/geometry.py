#!/usr/bin/env python3
"""Geometry — place room rectangles in a footprint, both levels solved together.

Bay-grid slicing with a relaxation pass. Rooms snap to the structural bay module the parti
declares, because traditional houses ARE built on one: joists span it, windows centre on it,
the facade composes from it. Where a room cannot be made to fit on the grid the cut is allowed
off it, and every such relaxation is recorded as a compromise rather than hidden.

Levels are solved jointly, not sequentially: candidate layouts are generated for each level and
scored in pairs on vertical alignment — bearing lines that continue, wet rooms that stack, a
stair that lands where it left. That is a harder problem than constraining the upper floor to
the lower, and it finds arrangements the sequential method cannot.

When the rooms will not fit: grow the footprint first, then shrink rooms toward their bands,
then drop optional rooms. A room below its furniture minimum is a defect that survives the
building; a slightly larger house is just a slightly larger house.

  python3 build/geometry.py plans/<id>.json [--out plans/<id>.geo.json] [--svg dist/<id>.svg]
"""
from __future__ import annotations
import json, os, math, random, argparse, importlib.util, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _mod(n, p):
    # Delegates to build/modcache.py so a module is executed once per process
    # rather than once per call. Same signature, same standalone-script
    # behaviour; see that file's header for why (OQ 28). Loaded by path here
    # because this file is itself usually loaded by path, so `build/` is not
    # necessarily on sys.path yet.
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(n, p)
PC = _mod("plan_check", f"{ROOT}/build/plan_check.py")
C = PC.load_corpus()

DIRS = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0),
        "NE": (1, 1), "NW": (-1, 1), "SE": (1, -1), "SW": (-1, -1)}
OUTDOOR = {"outdoor"}

# ---------------------------------------------------------------- helpers
def is_indoor(rtype): return C["rooms"].get(rtype, {}).get("function_class") not in OUTDOOR
def band(rtype):
    d = C["rooms"].get(rtype, {}).get("dimensions", {})
    return (d.get("area_sf") or [40, 900])

def snap(v, module, tol):
    """Nearest bay line, unless that would move the cut more than tol."""
    s = round(v / module) * module
    return (s, 0.0) if abs(s - v) <= tol else (v, abs(s - v))

# ---------------------------------------------------------------- slicing
def bias(room, axis):
    """Directional pull from the room's declared exterior walls: +1 north/east, -1 south/west."""
    b = 0.0
    for w in (room.get("exterior_walls") or []):
        dx, dy = DIRS.get(w, (0, 0))
        b += (dy if axis == "y" else dx)
    return b

def partition(rooms, axis, rng):
    """Split into two groups: the LOW group goes south or west, so it must be seeded with the
    rooms pulled that way. Grow each group through the door graph, so a cut severs as few
    connections as possible — a plan whose adjacencies survive the slicing is the whole point."""
    ids = {r["id"] for r in rooms}
    doors = {r["id"]: {d["to"] for d in (r.get("doors") or []) if d["to"] in ids} for r in rooms}
    # bias ASCENDING: most negative (south/west) first, because lo is placed low
    ranked = sorted(rooms, key=lambda r: (bias(r, axis), -r["_area"], r["id"]))
    total = sum(r["_area"] for r in ranked)
    target = total * rng.uniform(0.44, 0.56)
    lo, taken, acc = [], set(), 0.0
    seed = ranked[rng.randrange(min(3, len(ranked)))]      # vary the seed, or every run is identical
    lo.append(seed); taken.add(seed["id"]); acc = seed["_area"]
    while acc < target and len(taken) < len(ranked):
        # prefer a room already connected to the group AND pulled the right way
        best, bs = None, None
        for r in ranked:
            if r["id"] in taken: continue
            conn = len(doors[r["id"]] & taken)
            sc = (-conn, bias(r, axis), -r["_area"])
            if bs is None or sc < bs: best, bs = r, sc
        if best is None: break
        lo.append(best); taken.add(best["id"]); acc += best["_area"]
    hi = [r for r in ranked if r["id"] not in taken]
    if not lo or not hi:
        mid = max(1, len(ranked) // 2); lo, hi = ranked[:mid], ranked[mid:]
    return lo, hi

def spanning(rooms, axis):
    """A room with exterior walls on OPPOSITE sides has to run the full depth or width — which
    is exactly what a centre passage is, and why slicing it like any other room produces a
    treemap instead of a plan."""
    pairs = (("S", "N") if axis == "y" else ("W", "E"))
    for r in rooms:
        # Only CIRCULATION spans. A porch with three exterior walls wants the south edge,
        # not a slab through the middle of the house.
        if C["rooms"].get(r["type"], {}).get("function_class") != "circulation": continue
        w = set(r.get("exterior_walls") or [])
        if pairs[0] in w and pairs[1] in w: return r
    return None

def slice_rect(rooms, x, y, w, h, module, tol, rng, out, relax, depth=0):
    if not rooms: return
    if len(rooms) == 1:
        r = rooms[0]; out[r["id"]] = (round(x, 2), round(y, 2), round(w, 2), round(h, 2)); return

    # --- a spanning room becomes a slab across the whole rectangle, and the rest is sliced
    # either side of it. This is the move that turns a treemap into a plan.
    if len(rooms) > 2:
        sp = spanning(rooms, "y")
        if sp and h > w * 0.55:
            sw = max(module * 0.7, min(w * 0.4, sp["_area"] / h))
            sws, d = snap(sw, module, tol)
            if d: relax.append(round(d, 2))
            sw = max(module * 0.6, min(w * 0.45, sws)) * rng.uniform(0.94, 1.10)
            rest = [r for r in rooms if r["id"] is not sp["id"] and r["id"] != sp["id"]]
            west = [r for r in rest if bias(r, "x") < 0]
            east = [r for r in rest if r not in west]
            # let a borderline room cross the cut sometimes, or the search has nothing to explore
            for r in list(rest):
                if abs(bias(r, "x")) < 0.5 and rng.random() < 0.35:
                    (east if r in west else west).append(r)
                    (west if r in west else east).remove(r)
            if not west or not east:
                west, east = partition(rest, "x", rng)
            aw = sum(r["_area"] for r in west); ae = sum(r["_area"] for r in east)
            wfrac = aw / (aw + ae) if (aw + ae) else 0.5
            if "centre" in (sp["type"] or "") or "center" in (sp["type"] or ""):
                wfrac = (wfrac + 0.5) / 2.0      # a centre passage is named for where it goes
            wfrac = min(0.78, max(0.22, wfrac + rng.uniform(-0.07, 0.07)))
            rem = w - sw
            wwid, dd = snap(rem * wfrac, module, tol)
            if dd: relax.append(round(dd, 2))
            wwid = max(module * 0.6, min(rem - module * 0.6, wwid))
            out[sp["id"]] = (round(x + wwid, 2), round(y, 2), round(sw, 2), round(h, 2))
            slice_rect(west, x, y, wwid, h, module, tol, rng, out, relax, depth + 1)
            slice_rect(east, x + wwid + sw, y, rem - wwid, h, module, tol, rng, out, relax, depth + 1)
            return
        sp = spanning(rooms, "x")
        if sp and w > h * 0.55:
            sh = max(module * 0.5, min(h * 0.4, sp["_area"] / w))
            rest = [r for r in rooms if r["id"] != sp["id"]]
            south = [r for r in rest if bias(r, "y") < 0]
            north = [r for r in rest if r not in south]
            if not south or not north: south, north = partition(rest, "y", rng)
            a_s = sum(r["_area"] for r in south); a_n = sum(r["_area"] for r in north)
            sfrac = a_s / (a_s + a_n) if (a_s + a_n) else 0.5
            rem = h - sh
            shgt = max(module * 0.5, min(rem - module * 0.5, rem * sfrac))
            out[sp["id"]] = (round(x, 2), round(y + shgt, 2), round(w, 2), round(sh, 2))
            slice_rect(south, x, y, w, shgt, module, tol, rng, out, relax, depth + 1)
            slice_rect(north, x, y + shgt + sh, w, rem - shgt, module, tol, rng, out, relax, depth + 1)
            return

    axis = "x" if w >= h else "y"
    if abs(w - h) < module * 0.9 and rng.random() < 0.45: axis = "y" if axis == "x" else "x"
    lo, hi = partition(rooms, axis, rng)
    a_lo = sum(r["_area"] for r in lo); a_tot = a_lo + sum(r["_area"] for r in hi)
    frac = a_lo / a_tot if a_tot else 0.5
    if axis == "x":
        cut = w * frac
        s, d = snap(x + cut, module, tol)
        cut = max(module * 0.6, min(w - module * 0.6, s - x))
        if d: relax.append(round(d, 2))
        slice_rect(lo, x, y, cut, h, module, tol, rng, out, relax, depth + 1)      # lo goes west
        slice_rect(hi, x + cut, y, w - cut, h, module, tol, rng, out, relax, depth + 1)
    else:
        cut = h * frac
        s, d = snap(y + cut, module, tol)
        cut = max(module * 0.6, min(h - module * 0.6, s - y))
        if d: relax.append(round(d, 2))
        slice_rect(lo, x, y, w, cut, module, tol, rng, out, relax, depth + 1)      # lo goes south
        slice_rect(hi, x, y + cut, w, h - cut, module, tol, rng, out, relax, depth + 1)

# ---------------------------------------------------------------- scoring one level
def level_score(rects, rooms):
    """Area error, aspect sanity, exterior-wall satisfaction."""
    s = 0.0
    for r in rooms:
        x, y, w, h = rects[r["id"]]
        got, want = w * h, r["_area"]
        s += abs(got - want) / max(want, 1) * 10
        ar = max(w, h) / max(min(w, h), 0.1)
        if ar > 2.6: s += (ar - 2.6) * 6
        lo, hi = band(r["type"])
        if got < lo * 0.85: s += 12
    return s

def exterior_score(rects, rooms, W, H, tol=0.6):
    s = 0.0
    for r in rooms:
        want = set(r.get("exterior_walls") or [])
        if not want: continue
        x, y, w, h = rects[r["id"]]
        have = set()
        if y <= tol: have.add("S")
        if y + h >= H - tol: have.add("N")
        if x <= tol: have.add("W")
        if x + w >= W - tol: have.add("E")
        missing = {d for d in want if d in "NSEW"} - have
        s += len(missing) * 14
    return s

def adjacency_score(rects, rooms, plan_rooms):
    """Rooms with a door between them should actually touch."""
    s = 0.0
    byid = {r["id"]: r for r in rooms}
    for r in plan_rooms:
        if r["id"] not in rects: continue
        for d in (r.get("doors") or []):
            t = d["to"]
            if t == "exterior" or t not in rects: continue
            if not touching(rects[r["id"]], rects[t]): s += 14
    return s / 2.0

def touching(a, b, tol=0.35):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    if ax + aw < bx - tol or bx + bw < ax - tol: return False
    if ay + ah < by - tol or by + bh < ay - tol: return False
    ox = min(ax + aw, bx + bw) - max(ax, bx)
    oy = min(ay + ah, by + bh) - max(ay, by)
    return (ox > tol and oy > -tol) or (oy > tol and ox > -tol)

# ---------------------------------------------------------------- WP-2.2 compositional scoring
# entrance_faces (brief/plan context, 8-point compass) mapped down to this file's 4-wall model
# (N/S/E/W is all exterior_score/window placement ever used) -- a diagonal entrance is honoured
# by either of its two adjacent cardinals, not forced onto one arbitrarily.
_ENTRANCE_WALLS = {
    "N": {"N"}, "S": {"S"}, "E": {"E"}, "W": {"W"},
    "NE": {"N", "E"}, "SE": {"S", "E"}, "SW": {"S", "W"}, "NW": {"N", "W"},
}
_OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

def entrance_walls(plan):
    ef = (plan.get("context") or {}).get("entrance_faces")
    return _ENTRANCE_WALLS.get(ef, set())

def _touches_wall(rect, wall, W, H, tol=0.6):
    x, y, w, h = rect
    if wall == "S": return y <= tol
    if wall == "N": return y + h >= H - tol
    if wall == "W": return x <= tol
    if wall == "E": return x + w >= W - tol
    return False

def _dist_from_walls(rect, walls, W, H):
    """How far a room's near edge sits from the given wall set, in feet -- 0 if it touches one
    of them. Used to test the ceremonial sequence gets spatially deeper, not just door-connected."""
    x, y, w, h = rect
    best = None
    for wall in walls:
        d = {"S": y, "N": H - (y + h), "W": x, "E": W - (x + w)}[wall]
        best = d if best is None else min(best, d)
    return max(0.0, best) if best is not None else 0.0

def entrance_score(rects, rooms, W, H, ewalls):
    """WP-2.2: the entry-porch (function_class 'threshold') and whatever it opens into
    (typically an entrance-hall or centre-passage, function_class 'circulation') must sit on
    the entrance front. This is the specific bug PLAN-OF-ACTION.md names -- 'the current
    rendered Tidewater plan puts the portico inside the footprint' -- and it is weighted heavily
    enough (on the scale fatal-tier findings use elsewhere: compose.py's own SEV_W gives a
    fatal 100) that no candidate with the porch off the entrance wall can win against one that
    has it right, across the 250-candidate search."""
    if not ewalls: return 0.0
    s = 0.0
    byid = {r["id"]: r for r in rooms}
    for r in rooms:
        if r["id"] not in rects: continue
        fc = C["rooms"].get(r["type"], {}).get("function_class")
        if fc != "threshold": continue
        rect = rects[r["id"]]
        if not any(_touches_wall(rect, w, W, H) for w in ewalls):
            s += 100.0
        # whatever this threshold room opens into should also reach the entrance front,
        # directly or by being the room that receives the sequence (a hall, not a closet).
        for d in (r.get("doors") or []):
            t = d["to"]
            if t not in rects or t not in byid: continue
            tfc = C["rooms"].get(byid[t]["type"], {}).get("function_class")
            if tfc != "circulation": continue
            if not any(_touches_wall(rects[t], w, W, H) for w in ewalls):
                s += 40.0
    return s

def principal_and_service_score(rects, rooms, W, H, ewalls):
    """WP-2.2: principal rooms (drawing-room, parlor, living-room, dining-room -- function_class
    public/living/dining) want the entrance front; service rooms (kitchen, pantry, laundry,
    mudroom -- function_class service/work) want the wall opposite it. Soft, unlike
    entrance_score -- not every principal room can reach the front of a real house, and this is
    a preference the search should trade off against area and adjacency, not a rejection."""
    if not ewalls: return 0.0
    rear = {_OPPOSITE[w] for w in ewalls if w in _OPPOSITE}
    s = 0.0
    for r in rooms:
        if r["id"] not in rects: continue
        fc = C["rooms"].get(r["type"], {}).get("function_class")
        rect = rects[r["id"]]
        if fc in ("public", "living", "dining"):
            if not any(_touches_wall(rect, w, W, H) for w in ewalls): s += 3.5
        elif fc in ("service", "work"):
            if not any(_touches_wall(rect, w, W, H) for w in rear): s += 2.0
            if any(_touches_wall(rect, w, W, H) for w in ewalls): s += 3.0  # service ON the front is worse than merely not-rear
    return s

def ceremonial_score(rects, rooms, W, H, ewalls):
    """WP-2.2: 'the ceremonial sequence approach -> porch -> passage -> principal room is a
    path of increasing privacy rank with no backtracking.' Checked geometrically, not just by
    the door graph (which the parti already fixed at compose time and this solver cannot
    change): a principal room reached through a threshold room should sit spatially DEEPER
    into the plan (farther from the entrance wall) than the threshold room it passes through,
    door hop by door hop, for exactly the hops privacy_rank actually rises. Scoped to the direct
    porch-to-hall-to-principal-room chain PLAN-OF-ACTION.md's own acceptance example names, not
    an arbitrary-length whole-plan traversal -- see docs/geometry.md for what that would take."""
    if not ewalls: return 0.0
    byid = {r["id"]: r for r in rooms}
    s = 0.0
    for r in rooms:
        if r["id"] not in rects: continue
        rank = C["rooms"].get(r["type"], {}).get("privacy_rank")
        if rank is None: continue
        d_here = _dist_from_walls(rects[r["id"]], ewalls, W, H)
        for door in (r.get("doors") or []):
            t = door["to"]
            if t not in rects or t not in byid: continue
            trank = C["rooms"].get(byid[t]["type"], {}).get("privacy_rank")
            if trank is None or trank <= rank: continue        # only check rank-increasing hops
            d_there = _dist_from_walls(rects[t], ewalls, W, H)
            if d_there < d_here - 0.6:                          # backtrack: the deeper room is nearer the street
                s += 6.0 * (trank - rank)
    return s

def centre_hall_symmetry_score(rects, rooms, W, H, tol_frac=0.18):
    """WP-2.2: 'on a centre-hall parti the plan is symmetric about the passage to a stated
    tolerance.' Gated on the same spanning-circulation-room test the bay-grid slicer already
    uses for a centre passage (spanning() in this file) -- only a plan that actually has one is
    a centre-hall parti at all. For each room on one side of the spanning room's centreline,
    reward a same-type room roughly mirrored to the other side within tol_frac of the
    footprint's own width; a lone (unmirrored) room pays a small, not punitive, penalty --
    plenty of correct centre-hall plans have one asymmetric service room."""
    sp = spanning(rooms, "y") or spanning(rooms, "x")
    if not sp or sp["id"] not in rects: return 0.0
    sx, sy, sw, sh = rects[sp["id"]]
    axis_x = sw < sh  # a passage spanning north-south splits the plan left/right (mirror in x)
    centre = sx + sw / 2 if axis_x else sy + sh / 2
    tol = (W if axis_x else H) * tol_frac
    others = [r for r in rooms if r["id"] != sp["id"] and r["id"] in rects]
    used = set()
    s = 0.0
    for r in others:
        if r["id"] in used: continue
        rx, ry, rw, rh = rects[r["id"]]
        rc = rx + rw / 2 if axis_x else ry + rh / 2
        best, bd = None, None
        for o in others:
            if o["id"] == r["id"] or o["id"] in used or o["type"] != r["type"]: continue
            ox, oy, ow, oh = rects[o["id"]]
            oc = ox + ow / 2 if axis_x else oy + oh / 2
            # a mirror pair sits on opposite sides of the centreline at roughly equal distance
            if (rc - centre) * (oc - centre) >= 0: continue
            d = abs(abs(rc - centre) - abs(oc - centre))
            if bd is None or d < bd: best, bd = o, d
        if best and bd <= tol:
            used.add(r["id"]); used.add(best["id"])
        else:
            s += 1.5
    return s

# ---------------------------------------------------------------- joint scoring
def vertical_score(g, u, groundrooms, upperrooms, plan):
    """The reason both levels are solved together: bearing lines, stacks, and the stair."""
    if not u: return 0.0, []
    s, notes = 0.0, []
    gx = sorted({round(v[0], 1) for v in g.values()} | {round(v[0] + v[2], 1) for v in g.values()})
    gy = sorted({round(v[1], 1) for v in g.values()} | {round(v[1] + v[3], 1) for v in g.values()})
    off = 0
    for rid, (x, y, w, h) in u.items():
        for val, lines in ((x, gx), (x + w, gx), (y, gy), (y + h, gy)):
            if not any(abs(val - L) <= 0.75 for L in lines): off += 1
    s += off * 2.0
    if off: notes.append(f"{off} upper wall line(s) do not continue to a wall below; each is a transfer beam.")
    gt = {r["id"]: r for r in groundrooms}
    wet_g = {rid: v for rid, v in g.items() if set(gt.get(rid, {}).get("fixtures") or [])}
    ut = {r["id"]: r for r in upperrooms}
    for rid, (x, y, w, h) in u.items():
        if not set(ut.get(rid, {}).get("fixtures") or []): continue
        cx, cy = x + w / 2, y + h / 2
        over = any(vx <= cx <= vx + vw and vy <= cy <= vy + vh for (vx, vy, vw, vh) in wet_g.values())
        if not over: s += 8; notes.append(f"{ut[rid].get('name') or rid} sits over no wet room; its stack has nowhere to land.")
    for rid in u:
        if C["rooms"].get(ut.get(rid, {}).get("type"), {}).get("function_class") != "circulation": continue
        st = next((k for k in g if C["rooms"].get(gt.get(k, {}).get("type"), {}).get("id") == "stair-hall"), None)
    return s, notes

# ---------------------------------------------------------------- the solve
def lot_usable_width_ft(plan):
    """WP-2.4. Same rule as build/compose.py's own lot_usable_width_ft -- kept as a second,
    independent copy rather than a cross-module import, because geometry.py is loaded
    standalone via _mod() throughout this codebase (see main(), and every test's
    geometry_module fixture) and importing compose.py into it would pull in the composer's
    own heavy corpus load for a four-line helper. If this drifts from compose.py's version,
    docs/site.md says so and names both call sites."""
    site = plan.get("site") or {}
    ctx = plan.get("context") or {}
    lot_width = site.get("lot_width_ft")
    if lot_width is None: lot_width = ctx.get("lot_width_ft")
    if lot_width is None: return None
    side = site.get("setback_side_ft") or 0
    return max(0.0, lot_width - 2 * side)

def prepare_rooms(plan):
    """Indoor rooms per level, each carrying the `_area` its own record declares.

    Shared with build/solver.py (WP-2.3) so both engines place the same set of rooms
    against the same target areas. Returns (prep, levels) or (None, levels) when there
    is no ground level."""
    levels = {lv.get("index", i): lv for i, lv in enumerate(plan["levels"])}
    prep = {}
    for idx, lv in levels.items():
        rs = []
        for r in lv["rooms"]:
            if not is_indoor(r["type"]): continue
            q = dict(r); q["_area"] = (r.get("width_ft") or 10) * (r.get("length_ft") or 12)
            rs.append(q)
        prep[idx] = rs
    return (prep if 0 in prep else None), levels


# Footprint depth from the MASSING's own pile: a single-pile house is one room deep and a
# double-pile two, and inventing an aspect ratio instead produces a house that is the right
# area and the wrong shape.
PILE = {"single-pile": 22.0, "one-and-a-half-pile": 28.0, "double-pile": 36.0,
        "triple-pile": 46.0, "variable": 32.0}


def derive_footprint(plan, parti, prep):
    """Bay module, bay count and footprint, with the lot cap and the growth ordering.

    Extracted from solve() in WP-2.3 so the CP-SAT solver derives its footprint from
    exactly the same rule rather than a second copy that could drift: decision #11's
    "grow the footprint before compromising a room" is a settled decision, and it should
    have one implementation. Behaviour is verbatim what solve() did inline; the pinned
    relaxation count in tests/test_geometry.py is what proves it.

    Returns a dict of footprint facts, or one carrying `error` when the lot cannot hold
    even the minimum two bays."""
    bay = ((parti or {}).get("scaling") or {}).get("bay_module_ft") or 10.0
    catalog_maxbay = ((parti or {}).get("scaling") or {}).get("max_bay_count") or 7
    maxbay = catalog_maxbay
    # WP-2.4: compose.py's own footprint() estimate already caps candidate selection by lot
    # width, but this solver derives its own bay count independently (from the massing's pile
    # depth, not from compose.py's estimate) and is the placement that actually gets rendered
    # -- so it needs the same cap, or a plan that "fit the lot" in compose.py's estimate can
    # still be solved wider than its own lot right here, and the SVG lot line would be a lie
    # about the building drawn inside it. Unlike the parti's own catalogue max_bay_count --
    # which the growth loop below is already allowed to exceed by up to 3 bays rather than
    # leave a room too deep -- the lot is a physical fact, not a diagram convention, so it
    # bounds that growth loop too (see growth_ceiling below), not just the starting guess.
    lot_usable = lot_usable_width_ft(plan)
    lot_maxbay = None
    if lot_usable is not None:
        lot_maxbay = max(1, int(lot_usable // bay))
        maxbay = min(maxbay, lot_maxbay)
        if lot_maxbay < 2:
            return {"error": f"lot too narrow: {lot_usable:.0f} ft usable width after side setbacks "
                              f"cannot hold even this diagram's minimum 2 bays ({2*bay:.0f} ft) at its "
                              f"{bay:.0f} ft bay module."}
    a0 = sum(r["_area"] for r in prep[0])
    au = sum(r["_area"] for r in prep.get(1, []))
    m = C["massings"].get(plan.get("massing") or "", {})
    target_depth = PILE.get(m.get("depth_rooms"), 32.0)
    need = max(a0, au)
    grown, bays = [], max(2, min(maxbay, round((need / target_depth) / bay)))
    # growth_ceiling: the catalogue allows growing 3 bays past its own stated max before this
    # loop gives up and lets a room go deep instead; the lot (when stated) still bounds that,
    # since it can allow fewer bays than the catalogue max, not more.
    growth_ceiling = catalog_maxbay + 3
    if lot_maxbay is not None: growth_ceiling = min(growth_ceiling, lot_maxbay)
    while True:
        W = bays * bay
        H = need / W
        # grow the footprint before compromising a room — the stated infeasibility ordering
        if H <= target_depth * 1.18 or bays >= growth_ceiling: break
        bays += 1; grown.append(bays)
    while bays > 2 and need / ((bays - 1) * bay) <= target_depth * 1.18:
        bays -= 1
    W = round(bays * bay, 2); H = round(need / W, 2)
    return {"bay": bay, "bays": bays, "W": W, "H": H, "slack": (W * H) - max(a0, au),
            "grown": grown, "lot_usable": lot_usable, "lot_maxbay": lot_maxbay,
            "catalog_maxbay": catalog_maxbay, "growth_ceiling": growth_ceiling,
            "target_depth": target_depth, "need": need}


def under_band(rects_by_level, prep):
    """Rooms this layout placed below the floor of their own catalogue band.

    OQ 32, ruled 24 Aug 2026. `level_score` charges a flat 12 points for a room under its band
    and a candidate can win the search while paying it, so the spec Colonial's dining room comes
    out at 91 sf against a 122 sf floor -- on every seed. Nothing reported it: the plan RECORD
    still says 12 x 12, only the placement shrinks the room, and `plan_check.py` never reads
    `room.geometry`, so no layer of the critic was looking at the number that changed.

    The ruling was to report it here rather than to make the search refuse (which could leave a
    brief with no candidate and no explanation) or to teach the critic to read geometry (a much
    larger change every plan layer would feel). The search keeps its freedom to trade a room's
    size against everything else, which is what a heuristic is for. It stops doing it silently."""
    out = []
    for idx, rects in rects_by_level.items():
        for r in prep.get(idx, []):
            rect = rects.get(r["id"])
            if not rect: continue
            got = rect[2] * rect[3]
            lo, _hi = band(r["type"])
            floor = lo * 0.85
            if got < floor - 0.5:
                out.append({"room": r["id"], "name": r.get("name") or r["id"], "type": r["type"],
                            "placed_sf": round(got), "band_floor_sf": round(floor),
                            "short_by_pct": round(100 * (floor - got) / floor)})
    return sorted(out, key=lambda d: -d["short_by_pct"])


def write_record(plan, levels, ground, upper, fp, report):
    """Write coordinates, footprint and geometry_report back into the plan record.

    Shared with build/solver.py so both engines emit an identically-shaped record --
    the drawing is a render of the data (decision #11), and two engines writing two
    slightly different records would make that guarantee engine-dependent."""
    for idx, lv in levels.items():
        src = ground if idx == 0 else (upper if idx == 1 else {})
        for r in lv["rooms"]:
            if r["id"] in src:
                x, y, w, h = src[r["id"]]
                r["geometry"] = {"x_ft": x, "y_ft": y, "width_ft": round(w, 2), "depth_ft": round(h, 2),
                                 "area_sf": round(w * h)}
    plan["footprint"] = {"width_ft": fp["W"], "depth_ft": fp["H"], "bays": fp["bays"],
                         "bay_module_ft": fp["bay"], "area_sf": round(fp["W"] * fp["H"]),
                         "slack_sf": round(fp["slack"])}
    if fp.get("lot_usable") is not None:
        plan["footprint"]["lot_usable_width_ft"] = round(fp["lot_usable"], 1)
    plan["geometry_report"] = report
    return plan


def solve(plan, parti=None, candidates=250, seed=7):
    rng = random.Random(seed)
    prep, levels = prepare_rooms(plan)
    if prep is None: return {"error": "no ground level"}
    fp = derive_footprint(plan, parti, prep)
    if "error" in fp: return {"error": fp["error"]}
    bay, bays, W, H = fp["bay"], fp["bays"], fp["W"], fp["H"]
    grown, lot_maxbay, catalog_maxbay = fp["grown"], fp["lot_maxbay"], fp["catalog_maxbay"]
    tol = bay * 0.28                                    # the relaxation allowance

    # WP-2.2: composition_parti (the style's kit) and entrance_faces (the plan's own context)
    # feed the compositional scoring terms below. composition_parti is read for completeness
    # and future use, per PLAN-OF-ACTION.md's task list -- as of this package no style's kit
    # actually specifies it (status: empty everywhere), so nothing here branches on its value
    # yet; entrance_faces is what every term below actually keys off, and it is already on
    # every plan this solver has ever been run against (context.entrance_faces).
    composition_parti = ((C["kits"].get(plan.get("style") or "") or {}).get("slots") or {}).get("composition_parti")
    ewalls = entrance_walls(plan)

    best = None
    for _ in range(candidates):
        gr, grelax = {}, []
        slice_rect(copy.deepcopy(prep[0]), 0, 0, W, H, bay, tol, rng, gr, grelax)
        sg = (level_score(gr, prep[0]) + exterior_score(gr, prep[0], W, H) + adjacency_score(gr, prep[0], levels[0]["rooms"])
              + entrance_score(gr, prep[0], W, H, ewalls) + principal_and_service_score(gr, prep[0], W, H, ewalls)
              + ceremonial_score(gr, prep[0], W, H, ewalls) + centre_hall_symmetry_score(gr, prep[0], W, H))
        ur, urelax = {}, []
        if prep.get(1):
            slice_rect(copy.deepcopy(prep[1]), 0, 0, W, H, bay, tol, rng, ur, urelax)
            su = (level_score(ur, prep[1]) + exterior_score(ur, prep[1], W, H) + adjacency_score(ur, prep[1], levels[1]["rooms"])
                  + centre_hall_symmetry_score(ur, prep[1], W, H))
        else: su = 0.0
        vs, vnotes = vertical_score(gr, ur, prep[0], prep.get(1, []), plan)
        tot = sg + su + vs + 1.5 * len(grelax + urelax)
        if best is None or tot < best["score"]:
            best = {"score": round(tot, 1), "ground": gr, "upper": ur, "vnotes": vnotes,
                    "relaxations": grelax + urelax, "sg": round(sg, 1), "su": round(su, 1), "sv": round(vs, 1)}

    # --- write coordinates back into the plan
    rel = best["relaxations"]
    report = {
        "score": best["score"], "ground_score": best["sg"], "upper_score": best["su"], "vertical_score": best["sv"],
        "bays_grown": grown,
        "lot_capped": (lot_maxbay is not None and lot_maxbay < catalog_maxbay),
        "relaxations": {"count": len(rel), "max_off_grid_ft": round(max(rel), 2) if rel else 0,
                        "note": ("Cuts taken off the bay line to make a room fit. Each one is a joist run that "
                                 "does not land on a bearing line and a window bay that will not centre." if rel
                                 else "Every cut landed on a bay line.")},
        "vertical": best["vnotes"] or ["Every upper wall continues to a wall below and every stack lands."],
        "reading": ("Ground and upper were solved together and scored as a pair, so an upper layout that would "
                    "score better alone is rejected when it leaves walls unsupported.")}
    ub = under_band({0: best["ground"], 1: best["upper"]}, prep)
    report["under_band"] = {
        "count": len(ub), "rooms": ub,
        "note": ("Rooms placed below the floor of their own catalogue band. The search is allowed to "
                 "trade a room's size against everything else it is scoring, and it charges itself 12 "
                 "points each time -- but the plan record still carries the room's DECLARED size, and "
                 "nothing downstream reads these coordinates, so without this list the trade is "
                 "invisible. A room below its band is a defect that survives the life of the building. "
                 "build/solver.py refuses to make this trade at all (OQ 32)." if ub
                 else "Every room was placed at or above the floor of its own catalogue band.")}
    return write_record(plan, levels, best["ground"], best["upper"], fp, report)

# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--out"); ap.add_argument("--svg")
    ap.add_argument("--parti"); ap.add_argument("--candidates", type=int, default=250)
    ap.add_argument("--solver", default="heuristic", choices=["heuristic", "cp", "both"],
                    help="heuristic (this file's search, the default and the historical "
                         "behaviour) or cp / both (build/solver.py's constraint solver, WP-2.3)")
    ap.add_argument("--time", type=float, default=60.0, help="solver time budget, seconds")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    parti = json.load(open(f"{ROOT}/partis/{a.parti}.json")) if a.parti else None
    if a.solver == "heuristic":
        out = solve(plan, parti, a.candidates)
    else:
        # Loaded lazily: solver.py imports OR-Tools, and nothing else in this toolchain should
        # need it installed to run.
        sv = _mod("solver", f"{ROOT}/build/solver.py")
        out = sv.solve(plan, parti, time_budget_s=a.time, mode=a.solver)
    if "error" in out:
        print(out["error"])
        for r in (out.get("conflict") or {}).get("requirements", []): print(f"    · {r}")
        return
    fp, gr = out["footprint"], out["geometry_report"]
    print(f"\n  {plan['name']}")
    print(f"  footprint {fp['width_ft']} x {fp['depth_ft']} ft, {fp['bays']} bays of {fp['bay_module_ft']} ft, {fp['area_sf']} sf gross")
    print(f"  score {gr['score']}  (ground {gr['ground_score']}, upper {gr['upper_score']}, vertical {gr['vertical_score']})")
    print(f"  relaxations {gr['relaxations']['count']}, worst {gr['relaxations']['max_off_grid_ft']} ft off the bay line")
    for n in gr["vertical"][:6]: print(f"    · {n}")
    if a.out: json.dump(out, open(a.out, "w"), indent=1, ensure_ascii=False); print(f"  wrote {a.out}")
    if a.svg:
        rp = _mod("render_plan", f"{ROOT}/build/render_plan.py")
        rp.render(out, a.svg); print(f"  wrote {a.svg}")
    print()

if __name__ == "__main__":
    main()
