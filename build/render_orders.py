#!/usr/bin/env python3
"""Emit dist/orders.html — the live order-drawing tool, rendered from the engine itself.

    python3 build/render_orders.py            # write dist/orders.html
    python3 build/render_orders.py --check    # exit 1 if the committed page is not this output

`build_page()` RETURNS the page and writes nothing, so a check can hold the committed file to it
without touching the tree (WP-14.1). Until then this script computed everything at import time and
wrote as a side effect, nothing ran it, and the committed page carried three system packs that had
since moved -- `balcony-gallery`, `facade-gable` and `storey-graduation` -- with no check able to say
so. `build/build.py` now regenerates it on every build, as it does `dist/taxonomy.html`, and
`tests/svg_census.py` holds the committed page to `build_page()`.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

pe = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
prof = modcache.load("profiles", os.path.join(ROOT, "build", "profiles.py"))

OUT = os.path.join(ROOT, "dist", "orders.html")
TEMPLATE = os.path.join(ROOT, "build", "orders_template.html")
GEOM_MODULE_IN = 36.0        # the reference size; every consumer scales from it


# What a member IS, once per pack: the page's tooltip and info panel print these, and they do not
# move with the pedestal. Where a member STANDS moves, so that is served per variant below.
PAGE_MEMBER_KEYS = ("name", "profile", "height_parts", "projection_parts", "count", "enrichment",
                    "confidence", "note")


def stack_variants(r):
    """Per pedestal variant, what the page DRAWS and what it PRINTS, both from Python, at
    GEOM_MODULE_IN: the dimensions proportion_engine.dimension() gives and the paths
    build/profiles.py::pack_geometry() constructs. The page scales both by one ratio and computes
    neither (WP-14.2).

    Until WP-14.2 the page carried its own port of `stack_for`, `_synth_shaft` and `dimension()` --
    the dimensioning arithmetic a second time, in a second language. It agreed with Python on every
    case measured (26 packs x 3 diameters x pedestal on and off, 156 of 156), which is exactly why
    it had to go rather than be pinned: a copy that agrees today is the one nobody checks when the
    engine moves, and the engine is about to move (an overlay's own column height, WP-14.2 step 7).

    Two variants because dropping the pedestal moves every y above it -- a stack without its
    pedestal is a different stack, not a crop. Everything is linear in the module, so the page
    scales these rather than rebuilding them. Returns (variants, members), `members` keyed
    `assembly/member` and shared by both variants."""
    full = pe.stack_for(r)
    members, out = {}, {}
    for key, asms in (("with_pedestal", full),
                      ("no_pedestal", [a for a in full if a not in ("pedestal", "subplinth")])):
        d = pe.dimension(r, GEOM_MODULE_IN, include=asms)
        g = prof.pack_geometry(d, r.get("column"), r.get("projection_datum"))
        for a in d["assemblies"]:
            for m in a["members"]:
                members.setdefault(a["id"] + "/" + m["id"], {k: m.get(k) for k in PAGE_MEMBER_KEYS})
        out[key] = {
            "module_in": d["module_in"], "parts": d["parts"], "totals": d["totals"],
            "assemblies": [{"id": a["id"], "height_modules": a["height_modules"],
                            "height_in": a["height_in_stated"], "summed_in": a["height_in_summed"],
                            "y0": a["y_bottom_in"], "y1": a["y_top_in"],
                            "members": [{"id": m["id"], "y0": m["y_bottom_in"], "y1": m["y_top_in"],
                                         "height_in": m["height_in"],
                                         "projection_in": m.get("projection_in"),
                                         "side_by_side": bool(m.get("side_by_side"))}
                                        for m in a["members"]]}
                           for a in d["assemblies"]],
            # each member's FACE, as constructed -- the page ends a member's division line and
            # sets its label there, and knows nothing else about where a moulding reaches
            "face_x": {a["id"] + "/" + fc["id"]: fc["x"] for a in g["assemblies"] for fc in a["faces"]},
            **{k: g.get(k) for k in ("path", "outline_path", "ghost_path", "envelope_path", "bbox_in",
                                     "flutes", "assembly_datum", "die_naked", "die_naked_in",
                                     "die_naked_reason", "unpublished", "unconstructed",
                                     "drawn_straight", "lower_radius_in")},
        }
    return out, members


ORDERS = ["tuscan", "doric", "ionic", "corinthian", "composite"]
AUTHORITIES = [
    ("vignola",  "Vignola",  1562, "Regola delli cinque ordini"),
    ("palladio", "Palladio", 1570, "I Quattro Libri"),
    ("gibbs",    "Gibbs",    1732, "Rules for Drawing"),
    ("chambers", "Chambers", 1759, "A Treatise on Civil Architecture"),
    ("benjamin", "Benjamin", 1806, "The American Builder's Companion"),
]


def order_pack_ids():
    """EVERY ORDER PACK, not the authority x order cross-product. That grid takes 24 of the 26
    and says nothing about the other two: `greek-doric` (bound to greek-revival-american, regency
    and three more) and `moorish-arch` (bound to eight nodes) belong to no <authority>-<order>
    pair, and the `systems` loop below filters on kinds that exclude `order-system`, so both fell
    through BOTH loops. dist/orders.html served 55 of 57 packs and nothing said so. The grid is
    still used for the authority table's ORDERING; membership is now the corpus's own."""
    grid = [f"{auth}-{o}" for auth, _, _, _ in AUTHORITIES for o in ORDERS]
    return [pid for pid in grid if pid in pe.PACKS] + \
        sorted(pid for pid, p in pe.PACKS.items()
               if p.get("kind") == "order-system" and pid not in grid)


def page_data():
    packs = {}
    for pid in order_pack_ids():
        o = next((x for x in ORDERS if pid.endswith("-" + x)), pe.PACKS[pid].get("order") or "other")
        auth = pid.rsplit("-", 1)[0] if any(pid.endswith("-" + x) for x in ORDERS) else pid
        r = pe.resolve(pid)
        stack, members = stack_variants(r)
        packs[pid] = {
            "id": r["id"], "name": r["name"], "order": o, "authority": auth,
            "module": r["module"], "column": r.get("column", {}),
            # a pack with no `column` block (moorish-arch: "no order and no absolute module") has
            # no diameter for the page's scale to set, and is drawn at its own module instead
            "has_column": bool(r.get("column")),
            # OQ 65: which datum this pack's projections were measured from, stated
            # by the pack and inherited through the overlay chain by resolve()
            "projection_datum": r.get("projection_datum"),
            "members": members,
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
            "stack": stack,
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
    for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        n = json.load(open(f))
        style_names[n["id"]] = n["name"]

    return {"packs": packs, "systems": systems, "orders": ORDERS,
            "authorities": [{"id": a, "name": n, "year": y, "work": w} for a, n, y, w in AUTHORITIES],
            "styles": style_names, "engine_version": pe.ENGINE_VERSION}


def build_page(data=None):
    """The whole page as a string. Writes nothing."""
    tpl = open(TEMPLATE, encoding="utf-8").read()
    return tpl.replace("/*__DATA__*/null",
                       json.dumps(page_data() if data is None else data,
                                  separators=(",", ":"), ensure_ascii=False))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    data = page_data()
    page = build_page(data)
    if "--check" in argv:
        have = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else None
        if have != page:
            print("dist/orders.html is stale: run python3 build/render_orders.py")
            return 1
        print("dist/orders.html is current")
        return 0
    # ATOMIC, on build/build.py's idiom: a killed run must not leave the committed page truncated.
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(page)
    os.replace(tmp, OUT)
    print(f"order packs: {len(data['packs'])}  system packs: {len(data['systems'])}  "
          f"size {os.path.getsize(OUT)/1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
