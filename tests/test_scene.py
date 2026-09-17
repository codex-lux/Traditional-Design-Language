"""WP-12.1 — the scene record.

The guards are written against the three things this layer can get wrong that nothing else
would notice:

1. **A number that disagrees with the record it came from.** The scene is derived from the
   section, the roof and the placement, and its whole claim is that it is the SAME building.
   So the assertions are agreements — the envelope against the slabs, the rooms inside the
   envelope, the datums against the storeys — read from both sides rather than pinned.
2. **A thing drawn that the record does not hold.** Every solid must name the record path it
   came from and the weakest `kind` among its numbers, and a form this layer cannot construct
   must appear in `not_modelled` with a reason rather than be approximated by one it can.
3. **A dimension invented in this file.** A source-reading test refuses a numeric literal
   outside the named editorial allowlist, which is `tests/test_profiles.py`'s discipline
   (no arc arithmetic in JavaScript) applied to a different smuggling route.

Every assertion here was mutation-checked, and two of them were rewritten because the first
version could not fail — recorded in `docs/reports/wp-12.1-the-scene-record.md`.
"""
import ast
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANS = ("tidewater-georgian-careful", "spec-builder-colonial")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "build", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def one_element_plans(tmp_path_factory):
    """The two shipped plans as ONE-RECTANGLE records, written outside the repository.

    Returned as paths rather than as dicts because `scene._build_from_plan` takes a path, and
    because three tests in this file rebuild from the same record to check that they agree —
    a second reader opening `plans/` would be comparing two different houses. The write is
    under `tmp_path_factory`; nothing a test does may write inside the repository (CLAUDE.md,
    WP-11.10).
    """
    from conftest import as_one_element
    d = tmp_path_factory.mktemp("scene-one-element")
    out = {}
    for name in PLANS:
        plan = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
        stripped = as_one_element(plan)
        if name == "tidewater-georgian-careful":
            assert stripped, (
                "the Tidewater record stopped carrying a container: this whole fixture was "
                "written for WP-13.5's service wing and is now stripping nothing")
        path = str(d / f"{name}.json")
        json.dump(plan, open(path, "w"), indent=2)
        out[name] = path
    return out


@pytest.fixture(scope="module")
def scenes(one_element_plans):
    """Both shipped plans on the HEURISTIC, deliberately, and with the Tidewater plan's
    massing container STRIPPED.

    `auto` reaches a CP proof on one machine and spends its budget on another, so a suite
    built on it would assert different geometry on different runners — which is what WP-12.0
    measured happening to the elevation between two trees. The heuristic is reproducible, and
    the engine-dependent figures belong in a report, not a pin.

    **WP-13.5 PUT A SERVICE WING ON THE TIDEWATER RECORD AND THE SCENE LAYER IS NOT ELEMENT
    AWARE.** `roof.build_roof` derives ONE roof over the main block (`build/roof.py`'s own
    `wing_step_down` docstring records that it is main-block-only), so the scene of the shipped
    record is a roof over a 45 ft block beside 34 ft of walled wing with nothing over it. Every
    test in this file is about the SCENE LAYER's own arithmetic — does a plane slope, does an
    opening stand on the face it names, does the envelope agree with the slabs — and on a house
    whose roof does not reach a third of its walls those questions cannot be asked at all. So
    the fixture states a one-rectangle house, which is what every one of these assertions was
    written against, and `test_the_shipped_roof_does_not_reach_the_service_wing` below holds
    the OTHER half: the shipped record's own measured offset, named as the finding it is.

    Stripping and re-serialising is needed rather than handing a dict over, because
    `_build_from_plan` takes a PATH. The copy is written under `tmp_path_factory`, never
    inside the repository — CLAUDE.md's WP-11.10 rule, a test that writes a tracked corpus
    file is a data-loss bug whatever its `finally` says.
    """
    scene_m = _load("scene")
    out = {}
    for name in PLANS:
        s, section, err = scene_m._build_from_plan(one_element_plans[name], engine="heuristic")
        assert not err, f"{name}: {err}"
        out[name] = (s, section)
    return out


def test_the_shipped_roof_does_not_reach_the_service_wing():
    """WHAT THE FIXTURE ABOVE STEPS AROUND, MEASURED ON THE RECORD AS SHIPPED.

    `test_the_roof_sits_over_the_house_and_not_beside_it` is a test of ONE ARITHMETIC — the
    roof and the walls are laid from two corners of one rectangle, half an exterior wall apart
    — and WP-13.5 made the Tidewater record a house with two rectangles. On the shipped record
    that assertion fails by **34.0 ft**, which is not the origin defect it is written for at
    all: it is `roof.build_roof` covering the MAIN BLOCK and nothing else, so the west wing is
    walls and floor with open sky over them. Left as a red assertion it would have read as a
    regression in the origin; deleted it would have read as nothing.

    So the finding is asserted POSITIVELY and with its figure. The roof's west edge must stand
    at the main block's west edge, and the walls must run a long way further west than that —
    otherwise this test has stopped being about the wing. Both halves, because a guard that
    only says *the numbers differ* passes equally on a roof that covers everything and one
    that covers nothing.

    `oq/the-roof-record-and-the-plan-record-do-not-share-an-origin` is the ORIGIN half and
    stands. This is the element half, and it belongs to the same package's own finding that
    the drawing stack below the placer is not element aware — `build/roof.py::wing_step_down`
    names it in its own words, and refuses to publish a hyphen depth it cannot derive.
    """
    scene_m = _load("scene")
    scene, _section, err = scene_m._build_from_plan(
        os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"), engine="heuristic")
    assert not err, err
    planes = [s for s in scene["solids"] if s["class"] == "roof-plane"]
    walls = [s for s in scene["solids"] if s["class"] == "wall" and s.get("face")]
    assert planes and walls, "premise: the shipped scene draws both a roof and faced walls"
    roof_w = min(p[0] for s in planes for p in s["geometry"]["vertices"])
    wall_w = min(s["geometry"]["origin"][0] for s in walls)
    assert wall_w < roof_w - 10.0, (
        "premise: the shipped record no longer carries a wing west of the roof "
        f"(walls from {wall_w:.3f}, roof from {roof_w:.3f})")
    assert roof_w > -2.0, (
        f"the roof's west edge moved to {roof_w:.3f} ft: `build_roof` has either learnt about "
        "massing elements — in which case delete this test and re-measure the origin one — or "
        "gained a second defect")


def _extent(g):
    """The axis-aligned extent of any of the schema's primitives, as three (lo, hi) pairs.

    Written once here rather than per test: a containment assertion that only understood boxes
    would have said nothing about the roof planes and nothing about the openings, which are the
    two things this phase added and the two that have gone wrong.
    """
    if g["type"] == "box":
        o, s = g["origin"], g["size"]
        return [(o[i], o[i] + s[i]) for i in range(3)]
    if g["type"] == "plane":
        v = g["vertices"]
        return [(min(p[i] for p in v), max(p[i] for p in v)) for i in range(3)]
    if g["type"] == "prism":
        poly = g["polygon"]
        return [(min(p[0] for p in poly), max(p[0] for p in poly)),
                (min(p[1] for p in poly), max(p[1] for p in poly)),
                (g["z0"], g["z1"])]
    if g["type"] == "extrude":
        u = [(min(p[0] for p in g["outline"]), max(p[0] for p in g["outline"])),
             (min(p[1] for p in g["outline"]), max(p[1] for p in g["outline"]))]
        thick = (g["at"], g["at"] + g["thickness"])
        return {"xz": [u[0], thick, u[1]],
                "yz": [thick, u[0], u[1]],
                "xy": [u[0], u[1], thick]}[g["plane"]]
    raise AssertionError(f"no extent rule for a {g['type']} — add one rather than skipping it")


# ------------------------------------------------------------------ the record is well formed

def test_both_scenes_validate_against_the_schema(scenes):
    sv = _load("schema_validators")
    v = sv.compiled(os.path.join(ROOT, "schema", "scene.schema.json"))
    for name, (scene, _s) in scenes.items():
        errs = sorted(v.iter_errors(scene), key=lambda e: list(e.path))
        assert not errs, f"{name}: " + "; ".join(
            f"{'/'.join(str(p) for p in e.path)}: {e.message[:120]}" for e in errs[:3])


def test_every_solid_has_a_unique_id(scenes):
    for name, (scene, _s) in scenes.items():
        ids = [s["id"] for s in scene["solids"]]
        dupes = {i for i in ids if ids.count(i) > 1}
        assert not dupes, f"{name}: {sorted(dupes)[:5]}"
        assert len(ids) > 20, f"{name} drew only {len(ids)} solids — the fixture is not biting"


def test_every_solid_names_the_record_it_came_from_and_its_weakest_kind(scenes):
    """A solid with no source is a solid nobody can argue with, which is the whole of P6."""
    for name, (scene, _s) in scenes.items():
        for s in scene["solids"]:
            assert s.get("source", {}).get("record"), f"{name}: {s['id']} has no source"
            assert s.get("kind") in ("measured", "editorial", "derived", "judgment"), \
                f"{name}: {s['id']} has kind {s.get('kind')!r}"


def test_no_solid_carries_a_colour(scenes):
    """Colour is nomenclature here: `ink` and `tone` are names the viewer resolves from
    tokens.css. A hex in the record is a decision a reader cannot argue with and a second
    palette nobody maintains."""
    for name, (scene, _s) in scenes.items():
        blob = json.dumps(scene)
        assert "#" not in blob.replace("\\u0023", ""), f"{name} carries a '#' somewhere"


# ------------------------------------------------------------------ agreement with the record

def test_the_envelope_and_the_slabs_agree(scenes):
    """Two derivations of one rule by different routes: the exterior wall boxes (clear
    footprint grown outward by the stated thickness) and `export_ifc.slab_boxes`. They must
    describe the same rectangle, or the model and the IFC export are two buildings.

    THIS IS THE ASSERTION THAT CAUGHT THE REAL DEFECT. The first version of `_walls` grew
    every exterior wall INWARD, so the envelope came out exactly the clear footprint — each
    wall the right thickness in the right place along its own axis, and the whole 2.58 ft too
    small. No per-wall assertion would have seen it.
    """
    scene_m = _load("scene")
    for name, (scene, section) in scenes.items():
        ag = scene_m.agreement(scene, section)
        assert ag["envelope_vs_slab_ft"] <= 0.01, f"{name}: {ag}"


def test_every_placed_room_lies_inside_the_envelope(scenes):
    """A containment, not an equality — and it must be POSITIVE by about half a wall, because
    the rooms keep their clear dimensions and the walls wrap them."""
    scene_m = _load("scene")
    for name, (scene, section) in scenes.items():
        ag = scene_m.agreement(scene, section)
        assert ag["rooms_inside_envelope_ft"] > 0, \
            f"{name}: a room lies outside the envelope by {-ag['rooms_inside_envelope_ft']} ft"


def test_the_datums_are_the_sections_own_storey_heights(scenes):
    scene_m = _load("scene")
    for name, (scene, section) in scenes.items():
        assert scene_m.agreement(scene, section)["datums_vs_storeys_ft"] == 0.0, name
        # and the ladder is ordered, which is what makes it a ladder
        zs = [d["z_ft"] for d in scene["datums"]]
        assert zs == sorted(zs), f"{name}: datums out of order"


def test_the_roof_sits_over_the_house_and_not_beside_it(scenes):
    """THE FINDING THIS TEST EXISTS FOR. `roof_outline` and `elevation_profile` lay the roof
    out from (0, 0) over the OUTSIDE footprint while `wall_lines` lays the walls out from
    (0, 0) over the CLEAR one — two origins half an exterior wall apart, so read literally the
    roof sits 1.29 ft east and north of the house it covers. It has never mattered because no
    surface drew both. `oq/the-roof-record-and-the-plan-record-do-not-share-an-origin`.

    THE POPULATION IS PER ELEMENT, AND THAT IS THE MERGE'S OWN FINDING RATHER THAN A
    LOOSENING (16 Sep 2026). This swept every wall in the record against every roof plane,
    which is the same question on a one-rectangle house and a different one the moment a plan
    carries a dependency: `tidewater-georgian-careful` is tagged since WP-11.16, its walls run
    x[-35.292, 46.292] over three masses, and its roof covers the main block's
    x[-1.292, 46.288]. Read across the elements that is a 34 ft offset and the assertion
    failed; read within the element the roof is derived for it is 0.004 ft, the
    `section.footprint` rounding residue and nothing more.

    **The 34 ft is a real fact and it is not this assertion's**: the dependency and the hyphen
    have no roof at all, because `roof.py` derives one roof from `section.footprint`. That is
    named in `not_modelled` now and asserted by the test below, so scoping here hides nothing.
    """
    for name, (scene, _s) in scenes.items():
        planes = [s for s in scene["solids"] if s["class"] == "roof-plane"]
        if not planes:
            continue
        roofed = {s.get("element") or "main" for s in planes}
        walls = [s for s in scene["solids"] if s["class"] == "wall" and s.get("face")
                 and (s.get("element") or "main") in roofed]
        assert walls, f"{name}: roof planes over {roofed} and no wall in any of them"
        px = [p[0] for s in planes for p in s["geometry"]["vertices"]]
        py = [p[1] for s in planes for p in s["geometry"]["vertices"]]
        wx = [v for s in walls for v in (s["geometry"]["origin"][0],
                                         s["geometry"]["origin"][0] + s["geometry"]["size"][0])]
        wy = [v for s in walls for v in (s["geometry"]["origin"][1],
                                         s["geometry"]["origin"][1] + s["geometry"]["size"][1])]
        assert abs(min(px) - min(wx)) < 0.05 and abs(max(px) - max(wx)) < 0.05, \
            f"{name}: the roof is offset from the walls in x by " \
            f"{min(px) - min(wx):.3f}/{max(px) - max(wx):.3f} ft"
        assert abs(min(py) - min(wy)) < 0.05 and abs(max(py) - max(wy)) < 0.05, \
            f"{name}: the roof is offset from the walls in y"


def test_a_mass_this_layer_cannot_roof_is_named_and_not_silently_left_bare(scenes):
    """THE OTHER HALF OF THE TEST ABOVE, AND THE REASON SCOPING IT WAS NOT A LOOSENING.

    `roof.py` derives ONE roof from `section.footprint`, the main block's rectangle. `_walls`
    reads each wall's own `element` and `_slabs` takes `export_ifc.slab_boxes`, which is per
    element per storey — so on `tidewater-georgian-careful`, tagged since WP-11.16, the west
    dependency and the hyphen are drawn with their walls and their floors and nothing above
    them. The model shows two masses open to the sky and, until this, said nothing at all
    about it: a reader would have read the picture as the building rather than as the part of
    it this layer can construct, which is the fake-pass shape one dimension up.

    It is a DISCLOSURE and not a fix. A per-element roof needs a stated ridge relation between
    two masses and no record in this corpus carries one — the half of
    `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` WP-11.6 left open.

    The assertion is a CENSUS in both directions, so it cannot go quiet: every element the
    record states and the roof does not cover must be named, and an element the roof DOES
    cover must not be. Fifteen of the sixteen shipped plans carry no `footprint.blocks` at all
    and take no entry, so a seventeenth tagged plan arrives here rather than passing silently.
    """
    for name, (scene, _s) in scenes.items():
        roofed = {s.get("element") or "main"
                  for s in scene["solids"] if s["class"] == "roof-plane"}
        stated = {(b.get("id") or "main"): (b.get("role") or "main")
                  for b in (scene.get("elements") or [])}
        said = [n for n in scene["not_modelled"] if n.get("source") == "footprint.blocks"]
        named = {n["what"].rsplit("element ", 1)[-1].strip("'\"") for n in said}
        for bid, role in stated.items():
            if role == "main" or bid in roofed:
                assert bid not in named, \
                    f"{name}: {bid!r} is roofed and is named as unroofed"
                continue
            assert bid in named, (
                f"{name}: the record states a {role} element {bid!r}, the roof does not reach "
                f"it, and nothing in not_modelled says so — it is drawn open to the sky")
        for n in said:
            assert "oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it" \
                in n["why"], f"{name}: the refusal does not name the question it belongs to"


def test_a_roof_plane_slopes_and_is_not_a_box(scenes):
    """THE ONE THE PICTURE EARNED, AND NO OTHER ASSERTION IN THIS FILE COULD HAVE.

    The first version wrote each roof plane as a `prism` — one polygon extruded vertically
    between the eave height and the ridge height. That is a BOX that spans the roof's rise:
    the right footprint, the right two heights, and no slope anywhere in it. All three
    agreement figures accepted it, because all three measure the PLAN extent, and the
    fifteen tests here passed. The house rendered as a two-storey block with a lid, and that
    is how it was found — by drawing the scene and looking at it, which is WP-9.6's lesson
    (*"Lucas found it by looking at the sheet; nothing in the suite could"*).

    So the assertion is about the SHAPE and not the extent: a roof plane must carry per-vertex
    heights, and at least two of them must differ. A plane whose vertices are all at one height
    is a flat roof, and this corpus's gable family does not have one.
    """
    for name, (scene, _s) in scenes.items():
        planes = [s for s in scene["solids"] if s["class"] == "roof-plane"]
        if not planes:
            continue                      # a style with no migrated pitch draws none, and says so
        for pl in planes:
            g = pl["geometry"]
            assert g["type"] == "plane", \
                f"{name}: {pl['id']} is a {g['type']}, which cannot hold a slope"
            zs = {round(v[2], 3) for v in g["vertices"]}
            assert len(zs) >= 2, \
                f"{name}: {pl['id']} has every vertex at z={zs} — that is a flat roof, not a slope"
            # and the two heights must be the eave and the ridge the record states, not any two
            datums = {d["class"]: round(d["z_ft"], 3) for d in scene["datums"]}
            assert zs == {datums["eave"], datums["ridge"]}, \
                f"{name}: {pl['id']} spans {sorted(zs)}, not the record's eave and ridge " \
                f"{sorted({datums['eave'], datums['ridge']})}"


def test_a_gable_occupies_its_own_wall(scenes):
    """An E or W gable is a constant-x plane and an N or S gable a constant-y one, AND it
    occupies the same slab of space as the exterior wall it stands on.

    WP-12.1 wrote this test the weaker way — `at` against the OUTER face of the wall extent —
    and by doing so it ratified the very defect WP-12.2 then found in the openings. Under the
    schema's contract `at` is the LOW face and the extrusion runs along the plane's POSITIVE
    axis, so a gable whose `at` is the outer face stands one wall thickness PROUD of the house:
    a 1.29 ft ledge over the east and north walls of the Tidewater plan, drawn above the eave
    where a reader looks. The old assertion was true of that gable, which is what a test written
    against the wrong contract does.

    The interval is read from both sides now — the gable's `[at, at + thickness]` against the
    wall's own box on the same axis — so a shift in either direction fails. The tolerance is the
    `section.footprint` rounding residue and nothing more.

    AND THE WALL IS THE GABLE'S OWN ELEMENT'S (16 Sep 2026). `mine` was every wall carrying
    this face, and on the tagged Tidewater plan the E face is carried by the main block AND by
    the hyphen, whose east wall stands at x = -7.0 — so the sweep read the gable's own wall as
    [-7.0, 46.292] and convicted a gable sitting correctly in [44.997, 46.292]. A gable belongs
    to one mass; the wall it stands on is that mass's.
    """
    for name, (scene, _s) in scenes.items():
        walls = [s for s in scene["solids"] if s["class"] == "wall" and s.get("face")]
        for g in [s for s in scene["solids"] if s["class"] == "gable"]:
            f, geo = g["face"], g["geometry"]
            axis = 0 if f in ("E", "W") else 1
            assert geo["plane"] == ("yz" if axis == 0 else "xz"), \
                f"{name}: gable {f} is not a constant-{'x' if axis == 0 else 'y'} plane"
            el = g.get("element") or "main"
            mine = [w for w in walls if w["face"] == f and (w.get("element") or "main") == el]
            assert mine, f"{name}: no exterior wall on face {f} of element {el!r} for its " \
                         f"gable to stand on"
            lo = min(w["geometry"]["origin"][axis] for w in mine)
            hi = max(w["geometry"]["origin"][axis] + w["geometry"]["size"][axis] for w in mine)
            assert abs(geo["at"] - lo) < 0.05 and \
                abs(geo["at"] + geo["thickness"] - hi) < 0.05, (
                f"{name}: gable {f} occupies [{geo['at']}, {geo['at'] + geo['thickness']}] "
                f"where its own wall is [{lo}, {hi}] — a gable that is not in its wall is a "
                f"ledge over the eave")


# ------------------------------------------------------------------ the three states

def test_a_form_it_cannot_construct_is_named_and_not_approximated():
    """DRIVEN, not read off the corpus: both shipped plans declare a side-gable, so a test of
    the hip branch against the shipped records would assert nothing (WP-8.11's fixture rule).
    A copy of the record declares a hip; the scene must then draw NO roof plane and say the
    form's name in `not_modelled` — never approximate it with the gable it can build."""
    scene_m = _load("scene")
    geometry, structure, roof_m = _load("geometry"), _load("structure"), _load("roof")
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    plan.setdefault("declared", {})["roof_form"] = "hip"
    placed = geometry.solve(plan, None, 250, engine="heuristic")
    section = structure.build_section(placed, None, geometry_result=placed)
    roof = roof_m.build_roof(placed, None, section=section)
    scene = scene_m.build_scene(placed, section, roof, None)
    assert [s for s in scene["solids"] if s["class"] == "roof-plane"] == [], \
        "a hip was approximated by the planes of a gable"
    hips = [n for n in scene["not_modelled"] if "hip" in json.dumps(n)]
    assert hips, "the hip is neither drawn nor named — an omission is not a refusal"
    assert hips[0]["why"], "the refusal carries no reason, which is half of what a refusal is"


def test_the_note_states_the_count_even_when_it_is_zero(scenes):
    """An empty list is not the question closed (WP-11.6). The note must say `0 things` rather
    than fall silent, or a scene that models everything reads like a scene nobody checked."""
    for name, (scene, _s) in scenes.items():
        assert "not modelled" in scene["note"]
        assert str(len(scene["not_modelled"])) in scene["note"], name


def test_the_openings_are_drawn_on_every_face(scenes, one_element_plans):
    """WP-12.2 replaced this test's predecessor rather than deleting it.

    Until 12.2 an exterior wall was a plain box carrying a `not_modelled` entry that said so,
    because a blank wall must not read as a wall with no windows, and
    `test_the_walls_say_they_have_no_openings_yet` was written to FAIL when the openings landed.
    It did. What replaces it asserts the other side of the same rule: every face carries
    openings now, and NOTHING still says they are missing.
    """
    # RE-CUT AT WP-13.3: the openings are the PLAN's placed openings on each face, so a face
    # the plan places nothing on draws nothing -- the spec Colonial's E wall carries no placed
    # window -- and that is the record, not a wall declared unmodelled. What is asserted is
    # that every face the plan places an opening on draws one, that the frames on a face are
    # exactly the elevation's own rectangles for it, and that the shipped corpus still
    # exercises the branch (both plans place openings on at least three faces).
    EL = _load("elevation")
    for name, (scene, _s) in scenes.items():
        assert not any(n.get("class") == "opening" and "every face" in n.get("what", "")
                       for n in scene["not_modelled"]), (
            f"{name} draws openings and still declares them not modelled")
        by_face = {}
        for solid in scene["solids"]:
            if solid["class"] == "opening-frame":
                by_face[solid["face"]] = by_face.get(solid["face"], 0) + 1
        # the elevation the scene was built from, rebuilt the way `_build_from_plan` builds it
        # (heuristic, one placement for the section, the roof and the elevation)
        geo, st, rf = _load("geometry"), _load("structure"), _load("roof")
        plan = json.load(open(one_element_plans[name]))
        geo._SOLVE_CACHE.clear()
        res = geo.solve(plan, None, engine="heuristic")
        sec = st.build_section(res, None, geometry_result=res)
        ev = EL.build_elevation(res, None, section=sec, roof=rf.build_roof(res, None, section=sec))
        want = {f: len(EL.opening_rects(ev, f)["rects"]) for f in "SNEW"}
        assert by_face == {f: n for f, n in want.items() if n}, f"{name}: {by_face} against {want}"
        assert len(by_face) >= 3, f"{name}: the fixture draws openings on {sorted(by_face)} only"


def test_an_opening_frame_cites_the_placed_opening_and_never_a_rhythm(scenes):
    """WP-13.3 (the lead's pass). Since the elevation draws the plan's PLACED openings, an
    opening rect's provenance is `elevation.faces.<face>.placed`; the frame solid went on
    citing `elevation.faces.<face>.centres_ft` beside it -- the rhythm the elevation now keeps
    for its other readers and draws as nothing. A provenance naming a record the solid was not
    built from is a source pointer that resolves and does not agree (the Phase 11 trap), one
    layer over. Premise first: there are frames to check."""
    n = 0
    for name, (scene, _s) in scenes.items():
        for s in scene["solids"]:
            if s.get("class") != "opening-frame":
                continue
            n += 1
            also = s["source"].get("also") or []
            assert also and all(a.endswith(".placed") for a in also), f"{name}: {s['id']} cites {also}"
            assert not any("centres_ft" in a for a in also), f"{name}: {s['id']} cites the rhythm"
            assert s["source"]["record"].startswith("plan.levels["), f"{name}: {s['id']} {s['source']}"
    assert n > 0, "premise: no opening frame in either scene, so nothing was checked"


def test_an_opening_is_extruded_into_its_own_wall_and_not_out_of_it(scenes):
    """THE CONTRACT THE SCHEMA STATES, read back from the record.

    `at` is the LOW face of the wall and `thickness` always runs along the plane's POSITIVE
    axis. Written the other way — `at` on the OUTSIDE face of each wall, extruding positively —
    the south and west openings go into their walls and the north and east ones stand PROUD of
    them, and the model renders as a house with blocks stuck to two of its sides. No count and
    no plan-extent measurement can see that; it was found by looking at the picture.
    """
    for name, (scene, section) in scenes.items():
        t = (section["wall"]["exterior_in"]) / 12.0
        b = scene["bounds"]
        seen = 0
        for solid in scene["solids"]:
            if solid["class"] != "opening-frame":
                continue
            seen += 1
            g = solid["geometry"]
            assert g["thickness"] > 0, f"{name} {solid['id']} extrudes backwards"
            assert abs(g["thickness"] - t) < 0.01, f"{name} {solid['id']} is not a wall thick"
            axis = 1 if g["plane"] == "xz" else 0
            lo, hi = g["at"], g["at"] + g["thickness"]
            assert b["min"][axis] - 0.01 <= lo and hi <= b["max"][axis] + 0.01, (
                f"{name} {solid['id']} on face {solid['face']} is extruded to "
                f"[{lo}, {hi}], outside the building's own "
                f"[{b['min'][axis]}, {b['max'][axis]}]")
        assert seen > 0, f"{name} drew no openings at all"


def test_every_solid_lies_inside_the_declared_bounds(scenes):
    """A WHOLE-MEASURE ASSERTION, and it is the one that found WP-12.1's `bounds`.

    The frame's origin is the CLEAR SW corner, so an exterior wall grows outward to `-t` and the
    outside envelope starts negative. WP-12.1 stated `min: [0, 0, 0]` and `max` off the
    section's OUTSIDE footprint — the right SIZE in the wrong PLACE, offset by one exterior wall
    thickness, 1.292 ft on the Tidewater plan. **None of the three agreement figures could see
    it**, because all three compare the walls, the slabs and the datums to each other and not
    one of them reads `bounds`; a viewer framing the model from it would simply have drawn the
    house off centre.

    CONTAINMENT AND NOT EQUALITY. `section.footprint` is rounded to two places, so the stated
    frame and the drawn solids differ by up to 0.004 ft — the same residue the agreement table
    reports — and rounding one to the other to make an equality hold would be OQ 48's error in
    a new place. The tolerance is 0.01 ft: two and a half times the residue, and three hundred
    times smaller than the defect it caught.
    """
    for name, (scene, _s) in scenes.items():
        b = scene["bounds"]
        worst, who = 0.0, None
        for solid in scene["solids"]:
            for axis, (lo, hi) in enumerate(_extent(solid["geometry"])):
                over = max(b["min"][axis] - lo, hi - b["max"][axis])
                if over > worst:
                    worst, who = over, f"{solid['id']} ({solid['class']}) on {'xyz'[axis]}"
        assert worst <= 0.01, f"{name}: {who} stands {worst:.3f} ft outside the stated frame"


def test_the_frame_is_tight_and_not_merely_large_enough(scenes):
    """THE CONTAINMENT TEST ABOVE IS HALF A GUARD, AND A MUTATION PROVED IT (WP-12.7).

    Since WP-12.7 `bounds` is the UNION of the solids' own extents rather than the section's
    footprint plus a list of hand-written exceptions — which removes by construction the class of
    defect WP-12.1 shipped and WP-12.6 had to patch again for the chimneys. But it also makes
    containment nearly free: swapping the axes in `scene._extent`'s `xz` branch was measured to
    leave **the whole suite green**, because the wrong mapping makes the frame a SUPERSET. A
    frame too large is a real defect in the other direction — a viewer frames the model from it
    and zooms out past the house — and nothing could see it.

    So the frame is asserted TIGHT: on every axis some solid must reach it. This file keeps its
    own extent reader (per-axis pairs, a different shape from `scene._extent`'s two corners), so
    the two are independent readers of the same four primitives and neither can ratify the
    other's mistake.
    """
    for name, (scene, _s) in scenes.items():
        b = scene["bounds"]
        got_lo = [None, None, None]
        got_hi = [None, None, None]
        for solid in scene["solids"]:
            for axis, (lo, hi) in enumerate(_extent(solid["geometry"])):
                got_lo[axis] = lo if got_lo[axis] is None else min(got_lo[axis], lo)
                got_hi[axis] = hi if got_hi[axis] is None else max(got_hi[axis], hi)
        for axis in range(3):
            # z reaches the ridge, which is a DATUM and not a solid on a plan whose roof this
            # layer cannot construct, so the frame is legitimately taller than the solids there.
            slack_lo = b["min"][axis] - got_lo[axis]
            slack_hi = got_hi[axis] - b["max"][axis]
            assert slack_hi <= 0.01, (
                f"{name}: a solid stands {slack_hi:.3f} ft past the frame on {'xyz'[axis]}")
            if axis < 2:
                assert abs(slack_lo) <= 0.01, (
                    f"{name}: the frame reaches {b['min'][axis]} on {'xyz'[axis]} and the "
                    f"nearest solid only {got_lo[axis]} — {abs(slack_lo):.3f} ft of empty frame")
                assert abs(got_hi[axis] - b["max"][axis]) <= 0.01, (
                    f"{name}: the frame reaches {b['max'][axis]} on {'xyz'[axis]} and the "
                    f"furthest solid only {got_hi[axis]}")


def test_a_hearth_is_drawn_only_where_one_is_authored(scenes):
    """A fire is authored and never inferred (WP-11.4). The Tidewater record states three;
    every hearth solid must trace back to a room that states one."""
    scene, _s = scenes["tidewater-georgian-careful"]
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    stated = {r["id"] for lv in plan["levels"] for r in lv["rooms"] if r.get("hearth")}
    drawn = {s["room"] for s in scene["solids"] if s["class"] == "hearth"}
    assert drawn, "no hearth was drawn on a record that states three"
    assert drawn <= stated, f"a hearth was drawn in a room that authors none: {drawn - stated}"


# ------------------------------------------------------------------ the file itself

def test_the_scene_file_states_no_dimension_as_a_literal():
    """`build/scene.py` may carry a number only as a NAMED constant with an `editorial:` note
    above it. Anything else is a dimension smuggled into the layer whose whole rule is that it
    invents none.

    THE EXEMPTIONS ARE STRUCTURAL AND EACH IS NAMED, because a blanket one is how this kind of
    guard stops biting: 0, 1, 2, 3 and 12 are indices, halves and the inches in a foot; the
    second argument of `round()` is a precision; a `candidates=` default is a search-pool size.
    Anything else — 22.5, 0.35, 16 — is a measurement whatever it is called.

    The first version of this test flagged all four exempt shapes AND its own allowed constant,
    because `ast.walk` does not prune: `continue` on the assignment still yielded its child
    Constant. A guard that fires on the thing it exempts is a guard somebody will widen until
    it fires on nothing.
    """
    src = open(os.path.join(ROOT, "build", "scene.py")).read()
    tree = ast.parse(src)
    # CUT_HEIGHT_FT is the one editorial DIMENSION; DEFAULT_CANDIDATES is a search-pool
    # size, named for a different reason (see the module) and exempt for that reason.
    # `_MAX_DRAWN_RISERS` is a bound on the WORK and not a dimension: see its own comment.
    # It is named here rather than exempted by value precisely so a reader has to write the
    # sentence saying which it is.
    allowed_names = {"CUT_HEIGHT_FT", "DEFAULT_CANDIDATES", "_MAX_DRAWN_RISERS"}
    assigned = {t.id for node in ast.walk(tree) if isinstance(node, ast.Assign)
                for t in node.targets if isinstance(t, ast.Name)}
    assert allowed_names <= assigned, "the named editorial constant is gone from the file"
    # AND THE GUARD'S OWN BLIND SPOT, WRITTEN DOWN (WP-12.8). `STRUCTURAL` exempts 2.0 as an
    # index or a halving, and `CHIMNEY_ABOVE_RIDGE_FT = 2.0` -- an invented height that stood
    # every chimney on every plan 6 ft short of its own record -- sailed through this test for
    # exactly that reason. A structural exemption by VALUE cannot tell 2.0-the-index from
    # 2.0-the-dimension, so this test is a floor and not a ceiling: it catches a number nobody
    # named, and says nothing about a number named wrongly.

    exempt = set()          # by node identity, so the exemption cannot leak to a sibling
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id in allowed_names for t in node.targets):
            for c in ast.walk(node.value):
                exempt.add(id(c))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "round" and len(node.args) > 1:
            exempt.add(id(node.args[1]))
    STRUCTURAL = {0, 1, 2, 3, 12, 0.0, 1.0, 2.0, 3.0, 12.0}
    offenders = [(n.lineno, n.value) for n in ast.walk(tree)
                 if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
                 and not isinstance(n.value, bool) and n.value not in STRUCTURAL
                 and id(n) not in exempt]
    assert not offenders, ("build/scene.py states a dimension as a literal: "
                           + "; ".join(f"line {ln}: {v}" for ln, v in offenders[:6]))


def test_the_scene_is_deterministic(scenes, one_element_plans):
    """The same placed record must give the same scene twice. `tests/test_determinism.py`
    holds every directory read in this toolchain to a stable order; this is the same claim for
    a derived record, and it is what lets a viewer cache on a digest."""
    scene_m = _load("scene")
    for name, (scene, section) in scenes.items():
        again, _s2, err = scene_m._build_from_plan(one_element_plans[name], engine="heuristic")
        assert not err
        assert json.dumps(again, sort_keys=True) == json.dumps(scene, sort_keys=True), name
