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
furniture-fit counts as an EQUALITY (the figures are that file's, and they have moved three
times since this sentence carried a pair) and re-solves all sixteen plans to
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

# The door types `render_plan._door` draws with no leaf, spelled there (`render_plan.LEAFLESS`)
# and transcribed here because this file is a LEAF and may import no sibling;
# tests/test_furniture_pass.py holds the two tuples equal.
LEAFLESS = ("cased-opening", "open", "pocket", "garage", "bulkhead")


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


def pack_against_walls(rect, room_id, occupied, entries, noun="fixtures", placed=None, walls=None):
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
    # `walls` (WP-13.6) restricts the walls tried to the ones a positioned rule names -- the
    # wall opposite the bed, the two end walls -- in the packer's own order among them
    for wall in [o for o in WALL_ORDER if walls is None or o in walls]:
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
        if spec.get("corner"):
            # fg-corner (WP-13.6 made it real; the grammar had listed it EXECUTED with no code
            # behind it, so three catalogue items authored `corner` were seated as against-wall).
            # The first corner whose two walls both have a free run from it long enough: the
            # item's along-the-wall side on wall A, its depth on wall B, taking A in the packer's
            # own wall order and B in the same order among the perpendicular walls.
            seat_rect = None
            for cw in WALL_ORDER:
                for pw in [o for o in WALL_ORDER if walls[o]["along"] != walls[cw]["along"]]:
                    A, B = walls[cw], walls[pw]
                    # the corner's coordinate along A is B's position; along B it is A's
                    ca = (x if pw == "W" else x + w) if A["along"] else (y if pw == "S" else y + d)
                    cb = (y if cw == "S" else y + d) if A["along"] else (x if cw == "W" else x + w)
                    a_lo, a_hi = (ca, ca + fw) if pw in ("W", "S") else (ca - fw, ca)
                    b_lo, b_hi = (cb, cb + fd) if cw in ("S", "W") else (cb - fd, cb)
                    if not any(lo - 1e-6 <= a_lo and a_hi <= hi + 1e-6 for lo, hi in A["free"]):
                        continue
                    if not any(lo - 1e-6 <= b_lo and b_hi <= hi + 1e-6 for lo, hi in B["free"]):
                        continue
                    cand_rect = to_record((a_lo, b_lo, fw, fd) if A["along"] else (b_lo, a_lo, fd, fw))
                    if not _inside(cand_rect, rect) or not _clear_of_placed(cand_rect):
                        continue
                    seat_rect, wall = cand_rect, cw
                    if pw in ("W", "S"):          # the corner is A's LOW end: A packs from here
                        walls[cw]["cursor"] = max(walls[cw]["cursor"], fw)
                    break
                if seat_rect is not None:
                    break
            if seat_rect is None:
                out = {"item": spec["item"], "width_ft": round(fw, 2), "depth_ft": round(fd, 2)}
                for k in ("symbol", "rule", "grade"):
                    if spec.get(k) is not None:
                        out[k] = spec[k]
                out["unplaced"] = {
                    "reason": (f"no corner of this room has both its walls free for a {fw:.1f} x "
                               f"{fd:.1f} ft item -- every corner was tried in the wall order"),
                    "needs": {"width_ft": round(fw, 2), "depth_ft": round(fd, 2)},
                    "have": {o: round(walls[o]["clear"], 2) for o in order}}
                layout.append(out)
                continue
            out = {"item": spec["item"], "wall": wall, "corner": True,
                   "x_ft": round(seat_rect[0], 3), "y_ft": round(seat_rect[1], 3),
                   "width_ft": round(seat_rect[2], 3), "depth_ft": round(seat_rect[3], 3)}
            for k in ("symbol", "rule", "grade"):
                if spec.get(k) is not None:
                    out[k] = spec[k]
            layout.append(out)
            placed.append(seat_rect)
            continue
        # the wall it is already on first, then every other wall in clear-run order; and
        # within a wall every free segment, not only the first that is wide enough
        seat = seat_rect = None
        # fg-wall-run, the one READING among the placement rules: an item whose own sentence
        # states a run of wall unbroken by openings may only sit in a segment that long. Five
        # items in the catalogue carry the figure; WP-7.4 withdrew a sixth rather than loosen
        # the test, and that is the standard.
        min_run = float(spec.get("min_run_ft") or 0.0)
        # fg-bed-aisle (WP-13.6): an item carrying `aisle_ft` -- a bed, whose record says its
        # clearance is "30 in each side" -- keeps that much floor clear ALONG the wall either
        # side of itself, inside the wall's own extent and clear of everything placed, though
        # not necessarily clear of an opening: a door may open into a bedside aisle, and a
        # window may light it. The aisle is floor and not the item: it is not written, the
        # nightstand the record puts inside it is let in by `arrange_room`, and the wall's
        # cursor moves past it so the next item packs beyond the aisle. No fixture spec
        # carries the field, so the fixture layouts are byte-identical by construction.
        aisle = float(spec.get("aisle_ft") or 0.0)
        for cw in [wall] + [o for o in order if o != wall]:
            W_ = walls[cw]
            for lo, hi in W_["free"]:
                if min_run and (hi - lo) + 1e-6 < min_run:
                    continue
                start = max(lo, W_["base"] + W_["cursor"] + aisle)
                while hi - start >= fw - 1e-6:
                    if aisle and start + fw + aisle > W_["base"] + W_["run"] + 1e-6:
                        break        # the far aisle would leave the wall's extent
                    cand_rect = _seat_rect(cw, start, fw, fd)
                    if cand_rect is not None:
                        cand_rect = to_record(cand_rect)   # judge what will be written
                    ok = cand_rect is not None and _clear_of_placed(cand_rect)
                    if ok and aisle:
                        ok = all(a_ is not None and _clear_of_placed(to_record(a_))
                                 for a_ in (_seat_rect(cw, start - aisle, aisle, fd),
                                            _seat_rect(cw, start + fw, aisle, fd)))
                    if ok:
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
            howmany = "All four" if len(order) == 4 else f"The {len(order)} wall(s) named"
            if aisle:
                fw_words = f"{fw:.1f} x {fd:.1f} ft item with its {aisle:.1f} ft aisle either side"
            else:
                fw_words = f"{fw:.1f} x {fd:.1f} ft item"
            out = {"item": spec["item"], "width_ft": round(fw, 2),
                   "depth_ft": round(fd, 2)}
            for k in ("symbol", "rule", "grade", "piece", "of"):
                if spec.get(k) is not None:
                    out[k] = spec[k]
            # A REFUSAL NAMES ITS RULE TOO. It read `{"item", "width_ft", "depth_ft",
            # "unplaced"}` and nothing else, so an item the pass could not seat lost the
            # provenance every placed item carries -- and the grades exist precisely so a
            # reader can tell whose judgment a mark is. Found by the guard that asserts every
            # entry names its rule, on its first run.
            out["unplaced"] = {
                "reason": (f"no wall of this room has a clear run left for a {fw_words} "
                           f"that does not overlap what is already placed. "
                           f"{howmany} were tried ({tried}); {noun} already placed take "
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
        # `piece`/`of` travel with the spec: a counted catalogue item reaches this packer as
        # that many specs and each entry has to say which piece it is, or the key draws a
        # numeral per chair instead of one numeral on a set. NO SHIPPED PLAN REACHES IT --
        # swept at WP-13.6, every counted item in the corpus resolves to `fg-freestanding` or
        # to a positioned rule, so all 205 pieces are written elsewhere and the corpus is
        # byte-identical across this line. It is DRIVEN by tests/test_furniture_grammar.py.
        for k in ("symbol", "rule", "grade", "piece", "of"):
            if spec.get(k) is not None:
                out[k] = spec[k]
        layout.append(out)
        placed.append(seat_rect)
        walls[wall]["cursor"] = (seat - walls[wall]["base"]) + fw + aisle
    return layout, placed


def aisle_rects(entry, aisle_ft):
    """The two floor rectangles either side of a wall-seated entry along its wall, each
    `aisle_ft` wide and the entry's own depth deep -- what `pack_against_walls` kept clear for
    an item carrying `aisle_ft`, recomputed from the written entry so no second record of the
    seat is carried. [] for an entry on no wall or with no aisle."""
    if not aisle_ft or entry.get("x_ft") is None or not entry.get("wall"):
        return []
    x, y, w, d = entry["x_ft"], entry["y_ft"], entry["width_ft"], entry["depth_ft"]
    if entry["wall"] in ("S", "N"):
        return [(x - aisle_ft, y, aisle_ft, d), (x + w, y, aisle_ft, d)]
    return [(x, y - aisle_ft, w, aisle_ft), (x, y + d, w, aisle_ft)]


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
    blocked, which over-reserves by the corner and is the conservative direction.

    A PAIR IS TWO LEAVES OF HALF THE OPENING (WP-13.6). Until this the block was one square of
    the OPENING's width whatever the door type, so a 5 ft double door between the drawing and
    dining rooms reserved 5 x 5 ft of the dining room's floor while `render_plan._door` and
    `Sheet.jsx` draw two 2.5 ft leaves that each sweep a quarter disc of radius 2.5 -- the
    packer refusing the dining table for a swing the drawing does not make (plan §I, row 3/5/8:
    on the search placement the table for eight is refused by that block alone). The two
    squares are `w/2` along the wall each and `w/2` into the room, which is exactly the
    renderer's leaf radius (`_door`: `leaf(..., half, ...)` twice for `double`, `2 * half` once
    for a single leaf); a door type the renderer draws with no leaf (`render_plan.LEAFLESS`)
    blocks nothing, because nothing swings. `tests/test_furniture_pass.py` holds the block to
    the renderer's own leaf rule."""
    x, y, w, d = rect
    out = []
    for o in (room.get("doors") or []):
        if o.get("unplaced") or not o.get("wall") or o.get("position_ft") is None:
            continue
        if o.get("swing_into") and o.get("swing_into") != room.get("id"):
            continue          # it opens into the other room; this one keeps its floor
        if (o.get("type") or "swing") in LEAFLESS:
            continue          # a cased opening, a pocket, a garage door: no leaf swings
        lw = float(o.get("width_ft") or 3.0)
        p = float(o["position_ft"])
        wall = o["wall"]
        # (along-the-wall offset from the opening's centre, leaf width) per leaf
        leaves = [(-lw / 2.0, lw / 2.0), (0.0, lw / 2.0)] if o.get("type") == "double" \
            else [(-lw / 2.0, lw)]
        for off, leaf in leaves:
            if wall in ("S", "N"):
                ry = y if wall == "S" else y + d - leaf
                out.append((p + off, ry, leaf, leaf))
            else:
                rx = x if wall == "W" else x + w - leaf
                out.append((rx, p + off, leaf, leaf))
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


_GRAMMAR = None


def grammar():
    """furniture/grammar.json, read once. A rule's `applies_to` is the ONE spelling of which
    catalogue item it reaches (by placement, by a field, by a phrase in the item's own name
    or note) and a rule's figure (`fg-pair-facing`'s 10 ft) lives on the rule beside the
    sentence it was read from; this file reads both and re-spells neither, so a rule's reach
    and its number sit in the data where build/check_furniture.py can hold the quote."""
    global _GRAMMAR
    if _GRAMMAR is None:
        _GRAMMAR = json.load(open(os.path.join(ROOT, "furniture", "grammar.json")))
    return _GRAMMAR


# The rules that seat an item BY ANOTHER THING already on the floor or in the record -- a
# bed, a pier between two sashes, a drawn chimney breast, the room's own end walls, a table
# that names its seats. They are executed in `arrange_room` after the wall items and before
# the freestanding ones, in this order, and any of them whose stated relation has nothing to
# stand on is a named refusal, never a fallback to some other wall.
POSITIONED = ("fg-at-the-foot", "fg-beside-the-bed", "fg-between-the-windows",
              "fg-flanking-the-chimney-breast", "fg-opposite-the-bed", "fg-on-the-end-wall",
              "fg-facing-down-the-hall", "fg-pair-facing", "fg-chairs-around-the-table")


def rule_for(item):
    """The positioned rule whose `applies_to` reaches this catalogue item, or None. Read from
    the grammar -- `item_contains`, `item_startswith`, `note_contains`, case-blind -- in the
    file's own order, first match wins. A rule keyed on a `placement` or a `field` is not a
    positioned rule and is not returned here: the placement default and `fg-wall-run` are
    resolved where they always were."""
    name = (item.get("item") or "").lower()
    note = (item.get("note") or "").lower()
    for r in grammar().get("placement_rules") or []:
        a = r.get("applies_to") or {}
        if "item_contains" in a and a["item_contains"].lower() in name:
            return r["id"]
        if "item_startswith" in a and name.startswith(a["item_startswith"].lower()):
            return r["id"]
        if "note_contains" in a and a["note_contains"].lower() in note:
            return r["id"]
    return None


def rule_figure(rule_id, key):
    """A number a grammar rule states beside its quoted basis (`fg-pair-facing`'s
    `max_gap_ft`). None where the rule states none: a caller must then refuse, not default."""
    for r in grammar().get("placement_rules") or []:
        if r.get("id") == rule_id:
            v = r.get(key)
            return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    return None


def piece_count(item):
    """How many pieces the catalogue draws for this item: its authored `count` where the
    record says the footprint is ONE piece (`footprint_of: piece`), else one. A count on a
    GROUP footprint is the group drawn once -- the twin beds' [100, 80] is both beds already
    -- and a name stating a band ('six to eight side chairs') carries no `count` and is drawn
    once with the band on the key, because a band is not a count."""
    if item.get("footprint_of") == "piece" and isinstance(item.get("count"), int) \
            and not isinstance(item.get("count"), bool) and item["count"] > 1:
        return item["count"]
    return 1


_NUM_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
              "nine": 9, "ten": 10, "twelve": 12}
_SEATS_RE = re.compile(r"\b(?:seats|for)\s+(\d+|" + "|".join(_NUM_WORDS) + r")\b(\s+to\s+(?:\d+|"
                       + "|".join(_NUM_WORDS) + r")\b)?")


def seats_of(name):
    """`dining table, seats 8` -> 8; `dining table for eight` -> 8: the count of chairs a
    table's own name states. None where it states none -- and None for a BAND (`outdoor
    dining table for six to eight`), because a band is not a count and reading its low end
    as one would seat six chairs the record did not count."""
    m = _SEATS_RE.search((name or "").lower())
    if not m or m.group(2):
        return None
    w = m.group(1)
    return int(w) if w.isdigit() else _NUM_WORDS[w]


def _front_strip(entry, clear_ft):
    """fg-clear-in-front: the clear floor an item's record asks for beyond its own footprint
    (`clearance_in`), as a rectangle off the face AWAY from the wall it was seated on -- a
    drawer extends, a chair is pulled back, a person stands there. Nothing is drawn for it;
    it is floor the next item may not take. None for an item with no wall or no clearance."""
    if clear_ft <= 0 or entry.get("x_ft") is None:
        return None
    x, y, w, d = entry["x_ft"], entry["y_ft"], entry["width_ft"], entry["depth_ft"]
    wall = entry.get("wall")
    if wall == "S":   return (x, y + d, w, clear_ft)
    if wall == "N":   return (x, y - clear_ft, w, clear_ft)
    if wall == "W":   return (x + w, y, clear_ft, d)
    if wall == "E":   return (x - clear_ft, y, clear_ft, d)
    return None


def _entry(spec, r, wall=None, **extra):
    """A placed record entry. `piece`/`of` travel from the spec; `wall` is the wall the item
    is seated AGAINST and nothing else; `back` (in `extra`) is the compass side an item that
    is on no wall turns its back to, which is what `marks_for` orients by."""
    out = {"item": spec["item"], "x_ft": round(r[0], 3), "y_ft": round(r[1], 3),
           "width_ft": round(r[2], 3), "depth_ft": round(r[3], 3)}
    if wall:
        out["wall"] = wall
    for k in ("symbol", "rule", "grade", "piece", "of"):
        if spec.get(k) is not None:
            out[k] = spec[k]
    out.update({k: v for k, v in extra.items() if v is not None})
    return out


def _refused(spec, reason, **extra):
    out = {"item": spec["item"], "width_ft": round(spec["w_in"] / 12.0, 2),
           "depth_ft": round(spec["d_in"] / 12.0, 2), "unplaced": {"reason": reason}}
    for k in ("symbol", "rule", "grade", "piece", "of"):
        if spec.get(k) is not None:
            out[k] = spec[k]
    out.update({k: v for k, v in extra.items() if v is not None})
    return out


def _wall_free(occupied, room_id, wall, lo, hi):
    """Is the wall run [lo, hi] clear of every opening the placement seated on it?"""
    return all(b <= lo + 1e-6 or a >= hi - 1e-6 for a, b in occupied.get((room_id, wall), []))


def _clear(r, placed):
    return all(not _overlaps(r, q) for q in placed)


def _rect_of(e):
    return (e["x_ft"], e["y_ft"], e["width_ft"], e["depth_ft"])


def _bed(layout):
    """The room's bed as seated against its wall -- the first wall-seated entry drawing the
    BED symbol. `symbol_for` is the one reader of what an item's name draws (a nightstand and
    a bedside table are not beds; a bedstead, a day bed and a crib are), and a courtyard's
    "planting bed" is the one name that symbol table draws as a bed and is not one."""
    for e in layout:
        if e.get("x_ft") is None or e.get("wall") is None:
            continue
        n = (e.get("item") or "").lower()
        if (e.get("symbol") or symbol_for(n)) == "bed" and "planting" not in n:
            return e
    return None


def _opposite(wall):
    return {"S": "N", "N": "S", "W": "E", "E": "W"}.get(wall)


def _short_walls(rect):
    """The two END walls: the pair whose run is the room's shorter dimension."""
    _x, _y, w, d = rect
    return ("W", "E") if w > d else ("S", "N")


def _place_relative_to_bed(spec, rule, bed, rect, placed, occupied, room_id):
    """fg-at-the-foot and fg-beside-the-bed: a rectangle stated by the bed's own. Returns
    `(rect, back)` or None. At the foot: centred on the bed against its foot edge, the item's
    along-the-wall side along the bed's width, its back to the bed. Beside: on the bed's own
    wall, touching its side -- the side the piece index asks for first, the other second, so
    a pair takes both and a single takes the first that is free."""
    x, y, w, d = rect
    bx, by, bw, bd = _rect_of(bed)
    wall = bed["wall"]
    fw, fd = spec["w_in"] / 12.0, spec["d_in"] / 12.0
    cands = []
    if rule == "fg-at-the-foot":
        if wall == "S":   cands.append((bx + (bw - fw) / 2, by + bd, fw, fd))
        elif wall == "N": cands.append((bx + (bw - fw) / 2, by - fd, fw, fd))
        elif wall == "W": cands.append((bx + bw, by + (bd - fw) / 2, fd, fw))
        else:             cands.append((bx - fd, by + (bd - fw) / 2, fd, fw))
    else:
        side_first = (spec.get("piece") or 1) % 2 == 1
        for side in ((1, -1) if side_first else (-1, 1)):
            if wall in ("S", "N"):
                sx = bx + bw if side > 0 else bx - fw
                sy = by if wall == "S" else by + bd - fd
                cands.append((sx, sy, fw, fd))
            else:
                sy = by + bd if side > 0 else by - fw
                sx = bx if wall == "W" else bx + bw - fd
                cands.append((sx, sy, fd, fw))
    for c in cands:
        c = to_record(c)
        if not _inside(c, rect) or not _clear(c, placed):
            continue
        if rule == "fg-beside-the-bed":
            lo, hi = (c[0], c[0] + c[2]) if wall in ("S", "N") else (c[1], c[1] + c[3])
            if not _wall_free(occupied, room_id, wall, lo, hi):
                continue
        return c, wall
    return None


def _piers(room):
    """{wall: [(lo, hi), ...]} -- every placed sash's run on each wall, from the record."""
    by_wall = {}
    for win in (room.get("windows") or []):
        if win.get("unplaced") or not win.get("wall"):
            continue
        pos = win.get("positions_ft") or ([win["position_ft"]] if win.get("position_ft") is not None else [])
        half = float(win.get("width_ft") or 3.0) / 2.0
        by_wall.setdefault(win["wall"], []).extend((p - half, p + half) for p in pos)
    return by_wall


def _place_on_pier(spec, room, rect, placed, occupied):
    """fg-between-the-windows: centred on a pier -- the wall between two placed sashes -- on
    the first wall, in the packer's order, that has one long enough and clear. Returns
    `(rect, wall)` or `(None, None)`."""
    x, y, w, d = rect
    fw, fd = spec["w_in"] / 12.0, spec["d_in"] / 12.0
    by_wall = _piers(room)
    for wall in WALL_ORDER:
        edges = sorted(by_wall.get(wall) or [])
        for (_a0, a1), (b0, _b1) in zip(edges, edges[1:]):
            if (b0 - a1) + 1e-6 < fw:
                continue
            mid = (a1 + b0) / 2.0
            if wall in ("S", "N"):
                c = (mid - fw / 2, y if wall == "S" else y + d - fd, fw, fd)
                lo, hi = c[0], c[0] + fw
            else:
                c = (x if wall == "W" else x + w - fd, mid - fw / 2, fd, fw)
                lo, hi = c[1], c[1] + fw
            c = to_record(c)
            if _inside(c, rect) and _clear(c, placed) and _wall_free(occupied, room["id"], wall, lo, hi):
                return c, wall
    return None, None


def _place_flanking(spec, breast, rect, placed, occupied, room_id):
    """fg-flanking-the-chimney-breast: on the breast's own wall, touching its side -- the side
    the piece index asks for first, the other second, so a pair flanks and a single takes the
    first free side. Returns the rectangle or None."""
    x, y, w, d = rect
    fw, fd = spec["w_in"] / 12.0, spec["d_in"] / 12.0
    wall = breast["wall"]
    bx, by, bw, bd = _rect_of(breast)
    sides = (1, -1) if (spec.get("piece") or 1) % 2 == 1 else (-1, 1)
    for side in sides:
        if wall in ("S", "N"):
            sx = bx + bw if side > 0 else bx - fw
            c = (sx, y if wall == "S" else y + d - fd, fw, fd)
            lo, hi = sx, sx + fw
        else:
            sy = by + bd if side > 0 else by - fw
            c = (x if wall == "W" else x + w - fd, sy, fd, fw)
            lo, hi = sy, sy + fw
        c = to_record(c)
        if _inside(c, rect) and _clear(c, placed) and _wall_free(occupied, room_id, wall, lo, hi):
            return c
    return None


def _place_pair_facing(specs, rect, breast, placed, gap_max, standoff):
    """fg-pair-facing: two sofas face each other across a gap of at most `gap_max` (the
    record's own 10 ft), astride the hearth's axis and running out from the breast's face by
    `standoff` where the room draws a breast, else astride the room's long axis at its
    centre. Returns `[(rect, back), (rect, back)]` or None. The gap is the room's own where
    the record's ceiling does not fit; a room too shallow for two sofas and a foot between
    them refuses."""
    x, y, w, d = rect
    fw, fd = specs[0]["w_in"] / 12.0, specs[0]["d_in"] / 12.0
    if breast and breast["wall"] in ("W", "E"):
        axis = breast["y_ft"] + breast["depth_ft"] / 2.0
        gap = min(gap_max, d - 2 * fd - 1.0)
        x0 = (breast["x_ft"] + breast["width_ft"] + standoff) if breast["wall"] == "W" \
            else (breast["x_ft"] - standoff - fw)
        pair = [((x0, axis + gap / 2, fw, fd), "N"), ((x0, axis - gap / 2 - fd, fw, fd), "S")]
    elif breast and breast["wall"] in ("S", "N"):
        axis = breast["x_ft"] + breast["width_ft"] / 2.0
        gap = min(gap_max, w - 2 * fd - 1.0)
        y0 = (breast["y_ft"] + breast["depth_ft"] + standoff) if breast["wall"] == "S" \
            else (breast["y_ft"] - standoff - fw)
        pair = [((axis + gap / 2, y0, fd, fw), "E"), ((axis - gap / 2 - fd, y0, fd, fw), "W")]
    elif w >= d:
        axis = y + d / 2
        gap = min(gap_max, d - 2 * fd - 1.0)
        pair = [((x + (w - fw) / 2, axis + gap / 2, fw, fd), "N"),
                ((x + (w - fw) / 2, axis - gap / 2 - fd, fw, fd), "S")]
    else:
        axis = x + w / 2
        gap = min(gap_max, w - 2 * fd - 1.0)
        pair = [((axis + gap / 2, y + (d - fw) / 2, fd, fw), "E"),
                ((axis - gap / 2 - fd, y + (d - fw) / 2, fd, fw), "W")]
    if gap <= 0:
        return None
    out = [(to_record(r), back) for r, back in pair]
    a, b = out[0][0], out[1][0]
    if _inside(a, rect) and _inside(b, rect) and _clear(a, placed) and _clear(b, placed) \
            and not _overlaps(a, b):
        return out
    return None


def _chairs_around(spec, table, n, rect, placed):
    """fg-chairs-around-the-table: N chairs pulled up to the table's edges, each touching it
    and each turning its back to the room -- one at each end, the rest split along the long
    sides. Returns `(placed [(rect, back)], refused)`; a chair whose place fouls a door swing
    or something already seated is counted, never moved somewhere plausible."""
    x, y, w, d = rect
    cw, cd = spec["w_in"] / 12.0, spec["d_in"] / 12.0
    tx, ty, tw, td = _rect_of(table)
    along_x = tw >= td
    ends = min(2, n)
    per_side = n - ends
    left = (per_side + 1) // 2
    right = per_side - left
    cands = []
    if along_x:
        if ends >= 1: cands.append(((tx - cd, ty + (td - cw) / 2, cd, cw), "W"))
        if ends >= 2: cands.append(((tx + tw, ty + (td - cw) / 2, cd, cw), "E"))
        for k, side in ((left, -1), (right, 1)):
            for i in range(k):
                cx = tx + (i + 0.5) * tw / k - cw / 2
                cands.append(((cx, ty - cd, cw, cd), "S") if side < 0 else ((cx, ty + td, cw, cd), "N"))
    else:
        if ends >= 1: cands.append(((tx + (tw - cw) / 2, ty - cd, cw, cd), "S"))
        if ends >= 2: cands.append(((tx + (tw - cw) / 2, ty + td, cw, cd), "N"))
        for k, side in ((left, -1), (right, 1)):
            for i in range(k):
                cy = ty + (i + 0.5) * td / k - cw / 2
                cands.append(((tx - cd, cy, cd, cw), "W") if side < 0 else ((tx + tw, cy, cd, cw), "E"))
    out, refused = [], 0
    for c, back in cands:
        c = to_record(c)
        if _inside(c, rect) and _clear(c, placed):
            out.append((c, back))
            placed.append(c)
        else:
            refused += 1
    return out, refused


def arrange_room(room, catalogue_room, rect, occupied, blocked=None, breasts=None):
    """Seat one dry room's furniture. Returns `(layout, skipped)`.

    `catalogue_room` is the room TYPE's record -- this is where the furniture lives, so the
    pass reads the catalogue and writes the result onto the plan record, exactly as the
    opening grammar does. The renderers then read the record and never the catalogue, which is
    settled decision 11: nothing is drawn that is not in the record.

    `blocked` seeds the collision set with what other passes already drew -- the wet fixtures,
    and the stair well. `occupied` is the wall-span map and is read, never written. `breasts`
    is this room's chimney breasts as `threshold.hearth_pass` judged them (WP-13.6): the
    caller hands them in, because this file is a leaf and reads no sibling, and only a breast
    the pass DREW is a thing to flank or to face.

    THE ORDER IS THE GRAMMAR'S (WP-13.6). Wall items pack first, in catalogue order, and a
    counted item packs as that many pieces; then the POSITIONED items, each stated by another
    thing already on the floor -- at the foot of the bed, beside it, on the pier between two
    sashes, flanking the breast, on the wall opposite the bed, on an end wall, astride the
    hearth's axis; then the freestanding items, centred and stepped; then the chairs a table's
    own name seats. A positioned item whose stated relation has nothing to stand on (no bed
    seated, no pier, no drawn breast) is REFUSED naming the missing fact, never packed against
    some other wall as though the sentence had not been read. Every item seated on a wall
    reserves the clear floor its record asks for in front of it (`clearance_in`), which no
    later WALL-seated or positioned item may take -- a chest whose drawers cannot open is not
    a chest on a plan -- while a bed's clearance is its bedside AISLE (fg-bed-aisle) and the
    things the record puts inside it are let in. A freestanding item is not refused by a
    strip: its own records put it there (the coffee table inside the sofa's clearance)."""
    skipped = {}
    walls_first, positioned, freestanding, chairs = [], [], [], []
    for it in (catalogue_room.get("furniture") or []):
        why = drawable(it)
        if why:
            skipped[why] = skipped.get(why, 0) + 1
            continue
        fp = it["footprint_in"]
        base = {"item": it["item"], "w_in": fp[0], "d_in": fp[1],
                "clear_in": it.get("clearance_in") or 0,
                "symbol": symbol_for(it["item"]), "rule": None, "grade": None}
        run = it.get("needs_uninterrupted_wall_ft")
        place = it.get("placement") or "freestanding"
        rule = rule_for(it)
        n = piece_count(it)
        # fg-bed-aisle: a bed's clearance is an aisle EACH SIDE ("30 in each side, not 24"),
        # not floor in front of it; the packer keeps it along the wall
        if base["symbol"] == "bed" and place != "freestanding" and base["clear_in"] > 0 \
                and "planting" not in it["item"].lower():
            base["aisle_ft"] = base["clear_in"] / 12.0
        for k in range(n):
            spec = dict(base)
            if n > 1:
                spec["piece"], spec["of"] = k + 1, n
            if rule == "fg-chairs-around-the-table":
                spec["rule"], spec["grade"] = rule, "editorial-from-prose"
                chairs.append(spec)
            elif rule in POSITIONED:
                spec["rule"] = rule
                spec["grade"] = "reading" if rule == "fg-pair-facing" else "editorial-from-prose"
                positioned.append(spec)
            elif place == "freestanding":
                spec["rule"], spec["grade"] = "fg-freestanding", "editorial"
                freestanding.append(spec)
            else:
                spec["rule"] = {"against-wall": "fg-against-wall", "built-in": "fg-built-in",
                                "corner": "fg-corner"}.get(place, "fg-against-wall")
                spec["grade"] = "editorial"
                if place == "corner":
                    spec["corner"] = True
                if run:
                    # fg-wall-run is a READING: the figure is in the item's own sentence
                    spec["rule"], spec["grade"] = "fg-wall-run", "reading"
                    spec["min_run_ft"] = float(run)
                walls_first.append({"spec": spec})
    blocked = list(blocked or []) + door_swings(room, rect)
    layout, placed = pack_against_walls(rect, room["id"], occupied, walls_first,
                                        noun="furniture", placed=blocked)
    # fg-clear-in-front: the clear floor each seated wall item asks for. The packer returns
    # exactly one entry per input, in order, so the strip pairs with its own spec by position.
    strips = []                        # [(entry, strip)]
    for e, w_ in zip(layout, walls_first):
        if w_["spec"].get("aisle_ft"):
            strips.extend((e, a_) for a_ in aisle_rects(e, w_["spec"]["aisle_ft"]))
            continue
        st = _front_strip(e, (w_["spec"].get("clear_in") or 0) / 12.0)
        if st:
            strips.append((e, st))

    def _strips(but=None):
        return [s for e, s in strips if e is not but]

    def _seat_on_walls(spec, walls, rule, why):
        """A positioned rule that names WHICH walls and leaves the seat to the packer."""
        sub, _ = pack_against_walls(rect, room["id"], occupied, [{"spec": spec}],
                                    noun="furniture", placed=placed + _strips(), walls=walls)
        e = sub[0]
        if e.get("unplaced"):
            e["unplaced"]["reason"] = f"{rule}: {why} -- " + e["unplaced"]["reason"]
        else:
            placed.append(_rect_of(e))
            st = _front_strip(e, (spec.get("clear_in") or 0) / 12.0)
            if st:
                strips.append((e, st))
        layout.append(e)

    breast = next((b for b in (breasts or []) if b.get("drawn") and b.get("x_ft") is not None), None)
    # ---- the positioned items, in catalogue order; the facing pair is placed as a pair
    pair = [s for s in positioned if s["rule"] == "fg-pair-facing"]
    for spec in positioned:
        rule = spec["rule"]
        if rule == "fg-pair-facing":
            continue
        fw_, fd_ = spec["w_in"] / 12.0, spec["d_in"] / 12.0
        if rule in ("fg-at-the-foot", "fg-beside-the-bed", "fg-opposite-the-bed"):
            bed = _bed(layout)
            if bed is None:
                layout.append(_refused(spec, f"{rule}: this room has no bed seated against a wall "
                                             f"to stand by, so the sentence that seats this item "
                                             f"has nothing to read against"))
                continue
            if rule == "fg-opposite-the-bed":
                opp = _opposite(bed["wall"])
                _seat_on_walls(spec, (opp,), rule, f"the wall opposite the bed ({opp}) has no clear run for it")
                continue
            # the bed's own aisles do not refuse the things the record puts inside them: the
            # nightstand "within the bedside aisle", the bench at the foot
            got = _place_relative_to_bed(spec, rule, bed, rect, placed + _strips(but=bed),
                                         occupied, room["id"])
            if got is None:
                where = "at the foot of" if rule == "fg-at-the-foot" else "beside"
                layout.append(_refused(spec, f"{rule}: no clear floor {where} the bed on its "
                                             f"{bed['wall']} wall for a {fw_:.1f} x {fd_:.1f} ft item"))
                continue
            c, wall = got
            if rule == "fg-beside-the-bed":
                e = _entry(spec, c, wall=wall, by=bed["item"])
                st = _front_strip(e, (spec.get("clear_in") or 0) / 12.0)
                if st:
                    strips.append((e, st))
            else:
                e = _entry(spec, c, by=bed["item"], back=wall)
            layout.append(e)
            placed.append(c)
        elif rule == "fg-between-the-windows":
            c, wall = _place_on_pier(spec, room, rect, placed + _strips(), occupied)
            if c is None:
                layout.append(_refused(spec, f"{rule}: no wall of this room has a pier between two "
                                             f"placed sashes {fw_:.1f} ft long and clear"))
                continue
            e = _entry(spec, c, wall=wall)
            st = _front_strip(e, (spec.get("clear_in") or 0) / 12.0)
            if st:
                strips.append((e, st))
            layout.append(e)
            placed.append(c)
        elif rule == "fg-flanking-the-chimney-breast":
            if breast is None:
                layout.append(_refused(spec, f"{rule}: this room draws no chimney breast to flank "
                                             f"(the plan states no hearth here, or its breast was refused)"))
                continue
            c = _place_flanking(spec, breast, rect, placed + _strips(), occupied, room["id"])
            if c is None:
                layout.append(_refused(spec, f"{rule}: neither side of the breast on the "
                                             f"{breast['wall']} wall is clear for a {fw_:.1f} ft item"))
                continue
            e = _entry(spec, c, wall=breast["wall"], by="the chimney breast")
            layout.append(e)
            placed.append(c)
        elif rule in ("fg-on-the-end-wall", "fg-facing-down-the-hall"):
            ends = _short_walls(rect)
            _seat_on_walls(spec, ends, rule, f"neither end wall ({'/'.join(ends)}) has a clear run for it")
    if pair:
        gap_max = rule_figure("fg-pair-facing", "max_gap_ft")
        standoff = rule_figure("fg-pair-facing", "hearth_standoff_ft")
        two = None
        if gap_max is None or standoff is None:
            why = "fg-pair-facing: the grammar states no max_gap_ft / hearth_standoff_ft, so the pair cannot be placed"
        else:
            # both axes are OURS (the sentence states the facing and the gap), so they are
            # tried in order: the hearth's where the room draws a breast, then the centre line
            two = _place_pair_facing(pair, rect, breast, placed + _strips(), gap_max, standoff)
            by = "the hearth's axis"
            if two is None and breast:
                two = _place_pair_facing(pair, rect, None, placed + _strips(), gap_max, standoff)
                by = "the room's centre line (the hearth's axis was blocked)"
            elif not breast:
                by = "the room's centre line"
            why = ("fg-pair-facing: no clear floor for two sofas facing each other "
                   + ("astride the hearth's axis or " if breast else "")
                   + f"across the room's centre line within {gap_max:g} ft of each other")
        if two is None:
            for spec in pair:
                layout.append(_refused(spec, why))
        else:
            for spec, (c, back) in zip(pair, two):
                layout.append(_entry(spec, c, by=by, back=back))
                placed.append(c)
    # ---- the freestanding items
    # A strip does NOT refuse a freestanding item: the record puts the coffee table "16 to 18 in
    # from the sofa" -- inside the sofa's own 30 -- and the table's chairs inside the table's 54,
    # so a strip that refused them would contradict the sentences the clearance was read from.
    # Measured before it was believed: as an exclusion against everything, the strips refused
    # 41 items the previous packer had seated, the coffee table among them.
    # oq/a-clearance-is-sometimes-a-companions-place-and-sometimes-a-prohibition.
    for i, spec in enumerate(freestanding):
        r0 = place_freestanding(rect, spec, placed, i)
        if r0 is None:
            layout.append(_refused(spec, "the room has no clear floor at its centre for a "
                                         f"{spec['w_in'] / 12.0:.1f} x {spec['d_in'] / 12.0:.1f} ft item "
                                         "that does not foul a door swing, a fixture "
                                         "or something already placed"))
            continue
        layout.append(_entry(spec, r0))
        placed.append(r0)
    # ---- the chairs a table seats
    if chairs:
        table = next((e for e in layout if e.get("x_ft") is not None and seats_of(e.get("item"))), None)
        n = seats_of(table["item"]) if table else None
        spec = chairs[0]
        if table is None or not n:
            # THE COUNT IS UNJUDGED HERE AND THE REASON SAYS SO. The number of chairs is the
            # TABLE's -- read from its own name by `seats_of` -- so a room with no such table
            # placed has no count either, and one refused row naming no number is the honest
            # shape. Writing the catalogue's own `count` here instead would publish a figure
            # this rule does not read: the shipped corpus reaches this branch twice and both
            # times the catalogue states ONE uncounted `dining chair`, which is not the number
            # of chairs anybody was refused.
            layout.append(_refused(spec, "fg-chairs-around-the-table: no table stating its seats is "
                                         "placed in this room, so there is nothing for the chairs to "
                                         "be pulled up to and no count for them either -- the number "
                                         "is the table's own name's and this room has no such table "
                                         "placed"))
        else:
            got, refused = _chairs_around(spec, table, n, rect, placed)
            for k, (c, back) in enumerate(got):
                layout.append(_entry(dict(spec, piece=k + 1, of=n), c, by=table["item"], back=back))
                placed.append(c)
            if refused:
                layout.append(_refused(dict(spec, piece=len(got) + 1, of=n),
                                       f"fg-chairs-around-the-table: {refused} of the {n} chairs the "
                                       f"table seats have no clear floor at its edge",
                                       by=table["item"]))
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
    That is the whole of the transform: a reflection or a quarter turn chosen by `wall` -- or
    by `back`, the compass side an item on NO wall turns its back to (a chair pulled up to a
    table, a sofa of a facing pair, a bench at the foot of a bed; WP-13.6) -- and a scale. It lives here, once, and both renderers call it -- `derive.js` ports it and
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
    wall = entry.get("back") or entry.get("wall")

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
