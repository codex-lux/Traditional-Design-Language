#!/usr/bin/env python3
"""Emit dist/orders.html — the live order-drawing tool, rendered from the engine itself."""
import json, os, sys, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
spec = importlib.util.spec_from_file_location("pe", "build/proportion_engine.py")
pe = importlib.util.module_from_spec(spec); spec.loader.exec_module(pe)
_ps = importlib.util.spec_from_file_location("profiles", "build/profiles.py")
prof = importlib.util.module_from_spec(_ps); _ps.loader.exec_module(prof)

GEOM_MODULE_IN = 36.0        # the reference size; every consumer scales from it

def geometry_variants(r):
    """The pack's profile geometry, constructed ONCE here so the browser never constructs a
    moulding for itself (see build/profiles.py::pack_geometry for why that matters). Two
    variants because dropping the pedestal moves every y above it -- a stack without its
    pedestal is a different stack, not a crop. Everything is linear in the module, so the page
    scales these rather than rebuilding them."""
    full = pe.stack_for(r)
    out = {}
    for key, asms in (("with_pedestal", full),
                      ("no_pedestal", [a for a in full if a not in ("pedestal", "subplinth")])):
        d = pe.dimension(r, GEOM_MODULE_IN, include=asms)
        out[key] = prof.pack_geometry(d, r.get("column"), r.get("projection_datum"))
        out[key]["stack_height_in"] = d["totals"]["stack_height_in"]
    return out

ORDERS = ["tuscan", "doric", "ionic", "corinthian", "composite"]
AUTHORITIES = [
    ("vignola",  "Vignola",  1562, "Regola delli cinque ordini"),
    ("palladio", "Palladio", 1570, "I Quattro Libri"),
    ("gibbs",    "Gibbs",    1732, "Rules for Drawing"),
    ("chambers", "Chambers", 1759, "A Treatise on Civil Architecture"),
    ("benjamin", "Benjamin", 1806, "The American Builder's Companion"),
]

# EVERY ORDER PACK, not the authority x order cross-product. That grid takes 24 of the 26 and
# says nothing about the other two: `greek-doric` (bound to greek-revival-american, regency and
# three more) and `moorish-arch` (bound to eight nodes) belong to no <authority>-<order> pair,
# and the `systems` loop below filters on kinds that exclude `order-system`, so both fell
# through BOTH loops. dist/orders.html served 55 of 57 packs and nothing said so. The grid is
# still used for the authority table's ORDERING; membership is now the corpus's own.
_grid = [f"{auth}-{o}" for auth, _, _, _ in AUTHORITIES for o in ORDERS]
ORDER_PACK_IDS = [pid for pid in _grid if pid in pe.PACKS] + \
    sorted(pid for pid, p in pe.PACKS.items()
           if p.get("kind") == "order-system" and pid not in _grid)

packs = {}
for pid in ORDER_PACK_IDS:
        if True:
            o = next((x for x in ORDERS if pid.endswith("-" + x)), pe.PACKS[pid].get("order") or "other")
            auth = pid.rsplit("-", 1)[0] if any(pid.endswith("-" + x) for x in ORDERS) else pid
            r = pe.resolve(pid)
            packs[pid] = {
                "id": r["id"], "name": r["name"], "order": o, "authority": auth,
                "module": r["module"], "column": r.get("column", {}),
                # OQ 65: which datum this pack's projections were measured from, stated
                # by the pack and inherited through the overlay chain by resolve()
                "projection_datum": r.get("projection_datum"),
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
                "geometry": geometry_variants(r),
                "geometry_module_in": GEOM_MODULE_IN,
            }

systems = {}
for pid, p in pe.PACKS.items():
    if p["kind"] in ("trim-system", "opening-system", "room-system", "facade-system", "module-system"):
        r = pe.resolve(pid)
        systems[pid] = {"id": r["id"], "name": r["name"], "kind": r["kind"],
                        "projection_datum": r.get("projection_datum"),
                        "module": r["module"], "assemblies": r.get("assemblies", {}),
                        "derived_rules": r.get("derived_rules", []),
                        "conflicts": r.get("conflicts", []),
                        "authority_meta": r.get("authority", {}),
                        "applies_to": r.get("applies_to", []),
                        "diameters": pe.diameters_per_module(r)}

style_names = {}
import glob
for f in sorted(glob.glob("styles/*.json")):
    n = json.load(open(f)); style_names[n["id"]] = n["name"]

DATA = {"packs": packs, "systems": systems, "orders": ORDERS,
        "authorities": [{"id": a, "name": n, "year": y, "work": w} for a, n, y, w in AUTHORITIES],
        "styles": style_names, "engine_version": pe.ENGINE_VERSION}

tpl = open("build/orders_template.html").read()
open("dist/orders.html", "w").write(tpl.replace("/*__DATA__*/null", json.dumps(DATA, separators=(",", ":"), ensure_ascii=False)))
print(f"order packs: {len(packs)}  system packs: {len(systems)}  size {os.path.getsize('dist/orders.html')/1e6:.2f} MB")
