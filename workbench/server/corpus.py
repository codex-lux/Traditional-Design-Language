"""Adapter over mcp_server/core.py, plus the two aggregations no core function returns.

core.py is pure functions with no protocol dependency — the whole server leans on that.
Everything here is read-only over core._data(); nothing writes to the corpus, and nothing
here may ever invoke build/build.py (it rewrites kits/).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (ROOT, os.path.join(ROOT, "mcp_server"), os.path.join(ROOT, "build")):
    if p not in sys.path:
        sys.path.insert(0, p)

import core  # noqa: E402  (mcp_server/core.py)

CASCADE_EDGES = ("descends_from", "regional_of")


def phylogeny():
    """The whole style graph, flattened for the Phylogeny surface.

    dist/taxonomy.json proves the shape is derivable, but it is a build artifact;
    this derives live from the same styles/ files so the picture cannot go stale.
    """
    D = core._data()
    taxa, edges = [], []
    for n in D["styles"].values():
        p = n.get("period") or {}
        taxa.append({
            "id": n["id"], "name": n["name"], "rank": n["rank"],
            "member_of": n.get("member_of"), "status": n.get("status"),
            "confidence": n.get("confidence"),
            "origin": p.get("origin"),
            "floruit_start": p.get("floruit_start"), "floruit_end": p.get("floruit_end"),
            "decline_end": p.get("decline_end"), "circa": p.get("circa", False),
            "regions": (n.get("geography") or {}).get("regions", [])[:3],
            "short": (n.get("description") or {}).get("short"),
        })
        for e in n.get("lineage") or []:
            edges.append({
                "from": n["id"], "to": e["target"], "type": e["type"],
                "weight": e.get("weight"),
                "inherits_kit": bool(e.get("inherits_kit")) or e["type"] in CASCADE_EDGES,
            })
    return {"taxa": taxa, "edges": edges,
            "edge_types": {"cascade_carrying": list(CASCADE_EDGES),
                           "claimed_only": ["references", "reacts_against", "revives"],
                           "reticulate": ["hybridizes_with"]}}


def kit_cascade(style_id):
    """Per-ancestor rows for the Kit surface's cascade display.

    resolve_kit()'s provenance is a source→count dict with composite
    "a + b (extends)" keys — honest but not decomposable into the row-per-ancestor
    display the cascade deserves. This walks the same chain and counts each kit
    file's own bindings, so 'a thin kit is correct, not incomplete' stays visible.
    """
    D = core._data()
    if style_id not in D["styles"]:
        return {"error": f"unknown style '{style_id}'"}
    chain = [style_id] + core._cascade(style_id)  # _cascade returns ancestors only
    rows = []
    for dist, sid in enumerate(chain):
        kit = D["kits"].get(sid)
        counts = {"specified": 0, "extends": 0, "forbidden": 0, "open": 0}
        if kit:
            for s in (kit.get("slots") or {}).values():
                b = s.get("binding", "open")
                counts[b] = counts.get(b, 0) + 1
        node = D["styles"].get(sid) or {}
        rows.append({"distance": dist, "id": sid, "name": node.get("name", sid),
                     "rank": node.get("rank"), "has_kit": kit is not None, **counts})
    return {"style": style_id, "levels": len(rows), "cascade": rows,
            "note": ("Nearest first. A thin kit is correct, not incomplete — "
                     "a style states only what the cascade does not already give it.")}


def slot_detail(style_id, slot_id):
    """One slot, resolved: core.resolve_kit's row plus the FULL variant ladder from the
    kit file that actually binds it. resolve_kit summarises variants to canonical[] and
    forbidden[] — the permitted and atypical rungs (a four-rank ladder, not a binary)
    only exist in the kit records, so this walks the cascade to the binding kit."""
    row = core.resolve_kit(style_id, slot=slot_id, only_specified=False)
    if "error" in row:
        return row
    slot_row = (row.get("slots") or [None])[0]
    if not slot_row:
        return {"error": f"slot '{slot_id}' not found for '{style_id}'"}
    D = core._data()
    chain = [style_id] + core._cascade(style_id)
    variants, note, bound_by = None, None, None
    for sid in chain:
        kit = D["kits"].get(sid)
        s = (kit or {}).get("slots", {}).get(slot_id)
        if s and s.get("binding") in ("specified", "extends", "forbidden"):
            if variants is None and s.get("variants"):
                variants = s["variants"]
                bound_by = sid
            if note is None and s.get("note"):
                note = s["note"]
            if variants is not None and note is not None:
                break
    out = dict(slot_row)
    if variants is not None:
        out["variants"] = variants
        out["variants_from"] = bound_by
    if note is not None:
        out["note"] = note
    out["cascade_distance"] = {sid: i for i, sid in enumerate(chain)}
    return out


def invalidate():
    """Drop every cache so on-disk corpus edits are seen. Explicit by design:
    auto-invalidation per request would reintroduce the OQ-28 tax."""
    import modcache
    modcache.invalidate()
    core._data.cache_clear()
    return {"reloaded": True}
