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
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLES = ("primary", "secondary", "facade", "opening", "interior", "massing", "room")

# THE RATCHET, in one place. tests/test_wp46_packs.py IMPORTS this dict rather than restating the
# numbers, because a threshold duplicated in two files drifts apart and a ratchet that has drifted
# is slack.
#
# THAT SENTENCE WAS FALSE FOR THREE DAYS AND IS TRUE NOW (WP-8.2, 28 Aug 2026). No import existed;
# the test restated (293, 3366, 222) as a literal while this dict said 294/3367/222, so `--strict`
# could not have caught role_gaps or inherited_packs growing by one. The two drifted apart exactly
# as this comment says they cannot -- a claim in source that a later package falsified and nobody
# updated, in the file that measures OQ 51. The import is real now and a test asserts it. It was already slack once: this file compared (gaps, packs) as a TUPLE -- lexicographic,
# so inherited_packs could double unnoticed while role_gaps fell by one -- against a role_gaps
# threshold of 329 when the real figure was 294. Thirty-five units of silence.
#
# The test asserts EQUALITY, not `<=`, deliberately. Working the OQ 51 backlog LOWERS these; the
# equality assert forces whoever lowers them to come here and say so, which keeps the ratchet tight
# instead of letting slack accumulate underneath it as the numbers fall.
# 26 Aug 2026: unendorsed 233 -> 222, endorsed 61 -> 72. Eleven storey-graduation gaps
# adjudicated against each node's OWN record (see docs/reports/oq-51-first-adjudication-pass.md);
# re-pinned so the gain cannot be lost. role_gaps and inherited_packs do NOT move on an
# endorsement -- the cascade still delivers exactly what it delivered; what changed is that a
# human has now judged eleven of those deliveries to be right.
RATCHET = {"role_gaps": 287, "inherited_packs": 3356, "unendorsed": 249}

# A FLOOR, and it is what keeps the ceilings honest once a node can DECLINE a pack. `unendorsed`
# stopped being monotone the moment declining re-attributes a role to the next ancestor, which
# may itself be unjudged: a pass that judges ten and re-opens three is progress, and a ceiling
# alone cannot see that. `judged` is endorsed + declined and only ever goes UP.
RATCHET_FLOOR = {"judged": 48}

# A FOURTH, SEPARATE MEASUREMENT: pack rules landing on a slot the resolved kit binds
# `forbidden`. Not the OQ 51 backlog and deliberately not mixed into it. See --forbidden.
FORBIDDEN_RATCHET = 787

# THE FIRST FOUR DECLINES ARE THE ARGUMENT FOR THIS FLOOR, and the measurement is worth keeping.
# `ranch-style`, `craftsman-bungalow`, `california-bungalow` and `minimal-traditional` all
# receive `storey-graduation` -- a second-to-first-storey ratio -- and all four say in their own
# records that they have one storey, or one and a half. Declining it removed four real deliveries
# (inherited_packs 3366 -> 3362) and moved `unendorsed` by ZERO: each node's massing role simply
# re-attributed to the next ancestor, which nobody has judged either. Four correct refusals,
# headline number flat. Six more followed on `chambers-ionic` -- 3362 -> 3356, judged 42 -> 48,
# `unendorsed` STILL 249. Ten correct refusals and the headline has not moved once. That is why `judged` is the ratchet that matters and `unendorsed` is a
# work list rather than a score.


def applies_to_index():
    """pack id -> the set of nodes its own applies_to vouches for."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
        d = json.load(open(f))
        out[d["id"]] = set(d.get("applies_to") or ())
    return out



# PACKS WHOSE `applies_to` IS A BEHAVIOURAL GATE AND NOT BOOKKEEPING.
#
# Endorsing a node into one of these does not merely record a judgment -- it turns a check on.
# Nothing said so anywhere until WP-8.2: not OQ 51, not the adjudication report, not CLAUDE.md.
# The 26 August pass endorsed eleven nodes into `storey-graduation` and thereby switched a
# storey-height ratio check ON for eleven styles, and recorded that in no place at all.
#
# tests/test_wp46_packs.py asserts each pack id still occurs in each file named here, so a gate
# that MOVES fails a test rather than leaving this table quietly false -- WP-6.4's lesson that
# "until X lands" is a lie the moment X lands.
GATES = {
    "storey-graduation": [
        ("build/structure.py", "graduation_check",
         "storey-to-storey ratios are checked AT ALL. Called from build_section, so every plan "
         "of an endorsed style gains the finding and can now FAIL it.")],
    "timber-bay": [
        ("build/structure.py", "span_check via _timber_bay_applies_to",
         "span capacity switches from the light-frame joist table to the bay module's own"),
        ("build/geometry_cp.py", "the CP model reads the same list", "")],
    "opening-proportion": [
        ("build/elevation.py", "the build_elevation scope gate",
         "HALF of an AND with facade-classical: the whole elevation generator runs, or returns "
         "applicable:false with an empty measurements dict")],
    "facade-classical": [
        ("build/elevation.py", "the build_elevation scope gate", "the other half of that AND")],
    "gibbs-ionic": [
        ("build/elevation.py", "gibbs_applies",
         "`gibbs_order_applies_to_style` becomes a published measurement and the "
         "note_order_not_named_for_style disclosure disappears -- read OQ 84 first")],
}


def load():
    p = os.path.join(ROOT, "dist", "taxonomy.json")
    if not os.path.exists(p):
        sys.exit("dist/taxonomy.json missing — run build/build.py first")
    return json.load(open(p))


def measure(g):
    N = g["nodes"]
    build = [nid for nid, n in N.items() if n.get("rank") in ("style", "variant")]
    gaps, inherited_packs, declines = [], [], []
    for nid in sorted(build):
        n = N[nid]
        own = n.get("proportion_packs") or []
        own_roles = {e["role"] for e in own}
        own_ids = {e["pack"] for e in own}
        # OQ 51's refusal half (WP-8.2). A decline REMOVES the delivery -- it is not bookkeeping
        # beside a gap that stays. `resolve_packs` skips the pack, so the meter must too, or it
        # would go on describing a corpus nobody resolves (the same error `--slots` made when it
        # read the node's own kit while the resolver read the cascade). The gap then either
        # vanishes, because no other ancestor fills the role, or RE-ATTRIBUTES to the next
        # ancestor and has to be judged again -- which is why `unendorsed` is no longer monotone
        # and why RATCHET_FLOOR exists.
        declined = {d["pack"] for d in (n.get("declined_packs") or [])}
        chain = list(n.get("_cascade") or [])
        for pid in sorted(declined):
            if any(e["pack"] == pid
                   for a in chain for e in (N[a].get("proportion_packs") or [])):
                declines.append((nid, pid))
        # nearest ancestor binding each role / pack the node does not bind itself
        from_anc_role, from_anc_pack = {}, {}
        for a in chain:
            for e in (N[a].get("proportion_packs") or []):
                # `e["pack"] not in own_ids` ON BOTH LOOPS, added 28 Aug 2026 (WP-8.2). The role
                # loop did not have it and the pack loop did, and the asymmetry was not a style
                # choice -- it made the meter name deliveries that cannot happen. `resolve_packs`
                # walks `[node] + cascade` and keys on PACK ID, first wins, so when the node
                # binds pack P itself at chain[0] an ancestor's binding of P never governs
                # anything; it lands in `_overridden_by_ancestor` and is dead. Attributing a role
                # gap to that dead delivery then asks the WRONG pack's `applies_to` whether the
                # node is endorsed -- and it usually says yes, because the node binds that pack.
                #
                # Measured: 6 role gaps vanish (no other ancestor fills the role) and 33 more
                # re-attribute to a pack whose `applies_to` does NOT name the node. Net
                # 293/222/71 -> 287/249/38. The backlog is 27 larger than was published and
                # nearly half the endorsed figure was an artefact -- and the error flattered,
                # which is the direction this corpus has been caught by before.
                if e["pack"] in own_ids or e["pack"] in declined:
                    continue
                if e["role"] not in own_roles:
                    from_anc_role.setdefault(e["role"], (a, e["pack"]))
                from_anc_pack.setdefault(e["pack"], a)
        for role in ROLES:
            if role not in own_roles and role in from_anc_role:
                gaps.append((nid, role) + from_anc_role[role])
        for pid, a in from_anc_pack.items():
            inherited_packs.append((nid, pid, a))
    return build, gaps, inherited_packs, declines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roles", action="store_true")
    ap.add_argument("--slots", metavar="NODE")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--ancestors", action="store_true",
                    help="group the backlog by the ancestor that DELIVERS the gap — a reading "
                         "order, not an authoring axis")
    ap.add_argument("--full", action="store_true",
                    help="print every node in a group instead of the first five")
    ap.add_argument("--gates", action="store_true",
                    help="which packs' applies_to is a live behavioural gate, and what "
                         "endorsing one turns on")
    ap.add_argument("--forbidden", action="store_true",
                    help="pack rules landing on a slot the resolved kit binds `forbidden` — "
                         "ratcheted separately from the OQ 51 numbers")
    ap.add_argument("--impact", nargs=2, metavar=("NODE", "PACK"),
                    help="what a node loses, and what takes over, if it declines a pack")
    ap.add_argument("--unendorsed", action="store_true",
                    help="list the gaps no pack author has vouched for — OQ 51's work list")
    a = ap.parse_args()
    g = load()
    build, gaps, inherited, declines = measure(g)
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
                pid = ch["chosen"]["pack"]
                # A DECLINED PACK CAN STILL BE NAMED BY AN INHERITED SLOT-LEVEL RULING, and that
                # contradiction is worth printing rather than crashing on. `choose_pack` consults
                # the resolved slot record's own `packs` block -- a person's explicit ruling --
                # BEFORE precedence, and that block cascades like everything else in the kit. So
                # `ranch-style` declines `storey-graduation` on its own record while its
                # `baseboard`, `crown` and `chair_rail` still carry an ancestor's ruling naming
                # it. The decline wins (resolve_packs never delivered the pack, so the rule does
                # not exist to be chosen), and the stale ruling is surfaced here. Same class as
                # OQ 87: a slot record inherited in full, including a decision the descendant has
                # since made differently.
                src = packs.get(pid, {}).get("_source")
                foreign.append((sid, pid, src or "DECLINED by this node — an inherited "
                                                "slot-level `packs` ruling still names it"))
        print(f"{a.slots}: {len(by_slot)} slot(s) dimensioned, {len(foreign)} by a pack it never bound")
        for sid, pid, src in foreign:
            print(f"   {sid:28s} <- {pid:22s} bound on {src}")
        return



    if a.forbidden or a.impact:
        sys.path.insert(0, os.path.join(ROOT, "build"))
        import resolve_kit as rk
        CTX = {"ceiling_height": 108.0, "storey_height": 120.0, "opening_width": 36.0,
               "opening_height": 80.0, "span": 540.0, "wall_thickness": 13.5}

        def governed(nid, drop=None):
            """(slot -> chosen pack) for a node, optionally with one pack dropped."""
            chain = rk.chain_for(g, nid)
            packs = rk.resolve_packs(g, chain)
            if drop:
                packs = collections.OrderedDict(
                    (k, v) for k, v in packs.items() if k != drop)
            by_slot, _ = rk.eval_packs(packs, CTX, None)
            kit, _sv = rk.resolve_slots(g, chain, rk.scope_for(g, nid))
            out = {}
            for sid, rows in by_slot.items():
                ch = rk.choose_pack(kit.get(sid) or {}, rows, CTX)
                if ch and ch.get("chosen"):
                    out[sid] = (ch["chosen"]["pack"], packs.get(ch["chosen"]["pack"], {}).get("_source"))
            return out, kit

    if a.impact:
        nid, pid = a.impact
        before, _kit = governed(nid)
        chain = rk.chain_for(g, nid)
        src = next((x for x in chain[1:]
                    if any(e["pack"] == pid
                           for e in (g["nodes"][x].get("proportion_packs") or []))), None)
        mine = sorted(k for k, v in before.items() if v[0] == pid)
        print(f"{nid} receives {pid}" + (f" from {src}" % () if src else " from nowhere"))
        edge = any(e.get("target") == src for e in (g["nodes"][nid].get("lineage") or []))
        if src:
            print(f"  cascade depth {chain.index(src)}; "
                  f"{'a DIRECT lineage edge exists' if edge else 'there is NO direct lineage edge between them'}.")
        print(f"It currently GOVERNS {len(mine)} slot(s): {', '.join(mine) or '—'}\n")
        if not mine:
            print("Declining it changes no dimension on this node.")
            return
        after, kit = governed(nid, drop=pid)
        lost = 0
        print("If declined:")
        for sid in mine:
            nxt = after.get(sid)
            binding = (kit.get(sid) or {}).get("binding")
            flag = "  [the resolved kit binds this slot FORBIDDEN]" if binding == "forbidden" else ""
            if nxt:
                print(f"  {sid:28s} -> {nxt[0]:22s} ({nxt[1]}){flag}")
            else:
                lost += 1
                print(f"  {sid:28s} -> NOTHING — this slot loses all dimensioning{flag}")
        print(f"\n  {lost} slot(s) would lose all dimensioning.")
        print("\nA decline stops a wrong pack. It does not supply a right one — OQ 58's stated")
        print("limit, one layer down.")
        return

    if a.forbidden:
        # A SEPARATE MEASUREMENT AND A SEPARATE RATCHET. This is not the OQ 51 backlog: it counts
        # a KIT binding overruled by a PACK, not a role nobody bound, and declining packs will not
        # close it -- `--impact carpenter-gothic chambers-ionic` shows the slot handed to another
        # order on a slot the node forbids either way. Reported here and fixed in its own package,
        # because honouring it changes dimensions on most of the corpus.
        pairs, triples, rules = [], 0, 0
        by_slot, by_node = collections.Counter(), collections.Counter()
        pack_for_slot = collections.defaultdict(collections.Counter)
        by_precedence = 0
        NODES = g["nodes"]
        buildable = sorted(x for x, n in NODES.items()
                           if n.get("rank") in ("style", "variant"))
        for nid in buildable:
            chain = rk.chain_for(g, nid)
            packs = rk.resolve_packs(g, chain)
            own = {e["pack"] for e in (g["nodes"][nid].get("proportion_packs") or [])}
            bs, _ = rk.eval_packs(packs, CTX, None)
            kit, _sv = rk.resolve_slots(g, chain, rk.scope_for(g, nid))
            for sid, rows in bs.items():
                if (kit.get(sid) or {}).get("binding") != "forbidden":
                    continue
                ch = rk.choose_pack(kit.get(sid) or {}, rows, CTX)
                if not (ch and ch.get("chosen")):
                    continue
                pairs.append((nid, sid))
                by_slot[sid] += 1
                by_node[nid] += 1
                triples += len({r["pack"] for r in rows})
                rules += len(rows)
                for r in rows:
                    pack_for_slot[sid][r["pack"]] += 1
                if ch.get("how") == "style.proportion_packs":
                    by_precedence += 1
        print(f"{len(pairs)} (node, slot) pair(s) where the RESOLVED kit binds the slot "
              f"`forbidden`\nand a proportion pack dimensions it anyway, over "
              f"{len(by_node)} of {len(buildable)} buildable nodes.")
        print(f"{triples} (node, slot, pack) triples; {rules} individual rules.")
        print(f"{by_precedence} of the {len(pairs)} are decided by `style.proportion_packs` "
              f"precedence — nobody\nchose them; a `slot.packs` ruling is a human's and there "
              f"are {len(pairs) - by_precedence}.\n")
        print(f"  {'slot':24s} pairs  top packs")
        for sid, c in by_slot.most_common(12):
            top = ", ".join(k for k, _ in pack_for_slot[sid].most_common(3))
            print(f"  {sid:24s} {c:5d}  {top}")
        print(f"\n  {'node':32s} pairs")
        for nid, c in by_node.most_common(8):
            print(f"  {nid:32s} {c:5d}")
        print(f"\nRatchet {FORBIDDEN_RATCHET}. This is NOT the OQ 51 backlog and moves "
              f"independently of it:\nit counts a kit binding overruled by a pack, not a role "
              f"nobody bound. Declining packs will\nNOT close it — the slot is handed to the "
              f"next pack, which forbids it just as much.")
        if len(pairs) > FORBIDDEN_RATCHET:
            print(f"\nRATCHET BROKEN — forbidden-slot overrides grew: "
                  f"{FORBIDDEN_RATCHET} -> {len(pairs)}")
            if a.strict:
                sys.exit(1)
        return

    if a.ancestors:
        # A READING ORDER, NOT AN AUTHORING AXIS, and the DIRECT column is what says so.
        # A per-edge deny was designed and refused on exactly this measurement: most gaps reach
        # their delivering ancestor with no lineage edge between the two at all, so there is no
        # edge to write the refusal on. Adjudicate an ancestor's rows in one sitting -- one
        # classical-order question, answered once -- and write every verdict on the NODE.
        by_anc = collections.defaultdict(list)
        for nid, role, anc, pid in unendorsed:
            by_anc[anc].append((nid, role, pid))
        print(f"{len(unendorsed)} unendorsed role gap(s) arrive from {len(by_anc)} ancestor(s).")
        print("DIRECT counts the gaps whose node has a lineage edge straight to that ancestor;")
        print("the rest reach it transitively, down each node's own path through the cascade.\n")
        print(f"  {'ancestor':32s} {'GAPS':>4} {'NODES':>5} {'DIRECT':>6}  packs")
        for anc, rows in sorted(by_anc.items(), key=lambda kv: -len(kv[1])):
            nodes = sorted({r[0] for r in rows})
            direct = sum(1 for r in rows
                         if any(e.get("target") == anc
                                for e in ((g["nodes"].get(r[0]) or {}).get("lineage") or [])))
            packs = collections.Counter(r[2] for r in rows)
            top = ", ".join(f"{k} {v}" for k, v in packs.most_common(4))
            print(f"  {anc:32s} {len(rows):4d} {len(nodes):5d} {direct:6d}  {top}")
        return

    if a.gates:
        live = collections.Counter(pid for _, _, _, pid in unendorsed)
        on_gates = sum(c for p_, c in live.items() if p_ in GATES)
        print(f"{len([p_ for p_ in live if p_ in GATES])} of the {len(live)} packs in the work "
              f"list gate live behaviour.")
        print(f"{on_gates} of the {len(unendorsed)} unendorsed gaps sit on them: endorsing one "
              f"of those is a code change with no diff.\n")
        for pid in sorted(GATES, key=lambda k: -live.get(k, 0)):
            print(f"  {pid:22s} {live.get(pid, 0):3d} gap(s)")
            for path, sym, why in GATES[pid]:
                print(f"      ARMS {path}::{sym}")
                if why:
                    for line in textwrap.wrap(why, 88):
                        print(f"        {line}")
            if pid not in live:
                print("      NOT in the work list (0 unendorsed gaps) and still half of a live "
                      "gate — a list ordered by unendorsed count cannot show you that.")
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
            shown = nodes if a.full else nodes[:5]
            print(f"  {pid:24s} {len(nodes):5d} {c:5d}  "
                  f"{', '.join(shown)}{'' if a.full or len(nodes) <= 5 else ' …'}")
        if not a.full:
            print("\n  (--full prints every node; you cannot work a list the tool will not print)")
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
    print(f"      declined    {len(declines):3d}  a node has judged these WRONG and the cascade no longer delivers them")
    print(f"      judged      {len(gaps) - len(unendorsed) + len(declines):3d}  endorsed + declined — the only one of these that may only go UP")
    print("\nOQ 51 is RULED: adjudicate the unendorsed first, flip pack inheritance to opt-in after.")
    print("`--unendorsed` prints the work list in leverage order.")

    # Compared one at a time against RATCHET, deliberately. A tuple comparison here is
    # lexicographic: it would let inherited_packs double unnoticed as long as role_gaps had fallen
    # by one. Each number is its own ratchet and names itself when it grows.
    now = {"role_gaps": len(gaps), "inherited_packs": len(inherited), "unendorsed": len(unendorsed)}
    grown = [f"{k}: {RATCHET[k]} -> {v}" for k, v in now.items() if v > RATCHET[k]]
    # The floor, compared the other way. See RATCHET_FLOOR: `unendorsed` is no longer monotone
    # once a decline can re-attribute a role to the next ancestor, so a ceiling alone would read
    # a pass that judged ten and re-opened three as a regression.
    floors = {"judged": len(gaps) - len(unendorsed) + len(declines)}
    fell = [f"{k}: {RATCHET_FLOOR[k]} -> {v}" for k, v in floors.items() if v < RATCHET_FLOOR[k]]
    if grown:
        print("\nRATCHET BROKEN — the inheritance backlog grew: " + "; ".join(grown))
    if fell:
        print("\nFLOOR BROKEN — adjudications were lost: " + "; ".join(fell))
    if a.strict:
        sys.exit(1 if (grown or fell) else 0)


if __name__ == "__main__":
    main()
