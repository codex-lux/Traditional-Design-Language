#!/usr/bin/env python3
"""Authoring aid: what rule addresses does this pack share with its neighbours?

A derived rule is addressed by `(target_slot, dimension)`. Several rules may sit
at one address and usually that is right -- see OQ 48, and the measurement below.
There are three cases and only one is a defect:

  (i)   several rules at one address WITHIN one pack: a MENU. `room-harmonic`
        offers seven harmonic room shapes at `room_adjacency_overrides/width`
        and three ways to derive a vaulted height, each labelled "SHAPE 1 OF 7",
        "METHOD 1 OF 3". Correct and deliberate.
  (ii)  two packs at one address meaning the SAME quantity: alternatives, and
        precedence is exactly the mechanism for choosing. `facade-arcade` and
        `moorish-arch` both give an arch's rise; `opening-pointed` and
        `trim-sawn` both give a bargeboard's depth. Correct.
  (iii) two packs at one address meaning DIFFERENT quantities: a corruption.
        Whichever resolves last wins and nothing reports it, and precedence
        cannot help, because precedence decides which of two accounts of the
        SAME quantity to believe. `porch_support/height` meant both an impost
        block's height and a springing line 84 inches higher; `frieze/height`
        meant a classical entablature frieze and a suspended spindle valance.

WHY THIS IS AN AUTHORING AID AND NOT A BUILD CHECK. Only a human can tell (ii)
from (iii), because the difference is what the rule MEANS. Measured over the
whole corpus there are 597 cross-pack pairs, of which 144 involve a pack written
in WP-4.6; adjudicating those 144 by hand found EIGHT of case (iii), about five
per cent. So the mechanism is mostly working, and a checker carrying a 144-entry
allowlist that had to be re-adjudicated on every new pack would be a great deal
of ceremony for a five per cent hit rate. Run this when you write or bind a
pack, read the list, and rename the dimension where two packs mean two things --
the convention WP-4.6 settled on is a named dimension (`springing`, `upper_ratio`,
`end_ratio`, `facade_ratio`, `parapet_height`, `curve_count`, `step_rise`,
`stock_thickness`, `verge_overhang`, `valance_depth`, `member_count`).

    python3 build/pack_addresses.py trim-sawn
    python3 build/pack_addresses.py --all          # every pack, summary only
"""
import argparse
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load():
    packs = {}
    for f in glob.glob(os.path.join(ROOT, "proportions", "*", "*.json")):
        d = json.load(open(f))
        packs[d["id"]] = d
    nodes = []
    for f in glob.glob(os.path.join(ROOT, "styles", "*.json")):
        d = json.load(open(f))
        if d.get("rank") in ("style", "variant"):
            nodes.append(d)
    return packs, nodes


def addresses(pack):
    return {(r["target_slot"], r.get("dimension")) for r in pack.get("derived_rules", [])}


def rule_at(pack, addr):
    return [r for r in pack.get("derived_rules", [])
            if (r["target_slot"], r.get("dimension")) == addr]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack", nargs="?", help="pack id to report on")
    ap.add_argument("--all", action="store_true", help="summarise every pack")
    args = ap.parse_args()

    packs, nodes = load()

    if args.all or not args.pack:
        pairs = collections.defaultdict(set)
        intra = collections.Counter()
        for pid, p in packs.items():
            c = collections.Counter((r["target_slot"], r.get("dimension"))
                                    for r in p.get("derived_rules", []))
            intra[pid] = sum(v - 1 for v in c.values() if v > 1)
        for n in nodes:
            addr = collections.defaultdict(set)
            for e in n.get("proportion_packs") or []:
                for a in addresses(packs.get(e["pack"], {})):
                    addr[a].add(e["pack"])
            for a, ps in addr.items():
                ps = sorted(ps)
                for i in range(len(ps)):
                    for j in range(i + 1, len(ps)):
                        pairs[(ps[i], ps[j]) + a].add(n["id"])
        print(f"{len(packs)} packs, {len(nodes)} buildable nodes")
        print(f"cross-pack shared addresses (pack, pack, slot, dimension): {len(pairs)}")
        print(f"packs with a MENU (several rules at one of their own addresses): "
              f"{sum(1 for v in intra.values() if v)}")
        for pid, v in intra.most_common(6):
            if v:
                print(f"    {pid}: {v} extra rule(s) at addresses it already writes")
        print("\nA menu is correct. Run this with a pack id to adjudicate that pack's "
              "cross-pack shares.")
        return 0

    if args.pack not in packs:
        print(f"unknown pack '{args.pack}'")
        return 1

    me = packs[args.pack]
    mine = addresses(me)
    shared = collections.defaultdict(set)
    for n in nodes:
        ids = [e["pack"] for e in n.get("proportion_packs") or []]
        if args.pack not in ids:
            continue
        for other in ids:
            if other == args.pack:
                continue
            for a in mine & addresses(packs.get(other, {})):
                shared[(other,) + a].add(n["id"])

    if not shared:
        print(f"{args.pack}: shares no rule address with any pack it co-binds with.")
        return 0

    print(f"{args.pack} shares {len(shared)} address(es) with packs it co-binds with.")
    print("For each, decide: SAME quantity (leave it, precedence resolves) or "
          "DIFFERENT (rename the dimension).\n")
    for key in sorted(shared, key=lambda k: (-len(shared[k]), k)):
        other, slot, dim = key
        n = len(shared[key])
        print(f"  {slot}/{dim}  with {other}  on {n} node(s): "
              f"{', '.join(sorted(shared[key])[:4])}{' ...' if n > 4 else ''}")
        for r in rule_at(me, (slot, dim)):
            print(f"      mine : {r.get('note', '')[:96]}")
        for r in rule_at(packs[other], (slot, dim)):
            print(f"      other: {r.get('note', '')[:96]}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
