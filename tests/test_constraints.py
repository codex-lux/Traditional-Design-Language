"""Pins WP-1.1's constraint rule language: the schema, the vocabulary checker,
and the worked-example migration (english-classical + american-colonial,
140 constraints across 28 nodes). See docs/constraints.md and
docs/reports/wp-1.1-constraint-rule-language.md.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from conftest import load_style


def test_migrated_constraint_conforms_to_schema():
    """A real migrated constraint (georgian-colonial-american.c01, the odd-bay-
    count rule) validates against schema/constraint.schema.json.

    jsonschema lives in the system python3, not in pytest's own tool venv --
    see the note in test_proportion_engine.py -- so this shells out rather
    than importing jsonschema directly."""
    node = load_style("georgian-colonial-american")
    c = next(c for c in node["constraints"] if c.get("id") == "georgian-colonial-american.c01")
    assert c["test"]["direction"] == "one-of"
    assert c["test"]["set"] == ["3", "5", "7"]
    proc = subprocess.run(
        ["python3", "-c",
         "import json, jsonschema; "
         "schema = json.load(open('schema/constraint.schema.json')); "
         "node = json.load(open('styles/georgian-colonial-american.json')); "
         "c = next(c for c in node['constraints'] if c.get('id') == 'georgian-colonial-american.c01'); "
         "jsonschema.validate(c, schema); "
         "print('OK')"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert proc.returncode == 0 and "OK" in proc.stdout, proc.stdout + proc.stderr


def test_worked_example_migration_counts(check_constraints_module, capsys):
    """The english-classical + american-colonial worked example migrated
    exactly 140 constraints (28 nodes x 5 each): 106 with a test, 34 honestly
    scope: judgment. A drift here means a node's constraint count changed, or
    the migration script/data fell out of sync with it -- either is worth
    noticing, not silently passing."""
    sys.argv = ["check_constraints.py"]
    check_constraints_module.main()
    out = capsys.readouterr().out
    assert "140 migrated constraint(s) across 28 node(s)" in out
    assert "tested: 106   judgment: 34" in out


def test_expression_checker_flags_unknown_variable(constraint_vocabulary_module):
    cv = constraint_vocabulary_module
    known, unknown = cv.check_expression("bay_count")
    assert known == {"bay_count"} and not unknown
    known, unknown = cv.check_expression("bay_count and this_variable_does_not_exist")
    assert unknown == {"this_variable_does_not_exist"}


def test_expression_checker_ignores_keywords_and_functions(constraint_vocabulary_module):
    cv = constraint_vocabulary_module
    # the charleston-georgian piazza-bearing constraint's actual expression
    known, unknown = cv.check_expression("abs(piazza_bearing_deg - 225)")
    assert "piazza_bearing_deg" in known
    assert not unknown  # 'abs' must not be reported as an unknown variable


def test_checker_rejects_duplicate_id():
    """A duplicate constraint id across two nodes must be an error, not a
    silently-accepted collision -- ids are the stable address the composer
    and geometry solver key evaluation results on."""
    path = os.path.join(ROOT, "styles", "regency.json")
    backup = open(path).read()
    try:
        node = json.loads(backup)
        # collide regency's first migrated id with georgian-colonial-american's
        node["constraints"][3]["id"] = "georgian-colonial-american.c01"
        with open(path, "w") as f:
            json.dump(node, f)
        proc = subprocess.run(
            ["python3", os.path.join(ROOT, "build", "check_constraints.py")],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert proc.returncode != 0
        assert "duplicate constraint id" in proc.stdout
    finally:
        with open(path, "w") as f:
            f.write(backup)


def test_checker_rejects_hard_constraint_with_no_test_and_no_judgment_scope():
    """A hard, non-judgment constraint with its test stripped must fail --
    'unjudged is not passed' extended from slots to constraints (OQ 24)."""
    path = os.path.join(ROOT, "styles", "georgian-colonial-american.json")
    backup = open(path).read()
    try:
        node = json.loads(backup)
        c = next(c for c in node["constraints"] if c.get("id") == "georgian-colonial-american.c01")
        assert c["severity"] == "hard" and c["scope"] != "judgment"
        del c["test"]
        with open(path, "w") as f:
            json.dump(node, f)
        proc = subprocess.run(
            ["python3", os.path.join(ROOT, "build", "check_constraints.py")],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert proc.returncode != 0
        assert "no test" in proc.stdout
    finally:
        with open(path, "w") as f:
            f.write(backup)
