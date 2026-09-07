#!/usr/bin/env python3
"""The real solver (WP-2.3): room placement as CP-SAT over the bay grid.

Where build/geometry.py's search hill-climbs 250 random slicings toward
strongly-weighted preferences, this engine states the record's own declared
facts as HARD constraints and proves them satisfiable or names the conflict
(the 25 Aug rulings):

  HARD — no-overlap, containment, near-total coverage of the footprint;
  declared doors imply touching rooms; a threshold room with an exterior door
  is the entry and must reach the entrance front; each room at roughly its
  program size; each room's declared exterior walls.

  Wall pins carry two stated refinements, both from the same cause —
  `exterior_walls` speaks EXPOSURE in the fully-massed house (porches, ells,
  wings), which a flat rectangular footprint cannot always hold:
    * a PROTRUDING room (3+ walls, or a non-circulation opposite pair) and a
      room in a CONTESTED CORNER (two rooms of one level declaring the same
      corner pair — 10 of 12 partis do this) harden to "reach at least one
      declared wall", the rest scored at the heuristic's own 14 points;
    * any other wall pin stays fully hard UNLESS the solver PROVES a set of
      pins cannot co-hold with the remaining facts — exactly those proven
      pins are downgraded the same way, and every downgrade is stated in the
      result. Doors, program sizes, the entrance and capacity NEVER
      downgrade: they are what infeasibility is for.
  A circulation room declaring an opposite pair is the centre passage and
  spans — its two pins ARE the spanning rule.

  SOFT (weighted, mirrored from WP-2.2's scoring) — bay snapping (relaxations
  stay counted, never forbidden), the entrance hall on the front, principal/
  service zoning, ceremonial depth, wet-over-wet stacking, a centre passage
  near the centre.

Solving is two-phase per footprint: a hard-constraints-only pass finds (or
refutes) a placement fast; the full weighted objective then polishes it with
the phase-A solution as a hint, and if the polish runs out of time the
phase-A placement is returned, scored post-hoc and said so. On INFEASIBLE the
assumption cores drive the downgrade rounds and, when the conflict is real,
a plain-language minimal conflict set. The footprint grows a bay before a
requirement is blamed, per the layer's stated infeasibility ordering.

Determinism: one worker, fixed seed — the same record must yield the same
drawing, because the drawing is a render of the data.

Loaded through geometry.solve()'s dispatcher; not a CLI of its own.
"""
import copy
import math
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _mod(n, p):
    # Delegates to build/modcache.py — one module execution per process (OQ 28).
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(n, p)

GEO = _mod("geometry", f"{ROOT}/build/geometry.py")
C = GEO.C

U = 1                     # 1-ft integer grid (coarse on purpose: domains half the size)
MIN_DOOR_OVERLAP = 4      # the fallback for a door that declares no width of its own


def _door_overlap(d, v1, v2):
    """How much wall two rooms must share to hold THIS door (WP-6.3, closing OQ 41/63).

    The rule was `min(4, max(2, floor(0.9 * min(maxside))))`, and its comment said it
    "scales to the smaller room: a linen press's whole side may be 2 ft — its door is
    narrower than a parlor's, and demanding 4 ft would refuse real closets". **That branch
    has never once fired.** `maxside` is `max(width_ft, length_ft)` — the LONGER side — so
    dropping below 4 needs a room whose long side is under 3.34 ft, and there are **0 such
    rooms in all 16 plan records** (238 rooms measured). Every interior pair in the corpus
    got a flat 4 ft: the 3 x 5 linen press the comment names got a parlour's requirement,
    and so did `bed2cl`, which is literally 2 x 6. OQ 41's own text quotes the same dead
    expression as though it described behaviour.

    So the floor is now the door's own leaf and its jambs, which is what a door occupies and
    what both renderers and both exporters have measured against since WP-6.1 — one number,
    `openings.required_wall_ft`, in one place. 469 of the corpus's 471 doors declare a width
    (the two that do not are exterior and never reach here), so this is the record speaking
    rather than a constant. Ceiled to the model's integer grid.

    Measured per pair across the corpus: 102 tighter, 3 looser, 128 unchanged."""
    w = d.get("width_ft")
    if not w:
        return MIN_DOOR_OVERLAP
    OP = _mod("openings", f"{ROOT}/build/openings.py")
    need = OP.required_wall_ft(float(w))
    # never demand more shared wall than the smaller room can physically offer, or a wide
    # opening between two small rooms becomes an infeasibility rather than a finding
    room_cap = min(v1["maxside"], v2["maxside"])
    return max(2, min(int(math.ceil(need * U)), int(math.floor(room_cap * U))))
SCALE = 10                # objective weights are WP-2.2's, x10 into integers
COVERAGE = 0.97           # hard floor; the absorb pass grows rooms into the rest

# WP-11.7. The downgrade ladder, LOWEST AUTHORITY FIRST. On INFEASIBLE the round loop takes the
# first kind in this list that appears in the conflict core and downgrades exactly those pins,
# so a round always gives up the least authoritative fact it can.
#
#   wall   the record's `exterior_walls`  — released first
#   axis   the parti's own through-axis, read onto this plan
#   shape  the room record's own `dimensions.proportion` band — released last
#
# THE ORDER PUTS THE WALL FIRST, AND THAT IS A RULING RATHER THAN AN INTUITION (5 Sep 2026).
# The obvious ranking is the opposite one -- an `exterior_walls` entry is authored on THIS
# record and a proportion band is the corpus's rule about a room TYPE -- and it was written that
# way first. Then it was measured, and the two cannot both be hard:
#
#     shape band held, all 22 wall pins released  ->  OPTIMAL
#     shape band held, wall pins held             ->  INFEASIBLE, at every footprint to 10 bays
#
# and the ladder, ranked the other way, gave up 14 or 15 of the 15 shape pins at EVERY coverage
# floor from 0.97 down to 0.60 -- so coverage and packing are not the blocker and the band simply
# never survived. Measured on the drawing, releasing the walls instead: serious findings 79 -> 58,
# and NO room drawn outside its own band where the worst had been a 13 x 16 ft bedroom drawn
# 45 x 7. The price is relaxations 11 -> 18 and diverged 14 -> 17.
#
# CLAUDE.md has carried the reason all along: "A plan's `exterior_walls` are aspirations, not
# rectangle edges. Three Tidewater ground rooms each declare OPPOSITE walls, so each would have
# to span the full depth of the house. They are weights, at the 14 points `exterior_score`
# charges. Do not promote them to constraints; the corpus does not mean them that way." This
# engine promoted them anyway, from the day it was written, and the shape band is what made the
# contradiction visible rather than merely stated.
#
# A released wall pin is not discarded: it keeps the heuristic's own 14 points in the objective,
# which is what that note says it was always worth.
#
# A kind NOT in this list never downgrades: sizes, doors, the entrance and capacity are what
# infeasibility is FOR (the 25 Aug rulings). Adding a kind here is a decision about authority
# and belongs in a report, not in a diff.
_RANK = ("wall", "axis", "shape")


def _cls(rtype):
    return C["rooms"].get(rtype, {}).get("function_class")


def _fpd_at(fpd, bays):
    """The footprint fpd would have derived at a forced bay count — the
    grow-a-bay-before-blaming-a-requirement loop."""
    out = dict(fpd)
    W = round(bays * fpd["bay"], 2)
    H = round(fpd["need"] / W, 2)
    out.update({"bays": bays, "W": W, "H": H,
                "slack": (W * H) - fpd["need"],
                "grown": fpd["grown"] + list(range(fpd["bays"] + 1, bays + 1))})
    return out


def _protruding(room):
    walls = set(room.get("exterior_walls") or [])
    if len(walls) >= 3:
        return True
    opposite = ({"S", "N"} <= walls) or ({"W", "E"} <= walls)
    return opposite and _cls(room["type"]) != "circulation"


_CORNER_PAIRS = ({"N", "E"}, {"N", "W"}, {"S", "E"}, {"S", "W"})


def _contested_corners(rs):
    """Per the 25 Aug ruling (contested corners downgrade, stated): two or more
    rooms on one level declaring the same corner pair cannot all have the
    corner of one rectangle. Returns {room_id: note}."""
    out = {}
    for pair in _CORNER_PAIRS:
        claim = [r for r in rs
                 if pair <= set(r.get("exterior_walls") or []) and not _protruding(r)]
        if len(claim) > 1:
            names = ", ".join(sorted(r.get("name") or r["id"] for r in claim))
            for r in claim:
                out[r["id"]] = (f"{'/'.join(sorted(pair))} corner is contested ({names}) — "
                                f"the massing likely has a wing the flat footprint cannot hold")
    return out


class _Reqs:
    """Assumption literals: plain-language sentence, kind, and (for wall pins)
    a structured key so a proven-impossible pin can be downgraded by name."""

    def __init__(self, model):
        self.model = model
        self.lits = []      # (BoolVar, text, kind, key)
        self.notes = []     # stated model refinements (contested corners, downgrades)

    def lit(self, text, kind="other", key=None):
        b = self.model.NewBoolVar(f"req{len(self.lits)}")
        self.lits.append((b, text, kind, key))
        return b


def _w(weight):
    """A heuristic weight as an integer CP penalty, on this model's x10 SCALE.

    WP-7.4 wrote this as `int(w) * SCALE`, which truncates: a weight of 0.5 became 0 and the
    term silently vanished, and a weight of 40.9 became 40. Rounding the SCALED value keeps
    fractional weights meaningful, and a non-zero weight can never round away to nothing --
    a term that disappears because someone tuned it below 1.0 is the kind of silence this
    corpus exists to prevent."""
    v = int(round(float(weight) * SCALE))
    return v if v or not weight else (1 if weight > 0 else -1)


def _span_capacity(plan):
    """The clear span this plan's framing tradition can make, from the corpus rather than a
    constant: timber-bay.json's 20 ft bay module for the styles that list it, else the deepest
    member in construction/floor-structure.json's light_frame_joist_spans. Mirrors
    structure.span_check's own decision so the two engines charge the same fact."""
    try:
        ST = _mod("structure", f"{ROOT}/build/structure.py")
        if (plan.get("style") or "") in ST._timber_bay_applies_to():
            return 20.0
        tbl = ST.load_construction()["floor"]["light_frame_joist_spans"]
        return max(mm["max_clear_span_ft"] for mm in tbl)
    except Exception:
        return None       # catalogue unreadable: unjudged, so nothing is charged


def _element_boxes(els, Wi, Hi):
    """`{(level, room_id): (x, y, W, H)}` in integer units, and the global envelope.

    WP-11.11. The CP model built every room as `x = NewIntVar(0, Wi)` with `x + w <= Wi`: one
    rectangle, one non-negative coordinate space, and it REFUSED a plan with a second massing
    element rather than flatten two into one (which flatters the fatal count -- rooms crammed
    into one rectangle are all trivially reachable). Ruled 7 September 2026, taking
    `oq/the-proving-engine-cannot-place-a-second-massing-element`'s own first reading: **each
    room's coordinates are bounded by its OWN element's box**, in ONE coordinate space. CP-SAT
    integer variables take negative lower bounds, so a west dependency at x = -28 needs no
    shift and no second origin -- the alternative the question offered and this does not use.

    Everything the model says about "the block" is read through this: containment, the coverage
    floor, a declared exterior wall, a spanning room's through-axis, and an exterior door
    reaching the envelope. Each of those is a fact about the element the room stands in.

    The global envelope is returned beside it because the VARIABLE DOMAINS have to cover every
    element while the CONSTRAINTS bound each room to its own. Bounding a domain to its element
    would be tighter and is not done: it would put a room's `x` in a domain that excludes the
    origin, and the hint pass (`_hint_heuristic`, `_hint_values`) feeds values from a heuristic
    layout that may disagree by a foot -- a hint outside a domain is a silent model error, not
    a rejected hint.
    """
    box, xs, ys = {}, [0, Wi], [0, Hi]
    for lvl, elist in (els or {}).items():
        for e in elist or []:
            # INWARD to the grid, never outward. This model is integer at 1 ft (`U`) and a
            # dependency's edges are not: `dependency_sizes` sizes the box from its rooms'
            # own areas and lands on 4.6 or -3.7. Rounding to the NEAREST foot lets CP place a
            # room up to half a foot outside the mass the record states, which is the record
            # and the drawing disagreeing about where the house is -- the defect the refusal
            # this package removes was put there to prevent. Ceiling the low edge and flooring
            # the high one makes the integer box a SUBSET of the stated one, so anything proved
            # inside it is really inside; `_absorb` afterwards works in float space against the
            # element's true edges and grows the room back out to them. The main block is
            # already integral (`_snap_fpd`), so this is the identity on every single-element
            # plan in the corpus.
            ex, ey = math.ceil(e["x"] * U), math.ceil(e["y"] * U)
            eW = max(1, math.floor((e["x"] + e["W"]) * U) - ex)
            eH = max(1, math.floor((e["y"] + e["H"]) * U) - ey)
            xs += [ex, ex + eW]
            ys += [ey, ey + eH]
            for rid in e.get("rooms") or []:
                box[(lvl, rid)] = (ex, ey, eW, eH)
    return box, min(xs), min(ys), max(xs), max(ys)


def _build(plan, prep, fpd, ewalls, downgraded=frozenset(), objective=True,
           unproven=frozenset()):
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    reqs = _Reqs(m)
    Wi, Hi = int(round(fpd["W"] * U)), int(round(fpd["H"] * U))
    # WP-11.11. `els` is {level: [element, ...]} from `geometry.blocks_for` -- the massing
    # elements this level's rooms are laid into. Absent, or one element, and every box below is
    # `(0, 0, Wi, Hi)`, which is what this model read before the argument existed and is every
    # plan in the shipped corpus.
    # Computed here rather than threaded from `solve_cp`: `_build` has seven call sites in
    # this file and `geometry.blocks_for` is the one reader of which element a room stands in,
    # so a parameter would have been seven chances to pass a different answer.
    els = {lvl: GEO.blocks_for(plan, fpd, prep, lvl) for lvl in (0, 1) if prep.get(lvl)}
    ebox, gx0, gy0, gx1, gy1 = _element_boxes(els, Wi, Hi)
    gW, gH = gx1 - gx0, gy1 - gy0
    bayU = max(1, int(round(fpd["bay"] * U)))
    tolU = max(1, int(round(fpd["tol"] * U)))

    rooms = {}      # (level, id) -> dict of vars
    penalties = []  # (bool_or_int_expr, weight_x10)

    for lvl in (0, 1):
        rs = prep.get(lvl) or []
        if not rs:
            continue
        fill = (fpd["W"] * fpd["H"]) / max(1.0, sum(r["_area"] for r in rs))
        xiv, yiv = [], []
        for r in rs:
            dw = (r.get("width_ft") or 10)
            dl = (r.get("length_ft") or 12)
            smin = min(dw, dl)
            # floor scales to the room's own programme — a 1.4 ft linen press is
            # real; clamping it to 3 ft manufactured an infeasibility
            lo_side = max(1, int(math.floor(0.6 * smin * U)))
            # WP-11.11: the ROOM'S OWN element, not the block. `(0, 0, Wi, Hi)` on every
            # single-element plan, which is the whole shipped corpus.
            ex, ey, eW, eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
            x = m.NewIntVar(gx0, gx1, f"x{lvl}_{r['id']}")
            y = m.NewIntVar(gy0, gy1, f"y{lvl}_{r['id']}")
            w = m.NewIntVar(lo_side, max(lo_side, eW), f"w{lvl}_{r['id']}")
            h = m.NewIntVar(lo_side, max(lo_side, eH), f"h{lvl}_{r['id']}")
            a = m.NewIntVar(0, gW * gH, f"a{lvl}_{r['id']}")
            m.AddMultiplicationEquality(a, [w, h])
            # the room at roughly its program size — ONE requirement per room,
            # so a conflict names the room, not an anonymous inequality
            areaU = r["_area"] * U * U
            pr = reqs.lit(f"{r.get('name') or r['id']} needs roughly its program size "
                          f"({dw:g} x {dl:g} ft, within this layer's tolerance)",
                          kind="size")
            m.Add(a >= int(0.88 * areaU)).OnlyEnforceIf(pr)
            m.Add(a <= int(max(1.20, fill * 1.22) * areaU)).OnlyEnforceIf(pr)
            # containment in the room's OWN element (WP-11.11). The lower bounds are
            # constraints and not domains, for the hint reason in `_element_boxes`.
            # THE LOWER BOUND IS A CONSTRAINT WHENEVER THE DOMAIN IS WIDER THAN THE ELEMENT,
            # AND THE FIRST VERSION OF THIS TESTED `if ex:` INSTEAD. That read "on a
            # one-rectangle house ex is 0 and `x >= 0` is already the domain" -- true of the OLD
            # domain and false of the new one, because `gx0` is the leftmost element's edge and
            # a west dependency puts it at -34. So every MAIN-BLOCK room got a domain reaching
            # 34 ft west of the house and no constraint holding it back: measured on a
            # hand-tagged Tidewater, FIVE untagged rooms were placed or absorbed at a negative
            # x, in no element at all. The guard written to protect byte-identity created the
            # defect it was guarding against. `gx0 < ex` is the honest test -- it is False on
            # every single-element plan, so the model for the shipped corpus is unchanged, and
            # True exactly when the domain really is wider than the box.
            if gx0 < ex:
                m.Add(x >= ex)
            if gy0 < ey:
                m.Add(y >= ey)
            m.Add(x + w <= ex + eW)
            m.Add(y + h <= ey + eH)
            # THE SHORT AND LONG SIDES, BUILT UNCONDITIONALLY (WP-11.7). They used to live
            # inside `if objective:` because only the soft aspect term read them -- and phase A
            # runs with `objective=False`, which is the phase that draws this plan
            # (`_finish_feasible` keeps "hard-only phase A" whenever the polish times out). A
            # shape rule that exists only in the objective is a shape rule this plan never sees.
            mxs = m.NewIntVar(0, max(gW, gH), f"mx{lvl}_{r['id']}")
            mns = m.NewIntVar(0, max(gW, gH), f"mn{lvl}_{r['id']}")
            m.AddMaxEquality(mxs, [w, h])
            m.AddMinEquality(mns, [w, h])

            # THE ROOM'S OWN PROPORTION BAND, HARD (WP-11.7), AND NOT AN INVENTED TOLERANCE.
            # WP-11.7 was planned as per-room side bounds at an authored tolerance tau. It is
            # this instead, because the corpus already states the rule and tau would have been
            # a number nobody could source. Measured before choosing: all 23 dimensioned rooms
            # on `plans/tidewater-georgian-careful.json` declare a shape INSIDE their own type's
            # `dimensions.proportion` band, so binding the band constrains the drawing without
            # contradicting one authored record.
            #
            # It is the band `plan_check`'s drawn layer already convicts a room for leaving, so
            # the placer now proves what the critic tests -- `vertical_score`'s own rule that
            # the search and the arbiter must not convict and acquit the same house. One
            # spelling, `GEO.shape_band`, which the soft term below already reads.
            #
            # DOWNGRADABLE, and RANKED ABOVE A WALL PIN -- see `_RANK`, which carries the
            # measurement that decided it. The two cannot both be hard on this plan, and a
            # released wall pin keeps its 14 points in the objective, which is what CLAUDE.md
            # has always said an `exterior_walls` entry is worth.
            _ceil, _src = GEO.shape_band(r.get("type"))
            _nm = r.get('name') or r['id']
            if _ceil and (lvl, r["id"]) in downgraded:
                # proven unable to co-hold with the rest: stated, and scored rather than
                # forced, the same shape a downgraded wall pin takes six hundred lines down
                reqs.notes.append(
                    f"{_nm}'s own proportion band ({_ceil:g} to 1) could not co-hold with the "
                    f"other declared facts — downgraded, so this room may be drawn a shape its "
                    f"own record does not admit, and the drawn layer will say so")
            elif _ceil:
                _sh = reqs.lit(f"{_nm} is drawn no longer than {_ceil:g} to 1 — the "
                               f"proportion band its own room record states ({_src})",
                               kind="shape", key=(lvl, r["id"]))
                # STATED ON max/min, AND THE OBVIOUS REWRITE IS SLOWER — MEASURED, BECAUSE IT
                # LOOKS LIKE A FREE WIN AND IS NOT. `max(w,h) <= c * min(w,h)` is exactly
                # `w <= c*h AND h <= c*w` for positive sides, and that form needs no
                # AddMaxEquality/AddMinEquality pair, so it reads as strictly cheaper. Timed on
                # the two shipped plans with all wall pins released and the heuristic hint:
                #
                #     max/min (this form)     spec-builder 29.6 s   tidewater 11.3 s
                #     w <= c*h AND h <= c*w   spec-builder 48.2 s   tidewater 20.4 s
                #
                # CP-SAT's max/min propagators are stronger here than two reified linear
                # constraints, by a factor of about 1.7. The pair is built unconditionally
                # above and the soft aspect term shares it, so it costs nothing to reuse.
                m.Add(10 * mxs <= int(round(_ceil * 10)) * mns).OnlyEnforceIf(_sh)
            else:
                # The FLOOR is deliberately not stated: every room record's proportion floor is
                # 1.0 since the 3 Sep ruling, and `mxs >= mns` holds by construction, so a floor
                # constraint would be a branch that can never bite.
                reqs.notes.append(
                    f"{_nm}: its room type states no proportion band, so its drawn SHAPE is "
                    f"unconstrained here and unjudged by the drawn layer too — it may come "
                    f"back any shape at all and nothing will say so")
            if objective:
                # mirror level_score's own terms, term for term: area error
                # (10 x |got-want|/want) and aspect sanity (6 per ratio point
                # past 2.6, linearized against the short side)
                target = int(round(min(max(1.20, fill * 1.10), 1.22) * areaU))
                dev = m.NewIntVar(0, gW * gH, "")
                diff = m.NewIntVar(-gW * gH, gW * gH, "")
                m.Add(diff == a - target)
                m.AddAbsEquality(dev, diff)
                penalties.append((dev, max(1, int(round(10 * SCALE / max(areaU, 1))))))
                mx, mn = mxs, mns      # built above, unconditionally (WP-11.7)
                ov10 = m.NewIntVar(0, 10 * max(gW, gH), "")
                # THE `26` HERE WAS 2.6 x 10 -- THE SAME UNIVERSAL CONSTANT `level_score`
                # CARRIED, SPELLED A SECOND TIME (WP-9.4). Correcting the heuristic alone
                # would have fixed one of the two: `auto` sends 16 of 21 partis through this
                # engine, and the sheet that raised Phase 9 was CP-drawn -- its caption reads
                # "proven ... no placement exists". So the ceiling is read from the room's own
                # `dimensions.proportion` in BOTH engines, from geometry.shape_band(), which
                # is the one spelling. The corpus has been bitten by a rule written twice at
                # least four times; this is not a fifth.
                _ceil, _src = GEO.shape_band(r.get("type"))
                m.Add(ov10 >= 10 * mx - int(round(_ceil * 10)) * mn)
                penalties.append((ov10, 6))
                # The width floor the room's own record states, mirrored from level_score's
                # `(floor - short) * WIDTH_W`. A soft penalty and never a bound: a hard floor
                # here would manufacture the infeasibility `lo_side` above was written to
                # avoid, and WP-6.3 refused hard pins for inferred structure on the stronger
                # ground that only `kind == "wall"` literals are downgradable.
                _floor = GEO.width_floor(r.get("type"))
                if _floor and GEO.WIDTH_W:
                    underw = m.NewIntVar(0, max(gW, gH), "")
                    m.Add(underw >= int(round(_floor * U)) - mn)
                    penalties.append((underw, max(1, int(round(GEO.WIDTH_W)))))
            xiv.append(m.NewIntervalVar(x, w, m.NewIntVar(gx0, gx1, ""), f"xi{lvl}_{r['id']}"))
            yiv.append(m.NewIntervalVar(y, h, m.NewIntVar(gy0, gy1, ""), f"yi{lvl}_{r['id']}"))
            rooms[(lvl, r["id"])] = {"x": x, "y": y, "w": w, "h": h, "a": a, "r": r,
                                     "maxside": max(dw, dl)}
        m.AddNoOverlap2D(xiv, yiv)
        # coverage floor: no-overlap + containment + this bounds the void the
        # absorb pass must grow rooms into (the guillotine heuristic tiles exactly)
        upper_area = sum(rooms[(lvl, r["id"])]["a"] for r in rs)
        voids_below = ([r for r in (prep.get(0) or [])
                        if isinstance(r.get("_void"), dict) and not r["_void"].get("roofed")]
                       if lvl == 1 else [])
        if voids_below:
            # An upper storey over a courtyard cannot cover the footprint, and must not be
            # asked to (OQ 55). Without this the coverage floor and the open-void constraint
            # below contradict each other on every courtyard plan: the storey is required to
            # fill 97% of the block AND to leave the hole empty, and CP-SAT correctly reports
            # a brief that is perfectly buildable as infeasible. The hole comes off the target.
            # Written with integer coefficients (x100) because CP-SAT takes no float ones.
            c100 = int(round(COVERAGE * 100))
            void_area = sum(rooms[(0, v["id"])]["a"] for v in voids_below
                            if (0, v["id"]) in rooms)
            m.Add(100 * upper_area + c100 * void_area >= c100 * Wi * Hi)
        elif len(els.get(lvl) or []) > 1:
            # WP-11.11: PER ELEMENT. A coverage floor over the union would let a dependency
            # sit half empty while the main block over-filled to make up the total, which is
            # the "two elements flattened into one" reading this model refuses.
            for _e in (els or {}).get(lvl, []):
                _ids = [rid for rid in (_e.get("rooms") or []) if (lvl, rid) in rooms]
                if not _ids:
                    continue
                _ex, _ey = int(round(_e["x"] * U)), int(round(_e["y"] * U))
                _eW, _eH = int(round(_e["W"] * U)), int(round(_e["H"] * U))
                m.Add(sum(rooms[(lvl, rid)]["a"] for rid in _ids)
                      >= int(COVERAGE * _eW * _eH))
        else:
            m.Add(upper_area >= int(COVERAGE * Wi * Hi))

        # ---- declared exterior walls
        contested = _contested_corners(rs)
        for r in rs:
            v = rooms[(lvl, r["id"])]
            walls = list(r.get("exterior_walls") or [])
            _ex, _ey, _eW, _eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
            # WP-11.11, and it is WP-11.9's ruling 4 inside the solver: exterior is exterior.
            # A face on the dependency's own boundary carries a window, a sill, a load and the
            # weather, so a room's declared wall is a fact about ITS element.
            pins = {"S": v["y"] == _ey, "N": v["y"] + v["h"] == _ey + _eH,
                    "W": v["x"] == _ex, "E": v["x"] + v["w"] == _ex + _eW}
            diag_ok = [wl for wl in walls if wl in pins]
            if not diag_ok:
                continue
            softened = _protruding(r) or r["id"] in contested
            if softened:
                why = "it protrudes" if _protruding(r) else "its corner is contested"
                if r["id"] in contested:
                    reqs.notes.append(f"{r.get('name') or r['id']}: {contested[r['id']]}")
                lit = reqs.lit(f"{r.get('name') or r['id']} declares exterior walls "
                               f"{'/'.join(walls)} — {why}, so it must reach at "
                               f"least one of them (the others are scored, not forced)",
                               kind="wall-soft")
                touch = []
                for wl in diag_ok:
                    b = m.NewBoolVar("")
                    m.Add(pins[wl]).OnlyEnforceIf(b)
                    touch.append(b)
                m.AddBoolOr(touch).OnlyEnforceIf(lit)
                if objective:
                    # unreached declared walls keep the heuristic's own 14-point score
                    for b in touch:
                        penalties.append((b.Not(), 14 * SCALE // max(1, len(touch))))
            else:
                for wl in diag_ok:
                    key = (lvl, r["id"], wl)
                    if key in downgraded:
                        # downgraded pins carry their proof status honestly:
                        # "proven" only after the reinstatement pass tested THIS
                        # pin alone at THIS footprint; a pin the budget never
                        # re-proved says it was carried, never that it was proven
                        how = ("carried from the conflict core — not individually "
                               "re-proven in budget" if key in unproven else
                               "proven — restored alone, no placement exists")
                        reqs.notes.append(
                            f"{r.get('name') or r['id']}'s declared {wl} wall could not "
                            f"co-hold with the other declared facts ({how}) — read as "
                            f"exposure in the massing, scored, not forced")
                        if objective:
                            b = m.NewBoolVar("")
                            m.Add(pins[wl]).OnlyEnforceIf(b)
                            penalties.append((b.Not(), 14 * SCALE))
                    else:
                        lit = reqs.lit(f"{r.get('name') or r['id']} declares an exterior "
                                       f"wall on the {wl} — it must sit on that boundary",
                                       kind="wall", key=key)
                        m.Add(pins[wl]).OnlyEnforceIf(lit)

        idx0 = {r["id"]: r for r in rs}

        # ---- THE SPANNING PASSAGE, ON THE BLOCK'S OWN AXIS (WP-11.7)
        #
        # A circulation room declaring an OPPOSITE PAIR is the centre passage, and this file's
        # own docstring has said since WP-2.3 that "its two pins ARE the spanning rule". They
        # were -- until WP-11.7 ranked the shape band above the wall pins, at which point the
        # first infeasible round releases all 22 of them and the spanning rule goes with them.
        # Measured: the Tidewater passage came back 40 ft wide and 9 ft deep, running across
        # the house instead of through it, and `plan_check`'s entrance-axis census read
        # `passage_has_no_through_axis: 1` and compared nothing.
        #
        # So the rule is stated as itself rather than inferred from two pins that now rank
        # below it: the room SPANS its declared pair, and its centreline is the block's.
        # `kind="axis"`, ranked between wall and shape -- more authored than the corpus's rule
        # about a room type, less authored than nothing (it is read off THIS record's own
        # `exterior_walls`, and it is the diagram the parti is named for).
        #
        # It is one requirement, not two, so a conflict names the passage and its axis rather
        # than an anonymous pair of inequalities -- the same reason the programme size is one
        # literal per room.
        # WHICH room, and it is NOT "every circulation room declaring an opposite pair".
        # Written that way first, and measured: on the Tidewater record it selects TWO -- the
        # Centre Passage and the Back Hall (a `back-hall` is circulation and declares N and S
        # as a hyphen, not as a spine). Two rooms both pinned to the block's centre line cannot
        # both hold, so the round loop released BOTH axis pins and the passage went back to
        # running across the house. An axis rule that names two rooms names none.
        #
        # The one it means is the room the FRONT DOOR OPENS INTO -- which is exactly the
        # relation `plan_check`'s own entrance-axis census walks, threshold room to circulation
        # room, so the placer aims at the thing the critic measures. Where that picks out no
        # room, or more than one, the axis is UNJUDGED and nothing is pinned: a spine the record
        # does not single out is not one this engine may invent.
        _entered = set()
        for r in rs:
            if _cls(r.get("type")) != "threshold":
                continue
            if not any(d.get("to") == "exterior" for d in (r.get("doors") or [])):
                continue
            for d in (r.get("doors") or []):
                t = d.get("to")
                if t and t != "exterior" and (lvl, t) in rooms \
                        and _cls((idx0.get(t) or {}).get("type")) == "circulation":
                    _entered.add(t)
        _spines = [r for r in rs if r["id"] in _entered
                   and ({"S", "N"} <= set(r.get("exterior_walls") or [])
                        or {"W", "E"} <= set(r.get("exterior_walls") or []))]
        if len(_spines) != 1:
            if any(_cls(r.get("type")) == "circulation"
                   and ({"S", "N"} <= set(r.get("exterior_walls") or [])
                        or {"W", "E"} <= set(r.get("exterior_walls") or [])) for r in rs):
                reqs.notes.append(
                    f"level {lvl}: {len(_spines)} circulation room(s) reached from the front "
                    f"door declare an opposite pair, so which one is the spine is UNJUDGED and "
                    f"no axis is pinned — one room, or none")
        for r in _spines:
            walls = set(r.get("exterior_walls") or [])
            v = rooms[(lvl, r["id"])]
            _ex, _ey, _eW, _eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
            if {"S", "N"} <= walls:
                span, ctr, ext = (v["y"], v["h"], _eH), (v["x"], v["w"], _eW), "N-S"
            elif {"W", "E"} <= walls:
                span, ctr, ext = (v["x"], v["w"], _eW), (v["y"], v["h"], _eH), "E-W"
            else:
                continue
            key = (lvl, r["id"])
            if key in downgraded:
                reqs.notes.append(
                    f"{r.get('name') or r['id']}'s through-axis could not co-hold with the "
                    f"other declared facts — downgraded, so it may be drawn across the house "
                    f"rather than through it")
                continue
            _ax = reqs.lit(f"{r.get('name') or r['id']} runs {ext} through the house and sits "
                           f"on its centre line — it declares both {ext.replace('-', ' and ')} "
                           f"walls, which is the spanning rule",
                           kind="axis", key=key)
            m.Add(span[0] == 0).OnlyEnforceIf(_ax)
            m.Add(span[0] + span[1] == span[2]).OnlyEnforceIf(_ax)
            # SPANNING ONLY, AND THE CENTRING IS REFUSED WITH ITS MEASUREMENT.
            #
            # `PLAN-OF-ACTION.md` asks for "the spanning passage pinned on the block axis" and
            # the plan file spells it `2x + w == W`. Built and measured: with the shape bands
            # held and ALL 22 wall pins already released -- the most permissive model this
            # engine can offer -- adding the centring makes it INFEASIBLE in 0.9 s.
            #
            # The arithmetic says why, and it is a fact about the record rather than the
            # solver. The Centre Passage declares 12 x 34 ft; spanning the 40.08 ft depth puts
            # it 10.2 ft wide, and centred on a 60 ft front that leaves two strips of 24.9 ft
            # holding about 2,000 sf of programme in 1,992 sf of floor. That is an exact tiling
            # of both strips, by rooms that must each also sit inside their own proportion
            # band. There is no slack anywhere in it -- which is
            # `oq/the-placement-carries-no-wall-bands` measured from the other side.
            #
            # So the axis pin states the half that HOLDS: the passage runs through the house.
            # Its position along the front is left to the objective, where a centre-passage
            # term has scored it since WP-2.2. Do not reinstate the equality without first
            # re-running this measurement; a symmetric passage needs the footprint to gain the
            # slack that question is about, not a harder constraint.

        # ---- doors: declared topology must be geometrically real
        idx = idx0
        seen = set()
        for r in rs:
            v1 = rooms[(lvl, r["id"])]
            for d in (r.get("doors") or []):
                to = d["to"]
                if to == "exterior":
                    lit = reqs.lit(f"{r.get('name') or r['id']} has a door to the exterior "
                                   f"— it must reach the building envelope", kind="door")
                    onb = []
                    _ex, _ey, _eW, _eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
                    for cond in (v1["y"] == _ey, v1["y"] + v1["h"] == _ey + _eH,
                                 v1["x"] == _ex, v1["x"] + v1["w"] == _ex + _eW):
                        b = m.NewBoolVar("")
                        m.Add(cond).OnlyEnforceIf(b)
                        onb.append(b)
                    m.AddBoolOr(onb).OnlyEnforceIf(lit)
                    continue
                if to not in idx:
                    continue                    # other-level or outdoor: not this model's fact
                key = tuple(sorted((r["id"], to)))
                if key in seen:
                    continue
                seen.add(key)
                v2 = rooms[(lvl, to)]
                ovr = _door_overlap(d, v1, v2)
                lit = reqs.lit(f"{r.get('name') or r['id']} and {idx[to].get('name') or to} "
                               f"share a door — they must share enough wall for one",
                               kind="door")
                configs = []
                for a1, b1_ in ((v1, v2), (v2, v1)):
                    # overlap >= ovr needs all FOUR bounds: the two end-gap
                    # inequalities alone admit a side narrower than ovr sitting
                    # strictly inside the neighbour's span (a 2 ft landing
                    # against a 34 ft passage passes both and shares 2 ft)
                    b = m.NewBoolVar("")
                    m.Add(a1["x"] + a1["w"] == b1_["x"]).OnlyEnforceIf(b)
                    m.Add(a1["y"] <= b1_["y"] + b1_["h"] - ovr).OnlyEnforceIf(b)
                    m.Add(b1_["y"] <= a1["y"] + a1["h"] - ovr).OnlyEnforceIf(b)
                    m.Add(a1["h"] >= ovr).OnlyEnforceIf(b)
                    m.Add(b1_["h"] >= ovr).OnlyEnforceIf(b)
                    configs.append(b)
                    b2 = m.NewBoolVar("")
                    m.Add(a1["y"] + a1["h"] == b1_["y"]).OnlyEnforceIf(b2)
                    m.Add(a1["x"] <= b1_["x"] + b1_["w"] - ovr).OnlyEnforceIf(b2)
                    m.Add(b1_["x"] <= a1["x"] + a1["w"] - ovr).OnlyEnforceIf(b2)
                    m.Add(a1["w"] >= ovr).OnlyEnforceIf(b2)
                    m.Add(b1_["w"] >= ovr).OnlyEnforceIf(b2)
                    configs.append(b2)
                m.AddBoolOr(configs).OnlyEnforceIf(lit)

        # ---- soft: bay snapping with counted relaxations, per room edge
        if objective:
            for r in rs:
                v = rooms[(lvl, r["id"])]
                # WP-11.11. The DOMAIN spans every element (a west dependency sits at a
                # negative x, and `NewIntVar(0, span)` here would have made a SOFT term
                # infeasible), and the top line the y edge may legitimately sit on is the
                # room's OWN element's, not the main block's.
                _ex, _ey, _eW, _eH = ebox.get((lvl, r["id"]), (0, 0, Wi, Hi))
                for axis, dlo, dhi, top in (("x", gx0, gx1, None),
                                            ("y", gy0, gy1, _ey + _eH)):
                    edges = (v["x"], (v["x"] + v["w"])) if axis == "x" \
                        else (v["y"], (v["y"] + v["h"]))
                    span = max(1, dhi - dlo)
                    for e in edges:
                        ev = m.NewIntVar(dlo, dhi, "")
                        m.Add(ev == e)
                        # AddModuloEquality TRUNCATES toward zero, so a negative dividend
                        # gives a negative remainder and `emod`'s [0, bay-1] domain would make
                        # this SOFT term infeasible on a west dependency. The edge is shifted
                        # by a whole number of bays first -- `dlo` floored to the module, so
                        # the grid's own phase is untouched -- and the modulo sees a
                        # non-negative number. Inert on every plan in the corpus, where
                        # `dlo` is 0.
                        base = (dlo // bayU) * bayU
                        if base:
                            evp = m.NewIntVar(0, max(1, dhi - base), "")
                            m.Add(evp == ev - base)
                        else:
                            evp = ev          # every plan in the corpus; no extra variable
                        emod = m.NewIntVar(0, bayU - 1, "")
                        m.AddModuloEquality(emod, evp, bayU)
                        d = m.NewIntVar(0, bayU, "")
                        m.AddMinEquality(d, [emod, bayU - emod])
                        if axis == "y":
                            # the element's own top edge is a legitimate line even off-module
                            dH = m.NewIntVar(0, span, "")
                            dfH = m.NewIntVar(-span, span, "")
                            m.Add(dfH == ev - top)
                            m.AddAbsEquality(dH, dfH)
                            dmin = m.NewIntVar(0, span, "")
                            m.AddMinEquality(dmin, [d, dH])
                            d = dmin
                        off = m.NewBoolVar("")
                        m.Add(d <= tolU).OnlyEnforceIf(off.Not())
                        penalties.append((off, 15))     # 1.5 per relaxation, x10

    # ---- nothing sits over a void open to the sky (OQ 55)
    #
    # This is the guarantee the 25 Aug merge lost. OQ 55 closed with the rule stated in BOTH
    # engines, and the engine that stated it as a HARD constraint -- the deleted build/solver.py
    # -- is the one that did not survive; what was left was geometry.py's 40-point charge, which
    # is a price a candidate can pay and still win. A courtyard is a hole: there is no floor
    # under an upper room placed over it, no bearing, and the roof that room needs is the hole
    # itself. That is not a preference and it is not scoreable, so here it is a constraint.
    #
    # ROOFED voids are deliberately exempt, and the exemption is the reason `roofed` is a
    # separate fact from `within_footprint`: a Charleston single's upper piazza sits squarely on
    # its lower one and is correct. A void over a void is likewise fine -- an upper gallery may
    # open onto the same court.
    #
    # Mirrors geometry.py's vertical_score() term for term, including its 1.0 ft overlap
    # tolerance, so the two engines cannot disagree about what "over" means. The RING remains
    # stated rather than searched (courtyard_slice()'s guillotine tree, which the CP engine
    # inherits through the heuristic hint) -- that half of OQ 55 is a layout problem, not a
    # constraint, and is left stated rather than half-solved.
    ground_rooms = prep.get(0) or []
    upper_rooms = prep.get(1) or []
    open_voids = [r for r in ground_rooms
                  if isinstance(r.get("_void"), dict) and not r["_void"].get("roofed")]
    if open_voids and upper_rooms:
        # STRICT: the rooms may abut the void's edge and may not enter it by any amount.
        # geometry.py charges its 40 points only past a 1.0 ft overlap, and mirroring that
        # tolerance here was a real bug for two reasons. A scoring noise-tolerance is not a
        # placement licence -- 1 ft of bedroom over a courtyard is a foot of floor with nothing
        # under it. And it broke the guarantee downstream: the solver placed a room exactly 1 ft
        # into the court, and _absorb's keep-out limiter only stops a room that has not already
        # crossed the line, so the room grew straight through the hole. Proven, then undone.
        for ur in upper_rooms:
            if isinstance(ur.get("_void"), dict):
                continue                    # void over void is fine
            uv = rooms.get((1, ur["id"]))
            if uv is None:
                continue
            for vr in open_voids:
                gv = rooms.get((0, vr["id"]))
                if gv is None:
                    continue
                lit = reqs.lit(
                    f"{ur.get('name') or ur['id']} cannot sit over "
                    f"{vr.get('name') or vr['id']}, which is open to the sky: no floor under "
                    f"it, no bearing, and the roof it needs is the hole",
                    kind="void")
                # Separated on one axis or the other, by more than the shared tolerance.
                seps = []
                for cond in (uv["x"] + uv["w"] <= gv["x"],
                             gv["x"] + gv["w"] <= uv["x"],
                             uv["y"] + uv["h"] <= gv["y"],
                             gv["y"] + gv["h"] <= uv["y"]):
                    b = m.NewBoolVar("")
                    m.Add(cond).OnlyEnforceIf(b)
                    seps.append(b)
                m.AddBoolOr(seps).OnlyEnforceIf(lit)

    # ---- entrance front. HARD only for the threshold room that actually opens
    # to the exterior — that is the entry. The room catalog classes mudrooms
    # and entrance halls as threshold too, and WP-2.2's entrance_score charges
    # every one of them 100 points off the front (a finding, see the WP-2.3
    # report); those stay SOFT at the same 100 so the engines score alike, but
    # a service threshold can never render a brief infeasible.
    ground = prep.get(0) or []
    Wi0, Hi0 = int(round(fpd["W"] * U)), int(round(fpd["H"] * U))
    if ewalls:
        byid = {r["id"]: r for r in ground}
        for r in ground:
            if _cls(r["type"]) != "threshold" or (0, r["id"]) not in rooms:
                continue
            v = rooms[(0, r["id"])]
            pins = {"S": v["y"] == 0, "N": v["y"] + v["h"] == Hi0,
                    "W": v["x"] == 0, "E": v["x"] + v["w"] == Wi0}
            opens_out = any(d.get("to") == "exterior" for d in (r.get("doors") or []))
            onb = []
            for wl in ewalls:
                if wl not in pins:
                    continue
                b = m.NewBoolVar("")
                m.Add(pins[wl]).OnlyEnforceIf(b)
                onb.append(b)
            if not onb:
                continue
            if opens_out:
                lit = reqs.lit(f"the entrance faces {'/'.join(sorted(ewalls))} and "
                               f"{r.get('name') or r['id']} is the entry — it must sit "
                               f"on that front", kind="entrance")
                m.AddBoolOr(onb).OnlyEnforceIf(lit)
            elif objective:
                off = m.NewBoolVar("")
                m.AddBoolOr(onb + [off])
                penalties.append((off, 100 * SCALE))
            if objective:
                for d in (r.get("doors") or []):
                    t = d["to"]
                    if t in byid and _cls(byid[t]["type"]) == "circulation" and (0, t) in rooms:
                        vt = rooms[(0, t)]
                        tpins = {"S": vt["y"] <= 1, "N": vt["y"] + vt["h"] >= Hi0 - 1,
                                 "W": vt["x"] <= 1, "E": vt["x"] + vt["w"] >= Wi0 - 1}
                        onbt = []
                        for wl in ewalls:
                            if wl not in tpins:
                                continue
                            bb = m.NewBoolVar("")
                            m.Add(tpins[wl]).OnlyEnforceIf(bb)
                            onbt.append(bb)
                        if onbt:
                            far = m.NewBoolVar("")
                            m.AddBoolOr(onbt + [far])
                            penalties.append((far, 40 * SCALE))

    # ---- soft zoning + ceremonial depth + centre passage + wet stacks
    if objective and ewalls and ground:
        def dist_var(v):
            exprs = []
            for wl in ewalls:
                if wl == "S": exprs.append(v["y"])
                elif wl == "N": exprs.append(Hi0 - (v["y"] + v["h"]))
                elif wl == "W": exprs.append(v["x"])
                elif wl == "E": exprs.append(Wi0 - (v["x"] + v["w"]))
            dv = m.NewIntVar(0, max(Wi0, Hi0), "")
            m.AddMinEquality(dv, exprs)
            return dv

        OPP = {"S": "N", "N": "S", "W": "E", "E": "W"}
        rear = [OPP[w] for w in ewalls if w in OPP]
        dists = {}
        byid = {r["id"]: r for r in ground}
        for r in ground:
            if (0, r["id"]) not in rooms:
                continue
            v = rooms[(0, r["id"])]
            fc = _cls(r["type"])
            if fc in ("public", "living", "dining", "service", "work") or \
                    C["rooms"].get(r["type"], {}).get("privacy_rank") is not None:
                dists[r["id"]] = dist_var(v)
            if fc in ("public", "living", "dining"):
                p = m.NewBoolVar("")
                m.Add(dists[r["id"]] <= 1).OnlyEnforceIf(p.Not())
                penalties.append((p, 35))
            elif fc in ("service", "work"):
                rd_exprs = []
                for wl in rear:
                    if wl == "S": rd_exprs.append(v["y"])
                    elif wl == "N": rd_exprs.append(Hi0 - (v["y"] + v["h"]))
                    elif wl == "W": rd_exprs.append(v["x"])
                    elif wl == "E": rd_exprs.append(Wi0 - (v["x"] + v["w"]))
                if rd_exprs:
                    rd = m.NewIntVar(0, max(Wi0, Hi0), "")
                    m.AddMinEquality(rd, rd_exprs)
                    p = m.NewBoolVar("")
                    m.Add(rd <= 1).OnlyEnforceIf(p.Not())
                    penalties.append((p, 20))
                pf = m.NewBoolVar("")
                m.Add(dists[r["id"]] >= 2).OnlyEnforceIf(pf.Not())
                penalties.append((pf, 30))
        for r in ground:
            rank = C["rooms"].get(r["type"], {}).get("privacy_rank")
            if rank is None or r["id"] not in dists:
                continue
            for d in (r.get("doors") or []):
                t = d["to"]
                trank = C["rooms"].get(byid.get(t, {}).get("type", ""), {}).get("privacy_rank") \
                    if t in byid else None
                if trank is None or trank <= rank or t not in dists:
                    continue
                p = m.NewBoolVar("")
                m.Add(dists[t] >= dists[r["id"]] - 1).OnlyEnforceIf(p.Not())
                penalties.append((p, 6 * (trank - rank) * SCALE))
        for r in ground:
            if "centre" in (r["type"] or "") or "center" in (r["type"] or ""):
                v = rooms[(0, r["id"])]
                cd = m.NewIntVar(-Wi0 * 2, Wi0 * 2, "")
                m.Add(cd == 2 * v["x"] + v["w"] - Wi0)
                cda = m.NewIntVar(0, Wi0 * 2, "")
                m.AddAbsEquality(cda, cd)
                penalties.append((cda, 1))

    if objective:
        upper = prep.get(1) or []
        wet_g = [r for r in ground if set(r.get("fixtures") or []) and (0, r["id"]) in rooms]
        for r in upper:
            if not set(r.get("fixtures") or []) or (1, r["id"]) not in rooms:
                continue
            v = rooms[(1, r["id"])]
            over = []
            for g in wet_g:
                vg = rooms[(0, g["id"])]
                b = m.NewBoolVar("")
                m.Add(v["x"] < vg["x"] + vg["w"]).OnlyEnforceIf(b)
                m.Add(vg["x"] < v["x"] + v["w"]).OnlyEnforceIf(b)
                m.Add(v["y"] < vg["y"] + vg["h"]).OnlyEnforceIf(b)
                m.Add(vg["y"] < v["y"] + v["h"]).OnlyEnforceIf(b)
                over.append(b)
            none = m.NewBoolVar("")
            m.AddBoolOr(over + [none])
            penalties.append((none, 8 * SCALE))

        # WP-7.4 (OQ 95): declared `stacks_over`, charged. SOFT, and that is the whole design.
        #
        # OQ 95 recorded that a stacking constraint here "outranks every authored exterior wall
        # in the corpus", because the downgrade loop below reads
        # `[key for _t, k, key in core if k == "wall" and key]` and a non-wall pin can never
        # enter it -- measured, a hard version downgraded an authored kitchen wall to satisfy an
        # inferred stack, which is the OQ 52 family (an authored fact losing silently to a
        # derived one). That is true OF A HARD PIN. A penalty is not a pin: it creates no
        # assumption literal, never enters a conflict core, and cannot displace anything. The
        # blocker is sidestepped rather than solved, and the downgrade loop is untouched.
        #
        # Shaped exactly like the wet-stack term above so the two read as one mechanism, and
        # weighted from the same sweep that set geometry.STACK_W (measured on the heuristic:
        # broken claims across all 14 declaring partis).
        for r in upper:
            so = r.get("stacks_over")
            if not so or (1, r["id"]) not in rooms or (0, so) not in rooms:
                continue     # target not on the level below: unjudged, and unjudged is not charged
            v, vg = rooms[(1, r["id"])], rooms[(0, so)]
            b = m.NewBoolVar("")
            m.Add(v["x"] < vg["x"] + vg["w"]).OnlyEnforceIf(b)
            m.Add(vg["x"] < v["x"] + v["w"]).OnlyEnforceIf(b)
            m.Add(v["y"] < vg["y"] + vg["h"]).OnlyEnforceIf(b)
            m.Add(vg["y"] < v["y"] + v["h"]).OnlyEnforceIf(b)
            none = m.NewBoolVar("")
            m.AddBoolOr([b, none])
            penalties.append((none, _w(GEO.STACK_W)))

        # WP-7.4 (OQ 97): over-capacity clear spans, charged, on the same structural fact the
        # heuristic charges and plan_check reports.
        #
        # THE BEARING SET IS FINITE AND SMALL HERE, which is what makes this affordable. This
        # model is on a 1-ft integer grid (U = 1), and structure.bearing_lines calls an interior
        # wall bearing when it sits within 0.75 ft of a bay multiple -- so on whole feet the
        # only qualifying positions ARE the multiples. The candidate bearing lines are therefore
        # {0, bay, 2*bay, ... , extent}: seven of them on a 60 ft frontage at a 10 ft bay, not a
        # continuum, and the span rule becomes a handful of clauses over one bool per line.
        #
        # HALF-REIFIED ON PURPOSE. `f -> (face == L)` and nothing in the other direction: a line
        # may only be claimed bearing if a room face is really on it, while leaving it unclaimed
        # is free. False is the penalised direction, so the solver can never buy a bearing line
        # it has not placed a wall on, and the expensive `!=` half of a full reification is
        # never built. Measured: the model keeps its proof of tidewater-georgian-careful.
        cap_ft = _span_capacity(plan)
        if cap_ft:
            for lvl in (0, 1):
                rs = prep.get(lvl) or []
                if not rs:
                    continue
                # WP-11.11: PER ELEMENT. A clear span is a run of floor inside ONE mass; a
                # window of grid lines drawn across the gap between two detached elements is
                # the defect WP-11.9 removed from `structure.wall_lines`, arriving here.
                for _e in ((els or {}).get(lvl) or [{"id": "main", "x": 0, "y": 0,
                                                     "W": Wi / float(U), "H": Hi / float(U),
                                                     "rooms": [r["id"] for r in rs]}]):
                  _ex, _ey = int(round(_e["x"] * U)), int(round(_e["y"] * U))
                  _eW, _eH = int(round(_e["W"] * U)), int(round(_e["H"] * U))
                  _ers = [r for r in rs if r["id"] in set(_e.get("rooms") or [])]
                  if not _ers:
                      continue
                  for axis, lo0, extent in (("x", _ex, _ex + _eW), ("y", _ey, _ey + _eH)):
                    lines = list(range(lo0, extent + 1, bayU))
                    if lines[-1] != extent:
                        lines.append(extent)
                    act = {}
                    for L in lines[1:-1]:
                        faces = []
                        for r in _ers:
                            if (lvl, r["id"]) not in rooms:
                                continue
                            v = rooms[(lvl, r["id"])]
                            lo = v["x"] if axis == "x" else v["y"]
                            sz = v["w"] if axis == "x" else v["h"]
                            f1 = m.NewBoolVar(""); m.Add(lo == L).OnlyEnforceIf(f1)
                            f2 = m.NewBoolVar(""); m.Add(lo + sz == L).OnlyEnforceIf(f2)
                            faces += [f1, f2]
                        a_ = m.NewBoolVar("")
                        m.AddBoolOr(faces + [a_.Not()])   # a_ -> some face really sits on L
                        act[L] = a_
                    # Every run of consecutive grid lines longer than the capacity must
                    # contain a bearing line, or it pays.
                    #
                    # THIS IS NOT THE HEURISTIC'S QUANTITY AND THE COMMENT USED TO IMPLY IT WAS.
                    # `geometry._span_charge` charges ONCE PER over-capacity span, in proportion
                    # to how far over it is. This anchors one clause at EVERY grid line, so a
                    # single long clear span is charged once per anchor that cannot reach a
                    # bearing line: with lines every 10 ft, a 20 ft capacity and bearing only at
                    # 0 and 60, the heuristic charges 3x the weight and this charges 4x. Both
                    # grow with the span and neither mis-ranks two placements that differ only
                    # in span, but they are different numbers and calling them mirrors was
                    # loose. Making them identical needs reified consecutive-line logic, which
                    # is the expensive formulation this one exists to avoid.
                    #
                    # The `break` is sound: for a given `lo_L` the SHORTEST over-capacity window
                    # has the fewest inner lines, so its clause is the strictest, and every
                    # longer window's clause is implied by it.
                    capU = int(cap_ft * U)
                    for i, lo_L in enumerate(lines):
                        for hi_L in lines[i + 1:]:
                            if hi_L - lo_L <= capU:
                                continue
                            inner = [act[L] for L in lines[i + 1:] if L < hi_L and L in act]
                            viol = m.NewBoolVar("")
                            m.AddBoolOr(inner + [viol])
                            penalties.append((viol, _w(GEO.SPAN_W)))
                            break        # the shortest over-capacity window implies the rest

    if objective and penalties:
        m.Minimize(sum(p * wgt for p, wgt in penalties))
    m.AddAssumptions([lit for lit, _t, _k, _key in reqs.lits])
    return m, rooms, reqs


def _hint_heuristic(model, rooms, plan, parti, seed, candidates=40):
    """Warm-start from a heuristic run — the fallback doubles as the guide. The
    soft-blind phase A gets a cheap 40-candidate run; phase B is hinted with the
    full search's placement, which already optimized the SOFT terms and only
    needs its hard violations repaired — a far better basin than phase A's."""
    try:
        # level_aware=False deliberately (WP-7.1): a hint's only job is to be REPAIRABLE.
        # Hinting with the level-aware run took `tidewater-georgian-careful` from OPTIMAL to
        # UNKNOWN at budget -- a hint better by the heuristic's own score, in a basin the
        # proof could not close. See solve_heuristic's docstring.
        h = GEO.solve_heuristic(copy.deepcopy(plan), parti, candidates=candidates, seed=seed,
                                level_aware=False)
    except Exception:
        return
    if "error" in h:
        return
    for lv in h["levels"]:
        idx = lv.get("index", 0)
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g or (idx, r["id"]) not in rooms:
                continue
            v = rooms[(idx, r["id"])]
            model.AddHint(v["x"], int(round(g["x_ft"] * U)))
            model.AddHint(v["y"], int(round(g["y_ft"] * U)))
            model.AddHint(v["w"], int(round(g["width_ft"] * U)))
            model.AddHint(v["h"], int(round(g["depth_ft"] * U)))


def _hint_values(model, rooms, values):
    for key, (x, y, w, h) in values.items():
        if key not in rooms:
            continue
        v = rooms[key]
        model.AddHint(v["x"], x)
        model.AddHint(v["y"], y)
        model.AddHint(v["w"], w)
        model.AddHint(v["h"], h)


def _absorb(rects, W, H, caps=None, keepout=(), ratios=None, bounds=None):
    """Grow rooms into the void the coverage floor allows, edges moving outward
    only — a pinned boundary edge is already at its boundary, and a shared edge
    stops exactly at its neighbour, so nothing hard can break. `caps` bounds
    each room at the model's own size band (max area, sf): the solve PROVED
    "rooms at program size", and un-capped absorption was found stretching a
    2.8 sf linen press to 8 sf — a drawing quietly violating its own proof.
    A cap can leave residual void; honest empty floor beats an inflated room.

    `keepout` is a list of (x, y, w, h) this level's rooms may not grow over,
    and it exists because "nothing hard can break" was true only WITHIN a level
    (OQ 55). This pass runs per level with no cross-level view, so on a
    courtyard plan the CP engine proved no upper room sat over the open court
    and then this grew one across it — a guarantee proven and then undone by a
    post-pass, which is the same shape of defect as OQ 52 and just as invisible,
    because the record it writes looks exactly like a solved plan. The keep-out
    rectangles limit growth in all four directions exactly as a sibling room
    does, so the proof survives into the drawing.

    `ratios` is the same guarantee for SHAPE (WP-11.7), and it is the third time this pass has
    been caught undoing a proof the solve had just made. CP now holds each room inside its own
    `dimensions.proportion` band as a hard, downgradable pin; this pass then grew three of them
    straight back out of it -- measured on `plans/tidewater-georgian-careful.json`, the library
    to 1.69 against a ceiling of 1.6, the powder room to 2.66 against 2.2, and a closet to 4.21
    against 4.0, all three with their pin still HELD. A cap here can leave residual void, and
    honest empty floor beats a room the record does not admit; that is the same trade the area
    cap above already makes and it is made the same way.

    A room whose pin was DOWNGRADED is deliberately absent from `ratios`: the record says its
    band could not hold, so this pass has nothing to preserve for it.

    `bounds` is `{room_id: (x, y, W, H)}` -- the room's OWN massing element (WP-11.11), and the
    FOURTH time this pass has been caught undoing what the solve proved. CP now holds every room
    inside its element's box; this pass then grew one straight out of it, measured on a
    hand-tagged `tidewater-georgian-careful`: the breakfast room was proved at y >= 4.95, the
    west dependency's own south edge, and absorbed to y = 1.6 -- 3.35 ft of drawn floor outside
    the mass it belongs to, in a record that looks exactly like a solved plan. The four `lim`
    seeds below are the element's four faces now, and `(0, 0, W, H)` on a one-rectangle house,
    which is every plan in this corpus."""
    ids = list(rects)
    caps = caps or {}
    ratios = ratios or {}
    bounds = bounds or {}

    def _fits(rid, w, h):
        """Would this rectangle still sit inside the band the solve proved for it?"""
        c = ratios.get(rid)
        if not c:
            return True
        lo, hi = min(w, h), max(w, h)
        return hi <= c * lo + 0.01
    if keepout:
        rects = dict(rects)
        for i, ko in enumerate(keepout):
            rects[f"\0keepout{i}"] = tuple(ko)
    for _ in range(8):
        moved = False
        for rid in ids:
            x, y, w, h = rects[rid]
            cap = caps.get(rid, float("inf"))
            bx, by, bW, bH = bounds.get(rid, (0.0, 0.0, W, H))
            lim = bx + bW
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and oy < y + h - 0.01 and y < oy + oh - 0.01 and ox >= x + w - 0.01:
                    lim = min(lim, ox)
            if lim - (x + w) > 0.01:
                nw = min(lim - x, max(w, cap / max(h, 0.01)))
                if nw - w > 0.01 and _fits(rid, nw, h):
                    w = nw; moved = True
            lim = by + bH
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and ox < x + w - 0.01 and x < ox + ow - 0.01 and oy >= y + h - 0.01:
                    lim = min(lim, oy)
            if lim - (y + h) > 0.01:
                nh = min(lim - y, max(h, cap / max(w, 0.01)))
                if nh - h > 0.01 and _fits(rid, w, nh):
                    h = nh; moved = True
            lim = bx
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and oy < y + h - 0.01 and y < oy + oh - 0.01 and ox + ow <= x + 0.01:
                    lim = max(lim, ox + ow)
            if x - lim > 0.01:
                nw = min(w + (x - lim), max(w, cap / max(h, 0.01)))
                if nw - w > 0.01 and _fits(rid, nw, h):
                    x -= nw - w; w = nw; moved = True
            lim = by
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and ox < x + w - 0.01 and x < ox + ow - 0.01 and oy + oh <= y + 0.01:
                    lim = max(lim, oy + oh)
            if y - lim > 0.01:
                nh = min(h + (y - lim), max(h, cap / max(w, 0.01)))
                if nh - h > 0.01 and _fits(rid, w, nh):
                    y -= nh - h; h = nh; moved = True
            rects[rid] = (round(x, 2), round(y, 2), round(w, 2), round(h, 2))
        if not moved:
            break
    return {k: v for k, v in rects.items() if not k.startswith("\0keepout")}


def _merge_runs(spans, gap=0.05):
    """Merge a list of (lo, hi) into disjoint runs, closing hairline gaps."""
    out = []
    for lo, hi in sorted(spans):
        if out and lo <= out[-1][1] + gap:
            out[-1][1] = max(out[-1][1], hi)
        else:
            out.append([lo, hi])
    return [[round(lo, 2), round(hi, 2)] for lo, hi in out]


def _count_relaxations(rects_by_level, W, H, bay, tol):
    """Interior wall lines off the bay grid — the heuristic's own definition of
    a compromise — counted from the solved placement (per unique line, per axis)."""
    relax = []
    for lvl, rects in rects_by_level.items():
        for axis in ("x", "y"):
            edges = {}
            for (x, y, w, h) in rects.values():
                if axis == "x":
                    edges.setdefault(round(x, 1), []).append((y, y + h))
                    edges.setdefault(round(x + w, 1), []).append((y, y + h))
                else:
                    edges.setdefault(round(y, 1), []).append((x, x + w))
                    edges.setdefault(round(y + h, 1), []).append((x, x + w))
            span = W if axis == "x" else H
            for e, spans in edges.items():
                if e <= 0.05 or e >= span - 0.05:
                    continue
                d = abs(e - round(e / bay) * bay)
                if axis == "y":
                    d = min(d, abs(e - H))
                if d > tol:
                    # Positioned, like the heuristic's (OQ 33). This counter already knew where
                    # the line was -- `e` is the edge coordinate and the level is the loop key --
                    # and threw it away to append a bare float.
                    #
                    # It also knew, and threw away, WHERE ALONG THAT LINE THERE IS A WALL. The
                    # earlier note here refused an extent because "an edge is a wall line shared
                    # by however many rooms abut it, and inventing an extent for it would be a
                    # drawn claim nobody measured" -- correct about the invention, wrong that
                    # there was nothing to measure. `runs` is the union of the room faces that
                    # actually sit on this line: measured, not invented, and possibly several
                    # disjoint pieces, which is why it is a list and not a from/to pair. The
                    # sheet had been drawing an extentless mark at the MIDDLE OF THE PLAN, which
                    # on the Tidewater placement put a dashed tick and a triangle inside the
                    # drawing room with no wall under either -- the "arrows that seem to point to
                    # anything and everything" of Lucas's review, and a mark the room's own click
                    # could not be made through.
                    relax.append({"off_ft": round(d, 2), "axis": axis,
                                  "at_ft": round(e, 2), "level": lvl,
                                  "runs": _merge_runs(spans)})
    return relax


def _score(rects_by_level, prep, levels, plan, fpd, ewalls, relax):
    """The heuristic's OWN scoring of this placement, term for term, so the
    acceptance comparison is apples to apples."""
    W, H = fpd["W"], fpd["H"]
    gr = rects_by_level.get(0, {})
    ur = rects_by_level.get(1, {})
    sg = (GEO.level_score(gr, prep[0]) + GEO.exterior_score(gr, prep[0], W, H)
          + GEO.adjacency_score(gr, prep[0], levels[0]["rooms"])
          + GEO.entrance_score(gr, prep[0], W, H, ewalls)
          + GEO.principal_and_service_score(gr, prep[0], W, H, ewalls)
          + GEO.ceremonial_score(gr, prep[0], W, H, ewalls)
          + GEO.centre_hall_symmetry_score(gr, prep[0], W, H))
    if prep.get(1) and ur:
        su = (GEO.level_score(ur, prep[1]) + GEO.exterior_score(ur, prep[1], W, H)
              + GEO.adjacency_score(ur, prep[1], levels[1]["rooms"])
              + GEO.centre_hall_symmetry_score(ur, prep[1], W, H))
    else:
        su = 0.0
    sv, vnotes = GEO.vertical_score(gr, ur, prep[0], prep.get(1, []), plan)
    # WP-7.4: the span charge belongs HERE too, and leaving it out would quietly falsify this
    # function's own first sentence. `_finish_feasible` chooses among hard-valid placements by
    # this score, so a term the heuristic's candidate loop charges and this one does not is a
    # term the CP path cannot act on however well the CP model is steered by it.
    try:
        _floor = _mod("structure", f"{ROOT}/build/structure.py").load_construction()["floor"]
    except Exception:
        _floor = None
    spc, over = GEO._span_charge(rects_by_level, prep, W, H, fpd["bay"],
                                 plan.get("style"), _floor)
    tot = sg + su + sv + spc + 1.5 * len(relax)
    return {"score": round(tot, 1), "sg": round(sg, 1), "su": round(su, 1),
            "sv": round(sv, 1), "span_charge": round(spc, 1),
            "spans_over_capacity": over, "vnotes": vnotes}


def _values(solver, rooms):
    return {key: (solver.Value(v["x"]), solver.Value(v["y"]),
                  solver.Value(v["w"]), solver.Value(v["h"]))
            for key, v in rooms.items()}


def _solve_assuming(plan, prep, fpd, ewalls, texts, time_s, downgraded=frozenset(),
                    seed=7):
    """One fresh hard-only model asserting only the named requirements;
    returns (status, sufficient-core-texts-or-None)."""
    from ortools.sat.python import cp_model
    model, _, reqs = _build(plan, prep, fpd, ewalls, downgraded, objective=False)
    model.ClearAssumptions()
    by_lit = [(lit, t) for lit, t, _k, _key in reqs.lits if t in texts]
    model.AddAssumptions([lit for lit, _ in by_lit])
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_s
    s.parameters.num_search_workers = 1
    s.parameters.random_seed = seed  # the same infeasible record names the same conflicts
    st = s.Solve(model)
    core = None
    if st == cp_model.INFEASIBLE:
        idx = set(s.SufficientAssumptionsForInfeasibility())
        core = [t for lit, t in by_lit if lit.Index() in idx]
    return st, core


# greedy drop order: the likely-removable first, the likely-essential last
_DROP_ORDER = ("program size", "share a door", "door to the exterior",
               "protrudes", "contested", "exterior wall", "is the entry")


def _extract_conflicts(plan, prep, fpd, ewalls, budget_s=20.0, seed_core=None,
                       downgraded=frozenset()):
    """Turn CP-SAT's sufficient core into a plain-language conflict set,
    minimized within a time budget, AT THE NATURAL FOOTPRINT — extracting at
    the growth-ceiling footprint instead was this module's first real bug (a
    wide, shallow footprint manufactures conflicts the natural one never had).

    Two phases: (1) iterate the solver's own sufficient core to a fixpoint —
    one solve per pass, typically a fast collapse; (2) greedy drop-one on the
    remainder, removable-first. If the budget runs out first, the larger
    honest core is returned with minimized=False — the note says so."""
    from ortools.sat.python import cp_model
    deadline = time.monotonic() + budget_s

    if seed_core is None:
        model, _, reqs = _build(plan, prep, fpd, ewalls, downgraded, objective=False)
        s = cp_model.CpSolver()
        s.parameters.max_time_in_seconds = max(2.0, budget_s / 3)
        s.parameters.num_search_workers = 1
        s.parameters.random_seed = 7
        if s.Solve(model) != cp_model.INFEASIBLE:
            return None, False
        idx = set(s.SufficientAssumptionsForInfeasibility())
        by_index = {lit.Index(): t for lit, t, _k, _key in reqs.lits}
        seed_core = [by_index[i] for i in idx if i in by_index]

    kept = list(seed_core)
    while time.monotonic() < deadline:
        st, core = _solve_assuming(plan, prep, fpd, ewalls, set(kept),
                                   min(4.0, max(0.5, deadline - time.monotonic())),
                                   downgraded)
        if st != cp_model.INFEASIBLE or core is None or len(core) >= len(kept):
            break
        kept = core
    minimized = True
    ordered = sorted(kept, key=lambda t: next(
        (i for i, k in enumerate(_DROP_ORDER) if k in t), len(_DROP_ORDER)))
    for t in ordered:
        if time.monotonic() > deadline:
            minimized = False
            break
        if len(kept) <= 1:
            break
        # 1.5s cap: a drop that stays infeasible usually proves fast; a keep
        # unproven in time simply stays kept (the safe direction) — but an
        # UNKNOWN keep is not a PROVEN keep, so it clears the minimized flag
        st, _ = _solve_assuming(plan, prep, fpd, ewalls, set(kept) - {t},
                                min(1.5, max(0.5, deadline - time.monotonic())),
                                downgraded)
        if st == cp_model.INFEASIBLE:
            kept.remove(t)
        elif st == cp_model.UNKNOWN:
            minimized = False
    conflicts = kept or \
        ["the rooms cannot tile any footprint this parti and lot allow, even with "
         "every declared requirement dropped — the programme is too large for the diagram"]
    return conflicts, minimized


def _snap_fpd(fpd):
    """Snap the footprint depth to the integer model grid, so the record's
    footprint and the solved coordinates are the same fact — without this a
    29.6 ft derivation becomes a 30 ft model and the drawn boundary lies by
    the difference."""
    out = dict(fpd)
    H = round(int(round(fpd["H"] * U)) / U, 2)
    out["H"] = H
    out["slack"] = (out["W"] * H) - fpd["need"]
    return out


def solve_cp(plan, parti=None, seed=7, time_limit_s=20.0, candidates=250):
    from ortools.sat.python import cp_model
    levels, prep = GEO.prep_rooms(plan)
    fpd0 = GEO.derive_footprint(plan, parti, prep)
    if "error" in fpd0:
        return {"error": fpd0["error"]}
    fpd0 = _snap_fpd(fpd0)
    if fpd0["H"] < 1 or fpd0["W"] < 1:
        # a sub-1-ft dimension rounds to an empty integer model, whose
        # "infeasible" would be a statement about the rounding, not the plan
        return {"error": f"footprint degenerate at {fpd0['W']} x {fpd0['H']} ft — "
                         f"too small to model on the 1 ft grid", "unsolved": True}
    ewalls = GEO.entrance_walls(plan)
    started = time.monotonic()

    attempts = []
    downgraded = set()      # pins PROVEN unable to co-hold: (level, room, wall) for a wall
                            # pin, (level, room) for a WP-11.7 shape pin. Split by arity
                            # wherever it is read, never by position.
    rank_notes = []         # what each round gave up, and at which rank
    seed_core = None

    def _feasibility(fpd, tag, budget):
        """Phase A: hard constraints only."""
        model, rooms, reqs = _build(plan, prep, fpd, ewalls, frozenset(downgraded),
                                    objective=False)
        _hint_heuristic(model, rooms, plan, parti, seed, candidates=40)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = budget
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = seed
        status = solver.Solve(model)
        attempts.append((tag, "A:" + solver.StatusName(status)))
        return status, solver, rooms, reqs

    def _reinstate(fpd, vals):
        """A solver core is SUFFICIENT, not minimal — the round loop downgrades
        every wall pin the core names, which over-softens (both walls of one
        room have ridden in one core). So: restore each downgraded pin ALONE,
        at the footprint actually being drawn. Feasible → the downgrade was
        never needed; the pin returns to being a hard fact. INFEASIBLE → that
        is the pin's own proof, at this footprint. UNKNOWN or budget out →
        the downgrade stays but is stated as carried, never as proven."""
        unproven = set()
        pending = sorted(downgraded)
        for i, key in enumerate(pending):
            remaining = time_limit_s - (time.monotonic() - started)
            if remaining < 2.5:
                unproven.update(k for k in pending[i:] if k in downgraded)
                break
            trial = frozenset(downgraded - {key})
            model, rooms, _reqs2 = _build(plan, prep, fpd, ewalls, trial,
                                          objective=False)
            _hint_values(model, rooms, vals)
            s = cp_model.CpSolver()
            s.parameters.max_time_in_seconds = min(2.0, remaining - 0.5)
            s.parameters.num_search_workers = 1
            s.parameters.random_seed = seed
            st = s.Solve(model)
            # `key` is (level, room, wall) for a wall pin and (level, room) for a WP-11.7
            # shape pin. This read `key[2]` unconditionally and would have raised IndexError
            # on the first shape downgrade -- inside the reinstatement pass, where nothing in
            # the traceback would have named the ladder.
            attempts.append((f"restore L{key[0]} {key[1]}"
                             + (f" {key[2]}" if len(key) > 2 else " (shape)"),
                             "R:" + s.StatusName(st)))
            if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                downgraded.discard(key)
                vals = _values(s, rooms)
            elif st != cp_model.INFEASIBLE:
                unproven.add(key)
        return vals, unproven

    def _rects_scored(fpd, vals):
        rects_by_level = {}
        for (lvl, rid), (x, y, w, h) in vals.items():
            rects_by_level.setdefault(lvl, {})[rid] = (x / U, y / U, w / U, h / U)
        # SORTED, so the ground is absorbed before the storey that must avoid its holes.
        for lvl in sorted(rects_by_level):
            rs = prep.get(lvl) or []
            fill = (fpd["W"] * fpd["H"]) / max(1.0, sum(r["_area"] for r in rs))
            caps = {r["id"]: max(1.20, fill * 1.22) * r["_area"] for r in rs}
            # WP-11.7: the SHAPE half of the same guarantee. A room whose proportion pin the
            # ladder released is left out -- the record says its band could not hold, and this
            # pass has nothing to preserve for it.
            ratios = {}
            for r in rs:
                if (lvl, r["id"]) in downgraded:
                    continue
                _c, _ = GEO.shape_band(r.get("type"))
                if _c:
                    ratios[r["id"]] = _c
            keepout = []
            if lvl == 1:
                below = rects_by_level.get(0) or {}
                for gr in (prep.get(0) or []):
                    v = gr.get("_void")
                    if isinstance(v, dict) and not v.get("roofed") and gr["id"] in below:
                        keepout.append(below[gr["id"]])
            # WP-11.11: the room's OWN element bounds the growth. `None` on a one-rectangle
            # house -- the whole shipped corpus -- so `_absorb` takes its `(0, 0, W, H)`
            # default and every absorbed rectangle is unchanged.
            _els = GEO.blocks_for(plan, fpd, prep, lvl)
            _eb = ({rid: (e["x"], e["y"], e["W"], e["H"]) for e in _els for rid in e["rooms"]}
                   if len(_els) > 1 else None)
            rects_by_level[lvl] = _absorb(rects_by_level[lvl], fpd["W"], fpd["H"],
                                          caps=caps, keepout=keepout, ratios=ratios,
                                          bounds=_eb)
        relax = _count_relaxations(rects_by_level, fpd["W"], fpd["H"],
                                   fpd["bay"], fpd["tol"])
        sc = _score(rects_by_level, prep, levels, plan, fpd, ewalls, relax)
        return rects_by_level, relax, sc

    def _polish(fpd, hint, budget, tag):
        model, rooms, reqs = _build(plan, prep, fpd, ewalls, frozenset(downgraded),
                                    objective=True)
        if hint == "heuristic":
            _hint_heuristic(model, rooms, plan, parti, seed, candidates=candidates)
        else:
            _hint_values(model, rooms, hint)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max(1.5, budget)
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = seed
        statusB = solver.Solve(model)
        attempts.append((tag, "B:" + solver.StatusName(statusB)))
        if statusB in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return _values(solver, rooms), solver.StatusName(statusB),                 solver.ObjectiveValue() / SCALE
        return None, solver.StatusName(statusB), None

    def _finish_feasible(fpd, valsA, statusA_name):
        """Phase B: polish with the weighted objective, hinted two ways — the
        full heuristic search (soft-optimized, hard-repairable) and phase A's
        own placement (hard-clean). Every hard-valid placement is scored with
        the heuristic's own scorers and the BEST one is returned; the status
        says which. On a fully timed-out polish, A stands, scored post-hoc."""
        unproven = set()
        if downgraded:
            # minimal, individually-proven downgrades at the footprint being
            # drawn — the round loop's cores over-blame (see _reinstate)
            valsA, unproven = _reinstate(fpd, valsA)
        remaining = time_limit_s - (time.monotonic() - started)
        candidates_out = [("hard-only phase A", valsA, statusA_name + " (hard-only)", None)]
        vals1, st1, obj1 = _polish(fpd, "heuristic", remaining * 0.55, "polish-h")
        if vals1 is not None:
            candidates_out.append(("polish from the heuristic hint", vals1, st1, obj1))
        remaining2 = time_limit_s - (time.monotonic() - started)
        if remaining2 > 4.0 and st1 != "OPTIMAL":
            vals2, st2, obj2 = _polish(fpd, valsA, remaining2, "polish-a")
            if vals2 is not None:
                candidates_out.append(("polish from phase A", vals2, st2, obj2))
        scored = []
        for label, vals, stname, obj in candidates_out:
            rects_by_level, relax, sc = _rects_scored(fpd, vals)
            scored.append((sc["score"], label, rects_by_level, relax, sc, stname, obj))
        scored.sort(key=lambda t: t[0])
        _, label, rects_by_level, relax, sc, stname, objective = scored[0]
        status_name = f"{stname} — kept {label} (best of {len(scored)} hard-valid placements)"
        best = {"ground": rects_by_level.get(0, {}), "upper": rects_by_level.get(1, {}),
                "relaxations": relax, **sc}
        _, _, reqs_notes = _build(plan, prep, fpd, ewalls, frozenset(downgraded),
                                  objective=False, unproven=frozenset(unproven))
        return {"best": best, "fpd": fpd, "levels": levels,
                "solver": {"engine": "cp-sat", "status": status_name,
                           "objective": objective,
                           "wall_time_s": round(time.monotonic() - started, 2),
                           "attempts": attempts,
                           # WP-6.3 corrected two words of this claim. It said "rooms at
                           # program size", and the SOLVE does prove that — but `_absorb`
                           # runs after it and grows rooms to `max(1.20, fill*1.22)` times
                           # their programme area, measured at 1.22x on both ground levels
                           # and 2.27x on one upper. The record shipped a proof of programme
                           # size on a drawing that no longer held it. The cap is not the
                           # defect (honest empty floor beats an inflated room, and the cap
                           # is what stops a 2.8 sf linen press reaching 8); the CLAIM was.
                           "hard": "no-overlap; containment; coverage; declared doors "
                                   "share wall enough for their own leaf and jambs; the "
                                   "entry on its front; rooms at or above program size "
                                   "(the post-solve absorb pass grows them into leftover "
                                   "floor, capped, so the drawn size is a floor and not an "
                                   "equality); declared exterior walls (until a set is "
                                   "proven unable to co-hold — then downgraded, stated)",
                           "note": "the compositional terms are constraints and "
                                   "weighted objectives here, not search preferences",
                           # WP-11.7: `downgraded` holds keys of more than one KIND now --
                           # a wall pin is (level, room, wall) and a shape pin is (level,
                           # room). This comprehension unpacked three names from every key
                           # and would have raised on the first shape downgrade, in the
                           # RESULT BUILDER, where the traceback names neither the ladder
                           # nor the pin. Split by arity, and both reported.
                           "downgraded_wall_pins": sorted(
                               f"L{k[0]} {k[1]} {k[2]}" for k in downgraded if len(k) == 3),
                           "downgraded_shape_pins": sorted(
                               f"L{k[0]} {k[1]}" for k in downgraded if len(k) == 2),
                           "downgrade_rounds": list(rank_notes),
                           "refinements": sorted(set(reqs_notes.notes))}}

    # Round loop at the natural footprint: wall pins are hard until PROVEN
    # unable to co-hold; exactly those pins downgrade, stated. Doors, sizes,
    # the entrance and capacity never downgrade — they are what infeasibility
    # is FOR (25 Aug rulings, contested-corners read as a principle).
    for rnd in range(4):
        budget = min(6.0, max(2.0, (time_limit_s - (time.monotonic() - started)) * 0.5))
        status, solver, rooms, reqs = _feasibility(fpd0, f"{fpd0['bays']}b r{rnd}", budget)
        if status == cp_model.UNKNOWN:
            # the quick pass could not decide — spend the WHOLE remaining budget
            # before giving up (bailing at the 6s scout cap was a measured
            # mistake, and a 0.6x retry starved the 25-room double-pile too)
            budget = max(4.0, time_limit_s - (time.monotonic() - started))
            status, solver, rooms, reqs = _feasibility(fpd0, f"{fpd0['bays']}b r{rnd}+", budget)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return _finish_feasible(fpd0, _values(solver, rooms),
                                    solver.StatusName(status))
        if status == cp_model.UNKNOWN:
            return {"unsolved": True, "status": solver.StatusName(status),
                    "attempts": attempts}
        if status != cp_model.INFEASIBLE:
            # MODEL_INVALID or anything else unexpected: an empty core from it
            # would masquerade as a proof — refuse, stated, instead
            return {"unsolved": True, "status": solver.StatusName(status),
                    "attempts": attempts}
        idx = set(solver.SufficientAssumptionsForInfeasibility())
        core = [(t, k, key) for lit, t, k, key in reqs.lits if lit.Index() in idx]
        seed_core = [t for t, _k, _key in core]
        # THE LADDER IS RANKED (WP-11.7), and it was a single kind until this package.
        # It read `[key for _t, k, key in core if k == "wall" and key]` -- so a wall pin was
        # the only downgradable fact, and every requirement added since would either have been
        # un-downgradable (and taken the whole placement to INFEASIBLE) or would have had to be
        # soft, which on this plan means invisible: `_finish_feasible` keeps the hard-only
        # phase A placement whenever the polish times out, and the objective never runs.
        #
        # RANK IS AUTHORITY, LOWEST FIRST, AND THE ORDER IS THE POINT. An authored exterior
        # wall is the author's own statement about the house; a shape pin is the corpus's rule
        # about the room TYPE; an axis pin is inferred from the parti. So a round gives up the
        # inferred fact before the authored one, and OQ 95's standing requirement -- that an
        # authored wall can never lose to an inferred pin -- holds by construction rather than
        # by everything else being soft.
        #
        # Sizes, doors, the entrance and capacity are still ABSENT from this ladder and still
        # never downgrade: they are what infeasibility is for (the 25 Aug rulings, unchanged).
        # A SOLVER CORE IS SUFFICIENT AND NOT MINIMAL, WHICH IS WHY THE SECOND CLAUSE EXISTS.
        # Measured on `plans/tidewater-georgian-careful.json` the first time the shape pins ran:
        # the core came back as three literals -- the Back Hall's declared N wall, its declared
        # S wall, and its 7 x 16 ft programme -- and NO shape literal, although the shape pin was
        # the new fact that had just made the model infeasible. (A room declaring an opposite
        # pair must span the 40 ft depth; at 112 sf that is 2.8 ft wide, which is 14 to 1 against
        # a band of 5.) Ranking on the kinds the core happens to NAME would therefore have given
        # up two authored walls to save an inferred shape pin -- the exact inversion OQ 95
        # forbids, arrived at by accident.
        #
        # So: prefer the lowest-ranked kind the core names; and where the core names no pin of
        # that kind, fall back to the lowest-ranked LIVE pins belonging to the ROOMS the core
        # names. The conflict always names rooms, and the room is the unit an author reads.
        # A ROUND RELEASES THE WHOLE OF THE LOWEST-RANKED LIVE KIND, NOT THE PINS THE CORE
        # HAPPENS TO NAME, and that is a measurement rather than a shortcut.
        #
        # The narrow version -- downgrade exactly the cored pins -- was written first and swept.
        # On `plans/tidewater-georgian-careful.json` with the shape band live it needs EIGHT
        # rounds, and the intermediate states (some walls released, the band still held) are the
        # expensive ones: at a 6 s per-round cap round 2 comes back UNKNOWN, so the ladder never
        # converges inside any budget the bench can spend. Releasing the rank whole reaches the
        # same end state in ONE round, and with the heuristic hint that round is OPTIMAL in
        # 12.9 s against 26.1 s unhinted.
        #
        # It over-releases, and the file already has the answer to that: `_reinstate` restores
        # each downgraded pin ALONE at the footprint actually being drawn and keeps the ones
        # that hold, marking the rest carried-not-proven. Its own docstring says why -- "a
        # solver core is SUFFICIENT, not minimal" -- and that reasoning is the same one round
        # larger here. What a round must never do is release a kind that outranks one still
        # live, and it cannot: the loop takes the first kind in `_RANK` with a live pin.
        _downgradable = None
        for _kind in _RANK:
            live = [key for _lit, _t, k, key in reqs.lits
                    if k == _kind and key and key not in downgraded]
            if live:
                _named = sum(1 for _t, k, key in core if k == _kind and key)
                _downgradable = (_kind, live, _named)
                break
        if not _downgradable:
            break
        _kind, _keys, _named = _downgradable
        rank_notes.append(
            f"round {rnd}: released all {len(_keys)} live {_kind} pin(s) — the lowest-ranked "
            f"kind still held; the conflict core named {_named} of them, and the rest are "
            f"offered back one at a time by the reinstatement pass")
        downgraded.update(_keys)

    # capacity may still be the blocker: grow a bay before blaming a requirement
    for bays in range(fpd0["bays"] + 1, fpd0["growth_ceiling"] + 1):
        fpd = _snap_fpd(_fpd_at(fpd0, bays))
        budget = max(2.0, time_limit_s - (time.monotonic() - started))
        status, solver, rooms, reqs = _feasibility(fpd, f"{bays}b", budget)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return _finish_feasible(fpd, _values(solver, rooms),
                                    solver.StatusName(status))
        if status == cp_model.UNKNOWN:
            return {"unsolved": True, "status": solver.StatusName(status),
                    "attempts": attempts}

    conflicts, minimized = _extract_conflicts(plan, prep, fpd0, ewalls,
                                              seed_core=seed_core,
                                              downgraded=frozenset(downgraded))
    if conflicts is None:
        return {"unsolved": True, "status": "INFEASIBLE-but-core-extraction-failed",
                "attempts": attempts}
    note = (f"CP-SAT proved these requirements cannot all hold together at any "
            f"footprint this parti and lot allow ({fpd0['bays']}–"
            f"{fpd0['growth_ceiling']} bays tried"
            + (f", with {len(downgraded)} already-downgraded wall pin(s)" if downgraded else "")
            + "). Drop or change one, or change the diagram.")
    if not minimized:
        note += (" The set is a sufficient core, not fully minimized — the "
                 "minimization budget ran out; some listed requirements may be "
                 "removable individually.")
    return {"infeasible": {
        "proven": True,
        "conflicts": conflicts,
        "minimized": minimized,
        "downgraded_wall_pins": sorted(f"L{k[0]} {k[1]} {k[2]}" for k in downgraded
                                       if len(k) == 3),
        "downgraded_shape_pins": sorted(f"L{k[0]} {k[1]}" for k in downgraded if len(k) == 2),
        "note": note,
        "attempts": attempts}}


def hard_fact_violations(plan, out, extra_downgraded=None):
    """Count the hard facts a PLACEMENT violates: same-level declared doors with
    no drawable shared wall (render_plan's own 3.2 ft test), non-protruding
    declared walls unreached, the entry off its front. The heuristic trades
    these away at 14 points each; the CP engine cannot — so when the hill-climb
    'outscores' the constrained optimum, this is the number that says what the
    cheaper score actually bought. `out` is a solved plan record. Wall pins the
    solver PROVED unable to co-hold (out's own downgraded_wall_pins, stated
    per the ruling) are not violations — they are the model's stated reading
    of exposure-as-massing, and both engines leave them unreached alike.
    `extra_downgraded` takes another record's downgraded_wall_pins list so two
    engines' placements of the SAME plan are judged against the SAME facts —
    a heuristic record carries no downgrade list of its own, and charging it
    for pins the CP engine PROVED impossible would rig the comparison."""
    gr = out.get("geometry_report") or {}
    pin_strings = list(((gr.get("solver") or {}).get("downgraded_wall_pins") or []))
    # the proven-infeasible path carries its pins under infeasible, not solver
    pin_strings += list(((gr.get("infeasible") or {}).get("downgraded_wall_pins") or []))
    pin_strings += list(extra_downgraded or [])
    downgraded_keys = set()
    for s in pin_strings:
        # "L{level} {room-id} {wall}" — split from BOTH ends, because the
        # schema puts no pattern on room ids and an ingested id may hold spaces
        parts = s.split(" ")
        if len(parts) >= 3 and parts[0].startswith("L"):
            downgraded_keys.add((int(parts[0][1:]), " ".join(parts[1:-1]), parts[-1]))
    levels, prep = GEO.prep_rooms(plan)
    W = out["footprint"]["width_ft"]; H = out["footprint"]["depth_ft"]
    ewalls = GEO.entrance_walls(plan)
    rects_by_level = {}
    for lv in out["levels"]:
        idx = lv.get("index", 0)
        for r in lv["rooms"]:
            g = r.get("geometry")
            if g:
                rects_by_level.setdefault(idx, {})[r["id"]] = (
                    g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"])
    v = 0
    for lvl, rs in ((0, prep.get(0) or []), (1, prep.get(1) or [])):
        rects = rects_by_level.get(lvl, {})
        contested = _contested_corners(rs)
        ids = {r["id"] for r in rs}
        maxside = {r["id"]: max(r.get("width_ft") or 10, r.get("length_ft") or 12)
                   for r in rs}
        seen = set()
        for r in rs:
            if r["id"] not in rects:
                continue
            x, y, w, h = rects[r["id"]]
            if not (_protruding(r) or r["id"] in contested):
                for wl in (r.get("exterior_walls") or []):
                    if (lvl, r["id"], wl) in downgraded_keys:
                        continue
                    at = {"S": y <= 0.6, "N": y + h >= H - 0.6,
                          "W": x <= 0.6, "E": x + w >= W - 0.6}.get(wl)
                    # not `is False`: an np.bool_ False from upstream floats
                    # would silently uncount (the ezdxf lesson, WP-5.1)
                    if at is not None and not at:
                        v += 1
            for d in (r.get("doors") or []):
                to = d["to"]
                if to == "exterior" or to not in ids or to not in rects:
                    continue
                key = tuple(sorted((r["id"], to)))
                if key in seen:
                    continue
                seen.add(key)
                ox, oy, ow, oh = rects[to]
                # THE SAME RULE THE MODEL STATED, from the same function. This was a second
                # copy of the old expression, and a second copy of a rule is how an arbiter
                # comes to contradict the solver it arbitrates: change one and this one
                # convicts placements the model proved legal. The 0.05 slack is kept —
                # it is a float-comparison tolerance against integers the model rounded.
                ovr = _door_overlap(d, {"maxside": maxside[r["id"]]},
                                    {"maxside": maxside[to]}) - 0.05
                shared_v = (abs(x + w - ox) <= 0.4 or abs(ox + ow - x) <= 0.4) and                     min(y + h, oy + oh) - max(y, oy) >= ovr
                shared_h = (abs(y + h - oy) <= 0.4 or abs(oy + oh - y) <= 0.4) and                     min(x + w, ox + ow) - max(x, ox) >= ovr
                if not (shared_v or shared_h):
                    v += 1
        if lvl == 0 and ewalls:
            for r in rs:
                if _cls(r["type"]) != "threshold" or r["id"] not in rects:
                    continue
                if not any(d.get("to") == "exterior" for d in (r.get("doors") or [])):
                    continue
                x, y, w, h = rects[r["id"]]
                on = any({"S": y <= 0.6, "N": y + h >= H - 0.6,
                          "W": x <= 0.6, "E": x + w >= W - 0.6}.get(wl, False)
                         for wl in ewalls)
                if not on:
                    v += 1
    return v


# ------------------------------------------------------------------- selftest

def _feasible_fixture():
    """A small plan whose declared facts CAN all hold: unique corners, a real
    entry on the entrance front, satisfiable doors."""
    return {
        "id": "cp-selftest-feasible", "name": "CP selftest, feasible",
        "style": "georgian-colonial-american",
        "context": {"entrance_faces": "S"},
        "levels": [{"id": "ground", "index": 0, "floor_to_ceiling_ft": 9, "rooms": [
            {"id": "porch", "type": "entry-porch", "width_ft": 6, "length_ft": 10,
             "exterior_walls": ["S"], "doors": [{"to": "hall"}, {"to": "exterior"}]},
            {"id": "hall", "type": "entrance-hall", "width_ft": 10, "length_ft": 14,
             "doors": [{"to": "porch"}, {"to": "parlor"}, {"to": "kitchen"}]},
            {"id": "parlor", "type": "parlor", "width_ft": 14, "length_ft": 16,
             "exterior_walls": ["S", "W"], "doors": [{"to": "hall"}]},
            {"id": "kitchen", "type": "kitchen", "width_ft": 12, "length_ft": 14,
             "exterior_walls": ["N"], "doors": [{"to": "hall"}]},
        ]}]}


def _multi_element_fixture():
    """Three massing elements -- a main block, a hyphen, a dependency -- whose door graph is
    consistent with being three masses: every cross-element door goes THROUGH the hyphen, which
    is the only room that touches both of its neighbours.

    WP-11.11. This is the positive half of the acceptance surface: `_k5_fixture` proves the
    model still refuses what cannot be built, and this proves it can now build what can. The
    hand-tagged `tidewater-georgian-careful` is deliberately NOT this fixture -- that record
    declares a door between a main-block dining room and a dependency butler's pantry, so CP
    proves it unbuildable, which is a finding about the record and a bad acceptance test."""
    return {
        "id": "cp-selftest-multi-element", "name": "CP selftest, three massing elements",
        "style": "georgian-colonial-american",
        "context": {"entrance_faces": "S"},
        "levels": [{"id": "ground", "index": 0, "floor_to_ceiling_ft": 9, "rooms": [
            {"id": "porch", "type": "entry-porch", "width_ft": 6, "length_ft": 10,
             "exterior_walls": ["S"], "doors": [{"to": "hall"}, {"to": "exterior"}]},
            {"id": "hall", "type": "entrance-hall", "width_ft": 10, "length_ft": 14,
             "exterior_walls": ["W"],
             "doors": [{"to": "porch"}, {"to": "parlor"}, {"to": "link"}]},
            {"id": "parlor", "type": "parlor", "width_ft": 14, "length_ft": 16,
             "exterior_walls": ["S", "E"], "doors": [{"to": "hall"}]},
            {"id": "link", "type": "gallery-corridor", "width_ft": 8, "length_ft": 12,
             "block": "w-dep", "hyphen": True, "exterior_walls": ["N", "S"],
             "doors": [{"to": "hall"}, {"to": "kitchen"}]},
            {"id": "kitchen", "type": "kitchen", "width_ft": 14, "length_ft": 16,
             "block": "w-dep", "exterior_walls": ["N", "S", "W"],
             "doors": [{"to": "link"}, {"to": "pantry"}]},
            {"id": "pantry", "type": "pantry", "width_ft": 6, "length_ft": 10,
             "block": "w-dep", "exterior_walls": ["W"], "doors": [{"to": "kitchen"}]},
        ]}]}


def _k5_fixture():
    """Five rooms, every pair sharing a door: the door graph is K5, which is
    non-planar — no arrangement of touching rectangles can realize it. A TRUE
    conflict on the one axis that never downgrades (doors are topology)."""
    rooms = []
    ids = [f"r{i}" for i in range(5)]
    for i, rid in enumerate(ids):
        rooms.append({"id": rid, "type": "parlor", "width_ft": 12, "length_ft": 12,
                      "doors": [{"to": o} for o in ids if o != rid]})
    return {"id": "cp-selftest-k5", "name": "CP selftest, K5 doors",
            "style": "georgian-colonial-american",
            "levels": [{"id": "ground", "index": 0, "floor_to_ceiling_ft": 9,
                        "rooms": rooms}]}


def selftest():
    """The solver's acceptance surface on fast fixtures (the full best-of-800
    benchmark lives in tests/test_solver.py). Exit 3 (COULD NOT EVALUATE)
    without OR-Tools — check_all reports that as N/EV, never as a pass."""
    try:
        import ortools  # noqa: F401
    except ImportError:
        print("COULD NOT EVALUATE: the ortools package is not installed (pip install "
              "ortools). The CP-SAT solver was not exercised — this is not a pass; "
              "geometry.solve() falls back to the hill-climb and says so.")
        return 3

    failures = 0

    res = solve_cp(_feasible_fixture(), time_limit_s=25)
    if "best" not in res:
        print(f"  FAIL feasible fixture did not solve: {str(res)[:200]}")
        failures += 1
    else:
        g = res["best"]["ground"]
        W, H = res["fpd"]["W"], res["fpd"]["H"]
        probs = []
        px, py, pw, ph = g["porch"]
        if py > 0.01:
            probs.append("the entry porch is off the S front")
        kx, ky, kw, kh = g["kitchen"]
        if abs((ky + kh) - H) > 0.01:
            probs.append("kitchen is off its declared N wall")
        hx, hy, hw, hh = g["hall"]
        touching = (abs(px + pw - hx) < 0.01 or abs(hx + hw - px) < 0.01
                    or abs(py + ph - hy) < 0.01 or abs(hy + hh - py) < 0.01)
        if not touching:
            probs.append("porch and hall do not share a wall despite their door")
        if probs:
            print("  FAIL feasible fixture: " + "; ".join(probs))
            failures += 1
        else:
            print(f"  OK   feasible fixture: solved, entry on the front, doors touch "
                  f"({res['solver']['status']}, {res['solver']['wall_time_s']}s)")

    res = solve_cp(_k5_fixture(), time_limit_s=25)
    if not res.get("infeasible", {}).get("proven"):
        print(f"  FAIL K5 fixture was not proven infeasible: {str(res)[:200]}")
        failures += 1
    else:
        conflicts = res["infeasible"]["conflicts"]
        if not any("share a door" in c for c in conflicts):
            print(f"  FAIL K5 conflicts do not name the doors: {conflicts[:3]}")
            failures += 1
        else:
            print(f"  OK   K5 fixture: proven infeasible, {len(conflicts)} door "
                  f"conflict(s) named (a non-planar door graph cannot be a floor plan)")

    # WP-11.11 -- the positive half: a plan with three massing elements is PLACED, and every
    # room is inside its own element rather than flattened into the main block.
    res = solve_cp(_multi_element_fixture(), time_limit_s=25)
    if "best" not in res:
        print(f"  FAIL multi-element fixture did not solve: {str(res)[:220]}")
        failures += 1
    else:
        # through `_mod` and therefore through modcache -- CLAUDE.md's standing trap, with
        # `tests/test_modcache.py` behind it, and it caught this line in the full suite
        plan = _multi_element_fixture()
        levels, prep = GEO.prep_rooms(plan)
        els = GEO.blocks_for(plan, res["fpd"], prep, 0)
        owner = {rid: e for e in els for rid in e["rooms"]}
        probs = []
        if len(els) != 3:
            probs.append(f"the fixture makes {len(els)} element(s), not 3")
        worst = 0.0
        for rid, (x, y, w, h) in res["best"]["ground"].items():
            e = owner.get(rid)
            if not e:
                probs.append(f"{rid} belongs to no element")
                continue
            worst = max(worst, e["x"] - x, e["y"] - y,
                        (x + w) - (e["x"] + e["W"]), (y + h) - (e["y"] + e["H"]))
        if worst > 0.01:
            probs.append(f"a room is drawn {worst:.2f} ft outside its own element")
        if probs:
            print("  FAIL multi-element fixture: " + "; ".join(probs))
            failures += 1
        else:
            print(f"  OK   multi-element fixture: 3 elements placed, every room inside its own "
                  f"({res['solver']['status']}, {res['solver']['wall_time_s']}s)")

    if failures:
        print(f"\n{failures} selftest failure(s).")
        return 1
    print("\ngeometry_cp selftest: the solver proves what it places and names what it refuses.")
    return 0


if __name__ == "__main__":
    import sys as _sys
    if len(_sys.argv) > 1 and _sys.argv[1] == "selftest":
        _sys.exit(selftest())
    print(__doc__.split("\n\n")[0])
    print("Run 'python3 build/geometry_cp.py selftest', or use geometry.solve().")
