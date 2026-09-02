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
    # The ⌘K index, hand-typed in CLAUDE.md and policed by nothing.
    try:
        import importlib.util as _il
        _sp = _il.spec_from_file_location(
            "_corpus_for_counts", os.path.join(ROOT, "workbench", "server", "corpus.py"))
        _c = _il.module_from_spec(_sp); _sp.loader.exec_module(_c)
        _idx = _c.search_index()
        v["search_index"] = len(_idx if isinstance(_idx, list)
                                else (_idx.get("items") or _idx.get("entries") or _idx))
    except Exception:
        pass                      # optional: the workbench's deps are not the corpus's

    if "partis" in v:
        v["parti_count"] = v["partis"]

    # OQ 51's four numbers. They live in prose in CLAUDE.md, STATE-OF-THE-PROJECT.md, README.md
    # and docs/inheritance.md, and until now NOTHING derived them: `check_inheritance.py --strict`
    # pins them against its own RATCHET, which stops the corpus getting worse but says nothing
    # about whether the DOCUMENTS still describe it. WP-8.7 moved all four and had to find the
    # six prose sites by grep. Guarded from here.
    #
    # Read through modcache from the checker that owns them, never re-derived: `measure()` is 200
    # lines of cascade walking and a second copy would drift, which is the failure this whole file
    # exists to catch one layer up.
    tpath = os.path.join(ROOT, "dist", "taxonomy.json")
    if os.path.exists(tpath):
        sys.path.insert(0, os.path.join(ROOT, "build"))
        import modcache
        ci = modcache.load("check_inheritance", os.path.join(ROOT, "build", "check_inheritance.py"))
        _b, _gaps, _packs, _dec = ci.measure(ci.load())
        _applies = ci.applies_to_index()
        _un = [t for t in _gaps if t[0] not in _applies.get(t[3], ())]
        v["role_gaps"] = len(_gaps)
        v["inherited_packs"] = len(_packs)
        v["unendorsed"] = len(_un)
        v["endorsed"] = len(_gaps) - len(_un)
        v["declined"] = len(_dec)
        v["judged"] = v["endorsed"] + v["declined"]

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

        # WP-4.4's OTHER four numbers, and the reason they are here (2 Sep 2026): the naming
        # step finished on 31 Aug and its own figures went stale in eight files within two
        # days -- 322, 845, 330 and 188 against a live 786, 305 and 180 -- while this checker
        # stood one field away computing `image_records` from the same file. Every one of them
        # sat in exactly the fields no claim covered.
        #
        # The query and the charter test are the HARVESTER'S, loaded rather than restated:
        # `query_for` is what decides whether a record can be searched at all, and
        # `outside_the_survey` is the US-state allowlist. Re-deriving either here would be a
        # second spelling of a rule that already has one, which is how the citation grammar
        # came to disagree with itself in three places.
        v["image_building_named"] = sum(
            1 for x in assets if (x.get("provenance") or {}).get("building"))
        v["image_never_harvestable"] = sum(1 for x in assets if x.get("role") == "incorrect")
        sys.path.insert(0, os.path.join(ROOT, "build"))
        import modcache
        H = modcache.load("harvest_habs", os.path.join(ROOT, "build", "harvest_habs.py"))
        queries = {}
        for x in assets:
            if x.get("status") != "wanted":
                continue
            q = H.query_for(x)
            if q:
                queries[q] = (x.get("provenance") or {}).get("location")
        v["image_queries"] = len(queries)
        v["image_queries_us"] = sum(
            1 for q, loc in queries.items() if not H.outside_the_survey(loc))
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
    # Computed and never claimed until now: the checker was producing these and no row consumed
    # them, so a number in prose could disagree with a value the checker already had in hand.
    # Plus the search index size, which was hand-typed at 665 against a real 666.
    # `opening_placement_rules` and `no_interior_role` are computed and still unclaimed --
    # deliberately: no document states either, and writing a sentence into the prose so that a
    # checker has something to check would be the wrong way round.
    ("CLAUDE.md",              "search_index",   r"/api/search/index` \((\d+) named things"),
    # Keyed `parti_count`, NOT `partis`: `test_parti_confinement.py` scans build/ for any line
    # matching `"partis", <identifier>`, which is what a path join looks like, and a CLAIMS tuple
    # whose key is the directory name followed by a raw-string prefix is indistinguishable from
    # one. The guard is right; the key is what moves.
    ("CLAUDE.md",              "parti_count",    r"\*\*(\d+) partis naming \d+ of \d+ styles"),
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
    # The four WP-4.4 numbers that went stale in eight files inside two days (2 Sep 2026).
    # PLAN-OF-ACTION.md joins the guarded set here: it carried three of the four and was not in
    # this list at all, which is why its Status block could say 845/330/188 against a live
    # 786/305/180 while `check_counts.py` reported 0 stale in the same run.
    ("CLAUDE.md",              "image_building_named", r"round its own `exemplars` and (\d+) of$"),
    ("CLAUDE.md",              "image_records",        r"^   (\d+) name a building, across \d+ queries"),
    ("CLAUDE.md",              "image_queries",        r"^   \d+ name a building, across (\d+) queries of which"),
    ("CLAUDE.md",              "image_queries_us",     r"across \d+ queries of which (\d+) are inside HABS"),
    ("README.md",              "image_building_named", r"indexes wrongness\. (\d+) name a real$"),
    ("README.md",              "image_queries",        r"^  building to look for, across (\d+) distinct queries;"),
    ("README.md",              "image_never_harvestable", r"Of the rest, \*\*(\d+) can never be harvested"),
    ("README.md",              "image_queries_us",     r"distinct queries; (\d+) of those are in the United States"),
    ("PLAN-OF-ACTION.md",      "image_building_named", r"\*\*(\d+) records now name a real building\*\*"),
    ("PLAN-OF-ACTION.md",      "image_queries",        r"name a real building\*\* across (\d+) distinct queries"),
    ("PLAN-OF-ACTION.md",      "image_queries_us",     r"named eleven; (\d+) of those queries are within HABS"),
    ("STATE-OF-THE-PROJECT.md", "image_records",       r"\*\*The image layer: (\d+) records,"),
    ("STATE-OF-THE-PROJECT.md", "image_sourced",       r"\*\*The image layer: \d+ records, (\d+) files,"),
    ("STATE-OF-THE-PROJECT.md", "image_building_named", r"\d+ records, \d+ files, (\d+) naming a building\*\*"),
    ("STATE-OF-THE-PROJECT.md", "image_building_named", r"\*\*(\d+) name a real building to go and look for\*\*"),
    ("STATE-OF-THE-PROJECT.md", "image_queries",        r"own `exemplars`, across (\d+) distinct queries"),
    ("STATE-OF-THE-PROJECT.md", "image_queries_us",     r"distinct queries of which (\d+) are inside HABS"),
    ("STATE-OF-THE-PROJECT.md", "image_never_harvestable", r"name none, (\d+) are `role: incorrect`"),
    ("STATE-OF-THE-PROJECT.md", "image_records",       r"`assets/manifest\.json`, (\d+) records over \d+ style nodes"),
    # OQ 51's four, in the six places the prose states them (WP-8.7, 2 Sep 2026).
    ("CLAUDE.md",              "role_gaps",       r"pins three ceilings that may only go down -- \*\*(\d+) role_gaps\*\*"),
    ("CLAUDE.md",              "inherited_packs", r"\*\*([\d,]+) inherited_packs\*\*"),
    ("CLAUDE.md",              "unendorsed",      r"\*\*(\d+) unendorsed\*\* -- and one FLOOR"),
    ("CLAUDE.md",              "judged",          r"\*\*judged (\d+)\*\* \(endorsed \+ declined\)"),
    ("CLAUDE.md",              "inherited_packs", r"is the one with ([\d,]+) instances"),
    ("STATE-OF-THE-PROJECT.md", "role_gaps",      r"Measured: \*\*(\d+) \(node, role\) pairs\*\*"),
    ("STATE-OF-THE-PROJECT.md", "unendorsed",     r"of which \*\*(\d+) involve a pack whose own"),
    ("STATE-OF-THE-PROJECT.md", "inherited_packs", r"and \*\*([\d,]+)\*\* pack-arrivals purely by descent"),
    ("STATE-OF-THE-PROJECT.md", "declined",       r"judged by somebody, and (\d+) have now been DECLINED"),
    ("STATE-OF-THE-PROJECT.md", "inherited_packs", r"is the one with ([\d,]+) instances"),
    ("README.md",              "role_gaps",       r"first adjudication pass 2 Sep\): (\d+) role gaps"),
    ("README.md",              "unendorsed",      r"role gaps, (\d+) of them never judged"),
    ("README.md",              "judged",          r"of them never judged, (\d+) judged"),
    ("docs/inheritance.md",    "inherited_packs", r"declines took `inherited_packs` to ([\d,]+) and `judged`"),
    ("docs/inheritance.md",    "judged",          r"and `judged` to (\d+), and moved `unendorsed`"),
    ("docs/inheritance.md",    "unendorsed",      r"moved `unendorsed`\nby four — 249 to (\d+)"),
    # THE TRAPS LIST, AND IT IS THE REASON THIS BLOCK EXISTS AT ALL. The claim above matches the
    # meter paragraph 700 lines lower; CLAUDE.md's traps list carried its OWN copy of
    # `unendorsed` and went stale at 249 while this checker printed "0 stale" over it -- which is
    # verbatim the finding WP-4.4's half of this same branch published ("every stale figure sat
    # in a field no claim covered"), reproduced in the same file by the commit that fixed it.
    # A number stated twice needs claiming twice.
    ("CLAUDE.md",              "unendorsed",      r"the live backlog is \*\*(\d+) unjudged\*\* gaps"),
    # The sentence the plan named and the first pass pointed a claim at a DIFFERENT file instead.
    ("CLAUDE.md",              "image_never_harvestable", r"still wanted, and (\d+) of those can never be harvested"),
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
            if key not in v:
                # COULD NOT EVALUATE, named. The OQ 51 values need `dist/taxonomy.json`, which
                # `check_all` builds first and which is tracked -- but a bare run in a tree where
                # it is absent used to raise KeyError out of `str(v[key])`, so a checker whose
                # whole subject is honest reporting crashed instead of saying what it could not
                # judge. Unjudged is not passed, and it is not a traceback either.
                missing.append(f"{path}: {key} COULD NOT BE EVALUATED -- "
                               f"run build/build.py first (dist/taxonomy.json is missing)")
                continue
            rx = re.compile(pattern, re.M)
            hits = list(rx.finditer(text))
            if not hits:
                missing.append(f"{path}: no match for {key} -- pattern '{pattern}' has rotted")
                continue
            want = str(v[key])
            # REVERSE, and this is a fix rather than a style. `hits` is materialised once, so
            # every span in it indexes the text as it was BEFORE any rewrite. Rewriting forwards
            # shifts every later span by len(want) - len(got), and the next write lands off by
            # that much: `**311 wanted, 11 sourced**` became `*17771 wanted, 11 sourced**` in
            # STATE-OF-THE-PROJECT.md, where one pattern matched two lines. The old code carried
            # the comment `# offsets moved` and then recompiled the regex, which does nothing --
            # the list was already built. A guard that names the problem and does not address it.
            # Writing highest-offset-first leaves every remaining span valid.
            for m in reversed(hits):
                checked += 1
                got = m.group(1)
                # A THOUSANDS SEPARATOR IS FORMATTING, NOT A DIFFERENT NUMBER. `3,341` in prose
                # against a computed 3341 is not staleness, and treating it as such would either
                # fail the build forever or force the prose to write 3341 to suit a checker.
                # Compared without separators; rewritten under --fix in the form the sentence
                # already uses, so `--fix` never reformats a number it was only asked to correct.
                if got.replace(",", "") == want.replace(",", ""):
                    continue
                if "," in got and want.isdigit():
                    want_here = f"{int(want):,}"
                else:
                    want_here = want
                if got != want_here:
                    stale.append(f"{path}: {key} says {got}, data says {want_here}")
                    if args.fix:
                        a_, b_ = m.span(1)
                        text = text[:a_] + want_here + text[b_:]
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
