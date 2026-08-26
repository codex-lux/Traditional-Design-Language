#!/usr/bin/env python3
"""Every style can be put on the map, and at the finest precision its record supports — OQ 65.

    python3 build/check_gazetteer.py             # the three ratchet numbers
    python3 build/check_gazetteer.py --unplaced  # the styles the gazetteer cannot place
    python3 build/check_gazetteer.py --coarse    # placed, but only at country precision
    python3 build/check_gazetteer.py --strict    # exit nonzero if any ratchet has slipped

WHAT THIS IS ABOUT. The Phylogeny's map reading (WP-5.6) draws where each style arose. The
corpus holds NO coordinates — it says "Tidewater Virginia", and "the James, York, Rappahannock
and Potomac river plantations" — so the points come from `workbench/app/src/data/gazetteer.js`,
which is interface furniture keyed on those prose names. None of it is corpus data and none of
it may migrate into styles/*.json as measured fact; that is the laundering CLAUDE.md forbids.

The failure this guards is quiet by construction. A style whose regions and hearth name nothing
the gazetteer knows is reported by the map as UNPLACED — correctly, because inventing a point is
worse than admitting there is none. But "listed as unplaced" is a line in a panel nobody reads,
so a style added tomorrow can fall off the map and stay off it indefinitely. This makes that
fail a build instead.

THREE NUMBERS.
  `unplaced`  styles the gazetteer cannot place at all. Must stay 0: the map would be silently
              incomplete, and the corpus is the thing being described.
  `coarse`    styles placed only at country precision. A country is not a hearth, and a mark
              there says so by being drawn hollow — but most such styles are that way only
              because nobody read their hearth, so the number is worth watching.
  `unread`    styles whose `geography.hearth` names somewhere the gazetteer does not know, and
              which therefore sit coarser on the map than their own record could put them.
              This is the work list: each one is a place name to add, not a fact to invent.

COARSE IS NOT ALWAYS WRONG, which is why it is a ratchet and not an assertion of zero. A family
or a tradition is an abstraction over styles and has no birthplace; `victorian` and `british-isles`
are correctly country-wide. And two styles say so in their own hearth — `neo-eclectic`'s reads
"No design hearth; the style was generated inside production builders' plan departments", and
`craftsman-bungalow`'s "Streetcar suburbs nationwide; the type is defined by its distribution
channel". Those are records telling the truth, and a check that demanded a point for them would
be demanding a lie. They are counted as `by_record` and excluded from the ratchet.

This file reads the JS gazetteer directly rather than duplicating it. The alternative — a second
copy in Python — is exactly how two halves of the citation grammar came to disagree about dots.
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAZ = os.path.join(ROOT, "workbench", "app", "src", "data", "gazetteer.js")
STYLES = os.path.join(ROOT, "styles")

# Ratchets. These may only improve. Raising one is a decision somebody has to make on
# purpose, in a commit message, which is the whole point of pinning them here.
#
# All three are zero, which is the state OQ 65 reached and not the state it started in:
# 164 of 164 styles placed, every country-wide mark country-wide by its own record, and
# every hearth sentence in the corpus readable. A new style that names a place this
# gazetteer does not know moves one of these off zero and fails the build, which is the
# entire point — the map's own report would merely have listed it and gone quiet.
MAX_UNPLACED = 0
MAX_COARSE = 0
MAX_UNREAD = 0

# "Has no hearth by its own account" is decided by `statesNoHearth` in gazetteer.js and asked
# for through the bridge below — not re-spelled here. There were three copies of that regex
# and two of them already disagreed.


COULD_NOT_EVALUATE = 3

# The JS is asked to place every style and hand back the answer. This file used to
# re-implement placeByRegions/placeByHearth/regionAnchors/degreesApart in Python and compare
# nothing — a second copy of the ALGORITHM, which is precisely the trap its own docstring
# cited about the citation grammar. It parsed the JS data table and then duplicated the logic
# that reads it, so `CONTRADICTION_DEGREES` was a named constant on one side and a bare 45 on
# the other, and an edit to either would have moved the map while this check reported OK.
# An adversarial audit found the two copies still agreed on all 164 styles and one classifier
# regex already disagreeing. There is now one implementation, and this asks it.
PLACE_JS = r"""
import { placeStyle, placeByHearth, regionAnchors, statesNoHearth } from '%s';
import { readdirSync, readFileSync } from 'node:fs';
const out = {};
for (const f of readdirSync('%s').filter((f) => f.endsWith('.json'))) {
  const d = JSON.parse(readFileSync('%s/' + f, 'utf8'));
  const g = d.geography || {};
  const p = placeStyle(g.regions || [], g.hearth);
  // Whether the hearth was READABLE at all, which is a different question from whether it
  // won: a style whose regions already name something finer has a perfectly readable hearth.
  const readable = !!placeByHearth(g.hearth, regionAnchors(g.regions || []));
  out[d.id] = {
    rank: d.rank,
    hearth: g.hearth || null,
    hearthRead: readable,
    statedNoHearth: statesNoHearth(g.hearth),
    placed: p ? { precision: p.precision, region: p.region, via: p.via || 'regions' } : null,
  };
}
process.stdout.write(JSON.stringify(out));
"""


def placements():
    """Ask gazetteer.js where every style goes. Exits 3 (COULD NOT EVALUATE) without node.

    Node is not a dependency of the corpus — the data and every other checker run on the
    standard library alone, deliberately. So its absence is a named unjudged state, the same
    way the CAD selftests report N/EV without ezdxf. It is never a pass.
    """
    src = PLACE_JS % (GAZ, STYLES, STYLES)
    try:
        proc = subprocess.run(["node", "--input-type=module", "-e", src],
                              capture_output=True, text=True, cwd=ROOT, timeout=120)
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"COULD NOT EVALUATE: cannot run node to read the gazetteer ({e}). "
              f"The placement logic lives in {os.path.relpath(GAZ, ROOT)} and this check "
              f"asks it rather than keeping a second copy — so without node it has no "
              f"answer, which is not the same as a passing one.", file=sys.stderr)
        sys.exit(COULD_NOT_EVALUATE)
    if proc.returncode != 0:
        print("FAIL: gazetteer.js could not be loaded or threw:\n" + proc.stderr.strip(),
              file=sys.stderr)
        sys.exit(1)
    return json.loads(proc.stdout)


def gazetteer_size():
    """How many names the table holds — reported so a parse cliff reads as a parse cliff.

    Only the COUNT is read here, and only for the floor assertion below; nothing is placed
    from this. A reformat (prettier's double quotes, a multi-line array) drops it to zero, and
    without the floor the failure surfaced as "164 styles are unplaceable — go place them"
    when the truth was "somebody ran a formatter".
    """
    src = open(GAZ, encoding="utf-8").read()
    return len(re.findall(r"^\s*(?:'[^']+'|\"[^\"]+\")\s*:\s*\[", src, re.M))


# The table has held ~275 names since OQ 65. Well below that is a PARSE failure, not an
# authoring one: prettier's double quotes or a multi-line array drops the reader to zero, and
# without this the run reported "164 styles are unplaceable — go place them" when the truth
# was that somebody had run a formatter. Found by an adversarial audit.
MIN_GAZETTEER_ENTRIES = 200


def survey():
    placed = placements()
    size = gazetteer_size()
    if size < MIN_GAZETTEER_ENTRIES:
        print(f"FAIL: only {size} gazetteer entries parsed out of "
              f"{os.path.relpath(GAZ, ROOT)}, and there should be at least "
              f"{MIN_GAZETTEER_ENTRIES}. This is a PARSE failure, not a missing place: the "
              f"reader expects `'Name': [lat, lon, 'precision'],` one per line, in single "
              f"quotes. A reformat (prettier, a multi-line array) breaks it. Fix the reader "
              f"rather than the data.", file=sys.stderr)
        sys.exit(1)
    unplaced, coarse, unread, by_record = [], [], [], []
    counts = {"locality": 0, "region": 0, "country": 0}

    for sid, rec in sorted(placed.items()):
        hearth = rec.get("hearth")
        p = rec.get("placed")
        if p is None:
            unplaced.append(sid)
            continue
        counts[p["precision"]] += 1

        if p["precision"] == "country":
            # An abstraction, or a record that says it has no hearth, is correctly coarse.
            if rec.get("rank") in ("family", "tradition") or rec.get("statedNoHearth"):
                by_record.append(sid)
            else:
                coarse.append(sid)

        # A hearth sentence the gazetteer found NO place name in at all. Not "a hearth that
        # did not yield a town" — "The Peloponnese and Attica" is read correctly and the
        # answer is a region, because that is what the sentence names.
        if hearth and not rec.get("hearthRead") and not rec.get("statedNoHearth"):
            unread.append((sid, hearth[:90]))

    return {"gazetteer_entries": size, "counts": counts, "unplaced": unplaced,
            "coarse": coarse, "by_record": by_record, "unread": unread}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--unplaced", action="store_true")
    ap.add_argument("--coarse", action="store_true")
    ap.add_argument("--unread", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    r = survey()
    if a.json:
        print(json.dumps(r, indent=2))
        return 0

    total = sum(r["counts"].values()) + len(r["unplaced"])
    print(f"gazetteer: {r['gazetteer_entries']} place names, placing {total - len(r['unplaced'])} "
          f"of {total} styles")
    print(f"  by precision: {r['counts']['locality']} locality · {r['counts']['region']} region "
          f"· {r['counts']['country']} country")
    print(f"  unplaced {len(r['unplaced']):>3}  (ratchet {MAX_UNPLACED})   "
          f"— the map cannot draw these at all")
    print(f"  coarse   {len(r['coarse']):>3}  (ratchet {MAX_COARSE})   "
          f"— country-wide, and not by the record's own account")
    print(f"  unread   {len(r['unread']):>3}  (ratchet {MAX_UNREAD})   "
          f"— a hearth naming somewhere the gazetteer does not know")
    print(f"  by_record{len(r['by_record']):>3}        "
          f"— correctly country-wide: a family, a tradition, or a stated absence of hearth")

    if a.unplaced:
        print("\nunplaced:")
        for i in r["unplaced"]:
            print("  ", i)
    if a.coarse:
        print("\ncoarse (country precision, not by the record's account):")
        for i in r["coarse"]:
            print("  ", i)
    if a.unread:
        print("\nunread hearths — each is a place name to ADD to the gazetteer, never a "
              "coordinate to invent for the corpus:")
        for i, h in r["unread"]:
            print(f"   {i:<34} {h}")

    if a.strict:
        bad = []
        if len(r["unplaced"]) > MAX_UNPLACED:
            bad.append(f"unplaced {len(r['unplaced'])} > {MAX_UNPLACED}: {r['unplaced']}")
        if len(r["coarse"]) > MAX_COARSE:
            bad.append(f"coarse {len(r['coarse'])} > {MAX_COARSE}")
        if len(r["unread"]) > MAX_UNREAD:
            bad.append(f"unread {len(r['unread'])} > {MAX_UNREAD}")
        if bad:
            print("\nFAIL — a ratchet slipped. Either place the new style (add its region or "
                  "hearth name to workbench/app/src/data/gazetteer.js) or, if it genuinely "
                  "has no hearth, say so in its own record and this check will count it as "
                  "by_record.", file=sys.stderr)
            for b in bad:
                print("  " + b, file=sys.stderr)
            return 1
        print("\nOK — every style is placeable and no ratchet has slipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
