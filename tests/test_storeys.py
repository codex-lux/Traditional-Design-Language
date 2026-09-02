"""One storey derivation, read by everything that needs it.

WP-9.6. `structure.py` inverted `storey-graduation.json`'s own `ceiling_height_rule` to get
floor-to-floor from the ceiling height a plan states. `openings.py::stair_pass` instead wrote
`storey_in = (ch + 1.0) * 12.0` beside `ch = ground.get("floor_to_ceiling_ft") or 9.0` -- a
flat twelve inches of floor assembly and an invented ceiling, two constants standing where the
corpus has a derivation. On `plans/tidewater-georgian-careful.json` that was 144.0 in against
147.3, so the stair pass said 20 risers and the section that DRAWS the same stair said 21.

The derivation now lives in `build/storeys.py`, a LEAF: `structure.py` loads `geometry.py`,
which calls `openings.stair_pass`, so openings importing structure would close a cycle.
"""
import json, glob, math, os, importlib.util, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ST = _mod("build/storeys.py", "storeys_t")
GEOM = _mod("build/geometry.py", "geometry_st")
STRUCT = _mod("build/structure.py", "structure_st")


def _plans():
    # `sorted(` on the same line as the read (tests/test_determinism.py checks per line)
    return sorted(glob.glob(str(ROOT / "plans" / "*.json")))


def test_the_transcribed_fraction_still_matches_the_pack():
    """`STOREY_CEILING_FRACTION` is a TRANSCRIPTION of the pack's expression, not a read of
    it. That is defensible only while something holds the two together."""
    pack = json.loads((ROOT / "proportions" / "modules" / "storey-graduation.json").read_text())
    rule = next(r for r in pack["derived_rules"] if r.get("target_slot") == "ceiling_height_rule")
    assert rule["expression"] == "module - part * 1.25", (
        "storey-graduation.json's ceiling_height_rule changed to %r; build/storeys.py "
        "transcribes it as `1 - 1.25/12` and must be updated in the same commit"
        % rule["expression"])
    # part = module / 12, from the pack's own invariant ("the part is ten inches" on a ten-foot
    # module). So ceiling = module * (1 - 1.25/12).
    inv = " ".join(i["expression"] for i in pack["invariants"])
    assert "module.default_size_in / module.parts == 10.0" in inv, (
        "the pack's parts invariant moved; the /12 in build/storeys.py rests on it")
    assert abs(ST.STOREY_CEILING_FRACTION - (1.0 - 1.25 / 12.0)) < 1e-12


def test_a_level_with_no_stated_ceiling_is_unjudged_and_says_so():
    """Never an invented 9.0 ft. The number that used to stand there is the OQ 52 class."""
    out = ST.storey_heights({"levels": [{"id": "ground", "index": 0, "rooms": []}]})
    assert out[0]["storey_height_ft"] is None
    assert out[0]["ceiling_ft"] is None
    assert "unjudged" in out[0]["note"].lower(), (
        "a level that states no ceiling must SAY it is unjudged, not return a bare None a "
        "caller can read as zero")
    assert ST.ground_storey_in({"levels": [{"id": "ground", "index": 0, "rooms": []}]}) is None


def test_the_floor_assembly_is_not_a_constant():
    """The invented number was a flat 1.0 ft. The derived one moves with the ceiling, which
    is the whole reason the two spellings disagreed."""
    out = ST.storey_heights({"levels": [
        {"id": "a", "index": 0, "floor_to_ceiling_ft": 11, "rooms": []},
        {"id": "b", "index": 1, "floor_to_ceiling_ft": 8.5, "rooms": []}]})
    depths = [o["floor_structure_depth_in"] for o in out]
    assert depths[0] > depths[1], "the deduction must scale with the storey"
    assert abs(depths[0] - 15.35) < 0.01 and abs(depths[1] - 11.86) < 0.01, depths
    assert not any(abs(d - 12.0) < 0.01 for d in depths), (
        "a flat 12.00 in is the constant this package removed")


def test_the_two_stair_spellings_agree_on_every_shipped_plan():
    """The guard that matters. `openings.stair_pass` and `structure.stair_geometry` describe
    ONE stair, and until WP-9.6 they read different storeys."""
    checked, bad = 0, []
    for pf in _plans():
        plan = json.loads(pathlib.Path(pf).read_text())
        if "levels" not in plan:
            continue
        solved = GEOM.solve(json.loads(json.dumps(plan)), engine="heuristic")
        stair = solved.get("stair")
        section = STRUCT.build_section(json.loads(json.dumps(plan)))
        sg = section.get("stair") or {}
        if not stair or not sg.get("applicable"):
            continue                      # no placed stair hall; both decline, correctly
        checked += 1
        if stair.get("risers") != sg.get("risers"):
            bad.append(f"{os.path.basename(pf)}: openings {stair.get('risers')} risers, "
                       f"structure {sg.get('risers')}")
    assert checked, "no plan produced a stair from both readers — this test would be vacuous"
    assert not bad, ("the two spellings of one stair disagree:\n  " + "\n  ".join(bad))


def test_the_riser_divisor_is_READ_from_the_pack_and_not_transcribed():
    """It was a bare 7.25 in `openings.py` AND in `structure.py`, each commented with the name
    of the pack it was copied from — so moving the pack would have moved neither. Lucas ruled
    7.5 on 2 Sep 2026 and the pack is now the only place that number lives."""
    pack = json.loads((ROOT / "proportions" / "modules" / "storey-graduation.json").read_text())
    rule = next(r for r in pack["derived_rules"] if r.get("target_slot") == "stair_type")
    assert rule["expression"] == "ceil(module / %g)" % ST.riser_divisor_in(), (
        "build/storeys.py read %r out of an expression of %r — they must agree by "
        "construction" % (ST.riser_divisor_in(), rule["expression"]))
    # and no OTHER file may carry the number
    stray = []
    for py in sorted((ROOT / "build").glob("*.py")):
        if py.name == "storeys.py":
            continue
        for ln, line in enumerate(py.read_text().splitlines(), 1):
            if "/ 7.25)" in line or "/ 7.5)" in line:
                if line.lstrip().startswith("#"):
                    continue
                stray.append(f"{py.name}:{ln}: {line.strip()}")
    assert not stray, ("the riser divisor is transcribed outside build/storeys.py, which is "
                       "how the last one went stale:\n  " + "\n  ".join(stray))


def test_the_baked_kit_copy_agrees_with_its_own_expression():
    """`kits/georgian-colonial-american.kit.json` carries a BAKED copy of this pack rule --
    `oq/a-baked-pack-value-is-a-second-delivery-path` -- and it carries the expression AND the
    value the expression produced. **Moving the pack moved the expression and left the value**,
    so the same object said `ceil(module / 7.5)` and `17` on a 120 in module, where the
    expression gives 16. `check_kits.py` holds the `computed_at` CONTEXT keys consistent across
    a slot family and explicitly `continue`s on `"value"`, so nothing compared the two.

    Measured across all 159 kits: **143 baked derived parameters carry both an `expr` and a
    `computed_at.value`; exactly ONE is of a shape this reader can evaluate**, and that one is
    the one that broke. The other 142 are UNJUDGED here, not passed -- a general checker is
    `oq/a-baked-pack-value-is-a-second-delivery-path`'s to rule on, not this test's to invent.
    """
    kit = json.loads((ROOT / "kits" / "georgian-colonial-american.kit.json").read_text())
    p = kit["slots"]["stair_type"]["parameters"]["risers_per_storey"]
    pack = json.loads((ROOT / "proportions" / "modules" / "storey-graduation.json").read_text())
    rule = next(r for r in pack["derived_rules"] if r.get("target_slot") == "stair_type")
    assert p["expr"] == rule["expression"], (
        "the baked copy's expression (%r) has drifted from the pack's (%r)"
        % (p["expr"], rule["expression"]))
    module = p["computed_at"]["storey_height_in"]
    want = math.ceil(module / ST.riser_divisor_in())
    assert p["computed_at"]["value"] == want, (
        "the baked value is %r but %r on a %s in module gives %d -- the expression moved and "
        "the value did not, which is exactly what nothing checks"
        % (p["computed_at"]["value"], p["expr"], module, want))


def test_an_unrecognised_stair_expression_is_refused_not_defaulted(tmp_path):
    """A divisor that silently falls back to a stale number is the defect this replaces."""
    import shutil
    shutil.copytree(ROOT / "proportions", tmp_path / "proportions")
    pk = tmp_path / "proportions" / "modules" / "storey-graduation.json"
    d = json.loads(pk.read_text())
    for r in d["derived_rules"]:
        if r.get("target_slot") == "stair_type":
            r["expression"] = "module * 0.13"        # a shape the reader must not guess at
    pk.write_text(json.dumps(d))
    fresh = _mod("build/storeys.py", "storeys_refusal")
    try:
        fresh.riser_divisor_in(root=str(tmp_path))
    except ValueError as e:
        assert "does not recognise" in str(e), str(e)
    else:
        raise AssertionError("an unrecognised stair_type expression was accepted; the reader "
                             "must refuse rather than fall back to a number")


def test_structure_still_exposes_the_derivation_under_its_old_name():
    """`storey_heights` moved to a leaf module and is re-exported. Three tests in
    tests/test_structure.py call it through `structure`, and so may anything else."""
    plan = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())
    assert STRUCT.storey_heights(plan) == ST.storey_heights(plan)
    assert STRUCT.STOREY_CEILING_FRACTION == ST.STOREY_CEILING_FRACTION
