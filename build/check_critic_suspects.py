#!/usr/bin/env python3
"""check_critic_suspects.py — the meter for measurements that are the generator's, not the
house's (WP-9.1). See build/critic_suspects.py for why.

Three readings, printed; two ratchets; one verification:

  LITERALS   names `_derive_measurements` assigns a bare numeric literal. RATCHETED: the count
             may only go DOWN. To take a name off the list, model the quantity (read it from
             a record or a pack) or withhold it into `NOT_MODELLED` -- never by hiding the
             literal behind a name the AST cannot see, which the sweep below would catch.
  RATIOS     names that are a real figure scaled by a literal (`casing * 0.6`). Ratcheted the
             same way.
  SWEEP      names identical on every in-scope plan. Reported, not ratcheted: some are
             constants by construction (one head datum per storey is the pack's own hardest
             rule, stated in the generator by design) and the number moves with the reference
             corpus. What IS asserted is that the sweep ran over enough plans to mean anything.

  EDITORIAL  every entry in critique/suspects.json names a fault that exists, an expression
             that is one of that fault's own tests, and a basis whose quotation is really in
             the file it names -- the same verifier the opening grammar uses.

Exit 3 (COULD NOT EVALUATE) if the elevation generator cannot be loaded: an absent generator
is not a clean generator.

    python3 build/check_critic_suspects.py
    python3 build/check_critic_suspects.py --no-sweep     # the AST readings only (fast)
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COULD_NOT_EVALUATE = 3      # check_all.py's protocol -- 2 read as FAIL, which is a lie

# The ceilings. Measured 1 Sep 2026 on build/elevation.py as WP-9.1 found it; each may only
# go down, and the way down is to MODEL the thing, never to rename it.
# WP-9.4 RE-BASELINED THESE UPWARD, ONCE, IN PUBLIC: 35 -> 44 and 4 -> 7. The instrument
# was blind to five shapes already in elevation.py -- a constant dict read by subscript
# (SASH_FRAME, four measurements), a ternary with a literal branch, an `or 3` fallback, a
# literal inside max(), a literal one level down a BinOp -- and exempted 0.5 and 2.0 as
# "unit conversions". The jump is the instrument seeing, not the generator inventing.
LITERALS_CEILING = 44
RATIOS_CEILING = 7
UNJUDGED_CEILING = 0     # basis citations whose key path the walker could not follow
MIN_SWEEP_PLANS = 8


def _mod(name, path):
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-sweep", action="store_true")
    args = ap.parse_args()
    try:
        CS = _mod("critic_suspects", os.path.join(ROOT, "build", "critic_suspects.py"))
        lits = CS.source_literals()
        ratios = CS.literal_ratios()
    except Exception as exc:
        print(f"COULD NOT EVALUATE: build/elevation.py could not be read for its measurements: "
              f"{type(exc).__name__}: {exc}")
        return COULD_NOT_EVALUATE
    errors, notes = [], []

    print(f"{len(lits)} measurement(s) stated as a bare literal in elevation._derive_measurements "
          f"(ceiling {LITERALS_CEILING}):")
    for k, v in sorted(lits.items(), key=lambda kv: kv[1]["line"]):
        print(f"  line {v['line']:5d}  {k} = {v['value']}")
    if len(lits) > LITERALS_CEILING:
        errors.append(f"{len(lits)} literal measurements against a ceiling of {LITERALS_CEILING}: "
                      f"a new constant entered the measurements. Model it or withhold it into "
                      f"NOT_MODELLED; do not raise the ceiling.")
    elif len(lits) < LITERALS_CEILING:
        notes.append(f"literals fell to {len(lits)}; lower LITERALS_CEILING to {len(lits)} in the same commit")

    print(f"\n{len(ratios)} measurement(s) that are a figure scaled by a literal (ceiling {RATIOS_CEILING}):")
    for k, v in sorted(ratios.items(), key=lambda kv: kv[1]["line"]):
        print(f"  line {v['line']:5d}  {k}  {v['op']} {v['factor']}")
    if len(ratios) > RATIOS_CEILING:
        errors.append(f"{len(ratios)} literal-ratio measurements against a ceiling of {RATIOS_CEILING}")
    elif len(ratios) < RATIOS_CEILING:
        notes.append(f"ratios fell to {len(ratios)}; lower RATIOS_CEILING to {len(ratios)} in the same commit")

    # editorial entries, verified
    CO = _mod("check_openings", os.path.join(ROOT, "build", "check_openings.py"))
    rep = CO.Report()
    faults = {}
    for f in sorted(os.listdir(os.path.join(ROOT, "faults"))):
        if f.endswith(".json"):
            d = json.load(open(os.path.join(ROOT, "faults", f), encoding="utf-8"))
            faults[d["id"]] = d
    ed = CS.editorial()
    print(f"\n{len(ed)} editorial suspect(s) in critique/suspects.json:")
    for e in ed:
        print(f"  {e['id']}: {e['fault']} on {e['expression']}")
        where = f"critique/suspects.json[{e['id']}]"
        fault = faults.get(e["fault"])
        if not fault:
            errors.append(f"{where}: names fault '{e['fault']}', which does not exist")
            continue
        exprs = {fault.get("test", {}).get("expression")} | \
            {t.get("expression") for t in fault.get("secondary_tests", [])} | \
            {x.get("bounds_test", {}).get("expression") for x in fault.get("exceptions", [])}
        if e["expression"] not in exprs:
            errors.append(f"{where}: '{e['expression']}' is not one of {e['fault']}'s own tests")
        CO.check_basis(rep, e, source="critique/suspects.json")
    errors += rep.errors
    # a basis citing a key path the walker cannot follow is unjudged for that citation, and
    # this list is authored here: ratcheted at zero, never printed above a pass
    for u in rep.unjudged_items:
        print(f"N/EV  {u}")
    if len(rep.unjudged_items) > UNJUDGED_CEILING:
        errors.append(f"{len(rep.unjudged_items)} suspect citation(s) whose key path could not be walked, "
                      f"against a ceiling of {UNJUDGED_CEILING}")
    for u in rep.unjudged_items:
        print(f"N/EV {u}")

    if not args.no_sweep:
        const, n = CS.sweep()
        print(f"\n{len(const)} measurement(s) identical on every one of {n} in-scope plans:")
        for k, v in sorted(const.items()):
            tag = " (literal)" if k in lits else (" (ratio)" if k in ratios else "")
            print(f"  {k} = {v['value']}  on {v['plans']} plans{tag}")
        if n < MIN_SWEEP_PLANS:
            errors.append(f"the sweep covered {n} plans; below {MIN_SWEEP_PLANS} it cannot tell a "
                          f"constant from a coincidence")

    for n_ in notes:
        print(f"\nNOTE: {n_}")
    if errors:
        print("\n" + "\n".join(f"ERROR: {e}" for e in errors))
        return 1
    print(f"\nOK -- {len(lits)} literal and {len(ratios)} ratio measurements, both at or under their "
          f"ceilings; every editorial suspect names a real test and quotes a real sentence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
