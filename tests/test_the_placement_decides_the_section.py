"""THE SECTION AND THE IFC'S SLABS ARE THE PLACEMENT'S, WHATEVER RECORD IS HANDED (audit, 27 Sep 2026).

`geometry.solve` writes a placement INTO the record it is handed on a cache MISS and returns a copy
on a HIT, so a product caller (`corpus._placed` and every branch after it) hands a builder the
placed record on a record's first request and the declared one after. `structure.build_section`
read the massing elements off the handed record, and `export_ifc.slab_boxes` read the elements and
the rooms off it, while every other number in both came from the placement -- so each answered by
cache state. Measured on the tagged Tidewater before the fix: handed the placed record, the section
drew the dependency's envelope walls at x -34 and -7 and three over-capacity spans; handed the
declared record beside the SAME placement, no dependency walls and one span invented across the
whole house.

THE GUARD REPRODUCES THE MECHANISM rather than a proxy for it: one private cache, the declared
record solved twice -- the first call a miss that writes into its argument, the second a hit that
does not -- and each builder handed what the product would hand it. The premise is asserted, not
assumed: the first argument carries the elements and the second does not, and the plan has more
than one element, because on a one-rectangle house the two readings coincide and this passes on
any code.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
ST = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))
EI = modcache.load("export_ifc", os.path.join(ROOT, "build", "export_ifc.py"))
TIDEWATER = os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")


@pytest.fixture(scope="module")
def cold_and_warm():
    with open(TIDEWATER, encoding="utf-8") as fh:
        decl = json.load(fh)
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}          # private: nothing solved here is served to another test
    try:
        cold_arg = copy.deepcopy(decl)
        cold = GEO.solve(cold_arg, None, 250, engine="heuristic")
        warm_arg = copy.deepcopy(decl)
        warm = GEO.solve(warm_arg, None, 250, engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved
    return cold_arg, cold, warm_arg, warm


def test_the_premise_a_cold_solve_writes_into_its_argument_and_a_warm_one_does_not(cold_and_warm):
    cold_arg, cold, warm_arg, warm = cold_and_warm
    assert len((cold["footprint"] or {}).get("blocks") or []) > 1, "the plan must place >1 element"
    assert (cold_arg.get("footprint") or {}).get("blocks"), "a miss writes the placement into its argument"
    assert not (warm_arg.get("footprint") or {}).get("blocks"), (
        "a hit leaves its argument declared -- if this has changed, the cold/warm split this file "
        "guards is gone and the equalities below hold by construction: revisit it")


def test_the_section_is_the_same_on_a_cold_and_a_warm_request(cold_and_warm):
    cold_arg, cold, warm_arg, warm = cold_and_warm
    a = ST.build_section(cold_arg, None, geometry_result=cold)
    b = ST.build_section(warm_arg, None, geometry_result=warm)
    for la, lb in zip(a["levels"], b["levels"]):
        assert la["walls"] == lb["walls"], la.get("id")
        assert la["spans"] == lb["spans"], la.get("id")
    els = {w.get("element") for w in a["levels"][0]["walls"]}
    assert len(els - {None}) > 1, "the ground level's walls name more than one element"


def test_the_ifc_slabs_are_the_same_on_a_cold_and_a_warm_request(cold_and_warm):
    cold_arg, cold, warm_arg, warm = cold_and_warm
    a = ST.build_section(cold_arg, None, geometry_result=cold)
    b = ST.build_section(warm_arg, None, geometry_result=warm)
    t = a["wall"]["exterior_in"] / 12.0
    sa, sb = EI.slab_boxes(cold_arg, a, t), EI.slab_boxes(warm_arg, b, t)
    assert sa == sb
    assert {s["element"] for s in sa if s["level"] == 0} != {"main"}, \
        "a ground slab stands under the dependency, not only the main block"
