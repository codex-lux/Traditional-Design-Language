#!/usr/bin/env python3
"""critique.py — the analyst (WP-9.1).

`plan_check.check` is the critic: it says what is wrong. This file says what each finding
MEANS to a generator that wants to fix it, which is a different question and one nothing had
ever answered: a finding carried a room and a sentence, and the one consumer that acted on
findings (compose.repair) re-read the sentence with string slicing and acted on three of
fourteen layers.

    python3 build/critique.py plans/tidewater-georgian-careful.json [--engine auto|cp|heuristic]
                                                                   [--candidates N] [--declared]
                                                                   [--json]

It places the record ONCE (or reuses the placement it carries -- the same rule
workbench/server/corpus.py::_placed and export_dxf._solved_copy keep, so a bench plan is never
re-solved out from under its reader), runs the critic on the placed record so the section,
the roof and the elevation are of THAT placement (one building; WP-9.1 fixed the critic to do
this), and sorts every non-info finding into exactly one class, first match wins:

  advisory        the code layer -- advisory and jurisdictional by ruling, unscored.
  placement       the DECLARED record would have satisfied the need and the engine did not:
                  a stair whose declared hall would have held it, a passage declared at 6 ft
                  and drawn at 4, a room stranded because the search left its declared doors
                  no wall. The lever is the engine, the candidate count, or the CP conflict
                  set -- never a change to the record, which said the right thing.
  critic-suspect  the fault's failing test reads a number the elevation GENERATOR states as
                  its own constant (build/critic_suspects.py), or an editorial entry names
                  the pair. Evidence attached. NEVER acted on: a loop that obeyed these would
                  spend its rounds chasing the generator.
  actionable      a registered move (build/moves.py, WP-9.2) answers it and its precondition
                  holds on the declared record. Names the move.
  architect       everything else -- topology, adjacency, a judgment slot, a fault whose fix
                  the corpus states in words a generator cannot execute. Handed over with the
                  fault's own `right` fix quoted, or the rule's own `why`.

`info` findings are not classified: they are the critic saying COULD NOT EVALUATE, and they are
listed under `could_not_evaluate` with their rule ids so nothing reads their absence as a pass.

The result carries `key` -- [fatal, serious, minor, faults present] -- which is the whole of what
build/revise.py accepts or rolls back a round on.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, path):
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


PC = _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
GEO = _mod("geometry", os.path.join(ROOT, "build", "geometry.py"))
CS = _mod("critic_suspects", os.path.join(ROOT, "build", "critic_suspects.py"))

CLASSES = ("actionable", "placement", "critic_suspect", "architect", "advisory")


def _cp_available():
    try:
        from ortools.sat.python import cp_model  # noqa: F401
        return True
    except Exception:
        return False


def _registry():
    """The move registry, when WP-9.2 has shipped it; None before. The analyst classifies
    the same way either side of that line -- an issue a move WOULD answer is named as such
    -- but it may only call an issue `actionable` when the move exists."""
    path = os.path.join(ROOT, "build", "moves.py")
    if not os.path.exists(path):
        return None
    return _mod("moves", path)


def has_placement(plan):
    return any(r.get("geometry") for lv in plan.get("levels", []) for r in lv.get("rooms", []))


def key_of(check):
    """[fatal, serious, minor, faults present] -- lexicographic, lower is better. `info` and
    `advisory` are outside it: neither is a failure."""
    c = check.get("counts") or {}
    return [c.get("fatal", 0), c.get("serious", 0), c.get("minor", 0),
            (check.get("fault_summary") or {}).get("present", 0)]


# ------------------------------------------------------------------ the levers
def _lever(plan, finding, ctx=None):
    """What would change a placement-class finding, named. Never a record edit.

    The search asked for BY NAME (`engine="heuristic"`: the bench's drag path, check_all's
    bounded composer run) is a request not to spend a proof, and the lever honours it here
    rather than one step later: the first version named `prove-it`, the loop asked for it
    first, `_prove_it` refused it, and every heuristic-by-name run spent its first round on
    that refusal (the session's audit: `--revise-rounds 2` bought one round)."""
    engine = finding.get("engine") or ((plan.get("geometry_report") or {}).get("solver") or {}).get("engine")
    gr = plan.get("geometry_report") or {}
    if engine != "cp-sat":
        if _cp_available() and (ctx or {}).get("engine") != "heuristic":
            return {"lever": "engine", "move": "prove-it", "engine": engine,
                    "why": "the search placed this; CP-SAT holds the record's declared doors and "
                           "sizes as hard facts (WP-6.3: Tidewater 3 stranded rooms -> 0)"}
        return {"lever": "candidates", "move": "search-harder", "engine": engine,
                "why": "the search placed this and CP-SAT is not importable here; a wider pool "
                       "may hold the placement 250 candidates did not (WP-7.4, with its caveat)"}
    inf = gr.get("infeasible")
    if inf:
        return {"lever": "conflict-set", "engine": engine,
                "conflicts": list(inf.get("conflicts") or [])[:8],
                "why": "CP-SAT proved the record's declared facts cannot all hold; this is the "
                       "labelled least-bad relaxation, and the conflict set names what to change"}
    return {"lever": None, "engine": engine,
            "why": "CP-SAT proved this placement; what the record declares is what yields it, "
                   "and no engine setting changes that"}


# ------------------------------------------------------------------ classification
def _room(plan, rid):
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            if r["id"] == rid:
                return r
    return None


def _intended_move(plan, f):
    """The move id that answers this finding on the DECLARED record, or None with a reason.
    This is the analyst's reading; whether the move EXISTS is the registry's business."""
    k = f.get("kind")
    layer = f["layer"]
    room = _room(plan, f.get("room")) if f.get("room") else None
    if layer == "furniture" and k == "furniture-fit":
        return "widen-for-furniture", None
    if layer == "room":
        if k == "width-below-floor":
            return "widen-to-room-floor", None
        if k == "area-below-band":
            return "grow-to-band-floor", None
        if k == "ceiling-below-min":
            return None, "the ceiling comes from the style's own kit; a room type wanting more is the catalogue and the kit disagreeing, which is a judgment"
        return None, "a room above its band is a note to confirm, not a defect to shrink"
    if layer == "daylight":
        ext = f.get("exterior_walls") or (room or {}).get("exterior_walls") or []
        if k == "daylight-depth":
            head_ok = f.get("need_head_ft") is not None and f.get("ceiling_ft") \
                and f["need_head_ft"] <= f["ceiling_ft"] - 0.5
            if head_ok:
                return "raise-window-head", None
            opp = {"N": "S", "S": "N", "E": "W", "W": "E"}
            lit = set(f.get("lit_walls") or [])
            if any(opp.get(w) in ext for w in lit) and not any(opp.get(w) in lit for w in lit):
                return "light-the-far-end", None
            return None, "the head cannot reach the back of the room below the ceiling and no opposite exterior wall is declared; the back of the room is a service zone or the room is too deep -- the architect's call"
        if k in ("no-window", "sides-lit"):
            if ext:
                return "give-the-room-a-window", None
            return None, "the room declares no exterior wall to put a window in"
        return None, "the depth rule does not govern this room type"
    if layer == "style":
        if k == "variant-forbidden":
            if f.get("canonical"):
                return "replace-forbidden-declared-variant", None
            return None, "the cascade delivers no single canonical variant for this slot; choosing one is a judgment"
        if k == "slot-forbidden":
            return None, "the style forbids the slot outright; whether to withdraw the declaration is the author's"
        if k == "constraint-present":
            expr = f.get("expression") or ""
            if "passage_width" in expr:
                return "passage-to-its-band", None
            reads = {n for n in expr.replace("(", " ").replace(")", " ").replace("/", " ").replace("*", " ").split()}
            declared = set((plan.get("measurements") or {}).keys())
            if reads and reads <= declared:
                return "declared-measurement-to-its-rule", None
            return None, "the constraint reads a quantity the record derives rather than declares"
        return None, "an ontology or massing question, not a record edit"
    if layer == "fault" and k == "fault-present":
        fid = f.get("fault")
        if fid == "porch-too-shallow-to-inhabit":
            return "trade-width-for-depth-at-constant-area", None
        if fid == "dormer-off-the-bay" and "% 2" in (f.get("expression") or ""):
            return "reduce-the-dormer-count-to-the-rhythm", None
        if f.get("source") == "declared":
            if fid == "shutter-half-width-leaf":
                return "shutter-leaf-at-half-the-opening", None
            if fid == "window-squarer-than-the-style-permits":
                return "narrow-the-window-and-keep-the-height", None
            return "declared-measurement-to-its-rule", None
        return None, "the failing figure is one the elevation generator derived, not one the record declares; the corpus's own fix is quoted"
    if layer == "drawn":
        if k in ("unreachable", "cut-off"):
            if f.get("adjacent_placed"):
                return "add-the-grammar-door", None
            return None, "no placed room shares a wall long enough for a door; the diagram itself strands this room"
        if k == "stair-not-drawn":
            return "grow-stair-hall-to-its-run", None
        if k == "fixture-unplaced":
            return "widen-wet-room-for-fixture", None
        if k in ("passage-narrow",):
            return "passage-to-its-band", None
        if k == "wall-run":
            if len((room or {}).get("exterior_walls") or []) >= 2 and f.get("walls_with_windows"):
                return "move-window-off-the-needed-wall", None
            return None, "the room has one exterior wall and the piece wants an unbroken run of it; the corpus hands the arrangement to the architect (OQ 92)"
        if k == "stack-broken":
            return None, "both engines charge a broken stack and neither could keep it; no record edit states where an upper room lands (align-upper-walls was refused for want of a basis)"
        if k == "stack-unjudged":
            return None, "the record's own stacking claim cannot be evaluated -- it names no room, or a room on this room's own level, or one more than a level below. No placement changes that and no move may edit a claim its author wrote: `build/check_stacking.py` fails the build on it and the author fixes the record (WP-11.6)"
        if k == "room-not-placed":
            return None, "a room the placer never reached. Both engines place level 0 and level 1 only, so a room above them has no rectangle and nothing a move can edit would give it one -- oq/the-placer-places-two-levels-and-says-nothing-about-the-third"
        return None, "a drawn-against-declared size or a landing off its well is a placement outcome; the record already states the right size"
    if layer in ("adjacency", "circulation", "privacy", "grouping", "completeness", "servicing", "plan"):
        return None, "topology: which rooms touch which is the parti's and the author's; a door the grammar prescribes is added only to reach a stranded room (drawn layer)"
    return None, "no move reads this layer"


def _is_placement(plan, f):
    """The engine's finding, not the record's -- decided BEFORE `actionable`, so a move is
    never asked to fix what a proof would.

    HOW it is decided differs by kind, and the WP-9.1 report said "decided against the
    DECLARED record" of all of them (WP-9.4). Four kinds read the record's own fields:
    `stair-not-drawn` (`declared_fits`), `fixture-unplaced` (the declared walls against the
    fixture's footprint), `wall-run` (the declared free walls against the run), and the two
    passage kinds (`declared_ft` in its band). Five are decided by WHAT THE RECORD DECLARES
    AND THE ENGINE DID NOT REALISE, which is a fact of the finding rather than a measurement:
    an `unreachable` or `cut-off` room DECLARES the door the search did not seat (the
    finding's own `declared` count), a `stack-broken` room declares the stack, and
    `drawn-vs-declared`, `landing-off-well` and `stack-unplaced` are by definition the
    placement disagreeing with the declaration. For those five the search engine's finding
    is the engine's and the proving engine's is the record's, because a proof that could not
    seat a declared door has shown the declaration cannot be built as written -- and then
    the door move or the conflict set is the answer. Whether that reading is right for every
    kind is `oq/a-placement-finding-is-classed-by-what-the-engine-is-for-five-kinds` -- which
    WP-11.12 made a SIXTH kind, `span-over-capacity`, and it is the first one the record
    declares nothing about at all. See the comment on it below."""
    if f["layer"] != "drawn":
        return False
    k = f.get("kind")
    engine = f.get("engine")
    room = _room(plan, f.get("room")) if f.get("room") else None
    dw, dl = (room or {}).get("width_ft"), (room or {}).get("length_ft")
    if k in ("unreachable", "cut-off"):
        # the declared graph reaches every room (or the adjacency layer would say); a search
        # that could not seat the declared doors is the search's, a proof that could not is
        # the record's -- and then the door move or the conflict set is the answer
        return engine != "cp-sat"
    if k in ("drawn-vs-declared", "landing-off-well", "stack-unplaced"):
        return True
    if k == "stack-unjudged":
        # NOT a placement finding, and the distinction is the whole reason WP-11.6 gave these
        # their own kind: `stack-unplaced` is the placement failing to place a room, while this
        # is the RECORD naming a room that is not one level below. No engine can answer it.
        return False
    if k == "room-not-placed":
        # The placer's own two-level ceiling, which is neither engine's judgment of this record.
        return False
    if k == "span-over-capacity":
        # WP-11.12, AND IT STRETCHES THIS FUNCTION'S OWN DEFINITION, which is said here rather
        # than left for a reader to notice. Every other kind above is decided against something
        # the record DECLARES -- a door, a stack, a size, a passage width. A plan record states
        # no wall positions at all, so there is nothing declared for a clear span to disagree
        # with. It is classed `placement` on the other half of the definition: an engine setting
        # really does change it, and demonstrably -- WP-11.8 took the corpus figure from 11 to
        # 23 by changing what the search ranks first (deterministic, `engine="heuristic"`; the
        # pair that package published was an unlabelled `auto` reading and its BEFORE was 13),
        # and both engines already CHARGE the span
        # (`geometry.SPAN_W`, and CP's soft mirror). Under CP-SAT `_lever` then says there is no
        # setting left, which is the honest answer: the record declares nothing here, so a
        # proved placement's spans are what the brief yields.
        # `oq/a-placement-finding-is-classed-by-what-the-engine-is-for-five-kinds` is where this
        # reading belongs, and it is recorded there as the sixth kind.
        return True
    if k == "stack-broken":
        return engine != "cp-sat"
    if k == "stair-not-drawn":
        return bool(f.get("declared_fits"))
    if k in ("passage-narrow", "passage-dead-zone"):
        d = f.get("declared_ft")
        return bool(d and 6.0 <= d <= 7.0) if k == "passage-narrow" else bool(d and not (8.0 <= d <= 9.0))
    if k == "fixture-unplaced":
        need = f.get("need_ft") or [None, None]
        if dw and dl and need[0] and need[1]:
            return max(dw, dl) + 1e-6 >= need[0] and min(dw, dl) + 1e-6 >= need[1]
        return False
    if k == "wall-run":
        need = f.get("need_ft") or 0
        ext = set((room or {}).get("exterior_walls") or [])
        with_win = set(f.get("walls_with_windows") or [])
        declared_win = {w.get("wall") for w in (room or {}).get("windows") or []}
        free_walls = ext - declared_win
        if free_walls and dw and dl:
            along = {"N": max(dw, dl), "S": max(dw, dl), "E": min(dw, dl), "W": min(dw, dl)}
            return any(along.get(w, 0) >= need for w in free_walls)
        return False
    return False


def classify(plan, check, registry=None, C=None, ctx=None):
    """Sort every finding of a check result into the five classes (or could_not_evaluate)."""
    assessment = {c: [] for c in CLASSES}
    cne = []
    for f in check.get("findings", []):
        if f["severity"] == "info":
            cne.append({"id": f["id"], "layer": f["layer"], "rule": f.get("rule"),
                        "kind": f.get("kind"), "statement": f["statement"]})
            continue
        issue = {"finding": f, "id": f["id"], "severity": f["severity"], "layer": f["layer"],
                 "kind": f.get("kind"), "room": f.get("room"), "statement": f["statement"]}
        if f["layer"] == "code":
            issue.update({"class": "advisory",
                          "why": "the code layer is advisory and jurisdictional by ruling, and unscored"})
            assessment["advisory"].append(issue)
            continue
        if _is_placement(plan, f):
            lever = _lever(plan, f, ctx)
            if lever["lever"] is None:
                # proved, and no conflict named: nothing an engine setting can change. That is
                # not a placement question any more; it is the record's own consequence, and it
                # goes to the architect with the proof's account of itself.
                issue.update({"class": "architect", "why": lever["why"], "engine": lever["engine"],
                              "proved": True})
                assessment["architect"].append(issue)
                continue
            issue.update({"class": "placement", **lever,
                          "note": "the declared record would have satisfied this; the engine did not"})
            assessment["placement"].append(issue)
            continue
        suspect = CS.why_suspect(f) if f["layer"] == "fault" else None
        if suspect:
            issue.update({"class": "critic_suspect", "evidence": suspect,
                          "why": "the failing test reads a figure the elevation generator states "
                                 "as its own constant, or a pair the editorial list names; not "
                                 "acted on, and the report has to argue it"})
            assessment["critic_suspect"].append(issue)
            continue
        move, reason = _intended_move(plan, f)
        ans = registry.answering(f, plan, C, ctx) if registry is not None else []
        if ans:
            # THE REGISTRY DECIDES. A move is offered only if its precondition held on a copy
            # of this very plan, so `actionable` means "would apply", not "might".
            first = next((m for m in ans if m["id"] == move), None) or ans[0]
            issue.update({"class": "actionable", "move": first["id"], "would": first.get("would"),
                          "moves": [m["id"] for m in ans],
                          "basis": first.get("basis"), "authority": first.get("authority"),
                          "requires": first.get("requires")})
            assessment["actionable"].append(issue)
            continue
        issue["class"] = "architect"
        if move and registry is None:
            issue["why"] = f"a move would answer this ({move}) and the registry is not built yet"
            issue["intended_move"] = move
        elif move:
            issue["why"] = (f"{move} would answer this and its precondition does not hold on this record"
                            + (": " + reason if reason else ""))
            issue["intended_move"] = move
        else:
            issue["why"] = reason or "no move reads this finding"
        if f["layer"] == "fault":
            issue["fix_right"] = f.get("fix_right")
            issue["fix_cheap"] = f.get("fix_cheap")
        elif isinstance(f.get("rule"), str) and " " in f["rule"]:
            # an adjacency or grouping rule's own `why` rides in `rule` as prose; an id-shaped
            # rule (a constraint, a slot) is a citation, not an argument, and is left where it is
            issue["rule_why"] = f["rule"]
        assessment["architect"].append(issue)
    return assessment, cne


def critique(plan, engine="auto", candidates=250, parti=None, place=True, seed=7,
             time_limit_s=25.0, C=None, ctx=None):
    core = _mod("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))
    plan = core.copy_json(plan)
    C = C or PC.load_corpus()
    ctx = dict(ctx or {}); ctx.setdefault("candidates", candidates); ctx.setdefault("engine", engine)
    placement = {"reused": False, "requested": engine if place else None, "could_not_evaluate": None}
    if place:
        if has_placement(plan):
            placement["reused"] = True
        else:
            pt = core.load_parti(parti) if isinstance(parti, str) else parti
            out = GEO.solve(plan, pt, candidates, seed=seed, engine=engine, time_limit_s=time_limit_s)
            if "error" in out or out.get("unsolved"):
                placement["could_not_evaluate"] = out.get("error") or out.get("reason") or "unsolved"
            else:
                plan = out
    solver = (plan.get("geometry_report") or {}).get("solver") or {}
    check = PC.check(plan, C)
    assessment, cne = classify(plan, check, _registry(), C, ctx)
    return {
        "plan_id": plan.get("id"), "style": plan.get("style"),
        "engine": {"requested": engine if place else None, "ran": solver.get("engine"),
                   "reason": solver.get("reason"), "fallback": solver.get("fallback")},
        "placement": {**placement, "candidates": candidates if place else None,
                      "placed": has_placement(plan)},
        "plan": plan, "check": check, "key": key_of(check),
        "assessment": assessment,
        "counts_by_class": {c: len(v) for c, v in assessment.items()},
        "could_not_evaluate": {
            "findings": cne,
            "elevation": check.get("elevation_summary"),
            "drawn": (check.get("drawn_summary") or {}).get("evaluated"),
            "faults_unjudged": len(check.get("fault_unjudged") or []),
            "faults_not_applicable": len(check.get("fault_not_applicable") or []),
        },
        "note": ("Five classes and one non-class. A finding is placement, suspect, actionable, "
                 "architect or advisory -- never two of them -- and an info finding is the critic "
                 "saying it could not evaluate, listed and never counted as anything else."),
    }


# ------------------------------------------------------------------ cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--engine", default="auto", choices=["auto", "cp", "heuristic"])
    ap.add_argument("--candidates", type=int, default=250)
    ap.add_argument("--declared", action="store_true", help="critique the declared record, no placement")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    plan = json.load(open(a.plan, encoding="utf-8"))
    res = critique(plan, engine=a.engine, candidates=a.candidates, place=not a.declared)
    if a.json:
        out = {k: v for k, v in res.items() if k != "plan"}
        print(json.dumps(out, indent=1, ensure_ascii=False))
        return
    e = res["engine"]
    print(f"\n  {plan.get('name') or plan['id']}   [{res['style']}]   "
          f"engine {e['ran'] or 'none'}" + (f" ({e['fallback']}: {e['reason']})" if e.get("fallback") else "")
          + f"   key {res['key']}")
    for c in CLASSES:
        rows = res["assessment"][c]
        print(f"\n  {c.upper().replace('_', ' ')}  ({len(rows)})")
        for i in rows[:40]:
            tail = ""
            if c == "actionable":
                tail = f"  -> {i['move']}"
            elif c == "placement":
                tail = f"  -> {i.get('lever') or 'no lever'}" + (f" ({i.get('move')})" if i.get("move") else "")
            elif c == "critic_suspect":
                ev = i["evidence"][0]
                tail = "  <- " + (f"{ev['instrument']} {ev.get('measurement') or ev.get('id')}"
                                  + (f" = {ev['value']} at line {ev['line']}" if "value" in ev else ""))
            elif c == "architect" and i.get("intended_move"):
                tail = f"  (would be {i['intended_move']})"
            print(f"    [{i['severity']:<7}] {i['statement'][:110]}{tail}")
        if len(rows) > 40:
            print(f"    ... and {len(rows) - 40} more")
    q = res["could_not_evaluate"]
    print(f"\n  COULD NOT EVALUATE: {len(q['findings'])} info finding(s); elevation "
          f"{'from ' + str(q['elevation'].get('basis')) if q['elevation'] and q['elevation'].get('evaluated') else 'not derived'}; "
          f"drawn layer {'evaluated' if q['drawn'] else 'not evaluated'}; "
          f"{q['faults_unjudged']} faults unjudged, {q['faults_not_applicable']} not applicable\n")


if __name__ == "__main__":
    main()
