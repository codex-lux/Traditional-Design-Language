#!/usr/bin/env python3
"""Report what the lineage cascade delivers that nobody bound — OQ 51.

    python3 build/check_inheritance.py              # the three ratchet numbers
    python3 build/check_inheritance.py --roles      # per node, roles filled only by an ancestor
    python3 build/check_inheritance.py --slots ID   # per slot, who governs it and from where
    python3 build/check_inheritance.py --unendorsed # the work list, in leverage order (OQ 51's ruling)
    python3 build/check_inheritance.py --strict     # exit nonzero if any ratchet has grown

WHAT THIS IS ABOUT. `proportion_packs` being empty on a node means the NODE'S OWN array is empty.
`build/resolve_kit.py::resolve_packs` walks the whole `_cascade` and takes the nearest binder of
each pack id, so a node inherits its entire ancestry's bindings whether anyone judged them for it
or not. "132 of 132 bound" counts a node's own array; it has never measured what a node RECEIVES.

The finding that produced this checker: `egyptian-revival` was the corpus's one deliberately
unbound node, held out because nothing fitted its trabeated order — while `facade-peristyle` was
reaching it from five ancestors, unscoped, carrying an entasis rule its own c04 forbids.

THREE NUMBERS, AND THE THIRD IS THE WORK LIST. `role_gaps` counts (node, role) pairs where a node
has no binding of its own in that role — inheritance is filling it. `inherited_packs` counts pack
arrivals purely by descent, which is the scale of the mechanism rather than a fault count. But a
gap is not automatically wrong: if the inherited pack's own `applies_to` names the node, somebody
DID judge that this pack belongs there, and the cascade merely delivered what an author intended.
So `unendorsed` splits the gaps into the ones a pack author vouched for and the ones nobody has
ever judged. That third number is the backlog OQ 51's ruling says to work.

Adding a node to a pack's `applies_to` is therefore not bookkeeping — it is the adjudication, and
it moves a gap from unendorsed to endorsed. `unendorsed` should fall as the corpus is worked;
when it approaches zero, opt-in pack inheritance becomes a safety net rather than a cliff.

None of the three fails the build by default. This is a measured, documented backlog, not a
regression, and what protects the corpus is that the numbers are pinned in
tests/test_wp46_packs.py and cannot grow without a test going red.
"""
import argparse, collections, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLES = ("primary", "secondary", "facade", "opening", "interior", "massing", "room")

# THE RATCHET, in one place. tests/test_wp46_packs.py imports THIS dict rather than restating the
# numbers, because a threshold duplicated in two files drifts apart and a ratchet that has drifted
# is slack. It was already slack once: this file compared (gaps, packs) as a TUPLE -- lexicographic,
# so inherited_packs could double unnoticed while role_gaps fell by one -- against a role_gaps
# threshold of 329 when the real figure was 294. Thirty-five units of silence.
#
# The test asserts EQUALITY, not `<=`, deliberately. Working the OQ 51 backlog LOWERS these; the
# equality assert forces whoever lowers them to come here and say so, which keeps the ratchet tight
# instead of letting slack accumulate underneath it as the numbers fall.
RATCHET = {"role_gaps": 294, "inherited_packs": 3367, "unendorsed": 233}


def applies_to_index():
    """pack id -> the set of nodes its own applies_to vouches for."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
        d = json.load(open(f))
        out[d["id"]] = set(d.get("applies_to") or ())
    return out


def load():
    p = os.path.join(ROOT, "dist", "taxonomy.json")
    if not os.path.exists(p):
        sys.exit("dist/taxonomy.json missing — run build/build.py first")
    return json.load(open(p))


def measure(g):
    N = g["nodes"]
    build = [nid for nid, n in N.items() if n.get("rank") in ("style", "variant")]
    gaps, inherited_packs = [], []
    for nid in sorted(build):
        n = N[nid]
        own = n.get("proportion_packs") or []
        own_roles = {e["role"] for e in own}
        own_ids = {e["pack"] for e in own}
        chain = list(n.get("_cascade") or [])
        # nearest ancestor binding each role / pack the node does not bind itself
        from_anc_role, from_anc_pack = {}, {}
        for a in chain:
            for e in (N[a].get("proportion_packs") or []):
                if e["role"] not in own_roles:
                    from_anc_role.setdefault(e["role"], (a, e["pack"]))
                if e["pack"] not in own_ids:
                    from_anc_pack.setdefault(e["pack"], a)
        for role in ROLES:
            if role not in own_roles and role in from_anc_role:
                gaps.append((nid, role) + from_anc_role[role])
        for pid, a in from_anc_pack.items():
            inherited_packs.append((nid, pid, a))
    return build, gaps, inherited_packs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roles", action="store_true")
    ap.add_argument("--slots", metavar="NODE")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--unendorsed", action="store_true",
                    help="list the gaps no pack author has vouched for — OQ 51's work list")
    a = ap.parse_args()
    g = load()
    build, gaps, inherited = measure(g)
    applies = applies_to_index()
    unendorsed = [t for t in gaps if t[0] not in applies.get(t[3], ())]

    if a.slots:
        sys.path.insert(0, os.path.join(ROOT, "build"))
        import resolve_kit as rk
        CTX = {"ceiling_height": 108.0, "storey_height": 120.0, "opening_width": 36.0,
               "opening_height": 80.0, "span": 540.0, "wall_thickness": 13.5}
        chain = rk.chain_for(g, a.slots)
        packs = rk.resolve_packs(g, chain)
        own = {e["pack"] for e in (g["nodes"][a.slots].get("proportion_packs") or [])}
        by_slot, _ = rk.eval_packs(packs, CTX, None)
        # The CASCADE-RESOLVED slot record, not `load_kit(node)`. `choose_pack` consults the
        # record's own `packs` block -- a person's explicit ruling -- before precedence, and that
        # block is frequently inherited rather than restated on the node. Reading the node's own
        # kit file therefore takes a different branch on any slot whose ruling came from an
        # ancestor, and reports a different governing pack. Found by audit 25 Aug 2026: it made
        # ranch-style read 68 of 78 where the resolver's own semantics give 69, and pueblo-revival
        # 52 where they give 53. Both wrong numbers had been published. `resolve_kit.main` uses
        # `resolve_slots`, so this must too or the diagnostic measures a corpus nobody resolves.
        kit, _savings = rk.resolve_slots(g, chain, rk.scope_for(g, a.slots))
        foreign = []
        for sid, rows in sorted(by_slot.items()):
            ch = rk.choose_pack(kit.get(sid) or {}, rows, CTX)
            if ch and ch.get("chosen") and ch["chosen"]["pack"] not in own:
                foreign.append((sid, ch["chosen"]["pack"], packs[ch["chosen"]["pack"]]["_source"]))
        print(f"{a.slots}: {len(by_slot)} slot(s) dimensioned, {len(foreign)} by a pack it never bound")
        for sid, pid, src in foreign:
            print(f"   {sid:28s} <- {pid:22s} bound on {src}")
        return

    if a.unendorsed:
        by_pack = collections.Counter(pid for _, _, _, pid in unendorsed)
        print(f"{len(unendorsed)} of {len(gaps)} role gaps are endorsed by nobody.")
        print("Leverage order — adjudicating one pack settles every node under it.")
        print("NODES is the leverage (one judgment per node); GAPS is how many role gaps close.")
        print("They differ where a node reaches the same pack in two roles.\n")
        print(f"  {'pack':24s} {'NODES':>5} {'GAPS':>5}")
        for pid, c in by_pack.most_common():
            # One node reaching the same pack in two roles is ONE judgment, not two. The header
            # count is (node, role) pairs; the leverage is DISTINCT NODES. Printing a deduped list
            # under a pair count made the two disagree for facade-picturesque (7 gaps, 6 nodes),
            # which is a count whose label meant something other than the number. Both, labelled.
            nodes = sorted({n for n, _, _, p in unendorsed if p == pid})
            print(f"  {pid:24s} {len(nodes):5d} {c:5d}  "
                  f"{', '.join(nodes[:5])}{' …' if len(nodes) > 5 else ''}")
        return

    if a.roles:
        by_node = collections.defaultdict(list)
        for nid, role, anc, pid in gaps:
            by_node[nid].append((role, anc, pid))
        for nid in sorted(by_node, key=lambda n: -len(by_node[n]))[:25]:
            rs = by_node[nid]
            print(f"  {nid:34s} {len(rs)} role(s) filled by an ancestor: "
                  + ", ".join(f"{r}<-{a2}" for r, a2, _ in rs))

    by_role = collections.Counter(r for _, r, _, _ in gaps)
    print(f"\n{len(build)} buildable node(s).")
    print(f"  role_gaps       {len(gaps):4d}  (node, role) pairs where inheritance fills a role the node never bound")
    for r, c in by_role.most_common():
        print(f"      {r:10s} {c:3d}")
    print(f"  inherited_packs {len(inherited):4d}  (node, pack) arrivals purely by descent")
    print(f"  unendorsed      {len(unendorsed):4d}  of those role gaps, the ones no pack's applies_to vouches for")
    print(f"      endorsed    {len(gaps) - len(unendorsed):3d}  an author DID judge these; the cascade delivered what was intended")
    print("\nOQ 51 is RULED: adjudicate the unendorsed first, flip pack inheritance to opt-in after.")
    print("`--unendorsed` prints the work list in leverage order.")

    # Compared one at a time against RATCHET, deliberately. A tuple comparison here is
    # lexicographic: it would let inherited_packs double unnoticed as long as role_gaps had fallen
    # by one. Each number is its own ratchet and names itself when it grows.
    now = {"role_gaps": len(gaps), "inherited_packs": len(inherited), "unendorsed": len(unendorsed)}
    grown = [f"{k}: {RATCHET[k]} -> {v}" for k, v in now.items() if v > RATCHET[k]]
    if grown:
        print("\nRATCHET BROKEN — the inheritance backlog grew: " + "; ".join(grown))
    if a.strict:
        sys.exit(1 if grown else 0)


if __name__ == "__main__":
    main()
