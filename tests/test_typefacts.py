"""WP-13.2 -- the residual void is measured on the record, once, for both engines.

`build/typefacts.py` is a LEAF that reads a placed record and writes `geometry_report.type_facts`
from `geometry._disclose`, the one function both record writers call. Its first fact is TILING:
the floor of each placed level's massing block(s) lying inside no room rectangle, rasterised the
way the gate rasterises it. Lucas saw the prover leave a powder room open to the drawing room;
the record said nothing. Every guard here was mutation-checked with the mutation asserted to
have landed before its colour was believed.
"""
import copy
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

TF = modcache.load("typefacts", os.path.join(ROOT, "build", "typefacts.py"))
GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))


def _room(rid, x, y, w, h, **more):
    r = {"id": rid, "type": "parlor", "width_ft": w, "length_ft": h,
         "geometry": {"x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": h, "area_sf": w * h}}
    r.update(more)
    return r


def _plan(ground, upper=None, W=20.0, H=10.0, blocks=None):
    levels = [{"id": "ground", "index": 0, "rooms": ground}]
    if upper is not None:
        levels.append({"id": "upper", "index": 1, "rooms": upper})
    fp = {"width_ft": W, "depth_ft": H}
    if blocks:
        fp["blocks"] = blocks
    return {"id": "t", "levels": levels, "footprint": fp}


# ------------------------------------------------------------------ the leaf stays a leaf
def test_the_leaf_imports_no_sibling():
    """It is loaded by geometry.py, which loads plan_check.py, which will read this block back.
    One sibling import here closes a cycle. Same guard as build/stacking.py's and storeys.py's."""
    src = open(os.path.join(ROOT, "build", "typefacts.py"), encoding="utf-8").read()
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            assert "build" not in s or s.startswith("from __future__"), \
                f"typefacts.py must stay a leaf; found {s!r}"
    for bad in ("modcache", "_mod(", "_load(", "import geometry", "import plan_check",
                "import elements", "import stacking"):
        assert bad not in src, f"build/typefacts.py refers to {bad!r}; it is a LEAF"


# ------------------------------------------------------------------ the raster
class TestUncovered:
    def test_a_block_its_rooms_tile_has_no_residual_void(self):
        sf, strips = TF.uncovered([(0, 0, 10, 10), (10, 0, 10, 10)], (0, 0, 20, 10))
        assert sf == 0.0 and strips == []

    def test_a_strip_between_two_rooms_is_measured_and_located(self):
        """A 0.92 ft gap is what `_absorb` calls honest empty floor and what a reader sees as a
        room open to its neighbour; here it is 0.9 ft wide over the full 10 ft depth."""
        sf, strips = TF.uncovered([(0, 0, 9.1, 10), (10.0, 0, 10, 10)], (0, 0, 20, 10))
        assert sf == 9.0, sf
        assert len(strips) == 1, strips
        s = strips[0]
        assert (s["x_ft"], s["y_ft"], s["width_ft"], s["depth_ft"]) == (9.1, 0.0, 0.9, 10.0), s
        assert s["area_sf"] == 9.0

    def test_two_separate_holes_are_two_strips(self):
        """Two 1 ft bands that share no cell edge. (The first version of this fixture put a
        band against a slot and they met at a cell corner -- one L-shaped strip of 20 sf, which
        the code correctly reported and the test had not expected.)"""
        rects = [(0, 0, 10, 4), (0, 5, 10, 5), (10, 0, 10, 9)]
        sf, strips = TF.uncovered(rects, (0, 0, 20, 10))
        assert sf == 20.0, sf
        assert [s["area_sf"] for s in strips] == [10.0, 10.0]
        assert {(s["x_ft"], s["y_ft"]) for s in strips} == {(0.0, 4.0), (10.0, 9.0)}

    def test_two_holes_that_touch_are_one_strip(self):
        rects = [(0, 0, 10, 4), (0, 5, 10, 5), (11, 0, 9, 10)]      # a band meeting a slot
        sf, strips = TF.uncovered(rects, (0, 0, 20, 10))
        assert sf == 20.0 and len(strips) == 1 and strips[0]["area_sf"] == 20.0

    def test_a_room_outside_the_block_paints_nothing_and_one_straddling_paints_its_overlap(self):
        sf, _ = TF.uncovered([(30, 0, 5, 5)], (0, 0, 20, 10))
        assert sf == 200.0
        sf, _ = TF.uncovered([(-5, 0, 25, 10)], (0, 0, 20, 10))
        assert sf == 0.0

    def test_it_counts_the_way_the_gate_counts(self):
        """`tests/test_sheet_coherence.py::_uncovered` is the gate's own raster. The record
        and the gate must agree to the cell, or a sheet could pass one and fail the other."""
        spec = importlib.util.spec_from_file_location(
            "gate_for_typefacts", os.path.join(ROOT, "tests", "test_sheet_coherence.py"))
        sys.path.insert(0, os.path.join(ROOT, "tests"))
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        rooms = [_room("a", 0, 0, 9.13, 10), _room("b", 10.07, 0, 9.93, 10)]
        block = (0, 0, 20, 10)
        mine, _ = TF.uncovered([(r["geometry"]["x_ft"], r["geometry"]["y_ft"],
                                 r["geometry"]["width_ft"], r["geometry"]["depth_ft"]) for r in rooms],
                               block)
        theirs = gate._uncovered(rooms, block)
        assert abs(mine - theirs) < 1e-9, (mine, theirs)
        assert mine > 0, "the fixture is blind: no residual void to agree about"


# ------------------------------------------------------------------ the fact on the record
class TestTiling:
    def test_a_record_with_no_footprint_is_unjudged_not_zero(self):
        p = _plan([_room("a", 0, 0, 20, 10)])
        del p["footprint"]
        assert TF.tiling(p) is None
        assert TF.report(p)["tiling"] is None

    def test_a_record_with_no_placed_level_is_unjudged_not_zero(self):
        p = _plan([{"id": "a", "type": "parlor", "width_ft": 20, "length_ft": 10}])
        assert TF.tiling(p) is None

    def test_a_level_that_tiles_reads_zero_and_says_so(self):
        t = TF.tiling(_plan([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)]))
        assert t["uncovered_sf"] == 0.0
        assert [lv["uncovered_sf"] for lv in t["levels"]] == [0.0]
        assert "tiles its block" in t["note"]

    def test_a_level_with_a_hole_names_the_level_and_locates_the_strip(self):
        t = TF.tiling(_plan([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)],
                            upper=[_room("c", 0, 0, 20, 9.4)]))
        by = {lv["id"]: lv for lv in t["levels"]}
        assert by["ground"]["uncovered_sf"] == 0.0
        assert by["upper"]["uncovered_sf"] == 12.0, by["upper"]
        strip = by["upper"]["blocks"][0]["strips"][0]
        assert (strip["y_ft"], strip["depth_ft"], strip["width_ft"]) == (9.4, 0.6, 20.0)
        assert t["uncovered_sf"] == 12.0

    def test_a_reserved_void_paints_as_a_room(self):
        """OQ 55's courtyard is a rectangle the record NAMES and draws open; this fact is about
        floor nobody declared."""
        court = _room("court", 5, 0, 10, 10, type="courtyard")
        court["geometry"]["void"] = {"heated": False, "roofed": False}
        t = TF.tiling(_plan([_room("a", 0, 0, 5, 10), court, _room("b", 15, 0, 5, 10)]))
        assert t["uncovered_sf"] == 0.0

    def test_an_element_with_no_room_on_a_level_has_no_floor_there(self):
        """WP-11.9's rule, without importing `elements`: the upper storey of a single-storey
        wing is not 300 sf of residual void."""
        blocks = [{"id": "main", "role": "main", "x_ft": 0, "y_ft": 0, "width_ft": 20, "depth_ft": 10},
                  {"id": "dep", "role": "dependency", "x_ft": -30, "y_ft": 0, "width_ft": 30, "depth_ft": 10}]
        p = _plan([_room("a", 0, 0, 20, 10), _room("k", -30, 0, 30, 10)],
                  upper=[_room("c", 0, 0, 20, 10)], blocks=blocks)
        t = TF.tiling(p)
        by = {lv["id"]: lv for lv in t["levels"]}
        assert [b["block"] for b in by["ground"]["blocks"]] == ["main", "dependency"]
        assert [b["block"] for b in by["upper"]["blocks"]] == ["main"], by["upper"]
        assert t["uncovered_sf"] == 0.0
        # and the premise: with the skip deleted the wing WOULD read as 300 sf of void
        sf, _ = TF.uncovered([(0, 0, 20, 10)], (-30, 0, 30, 10))
        assert sf == 300.0


# ------------------------------------------------------------------ both record writers carry it
class TestItIsOnTheRecordForBothEngines:
    def test_disclose_writes_type_facts_beside_the_stacking_tally(self):
        """`_disclose` is the one function both writers call (OQ 40's disclosure shipped in one
        of them for two phases). The block goes in there and nowhere else."""
        p = _plan([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 9.5, 10)])
        p["geometry_report"] = {}
        GEO._disclose(p)
        tf = p["geometry_report"]["type_facts"]
        assert tf["tiling"]["uncovered_sf"] == 5.0, tf
        # AND THE VERDICT BESIDE IT (WP-13.4). `_disclose` used to write
        # `rep["type_facts"] = TF.report(plan)` inline; the measurement and the decision drawn
        # from it are now written together by `TF.judge`, so a caller cannot get one without
        # the other -- `corpus._placed`'s short circuit and `export_dxf._solved_copy`'s are the
        # two other callers, and each is handed a record that never reaches a record writer.
        assert p["geometry_report"]["refused"] is None or \
            p["geometry_report"]["refused"]["facts"], "a refusal that names no fact"
        src = open(os.path.join(ROOT, "build", "geometry.py"), encoding="utf-8").read()
        # ONE WRITER, read as a property rather than pinned as a literal: the assignment moved
        # into the leaf, so what this file guards is that `geometry.py` never assigns the key
        # itself and reaches it through the one function.
        assert 'rep["type_facts"] =' not in src, (
            "geometry.py assigns type_facts directly again -- it and `refused` are written "
            "together by typefacts.judge, and a second writer of either is how the record "
            "comes to carry a measurement with no verdict")
        assert src.count("TF.judge(plan)") == 2, (
            "TF.judge is called from `_disclose` and from `_refuse` and nowhere else")
        body = src[src.index("def _disclose(plan):"):]
        body = body[:body.index("\ndef ")]
        assert "TF.judge(plan)" in body

    def test_the_shipped_search_placement_carries_the_fact(self):
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        GEO._SOLVE_CACHE.clear()
        out = GEO.solve(copy.deepcopy(plan), None, 250, engine="heuristic")
        t = out["geometry_report"]["type_facts"]["tiling"]
        assert t and len(t["levels"]) == 2
        # the search tiles exactly by construction (WP-9.2: the slicer tiles); a hole here is
        # the engine changing, not the fact
        assert t["uncovered_sf"] == 0.0, t


# ================================================================== WP-13.3: the other three facts
# The leaf may import nothing, and `geometry._disclose` hands it the plan alone. So each fact is
# either READ off a verdict the record already carries (stacks, span capacity) or measured by a
# TRANSCRIPTION of the one spelling (the shared-edge test, the bay-grid test, the flue-wall
# table), and every transcription is held to its original here -- the defaults are read off the
# originals' own signatures, the tables compared entry for entry, and the line sets compared on
# every shipped plan. Every guard below was mutation-checked with the mutation asserted to land.
import inspect  # noqa: E402

ST = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))
HE = modcache.load("hearths", os.path.join(ROOT, "build", "hearths.py"))
STK = modcache.load("stacking", os.path.join(ROOT, "build", "stacking.py"))
DISC = modcache.load("disclosures", os.path.join(ROOT, "build", "disclosures.py"))
# `sorted(` ON THE SAME LINE AS EACH READ. The outer `sorted()` below already made this list
# deterministic, and `tests/test_determinism.py::test_corpus_globs_are_sorted` reads LINE BY
# LINE -- a sort that opens on the line above reads to it as an unsorted glob, and it went red
# on this file from `af8acff` until WP-13.6 met it. The value is unchanged either way: the
# outer sort is over the whole concatenation. tests/test_furniture_drawn.py carries the same
# note for the same reason; write for the reader you have.
PLANS = sorted(
    [os.path.join(ROOT, "plans", f) for f in sorted(os.listdir(os.path.join(ROOT, "plans")))
     if f.endswith(".json")]
    + [os.path.join(ROOT, "plans", "reference", f)
       for f in sorted(os.listdir(os.path.join(ROOT, "plans", "reference"))) if f.endswith(".json")])


def _solved(path):
    plan = json.load(open(path, encoding="utf-8"))
    GEO._SOLVE_CACHE.clear()
    return GEO.solve(copy.deepcopy(plan), None, 250, engine="heuristic")


class TestTheTranscriptionsAreHeldToTheirOneSpelling:
    def test_the_flue_wall_table_is_hearths_own_table(self):
        """FLUE_WALLS is `hearths.HEARTH_RULES[...]["walls"]`, entry for entry, both ways: a row
        added to the table and not the leaf would silently make every fire under it unjudged."""
        assert set(TF.FLUE_WALLS) == set(HE.HEARTH_RULES), \
            (set(TF.FLUE_WALLS) ^ set(HE.HEARTH_RULES))
        for k, rule in HE.HEARTH_RULES.items():
            assert tuple(TF.FLUE_WALLS[k]) == tuple(rule["walls"]), k

    def test_the_tolerances_are_read_off_the_originals_signatures(self):
        """The shared-edge tolerance is `_shared_segment`'s `tol` default, the grid tolerance is
        `bearing_lines`' `tol` default, and the minimum shared run is the literal in
        `_shared_segment`'s body. If structure.py moves one, this fails naming it."""
        assert TF.SHARED_EDGE_TOL_FT == inspect.signature(ST._shared_segment).parameters["tol"].default
        assert TF.BEARING_GRID_TOL_FT == inspect.signature(ST.bearing_lines).parameters["tol"].default
        src = inspect.getsource(ST._shared_segment)
        assert f"if hi - lo > {TF.MIN_SHARED_RUN_FT:g}" in src, src
        assert TF.TILING_TOL_SF == DISC.TILED_SF

    def test_the_bearing_lines_agree_with_the_gates_reader_on_every_shipped_plan(self):
        """The leaf's transcription against the original, on the interior bearing lines of every
        placed level of every shipped plan on the deterministic engine. Line for line, not a
        count -- WP-11.15's phantom span had the same count.

        **THE CONTROL WAS A FOURTH SPELLING OF THE RULE AND IT HAD NEVER BEEN TAUGHT ABOUT
        MASSING ELEMENTS (WP-13.5).** It read
        `ST.bearing_lines(ST.wall_lines(rooms, W, H), bay)` -- every room of the level handed to
        one call with the MAIN BLOCK's `W, H` -- which is precisely the reading WP-11.6's layer 2
        removed from `structure.build_section`, where the arithmetic runs ONCE PER ELEMENT over
        that element's own rooms at that element's own origin. It agreed with the leaf for as
        long as every shipped plan was one rectangle; WP-13.5 gave the Tidewater record a service
        wing and the two parted at once, the hand-rolled control reporting an extra interior
        bearing line at `('x', 0)` -- the main block's own WEST wall, which reads as interior only
        to a caller that thinks the hyphen and the dependency are inside the block.

        So the control is `structure.build_section`'s own per-element walls now. That is still an
        independent reader -- a different module, a different call path, the record's own
        published structure rather than a re-derivation -- and it is the one the gate and every
        other consumer already use. Measured on the shipped Tidewater record: the section and the
        leaf agree exactly, `L0 [('y', 26.56)]` and
        `L1 [('x', 18.0), ('x', 27.0), ('x', 36.0), ('y', 9.6), ('y', 26.6)]`.

        The premise is asserted, because a test that compares two readers on a corpus of
        one-rectangle houses is not testing the thing that broke: at least one plan must state a
        container.
        """
        compared = 0
        multi = 0
        for path in PLANS:
            out = _solved(path)
            if "error" in out:
                continue
            mine = TF.bearing_lines(out)
            if mine is None:
                continue
            section = ST.build_section(out, None, geometry_result=out)
            if "error" in section:
                continue
            if len((out.get("footprint") or {}).get("blocks") or []) > 1:
                multi += 1
            for i, slv in enumerate(section.get("levels") or []):
                theirs = sorted({(w["axis"], round(w["position_ft"], 2))
                                 for w in (slv.get("walls") or [])
                                 if w.get("role") == "interior" and w.get("bearing")})
                idx = slv.get("index", i)
                assert mine.get(idx, []) == theirs, (
                    os.path.basename(path), idx, mine.get(idx), theirs)
                compared += 1
        assert compared >= 20, compared
        assert multi >= 1, (
            "no shipped plan states more than one massing element, so this comparison runs only "
            "where the defect it was re-cut for cannot occur")


class TestStacksReadTheTally:
    def test_a_record_with_no_tally_is_unjudged_not_held(self):
        p = _plan([_room("a", 0, 0, 10, 10)], upper=[_room("u", 0, 0, 10, 10, stacks_over="a")])
        s = TF.stacks(p)
        assert s["status"] == TF.UNJUDGED and "no stacking tally" in s["detail"]

    def test_the_verdict_is_the_tallys_and_the_fraction_is_the_containment(self):
        """Read, not re-derived: the same claim is HELD under a `kept` tally and DOWNGRADED under
        a `broken` one, and the fraction beside it is the smaller room's share inside the larger."""
        p = _plan([_room("a", 0, 0, 10, 10)], upper=[_room("u", 5, 0, 10, 10, stacks_over="a")])
        p["geometry_report"] = {"stacking": {"kept": [{"level": 1, "room": "u", "over": "a"}],
                                             "broken": [], "unjudged": []}}
        s = TF.stacks(p)
        assert s["status"] == TF.HELD and s["claims"][0]["fraction"] == 0.5
        p["geometry_report"]["stacking"] = {"kept": [], "unjudged": [],
                                            "broken": [{"level": 1, "room": "u", "over": "a"}]}
        s = TF.stacks(p)
        assert s["status"] == TF.DOWNGRADED and "50%" in s["detail"]

    def test_a_house_declaring_no_stack_is_unjudged_with_that_reason(self):
        p = _plan([_room("a", 0, 0, 10, 10)])
        p["geometry_report"] = {"stacking": {"kept": [], "broken": [], "unjudged": []}}
        s = TF.stacks(p)
        assert s["status"] == TF.UNJUDGED and "declares no vertical stack" in s["detail"]

    def test_the_shipped_heuristic_tally_reconciles_with_stacking_judge(self):
        out = _solved(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"))
        kept, broken, unj = STK.judge(out)
        s = TF.stacks(out)
        assert len([r for r in s["claims"] if r["verdict"] == "kept"]) == len(kept)
        assert len([r for r in s["claims"] if r["verdict"] == "broken"]) == len(broken)
        assert len(s["unjudged"]) == len(unj)
        assert s["status"] == (TF.DOWNGRADED if broken else (TF.HELD if kept else TF.UNJUDGED))


def _two_level(ground, upper, W=20.0, H=20.0):
    p = _plan(ground, upper=upper, W=W, H=H)
    p["footprint"]["bay_module_ft"] = 10.0
    return p


class TestBearingIsMeasuredAndRead:
    def test_an_upper_line_on_a_ground_line_holds_and_one_off_it_is_named(self):
        g = [_room("a", 0, 0, 10, 20), _room("b", 10, 0, 10, 20)]           # shared x=10 on the grid
        u = [_room("c", 0, 0, 10, 20), _room("d", 10, 0, 10, 20)]
        p = _two_level(g, u)
        p["geometry_report"] = {"span_capacity": {"over_capacity": 0}}
        b = TF.bearing(p)
        assert b["halves"] == {"continuity": TF.HELD, "capacity": TF.HELD} and b["status"] == TF.HELD
        # an upper wall at x=13 is 3 ft off the grid, beyond the 0.75 tolerance: a partition,
        # so the upper floor carries no bearing line at all
        u2 = [_room("c", 0, 0, 13, 20), _room("d", 13, 0, 7, 20)]
        p2 = _two_level(g, u2)
        p2["geometry_report"] = {"span_capacity": {"over_capacity": 0}}
        b2 = TF.bearing(p2)
        assert b2["halves"]["continuity"] == TF.DOWNGRADED and "no bearing line at all" in b2["detail"]
        # an upper line ON the grid but on no ground line: y=10 above a ground floor split in x
        u3 = [_room("c", 0, 0, 20, 10), _room("d", 0, 10, 20, 10)]
        p3 = _two_level(g, u3)
        p3["geometry_report"] = {"span_capacity": {"over_capacity": 0}}
        b3 = TF.bearing(p3)
        assert b3["halves"]["continuity"] == TF.DOWNGRADED
        assert b3["unsupported_upper_lines"] == [{"axis": "y", "position_ft": 10.0, "nearest_ground_ft": None}]

    def test_capacity_is_read_off_the_record_and_absent_is_unjudged(self):
        g = [_room("a", 0, 0, 10, 20), _room("b", 10, 0, 10, 20)]
        u = [_room("c", 0, 0, 10, 20), _room("d", 10, 0, 10, 20)]
        p = _two_level(g, u)
        assert TF.bearing(p)["halves"]["capacity"] == TF.UNJUDGED
        p["geometry_report"] = {"span_capacity": {"over_capacity": 2}}
        b = TF.bearing(p)
        assert b["halves"]["capacity"] == TF.DOWNGRADED
        assert "2 clear span(s)" in b["detail"]

    def test_capacity_does_not_refuse_a_drawing_and_continuity_does(self):
        """RULED BY LUCAS, 16 SEP 2026: "capacity shouldn't refuse a drawing -- continuity
        only". This test is the ruling, and the assertion it replaced said the opposite --
        `b["status"] == TF.DOWNGRADED` on a record whose only fault was an over-capacity span.
        That is a ruling executed, not a pin loosened, and the measurement that asked for it is
        in `build/typefacts.py::bearing`'s own comment: the capacity half alone refused 33 of
        the 37 shipped records and partis swept.

        Both halves are asserted in BOTH directions, because a status that simply stopped
        moving would pass this too: continuity decides it, and capacity is still SAID."""
        g = [_room("a", 0, 0, 10, 20), _room("b", 10, 0, 10, 20)]
        u = [_room("c", 0, 0, 10, 20), _room("d", 10, 0, 10, 20)]

        # capacity broken, continuity held -> HELD, and the span is still reported
        p = _two_level(g, u)
        p["geometry_report"] = {"span_capacity": {"over_capacity": 3}}
        b = TF.bearing(p)
        assert b["halves"]["capacity"] == TF.DOWNGRADED
        assert b["halves"]["continuity"] == TF.HELD
        assert b["status"] == TF.HELD, "an over-capacity span refused a drawing"
        assert b["capacity_status"] == TF.DOWNGRADED and b["capacity_refuses"] is False
        assert b["spans_over_capacity"] == 3 and "3 clear span(s)" in b["detail"], (
            "capacity stopped being reported when it stopped deciding")

        # continuity broken, capacity held -> DOWNGRADED. The discriminator, without which
        # this test would pass on a `bearing` that never downgrades anything at all.
        u_off = [_room("c", 0, 0, 20, 10), _room("d", 0, 10, 20, 10)]
        q = _two_level(g, u_off)
        q["geometry_report"] = {"span_capacity": {"over_capacity": 0}}
        bq = TF.bearing(q)
        assert bq["halves"]["capacity"] == TF.HELD
        assert bq["halves"]["continuity"] == TF.DOWNGRADED and bq["status"] == TF.DOWNGRADED

        # continuity UNJUDGED with capacity broken -> UNJUDGED. Unjudged is not passed, and
        # under WP-13.4's contract it is not refused either: a one-level house cannot be
        # refused a drawing for having no upper floor to carry a line down.
        one = _plan([_room("a", 0, 0, 10, 20), _room("b", 10, 0, 10, 20)])
        one["footprint"]["bay_module_ft"] = 10.0
        one["geometry_report"] = {"span_capacity": {"over_capacity": 4}}
        bo = TF.bearing(one)
        assert bo["halves"]["continuity"] == TF.UNJUDGED
        assert bo["halves"]["capacity"] == TF.DOWNGRADED
        assert bo["status"] == TF.UNJUDGED

    def test_one_level_is_unjudged_for_continuity(self):
        p = _plan([_room("a", 0, 0, 10, 20), _room("b", 10, 0, 10, 20)])
        p["footprint"]["bay_module_ft"] = 10.0
        assert TF.bearing(p)["halves"]["continuity"] == TF.UNJUDGED

    def test_no_bay_module_is_unjudged(self):
        p = _plan([_room("a", 0, 0, 10, 20), _room("b", 10, 0, 10, 20)], upper=[_room("c", 0, 0, 20, 20)])
        assert TF.bearing_lines(p) is None
        assert TF.bearing(p)["halves"]["continuity"] == TF.UNJUDGED


class TestTheHearthOnItsFlue:
    def _fixture(self, massing="four-over-four", wall="W", x=0.0):
        p = _plan([_room("a", x, 0, 10, 10, hearth=[{"wall": wall}]), _room("b", 10, 0, 10, 10)])
        p["massing"] = massing
        return p

    def test_a_fire_on_the_face_holds_and_one_inboard_is_downgraded_with_the_figure(self):
        assert TF.hearth(self._fixture())["status"] == TF.HELD
        h = TF.hearth(self._fixture(x=0.5))
        assert h["status"] == TF.DOWNGRADED and h["fires"][0]["inboard_ft"] == 0.5
        assert "0.5 ft inboard" in h["detail"] and "0.50 ft inboard" in h["fires"][0]["why"]

    def test_a_fire_on_a_wall_the_massing_puts_no_flue_on_is_unjudged_by_name(self):
        h = TF.hearth(self._fixture(wall="N"))
        assert h["status"] == TF.UNJUDGED and "puts its flues on E/W" in h["fires"][0]["why"]

    def test_no_massing_and_a_compound_massing_are_unjudged_with_distinct_reasons(self):
        p = self._fixture()
        del p["massing"]
        h = TF.hearth(p)
        assert h["status"] == TF.UNJUDGED and "names no massing" in h["fires"][0]["why"]
        # premise: hall-and-parlor really states a compound in the catalogue
        rows = json.load(open(TF.MASSING_CATALOG, encoding="utf-8"))
        hp = next(r for r in rows if r["id"] == "hall-and-parlor")
        assert " or " in hp["hearth"], hp["hearth"]
        h2 = TF.hearth(self._fixture(massing="hall-and-parlor"))
        assert h2["status"] == TF.UNJUDGED and "does not read" in h2["fires"][0]["why"]

    def test_the_flue_walls_agree_with_hearths_flue_walls_on_every_shipped_plan(self):
        """Same answer as `hearths.flue_walls(plan, massing)` -- walls or a refusal -- on every
        plan record, so the leaf's reading of the catalogue cannot drift from the reader's."""
        mass = {m["id"]: m for m in json.load(open(TF.MASSING_CATALOG, encoding="utf-8"))}
        agreed = 0
        for path in PLANS:
            plan = json.load(open(path, encoding="utf-8"))
            mine, why = TF.flue_walls_of(plan)
            m = mass.get(plan.get("massing"))
            theirs, twhy = HE.flue_walls(plan, m) if m else (None, "no massing")
            if theirs is None:
                assert mine is None, (path, mine, twhy)
            else:
                assert tuple(mine) == tuple(theirs["walls"]), (path, mine, theirs)
                agreed += 1
        assert agreed >= 1, "no shipped plan resolved a flue wall: the comparison ran on nothing"


class TestTheReportCarriesFourVerdicts:
    def test_status_names_all_four_and_never_holds_by_absence(self):
        p = _plan([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)])
        r = TF.report(p)
        assert set(r["status"]) == {"tiling", "stacks", "bearing", "hearth"}
        assert r["status"]["tiling"] == TF.HELD
        assert r["status"]["stacks"] == TF.UNJUDGED and r["status"]["hearth"] == TF.UNJUDGED
        assert r["status"]["bearing"] == TF.UNJUDGED
        assert "Unjudged: bearing, hearth, stacks" in r["note"]
        assert r["tiling"]["status"] == TF.HELD and r["tiling"]["tolerance_sf"] == TF.TILING_TOL_SF

    def test_a_level_with_a_hole_reads_downgraded_not_held(self):
        """The tiling verdict is the measurement's: a 5 sf strip between two rooms is over the
        0.05 sf tolerance, so the status says DOWNGRADED and names it in the note."""
        p = _plan([_room("a", 0, 0, 10, 10), _room("b", 10.5, 0, 9.5, 10)])
        r = TF.report(p)
        assert r["tiling"]["uncovered_sf"] == 5.0
        assert r["status"]["tiling"] == TF.DOWNGRADED and r["tiling"]["status"] == TF.DOWNGRADED
        assert "DOWNGRADED: tiling" in r["note"]

    def test_the_shipped_search_record_carries_all_four(self):
        out = _solved(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"))
        tf = out["geometry_report"]["type_facts"]
        assert set(tf["status"]) == {"tiling", "stacks", "bearing", "hearth"}
        assert tf["status"]["tiling"] == TF.HELD
        # the search tiles by construction and reads its own stacking tally
        kept, broken, _ = STK.judge(out)
        assert tf["status"]["stacks"] == (TF.DOWNGRADED if broken else TF.HELD)
        assert tf["hearth"]["flue_walls"] == ["E", "W"]
