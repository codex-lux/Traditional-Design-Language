#!/usr/bin/env python3
"""Which houses the composer returns, and on what: an instrument, not a test (WP-16.1).

`compose.compose` ranks its candidates and returns the first few. Its order has moved three times
in two phases for reasons the counts beside it did not show: WP-13.3 and WP-13.5 moved which
diagrams a Tidewater Georgian brief is offered, and WP-15.8's audit found the native diagram
returning to the set through verdicts that had become unjudged. Phase 16 changes two of the things
the ranking reads (R4: a fault is clear only where its governing test ran; R13: an unjudged fatal
breaks ties against a candidate). This records, per brief, what the composer returns and every
figure the ranking read, so a movement can be attributed rather than noticed.

For every brief in `briefs/` it composes with `revise=False` (the placed loop runs after the
ranking and on a wall clock) and with the DECLARED loop's wall-clock budget lifted, because
`compose.repair` stops at 6 s and a set that depends on how fast this machine is today is not a
measurement. Each returned candidate carries:

  rank, parti                 -- the returned order
  fatal                       -- judged fatal findings (`counts.fatal`)
  unjudged_fatal              -- fatal faults the corpus could not judge on it, by id
  fault_summary               -- present / clear / unjudged / not_applicable
  solecisms_share, score      -- the axis R4 can move, and the composite it feeds
  demerits

    python3 tests/compose_sets.py                 # one line per returned candidate
    python3 tests/compose_sets.py --out X.json    # and the whole record, written where told
    python3 tests/compose_sets.py --root <tree>   # another checkout (a control)

It writes nothing unless told where, never inside the repository by default. The name does not
begin `test_`, so pytest does not collect it.
"""
import argparse
import glob
import json
import os
import sys

sys.dont_write_bytecode = True


def _unjudged_fatal(cand, style, D):
    """The fatal faults on this candidate's `fault_unjudged` list, by id.

    Read off the FAULT RECORD's severity for this style, not off the row, so a tree whose rows
    carry no severity (every tree before WP-16.1) is measured by the same rule as one that does."""
    out = []
    for row in (cand.get("_check") or {}).get("fault_unjudged") or []:
        f = D["faults"].get(row.get("fault"))
        if not f:
            continue
        sev = next((s["severity"] for s in f.get("severity_by_style", [])
                    if s.get("style") == style), f.get("severity"))
        if sev == "fatal":
            out.append(row["fault"])
    return sorted(out)


def census(root, candidates=4):
    sys.path.insert(0, os.path.join(root, "build"))
    import modcache
    CO = modcache.load("compose", os.path.join(root, "build", "compose.py"))
    CORE = modcache.load("tdlcore", os.path.join(root, "mcp_server", "core.py"))
    D = CORE._data()
    orig_repair = CO.repair
    orig_score = CO.score_candidate
    orig_inst = CO.instantiate
    seen, parti_of, scored = {}, {}, []

    def repair(plan, rounds=6, budget_s=6.0):
        # the declared loop, with its wall clock lifted: rounds still bound it
        return orig_repair(plan, rounds=rounds, budget_s=None)

    def instantiate(parti_id, brief):
        r = orig_inst(parti_id, brief)
        parti_of[id(r[0])] = parti_id
        return r

    def score_candidate(res, plan, brief, *a, **kw):
        # keep the plan_check result each card was scored on, keyed by the plan object, so the
        # unjudged fatals are read off the same result the ranking read -- and every candidate
        # SCORED, not only the ones returned, because a movement in the returned set is
        # explained by the ones that were not
        card = orig_score(res, plan, brief, *a, **kw)
        seen[id(plan)] = res
        sol = next((x for x in card.get("score_axes") or [] if x.get("axis") == "solecisms"), {})
        scored.append({"parti": parti_of.get(id(plan)),
                       "fatal": (res.get("counts") or {}).get("fatal", 0),
                       "fatal_findings": sorted(
                           f"{f.get('kind')}:{f.get('fault') or f.get('rule') or f.get('room') or ''}"
                           for f in res.get("findings") or [] if f.get("severity") == "fatal"),
                       "unjudged_fatal": _unjudged_fatal({"_check": res}, brief.get("style"), D),
                       "fault_summary": res.get("fault_summary"),
                       "solecisms_share": sol.get("share"), "score": card.get("score")})
        return card

    CO.repair = repair
    CO.score_candidate = score_candidate
    CO.instantiate = instantiate
    out = {}
    try:
        for p in sorted(glob.glob(os.path.join(root, "briefs", "*.json"))):
            name = os.path.basename(p)[:-5]
            brief = json.load(open(p))
            seen.clear(); parti_of.clear(); del scored[:]
            res = CO.compose(brief, candidates=candidates, revise=False)
            rows = []
            for i, c in enumerate(res.get("candidates") or []):
                chk = seen.get(id(c.get("plan"))) or {}
                c["_check"] = chk
                axes = {a.get("axis"): a for a in (c.get("score_axes") or [])
                        if isinstance(a, dict)}
                sol = axes.get("solecisms") or {}
                rows.append({
                    "rank": i + 1, "parti": c.get("parti"),
                    "fatal": (c.get("counts") or {}).get("fatal", 0),
                    "unjudged_fatal": _unjudged_fatal(c, brief.get("style"), D),
                    "fault_summary": chk.get("fault_summary"),
                    "solecisms_share": sol.get("share"),
                    "score": c.get("score"), "demerits": c.get("demerits"),
                    "named_by_brief": c.get("named_by_brief")})
            out[name] = {"style": brief.get("style"), "returned": rows,
                         "scored": sorted(scored, key=lambda r: r["parti"] or "")}
    finally:
        CO.repair = orig_repair
        CO.score_candidate = orig_score
        CO.instantiate = orig_inst
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--candidates", type=int, default=4)
    ap.add_argument("--out")
    a = ap.parse_args()
    out = census(os.path.abspath(a.root), a.candidates)
    for name, v in out.items():
        print(f"{name} ({v['style']})")
        returned = [r["parti"] for r in v["returned"]]
        for r in sorted(v["scored"], key=lambda r: (r["fatal"], -(r["score"] or 0))):
            fs = r["fault_summary"] or {}
            print(f"     {'*' if r['parti'] in returned else ' '} {r['parti']:34s} fatal {r['fatal']}"
                  f"  unjudged fatal {len(r['unjudged_fatal'])}  score {r['score']}  faults "
                  f"p/c/u/na {fs.get('present')}/{fs.get('clear')}/{fs.get('unjudged')}/"
                  f"{fs.get('not_applicable')}")
        for r in v["returned"]:
            fs = r["fault_summary"] or {}
            print(f"  {r['rank']}. {r['parti']:34s} fatal {r['fatal']}  unjudged fatal "
                  f"{len(r['unjudged_fatal'])}  faults p/c/u/na {fs.get('present')}/"
                  f"{fs.get('clear')}/{fs.get('unjudged')}/{fs.get('not_applicable')}  "
                  f"solecisms {r['solecisms_share']}  score {r['score']}")
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)
        print(f"  wrote {a.out}")


if __name__ == "__main__":
    main()
