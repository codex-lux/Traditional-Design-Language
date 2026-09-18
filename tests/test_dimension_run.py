"""The dimension run under each plate, and the foot of the sheet it pushed down (WP-13.2).

`build/render_plan.py` carried a bay figure ABOVE each plate and nothing under it, so the only
thing a reader could step a dimension off was the scale bar -- whose zero stood at `M + BP`,
the sheet's margin and model x = -4.42 ft, so a straightedge from its 0 to the first bay line
read 13.4 ft against "9". The gate (`tests/test_sheet_coherence.py`) owns that row on four
sheets; this file holds the port of `Sheet.jsx::DimRun` on one plan, fast, both registers:

  * every figure on a run is `_fmt` of the model distance between the ticks it sits between,
    read back from the ink through the plate's own `data-frame` -- a figure computed from the
    wrong stops, or a tick struck from a second affine, is red here;
  * the two extension lines no bay line supplies stand on the CLEAR FACE, x = 0 and x = W,
    and start at the clear face y = 0, not at the plate's drawn margin;
  * the foot is stacked in order and nothing overprints: the runs above the scale bar, the
    bar above the schedule rule, the schedule above the table, the table inside the canvas.
    `tests/test_sheet_canvas.py` reads rects only, so a foot that grew without the canvas
    following would have kept it green while the schedule was set through the table.

It reads the emitted ink and never the code's arithmetic, so a mutation that keeps the sum but
draws the wrong thing is caught. The regexes below select on the `data-run` group each run is
wrapped in, because a selector that matches nothing passes vacuously -- every reader here
asserts its count before it asserts its claim.
"""
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build"))
import modcache  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = "tidewater-georgian-careful"


def _load(name):
    return modcache.load(name, os.path.join(ROOT, "build", f"{name}.py"))


@pytest.fixture(scope="module")
def sheets(tmp_path_factory):
    """(placed record, svg) per register, solved ONCE on the deterministic engine."""
    G, RP = _load("geometry"), _load("render_plan")
    out = G.solve(json.load(open(os.path.join(ROOT, "plans", PLAN + ".json"))), engine="heuristic")
    d = tmp_path_factory.mktemp("dimrun")
    got = {}
    for reg in RP.REGISTERS:
        p = str(d / f"{reg}.svg")
        RP.render(out, p, register=reg)
        got[reg] = (out, open(p, encoding="utf-8").read())
    return got


# ---------------------------------------------------------------- readers of the ink
_RUN = re.compile(r'<g data-run="(\w+)" data-level="([^"]*)">(.*?)</g>', re.S)
_TICK = re.compile(r'<line class="fn" x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"/>')
_FIG = re.compile(r'<text class="dm" x="([-\d.]+)" y="([-\d.]+)" text-anchor="middle"(?: style="([^"]*)")?>([^<]*)</text>')
_GD = re.compile(r'<line class="gd" x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"/>')
_BAR = re.compile(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="5"')
_CANVAS = re.compile(r'<svg[^>]*width="([\d.]+)" height="([\d.]+)"')
_RULE = re.compile(r'<line x1="[\d.]+" y1="([\d.]+)" x2="[\d.]+" y2="[\d.]+" stroke="[^"]*" stroke-width="1"/>')


def _frames(svg):
    m = re.search(r"data-frame='([^']+)'", svg)
    assert m, "the sheet carries no data-frame"
    return {p["id"]: p for p in json.loads(m.group(1))["plates"]}


def _affine(plate):
    ox, oy = plate["origin_px"]
    ax, ay = plate["at_origin_ft"]
    k = plate["px_per_ft"]
    return (lambda v: ox + (v - ax) * k), (lambda v: oy + (ay - v) * k), k


def _runs(svg):
    """{(kind, level): (ticks x sorted, [(x, y, style, label)], run y)}"""
    out = {}
    for kind, level, body in _RUN.findall(svg):
        ticks = sorted((float(x1) + float(x2)) / 2 for x1, _y1, x2, _y2 in _TICK.findall(body))
        figs = [(float(x), float(y), st, lab) for x, y, st, lab in _FIG.findall(body)]
        line = _GD.findall(body)
        assert len(line) == 1, f"run {kind}/{level} draws {len(line)} run lines"
        out[(kind, level)] = (ticks, figs, float(line[0][1]))
    return out


# ---------------------------------------------------------------- the figures
@pytest.mark.parametrize("register", ("presentation", "working"))
def test_every_run_figure_is_the_distance_between_its_ticks(sheets, register):
    out, svg = sheets[register]
    RP = _load("render_plan")
    frames = _frames(svg)
    runs = _runs(svg)
    levels = [lv for lv in out["levels"] if any(r.get("geometry") for r in lv["rooms"])]
    assert len(runs) == 2 * len(levels), f"{len(runs)} runs for {len(levels)} plates"
    W, bm = out["footprint"]["width_ft"], out["footprint"]["bay_module_ft"]
    assert W / bm >= 3, "COULD NOT EVALUATE: fewer than three bays, no interior tick to read"
    checked = 0
    for (kind, level), (ticks, figs, _y) in runs.items():
        X, _Y, k = _affine(frames[level])
        want = [0.0, W] if kind == "overall" else [0.0] + [b * bm for b in range(1, int((W - 0.01) // bm) + 1)] + [W]
        want = [v for i, v in enumerate(want) if i == 0 or v - want[i - 1] > 0.01]
        assert len(ticks) == len(want), f"{kind}/{level}: {len(ticks)} ticks for stops {want}"
        for t, v in zip(ticks, want):
            assert abs(t - X(v)) < 0.2, f"{kind}/{level}: a tick at {t:.1f} px, X({v}) is {X(v):.1f}"
        assert len(figs) == len(ticks) - 1, f"{kind}/{level}: {len(figs)} figures for {len(ticks)} ticks"
        for (x, _y, st, lab), a, b in zip(sorted(figs), ticks, ticks[1:]):
            ft = (b - a) / k
            assert lab == RP._fmt(ft), f"{kind}/{level}: figure {lab!r} over a {ft:.2f} ft segment"
            assert abs(x - (a + b) / 2) < 0.2, f"{kind}/{level}: figure {lab!r} at {x:.1f}, midpoint {(a + b) / 2:.1f}"
            assert "font-size=" not in st, "a size written as an attribute loses to .dm"
            checked += 1
    assert checked >= 8, f"only {checked} figures read"


@pytest.mark.parametrize("register", ("presentation", "working"))
def test_the_figures_are_feet_and_inches_never_decimal(sheets, register):
    _out, svg = sheets[register]
    labs = [lab for _k, _l, body in _RUN.findall(svg) for *_r, lab in _FIG.findall(body)]
    assert labs, "no run figure on the sheet"
    for lab in labs:
        assert re.fullmatch(r"\d+'(-\d+\")?", lab), f"{lab!r} is not a feet-and-inches figure"


# ---------------------------------------------------------------- the extension lines
@pytest.mark.parametrize("register", ("presentation", "working"))
def test_the_extension_lines_stand_on_the_clear_face(sheets, register):
    """The bay lines already run past the plate; the two the grid does not supply, at 0 and
    W, must start at the CLEAR FACE (y = 0) on the clear face's x -- the datum the run and the
    scale bar's zero both stand on -- and reach past the lower run."""
    out, svg = sheets[register]
    frames = _frames(svg)
    runs = _runs(svg)
    W = out["footprint"]["width_ft"]
    vlines = [(float(x1), float(y1), float(x2), float(y2)) for x1, y1, x2, y2 in _GD.findall(svg)
              if abs(float(x1) - float(x2)) < 0.05]
    assert vlines, "no vertical construction line on the sheet"
    seen = 0
    for level, plate in frames.items():
        X, Y, _k = _affine(plate)
        _t, _f, low = runs[("overall", level)]
        for v in (0.0, W):
            here = [l for l in vlines if abs(l[0] - X(v)) < 0.2]
            assert here, f"{level}: no extension line at X({v}) = {X(v):.1f}"
            top = min(min(l[1], l[3]) for l in here)
            bot = max(max(l[1], l[3]) for l in here)
            assert abs(top - Y(0.0)) < 0.2, (
                f"{level}: the extension line at x={v} starts at y={top:.1f}, the clear face is {Y(0.0):.1f}")
            assert bot > low, f"{level}: the extension line at x={v} stops at {bot:.1f}, above the run at {low:.1f}"
            seen += 1
        # and every INTERIOR tick of the bay run stands on a bay line that reaches past it --
        # "the tick on the run stands on the very line the figure above it names"
        ticks, _f, bay_y = runs[("bays", level)]
        assert len(ticks) > 2, f"COULD NOT EVALUATE: {level} has no interior bay tick"
        for t in ticks[1:-1]:
            here = [l for l in vlines if abs(l[0] - t) < 0.2 and min(l[1], l[3]) < Y(0.0) and max(l[1], l[3]) > low]
            assert here, f"{level}: the tick at {t:.1f} px stands on no bay line reaching past the runs"
    assert seen == 2 * len(frames)


def test_a_figure_wider_than_its_segment_is_set_smaller_never_dropped():
    """The shrink branch of `dim_run`, which no shipped plan exercises (a 9 ft bay is 117 px
    and a figure 24). A 1.5 ft segment at 13 px/ft has 11.5 px between its ticks for a 24 px
    figure: the figure is set at the floor, whole, in `style=` -- never as an attribute, which
    `.dm` would beat -- and a segment that fits carries no size at all."""
    RP = _load("render_plan")
    got = "".join(RP.dim_run(lambda v: 100.0 + v * 13.0, 50.0, [0.0, 1.5, 3.0, 12.0]))
    figs = _FIG.findall(got)
    assert [f[3] for f in figs] == ["1'-6\"", "1'-6\"", "9'"], figs
    assert figs[0][2] == f'font-size:{RP.DIM_FIG_FLOOR_PX:.2f}px' == figs[1][2], figs
    assert figs[2][2] == "", "a figure that fits must not carry a size"
    assert 'font-size="' not in got
    assert len(_TICK.findall(got)) == 4 and len(_GD.findall(got)) == 1


# ---------------------------------------------------------------- the foot of the sheet
@pytest.mark.parametrize("register", ("presentation", "working"))
def test_the_foot_is_stacked_in_order_and_nothing_overprints(sheets, register):
    _out, svg = sheets[register]
    cw, ch = (float(v) for v in _CANVAS.search(svg).groups())
    runs = _runs(svg)
    run_low = max(y for _t, _f, y in runs.values())
    bars = sorted({float(y) for _x, y, _w in _BAR.findall(svg)})
    assert len(bars) == 1, f"scale-bar cells on {len(bars)} rows"
    bar_y = bars[0]
    rule = [float(y) for y in _RULE.findall(svg)]
    assert len(rule) == 1, f"{len(rule)} schedule rules"
    # The table's own header is a `class="lb"` text with a fill too, so the schedule is
    # selected by DOCUMENT POSITION: every filled `lb` line emitted before the table header.
    table = re.search(r'<text class="lb"[^>]*y="([\d.]+)"[^>]*>WHAT THE RECORD ASKED FOR', svg)
    end = table.start() if table else len(svg)
    sched = [float(m.group(1)) for m in
             re.finditer(r'<text class="lb" x="[\d.]+" y="([\d.]+)" style="fill:', svg) if m.start() < end]
    assert sched, "no schedule line"
    last_text = max(float(y) for y in re.findall(r'<text[^>]*\by="([-\d.]+)"', svg))
    assert run_low + 4 < bar_y, f"the lower run at {run_low:.1f} is not above the scale bar at {bar_y:.1f}"
    assert bar_y + 5 + 16 < rule[0], f"the scale bar's labels at {bar_y + 16:.1f} reach the schedule rule at {rule[0]:.1f}"
    assert rule[0] < min(sched), f"the schedule rule at {rule[0]:.1f} is below the first schedule line at {min(sched):.1f}"
    if table:
        assert max(sched) < float(table.group(1)), (
            f"the schedule's last line at {max(sched):.1f} is not above the table at {table.group(1)}")
    assert last_text <= ch - 0.5, f"a text at y={last_text:.1f} is outside a canvas {ch:.0f} high"
    assert cw > 0


def test_the_scale_bar_and_the_runs_share_the_ground_plates_clear_face(sheets):
    """The gate owns this on four sheets and two engines; this is its cheap twin on one, so
    the bar's zero and the run's first tick can be mutation-checked in seconds. Both are
    read from the ink against the plate's stated frame, never from each other."""
    _out, svg = sheets["presentation"]
    frames = _frames(svg)
    ground = next(iter(frames.values()))
    X, _Y, _k = _affine(ground)
    cells = sorted(float(x) for x, _y, _w in _BAR.findall(svg))
    assert len(cells) == 4, cells
    ticks, _f, _y = _runs(svg)[("bays", ground["id"])]
    assert abs(cells[0] - X(0.0)) < 0.2, f"the bar's zero is at {cells[0]:.1f}, the clear face at {X(0.0):.1f}"
    assert abs(ticks[0] - X(0.0)) < 0.2, f"the run's first tick is at {ticks[0]:.1f}, the clear face at {X(0.0):.1f}"
