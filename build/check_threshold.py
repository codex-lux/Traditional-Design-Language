#!/usr/bin/env python3
"""threshold/grammar.json — every rule declares its grade, every quote is checked, and the
side table is proved TOTAL over the corpus (WP-11.4).

What this checks, and why each one is here:

  1. The file parses, carries the keys the grammar promises, and its `executed` /
     `stated_not_executed` id lists name rules that exist.
  2. Every rule declares a `grade` from the file's own `grades` block, and every rule the
     drawing can name is in the file — `build/threshold.py` writes a `rule` id onto every
     entry and every refusal, and a rule id nothing declares is a citation to nowhere.
  3. Every `basis` names a record that EXISTS and, where it quotes, quotes something that
     record actually says, UNDER THE KEY PATH IT NAMES — `build/check_openings.py::check_basis`
     CALLED and not copied, exactly as `check_furniture.py` and `check_windows.py` call it.
     That function already resolves a kit's slot and its parameters without the path having
     to spell `slots.` or `parameters.`, which is how a kit figure is addressed here.
  4. An `editorial` rule must NOT quote a record. A judgment wearing a citation reads as
     sourced and is worse than a judgment.
  5. **`build/threshold.py::SIDE_OF` IS TOTAL OVER THE CORPUS.** Every `hearth_position`
     variant id that appears in any kit — own file or cascade — and every `hearth` value any
     massing states is either mapped to a side or recorded as unmappable WITH A REASON. A
     token this table does not carry fails the build rather than defaulting to a side, which
     is the whole difference between this and the substring test WP-8.4 refused.
  6. The three-way measurement the package's own refusals rest on is RE-DERIVED here rather
     than quoted: how many nodes make a portico canonical, how many resolve a `portico_bays`,
     and how many state a column diameter in inches. The refusal rules quote those numbers in
     their notes; if the corpus moves, this check says so.

    python3 build/check_threshold.py
    python3 build/check_threshold.py --strict     # warnings become errors
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAMMAR = os.path.join(ROOT, "threshold", "grammar.json")


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
        """check_openings.check_basis calls this name when it cannot walk a key path.
        UNJUDGED, never a pass -- the corpus's own rule."""
        self.unjudged_list.append(f"{where}: {msg}")


def _rules(g):
    for block in ("placement_rules", "refusal_rules", "stated_rules_not_executed"):
        for r in g.get(block) or []:
            yield block, r


def check(strict=False):
    rep = Report()
    co = _mod("check_openings", os.path.join(ROOT, "build", "check_openings.py"))
    th = _mod("threshold", os.path.join(ROOT, "build", "threshold.py"))
    pc = _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
    rk = _mod("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
    C = pc.load_corpus()

    g = json.load(open(GRAMMAR, encoding="utf-8"))
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
        if r.get("grade") not in grades:
            rep.err(where, f"grade {r.get('grade')!r} is not one of {sorted(grades)}")
        if not r.get("rule"):
            rep.err(where, "no `rule` — a rule that does not say what it does cannot be argued with")
        basis = r.get("basis") or ""
        if not basis:
            rep.err(where, "no `basis` — an editorial call must say what it read, or say plainly "
                           "that it read nothing")
            continue
        names_record = any(p in basis for p in ("rooms/", "kits/", "styles/", "faults/",
                                                "groupings/", "proportions/", "massings/", "build/"))
        if r.get("grade") == "editorial":
            if '"' in basis and names_record:
                rep.err(where, "an `editorial` rule quotes a record. A judgment wearing a "
                               "citation reads as sourced and is worse than a judgment.")
        elif not names_record:
            rep.err(where, f"grade {r.get('grade')!r} claims the corpus states this, and the "
                           f"basis names no record")
        else:
            co.check_basis(rep, r, source="threshold/grammar.json")

    for key in ("executed", "stated_not_executed"):
        for rid in g.get(key) or []:
            if rid not in ids:
                rep.err(f"grammar:{key}", f"names {rid!r}, which is not a rule in this file")

    # 2b: every rule id build/threshold.py can write onto a record is declared here. A source
    # read rather than a list transcribed, because a transcribed list goes stale in silence.
    src = open(os.path.join(ROOT, "build", "threshold.py"), encoding="utf-8").read()
    import re
    for rid in sorted(set(re.findall(r'_graded\("([a-z0-9-]+)"\)', src))):
        if rid not in ids:
            rep.err("build/threshold.py", f"writes rule id {rid!r}, which threshold/grammar.json "
                                          f"does not declare")

    # 5: the side table, total over the corpus
    graph = rk.load_graph()
    kit_tokens, massing_tokens = set(), set()
    for nid, kit in C["kits"].items():
        for v in (((kit.get("slots") or {}).get("hearth_position") or {}).get("variants") or []):
            kit_tokens.add(v["id"])
        try:
            slots, _ = rk.resolve_slots(graph, rk.chain_for(graph, nid), rk.scope_for(graph, nid))
        except SystemExit:
            continue
        for v in ((slots.get("hearth_position") or {}).get("variants") or []):
            kit_tokens.add(v["id"])
    for m in C["massings"].values():
        if m.get("hearth"):
            massing_tokens.add(m["hearth"])
    for label, tokens, table in (("SIDE_OF", kit_tokens, th.SIDE_OF),
                                 ("MASSING_HEARTH", massing_tokens, th.MASSING_HEARTH)):
        for t in sorted(t for t in tokens if t not in table):
            rep.err(f"build/threshold.py:{label}",
                    f"the corpus uses hearth position {t!r} and the closed table does not carry "
                    f"it — a token this table does not name must fail the build, never default "
                    f"to a side")
        for t in sorted(t for t in table if t not in tokens):
            rep.warn(f"build/threshold.py:{label}",
                     f"{t!r} is in the table and in no record it governs — a dead entry, "
                     f"harmless but unread")
    sided = sorted(t for t, (sd, _g, _w) in th.SIDE_OF.items() if sd)
    ends = sorted(t for t, (_s, gg, _w) in th.MASSING_HEARTH.items() if gg is True)
    disj = sorted(t for t in th.MASSING_HEARTH if " or " in t)
    print(f"  kit hearth_position tokens in use: {len(kit_tokens)}; the closed table names a "
          f"SIDE for {len(sided)} ({', '.join(sided)})")
    print(f"  massing hearth values in use: {len(massing_tokens)}; at a gable end: {len(ends)}; "
          f"a DISJUNCTION naming two positions and choosing neither: {len(disj)} "
          f"({', '.join(disj)})")

    # 6: the three-fact measurement the refusals rest on
    portico = bays = dia = both = 0
    for nid in sorted(C["kits"]):
        try:
            slots, _ = rk.resolve_slots(graph, rk.chain_for(graph, nid), rk.scope_for(graph, nid))
        except SystemExit:
            continue
        pt = slots.get("porch_type") or {}
        can = [v["id"] for v in (pt.get("variants") or []) if v.get("status") == "canonical"]
        is_p = any("portico" in v for v in can)
        b = ((pt.get("parameters") or {}).get("portico_bays") or {}).get("value")
        d = (((slots.get("porch_support") or {}).get("parameters") or {}).get("base_diameter_in")
             or ((slots.get("column") or {}).get("parameters") or {}).get("base_diameter_in"))
        portico += bool(is_p)
        bays += b is not None
        dia += bool(d)
        both += bool(is_p and b is not None and d)
    print(f"  nodes with a canonical portico: {portico}; resolving a portico_bays: {bays}; "
          f"stating a column diameter in inches: {dia}; with all three: {both}")
    if both:
        rep.warn("threshold/grammar.json:th-a-column-needs-a-diameter",
                 f"{both} node(s) now carry all three facts a drawn column needs. The refusal "
                 f"this rule records is no longer total and the placement is not built.")

    ex = len(g.get("executed") or [])
    sn = len(g.get("stated_not_executed") or [])
    print(f"  rules: {len(ids)} ({ex} executed, {sn} stated and not executed)")
    by_grade = {}
    for _b, r in _rules(g):
        by_grade[r.get("grade")] = by_grade.get(r.get("grade"), 0) + 1
    for gr in sorted(by_grade, key=str):
        print(f"    grade {str(gr):22s} {by_grade[gr]}")
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
