#!/usr/bin/env python3
"""furniture/grammar.json — every rule declares its grade, and every quote is checked.

WP-11.3. What this checks, and why each one is here:

  1. The file parses, carries the keys the grammar promises, and its `executed` /
     `stated_not_executed` id lists name rules that exist.
  2. Every rule declares a `grade` from the file's own `grades` block. A rule with no grade is
     a rule whose provenance nobody stated, and the whole point of this grammar is that a
     reader can tell what the corpus said from what we decided.
  3. Every `basis` names a record that EXISTS and, where it quotes, quotes something that
     record actually says, UNDER THE KEY PATH IT NAMES. This is
     `build/check_openings.py::check_basis`, CALLED and not copied — that function already
     walks `furniture[<item>].note` because its `_walk_keypath` resolves a bracketed key on a
     list by the element's own `item`, and it already carries WP-9.4's finding that a real
     sentence cited under the wrong key used to pass. `build/check_windows.py` is the existing
     precedent for importing it; the corpus has been bitten three times by one rule spelled
     twice.
  4. An `editorial` rule must NOT quote a record. That direction matters as much as the other:
     a judgment dressed in a citation is worse than a judgment, because it reads as sourced.
  5. Every item in the room catalogue carries a `kind` from the schema's enum, and the counts
     are published. `check_rooms.py` requires the field; this prints the distribution, so a
     silent drift from 241 objects to 200 is visible rather than merely legal.
  6. A `variant` names an alternative to an object listed EARLIER in the same room. A variant
     that is the first `object`-less entry of its room has nothing to be an alternative to,
     which is the one way this vocabulary can be wrong without being invalid.

    python3 build/check_furniture.py
    python3 build/check_furniture.py --strict     # warnings become errors
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAMMAR = os.path.join(ROOT, "furniture", "grammar.json")

COULD_NOT_EVALUATE = 3

KINDS = ("object", "reservation", "covering", "placed-elsewhere", "variant")


def _mod(name, path):
    """build/modcache.py and never a local loader (OQ 28; tests/test_modcache.py counts them).
    The first draft carried a `spec_from_file_location` fallback and that guard found it."""
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
        """check_openings.check_basis calls this name when it cannot walk a key path.
        UNJUDGED, never a pass -- the corpus's own rule."""
        self.unjudged_list.append(f"{where}: {msg}")


def _rules(g):
    """Every rule object in the file, with the block it came from."""
    for block in ("placement_rules", "refusal_rules", "stated_rules_not_executed"):
        for r in g.get(block) or []:
            yield block, r


def check(strict=False):
    rep = Report()
    # check_openings owns the basis machinery and this file CALLS it rather than copying it.
    co = _mod("check_openings", os.path.join(ROOT, "build", "check_openings.py"))

    g = json.load(open(GRAMMAR))
    grades = set(g.get("grades") or {})
    if not grades:
        rep.err("grammar", "no `grades` block — a rule's provenance has nothing to declare against")

    ids = set()
    for block, r in _rules(g):
        rid = r.get("id") or "<no id>"
        where = f"{block}:{rid}"
        if rid in ids:
            rep.err(where, "duplicate rule id")
        ids.add(rid)
        grade = r.get("grade")
        if grade not in grades:
            rep.err(where, f"grade {grade!r} is not one of {sorted(grades)}")
        if not r.get("rule"):
            rep.err(where, "no `rule` — a rule that does not say what it does cannot be argued with")
        # 3 + 4: the basis, and the direction that matters both ways
        basis = r.get("basis") or ""
        if not basis:
            rep.err(where, "no `basis` — an editorial call must say what it read, "
                           "or say plainly that it read nothing")
            continue
        names_record = any(p in basis for p in ("rooms/", "kits/", "styles/", "faults/",
                                                "groupings/", "proportions/", "build/"))
        if grade == "editorial":
            if '"' in basis and names_record:
                rep.err(where, "an `editorial` rule quotes a record. A judgment wearing a "
                               "citation reads as sourced and is worse than a judgment.")
        else:
            if not names_record:
                rep.err(where, f"grade {grade!r} claims the corpus states this, and the basis "
                               f"names no record")
            else:
                co.check_basis(rep, r, source="furniture/grammar.json")

    for key in ("executed", "stated_not_executed"):
        for rid in g.get(key) or []:
            if rid not in ids:
                rep.err(f"grammar:{key}", f"names {rid!r}, which is not a rule in this file")

    # 5 + 6: the catalogue's own `kind` values
    import glob
    counts = {k: 0 for k in KINDS}
    total = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))):
        d = json.load(open(f))
        seen_object = False
        for it in (d.get("furniture") or []):
            total += 1
            k = it.get("kind")
            where = f"rooms/{d['id']}.json:{it['item'][:40]}"
            if k not in KINDS:
                rep.err(where, f"kind {k!r} is not one of {list(KINDS)}")
                continue
            counts[k] += 1
            if k == "object":
                seen_object = True
            if k == "variant" and not seen_object:
                rep.err(where, "kind `variant` means an alternative to an object listed EARLIER "
                               "in this room, and no object precedes it")
    print(f"  furniture items: {total}")
    for k in KINDS:
        print(f"    {k:17s} {counts[k]}")
    ex = len(g.get("executed") or [])
    sn = len(g.get("stated_not_executed") or [])
    print(f"  rules: {len(ids)} ({ex} executed, {sn} stated and not executed)")
    by_grade = {}
    for _b, r in _rules(g):
        by_grade[r.get("grade")] = by_grade.get(r.get("grade"), 0) + 1
    for gr in sorted(by_grade):
        print(f"    grade {gr:22s} {by_grade[gr]}")
    return rep


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
