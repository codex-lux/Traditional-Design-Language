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
import inspect
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


def _setback_rooms():
    """A room SET BACK from its element's own face, inside `_boundary_wall`'s 0.6 ft tolerance.

    The fixture above cannot tell the two branches of `_edge_of` apart: the kitchen fills DEP
    exactly, so the element's north face and the room's north face are both 33.0 and deleting
    the element-box branch entirely leaves every assertion green. An audit proved that by
    deleting it -- 9 of 9 passed. A guard that runs only where the two answers coincide is not
    a guard for the branch that chooses between them.

    Here the scullery stands at y 20.4..32.6 inside an element ending at 33.0. It is still ON
    the boundary (0.4 < 0.6), so an opening is placed; but the ELEMENT's face is 33.0 and the
    ROOM's is 32.6, and only the element's is right -- the wall the window is cut through is
    the element's envelope, not the room's inner face.
    """
    return [
        {"id": "hall", "type": "entrance-hall", "width_ft": 40, "length_ft": 42,
         "exterior_walls": ["S"],
         "doors": [{"to": "exterior", "width_ft": 3, "wall": "S", "position_ft": 20}],
         "geometry": {"x_ft": 0.0, "y_ft": 0.0, "width_ft": 40.0, "depth_ft": 42.0}},
        {"id": "scullery", "type": "kitchen", "width_ft": 23, "length_ft": 12.2,
         "exterior_walls": ["N"],
         "windows": [{"wall": "N", "count": 1, "width_ft": 3}],
         "doors": [{"to": "exterior", "width_ft": 3, "wall": "N", "position_ft": -18.5}],
         "geometry": {"x_ft": -30.0, "y_ft": 20.4, "width_ft": 23.0, "depth_ft": 12.2}},
    ]


def test_the_element_box_branch_is_the_one_that_decides_and_is_not_the_rooms_face():
    """THE BRANCH THE OTHER TESTS CANNOT SEE. With the element known the answer is the
    ELEMENT's face; with it unknown, the room's own. Here those are 33.0 and 32.6, so deleting
    the `box` branch of `_edge_of` changes this assertion and cannot pass either way."""
    rooms = _setback_rooms()
    with_box = RP.derive_openings(rooms, 40.0, 42.0, bounds={"hall": MAIN, "scullery": DEP})
    without = RP.derive_openings(rooms, 40.0, 42.0, bounds=None)
    a = next(e for e in with_box["exterior"] if e["room"] == "scullery")
    b = next(e for e in without["exterior"] if e["room"] == "scullery")
    assert a["edge_ft"] == 33.0, "with its element known, the door sits on the ELEMENT's face"
    assert b["edge_ft"] == 32.6, "with no element known, it falls back to the ROOM's own face"
    assert a["edge_ft"] != b["edge_ft"], (
        "the two branches must be distinguishable on this fixture, or neither is guarded")
    # AND THE WINDOW IS NOT MERELY MOVED, IT IS RECOVERED. Without the element the room's north
    # edge is nowhere near the FOOTPRINT's (32.6 against 42.0), so the wall is not a boundary at
    # all and the window is refused outright -- which is WP-11.14's "five authored windows
    # recovered from 'the placement puts this room on no such boundary wall'", reproduced on two
    # rectangles. Asserting a moved window here would assert an effect this code does not have.
    aw = [w for w in with_box["windows"] if w["room"] == "scullery"]
    bw = [w for w in without["windows"] if w["room"] == "scullery"]
    assert len(aw) == 1 and aw[0]["edge_ft"] == 33.0, (
        "with its element known the window is placed on the element's own face")
    assert bw == [], (
        "without the element the wall is not a boundary of the footprint, so the window is "
        "refused -- the defect WP-11.14 removed")


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
    three numbers on the same two rectangles.

    IT READS THE PARAMETER ORDER, NOT THE SIGNATURE TEXT. The first version pinned three whole
    `function` lines verbatim, so renaming a local `box` to `elBox` -- which leaves the code
    correct, and the JS suite green -- broke it. That is the literal-pin antipattern this very
    package removed from `tests/test_appendages.py`, reintroduced three times over in the file
    that removed it. The property is that `bounds` is LAST and `box` is LAST, in both spellings.
    """
    import re
    js = (ROOT / "workbench" / "app" / "src" / "sheet" / "derive.js").read_text()

    def params(name):
        m = re.search(r"function\s+" + name + r"\s*\(([^)]*)\)", js)
        assert m, f"{name} is gone from derive.js"
        return [p.split("=")[0].strip() for p in m.group(1).split(",") if p.strip()]

    assert params("doors")[-1] == "bounds", "doors must take bounds last, as Python does"
    assert params("windows")[-1] == "bounds", "windows must take bounds last, as Python does"
    assert len(params("boundaryWall")) == 6, "boundaryWall must take the element box"
    py = list(inspect.signature(RP.derive_openings).parameters)
    assert py[-1] == "bounds", (
        f"derive_openings takes {py[-1]} last; the two spellings must agree on position")
    jt = (ROOT / "workbench" / "app" / "src" / "derive.test.mjs").read_text()
    assert "twoElementRects" in jt, "the JS twin of this file's fixture is gone"


# --------------------------------------------------------------- the guarantee

# RE-DERIVED AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026), AND THE GUARANTEE THIS PIN STATES
# IS UNCHANGED. It says WP-11.14 is the IDENTITY on a one-rectangle house -- a boundary room's
# own element face IS the footprint edge -- and that is still true; what moved is the house.
# Main's WP-11.2 reads the massing's own bay count and its parity, resizing both shipped plans
# (Tidewater 60.0 x 40.08 -> 63 x 38.17, spec Colonial 40.0 x 38.44 -> 50.0 x 30.75), and this
# merge adds `data-t` to every wall band so the plate states its own thickness. Both change the
# bytes of every sheet. The pin is re-derived rather than removed because its subject -- that
# the element-aware exterior face changes nothing where there is one element -- is exactly what
# WP-11.16's record edit will falsify, loudly, when it tags a plan.
#
# AND THIS PIN WAS RE-DERIVED TWICE, BECAUSE THE FIRST READING WAS TAKEN ON A MUTATED TREE. A
# mutation harness checking the ported record table was interrupted between writing its first
# mutation and restoring the file, leaving `if False:` where `if all_diverged:` belongs -- so
# the sheet it hashed was one with the table's height reserved and the table not drawn. The
# figure looked exactly like a legitimate re-derivation. CLAUDE.md already records the shape
# (*"a mutation that silently does not REVERT makes every later result meaningless, and it
# reads as success"*); what this adds is that the damage outlives the harness, into any number
# measured afterwards. **After an interrupted mutation run, restore the file and re-derive
# every figure taken since.**
# WP-12.4 moved this by adding one `data-frame` attribute to the root <svg> of every plate,
# so the corpus hashes 535077ae0bca1ea2 now. **A re-pin on its own would have converted a
# defect into a claim** -- this pin's whole job is to say that WP-11.14 is the IDENTITY on a
# one-rectangle corpus, and overwriting the number tells the next reader that identity was
# re-verified when all that happened is that a new value was written down. So the STRIPPED
# hash is asserted too, and it is WP-11.14's own: re-derived over the same sixteen sheets with
# ` data-frame='...'` removed, it is 373d0116be7cecb8 to the character. 16 of 16 sheets carry
# the attribute and it adds 2,918 bytes in total.
#
# AND THE PIN CAUGHT A PACKAGE THAT HAD ALREADY BEEN COMMITTED. WP-12.4 verified the property
# by diffing all 44 plates with the attribute stripped and never ran the guard that MEASURES
# it, so three commits shipped red on an assertion whose own message names the property they
# were checking by hand. That is this repository's own *a package that commits before its
# build finishes learns what it broke from the build*, met by the package that had just
# written the sentence down.
CORPUS_SHEET_SHA = "c4210345a77b9904"
CORPUS_SHEET_SHA_NO_FRAME = "b620afc41d04b412"
# BOTH MOVED AT WP-12.9, AND THE MOVEMENT IS ACCOUNTED RATHER THAN RE-PINNED. Was
# 535077ae0bca1ea2 / 373d0116be7cecb8 (WP-11.14's stripped value, which WP-12.4 left alone).
#
# ONE SHEET OF SIXTEEN MOVED -- `tidewater-georgian-careful`, the only shipped plan that draws a
# chimney stack -- by 296 bytes: four tooltips gain "(a judgment, not a measurement)" and the
# title block gains one schedule row, so the canvas grows 962 -> 976 px and every row below the
# new line shifts by exactly 14. NOTHING IN THE DRAWING FIELD MOVED.
#
# THE ACCOUNTING WAS PROVED AND NOT REASONED. Removing the single field this package added --
# `judgment: true` on `kits/georgian-colonial-american.kit.json`'s `chimney.stack_plan_in` --
# and re-rendering gives all SIXTEEN sheets byte-identical to the previous commit. So the whole
# corpus movement is attributable to that one flag and to nothing else in the package, which is
# what a re-pin owes: WP-12.4 published "16 of 16 plates byte-identical" from a comparison that
# was not this one and shipped three commits on a red assertion.
#
# AND THE HARNESS THAT MEASURED IT WAS WRONG ONCE, WHICH IS WHY THERE WAS A CONTROL. The first
# sweep hashed the sixteen rendered files in FILENAME order; this test hashes them in
# `plans/*.json` order followed by `plans/reference/*.json`, and the two are not the same
# sequence. It produced a confident pair of hashes that were hashes of nothing anybody computes.
# Running the same harness over a `git archive HEAD` checkout and requiring it to reproduce
# 535077ae0bca1ea2 / 373d0116be7cecb8 is what caught it -- a re-pin whose instrument has not
# been shown to reproduce the OLD value is not a measurement, it is a new number.


@pytest.mark.parametrize("engine", ["heuristic"])
def test_no_shipped_sheet_moves(engine, tmp_path):
    """THE GUARANTEE, measured on a `git archive HEAD` checkout before the package and on the
    working tree after. Deterministic: `engine="heuristic"`, which is why it is pinned and the
    `auto` figure is not."""
    import hashlib
    import re as _re
    GEO = _mod("geometry")
    h = hashlib.sha256()
    bare = hashlib.sha256()          # the same sheets with WP-12.4's `data-frame` removed
    framed = 0
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
        b = out.read_bytes()
        s = _re.sub(rb" data-frame='[^']*'", b"", b)
        framed += (b != s)
        h.update(b)
        bare.update(s)
        n += 1
    assert n == 16
    # THE GUARANTEE, and it is the second assertion rather than the first. With WP-12.4's one
    # disclosure attribute removed, the corpus must still hash to what WP-11.14 measured -- so
    # a later package cannot quietly buy a green tick by re-pinning the raw number.
    assert framed == 16, f"only {framed} of 16 sheets carry a data-frame; the premise has moved"
    assert bare.hexdigest()[:16] == CORPUS_SHEET_SHA_NO_FRAME, (
        "a shipped sheet moved by more than the data-frame attribute accounts for. On a "
        "one-rectangle house a boundary room's own face IS the footprint edge, so WP-11.14 "
        "must be the identity on every plan in this corpus")
    assert h.hexdigest()[:16] == CORPUS_SHEET_SHA, (
        "a shipped sheet moved. If the assertion above passed, the movement is inside the "
        "data-frame attribute itself and the renderers' affine has changed")


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
