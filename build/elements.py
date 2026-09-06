#!/usr/bin/env python3
"""Which massing element a room stands in, and what each element's own envelope is — ONE
spelling.

**A LEAF, on `build/storeys.py`'s, `build/assemblies.py`'s, `build/furniture.py`'s and
`build/stacking.py`'s precedent, and it must stay one.** `geometry.py` loads `plan_check.py`
at import time and `structure.py` loads `geometry.py`, so the six layers that have to agree
about this sit on three different rungs of that ladder. Every helper here imports no sibling.

WHY THIS FILE EXISTS
--------------------
OQ 40 was ruled on 3 Sep 2026: a dependency is a second massing ELEMENT, not a second plan
level. `geometry.blocks_for` places it, `blocks_record` writes it and both renderers draw it.
An adversarial audit then measured SIX layers below the placer still reading
`footprint.width_ft`/`depth_ft` as the whole building, each wrong in its own direction on a
dependency room — a window drawn fourteen feet from its room, a clear span manufactured across
the hyphen gap, an upper wall "supported" by a wall under no upper floor, a house reporting
`lot_capped: true` at 34 ft wider than its lot, a critic convicting a dependency room of
reaching no exterior wall, and IfcSpaces floating clear of their slab. That is
`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`, and WP-11.9 is its
answer.

THE FOUR RULINGS THIS FILE IMPLEMENTS (Lucas, 5 September 2026)
---------------------------------------------------------------
1. **Per-element envelope, union reported beside it.** Each element has its own four walls,
   its own boundary for openings and its own slab. The union bounding box is DERIVED and
   written beside them for the readers that are not per-element — the roof spans something and
   the lot holds something, and neither is an element.
2. **The lot cap is on the BUILT EXTENT, elements only, gap excluded.** `extent_width_ft`
   measures the union of the elements' x-intervals, so open ground between two detached
   elements is not charged against the lot. Where a hyphen fills the gap (ruling 3) the
   elements abut and the measure is simply the total.
3. **A hyphen is an element, and abutment is a constraint.** `role: "hyphen"` stays. Every
   count here says which roles it includes rather than leaving a reader to guess whether a
   two-element house has two elements or three.
4. **`touches` is measured against the room's OWN element's face.** Exterior is exterior: a
   dependency room on its element's east face carries a window, a sill and the weather, and
   `plan_check`'s drawn layer counts it. A face that looks across a gap at another element is
   still exterior; it is counted separately as `faces_across_a_gap` so a later ruling has the
   number without this one having baked an answer in.

HOW A ROOM IS JOINED TO ITS ELEMENT, AND WHY IT IS GEOMETRIC
------------------------------------------------------------
`footprint.blocks` rows carry no room list — `blocks_record` drops the one `blocks_for` builds
— and a room's own `block` tag names the DEPENDENCY, not the hyphen element beside it
(`<bid>-hyphen`), so the tag alone cannot place a hyphen room. The join is CONTAINMENT of the
room's placed rectangle in the element's, which the slicer makes exact: `slice_rect` tiles each
element with its own rooms and nothing else.

**A room that lands in no element is UNJUDGED, never assigned to the main block.** Defaulting
to element zero is precisely the defect this file was written to remove: it is what every one
of the six layers already does, and it is right for the whole shipped corpus and wrong for the
one record that motivated the work.
"""

TOL = 0.5   # ft. Rooms tile their element exactly; this absorbs the record's 2 dp rounding.

# The roles `blocks_for` writes today. Named rather than matched loosely, so a role added
# later has to be considered here rather than silently counted as a dependency.
ROLES = ("main", "dependency", "hyphen")


def elements(plan):
    """Every massing element, main first. A ONE-rectangle house returns one element.

    The single-element answer is synthesised from the footprint scalars rather than left
    empty: every caller then has one code path, and `blocks_record` deliberately writes no
    `blocks` key on a one-rectangle house (every plan in this corpus is one), so a reader that
    demanded the key would be reading nothing on all sixteen.
    """
    fp = (plan or {}).get("footprint") or {}
    rows = fp.get("blocks") or []
    out = []
    for b in rows:
        out.append({"id": b.get("id"), "role": b.get("role") or "dependency",
                    "x": float(b.get("x_ft") or 0.0), "y": float(b.get("y_ft") or 0.0),
                    "W": float(b.get("width_ft") or 0.0), "H": float(b.get("depth_ft") or 0.0),
                    "attached_to": b.get("attached_to")})
    if out:
        return out
    W, H = fp.get("width_ft"), fp.get("depth_ft")
    if not W or not H:
        return []
    return [{"id": "main", "role": "main", "x": 0.0, "y": 0.0,
             "W": float(W), "H": float(H), "attached_to": None}]


def is_multi(plan):
    """More than one massing element — the condition every disclosure in this layer hangs on."""
    return len(elements(plan)) > 1


def _contains(el, g):
    return (g["x_ft"] >= el["x"] - TOL and g["y_ft"] >= el["y"] - TOL
            and g["x_ft"] + g["width_ft"] <= el["x"] + el["W"] + TOL
            and g["y_ft"] + g["depth_ft"] <= el["y"] + el["H"] + TOL)


def element_of(plan, room, els=None):
    """The element this placed room stands in, or None.

    None means COULD NOT EVALUATE and every caller must treat it as that. It happens when the
    room is unplaced, when the plan carries no footprint, and — the case worth naming — when a
    room's rectangle straddles two elements, which the slicer cannot produce and a
    caller-supplied record can.
    """
    g = (room or {}).get("geometry")
    if not g:
        return None
    for el in (els if els is not None else elements(plan)):
        if _contains(el, g):
            return el
    return None


def bounds_of(el):
    """`(x, y, W, H)` — the tuple the six layers want, from an element dict."""
    return (el["x"], el["y"], el["W"], el["H"])


def bounds_index(plan, level_rooms):
    """`{room_id: (x, y, W, H)}` for one level's rooms, over their OWN elements.

    Built once per level and threaded down, because `openings.place` asks it per room per
    opening and re-walking the element list each time is the kind of quadratic nobody notices
    until a record has forty rooms.

    A room with no element is ABSENT from the map rather than present with the main block's
    bounds. Callers use `.get(rid)` and decide what to do with a miss; that is the whole
    difference between this and the code it replaces.
    """
    els = elements(plan)
    out = {}
    for r in level_rooms or []:
        el = element_of(plan, r, els)
        if el is not None:
            out[r["id"]] = bounds_of(el)
    return out


def _union_measure(intervals):
    """Total length of a union of closed intervals — the 'gap excluded' of ruling 2."""
    xs = sorted((a, b) for a, b in intervals if b > a)
    if not xs:
        return 0.0
    total, cur_lo, cur_hi = 0.0, xs[0][0], xs[0][1]
    for lo, hi in xs[1:]:
        if lo > cur_hi:
            total += cur_hi - cur_lo
            cur_lo, cur_hi = lo, hi
        else:
            cur_hi = max(cur_hi, hi)
    total += cur_hi - cur_lo
    return round(total, 4)


def extent_width_ft(plan, els=None):
    """What the lot cap is ON (ruling 2): the width the building actually occupies.

    The measure of the union of the elements' x-intervals. Two elements with a hyphen between
    them abut, so this is their total; two DETACHED elements leave open ground between them,
    and that ground is not the building and is not charged against the lot.

    Measured on the hand-tagged Tidewater record before this existed: a 60 ft main block, a
    7 ft hyphen and a 30 ft dependency built 97 ft of house while `lot_capped` reported on the
    60 alone.
    """
    els = els if els is not None else elements(plan)
    return _union_measure([(e["x"], e["x"] + e["W"]) for e in els])


def extent_depth_ft(plan, els=None):
    """The same measure on the other axis. Elements are laid out side by side today, so this
    is the deepest element rather than a sum; it is computed the same way so that a future
    layout which stacks them north-south needs no second rule."""
    els = els if els is not None else elements(plan)
    return _union_measure([(e["y"], e["y"] + e["H"]) for e in els])


def union_bbox(plan, els=None):
    """`(x0, y0, x1, y1)` over every element — ruling 1's 'union reported beside it'.

    This is what a reader that is NOT per-element wants: the roof spans it and a site drawing
    frames it. It is deliberately NOT what the lot cap reads, because it includes the gap.
    """
    els = els if els is not None else elements(plan)
    if not els:
        return None
    return (round(min(e["x"] for e in els), 2), round(min(e["y"] for e in els), 2),
            round(max(e["x"] + e["W"] for e in els), 2),
            round(max(e["y"] + e["H"] for e in els), 2))


def boundary_walls(rect, bounds, tol=0.6):
    """Which of a room's own walls lie on its ELEMENT's boundary, with their runs.

    The body is `openings._boundary_walls`, moved here so the opening placer, the drawn layer's
    `touches` tests and anything else that asks "is this wall on the outside" cannot answer
    differently. `bounds` is the room's own element (ruling 1), never the main block.
    """
    x, y, w, h = rect
    bx, by, bw, bh = bounds
    out = {}
    if y <= by + tol:
        out["S"] = (x, x + w)
    if y + h >= by + bh - tol:
        out["N"] = (x, x + w)
    if x <= bx + tol:
        out["W"] = (y, y + h)
    if x + w >= bx + bw - tol:
        out["E"] = (y, y + h)
    return out


def faces_across_a_gap(plan, els=None, tol=1.0):
    """Element faces that look across open ground at another element.

    Ruling 4 counts such a face as exterior — it is, of the weather — and this is the number
    the ruling asked to be kept separately so that a later one can be taken on evidence. A face
    is 'across a gap' when another element lies beyond it on the same axis with clear ground
    between: an abutting hyphen is NOT a gap, which is the whole reason a hyphen is an element.

    Returns a list of `{element, wall, faces}` rows.
    """
    els = els if els is not None else elements(plan)
    out = []
    for a in els:
        for b in els:
            if a is b:
                continue
            # vertical overlap, so the two are side by side rather than one above the other
            if min(a["y"] + a["H"], b["y"] + b["H"]) - max(a["y"], b["y"]) <= 0:
                continue
            def _clear(lo, hi):
                """No third element standing in the interval — otherwise it is not open
                ground, it is a hyphen, and a hyphen is exactly what stops this being a gap."""
                return not any(m is not a and m is not b
                               and m["x"] < hi - tol and m["x"] + m["W"] > lo + tol
                               for m in els)
            gap_e = b["x"] - (a["x"] + a["W"])
            gap_w = a["x"] - (b["x"] + b["W"])
            if gap_e > tol and _clear(a["x"] + a["W"], b["x"]):
                out.append({"element": a["id"], "wall": "E", "faces": b["id"],
                            "gap_ft": round(gap_e, 2)})
            if gap_w > tol and _clear(b["x"] + b["W"], a["x"]):
                out.append({"element": a["id"], "wall": "W", "faces": b["id"],
                            "gap_ft": round(gap_w, 2)})
    return out


def _shares_wall(a, b, tol=0.4):
    """Two placed rectangles share a run of wall — the same test `openings._shared` makes.

    Spelled here rather than imported because this file is a LEAF and `openings.py` is not; the
    two are held together by `tests/test_elements.py`, which runs both over the same pairs.
    """
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    if abs((ax + aw) - bx) <= tol or abs((bx + bw) - ax) <= tol:
        return min(ay + ah, by + bh) - max(ay, by) > tol
    if abs((ay + ah) - by) <= tol or abs((by + bh) - ay) <= tol:
        return min(ax + aw, bx + bw) - max(ax, bx) > tol
    return False


def unabutted_hyphen_rooms(plan, level_rooms, els=None):
    """Hyphen rooms that connect nothing — ruling 3's constraint, as a number.

    A hyphen exists to join two elements. `blocks_for` centres every element on the main
    block's depth axis and then slices each with an INDEPENDENT `slice_rect` call, so nothing
    made the room on the house side of the boundary share any wall with the hyphen room, or the
    hyphen room with the dependency's anchor. Measured on the one parti whose door graph was
    correct: the hyphen at y 9.36-29.36 against a stair at y 30.0-38.71, missing by 0.64 ft,
    both its doors `unplaced` and the hyphen itself fatal-unreachable. **The one room whose
    entire reason for existing is to connect two elements connected neither.**

    Returns a list of `{room, element, unconnected}` where `unconnected` names the neighbouring
    element ids the room reaches no room in. **Zero on every plan in this corpus**, because
    every one of them is a single rectangle -- which is what lets the search rank on it without
    moving a single shipped placement.
    """
    els = els if els is not None else elements(plan)
    if len(els) < 2:
        return []
    rects, owner = {}, {}
    for r in level_rooms or []:
        g = r.get("geometry")
        if not g:
            continue
        rects[r["id"]] = (g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"])
        el = element_of(plan, r, els)
        if el is not None:
            owner[r["id"]] = el["id"]
    return unabutted_hyphens(els, rects, owner)


def unabutted_hyphens(els, rects, owner):
    """The same rule over RAW rectangles — the entry point the search uses.

    `geometry.solve_heuristic` has element dicts and `{room: (x, y, w, h)}` in hand inside its
    candidate loop and no plan record at all; building one per candidate to ask this question
    would be absurd, and re-spelling the rule beside it is what this repository keeps paying
    for. One body, two doors.
    """
    if len(els) < 2:
        return []
    out = []
    for hy in [e for e in els if e["role"] == "hyphen"]:
        # the elements a hyphen must join: what it is attached to, and whatever lies on its
        # other side. Read off the geometry rather than off a field, because `attached_to`
        # names the main block for both halves of a pair.
        nbrs = [e["id"] for e in els
                if e is not hy
                and (abs(e["x"] + e["W"] - hy["x"]) <= 0.05
                     or abs(hy["x"] + hy["W"] - e["x"]) <= 0.05)]
        for rid, oid in owner.items():
            if oid != hy["id"]:
                continue
            missed = []
            for nb in nbrs:
                if not any(_shares_wall(rects[rid], rects[o])
                           for o, oo in owner.items() if oo == nb and o in rects):
                    missed.append(nb)
            if missed:
                out.append({"room": rid, "element": hy["id"], "unconnected": missed})
    return out


def abutment_report(plan, level_rooms, els=None, tol=0.05):
    """Whether the elements meet, and whether the ROOMS across each boundary meet (ruling 3).

    Two questions, reported separately, because they fail independently and the second is the
    one that was measured wrong. Elements abut when their rectangles touch -- `blocks_for` has
    always produced that, laying each element against the last edge. Rooms abut when a room on
    one side of the boundary shares a run of wall with a room on the other, and that is what
    nothing made true.
    """
    els = els if els is not None else elements(plan)
    by_id = {e["id"]: e for e in els}
    attached = abutting = 0
    gaps = []
    for e in els:
        tgt = by_id.get(e.get("attached_to") or "")
        if tgt is None:
            continue
        attached += 1
        d = max(e["x"] - (tgt["x"] + tgt["W"]), tgt["x"] - (e["x"] + e["W"]))
        # A HYPHEN BETWEEN THEM IS NOT A GAP, and this branch is why `attached_to` was not
        # simply re-pointed at the hyphen instead. `blocks_for` names the main block as the
        # anchor of BOTH halves of a pair, which is true of the massing (the dependency depends
        # on the house, not on the corridor) and false of the geometry (they do not touch). An
        # element lying wholly in the interval between the two closes it.
        if d > tol:
            lo = min(e["x"] + e["W"], tgt["x"] + tgt["W"])
            hi = max(e["x"], tgt["x"])
            if any(m is not e and m is not tgt
                   and m["x"] >= lo - tol and m["x"] + m["W"] <= hi + tol for m in els):
                d = 0.0
        if d <= tol:
            abutting += 1
        else:
            gaps.append({"element": e["id"], "attached_to": tgt["id"], "gap_ft": round(d, 2)})
    un = unabutted_hyphen_rooms(plan, level_rooms, els)
    return {"attached": attached, "abutting": abutting, "gaps": gaps,
            "hyphen_rooms_connecting_nothing": un}
