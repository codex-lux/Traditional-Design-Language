#!/usr/bin/env python3
"""fault_thresholds.py -- where a fault's threshold comes from, per style.

WHY THIS EXISTS. OQ 63 (closed 24 Aug 2026) found that a fault's tests are written for one
tradition and run against every style, added `applies_to_styles` to the shared test object,
and scoped SIX secondary tests. It deferred the primary sweep in writing -- *"The same
pattern exists on PRIMARY tests ... That sweep wants its own package"* -- and deferred
`truss-flattened-pitch`'s per-style band table as *"the remaining work"*. This is that
package's instrument. **It reports and decides nothing**: no ratchet lives here, no check
runs it, and it convicts no record. Its output is the reading WP-14.5 is written from.

Measured before it was built, and each figure bounds what this file may claim:

  * **0 of 210 primary tests carry `applies_to_styles`.** All six uses are on secondaries,
    across five records. The primary sweep is unstarted, not partly done.
  * **The elevation layer speaks for 41 of 164 styles.** The other 123 return
    `applicable: false` naming their own reason -- outside `opening-proportion`'s and/or
    `facade-classical`'s calibration -- and are wholly UNJUDGED: median 184 unjudged, 0
    clear, 0 present, 0 measurements. **A census that counts them as clean is the fake-pass
    direction at corpus scale**, so this file states the denominator as 41 and prints the
    123 by name.
  * Over those 41, one plan's measurements with only the style label swapped, and TWO
    QUANTITIES THAT MUST NOT SHARE A WORD -- this docstring called both "convictions" until
    they were re-derived side by side. **FAULTS present: 892** (636 failing on a primary, 300
    on a secondary, 51 on both). **FAILING-TEST ROWS: 944** (642 primary, 293 secondary, 9
    bounds_test), which is what the census below counts, because a fault can fail on two
    tests at once and `plan_check` prints only the first -- 35 of 251 findings over the
    shipped plans hide a second
    (`oq/a-fault-present-finding-names-one-of-its-failing-tests`). Before WP-14.5's own
    substitution the pair was 894 and 951.

THE DISCRIMINATOR, AND WHY A NAIVE ONE WAS REFUSED. **Fourteen faults convict 41 of 41
styles** -- re-derived here, because the figure this docstring first carried was SEVEN and a
number quoted rather than re-run is exactly what this package is about. That is NOT evidence
of a one-tradition number: with the measurements held constant it is
equally consistent with the house genuinely having the fault, and
`storeys-out-of-vertical-alignment` is one this corpus already records firing at 38.556 in
against 2.0. **Ruled 20 Sep 2026: a threshold is convicted only where the corpus ALREADY
holds a style-specific figure for the same quantity.** No band may be invented here.

SO THE JOIN IS THE HARD PART, AND IT IS A CLOSED TABLE. A fault test reads
`roof_slope_angle_deg`; the style states `roof_pitch_rise_per_12`. Two names, one quantity,
and no name match finds it -- which is OQ 48's own problem one layer out. `QUANTITY_JOIN`
below is authored, explicit and closed, on `build/construction_vocabulary.py`'s precedent:
each entry says which two names mean one quantity and how to convert, each carries its
reason, and **an expression the table does not reach is reported `no_second_number` rather
than guessed at**. Authoring a RELATION between two records is not authoring a NUMBER; the
numbers stay where their authors put them.

    python3 build/fault_thresholds.py                 # the census
    python3 build/fault_thresholds.py --json          # the report's own tables
    python3 build/fault_thresholds.py --fault <id>    # one fault, every style
    python3 build/fault_thresholds.py --refusals      # the 123, by name and reason
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COULD_NOT_EVALUATE = 3     # check_all.py's protocol -- 2 reads as FAIL, which is a lie

# The corpus's own most carefully authored plan, and the one `check_division_guards.py` and
# two test files already swap styles on. The house is held CONSTANT on purpose: this file
# measures the threshold, and a different house per style would measure the house.
PROBE_PLAN = os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")


def _mod(name, path):
    # build/modcache.py, never a local by-path loader (OQ 28; tests/test_modcache.py counts
    # module executions, and tests/test_no_by_path_loaders.py reads this file's source).
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


# --------------------------------------------------------------------- the quantity join
#
# fault-test expression  ->  how the corpus states the same quantity per style.
#
# `reads`   the identifier a fault test measures.
# `states`  the expression a style's own migrated constraint uses for that quantity.
# `convert` takes the style-side value and returns the fault-side one.
# `why`     the argument that the two are one quantity. Checkable by a reader; this is the
#           part a machine cannot supply and the part that makes an entry admissible.
#
# TO ADD AN ENTRY you must be able to write `why` as a statement about the two records, not
# about the numbers coming out close. Two names that happen to agree on this corpus are
# OQ 48's error wearing a join's clothes.
QUANTITY_JOIN = {
    "roof_slope_angle_deg": {
        "states": "roof_pitch_rise_per_12",
        "convert": lambda v: math.degrees(math.atan(v / 12.0)),
        "units_in": "rise per 12",
        "units_out": "deg",
        "why": "Rise-per-12 and the slope angle are the same quantity in two notations -- "
               "atan(rise/12) is exact, not a calibration. Measured: the five bands "
               "`truss-flattened-pitch`'s own note names reproduce from the styles' migrated "
               "constraints to a tenth of a degree on four of five, which is the evidence "
               "that the note is a transcription of this data rather than a second source.",
    },
}

# Expressions a reader will reach for and which this table REFUSES, each with the reason.
# A refusal recorded here is a decision; an expression simply absent is an unread question,
# and the census prints those two apart.
JOIN_REFUSED = {
    "roof_height_eave_to_ridge": "A roof's height over its wall depends on the SPAN and the "
                                 "wall height as well as the pitch, so a per-style pitch does "
                                 "not determine it. `truss-flattened-pitch`'s primary test is "
                                 "deliberately the style-independent form and its own note "
                                 "says so; scoping it would be scoping the wrong test.",
    "wall_height_grade_to_eave": "The denominator of the same ratio, and the same reason.",
}


def style_band(style, states, D):
    """The style's OWN statement of a quantity, as `(lo, hi, rule_id, direction)`.

    **DELEGATES to `mcp_server/core.py::style_band` and does not respell it.** That is the
    reader the engine substitutes with (WP-14.5), so a diagnostic that walked the constraint
    list itself could report a band the engine does not use -- which is the defect this whole
    package is about, committed by its own instrument. The shapes differ only in field order:
    core returns `(direction, lo, hi, rule)` because a direction decides how the other three
    are read.
    """
    CORE = _mod("core", os.path.join(ROOT, "mcp_server", "core.py"))
    b = CORE.style_band(style, states, D)
    if b is None:
        return None
    direction, lo, hi, rule = b
    return (lo, hi, rule, direction)


def second_number(style, names, D):
    """Does the corpus already hold a style-specific figure for any quantity this test reads?

    The ruling of 20 Sep 2026 in one function. Returns a list of evidence dicts (possibly
    empty) and a list of the names this file's table does not reach, so a caller can tell
    *no second number exists* from *nobody has asked whether one does*.
    """
    found, unreached = [], []
    for n in sorted(names):
        entry = QUANTITY_JOIN.get(n)
        if not entry:
            if n in JOIN_REFUSED:
                continue                       # a decision, not a gap
            unreached.append(n)
            continue
        band = style_band(style, entry["states"], D)
        if not band:
            continue                           # the table reaches it; this style states none
        lo, hi, rule, direction = band
        found.append({
            "reads": n, "states": entry["states"], "rule": rule, "direction": direction,
            "lo": None if lo is None else round(entry["convert"](lo), 1),
            "hi": None if hi is None else round(entry["convert"](hi), 1),
            "units": entry["units_out"],
        })
    return found, unreached


def reading(style, plan, EL):
    """One style's measurements, or the generator's own refusal, verbatim.

    `build_elevation` declines 123 of 164 styles by name. That refusal is DATA -- it is the
    census's own denominator -- so it is returned rather than swallowed by an `except`.
    """
    probe = dict(plan)
    probe["style"] = style
    try:
        el = EL.build_elevation(probe)
    except Exception as exc:                                        # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"
    meas = el.get("measurements") or {}
    if not any(v is not None for v in meas.values()):
        return None, el.get("note") or "the generator supplied no measurement and said nothing"
    return meas, None


def census(plan=None, styles=None):
    """Per (style, fault, test location): the verdict, and where the deciding number is from.

    THREE buckets and never two. `evidenced` is a finding; `no_second_number` is a research
    gap that convicts nothing; `unreached_names` is this file's own table saying it has not
    been asked. Collapsing the second into the first is what the ruling forbids.
    """
    EL = _mod("elevation", os.path.join(ROOT, "build", "elevation.py"))
    CORE = _mod("core", os.path.join(ROOT, "mcp_server", "core.py"))
    DET = _mod("detection", os.path.join(ROOT, "build", "detection.py"))
    D = CORE._data()
    plan = plan or json.load(open(PROBE_PLAN, encoding="utf-8"))
    styles = styles or sorted(D["styles"])

    rows, refused, unreached = [], [], set()
    for style in styles:
        meas, why = reading(style, plan, EL)
        if meas is None:
            refused.append({"style": style, "why": why})
            continue
        r = CORE.check_measurements(meas, style=style, limit=10 ** 6)
        for row in r["faults_present"]:
            rec = D["faults"][row["fault"]]
            primary = (rec.get("test") or {}).get("expression")
            secondary = {t.get("expression") for t in (rec.get("secondary_tests") or [])}
            for ev in (row.get("failing") or []):
                expr = ev.get("expression")
                where = ("primary" if expr == primary
                         else "secondary" if expr in secondary else "bounds_test")
                names = DET.identifiers(expr)
                found, miss = second_number(style, names, D)
                unreached |= set(miss)
                rows.append({
                    "style": style, "fault": row["fault"], "where": where,
                    "expression": expr, "value": ev.get("value"),
                    "required": ev.get("required"), "severity": row.get("severity"),
                    "universal": "universal" in (rec.get("applies_to") or []),
                    "scoped": bool((rec.get("test") or {}).get("applies_to_styles")),
                    "evidence": found,
                })
    return {"judged": len(styles) - len(refused), "styles": len(styles),
            "refused": refused, "rows": rows, "unreached_names": sorted(unreached)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="the report's own tables")
    ap.add_argument("--fault", help="one fault id, every style that judges it")
    ap.add_argument("--refusals", action="store_true", help="the styles with no elevation")
    a = ap.parse_args(argv)

    try:
        c = census()
    except Exception as exc:                                        # noqa: BLE001
        print(f"COULD NOT EVALUATE: the census could not be taken: {type(exc).__name__}: {exc}")
        return COULD_NOT_EVALUATE

    if a.json:
        print(json.dumps(c, indent=2, sort_keys=True))
        return 0
    if a.refusals:
        print(f"{len(c['refused'])} of {c['styles']} styles supply no measurement:\n")
        for r in c["refused"]:
            print(f"  {r['style']:<34} {r['why']}")
        return 0

    rows = [r for r in c["rows"] if not a.fault or r["fault"] == a.fault]
    ev = [r for r in rows if r["evidence"]]
    prim = [r for r in rows if r["where"] == "primary"]
    print(f"THE CENSUS IS OVER {c['judged']} OF {c['styles']} STYLES. The other "
          f"{len(c['refused'])} supply no measurement at all and are UNJUDGED, not clean "
          f"(--refusals names them).\n")
    print(f"  conviction rows            {len(rows)}")
    print(f"    deciding on a PRIMARY    {len(prim)}")
    print(f"    deciding on a secondary  {sum(1 for r in rows if r['where'] == 'secondary')}")
    print(f"    deciding on a bounds_test{sum(1 for r in rows if r['where'] == 'bounds_test'):>3}")
    print(f"\n  EVIDENCED -- the corpus already states this style's own figure: {len(ev)}")
    for r in ev[:40]:
        e = r["evidence"][0]
        band = f"{e['lo']}" + (f"-{e['hi']}" if e["hi"] is not None else " and up")
        print(f"    {r['style']:<28} {r['fault']:<34} {r['expression']}"
              f" = {r['value']} against {r['required']}   own band {band} {e['units']}  [{e['rule']}]")
    print(f"\n  NO SECOND NUMBER -- universal because nobody wrote another: "
          f"{len(rows) - len(ev)}  (reported, convicting nothing)")
    print(f"\n  this file's join table does not reach {len(c['unreached_names'])} measurement "
          f"name(s); {len(JOIN_REFUSED)} more are refused with a stated reason.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
