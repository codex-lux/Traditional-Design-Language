#!/usr/bin/env python3
"""Geometry — place room rectangles in a footprint, both levels solved together.

Bay-grid slicing with a relaxation pass. Rooms snap to the structural bay module the parti
declares, because traditional houses ARE built on one: joists span it, windows centre on it,
the facade composes from it. Where a room cannot be made to fit on the grid the cut is allowed
off it, and every such relaxation is recorded as a compromise rather than hidden.

Levels are solved jointly, not sequentially: candidate layouts are generated for each level and
scored in pairs on vertical alignment — bearing lines that continue, and wet rooms that stack.
That is a harder problem than constraining the upper floor to the lower, and it finds
arrangements the sequential method cannot.

This docstring claimed a third term — "a stair that lands where it left" — from the day it was
written until WP-6.1, and `vertical_score` had none for another three packages. WP-6.3 built a
charge and refused it as inert (byte-identical output at 100x and 10,000x); WP-7.1 made the
generator level-aware and moved bearing without moving stacking; WP-7.4 charges declared
`stacks_over` in both engines and works — the refused charge keyed on landing-over-stair, a
pair neither shipped plan declares, and was measured against a 250-candidate pool too thin to
contain the alternative. Read `vertical_score`'s own comment before quoting any of that: two
published refusals are superseded there, with the measurement that superseded them. This file
says what it does, not what it was meant to.

When the rooms will not fit: grow the footprint first, then shrink rooms toward their bands,
then drop optional rooms. A room below its furniture minimum is a defect that survives the
building; a slightly larger house is just a slightly larger house.

  python3 build/geometry.py plans/<id>.json [--out plans/<id>.geo.json] [--svg dist/<id>.svg]
"""
from __future__ import annotations
import json, os, math, random, argparse, importlib.util, copy, hashlib, re

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

def void_spec(rtype):
    """OQ 55's `void` block on an outdoor room, or None if the room is not a reserved void.

    Ruled 24 Aug 2026: outdoor rooms are carried as placed, dimensioned voids -- excluded from
    the area budget and the heated envelope, drawn open -- rather than dropped before placement.
    A room with no `void` block is treated as `within_footprint: false`, which IS the behaviour
    before the ruling: left out of placement entirely. That is deliberately the default, because
    a room nobody has judged must not be silently promoted into the footprint.

    Returns None for anything not a within-footprint void, so `if void_spec(t)` reads as
    "this room takes a rectangle in the block but is not part of the heated envelope"."""
    r = C["rooms"].get(rtype, {})
    if r.get("function_class") not in OUTDOOR: return None
    v = r.get("void") or {}
    return v if v.get("within_footprint") else None

def is_placed(rtype):
    """Everything that takes a rectangle in the block: every indoor room, plus reserved voids."""
    return is_indoor(rtype) or void_spec(rtype) is not None
def band(rtype):
    d = C["rooms"].get(rtype, {}).get("dimensions", {})
    return (d.get("area_sf") or [40, 900])

# WP-9.4. `band()` above has read ONE KEY of the three the same dict carries since the room
# catalogue was written. `dimensions` states `area_sf`, `width_ft` AND `proportion`, and until
# this package the placer read the first and scored shape off a universal constant instead:
# `level_score`'s `if ar > 2.6`. Measured over the 60 room records --
#
#   54 declare `proportion`; 43 of those have a CEILING BELOW 2.6 (median 2.0), so the
#   constant was LOOSER than the corpus on four rooms in five; and the 11 above it are exactly
#   the rooms meant to be long -- gallery-corridor 12.0, centre-passage 5.0, entry-porch 5.0 --
#   which the constant OVER-charged for being what they are. A passage paid 8.9 points for its
#   own proportion while a kitchen drawn 10 x 30 paid 2.40 against 14 for one missing wall.
#
# Ruled by Lucas on 1 Sep 2026: the bands BIND AT THEIR STATED CEILING, per room type, exactly
# as written. That is the corpus deciding rather than this file, and it authors no threshold --
# the condition WP-9.1 worked under and this package keeps.
#
# A room type with no `proportion` keeps the old constant, and `shape_band` says which answer
# it gave, because a default that cannot be distinguished from a reading is how a constant
# survives a package that was supposed to remove it.
ASPECT_FALLBACK = 2.6

def shape_band(rtype):
    """(ceiling, source) for a room type's aspect. `source` is 'corpus' or 'fallback'."""
    d = C["rooms"].get(rtype, {}).get("dimensions", {})
    pr = d.get("proportion")
    if isinstance(pr, list) and len(pr) == 2 and pr[1]:
        return float(pr[1]), "corpus"
    return ASPECT_FALLBACK, "fallback"

def width_floor(rtype):
    """The short-dimension floor a room type states, or None. Read, never invented."""
    d = C["rooms"].get(rtype, {}).get("dimensions", {})
    w = d.get("width_ft")
    return float(w[0]) if isinstance(w, list) and w else None

def wall_lines(rects, r=1):
    """The x and y lines a set of placed rectangles puts walls on.

    One spelling, used by `vertical_score`'s bearing term and by the level-aware generator
    that feeds it (WP-7.1). A second copy of this is how a scorer and the generator it scores
    come to disagree about where the walls are."""
    xs = {round(v[0], r) for v in rects.values()} | {round(v[0] + v[2], r) for v in rects.values()}
    ys = {round(v[1], r) for v in rects.values()} | {round(v[1] + v[3], r) for v in rects.values()}
    return sorted(xs), sorted(ys)


def snap(v, module, tol, prefer=()):
    """Where a cut lands: a wall line below if there is one, else the nearest bay line.

    `prefer` is the level below's wall lines on this axis, and it is the whole of WP-7.1
    (OQ 95). Until it existed, `slice_rect` was called for the upper level with NO reference
    to the ground placement -- so `vertical_score` scored candidates produced blind, and 26 of
    49 `stacks_over` claims across the corpus were drawn broken because the search could not
    aim, only re-rank. The ground layout is fully populated at the moment the upper level is
    generated; it was simply never passed.

    THE RETURNED `off` IS THE DEFINITION CORRECTION, and it must be read carefully. A
    relaxation is defined in this file's own prose as "a joist run that does not land on a
    bearing wall"; the code has always approximated that as "misses the bay module". Those are
    not the same thing -- 18 of 30 ground wall lines on the shipped plans are themselves off
    the bay grid, so a cut landing squarely on a wall below would have been counted a
    compromise while a cut on a bare bay line with nothing under it was counted sound. A cut
    that lands on a wall below returns off=0.0 because it DOES land on bearing. That is the
    prose finally executed, not a loosening of it."""
    for L in prefer:
        if abs(L - v) <= tol:
            return (L, 0.0)
    s = round(v / module) * module
    return (s, 0.0) if abs(s - v) <= tol else (v, abs(s - v))

# ---------------------------------------------------------------- slicing
def bias(room, axis, below=None):
    """Directional pull from the room's declared exterior walls: +1 north/east, -1 south/west."""
    b = 0.0
    for w in (room.get("exterior_walls") or []):
        dx, dy = DIRS.get(w, (0, 0))
        b += (dy if axis == "y" else dx)
    # WP-7.1 (OQ 95), and this is the half that aims a ROOM rather than a wall line. Snapping
    # the upper cuts to the walls below makes upper walls continue -- measured, transfer beams
    # 21 -> 9 on the Tidewater plan -- and does nothing whatever for `stacks_over`, because
    # moving a line does not move a room. Measured across all 14 partis that declare the
    # field, cut-line snapping ALONE took broken claims from 26/49 to 30/49: worse, not
    # better. A room that says it stacks over another has to be PULLED toward it while the
    # rooms are being divided, which is here.
    #
    # Weighted at 2.0 against an exterior wall's 1.0: a waste stack with nothing under it is
    # a defect that survives the building, and a room's declared exposure is a preference the
    # search is meant to trade off. Scaled by how far off centre the target actually sits, so
    # a target in the middle of the block exerts no false pull.
    if below:
        t = (below.get("rects") or {}).get(room.get("stacks_over") or "")
        if t:
            span = (below.get("H") or 0) if axis == "y" else (below.get("W") or 0)
            if span:
                c = (t[1] + t[3] / 2.0) if axis == "y" else (t[0] + t[2] / 2.0)
                b += 2.0 * max(-1.0, min(1.0, (c - span / 2.0) / (span / 2.0)))
    return b

def partition(rooms, axis, rng, below=None):
    """Split into two groups: the LOW group goes south or west, so it must be seeded with the
    rooms pulled that way. Grow each group through the door graph, so a cut severs as few
    connections as possible — a plan whose adjacencies survive the slicing is the whole point."""
    ids = {r["id"] for r in rooms}
    doors = {r["id"]: {d["to"] for d in (r.get("doors") or []) if d["to"] in ids} for r in rooms}
    # bias ASCENDING: most negative (south/west) first, because lo is placed low
    ranked = sorted(rooms, key=lambda r: (bias(r, axis, below), -r["_area"], r["id"]))
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
            sc = (-conn, bias(r, axis, below), -r["_area"])
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
    treemap instead of a plan.

    REFUSES WHEN MORE THAN ONE ROOM QUALIFIES (WP-9.4). This returned the FIRST match in file
    order, and on `five-part-palladian` three level-0 rooms satisfy its test identically:
    `passage` (`["S","N"]`), `westhyphen` and `easthyphen` (both `["N","S"]`, both
    `gallery-corridor`, both circulation). It returned `passage` because the parti happens to
    list it first, and `easthyphen` after a shuffle -- verified. The spine of the house was
    being decided by JSON key order.

    A silent order-dependent answer is worse than no answer: the caller's slab branch is the
    single largest move the slicer makes, and there was no way to tell a diagram with one
    spine from a diagram with three. Refusing hands the rectangle to the ordinary partition,
    which is the honest fallback, and the count is reported by the caller so the refusal is
    visible rather than inferred from a plan that looks odd.
    """
    pairs = (("S", "N") if axis == "y" else ("W", "E"))
    hits = []
    for r in rooms:
        # Only CIRCULATION spans. A porch with three exterior walls wants the south edge,
        # not a slab through the middle of the house.
        if C["rooms"].get(r["type"], {}).get("function_class") != "circulation": continue
        w = set(r.get("exterior_walls") or [])
        if pairs[0] in w and pairs[1] in w: hits.append(r)
    if len(hits) <= 1:
        return hits[0] if hits else None
    # MORE THAN ONE ROOM QUALIFIES, AND REFUSING THROWS AWAY A CORRECT ANSWER. The first
    # draft of this returned None on a tie, which broke the shipped reference plan: on
    # plans/tidewater-georgian-careful.json BOTH `passage` (S,N) and `backhall` (N,S) are
    # circulation rooms declaring an opposite pair, so the slab never formed and the entry
    # porch left the S entrance wall (tests/test_composition.py:173).
    #
    # So the tie is BROKEN rather than refused, and by the corpus rather than by file order:
    # the spine is the larger circulation room. rooms/back-hall.json says why in its own
    # words -- it is "the second circulation system", existing "so that one set of people can
    # move through the house without meeting another set", and "designed to be invisible from
    # the formal plan". A back hall is not the axis of the house and a hyphen is not either.
    # Area is the corpus's own statement of that, already carried per room, and the id
    # tie-break makes the answer independent of dict order.
    hits.sort(key=lambda r: (-(r.get("_area") or 0.0), r["id"]))
    SPANNING_AMBIGUOUS.append(tuple(sorted(r["id"] for r in hits)))
    return hits[0]


# Every refusal `spanning()` makes, so the caller can report it. A list rather than a counter
# because WHICH rooms tied is the thing an author needs to fix, and `five-part-palladian`'s
# tie (passage / easthyphen / westhyphen) is a data question -- two hyphens identical in every
# typed field -- not a code one.
SPANNING_AMBIGUOUS = []

def ring_depth(W, H, court_area, sides=4):
    """Depth of the ranges around a court, solved from the court's own declared area.

    Four sides: the court is (W-2d) x (H-2d), so 4d^2 - 2d(W+H) + (WH - court) = 0 and the
    smaller root is the one that puts the ranges around the court rather than inside it.
    Three sides (a U): the court is (W-2d) x (H-d), open on the south.

    Returns None when the block cannot hold that court at all -- the discriminant goes
    negative, or the ranges come out too shallow to hold a room. That is a real answer and the
    caller falls back to the ordinary slicer rather than drawing a ring nobody could build."""
    if court_area <= 0 or W <= 0 or H <= 0: return None
    if sides >= 4:
        a, b, c = 4.0, -2.0 * (W + H), W * H - court_area
    else:
        a, b, c = 2.0, -(2.0 * H + W), W * H - court_area
    disc = b * b - 4 * a * c
    if disc < 0: return None
    d = (-b - math.sqrt(disc)) / (2 * a)
    if d < 7.0 or d > min(W, H) / 2.2: return None
    return d


def courtyard_slice(rooms, W, H, module, tol, rng, out, relax, sides=4):
    """Lay a block out as ranges around a court. Returns False if it cannot, having drawn nothing.

    OQ 55, and the reason this exists rather than a scoring term alone: a ring is not something
    a random guillotine partition finds. Four thousand candidates of the ordinary slicer put the
    court in the block's corner every time, because isolating one room into the innermost cell
    of a four-deep nesting is not a thing random splits do. A ring IS guillotine-decomposable --
    cut at the court's south and north edges to get three bands, then cut the middle band at its
    west and east edges -- so the tree is stated here instead of searched for. The ranges
    themselves are still sliced by the ordinary search, which is what it is good at.

    The court's depth is not chosen: it falls out of the court's own declared area against the
    block (see ring_depth), which is the corpus deciding rather than this function."""
    voids = [r for r in rooms if isinstance(r.get("_void"), dict) and not r["_void"].get("roofed")]
    if len(voids) != 1: return False
    court = voids[0]
    ring = [r for r in rooms if r["id"] != court["id"]]
    if len(ring) < sides: return False
    d = ring_depth(W, H, court["_area"], sides)
    if d is None: return False

    # The four (or three) bands, as guillotine cuts. South is y=0 by this file's convention.
    cw, ch = W - 2 * d, (H - 2 * d if sides >= 4 else H - d)
    bands = [("S", 0.0, 0.0, W, d)] if sides >= 4 else []
    y0 = d if sides >= 4 else 0.0
    bands += [("W", 0.0, y0, d, ch), ("E", W - d, y0, d, ch), ("N", 0.0, y0 + ch, W, d)]
    out[court["id"]] = (round(d, 2), round(y0, 2), round(cw, 2), round(ch, 2))

    caps = [(k, x, y, w, h, w * h) for (k, x, y, w, h) in bands]
    groups = {c[0]: [] for c in caps}

    # OQ 61: when the parti gives the covered walk one record per range -- as many roofed voids
    # as there are bands -- that IS the range assignment, and it is read rather than guessed:
    # the i-th walk takes the i-th band (the parti lists them in this file's own band order, S
    # W E N, so the range holding the entry passage is the one on the street), and every other
    # room goes to the band of the walk it has a door to. A room with no door to any walk
    # follows the room it does open off, which is how a larder reaches the kitchen's range and a
    # primary bathroom its bedroom's. That is the diagram stating its own topology; falling back
    # to filling bands by area would place a room in a range whose corredor it cannot reach.
    walks = [r for r in ring if isinstance(r.get("_void"), dict) and r["_void"].get("roofed")]
    assigned = False
    if len(walks) == len(caps):
        band_of = {}
        for c, wroom in zip(caps, walks):
            groups[c[0]].append(wroom); band_of[wroom["id"]] = c[0]
        rest = [r for r in ring if r["id"] not in band_of]
        walk_ids = set(band_of)
        def _doors(r):
            return [(d["to"] if isinstance(d, dict) else d) for d in (r.get("doors") or [])]
        # A door to a WALK first, for every room, before any room is placed by a neighbour.
        # Doing both in one pass lets a room inherit a range from a sibling that was itself
        # assigned earlier in the same pass -- which put the kitchen in the street range because
        # it happened to list the dining room before its own corredor.
        for r in rest:
            hit = next((d for d in _doors(r) if d in walk_ids), None)
            if hit: band_of[r["id"]] = band_of[hit]; groups[band_of[hit]].append(r)
        for _pass in range(3):
            for r in rest:
                if r["id"] in band_of: continue
                for tid in _doors(r):
                    if tid in band_of:
                        band_of[r["id"]] = band_of[tid]; groups[band_of[tid]].append(r); break
        if all(r["id"] in band_of for r in rest):
            assigned = True
        else:
            groups = {c[0]: [] for c in caps}

    if not assigned:
        # Rooms go round the ring in the order the parti wrote them, which is the order its
        # author walked the house. Each band takes rooms until it has its own area; nothing is
        # re-sorted, because the sequence IS the adjacency information a parti carries about a
        # ring. This is the path for a parti whose walk is still one record.
        total = sum(c[5] for c in caps)
        have = sum(r["_area"] for r in ring)
        i, queue = 0, list(ring)
        for n, c in enumerate(caps):
            want = c[5] / total * have
            acc = 0.0
            remaining_bands = len(caps) - n - 1
            while i < len(queue) and (acc < want or len(queue) - i > remaining_bands * 6):
                if acc >= want and len(queue) - i <= remaining_bands: break
                groups[c[0]].append(queue[i]); acc += queue[i]["_area"]; i += 1
                if remaining_bands and len(queue) - i <= remaining_bands: break
        for r in queue[i:]: groups[caps[-1][0]].append(r)
    if any(not groups[c[0]] for c in caps): return False
    # OQ 61 + OQ 62: the walk is laid against the COURT side of its own band, not left to the
    # ordinary slicer to place somewhere in it. A corredor is by definition the edge between the
    # ranges and the void -- that is what makes it the circulation -- and once OQ 62 gave the
    # four walks real declared sizes, a walk small relative to its band was pushed off the court
    # by the rooms beside it. Stating the strip is the same move as stating the ring: the search
    # is good at slicing a range and has no way to know which of its edges matters.
    INNER = {"S": "N", "N": "S", "W": "E", "E": "W"}
    for (k, x, y, w, h, _a) in caps:
        grp = groups[k]
        walk = next((r for r in grp if isinstance(r.get("_void"), dict)
                     and r["_void"].get("roofed")), None)
        rest = [r for r in grp if walk is None or r["id"] != walk["id"]]
        if walk is None or not rest:
            slice_rect(copy.deepcopy(grp), x, y, w, h, module, tol, rng, out, relax)
            continue
        along = w if k in ("S", "N") else h            # the band's length along the court
        strip = max(module * 0.55, min((h if k in ("S", "N") else w) * 0.6,
                                       walk["_area"] / max(along, 1.0)))
        side = INNER[k]
        if side == "N":     wx, wy, ww, wh = x, y + h - strip, w, strip; rx, ry, rw, rh = x, y, w, h - strip
        elif side == "S":   wx, wy, ww, wh = x, y, w, strip;             rx, ry, rw, rh = x, y + strip, w, h - strip
        elif side == "E":   wx, wy, ww, wh = x + w - strip, y, strip, h; rx, ry, rw, rh = x, y, w - strip, h
        else:               wx, wy, ww, wh = x, y, strip, h;             rx, ry, rw, rh = x + strip, y, w - strip, h
        out[walk["id"]] = (round(wx, 2), round(wy, 2), round(ww, 2), round(wh, 2))
        slice_rect(copy.deepcopy(rest), rx, ry, rw, rh, module, tol, rng, out, relax)
    return True


def _clamp_cut(v, extent, module):
    """The corrected clamp, MEASURED AND NOT CALLED. Read this before calling it (WP-9.4).

    IT IS NOT WIRED IN, and that is a refusal with numbers behind it rather than an oversight.
    Building it, measuring it and leaving it uncalled is the honest record of what was found:
    the defect below is real, the fix below is right, and shipping the fix on its own makes
    the corpus worse in two ways that are both consequences of what the defect was silently
    doing. Wiring it in is a package of its own, and it must replace the accidental filter
    described below with a STATED one in the same change.

      * Fatals over the 21-parti sweep go 114 -> 127 on the heuristic.
      * THE ENTRY PORCH GOES SHALLOW. On plans/tidewater-georgian-careful.json it is drawn
        10.0 x 6.0 ft with the shipped clamp and 5.0 x 8.3 ft with this one, so its clear
        depth falls 6.0 -> 5.0 and `porch-nobody-can-sit-on` (at-least 6.0) fires again --
        a fault WP-7.4 had cleared, and whose clearing that package recorded as a real gain.
        Isolated by toggling this function alone against the door weights: the porch is
        10.0 x 6.0 under BOTH door settings with the old clamp and 5.0 x something under
        both with the new one.
      * The relaxation count moves 7 -> 8, pinned verbatim in two files.

    WHY A CORRECT FIX MAKES THINGS WORSE. No winning placement at HEAD contains a
    negative-dimension room, on any of the 21 partis -- checked directly. The defect never
    reached a sheet. What it did was ELIMINATE 22.3% of candidates before they could be
    scored, and those candidates were the cramped ones. Repairing the geometry admits them to
    the competition, where some of them win. The bug was an accidental filter, and this
    codebase already has the rule for that case: a fix that removes a shield is a fix that has
    to look at what the shield was covering.

    Keep the fix here, unwired, so the next reader has the corrected arithmetic, the
    measurements, and the reason -- rather than rediscovering the inversion and shipping it.

    ---- the defect, and this function's arithmetic ----

    The clamp this replaces was `max(module * 0.6, min(extent - module * 0.6, v))`, whose
    intent is "leave at least 0.6 of a module on each side". That is impossible when
    `extent < 1.2 * module`, and the expression does not fail there -- it INVERTS: the inner
    `min` returns something below `module * 0.6`, the outer `max` then returns `module * 0.6`,
    which is larger than the rectangle, and the second child is handed a NEGATIVE dimension.

    Measured before the fix, over 3,000 candidates on plans/tidewater-georgian-careful.json:
    670 layouts (22.3%) contained at least one negative-dimension room -- cellarstair 316,
    powder 271, pantry 76, butlers 49, stair 33, porch 6, library 5 -- and 72 broke the
    exact-tiling identity by more than 0.5 sf. That identity is what `over_band()`'s published
    refusal rests on. None of them ever reached a sheet, because `level_score` makes a
    negative-area room lose: THE POOL'S DIVERSITY WAS THE SHIELD, which is a reason to fix it
    rather than to keep relying on it.

    Byte-identical where the old expression was already correct. For `extent >= 1.2 * module`
    both bounds collapse to the old ones exactly; below it they collapse toward the midpoint,
    so the cut splits the rectangle evenly and both children stay positive.
    """  # noqa: unused -- deliberately, see above
    lo = min(module * 0.6, extent / 2.0)
    hi = max(extent - module * 0.6, extent / 2.0)
    return max(lo, min(hi, v))


def _relax(relax, off, axis, at, span_lo, span_hi):
    """Record a cut that missed the bay line, WITH ITS POSITION (OQ 33).

    P7 of the interface standard says a compromise is counted AND appears on the drawing, at its
    location. It was only ever counted: this list held bare floats, so the workbench could print
    an honest tally and had nothing to place a mark with, and `RelaxationMarker` -- a component
    built for exactly this -- had no data to render. The tally was true and the drawing was
    silent about where the truth applied.

    A relaxation is a guillotine cut that did not land on the structural bay: `axis` is the axis
    it cuts ACROSS ("x" a vertical line, "y" a horizontal one), `at_ft` is where the line sits on
    that axis, and from/to are its extent along the other one. That is a joist run that does not
    land on a bearing wall, and a builder can now be shown WHICH one.
    """
    relax.append({"off_ft": round(off, 2), "axis": axis, "at_ft": round(at, 2),
                  "from_ft": round(span_lo, 2), "to_ft": round(span_hi, 2)})


def slice_rect(rooms, x, y, w, h, module, tol, rng, out, relax, depth=0, below=None):
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
            slab_off = d          # raw, NOT rounded: `if round(d, 2)` swallows a sub-half-inch
                                  # miss that `if d` counted, and the pinned relaxation count is
                                  # exactly the kind of number that must not move by accident.
            sw = max(module * 0.6, min(w * 0.45, sws)) * rng.uniform(0.94, 1.10)
            rest = [r for r in rooms if r["id"] is not sp["id"] and r["id"] != sp["id"]]
            west = [r for r in rest if bias(r, "x", below) < 0]
            east = [r for r in rest if r not in west]
            # let a borderline room cross the cut sometimes, or the search has nothing to explore
            for r in list(rest):
                if abs(bias(r, "x", below)) < 0.5 and rng.random() < 0.35:
                    (east if r in west else west).append(r)
                    (west if r in west else east).remove(r)
            if not west or not east:
                west, east = partition(rest, "x", rng, below)
            aw = sum(r["_area"] for r in west); ae = sum(r["_area"] for r in east)
            wfrac = aw / (aw + ae) if (aw + ae) else 0.5
            if "centre" in (sp["type"] or "") or "center" in (sp["type"] or ""):
                wfrac = (wfrac + 0.5) / 2.0      # a centre passage is named for where it goes
            wfrac = min(0.78, max(0.22, wfrac + rng.uniform(-0.07, 0.07)))
            rem = w - sw
            # The line this decides sits at x + wwid, so a wall line below -- which is stated
            # in MODEL coordinates, not in this rectangle's -- can only be preferred by
            # snapping the absolute position. The blind path keeps the original WIDTH snap
            # byte for byte: the two are not equivalent once x is off the module, and
            # changing it silently moved the ground placement, cost CP-SAT its proof of
            # `tidewater-georgian-careful`, and took a whole afternoon to find.
            _px = (below or {}).get("x", ())
            if _px:
                _abs, dd = snap(x + rem * wfrac, module, tol, _px)
                wwid = _abs - x
            else:
                wwid, dd = snap(rem * wfrac, module, tol)
            wwid = max(module * 0.6, min(rem - module * 0.6, wwid))   # _clamp_cut: refused, see it
            out[sp["id"]] = (round(x + wwid, 2), round(y, 2), round(sw, 2), round(h, 2))
            # Both edges of the spanning slab, now that its position is known. The width snap
            # (slab_off) misses the grid at the slab's FAR edge; the wwid snap at its near one.
            if dd: _relax(relax, dd, "x", x + wwid, y, y + h)
            if slab_off: _relax(relax, slab_off, "x", x + wwid + sw, y, y + h)
            slice_rect(west, x, y, wwid, h, module, tol, rng, out, relax, depth + 1, below)
            slice_rect(east, x + wwid + sw, y, rem - wwid, h, module, tol, rng, out, relax, depth + 1, below)
            return
        sp = spanning(rooms, "x")
        if sp and w > h * 0.55:
            sh = max(module * 0.5, min(h * 0.4, sp["_area"] / w))
            rest = [r for r in rooms if r["id"] != sp["id"]]
            south = [r for r in rest if bias(r, "y", below) < 0]
            north = [r for r in rest if r not in south]
            if not south or not north: south, north = partition(rest, "y", rng, below)
            a_s = sum(r["_area"] for r in south); a_n = sum(r["_area"] for r in north)
            sfrac = a_s / (a_s + a_n) if (a_s + a_n) else 0.5
            rem = h - sh
            shgt = max(module * 0.5, min(rem - module * 0.5, rem * sfrac))
            out[sp["id"]] = (round(x, 2), round(y + shgt, 2), round(w, 2), round(sh, 2))
            slice_rect(south, x, y, w, shgt, module, tol, rng, out, relax, depth + 1, below)
            slice_rect(north, x, y + shgt + sh, w, rem - shgt, module, tol, rng, out, relax, depth + 1, below)
            return

    axis = "x" if w >= h else "y"
    if abs(w - h) < module * 0.9 and rng.random() < 0.45: axis = "y" if axis == "x" else "x"
    lo, hi = partition(rooms, axis, rng, below)
    a_lo = sum(r["_area"] for r in lo); a_tot = a_lo + sum(r["_area"] for r in hi)
    frac = a_lo / a_tot if a_tot else 0.5
    if axis == "x":
        cut = w * frac
        s, d = snap(x + cut, module, tol, (below or {}).get('x', ()))
        cut = max(module * 0.6, min(w - module * 0.6, s - x))         # _clamp_cut: refused, see it
        if d: _relax(relax, d, "x", x + cut, y, y + h)
        slice_rect(lo, x, y, cut, h, module, tol, rng, out, relax, depth + 1, below)      # lo goes west
        slice_rect(hi, x + cut, y, w - cut, h, module, tol, rng, out, relax, depth + 1, below)
    else:
        cut = h * frac
        s, d = snap(y + cut, module, tol, (below or {}).get('y', ()))
        cut = max(module * 0.6, min(h - module * 0.6, s - y))         # _clamp_cut: refused, see it
        if d: _relax(relax, d, "y", y + cut, x, x + w)
        slice_rect(lo, x, y, w, cut, module, tol, rng, out, relax, depth + 1, below)      # lo goes south
        slice_rect(hi, x, y + cut, w, h - cut, module, tol, rng, out, relax, depth + 1, below)

# ---------------------------------------------------------------- scoring one level
SHAPE_W = 6.0        # the charge per unit of aspect over a room's OWN ceiling (WP-9.4)

# BUILT, SWEPT, AND SHIPPED AT ZERO (WP-9.4). The charge per foot below a room's own stated
# short-dimension floor -- `dimensions.width_ft[0]`, declared by 58 of 60 room types, already
# read by `compose.repair()` and by `plan_check`'s room layer, and invisible to the placer.
#
# It does what it was built to do, ON THE WEAKER ENGINE ONLY. Swept over the 21 partis:
#
#   weight        0     2     6    14    30
#   below floor 100    98    90    84    69      <- monotone, and the point of the term
#   over ratio  134   133   123   119   111      <- monotone
#   fatal       119   118   124   126   135      <- worse in the middle than at the bottom
#
# That fatal column is WP-7.4's published hazard recurring: a term can be worse in the middle
# of its range than at either end, so zero and both extremes were swept.
#
# AND ON `auto`, WHICH IS WHAT SHIPS, IT IS A BAD TRADE: fatal 39 -> 42 to move rooms below
# their floor 113 -> 112. CP already holds each room inside 0.88-1.20 of its programme as a
# HARD constraint, so the floor has little left to say there, and the three fatals are real.
# The heuristic's own gain (106 -> 95) is not worth buying on the engine nobody draws with.
#
# Kept rather than deleted, at zero, so the next reader has the term, the sweep and the reason
# instead of rebuilding it. Raise the weight only with a fresh sweep ON `auto`.
WIDTH_W = 0.0


def level_score(rects, rooms):
    """Area error, aspect against the room's OWN band, width floor, exterior-wall satisfaction.

    WP-9.4 replaced a universal `if ar > 2.6` with the ceiling each room type states. Read
    `shape_band()`'s comment for the measurement; the short version is that the constant was
    looser than the corpus on 43 of 54 room types and charged the other 11 for being long,
    which is what a passage and a gallery are FOR. Weight is unchanged at 6.0 so the only
    thing that moved is which number the 6.0 multiplies.

    The width floor is new and is the same move: `dimensions.width_ft[0]` is stated by 58 of
    60 room types, is what `compose.repair()` already widens a room to, and is what
    `plan_check`'s room layer already convicts a record on. The placer was the one reader of
    that dict that could not see it -- which is how a 16 x 20 kitchen was drawn 10 x 30 while
    the record, the composer and the critic all agreed 10 ft was below its floor.
    """
    s = 0.0
    for r in rooms:
        x, y, w, h = rects[r["id"]]
        got, want = w * h, r["_area"]
        s += abs(got - want) / max(want, 1) * 10
        short, long_ = min(w, h), max(w, h)
        ar = long_ / max(short, 0.1)
        ceil, _src = shape_band(r["type"])
        if ar > ceil: s += (ar - ceil) * SHAPE_W
        floor = width_floor(r["type"])
        if floor and short < floor: s += (floor - short) * WIDTH_W
        lo, hi = band(r["type"])
        if got < lo * 0.85: s += 12
    return s

def exterior_score(rects, rooms, W, H, tol=0.6, bounds=None):
    """`bounds` (OQ 40) maps a room id to the massing element it sits in, as (x, y, W, H).

    A wing room's north wall is the WING's north wall; charged against the main block's it
    would be missing three walls it actually has, at 14 points each, and the solver would pull
    every dependency room back into the main rectangle to stop paying. With `bounds` absent --
    or on a one-element house, where every room maps to (0, 0, W, H) -- this is the arithmetic
    it has always done."""
    s = 0.0
    for r in rooms:
        want = set(r.get("exterior_walls") or [])
        if not want: continue
        x, y, w, h = rects[r["id"]]
        bx, by, bW, bH = (bounds or {}).get(r["id"], (0.0, 0.0, W, H))
        have = set()
        if y - by <= tol: have.add("S")
        if y + h >= by + bH - tol: have.add("N")
        if x - bx <= tol: have.add("W")
        if x + w >= bx + bW - tol: have.add("E")
        missing = {d for d in want if d in "NSEW"} - have
        s += len(missing) * 14
    return s

def void_enclosure_score(rects, rooms, W, H, shape, tol=0.6):
    """OQ 55: an unroofed void on a courtyard massing has to be surrounded, or it is a notch.

    Found by building the ruling and looking at the first drawing it produced: the court came
    out in the block's SW corner against two exterior walls. That is the right area in the
    right block and it is not a courtyard -- a court is defined by what encloses it, which is
    `rooms/courtyard.json`'s own first sentence, so a court open to the street is a
    contradiction of the diagram rather than a variant of it.

    How many sides may be open is a fact about the MASSING, not about the room: the same
    `courtyard` room serves `courtyard-full` (enclosed on four) and `courtyard-u` (three ranges
    and a fourth side held by a wall or left open), so the allowance is read from the massing's
    own `footprint` field. Any other shape is not charged at all -- a piazza runs along a flank
    and MUST reach the perimeter, and charging it for that would be the check misfiring on the
    case it was not written for."""
    allowed = {"courtyard": 0, "u": 1}.get((shape or "").strip().lower())
    if allowed is None: return 0.0
    s = 0.0
    for r in rooms:
        v = r.get("_void")
        if not isinstance(v, dict) or v.get("roofed"): continue
        if r["id"] not in rects: continue
        x, y, w, h = rects[r["id"]]
        touched = sum(1 for hit in (y <= tol, y + h >= H - tol, x <= tol, x + w >= W - tol) if hit)
        if touched > allowed: s += (touched - allowed) * 14
    return s

# WP-9.4 (task B). A door pair's charge is scaled by what the CORPUS says the opening between
# those two rooms IS, read from openings/grammar.json — the document that already types all
# 1,890 room pairs — rather than by one flat number for every pair in the house.
#
# Ruled by Lucas on 1 Sep 2026: a door is a hard adjacency where the grammar dimensions it as a
# real opening, and a connectivity wish otherwise. The grammar draws that line itself and needs
# no help: `open` (5.0-6.5 and 6.0-10.0 ft), `double` (5.0-6.0) and `cased-opening` (4.0-6.0)
# are openings two rooms can only have by being one architectural volume, while a `swing` at
# 2.0-3.7 ft is the connectivity case. `openings.required_wall_ft` — this corpus's ONE spelling
# of how much shared wall an opening needs — then supplies the scale, so the ratio between
# pairs comes entirely from the corpus and the only authored number is the anchor below.
#
# ANCHORED ON THE GRAMMAR'S OWN DEFAULT so the change is a re-weighting and not a re-scaling:
# `og-default` is a 2.6-3.0 ft swing, whose midpoint needs 3.5 ft of wall, and ADJ_ANCHOR is
# set so that pair costs exactly the 14 it has always cost. Every other pair moves relative to
# it, in the direction the corpus states.
ADJ_ANCHOR = 14.0 / 3.5          # points per foot of the shared wall the corpus asks for
_ADJ_CACHE = {}
_HARD_OPENING = ("open", "double", "cased-opening")


def door_weight(a_type, b_type):
    """(points, hard) for a door between two room types, from the grammar. Cached: this is
    called inside the 250-candidate loop and resolving walks the rule list."""
    key = tuple(sorted((a_type or "", b_type or "")))
    hit = _ADJ_CACHE.get(key)
    if hit is not None:
        return hit
    try:
        CO = _mod("check_openings", f"{ROOT}/build/check_openings.py")
        OP = _mod("openings", f"{ROOT}/build/openings.py")
        g = CO.load_grammar() if hasattr(CO, "load_grammar") else json.load(
            open(os.path.join(ROOT, "openings", "grammar.json")))
        rule = CO.resolve(g, a_type, C["rooms"].get(a_type) or {},
                          b_type, C["rooms"].get(b_type) or {})
        op = rule.get("opening") or {}
        band = op.get("width_band_ft") or [2.8, 3.0]
        need = OP.required_wall_ft(sum(band) / 2.0)
        out = (ADJ_ANCHOR * need, op.get("type") in _HARD_OPENING)
    except Exception:
        out = (14.0, False)          # the flat charge this replaces, if the grammar cannot be read
    _ADJ_CACHE[key] = out
    return out


def adjacency_score(rects, rooms, plan_rooms):
    """Rooms with a door between them should actually touch, weighted by what the door IS."""
    s = 0.0
    byid = {r["id"]: r for r in plan_rooms}
    for r in plan_rooms:
        if r["id"] not in rects: continue
        for d in (r.get("doors") or []):
            t = d["to"]
            if t == "exterior" or t not in rects: continue
            if touching(rects[r["id"]], rects[t]): continue
            pts, _hard = door_weight(r.get("type"), (byid.get(t) or {}).get("type"))
            s += pts
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
# WP-7.4 (OQ 95). The one NAMED weight in this file, and it is named because it was chosen by
# sweep rather than by analogy -- see the measurement in vertical_score below. Its neighbours
# (the wet-stack 8, the transfer-beam 2.0) are inline literals like every other weight here;
# this one carries a name so the sweep that set it can be re-run against it.
STACK_W = 40.0

# DECLARED STACKING AS A RULE RATHER THAN A CHARGE (WP-11.5). A named switch, not a literal
# threaded through the loop, for the reason WP-7.4 records: `_SOLVE_CACHE` is keyed on call
# ARGUMENTS, so a sweep over a module constant silently measures the first value unless the
# cache is cleared -- and a sweep that cannot be run is a rule nobody can refuse. Clear
# `_SOLVE_CACHE` between settings.
#
# **DEFAULT OFF, AND THE NUMBER THAT DECIDED IT IS A 40 FT CLEAR SPAN.** The rule works: broken
# claims 4 -> 1 on the spec Colonial and 8 -> 2 on the Tidewater at the shipped 250 candidates,
# and 4 -> 0 and 3 -> 0 at 1,000. It also more than halves the spec Colonial's worst squeezed
# room (Stair Hall 53% short -> 16%, total shortfall 46 sf -> 30 sf). But at 250 candidates the
# strict candidate on that same plan introduces **two over-capacity clear spans where there were
# none, the worst 40.0 ft against a 20 ft capacity** -- a structural defect on a shipped
# reference plan, traded for a waste stack. On the Tidewater plan the same trade goes the other
# way: 2 spans -> 4, but the worst falls 53.9 ft -> 36.0.
#
# Two shipped plans, opposite structural verdicts, at a pool size the infrastructure audit says
# is already the server's bound and at which the rule is NOT free. That is a ruling, not a
# default: `oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford`. The mechanism is
# built, guarded and measured both ways; flipping it is one line.
STACK_HARD = False

# WP-7.4 (OQ 97). The span charge, and both halves of its form were chosen by sweep.
#
# OQ 97 asked whether span capacity should be a search term "and at what force", and answered
# its own cost question wrongly: it said putting the check in a 250-candidate loop is the
# "25 s x N cost that build_section's own docstring exists to avoid". That 25 s is the SOLVE
# inside build_section, which the candidate loop already has. The check itself --
# structure.wall_lines -> bearing_lines -> span_check over rects that already exist -- measures
# 0.026 s for 250 iterations, against the 250-candidate search's own 0.21 s. So the corpus's
# REAL structural check is affordable here and the "cheap proxy" OQ 97 speculated about is not
# needed. A proxy would also have been wrong: geometry.wall_lines collects every room edge and
# cannot tell bearing from partition, so its widest gap is an under-estimate of the clear span
# -- which is exactly the error WP-7.4 had just removed from span_check itself.
#
# PROPORTIONAL TO HOW FAR OVER CAPACITY THE SPAN IS -- `SPAN_W * span/capacity` -- and the
# ratio rather than the absolute overage, so a hand-framed 20 ft bay and a light-frame joist
# table compare on the same scale. Because ONLY over-capacity spans are charged, that ratio is
# greater than 1 by construction: a marginal violation already costs about SPAN_W and a 60 ft
# run over a 20 ft capacity costs three times it. (This was first written as
# `SPAN_W * (1 + (span/cap - 1))` under a comment arguing for "flat plus graded, because
# neither alone is right". The two are the same expression. The comment described a
# distinction the code did not make, which is the WP-6.4 failure mode in code an hour old --
# the algebra is stated here so the next person does not re-derive the argument.)
SPAN_W = 20.0


def _span_charge(rects_by_level, prep, W, H, bay, style, floor_catalog):
    """Over-capacity clear spans, charged, using structure.py's own check rather than a
    restatement of it.

    Deliberately NOT re-spelled here. There are already two `wall_lines` in this tree
    (this file's, over raw rects, and structure's, over placed room records) and the
    REF_RE/CITE_RE/parseCite drift is what a third spelling of one rule costs. `structure`
    imports this module, so it is loaded lazily on first use rather than at import."""
    if floor_catalog is None:
        # the catalogue could not be read: the span cannot be evaluated, so it is not scored
        # and not reported as clear either. A zero here would read as "no span exceeds
        # capacity", which is the OQ 52 lie in the cheapest possible place.
        return 0.0, None
    ST = _mod("structure", f"{ROOT}/build/structure.py")
    charge, over = 0.0, 0
    for idx, rects in rects_by_level.items():
        if not rects: continue
        rs = []
        for r in prep.get(idx, []):
            v = rects.get(r["id"])
            if not v: continue
            g = {"x_ft": v[0], "y_ft": v[1], "width_ft": v[2], "depth_ft": v[3]}
            # a wall facing an unroofed void is weather-facing and bearing (OQ 55), and
            # structure.wall_lines reads that off the geometry block, not the catalogue
            vd = r.get("_void")
            if isinstance(vd, dict):
                g["void"] = {"heated": False, "roofed": bool(vd.get("roofed"))}
            rs.append({"id": r["id"], "geometry": g})
        if not rs: continue
        bearing = ST.bearing_lines(ST.wall_lines(rs, W, H), bay)
        for sp in ST.span_check(bearing, W, H, style, floor_catalog):
            if sp["ok"] or not sp.get("max_span_ft"): continue
            over += 1
            charge += SPAN_W * (sp["span_ft"] / sp["max_span_ft"])
    return charge, over


def element_of(plan, groundrooms):
    """`{ground_room_id: element_id}`, or `{}` on a one-element plan (WP-11.6, layer 3).

    The join is the room's own `block` tag and NOT `footprint.blocks`, and the reason is an
    ordering one that cost a first attempt: `blocks_record` writes that list inside
    `write_record`, AFTER the search loop this runs in, so a map built from it is empty exactly
    where the charge is decided. The tag is what `blocks_for` itself groups on
    (`is_block_tag(r.get("block"))`), so reading it here is the same spelling one step earlier.

    `{}` on a plan where no ground room carries a tag, which is every plan in this corpus."""
    tagged = {r["id"]: r["block"] for r in (groundrooms or []) if is_block_tag(r.get("block"))}
    if not tagged:
        return {}
    return {r["id"]: tagged.get(r["id"], "main") for r in groundrooms}


def declared_stack_breaks(g, u, upperrooms, elements=None):
    """Every `stacks_over` claim the placement BREAKS, in ONE place (WP-11.5).

    Strict positive rectangle intersection -- plan_check's drawn layer's own rule, so the
    search, the charge and the critic cannot convict and acquit the same house. It was spelled
    once inside `vertical_score` and is now spelled once here, because WP-11.5 needs the same
    test at CANDIDATE-REJECTION time and a second transcription is the
    `openings.required_wall_ft` error (an arbiter carrying its own copy of a rule) in a new
    place.

    A CLAIM WHOSE TARGET IS NOT ON THE LEVEL BELOW IS NOT A BREAK AND IS NOT RETURNED. The
    generator cannot answer it; counting it as broken would convict a placement of something
    nobody could have placed, and counting it as satisfied would be a fake pass. It is neither,
    and `declared_stack_census` below is what says how many there are."""
    ut = {r["id"]: r for r in upperrooms}
    out = []
    for rid, (x, y, w, h) in u.items():
        so = (ut.get(rid, {}) or {}).get("stacks_over")
        if not so:
            continue
        t = g.get(so)
        if not t:
            continue
        # A CLAIM ACROSS TWO MASSING ELEMENTS IS UNJUDGED, NOT BROKEN (WP-11.6, layer 3 of 6).
        # The placer lays only level 0 into elements, so every upper room is inside the main
        # block and a dependency is entirely outside it -- 14 ft away at the closest on the
        # reference fixture, the hyphen's own default gap. No placement this engine can produce
        # puts an upper room over a dependency room, so charging STACK_W for the failure
        # convicts the record of something the generator cannot do. Measured: an upper bath
        # declaring `stacks_over` a kitchen tagged into a west dependency was charged 40 points
        # and told "is drawn clear of it", which reads as a placement gone wrong rather than a
        # claim nobody could keep. That is the OQ 52 family.
        #
        # It is returned as `unjudged` rather than dropped, so a caller counting breaks and a
        # caller reporting them see the same three states the rest of this corpus uses.
        if (elements or {}).get(so, "main") != "main":
            out.append({"room": rid, "over": so, "name": ut[rid].get("name") or rid,
                        "unjudged": f"in the {elements[so]} element"})
            continue
        if (min(x + w, t[0] + t[2]) - max(x, t[0]) <= 0
                or min(y + h, t[1] + t[3]) - max(y, t[1]) <= 0):
            out.append({"room": rid, "over": so,
                        "name": ut[rid].get("name") or rid})
    return out


def stack_breaks_only(g, u, upperrooms, elements=None):
    """The BROKEN claims alone -- what a charge and a rejection may act on. An unjudged claim is
    neither, and a caller that treated the full list as breaks would charge for one."""
    return [b for b in declared_stack_breaks(g, u, upperrooms, elements)
            if not b.get("unjudged")]


def declared_stack_census(g, u, upperrooms):
    """`{claimed, judged, broken, unjudged}` for a placement's declared stacking.

    THREE STATES, because two would lie: `unjudged` counts a claim whose target is not on the
    level below or whose own room was not placed, and `judged` is the denominator any rate
    should be read against. A placement that satisfies zero of zero claims is not a placement
    that stacks."""
    ut = {r["id"]: r for r in upperrooms}
    claimed = judged = 0
    for r in upperrooms:
        if not r.get("stacks_over"):
            continue
        claimed += 1
        if r["id"] in u and g.get(r["stacks_over"]):
            judged += 1
    broken = len(declared_stack_breaks(g, u, upperrooms))
    return {"claimed": claimed, "judged": judged, "broken": broken,
            "satisfied": judged - broken, "unjudged": claimed - judged}


def vertical_score(g, u, groundrooms, upperrooms, plan):
    """The reason both levels are solved together: bearing lines, stacks, and the stair."""
    if not u: return 0.0, []
    s, notes = 0.0, []
    gx, gy = wall_lines(g)      # the same spelling the generator slices against (WP-7.1)
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
    # DECLARED STACKING, CHARGED (WP-7.4, OQ 95). A room whose record says it sits over
    # another room and does not is a waste stack with nothing under it -- a defect that
    # survives the life of the building. Until this package it was REPORTED by
    # plan_check.drawn_layer and prevented by neither engine.
    #
    # THIS SUPERSEDES TWO PUBLISHED REFUSALS, AND BOTH ARE WORTH KNOWING BEFORE TOUCHING IT.
    #
    # (1) WP-6.3 built a stacking charge, swept it at 100x and 10,000x, got BYTE-IDENTICAL
    # output, and concluded "the search can only re-rank blind candidates and can never
    # produce a stacking one". The measurement was sound and the conclusion drawn from it was
    # not. That charge keyed on landing-over-stair, a pair NEITHER shipped plan declares, so it
    # was inert for a reason that had nothing to do with the search's reach. WP-7.1 falsified
    # the stated reason directly: over 24 seeds the winning candidate satisfies 1 to 3 of
    # tidewater's 3 cross-level claims. The search reaches stacking placements.
    #
    # (2) WP-7.1 then made the generator level-aware and moved broken claims 26/47 -> 27/47:
    # flat. That is also true, and it is not evidence against a term. Moving a cut line moves a
    # wall; it does not move a room over another room. Bearing continuity and declared stacking
    # are two problems and OQ 95 conflated them.
    #
    # WHAT MADE THE TERM LOOK INERT WAS THE SIZE OF THE POOL IT WAS RE-RANKING. Measured over
    # 2,000 candidates (5 seeds x 400) rather than the shipped 250 at one seed: on
    # tidewater-georgian-careful, 12 candidates beat the winner's 3 broken claims WHILE KEEPING
    # THE PORCH ON THE ENTRANCE FRONT, at a cost of +41.3 points; on spec-builder-colonial, 6
    # candidates at +2.1. In the thin pool the only better-stacking candidates are ones that
    # move the porch off the front -- entrance_score 0 -> 100, WP-2.2's founding bug -- which is
    # why the break-even read 378 and 52 there. A sampling artefact, not a property of the
    # charge.
    #
    # THE TEST IS plan_check's, DELIBERATELY. Strict positive rectangle intersection, the same
    # rule as plan_check.py's drawn layer, so the search and the critic cannot convict and
    # acquit the same house. Do not "improve" it to a centroid or an overlap fraction here
    # without changing it there in the same commit -- that is the openings.required_wall_ft
    # error (an arbiter carrying its own transcription of a rule) in a new place.
    #
    # A CLAIM WHOSE TARGET IS NOT ON THE LEVEL BELOW IS UNJUDGED AND IS NOT CHARGED. The
    # generator cannot answer it and a zero would read as a pass (the OQ 52 rule).
    _els = element_of(plan, groundrooms)
    for br in declared_stack_breaks(g, u, upperrooms, _els):
        if br.get("unjudged"):
            notes.append(f"{br['name']} declares it stacks over "
                         f"{gt.get(br['over'], {}).get('name') or br['over']}, which is "
                         f"{br['unjudged']} — COULD NOT EVALUATE: this placer lays only the "
                         f"ground level into elements, so no upper room can be placed over a "
                         f"dependency and the claim can neither hold nor be broken here.")
            continue
        s += STACK_W
        notes.append(f"{br['name']} declares it stacks over "
                     f"{gt.get(br['over'], {}).get('name') or br['over']} and is drawn clear "
                     f"of it.")

    # OQ 55: nothing may sit over an UNROOFED reserved void. A courtyard is open to the sky --
    # a room placed above it has no floor and no bearing, and the roof plane it would need is
    # the hole. A ROOFED void is the opposite case and is deliberately not charged: the whole
    # point of separating `roofed` from `within_footprint` is that a Charleston single's upper
    # piazza sits on its lower one, and that is correct rather than a defect.
    open_voids = {rid: g[rid] for rid in g
                  if isinstance(gt.get(rid, {}).get("_void"), dict)
                  and not gt[rid]["_void"].get("roofed") and rid in g}
    for rid, (x, y, w, h) in u.items():
        if isinstance(ut.get(rid, {}).get("_void"), dict): continue   # void over void is fine
        for vid, (vx, vy, vw, vh) in open_voids.items():
            ox = min(x + w, vx + vw) - max(x, vx)
            oy = min(y + h, vy + vh) - max(y, vy)
            if ox > 1.0 and oy > 1.0:
                s += 40
                notes.append(f"{ut[rid].get('name') or rid} is placed over "
                             f"{gt[vid].get('name') or vid}, which is open to the sky: "
                             f"no floor under it, no bearing, and the roof it needs is the hole.")
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

def prep_rooms(plan):
    """Rooms per level index, each carrying the `_area` its own record declares. Shared by the
    heuristic search below and the CP-SAT engine (WP-2.3, build/geometry_cp.py) so the two
    engines place exactly the same room set. Returns (prep, levels), or (None, levels) when
    there is no ground level.

    Since OQ 55 this is no longer only indoor rooms: reserved voids (outdoor rooms whose own
    record says they sit within the block -- a courtyard, a piazza, a loggia) are placed too,
    carrying `_void`. Terraces and anything else with no `void` block still drop out here,
    which is right: a terrace is appended at grade and the block would be the same shape
    without it.

    (Named `prep_rooms` after the 25 Aug merge: two sessions built WP-2.3 independently and
    this function had two names. `geometry_cp.py` calls this one, so it is the one that
    survives; the void handling is the other branch's and is kept.)"""
    levels = {lv.get("index", i): lv for i, lv in enumerate(plan["levels"])}
    prep = {}
    for idx, lv in levels.items():
        rs = []
        for r in lv["rooms"]:
            if not is_placed(r["type"]): continue
            q = dict(r); q["_area"] = (r.get("width_ft") or 10) * (r.get("length_ft") or 12)
            # OQ 55: a reserved void is placed and dimensioned like any other room, and is
            # marked here so every consumer that means HEATED area rather than FOOTPRINT area
            # can tell the difference. `_void` is False on an indoor room and a dict on a void,
            # so the flag carries the roofed/unroofed fact with it rather than needing a second
            # corpus lookup at each use.
            q["_void"] = void_spec(r["type"]) or False
            rs.append(q)
        prep[idx] = rs
    # (levels, prep), which is the order geometry_cp.py unpacks at its two call sites. The
    # other branch returned (prep, levels) and signalled "no ground level" by returning None
    # for prep; that guard is kept below at the one caller that needs it, because silently
    # returning None here would make the CP engine's `levels, prep = ...` bind prep to a level
    # dict. Merge of 25 Aug: two independent WP-2.3 implementations, one surviving signature.
    return levels, prep


# Footprint depth from the MASSING's own pile: a single-pile house is one room deep and a
# double-pile two, and inventing an aspect ratio instead produces a house that is the right
# area and the wrong shape.
PILE = {"single-pile": 22.0, "one-and-a-half-pile": 28.0, "double-pile": 36.0,
        "triple-pile": 46.0, "variable": 32.0}


# ---------------------------------------------------------------- massing elements (OQ 40)
# A house is one rectangle in this corpus until a room says otherwise. OQ 40 was ruled on
# 3 Sep 2026: a dependency is a SECOND MASSING ELEMENT -- not a second plan level (which
# `write_record` below would hand an empty source and draw nowhere, while structure.py's
# unfiltered eave sum added its storey height to the main block) and not a new record kind
# (which forfeits plan_check's `via` bridge, on which butlers-pantry's HARD must_adjoin
# kitchen depends). A room joins an element by its own `block` field; a room with none is in
# the main block.
#
# THE DISCIPLINE THIS FUNCTION EXISTS TO KEEP: a plan that declares no second block must place
# BYTE-IDENTICALLY. All sixteen plans in this corpus are one rectangle, two of them ship, and
# their placements and pinned relaxation counts are the regression guard for the whole change.
# So the one-block case returns a single element at 0,0 covering the footprint derive_footprint
# already computed, every room in it, in `prep`'s own order -- which makes the slice call below
# the same call with the same rng draws, not a similar one.
HYPHEN_DEFAULT_FT = 14.0   # dependency-and-hyphen.json bands hyphen_length_ft 12-20. NOT the band's
                           # midpoint, which is 16 -- an earlier comment here said so and was wrong;
                           # used only until a hyphen room is placed and states its own width.

def is_block_tag(v):
    """Is this `block` field a massing-element id? One rule, read in both places that ask.

    A `block` is an id, and only a non-empty STRING is one. The plan record on the heavy
    workbench routes is caller-supplied and nothing validates it against the schema before it
    reaches here, so a list or a dict arriving in this field became a `TypeError: unhashable
    type` inside `blocks_for`'s `setdefault` -- an HTTP 500 from a field the schema types
    `string`. Anything else is ignored, which puts the room in the main block: the conservative
    answer, and the same one a record written before this field existed already gets.

    It is a named function rather than an inline test because `solve()`'s CP refusal asks the
    same question 800 lines away, and the two answering differently is how a plan comes to be
    refused by the prover for a second element the placer does not build.
    """
    return isinstance(v, str) and bool(v.strip())


def flank_sizes(prep, bay, level=0):
    """Every flanking element's side, hyphen gap, width and depth -- the ONE spelling, read twice.

    `blocks_for` lays these out; `derive_footprint` asks how much roofed ground they take beside
    the main block, because the lot cap is on the BUILT EXTENT (WP-11.6 layer 4). It has to be one
    function: a second transcription of the sizing rule would let the cap and the placement
    disagree about how wide the house is, which is the very defect the cap exists to catch,
    arriving one layer up.

    THE SIZES DO NOT DEPEND ON THE MAIN BLOCK, and that is what makes the cap computable before
    the main block's bay count is chosen rather than after it. A dependency's width comes from its
    own rooms' declared areas over a single-pile depth and its gap from the hyphen room's own
    width; neither reads `fp["W"]`. Only the x positions and the y centring do, and those stay in
    `blocks_for`.

    Returns an ordered list of `{id, side, gap, W, H, hyph, body}` -- empty on every plan in this
    corpus, all sixteen of which are one rectangle."""
    rooms = (prep or {}).get(level) or []
    by_id, order = {}, []
    for r in rooms:
        if not is_block_tag(r.get("block")):
            continue
        by_id.setdefault(r["block"], []).append(r)
        if r["block"] not in order: order.append(r["block"])
    out = []
    for bid in order:
        rs = by_id[bid]
        need = sum(r["_area"] for r in rs)
        # Side from the rooms' own exterior_walls; a tie or a silence goes west, and says so.
        walls = {d for r in rs for d in (r.get("exterior_walls") or [])}
        side = "E" if ("E" in walls and "W" not in walls) else "W"
        # A hyphen room tagged into this element states the gap; otherwise the grouping's own
        # band midpoint stands in and says so. This is the whole reason the hyphen is a ROOM:
        # `hyphen_length_ft` is a machine-tested rule in both hyphen groupings and it had never
        # been evaluated on any plan, because the only hyphen this composer produced was a local
        # variable inside two f-strings.
        hyph = [r for r in rs if C["rooms"].get(r["type"], {}).get("function_class") == "circulation"
                and r.get("hyphen")]
        gap = float(hyph[0].get("width_ft") or HYPHEN_DEFAULT_FT) if hyph else HYPHEN_DEFAULT_FT
        body = [r for r in rs if r not in hyph]
        need_body = sum(r["_area"] for r in body) or need
        # A dependency is sized against a SINGLE-PILE depth, not the main block's own pile.
        # Using the main block's produced a 10 x 50 ft splinter off a 70 ft house: the target
        # depth for a double-pile main block is 36 ft, and dividing a small service programme by
        # it leaves one bay of width and all the area in depth. The massing catalogue states the
        # relation in its own prose -- five-part-palladian is "2-2.5 main / 1-1.5 wings" -- and a
        # wing one room deep is what that describes.
        dep_depth = PILE["single-pile"]
        bays = max(1, round((need_body / dep_depth) / bay))
        W = round(bays * bay, 2)
        H = round(need_body / W, 2) if W else 0.0
        out.append({"id": bid, "side": side, "gap": gap, "W": W, "H": H,
                    "hyph": hyph, "body": body})
    return out


def flanking_extent_ft(prep, bay, level=0):
    """The roofed ground the flanking elements take beside the main block, in feet.

    THE HYPHEN IS COUNTED, and that is the ruling and not an implementation choice:
    `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` item 2, ruled 4 Sep
    2026 -- *"the hyphen is roofed ground; a building whose covered area overruns its lot has
    overrun it"*. So the sum is `gap + width` per element and never width alone.

    0.0 on every plan in this corpus, which is what keeps the lot cap byte-identical for the
    sixteen one-rectangle records by construction rather than by a branch."""
    return round(sum(e["gap"] + e["W"] for e in flank_sizes(prep, bay, level)), 2)


def blocks_for(plan, fp, prep, level=0):
    """The massing elements this level's rooms are laid into, main block first.

    Returns a list of {id, role, x, y, W, H, rooms}. `rooms` is the ordered list of room ids
    that belong to the element. The main block is always first and always at the origin, so a
    reader that only understands one rectangle can take element zero and be right.

    A dependency is sized from its OWN rooms' declared areas -- never from a share of the main
    block's -- because that is what makes it a second element rather than a subdivision of the
    first. Its side comes from the rooms' own `exterior_walls`, which is the corpus's existing
    idiom for laterality (five-part's kitchen dependency declares W and its carriage dependency
    E) rather than a new field nobody has authored.
    """
    rooms = prep.get(level) or []
    tagged = [r for r in rooms if is_block_tag(r.get("block"))]
    # x and y are the INTEGER 0, not 0.0, and that is not fussiness: the call this replaces
    # passed `slice_rect(..., 0, 0, W, H, ...)`, and a float origin makes the written record
    # carry `"x_ft": 0.0` where it carried `"x_ft": 0` -- numerically identical, textually not.
    # A first pass here used 0.0 and a placement-hash comparison duly reported both shipped
    # plans as moved; they had not moved, the instrument had. Keeping the int keeps the record
    # byte-identical as well as the geometry, and costs nothing.
    main = {"id": "main", "role": "main", "x": 0, "y": 0,
            "W": fp["W"], "H": fp["H"], "rooms": [r["id"] for r in rooms if not r.get("block")]}
    if not tagged:
        # The whole corpus, today. One element, every room, the footprint as derived.
        main["rooms"] = [r["id"] for r in rooms]
        return [main]

    bay = fp["bay"]
    out = [main]
    west_edge, east_edge = 0.0, fp["W"]
    # The sizing moved to `flank_sizes` at WP-11.6 layer 4 so the lot cap could read it without a
    # second transcription. What is left here is what actually needs the main block: where each
    # element sits along x, and the y centring on the main block's axis.
    for el in flank_sizes(prep, bay, level):
        bid, side, gap, W, H = el["id"], el["side"], el["gap"], el["W"], el["H"]
        hyph = el["hyph"]
        if side == "W":
            # `west_edge`, not a hardcoded 0.0. The east branch three lines down reads
            # `east_edge` correctly, and the asymmetry was the tell: a SECOND west element put
            # its hyphen back at [-gap, 0] on top of the first one's, and possibly on top of the
            # first dependency. One element hid it, because then `west_edge` IS 0.
            hx = west_edge - gap
            west_edge -= gap + W
            x = west_edge
        else:
            hx = east_edge
            x = east_edge + gap
            east_edge = x + W
        if hyph:
            # The hyphen is its own element, in the gap, lower and shallower than both -- which
            # is dependency-and-hyphen.json's own rule about it.
            hh = min(H, float(hyph[0].get("length_ft") or H))
            out.append({"id": bid + "-hyphen", "role": "hyphen", "x": round(hx, 2),
                        "y": round((fp["H"] - hh) / 2.0, 2), "W": round(gap, 2), "H": round(hh, 2),
                        "rooms": [r["id"] for r in hyph], "attached_to": "main", "side": side})
        out.append({"id": bid, "role": "dependency", "x": round(x, 2),
                    "y": round((fp["H"] - H) / 2.0, 2),   # centred on the main block's axis
                    "W": W, "H": H, "rooms": [r["id"] for r in el["body"]],
                    "attached_to": "main", "side": side})
    return out


def parti_for(plan, parti=None):
    """The parti this placement is of: the one the caller passed, else the one the RECORD names.

    A plan record may name its parti since WP-11.2 (`plan.parti`, an id and never a record --
    WP-9.4's rule, because a caller-supplied parti RECORD reached `bay_module_ft` unchecked and
    put 114 bays of half a foot on a house). Until then the diagram's own bay module could not
    reach the placement at all: `centre-passage-double-pile` states 9 ft and every sheet of it
    was drawn on this function's 10 ft default, because the only route in was a caller who
    happened to pass the parti separately, and the CLI, the bench's drawing route and the
    shipped reference plans all did not.

    The id becomes a path in exactly ONE place in this repository -- `core.load_parti` -- and
    this is not a fourth copy of that join: it calls it. Loaded lazily, because `core` loads
    THIS module and an import at module scope would close the cycle."""
    if parti:
        return parti
    pid = plan.get("parti")
    if not pid or not isinstance(pid, str):
        return None
    core = _mod("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))
    return core.load_parti(pid)


def massing_bays(massing):
    """What the massing states about its own bay count, read CONSERVATIVELY.

    `bays` is prose across the catalogue -- "5", "3-5", "variable", "irregular", "5-7 main",
    "3 (narrow end to street)", "1 per face" -- so this reads only the two forms it can be sure
    of, a bare integer and a bare range, and reports every other as UNREADABLE rather than
    guessing. "5-7 main" is refused deliberately: the word `main` is doing work (the count is of
    the main block of a multi-element house) and a reader that dropped it would state a fact
    about the wrong thing.

    Returns {"min", "max", "stated", "readable"}; `readable` False means the massing said
    something this function may not act on, which is not the same as the massing saying nothing.
    """
    stated = (massing or {}).get("bays")
    out = {"stated": stated, "readable": False, "min": None, "max": None}
    if not isinstance(stated, str):
        return out
    t = stated.strip()
    m = re.fullmatch(r"(\d+)", t)
    if m:
        out.update(readable=True, min=int(m.group(1)), max=int(m.group(1)))
        return out
    m = re.fullmatch(r"(\d+)\s*[-–]\s*(\d+)", t)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        if lo <= hi:
            out.update(readable=True, min=lo, max=hi)
    return out


def wants_a_centre_bay(plan, parti, massing):
    """Whether this diagram needs an ODD bay count, and why, stated rather than assumed.

    A five-bay Georgian's one non-negotiable move is the door in the middle bay with two
    windows either side, and an even count has no middle bay -- so a diagram whose entrance is
    on the axis of a through-passage cannot be drawn on six bays however good the placement is.
    The corpus states this twice and neither statement had a reader: `four-over-four` says
    `bays: "5"` and *"Facade symmetry is a hard constraint, not a preference"*, and
    `centre-passage-core`'s own description says the passage *"makes the facade symmetrical
    because the door is now genuinely in the middle."*

    Two signals, and the massing's own stated count is the stronger: it is a fact about this
    record's massing rather than an inference from its circulation type. Returns (bool, why)."""
    mb = massing_bays(massing)
    if mb["readable"] and mb["min"] == mb["max"] and mb["min"] % 2 == 1:
        return True, f'the massing states {mb["stated"]} bays'
    if (parti or {}).get("circulation_parti") == "center-hall":
        return True, "a centre-hall diagram puts its door in the middle bay"
    return False, None


def derive_footprint(plan, parti=None, prep=None):
    """Bay module, bay count and footprint, with the lot cap and the growth ordering.

    Extracted from solve() in WP-2.3 so the CP-SAT solver derives its footprint from
    exactly the same rule rather than a second copy that could drift: decision #11's
    "grow the footprint before compromising a room" is a settled decision, and it should
    have one implementation. Behaviour is verbatim what solve() did inline; the pinned
    relaxation count in tests/test_geometry.py is what proves it.

    Returns a dict of footprint facts, or one carrying `error` when the lot cannot hold
    even the minimum two bays."""
    parti = parti_for(plan, parti)
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
    # WP-11.6 LAYER 4: THE CAP IS ON THE BUILT EXTENT, HYPHEN INCLUDED. Ruled 4 Sep 2026,
    # `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` item 2 -- "the hyphen
    # is roofed ground; a building whose covered area overruns its lot has overrun it". Until this
    # the cap was on the MAIN BLOCK alone, so the flanking elements were free: measured on the
    # Tidewater plan with its service rooms tagged into a west dependency, an 80 ft lot got a
    # 104 ft built extent -- 24 ft over -- and the record said `lot_capped: false`, which is the
    # placer asserting the lot did not constrain a house that overruns it.
    #
    # The flank is computable HERE, before the main block's bay count is chosen, because a
    # dependency is sized from its own rooms and its gap from its own hyphen; see `flank_sizes`,
    # which is the one spelling both this and `blocks_for` read.
    if prep is None:
        _, prep = prep_rooms(plan)
    flank = flanking_extent_ft(prep, bay)
    lot_usable = lot_usable_width_ft(plan)
    lot_maxbay = None
    if lot_usable is not None:
        for_main = lot_usable - flank
        # `int(x // bay)` where the old line said `max(1, int(lot_usable // bay))`: with no flank
        # the two agree wherever the answer is 2 or more, and both take the refusal below where it
        # is less, so the sixteen one-rectangle plans are untouched. Where they differ is a lot the
        # flank has already eaten, and there 0 is honest where 1 is a lie about a house that has
        # no room for even one bay.
        lot_maxbay = int(for_main // bay) if for_main > 0 else 0
        maxbay = min(maxbay, max(1, lot_maxbay))
        if lot_maxbay < 2:
            if flank:
                return {"error": f"lot too narrow for the built extent: {lot_usable:.0f} ft usable "
                                  f"width after side setbacks, of which the flanking element(s) and "
                                  f"their hyphen(s) take {flank:.0f} ft, leaves {for_main:.0f} ft "
                                  f"for the main block -- not this diagram's minimum 2 bays "
                                  f"({2*bay:.0f} ft) at its {bay:.0f} ft bay module. The cap is on "
                                  f"the built extent, hyphen included, and no bay count for the "
                                  f"main block makes this house fit this lot."}
            return {"error": f"lot too narrow: {lot_usable:.0f} ft usable width after side setbacks "
                              f"cannot hold even this diagram's minimum 2 bays ({2*bay:.0f} ft) at its "
                              f"{bay:.0f} ft bay module."}
    tol = bay * 0.28
    # The "no ground level" guard from main's side. It used to be signalled by prep_rooms
    # returning None for prep; that could not survive the (levels, prep) signature the CP
    # engine needs, so it is an explicit check here instead. PILE stays at module scope --
    # main's side redeclared it locally and the two copies were identical.
    # `prep` is resolved above the lot block now (the flank needs it); this is the check alone.
    if 0 not in prep or not prep[0]:
        return {"error": "no ground level"}
    a0 = sum(r["_area"] for r in prep[0])
    au = sum(r["_area"] for r in prep.get(1, []))
    m = C["massings"].get(plan.get("massing") or "", {})
    target_depth = PILE.get(m.get("depth_rooms"), 32.0)
    need = max(a0, au)
    # OQ 55, found by building it: on a void-bearing massing `depth_rooms` describes the RANGE,
    # not the block. `courtyard-full` and `courtyard-u` both read `single-pile` -- correctly, the
    # ranges around a court ARE one room deep -- and crossing the block you pass range, corredor,
    # court, corredor, range. Feeding the court's area into a 22 ft depth target produced a
    # 121 x 24.6 ft strip with the patio inside it: the right area, a shape that is not the
    # diagram, and a house nobody could build. The massing's own `footprint` field is what
    # distinguishes them -- "courtyard" has ranges on both sides of the void, "U" on one -- and
    # the void band's depth is the reserved area over the block width, which is why this is
    # recomputed inside the growth loop rather than fixed before it.
    void_sf = sum(r["_area"] for r in prep[0] if isinstance(r.get("_void"), dict))
    void_ranges = {"courtyard": 2, "u": 1}.get((m.get("footprint") or "").strip().lower())
    if void_ranges is not None and void_sf:
        base_depth = void_ranges * target_depth
        def depth_for(width): return base_depth + void_sf / max(width, 1.0)
    else:
        void_ranges = None
        def depth_for(width): return target_depth
    # WP-11.2. THE MASSING'S OWN BAY COUNT IS THE STARTING POINT, AND ITS PARITY SURVIVES
    # GROWTH. Until this the count came only from the area arithmetic below, so
    # `four-over-four`'s `bays: "5"` had no reader and the shipped Tidewater sheet was drawn
    # SIX bays wide under a title that says five -- and an even count has no middle bay, which
    # is where a Georgian door goes. The growth loop steps by TWO on a diagram that wants a
    # centre bay, so a five-bay house that will not fit becomes seven and never six.
    odd_wanted, odd_why = wants_a_centre_bay(plan, parti, m)
    mb = massing_bays(m)
    step = 2 if odd_wanted else 1
    from_area = max(2, min(maxbay, round((need / target_depth) / bay)))
    start = from_area
    if mb["readable"]:
        # the massing's stated minimum is a floor on the diagram, not a target for the area:
        # a house with more program than five bays hold grows, and one with less does not
        # shrink below the count its own massing names.
        start = max(mb["min"], from_area)
        if mb["max"] is not None:
            start = min(start, max(mb["max"], from_area))
    if odd_wanted and start % 2 == 0:
        # THE BUMP MAY NOT CROSS THE LOT (WP-11.6 layer 4). It used to, and that is one of the two
        # ways the cap was bypassed: on a lot holding six bays this line made a seven-bay house,
        # 3 ft over, on a ONE-RECTANGLE plan -- so the bypass was never about massing elements at
        # all. And `bay_count_forced_even` twenty lines below says "today the only way here is a
        # lot too narrow to hold the odd count", which was unreachable for exactly this reason:
        # the bump made the count odd whatever the lot said, so the lot could never force an even
        # one. A refusal that cannot fire, with a comment naming the case it cannot fire in.
        if lot_maxbay is None or start + 1 <= lot_maxbay:
            start += 1
    grown, bays = [], max(2, start)
    growth_ceiling = catalog_maxbay + 3
    if lot_maxbay is not None: growth_ceiling = min(growth_ceiling, lot_maxbay)
    while True:
        W = bays * bay
        H = need / W
        # grow the footprint before compromising a room — the stated infeasibility ordering.
        # `depth_for(W)` rather than the bare `target_depth` main's side used: on a ring massing
        # the pile describes the RANGE and the block's target is ranges x pile PLUS the void
        # band (OQ 55), so a fixed target shrinks a courtyard block to a light well.
        if H <= depth_for(W) * 1.18 or bays + step > growth_ceiling: break
        bays += step; grown.append(bays)
    floor_bays = max(2, mb["min"] if mb["readable"] else 2)
    while bays - step >= floor_bays and \
            need / ((bays - step) * bay) <= depth_for((bays - step) * bay) * 1.18:
        bays -= step
    # OQ 55: on a ring massing the bay count decides the COURT's proportion, not just the
    # block's, and the court's proportion is the number the diagram turns on --
    # rooms/courtyard.json says so at length ("below about 0.8 the court is a light well...
    # above about 3.0 it has stopped being a court"). The growth-and-shrink loops above are
    # written for a block that holds rooms, and left alone they shrank this block to 4 bays and
    # made the court a 16 x 40 slot: in band for area, out of band for the one ratio that
    # matters. So on a ring massing the bay count is re-chosen against the courtyard room's own
    # `proportion` band, which is the corpus deciding rather than this function.
    if void_ranges is not None and void_sf:
        court = next((r for r in prep[0] if isinstance(r.get("_void"), dict)
                      and not r["_void"].get("roofed")), None)
        prop = ((C["rooms"].get((court or {}).get("type"), {}).get("dimensions") or {})
                .get("proportion")) if court else None
        if court and prop:
            aim = (prop[0] + prop[1]) / 2.0
            scored = []
            for b in range(2, int(growth_ceiling) + 1):
                Wb = b * bay; Hb = need / Wb
                dd = ring_depth(Wb, Hb, court["_area"], 4 if void_ranges == 2 else 3)
                if dd is None: continue
                cw = Wb - 2 * dd
                chh = (Hb - 2 * dd) if void_ranges == 2 else (Hb - dd)
                if cw <= 0 or chh <= 0: continue
                ar = max(cw, chh) / min(cw, chh)
                penalty = 0.0 if prop[0] <= ar <= prop[1] else min(abs(ar - prop[0]), abs(ar - prop[1])) * 10
                scored.append((penalty + abs(ar - aim), b))
            if scored:
                bays = min(scored)[1]
    W = round(bays * bay, 2); H = round(need / W, 2)
    # `tol` is carried in the dict (main's side) so solve_heuristic and geometry_cp read one
    # relaxation allowance rather than each recomputing it. The void keys are OQ 55's.
    # A diagram that wanted a centre bay and did not get one is a REFUSAL, named -- not a
    # silent six. Today the only way here is a lot too narrow to hold the odd count.
    forced_even = bool(odd_wanted and bays % 2 == 0)
    return {"bay": bay, "tol": tol, "bays": bays, "W": W, "H": H,
            "wants_centre_bay": odd_wanted, "centre_bay_why": odd_why,
            "bay_count_forced_even": forced_even,
            "massing_bays": mb["stated"], "massing_bays_readable": mb["readable"],
            "massing_min_bays": mb["min"] if mb["readable"] else None,
            "slack": (W * H) - max(a0, au),
            "grown": grown, "lot_usable": lot_usable, "lot_maxbay": lot_maxbay,
            "flank": flank, "built_extent": round(W + flank, 2),
            "catalog_maxbay": catalog_maxbay, "growth_ceiling": growth_ceiling,
            "target_depth": round(depth_for(W), 2), "range_depth": target_depth,
            "void_ranges": void_ranges, "void_sf": round(void_sf), "need": need}


# What `geometry_report.score` MEANS, said where the number is built rather than left to the
# reader. It is a sum of penalties -- 10 a unit of area error, 12 a room under its band, 14 a
# missing exterior wall, 1.5 an off-grid relaxation -- so LOWER IS BETTER and the argmin wins.
# Raised by the adversarial audit of the candidate-score fix (26 Aug 2026) as the same defect
# one layer down: compose.py published a demerit total under the word "score" and every reader
# took the biggest number for the winner. This one is not renamed, because it is consumed by
# tests/test_solver.py's benchmark and by mcp_server/core.py as a comparison quantity and not
# as a grade -- but it now says which way it runs everywhere it is printed or published.
DEMERIT_NOTE = ("The score is a DEMERIT TOTAL: lower is better, no ceiling, and the best "
                "placement is the smallest number. It is not the candidate score compose.py "
                "publishes, which is out of 100 and runs the other way. ")

def _lot_block(fp):
    """What the lot did to this placement, measured on the BUILT EXTENT (WP-11.6 layer 4).

    Written once because both engines must say the same thing -- `_over_band_block`'s own reason,
    one function up.

    THE EXTENT IS THE ROOFED GROUND, HYPHEN INCLUDED, which is the ruling of 4 Sep 2026 on
    `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` item 2 and not an
    implementation choice. Until this the record carried `lot_capped` alone, which is a claim
    about the MAIN BLOCK'S BAY COUNT, and it was published as `false` -- "the lot did not
    constrain this house" -- over a built extent 24 ft wider than the lot it names. A boolean
    about one rectangle cannot answer a question about a building.

    THREE STATES, NEVER TWO: a plan that states no lot width gets COULD NOT EVALUATE and is not
    told it fits."""
    usable = fp.get("lot_usable")
    flank = fp.get("flank") or 0.0
    extent = fp.get("built_extent")
    if extent is None: extent = fp.get("W")
    made_of = (f" ({fp.get('W'):.1f} ft of main block and {flank:.1f} ft of flanking element(s) "
               f"and hyphen(s))") if flank else ""
    out = {"usable_width_ft": usable, "built_extent_ft": extent, "flanking_ft": flank,
           "main_block_ft": fp.get("W")}
    if usable is None:
        out["over_ft"] = None
        out["note"] = ("COULD NOT EVALUATE: this plan states no lot width, so the built extent is "
                       "reported, nothing is capped, and nothing is claimed to fit.")
        return out
    over = round(extent - usable, 2)
    out["over_ft"] = max(0.0, over)
    if over <= 0:
        out["note"] = (f"The built extent is {extent:.1f} ft{made_of} within {usable:.1f} ft of "
                       f"usable lot width.")
        return out
    # THE RESIDUE IS NAMED RATHER THAN LEFT AS A NUMBER. The cap bounds the growth loop and the
    # centre-bay parity bump; it does NOT overrule the massing's own stated minimum bay count,
    # because nobody has ruled that a lot outranks a diagram's floor and silently shrinking below
    # it would compromise the diagram to save the site -- decision #11's ordering in reverse.
    mmin, bays, lmb = fp.get("massing_min_bays"), fp.get("bays"), fp.get("lot_maxbay")
    why = ""
    if mmin and bays is not None and bays <= mmin and lmb is not None and lmb < mmin:
        why = (f" The main block is at its massing's own stated minimum of {mmin} bays and the lot "
               f"holds {lmb}: the cap bounds the growth loop and the parity bump and does not "
               f"overrule the diagram's floor. Whether it should is "
               f"oq/a-lot-too-narrow-for-the-diagrams-own-minimum-bay-count.")
    out["note"] = (f"OVER THE LOT BY {over:.1f} ft: a built extent of {extent:.1f} ft{made_of} on "
                   f"{usable:.1f} ft of usable lot width.{why}")
    return out


def _over_band_block(ob):
    """The report block, written once because both engines must say the same thing."""
    by_record = [r for r in ob if r["declared_over_ceiling"]]
    return {
        "count": len(ob), "rooms": ob,
        "declared_over_ceiling": len(by_record),
        "note": ("Rooms placed above the ceiling of their own catalogue band. This is "
                 "REPORTED and deliberately not charged: the slicer tiles the footprint "
                 "exactly, so an over-band charge is an under-band charge plus a constant "
                 "(measured: three formulations, not one room changed size), and "
                 "`level_score` already bills area error symmetrically. Where "
                 "`declared_over_ceiling` is true the room was over its ceiling AS "
                 "DECLARED and the placement is not the author of it. See over_band()'s "
                 "own docstring for the identity and the measurements."
                 if ob else "Every room was placed at or below the ceiling of its own band.")}


def over_band(rects_by_level, prep):
    """Rooms this layout placed ABOVE the ceiling of their own catalogue band.

    WP-6.3, and the shape of it is a finding. The obvious move was to mirror `under_band`
    with a matching CHARGE in `level_score`, so that a passage placed 63% over its
    declaration would cost a candidate something. That was measured and refused, because
    the slicer tiles the footprint EXACTLY: with `Sum(got)` fixed at the block area T,

        Sum max(0, got - hi)  ==  (T - Sum hi)  +  Sum max(0, hi - got)

    is an identity, not an approximation — verified to under 0.5 sf on both levels of the
    shipped plan. So "penalise a room over its ceiling" IS "penalise a room under its
    ceiling", plus a constant. It pushes every room UP; it does not oppose `under_band`,
    it amplifies it. On the Tidewater upper level the term is 96.3% constant (an
    irreducible floor of 671 sf against 697 placed) and its coefficient of variation
    across all 250 candidates is 4.67%. Three formulations — flat 12 a room, proportional,
    per-square-foot — were run through the whole search: **not one room changed size**, and
    the score moved by exactly the predicted constant.

    Over-size is also already charged. `level_score` bills `abs(got - want)/want * 10`,
    which is symmetric, and the upper passage already pays 6.3 of it. What produces the
    +63% is that `1/want` weighting routing unavoidable slack to the LARGEST room, which is
    a deliberate allocation; an over-band charge normalised by `hi` has the same gradient
    and would reinforce it.

    And the slack is the RECORD's, not the placement's: the Tidewater upper storey is
    programmed at 1,621 sf inside a block sized by the 2,405 sf ground floor. No placement
    can absorb 784 sf. Charging for it would convict the solver of the brief's arithmetic —
    the OQ 52 family of error. SIX rooms on that plan are over their band ceiling AS
    DECLARED, before any placement runs (`landing` 108 against 60, `hallbath` 88 against 70,
    `linen` 15 against 6, and `passage`, `powder`, `chamber2`), which is the same point
    again. Note that this is not the same set as `declared_over_ceiling` below, which counts
    only rooms the placement ALSO put over the ceiling: five, because `passage` is declared
    at 408 against a 400 ceiling and is then placed under it. The two numbers answer
    different questions and a reader meeting them together should be told which.

    So this REPORTS and does not charge, and it says which of the two cases each room is:
    over its ceiling because it was declared that way, or because the placement put it
    there. The drawn layer in build/plan_check.py is where a reader is told about it."""
    out = []
    for idx, rects in rects_by_level.items():
        for r in prep.get(idx, []):
            rect = rects.get(r["id"])
            if not rect:
                continue
            got = rect[2] * rect[3]
            _lo, hi = band(r["type"])
            if hi and got > hi + 0.5:
                declared = (r.get("width_ft") or 0) * (r.get("length_ft") or 0)
                out.append({"room": r["id"], "name": r.get("name") or r["id"],
                            "type": r["type"], "placed_sf": round(got),
                            "band_ceiling_sf": round(hi),
                            "over_by_pct": round(100 * (got - hi) / hi),
                            # the distinction that stops this reading as an accusation
                            "declared_over_ceiling": bool(declared and declared > hi + 0.5)})
    return sorted(out, key=lambda d: -d["over_by_pct"])


def under_band(rects_by_level, prep):
    """Rooms this layout placed below the floor of their own catalogue band.

    OQ 54, ruled 24 Aug 2026. `level_score` charges a flat 12 points for a room under its band
    and a candidate can win the search while paying it, so the spec Colonial's dining room comes
    out at 91 sf against a 122 sf floor -- on every seed. Nothing reported it: the plan RECORD
    still says 12 x 12, only the placement shrinks the room, and `plan_check.py` never reads
    `room.geometry`, so no layer of the critic was looking at the number that changed.

    The ruling was to report it here rather than to make the search refuse (which could leave a
    brief with no candidate and no explanation) or to teach the critic to read geometry (a much
    larger change every plan layer would feel). The search keeps its freedom to trade a room's
    size against everything else, which is what a heuristic is for. It stops doing it silently.

    WP-6.4 closed an asymmetry with `over_band`, which has read the DECLARATION since it was
    written and carries `declared_over_ceiling` so a room the brief made oversized is not
    blamed on the placement. This read only the catalogue band, so a kitchen declared 16 x 20
    and placed at 63% of that was invisible here unless it ALSO crossed the catalogue floor --
    and the catalogue floor is the looser of the two tests for a generously declared room. It
    now carries the declared figure alongside the band one. The two are different questions
    and the entry says which is which: `short_by_pct` is against the type's catalogue floor,
    `declared_short_by_pct` is against what this plan actually asked for."""
    out = []
    for idx, rects in rects_by_level.items():
        for r in prep.get(idx, []):
            rect = rects.get(r["id"])
            if not rect: continue
            got = rect[2] * rect[3]
            lo, _hi = band(r["type"])
            floor = lo * 0.85
            if got < floor - 0.5:
                e = {"room": r["id"], "name": r.get("name") or r["id"], "type": r["type"],
                     "placed_sf": round(got), "band_floor_sf": round(floor),
                     "short_by_pct": round(100 * (floor - got) / floor)}
                declared = (r.get("width_ft") or 0) * (r.get("length_ft") or 0)
                if declared:
                    e["declared_sf"] = round(declared)
                    # signed: a room can sit under its catalogue floor and still be at or over
                    # what the brief asked for, and calling that a shortfall would be the OQ 52
                    # error -- convicting the placement of the record's own arithmetic
                    e["declared_short_by_pct"] = round(100 * (declared - got) / declared)
                out.append(e)
    return sorted(out, key=lambda d: -d["short_by_pct"])


def voids_report(rects_by_level, prep, ring=None):
    """What was reserved, where, and what it cost the heated area (OQ 55).

    Shared with build/geometry_cp.py so both engines report the reservation identically -- the
    drawing is a render of the data, and two engines describing the same court two different
    ways would put that guarantee back in doubt. `ring` is the heuristic's own ring-layout
    tally and is None for the constraint solver, which does not lay out a ring: it inherits the
    heuristic's slicing tree as its topology and refines it."""
    voids = []
    for idx, rects in sorted(rects_by_level.items()):
        for r in prep.get(idx, []):
            if not isinstance(r.get("_void"), dict) or r["id"] not in (rects or {}): continue
            x, y, w, h = rects[r["id"]]
            voids.append({"room": r["id"], "name": r.get("name") or r["id"], "type": r["type"],
                          "level": idx, "area_sf": round(w * h),
                          "roofed": bool(r["_void"].get("roofed"))})
    return {
        "count": len(voids), "rooms": voids,
        "ring_layout": ring,
        "reserved_sf": round(sum(v["area_sf"] for v in voids if v["level"] == 0)),
        "note": ("Reserved voids: placed and dimensioned like any other room, excluded from the "
                 "heated envelope, drawn open (OQ 55). The block was sized to hold them, so the "
                 "footprint is larger than the heated area by the reserved figure -- that is the "
                 "diagram being honoured rather than the house being inflated. An unroofed void "
                 "is a hole in the roof plane; nothing is placed over it, and the roof pass is "
                 "told so rather than left to span it." if voids
                 else "No reserved voids on this plan.")}


def _record_prep(levels):
    """The ground rooms `blocks_record` measures, filtered exactly as the SLICER filters them.

    The two call sites below built this dict inline and did NOT apply `is_placed()`, which the
    slicing path applies in `prep_rooms`. So a room the placer never gives a rectangle to -- an
    outdoor room with no `void.within_footprint`, a terrace -- still counted toward its block's
    area and toward the side its `exterior_walls` vote for. Measured on a synthetic dependency
    holding a garage and a terrace: the sliced element was 20 x 22 ft holding one room, and the
    element WRITTEN INTO THE RECORD was 50 x 20.8 holding two -- a rectangle no room occupies,
    in the field a reader takes for the building's shape.

    One function with two callers, for the same reason `plan_check.furniture_shortfalls` is: the
    two spellings were identical when written and drifted the moment one of them was right.
    """
    return {0: [dict(r, _area=(r.get("width_ft") or 10) * (r.get("length_ft") or 12))
                for r in levels[0]["rooms"] if is_placed(r.get("type"))]}


def multi_element_disclosure(plan):
    """What a multi-element placement does NOT yet judge, stated on the record (OQ 40).

    The block machinery places a dependency beside the house and both renderers draw it there.
    ONE layer below it still reads `footprint.width_ft/depth_ft` as though it were the whole
    building (six until WP-11.6, which taught `openings`, `structure`, `vertical_score`, the lot
    cap and `plan_check`'s drawn layer; their entries below are kept for the record and marked),
    and each was wrong in its own direction on a dependency room -- measured, not supposed, by an
    adversarial audit of the change that introduced blocks. **This count is written out in words
    and the list below it is the record; the WORD said FIVE for two commits while the list held
    three**, which is why the machine-readable answer is `not_element_aware` and never this
    sentence:

      openings   TAUGHT AT WP-11.6 and no longer in the list. It got the MAIN block's W and H,
                 so on the reference fixture a dependency at x -41..-14 touched no boundary at
                 all and NINE of fourteen declared openings came back `unplaced` saying "the
                 placement puts this room on no such boundary wall" -- a refusal produced by the
                 instrument rather than by the house. `envelopes()` maps a room to its own
                 element by the `block` tag the placer itself groups on.
      structure  TAUGHT AT WP-11.6 and no longer in the list. `wall_lines` swept every placed
                 room into one envelope, so a dependency partition became a bearing line beyond
                 W and the gap between the elements could be spanned; the dependency itself got
                 no envelope walls at all (measured 0 of 2). `build_section` runs the three
                 structure functions once per element now, at the element's own origin.
      vertical   TAUGHT AT WP-11.6, and the entry's own description of it was half wrong. The
                 support-credit it named is UNREACHABLE (the upper level is always inside the
                 main block and dependency lines always outside it, 14 ft away at the closest
                 against a 0.75 ft tolerance). What was real is the other sign: a `stacks_over`
                 claim naming a room in another element was charged 40 points for a failure no
                 placement could avoid. Unjudged now, with its reason.
      lot        TAUGHT AT WP-11.6, and the bypass turned out not to be about elements at all.
                 The cap is on the BUILT EXTENT now, hyphen included (the ruling's item 2), and
                 `flank_sizes` is the one spelling this and `blocks_for` both read. But the probe
                 that measured 24 ft over an 80 ft lot found TWO bypasses and the second is on
                 every plan: the centre-bay parity bump ignored the cap, so a lot holding six bays
                 got a seven-bay ONE-RECTANGLE house. `geometry_report.lot` reports the extent,
                 the flank and the overrun in three states.
      critic     TAUGHT AT WP-11.6. The drawn layer's four `touches` tests read the room's own
                 element (`openings.envelopes`, layer 1's map, not a second spelling), and where
                 a wall of that element looks across the gap at another element the finding SAYS
                 SO -- exterior to the weather, interior to the view, which is ruling 4's second
                 half and a sentence rather than a severity. Measured on the fixture: two
                 dependency rooms read `[]` against the main block and `['S','W']` / `['S','E']`
                 against their own, while `chamber2` and `stair` read `[]` on both.
      export_ifc `export_ifc` sizes the floor slab `W + 2*t_ext` centred on the main block, so a
                 dependency's IfcSpaces float clear of the slab under them.

    None of that is fixed here and none of it is claimed to be. It is DISCLOSED, because the
    alternative is a record that reports numbers from five instruments pointed at one rectangle
    while describing two -- and the composer emits no `block` today, so the only way to reach
    this state is a caller-supplied record, which is exactly the reader who cannot know.
    """
    fp = plan.get("footprint") or {}
    if len(fp.get("blocks") or []) < 2:
        return None
    note = {
        "elements": len(fp["blocks"]),
        # FIVE, DOWN FROM SIX (WP-11.6). `openings` is taught: `openings.envelopes()` maps each
        # room to its OWN element's rectangle and `_boundary_walls` tests against that instead of
        # the main block. Measured on the reference fixture, dependency openings refused fell
        # 9 -> 5, and the five that remain are honest -- a kitchen whose north edge is 23.72
        # against its element's 29.12 really does not reach that face.
        #
        # **THE FALLING COUNT IS THE RULING'S OWN CHECK** ("must name five, then four, then none
        # -- a falling count, in the record, is how this ruling is checked rather than claimed").
        # Do not remove a name here until the layer it names reads the element. The order is
        # ruled and it is not arbitrary: openings first, because it makes the dependency's
        # windows real and therefore turns `structure`'s missing envelope into a DRAWN collision
        # rather than a silent absence.
        # FOUR, down from five (WP-11.6 layer 2). `structure` is taught: `build_section` runs
        # `wall_lines`/`bearing_lines`/`span_check` ONCE PER ELEMENT over that element's own
        # rooms, with the element's own origin. Measured on the reference fixture: the main
        # element's wall set no longer carries the dependency's partition (an x line at -23.3 on
        # a 0-63 block), the dependency has its own two envelope walls where it had 0 of 2, and
        # no span is computed across the gap. **The dependency's own structure is judged for the
        # first time and immediately fails**: 27.0 ft and 20.07 ft against a 20 ft hand-framed
        # capacity. That is the shield lesson arriving as the ruling predicted -- teaching
        # openings made its windows real, teaching structure makes its spans real.
        # THREE, down from six (WP-11.6 layers 1-3). `vertical_score` is taught, and ONE HALF OF
        # WHAT THE ENTRY SAID ABOUT IT WAS NEVER REACHABLE, which is worth more than the fix.
        #
        # The entry's claim -- "an upper wall within 0.75 ft of a dependency wall line scores as
        # continues to a wall below, where there is no upper floor at all" -- CANNOT FIRE with
        # this placer. `blocks_for` lays only level 0 into elements, so every upper room is
        # inside the main block and every dependency line is outside it; on the reference
        # fixture the nearest dependency face is 14 ft away, which is the hyphen's own default
        # gap against a 0.75 ft tolerance. Measured, not reasoned: 0 upper edges within
        # tolerance of any of -41.0, -23.3, -14.0.
        #
        # What WAS reachable is the opposite sign: a `stacks_over` claim naming a room in
        # another element was CHARGED 40 points and told "is drawn clear of it", when no
        # placement this engine can produce could satisfy it. It is COULD NOT EVALUATE now, with
        # its reason. Measured on the fixture: vertical_score 114 -> 74.
        #
        # The wet-stack test needed no change and that was measured too: an upper bath over a
        # kitchen that has moved into a detached dependency really does sit over no wet room.
        # TWO, down from six (WP-11.6 layers 1-4). The lot cap is on the built extent now, and
        # the finding that came with it is that ITS BYPASS WAS NEVER ABOUT ELEMENTS: the
        # centre-bay parity bump crossed the cap on a one-rectangle plan (a lot holding six bays,
        # a seven-bay house, 3 ft over), and `bay_count_forced_even` -- the refusal whose own
        # comment says "today the only way here is a lot too narrow to hold the odd count" --
        # could not fire, because the bump made the count odd whatever the lot said.
        #
        # A residue is DISCLOSED rather than capped: the massing's own stated minimum bay count
        # still outranks the lot, so a five-bay diagram on a lot holding four is 9 ft over and
        # `geometry_report.lot.note` says exactly that and names the question.
        # ONE, down from six (WP-11.6 layers 1-5). `plan_check`'s drawn layer is taught, and
        # the finding that came with it was recorded two layers earlier: teaching `openings` had
        # made this layer's SYMPTOM vanish (landlocked findings 2 -> 0) without touching its
        # arithmetic, so a meter watching the finding would have crossed this name off at layer 1.
        # Driving the condition -- stripping the placement from the dependency's windows -- is
        # what kept it honest, and it is what the guard does now.
        "not_element_aware": ["export_ifc"],
        "note": ("COULD NOT EVALUATE for these layers: this placement has more than one massing "
                 "element and each of the layers named reads footprint.width_ft/depth_ft as the "
                 "whole building. Openings on a dependency wall, spans across the gap, upper-wall "
                 "support, the lot cap and the drawn exterior-wall test are all unreliable here. "
                 "Teaching them about elements is a package of its own."),
    }
    off = sorted({r["id"] for lv in plan.get("levels", [])
                  if (lv.get("index") or 0) != 0
                  for r in lv.get("rooms", []) if is_block_tag(r.get("block"))})
    if off:
        # The schema admits `block` on any room; the placer only ever reads level 0.
        note["ignored_tags_above_ground"] = off
        note["note"] += (f" And {len(off)} room(s) above the ground level carry a `block` tag that "
                         "the placer does not read -- they were placed in the main rectangle.")
    return note


def blocks_record(plan, fp, prep):
    """`footprint.blocks` for the record, or None on a one-rectangle house (OQ 40).

    Returns None rather than a single-entry list when there is one element, and that is
    deliberate: every plan in this corpus is one rectangle, and writing a `blocks` key onto all
    sixteen of them would be a schema-visible change to records nothing has asked to change.
    The footprint scalars beside it already describe the main block and always have."""
    blocks = blocks_for(plan, fp, prep, 0)
    if len(blocks) < 2:
        return None
    out = []
    for b in blocks:
        row = {"id": b["id"], "role": b["role"], "x_ft": float(b["x"]), "y_ft": float(b["y"]),
               "width_ft": float(b["W"]), "depth_ft": float(b["H"]),
               "area_sf": round(b["W"] * b["H"])}
        if b.get("attached_to"): row["attached_to"] = b["attached_to"]
        out.append(row)
    return out


def write_record(plan, levels, ground, upper, fp, report):
    """Write coordinates, footprint and geometry_report back into the plan record.

    Shared with build/geometry_cp.py so both engines emit an identically-shaped record --
    the drawing is a render of the data (decision #11), and two engines writing two
    slightly different records would make that guarantee engine-dependent."""
    void_sf = 0.0
    for idx, lv in levels.items():
        src = ground if idx == 0 else (upper if idx == 1 else {})
        for r in lv["rooms"]:
            if r["id"] in src:
                x, y, w, h = src[r["id"]]
                r["geometry"] = {"x_ft": x, "y_ft": y, "width_ft": round(w, 2), "depth_ft": round(h, 2),
                                 "area_sf": round(w * h)}
                # OQ 55: the record says on the rect itself whether it is a reserved void, so
                # every downstream consumer -- the renderer, the structure pass, the roof pass,
                # anything that reads a plan file it did not solve -- can tell without going
                # back to the room catalogue. `heated: false` is the operative claim; `roofed`
                # says whether anything may sit above it.
                v = void_spec(r["type"])
                if v:
                    r["geometry"]["void"] = {"heated": False, "roofed": bool(v.get("roofed"))}
                    if idx == 0: void_sf += w * h
    gross = fp["W"] * fp["H"]
    plan["footprint"] = {"width_ft": fp["W"], "depth_ft": fp["H"], "bays": fp["bays"],
                         "bay_module_ft": fp["bay"], "area_sf": round(gross),
                         "slack_sf": round(fp["slack"])}
    _blocks = blocks_record(plan, fp, _record_prep(levels)) if levels.get(0) else None
    if _blocks: plan["footprint"]["blocks"] = _blocks
    if void_sf:
        # area_sf keeps its meaning -- the block, outside the reserved voids as much as inside
        # them, which is what the roof spans and the lot must hold. What it never meant and
        # was silently taken for was the heated area, so that is now stated separately rather
        # than left to be inferred from a number that does not carry it.
        # Derived from the two rounded figures rather than rounded independently, so the three
        # numbers in the record add up. A footprint block that is out by a square foot invites
        # exactly the doubt this ruling exists to remove.
        plan["footprint"]["void_area_sf"] = round(void_sf)
        plan["footprint"]["heated_area_sf"] = plan["footprint"]["area_sf"] - round(void_sf)
        plan["footprint"]["area_note"] = (
            "area_sf is the gross block: what the roof spans and the lot must hold. "
            "heated_area_sf takes out the reserved voids (OQ 55) -- they are placed and "
            "dimensioned, and they are not conditioned space.")
    if fp.get("lot_usable") is not None:
        plan["footprint"]["lot_usable_width_ft"] = round(fp["lot_usable"], 1)
    plan["geometry_report"] = report
    _me = multi_element_disclosure(plan)
    if _me: report["multi_element"] = _me
    return plan


def solve_heuristic(plan, parti=None, candidates=250, seed=7, level_aware=True):
    """The hill-climbing search. Named `solve_heuristic` since the 25 Aug merge: `solve()`
    below is now a dispatcher that prefers the CP-SAT engine and falls back to this one.

    `level_aware` (WP-7.1, OQ 95) slices the upper level against the ground layout instead of
    blind. It is TRUE for a placement and FALSE for a CP warm-start, and that split is a
    measured necessity rather than a preference. A hint's only job is to be REPAIRABLE; a
    placement's job is to be right, and they are not the same job. Measured on
    `plans/tidewater-georgian-careful.json`, the plan WP-6.3 fought to make solvable at all:
    hinting CP-SAT with the level-aware run took it from OPTIMAL to UNKNOWN at its 25 s
    budget, so the whole sheet fell back to the hill-climb. A better hint by this file's own
    score was a worse basin for the proof. `geometry_cp.py::_hint_heuristic` therefore asks
    for the blind run, and CP's own placement is unchanged byte for byte."""
    rng = random.Random(seed)
    levels, prep = prep_rooms(plan)
    if prep is None or 0 not in prep: return {"error": "no ground level"}
    fp = derive_footprint(plan, parti, prep)
    if "error" in fp: return {"error": fp["error"]}
    bay, bays, W, H = fp["bay"], fp["bays"], fp["W"], fp["H"]
    grown, lot_maxbay, catalog_maxbay = fp["grown"], fp["lot_maxbay"], fp["catalog_maxbay"]
    lot_usable, slack, tol = fp["lot_usable"], fp["slack"], fp["tol"]

    # WP-2.2: composition_parti (the style's kit) and entrance_faces (the plan's own context)
    # feed the compositional scoring terms below. composition_parti is read for completeness
    # and future use, per PLAN-OF-ACTION.md's task list -- as of this package no style's kit
    # actually specifies it (status: empty everywhere), so nothing here branches on its value
    # yet; entrance_faces is what every term below actually keys off, and it is already on
    # every plan this solver has ever been run against (context.entrance_faces).
    composition_parti = ((C["kits"].get(plan.get("style") or "") or {}).get("slots") or {}).get("composition_parti")
    ewalls = entrance_walls(plan)
    void_shape = (C["massings"].get(plan.get("massing") or "", {}).get("footprint") or "")

    # OQ 55: on a courtyard massing the ground level is laid out as ranges around the court
    # rather than searched for, because the search cannot find a ring (see courtyard_slice).
    # `ring_sides` is None for every other massing, and everything below is then untouched.
    ring_sides = {"courtyard": 4, "u": 3}.get(void_shape.strip().lower())
    ring_used = ring_failed = 0

    # loaded once per solve rather than once per candidate: it is a file read, and the span
    # charge below is only affordable because nothing in it touches the disk
    try:
        _floor = _mod("structure", f"{ROOT}/build/structure.py").load_construction()["floor"]
    except Exception:
        _floor = None

    gblocks = blocks_for(plan, fp, prep, 0)
    # room id -> the element's own rectangle, so exterior_score charges a wing room against the
    # wing's walls and not against the main block's. One element -> every room maps to 0,0,W,H,
    # which is exactly what the function did before it took this argument.
    gbounds = {rid: (b["x"], b["y"], b["W"], b["H"]) for b in gblocks for rid in b["rooms"]}
    best = None
    # DECLARED STACKING AS A RULE RATHER THAN A CHARGE (WP-11.5). Two incumbents: the best
    # candidate overall, and the best that breaks NO claim its own author wrote. The strict one
    # wins if it exists.
    #
    # IT IS NOT A `continue`, AND THAT IS THE WHOLE DESIGN. Rejecting a breaking candidate
    # outright empties the pool on any plan whose claims the slicing tree cannot satisfy, and an
    # empty pool is a placement failure where the corpus wants a stated compromise. When no
    # strict candidate exists the search SAYS SO on the record and falls back to the charge it
    # has always paid -- a silent fallback would be a hard rule that is not one.
    best_strict = None
    for _ in range(candidates):
        gr, grelax = {}, []
        drew = False
        if ring_sides:
            drew = courtyard_slice(copy.deepcopy(prep[0]), W, H, bay, tol, rng, gr, grelax, ring_sides)
            if drew: ring_used += 1
            else: gr, grelax, ring_failed = {}, [], ring_failed + 1
        if not drew:
            # OQ 40: one slice per massing element. With one element -- every plan in this
            # corpus today -- `gblocks` is a single entry at 0,0 holding every room in prep's
            # own order, so this is the same single call with the same rng draws it always was.
            for _b in gblocks:
                _rs = [r for r in prep[0] if r["id"] in set(_b["rooms"])]
                if _rs:
                    slice_rect(copy.deepcopy(_rs), _b["x"], _b["y"], _b["W"], _b["H"],
                               bay, tol, rng, gr, grelax)
        sg = (level_score(gr, prep[0]) + exterior_score(gr, prep[0], W, H, bounds=gbounds) + adjacency_score(gr, prep[0], levels[0]["rooms"])
              + entrance_score(gr, prep[0], W, H, ewalls) + principal_and_service_score(gr, prep[0], W, H, ewalls)
              + ceremonial_score(gr, prep[0], W, H, ewalls) + centre_hall_symmetry_score(gr, prep[0], W, H)
              + void_enclosure_score(gr, prep[0], W, H, void_shape))
        ur, urelax = {}, []
        if prep.get(1):
            # WP-7.1 (OQ 95): the upper level is sliced AGAINST THE GROUND LAYOUT, not blind.
            # `gr` is fully populated four lines above and was simply never passed, so
            # `vertical_score` below has always been scoring candidates produced with no
            # knowledge of what they must sit on. Nothing else changes: the rng stream is
            # untouched (no new draws), so the slicing TREE is identical candidate for
            # candidate and only the cut POSITIONS move -- onto the walls below where one is
            # within tolerance, and onto the bay line exactly as before where none is.
            below = None
            if level_aware:
                gx, gy = wall_lines(gr)
                below = {"x": gx, "y": gy, "rects": gr, "W": W, "H": H}
            slice_rect(copy.deepcopy(prep[1]), 0, 0, W, H, bay, tol, rng, ur, urelax,
                       below=below)
            su = (level_score(ur, prep[1]) + exterior_score(ur, prep[1], W, H) + adjacency_score(ur, prep[1], levels[1]["rooms"])
                  + centre_hall_symmetry_score(ur, prep[1], W, H))
        else: su = 0.0
        vs, vnotes = vertical_score(gr, ur, prep[0], prep.get(1, []), plan)
        _breaks = len(stack_breaks_only(gr, ur, prep.get(1, []),
                                        element_of(plan, prep[0]))) if (ur and STACK_HARD) else 0
        # WP-7.4 (OQ 97): the structural check the corpus already runs, run here too. See
        # _span_charge -- this is structure.span_check itself and not a proxy.
        #
        # THE EARLY-OUT IS EXACT, NOT AN APPROXIMATION, and it is here because the check is
        # the most expensive thing in this loop: it rebuilds each level's room records and
        # runs structure.wall_lines' O(n^2) shared-segment scan, which took a 250-candidate
        # solve from 0.21 s to 0.57 s -- and `solve_heuristic` is what the workbench's wall
        # drag calls by name. `_span_charge` can only ever ADD, so a candidate already at or
        # above the incumbent cannot win however few spans it has, and skipping it changes no
        # outcome. Most candidates lose, so most never pay for the check.
        part = sg + su + vs + 1.5 * len(grelax + urelax)
        if best is not None and part >= best["_raw"]:
            continue
        try:
            spc, sp_over = _span_charge({0: gr, 1: ur}, prep, W, H, bay, plan.get("style"), _floor)
        except Exception:
            # The catalogue LOAD is guarded above; the CALL was not, so a floor-structure.json
            # missing `light_frame_joist_spans` (KeyError) or holding an empty list (ValueError
            # out of max()) took down the whole placement, while an unreadable file degraded to
            # a stated COULD NOT EVALUATE. Same failure, two behaviours. Now one: unjudged.
            spc, sp_over = 0.0, None
        tot = part + spc
        # Compare raw against raw. "score" is stored rounded to 1dp, so comparing an
        # unrounded challenger against it let a strictly WORSE candidate win whenever
        # rounding nudged the incumbent up: 40.06 stores as 40.1, and a 40.08 challenger
        # satisfies 40.08 < 40.1. The error is bounded at 0.05, but it meant a
        # 250-candidate search did not reliably return its own argmin.
        # ONE ROW, TWO INCUMBENTS (WP-11.5). Built once and shared by reference: an earlier
        # draft built it twice and the two copies are a second transcription waiting to drift.
        # Nothing downstream mutates a row.
        _row = None
        if ((best is None or tot < best["_raw"])
                or (_breaks == 0 and (best_strict is None or tot < best_strict["_raw"]))):
            _row = {"_raw": tot, "_breaks": _breaks,
                    "score": round(tot, 1), "ground": gr, "upper": ur, "vnotes": vnotes,
                    # Level stamped as the two lists merge — slice_rect does not know which
                    # storey it is slicing, and a mark has to know which plan it belongs on (OQ 33).
                    "relaxations": ([dict(r, level=0) for r in grelax]
                                    + [dict(r, level=1) for r in urelax]),
                    "sg": round(sg, 1), "su": round(su, 1), "sv": round(vs, 1),
                    "span_charge": round(spc, 1), "spans_over_capacity": sp_over}
        if _row is not None and (best is None or tot < best["_raw"]):
            best = _row
        if _row is not None and _breaks == 0 and (best_strict is None
                                                  or tot < best_strict["_raw"]):
            best_strict = _row

    # THE STRICT WINNER TAKES IT IF ONE EXISTS (WP-11.5), and the record says which happened.
    # `declared` is the denominator: a plan with no `stacks_over` claim at all takes this branch
    # with `claimed: 0` and the rule is vacuous on it, which is stated rather than implied.
    _claimed = (sum(1 for r in prep.get(1, []) if r.get("stacks_over"))
                if STACK_HARD else 0)
    _stacking = {"claimed": _claimed,
                 "rule": "hard" if (_claimed and best_strict is not None) else "charge"}
    if _claimed and best_strict is not None:
        if best_strict is not best:
            _stacking["cost_points"] = round(best_strict["_raw"] - best["_raw"], 1)
            _stacking["note"] = (
                f"A candidate satisfying all {_claimed} declared stacking claim(s) was preferred "
                f"over a cheaper one that broke "
                f"{best['_breaks']}, at {_stacking['cost_points']} points.")
        else:
            _stacking["note"] = (f"The best candidate overall already satisfied all {_claimed} "
                                 f"declared stacking claim(s); the rule cost nothing.")
        best = best_strict
    elif _claimed:
        # NOT A SILENT FALLBACK. No candidate in the pool satisfied every claim, so the search
        # is paying STACK_W instead and the sheet must be able to say so -- a hard rule that
        # quietly becomes a charge is worse than the charge, because a reader then believes the
        # claims were honoured.
        _stacking["note"] = (
            f"NO CANDIDATE of {candidates} satisfied all {_claimed} declared stacking claim(s); "
            f"the best breaks {best['_breaks']} and is charged {STACK_W:g} points for each. The "
            f"rule fell back to the charge and this note is the disclosure.")
        _stacking["broken"] = best["_breaks"]

    # --- write coordinates back into the plan (write_record does it, below)
    rel = best["relaxations"]
    report = {
        "score": best["score"], "ground_score": best["sg"], "upper_score": best["su"], "vertical_score": best["sv"],
        "bays_grown": fp["grown"],
        "lot_capped": (fp["lot_maxbay"] is not None and fp["lot_maxbay"] < fp["catalog_maxbay"]),
        "lot": _lot_block(fp),
        "relaxations": {"count": len(rel),
                        "max_off_grid_ft": round(max(r["off_ft"] for r in rel), 2) if rel else 0,
                        # P7: counted AND locatable. Each mark carries the axis it cuts across,
                        # where it sits, and its extent, so the sheet can draw it in place
                        # instead of only tallying it (OQ 33).
                        "marks": rel,
                        "note": ("Cuts taken off the bay line to make a room fit. Each one is a joist run that "
                                 "does not land on a bearing line and a window bay that will not centre." if rel
                                 else "Every cut landed on a bay line.")},
        "vertical": best["vnotes"] or ["Every upper wall continues to a wall below and every stack lands."],
        "stacking": _stacking,
        "reading": (DEMERIT_NOTE +
                    "Ground and upper were solved together and scored as a pair, so an upper "
                    "layout that would score LOWER alone is rejected when it leaves walls "
                    "unsupported.")}
    # WP-7.4 (OQ 97). Reported for exactly the reason `under_band` below is: the search now
    # TRADES against this, and a trade the record does not carry is a trade nobody can see. An
    # over-capacity span is a defect that survives the building, so the count is stated whether
    # it is zero or not -- and `None` is the third state, meaning the construction catalogue
    # could not be read and the span was never evaluated. A zero there would read as "nothing
    # exceeds capacity", which is the OQ 52 lie in the cheapest possible place.
    _spo = best.get("spans_over_capacity")
    report["span_capacity"] = {
        "over_capacity": _spo,
        "charge": best.get("span_charge"),
        "weight": SPAN_W,
        "note": ("COULD NOT EVALUATE -- construction/floor-structure.json was unreadable, so no "
                 "span was checked and none is claimed clear." if _spo is None else
                 "Every clear span between bearing lines is within its framing capacity."
                 if not _spo else
                 f"{_spo} clear span(s) exceed the capacity their framing tradition states. The "
                 f"search charges each in proportion to how far over it is and trades that "
                 f"against everything else it scores; build/structure.py's section report names "
                 f"them individually.")}
    ub = under_band({0: best["ground"], 1: best["upper"]}, prep)
    report["over_band"] = _over_band_block(
        over_band({0: best["ground"], 1: best["upper"]}, prep))
    report["under_band"] = {
        "count": len(ub), "rooms": ub,
        "note": ("Rooms placed below the floor of their own catalogue band. The search is allowed to "
                 "trade a room's size against everything else it is scoring, and it charges itself 12 "
                 "points each time -- but the plan record still carries the room's DECLARED size, and "
                 "nothing downstream reads these coordinates, so without this list the trade is "
                 "invisible. A room below its band is a defect that survives the life of the building. "
                 "build/geometry_cp.py refuses to make this trade at all (OQ 54)." if ub
                 else "Every room was placed at or above the floor of its own catalogue band.")}
    report["voids"] = voids_report(
        {0: best["ground"], 1: best["upper"]}, prep,
        ring=(None if not ring_sides else
              {"sides": ring_sides, "used": ring_used, "fell_back": ring_failed,
               "note": ("Ground laid out as ranges around the court, stated as a guillotine tree "
                        "rather than searched for." if ring_used else
                        "Courtyard massing, but the ring could not be built -- the block cannot "
                        "hold the declared court with ranges deep enough to be rooms, so the "
                        "ordinary search ran instead and the court is a notch in the block, not "
                        "a court. Read the drawing before believing the plan.")}))
    return write_record(plan, levels, best["ground"], best["upper"], fp, report)


def _finish(plan, best, fpd, levels, solver=None, infeasible=None):
    """Write a placement back into the plan record. Main's side extracted this so the CP engine
    and the heuristic emit the same record shape; `solve()` below calls it for the CP path.
    `solver` names which engine produced this placement and why; `infeasible` carries the CP
    engine's named conflict set when the declared facts cannot all hold and this drawing is the
    labelled least-bad relaxation.

    OQ 55 on this path: the CP engine does not yet lay out a courtyard RING -- that is stated as
    a guillotine tree in courtyard_slice() and the heuristic owns it -- but the footprint's void
    accounting is derived from the same fpd, so a CP-produced record still says what is reserved
    and what is heated rather than silently reporting the gross block as conditioned space. The
    remaining gap (a CP-placed ring) is recorded in docs/geometry.md rather than papered over.
    """
    W, H, bays, bay = fpd["W"], fpd["H"], fpd["bays"], fpd["bay"]
    for idx, lv in levels.items():
        src = best["ground"] if idx == 0 else (best["upper"] if idx == 1 else {})
        for r in lv["rooms"]:
            if r["id"] in src:
                x, y, w, h = src[r["id"]]
                r["geometry"] = {"x_ft": x, "y_ft": y, "width_ft": round(w, 2),
                                 "depth_ft": round(h, 2), "area_sf": round(w * h)}
    plan["footprint"] = {"width_ft": W, "depth_ft": H, "bays": bays, "bay_module_ft": bay,
                         "area_sf": round(W * H), "slack_sf": round(fpd["slack"])}
    _blocks = blocks_record(plan, fpd, _record_prep(levels)) if levels.get(0) else None
    if _blocks: plan["footprint"]["blocks"] = _blocks
    void_sf = fpd.get("void_sf") or 0
    if void_sf:
        plan["footprint"]["void_area_sf"] = round(void_sf)
        plan["footprint"]["heated_area_sf"] = plan["footprint"]["area_sf"] - round(void_sf)
        plan["footprint"]["area_note"] = (
            "area_sf is the gross block: what the roof spans and the lot must hold. "
            "heated_area_sf takes out the reserved voids (OQ 55) -- they are placed and "
            "dimensioned, and they are not conditioned space.")
    if fpd.get("lot_usable") is not None:
        plan["footprint"]["lot_usable_width_ft"] = round(fpd["lot_usable"], 1)

    # The report is built HERE, not by the caller. The 25 Aug merge moved the shared
    # report block into solve_heuristic (which augments it with under_band and voids) and
    # left this path writing into a `geometry_report` that did not exist yet -- a KeyError
    # on every CP-produced placement, which main's own test_check_plans_solve_with_stated
    # _downgrades caught immediately.
    rel = best.get("relaxations") or []
    plan["geometry_report"] = {
        "score": best.get("score"), "ground_score": best.get("sg"),
        "upper_score": best.get("su"), "vertical_score": best.get("sv"),
        # WP-7.4: the CP path builds its report from named keys, so a term added to `_score`
        # reaches the record only if it is named here too. It was not, and the span charge the
        # CP acceptance comparison now uses was computed and dropped -- the same shape as the
        # bug this package opened with.
        "span_capacity": {
            "over_capacity": best.get("spans_over_capacity"),
            "charge": best.get("span_charge"),
            "weight": SPAN_W,
            "note": ("COULD NOT EVALUATE -- construction/floor-structure.json was unreadable, "
                     "so no span was checked and none is claimed clear."
                     if best.get("spans_over_capacity") is None else
                     "Every clear span between bearing lines is within its framing capacity."
                     if not best.get("spans_over_capacity") else
                     f"{best.get('spans_over_capacity')} clear span(s) exceed the capacity their "
                     f"framing tradition states; build/structure.py's section report names "
                     f"them individually.")},
        "bays_grown": fpd.get("grown"),
        "lot_capped": (fpd.get("lot_maxbay") is not None
                       and fpd["lot_maxbay"] < fpd.get("catalog_maxbay", 10 ** 9)),
        "lot": _lot_block(fpd),
        "relaxations": {
            "count": len(rel),
            "max_off_grid_ft": round(max(r["off_ft"] for r in rel), 2) if rel else 0,
            "marks": rel,        # P7, on the CP path too (OQ 33)
            "note": ("Cuts taken off the bay line to make a room fit. Each one is a joist run "
                     "that does not land on a bearing line and a window bay that will not "
                     "centre." if rel else "Every cut landed on a bay line.")},
        "vertical": best.get("vnotes")
                    or ["Every upper wall continues to a wall below and every stack lands."],
        "reading": (DEMERIT_NOTE +
                    "Ground and upper were solved together and scored as a pair, so an upper "
                    "layout that would score LOWER alone is rejected when it leaves walls "
                    "unsupported.")}
    # OQ 54 and OQ 55 must be reported on BOTH engines. `solve_heuristic` builds these with
    # its own prep and ring tally; here they are derived from the plan, because a guarantee
    # that holds only on the fallback engine is not a guarantee. `ring=None` is honest: the CP
    # engine does not lay out a ring (see OQ 55), and voids_report says so rather than
    # implying one was placed.
    _levels, _prep = prep_rooms(plan)
    _rects = {idx: {r["id"]: (r["geometry"]["x_ft"], r["geometry"]["y_ft"],
                              r["geometry"]["width_ft"], r["geometry"]["depth_ft"])
                    for r in lv["rooms"] if r.get("geometry")}
              for idx, lv in (_levels or {}).items()}
    ub = under_band(_rects, _prep)
    plan["geometry_report"]["over_band"] = _over_band_block(over_band(_rects, _prep))
    plan["geometry_report"]["under_band"] = {
        "count": len(ub), "rooms": ub,
        "note": ("Rooms placed below the floor of their own catalogue band (OQ 54)." if ub
                 else "Every room was placed at or above the floor of its own catalogue band.")}
    plan["geometry_report"]["voids"] = voids_report(_rects, _prep, ring=None)
    if solver:
        plan["geometry_report"]["solver"] = solver
    if infeasible:
        plan["geometry_report"]["infeasible"] = infeasible
    return plan


_SOLVE_CACHE = {}
# A plan larger than this is solved and returned but never cached — see solve(). 1 MB is ~40x
# the largest record in plans/ and small enough that 64 of them cannot matter.
MAX_CACHEABLE_BYTES = 1024 * 1024

def solve(plan, parti=None, candidates=250, seed=7, engine="auto", time_limit_s=25.0):
    # 25 s default, not 15: both reference plans need ~20-30 s of CP — a budget
    # that can never finish them makes "auto" a tax that always ships the
    # heuristic anyway (found in the WP-2.3 audit)
    """The placement entry point every consumer calls (WP-2.3 dispatcher).

    engine="auto" (default): the CP-SAT engine (build/geometry_cp.py) when
    OR-Tools is available — hard constraints on the record's own declared
    facts, a named conflict set on infeasibility — falling back to the
    heuristic search when the library is absent or the solver runs out of
    time, with the reason named in geometry_report.solver either way.
    engine="cp" | "heuristic" force one engine.

    On a proven-infeasible plan (per the 25 Aug ruling): geometry_report
    carries the named conflict set AND the heuristic's least-bad placement,
    clearly labelled — the partner hears the refusal and still sees a drawing.

    Results are memoized per process (deep-copied out) because the
    structure→roof→elevation chain and the test suite solve the same record
    many times over, and a CP solve is not free the way the slicer was.
    Read the RETURNED record — on a cache hit the argument is left untouched,
    so the old solve-then-read-the-argument idiom is unreliable now.

    time_limit_s is a target, not a hard wall: the CP phases carry small
    minimum budgets so a retry is never starved, and a 15 s limit can take
    ~20 s of wall clock on a hard record before falling back.
    """
    if engine not in ("auto", "cp", "heuristic"):
        return {"error": f"unknown engine {engine!r} — one of auto, cp, heuristic",
                "unsolved": True}
    # the parti's CONTENT keys the cache, not its id: an id-less parti stub
    # (tests build them) or two partis sharing an id must never collide
    plan_s = json.dumps(plan, sort_keys=True, default=str)
    parti_s = json.dumps(parti, sort_keys=True, default=str) if parti else None
    # HASHED, not stored. The key used to be the serialised plan itself, and 64 of those were
    # retained — so a caller posting a large record 64 times pinned 64 copies of it in the key
    # alone, on top of 64 deep-copied results. A plan record arrives over HTTP; its size is
    # the caller's choice. sha256 makes the key constant-size whatever the record weighs.
    key = (hashlib.sha256(plan_s.encode()).hexdigest(),
           hashlib.sha256(parti_s.encode()).hexdigest() if parti_s else None,
           candidates, seed, engine, time_limit_s)
    hit = _SOLVE_CACHE.get(key)
    if hit is not None:
        return copy.deepcopy(hit)
    out = _solve_uncached(plan, parti, candidates, seed, engine, time_limit_s)
    # WP-6.2 — openings are placed HERE, in the one dispatcher both engines come through,
    # so a CP placement and a heuristic placement carry the same kind of record and every
    # consumer (the renderers, the exporters, the drawn-house layer of plan_check) reads
    # positions rather than inventing them. Before this, a door had no wall and each
    # consumer guessed its own.
    if "error" not in out and not out.get("unsolved"):
        try:
            OP = _mod("openings", f"{ROOT}/build/openings.py")
            OP.place(out, C)
        except Exception as exc:                       # never lose a good placement to it
            out.setdefault("geometry_report", {})["openings_error"] = (
                f"could not place openings: {exc.__class__.__name__}: {exc}")
    # And a large INPUT is not remembered at all. Stated precisely because the first version of
    # this comment said "the VALUE is bounded too" and the guard below reads len(plan_s) — the
    # input, not the cached result. The result is a solved plan, strictly larger than the record
    # that produced it (~1.5x measured), so 64 entries just under the limit still retain
    # something over 100 MB. That is far better than the unbounded original and it is not the
    # bound the old sentence claimed. Every plan in plans/ is under 30 KB, so no real record is
    # affected either way.
    #
    # THE OPENINGS PASS RUNS BEFORE THE GUARD, NOT INSIDE IT (merge of main, 27 Aug 2026). The
    # two changes are orthogonal and both are wanted: openings must be placed on every result
    # this dispatcher returns, cached or not, or an over-large plan would come back with doors
    # that have no wall. Only the CACHE WRITE is size-guarded.
    if len(plan_s) <= MAX_CACHEABLE_BYTES:
        if len(_SOLVE_CACHE) > 64:
            _SOLVE_CACHE.clear()
        _SOLVE_CACHE[key] = copy.deepcopy(out)
    return out


def _solve_uncached(plan, parti, candidates, seed, engine, time_limit_s):
    if engine == "heuristic":
        out = solve_heuristic(plan, parti, candidates, seed)
        if "error" not in out:
            out["geometry_report"]["solver"] = {"engine": "heuristic", "reason": "requested"}
        return out

    # CP-SAT CANNOT PLACE A SECOND MASSING ELEMENT, AND MUST SAY SO RATHER THAN PLACE IT WRONGLY
    # (OQ 40, found by the adversarial audit of the change that made one placeable, 3 Sep 2026).
    # geometry_cp builds every room as `x = NewIntVar(0, Wi)` with `x + w <= Wi` -- one rectangle,
    # one non-negative coordinate space -- and its tiling, `_absorb`, `_snap_fpd`, the hint and the
    # objective all rest on that. Handed a plan with a dependency it did not fail; it placed the
    # dependency's rooms INSIDE the main block (the garage at x = 50 of a 0-70 block) while
    # `footprint.blocks` went on describing an element at x = 84-114. The record and the drawing
    # then disagreed about where the house is, which is the one thing Phase 6 exists to prevent --
    # and it silently flattered a published measurement, because rooms crammed into one rectangle
    # are all reachable and the fatal count looked like a proof of the composition.
    # Teaching CP about blocks is a package, not a patch. Until then this is a refusal, taken on
    # the same path as a missing ortools: `auto` falls back to the hill-climb with the reason
    # stated in `geometry_report.solver`, and the plate reads that rather than asserting a proof.
    _blocked = any(is_block_tag(r.get("block"))
                   for lv in plan.get("levels", []) for r in lv.get("rooms", []))
    if _blocked:
        if engine == "cp":
            return {"error": "could not solve with CP-SAT: this plan has more than one massing "
                             "element (a dependency), and the CP model places every room in a "
                             "single rectangle. Use the hill-climb, which states the elements.",
                    "unsolved": True}
        out = solve_heuristic(plan, parti, candidates, seed)
        if "error" not in out:
            out["geometry_report"]["solver"] = {
                "engine": "heuristic", "fallback": "engine",
                "reason": "this plan has more than one massing element and the CP model places "
                          "every room in a single rectangle; fell back to the hill-climb, which "
                          "places each element in its own"}
        return out

    try:
        # probe the exact import the engine needs — a broken or partial
        # install where `import ortools` succeeds but the sat module is
        # missing must take the honest fallback, not crash mid-solve
        from ortools.sat.python import cp_model  # noqa: F401 — probe only
        cp_available = True
    except ImportError:
        cp_available = False
    if not cp_available:
        if engine == "cp":
            return {"error": "could not solve with CP-SAT: the ortools package is not installed "
                             "(pip install ortools).", "unsolved": True}
        out = solve_heuristic(plan, parti, candidates, seed)
        if "error" not in out:
            out["geometry_report"]["solver"] = {
                "engine": "heuristic",
                "reason": "ortools is not installed — the CP-SAT engine (WP-2.3) is the real "
                          "solver; this placement is the 250-candidate hill-climb and its "
                          "compositional terms are preferences, not proven constraints"}
        return out

    GC = _mod("geometry_cp", f"{ROOT}/build/geometry_cp.py")
    res = GC.solve_cp(plan, parti, seed=seed, time_limit_s=time_limit_s, candidates=candidates)
    if "error" in res:
        return res
    if res.get("infeasible"):
        # the ruling: named conflict set + the least-bad drawing, clearly labelled
        out = solve_heuristic(plan, parti, candidates, seed)
        if "error" in out:
            out["infeasible"] = res["infeasible"]
            return out
        out["geometry_report"]["solver"] = {
            "engine": "heuristic (least-bad, labelled)",
            "reason": "CP-SAT proved the declared facts cannot all hold; this drawing is the "
                      "heuristic's least-bad relaxation and the conflicts below say what it relaxes"}
        out["geometry_report"]["infeasible"] = res["infeasible"]
        return out
    if res.get("unsolved"):
        if engine == "cp":
            # forced-cp means PROVE or refuse — quietly shipping the heuristic
            # placement would let the "prove" button return an unproven drawing
            return {"error": f"could not solve with CP-SAT in {time_limit_s:.0f}s "
                             f"({res.get('status', '?')}) — no placement was proven; "
                             f"engine=\"auto\" falls back to the heuristic and says so",
                    "unsolved": True, "status": res.get("status")}
        out = solve_heuristic(plan, parti, candidates, seed)
        if "error" not in out:
            # WHY it fell back, as a machine-readable word beside the sentence. UNKNOWN means
            # the solver ran and could not decide inside the budget — a loaded machine, and a
            # genuinely unjudged state. Anything else (MODEL_INVALID, or a status this code
            # does not recognise) means the model or the engine is broken, which is a failure
            # and must never be mistaken for the first case. They used to share one sentence,
            # so a test discriminating on the words could not tell them apart: tests/test_solver.py
            # skipped on a structurally invalid model and check_all stayed green. Found by an
            # adversarial audit of the OQ 66 work.
            status = res.get("status", "?")
            out["geometry_report"]["solver"] = {
                "engine": "heuristic",
                "fallback": "budget" if status == "UNKNOWN" else "engine",
                "status": status,
                "reason": f"CP-SAT returned no solution in {time_limit_s:.0f}s "
                          f"({status}); fell back to the hill-climb"}
        return out
    return _finish(plan, res["best"], res["fpd"], res["levels"], solver=res["solver"])

# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--out"); ap.add_argument("--svg")
    ap.add_argument("--parti"); ap.add_argument("--candidates", type=int, default=250)
    # `--engine`, matching solve()'s own parameter. This was `--solver heuristic|cp|both`
    # against build/solver.py until the 25 Aug merge: two sessions built WP-2.3 independently
    # and geometry_cp.py is the engine that survived, so the flag now names the dispatcher's
    # own vocabulary rather than a second solver's.
    ap.add_argument("--engine", default="auto", choices=["auto", "cp", "heuristic"],
                    help="auto (default: the CP-SAT engine when OR-Tools is present, falling "
                         "back to this file's search with the reason named in "
                         "geometry_report.solver), or force one of cp / heuristic")
    ap.add_argument("--time", type=float, default=25.0, help="CP time budget, seconds")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    parti = json.load(open(f"{ROOT}/partis/{a.parti}.json")) if a.parti else None
    out = solve(plan, parti, a.candidates, engine=a.engine, time_limit_s=a.time)
    if "error" in out:
        print(out["error"])
        for r in (out.get("conflict") or {}).get("requirements", []): print(f"    · {r}")
        return
    fp, gr = out["footprint"], out["geometry_report"]
    print(f"\n  {plan['name']}")
    print(f"  footprint {fp['width_ft']} x {fp['depth_ft']} ft, {fp['bays']} bays of {fp['bay_module_ft']} ft, {fp['area_sf']} sf gross")
    # WP-7.4 audit: the decomposition has to ADD UP. It listed ground, upper and vertical while
    # `score` also carried the span charge and the relaxation tax, so the Tidewater plan printed
    # 714.6 against parts summing to 644.7 -- 69.9 unexplained, which is the 70.0 span charge.
    # A breakdown a reader cannot reconcile with its own total is worse than no breakdown.
    _sc = (gr.get("span_capacity") or {}).get("charge") or 0.0
    _rx = 1.5 * (gr.get("relaxations") or {}).get("count", 0)
    print(f"  score {gr['score']} — LOWER IS BETTER, it counts what the placement costs "
          f"(ground {gr['ground_score']}, upper {gr['upper_score']}, "
          f"vertical {gr['vertical_score']}, spans {_sc}, relaxations {_rx:g})")
    print(f"  relaxations {gr['relaxations']['count']}, worst {gr['relaxations']['max_off_grid_ft']} ft off the bay line")
    for n in gr["vertical"][:6]: print(f"    · {n}")
    if a.out: json.dump(out, open(a.out, "w"), indent=1, ensure_ascii=False); print(f"  wrote {a.out}")
    if a.svg:
        rp = _mod("render_plan", f"{ROOT}/build/render_plan.py")
        rp.render(out, a.svg); print(f"  wrote {a.svg}")
    print()

if __name__ == "__main__":
    main()
