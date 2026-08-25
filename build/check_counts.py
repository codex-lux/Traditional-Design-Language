#!/usr/bin/env python3
"""Catch stale hand-typed counts in the prose files.

`gen_readme_counts.py` generates README's counts block, and a generated block
cannot drift. Everything else does. WP-4.6's second tranche (25 Aug 2026) found
CLAUDE.md -- the file every agent is told to read first -- reporting 36 packs
when there were 40, 95 slots when there were 96, and ontology 0.5.0 four commits
after 0.6.0 shipped; docs/proportion.md, docs/README.md, STATE-OF-THE-PROJECT.md
and README's prose were stale in the same three directions. Each was fixed by
hand, which is how it got that way in the first place.

So: every count that appears in prose is declared here once, next to the
expression that computes it from the data, and this script fails the build when
the two disagree. `--fix` rewrites the prose in place.

This is deliberately NOT a generator. These numbers sit inside sentences that
argue something, and a generator would have to own the sentences too. A checker
lets the prose stay written by a person and still stops it lying.

Run:  python3 build/check_counts.py [--fix] [--verbose]
Exit: 0 clean, 1 if any claim is stale (or was rewritten under --fix).
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def computed():
    """Every figure the prose is allowed to quote, computed from the data."""
    v = {}
    packs = [json.load(open(f)) for f in glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))]
    v["packs"] = len(packs)
    v["pack_conflicts"] = sum(len(p.get("conflicts", [])) for p in packs)

    slots_doc = json.load(open(os.path.join(ROOT, "elements", "slots.json")))
    v["slots"] = sum(len(g["slots"]) for g in slots_doc["groups"])
    v["ontology"] = slots_doc.get("version", "?")

    nodes = [json.load(open(f)) for f in glob.glob(os.path.join(ROOT, "styles", "*.json"))]
    buildable = [n for n in nodes if n.get("rank") in ("style", "variant")]
    v["nodes"] = len(nodes)
    v["buildable"] = len(buildable)
    v["bound"] = sum(1 for n in buildable if n.get("proportion_packs"))
    for role in ("opening", "facade", "interior"):
        v["no_%s_role" % role] = sum(
            1 for n in buildable
            if not any(e["role"] == role for e in n.get("proportion_packs") or [])
        )
    v["rooms"] = len(glob.glob(os.path.join(ROOT, "rooms", "*.json")))
    v["groupings"] = len(glob.glob(os.path.join(ROOT, "groupings", "*.json")))
    v["partis"] = len(glob.glob(os.path.join(ROOT, "partis", "*.json")))
    v["faults"] = len(glob.glob(os.path.join(ROOT, "faults", "*.json")))
    v["massings"] = len(json.load(open(os.path.join(ROOT, "massings", "catalog.json"))))
    return v


# (file, key, regex).  The regex must have exactly one capturing group, and that
# group must be the number (or version string) being claimed.  Every occurrence
# is checked, so a file may repeat a claim.
CLAIMS = [
    ("CLAUDE.md",              "packs",         r"\*\*(\d+) packs, \d+ of \d+ nodes bound\*\*"),
    ("CLAUDE.md",              "bound",         r"\*\*\d+ packs, (\d+) of \d+ nodes bound\*\*"),
    ("CLAUDE.md",              "buildable",     r"\*\*\d+ packs, \d+ of (\d+) nodes bound\*\*"),
    ("CLAUDE.md",              "no_opening_role", r"(\d+) nodes still have no opening-role pack"),
    ("CLAUDE.md",              "no_facade_role",  r"and (\d+) no facade-role pack"),
    ("CLAUDE.md",              "slots",         r"(\d+) slots \(ontology [\d.]+\)"),
    ("CLAUDE.md",              "ontology",      r"\d+ slots \(ontology ([\d.]+)\)"),
    ("CLAUDE.md",              "nodes",         r"^(\d+) nodes · \d+ slots"),
    ("CLAUDE.md",              "massings",      r"· (\d+) massings ·"),
    ("CLAUDE.md",              "rooms",         r"· (\d+) rooms ·"),
    ("CLAUDE.md",              "groupings",     r"· (\d+) groupings ·"),
    ("CLAUDE.md",              "faults",        r"· (\d+) faults ·"),
    ("STATE-OF-THE-PROJECT.md", "packs",        r"resolves and dimensions all (\d+) packs"),
    # Repointed 25 Aug 2026: the appendix row and the Part V sentence were both rewritten when
    # WP-4.6 closed, and these four patterns rotted. A rotted pattern is a failure in this checker
    # for a reason -- the sentence it guarded still carries a number, and nothing was watching it.
    ("STATE-OF-THE-PROJECT.md", "packs",        r"\*\*(\d+) packs, \d+ conflicts"),
    ("STATE-OF-THE-PROJECT.md", "pack_conflicts", r"\*\*\d+ packs, (\d+) conflicts"),
    ("STATE-OF-THE-PROJECT.md", "no_opening_role", r"68 → (\d+) with no opening-role pack"),
    ("STATE-OF-THE-PROJECT.md", "no_facade_role",  r"68 → (\d+) with no facade-role pack"),
    ("docs/README.md",         "packs",         r"(\d+) packs as functions not tables"),
    ("docs/proportion.md",     "packs",         r"^(\d+) packs, in four kinds:"),
    ("README.md",              "packs",         r"the syntax\. (\d+) packs, and they are"),
    ("README.md",              "no_opening_role", r"(\d+) nodes still have no opening-role pack"),
    ("README.md",              "no_facade_role",  r"no opening-role pack and (\d+) no facade-role pack"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="rewrite stale claims in place")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    v = computed()
    stale, checked, missing = [], 0, []

    by_file = {}
    for path, key, pattern in CLAIMS:
        by_file.setdefault(path, []).append((key, pattern))

    for path, claims in by_file.items():
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            missing.append(f"{path}: file not found")
            continue
        text = open(full).read()
        for key, pattern in claims:
            rx = re.compile(pattern, re.M)
            hits = list(rx.finditer(text))
            if not hits:
                missing.append(f"{path}: no match for {key} -- pattern '{pattern}' has rotted")
                continue
            want = str(v[key])
            for m in hits:
                checked += 1
                got = m.group(1)
                if got != want:
                    stale.append(f"{path}: {key} says {got}, data says {want}")
                    if args.fix:
                        s, e = m.span(1)
                        text = text[:s] + want + text[e:]
                        rx = re.compile(pattern, re.M)   # offsets moved
        if args.fix:
            open(full, "w").write(text)

    if args.verbose:
        for k in sorted(v):
            print(f"  {k:18s} {v[k]}")

    for m in missing:
        print("MISSING  " + m)
    for s in stale:
        print(("FIXED    " if args.fix else "STALE    ") + s)

    print(f"\n{checked} count claim(s) checked across {len(by_file)} file(s); "
          f"{len(stale)} stale, {len(missing)} pattern(s) not found.")
    if missing:
        print("A pattern that no longer matches is a failure too: the sentence it guarded "
              "was rewritten and the count in it is now unguarded.")
    return 1 if (stale or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
