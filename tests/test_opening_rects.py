"""WP-12.2 — one opening rectangle, three callers.

`(x0, x1, sill, head)` was written out three times: `render_elevation._window` for a sash,
`render_elevation._entrance` for the door, and `export_dxf._win`. So was the LOOP around it —
each renderer independently read the face's bays, the two storey windows and the two floor
datums, skipped a blind bay and branched on the entrance door. **That duplication has already
cost this corpus once.** When the blind bay arrived (OQ 85) the SVG learned to skip it and the
DXF did not, so the CAD file went on drawing a window through a chimney; the export selftest
could not see it, because it round-trips FINDINGS and not geometry.

The guards here are written against the three ways that can come back:

1. **A second spelling of the rectangle.** An AST guard refuses a read of any of the five record
   fields the rectangle is made from — in any of the three callers, unless it is inside an
   f-string, which is a label and not a rectangle — and refuses a second derivation of the bay
   loop in any of them.
2. **A caller that stops consuming the one function.** The blind-bay delta is read from the
   function, the SVG and the DXF at once, and from the scene beside them — if any of the three
   derives its own list again, they stop moving together.
3. **A rectangle that is not the record's own arithmetic.** Exact float equalities, which a
   `round()` in the middle would break — and rounding there is not hypothetical: the first
   version rounded, and the SVG stopped being what it had drawn before the lift.

**THE BLIND BAY IS UNREACHABLE FROM THE CORPUS AND THEREFORE DRIVEN.** All sixteen plan records
produce zero blind bays today — WP-11.4 moved this house's stacks off the gable centre line and
onto its stated flues, so the bay a stack used to stand on is a plain window bay again. A test
that only rendered the shipped plans would pass with the skip deleted, which is WP-8.11's rule.
"""
import ast
import importlib.util
import json
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANS = ("tidewater-georgian-careful", "spec-builder-colonial")

# The record fields the rectangle is made from. Outside `build/elevation.py` one of these may be
# PRINTED and never COMPUTED WITH — the elevation sheet's legend reports the stated opening in its
# caption, which is a label and not a rectangle. That distinction is the rule the guard states;
# naming the one file that happens to carry a legend would be fitting the corpus that exists.
RECT_FIELDS = ("opening_width_in", "sill_height_above_floor_in", "head_height_above_floor_in",
               "door_leaf_width_in", "door_leaf_height_in")
CALLERS = ("render_elevation.py", "export_dxf.py", "scene.py")


def _labels_only(path):
    """Every read of a RECT_FIELDS key in `path` that is not inside an f-string interpolation."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and node.value in RECT_FIELDS):
            continue
        up, printed = node, False
        while up in parents:
            up = parents[up]
            if isinstance(up, ast.FormattedValue):
                printed = True
                break
        if not printed:
            out.append((node.lineno, node.value))
    return out


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "build", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _elevation(plan_id):
    """One elevation, on the HEURISTIC.

    `auto` reaches a CP proof on one machine and spends its budget on another, so a suite built
    on it would assert different geometry on different runners — which is what WP-12.0 measured
    happening to this very layer between two trees.
    """
    st, rf, el, ge = (_load(n) for n in ("structure", "roof", "elevation", "geometry"))
    plan = json.load(open(os.path.join(ROOT, "plans", f"{plan_id}.json")))
    res = ge.solve(plan, None, engine="heuristic")
    placed = res.get("plan", plan)
    section = st.build_section(placed, None, geometry_result=res)
    roof = rf.build_roof(placed, None, section=section)
    return el.build_elevation(placed, None, section=section, roof=roof)


@pytest.fixture(scope="module")
def elevations():
    return {p: _elevation(p) for p in PLANS}


# ------------------------------------------------------------------ one spelling, by reading

def test_the_rectangles_own_record_fields_are_read_in_one_file():
    """A dead local counts. The first pass of the lift left `door_w_in, door_h_in =
    ent["door_leaf_width_in"], ent["door_leaf_height_in"]` standing unused at the top of
    `_entrance`, three lines above the rectangle that already carried both numbers — which is
    how a second spelling grows back after the code that used it has gone.
    """
    offenders = [f"{fname}:{line} computes with {field!r}"
                 for fname in CALLERS
                 for line, field in _labels_only(os.path.join(ROOT, "build", fname))]
    assert not offenders, (
        "the opening rectangle's own record fields are read outside build/elevation.py:\n  "
        + "\n  ".join(offenders)
        + "\nThe rectangle comes from elevation.opening_rects(); read it from there.")
    # AND THE GUARD IS NOT VACUOUS: the legend really does print two of them, so the
    # f-string exemption is exercised rather than merely available.
    src = open(os.path.join(ROOT, "build", "render_elevation.py"), encoding="utf-8").read()
    assert src.count("opening_width_in") == 2, (
        "the sheet legend used to print the stated ground and upper opening widths; if that has "
        "changed, this guard's own exemption is no longer exercised by anything")


def test_every_caller_takes_its_bays_from_the_one_function():
    """Each of the three files calls `opening_rects` and none of them rebuilds the loop.

    The loop is the half that bit: `zip(centres_ft, kinds)` with a `blind` branch and a
    `door`-on-the-entrance-face branch, written out twice. It exists once now.
    """
    for fname in CALLERS:
        src = open(os.path.join(ROOT, "build", fname), encoding="utf-8").read()
        tree = ast.parse(src)
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == "opening_rects"]
        assert calls, f"{fname} draws openings and does not call elevation.opening_rects()"
        # AND IT DOES NOT WALK THE FACE'S OWN BAY LIST A SECOND TIME. The loop is the half that
        # bit — `zip(centres_ft, kinds)` with a `blind` branch — so any `zip` over the face's
        # own centres in one of these files is that loop growing back.
        zips = [n for n in ast.walk(tree)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "zip"
                and any(isinstance(c, ast.Constant) and c.value == "centres_ft"
                        for a in n.args for c in ast.walk(a))]
        assert not zips, (
            f"{fname}:{zips[0].lineno} zips the face's own centres again — that loop is "
            "elevation.opening_rects()'s, and having it twice is the OQ 85 defect's own shape")


# ------------------------------------------------------------------ the record's own arithmetic

def test_the_rectangle_is_the_records_own_numbers(elevations):
    """Width, centring, sill and head, read from both sides. Exact equality throughout: a
    `round()` anywhere in `opening_rects` breaks every one of these, and it must, because
    rounding moved the drawn SVG coordinates the first time this function was written."""
    el = _load("elevation")
    seen = 0
    for pid, elev in elevations.items():
        sw = elev["storey_windows"]
        floors = {s["index"]: s["grade_to_floor_ft"] * 12.0 for s in elev["section"]["storeys"]}
        for face in ("S", "N", "E", "W"):
            for r in el.opening_rects(elev, face)["rects"]:
                seen += 1
                # THE CONSTRUCTION, not the difference. `x1 - x0` reintroduces its own
                # rounding — 75.5315 - 36.8845 is not 38.647 in binary — so asserting that
                # would be a test of IEEE 754 rather than of this function. What must hold
                # exactly is that each edge is the centre plus or minus half the stated width,
                # unrounded, which is what a `round()` in `opening_rects` would break.
                assert r["x0_in"] == r["cx_in"] - r["width_in"] / 2.0, f"{pid} {r['id']} x0"
                assert r["x1_in"] == r["cx_in"] + r["width_in"] / 2.0, f"{pid} {r['id']} x1"
                if r["kind"] == "window":
                    si = 0 if r["storey"] == "ground" else 1
                    rec = sw[si]
                    assert r["width_in"] == rec["opening_width_in"], f"{pid} {r['id']}"
                    assert r["sill_in"] == floors[si] + rec["sill_height_above_floor_in"]
                    assert r["head_in"] == floors[si] + rec["head_height_above_floor_in"]
                else:
                    ent = elev["entrance"]
                    assert r["width_in"] == ent["door_leaf_width_in"]
                    assert r["sill_in"] == floors[0], "a door stands on its own floor"
                    assert r["head_in"] == floors[0] + ent["door_leaf_height_in"]
    assert seen == 72, f"expected 72 openings over the two shipped plans, read {seen}"


def test_every_rectangle_names_the_record_it_came_from(elevations):
    el = _load("elevation")
    for pid, elev in elevations.items():
        for face in ("S", "N", "E", "W"):
            got = el.opening_rects(elev, face)
            for r in got["rects"]:
                assert r["source"], f"{pid} {r['id']} names no record"
            for x in got["refused"]:
                assert x["why"] and x["source"], f"{pid} a refusal with no reason or no source"


# ------------------------------------------------------------------ the branch the corpus lost

def test_no_shipped_plan_reaches_a_blind_bay(elevations):
    """THE REASON THE TEST BELOW IS DRIVEN, asserted rather than remembered.

    OQ 85 blinds the bay a chimney stack stands on. WP-11.4 then moved this house's stacks off
    the gable centre line and onto the flues the plan states — 11.77 and 14.21 ft against bay
    centres of 6.79, 20.38 and 33.96 — so nothing is blinded any more, on any of the sixteen
    plan records. If this ever fails, the corpus has grown a blind bay and the fixture below has
    stopped being the only way to reach the skip.
    """
    for pid, elev in elevations.items():
        blind = sum(f.get("kinds", []).count("blind") for f in elev["faces"].values())
        assert blind == 0, (
            f"{pid} now states {blind} blind bay(s). Good — but re-read the driven fixture in "
            "test_a_blind_bay_is_skipped_by_all_three_callers, which exists because there were "
            "none.")


def test_a_blind_bay_is_skipped_by_all_three_callers(elevations, tmp_path):
    """THE CENTREPIECE, and the one assertion the shipped corpus cannot make.

    One bay is blinded by hand and the delta is read from all four surfaces at once: the
    function, the SVG, the DXF and the scene. A caller that derived its own list again would
    stay put while the other three moved — which is exactly the state this corpus was in
    between the blind bay landing in the SVG and the DXF learning about it.

    A POSITIVE COUNT FIRST. A selector that matches nothing makes a delta of zero look like a
    delta of zero, and this repository has shipped that inversion before.
    """
    el, re_, dx, sc = (_load(n) for n in
                       ("elevation", "render_elevation", "export_dxf", "scene"))
    ezdxf = pytest.importorskip("ezdxf")  # noqa: F841 — the DXF half needs the optional package
    elev = json.loads(json.dumps(elevations["tidewater-georgian-careful"]))
    face = "N"                                  # no entrance on it, so the delta is two windows
    bay = 1

    def surfaces(e):
        rects = el.opening_rects(e, face)["rects"]
        svg_path = tmp_path / "e.svg"
        re_.render_elevation(e, str(svg_path), face=face)
        svg = svg_path.read_text()
        dxf_path = tmp_path / "e.dxf"
        dx.export_elevation_dxf(e, str(dxf_path), face=face)
        doc = ezdxf.readfile(str(dxf_path))
        drawn = [x for x in doc.modelspace() if x.dxf.layer == "TDL-ELEV-OPENING"]
        return (len(rects), len(re.findall(r'<rect class="op"', svg)), len(drawn))

    before = surfaces(elev)
    assert all(n > 0 for n in before), f"a selector matched nothing: {before}"

    assert elev["faces"][face]["kinds"][bay] == "window", "the fixture must blind a WINDOW bay"
    elev["faces"][face]["kinds"][bay] = "blind"
    after = surfaces(elev)

    assert [b - a for b, a in zip(before, after)] == [2, 2, 2], (
        f"blinding one bay must remove one opening at each of two storeys from the function, "
        f"the SVG and the DXF alike; got {before} -> {after}")

    got = el.opening_rects(elev, face)
    assert not any(r["bay"] == bay for r in got["rects"])
    assert any(x["bay"] == bay and "blind" in x["why"] for x in got["refused"]), (
        "a blind bay must be REFUSED with its reason, not silently absent — the bay is real, "
        "it holds its place in the rhythm, and a stack stands on its axis")


def test_the_scene_drops_the_same_bay(elevations):
    """The third caller, read the same way. `build/scene.py` turns each rectangle into an
    `opening-frame` solid, so the same blinding must cost it the same two.

    THIS ASSERTION COUNTED EVERY SOLID UNTIL WP-12.6 AND ITS OWN DOCSTRING NAMED THE FRAMES.
    The two happened to be the same number while an opening was a bare rectangle; the moment
    the envelope was dressed, blinding a bay cost 22 solids — two frames, two meeting rails and
    eighteen glazing bars — and the guard went red on a package that had not touched the
    blinding at all. A count that is only incidentally the property it is named for is a guard
    that fails on the next unrelated change, which is the LOUD half of the selector fault this
    file already records (the quiet half goes blind instead).

    So it reads the frames, and it reads the DRESSING SEPARATELY — because a total count could
    never have said what matters here: that a bay's sash bars leave with the bay. A change that
    dropped the frame and left its muntins hanging in the wall plane is a real defect, it is
    invisible to any count of the whole, and it is exactly the shape WP-12.2's original defect
    had (the SVG learned to skip the bay and the DXF did not).
    """
    el, sc = _load("elevation"), _load("scene")
    elev = json.loads(json.dumps(elevations["tidewater-georgian-careful"]))
    section = elev["section"]

    class _States:
        def __init__(self): self.said = []
        def cannot(self, what, why, source, cls=None): self.said.append((what, why, source, cls))

    def frames(solids):
        return {s["id"] for s in solids if s["class"] == "opening-frame"}

    before = sc._openings(elev, section, _States())
    assert before, "the scene drew no openings at all"
    n_dress_before = len(before) - len(frames(before))
    assert n_dress_before > 0, (
        "no opening carries any dressing, so the second half of this test asserts nothing — "
        "WP-12.6 draws a sash and its bars on every drawn window")

    elev["faces"]["N"]["kinds"][1] = "blind"
    states = _States()
    after = sc._openings(elev, section, states)

    gone = frames(before) - frames(after)
    assert len(gone) == 2, (
        f"{len(frames(before))} -> {len(frames(after))} frames; dropped {sorted(gone)}")
    assert frames(after) < frames(before), "the blinded bay's frames are a strict subset"

    # and every solid dressing one of those two frames left with it
    ids_after = {s["id"] for s in after}
    orphans = sorted(i for i in ids_after
                     if any(i.startswith(g + "-") for g in gone))
    assert not orphans, (
        f"{len(orphans)} solid(s) still dress a bay the scene refused to draw: {orphans[:4]}")
    assert len(before) - len(after) > 2, (
        "the frames went and their dressing did not, which is the defect the line above is "
        "written to catch arriving from the other direction")

    assert any("blind" in why for _w, why, _s, _c in states.said), (
        "the scene must record the refusal, not merely draw two fewer frames")


def test_an_opening_has_one_name_and_the_scene_does_not_rebuild_it(elevations):
    """THE FRAME'S ID IS THE RECTANGLE'S OWN, AND THIS ASSERTION EXISTS BECAUSE A MUTATION
    PROVED NOTHING ELSE CHECKED IT.

    `opening_rects` has named every rectangle since WP-12.2 — `S-0-ground` for a sash,
    `S-3-door` for the entrance. WP-12.1's `_openings` rebuilt that name out of four fields
    (`{face}-{bay}-{storey}-{kind}`), and when WP-12.6 came to dress the opening it keyed the
    sash, its bars and its shutters off `r["id"]`. So one opening carried TWO names and every
    assertion relating a frame to its own dressing was comparing strings that could not match.

    It cost nothing that a reader could see — the picture was right, the ids were unique, the
    schema was satisfied — and it made the blind-bay guard one line above unable to notice a
    frame dropped while its glazing bars stayed in the wall plane. Restoring the hand-built name
    left every suite in this repository green, which is why this test is here rather than a
    comment.
    """
    el, sc = _load("elevation"), _load("scene")
    elev = json.loads(json.dumps(elevations["tidewater-georgian-careful"]))

    class _States:
        def cannot(self, *_a, **_k): pass

    want = set()
    for face in ("S", "N", "E", "W"):
        want |= {r["id"] for r in el.opening_rects(elev, face)["rects"]}
    assert want, "the elevation states no opening, so this compares two empty sets"

    solids = sc._openings(elev, elev["section"], _States())
    got = {s["id"] for s in solids if s["class"] == "opening-frame"}
    assert got == want, (
        f"the scene names {len(got - want)} opening(s) the elevation does not: "
        f"{sorted(got - want)[:3]}; and misses {sorted(want - got)[:3]}")

    # and every other solid on an opening is prefixed by one of those names, so a dressing
    # solid can always be traced to the frame it dresses
    stray = sorted(s["id"] for s in solids if s["class"] != "opening-frame"
                   and not any(s["id"].startswith(w + "-") for w in want))
    assert not stray, f"{len(stray)} dressing solid(s) name no opening: {stray[:4]}"


# ------------------------------------------------------------------ the other refusals

def test_a_storey_that_states_no_window_is_refused_and_not_invented(elevations):
    el = _load("elevation")
    elev = json.loads(json.dumps(elevations["tidewater-georgian-careful"]))
    elev["storey_windows"] = elev["storey_windows"][:1]          # the upper storey states none
    got = el.opening_rects(elev, "N")
    assert got["rects"], "the ground storey still states one"
    assert all(r["storey"] == "ground" for r in got["rects"])
    assert any(x.get("storey") == "upper" for x in got["refused"]), (
        "an unstated upper window is a refusal with a reason, not an absence")


def test_a_one_storey_house_gets_one_row_of_windows(elevations):
    """THE DEFECT THE LIFT REMOVED FROM SIX OF THE ELEVEN PLANS THAT DRAW AN ELEVATION.

    Both renderers resolved the upper storey as
    `next((s for s in storeys if s["index"] == 1), ground)` — falling back to the GROUND storey
    when there is no second one — and then unconditionally drew a second row of windows at that
    datum, using the upper storey window's own sill and head above floor. On a one-storey house
    that is a whole row of openings the record does not hold, standing above the ground row in
    the cornice zone. Measured across the plan corpus: **six of the eleven plans that build an
    elevation state only storey 0**, and each was drawing eleven `op` rectangles where it holds
    six, with eighteen shutters where it holds eight.

    It cost nothing on either shipped plan, because both are two-storey — which is why this
    package's first measurement, taken over those two, said the lift changed nothing.
    **Verifying a corpus-wide change on the plans that happen to ship is verifying it on two of
    sixteen.**

    AND THE REFUSAL CARRIES THE RIGHT REASON OF TWO. A storey the section does not state is a
    fact about the BUILDING; a storey that exists with no floor datum is a fact about the
    RECORD. They call for different actions, so they do not share a message.
    """
    el = _load("elevation")
    elev = json.loads(json.dumps(elevations["tidewater-georgian-careful"]))
    two = el.opening_rects(elev, "N")
    assert {r["storey"] for r in two["rects"]} == {"ground", "upper"}

    elev["section"]["storeys"] = [s for s in elev["section"]["storeys"]
                                  if s.get("index") == 0]
    one = el.opening_rects(elev, "N")
    assert {r["storey"] for r in one["rects"]} == {"ground"}, \
        "a one-storey house drew an upper row of windows"
    assert len(one["rects"]) * 2 == len(two["rects"])
    up = [x for x in one["refused"] if x.get("storey") == "upper"]
    assert len(up) == len(one["rects"]), "every bay must say why it has no upper opening"
    assert all("no storey 1" in x["why"] for x in up), \
        f"the refusal must name the building's own storey count, not a missing datum: {up[:1]}"

    # and the OTHER cause keeps its own message
    elev["section"]["storeys"][0].pop("grade_to_floor_ft")
    none = el.opening_rects(elev, "N")
    assert not none["rects"]
    assert any("no floor datum" in x["why"] for x in none["refused"]), \
        "a storey that exists without a datum is a different refusal from a storey that does not"


def test_a_door_bay_off_the_entrance_face_draws_a_window(elevations):
    """PRESERVED BEHAVIOUR, pinned because it is a judgment rather than an accident.

    Both renderers already did this before the lift: a bay the record calls a door draws a
    window on any face but the entrance front. Which faces carry a door is the elevation's
    judgment and not this function's, so the lift carried the behaviour across rather than
    correcting it — and a silent correction inside a refactor is the thing this package is
    about.

    **AND THE CONDITION IS UNREACHABLE FROM THE GENERATOR**, so this test drives it because
    nothing in the corpus can. `_face_bays` writes `kinds[mid] = "door"` only under
    `has_entrance`, which is `f == entrance_face`; swept over all sixteen plan records, 44 faces
    are built with 11 door bays and 0 of them off the entrance front. The branch is kept — it is
    a fallback, not a check, and deleting it would draw a door on a wall with no entrance
    composition to dress it — and driven, so that it cannot quietly stop working.
    """
    el = _load("elevation")
    elev = json.loads(json.dumps(elevations["tidewater-georgian-careful"]))
    assert elev["entrance_face"] != "E"
    elev["faces"]["E"]["kinds"][0] = "door"
    kinds = {r["kind"] for r in el.opening_rects(elev, "E")["rects"] if r["bay"] == 0}
    assert kinds == {"window"}, f"a door bay off the entrance face drew {kinds}"
    ent_kinds = {r["kind"] for r in
                 el.opening_rects(elev, elev["entrance_face"])["rects"] if r["storey"] == "ground"}
    assert "door" in ent_kinds, "and the entrance front still draws its door"
