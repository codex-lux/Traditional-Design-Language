"""Pins WP-1.1's constraint rule language: the schema, the vocabulary checker,
and the migration itself. The worked example (english-classical + american-
colonial, 140 constraints across 28 nodes) proved the shape; the remaining 25
families were then migrated in one batched pass (23 Aug 2026, 8 parallel
batches by family), bringing the corpus to 660 migrated constraints across
132 nodes -- every style/variant node that carries a `constraints` array at
all. See docs/constraints.md and docs/reports/wp-1.1-constraint-rule-language.md
for the worked example, and docs/reports/wp-1.1-remaining-families-migration.md
for the full-corpus pass.
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


def test_full_corpus_migration_counts(check_constraints_module, capsys):
    """UPDATED 23 Aug 2026 when the remaining 25 families were migrated in one
    batched pass: the corpus-wide total is now 660 migrated constraints across
    132 nodes (every style/variant that carries a `constraints` array at all),
    365 with a test and 295 honestly scope: judgment (55%/45%) -- a markedly
    higher judgment fraction than the 140-constraint worked example's 24%,
    because the worked example's two families (English Classical, American
    Colonial) happen to be dimension-heavy relative to the corpus as a whole;
    several of the newly-migrated families (Tudor-Jacobean, Renaissance-
    classical, the Beaux-Arts/French Baroque cluster) are dominated by
    compositional/hierarchical rules with no number in them at all. See
    docs/reports/wp-1.1-remaining-families-migration.md for the family-by-
    family breakdown and the vocabulary gaps the batches found. A drift here
    means a node's constraint count changed, or the corpus fell out of sync
    with what check_constraints.py reports -- either is worth noticing, not
    silently passing."""
    sys.argv = ["check_constraints.py"]
    check_constraints_module.main()
    out = capsys.readouterr().out
    assert "660 migrated constraint(s) across 132 node(s)" in out
    assert "tested: 365   judgment: 295" in out


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
