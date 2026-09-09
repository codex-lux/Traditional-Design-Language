#!/usr/bin/env python3
"""The scene record — constructed 3D geometry between the placed plan and any camera.

WP-12.1, `docs/prd/phase-12-the-sheet-in-the-round.md` §§5-6.

WHAT THIS IS FOR, AND THE FINDING IT INHERITS. WP-5.11 asked whether SVG could carry a
drawn cornice or whether the project needed CAD or BIM underneath, and answered that the
FORMAT was never the constraint: *a format serialises what is modelled and cannot invent
what is not*. The missing thing was the layer between — constructed 2D geometry
(`build/profiles.py`). This is the same finding one dimension up. A continuous camera needs
a scene resident in the browser; what it does NOT need is a modelling kernel, because
everything a camera can show is already in the record. So the geometry is constructed here,
in Python, once, and the viewer only draws it. **JavaScript learns no more about a house
than it knows about a cyma today, which is nothing.**

THE FRAME. x east, y north, z up, feet throughout; the origin is the main block's SW corner
at GRADE, which is the plan frame `render_plan.py` fixed with z added. `z = 0` is grade and
the ground floor sits at `section.storeys[0].grade_to_floor_ft`. A viewer sets its up vector
to +z and transforms nothing: what the record says is what the camera sees.

WHAT IT MAY NOT DO (PRD §5.5, and every one of these is a rule this corpus already keeps):

- It may not invent a dimension. Every solid carries the `source.record` path of the numbers
  that made it and the WEAKEST `kind` among them.
- It may not restate a rule that exists. It imports `export_ifc.slab_boxes`,
  `structure.wall_thickness`, `hearths.breast`, `compass`, `storeys` — it does not
  re-derive any of them. A second transcription of a rule is how two records of one
  building come to disagree, which is the defect WP-12.0 had just finished removing one
  layer up.
- It may not carry a numeric literal that is a dimension. `tests/test_scene.py` reads this
  file's source and refuses one outside the named-constant allowlist below.
- **It may not draw what the record does not hold.** Where the record states a thing this
  layer cannot construct — a hip roof's planes, a stair's flights, an opening's reveal —
  the thing goes in `not_modelled` with its reason and is COUNTED, never silently omitted.
  A scene with an empty list prints "0 things not modelled" rather than nothing, because an
  empty list is not the question closed (WP-11.6).

WHAT IT IS NOT, YET. Openings are WP-12.2's — until then an exterior wall is a plain box and
this file says so in `not_modelled` rather than letting a blank wall read as a finished one.
Sashes, cornices, chimney solids, dormers, the entrance and the porch are WP-12.6 and 12.7.

CLI:
    python3 build/scene.py plans/tidewater-georgian-careful.json [--engine auto] [--out s.json]
    python3 build/scene.py selftest
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache as _mc  # noqa: E402

SCENE_VERSION = "0.1.0"

# ---------------------------------------------------------------- editorial constants
# The allowlist the source-reading test enforces. A number here is a DECISION nobody has
# sourced, and it says so in its own name and note; a number anywhere else in this file is
# a bug. Both are ruled and both are marked, exactly as `storey-graduation`'s 7.5 in riser
# divisor is.

# editorial: the drafting convention for a plan's cut plane, 4 ft above finished floor
# (PRD ruling R2, taken 8 Sep 2026). The corpus states no rule for it, so it is judgment,
# it is named, and the plan caption prints it. A ruled number with no source is still
# editorial.
CUT_HEIGHT_FT = 4.0

# NOT a dimension, and named for a different reason: the search pool a scene is placed on.
# `oq/a-placement-rule-is-free-at-a-pool-the-server-cannot-afford` records that four packages
# have now measured a placement rule whose verdict is a property of THIS number, so it is the
# last figure in this file that should sit unnamed in an argparse call.
DEFAULT_CANDIDATES = 250


def _mod(name):
    return _mc.load(name, os.path.join(ROOT, "build", f"{name}.py"))


# ---------------------------------------------------------------- ids
# The `tdl_id` scheme is `export_ifc.py`'s, extended. It is not a new convention: a solid
# and the IfcProduct that will one day be swept from it must answer to the same name, or
# click-to-record means one thing in the viewer and another in the model a drafter opens.

def _wall_id(level, i):
    return f"L{level}-wall-{i}"


def _slab_id(level, element):
    return f"floor-L{level}" + (f"-{element}" if element and element != "main" else "")


# ---------------------------------------------------------------- the three states

class _States:
    """Drawn, not modelled, judgment — collected as the scene is built so that a refusal
    is recorded where it is TAKEN rather than remembered and listed at the end. The count
    is printed on the plate; the list is what a reader opens."""

    def __init__(self):
        self.not_modelled = []
        self.judgment = []

    def cannot(self, what, why, source, cls="geometry"):
        self.not_modelled.append({"what": what, "why": why, "source": source, "class": cls})

    def judged(self, what, why, source):
        self.judgment.append({"what": what, "why": why, "source": source})


def _solid(sid, cls, geometry, ink, tone, source, kind, level=None, element="main",
           face=None, room=None, note=None):
    """One drawable thing. `ink` and `tone` are NAMES the viewer resolves from `tokens.css`
    — a solid never carries a hex, because colour in this system is nomenclature and a hex
    in a record is a decision nobody can argue with."""
    s = {"id": sid, "class": cls, "geometry": geometry, "ink": ink, "tone": tone,
         "source": source, "kind": kind, "element": element}
    if level is not None:
        s["level"] = level
    if face:
        s["face"] = face
    if room:
        s["room"] = room
    if note:
        s["note"] = note
    return s


# ---------------------------------------------------------------- the layers

def _storey_datums(section, states):
    """Every horizontal datum a drawing names, from the section's own storeys and roof.

    The heights are `structure.py`'s and are not recomputed here. A storey that states no
    height is CARRIED as unjudged rather than dropped: `storeys.py` returns None where a
    level states no ceiling, and a datum silently missing reads as a building with one
    fewer floor."""
    out, storeys = [], section.get("storeys") or []
    for st in storeys:
        z = st.get("grade_to_floor_ft")
        if z is None:
            states.cannot(f"storey {st.get('id')} floor datum",
                          "the level states no ceiling, so storeys.py returns no height "
                          "for it and there is no floor to place",
                          f"section.storeys[{st.get('index')}]", cls="datum")
            continue
        out.append({"id": f"floor-{st['id']}", "label": _feet(z), "z_ft": z,
                    "class": "floor", "source": f"section.storeys[{st.get('index')}]"
                    ".grade_to_floor_ft", "kind": "derived"})
        ch = st.get("ceiling_ft")
        if ch is not None:
            out.append({"id": f"ceiling-{st['id']}", "label": _feet(z + ch),
                        "z_ft": round(z + ch, 3), "class": "ceiling",
                        "source": f"section.storeys[{st.get('index')}].ceiling_ft",
                        "kind": "measured"})
    roof = section.get("roof") or {}
    for key, cls in (("grade_to_eave_ft", "eave"), ("grade_to_ridge_ft", "ridge")):
        z = roof.get(key)
        if z is None:
            states.cannot(f"{cls} datum", roof.get("note") or
                          "the section states no height for it", f"section.roof.{key}",
                          cls="datum")
            continue
        out.append({"id": cls, "label": _feet(z), "z_ft": z, "class": cls,
                    "source": f"section.roof.{key}", "kind": "derived"})
    out.append({"id": "grade", "label": _feet(0.0), "z_ft": 0.0, "class": "grade",
                "source": "frame.origin", "kind": "editorial"})
    return sorted(out, key=lambda d: d["z_ft"])


def _feet(v):
    """A datum's label in feet and inches. `render_plan.py` and `derive.js` both spell this;
    this is the third and it is deliberate — the scene record is consumed by a viewer that
    must not know how this corpus writes a dimension, so the STRING travels with the datum.
    The arithmetic is trivial and the alternative is a fourth copy in JavaScript."""
    neg = v < 0
    v = abs(v)
    ft = int(v)
    inch = int(round((v - ft) * 12))
    if inch == 12:
        ft, inch = ft + 1, 0
    return ("-" if neg else "+") + f"{ft}′-{inch}″"


def _slabs(plan, section, states):
    """One box per (storey, element), from `export_ifc.slab_boxes` — IMPORTED, never
    re-derived. That function is pure arithmetic precisely so it can be read where
    `ifcopenshell` is absent, which is here and in CI; this is its second reader and the
    reason it was written that way."""
    ei = _mod("export_ifc")
    t_ext = (section.get("wall") or {}).get("exterior_in")
    if t_ext is None:
        states.cannot("floor slabs", "the section states no exterior wall thickness",
                      "section.wall.exterior_in")
        return []
    boxes = ei.slab_boxes(plan, section, t_ext / 12.0)
    out = []
    for b in boxes:
        out.append(_solid(
            _slab_id(b["level"], b.get("element")), "slab",
            {"type": "box",
             "origin": [round(b["cx"] - b["width_ft"] / 2, 3),
                        round(b["cy"] - b["depth_ft"] / 2, 3),
                        round(b["grade_to_floor_ft"] - b["thickness_ft"], 3)],
             "size": [round(b["width_ft"], 3), round(b["depth_ft"], 3),
                      round(b["thickness_ft"], 3)]},
            "seen", "paper-mat",
            {"record": "export_ifc.slab_boxes(plan, section, t_ext)",
             "also": ["section.wall.exterior_in", "section.storeys[].grade_to_floor_ft"]},
            "derived", level=b["level"], element=b.get("element") or "main"))
    return out


def _walls(section, states):
    """Every wall segment on every level, as a box.

    The segments, their roles and their bearing verdicts are `structure.wall_lines` and
    `structure.bearing_lines`' — read, not recomputed. Two things this layer must add and
    does so from the record rather than by choosing:

    HEIGHT comes from the storey the wall is on (`ceiling_ft`), and a storey with no stated
    ceiling yields no walls and a refusal, because a wall of invented height is exactly the
    class OQ 52 removed from the elevation.

    THICKNESS and the direction it grows are `export_ifc.py`'s convention, and following it
    is the point: an exterior wall grows OUTWARD from the clear line so its inner face sits
    where the room's rectangle says the room ends, and an interior wall is centred on the
    line it shares. Diverge from that and the scene and the IFC model are two buildings."""
    wall_rec = section.get("wall") or {}
    t_ext = wall_rec.get("exterior_in")
    t_bear = wall_rec.get("bearing_interior_in")
    t_part = wall_rec.get("partition_in")
    if t_ext is None or t_bear is None or t_part is None:
        states.cannot("walls", "the section states no wall thicknesses",
                      "section.wall")
        return []
    storeys = {st.get("index"): st for st in (section.get("storeys") or [])}
    out = []
    for lv in section.get("levels") or []:
        idx = lv.get("index")
        st = storeys.get(idx) or {}
        h = st.get("ceiling_ft")
        z = st.get("grade_to_floor_ft")
        if h is None or z is None:
            states.cannot(f"walls on level {idx}",
                          "the storey states no ceiling height, so a wall on it would have "
                          "to be given one — which is the invented measurement OQ 52 removed",
                          f"section.storeys[{idx}]")
            continue
        for i, w in enumerate(lv.get("walls") or []):
            exterior = w.get("role") == "exterior"
            t_in = t_ext if exterior else (t_bear if w.get("bearing") else t_part)
            t = t_in / 12.0
            lo, hi, pos = w.get("lo_ft"), w.get("hi_ft"), w.get("position_ft")
            if lo is None or hi is None or pos is None:
                states.cannot(f"wall {_wall_id(idx, i)}",
                              "the segment states no extent", f"section.levels[{idx}]"
                              f".walls[{i}]")
                continue
            # An exterior wall grows OUTWARD from the clear line so its inner face sits where
            # the room's rectangle says the room ends; an interior one is centred on the line
            # it shares. `wall["wall"]` names which side of the block an exterior segment is,
            # and outward is negative on the low sides (S at y=0, W at x=0) and positive on
            # the high ones (N, E).
            #
            # THE FIRST VERSION HAD THIS EXACTLY BACKWARDS AND EVERY EXTERIOR WALL GREW INTO
            # THE HOUSE. It was not visible in any single number — each wall was the right
            # thickness in the right place along its own axis — and it was caught by summing
            # the extent: the envelope came out 63.0 x 38.17, which is the CLEAR footprint,
            # where an outside-to-outside envelope must be larger than the rooms it wraps.
            # Measure the whole, not the part.
            grow = t
            if exterior:
                near = pos if w.get("wall") in ("N", "E") else pos - t
            else:
                near = pos - t / 2.0
            if w.get("axis") == "x":          # constant x, running along y
                origin = [round(near, 3), round(lo, 3), round(z, 3)]
                size = [round(grow, 3), round(hi - lo, 3), round(h, 3)]
            else:                              # constant y, running along x
                origin = [round(lo, 3), round(near, 3), round(z, 3)]
                size = [round(hi - lo, 3), round(grow, 3), round(h, 3)]
            out.append(_solid(
                _wall_id(idx, i), "wall", {"type": "box", "origin": origin, "size": size},
                "cut" if exterior else ("profile" if w.get("bearing") else "seen"),
                "salmon" if exterior else "paper-deep",
                {"record": f"section.levels[{idx}].walls[{i}]",
                 "also": ["section.wall", f"section.storeys[{idx}].ceiling_ft"]},
                # `kind` is the WEAKEST of the numbers that made a solid, and for a wall box
                # that is its thickness. `structure.wall_thickness` writes a `note` on exactly
                # one occasion — when the plan declared no `construction_type` and it assumed
                # one ("No construction_type declared on this plan; assumed platform-frame") —
                # so the note is a declared-versus-assumed signal and not decoration. Measured:
                # `tidewater-georgian-careful` declares solid masonry and its walls come out
                # `derived`; `spec-builder-colonial` declares nothing, and all 41 of its walls
                # are honestly `editorial`.
                "editorial" if wall_rec.get("note") else "derived",
                level=idx, element=w.get("element") or "main",
                face=w.get("wall") if exterior else None,
                note=w.get("why")))
    return out


# How far a stack stands above the ridge where its own record states no cap height. EDITORIAL:
# no pack in this corpus states it, and a stack level with the ridge draws as a house with a
# hole in its roof. Named so it cannot read as a measurement.
CHIMNEY_ABOVE_RIDGE_FT = 2.0


def _face_extrude(face, u0, u1, z0, z1, ox, oy, W, D, t_ext):
    """(plane, at, outline) for a rectangle on one face, in the scene's own frame (WP-12.6).

    THE ONE SPELLING, lifted out of `_openings` because WP-12.6 needed the identical mapping
    for every sash bar, shutter leaf and cornice run — forty more copies of it on the Tidewater
    plan alone. `u` runs along the face from its own left edge and `z` above grade, both in FEET.

    `at` IS THE LOW FACE AND THE EXTRUSION ALWAYS RUNS +AXIS. That is WP-12.2's contract, and its
    first version put `at` on the OUTSIDE face with an always-positive thickness — so south and
    west openings went INTO their walls and north and east ones stood PROUD of them, which no
    number in the record disagreed with and one picture showed at once.
    """
    if face in ("S", "N"):
        return ("xz", (oy if face == "S" else oy + D - t_ext),
                [[ox + u0, z0], [ox + u1, z0], [ox + u1, z1], [ox + u0, z1]])
    return ("yz", (ox if face == "W" else ox + W - t_ext),
            [[oy + u0, z0], [oy + u1, z0], [oy + u1, z1], [oy + u0, z1]])


def _openings(elev, section, states):
    """The openings, as their own solids, from `elevation.opening_rects` — the THIRD caller of
    the one function WP-12.2 lifted (the SVG renderer and the DXF exporter are the other two).

    THEY ARE FRAMES AND NOT HOLES, and the distinction is the honest one. A hole is a boolean
    subtraction from the wall it sits in, and this layer does no CSG: the wall stays the box the
    section describes and the opening is drawn as the rectangle the elevation states, in its own
    face plane, at the reveal. WP-12.6 dresses it with sash, muntins, sill and shutters; what is
    here is the opening's extent, which is what the elevation actually determines.

    A face the elevation refuses carries no openings and says so once, rather than per bay.
    """
    out = []
    if not elev or elev.get("error") or not elev.get("faces"):
        states.cannot("openings on every face",
                      (elev or {}).get("error") or "the elevation generator refuses outside the "
                      "classical-front family, so no face states an opening",
                      "elevation.faces", cls="opening")
        return out
    fp = section.get("footprint") or {}
    W, D = fp.get("width_ft"), fp.get("depth_ft")
    t_ext = ((section.get("wall") or {}).get("exterior_in") or 0) / 12.0
    ox = oy = -t_ext
    EL = _mod("elevation")
    kept = {}
    for face in ("S", "N", "E", "W"):
        got = EL.opening_rects(elev, face)
        kept[face] = got["rects"]
        for r in got["refused"]:
            states.cannot(f"opening on face {face} bay {r.get('bay')}", r["why"], r["source"],
                          cls="opening")
        for r in got["rects"]:
            # The face's own horizontal runs along the wall it is on: x for S and N, y for E
            # and W. The elevation lays every face out from its own left edge at 0, and the
            # faces are laid over the OUTSIDE footprint, so they take the same origin shift the
            # roof does — one frame for the whole scene.
            u0, u1 = r["x0_in"] / 12.0, r["x1_in"] / 12.0
            z0, z1 = r["sill_in"] / 12.0, r["head_in"] / 12.0
            # `at` IS THE LOW FACE AND THE EXTRUSION ALWAYS RUNS +AXIS, which is the whole
            # contract: a viewer extrudes `thickness` from `at` in the plane's own positive
            # direction and never has to know which side of the building it is on. The first
            # version put `at` on the OUTSIDE face of every wall and extruded positively from
            # there, so the south and west openings went into the wall and the north and east
            # ones stood proud of it — and it rendered as a house with blocks stuck to two of
            # its faces. Caught by looking at the picture, which is the second time in this
            # phase that a geometry defect was invisible to every number.
            plane, at, outline = _face_extrude(face, u0, u1, z0, z1, ox, oy, W, D, t_ext)
            # THE OPENING'S ID IS THE RECT'S OWN AND IS NOT REBUILT HERE. `opening_rects` has
            # named every rectangle since WP-12.2 (`S-0-ground`, `S-3-door`); WP-12.1 rebuilt
            # that name out of four fields, and when WP-12.6 came to dress the opening it keyed
            # the sash and its bars off `r["id"]` instead — so one opening had two names, the
            # frame's and its own dressing's, and no assertion comparing them could hold. Found
            # by a mutation that dropped a frame and left its bars hanging in the wall plane
            # while the guard written to catch exactly that stayed green.
            out.append(_solid(
                r["id"], "opening-frame",
                {"type": "extrude", "plane": plane, "at": round(at, 3),
                 "thickness": round(t_ext, 3),
                 "outline": [[round(a, 3), round(b, 3)] for a, b in outline]},
                "profile", "paper-lit",
                {"record": r["source"], "also": [f"elevation.faces.{face}.centres_ft"]},
                "derived", face=face,
                note="the opening's extent, drawn in the face plane at the reveal. It is a "
                     "FRAME and not a hole: this layer does no boolean subtraction, so the "
                     "wall behind it is the box the section describes"))
    out.extend(_dress_openings(elev, states, kept, ox, oy, W, D, t_ext))
    return out


# The muntin bar is drawn SQUARE — its width in the sash plane is the only dimension the record
# states for it, and how far a bar stands proud of the glass is not a number this corpus holds.
# Said here rather than left as a bare `bw` at the call site.
_BAR_IS_SQUARE = True


def _dress_openings(elev, states, rects_by_face, ox, oy, W, D, t_ext):
    """Sash bars, shutters and the sill, on every drawn opening (WP-12.6).

    EVERY NUMBER IS THE RECORD'S OWN. `lights_across`, `lights_high_per_sash`, `muntin_width_in`,
    `shutter_leaf_width_in` and `shutter_panel_count` are `elevation._storey_window`'s fields,
    read off the rect's own `record`, so a window drawn here cannot disagree with the elevation
    plate beside it about how many lights it has.

    THE LIGHT COUNT IS `lights_across x lights_high_per_sash x 2` and the bars are laid to give
    exactly that: `across - 1` verticals running the full opening — the two sashes of a
    double-hung align, so a bar is one member and not two — and `2 x high - 1` horizontals, of
    which the middle one is the MEETING RAIL and is a real member rather than a glazing bar. It
    carries its own class so a reader can tell them apart.

    THE SILL IS REFUSED, AND THAT IS THE FINDING. `window_sill.projection_in` resolves to a BAND
    on `tidewater-georgian` — `[0, 1]` in, because a child `extends` replaced the ancestor's
    derivation — and only 2 of 159 kits state the parameter at all. That is
    `oq/a-child-band-replaces-an-ancestor-derivation` reaching its first consumer: WP-11.4 raised
    it as a data observation with nothing reading it, and a drawing is the thing that cannot draw
    a band. A sill at the band's midpoint is a measurement nobody authored.
    """
    out = []
    for face, rects in rects_by_face.items():
        for r in rects:
            rec = r.get("record")
            if r.get("kind") != "window" or not rec:
                continue
            u0, u1 = r["x0_in"] / 12.0, r["x1_in"] / 12.0
            z0, z1 = r["sill_in"] / 12.0, r["head_in"] / 12.0
            across, high = rec.get("lights_across"), rec.get("lights_high_per_sash")
            bar = rec.get("muntin_width_in")
            src = {"record": f"elevation.storey_windows[{r['storey']}].muntin_width_in",
                   "also": [f"elevation.storey_windows[{r['storey']}].lights_across",
                            f"elevation.storey_windows[{r['storey']}].lights_high_per_sash"]}
            if not across or not high or not bar:
                states.cannot(f"the sash bars in {r['id']}",
                              "the storey window states no light count or no muntin width, so "
                              "the number of lights is not a fact this record holds",
                              f"elevation.storey_windows[{r['storey']}]", cls="opening")
                continue
            bw = bar / 12.0
            plane, at, _ = _face_extrude(face, u0, u1, z0, z1, ox, oy, W, D, t_ext)

            def _bar(sid, a, b, c, d, cls):
                _, _, ol = _face_extrude(face, a, b, c, d, ox, oy, W, D, t_ext)
                return _solid(sid, cls,
                              {"type": "extrude", "plane": plane, "at": round(at, 3),
                               "thickness": round(bw, 4),
                               "outline": [[round(x, 3), round(y, 3)] for x, y in ol]},
                              "fine", "paper-lit", src, "measured", face=face)

            for i in range(1, across):
                cu = u0 + (u1 - u0) * i / across
                out.append(_bar(f"{r['id']}-bar-v{i}", cu - bw / 2, cu + bw / 2, z0, z1, "muntin"))
            rows = 2 * high
            for j in range(1, rows):
                cz = z0 + (z1 - z0) * j / rows
                # THE SCHEMA ALREADY NAMED THIS VOCABULARY and the first draft invented its own.
                # `scene.schema.json`'s class enum has carried `muntin` and `sash` since WP-12.1;
                # `sash-bar` and `meeting-rail` are words I made up, and the schema check caught
                # all 350 of them at once. A glazing bar is a MUNTIN. The middle horizontal is
                # the MEETING RAIL, which is the bottom rail of the upper sash meeting the top
                # rail of the lower one -- a member of the SASH and not a glazing bar, which is
                # the distinction the schema's own two words already draw.
                out.append(_bar(f"{r['id']}-bar-h{j}", u0, u1, cz - bw / 2, cz + bw / 2,
                                "sash" if j == high else "muntin"))

            # THE SHUTTERS, where the style carries them. A leaf is drawn OPEN and flat against
            # the wall beside its own jamb, which is the only position the record determines: a
            # closed leaf would assert something about the day the drawing represents, and no
            # record states one.
            # `shutters_carried` IS PER STOREY WINDOW and not on the elevation.
            # `elevation.py` sets it at 1843 as `sw["shutters_carried"]`; reading it off `elev`
            # returns None on every house, and the first draft of this function did exactly that
            # — so no shutter would ever have been drawn, on any plan, silently. It was found by
            # printing the class census before and after, and by nothing else: the sash bars
            # appeared, the picture looked dressed, and a whole class was absent from it.
            lw_in = rec.get("shutter_leaf_width_in")
            if rec.get("shutters_carried") and lw_in:
                lw = lw_in / 12.0
                lh = (rec.get("shutter_leaf_height_in") or (r["head_in"] - r["sill_in"])) / 12.0
                for side, (a, b) in (("l", (u0 - lw, u0)), ("r", (u1, u1 + lw))):
                    _, _, ol = _face_extrude(face, a, b, z0, z0 + lh, ox, oy, W, D, t_ext)
                    out.append(_solid(
                        f"{r['id']}-shutter-{side}", "shutter",
                        {"type": "extrude", "plane": plane, "at": round(at, 3),
                         "thickness": round(bw, 4),
                         "outline": [[round(x, 3), round(y, 3)] for x, y in ol]},
                        # THREE INVENTED NAMES IN A ROW, and the schema caught every one:
                        # `sash-bar`/`meeting-rail` for the class, `hidden` for the ink, and
                        # `sepia` for this tone. `scene.schema.json` already names the whole
                        # vocabulary — read the enum before naming anything.
                        "seen", "sepia-pale",
                        {"record": f"elevation.storey_windows[{r['storey']}].shutter_leaf_width_in",
                         "also": ["elevation.shutters_carried"]},
                        "measured", face=face,
                        note=f"drawn open; {rec.get('shutter_panel_count')} panels a leaf"))
    if rects_by_face:
        states.cannot("the sills under every window",
                      "`window_sill.projection_in` resolves to a BAND rather than a figure on "
                      "the nodes this corpus draws (tidewater-georgian states [0, 1] in, a child "
                      "`extends` that replaced the ancestor's derivation), and only 2 of 159 "
                      "kits state the parameter at all. A sill drawn at the midpoint of a band "
                      "is a measurement nobody authored — see "
                      "oq/a-child-band-replaces-an-ancestor-derivation",
                      "kit.window_sill.projection_in", cls="opening")
    return out


def _dormers(elev, states):
    """The dormers, or the record's own reason there are none to draw (WP-12.6).

    IT READS THE DORMER RECORD'S OWN FIELDS, AND THE PLAN SAID THEY DO NOT EXIST.
    `PLAN-OF-ACTION.md`'s WP-12.6 line says to read `refused` / `placed_count` /
    `placement_shortfall_note` because "there is no `placeable` and no `not_drawn_reason`, which
    the PRD assumed". **That correction is false.** Both fields are on the dormer record
    (`elevation.py` 1971-1980) and `render_elevation.py` has read them since the day they landed;
    all six names are on the one record. Following the plan would have re-derived `placeable`'s
    judgment from `refused` — a second reader of one question, which is the defect this corpus
    meets more often than any other.

    AND IT READ THE WRONG ONE OF THEM FOR THE WHOLE OF THIS PACKAGE'S FIRST DRAFT. The key is
    `dormers`, PLURAL — `build_elevation` writes it at `elevation.py` 2012 and
    `render_elevation.py` has read `elev.get("dormers")` in both its readers all along. This
    function read `dormer`, so it returned `{}` on every record in the corpus and drew, refused
    and disclosed nothing. It was invisible to its own three tests, because all three DRIVE it
    with a hand-built dict — and that dict carried the same wrong key as the code, so the test
    and the defect agreed with each other. `test_the_key_this_function_reads_is_the_key_the
    _elevation_writes` takes the name off a real elevation now instead of a literal.

    That is the SECOND field this package read off the wrong record — `shutters_carried` is set
    per storey window and not on the elevation, and drew no shutter anywhere until a census of
    solid classes caught it. Both were silent, and neither was found by reading.

    FOUR STATES, AND THE FOURTH IS THE ONE BOTH SHIPPED PLANS ARE IN. Stated with a count and
    placeable -> drawn (Stage B; the geometry wants the roof surface). Stated with a count and
    NOT placeable -> a `not_modelled` entry carrying the record's OWN `not_drawn_reason`, because
    `spec-builder-colonial`'s roof has no judged pitch and no judged ridge, so there is no
    surface to stand a dormer on — while the count still reaches the fault corpus, which once
    judged three dormers on a sheet that drew none. Not stated at all -> nothing, and no
    reassuring zero. **Stated with a count of ZERO -> also nothing**, and that is not the same
    silence: the record has considered dormers and says the house has none.

    The first version gated on `stated` alone and filed *"the dormer solids could not be
    modelled"* against both shipped plans, each of which states `count: 0`. A refusal about
    something that does not exist is the fake-unjudged shape wearing its other face — it reads
    as a gap in this layer where the record is in fact complete — and it is exactly as dishonest
    as a fake pass. `elevation.py` 1954 is the authority: `placeable` and `not_drawn_reason` are
    written only `if dorm.get("count")`, so a count of zero can never reach the branch below and
    gating anywhere but on the count invents a state the writer does not have.
    """
    dorm = (elev or {}).get("dormers") or {}
    if not dorm.get("stated") or dorm.get("refused") or not dorm.get("count"):
        return []
    if dorm.get("placeable") is False:
        states.cannot("the dormers the record states",
                      dorm.get("not_drawn_reason") or "the record states no reason",
                      "elevation.dormers.not_drawn_reason", cls="dormer")
        return []
    short = dorm.get("placement_shortfall_note")
    if short:
        states.cannot("some of the dormers the record states", short,
                      "elevation.dormers.placement_shortfall_note", cls="dormer")
    states.cannot("the dormer solids", "WP-12.6 states the dormer's THREE refusal states and "
                  "draws none: the cheeks, face and own roof stand on the roof surface, which "
                  "this layer models as two planes rather than as a solid to sit a box on",
                  "elevation.dormers", cls="dormer")
    return []


def _roof(plan, section, roof, states, elev=None):
    """The roof volume, and — where this file cannot construct it — the refusal.

    GABLE ONLY, and the boundary is the record's rather than this file's convenience.
    `roof.py` gives a ridge with its axis, extent and height for the gable family, and for a
    hip it gives `hip_lines` in PLAN ONLY with height "implied"; for a gambrel it gives break
    offsets; for a cross-gable it says in its own note that no valley geometry exists because
    the plan layer has never placed a second volume to cut one against. So a hip, a gambrel
    and a cross are NAMED here, with the form, rather than approximated by a gable — which is
    what a reader would never be able to tell from a drawing.
    """
    main = roof.get("main") or {}
    form = main.get("form")
    ridge = main.get("ridge") or {}
    z_ridge = ridge.get("grade_to_ridge_ft")
    z_eave = main.get("grade_to_eave_ft")
    fp = section.get("footprint") or {}
    W, D = fp.get("width_ft"), fp.get("depth_ft")
    out = []

    # THE ROOF RECORD AND THE PLAN RECORD DO NOT SHARE AN ORIGIN, AND THIS LAYER IS THE FIRST
    # THING THAT HAD TO PUT THEM IN ONE PICTURE.
    #
    # `roof_outline` and `elevation_profile` lay the roof out from (0, 0) over the OUTSIDE
    # footprint — 0 to 65.58 by 0 to 40.75 on the Tidewater plan — while `wall_lines` lays the
    # walls out from (0, 0) over the CLEAR one, 0 to 63 by 0 to 38.17. Both call their corner
    # the origin and the two corners are half an exterior wall apart, so read literally the
    # roof sits 1.29 ft east and north of the house it covers.
    #
    # It has never mattered, because the plan sheet draws rooms and the roof plan draws a roof
    # and no surface has ever drawn both. In three dimensions they must coexist, and the offset
    # becomes a roof visibly sliding off its walls.
    #
    # `export_ifc.slab_boxes` already answers it — its slabs are CENTRED on the clear
    # rectangle, at origin (-t, -t) — so this follows that convention rather than inventing a
    # third: the plan frame is the authority (the plan schema defines the origin as the block's
    # SW corner) and the outside envelope is centred on it. Which record should MOVE is
    # `oq/the-roof-record-and-the-plan-record-do-not-share-an-origin`.
    #
    # (That citation is on ONE LINE for a reason worth knowing: `check_citations.py` reads line
    # by line, so a slug wrapped across a newline is cited as its truncated left half, which
    # names no entry. This session found that shape in the Phase 12 PRD in the morning, wrote
    # it down as a trap, and committed it here in the afternoon.)
    t_ext_ft = ((section.get("wall") or {}).get("exterior_in") or 0) / 12.0
    ox = oy = -t_ext_ft
    if form not in ("gable", "side-gable", "front-gable"):
        states.cannot(f"roof planes for form {form!r}",
                      (main.get("note") or "").strip() or
                      f"roof.py states the form and its pitch; the planes of a {form} are "
                      f"not dimensioned by any record this layer reads",
                      "roof.main", cls="roof")
        return out
    if z_ridge is None or z_eave is None or W is None or D is None:
        states.cannot("roof planes",
                      "the roof record carries no ridge or eave height",
                      "roof.main.ridge.grade_to_ridge_ft", cls="roof")
        return out
    # The two slopes, as prisms with the true pitched polygon. `export_ifc.py` emits these as
    # rotated slabs; a prism carries the same surface without a rotation the viewer would
    # have to reproduce, and the polygon is read straight off the face silhouette below.
    axis = ridge.get("axis")
    ridge_pos = ridge.get("position_ft")

    # A SLOPE IS NOT A PRISM, AND THE FIRST VERSION OF THIS DREW A FLAT-TOPPED BOX.
    #
    # `prism` extrudes one polygon vertically between two heights, so a roof plane written as a
    # prism from the eave height to the ridge height is a BOX that spans the roof's rise — the
    # right footprint, the right two heights, and no slope anywhere in it. Every agreement
    # figure this layer computes was satisfied by it, because all three measure the PLAN extent,
    # and the house rendered as a two-storey block with a lid.
    #
    # It was caught by drawing the scene and looking at it, which is this project's own most
    # expensive lesson (WP-9.6: "Lucas found it by looking at the sheet; nothing in the suite
    # could"). A sloping plane needs a per-vertex height, so it gets a primitive of its own —
    # `plane`, four vertices in 3D — rather than being coerced into one that cannot hold it.
    def _plane(n, verts, extra=None):
        out.append(_solid(
            f"roof-plane-{n}", "roof-plane",
            {"type": "plane", "vertices": [[round(a, 3), round(b, 3), round(c, 3)]
                                           for a, b, c in verts]},
            "profile", "paper-deep",
            {"record": "roof.main.ridge",
             "also": ["roof.main.pitch_rise_per_12", "section.roof.grade_to_eave_ft"]},
            "derived", note="two eave corners at the eave height and two ridge corners at the "
                            "ridge height: the slope is in the vertices, not in a rotation"))

    if axis == "x":       # ridge runs along x, slopes fall to y = 0 and y = D
        for n, y0 in enumerate((0.0, D)):
            _plane(n, [(ox, oy + y0, z_eave), (ox + W, oy + y0, z_eave),
                       (ox + W, oy + ridge_pos, z_ridge), (ox, oy + ridge_pos, z_ridge)])
    else:                  # ridge runs along y, slopes fall to x = 0 and x = W
        for n, x0 in enumerate((0.0, W)):
            _plane(n, [(ox + x0, oy, z_eave), (ox + x0, oy + D, z_eave),
                       (ox + ridge_pos, oy + D, z_ridge), (ox + ridge_pos, oy, z_ridge)])
    # The gable ends: the wall above the eave, as the face's own silhouette polygon.
    profiles = roof.get("elevation_profiles") or {}
    gable_faces = ("E", "W") if axis == "x" else ("S", "N")
    for f in gable_faces:
        prof = profiles.get(f)
        if not prof:
            states.cannot(f"gable on face {f}", "the roof record carries no silhouette for "
                          "this face", f"roof.elevation_profiles.{f}", cls="roof")
            continue
        out.append(_solid(
            f"gable-{f}", "gable",
            # A gable stands on the face it names: an E or W gable is a constant-X plane
            # and sits at an x, an N or S gable is a constant-Y plane and sits at a y. The
            # first version took `D` for the E face — the DEPTH as an x coordinate — which
            # put the east gable inside the house, and it was caught by reading the number
            # against the wall extent rather than by reading the expression.
            # `at` is the LOW face and the extrusion runs +axis, as for every opening above.
            {"type": "extrude", "plane": "yz" if f in ("E", "W") else "xz",
             "at": round((ox if f == "W" else oy if f == "S"
                          else ox + W - t_ext_ft if f == "E" else oy + D - t_ext_ft), 3),
             "thickness": round(t_ext_ft, 3),
             "outline": [[round(u + (oy if f in ("E", "W") else ox), 3), round(v, 3)]
                         for u, v in prof]},
            "cut", "salmon",
            {"record": f"roof.elevation_profiles.{f}"}, "derived", face=f))
    out += _chimneys(roof, elev, section, states)
    return out


def _chimneys(roof, elev, section, states):
    """The stacks: a SOLID where the plan size is stated, an AXIS and a named judgment where it
    is not (WP-12.6).

    THIS FUNCTION IS SPECIFIED BY THE REFUSAL IT REPLACES. `_roof` has carried, since WP-12.1,
    the sentence *"the stack's plan size is a judgment the corpus declines to settle
    (brick-course states 22 in with judgment: true — 'the mason will build 18 or 27'), so a solid
    here would be an invented dimension; WP-12.6 draws an axis line and names the judgment."*
    This is that, and the refusal is deleted rather than left beside its own fix — which is
    WP-6.4's rule that "until X lands" is a lie the moment X lands.

    A JUDGMENT IS NOT A REFUSAL AND THE RECORD KEEPS THEM APART. `not_modelled` means the record
    holds a thing this layer did not draw; `judgment` means the corpus itself declines to settle
    the number. Collapsing the second into the first would say the corpus is silent where it has
    in fact spoken and said "the mason decides" — and a reader owed that distinction is exactly
    the reader who is choosing a brick.
    """
    ch = (roof.get("chimneys") or {})
    positions = ch.get("positions") or []
    if not positions:
        return []
    plan_in = (elev or {}).get("chimney_stack_plan_in")
    is_judgment = bool((elev or {}).get("chimney_stack_plan_judgment"))
    z_ridge = ((roof.get("main") or {}).get("ridge") or {}).get("grade_to_ridge_ft")
    fp = section.get("footprint") or {}
    t_ext = ((section.get("wall") or {}).get("exterior_in") or 0) / 12.0
    out = []
    if z_ridge is None:
        states.cannot("the chimney stacks",
                      "the roof record judges no ridge height, so there is nothing to carry a "
                      "stack up past", "roof.main.ridge.grade_to_ridge_ft", cls="chimney")
        return out
    for i, pos in enumerate(positions):
        x = pos.get("x_ft")
        y = pos.get("y_ft")
        if x is None or y is None:
            states.cannot(f"chimney stack {i}", "the roof record places it on no axis",
                          f"roof.chimneys.positions[{i}]", cls="chimney")
            continue
        top = pos.get("grade_to_cap_ft") or (z_ridge + CHIMNEY_ABOVE_RIDGE_FT)
        if is_judgment or not plan_in:
            # THE AXIS, and nothing wider. A line has no plan size, which is precisely the fact
            # the corpus is declining to settle.
            out.append(_solid(
                f"chimney-{i}-axis", "chimney",
                {"type": "plane", "vertices": [[round(x - t_ext, 3), round(y - t_ext, 3), 0.0],
                                               [round(x - t_ext, 3), round(y - t_ext, 3),
                                                round(top, 3)]]},
                # `construction` and not `hidden`: the schema's ink enum is
                # cut/profile/seen/fine/construction and `hidden` is a word I invented. An axis
                # IS a construction line, which is the enum's own name for it.
                "construction", "paper-mat",
                {"record": f"roof.chimneys.positions[{i}]",
                 "also": ["elevation.chimney_stack_plan_judgment"]},
                "judgment", note="the stack's axis; its plan size is a judgment the corpus "
                                 "declines to settle, so no solid is drawn"))
            states.judged(f"chimney stack {i}",
                          f"the plan size is stated as {plan_in} in with judgment: true — "
                          "brick-course's own note is that the mason will build 18 or 27. The "
                          "axis is drawn and the mass is not.",
                          "elevation.chimney_stack_plan_in")
            continue
        w = plan_in / 12.0
        out.append(_solid(
            f"chimney-{i}", "chimney",
            {"type": "box",
             "origin": [round(x - t_ext - w / 2, 3), round(y - t_ext - w / 2, 3), 0.0],
             "size": [round(w, 3), round(w, 3), round(top, 3)]},
            "cut", "salmon",
            {"record": f"roof.chimneys.positions[{i}]",
             "also": ["elevation.chimney_stack_plan_in"]},
            "measured"))
    return out


def _hearths(plan, states):
    """A fire is authored and never inferred (WP-11.4), so this reads `room.hearth[]` and
    draws only what is there. The breast rectangle is `hearths.breast`' — imported, because
    `render_plan.py` already draws that exact rectangle as poché and two spellings of one
    breast is how a plan and a model come to disagree about where a fire is."""
    hearths = _mod("hearths")
    out = []
    for lv in plan.get("levels") or []:
        idx = lv.get("level", 0) or 0
        for r in lv.get("rooms") or []:
            for n, h in enumerate(r.get("hearth") or []):
                b = hearths.breast(r, h)
                if not b or b.get("undrawable"):
                    states.cannot(f"hearth {r['id']}-{n}",
                                  (b or {}).get("why") or "the breast could not be placed "
                                  "against the wall the record names",
                                  f"levels[].rooms[{r['id']}].hearth[{n}]", cls="hearth")
                    continue
                out.append(_solid(
                    f"{r['id']}-hearth-{n}", "hearth",
                    {"type": "box",
                     "origin": [round(b["x_ft"], 3), round(b["y_ft"], 3), 0.0],
                     "size": [round(b["width_ft"], 3), round(b["depth_ft"], 3), 0.0]},
                    "cut", "salmon",
                    {"record": f"levels[].rooms[{r['id']}].hearth[{n}]",
                     "also": ["build/hearths.py::breast"]},
                    "editorial", level=idx, room=r["id"],
                    note="the breast's projection is a judgment; its height is not modelled "
                         "and the box carries a zero rather than an invented one"))
    return out


def _spaces(plan, section):
    """Every placed room as a prism, for picking. NEVER DRAWN — a space is how a click finds
    a record, and drawing it would put a box inside every wall in the model."""
    storeys = {st.get("index"): st for st in (section.get("storeys") or [])}
    out = []
    for n, lv in enumerate(plan.get("levels") or []):
        idx = lv.get("level", n) or n
        st = storeys.get(idx) or {}
        z = st.get("grade_to_floor_ft")
        h = st.get("ceiling_ft")
        for r in lv.get("rooms") or []:
            g = r.get("geometry")
            if not g:
                continue
            out.append({
                "id": r["id"], "type": r.get("type"), "name": r.get("name") or r["id"],
                "level": idx, "element": r.get("block") or "main",
                "geometry": {"type": "prism",
                             "polygon": [[g["x_ft"], g["y_ft"]],
                                         [g["x_ft"] + g["width_ft"], g["y_ft"]],
                                         [g["x_ft"] + g["width_ft"], g["y_ft"] + g["depth_ft"]],
                                         [g["x_ft"], g["y_ft"] + g["depth_ft"]]],
                             "z0": z, "z1": (None if z is None or h is None else round(z + h, 3))},
                "drawn_ft": [g["width_ft"], g["depth_ft"]],
                "declared_ft": [r.get("width_ft"), r.get("length_ft")],
                "source": f"levels[].rooms[{r['id']}].geometry"})
    return out


def _marks(plan):
    """The relaxation triangles, at the positions the placement recorded. `render_plan.py`
    and `derive.js` are held to one rule for these (P7, OQ 33); this reads the RECORD they
    both read rather than becoming a third placer of them."""
    rep = (plan.get("geometry_report") or {}).get("relaxations") or {}
    out, unlocated = [], []
    for i, m in enumerate(rep.get("marks") or []):
        if m.get("x_ft") is None and m.get("y_ft") is None:
            unlocated.append({"id": f"relaxation-{i}", "why": "the placement recorded this "
                              "cut with no position, so it is named and not placed",
                              "source": f"geometry_report.relaxations.marks[{i}]"})
            continue
        out.append({"id": f"relaxation-{i}",
                    "at": [m.get("x_ft"), m.get("y_ft"), None],
                    "axis": m.get("axis"), "off_ft": m.get("off_ft"),
                    "level": m.get("level"),
                    "source": f"geometry_report.relaxations.marks[{i}]"})
    return {"relaxations": out, "unlocated": unlocated,
            "count": rep.get("count"), "max_off_grid_ft": rep.get("max_off_grid_ft")}


# ---------------------------------------------------------------- the record

def build_scene(plan, section, roof, elev=None, *, kit=None, packs=None):
    """The scene, from a PLACED plan and the section, roof and elevation built on it.

    `elev` is accepted and read only for the faces' bay centres; it is optional because the
    elevation REFUSES outside the classical-front family, and a refusal there must cost the
    reader the facade and not the building.
    """
    states = _States()
    compass = _mod("compass")
    north = compass.plan_north(plan)

    fp = section.get("footprint") or {}
    W, D = fp.get("width_ft"), fp.get("depth_ft")
    # The one place this file states the exterior wall's thickness in feet, for the frame below.
    _t_ext_ft = ((section.get("wall") or {}).get("exterior_in") or 0) / 12.0
    solids = []
    solids += _slabs(plan, section, states)
    solids += _walls(section, states)
    solids += _openings(elev, section, states)
    solids += _roof(plan, section, roof, states, elev)
    solids += _dormers(elev, states)
    solids += _hearths(plan, states)

    datums = _storey_datums(section, states)
    z_top = max([d["z_ft"] for d in datums] or [0.0])
    # A STACK STANDS ABOVE THE RIDGE, SO THE FRAME MUST REACH IT (WP-12.6). `z_top` is the
    # highest DATUM, and the highest datum is the ridge — but a chimney level with the ridge is
    # a hole in the roof, so `_chimneys` carries its cap above it and the stated frame then no
    # longer contained the model. Caught by `test_every_solid_lies_inside_the_declared_bounds`,
    # which WP-12.2 wrote after finding `bounds` the right SIZE in the wrong PLACE — the same
    # guard, catching the same field being wrong for the opposite reason.
    for _s in solids:
        if _s["class"] != "chimney":
            continue
        _g = _s["geometry"]
        _z = (_g["origin"][2] + _g["size"][2]) if _g["type"] == "box" else max(
            v[2] for v in _g["vertices"])
        z_top = max(z_top, _z)

    faces = {}
    for f in ("S", "N", "E", "W"):
        row = {"label": f"{ {'S': 'SOUTH', 'N': 'NORTH', 'E': 'EAST', 'W': 'WEST'}[f] } ELEVATION",
               "token": compass.face_token(f, north)}
        if elev and not elev.get("error"):
            if elev.get("entrance_face") == f:
                row["role"] = "THE ENTRANCE FRONT"
            fb = (elev.get("faces") or {}).get(f) or {}
            if fb:
                row["bays"] = {"centres_ft": fb.get("centres_ft"), "kinds": fb.get("kinds"),
                               "note": fb.get("note")}
                row["outside_width_ft"] = (fb.get("outside_width_in") or 0) / 12.0 or None
        faces[f] = row
    if not elev or elev.get("error") or not elev.get("faces"):
        states.cannot("the bay rhythm on every face",
                      (elev or {}).get("error") or "the elevation generator refuses outside "
                      "the classical-front family, so no face carries a bay layout",
                      "elevation.faces", cls="facade")

    grid = {"bays": (plan.get("footprint") or {}).get("bays"),
            "module_ft": (plan.get("footprint") or {}).get("bay_module_ft"),
            "source": "footprint"}

    spaces = _spaces(plan, section)
    counts = {"measured": 0, "editorial": 0, "derived": 0, "judgment": 0}
    for s in solids:
        counts[s["kind"]] = counts.get(s["kind"], 0) + 1

    n_nm = len(states.not_modelled)
    return {
        "scene_version": SCENE_VERSION,
        "plan_id": plan.get("id"), "style": plan.get("style"),
        "parti": plan.get("parti"), "massing": plan.get("massing"),
        "frame": {"units": "ft", "x": "east", "y": "north", "z": "up",
                  "origin": "main block SW corner at grade",
                  "north": {"plan_north_is_true_north": not north.get("stated"),
                            "bearing_deg": north.get("bearing_deg"),
                            "assumption": compass.assumption(north)}},
        "entrance_face": (elev or {}).get("entrance_face"),
        "faces": faces,
        # THE BOUNDS ARE THE OUTSIDE ENVELOPE AND THE ORIGIN IS THE CLEAR CORNER, so they start
        # NEGATIVE. WP-12.1 wrote `min: [0, 0, 0]` and `max: [W, D]` off the section's OUTSIDE
        # footprint while every solid in the scene is laid from the CLEAR SW corner — an
        # exterior wall grows outward to `-t`, and so do the slabs, the roof and now the
        # openings. So the stated frame was the right SIZE in the wrong PLACE, offset by one
        # exterior wall thickness (1.292 ft on the Tidewater plan): declared [0, 65.58] against
        # a drawn [-1.292, 64.292]. Nothing in the record disagreed with itself, because the
        # three agreement figures compare the walls, the slabs and the datums to each other and
        # none of them reads `bounds` — a viewer framing the model from it would have centred
        # the house half a foot off and nobody would have known why.
        #
        # Found by WP-12.2, from listening to the openings: they are the first solids whose own
        # `at` is printed in the record, and printing them beside `bounds` made the offset
        # legible. `tests/test_scene.py::test_every_solid_lies_inside_the_declared_bounds` is
        # the guard, and it is a CONTAINMENT rather than an equality for the reason the
        # agreement figures already carry: `section.footprint` is rounded to two places, so the
        # frame and the solids differ by up to 0.004 ft and rounding one to the other would be
        # OQ 48's error in a new place.
        "bounds": {"min": [round(-_t_ext_ft, 3), round(-_t_ext_ft, 3), 0.0],
                   "max": [round(W - _t_ext_ft, 3), round(D - _t_ext_ft, 3), round(z_top, 3)]},
        "grid": grid,
        "storeys": [{"id": st.get("id"), "index": st.get("index"),
                     "floor_z_ft": st.get("grade_to_floor_ft"),
                     "ceiling_z_ft": (None if st.get("grade_to_floor_ft") is None
                                      or st.get("ceiling_ft") is None
                                      else round(st["grade_to_floor_ft"] + st["ceiling_ft"], 3)),
                     "storey_height_ft": st.get("storey_height_ft"),
                     "source": f"section.storeys[{st.get('index')}]"}
                    for st in (section.get("storeys") or [])],
        "datums": datums,
        "elements": [{"id": b.get("id"), "role": b.get("role"),
                      "rect": {"x_ft": b.get("x_ft"), "y_ft": b.get("y_ft"),
                               "width_ft": b.get("width_ft"), "depth_ft": b.get("depth_ft")}}
                     for b in ((plan.get("footprint") or {}).get("blocks") or
                               [{"id": "main", "role": "main", "x_ft": 0.0, "y_ft": 0.0,
                                 "width_ft": W, "depth_ft": D}])],
        "solids": solids,
        "spaces": spaces,
        "marks": _marks(plan),
        "cut_height_ft": CUT_HEIGHT_FT,
        "not_modelled": states.not_modelled,
        "judgment": states.judgment,
        "provenance_counts": counts,
        "solver": (plan.get("geometry_report") or {}).get("solver"),
        "note": (f"Nothing here is drawn that is not in the record. {n_nm} thing"
                 f"{'' if n_nm == 1 else 's'} the record holds "
                 f"{'is' if n_nm == 1 else 'are'} not modelled; "
                 f"{'it is' if n_nm == 1 else 'they are'} listed, not omitted."),
    }


# ---------------------------------------------------------------- CLI

def _build_from_plan(path, engine="auto", candidates=DEFAULT_CANDIDATES):
    """Returns `(scene, section, error)`.

    The section comes back BESIDE the scene rather than inside it. A first version stashed it
    under a `_section` key for the CLI's convenience, which would have put a key in the record
    that the schema does not admit and that every consumer would have had to know to ignore —
    a private field in a published document. The scene is the document; the section is the
    thing it was measured against; a tuple says so."""
    geometry = _mod("geometry")
    structure = _mod("structure")
    roof_m = _mod("roof")
    elevation = _mod("elevation")
    plan = json.load(open(path))
    placed = geometry.solve(plan, None, candidates, engine=engine)
    if "error" in placed:
        return None, None, placed["error"]
    section = structure.build_section(placed, None, geometry_result=placed)
    if "error" in section:
        return None, None, section["error"]
    roof = roof_m.build_roof(placed, None, section=section)
    if "error" in roof:
        return None, None, roof["error"]
    elev = elevation.build_elevation(placed, None, section=section, roof=roof)
    return build_scene(placed, section, roof, None if "error" in elev else elev), section, None


def agreement(scene, section):
    """The measurement the phase is held to (PRD §9 item 5): does the scene agree with the
    records it was built from? Each number is REPORTED whether or not it is zero, because a
    check that only speaks when it fails cannot be watched for drift.

    The three are not the same kind of claim, and saying so matters:

    - `envelope_vs_slab` compares two things this file derived from ONE rule by two routes
      (the wall boxes, and `export_ifc.slab_boxes`). It should be zero to rounding, and a
      residue means the two readings of the exterior thickness have parted.
    - `rooms_inside_envelope` is a CONTAINMENT, not an equality: every placed room must lie
      within the walls. A negative number is a room outside its own house.
    - `datums_vs_storeys` re-reads the section's own storey heights off the finished record.

    Rounding lives in all three: the wall boxes come from the clear footprint plus twice the
    exterior thickness, the slabs from `slab_boxes`' own arithmetic, and the roof from
    `section.footprint`, which is rounded to two places. So the agreement is a small number
    rather than an exact zero, and the number is printed rather than a tolerance being
    asserted and forgotten.
    """
    def ext(pred):
        xs, ys = [], []
        for s in scene["solids"]:
            if not pred(s):
                continue
            g = s["geometry"]
            if g["type"] == "box":
                o, z = g["origin"], g["size"]
                xs += [o[0], o[0] + z[0]]
                ys += [o[1], o[1] + z[1]]
            elif g["type"] == "prism":
                for a, b in g["polygon"]:
                    xs.append(a)
                    ys.append(b)
        return (min(xs), max(xs), min(ys), max(ys)) if xs else None

    walls = ext(lambda s: s["class"] == "wall" and s.get("face"))
    slabs = ext(lambda s: s["class"] == "slab")
    out = {}
    if walls and slabs:
        out["envelope_vs_slab_ft"] = round(max(abs(a - b) for a, b in zip(walls, slabs)), 4)
    rooms = [p for sp in scene["spaces"] for p in sp["geometry"]["polygon"]]
    if walls and rooms:
        out["rooms_inside_envelope_ft"] = round(min(
            [min(p[0] - walls[0], walls[1] - p[0]) for p in rooms] +
            [min(p[1] - walls[2], walls[3] - p[1]) for p in rooms]), 4)
    d = {x["class"]: x["z_ft"] for x in scene["datums"]}
    worst = 0.0
    for st in section.get("storeys") or []:
        z = st.get("grade_to_floor_ft")
        if z is None:
            continue
        got = next((x["z_ft"] for x in scene["datums"] if x["id"] == f"floor-{st['id']}"), None)
        if got is not None:
            worst = max(worst, abs(got - z))
    out["datums_vs_storeys_ft"] = round(worst, 4)
    return out


def _report(scene, section=None):
    """The §9 measurement contract: what this package is held to, before and after."""
    by_class = {}
    for s in scene["solids"]:
        by_class[s["class"]] = by_class.get(s["class"], 0) + 1
    print(f"scene {scene['plan_id']} · {scene['style']}")
    print(f"  solids {len(scene['solids'])}: " +
          ", ".join(f"{k} {v}" for k, v in sorted(by_class.items())))
    print(f"  spaces {len(scene['spaces'])}   datums {len(scene['datums'])}")
    print(f"  not modelled {len(scene['not_modelled'])}: " +
          "; ".join(sorted({n['class'] for n in scene['not_modelled']})))
    print(f"  judgment {len(scene['judgment'])}")
    print(f"  provenance {scene['provenance_counts']}")
    if section is not None:
        ag = agreement(scene, section)
        print("  agreement " + ", ".join(f"{k} {v}" for k, v in sorted(ag.items())))
    print(f"  payload {len(json.dumps(scene))} bytes")
    print(f"  {scene['note']}")


def selftest():
    """Run inside `validate.py` rather than as a 51st check, so `TOTAL_CHECKS` does not move
    (WP-11.6's precedent for a check that goes inside an existing checker)."""
    bad = 0
    for name in ("tidewater-georgian-careful", "spec-builder-colonial"):
        scene, section, err = _build_from_plan(os.path.join(ROOT, "plans", f"{name}.json"),
                                               engine="heuristic")
        if err:
            print(f"FAIL scene {name}: {err}", file=sys.stderr)
            bad += 1
            continue
        ag = agreement(scene, section) if section else {}
        if ag.get("rooms_inside_envelope_ft", 0) < 0:
            print(f"FAIL scene {name}: a placed room lies outside the envelope "
                  f"({ag['rooms_inside_envelope_ft']} ft)", file=sys.stderr)
            bad += 1
        ids = [s["id"] for s in scene["solids"]]
        if len(ids) != len(set(ids)):
            print(f"FAIL scene {name}: duplicate solid ids", file=sys.stderr)
            bad += 1
        for s in scene["solids"]:
            if not s.get("source", {}).get("record") or not s.get("kind"):
                print(f"FAIL scene {name}: {s['id']} carries no source or no kind",
                      file=sys.stderr)
                bad += 1
                break
        print(f"  {name}: {len(scene['solids'])} solid(s), {len(scene['spaces'])} space(s), "
              f"{len(scene['not_modelled'])} not modelled, agreement "
              + ", ".join(f"{k} {v}" for k, v in sorted(ag.items())))
    print("OK — scene" if not bad else f"FAIL — scene ({bad})")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("plan", help="a plan record, or the word 'selftest'")
    ap.add_argument("--engine", default="auto", choices=["auto", "cp", "heuristic"])
    ap.add_argument("--candidates", type=int, default=DEFAULT_CANDIDATES)
    ap.add_argument("--out", help="write the scene record here")
    a = ap.parse_args()
    if a.plan == "selftest":
        return selftest()
    scene, section, err = _build_from_plan(a.plan, engine=a.engine, candidates=a.candidates)
    if err:
        print(f"could not build a scene: {err}", file=sys.stderr)
        return 1
    _report(scene, section)
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(scene, fh, indent=1)
        print(f"  wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
