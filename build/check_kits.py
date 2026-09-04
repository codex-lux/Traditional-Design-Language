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
import ast, json, os, sys, glob, argparse, collections

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
    slots, groups, derives, kinds = [], {}, {}, {}
    for g in doc["groups"]:
        for s in g["slots"]:
            slots.append(s["id"])
            groups[s["id"]] = g["id"]
            kinds[s["id"]] = s.get("value_type")
            if s.get("derives_from_module"):
                derives[s["id"]] = s["derives_from_module"]
    return doc["version"], slots, groups, derives, kinds


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


def provenance_census(kits_seen):
    """The kind-of-claim census, computed rather than recounted (OQ 18).

    `docs/open-questions.md` #18 has carried a hand-counted figure for editorial parameters
    since the migration, and it went stale twice. It is a real number about how much of this
    corpus is our own convention rather than a sourced fact, and a number that matters that
    much should not depend on someone remembering to recount it. Printed by every run.

    The figure that matters is not `editorial` -- an editorial call with a note saying what it
    rests on is the corpus working as designed -- but editorial with NEITHER a source NOR a
    note: a number nobody can check and nobody said anything about."""
    lines = []
    kinds = ("measured", "derived", "editorial", "invented", "code", None)
    # `editorial-bare` shares this counter and is a SUBSET of `editorial`; summing every key
    # would count those parameters twice and inflate the denominator every percentage uses.
    total = sum(kits_seen.get(k, 0) for k in kinds)
    for k in kinds:
        n = kits_seen.get(k, 0)
        if n: lines.append("%s %d (%.1f%%)" % (k or "unlabelled", n, 100.0 * n / max(total, 1)))
    return total, lines


DIMENSIONAL_UNITS = {"in", "ft", "mm", "deg", "rise_in_12", "courses", "percent"}


def check_determined_by(errs, warns, nid, kit, ont_ids):
    """Give `determined_by` semantics, and hold the corpus to them (OQ 19).

    The field has been declarative since it was added: `porch_ceiling` says it is determined by
    the order, the entablature and the porch support, which is better than prose, and nothing
    resolved it because the schema never said what the determination MEANS. Three things it can
    mean that a checker can enforce, and each of them found something:

    1. **The determiners must be bound.** A slot that says it is whatever the order requires,
       on a kit whose `order` slot is empty, is UNJUDGED -- and it reads today as specified,
       which is the corpus's first discipline inverted. Checked against the kit file only, so
       a determiner a child inherits from a parent is a warning rather than an error.
    2. **No cycles.** Two slots that each say the other decides them decide nothing.
    3. **A determined slot may not state a dimensional number as an independent claim.** The
       schema's own note has always said it: "A portico soffit is whatever the bound order's
       entablature requires; specifying it separately either restates the order or contradicts
       it." So a number here must be `kind: derived`, or carry a `source`/`expr` tying it to
       the determiner, or say in its own note why it is genuinely independent of it. An
       unsourced editorial number sitting where a determination should be is the one case
       nobody can tell apart from a contradiction."""
    slots = kit.get("slots") or {}
    for sid, s in slots.items():
        db = s.get("determined_by") or []
        if not db: continue
        for x in db:
            if x not in ont_ids:
                errs.append("%s: %s.determined_by names '%s', which is not a slot" % (nid, sid, x))
                continue
            if x == sid:
                errs.append("%s: %s.determined_by names itself" % (nid, sid)); continue
            other = slots.get(x) or {}
            if sid in (other.get("determined_by") or []):
                errs.append("%s: %s and %s each say the other determines them, which decides "
                            "nothing (OQ 19)" % (nid, sid, x))
            if other.get("status") in (None, "empty") or other.get("binding") in (None, "open"):
                warns.append("%s: %s is determined_by %s, and %s is not bound on this kit "
                             "(status %s, binding %s) -- so this slot is UNJUDGED, not specified, "
                             "unless an ancestor binds it (OQ 19)"
                             % (nid, sid, x, x, other.get("status"), other.get("binding")))
        for pname, pv in (s.get("parameters") or {}).items():
            if not isinstance(pv, dict) or pv.get("unit") not in DIMENSIONAL_UNITS: continue
            if pv.get("kind") == "derived" or pv.get("source") or pv.get("expr"): continue
            if pv.get("note"): continue
            warns.append("%s: %s.%s is a %s number on a slot determined_by %s, with no source, "
                         "no expression and no note saying why it is independent of the "
                         "determiner -- restatement and contradiction look identical here (OQ 19)"
                         % (nid, sid, pname, pv.get("kind"), ", ".join(db)))


RULE_KINDS = {"topology", "axis", "sequence", "daylight", "element-placement",
              "hierarchy", "orientation", "other"}
RULE_EFFECTS = {"adds", "restricts", "suppresses"}
ADJ_KEYS = {"must_adjoin", "should_adjoin", "must_not_adjoin"}


def check_rule_blocks(errs, warns, nid, kit, rule_slots, rooms):
    """The typed `rules` array on a rule-valued slot (OQ 15).

    Three things nothing else can catch: a `rules` block on a slot the ontology does not type as
    a rule (which means someone has put a rule statement where a parameter belongs); a
    `suppresses` effect with no machine-readable target, which is the one case that MUST be
    readable because build/plan_check.py acts on it and a suppression that exists only as prose
    is a rule the validator goes on enforcing while the kit says it should not; and a suppression
    naming a room or a rule that does not exist, which would switch nothing off and say nothing
    about it."""
    for sid, slot in (kit.get("slots") or {}).items():
        rules = slot.get("rules")
        if not rules: continue
        if sid not in rule_slots:
            warns.append("%s: %s carries a `rules` block but the ontology types it as '%s', not "
                         "'rule' -- a rule statement in a slot that holds values"
                         % (nid, sid, rule_slots.get(sid, "?")))
        for i, r in enumerate(rules):
            where = "%s: %s.rules[%d]" % (nid, sid, i)
            if r.get("kind") not in RULE_KINDS:
                errs.append("%s: kind '%s' is not one of %s" % (where, r.get("kind"), sorted(RULE_KINDS)))
            if r.get("effect") not in RULE_EFFECTS:
                errs.append("%s: effect '%s' is not one of %s" % (where, r.get("effect"), sorted(RULE_EFFECTS)))
            sup = r.get("suppresses")
            if r.get("effect") == "suppresses" and not sup:
                errs.append("%s: effect is 'suppresses' with no `suppresses` target. A suppression "
                            "that exists only as prose is a rule the validator goes on enforcing "
                            "while this kit says it should not (OQ 15)." % where)
            if sup and r.get("effect") != "suppresses":
                errs.append("%s: carries a `suppresses` target but its effect is '%s'" % (where, r.get("effect")))
            if not sup: continue
            room = rooms.get(sup.get("room"))
            if room is None:
                errs.append("%s: suppresses room '%s', which is not in rooms/" % (where, sup.get("room")))
                continue
            key = sup.get("key")
            if key not in ADJ_KEYS:
                errs.append("%s: suppresses key '%s' is not an adjacency list" % (where, key)); continue
            targets = {x.get("room") for x in (room.get("adjacency", {}) or {}).get(key, [])}
            if sup.get("target") not in targets:
                errs.append("%s: suppresses %s.%s -> '%s', and that room states no such rule "
                            "(it states: %s). Suppressing a rule that is not there switches "
                            "nothing off and says nothing about it."
                            % (where, sup.get("room"), key, sup.get("target"),
                               ", ".join(sorted(targets)) or "none"))


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


# A baked snapshot's context is what `computed_at` STATES, and the three bindings it states are
# not the five the expressions read. `span` and `room_width` never appear there, so a snapshot
# whose expression reads one of them agrees or disagrees according to a number nobody wrote down
# -- REF_CTX's `span: 540.0` happens to be the value they were baked at, and that is a
# reconstruction, not a record. Those are UNJUDGED and ratcheted; the rest are judged.
BAKED_CONTEXT_FROM_PACK = ("module", "part", "column_height")
BAKED_UNJUDGED_CEILING = 8       # may only go DOWN -- close one by recording the binding it reads
BAKED_JUDGED_FLOOR = 135         # may only go UP -- catches the instrument going blind


def check_baked_snapshots(errs, unjudged, nid, kit, stats):
    """A `kind: derived` parameter carries an `expr` AND the value that expr produced. Nothing
    re-derived it (`oq/a-baked-pack-value-is-a-second-delivery-path`).

    That question was raised from scope refusals and its sharpest instance arrived in ordinary
    work: WP-9.6 moved `storey-graduation`'s riser divisor on Lucas's ruling, and the baked copy in
    `georgian-colonial-american` kept the old VALUE beside the new EXPRESSION -- one object stating
    a riser count its own expression no longer produces. Both instruments ran with the defect in
    place and neither moved. (The divisor itself is deliberately not repeated here:
    `tests/test_storeys.py` refuses it in any file but `build/storeys.py`, and a docstring
    quoting it would go stale the next time it moves.)
    THIS FUNCTION IS THE ONE THAT WOULD HAVE: `check_derived_module_family` above holds the
    context keys consistent across a slot family and explicitly `continue`s on `"value"`, which
    is the one key that had gone wrong.

    A snapshot is judged by re-deriving its expression AT THE CONTEXT IT RECORDS. It is UNJUDGED
    -- never passed -- where the expression reads a binding `computed_at` does not carry, because
    then any verdict is really a verdict about `REF_CTX`. `module`, `part` and `column_height`
    are not in `computed_at` and do not need to be: they are functions of the pack the parameter
    names in `source`, so they are recoverable rather than assumed."""
    for sid, sv in (kit.get("slots") or {}).items():
        for pname, pv in (sv.get("parameters") or {}).items():
            if not isinstance(pv, dict) or "expr" not in pv:
                continue
            ca = pv.get("computed_at")
            if not isinstance(ca, dict) or "value" not in ca:
                continue
            where = "%s.%s.%s" % (nid, sid, pname)
            stored = ca["value"]
            src = pv.get("pack") or pv.get("source")
            if not isinstance(stored, (int, float)) or isinstance(stored, bool):
                stats["baked_unjudged"] += 1
                unjudged.append("%s: stored value is not a number" % where)
                continue
            # `<name>_in` is the binding `<name>`, in inches, which is what the bindings are in.
            # Read generally rather than from a list of three, so recording `span_in` on a
            # snapshot closes its gap without touching this function.
            ctx = {k[:-3]: v for k, v in ca.items()
                   if k.endswith("_in") and isinstance(v, (int, float))}
            try:
                tree = ast.parse(pv["expr"], mode="eval")
            except SyntaxError as e:
                errs.append("%s: expr does not parse: %s" % (where, e))
                continue
            reads = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} - set(pe._ALLOWED)
            gap = reads - set(ctx) - set(BAKED_CONTEXT_FROM_PACK)
            if gap:
                stats["baked_unjudged"] += 1
                unjudged.append("%s: reads %s, which `computed_at` does not record"
                                % (where, ", ".join(sorted(gap))))
                continue
            try:
                pk = pe.resolve(src)
                mod = (ORDER_MODULE if pk.get("kind") == "order-system"
                       else (pk["module"].get("default_size_in") or 6.0))
                env = dict(pe.DEFAULT_BINDINGS)
                env.update(ctx)
                env["module"] = mod
                env["part"] = mod / pk["module"]["parts"]
                col = pk.get("column", {})
                env["column_height"] = (col.get("height_modules", 0) * mod
                                        if col.get("height_modules") else 0)
                got = pe.evaluate_expr(pv["expr"], env)
            except Exception as e:
                stats["baked_unjudged"] += 1
                unjudged.append("%s: %s" % (where, e))
                continue
            stats["baked_judged"] += 1
            # The snapshot is stored rounded (resolve_kit writes `round(val, 3)`), so the
            # tolerance is the rounding, not a fudge for a value that has really moved.
            if abs(got - stored) > max(0.01, abs(stored) * 0.001):
                errs.append("%s: the snapshot says %s and its own expression `%s` gives %s at the "
                            "context it records. A derived value is a cached computation with no "
                            "cache invalidation; this one is stale."
                            % (where, stored, pv["expr"], round(got, 4)))


def check_slot_fields(errs, warns, nid, kit, ont_fields):
    """A slot may DECLARE fields in elements/slots.json (`fields[]`, with `required` and, for an
    enum, the permitted values under `examples`). `expressed_frame` is the only slot that does, and
    OQ 47 added it precisely because `member_status` -- structural / structural-and-expressed /
    applied / none -- is the field the slot exists for. NOTHING READ THAT DECLARATION: an audit on
    25 Aug 2026 found that a kit could take a position on the slot without stating the status, and
    that `"aplied"` would validate, because the kit schema types a variant id as a free string. A
    required field that nobody enforces is a comment.

    The categorical is carried by the VARIANT ID -- `{"id": "applied", ...}` -- because a variant
    can be FORBIDDEN and a parameter cannot. So the enum is checked against variant ids, which is
    where the data actually puts it, not against a parameter named after the field.

    `binding: open` means the style has not taken a position yet and is not required to: 145 of the
    159 kits are seeded and unbound. The requirement bites once a kit says `specified` or
    `forbidden`, which is the point at which it IS making a claim.
    """
    for sid, decl in ont_fields.items():
        rec = (kit.get("slots") or {}).get(sid)
        if not isinstance(rec, dict):
            continue
        binding = rec.get("binding")
        variants = [v for v in (rec.get("variants") or []) if isinstance(v, dict)]
        for fld in decl:
            allowed = fld.get("examples") if fld.get("value_type") == "enum" else None
            if not allowed:
                continue
            ids = [v.get("id") for v in variants]
            if fld.get("required") and binding in ("specified", "forbidden") and not ids:
                errs.append("%s: slot '%s' is %s but states no '%s' -- elements/slots.json marks "
                            "it required, and it is the field the slot exists for"
                            % (nid, sid, binding, fld["id"]))
            for got in ids:
                if got not in allowed:
                    errs.append("%s: slot '%s' variant id %r is not a permitted '%s' -- "
                                "elements/slots.json allows %s"
                                % (nid, sid, got, fld["id"], allowed))


def main():
    ap = argparse.ArgumentParser(description="Validate the kit corpus")
    ap.add_argument("style", nargs="?", help="check one kit only")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    ont_version, ont_slots, ont_groups, ont_derives, ont_kinds = ontology()
    ont_fields = {}
    for _g in json.load(open(os.path.join(ROOT, "elements", "slots.json")))["groups"]:
        for _sl in _g["slots"]:
            if _sl.get("fields"):
                ont_fields[_sl["id"]] = _sl["fields"]
    rule_slots = {k: v for k, v in ont_kinds.items() if v == "rule"}
    rooms = {}
    for rp in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))):
        r = json.load(open(rp)); rooms[r["id"]] = r
    ont_set = set(ont_slots)
    g = graph()
    schema_path = os.path.join(ROOT, "schema", "kit.schema.json")
    schema = json.load(open(schema_path))

    files = ([os.path.join(ROOT, "kits", "%s.kit.json" % a.style)] if a.style
             else sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))))

    errs, warns = [], []
    stats = collections.Counter()
    baked_unjudged = []
    census = collections.Counter()
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
        check_rule_blocks(errs, warns, base, kit, rule_slots, rooms)
        check_determined_by(errs, warns, base, kit, ont_set)
        check_slot_fields(errs, warns, base, kit, ont_fields)
        check_baked_snapshots(errs, baked_unjudged, base, kit, stats)
        for _s in (kit.get("slots") or {}).values():
            for _pv in (_s.get("parameters") or {}).values():
                if not isinstance(_pv, dict): continue
                census[_pv.get("kind")] += 1
                if _pv.get("kind") == "editorial" and not _pv.get("source") and not _pv.get("note"):
                    census["editorial-bare"] += 1
                # WP-11.1. The census had counted the OTHER kind for a year. `measured` is "from
                # surviving fabric or a documented standard" (the schema's words), and 672 of
                # 1,161 carried no `source`; 542 sat on a slot with no `sources[]` either. Both
                # are SUBSETS of `measured` and stay out of the denominator, as editorial-bare does.
                if _pv.get("kind") == "measured" and not _pv.get("source"):
                    census["measured-bare"] += 1
                    if not _s.get("sources"):
                        census["measured-bare-slot"] += 1
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
    total, bits = provenance_census(census)
    print("\nparameters by provenance (%d in all): %s" % (total, ", ".join(bits)))
    print("  editorial with NEITHER a source NOR a note: %d (%.1f%% of all parameters). "
          "That is the figure OQ 18 is about -- a number nobody can check and nobody said "
          "anything about. An editorial call WITH a note is the corpus working as designed."
          % (census["editorial-bare"], 100.0 * census["editorial-bare"] / max(total, 1)))
    print("  measured with NO source on the parameter: %d (%.1f%%); %d of those on a slot with no "
          "`sources[]` either. That is the figure WP-11.1 is about -- a number claiming to have been "
          "measured that nothing on the record says where. build/check_research.py ratchets it and "
          "splits it by whether a generator reads the slot."
          % (census["measured-bare"], 100.0 * census["measured-bare"] / max(total, 1),
             census["measured-bare-slot"]))

    # THE BAKED SNAPSHOTS, AND THE UNJUDGED ONES REPORTED AS UNJUDGED. A snapshot whose
    # expression reads a binding `computed_at` does not carry is not passing this check; it is
    # outside it, and saying so is the whole of `oq/a-baked-pack-value-is-a-second-delivery-path`'s
    # complaint that the count of stale values here was "unknown, not zero".
    print("\nbaked derived snapshots: %d re-derived at the context they record and AGREEING, "
          "%d COULD NOT BE JUDGED" % (stats["baked_judged"], stats["baked_unjudged"]))
    for x in baked_unjudged:
        print("  ? " + x)
    # A CORPUS-WIDE CLAIM MAY NOT BE ENFORCED ON A FILTERED RUN, and shipping it that way made
    # `check_kits.py <one-style>` fail on every node in the corpus. WP-8.8 added these two bounds
    # and asserted them unconditionally; a single-kit run sees ~10 snapshots against a floor of
    # 135 and errors, which is the floor working correctly on a question nobody asked it. Caught
    # by `test_kit_cascade.py`'s dangling-replace test, whose CLEANUP re-runs one kit and asserts
    # the corpus is clean again -- so it was found by a test about something else, on the full
    # suite, after the targeted suites were green. The same shape as the unsorted glob in WP-8.7.
    if a.style:
        print("  (both bounds are corpus-wide and are NOT judged on a single-kit run)")
    else:
        if stats["baked_unjudged"] > BAKED_UNJUDGED_CEILING:
            errs.append("baked snapshots that cannot be judged from their own record: %d against "
                        "a ceiling of %d. Record the binding the expression reads in "
                        "`computed_at` rather than raising this."
                        % (stats["baked_unjudged"], BAKED_UNJUDGED_CEILING))
        if stats["baked_judged"] < BAKED_JUDGED_FLOOR:
            errs.append("only %d baked snapshots were judged against a floor of %d. This number "
                        "falls when the instrument goes blind, not only when the corpus shrinks "
                        "-- check that before re-pinning it."
                        % (stats["baked_judged"], BAKED_JUDGED_FLOOR))

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
