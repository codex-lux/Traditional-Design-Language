#!/usr/bin/env python3
"""check_assets.py — the asset manifest, held to its own schema and its own words.

NOTHING VALIDATED THIS FILE. `schema/asset.schema.json` has existed since the layer was authored,
and the only code that reads it is `build/gen_assets.py`, which validates at GENERATION time --
so every edit made after generation, by hand or by `harvest_habs.py --write` or by
`link_asset_faults.py`, went in unchecked. `build/check_all.py` had no asset check at all. This is
the file five tools now write to and no tool read.

The four things it asserts, and why each one is here rather than assumed:

1. EVERY RECORD VALIDATES. jsonschema, which is what gen_assets.py does once and nothing does
   again.

2. `sourced` MEANS A FILE IS THERE. The schema's own gloss is "file present, unreviewed", and
   `harvest_habs.py` used to set `sourced` while writing only a URL, leaving `file` null -- a
   status contradicting the schema's definition of itself, on a record nobody would look at
   twice. The file must exist on disk and its sha256 and byte count must match what the record
   claims, because a record whose digest has drifted is a record describing something else.

3. A DRAWING IS NEVER KINDED `photograph`. A record carrying `generated_from` is a drawing of a
   rule; its `alt_text` opens "A {style} house showing...", which becomes a false claim the
   instant the file is a drawing. The plate itself must also say so -- an SVG this corpus
   generated and did not disclose is the same lie one layer down.

4. NO LICENCE IS ASSERTED WITHOUT EVIDENCE. `license` is a conclusion a person draws;
   `rights_evidence` is what a source actually said. A record carrying a licence stronger than
   `unknown` on material this project did not author must carry the evidence it was read from.
   The Library of Congress's rights sentence is byte-identical on a government photograph and on
   a HABS photograph OF a third party's copyrighted drawing, so the conclusion cannot be derived
   from the boilerplate and must be recorded as somebody's judgment.

Exit 0 clean, 1 on a failure, 3 if it could not evaluate (no jsonschema) -- which is COULD NOT
EVALUATE and is not a pass.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets", "manifest.json")
SCHEMA = os.path.join(ROOT, "schema", "asset.schema.json")

# A licence this project may assert about its own generated work without citing anyone.
OWN_WORK = ("owned",)
DRAWING_KINDS = ("detail-drawing", "line-diagram", "elevation", "section", "plan",
                 "measured-drawing", "hand-sketch", "render", "ai-generated")


def main():
    try:
        import jsonschema
    except ImportError:
        print("COULD NOT EVALUATE: jsonschema is not installed, so the manifest was not "
              "validated. That is an unjudged state and not a pass.")
        return 3

    doc = json.load(open(ASSETS))
    schema = json.load(open(SCHEMA))
    assets = doc.get("assets") or []
    errs = []

    for a in assets:
        aid = a.get("id", "<no id>")
        try:
            jsonschema.validate(a, schema)
        except jsonschema.ValidationError as e:
            errs.append("%s: %s" % (aid, e.message))
            continue

        prov = a.get("provenance") or {}
        f = a.get("file")

        if a.get("status") == "sourced":
            if not (f and f.get("path")):
                errs.append("%s: status `sourced` with no file. The schema defines sourced as "
                            "'file present, unreviewed'." % aid)
            else:
                # `file.path` has no pattern in the schema, and os.path.join DISCARDS ROOT
                # entirely if it is absolute. Build-time, repo-controlled data -- but this is
                # the traversal-primitive shape and it costs two lines to not have it.
                path = os.path.normpath(os.path.join(ROOT, f["path"]))
                if os.path.isabs(f["path"]) or not path.startswith(ROOT + os.sep):
                    errs.append("%s: file.path %r escapes the repository" % (aid, f["path"]))
                elif not os.path.exists(path):
                    errs.append("%s: names %s, which does not exist" % (aid, f["path"]))
                else:
                    data = open(path, "rb").read()
                    if f.get("sha256") and hashlib.sha256(data).hexdigest() != f["sha256"]:
                        errs.append("%s: the file's digest is not the one the record claims -- "
                                    "the record describes something else now" % aid)
                    if f.get("bytes") is not None and len(data) != f["bytes"]:
                        errs.append("%s: %d bytes on disk against %d recorded"
                                    % (aid, len(data), f["bytes"]))

        if a.get("generated_from"):
            if a.get("kind") == "photograph":
                errs.append("%s: carries `generated_from` and is kinded `photograph`. A drawing "
                            "of a rule is not a photograph of a building." % aid)
            elif a.get("kind") not in DRAWING_KINDS:
                errs.append("%s: carries `generated_from` and an unexpected kind %r"
                            % (aid, a.get("kind")))
            svg_path = os.path.normpath(os.path.join(ROOT, (f or {}).get("path") or ""))
            if f and f.get("path", "").endswith(".svg") and not os.path.exists(svg_path):
                # Reported, not raised. This used to open the file unconditionally, so a
                # `generated_from` record carrying a `file` at any status other than `sourced`
                # with the file missing produced a FileNotFoundError traceback instead of a
                # named failure -- a checker that crashes reports nothing at all.
                errs.append("%s: names %s, which does not exist" % (aid, f["path"]))
            elif f and f.get("path", "").endswith(".svg"):
                svg = open(svg_path).read()
                if "NOT A DRAWING OF A REAL BUILDING" not in svg:
                    errs.append("%s: the plate does not say it is generated. Prose beside an "
                                "image does not travel with it." % aid)

        lic = prov.get("license")
        if lic and lic not in ("unknown",) + OWN_WORK:
            if not prov.get("rights_evidence"):
                errs.append("%s: asserts license %r with no `rights_evidence`. A licence is a "
                            "conclusion; the evidence it was read from has to be on the record."
                            % (aid, lic))

    # EVERY GENERATED FILE MUST BE CLAIMED BY A RECORD. check_assets tested sourced -> file and
    # never file -> record, so `rm assets/manifest.json && python3 build/gen_assets.py` produced
    # 1,850 wanted records, orphaned all 73 SVGs on disk, and this checker exited 0 saying "every
    # sourced record has the file it claims" -- vacuously true, because there were none.
    import glob
    claimed = {a["file"]["path"] for a in assets if (a.get("file") or {}).get("path")}
    for p_ in sorted(glob.glob(os.path.join(ROOT, "assets", "generated", "*.svg"))):
        rel = os.path.relpath(p_, ROOT)
        if rel not in claimed:
            errs.append("%s is on disk and no record claims it. A file nothing points at is "
                        "either a deleted record or a regeneration that lost one." % rel)

    # The header's own tally, which three writers recompute and could disagree about.
    by_status = {}
    for a in assets:
        by_status[a.get("status")] = by_status.get(a.get("status"), 0) + 1
    claimed = (doc.get("counts") or {}).get("by_status") or {}
    if claimed != by_status:
        errs.append("counts.by_status says %r, the records say %r" % (claimed, by_status))
    if (doc.get("counts") or {}).get("total") != len(assets):
        errs.append("counts.total says %r, the file holds %d"
                    % ((doc.get("counts") or {}).get("total"), len(assets)))

    if errs:
        for e in errs[:40]:
            print("  x " + e)
        if len(errs) > 40:
            print("  ... and %d more" % (len(errs) - 40))
        print("\n%d asset problem(s)" % len(errs))
        return 1
    print("%d asset record(s) valid; %s; every sourced record has the file it claims."
          % (len(assets), ", ".join("%s %d" % (k, v) for k, v in sorted(by_status.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
