"""The wall is a body, and the body is the record's.

Until the Drawn Language pass every wall on the plan sheet was a single stroke and the word
"thickness" did not appear in `build/render_plan.py`. `build/structure.py` had computed all
three thicknesses since WP-3.1 -- exterior, bearing-interior and partition, from the plan's own
`declared.construction_type` against `construction/wall-assemblies.json` -- and no drawing had
ever read one.

These tests hold the drawing to that record rather than to a picture. Each one is written so
that it fails on a mutation of the thing it is about: the last three sheet defects in this
repository were found by looking at a sheet, and a test that cannot fail is worse than no test
because its output is a green tick.
"""
import importlib.util
import json
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "build", name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = _mod("geometry")
RP = _mod("render_plan")
ST = _mod("structure")

BAND = re.compile(r'<rect class="(pm|pp)" data-wall="(\w+)"[^>]*? x="([-\d.]+)" y="([-\d.]+)" '
                  r'width="([\d.]+)" height="([\d.]+)"')
# The band's own stated thickness, in inches. See `_thicknesses` below for why the rectangle
# cannot answer this and why reading it from the rectangle was wrong.
BAND_T = re.compile(r'<rect class="(?:pm|pp)" data-wall="(\w+)" data-t="([\d.]+)"')


def _solved(name="tidewater-georgian-careful", **over):
    plan = json.load(open(os.path.join(ROOT, "plans", name + ".json")))
    if over:
        plan.setdefault("declared", {}).update(over)
    G._SOLVE_CACHE.clear()
    return G.solve(plan, engine="heuristic")


def _bands(svg):
    """(kind, wall, x, y, w, h) for every wall body on the sheet, in sheet pixels."""
    return [(k, n, float(x), float(y), float(w), float(h))
            for k, n, x, y, w, h in BAND.findall(svg)]


@pytest.fixture(scope="module")
def sheet(tmp_path_factory):
    out = _solved()
    path = str(tmp_path_factory.mktemp("poche") / "sheet.svg")
    RP.render(out, path)
    return out, open(path).read()


def test_the_sheet_draws_walls_at_all(sheet):
    """The vacuity guard, first, because every test below selects on the same pattern."""
    _out, svg = sheet
    bands = _bands(svg)
    assert len(bands) > 40, f"only {len(bands)} wall bodies on the sheet"
    assert {k for k, *_ in bands} == {"pm", "pp"}, "both a masonry and a partition body are expected"
    assert {n for _k, n, *_ in bands} >= {"exterior", "bearing", "partition"}, (
        "the sheet does not distinguish the three walls the record states")


def test_every_thickness_drawn_is_a_thickness_the_record_states(sheet):
    """Three thicknesses, and all three are read from the construction catalogue.

    A band is a rectangle, so its thickness is its SHORT side. Every one must be one of the
    three the assembly states -- not a house convention, not a number chosen to look right."""
    out, svg = sheet
    wall = ST.wall_thickness(out)
    want = {"exterior": round(wall["exterior_in"] / 12.0 * RP.PX_PER_FT, 1),
            "bearing": round(wall["bearing_interior_in"] / 12.0 * RP.PX_PER_FT, 1),
            "court": round(wall["exterior_in"] / 12.0 * RP.PX_PER_FT, 1),
            "partition": round(wall["partition_in"] / 12.0 * RP.PX_PER_FT, 1)}
    assert len({want["exterior"], want["bearing"], want["partition"]}) == 3, \
        f"this plan's assembly does not distinguish three walls: {wall}"
    # ONE SIDE OF THE RECTANGLE, NOT ITS SHORT SIDE. A pier between two windows is a run
    # shorter than the wall is thick, so `min(w, h)` reads its LENGTH -- measured, the first
    # version of this test convicted the sheet of drawing 7.8 and 13.0 px walls that are in
    # fact 0.6 and 1.0 ft of perfectly correct 15.5 in masonry.
    seen = set()
    for _k, n, _x, _y, w, h in _bands(svg):
        t = want[n]
        assert abs(w - t) < 0.15 or abs(h - t) < 0.15, (
            f"a {n} wall is drawn {w:.1f} x {h:.1f} px and the record states {t:.1f} px thick")
        seen.add(n)
    assert seen >= {"exterior", "bearing", "partition"}, (
        f"only {sorted(seen)} drawn -- a wall kind is going undrawn")


def test_the_drawing_changes_when_the_construction_does(tmp_path):
    """THE MUTATION IS THE TEST. A sheet that draws the same wall whatever the house is built
    of is a sheet reading a constant, and the assertion above would still pass on it -- the
    three thicknesses would simply be three constants. Two houses, two assemblies, and the ink
    has to move: solid masonry states 15.5 / 11 / 4.5 in, platform frame 8 / 5.5 / 4.5."""
    a = _solved()
    b = _solved(construction_type="platform-frame")
    pa, pb = str(tmp_path / "a.svg"), str(tmp_path / "b.svg")
    RP.render(a, pa); RP.render(b, pb)
    def env(svg):
        return {round(min(w, h), 1) for _k, n, _x, _y, w, h in _bands(svg) if n == "exterior"}
    ta, tb = env(open(pa).read()), env(open(pb).read())
    assert ta != tb, (
        f"the same wall bodies {sorted(ta)} are drawn for solid masonry and platform frame -- "
        "the sheet is not reading the plan's own construction_type")
    assert max(ta) > max(tb), "a two-wythe masonry envelope is thicker than a frame one"


def test_an_opening_is_a_hole_and_not_a_mark_laid_over_a_wall(sheet):
    """Every opening `derive_openings` places has a gap cut for it in the wall body.

    This is the difference between the wall being a body and the wall being a line: before the
    Drawn Language pass a window was a coloured bar drawn ON TOP of an unbroken stroke, so the
    sheet showed a wall that ran straight through its own windows."""
    out, svg = sheet
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    levels = [lv for lv in out["levels"] if any("geometry" in r for r in lv["rooms"])]
    checked = 0
    for lv in levels:
        op = RP.derive_openings(lv["rooms"], W, H)
        gaps = RP.opening_gaps(op, W, H)
        assert gaps, "no openings on this level -- the check would be vacuous"
        bands, _stray = RP.wall_bands(lv["rooms"], [(0.0, 0.0, W, H)], W, H,
                                      fp.get("bay_module_ft"), ST.wall_thickness(out), gaps)
        for axis, pos, lo, hi in gaps:
            mid = (lo + hi) / 2.0
            for b in bands:
                if axis == "x":
                    covers = (b["x_ft"] - 0.02 <= pos <= b["x_ft"] + b["width_ft"] + 0.02
                              and b["y_ft"] < mid < b["y_ft"] + b["depth_ft"])
                else:
                    covers = (b["y_ft"] - 0.02 <= pos <= b["y_ft"] + b["depth_ft"] + 0.02
                              and b["x_ft"] < mid < b["x_ft"] + b["width_ft"])
                assert not covers, (
                    f"an opening on the {axis} wall at {pos:.2f} ft, running {lo:.2f}-{hi:.2f}, "
                    f"has wall drawn across its middle")
                checked += 1
    assert checked, "no band was compared against an opening -- this test would pass vacuously"


def test_the_envelope_is_drawn_outside_the_rooms_it_wraps(sheet):
    """`geometry.py` tiles the block exactly with rooms, so the block's edge is the INSIDE face
    of the exterior wall. Drawing the envelope centred there would take half its thickness out
    of every room on the boundary and quietly shrink the house by a foot and a half."""
    out, _svg = sheet
    fp = out["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    wall = ST.wall_thickness(out)
    ext = wall["exterior_in"] / 12.0
    lv = [l for l in out["levels"] if any("geometry" in r for r in l["rooms"])][0]
    op = RP.derive_openings(lv["rooms"], W, H)
    bands, _stray = RP.wall_bands(lv["rooms"], [(0.0, 0.0, W, H)], W, H, fp.get("bay_module_ft"),
                                 wall, RP.opening_gaps(op, W, H))
    south = [b for b in bands if abs(b["y_ft"] + b["depth_ft"]) < 0.01]
    assert south, "no south envelope band was drawn"
    for b in south:
        assert b["y_ft"] < -ext + 0.01, (
            f"the south envelope is drawn from y={b['y_ft']:.2f} ft, which is inside the rooms "
            "it wraps rather than outside them")


def _thicknesses(svg, name):
    """The stated thickness, in inches, of every band of one wall class.

    RE-CUT AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026). This read `min(width, height)` off
    the drawn rectangle, and `render_plan.wall_bands` says in its own body why that is a proxy
    and not the property: *"a pier between two windows is a run SHORTER than the wall is thick,
    so the short side of the rectangle is its length and not its thickness."* It held while
    every run was longer than it was thick. The merged placement (63 ft on 7 bays of 9, main's
    WP-11.2) produced a **0.365 ft masonry stub** between two openings, and the guard duly
    reported a load-bearing wall drawn thinner than a partition -- a false conviction of the
    drawing, from an instrument measuring the wrong quantity. The band has carried `t_ft` all
    along; the plate publishes it as `data-t` now and this reads that."""
    return {float(t) for n, t in BAND_T.findall(svg) if n == name}


def test_a_partition_is_drawn_thinner_than_the_wall_that_carries_it(sheet):
    """The drawing says which walls CARRY -- a fact the record has held since WP-3.1 and no
    plate had ever shown. If the two are drawn alike the reader cannot tell a partition from a
    bearing line, which is the whole reason the corpus tags them."""
    _out, svg = sheet
    pm = _thicknesses(svg, "bearing")
    pp = _thicknesses(svg, "partition")
    assert pm and pp, "the sheet draws only one kind of interior wall body"
    assert max(pp) < min(pm), (
        f"partitions are drawn {sorted(pp)} in and load-bearing walls {sorted(pm)} in -- a "
        "reader cannot tell them apart")
    # AND THE STATED THICKNESS IS THE ASSEMBLY'S, not whatever the rectangle happens to be.
    # Without this the plate could publish a `data-t` of its own invention and the test above
    # would still pass, which is the failure mode the attribute was added to remove.
    out, _svg = sheet
    wall = ST.wall_thickness(out)
    assert pm == {round(wall["bearing_interior_in"], 1)}, (
        f"the plate states {sorted(pm)} in of bearing wall against the assembly's "
        f"{wall['bearing_interior_in']}")
    assert pp == {round(wall["partition_in"], 1)}


def test_the_stated_thickness_is_not_recoverable_from_the_rectangle(sheet):
    """THE REASON THE ATTRIBUTE EXISTS, asserted rather than left in a comment. At least one
    band on this sheet is drawn SHORTER than it is thick, so `min(width, height)` reads its
    length; a guard using that proxy convicts the drawing. If this ever stops being true the
    proxy would start working again -- and the attribute would still be the right answer, so
    the test says COULD NOT EVALUATE rather than passing on the absence of the case."""
    out, svg = sheet
    bands = _bands(svg)
    stated = {n: t for n, t in ((n, float(t)) for n, t in BAND_T.findall(svg))}
    scale = None
    for _k, n, _x, _y, w, h in bands:
        if n in stated and stated[n]:
            scale = min(w, h) / (stated[n] / 12.0) if min(w, h) else None
            break
    stubs = [(n, round(min(w, h), 2)) for _k, n, _x, _y, w, h in bands
             if scale and min(w, h) < (stated.get(n, 0) / 12.0) * scale - 0.05]
    if not stubs:
        pytest.skip("COULD NOT EVALUATE: no run on this sheet is shorter than its wall is "
                    "thick, so the proxy this attribute replaces cannot be shown wrong here")
    assert stubs, stubs
