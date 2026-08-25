#!/usr/bin/env python3
"""Validate the system proportion packs in proportions/systems/.

These are the packs that sit between the orders and the building: the ones that
proportion a facade, a room, a trim run and an opening. They use the same schema
as the order and module packs but a different set of kinds, and they bind a wider
set of variables (room_length, room_width, span, wall_thickness) than the order
packs do.

Checks, in order:
  1. JSON parses
  2. conforms to schema/proportion-pack.schema.json (jsonschema, draft 2020-12)
  3. id matches filename, ids unique across the directory
  4. kind is one of the system kinds and matches the filename family
  5. authority.strength is present and is one of the schema's values
  6. module.default_size_in is a real number and module.parts is positive
  7. derived_rules[].target_slot resolves against elements/slots.json
  8. derived_rules[].expression parses and uses only bound variables and allowed funcs
  9. applies_to[] entries resolve against styles/*.json
 10. massing:<id> cross-references anywhere in the pack resolve against massings/catalog.json
 11. ASSEMBLY MEMBER SUMS: member height_parts sum to height_modules * module.parts
     (unless sums_check is false, which must be explained in a member note)
 12. assembly member ids are unique within an assembly
 13. derived_rules[].range is [lo, hi] with lo <= hi
 14. derived_rules count is in the 12-20 band the system packs are specified at
 15. conflicts count is in the 3-6 band, and every `with` is a schema enum value
 16. at least one derived_rule is marked judgment: true
 17. INVARIANTS: every invariants[].expression evaluates true against the pack,
     with equality relaxed to the invariant's tolerance
 18. every derived_rules[].expression evaluates to a finite number over a sweep of
     sample bindings, and lands inside its declared range (warning if outside)

Run:  python3 build/check_systems.py [--dir proportions/systems] [--verbose]
Exit: 0 clean, 1 on any error. Warnings do not fail the build.
"""
import argparse
import ast
import glob
import json
import math
import os
import re
import sys

import jsonschema

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SYSTEM_KINDS = {"facade-system", "room-system", "trim-system", "opening-system"}
RULE_BAND = (12, 20)
CONFLICT_BAND = (3, 6)
SUM_TOL = 1e-6

CONFLICT_WITH = {
    "energy-code", "egress-code", "accessibility-code", "structural", "cost",
    "material-availability", "climate", "zoning", "construction-tolerance",
}

# Variables the engine binds when it evaluates a derived_rule in a system pack.
RULE_VARS = {
    "module", "part", "ceiling_height", "opening_width", "opening_height", "storey_height",
    "column_height", "wall_thickness", "span", "room_length", "room_width",
}
RULE_FUNCS = {"floor", "ceil", "round", "min", "max", "abs", "sqrt"}

MASSING_REF = re.compile(r"massing:([a-z0-9]+(?:-[a-z0-9]+)*)")

# A sweep of plausible bindings. Every derived_rule expression must survive all of
# them and return a finite number.
SAMPLE_BINDINGS = [
    {"opening_width": 30.0, "ceiling_height": 96.0, "storey_height": 108.0,
     "column_height": 96.0, "wall_thickness": 5.5, "span": 144.0,
     "room_length": 168.0, "room_width": 132.0},
    {"opening_width": 36.0, "ceiling_height": 114.0, "storey_height": 126.0,
     "column_height": 120.0, "wall_thickness": 9.0, "span": 216.0,
     "room_length": 240.0, "room_width": 192.0},
    {"opening_width": 42.0, "ceiling_height": 132.0, "storey_height": 150.0,
     "column_height": 144.0, "wall_thickness": 13.5, "span": 288.0,
     "room_length": 288.0, "room_width": 216.0},
]


# ------------------------------------------------------------------ expressions

class SafeEval(ast.NodeVisitor):
    """Evaluate a restricted arithmetic/comparison expression over a namespace
    addressed by dotted paths, e.g. assemblies.wall_section_georgian.height_modules
    or assemblies.elevation.members.storey_one.height_parts (a list of dicts is
    addressable by the members' "id")."""

    ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)
    ALLOWED_CMP = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)
    FUNCS = {"floor": math.floor, "ceil": math.ceil, "round": round,
             "min": min, "max": max, "abs": abs, "sqrt": math.sqrt}

    def __init__(self, root, tolerance):
        self.root = root
        self.tol = tolerance

    def resolve(self, node):
        parts, cur = [], node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if not isinstance(cur, ast.Name):
            raise ValueError("unsupported attribute base")
        parts.append(cur.id)
        parts.reverse()
        obj = self.root
        for p in parts:
            if isinstance(obj, dict) and p in obj:
                obj = obj[p]
            elif isinstance(obj, list):
                match = [x for x in obj if isinstance(x, dict) and x.get("id") == p]
                if len(match) != 1:
                    raise KeyError(".".join(parts))
                obj = match[0]
            else:
                raise KeyError(".".join(parts))
        if obj is None:
            raise KeyError(".".join(parts) + " is null")
        return obj

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if isinstance(node.value, (bool, int, float)):
            return node.value
        raise ValueError("only numeric constants allowed")

    def visit_Name(self, node):
        return self.resolve(node)

    def visit_Attribute(self, node):
        return self.resolve(node)

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name) or node.func.id not in self.FUNCS:
            raise ValueError("only floor/ceil/round/min/max/abs/sqrt may be called")
        if node.keywords:
            raise ValueError("keyword arguments not allowed")
        return self.FUNCS[node.func.id](*[self.visit(a) for a in node.args])

    def visit_BoolOp(self, node):
        vals = [self.visit(v) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(bool(v) for v in vals)
        if isinstance(node.op, ast.Or):
            return any(bool(v) for v in vals)
        raise ValueError("unsupported boolean op")

    def visit_UnaryOp(self, node):
        v = self.visit(node.operand)
        if isinstance(node.op, ast.USub):
            return -v
        if isinstance(node.op, ast.UAdd):
            return +v
        if isinstance(node.op, ast.Not):
            return not bool(v)
        raise ValueError("unsupported unary op")

    def visit_BinOp(self, node):
        if not isinstance(node.op, self.ALLOWED_BINOPS):
            raise ValueError("unsupported binary op")
        a, b = self.visit(node.left), self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return a + b
        if isinstance(node.op, ast.Sub):
            return a - b
        if isinstance(node.op, ast.Mult):
            return a * b
        if isinstance(node.op, ast.Div):
            return a / b
        if isinstance(node.op, ast.Pow):
            return a ** b
        return a % b

    def visit_Compare(self, node):
        left, ok = self.visit(node.left), True
        for op, comp in zip(node.ops, node.comparators):
            right = self.visit(comp)
            if not isinstance(op, self.ALLOWED_CMP):
                raise ValueError("unsupported comparison")
            if isinstance(op, ast.Eq):
                ok = ok and math.isclose(left, right, rel_tol=0, abs_tol=max(self.tol, 1e-12))
            elif isinstance(op, ast.NotEq):
                ok = ok and not math.isclose(left, right, rel_tol=0, abs_tol=max(self.tol, 1e-12))
            elif isinstance(op, ast.Lt):
                ok = ok and left < right + self.tol
            elif isinstance(op, ast.LtE):
                ok = ok and left <= right + self.tol
            elif isinstance(op, ast.Gt):
                ok = ok and left > right - self.tol
            elif isinstance(op, ast.GtE):
                ok = ok and left >= right - self.tol
            left = right
        return ok

    def generic_visit(self, node):
        raise ValueError(f"unsupported syntax: {type(node).__name__}")


def eval_invariant(expr, pack, tol):
    return SafeEval(pack, tol).visit(ast.parse(expr, mode="eval"))


def eval_rule(expr, module_in, parts, binding):
    env = dict(SafeEval.FUNCS)
    env.update(binding)
    env["module"] = module_in
    env["part"] = module_in / parts
    return eval(compile(ast.parse(expr, mode="eval"), "<rule>", "eval"),
                {"__builtins__": {}}, env)


def rule_expr_vars(expr):
    tree = ast.parse(expr, mode="eval")
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}


# ------------------------------------------------------------------ loaders

def load_slot_ids(path):
    ids = set()
    for group in json.load(open(path, encoding="utf-8"))["groups"]:
        for slot in group["slots"]:
            ids.add(slot["id"])
    return ids


def load_style_ids(styles_dir):
    return {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(styles_dir, "*.json"))}


def load_massing_ids(path):
    if not os.path.exists(path):
        return set()
    return {m["id"] for m in json.load(open(path, encoding="utf-8"))}


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(ROOT, "proportions", "systems"))
    ap.add_argument("--schema", default=os.path.join(ROOT, "schema", "proportion-pack.schema.json"))
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    schema = json.load(open(args.schema, encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    slots = load_slot_ids(os.path.join(ROOT, "elements", "slots.json"))
    styles = load_style_ids(os.path.join(ROOT, "styles"))
    massings = load_massing_ids(os.path.join(ROOT, "massings", "catalog.json"))

    errs, warns, seen = [], [], {}
    files = sorted(glob.glob(os.path.join(args.dir, "*.json")))
    if not files:
        print(f"no system packs found in {args.dir}", file=sys.stderr)
        return 1

    for path in files:
        base = os.path.basename(path)[:-5]
        E = lambda m: errs.append(f"{base}: {m}")
        W = lambda m: warns.append(f"{base}: {m}")

        try:
            pack = json.load(open(path, encoding="utf-8"))
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

        if pack["kind"] not in SYSTEM_KINDS:
            E(f"kind is '{pack['kind']}', expected one of {sorted(SYSTEM_KINDS)}")
        family = base.split("-")[0]
        expected = {"facade": "facade-system", "room": "room-system",
                    "trim": "trim-system", "opening": "opening-system"}.get(family)
        if expected and pack["kind"] != expected:
            E(f"filename family '{family}' implies kind '{expected}', got '{pack['kind']}'")

        if not pack["authority"].get("strength"):
            E("authority.strength missing")

        mod = pack["module"]
        if not isinstance(mod.get("default_size_in"), (int, float)):
            E("module.default_size_in must be a real number so the engine runs untold")
        if mod["parts"] <= 0:
            E("module.parts must be positive")

        # ---- derived rules
        rules = pack.get("derived_rules", [])
        if not (RULE_BAND[0] <= len(rules) <= RULE_BAND[1]):
            W(f"{len(rules)} derived_rules, expected {RULE_BAND[0]}-{RULE_BAND[1]}")
        n_judgment = 0
        for i, r in enumerate(rules):
            if r.get("judgment"):
                n_judgment += 1
            if r["target_slot"] not in slots:
                E(f"derived_rules[{i}]: unknown target_slot '{r['target_slot']}'")
            rng = r.get("range")
            if rng is not None and rng[0] > rng[1]:
                E(f"derived_rules[{i}]: range {rng} is inverted")
            expr = (r.get("expression") or "").strip()
            if not expr:
                E(f"derived_rules[{i}]: empty expression")
                continue
            try:
                unknown = rule_expr_vars(expr) - RULE_VARS - RULE_FUNCS
            except SyntaxError as exc:
                E(f"derived_rules[{i}]: expression does not parse: {expr} ({exc})")
                continue
            if unknown:
                E(f"derived_rules[{i}] ({r['target_slot']}): unbound variable(s) "
                  f"{sorted(unknown)} in '{expr}'")
                continue
            for b in SAMPLE_BINDINGS:
                try:
                    v = eval_rule(expr, mod["default_size_in"], mod["parts"], b)
                except Exception as exc:
                    E(f"derived_rules[{i}] ({r['target_slot']}): '{expr}' failed on {b}: {exc}")
                    break
                if not isinstance(v, (int, float)) or not math.isfinite(v):
                    E(f"derived_rules[{i}] ({r['target_slot']}): non-finite result {v!r}")
                    break
                if rng and not (rng[0] <= v <= rng[1]):
                    # `b['opening_width', 'opening_height']` was a TUPLE KEY, not a fallback -- a
                    # KeyError every time it ran, which means it never ran: this path is reached
                    # only when a rule lands outside its own declared range. check_modules.py had
                    # the identical line and it was fixed on 25 Aug when a module pack finally went
                    # out of band; its sibling -- the checker covering the 18 SYSTEM packs, which is
                    # most of what WP-4.6 wrote -- was left with the bug. Found by audit the same
                    # day. Second occurrence of a bug fixed once is this codebase's standing pattern.
                    ctx = ", ".join(f"{k}={b[k]:g}" for k in sorted(b))
                    W(f"derived_rules[{i}] ({r['target_slot']}/{r.get('dimension')}): "
                      f"{v:g} outside declared range {rng} at {ctx}")
                elif args.verbose:
                    print(f"    ok  {base}.rule[{i}] {r['target_slot']} -> {v:g}")
        if rules and n_judgment == 0:
            E("no derived_rule is marked judgment: true - a pack that claims to know "
              "everything is not trustworthy")

        # ---- conflicts
        confs = pack.get("conflicts", [])
        if not (CONFLICT_BAND[0] <= len(confs) <= CONFLICT_BAND[1]):
            W(f"{len(confs)} conflicts, expected {CONFLICT_BAND[0]}-{CONFLICT_BAND[1]}")
        for i, c in enumerate(confs):
            if c["with"] not in CONFLICT_WITH:
                E(f"conflicts[{i}]: unknown 'with' value '{c['with']}'")
            if not c.get("resolution"):
                W(f"conflicts[{i}] ({c['with']}): no resolution given")

        # ---- referential integrity
        for sid in pack.get("applies_to", []):
            if sid not in styles:
                E(f"applies_to: unknown style node '{sid}'")

        blob = json.dumps(pack)
        for mid in set(MASSING_REF.findall(blob)):
            if massings and mid not in massings:
                E(f"unknown massing cross-reference 'massing:{mid}'")

        # ---- assemblies
        for name, asm in (pack.get("assemblies") or {}).items():
            ids = [m["id"] for m in asm["members"]]
            dupes = sorted({i for i in ids if ids.count(i) > 1})
            if dupes:
                E(f"assemblies.{name}: duplicate member ids {dupes}")
            total = sum(m["height_parts"] for m in asm["members"])
            want = asm["height_modules"] * mod["parts"]
            if asm.get("sums_check", True):
                if abs(total - want) > SUM_TOL:
                    E(f"assemblies.{name}: members sum to {total!r} parts, "
                      f"height_modules*parts = {want!r} (delta {total - want:g})")
                elif args.verbose:
                    print(f"    ok  {base}.{name}: {total:g} parts")
            else:
                explained = any("sums_check" in (m.get("note") or "").lower()
                                for m in asm["members"])
                if not explained:
                    E(f"assemblies.{name}: sums_check false with no member note explaining why")
                else:
                    W(f"assemblies.{name}: sums_check disabled "
                      f"(members sum {total:g}, stated {want:g})")

        # ---- invariants
        for i, inv in enumerate(pack.get("invariants", [])):
            tol = inv.get("tolerance", 0.02)
            try:
                result = eval_invariant(inv["expression"], pack, tol)
            except Exception as exc:
                E(f"invariants[{i}]: could not evaluate '{inv['expression']}': {exc}")
                continue
            if result is not True:
                E(f"invariants[{i}] FAILED: {inv['statement'][:80]}  "
                  f"[{inv['expression']}] -> {result!r}")
            elif args.verbose:
                print(f"    ok  {base}.invariant[{i}]: {inv['expression']}")

    for w in warns:
        print(f"WARN  {w}")
    for e in errs:
        print(f"ERROR {e}")
    print(f"\n{len(files)} system pack(s) checked, {len(errs)} error(s), {len(warns)} warning(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
