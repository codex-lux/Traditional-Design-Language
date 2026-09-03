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
  * precedence does not CONTRADICT role: nothing that is not itself primary may
    sit ahead of a primary binding. Added WP-4.6, after that package introduced
    the fault twelve times by inserting each new binding at the first unused
    precedence, which is nearly always 0
  * every entry has `pack`, `role`, `note`; `authority` is optional (only
    order-system packs and material modules with more than one attested
    written/documented authority tend to carry one)

    python3 build/check_pack_bindings.py                # whole corpus
    python3 build/check_pack_bindings.py tidewater-georgian
"""
import argparse
import glob
import json
import re
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_ENTRY_FIELDS = {"pack", "role", "note"}
# WP-4.6 (25 Aug 2026) found this set and schema/style-node.schema.json's own role
# enum disagreeing: "trim" was legal here and illegal there. A new pack bound with
# role "trim" passed --strict and then failed validate.py, and the failure did not
# look like a role problem at all -- see the note on the cascade below. The schema
# is the authority and nothing in the corpus used "trim", so it comes out of here.
# The two lists are now identical and a test pins that they stay so.
VALID_ROLES = {
    "primary", "secondary", "facade", "opening", "interior", "massing",
    "room", "optional",
}
# The cascade is worth recording because the diagnostic was badly misleading. A node
# that fails schema validation is DROPPED from validate.py's node set, so every
# lineage and distinguished_from reference pointing AT it then reports "target does
# not exist". Nine nodes with an illegal role produced forty-seven errors, thirty-eight
# of which named entirely innocent nodes and none of which mentioned a role. If you
# are ever reading a pile of "target does not exist" errors for nodes that plainly
# exist, look at the top of the list for a SCHEMA error first.

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
# EMPTIED 25 Aug 2026 by OQ 49. `egyptian-revival` was the last member and the only one that had
# survived WP-4.6: it is now bound to `facade-peristyle` SCOPED to the two rules that fit, with the
# thirteen that do not -- including an entasis its own c04 forbids -- excluded by the `slots` field
# rather than by a note nobody reads. The set is kept rather than deleted because the mechanism it
# names is still the right answer for a node that genuinely fits nothing, and because emptying it is
# the measurement: 132 of 132 buildable nodes now carry a binding.
DELIBERATELY_UNBOUND = set()


def _pe():
    """proportion_engine, through modcache -- never a local by-path loader (see CLAUDE.md)."""
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    return modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))


def _all_pack_ids():
    ids = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
        d = json.load(open(f))
        ids[d["id"]] = d
    return ids


def _load_nodes():
    nodes = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = json.load(open(f))
        nodes[d["id"]] = d
    return nodes



def _graph():
    """dist/taxonomy.json, for `_cascade`. `_load_nodes()` reads styles/*.json directly and has
    no cascade at all, which is exactly why the decline checks live here and not in validate.py:
    the one thing a decline must be held to is that the pack REALLY REACHES the node by descent,
    and only the built graph knows that. build.py runs first in check_all.py for this reason."""
    return json.load(open(os.path.join(ROOT, "dist", "taxonomy.json")))


def check_declines(node, packs, graph, errors):
    """`declined_packs`, OQ 51's refusal half (WP-8.2).

    The failure this guards is specific and it is the reason the field is checked at all: a
    decline that refuses nothing reads EXACTLY like an adjudicated refusal. It appears in the
    record, it counts as judged in the meter, and it does nothing -- which is worse than never
    having been written, because the gap now looks settled. Same shape, and deliberately the
    same words, as the `slots_except`-that-refuses-nothing check above it.
    """
    nid = node["id"]
    declines = node.get("declined_packs") or []
    if not declines:
        return
    own = {e["pack"] for e in (node.get("proportion_packs") or [])}
    gnode = (graph.get("nodes") or {}).get(nid) or {}
    chain = list(gnode.get("_cascade") or [])
    reachable = {e["pack"]
                 for a in chain
                 for e in ((graph["nodes"].get(a) or {}).get("proportion_packs") or [])}
    seen = set()
    raw = None
    for i, d in enumerate(declines):
        pid = d.get("pack")
        if pid not in packs:
            errors.append(f"{nid}: declined_packs[{i}] names '{pid}', which is not a pack id")
            continue
        if pid in seen:
            errors.append(f"{nid}: declines '{pid}' twice -- one judgment per (node, pack)")
        seen.add(pid)
        if pid in own:
            errors.append(
                f"{nid}: declines '{pid}' and BINDS it as well. That is a binding to delete, not "
                f"a decline to write -- resolve_packs takes the node's own binding at chain[0] "
                f"and the decline would refuse nothing.")
        elif pid not in reachable:
            errors.append(
                f"{nid}: declines '{pid}', which does not reach it by descent. The decline "
                f"refuses nothing while reading as an adjudicated refusal, and the meter counts "
                f"it as judged.")
        if d.get("basis") == "node-record":
            q = (d.get("quote") or "").strip()
            if not q or not d.get("quoted_from"):
                errors.append(
                    f"{nid}: declines '{pid}' on basis `node-record` with no quote or no "
                    f"`quoted_from`. An unquoted node-record basis is an editorial call wearing "
                    f"a citation; say `editorial` and mean it.")
            else:
                if raw is None:
                    raw = open(os.path.join(ROOT, "styles", f"{nid}.json"), encoding="utf-8").read()
                    raw = re.sub(r"\s+", " ", raw)
                if re.sub(r"\s+", " ", q) not in raw:
                    errors.append(
                        f"{nid}: declines '{pid}' quoting {q[:60]!r}, which does not appear in "
                        f"this node's own record. A citation that cannot be checked is a guess "
                        f"wearing a citation (check_openings.py's discipline).")


def check_opt_ins(node, packs, graph, errors):
    """`inherits_packs`, OQ 51's DELIVERY half (re-ruled 3 Sep 2026).

    The exact mirror of `check_declines` above, and it exists for the same reason in the same
    words: an opt-in that admits nothing reads EXACTLY like a considered one. It appears in the
    record and it does nothing -- worse than never having been written, because the delivery now
    looks decided.

    Three lies, two of them straight mirrors of the decline's and the third with no counterpart:
    a pack that does not reach the node by descent (nothing to admit), a pack the node already
    binds (`resolve_packs` takes the node's own binding at chain[0], so the opt-in is inert), and
    opting into a pack this node also DECLINES -- which the refusal half cannot have, because
    there was only ever one field to contradict.

    It does NOT require the pack to have flipped. An opt-in written before its pack declares
    `delivery: opt-in` is inert but correct, and that is the whole staging discipline: the nodes
    that should keep a pack say so first, the pack flips second, and the stranding meter reads
    the difference."""
    nid = node["id"]
    opt = node.get("inherits_packs") or []
    if not opt:
        return
    own = {e["pack"] for e in (node.get("proportion_packs") or [])}
    declined = {d.get("pack") for d in (node.get("declined_packs") or [])}
    gnode = (graph.get("nodes") or {}).get(nid) or {}
    chain = list(gnode.get("_cascade") or [])
    reachable = {e["pack"]
                 for a in chain
                 for e in ((graph["nodes"].get(a) or {}).get("proportion_packs") or [])}
    seen = set()
    for i, pid in enumerate(opt):
        if pid not in packs:
            errors.append(f"{nid}: inherits_packs[{i}] names '{pid}', which is not a pack id")
            continue
        if pid in seen:
            errors.append(f"{nid}: opts into '{pid}' twice -- one statement per (node, pack)")
        seen.add(pid)
        if pid in declined:
            errors.append(
                f"{nid}: opts into '{pid}' and DECLINES it. One of the two is a judgment somebody "
                f"changed and did not delete; the record cannot hold both.")
        if pid in own:
            errors.append(
                f"{nid}: opts into '{pid}' and BINDS it as well. `resolve_packs` takes the node's "
                f"own binding at chain[0] and never gates it, so the opt-in admits nothing.")
        elif pid not in reachable:
            errors.append(
                f"{nid}: opts into '{pid}', which does not reach it by descent. The opt-in admits "
                f"nothing while reading as a considered delivery.")


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

        # OQ 49: a SCOPED binding names the target slots (or slot/dimension pairs) it may
        # contribute. The failure worth catching is not a malformed scope but a scope that names
        # something the pack does not write: it is then a silent no-op, the node gets nothing, and
        # the binding still reads as though it delivered a rule. That is precisely the shape of
        # failure this field was added to prevent, so it must not be reintroduced by the field.
        scope = e.get("slots")
        deny = e.get("slots_except")
        if scope is not None and deny is not None:
            errors.append(
                f"{nid}: entry {i} ('{pack_id}') states both `slots` and `slots_except`. One is an "
                f"allowlist and the other a denylist; together they are a rule nobody can read off "
                f"the record, and the schema forbids the pair.")
        # The SAME no-op check, for the denylist. A scope that names something the pack does not
        # write is the failure this field class exists to prevent, and it is worse on a denylist:
        # an allowlist that admits nothing delivers nothing and is noticed, while a denylist that
        # refuses nothing delivers EVERYTHING and reads exactly like a scope that worked.
        _w = set()
        if deny:
            try:
                _rr = _pe().resolve(pack_id).get("derived_rules", [])
            except Exception:
                _rr = packs[pack_id].get("derived_rules", [])
            _w = {r["target_slot"] for r in _rr} | {f"{r['target_slot']}/{r.get('dimension')}" for r in _rr}
            # A DENYLIST THAT REFUSES EVERYTHING is a binding that delivers nothing while still
            # reading as an `opening`-role pack on the node. The comment below claims an allowlist
            # admitting nothing "is noticed"; nothing noticed either form until the WP-5.14 audit
            # tried it. A scope must leave at least one rule, or it is a removal wearing a scope's
            # clothes and the binding should simply be deleted.
            _left = [r for r in _rr
                     if not (r["target_slot"] in deny
                             or "%s/%s" % (r["target_slot"], r.get("dimension")) in deny)]
            if not _left:
                errors.append(
                    f"{nid}: entry {i} ('{pack_id}') excludes every rule the pack writes -- the "
                    f"binding delivers nothing while still reading as a bound {e.get('role')} "
                    f"pack. Delete the binding instead of scoping it to nothing.")
        for entry in (deny or []):
            if entry not in _w:
                errors.append(
                    f"{nid}: entry {i} ('{pack_id}') excludes '{entry}', which that pack does not "
                    f"write -- the exclusion refuses nothing and the binding delivers the whole "
                    f"pack while reading as though it were scoped")
        if deny is not None and not deny:
            errors.append(f"{nid}: entry {i} ('{pack_id}') has an empty `slots_except` scope")
        if scope is not None:
            # OVERLAY-MERGED rules, via pe.resolve -- not the pack file's own derived_rules. The
            # enforcer (resolve_kit.eval_packs) filters against the resolved pack, and 18 of the 57
            # packs are overlays that inherit most of their rules from a base: gibbs-ionic writes 8
            # in its own file and 18 once resolved. Validating against the raw file would reject a
            # legitimate scope naming any of the 10 inherited ones -- rejecting good data with the
            # words "the scope admits nothing", which is worse than the no-op it exists to catch.
            # Found by audit 25 Aug 2026; latent, because no scope currently targets an overlay.
            try:
                resolved_rules = _pe().resolve(pack_id).get("derived_rules", [])
            except Exception:
                resolved_rules = packs[pack_id].get("derived_rules", [])
            written = {r["target_slot"] for r in resolved_rules}
            written |= {f"{r['target_slot']}/{r.get('dimension')}" for r in resolved_rules}
            for entry in scope:
                if entry not in written:
                    errors.append(
                        f"{nid}: entry {i} ('{pack_id}') is scoped to '{entry}', which that pack "
                        f"does not write -- the scope admits nothing and the binding is a no-op")
            if not scope:
                errors.append(f"{nid}: entry {i} ('{pack_id}') has an empty `slots` scope")
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

    # Precedence must not contradict role. WP-4.6 (25 Aug 2026) found sixteen nodes where a
    # secondary, optional or role-scoped binding sat at a LOWER precedence than a primary one --
    # twelve of them introduced by that package itself, because every new binding was inserted at
    # the first unused precedence and 0 is usually free. Nothing caught it: `precedence` was checked
    # for being a total order and never for agreeing with `role`, so the two fields could say
    # opposite things and the build stayed green.
    #
    # Only the narrow rule is an ERROR, because it is the only one the corpus actually holds to.
    # A measurement over all 132 buildable nodes found `secondary` sitting ahead of `facade`,
    # `opening`, `interior`, `room` and `massing` in 253 places across 59 nodes -- which is not a
    # bug but the corpus's own convention: the ORDER packs come first, then the role packs. And
    # `optional` sits ahead of a role pack in 40 places across 23 nodes, which is untidy, is mostly
    # older than this package, and is not worth churning the corpus over. Both are warned about,
    # once per node, so the observation is visible without failing anyone's build.
    prims = [e for e in entries if e.get("role") == "primary" and e.get("precedence") is not None]
    if prims:
        lo = min(e["precedence"] for e in prims)
        ahead = [e for e in entries
                 if e.get("role") not in ("primary", None)
                 and e.get("precedence") is not None and e["precedence"] < lo]
        for e in ahead:
            errors.append(
                f"{nid}: '{e['pack']}' is {e['role']} at precedence {e['precedence']} but sits "
                f"ahead of a primary at {lo} -- precedence and role disagree"
            )
    opts = [e for e in entries if e.get("role") == "optional" and e.get("precedence") is not None]
    if opts:
        others = [e for e in entries
                  if e.get("role") not in ("optional", None) and e.get("precedence") is not None]
        if others and min(o["precedence"] for o in opts) < max(x["precedence"] for x in others):
            warnings.append(
                f"{nid}: an optional binding sits ahead of a non-optional one -- untidy rather "
                f"than wrong, and mostly older than WP-4.6; see the note in this file"
            )


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
    graph = _graph()
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

        check_declines(node, packs, graph, errors)
        check_opt_ins(node, packs, graph, errors)
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
