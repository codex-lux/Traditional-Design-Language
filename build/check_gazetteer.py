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
import math
import os
import re
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

PRECISION_RANK = {"locality": 0, "region": 1, "country": 2}
# A hearth that says there is no hearth. Matched on the record's own words.
NO_HEARTH = re.compile(r"no (single |design )?hearth|nationwide", re.I)


def load_gazetteer(path=GAZ):
    """Parse the JS object literal. Deliberately not an import and not a duplicate.

    The entries are `'Name': [lat, lon, 'precision'],` — one per line, by construction of
    that file. Anything that does not match that shape is skipped, and the count is
    reported so a reformat that breaks the parse shows up as a cliff rather than as a
    silent zero.
    """
    src = open(path, encoding="utf-8").read()
    body = src[src.index("export const GAZETTEER"):]
    entry = re.compile(
        r"^\s*(?:'([^']+)'|\"([^\"]+)\")\s*:\s*\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*,\s*'(\w+)'\s*\]",
        re.M)
    out = {}
    for m in entry.finditer(body):
        name = m.group(1) if m.group(1) is not None else m.group(2)
        out[name] = (float(m.group(3)), float(m.group(4)), m.group(5))
    return out


def _styles():
    for f in sorted(os.listdir(STYLES)):
        if f.endswith(".json"):
            yield json.load(open(os.path.join(STYLES, f), encoding="utf-8"))


def _degrees_apart(hit, anchor):
    dlat = hit[0] - anchor[0]
    dlon = (hit[1] - anchor[1]) * math.cos(math.radians((hit[0] + anchor[0]) / 2))
    return math.hypot(dlat, dlon)


def _place_by_regions(gaz, regions):
    best = None
    for r in regions or []:
        hit = gaz.get(r) or gaz.get(str(r).strip())
        if not hit:
            continue
        rank = PRECISION_RANK[hit[2]]
        if best is None or rank < best[0]:
            best = (rank, hit, r)
            if rank == 0:
                break
    return best


def _anchors(gaz, regions):
    """Every point the style's own regions vouch for."""
    out = []
    for r in regions or []:
        hit = gaz.get(r) or gaz.get(str(r).strip())
        if hit:
            out.append((hit[0], hit[1]))
    return out


def _place_by_hearth(gaz, hearth, anchors):
    """The same reading placeByHearth does in the app, anchor check included: a hearth may
    SHARPEN a region, never contradict one — where "contradict" means far from EVERY region
    the style names, not merely from the finest. That distinction is load-bearing.
    `churrigueresque` names Spain, Mexico and the Spanish Americas, and its hearth reads
    "Madrid, Salamanca and Andalusia"; against the finest region alone Madrid looked like a
    contradiction. Against all of them, Spain vouches for it. And
    `dutch-colonial-american` still refuses Amsterdam, because all six of its regions are
    American — resolving the sentence to Albany, which is what it meant."""
    if not hearth:
        return None
    text = hearth.lower()
    best = None
    for name in sorted(gaz, key=len, reverse=True):
        hit = gaz[name]
        rank = PRECISION_RANK[hit[2]]
        if best is not None and rank >= best[0]:
            continue
        if not re.search(r"(^|[^a-z])" + re.escape(name.lower()) + r"($|[^a-z])", text):
            continue
        if anchors and not any(_degrees_apart(hit, a) <= 45 for a in anchors):
            continue          # contradicts every region named; not this style's Boston
        best = (rank, hit, name)
        if rank == 0:
            break
    return best


def survey():
    gaz = load_gazetteer()
    unplaced, coarse, unread, by_record = [], [], [], []
    counts = {"locality": 0, "region": 0, "country": 0}

    for s in _styles():
        g = s.get("geography") or {}
        hearth = g.get("hearth")
        by_region = _place_by_regions(gaz, g.get("regions"))
        by_hearth = _place_by_hearth(gaz, hearth, _anchors(gaz, g.get("regions")))
        best = by_hearth if (by_hearth and (by_region is None or by_hearth[0] < by_region[0])) \
            else by_region

        if best is None:
            unplaced.append(s["id"])
            continue
        counts[best[1][2]] += 1

        if best[1][2] == "country":
            # An abstraction, or a record that says it has no hearth, is correctly coarse.
            if s.get("rank") in ("family", "tradition") or (hearth and NO_HEARTH.search(hearth)):
                by_record.append(s["id"])
            else:
                coarse.append(s["id"])

        # A hearth sentence the gazetteer can find NO place name in at all. Not "a hearth
        # that did not yield a town" — "The Peloponnese and Attica" is read correctly and
        # the answer is a region, because that is what the sentence names. The work list is
        # only the sentences this file cannot read a single word of.
        if hearth and by_hearth is None and not NO_HEARTH.search(hearth):
            unread.append((s["id"], hearth[:90]))

    return {"gazetteer_entries": len(gaz), "counts": counts, "unplaced": unplaced,
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
