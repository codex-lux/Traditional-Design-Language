"""Pins WP-1.3's ontology work: the wall_thickness trade split (OQ 12, the
fourth and last of that family) and the derives_from_module cross-references
(OQ 13). See docs/open-questions.md and docs/reports/wp-1.3-kit-schema-operators.md.
"""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from conftest import load_style


def load_slots():
    return json.load(open(os.path.join(ROOT, "elements", "slots.json")))


def test_ontology_is_95_slots_at_0_5_0():
    d = load_slots()
    assert d["version"] == "0.5.0"
    ids = [s["id"] for g in d["groups"] for s in g["slots"]]
    assert len(ids) == 95
    assert len(set(ids)) == 95  # no duplicate ids introduced


def test_wall_thickness_split_by_trade():
    """The fourth split OQ 12 called for -- window_head, corner_treatment and
    window_surround were already split (0.3.0, predating this ruling);
    wall_thickness_expression had no split under any name until this."""
    d = load_slots()
    by_id = {s["id"]: s for g in d["groups"] for s in g["slots"]}
    for sid in ("wall_thickness_masonry", "wall_thickness_frame"):
        assert sid in by_id
        assert by_id[sid]["value_type"] == "parametric"
        assert by_id[sid]["units"] == "in"


def test_derives_from_module_family():
    """entablature is the root; the other five point at it. Each reference
    resolves to a real slot (checked structurally here; validate.py enforces
    it corpus-wide, see test_validate_rejects_bad_derives_from_module)."""
    d = load_slots()
    by_id = {s["id"]: s for g in d["groups"] for s in g["slots"]}
    family = ("cornice", "frieze", "modillion_dentil", "crown", "chair_rail")
    for sid in family:
        assert by_id[sid].get("derives_from_module") == "entablature", sid
    assert "derives_from_module" not in by_id["entablature"]


def test_new_wall_thickness_slots_exist_on_every_kit():
    """build.py (WP-1.3) added the two new slots to every kit file.

    UPDATED 23 Aug 2026 (WP-4.2, wave B): this test originally also asserted
    that both slots were still `open`/`empty` on every kit -- true at the
    moment the slots were introduced, when the assertion's real job was to
    catch build.py's migration accidentally pre-populating something. That
    job is done; it is not a corpus invariant. Kit-fill work is now
    intentionally specifying these slots with real, sourced content where a
    style or family's own text supports it -- e.g.
    colonial-iberian-americas.wall_thickness_masonry (24-40 in, sourced from
    mexican-colonial and mexican-hacienda's own measured ranges). Asserting
    every kit stays open/empty would make this test fail every time
    legitimate authoring happens, which is the opposite of what a test
    should do. What still matters and is still checked: the slot exists,
    with the right group, on every kit file -- i.e. build.py's migration
    reached everything and check_kits.py has something to validate no
    matter which kits have been authored yet."""
    import glob
    for path in glob.glob(os.path.join(ROOT, "kits", "*.kit.json")):
        kit = json.load(open(path))
        for sid in ("wall_thickness_masonry", "wall_thickness_frame"):
            assert sid in kit["slots"], (path, sid)
            assert kit["slots"][sid]["group"] == "envelope", (path, sid)


def test_validate_rejects_bad_derives_from_module():
    """A derives_from_module referencing a nonexistent slot must be a
    validate.py error -- referential integrity for the new cross-reference,
    the same discipline as every other cross-reference in the corpus."""
    path = os.path.join(ROOT, "elements", "slots.json")
    backup = open(path).read()
    try:
        d = json.loads(backup)
        for g in d["groups"]:
            for s in g["slots"]:
                if s["id"] == "cornice":
                    s["derives_from_module"] = "this-slot-does-not-exist"
        with open(path, "w") as f:
            json.dump(d, f)
        proc = subprocess.run(
            ["python3", os.path.join(ROOT, "build", "validate.py")],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert proc.returncode != 0
        assert "derives_from_module" in proc.stdout and "does not exist" in proc.stdout
    finally:
        with open(path, "w") as f:
            f.write(backup)


def test_service_zone_strategy_tidewater_fact_stated_once():
    """OQ 17: the parent used to carry strategy_tidewater as an
    applies_when.regions parameter AND the tidewater-georgian variant node
    restated the same 25-80ft fact via its own kit binding -- two mechanisms,
    one fact. Reconciled in WP-1.3 per the new guidance in
    docs/inheritance.md: since the variant node already exists (with its own
    identity), it's the sole statement; the parent's parameter is removed."""
    parent = json.load(open(os.path.join(ROOT, "kits", "georgian-colonial-american.kit.json")))
    parent_params = parent["slots"]["service_zone_strategy"]["parameters"]
    assert "strategy_tidewater" not in parent_params
    # the three regions with no variant node binding this slot are untouched
    for still_present in ("strategy_new_england", "strategy_mid_atlantic", "strategy_low_country"):
        assert still_present in parent_params

    variant = json.load(open(os.path.join(ROOT, "kits", "tidewater-georgian.kit.json")))
    variant_slot = variant["slots"]["service_zone_strategy"]
    assert variant_slot["binding"] == "extends"
    assert variant_slot["parameters"]["detached_typical_distance"]["range"] == [25, 80]


def test_validate_rejects_self_referential_derives_from_module():
    path = os.path.join(ROOT, "elements", "slots.json")
    backup = open(path).read()
    try:
        d = json.loads(backup)
        for g in d["groups"]:
            for s in g["slots"]:
                if s["id"] == "cornice":
                    s["derives_from_module"] = "cornice"
        with open(path, "w") as f:
            json.dump(d, f)
        proc = subprocess.run(
            ["python3", os.path.join(ROOT, "build", "validate.py")],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert proc.returncode != 0
        assert "cannot reference itself" in proc.stdout
    finally:
        with open(path, "w") as f:
            f.write(backup)
