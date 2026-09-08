#!/usr/bin/env python3
"""Validate the migrated style constraints (schema/constraint.schema.json)
across styles/*.json.

Checks beyond plain JSON Schema conformance:

  * every constraint id is unique across the whole corpus and matches
    <style-id>.c##
  * a `test` is present only when scope != 'judgment'; a judgment-scope
    constraint must NOT carry a test (that would be pretending a threshold
    exists when the sources don't determine one)
  * every hard constraint is either tested or explicitly scope: judgment --
    nothing hard is silently unaddressed
  * test.expression references only names in build/constraint_vocabulary.py
  * direction 'between' has both threshold and upper; 'one-of' has `set` and
    no threshold; the others have threshold and no `set`

    python3 build/check_constraints.py                # whole corpus
    python3 build/check_constraints.py tidewater-georgian
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import constraint_vocabulary as cv
import schema_validators

try:
    import jsonschema
except ImportError:
    jsonschema = None


def main():
    ap = argparse.ArgumentParser(description="Validate style constraints")
    ap.add_argument("style", nargs="?", help="check one style only")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    schema_path = os.path.join(ROOT, "schema", "constraint.schema.json")
    schema = json.load(open(schema_path))
    # Compiled once for every constraint on every node, not rebuilt per constraint.
    constraint_validator = schema_validators.compiled(schema_path) if jsonschema else None

    files = ([os.path.join(ROOT, "styles", f"{a.style}.json")] if a.style
              else sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))))

    errs, warns = [], []
    all_ids = {}
    stats = {"total": 0, "tested": 0, "judgment": 0, "hard_untested_nonjudgment": 0,
              "by_direction": {}, "by_scope": {}}
    nodes_with_any_constraint = 0
    nodes_with_ids = 0

    for f in files:
        base = os.path.basename(f)[:-len(".json")]
        try:
            node = json.load(open(f))
        except Exception as e:
            errs.append(f"{base}: UNPARSEABLE JSON: {e}")
            continue

        constraints = node.get("constraints", [])
        if not constraints:
            continue
        nodes_with_any_constraint += 1
        has_migrated = any("id" in c for c in constraints)
        if has_migrated:
            nodes_with_ids += 1

        for i, c in enumerate(constraints):
            if "id" not in c:
                # not yet migrated -- fine, this checker only judges migrated constraints
                continue
            stats["total"] += 1
            cid = c["id"]
            if cid in all_ids:
                errs.append(f"{base}: duplicate constraint id '{cid}' (also on {all_ids[cid]})")
            all_ids[cid] = base
            if not cid.startswith(base + ".c"):
                errs.append(f"{base}.constraints[{i}]: id '{cid}' does not match '{base}.c##' pattern")

            if jsonschema:
                try:
                    schema_validators.raise_first(constraint_validator, c)
                except jsonschema.ValidationError as e:
                    errs.append(f"{base}.{cid}: schema violation: {e.message}")
                    continue

            scope = c.get("scope")
            stats["by_scope"][scope] = stats["by_scope"].get(scope, 0) + 1
            test = c.get("test")

            if scope == "judgment":
                stats["judgment"] += 1
                if test:
                    errs.append(f"{base}.{cid}: scope is 'judgment' but a test is present -- "
                                f"either the sources determine this (drop judgment) or they don't (drop the test)")
                continue

            if test:
                stats["tested"] += 1
                direction = test.get("direction")
                stats["by_direction"][direction] = stats["by_direction"].get(direction, 0) + 1
                if direction == "between":
                    if "upper" not in test or "threshold" not in test:
                        errs.append(f"{base}.{cid}: direction 'between' needs both threshold and upper")
                elif direction == "one-of":
                    if "set" not in test:
                        errs.append(f"{base}.{cid}: direction 'one-of' needs a 'set'")
                    if "threshold" in test:
                        errs.append(f"{base}.{cid}: direction 'one-of' should not carry a numeric threshold")
                else:
                    if "threshold" not in test:
                        errs.append(f"{base}.{cid}: direction '{direction}' needs a threshold")

                known, unknown = cv.check_expression(test["expression"])
                if unknown:
                    warns.append(f"{base}.{cid}: expression references unknown variable(s) {sorted(unknown)} "
                                 f"-- not in build/constraint_vocabulary.py")
            else:
                if c.get("severity") == "hard":
                    stats["hard_untested_nonjudgment"] += 1
                    errs.append(f"{base}.{cid}: severity 'hard', scope '{scope}' (not judgment), "
                                f"but no test -- either add one, or set scope: judgment with a reason")

    print(f"\n{stats['total']} migrated constraint(s) across {nodes_with_ids} node(s) "
          f"({nodes_with_any_constraint} node(s) carry constraints at all)")
    print(f"  tested: {stats['tested']}   judgment: {stats['judgment']}")
    print(f"  by scope: {stats['by_scope']}")
    print(f"  by direction: {stats['by_direction']}")

    if warns:
        print(f"\n{len(warns)} WARNINGS")
        for w in warns:
            print(f"  ! {w}")

    if errs:
        print(f"\n{len(errs)} ERRORS")
        for e in errs:
            print(f"  x {e}")
        sys.exit(1)

    print("\nOK — migrated constraints conform to constraint.schema.json, "
          "every hard non-judgment constraint is tested, no untested hard constraint hides.")


if __name__ == "__main__":
    main()
