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


def test_a_gable_stands_on_the_face_it_names(scenes):
    """An E or W gable is a constant-x plane and an N or S gable a constant-y one. The first
    version took the DEPTH as the east gable's x coordinate, which put it inside the house —
    caught by reading the number against the wall extent rather than by reading the code."""
    for name, (scene, _s) in scenes.items():
        walls = [s for s in scene["solids"] if s["class"] == "wall" and s.get("face")]
        xs = [v for s in walls for v in (s["geometry"]["origin"][0],
                                         s["geometry"]["origin"][0] + s["geometry"]["size"][0])]
        ys = [v for s in walls for v in (s["geometry"]["origin"][1],
                                         s["geometry"]["origin"][1] + s["geometry"]["size"][1])]
        for g in [s for s in scene["solids"] if s["class"] == "gable"]:
            at, plane, f = g["geometry"]["at"], g["geometry"]["plane"], g["face"]
            if f in ("E", "W"):
                assert plane == "yz", f"{name}: gable {f} is not a constant-x plane"
                assert abs(at - (max(xs) if f == "E" else min(xs))) < 0.05, \
                    f"{name}: gable {f} stands at x={at}, not on its own face"
            else:
                assert plane == "xz", f"{name}: gable {f} is not a constant-y plane"
                assert abs(at - (max(ys) if f == "N" else min(ys))) < 0.05, \
                    f"{name}: gable {f} stands at y={at}, not on its own face"


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


def test_the_walls_say_they_have_no_openings_yet(scenes):
    """WP-12.2's holes are not here, and a blank wall must not read as a wall with no windows.
    When 12.2 lands this test is the thing that says so: it will fail, and the entry it is
    asserting on should be REPLACED by holes rather than deleted."""
    for name, (scene, _s) in scenes.items():
        assert any(n.get("class") == "opening" for n in scene["not_modelled"]), name


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
