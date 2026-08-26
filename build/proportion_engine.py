#!/usr/bin/env python3
"""The proportion engine.

A proportion pack is a function, not a table. Give it a module and a context and it
emits a fully dimensioned assembly. This module is that function.

  resolve(pack_id)                 merge an overlay onto its base, normalising modules
  dimension(pack, module_in)       absolute dimensions and stacking positions per member
  evaluate(pack, bindings)         run the derived_rules
  check_invariants(pack)           prove the pack satisfies what it claims about itself

CLI:
  python3 build/proportion_engine.py list
  python3 build/proportion_engine.py show vignola-corinthian --module 6
  python3 build/proportion_engine.py show gibbs-ionic --module 7 --rules --ceiling 108
  python3 build/proportion_engine.py compare vignola-doric gibbs-doric benjamin-doric
"""
import json, os, glob, ast, math, copy, argparse, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE_VERSION = "0.1.0"

# ---------------------------------------------------------------- load
def load_all():
    packs = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "**", "*.json"), recursive=True)):
        p = json.load(open(f))
        p["_file"] = os.path.relpath(f, ROOT)
        packs[p["id"]] = p
    return packs

PACKS = load_all()

# ---------------------------------------------------------------- safe expressions
_ALLOWED = {
    "floor": math.floor, "ceil": math.ceil, "round": round, "min": min, "max": max,
    "abs": abs, "sqrt": math.sqrt, "pi": math.pi,
}

class ExprError(Exception): pass

def _eval_node(node, env):
    if isinstance(node, ast.Expression): return _eval_node(node.body, env)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, bool)): return node.value
        raise ExprError(f"constant {node.value!r} not allowed")
    if isinstance(node, ast.Name):
        if node.id in env: return env[node.id]
        if node.id in _ALLOWED: return _ALLOWED[node.id]
        raise ExprError(f"unbound name '{node.id}'")
    if isinstance(node, ast.Attribute):
        base = _eval_node(node.value, env)
        if isinstance(base, dict) and node.attr in base: return base[node.attr]
        # assemblies.X.members.<member_id> — address a list of records by its id field
        if isinstance(base, list):
            for it in base:
                if isinstance(it, dict) and it.get("id") == node.attr: return it
        raise ExprError(f"no attribute '{node.attr}'")
    if isinstance(node, ast.BinOp):
        l, r = _eval_node(node.left, env), _eval_node(node.right, env)
        op = type(node.op)
        return {ast.Add: lambda: l + r, ast.Sub: lambda: l - r, ast.Mult: lambda: l * r,
                ast.Div: lambda: l / r, ast.Pow: lambda: l ** r,
                ast.Mod: lambda: l % r, ast.FloorDiv: lambda: l // r}[op]()
    if isinstance(node, ast.UnaryOp):
        v = _eval_node(node.operand, env)
        return -v if isinstance(node.op, ast.USub) else (+v if isinstance(node.op, ast.UAdd) else (not v))
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, env); out = True
        for op, comp in zip(node.ops, node.comparators):
            right = _eval_node(comp, env)
            out = out and {ast.Eq: left == right, ast.NotEq: left != right,
                           ast.Lt: left < right, ast.LtE: left <= right,
                           ast.Gt: left > right, ast.GtE: left >= right}[type(op)]
            left = right
        return out
    if isinstance(node, ast.BoolOp):
        vals = [_eval_node(v, env) for v in node.values]
        return all(vals) if isinstance(node.op, ast.And) else any(vals)
    if isinstance(node, ast.Call):
        fn = _eval_node(node.func, env)
        if fn not in _ALLOWED.values(): raise ExprError("call not allowed")
        return fn(*[_eval_node(a, env) for a in node.args])
    if isinstance(node, ast.IfExp):
        return _eval_node(node.body, env) if _eval_node(node.test, env) else _eval_node(node.orelse, env)
    raise ExprError(f"syntax {type(node).__name__} not allowed")

def evaluate_expr(expr, env):
    return _eval_node(ast.parse(expr, mode="eval"), env)

# ---------------------------------------------------------------- overlay resolution
def diameters_per_module(pack):
    """How many lower column diameters one module of this pack equals.

    Authorities do not agree on the module and this is the first thing that breaks an
    overlay. Vignola and Chambers use the SEMIdiameter; Palladio uses the WHOLE diameter
    (except his Doric). Merging an overlay onto a base without normalising here silently
    doubles or halves every dimension in the inherited half of the pack."""
    m = pack.get("module", {})
    if isinstance(m.get("diameters"), (int, float)): return float(m["diameters"])
    name = m.get("name", "").lower()
    # order matters: a Palladio note explaining the difference FROM Vignola contains the
    # word "semidiameter", so only the name itself may decide, and "whole" wins first.
    if "whole diameter" in name or "full diameter" in name: return 1.0
    if "semidiameter" in name or "semi-diameter" in name or "half" in name: return 0.5
    if "diameter" in name: return 1.0
    return 0.5

def _convert_assembly(a, ratio, part_ratio):
    a = copy.deepcopy(a)
    if isinstance(a.get("height_modules"), (int, float)):
        a["height_modules"] = a["height_modules"] * ratio
    for mem in a.get("members", []):
        for k in ("height_parts", "projection_parts", "spacing_parts"):
            if isinstance(mem.get(k), (int, float)): mem[k] = mem[k] * part_ratio
    return a

def _members_sum_to_whole(assembly, parts):
    if not assembly.get("members"): return False
    tot = sum(m.get("height_parts", 0) for m in assembly["members"]) / parts
    return abs(tot - assembly.get("height_modules", -1)) < 0.02

def resolve(pack_id, _seen=None):
    """Merge an overlay onto its base. Everything an overlay does not state, it inherits.

    An overlay assembly whose members sum to its stated height REPLACES the base assembly
    outright (the author has restated the whole stack). Otherwise it PATCHES member by id.
    That rule is deterministic and it is why overlays can both refine and rewrite."""
    _seen = _seen or set()
    if pack_id in _seen: raise ValueError(f"overlay cycle at {pack_id}")
    _seen.add(pack_id)
    if pack_id not in PACKS: raise KeyError(f"no pack '{pack_id}'")
    pack = copy.deepcopy(PACKS[pack_id])
    base_id = pack.get("overlay_of")
    if not base_id:
        pack["_resolved_from"] = [pack_id]
        return pack

    base = resolve(base_id, _seen)
    # --- normalise the base into the overlay's module system before merging anything
    bD, oD = diameters_per_module(base), diameters_per_module(pack)
    bP, oP = base["module"]["parts"], pack["module"]["parts"]
    mod_ratio = bD / oD                      # one base module in overlay modules
    part_ratio = (bD / bP) / (oD / oP)       # one base part in overlay parts
    rescaled = abs(mod_ratio - 1.0) > 1e-9 or abs(part_ratio - 1.0) > 1e-9
    if rescaled:
        base = copy.deepcopy(base)
        base["assemblies"] = {k: _convert_assembly(v, mod_ratio, part_ratio)
                              for k, v in (base.get("assemblies") or {}).items()}
        for k in ("height_modules", "shaft_height_modules"):
            if isinstance(base.get("column", {}).get(k), (int, float)):
                base["column"][k] = base["column"][k] * mod_ratio
    out = copy.deepcopy(base)
    out["_resolved_from"] = base.get("_resolved_from", [base_id]) + [pack_id]
    out["_overlay_notes"] = []

    for k in ("id", "name", "aka", "authority", "module", "confidence", "notes", "_file", "overlay_of"):
        if k in pack: out[k] = pack[k]

    parts = out["module"]["parts"]
    if "column" in pack:
        out.setdefault("column", {}).update(pack["column"])

    for aname, a in (pack.get("assemblies") or {}).items():
        if aname not in out.get("assemblies", {}) or _members_sum_to_whole(a, parts):
            out.setdefault("assemblies", {})[aname] = copy.deepcopy(a)
            out["_overlay_notes"].append(f"{aname}: replaced outright by {pack_id}")
        else:
            tgt = out["assemblies"][aname]
            if "height_modules" in a: tgt["height_modules"] = a["height_modules"]
            byid = {m["id"]: i for i, m in enumerate(tgt.get("members", []))}
            for m in a.get("members", []):
                if m["id"] in byid: tgt["members"][byid[m["id"]]] = copy.deepcopy(m)
                else: tgt.setdefault("members", []).append(copy.deepcopy(m))
            out["_overlay_notes"].append(f"{aname}: patched by {pack_id}")

    # Invariants are claims about ONE authority's system. An overlay that states any of
    # its own replaces the base's outright — Palladio does not owe Vignola his 1/4 rule.
    if pack.get("invariants"):
        out["invariants"] = copy.deepcopy(pack["invariants"])
        out["_overlay_notes"].append(f"invariants: replaced outright by {pack_id}")
    for key, keyfn in (("derived_rules", lambda r: (r.get("target_slot"), r.get("dimension"))),
                       ("conflicts", lambda c: (c.get("with"), c.get("statement")[:40]))):
        inherited = out.get(key, [])
        if key == "derived_rules" and rescaled:
            # a rule written in base modules means something else under a different module
            dropped = [r for r in inherited if "module" in r.get("expression", "") or "part" in r.get("expression", "")]
            if dropped:
                out["_overlay_notes"].append(
                    f"derived_rules: dropped {len(dropped)} inherited module-relative rule(s) — "
                    f"{base_id} measures in {bD} D per module, {pack_id} in {oD}")
            inherited = [r for r in inherited if r not in dropped]
        merged = {keyfn(x): x for x in inherited}
        for x in pack.get(key, []): merged[keyfn(x)] = x
        out[key] = list(merged.values())

    for k in ("intercolumniation", "applies_to", "sources"):
        if k in pack: out[k] = pack[k]
    return out

# ---------------------------------------------------------------- dimensioning
STACK_ORDER = ["pedestal", "base", "shaft", "capital", "architrave", "frieze", "cornice"]

def stack_for(pack):
    """Which assemblies actually make the vertical stack for this pack.

    Authorities publish unevenly. Benjamin's Greek Doric has no base at all and gives the
    entablature whole rather than in three; several overlays state only the members they
    changed. Rather than draw a broken order, derive what is missing and say so."""
    A = pack.get("assemblies") or {}
    out = []
    for a in ("pedestal", "subplinth", "base", "shaft", "capital"):
        if a in A: out.append(a)
    if all(x in A for x in ("architrave", "frieze", "cornice")):
        out += ["architrave", "frieze", "cornice"]
    elif "entablature" in A:
        out.append("entablature")
    return out

def _synth_shaft(pack, order):
    """A pack may state a column height and no shaft. The shaft is what is left over."""
    A = pack.get("assemblies") or {}
    col = (pack.get("column") or {}).get("height_modules")
    if not col or "shaft" in A: return None
    used = sum(A[a].get("height_modules", 0) for a in ("base", "capital") if a in A)
    h = col - used
    if h <= 0: return None
    return {"height_modules": h, "sums_check": False, "_derived": True,
            "members": [{"id": "shaft_derived", "name": "Shaft (derived: column less base and capital)",
                         "height_parts": h * pack["module"]["parts"], "projection_parts": 0,
                         "profile": "flat", "confidence": "medium",
                         "note": "This authority does not publish the shaft as its own assembly. Height derived from the stated column height."}]}

def dimension(pack, module_in=None, include=None):
    """Absolute dimensions for every member, with cumulative stacking positions."""
    mod = module_in if module_in is not None else (pack["module"].get("default_size_in") or 6.0)
    parts = pack["module"]["parts"]
    part_in = mod / parts
    pack = copy.deepcopy(pack)
    syn = _synth_shaft(pack, None)          # derive first, so the stack sees it
    if syn: pack.setdefault("assemblies", {})["shaft"] = syn
    order = [a for a in (include or stack_for(pack)) if a in (pack.get("assemblies") or {})]
    if syn and "shaft" not in order:
        i = order.index("capital") if "capital" in order else len(order)
        order.insert(i, "shaft")
    y = 0.0
    out = {"pack": pack["id"], "name": pack["name"], "engine_version": ENGINE_VERSION,
           "module_in": mod, "parts": parts, "part_in": part_in,
           "diameters_per_module": diameters_per_module(pack),
           "resolved_from": pack.get("_resolved_from", [pack["id"]]),
           "authority": pack.get("authority", {}).get("source"),
           "assemblies": [], "totals": {}}
    for aname in order:
        a = pack["assemblies"][aname]
        ay = y
        members = []
        # sums_check:false means the members stand SIDE BY SIDE, not stacked. The Doric
        # triglyph and metope are each the full height of the frieze; stacking them makes
        # the order nine inches too tall.
        side = a.get("sums_check", True) is False
        for m in a.get("members", []):
            h = m.get("height_parts", 0) * part_in
            my0 = ay if side else y
            members.append({
                "id": m["id"], "name": m["name"], "profile": m.get("profile", "flat"),
                "height_parts": m.get("height_parts", 0), "height_in": round(h, 4),
                "projection_parts": m.get("projection_parts", 0),
                "projection_in": round(m.get("projection_parts", 0) * part_in, 4),
                "y_bottom_in": round(my0, 4), "y_top_in": round(my0 + h, 4), "side_by_side": side,
                "count": m.get("count"), "spacing_in": (m["spacing_parts"] * part_in) if m.get("spacing_parts") else None,
                "enrichment": m.get("enrichment"), "confidence": m.get("confidence", "high"),
                "note": m.get("note"),
            })
            if not side: y += h
        if side: y = ay + a.get("height_modules", 0) * mod
        stated = a.get("height_modules", 0) * mod
        out["assemblies"].append({
            "id": aname, "height_modules": a.get("height_modules"),
            "height_in_stated": round(stated, 4),
            "height_in_summed": round(y - ay, 4),
            "sums_check": a.get("sums_check", True),
            "y_bottom_in": round(ay, 4), "y_top_in": round(y, 4), "members": members,
        })
    out["totals"]["stack_height_in"] = round(y, 4)
    col = pack.get("column", {})
    dpm = diameters_per_module(pack)
    diam = mod / dpm                      # NOT 2*mod — Palladio's module IS the diameter
    out["totals"]["lower_diameter_in"] = round(diam, 4)
    if col.get("height_modules"):
        out["totals"]["column_height_in"] = round(col["height_modules"] * mod, 4)
        out["totals"]["column_height_diameters"] = round(col["height_modules"] * dpm, 4)
        if col.get("diminution"):
            out["totals"]["upper_diameter_in"] = round(diam * col["diminution"], 4)
    ent = (pack.get("assemblies") or {}).get("entablature")
    if ent: out["totals"]["entablature_height_in"] = round(ent["height_modules"] * mod, 4)
    return out

# ---------------------------------------------------------------- rules
DEFAULT_BINDINGS = {
    "ceiling_height": 108.0, "opening_width": 36.0, "opening_height": 80.0, "storey_height": 120.0,
    "wall_thickness": 12.0, "span": 240.0, "room_length": 288.0, "room_width": 192.0,
}

def stated_precision(x):
    """Half a unit in the last decimal place the number was WRITTEN to.

    A band edge written `0.219` is not the real number 0.219; it is the author saying "0.219
    to the precision I am giving you", which is 0.2185-0.2195. Four rules evaluated 7/32 =
    0.21875 against a floor of 0.219 -- the three-decimal rounding of the very expression the
    band exists to contain -- and were reported out of band by 0.00025, while the workbench
    displayed the value rounded to 0.2188 and so printed a number that looked inside the band
    it said was violated.

    check_invariants() already carries this idea, and says why: "these are ratios written down
    by hand in the sixteenth century and stored as decimals. 5/6 is 0.8333333333 in the file
    and it is not going to equal 0.8333333333333333." This derives the tolerance from the
    author's own precision instead of choosing a constant, so a band written to four places
    gets a tenth of the slack of one written to three, and a band written `10` gets 0.05 --
    which is nothing, correctly.
    """
    CAP = 5e-4
    s = repr(float(x))
    if "e" in s or "E" in s:
        return 0.0
    frac = s.split(".")[1] if "." in s else ""
    frac = "" if frac == "0" else frac
    half_ulp = 0.5 * (10 ** -len(frac)) if frac else 0.5
    # CAPPED, and the cap is the point. Half a unit in the last place of an edge written `0.3`
    # is 0.05, which is 17% of the band and would forgive a genuine violation; of an edge
    # written `10` it is 0.5. The artefact this absorbs is decimal rounding at the three and
    # four places these bands are actually written to, and half a thousandth is the largest
    # step that can arise there. An edge written more precisely gets proportionately less.
    return min(half_ulp, CAP)


def out_of_calibration(rule, env, module_in):
    """The bindings a rule was calibrated for, and whether we are inside them.

    `calibrated_for` has been in the schema since the chair-rail correction, described as "the
    context in which this rule was calibrated. Outside it the rule still evaluates and should
    not be trusted" -- and nothing read it. Four of Benjamin's eave cornices say, in capitals,
    in their own authority note, BIND storey_height TO THE FULL WALL HEIGHT; DEFAULT_BINDINGS
    gives one 10 ft storey, and all four were duly reported out of band. Benjamin's own worked
    example is a 35 ft house and lands them squarely inside it.

    Returns a list of human-readable reasons, empty when the rule is in calibration. A rule
    outside its calibration is UNJUDGED -- `in_range` is withheld, not set False. Judging a
    rule against a binding its own note tells you not to use is the unjudged-reported-as-failed
    direction, and it convicted six rules of being wrong about a building they were never
    given.
    """
    cal = rule.get("calibrated_for") or {}
    reasons = []
    for k, band in cal.items():
        if k == "note" or not isinstance(band, (list, tuple)) or len(band) != 2:
            continue
        v = module_in if k == "module" else env.get(k)
        if v is None:
            continue
        if not (band[0] <= v <= band[1]):
            reasons.append(f"{k} is {v:g}, calibrated for {band[0]:g}-{band[1]:g}")
    return reasons


def evaluate(pack, module_in=None, bindings=None):
    mod = module_in if module_in is not None else (pack["module"].get("default_size_in") or 6.0)
    parts = pack["module"]["parts"]
    env = dict(DEFAULT_BINDINGS)
    env.update(bindings or {})
    env["module"] = mod
    env["part"] = mod / parts
    col = pack.get("column", {})
    env["column_height"] = col.get("height_modules", 0) * mod if col.get("height_modules") else env.get("column_height", 0)
    results = []
    for r in pack.get("derived_rules", []):
        row = {"target_slot": r["target_slot"], "dimension": r.get("dimension"),
               "quantity": r.get("quantity"),          # OQ 48: what the rule MEASURES
               "expression": r["expression"], "units": r.get("units"),
               "judgment": bool(r.get("judgment")), "range": r.get("range"),
               "note": r.get("note"), "authority_note": r.get("authority_note"),
               # calibrated_for and diagnostic complete the schema's eleven rule fields. They were
               # dropped here, and `resolve_kit.py:310` reads `calibrated_for` off this very row --
               # so `stale_calibration` was ALWAYS False and the warning at :594 could never fire.
               # `trim-classical`'s chair rail says in its own words that the derivation only
               # reaches the measured 30-32 in band at 142.5 in, and the resolver printed 22.75 in
               # with no warning. Same bug as `quantity` (fixed 25 Aug), found in the same audit:
               # a row rebuilt key-by-key from a richer source drops whatever nobody re-listed.
               # tests/test_wp46_packs.py compares this dict against the schema so it cannot recur.
               "calibrated_for": r.get("calibrated_for"), "diagnostic": r.get("diagnostic")}
        try:
            v = evaluate_expr(r["expression"], env)
            row["value"] = round(v, 4) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
            if r.get("range") and isinstance(v, (int, float)):
                lo, hi = r["range"]
                why = out_of_calibration(r, env, mod)
                if why:
                    # UNJUDGED, not failed. in_range is left absent exactly as it is for a rule
                    # with no range at all, and the reason is published beside it.
                    row["out_of_calibration"] = "; ".join(why)
                else:
                    tol = max(stated_precision(lo), stated_precision(hi))
                    row["in_range"] = (lo - tol) <= v <= (hi + tol)
        except Exception as e:
            row["error"] = str(e)
        results.append(row)
    return {"pack": pack["id"], "module_in": mod, "bindings": env, "rules": results}

def check_invariants(pack):
    """Prove the pack satisfies what it claims about itself.

    Equality is checked within the invariant's stated tolerance, because these are
    ratios written down by hand in the sixteenth century and stored as decimals.
    5/6 is 0.8333333333 in the file and it is not going to equal 0.8333333333333333."""
    env = {"assemblies": pack.get("assemblies", {}), "column": pack.get("column", {}),
           "module": pack.get("module", {})}
    out = []
    for inv in pack.get("invariants", []):
        row = {"statement": inv["statement"], "expression": inv["expression"]}
        tol = inv.get("tolerance", 0.02)
        try:
            holds = bool(evaluate_expr(inv["expression"], env))
            if not holds:
                tree = ast.parse(inv["expression"], mode="eval").body
                if isinstance(tree, ast.Compare) and len(tree.ops) == 1 and isinstance(tree.ops[0], ast.Eq):
                    l = _eval_node(tree.left, env); r = _eval_node(tree.comparators[0], env)
                    if isinstance(l, (int, float)) and isinstance(r, (int, float)):
                        holds = abs(l - r) <= max(tol, abs(r) * tol)
                        row["delta"] = round(l - r, 6)
            row["holds"] = holds
        except Exception as e:
            row["error"] = str(e); row["holds"] = None
        out.append(row)
    return out

# ---------------------------------------------------------------- cli
def _fmt_in(x):
    if x is None: return "-"
    ft, rem = divmod(x, 12)
    whole = int(rem); frac = rem - whole
    six = round(frac * 16)
    if six == 16: whole += 1; six = 0
    fs = f" {six}/16" if six else ""
    from fractions import Fraction
    if six:
        fr = Fraction(six, 16); fs = f" {fr.numerator}/{fr.denominator}"
    return (f"{int(ft)}'-" if ft else "") + f"{whole}{fs}\""

def main():
    ap = argparse.ArgumentParser(description="Traditional Design Language — proportion engine")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    s = sub.add_parser("show"); s.add_argument("pack"); s.add_argument("--module", type=float)
    s.add_argument("--rules", action="store_true"); s.add_argument("--ceiling", type=float)
    s.add_argument("--json", action="store_true")
    c = sub.add_parser("compare"); c.add_argument("packs", nargs="+")
    c.add_argument("--diameter", type=float, default=12.0,
                   help="Compare at a common COLUMN DIAMETER, not a common module — authorities do not share a module.")
    sub.add_parser("selftest")
    a = ap.parse_args()

    if a.cmd == "list":
        by = {}
        for p in PACKS.values(): by.setdefault(p["kind"], []).append(p)
        for k in sorted(by):
            print(f"\n{k}")
            for p in sorted(by[k], key=lambda x: x["id"]):
                ov = f"  overlay of {p['overlay_of']}" if p.get("overlay_of") else ""
                print(f"  {p['id']:<26} {p['name'][:46]:<48}{ov}")
        print(f"\n{len(PACKS)} packs")

    elif a.cmd == "show":
        pk = resolve(a.pack)
        d = dimension(pk, a.module)
        if a.json: print(json.dumps({"dimensions": d, "rules": evaluate(pk, a.module, {"ceiling_height": a.ceiling} if a.ceiling else None), "invariants": check_invariants(pk)}, indent=2)); return
        print(f"\n{pk['name']}   [{' → '.join(d['resolved_from'])}]")
        print(f"{pk['authority']['source']}")
        print(f"module {_fmt_in(d['module_in'])} in {d['parts']} parts, one part {_fmt_in(d['part_in'])}\n")
        for asm in d["assemblies"]:
            flag = "" if abs(asm["height_in_stated"] - asm["height_in_summed"]) < 0.01 or not asm["sums_check"] else "  ** SUM MISMATCH"
            print(f"  {asm['id'].upper():<14} {asm['height_modules']:>7} M   {_fmt_in(asm['height_in_stated']):>10}{flag}")
            for m in asm["members"]:
                cf = "" if m["confidence"] == "high" else f"  ({m['confidence']})"
                rep = f"  x{m['count']}" if m.get("count") else ""
                print(f"      {m['name'][:40]:<42}{m['height_parts']:>6}p {_fmt_in(m['height_in']):>9}  proj {_fmt_in(m['projection_in']):>8}  {m['profile']}{rep}{cf}")
        print(f"\n  TOTALS")
        for k, v in d["totals"].items(): print(f"      {k:<26}{_fmt_in(v)}")
        inv = check_invariants(pk)
        if inv:
            print(f"\n  INVARIANTS")
            for i in inv: print(f"      [{'ok ' if i['holds'] else 'FAIL'}] {i['statement'][:100]}")
        if a.rules:
            ev = evaluate(pk, a.module, {"ceiling_height": a.ceiling} if a.ceiling else None)
            print(f"\n  DERIVED RULES  (ceiling {_fmt_in(ev['bindings']['ceiling_height'])}, opening {_fmt_in(ev['bindings']['opening_width'])})")
            for r in ev["rules"]:
                j = " [JUDGMENT — designer decides]" if r["judgment"] else ""
                val = r.get("error") or (f"{_fmt_in(r['value'])}" if r.get("units") == "in" and isinstance(r.get("value"), (int, float)) else r.get("value"))
                print(f"      {r['target_slot']+'.'+(r['dimension'] or ''):<34}{str(val):>12}   {r['expression'][:44]}{j}")

    elif a.cmd == "compare":
        ds = []
        for pid in a.packs:
            pk = resolve(pid)
            ds.append(dimension(pk, a.diameter * diameters_per_module(pk)))
        keys = ["column_height_in", "column_height_diameters", "entablature_height_in", "upper_diameter_in"]
        print(f"\ncommon column diameter {_fmt_in(a.diameter)}\n")
        print(f"  {'':<26}" + "".join(f"{p[:20]:>22}" for p in a.packs))
        for k in keys:
            if k.endswith("_diameters"):
                print(f"  {k:<26}" + "".join(f"{(str(d['totals'].get(k))+' D'):>22}" for d in ds))
            else:
                print(f"  {k:<26}" + "".join(f"{_fmt_in(d['totals'].get(k)):>22}" for d in ds))
        for asm in STACK_ORDER + ["entablature"]:
            row = []
            for d in ds:
                m = next((x for x in d["assemblies"] if x["id"] == asm), None)
                row.append(_fmt_in(m["height_in_stated"]) if m else "—")
            if any(r != "—" for r in row):
                print(f"  {asm:<26}" + "".join(f"{r:>22}" for r in row))

    elif a.cmd == "selftest":
        bad = 0
        for pid in sorted(PACKS):
            pk = resolve(pid)
            d = dimension(pk)
            for asm in d["assemblies"]:
                if asm["sums_check"] and abs(asm["height_in_stated"] - asm["height_in_summed"]) > 0.01:
                    print(f"  SUM  {pid}.{asm['id']}: stated {asm['height_in_stated']} summed {asm['height_in_summed']}"); bad += 1
            for i in check_invariants(pk):
                if i["holds"] is not True:
                    print(f"  INV  {pid}: {i.get('error') or 'false'} :: {i['expression']}"); bad += 1
            for r in evaluate(pk)["rules"]:
                if "error" in r: print(f"  RULE {pid}.{r['target_slot']}: {r['error']}"); bad += 1
        print(f"\n{len(PACKS)} packs resolved and dimensioned, {bad} problem(s)")
        sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
