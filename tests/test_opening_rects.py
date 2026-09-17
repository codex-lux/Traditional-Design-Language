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

def _record_opening(elev, r):
    """The plan's own record of the opening a rectangle was drawn from: the room's window or
    exterior door on that wall, at that position. Read from the SECTION's placed record -- the
    one placement the section, the roof and the elevation share -- and never from the rect."""
    placed = elev["section"]["geometry"]
    lv = placed["levels"][r["storey"] == "upper"]
    room = next(x for x in lv["rooms"] if x["id"] == r["room"])
    if r["kind"] == "door":
        return next(d for d in room["doors"] if d.get("to") == "exterior"
                    and abs(float(d["position_ft"]) - r["along_ft"]) < 1e-9)
    return next(w for w in room["windows"]
                if any(abs(float(p) - r["along_ft"]) < 1e-9 for p in (w.get("positions_ft") or [])))


def test_the_rectangle_is_the_records_own_numbers(elevations):
    """Width, centring, sill and head, read from both sides. Exact equality throughout: a
    `round()` anywhere in `opening_rects` breaks every one of these, and it must, because
    rounding moved the drawn SVG coordinates the first time this function was written.

    WP-13.3: THE WIDTH AND THE CENTRE ARE THE PLAN'S, not the storey window's and not the
    rhythm's. Each rectangle is a placed window or exterior door the plan's own record carries
    on that wall (`_record_opening` finds it from the section's placed record, at the rect's
    own `along_ft`), so its width is that opening's `width_ft` in inches and its centre is
    `face_u_ft` of that position -- the one conversion, in the face's own datum. The sill and
    head are still the storey window's (the plan states no window height) and a door's leaf
    height is the entrance's, the one door height the record states; both are named on the
    rect. And the count is of PLACED openings: the 72 rhythm rectangles over the two shipped
    plans became the 34 the plans place and this file draws on the heuristic -- Tidewater 22
    (S 11, N 7, E 3, W 1) and the spec Colonial 12 (S 6, N 4, E 0, W 2), READ off the rects
    per face rather than summed by hand -- and pinned so that a regression to drawing the
    rhythm, 72 again, cannot pass as 'more'. The Tidewater W face PLACES two windows and draws
    one: the primary bedroom's upper sash at y 10.547 (3.5 ft wide) overlaps the west stack
    at 11.77 clear, and `opening_rects` refuses it by name (OQ 85) --
    `test_no_shipped_plan_reaches_a_blind_bay` pins that one refusal. This count was 35 while
    the N and W faces were mirrored, which put that sash 27.8 ft from the stack it stands on.
    """
    el = _load("elevation")
    seen = {}
    for pid, elev in elevations.items():
        sw = elev["storey_windows"]
        floors = {s["index"]: s["grade_to_floor_ft"] * 12.0 for s in elev["section"]["storeys"]}
        fp = elev["section"]["footprint"]
        t_ft = elev["section"]["wall"]["exterior_in"] / 12.0
        for face in ("S", "N", "E", "W"):
            for r in el.opening_rects(elev, face)["rects"]:
                seen[pid] = seen.get(pid, 0) + 1
                # THE CONSTRUCTION, not the difference. `x1 - x0` reintroduces its own
                # rounding — 75.5315 - 36.8845 is not 38.647 in binary — so asserting that
                # would be a test of IEEE 754 rather than of this function. What must hold
                # exactly is that each edge is the centre plus or minus half the stated width,
                # unrounded, which is what a `round()` in `opening_rects` would break.
                assert r["x0_in"] == r["cx_in"] - r["width_in"] / 2.0, f"{pid} {r['id']} x0"
                assert r["x1_in"] == r["cx_in"] + r["width_in"] / 2.0, f"{pid} {r['id']} x1"
                rec_op = _record_opening(elev, r)
                assert r["cx_in"] == el.face_u_ft(face, r["along_ft"], fp["clear_width_ft"],
                                                  fp["clear_depth_ft"], t_ft) * 12.0, \
                    f"{pid} {r['id']}: the centre is not the plan's position in the face's datum"
                placed = next(p for p in elev["faces"][face]["placed"]
                              if p["room"] == r["room"] and p["storey"] == r["storey"]
                              and p["along_ft"] == r["along_ft"])
                if rec_op.get("width_ft"):
                    assert placed["width_declared"] is True
                    assert r["width_in"] == float(rec_op["width_ft"]) * 12.0, \
                        f"{pid} {r['id']}: the width is not the plan's own"
                else:
                    # a width the record left unstated is the plan sheet's own default, and
                    # the placed entry says so rather than passing it off as authored
                    assert placed["width_declared"] is False, f"{pid} {r['id']}"
                    want = (_load("render_plan").DEFAULT_EXT_DOOR_FT if r["kind"] == "door"
                            else 3.0) * 12.0        # `derive_openings`' own `or 3` for a window
                    assert r["width_in"] == want, f"{pid} {r['id']}: not the sheet's default"
                if r["kind"] == "window":
                    si = 0 if r["storey"] == "ground" else 1
                    rec = sw[si]
                    assert r["record"] is rec
                    assert r["sill_in"] == floors[si] + rec["sill_height_above_floor_in"]
                    assert r["head_in"] == floors[si] + rec["head_height_above_floor_in"]
                else:
                    ent = elev["entrance"]
                    assert r["sill_in"] == floors[0], "a door stands on its own floor"
                    assert r["head_in"] == floors[0] + ent["door_leaf_height_in"]
    # PER PLAN, BECAUSE A TOTAL OVER TWO HOUSES CANNOT SAY WHICH ONE MOVED.
    #
    # This read `seen == 72` until the 16 Sep merge, and the merge moved it to 64 -- all of it
    # on the Tidewater plan, 40 -> 32, and none of it on the spec Colonial. The cause is
    # WP-11.16's record edit meeting WP-12.2's lift: tagging that plan's service programme into
    # a west dependency takes the MAIN BLOCK from 63 ft and 7 bays to 45 ft and 5 bays, and
    # 2 bays x 2 storeys x 2 long faces is exactly the 8 that left (S and N each 14 -> 10, the
    # gable ends unmoved at 6). The rectangle arithmetic every assertion above tests did not
    # change; the house did.
    #
    # Re-derive per plan before touching either number. A bump of the total would have been a
    # measurement's clothes on a house nobody looked at.
    assert seen == {"tidewater-georgian-careful": 32, "spec-builder-colonial": 32}, (
        f"the opening census over the two shipped plans moved: {seen}. Derive WHICH plan and "
        f"why -- the bay count, the storey count and the faces -- before re-pinning it.")


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

# THE ONE PLACED WINDOW THE SHIPPED CORPUS REFUSES FOR A STACK (WP-13.3), pinned by name.
# The Tidewater primary bedroom's upper W sash is placed at y 10.547 ft, 3.5 ft wide, and the
# west stack stands at 11.77 ft clear (13.06 in the roof's outside frame), 1.83 ft wide: they
# overlap by about 1.45 ft, so the sash is refused (OQ 85) and the W face draws one window of
# the two the plan places there. It was invisible while the N and W faces were mirrored, which
# put that sash 27.8 ft from the stack it stands on. Pinned as a SET so that a change in either
# direction shows: a second refusal is a placement to look at, and none is either a fix in
# `openings.py` or the refusal going blind.
STACK_REFUSED_ON_THE_SHIPPED_PLANS = {("tidewater-georgian-careful", "W", "primary", "upper")}


def test_no_shipped_plan_reaches_a_blind_bay(elevations):
    """THE REASON THE TEST BELOW IS DRIVEN, asserted rather than remembered.

    OQ 85 blinds the bay a chimney stack stands on. WP-11.4 then moved this house's stacks off
    the gable centre line and onto the flues the plan states — 11.77 and 14.21 ft against bay
    centres of 6.79, 20.38 and 33.96 — so no RHYTHM bay is blinded any more, on any of the
    sixteen plan records. If this ever fails, the corpus has grown a blind bay.

    AND SINCE WP-13.3 THE RULE REACHES PLACED WINDOWS, and the shipped corpus reaches it ONCE
    (`STACK_REFUSED_ON_THE_SHIPPED_PLANS`). The driven test below is still the only route to the
    refusal on the N face and through all three callers at once, so it stays driven; what this
    asserts is that the corpus's own case is exactly the one named, no more and no fewer.
    """
    el = _load("elevation")
    got = set()
    for pid, elev in elevations.items():
        blind = sum(f.get("kinds", []).count("blind") for f in elev["faces"].values())
        assert blind == 0, (
            f"{pid} now states {blind} blind bay(s). Good — but re-read the driven fixture in "
            "test_a_stack_on_a_placed_window_is_refused_by_all_three_callers, which exists "
            "because there were none.")
        # READ THE SOURCE, NOT A WORD: the placer's own refusal prose says "chimney" and
        # "stack" about a breast it kept a sash clear of, and the first draft of this premise
        # matched that word and convicted the placer's refusals as the elevation's. The
        # elevation's stack refusal names `stack_axes_ft` as its source and nothing else does.
        for f in "SNEW":
            for x in el.opening_rects(elev, f)["refused"]:
                if x["source"].endswith(".stack_axes_ft"):
                    got.add((pid, f, x["room"], x["storey"]))
    assert got == STACK_REFUSED_ON_THE_SHIPPED_PLANS, (
        f"placed openings refused for a stack: {sorted(got)} against the pinned "
        f"{sorted(STACK_REFUSED_ON_THE_SHIPPED_PLANS)} -- a placement moved, or the refusal did")


def _stack_on(elev, face, u_ft, half_ft=None):
    """Drive a stack onto a face at `u_ft`, in place, the way `build_elevation` records one:
    `stack_axes_ft` and `stack_half_width_ft` on the face record. The RHYTHM's blind-bay rule
    is not re-run here on purpose -- what is under test is the PLACED opening's refusal, and
    the two are different rules for different questions (`opening_on_a_stack`'s docstring)."""
    elev["faces"][face]["stack_axes_ft"] = [u_ft]
    if half_ft is not None:
        elev["faces"][face]["stack_half_width_ft"] = half_ft
    return elev


def test_a_stack_on_a_placed_window_is_refused_by_all_three_callers(elevations, tmp_path):
    """THE CENTREPIECE, and the one assertion the shipped corpus cannot make.

    WP-13.3: the opening is a PLACED window now, not a rhythm bay, so what is driven is a stack
    standing on one -- the roof record's own two fields on the face record, set by hand -- and
    the delta is read from all four surfaces at once: the function, the SVG, the DXF and the
    scene. A caller that derived its own list again would stay put while the other three moved,
    which is exactly the state this corpus was in between the blind bay landing in the SVG and
    the DXF learning about it. (Until WP-13.3 this test set `kinds[bay] = "blind"` on the
    rhythm; that mutation moves nothing now, because a rhythm centre is no longer an opening.)

    A POSITIVE COUNT FIRST. A selector that matches nothing makes a delta of zero look like a
    delta of zero, and this repository has shipped that inversion before. And the delta is
    MEASURED off the placed list -- how many placed windows on this face a stack at that axis
    overlaps -- rather than assumed to be two: an upper window need not stand over a lower one
    any more, which is the whole subject of this package.
    """
    el, re_, dx, sc = (_load(n) for n in
                       ("elevation", "render_elevation", "export_dxf", "scene"))
    ezdxf = pytest.importorskip("ezdxf")  # noqa: F841 — the DXF half needs the optional package
    elev = json.loads(json.dumps(elevations["tidewater-georgian-careful"]))
    face = "N"                                  # no entrance on it, so no door is involved
    target = next(p for p in elev["faces"][face]["placed"]
                  if p["kind"] == "window" and p["storey"] == "ground")
    half = elev["faces"][face]["stack_half_width_ft"]
    expect = [p for p in elev["faces"][face]["placed"] if p["kind"] == "window"
              and el.opening_on_a_stack(p["u_ft"], p["width_ft"], [target["u_ft"]], half)]
    assert expect and target in expect, "the fixture must put the stack on at least one window"

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

    _stack_on(elev, face, target["u_ft"])
    after = surfaces(elev)

    k = len(expect)
    assert [b - a for b, a in zip(before, after)] == [k, k, k], (
        f"a stack on a placed window must remove the {k} window(s) it stands on from the "
        f"function, the SVG and the DXF alike; got {before} -> {after}")

    got = el.opening_rects(elev, face)
    assert not any(r["room"] == target["room"] and r["along_ft"] == target["along_ft"]
                   for r in got["rects"])
    hit = [x for x in got["refused"] if x.get("room") == target["room"] and "stack" in x["why"]]
    assert hit, (
        "a window a stack stands on must be REFUSED with its reason, not silently absent — "
        "the plan placed it, and a stack stands where it would be (OQ 85)")
    assert "OQ 85" in hit[0]["why"] and str(round(target["u_ft"], 2)) in hit[0]["why"], hit[0]


def test_a_door_on_a_stack_is_drawn_and_counted_not_deleted(elevations):
    """The half OQ 85 keeps: a DOOR on a stack's axis is as impossible as a window on one, and
    deleting an entrance is not a decision this generator may take on its own, so the door is
    drawn and the collision reaches `count_of_openings_on_the_axis_of_a_chimney_stack`, where
    `window-on-the-chimney-axis` fires and a human decides.

    WP-13.5: the face is READ rather than named. This said *"the N face's placed back doors,
    which is where the Tidewater plan seats three"*, and after the service programme moved into
    the dependency that record declares, the main block's N face carries none and its E face
    carries one. Which face has a back door is a property of the placement; the property under
    test is not."""
    el = _load("elevation")
    elev = json.loads(json.dumps(elevations["tidewater-georgian-careful"]))
    face = next(f for f in ("N", "E", "W", "S") if f != elev["entrance_face"]
                and any(p["kind"] == "door" for p in (elev["faces"][f].get("placed") or [])))
    door = next(p for p in elev["faces"][face]["placed"] if p["kind"] == "door")
    _stack_on(elev, face, door["u_ft"])
    got = el.opening_rects(elev, face)
    assert any(r["kind"] == "door" and r["room"] == door["room"] for r in got["rects"]), \
        "the door was deleted"
    assert not any(x.get("room") == door["room"] and x.get("kind") == "door"
                   for x in got["refused"])
    # the elevation record is rebuilt around the mutated face so the measurement reads it
    m = el._derive_measurements(elev)
    assert m["count_of_openings_on_the_axis_of_a_chimney_stack"] >= 1, \
        "the collision was neither resolved nor reported — it just vanished"


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

    # WP-13.3: a stack driven onto a placed N window, the same driver as the test above, and
    # the delta measured off the placed list rather than assumed to be two
    face = "N"
    target = next(p for p in elev["faces"][face]["placed"]
                  if p["kind"] == "window" and p["storey"] == "ground")
    half = elev["faces"][face]["stack_half_width_ft"]
    k = sum(1 for p in elev["faces"][face]["placed"] if p["kind"] == "window"
            and el.opening_on_a_stack(p["u_ft"], p["width_ft"], [target["u_ft"]], half))
    assert k > 0
    _stack_on(elev, face, target["u_ft"])
    states = _States()
    after = sc._openings(elev, section, states)

    gone = frames(before) - frames(after)
    assert len(gone) == k, (
        f"{len(frames(before))} -> {len(frames(after))} frames; dropped {sorted(gone)}")
    assert frames(after) < frames(before), "the blinded bay's frames are a strict subset"

    # and every solid dressing one of those two frames left with it
    ids_after = {s["id"] for s in after}
    orphans = sorted(i for i in ids_after
                     if any(i.startswith(g + "-") for g in gone))
    assert not orphans, (
        f"{len(orphans)} solid(s) still dress a bay the scene refused to draw: {orphans[:4]}")
    assert len(before) - len(after) > k, (
        "the frames went and their dressing did not, which is the defect the line above is "
        "written to catch arriving from the other direction")

    assert any("stack" in why for _w, why, _s, _c in states.said), (
        "the scene must record the refusal, not merely draw fewer frames")


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
    n_upper = sum(1 for r in two["rects"] if r["storey"] == "upper")
    n_ground = sum(1 for r in two["rects"] if r["storey"] == "ground")
    assert n_upper and n_ground

    elev["section"]["storeys"] = [s for s in elev["section"]["storeys"]
                                  if s.get("index") == 0]
    one = el.opening_rects(elev, "N")
    assert {r["storey"] for r in one["rects"]} == {"ground"}, \
        "a one-storey house drew an upper row of windows"
    # WP-13.3: the ground row is the PLACED ground row, unmoved, and the upper row is not
    # 'half of the rects' -- an upper storey need not carry one opening per lower one -- but
    # every placed upper opening, each refused by name
    assert len(one["rects"]) == n_ground
    # the PLACED upper openings' refusals, apart from the placer's own (a window the placer
    # never seated is refused for the placer's reason on any storey count)
    up = [x for x in one["refused"] if x.get("storey") == "upper"
          and "placer refused" not in x["why"]]
    assert len(up) == n_upper, "every placed upper opening must say why it is not drawn"
    assert all("no storey 1" in x["why"] for x in up), \
        f"the refusal must name the building's own storey count, not a missing datum: {up[:1]}"

    # and the OTHER cause keeps its own message
    elev["section"]["storeys"][0].pop("grade_to_floor_ft")
    none = el.opening_rects(elev, "N")
    assert not none["rects"]
    assert any("no floor datum" in x["why"] for x in none["refused"]), \
        "a storey that exists without a datum is a different refusal from a storey that does not"


def test_a_placed_door_off_the_entrance_face_is_a_leaf_and_not_a_doorcase(elevations, tmp_path):
    """THE BEHAVIOUR THIS REPLACES was pinned as a judgment: a RHYTHM bay the record called a
    door drew a window on any face but the entrance front, because which faces carry a door
    was the elevation's judgment. Since WP-13.3 which faces carry a door is the PLAN's: the
    Tidewater placement seats three exterior doors on its N face (the passage, the back hall
    and the kitchen), and each is drawn there as a door -- a leaf -- and NOT dressed as the
    entrance. Only the rect that carries `entrance` takes the casing and the sidelights; a
    renderer dressing every door rect would put a Gibbs doorcase on the kitchen door.

    Read off the emitted SVG: the N face draws its door leaves (`class="dr"`) and NO casing
    (`class="cs"`); the entrance front draws exactly one casing, around the one door that
    carries the composition. (The DXF exporter dresses every door rect with the casing and is
    outside this slice; the rect says `entrance: None` and that is the one condition it needs.)
    """
    el, re_ = _load("elevation"), _load("render_elevation")
    elev = json.loads(json.dumps(elevations["tidewater-georgian-careful"]))
    # WP-13.5 MOVED THE PLACEMENT AND WITH IT THE BACK DOORS. The docstring above describes
    # THREE exterior doors on the N face; with the service programme in the dependency this
    # record declares, the N face of the main block carries NONE and the E face carries one.
    # So the face is read rather than named, and a SECOND door is DRIVEN onto it -- the
    # property under test is "EVERY door off the front is a leaf and none is dressed", and one
    # subject cannot tell "every" from "the first". The corpus offers at most one back door on
    # any face of either shipped plan now, measured; a fixture that waits for the corpus to
    # offer two is measuring the corpus (WP-8.11).
    face = next(f for f in ("N", "E", "W", "S") if f != elev["entrance_face"]
                and any(p["kind"] == "door" for p in (elev["faces"][f].get("placed") or [])))
    assert elev["entrance_face"] != face
    placed = elev["faces"][face]["placed"]
    real = next(p for p in placed if p["kind"] == "door")
    driven = json.loads(json.dumps(real))
    driven["u_ft"] = round(float(real["u_ft"]) + 8.0, 3)
    placed.append(driven)
    doors = [r for r in el.opening_rects(elev, face)["rects"] if r["kind"] == "door"]
    assert len(doors) >= 2, "the fixture needs a face with placed doors that is not the front"
    assert all(r["entrance"] is None for r in doors), "a back door carried the entrance composition"
    assert all(r["record"] is None for r in doors)
    svg_path = tmp_path / "n.svg"
    re_.render_elevation(elev, str(svg_path), face=face)
    svg = svg_path.read_text()
    assert len(re.findall(r'<rect class="dr', svg)) == len(doors), "a placed door was not drawn as a leaf"
    assert not re.findall(r'<rect class="cs"', svg), "a back door was dressed as the entrance"

    front = el.opening_rects(elev, elev["entrance_face"])["rects"]
    ents = [r for r in front if r["kind"] == "door" and r["entrance"]]
    assert len(ents) == 1, "exactly one door on the front carries the entrance composition"
    re_.render_elevation(elev, str(svg_path), face=elev["entrance_face"])
    assert len(re.findall(r'<rect class="cs"', svg_path.read_text())) == 1
