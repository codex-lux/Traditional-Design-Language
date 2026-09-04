"""WP-11.1 — the sheet says what the placement gave up.

`docs/reports/tidewater-layout-diagnosis-2026-09-04.md` J1: the plate read

    PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS

over a placement that had set aside SIXTEEN of the record's declared exterior walls, both ends of
the centre passage among them, with `objective: null`. Four more facts the record already carried
— the set-aside walls, the objective that did not run, twenty-seven undrawn window units and
thirty transfer beams — had no reader anywhere in the tree.

These tests are written against `build/disclosures.banner`, on RECORDS BUILT HERE, rather than by
mutating source and re-rendering: a fixture that states its own solver record can assert both
directions of every line (present when the record says so, ABSENT when it does not), and the
absent half is the half that catches a line hard-coded to fire. Each was mutation-checked while
being written — remove the clause under test and the test goes red — and the two that pin a real
placement say so in their own names.
"""
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

DISC = modcache.load("disclosures", os.path.join(ROOT, "build", "disclosures.py"))
RP = modcache.load("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))


def ids(lines):
    return [ln["id"] for ln in lines]


def text_of(lines, lid):
    for ln in lines:
        if ln["id"] == lid:
            return ln["text"]
    return None


def _plan(**over):
    """A minimal placed record. Every field a disclosure reads is stated here, so a test can
    take one away and watch its line disappear."""
    p = {
        "id": "fixture", "name": "A Fixture", "style": "tidewater-georgian",
        "levels": [{"id": "ground", "index": 0, "rooms": [
            {"id": "hall", "name": "Hall", "width_ft": 10, "length_ft": 20,
             "exterior_walls": ["S", "N"],
             "windows": [{"wall": "S", "count": 2}, {"wall": "N", "count": 1}],
             "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 10, "depth_ft": 20, "area_sf": 200}},
        ]}],
        "footprint": {"width_ft": 30, "depth_ft": 20},
        "geometry_report": {"relaxations": {"count": 0}, "vertical": [],
                            "solver": {"engine": "cp-sat", "objective": 12.5,
                                       "downgraded_wall_pins": []}},
        "opening_report": {"windows_unplaced": 0},
    }
    p.update(over)
    return p


# ------------------------------------------------------------------ the walls set aside
class TestTheWallsSetAside:
    def test_a_downgraded_pin_is_named_with_its_room(self):
        p = _plan()
        p["geometry_report"]["solver"]["downgraded_wall_pins"] = ["L0 hall S", "L0 hall N"]
        lines = DISC.banner(p)
        t = text_of(lines, "walls-set-aside")
        assert t is not None, "two set-aside pins and the plate says nothing"
        assert "2 DECLARED EXTERIOR WALLS SET ASIDE" in t
        assert "HALL" in t, "the line has to name the room, not only the count"

    def test_no_pins_means_no_line_at_all(self):
        """The half that catches a line hard-coded to fire. A placement that gave nothing up
        must produce NO line here — a '0 walls set aside' would train a reader to skip it."""
        assert text_of(DISC.banner(_plan()), "walls-set-aside") is None

    def test_the_engine_line_says_how_many_of_the_record_survived(self):
        p = _plan()
        p["geometry_report"]["solver"]["downgraded_wall_pins"] = ["L0 hall S"]
        t = text_of(DISC.banner(p), "engine")
        # the fixture declares two exterior walls and one was dropped
        assert t == "PLACEMENT PROVED (CP-SAT) AGAINST 1 OF THE RECORD'S 2 DECLARED EXTERIOR WALLS"

    def test_an_unrelaxed_proof_still_says_it_proved_the_record(self):
        assert text_of(DISC.banner(_plan()), "engine") == \
            "PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS"

    def test_the_engine_line_tone_moves_with_the_relaxation(self):
        """A warning drawn in the reassuring colour is a warning the sheet does not give
        (WP-6.1's own finding, in the line that carries this package's subject)."""
        clean = [ln for ln in DISC.banner(_plan()) if ln["id"] == "engine"][0]
        p = _plan()
        p["geometry_report"]["solver"]["downgraded_wall_pins"] = ["L0 hall S"]
        relaxed = [ln for ln in DISC.banner(p) if ln["id"] == "engine"][0]
        assert clean["tone"] == "verd" and relaxed["tone"] == "copper"


# ------------------------------------------------------------------ the objective
class TestTheObjectiveThatDidNotRun:
    def test_a_null_objective_on_cp_is_disclosed(self):
        p = _plan()
        p["geometry_report"]["solver"]["objective"] = None
        t = text_of(DISC.banner(p), "objective")
        assert t and "COMPOSITIONAL OBJECTIVE DID NOT RUN" in t

    def test_an_objective_that_ran_says_nothing(self):
        assert text_of(DISC.banner(_plan()), "objective") is None

    def test_the_hill_climb_never_takes_this_line(self):
        """THE ONE THAT COST AN HOUR. The heuristic writes no `objective` at all, so
        `objective is None` is true of it — and the first version of the instrument duly
        published 'the objective did not run' about the ONE engine that always runs it: the
        hill-climb's score IS its objective, summed over every candidate it looks at."""
        p = _plan()
        p["geometry_report"]["solver"] = {"engine": "heuristic"}
        assert text_of(DISC.banner(p), "objective") is None


# ------------------------------------------------------------------ the windows
class TestTheWindowsNotDrawn:
    def test_the_count_and_the_reasons(self):
        p = _plan()
        p["opening_report"]["windows_unplaced"] = 2
        p["levels"][0]["rooms"][0]["windows"][0]["unplaced"] = {
            "reason": "the placement puts this room on no such boundary wall"}
        t = text_of(DISC.banner(p), "windows")
        assert t and t.startswith("2 OF 3 DECLARED WINDOW UNIT(S) NOT DRAWN")
        assert "ON NO SUCH WALL" in t, "the reason is grouped and shortened, not dropped"

    def test_nothing_unplaced_means_no_line(self):
        assert text_of(DISC.banner(_plan()), "windows") is None

    def test_a_parameterised_reason_is_one_bucket_and_not_a_second_count(self):
        """`openings.py` writes one reason with a count already inside it — "1 of 2 unit(s) had
        no clear run left on this wall" — and counting by sentence put a second number in front
        of it: "2 1 OF 2 UNIT(S) HAD NO CLEAR RUN…", which reads as a typo and is really two
        counts in a row. Found on the bench's own payload, not in a test."""
        p = _plan()
        p["opening_report"]["windows_unplaced"] = 3
        p["levels"][0]["rooms"][0]["windows"][0]["unplaced"] = {
            "reason": "1 of 2 unit(s) had no clear run left on this wall"}
        p["levels"][0]["rooms"][0]["windows"][1]["unplaced"] = {
            "reason": "2 of 3 unit(s) had no clear run left on this wall"}
        t = text_of(DISC.banner(p), "windows")
        assert "NO CLEAR RUN LEFT ON THE WALL" in t
        assert "UNIT(S) HAD" not in t, t
        # both records land in ONE bucket carrying the disclosure's own count
        assert t.count("NO CLEAR RUN LEFT ON THE WALL") == 1, t

    def test_the_denominator_counts_units_not_records(self):
        """A window record carries a `count`; the line is about units of glass, because that
        is what a reader counts on an elevation."""
        p = _plan()
        p["opening_report"]["windows_unplaced"] = 1
        p["levels"][0]["rooms"][0]["windows"][0]["unplaced"] = {"reason": "x"}
        assert "OF 3 DECLARED" in text_of(DISC.banner(p), "windows")


# ------------------------------------------------------------------ the transfers
class TestTheTransferBeams:
    def test_the_count_is_read_out_of_the_sentence(self):
        p = _plan()
        p["geometry_report"]["vertical"] = [
            "30 upper wall line(s) do not continue to a wall below; each is a transfer beam.",
            "Chamber Bath sits over no wet room; its stack has nowhere to land."]
        t = text_of(DISC.banner(p), "transfers")
        assert t and t.startswith("30 UPPER WALL LINE(S)")

    def test_a_vertical_report_with_no_transfer_sentence_says_nothing(self):
        p = _plan()
        p["geometry_report"]["vertical"] = ["Chamber Bath sits over no wet room."]
        assert text_of(DISC.banner(p), "transfers") is None


# ------------------------------------------------------------------ style against title
class TestTheStyleTheSheetJudgedBy:
    STYLES = {"tidewater-georgian": {"name": "Tidewater Georgian"},
              "palladian": {"name": "Palladian"},
              "english-palladian": {"name": "English Palladian"}}

    def test_a_title_naming_another_style_is_disclosed(self):
        """The sheet Lucas read was titled 'Tidewater Georgian, five bays, carefully planned'
        and carried the style slot `palladian` — a different node, a different cascade, a
        different fault set, and no line anywhere said so."""
        p = _plan(style="english-palladian", name="Tidewater Georgian, five bays")
        t = text_of(DISC.banner(p, styles=self.STYLES), "style")
        assert t and "JUDGED AS ENGLISH-PALLADIAN" in t and "TIDEWATER GEORGIAN" in t

    def test_a_title_that_agrees_says_nothing(self):
        p = _plan(style="tidewater-georgian", name="Tidewater Georgian, five bays")
        assert text_of(DISC.banner(p, styles=self.STYLES), "style") is None

    def test_a_title_naming_no_style_says_nothing(self):
        """Most plan titles name no style. A line that fired on silence would fire on almost
        every sheet and be ignored by the second week."""
        p = _plan(style="tidewater-georgian", name="A house for the Robinsons")
        assert text_of(DISC.banner(p, styles=self.STYLES), "style") is None

    def test_a_parti_that_does_not_list_the_style_is_disclosed(self):
        p = _plan(style="tidewater-georgian", name="A house", parti="shotgun-linear")
        partis = {"shotgun-linear": {"styles": ["creole-cottage-vernacular"]}}
        t = text_of(DISC.banner(p, styles=self.STYLES, partis=partis), "style")
        assert t and "SHOTGUN-LINEAR" in t

    def test_a_parti_that_lists_the_style_says_nothing(self):
        p = _plan(style="tidewater-georgian", name="A house", parti="p")
        partis = {"p": {"styles": ["tidewater-georgian"]}}
        assert text_of(DISC.banner(p, styles=self.STYLES, partis=partis), "style") is None


# ------------------------------------------------------------------ the plate itself
class TestTheDrawnPlate:
    """The lines have to reach the SVG, and no line may leave the canvas. The second is the
    general form of the defect the first draft of this package introduced: the undrawn-window
    line ran 160 characters and the canvas cut it mid-word — a disclosure the sheet does not
    make, produced by the package sent to make the sheet disclose."""

    def _svg(self, tmp_path, plan):
        out = str(tmp_path / "sheet.svg")
        RP.render(plan, out)
        return open(out, encoding="utf-8").read()

    def _rows(self, svg):
        return re.findall(r'class="lb"[^>]*>([^<]*)<', svg)

    def test_no_banner_row_leaves_the_canvas(self, tmp_path):
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        placed = GEO.solve(plan, None, 60, engine="heuristic")
        svg = self._svg(tmp_path, placed)
        width = float(re.search(r'width="(\d+)"', svg).group(1))
        for row in self._rows(svg):
            # `pad` is 42 either side; the `.lb` advance is the renderer's own constant
            assert 42 + len(row) * RP.LB_ADVANCE_PX <= width, \
                f"this row runs off a {width:.0f} px plate: {row!r}"

    def test_a_long_line_wraps_rather_than_truncating(self):
        long = "A " + "VERY LONG DISCLOSURE " * 12
        rows = RP._wrap_banner(long, 400)
        assert len(rows) > 1
        # nothing may be lost: every word of the original survives, in order
        assert " ".join(r.strip() for r in rows).split() == long.split()

    def test_the_record_table_names_every_diverged_room(self, tmp_path):
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        placed = GEO.solve(plan, None, 60, engine="heuristic")
        svg = self._svg(tmp_path, placed)
        diverged = [d for lv in placed["levels"] for d in RP.declared_divergence(lv["rooms"])]
        assert diverged, "the fixture is blind: this placement diverged from nothing"
        assert "WHAT THE RECORD ASKED FOR" in svg
        names = [d["name"] for d in diverged]
        for d in diverged:
            label = d["name"] if names.count(d["name"]) == 1 else f'{d["name"]} ({d["id"]})'
            assert f"{label}: drawn" in svg, f'{label} is marked ∗ and not in the table'

    def test_two_rooms_with_one_name_are_told_apart_in_the_table(self, tmp_path):
        """Two rooms called "Closet" produced two rows a reader could not attribute, differing
        only in figures. Same class as WP-9.4's two rooms sharing an id, on the surface."""
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        placed = GEO.solve(plan, None, 60, engine="heuristic")
        diverged = [d for lv in placed["levels"] for d in RP.declared_divergence(lv["rooms"])]
        names = [d["name"] for d in diverged]
        dupes = {n for n in names if names.count(n) > 1}
        assert dupes, "the fixture is blind: no two diverged rooms share a name on this plan"
        svg = self._svg(tmp_path, placed)
        for d in diverged:
            if d["name"] in dupes:
                assert f'{d["name"]} ({d["id"]})' in svg

    def test_the_table_prints_the_declared_figure_not_only_the_percentage(self, tmp_path):
        """A percentage says how far the placement went; only the figure says what to build."""
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        placed = GEO.solve(plan, None, 60, engine="heuristic")
        svg = self._svg(tmp_path, placed)
        assert re.search(r'drawn [^,]+, record [^(]+\(', svg)

    def test_nothing_the_table_draws_leaves_the_canvas(self, tmp_path):
        """A fixed allowance under the plates is how a third of an upper floor came to be drawn
        outside this canvas once already (WP-9.6), so the table's height is computed.

        THE FIRST VERSION OF THIS TEST WAS BLIND AND THE MUTATION FOUND IT. It compared the
        canvas height with the table against the height without, which passes with the growth
        term deleted — because a plan with no diverged rooms also loses a BANNER line, and 14
        px of banner is enough to keep `tall > short` true. Two causes, one comparison, and the
        one under test contributed nothing. The property that actually matters is direct: no
        mark the sheet draws may sit below the canvas it declares."""
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        placed = GEO.solve(plan, None, 60, engine="heuristic")
        svg = self._svg(tmp_path, placed)
        height = float(re.search(r'height="(\d+)"', svg).group(1))
        ys = [float(y) for y in re.findall(r'<text[^>]*\sy="([\d.]+)"', svg)]
        assert ys, "the fixture is blind: this sheet drew no text at all"
        assert max(ys) <= height, (
            f"a label sits at y={max(ys):.0f} on a canvas {height:.0f} px tall")
        # and the guard must be able to fail: the table has to reach the bottom region, or a
        # canvas sized for the plates alone would satisfy this vacuously
        assert max(ys) > height - 60, (
            "the lowest mark is far above the canvas foot — this assertion would hold with no "
            "table drawn at all, which is not what it is for")

# ------------------------------------------------------------------ the proving engine
class TestOnTheProvingEngine:
    """The lines this package exists for only appear on a CP placement, so these run the CP
    engine or report COULD NOT EVALUATE. They never fall back to the hill-climb and call it the
    proof: that substitution is exactly what the sheet was doing in prose."""

    def _cp(self):
        try:
            from ortools.sat.python import cp_model  # noqa: F401
        except Exception:
            pytest.skip("COULD NOT EVALUATE — ortools is absent, so there is no proof to "
                        "disclose. Measuring the hill-climb here and calling it the proof is "
                        "the substitution this package removed from the plate.")
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        # 120 s, not the 25 s default, and the number is a MEASUREMENT rather than a margin:
        # after WP-11.2 moved this plan to seven bays of 9 ft the CP engine returns UNKNOWN at
        # 25 s, reaches phase A at 60 and phase B at 120. A test that took the default would
        # skip on a real regression and read as a machine being slow.
        out = GEO.solve(plan, None, 250, engine="cp", time_limit_s=120)
        if "error" in out:
            pytest.skip(f'COULD NOT EVALUATE — CP-SAT returned no placement in 120 s on this '
                        f'machine: {out["error"]}. Not a pass: the disclosure this asserts is '
                        f'about a proof, and there is no proof to read.')
        return out

    def test_the_shipped_tidewater_plan_discloses_its_set_aside_walls(self):
        placed = self._cp()
        pins = (placed["geometry_report"]["solver"].get("downgraded_wall_pins") or [])
        lines = DISC.banner(placed)
        if not pins:
            assert text_of(lines, "walls-set-aside") is None
            return
        t = text_of(lines, "walls-set-aside")
        assert t and str(len(pins)) in t
        # and the engine line must no longer claim the whole record
        assert text_of(lines, "engine") != \
            "PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS"
