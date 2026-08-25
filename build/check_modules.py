#!/usr/bin/env python3
"""Validate the module-system proportion packs in proportions/modules/.

Checks, in order:
  1. JSON parses
  2. conforms to schema/proportion-pack.schema.json (jsonschema, draft 2020-12)
  3. id matches filename
  4. ids are unique across the directory
  5. kind == "module-system" and authority.strength is present
  6. module.default_size_in is a real number (the engine must run untold)
  7. derived_rules[].target_slot resolves against elements/slots.json
  8. applies_to[] entries resolve against styles/*.json
  9. massing:<id> cross-references in note text resolve against massings/catalog.json
 10. assemblies: member height_parts sum to height_modules * module.parts (where sums_check)
 11. derived_rules[].range is [lo, hi] with lo <= hi
 12. derived_rules count is in the 10-18 band the pack spec asks for
 13. conflicts count is in the 3-6 band
 14. invariants[].expression evaluates true against the pack
 15. --eval: every derived_rules[].expression evaluates to a finite number over a
     sweep of sample bindings, and lands inside its declared range

Run:  python3 build/check_modules.py [--dir proportions/modules] [--eval]
Exit: 0 clean, 1 on any error.
"""
import argparse
import ast
import glob
import json
import math
import os
import re
import sys

try:
    import jsonschema
except ImportError:
    import sys as _sys
    print("SKIPPED — jsonschema is not installed, so nothing here was checked.")
    print("    pip install jsonschema")
    # Exit 3, the convention build/check_all.py reads as "could not evaluate". Exiting 1
    # would report a missing dependency as a failed data check, which is the collapse
    # this corpus forbids everywhere else.
    _sys.exit(3)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RULE_BAND = (10, 18)
CONFLICT_BAND = (3, 6)
SUM_TOL = 1e-6

MASSING_REF = re.compile(r"massing:([a-z0-9]+(?:-[a-z0-9]+)*)")


def load_slot_ids(path):
    ids = set()
    for group in json.load(open(path))["groups"]:
        for slot in group["slots"]:
            ids.add(slot["id"])
    return ids


def load_style_ids(styles_dir):
    return {os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(styles_dir, "*.json")))}


def load_massing_ids(path):
    return {m["id"] for m in json.load(open(path))}


class Ref:
    """Attribute/item access over the pack dict, so invariant expressions can be written
    as 'module.default_size_in' or 'assemblies.water_table.height_modules'."""

    def __init__(self, data):
        self._d = data

    def __getattr__(self, name):
        try:
            v = self._d[name]
        except (KeyError, TypeError):
            raise AttributeError(name)
        return Ref(v) if isinstance(v, dict) else v

    def __repr__(self):
        return f"Ref({self._d!r})"


ALLOWED_NODES = (
    ast.Expression, ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.Compare, ast.Name,
    ast.Load, ast.Constant, ast.Attribute, ast.And, ast.Or, ast.Not, ast.USub,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
)


def eval_invariant(expr, pack):
    """Evaluate an invariant expression against the pack. Equality comparisons are
    relaxed to the invariant's tolerance by rewriting them as abs(a - b) <= tol,
    which we do by evaluating both sides separately when the top node is a simple ==."""
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise ValueError(f"disallowed syntax {type(node).__name__!r} in invariant")
    env = {k: (Ref(v) if isinstance(v, dict) else v) for k, v in pack.items()}
    return tree, env


def check_invariant(inv, pack):
    expr = inv["expression"]
    tol = inv.get("tolerance", 0.02)
    tree, env = eval_invariant(expr, pack)
    node = tree.body
    # relax a bare `a == b` to a tolerance comparison
    if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
        lhs = eval(compile(ast.Expression(node.left), "<inv>", "eval"), {"__builtins__": {}}, env)
        rhs = eval(compile(ast.Expression(node.comparators[0]), "<inv>", "eval"), {"__builtins__": {}}, env)
        return abs(float(lhs) - float(rhs)) <= max(tol, 1e-9), f"{lhs} vs {rhs}"
    val = eval(compile(tree, "<inv>", "eval"), {"__builtins__": {}}, env)
    return bool(val), repr(val)


EXPR_FUNCS = {"ceil": math.ceil, "floor": math.floor, "round": round,
              "min": min, "max": max, "abs": abs, "sqrt": math.sqrt}

# A sweep of plausible bindings. Every derived_rules expression must survive all of them.
SAMPLE_BINDINGS = [
    {"opening_height": 80.0, "opening_width": 28.0, "ceiling_height": 96.0, "storey_height": 108.0,
     "wall_thickness": 9.0, "span": 192.0},
    {"opening_width": 32.0, "ceiling_height": 108.0, "storey_height": 120.0,
     "wall_thickness": 13.5, "span": 216.0},
    {"opening_width": 40.0, "ceiling_height": 132.0, "storey_height": 144.0,
     "wall_thickness": 18.0, "span": 240.0},
]


def eval_rule(expr, module_in, parts, binding):
    env = dict(EXPR_FUNCS)
    env.update(binding)
    env["module"] = module_in
    env["part"] = module_in / parts
    return eval(compile(ast.parse(expr, mode="eval"), "<rule>", "eval"),
                {"__builtins__": {}}, env)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", action="store_true",
                    help="also evaluate every derived rule over a sweep of sample bindings")
    ap.add_argument("--dir", default=os.path.join(ROOT, "proportions", "modules"))
    ap.add_argument("--schema", default=os.path.join(ROOT, "schema", "proportion-pack.schema.json"))
    args = ap.parse_args()

    schema = json.load(open(args.schema))
    validator = jsonschema.Draft202012Validator(schema)
    slots = load_slot_ids(os.path.join(ROOT, "elements", "slots.json"))
    styles = load_style_ids(os.path.join(ROOT, "styles"))
    massings = load_massing_ids(os.path.join(ROOT, "massings", "catalog.json"))

    errs, warns, seen = [], [], {}
    files = sorted(glob.glob(os.path.join(args.dir, "*.json")))
    if not files:
        print(f"no packs found in {args.dir}", file=sys.stderr)
        return 1

    for path in files:
        base = os.path.basename(path)[:-5]
        E = lambda m: errs.append(f"{base}: {m}")
        W = lambda m: warns.append(f"{base}: {m}")

        try:
            pack = json.load(open(path))
        except Exception as exc:
            E(f"UNPARSEABLE JSON: {exc}")
            continue

        schema_errors = sorted(validator.iter_errors(pack), key=lambda e: list(e.absolute_path))
        if schema_errors:
            for e in schema_errors:
                loc = "/".join(str(p) for p in e.absolute_path) or "<root>"
                E(f"SCHEMA {loc}: {e.message}")
            continue

        if pack["id"] != base:
            E(f"id '{pack['id']}' does not match filename")
        if pack["id"] in seen:
            E(f"duplicate id (also in {seen[pack['id']]})")
        seen[pack["id"]] = base

        if pack["kind"] != "module-system":
            E(f"kind is '{pack['kind']}', expected 'module-system'")

        mod = pack["module"]
        if not isinstance(mod.get("default_size_in"), (int, float)):
            E("module.default_size_in must be a real number so the engine runs untold")
        if mod["parts"] <= 0:
            E("module.parts must be positive")

        rules = pack.get("derived_rules", [])
        if not (RULE_BAND[0] <= len(rules) <= RULE_BAND[1]):
            W(f"{len(rules)} derived_rules, expected {RULE_BAND[0]}-{RULE_BAND[1]}")
        for i, r in enumerate(rules):
            if r["target_slot"] not in slots:
                E(f"derived_rules[{i}]: unknown target_slot '{r['target_slot']}'")
            rng = r.get("range")
            if rng is not None and rng[0] > rng[1]:
                E(f"derived_rules[{i}]: range {rng} is inverted")
            if not r.get("expression", "").strip():
                E(f"derived_rules[{i}]: empty expression")
                continue
            if args.eval:
                for b in SAMPLE_BINDINGS:
                    try:
                        v = eval_rule(r["expression"], mod["default_size_in"], mod["parts"], b)
                    except Exception as exc:
                        E(f"derived_rules[{i}] ({r['target_slot']}): "
                          f"'{r['expression']}' failed on {b}: {exc}")
                        break
                    if not isinstance(v, (int, float)) or not math.isfinite(v):
                        E(f"derived_rules[{i}] ({r['target_slot']}): "
                          f"non-finite result {v!r} on {b}")
                        break
                    if rng and not (rng[0] <= v <= rng[1]):
                        W(f"derived_rules[{i}] ({r['target_slot']}): "
                          f"{v:g} outside declared range {rng} at opening_width="
                          f"{b['opening_width', 'opening_height']:g}, storey_height={b['storey_height']:g}")

        confs = pack.get("conflicts", [])
        if not (CONFLICT_BAND[0] <= len(confs) <= CONFLICT_BAND[1]):
            W(f"{len(confs)} conflicts, expected {CONFLICT_BAND[0]}-{CONFLICT_BAND[1]}")

        for sid in pack.get("applies_to", []):
            if sid not in styles:
                E(f"applies_to: unknown style node '{sid}'")

        blob = json.dumps(pack)
        for mid in set(MASSING_REF.findall(blob)):
            if mid not in massings:
                E(f"unknown massing cross-reference 'massing:{mid}'")

        for name, asm in (pack.get("assemblies") or {}).items():
            if asm.get("sums_check", True):
                total = sum(m["height_parts"] for m in asm["members"])
                want = asm["height_modules"] * mod["parts"]
                if abs(total - want) > SUM_TOL:
                    E(f"assemblies.{name}: members sum to {total} parts, "
                      f"height_modules*parts = {want}")

        for i, inv in enumerate(pack.get("invariants", [])):
            try:
                ok, detail = check_invariant(inv, pack)
            except Exception as exc:
                E(f"invariants[{i}]: could not evaluate '{inv['expression']}': {exc}")
                continue
            if not ok:
                E(f"invariants[{i}] FAILED: {inv['expression']} -> {detail}")

    for w in warns:
        print(f"WARN  {w}")
    for e in errs:
        print(f"ERROR {e}")
    print(f"\n{len(files)} pack(s) checked, {len(errs)} error(s), {len(warns)} warning(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
