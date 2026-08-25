#!/usr/bin/env python3
"""Validate proportion_packs bindings on every buildable style/variant node
(WP-4.1, PLAN-OF-ACTION.md).

"Buildable" means rank in {"style", "variant"} -- 132 nodes total. Family and
tradition nodes are organisational and are not bound directly; only their
members are.

Checks:

  * every buildable node has a non-empty `proportion_packs` list
  * every `pack` id resolves to a real file under proportions/{orders,
    overlays,systems,modules}/
  * no node binds more than one pack with role in {"primary"} whose pack
    record is an order-system pack of kind order-system AND simultaneously
    binds both a classical trim family (trim-classical) and a craftsman one
    (trim-craftsman) as primary -- the two trim families are mutually
    exclusive per PLAN-OF-ACTION.md's own task description ("no node binds
    both trim-classical and trim-craftsman as primary")
  * `precedence` values on one node's proportion_packs are a total order --
    unique integers, no ties, no gaps required (gaps are fine; a duplicate
    or missing precedence is not)
  * every entry has `pack`, `role`, `note`; `authority` is optional (only
    order-system packs and material modules with more than one attested
    written/documented authority tend to carry one)

    python3 build/check_pack_bindings.py                # whole corpus
    python3 build/check_pack_bindings.py tidewater-georgian
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_ENTRY_FIELDS = {"pack", "role", "note"}
VALID_ROLES = {
    "primary", "secondary", "facade", "opening", "interior", "massing",
    "room", "optional", "trim",
}

# WP-4.1 (23 Aug 2026, wave 2 merge) bound 129 of the 132 buildable nodes. The
# remaining 3 were deliberately left unbound rather than forced onto a pack
# that doesn't fit, per PLAN-OF-ACTION.md's own instruction for this work
# package ("where a needed pack does not exist... list it -- do not bind the
# wrong pack"). Each is a real, checked gap, not an oversight -- see
# docs/reports/wp-4.1-proportion-pack-bindings.md for the full reasoning per
# node and the consolidated candidate-pack list this fed to WP-4.6:
#   - egyptian-revival: trabeated/battered-wall/no-arch Egyptian order; none
#     of the 5 Vignola-derived orders are even structurally the same family.
#   - moorish-andalusian, mudejar: horseshoe-arch/muqarnas/geometric Islamic
#     setting-out; no classical order or room/facade system in the library
#     models it, and room-vernacular's own applies_to list excludes both by
#     the pack author's own hand.
# --strict still fails the build on any OTHER unbound node (a real
# regression), but tolerates exactly these three as a known, documented,
# permanent-until-WP-4.6 exception rather than papering over the difference
# between "not done yet" and "correctly refused."
# WP-4.6, 24 Aug 2026: `moorish-andalusian` and `mudejar` come OFF this list. They were on it
# because no pack in the library encoded a horseshoe arch, an impost block or an alfiz, and
# WP-4.1 was right to leave them unbound rather than force a Vignola order onto a node whose own
# text says "no order and no absolute module". `proportions/orders/moorish-arch.json` is that
# pack, so the reason has gone and the allowlist entry with it. Retiring an allowlist entry when
# the thing it excused is fixed is the point of having one; leaving it would let the next real
# gap hide behind it.
#
# `egyptian-revival` stays, and its reason is untouched: trabeated, archaeological, copied from
# Denon's plates, explicitly not module-derived, and almost never a house -- so neither the order
# packs nor the domestic room packs reach it.
DELIBERATELY_UNBOUND = {"egyptian-revival"}


def _all_pack_ids():
    ids = {}
    for f in glob.glob(os.path.join(ROOT, "proportions", "*", "*.json")):
        d = json.load(open(f))
        ids[d["id"]] = d
    return ids


def _load_nodes():
    nodes = {}
    for f in glob.glob(os.path.join(ROOT, "styles", "*.json")):
        d = json.load(open(f))
        nodes[d["id"]] = d
    return nodes


def check_node(node, packs, errors, warnings, strict):
    nid = node["id"]
    entries = node.get("proportion_packs")
    if not entries:
        if strict and nid not in DELIBERATELY_UNBOUND:
            errors.append(f"{nid}: no proportion_packs binding at all")
        else:
            warnings.append(f"{nid}: no proportion_packs binding at all"
                             + ("  (deliberate -- see docs/reports/wp-4.1-proportion-pack-bindings.md)"
                                if nid in DELIBERATELY_UNBOUND else ""))
        return

    seen_precedence = {}
    trim_primary = set()
    for i, e in enumerate(entries):
        missing = REQUIRED_ENTRY_FIELDS - e.keys()
        if missing:
            errors.append(f"{nid}: entry {i} missing field(s) {sorted(missing)}")
            continue
        pack_id = e["pack"]
        if pack_id not in packs:
            errors.append(f"{nid}: entry {i} binds unknown pack '{pack_id}'")
            continue
        role = e["role"]
        if role not in VALID_ROLES:
            warnings.append(f"{nid}: entry {i} ('{pack_id}') has unrecognised role '{role}'")
        prec = e.get("precedence")
        if prec is None:
            errors.append(f"{nid}: entry {i} ('{pack_id}') has no precedence")
        else:
            if prec in seen_precedence:
                errors.append(
                    f"{nid}: precedence {prec} used by both '{seen_precedence[prec]}' and '{pack_id}' -- not a total order"
                )
            seen_precedence[prec] = pack_id
        if role == "primary" and pack_id in ("trim-classical", "trim-craftsman"):
            trim_primary.add(pack_id)
        if role == "trim" and pack_id in ("trim-classical", "trim-craftsman"):
            trim_primary.add(pack_id)

    if {"trim-classical", "trim-craftsman"} <= trim_primary:
        errors.append(f"{nid}: binds both trim-classical and trim-craftsman as primary/trim")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("node", nargs="?", help="Check a single style/variant node id instead of the whole corpus")
    ap.add_argument("--strict", action="store_true",
                     help="Treat a completely unbound buildable node as an error (fails the build), except the 3"
                          " nodes in DELIBERATELY_UNBOUND which stay warnings even under --strict. Wired into"
                          " check_all.py as of the WP-4.1 merge (23 Aug 2026).")
    args = ap.parse_args()

    packs = _all_pack_ids()
    nodes = _load_nodes()
    buildable = [n for n in nodes.values() if n.get("rank") in ("style", "variant")]

    if args.node:
        buildable = [n for n in buildable if n["id"] == args.node]
        if not buildable:
            print(f"'{args.node}' is not a buildable (style/variant) node id.")
            sys.exit(1)

    errors, warnings = [], []
    bound = 0
    role_counts = {}
    pack_use_counts = {}
    for node in buildable:
        if node.get("proportion_packs"):
            bound += 1
            for e in node["proportion_packs"]:
                role_counts[e.get("role")] = role_counts.get(e.get("role"), 0) + 1
                pack_use_counts[e.get("pack")] = pack_use_counts.get(e.get("pack"), 0) + 1
        check_node(node, packs, errors, warnings, args.strict)

    print(f"{bound} of {len(buildable)} buildable (style/variant) node(s) bound"
          + (f" (checking only '{args.node}')" if args.node else ""))
    if not args.node:
        print(f"  by role: {dict(sorted(role_counts.items(), key=lambda kv: -kv[1]))}")
        never_used = set(packs) - set(pack_use_counts)
        if never_used:
            print(f"  packs never bound by any node ({len(never_used)}): {sorted(never_used)}")

    if warnings:
        print(f"\n{len(warnings)} WARNING(S)")
        for w in warnings:
            print(f"  ! {w}")

    if errors:
        print(f"\n{len(errors)} ERROR(S)")
        for e in errors:
            print(f"  x {e}")
        print("\nFAILED")
        sys.exit(1)

    missing = len(buildable) - bound
    if missing and not args.node:
        undocumented = missing - len(DELIBERATELY_UNBOUND & {n["id"] for n in buildable})
        if undocumented:
            print(f"\n{undocumented} buildable node(s) have no binding and are NOT in DELIBERATELY_UNBOUND --"
                  " this is new, not the WP-4.1 baseline, and should be investigated.")
        else:
            print(f"\n{missing} buildable node(s) have no binding, all {len(DELIBERATELY_UNBOUND)} accounted for by"
                  " DELIBERATELY_UNBOUND (see docs/reports/wp-4.1-proportion-pack-bindings.md).")

    print("\nOK — every bound node's proportion_packs conforms")


if __name__ == "__main__":
    main()
