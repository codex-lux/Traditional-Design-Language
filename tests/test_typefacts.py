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
        src = open(os.path.join(ROOT, "build", "geometry.py"), encoding="utf-8").read()
        assert src.count('rep["type_facts"] = TF.report(plan)') == 1
        assert src.count('["type_facts"]') == 1, "a second writer of the block has appeared"
        body = src[src.index("def _disclose(plan):"):]
        body = body[:body.index("\ndef ")]
        assert "TF.report(plan)" in body

    def test_the_shipped_search_placement_carries_the_fact(self):
        plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        GEO._SOLVE_CACHE.clear()
        out = GEO.solve(copy.deepcopy(plan), None, 250, engine="heuristic")
        t = out["geometry_report"]["type_facts"]["tiling"]
        assert t and len(t["levels"]) == 2
        # the search tiles exactly by construction (WP-9.2: the slicer tiles); a hole here is
        # the engine changing, not the fact
        assert t["uncovered_sf"] == 0.0, t
