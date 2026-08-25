#!/usr/bin/env python3
"""Find two proportion packs that write DIFFERENT quantities to one (slot, dimension) address
on a node that binds them both — OQ 48's case (iii), the silent corruption.

    python3 build/check_addresses.py            # errors on a real collision
    python3 build/check_addresses.py --report   # also list what could not be judged

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
    a = ap.parse_args()
    packs, nodes = load()

    # which packs co-bind, and where
    cob = collections.defaultdict(set)
    for n in nodes:
        ids = sorted({e["pack"] for e in (n.get("proportion_packs") or [])})
        for x, y in itertools.combinations(ids, 2):
            cob[(x, y)].add(n["id"])

    errors, unjudged = [], []
    for (x, y), where in sorted(cob.items()):
        if x not in packs or y not in packs:
            continue
        by_addr = {}
        for pid in (x, y):
            for r in packs[pid].get("derived_rules", []):
                by_addr.setdefault((r["target_slot"], r["dimension"]), {}).setdefault(pid, set()).add(
                    r.get("quantity"))
        for addr, sides in by_addr.items():
            if len(sides) < 2:
                continue
            qx, qy = sides[x], sides[y]
            if None in qx or None in qy:
                unjudged.append((x, y, addr, sorted(where)[:3]))
                continue
            if not (qx & qy):
                errors.append((x, y, addr, sorted(qx), sorted(qy), sorted(where)))

    for x, y, addr, qx, qy, where in errors:
        print(f"x {addr[0]}/{addr[1]}: '{x}' measures {qx} and '{y}' measures {qy} "
              f"-- {len(where)} node(s) bind both, e.g. {', '.join(where[:3])}")
    if a.report:
        for x, y, addr, where in unjudged:
            print(f"? {addr[0]}/{addr[1]}: '{x}' and '{y}' -- one or both rules carry no `quantity`, "
                  f"so this pair COULD NOT BE JUDGED (e.g. {', '.join(where)})")

    print(f"\n{len(cob)} co-binding pack pair(s); {len(errors)} address(es) where two packs measure "
          f"different quantities; {len(unjudged)} could not be judged.")
    if errors:
        print("  These are OQ 48 case (iii): precedence picks a winner and the other quantity is set")
        print("  aside. `build/resolve_kit.py` now NAMES what it set aside instead of discarding it.")
        print("  The count is pinned by a test; fixing them is a migration and is not done here.")
        if a.strict:
            sys.exit(1)
        return
    print("OK -- no co-binding pair writes two different quantities to one address")


if __name__ == "__main__":
    main()
