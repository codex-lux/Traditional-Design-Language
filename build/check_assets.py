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

4. A BUILDING NAME TRACES TO AN EXEMPLAR, OR IT IS AN UNSOURCED CLAIM ABOUT SOMEBODY'S HOUSE.
   `provenance.building` is what `harvest_habs.py` SEARCHES ON, so a wrong one does not fail --
   it fetches a photograph of the wrong building and files it against a style. Nothing checked
   it: `name_asset_buildings.py` deals each record round its depicted node's own `exemplars`,
   and a hand-typed name that matches no exemplar was indistinguishable from a dealt one. The
   name and its location must both be an exemplar's, on a node the record says it depicts. And
   a building belongs only on a record that wants a PHOTOGRAPH of a real house: the assigner
   keyed on `role` once and gave 52 line-diagrams a real building, which is the defect this
   turns from a fixed bug into a standing rule.

5. NO LICENCE IS ASSERTED WITHOUT EVIDENCE. `license` is a conclusion a person draws;
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

def _exemplars():
    """node id -> its `exemplars`, from `name_asset_buildings.py` -- the module that WRITES the
    names, so the reader and the writer cannot drift into two answers about what an exemplar is."""
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    n = modcache.load("name_asset_buildings",
                      os.path.join(ROOT, "build", "name_asset_buildings.py"))
    return n.exemplars_by_node()


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
    # COMPILED ONCE, NOT REBUILT 1,850 TIMES. `jsonschema.validate(a, schema)` in this loop
    # was 36.1 s of check_all.py's 197 s -- 18% of the whole checker suite, spent building
    # the same validator object once per asset record. Compiled: 0.35 s. See
    # build/schema_validators.py, and CLAUDE.md's WP-10.1 entry for the same wrapper
    # measured at 17.9% of /api/plan/evaluate.
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import schema_validators
    validator = schema_validators.compiled(SCHEMA)
    assets = doc.get("assets") or []
    errs = []
    EX = _exemplars()

    for a in assets:
        aid = a.get("id", "<no id>")
        try:
            schema_validators.raise_first(validator, a)
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

        building = prov.get("building")
        if building:
            if a.get("kind") != "photograph":
                errs.append("%s: names the building %r and is kinded %r. A building belongs on a "
                            "photograph of one; a drawing of a rule has nothing to go and look at."
                            % (aid, building, a.get("kind")))
            elif a.get("role") == "incorrect":
                errs.append("%s: names the building %r on a `role: incorrect` record. The corpus "
                            "names buildings that exemplify a style and never ones that exemplify "
                            "a fault, so this is a claim about somebody's house." % (aid, building))
            else:
                nodes = (a.get("depicts") or {}).get("nodes") or []
                pool = [e for n_ in nodes for e in EX.get(n_, [])]
                hit = [e for e in pool if e.get("name") == building]
                if not pool:
                    errs.append("%s: names the building %r and depicts no node that records an "
                                "exemplar, so the name traces to nothing." % (aid, building))
                elif not hit:
                    errs.append("%s: names the building %r, which is not an exemplar of any node "
                                "it depicts (%s). A building name is what the harvester searches "
                                "on -- an untraceable one fetches a photograph of the wrong house."
                                % (aid, building, ", ".join(nodes) or "none"))
                elif prov.get("location") and not any(
                        e.get("location") == prov["location"] for e in hit):
                    errs.append("%s: names %r at %r; the exemplar records %r. The location is half "
                                "the query." % (aid, building, prov["location"],
                                                (hit[0].get("location") or "no location")))

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
    named = sum(1 for a in assets if (a.get("provenance") or {}).get("building"))
    print("%d asset record(s) valid; %s; every sourced record has the file it claims; "
          "%d name a building and every one of them is an exemplar of a node the record depicts."
          % (len(assets), ", ".join("%s %d" % (k, v) for k, v in sorted(by_status.items())), named))
    return 0


if __name__ == "__main__":
    sys.exit(main())
