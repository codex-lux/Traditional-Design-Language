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
        # `status` is stated because WP-13.2's engine line READS it: a proof is a status
        # beginning OPTIMAL with an objective, and a fixture that omitted it would be claiming
        # the green line off the engine's name, which is the defect that package removed.
        "geometry_report": {"relaxations": {"count": 0}, "vertical": [],
                            "solver": {"engine": "cp-sat", "status": "OPTIMAL", "objective": 12.5,
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


# ------------------------------------------- the engine's name is not a proof (WP-13.2)
GREEN = "PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS"


class TestTheEngineLineDoesNotCertifyOnTheName:
    """The gate (`tests/test_sheet_coherence.py`) found the green line over a record reading
    `status: FEASIBLE — kept polish from the heuristic hint (best of 2 hard-valid placements)`,
    `objective: 518.9`. What that record proves is that the hard set is satisfiable; PROVED
    AGAINST THE RECORD'S DECLARED FACTS is what a reader takes it for. The green line prints only
    on OPTIMAL with an objective and no pin set aside; everything else prints the status it has."""

    REFERENCE = "FEASIBLE — kept polish from the heuristic hint (best of 2 hard-valid placements)"

    def _line(self, **solver):
        p = _plan()
        p["geometry_report"]["solver"].update(solver)
        return [ln for ln in DISC.banner(p) if ln["id"] == "engine"][0]

    def test_the_reference_sheets_own_record_is_not_certified(self):
        ln = self._line(status=self.REFERENCE, objective=518.9)
        assert ln["text"] != GREEN
        assert ln["tone"] == "copper"
        assert "NOT PROVED AT THE OPTIMUM" in ln["text"], ln
        assert "FEASIBLE" in ln["text"], "the status the record has is printed, verbatim"

    def test_a_null_objective_on_an_optimal_hard_only_status_is_not_certified(self):
        """`OPTIMAL (hard-only) — kept hard-only phase A` begins with OPTIMAL and proves nothing
        about the composition: `objective_not_run` prints beside it and the green line does not."""
        p = _plan()
        p["geometry_report"]["solver"].update(
            status="OPTIMAL (hard-only) — kept hard-only phase A", objective=None)
        lines = DISC.banner(p)
        assert text_of(lines, "engine") != GREEN
        assert "HARD-ONLY" in text_of(lines, "engine")
        assert text_of(lines, "objective") and "DID NOT RUN" in text_of(lines, "objective")

    def test_a_record_with_no_status_is_unjudged_and_not_proved(self):
        p = _plan()
        del p["geometry_report"]["solver"]["status"]
        ln = [ln for ln in DISC.banner(p) if ln["id"] == "engine"][0]
        assert ln["text"] != GREEN and ln["tone"] == "copper"
        assert "NOT RECORDED" in ln["text"], ln

    def test_optimal_with_an_objective_and_nothing_set_aside_is_the_green_line(self):
        ln = self._line(status="OPTIMAL", objective=12.5)
        assert ln["text"] == GREEN and ln["tone"] == "verd"

    def test_the_set_aside_walls_are_still_named_on_an_unproved_placement(self):
        ln = self._line(status=self.REFERENCE, objective=518.9, downgraded_wall_pins=["L0 hall S"])
        assert "AGAINST 1 OF THE RECORD'S 2 DECLARED EXTERIOR WALLS" in ln["text"], ln
        assert "NOT PROVED AT THE OPTIMUM" in ln["text"]

    def test_the_hill_climb_line_is_untouched(self):
        p = _plan()
        p["geometry_report"]["solver"] = {"engine": "heuristic"}
        assert text_of(DISC.banner(p), "engine") == "PLACEMENT SEARCHED, NOT PROVED — HILL-CLIMB"


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


# ------------------------------------------------------ the declared stacks (WP-13.2)
class TestTheDeclaredStacks:
    """The plate printed cuts, spans and undrawable doors from `geometry_report` and omitted
    `stacking`; three stacks drawn clear of the room they name reached no line."""

    def _tally(self, kept=(), broken=(), unjudged=()):
        def e(pair):
            return {"room": pair[0], "over": pair[1], "field": "stacks_over", "level": 1}
        st = {"claims": len(kept) + len(broken) + len(unjudged),
              "kept": [e(k) for k in kept], "broken": [e(b) for b in broken],
              "unjudged": [dict(e(u), reason="this room is not placed") for u in unjudged],
              "note": "x"}
        p = _plan()
        p["geometry_report"]["stacking"] = st
        return p

    def test_a_broken_stack_is_named_in_iron(self):
        ln = [ln for ln in DISC.banner(self._tally(kept=[("a", "b")], broken=[("landing", "stair")]))
              if ln["id"] == "stacking"][0]
        assert ln["tone"] == "iron"
        assert ln["text"].startswith("1 OF 2 DECLARED STACK(S) DRAWN CLEAR OF THE ROOM THEY NAME")
        assert "LANDING/STAIR" in ln["text"]

    def test_stacks_that_all_land_say_so_in_verd(self):
        ln = [ln for ln in DISC.banner(self._tally(kept=[("a", "b"), ("c", "d")]))
              if ln["id"] == "stacking"][0]
        assert ln["tone"] == "verd" and ln["text"].startswith("2 OF 2 DECLARED STACK(S) LAND")

    def test_the_unjudged_count_travels_because_unjudged_is_not_kept(self):
        t = text_of(DISC.banner(self._tally(kept=[("a", "b")], unjudged=[("c", "d")])), "stacking")
        assert "1 COULD NOT BE EVALUATED" in t, t
        t = text_of(DISC.banner(self._tally(unjudged=[("c", "d")])), "stacking")
        assert "COULD NOT BE EVALUATED" in t and "NONE IS KNOWN TO LAND" in t, t

    def test_a_record_with_no_claim_takes_no_line(self):
        assert text_of(DISC.banner(self._tally()), "stacking") is None
        assert text_of(DISC.banner(_plan()), "stacking") is None

    def test_the_rule_block_alone_without_the_leafs_tally_takes_no_line(self):
        """`solve_heuristic` writes `claimed`/`rule` and `_disclose` merges the leaf's
        `claims`/`kept`/`broken` over it; a record carrying only the first has no verdict to
        print, and printing "0 OF 5" from `claimed` would be a count of nothing judged."""
        p = _plan()
        p["geometry_report"]["stacking"] = {"claimed": 5, "rule": "charge"}
        assert text_of(DISC.banner(p), "stacking") is None


# ------------------------------------------------------ the fires not drawn (WP-13.2)
class TestTheFiresNotDrawn:
    """A stated fire the placement could not put on a flue, and a stated flue left with no
    stack. Both verdicts were in `plan.hearths.unplaced` and reached the working register's
    field caption and nothing else; the browser walk met it as a stack count of 1 against a pin
    of 2 with no line naming the missing west stack."""

    def _hearths(self, breasts=(), flues=(), generic=False, judged=3):
        un = [{"what": f"the breast of {r}'s hearth", "room": r, "hearth_index": 0,
               "reason": "the record puts this fire on the room's W wall and the placement puts "
                         "that wall 18.0 ft inboard of the element's W face",
               "rule": "hearths.breast", "grade": "reading"} for r in breasts]
        un += [{"what": f"the stack for flue '{f}'", "flue": f, "wall": "W", "serves": ["a", "b"],
                "reason": "none of the 2 fire(s) the record puts on this flue stands on a "
                          "boundary wall on this placement", "rule": "hearths.flues",
                "grade": "reading"} for f in flues]
        if generic:
            un.append({"what": "the stacks", "reason": "no canonical hearth position names "
                       "which face of the end wall the mass stands on",
                       "rule": "th-which-side-of-the-end-wall", "grade": "reading"})
        p = _plan()
        p["hearths"] = {"stacks": [], "unplaced": un,
                        "breasts": [{"room": f"r{i}", "judged": True, "drawn": True}
                                    for i in range(judged)],
                        "flues": []}
        return p

    def test_a_refused_breast_and_a_refused_flue_are_named_in_iron(self):
        ln = [ln for ln in DISC.banner(self._hearths(breasts=["drawing", "dining"],
                                                      flues=["west-stack"], judged=3))
              if ln["id"] == "fires"][0]
        assert ln["tone"] == "iron"
        assert ln["text"].startswith("2 OF 3 STATED FIRE(S) NOT DRAWN — DRAWING, DINING"), ln["text"]
        assert "STACK WEST-STACK NOT PLACED (2 FIRE(S), NONE ON A BOUNDARY WALL)" in ln["text"], ln["text"]
        assert ln["detail"]["stated"] == 3 and len(ln["detail"]["breasts"]) == 2

    def test_a_house_that_states_no_fire_takes_no_line(self):
        """`hearth_pass` refuses "the stacks" wholesale on a plan whose massing cannot be read
        or that states no hearth -- 15 of the 16 shipped plans on the search engine. That entry
        names no room and no flue, and a FIRES NOT DRAWN line over it would be a refusal about
        fires nobody stated: the fake-unjudged collapse WP-12.6 met on dormers."""
        assert text_of(DISC.banner(self._hearths(generic=True, judged=0)), "fires") is None
        assert text_of(DISC.banner(_plan()), "fires") is None
        assert text_of(DISC.banner(_plan(hearths={"stacks": [], "unplaced": []})), "fires") is None

    def test_fires_all_drawn_take_no_line_because_the_poche_is_the_disclosure(self):
        assert text_of(DISC.banner(self._hearths(judged=3)), "fires") is None

    def test_the_generic_refusal_beside_a_real_one_does_not_inflate_the_count(self):
        t = text_of(DISC.banner(self._hearths(breasts=["dining"], generic=True, judged=2)), "fires")
        assert t.startswith("1 OF 2 STATED FIRE(S) NOT DRAWN — DINING"), t
        assert "STACK" not in t

    def test_the_line_follows_the_stacks_line_in_the_banner(self):
        p = self._hearths(breasts=["dining"], judged=1)
        p["geometry_report"]["stacking"] = {"claims": 1, "kept": [{"room": "a", "over": "b"}],
                                            "broken": [], "unjudged": []}
        order = ids(DISC.banner(p))
        assert order.index("fires") == order.index("stacking") + 1, order


# ------------------------------------------------- the furniture not drawn (WP-13.2)
class TestTheFurnitureNotDrawn:
    def test_the_three_counts_are_named_apart(self):
        p = _plan()
        p["opening_report"].update(furniture_unplaced=6,
                                   furniture_skipped={"fg-not-an-object": 20, "fg-too-thin-to-draw": 2},
                                   furniture_not_reached=11)
        t = text_of(DISC.banner(p), "furniture")
        assert t.startswith("39 FURNITURE ITEM(S) NOT DRAWN — 6 UNPLACED, 22 SKIPPED"), t
        assert "FG-NOT-AN-OBJECT 20" in t and t.endswith("11 NOT REACHED"), t

    def test_the_counts_are_read_defensively_int_list_or_dict(self):
        p = _plan()
        p["opening_report"].update(furniture_unplaced=["a", "b"], furniture_skipped=["x"],
                                   furniture_not_reached="3")
        t = text_of(DISC.banner(p), "furniture")
        assert t.startswith("6 FURNITURE ITEM(S) NOT DRAWN — 2 UNPLACED, 1 SKIPPED, 3 NOT REACHED"), t

    def test_nothing_refused_means_no_line(self):
        p = _plan()
        p["opening_report"].update(furniture_unplaced=0, furniture_skipped={}, furniture_not_reached=0)
        assert text_of(DISC.banner(p), "furniture") is None
        assert text_of(DISC.banner(_plan()), "furniture") is None


# --------------------------------------------------- the residual void (WP-13.2)
class TestTheResidualVoid:
    def _tf(self, ground_sf, upper_sf=0.0, strips=None):
        def lv(i, name, sf):
            return {"level": i, "id": name, "uncovered_sf": sf,
                    "blocks": [{"block": "main", "uncovered_sf": sf,
                                "strips": strips if sf else []}]}
        p = _plan()
        p["geometry_report"]["type_facts"] = {"tiling": {
            "step_ft": 0.1, "levels": [lv(0, "ground", ground_sf), lv(1, "upper", upper_sf)],
            "uncovered_sf": ground_sf + upper_sf}}
        return p

    def test_a_level_with_floor_in_no_room_is_named_in_iron_with_its_worst_strip(self):
        lines = [ln for ln in DISC.banner(self._tf(26.5, strips=[{"area_sf": 20.5}, {"area_sf": 6.0}]))
                 if ln["id"].startswith("void")]
        assert [ln["id"] for ln in lines] == ["void-ground"]
        assert lines[0]["tone"] == "iron"
        assert lines[0]["text"].startswith("26.5 SF OF GROUND IS NO ROOM — 2 STRIPS"), lines[0]
        assert "WORST 20.5 SF" in lines[0]["text"]

    def test_two_levels_with_voids_are_two_lines(self):
        lines = [ln for ln in DISC.banner(self._tf(26.5, 48.8, strips=[{"area_sf": 1.0}]))
                 if ln["id"].startswith("void")]
        assert [ln["id"] for ln in lines] == ["void-ground", "void-upper"]

    def test_every_level_tiling_is_said_in_verd_not_left_silent(self):
        """Evaluated-and-tiled must be tellable from never-evaluated on the plate."""
        lines = [ln for ln in DISC.banner(self._tf(0.0)) if ln["id"].startswith("void")]
        assert len(lines) == 1 and lines[0]["tone"] == "verd"
        assert lines[0]["text"].startswith("EVERY PLACED LEVEL TILES ITS BLOCK")

    def test_the_block_absent_means_no_line_never_a_zero(self):
        assert not [ln for ln in DISC.banner(_plan()) if ln["id"].startswith("void")]
        p = _plan()
        p["geometry_report"]["type_facts"] = {"tiling": None}
        assert not [ln for ln in DISC.banner(p) if ln["id"].startswith("void")]


# ---------------------------------------------- the clear spans, moved here (WP-13.2)
class TestTheClearSpans:
    def test_three_states_and_the_zero_is_printed(self):
        p = _plan()
        p["geometry_report"]["span_capacity"] = {"over_capacity": 3, "worst_span_ft": 35.5}
        ln = [ln for ln in DISC.banner(p) if ln["id"] == "span"][0]
        assert ln["tone"] == "iron" and ln["text"].startswith(
            "3 CLEAR SPAN(S) OVER THE FRAMING CAPACITY, WORST 35.5 FT")
        p["geometry_report"]["span_capacity"] = {"over_capacity": 0}
        ln = [ln for ln in DISC.banner(p) if ln["id"] == "span"][0]
        assert ln["tone"] == "verd" and ln["text"].startswith("0 CLEAR SPAN(S)")
        p["geometry_report"]["span_capacity"] = {"over_capacity": None}
        ln = [ln for ln in DISC.banner(p) if ln["id"] == "span"][0]
        assert ln["tone"] == "copper" and "NOT EVALUATED" in ln["text"]

    def test_a_record_with_no_report_at_all_takes_no_span_line(self):
        p = _plan()
        del p["geometry_report"]
        assert text_of(DISC.banner(p), "span") is None


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

    def test_the_plate_prints_the_banner_and_not_its_own_copy_of_it(self, tmp_path):
        """WP-13.2. `render_plan.py` imported `disclosures` and spelled two of its lines itself,
        which is how the plate printed PLACEMENT PROVED on the engine's name for a fortnight
        after this module had stopped saying it. Every record-derived line `banner()` returns
        must be a row of the schedule, and the engine row must be `banner()`'s engine text and
        not another one -- the mutation that reinstates the plate's own copy goes red here."""
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        placed = GEO.solve(plan, None, 60, engine="heuristic")
        svg = self._svg(tmp_path, placed)
        rows = " ".join(self._rows(svg))
        lines = DISC.banner(placed)
        assert {ln["id"] for ln in lines} >= {"relaxations", "span", "stacking", "furniture",
                                              "engine"}, [ln["id"] for ln in lines]
        for ln in lines:
            assert ln["text"] in rows, f"the plate does not print the banner's {ln['id']} line"
        # and the engine row is the module's, not a second spelling: with the search there is
        # exactly one row naming the placement's engine and it is banner()'s own
        engine_rows = [r for r in self._rows(svg) if r.startswith("PLACEMENT ")]
        assert engine_rows == [text_of(lines, "engine")], engine_rows

    def test_the_presentation_register_does_not_claim_a_mark_it_does_not_draw(self, tmp_path):
        """`banner(marked=...)`: the diverged line says MARKED ∗ only where the ∗ is on the
        field, which the presentation register does not draw."""
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        placed = GEO.solve(plan, None, 60, engine="heuristic")
        out = str(tmp_path / "pres.svg")
        RP.render(placed, out, register="presentation")
        pres = [r for r in self._rows(open(out, encoding="utf-8").read()) if "DRAWN AT A SIZE" in r]
        work = [r for r in self._rows(self._svg(tmp_path, placed)) if "DRAWN AT A SIZE" in r]
        assert pres and work, "the fixture is blind: no diverged room on this placement"
        assert "MARKED ∗" not in pres[0] and "MARKED ∗" in work[0]

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


# ------------------------------------------------- the stack's plan size is a judgment (WP-12.9)
class TestTheStackPlanJudgment:
    """The chimney's 22 in is a decision the corpus declines to settle, drawn on three surfaces.

    `brick-course`'s rule for it carries `judgment: true` and says why -- twenty-two inches on
    the default coursing is between sizes, and a mason will build 18 or 27. `render_elevation.py`
    has printed that in the plate's legend since WP-5.11 and `build/scene.py` refuses to draw a
    solid over it at all (WP-12.6). THE PLAN SHEET DREW THE SQUARE AND CALLED IT A MEASUREMENT --
    its tooltip read "chimney stack, 22.0 in square" and no line anywhere said the number was not
    settled, on the one surface of the three where a reader is choosing a brick.

    The root was one field: the baked snapshot of that rule in `kits/georgian-colonial-american
    .kit.json` carried `kind: derived` and NO judgment flag, and `check_kits.py` re-derived only
    the VALUE, so nothing could see it. Measured over the 93 snapshots matchable to a source
    rule, 13 dropped a `judgment: true` and ZERO carried one.
    """

    def _placed(self, **stack):
        sk = {"wall": "W", "side": "exterior", "stack_plan_in": 22.0,
              "stack_plan_judgment": True,
              "stack_plan_basis": "chimney plan dimensions are whole bricks; a stack is 2 x 3",
              "x_ft": 0.0, "y_ft": 10.0, "width_ft": 1.83, "depth_ft": 1.83}
        sk.update(stack)
        return _plan(hearths={"stacks": [sk]})

    def test_the_line_names_the_figure_and_says_it_is_not_a_measurement(self):
        t = text_of(DISC.banner(self._placed()), "stack-judgment")
        assert t is not None, "a stack flagged a judgment produces no line at all"
        assert "22.0" in t, t
        assert "JUDGMENT, NOT A MEASUREMENT" in t, t

    def test_the_basis_travels_with_the_flag(self):
        """A judgment with no basis named is what this corpus forbids one step further than a
        figure with no source -- the shape the two-Phase-11 merge met when the hearth tooltip's
        `Morris 1734, judgment` became a bare `judgment`."""
        t = text_of(DISC.banner(self._placed()), "stack-judgment")
        assert "WHOLE BRICKS" in t, t
        # cut at a clause and MARK the elision, which is WP-11.5's rule: OQ 18's first version
        # cut a quoted basis at a hard 150 characters and landed mid-word 148 times.
        assert t.endswith("…"), f"the basis was elided and the line does not say so: {t}"
        assert "2 X 3" not in t, f"the clause cut did not happen: {t}"

    def test_a_basis_that_needs_no_cutting_carries_no_elision_mark(self):
        """The other half, without which the mark above could be unconditional."""
        t = text_of(DISC.banner(self._placed(stack_plan_basis="whole bricks")), "stack-judgment")
        assert t.endswith("WHOLE BRICKS"), t
        assert "…" not in t, t

    def test_a_stack_whose_size_the_corpus_HAS_settled_takes_no_line(self):
        """The absent half, and it is the half that catches a line hard-coded to fire. A stack
        drawn at a figure the corpus settled is a measurement and must say nothing."""
        assert text_of(DISC.banner(self._placed(stack_plan_judgment=False)), "stack-judgment") is None

    def test_a_house_with_no_stack_takes_no_line(self):
        assert text_of(DISC.banner(_plan()), "stack-judgment") is None
        assert text_of(DISC.banner(_plan(hearths={"stacks": []})), "stack-judgment") is None

    def test_a_judgment_with_no_figure_takes_no_line_rather_than_printing_None(self):
        """`stack_plan_in` absent is the record declining to state a size at all. Printing
        "None SQUARE" would be a disclosure that says nothing and looks like one that does."""
        assert text_of(DISC.banner(self._placed(stack_plan_in=None)), "stack-judgment") is None

    def test_the_count_is_the_stacks_that_carry_the_judgment_and_not_every_stack(self):
        p = _plan(hearths={"stacks": [
            dict(self._placed()["hearths"]["stacks"][0]),
            dict(self._placed()["hearths"]["stacks"][0], wall="E"),
            dict(self._placed()["hearths"]["stacks"][0], wall="N", stack_plan_judgment=False)]})
        t = text_of(DISC.banner(p), "stack-judgment")
        assert t.startswith("2 STACKS"), f"three stacks, two of them judgments: {t}"
