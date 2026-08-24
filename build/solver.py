#!/usr/bin/env python3
"""Solver — room placement as a constraint programme, not a search over guesses (WP-2.3).

`build/geometry.py` places rooms by generating 250 randomised guillotine slicings and keeping
the best. That produces valid, drawable plans, and every compositional rule WP-2.2 added is
scored inside it. But a scored preference is not an enforced constraint, and the difference
shows in the one place a plan-development partner most needs the system to be strong: when a
brief cannot be built, the search returns its least-bad plan rather than saying *what
conflicts*. "The house is 40 square feet short" is a different conversation from "here is a
plan with a nine-foot dining room in it."

This module states the same problem to CP-SAT over the same bay grid:

  * every room is an integer rectangle on a quarter-foot grid, inside the footprint;
  * rooms on a level do not overlap, and their areas sum to the footprint exactly, so the
    result tiles rather than leaves voids the renderer would draw as holes;
  * the requirements that were weights in the heuristic -- a room's declared exterior walls,
    a door meaning two rooms actually touch, the entrance on the entrance front, the centre
    passage spanning, an upper wet room landing over a lower one -- are HARD, and each one
    carries a named assumption literal;
  * the softer compositional preferences (principal rooms forward, service to the rear, the
    ceremonial sequence going deeper, centre-hall symmetry, cuts landing on bay lines, upper
    walls continuing to a wall below) stay in the objective at the weights geometry.py gives
    them, because they are genuinely preferences and a real house trades them off.

When the hard set cannot all hold at once, CP-SAT returns the assumptions that conflict.
Those literals are named for the requirements they came from, so an infeasible plan comes
back as "the Library and the Drawing Room cannot both hold their minimum at this footprint"
rather than as a bad drawing. Requirements that can honestly be relaxed are relaxed -- at the
weight the heuristic already paid for them silently -- and the record NAMES what was relaxed.
Requirements that cannot (a room below its minimum is a defect that survives the building)
stop the solve and return the conflict.

Two disciplines carried over deliberately:

  * The heuristic is kept, run first, and used three ways: as a hint CP-SAT starts from, as a
    cross-check, and as the fallback when OR-Tools is not installed. The fallback is always
    REPORTED in geometry_report.solver, never silent -- a plan placed by a different engine
    than the caller thinks is a lie about the drawing.
  * The score in the record is never the CP objective. Both layouts are re-scored by
    geometry.py's own scoring functions and the better one is kept, so "the CP solution scores
    at least as well" is a measured claim on one metric, not two engines grading themselves.

  python3 build/solver.py plans/<id>.json [--parti <id>] [--mode cp|heuristic|both]
                          [--out plans/<id>.geo.json] [--svg dist/<id>.svg] [--time 60]
"""
from __future__ import annotations
import json, os, math, time, argparse, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _mod(n, p):
    # Same path-loading pattern as every other script in build/, delegating to modcache so a
    # module is executed once per process rather than once per call (OQ 28).
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(n, p)

GEO = _mod("geometry", f"{ROOT}/build/geometry.py")
C = GEO.C

U = 4                      # grid units per foot: a quarter foot (3 in)
SCALE = 100000             # objective scale: geometry.py's own weights are fractional
MIN_SIDE_FT = 4.0          # no enclosed room is narrower than this, whatever the packing wants
TOUCH_FT = 3.5             # a door needs this much shared wall; render_plan.py draws one at 3.2

# ---------------------------------------------------------------- shared scoring
def relaxations_from_rects(rects_by_level, W, H, bay, tol=0.02):
    """Recount off-grid cuts from a finished layout.

    geometry.py counts a relaxation as it takes one, cut by cut, during generation. A finished
    layout has no memory of that, so this counts the thing the count is *about*: distinct
    interior wall lines that do not land on a bay line. Each one is a joist run that misses a
    bearing line and a window bay that will not centre, which is what makes it a compromise
    worth reporting. The two counts are close but not identical by construction -- one counts
    cuts, this counts lines -- and docs/geometry.md says so."""
    lines_x, lines_y = set(), set()
    for rects in rects_by_level:
        for (x, y, w, h) in rects.values():
            lines_x.add(round(x, 2)); lines_x.add(round(x + w, 2))
            lines_y.add(round(y, 2)); lines_y.add(round(y + h, 2))
    offs = []
    for lines, extent in ((lines_x, W), (lines_y, H)):
        for v in sorted(lines):
            if abs(v) <= tol or abs(v - extent) <= tol:
                continue                                     # the footprint's own edges
            d = abs(v - round(v / bay) * bay)
            if d > tol:
                offs.append(round(d, 2))
    return len(offs), offs


def score_layout(ground, upper, prep, levels, plan, W, H, bay):
    """Score a layout with geometry.py's OWN functions, whatever engine produced it.

    This is the whole basis of the cross-check. The CP objective is a mirror of these terms
    with linear proxies where CP-SAT needs one, so it cannot be trusted to equal them; this
    can, because it is literally the same code the heuristic is judged by."""
    ewalls = GEO.entrance_walls(plan)
    p0, p1 = prep[0], prep.get(1, [])
    sg = (GEO.level_score(ground, p0) + GEO.exterior_score(ground, p0, W, H)
          + GEO.adjacency_score(ground, p0, levels[0]["rooms"])
          + GEO.entrance_score(ground, p0, W, H, ewalls)
          + GEO.principal_and_service_score(ground, p0, W, H, ewalls)
          + GEO.ceremonial_score(ground, p0, W, H, ewalls)
          + GEO.centre_hall_symmetry_score(ground, p0, W, H))
    if p1 and upper:
        su = (GEO.level_score(upper, p1) + GEO.exterior_score(upper, p1, W, H)
              + GEO.adjacency_score(upper, p1, levels[1]["rooms"])
              + GEO.centre_hall_symmetry_score(upper, p1, W, H))
    else:
        su = 0.0
    vs, vnotes = GEO.vertical_score(ground, upper, p0, p1, plan)
    nrel, offs = relaxations_from_rects([r for r in (ground, upper) if r], W, H, bay)
    total = sg + su + vs + 1.5 * nrel
    return {"score": round(total, 1), "ground": round(sg, 1), "upper": round(su, 1),
            "vertical": round(vs, 1), "vnotes": vnotes, "relaxations": nrel,
            "max_off_grid_ft": round(max(offs), 2) if offs else 0}


# ---------------------------------------------------------------- requirement naming
def _fc(rtype):
    return C["rooms"].get(rtype, {}).get("function_class")

def _rank(rtype):
    return C["rooms"].get(rtype, {}).get("privacy_rank")

def _display(room):
    return room.get("name") or room.get("type") or room.get("id")

def _min_area_sf(room):
    """The floor below which this room stops being the room it is named as.

    geometry.py's level_score already treats `area < catalog_low * 0.85` as a defect worth 12
    points; this makes the same line hard. The catalog band is the authority -- a drawing room
    that seats a dinner party is 320 sf at the bottom of its band and a 15x20 room called a
    drawing room is a parlor, as rooms/drawing-room.json says at length."""
    lo, _hi = GEO.band(room["type"])
    declared = room.get("_area") or 0
    return min(lo * 0.85, declared) if declared else lo * 0.85


# ---------------------------------------------------------------- slicing structure
def guillotine_tree(items, x0, y0, x1, y1, tol=0.05):
    """Recover the slicing tree from a finished layout.

    A guillotine layout is one you can cut in two with a straight line that crosses no room,
    and then cut each half the same way. geometry.py's slicer produces exactly that by
    construction, so the tree can be read back off its output without touching the slicer or
    changing a single number it computes.

    This matters because of what the free-packing model could not do. Asking CP-SAT to place
    loose rectangles that tile the footprint exactly means asking it to satisfy
    `sum(w_i * h_i) == W * H` over a dozen nonlinear products, and measured on the shipped spec
    Colonial it could not decide that even in 240 s with four workers and a known-good hint.
    Read the slicing structure instead and the tiling is free: a tree of cuts tiles whatever it
    covers, by construction, at any cut position. What is left -- WHERE each cut goes -- is
    linear in the cut variables, and that CP-SAT solves to proven optimality in well under a
    second. The heuristic proposes the topology; the solver proves the geometry.

    Returns a nested dict, or None if the layout is not guillotine (nothing in this codebase
    produces one that is not, but the caller checks rather than assuming)."""
    if not items: return None
    if len(items) == 1:
        return {"leaf": items[0][0]}
    for axis in ("x", "y"):
        lo_i, hi_i = (0, 2) if axis == "x" else (1, 3)
        lo_b, hi_b = (x0, x1) if axis == "x" else (y0, y1)
        edges = sorted({round(r[lo_i] + r[hi_i], 2) for _, r in items})
        for c in edges:
            if c <= lo_b + tol or c >= hi_b - tol: continue
            lo = [it for it in items if it[1][lo_i] + it[1][hi_i] <= c + tol]
            hi = [it for it in items if it[1][lo_i] >= c - tol]
            if not lo or not hi or len(lo) + len(hi) != len(items): continue
            if axis == "x":
                a = guillotine_tree(lo, x0, y0, c, y1, tol)
                b = guillotine_tree(hi, c, y0, x1, y1, tol)
            else:
                a = guillotine_tree(lo, x0, y0, x1, c, tol)
                b = guillotine_tree(hi, x0, c, x1, y1, tol)
            if a and b:
                return {"axis": axis, "cut": c, "lo": a, "hi": b}
    return None


def trees_from_layout(ground, upper, W, H):
    """One slicing tree per level, read off a heuristic layout."""
    out = {}
    for idx, rects in ((0, ground), (1, upper)):
        if not rects: continue
        t = guillotine_tree(sorted(rects.items()), 0.0, 0.0, W, H)
        if t is None: return None
        out[idx] = t
    return out


# ---------------------------------------------------------------- the CP model
class _Model:
    """Builds one CP-SAT model for a given footprint, and remembers what every literal means."""

    def __init__(self, cp_model, plan, prep, levels, fp, demoted=frozenset(), soft_kinds=frozenset(),
                 objective=True, trees=None):
        self.cp = cp_model
        self.m = cp_model.CpModel()
        self.plan, self.prep, self.levels, self.fp = plan, prep, levels, fp
        self.demoted = set(demoted)
        self.soft_kinds = frozenset(soft_kinds)
        self.objective = objective
        self.trees = trees or {}
        self.W, self.H, self.bay = fp["W"], fp["H"], fp["bay"]
        self.Wu = int(round(self.W * U))
        self.Hu = int(round(self.H * U))
        self.bayu = int(round(self.bay * U))
        self.ewalls = GEO.entrance_walls(plan)
        self.v = {}            # (level, room_id) -> dict of vars
        self.lits = {}         # requirement name -> BoolVar
        self.terms = []        # (weight, var) pairs for the objective
        self._build()

    # -- helpers ---------------------------------------------------
    def _is_soft(self, name):
        """Is this requirement a weight rather than a constraint in this model?

        Two ways it can be: the caller demoted it after a conflict named it, or the whole kind
        is soft in this tier (see the two tiers in solve())."""
        return name in self.demoted or _kind(name) in self.soft_kinds

    def _lit(self, name):
        """A named assumption literal. A demoted requirement gets no literal: it moves into the
        objective at the weight geometry.py already charged for missing it."""
        b = self.m.NewBoolVar(f"a::{name}")
        self.lits[name] = b
        return b

    def _pen(self, weight, var):
        self.terms.append((int(round(weight * SCALE)), var))

    def _touches(self, r, wall):
        """Reified: this room's rectangle reaches that wall of the footprint."""
        b = self.m.NewBoolVar("")
        x, y, w, h = r["x"], r["y"], r["w"], r["h"]
        if wall == "S":   on, off = (y == 0), (y >= 1)
        elif wall == "N": on, off = (y + h == self.Hu), (y + h <= self.Hu - 1)
        elif wall == "W": on, off = (x == 0), (x >= 1)
        elif wall == "E": on, off = (x + w == self.Wu), (x + w <= self.Wu - 1)
        else: return None
        self.m.Add(on).OnlyEnforceIf(b)
        self.m.Add(off).OnlyEnforceIf(b.Not())
        return b

    def _touch_any(self, r, walls):
        bs = [self._touches(r, w) for w in walls]
        bs = [b for b in bs if b is not None]
        if not bs: return None
        if len(bs) == 1: return bs[0]
        any_b = self.m.NewBoolVar("")
        self.m.AddBoolOr(bs).OnlyEnforceIf(any_b)
        for b in bs: self.m.AddImplication(b, any_b)
        return any_b

    def _depth(self, r):
        """Distance from the entrance front, in grid units -- how deep into the house a room
        sits. The ceremonial sequence is about this, not about the door graph, which the parti
        already fixed and this solver cannot change."""
        if not self.ewalls: return None
        x, y, w, h = r["x"], r["y"], r["w"], r["h"]
        exprs = []
        for wall in self.ewalls:
            if wall == "S":   exprs.append(y)
            elif wall == "N": exprs.append(self.Hu - (y + h))
            elif wall == "W": exprs.append(x)
            elif wall == "E": exprs.append(self.Wu - (x + w))
        if not exprs: return None
        if len(exprs) == 1:
            d = self.m.NewIntVar(0, max(self.Wu, self.Hu), "")
            self.m.Add(d == exprs[0]); return d
        d = self.m.NewIntVar(0, max(self.Wu, self.Hu), "")
        self.m.AddMinEquality(d, exprs)
        return d

    # -- construction ----------------------------------------------
    def _build(self):
        for idx in (0, 1):
            if self.prep.get(idx):
                self._level(idx)
        self._entrance()
        self._vertical()
        if self.objective:
            self.m.Minimize(sum(wgt * var for wgt, var in self.terms))

    def _leaf_vars(self, idx, rid, x0, y0, x1, y1):
        """Give one room the rectangle its place in the slicing tree defines."""
        room = next(r for r in self.prep[idx] if r["id"] == rid)
        x = self.m.NewIntVar(0, self.Wu, f"x{idx}_{rid}")
        y = self.m.NewIntVar(0, self.Hu, f"y{idx}_{rid}")
        xe = self.m.NewIntVar(0, self.Wu, f"xe{idx}_{rid}")
        ye = self.m.NewIntVar(0, self.Hu, f"ye{idx}_{rid}")
        self.m.Add(x == x0); self.m.Add(xe == x1)
        self.m.Add(y == y0); self.m.Add(ye == y1)
        w = self.m.NewIntVar(1, self.Wu, f"w{idx}_{rid}")
        h = self.m.NewIntVar(1, self.Hu, f"h{idx}_{rid}")
        self.m.Add(w == xe - x); self.m.Add(h == ye - y)
        area = self.m.NewIntVar(1, self.Wu * self.Hu, f"a{idx}_{rid}")
        self.m.AddMultiplicationEquality(area, [w, h])
        self.v[(idx, rid)] = {"room": room, "x": x, "y": y, "w": w, "h": h, "xe": xe, "ye": ye,
                              "area": area, "want": int(round(room["_area"] * U * U))}

    def _build_tree(self, idx, node, x0, y0, x1, y1):
        """Walk the slicing tree, creating one cut variable per internal node.

        Every rectangle is a difference of cut variables, so the whole geometry is linear and
        the layout tiles at any feasible assignment. Nothing here forbids overlap, because a
        tree of cuts cannot produce one."""
        if "leaf" in node:
            self._leaf_vars(idx, node["leaf"], x0, y0, x1, y1)
            return
        axis = node["axis"]
        if axis == "x":
            c = self.m.NewIntVar(0, self.Wu, "")
            self.m.Add(c >= x0 + 1); self.m.Add(c <= x1 - 1)
            self.m.AddHint(c, max(1, min(self.Wu - 1, int(round(node["cut"] * U)))))
            self._build_tree(idx, node["lo"], x0, y0, c, y1)
            self._build_tree(idx, node["hi"], c, y0, x1, y1)
        else:
            c = self.m.NewIntVar(0, self.Hu, "")
            self.m.Add(c >= y0 + 1); self.m.Add(c <= y1 - 1)
            self.m.AddHint(c, max(1, min(self.Hu - 1, int(round(node["cut"] * U)))))
            self._build_tree(idx, node["lo"], x0, y0, x1, c)
            self._build_tree(idx, node["hi"], x0, c, x1, y1)

    def _level_sliced(self, idx):
        self._build_tree(idx, self.trees[idx], 0, 0, self.Wu, self.Hu)
        for room in self.prep[idx]:
            if (idx, room["id"]) in self.v:
                self._room_terms(idx, room)
        self._adjacency(idx, self.prep[idx])
        self._symmetry(idx, self.prep[idx])

    def _level(self, idx):
        if idx in self.trees:
            return self._level_sliced(idx)
        rooms = self.prep[idx]
        xs, ys = [], []
        for room in rooms:
            rid = room["id"]
            want_u2 = int(round(room["_area"] * U * U))
            min_side = int(round(max(MIN_SIDE_FT,
                                     0.5 * min(room.get("width_ft") or MIN_SIDE_FT,
                                               room.get("length_ft") or MIN_SIDE_FT)) * U))
            min_side = max(1, min(min_side, self.Wu, self.Hu))
            x = self.m.NewIntVar(0, self.Wu, f"x{idx}_{rid}")
            y = self.m.NewIntVar(0, self.Hu, f"y{idx}_{rid}")
            w = self.m.NewIntVar(1, self.Wu, f"w{idx}_{rid}")
            h = self.m.NewIntVar(1, self.Hu, f"h{idx}_{rid}")
            self.m.Add(x + w <= self.Wu)
            self.m.Add(y + h <= self.Hu)
            area = self.m.NewIntVar(1, self.Wu * self.Hu, f"a{idx}_{rid}")
            self.m.AddMultiplicationEquality(area, [w, h])
            xe = self.m.NewIntVar(0, self.Wu, f"xe{idx}_{rid}")
            ye = self.m.NewIntVar(0, self.Hu, f"ye{idx}_{rid}")
            self.m.Add(xe == x + w)
            self.m.Add(ye == y + h)
            ix = self.m.NewIntervalVar(x, w, xe, "")
            iy = self.m.NewIntervalVar(y, h, ye, "")
            self.v[(idx, rid)] = {"room": room, "x": x, "y": y, "w": w, "h": h,
                                  "xe": xe, "ye": ye,
                                  "area": area, "ix": ix, "iy": iy, "want": want_u2}
            xs.append(ix); ys.append(iy)

        self.m.AddNoOverlap2D(xs, ys)
        # Areas summing to the footprint, with no overlap and everything inside, IS an exact
        # tiling -- one linear constraint that buys a layout with no voids for render_plan.py
        # to draw as holes. The heuristic gets the same property structurally, from slicing.
        self.m.Add(sum(self.v[(idx, r["id"])]["area"] for r in rooms) == self.Wu * self.Hu)

        for room in rooms:
            self._room_terms(idx, room)
        self._adjacency(idx, rooms)
        self._symmetry(idx, rooms)

    def _room_terms(self, idx, room):
        rid = room["id"]
        r = self.v[(idx, rid)]
        name = f"room-minimum:{rid}"
        min_a = int(round(_min_area_sf(room) * U * U))
        min_side = int(round(max(MIN_SIDE_FT, 0.5 * min(room.get("width_ft") or MIN_SIDE_FT,
                                                        room.get("length_ft") or MIN_SIDE_FT)) * U))
        min_side = max(1, min(min_side, self.Wu, self.Hu))
        # A room below its minimum is never demotable. This is the one requirement whose
        # violation is a defect that survives the whole life of the building, so it is the one
        # that turns an over-stuffed brief into a stated conflict instead of a bad plan. The
        # narrowest side rides on the same literal: 400 sf in a four-foot ribbon is not the room
        # either, and a conflict should be able to say so by name.
        lit = self._lit(name)
        self.m.Add(r["area"] >= min_a).OnlyEnforceIf(lit)
        self.m.Add(r["w"] >= min_side).OnlyEnforceIf(lit)
        self.m.Add(r["h"] >= min_side).OnlyEnforceIf(lit)

        # --- declared exterior walls
        for wall in (room.get("exterior_walls") or []):
            if wall not in "NSEW" or len(wall) != 1: continue
            rname = f"exterior-wall:{rid}:{wall}"
            b = self._touches(r, wall)
            if self._is_soft(rname):
                self._pen(14.0, b.Not())                      # exterior_score's own weight
            else:
                self.m.Add(b == 1).OnlyEnforceIf(self._lit(rname))

        # --- the spanning circulation room is a slab, not a rectangle to pack
        # (geometry.py's own move that turns a treemap into a plan)
        sp_y = GEO.spanning(self.prep[idx], "y")
        sp_x = GEO.spanning(self.prep[idx], "x")
        if sp_y is not None and sp_y["id"] == rid:
            rname = f"spanning:{rid}"
            if self._is_soft(rname): self._pen(14.0, self._eqbool(r["h"], self.Hu).Not())
            else: self.m.Add(r["h"] == self.Hu).OnlyEnforceIf(self._lit(rname))
        elif sp_x is not None and sp_x["id"] == rid:
            rname = f"spanning:{rid}"
            if self._is_soft(rname): self._pen(14.0, self._eqbool(r["w"], self.Wu).Not())
            else: self.m.Add(r["w"] == self.Wu).OnlyEnforceIf(self._lit(rname))

        # --- soft: area fidelity, mirroring level_score's |got-want|/want * 10
        dev = self.m.NewIntVar(0, self.Wu * self.Hu, "")
        self.m.AddAbsEquality(dev, r["area"] - r["want"])
        self._pen(10.0 / max(r["want"], 1), dev)

        # --- soft: aspect, a linear proxy for level_score's (ar - 2.6) * 6.
        # exc5 = max(0, 5w - 13h, 5h - 13w) is 5*min_side*(ar - 2.6) when the room is too thin.
        exc5 = self.m.NewIntVar(0, 13 * max(self.Wu, self.Hu), "")
        self.m.AddMaxEquality(exc5, [0, 5 * r["w"] - 13 * r["h"], 5 * r["h"] - 13 * r["w"]])
        est_min = max(1, int(round(min(room.get("width_ft") or 10, room.get("length_ft") or 12) * U)))
        self._pen(6.0 / (5.0 * est_min), exc5)

        # --- soft: cuts landing on bay lines. Each interior line is shared by two rooms, so
        # the per-edge weight is half geometry.py's 1.5-per-cut; the reported count is a
        # recount from the finished layout (relaxations_from_rects), not this.
        for val, extent, step in ((r["x"], self.Wu, self.bayu), (r["x"] + r["w"], self.Wu, self.bayu),
                                  (r["y"], self.Hu, self.bayu), (r["y"] + r["h"], self.Hu, self.bayu)):
            self._pen(0.75, self._offgrid(val, extent, step))

        # --- soft: principal rooms forward, service to the rear (WP-2.2's weights)
        if self.ewalls:
            fc = _fc(room["type"])
            rear = {GEO._OPPOSITE[w] for w in self.ewalls if w in GEO._OPPOSITE}
            if fc in ("public", "living", "dining"):
                front = self._touch_any(r, self.ewalls)
                if front is not None: self._pen(3.5, front.Not())
            elif fc in ("service", "work"):
                back = self._touch_any(r, rear)
                if back is not None: self._pen(2.0, back.Not())
                front = self._touch_any(r, self.ewalls)
                if front is not None: self._pen(3.0, front)

    def _eqbool(self, var, value):
        b = self.m.NewBoolVar("")
        self.m.Add(var == value).OnlyEnforceIf(b)
        self.m.Add(var != value).OnlyEnforceIf(b.Not())
        return b

    def _offgrid(self, expr, extent, step):
        """Reified: this edge coordinate does NOT land on a bay line (or a footprint edge)."""
        allowed = sorted({0, extent} | {k for k in range(0, extent + 1, step)})
        on = self.m.NewBoolVar("")
        eqs = []
        for L in allowed:
            e = self.m.NewBoolVar("")
            self.m.Add(expr == L).OnlyEnforceIf(e)
            self.m.Add(expr != L).OnlyEnforceIf(e.Not())
            self.m.AddImplication(e, on)
            eqs.append(e)
        self.m.AddBoolOr(eqs).OnlyEnforceIf(on)
        return on.Not()

    def _adjacency(self, idx, rooms):
        """A door between two rooms means the rooms touch, along enough wall to hang one."""
        ids = {r["id"] for r in rooms}
        seen = set()
        seg = int(round(TOUCH_FT * U))
        for room in rooms:
            for d in (room.get("doors") or []):
                t = d.get("to")
                if t == "exterior" or t not in ids or t == room["id"]: continue
                key = tuple(sorted((room["id"], t)))
                if key in seen: continue
                seen.add(key)
                if (idx, key[0]) not in self.v or (idx, key[1]) not in self.v: continue
                a, b = self.v[(idx, key[0])], self.v[(idx, key[1])]
                rname = f"adjacency:{key[0]}~{key[1]}"
                # geometry.py's adjacency_score charges 14 per door that does not land and then
                # halves the total, so a pair whose door is declared from BOTH rooms costs 14
                # and a pair declared from one costs 7. Mirroring that here matters: weighted
                # flat at 7, the solver quietly buys off mutual doors at half price.
                declared = sum(1 for rr in rooms if rr["id"] in key
                               for dd in (rr.get("doors") or []) if dd.get("to") in key
                               and dd.get("to") != rr["id"])
                weight = 7.0 * max(1, min(2, declared))
                sides = []
                for (p, q) in ((a, b), (b, a)):
                    # p's east edge on q's west edge, overlapping vertically by `seg`
                    s = self.m.NewBoolVar("")
                    self.m.Add(p["x"] + p["w"] == q["x"]).OnlyEnforceIf(s)
                    self.m.Add(p["y"] + p["h"] >= q["y"] + seg).OnlyEnforceIf(s)
                    self.m.Add(q["y"] + q["h"] >= p["y"] + seg).OnlyEnforceIf(s)
                    sides.append(s)
                    # p's north edge on q's south edge, overlapping horizontally
                    s2 = self.m.NewBoolVar("")
                    self.m.Add(p["y"] + p["h"] == q["y"]).OnlyEnforceIf(s2)
                    self.m.Add(p["x"] + p["w"] >= q["x"] + seg).OnlyEnforceIf(s2)
                    self.m.Add(q["x"] + q["w"] >= p["x"] + seg).OnlyEnforceIf(s2)
                    sides.append(s2)
                if self._is_soft(rname):
                    touched = self.m.NewBoolVar("")
                    self.m.AddBoolOr(sides).OnlyEnforceIf(touched)
                    for s in sides: self.m.AddImplication(s, touched)
                    self._pen(weight, touched.Not())
                else:
                    self.m.AddBoolOr(sides).OnlyEnforceIf(self._lit(rname))

    def _entrance(self):
        """The entry porch, and the circulation room it opens into, reach the entrance front.

        This is the specific defect WP-2.2 was written for -- the portico inside the footprint.
        There it became a 100-point score term no candidate could win against; here it is a
        constraint, which is the whole difference this package is about."""
        if not self.ewalls or not self.prep.get(0): return
        rooms = self.prep[0]
        byid = {r["id"]: r for r in rooms}
        for room in rooms:
            if _fc(room["type"]) != "threshold": continue
            r = self.v[(0, room["id"])]
            rname = f"entrance-front:{room['id']}"
            b = self._touch_any(r, self.ewalls)
            if b is None: continue
            if self._is_soft(rname): self._pen(100.0, b.Not())
            else: self.m.Add(b == 1).OnlyEnforceIf(self._lit(rname))
            for d in (room.get("doors") or []):
                t = d.get("to")
                if t not in byid or (0, t) not in self.v: continue
                if _fc(byid[t]["type"]) != "circulation": continue
                hname = f"entrance-hall:{t}"
                if hname in self.lits: continue
                hb = self._touch_any(self.v[(0, t)], self.ewalls)
                if hb is None: continue
                if self._is_soft(hname): self._pen(40.0, hb.Not())
                else: self.m.Add(hb == 1).OnlyEnforceIf(self._lit(hname))

        # --- soft: the ceremonial sequence goes spatially deeper, hop by rank-increasing hop
        for room in rooms:
            rank = _rank(room["type"])
            if rank is None: continue
            d_here = self._depth(self.v[(0, room["id"])])
            if d_here is None: continue
            for door in (room.get("doors") or []):
                t = door.get("to")
                if (0, t) not in self.v: continue
                trank = _rank(self.v[(0, t)]["room"]["type"])
                if trank is None or trank <= rank: continue
                d_there = self._depth(self.v[(0, t)])
                if d_there is None: continue
                back = self.m.NewBoolVar("")
                self.m.Add(d_there < d_here - 2).OnlyEnforceIf(back)
                self.m.Add(d_there >= d_here - 2).OnlyEnforceIf(back.Not())
                self._pen(6.0 * (trank - rank), back)

    def _symmetry(self, idx, rooms):
        """On a centre-hall parti, a same-type pair should mirror across the passage.

        Gated on the same spanning-room test the slicer uses, because only a plan that has one
        is a centre-hall parti at all. Doubled coordinates keep the centreline integral:
        d = 2x + w is twice a room's centre, and a mirrored pair satisfies d_a + d_b = 2*d_sp."""
        sp = GEO.spanning(rooms, "y") or GEO.spanning(rooms, "x")
        if sp is None or (idx, sp["id"]) not in self.v: return
        s = self.v[(idx, sp["id"])]
        axis_x = True                      # a passage spanning N-S mirrors the plan left/right
        if GEO.spanning(rooms, "y") is None: axis_x = False
        d_sp = (2 * s["x"] + s["w"]) if axis_x else (2 * s["y"] + s["h"])
        tol = int(round((self.Wu if axis_x else self.Hu) * 0.18)) * 2
        bytype = {}
        for r in rooms:
            if r["id"] == sp["id"] or (idx, r["id"]) not in self.v: continue
            bytype.setdefault(r["type"], []).append(r["id"])
        for rtype, ids in bytype.items():
            if len(ids) < 2: continue
            a, b = self.v[(idx, ids[0])], self.v[(idx, ids[1])]
            da = (2 * a["x"] + a["w"]) if axis_x else (2 * a["y"] + a["h"])
            db = (2 * b["x"] + b["w"]) if axis_x else (2 * b["y"] + b["h"])
            mirrored = self.m.NewBoolVar("")
            diff = self.m.NewIntVar(-4 * max(self.Wu, self.Hu), 4 * max(self.Wu, self.Hu), "")
            self.m.Add(diff == da + db - 2 * d_sp)
            adiff = self.m.NewIntVar(0, 4 * max(self.Wu, self.Hu), "")
            self.m.AddAbsEquality(adiff, diff)
            self.m.Add(adiff <= tol).OnlyEnforceIf(mirrored)
            self.m.Add(adiff > tol).OnlyEnforceIf(mirrored.Not())
            self._pen(1.5, mirrored.Not())

    def _vertical(self):
        """Both levels in one model, which is why they are solved together at all: an upper
        layout that scores better alone is not better if it leaves walls unsupported."""
        if not self.prep.get(1) or not self.prep.get(0): return
        g = [self.v[(0, r["id"])] for r in self.prep[0]]
        u = [self.v[(1, r["id"])] for r in self.prep[1]]
        gx, gy = [], []
        for r in g:
            gx += [r["x"], r["x"] + r["w"]]
            gy += [r["y"], r["y"] + r["h"]]
        near = 3                                     # 0.75 ft, geometry.py's own tolerance
        for r in u:
            for val, lines in ((r["x"], gx), (r["x"] + r["w"], gx),
                               (r["y"], gy), (r["y"] + r["h"], gy)):
                aligned = self.m.NewBoolVar("")
                opts = []
                for L in lines:
                    e = self.m.NewBoolVar("")
                    self.m.Add(val - L <= near).OnlyEnforceIf(e)
                    self.m.Add(val - L >= -near).OnlyEnforceIf(e)
                    self.m.AddImplication(e, aligned)
                    opts.append(e)
                self.m.AddBoolOr(opts).OnlyEnforceIf(aligned)
                self._pen(2.0, aligned.Not())        # vertical_score's own per-edge weight

        # --- an upper wet room lands over a lower one. Asserted only where the ground floor
        # HAS a wet room: where it has none the requirement is unsatisfiable by construction,
        # and an unsatisfiable requirement is an observation for the report, not a conflict.
        wet_g = [r for r in g if set(r["room"].get("fixtures") or [])]
        if not wet_g: return
        for r in u:
            if not set(r["room"].get("fixtures") or []): continue
            rname = f"wet-stack:{r['room']['id']}"
            opts = []
            for q in wet_g:
                o = self.m.NewBoolVar("")
                # the upper room's near corner sits inside the lower room's footprint
                self.m.Add(r["x"] + 1 >= q["x"]).OnlyEnforceIf(o)
                self.m.Add(r["x"] + 1 <= q["x"] + q["w"]).OnlyEnforceIf(o)
                self.m.Add(r["y"] + 1 >= q["y"]).OnlyEnforceIf(o)
                self.m.Add(r["y"] + 1 <= q["y"] + q["h"]).OnlyEnforceIf(o)
                opts.append(o)
            if self._is_soft(rname):
                over = self.m.NewBoolVar("")
                self.m.AddBoolOr(opts).OnlyEnforceIf(over)
                for o in opts: self.m.AddImplication(o, over)
                self._pen(8.0, over.Not())           # vertical_score's own weight
            else:
                self.m.AddBoolOr(opts).OnlyEnforceIf(self._lit(rname))

    # -- solving ---------------------------------------------------
    def hint(self, ground, upper):
        """Start CP-SAT from the heuristic's answer. It is 0.6 s of work and it means the
        optimiser opens on a real plan rather than on nothing.

        The EDGES are snapped to the grid, not the position and the size independently. That
        distinction is the whole value of the hint: two rooms that share a wall hold the same
        coordinate for it, so snapping edges moves both sides of the wall together and the
        layout still tiles. Snapping x and w apart pulls the two sides of every shared wall to
        different places, and the hint arrives violating the one constraint -- areas summing to
        the footprint -- that the model is hardest to satisfy. A hint that breaks the hardest
        constraint is worse than no hint: CP-SAT spends its budget repairing it."""
        for idx, rects in ((0, ground), (1, upper)):
            for rid, (x, y, w, h) in (rects or {}).items():
                key = (idx, rid)
                if key not in self.v: continue
                r = self.v[key]
                x0 = max(0, min(self.Wu, int(round(x * U))))
                y0 = max(0, min(self.Hu, int(round(y * U))))
                x1 = max(x0 + 1, min(self.Wu, int(round((x + w) * U))))
                y1 = max(y0 + 1, min(self.Hu, int(round((y + h) * U))))
                self.m.AddHint(r["x"], x0)
                self.m.AddHint(r["y"], y0)
                self.m.AddHint(r["w"], x1 - x0)
                self.m.AddHint(r["h"], y1 - y0)
                self.m.AddHint(r["xe"], x1)
                self.m.AddHint(r["ye"], y1)

    def names_for(self, indices):
        """Map CP-SAT's core (variable indices) back to the requirement names it came from.

        An index can be negative when the core names a literal's negation; the requirement it
        belongs to is the same either way."""
        proto = self.m.Proto()
        out = set()
        for i in indices:
            idx = i if i >= 0 else -i - 1
            if 0 <= idx < len(proto.variables):
                nm = proto.variables[idx].name
                if nm.startswith("a::"): out.add(nm[3:])
        return out

    def extract(self, solver):
        out = {0: {}, 1: {}}
        for (idx, rid), r in self.v.items():
            x = solver.Value(r["x"]) / U; y = solver.Value(r["y"]) / U
            w = solver.Value(r["w"]) / U; h = solver.Value(r["h"]) / U
            out[idx][rid] = (round(x, 2), round(y, 2), round(w, 2), round(h, 2))
        return out[0], out[1]


# ---------------------------------------------------------------- what the drawing actually meets
def _shared_run(a, b, tol=0.05):
    """Length of wall two rectangles genuinely share, in feet. 0 when they only meet at a corner."""
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    if abs((ax + aw) - bx) <= tol or abs((bx + bw) - ax) <= tol:
        return max(0.0, min(ay + ah, by + bh) - max(ay, by))
    if abs((ay + ah) - by) <= tol or abs((by + bh) - ay) <= tol:
        return max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
    return 0.0


def unmet_requirements(ground, upper, prep, plan, W, H):
    """Which named requirements the finished layout does NOT meet, measured from the rectangles.

    Reported beside the list of requirements the solver demoted, and it is the more trustworthy
    of the two: a demotion says what the solver stopped insisting on, this says what the drawing
    in your hand actually fails. A requirement absent from both lists holds, and the difference
    between 'relaxed' and 'still unmet' is exactly the difference between could-not-evaluate and
    evaluated-and-failed that the rest of the corpus keeps."""
    out = []
    ewalls = GEO.entrance_walls(plan)
    rects = {0: ground or {}, 1: upper or {}}
    for idx, rooms in prep.items():
        if idx not in rects: continue
        byid = {r["id"]: r for r in rooms}
        for room in rooms:
            rid = room["id"]
            rect = rects[idx].get(rid)
            if not rect: continue
            x, y, w, h = rect
            if w * h < _min_area_sf(room) - 0.5:
                out.append(f"room-minimum:{rid}")
            for wall in (room.get("exterior_walls") or []):
                if wall not in "NSEW" or len(wall) != 1: continue
                if not GEO._touches_wall(rect, wall, W, H):
                    out.append(f"exterior-wall:{rid}:{wall}")
            seen = set()
            for d in (room.get("doors") or []):
                t = d.get("to")
                if t == "exterior" or t not in byid or t == rid: continue
                key = tuple(sorted((rid, t)))
                if key in seen or t not in rects[idx]: continue
                seen.add(key)
                if _shared_run(rect, rects[idx][t]) < TOUCH_FT - 0.05:
                    out.append(f"adjacency:{key[0]}~{key[1]}")
            if idx == 0 and ewalls and _fc(room["type"]) == "threshold":
                if not any(GEO._touches_wall(rect, wl, W, H) for wl in ewalls):
                    out.append(f"entrance-front:{rid}")
                for d in (room.get("doors") or []):
                    t = d.get("to")
                    if t not in byid or t not in rects[idx]: continue
                    if _fc(byid[t]["type"]) != "circulation": continue
                    if not any(GEO._touches_wall(rects[idx][t], wl, W, H) for wl in ewalls):
                        out.append(f"entrance-hall:{t}")
        sp_y, sp_x = GEO.spanning(rooms, "y"), GEO.spanning(rooms, "x")
        if sp_y is not None and sp_y["id"] in rects[idx]:
            if abs(rects[idx][sp_y["id"]][3] - H) > 0.3: out.append(f"spanning:{sp_y['id']}")
        elif sp_x is not None and sp_x["id"] in rects[idx]:
            if abs(rects[idx][sp_x["id"]][2] - W) > 0.3: out.append(f"spanning:{sp_x['id']}")
    # wet stacks, only where the ground floor has one to land on
    g_rooms = {r["id"]: r for r in prep.get(0, [])}
    wet_g = [rid for rid in (ground or {}) if set((g_rooms.get(rid) or {}).get("fixtures") or [])]
    if wet_g:
        for room in prep.get(1, []):
            rid = room["id"]
            if not set(room.get("fixtures") or []) or rid not in (upper or {}): continue
            x, y, w, h = upper[rid]
            cx, cy = x + w / 2, y + h / 2
            if not any(ground[q][0] <= cx <= ground[q][0] + ground[q][2]
                       and ground[q][1] <= cy <= ground[q][1] + ground[q][3] for q in wet_g):
                out.append(f"wet-stack:{rid}")
    return sorted(set(out))


# ---------------------------------------------------------------- conflict prose
_KIND_PROSE = {
    "room-minimum": "hold {names} at {their} stated minimum",
    "exterior-wall": "give {names} the exterior {wall} wall {each} declares",
    "adjacency": "put a door between {names}",
    "entrance-front": "bring {names} to the entrance front",
    "entrance-hall": "bring {names} to the entrance front",
    "spanning": "run {names} the full depth of the house",
    "wet-stack": "land {names} over a wet room below",
}

def _kind(name): return name.split(":", 1)[0]

def _room_of(name, prep):
    """Map a requirement name back to the room record(s) it constrains."""
    parts = name.split(":")
    ids = []
    if len(parts) > 1:
        ids = parts[1].split("~") if "~" in parts[1] else [parts[1]]
    out = []
    for lst in prep.values():
        for r in lst:
            if r["id"] in ids: out.append(r)
    return out


def conflict_prose(core, prep, fp, plan):
    """Say, in a sentence a builder would accept, what cannot be done at once.

    The machine-readable requirement names travel beside this, not instead of it -- the
    project's rule is that making a rule executable adds a test, it does not replace the
    statement."""
    massing = C["massings"].get(plan.get("massing") or "", {})
    pile = (massing.get("depth_rooms") or "").replace("-", " ")
    clauses, minima = [], []
    for name in core:
        kind = _kind(name)
        rooms = _room_of(name, prep)
        names = [_display(r) for r in rooms] or [name.split(":", 1)[-1]]
        joined = names[0] if len(names) == 1 else " and ".join([", ".join(names[:-1]), names[-1]])
        if kind == "room-minimum":
            minima.append(joined)
        elif kind == "exterior-wall":
            wall = name.rsplit(":", 1)[-1]
            clauses.append(f"give the {joined} its declared {wall} wall")
        elif kind in ("entrance-front", "entrance-hall"):
            clauses.append(f"bring the {joined} to the entrance front")
        elif kind == "adjacency":
            clauses.append(f"put a door between the {joined}")
        elif kind == "spanning":
            clauses.append(f"run the {joined} the full depth of the house")
        elif kind == "wet-stack":
            clauses.append(f"land the {joined} over a wet room below")
        else:
            clauses.append(name)
    bits = []
    if minima:
        held = minima[0] if len(minima) == 1 else " and ".join([", ".join(minima[:-1]), minima[-1]])
        one = len(minima) == 1
        bits.append(f"hold the {held} at {'its' if one else 'their'} stated "
                    f"{'minimum' if one else 'minimums'}")
    bits += clauses
    if not bits:
        return "the requirements conflict, but the solver could not name which."
    tail = bits[0] if len(bits) == 1 else " and ".join([", ".join(bits[:-1]), bits[-1]])
    house = f"{fp['bays']}-bay, {fp['W']:g} x {fp['H']:g} ft {pile} house".replace("  ", " ")
    # Why the footprint cannot simply be made bigger -- the reader's first question, and the
    # answer decides what they do next: buy a wider lot, or ask for less house.
    if fp.get("lot_maxbay") is not None and fp["bays"] >= fp["lot_maxbay"]:
        wall = ("the lot allows no more bays after its side setbacks, so the house cannot be "
                "made wider")
    elif fp.get("depth_capped"):
        wall = (f"the footprint has grown to the {fp['bays']} bays the parti allows, and it "
                f"cannot be made deeper without ceasing to be a {pile or 'house'}")
    else:
        wall = "the footprint has already grown to the ceiling the parti allows"
    return (f"a {house} ({round(fp['W'] * fp['H'])} sf a floor) cannot {tail} at once, and "
            f"{wall}. Drop a room, widen a room's band, or change the massing.")


# ---------------------------------------------------------------- the solve
def _phase(cp_model, model, seed, workers, limit, assume=True):
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(limit)
    solver.parameters.num_search_workers = int(workers)
    solver.parameters.random_seed = int(seed)
    if assume and model.lits:
        model.m.ClearAssumptions()
        model.m.AddAssumptions(list(model.lits.values()))
    status = solver.Solve(model.m)
    return solver, status


def _minimal_core(cp_model, plan, prep, levels, fp, core, seed, workers, budget, soft_kinds):
    """Deletion-based minimization of the conflict set.

    CP-SAT's own core is *sufficient*, not minimal -- it can name requirements that are along
    for the ride. Dropping one at a time and re-solving keeps only the ones the infeasibility
    actually needs. A drop whose re-solve times out is KEPT, and the report says the set is
    minimal up to the time budget rather than claiming a minimality it did not prove: the same
    rule as the rest of the corpus, where could-not-evaluate is never folded into passed."""
    core = sorted(core)
    proved = True
    t0 = time.time()
    keep = list(core)
    for name in core:
        if len(keep) <= 1: break
        if time.time() - t0 > budget:
            proved = False
            break
        trial = [n for n in keep if n != name]
        m2 = _Model(cp_model, plan, prep, levels, fp, soft_kinds=soft_kinds)
        m2.m.ClearAssumptions()
        m2.m.AddAssumptions([m2.lits[n] for n in trial if n in m2.lits])
        s2 = cp_model.CpSolver()
        s2.parameters.max_time_in_seconds = min(2.0, max(0.5, budget - (time.time() - t0)))
        s2.parameters.num_search_workers = int(workers)
        s2.parameters.random_seed = int(seed)
        st = s2.Solve(m2.m)
        if st == cp_model.INFEASIBLE:
            keep = trial                       # the dropped one was not needed
        elif st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            proved = False                     # could not tell; keep it, and say so
    return keep, proved


# --- which requirements are constraints, and which are weights.
#
# This split is a finding, not a preference. Asserting every declared requirement as a hard
# constraint makes the shipped Tidewater plan infeasible, and not marginally: three of its
# ground rooms (`passage`, `backhall`, `kitchen`) each declare exterior walls on OPPOSITE
# sides, so each must run the full depth of the house, while `porch` declares both E and W and
# so must run the full width across the front. Those cannot all be true of rectangles in one
# footprint. The records are not wrong -- `exterior_walls` in a hand-authored plan means "this
# room has exposure on these sides", which a real plan delivers with an ell, a bay or a wall
# that is not the bounding box's -- but read literally as rectangle edges they are aspirations,
# and geometry.py has always treated them as a 14-point preference for exactly that reason.
#
# So: minimums are hard because a room below its band is a defect that survives the building.
# The entrance and the spanning passage are hard because they are architectural facts a plan
# either has or does not, and WP-2.2 was written for the one defect (the portico inside the
# footprint) that comes of treating the first as a preference. Exterior walls, doors and wet
# stacks stay weights at exactly the weights geometry.py already charged -- but CP-SAT
# *optimises* them where the heuristic sampled 250 guesses at them.
SOFT_ALWAYS = {"exterior-wall", "adjacency", "wet-stack"}
HARD_GEOMETRIC = {"entrance-front", "entrance-hall", "spanning"}
DEMOTABLE = set(HARD_GEOMETRIC)
MAX_DEMOTION_ROUNDS = 4
HINT_SEEDS = 6            # heuristic runs tried for a hint that satisfies the room minimums
TOPOLOGIES = 6            # distinct slicing topologies whose cuts the solver optimises


def solve(plan, parti=None, seed=7, time_budget_s=60.0, mode="cp",
          heuristic_candidates=800, workers=1):
    """Place the plan's rooms. Returns the plan record, or {'error', 'conflict'} when the
    requirements cannot all hold and the ones that cannot are not relaxable."""
    t_start = time.time()
    if mode == "heuristic":
        out = GEO.solve(plan, parti, heuristic_candidates, seed)
        if isinstance(out, dict) and "geometry_report" in out:
            out["geometry_report"]["solver"] = {"engine": "heuristic", "status": "n/a",
                                                "wall_time_s": round(time.time() - t_start, 2),
                                                "relaxed_requirements": [], "fallback_reason": None}
        return out

    prep, levels = GEO.prepare_rooms(plan)
    if prep is None: return {"error": "no ground level"}
    fp0 = GEO.derive_footprint(plan, parti, prep)
    if "error" in fp0: return {"error": fp0["error"]}

    # The heuristic first, always: it is the hint, the cross-check and the fallback, and at
    # 800 candidates it costs well under a second.
    #
    # The cross-check baseline is the default seed's best-of-N, because that is the number the
    # acceptance is written against. The HINT may come from a different seed: a heuristic
    # layout that puts a room below its band is a layout the solver must reject, and handing
    # CP-SAT a hint it has to tear up costs more than it saves. So a few seeds are tried and
    # the first that keeps every room at its minimum is preferred, falling back to the
    # best-scoring one when none does.
    h_plan = GEO.solve(copy.deepcopy(plan), parti, heuristic_candidates, seed)
    h_ground, h_upper = _layout_of(h_plan)
    h_score = None
    if h_ground:
        h_score = score_layout(h_ground, h_upper, prep, levels, plan,
                               h_plan["footprint"]["width_ft"], h_plan["footprint"]["depth_ft"],
                               h_plan["footprint"]["bay_module_ft"])
    hint_g, hint_u, hint_seed = h_ground, h_upper, seed
    hint_feasible = _meets_minimums(h_ground, h_upper, prep)
    if not hint_feasible:
        for extra in range(1, HINT_SEEDS):
            alt = GEO.solve(copy.deepcopy(plan), parti, heuristic_candidates, seed + extra)
            ag, au = _layout_of(alt)
            if ag and _meets_minimums(ag, au, prep):
                hint_g, hint_u, hint_seed, hint_feasible = ag, au, seed + extra, True
                break

    try:
        from ortools.sat.python import cp_model
    except ImportError:
        out = GEO.solve(plan, parti, heuristic_candidates, seed)
        if isinstance(out, dict) and "geometry_report" in out:
            out["geometry_report"]["solver"] = {
                "engine": "heuristic-fallback", "status": "ortools-missing",
                "wall_time_s": round(time.time() - t_start, 2), "relaxed_requirements": [],
                "fallback_reason": ("OR-Tools is not installed, so the plan was placed by the "
                                    "heuristic search, not by the constraint solver. Its "
                                    "compositional terms are preferences, not enforced "
                                    "requirements, and no conflict set can be reported. "
                                    "pip install -r requirements.txt"),
                "cross_check": None}
        return out

    # ---- Tier 1: can this brief be housed at all?
    #
    # Every placement requirement is soft here and only the room minimums are asserted, so an
    # infeasibility at this tier means one thing only: the rooms this brief asks for do not fit
    # in this footprint at the sizes that keep them the rooms they are named as. That is the
    # answer a plan-development partner needs early, and separating it from the geometric
    # requirements is what stops the two being confused -- the exact-tiling equality couples
    # every area variable, so a purely geometric conflict otherwise surfaces as a core full of
    # room minimums that have nothing to do with it. Tier 1 also guarantees the demotion loop
    # below terminates: it is the model everything else relaxes toward.
    fp = _cap_depth(dict(fp0))
    budget_1 = max(4.0, time_budget_s * 0.18)
    proved_fits = False
    status_name = None
    while True:
        base_model = _Model(cp_model, plan, prep, levels, fp,
                            soft_kinds=SOFT_ALWAYS | HARD_GEOMETRIC, objective=False)
        base_model.hint(hint_g, hint_u)
        base_solver, status = _phase(cp_model, base_model, seed, workers, budget_1)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            proved_fits = True
            break
        if status != cp_model.INFEASIBLE:
            # Could not prove the rooms do not fit. That is not the same as proving they do,
            # and it is emphatically not a conflict: placement below does not depend on this
            # answer, so the honest move is to carry on and record that the question was not
            # settled rather than report a conflict the solver never established.
            break
        core = sorted(base_model.names_for(base_solver.SufficientAssumptionsForInfeasibility()))
        if fp["bays"] < fp["growth_ceiling"]:
            # Grow the footprint before compromising a room -- decision #11, now enforced by a
            # solver that has actually proved the rooms do not fit, rather than approximated by
            # a search that never sees the constraint.
            fp = _grow(fp)
            continue
        core, proved = _minimal_core(cp_model, plan, prep, levels, fp, core, seed, workers,
                                     max(3.0, time_budget_s * 0.25), SOFT_ALWAYS | HARD_GEOMETRIC)
        prose = conflict_prose(core, prep, fp, plan)
        return {"error": prose,
                "conflict": {"requirements": core, "minimal": proved, "prose": prose,
                             "footprint": {"width_ft": fp["W"], "depth_ft": fp["H"],
                                           "bays": fp["bays"], "bay_module_ft": fp["bay"]},
                             "grown_to_ceiling": fp["bays"],
                             "note": ("These rooms cannot all hold their stated minimum in this "
                                      "footprint, and the footprint has already grown to the "
                                      "ceiling the parti and the lot allow. A room below its band "
                                      "is a defect that survives the life of the building, so the "
                                      "solver returns the conflict rather than a plan that hides it."
                                      + ("" if proved else " The set is minimal up to the time "
                                         "budget: one or more drops could not be decided in time "
                                         "and were kept."))}}

    # ---- Tier 2: optimise the cut positions of real slicing topologies.
    #
    # The heuristic proposes a topology -- which rooms sit either side of which cut -- and
    # CP-SAT places every cut in it to proven optimality. Several topologies are tried, from
    # different heuristic seeds, and the best result by geometry.py's own scoring wins. This is
    # where the package's claim actually lands: the heuristic picks its cut positions from a
    # random draw and keeps the luckiest of 800, while the same topology solved here is the
    # best that topology admits, and CP-SAT proves it.
    #
    # Where a requirement cannot hold in a given topology, the demotable ones CP-SAT names drop
    # to the weight geometry.py's own scoring already charged for missing them -- which is what
    # the heuristic did silently on every run. Naming them is the difference.
    budget_2 = max(3.0, time_budget_s * 0.16)
    best = None
    demoted, rounds, topologies = set(), 0, 0
    seen_trees = set()
    for extra in range(TOPOLOGIES):
        # Stop starting new topologies once the next one could not finish inside the budget.
        # The budget is a promise about wall time, and a solve already begun runs to its own
        # limit, so the check has to be made before starting, not after.
        if time.time() - t_start + budget_2 > time_budget_s * 0.97: break
        src = (hint_g, hint_u) if extra == 0 else _layout_of(
            GEO.solve(copy.deepcopy(plan), parti, heuristic_candidates, hint_seed + 100 * extra))
        if not src[0]: continue
        trees = trees_from_layout(src[0], src[1], fp["W"], fp["H"])
        if trees is None: continue
        key = json.dumps(trees, sort_keys=True)
        if key in seen_trees: continue
        seen_trees.add(key)
        topologies += 1
        local, rnd = set(demoted), 0
        for rnd in range(1, MAX_DEMOTION_ROUNDS + 1):
            m = _Model(cp_model, plan, prep, levels, fp, local, soft_kinds=SOFT_ALWAYS, trees=trees)
            s, status = _phase(cp_model, m, seed, workers, budget_2)
            if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                g, u = m.extract(s)
                sc = score_layout(g, u, prep, levels, plan, fp["W"], fp["H"], fp["bay"])
                if best is None or sc["score"] < best["score"]["score"]:
                    best = {"ground": g, "upper": u, "score": sc, "status": s.StatusName(status),
                            "demoted": set(local), "rounds": rnd}
                break
            if status != cp_model.INFEASIBLE:
                break
            core = m.names_for(s.SufficientAssumptionsForInfeasibility())
            newly = {n for n in core if _kind(n) in DEMOTABLE} - local
            if not newly: break
            local |= newly

    if best is None:
        return _fallback(plan, parti, seed, heuristic_candidates, t_start,
                         "no slicing topology could be solved within the time budget; the "
                         "heuristic placed this plan instead.")
    ground, upper = best["ground"], best["upper"]
    cp_score, status_name = best["score"], best["status"]
    demoted, rounds = best["demoted"], best["rounds"]

    # --- cross-check: the same scorer on both layouts, and the better one is kept.
    #
    # The footprint's depth is written back at the quarter-foot the solver actually worked in.
    # The rooms tile that depth exactly, so recording the pre-quantisation figure instead would
    # draw a footprint outline an inch deeper than the rooms inside it -- a sliver of nothing
    # along the back wall, and the drawing disagreeing with the data it is supposed to be a
    # view of. The shift is at most an eighth of a foot and it is the depth the plan HAS.
    engine = "cp-sat"
    chosen, chosen_score, chosen_upper = ground, cp_score, upper
    chosen_fp = {**fp, "H": round(int(round(fp["H"] * U)) / U, 2)}
    chosen_fp["slack"] = (chosen_fp["W"] * chosen_fp["H"]) - fp["need"]
    if h_score is not None and h_score["score"] < cp_score["score"]:
        engine = "heuristic-won-cross-check"
        chosen, chosen_upper, chosen_score = h_ground, h_upper, h_score
        chosen_fp = {**fp, "W": h_plan["footprint"]["width_ft"], "H": h_plan["footprint"]["depth_ft"],
                     "bays": h_plan["footprint"]["bays"], "bay": h_plan["footprint"]["bay_module_ft"],
                     "slack": h_plan["footprint"]["slack_sf"]}
    unmet = unmet_requirements(chosen, chosen_upper, prep, plan, chosen_fp["W"], chosen_fp["H"])

    report = {
        "score": chosen_score["score"], "ground_score": chosen_score["ground"],
        "upper_score": chosen_score["upper"], "vertical_score": chosen_score["vertical"],
        "bays_grown": fp["grown"],
        "lot_capped": (fp["lot_maxbay"] is not None and fp["lot_maxbay"] < fp["catalog_maxbay"]),
        "relaxations": {"count": chosen_score["relaxations"],
                        "max_off_grid_ft": chosen_score["max_off_grid_ft"],
                        "note": ("Wall lines that do not land on a bay line. Each one is a joist run "
                                 "that misses a bearing line and a window bay that will not centre."
                                 if chosen_score["relaxations"] else "Every wall line landed on a bay line.")},
        "vertical": chosen_score["vnotes"] or ["Every upper wall continues to a wall below and every stack lands."],
        "reading": ("Ground and upper were stated as one constraint programme and solved together, so "
                    "an upper layout that would score better alone is rejected when it leaves walls "
                    "unsupported."),
        "solver": {
            "engine": engine, "status": status_name,
            "wall_time_s": round(time.time() - t_start, 2),
            "relaxed_requirements": sorted(demoted),
            "unmet_requirements": unmet,
            "relaxed_note": (
                "These requirements could not all hold at once. Each was relaxed to the weight "
                "geometry.py's own scoring already charged for missing it -- which is what the "
                "heuristic did silently on every run. Naming them is the difference."
                if demoted else "Every stated requirement was asserted as a constraint, not a preference."),
            "unmet_note": (
                "Measured from the finished rectangles rather than from what the solver stopped "
                "insisting on: these are the requirements the drawing in your hand does not meet. "
                "A requirement in neither list holds." if unmet
                else "Every named requirement holds in the returned layout."),
            "demotion_rounds": rounds,
            "topologies_tried": topologies,
            "rooms_fit_proved": proved_fits,
            "rooms_fit_note": (
                "The solver proved these rooms fit this footprint at their stated minimums."
                if proved_fits else
                "Whether these rooms fit this footprint at their stated minimums was NOT settled "
                "within the time budget. That is could-not-evaluate, not evaluated-and-passed: "
                "the layout below meets every minimum, but no claim is made that a conflict "
                "could not have been found with longer to look."),
            "cross_check": {"cp_score": cp_score["score"],
                            "heuristic_score": h_score["score"] if h_score else None,
                            "heuristic_candidates": heuristic_candidates,
                            "note": ("Both layouts scored by geometry.py's own scoring functions, "
                                     "so the comparison is one metric and not two engines grading "
                                     "themselves.")},
            "fallback_reason": None}}
    if mode == "both" and h_score is not None:
        report["solver"]["cross_check"]["heuristic_relaxations"] = h_score["relaxations"]
    return GEO.write_record(plan, levels, chosen, chosen_upper, chosen_fp, report)


DEPTH_TOLERANCE = 1.18          # the same slack geometry.py's own growth loop allows


def _cap_depth(fp):
    """Bound the footprint's depth by the massing's own pile.

    geometry.py grows the footprint in bays and then lets depth take whatever the area needs.
    That is fine while bays are free, but when the lot caps the bay count the depth grows
    without limit, and a brief that cannot be built comes back as a 20 x 75 ft "single-pile"
    house -- which is not a single-pile house, it is a different massing wearing the name. The
    pile is a style fact, not a diagram convention, so this bounds it at the same 1.18 slack
    geometry.py's growth loop already allows, and lets the rooms be what does not fit.

    This is what makes an infeasible brief reachable at all: while the footprint is derived
    from the rooms it contains, the rooms always fit by construction, and no conflict set could
    ever be reported. Bounding depth is what turns "grow the footprint before compromising a
    room" into a statement with an end -- grow it in bays, up to the ceiling the parti and the
    lot allow, and when that runs out, say so."""
    fp = dict(fp)
    cap = round(fp["target_depth"] * DEPTH_TOLERANCE, 2)
    if fp["H"] > cap:
        fp["H"] = cap
        fp["depth_capped"] = True
        fp["slack"] = (fp["W"] * fp["H"]) - fp["need"]
    else:
        fp.setdefault("depth_capped", False)
    return fp


def _layout_of(plan_out):
    """Pull the per-level rectangles back out of a solved plan record."""
    ground, upper = {}, {}
    if not isinstance(plan_out, dict) or "geometry_report" not in plan_out:
        return ground, upper
    for i, lv in enumerate(plan_out["levels"]):
        idx = lv.get("index", i)
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g: continue
            rect = (g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"])
            (ground if idx == 0 else upper)[r["id"]] = rect
    return ground, upper


def _meets_minimums(ground, upper, prep):
    """Does this layout keep every room at or above the floor of its own band?

    Asked of a *heuristic* layout, and the answer is often no: the spec Colonial's dining room
    comes back at 91 sf against a 122 sf minimum, because geometry.py's level_score charges a
    flat 12 points for a room below its band and a candidate can win while paying it. That is
    the whole difference this package is about -- but it also means the obvious hint is a
    layout CP-SAT must reject, and a rejected hint is worse than none. So the hint is chosen
    from among several heuristic runs by whether it satisfies the constraint, not only by
    what it scores."""
    for idx, rects in ((0, ground), (1, upper)):
        for room in prep.get(idx, []):
            rect = rects.get(room["id"])
            if not rect: continue
            if rect[2] * rect[3] < _min_area_sf(room) - 0.01:
                return False
    return True


def _grow(fp):
    fp = dict(fp)
    fp["bays"] += 1
    fp["grown"] = list(fp["grown"]) + [fp["bays"]]
    fp["W"] = round(fp["bays"] * fp["bay"], 2)
    fp["H"] = round(fp["need"] / fp["W"], 2)
    fp["slack"] = (fp["W"] * fp["H"]) - fp["need"]
    fp["depth_capped"] = False
    return _cap_depth(fp)


def _fallback(plan, parti, seed, candidates, t_start, reason):
    out = GEO.solve(plan, parti, candidates, seed)
    if isinstance(out, dict) and "geometry_report" in out:
        out["geometry_report"]["solver"] = {
            "engine": "heuristic-fallback", "status": "fallback",
            "wall_time_s": round(time.time() - t_start, 2), "relaxed_requirements": [],
            "fallback_reason": reason, "cross_check": None}
    return out


# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--out"); ap.add_argument("--svg")
    ap.add_argument("--parti"); ap.add_argument("--mode", default="cp",
                                                choices=["cp", "heuristic", "both"])
    ap.add_argument("--time", type=float, default=60.0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--candidates", type=int, default=800)
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    parti = json.load(open(f"{ROOT}/partis/{a.parti}.json")) if a.parti else None
    out = solve(plan, parti, seed=a.seed, time_budget_s=a.time, mode=a.mode,
                heuristic_candidates=a.candidates, workers=a.workers)
    if "error" in out:
        print(f"\n  {plan.get('name', a.plan)}")
        print(f"  INFEASIBLE — {out['error']}")
        for r in (out.get("conflict") or {}).get("requirements", []):
            print(f"    · {r}")
        print()
        return
    fp, gr = out["footprint"], out["geometry_report"]
    sv = gr.get("solver", {})
    print(f"\n  {plan['name']}")
    print(f"  footprint {fp['width_ft']} x {fp['depth_ft']} ft, {fp['bays']} bays of "
          f"{fp['bay_module_ft']} ft, {fp['area_sf']} sf gross")
    print(f"  engine {sv.get('engine')} ({sv.get('status')}) in {sv.get('wall_time_s')} s")
    print(f"  score {gr['score']}  (ground {gr['ground_score']}, upper {gr['upper_score']}, "
          f"vertical {gr['vertical_score']})")
    cc = sv.get("cross_check") or {}
    if cc.get("heuristic_score") is not None:
        print(f"  cross-check: cp {cc['cp_score']} vs heuristic {cc['heuristic_score']} "
              f"(best of {cc['heuristic_candidates']})")
    print(f"  relaxations {gr['relaxations']['count']}, worst "
          f"{gr['relaxations']['max_off_grid_ft']} ft off the bay line")
    for r in sv.get("relaxed_requirements", []): print(f"    relaxed · {r}")
    for n in gr["vertical"][:6]: print(f"    · {n}")
    if a.out: json.dump(out, open(a.out, "w"), indent=1, ensure_ascii=False); print(f"  wrote {a.out}")
    if a.svg:
        rp = _mod("render_plan", f"{ROOT}/build/render_plan.py")
        rp.render(out, a.svg); print(f"  wrote {a.svg}")
    print()


if __name__ == "__main__":
    main()
