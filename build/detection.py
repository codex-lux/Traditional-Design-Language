#!/usr/bin/env python3
"""detection.py — the one reader of a fault record's `detection` prose.

WHY THIS EXISTS. `detection` is REQUIRED on every one of the 210 records in `faults/`. It is
139,070 characters -- nearly TEN TIMES the 14,154 of `daylight.orientation`, whose zero
readers WP-11.9 closed -- and its schema description says what it is for: "How to spot it fast, from the street or from a photograph.
Written for both a person and a model looking at an image." Until this module **nothing read
one of them** -- every `detection` hit in the tree's Python and JavaScript is a different
sense of the word. That is the shape of `daylight.orientation`'s zero readers (WP-11.9), at
ten times the size.

IT IS NOT THE LARGEST PROSE FIELD HERE AND AN EARLIER DRAFT OF THIS DOCSTRING SAID IT WAS.
`correct_practice` is 191,878 characters over the same 210 records. That one has a reader
(`tests/test_facade.py`), so it is not this defect -- but the claim was wrong, and it is the
third figure in this package corrected by MEASURING rather than by re-reading.

THE READER IT WAS WRITTEN FOR IS THE UNJUDGED VERDICT. On `tidewater-georgian-careful` --
this corpus's own most carefully authored plan -- `core.check_measurements` returns **120 of
210 faults COULD NOT EVALUATE**, naming **299 distinct missing measurements**, and says
nothing else about any of them. Three records already exist about each of those names and
none of them reaches the reader:

  · the fault's own `detection` prose, which is the corpus's written account of how to
    obtain the number;
  · the surfaces its tests declare (`measurable_from`);
  · and, for 23 of the 299, a REFUSAL taken deliberately and written down --
    `arrangement.NOT_DERIVABLE` and `elevation.NOT_MODELLED` name the quantity and say why
    this corpus will not supply it.

So a reader is told "could not evaluate: needs `dedicated_plant_room_area_sqft`" about a name
the corpus considered, built, measured, and withdrew because it convicted both reference
plans -- and is given no way to know that. An unjudged whose reason is recorded elsewhere and
never quoted reads exactly like a gap nobody has looked at. This module makes the join.

WHAT THIS MODULE MAY NOT DO.

  · It may not supply a measurement. It reports; `arrangement.py` and `elevation.py` derive.
  · It may not COPY a refusal. `refusals()` reads the two authorities live, so a reason
    corrected there is corrected here, and a name added there is refused here with no edit.
    Two spellings of one refusal is the defect `check_addresses.py` exists for.
  · `checks()` is a CRUDE SPLIT of English prose and is a READING AID, NOT A COUNT. The
    number it returns may not be ratcheted, published as a measurement, or compared between
    records: the prose numbers its checks four different ways and this reader knows two of
    them. `check_grouping_rules.prose_meter`'s discipline, one population over -- the way to
    make it exact is to author the split, never to widen the pattern until the number looks
    right.

TWO DISCRIMINATORS WERE BUILT HERE AND MEASURED AND FALSIFIED, and they are recorded because
each one reads perfectly well and is wrong:

  1. "`measurable_from: photograph` means this compiler can never reach it." FALSE. **54
     photograph-only faults are JUDGED** on the Tidewater plan, because `elevation.py`
     supplies 184 quantities a photograph test can read. `measurable_from` says what a
     photograph SUFFICES for; it does not say a drawing cannot.
  2. "The detection prose names its own surface, so hold it against the tests'
     `measurable_from`." Unusable as a checker: **the word `elevation` in this prose means
     the FACE of the building, not the drawing** ("count exterior doors on the rear
     elevation"). A naive vocabulary including it reports 22 records whose prose and tests
     share no surface; **12 of the 22 are that word sense and vanish when it is excluded**,
     so a checker built on the naive match would convict twelve records of a disagreement
     they do not have. The 10 that survive are real and are not a defect either -- a fault
     may honestly describe a photograph route while its test is stated for a plan -- which is
     why `surface_words()` is REPORTED, ratcheted nowhere, and convicts nothing.

  python3 build/detection.py <fault-id>          # the procedure, its surfaces, its quantities
  python3 build/detection.py --plan plans/<id>.json   # the unjudged census for one plan
  python3 build/detection.py --contradictions    # names a table refuses and a layer supplies
  python3 build/detection.py selftest
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAULTS = os.path.join(ROOT, "faults")


def _mod(name, path):
    # build/modcache.py, never a local by-path loader (OQ 28; tests/test_modcache.py counts
    # module executions, and tests/test_no_by_path_loaders.py reads this file's source).
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


# ------------------------------------------------------------------ the refusal authorities
#
# Read live and never copied. A (module, attribute) pair per table; the module is loaded
# through modcache, so the cost is one import shared with plan_check, which loads both.
#
# TO ADD A TABLE: add the pair. Do NOT add a name to a dict here -- a refusal belongs beside
# the layer that would otherwise have derived it, where the reason can be checked against the
# code that would have done the deriving.
REFUSAL_TABLES = (
    ("arrangement", "NOT_DERIVABLE"),
    ("elevation", "NOT_MODELLED"),
)

# (There is no DRAWN_SURFACES constant, and an earlier draft had one. Discriminator 1 in the
# docstring -- that a `photograph` test is out of a drawing-based compiler's reach -- was
# falsified by measurement, so a constant naming the drawing surfaces had no reader left, and
# a dead constant in a module about unread fields is a poor advertisement.)

_IDENT = re.compile(r"\b[a-z_][a-z0-9_]*\b")


def identifiers(expression):
    """The measurement names an expression reads. THE ONE SPELLING of this split.

    `plan_check._clear_on_a_constant` reads the same thing off a CLEARED fault's evaluated
    tests and called this through a second copy of the pattern for about an hour. Two
    spellings of one rule is what `check_addresses.py` exists for.
    """
    return {m.group(0) for m in _IDENT.finditer(expression)} if isinstance(expression, str) else set()

# The two ways this prose numbers its checks. It has at least four -- "(1) ... (2) ...",
# "Second, ... Third, ...", "A third quick check", and an unnumbered run of sentences -- and
# this reader knows the first two. See the docstring: the result is a reading aid.
_PARENTHESISED = re.compile(r"(?=\((?:[1-9])\)\s)")
_ORDINAL = re.compile(
    r"(?=(?:\bSecond\b|\bThird\b|\bFourth\b|\bFifth\b|\bSixth\b)(?:,|\s+(?:and|check|test)\b))"
)


def _load_faults():
    out = {}
    for name in sorted(os.listdir(FAULTS)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(FAULTS, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        if isinstance(rec, dict) and isinstance(rec.get("id"), str):
            out[rec["id"]] = rec
    return out


def refusals():
    """Every measurement name a layer of this corpus refuses to supply, with its reason.

    Read live from the tables themselves. The value is {"by": "<module>.<attr>", "why":
    "<the reason as written there>"} -- verbatim, because the reason is the whole value of a
    refusal and a paraphrase of one is a second refusal.
    """
    out = {}
    for mod_name, attr in REFUSAL_TABLES:
        mod = _mod(mod_name, os.path.join(ROOT, "build", mod_name + ".py"))
        table = getattr(mod, attr, None)
        if not isinstance(table, dict):
            continue
        for name, why in table.items():
            if name in out:
                # Two tables refusing one name is not an error -- it is two layers each
                # declining the same quantity -- but the reader must be told both, or the
                # first-wins order of REFUSAL_TABLES silently picks one reason.
                out[name]["by"] += " and " + f"{mod_name}.{attr}"
                out[name]["also"] = why
                continue
            out[name] = {"by": f"{mod_name}.{attr}", "why": why}
    return out


def measurement_names(fault):
    """Every identifier the fault's tests read, over ALL THREE test locations.

    A fault's tests live in `test`, `secondary_tests` and `exceptions[].bounds_test`, and the
    third is the one that bites -- it SUBSTITUTES for the primary on a matching style. Each
    test's `applies_when` is read too: a precondition that cannot be evaluated leaves the test
    not run, so its measurement is as missing as the test's own.
    """
    out = set()
    for t in _tests(fault):
        for expr in (t.get("expression"), (t.get("applies_when") or {}).get("expression")):
            out |= identifiers(expr)
    return out


def _tests(fault):
    if not isinstance(fault, dict):
        return []
    out = []
    if isinstance(fault.get("test"), dict):
        out.append(fault["test"])
    for t in fault.get("secondary_tests") or []:
        if isinstance(t, dict):
            out.append(t)
    for e in fault.get("exceptions") or []:
        if isinstance(e, dict) and isinstance(e.get("bounds_test"), dict):
            out.append(e["bounds_test"])
    return out


def surfaces(fault):
    """The surfaces the fault's OWN tests declare, sorted. COULD NOT EVALUATE is `[]`.

    Not derived from the detection prose -- see falsified discriminator 2 in the module
    docstring. An empty list is a fault whose tests declare no surface at all, which is a
    third state and not a photograph.
    """
    return sorted({t["measurable_from"] for t in _tests(fault)
                   if isinstance(t.get("measurable_from"), str)})


def surface_words(fault):
    """The surfaces the DETECTION PROSE names, by word match. AN UPPER BOUND, AND A BAD ONE.

    It is here so that the reading is available and so that its failure mode is written down
    beside it rather than rediscovered: `elevation` and `section` are excluded from the
    vocabulary ON PURPOSE. In this prose "elevation" overwhelmingly means the FACE of the
    building -- "count exterior doors on the rear elevation of the main block" -- and a match
    on it reported 22 records whose prose and tests share no surface, of which 12 were that
    word sense alone -- and THAT figure is a property of the vocabulary rather than of the
    corpus, so `tests/test_detection.py` pins the naive vocabulary in full beside it.
    Nothing may be ratcheted on this function and no check may convict on
    it: the 10 that survive the exclusion are genuine differences of route, not errors.
    """
    prose = fault.get("detection") if isinstance(fault, dict) else None
    if not isinstance(prose, str):
        return []
    words = {
        "photograph": r"\bphotograph\b|\bphoto\b|\bimage\b|\blisting shot\b",
        "plan": r"\bon a plan\b|\bon the plan\b|\bin plan\b|\bin the plan\b|\bfrom a plan\b|\bplan overlay\b",
        "site-visit": r"\bon site\b|\bin person\b|\bwith a tape\b|\bstand in\b",
    }
    return sorted(k for k, pat in words.items() if re.search(pat, prose, re.I))


def checks(fault):
    """The detection procedure split into the checks its own prose numbers.

    A READING AID, NOT A COUNT -- see the module docstring. Returns the whole prose as a
    single element where it numbers nothing, which is the honest answer and not a claim that
    the procedure has one check.
    """
    prose = fault.get("detection") if isinstance(fault, dict) else None
    if not isinstance(prose, str) or not prose.strip():
        return []
    parts = [p.strip() for p in _PARENTHESISED.split(prose) if p.strip()]
    if len(parts) == 1:
        parts = [p.strip() for p in _ORDINAL.split(prose) if p.strip()]
    return parts


def disposition(name, refs=None):
    """What this corpus has already decided about one missing measurement name.

    Two verdicts, and the second is deliberately not called a gap:

      refused     a layer names this quantity and declines to supply it, with a reason
                  written beside the code that would have derived it. The decision is taken;
                  the reader needs the reason, not a work item.
      unsupplied  no layer refuses it and no layer supplies it. That is NOT "nobody has
                  looked" and it is NOT "impossible" -- it is unread, and which of the two it
                  is cannot be decided from the record. Saying more would be inventing a
                  verdict, which is what this whole module exists to stop.
    """
    refs = refusals() if refs is None else refs
    hit = refs.get(name)
    if hit:
        return {"name": name, "verdict": "refused", **hit}
    return {"name": name, "verdict": "unsupplied"}


def contradictions(supplied):
    """Names a refusal table refuses that the measurement layer SUPPLIES anyway.

    `supplied` is the measurement dict a caller actually handed the fault evaluator. A name
    in both is a refusal that cannot bite: a reader of the table concludes this corpus
    declines to state the quantity, and the fault is judged on it regardless. That is the
    same shape as a guard that cannot fire, on the other side of the line.

    It is a REPORT with a ratchet and not an error, because the two live instances are of
    opposite kinds and one of them is correct -- see `tests/test_detection.py` and the
    WP-13.1 report.
    """
    refs = refusals()
    return sorted(n for n in supplied if n in refs)


# ---------------------------------------------------------------------------- the census
def census(plan_result=None, faults=None):
    """The corpus figure this module was built to publish.

    Takes a `plan_check.check()` result and counts, over its `fault_unjudged` rows, what has
    already been decided about each distinct missing name.
    """
    faults = _load_faults() if faults is None else faults
    refs = refusals()
    out = {"faults": len(faults), "refusals": len(refs)}
    # Corpus-side, independent of any plan: every identifier any fault test reads, and how
    # many of those a table refuses.
    read = set()
    for rec in faults.values():
        read |= measurement_names(rec)
    out["identifiers_read_by_fault_tests"] = len(read)
    out["refusals_naming_nothing_any_test_reads"] = sorted(n for n in refs if n not in read)
    if plan_result is None:
        return out
    rows = plan_result.get("fault_unjudged") or []
    names, refused, unsupplied = set(), set(), set()
    per_fault = {"refused": 0, "unsupplied": 0, "mixed": 0, "no_names": 0}
    for row in rows:
        ns = [n for n in (row.get("needs") or []) if isinstance(n, str)]
        names.update(ns)
        r = {n for n in ns if n in refs}
        u = set(ns) - r
        refused |= r
        unsupplied |= u
        per_fault["no_names" if not ns else
                   "refused" if not u else
                   "unsupplied" if not r else "mixed"] += 1
    out.update({
        "unjudged_faults": len(rows),
        "distinct_missing_names": len(names),
        "missing_refused": len(refused),
        "missing_unsupplied": len(unsupplied),
        "by_fault": per_fault,
    })
    return out


# ---------------------------------------------------------------------------------- CLI
def _print_fault(fid, faults, refs):
    rec = faults.get(fid)
    if rec is None:
        print(f"no such fault: {fid}")
        return 1
    print(f"{rec['id']} — {rec.get('name')}   [{rec.get('severity')}]")
    print(f"  surfaces its tests declare : {', '.join(surfaces(rec)) or '(none declared)'}")
    print(f"  surfaces its prose names   : {', '.join(surface_words(rec)) or '(none matched)'}"
          "   (an upper bound by word match; decides nothing)")
    print("\n  DETECTION (the procedure, as written):")
    for i, ch in enumerate(checks(rec), 1):
        print(f"    [{i}] {ch}")
    print("\n  QUANTITIES ITS TESTS READ:")
    for n in sorted(measurement_names(rec)):
        d = disposition(n, refs)
        if d["verdict"] == "refused":
            print(f"    REFUSED    {n}")
            print(f"               {d['by']}: {d['why']}")
        else:
            print(f"    unsupplied {n}")
    return 0


def main(argv):
    faults = _load_faults()
    refs = refusals()
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "selftest":
        return selftest()
    if argv[0] == "--contradictions":
        print("A name a refusal table refuses that the measurement layer supplies anyway.")
        print("Run against the elevation and arrangement layers on every shipped plan.\n")
        EL = _mod("elevation", os.path.join(ROOT, "build", "elevation.py"))
        AR = _mod("arrangement", os.path.join(ROOT, "build", "arrangement.py"))
        supplied = set()
        for path in sorted(glob.glob(os.path.join(ROOT, "plans", "*.json"))):
            plan = json.load(open(path, encoding="utf-8"))
            try:
                el = EL.build_elevation(plan)
                supplied |= {k for k, v in (el.get("measurements") or {}).items() if v is not None}
            except Exception:                                        # noqa: BLE001
                pass
            try:
                supplied |= {k for k, v in AR.declared(plan).items() if v is not None}
            except Exception:                                        # noqa: BLE001
                pass
        hits = contradictions(supplied)
        for n in hits:
            print(f"  {n}\n    refused by {refs[n]['by']}: {refs[n]['why']}")
        print(f"\n{len(hits)} contradiction(s).")
        return 0
    if argv[0] == "--plan":
        PC = _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
        plan = json.load(open(argv[1], encoding="utf-8"))
        res = PC.check(plan)
        c = census(res, faults)
        print(json.dumps(c, indent=1))
        print("\nUNJUDGED faults every one of whose missing names has been REFUSED by name:")
        for row in res.get("fault_unjudged") or []:
            ns = [n for n in (row.get("needs") or []) if isinstance(n, str)]
            if ns and all(n in refs for n in ns):
                print(f"  {row['fault']}")
                for n in ns:
                    print(f"      {n}\n        {refs[n]['by']}: {refs[n]['why']}")
        return 0
    return _print_fault(argv[0], faults, refs)


def selftest():
    faults = _load_faults()
    refs = refusals()
    bad = []
    if len(faults) < 200:
        bad.append(f"only {len(faults)} fault records loaded")
    for fid, rec in faults.items():
        if not isinstance(rec.get("detection"), str) or not rec["detection"].strip():
            bad.append(f"{fid}: no detection prose")
        if not checks(rec):
            bad.append(f"{fid}: checks() returned nothing")
    read = set()
    for rec in faults.values():
        read |= measurement_names(rec)
    dead = sorted(n for n in refs if n not in read)
    for n in dead:
        bad.append(f"refusal names nothing any fault test reads: {n} ({refs[n]['by']})")
    print(f"{len(faults)} faults · {len(refs)} refusals · {len(read)} identifiers read by fault tests")
    if bad:
        for b in bad:
            print("  x " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
