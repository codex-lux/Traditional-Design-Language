#!/usr/bin/env python3
"""Find two proportion packs that write DIFFERENT quantities to one (slot, dimension) address
on a node that binds them both — OQ 48's case (iii), the silent corruption.

    python3 build/check_addresses.py            # both scopes; errors on a real collision
    python3 build/check_addresses.py --report   # also list what could not be judged
    python3 build/check_addresses.py --scope own|cascade|both

TWO SCOPES, AND THE NARROW ONE ALONE WAS PUBLISHED AS CLOSURE. This checker originally built its
co-binding set from each node's OWN `proportion_packs` array. But `resolve_kit.resolve_packs`
walks the whole `_cascade`, so the packs that actually meet on a node are far more than the ones
it bound -- that is OQ 51, and measuring addresses at the narrow scope while the resolver works at
the wide one made "OQ 48 closed at 0 collisions" a statement about a corpus nobody resolves.
Found by audit on 25 Aug 2026. Both scopes are now measured and reported:

    own bindings      442 pairs    0 collisions     14 could-not-judge   <- OQ 48's closure, true
    cascade-resolved 1264 pairs    9 collisions    111 could-not-judge   <- the real exposure

The 9 are a newly measured backlog, not a regression: they are ratcheted so they cannot grow, and
the own-scope 0 stays a hard failure on the first new one.

WHY THIS COULD NOT BE A UNIQUENESS CHECK. A `(slot, dimension)` address legitimately holds
several rules in two of its three cases, and only the third is wrong:

  (i)   several rules at one address WITHIN one pack — a MENU, authored deliberately, and the
        notes say so ("SHAPE 1 OF 7 — THE ROUND ROOM", "METHOD 1 OF 3 — THE ARITHMETIC MEAN").
        `room-harmonic` writes room_adjacency_overrides/width ten times and every one is right.
  (ii)  two packs offering alternative accounts of the SAME quantity — precedence is exactly
        the mechanism for choosing, and twenty-four packs giving a chair rail's height above
        the floor is the system working.
  (iii) two packs meaning DIFFERENT quantities at one address — a corruption, because whichever
        resolves last wins, nothing reports it, and precedence cannot help: precedence decides
        which of two accounts of ONE quantity to believe, and here there are two quantities.

A naive uniqueness check flags 1,710 correct rules to catch the wrong ones. So the rule's
`quantity` field (OQ 48) names what it MEASURES, making (slot, dimension, quantity) the real
address, and this checker compares meanings instead of guessing.

UNJUDGED IS NOT PASSED. A rule with no `quantity` cannot be compared, and the pair is reported
as could-not-evaluate rather than as agreement. `--report` prints those; the exit code ignores
them, because failing the build on unannotated legacy rules would just get the field rubber-
stamped, which is the failure this whole entry is about.
"""
import argparse, collections, glob, itertools, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load():
    packs = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
        d = json.load(open(f))
        packs[d["id"]] = d
    nodes = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json")))]
    return packs, nodes


# Pinned. own-scope collisions must stay 0 (OQ 48's closure). cascade-scope is a measured backlog
# under OQ 51 and may only go DOWN -- it falls as the cascade is adjudicated.
#
# kit_vs_pack is a THIRD measured backlog, first counted 27 Aug 2026 (WP-5.10, OQ 86) and
# CORRECTED 28 Aug by that package's own adversarial audit. The first count was 133 and was
# units-blind: 71 of its pairs compared a figure in inches against a pack rule stating a ratio,
# and one compared 60-72 DEGREES against 1.7321 -- tan 60, the same slope, reported as a
# contradiction. That is OQ 53's class, reproduced in a new function ninety lines below the
# docstring recording it. Comparing only same-unit pairs gives 62 real contradictions and moves
# the rest to could-not-evaluate, where a units mismatch belongs.
#
# The instance that found it is NOT in the count, because it was fixed in the same commit:
# `tidewater-georgian` authored its brick sill's projection at 0-1 in as MEASURED while
# `sash-light` delivered 2.25 in "sloped about 1 in 6 with a drip" to the same address, in a node
# whose kit FORBIDS the sloped sill and says why.
RATCHET = {"own": 0, "cascade": 9, "kit_vs_pack": 62}


def cobinding(nodes, scope):
    """(pack_x, pack_y) -> nodes where both are in play. `own` reads each node's own bindings;
    `cascade` reads what resolve_packs actually assembles, which is what the compiler sees."""
    cob = collections.defaultdict(set)
    if scope == "own":
        for n in nodes:
            ids = sorted({e["pack"] for e in (n.get("proportion_packs") or [])})
            for x, y in itertools.combinations(ids, 2):
                cob[(x, y)].add(n["id"])
        return cob
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import resolve_kit as rk
    g = rk.load_graph()
    for nid, n in g["nodes"].items():
        if n.get("rank") not in ("style", "variant"):
            continue
        ids = sorted(rk.resolve_packs(g, rk.chain_for(g, nid)).keys())
        for x, y in itertools.combinations(ids, 2):
            cob[(x, y)].add(nid)
    return cob


def compare(packs, cob):
    """Two packs writing DIFFERENT quantities to one address is the corruption (OQ 48). Two
    packs writing the same quantity in different UNITS is a second, quieter state (OQ 53):
    they agree about what they measure and disagree about what they are saying it in, so
    precedence -- which exists to choose between rival accounts of one quantity -- was
    choosing between a measurement and a bare ratio and could deliver either. It is reported
    separately rather than folded into the collisions, because it is not the same fault and
    the fix is not the same fix: a collision wants a named dimension, this wants the ratio's
    referent moved out of its prose note and into its expression."""
    errors, unjudged, unit_splits = [], [], []
    for (x, y), where in sorted(cob.items()):
        if x not in packs or y not in packs:
            continue
        by_addr = {}
        for pid in (x, y):
            for r in packs[pid].get("derived_rules", []):
                by_addr.setdefault((r["target_slot"], r["dimension"]), {}).setdefault(
                    pid, set()).add((r.get("quantity"), r.get("units")))
        for addr, sides in by_addr.items():
            if len(sides) < 2:
                continue
            qx = {q for q, _ in sides[x]}
            qy = {q for q, _ in sides[y]}
            if None in qx or None in qy:
                unjudged.append((x, y, addr, sorted(where)[:3]))
                continue
            if not (qx & qy):
                errors.append((x, y, addr, sorted(qx), sorted(qy), sorted(where)))
                continue
            # Same quantity on both sides. Do they agree on the units they say it in?
            for q in sorted(qx & qy):
                ux = {u for qq, u in sides[x] if qq == q}
                uy = {u for qq, u in sides[y] if qq == q}
                if ux != uy and not (ux & uy):
                    unit_splits.append((x, y, addr, q, sorted(map(str, ux)),
                                        sorted(map(str, uy)), sorted(where)))
    return errors, unjudged, unit_splits


# ---------------------------------------------------------------- kit parameter vs pack rule
def kit_vs_pack(nodes):
    """A node's OWN authored parameter and a pack rule, at one address, disagreeing.

    OQ 48 measured pack against pack. This is the same corruption one layer over, and it was
    invisible to that measurement for the same reason it was invisible to everyone else: the kit
    writes a parameter called `projection_in` and a pack writes dimension `projection`, so the two
    never met under one name. `tidewater-georgian` authored its brick sill's projection as 0-1 in,
    `kind: measured`, while `sash-light` delivered 2.25 in "sloped about 1 in 6 with a drip" to the
    same slot -- a figure more than twice the node's own, in a node whose kit FORBIDS the sloped
    sill and gives its reason. Nothing compared them, and the resolved slot carried both.

    THE MAPPING is `<dimension>` or `<dimension>_in`, which is the convention the corpus already
    uses everywhere. Only a parameter the node authored as `measured` is compared: a `derived` one
    is a pack's own value copied into the kit and agreeing with itself, and reporting those would
    bury the real cases under hundreds of tautologies.

    WHAT IS COMPARED is the VALUE, not the quantity -- a kit parameter has no `quantity` field, so
    the pack-versus-pack test cannot be reused. A range and a figure are compared by whether the
    figure falls in the range; two figures by a 10 per cent tolerance, which is loose on purpose:
    the corruption worth reporting is a member drawn twice the size, not rounding.

    AND ONLY WHERE THE TWO SIDES SAY IT IN THE SAME UNITS, which the first version of this
    function did not check -- reproducing OQ 53 (the open question recording that this very file
    compares `quantity` without `units`) ninety lines below the docstring that documents it. It
    put 71 cross-unit pairs into a corruption count of 133: 70 comparing a kit figure in INCHES
    against a pack rule stating a RATIO, and one comparing `dutch-colonial-american`'s
    `gambrel_lower_slope` of 60-72 DEGREES against `dutch-gambrel`'s 1.7321 -- which is tan 60,
    the same slope, reported as a contradiction. A mismatch of units at one address is a real
    finding and a DIFFERENT one; it goes to `unjudged`, which is what could-not-evaluate is
    called here, rather than being counted as a corruption."""
    import resolve_kit as _rk  # noqa: E402
    hits, unjudged = [], []
    CTX = {"ceiling_height": 108.0, "storey_height": 120.0, "opening_height": 80.0,
           "opening_width": 36.0, "span": 16.0}
    g = _rk.load_graph()
    for nid in sorted(n["id"] for n in nodes):
        kit = _rk.load_kit(nid)
        if not kit:
            continue
        try:
            chain = _rk.chain_for(g, nid)
            packs = _rk.resolve_packs(g, chain)
            # OQ 88: pass the node's own scope facts, or every scoped rule reads as UNJUDGED
            # here and this reporter goes on counting contradictions from rules that are not
            # about this construction at all -- which is the same "measuring a corpus nobody
            # resolves" error the cascade scope was added to fix.
            _slots, _ = _rk.resolve_slots(g, chain, _rk.scope_for(g, nid))
            pack_slots, _ = _rk.eval_packs(packs, {**CTX, **_rk.scope_facts(_slots)}, None)
        except Exception:
            continue
        for sid, rec in kit.items():
            for pname, pval in (rec.get("parameters") or {}).items():
                if not isinstance(pval, dict) or pval.get("kind") != "measured":
                    continue
                dim = pname[:-3] if pname.endswith("_in") else pname
                rows = [r for r in (pack_slots.get(sid) or []) if r.get("dimension") == dim]
                if not rows:
                    continue
                lo, hi = None, None
                if isinstance(pval.get("range"), list) and len(pval["range"]) == 2:
                    lo, hi = pval["range"]
                elif isinstance(pval.get("value"), (int, float)):
                    lo = hi = pval["value"]
                if lo is None:
                    unjudged.append((nid, sid, dim, pname))
                    continue
                for r in rows:
                    v = r.get("value")
                    if not isinstance(v, (int, float)):
                        unjudged.append((nid, sid, dim, r["pack"]))
                        continue
                    if pval.get("unit") != r.get("units"):
                        # Same address, different units: not a corruption of the FIGURE, and
                        # comparing the numbers would invent one. OQ 53's class, reported as
                        # could-not-evaluate rather than as a contradiction.
                        unjudged.append((nid, sid, dim,
                                         f"{r['pack']} says it in {r.get('units')}, "
                                         f"the node in {pval.get('unit')}"))
                        continue
                    tol = 0.10 * max(abs(hi), abs(lo), abs(v), 1e-9)
                    if v < lo - tol or v > hi + tol:
                        hits.append((nid, sid, dim, pname, (lo, hi), r["pack"], v))
    return hits, unjudged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="also list pairs that could not be judged")
    ap.add_argument("--strict", action="store_true",
                    help="exit nonzero on a real collision. OFF by default, deliberately: the 139 "
                         "found when this checker shipped are recorded in OQ 48 and fixing them is "
                         "a migration, not a patch. Failing the build on a known, counted, "
                         "documented backlog would stop all work until that migration lands, and "
                         "the thing that actually protects the corpus is the pinned COUNT in "
                         "tests/test_wp46_packs.py, which fails the moment a new pack adds a 140th.")
    ap.add_argument("--scope", choices=("own", "cascade", "both"), default="both",
                    help="`own` reads each node's own bindings; `cascade` reads what "
                         "resolve_packs actually assembles. Default both.")
    a = ap.parse_args()
    packs, nodes = load()

    scopes = ("own", "cascade") if a.scope == "both" else (a.scope,)
    counts, failed = {}, []
    for scope in scopes:
        cob = cobinding(nodes, scope)
        errors, unjudged, unit_splits = compare(packs, cob)
        counts[scope] = (len(cob), len(errors), len(unjudged), len(unit_splits))

        print(f"\n--- scope: {scope} " + "-" * 40)
        for x, y, addr, qx, qy, where in errors:
            print(f"x {addr[0]}/{addr[1]}: '{x}' measures {qx} and '{y}' measures {qy} "
                  f"-- {len(where)} node(s), e.g. {', '.join(where[:3])}")
        for x, y, addr, q, ux, uy, where in unit_splits:
            print(f"u {addr[0]}/{addr[1]}/{q}: '{x}' says it in {'/'.join(ux)} and '{y}' in "
                  f"{'/'.join(uy)} -- {len(where)} node(s), e.g. {', '.join(where[:3])}")
        if a.report:
            for x, y, addr, where in unjudged:
                print(f"? {addr[0]}/{addr[1]}: '{x}' and '{y}' -- one or both rules carry no "
                      f"`quantity`, so this pair COULD NOT BE JUDGED (e.g. {', '.join(where)})")
        print(f"{len(cob)} co-binding pack pair(s); {len(errors)} address(es) where two packs "
              f"measure different quantities; {len(unit_splits)} where they agree on the quantity "
              f"and differ on its units; {len(unjudged)} could not be judged.")
        if len(errors) > RATCHET[scope]:
            failed.append(f"{scope}: {RATCHET[scope]} -> {len(errors)}")

    # Never the unqualified "OK". `unjudged` is could-not-evaluate, and a summary that says OK
    # while 111 pairs were never compared is the cardinal rule broken in the sentence rather than
    # in the code. State what was judged and what was not, always.
    print()
    for scope in scopes:
        pairs, errs, unj, usp = counts[scope]
        verdict = "no collision" if errs == 0 else f"{errs} COLLISION(S)"
        print(f"{scope:8s}: {pairs:5d} pairs -- {verdict}, {usp} unit split(s), {unj} pair(s) "
              f"COULD NOT BE JUDGED (ratchet {RATCHET[scope]})")
    if "cascade" in scopes and counts["cascade"][1] > counts.get("own", (0, 0, 0))[1]:
        print("\nThe cascade number is the one the compiler is exposed to: `resolve_packs` walks "
              "the whole\nlineage, so packs a node never bound meet at its addresses too. That is "
              "OQ 51's surface,\nand OQ 48's closure at 0 is a statement about own bindings only.")
    # OQ 48 AT THE KIT LAYER. The pack-versus-pack measurement above cannot see a node's own
    # authored parameter contradicting a pack rule at the same address, because the two are
    # written under different names -- which is exactly how a brick sill authored at 0-1 in sat
    # beside a pack's 2.25 in "sloped 1 in 6" in a node that forbids the sloped sill.
    kp_hits, kp_unjudged = kit_vs_pack(nodes)
    print(f"\n--- scope: kit-vs-pack " + "-" * 33)
    for nid, sid, dim, pname, band, pack, v in kp_hits:
        print(f"k {nid} {sid}/{dim}: the node authors {pname} = {band[0]}-{band[1]} as MEASURED "
              f"and '{pack}' delivers {v} to the same address")
    print(f"{len(kp_hits)} node parameter(s) contradicted by a pack rule; {len(kp_unjudged)} "
          f"could not be judged (ratchet {RATCHET['kit_vs_pack']}).")
    if len(kp_hits) > RATCHET["kit_vs_pack"]:
        failed.append(f"kit_vs_pack: {RATCHET['kit_vs_pack']} -> {len(kp_hits)}")

    if failed:
        print("\nRATCHET BROKEN — address collisions grew: " + "; ".join(failed))
    if a.strict:
        sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
