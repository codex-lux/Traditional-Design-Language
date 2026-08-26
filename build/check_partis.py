#!/usr/bin/env python3
"""check_partis.py - validate the parti catalogue.

Partis were the one catalogue nothing checked. `schema/parti.schema.json` has existed
since the layer was built and was referenced by no code in the repository: `validate.py`
covers the style graph, `check_rooms.py` covers rooms and groupings, and a malformed
parti surfaced only as a KeyError somewhere inside `compose.py` at the moment a brief
happened to reach it. That was tolerable while there were twelve files written by one
hand in one sitting. WP-4.5 roughly doubles the catalogue, so the checker comes first.

Checks, in order:
  1. every partis/*.json against schema/parti.schema.json
  2. id matches filename, ids unique
  3. rooms[].type resolves against rooms/*.json
  4. groupings[] resolves against groupings/*.json
  5. massing and alternate_massings resolve against massings/catalog.json
  6. styles[] resolves against styles/*.json, and every entry is a BUILDABLE node
     (a parti native to a family or a tradition is a category error - you cannot
     compose for a rank that has no kit)
  7. the door graph closes: every doors[] target is a room id in the same parti or
     the literal "exterior", and every door is reciprocated or reciprocable
  8. level sanity, and that a parti declaring storeys > 1 actually places rooms above
  9. circulation_parti agrees with the groupings it names (a grouping carries an
     ARRAY of acceptable values; a parti carries one scalar - they must intersect)
 10. COMPOSABILITY (OQ 59): every parti is instantiated against the first style in its
     own `styles` array and run through plan_check. A FATAL finding is an error here.
     Everything above this line checks that a parti is well FORMED; this checks that the
     diagram works - that it satisfies the room catalogue's own hard adjacency rules,
     which is what plan_check will hold any plan built from it to.
 11. `area_range_sf` is a size this parti's own room list can be built at (OQ 45), with the
     ceiling computed the way compose.instantiate actually builds -- repeating rooms counted
     once per bedroom at the top of the parti's own bedroom_range
 12. coverage: which buildable nodes with a canonical massing no parti names

Check 12 is the one WP-4.5 exists to move, so it is reported as a count and a list
rather than an error - a partial catalogue is a state of the project, not a defect.

Check 10 was added after five of twenty-one partis were found carrying fatal findings
against their OWN native style, so the composer would not recommend them for the styles
they were written for: a Charleston-single-house brief came back with a centre-passage
single pile, because a fatal is 100 points and nativity is worth at most 140. That was
the composer working exactly as designed on data that was wrong, and nothing looked at
the data. It runs in about four seconds for the whole catalogue.

    python3 build/check_partis.py            # everything
    python3 build/check_partis.py --no-compose   # skip check 10 (no compose.py import)
    python3 build/check_partis.py --strict   # warnings become errors
    python3 build/check_partis.py --coverage # print the uncovered-node work list
"""

import json
import os
import sys
import glob
import argparse
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def err(self, where, msg):
        self.errors.append((where, msg))

    def warn(self, where, msg):
        self.warnings.append((where, msg))


def build_universe():
    u = {}
    u["massings"] = {m["id"] for m in load(os.path.join(ROOT, "massings", "catalog.json"))}
    u["rooms"] = {os.path.basename(p)[:-5]
                  for p in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json")))}
    # the full records too, for check 11 (OQ 45), which needs each room's catalogue band
    u["room_records"] = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))):
        r = load(p); u["room_records"][r["id"]] = r
    u["groupings"] = {os.path.basename(p)[:-5]
                      for p in sorted(glob.glob(os.path.join(ROOT, "groupings", "*.json")))}
    styles, buildable, canonical = {}, set(), {}
    for p in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = load(p)
        styles[d["id"]] = d
        if d.get("rank") in ("style", "variant"):
            buildable.add(d["id"])
            cm = {a["massing"] for a in (d.get("massing_affinities") or [])
                  if a.get("affinity") == "canonical"}
            if cm:
                canonical[d["id"]] = cm
    u["styles"] = styles
    u["buildable"] = buildable
    u["canonical"] = canonical
    # a grouping's circulation_parti is an ARRAY of acceptable values; a parti's is one
    u["grouping_circulation"] = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "groupings", "*.json"))):
        d = load(p)
        cp = d.get("circulation_parti")
        if cp:
            u["grouping_circulation"][d["id"]] = set(cp if isinstance(cp, list) else [cp])
    return u


def validate_schema(rep, path, doc, validator):
    if validator is None:
        return
    for e in sorted(validator.iter_errors(doc), key=lambda x: list(x.path)):
        loc = "/".join(str(p) for p in e.path) or "<root>"
        rep.err(f"parti:{os.path.basename(path)}", f"schema at {loc}: {e.message}")


def check_parti(rep, path, p, u):
    where = f"parti:{p.get('id', os.path.basename(path))}"
    fname = os.path.basename(path)[:-5]
    if p.get("id") != fname:
        rep.err(where, f"id '{p.get('id')}' does not match filename '{fname}.json'")

    # --- massings
    for key in ("massing",):
        m = p.get(key)
        if m and m not in u["massings"]:
            rep.err(where, f"{key} '{m}' is not in massings/catalog.json")
    for m in (p.get("alternate_massings") or []):
        if m not in u["massings"]:
            rep.err(where, f"alternate_massings '{m}' is not in massings/catalog.json")
    if p.get("massing") in (p.get("alternate_massings") or []):
        rep.warn(where, f"'{p['massing']}' is both the massing and an alternate_massing")

    # --- styles: must exist, and must be a rank you can actually compose for
    for s in (p.get("styles") or []):
        if s not in u["styles"]:
            rep.err(where, f"styles names '{s}', which is not a node in styles/")
        elif s not in u["buildable"]:
            rank = u["styles"][s].get("rank")
            rep.err(where, f"styles names '{s}', which is a {rank} - a parti can only be "
                           f"native to a style or a variant, since only those have kits")

    # --- groupings
    for g in (p.get("groupings") or []):
        if g not in u["groupings"]:
            rep.err(where, f"groupings names '{g}', which is not in groupings/")

    # --- circulation_parti must be one a named grouping accepts
    cp = p.get("circulation_parti")
    if cp:
        for g in (p.get("groupings") or []):
            allowed = u["grouping_circulation"].get(g)
            if allowed and cp not in allowed:
                rep.warn(where, f"circulation_parti '{cp}' is not among the values grouping "
                                f"'{g}' accepts ({', '.join(sorted(allowed))})")

    # --- rooms and the door graph
    rooms = p.get("rooms") or []
    ids = [r.get("id") for r in rooms]
    for dup in [k for k, v in Counter(ids).items() if v > 1]:
        rep.err(where, f"duplicate room id '{dup}' within the parti")
    idset = set(ids)
    levels = set()
    for r in rooms:
        rid = r.get("id")
        t = r.get("type")
        if t and t not in u["rooms"]:
            rep.err(where, f"room '{rid}' has type '{t}', which is not in rooms/")
        lv = r.get("level")
        if lv is not None:
            levels.add(lv)
        for d in (r.get("doors") or []):
            if d == "exterior":
                continue
            if d not in idset:
                rep.err(where, f"room '{rid}' has a door to '{d}', which is not a room in "
                               f"this parti (nor the literal 'exterior')")
        for so in ([r.get("stacks_over")] if isinstance(r.get("stacks_over"), str)
                   else (r.get("stacks_over") or [])):
            if so and so not in idset:
                rep.err(where, f"room '{rid}' stacks_over '{so}', which is not a room here")

    # A parti's door graph is declared once per pair by convention (compose.py's
    # symmetrise_doors mirrors it), so a one-sided door is correct. What is NOT
    # correct is a room no door reaches at all: the composer would place it and the
    # validator would then report it as unreachable, on every plan, forever.
    reachable = set()
    for r in rooms:
        for d in (r.get("doors") or []):
            if d != "exterior":
                reachable.add(d)
        if r.get("doors"):
            reachable.add(r.get("id"))
    for r in rooms:
        if r.get("id") not in reachable and len(rooms) > 1:
            rep.err(where, f"room '{r.get('id')}' has no door to or from anything")

    # --- storeys against the levels actually used
    st = p.get("storeys")
    if st and st > 1 and not any(lv and lv > 0 for lv in levels):
        rep.warn(where, f"declares {st} storeys but places no room above level 0")
    if st == 1 and any(lv and lv > 0 for lv in levels):
        rep.err(where, "declares 1 storey but places rooms above level 0")

    # --- ranges
    ar = p.get("area_range_sf")
    if ar and ar[0] >= ar[1]:
        rep.err(where, f"area_range_sf {ar} is not ascending")
    br = p.get("bedroom_range")
    if br and br[0] > br[1]:
        rep.err(where, f"bedroom_range {br} is not ascending")


def check_area_range_is_reachable(rep, partis, rooms):
    """A parti's `area_range_sf` must be a size its own room list can actually be built at.

    OQ 45, ruled 24 Aug 2026. The field described the TYPE and the composer instantiates a fixed
    room list, so the top of the range was unreachable by the only mechanism the composer has
    for growing a house -- making the same rooms bigger until each hits its catalogue band.
    Measured across the catalogue, seventeen of twenty-one partis reached their own stated
    maximum comfortably and four could not: `courtyard-and-portal` reached 43% of its stated
    9,000 sf, `great-hall-h-plan` 82% of 12,000, and two more at 96 and 97%. A brief at the top
    of such a range came back missing by 40% under a decision log correctly saying the diagram
    grows by having more rooms -- with no way to act on it.

    The ceiling is the sum of every non-outdoor room's catalogue band TOP, with rooms marked
    `repeats_with_bedrooms` counted once per bedroom at the top of the parti's own
    `bedroom_range` -- because that is what `compose.instantiate` actually builds, and a bound
    computed against a room list the composer never instantiates would be measuring the wrong
    house."""
    for p in partis:
        rng = p.get("area_range_sf")
        if not rng: continue
        lo, hi = rng
        beds_max = (p.get("bedroom_range") or [0, 1])[1]
        ceiling = 0.0
        for r in p.get("rooms", []):
            rt = rooms.get(r.get("type"))
            if rt is None or rt.get("function_class") == "outdoor": continue
            band = (rt.get("dimensions", {}) or {}).get("area_sf") or [0, 0]
            # compose.py keeps the stated room AND adds one copy per extra bedroom, so a
            # repeating room appears (beds_max - beds_stated + 1) times at the top of the range.
            n = 1
            if r.get("repeats_with_bedrooms"):
                stated = sum(1 for x in p["rooms"] if x.get("repeats_with_bedrooms")
                             and x.get("type") == r.get("type"))
                n = max(1, beds_max - stated + 1)
            ceiling += band[1] * n
        if ceiling <= 0: continue
        if hi > ceiling * 1.02:
            rep.err("parti:%s" % p.get("id"),
                    "area_range_sf tops at %d sf and this room list reaches %d at every room's "
                    "band top (%d%%). The range must be what the AUTHORED rooms can be built at; "
                    "the type's true size belongs in the description (OQ 45)."
                    % (hi, ceiling, round(100 * ceiling / hi)))
        elif lo < ceiling * 0.05:
            rep.warn("parti:%s" % p.get("id"),
                     "area_range_sf starts at %d sf against a %d sf ceiling -- a range that wide "
                     "says very little" % (lo, ceiling))


def check_composability(rep, partis):
    """Instantiate each parti against its own first native style and run plan_check on it.

    OQ 59. Everything else in this file checks that a parti is well FORMED. This checks that
    the diagram WORKS: that it satisfies the room catalogue's own hard adjacency rules, which
    is what plan_check holds any plan built from it to. Five of twenty-one partis were carrying
    fatal findings against the styles they were written for, and the composer -- correctly, on
    100 points a fatal against at most 140 for nativity -- was refusing to recommend them. A
    Charleston-single-house brief came back with a centre-passage single pile.

    Deliberately run on the plan AS INSTANTIATED, before compose.py's repair pass. Repair
    widens rooms and adds doors to clear findings; a diagram that only works after repair is a
    diagram whose author left the work to the machine, and the five real failures here are
    identical before and after it, so nothing is lost by checking the stricter thing.

    Returns the per-parti fatal counts so the caller can print them; errors go into `rep`."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "build"))
        import compose
    except Exception as e:                       # pragma: no cover - environment, not data
        rep.warn("<setup>", f"compose.py could not be imported - composability check skipped: {e}")
        return None
    def fatal_keys(pid, style):
        """The fatal findings a parti produces against a style, keyed so two runs can be
        subtracted. The key deliberately includes the REQUIREMENT and not the measured value:
        a style-level fault fires the same test for every parti, so it cancels, while a parti
        that fails a DIFFERENT test of the same fault does not."""
        brief = {"id": "check", "name": "check", "style": style,
                 "target_area_sf": 2600, "bedrooms": 3, "bathrooms": 2.0,
                 "context": {"climate_zone": "3A", "lot_width_ft": 120, "entrance_faces": "S",
                             "jurisdiction": "IRC model text, advisory", "budget_tier": "custom"},
                 "household": "check"}
        plan, _log, _parti = compose.instantiate(pid, brief)
        res = compose.PC.check(plan, compose.C)
        out = {}
        for f in res["findings"]:
            if f["severity"] != "fatal": continue
            stmt = f["statement"]
            req = stmt.split(" against ", 1)[1] if " against " in stmt else ""
            out[(f.get("layer"), f.get("rule"), f.get("room"), req)] = stmt
        return out

    # A control diagram, run against the SAME style, so what this check reports is what the
    # PARTI does and not what the style does. Three of cape-central-chimney's four fatals fire
    # identically for every parti composed for cape-cod-colonial -- they are facts about that
    # style's kit and its elevation, and blaming the parti for them would make this check a
    # generator of false accusations against exactly the files it exists to protect. The
    # control is the simplest diagram in the catalogue and is never itself the parti under test
    # except in the one case where it is, which is skipped.
    CONTROL = "hall-and-parlor"

    counts = {}
    for p in partis:
        pid = p.get("id")
        styles = p.get("styles") or []
        if not styles:
            rep.warn(f"parti:{pid}", "names no styles, so there is nothing to compose it against")
            continue
        style = styles[0]
        try:
            mine = fatal_keys(pid, style)
            base = {} if pid == CONTROL else fatal_keys(CONTROL, style)
        except Exception as e:
            rep.err(f"parti:{pid}", f"cannot be composed for its own style '{style}': {e}")
            continue
        own = {k: v for k, v in mine.items() if k not in base}
        counts[pid] = len(own)
        for k in sorted(own, key=lambda k: own[k]):
            rep.err(f"parti:{pid}", f"FATAL against its own style '{style}': {own[k]}")
        shared = len(mine) - len(own)
        if shared:
            rep.warn(f"parti:{pid}",
                     f"{shared} further fatal finding(s) against '{style}' are the STYLE's, not "
                     f"this diagram's -- the control parti produces them too")
    return counts


def coverage(partis, u):
    """Which buildable nodes with a canonical massing does no parti name?

    This is WP-4.5's own work list, and the number the README's `parti_native_styles`
    figure reports. It is not an error: a partial catalogue is a state of the project."""
    named = set()
    for p in partis:
        named.update(p.get("styles") or [])
    uncovered = {}
    for sid, cm in u["canonical"].items():
        if sid not in named:
            uncovered[sid] = cm
    return named, uncovered


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="warnings are errors")
    ap.add_argument("--coverage", action="store_true", help="print the uncovered-node work list")
    ap.add_argument("--no-compose", action="store_true",
                    help="skip the composability check (check 10), which imports compose.py")
    args = ap.parse_args()

    rep = Report()
    u = build_universe()

    try:
        from jsonschema import Draft202012Validator
        v = Draft202012Validator(load(os.path.join(ROOT, "schema", "parti.schema.json")))
    except ImportError:
        rep.warn("<setup>", "jsonschema not installed - schema validation skipped")
        v = None

    partis = []
    for path in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))):
        try:
            doc = load(path)
        except Exception as e:
            rep.err(f"parti:{os.path.basename(path)}", f"unparseable JSON: {e}")
            continue
        validate_schema(rep, path, doc, v)
        partis.append(doc)
        check_parti(rep, path, doc, u)

    for dup in [k for k, n in Counter(p.get("id") for p in partis).items() if n > 1]:
        rep.err("<catalogue>", f"duplicate parti id '{dup}'")

    check_area_range_is_reachable(rep, partis, u["room_records"])
    fatals = None if args.no_compose else check_composability(rep, partis)

    named, uncovered = coverage(partis, u)

    print(f"partis: {len(partis)}   native styles: {len(named)} of {len(u['buildable'])} buildable")
    print(f"buildable nodes with a canonical massing: {len(u['canonical'])}")
    print(f"  ...of which no parti names: {len(uncovered)}")
    if fatals is not None:
        broken = {k: v for k, v in fatals.items() if v}
        print(f"composable against their own first native style: "
              f"{len(fatals) - len(broken)} of {len(fatals)}")
        for pid in sorted(broken, key=lambda k: -broken[k]):
            print(f"  {broken[pid]:>3} fatal  {pid}")

    by_massing = defaultdict(list)
    for sid, cm in uncovered.items():
        for m in cm:
            by_massing[m].append(sid)
    if by_massing:
        print("\nuncovered nodes by canonical massing (the WP-4.5 work list)")
        for m in sorted(by_massing, key=lambda k: -len(by_massing[k])):
            print(f"  {len(by_massing[m]):>3}  {m}")
            if args.coverage:
                for sid in sorted(by_massing[m]):
                    print(f"          {sid}")

    if rep.warnings:
        print(f"\nWARNINGS ({len(rep.warnings)})")
        for w, m in rep.warnings:
            print(f"  {w}: {m}")
    if rep.errors:
        print(f"\nERRORS ({len(rep.errors)})")
        for w, m in rep.errors:
            print(f"  {w}: {m}")

    bad = len(rep.errors) + (len(rep.warnings) if args.strict else 0)
    print(f"\n{'FAIL' if bad else 'OK'}  errors={len(rep.errors)} warnings={len(rep.warnings)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
