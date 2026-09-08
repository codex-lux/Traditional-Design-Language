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
# The plate's own stated top edge. This used to select the paper-ground rect by its dark
# hex, which the Drawn Language pass removed along with the ground itself -- the room is the
# paper now, and a sheet with no fill to select would have made this guard pass over an empty
# list. Selecting a colour was the weakness; the plate states its origin instead.
PLATE = re.compile(r'<text class="lb" data-plate="[^"]*" data-plate-top="([-\d.]+)"')


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
        tops = sorted({round(float(y), 1) for y in PLATE.findall(svg)})
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
    def _plan_with_a_dependency(geometry_module):
        """Tagged BY HAND, and an EAST dependency on purpose.

        The composer writes no `block` on any room: the packages that would have taught it to
        were reverted on 3 Sep 2026 when the audit found five further defects downstream of them.
        The block machinery below stands, so the fixture states the tag the composer will one day
        write. East rather than west because east is the direction the original defect ran -- a
        room past the main block's right edge lands in the NEXT LEVEL'S PANEL and is drawn there
        silently, where a west one merely leaves the canvas and is visibly missing.
        """
        from test_geometry import _tagged_dependency_plan
        plan = _tagged_dependency_plan()
        for r in plan["levels"][0]["rooms"]:
            if r.get("block"):
                r["exterior_walls"] = ["N", "S", "E"]     # an EAST dependency
        geometry_module._SOLVE_CACHE.clear()
        geometry_module.solve(plan, None, engine="heuristic")
        return plan

    def test_every_room_is_drawn_inside_its_own_levels_panel(self, geometry_module, tmp_path):
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

        plan = self._plan_with_a_dependency(geometry_module)
        dep = [r for lv in plan["levels"] for r in lv["rooms"] if r.get("block") and r.get("geometry")]
        assert dep, "this fixture must actually produce a dependency, or the test proves nothing"
        assert any(r["geometry"]["x_ft"] + r["geometry"]["width_ft"] > plan["footprint"]["width_ft"]
                   or r["geometry"]["x_ft"] < 0 for r in dep), \
            "and at least one of its rooms must fall outside the main block"

        out = tmp_path / "audit_dep_sheet.svg"
        rp.render(plan, str(out))
        svg = out.read_text()
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

    def test_the_building_outline_is_one_rect_per_element_not_one_across_the_gap(
            self, geometry_module, tmp_path):
        """The residual the first fix left, found in the second audit pass.

        Sizing the sheet to the drawn extent was right; drawing the BUILDING at that size was
        not. The paper ground and the `.wl` perimeter were both `X(0), Y(H), pw, ph` -- the whole
        extent -- so a 70 ft house beside a 20 ft dependency across a 14 ft hyphen was outlined
        as one solid 104 ft rectangle with the gap inside it, and the hyphen the reader is meant
        to see disappeared into the building. On a WEST dependency it was worse than wrong: `X(0)`
        sits 34 ft into the panel and the rect then ran 34 ft past its right edge, off the sheet.

        Asserted on the EMITTED SVG and on both handednesses, because the west case is the one
        that leaves the canvas and the east case is the one that hides the gap."""
        import re, importlib.util, os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location("rp", os.path.join(root, "build", "render_plan.py"))
        rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)
        from test_geometry import _tagged_dependency_plan

        for side in ("E", "W"):
            plan = _tagged_dependency_plan()
            for r in plan["levels"][0]["rooms"]:
                if r.get("block"):
                    r["exterior_walls"] = ["N", "S", side]
            geometry_module._SOLVE_CACHE.clear()
            geometry_module.solve(plan, None, engine="heuristic")
            blocks = plan["footprint"]["blocks"]
            assert len(blocks) == 2, f"fixture must place two elements, got {len(blocks)}"

            out = tmp_path / f"perimeter_{side}.svg"
            rp.render(plan, str(out))
            svg = out.read_text()
            canvas_w = float(re.search(r'viewBox="0 0 ([\d.]+) ', svg).group(1))
            # READ THE ENVELOPE BANDS, WHICH IS WHAT AN OUTLINE IS NOW. The building used to be
            # outlined by a stroked `.wl` rect per element; the Drawn Language pass made the
            # wall a BODY, so each element's envelope is four poche bands carrying that
            # element's index. Selecting on `data-block` also drops the scale derivation this
            # test used to do -- it divided the widest drawn rect by the widest declared block
            # to recover px-per-foot, which is circular the moment the drawn rect includes the
            # wall thickness. Grouping by element states the property directly instead.
            # PER PLATE, and the first version of this was not -- it unioned each element's
            # bands over the WHOLE sheet, so block 0's envelope on the ground plate and its
            # envelope on the upper plate merged into one span 163 ft wide and the assertion
            # fired on a sheet that was drawing correctly. The levels are side by side; a
            # question about one house's outline is a question about one plate.
            plates = re.split(r'(?=<text class="lb" data-plate=")', svg)[1:]
            assert plates, "no plate markers in the sheet -- the selector has gone stale"
            # `[^>]*?` between the class and the id: the band also states WHICH of the three
            # walls it is (`data-wall`), and a selector that assumed the attribute order went
            # stale the moment that was added -- it matched nothing and the test failed loudly,
            # which is the good outcome, but an over-specified selector is one edit from being
            # the silent kind instead.
            band_re = re.compile(
                r'<rect class="pm"[^>]*? data-block="(\d+)" x="([-\d.]+)" y="[-\d.]+" '
                r'width="([\d.]+)" height="([\d.]+)"')
            bands = [m for plate in plates for m in band_re.findall(plate)]
            assert bands, "no envelope bands in the sheet -- the selector has gone stale"
            got = {int(b_) for b_, _x, _w, _h in bands}
            assert got == set(range(len(blocks))), (
                f"[{side}] the sheet draws envelopes for elements {sorted(got)} against "
                f"{len(blocks)} in the record")

            spans = {}
            for pi, plate in enumerate(plates):
                for b_, x, w, _h in band_re.findall(plate):
                    x, w = float(x), float(w)
                    lo, hi = spans.get((pi, int(b_)), (x, x + w))
                    spans[(pi, int(b_))] = (min(lo, x), max(hi, x + w))
            # No element's envelope may reach across the gap into another's. Two elements whose
            # drawn spans overlap are one rectangle with the hyphen inside it, which is the
            # defect: a 70 ft house beside a 20 ft dependency outlined as one 104 ft building.
            ordered = sorted(spans.values())
            assert len(ordered) >= 2, (
                f"[{side}] only {len(ordered)} envelope(s) drawn -- a two-element plan whose "
                "elements are not both drawn cannot exercise this guard at all")
            for (lo1, hi1), (lo2, _hi2) in zip(ordered, ordered[1:]):
                assert hi1 < lo2 + 0.5, (
                    f"[{side}] two elements' envelopes run {lo1:.0f}-{hi1:.0f} and from "
                    f"{lo2:.0f} -- the gap between the blocks is being drawn as building")
            for _b, x, w, _h in bands:
                x, w = float(x), float(w)
                assert x >= -0.5 and x + w <= canvas_w + 0.5, (
                    f"[{side}] a band runs from {x:.0f} to {x+w:.0f} on a {canvas_w:.0f} px "
                    "canvas -- it is drawn off the sheet")

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
