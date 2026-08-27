#!/usr/bin/env python3
"""Validate proportion packs.

For every pack in proportions/**/*.json this script:
  1. parses the JSON;
  2. validates it against schema/proportion-pack.schema.json;
  3. asserts that each assembly's member heights sum to height_modules * module.parts
     (unless the assembly sets sums_check: false, which must then be explained in a
     member note -- an unexplained false is itself an error);
  4. evaluates every `invariant` expression against the pack;
  5. checks referential integrity of derived_rules.target_slot against elements/slots.json
     and of applies_to against styles/*.json;
  6. checks that derived_rule expressions only use variables the engine binds, and parse;
  7. resolves every `overlay_of` against the rest of the corpus: the target must exist,
     must be the same `kind`, must not be the pack itself, and where the overlay
     subdivides its module differently from its base (Chambers and Benjamin both use
     thirty minutes against Vignola's twelve or eighteen) module.note must say so,
     because otherwise every height_parts figure reads against the wrong module.
     An overlay legitimately omits assemblies, invariants and most of `column`;
     nothing in this step demands completeness of an overlay.

Exit status is non-zero if any check fails. Warnings do not fail the build.

Run:  python3 build/check_orders.py [--verbose]
"""
import ast
import glob
import json
import math
import os
import sys

# The engine, by path, through the shared module cache — build/modcache.py exists because a
# local by-path loader re-executes the module on every call (OQ 28).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modcache
ENGINE = modcache.load("proportion_engine",
                       os.path.join(os.path.dirname(os.path.abspath(__file__)), "proportion_engine.py"))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(ROOT, "schema", "proportion-pack.schema.json")
PACK_GLOB = os.path.join(ROOT, "proportions", "**", "*.json")

# Variables the rules engine promises to bind when it evaluates a derived_rule.
# The first six are what an order pack needs. The last four are bound in addition for
# the module and system packs, which proportion rooms, walls and whole elevations:
# check_modules.py already sweeps wall_thickness and span, and the room systems need
# the plan dimensions. See build/check_systems.py, which uses the same set.
RULE_VARS = {"module", "part", "ceiling_height", "opening_width", "opening_height", "storey_height",
             "column_height", "wall_thickness", "span", "room_length", "room_width"}
# Helper functions a derived_rule expression may call.
RULE_FUNCS = {"floor", "ceil", "round", "min", "max", "abs", "sqrt"}

FLOAT_TOL = 1e-6

errors = []
warnings = []
notes = []
checked = 0
# id -> pack, for every pack that declares overlay_of; resolved after all are loaded.
overlays = {}
# id -> pack, every pack in the corpus.
by_id = {}


def err(pack_id, msg):
    errors.append(f"{pack_id}: {msg}")


def warn(pack_id, msg):
    warnings.append(f"{pack_id}: {msg}")


def note(pack_id, msg):
    """A third state: neither wrong nor clean, but a fact the corpus must not hold silently.

    OQ 72's whole cost was that a pack disagreeing with its own declaration said nothing, so the
    published account of it claimed the column family was sound. This is what a checker owes a
    known, ruled, handled condition -- disclosure without the false alarm of a warning."""
    notes.append(f"{pack_id}: {msg}")


# ---------------------------------------------------------------- expressions

class SafeEval(ast.NodeVisitor):
    """Evaluate a restricted arithmetic/comparison expression over a namespace
    addressed by dotted paths (e.g. assemblies.cornice.height_modules)."""

    ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod)
    ALLOWED_CMP = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)
    FUNCS = {"floor": math.floor, "ceil": math.ceil, "round": round,
             "min": min, "max": max, "abs": abs, "sqrt": math.sqrt}

    def __init__(self, root, tolerance):
        self.root = root
        self.tol = tolerance

    # -- resolution of dotted names -------------------------------------------
    def resolve(self, node):
        parts = []
        cur = node
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
                # allow addressing a list of dicts by their "id"
                match = [x for x in obj if isinstance(x, dict) and x.get("id") == p]
                if len(match) != 1:
                    raise KeyError(".".join(parts))
                obj = match[0]
            else:
                raise KeyError(".".join(parts))
        if obj is None:
            raise KeyError(".".join(parts) + " is null")
        return obj

    # -- visitors --------------------------------------------------------------
    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if isinstance(node.value, bool) or isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("only numeric constants allowed")

    def visit_Name(self, node):
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

    def visit_Attribute(self, node):
        return self.resolve(node)

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
        left = self.visit(node.left)
        ok = True
        for op, comp in zip(node.ops, node.comparators):
            right = self.visit(comp)
            if not isinstance(op, self.ALLOWED_CMP):
                raise ValueError("unsupported comparison")
            if isinstance(op, ast.Eq):
                ok = ok and math.isclose(left, right, rel_tol=0, abs_tol=self.tol)
            elif isinstance(op, ast.NotEq):
                ok = ok and not math.isclose(left, right, rel_tol=0, abs_tol=self.tol)
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


def eval_expr(expr, root, tolerance):
    tree = ast.parse(expr, mode="eval")
    return SafeEval(root, tolerance).visit(tree)


def rule_expr_vars(expr):
    """Free variable names used by a derived_rule expression."""
    tree = ast.parse(expr, mode="eval")
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}


# ---------------------------------------------------------------- main checks

def check_pack(path, schema, slot_ids, style_ids, verbose=False):
    global checked
    base = os.path.basename(path)[:-5]
    try:
        pack = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        errors.append(f"{base}: UNPARSEABLE JSON: {e}")
        return
    pid = pack.get("id", base)

    # 1. schema
    try:
        import jsonschema
        jsonschema.validate(pack, schema)
    except ImportError:
        warn(pid, "jsonschema not installed; schema validation skipped")
    except Exception as e:
        err(pid, f"SCHEMA {'/'.join(str(p) for p in getattr(e, 'absolute_path', []))}: {e.message}")
        return

    if pid != base:
        err(pid, f"id '{pid}' does not match filename '{base}'")
    if pid in by_id:
        err(pid, "duplicate pack id")
    by_id[pid] = pack

    parts = pack["module"]["parts"]

    # 2. assembly sums
    for name, asm in pack.get("assemblies", {}).items():
        expected = asm["height_modules"] * parts
        total = sum(m["height_parts"] for m in asm["members"])
        sums_check = asm.get("sums_check", True)
        if sums_check:
            if not math.isclose(total, expected, rel_tol=0, abs_tol=FLOAT_TOL):
                err(pid, f"assembly '{name}' members sum to {total} parts, "
                         f"expected {expected} ({asm['height_modules']} modules x {parts} parts)")
            elif verbose:
                print(f"    ok  {pid}.{name}: {total} parts")
        else:
            explained = any("sums_check" in (m.get("note") or "").lower() for m in asm["members"])
            if not explained:
                err(pid, f"assembly '{name}' sets sums_check false with no member note explaining why")
            else:
                warn(pid, f"assembly '{name}' sums_check disabled (members sum {total}, "
                          f"stated {expected}) - explained in a member note")
        # duplicate member ids
        ids = [m["id"] for m in asm["members"]]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            err(pid, f"assembly '{name}' has duplicate member ids: {sorted(dupes)}")

        # WP-5.7: a repeating member's own width against its own pitch. A tooth as wide as its
        # pitch leaves no gap between teeth, which is a solid band with extra steps; a tooth
        # WIDER than its pitch is teeth overlapping each other, which cannot be built. Neither is
        # caught by the schema, because both are perfectly good numbers on their own.
        for m in asm["members"]:
            w, sp = m.get("width_parts"), m.get("spacing_parts")
            if w is None:
                continue
            if w <= 0:
                err(pid, f"member '{m['id']}': width_parts {w} is not a width")
            elif sp is None:
                err(pid, f"member '{m['id']}': states a width_parts of {w} but no spacing_parts "
                         f"to lay it out on — a width without a pitch places nothing")
            elif w >= sp:
                err(pid, f"member '{m['id']}': width_parts {w} is not under its own pitch of "
                         f"{sp} — teeth this wide leave no gap between them")

    # 3. invariants
    for inv in pack.get("invariants", []):
        tol = inv.get("tolerance", 0.02)
        try:
            result = eval_expr(inv["expression"], pack, tol)
        except Exception as e:
            err(pid, f"invariant '{inv['expression']}' could not be evaluated: {e}")
            continue
        if result is not True:
            err(pid, f"invariant FAILS: {inv['statement']}  [{inv['expression']}]")
        elif verbose:
            print(f"    ok  {pid} invariant: {inv['expression']}")

    # 4. derived_rules
    for r in pack.get("derived_rules", []):
        if slot_ids and r["target_slot"] not in slot_ids:
            err(pid, f"derived_rule target_slot '{r['target_slot']}' is not a slot id in elements/slots.json")
        try:
            used = rule_expr_vars(r["expression"])
        except SyntaxError as e:
            err(pid, f"derived_rule expression does not parse: {r['expression']} ({e})")
            continue
        unknown = used - RULE_VARS - RULE_FUNCS
        if unknown:
            err(pid, f"derived_rule '{r['target_slot']}' uses unbound variable(s) {sorted(unknown)} "
                     f"in '{r['expression']}'")
        rng = r.get("range")
        if rng and rng[0] > rng[1]:
            err(pid, f"derived_rule '{r['target_slot']}' has an inverted range {rng}")

    # 8. EVALUATE every ranged rule against its own band.
    #
    # check_modules.py --eval and check_systems.py have both done this for years, and neither
    # covers proportions/orders/ or proportions/overlays/ -- which is where 22 rules were
    # sitting outside their own declared bands, published to the workbench as "· out of band",
    # with no checker looking (OQ 68). Evaluation goes through proportion_engine.evaluate()
    # rather than a second implementation here, so what this checks is exactly what the MCP
    # tool and the workbench publish: the same tolerance, and the same withholding of
    # judgement where a rule states a calibration context the default bindings are outside.
    #
    # A violation is a WARNING and not an error, deliberately. Two survive at the time of
    # writing and both are recorded in OQ 68 as wanting a ruling rather than a patch; turning
    # them into errors would fail the build on two findings the corpus is correctly making.
    try:
        ev = ENGINE.evaluate(pack)
    except Exception as exc:
        err(pid, f"derived_rules could not be evaluated: {exc}")
        ev = None
    for r in (ev or {}).get("rules", []):
        if r.get("error"):
            err(pid, f"derived_rule '{r['target_slot']}' failed to evaluate: {r['error']}")
        elif r.get("in_range") is False:
            warn(pid, f"derived_rule '{r['target_slot']}/{r.get('dimension')}' evaluates to "
                      f"{r['value']:g} {r.get('units') or ''}".rstrip()
                      + f", outside its own declared range {r['range']}")

    n_judgment = sum(1 for r in pack.get("derived_rules", []) if r.get("judgment"))
    if pack.get("derived_rules") and n_judgment == 0:
        warn(pid, "no derived_rule is marked judgment: true - a pack that claims to know everything is suspect")

    # 5. applies_to referential integrity
    for s in pack.get("applies_to", []):
        if style_ids and s not in style_ids:
            err(pid, f"applies_to '{s}' is not a style node id in styles/")

    # 6. overlay target -- resolved in a second pass by check_overlays()
    if pack.get("overlay_of"):
        overlays[pid] = pack

    checked += 1


# ---------------------------------------------------------------- overlays

def _profiles():
    import importlib.util
    spec = importlib.util.spec_from_file_location("prof", os.path.join(ROOT, "build", "profiles.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def check_projection_datum(by_id):
    """OQ 65, ruled 26 Aug 2026. Every pack whose members carry a projection at all must
    say which datum it was measured from, and the declaration is VERIFIED against the
    pack's own geometry rather than trusted: a shaft body reads 0 under the naked reading
    and the semidiameter under the axis reading, and a capital's widest member cannot sit
    inside the shaft. A pack that declares one thing and draws another is worse than a
    pack that declares nothing, because the next consumer will believe it."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("pe", os.path.join(ROOT, "build", "proportion_engine.py"))
    pe = importlib.util.module_from_spec(spec); spec.loader.exec_module(pe)
    for pid, pack in sorted(by_id.items()):
        if pack.get("kind") != "order-system":
            continue
        try:
            r = pe.resolve(pid)
            d = pe.dimension(r, 36.0, None)
        except Exception as e:                    # a pack that will not dimension is
            warn(pid, f"could not dimension for the projection-datum check: {e}")
            continue
        has_proj = any((m.get("projection_in") or 0)
                       for a in d["assemblies"] for m in a.get("members", []))
        declared = d.get("projection_datum")
        if not has_proj:
            continue                              # nothing to measure from: nothing to say
        if not declared:
            err(pid, "carries projections but no projection_datum — a reader cannot tell "
                     "whether a figure is an offset from the naked or a radius from the "
                     "axis, and guessing draws the shaft narrower than its own mouldings "
                     "(OQ 65)")
            continue
        observed = pe.observed_projection_datum(d)
        if observed is None:
            warn(pid, f"declares projection_datum '{declared}' and its own geometry cannot "
                      f"confirm it — no published shaft body and no base or capital to read")
        elif observed != declared:
            err(pid, f"declares projection_datum '{declared}' but its geometry reads "
                     f"'{observed}' — one of the two is wrong and every drawing of this "
                     f"pack is wrong with it")


        # WHERE THE DECLARATION DOES NOT HOLD, reported per assembly-group (OQ 72, ruled
        # 27 Aug 2026). This check read the SHAFT and nothing else, so it passed gibbs-ionic
        # clean while that pack's whole capital, whole pedestal and whole entablature
        # contradicted the same declaration -- and the published account of OQ 72 said the
        # column family was sound on the strength of it.
        #
        # This is a NOTE, not an error. The declaration is the COLUMN's and is correct there;
        # build/profiles.py::pack_geometry now detects the reading per group from the pack's own
        # evidence, so a pack that disagrees with itself is drawn right rather than drawn wrong
        # and blamed. What must never happen again is that it disagrees SILENTLY.
        if declared == "axis":
            try:
                geo = _profiles().pack_geometry(d, r.get("column"), declared)
            except Exception as e:
                warn(pid, f"could not read assembly datums: {e}")
            else:
                naked_groups = sorted({a for a, v in geo["assembly_datum"].items() if v == "naked"})
                if naked_groups:
                    note(pid, "declares axis, but its own figures read as relief from the naked "
                              f"in: {', '.join(naked_groups)} — drawn that way by evidence "
                              f"(OQ 72), not by the declaration")

def check_overlays(by_id):
    """Resolve every overlay_of against the loaded corpus.

    An overlay carries ONLY its deltas: it legitimately omits assemblies,
    invariants, intercolumniation and most of `column`, all of which it
    inherits from its base. Nothing here may therefore demand completeness.
    What it does check is that the pointer is real and that the two packs are
    the same kind of thing, so a typo in overlay_of cannot silently produce an
    overlay that inherits from nothing.
    """
    for pid, pack in sorted(overlays.items()):
        target = pack["overlay_of"]
        if target == pid:
            err(pid, "overlay_of points at itself")
            continue
        base = by_id.get(target)
        if base is None:
            err(pid, f"overlay_of '{target}' does not name any pack under proportions/")
            continue
        if base.get("overlay_of"):
            warn(pid, f"overlay_of '{target}' is itself an overlay - inheritance is chained, "
                      f"which no consumer of these packs currently resolves")
        if base.get("kind") != pack.get("kind"):
            err(pid, f"overlay kind '{pack.get('kind')}' does not match base "
                     f"'{target}' kind '{base.get('kind')}'")
        # A different module subdivision is legitimate -- Benjamin uses Chambers's
        # 30 minutes where Vignola uses 12 or 18 -- but every height_parts figure
        # in the overlay then means something different from the base's, so it
        # has to be stated rather than left for a reader to discover.
        bp, op = base.get("module", {}).get("parts"), pack.get("module", {}).get("parts")
        if bp and op and bp != op:
            note = (pack.get("module", {}).get("note") or "").lower()
            if not any(tok in note for tok in ("part", "minute", "subdivid")):
                err(pid, f"module.parts {op} differs from base '{target}' ({bp}) and "
                         f"module.note does not explain it - every height_parts in this "
                         f"pack would be read against the wrong module")
            else:
                warn(pid, f"module.parts {op} differs from base '{target}' ({bp}) - "
                          f"explained in module.note")
        # An overlay that restates nothing is pointless; one that restates
        # everything is not an overlay.
        if not any(k in pack for k in ("assemblies", "column", "derived_rules", "conflicts")):
            warn(pid, f"overlay of '{target}' carries no assemblies, column, derived_rules "
                      f"or conflicts - it states no delta")


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    schema = json.load(open(SCHEMA_PATH, encoding="utf-8"))

    slot_ids = set()
    slots_path = os.path.join(ROOT, "elements", "slots.json")
    if os.path.exists(slots_path):
        for g in json.load(open(slots_path, encoding="utf-8"))["groups"]:
            for s in g["slots"]:
                slot_ids.add(s["id"])

    style_ids = set()
    for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        style_ids.add(os.path.basename(f)[:-5])

    packs = sorted(glob.glob(PACK_GLOB, recursive=True))
    if not packs:
        print("no proportion packs found under proportions/", file=sys.stderr)
        return 1

    for p in packs:
        if verbose:
            print(f"  {os.path.relpath(p, ROOT)}")
        check_pack(p, schema, slot_ids, style_ids, verbose)

    check_overlays(by_id)
    check_projection_datum(by_id)

    for n in notes:
        print(f"NOTE  {n}")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    print(f"\n{checked} pack(s) checked, {len(errors)} error(s), "
          f"{len(warnings)} warning(s), {len(notes)} note(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
