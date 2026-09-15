"""The sheet, read as a fluent reader reads it -- Phase 13's gate, written RED before any fix.

On 15 Sep 2026 Lucas read the two plates of the Tidewater sheet and listed nine things wrong
with it: the stair halls do not stack; the door swings are mirrored; the furniture makes no
sense and carries no label; the chimneys stand on windows and bear no relation to a fireplace;
the powder room is not enclosed; the bays are not coordinated between floors, plans or
elevations; the scale does not scale. It was his SECOND such list -- the first, 4 Sep, produced
sixty findings and an order of work whose structural items were built on the SEARCH engine,
measured inert there, and stood down, while the sheet he reads is drawn by the PROVER. Nothing
in 1,469 tests read the whole plate for any of the nine; each tests a part.

So this file reads the plate. Every test here renders the reference plan AND the composer's
own top candidate for the Tidewater brief (the sheet Lucas actually read was a compose
candidate) on both engines, reads the SVG and the placed record back, and asserts as a NUMBER
what a reader sees. Every assertion carries the measured figure in its message, so a red row
is a reproduction and not an opinion.

The rules this file is held to:

  * It reads the emitted ink (`tests/test_drawn_geometry.py`'s discipline) -- the W3C
    endpoint-to-centre rule is implemented HERE, independently of the code under test.
  * The heuristic figures are deterministic and may be ratcheted. The CP-SAT figures are NOT:
    `auto` returned 130/132/133 on one unchanged tree (CLAUDE.md), so on the prover this file
    asserts only what Phase 13 step 3 makes HARD -- a proved fact is deterministic by
    construction. Until then those rows are red, which is the point.
  * Unjudged is not passed: a sheet with nothing to judge SKIPS with the words COULD NOT
    EVALUATE; it never passes by absence.
  * NO RE-BASELINING. A red assertion here is a defect on the sheet, not a ceiling to raise.

`docs/reports/wp-13.1-the-gate.md` is the account of what each row measured on `840c7f1`.
"""
import copy
import json
import math
import os
import re
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _b(name):
    return modcache.load(name, os.path.join(ROOT, "build", name + ".py"))


G = _b("geometry")
RP = _b("render_plan")
ST = _b("structure")
HE = _b("hearths")
RF = _b("roof")
EL = _b("elevation")
CO = _b("compose")
STK = _b("stacking")

CAREFUL = "tidewater-georgian-careful"
BRIEF = "family-georgian"
KINDS = ("careful", "candidate")
ENGINES = ("heuristic", "cp")
SHEETS = [(k, e) for k in KINDS for e in ENGINES]
IDS = [f"{k}-{e}" for k, e in SHEETS]

# ---------------------------------------------------------------- the sheets, solved once
_CACHE, _DECLARED = {}, {}


def _declared(kind):
    """The DECLARED record, carrying its parti ID (an id and never a record -- WP-9.4's rule;
    `geometry.parti_for` loads it through the one place an id becomes a path). `careful` is
    the shipped reference plan; `candidate` is the composer's top diagram for the Tidewater
    brief, as composed (no revision loop -- the loop is the search engine's and this file
    measures placements). Composed ONCE: a fixture that re-composed on every failing row cost
    nine minutes on the first run of this file."""
    if kind not in _DECLARED:
        if kind == "careful":
            plan = json.load(open(os.path.join(ROOT, "plans", CAREFUL + ".json")))
        else:
            brief = json.load(open(os.path.join(ROOT, "briefs", BRIEF + ".json")))
            cand = CO.compose(brief, candidates=2, revise=False)["candidates"][0]
            plan = cand["plan"]
            plan.setdefault("parti", cand["parti"])
        _DECLARED[kind] = plan
    return _DECLARED[kind]


@pytest.fixture(scope="module")
def sheets(tmp_path_factory):
    """`get(kind, engine)` -> (placed record, presentation SVG, svg path). Solved once per
    module: the prover costs ~40 s a sheet and there are two of them. A sheet that could not
    be solved is remembered as such, so every row fails fast with the same reason."""
    out_dir = tmp_path_factory.mktemp("coherence")

    def get(kind, engine, strict=False):
        """`strict=True` turns an unplaceable sheet into a FAILURE (one row owns that fact);
        every other row reports COULD NOT EVALUATE, because sixteen copies of one error are
        not sixteen findings and a skipped row is never a passed one."""
        key = (kind, engine)
        if key not in _CACHE:
            plan = copy.deepcopy(_declared(kind))
            G._SOLVE_CACHE.clear()
            try:
                out = G.solve(plan, None, 250, engine=engine)
            except Exception as e:                       # noqa: BLE001 -- remembered, not hidden
                _CACHE[key] = f"{kind} could not be placed on {engine}: {e}"
            else:
                if "error" in out:
                    _CACHE[key] = f"{kind} could not be placed on {engine}: {out['error']}"
                else:
                    path = str(out_dir / f"{kind}-{engine}.svg")
                    RP.render(out, path, register="presentation")   # the register the workbench draws
                    _CACHE[key] = (out, open(path, encoding="utf-8").read(), path)
        if isinstance(_CACHE[key], str):
            if strict:
                pytest.fail(_CACHE[key])
            pytest.skip("COULD NOT EVALUATE: " + _CACHE[key])
        return _CACHE[key]
    return get


# ---------------------------------------------------------------- readers of the record
def _placed_levels(out):
    return [lv for lv in out["levels"] if any(r.get("geometry") for r in lv["rooms"])]


def _rooms(lv):
    return [r for r in lv["rooms"] if r.get("geometry") and not r["geometry"].get("void")]


def _rect(r):
    g = r["geometry"]
    return g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]


def _blocks(out):
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    return [(b["x_ft"], b["y_ft"], b["width_ft"], b["depth_ft"]) for b in (fp.get("blocks") or [])] \
        or [(0.0, 0.0, W, H)]


def _engine(out):
    return ((out.get("geometry_report") or {}).get("solver") or {}).get("engine")


# ---------------------------------------------------------------- readers of the ink
def _frame(svg):
    m = re.search(r"data-frame='([^']+)'", svg)
    assert m, "the sheet carries no data-frame"
    return json.loads(m.group(1))["plates"]


def _xy(plate):
    ox, oy = plate["origin_px"]
    ax, ay = plate["at_origin_ft"]
    k = plate["px_per_ft"]
    return (lambda v: ox + (v - ax) * k), (lambda v: oy + (ay - v) * k), k


def _schedule(svg):
    """The title-block lines, in order -- every `class="lb"` text after the schedule rule."""
    return [t for t in re.findall(r'<text class="lb"[^>]*>([^<]*)</text>', svg)]


def _texts(svg):
    return re.findall(r'<text\b([^>]*)>([^<]*)</text>', svg)


_ATTR = re.compile(r'(\w[\w-]*)="([^"]*)"')


def _attrs(s):
    return dict(_ATTR.findall(s))


def _svg_arc_centre(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    """W3C SVG 1.1 F.6.5 endpoint-to-centre. Deliberately an independent implementation,
    the same one `tests/test_drawn_geometry.py` carries for the mouldings -- a guard that
    shares an implementation with its subject cannot catch that implementation being wrong."""
    cphi, sphi = math.cos(phi), math.sin(phi)
    dx2, dy2 = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p, y1p = cphi * dx2 + sphi * dy2, -sphi * dx2 + cphi * dy2
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        rx *= math.sqrt(lam)
        ry *= math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if fa == fs:
        co = -co
    cxp, cyp = co * (rx * y1p / ry), co * (-ry * x1p / rx)
    return cphi * cxp - sphi * cyp + (x1 + x2) / 2.0, sphi * cxp + cphi * cyp + (y1 + y2) / 2.0


_LEAF = re.compile(
    r'<path class="sw" d="M ([-\d.]+) ([-\d.]+) A ([\d.]+) [\d.]+ 0 0 ([01]) ([-\d.]+) ([-\d.]+)"/>'
    r'\s*<line class="dr" x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"/>')


def _door_arcs(svg):
    """Every drawn door leaf: (start, radius, sweep, end, hinge), in sheet px. The hinge is
    the `class="dr"` leaf line emitted straight after the arc, whose (x1, y1) is the hinge."""
    out = []
    for ex, ey, r, sw, tx, ty, hx, hy, _lx, _ly in _LEAF.findall(svg):
        out.append(((float(ex), float(ey)), float(r), int(sw), (float(tx), float(ty)),
                    (float(hx), float(hy))))
    return out


# ---------------------------------------------------------------- 0. vacuity
@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_the_sheet_is_drawn_at_all(sheets, kind, engine):
    """Every assertion below selects on the ink; this pins that there is ink to select on, so
    a selector matching nothing cannot make the file green (the `class="ch"` lesson).

    AND IT IS THE ONE ROW THAT OWNS "THIS SHEET COULD NOT BE PLACED AT ALL". Measured on
    `840c7f1`: the composer's own top candidate for the Tidewater brief returns UNKNOWN from
    CP-SAT inside the 40 s batch budget, so the bench's `auto` falls back to the search and the
    sheet Lucas read was never proved. That is a fact about the product, stated here once."""
    out, svg, _ = sheets(kind, engine, strict=True)
    levels = _placed_levels(out)
    assert len(levels) >= 2, f"{len(levels)} placed level(s)"
    assert sum(len(_rooms(lv)) for lv in levels) >= 10
    assert len(_frame(svg)) == len(levels)
    assert len(_door_arcs(svg)) >= 6, "fewer than six door leaves on the sheet"
    assert svg.count('class="fu"') >= 10, "fewer than ten furniture marks on the sheet"
    assert _engine(out) in ("cp-sat", "heuristic"), _engine(out)


# ---------------------------------------------------------------- 1. the stairs do not stack
@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_declared_stacks_land_by_containment(sheets, kind, engine):
    """A room that declares `stacks_over` another stands OVER it -- contained, not merely
    touching. `stacking.py`'s kept/broken test is a strict positive intersection, under which
    a 0.16 sf corner counts as a landed stack; this asks for the smaller rectangle to lie at
    least 90% inside the larger, which is what "the stair hall stacks" means to a reader."""
    out, _svg, _ = sheets(kind, engine)
    kept, broken, unjudged = STK.judge(out)
    claims = kept + broken
    if not claims:
        pytest.skip(f"COULD NOT EVALUATE: {kind} declares no judgeable stack "
                    f"({len(unjudged)} unjudged)")
    by = STK.rooms_by_level(out)
    bad = []
    for c in claims:
        a = STK._rect(by[c["level"]][c["room"]])
        b = STK._rect(by[c["level"] - 1][c["over"]])
        ix = max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
        iy = max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
        frac = (ix * iy) / min(a[2] * a[3], b[2] * b[3])
        if frac < 0.9:
            bad.append(f"{c['room']} over {c['over']}: {ix * iy:.1f} sf shared, "
                       f"{frac * 100:.0f}% of the smaller room")
    assert not bad, (f"{len(bad)} of {len(claims)} declared stacks do not land on {_engine(out)}: "
                     + "; ".join(bad))


# ---------------------------------------------------------------- 2. the door swings
@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_every_door_arc_is_centred_on_its_hinge(sheets, kind, engine):
    """Read the emitted arc back through the W3C rule: its centre must be the hinge the leaf
    line beside it is drawn from. A mirrored arc -- drawn as its own reflection about the
    chord, hollowing back toward the hinge -- has its centre r*sqrt(2) away from it."""
    _out, svg, _ = sheets(kind, engine)
    arcs = _door_arcs(svg)
    bad = []
    for (ex, ey), r, sw, (tx, ty), (hx, hy) in arcs:
        cx, cy = _svg_arc_centre(ex, ey, r, r, 0.0, 0, sw, tx, ty)
        err = math.hypot(cx - hx, cy - hy)
        if err > 0.6:
            wall = "horizontal" if abs(hy - ty) < 0.05 else "vertical"
            bad.append(f"hinge ({hx:.1f},{hy:.1f}) on a {wall} wall, centre off by {err:.1f} px"
                       f" (r={r:.1f}, r*sqrt2={r * math.sqrt(2):.1f})")
    assert not bad, (f"{len(bad)} of {len(arcs)} door arcs are drawn as their own mirror: "
                     + "; ".join(bad[:6]))


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_every_door_arc_in_the_dxf_swings_the_way_the_record_says(sheets, kind, engine):
    """The DXF draws a third door arc, and it must be the same door: centred on the hinge the
    record states, at the leaf's radius, sweeping to the side `swing_positive` names."""
    ezdxf = pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    EX = _b("export_dxf")
    out, _svg, path = sheets(kind, engine)
    dxf = path.replace(".svg", ".dxf")
    EX.export_plan_dxf(out, dxf)
    doc = ezdxf.readfile(dxf)
    arcs = [e for e in doc.modelspace() if e.dxftype() == "ARC" and "DOOR" in e.dxf.layer.upper()]
    IN = getattr(EX, "IN", 12.0)
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    want, bad = 0, []
    for lv in _placed_levels(out):
        op = RP.openings_of_level(out, lv)
        for d in op["interior"]:
            if d["type"] in RP.LEAFLESS:
                continue
            half = d["width_ft"] / 2.0
            low = (d.get("hinge") or "low") == "low"      # the RECORD's jamb, read by all three
            if d["horiz"]:
                px, py = d["pos_ft"], d["at_ft"]
                tip = 90 if d["swing_positive"] else 270
                leaves = ([((px - half, py), half, tip), ((px + half, py), half, tip)]
                          if d["type"] == "double" else
                          [((px - half if low else px + half, py), 2 * half, tip)])
            else:
                px, py = d["at_ft"], d["pos_ft"]
                tip = 0 if d["swing_positive"] else 180
                leaves = ([((px, py - half), half, tip), ((px, py + half), half, tip)]
                          if d["type"] == "double" else
                          [((px, py - half if low else py + half), 2 * half, tip)])
            for (hx, hy), r, tip_deg in leaves:
                want += 1
                hit = None
                for a in arcs:
                    c = a.dxf.center
                    if math.hypot(c.x - hx * IN, c.y - hy * IN) <= 1.0 and abs(a.dxf.radius - r * IN) <= 1.0:
                        s, e = a.dxf.start_angle % 360, a.dxf.end_angle % 360
                        span = (e - s) % 360 or 360
                        if (tip_deg - s) % 360 <= span + 1e-6:
                            hit = a
                            break
                if hit is None:
                    bad.append(f"{d.get('from', '?')}-{d.get('to', '?')} hinge ({hx:.2f},{hy:.2f}) "
                               f"r={r:.2f} ft, leaf toward {tip_deg} deg")
    assert want, "COULD NOT EVALUATE: no interior door on this plan"
    assert not bad, (f"{len(bad)} of {want} door leaves have no DXF arc centred on their hinge "
                     f"and swung the way the record says ({len(arcs)} door arcs in the file): "
                     + "; ".join(bad[:6]))


# ---------------------------------------------------------------- 6. the powder room
def _uncovered(rooms, block, step=0.1):
    """Square feet of `block` inside no room rectangle, by rasterising at `step`."""
    bx, by, bw, bh = block
    nx, ny = int(round(bw / step)), int(round(bh / step))
    cov = bytearray(nx * ny)
    for r in rooms:
        x, y, w, h = _rect(r)
        x0, y0 = int(round((x - bx) / step)), int(round((y - by) / step))
        x1, y1 = int(round((x + w - bx) / step)), int(round((y + h - by) / step))
        for yy in range(max(0, y0), min(ny, y1)):
            row = yy * nx
            for xx in range(max(0, x0), min(nx, x1)):
                cov[row + xx] = 1
    return sum(1 for v in cov if not v) * step * step


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_every_level_tiles_its_block(sheets, kind, engine):
    """The rooms of a level tile the block they sit in: there is no floor that is no room.
    `geometry_cp.COVERAGE = 0.97` is a hard FLOOR and `_absorb` accepts "honest empty floor";
    the honest empty floor arrives as a 0.92 ft strip between two rooms across which no wall
    is drawn, and a reader sees a powder room open to the drawing room."""
    out, _svg, _ = sheets(kind, engine)
    bad = []
    for lv in _placed_levels(out):
        for blk in _blocks(out):
            inside = [r for r in _rooms(lv) if blk[0] - 0.05 <= _rect(r)[0] and
                      _rect(r)[0] + _rect(r)[2] <= blk[0] + blk[2] + 0.05 and
                      blk[1] - 0.05 <= _rect(r)[1] and
                      _rect(r)[1] + _rect(r)[3] <= blk[1] + blk[3] + 0.05]
            if not inside:
                continue
            u = _uncovered(inside, blk)
            if u > 0.05:
                bad.append(f"{lv['id']}: {u:.1f} sf of the {blk[2]:g} x {blk[3]:g} block is no room")
    assert not bad, f"on {_engine(out)}: " + "; ".join(bad)


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_every_room_edge_carries_a_wall_or_an_opening(sheets, kind, engine):
    """Every edge of every placed room is ink: a wall body, or an opening cut through one.
    `wall_bands` draws interior walls only where two rooms SHARE an edge, so an edge that
    bounds residual void gets nothing -- no poche, no line, no door.

    THE MEASURE IS THE LONGEST CONTIGUOUS MISSING RUN, not the total. `_trim_junctions` cuts
    each run back to the face of the wall it meets, so a 38 ft passage edge on the tiling
    engine shows 0.7 ft of missing ink in three-inch bites at its cross-walls -- correct
    drawing. A 6 ft hole where a room bounds residual void is one run. A run over 1.0 ft is
    a wall that is not there."""
    out, _svg, _ = sheets(kind, engine)
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    wall = ST.wall_thickness(out)
    bad, checked = [], 0
    for lv in _placed_levels(out):
        op = RP.openings_of_level(out, lv)
        gaps = RP.opening_gaps(op, W, H)
        bands, _stray = RP.wall_bands(lv["rooms"], _blocks(out), W, H, fp.get("bay_module_ft"),
                                      wall, gaps)

        def covered(axis, pos, s):
            for b in bands:
                if axis == "x" and b["x_ft"] - 0.06 <= pos <= b["x_ft"] + b["width_ft"] + 0.06 \
                        and b["y_ft"] - 0.02 <= s <= b["y_ft"] + b["depth_ft"] + 0.02:
                    return True
                if axis == "y" and b["y_ft"] - 0.06 <= pos <= b["y_ft"] + b["depth_ft"] + 0.06 \
                        and b["x_ft"] - 0.02 <= s <= b["x_ft"] + b["width_ft"] + 0.02:
                    return True
            for gax, gpos, lo, hi in gaps:
                if gax == axis and abs(gpos - pos) <= RP.GAP_TOL_FT and lo - 0.02 <= s <= hi + 0.02:
                    return True
            return False

        for r in _rooms(lv):
            x, y, w, h = _rect(r)
            for label, axis, pos, lo, hi in (("W", "x", x, y, y + h), ("E", "x", x + w, y, y + h),
                                             ("S", "y", y, x, x + w), ("N", "y", y + h, x, x + w)):
                if hi - lo < 1.6:
                    continue
                miss, run, worst = 0.0, 0.0, 0.0
                s = lo + 0.3
                while s < hi - 0.3:
                    checked += 1
                    if not covered(axis, pos, s):
                        miss += 0.1
                        run += 0.1
                        worst = max(worst, run)
                    else:
                        run = 0.0
                    s += 0.1
                if worst > 1.0:
                    bad.append(f"{lv['id']} {r['id']} {label} edge: a {worst:.1f} ft run of its "
                               f"{hi - lo:.1f} ft has neither wall nor opening ({miss:.1f} ft in all)")
    assert checked, "COULD NOT EVALUATE: no room edge was sampled"
    assert not bad, (f"on {_engine(out)}, {len(bad)} room edge(s) are drawn as nothing: "
                     + "; ".join(bad[:8]))


# ---------------------------------------------------------------- 4. the chimneys
def _stacks(out):
    return [s for s in ((out.get("hearths") or {}).get("stacks") or []) if s.get("x_ft") is not None]


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_every_hearth_breast_stands_on_a_wall_a_stack_stands_on(sheets, kind, engine):
    """A fireplace has a flue behind it. The breast `hearths.breast` draws on the room's
    declared wall must lie on the block face that wall names, with a stack of the same wall
    letter standing behind it along the wall -- not 26 ft inboard of the only stack on that
    side, on a wall the solver released."""
    out, _svg, _ = sheets(kind, engine)
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    stacks = _stacks(out)
    rows, bad = 0, []
    for lv in _placed_levels(out):
        for r in _rooms(lv):
            for h in (r.get("hearth") or []):
                br = HE.breast(r, h)
                if not br:
                    continue
                rows += 1
                wl = br["wall"]
                face = {"W": br["x_ft"], "E": br["x_ft"] + br["width_ft"],
                        "S": br["y_ft"], "N": br["y_ft"] + br["depth_ft"]}[wl]
                block_face = {"W": 0.0, "E": W, "S": 0.0, "N": H}[wl]
                along = (br["y_ft"], br["y_ft"] + br["depth_ft"]) if wl in ("E", "W") \
                    else (br["x_ft"], br["x_ft"] + br["width_ft"])
                mine = [s for s in stacks if s["wall"] == wl]
                behind = [s for s in mine
                          if (min(along[1], (s["y_ft"] if wl in ("E", "W") else s["x_ft"]) +
                                  (s["depth_ft"] if wl in ("E", "W") else s["width_ft"]))
                              - max(along[0], s["y_ft"] if wl in ("E", "W") else s["x_ft"])) > -1.0]
                if abs(face - block_face) > 0.1 or not behind:
                    where = ", ".join(f"{s['wall']} stack along {s['y_ft'] if wl in ('E', 'W') else s['x_ft']:.1f}"
                                      f"-{(s['y_ft'] + s['depth_ft']) if wl in ('E', 'W') else (s['x_ft'] + s['width_ft']):.1f}"
                                      for s in mine) or "no stack on that wall"
                    bad.append(f"{r['id']}'s breast on its {wl} wall stands {abs(face - block_face):.1f} ft "
                               f"from the {wl} face, along {along[0]:.1f}-{along[1]:.1f}; {where}")
    if not rows:
        pytest.skip(f"COULD NOT EVALUATE: {kind} states no placed hearth")
    assert not bad, (f"on {_engine(out)}, {len(bad)} of {rows} hearths have no flue behind them: "
                     + "; ".join(bad))


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_the_plans_stacks_are_the_roofs_stacks(sheets, kind, engine):
    """One building: the stack the plan draws in poche is the stack the roof and the elevation
    stand on the ridge. On `840c7f1` the roof reconciled its positions to the hearths' flue
    axes while the plan put one 22 in square at the centre of each gable end from the
    rectangle alone -- 5.4 and 7.3 ft apart along the wall.

    COMPARED ALONG THE WALL AND BY END, NOT ACROSS THE WALL. The two records do not share an
    origin (`oq/the-roof-record-and-the-plan-record-do-not-share-an-origin`): the roof's x is
    the wall FACE in an outside-to-outside frame and the plan's exterior square is centred
    half a stack outside the wall, so the across-wall distance is 2.2 ft on every plan by
    construction and measures the frame, not the house. What a reader sees is whether the
    chimney stands over the fire ALONG the gable, and which end it is on."""
    out, _svg, _ = sheets(kind, engine)
    roof = RF.build_roof(copy.deepcopy(out))
    assert "error" not in roof, roof.get("error")
    positions = (roof.get("chimneys") or {}).get("positions") or []
    stacks = _stacks(out)
    if not positions and not stacks:
        pytest.skip("COULD NOT EVALUATE: neither the roof nor the plan places a stack")
    W = out["footprint"]["width_ft"]
    # the roof's frame is outside-to-outside (its W stack sits at x = 0 on the outer face and
    # its E at W + 2t), so a coordinate ALONG the wall is the plan's plus one wall thickness;
    # converted here, and stated, rather than absorbed into a tolerance
    t = ST.wall_thickness(out)["exterior_in"] / 12.0
    bad = []
    for p in positions:
        end = "W" if p["x_ft"] < (W + 2 * t) / 2 else "E"
        same_end = [s for s in stacks if s["wall"] == end]
        y_plan = p["y_ft"] - t
        near = min((abs(y_plan - (s["y_ft"] + s["depth_ft"] / 2)) for s in same_end),
                   default=math.inf)
        if near > 1.0:
            bad.append(f"the roof's {end} stack at y={p['y_ft']:.1f} (plan frame {y_plan:.1f}) "
                       f"stands {near:.1f} ft along the wall from the nearest plan stack on that "
                       f"end" + ("" if same_end else " -- the plan draws none there"))
    if len(positions) != len(stacks):
        bad.append(f"the roof stands {len(positions)} stack(s) and the plan draws {len(stacks)}")
    assert not bad, "; ".join(bad)


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_no_window_is_pressed_against_a_stack(sheets, kind, engine):
    """A window and a chimney stack on one wall keep a masonry pier between them. On the
    elevation OQ 85 made the stack's bay blind; the plan seats windows around doors only and
    runs `hearth_pass` last, so a stack can overlap a window by 8 in with nothing to say so."""
    out, _svg, _ = sheets(kind, engine)
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    stacks = _stacks(out)
    if not stacks:
        pytest.skip("COULD NOT EVALUATE: the plan places no stack")
    seen, bad = 0, []
    for lv in _placed_levels(out):
        op = RP.openings_of_level(out, lv)
        for win in op["windows"]:
            for s in stacks:
                if s["wall"] != win["wall"]:
                    continue
                seen += 1
                if s["wall"] in ("E", "W"):
                    slo, shi = s["y_ft"], s["y_ft"] + s["depth_ft"]
                else:
                    slo, shi = s["x_ft"], s["x_ft"] + s["width_ft"]
                wlo, whi = win["at_ft"] - win["width_ft"] / 2, win["at_ft"] + win["width_ft"] / 2
                gap = max(slo - whi, wlo - shi)
                if gap < 1.0:
                    bad.append(f"{lv['id']} {s['wall']} stack {slo:.1f}-{shi:.1f} against a window "
                               f"{wlo:.1f}-{whi:.1f}: {'overlapping by ' + format(-gap, '.2f') if gap < 0 else format(gap, '.2f') + ' ft clear'}")
    if not seen:
        pytest.skip("COULD NOT EVALUATE: no window is placed on a wall that carries a stack")
    assert not bad, (f"on {_engine(out)}, {len(bad)} window(s) are pressed against a stack: "
                     + "; ".join(bad))


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_no_window_sits_inside_a_chimney_breast(sheets, kind, engine):
    """The BREAST is what a reader sees as the chimney in plan -- 4.7 ft of masonry poche on
    the room's wall -- and three functions default to the same point on that wall: the
    breast's centre (`hearths.breast`), a lone window's position (`openings._place_windows`,
    `(k+1)/(n+1)` for n = 1) and the flue axis (`hearths.stack_axes`). A room with one window
    and one position-less hearth on one wall is GUARANTEED a sash dead centre in the breast.
    Measured on `840c7f1`: the dining and library windows lie 100% inside their breasts."""
    out, _svg, _ = sheets(kind, engine)
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    rows, bad = 0, []
    for lv in _placed_levels(out):
        op = RP.openings_of_level(out, lv)
        for r in _rooms(lv):
            for h in (r.get("hearth") or []):
                br = HE.breast(r, h)
                if not br:
                    continue
                rows += 1
                wl = br["wall"]
                blo, bhi = (br["y_ft"], br["y_ft"] + br["depth_ft"]) if wl in ("E", "W") \
                    else (br["x_ft"], br["x_ft"] + br["width_ft"])
                for win in op["windows"]:
                    if win["wall"] != wl:
                        continue
                    wlo, whi = win["at_ft"] - win["width_ft"] / 2, win["at_ft"] + win["width_ft"] / 2
                    shared = min(bhi, whi) - max(blo, wlo)
                    if shared > -1.0:
                        bad.append(f"{r['id']}'s breast on {wl} {blo:.1f}-{bhi:.1f} against a window "
                                   f"{wlo:.1f}-{whi:.1f}: "
                                   + (f"{shared / win['width_ft'] * 100:.0f}% of the sash inside the breast"
                                      if shared > 0 else f"{-shared:.2f} ft clear"))
    if not rows:
        pytest.skip(f"COULD NOT EVALUATE: {kind} states no placed hearth")
    assert not bad, (f"on {_engine(out)}, {len(bad)} window(s) stand in a chimney breast: "
                     + "; ".join(bad))


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_every_declared_door_is_drawable(sheets, kind, engine):
    """A room with walls on four sides and no door is sealed, and the sheet Lucas read in
    Phase 6 had a kitchen whose only drawn door was to the outside. `derive_openings` names
    every declared door the placement leaves no shared wall for; a coherent sheet has none."""
    out, _svg, _ = sheets(kind, engine)
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    declared, bad = 0, []
    for lv in _placed_levels(out):
        op = RP.openings_of_level(out, lv)
        declared += len(op["interior"]) + len(op["exterior"]) + len(op.get("undrawable") or [])
        for u in (op.get("undrawable") or []):
            bad.append(f"{lv['id']} {u.get('from')}-{u.get('to')}: {u.get('reason') or u.get('why') or ''}".rstrip(": "))
    assert declared, "COULD NOT EVALUATE: the plan declares no door"
    assert not bad, (f"on {_engine(out)}, {len(bad)} of {declared} declared doors have no drawable "
                     f"opening -- the rooms behind them are sealed or reached some other way: "
                     + "; ".join(bad[:8]))


# ---------------------------------------------------------------- 7. the bays
def _bearing(out, lv):
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    walls = ST.bearing_lines(ST.wall_lines(_rooms(lv), W, H), fp.get("bay_module_ft") or 10.0)
    return sorted({(w["axis"], round(w["position_ft"], 2)) for w in walls
                   if w["role"] == "interior" and w.get("bearing")})


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_every_upper_bearing_line_stands_on_a_ground_bearing_line(sheets, kind, engine):
    """Bearing continuity: a wall that carries the upper floor stands on a wall below, on the
    bay grid. An upper floor with NO bearing line at all is a 63 ft clear span, which the
    corpus already calls serious; it fails here rather than passing vacuously."""
    out, _svg, _ = sheets(kind, engine)
    levels = _placed_levels(out)
    ground, upper = _bearing(out, levels[0]), _bearing(out, levels[1])
    assert upper, (f"on {_engine(out)} the upper floor carries no bearing line at all "
                   f"(ground has {len(ground)}): every upper wall is a partition and the floor "
                   f"is one clear span")
    bad = []
    for axis, pos in upper:
        near = min((abs(pos - g) for a, g in ground if a == axis), default=math.inf)
        if near > 0.75:
            bad.append(f"upper {axis}={pos:g} ft stands {near:.2f} ft from the nearest ground "
                       f"bearing line")
    assert not bad, (f"on {_engine(out)}, {len(bad)} of {len(upper)} upper bearing lines stand "
                     f"on nothing (ground bearing lines: {ground}): " + "; ".join(bad))


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_the_elevations_openings_are_the_plans_placed_openings(sheets, kind, engine):
    """One bay system. The front elevation draws the openings the plan PLACED on that wall,
    where it placed them -- not a face divided evenly into the plan's bay count with a window
    in each. Compared at the ground storey of the entrance front, centre to centre, 3 in."""
    out, _svg, _ = sheets(kind, engine)
    elev = EL.build_elevation(copy.deepcopy(out))
    assert "error" not in elev, elev.get("error")
    face = elev.get("entrance_face") or (out.get("context") or {}).get("entrance_faces") or "S"
    rects = EL.opening_rects(elev, face)["rects"]
    ground_rects = [r for r in rects if r["storey"] == "ground"]
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    ext = ST.wall_thickness(out)["exterior_in"] / 12.0
    lv = _placed_levels(out)[0]
    op = RP.openings_of_level(out, lv)
    plan = [d["at_ft"] for d in op["exterior"] if d["wall"] == face] + \
           [w["at_ft"] for w in op["windows"] if w["wall"] == face]
    if not plan:
        pytest.skip(f"COULD NOT EVALUATE: the plan places no opening on the {face} front")
    # the face's own left edge is the OUTSIDE of the wall; the plan measures from the clear face
    plan_in = sorted((p + ext) * 12.0 for p in plan) if face in ("S", "E") else \
        sorted((W - p + ext) * 12.0 for p in plan)
    elev_in = sorted(r["cx_in"] for r in ground_rects)
    bad = []
    for p in plan_in:
        near = min((abs(p - e) for e in elev_in), default=math.inf)
        if near > 3.0:
            bad.append(f"plan opening at {p / 12:.2f} ft is {near:.0f} in from the nearest elevation opening")
    if len(plan_in) != len(elev_in):
        bad.append(f"the plan places {len(plan_in)} opening(s) on the {face} front and the "
                   f"elevation draws {len(elev_in)}")
    assert not bad, (f"on {_engine(out)}: " + "; ".join(bad) +
                     f" (elevation centres {[round(e / 12, 2) for e in elev_in]} ft, "
                     f"plan {[round(p / 12, 2) for p in plan_in]} ft)")


# ---------------------------------------------------------------- 3, 5, 8. the furniture
@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_every_furniture_mark_carries_its_name(sheets, kind, engine):
    """A furniture mark is a rectangle with a `<title>` tooltip -- invisible in print, in a
    PDF and on the plate Lucas read. Every placed item is named on the plate the way a
    draughtsman names it: a NUMERAL on (or beside) the mark, and a KEY line carrying that
    numeral and the item's whole name -- set inside the room where a corner holds it, and
    otherwise in the margin schedule under the room's own name, which is a stated refusal
    and not a silence (WP-13.2 ratchets how many rooms take the margin).

    The first cut of this row asked for the name INSIDE the room and refused the margin form;
    the lead admitted it once the slice showed that ten of fifty-six items live in rooms no
    corner of which holds a key at the smallest legible size, and that the margin line names
    the room. A numeral with no key, or a key with no numeral on the mark, still fails."""
    out, svg, _ = sheets(kind, engine)
    plates = _frame(svg)
    texts = [(_attrs(a), re.sub(r"\s+", " ", t.strip().upper())) for a, t in _texts(svg)]
    numerals = [(a["data-key-room"], a["data-key-numeral"], float(a["x"]), float(a["y"]))
                for a, _t in texts if "data-key-numeral" in a]
    want, bad = 0, []
    for i, lv in enumerate(_placed_levels(out)):
        X, Y, _k = _xy(plates[i])
        for r in _rooms(lv):
            rname = re.sub(r"\s+", " ", (r.get("name") or r["id"]).strip().upper())
            # the room's key: its in-room lines, or its margin line under the room's name
            key = [t for a, t in texts if a.get("data-key") == r["id"]]
            key += [t.split(":", 1)[1] for a, t in texts
                    if a.get("class") == "lb" and t.startswith(f"FURNITURE KEY, {rname}") and ":" in t]
            entries = {}
            for line in key:
                for m in re.finditer(r"(?:^|;\s*)(\d+)\s+([^;]+)", line.strip()):
                    entries[m.group(1)] = m.group(2).strip()
            for f in (r.get("furniture_layout") or []):
                if not f.get("marks"):
                    continue
                want += 1
                name = re.sub(r"\s+", " ", f["item"].strip().upper())
                num = next((n for n, nm in entries.items() if name in nm), None)
                if num is None:
                    bad.append(f"{r['id']}: {f['item']!r} is in no key line")
                    continue
                rect = next((m["rect"] for m in f["marks"] if "rect" in m), None)
                if rect:
                    mx, my, mw, mh = rect
                    x0, x1 = X(mx) - 10, X(mx + mw) + 10
                    y0, y1 = Y(my + mh) - 10, Y(my) + 10
                    on_mark = any(rid == r["id"] and n == num and x0 <= nx <= x1 and y0 <= ny <= y1
                                  for rid, n, nx, ny in numerals)
                    if not on_mark:
                        bad.append(f"{r['id']}: {f['item']!r} is keyed {num} and no numeral {num} "
                                   f"stands on its mark")
    if not want:
        pytest.skip("COULD NOT EVALUATE: no furniture is placed on this sheet")
    assert not bad, (f"{len(bad)} of {want} placed furniture items carry no name on the plate: "
                     + "; ".join(bad[:8]))


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_every_furniture_refusal_reaches_the_schedule(sheets, kind, engine):
    """`openings.py` counts the items it could not seat, skipped or never reached, and
    `furniture.py:277` says "a skipped item is a verdict here, never a silence". The counts
    are written to `opening_report` and read by nothing. The schedule says them."""
    out, svg, _ = sheets(kind, engine)
    rep = out.get("opening_report") or {}

    def n(v):
        return len(v) if isinstance(v, (list, dict)) else int(v or 0)
    refused = (n(rep.get("furniture_unplaced")) + sum((rep.get("furniture_skipped") or {}).values())
               + n(rep.get("furniture_not_reached")))
    if not refused:
        pytest.skip("COULD NOT EVALUATE: this placement refused no furniture")
    lines = [ln for ln in _schedule(svg) if "FURNITURE" in ln.upper()]
    assert lines, (f"{refused} furniture item(s) were refused, skipped or never reached on this "
                   f"placement and no line of the schedule says so "
                   f"(unplaced {n(rep.get('furniture_unplaced'))}, skipped "
                   f"{sum((rep.get('furniture_skipped') or {}).values())}, not reached "
                   f"{n(rep.get('furniture_not_reached'))})")


# ---------------------------------------------------------------- 9. the scale
_FIG = re.compile(r'<text class="dm" x="([\d.]+)" y="([\d.]+)" text-anchor="middle" '
                  r'style="font-size:7px;fill:[^"]*">(\d+)</text>')
_VLINE = re.compile(r'<line\b[^>]*\bx1="([-\d.]+)"[^>]*\by1="([-\d.]+)"[^>]*\bx2="([-\d.]+)"[^>]*\by2="([-\d.]+)"')


_BAR = re.compile(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="5"')


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_the_scale_bars_zero_is_a_datum_of_the_plate(sheets, kind, engine):
    """"The bay grid lines are not to scale against the scale bar." The grid IS to scale (the
    next test) and the clear face IS drawn -- the poche is a stroked band, so its inner edge at
    x = 0 is 3 px of ink. What is wrong is where the BAR sits: its zero is at `M + BP`, the
    sheet's hard left margin, which is the plate's own origin and model x = -4.42 ft -- the
    drawn-extent margin, not the clear face, not the masonry face, not anything drawn. It is
    ruled 26 px straight under the plan on the sheet's strongest alignment, so a reader laying
    a straightedge from its 0 to the first bay line reads 13.4 ft against a figure that says
    9. The bar's zero stands on a datum of the plate: the clear face, x = 0."""
    out, svg, _ = sheets(kind, engine)
    plate = _frame(svg)[0]
    X, _Y, k = _xy(plate)
    x0 = X(0.0)
    cells = sorted((float(x), float(w)) for x, _y, w in _BAR.findall(svg))
    assert len(cells) == 4, f"COULD NOT EVALUATE: {len(cells)} scale-bar cells found"
    bar0 = cells[0][0]
    figs = sorted((float(x), int(n)) for x, _y, n in _FIG.findall(svg)
                  if plate["origin_px"][0] <= float(x) <= plate["origin_px"][0] + (out["footprint"]["width_ft"] + 8) * k)
    assert figs, "COULD NOT EVALUATE: no bay figure on the ground plate"
    read = (figs[0][0] - bar0) / k
    assert abs(bar0 - x0) <= 1.0, (
        f"the scale bar's zero is at {bar0:.1f} px and the plate's clear face x=0 is at {x0:.1f} px, "
        f"{(bar0 - x0) / k:+.2f} ft apart; a reader stepping the bar to the first bay figure "
        f"'{figs[0][1]}' reads {read:.1f} ft, {read / figs[0][1] * 100 - 100:+.0f}%")


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_the_scale_bar_recovers_the_bay_grid(sheets, kind, engine):
    """The literal half of the complaint, pinned as true: the grid IS to scale against the
    bar. Both derive from one `scale`, and this is the row that says so with a number."""
    out, svg, _ = sheets(kind, engine)
    plate = _frame(svg)[0]
    k = plate["px_per_ft"]
    cells = [float(w) for w in re.findall(r'<rect x="[\d.]+" y="[\d.]+" width="([\d.]+)" height="5"', svg)]
    assert len(cells) == 4, cells
    assert all(abs(c - 5 * k) < 0.1 for c in cells), f"scale-bar cells {cells} px against {5 * k} for 5 ft"
    xs = sorted({float(x) for x, _y, _n in _FIG.findall(svg)})
    bm = out["footprint"].get("bay_module_ft") or 10
    steps = [round(b - a, 1) for a, b in zip(xs, xs[1:]) if b - a < 2 * bm * k]
    assert steps and all(abs(s - bm * k) < 0.15 for s in steps), (
        f"bay figures {steps} px apart against {bm * k:.1f} for {bm} ft")


# ---------------------------------------------------------------- the title block's honesty
@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_the_plate_does_not_certify_a_placement_whose_objective_did_not_run(sheets, kind, engine):
    """`render_plan.py` prints PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS in
    green on the engine's NAME alone. A FEASIBLE truncation whose compositional objective ran
    for four seconds is not that, and `disclosures.objective_not_run` exists to say so."""
    out, svg, _ = sheets(kind, engine)
    sv = (out.get("geometry_report") or {}).get("solver") or {}
    if sv.get("engine") != "cp-sat":
        pytest.skip(f"COULD NOT EVALUATE: this sheet was drawn by {sv.get('engine')}, which cannot certify")
    lines = _schedule(svg)
    proved = any("PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS" in ln for ln in lines)
    status = str(sv.get("status") or "")
    optimum = status.upper().startswith("OPTIMAL") and sv.get("objective") is not None
    if optimum:
        return   # a proof at the optimum may say so
    assert not proved, (f"the plate certifies the placement in green while the solver's own record "
                        f"reads status={status!r}, objective={sv.get('objective')!r}")
    assert any("OBJECTIVE" in ln.upper() or "FEASIBLE" in ln.upper() for ln in lines), (
        f"status={status!r}: nothing on the plate says the compositional objective did not run")


@pytest.mark.parametrize("kind,engine", SHEETS, ids=IDS)
def test_a_broken_stack_reaches_the_schedule(sheets, kind, engine):
    """The plate prints cuts off the bay line, clear spans and undrawable doors from
    `geometry_report`, and omits `stacking`. A declared stack drawn clear of its room is a
    compromise, and a compromise is counted AND appears on the sheet (OQ 33)."""
    out, svg, _ = sheets(kind, engine)
    _kept, broken, _unjudged = STK.judge(out)
    if not broken:
        pytest.skip("COULD NOT EVALUATE: no declared stack is broken on this placement")
    lines = [ln for ln in _schedule(svg) if "STACK" in ln.upper() and "DECLARED" in ln.upper()]
    assert lines, (f"{len(broken)} declared stack(s) are drawn clear of the room they name "
                   f"({', '.join(b['room'] + '/' + b['over'] for b in broken)}) and no line of the "
                   f"schedule says so")
