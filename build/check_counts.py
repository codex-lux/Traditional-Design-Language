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
    packs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json")))]
    v["packs"] = len(packs)
    v["pack_conflicts"] = sum(len(p.get("conflicts", [])) for p in packs)

    slots_doc = json.load(open(os.path.join(ROOT, "elements", "slots.json")))
    v["slots"] = sum(len(g["slots"]) for g in slots_doc["groups"])
    v["ontology"] = slots_doc.get("version", "?")

    nodes = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json")))]
    buildable = [n for n in nodes if n.get("rank") in ("style", "variant")]
    v["nodes"] = len(nodes)
    v["buildable"] = len(buildable)
    v["bound"] = sum(1 for n in buildable if n.get("proportion_packs"))
    for role in ("opening", "facade", "interior"):
        v["no_%s_role" % role] = sum(
            1 for n in buildable
            if not any(e["role"] == role for e in n.get("proportion_packs") or [])
        )
    v["rooms"] = len(sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))))
    v["groupings"] = len(sorted(glob.glob(os.path.join(ROOT, "groupings", "*.json"))))
    v["partis"] = len(sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))))
    v["faults"] = len(sorted(glob.glob(os.path.join(ROOT, "faults", "*.json"))))
    v["massings"] = len(json.load(open(os.path.join(ROOT, "massings", "catalog.json"))))

    # WP-6.2. The opening grammar's size, so a sentence quoting it cannot drift from it.
    gpath = os.path.join(ROOT, "openings", "grammar.json")
    if os.path.exists(gpath):
        g = json.load(open(gpath))
        v["opening_rules"] = (len(g.get("pair_rules") or [])
                              + len(g.get("class_defaults") or []) + 1)
        v["opening_placement_rules"] = len(g.get("placement_rules") or [])

    # WP-4.4. The asset layer's own numbers were policed by NOTHING -- "322 image records, 0
    # sourced" was hand-typed in CLAUDE.md, README.md and STATE-OF-THE-PROJECT.md, and
    # docs/assets.md still said 292 records and 136 pairs against a file holding 322 and 150.
    # Four places, three different wrong answers, and no check could see any of them, which is
    # exactly the class check_counts.py exists for.
    apath = os.path.join(ROOT, "assets", "manifest.json")
    if os.path.exists(apath):
        a = json.load(open(apath))
        assets = a.get("assets") or []
        v["image_records"] = len(assets)
        by_status = {}
        for x in assets:
            by_status[x.get("status")] = by_status.get(x.get("status"), 0) + 1
        v["image_sourced"] = by_status.get("sourced", 0)
        v["image_wanted"] = by_status.get("wanted", 0)
        v["image_pairs"] = sum(1 for x in assets if x.get("role") == "correct")
        v["image_critical"] = sum(1 for x in assets if x.get("priority") == "critical")
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
    ("CLAUDE.md",              "opening_rules", r"(\d+) opening-grammar rules"),
    ("docs/reports/wp-6.2-opening-semantics.md", "opening_rules",
     r"\*\*`openings/grammar\.json`\*\* — (\d+) rules"),
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
    # WP-4.4's asset counts, in the four places that carried them by hand.
    ("CLAUDE.md",              "image_records",  r"(\d+) image records, \*\*\d+ sourced\*\*"),
    ("CLAUDE.md",              "image_sourced",  r"\d+ image records, \*\*(\d+) sourced\*\*"),
    ("CLAUDE.md",              "image_wanted",   r"proportion packs; (\d+) still wanted"),
    ("README.md",              "image_records",  r"(\d+) specified images, \d+ drawn"),
    ("README.md",              "image_sourced",  r"\d+ specified images, (\d+) drawn"),
    ("README.md",              "image_wanted",   r"\*\*(\d+) wanted and \d+ sourced\*\*"),
    ("README.md",              "image_sourced",  r"\*\*\d+ wanted and (\d+) sourced\*\*"),
    ("README.md",              "image_wanted",   r"^- \*\*The images\.\*\* (\d+) of \d+ asset records"),
    ("README.md",              "image_records",  r"^- \*\*The images\.\*\* \d+ of (\d+) asset records"),
    ("STATE-OF-THE-PROJECT.md", "image_wanted",  r"\*\*(\d+) wanted, \d+ sourced\*\*"),
    ("STATE-OF-THE-PROJECT.md", "image_sourced", r"\*\*\d+ wanted, (\d+) sourced\*\*"),
    ("docs/assets.md",         "image_records",  r"holds \*\*(\d+) records"),
    ("docs/assets.md",         "image_wanted",   r"records — (\d+) wanted and \d+ sourced"),
    ("docs/assets.md",         "image_sourced",  r"records — \d+ wanted and (\d+) sourced"),
    ("docs/assets.md",         "image_pairs",    r"sourced, (\d+) good/bad pairs"),
    ("docs/assets.md",         "image_critical", r"good/bad pairs, (\d+) critical"),
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
