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


def proportions_with_members(pack_id, column_diameter=None, module=None,
                             ceiling_height=108.0, opening_width=36.0):
    """core.get_proportions plus full member lists for EVERY assembly — the plate
    drawing needs the whole stack at once, and the API's one-assembly-at-a-time
    shape (right for an agent's context budget) would cost seven round-trips."""
    out = core.get_proportions(pack_id, column_diameter=column_diameter, module=module,
                               ceiling_height=ceiling_height, opening_width=opening_width)
    if "error" in out:
        return out
    pe = core._data()["engine"]
    pk = pe.resolve(pack_id)
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
    """
    if any("geometry" in r for lv in plan.get("levels", []) for r in lv["rooms"]):
        return plan
    geo = core._mod("geometry", os.path.join(ROOT, "build", "geometry.py"))
    return geo.solve(plan, parti, candidates, engine="auto")


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
                return {"error": solved["error"]}
            rp = core._mod("render_plan", f"{B}/render_plan.py")
            rp.render(solved, out_path, register=register)
            # the solver's own account travels with the drawing: a sheet a reader may print
            # has to be able to say whether its placement was proved or searched
            meta = {"relaxations": solved["geometry_report"].get("relaxations"),
                    "solver": solved["geometry_report"].get("solver")}
        elif kind == "elevation":
            EL = core._mod("elevation", f"{B}/elevation.py")
            elev = EL.build_elevation(plan, pt)
            if "error" in elev:
                return {"error": elev["error"]}
            re_ = core._mod("render_elevation", f"{B}/render_elevation.py")
            re_.render_elevation(elev, out_path, face=face)
            meta = {"entrance_face": elev.get("entrance_face"),
                    "date_of_representation": elev.get("date_of_representation"),
                    "glass_module_in": elev.get("glass_module_in")}
        elif kind in ("section", "bearing"):
            st = core._mod("structure", f"{B}/structure.py")
            # WP-6.4: hand it the SAME placement the plan sheet draws. `build_section`'s own
            # heuristic default is for its internal callers (plan_check's elevation layer,
            # the composer's scoring loop); a user-facing sheet is not one of those, and
            # taking that default here shipped a section of a different house.
            placed = _placed(plan, pt, candidates)
            if "error" in placed:
                return {"error": placed["error"]}
            section = st.build_section(plan, pt, geometry_result=placed)
            if "error" in section:
                return {"error": section["error"]}
            rs = core._mod("render_section", f"{B}/render_section.py")
            if kind == "section":
                rs.render_section(section, out_path)
            else:
                rs.render_bearing_diagram(section, out_path)
        elif kind == "roof":
            rf = core._mod("roof", f"{B}/roof.py")
            roof = rf.build_roof(plan, pt)
            if "error" in roof:
                return {"error": roof["error"]}
            rr = core._mod("render_roof", f"{B}/render_roof.py")
            rr.render_roof(roof, out_path)
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
                EI = core._mod("export_ifc", f"{B}/export_ifc.py")
                p = _os.path.join(td, "out.ifc")
                res = EI.export_ifc(plan, p, pt)
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
                    rf = core._mod("roof", f"{B}/roof.py")
                    roof = rf.build_roof(plan, pt)
                    res = roof if "error" in roof else EX.export_roof_dxf(roof, p)
                elif kind == "elevation":
                    EL = core._mod("elevation", f"{B}/elevation.py")
                    elev = EL.build_elevation(plan, pt)
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
    reset_search_index()
    return {"reloaded": True}
