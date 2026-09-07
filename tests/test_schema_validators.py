"""A compiled validator must report the SAME error the wrapper it replaced would have.

WP-11.12. `jsonschema.validate(instance, schema)` rebuilds the validator on every call --
looks up the class, re-runs `check_schema` over the schema, constructs a fresh object --
and five checkers were calling it in a loop. Measured on the asset manifest alone:
36.1 s for 1,850 records against 0.35 s compiled, which was 18% of build/check_all.py's
whole 197 s checker loop.

CLAUDE.md already carries this defect, for the workbench's plan gate, where WP-10.1
measured the same wrapper at 60.5 ms a call and 17.9% of `/api/plan/evaluate`. What that
entry did not say is that the same wrapper was being paid about 2,400 times a build by the
checkers -- so the lesson it ends with, MEASURE WHAT YOU ADD TO THE HOT PATH BEFORE YOU
ADD IT, has a companion: then go and look for the shape somewhere else.

THE RISK OF THE FIX IS THE MESSAGE AND NOT THE SPEED. `validate()` raises
`best_match(iter_errors(instance))` -- not the first error, the best one -- and every
checker here puts `e.message` into a failure a person reads and a test asserts on. A
faster validator that chose a DIFFERENT error would be a silent change to every failure
this corpus can produce, and nothing else in the tree would notice. So this holds the two
against each other on real records from every schema the checkers loop over, clean and
broken.
"""
import glob
import importlib.util
import json
import os

import pytest

jsonschema = pytest.importorskip("jsonschema")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sv():
    spec = importlib.util.spec_from_file_location(
        "schema_validators_under_test", os.path.join(ROOT, "build", "schema_validators.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# (schema, a real record of that kind) for every schema a checker validates in a loop.
CASES = {
    "asset.schema.json": lambda: json.load(
        open(f"{ROOT}/assets/manifest.json", encoding="utf-8"))["assets"][0],
    "style-node.schema.json": lambda: json.load(
        open(sorted(glob.glob(f"{ROOT}/styles/*.json"))[0], encoding="utf-8")),
    "kit.schema.json": lambda: json.load(
        open(sorted(glob.glob(f"{ROOT}/kits/*.kit.json"))[0], encoding="utf-8")),
    "proportion-pack.schema.json": lambda: json.load(
        open(sorted(glob.glob(f"{ROOT}/proportions/**/*.json", recursive=True))[0],
             encoding="utf-8")),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_a_valid_record_passes_both(name):
    sv = _sv()
    schema_path = os.path.join(ROOT, "schema", name)
    record = CASES[name]()
    jsonschema.validate(record, json.load(open(schema_path, encoding="utf-8")))
    sv.raise_first(sv.compiled(schema_path), record)          # must not raise either


@pytest.mark.parametrize("name", sorted(CASES))
def test_a_broken_record_raises_the_same_message_from_both(name):
    """Every required property, removed one at a time. Not one hand-picked break: the
    `best_match` heuristic chooses between competing errors, and a single fixture would
    exercise one branch of it and read as proof about all of them."""
    sv = _sv()
    schema_path = os.path.join(ROOT, "schema", name)
    schema = json.load(open(schema_path, encoding="utf-8"))
    validator = sv.compiled(schema_path)
    record = CASES[name]()
    required = [k for k in schema.get("required", []) if k in record]
    assert required, f"{name}: no required property to remove -- this test proves nothing"

    for key in required:
        broken = {k: v for k, v in record.items() if k != key}
        with pytest.raises(jsonschema.ValidationError) as naive:
            jsonschema.validate(broken, schema)
        with pytest.raises(jsonschema.ValidationError) as fast:
            sv.raise_first(validator, broken)
        assert fast.value.message == naive.value.message, (
            f"{name} without {key!r}: the compiled validator reports "
            f"{fast.value.message!r} where jsonschema.validate reports "
            f"{naive.value.message!r}. Every checker puts this string in front of a person.")
        assert list(fast.value.absolute_path) == list(naive.value.absolute_path)


def test_the_validator_is_built_once_per_schema():
    """The whole point. Two calls for one path must hand back one object -- if they do not,
    the loop is paying construction again and the 36 s comes straight back with every check
    still green."""
    sv = _sv()
    p = os.path.join(ROOT, "schema", "asset.schema.json")
    assert sv.compiled(p) is sv.compiled(p)
    assert sv.compiled(p) is sv.compiled(os.path.join(ROOT, "schema", "..", "schema",
                                                      "asset.schema.json"))


def test_an_invalid_schema_is_refused_at_compile_time():
    """`validate()` runs check_schema on every call; this runs it once, and must still run
    it. A compiled validator built from a nonsense schema would accept everything."""
    sv = _sv()
    with pytest.raises(jsonschema.SchemaError):
        sv.compiled(os.path.join(ROOT, "tests", "fixtures", "not_a_schema.json"))


def test_no_checker_still_rebuilds_a_validator_in_a_loop():
    """A source read, because the cost is invisible in every other way: the checker is
    correct, its output is identical, and it is only slower. The five call sites below were
    36.1 + 5.95 + 5.35 + 1.79 + 1.89 seconds of every build."""
    offenders = []
    for f in sorted(glob.glob(os.path.join(ROOT, "build", "check_*.py"))
                    + [os.path.join(ROOT, "build", "validate.py")]):
        src = open(f, encoding="utf-8").read()
        for i, line in enumerate(src.splitlines(), 1):
            if "jsonschema.validate(" in line and not line.lstrip().startswith("#"):
                offenders.append(f"{os.path.relpath(f, ROOT)}:{i}")
    assert not offenders, (
        f"{offenders} calls jsonschema.validate(), which rebuilds the validator every time. "
        f"Use build/schema_validators.compiled() once and raise_first() in the loop.")
