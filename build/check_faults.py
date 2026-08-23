#!/usr/bin/env python3
"""Validate the fault corpus.

Checks every file in faults/ against schema/fault.schema.json, then runs the
structural checks the schema cannot express:

  * every id in `slots` exists in elements/slots.json
  * every style id in `applies_to` and in `exceptions[].style` resolves to a
    file in styles/, or is one of the permitted non-style tokens
  * every cross-reference in `confused_with[].fault` resolves to another fault
  * the filename matches the record's own id

Then reports counts by severity, frequency, category and slot group, plus slot
coverage, so it is obvious which parts of the ontology have no faults yet.

Usage:  python3 build/check_faults.py [--quiet]
Exit code 1 if anything failed.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAULTS = os.path.join(ROOT, "faults")
SCHEMA = os.path.join(ROOT, "schema", "fault.schema.json")
SLOTS = os.path.join(ROOT, "elements", "slots.json")
STYLES = os.path.join(ROOT, "styles")

# Tokens permitted in applies_to / exceptions[].style that are not style ids.
# The schema calls these "a construction or region token".
UNIVERSAL = "universal"
TOKEN_PREFIXES = ("construction:", "region:", "climate:", "period:", "type:")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def slot_index():
    """slot id -> group id, from elements/slots.json."""
    data = load(SLOTS)
    out = {}
    for group in data["groups"]:
        for slot in group["slots"]:
            out[slot["id"]] = group["id"]
    return out


def style_ids():
    return {
        f[:-5]
        for f in os.listdir(STYLES)
        if f.endswith(".json")
    }


def style_ok(token, styles):
    if token == UNIVERSAL:
        return True
    if token in styles:
        return True
    return token.startswith(TOKEN_PREFIXES)


def main(argv):
    quiet = "--quiet" in argv
    if not os.path.isdir(FAULTS):
        print("no faults/ directory")
        return 1

    files = sorted(f for f in os.listdir(FAULTS) if f.endswith(".json"))
    if not files:
        print("faults/ is empty")
        return 1

    schema = load(SCHEMA)
    slots = slot_index()
    styles = style_ids()

    try:
        from jsonschema import Draft202012Validator
        validator = Draft202012Validator(schema)
    except ImportError:
        validator = None
        print("WARNING: jsonschema not installed; schema validation skipped")

    records = {}
    errors = []
    warnings = []

    for name in files:
        path = os.path.join(FAULTS, name)
        try:
            rec = load(path)
        except json.JSONDecodeError as exc:
            errors.append("%s: not valid JSON: %s" % (name, exc))
            continue

        if validator is not None:
            for err in sorted(validator.iter_errors(rec), key=lambda e: list(e.path)):
                loc = "/".join(str(p) for p in err.path) or "(root)"
                errors.append("%s: schema at %s: %s" % (name, loc, err.message))

        fid = rec.get("id")
        if not isinstance(fid, str):
            errors.append("%s: missing or non-string id" % name)
            continue
        if name != fid + ".json":
            errors.append("%s: filename does not match id %r" % (name, fid))
        if fid in records:
            errors.append("%s: duplicate id %r" % (name, fid))
        records[fid] = rec

    for fid, rec in sorted(records.items()):
        for sid in rec.get("slots", []):
            if sid not in slots:
                errors.append("%s: slot %r not in elements/slots.json" % (fid, sid))

        for token in rec.get("applies_to", []):
            if not style_ok(token, styles):
                errors.append("%s: applies_to %r is not a style id or a known token" % (fid, token))

        for exc in rec.get("exceptions", []):
            token = exc.get("style", "")
            if not style_ok(token, styles):
                errors.append("%s: exceptions[].style %r does not resolve" % (fid, token))
            if token == UNIVERSAL:
                errors.append("%s: exceptions[].style may not be 'universal'" % fid)
            if not exc.get("bounds"):
                warnings.append("%s: exception on %r has no bounds — exceptions without "
                                "bounds become loopholes" % (fid, token))

        if not rec.get("exceptions"):
            warnings.append("%s: no exceptions[] — confirm this is genuinely universal" % fid)

        for ref in rec.get("confused_with", []):
            target = ref.get("fault")
            if target not in records:
                errors.append("%s: confused_with references unknown fault %r" % (fid, target))
            elif target == fid:
                errors.append("%s: confused_with references itself" % fid)

        # 0.2.0 cross-references between faults. Same rule as confused_with:
        # a dangling pointer is an error, a self-reference is an error.
        for field in ("co_occurs_with", "alternative_to"):
            for target in rec.get(field, []):
                if target not in records:
                    errors.append("%s: %s references unknown fault %r" % (fid, field, target))
                elif target == fid:
                    errors.append("%s: %s references itself" % (fid, field))

        # 0.2.0 style-keyed fields resolve against styles/ like applies_to does.
        for entry in rec.get("severity_by_style", []):
            if not style_ok(entry.get("style", ""), styles):
                errors.append("%s: severity_by_style[].style %r does not resolve"
                              % (fid, entry.get("style")))
        for entry in rec.get("inverted_by", []):
            if not style_ok(entry.get("style", ""), styles):
                errors.append("%s: inverted_by[].style %r does not resolve"
                              % (fid, entry.get("style")))

        # applies_when.slots inside an exception must name real slots.
        for exc in rec.get("exceptions", []):
            aw = exc.get("applies_when") or {}
            for sid in aw.get("slots", []):
                if sid not in slots:
                    errors.append("%s: exceptions[].applies_when.slots %r not in "
                                  "elements/slots.json" % (fid, sid))

        # A test is only useful if it is complete enough to evaluate.
        def check_test(t, where):
            if not t:
                return
            missing = [k for k in ("expression", "threshold", "direction") if t.get(k) is None]
            if missing:
                warnings.append("%s: %s missing %s — not evaluable"
                                % (fid, where, ", ".join(missing)))
            if t.get("direction") == "between" and t.get("upper") is None:
                errors.append("%s: %s direction is 'between' with no upper bound" % (fid, where))
            if not t.get("measurable_from"):
                warnings.append("%s: %s has no measurable_from — say whether a photograph "
                                "can evaluate it" % (fid, where))

        check_test(rec.get("test"), "test")
        for exc in rec.get("exceptions", []):
            if exc.get("bounds_test"):
                check_test(exc["bounds_test"], "exceptions[%s].bounds_test" % exc.get("style"))

        if not rec.get("test"):
            warnings.append("%s: no test[] — add one wherever a ratio exists" % fid)

        fixes = rec.get("fixes") or {}
        for tier in ("right", "cheap", "dishonest"):
            if not fixes.get(tier):
                warnings.append("%s: fixes.%s missing" % (fid, tier))

        cause = rec.get("cause") or {}
        if not cause.get("cost_saved"):
            warnings.append("%s: cause.cost_saved missing" % fid)
        if cause.get("driver") == "ignorance":
            warnings.append("%s: cause.driver is 'ignorance' — this should be rare" % fid)

    # ---- report -------------------------------------------------------
    print("faults: %d files, %d records" % (len(files), len(records)))

    def tally(label, key):
        counts = Counter(rec.get(key) or "(unset)" for rec in records.values())
        print("\n%s" % label)
        for value, n in counts.most_common():
            print("  %-14s %4d" % (value, n))

    tally("by severity", "severity")
    tally("by frequency", "frequency")
    tally("by category", "category")

    by_group = Counter()
    by_slot = Counter()
    for rec in records.values():
        seen = set()
        for sid in rec.get("slots", []):
            by_slot[sid] += 1
            g = slots.get(sid)
            if g and g not in seen:
                by_group[g] += 1
                seen.add(g)
    print("\nby slot group")
    for g, n in by_group.most_common():
        print("  %-22s %4d" % (g, n))

    n = len(records)
    print("\n0.2.0 field uptake")
    for field in ("test", "severity_by_style", "inverted_by", "co_occurs_with",
                  "alternative_to", "severity_trajectory"):
        k = sum(1 for r in records.values() if r.get(field))
        print("  %-22s %4d of %d" % (field, k, n))
    k = sum(1 for r in records.values()
            if any(e.get("bounds_test") for e in r.get("exceptions", [])))
    print("  %-22s %4d of %d" % ("exceptions.bounds_test", k, n))
    k = sum(1 for r in records.values() if (r.get("cause") or {}).get("cost_negative"))
    print("  %-22s %4d of %d" % ("cause.cost_negative", k, n))
    k = sum(1 for r in records.values()
            if any(rv.get("kind") == "code" for rv in r.get("rule_violated", [])))
    print("  %-22s %4d of %d" % ("rule_violated kind=code", k, n))

    measurable = Counter((r.get("test") or {}).get("measurable_from") or "(no test)"
                         for r in records.values())
    print("\ntest.measurable_from")
    for value, k in measurable.most_common():
        print("  %-14s %4d" % (value, k))

    uncovered = [s for s in slots if s not in by_slot]
    print("\nslot coverage: %d of %d slots carry at least one fault" % (len(by_slot), len(slots)))
    if uncovered and not quiet:
        print("  uncovered: %s" % ", ".join(sorted(uncovered)))

    if warnings and not quiet:
        print("\nWARNINGS (%d)" % len(warnings))
        for wmsg in warnings:
            print("  ! %s" % wmsg)

    if errors:
        print("\nERRORS (%d)" % len(errors))
        for emsg in errors:
            print("  x %s" % emsg)
        return 1

    print("\nOK — no errors")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
