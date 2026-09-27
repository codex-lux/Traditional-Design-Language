"""The bay grid is drawn on a module somebody stated, or the sheet says whose default it is (WP-14.4).

`geometry.derive_footprint` lays the footprint on the parti's own `bay_module_ft`, or on 10 ft when
no parti states one -- and fifteen of the sixteen shipped plans name no parti. The working sheet
drew that grid and labelled its lines, both registers drew the walls on it as bearing bodies, and
nothing on either plate said the module was the placer's own. The record now carries who stated it
(`geometry_report.bay_module`), `disclosures.bay_module` is the one line both surfaces print, and a
record carrying no module at all gets no grid rather than a silent 10 ft one.
"""
import copy
import json
import os
import re
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache as mc  # noqa: E402

G = mc.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
RP = mc.load("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
DISC = mc.load("disclosures", os.path.join(ROOT, "build", "disclosures.py"))

LINE = "BAY GRID AT THE PLACER'S DEFAULT"


def _placed(name, engine="heuristic", **kw):
    sub = "plans" if not name.startswith(("good-", "bad-")) else os.path.join("plans", "reference")
    plan = json.load(open(os.path.join(ROOT, sub, name + ".json")))
    G._SOLVE_CACHE.clear()
    return G.solve(copy.deepcopy(plan), engine=engine, **kw)


def _sheet(placed):
    d = tempfile.mkdtemp()
    out = os.path.join(d, "p.svg")
    RP.render(placed, out)
    return open(out).read()


def test_a_parti_that_states_its_module_is_named_and_no_line_is_printed():
    p = _placed("tidewater-georgian-careful")
    bm = p["geometry_report"]["bay_module"]
    assert bm["stated_by"] == p["parti"] and bm["ft"] == p["footprint"]["bay_module_ft"], bm
    assert not [ln for ln in DISC.banner(p) if ln["id"] == "bay-module"]
    assert LINE not in _sheet(p)


def test_a_plan_naming_no_parti_is_drawn_on_the_default_and_says_so():
    p = _placed("spec-builder-colonial")
    assert not p.get("parti"), "the premise: this plan names no parti"
    bm = p["geometry_report"]["bay_module"]
    assert bm["stated_by"] is None and bm["ft"] == 10.0, bm
    assert [ln for ln in DISC.banner(p) if ln["id"] == "bay-module"], "the default is not said"
    svg = _sheet(p)
    assert LINE in svg and svg.count('class="gd"') > 2, "the grid is drawn and its module said"


def test_both_record_writers_carry_it():
    """The proving engine writes its record through `_finish`, the search through
    `write_record`; a disclosure wired into one is the defect `_disclose` exists to prevent."""
    p = _placed("bad-04-log-cabin", engine="cp", time_limit_s=8)
    assert p["geometry_report"]["solver"]["engine"] == "cp-sat", "the premise: the prover placed it"
    assert p["geometry_report"]["bay_module"]["stated_by"] is None


def test_a_record_with_no_module_gets_no_grid_and_says_so():
    """DRIVEN: every record the placer writes carries a module, so a record without one -- one
    ingested from a drawing, or placed before the field existed -- is made by hand."""
    p = _placed("spec-builder-colonial")
    assert p["footprint"].get("bay_module_ft"), "the premise: the placed record carries a module"
    before = _sheet(p)
    q = copy.deepcopy(p)
    del q["footprint"]["bay_module_ft"]
    q["geometry_report"].pop("bay_module", None)
    after = _sheet(q)
    grid = lambda s: len(re.findall(r'<line class="gd"', s))  # noqa: E731
    assert grid(after) < grid(before), "a grid was drawn on a module the record does not state"
    assert "NO BAY MODULE ON THE RECORD" in after
    assert "NO BAY MODULE ON THE RECORD" not in before
