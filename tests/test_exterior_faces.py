"""WP-11.14 — an exterior opening is drawn on its own massing element's face.

WP-11.9 taught six layers below the placer about massing elements. The DRAWING was not one of
them, and WP-11.13 found it by rendering the tagged plan that package made provable and looking
at the sheet: two exterior doors, each with its sill and swing arc, in open space north of the
whole building.

Measured on the hand-tagged `tidewater-georgian-careful`, before:

    exterior doors   backhall drawn at 42.0 against its own face at 30.0   (12.00 ft out)
                     kitchen  drawn at 42.0 against its own face at 33.02  ( 8.98 ft out)
    windows          7 drawn, 16 refused -- of which 5 stood on their own element's face and
                     were dropped as "off-footprint", and 11 were correct refusals (the
                     placement put those rooms inland)

Two separate causes wearing one symptom, and they are worth keeping apart:

  * `_boundary_wall` asked whether a room touched the FOOTPRINT. On a dependency at x = -30
    that satisfied `x <= tol` for reasons of SIGN, and matched nothing on the other three
    faces -- so windows on real exterior walls were refused. `bounds` fixes this.
  * `render()` drew every exterior opening at `0`/`W`/`H`. The entry carried a position ALONG
    the wall (`at_ft`) and nothing across it, because on an INTERIOR entry `at_ft` means the
    perpendicular -- one key, two meanings. `edge_ft` fixes this, and its fallback is the
    ROOM's own face, never the footprint's.

The corpus is BYTE-IDENTICAL across the package: all sixteen shipped sheets hash
`4cfba3a0885ddccb` before and after, because on a one-rectangle house a boundary room's own
face IS the footprint edge.
"""
import glob
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, ROOT / "build" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


RP = _mod("render_plan")

# main block 0..40 x 0..42; west dependency -30..-7 x 20..33 -- the same two rectangles as
# workbench/app/src/derive.test.mjs's `twoElementRects`, so the two renderers are held to one
# answer on a case the frozen fixtures cannot carry (no plan in the corpus has a `block` tag).
MAIN = (0.0, 0.0, 40.0, 42.0)
DEP = (-30.0, 20.0, 23.0, 13.0)


def _rooms():
    return [
        {"id": "hall", "type": "entrance-hall", "width_ft": 40, "length_ft": 42,
         "exterior_walls": ["S", "N"],
         "windows": [{"wall": "N", "count": 1, "width_ft": 3}],
         "doors": [{"to": "exterior", "width_ft": 3, "wall": "S", "position_ft": 20}],
         "geometry": {"x_ft": 0.0, "y_ft": 0.0, "width_ft": 40.0, "depth_ft": 42.0}},
        {"id": "kitchen", "type": "kitchen", "width_ft": 23, "length_ft": 13,
         "exterior_walls": ["N"],
         "windows": [{"wall": "N", "count": 1, "width_ft": 3}],
         "doors": [{"to": "exterior", "width_ft": 3, "wall": "N", "position_ft": -18.5}],
         "geometry": {"x_ft": -30.0, "y_ft": 20.0, "width_ft": 23.0, "depth_ft": 13.0}},
    ]


BOUNDS = {"hall": MAIN, "kitchen": DEP}


# --------------------------------------------------------------- the door

def test_an_exterior_door_is_drawn_on_its_own_face_and_not_the_footprints():
    op = RP.derive_openings(_rooms(), 40.0, 42.0, bounds=BOUNDS)
    k = next(e for e in op["exterior"] if e["room"] == "kitchen")
    assert k["edge_ft"] == 33.0, (
        "the kitchen's element ends at y=33; before WP-11.14 this door was drawn at the "
        "footprint's 42.0, which is 8.98 ft north of the room, in open space")


def test_the_fallback_is_the_rooms_own_face_and_never_the_footprints():
    """With no element known the ROOM's face is the answer -- which is why the fix reaches a
    one-rectangle plan as the identity rather than as a change. Asserting a difference between
    the two calls would be asserting one this code does not have, and the JS twin says the
    same thing in the same words."""
    op = RP.derive_openings(_rooms(), 40.0, 42.0, bounds=None)
    k = next(e for e in op["exterior"] if e["room"] == "kitchen")
    assert k["edge_ft"] == 33.0
    assert k["edge_ft"] != 42.0


def test_a_room_in_no_element_is_not_given_element_zeros_box():
    """WP-11.9's rule. Element zero's north face is 42 and so is the footprint's; the room's
    own is 33, and 33 is the only honest answer for a room the map does not place."""
    op = RP.derive_openings(_rooms(), 40.0, 42.0, bounds={"hall": MAIN})
    k = next(e for e in op["exterior"] if e["room"] == "kitchen")
    assert k["edge_ft"] == 33.0


# --------------------------------------------------------------- the window

def test_a_window_on_its_own_element_face_is_drawn_rather_than_refused():
    op = RP.derive_openings(_rooms(), 40.0, 42.0, bounds=BOUNDS)
    kw = [w for w in op["windows"] if w["room"] == "kitchen"]
    assert len(kw) == 1, "the kitchen's north wall is exterior on its own element"
    assert kw[0]["edge_ft"] == 33.0


def test_without_bounds_that_window_is_refused_and_counted_rather_than_vanishing():
    """This is the half `bounds` really buys, and it is the bigger number: `_boundary_wall`
    asked about the FOOTPRINT, so five windows standing on a real exterior wall were dropped.
    They were COUNTED as off-footprint, never silently lost, which is why the symptom was a
    sheet with fewer windows than the record and no line saying so."""
    op = RP.derive_openings(_rooms(), 40.0, 42.0, bounds=None)
    assert [w for w in op["windows"] if w["room"] == "kitchen"] == []
    assert op["windows_off_footprint"] >= 1


# --------------------------------------------------------------- both renderers, one answer

def test_the_two_renderers_take_bounds_in_the_same_place():
    """`tests/fixtures/sheet_symbols/` cannot hold this pair to one answer -- no plan in the
    corpus carries a `block` tag, so the frozen fixtures have one element. The contract for
    this case is that both files take the argument, and both hand-built suites assert the same
    three numbers on the same two rectangles."""
    js = (ROOT / "workbench" / "app" / "src" / "sheet" / "derive.js").read_text()
    assert "export function doors(rooms, W, H, tol = 0.6, appendages = null, bounds = null)" in js
    assert "export function windows(rooms, W, H, tol = 0.6, extDoors = [], bounds = null)" in js
    assert "function boundaryWall(r, wall, W, H, tol, box)" in js
    jt = (ROOT / "workbench" / "app" / "src" / "derive.test.mjs").read_text()
    assert "twoElementRects" in jt, "the JS twin of this file's fixture is gone"
    for n in ("33", "42"):
        assert n in jt


# --------------------------------------------------------------- the guarantee

CORPUS_SHEET_SHA = "4cfba3a0885ddccb"


@pytest.mark.parametrize("engine", ["heuristic"])
def test_no_shipped_sheet_moves(engine, tmp_path):
    """THE GUARANTEE, measured on a `git archive HEAD` checkout before the package and on the
    working tree after. Deterministic: `engine="heuristic"`, which is why it is pinned and the
    `auto` figure is not."""
    import hashlib
    GEO = _mod("geometry")
    h = hashlib.sha256()
    n = 0
    for pf in (sorted(glob.glob(str(ROOT / "plans" / "*.json")))
               + sorted(glob.glob(str(ROOT / "plans" / "reference" / "*.json")))):
        d = json.loads(pathlib.Path(pf).read_text())
        if "levels" not in d:
            continue
        GEO._SOLVE_CACHE.clear()
        sol = GEO.solve(json.loads(json.dumps(d)), engine=engine)
        out = tmp_path / f"{pathlib.Path(pf).stem}.svg"
        RP.render(sol, str(out))
        h.update(out.read_bytes())
        n += 1
    assert n == 16
    assert h.hexdigest()[:16] == CORPUS_SHEET_SHA, (
        "a shipped sheet moved. On a one-rectangle house a boundary room's own face IS the "
        "footprint edge, so WP-11.14 must be the identity on every plan in this corpus")


# --------------------------------------------------------------- the DRAWING, not the derivation

def _tagged_solved():
    """`tidewater-georgian-careful` with its service programme in a west dependency, placed on
    the deterministic engine. Cached: it is the only solve in this file."""
    if not hasattr(_tagged_solved, "_v"):
        GEO = _mod("geometry")
        p = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())
        dep = {"kitchen", "pantry", "breakfast", "powder", "cellarstair"}
        for lv in p["levels"]:
            for r in lv["rooms"]:
                if r["id"] in dep:
                    r["block"] = "west-dependency"
                elif r["id"] == "backhall":
                    r["block"] = "west-dependency"
                    r["hyphen"] = True
        GEO._SOLVE_CACHE.clear()
        _tagged_solved._v = GEO.solve(p, engine="heuristic")
    return json.loads(json.dumps(_tagged_solved._v))


def test_the_drawing_reads_edge_ft_and_does_not_recompute_the_footprint_edge(tmp_path):
    """AND THE FIRST MUTATION PASS PROVED THIS TEST WAS MISSING. Every assertion above reads
    `derive_openings`' OUTPUT; none read the drawing. Reverting `render()`'s use of `edge_ft`
    -- the one line that actually put two doors in mid-air -- left all of them green.

    That is WP-11.10's own finding, one package later and in the same file: *"the first guard
    could not fail: a test reading `derive_openings` directly stayed green with `render()`'s
    call site reverted, so it reads the rendered plate instead."*

    So this renders the same tagged plan twice -- once as shipped, once with `edge_ft` stripped
    from every derived entry, which is exactly the fallback the defect was -- and requires the
    two plates to DIFFER. It cannot pass if the drawing ignores the field.
    """
    plan = _tagged_solved()
    a = tmp_path / "with.svg"
    RP.render(plan, str(a))

    real = RP.derive_openings

    def _strip(key):
        def f(*args, **kwargs):
            op = real(*args, **kwargs)
            for e in op.get(key) or []:
                e.pop("edge_ft", None)
            return op
        return f

    # ONE KEY AT A TIME, and a first version stripped both -- which could not fail on a
    # mutation to the DOOR path, because the windows alone still moved the plate and the two
    # renders duly differed. A guard that passes for the wrong half is the class this whole
    # package is about.
    for key in ("exterior", "windows"):
        RP.derive_openings = _strip(key)
        try:
            b = tmp_path / f"without_{key}.svg"
            RP.render(_tagged_solved(), str(b))
        finally:
            RP.derive_openings = real
        assert a.read_text() != b.read_text(), (
            f"the plate is identical with `edge_ft` removed from every {key} entry, so the "
            f"drawing is not reading it and those openings still go on the footprint's wall")


def test_the_tagged_plate_draws_no_exterior_door_on_the_footprint_edge(tmp_path):
    """The positive form, on the record rather than on pixels: every exterior door of the
    tagged plan carries an `edge_ft` equal to its own element's face, and two of them are NOT
    the footprint's north edge -- which is where all four were drawn before."""
    EL = _mod("elements")
    plan = _tagged_solved()
    H = plan["footprint"]["depth_ft"]
    ground = [r for lv in plan["levels"] if (lv.get("index") or 0) == 0
              for r in lv["rooms"] if r.get("geometry")]
    els = EL.elements(plan)
    bounds = EL.bounds_index(plan, ground)
    W = plan["footprint"]["width_ft"]
    op = RP.derive_openings(ground, W, H, bounds=bounds)
    off_block = 0
    for e in op["exterior"]:
        own = next((x for x in els if e["room"] in (x.get("rooms") or [])), None)
        if own is None:
            own = EL.element_of(plan, next(r for r in ground if r["id"] == e["room"]), els)
        assert own is not None, f"{e['room']} stands in no element"
        face = {"S": own["y"], "N": own["y"] + own["H"],
                "W": own["x"], "E": own["x"] + own["W"]}[e["wall"]]
        assert abs(e["edge_ft"] - face) < 0.02, (
            f"{e['room']}'s {e['wall']} door is drawn at {e['edge_ft']} against its own "
            f"element's face at {face}")
        # ANY wall, not just N: which face a dependency room presents is the placer's to
        # choose, and the first version of this counted only north doors -- a filter written
        # from a CP placement and then run on the deterministic one, where the kitchen's
        # exterior door is on its SOUTH face. Engine-specific numbers do not belong in a
        # `heuristic` test (CLAUDE.md: ratchet the deterministic figures only).
        if abs(face - {"N": H, "S": 0.0, "W": 0.0, "E": W}[e["wall"]]) > 0.02:
            off_block += 1
    assert off_block == 2, (
        f"{off_block} exterior doors stand clear of the footprint's own edge on `heuristic`; "
        "before WP-11.14 every one of them was drawn on it -- the backhall's at 29.95 against "
        "the footprint's 41.9, and the kitchen's at 8.93 against 0.0")
