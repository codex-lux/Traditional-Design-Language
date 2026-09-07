#!/usr/bin/env python3
"""Hold a grouping's `internal_rules` against the room record it constrains, and against the
rules of a grouping some parti carries alongside it.

    python3 build/check_grouping_rules.py            # measure and report
    python3 build/check_grouping_rules.py --report   # also list what could not be compared
    python3 build/check_grouping_rules.py --strict   # exit nonzero when a ratchet is broken

WHY THIS EXISTS. `build/check_addresses.py` polices pack-versus-pack and kit-versus-pack at one
address and does not see groupings, room bands or fault tests at all. So a grouping rule and the
room record it constrains could state different numbers for one quantity and nothing noticed --
`piazza-and-single-house-core` demands `piazza_depth_ft at-least 10` HARD while `rooms/piazza.json`
bands its width 8 to 14 and cites "the measured Charleston piazzas run 8 to 12 ft", so a 9 ft
piazza is inside the band, inside the cited measurement, and fails a hard rule. Six instances were
found by hand, and the count went from four to six WHILE THE REGISTER ENTRY WAS BEING AUDITED,
which is the argument for counting them instead of looking for them.
`oq/a-grouping-rule-and-a-room-record-can-disagree`, ruled 2 Sep 2026 as shape (1).

THIS CHECKER DECIDES NO NUMBER, AND THAT IS THE RULING RATHER THAN A LIMITATION. Three of the six
have a source on one side only and it is not consistently the same side: the piazza's evidence is
on the ROOM RECORD and the grouping rule demanding 10 ft has none. Its job is to make each
disagreement visible and unjudged and hand it to an architect. Do not reconcile an instance by
picking the stricter or the looser number to turn this check green.

WHAT IT COMPARES

  (A) rule vs room band -- for a rule whose `measures` names a room and a band, ONLY the bound the
      rule actually states. A rule saying `at-least 10` makes no claim about a ceiling, so
      comparing whole intervals would report every one-sided rule as "looser" and bury the real
      findings under 20 of its own noise.
  (B) rule vs co-carried rule -- for every pair of groupings some parti carries together, rules
      sharing a `measures.quantity`. This is `check_addresses.cobinding()` one layer out, and it
      is what catches one measure spelled twice: `georgian-service-core` tests
      `wing_ridge_ft / main_ridge_ft at-most 0.85` where `dependency-and-hyphen` tests
      `dependency_ridge_ft / main_ridge_ft between 0.6 and 0.8`, and `five-part-palladian` carries
      both.
  (C) the prose meter -- see below. It is the reason (A) agreeing is not read as nothing-to-see.

UNJUDGED IS NOT PASSED, and here that rule has teeth it did not have elsewhere, because THE MOST
DANGEROUS OUTPUT OF THIS CHECKER IS THE WORD "AGREES". Measured before it was written, of the six
known instances a band comparison catches three; one it MISSES because the grouping's figure lives
in prose; and one -- the sleeping porch -- it reports as AGREEING. `sleeping-porch-cluster` tests
`porch_depth_ft at-least 8` and `rooms/sleeping-porch.json` bands [8, 12], so the two executable
numbers coincide exactly, while the record's own `critical_dimension` says "NINE FEET OF DEPTH IF
THE BED RUNS ACROSS, seven if it runs along" -- a conditional floor with no axis to be conditional
on, which is `oq/register-is-not-style`'s first customer. A green tick there would be this corpus's
own founding failure: every part well-formed and the whole saying nothing.

So (C) exists. For every band this checker compares, it scans the room's `critical_dimension` for
a figure in the same units that is NEITHER the band's floor NOR its ceiling, and for every rule it
scans the `statement` for a figure the `test` does not carry, and reports both as UNCOMPARED with
the sentence quoted. IT IS A CRUDE REGEX AND THIS DOCSTRING SAYS SO: it is an upper bound, several
of its hits are the benign case of a test stating a floor while the prose states a band, and it
needs eyes. An instrument that overcounts and says so is worth more here than a silence.

RATCHETS. Four ceilings that may only fall, and one FLOOR that may only rise. The floor is not
decoration: `check_addresses` learned that a may-only-fall ratchet lies when the instrument
measures LESS, and it fails on any node that would not resolve for exactly that reason. Here the
equivalent failure is deleting a `measures` annotation -- disagreements fall, and the corpus looks
better for having stopped looking. `compared` going down fails the build.
"""
import argparse, collections, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Measured 2 Sep 2026 on the first run, and thereafter may only improve. Read the entries before
# moving one: several of these numbers are supposed to be non-zero, and driving them to zero by
# the wrong route is the failure this checker is about.
#
#   rule_vs_band 3      The register's instances 1, 2 and 3, and they are the DELIVERABLE. The
#                       passage 8 against a band floor of 6, the piazza 10 against 8, the bedroom
#                       10 against 11. Ruled 2 Sep: no number is reconciled to make this fall.
#   rule_vs_rule 2      The ridge pair, on two grouping pairs rather than one -- `five-part-
#                       palladian` carries `georgian-service-core` alongside BOTH
#                       `dependency-and-hyphen` and `garage-and-hyphen`. The register said one.
#   unit_splits  0      Nothing yet says one quantity in two units across a co-carried pair.
#                       Zero here is a real zero: 26 of 26 tested rules carry `units`.
#   uncomparable 21     Rules whose quantity names no room band -- ridge ratios, work triangles,
#                       a landing depth. Mostly correct and permanent: a building-level quantity
#                       has no band to be held against. NOT a backlog to drive to zero, and
#                       binding one to a band it does not mean would be the OQ 48 error.
#                       **22 -> 21 at WP-11.7, and the fall is not progress**: it is
#                       `centre-passage-core`'s facade-share rule losing its `test` when the
#                       facade ruling made it a REPORT rather than a requirement, so there is one
#                       fewer test to be uncomparable. A ceiling that falls because a rule stopped
#                       being executable is exactly the way a may-only-fall ratchet lies, which is
#                       why the `compared` FLOOR below is the guard that matters here -- it held
#                       at 5 across the change, measured.
#                       **21 -> 23 at WP-11.9, and this rise IS legitimate**: two of the twenty
#                       prose rules the Tidewater diagnosis lists were given a test in that
#                       package -- `passage_ends_with_a_door` and `stair_hall_opens_off_the_
#                       passage` -- and both measure a COUNT, which no room band states or could.
#                       They land in the "correct and permanent" bucket this entry already
#                       describes. A same-commit ceiling change is how a blinded instrument gets
#                       ratified (WP-9.4), so the guard is the FLOOR: `compared` held at 5 across
#                       this change, measured, and the two new rules are named here so a later
#                       reader can check the claim rather than take it.
#   prose_uncompared 35 Figures stated in prose that no test or band carries. Falls when a figure
#                       is AUTHORED into a test (the passage's was, in this package) -- never by
#                       tightening the regex until the number looks better.
#   compared 5          A FLOOR. Deleting a `measures` annotation makes every ceiling above look
#                       better, which is the one way a may-only-fall ratchet lies. `check_
#                       addresses` guards the same hole by failing on a node that would not
#                       resolve; this is the same guard wearing this checker's clothes.
RATCHET = {
    "rule_vs_band": 3,
    "rule_vs_rule": 2,
    "unit_splits": 0,
    "uncomparable": 23,
    "prose_uncompared": 35,
    "compared": 5,          # a FLOOR -- may only RISE
}


def _mod(name, path):
    # build/modcache.py, never a local loader (OQ 28; tests/test_modcache.py counts loads)
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


def _parse(test):
    """`arrangement.parse_rule_test` and NOTHING ELSE.

    That function's own comment reads "ONE PARSER, and it lives here", and `roof.py` already
    delegates to it rather than keeping the private `between`-only spelling it used to have. A
    second spelling of one rule is what this corpus has been bitten by three times.
    """
    ARR = _mod("arrangement", os.path.join(ROOT, "build", "arrangement.py"))
    return ARR.parse_rule_test(test)


def load():
    groupings, rooms, partis = {}, {}, []
    for f in sorted(glob.glob(os.path.join(ROOT, "groupings", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        groupings[d["id"]] = d
    for f in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        rooms[d["id"]] = d
    for f in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))):
        partis.append(json.load(open(f, encoding="utf-8")))
    return groupings, rooms, partis


def tested_rules(groupings):
    """Every internal rule carrying a test, with its grouping id and index."""
    out = []
    for gid in sorted(groupings):
        for i, ru in enumerate(groupings[gid].get("internal_rules") or []):
            if ru.get("test"):
                out.append((gid, i, ru))
    return out


def stated_bounds(parsed):
    """The bounds a rule ACTUALLY claims, as (floor, ceiling), either possibly None.

    `at-least X` claims a floor and says nothing about a ceiling. Treating the silence as a
    claim is what would make every one-sided rule read as looser than its band.
    """
    d, t = parsed["direction"], parsed["threshold"]
    if d == "at-least":
        return (t, None)
    if d == "at-most":
        return (None, t)
    if d == "between":
        return (t, parsed.get("upper"))
    if d == "equals":
        return (t, t)
    return (None, None)


# ------------------------------------------------------------------ (A) rule vs room band
def rule_vs_band(groupings, rooms):
    """Compare each annotated rule's stated bound against the room band it names.

    Four outcomes per rule, and the fourth is the one that must never be silent:
      agrees          -- the bound the rule states equals the band's corresponding end
      rule-stricter   -- the rule forbids part of the band; a value the RECORD calls correct
                         fails the rule (the piazza: 10 against a floor of 8)
      rule-looser     -- the rule admits outside the band; a value PASSING the rule fails the
                         record's own band (the bedroom: 10 against a floor of 11)
      uncomparable    -- no `measures`, no room, no band, band absent, units disagree, or the
                         test is not in a form the one parser knows
    """
    hits, uncomparable, compared = [], [], 0
    for gid, i, ru in tested_rules(groupings):
        m = ru.get("measures") or {}
        where = f"{gid}[{i}]"
        if not m:
            uncomparable.append((where, ru["test"], "the rule carries no `measures`"))
            continue
        if not (m.get("room") and m.get("band")):
            uncomparable.append((where, ru["test"],
                                 f"`{m.get('quantity')}` names no room band -- a building-level "
                                 f"quantity is compared rule-to-rule only"))
            continue
        rm = rooms.get(m["room"])
        if rm is None:
            uncomparable.append((where, ru["test"], f"no room record `{m['room']}`"))
            continue
        band = (rm.get("dimensions") or {}).get(m["band"])
        if band is None:
            uncomparable.append((where, ru["test"],
                                 f"`{m['room']}` states no `{m['band']}`"))
            continue
        # A room band's units are fixed by its own key. Compare only where the rule says it in
        # the same units -- never convert. `check_addresses` compared a quantity without its
        # units and reported 60 DEGREES against 1.7321, which is tan 60: the same slope, called
        # a contradiction (OQ 53). ft<->in here is arithmetically safe and is STILL refused, so
        # that the count of cross-unit pairs is visible rather than silently absorbed.
        band_units = {"width_ft": "ft", "length_ft": "ft", "area_sf": "sf",
                      "proportion": "ratio", "ceiling_min_ft": "ft"}[m["band"]]
        if m.get("units") != band_units:
            uncomparable.append((where, ru["test"],
                                 f"the rule says it in {m.get('units')} and `{m['room']}`'s "
                                 f"{m['band']} is in {band_units} -- UNIT SPLIT, not converted"))
            continue
        parsed = _parse(ru["test"])
        if not parsed:
            uncomparable.append((where, ru["test"], "the test is not in a form the parser knows"))
            continue
        # `ceiling_min_ft` is a scalar floor, not a two-element band.
        lo, hi = (band, None) if not isinstance(band, list) else (band[0], band[1])
        r_lo, r_hi = stated_bounds(parsed)
        judged = False
        for end, rule_v, band_v in (("floor", r_lo, lo), ("ceiling", r_hi, hi)):
            if rule_v is None or band_v is None:
                continue
            judged = True
            if abs(rule_v - band_v) < 1e-9:
                continue
            stricter = (rule_v > band_v) if end == "floor" else (rule_v < band_v)
            hits.append((where, ru["severity"], ru["test"], m["room"], m["band"], end,
                         rule_v, band_v, "rule-stricter" if stricter else "rule-looser"))
        if judged:
            compared += 1
        else:
            uncomparable.append((where, ru["test"],
                                 f"the rule states no bound `{m['room']}`.{m['band']} also states"))
    return hits, uncomparable, compared


# ------------------------------------------------------------ (B) rule vs co-carried rule
def co_carried(groupings, partis):
    """(grouping_x, grouping_y) -> the partis carrying both. `cobinding()` one layer out."""
    pairs = collections.defaultdict(set)
    for p in partis:
        gs = sorted({g for g in (p.get("groupings") or []) if g in groupings})
        for a in range(len(gs)):
            for b in range(a + 1, len(gs)):
                pairs[(gs[a], gs[b])].add(p["id"])
    return pairs


def rule_vs_rule(groupings, partis):
    """Two groupings a parti carries together, stating different bounds for one quantity."""
    hits, unit_splits, uncomparable = [], [], []
    by_q = collections.defaultdict(list)
    for gid, i, ru in tested_rules(groupings):
        m = ru.get("measures") or {}
        if m.get("quantity"):
            by_q[(gid, m["quantity"])].append((i, ru, m))
    pairs = co_carried(groupings, partis)
    seen = set()
    for (gx, gy), where in sorted(pairs.items()):
        qx = {q for g, q in by_q if g == gx}
        qy = {q for g, q in by_q if g == gy}
        for q in sorted(qx & qy):
            for ix, rux, mx in by_q[(gx, q)]:
                for iy, ruy, my in by_q[(gy, q)]:
                    key = (gx, ix, gy, iy)
                    if key in seen:
                        continue
                    seen.add(key)
                    if mx.get("units") != my.get("units"):
                        unit_splits.append((gx, ix, gy, iy, q, mx.get("units"), my.get("units"),
                                            sorted(where)))
                        continue
                    px, py = _parse(rux["test"]), _parse(ruy["test"])
                    if not px or not py:
                        uncomparable.append((f"{gx}[{ix}] vs {gy}[{iy}]", q,
                                             "one test is not in a form the parser knows"))
                        continue
                    # Only the ends BOTH rules state, for the reason `rule_vs_band` gives:
                    # `at-most 0.85` makes no claim about a floor, and comparing the tuples
                    # whole would report every floor-silent rule as disagreeing with every
                    # rule that states one.
                    bx, by = stated_bounds(px), stated_bounds(py)
                    ends = [(e, u, v) for e, u, v in (("floor", bx[0], by[0]),
                                                      ("ceiling", bx[1], by[1]))
                            if u is not None and v is not None]
                    if not ends:
                        uncomparable.append((f"{gx}[{ix}] vs {gy}[{iy}]", q,
                                             "the two rules state no bound in common"))
                        continue
                    for e, u, v in ends:
                        if abs(u - v) > 1e-9:
                            hits.append((gx, ix, rux["test"], gy, iy, ruy["test"], q,
                                         sorted(where), e, u, v))
    return hits, unit_splits, uncomparable


# ----------------------------------------------------------------- (C) the prose meter
#
# WORDS COUNT, AND THE FIRST VERSION OF THIS METER PROVED IT BY FAILING. It scanned for digits
# with any unit, returned 50 figures of which about 45 were inch-steps inside an arithmetic
# derivation ("a queen mattress is 60 by 80 ... you need 24 in clear"), and MISSED the one case
# the meter exists for: `rooms/sleeping-porch.json` says "NINE FEET OF DEPTH IF THE BED RUNS
# ACROSS, seven if it runs along" -- in words. A meter that buries its signal in its own noise
# and then does not contain the signal is worse than no meter, because its output is a number
# rather than a green tick.
#
# So: figures in the band's OWN units only, digits and number-words both, and the sentence the
# figure sits in rather than the first hundred characters of the record.
_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
          "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
          "fourteen": 14, "fifteen": 15, "sixteen": 16, "eighteen": 18, "twenty": 20}
_UNIT = {"ft": r"(?:ft|feet|foot)", "in": r"(?:in|inches)", "sf": r"(?:sf)"}


def figures_in(text, units):
    """Every figure stated in `units`, as digits or as a number-word. (value, sentence)."""
    if units not in _UNIT:
        return []
    u = _UNIT[units]
    out = []
    for sent in re.split(r"(?<=[.;])\s+", text):
        for m in re.finditer(rf"\b(\d+(?:\.\d+)?)\s*{u}\b", sent, re.I):
            out.append((float(m.group(1)), sent.strip()))
        if units == "ft":
            words = "|".join(_WORDS)
            for m in re.finditer(rf"\b({words})\s+(?:feet|foot|ft)\b", sent, re.I):
                out.append((float(_WORDS[m.group(1).lower()]), sent.strip()))
    return out


def prose_meter(groupings, rooms):
    """Figures stated in prose that no executable number carries. UNJUDGED, never a finding.

    Two populations:
      * a room whose `critical_dimension` names a figure, in the band's own units, that is
        neither end of a band this checker compared -- the sleeping porch's NINE FEET against a
        band floor of 8, and `rooms/keeping-room.json`'s "THE RADIANT REACH OF THE FIRE, AND IT
        IS 10 FT" against a grouping that reasons to 12 in prose and tests 14, which is THREE
        numbers for one measure where the register found two;
      * a rule whose `statement` names a figure its own `test` does not carry -- the passage's
        8 to 14 ft beside a test measuring a ratio, until WP-9.7 authored it.

    Still an upper bound, and still needs eyes: prose legitimately states a band ceiling beside
    a test stating only a floor. Ratchet it down by AUTHORING the figure into a test, which is
    what the passage rule did -- never by tightening the regex until the number looks better.
    """
    out = []
    bands_used = collections.defaultdict(set)
    for gid, i, ru in tested_rules(groupings):
        m = ru.get("measures") or {}
        if m.get("room") and m.get("band"):
            bands_used[m["room"]].add((m["band"], m.get("units")))
    for rid in sorted(bands_used):
        rm = rooms.get(rid)
        if not rm:
            continue
        dims = rm.get("dimensions") or {}
        prose = dims.get("critical_dimension") or ""
        for band, units in sorted(bands_used[rid]):
            v = dims.get(band)
            ends = set(v) if isinstance(v, list) else {v}
            for fig, sent in figures_in(prose, units):
                if not any(e is not None and abs(fig - e) < 1e-9 for e in ends):
                    row = ("room", f"{rid}.{band}", fig, sent)
                    if row not in out:      # one sentence may state "9 ft" three times
                        out.append(row)
    for gid, i, ru in tested_rules(groupings):
        units = (ru.get("measures") or {}).get("units")
        in_test = {float(x) for x in re.findall(r"\b\d+(?:\.\d+)?\b", ru["test"])}
        for fig, sent in figures_in(ru["statement"], units):
            if not any(abs(fig - t) < 1e-9 for t in in_test):
                row = ("rule", f"{gid}[{i}]", fig, sent)
                if row not in out:
                    out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true",
                    help="also list every pair that could not be compared, and the prose meter")
    ap.add_argument("--strict", action="store_true", help="exit nonzero when a ratchet breaks")
    a = ap.parse_args()
    groupings, rooms, partis = load()
    failed = []

    band_hits, band_unc, compared = rule_vs_band(groupings, rooms)
    print("--- rule vs room band " + "-" * 38)
    for where, sev, test, room, band, end, rv, bv, direction in band_hits:
        print(f"x {where} ({sev}) '{test}' sets a {end} of {rv:g}; rooms/{room}.json's {band} "
              f"{end} is {bv:g} -- {direction}")
    if a.report:
        for where, test, why in band_unc:
            print(f"? {where} '{test}': {why} -- COULD NOT BE COMPARED")
    print(f"{compared} rule(s) compared against a room band; {len(band_hits)} disagreement(s); "
          f"{len(band_unc)} COULD NOT BE COMPARED (ratchet {RATCHET['rule_vs_band']}, "
          f"floor on compared {RATCHET['compared']}).")

    rr_hits, rr_units, rr_unc = rule_vs_rule(groupings, partis)
    print("\n--- rule vs co-carried rule " + "-" * 32)
    for gx, ix, tx, gy, iy, ty, q, where, end, u, v in rr_hits:
        print(f"x {q} ({end}): {gx}[{ix}] '{tx}' says {u:g} where {gy}[{iy}] '{ty}' says {v:g} "
              f"-- carried together by {', '.join(where)}")
    for gx, ix, gy, iy, q, ux, uy, where in rr_units:
        print(f"u {q}: {gx}[{ix}] says it in {ux} and {gy}[{iy}] in {uy} "
              f"-- carried together by {', '.join(where)}")
    print(f"{len(rr_hits)} co-carried disagreement(s); {len(rr_units)} unit split(s); "
          f"{len(rr_unc)} could not be compared (ratchet {RATCHET['rule_vs_rule']}).")

    prose = prose_meter(groupings, rooms)
    print("\n--- prose figures nothing compares " + "-" * 25)
    if a.report:
        for kind, who, fig, text in prose:
            print(f"? {kind} {who}: {fig:g} appears in prose and in no executable number "
                  f'-- "{text}..."')
    print(f"{len(prose)} figure(s) stated in prose that no test or band carries "
          f"(ratchet {RATCHET['prose_uncompared']}). CRUDE REGEX, an upper bound: several are the "
          f"benign case of a test stating a floor while its prose states a band. --report lists "
          f"them.")

    # Never the unqualified OK. State what was judged and what was not, in the same breath.
    print(f"\ncompared {compared} rule(s) against a band and {len(rr_hits) + len(rr_unc)} "
          f"co-carried pair(s); {len(band_hits)} band disagreement(s), {len(rr_hits)} co-carried "
          f"disagreement(s); {len(band_unc)} rule(s) and {len(prose)} prose figure(s) COULD NOT "
          f"BE COMPARED -- which is not agreement.")

    for key, got in (("rule_vs_band", len(band_hits)), ("rule_vs_rule", len(rr_hits)),
                     ("unit_splits", len(rr_units)), ("uncomparable", len(band_unc)),
                     ("prose_uncompared", len(prose))):
        if got > RATCHET[key]:
            failed.append(f"{key}: {RATCHET[key]} -> {got}")
    # THE FLOOR. Deleting a `measures` annotation makes every ceiling above look better, which is
    # the one way a may-only-fall ratchet lies -- `check_addresses` guards the same hole by
    # failing on a node that would not resolve.
    if compared < RATCHET["compared"]:
        failed.append(f"compared FELL: {RATCHET['compared']} -> {compared}; the checker is "
                      f"measuring less, which is not the same as the corpus agreeing more")

    if failed:
        print("\nRATCHET BROKEN — " + "; ".join(failed))
    if a.strict:
        sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
