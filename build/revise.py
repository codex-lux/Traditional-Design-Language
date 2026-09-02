#!/usr/bin/env python3
"""revise.py — the corrective revisions (WP-9.2).

    python3 build/revise.py plans/tidewater-georgian-careful.json [--rounds 6] [--engine auto|cp|heuristic]
                            [--candidates 250] [--budget-s 120] [--declared] [--parti <id>] [--json] [--out path]
    python3 build/revise.py --sweep [--engine heuristic] [--json --out sweep.json]

The loop Lucas asked for: the critic assesses the drawn house, the analyst (build/critique.py)
says what each finding means, and the generator fixes what a registered move (build/moves.py)
can fix -- in plan and in elevation -- round after round, until nothing it can do improves the
verdict. Every move names the finding it answered and the corpus sentence it executed; every
refusal is stated; what remains is handed to the architect with the corpus's own fix quoted.

THE RULES, each of which was paid for:

  · A move edits DECLARED fields only. After a move that changes the plan, the placement is
    stripped (build/openings.py::strip_placement, the exporter's own list) and re-solved, so the
    drawing stays a render of the data. A move that changes only the elevation's inputs keeps
    the placement and re-derives.
  · A round is ACCEPTED only if the key -- [fatal, serious, minor, faults present], over the
    non-info, non-advisory findings -- strictly decreases and no new fatal appears. Otherwise
    the round is rolled back BYTE-IDENTICALLY (compose.repair accepted the worse result on a
    non-improving round; there was no rollback at all), its (move, finding) pairs go TABU, and
    the loop continues with what is left rather than stopping on the first refused round --
    on the search engine one re-placement of noise is not a reason to give up.
  · One move per room per round. A batch that is refused is retried one move at a time, in
    severity order, so a good move is not lost to a bad neighbour and every refusal is
    attributed.
  · A lever (the proof, a wider search) is tried only when no declared move is left, alone,
    and through the same acceptance rule -- WP-7.4 measured 250 -> 2,000 candidates making
    plans worse on fatal, so a lever is never a default.
  · It stops on: no applicable move; the round cap; the budget (the accepted state is kept);
    a declared record it has seen before (oscillation); or nothing left but what belongs to the
    engine, the critic's own defects, or the architect.
  · It never touches a critic-suspect, never writes a placement key, never fills a judgment
    slot, never calls the plan good.

The result carries the critique before and after, every round with its attribution from the
stable finding ids (OQ 32), and the three lists that matter as much as the moves: what remains
by class, what was handed to the architect, and what was refused and why. The same report is
written onto the plan as `revision_report` (schema 0.4.0).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, path):
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


CR = _mod("critique", os.path.join(ROOT, "build", "critique.py"))
MV = _mod("moves", os.path.join(ROOT, "build", "moves.py"))
OP = _mod("openings", os.path.join(ROOT, "build", "openings.py"))
PC = _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))

SEV = {"fatal": 0, "serious": 1, "minor": 2, "advisory": 3, "info": 4}
MAX_MOVES_PER_ROUND = 6


def _hash(plan):
    """The DECLARED record's fingerprint: the placement stripped from a copy, keys sorted."""
    return hashlib.sha256(json.dumps(OP.strip_placement(copy.deepcopy(plan)), sort_keys=True).encode()).hexdigest()[:16]


def _ids(crit, severity=None):
    return {f["id"] for f in crit["check"]["findings"]
            if f["severity"] not in ("info", "advisory") and (severity is None or f["severity"] == severity)}


def _improves(new, old):
    """Strictly better key, and no fatal that was not there before -- and JUDGED. A critique
    whose placement could not be evaluated reports the DECLARED key, which carries no drawn
    finding and is lower for that reason alone; the audit's own CP-SAT measurement accepted
    the Tidewater plan at [0, 22, 58, 19] with no placement at all after a proof timed out.
    Unjudged is not passed, and in this loop it is not better either (WP-9.4)."""
    if (new.get("placement") or {}).get("could_not_evaluate"):
        return False
    if not (new["key"] < old["key"]):
        return False
    return not (_ids(new, "fatal") - _ids(old, "fatal"))


def _choose(crit, tabu, limit=MAX_MOVES_PER_ROUND):
    """(move id, issue) pairs for this round: severity first, one per room, registry order
    within an issue, nothing tabu."""
    picks, rooms = [], set()
    issues = sorted(crit["assessment"]["actionable"], key=lambda i: (SEV.get(i["severity"], 9), i["id"]))
    for i in issues:
        slot = i.get("room") or i["id"]
        if slot in rooms:
            continue
        for mid in i.get("moves") or []:
            if (mid, i["id"]) in tabu:
                continue
            picks.append((mid, i))
            rooms.add(slot)
            break
        if len(picks) >= limit:
            break
    return picks


def _attrib(before, after):
    b, a = _ids(before), _ids(after)
    return {"cleared": sorted(b - a), "persisted": sorted(b & a), "opened": sorted(a - b)}


def revise(plan, rounds=6, engine="auto", candidates=250, budget_s=None, brief=None, place=True,
           parti=None, on_round=None, C=None, seed=7, time_limit_s=25.0):
    core = _mod("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))
    C = C or PC.load_corpus()
    parti_rec = core.load_parti(parti) if isinstance(parti, str) else parti
    plan = core.copy_json(plan)
    ctx = {"parti": parti_rec, "must_have": list((brief or {}).get("must_have") or []),
           "candidates": candidates, "engine": engine}
    t0 = time.perf_counter()
    log, tabu, levers_tried = [], set(), set()
    # the live tabu set rides in ctx so moves.answering can offer a successor move once the
    # move before it has been refused by measurement (the session's audit: three `_AFTER`
    # moves were unreachable after their predecessor was rolled back)
    ctx["tabu"] = tabu

    def _report(rnd):
        # EVERY logged round is reported, the refused-lever and nothing-applied rounds
        # included: WP-9.3's revise job emitted no `round` event on a plan whose only round
        # was a refused proof, because two of the four paths that log a round skipped the
        # callback. One reporter, so a fifth path cannot skip it either. And the reader's
        # seam may not discard the loop's work: a callback that raises is recorded on the
        # round and the loop continues (WP-9.4 -- an exception in on_round killed the job).
        log.append(rnd)
        if on_round:
            try:
                on_round(rnd)
            except Exception as exc:
                rnd["on_round_error"] = f"{type(exc).__name__}: {exc}"[:200]

    def _crit(p):
        return CR.critique(p, engine=ctx["engine"], candidates=ctx["candidates"], parti=parti_rec,
                           place=place, seed=seed, time_limit_s=time_limit_s, C=C, ctx=ctx)

    crit = _crit(plan)
    plan = crit["plan"]                      # carries the placement from here on
    # the placed loop needs a placed house to hold its rounds against; a first placement that
    # could not be evaluated is stated and the loop does not run on a declared key wearing a
    # placed mode's name (WP-9.4)
    placement_unjudged = place and (crit.get("placement") or {}).get("could_not_evaluate")
    # a COPY: `crit` is rebound only on an accepted round, so on a run that accepts nothing
    # `before` and `after` were one dict under two names, and the bench reads both (WP-9.4)
    before = copy.deepcopy(crit)
    seen = {_hash(plan)}
    stop = None
    n = 0
    if placement_unjudged:
        stop = "placement-could-not-be-evaluated"
        rounds = 0
    while n < rounds:
        if budget_s is not None and time.perf_counter() - t0 > budget_s:
            stop = "budget"
            break
        n += 1
        picks = _choose(crit, tabu)
        rnd = {"n": n, "engine": crit["engine"]["ran"], "candidates": ctx["candidates"],
               "key_before": list(crit["key"]), "moves": [], "accepted": False}
        # THE PROOF COMES FIRST WHERE IT IS TO BE HAD. Measured on the first run of this loop:
        # on the search engine every declared move -- the pantry to 9.1 ft, the stair hall to
        # 9.6 -- was judged against a fresh heuristic re-placement and "made the plan worse"
        # (fatal 3 -> 9 on one), because the search scrambles; then the proof cleared all three
        # fatals in one round and every refused move stayed tabu. A declared move is judged
        # against the engine the record will be drawn with, so when the placement is the
        # search's and CP-SAT is importable, the proof is asked for before any declared move
        # and the tabu earned under the search is forgotten when the engine changes.
        prove_first = (crit["assessment"]["placement"] and crit["engine"]["ran"] != "cp-sat"
                       and "prove-it" not in levers_tried
                       and crit["assessment"]["placement"][0].get("move") == "prove-it")
        if not picks or prove_first:
            # a lever, alone: the proof first, or when no declared move is left
            lever = None
            if crit["assessment"]["placement"]:
                wanted = crit["assessment"]["placement"][0].get("move")
                if wanted and wanted not in levers_tried:
                    lever = wanted
            if lever is None:
                stop = "converged" if not crit["assessment"]["actionable"] else "no-applicable-move"
                n -= 1
                break
            levers_tried.add(lever)
            res = MV.apply(lever, plan, crit["assessment"]["placement"][0]["finding"], C, ctx)
            if "refused" in res:
                rnd["moves"].append({"move": lever, "refused": res["refused"],
                                     "finding": crit["assessment"]["placement"][0]["id"]})
                _report(rnd)
                continue
            saved = dict(ctx)
            ctx.update(res["lever"])
            trial = OP.strip_placement(copy.deepcopy(plan))
            new = _crit(trial)
            entry = {"move": lever, "finding": crit["assessment"]["placement"][0]["id"],
                     "basis": res["basis"], "lever": res["lever"], "log": res["log"]}
            if _improves(new, crit):
                rnd.update(accepted=True, key_after=list(new["key"]), **_attrib(crit, new))
                # the verdict rides on the MOVE ENTRY as well as on the round: the summary,
                # the sweep, the CLI and the bench's round event all read the entry, and until
                # WP-9.4 an accepted proof counted as 0 moves applied and a proof rolled back
                # by measurement read as "applied; its finding persisted"
                entry.update(accepted=True, cleared=True)
                engine_changed = new["engine"]["ran"] != crit["engine"]["ran"]
                plan, crit = new["plan"], new
                # a refusal measured under the old engine says nothing about the new one --
                # and ONLY then: `search-harder` changes the candidate count, not the engine,
                # and a refusal under 250 candidates says the same thing under 1,000
                if tabu and engine_changed:
                    rnd["tabu_forgotten"] = len(tabu)
                    tabu.clear()
            else:
                rnd.update(key_after=list(new["key"]), refused_by_measurement=True)
                entry.update(cleared=False, refused_by_measurement=True, key_after=list(new["key"]))
                ctx.clear(); ctx.update(saved)
            rnd["moves"].append(entry)
            rnd["engine_after"] = new["engine"]["ran"]
            _report(rnd)
            continue

        over_budget = lambda: budget_s is not None and time.perf_counter() - t0 > budget_s
        snapshot = copy.deepcopy(plan)
        applied = []
        for mid, issue in picks:
            res = MV.apply(mid, plan, issue["finding"], C, ctx)
            if "refused" in res:
                tabu.add((mid, issue["id"]))
                rnd["moves"].append({"move": mid, "finding": issue["id"], "refused": res["refused"]})
                continue
            applied.append((mid, issue, res))
        if not applied:
            _report(rnd)
            continue
        replace = any(r["requires"] == "re-place" for _m, _i, r in applied)
        if replace:
            OP.strip_placement(plan)
        new = _crit(plan)

        def _record(entries, new, accepted):
            att = _attrib(crit, new)
            for mid, issue, res in entries:
                rnd["moves"].append({"move": mid, "finding": issue["id"], "basis": res.get("basis"),
                                     "tier": res.get("tier"), "kind": res.get("kind"),
                                     "authority": res.get("authority"), "requires": res.get("requires"),
                                     "changed": res.get("changed"), "log": res.get("log"),
                                     "cleared": accepted and issue["id"] in att["cleared"],
                                     "accepted": accepted})
            return att

        if _improves(new, crit):
            att = _record(applied, new, True)
            rnd.update(accepted=True, key_after=list(new["key"]), re_placed=replace, **att)
            plan, crit = new["plan"], new
        else:
            # roll the batch back, then try each move alone in severity order
            rnd["batch_refused_by_measurement"] = {"key_after": list(new["key"])}
            plan = copy.deepcopy(snapshot)
            # the batch wrote into the object `crit["plan"]` names; after the rollback the
            # critique has to point at the restored record, or `critique_after["plan"]` is
            # a stripped, half-moved house that is not the plan returned (the session's audit)
            crit["plan"] = plan
            accepted_one = None
            tried = set()
            for mid, issue, _res in applied:
                if over_budget():
                    # the budget binds INSIDE a round too: a batch of six retried one at a
                    # time is six more solves, and compose runs this on every pick. Every
                    # move the cut leaves untried is an ENTRY, so the count and the reader
                    # see it (the session's audit: work rolled back and recorded nowhere)
                    for m2, i2, _r in applied:
                        tabu.add((m2, i2["id"]))
                        if (m2, i2["id"]) not in tried:
                            rnd["moves"].append({"move": m2, "finding": i2["id"],
                                                 "refused": "the budget was spent before this move could be retried alone"})
                    rnd["budget_cut_retries"] = True
                    break
                tried.add((mid, issue["id"]))
                trial = copy.deepcopy(snapshot)
                res = MV.apply(mid, trial, issue["finding"], C, ctx)
                if "refused" in res:
                    tabu.add((mid, issue["id"]))
                    rnd["moves"].append({"move": mid, "finding": issue["id"], "refused": res["refused"]})
                    continue
                if res["requires"] == "re-place":
                    OP.strip_placement(trial)
                new1 = _crit(trial)
                if _improves(new1, crit):
                    att = _record([(mid, issue, res)], new1, True)
                    rnd.update(accepted=True, key_after=list(new1["key"]),
                               re_placed=res["requires"] == "re-place", **att)
                    plan, crit = new1["plan"], new1
                    accepted_one = mid
                    break
                tabu.add((mid, issue["id"]))
                rnd["moves"].append({"move": mid, "finding": issue["id"], "refused_by_measurement": True,
                                     "key_after": list(new1["key"]), "log": res.get("log")})
            if accepted_one is None:
                for mid, issue, _res in applied:
                    tabu.add((mid, issue["id"]))
                rnd["key_after"] = list(crit["key"])
        rnd.setdefault("key_after", list(crit["key"]))
        _report(rnd)
        h = _hash(plan)
        if rnd["accepted"] and h in seen:
            stop = "oscillation"
            break
        seen.add(h)
    else:
        # the while/else: the loop ran out of rounds without a break. With rounds=0 it never
        # started, and "round-cap" would be a lie about a cap that was never reached.
        stop = stop or ("round-cap" if rounds > 0 else "no-rounds")

    # the brief's own area discipline, once, after the loop -- reclaim's, not re-implemented
    # -- and under the loop's own rule. The sweep's first run handed back tower-villa at
    # [3, 36, 46, 0] -> [4, 23, 49, 0]: every round had refused a new fatal and the reclaim
    # after the last round re-placed the house and opened one. The area discipline does not
    # outrank the rule the rounds were held to, so a reclaim that opens a fatal is rolled back
    # and SAID; the report carries both keys rather than the flattering one.
    reclaimed = None
    if brief and brief.get("target_area_sf"):
        CO = _mod("compose", os.path.join(ROOT, "build", "compose.py"))
        kept, kept_crit = copy.deepcopy(plan), crit
        res, clog = CO.reclaim(plan, brief["target_area_sf"], brief.get("area_tolerance", 0.12), crit["check"])
        if clog:
            OP.strip_placement(plan)
            crit = _crit(plan)
            plan = crit["plan"]
            reclaimed = {"log": clog, "key_before": list(kept_crit["key"]), "key_after": list(crit["key"]),
                         "rolled_back": False}
            unjudged = (crit.get("placement") or {}).get("could_not_evaluate")
            # the same rule the rounds were held to, one screen below _improves: an unjudged
            # re-placement is not lower, and a rise in fatal OR serious is a worse house; only
            # the minor axis may pay for the brief's area (the session's audit found this
            # branch comparing fatals alone with no unjudged guard)
            worse = unjudged or crit["key"][:2] > kept_crit["key"][:2]
            if worse:
                reclaimed["rolled_back"] = True
                reclaimed["why"] = ((f"the placement after reclaim could not be evaluated ({unjudged}); "
                                     f"an unjudged key is not a lower one") if unjudged else
                                    (f"reclaim raised fatal or serious on this engine ({kept_crit['key']} -> "
                                     f"{crit['key']}); the area discipline does not outrank the rule "
                                     f"every round was held to")) + ", so the accepted state is kept"
                plan, crit = kept, kept_crit
                crit["plan"] = plan          # reclaim wrote into the old object; see the rollback above

    after = crit
    assert after["plan"] is plan, "the critique returned must be of the record returned"
    remaining = {c: [{"id": i["id"], "severity": i["severity"], "statement": i["statement"],
                      **({"lever": i.get("lever")} if c == "placement" else {}),
                      **({"move": i.get("move")} if c == "actionable" else {})}
                     for i in after["assessment"][c]]
                 for c in ("actionable", "placement", "critic_suspect", "architect", "advisory")}
    handed = [{"id": i["id"], "severity": i["severity"], "statement": i["statement"], "why": i.get("why"),
               "fix_right": i.get("fix_right"), "fix_cheap": i.get("fix_cheap"), "rule_why": i.get("rule_why")}
              for i in after["assessment"]["architect"]]
    suspects = [{"id": i["id"], "statement": i["statement"], "evidence": i["evidence"]}
                for i in after["assessment"]["critic_suspect"]]
    refused = [m for r in log for m in r["moves"] if m.get("refused") or m.get("refused_by_measurement")]
    applied_n = sum(1 for r in log for m in r["moves"] if m.get("accepted"))
    report = {"schema": "0.4.0", "mode": "placed" if place else "declared",
              "engine": {"requested": engine, "final": after["engine"]["ran"], "candidates": ctx["candidates"]},
              "rounds": log, "stop_reason": stop,
              "key_before": list(before["key"]), "key_after": list(after["key"]),
              "remaining": remaining, "handed_to_architect": handed, "refused": refused,
              "suspects": suspects, "reclaimed": reclaimed,
              "placement_unjudged": placement_unjudged or None,
              "summary": {"rounds": len(log), "moves_applied": applied_n, "moves_refused": len(refused),
                          "key_before": list(before["key"]), "key_after": list(after["key"]),
                          "stop_reason": stop, "seconds": round(time.perf_counter() - t0, 1)},
              "note": ("Every move names the finding it answered and the sentence it executed; every "
                       "refusal is stated; what remains is the engine's, the critic's own, or the "
                       "architect's, and the loop says which. A lower key is not a good plan.")}
    plan["revision_report"] = report
    return {"plan": plan, "report": report, "critique_before": before, "critique_after": after,
            "rounds": log, "handed_to_architect": handed, "refused": refused, "suspects": suspects,
            "stop_reason": stop, "key_before": report["key_before"], "key_after": report["key_after"]}


# ------------------------------------------------------------------ the sweep
def sweep(engine="heuristic", rounds=6, candidates=250, budget_s=None, partis=None):
    """Every parti composed against its first native style (check_partis.py's own brief), plus
    both shipped plans, revised; before/after keys by class and per-move clear counts."""
    import glob
    CO = _mod("compose", os.path.join(ROOT, "build", "compose.py"))
    rows, per_move = [], {}
    brief_of = lambda style: {"id": "check", "name": "check", "style": style,
                              "target_area_sf": 2600, "bedrooms": 3, "bathrooms": 2.0,
                              "context": {"climate_zone": "3A", "lot_width_ft": 120, "entrance_faces": "S",
                                          "jurisdiction": "IRC model text, advisory", "budget_tier": "custom"},
                              "household": "check"}
    jobs = []
    for f in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))):
        p = json.load(open(f, encoding="utf-8"))
        if partis and p["id"] not in partis:
            continue
        style = p["styles"][0]
        plan, _log, _p = CO.instantiate(p["id"], brief_of(style))
        jobs.append((f"{p['id']} / {style}", plan, p, brief_of(style)))
    for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
        jobs.append((pid, json.load(open(os.path.join(ROOT, "plans", f"{pid}.json"), encoding="utf-8")), None, None))
    for label, plan, parti_rec, brief in jobs:
        try:
            r = revise(plan, rounds=rounds, engine=engine, candidates=candidates, budget_s=budget_s,
                       brief=brief, parti=parti_rec, place=True)
        except Exception as exc:
            rows.append({"plan": label, "error": f"{type(exc).__name__}: {exc}"})
            continue
        s = r["report"]["summary"]
        row = {"plan": label, "key_before": s["key_before"], "key_after": s["key_after"],
               "rounds": s["rounds"], "applied": s["moves_applied"], "refused": s["moves_refused"],
               "stop": s["stop_reason"], "seconds": s["seconds"],
               "remaining": {c: len(v) for c, v in r["report"]["remaining"].items()}}
        rows.append(row)
        for rd in r["rounds"]:
            for m in rd["moves"]:
                d = per_move.setdefault(m["move"], {"applied": 0, "cleared": 0, "refused": 0})
                if m.get("accepted"):
                    d["applied"] += 1
                    d["cleared"] += 1 if m.get("cleared") else 0
                elif m.get("refused") or m.get("refused_by_measurement"):
                    d["refused"] += 1
    never = [m["id"] for m in MV.registry()["moves"] if m["id"] not in per_move]
    return {"engine": engine, "rounds": rounds, "candidates": candidates, "plans": rows,
            "per_move": per_move, "never_fired": never}


# ------------------------------------------------------------------ cli
def _print(r):
    s = r["report"]["summary"]
    print(f"\n  {r['plan'].get('name') or r['plan']['id']}   key {s['key_before']} -> {s['key_after']}   "
          f"{s['rounds']} round(s), {s['moves_applied']} move(s) applied, {s['moves_refused']} refused, "
          f"stopped: {s['stop_reason']}   {s['seconds']} s")
    for rd in r["rounds"]:
        tag = "ACCEPTED" if rd["accepted"] else "rolled back"
        print(f"\n  round {rd['n']}  [{rd['engine']}]  {rd['key_before']} -> {rd.get('key_after')}  {tag}")
        for m in rd["moves"]:
            if m.get("refused"):
                print(f"      x {m['move']:<40} refused: {m['refused'][:100]}")
            elif m.get("refused_by_measurement"):
                print(f"      x {m['move']:<40} made the plan worse ({m.get('key_after')}): {(m.get('log') or '')[:80]}")
            else:
                print(f"      {'+' if m.get('cleared') else '~'} {m['move']:<40} {(m.get('log') or '')[:100]}")
        if rd.get("opened"):
            print(f"      opened: {', '.join(rd['opened'][:6])}")
    rem = r["report"]["remaining"]
    print(f"\n  REMAINING  placement {len(rem['placement'])} · suspect {len(rem['critic_suspect'])} · "
          f"architect {len(rem['architect'])} · advisory {len(rem['advisory'])} · actionable-but-tabu {len(rem['actionable'])}")
    for h in r["handed_to_architect"][:12]:
        print(f"    [{h['severity']:<7}] {h['statement'][:100]}")
    if len(r["handed_to_architect"]) > 12:
        print(f"    ... and {len(r['handed_to_architect']) - 12} more")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", nargs="?")
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--engine", default="auto", choices=["auto", "cp", "heuristic"])
    ap.add_argument("--candidates", type=int, default=250)
    ap.add_argument("--budget-s", type=float)
    ap.add_argument("--declared", action="store_true")
    ap.add_argument("--parti")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--sweep", action="store_true")
    a = ap.parse_args()
    if a.sweep:
        res = sweep(engine=a.engine, rounds=a.rounds, candidates=a.candidates, budget_s=a.budget_s)
        if a.out:
            json.dump(res, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        if a.json and not a.out:
            print(json.dumps(res, indent=1, ensure_ascii=False)); return
        print(f"\n  sweep on {res['engine']}, {res['rounds']} rounds, {res['candidates']} candidates\n")
        for row in res["plans"]:
            if "error" in row:
                print(f"  {row['plan']:<48} ERROR {row['error'][:80]}"); continue
            print(f"  {row['plan']:<48} {str(row['key_before']):<18} -> {str(row['key_after']):<18} "
                  f"{row['rounds']}r {row['applied']}+ {row['refused']}x  {row['stop']:<18} {row['seconds']:>6.1f}s")
        print("\n  per move:")
        for mid, d in sorted(res["per_move"].items()):
            print(f"    {mid:<42} applied {d['applied']:>3}  cleared {d['cleared']:>3}  refused {d['refused']:>3}")
        print(f"\n  never fired: {', '.join(res['never_fired']) or 'none'}\n")
        return
    if not a.plan:
        ap.error("a plan, or --sweep")
    plan = json.load(open(a.plan, encoding="utf-8"))
    r = revise(plan, rounds=a.rounds, engine=a.engine, candidates=a.candidates, budget_s=a.budget_s,
               place=not a.declared, parti=a.parti)
    if a.out:
        json.dump(r["plan"], open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if a.json:
        print(json.dumps(r["report"], indent=1, ensure_ascii=False)); return
    _print(r)


if __name__ == "__main__":
    main()
