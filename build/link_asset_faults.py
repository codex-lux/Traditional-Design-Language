#!/usr/bin/env python3
"""link_asset_faults.py — join the asset records to the faults they are evidence about.

`schema/asset.schema.json` has carried a `depicts.faults` array since the layer was authored,
`schema/fault.schema.json` has carried the reverse `assets` array, and BOTH WERE EMPTY ON EVERY
RECORD -- 0 of 322 assets and 0 of 210 faults. The Fault Corpus surface queries
`api.assets({fault: id})` and so has shown "no image records are filed against this fault yet"
for every fault in the corpus since it was built, while 322 records sat one join away. The
component that would render them was unreachable in the shipped app.

THE RULE, stated once and applied mechanically:

    an asset is evidence about a fault when the fault names a slot the asset depicts
    AND the fault applies to a style the asset depicts.

Both halves are load-bearing. Slot alone gives 2,156 links and puts fourteen faults on a single
porch record -- `porch_support` is named by faults about columns, about posts, about rails and
about spacing, and an image of a turned post is not evidence about all of them. Adding the style
test takes it to 209 links over 94 assets reaching 20 distinct faults, because a fault written
for Queen Anne does not become evidence because a Georgian record happens to share a slot id.

WHAT THIS IS NOT. It is a DERIVATION, not an authored judgment, and it is recomputable from the
two records it joins -- which is why it lives in a script and says so rather than being typed
into the manifest. It does not claim the image is a good illustration of the fault; it claims
the fault and the image are about the same slot on the same style. A person deciding which of
Westover's photographs best shows a fault is doing something this cannot do.

Both halves of a good/bad pair link. The `correct` record is evidence about the fault too --
it is what the fault says the building should have done.

    python3 build/link_asset_faults.py            # report, write nothing
    python3 build/link_asset_faults.py --write    # write depicts.faults
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets", "manifest.json")

sys.path.insert(0, os.path.join(ROOT, "build"))
import manifest_io  # noqa: E402  -- the one atomic writer for this file


def load_faults():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "faults", "*.json"))):
        try:
            out.append(json.load(open(p)))
        except Exception as e:
            print("  skipped %s — %s" % (os.path.basename(p), e))
    return out


def links_for(asset, faults):
    """The fault ids this asset is evidence about. Sorted, so a rerun is a no-op diff."""
    dp = asset.get("depicts") or {}
    slots = set(dp.get("slots") or [])
    nodes = set(dp.get("nodes") or [])
    if not slots or not nodes:
        return []
    hit = []
    for f in faults:
        if not (slots & set(f.get("slots") or [])):
            continue
        if not (nodes & set(f.get("applies_to") or [])):
            continue
        hit.append(f["id"])
    return sorted(hit)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="write depicts.faults into the manifest")
    a = ap.parse_args()

    faults = load_faults()
    doc = json.load(open(ASSETS))
    total = changed = 0
    reached = set()
    for asset in doc["assets"]:
        ids = links_for(asset, faults)
        had = (asset.get("depicts") or {}).get("faults")
        total += len(ids)
        reached.update(ids)
        # `if not ids: continue` meant a record whose links all disappeared -- a fault's `slots`
        # or `applies_to` edited -- kept its stale array forever, was never counted as changed,
        # and so the report said "0 record(s) would change" against a file that was wrong.
        # gen_assets then carried the stale array forward, so nothing could ever clear it.
        if had == (ids or None) or (not ids and not had):
            continue
        changed += 1
        if a.write:
            dep = asset.setdefault("depicts", {})
            if ids:
                dep["faults"] = ids
            else:
                dep.pop("faults", None)

    linked = sum(1 for x in doc["assets"] if links_for(x, faults))
    print("%d of %d asset(s) are evidence about at least one fault" % (linked, len(doc["assets"])))
    print("%d link(s) in total, reaching %d of %d fault(s)" % (total, len(reached), len(faults)))
    print("%d record(s) would change" % changed)
    if not a.write:
        print("\nreport only — pass --write to apply")
        return 0
    if changed:
        manifest_io.write_manifest(doc, ASSETS)
        print("wrote %s" % os.path.relpath(ASSETS, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
