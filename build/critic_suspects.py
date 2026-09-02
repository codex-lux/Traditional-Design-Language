#!/usr/bin/env python3
"""critic_suspects.py — which of the critic's measurements are measurements of the GENERATOR
rather than of the house (WP-9.1).

WHY THIS EXISTS. Run the fault corpus against both shipped reference plans and the same
fifteen serious faults come back on both with IDENTICAL values: casing-at-a-third-of-palladio
at 0.6, house-without-a-base at 30.0, surround-that-lies-about-the-wall at 4.0, wing-pitch-drift
at 0.0. Those are not two houses sharing a defect; they are `build/elevation.py` stating a
constant -- `"window_reveal_depth_in": 4.0`, `casing_width_in * 0.6` -- and the corpus
convicting every classical plan of it. OQ 52 swept twelve invented constants out of the
measurements in August and guarded them with `NOT_MODELLED`; this file finds the class rather
than the instances, because a revision loop that OBEYED these findings would spend its rounds
chasing the generator's own numbers, and a loop that ignored them silently would be hiding a
finding. The analyst (build/critique.py) marks a fault whose failing test reads one of these
names `critic-suspect`, attaches the evidence, and never acts on it.

Three instruments, and the third cannot see everything:

  source_literals()  an AST read of `_derive_measurements`: every measurement name assigned a
                     bare numeric literal, with its line. Cheap; run at critique time.
  literal_ratios()   the same read for a real figure scaled by a literal --
                     `ent["casing_width_in"] * 0.6` -- which VARIES across plans and is still
                     the generator's number. Cheap; run at critique time.
  sweep(plans)       every name whose value is identical on every in-scope plan that supplies
                     it. Slow (an elevation per plan); the checker's meter, not runtime. It
                     sees constants the AST cannot (a value read from a pack that never
                     changes) and cannot see a ratio, which is why both exist.

A name is a suspect if any instrument names it, or if `critique/suspects.json` names the
(fault, expression) editorially with a quoted basis -- for the case the instruments cannot
see: `column-without-entasis` fires because the generator draws every shaft parallel ("no
entasis rule exists anywhere in this codebase"), which is a fact about the generator stated in
its own source, not a fact about the house.

Being a suspect is not being wrong. `six-eight-door-in-a-tall-room` at 0.638 on an 11 ft
ceiling may be a real finding about a real door; this file does not say. It says the analyst
may not send a generator to fix it, and the report has to argue each one.
"""
from __future__ import annotations

import ast
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ELEVATION = os.path.join(ROOT, "build", "elevation.py")
SUSPECTS = os.path.join(ROOT, "critique", "suspects.json")
FUNC = "_derive_measurements"
# WP-9.4: measurements folded in AFTER _derive_measurements returns are the generator's just
# the same; the first instrument read one function and a literal moved past its end left
# the count with no error. Every function that writes into the measurement dict is read.
FUNCS = ("_derive_measurements", "build_elevation")


def _mod(name, path):
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


def _tree(src=None):
    return ast.parse(src if src is not None else open(ELEVATION, encoding="utf-8").read())


def _func_node(src=None):
    tree = _tree(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == FUNC:
            return node
    raise LookupError(f"{FUNC} not found in {ELEVATION}")


def _func_nodes(src=None):
    """Every function the instrument reads -- FUNC, then the others of FUNCS present."""
    tree = _tree(src)
    found = {node.name: node for node in ast.walk(tree)
             if isinstance(node, ast.FunctionDef) and node.name in FUNCS}
    if FUNC not in found:
        raise LookupError(f"{FUNC} not found in {ELEVATION}")
    return [found[n] for n in FUNCS if n in found]


def _module_constants(src=None):
    """Module-level names bound to a numeric literal or to a dict literal of numeric
    literals (`SASH_FRAME = {"stile_in": 2.0, ...}`): a literal hidden behind a name the
    first instrument could not see. Four measurements read SASH_FRAME by subscript."""
    consts = {}
    for node in _tree(src).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name, v = node.targets[0].id, node.value
            if _is_num(v):
                consts[name] = v.value
            elif isinstance(v, ast.Dict) and v.keys and all(
                    isinstance(k, ast.Constant) and isinstance(k.value, str) and _is_num(val)
                    for k, val in zip(v.keys, v.values)):
                consts[name] = {k.value: val.value for k, val in zip(v.keys, v.values)}
    return consts


def _assignments(fn):
    """Yield (name, value_node, lineno) for every `m["name"] = <value>` and every key of a
    dict literal handed to `m.update({...})` inside the function. `m` is whatever the
    function returns a comprehension over -- read as the target of those two shapes rather
    than assumed by name, so a rename of the accumulator does not blind this."""
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            t = node.targets[0]
            if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) \
                    and isinstance(t.slice, ast.Constant) and isinstance(t.slice.value, str):
                yield t.slice.value, node.value, node.lineno
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "update" and node.args and isinstance(node.args[0], ast.Dict):
            for k, v in zip(node.args[0].keys, node.args[0].values):
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    yield k.value, v, getattr(v, "lineno", node.lineno)


def _is_num(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
        and not isinstance(node.value, bool)


def _literal_value(node, consts):
    """The numeric literal a value node states, through the shapes WP-9.4 found the first
    instrument blind to: a negated literal, a module constant by name, a constant dict by
    subscript (`SASH_FRAME["stile_in"]`), a ternary whose EVERY branch is a literal, a
    boolean fallback whose LAST operand is a literal (`x or 3`), and a bare literal inside
    `max`/`min`/`int`/`float`/`round`. Returns None where the value is a real figure of the
    house -- a computed expression -- or a mix the reader has to judge."""
    if _is_num(node):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and _is_num(node.operand):
        return -node.operand.value
    if isinstance(node, ast.Name) and isinstance(consts.get(node.id), (int, float)):
        return consts[node.id]
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
            and isinstance(consts.get(node.value.id), dict) \
            and isinstance(node.slice, ast.Constant) and node.slice.value in consts[node.value.id]:
        return consts[node.value.id][node.slice.value]
    if isinstance(node, ast.IfExp):
        a, b = _literal_value(node.body, consts), _literal_value(node.orelse, consts)
        if a is not None and b is not None:
            return a if a == b else (a, b)
        # one branch a literal: the measurement is a constant on that branch -- suspect
        return a if a is not None else b
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or) and node.values:
        return _literal_value(node.values[-1], consts)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in ("max", "min", "round", "int", "float") and node.args:
        lits = [_literal_value(a, consts) for a in node.args]
        lits = [v for v in lits if v is not None]
        if node.func.id in ("max", "min"):
            # max(1, x): the floor is a literal the generator invented; report it
            return lits[0] if lits else None
        return lits[0] if len(lits) == len(node.args) else None
    return None


def _unwrap_round(node):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "round" \
            and node.args:
        return node.args[0]
    return node


_CACHE = {}


def _cached(kind, src, compute):
    """The AST read of elevation.py is ~30 ms and why_suspect asks for it once per fault
    finding; a critique of one plan asked two dozen times. Memoised on the file's mtime when
    reading the real file, never when handed a source string."""
    if src is not None:
        return compute()
    try:
        key = (kind, os.path.getmtime(ELEVATION))
    except OSError:
        return compute()
    if key not in _CACHE:
        # evict only a STALE reading of the same kind; the two kinds share the cache and the
        # first version cleared it wholesale, so literals and ratios evicted each other on
        # every alternate call and the memo was a no-op (40 AST parses per critique, measured)
        for k in [k for k in _CACHE if k[0] == kind]:
            del _CACHE[k]
        _CACHE[key] = compute()
    return _CACHE[key]


def source_literals(src=None):
    """{name: {"value", "line"}} for every measurement stated as a bare numeric literal."""
    return _cached("literals", src, lambda: _source_literals(src))


def _source_literals(src=None):
    out = {}
    consts = _module_constants(src)
    for fn in _func_nodes(src):
        for name, v, line in _assignments(fn):
            val = _literal_value(v, consts)
            if val is not None and name not in out:
                out[name] = {"value": val, "line": line, "shape": type(v).__name__}
    return out


def literal_ratios(src=None):
    """{name: {"factor", "op", "line"}} for every measurement that is a real figure scaled or
    offset by a numeric literal -- `x * 0.6`, `x + 4.0`, `x / 3.5` -- possibly inside round().
    A literal on one side of a multiplication is the generator supplying a proportion the
    corpus never stated; the value varies with the house, the ratio does not."""
    return _cached("ratios", src, lambda: _literal_ratios(src))


# `x * 12.0` and `x / 12.0` are unit conversions, not proportions: feet to inches is not a
# number the generator invented. 0.5 and 2.0 WERE on this list and are not conversions of
# anything -- `upper_h * 0.5` is an egress rule the generator made up (WP-9.4).
UNIT_CONVERSIONS = (12, 12.0, 144, 144.0, 1, 1.0)


def _ratio_literal(v):
    """The numeric literal that scales or offsets a real figure anywhere in a BinOp tree --
    `x * 0.6`, `round(a + 4 * b, 2)`: the first instrument looked only at the top-level
    operator's two sides and missed a literal one level down."""
    v = _unwrap_round(v)
    if isinstance(v, ast.BinOp) and isinstance(v.op, (ast.Mult, ast.Div, ast.Add, ast.Sub)):
        for side in (v.right, v.left):
            if _is_num(side) and side.value not in UNIT_CONVERSIONS:
                return side.value, type(v.op).__name__
        for side in (v.left, v.right):
            found = _ratio_literal(side)
            if found:
                return found
    return None


def _literal_ratios(src=None):
    out = {}
    for fn in _func_nodes(src):
        for name, v, line in _assignments(fn):
            found = _ratio_literal(v)
            if found and name not in out:
                out[name] = {"factor": found[0], "op": found[1], "line": line}
    return out


def in_scope_plans():
    """The plan records the elevation generator will actually compose a front for -- both
    shipped plans and the reference corpus, minus the styles outside opening-proportion's
    and facade-classical's own applies_to lists (which return `applicable: False`)."""
    paths = sorted(glob.glob(os.path.join(ROOT, "plans", "*.json"))) + \
        sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json")))
    return paths


def sweep(paths=None):
    """{name: {"value", "plans"}} for every measurement whose value is identical on every
    in-scope plan that supplies it, over at least three plans. Also returns the number of
    plans that were in scope, because a sweep over one plan finds everything constant."""
    EL = _mod("elevation", ELEVATION)
    seen = {}
    n = 0
    for path in (paths or in_scope_plans()):
        plan = json.load(open(path, encoding="utf-8"))
        try:
            elev = EL.build_elevation(plan)
        except Exception as exc:                   # a plan the generator cannot front
            continue
        if "error" in elev or elev.get("applicable") is False:
            continue
        n += 1
        for k, v in (elev.get("measurements") or {}).items():
            if v is None:
                continue
            seen.setdefault(k, []).append(v)
    out = {}
    for k, vals in seen.items():
        if len(vals) >= 3 and len(set(map(repr, vals))) == 1:
            out[k] = {"value": vals[0], "plans": len(vals)}
    return out, n


_EDITORIAL = {}


def editorial():
    """The hand-authored list: (fault, expression) pairs the instruments cannot see, each with
    a basis quoting where the generator says so of itself. Memoised on the file's mtime."""
    if not os.path.exists(SUSPECTS):
        return []
    key = os.path.getmtime(SUSPECTS)
    if key not in _EDITORIAL:
        _EDITORIAL.clear()
        _EDITORIAL[key] = json.load(open(SUSPECTS, encoding="utf-8")).get("suspects", [])
    return _EDITORIAL[key]


def suspect_names():
    """Every measurement name an instrument or the editorial list marks. Cheap: AST only."""
    names = set(source_literals()) | set(literal_ratios())
    return names


def why_suspect(finding):
    """For a `fault-present` finding carrying `reads` and `expression`: the evidence that makes
    it a suspect, or None. Evidence names the instrument, the measurement, the literal and the
    line, or the editorial basis -- never just the word 'suspect'."""
    if finding.get("layer") != "fault":
        return None
    lits, ratios = source_literals(), literal_ratios()
    hits = []
    for n in finding.get("reads") or []:
        if n in lits:
            hits.append({"instrument": "source-literal", "measurement": n,
                         "value": lits[n]["value"], "line": lits[n]["line"]})
        elif n in ratios:
            hits.append({"instrument": "literal-ratio", "measurement": n,
                         "factor": ratios[n]["factor"], "op": ratios[n]["op"],
                         "line": ratios[n]["line"]})
    for e in editorial():
        if e["fault"] == finding.get("fault") and e["expression"] == finding.get("expression"):
            hits.append({"instrument": "editorial", "id": e["id"], "basis": e["basis"],
                         "why": e["why"]})
    return hits or None


if __name__ == "__main__":
    lits, ratios = source_literals(), literal_ratios()
    print(f"{len(lits)} measurement(s) stated as a literal in {FUNC}:")
    for k, v in sorted(lits.items(), key=lambda kv: kv[1]["line"]):
        print(f"  line {v['line']:5d}  {k} = {v['value']}")
    print(f"\n{len(ratios)} measurement(s) that are a figure scaled by a literal:")
    for k, v in sorted(ratios.items(), key=lambda kv: kv[1]["line"]):
        print(f"  line {v['line']:5d}  {k}  {v['op']} {v['factor']}")
    if "--sweep" in sys.argv:
        const, n = sweep()
        print(f"\n{len(const)} measurement(s) identical on every one of {n} in-scope plans:")
        for k, v in sorted(const.items()):
            tag = " (literal)" if k in lits else (" (ratio)" if k in ratios else "")
            print(f"  {k} = {v['value']}  on {v['plans']} plans{tag}")
