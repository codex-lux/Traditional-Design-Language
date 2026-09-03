#!/usr/bin/env python3
"""Resolve a style's kit of parts through the cascade.

A kit file is not a parts list, it is a diff against its ancestors. This script turns the
diff back into a building specification: it walks the `_cascade` chain that build.py
precomputes, merges the kit files nearest-ancestor-wins, applies `extends` deltas, resolves
which of several bound proportion packs governs each slot, and prints the result with the
ancestor each binding came from.

The SOURCE column is the point. A resolved kit without provenance is just a long file;
with provenance you can see that Tidewater Georgian is twenty-one local decisions on top of
sixty-odd inherited ones, and you can argue about the twenty-one.

Resolution rule (docs/inheritance.md, extended for kit schema 0.2.0):
    walk the chain nearest first;
    `specified` or `forbidden` stops the walk and supplies the value;
    `extends` records a delta and the walk CONTINUES to find the base it merges into;
    `open` is transparent;
    with no stop found, the slot is open and unresolved — an `extends` with no base is a
    dangling diff, reported as such, and check_kits.py fails on it.

Merge semantics for `extends`, applied farthest-ancestor-first so the nearest wins:
    parameters   merge by key; a child key replaces the inherited one outright
    variants     apply each record's `op` — add / remove / replace, matched on id;
                 a record with no op defaults to add
    rule         child replaces if present, otherwise inherited. THERE IS NO APPEND,
                 which is the one case extends does not cover; see the note it prints
    packs, code_conflict, determined_by, judgment, invented, confidence
                 child replaces the whole field if present, otherwise inherited
    note         both are kept — the child's as `note`, the ancestors' as inherited_notes

Usage:
    python3 build/resolve_kit.py tidewater-georgian
    python3 build/resolve_kit.py tidewater-georgian --ceiling 132 --module 5
    python3 build/resolve_kit.py tidewater-georgian --group openings --verbose
    python3 build/resolve_kit.py tidewater-georgian --slot chair_rail --verbose
    python3 build/resolve_kit.py tidewater-georgian --json
    python3 build/resolve_kit.py tidewater-georgian --slot window_head_masonry --date 1745
        # date-conditional resolution (docs/open-questions.md #22): narrows every
        # slot's variant list to what applies_when.date_range permits at that year.
        # Nothing excluded is silently dropped -- what got left out is always shown.
"""
import json, os, sys, argparse, collections, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import proportion_engine as pe
import modcache

STOP = ("specified", "forbidden")
AUTHORING_CEILING = 108.0        # the context the kits' in_calibration flags were set at


# ---------------------------------------------------------------- load
def load_graph():
    p = os.path.join(ROOT, "dist", "taxonomy.json")
    if not os.path.exists(p):
        sys.exit("dist/taxonomy.json missing — run build/build.py first")
    return json.load(open(p))


def load_kit(style_id):
    p = os.path.join(ROOT, "kits", "%s.kit.json" % style_id)
    return json.load(open(p)).get("slots", {}) if os.path.exists(p) else {}


def slot_order(graph):
    return [(s["id"], s["group"], s.get("name", s["id"])) for s in graph["slots"]]


def chain_for(graph, style_id):
    n = graph["nodes"].get(style_id)
    if not n:
        sys.exit("no such node: %s" % style_id)
    return [style_id] + list(n.get("_cascade", []))


def scope_for(graph, style_id):
    """Which ancestors in this node's chain may contribute only SOME slots (OQ 58).

    Absent for almost every ancestor, and absent entirely for a node with no scoped edge, which
    is the historical behaviour: an edge with no `slots` list carries the donor's whole kit. An
    edge that names slots carries those and nothing else, which is what a `hybridizes_with` edge
    drawn for one aspect of a donor's practice actually means."""
    return dict((graph["nodes"].get(style_id) or {}).get("_cascade_scope") or {})


# ---------------------------------------------------------------- extends merge
MERGE_REPLACE = ("rule", "packs", "code_conflict", "determined_by",
                 "judgment", "invented", "confidence", "sources", "status")


def apply_variant_ops(base, deltas):
    """Apply add / remove / replace records onto an inherited variant list."""
    out = [copy.deepcopy(v) for v in base]
    idx = {v["id"]: i for i, v in enumerate(out)}
    log = []
    for d in deltas:
        op = d.get("op", "add")
        vid = d["id"]
        rec = {k: v for k, v in d.items() if k != "op"}
        if op == "remove":
            if vid in idx:
                out[idx[vid]] = None
                log.append("-%s" % vid)
            else:
                log.append("-%s (absent)" % vid)
        elif op == "replace":
            if vid in idx:
                out[idx[vid]] = rec
                log.append("~%s" % vid)
            else:
                out.append(rec)
                idx[vid] = len(out) - 1
                log.append("+%s (replace with no base)" % vid)
        else:                                   # add
            if vid in idx:
                out[idx[vid]] = rec
                log.append("~%s (add over existing)" % vid)
            else:
                out.append(rec)
                idx[vid] = len(out) - 1
                log.append("+%s" % vid)
    return [v for v in out if v is not None], log


def merge_extends(base, delta, base_src, delta_src):
    """Merge one `extends` record into a resolved base. Returns (record, provenance)."""
    out = copy.deepcopy(base)
    prov = {"restated": 0, "inherited_fields": [], "ops": []}
    out["binding"] = base.get("binding", "specified")

    bp = out.get("parameters") or {}
    dp = delta.get("parameters") or {}
    for k, v in dp.items():
        bp[k] = copy.deepcopy(v)
    if bp:
        out["parameters"] = bp
    inherited_param_keys = [k for k in bp if k not in dp]

    if delta.get("variants"):
        out["variants"], prov["ops"] = apply_variant_ops(out.get("variants") or [], delta["variants"])

    for k in MERGE_REPLACE:
        if k in delta:
            out[k] = copy.deepcopy(delta[k])
        elif k in base:
            prov["inherited_fields"].append(k)

    # rule_append (kit schema 0.2.1, docs/open-questions.md #16): the one restatement
    # case `extends` didn't cover, because `rule` is a single string and a child adding
    # a clause had to replace the whole sentence or leave the resolved rule silent about
    # its own change. Joined onto whatever `rule` this merge step resolved to (inherited,
    # or freshly replaced above if the same delta unusually set both) as an additional
    # sentence, with the join recorded in _rule_append so provenance output can show
    # which ancestor contributed which clause.
    if delta.get("rule_append"):
        base_rule = out.get("rule") or ""
        appended = delta["rule_append"]
        out["rule"] = (base_rule + " " + appended).strip() if base_rule else appended
        joins = list(out.get("_rule_append") or [])
        joins.append({"from": delta_src, "appended": appended, "joined_after": base_rule})
        out["_rule_append"] = joins
        prov["rule_appended_from"] = delta_src

    notes = list(base.get("_inherited_notes") or [])
    if base.get("note"):
        notes.append({"from": base_src, "note": base["note"]})
    out["_inherited_notes"] = notes
    if delta.get("note"):
        out["note"] = delta["note"]
    else:
        out.pop("note", None)

    # How much this delta did NOT have to say. Under 0.1.0 an override replaced the whole
    # slot, so every inherited field here is a line the author would have had to copy.
    prov["restated"] = len(inherited_param_keys) + len(prov["inherited_fields"]) + \
        max(0, len(out.get("variants") or []) - len(delta.get("variants") or []))
    prov["inherited_param_keys"] = inherited_param_keys
    out["_extends"] = {"delta_from": delta_src, "base_from": base_src, **prov}
    return out, prov


def resolve_slots(graph, chain, scope=None):
    kits = {nid: load_kit(nid) for nid in chain}
    inline = {nid: (graph["nodes"][nid].get("kit") or {}) for nid in chain}
    out = collections.OrderedDict()
    savings = {"slots": 0, "fields": 0, "detail": []}
    scope = scope or {}

    for sid, group, name in slot_order(graph):
        deltas, rec, src = [], None, None
        for nid in chain:
            # OQ 58: an ancestor reached by a scoped edge contributes only the slots that edge
            # was drawn for. Skipping it here rather than filtering its kit means the walk
            # simply continues past it to the next ancestor, which is exactly what "this edge
            # does not carry that slot" should mean.
            allowed = scope.get(nid)
            if allowed is not None and sid not in allowed:
                continue
            v, tag = None, ""
            for store, t in ((inline[nid], " (inline)"), (kits[nid], "")):
                cand = store.get(sid)
                if cand and cand.get("binding") in ("specified", "forbidden", "extends"):
                    v, tag = cand, t
                    break
            if not v:
                continue
            if v["binding"] == "extends":
                deltas.append((nid + tag, v))
                continue
            rec, src = copy.deepcopy(v), nid + tag
            break

        if rec is None:
            if deltas:
                # a dangling diff: nothing upstream to merge into. Honour it as if
                # specified, and say so loudly.
                src, rec = deltas[-1][0], copy.deepcopy(deltas[-1][1])
                rec["_dangling_extends"] = True
                deltas = deltas[:-1]
            else:
                rec = {"binding": "open", "status": "empty"}
                src = None

        chain_src = [src] if src else []
        for dsrc, d in reversed(deltas):          # farthest ancestor first
            rec, prov = merge_extends(rec, d, chain_src[-1] if chain_src else "—", dsrc)
            chain_src.append(dsrc)
            savings["slots"] += 1
            savings["fields"] += prov["restated"]
            savings["detail"].append((sid, dsrc, prov["restated"]))

        rec["_source"] = chain_src[-1] if chain_src else None
        rec["_source_chain"] = chain_src
        rec["_group"] = group
        rec["_name"] = name
        out[sid] = rec
    return out, savings


def resolve_packs(graph, chain):
    """Every pack that governs this node, nearest binder wins per pack id.

    OQ 51's REFUSAL HALF LIVES HERE (WP-8.2, 28 Aug 2026). A node may DECLINE a pack that
    reaches it only by descent, and this is the right function for it because a decline is per
    (node, pack) and this is the one function that decides pack MEMBERSHIP. `eval_packs` decides
    which RULES a member contributes -- that is what `slots`/`slots_except` are for, and those
    are per BINDING, travelling with the ancestor's record, so they change behaviour for every
    descendant and for the ancestor itself and structurally cannot express a per-descendant
    refusal. Different question, different function.

    `chain[0]` is always the node: all eight callers pass `chain_for(g, nid)`, so the fix reaches
    `--slots`, check_addresses' cascade scope, resolve_kit's own main, elevation, compose and
    three test modules with no per-caller change.
    """
    node = graph["nodes"].get(chain[0]) if chain else None
    declined = {d["pack"] for d in ((node or {}).get("declined_packs") or [])}
    # OQ 51's DELIVERY HALF, re-ruled 3 Sep 2026: a pack may declare `delivery: opt-in`, and one
    # that does reaches a node only where the node binds it or names it here. Staged per pack --
    # a pack that declares nothing behaves exactly as it always has, so this is inert until a
    # pack is flipped, and each flip is one pack's worth of stranding rather than the corpus's.
    # Read beside `declined` because they are the same question answered opposite ways and a
    # reader looking for "why does this node not have that pack" should find both here.
    opted_in = set((node or {}).get("inherits_packs") or [])
    out = collections.OrderedDict()
    for nid in chain:
        for pb in graph["nodes"][nid].get("proportion_packs", []) or []:
            pid = pb["pack"]
            # The node's OWN binding is never gated -- `nid != chain[0]` -- for the same reason
            # the decline guard carries that test: chain[0] is the node, and a node that binds a
            # pack has opted into it by binding it. Gating that would delete an authored record.
            if (nid != chain[0] and pid not in opted_in
                    and (graph.get("_packs", {}).get(pid, {}).get("delivery") == "opt-in")):
                continue
            # A node may not decline a pack it BINDS ITSELF -- that is a binding to delete, not a
            # decline to write, and check_pack_bindings errors on it. The `nid != chain[0]` guard
            # is belt and braces so a corpus that slipped past the checker still resolves
            # coherently rather than silently dropping the node's own authored binding.
            if pid in declined and nid != chain[0]:
                continue
            if pid in out:
                out[pid]["_overridden_by_ancestor"].append(nid)
                continue
            rec = dict(pb)
            rec["_source"] = nid
            rec["_overridden_by_ancestor"] = []
            out[pid] = rec
    return out


def refusals_for(graph, style_id):
    """What this node declined, and which ancestor would otherwise have delivered it.

    A separate function rather than an extra key in `resolve_packs`' mapping, deliberately:
    `check_addresses.cobinding` does `sorted(resolve_packs(...).keys())` and `eval_packs`
    iterates `packs.items()`, so a `_declined` key in that dict would become a pack id in two
    checkers.
    """
    n = graph["nodes"].get(style_id) or {}
    chain = chain_for(graph, style_id)
    out = []
    for d in (n.get("declined_packs") or []):
        deliverer = next((a for a in chain[1:]
                          if any(e["pack"] == d["pack"]
                                 for e in (graph["nodes"][a].get("proportion_packs") or []))),
                         None)
        rec = dict(d)
        rec["_would_have_come_from"] = deliverer
        out.append(rec)
    return out


# ---------------------------------------------------------------- evaluation
def pack_env(pk, ctx, module_override=None):
    if module_override is not None and pk.get("kind") == "order-system":
        mod = module_override
    else:
        mod = pk["module"].get("default_size_in") or 6.0
    env = dict(pe.DEFAULT_BINDINGS)
    env.update(ctx)
    env["module"] = mod
    env["part"] = mod / pk["module"]["parts"]
    col = pk.get("column", {})
    env["column_height"] = col.get("height_modules", 0) * mod if col.get("height_modules") else 0
    return env, mod


def _construction_vocabulary():
    """build/construction_vocabulary.py, through modcache (CLAUDE.md, OQ 28)."""
    return modcache.load("construction_vocabulary",
                         os.path.join(ROOT, "build", "construction_vocabulary.py"))


def scope_facts(slots):
    """What `proportion_engine.rule_scope()` needs, off a node's RESOLVED slots (OQ 88).

    One place, so a second reading of "is this a brick house" cannot drift from the first.

    IT NO LONGER CLASSIFIES (WP-8.4). Until 28 Aug this returned a single label --
    masonry / frame / mixed -- from `pe.construction_of()`, a SUBSTRING TEST over canonical
    `primary_cladding` ids. A substring test over a SURFACE cannot answer a question about an
    ASSEMBLY, and it disagreed with the node's own `construction_type` on 13 of 164 styles in
    both directions: `cape-dutch` is `sun-dried-brick-or-rubble-masonry` with braced timber
    frame FORBIDDEN, and its `lime-plaster-limewash-white` cladding carries no masonry word, so
    the frame-wall sill rule was delivered to a mass masonry wall -- OQ 88's own bug surviving
    inside OQ 88's fix. `prairie-school` and `storybook-style` are framed houses whose stucco
    and Roman brick surfaces read as masonry, and the frame rule was dropped from them.
    The resolved slots now travel whole and `rule_scope` resolves each token against them
    through `build/construction_vocabulary.py`, which reads `construction_type` first and maps
    to variant ids that exist.

    `elevation.py` answers the same question better at PLAN scope, from structure.py's solved
    `section["wall"]["bearing"]`, because by then there is an actual house. This is what can be
    said when all there is, is a style.
    """
    canonical = {}
    for sid, rec in (slots or {}).items():
        ids = [v["id"] for v in (rec.get("variants") or []) if v.get("status") == "canonical"]
        if ids:
            canonical[sid] = ids
    return {"resolved_slots": slots or {}, "resolved_variants": canonical}


def eval_packs(packs, ctx, module_override, kit, scope_dropped=None):
    """Every rule the bound packs contribute, keyed by target slot.

    `oq/forbidden-stops-the-pack-cascade` (WP-8.3): A PACK RULE MAY NOT WRITE TO A SLOT THE RESOLVED KIT BINDS `forbidden`.
    `docs/inheritance.md`'s binding table has always said `forbidden` means "This node prohibits
    the slot. Stops the cascade." It stopped the KIT cascade and never the PACK cascade, and 787
    (node, slot) pairs across 118 of 132 nodes carried a pack-supplied dimension for a slot the
    kit forbids -- every one of them decided by an ancestor's precedence number, and not one
    chosen by a human.

    THE REFUSED RULE IS MARKED, NOT DELETED. Dropping it would destroy the fact that a pack
    wanted to write there and was refused, which is the whole measurement; and `check_addresses`
    reads these rows without ever calling `choose_pack`, so a refusal placed only in the chooser
    would not reach it. Same discipline as `openings.py` marking an opening it cannot realise
    `unplaced` with a reason and never deleting it, and as `calibrated_for` publishing
    `out_of_calibration` rather than withholding in silence. OQ 88's own scope drop (below)
    predates that rule and is kept as a DROP because `scope_dropped` records every one -- the
    two refusals are reported by different means and neither is silent.

    `kit` IS REQUIRED AND HAS NO DEFAULT, deliberately. A `kit=None` default would let every one
    of the eight call sites keep the old behaviour by saying nothing -- which is the exact failure
    the fault schema's own note describes for a mistyped guard: "omit `expression` and the
    precondition is ignored entirely, the test runs unguarded and convicts". A caller with no kit
    passes `{}` and means it. It is also what OQ 88's scope reads: `scope_facts` is applied HERE
    rather than by every caller, because a caller who forgot it got `resolved_slots: None`, every
    scope `unknown`, and a mechanism silently inert with nothing said.
    """
    if scope_dropped is None:
        scope_dropped = []
    if kit:
        ctx = {**ctx, **scope_facts(kit)}
    by_slot = collections.defaultdict(list)
    errors = []
    # OQ 88. Callers that want to report what scope removed pass a list in; the default keeps
    # the two-value return every existing caller already unpacks.
    if scope_dropped is None:
        scope_dropped = []
    for pid, binding in packs.items():
        try:
            pk = pe.resolve(pid)
        except Exception as e:
            errors.append("%s: %s" % (pid, e))
            continue
        env, mod = pack_env(pk, ctx, module_override)
        try:
            ev = pe.evaluate(pk, mod, ctx)
        except Exception as e:
            errors.append("%s: %s" % (pid, e))
            continue
        # OQ 49: a binding may be SCOPED to named target slots. Absent means the whole pack, which
        # is the historical behaviour and stays the default. This is the one place a scoped binding
        # can be enforced -- everything downstream reads `by_slot` and cannot tell where a rule came
        # from, which is exactly how `role: optional` plus a note in prose failed to scope anything.
        # An entry is either a bare slot id (every rule the pack writes there) or `slot/dimension`
        # (exactly one rule). Both are needed: `jetty-overhang` writes material_change_rule once,
        # but `facade-portada` writes ornament_vocabulary four times and only one of them applies
        # to the node being scoped.
        scope = binding.get("slots")
        # `slots_except` is the same field turned round (WP-5.14). An allowlist cannot express
        # "everything but this one" without listing the rest by hand, and a hand-maintained
        # allowlist silently stops delivering any rule the pack gains later -- which for
        # `sash-light`'s fourteen addresses would have meant listing thirteen to refuse one.
        # Mutually exclusive with `slots`; the schema says so and check_pack_bindings enforces it.
        deny = binding.get("slots_except")

        def _named(r, names):
            return (r["target_slot"] in names
                    or "%s/%s" % (r["target_slot"], r.get("dimension")) in names)

        def _refused(sid):
            """(refused, why) for a slot the resolved kit forbids.

            THE HUMAN OVERRIDE, per `oq/forbidden-stops-the-pack-cascade`'s ruling: a slot whose own `packs` block names this
            pack is a person's explicit ruling and wins. `choose_pack`'s own docstring calls that
            block "the only place a human has said which pack wins", and it is consulted there
            first for the same reason. Zero of the 787 qualify today, so the override strands
            nothing and cannot be claimed as coverage -- it exists so a node that genuinely wants
            one dimension from an otherwise-refused member has a way to say so.
            """
            rec = (kit or {}).get(sid) or {}
            if rec.get("binding") != "forbidden":
                return False, None
            if any(x.get("pack") == pid for x in (rec.get("packs") or [])):
                return False, None
            return True, (rec.get("note") or "the resolved kit binds this slot `forbidden`")

        for r in ev["rules"]:
            if "error" in r:
                continue
            if scope is not None and not _named(r, scope):
                continue
            if deny is not None and _named(r, deny):
                continue
            # OQ 88: a rule whose own note says it is not about this construction is NOT
            # delivered. `proportion_engine.rule_scope()` decided this and wrote the reason;
            # dropping it here is the same enforcement point the two binding scopes use, for
            # the same reason -- everything downstream reads `by_slot` and cannot tell where a
            # rule came from. The drop is recorded, not silent: a rule that vanishes with no
            # trace is the failure this corpus polices, so `scope_dropped` carries every one.
            if r.get("out_of_scope"):
                scope_dropped.append({"pack": pid, "slot": r["target_slot"],
                                      "dimension": r.get("dimension"),
                                      "why": r["out_of_scope"]})
                continue
            refused, why = _refused(r["target_slot"])
            by_slot[r["target_slot"]].append({
                "refused_by_kit": refused, "refused_because": why,
                "pack": pid, "role": binding.get("role"), "from": binding["_source"],
                "style_precedence": binding.get("precedence"),
                "dimension": r.get("dimension"), "quantity": r.get("quantity"),
                "expression": r["expression"],
                "value": r.get("value"), "units": r.get("units"),
                "judgment": r.get("judgment"),
                "calibrated_for": r.get("calibrated_for"),
                # THE ENGINE'S REFUSAL, WHICH THIS REBUILD USED TO DROP. `evaluate()` sets
                # `out_of_calibration` when the environment is outside the band the rule was
                # calibrated in -- it is the engine declining to stand behind the number --
                # and a key-by-key rebuild that does not name it delivers the number with the
                # refusal stripped off. `resolve_kit.py --slot chair_rail` on `adam-style`
                # printed 1'-10 3/4" with no warning while the engine row carried
                # "ceiling_height is 108, calibrated for 142.5-168": the exact symptom this
                # file and `proportion_engine.py` both record as already fixed. 391 such rows
                # reach here across 164 nodes. `range`/`in_range` come with it, because a
                # band with no membership is what makes an unjudged rule look like a passing
                # one. Found by the WP-8.4 adversarial audit.
                "out_of_calibration": r.get("out_of_calibration"),
                "range": r.get("range"), "in_range": r.get("in_range"),
                # Present ONLY when the scope could not be decided (a both-ways style). Absent
                # means the rule is in scope, never that nobody looked.
                "scope_unjudged": r.get("scope_unjudged"),
            })
    return by_slot, errors


def choose_pack(rec, rows, ctx):
    """Resolve which bound pack governs the slot, rather than only displaying the spread.

    Order of authority:
      1. the slot's own `packs` block, lowest precedence first, skipping any marked out
         of calibration — this is the author's explicit ruling and it is the only place
         a human has said which pack wins
      2. the style node's `proportion_packs.precedence`
      3. no ruling: report the disagreement, which is what 0.1.0 could only ever do
    """
    # `oq/forbidden-stops-the-pack-cascade` (WP-8.3): a rule `eval_packs` marked `refused_by_kit` may not be chosen. The mark is
    # made there, where the kit is in hand and the row is built; the choice is refused here. One
    # judgment, two places that must agree, and they agree because only one of them decides.
    # Reported, never silently dropped: a slot whose every candidate was refused returns
    # `how: "kit.forbidden"` with the binding's own note, so a reader sees an explicit refusal
    # rather than an absence indistinguishable from "no pack writes here".
    live_rows = [r for r in (rows or []) if not r.get("refused_by_kit")]
    if rows and not live_rows:
        # EVERY BRANCH OF THIS FUNCTION RETURNS THE SAME KEYS. `rejected` and
        # `stale_calibration` are indexed unconditionally by `main()`'s --slot view and by its
        # PACK RESOLUTION summary, so a branch that omits them is a KeyError on every node the
        # branch fires for -- which for this one is 776 (node, slot) pairs across 118 of 132
        # buildable nodes, i.e. exactly the population WP-8.3 was built to name. Found by the
        # WP-8.4 adversarial audit; the branch shipped in WP-8.3 without a caller ever running.
        # `refused` and `why` are the two this branch ADDS; they are additive and safe.
        return {"how": "kit.forbidden", "chosen": None, "ranked": [],
                "rejected": [], "stale_calibration": False,
                "refused": list(rows),
                "why": next((r.get("refused_because") for r in rows if r.get("refused_because")),
                            "the resolved kit binds this slot `forbidden`")}
    rows = live_rows
    declared = rec.get("packs") or []
    if declared:
        ranked = sorted(declared, key=lambda p: (p.get("precedence") if p.get("precedence") is not None else 99))
        live = [p for p in ranked if p.get("in_calibration") is not False]
        chosen = live[0] if live else None
        stale = (abs(ctx.get("ceiling_height", AUTHORING_CEILING) - AUTHORING_CEILING) > 0.01
                 and any(p.get("in_calibration") is False for p in ranked))
        return {"how": "slot.packs", "chosen": chosen,
                "rejected": [p for p in ranked if p.get("in_calibration") is False],
                "ranked": ranked, "stale_calibration": stale}
    if rows:
        prec = [r for r in rows if r.get("style_precedence") is not None]
        if prec:
            ranked = sorted(prec, key=lambda r: r["style_precedence"])
            # OQ 48: rows at one (slot, dimension) may MEASURE DIFFERENT THINGS. Precedence decides
            # which of two accounts of ONE quantity to believe; it cannot decide between two
            # quantities, and until now the loser was discarded with nothing said. Group by
            # `quantity`, choose within the winning group, and REPORT the groups set aside -- the
            # contract is unchanged for the single-quantity case, which is most of them.
            # Grouped by (dimension, quantity), not by quantity alone: `by_slot` is keyed on the
            # SLOT, so rows for different dimensions of one slot are already in this list and were
            # being compared against each other. A `count` rule is not an alternative account of a
            # `width` rule any more than two quantities are.
            groups = collections.OrderedDict()
            for r in ranked:
                groups.setdefault((r.get("dimension"), r.get("quantity")), []).append(r)
            win_q = next(iter(groups))
            winners = groups[win_q]
            # Only a SAME-DIMENSION, different-quantity group is the corruption OQ 48 is about.
            # Different dimensions of one slot -- a count, a width, a spacing -- are a normal
            # fan-out and were never in competition; reporting those would bury the real ones.
            by_dim = collections.OrderedDict()
            for (dim, q), rs in groups.items():
                by_dim.setdefault(dim, []).append((q, rs))
            others = []
            for dim, qs in by_dim.items():
                if len(qs) < 2:
                    continue
                keep = qs[0][0]
                # Three things this must not do, all found by audit on 25 Aug 2026.
                #
                # (1) UNJUDGED IS NOT PASSED, and it is not DECIDED either. A rule with no
                #     `quantity` cannot be compared -- 268 of 751 have none -- so saying it was
                #     "set aside in favour of" something is a decision nobody made. It is reported
                #     as could-not-judge, in the schema's own words for the same case.
                # (2) "in favour of X" was false whenever this dimension is not the CHOSEN one:
                #     only one group is delivered, so at any other dimension BOTH quantities were
                #     dropped and neither prevailed. Say dropped, not set aside.
                # (3) A menu inside ONE pack is case (i), authored deliberately -- room-harmonic
                #     writes one address ten times and every one is right. Reporting those buried
                #     the cross-pack cases at a 68% false-alarm rate. Flag which kind it is.
                chosen_dim = (dim == win_q[0])
                for q, rs in qs[1:]:
                    packs_here = sorted({x["pack"] for x in rs})
                    keep_packs = sorted({x["pack"] for x in qs[0][1]})
                    cross = bool(set(packs_here) ^ set(keep_packs))
                    if q is None or keep is None:
                        verdict = ("%s: '%s' and '%s' COULD NOT BE JUDGED -- one carries no "
                                   "`quantity`, so it is unknown whether they measure the same "
                                   "thing" % (dim, q or "unstated", keep or "unstated"))
                        kind = "could-not-judge"
                    elif chosen_dim:
                        verdict = "%s: %s set aside in favour of %s" % (dim, q, keep)
                        kind = "set-aside"
                    else:
                        verdict = ("%s: %s and %s both dropped -- this slot resolved at "
                                   "dimension '%s'" % (dim, q, keep, win_q[0]))
                        kind = "both-dropped"
                    others.append({"quantity": verdict, "kind": kind,
                                   "cross_pack": cross, "packs": packs_here})
            # OQ 53: A BARE RATIO IS NOT A DIMENSION, and precedence must not deliver one as if
            # it were. Rules at one (slot, dimension, quantity) may state the same quantity in
            # different UNITS -- `casing_face_width` is written `opening_width / 6` in inches by
            # trim-classical and its peers, and `1 / 6` as a bare ratio by the order packs, whose
            # own notes carry the referent ("Of opening_width.") in PROSE, where no evaluator can
            # read it. Grouping on (dimension, quantity) alone put them in one group, so a ratio
            # could win on precedence and be written into the kit as the dimension: `craftsman`
            # and `craftsman-bungalow` resolved `casing` to 0.1667 where 6 in was meant, with
            # chambers-ionic's 1/6 beating palladio-tuscan's opening_width/6 -- two rules saying
            # exactly the same thing, one of them saying it in a form that is not a measurement.
            #
            # The fix is not to convert the ratios. Their bands are scale-free and correct as
            # ratios (0.1429-0.1667 holds at every opening width, where an inch band would only
            # hold at one), and several are genuinely DIFFERENT accounts rather than the same one
            # reworded -- palladio-ionic proportions the Ionic pedestal to the arch void, not the
            # order, and says so; chambers-ionic measures against the whole order's height. Those
            # are rival accounts, which is what precedence is for, and flattening them into
            # inches would invent a referent the source never gave.
            #
            # So: prefer a rule that yields a MEASUREMENT over one that yields a bare ratio, and
            # say so. Where only a ratio exists the slot still takes it, marked `not_a_dimension`
            # so a consumer sees a stated limitation rather than a plausible wrong number. Making
            # a ratio's referent machine-readable (a `ratio_of` field beside `units`) is the
            # standing fix for that residue and is recorded in OQ 53 rather than half-done here.
            dimensional = [w for w in winners if w.get("units") not in (None, "ratio")]
            demoted = None
            if dimensional and winners[0].get("units") == "ratio":
                demoted = {"pack": winners[0]["pack"], "expression": winners[0]["expression"],
                           "why": ("a bare ratio cannot be a dimension: its referent is stated "
                                   "only in the rule's prose note")}
                winners = dimensional + [w for w in winners if w not in dimensional]
            chosen = {"pack": winners[0]["pack"], "expression": winners[0]["expression"],
                      "quantity": win_q[1], "dimension": win_q[0],
                      "units": winners[0].get("units")}
            if demoted:
                chosen["ratio_demoted"] = demoted
            # Deliberately NOT flagged: an address where every rule is a ratio. Most such
            # quantities ARE ratios and are right in that form -- `main_roof_pitch`,
            # `opening_height_over_width`, `arch_rise_over_span`, `wall_thickness_over_span` --
            # and a first version of this flag fired 1,463 times across all 132 nodes, which is
            # a checker crying wolf rather than a finding. Only the demotion above is provable
            # from the data alone: a measurement of this very quantity was on the table and a
            # ratio was delivered instead.
            return {"how": "style.proportion_packs", "chosen": chosen,
                    "rejected": [], "ranked": ranked, "stale_calibration": False,
                    "other_quantities": others}
        if len({r["pack"] for r in rows}) > 1:
            return {"how": "unresolved", "chosen": None, "rejected": [],
                    "ranked": rows, "stale_calibration": False}
        return {"how": "single", "chosen": {"pack": rows[0]["pack"], "expression": rows[0]["expression"]},
                "rejected": [], "ranked": rows, "stale_calibration": False}
    return None


def eval_parameters(rec, ctx):
    out = {}
    for k, v in (rec.get("parameters") or {}).items():
        if not isinstance(v, dict):
            out[k] = v
            continue
        if "expr" in v:
            try:
                pk = pe.resolve(v.get("source"))
                env, _ = pack_env(pk, ctx, 5.0 if pk.get("kind") == "order-system" else None)
                val = pe.evaluate_expr(v["expr"], env)
                r = {"expr": v["expr"], "pack": v.get("source"), "value": round(val, 3),
                     "unit": v.get("unit"), "kind": v.get("kind"), "diagnostic": v.get("diagnostic")}
                ca = v.get("computed_at") or {}
                if (abs(ca.get("ceiling_height_in", -1) - ctx.get("ceiling_height", 0)) < 0.01
                        and isinstance(ca.get("value"), (int, float))
                        and abs(ca["value"] - val) > 0.01):
                    r["stored"] = ca["value"]
                out[k] = r
            except Exception as e:
                out[k] = {"expr": v.get("expr"), "pack": v.get("source"), "error": str(e)}
        else:
            for key in ("value", "range", "set"):
                if key in v:
                    out[k] = {"value": v[key], "unit": v.get("unit"), "kind": v.get("kind"),
                              "diagnostic": v.get("diagnostic"), "applies_when": v.get("applies_when")}
                    break
    return out


# ---------------------------------------------------------------- printing
def fmt_val(v, unit=None):
    if isinstance(v, float) and unit == "in":
        return pe._fmt_in(v)
    if isinstance(v, float):
        return "%.4g" % v
    return str(v)


def short(v, n):
    s = str(v)
    return s if len(s) <= n else s[: n - 1] + "…"


def in_period(variant, date):
    """Whether a variant record applies at the given year (docs/open-questions.md
    #22). A variant with no `applies_when.date_range` applies at any date, by
    the same "absence is not a restriction" reading the rest of the schema
    uses. `date=None` means no filtering is in effect -- always True, which is
    also the pre-0.2.2 behaviour every existing caller keeps by default."""
    if date is None:
        return True
    dr = (variant.get("applies_when") or {}).get("date_range")
    if not dr:
        return True
    start, end = dr
    return start <= date <= end


def filter_variants_by_date(variants, date):
    """(in_period, out_of_period) — never silently drops the excluded ones;
    callers are expected to say what got left out, not just what's left."""
    if date is None:
        return list(variants), []
    kept = [v for v in variants if in_period(v, date)]
    dropped = [v for v in variants if not in_period(v, date)]
    return kept, dropped


def variant_summary(rec, n=46, date=None):
    vs = rec.get("variants") or []
    vs, dropped = filter_variants_by_date(vs, date)
    if not vs and not dropped:
        return ""
    can = [v["id"] for v in vs if v["status"] == "canonical"]
    perm = [v["id"] for v in vs if v["status"] == "permitted"]
    forb = [v for v in vs if v["status"] == "forbidden"]
    head = ", ".join(can or perm)
    tail = "  (-%d forbidden)" % len(forb) if forb else ""
    if date is not None and dropped:
        tail += "  [%d out of period @%s]" % (len(dropped), date)
    return short(head, n - len(tail)) + tail


def main():
    ap = argparse.ArgumentParser(description="Resolve a kit of parts through the cascade")
    ap.add_argument("style")
    ap.add_argument("--ceiling", type=float, default=108.0, help="finished ceiling height, inches")
    ap.add_argument("--storey", type=float, help="storey height, inches (default: ceiling + 12)")
    ap.add_argument("--opening", type=float, default=36.0)
    ap.add_argument("--span", type=float, default=540.0)
    ap.add_argument("--module", type=float,
                    help="module for the ORDER packs, inches (5 in = a 10 in column diameter). "
                         "Module systems keep their own: a brick course is 2 3/4 in whatever the order does.")
    ap.add_argument("--group")
    ap.add_argument("--slot")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--date", type=int,
                    help="a year: narrow every slot's variant list to what applies_when.date_range "
                         "actually permits at that date, rather than presenting all of them at once "
                         "(docs/open-questions.md #22). Nothing excluded is silently dropped -- the "
                         "count and ids of what got left out are always shown.")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    graph = load_graph()
    chain = chain_for(graph, a.style)
    slots, savings = resolve_slots(graph, chain, scope_for(graph, a.style))
    packs = resolve_packs(graph, chain)
    ctx = {"ceiling_height": a.ceiling,
           "storey_height": a.storey if a.storey else a.ceiling + 12.0,
           "opening_height": 80.0, "opening_width": a.opening, "span": a.span}
    scope_dropped = []
    pack_slots, pack_errors = eval_packs(packs, ctx, a.module, slots, scope_dropped)

    if a.json:
        payload = {"style": a.style, "chain": chain, "context": ctx, "date": a.date,
                   "proportion_packs": packs, "slots": {}, "pack_derived": pack_slots,
                   "pack_errors": pack_errors, "extends_savings": savings}
        for sid, rec in slots.items():
            r = dict(rec)
            r["parameters_evaluated"] = eval_parameters(rec, ctx)
            r["pack_choice"] = choose_pack(rec, pack_slots.get(sid, []), ctx)
            if a.date is not None and rec.get("variants"):
                r["variants"] = [{**v, "in_period": in_period(v, a.date)} for v in rec["variants"]]
            payload["slots"][sid] = r
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        return

    node = graph["nodes"][a.style]
    print("\n%s  [%s]" % (node["name"], a.style))
    print("evaluated at ceiling %s, storey %s, opening %s, span %s%s%s"
          % (pe._fmt_in(ctx["ceiling_height"]), pe._fmt_in(ctx["storey_height"]),
             pe._fmt_in(ctx["opening_width"]), pe._fmt_in(ctx["span"]),
             ", order module %s" % pe._fmt_in(a.module) if a.module else "",
             ", date %s" % a.date if a.date is not None else ""))

    print("\nCASCADE  (nearest first)")
    for i, nid in enumerate(chain):
        k = load_kit(nid)
        c = collections.Counter(v.get("binding") for v in k.values())
        n = c["specified"] + c["forbidden"] + c["extends"]
        desc = ("%d bindings (%d specified, %d extends, %d forbidden)"
                % (n, c["specified"], c["extends"], c["forbidden"])) if n else "empty kit"
        print("  %s %2d  %-38s %s" % ("*" if n else " ", i, nid, desc))

    print("\nPROPORTION PACKS  (%d bound)" % len(packs))
    for pid, b in packs.items():
        ov = ("  [also bound by %s]" % ", ".join(b["_overridden_by_ancestor"])) if b["_overridden_by_ancestor"] else ""
        pr = "  prec %s" % b["precedence"] if b.get("precedence") is not None else ""
        print("  %-20s %-10s from %-28s%s%s" % (pid, b.get("role", "-"), b["_source"], pr, ov))
    for e in pack_errors:
        print("  ! %s" % e)

    if a.slot:
        rec = slots.get(a.slot)
        if not rec:
            sys.exit("no such slot: %s" % a.slot)
        params = eval_parameters(rec, ctx)
        print("\nSLOT  %s  (%s)" % (a.slot, rec["_group"]))
        print("  binding   %s%s" % (rec["binding"], " (merged via extends)" if rec.get("_extends") else ""))
        print("  source    %s" % (" <- ".join(reversed(rec["_source_chain"])) or "— unresolved, open"))
        if rec.get("_extends"):
            x = rec["_extends"]
            print("  extends   %s merged into %s; %d field(s) inherited without restatement"
                  % (x["delta_from"], x["base_from"], x["restated"]))
            if x.get("ops"):
                print("            variant ops: %s" % ", ".join(x["ops"]))
            if x.get("inherited_param_keys"):
                print("            inherited parameters: %s" % ", ".join(x["inherited_param_keys"]))
        for f in ("status", "confidence", "judgment", "invented"):
            if rec.get(f) is not None and rec.get(f) is not False:
                print("  %-9s %s" % (f, rec[f]))
        if rec.get("determined_by"):
            print("  determined_by  %s" % ", ".join(rec["determined_by"]))
        slot_variants, dropped_variants = filter_variants_by_date(rec.get("variants") or [], a.date)
        for v in slot_variants:
            aw = ("  when %s" % json.dumps(v["applies_when"])) if v.get("applies_when") else ""
            print("    [%-9s] %-42s%s" % (v["status"], v["id"], aw))
            if a.verbose and v.get("note"):
                print("                  %s" % short(v["note"], 110))
        if a.date is not None and dropped_variants:
            print("    -- %d out of period at %s: %s"
                  % (len(dropped_variants), a.date, ", ".join(v["id"] for v in dropped_variants)))
        if params:
            print("  parameters")
            for k, v in params.items():
                if not isinstance(v, dict):
                    continue
                if "expr" in v:
                    line = "    %-32s %-14s %s  [%s]" % (k, fmt_val(v.get("value"), v.get("unit")),
                                                          v["expr"], v.get("pack"))
                    if v.get("diagnostic"):
                        line += "  DIAGNOSTIC"
                    if "stored" in v:
                        line += "  DRIFT %s" % v["stored"]
                    print(line)
                else:
                    print("    %-32s %-14s %s%s" % (k, short(v.get("value"), 14), v.get("unit") or "",
                          "  when " + json.dumps(v["applies_when"]) if v.get("applies_when") else ""))
        if rec.get("rule"):
            print("  rule      %s" % rec["rule"])
            for ap in rec.get("_rule_append") or []:
                print("            (+ clause from %s: \"%s\")" % (ap["from"], short(ap["appended"], 90)))
        for cc in rec.get("code_conflict") or []:
            print("  CODE CONFLICT [%s]  period: %s" % (cc.get("severity"), cc["period_value"]))
            print("      requires: %s (%s)" % (cc["code_requirement"], cc.get("code_ref", "-")))
            print("      resolve:  %s" % cc["resolution"])
        ch = choose_pack(rec, pack_slots.get(a.slot, []), ctx)
        if ch:
            print("  PACK RESOLUTION  (%s)" % ch["how"])
            if ch["chosen"]:
                print("    governs   %-18s %s" % (ch["chosen"]["pack"], ch["chosen"].get("expression", "")))
            if ch.get("why"):
                # A refusal is a RESULT, not an absence. Printing the reason here is the whole
                # point of marking rather than deleting the row.
                print("    refused   %s" % short(ch["why"], 100))
                for r in ch.get("refused") or []:
                    print("      would have said  %-18s %-12s %s"
                          % (r["pack"], r.get("dimension") or "-", r.get("expression", "")))
            for r in ch.get("rejected") or []:
                print("    rejected  %-18s %s  — out of calibration" % (r["pack"], r.get("expression", "")))
            if ch.get("stale_calibration"):
                print("    ! the in_calibration flags were set at a 9 ft ceiling and are static; "
                      "re-check them at this context")
        rows = pack_slots.get(a.slot, [])
        if rows:
            print("  what every bound pack says about this slot")
            for r in rows:
                j = "  [judgment]" if r["judgment"] else ""
                print("    %-18s %-12s %-14s %s%s" % (r["pack"], r["dimension"] or "-",
                      fmt_val(r["value"], r["units"]), r["expression"][:42], j))
                # THE ENGINE'S REFUSAL, PRINTED WHERE THE NUMBER IS. This row used to show
                # `adam-style`'s chair rail as 1'-10 3/4" with nothing beside it while the
                # engine row said "ceiling_height is 108, calibrated for 142.5-168" -- the
                # very symptom this file's own docstring records as fixed. A number a reader
                # can copy, from a rule the engine declined to stand behind.
                if r.get("out_of_calibration"):
                    print("      ! OUT OF CALIBRATION — %s" % r["out_of_calibration"])
        if rec.get("note"):
            print("  note      %s" % rec["note"])
        for n in rec.get("_inherited_notes") or []:
            print("  inherited note (%s)  %s" % (n["from"], short(n["note"], 150)))
        return

    groups = collections.OrderedDict()
    for sid, rec in slots.items():
        groups.setdefault(rec["_group"], []).append((sid, rec))

    print("\nRESOLVED KIT")
    for gid, rows in groups.items():
        if a.group and gid != a.group:
            continue
        print("\n  %s" % gid.upper())
        print("  %-26s %-10s %-34s %s" % ("slot", "binding", "source", "variants / key parameters"))
        print("  " + "-" * 112)
        for sid, rec in rows:
            src = rec["_source"] or "—"
            if rec.get("_extends"):
                src = "%s + %s" % (rec["_extends"]["base_from"], rec["_extends"]["delta_from"])
            b = rec["binding"]
            if rec.get("_extends"):
                b = "extends"
            if b == "open":
                detail = ""
            elif rec["binding"] == "forbidden":
                detail = short(rec.get("rule") or "", 46)
            else:
                detail = variant_summary(rec, date=a.date)
                if not detail:
                    params = eval_parameters(rec, ctx)
                    keys = list(params)[:3]
                    detail = short(", ".join("%s=%s" % (k, fmt_val(params[k].get("value"), params[k].get("unit")))
                                             for k in keys), 46)
            flags = ""
            if rec.get("invented"):
                flags += " INV"
            if rec.get("code_conflict"):
                flags += " CODE"
            if rec.get("_dangling_extends"):
                flags += " DANGLING"
            if rec.get("_rule_append"):
                flags += " APPEND"
            print("  %-26s %-10s %-34s %s%s" % (sid, b, short(src, 34), detail, flags))
            if a.verbose:
                params = eval_parameters(rec, ctx)
                for k, val in params.items():
                    if isinstance(val, dict) and "expr" in val:
                        print("      %-28s %-12s %s  [%s]" % (k, fmt_val(val.get("value"), val.get("unit")),
                              val["expr"][:38], val.get("pack")))
                if rec.get("rule"):
                    print("      rule: %s" % rec["rule"])
                    for ap in rec.get("_rule_append") or []:
                        print("            (+ clause from %s)" % ap["from"])

    by_src = collections.Counter()
    for rec in slots.values():
        if rec.get("_extends"):
            by_src["%s + %s (extends)" % (rec["_extends"]["base_from"], rec["_extends"]["delta_from"])] += 1
        else:
            by_src[rec["_source"] or "— unresolved (open)"] += 1
    by_bind = collections.Counter("extends" if r.get("_extends") else r["binding"] for r in slots.values())

    print("\nPROVENANCE  (%d slots)" % len(slots))
    for src, n in by_src.most_common():
        pct = 100.0 * n / len(slots)
        print("  %-46s %3d  %5.1f%%  %s" % (src, n, pct, "█" * int(round(pct / 2.5))))
    print("\n  bindings: " + ", ".join("%s %d" % (k, v) for k, v in sorted(by_bind.items())))

    print("\nEXTENDS")
    print("  %d slot(s) merged rather than replaced" % savings["slots"])
    print("  %d inherited field(s) NOT restated — under 0.1.0 every one of these was a copy"
          % savings["fields"])
    if savings["detail"]:
        top = sorted(savings["detail"], key=lambda x: -x[2])[:8]
        print("  largest savings: " + ", ".join("%s(%d)" % (s, n) for s, _, n in top))
    dangling = [s for s, r in slots.items() if r.get("_dangling_extends")]
    if dangling:
        print("  ! DANGLING (no ancestor to merge into): %s" % ", ".join(dangling))

    covered = sorted(set(pack_slots) & set(slots))
    ruled = unruled = 0
    unruled_slots, refused_slots = [], []
    for s in covered:
        ch = choose_pack(slots[s], pack_slots[s], ctx)
        if ch and ch["how"] in ("slot.packs", "style.proportion_packs", "single"):
            ruled += 1
        elif ch and ch["how"] == "unresolved":
            unruled += 1
            unruled_slots.append(s)
        elif ch and ch["how"] == "kit.forbidden":
            # THE FOURTH STATE, AND IT HAS TO BE IN THE TOTALS. WP-8.3 added it and this loop
            # counted it as neither ruled nor unresolved, so `american-farmhouse-vernacular`
            # printed "77 of 97 slots ... 59 resolved, 0 still unresolved" and left 18 slots
            # named nowhere -- a state in no bucket, which is the one collapse this corpus
            # forbids above all others. Found by the WP-8.4 adversarial audit.
            refused_slots.append(s)
    print("\nPACK RESOLUTION  (%d of %d slots have a bound pack speaking to them)" % (len(covered), len(slots)))
    print("  %d resolved by an explicit ruling, %d still unresolved, %d REFUSED because the "
          "resolved kit forbids the slot" % (ruled, unruled, len(refused_slots)))
    if len(covered) != ruled + unruled + len(refused_slots):
        print("  ! %d slot(s) in NO bucket -- choose_pack returned a `how` this summary does "
              "not name, and a state in no bucket reads as absent"
              % (len(covered) - ruled - unruled - len(refused_slots)))
    # OQ 48: where two packs at one address MEASURE DIFFERENT THINGS, precedence picks a winner and
    # the other quantity is set aside. It used to be discarded with nothing said; now it is named,
    # because a rule that was silently dropped is unjudged and unjudged must not read as absent.
    aside, kinds = [], collections.Counter()
    for s in covered:
        ch = choose_pack(slots[s], pack_slots[s], ctx) or {}
        for o in ch.get("other_quantities") or []:
            kinds[o.get("kind", "set-aside")] += 1
            aside.append("%s (%s, from %s)" % (s, o["quantity"] or "unstated", "/".join(o["packs"])))
    if aside:
        # Broken down by kind. The single word "set aside" was applied to all three cases,
        # including the ones nobody judged -- which is the cardinal rule broken in the summary
        # line rather than in the data. `--slot <id>` shows any one of them in full.
        summary = ", ".join("%d %s" % (n, k) for k, n in kinds.most_common())
        print("  ! %d competing quantity/ies at an address (%s):" % (len(aside), summary))
        for line in aside[:8]:            # not `a`: that is the argparse Namespace
            print("      " + line)
        if len(aside) > 8:
            print("      ... and %d more" % (len(aside) - 8))
        print("      (`check_addresses.py --scope cascade --report` measures this corpus-wide)")
    if unruled_slots:
        print("  unresolved: " + ", ".join(unruled_slots))
    if refused_slots:
        print("  refused (kit binds the slot `forbidden`): " + ", ".join(refused_slots))
    stale = [s for s in covered if (choose_pack(slots[s], pack_slots[s], ctx) or {}).get("stale_calibration")]
    if stale:
        print("  ! in_calibration is static and was set at a 9 ft ceiling; re-check at this context: %s"
              % ", ".join(stale))
    inv = [s for s, r in slots.items() if r.get("invented")]
    cc = [s for s, r in slots.items() if r.get("code_conflict")]
    print("  invented slots: %s" % (", ".join(inv) or "none"))
    print("  code conflicts: %s" % (", ".join(cc) or "none"))


if __name__ == "__main__":
    main()
