#!/usr/bin/env python3
"""Every `stacks_over` and `wet_stack_with` claim in the corpus, against what the field means.

WP-11.6. The two fields were one field until plan schema 0.8.0, whose description read *"room
id on the level below, for plumbing and structure"* — two duties — and one shipped record used
it for a ground-level room naming another ground-level room, which is the plumbing duty and
cannot be the structural one. Three readers dropped that claim with a bare `continue` and no
note, so the plan carried four claims of which three were judged and nothing said which three.

What this checks:

  1. Every `stacks_over` target EXISTS as a room in the same document.
  2. Every `stacks_over` names a room exactly ONE LEVEL BELOW the claimant. Same level, above,
     or two or more below is an ERROR, and the message names `wet_stack_with` where that is
     the field the author wanted. This is the check that would have caught the powder room.
  3. Every `wet_stack_with` target exists. Any level, including the claimant's own — that is
     the whole point of the field, and the target need not itself be wet, because a stack needs
     a chase and a stair shaft is one.
  4. No room states BOTH fields naming the SAME room: one claim written twice is two records of
     one fact, which is the shape this corpus keeps being bitten by.
  5. The placer's two-level ceiling, re-derived rather than quoted. `build/stacking.py` states
     `PLACED_LEVEL_INDICES`; any plan declaring a level outside it is REPORTED here, because
     every room on such a level is drawn nowhere and every drawn judgment about it is unjudged.
     `plans/reference/bad-03-narrow-lot-townhome.json` is the one instance and it is expected;
     a SECOND one, or that one disappearing, both mean something and both should be read.

WHAT THIS DELIBERATELY DOES NOT CHECK, AND WHY IT CANNOT
--------------------------------------------------------
**That a plan states the stacking its own parti declares.** That is how WP-11.6's own two
claims were found — by hand, by knowing that `plans/tidewater-georgian-careful.json` is a
`centre-passage-double-pile` and reading the parti beside it. Measured: **no plan record in
the corpus names a parti.** There is no `parti` key on any of the sixteen, so the join does not
exist and building it on matching room ids would be inventing a fact from a coincidence.
Recorded in `oq/a-plan-does-not-name-the-parti-it-was-built-from` rather than guessed at.

This checker never SOLVES anything. `kept` / `broken` / `not placed` are properties of a
placement and belong to `geometry_report.stacking`; the errors here are properties of the
RECORD, and a record error is the same on every engine.

    python3 build/check_stacking.py
    python3 build/check_stacking.py --strict     # warnings become errors
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, path):
    """build/modcache.py and never a local loader (OQ 28; tests/test_modcache.py counts them)."""
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache as _mc
    return _mc.load(name, path)


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.unjudged_list = []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")

    def unjudged(self, where, msg):
        self.unjudged_list.append(f"{where}: {msg}")


def _plan_rooms(doc):
    """[(level index, room record)] for a PLAN, reading `index` where a level states one."""
    for i, lv in enumerate(doc.get("levels") or []):
        idx = lv.get("index")
        for r in lv.get("rooms") or []:
            yield (i if idx is None else idx), r


def _parti_rooms(doc):
    """[(level, room record)] for a PARTI, where the level is on the room."""
    for r in doc.get("rooms") or []:
        yield r.get("level", 0), r


def _check_doc(where, pairs, rep):
    """The rules, once, for a plan or a parti — the two documents state levels differently and
    mean the same thing by a stack, so the reading differs and the RULE must not."""
    level_of = {r["id"]: lvl for lvl, r in pairs if r.get("id")}
    claims = 0
    for lvl, r in pairs:
        rid = r.get("id")
        so, ws = r.get("stacks_over"), r.get("wet_stack_with")
        if so and ws and so == ws:
            rep.err(where, f"room '{rid}' names '{so}' as BOTH its stacks_over and its "
                           f"wet_stack_with — one claim written twice. State the one that is "
                           f"true: stacks_over is the structural alignment, wet_stack_with the "
                           f"shared chase.")
        if ws:
            if ws not in level_of:
                rep.err(where, f"room '{rid}' has wet_stack_with '{ws}', which is not a room "
                               f"in this document")
        if not so:
            continue
        claims += 1
        if so not in level_of:
            rep.err(where, f"room '{rid}' has stacks_over '{so}', which is not a room in this "
                           f"document")
            continue
        gap = lvl - level_of[so]
        if gap == 1:
            continue
        why = ("on this room's own level" if gap == 0 else
               "ABOVE this room" if gap < 0 else
               f"{gap} levels below this room")
        rep.err(where, f"room '{rid}' (level {lvl}) has stacks_over '{so}', which is {why}. "
                       f"stacks_over is a STRUCTURAL claim about the level exactly one below "
                       f"and every reader of it judges rectangle overlap across two levels" +
                       (". A claim about a shared plumbing chase is `wet_stack_with`, which "
                        "takes any level including this one." if gap == 0 else "."))
    return claims


def check(strict=False):
    rep = Report()
    STK = _mod("stacking", os.path.join(ROOT, "build", "stacking.py"))
    claims = docs = 0
    off_ceiling = []

    for pf in sorted(glob.glob(os.path.join(ROOT, "plans", "*.json"))) + \
              sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))):
        doc = json.load(open(pf))
        if "levels" not in doc:
            continue
        docs += 1
        where = os.path.relpath(pf, ROOT)
        pairs = list(_plan_rooms(doc))
        claims += _check_doc(where, pairs, rep)
        # 5. the placer's own ceiling, re-derived against the module that states it
        beyond = sorted({lvl for lvl, r in pairs
                         if lvl not in STK.PLACED_LEVEL_INDICES
                         and STK.takes_a_rectangle(r.get("type"), _rooms())})
        if beyond:
            off_ceiling.append((where, beyond))
            rep.warn(where, f"declares level(s) {beyond}, which neither engine places "
                            f"(build/stacking.py PLACED_LEVEL_INDICES = "
                            f"{list(STK.PLACED_LEVEL_INDICES)}). Every room there is drawn "
                            f"nowhere; geometry_report.multi_level says so on the record.")

    for pf in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))):
        doc = json.load(open(pf))
        docs += 1
        claims += _check_doc(os.path.relpath(pf, ROOT), list(_parti_rooms(doc)), rep)

    print(f"  documents: {docs} · stacks_over claims: {claims} · "
          f"records declaring a level nobody places: {len(off_ceiling)}")
    for where, beyond in off_ceiling:
        print(f"    unplaced level(s) {beyond} in {where}")
    return rep


_ROOMS = {}


def _rooms():
    if not _ROOMS:
        for f in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))):
            r = json.load(open(f))
            _ROOMS[r["id"]] = r
    return _ROOMS


def main():
    strict = "--strict" in sys.argv
    rep = check(strict)
    for u in rep.unjudged_list:
        print(f"  N/EV {u}")
    for w in rep.warnings:
        print(f"  warn {w}")
    for e in rep.errors:
        print(f"  ERR  {e}")
    bad = len(rep.errors) + (len(rep.warnings) if strict else 0)
    print(f"{'FAIL' if bad else 'OK'}  errors={len(rep.errors)} warnings={len(rep.warnings)} "
          f"unjudged={len(rep.unjudged_list)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
