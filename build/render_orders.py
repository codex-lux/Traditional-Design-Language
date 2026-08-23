#!/usr/bin/env python3
"""Emit dist/orders.html — the live order-drawing tool, rendered from the engine itself."""
import json, os, sys, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
spec = importlib.util.spec_from_file_location("pe", "build/proportion_engine.py")
pe = importlib.util.module_from_spec(spec); spec.loader.exec_module(pe)

ORDERS = ["tuscan", "doric", "ionic", "corinthian", "composite"]
AUTHORITIES = [
    ("vignola",  "Vignola",  1562, "Regola delli cinque ordini"),
    ("palladio", "Palladio", 1570, "I Quattro Libri"),
    ("gibbs",    "Gibbs",    1732, "Rules for Drawing"),
    ("chambers", "Chambers", 1759, "A Treatise on Civil Architecture"),
    ("benjamin", "Benjamin", 1806, "The American Builder's Companion"),
]

packs = {}
for auth, _, _, _ in AUTHORITIES:
    for o in ORDERS:
        pid = f"{auth}-{o}"
        if pid in pe.PACKS:
            r = pe.resolve(pid)
            packs[pid] = {
                "id": r["id"], "name": r["name"], "order": o, "authority": auth,
                "module": r["module"], "column": r.get("column", {}),
                "assemblies": r.get("assemblies", {}),
                "invariants": pe.check_invariants(r),
                "derived_rules": r.get("derived_rules", []),
                "conflicts": r.get("conflicts", []),
                "intercolumniation": r.get("intercolumniation", {}),
                "authority_meta": r.get("authority", {}),
                "resolved_from": r.get("_resolved_from", [r["id"]]),
                "overlay_notes": r.get("_overlay_notes", []),
                "notes": r.get("notes", ""),
                "applies_to": r.get("applies_to", []),
                "confidence": r.get("confidence", "medium"),
                "diameters": pe.diameters_per_module(r),
            }

systems = {}
for pid, p in pe.PACKS.items():
    if p["kind"] in ("trim-system", "opening-system", "room-system", "facade-system", "module-system"):
        r = pe.resolve(pid)
        systems[pid] = {"id": r["id"], "name": r["name"], "kind": r["kind"],
                        "module": r["module"], "assemblies": r.get("assemblies", {}),
                        "derived_rules": r.get("derived_rules", []),
                        "conflicts": r.get("conflicts", []),
                        "authority_meta": r.get("authority", {}),
                        "applies_to": r.get("applies_to", []),
                        "diameters": pe.diameters_per_module(r)}

style_names = {}
import glob
for f in glob.glob("styles/*.json"):
    n = json.load(open(f)); style_names[n["id"]] = n["name"]

DATA = {"packs": packs, "systems": systems, "orders": ORDERS,
        "authorities": [{"id": a, "name": n, "year": y, "work": w} for a, n, y, w in AUTHORITIES],
        "styles": style_names, "engine_version": pe.ENGINE_VERSION}

tpl = open("build/orders_template.html").read()
open("dist/orders.html", "w").write(tpl.replace("/*__DATA__*/null", json.dumps(DATA, separators=(",", ":"), ensure_ascii=False)))
print(f"order packs: {len(packs)}  system packs: {len(systems)}  size {os.path.getsize('dist/orders.html')/1e6:.2f} MB")
