"""THE AUDIT OF PHASE 17 (30 Oct 2026): THE TILING RASTER HAD NO CEILING.

`typefacts.uncovered` paints and floods one Python-loop cell per 0.1 ft square, so ONE 600 ft
block took 35 s and a 28 KB body posted to a drawing route held a worker for 13.7 s. Above
`RASTER_CELLS_MAX` cells of work the tiling is UNJUDGED with the reason stated, and the work is
never begun. Unjudged never refuses, so this is defence in depth behind the carried-placement
registry (`workbench/server/corpus.py`), which keeps a client's own rectangles off this path.
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

TF = modcache.load("typefacts", os.path.join(ROOT, "build", "typefacts.py"))
DI = modcache.load("disclosures", os.path.join(ROOT, "build", "disclosures.py"))


def _room(rid, x, y, w, h):
    return {"id": rid, "type": "parlor", "width_ft": w, "length_ft": h,
            "geometry": {"x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": h, "area_sf": w * h}}


def _plan(rooms, W, H):
    return {"id": "t", "levels": [{"id": "ground", "index": 0, "rooms": rooms}],
            "footprint": {"width_ft": W, "depth_ft": H}}


def test_the_ceiling_is_named_and_above_every_house_this_corpus_places():
    assert TF.RASTER_CELLS_MAX >= 2_000_000, "a real house's block must stay judgeable"
    # the Tidewater main block, rooms tiling it: well under the ceiling
    assert TF.raster_work([(0, 0, 45, 37.24)], (0, 0, 45, 37.24, "main")) < TF.RASTER_CELLS_MAX / 10


def test_raster_work_counts_the_block_and_each_clamped_rectangle():
    blk = (0, 0, 20, 10, "main")
    assert TF.raster_work([], blk) == 200 * 100
    assert TF.raster_work([(0, 0, 10, 10)], blk) == 200 * 100 + 100 * 100
    # clamped to the block: a rectangle running past it is charged only its cells inside
    assert TF.raster_work([(-5, 0, 25, 10)], blk) == 200 * 100 + 200 * 100


def test_a_600_ft_block_is_unjudged_at_once_and_never_rasterised():
    """The measured defect: 35 s for this block. Mutation: delete the ceiling test in `uncovered`
    and this goes red on the clock (and on the verdict)."""
    plan = _plan([_room("a", 0, 0, 600, 300), _room("b", 0, 300, 600, 300)], 600.0, 600.0)
    t0 = time.perf_counter()
    t = TF.tiling(plan)
    took = time.perf_counter() - t0
    assert took < 2.0, f"the raster ran ({took:.1f} s) where it must refuse before it begins"
    assert t["uncovered_sf"] is None
    blk = t["levels"][0]["blocks"][0]
    assert blk["uncovered_sf"] is None and "RASTER_CELLS_MAX" in blk["unjudged"]
    assert TF.tiling_status(t) == TF.UNJUDGED, "past the ceiling is unjudged, never held"
    assert TF.report(plan)["status"]["tiling"] == TF.UNJUDGED


def test_the_unjudged_tiling_prints_neither_a_figure_nor_a_pass():
    plan = _plan([_room("a", 0, 0, 600, 600)], 600.0, 600.0)
    plan["geometry_report"] = {"type_facts": TF.report(plan)}
    lines = DI.residual_void(plan)        # before the fix: TypeError formatting None with :g
    assert lines and all("TILES ITS BLOCK" not in ln["text"] for ln in lines), lines
    assert any("NOT JUDGED" in ln["text"] for ln in lines), lines


def test_a_house_under_the_ceiling_is_judged_exactly_as_before():
    plan = _plan([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 9.5, 10)], 20.0, 10.0)
    t = TF.tiling(plan)
    assert t["uncovered_sf"] == 5.0
    assert TF.tiling_status(t) == TF.DOWNGRADED
