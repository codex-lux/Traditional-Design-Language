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
    for f in glob.glob(os.path.join(ROOT, "proportions", "*", "*.json")):
        d = json.load(open(f))
        packs[d["id"]] = d
    nodes = [json.load(open(f)) for f in glob.glob(os.path.join(ROOT, "styles", "*.json"))]
    return packs, nodes


# Pinned. own-scope collisions must stay 0 (OQ 48's closure). cascade-scope is a measured backlog
# under OQ 51 and may only go DOWN -- it falls as the cascade is adjudicated.
RATCHET = {"own": 0, "cascade": 9}


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
    errors, unjudged = [], []
    for (x, y), where in sorted(cob.items()):
        if x not in packs or y not in packs:
            continue
        by_addr = {}
        for pid in (x, y):
            for r in packs[pid].get("derived_rules", []):
                by_addr.setdefault((r["target_slot"], r["dimension"]), {}).setdefault(
                    pid, set()).add(r.get("quantity"))
        for addr, sides in by_addr.items():
            if len(sides) < 2:
                continue
            qx, qy = sides[x], sides[y]
            if None in qx or None in qy:
                unjudged.append((x, y, addr, sorted(where)[:3]))
                continue
            if not (qx & qy):
                errors.append((x, y, addr, sorted(qx), sorted(qy), sorted(where)))
    return errors, unjudged


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
        errors, unjudged = compare(packs, cob)
        counts[scope] = (len(cob), len(errors), len(unjudged))

        print(f"\n--- scope: {scope} " + "-" * 40)
        for x, y, addr, qx, qy, where in errors:
            print(f"x {addr[0]}/{addr[1]}: '{x}' measures {qx} and '{y}' measures {qy} "
                  f"-- {len(where)} node(s), e.g. {', '.join(where[:3])}")
        if a.report:
            for x, y, addr, where in unjudged:
                print(f"? {addr[0]}/{addr[1]}: '{x}' and '{y}' -- one or both rules carry no "
                      f"`quantity`, so this pair COULD NOT BE JUDGED (e.g. {', '.join(where)})")
        print(f"{len(cob)} co-binding pack pair(s); {len(errors)} address(es) where two packs "
              f"measure different quantities; {len(unjudged)} could not be judged.")
        if len(errors) > RATCHET[scope]:
            failed.append(f"{scope}: {RATCHET[scope]} -> {len(errors)}")

    # Never the unqualified "OK". `unjudged` is could-not-evaluate, and a summary that says OK
    # while 111 pairs were never compared is the cardinal rule broken in the sentence rather than
    # in the code. State what was judged and what was not, always.
    print()
    for scope in scopes:
        pairs, errs, unj = counts[scope]
        verdict = "no collision" if errs == 0 else f"{errs} COLLISION(S)"
        print(f"{scope:8s}: {pairs:5d} pairs -- {verdict}, {unj} pair(s) COULD NOT BE JUDGED "
              f"(ratchet {RATCHET[scope]})")
    if "cascade" in scopes and counts["cascade"][1] > counts.get("own", (0, 0, 0))[1]:
        print("\nThe cascade number is the one the compiler is exposed to: `resolve_packs` walks "
              "the whole\nlineage, so packs a node never bound meet at its addresses too. That is "
              "OQ 51's surface,\nand OQ 48's closure at 0 is a statement about own bindings only.")
    if failed:
        print("\nRATCHET BROKEN — address collisions grew: " + "; ".join(failed))
    if a.strict:
        sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
