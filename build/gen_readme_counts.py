#!/usr/bin/env python3
"""Regenerate the counts block that opens README.md from the data itself.

Run after any change to styles/, kits/, rooms/, faults/, proportions/,
elements/slots.json, massings/catalog.json, groupings/, partis/, or
mcp_server/server.py. Writes README.md in place, replacing the text
between the `<!-- COUNTS:START -->` and `<!-- COUNTS:END -->` markers.
If those markers are not present, prints the block instead of writing.

This exists because the review of 23 Aug 2026 found the README five
numbers stale in five different directions (82 vs 93 slots, 17 vs 23
MCP tools) even *within the same file* — one line correct, the next
wrong. A generated block cannot drift because it is not typed by hand.
"""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path):
    return json.load(open(ROOT / path))


def count_glob(pattern):
    return len(glob.glob(str(ROOT / pattern), recursive=True))


def compute_counts():
    c = {}

    slots_doc = load("elements/slots.json")
    all_slots = [s for g in slots_doc["groups"] for s in g["slots"]]
    c["slots"] = len(all_slots)
    c["slot_groups"] = len(slots_doc["groups"])
    c["ontology_version"] = slots_doc.get("version", "?")

    massings = load("massings/catalog.json")
    c["massings"] = len(massings)
    c["massings_with_expansion_logic"] = sum(
        1 for m in massings if m.get("expansion_logic")
    )

    c["rooms"] = count_glob("rooms/*.json")
    c["groupings"] = count_glob("groupings/*.json")
    c["partis"] = count_glob("partis/*.json")
    c["proportion_packs"] = count_glob("proportions/**/*.json")
    c["kits"] = count_glob("kits/*.json")
    c["faults"] = count_glob("faults/*.json")
    c["plans"] = count_glob("plans/*.json")
    c["briefs"] = count_glob("briefs/*.json")
    c["schema_files"] = count_glob("schema/*.json")

    kits_populated = 0
    for f in glob.glob(str(ROOT / "kits/*.json")):
        d = json.load(open(f))
        if any(s.get("binding") != "open" for s in d["slots"].values()):
            kits_populated += 1
    c["kits_populated"] = kits_populated
    c["kits_empty"] = c["kits"] - kits_populated

    style_docs = [json.load(open(f)) for f in glob.glob(str(ROOT / "styles/*.json"))]
    c["styles_total"] = len(style_docs)
    by_rank = {}
    for d in style_docs:
        by_rank[d.get("rank", "?")] = by_rank.get(d.get("rank", "?"), 0) + 1
    c["styles_by_rank"] = by_rank
    c["lineage_edges"] = sum(len(d.get("lineage", [])) for d in style_docs)
    all_constraints = [c2 for d in style_docs for c2 in d.get("constraints", [])]
    c["constraints_total"] = len(all_constraints)
    c["constraints_hard"] = sum(1 for x in all_constraints if x.get("severity") == "hard")
    c["constraints_soft"] = sum(1 for x in all_constraints if x.get("severity") == "soft")
    c["constraints_advisory"] = sum(1 for x in all_constraints if x.get("severity") == "advisory")
    c["exemplars"] = sum(len(d.get("exemplars", [])) for d in style_docs)
    c["massing_affinities"] = sum(len(d.get("massing_affinities", [])) for d in style_docs)
    c["styles_with_pack_bindings"] = sum(1 for d in style_docs if d.get("proportion_packs"))

    faults_docs = [json.load(open(f)) for f in glob.glob(str(ROOT / "faults/*.json"))]
    c["fault_exceptions"] = sum(len(d.get("exceptions", [])) for d in faults_docs)
    c["fault_exceptions_numeric"] = sum(
        1 for d in faults_docs for e in d.get("exceptions", []) if e.get("bounds_test")
    )

    rooms_docs = [json.load(open(f)) for f in glob.glob(str(ROOT / "rooms/*.json"))]
    c["room_style_variation_entries"] = sum(len(d.get("style_variation", [])) for d in rooms_docs)

    manifest = load("assets/manifest.json")
    c["image_records"] = manifest["counts"]["total"]
    c["image_pairs"] = manifest["counts"].get("pairs", "?")

    server_src = (ROOT / "mcp_server/server.py").read_text()
    c["mcp_tools"] = len(re.findall(r"@mcp\.tool\(\)", server_src))

    partis_docs = [json.load(open(f)) for f in glob.glob(str(ROOT / "partis/*.json"))]
    native_styles = set()
    for d in partis_docs:
        native_styles.update(d.get("styles", []))
    c["parti_native_styles"] = len(native_styles)

    return c


def render_block(c):
    return (
        f"**{c['styles_total']} taxa · {c['lineage_edges']} lineage edges · "
        f"{c['slots']} element slots · {c['massings']} massings · {c['rooms']} rooms · "
        f"{c['groupings']} groupings · {c['proportion_packs']} executable proportion packs · "
        f"{c['faults']} named faults · {c['image_records']} specified images · "
        f"{c['partis']} partis · {c['mcp_tools']} MCP tools**\n\n"
        f"**700 BC – AD 2026**"
    )


def main():
    c = compute_counts()
    block = render_block(c)
    readme = ROOT / "README.md"
    text = readme.read_text()
    start, end = "<!-- COUNTS:START -->", "<!-- COUNTS:END -->"
    if start in text and end in text:
        pre = text.split(start)[0]
        post = text.split(end)[1]
        new_text = pre + start + "\n" + block + "\n" + end + post
        readme.write_text(new_text)
        print(f"README.md counts block regenerated ({len(c)} figures computed).")
    else:
        print("No COUNTS markers found in README.md — printing block instead:\n")
        print(block)

    if "--verbose" in sys.argv:
        print()
        for k, v in c.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
