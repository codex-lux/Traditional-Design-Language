#!/usr/bin/env python3
"""Build the Traditional Design Language artifacts.

Outputs
  kits/<id>.kit.json     one per style/variant: the 82-slot directory, ready to populate
  dist/taxonomy.json     the whole graph in one file, for platform/agent ingestion
  dist/taxonomy.agent.md a compact context-window digest, one block per node
  dist/taxonomy.html     the interactive phylogeny
"""
import json, os, glob, html, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

nodes = {}
for f in glob.glob("styles/*.json"):
    n = json.load(open(f)); nodes[n["id"]] = n
slots_doc = json.load(open("elements/slots.json"))
KIT_VERSION = json.load(open("schema/kit.schema.json")).get("version", "0.2.1")
massings = {m["id"]: m for m in json.load(open("massings/catalog.json"))}

SLOTS = []
for g in slots_doc["groups"]:
    for s in g["slots"]:
        SLOTS.append({**s, "group": g["id"], "group_name": g["name"]})

# ---------- 1. kit directories ----------
# WP-4.2: family nodes (rank "family") now get a kit file too, same 95-slot skeleton as
# every style/variant. A family kit is not part of the lineage DAG (families carry no
# lineage edges at all -- they are member_of's organisational drawer, not descent) but it
# does participate in the cascade below as each member's nearest, most-shared ancestor.
made = 0
for i, n in nodes.items():
    if n["rank"] not in ("style", "variant", "family"):
        continue
    path = f"kits/{i}.kit.json"
    existing = json.load(open(path))["slots"] if os.path.exists(path) else {}
    # Kit schema 0.2.0: an empty slot carries no `rule` key at all. In 0.1.0 the template
    # wrote "rule": null, which the 0.2.0 schema rejects because rule is typed string —
    # so every one of the untouched kits had to be regenerated rather than hand-patched.
    kit = {"style": i, "style_name": n["name"],
           "ontology_version": slots_doc["version"], "kit_version": KIT_VERSION, "slots": {}}
    for s in SLOTS:
        prev = existing.get(s["id"])
        if prev is not None:
            prev = {k: v for k, v in prev.items() if not (k == "rule" and v is None)}
            prev["group"] = s["group"]
            kit["slots"][s["id"]] = prev
        else:
            kit["slots"][s["id"]] = {"group": s["group"], "binding": "open", "status": "empty"}
    json.dump(kit, open(path, "w"), indent=2, ensure_ascii=False); made += 1

# ---------- 2. cascade ----------
def cascade_chain(i, seen):
    """i's real-descent ancestors, nearest first, walking `lineage` edges with
    inherits_kit: true. Whenever the walk lands on a style-rank ancestor, that ancestor's
    OWN family (WP-4.2, see family_of() below) is spliced in immediately after it and
    before that ancestor's own further lineage ancestors — nearest and most-shared first,
    most distant and most specific descent last. `seen` is shared across the whole
    recursion so a family reached through one branch is not revisited through another."""
    out = []
    for e in sorted(nodes[i].get("lineage", []), key=lambda e: -e.get("weight", 1)):
        if not e.get("inherits_kit"): continue
        t = e["target"]
        if t in seen or t not in nodes: continue
        seen.add(t); out.append(t)
        if nodes[t]["rank"] == "style":
            fam = family_of(t)
            if fam and fam not in seen:
                seen.add(fam); out.append(fam)
        out.extend(cascade_chain(t, seen))
    return out

def family_of(i):
    """WP-4.2: nearest ancestor of rank 'family' reached by walking `member_of`
    (organisational placement, not lineage/descent) up from i. A variant's member_of is
    its parent style, not its family directly, so this walks through that style without
    adding it (the style itself is reached separately, via real lineage descent, if at
    all). Returns None for a family or tradition node itself, or an orphaned node."""
    cur = nodes[i].get("member_of")
    seen = {i}
    while cur and cur in nodes and cur not in seen:
        seen.add(cur)
        if nodes[cur]["rank"] == "family":
            return cur
        cur = nodes[cur].get("member_of")
    return None

for i, n in nodes.items():
    seen = {i}
    out = []
    if n["rank"] == "style":
        # i's own family comes before i's own lineage ancestors -- the nearest, most-
        # shared base a style extends against, per PLAN-OF-ACTION.md's WP-4.2.
        fam = family_of(i)
        if fam:
            seen.add(fam); out.append(fam)
    out.extend(cascade_chain(i, seen))
    n["_cascade"] = out
    n["_children"] = []
    n["_descendants"] = []
for i, n in nodes.items():
    if n.get("member_of"): nodes[n["member_of"]]["_children"].append(i)
    for e in n.get("lineage", []):
        if e["target"] in nodes: nodes[e["target"]]["_descendants"].append({"id": i, "type": e["type"]})

# ---------- 3. taxonomy.json ----------
bundle = {
  "$schema": "schema/style-node.schema.json",
  "version": "0.1.0",
  "generated_from": "styles/*.json + elements/slots.json + massings/catalog.json",
  "counts": {"nodes": len(nodes),
             "by_rank": {r: sum(1 for n in nodes.values() if n["rank"] == r)
                         for r in ("tradition","family","style","variant")},
             "slots": len(SLOTS), "massings": len(massings)},
  "edge_semantics": {
    "descends_from": "actual transmission of building practice; carries the kit cascade",
    "references": "claimed or quoted ancestry imitated without descent; does NOT carry the cascade",
    "reacts_against": "defined by inversion of a predecessor",
    "hybridizes_with": "reticulation; a co-parent of comparable weight",
    "regional_of": "variant to its parent style; carries the cascade",
    "revives": "deliberate resurrection after a gap"
  },
  "slots": SLOTS, "massings": list(massings.values()), "nodes": nodes
}
json.dump(bundle, open("dist/taxonomy.json","w"), indent=2, ensure_ascii=False)

# ---------- 4. agent digest ----------
def yr(v):
    if v is None: return "?"
    return f"{-v} BC" if v < 0 else str(v)
lines = ["# Traditional Design Language — taxonomy digest",
         "",
         f"{len(nodes)} nodes. Ranks: tradition > family > style > variant. `member_of` is the browsing container; `lineage` is the real graph.",
         "Edge types: descends_from (real transmission), references (claimed ancestry, no descent), reacts_against, hybridizes_with, regional_of, revives.",
         "Select a node id to enter its kit-of-parts directory at kits/<id>.kit.json.", ""]
order = sorted(nodes.values(), key=lambda n: (n["period"]["floruit_start"], n["id"]))
for n in order:
    p = n["period"]
    lin = "; ".join(f"{e['type']} {e['target']}" for e in n.get("lineage", [])) or "—"
    lines.append(f"## {n['id']}  [{n['rank']}]")
    lines.append(f"**{n['name']}** · {yr(p['floruit_start'])}–{yr(p['floruit_end'])} · {', '.join(n['geography']['regions'][:3])} · in: {n.get('member_of') or 'root'}")
    lines.append(f"{n['description']['short']}")
    lines.append(f"- lineage: {lin}")
    if n.get("diagnostic_tells"):
        lines.append(f"- tells: {' | '.join(n['diagnostic_tells'][:4])}")
    if n.get("massing_affinities"):
        can = [m["massing"] for m in n["massing_affinities"] if m["affinity"] in ("canonical","common")]
        if can: lines.append(f"- massings: {', '.join(can)}")
    lines.append("")
open("dist/taxonomy.agent.md","w").write("\n".join(lines))

print(f"kits written: {made}  (ontology {slots_doc['version']}, kit schema {KIT_VERSION}, {len(SLOTS)} slots)")
print(f"dist/taxonomy.json  {os.path.getsize('dist/taxonomy.json')/1e6:.2f} MB")
print(f"dist/taxonomy.agent.md {os.path.getsize('dist/taxonomy.agent.md')/1e3:.0f} KB")
