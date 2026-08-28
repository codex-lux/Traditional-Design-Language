#!/usr/bin/env python3
"""Every fault test that DIVIDES, against every measurement a generator supplies as ZERO.

WHY THIS EXISTS. This corpus's flagship failure is not a wrong number; it is a rule that
presupposes the thing it measures, running on a house that has none. `dormer-off-the-bay`'s
parity secondary is `dormer_count % 2 == 1`, and the day WP-5.13 gave the plan record a way
to state "no dormers" both reference houses were convicted of "Dormers Off the Rhythm: 0
against equals 1". Zero dormers is not an even number of dormers.

`applies_when` (schema/fault.schema.json, test-level) is the guard, and the standing rule is
that ANY test whose expression divides by a count needs one. That rule has been enforced by
memory. This is the meter.

THE TWO NUMBERS, AND THE SECOND IS THE ONE THAT MATTERS.

  UNGUARDED  every test -- primary, secondary, or an exception's `bounds_test`, which
             SUBSTITUTES for the primary -- whose expression has a name in a denominator and
             carries no `applies_when.expression`. Most are safe: a width or a height is never
             zero on a building that exists. Ratcheted anyway, because the population is where
             the hazard comes from.

  LIVE       the subset whose denominator is a name a generator ACTUALLY SUPPLIES AS ZERO on
             some style today. This is measured, not guessed from the name: the sweep composes
             an elevation for every style in the corpus and records which measurements come
             back 0. A prefix test over names would be the same mistake as OQ 88's
             irreproducible "27 masonry nodes", which was an artefact of `startswith("brick")`.

             LIVE IS PINNED AT ZERO AND MUST STAY THERE. It goes non-zero in exactly two ways,
             and both are the same bug arriving from opposite directions: a generator starts
             supplying a new zero (which is what WP-5.13 did, and it convicted two houses), or
             an unguarded test starts dividing by one that already exists.

The sweep is over ALL 164 STYLES, never the two shipping plans. Three separate defects in
WP-5.13/5.17 were invisible to both reference plans and fell out of a style sweep in seconds.
"""
import collections
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAULTS = os.path.join(ROOT, "faults")
PLAN = os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")

UNGUARDED_RATCHET = 306      # may only fall
LIVE_RATCHET = 0             # may never rise
COULD_NOT_EVALUATE = 2

DENOMINATOR = re.compile(r"/\s*([A-Za-z_][A-Za-z0-9_]*)")


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def dividing_tests():
    """(fault, where, expression, [denominators]) for every UNGUARDED dividing test."""
    out = []
    for name in sorted(os.listdir(FAULTS)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(FAULTS, name), encoding="utf-8") as fh:
            rec = json.load(fh)

        def look(t, where):
            if not t or not t.get("expression"):
                return
            # A guard with an expression is a guard. `_eval_test` refuses a malformed one
            # loudly (WP-5.14), so presence is enough here.
            if (t.get("applies_when") or {}).get("expression"):
                return
            names = sorted(set(DENOMINATOR.findall(t["expression"])))
            if names:
                out.append((rec["id"], where, t["expression"], names))

        look(rec.get("test"), "test")
        for i, t in enumerate(rec.get("secondary_tests") or []):
            look(t, "secondary_tests[%d]" % i)
        for exc in (rec.get("exceptions") or []):
            # THE THIRD LOCATION, AND THE ONE THAT BITES: core.check_measurements
            # SUBSTITUTES a bounds_test for the fault's primary on a style match, so an
            # unguarded division here replaces a guarded one.
            look(exc.get("bounds_test"),
                 "exceptions[%s].bounds_test" % exc.get("style"))
    return out


def measured_zeros():
    """measurement name -> how many styles a generator supplies it as 0 on."""
    el = _mod("elevation", "build/elevation.py")
    core = _mod("core", "mcp_server/core.py")
    with open(PLAN, encoding="utf-8") as fh:
        plan = json.load(fh)
    zeros, composed = collections.Counter(), 0
    for style in sorted(core._data()["styles"]):
        probe = dict(plan)
        probe["style"] = style
        try:
            meas = el.build_elevation(probe)["measurements"]
        except Exception:
            continue
        composed += 1
        for k, v in meas.items():
            if v == 0:
                zeros[k] += 1
    return zeros, composed


def main():
    unguarded = dividing_tests()
    try:
        zeros, composed = measured_zeros()
    except Exception as e:                                   # pragma: no cover
        print("COULD NOT EVALUATE — the elevation generator did not run: %s" % e)
        print("The unguarded population is %d; the LIVE hazard was not measured, "
              "which is not a pass." % len(unguarded))
        return COULD_NOT_EVALUATE
    if not composed:
        print("COULD NOT EVALUATE — no style composed an elevation, so no zero was observed")
        return COULD_NOT_EVALUATE

    live = [(fid, where, d, zeros[d]) for fid, where, _e, names in unguarded
            for d in names if d in zeros]

    by_where = collections.Counter(w.split("[")[0] for _f, w, _e, _n in unguarded)
    print("%d style(s) composed an elevation; %d measurement name(s) come back ZERO on at "
          "least one" % (composed, len(zeros)))
    print("%d unguarded dividing test(s) — %s (ratchet %d)"
          % (len(unguarded), ", ".join("%s %d" % (k, v) for k, v in sorted(by_where.items())),
             UNGUARDED_RATCHET))
    print("%d of them divide by a name a generator actually supplies as zero (ratchet %d)"
          % (len(live), LIVE_RATCHET))
    for fid, where, d, n in live:
        print("  x %s %s divides by %s, which is 0 on %d style(s) and has no applies_when"
              % (fid, where, d, n))

    failed = []
    if len(live) > LIVE_RATCHET:
        failed.append("live divisions by a supplied zero: %d -> %d" % (LIVE_RATCHET, len(live)))
    if len(unguarded) > UNGUARDED_RATCHET:
        failed.append("unguarded dividing tests: %d -> %d"
                      % (UNGUARDED_RATCHET, len(unguarded)))
    if failed:
        print("\nRATCHET BROKEN — " + "; ".join(failed))
        print("A test that divides by a count needs an `applies_when` precondition, or it "
              "errors on the house that has none. Guard it; do not raise the ratchet.")
        return 1
    print("\nEvery dividing test whose denominator a generator can supply as zero is guarded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
