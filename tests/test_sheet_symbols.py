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
