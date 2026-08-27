#!/usr/bin/env python3
"""Check openings/window-grammar.json (WP-7.3, OQ 78).

Seven checks, and the two that matter most are the same two the door grammar's checker
enforces: every editorial `basis` must quote prose that is really in the record it names, and
the resolution must be TOTAL — every (room type, wall exposure) the corpus can produce has to
land on a named rule, so no window is ever dimensioned from nothing.

The third is this file's own: the grammar decides a window's ROLE and the kit decides its
SASH KIND, and neither may state the other's. A room rule carrying a `unit_type`, or a kit
variant leaking a role, is the same fact in two places — the failure this corpus keeps paying
for (REF_RE/CITE_RE/parseCite, relaxation_marks/relaxationMarks).

    python3 build/check_windows.py [--strict] [--coverage]
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache                                                        # noqa: E402
CO = modcache.load("check_openings", os.path.join(ROOT, "build", "check_openings.py"))
Report, load = CO.Report, CO.load

GRAMMAR = "openings/window-grammar.json"
WALLS = ("exterior", "interior")
ROLES_NEEDING_INTERIOR = {"borrowed-light"}


def rooms_corpus():
    out = {}
    d = os.path.join(ROOT, "rooms")
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".json"):
            r = load(os.path.join(d, fn))
            out[r["id"]] = r
    return out


def all_rules(g):
    return list(g.get("room_rules") or []) + list(g.get("class_defaults") or []) + [g["default"]]


def resolve(g, room, wall):
    """First match in the stated order. Returns (rule, tier)."""
    for r in (g.get("room_rules") or []):
        w = r.get("when") or {}
        types = (w.get("room") or {}).get("type") or []
        if room["id"] in types and w.get("wall", wall) == wall:
            return r, "room"
    for r in (g.get("class_defaults") or []):
        w = r.get("when") or {}
        fcs = (w.get("room") or {}).get("function_class") or []
        if room.get("function_class") in fcs and w.get("wall", wall) == wall:
            return r, "class"
    return g["default"], "default"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    a = ap.parse_args()
    rep = Report()
    gpath = os.path.join(ROOT, GRAMMAR)
    if not os.path.exists(gpath):
        print(f"ERROR: {GRAMMAR} is missing")
        return 1
    g = load(gpath)
    rules = all_rules(g)

    # 1. editorial, and saying so
    if g.get("kind") != "editorial" or not g.get("judgment"):
        rep.err(GRAMMAR, "the file must declare kind: editorial and judgment: true")
    if not g.get("note"):
        rep.err(GRAMMAR, "an editorial file must carry a note saying no source is recorded")

    # 2. ids stable and unique
    seen = set()
    for r in rules:
        if not r.get("id"):
            rep.err(GRAMMAR, "a rule has no id")
        elif r["id"] in seen:
            rep.err(GRAMMAR, f"duplicate rule id {r['id']}")
        seen.add(r.get("id"))

    # 3. THE BASIS IS CHECKED, not trusted -- the door grammar's own function, not a copy
    for r in rules:
        if r["id"] == g["default"]["id"]:
            continue                      # the default cites a system, not a room sentence
        CO.check_basis(rep, r, GRAMMAR)

    # 4. a rule states a ROLE and never a sash kind
    roles = set((g.get("roles") or {}).keys())
    for r in rules:
        u = r.get("unit") or {}
        if u.get("role") not in roles:
            rep.err(GRAMMAR, f"{r['id']} states role {u.get('role')!r}, which roles{{}} does not define")
        if "unit_type" in u or "window_type" in u:
            rep.err(GRAMMAR, f"{r['id']} states a sash kind — that is the kit's to say, not this file's")

    # 5. a borrowed light is never in an exterior wall
    for r in rules:
        u, w = r.get("unit") or {}, (r.get("when") or {})
        if u.get("role") in ROLES_NEEDING_INTERIOR and w.get("wall") != "interior":
            rep.err(GRAMMAR, f"{r['id']} puts a {u['role']} on a {w.get('wall')} wall")

    # 6. TOTALITY: every room type against every wall exposure resolves to a named rule
    C = rooms_corpus()
    tiers = {"room": 0, "class": 0, "default": 0}
    pairs = 0
    for rid, room in C.items():
        for wall in WALLS:
            rule, tier = resolve(g, room, wall)
            pairs += 1
            tiers[tier] += 1
            if not rule or not rule.get("id"):
                rep.err(GRAMMAR, f"{rid} on an {wall} wall resolves to nothing")
    if a.coverage or a.strict:
        named = tiers["room"] + tiers["class"]
        print(f"  coverage: {pairs} (room type x wall exposure) resolutions; "
              f"{tiers['room']} by a room rule, {tiers['class']} by a class default, "
              f"{tiers['default']} fall through to {g['default']['id']}")
        print(f"  note: {named} of {pairs} ({100.0 * named / pairs:.1f}%) land on a rule that "
              f"read something; the rest reach a named default, which is a rule but not an answer")

    # 7. the file must be HONEST about the vocabulary rather than publish an idealised one.
    # `unit_type` carries the kit's own resolved string; there is no closed enum, and a first
    # draft of this file invented one (double-hung / casement / fixed / …) that the kits do
    # not use -- which would have been a second spelling of the kits' vocabulary, drifting
    # from the moment either changed.
    ut = g.get("unit_types") or {}
    if ut.get("values"):
        rep.err(GRAMMAR, "unit_types publishes a closed enum; `unit_type` carries the kit's "
                         "own resolved string and this file must not spell it a second time")
    obs = ut.get("observed") or {}
    if not obs.get("styles_resolving"):
        rep.err(GRAMMAR, "unit_types states no measured coverage — how many styles the cascade "
                         "can answer for is the whole three-state claim")

    n_room = len(g.get("room_rules") or [])
    n_cls = len(g.get("class_defaults") or [])
    print(f"\n{'OK' if not rep.errors else 'FAIL'} — window grammar: {n_room} room rule(s), "
          f"{n_cls} class default(s), {pairs} resolutions, {len(rep.errors)} error(s), "
          f"{len(rep.warnings)} warning(s)")
    for e in rep.errors:
        print(f"  ERROR {e}")
    for w in rep.warnings:
        print(f"  warn  {w}")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
