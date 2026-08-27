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


def _build(plan, prep, fpd, ewalls, downgraded=frozenset(), objective=True,
           unproven=frozenset()):
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    reqs = _Reqs(m)
    Wi, Hi = int(round(fpd["W"] * U)), int(round(fpd["H"] * U))
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
            x = m.NewIntVar(0, Wi, f"x{lvl}_{r['id']}")
            y = m.NewIntVar(0, Hi, f"y{lvl}_{r['id']}")
            w = m.NewIntVar(lo_side, Wi, f"w{lvl}_{r['id']}")
            h = m.NewIntVar(lo_side, Hi, f"h{lvl}_{r['id']}")
            a = m.NewIntVar(0, Wi * Hi, f"a{lvl}_{r['id']}")
            m.AddMultiplicationEquality(a, [w, h])
            # the room at roughly its program size — ONE requirement per room,
            # so a conflict names the room, not an anonymous inequality
            areaU = r["_area"] * U * U
            pr = reqs.lit(f"{r.get('name') or r['id']} needs roughly its program size "
                          f"({dw:g} x {dl:g} ft, within this layer's tolerance)",
                          kind="size")
            m.Add(a >= int(0.88 * areaU)).OnlyEnforceIf(pr)
            m.Add(a <= int(max(1.20, fill * 1.22) * areaU)).OnlyEnforceIf(pr)
            m.Add(x + w <= Wi)
            m.Add(y + h <= Hi)
            if objective:
                # mirror level_score's own terms, term for term: area error
                # (10 x |got-want|/want) and aspect sanity (6 per ratio point
                # past 2.6, linearized against the short side)
                target = int(round(min(max(1.20, fill * 1.10), 1.22) * areaU))
                dev = m.NewIntVar(0, Wi * Hi, "")
                diff = m.NewIntVar(-Wi * Hi, Wi * Hi, "")
                m.Add(diff == a - target)
                m.AddAbsEquality(dev, diff)
                penalties.append((dev, max(1, int(round(10 * SCALE / max(areaU, 1))))))
                mx = m.NewIntVar(0, max(Wi, Hi), "")
                mn = m.NewIntVar(0, max(Wi, Hi), "")
                m.AddMaxEquality(mx, [w, h])
                m.AddMinEquality(mn, [w, h])
                ov10 = m.NewIntVar(0, 10 * max(Wi, Hi), "")
                m.Add(ov10 >= 10 * mx - 26 * mn)
                penalties.append((ov10, 6))
            xiv.append(m.NewIntervalVar(x, w, m.NewIntVar(0, Wi, ""), f"xi{lvl}_{r['id']}"))
            yiv.append(m.NewIntervalVar(y, h, m.NewIntVar(0, Hi, ""), f"yi{lvl}_{r['id']}"))
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
        else:
            m.Add(upper_area >= int(COVERAGE * Wi * Hi))

        # ---- declared exterior walls
        contested = _contested_corners(rs)
        for r in rs:
            v = rooms[(lvl, r["id"])]
            walls = list(r.get("exterior_walls") or [])
            pins = {"S": v["y"] == 0, "N": v["y"] + v["h"] == Hi,
                    "W": v["x"] == 0, "E": v["x"] + v["w"] == Wi}
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

        # ---- doors: declared topology must be geometrically real
        idx = {r["id"]: r for r in rs}
        seen = set()
        for r in rs:
            v1 = rooms[(lvl, r["id"])]
            for d in (r.get("doors") or []):
                to = d["to"]
                if to == "exterior":
                    lit = reqs.lit(f"{r.get('name') or r['id']} has a door to the exterior "
                                   f"— it must reach the building envelope", kind="door")
                    onb = []
                    for cond in (v1["y"] == 0, v1["y"] + v1["h"] == Hi,
                                 v1["x"] == 0, v1["x"] + v1["w"] == Wi):
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
                for axis, span in (("x", Wi), ("y", Hi)):
                    edges = (v["x"], (v["x"] + v["w"])) if axis == "x" \
                        else (v["y"], (v["y"] + v["h"]))
                    for e in edges:
                        ev = m.NewIntVar(0, span, "")
                        m.Add(ev == e)
                        emod = m.NewIntVar(0, bayU - 1, "")
                        m.AddModuloEquality(emod, ev, bayU)
                        d = m.NewIntVar(0, bayU, "")
                        m.AddMinEquality(d, [emod, bayU - emod])
                        if axis == "y":
                            # the top boundary Hi is a legitimate line even off-module
                            dH = m.NewIntVar(0, span, "")
                            dfH = m.NewIntVar(-span, span, "")
                            m.Add(dfH == ev - Hi)
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
        h = GEO.solve_heuristic(copy.deepcopy(plan), parti, candidates=candidates, seed=seed)
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


def _absorb(rects, W, H, caps=None, keepout=()):
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
    does, so the proof survives into the drawing."""
    ids = list(rects)
    caps = caps or {}
    if keepout:
        rects = dict(rects)
        for i, ko in enumerate(keepout):
            rects[f"\0keepout{i}"] = tuple(ko)
    for _ in range(8):
        moved = False
        for rid in ids:
            x, y, w, h = rects[rid]
            cap = caps.get(rid, float("inf"))
            lim = W
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and oy < y + h - 0.01 and y < oy + oh - 0.01 and ox >= x + w - 0.01:
                    lim = min(lim, ox)
            if lim - (x + w) > 0.01:
                nw = min(lim - x, max(w, cap / max(h, 0.01)))
                if nw - w > 0.01:
                    w = nw; moved = True
            lim = H
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and ox < x + w - 0.01 and x < ox + ow - 0.01 and oy >= y + h - 0.01:
                    lim = min(lim, oy)
            if lim - (y + h) > 0.01:
                nh = min(lim - y, max(h, cap / max(w, 0.01)))
                if nh - h > 0.01:
                    h = nh; moved = True
            lim = 0.0
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and oy < y + h - 0.01 and y < oy + oh - 0.01 and ox + ow <= x + 0.01:
                    lim = max(lim, ox + ow)
            if x - lim > 0.01:
                nw = min(w + (x - lim), max(w, cap / max(h, 0.01)))
                if nw - w > 0.01:
                    x -= nw - w; w = nw; moved = True
            lim = 0.0
            for o, (ox, oy, ow, oh) in rects.items():
                if o != rid and ox < x + w - 0.01 and x < ox + ow - 0.01 and oy + oh <= y + 0.01:
                    lim = max(lim, oy + oh)
            if y - lim > 0.01:
                nh = min(h + (y - lim), max(h, cap / max(w, 0.01)))
                if nh - h > 0.01:
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
    tot = sg + su + sv + 1.5 * len(relax)
    return {"score": round(tot, 1), "sg": round(sg, 1), "su": round(su, 1),
            "sv": round(sv, 1), "vnotes": vnotes}


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
    downgraded = set()      # (level, room_id, wall) pins PROVEN unable to co-hold
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
            attempts.append((f"restore L{key[0]} {key[1]} {key[2]}",
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
            keepout = []
            if lvl == 1:
                below = rects_by_level.get(0) or {}
                for gr in (prep.get(0) or []):
                    v = gr.get("_void")
                    if isinstance(v, dict) and not v.get("roofed") and gr["id"] in below:
                        keepout.append(below[gr["id"]])
            rects_by_level[lvl] = _absorb(rects_by_level[lvl], fpd["W"], fpd["H"],
                                          caps=caps, keepout=keepout)
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
                           "downgraded_wall_pins": sorted(
                               f"L{l} {r} {w}" for l, r, w in downgraded),
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
        wall_keys = [key for _t, k, key in core if k == "wall" and key]
        if not wall_keys:
            break
        downgraded.update(wall_keys)

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
        "downgraded_wall_pins": sorted(f"L{l} {r} {w}" for l, r, w in downgraded),
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
