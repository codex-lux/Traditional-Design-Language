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
"""
import json, os, sys, argparse, collections, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import proportion_engine as pe

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


def resolve_slots(graph, chain):
    kits = {nid: load_kit(nid) for nid in chain}
    inline = {nid: (graph["nodes"][nid].get("kit") or {}) for nid in chain}
    out = collections.OrderedDict()
    savings = {"slots": 0, "fields": 0, "detail": []}

    for sid, group, name in slot_order(graph):
        deltas, rec, src = [], None, None
        for nid in chain:
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
    out = collections.OrderedDict()
    for nid in chain:
        for pb in graph["nodes"][nid].get("proportion_packs", []) or []:
            pid = pb["pack"]
            if pid in out:
                out[pid]["_overridden_by_ancestor"].append(nid)
                continue
            rec = dict(pb)
            rec["_source"] = nid
            rec["_overridden_by_ancestor"] = []
            out[pid] = rec
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


def eval_packs(packs, ctx, module_override=None):
    by_slot = collections.defaultdict(list)
    errors = []
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
        for r in ev["rules"]:
            if "error" in r:
                continue
            by_slot[r["target_slot"]].append({
                "pack": pid, "role": binding.get("role"), "from": binding["_source"],
                "style_precedence": binding.get("precedence"),
                "dimension": r.get("dimension"), "expression": r["expression"],
                "value": r.get("value"), "units": r.get("units"),
                "judgment": r.get("judgment"),
                "calibrated_for": r.get("calibrated_for"),
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
            return {"how": "style.proportion_packs", "chosen": {"pack": ranked[0]["pack"],
                    "expression": ranked[0]["expression"]}, "rejected": [], "ranked": ranked,
                    "stale_calibration": False}
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


def variant_summary(rec, n=46):
    vs = rec.get("variants") or []
    if not vs:
        return ""
    can = [v["id"] for v in vs if v["status"] == "canonical"]
    perm = [v["id"] for v in vs if v["status"] == "permitted"]
    forb = [v for v in vs if v["status"] == "forbidden"]
    head = ", ".join(can or perm)
    tail = "  (-%d forbidden)" % len(forb) if forb else ""
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
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    graph = load_graph()
    chain = chain_for(graph, a.style)
    slots, savings = resolve_slots(graph, chain)
    packs = resolve_packs(graph, chain)
    ctx = {"ceiling_height": a.ceiling,
           "storey_height": a.storey if a.storey else a.ceiling + 12.0,
           "opening_height": 80.0, "opening_width": a.opening, "span": a.span}
    pack_slots, pack_errors = eval_packs(packs, ctx, a.module)

    if a.json:
        payload = {"style": a.style, "chain": chain, "context": ctx,
                   "proportion_packs": packs, "slots": {}, "pack_derived": pack_slots,
                   "pack_errors": pack_errors, "extends_savings": savings}
        for sid, rec in slots.items():
            r = dict(rec)
            r["parameters_evaluated"] = eval_parameters(rec, ctx)
            r["pack_choice"] = choose_pack(rec, pack_slots.get(sid, []), ctx)
            payload["slots"][sid] = r
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        return

    node = graph["nodes"][a.style]
    print("\n%s  [%s]" % (node["name"], a.style))
    print("evaluated at ceiling %s, storey %s, opening %s, span %s%s"
          % (pe._fmt_in(ctx["ceiling_height"]), pe._fmt_in(ctx["storey_height"]),
             pe._fmt_in(ctx["opening_width"]), pe._fmt_in(ctx["span"]),
             ", order module %s" % pe._fmt_in(a.module) if a.module else ""))

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
        for v in rec.get("variants") or []:
            aw = ("  when %s" % json.dumps(v["applies_when"])) if v.get("applies_when") else ""
            print("    [%-9s] %-42s%s" % (v["status"], v["id"], aw))
            if a.verbose and v.get("note"):
                print("                  %s" % short(v["note"], 110))
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
        for cc in rec.get("code_conflict") or []:
            print("  CODE CONFLICT [%s]  period: %s" % (cc.get("severity"), cc["period_value"]))
            print("      requires: %s (%s)" % (cc["code_requirement"], cc.get("code_ref", "-")))
            print("      resolve:  %s" % cc["resolution"])
        ch = choose_pack(rec, pack_slots.get(a.slot, []), ctx)
        if ch:
            print("  PACK RESOLUTION  (%s)" % ch["how"])
            if ch["chosen"]:
                print("    governs   %-18s %s" % (ch["chosen"]["pack"], ch["chosen"].get("expression", "")))
            for r in ch["rejected"]:
                print("    rejected  %-18s %s  — out of calibration" % (r["pack"], r.get("expression", "")))
            if ch["stale_calibration"]:
                print("    ! the in_calibration flags were set at a 9 ft ceiling and are static; "
                      "re-check them at this context")
        rows = pack_slots.get(a.slot, [])
        if rows:
            print("  what every bound pack says about this slot")
            for r in rows:
                j = "  [judgment]" if r["judgment"] else ""
                print("    %-18s %-12s %-14s %s%s" % (r["pack"], r["dimension"] or "-",
                      fmt_val(r["value"], r["units"]), r["expression"][:42], j))
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
                detail = variant_summary(rec)
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
            print("  %-26s %-10s %-34s %s%s" % (sid, b, short(src, 34), detail, flags))
            if a.verbose:
                params = eval_parameters(rec, ctx)
                for k, val in params.items():
                    if isinstance(val, dict) and "expr" in val:
                        print("      %-28s %-12s %s  [%s]" % (k, fmt_val(val.get("value"), val.get("unit")),
                              val["expr"][:38], val.get("pack")))
                if rec.get("rule"):
                    print("      rule: %s" % rec["rule"])

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
    unruled_slots = []
    for s in covered:
        ch = choose_pack(slots[s], pack_slots[s], ctx)
        if ch and ch["how"] in ("slot.packs", "style.proportion_packs", "single"):
            ruled += 1
        elif ch and ch["how"] == "unresolved":
            unruled += 1
            unruled_slots.append(s)
    print("\nPACK RESOLUTION  (%d of %d slots have a bound pack speaking to them)" % (len(covered), len(slots)))
    print("  %d resolved by an explicit ruling, %d still unresolved" % (ruled, unruled))
    if unruled_slots:
        print("  unresolved: " + ", ".join(unruled_slots))
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
