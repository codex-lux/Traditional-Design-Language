#!/usr/bin/env python3
"""name_asset_buildings.py — give each asset record a real building to go and look for.

WP-4.4's own status block names this as the step that needs no network: without it every harvest
query degrades to a search on the style's NAME, so every record about a style asks for the same
thing and takes the same answer. `build/harvest_habs.py` skips such records rather than searching on a style name, and that
skip is why this exists.

It was done by hand for 161 records in commit `347d0ab`, when the manifest covered three style
nodes. The manifest now covers 142, so it is a script.

TWO RULES, AND THE SECOND IS THE ONE THAT WAS LEARNED THE HARD WAY.

1. ONLY A RECORD THAT CAN HAVE A BUILDING GETS ONE. `role: incorrect` never does. The corpus
   names buildings that exemplify a STYLE and never ones that exemplify a FAULT, so there is no
   exemplar to draw on, and naming a real house as an instance of an error would be both
   unsourced and a claim about somebody's home. Those records keep no building and the harvester
   goes on skipping them, correctly.

2. ROUND-ROBIN, NOT FIRST. A first pass over the original 161 took each node's FIRST exemplar and
   put 151 of them on Westover -- one building standing for a whole style's worth of slots, which
   is the degeneracy `harvest_habs.py`'s own guard exists to prevent, arriving by a different
   road. Records are sorted by id and dealt round the node's exemplars in order, so the
   assignment is deterministic, reproducible, and spread.

It never overwrites a building a record already carries: the 161 assigned by hand stay as they
were, and a rerun is a no-op on them.

    python3 build/name_asset_buildings.py           # report, write nothing
    python3 build/name_asset_buildings.py --write
"""
import argparse
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets", "manifest.json")

sys.path.insert(0, os.path.join(ROOT, "build"))
import manifest_io  # noqa: E402  -- the one atomic writer for this file

# THE QUESTION IS PHOTOGRAPH-OR-DRAWING, AND `role` DOES NOT ANSWER IT. `role` says
# correct/incorrect; `kind` says what sort of picture the record wants. Keying on role gave a
# real building to 52 line-diagrams whose own alt_text reads "No historical precedent exists for
# this slot, so there is nothing to photograph and the drawing has to carry the argument", and to
# 7 code-conflict comparison drawings. `harvest_habs.py` then keys on `provenance.building`, so
# --live would have spent rate-limited requests on them and stamped a real HABS survey's number,
# author and rights statement onto a drawing of an invented rule.
#
# A record gets a building when it wants a PHOTOGRAPH of one and is not depicting a fault.
NAMEABLE_KINDS = ("photograph",)
UNNAMEABLE_ROLES = ("incorrect",)


def exemplars_by_node():
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        ex = [e for e in (d.get("exemplars") or [])
              if isinstance(e, dict) and e.get("name")]
        if ex:
            out[d["id"]] = ex
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="write provenance.building and location")
    a = ap.parse_args()

    ex = exemplars_by_node()
    doc = json.load(open(ASSETS))

    # Group the nameable, unnamed records by the node they depict, sorted by id so the deal is
    # deterministic across runs and machines.
    todo = collections.defaultdict(list)
    for rec in doc["assets"]:
        if rec.get("kind") not in NAMEABLE_KINDS or rec.get("role") in UNNAMEABLE_ROLES:
            continue
        if (rec.get("provenance") or {}).get("building"):
            continue
        nodes = (rec.get("depicts") or {}).get("nodes") or []
        node = next((n for n in nodes if n in ex), None)
        if node:
            todo[node].append(rec)

    assigned = 0
    would_gain = set()
    spread = collections.Counter()
    for node in sorted(todo):
        pool = ex[node]
        for i, rec in enumerate(sorted(todo[node], key=lambda r: r["id"])):
            e = pool[i % len(pool)]
            spread[node] += 1
            assigned += 1
            would_gain.add(rec["id"])
            if a.write:
                prov = rec.setdefault("provenance", {})
                prov["building"] = e["name"]
                if e.get("location"):
                    prov["location"] = e["location"]

    # What is left, and why -- never a silent remainder, and never a remainder counted BEFORE the
    # assignment it is meant to describe. The first version of this loop ran over the pre-write
    # state, so on a dry run the 684 records about to be named were reported as "its style records
    # no exemplars" -- a report that was wrong about exactly the records the run was for.
    unnamed = collections.Counter()
    for rec in doc["assets"]:
        if (rec.get("provenance") or {}).get("building") or rec["id"] in would_gain:
            continue
        if rec.get("role") == "incorrect":
            unnamed["role: incorrect — the corpus names no building for a fault"] += 1
        elif rec.get("kind") != "photograph":
            unnamed["not a photograph — a drawing of a rule needs no building"] += 1
        elif not ((rec.get("depicts") or {}).get("nodes") or []):
            unnamed["depicts no style node"] += 1
        else:
            unnamed["its style records no exemplars"] += 1

    named_after = sum(1 for r in doc["assets"]
                      if (r.get("provenance") or {}).get("building") or r["id"] in would_gain)
    print("%d record(s) would gain a building, across %d style node(s)" % (assigned, len(todo)))
    print("%d of %d record(s) would then name one" % (named_after, len(doc["assets"])))
    print("still unnamed, by reason:")
    for why, n in unnamed.most_common():
        print("  %5d  %s" % (n, why))
    worst = spread.most_common(3)
    if worst:
        print("busiest nodes: " + ", ".join("%s %d" % (k, v) for k, v in worst))

    if not a.write:
        print("\nreport only — pass --write to apply")
        return 0
    manifest_io.write_manifest(doc, ASSETS)
    print("wrote %s" % os.path.relpath(ASSETS, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
