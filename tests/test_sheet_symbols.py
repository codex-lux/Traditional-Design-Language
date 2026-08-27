"""Both renderers of a plan record must draw the same openings (WP-6.1).

The other half of this contract is workbench/app/src/derive.test.mjs, which runs the
JavaScript renderer over the same fixtures. Read tests/fixtures/sheet_symbols/README.md
for why the placement inside a fixture is frozen rather than solved here.

These tests also pin the three specific lies the sheet used to tell, by name, so that
fixing them cannot be quietly undone:
  · a door narrower than 3.2 ft was never drawn, though the solver would prove it
  · a door with no drawable wall was dropped in silence
  · a window and an exterior door were placed on the same masonry, window painted last
"""
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "sheet_symbols"
sys.path.insert(0, str(ROOT / "build"))

import modcache  # noqa: E402  (the project's one module loader — never a local copy)

render_plan = modcache.load("render_plan", str(ROOT / "build" / "render_plan.py"))

FIXTURES = sorted(p for p in FIX.glob("*.json"))


def _fixtures():
    assert FIXTURES, "no sheet-symbol fixtures — generate.py has not been run"
    return FIXTURES


@pytest.mark.parametrize("path", _fixtures(), ids=lambda p: p.stem)
def test_python_renderer_matches_the_contract(path):
    """render_plan.derive_openings reproduces the frozen fixture exactly."""
    fx = json.loads(path.read_text())
    W = fx["footprint"]["width_ft"]
    H = fx["footprint"]["depth_ft"]
    for lv in fx["levels"]:
        got = render_plan.derive_openings(lv["rooms"], W, H)
        assert got == lv["expected"], (
            f"{path.stem} level {lv['id']}: the Python renderer no longer draws what the "
            f"contract says. If this change is intended, regenerate the fixtures and read "
            f"the diff — workbench/app/src/derive.test.mjs must change with it."
        )


@pytest.mark.parametrize("path", _fixtures(), ids=lambda p: p.stem)
def test_every_declared_door_is_drawn_or_named(path):
    """No declared door may simply vanish. Either it is drawn, or it is on the undrawable
    list with a reason — the state this file exists to make impossible is the third one,
    where the record holds a door and the sheet holds neither the door nor a word about it.
    """
    fx = json.loads(path.read_text())
    for lv in fx["levels"]:
        exp = lv["expected"]
        drawn = {tuple(sorted(d["pair"])) for d in exp["interior"]}
        named = {tuple(sorted((u["from"], u["to"]))) for u in exp["undrawable"]}
        ext_drawn = sum(1 for _ in exp["exterior"])
        ext_named = sum(1 for u in exp["undrawable"] if u["to"] == "exterior")

        declared_pairs, declared_ext = set(), 0
        for r in lv["rooms"]:
            for d in (r.get("doors") or []):
                if d["to"] == "exterior":
                    declared_ext += 1
                else:
                    declared_pairs.add(tuple(sorted((r["id"], d["to"]))))

        missing = declared_pairs - drawn - named
        assert not missing, f"{path.stem} {lv['id']}: doors neither drawn nor named: {sorted(missing)}"
        assert ext_drawn + ext_named == declared_ext, (
            f"{path.stem} {lv['id']}: {declared_ext} exterior door(s) declared, "
            f"{ext_drawn} drawn and {ext_named} named"
        )
        for u in exp["undrawable"]:
            assert u["reason"].strip(), "an undrawable door must say WHY it could not be drawn"


@pytest.mark.parametrize("path", _fixtures(), ids=lambda p: p.stem)
def test_no_opening_is_drawn_over_another(path):
    """A door and a window may not occupy the same masonry.

    On the shipped Tidewater sheet this fired twice — the centre passage's front door and
    the kitchen's back door were each drawn at their wall's midpoint, and each had a single
    declared window on the same wall, also at the midpoint. WindowMark paints a filled rect
    and DoorMark paints a 0.7 ft break, so the window swallowed the door and a reader saw a
    house whose passage has no door at either end.
    """
    fx = json.loads(path.read_text())
    for lv in fx["levels"]:
        exp = lv["expected"]
        spans = {}
        for d in exp["exterior"]:
            spans.setdefault((d["room"], d["wall"]), []).append(
                ("door", d["at_ft"] - d["width_ft"] / 2, d["at_ft"] + d["width_ft"] / 2))
        for w in exp["windows"]:
            spans.setdefault((w["room"], w["wall"]), []).append(
                ("window", w["at_ft"] - w["width_ft"] / 2, w["at_ft"] + w["width_ft"] / 2))
        for key, items in spans.items():
            items.sort(key=lambda t: t[1])
            for (k1, a1, b1), (k2, a2, b2) in zip(items, items[1:]):
                assert a2 >= b1 - 1e-6, (
                    f"{path.stem} {lv['id']} {key[0]} wall {key[1]}: {k1} "
                    f"[{a1:.2f},{b1:.2f}] overlaps {k2} [{a2:.2f},{b2:.2f}]"
                )


def test_a_narrow_door_is_drawn_at_its_own_width():
    """OQ 41/63, the renderer half. The old test was a flat 3.2 ft for every door, so a
    2.2 ft closet door the CP engine proves on a 2 ft shared wall was held as a fact and
    appeared in no drawing. The test is now the leaf plus its jambs."""
    assert render_plan.required_wall_ft(2.2) == pytest.approx(2.9)
    a = {"x_ft": 0, "y_ft": 0, "width_ft": 10, "depth_ft": 10}
    b = {"x_ft": 10, "y_ft": 0, "width_ft": 10, "depth_ft": 3.0}   # 3.0 ft of shared wall
    assert render_plan._shared(a, b, width_ft=2.2) is not None, "a closet door fits 3.0 ft"
    assert render_plan._shared(a, b, width_ft=3.5) is None, "a 3.5 ft leaf does not"
    # and the historical default is unchanged for callers that state no width
    assert render_plan._shared(a, b) is None


def test_the_kitchen_keeps_its_doors_on_the_record_even_when_undrawable():
    """The reported symptom, pinned. On the Tidewater placement the kitchen's five interior
    doors have no drawable shared wall, so the sheet drew the kitchen with one exterior door
    and nothing else — a room reachable only from outdoors — and said nothing at all. They
    must now every one be named."""
    fx = json.loads((FIX / "tidewater-georgian-careful.json").read_text())
    ground = next(lv for lv in fx["levels"] if lv["index"] == 0)
    named = {tuple(sorted((u["from"], u["to"]))) for u in ground["expected"]["undrawable"]}
    kitchen = {p for p in named if "kitchen" in p}
    assert len(kitchen) >= 5, f"expected the kitchen's undrawable doors to be named; got {kitchen}"


def test_a_relaxation_mark_is_drawn_on_the_wall_it_is_true_of_or_not_drawn():
    """The JS half is `relaxationMarks` in derive.test.mjs, and the two must agree.

    A CP mark carries `runs` rather than a from/to extent, and both renderers used to drop
    such a mark at the MIDDLE OF THE PLAN: on the Tidewater placement that put a dashed tick
    and a triangle inside the drawing room, on a line that has no wall anywhere near it.
    Those are the arrows Lucas reported as pointing "to anything and everything"."""
    W, H = 60, 40
    heur = {"off_ft": 2, "axis": "y", "at_ft": 27, "level": 0, "from_ft": 10, "to_ft": 20}
    cp = {"off_ft": 3, "axis": "y", "at_ft": 27, "level": 0, "runs": [[51, 60], [0, 4]]}
    nowhere = {"off_ft": 4, "axis": "y", "at_ft": 27, "level": 0}
    other = {"off_ft": 5, "axis": "x", "at_ft": 13, "level": 1, "runs": [[0, 40]]}

    drawn, unlocated = render_plan.relaxation_marks([heur, cp, nowhere, other], 0, W, H)
    assert len(drawn) == 2, "the level-1 mark belongs to the other plate"
    assert [m["off_ft"] for m in unlocated] == [4], "a mark on no wall is named, never placed"

    (_m0, runs0, at0), (_m1, runs1, at1) = drawn
    assert runs0 == [(10, 20)] and at0 == pytest.approx(15)
    assert len(runs1) == 2, "both measured pieces of the line are drawn"
    assert at1 == pytest.approx(55.5), "the triangle hangs on the longest real run"
    assert at1 != pytest.approx(W / 2), "and never at the middle of the plan"

    # a run off the plate is clipped; one with nothing left locates nothing
    drawn, unlocated = render_plan.relaxation_marks(
        [{"off_ft": 2, "axis": "x", "at_ft": 5, "level": 0, "runs": [[-8, 12]]},
         {"off_ft": 2, "axis": "x", "at_ft": 6, "level": 0, "runs": [[80, 96]]}], 0, W, H)
    assert [r for _m, r, _a in drawn] == [[(0, 12)]]
    assert len(unlocated) == 1


def test_the_cp_counter_gives_every_relaxation_a_wall_to_sit_on():
    """The counter knew which room faces lay on the off-grid line and threw them away, so
    the sheet had nothing to place the mark by and dropped it at the middle of the plan.

    Measured on the counter itself rather than on a frozen placement: `_count_relaxations`
    is a pure function of the rectangles, so this needs no solver and pins the mechanism
    instead of one machine's search result. Two rooms meet on a line at x = 13 that the
    10 ft bay does not carry, and they meet along y 25..40 — nowhere near the middle."""
    cp = modcache.load("geometry_cp", str(ROOT / "build" / "geometry_cp.py"))
    rects = {"a": (0.0, 25.0, 13.0, 15.0), "b": (13.0, 25.0, 27.0, 15.0),
             "c": (0.0, 0.0, 40.0, 25.0)}
    marks = cp._count_relaxations({0: rects}, W=40, H=40, bay=10.0, tol=0.5)
    assert marks, "a wall at 13 ft on a 10 ft bay is a relaxation"
    for m in marks:
        assert m.get("runs"), f"{m} carries no measured wall to sit on"
    line = next(m for m in marks if m["axis"] == "x" and m["at_ft"] == 13.0)
    assert line["runs"] == [[25.0, 40.0]], "the run is where the rooms actually meet"
    drawn, unlocated = render_plan.relaxation_marks(marks, 0, 40, 40)
    assert not unlocated and len(drawn) == len(marks)
    assert all(a >= 25.0 for _m, runs, _at in drawn for a, _b in runs
               if _m["axis"] == "x"), "and not across the room below it"
