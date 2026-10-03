#!/usr/bin/env python3
"""What a CLEAR fault verdict rests on: an instrument, not a test (WP-15.8's audit).

UNTIL WP-16.1, `core.check_measurements` judged each fault with a `_judge` that returned `clear`
when at least one of the fault's tests was EVALUATED and none of those failed. A test that wanted a
measurement nobody supplied was not in that list, so a fault whose governing test could not run
read clear on whatever secondary did: 142 of the 550 clear verdicts on the sixteen shipped plans,
measured at `a4abb85`. R4 (ruled 29 Sep 2026) made the governing test decide: a fault is clear only
where the primary, or the earned exception's bounds test, ran; otherwise it is could-not-evaluate,
carrying the tests that ran as `ran`; and a clear names every applicable secondary that did not run
as `secondaries_not_run`. So on a tree with R4 the `governing test not run` count below is 0 by
construction, and the two figures to read are `unjudged with evidence` (a could-not-evaluate row
carrying the tests that ran) and `clear naming an unrun secondary`. Run it on a control to see the
old shape (`--root`).

This instrument places every shipped plan on the deterministic engine, runs `plan_check.check` on
the placement exactly as the bench does, captures the one `check_measurements` call it makes, and
sorts every clear verdict by what it rests on:

  governing test ran        -- the primary, or the bounds_test of an exception this style earned;
  governing test not run    -- and why: `needed` (a measurement nobody supplied), `declined`
                               (its `applies_when` precondition is not met), `scoped` (it is
                               written for another style), `error`;
  a secondary not run       -- an applicable secondary that wanted a measurement nobody supplied.

`oq/a-fault-reads-clear-when-its-governing-test-could-not-run` carries the figures and the
rulings they need. Re-derive them with this file rather than quoting them:

    python3 tests/fault_clears.py                 # the census, one line per plan
    python3 tests/fault_clears.py --out X.json    # and every row, written where told
    python3 tests/fault_clears.py --root <tree>   # another checkout (a control)

It writes nothing unless told where, never inside the repository by default, and reads the corpus
through `modcache` in sorted order. The name does not begin `test_`, so pytest does not collect it.
"""
import argparse
import collections
import glob
import json
import os
import sys

sys.dont_write_bytecode = True


def census(root, engine="heuristic"):
    sys.path.insert(0, os.path.join(root, "build"))
    import modcache
    GEO = modcache.load("geometry", os.path.join(root, "build", "geometry.py"))
    PC = modcache.load("plan_check", os.path.join(root, "build", "plan_check.py"))
    CORE = modcache.load("tdlcore", os.path.join(root, "mcp_server", "core.py"))
    D = CORE._data()
    cap = {}
    orig = CORE.check_measurements

    def spy(meas, **kw):
        r = orig(meas, **kw)
        cap.update(r=r, meas=meas, style=kw.get("style"), context=kw.get("context"))
        return r

    CORE.check_measurements = spy
    out = {}
    try:
        paths = (sorted(glob.glob(os.path.join(root, "plans", "*.json")))
                 + sorted(glob.glob(os.path.join(root, "plans", "reference", "*.json"))))
        for p in paths:
            name = os.path.basename(p)[:-5]
            GEO._SOLVE_CACHE.clear()
            cap.clear()
            q = GEO.solve(json.load(open(p)), engine=engine)
            if q.get("error") or q.get("unsolved"):
                out[name] = {"error": str(q.get("error") or "unsolved")}
                continue
            PC.check(q)
            if "r" not in cap:
                out[name] = {"error": "plan_check made no check_measurements call"}
                continue
            r, meas, style, ctx = cap["r"], cap["meas"], cap["style"], cap["context"]
            rows = []
            for c in r.get("faults_clear", []):
                f = D["faults"][c["fault"]]
                gov = f["test"]
                exc = next((e for e in f.get("exceptions", []) if style and e.get("style") == style), None)
                if exc and exc.get("bounds_test") and CORE.grant_exception(exc, style, ctx)["verdict"] == "granted":
                    gov = exc["bounds_test"]
                ran = [x.get("expression") for x in c.get("results", [])]
                if gov.get("expression") in ran:
                    gov_state, missing = "ran", None
                elif not CORE._test_applies(gov, style, D):
                    gov_state, missing = "scoped", None
                else:
                    e = CORE._eval_test(gov, meas) or {"status": "none"}
                    gov_state = {"need_measurements": "needed", "not_applicable": "declined",
                                 "error": "error"}.get(e["status"], e["status"])
                    missing = e.get("missing")
                secs = [t for t in (f.get("secondary_tests") or []) if t and CORE._test_applies(t, style, D)]
                unrun = [t["expression"] for t in secs
                         if (CORE._eval_test(t, meas) or {}).get("status") == "need_measurements"]
                rows.append({"fault": c["fault"], "severity": f.get("severity"),
                             "governing": gov.get("expression"), "governing_state": gov_state,
                             "missing": missing, "ran": ran, "secondaries_not_run": unrun})
            # SINCE WP-16.1 (R4) a fault whose governing test could not run is could-not-evaluate
            # and carries what ran as `ran`. Those rows are the population this instrument was
            # written to count, and they are counted here on their own grain, so a tree before
            # the ruling (clears with the governing test not run) and a tree after it (unjudged
            # rows carrying evidence) can be compared plan by plan.
            with_ev = []
            for u in r.get("could_not_judge", []):
                if u.get("ran"):
                    f = D["faults"][u["fault"]]
                    with_ev.append({"fault": u["fault"], "severity": u.get("severity") or f.get("severity"),
                                    "governing": (u.get("governing_not_run") or {}).get("expression"),
                                    "missing": (u.get("governing_not_run") or {}).get("missing"),
                                    "ran": [x.get("expression") for x in u["ran"]]})
            out[name] = {"clear": len(rows), "rows": rows, "summary": r.get("summary"),
                         "unjudged_with_evidence": with_ev,
                         "clear_naming_an_unrun_secondary":
                             sum(1 for c in r.get("faults_clear", []) if c.get("secondaries_not_run"))}
    finally:
        CORE.check_measurements = orig
    return out


def summary(out):
    rows = [x for v in out.values() for x in v.get("rows", [])]
    gov = collections.Counter(x["governing_state"] for x in rows)
    sev = collections.Counter(x["severity"] for x in rows if x["governing_state"] == "needed")
    any_unrun = sum(1 for x in rows if x["governing_state"] == "needed" or x["secondaries_not_run"])
    faults = sorted({x["fault"] for x in rows if x["governing_state"] == "needed"})
    ev = [x for v in out.values() for x in v.get("unjudged_with_evidence", [])]
    tot = collections.Counter()
    for v in out.values():
        for k, n in (v.get("summary") or {}).items():
            tot[k] += n
    return {"plans": len(out), "clear": len(rows), "governing": dict(sorted(gov.items())),
            "governing_needed_by_severity": dict(sorted(sev.items())),
            "governing_needed_faults": faults,
            "any_applicable_test_not_run": any_unrun,
            "verdicts": dict(sorted(tot.items())),
            "unjudged_with_evidence": len(ev),
            "unjudged_with_evidence_by_severity":
                dict(sorted(collections.Counter(x["severity"] for x in ev).items())),
            "unjudged_with_evidence_faults": sorted({x["fault"] for x in ev}),
            "clear_naming_an_unrun_secondary":
                sum(v.get("clear_naming_an_unrun_secondary", 0) for v in out.values())}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--engine", default="heuristic")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = census(os.path.abspath(a.root), a.engine)
    for name, v in out.items():
        if "error" in v:
            print(f"  {name:36s} ERROR {v['error']}")
            continue
        n = sum(1 for x in v["rows"] if x["governing_state"] == "needed")
        sm = v.get("summary") or {}
        print(f"  {name:36s} clear {v['clear']:3d}   governing test not run (needed) {n:3d}   "
              f"unjudged with evidence {len(v.get('unjudged_with_evidence') or []):3d}   "
              f"p/c/u/na {sm.get('present')}/{sm.get('clear')}/{sm.get('unjudged')}/"
              f"{sm.get('not_applicable')}")
    s = summary(out)
    print(json.dumps(s, indent=1))
    if a.out:
        json.dump({"summary": s, "plans": out}, open(a.out, "w"), indent=1)
        print(f"  wrote {a.out}")


if __name__ == "__main__":
    main()
