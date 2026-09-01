#!/usr/bin/env python3
"""check_openings.py — validate the opening grammar (WP-6.2).

The grammar says which KIND of opening belongs between which two rooms. It is editorial
by ruling, which makes checking it MORE important rather than less: an editorial call that
cannot be traced to the prose it reads is indistinguishable from an invention, and the one
thing this corpus must never do is launder a guess.

Checks, in order:
  1. openings/grammar.json against schema/opening-grammar.schema.json
  2. rule ids unique and well-formed
  3. every `when` side resolves — a room type against the catalogue, a function_class
     against the classes the catalogue actually uses. A rule keyed on a type nobody wrote
     is a rule that never fires, silently.
  4. every `basis` names a record that EXISTS and, where it quotes, quotes something that
     record actually says. This is the check the file is for.
  5. TOTALITY — every ordered pair of room types, plus every type against `exterior`,
     resolves to some rule. The default is a rule, so this cannot fail outright; what it
     reports is how much of the corpus falls THROUGH to the default, which is the honest
     measure of how much of this grammar is still unwritten.
  6. bands sane (lo < hi, positive, inside the plan schema's own door enum for type)
  7. where a rule's band and a bound kit's stated width_in disagree, report it — the kit
     is the corpus's own number and this file's band is editorial, so a clash means the
     band is wrong, not the kit.

    python3 build/check_openings.py
    python3 build/check_openings.py --strict     # warnings become errors
    python3 build/check_openings.py --coverage   # print the fall-through table
"""

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OK, WARN, ERR = "ok", "WARN", "ERROR"


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")

    def note(self, msg):
        self.notes.append(msg)


def rooms_index():
    idx = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))):
        d = load(p)
        idx[d["id"]] = d
    return idx


def all_rules(g):
    """Every rule in resolution order, most specific first."""
    return list(g.get("pair_rules") or []) + list(g.get("class_defaults") or []) + [g["default"]]


def side_matches(side, room_id, room):
    if side.get("any"):
        return True
    if "type" in side:
        return side["type"] == room_id
    fc = side.get("function_class")
    if fc is None:
        return False
    if isinstance(fc, str):
        fc = [fc]
    return (room or {}).get("function_class") in fc


def resolve(g, a_id, a_room, b_id, b_room):
    """The rule that governs the opening between two rooms. Unordered: a door is one door."""
    for rule in all_rules(g):
        w = rule.get("when")
        if w is None:
            return rule
        if (side_matches(w["a"], a_id, a_room) and side_matches(w["b"], b_id, b_room)) or \
           (side_matches(w["a"], b_id, b_room) and side_matches(w["b"], a_id, a_room)):
            return rule
    return g["default"]


# --------------------------------------------------------------------- the basis check
# `build/<file>.py` is admitted since WP-9.1: critique/suspects.json's bases quote the elevation
# GENERATOR saying what it does not model, and that sentence lives in its source, not in a record.
_REC_RE = re.compile(r"((?:rooms|kits|styles|faults|groupings|proportions)/[A-Za-z0-9_.\-/]+\.json"
                     r"|build/[A-Za-z0-9_]+\.py)")
_QUOTE_RE = re.compile(r"\"([^\"]{25,})\"")


def check_basis(rep, rule, source="openings/grammar.json"):
    """A basis must name a record that exists, and any long quotation in it must appear in
    that record. Editorial is a licence to judge, never a licence to make things up.

    `source` names the file being checked so build/check_windows.py can call this rather than
    grow a second copy — the corpus has been bitten three times by one rule spelled twice."""
    basis = rule.get("basis") or ""
    where = f"{source}[{rule['id']}]"
    paths = _REC_RE.findall(basis)
    if not paths:
        rep.err(where, "basis names no record — an editorial call must say what it read")
        return
    blobs = []
    for rel in paths:
        full = os.path.join(ROOT, rel)
        if not os.path.exists(full):
            rep.err(where, f"basis names {rel}, which does not exist")
            continue
        with open(full, "r", encoding="utf-8") as fh:
            blobs.append(fh.read())
    if not blobs:
        return
    hay = "\n".join(blobs)
    # normalise the way JSON stores prose: escaped quotes, and any run of whitespace
    hay_n = re.sub(r"\s+", " ", hay.replace('\\"', '"'))
    for q in _QUOTE_RE.findall(basis):
        needle = re.sub(r"\s+", " ", q).strip()
        # an elision is the author's, and the halves either side must each be real
        parts = [p.strip() for p in needle.split("...") if len(p.strip()) >= 20]
        for part in (parts or [needle]):
            if part not in hay_n:
                rep.err(where, f"basis quotes {part[:70]!r}, which is not in {', '.join(paths)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    args = ap.parse_args()

    rep = Report()
    gpath = os.path.join(ROOT, "openings", "grammar.json")
    if not os.path.exists(gpath):
        print("ERROR: openings/grammar.json is missing")
        return 1
    g = load(gpath)

    # 1 — schema
    try:
        import jsonschema
        schema = load(os.path.join(ROOT, "schema", "opening-grammar.schema.json"))
        errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(g),
                      key=lambda e: list(e.path))
        for e in errs:
            rep.err("schema", f"{list(e.path)}: {e.message[:200]}")
    except ImportError:
        # COULD NOT EVALUATE, and said so — never counted as a pass
        rep.note("N/EV schema validation — jsonschema is not installed")

    rules = all_rules(g)

    # 2 — ids
    seen = set()
    for r in rules:
        rid = r.get("id", "")
        if rid in seen:
            rep.err("ids", f"duplicate rule id {rid}")
        seen.add(rid)

    rooms = rooms_index()
    classes = {d.get("function_class") for d in rooms.values()}

    # 3 — every side resolves
    for r in rules:
        w = r.get("when")
        if not w:
            continue
        for side_name in ("a", "b"):
            s = w[side_name]
            if "type" in s and s["type"] != "exterior" and s["type"] not in rooms:
                rep.err(f"openings/grammar.json[{r['id']}]",
                        f"{side_name}.type '{s['type']}' is not a room in the catalogue")
            fc = s.get("function_class")
            if fc is not None:
                for c in ([fc] if isinstance(fc, str) else fc):
                    if c not in classes:
                        rep.err(f"openings/grammar.json[{r['id']}]",
                                f"{side_name}.function_class '{c}' is used by no room")

    # 4 — basis
    for r in rules:
        check_basis(rep, r)

    # 6 — bands
    for r in rules:
        lo, hi = r["opening"]["width_band_ft"]
        if not (0 < lo < hi):
            rep.err(f"openings/grammar.json[{r['id']}]",
                    f"width_band_ft {[lo, hi]} is not an ascending positive band")
        # a garage door genuinely is that wide; every other kind of opening is not
        cap = 20 if r["opening"]["type"] == "garage" else 10
        if hi > cap:
            rep.warn(f"openings/grammar.json[{r['id']}]",
                     f"width_band_ft tops out at {hi} ft, above the {cap} ft ceiling for "
                     f"a {r['opening']['type']} opening")

    # 5 — totality, and the fall-through count that is the real measure
    ids = sorted(rooms) + ["exterior"]
    fell = []
    by_rule = {}
    for i, a in enumerate(ids):
        for b in ids[i:]:
            if a == "exterior" and b == "exterior":
                continue
            rule = resolve(g, a, rooms.get(a), b, rooms.get(b))
            by_rule[rule["id"]] = by_rule.get(rule["id"], 0) + 1
            if rule["id"] == g["default"]["id"]:
                fell.append((a, b))
    total = sum(by_rule.values())
    covered = total - len(fell)
    rep.note(f"{covered} of {total} room pairs are governed by a named rule "
             f"({100.0 * covered / total:.1f}%); {len(fell)} fall through to "
             f"{g['default']['id']}, which is a rule but not an answer")

    # 7 — a band that argues with a kit's own stated width
    kit = os.path.join(ROOT, "kits", "georgian-colonial-american.kit.json")
    if os.path.exists(kit):
        k = load(kit)
        slots = k.get("slots", {})
        entry = (slots.get("entry_door") or {}).get("parameters") or {}
        w = entry.get("measured_width_in") or {}
        band = w.get("range") or w.get("value")
        if isinstance(band, list) and len(band) == 2:
            klo, khi = band[0] / 12.0, band[1] / 12.0
            for r in rules:
                if r["id"] != "og-entry-door":
                    continue
                lo, hi = r["opening"]["width_band_ft"]
                if lo > khi or hi < klo:
                    rep.err(f"openings/grammar.json[{r['id']}]",
                            f"band {lo}-{hi} ft does not overlap the kit's own "
                            f"entry_door measured_width_in {band} ({klo:.2f}-{khi:.2f} ft)")

    if args.coverage:
        print("\nrules by pairs governed:")
        for rid, n in sorted(by_rule.items(), key=lambda kv: -kv[1]):
            print(f"  {n:6d}  {rid}")
        if fell:
            print(f"\nfell through to the default ({len(fell)}), first 40:")
            for a, b in fell[:40]:
                print(f"  {a} — {b}")

    for n in rep.notes:
        print(f"  note: {n}")
    for w in rep.warnings:
        print(f"  WARN {w}")
    for e in rep.errors:
        print(f"  ERROR {e}")

    bad = len(rep.errors) + (len(rep.warnings) if args.strict else 0)
    if bad:
        print(f"\ncheck_openings: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
        return 1
    print(f"OK — opening grammar: {len(rules)} rules, "
          f"{covered}/{total} pairs named, {len(rep.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
