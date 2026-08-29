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
WP-5.13/5.14 were invisible to both reference plans and fell out of a style sweep in seconds.
"""
import collections
import functools
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAULTS = os.path.join(ROOT, "faults")
PLAN = os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")

# 306 -> 307 on 28 Aug 2026, and the direction is the reader improving rather than the corpus
# worsening: widening `denominators()` to see a PARENTHESISED denominator surfaced
# `door-too-wide-for-its-surround`'s `door_leaf_width_in / (storey_height_in / 3.5)`, which
# divides by a name the old regex could not see at all. A ratchet raised because the instrument
# got sharper must say so, or the next reader reads it as a regression that was waved through.
UNGUARDED_RATCHET = 307      # may only fall
LIVE_RATCHET = 0             # may never rise
COULD_NOT_EVALUATE = 3      # check_all.py's protocol -- 2 read as FAIL, which is a lie
                            # about WHICH state the checker was in. A sweep that could not
                            # run is not a sweep that found something, and the runner has
                            # one code for each; this file declared its own and got the
                            # wrong one. Every other checker in build/ uses 3.

# EVERY NAME IN A DENOMINATOR, not just an identifier sitting immediately after the slash.
# The first version was `/\s*([A-Za-z_][A-Za-z0-9_]*)` and could not see a PARENTHESISED
# denominator: `door_leaf_width_in / (storey_height_in / 3.5)` divides by an expression whose
# only name is `storey_height_in`, and the checker read no denominator at all -- an unguarded
# division invisible to the thing built to find unguarded divisions. Six other expressions in
# the corpus divide by a bare literal (`/ 2`, `/ 10`), which is genuinely safe and correctly
# yields no name. Found by the WP-8.4 adversarial audit.
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def denominators(expr):
    """Every NAME that appears in a denominator position, parentheses included.

    Walks the expression once: at each `/`, take the following operand -- a parenthesised
    group balanced by depth, or the run up to the next operator -- and return the identifiers
    inside it.

    TWO FORMS IT CANNOT ATTRIBUTE, and `unattributable_denominators()` beside it is what
    names them -- this docstring used to promise that `main()` reported them and `main()`
    had no such branch, which is this project's own named disease inside the file that
    measures another instance of it. A function call takes the callee and loses the argument
    (`a / max(b, 1)` -> `{'max'}`); a unary minus yields nothing at all (`a / -b` -> set()).
    Neither form occurs in the corpus today -- 0 of the 326 dividing expressions -- so this
    is a false promise made true rather than a live miss found."""
    out, i, n = set(), 0, len(expr or "")
    while i < n:
        if expr[i] != "/":
            i += 1
            continue
        j = i + 1
        while j < n and expr[j] == " ":
            j += 1
        if j < n and expr[j] == "(":
            depth, k = 0, j
            while k < n:
                if expr[k] == "(":
                    depth += 1
                elif expr[k] == ")":
                    depth -= 1
                    if depth == 0:
                        k += 1
                        break
                k += 1
            operand, i = expr[j:k], k
        else:
            k = j
            while k < n and (expr[k].isalnum() or expr[k] in "_."):
                k += 1
            operand, i = expr[j:k], max(k, j + 1)
        out.update(_IDENT.findall(operand))
    return out


def unattributable_denominators():
    """Dividing tests whose denominator this walker cannot read, named rather than dropped.

    A denominator it cannot attribute is a test the LIVE meter cannot see, so silently
    dropping it makes an unguarded division invisible forever -- unjudged collapsed into a
    pass, in the checker written to stop exactly that. Two forms: a call, where `_IDENT`
    returns the callee and not the argument; and a unary minus, where the operand run stops
    immediately and returns nothing.
    """
    out = []
    for fid, where, expr, names in dividing_tests():
        for m in re.finditer(r"/\s*(.+?)(?=$|[+\-*/<>=,)])", expr or ""):
            operand = m.group(1).strip()
            if re.match(r"^[A-Za-z_][A-Za-z0-9_.]*\s*\(", operand):
                out.append((fid, where, expr, "a call: `%s`" % operand))
            elif operand.startswith("-"):
                out.append((fid, where, expr, "a unary minus: `%s`" % operand))
        if "/" in (expr or "") and not names:
            out.append((fid, where, expr, "no name attributed to any denominator"))
    return out


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
            names = sorted(denominators(t["expression"]))
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


@functools.lru_cache(maxsize=1)
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


def live_hazards():
    """The measurement, in ONE place, so a test can take it rather than read the pin.

    `tests/test_construction_scope.py` asserted `LIVE_RATCHET == 0` -- the module's own
    literal -- and called itself "the figure that matters". Adding an unguarded
    `x / dormer_count` secondary to a fault broke this checker's ratchet and left that test
    green, because a constant is not a measurement. Extracted rather than duplicated: two
    copies of this computation is how the citation grammar came to be spelled three ways.

    Returns (live, unguarded, composed, zeros). Raises whatever the sweep raises -- the
    CALLER decides whether that is COULD NOT EVALUATE, because only the caller knows
    whether it can report the state distinctly.
    """
    unguarded = dividing_tests()
    zeros, composed = measured_zeros()
    live = [(fid, where, d, zeros[d]) for fid, where, _e, names in unguarded
            for d in names if d in zeros]
    return live, unguarded, composed, zeros


def main():
    unguarded = dividing_tests()          # for the COULD-NOT-EVALUATE message only; the
    try:                                  # judged run takes its copy from live_hazards()
        live, unguarded, composed, zeros = live_hazards()
    except Exception as e:                                   # pragma: no cover
        print("COULD NOT EVALUATE — the elevation generator did not run: %s" % e)
        print("The unguarded population is %d; the LIVE hazard was not measured, "
              "which is not a pass." % len(unguarded))
        return COULD_NOT_EVALUATE
    if not composed:
        print("COULD NOT EVALUATE — no style composed an elevation, so no zero was observed")
        return COULD_NOT_EVALUATE

    unattributable = unattributable_denominators()
    by_where = collections.Counter(w.split("[")[0] for _f, w, _e, _n in unguarded)
    print("%d style(s) composed an elevation; %d measurement name(s) come back ZERO on at "
          "least one" % (composed, len(zeros)))
    if unattributable:
        print("%d dividing test(s) whose denominator this walker CANNOT ATTRIBUTE — they are "
              "invisible to the live meter below, which is not a pass:" % len(unattributable))
        for fid, where, expr, why in unattributable[:10]:
            print("  ? %s %s: %s (%s)" % (fid, where, expr, why))
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
