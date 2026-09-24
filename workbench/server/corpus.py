"""Adapter over mcp_server/core.py, plus the two aggregations no core function returns.

core.py is pure functions with no protocol dependency — the whole server leans on that.
Everything here is read-only over core._data(); nothing writes to the corpus, and nothing
here may ever invoke build/build.py (it rewrites kits/).
"""
import hashlib
import json
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

    NOT CACHED, and that is a measurement rather than an oversight. An audit added a
    module-level cache here on the argument that this was "the same bug as the search
    index, one endpoint over". It was not, and the cache was 7.8x SLOWER: the rebuild
    below only walks already-in-memory core._data() and costs 0.23 ms, while returning a
    cached copy costs 1.79 ms because core.copy_json is json.loads(json.dumps(o)) over
    157 KB. The endpoint costs 20.79 ms end to end, so the build is 1.1% of it and the
    rest is FastAPI's encoder — caching the build optimised the one part that was already
    cheap and added a serialisation round trip to do it.

    search_index() above IS worth caching, and the difference is the point: its rebuild
    re-globs and re-parses 21 parti files (2.74 ms), and it returns the SHARED object
    rather than a copy. Measure before imitating it.
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
            # The whole list, not the first three. The truncation was fine while this fed
            # a caption; the map view places a style by the FINEST region it names, and 82
            # of 164 styles carry more than three — so a cut here silently coarsened half
            # the corpus, putting styles in the middle of a country that name a valley.
            "regions": (n.get("geography") or {}).get("regions", []),
            # And the hearth, which is finer still: `regions` says "United States" where
            # the hearth says "Pasadena and Los Angeles, California". 59 of the 81
            # country-level placements had a hearth naming somewhere better (OQ 65).
            "hearth": (n.get("geography") or {}).get("hearth"),
            "short": (n.get("description") or {}).get("short"),
        })
        for e in n.get("lineage") or []:
            edges.append({
                "from": n["id"], "to": e["target"], "type": e["type"],
                "weight": e.get("weight"),
                "inherits_kit": bool(e.get("inherits_kit")) or e["type"] in CASCADE_EDGES,
                # WP-14.4 (PRD §H.6): the lineage record's own slot scope where it states one
                # (OQ 58 -- a scoped edge carries THOSE slots and nothing else), null where it
                # does not. Served rather than re-read by the app, beside the one spelling of
                # "this edge carries the cascade" above.
                "slots": e.get("slots"),
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


def _hay(*parts):
    """One lowercase haystack from whatever a record can offer. Lists are flattened,
    dicts contribute their values, None is skipped, and everything is joined with a
    space so a substring cannot straddle two fields and match nothing real."""
    out = []

    def add(v):
        if v is None:
            return
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, (list, tuple, set)):
            for x in v:
                add(x)
        elif isinstance(v, dict):
            for x in v.values():
                add(x)
        elif isinstance(v, (int, float)):
            out.append(str(v))

    for p in parts:
        add(p)
    return " ".join(out).lower()


def _author(authority):
    """A pack's `authority` is {"source": "Asher Benjamin, The Practical House Carpenter
    (Boston, 1830), 'Doric Order, Example No. 3', Plate VI…"} — a full bibliographic
    citation, and the whole of it prose. The name is the part somebody types, so only the
    first clause is indexed. Searching "bunting" still finds the adobe module; searching a
    plate number no longer finds anything."""
    if isinstance(authority, dict):
        authority = authority.get("source")
    if not isinstance(authority, str):
        return None
    return authority.split(",")[0].strip()[:60] or None


# Built once per process. The corpus does not change under a running server — that is why the
# client caches the response forever — but the SERVER was rebuilding all 665 entries and
# re-globbing and re-parsing the 21 parti files on EVERY request: 214 KB and 3.3 ms of CPU a
# call, 11x the cost of /api/phylogeny, on an endpoint deliberately left out of the metered
# set. An adversarial audit measured it. /api/dev/reload already exists for the case where the
# corpus is edited under a dev server; it clears core's caches, so this is cleared with it.
_SEARCH_INDEX = None


def reset_search_index():
    global _SEARCH_INDEX
    _SEARCH_INDEX = None


def search_index():
    """Every nameable thing in the corpus, as one flat list the palette can hold.

    Sent once and matched in the browser: a round trip per keystroke would be slower than
    the corpus is large. The scoring lives in the client (src/search/match.js); this only
    says what exists and what it is called.

    WHAT IS INDEXED, and why it is less than core.find_style searches: names, ids, akas
    and the short categorical fields — the words somebody types when they are looking for
    a thing. Not the prose. Indexing every fault's `cause` and `correct_practice` and
    every style's `diagnostic_tells` took the payload from 130 KB to 855 KB, and bought
    results nobody could account for: typing "brick" would surface a fault because the
    word appears in the third paragraph of its remedy. Prose search already has two
    better homes — `/api/styles?query=` searches the tells server-side, and the rail
    reads the corpus properly. The palette finds things by name. That boundary is stated
    in the response's own `indexes` field so a caller need not guess it.

    Every entry carries a `cite` in the citation grammar rather than a surface name, so
    the palette dispatches through exactly the router the rail already uses and cannot
    reach a place a citation could not name. workbench/server/tests/test_search_index.py
    holds that: each cite must parse and resolve.
    """
    global _SEARCH_INDEX
    if _SEARCH_INDEX is not None:
        return _SEARCH_INDEX
    import glob as _glob
    import json as _json
    import os as _os

    D = core._data()
    e = []

    for s in D["styles"].values():
        d = s.get("description") or {}
        e.append({
            "cite": "style:" + s["id"], "kind": "style", "id": s["id"], "name": s["name"],
            "meta": s.get("rank"),
            "hay": _hay(s["name"], s["id"], s.get("aka"),
                        (s.get("geography") or {}).get("regions")),
            "short": d.get("short"),
        })

    for s in D["slots"].values():
        e.append({
            "cite": "slot:" + s["id"], "kind": "slot", "id": s["id"], "name": s["name"],
            "meta": s.get("group_name") or s.get("group"),
            "hay": _hay(s["name"], s["id"], s.get("group"), s.get("group_name")),
        })

    for f in D["faults"].values():
        e.append({
            "cite": "fault:" + f["id"], "kind": "fault", "id": f["id"], "name": f["name"],
            "meta": f.get("category"),
            "hay": _hay(f["name"], f["id"], f.get("aka"), f.get("category")),
        })

    for pid, p in D["engine"].PACKS.items():
        e.append({
            "cite": "pack:" + pid, "kind": "pack", "id": pid, "name": p.get("name", pid),
            "meta": p.get("kind"),
            "hay": _hay(p.get("name"), pid, p.get("aka"), p.get("kind"), _author(p.get("authority"))),
        })

    for r in D["rooms"].values():
        e.append({
            "cite": "room:" + r["id"], "kind": "room", "id": r["id"], "name": r["name"],
            "meta": r.get("function_class"),
            "hay": _hay(r["name"], r["id"], r.get("aka"), r.get("function_class")),
        })

    for m in D["massings"].values():
        e.append({
            "cite": "massing:" + m["id"], "kind": "massing", "id": m["id"], "name": m["name"],
            "meta": m.get("footprint"),
            "hay": _hay(m["name"], m["id"], m.get("aka")),
        })

    for g in D["groupings"].values():
        e.append({
            "cite": "grouping:" + g["id"], "kind": "grouping", "id": g["id"], "name": g["name"],
            "meta": g.get("scale"),
            "hay": _hay(g["name"], g["id"], g.get("aka"), g.get("scale")),
        })

    for f in sorted(_glob.glob(_os.path.join(ROOT, "partis", "*.json"))):
        try:
            p = _json.load(open(f))
        except Exception:
            continue          # a parti that will not parse is check_partis.py's to report
        e.append({
            "cite": "parti:" + p["id"], "kind": "parti", "id": p["id"],
            "name": p.get("name", p["id"]), "meta": p.get("circulation_parti"),
            "hay": _hay(p.get("name"), p["id"], p.get("aka"), p.get("circulation_parti")),
        })

    _SEARCH_INDEX = {
        "count": len(e),
        "entries": e,
        "indexes": ["name", "id", "aka", "categorical fields (rank, group, category, "
                    "kind, function_class, scale, circulation_parti)", "style regions"],
        "does_not_index": ["prose bodies: diagnostic_tells, defining_characteristics, "
                           "fault cause and correct_practice, slot notes, descriptions"],
        "note": ("The palette finds things by name. For prose use /api/styles?query=, "
                 "which searches the tells server-side, or ask the rail."),
    }
    return _SEARCH_INDEX


def pack_list():
    """Every proportion pack, for the Proportions surface's navigation. The
    non-classical packs are equal citizens — most traditional buildings were
    proportioned from a material module, not a column — so the list leads with the
    system and module packs and the kind is first-class, not an afterthought."""
    packs = core._data()["engine"].PACKS
    out = []
    for pid, p in packs.items():
        out.append({"id": pid, "name": p.get("name", pid), "kind": p.get("kind"),
                    "authority": p.get("authority"),
                    "overlay_on": p.get("overlay_on")})
    kind_rank = {"module-system": 0, "trim-system": 1, "opening-system": 2,
                 "room-system": 3, "facade-system": 4, "order-system": 5}
    out.sort(key=lambda r: (kind_rank.get(r["kind"], 9), r["id"]))
    return {"count": len(out), "packs": out,
            "note": ("Order packs are <authority>-<order> and compare at a common column "
                     "DIAMETER, never a common module — authorities do not share one.")}


CEILING_DEFAULT_IN = 108.0     # the route's defaults since WP-5.2, now applied HERE so the
OPENING_DEFAULT_IN = 36.0      # route can tell "not given" from "given as 108" (PRD §H.1)


def _profiles():
    """`build/profiles.py`, through modcache -- never a local by-path loader."""
    return core._mod("profiles", os.path.join(ROOT, "build", "profiles.py"))


def proportions_with_members(pack_id, column_diameter=None, module=None,
                             ceiling_height=None, opening_width=None):
    """core.get_proportions plus full member lists for EVERY assembly — the plate
    drawing needs the whole stack at once, and the API's one-assembly-at-a-time
    shape (right for an agent's context budget) would cost seven round-trips.

    WP-14.4 (PRD §H.1): EVERY PACK THE ENGINE CAN DRAW, NOT ONLY THE 25 WITH A COLUMN STACK.
    `pe.dimension(pk, mod, None)` dimensions `stack_for(pk)`, which knows only order assembly
    names, so for every pack without a stack it returned ZERO assemblies -- although asked one
    assembly at a time the same engine dimensions `trim-classical`'s three wall sections and
    three casings, 71 members. `drawing` says which path a pack takes:
      "stack"       -- `stack_for` is non-empty: THE EXISTING PATH, every pre-existing key's value
                       byte for byte (held by workbench/server/tests/test_pack_plates.py against
                       `core.get_proportions`, and in the WP-14.4 report by the base commit's
                       own function over all 25 stacked packs at four argument sets, 100 of
                       100). Only the new keys below are added.
      "assemblies"  -- no stack and the pack carries assemblies (26 non-order packs and
                       `moorish-arch`, an order pack whose impost, arch and alfiz are no column):
                       each assembly dimensioned on its own with `include=[aid]`, so its y runs
                       from 0, and its geometry built on the WALL datum, because none of these
                       stands on a column and the order datum read `trim-classical`'s ceiling
                       module as a column radius.
      null          -- nothing to draw (five packs: no assemblies at all). Never a picture of
                       something the record does not hold.

    THE MODULE BOUND TO THE CEILING. A pack whose `module.equals` is `ceiling_height` states that
    its module IS the room's ceiling (`build/check_systems.py` check 19 lie-checks the claim), so
    the module IS the ceiling here: the plate and the rules table describe one wall, and a reader
    moving the ceiling moves both. Where no ceiling is given it defaults to the pack's own
    `default_size_in` -- `trim-classical`'s 114 in, at which its part is exactly six inches --
    and not to the route's 108, which would silently re-dimension the pack every reader opens
    first. Every other pack takes today's call with today's defaults.
    """
    pe = core._data()["engine"]
    try:
        pk = pe.resolve(pack_id)
    except Exception:
        # core's own refusal shape -- {"error", "available", "hint"} -- rather than a second
        # wording of "no such pack".
        return core.get_proportions(pack_id)
    equals = (pk.get("module") or {}).get("equals")
    bound = equals == "ceiling_height"
    if ceiling_height is not None:
        ceiling = ceiling_height
    elif bound:
        ceiling = pk["module"]["default_size_in"]
    else:
        ceiling = CEILING_DEFAULT_IN
    opening = opening_width if opening_width is not None else OPENING_DEFAULT_IN
    if bound:
        # the `module` and `column_diameter` arguments are NOT read: the module is the ceiling
        out = core.get_proportions(pack_id, module=ceiling, ceiling_height=ceiling,
                                   opening_width=opening)
    else:
        out = core.get_proportions(pack_id, column_diameter=column_diameter, module=module,
                                   ceiling_height=ceiling, opening_width=opening)
    if "error" in out:
        return out
    stacked = bool(pe.stack_for(pk))
    drawing = "stack" if stacked else ("assemblies" if pk.get("assemblies") else None)
    if drawing == "stack":
        _stacked_members(out, pk, pe)
    else:
        # The per-assembly geometry carries what the plate draws. The pack-level `geometry`
        # is null: under the order datum it drew every one of these packs off its own wall.
        if pk.get("column"):
            out["column"] = {k: v for k, v in pk["column"].items()
                             if k in ("entasis_begins_at",)}
        out["projection_datum"] = pk.get("projection_datum")
        out["geometry"] = None
        out["assemblies"] = (_wall_assemblies(pk, pe, out["module_in"])
                             if drawing == "assemblies" else [])
    out["drawing"] = drawing
    out["at"] = {"ceiling_height": ceiling, "opening_width": opening,
                 "module_in": out["module_in"]}
    out["module_name"] = pk["module"]["name"]
    out["module_bound_to"] = equals
    out["kind"] = pk["kind"]
    out["used_by"] = pack_users(pk["id"])
    return out


def _wall_assemblies(pk, pe, module_in):
    """Each assembly of a stackless pack, in the pack's declaration order, on the wall datum.

    `height_in` is the SUMMED extent -- what is drawn -- and `height_in_stated` the stated
    height. They are EQUAL on all 50 assemblies of the 27 stackless packs, measured: side-by-side
    members (`sums_check: false`, `moorish-arch`'s arch and alfiz) are given the stated height by
    `dimension()` itself, and a stacked record whose members do not sum to it is refused by
    `check_systems.py` check 11 and by `check_orders.py`. Both are served because a record
    COULD state a height its members do not fill, and the plate must draw what is there -- the
    case is DRIVEN in `workbench/server/tests/test_pack_plates.py`, since no shipped record
    reaches it. `owner` is the pack in the overlay chain that actually STATES the assembly
    (`pe.assembly_owner`, the one spelling) -- no stackless pack is an overlay today, so that
    case is driven too. `unconstructed`
    is what `profiles.py` could not construct -- reported, never drawn as something else."""
    prof = _profiles()
    rows = []
    for aid in (pk.get("assemblies") or {}):
        d = pe.dimension(pk, module_in, [aid])
        if not d["assemblies"]:
            continue
        da = d["assemblies"][0]
        g = prof.pack_geometry(d, datum="wall")
        rows.append({"id": aid, "height_modules": da["height_modules"],
                     "height_in": da["height_in_summed"],
                     "height_in_stated": da["height_in_stated"],
                     "sums_check": da["sums_check"], "members": da["members"],
                     "owner": pe.assembly_owner(pk["id"], aid),
                     "geometry": g["assemblies"][0], "unconstructed": g["unconstructed"]})
    return rows


def _stacked_members(out, pk, pe):
    """The stack path, unchanged since WP-5.11: every pre-existing key's value byte for byte."""
    d = pe.dimension(pk, out["module_in"], None)
    members = {a["id"]: a["members"] for a in d["assemblies"]}
    for a in out["assemblies"]:
        a["members"] = members.get(a["id"], [])
    # The column record itself, for the plate that draws the stack against the shaft's
    # own naked: a band's projection is measured FROM a datum, and above the astragal
    # that datum is the diminished radius, not the lower one. Without diminution and
    # entasis_begins_at the plate would have to assume a taper the authority may not
    # publish -- chambers-corinthian begins its diminution at the base, gibbs at a third.
    # entasis_begins_at only: the taper itself comes from totals.upper_diameter_in, and
    # `fluting.profile` is a paragraph of prose that would ride on every request unread
    if pk.get("column"):
        out["column"] = {k: v for k, v in pk["column"].items()
                         if k in ("entasis_begins_at",)}
    # OQ 65, ruled: which datum this pack's projections are measured from is STATED, not
    # derived by whoever draws them. Inherited through the overlay chain by resolve().
    out["projection_datum"] = pk.get("projection_datum")
    # WP-5.11: the constructed moulding geometry, so the browser draws what the engine built
    # rather than re-deriving a curve or a datum for itself. Segments are in inches at the
    # module above; a client wanting another size scales them, because pack geometry is linear
    # in the module (proved in tests/test_profiles.py). See build/profiles.py for why this is
    # served rather than ported: every copy of this arithmetic that has ever existed in this
    # corpus has eventually disagreed with the others.
    prof = core._mod("profiles", os.path.join(ROOT, "build", "profiles.py")) \
        if hasattr(core, "_mod") else None
    if prof is None:
        import importlib.util as _il
        _s = _il.spec_from_file_location("profiles", os.path.join(ROOT, "build", "profiles.py"))
        prof = _il.module_from_spec(_s); _s.loader.exec_module(prof)
    out["geometry"] = prof.pack_geometry(d, pk.get("column"), pk.get("projection_datum"))
    return out


# ----------------------------------------------------------------- who uses a pack (WP-14.4)
def _pack_card(pid, binding=None):
    """A pack by name and kind from the registry, plus the binding's role and precedence."""
    raw = core._data()["engine"].PACKS.get(pid) or {}
    card = {"pack": pid, "name": raw.get("name"), "kind": raw.get("kind")}
    if binding is not None:
        card["role"] = binding.get("role")
        card["precedence"] = binding.get("precedence")
    return card


def _style_name(sid):
    if sid is None:
        return None
    return (core._data()["styles"].get(sid) or {}).get("name")


def pack_users(pack_id):
    """Who this pack reaches, by INVERTING `build/resolve_kit.resolve_packs` over every node of
    `core._kit_graph()` (PRD §H.2) -- no second cascade. `resolve_packs` is the one function
    that decides pack MEMBERSHIP, declines and the opt-in gate included, so a second walk here
    would be a third spelling of OQ 51's rule the first time either moved.

      own                      nodes that bind the pack themselves (`_source` is the node)
      delivered                nodes it reaches through an ancestor, with the ancestor, the
                               binding's role, and whether the node names it in `inherits_packs`
      applies_to_only          named in the pack's own `applies_to` and reached by nothing
      bound_not_in_applies_to  bound by a node the pack's `applies_to` does not name
    """
    rk, g = core._kit_graph()
    own, delivered = [], []
    for nid in sorted(g.get("nodes") or {}):
        rec = rk.resolve_packs(g, rk.chain_for(g, nid)).get(pack_id)
        if rec is None:
            continue
        if rec["_source"] == nid:
            own.append(nid)
        else:
            node = g["nodes"][nid]
            delivered.append({"style": nid, "from": rec["_source"], "role": rec.get("role"),
                              "opted_in": pack_id in (node.get("inherits_packs") or [])})
    try:
        applies = list(core._data()["engine"].resolve(pack_id).get("applies_to") or [])
    except Exception:
        applies = []
    reached = set(own) | {d["style"] for d in delivered}
    return {"own": own, "delivered": delivered,
            "applies_to_only": sorted(set(applies) - reached),
            "bound_not_in_applies_to": sorted(set(own) - set(applies))}


def _precedence_key(card):
    p = card.get("precedence")
    return (p is None, p if p is not None else 0, card["pack"])


def style_packs(style_id):
    """A style's packs by provenance (PRD §H.3), from `resolve_packs` over its own chain.

    own       the node binds it
    opted_in  an ancestor delivers it AND the node names it in `inherits_packs`
    delivered an ancestor delivers it by cascade, grouped by that ancestor, nearest first
    withheld  the opt-in gate stopped it (`resolve_kit.withheld_for`, the one reader)
    declined  the node refused it (`resolve_kit.refusals_for`, the one reader)

    Five lists and never fewer: a pack that reaches a node, one withheld from it and one it
    declined are three different facts, and a reader asking "why does this style not have that
    pack" is answered by the last two."""
    D = core._data()
    rk, g = core._kit_graph()
    if style_id not in D["styles"] or style_id not in (g.get("nodes") or {}):
        return core.get_style(style_id)          # get_style's own refusal shape -> a 404
    chain = rk.chain_for(g, style_id)
    node = g["nodes"][style_id]
    opted = set(node.get("inherits_packs") or [])
    own, opted_in, groups = [], [], {}
    for pid, rec in rk.resolve_packs(g, chain).items():
        src = rec["_source"]
        card = _pack_card(pid, rec)
        if src == style_id:
            own.append(card)
        elif pid in opted:
            opted_in.append(dict(card, **{"from": src, "from_name": _style_name(src)}))
        else:
            groups.setdefault(src, []).append(card)
    own.sort(key=_precedence_key)
    opted_in.sort(key=_precedence_key)
    delivered = []
    for src in sorted(groups, key=chain.index):
        # the packs in THAT ancestor's own binding order
        order = [pb["pack"] for pb in (g["nodes"][src].get("proportion_packs") or [])]
        packs = sorted(groups[src], key=lambda c: order.index(c["pack"])
                       if c["pack"] in order else len(order))
        delivered.append({"from": src, "from_name": _style_name(src),
                          "distance": chain.index(src), "packs": packs})
    withheld = []
    for pid, rec in rk.withheld_for(g, style_id).items():
        src = rec.get("_would_have_come_from")
        withheld.append(dict(_pack_card(pid), role=rec.get("role"), **{
            "from": src, "from_name": _style_name(src), "why": rec.get("_why")}))
    declined = []
    for rec in rk.refusals_for(g, style_id):
        src = rec.get("_would_have_come_from")
        declined.append(dict(_pack_card(rec["pack"]), **{
            "from": src, "from_name": _style_name(src),
            "reason": rec.get("reason"), "basis": rec.get("basis")}))
    return {"style": style_id, "own": own, "opted_in": opted_in, "delivered": delivered,
            "withheld": withheld, "declined": declined,
            "counts": {"own": len(own), "opted_in": len(opted_in),
                       "delivered": sum(len(gr["packs"]) for gr in delivered),
                       "withheld": len(withheld), "declined": len(declined)}}


# ----------------------------------------------------------------- the dossier (WP-14.4)
# THE SECTION ORDER IS `citations.DOSSIER_SECTIONS` (PRD §D.1), which WP-14.3 adds and pins to
# the app's copy in `test_grammar_agreement.py`. Until it lands this module carries the nine
# strings as a FALLBACK and reads the real one the moment it exists; WP-14.3 deletes this line.
# `workbench/server/tests/test_dossier_routes.py` fails if the two ever disagree, so the
# fallback cannot quietly become a third spelling.
_SECTIONS_UNTIL_14_3 = ("identify", "members", "lineage", "kit", "proportions", "plans",
                        "rules", "faults", "evidence")
_VERDICT_KEYS = ("EXCEPTION_FOR_THIS_STYLE", "EXCEPTION_NOT_EARNED_BY_THIS_STYLE",
                 "EXCEPTION_WHOSE_CONDITION_COULD_NOT_BE_JUDGED", "INVERTED_FOR_THIS_STYLE")


def dossier_sections():
    """The dossier's section ids, in order: the citations module's, else the fallback."""
    from . import citations
    return tuple(getattr(citations, "DOSSIER_SECTIONS", None) or _SECTIONS_UNTIL_14_3)


def _node_ref(n):
    return {"id": n["id"], "name": n.get("name"), "rank": n.get("rank")}


def _by_floruit(n):
    return ((n.get("period") or {}).get("floruit_start") is None,
            (n.get("period") or {}).get("floruit_start") or 0, n["id"])


def dossier_faults(style_id):
    """`core.find_faults(style=...)` partitioned three ways (PRD §H.4): a verdict for THIS style
    (an exception read for it, an inversion, or a severity its record states for it), a fault
    written for its lineage rather than for every house, and the universal rest. The three
    partition `matches`, which the route's test holds."""
    D = core._data()
    res = core.find_faults(style=style_id, limit=300)
    here, lineage, universal = [], [], 0
    for card in res["faults"]:
        rec = D["faults"].get(card["id"]) or {}
        if any(k in card for k in _VERDICT_KEYS) or any(
                s.get("style") == style_id for s in (rec.get("severity_by_style") or [])):
            here.append(card["id"])
        elif "universal" not in (rec.get("applies_to") or []):
            lineage.append(card["id"])
        else:
            universal += 1
    return {"verdict_here": here, "lineage": lineage, "universal_count": universal,
            "matches": res["matches"]}


def dossier_plan_types(style_id):
    """The three lists the Plan types section shows (PRD §H.4): massing affinities from the
    node, native partis from `core.list_partis`, and the groupings whose `style_variation`
    NAMES this style with `present` not false. Not `GET /api/groupings?style=`, which returns
    every grouping not marked absent (PRD §0.1 #12)."""
    D = core._data()
    n = D["styles"][style_id]
    affs = [{"massing": m.get("massing"),
             "massing_name": (D["massings"].get(m.get("massing")) or {}).get("name"),
             "affinity": m.get("affinity")} for m in (n.get("massing_affinities") or [])]
    partis = [{"id": p["id"], "name": p.get("name")}
              for p in core.list_partis(style=style_id)["partis"]]
    groupings = []
    for gid in sorted(D["groupings"]):
        gr = D["groupings"][gid]
        for sv in gr.get("style_variation") or []:
            if sv.get("style") == style_id and sv.get("present") is not False:
                groupings.append({"id": gid, "name": gr.get("name"), "note": sv.get("note")})
                break
    return {"massing_affinities": affs, "partis": partis, "groupings": groupings}


def style_dossier(style_id):
    """What a Style Dossier's head and section strip need, as COUNTS (PRD §H.4, §D.2).

    Each count is the figure its own endpoint would give -- the kit's is `/api/kit`'s
    `slots_returned`, the proportions' is the sum of `/api/styles/{id}/packs`' five lists --
    and `workbench/server/tests/test_dossier_routes.py` holds every one to that endpoint, so the
    strip cannot promise a section the section does not deliver. A section whose count is zero
    is OMITTED rather than listed empty; `identify` is always listed and has no count. That rule
    over these counts IS the rank-awareness -- a tradition has no kit, no rules, no packs -- with
    one rank rule for faults: at a tradition or a family only the lineage and the verdicts count,
    because a universal fault is about a house and a tradition is not built."""
    D = core._data()
    n = D["styles"].get(style_id)
    if not n:
        return core.get_style(style_id)          # get_style's own refusal shape -> a 404
    S = D["styles"]
    chain, cur, seen = [], S.get(n.get("member_of") or ""), {style_id}
    while cur and cur["id"] not in seen:
        seen.add(cur["id"])
        chain.append(_node_ref(cur))
        cur = S.get(cur.get("member_of") or "")
    chain.reverse()                              # root first
    members = sorted((m for m in S.values() if m.get("member_of") == style_id), key=_by_floruit)
    buildable = []
    if n.get("rank") in ("tradition", "family"):
        frontier, found = [style_id], {}
        while frontier:
            nxt = [m for m in S.values() if m.get("member_of") in frontier and m["id"] not in found]
            for m in nxt:
                found[m["id"]] = m
            frontier = [m["id"] for m in nxt]
        buildable = [_node_ref(m) for m in sorted(found.values(), key=_by_floruit)
                     if m.get("rank") in ("style", "variant")]
    faults = dossier_faults(style_id)
    plans = dossier_plan_types(style_id)
    packs = style_packs(style_id)
    descendants = sum(1 for m in S.values() for e in (m.get("lineage") or [])
                      if e.get("target") == style_id)
    if n.get("rank") in ("style", "variant"):
        fault_count = faults["matches"]
    else:
        fault_count = len(faults["verdict_here"]) + len(faults["lineage"])
    counts = {
        "members": len(members),
        "lineage": len(n.get("lineage") or []) + descendants,
        "kit": core.resolve_kit(style_id).get("slots_returned", 0),
        "proportions": sum((packs.get("counts") or {}).values()),
        "plans": sum(len(v) for v in plans.values()),
        "rules": len(n.get("constraints") or []),
        "faults": fault_count,
        "evidence": (len(n.get("exemplars") or []) + len(n.get("sources") or [])
                     + core.find_assets(style=style_id)["matches"]),
    }
    sections = []
    for sid in dossier_sections():
        if sid == "identify":
            sections.append({"id": "identify", "count": None})
        elif counts.get(sid):
            sections.append({"id": sid, "count": counts[sid]})
    return {"id": style_id, "name": n.get("name"), "rank": n.get("rank"),
            "member_of": n.get("member_of"), "chain": chain,
            "members": [_node_ref(m) for m in members], "buildable_at": buildable,
            "sections": sections, "faults": faults, "plan_types": plans}


def _typefacts():
    """`build/typefacts.py`, the leaf that holds the one verdict (WP-13.4)."""
    return core._mod("typefacts", os.path.join(ROOT, "build", "typefacts.py"))


def refused_response(ref):
    """The shape every server surface hands back on a refused placement (WP-13.4).

    Lucas ruled 15 Sep 2026 that a placement breaking a hard fact of the type is REFUSED
    rather than drawn, reversing the 25 Aug ruling ("the partner hears the refusal and still
    sees a drawing") for every user-facing surface. The RECORD keeps the least-bad placement,
    because it is what the conflict set is about and it is the wall drag's working sketch; no
    surface a person reads draws it.

    **THE KEY IS `refused_placement` AND IT MAY NEVER BE `refusal`.** `app.py`'s export route
    maps a `refusal` key to **501 Not Implemented** -- the honest missing-library answer for
    ezdxf or ifcopenshell -- so a placement refusal wearing that key would tell a reader the
    server lacks a capability it has. A refused house is a 422: the request was understood and
    the answer is no.

    `unsolved` rides along because every existing caller of `_placed` already tests
    `"error" in res`, and a refusal is an error to them in exactly the sense that there is
    nothing to draw. The reason is not a bare string: `refused_placement` is
    `typefacts.refusal`'s own typed dict, with the conflict set and the reader-facing lines."""
    what = "; ".join(c.get("about") or c.get("fact") or str(c)
                     for c in (ref.get("conflicts") or [])
                     if isinstance(c, dict)) if ref.get("kind") != "infeasible" else ""
    if ref.get("kind") == "infeasible":
        sentence = ("This placement is REFUSED: CP-SAT proved the record's declared facts "
                    "cannot all hold, so there is no house to draw. The conflict set says "
                    "which requirements are in the way; the brief or the parti is what changes.")
    else:
        sentence = ("This placement is REFUSED: it breaks the type's own facts"
                    + (f" -- {what}" if what else "")
                    + ". The record keeps the least-bad placement as the conflict set's own "
                      "explanation; no sheet, export or model is drawn from it.")
    return {"error": sentence, "refused_placement": ref, "unsolved": True}


def _forward(res):
    """Pass a refusal (or a plain error) UP without flattening it to its sentence.

    Three call sites in `drawing()` and one in `scene()` read `{"error": res["error"]}` and
    dropped everything else, so the conflict set died one frame above where it was computed
    and the route answered 422 with a sentence and no evidence (WP-13.4). Named rather than
    inlined because there are four of them and a fifth will be written."""
    return {k: v for k, v in res.items()
            if k in ("error", "refused_placement", "unsolved", "detail")}


def _placed(plan, parti=None, candidates=250):
    """Place the plan ONCE, on the proving engine, for every sheet in a drawing set.

    WP-6.4. Until this, each sheet solved for itself and they did not agree: the plan SVG
    went through `engine="auto"` (WP-6.3), while `export_dxf._solved_copy` forced
    `engine="heuristic"` and `structure.build_section` took its own heuristic default. A
    reader looking at a CP-proved plan sheet could download a DXF of a DIFFERENT placement
    of the same house, and the section beside it was a third. One drawing set is one
    building or it is nothing.

    A record that already carries `geometry` is returned untouched -- a bench plan the
    client has already had placed must not be re-solved out from under the sheet the reader
    is looking at, which is the same rule `_solved_copy` applies.

    **THE SHORT CIRCUIT RE-JUDGES, AND THAT IS WP-13.4'S HALF OF IT.** A carried record never
    reaches a record writer, so `geometry._disclose` never runs on it and nothing has decided
    whether it may be drawn: a composed candidate (`compose.py`), the plan `scene()` returns,
    and any record a client keeps and posts back all arrive this way. `typefacts.judge` is the
    SAME function `_disclose` calls -- it re-measures the tiling, the bearing continuity and
    the hearth off the rectangles and re-reads the stacking tally the record carries -- so the
    verdict is one spelling with three callers rather than a second reader here. It is cheap
    (25 ms on the Tidewater record, measured) and it does NOT re-solve: the record is returned
    as it stands, which is the guarantee this branch exists for.
    """
    TF = _typefacts()
    if any("geometry" in r for lv in plan.get("levels", []) for r in lv["rooms"]):
        try:
            ref = TF.judge(plan)
        except Exception as e:                      # noqa: BLE001 -- unjudged, not refused
            # A record we could not measure is COULD NOT EVALUATE and is not a refusal: the
            # three states are held, downgraded and unjudged, and collapsing the third into
            # either of the others is what this corpus names first.
            return {"error": f"the placement this record carries could not be judged: "
                             f"{type(e).__name__}: {str(e)[:200]}", "unsolved": True}
        if ref:
            return refused_response(ref)
        return plan
    geo = core._mod("geometry", os.path.join(ROOT, "build", "geometry.py"))
    # THE INPUT'S OWN FINGERPRINT, TAKEN BEFORE THE SOLVE (WP-11.8, finding J6). Two CP-SAT runs
    # of one record agree to the foot -- OQ 44's "reproducible by default" holds and was
    # re-measured for the diagnosis -- so when the bench's sheet and the CLI's disagree, the INPUT
    # differed: a style, a parti, or an edit. The plate carried nothing that would let a reader
    # tell which, and "the same house drawn twice, differently" is the one thing a reader cannot
    # diagnose from the drawing. Digested here rather than after placement, because the point is
    # to identify what was HANDED to the solver.
    digest = hashlib.sha256(json.dumps(plan, sort_keys=True,
                                       default=str).encode()).hexdigest()[:12]
    out = geo.solve(plan, parti, candidates, engine="auto")
    if "error" in out:
        return out
    sv = (out.get("geometry_report") or {}).setdefault("solver", {})
    # WHICH placement this surface drew and WHY, which the ruling asks for by name
    # (`oq/a-proof-of-feasibility-is-not-a-proof-of-composition`). `engine` already says what ran;
    # this says who asked, with what, and on which record -- and where a proof's compositional
    # objective did not run, `solver.alternative` beside it carries the search's placement and
    # BOTH its numbers.
    sv["drawn_by"] = {
        "surface": "workbench/server/corpus.py::_placed",
        "engine_requested": "auto",
        "candidates": candidates,
        "parti": (parti or {}).get("id") if isinstance(parti, dict) else parti,
        "input_digest": digest,
        "why": ("Every sheet in a drawing set takes this one placement (WP-6.4), on the proving "
                "engine where it can be had. Where the proof's compositional objective did not "
                "run, `solver.alternative` carries the search's placement beside it with its "
                "demerit score AND the count of declared facts it breaks -- the second number is "
                "not optional, because a lower score alone reads as a better house and is not "
                "(oq/a-proof-of-feasibility-is-not-a-proof-of-composition)."),
    }
    # AND THEN THE VERDICT, READ OFF THE RECORD (WP-13.4). `geometry._disclose` wrote it
    # through `typefacts.judge`; nothing here re-derives "may this be drawn".
    ref = (out.get("geometry_report") or {}).get("refused")
    if ref:
        return refused_response(ref)
    return out


def drawing(kind, plan, parti=None, face=None, candidates=250, register="presentation"):
    """Run the build/ pipeline for one drawing and return its SVG, re-tokenized to
    the Drawn Language. Everything is generated from the record — the same modules
    the CLI drives, to a tempfile, read back, recoloured, never redrawn.

    THE PLAN SHEET DEFAULTS TO THE PRESENTATION REGISTER HERE AND TO THE WORKING ONE IN
    `render_plan.render`, AND THE SPLIT IS DELIBERATE. `render()`'s default is the
    conservative direction for a machine: a caller that does not choose keeps every
    disclosure it had, so no count and no mark can vanish through a default argument. This
    is the surface a PERSON reads, and the reader's sheet is the clean one -- the drawing
    and its names, with the disclosures set in the title block below the border where a
    draughtsman puts a note. A caller asks for `working` to get the dimension strings, the
    divergence marks and the relaxation triangles back onto the field."""
    import os as _os
    import tempfile

    from . import svg_theme

    B = _os.path.join(ROOT, "build")
    plan = core.copy_json(plan)
    # core.load_parti, never a join of our own: `parti` is a caller-supplied string from a
    # POST body and this was one of two unsanitised copies. See core.load_parti's docstring.
    pt = core.load_parti(parti)

    def _tmp():
        fd, p = tempfile.mkstemp(suffix=".svg")
        _os.close(fd)
        return p

    out_path = _tmp()
    meta = {}
    try:
        if kind == "plan":
            # WP-6.3: `auto`, not `heuristic`. This endpoint produces the SHEET — the thing
            # a reader looks at and judges the house by — and on the shipped Tidewater plan
            # the heuristic draws a kitchen with none of its five interior doors while the
            # CP engine draws all of them. A drawing is the wrong place to spend
            # correctness to save seconds. WP-6.4 moved the solve into `_placed` so the
            # section beside this sheet is a section of THIS house.
            solved = _placed(plan, pt, candidates)
            if "error" in solved:
                return _forward(solved)
            rp = core._mod("render_plan", f"{B}/render_plan.py")
            rp.render(solved, out_path, register=register)
            # the solver's own account travels with the drawing: a sheet a reader may print
            # has to be able to say whether its placement was proved or searched
            meta = {"relaxations": solved["geometry_report"].get("relaxations"),
                    "solver": solved["geometry_report"].get("solver")}
        elif kind == "elevation":
            # WP-12.0: the SAME placement the plan sheet draws, as the section and bearing
            # sheets below have taken since WP-6.4 -- and this branch did not. It called
            # `build_elevation(plan, pt)` with no section, so the elevation fell into
            # `build_section`'s heuristic default, whose own comment says that default is
            # "for INTERNAL callers ONLY" (plan_check's elevation layer, the composer's
            # scoring loop). The elevation READS placement, so wherever the set's own solve
            # reached a proof the elevation was a drawing of a different house -- under a
            # banner WP-6.4 wrote saying "one drawing set is one building or it is nothing."
            #
            # MEASURED on spec-builder-colonial before the fix: the plan sheet proved
            # 50.0 x 31.0 with CP-SAT while the elevation was built on a heuristic placement,
            # and `porch_clear_depth_ft` -- the measurement `porch-too-shallow-to-inhabit`
            # reads, this project's own Four-Foot Porch -- published 4.75 ft for a porch the
            # plan beside it drew at 4.0. A fault measurement wrong in the flattering
            # direction, which is the OQ 52 family. On tidewater-georgian-careful the two
            # AGREED, because `auto` spends its budget there and falls back to the same
            # heuristic: invisible on one shipped plan and real on the other.
            EL = core._mod("elevation", f"{B}/elevation.py")
            ST_ = core._mod("structure", f"{B}/structure.py")
            RF_ = core._mod("roof", f"{B}/roof.py")
            placed = _placed(plan, pt, candidates)
            if "error" in placed:
                return _forward(placed)
            section = ST_.build_section(plan, pt, geometry_result=placed)
            if "error" in section:
                return {"error": section["error"]}
            roof = RF_.build_roof(plan, pt, section=section)
            if "error" in roof:
                return {"error": roof["error"]}
            elev = EL.build_elevation(plan, pt, section=section, roof=roof)
            if "error" in elev:
                return {"error": elev["error"]}
            re_ = core._mod("render_elevation", f"{B}/render_elevation.py")
            re_.render_elevation(elev, out_path, face=face)
            meta = {"entrance_face": elev.get("entrance_face"),
                    "date_of_representation": elev.get("date_of_representation"),
                    "glass_module_in": elev.get("glass_module_in"),
                    # the engine and the input digest, as the plan sheet has carried since
                    # WP-11.8: a reader comparing two plates of "the same house" can now tell
                    # whether the INPUT differed (finding J6 of the 4 Sep diagnosis).
                    "solver": (placed.get("geometry_report") or {}).get("solver")}
        elif kind in ("section", "bearing"):
            st = core._mod("structure", f"{B}/structure.py")
            # WP-6.4: hand it the SAME placement the plan sheet draws. `build_section`'s own
            # heuristic default is for its internal callers (plan_check's elevation layer,
            # the composer's scoring loop); a user-facing sheet is not one of those, and
            # taking that default here shipped a section of a different house.
            placed = _placed(plan, pt, candidates)
            if "error" in placed:
                return _forward(placed)
            section = st.build_section(plan, pt, geometry_result=placed)
            if "error" in section:
                return {"error": section["error"]}
            rs = core._mod("render_section", f"{B}/render_section.py")
            if kind == "section":
                rs.render_section(section, out_path)
            else:
                rs.render_bearing_diagram(section, out_path)
        elif kind == "roof":
            # WP-12.0, the same defect as the elevation branch above: `build_roof` was called
            # with no section, so it built its own on the heuristic while the plan sheet in
            # the same set was a proof. The roof's ridge, eave and chimney heights all come
            # off that section.
            rf = core._mod("roof", f"{B}/roof.py")
            st_ = core._mod("structure", f"{B}/structure.py")
            placed = _placed(plan, pt, candidates)
            if "error" in placed:
                return _forward(placed)
            section = st_.build_section(plan, pt, geometry_result=placed)
            if "error" in section:
                return {"error": section["error"]}
            roof = rf.build_roof(plan, pt, section=section)
            if "error" in roof:
                return {"error": roof["error"]}
            rr = core._mod("render_roof", f"{B}/render_roof.py")
            rr.render_roof(roof, out_path)
            meta = {"solver": (placed.get("geometry_report") or {}).get("solver")}
        else:
            return {"error": f"unknown drawing kind '{kind}'",
                    "kinds": ["plan", "elevation", "section", "bearing", "roof"]}
        svg = open(out_path).read()
    except SystemExit as e:  # render_plan raises SystemExit on an unsolved plan
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:300]}"}
    finally:
        try:
            _os.unlink(out_path)
        except OSError:
            pass
    if kind == "plan":
        meta["register"] = register
    return {"kind": kind, "svg": svg_theme.retokenize(svg), **meta}


# ----------------------------------------------------------------- the scene (WP-12.3)

# The six views that HAVE a plate. `AXON` and `APPROACH` are named views of the model with no
# orthographic drawing behind them, and the PRD says so rather than inventing one: a perspective
# has no plate because a perspective dimension is never true.
SCENE_PLATES = (("plan", None), ("elevation", "S"), ("elevation", "N"),
                ("elevation", "E"), ("elevation", "W"), ("roof", None))


def rooms_meta(plan):
    """Per-room-type catalogue facts the overlays draw from — privacy rank, plumbing, the
    daylight depth multiplier, and the furniture the client could not otherwise draw.

    LIFTED OUT OF `evaluate.py` BY WP-12.5, because the Round needs the same dict and the
    scene route is a different call. A second copy is how two surfaces of one house come to
    disagree about which rooms are wet — and the analytic rules that READ this dict were
    themselves two copies until the same package lifted them into `overlayRules.js`.

    Joined here so the client never re-derives corpus data: `daylight.depth_multiplier` is
    carried through as-is, INCLUDING a stated zero, which three records use to say the room
    takes no daylight depth at all and which a `or` in this loop would have turned into a
    missing value."""
    D = core._data()
    meta = {}
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            t = r.get("type")
            if t and t not in meta:
                room = D["rooms"].get(t) or {}
                meta[t] = {
                    "function_class": room.get("function_class"),
                    "privacy_rank": room.get("privacy_rank"),
                    "plumbing": (room.get("servicing") or {}).get("plumbing"),
                    "daylight_multiplier": (room.get("daylight") or {}).get("depth_multiplier"),
                    "furniture": [
                        {"item": f.get("item"), "footprint_in": f.get("footprint_in"),
                         "clearance_in": f.get("clearance_in"), "essential": f.get("essential")}
                        for f in (room.get("furniture") or [])
                        if f.get("footprint_in")
                    ],
                }
    return meta


def scene(plan, parti=None, candidates=250, plates=True):
    """The constructed-3D record for the Round, with the PLACED record and every named view's
    plate beside it — deliberately ONE metered call rather than seven.

    IT IS NOT A SIXTH DRAWING KIND. `/api/drawings/{kind}` returns an SVG and this returns a
    record; `test_unknown_kind_names_the_kinds` uses `axonometric` as its negative fixture and
    stays true, which it would not if a camera were smuggled into that enum.

    WHY EVERYTHING COMES BACK AT ONCE, AND THE MEASUREMENT THAT DECIDED IT (WP-12.3). The Round
    has six views that carry a plate. Fetched one at a time beside the scene that is SEVEN calls
    against `limits.heavy_calls_per_hour()`, which is 60 — eight record changes an hour, for a
    surface whose whole subject is moving between views of one house. Measured on
    `tidewater-georgian-careful`:

        a cold solve                              37.48 s
        a record that already carries geometry     0.00 s   (the short-circuit, not the cache)
        all six plates on the placed record        0.38 s
        build_scene on the placed record           0.00 s
        the whole call, end to end               38.46 s
        scene + plates + placed record            70,702 bytes gzipped (376,574 raw)

    The last row of timings is the one to quote: the section, the roof, the elevation, the scene,
    the six plates AND the first-call module loads are the 0.98 s between it and the solve --
    **2.6% of the placement**. So the budget rather than the clock is what bites. One call buys
    sixty record changes an hour where seven calls buy eight.

    **THE SIZE ROW IS WP-12.3's AND IS NOW WRONG TWICE OVER (re-measured WP-12.8).** The TIME
    claim stands: end to end 39.00 s against a solve that is almost all of it. The BYTES do not.
    Measured on the same plan on this tree: **621,870 raw and 97,442 gzipped**, of which the
    scene record alone is 270,029 raw against WP-12.3's 64,928 -- WP-12.6 dressed the envelope
    and WP-12.7 added the doorcase and the stoop, taking 101 solids to 500, and 350 of the 500
    are muntins. Two separate corrections in one row:

      - the published 70,702 was gzip level **6** and `app.GZipExceptSSE` deploys level **4**,
        so the wire figure was never the server's; at level 4 the old payload is 85,115.
      - "about 71 KB on the wire" is **95 KB** now.

    And the 2.6% must not be read as a claim about SIZE, which is the trap in quoting it beside
    the row above: the placed record is 57,957 of 621,870 raw bytes, so **ninety per cent of
    this response is everything-but-the-placement** while under three per cent of its time is.
    One number, two questions, opposite answers.

    THE PLACED RECORD COMES BACK FOR A SECOND REASON. `_placed` returns a record carrying
    `geometry` untouched, so a client that keeps this one and posts it to a later export or
    evaluate pays 0.00 s where a fresh record pays 37.48 s. That is not a cache: it is the
    drawing set's own rule (WP-6.4) — one placement, and every surface that reads it is reading
    the same building.

    `plates=False` returns the scene alone. Both branches are driven by
    `workbench/server/tests/test_scene_endpoint.py`, because a knob nobody exercises is a branch
    nobody tests.
    """
    # A PARTI IS AN ID HERE, NEVER A RECORD (WP-9.4), and the refusal is `core.critique_plan`'s
    # own words. A caller-supplied record becomes the template `geometry` reads its bay module
    # off, which is how 114 bays of half a foot reached the solver through two bench routes.
    if parti is not None and not isinstance(parti, str):
        return {"error": "parti must be a parti id, not a record",
                "detail": type(parti).__name__}
    pt = core.load_parti(parti)
    placed = _placed(plan, pt, candidates)
    if "error" in placed:
        return _forward(placed)
    # `B` is a LOCAL in each of the three functions that need it, not a module name -- and so is
    # `_os`, which those three alias with their own `import os as _os`. The first draft of this
    # function borrowed both from a neighbour and raised `NameError` twice; `os` is imported
    # plainly at module scope and is what this uses. Both were caught by the tests on their first
    # two runs, which is what they are for -- and neither would have been caught by reading, because
    # the surrounding functions read exactly as though the names were module-level.
    B = os.path.join(ROOT, "build")
    ST_ = core._mod("structure", f"{B}/structure.py")
    RF_ = core._mod("roof", f"{B}/roof.py")
    EL_ = core._mod("elevation", f"{B}/elevation.py")
    SC_ = core._mod("scene", f"{B}/scene.py")
    try:
        section = ST_.build_section(placed, pt, geometry_result=placed)
        if "error" in section:
            return {"error": section["error"]}
        roof = RF_.build_roof(placed, pt, section=section)
        if "error" in roof:
            return {"error": roof["error"]}
        # A REFUSED ELEVATION IS NOT AN ERROR HERE, and `build_scene` is written for it: outside
        # the classical-front family the generator declines, and the scene then carries one
        # `not_modelled` entry saying no face states an opening rather than failing. Passing
        # `None` is `scene._build_from_plan`'s own reading of the same refusal.
        elev = EL_.build_elevation(placed, pt, section=section, roof=roof)
        rec = SC_.build_scene(placed, section, roof, None if "error" in elev else elev)
    except Exception as e:                      # noqa: BLE001 -- a refusal is content
        return {"error": f"{type(e).__name__}: {str(e)[:300]}"}
    # THE OVERLAYS NEED THE CATALOGUE AND THIS ROUTE IS THE ONLY CALL THE ROUND MAKES.
    # Without it `meta` reaches the viewer as undefined and every wash comes back empty while
    # looking exactly like an overlay that works: no privacy rank resolves, `isWet` is false
    # for every room, and the daylight reach silently falls back on every one. A surface that
    # draws nothing is indistinguishable from a house with nothing to draw.
    out = {"scene": rec, "plan": placed,
           "rooms_meta": rooms_meta(placed),
           "solver": (placed.get("geometry_report") or {}).get("solver")}
    if plates:
        drawn, refused = {}, {}
        for kind, face in SCENE_PLATES:
            key = f"{kind}:{face}" if face else kind
            # THE ID AND NOT THE RESOLVED RECORD. `drawing()` calls `core.load_parti` itself,
            # and that function takes a caller's STRING: handed a dict it does
            # `os.path.basename(str(dict))`, finds no such file and returns None — so every
            # plate would have been drawn with NO PARTI while the scene beside it used one.
            # Two different buildings in one response, which is the defect WP-12.0 removed one
            # layer up. Found by reading `load_parti`'s signature, not by running it.
            got = drawing(kind, placed, parti=parti, face=face, candidates=candidates)
            # A PLATE THAT COULD NOT BE DRAWN IS NAMED, NEVER DROPPED. An elevation refuses
            # outside the classical-front family and a roof refuses where the style states no
            # migrated pitch; a missing key would read to the viewer as a view it has not
            # fetched yet, which is the one thing it must not read as.
            if "error" in got:
                refused[key] = got["error"]
            else:
                # THE WHOLE RESULT, NOT JUST THE SVG. A plate is its drawing AND the things the
                # drawing does not say for itself -- WP-3.2's photograph-measurable disclosure,
                # which face the record calls the entrance front, the relaxation count, and
                # WP-11.8's engine-and-input-digest line. WP-12.4 first stored `got["svg"]` here
                # and the bench's elevation lost every one of them: the plate looked right and
                # had stopped disclosing, which is the failure this surface exists not to have.
                # The browser walk caught it, on the two checks that read the caption.
                drawn[key] = got
        out["plates"] = drawn
        out["plates_refused"] = refused
    return out


def export_cad(fmt, plan, kind=None, parti=None, face=None, candidates=250):
    """WP-5.1: run build/export_dxf.py or build/export_ifc.py for one plan and
    return the file's text (DXF and IFC-SPF are both text formats). Refusals —
    a missing optional library, an elevation outside the classical-front
    family — come back stated with `unexported`/`refusal`, never collapsed
    into an empty file."""
    import os as _os
    import tempfile

    B = _os.path.join(ROOT, "build")
    plan = core.copy_json(plan)
    # core.load_parti, never a join of our own — see its docstring.
    pt = core.load_parti(parti)
    pid = plan.get("id", "plan")

    try:
        with tempfile.TemporaryDirectory() as td:
            if fmt == "ifc":
                # WP-13.4: THIS ROUTE DID NOT GO THROUGH `_placed`. It handed the DECLARED
                # plan to `export_ifc`, which called `structure.build_section` with no
                # `geometry_result` and took that function's heuristic default -- the one its
                # own comment reserves for "INTERNAL callers ONLY" (plan_check's elevation
                # layer, the composer's scoring loop). So the IFC a reader downloaded was a
                # placement of a different house from the plan sheet beside it, which is
                # exactly WP-6.4's finding surviving in the one export branch nobody moved,
                # and it also meant the refusal could not reach here at all.
                EI = core._mod("export_ifc", f"{B}/export_ifc.py")
                p = _os.path.join(td, "out.ifc")
                placed = _placed(plan, pt, candidates)
                if "error" in placed:
                    return placed
                res = EI.export_ifc(plan, p, pt, geometry_result=placed)
                if "error" in res:
                    return res
                return {"format": "ifc", "filename": f"{pid}.ifc", "text": open(p).read(),
                        "counts": res["counts"], "units": res["units"], "schema": res["schema"]}
            if fmt == "dxf":
                EX = core._mod("export_dxf", f"{B}/export_dxf.py")
                kind = kind or "plan"
                p = _os.path.join(td, "out.dxf")
                # WP-6.4: the exported sheet is a sheet of the house on screen. Both of
                # these used to place the plan for themselves on the weaker engine, so a
                # downloaded DXF was a different placement from the SVG the reader was
                # looking at when they pressed the button.
                if kind == "plan":
                    placed = _placed(plan, pt, candidates)
                    if "error" in placed:
                        return placed
                    res = EX.export_plan_dxf(placed, p, pt, candidates)
                elif kind == "section":
                    st = core._mod("structure", f"{B}/structure.py")
                    placed = _placed(plan, pt, candidates)
                    if "error" in placed:
                        return placed
                    section = st.build_section(plan, pt, geometry_result=placed)
                    res = section if "error" in section else EX.export_section_dxf(section, p)
                elif kind == "roof":
                    # WP-12.0: the exported sheet is a sheet of the house on screen, which
                    # is WP-6.4's rule and which the section branch above already keeps.
                    # These two took `build_section`'s internal heuristic default instead.
                    rf = core._mod("roof", f"{B}/roof.py")
                    st = core._mod("structure", f"{B}/structure.py")
                    placed = _placed(plan, pt, candidates)
                    if "error" in placed:
                        return placed
                    section = st.build_section(plan, pt, geometry_result=placed)
                    if "error" in section:
                        return section
                    roof = rf.build_roof(plan, pt, section=section)
                    res = roof if "error" in roof else EX.export_roof_dxf(roof, p)
                elif kind == "elevation":
                    EL = core._mod("elevation", f"{B}/elevation.py")
                    st = core._mod("structure", f"{B}/structure.py")
                    rf = core._mod("roof", f"{B}/roof.py")
                    placed = _placed(plan, pt, candidates)
                    if "error" in placed:
                        return placed
                    section = st.build_section(plan, pt, geometry_result=placed)
                    if "error" in section:
                        return section
                    roof = rf.build_roof(plan, pt, section=section)
                    if "error" in roof:
                        return roof
                    elev = EL.build_elevation(plan, pt, section=section, roof=roof)
                    res = elev if "error" in elev else EX.export_elevation_dxf(elev, p, face)
                else:
                    return {"error": f"unknown DXF sheet kind '{kind}'",
                            "kinds": ["plan", "section", "roof", "elevation"]}
                if "error" in res:
                    return res
                suffix = res.get("sheets", kind)
                return {"format": "dxf", "kind": kind,
                        "filename": f"{pid}-{suffix}.dxf", "text": open(p).read()}
            return {"error": f"unknown export format '{fmt}'", "formats": ["dxf", "ifc"]}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:300]}"}


def ingest_dxf(dxf_text, units=None):
    """WP-5.5: a drafter's DXF (sent as text) -> room candidates + named gaps
    for the Transcription surface to complete; a TDL-emitted sheet comes back
    a complete record. All the judgment lives in build/ingest_dxf.py."""
    import os as _os
    import tempfile

    B = _os.path.join(ROOT, "build")
    ING = core._mod("ingest_dxf", f"{B}/ingest_dxf.py")
    fd, p = tempfile.mkstemp(suffix=".dxf")
    try:
        with _os.fdopen(fd, "w") as f:
            f.write(dxf_text)
        return ING.extract(p, units)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:300]}"}
    finally:
        try:
            _os.unlink(p)
        except OSError:
            pass


def invalidate():
    """Drop every cache so on-disk corpus edits are seen. Explicit by design:
    auto-invalidation per request would reintroduce the OQ-28 tax."""
    import modcache
    modcache.invalidate()
    core._data.cache_clear()
    core.schema.cache_clear()          # the parsed plan/brief schemas
    core._all_partis.cache_clear()     # the 21 parsed parti records
    # citations' two id sets were missed by the first version of this function, so
    # /api/dev/reload left a newly added parti uncitable for the life of the process — the
    # rail would downgrade [[cite:parti:new-one]] to plain text and say nothing.
    from . import citations
    citations._parti_ids.cache_clear()
    citations._constraint_ids.cache_clear()
    # AND THE THIRD MISS OF THE SAME KIND, found by the WP-8.4 adversarial audit. That
    # package added `_kit_graph` and `_resolved_kit` to core.py and did not add them here, so
    # after a reload every fault-exception precondition was still resolved against the
    # PRE-EDIT kit graph for the life of the process: the bench showed an author's change to
    # `styles/pueblo-revival.json` everywhere except in whether a licence was granted on it,
    # and nothing said the verdict was stale. `_kit_graph` additionally pinned the
    # pre-invalidate `resolve_kit` module object, so two of them were live at once.
    #
    # THE PATTERN IS THE FINDING: every lru_cache added to core.py has to be added here, and
    # three of the five have been missed on their way in. `test_reload_clears_every_cache`
    # walks core's own module dict instead of naming them, so a fourth cannot be missed.
    core._kit_graph.cache_clear()
    core._resolved_kit.cache_clear()
    core.validator.cache_clear()       # the COMPILED plan/brief validators, which hold the
                                       # schema dicts cleared two lines above: clearing the
                                       # parse and not the validator built from it would leave
                                       # a reload validating against the pre-edit schema.
    reset_search_index()
    return {"reloaded": True}
