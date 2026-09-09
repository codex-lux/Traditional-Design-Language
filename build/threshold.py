#!/usr/bin/env python3
"""threshold.py -- the stoop at the entrance door and the stack at the gable end (WP-11.4).

Two things this corpus has stated in full since Phase 1 and no drawing has ever read. The
kit says the stoop is a masonry platform 122.4 in wide reached by risers of 6 7/8 in; it
says the stack is 22 in square; and `hearth_position`'s own rule says the mass of it "sits
outside the heated volume in summer". None of that reached a plate. This pass writes both
onto the placed record so both renderers can draw them and neither can derive them -- the
rule WP-6.2 settled for openings and WP-11.3 kept for furniture.

WHY THE STACK IS IN A FILE CALLED `threshold`, WHICH IS A MECHANICAL REASON AND IS STATED
RATHER THAN DRESSED UP AS A CONCEPTUAL ONE. Both passes read the CASCADE-RESOLVED kit, and
`resolve_slots` costs 13.3 ms per style, measured. `place()` runs inside `/api/plan/evaluate`,
which the infrastructure audit measured as the whole server's bound at 338 ms of CPU, so a
second module would have resolved the same kit twice on that route for the sake of a tidier
filename. One module, one cache, and this paragraph so nobody has to guess.

NOT A LEAF, AND THAT IS DELIBERATE. `build/storeys.py`, `build/assemblies.py` and
`build/furniture.py` import nothing from `build/` because they are called from
`openings.py`, which `geometry.py` calls, which `structure.py` loads -- a sibling import
there closes a cycle. This file loads `resolve_kit`, and that is safe because
`resolve_kit` reaches exactly two modules, `proportion_engine` and (through it)
`construction_vocabulary`, and neither reaches `geometry`. Checked by
`tests/test_threshold_pass.py`, which walks the import graph rather than trusting this
sentence.

WHAT IT REFUSES, WHICH IS MOST OF WHAT IT WAS ASKED TO DO:

  * A COLUMN. `PLAN-OF-ACTION.md` asks for "columns and their answering pilasters where
    `portico_bays = 1`". Read that way it would put a portico on `tidewater-georgian`, a
    shipped reference plan whose own kit calls a portico ATYPICAL there and whose canonical
    porch is `stoop-only`. `portico_bays`' own slot rule carries the precondition in its
    first clause -- "WHERE A PORTICO OCCURS it is one bay wide" -- and 5 of the 8 nodes that
    resolve a `portico_bays` have no portico among their canonical porch types. That is
    WP-8.4's finding in a new place: a parameter read without the condition its own record
    states. And where a portico IS canonical the column has no width: exactly ONE node in 164
    (`neoclassical-revival`) states a column diameter in inches, and it states no
    `portico_bays`. The intersection of the three facts a drawn column needs is EMPTY across
    the corpus, so this pass places no column anywhere and says so per node.
  * WHICH ROOMS TAKE A HEARTH. `PLAN-OF-ACTION.md`: "Which rooms take a hearth is not in any
    record: raise it, do not read it." `oq/which-rooms-take-the-hearth`.
  * A STACK WHOSE SIDE OF THE WALL NOBODY STATED. `SIDE_OF` below is a CLOSED table on
    `build/construction_vocabulary.py`'s precedent, and it decides `exterior` or `interior`
    for exactly two of the fifteen `hearth_position` variant ids in use. Everything else is
    recorded as unmappable WITH A REASON and the stack is not placed.
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_ROOF_FORM = "side-gable"


def _mod(name, path):
    # build/modcache.py, never a local loader (OQ 28; tests/test_modcache.py counts loads)
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


_GRAMMAR = None


def grammar():
    global _GRAMMAR
    if _GRAMMAR is None:
        with open(os.path.join(ROOT, "threshold", "grammar.json"), "r", encoding="utf-8") as fh:
            _GRAMMAR = json.load(fh)
    return _GRAMMAR


def rule(rid):
    for block in ("placement_rules", "refusal_rules"):
        for r in grammar().get(block) or []:
            if r["id"] == rid:
                return r
    return {}


def _graded(rid):
    """Every entry this pass writes names the rule that put it there and that rule's GRADE.
    WP-11.3's discipline: a reader must be able to tell what the corpus said from what we
    decided, on the record and not only in a report."""
    r = rule(rid)
    return {"rule": rid, "grade": r.get("grade")}


# ---------------------------------------------------------------- the resolved kit, once
_RESOLVED = {}
_GRAPH = None


def _graph(rk):
    """`resolve_kit.load_graph()` re-reads and re-walks dist/taxonomy.json every call --
    18 ms, measured -- and it is not cached in that module. Cached here because this pass
    asks for it once per STYLE and a sweep over the sixteen shipped plans has a dozen
    distinct styles: 216 ms of re-reading one artefact, on the route the infrastructure
    audit measured as the whole server's bound."""
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = rk.load_graph()
    return _GRAPH


def resolved_slots(style):
    """The CASCADE-resolved slot record, cached per style. 13.3 ms uncached, measured on
    `tidewater-georgian`; this pass asks for it once per plan and the cache carries it
    across the sixteen plans a sweep places."""
    if style not in _RESOLVED:
        rk = _mod("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
        g = _graph(rk)
        try:
            slots, _ = rk.resolve_slots(g, rk.chain_for(g, style), rk.scope_for(g, style))
        except SystemExit:
            # resolve_kit exits on an unknown node; a plan naming a style with no kit is a
            # could-not-evaluate here and never a pass.
            slots = None
        _RESOLVED[style] = slots
    return _RESOLVED[style]


def _param(slots, slot, name):
    if not slots:
        return None
    return ((slots.get(slot) or {}).get("parameters") or {}).get(name)


def _canonical(rec):
    return [v["id"] for v in ((rec or {}).get("variants") or []) if v.get("status") == "canonical"]


# ---------------------------------------------------------------- roof form and ridge axis
# MOVED HERE FROM build/roof.py, which now delegates. Both are pure functions of the plan
# and the massing -- no section, no structure, no ridge height -- and the plan layer needs
# the ridge AXIS to know which two walls are the gable ends. Spelling that arithmetic a
# second time in the placement path is the thing this corpus refuses most consistently, and
# `tests/test_threshold_pass.py` pins roof.py's whole output byte-identical across the move.
def roof_form_for(plan, massing):
    """plan.declared.roof_form governs; falls back to the massing's own first-listed
    roof_default with an explicit note when undeclared -- 'unjudged is not passed' at the
    roof layer. A declared form outside the massing's roof_default list is NOT an error --
    that list is typical forms, not an exhaustive permitted set -- but is noted."""
    declared = (plan.get("declared") or {}).get("roof_form")
    defaults = massing.get("roof_default") or [DEFAULT_ROOF_FORM]
    if declared:
        note = None if declared in defaults else (
            f"'{declared}' is declared but is not in massing '{massing.get('id')}''s own roof_default list "
            f"({', '.join(defaults)}) -- not an error, that list is typical forms, not an exhaustive set, but worth a second look.")
        return declared, note
    return defaults[0], f"No roof_form declared; used massing '{massing.get('id')}''s first default ('{defaults[0]}')."


def ridge_axis(form):
    """Which plan axis the ridge runs along, for the two single-ridge gable forms.
    side-gable: ridge parallel to the wider/entrance-parallel dimension (axis 'x', the
    convention render_plan.py and structure.py already use -- S/N walls run along x).
    front-gable: ridge perpendicular to the entrance (axis 'y', W/E walls run along y)."""
    return "x" if form in ("side-gable", "hip") else "y"


def gable_end_points(W, D, axis):
    """The two gable ends' mid-wall points. ONE spelling, read by build/roof.py for the
    stack's HEIGHT and by hearth_pass below for its PLAN."""
    if axis == "x":
        return [(0.0, D / 2.0), (W, D / 2.0)]
    return [(W / 2.0, 0.0), (W / 2.0, D)]


def gable_end_walls(axis):
    """The compass letters of the two gable-end walls, in the same order as
    gable_end_points. x-axis ridge -> the ends are W and E; y-axis ridge -> S and N."""
    return ("W", "E") if axis == "x" else ("S", "N")


# ---------------------------------------------------------------- the closed hearth table
# WHERE THE HEARTH IS, AND WHICH FACE OF THE WALL ITS MASS STANDS ON -- a CLOSED TABLE and
# not a substring test, on build/construction_vocabulary.py's precedent (WP-8.4: "a substring
# test over a surface cannot answer a question about an assembly").
#
# THERE ARE TWO VOCABULARIES FOR ONE FACT AND THEY ARE NOT THE SAME VOCABULARY. A kit's
# `hearth_position` slot names variant IDS; a massing's `hearth` field is free prose, and
# SEVEN of the forty massings state a DISJUNCTION there, in six distinct words -- `gable-end or corner`,
# `gable-end-paired or central-stack`, `party-wall or end`, `central or end`, `interior or
# end`, `central or none` -- naming two positions and choosing neither. Both vocabularies
# are here, in separate tables, because a checker that proved one total while the other went
# unread would be exactly the guard-that-cannot-fire this repo keeps finding.
#
# `build/roof.py::chimney_positions` still reads the massing field with `"gable-end" in
# hearth`, which answers TRUE for two of the three disjunctions above, and that fallback
# fires on 135 of 159 styles. It is NOT changed here: it decides a HEIGHT, changing it moves
# real output on three massings, and that measurement belongs to whoever makes it.
# `oq/the-massing-states-its-hearth-in-prose-and-a-substring-test-reads-it`.
#
# Each entry is (side, at_a_gable_end, why) with side in {"exterior", "interior", None} and
# at_a_gable_end in {True, False, None}. None is UNJUDGED in both columns and never a
# default: a token neither table carries fails build/check_threshold.py.
SIDE_OF = {
    # --- the kit's `hearth_position` variant ids
    "exterior-end": ("exterior", True,
                     "names the end AND the face: the mass is outside the wall"),
    "interior-paired-flanking-ridge": ("interior", False,
                                       "stacks flanking the ridge stand inside the envelope and are not at an end"),
    "gable-end-paired": (None, True, "names the END and the PAIRING and not which face of it the mass stands on"),
    "central-stack": (None, False, "a central stack is not at a gable end at all"),
    "central-open-hearth": (None, False, "an open hearth in the floor of a hall has no stack to have a side"),
    "corner": (None, False, "a corner hearth has no gable-end stack -- tidewater-georgian's own record says so in the variant's note"),
    "corner-fireplace-with-hood": (None, False, "as `corner`"),
    "distributed": (None, None, "names the count and its spread, and no position on any wall"),
    "flett-open-hearth-no-chimney": (None, False, "states that there is no chimney"),
    "inserted-masonry-stack-in-former-screens-passage": (None, False, "names the bay the stack was inserted into, which is not an end wall"),
    "lobby-entry-single-dominant-stack": (None, False, "a lobby-entry stack stands against the entrance, not at an end"),
    "open-hearth-central-arestue": (None, False, "as `central-open-hearth`"),
    "open-hearth-in-open-hall": (None, False, "as `central-open-hearth`"),
    "round-backed-fireplace-ashlar-hood-in-hall": (None, False, "names the firebox and its hood, not the stack's position"),
    "wall-fireplace-with-stack": (None, None, "names a wall fireplace generally and no wall in particular"),
}

MASSING_HEARTH = {
    "gable-end-paired": (None, True, "as the kit token of the same name: the end and the pairing, not the face"),
    "gable-end": (None, True, "names the end and not the face"),
    "end": (None, True, "names the end and not the face; and `end` is the gable end only where the ridge runs the other way, which this word does not say"),
    "central": (None, False, "a central stack"),
    "central-mass": (None, False, "a central mass"),
    "central-stack": (None, False, "a central stack"),
    "distributed": (None, None, "names the spread and no position"),
    "living-room-focal": (None, False, "names the room the hearth is the focus of, not a wall"),
    "party-wall": (None, False, "a party wall is shared with the next house and is not a gable end this drawing owns"),
    "gable-end or corner": (None, None, "A DISJUNCTION. The massing names two positions and chooses neither."),
    "gable-end-paired or central-stack": (None, None, "A DISJUNCTION, and the two branches are at opposite ends of the plan."),
    "party-wall or end": (None, None, "A DISJUNCTION."),
    "central or end": (None, None, "A DISJUNCTION."),
    "central or none": (None, None, "A DISJUNCTION, and one branch is that there is no hearth."),
    "interior or end": (None, None, "A DISJUNCTION."),
}


def hearth_facts(token, from_massing=False):
    """(side, at_a_gable_end, why) for one hearth token, from the table its vocabulary
    belongs to. A token in neither table raises nothing and answers UNJUDGED in both
    columns; build/check_threshold.py is what fails the build on it, so a corpus edit
    cannot quietly acquire a default here."""
    t = MASSING_HEARTH if from_massing else SIDE_OF
    return t.get(token, (None, None, f"`{token}` is not in this file's closed table"))


def at_gable_end(canonical, from_massing=False):
    """(verdict, why) -- True where at least one canonical position is at a gable end, False
    where every one of them is somewhere else, None where the record does not say."""
    verdicts = [hearth_facts(v, from_massing) for v in canonical]
    if any(g is True for _s, g, _w in verdicts):
        return True, None
    if verdicts and all(g is False for _s, g, _w in verdicts):
        return False, "; ".join(f"`{v}`: {w}" for v, (_s, _g, w) in zip(canonical, verdicts))
    return None, ("the record does not say whether this hearth is at a gable end: "
                  + "; ".join(f"`{v}`: {w}" for v, (_s, _g, w) in zip(canonical, verdicts)))


def stack_side(canonical, from_massing=False):
    """(side, why). `exterior` or `interior` where the node's own canonical hearth positions
    map to exactly one side; None, with the reason, where they map to none or to both. Both
    is a CONTRADICTION and is reported as one -- never resolved by preferring a side, which
    would be inventing the answer the records disagree about."""
    sides, unmapped = set(), []
    for v in canonical:
        s, _g, why = hearth_facts(v, from_massing)
        if s:
            sides.add(s)
        else:
            unmapped.append(f"`{v}`: {why}")
    if len(sides) == 1:
        return sides.pop(), None
    if len(sides) > 1:
        return None, ("the record's own canonical hearth positions name BOTH faces of the end wall "
                      f"({', '.join(sorted(sides))}) -- a contradiction in the record, not a choice "
                      f"for a drawing")
    if unmapped:
        return None, ("no canonical hearth position names which face of the end wall the mass "
                      "stands on: " + "; ".join(unmapped))
    return None, "the record states no canonical hearth position at all"


# ---------------------------------------------------------------- the stoop
SERVICE_CLASSES = ("service", "work", "storage", "sanitary")


def _fclass(room, C):
    return ((C.get("rooms") or {}).get(room.get("type")) or {}).get("function_class")


def _entrance_doors(plan, face, C):
    """(entrance doors, service doors that landed on the entrance face).

    Every exterior door on the entrance face -- MINUS any carried by a service room. A door
    is not `rank`ed on any record in this corpus (the field exists at plan schema 0.3.0 and
    nothing writes it), so the only structured fact available is the ROOM'S OWN
    `function_class`, and `steps_and_stoop` describes the ENTRANCE composition: a scullery
    door does not get a 10 ft platform because the placer put it on the front.

    THE SPLIT IS NOT HYPOTHETICAL AND IT IS ENGINE-DEPENDENT. On the search engine the
    Tidewater plan puts one exterior door on the S front, the porch's. On CP-SAT it puts the
    KITCHEN's there too -- legal by the record, which declares S among that room's exterior
    walls, and a service door on the entrance front all the same. The second is returned
    separately so the sheet can name it rather than dress it as an entrance."""
    entrance, service = [], []
    for lv in plan.get("levels", [])[:1]:          # the ground floor and only it
        for r in lv.get("rooms", []):
            for d in (r.get("doors") or []):
                if d.get("to") != "exterior" or d.get("unplaced"):
                    continue
                if d.get("wall") != face or d.get("position_ft") is None:
                    continue
                (service if _fclass(r, C) in SERVICE_CLASSES else entrance).append((r, d))
    return entrance, service


def _other_exterior_doors(plan, face):
    out = []
    for lv in plan.get("levels", [])[:1]:
        for r in lv.get("rooms", []):
            for d in (r.get("doors") or []):
                if d.get("to") == "exterior" and not d.get("unplaced") and d.get("wall") != face:
                    out.append((r, d))
    return out


def entrance_pass(plan, C, report):
    """The stoop and its flight at the entrance door, and every refusal by name.

    Writes plan["threshold"]. Never writes a room, a dimension or a door."""
    style = plan.get("style")
    slots = resolved_slots(style)
    face = (plan.get("context") or {}).get("entrance_faces")
    fp = plan.get("footprint") or {}
    W, D = fp.get("width_ft"), fp.get("depth_ft")
    t_ft = float(((fp.get("wall") or {}).get("exterior_in") or 0.0)) / 12.0
    out = {"steps": [], "supports": [], "unplaced": [], "figures": {}}
    plan["threshold"] = out
    if not slots:
        out["unplaced"].append({"what": "the stoop", "reason":
                                f"style '{style}' has no kit this pass can resolve -- could not evaluate",
                                **_graded("th-stoop-at-the-entrance-door")})
        return out
    if not face:
        out["unplaced"].append({"what": "the stoop", "reason":
                                "the plan states no context.entrance_faces, so no door on this record is "
                                "the entrance door -- could not evaluate",
                                **_graded("th-stoop-at-the-entrance-door")})
        return out

    depth_ft = _stoop_depth_ft(slots)
    figs = {
        "platform_width_in": _figure(slots, "platform_width_in", "th-platform-width"),
        "riser_height_in": _figure(slots, "riser_height_in", "th-riser-height"),
        "tread_depth_in": _figure(slots, "tread_depth_in", "th-tread-depth", band="mid"),
        "riser_count": _figure(slots, "riser_count_from_grade", "th-riser-count", band="low"),
        "stoop_depth_ft": depth_ft,
    }
    out["figures"] = figs

    missing = [k for k in ("platform_width_in", "riser_height_in", "tread_depth_in",
                           "riser_count", "stoop_depth_ft") if figs[k].get("value") is None]
    if missing:
        out["unplaced"].append({"what": "the stoop", "reason":
                                "this style's cascade states no "
                                + ", ".join(missing)
                                + " -- unjudged, and a flight drawn from a number nobody wrote "
                                  "down is the thing this corpus refuses",
                                **_graded("th-stoop-at-the-entrance-door")})
    else:
        ent, svc = _entrance_doors(plan, face, C)
        for r, d in ent:
            out["steps"].append(_one_stoop(r, d, face, t_ft, figs, W, D))
        for r, d in svc:
            out["unplaced"].append({
                "what": f"steps at the {d['wall']} door of {r['id']}",
                "reason": f"an exterior door on the ENTRANCE face ({face}) carried by a room "
                          f"whose function_class is '{_fclass(r, C)}' -- the placement put a "
                          f"service door on the entrance front, and steps_and_stoop describes "
                          f"the entrance composition, so it is named here rather than given one",
                **_graded("th-only-the-entrance-door")})

    for r, d in _other_exterior_doors(plan, face):
        out["unplaced"].append({
            "what": f"steps at the {d['wall']} door of {r['id']}",
            "reason": "steps_and_stoop describes the ENTRANCE composition -- its platform is "
                      "'the entrance composition plus about 18 in of platform each side' -- and no "
                      "record in this corpus states a service door's steps",
            **_graded("th-only-the-entrance-door")})

    sup = _supports(slots, style)
    if sup.get("placed"):
        out["supports"].extend(sup["placed"])
    out["unplaced"].extend(sup["unplaced"])
    return out


def _figure(slots, name, rule_id, band=None):
    """One `steps_and_stoop` figure, with the record's OWN `kind` where the record gives a
    figure and `editorial` only where a BAND had to be reduced to one number.

    THE DIRECTION THAT IS EASY TO GET WRONG IS THIS ONE. Marking every figure `editorial` is
    the safe-looking error and it is still an error: `federal-style` resolves
    `riser_count_from_grade` as a DERIVED 4 from `storey-graduation`, and calling that a
    judgment tells a reader the corpus said less than it did. `kind` here is the record's
    unless this function chose the number.

    `band="low"` takes the band's low end, `band="mid"` its midpoint, and the two rules that
    use them are graded separately in threshold/grammar.json with a reason apiece -- the
    flight's tread count is the only thing on this drawing that claims ground OUTSIDE the
    house, so it takes the least the band permits; a tread is bounded above and below by use,
    so it takes the middle."""
    p = _param(slots, "steps_and_stoop", name) or {}
    out = {"value": None, "kind": None, **_graded(rule_id)}
    if not p:
        out["reason"] = f"this style's resolved steps_and_stoop states no {name}"
        return out
    if "computed_at" in p and p["computed_at"].get("value") is not None:
        out["value"], out["kind"] = p["computed_at"]["value"], p.get("kind", "derived")
    elif p.get("value") is not None:
        out["value"], out["kind"] = p["value"], p.get("kind")
    elif p.get("range") and band:
        r = p["range"]
        out["value"] = r[0] if band == "low" else (r[0] + r[1]) / 2.0
        out["band"], out["kind"] = r, "editorial"
        out["reduced_from_a_band"] = band
    elif p.get("range"):
        out["band"] = p["range"]
        out["reason"] = (f"{name} is stated as a band and this figure has no rule for reducing "
                         f"one -- unjudged")
    return out


def _stoop_depth_ft(slots):
    """THE ONE FIGURE THREE RECORDS ALL ADMIT. The corpus states the stoop's depth three
    times, in two slots, and the three do not agree: `steps_and_stoop.platform_depth_in`
    bands it [36, 60] in, `porch_depth.stoop_depth_ft` bands it [4, 6] ft = [48, 72] in, and
    `porch_depth.stoop_min_depth_in` states a floor of 48 in. A 36 in stoop is inside the
    first band and below the third. 48 in is the only value all three admit -- the low end of
    one band, the midpoint of the other, and the stated minimum exactly -- and that is why it
    is taken rather than either midpoint. Where the three do not intersect, this returns None
    with the reason and nothing is drawn."""
    pd = (_param(slots, "steps_and_stoop", "platform_depth_in") or {}).get("range")
    sd = (_param(slots, "porch_depth", "stoop_depth_ft") or {}).get("range")
    mn = (_param(slots, "porch_depth", "stoop_min_depth_in") or {}).get("value")
    lo, hi = 0.0, math.inf
    stated = []
    if pd:
        lo, hi = max(lo, pd[0]), min(hi, pd[1]); stated.append(f"platform_depth_in {pd} in")
    if sd:
        lo, hi = max(lo, sd[0] * 12.0), min(hi, sd[1] * 12.0); stated.append(f"stoop_depth_ft {sd} ft")
    if mn is not None:
        lo = max(lo, float(mn)); stated.append(f"stoop_min_depth_in {mn} in")
    if not stated:
        return {"value": None, "reason": "no slot states the stoop's depth", **_graded("th-platform-depth")}
    if lo > hi:
        return {"value": None, "stated": stated, **_graded("th-platform-depth"),
                "reason": "the corpus's own statements of the stoop's depth do not intersect: "
                          + "; ".join(stated) + " -- unjudged, not averaged"}
    return {"value": round(lo / 12.0, 3), "stated": stated, "kind": "editorial",
            **_graded("th-platform-depth")}


def _one_stoop(room, door, face, t_ft, figs, W, D):
    """The platform and the flight, in model feet, outside the block.

    THE ROOM'S OWN FLOOR IS THE PLATFORM WHERE THE RECORD SAYS SO. Where the entrance door
    is carried by a room typed `entry-porch`, that room IS the raised platform -- it is
    placed, dimensioned and drawn already -- and drawing a second one in front of it would
    put two thresholds on one house. Only the flight goes outside. Where the door opens from
    an interior room the platform is drawn at the kit's own `platform_width_in`."""
    pos = float(door["position_ft"])
    g = room.get("geometry") or {}
    plat_w = float(figs["platform_width_in"]["value"]) / 12.0
    depth = float(figs["stoop_depth_ft"]["value"])
    n = int(figs["riser_count"]["value"])
    tread = float(figs["tread_depth_in"]["value"]) / 12.0

    along_horizontal = door["wall"] in ("S", "N")
    # the extent of the wall this flight descends from, so a stoop is never wider than the
    # room behind it -- the record's own rectangle, never a guess
    if g:
        w_lo = g["x_ft"] if along_horizontal else g["y_ft"]
        w_hi = w_lo + (g["width_ft"] if along_horizontal else g["depth_ft"])
    else:
        w_lo, w_hi = (0.0, W) if along_horizontal else (0.0, D)
    half = plat_w / 2.0
    lo = max(w_lo, min(pos - half, w_hi - plat_w))
    hi = min(w_hi, lo + plat_w)
    lo = max(w_lo, hi - plat_w)

    is_porch = room.get("type") == "entry-porch"
    entry = {"room": room["id"], "wall": door["wall"], "door_position_ft": pos,
             "riser_count": n, "riser_height_in": figs["riser_height_in"]["value"],
             "tread_depth_in": figs["tread_depth_in"]["value"],
             "platform_is_the_room": is_porch,
             **_graded("th-stoop-at-the-entrance-door")}
    # the outward coordinate of the block's OUTSIDE face on this wall
    face0 = {"S": -t_ft, "N": D + t_ft, "W": -t_ft, "E": W + t_ft}[door["wall"]]
    at = face0
    if not is_porch:
        entry["platform"] = _band(door["wall"], lo, hi, at, depth)
        at = face0 - depth if door["wall"] in ("S", "W") else face0 + depth
    # the flight: n risers means n - 1 treads on the ground before the platform is reached
    treads = max(n - 1, 1)
    entry["flight"] = _band(door["wall"], lo, hi, at, treads * tread)
    entry["nosings"] = _nosings(door["wall"], lo, hi, at, treads, tread)
    entry["flight_width_ft"] = round(hi - lo, 3)
    return entry


def _band(wall, lo, hi, at, depth):
    """A rectangle lying outside `wall`, `depth` ft deep, running from `lo` to `hi` along it.
    `at` is the coordinate of its INNER edge, already outside the wall body."""
    if wall == "S":
        return {"x_ft": round(lo, 3), "y_ft": round(at - depth, 3),
                "width_ft": round(hi - lo, 3), "depth_ft": round(depth, 3)}
    if wall == "N":
        return {"x_ft": round(lo, 3), "y_ft": round(at, 3),
                "width_ft": round(hi - lo, 3), "depth_ft": round(depth, 3)}
    if wall == "W":
        return {"x_ft": round(at - depth, 3), "y_ft": round(lo, 3),
                "width_ft": round(depth, 3), "depth_ft": round(hi - lo, 3)}
    return {"x_ft": round(at, 3), "y_ft": round(lo, 3),
            "width_ft": round(depth, 3), "depth_ft": round(hi - lo, 3)}


def _nosings(wall, lo, hi, at, treads, tread):
    """The nosing lines INSIDE the flight, parallel to the wall -- `treads - 1` of them,
    because the flight rectangle's own two edges are the top and bottom nosings and drawing
    those again would put two lines on one edge. A flight of one tread is a rectangle and
    takes no line at all. This is what makes a flight read as a flight and not as a slab,
    which is the whole of what a plan says about a step."""
    out = []
    for i in range(1, treads):
        off = i * tread
        if wall in ("S", "W"):
            c = at - off
        else:
            c = at + off
        if wall in ("S", "N"):
            out.append({"line": [round(lo, 3), round(c, 3), round(hi, 3), round(c, 3)]})
        else:
            out.append({"line": [round(c, 3), round(lo, 3), round(c, 3), round(hi, 3)]})
    return out


def _supports(slots, style):
    """The portico's columns and their answering pilasters -- and the reason there are none.

    THREE FACTS ARE NEEDED TO DRAW A COLUMN AND NO NODE IN THIS CORPUS HAS ALL THREE: a
    canonical porch type that IS a portico, a bay count, and a diameter in inches. Measured
    over all 159 nodes that carry a kit: 23 have a canonical portico, 8 resolve a `portico_bays`,
    3 have both,
    and exactly 1 (`neoclassical-revival`, [20, 28] in, measured) states a diameter -- and
    that one states no bay count. The intersection is empty. This function reports which of
    the three each node is missing rather than supplying one."""
    out = {"placed": [], "unplaced": []}
    pt = (slots or {}).get("porch_type") or {}
    can = _canonical(pt)
    bays = ((pt.get("parameters") or {}).get("portico_bays") or {}).get("value")
    ps = (slots or {}).get("porch_support") or {}
    dia = ((ps.get("parameters") or {}).get("base_diameter_in")
           or (((slots or {}).get("column") or {}).get("parameters") or {}).get("base_diameter_in"))
    is_portico = any("portico" in v for v in can)
    if not is_portico:
        out["unplaced"].append({
            "what": "the portico's columns",
            "reason": (f"'{style}' states no canonical portico (canonical porch type"
                       f"{'s' if len(can) != 1 else ''}: {', '.join(can) or 'none'})"
                       + (f", and its `portico_bays` of {bays} is conditioned by its own slot rule "
                          f"-- 'where a portico occurs it is one bay wide' -- on a condition this "
                          f"node does not meet" if bays is not None else "")),
            **_graded("th-a-portico-only-where-one-is-canonical")})
        return out
    if bays is None:
        out["unplaced"].append({"what": "the portico's columns",
                                "reason": f"'{style}' makes a portico canonical and states no portico_bays "
                                          f"-- unjudged, and a bay count is not derivable from the porch's depth",
                                **_graded("th-a-portico-only-where-one-is-canonical")})
        return out
    if not dia:
        out["unplaced"].append({"what": "the portico's columns",
                                "reason": f"'{style}' states the column's height in DIAMETERS and never a "
                                          f"diameter, and one node in this corpus states one in inches -- see "
                                          f"build/check_threshold.py, which re-derives the four counts "
                                          f"every run rather than quoting them; "
                                          f"and it is not this one -- unjudged, and a column drawn at an "
                                          f"invented width is an invented measurement",
                                **_graded("th-a-column-needs-a-diameter")})
        return out
    out["unplaced"].append({"what": "the portico's columns",
                            "reason": "a node with all three facts exists for the first time; the placement "
                                      "is not built, because until now nothing could reach this branch",
                            **_graded("th-a-column-needs-a-diameter")})
    return out


# ---------------------------------------------------------------- the stack
def hearth_pass(plan, C, report):
    """The gable-end stacks, from the node's OWN kit and the massing, and never the cascade.

    THE OWN KIT, FOR THE SAME REASON build/roof.py READS IT: an inherited `forbidden` is a
    prohibition an ancestor made and the descendant never overturned, and is safe to read
    from the cascade; an inherited CANONICAL VARIANT is a positive claim the descendant never
    made, and is not, until somebody has adjudicated the slot on that node. `colonial-revival`
    is the case that proves it here as it proved it there: its `hearth_position` is `open`, so
    the cascade hands it `central-open-hearth` from `english-gothic`, seven steps up and
    date-gated to 1180-1450. The massing's own `hearth` field is the honest fallback.

    THE SIZE IS THE ONE THING READ FROM THE CASCADE, and that is deliberate: `stack_plan_in`
    is a DIMENSION, and a dimension arriving through the lineage is what the cascade is for.
    `tidewater-georgian`'s own kit states the stack's height above the ridge and not its plan,
    which comes from `georgian-colonial-american` as `part * 8` = 22 in."""
    style = plan.get("style")
    fp = plan.get("footprint") or {}
    W, D = fp.get("width_ft"), fp.get("depth_ft")
    t_ft = float(((fp.get("wall") or {}).get("exterior_in") or 0.0)) / 12.0
    out = {"stacks": [], "unplaced": [], "source": None, "side": None,
           "hearth_rooms": None,
           "hearth_rooms_note": "NOT READ. Which rooms take a hearth is stated in no record in "
                                "this corpus -- `hearth_position.rule` says the end rooms and "
                                "nothing says which rooms those are on a placed plan. "
                                "oq/which-rooms-take-the-hearth."}
    plan["hearths"] = out
    own = ((C["kits"].get(style, {}).get("slots") or {}).get("hearth_position") or {})
    canonical = _canonical(own)
    massing = C["massings"].get(plan.get("massing"), {})
    m_hearth = massing.get("hearth")
    from_massing = False
    if canonical:
        out["source"] = f"kit hearth_position slot: {', '.join(canonical)}"
    elif m_hearth:
        out["source"] = f"massing '{massing.get('id')}' hearth: {m_hearth}"
        canonical = [m_hearth]
        from_massing = True
    if not out["source"]:
        out["unplaced"].append({"what": "the stacks", "reason":
                                "no own-kit hearth_position and no massing hearth field to place a "
                                "stack from -- unjudged", **_graded("th-stack-at-the-gable-end")})
        return out
    gable, gwhy = at_gable_end(canonical, from_massing)
    if gable is not True:
        out["unplaced"].append({"what": "the stacks", "reason":
                                (f"{out['source']} does not call for a gable-end hearth: {gwhy}"
                                 if gable is False else
                                 f"{out['source']} -- {gwhy}"),
                                **_graded("th-stack-at-the-gable-end")})
        return out

    side, why = stack_side(canonical, from_massing)
    out["side"] = side
    if side is None:
        out["unplaced"].append({"what": "the stacks", "reason": why,
                                **_graded("th-which-side-of-the-end-wall")})
        return out

    size = (_param(resolved_slots(style), "chimney", "stack_plan_in") or {})
    s_in = size.get("computed_at", {}).get("value") if "computed_at" in size else size.get("value")
    # AND WHETHER THAT FIGURE IS A DECISION SOMEBODY STILL OWES (WP-12.9). `brick-course`'s rule
    # is flagged `judgment: true` -- "twenty-two inches on the default coursing is between sizes;
    # the mason will build 18 or 27" -- and the snapshot of it in the kit carried no flag at all
    # until WP-12.9, so this function read a settled measurement out of a deferred decision. The
    # elevation has disclosed it since WP-5.11 and the scene refuses a solid over it (WP-12.6);
    # the PLAN drew a poche square and its tooltip called it a measurement, which is the one
    # surface of the three where a reader cannot tell a decision from a fact.
    # AND ITS BASIS TRAVELS WITH IT. A judgment with no basis named is what this corpus forbids
    # one step further than a figure with no source -- the shape the two-Phase-11 merge met when
    # the hearth tooltip's "Morris 1734, judgment" became a bare "judgment". The parameter's own
    # note is what the record at hand states, so that is what is read: one reader, one sentence.
    s_judgment = bool(size.get("judgment"))
    s_basis = size.get("note") if s_judgment else None
    if s_in is None:
        out["unplaced"].append({"what": "the stacks", "reason":
                                f"'{style}' states no chimney stack_plan_in anywhere in its cascade "
                                f"-- unjudged, and a stack drawn at an invented size is an invented "
                                f"measurement", **_graded("th-stack-plan-size")})
        return out
    if not W or not D:
        out["unplaced"].append({"what": "the stacks", "reason":
                                "no footprint on this record", **_graded("th-stack-at-the-gable-end")})
        return out

    form, _note = roof_form_for(plan, massing)
    if form in ("hip", "gable-on-hip"):
        out["unplaced"].append({"what": "the stacks", "reason":
                                f"the declared roof form is '{form}', which has no full gable-end wall "
                                f"to run a stack through -- the same refusal build/roof.py makes, and "
                                f"for the same reason", **_graded("th-stack-at-the-gable-end")})
        return out
    axis = ridge_axis(form)
    s = float(s_in) / 12.0
    for (x, y), wall in zip(gable_end_points(W, D, axis), gable_end_walls(axis)):
        rect = _stack_rect(wall, s, t_ft, W, D, side, x if axis == "y" else y)
        out["stacks"].append({"wall": wall, "side": side, "stack_plan_in": s_in,
                              "stack_plan_judgment": s_judgment,
                              "stack_plan_basis": s_basis,
                              "source": out["source"], **rect,
                              **_graded("th-stack-at-the-gable-end")})
    return out


def _stack_rect(wall, s, t, W, D, side, along):
    """The stack's square, centred on `along` (the mid-depth of the end wall, where the
    double pile's own partition falls) and seated on the face the record names.

    The block's edge is the wall's INSIDE face (WP-11.1), so the outside face of a wall is
    `t` beyond it. An EXTERIOR stack projects its whole plan dimension beyond that outside
    face; an INTERIOR one projects it inward from the inside face. That the 22 in is the
    stack's own section and not a figure measured from somewhere else is a reading of its
    note -- "a stack is 1.5 x 2 bricks (13.5 x 18 in), 2 x 2 (18 in), 2 x 3 (18 x 27 in)",
    which are section dimensions -- and is graded as one."""
    lo = round(along - s / 2.0, 3)
    if wall == "W":
        x0 = -t - s if side == "exterior" else 0.0
        return {"x_ft": round(x0, 3), "y_ft": lo, "width_ft": round(s, 3), "depth_ft": round(s, 3)}
    if wall == "E":
        x0 = W + t if side == "exterior" else W - s
        return {"x_ft": round(x0, 3), "y_ft": lo, "width_ft": round(s, 3), "depth_ft": round(s, 3)}
    if wall == "S":
        y0 = -t - s if side == "exterior" else 0.0
        return {"x_ft": lo, "y_ft": round(y0, 3), "width_ft": round(s, 3), "depth_ft": round(s, 3)}
    y0 = D + t if side == "exterior" else D - s
    return {"x_ft": lo, "y_ft": round(y0, 3), "width_ft": round(s, 3), "depth_ft": round(s, 3)}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    pc = _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
    geometry = _mod("geometry", os.path.join(ROOT, "build", "geometry.py"))
    plan = json.load(open(sys.argv[1], encoding="utf-8"))
    placed = geometry.solve(plan, engine="heuristic")
    print(json.dumps({"threshold": placed.get("threshold"), "hearths": placed.get("hearths")},
                     indent=1))


if __name__ == "__main__":
    main()
