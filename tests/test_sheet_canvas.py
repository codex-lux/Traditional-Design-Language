"""Every mark a sheet draws must be INSIDE the canvas it declares.

WP-9.6: `render_plan.render()` reassigned `top` -- the sheet's top margin, read by both
`total_h` and by `oy = top + extra_top` once per level -- to a room-label local inside the
level loop. The first plate was placed from the real margin and every plate after it from
wherever the last room's label block began. On plans/tidewater-georgian-careful.json the
ground plate sat at y=134 and the upper at y=378.2, running to y=658 on a canvas sized 498:
a third of the upper floor outside the viewBox, not drawn, and the two levels no longer
aligned. Lucas found it by looking at the sheet; nothing in the suite could.

Two guards, and their sensitivities differ -- stated because a reader will otherwise assume
the first one caught this:

  test_every_level_plate_shares_one_top_edge   catches THIS bug. Reverting the rename turns
                                               it red (spec-builder-colonial, plates at
                                               134.0 and 152.1).
  test_no_drawn_rect_leaves_the_declared_canvas  does NOT catch it on `engine="heuristic"`,
                                               where the drift is only ~18 px and stays
                                               inside the sheet's 84 px of bottom padding.
                                               It fires when the canvas is undersized by
                                               more than that padding (mutation-checked at
                                               -100 and -160 px) and it is what would have
                                               caught the 160 px overflow the `auto`
                                               placement actually produced.

Both are kept because they fail on different mutations. The general one is deliberately
"no drawn rect leaves the declared canvas" rather than a pin on this plan's numbers,
because the defect was a coordinate escaping its own sizing arithmetic and the next one
will be too.
"""
import json, re, glob, os, importlib.util, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = _mod("build/geometry.py", "geometry_canvas")
RP = _mod("build/render_plan.py", "render_plan_canvas")

CANVAS = re.compile(r'<svg[^>]*width="([\d.]+)" height="([\d.]+)"')
RECT = re.compile(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" height="([\d.]+)"')
PLATE = re.compile(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" height="([\d.]+)" '
                   r'fill="#0F2536"')


def _sheet(name, tmp_path):
    plan = json.loads((ROOT / "plans" / (name + ".json")).read_text())
    solved = G.solve(json.loads(json.dumps(plan)), engine="heuristic")
    out = str(tmp_path / (name + ".svg"))
    RP.render(solved, out)
    return pathlib.Path(out).read_text()


def _plans():
    # `sorted(` on the same line as the read -- tests/test_determinism.py checks per line.
    return sorted(os.path.basename(p)[:-5]
                  for p in sorted(glob.glob(str(ROOT / "plans" / "*.json"))))


def test_no_drawn_rect_leaves_the_declared_canvas(tmp_path):
    offenders = []
    checked = 0
    for name in _plans():
        try:
            svg = _sheet(name, tmp_path)
        except SystemExit:
            continue                      # no geometry on this plan; render refuses, correctly
        cm = CANVAS.search(svg)
        assert cm, f"{name}: the sheet declares no canvas at all"
        cw, ch = float(cm.group(1)), float(cm.group(2))
        checked += 1
        for x, y, w, h in RECT.findall(svg):
            x, y, w, h = float(x), float(y), float(w), float(h)
            if x < -0.5 or y < -0.5 or x + w > cw + 0.5 or y + h > ch + 0.5:
                offenders.append(f"{name}: rect ({x:.1f},{y:.1f},{w:.1f}x{h:.1f}) "
                                 f"reaches ({x + w:.1f},{y + h:.1f}) outside {cw:.0f}x{ch:.0f}")
                break                     # one per plan is enough to name it
    assert checked, "no plan rendered — this test would pass vacuously"
    assert not offenders, ("a sheet draws outside the canvas it declares, so the mark is "
                           "simply not there for the reader:\n  " + "\n  ".join(offenders))


def test_every_level_plate_shares_one_top_edge(tmp_path):
    """The levels of one house are drawn side by side and must line up.

    `oy` is computed identically for every level, so any disagreement means something
    reassigned the margin between passes -- which is exactly what happened.
    """
    multi = 0
    for name in _plans():
        try:
            svg = _sheet(name, tmp_path)
        except SystemExit:
            continue
        tops = sorted({round(float(y), 1) for _x, y, _w, _h in PLATE.findall(svg)})
        if len(PLATE.findall(svg)) < 2:
            continue
        multi += 1
        assert len(tops) == 1, (
            f"{name}: the level plates start at different heights {tops} — they are drawn "
            f"side by side and share one top margin, so this means the margin was "
            f"reassigned between passes")
    assert multi, "no multi-level plan rendered — this test would pass vacuously"
