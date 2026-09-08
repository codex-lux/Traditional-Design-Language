#!/usr/bin/env python3
"""arrangement.py — the measurements a house's ARRANGEMENT can supply (WP-9.1).

Raised by Lucas on 1 September 2026 against a rendered sheet: a 10 x 30 ft kitchen, a
portico off the axis of the passage it serves, a dining room landlocked in the middle of
the house, a stair in the corner of a misshapen hall. Every part well-formed, the whole
meaningless -- this project's founding failure mode, one level above where Phase 6 left it.

Twenty-eight faults in this corpus carry a test whose `measurable_from` is `plan`, and they
name exactly those complaints: `passage-that-is-a-corridor`, `stair-at-the-front-door`,
`service-route-through-the-formal-plan`, `the-room-nobody-enters`. Twenty-seven of the
twenty-eight came back UNJUDGED on the corpus's own most carefully authored plan, because
the fault layer's measurement namespace is `plan.measurements` (empty on fifteen of sixteen
records), the per-room width and length, and build/elevation.py's ~110 elevation
quantities. Not one plan-arrangement variable was supplied by anything. The named-error
corpus had the vocabulary and no measurement layer underneath it.

This module is that layer, and it is TWO functions rather than one because of a ruling.
OQ 54 was reversed on 26 Aug and the reversal has a boundary: `plan_check`'s `drawn` layer
is the ONLY layer that may read placement. So:

  · `declared(plan)` is geometry-blind. The door graph, the declared dimensions, the room
    list. It feeds the fault layer, which judges the house the record DECLARES, and it
    works on a plan nobody has placed. A test pins that it returns the same dict whether or
    not a placement exists.
  · `grouping_vars(plan, placed=..., footprint=...)` supplies what the groupings' own
    `internal_rules` tests name, and takes the placement where a rule can only be answered
    once the house is drawn -- the passage against its facade, above all.
  · The checks that read a placement DIRECTLY live in `plan_check.drawn_layer`, not here,
    because that is the layer OQ 54's reversal licensed to do it. This module holds no
    `drawn()` function; an earlier draft of this docstring promised one, which was a false
    statement about the code of exactly the kind WP-6.4 was written about.

A fault is evaluated in exactly ONE layer, whichever its variable honestly lives in.
Evaluating a fault in both would let the two answers disagree about one house, which is the
shape of defect this package exists to remove.

WHAT THIS MODULE MAY NOT DO. It may not invent a measurement. `NOT_DERIVABLE` names every
plan variable this corpus cannot honestly supply today and says why for each, and the
filter runs at the point measurements are returned rather than at each call site -- the
`elevation.NOT_MODELLED` mechanism, adopted here for the same reason it exists there: OQ 52
found twelve invented constants convicting both reference plans, and a comment saying "we
do not model this" is not a guard. To take a name off the list, model the thing in the same
commit.

  python3 build/arrangement.py plans/<id>.json    # print what this plan can supply
  python3 build/arrangement.py selftest
"""
from __future__ import annotations

import json
import os
import sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, path):
    # build/modcache.py, never a local loader (OQ 28; tests/test_modcache.py counts loads)
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


# ---------------------------------------------------------------- what cannot be derived
#
# Read the reason before adding to this dict, and read it twice before taking a name OFF.
# Every entry here is a variable some fault test names and this corpus cannot measure. A
# name in this dict is filtered out of the returned measurements, so the fault it belongs
# to reports COULD NOT EVALUATE -- which is the honest answer and is not a pass.
NOT_DERIVABLE = {
    # OQ 52's exact class. roof.py places stacks in ELEVATION space and the only figure
    # available for a breast (brick-course's 22 in) is flagged `judgment: true`;
    # `elevation.NOT_MODELLED` already refuses the four elevation spellings on that ground.
    # Re-deriving it here under a plan-shaped name would be that defect wearing a new hat.
    #
    # THE REASONS BELOW WERE REWRITTEN BY WP-11.4 AND THE OLD ONES ARE WHY. They said "no
    # record carries a chimney PLAN dimension" and "the plan has no chimney footprint", and
    # both stopped being true the moment `hearth` landed on a plan room (schema 0.7.0):
    # `build/hearths.py::breast` returns a rectangle in model feet and `render_plan.py` draws
    # it. **The entries STAY, and the distinction is the point.** The projection exists and is
    # Morris 1734's depth column interpolated, carrying `judgment: true` — and this corpus's
    # rule is that a judgment figure may be DRAWN but never published as a MEASUREMENT (the
    # chimney's 22 in is the standing precedent). So the refusal is unchanged and its GROUND
    # has moved from "there is no such thing in the plan" to "there is, and it is a judgment".
    # Leaving the old wording would have been WP-6.4's finding exactly: a comment asserting a
    # state of the world that the package one directory over had just falsified.
    "chimney_breast_projection_or_wall_thickness_in":
        "the plan carries a chimney breast since WP-11.4, but its projection is Morris 1734 "
        "interpolated and flagged judgment; a judgment figure may be drawn and not measured",
    "central_chimney_base_dimension_ft":
        "as chimney_breast_projection_or_wall_thickness_in -- a hearth states its wall and "
        "opening, and nothing in the corpus states a central stack's base in plan",
    "firebox_depth_in":
        "a hearth states its opening width, never its depth; no firebox is modelled in plan",
    "wall_thickness_in":
        "the plan record states no wall thickness; construction_type says what a wall is OF, not how thick",
    # No HVAC model exists anywhere in this corpus -- no slot, no kit parameter, no line in
    # any renderer. A proxy counted off room adjacency would be a guess with a number on it.
    "duct_runs_crossing_the_principal_passage":
        "no duct, plenum or mechanical route is modelled anywhere in the corpus",
    # The sightline needs the table, and the table needs furniture ARRANGEMENT, which Lucas
    # refused as a sizing input (OQ 92: "the tail wagging the dog"). A door-adjacency proxy
    # would be a second spelling of `powder-room-on-the-dining-room`'s own adjacency rule,
    # which the adjacency layer already reads from rooms/dining-room.json.
    "wc_doors_within_the_dining_table_sightline":
        "needs the dining table placed; furniture arrangement beyond a stated wall run is refused (OQ 92)",
    # The wet-wall question is about a PLUMBING wall's thickness, which no record states.
    # The arrangement half of `stack-with-nowhere-to-land` -- is there anything under the
    # fixture at all -- is already the drawn layer's `stacks_over` check.
    "upper_floor_wet_fixtures_landing_on_a_wall_of_at_least_5_5_in":
        "no plumbing-wall thickness is modelled; the arrangement half is the drawn stacks_over check",
    "upper_floor_wet_fixtures":
        "as above -- the denominator would be honest and the numerator invented, which is worse than neither",
    # No interior trim model. NOTE for whoever models it: `one-trim-grade-for-every-room`'s
    # expression is `rooms_with_full_cornice / finished_rooms` and divides by a count, so it
    # needs an `applies_when` the day the denominator becomes suppliable -- OQ 89's lesson,
    # that supplying a withheld measurement arms every rule which presupposed it.
    "rooms_with_full_cornice":
        "no interior trim grade is modelled per room",
    "finished_rooms":
        "as rooms_with_full_cornice; and its fault divides by this count, so it needs an applies_when first",
    # Material and opening-schedule questions that happen to carry measurable_from: plan.
    # Not arrangement, and out of this package's scope -- stated rather than silently absent.
    "plan_offset_at_material_change_in":
        "a cladding-return question, not an arrangement one; out of WP-9.1's scope",
    "net_clear_opening_sqft":
        "an egress-sash question; the plan states no sash operation or clear opening",
    "net_clear_opening_height_in":
        "as net_clear_opening_sqft",
    "largest_single_leaf_net_clear_opening_sqft":
        "as net_clear_opening_sqft",
    "swing_or_fold_clearance_outside_the_opening_ft":
        "the plan models no garage door operation",
    "toplight_area_sf":
        "no toplight or roof glazing is modelled in plan",
    "patio_width":
        "no patio or enclosing range is modelled; the site layer states neither",
    "enclosing_range_height":
        "as patio_width",
    "setback_from_lot_line_at_rough_flank_ft":
        "the site record states no lot lines",
    "street_frontage_ft":
        "the site record states no frontage; supplied only where a plan's site block declares one",
    # REFUSED AFTER BEING BUILT, AND THE REASON IS THE WHOLE OF WP-5.13's RULE. The first
    # draft of this module derived a plant room's absence as a MEASURED ZERO, on the
    # argument that a plan record states its entire room list so "there is none" is a fact
    # the record asserts. It convicted BOTH reference plans on the first sweep -- the
    # deliberately ordinary spec plan AND the careful Tidewater Georgian written to see
    # whether the validator stays quiet on a good house.
    #
    # That is the OQ 52 signature: an invented constant convicting the plans that ship. The
    # dormer precedent says exactly why it is invented. `declared.dormer` earned its zero by
    # gaining THREE states -- key absent means could not evaluate, "none" means the author
    # looked and there are none -- because "what made them refusable was never the geometry;
    # it was that an absent dormer and an unstatable one were indistinguishable". A plan
    # whose room list has no plant room and a plan that does not model mechanical services
    # at all are indistinguishable here in exactly the same way, and neither reference plan
    # models services anywhere. To take this name off the list, give the plan schema a way
    # to say "services considered, none enclosed" and supply the zero only in that case.
    # AND THE SECOND REASON IS STRONGER THAN THE FIRST. There is no room type for a plant
    # room in this corpus: the 60 records in `rooms/` hold no `mechanical-room`, no
    # `plant-room`, no `utility-room`, and the nearest neighbours (`cellar`, `workshop`,
    # `laundry`) are all rooms a house has for other reasons. So a plan record cannot state
    # that it HAS one either, and the fault is unjudgeable from a plan record in both
    # directions until the catalogue gains the type.
    "dedicated_plant_room_area_sqft":
        "an absent plant room and an unmodelled one are indistinguishable here (the WP-5.13 dormer test), "
        "and the room catalogue has no type that could state the presence of one",
}


# ---------------------------------------------------------------- the route model
#
# THIS IS AN EDITORIAL CALL AND IT IS MARKED AS ONE. Four fault tests ask about "daily"
# circulation -- `ceremonial-front-door`, `the-room-nobody-enters` -- and a door graph
# cannot answer that on its own: it says what connects, never who walks it. So the routes
# below are a stated model of household movement, quoting the corpus prose each is read
# from, and `check_basis` verifies the quotations against the records they name exactly as
# it does for openings/grammar.json. An editorial call whose citation cannot be checked is
# a guess wearing a citation.
#
# It is deliberately SMALL. Every route here is one the corpus's own room records already
# describe in words; nothing is added because it seemed plausible.
ROUTE_MODEL = {
    "id": "arrangement-daily-routes",
    "kind": "editorial",
    "note": (
        "EDITORIAL THROUGHOUT, AND NO SOURCE IS RECORDED (the OQ 18 form). A door graph "
        "states what connects to what; it cannot state who walks where, and four fault "
        "tests in this corpus ask exactly that. Rather than let those faults stay "
        "permanently unjudged, or answer them from a proxy nobody declared, the household "
        "movements below are stated as a closed model, each quoting the room record whose "
        "prose it reads. They are the routes this corpus already describes in words: the "
        "arrival route from the street door, the service route from kitchen to dining "
        "room, and the daily route from the family's own entrance to the rooms it uses. "
        "A route absent from this table is not a route this corpus denies -- it is one "
        "nobody has written down, and the fault that needs it stays unjudged."
    ),
    "routes": [
        {
            "id": "rt-arrival",
            "from": {"function_class": "threshold"},
            "to": {"function_class": "public"},
            "basis": "rooms/centre-passage.json adjacency.should_adjoin[parlor].why: \"the "
                     "passage's whole point is to serve the principal rooms symmetrically; parlor "
                     "one side, dining room the other, is the canonical arrangement\".",
            "note": "The visitor's route: street door to the best room, which is what a passage is for.",
        },
        {
            "id": "rt-service-food",
            "from": {"type": "kitchen"},
            "to": {"type": "dining-room"},
            "basis": "rooms/kitchen.json adjacency.must_adjoin[dining-room].why: \"Food travels hot "
                     "and the route must not cross the entry sequence or a public circulation\".",
            "note": "The one route this corpus states as a hard adjacency with an explicit via list.",
        },
        {
            "id": "rt-family-entry",
            "from": {"type": "mudroom"},
            "to": {"type": "kitchen"},
            "basis": "rooms/kitchen.json adjacency.should_adjoin[mudroom].why: \"THE SHOPPING ROUTE. "
                     "In every modern house the groceries come in from the drive, and the distance "
                     "from that door to the refrigerator is walked twice a week with both hands full "
                     "for the life of the building. Nobody draws it and everybody feels it.\"",
            "note": "The daily family route, and the one the corpus is most explicit about.",
        },
    ],
}


# ---------------------------------------------------------------- grouping rule tests
#
# A grouping's `internal_rules[].test` is a plain SENTENCE -- "passage_width_ft /
# facade_width_ft between 0.18 and 0.27" -- and not the {expression, direction, threshold}
# object faults and style constraints use. There is no schema for a grouping-level test in
# this corpus, which is most of the reason 26 of the 84 rules carry one and essentially
# nothing evaluated any of them: `build/roof.py` reads two, for the ridge ratios, and
# `plan_check` surfaced only the rules that have NO test, as "check by hand".
#
# ONE PARSER, and it lives here. roof.py's `_parse_prose_between` delegates to this rather
# than keeping its own -- it handled `between` alone, and a second spelling of a rule is
# what this corpus has been bitten by three times.
_DIRECTIONS = ("at-least", "at-most", "equals", "between")


def parse_rule_test(test):
    """Turn a grouping rule's sentence into the structured test shape core._eval_test wants.

    Returns None where the sentence is not one of the four forms in use, which is the
    honest answer: an unparsed rule is unjudged, never passed.
    """
    import re
    if not test or not isinstance(test, str):
        return None
    s = test.strip()
    m = re.search(r"^(.*?)\s+between\s+([\d.]+)\s+and\s+([\d.]+)\s*$", s)
    if m:
        return {"expression": m.group(1).strip(), "direction": "between",
                "threshold": float(m.group(2)), "upper": float(m.group(3))}
    m = re.search(r"^(.*?)\s+(at-least|at-most|equals)\s+(.+?)\s*$", s)
    if m:
        expr, direction, thr = m.group(1).strip(), m.group(2), m.group(3).strip()
        try:
            return {"expression": expr, "direction": direction, "threshold": float(thr)}
        except ValueError:
            # `landing_depth_in at-least stair_width_in` -- the threshold is a VARIABLE.
            # Fold it into the expression as a difference so one evaluator handles both:
            # (a - b) at-least 0 is the same claim and needs no second code path.
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", thr):
                if direction == "at-least":
                    return {"expression": f"({expr}) - {thr}", "direction": "at-least", "threshold": 0.0}
                if direction == "at-most":
                    return {"expression": f"({expr}) - {thr}", "direction": "at-most", "threshold": 0.0}
                return {"expression": f"({expr}) - {thr}", "direction": "equals", "threshold": 0.0}
    return None


# ---------------------------------------------------------------- catalogue access
def _catalog():
    core = _mod("core", f"{ROOT}/mcp_server/core.py")
    return core._data()


def _rooms_of(plan):
    """Every room on the plan, id -> record, with its level index remembered."""
    out, level_of = {}, {}
    for i, lv in enumerate(plan.get("levels") or []):
        for r in lv.get("rooms") or []:
            out[r["id"]] = r
            level_of[r["id"]] = i
    return out, level_of


def _rt(C, r):
    """The room-catalogue record for a plan room, or None if the type is unknown."""
    return C["rooms"].get(r.get("type"))


def _fclass(C, r):
    rt = _rt(C, r)
    return (rt or {}).get("function_class")


def _door_graph(rooms, placed_only=False):
    """Undirected adjacency over DECLARED doors, plus the set of rooms with a door out.

    `placed_only` drops the openings the placement could not realise, which is what the
    drawn layer wants and what the declared layer must not do."""
    edges = {rid: set() for rid in rooms}
    outside = set()
    for rid, r in rooms.items():
        for d in (r.get("doors") or []):
            if placed_only and d.get("unplaced"):
                continue
            t = d.get("to")
            if t == "exterior":
                outside.add(rid)
                continue
            if t in edges:
                edges[rid].add(t)
                edges[t].add(rid)
    return edges, outside


def _hops(edges, starts, goal):
    """Fewest rooms entered walking from any of `starts` to `goal`, or None if unreachable.

    Counts THRESHOLDS crossed, which is what the fault tests ask for: a room you reach
    without leaving the room you started in is one threshold away."""
    if not starts or goal is None:
        return None
    seen = set(starts)
    q = deque((s, 0) for s in starts)
    while q:
        cur, d = q.popleft()
        if cur == goal:
            return d
        for nxt in edges.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, d + 1))
    return None


def _path(edges, start, goal):
    """One shortest path start -> goal as a list of room ids, or None."""
    if start is None or goal is None:
        return None
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            out = []
            while cur is not None:
                out.append(cur)
                cur = prev[cur]
            return list(reversed(out))
        for nxt in edges.get(cur, ()):
            if nxt not in prev:
                prev[nxt] = cur
                q.append(nxt)
    return None


def _match(C, r, sel):
    """Does a room match a route-model selector?"""
    if "type" in sel and r.get("type") != sel["type"]:
        return False
    if "function_class" in sel and _fclass(C, r) != sel["function_class"]:
        return False
    return True


# ---------------------------------------------------------------- the declared half
def declared(plan, C=None):
    """Measurements derivable WITHOUT reading any placement.

    Geometry-blind by construction: this function never touches `room.geometry`, so it is
    safe to feed the fault layer, which judges the declared house. It works on a plan
    nobody has placed -- which is most of them.
    """
    C = C or _catalog()
    rooms, level_of = _rooms_of(plan)
    if not rooms:
        return {}
    m = {}
    edges, outside = _door_graph(rooms)
    ground = [rid for rid in rooms if level_of.get(rid) == 0]

    # --- the front door and what it opens into
    # The threshold room is the one with a door to the exterior whose type is a threshold or
    # circulation room. A house whose only exterior door lands in a living room is exactly
    # what `front-door-into-the-living-room` is about, so the ENTRY room is whatever the
    # front door opens into, threshold or not.
    entry = None
    for rid in ground:
        if rid not in outside:
            continue
        fc = _fclass(C, rooms[rid])
        if fc in ("threshold", "circulation"):
            entry = rid
            break
    if entry is None:
        entry = next((rid for rid in ground if rid in outside), None)
    if entry is not None:
        r = rooms[entry]
        w, l = r.get("width_ft"), r.get("length_ft")
        if w and l:
            # `front-door-into-the-living-room` asks for the area of the space you arrive
            # in. Where arrival is a room in its own right that is its area; where the
            # front door opens straight into a living room the fault's own premise is met
            # and the number it wants is that room's -- the test's threshold does the rest.
            m["entry_space_floor_area_sqft"] = round(w * l, 1)

    # --- doors that close, which is what makes a room a room in a room-based style
    # A cased opening is not a door. The plan record states `type` per door since schema
    # 0.3.0; where it does not, the opening grammar's own resolution decides -- but this
    # layer is geometry-blind and the grammar needs no geometry, so it is honest here.
    LEAFED = {"swing", "double", "sliding", "pocket", "bifold"}
    closable, seen_pairs = 0, set()
    specs = set()
    for rid in ground:
        for d in (rooms[rid].get("doors") or []):
            t = d.get("to")
            if t == "exterior":
                specs.add((d.get("width_ft"), d.get("type") or "swing"))
                continue
            if t not in rooms or level_of.get(t) != 0:
                continue
            pair = tuple(sorted((rid, t)))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            dt = d.get("type")
            specs.add((d.get("width_ft"), dt or "swing"))
            if dt is None or dt in LEAFED:
                closable += 1
    if seen_pairs or entry is not None:
        m["closable_ground_floor_room_doors"] = closable
    if specs:
        # `every-door-the-same-door` counts how many DIFFERENT doors a house specifies.
        m["distinct_door_specifications_per_house"] = len(specs)

    # --- the passage's own clear width, from the declaration
    for rid, r in rooms.items():
        if r.get("type") in ("centre-passage", "cross-passage"):
            w, l = r.get("width_ft"), r.get("length_ft")
            if w and l:
                m.setdefault("passage_clear_width_ft", round(min(w, l), 2))
                m.setdefault("open_central_passage_width_ft", round(min(w, l), 2))

    # --- the secondary bedroom's short dimension
    # Closets are separate rooms in this corpus, so a declared width IS a clear width here.
    sec = []
    for rid, r in rooms.items():
        if r.get("type") in ("bedroom", "bedchamber"):
            w, l = r.get("width_ft"), r.get("length_ft")
            if w and l:
                sec.append(min(w, l))
    if sec:
        m["secondary_bedroom_clear_short_dimension_ft"] = round(min(sec), 2)

    # --- the main block's depth
    #
    # NOT from `plan["footprint"]`, and the reason is the layer's whole contract. That block
    # is written by build/geometry.py during a solve, so reading it would make this
    # geometry-blind function answer differently once a placement existed -- and the fault
    # layer it feeds is the one OQ 54 ruled must never see a placement. An author may also
    # declare a footprint by hand, and the record cannot distinguish the two, which is the
    # same indistinguishability that refuses the plant room above.
    #
    # `derive_footprint` is safe because it reads the DECLARED record and the parti and no
    # placement at all: given the same declaration it returns the same block whether or not
    # anybody has ever solved the plan. Wrapped for the reason the elevation fold is: a plan
    # it cannot read loses this one measurement, not the run.
    try:
        GEO = _mod("geometry", f"{ROOT}/build/geometry.py")
        parti = None
        pid = plan.get("parti")
        if pid:
            core = _mod("core", f"{ROOT}/mcp_server/core.py")
            try:
                parti = core.load_parti(pid)
            except Exception:
                parti = None
        fp = GEO.derive_footprint(plan, parti) if parti else None
        if fp:
            W, H = fp[0], fp[1]
            m.setdefault("main_block_depth_ft", round(min(W, H), 2))
    except Exception:
        pass

    # --- routes: the service route, and the daily routes the model states
    dining = next((rid for rid, r in rooms.items() if r.get("type") == "dining-room"), None)
    kitchen = next((rid for rid, r in rooms.items() if r.get("type") == "kitchen"), None)
    formal = {rid for rid, r in rooms.items()
              if _fclass(C, r) in ("public", "dining") and r.get("type") != "dining-room"}
    if kitchen and dining:
        p = _path(edges, kitchen, dining)
        if p is not None:
            # A service route CROSSING a formal room: count the formal rooms the shortest
            # kitchen-to-dining path passes THROUGH, endpoints excluded. rooms/kitchen.json
            # states the rule and names the licensed intermediates in its own `via` list.
            m["service_routes_crossing_a_formal_room"] = sum(1 for x in p[1:-1] if x in formal)

    # --- thresholds from the public way to the principal bedroom
    principal = next((rid for rid, r in rooms.items()
                      if r.get("type") == "primary-bedroom"), None)
    if principal is not None and outside:
        h = _hops(edges, outside, principal)
        if h is not None:
            m["thresholds_from_public_way_to_principal_bedroom"] = h

    # --- the daily-route questions, under the stated model
    if entry is not None:
        routes = []
        for spec in ROUTE_MODEL["routes"]:
            srcs = [rid for rid, r in rooms.items() if _match(C, r, spec["from"])]
            dsts = [rid for rid, r in rooms.items() if _match(C, r, spec["to"])]
            for s in srcs:
                for d_ in dsts:
                    if s == d_:
                        continue
                    p = _path(edges, s, d_)
                    if p:
                        routes.append(p)
        if routes:
            # `ceremonial-front-door`: does anybody actually walk through the formal entry
            # hall in the course of a day, or is it a room kept for visitors who never come?
            m["daily_circulation_routes_through_the_formal_entry_hall"] = sum(
                1 for p in routes if entry in p)
            # `the-room-nobody-enters`: the same question asked of a principal room.
            best = None
            for rid, r in rooms.items():
                if _fclass(C, r) != "public":
                    continue
                n = sum(1 for p in routes if rid in p[1:-1] or rid in p)
                best = n if best is None else min(best, n)
            if best is not None:
                m["principal_room_daily_routes_through_it"] = best

    # --- openly connected principal rooms (the exception `open-plan-in-a-room-based-style`
    #     uses to license a genuinely open modern plan)
    openish = 0
    seen_pairs = set()
    for rid, r in rooms.items():
        if _fclass(C, r) not in ("public", "dining"):
            continue
        for d in (r.get("doors") or []):
            t = d.get("to")
            if t not in rooms or _fclass(C, rooms[t]) not in ("public", "dining"):
                continue
            pair = tuple(sorted((rid, t)))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            if (d.get("type") or "swing") in ("open", "cased-opening"):
                openish += 1
    if seen_pairs:
        m["openly_connected_principal_rooms"] = openish

    # --- only where the record states the thing
    site = plan.get("site") or {}
    if isinstance(site.get("street_frontage_ft"), (int, float)):
        m["street_frontage_ft"] = float(site["street_frontage_ft"])

    return _filter(m)


def grouping_vars(plan, C=None, placed=None, footprint=None):
    """Variables the grouping layer's own `internal_rules` tests name.

    Supplied from the record where the quantity is declared, and from the placement where
    it is only knowable once the house is drawn (`placed` and `footprint` are passed in by
    the drawn layer; without them the placement-dependent names are simply absent, and the
    rules that need them report could-not-evaluate). Twenty-six rules carry a test and
    nineteen of those are `hard`; what this cannot supply stays unjudged.
    """
    C = C or _catalog()
    rooms, level_of = _rooms_of(plan)
    m = {}

    def dim(rid_types, which):
        got = []
        for rid, r in rooms.items():
            if r.get("type") in rid_types:
                w, l = r.get("width_ft"), r.get("length_ft")
                if w and l:
                    got.append(min(w, l) if which == "short" else max(w, l))
        return min(got) if got else None

    # --- declared
    m["bedroom_short_dimension_ft"] = dim(("bedroom", "bedchamber"), "short")
    m["mudroom_clear_width_ft"] = dim(("mudroom",), "short")
    m["gallery_depth_ft"] = dim(("gallery",), "short")
    m["piazza_depth_ft"] = dim(("piazza",), "short")
    m["porch_depth_ft"] = dim(("sleeping-porch", "porch", "entry-porch"), "short")
    m["bed_wall_clear_ft"] = dim(("primary-bedroom",), "short")
    for rid, r in rooms.items():
        if r.get("type") == "hall":
            w, l = r.get("width_ft"), r.get("length_ft")
            if w and l:
                m.setdefault("hall_area", w * l)
        if r.get("type") == "parlor":
            w, l = r.get("width_ft"), r.get("length_ft")
            if w and l:
                m.setdefault("parlor_area", w * l)
    # the principal room's ceiling, which the piazza core states a floor for
    ceils = []
    for lv in (plan.get("levels") or []):
        for r in (lv.get("rooms") or []):
            if _fclass(C, r) in ("public", "dining"):
                ch = r.get("ceiling_ft") or lv.get("floor_to_ceiling_ft")
                if ch:
                    ceils.append(float(ch))
    if ceils:
        m["principal_ceiling_ft"] = max(ceils)
    # the stair's own arithmetic, straight off the record WP-6.2 gave it
    st = plan.get("stair") or {}
    if st.get("landing_depth_ft"):
        m["landing_depth_in"] = float(st["landing_depth_ft"]) * 12.0
    if st.get("width_ft"):
        m["stair_width_in"] = float(st["width_ft"]) * 12.0
    if st.get("riser_in"):
        # one riser dimension for the whole flight is what the record carries, so the
        # variation IS zero -- a measured zero, not an assumed one: the generator derives
        # every riser from one storey height and cannot produce a varying one.
        m["riser_variation_in"] = 0.0
    # a garage door onto a bedroom: the declared adjacency answers it
    gtb = 0
    for rid, r in rooms.items():
        if r.get("type") != "garage":
            continue
        for d in (r.get("doors") or []):
            t = rooms.get(d.get("to"))
            if t and _fclass(C, t) == "sleeping":
                gtb += 1
    if any(r.get("type") == "garage" for r in rooms.values()):
        m["garage_to_bedroom_adjacency"] = gtb
        gw = [d.get("width_ft") for rid, r in rooms.items() if r.get("type") == "garage"
              for d in (r.get("doors") or []) if d.get("to") == "exterior" and d.get("width_ft")]
        if gw:
            m["garage_door_width_ft"] = max(gw)
    # the primary suite's share of the sleeping floor
    suite, sleeping = 0.0, 0.0
    for rid, r in rooms.items():
        w, l = r.get("width_ft"), r.get("length_ft")
        if not (w and l):
            continue
        if level_of.get(rid) != (1 if len(plan.get("levels") or []) > 1 else 0):
            continue
        sleeping += w * l
        if r.get("type") in ("primary-bedroom", "primary-bathroom",
                             "walk-in-closet", "dressing-room"):
            suite += w * l
    if sleeping > 0 and suite > 0:
        m["suite_area_sf"] = round(suite, 1)
        m["sleeping_floor_area_sf"] = round(sleeping, 1)

    # --- BOTH ENDS OF THE PASSAGE, AND THE STAIR THAT OPENS OFF IT (WP-11.9)
    #
    # Two of the twenty prose rules the Tidewater diagnosis's Part VI lists. Both are DECLARED
    # facts -- a door's `to` is authored even though its `wall` is solver output -- so they are
    # answerable on all sixteen plan records rather than on the two that carry a placement.
    #
    # An end of the passage counts as doored where the door reaches outdoors, DIRECTLY or through
    # a threshold room. That second clause is not a loosening: the Tidewater passage's front door
    # is `to: porch`, because the porch is a room in this model and the front door is between the
    # two, so a reader counting only `to: exterior` would find one end where the record states
    # two -- and would report the diagnosis's own B4 against a record that does not commit it.
    #
    # LEVEL 0 ONLY, and the type is preferred rather than pooled. The Tidewater record carries a
    # second `centre-passage` on the floor above, which is the landing corridor and has no ends to
    # door; and where a record ever carries a `centre-passage` AND a `cross-passage` on the ground
    # floor, the grouping is about the first and the second is likely a service run. Among several
    # of ONE type the WORST is taken, not the best: reporting the best would be the flattering
    # direction, which is the OQ 52 family. One of the sixteen records carries a passage at all,
    # and it carries exactly one, so neither clause is exercised by this corpus -- both are driven
    # in `tests/test_compass.py`.
    ground = [rid for rid, r in rooms.items() if level_of.get(rid) == 0]
    passages = [rid for rid in ground if rooms[rid].get("type") == "centre-passage"] \
        or [rid for rid in ground if rooms[rid].get("type") == "cross-passage"]
    if passages:
        counts = []
        for rid in passages:
            # DISTINCT REACHES, NOT DOORS, AND A THRESHOLD ROOM MUST ITSELF REACH OUTDOORS
            # (audit, 7 Sep 2026). The first version counted qualifying DOORS against a rule
            # whose own `measures.quantity` is `passage_ends_reached`, so two doors into the
            # same porch scored 2, and any door into a threshold-class room scored whether or
            # not that room had a way out -- a passage opening into a mid-run vestibule and an
            # entrance hall passed a HARD rule with neither end doored. Both were false passes
            # on the flattering side, which is the OQ 52 family this function's own comment
            # commits against, committed in the sentence making the commitment.
            #
            # WHAT IT MEASURES IS A NECESSARY CONDITION AND NOT A SUFFICIENT ONE, and the
            # distinction is a property of the LAYER rather than a shortcut. A door's `wall`
            # and `position_ft` are solver output; only its `to` is authored. So the declared
            # record can say that a passage reaches the outdoors by two independent routes and
            # cannot say that those routes are at its two ENDS. Two reaches is what a doored
            # pair of ends implies; the ends themselves are the ALIGNMENT half, which was split
            # out of this rule at WP-11.9, carries no test, and is named to the reader for
            # exactly this reason.
            reaches = set()
            for d in (rooms[rid].get("doors") or []):
                to = d.get("to")
                if to == "exterior":
                    reaches.add("exterior")
                elif to in rooms and _fclass(C, rooms[to]) == "threshold":
                    if any(dd.get("to") == "exterior" for dd in (rooms[to].get("doors") or [])):
                        reaches.add(to)
            counts.append(len(reaches))
        m["passage_ends_with_a_door"] = float(min(counts))
        # The stair rises in the passage, or in a hall opening off it. The FIRST half is true by
        # construction in this model -- `openings.stair_pass` will only put a stair in a room of
        # type `stair-hall` -- so a test of it would be an instrument that cannot fail, which
        # this corpus rates worse than a test that cannot fail. What is failable is the SECOND
        # half: a stair hall reached from a room rather than from the passage.
        halls = [rid for rid, r in rooms.items()
                 if r.get("type") == "stair-hall" and level_of.get(rid) == 0]
        if halls:
            # SEVERAL STAIR HALLS THAT DISAGREE ARE COULD-NOT-EVALUATE, NOT THE BEST OF THEM
            # (audit, 7 Sep 2026). The first version set `reach = 1.0` on ANY hall reaching a
            # passage -- the flattering reading, ten lines below the comment explaining why the
            # statement above it takes the worst -- so a principal stair off the passage
            # excused a second hall reached only from the dining room, on a HARD rule.
            #
            # AND `min` IS NOT THE FIX EITHER, which is why this is a third state rather than a
            # corrected second one. This model has no way to tell a principal stair from a
            # service stair: both are type `stair-hall`, and a service stair that does NOT open
            # off the passage is correct in a house of this kind. Taking the worst would convict
            # a right building; taking the best acquits a wrong one. Where the ground-floor
            # stair halls disagree the variable is WITHHELD, and `plan_check` reports the rule
            # unjudged naming the variable it could not get -- which is the honest thing the
            # corpus can say with the facts it has.
            reached = [any(pid in {d.get("to") for d in (rooms[h].get("doors") or [])}
                           or h in {d.get("to") for d in (rooms[pid].get("doors") or [])}
                           for pid in passages)
                       for h in halls]
            if all(reached) or not any(reached):
                m["stair_hall_opens_off_the_passage"] = 1.0 if all(reached) else 0.0

    # --- placement-dependent (absent unless the drawn layer passes a placement in)
    if placed and footprint:
        fw, fh = footprint
        for rid, r in rooms.items():
            g = placed.get(rid)
            if not g:
                continue
            if r.get("type") in ("centre-passage", "cross-passage"):
                m.setdefault("passage_width_ft", round(min(g["width_ft"], g["depth_ft"]), 2))
        if fw:
            m["facade_width_ft"] = round(float(fw), 2)

    return _filter(m)


def _filter(m):
    """Drop the names this corpus may not supply, and every None.

    Run at the point measurements are RETURNED rather than at each call site: OQ 52's
    twelve invented constants came back into elevation.py through an `m.update()` after
    exactly this discipline had been applied per-site, and the fix there was to filter at
    the boundary. Same fix, same reason.
    """
    return {k: v for k, v in m.items() if v is not None and k not in NOT_DERIVABLE}


# ---------------------------------------------------------------- entry point
def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[-2].strip())
        return 2
    plan = json.load(open(argv[1]))
    d = declared(plan)
    print(f"declared: {len(d)} measurement(s)")
    for k, v in sorted(d.items()):
        print(f"  {k} = {v}")
    print(f"\nnot derivable by this corpus: {len(NOT_DERIVABLE)} name(s) -- "
          f"each reports COULD NOT EVALUATE, which is not a pass")
    return 0


def selftest():
    """Prove the derivations on constructed houses, in both directions.

    A check that cannot fail is worse than no check, so every assertion here is paired
    with a house built to break it.
    """
    C = _catalog()
    fails = []

    def eq(label, got, want):
        if got != want:
            fails.append(f"{label}: got {got!r}, want {want!r}")

    # A minimal two-room house: porch -> passage -> parlor, kitchen off the passage.
    def house(**over):
        p = {
            "id": "selftest", "name": "selftest", "style": "tidewater-georgian",
            "levels": [{"level": 0, "floor_to_ceiling_ft": 9, "rooms": [
                {"id": "porch", "type": "entry-porch", "width_ft": 6, "length_ft": 12,
                 "doors": [{"to": "exterior", "width_ft": 3.0}, {"to": "passage", "width_ft": 3.0}]},
                {"id": "passage", "type": "centre-passage", "width_ft": 10, "length_ft": 30,
                 "doors": [{"to": "porch", "width_ft": 3.0}, {"to": "parlor", "width_ft": 3.0},
                           {"to": "dining", "width_ft": 3.0}]},
                {"id": "parlor", "type": "parlor", "width_ft": 16, "length_ft": 18,
                 "doors": [{"to": "passage", "width_ft": 3.0}]},
                {"id": "dining", "type": "dining-room", "width_ft": 14, "length_ft": 16,
                 "doors": [{"to": "passage", "width_ft": 3.0}, {"to": "kitchen", "width_ft": 2.8}]},
                {"id": "kitchen", "type": "kitchen", "width_ft": 12, "length_ft": 14,
                 "doors": [{"to": "dining", "width_ft": 2.8}]},
            ]}],
        }
        for k, v in over.items():
            p[k] = v
        return p

    m = declared(house(), C)
    eq("passage_clear_width_ft", m.get("passage_clear_width_ft"), 10.0)
    # The plant-room zero was BUILT and withdrawn: it convicted both reference plans,
    # including the careful one, and the catalogue has no room type that could state the
    # presence of a plant room either. Refused in both directions, and pinned here.
    eq("plant room stays refused", m.get("dedicated_plant_room_area_sqft"), None)
    # kitchen -> dining is direct, so no formal room is crossed
    eq("service route crosses nothing", m.get("service_routes_crossing_a_formal_room"), 0)

    # Now route the kitchen through the parlour and the count must MOVE. A test that
    # cannot fail is the thing WP-8.6 found nine of.
    bad = house()
    rms = {r["id"]: r for r in bad["levels"][0]["rooms"]}
    rms["kitchen"]["doors"] = [{"to": "parlor", "width_ft": 2.8}]
    rms["dining"]["doors"] = [{"to": "passage", "width_ft": 3.0}]
    rms["parlor"]["doors"] = [{"to": "passage", "width_ft": 3.0}, {"to": "kitchen", "width_ft": 2.8}]
    m2 = declared(bad, C)
    if not (m2.get("service_routes_crossing_a_formal_room", 0) >= 1):
        fails.append("service route through the parlour was not counted: "
                     f"{m2.get('service_routes_crossing_a_formal_room')!r}")

    # The filter must actually filter.
    if any(k in declared(house(), C) for k in NOT_DERIVABLE):
        fails.append("a NOT_DERIVABLE name reached the returned measurements")
    if "chimney_breast_projection_or_wall_thickness_in" not in NOT_DERIVABLE:
        fails.append("the chimney plan dimension left NOT_DERIVABLE without being modelled")

    # Every route in the model must cite a record that exists and quote it correctly. This
    # calls check_openings.check_basis rather than copying it -- the corpus has been bitten
    # three times by one rule spelled twice.
    CO = _mod("check_openings", f"{ROOT}/build/check_openings.py")

    class _Rep:
        def __init__(self): self.errs = []
        def err(self, where, msg): self.errs.append(f"{where}: {msg}")

    rep = _Rep()
    for rule in ROUTE_MODEL["routes"]:
        CO.check_basis(rep, rule, source="build/arrangement.py::ROUTE_MODEL")
    fails.extend(rep.errs)

    # EVERY ROOM-TYPE TOKEN THIS MODULE SELECTS ON MUST NAME A REAL ROOM TYPE. The opening
    # grammar's checker states the principle: "a rule keyed on a room type nobody wrote is a
    # rule that never fires, silently." The first draft of this file carried four such
    # tokens -- `chamber`, `secondary-bedroom`, `principal-bedroom`, `hall-and-parlor-hall`
    # -- all of them plausible-looking aliases of types that exist under other names, none
    # of them matching anything. Two of the four sat in the selector for
    # `secondary_bedroom_clear_short_dimension_ft`, which is the measurement
    # `closet-depth-taken-from-the-room` judges every house on.
    import re as _re
    _src = open(os.path.join(ROOT, "build", "arrangement.py")).read()
    _toks = set()
    for grp in _re.findall(r'r\.get\("type"\) in \(([^)]*)\)', _src):
        _toks |= {t.strip().strip("\"'") for t in grp.split(",") if t.strip()}
    for one in _re.findall(r'r\.get\("type"\) == "([a-z\-]+)"', _src):
        _toks.add(one)
    _dead = sorted(t for t in _toks if t and t not in C["rooms"])
    if _dead:
        fails.append(f"selector names {len(_dead)} room type(s) the catalogue does not have, "
                     f"so those branches can never fire: {', '.join(_dead)}")

    if len(ROUTE_MODEL["note"]) < 200:
        fails.append("the route model's honesty note is under the 200-character floor the "
                     "opening grammar's schema sets for the same kind of statement")

    if fails:
        print("arrangement selftest FAILED")
        for f in fails:
            print("  -", f)
        return 1
    print(f"arrangement selftest ok — {len(NOT_DERIVABLE)} name(s) refused with a reason, "
          f"{len(ROUTE_MODEL['routes'])} route(s) cited and verified")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
