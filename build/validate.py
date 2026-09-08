#!/usr/bin/env python3
"""Validate the style graph: schema conformance, referential integrity, acyclicity, date coherence."""
import json, os, sys, glob
try:
    import jsonschema
except ImportError:
    import sys as _sys
    print("SKIPPED — jsonschema is not installed, so nothing here was checked.")
    print("    pip install jsonschema")
    # Exit 3, the convention build/check_all.py reads as "could not evaluate". Exiting 1
    # would report a missing dependency as a failed data check, which is the collapse
    # this corpus forbids everywhere else.
    _sys.exit(3)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import schema_validators                                                   # noqa: E402
# Compiled once for all 164 nodes rather than rebuilt per node: 5.95 s -> 0.19 s.
sch_validator = schema_validators.compiled(f"{ROOT}/schema/style-node.schema.json")
massings = {m["id"] for m in json.load(open(f"{ROOT}/massings/catalog.json"))}
slots = set()
slot_records = {}
for g in json.load(open(f"{ROOT}/elements/slots.json"))["groups"]:
    for s in g["slots"]:
        slots.add(s["id"])
        slot_records[s["id"]] = s

nodes, errs, warns = {}, [], []

# derives_from_module referential integrity (docs/open-questions.md #13): every
# reference must point at a real slot, and not at itself.
for sid, s in slot_records.items():
    dfm = s.get("derives_from_module")
    if dfm is None:
        continue
    if dfm not in slots:
        errs.append(f"slot {sid}: derives_from_module '{dfm}' does not exist")
    elif dfm == sid:
        errs.append(f"slot {sid}: derives_from_module cannot reference itself")
files = sorted(glob.glob(f"{ROOT}/styles/*.json"))
for f in files:
    base = os.path.basename(f)[:-5]
    try:
        n = json.load(open(f))
    except Exception as e:
        errs.append(f"{base}: UNPARSEABLE JSON: {e}"); continue
    try:
        schema_validators.raise_first(sch_validator, n)
    except jsonschema.ValidationError as e:
        errs.append(f"{base}: SCHEMA {'/'.join(str(p) for p in e.absolute_path)}: {e.message}"); continue
    if n["id"] != base: errs.append(f"{base}: id '{n['id']}' does not match filename")
    if n["id"] in nodes: errs.append(f"{base}: duplicate id")
    nodes[n["id"]] = n

RANK_ORDER = {"tradition":0,"family":1,"style":2,"variant":3}
for i, n in nodes.items():
    mo = n.get("member_of")
    if n["rank"] == "tradition":
        if mo: errs.append(f"{i}: tradition must have member_of null")
    else:
        if not mo: errs.append(f"{i}: rank {n['rank']} requires member_of")
        elif mo not in nodes: errs.append(f"{i}: member_of '{mo}' does not exist")
        elif RANK_ORDER[nodes[mo]["rank"]] >= RANK_ORDER[n["rank"]]:
            errs.append(f"{i}: member_of '{mo}' rank {nodes[mo]['rank']} not above {n['rank']}")
    for e in n.get("lineage", []):
        if e["target"] not in nodes: errs.append(f"{i}: lineage target '{e['target']}' does not exist")
        if e["target"] == i: errs.append(f"{i}: self-referential lineage edge")
    if n["rank"] == "variant":
        if not any(e["type"] == "regional_of" for e in n.get("lineage", [])):
            warns.append(f"{i}: variant has no regional_of edge")
    p = n["period"]
    if p["floruit_start"] > p["floruit_end"]: errs.append(f"{i}: floruit_start > floruit_end")
    if p.get("origin") and p["origin"] > p["floruit_start"]: warns.append(f"{i}: origin after floruit_start")
    for df in n.get("distinguished_from", []):
        t = df["node"]
        if t.startswith("massing:"):
            if t[8:] not in massings: errs.append(f"{i}: distinguished_from unknown massing '{t}'")
        elif t not in nodes:
            errs.append(f"{i}: distinguished_from target '{t}' does not exist")
    for e in n.get("lineage", []):
        ik = e.get("inherits_kit", False)
        if e["type"] in ("descends_from","regional_of") and not ik:
            errs.append(f"{i}: {e['type']} -> {e['target']} must set inherits_kit true (it is transmission)")
        if e["type"] in ("references","reacts_against","revives") and ik:
            errs.append(f"{i}: {e['type']} -> {e['target']} must not set inherits_kit (it is not transmission)")
        if ik and e["target"] in nodes and nodes[e["target"]]["rank"] not in ("style","variant"):
            errs.append(f"{i}: inheritance edge -> '{e['target']}' targets rank {nodes[e['target']]['rank']}; only style/variant carry kits")
    for ma in n.get("massing_affinities", []):
        if ma["massing"] not in massings: errs.append(f"{i}: unknown massing '{ma['massing']}'")
    for k in n.get("kit", {}):
        if k not in slots: errs.append(f"{i}: unknown kit slot '{k}'")

# membership tree acyclicity
for i in nodes:
    seen, cur = set(), i
    while cur:
        if cur in seen: errs.append(f"{i}: member_of cycle"); break
        if cur not in nodes: break
        seen.add(cur); cur = nodes[cur].get("member_of")

# lineage DAG acyclicity (inheritance edges only)
INHERIT = {"descends_from","regional_of","hybridizes_with","revives"}
color = {}
def dfs(u, stack):
    color[u] = 1
    for e in nodes[u].get("lineage", []):
        v = e["target"]
        if e["type"] not in INHERIT or v not in nodes: continue
        if color.get(v) == 1: errs.append("LINEAGE CYCLE: " + " -> ".join(stack + [u, v]))
        elif color.get(v, 0) == 0: dfs(v, stack + [u])
    color[u] = 2
for i in nodes:
    if color.get(i, 0) == 0: dfs(i, [])

# chronology: a node should not predate an ancestor it descends from
for i, n in nodes.items():
    for e in n.get("lineage", []):
        if e["type"] in ("descends_from","regional_of") and e["target"] in nodes:
            if n["period"]["floruit_start"] < nodes[e["target"]]["period"]["floruit_start"] - 25:
                warns.append(f"{i} ({n['period']['floruit_start']}) starts well before ancestor {e['target']} ({nodes[e['target']]['period']['floruit_start']})")

print(f"nodes: {len(nodes)}  files: {len(files)}")
by_rank = {}
for n in nodes.values(): by_rank[n["rank"]] = by_rank.get(n["rank"], 0) + 1
print("by rank:", by_rank)
if warns:
    print(f"\n{len(warns)} WARNINGS"); [print("  ! " + w) for w in warns[:60]]
if errs:
    print(f"\n{len(errs)} ERRORS"); [print("  x " + e) for e in errs[:80]]; sys.exit(1)
print("\nOK — schema valid, references resolve, no cycles.")
