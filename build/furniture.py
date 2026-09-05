#!/usr/bin/env python3
"""Arranging what a room holds — the packer, and the free-run subtraction under it.

WP-11.3. Two things live here and both were lifted out of `build/openings.py` rather than
copied, because a second spelling of one rule is the failure this corpus meets most often:

  `free_runs(lo, hi, blocked)`      -- was `openings._free`
  `pack_against_walls(...)`         -- was the body of `openings.fixture_pass`

**IT IS A LEAF AND MUST STAY ONE. Nothing here may import a sibling.** `structure.py` loads
`geometry.py`, which calls `openings.place`, so anything in the placement path that reaches
back up closes an import cycle. `build/storeys.py` (WP-9.6) and `build/assemblies.py` (WP-11.2)
answer this the same way and both say so in their own headers; `openings.py` re-exports
`_free = furniture.free_runs` so every existing caller is unchanged and there is exactly ONE
implementation.

**THE PACKER'S OUTPUT FOR FIXTURES IS BYTE-IDENTICAL TO WHAT WP-7.4 SHIPPED, AND THAT IS A
HARD REQUIREMENT RATHER THAN A COURTESY.** `tests/test_furniture_drawn.py` pins the drawn
furniture-fit counts as an EQUALITY (86 across, 69 along) and re-solves all sixteen plans to
get them, so a placement that moves by a hundredth of a foot fails the build. Every comment
WP-7.2 and WP-7.4 wrote about WHY this algorithm is shaped as it is travels with the code.

WHAT THIS FILE DELIBERATELY DOES NOT DO: the fit arithmetic. `plan_check.furniture_shortfalls`
is the one spelling of *whether a room can hold a thing*, and `tests/test_furniture_drawn.py`
greps every `build/*.py` for that function's clearance expression to keep it so. (This sentence
named the expression itself in its first draft and the guard duly failed the build -- a plain
substring scan cannot tell prose from code, and the guard is right.) This file answers a
different question -- *where does the thing go* -- and never sizes a room. `docs/model.md`: "A room's size
comes from its programme and its catalogue band ... the furniture is arranged into the room as
given." Authority runs one way and this file is downstream of it.
"""
from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WALL_ORDER = ("S", "N", "W", "E")


def free_runs(lo, hi, blocked):
    """`(lo, hi)` minus every `(a, b)` in `blocked`, as a list of open runs.

    Was `openings._free`. `plan_check.py` carries a THIRD inline spelling of this same
    subtraction in its wall-run check; that one is a known duplicate and is not this file's
    to move, but do not add a fourth."""
    free = [(lo, hi)]
    for a, b in blocked:
        nxt = []
        for s, e in free:
            if b <= s or a >= e:
                nxt.append((s, e))
                continue
            if a > s:
                nxt.append((s, min(a, e)))
            if b < e:
                nxt.append((max(b, s), e))
        free = nxt
    return [(s, e) for s, e in free if e - s > 1e-6]


def pack_against_walls(rect, room_id, occupied, entries, noun="fixtures", placed=None):
    """Seat each entry against a wall of `rect`, respecting what `occupied` already holds.

    `rect` is `(x, y, w, d)` in plan feet. `occupied` is the placement's own
    `{(room_id, wall): [(lo, hi), ...]}` map of wall spans already taken by doors and windows;
    it is READ and never written -- a fixture is a 2-D rectangle and that map holds 1-D spans,
    so a later pass learns about this one through `placed`, not through `occupied`.

    `entries` is a list of dicts, in the order they should be tried:
        {"spec": {"item": str, "w_in": float, "d_in": float}}   -- pack this
        {"emit": {...}}                                          -- append verbatim, pack nothing
    The second form is how a caller reports something it could not even size, in its own words
    and in the right place in the list.

    `placed` seeds the collision set with rectangles some earlier pass already drew in this
    room, so furniture can be kept off the fixtures. Returns `(layout, placed)`.

    ---- everything below this line is WP-7.2's and WP-7.4's, moved and not rewritten ----

    WP-7.2: the wall with the longest CLEAR run, not simply the longest wall. Packing against
    the longest wall regardless of what is already on it reported the powder room's water
    closet and basin as unfittable because its 11 ft south wall was 9 ft spoken for, while its
    east wall stood empty. A fixture refused on a wall nobody tried is a false "cannot fit",
    and this corpus is built to distinguish evaluated-and-failed from not-looked-at.

    WP-7.4: THE RUN TURNS THE CORNER. WP-7.2's version then packed every fixture onto that one
    wall -- the same error one level up, and it surfaced the moment WP-7.4's score terms moved a
    room: `spec-builder-colonial`'s primary bath is 9 x 18 ft, its four fixtures want 22 ft, its
    longest clear run is 17.2 ft, and its other three walls stood empty. Each wall keeps its own
    cursor and an item tries the wall it is already on first, so a room whose items all fit on
    one wall packs BYTE-IDENTICALLY to before.

    A SEAT IS ACCEPTED ONLY IF THE RECTANGLE IT PRODUCES IS REALLY FREE. The first version of
    this reserved the corner by starting a newly opened wall past the deepest fixture placed
    anywhere in the room, and called that "conservative". It is not: every wall packs from its
    LOW end, and the four low ends are four different corners, so the reserve guards the SW
    corner and does nothing for NE, pushes W into N at NW and S into E at SE. Measured over a
    sweep of 81 plausible primary-bathroom sizes, 60 came out with a drawn fixture overlapping
    another or sitting outside the room. Nothing in the corpus's own 16 plans showed it, which
    is exactly why it needed measuring rather than reasoning about. The approximation is gone: a
    candidate seat is now turned into its actual rectangle and rejected if it leaves the room or
    touches anything already placed, which also covers the OPPOSITE-wall case (a 6 ft room
    cannot hold a 5.5 ft fixture on W and a 5 ft one on E) that no corner rule could ever have
    caught."""
    x, y, w, d = rect
    cand = []
    for wall in WALL_ORDER:
        along = wall in ("S", "N")
        wrun = w if along else d
        wbase = x if along else y
        wfree = sorted(free_runs(wbase, wbase + wrun, occupied.get((room_id, wall), [])))
        longest = max((b - a for a, b in wfree), default=0.0)
        # ties break on the longer wall, then S/W, so an unobstructed room packs exactly
        # as it did before this change
        cand.append((-longest, -wrun, WALL_ORDER.index(wall), wall, along, wrun, wbase, wfree))
    cand.sort()
    walls = {c[3]: {"along": c[4], "run": c[5], "base": c[6], "free": c[7],
                    "clear": -c[0], "cursor": 0.0} for c in cand}
    order = [c[3] for c in cand]
    wall = order[0]
    layout = []
    placed = list(placed or [])   # (x, y, w, d) of everything already drawn in this room

    def _seat_rect(cw, seat, fw, fd):
        """The rectangle a seat on `cw` would occupy, or None if it leaves the room."""
        along = walls[cw]["along"]
        if along and fd > d + 1e-6: return None
        if not along and fd > w + 1e-6: return None
        off = (y if cw == "S" else y + d - fd) if along else (x if cw == "W" else x + w - fd)
        return ((seat, off, fw, fd) if along else (off, seat, fd, fw))

    def _clear_of_placed(rect_):
        for q in placed:
            if (min(rect_[0] + rect_[2], q[0] + q[2]) - max(rect_[0], q[0]) > 1e-6
                    and min(rect_[1] + rect_[3], q[1] + q[3]) - max(rect_[1], q[1]) > 1e-6):
                return False
        return True

    for entry in entries:
        if "emit" in entry:
            layout.append(entry["emit"])
            continue
        spec = entry["spec"]
        fw = spec["w_in"] / 12.0
        fd = spec["d_in"] / 12.0
        # the wall it is already on first, then every other wall in clear-run order; and
        # within a wall every free segment, not only the first that is wide enough
        seat = seat_rect = None
        # fg-wall-run, the one READING among the placement rules: an item whose own sentence
        # states a run of wall unbroken by openings may only sit in a segment that long. Five
        # items in the catalogue carry the figure; WP-7.4 withdrew a sixth rather than loosen
        # the test, and that is the standard.
        min_run = float(spec.get("min_run_ft") or 0.0)
        for cw in [wall] + [o for o in order if o != wall]:
            W_ = walls[cw]
            for lo, hi in W_["free"]:
                if min_run and (hi - lo) + 1e-6 < min_run:
                    continue
                start = max(lo, W_["base"] + W_["cursor"])
                while hi - start >= fw - 1e-6:
                    cand_rect = _seat_rect(cw, start, fw, fd)
                    if cand_rect is not None:
                        cand_rect = to_record(cand_rect)   # judge what will be written
                    if cand_rect is not None and _clear_of_placed(cand_rect):
                        seat, seat_rect, wall = start, cand_rect, cw
                        break
                    if cand_rect is None:
                        break        # too deep for this wall's room dimension: no seat fits
                    start += 0.5     # step along and try again past the obstruction
                if seat is not None: break
            if seat is not None: break
        if seat is None:
            tried = ", ".join(f"{o} {walls[o]['clear']:.1f} ft clear of {walls[o]['run']:.1f}"
                              for o in order)
            out = {"item": spec["item"], "width_ft": round(fw, 2),
                   "depth_ft": round(fd, 2)}
            for k in ("symbol", "rule", "grade"):
                if spec.get(k) is not None:
                    out[k] = spec[k]
            # A REFUSAL NAMES ITS RULE TOO. It read `{"item", "width_ft", "depth_ft",
            # "unplaced"}` and nothing else, so an item the pass could not seat lost the
            # provenance every placed item carries -- and the grades exist precisely so a
            # reader can tell whose judgment a mark is. Found by the guard that asserts every
            # entry names its rule, on its first run.
            out["unplaced"] = {
                "reason": (f"no wall of this room has a clear run left for a {fw:.1f} x "
                           f"{fd:.1f} ft item that does not overlap what is already placed. "
                           f"All four were tried ({tried}); {noun} already placed take "
                           f"{walls[wall]['cursor']:.1f} ft of the {wall} wall"),
                "needs": {"width_ft": round(fw, 2), "depth_ft": round(fd, 2)},
                "have": {o: round(walls[o]["clear"], 2) for o in order}}
            layout.append(out)
            continue
        out = {
            "item": spec["item"],
            "wall": wall,
            # WP-7.4 audit: position and extent are rounded to the SAME precision. They were
            # 3dp and 2dp, so a fixture against the far wall came out at 2.333 + 2.67 = 5.003
            # in a 5.00 ft room -- the "against the wall it names" invariant held only to about
            # 0.005 ft, and an outside-the-room check had to be written with a tolerance loose
            # enough to hide a real 0.04 ft error.
            "x_ft": round(seat_rect[0], 3),
            "y_ft": round(seat_rect[1], 3),
            "width_ft": round(seat_rect[2], 3),
            "depth_ft": round(seat_rect[3], 3),
        }
        for k in ("symbol", "rule", "grade"):
            if spec.get(k) is not None:
                out[k] = spec[k]
        layout.append(out)
        placed.append(seat_rect)
        walls[wall]["cursor"] = (seat - walls[wall]["base"]) + fw
    return layout, placed


# ------------------------------------------------------------------- the symbols
_SYMBOLS = None


def symbols():
    """furniture/symbols.json, read once. A few primitives in a unit square per symbol, which
    each renderer maps into the item's own rectangle -- an affine map and not a construction,
    which is why both may do it. What must not be spelled twice is the SHAPE, and it is here."""
    global _SYMBOLS
    if _SYMBOLS is None:
        _SYMBOLS = json.load(open(os.path.join(ROOT, "furniture", "symbols.json")))
    return _SYMBOLS


_WORD_RE = {}


def symbol_for(item_name):
    """The symbol id for an item, by keyword, in the file's own stated order.

    A keyword table on `openings._FIXTURE_ALIASES`'s precedent: 188 distinct leading names
    cover the 219 drawn items, so an exact table would be mostly misses -- and a WRONG symbol
    is worse than a plain outline, which is why anything unmatched falls to `block`, the
    item's own rectangle, exactly as every fixture is drawn today.

    IT MATCHES A WHOLE WORD, AND THAT IS WHERE IT PARTS COMPANY WITH `_FIXTURE_ALIASES`.
    A bare substring, which is what that table uses over its nine short fixture names, drew
    `rooms/bedroom.json`'s "desk (any BEDroom occupied by anyone under twenty-five)" AS A BED
    -- caught by the guard that asserts a bedroom draws at most one bed. A plural or a
    possessive still matches, because the catalogue writes "bookcases" and "card tables"."""
    s = symbols()
    low = (item_name or "").lower()
    for sid in s["order"]:
        for kw in (s["symbols"].get(sid) or {}).get("match") or []:
            rx = _WORD_RE.get(kw)
            if rx is None:
                rx = _WORD_RE[kw] = re.compile(r"\b" + re.escape(kw) + r"(?:e?s)?(?:'s)?\b")
            if rx.search(low):
                return sid
    return "block"


# --------------------------------------------------------------- the arrangement
# WP-11.3. Everything below arranges a DRY room's furniture, from the room catalogue's own
# `furniture` array, after the openings, the stair and the wet fixtures have taken their runs.
# The rules are furniture/grammar.json's and every one of them declares a grade there saying
# how much of it is the corpus's and how much is ours. Nothing here reads or writes a room's
# dimensions: docs/model.md, on OQ 92 -- "A room's size comes from its programme and its
# catalogue band ... the furniture is arranged into the room as given."

DRAWN_KIND = "object"
MIN_PLAN_SIDE_IN = 8.0     # fg-too-thin-to-draw, and plan_check.py's own `if fw < 8`


def drawable(item):
    """Is this entry a thing a plan draws? Three-state, and the reason is returned.

    `None` means yes. Anything else is the rule id that refused it, which the caller counts
    and the plate reports -- a skipped item is a verdict here, never a silence."""
    if (item.get("kind") or DRAWN_KIND) != DRAWN_KIND:
        return "fg-not-an-object"
    fp = item.get("footprint_in") or []
    if len(fp) == 2 and min(fp) < MIN_PLAN_SIDE_IN:
        return "fg-too-thin-to-draw"
    return None


def door_swings(room, rect):
    """The rectangles this room's own doors sweep, from the record and not from a guess.

    `swing_into` names the room a leaf opens into and `hinge` which jamb it turns on -- both
    written by build/openings.py since WP-6.2, and read by NEITHER renderer, which is why a
    door arc is still recomputed from room centroids at draw time. This is their first reader.
    A leaf of width w sweeps a quarter disc of radius w; the square that contains it is what is
    blocked, which over-reserves by the corner and is the conservative direction."""
    x, y, w, d = rect
    out = []
    for o in (room.get("doors") or []):
        if o.get("unplaced") or not o.get("wall") or o.get("position_ft") is None:
            continue
        if o.get("swing_into") and o.get("swing_into") != room.get("id"):
            continue          # it opens into the other room; this one keeps its floor
        lw = float(o.get("width_ft") or 3.0)
        p = float(o["position_ft"])
        wall = o["wall"]
        if wall in ("S", "N"):
            ry = y if wall == "S" else y + d - lw
            out.append((p - lw / 2.0, ry, lw, lw))
        else:
            rx = x if wall == "W" else x + w - lw
            out.append((rx, p - lw / 2.0, lw, lw))
    return out


def to_record(r):
    """The rectangle the RECORD will carry, rounded once, here.

    WP-11.8, found by a guard on the first placement that moved under it. `_overlaps` and
    `_inside` judged the full-precision rectangle and the record then wrote `round(v, 3)`, so a
    seat computed to abut exactly could be written 0.001 ft over its neighbour: on
    `good-03-parlor-drawing-room-house` the foyer's two hall chairs ended at 33.574 against a
    coat closet beginning at 33.573. A thousandth of a foot is nothing to look at and it is a
    SECOND RECORD OF ONE FACT -- the thing this file's own WP-7.4 note two functions below is
    about, where position and extent were rounded to different precisions and an
    outside-the-room guard had to be loosened enough to hide a real 0.04 ft error.

    So the rounding happens BEFORE the collision and containment tests rather than after them,
    and what was judged is what is written. An item whose rounded rectangle no longer fits is
    refused and says so, which is the direction that cannot lie.
    """
    return (round(r[0], 3), round(r[1], 3), round(r[2], 3), round(r[3], 3))


def _overlaps(a, b):
    return (min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]) > 1e-6
            and min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]) > 1e-6)


def _inside(rect, box, tol=1e-6):
    x, y, w, d = box
    return (rect[0] >= x - tol and rect[1] >= y - tol
            and rect[0] + rect[2] <= x + w + tol and rect[1] + rect[3] <= y + d + tol)


def place_freestanding(rect, spec, blocked, step_index):
    """fg-freestanding: centred on the room, long axis along the room's, stepped for the next.

    EDITORIAL, and graded so in furniture/grammar.json: no sentence in this corpus says a
    freestanding item is centred. Returns a rectangle or None."""
    x, y, w, d = rect
    fw, fd = spec["w_in"] / 12.0, spec["d_in"] / 12.0
    long_ = fw if fw >= fd else fd
    short = fd if fw >= fd else fw
    room_is_tall = d > w
    iw, ih = (short, long_) if room_is_tall else (long_, short)
    if iw > w + 1e-6 or ih > d + 1e-6:
        return None
    cx, cy = x + w / 2.0, y + d / 2.0
    clear = max(0.5, (spec.get("clear_in") or 0) / 12.0)
    # the step alternates about the centre so a pair sits either side of it rather than
    # marching off one end
    k = (step_index + 1) // 2
    sign = 1 if step_index % 2 else -1
    off = sign * k * ((long_ if room_is_tall else short) + clear)
    r0 = ((cx - iw / 2.0, cy - ih / 2.0 + off, iw, ih) if room_is_tall
          else (cx - iw / 2.0 + off, cy - ih / 2.0, iw, ih))
    r0 = to_record(r0)                                     # judge what will be written
    if not _inside(r0, rect):
        return None
    if any(_overlaps(r0, b) for b in blocked):
        return None
    return r0


def arrange_room(room, catalogue_room, rect, occupied, blocked=None):
    """Seat one dry room's furniture. Returns `(layout, skipped)`.

    `catalogue_room` is the room TYPE's record -- this is where the furniture lives, so the
    pass reads the catalogue and writes the result onto the plan record, exactly as the
    opening grammar does. The renderers then read the record and never the catalogue, which is
    settled decision 11: nothing is drawn that is not in the record.

    `blocked` seeds the collision set with what other passes already drew -- the wet fixtures,
    and the stair well. `occupied` is the wall-span map and is read, never written."""
    skipped = {}
    entries, freestanding = [], []
    for it in (catalogue_room.get("furniture") or []):
        why = drawable(it)
        if why:
            skipped[why] = skipped.get(why, 0) + 1
            continue
        fp = it["footprint_in"]
        spec = {"item": it["item"], "w_in": fp[0], "d_in": fp[1],
                "clear_in": it.get("clearance_in") or 0,
                "symbol": symbol_for(it["item"]), "rule": None, "grade": None}
        run = it.get("needs_uninterrupted_wall_ft")
        place = it.get("placement") or "freestanding"
        if place == "freestanding":
            spec["rule"], spec["grade"] = "fg-freestanding", "editorial"
            freestanding.append(spec)
        else:
            spec["rule"] = {"against-wall": "fg-against-wall", "built-in": "fg-built-in",
                            "corner": "fg-corner"}.get(place, "fg-against-wall")
            spec["grade"] = "editorial"
            if run:
                # fg-wall-run is a READING: the figure is in the item's own sentence
                spec["rule"], spec["grade"] = "fg-wall-run", "reading"
                spec["min_run_ft"] = float(run)
            entries.append({"spec": spec})
    blocked = list(blocked or []) + door_swings(room, rect)
    layout, placed = pack_against_walls(rect, room["id"], occupied, entries,
                                        noun="furniture", placed=blocked)
    for i, spec in enumerate(freestanding):
        r0 = place_freestanding(rect, spec, placed, i)
        if r0 is None:
            layout.append({"item": spec["item"], "rule": spec["rule"], "grade": spec["grade"],
                           "width_ft": round(spec["w_in"] / 12.0, 2),
                           "depth_ft": round(spec["d_in"] / 12.0, 2),
                           "unplaced": {"reason": (
                               "the room has no clear floor at its centre for a "
                               f"{spec['w_in'] / 12.0:.1f} x {spec['d_in'] / 12.0:.1f} ft item "
                               "that does not foul a door swing, a fixture or something "
                               "already placed")}})
            continue
        layout.append({"item": spec["item"], "symbol": spec["symbol"], "rule": spec["rule"],
                       "grade": spec["grade"],
                       "x_ft": round(r0[0], 3), "y_ft": round(r0[1], 3),
                       "width_ft": round(r0[2], 3), "depth_ft": round(r0[3], 3)})
        placed.append(r0)
    # THE MARKS GO ON THE RECORD. Each renderer then draws what is there and derives nothing,
    # which is WP-6.2's own finding applied to a second layer: giving the renderers one
    # position and letting each re-derive the spacing from it put them 0.7 in apart on the
    # first plan it was tried on. A symbol id plus a rectangle is exactly that shape of
    # invitation, so the unit-square map is run ONCE, here, and the answer is written down.
    for e in layout:
        m = marks_for(e)
        if m:
            e["marks"] = m
    return layout, skipped


def marks_for(entry):
    """A placed furniture entry -> its primitives in MODEL feet, ready to draw.

    The unit square's y runs from the item's BACK to its front, so a sofa's back line lands
    against the wall it was seated on rather than wherever the model's south happens to be.
    That is the whole of the transform: a reflection or a quarter turn chosen by `wall`, and a
    scale. It lives here, once, and both renderers call it -- `derive.js` ports it and
    `tests/fixtures/sheet_symbols/` freezes this output so the two cannot drift, which is the
    same contract the openings are held to.

    Returns [] for an unplaced entry: an item that could not be seated has a reason and no
    geometry, and drawing it somewhere plausible is what this corpus refuses."""
    if entry.get("unplaced") or entry.get("x_ft") is None:
        return []
    sid = entry.get("symbol") or "block"
    sym = (symbols()["symbols"].get(sid) or symbols()["symbols"]["block"])
    x, y = float(entry["x_ft"]), float(entry["y_ft"])
    w, d = float(entry["width_ft"]), float(entry["depth_ft"])
    wall = entry.get("wall")

    def pt(u, v):
        """(u, v) in the unit square -> model feet. v = 0 is the item's back."""
        if wall == "N":       return (x + (1.0 - u) * w, y + (1.0 - v) * d)
        if wall == "W":       return (x + v * w, y + u * d)
        if wall == "E":       return (x + (1.0 - v) * w, y + (1.0 - u) * d)
        return (x + u * w, y + v * d)          # S, and freestanding: back to the south

    out = []
    for prim in sym.get("primitives") or []:
        if "rect" in prim:
            u, v, uw, vh = prim["rect"]
            xs = [pt(u, v), pt(u + uw, v), pt(u + uw, v + vh), pt(u, v + vh)]
            x0 = min(p[0] for p in xs); y0 = min(p[1] for p in xs)
            x1 = max(p[0] for p in xs); y1 = max(p[1] for p in xs)
            out.append({"rect": [round(x0, 3), round(y0, 3),
                                 round(x1 - x0, 3), round(y1 - y0, 3)]})
        elif "line" in prim:
            u1, v1, u2, v2 = prim["line"]
            a, b = pt(u1, v1), pt(u2, v2)
            out.append({"line": [round(a[0], 3), round(a[1], 3),
                                 round(b[0], 3), round(b[1], 3)]})
        elif "circle" in prim:
            u, v, r = prim["circle"]
            c = pt(u, v)
            out.append({"circle": [round(c[0], 3), round(c[1], 3),
                                   round(r * min(w, d), 3)]})
    return out
