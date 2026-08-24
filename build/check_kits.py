#!/usr/bin/env python3
"""Validate the kit corpus against schema/kit.schema.json (0.2.0).

Beyond JSON Schema conformance this checks the four things the schema cannot express and
that authoring the Georgian kit showed were easy to get wrong:

  * every slot id in a kit exists in the element ontology, and every ontology slot is
    present in the kit — a kit that has drifted from the ontology fails silently otherwise
  * every `extends` binding actually has an ancestor in the cascade that specifies the
    slot it claims to extend. An extends with nothing to merge into is a dangling diff
    and resolves to the same thing as `open`, which is not what the author meant
  * every dimensional parameter carries a unit. Units surviving only in key names was
    the single most fragile thing about 0.1.0
  * every parameter states exactly one of value / range / set / expr, and every expr
    actually evaluates in the proportion engine

and it reports, rather than fails, on the things that should stay visible: slots marked
`invented`, slots marked `judgment`, parameters of kind `invented` or `editorial`, and
pack bindings marked out of calibration.

    python3 build/check_kits.py                # whole corpus
    python3 build/check_kits.py tidewater-georgian --verbose
"""
import json, os, sys, glob, argparse, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import proportion_engine as pe

try:
    import jsonschema
except ImportError:
    jsonschema = None

DIMENSIONAL = {"in", "ft", "mm", "deg", "rise_in_12", "courses"}
VALUE_KEYS = ("value", "range", "set", "expr")
STOPS = ("specified", "forbidden", "extends")

REF_CTX = {"ceiling_height": 108.0, "storey_height": 120.0, "opening_height": 80.0, "opening_width": 36.0,
           "span": 540.0, "room_width": 192.0, "room_length": 288.0, "wall_thickness": 13.5}
ORDER_MODULE = 5.0


def ontology():
    doc = json.load(open(os.path.join(ROOT, "elements", "slots.json")))
    slots, groups, derives = [], {}, {}
    for g in doc["groups"]:
        for s in g["slots"]:
            slots.append(s["id"])
            groups[s["id"]] = g["id"]
            if s.get("derives_from_module"):
                derives[s["id"]] = s["derives_from_module"]
    return doc["version"], slots, groups, derives


def graph():
    p = os.path.join(ROOT, "dist", "taxonomy.json")
    return json.load(open(p)) if os.path.exists(p) else None


def eval_expr(pack_id, expr):
    pk = pe.resolve(pack_id)
    mod = ORDER_MODULE if pk.get("kind") == "order-system" else (pk["module"].get("default_size_in") or 6.0)
    env = dict(pe.DEFAULT_BINDINGS)
    env.update(REF_CTX)
    env["module"] = mod
    env["part"] = mod / pk["module"]["parts"]
    col = pk.get("column", {})
    env["column_height"] = col.get("height_modules", 0) * mod if col.get("height_modules") else 0
    return pe.evaluate_expr(expr, env)


def check_derived_module_family(errs, nid, kit, derives):
    """OQ 13: a chair rail's module must derive from the same run as the exterior cornice.

    `derives_from_module` has existed since WP-1.3 and validate.py already checks that the
    reference resolves. What it did not check is the thing the ruling was actually about: that
    the members of a family were computed against the SAME context. A cornice worked out at a
    120 in storey and a chair rail worked out at a 96 in one are not one entablature at two
    scales, they are two entablatures -- and the whole point of the cross-reference is that they
    are one object.

    Compares only keys the two records share, and requires those to agree. A member that records
    a partial context (a chair rail derived from the ceiling height alone) is not in conflict
    with one that records more; a member that records the SAME key with a different value is."""
    fam = {}
    for sid in (kit.get("slots") or {}):
        base = derives.get(sid)
        if base:
            fam.setdefault(base, []).append(sid)
    for base, members in fam.items():
        seen = {}                       # context key -> (value, where it was first seen)
        for sid in sorted(members) + ([base] if base in (kit.get("slots") or {}) else []):
            sl = (kit["slots"].get(sid) or {})
            for pname, pv in (sl.get("parameters") or {}).items():
                ca = pv.get("computed_at")
                if not isinstance(ca, dict):
                    continue
                for ck, cv in ca.items():
                    if ck == "value":
                        continue
                    if ck in seen and seen[ck][0] != cv:
                        errs.append(
                            "%s: %s.%s computes against %s=%s but %s used %s=%s; the %s family "
                            "must derive from one run (OQ 13)"
                            % (nid, sid, pname, ck, cv, seen[ck][1], ck, seen[ck][0], base))
                    else:
                        seen.setdefault(ck, (cv, f"{sid}.{pname}"))


def main():
    ap = argparse.ArgumentParser(description="Validate the kit corpus")
    ap.add_argument("style", nargs="?", help="check one kit only")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    ont_version, ont_slots, ont_groups, ont_derives = ontology()
    ont_set = set(ont_slots)
    g = graph()
    schema_path = os.path.join(ROOT, "schema", "kit.schema.json")
    schema = json.load(open(schema_path))

    files = ([os.path.join(ROOT, "kits", "%s.kit.json" % a.style)] if a.style
             else sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))))

    errs, warns = [], []
    stats = collections.Counter()
    invented, judgment, out_of_cal, populated = [], [], [], []

    for f in files:
        base = os.path.basename(f)[: -len(".kit.json")]
        try:
            kit = json.load(open(f))
        except Exception as e:
            errs.append("%s: UNPARSEABLE JSON: %s" % (base, e))
            continue

        if jsonschema:
            try:
                jsonschema.validate(kit, schema)
            except jsonschema.ValidationError as e:
                errs.append("%s: SCHEMA %s: %s" % (base, "/".join(str(p) for p in e.absolute_path), e.message))
                continue
        if kit.get("style") != base:
            errs.append("%s: style '%s' does not match filename" % (base, kit.get("style")))
        if kit.get("ontology_version") != ont_version:
            errs.append("%s: ontology_version %s, ontology is %s" % (base, kit.get("ontology_version"), ont_version))
        if kit.get("kit_version") != schema.get("version"):
            errs.append("%s: kit_version %s, schema is %s" % (base, kit.get("kit_version"), schema.get("version")))

        slots = kit.get("slots", {})
        check_derived_module_family(errs, base, kit, ont_derives)
        unknown = set(slots) - ont_set
        missing = ont_set - set(slots)
        if unknown:
            errs.append("%s: slot ids not in the ontology: %s" % (base, ", ".join(sorted(unknown))))
        if missing:
            errs.append("%s: ontology slots absent from the kit: %s" % (base, ", ".join(sorted(missing))))

        # cascade context for extends
        chain = []
        if g and base in g["nodes"]:
            chain = g["nodes"][base].get("_cascade", [])
        anc_specifies, anc_variants = {}, {}
        for anc in chain:
            ap_ = os.path.join(ROOT, "kits", "%s.kit.json" % anc)
            if not os.path.exists(ap_):
                continue
            try:
                ak = json.load(open(ap_)).get("slots", {})
            except Exception:
                continue
            for sid, sv in ak.items():
                if sv.get("binding") in ("specified", "forbidden") and sid not in anc_specifies:
                    anc_specifies[sid] = anc
                    anc_variants[sid] = {v["id"] for v in sv.get("variants", [])}

        n_spec = 0
        for sid, sv in slots.items():
            if sid not in ont_set:
                continue
            if sv.get("group") and sv["group"] != ont_groups[sid]:
                errs.append("%s.%s: group '%s', ontology says '%s'" % (base, sid, sv["group"], ont_groups[sid]))
            b = sv.get("binding", "open")
            stats[b] += 1
            if b in STOPS:
                n_spec += 1

            if b == "extends":
                if not chain:
                    errs.append("%s.%s: binding 'extends' but the node has no cascade chain" % (base, sid))
                elif sid not in anc_specifies:
                    errs.append("%s.%s: binding 'extends' but no ancestor in the cascade specifies it "
                                "— a dangling diff, which resolves the same as 'open'" % (base, sid))
                else:
                    ops = [v for v in sv.get("variants", []) if not v.get("op")]
                    if ops:
                        warns.append("%s.%s: extends binding has %d variant record(s) without an `op`; "
                                     "they will default to add" % (base, sid, len(ops)))
                    # An op that names an id the inherited list does not contain silently
                    # becomes an `add`, which is how a one-character typo turns a
                    # prohibition into a duplicate permitted variant. Found exactly that
                    # way on chimney: the parent had `paired-and-joined-by-curtain` and
                    # the child replaced `paired-and-joined-by-arched-curtain`.
                    have = anc_variants.get(sid, set())
                    for vr in sv.get("variants", []):
                        if vr.get("op") in ("remove", "replace") and vr["id"] not in have:
                            errs.append("%s.%s: variant op '%s' targets '%s', which no ancestor "
                                        "defines — it will silently become an `add`"
                                        % (base, sid, vr["op"], vr["id"]))

            for vr in sv.get("variants", []):
                if vr.get("op") and b != "extends":
                    warns.append("%s.%s: variant '%s' carries op '%s' on a '%s' binding, where it has no effect"
                                 % (base, sid, vr["id"], vr["op"], b))
                if vr.get("status") == "forbidden" and not vr.get("note"):
                    warns.append("%s.%s: forbidden variant '%s' has no note saying why" % (base, sid, vr["id"]))

            pkeys = list((sv.get("parameters") or {}).keys())
            for pk_ in pkeys:
                for suf in ("_in", "_ft", "_deg", "_ratio", "_count"):
                    if pk_ + suf in pkeys:
                        warns.append("%s.%s: parameters '%s' and '%s%s' look like the same "
                                     "quantity under two names" % (base, sid, pk_, pk_, suf))
            for pk_, pv in (sv.get("parameters") or {}).items():
                present = [k for k in VALUE_KEYS if k in pv]
                if len(present) != 1:
                    errs.append("%s.%s.%s: must state exactly one of value/range/set/expr, has %d"
                                % (base, sid, pk_, len(present)))
                    continue
                unit = pv.get("unit")
                if unit is None:
                    errs.append("%s.%s.%s: no unit" % (base, sid, pk_))
                elif unit in DIMENSIONAL and "value" in pv and isinstance(pv["value"], str):
                    pass  # e.g. "8:12" as rise_in_12
                if "expr" in pv:
                    if unit is None or unit == "none":
                        errs.append("%s.%s.%s: derived parameter with unit '%s'" % (base, sid, pk_, unit))
                    # `pack` is a pack id; `source` is free text and may be a book. Either
                    # satisfies the rule, which is that a derived value must say where it came from.
                    src = pv.get("pack") or pv.get("source")
                    if not src:
                        errs.append("%s.%s.%s: expr with no source pack or source" % (base, sid, pk_))
                    else:
                        try:
                            eval_expr(src, pv["expr"])
                        except Exception as e:
                            errs.append("%s.%s.%s: expr does not evaluate against pack '%s': %s"
                                        % (base, sid, pk_, src, e))
                if pv.get("kind") == "invented":
                    stats["param_invented"] += 1
                if pv.get("kind") == "editorial":
                    stats["param_editorial"] += 1

            for pb in sv.get("packs", []) or []:
                try:
                    pe.resolve(pb["pack"])
                except Exception as e:
                    errs.append("%s.%s: pack '%s' does not resolve: %s" % (base, sid, pb["pack"], e))
                    continue
                if pb.get("expression"):
                    try:
                        eval_expr(pb["pack"], pb["expression"])
                    except Exception as e:
                        errs.append("%s.%s: pack expression does not evaluate: %s" % (base, sid, e))
                if pb.get("in_calibration") is False:
                    out_of_cal.append("%s.%s [%s]" % (base, sid, pb["pack"]))
            prec = [pb.get("precedence") for pb in sv.get("packs", []) or []]
            if prec and any(p is None for p in prec) and len(prec) > 1:
                warns.append("%s.%s: %d packs bound and at least one has no precedence" % (base, sid, len(prec)))

            for cc in sv.get("code_conflict", []) or []:
                if not cc.get("code_ref"):
                    warns.append("%s.%s: code_conflict with no code_ref" % (base, sid))

            if sv.get("invented"):
                invented.append("%s.%s" % (base, sid))
            if sv.get("judgment"):
                judgment.append("%s.%s" % (base, sid))
            if sv.get("status") in ("drafted", "reviewed") and b == "open" and not sv.get("note"):
                warns.append("%s.%s: status %s but binding open and no note explaining why"
                             % (base, sid, sv.get("status")))

        if n_spec:
            populated.append((base, n_spec))

    print("kits: %d   ontology %s   schema %s" % (len(files), ont_version, schema.get("version")))
    if not jsonschema:
        print("  ! jsonschema not installed — structural validation skipped")
    print("populated: %d" % len(populated))
    for b, n in sorted(populated, key=lambda x: -x[1]):
        print("    %-34s %d bindings" % (b, n))
    print("bindings across the corpus: " + ", ".join(
        "%s %d" % (k, v) for k, v in sorted(stats.items()) if not k.startswith("param_")))

    if invented:
        print("\nINVENTED — authored rather than retrieved, keep visible (%d)" % len(invented))
        for x in invented:
            print("  ! %s" % x)
    if judgment:
        print("\nJUDGMENT — the sources do not determine these (%d)" % len(judgment))
        print("  " + ", ".join(judgment))
    if out_of_cal:
        print("\nPACK BINDINGS OUT OF CALIBRATION (%d)" % len(out_of_cal))
        for x in out_of_cal:
            print("  ! %s" % x)
    print("\nparameters by provenance: invented %d, editorial %d"
          % (stats["param_invented"], stats["param_editorial"]))

    if warns:
        print("\n%d WARNINGS" % len(warns))
        for w in (warns if a.verbose else warns[:25]):
            print("  ! " + w)
        if not a.verbose and len(warns) > 25:
            print("  ... %d more (--verbose)" % (len(warns) - 25))
    if errs:
        print("\n%d ERRORS" % len(errs))
        for e in errs[:60]:
            print("  x " + e)
        sys.exit(1)
    print("\nOK — kits conform to %s, slot ids resolve, extends bindings have ancestors, "
          "every dimensional parameter carries a unit." % schema.get("version"))


if __name__ == "__main__":
    main()
