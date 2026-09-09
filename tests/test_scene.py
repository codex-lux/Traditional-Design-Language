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
def scenes():
    """Both shipped plans on the HEURISTIC, deliberately.

    `auto` reaches a CP proof on one machine and spends its budget on another, so a suite
    built on it would assert different geometry on different runners — which is what WP-12.0
    measured happening to the elevation between two trees. The heuristic is reproducible, and
    the engine-dependent figures belong in a report, not a pin.
    """
    scene_m = _load("scene")
    out = {}
    for name in PLANS:
        s, section, err = scene_m._build_from_plan(
            os.path.join(ROOT, "plans", f"{name}.json"), engine="heuristic")
        assert not err, f"{name}: {err}"
        out[name] = (s, section)
    return out


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
    """
    for name, (scene, _s) in scenes.items():
        planes = [s for s in scene["solids"] if s["class"] == "roof-plane"]
        walls = [s for s in scene["solids"] if s["class"] == "wall" and s.get("face")]
        if not planes:
            continue
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
    """
    for name, (scene, _s) in scenes.items():
        walls = [s for s in scene["solids"] if s["class"] == "wall" and s.get("face")]
        for g in [s for s in scene["solids"] if s["class"] == "gable"]:
            f, geo = g["face"], g["geometry"]
            axis = 0 if f in ("E", "W") else 1
            assert geo["plane"] == ("yz" if axis == 0 else "xz"), \
                f"{name}: gable {f} is not a constant-{'x' if axis == 0 else 'y'} plane"
            mine = [w for w in walls if w["face"] == f]
            assert mine, f"{name}: no exterior wall on face {f} for its gable to stand on"
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


def test_the_openings_are_drawn_on_every_face(scenes):
    """WP-12.2 replaced this test's predecessor rather than deleting it.

    Until 12.2 an exterior wall was a plain box carrying a `not_modelled` entry that said so,
    because a blank wall must not read as a wall with no windows, and
    `test_the_walls_say_they_have_no_openings_yet` was written to FAIL when the openings landed.
    It did. What replaces it asserts the other side of the same rule: every face carries
    openings now, and NOTHING still says they are missing.
    """
    for name, (scene, _s) in scenes.items():
        assert not any(n.get("class") == "opening" and "every face" in n.get("what", "")
                       for n in scene["not_modelled"]), (
            f"{name} draws openings and still declares them not modelled")
        by_face = {}
        for solid in scene["solids"]:
            if solid["class"] == "opening-frame":
                by_face[solid["face"]] = by_face.get(solid["face"], 0) + 1
        assert set(by_face) == {"S", "N", "E", "W"}, f"{name}: openings on {sorted(by_face)}"
        assert all(n > 0 for n in by_face.values()), f"{name}: {by_face}"


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
    allowed_names = {"CUT_HEIGHT_FT", "DEFAULT_CANDIDATES"}
    assigned = {t.id for node in ast.walk(tree) if isinstance(node, ast.Assign)
                for t in node.targets if isinstance(t, ast.Name)}
    assert allowed_names <= assigned, "the named editorial constant is gone from the file"

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


def test_the_scene_is_deterministic(scenes):
    """The same placed record must give the same scene twice. `tests/test_determinism.py`
    holds every directory read in this toolchain to a stable order; this is the same claim for
    a derived record, and it is what lets a viewer cache on a digest."""
    scene_m = _load("scene")
    for name, (scene, section) in scenes.items():
        again, _s2, err = scene_m._build_from_plan(
            os.path.join(ROOT, "plans", f"{name}.json"), engine="heuristic")
        assert not err
        assert json.dumps(again, sort_keys=True) == json.dumps(scene, sort_keys=True), name
