#!/usr/bin/env python3
"""Export a plan record as an IFC4 model (WP-5.1): walls, slabs, openings, roof
and spaces, every product carrying its TDL ids in a "TDL" property set so a
BIM tool can trace any element back to the record it renders.

The model is generated from the same records the drawing set renders from —
geometry.solve() placement, structure.build_section() walls/storeys/thickness,
roof.build_roof() form — never re-derived. Lengths are in FEET (a
conversion-based unit on the project; falls back to SI metres, stated in the
result, if the unit API refuses).

What is honestly NOT modelled, stated per element in its own Pset rather than
silently absent:
  * roof geometry beyond the plain gable family — a hip/gambrel/cross roof is
    an IfcRoof entity with its form, pitch and ridge heights as properties and
    a `geometry_note` naming the gap, not a guessed solid;
  * a window whose record states no height — the IfcWindow exists, carries its
    record, and says why it has no body;
  * chimneys, stairs, trim — outside this package's scope (see the WP report);
  * the ROOF is still derived for the main block alone — a multi-element house
    gets a slab per element (WP-11.6) and one roof, with no stated ridge
    relation per element. That is ruling 1's second half and it is unbuilt.

Wall placement: exterior walls sit with their inner face on the clear-dimension
boundary (the record's rooms are clear dims; outside-to-outside = clear + 2t,
structure.py's own convention); interior walls are centred on their shared line.

Honest refusals: without ifcopenshell installed every entry point returns
{"error": "could not export: …", "unexported": True}, and `selftest` exits 3,
which check_all.py reports as COULD NOT EVALUATE, never as passed.

    python3 build/export_ifc.py plans/tidewater-georgian-careful.json --out dist/ifc/tidewater.ifc
    python3 build/export_ifc.py selftest
"""
import argparse
import copy
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _mod(n, p):
    # Delegates to build/modcache.py — one module execution per process (OQ 28).
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(n, p)

REFUSAL = {"error": "could not export: the ifcopenshell package is not installed "
                    "(pip install ifcopenshell). Nothing was written.",
           # "refusal" = COULD NOT EVALUATE (missing dep), never a real failure
           "unexported": True, "refusal": True}

GABLE_FORMS = ("gable", "side-gable", "front-gable")


def slab_boxes(plan, section, t_ext):
    """One slab per (storey, massing element), as plain numbers (WP-11.6, layer 6 of 6).

    Ruling 1 of `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`:
    *"an element has its own envelope ... `export_ifc` a slab per element"*. Until this there was
    ONE slab per storey, sized `W + 2t` by `D + 2t` on the MAIN BLOCK and centred on it, while
    every `IfcSpace` is placed from its room's own ABSOLUTE rectangle -- so a dependency room's
    space floated clear of every slab in the model. Measured on the reference fixture: the main
    slab spans x[-1.29, 64.29] and three placed rooms sit at x[-41.0, -14.0].

    IT IS PURE ARITHMETIC AND THAT IS THE POINT. `ifcopenshell` is optional and this environment
    does not have it, so the export's own selftest reports COULD NOT EVALUATE and a slab rule
    written inside the writer could not be measured here at all -- the layer would have been
    "fixed" against a check that never ran. The geometry is computed where a test can read it and
    emitted where it cannot.

    AN ELEMENT GETS A SLAB ON A STOREY ONLY WHERE A ROOM OF THAT ELEMENT IS PLACED ON IT.
    `blocks_for` lays only level 0 into elements, so a dependency has a ground slab and no upper
    one -- that is the building rather than an omission, and it is why this reads the rooms rather
    than crossing every element with every storey.

    A one-rectangle plan carries no `footprint.blocks`, so every room falls to `main`, the box
    falls back to the footprint scalars, and the returned list is one entry per storey with the
    same numbers the single-slab loop produced. Byte-identical by construction, not by a branch.

    Returns `[{level, element, width_ft, depth_ft, cx, cy, thickness_ft, grade_to_floor_ft}]`,
    main block first on each storey."""
    # THE ELEMENTS AND THE ROOMS ARE THE SECTION'S PLACEMENT'S (audit, 27 Sep 2026), as the
    # footprint already was: this read both off `plan`, which a product caller hands placed on a
    # record's first request and declared after it (`geometry.solve` writes into its argument on a
    # cache miss only), so the IFC's slabs depended on the cache -- one slab per storey on a warm
    # request, a dependency slab missing, and the dependency's rooms over nothing. `plan` stays in
    # the signature for its callers; nothing in it is read here.
    geo = section["geometry"]
    fp = geo["footprint"]
    W, D = fp["width_ft"], fp["depth_ft"]
    blocks = {b["id"]: b for b in (fp.get("blocks") or [])}
    GEOM = _mod("geometry", os.path.join(ROOT, "build", "geometry.py"))
    on_level = {}
    for lv in geo.get("levels", []):
        idx = lv.get("index", 0)
        for r in lv.get("rooms", []):
            if not r.get("geometry"):
                continue
            tag = r.get("block") if GEOM.is_block_tag(r.get("block")) else None
            # A tag naming an element the placer did not build is read as the main block, which
            # is `is_block_tag`'s own conservative answer one layer up rather than a new rule.
            on_level.setdefault(idx, set()).add(tag if tag in blocks else "main")
    out = []
    for st in section.get("storeys", []):
        idx = st.get("index")
        if st.get("storey_height_ft") is None or (idx or 0) < 0:
            continue
        thick = (st.get("floor_structure_depth_in") or 10.0) / 12.0
        for el in sorted(on_level.get(idx) or {"main"}, key=lambda e: (e != "main", e)):
            b = blocks.get(el)
            bx, by, bw, bd = ((b["x_ft"], b["y_ft"], b["width_ft"], b["depth_ft"])
                              if b else (0.0, 0.0, W, D))
            out.append({"level": idx, "element": el,
                        "width_ft": bw + 2 * t_ext, "depth_ft": bd + 2 * t_ext,
                        "cx": bx + bw / 2.0, "cy": by + bd / 2.0,
                        "thickness_ft": thick,
                        "grade_to_floor_ft": float(st["grade_to_floor_ft"])})
    return out


def _ifc():
    try:
        import ifcopenshell
        import ifcopenshell.api
        return ifcopenshell
    except ImportError:
        return None


def _run(_usecase, _file, **kw):
    # underscored positionals so callers' name=/file= kwargs cannot collide
    import ifcopenshell.api
    return ifcopenshell.api.run(_usecase, _file, **kw)


def _pset(f, product, props):
    ps = _run("pset.add_pset", f, product=product, name="TDL")
    _run("pset.edit_pset", f, pset=ps,
         properties={k: v for k, v in props.items() if v is not None})


def _placement(f, product, xyz, rot_z_deg=0.0):
    """`xyz` is in the PROJECT's unit -- the record's feet, or in the stated SI fallback the same
    feet values, as that fallback's note says.

    `is_si=False`, AND ITS ABSENCE HAD PUT EVERY PRODUCT OF EVERY MODEL AT 3.28 TIMES ITS PLACE
    (audit, 27 Sep 2026). `geometry.edit_object_placement` defaults to `is_si=True`: it reads the
    matrix as METRES and converts it into the project's unit, so a coordinate in feet was divided
    by 0.3048 on its way into the file. Every body (`_box`, a profile in the record's own feet) is
    the right size and every placement is 3.2808 times too far from the origin -- measured on
    `spec-builder-colonial`, the Foyer's centre (6.75, 27.72) ft written at (22.13, 90.93). A
    model of scattered, correctly-sized pieces, and the storey's `Elevation` (set directly, in
    feet) disagreeing with its own placement. Since this function was written, and invisible to
    every guard: the selftest counts entities and ids, the ids test reads the pset, and the one
    test comparing opening and wall reads them RELATIVE to each other, where a uniform scale
    cancels. `tests/test_ifc_openings_are_the_sheets.py` reads placements against the record now.
    """
    import numpy as np
    m = np.eye(4)
    if rot_z_deg:
        a = math.radians(rot_z_deg)
        m[0][0], m[0][1] = math.cos(a), -math.sin(a)
        m[1][0], m[1][1] = math.sin(a), math.cos(a)
    m[0][3], m[1][3], m[2][3] = xyz
    _run("geometry.edit_object_placement", f, product=product, matrix=m, is_si=False)


def _box(f, body_ctx, product, w, d, h):
    """A w x d x h box, its own origin at the centre of its w x d base."""
    profile = f.createIfcRectangleProfileDef("AREA", None, None, w, d)
    direction = f.createIfcDirection((0.0, 0.0, 1.0))
    solid = f.createIfcExtrudedAreaSolid(profile, None, direction, h)
    shape = f.createIfcShapeRepresentation(body_ctx, "Body", "SweptSolid", [solid])
    product.Representation = f.createIfcProductDefinitionShape(None, None, [shape])


def export_ifc(plan, path, parti=None, geometry_result=None):
    """`geometry_result` is the drawing set's ONE placement, and a user-facing caller must
    pass it (WP-13.4).

    Without it `build_section` takes its own heuristic default, which that function's comment
    reserves for INTERNAL callers -- plan_check's elevation layer and the composer's scoring
    loop. `workbench/server/corpus.export_cad` was not one of those and took it anyway, so the
    IFC a reader downloaded was a placement of a different house from the plan sheet they were
    looking at when they pressed the button: WP-6.4's "one drawing set is one building"
    surviving in the one export branch that was never moved. It also meant the refusal to draw
    could not reach this format at all, because nothing here ever went through `_placed`.

    The default stays `None` for the CLI and the selftest below, which place for themselves."""
    ios = _ifc()
    if ios is None:
        return dict(REFUSAL)
    # THE CLI AND LIBRARY PATH REFUSES WHAT THE SHEET REFUSES (audit, 27 Sep 2026). With no
    # placement handed, this took `build_section`'s internal heuristic default and judged nothing:
    # `export_ifc(<the Tidewater record>)` wrote 50 walls, 4 slabs and 24 spaces of a placement
    # the same record's plan sheet, DXF and heuristic verdict all refuse. It takes the DXF's own
    # `_solved_copy` now -- the one spelling of "place for export and refuse", on the engine the
    # bench draws with -- so the CLI's two CAD files are one building and one verdict.
    if geometry_result is None:
        EX = _mod("export_dxf", f"{ROOT}/build/export_dxf.py")
        _orig, geometry_result = EX._solved_copy(plan, parti)
        if "error" in geometry_result:
            return dict(geometry_result, unexported=True)
    ST = _mod("structure", f"{ROOT}/build/structure.py")
    RF = _mod("roof", f"{ROOT}/build/roof.py")
    section = ST.build_section(copy.deepcopy(plan), parti, geometry_result=geometry_result)
    if "error" in section:
        return {"error": section["error"], "unexported": True}
    roof = RF.build_roof(copy.deepcopy(plan), parti, section=section)
    roof_ok = "error" not in roof

    f = ios.file(schema="IFC4")
    pid, style = plan.get("id", "plan"), plan.get("style")
    project = _run("root.create_entity", f, ifc_class="IfcProject",
                   name=f"TDL {plan.get('name', pid)}")
    # lengths in feet, the record's own unit; SI metres only as a stated fallback
    unit_note = "feet (conversion-based unit)"
    try:
        foot = _run("unit.add_conversion_based_unit", f, name="foot")
        _run("unit.assign_unit", f, units=[foot])
    except Exception as e:
        _run("unit.assign_unit", f)
        unit_note = f"SI metres — the foot unit could not be constructed ({type(e).__name__}); NOTE: coordinates are still the record's feet values"
    ctx = _run("context.add_context", f, context_type="Model")
    body = _run("context.add_context", f, context_type="Model",
                context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)

    site = _run("root.create_entity", f, ifc_class="IfcSite", name=f"{pid} site")
    building = _run("root.create_entity", f, ifc_class="IfcBuilding", name=pid)
    _run("aggregate.assign_object", f, products=[site], relating_object=project)
    _run("aggregate.assign_object", f, products=[building], relating_object=site)
    _pset(f, building, {"plan_id": pid, "style": style,
                        "massing": plan.get("massing"),
                        "source": "Traditional-Design-Language plan record"})

    geo = section["geometry"]
    fp = geo["footprint"]
    W, D = fp["width_ft"], fp["depth_ft"]
    wall_rec = section["wall"]
    t_ext = wall_rec["exterior_in"] / 12.0
    t_bear = wall_rec["bearing_interior_in"] / 12.0
    t_part = wall_rec["partition_in"] / 12.0

    storeys = {}
    for st in sorted([s for s in section["storeys"]
                      if s.get("storey_height_ft") is not None and (s.get("index") or 0) >= 0],
                     key=lambda s: s["index"]):
        storey = _run("root.create_entity", f, ifc_class="IfcBuildingStorey",
                      name=st["id"] or f"level {st['index']}")
        storey.Elevation = float(st["grade_to_floor_ft"])
        _run("aggregate.assign_object", f, products=[storey], relating_object=building)
        _placement(f, storey, (0.0, 0.0, float(st["grade_to_floor_ft"])))
        _pset(f, storey, {"plan_id": pid, "style": style, "tdl_id": st["id"],
                          "ceiling_ft": st.get("ceiling_ft"),
                          "storey_height_ft": st.get("storey_height_ft"),
                          "floor_structure_depth_in": st.get("floor_structure_depth_in")})
        storeys[st["index"]] = (storey, st)

    counts = {"walls": 0, "slabs": 0, "spaces": 0, "windows": 0, "doors": 0,
              "windows_without_geometry": 0}

    # ---- slabs: one framed floor per storey AND PER MASSING ELEMENT (WP-11.6 layer 6), its top
    # at the storey's own datum. The geometry is `slab_boxes`, above, so it can be measured in an
    # environment with no ifcopenshell -- which is this one, and every one CI runs.
    for sb in slab_boxes(plan, section, t_ext):
        idx = sb["level"]
        if idx not in storeys:
            continue
        storey, st = storeys[idx]
        # The main block's slab keeps its old name and id EXACTLY; only a second element's
        # carries a suffix, so a one-rectangle model is unchanged down to its tdl ids.
        suffix = "" if sb["element"] == "main" else f" {sb['element']}"
        tdl = f"floor-L{idx}" if sb["element"] == "main" else f"floor-L{idx}-{sb['element']}"
        slab = _run("root.create_entity", f, ifc_class="IfcSlab",
                    name=f"{pid} floor L{idx}{suffix}")
        slab.PredefinedType = "FLOOR"
        _box(f, body, slab, sb["width_ft"], sb["depth_ft"], sb["thickness_ft"])
        _placement(f, slab, (sb["cx"], sb["cy"],
                             sb["grade_to_floor_ft"] - sb["thickness_ft"]))
        _run("spatial.assign_container", f, products=[slab], relating_structure=storey)
        _pset(f, slab, {"plan_id": pid, "style": style, "tdl_id": tdl,
                        "element": sb["element"],
                        "depth_in": st.get("floor_structure_depth_in")})
        counts["slabs"] += 1

    # ---- walls per level, from structure.py's own wall lines
    # EVERY EXTERIOR WALL, WITH ITS FACE AND ITS RUN (audit, 27 Sep 2026). This was a map keyed
    # (level, letter), so on a house of several massing elements the LAST element's W wall hosted
    # every W window of the level; an opening now finds the exterior wall of its letter whose face
    # is the opening's own face and whose run contains it -- `_host`, below.
    exterior_walls = {}   # level -> [(IfcWall, along_axis, cx, cy, z, t, letter, face, lo, hi)]
    for lv in section["levels"]:
        idx = lv.get("index", 0)
        if idx not in storeys:
            continue
        storey, st = storeys[idx]
        z = float(st["grade_to_floor_ft"])
        hgt = float(st["ceiling_ft"])
        for wi, wl in enumerate(lv["walls"]):
            length = wl["hi_ft"] - wl["lo_ft"]
            if length <= 0.1:
                continue
            if wl["role"] == "exterior":
                t = t_ext
            else:
                t = t_bear if wl.get("bearing") else t_part
            wall = _run("root.create_entity", f, ifc_class="IfcWall",
                        name=f"{pid} L{idx} {wl['role']} {wl.get('wall', '')} "
                             f"{wl['axis']}={wl['position_ft']}".strip())
            # axis "x": constant-x wall running along y; axis "y": constant-y along x
            along_y = wl["axis"] == "x"
            w_, d_ = (t, length) if along_y else (length, t)
            _box(f, body, wall, w_, d_, hgt)
            cx = wl["position_ft"] if along_y else (wl["lo_ft"] + wl["hi_ft"]) / 2
            cy = (wl["lo_ft"] + wl["hi_ft"]) / 2 if along_y else wl["position_ft"]
            if wl["role"] == "exterior":
                # inner face on the clear line: shift half a thickness OUTWARD, which is the side
                # the wall's own letter names (audit, 27 Sep 2026). This read `position_ft <= 0.01`,
                # which is the same answer on a one-rectangle house and the wrong one for a
                # dependency's E wall at x = -7: it shifted west, into the dependency. A wall with no
                # compass letter (one facing a court) keeps the old reading.
                letter = wl.get("wall")
                out = ((-t / 2 if letter in ("W", "S") else t / 2) if letter in ("N", "E", "S", "W")
                       else (-t / 2 if wl["position_ft"] <= 0.01 else t / 2))
                if along_y:
                    cx += out
                else:
                    cy += out
            _placement(f, wall, (cx, cy, z))
            _run("spatial.assign_container", f, products=[wall], relating_structure=storey)
            _pset(f, wall, {"plan_id": pid, "style": style,
                            "tdl_id": f"L{idx}-wall-{wi}", "role": wl["role"],
                            "wall": wl.get("wall"), "axis": wl["axis"],
                            "position_ft": wl["position_ft"], "bearing": wl.get("bearing"),
                            "why": wl.get("why"), "thickness_in": round(t * 12, 2),
                            "rooms": ",".join(wl.get("rooms", [])) or None,
                            "construction_type": wall_rec["construction_type"]})
            counts["walls"] += 1
            if wl["role"] == "exterior":
                exterior_walls.setdefault(idx, []).append(
                    (wall, "y" if along_y else "x", cx, cy, z, t, wl.get("wall"),
                     wl["position_ft"], wl["lo_ft"], wl["hi_ft"]))

    def _host(idx, letter, face, along):
        return next((h for h in exterior_walls.get(idx, [])
                     if h[6] == letter and abs(h[7] - face) <= 0.05
                     and h[8] - 0.05 <= along <= h[9] + 0.05), None)

    RP = _mod("render_plan", f"{ROOT}/build/render_plan.py")
    EL_ = _mod("elements", f"{ROOT}/build/elements.py")

    # ---- spaces and their windows/doors, from the solved placement
    for lv in geo["levels"]:
        idx = lv.get("index", 0)
        if idx not in storeys:
            continue
        storey, st = storeys[idx]
        z = float(st["grade_to_floor_ft"])
        bounds = EL_.bounds_index(geo, lv["rooms"])
        for r in lv["rooms"]:
            g = r.get("geometry")
            if not g:
                continue
            hgt = float(r.get("ceiling_ft") or st["ceiling_ft"])
            space = _run("root.create_entity", f, ifc_class="IfcSpace",
                         name=r.get("name") or r["id"])
            _box(f, body, space, g["width_ft"], g["depth_ft"], hgt)
            _placement(f, space, (g["x_ft"] + g["width_ft"] / 2,
                                  g["y_ft"] + g["depth_ft"] / 2, z))
            _run("aggregate.assign_object", f, products=[space], relating_object=storey)
            _pset(f, space, {"plan_id": pid, "style": style, "tdl_id": r["id"],
                             "room_type": r["type"], "area_sf": g.get("area_sf"),
                             "ceiling_ft": r.get("ceiling_ft")})
            counts["spaces"] += 1

            for wi, win in enumerate(r.get("windows") or []):
                wall_letter = win.get("wall")
                cnt = win.get("count") or 1
                w_ft = win.get("width_ft") or 3.0
                h_ft = win.get("height_ft")
                head_ft = r.get("window_head_ft")
                # WHERE THE PLACEMENT SEATS EACH UNIT, AND NOWHERE ELSE (audit, 27 Sep 2026). This
                # spaced every declared unit evenly along the room's edge (`(k + 1) / (cnt + 1)`) on
                # the footprint's outer face, and never read the placed `positions_ft` or the
                # placer's `unplaced` -- measured over the twelve drawable reference plans, 112
                # window units cut against the 57 the plan sheet draws, 55 of them units the placer
                # REFUSED (bad-01 5 against 3, good-03 11 against 2, good-04 9 against 2). A unit is
                # cut where the record seats it, on the face `render_plan._boundary_wall` gives the
                # sheet (the room's own element's), in the exterior wall that face belongs to; a
                # unit the placer refused is carried as data with the placer's own reason.
                seat = RP._boundary_wall(g, wall_letter, W, D, 0.6, bounds.get(r["id"]))
                pos = [float(q) for q in (win.get("positions_ft") or [])] if seat else []
                for k in range(cnt):
                    window = _run("root.create_entity", f, ifc_class="IfcWindow",
                                  name=f"{r['id']} window {wi}.{k}")
                    note, host = None, None
                    if k >= len(pos):
                        why = ((win.get("unplaced") or {}).get("reason")
                               or ("the placement puts this room on no such boundary wall"
                                   if not seat else "the record carries no placed position for it"))
                        note = (f"not placed: {why} — no geometry emitted, the record is carried "
                                f"as data, and the plan sheet draws no sash here either")
                    else:
                        host = _host(idx, wall_letter, seat[3], pos[k])
                        if host is None:
                            note = (f"record names wall '{wall_letter}' but the solved placement "
                                    f"has no exterior wall of that letter on this room's face — no "
                                    f"geometry emitted, the record is carried as data")
                        elif h_ft is None:
                            note = "record states no height_ft — no geometry emitted, not guessed"
                    if note is None:
                        # centred IN its wall, through its whole thickness: the box took the wall's
                        # thickness and stood on the wall's inner face, so it cut only the inner
                        # half of the wall it was meant to pierce (same audit)
                        if wall_letter in ("S", "N"):
                            cx, cy = pos[k], host[3]
                            w_, d_ = w_ft, host[5]
                        else:
                            cx, cy = host[2], pos[k]
                            w_, d_ = host[5], w_ft
                        # the record's own sill_ft first (schema has carried it
                        # since 0.1.0, unused until WP-5.5 noticed), then the
                        # head-minus-height derivation, then an editorial default
                        if win.get("sill_ft") is not None:
                            sill, sill_src = win["sill_ft"], "record sill_ft"
                        elif head_ft:
                            sill, sill_src = head_ft - h_ft, "window_head_ft - height_ft"
                        else:
                            sill, sill_src = 2.5, "editorial default 2.5 ft"
                        opening = _run("root.create_entity", f, ifc_class="IfcOpeningElement",
                                       name=f"{r['id']} opening {wi}.{k}")
                        _box(f, body, opening, w_, d_, h_ft)
                        _placement(f, opening, (cx, cy, z + sill))
                        _run("feature.add_feature", f, feature=opening, element=host[0])
                        _box(f, body, window, w_, d_, h_ft)
                        _placement(f, window, (cx, cy, z + sill))
                        _run("feature.add_filling", f, opening=opening, element=window)
                        _pset(f, window, {"plan_id": pid, "style": style,
                                          "tdl_id": f"{r['id']}-window-{wi}-{k}",
                                          "room": r["id"], "wall": wall_letter,
                                          "width_ft": w_ft, "height_ft": h_ft,
                                          "position_ft": round(pos[k], 3),
                                          "sill_ft": round(sill, 2), "sill_source": sill_src,
                                          "operable": win.get("operable")})
                    else:
                        _pset(f, window, {"plan_id": pid, "style": style,
                                          "tdl_id": f"{r['id']}-window-{wi}-{k}",
                                          "room": r["id"], "wall": wall_letter,
                                          "width_ft": w_ft, "height_ft": h_ft,
                                          "geometry_note": note})
                        counts["windows_without_geometry"] += 1
                    _run("spatial.assign_container", f, products=[window],
                         relating_structure=storey)
                    counts["windows"] += 1

    # ---- interior doors: an IfcDoor per shared-wall door record (drawn once per
    # pair, the plan-render convention); exterior doors carry data, no geometry
    #
    # WHERE THE SHEET HANGS EACH LEAF (audit, 27 Sep 2026). A door stood at the midpoint of the
    # shared run `render_plan._shared` found, which is where a door was drawn before WP-6.2 gave
    # every door a placed position -- measured over the twelve drawable reference plans, 10 of 84
    # interior doors stood somewhere the plan sheet does not draw them, the worst 4.23 ft away
    # (good-02, family to kitchen). The door is read from `render_plan.openings_of_level`, the
    # sheet's own call: its seat where it has one, its refusal, in the placer's words, where not.
    for i_lv, lv in enumerate(geo["levels"]):
        idx = lv.get("index", 0)
        if idx not in storeys:
            continue
        storey, st = storeys[idx]
        z = float(st["grade_to_floor_ft"])
        ops = RP.openings_of_level(geo, lv, i_lv)
        seated = {tuple(sorted(e["pair"])): e for e in ops["interior"]}
        refused = {tuple(sorted((u["from"], u["to"]))): u.get("reason")
                   for u in ops["undrawable"] if u.get("to") != "exterior"}
        drawn = set()
        for r in lv["rooms"]:
            for di, d in enumerate(r.get("doors") or []):
                to = d["to"]
                key = tuple(sorted((r["id"], to)))
                door = _run("root.create_entity", f, ifc_class="IfcDoor",
                            name=f"{r['id']} door to {to}")
                props = {"plan_id": pid, "style": style,
                         "tdl_id": f"{r['id']}-door-{di}", "room": r["id"], "to": to,
                         "width_ft": d.get("width_ft")}
                e = seated.get(key)
                if to == "exterior" or e is None or key in drawn:
                    props["geometry_note"] = (
                        "exterior door — carried as data; this model cuts no exterior door "
                        "opening (the plan sheet and the elevation draw it where the placement "
                        "seats it)" if to == "exterior" else
                        f"not placed: {refused.get(key) or 'no shared wall segment in the solved placement'}"
                        if e is None else
                        "pair already carries the placed leaf")
                else:
                    drawn.add(key)
                    horiz = e["horiz"]
                    px, py = (e["pos_ft"], e["at_ft"]) if horiz else (e["at_ft"], e["pos_ft"])
                    w_ft = e["width_ft"]
                    w_, d_ = (w_ft, t_part) if horiz else (t_part, w_ft)
                    _box(f, body, door, w_, d_, 6.67)
                    _placement(f, door, (px, py, z))
                    props["position_ft"] = round(e["pos_ft"], 3)
                    props["height_ft"] = 6.67
                    props["height_source"] = "editorial default 6 ft 8 in leaf"
                _run("spatial.assign_container", f, products=[door], relating_structure=storey)
                _pset(f, door, props)
                counts["doors"] += 1

    # ---- roof: geometry for the plain gable family, an honest entity for the rest
    ifc_roof = _run("root.create_entity", f, ifc_class="IfcRoof", name=f"{pid} roof")
    _run("spatial.assign_container", f, products=[ifc_roof],
         relating_structure=list(storeys.values())[-1][0])
    roof_props = {"plan_id": pid, "style": style, "tdl_id": "roof"}
    if roof_ok:
        m = roof["main"]
        roof_props.update({"form": m.get("form"), "pitch_rise_per_12": m.get("pitch_rise_per_12"),
                           "pitch_source": m.get("pitch_source"),
                           "grade_to_eave_ft": m.get("grade_to_eave_ft"),
                           "grade_to_ridge_ft": (m.get("ridge") or {}).get("grade_to_ridge_ft")})
        # T3 in the property set (WP-16.8, the audit of Phase 16, auditor D): the form is the kit's
        # judgment where its writer flags it, said on the sheets and the roof plan and not here
        _rj = _mod("disclosures", os.path.join(ROOT, "build", "disclosures.py")).roof_form_judgment(roof)
        if _rj:
            roof_props["form_judgment"] = _rj
        ridge = m.get("ridge") or {}
        if m.get("form") in GABLE_FORMS and ridge.get("grade_to_ridge_ft") and m.get("pitch_rise_per_12"):
            eave, ridge_h = m["grade_to_eave_ft"], ridge["grade_to_ridge_ft"]
            axis = ridge.get("axis", "x")
            # THE ROOF IS THE UNION READER, and ruling 1 says so in as many words: an element
            # has its own envelope and the union is reported beside it, because the roof spans
            # something and that something is not an element. On a one-rectangle house the union
            # IS the main block and every figure below is unchanged; on a multi-element house
            # this is a stated approximation -- one gable over the whole union -- and
            # `geometry_report.multi_element` is where a reader is told the roof layer has not
            # been taught about elements.
            # `EL` and `_els` were this branch's, defined in the slab loop the merge
            # replaced with main's `slab_boxes`; the reader is loaded here instead so the
            # roof keeps the union it is supposed to span.
            _EL = _mod("elements", os.path.join(ROOT, "build", "elements.py"))
            _bb = _EL.union_bbox(plan) or (0.0, 0.0, W, D)
            ow, od = (_bb[2] - _bb[0]) + 2 * t_ext, (_bb[3] - _bb[1]) + 2 * t_ext
            ridge_len, span = (ow, od) if axis == "x" else (od, ow)
            slope_run, slope_rise = span / 2.0, ridge_h - eave
            slope_len = math.hypot(slope_run, slope_rise)
            pitch_deg = math.degrees(math.atan2(slope_rise, slope_run))
            for side in (0, 1):
                plate = _run("root.create_entity", f, ifc_class="IfcSlab",
                             name=f"{pid} roof plane {side}")
                plate.PredefinedType = "ROOF"
                if axis == "x":
                    _box(f, body, plate, ridge_len, slope_len, 0.5)
                    rot = pitch_deg if side == 0 else -pitch_deg
                    cy = -t_ext + slope_run / 2 if side == 0 else D + t_ext - slope_run / 2
                    _place_rotated_x(f, plate, (W / 2, cy, eave + slope_rise / 2), rot)
                else:
                    _box(f, body, plate, slope_len, ridge_len, 0.5)
                    rot = -pitch_deg if side == 0 else pitch_deg
                    cx = -t_ext + slope_run / 2 if side == 0 else W + t_ext - slope_run / 2
                    _place_rotated_y(f, plate, (cx, D / 2, eave + slope_rise / 2), rot)
                _run("aggregate.assign_object", f, products=[plate], relating_object=ifc_roof)
                _pset(f, plate, {"plan_id": pid, "style": style, "tdl_id": f"roof-plane-{side}",
                                 "pitch_rise_per_12": m.get("pitch_rise_per_12")})
                counts["slabs"] += 1
            roof_props["geometry"] = "two gable planes"
        else:
            roof_props["geometry_note"] = (f"form '{m.get('form')}' is not modelled by WP-5.1 "
                                           f"(gable planes only) — the roof's own record rides "
                                           f"here as properties, the geometry is not guessed")
    else:
        roof_props["geometry_note"] = f"roof record unavailable: {roof.get('error')}"
    _pset(f, ifc_roof, roof_props)

    f.write(path)
    return {"path": path, "counts": counts, "units": unit_note,
            "schema": "IFC4", "roof_form": (roof.get("main", {}) or {}).get("form") if roof_ok else None}


def _place_rotated_x(f, product, xyz, deg):
    """Placement rotated about the global X axis (a roof plane whose ridge runs x)."""
    import numpy as np
    a = math.radians(deg)
    m = np.eye(4)
    m[1][1], m[1][2] = math.cos(a), -math.sin(a)
    m[2][1], m[2][2] = math.sin(a), math.cos(a)
    m[0][3], m[1][3], m[2][3] = xyz
    _run("geometry.edit_object_placement", f, product=product, matrix=m)


def _place_rotated_y(f, product, xyz, deg):
    import numpy as np
    a = math.radians(deg)
    m = np.eye(4)
    m[0][0], m[0][2] = math.cos(a), math.sin(a)
    m[2][0], m[2][2] = -math.sin(a), math.cos(a)
    m[0][3], m[1][3], m[2][3] = xyz
    _run("geometry.edit_object_placement", f, product=product, matrix=m)


# -------------------------------------------------------------------- selftest

SELFTEST_PLANS = ["plans/spec-builder-colonial.json", "plans/tidewater-georgian-careful.json"]


def selftest():
    """Build the IFC for both check plans, reopen it, and verify the acceptance
    surface: walls, slabs, openings, roof and spaces present, every one carrying
    its TDL ids. Exit 3 (COULD NOT EVALUATE) without ifcopenshell."""
    ios = _ifc()
    if ios is None:
        print("COULD NOT EVALUATE: the ifcopenshell package is not installed "
              "(pip install ifcopenshell). The IFC export was not exercised — this is not a pass.")
        return 3
    import ifcopenshell.util.element as uel
    import tempfile
    failures = unevaluated = 0
    for rel in SELFTEST_PLANS:
        plan = json.load(open(os.path.join(ROOT, rel)))
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "out.ifc")
            res = export_ifc(plan, path)
            # A REFUSED PLACEMENT IS COULD NOT EVALUATE, NEITHER A PASS NOR A FAILURE -- the DXF
            # selftest's rule since 16 Sep, reached here the day this path learned to refuse
            # (audit, 27 Sep 2026). Until then this passed by writing an IFC of a placement the
            # ruling forbids drawing.
            if res.get("refused_placement"):
                why = res["refused_placement"]
                print(f"  COULD NOT EVALUATE {rel}: the placement is refused for "
                      f"{', '.join(why.get('facts') or ['an unnamed fact'])}, so no IFC was "
                      f"written and the acceptance surface was not exercised. This is not a pass.")
                unevaluated += 1
                continue
            if "error" in res:
                print(f"  FAIL {rel}: {res['error']}")
                failures += 1
                continue
            g = ios.open(path)
            probs = []
            for cls in ("IfcWall", "IfcSlab", "IfcSpace", "IfcWindow", "IfcDoor",
                        "IfcRoof", "IfcOpeningElement", "IfcBuildingStorey"):
                if not g.by_type(cls):
                    probs.append(f"no {cls}")
            missing_pset = 0
            for cls in ("IfcWall", "IfcSlab", "IfcSpace", "IfcWindow", "IfcDoor", "IfcRoof"):
                for el in g.by_type(cls):
                    ps = uel.get_psets(el).get("TDL") or {}
                    if not ps.get("plan_id") or "tdl_id" not in ps:
                        missing_pset += 1
            if missing_pset:
                probs.append(f"{missing_pset} element(s) without TDL ids in their Pset")
            placed = sum(1 for lv in plan["levels"] for r in lv["rooms"])
            spaces = len(g.by_type("IfcSpace"))
            if spaces == 0 or spaces > placed:
                probs.append(f"{spaces} spaces for {placed} recorded rooms")
            if probs:
                print(f"  FAIL {rel}: " + "; ".join(probs))
                failures += 1
            else:
                c = res["counts"]
                print(f"  OK   {rel}: {c['walls']} walls, {c['slabs']} slabs, {c['spaces']} spaces, "
                      f"{c['windows']} windows ({c['windows_without_geometry']} data-only), "
                      f"{c['doors']} doors, roof '{res['roof_form']}', units {res['units'].split(' —')[0]}")
    if failures:
        print(f"\n{failures} selftest failure(s).")
        return 1
    if unevaluated:
        print(f"\nCOULD NOT EVALUATE: {unevaluated} of {len(SELFTEST_PLANS)} plan(s) are refused "
              f"and no IFC was written for them. This is not a pass.")
        return 3
    print("\nexport_ifc selftest: acceptance surface present on both plans.")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--parti")
    ap.add_argument("--out")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    parti = json.load(open(f"{ROOT}/partis/{a.parti}.json")) if a.parti else None
    out = a.out or os.path.join(ROOT, "dist", "ifc", f"{plan.get('id','plan')}.ifc")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    res = export_ifc(plan, out, parti)
    if "error" in res:
        print(f"  ! {res['error']}")
        sys.exit(3 if res.get("refusal") else 1)
    c = res["counts"]
    print(f"\n  {plan.get('name', plan.get('id'))}")
    print(f"  wrote {res['path']} ({res['schema']}, lengths in {res['units']})")
    print(f"  {c['walls']} walls, {c['slabs']} slabs, {c['spaces']} spaces, {c['windows']} windows, "
          f"{c['doors']} doors ({c['windows_without_geometry']} window(s) data-only, stated in their Pset)")
    print()


if __name__ == "__main__":
    main()
