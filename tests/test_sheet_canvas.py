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


class TestADependencyIsDrawnInsideItsOwnPanel:
    """OQ 40, found by the adversarial audit of the change that introduced it (3 Sep 2026).

    `render_plan.render` laid out one panel per level, each `footprint.width_ft * scale` wide,
    and mapped a room at model x to `pad + x*scale`. `footprint.width_ft` is the MAIN BLOCK. So
    a garage dependency placed at model x = 84 landed at SVG x = 630 in a ground panel ending at
    532 -- the garage, its mudroom and the breakfast room were drawn ON TOP OF THE UPPER FLOOR'S
    PLATE. Nothing clipped and nothing complained: the marks were inside the canvas, in the wrong
    panel. A west dependency at negative x would have gone off the left edge of the sheet
    entirely.

    The drawn extent is now separate from the main block's, which `derive_openings` still needs
    unchanged -- widening W there would put windows on interior walls."""

    @staticmethod
    def _plan_with_a_dependency(compose_module, geometry_module):
        import json, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        brief = json.load(open(os.path.join(root, "briefs", "family-georgian.json")))
        plan, _log, _p = compose_module.instantiate("centre-passage-double-pile", brief)
        geometry_module._SOLVE_CACHE.clear()
        geometry_module.solve(plan, compose_module.C, engine="heuristic")
        return plan

    def test_every_room_is_drawn_inside_its_own_levels_panel(self, compose_module, geometry_module):
        """READS THE EMITTED SVG, and the first version of this test did not.

        That version recomputed the panel width from the plan and then checked the plan against
        it -- so it was asserting its own arithmetic, and reverting the fix in render_plan.py
        left it GREEN. It was exactly the vacuous guard this audit was hunting for, written by
        the audit. What discriminates is where the marks actually landed, so this reads the
        room-name labels out of the SVG and solves the panel geometry from the canvas the
        renderer itself chose."""
        import re, importlib.util, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location("rp", os.path.join(root, "build", "render_plan.py"))
        rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)

        plan = self._plan_with_a_dependency(compose_module, geometry_module)
        dep = [r for lv in plan["levels"] for r in lv["rooms"] if r.get("block") and r.get("geometry")]
        assert dep, "this fixture must actually produce a dependency, or the test proves nothing"
        assert any(r["geometry"]["x_ft"] + r["geometry"]["width_ft"] > plan["footprint"]["width_ft"]
                   or r["geometry"]["x_ft"] < 0 for r in dep), \
            "and at least one of its rooms must fall outside the main block"

        out = os.path.join("/tmp", "audit_dep_sheet.svg")
        rp.render(plan, out)
        svg = open(out).read()
        canvas_w = float(re.search(r'viewBox="0 0 ([\d.]+) ', svg).group(1))

        # Solve the panel width from the renderer's OWN canvas: total = 2*pad + n*panel + (n-1)*gap.
        n_levels = len([lv for lv in plan["levels"] if any("geometry" in r for r in lv["rooms"])])
        pad, gap = 42, 58
        panel_w = (canvas_w - 2 * pad - (n_levels - 1) * gap) / n_levels
        ground_right = pad + panel_w

        # Where the marks actually are: every room-name label the sheet drew, by x.
        labels = {t.strip(): float(x) for x, t in
                  re.findall(r'class="nm"[^>]*x="([-\d.]+)"[^>]*>([^<]+)<', svg)}
        assert labels, "no room labels in the sheet -- the selector has gone stale and this test is vacuous"
        for r in dep:
            name = (r.get("name") or r["id"])
            hits = [v for k, v in labels.items() if k.lower().startswith(name.lower()[:10])]
            if not hits:
                continue
            assert min(hits) <= ground_right + 0.5, (
                f"{r['id']} is labelled at SVG x {min(hits):.0f}, past the ground panel's right "
                f"edge at {ground_right:.0f} -- it is drawn on another level's plate")
            assert min(hits) >= pad - 0.5, f"{r['id']} is drawn off the left edge of the sheet"

    def test_a_one_block_sheet_is_unchanged_by_the_drawn_extent(self, geometry_module):
        """The main block is still the main block: with no dependency the drawn extent equals it
        and the sheet must be byte-identical to what it always was."""
        import json, os, importlib.util
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location("rp", os.path.join(root, "build", "render_plan.py"))
        rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)
        plan = json.load(open(os.path.join(root, "plans", "tidewater-georgian-careful.json")))
        geometry_module._SOLVE_CACHE.clear()
        geometry_module.solve(plan, engine="heuristic")
        pts = [r["geometry"] for lv in plan["levels"] for r in lv["rooms"] if r.get("geometry")]
        assert min(g["x_ft"] for g in pts) >= 0.0
        assert max(g["x_ft"] + g["width_ft"] for g in pts) <= plan["footprint"]["width_ft"] + 0.01, (
            "this plan is one rectangle; if that stops being true the byte-identity claim is void")
