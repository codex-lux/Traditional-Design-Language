#!/usr/bin/env python3
"""Plan validator — the critic, and the fitness function a composer will need.

Reads a plan record and reports every violation it can find across five layers:
rooms, groupings, faults, code, and style. Style exceptions are honoured throughout,
so a Georgian five-foot portico is not reported as the four-foot-porch fault.

  python3 build/plan_check.py plans/<id>.json [--json] [--layer room] [--min-severity serious]
"""
from __future__ import annotations
import json, os, glob, re, sys, argparse, importlib.util, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEV_ORDER = ["fatal", "serious", "minor", "advisory", "info"]
STRENGTH_SEV = {"hard": "fatal", "strong": "serious", "preferred": "minor"}
# Constraint severity (hard/soft/advisory, schema/constraint.schema.json) uses a different
# vocabulary than room-adjacency STRENGTH_SEV; mapped to match the STYLE layer's own existing
# choice of "serious" for a forbidden-slot violation, not room-adjacency's "fatal" for hard --
# a single wrong roof pitch is a serious style violation, not grounds to fail the whole plan
# the way a duplicate room id is.
CONSTRAINT_SEV = {"hard": "serious", "soft": "minor", "advisory": "advisory"}

def _load(name, path):
    # Delegates to build/modcache.py so a module is executed once per process
    # rather than once per call. Same signature, same standalone-script
    # behaviour; see that file's header for why (OQ 28). Loaded by path here
    # because this file is itself usually loaded by path, so `build/` is not
    # necessarily on sys.path yet.
    import sys as _sys
    _b = os.path.join(ROOT, "build")
    if _b not in _sys.path:
        _sys.path.insert(0, _b)
    import modcache as _mc
    return _mc.load(name, path)

# SUBSTITUTION, and it runs in one direction (OQ 43, ruled 24 Aug 2026).
#
# This was a list of flat sets and `_alias` treated membership as mutual: if a primary bathroom
# counted as a bathroom then a bathroom counted as a primary bathroom. That is right for some
# pairings and wrong for exactly the ones that matter. A primary bedroom's rule to adjoin a
# PRIMARY bathroom is not satisfied by the hall bath being somewhere in the house; a parlor's
# rule to adjoin an entrance hall IS satisfied by a centre passage.
#
# Each entry names the SPECIFIC room and the general requests it can stand in for. Read it as
# "a walk-in closet will do where a closet was asked for, and a closet will not do where a
# walk-in closet was asked for." Where two rooms genuinely substitute both ways, both directions
# are listed and the comment says why.
#
# Measured across all 129 composable styles before the change: of 542 findings where the plan
# modelled an equivalent of the room a rule wanted, 214 were legitimate substitutions and 294
# were the reverse -- a general room offered where a specific one was asked for, reported as
# though the plan had the room. Making it directional returns those 294 to honest absence and
# promotes the 214 to real adjacency findings, 115 of them fatal across 67 styles. Those 115 are
# genuine: the plan has the room and the rule's subject does not reach it.
SUBSTITUTES = {
    # circulation. A landing IS the stair hall at the head of the stair, and the entrance-hall
    # family is genuinely mutual: whichever of these a plan calls its entry sequence, the front
    # door opens into it and the principal rooms open off it, which is the definition the group
    # holds. gallery-corridor was added by WP-4.5 on the reference corpus's evidence (good-01
    # and good-05 use a Gallery as exactly that room) and centre-passage by OQ 59.
    "landing": {"stair-hall"},
    "stair-hall": {"entrance-hall"},
    "vestibule": {"entrance-hall"},
    "gallery-corridor": {"entrance-hall"},
    "centre-passage": {"entrance-hall"},
    "entrance-hall": {"stair-hall", "vestibule", "gallery-corridor", "centre-passage",
                      "cross-passage"},
    # `hall` in the Anglo-American vernacular sense -- the undivided room the front door opens
    # into, not a corridor. Added when making this table directional showed 24 findings of the
    # shape "Parlor does not reach an entrance hall" on hall-and-parlor and living-hall
    # diagrams, where the parlor is entered from the hall and that is exactly right for the
    # type. The room's own record states it: `entered_from` is cross-passage, entry-porch,
    # exterior, breezeway -- i.e. the outside -- and its own aka list carries "living hall". It
    # substitutes in ONE direction: a hall does the entrance hall's job, and an entrance hall is
    # not a hall, which is a room you eat and sleep in.
    "hall": {"entrance-hall"},
    # the screens passage. Its own record: "a passage running ACROSS the building FROM THE FRONT
    # DOOR to the back door... with the service rooms opening off one side and the hall off the
    # other", entered from the exterior and the entry porch. That is the entrance sequence of a
    # medieval and Tudor plan, and it is what an H-plan manor's porch opens into.
    "cross-passage": {"entrance-hall"},

    # storage. A walk-in closet or a linen press will do where a closet was asked for; a plain
    # closet will not do where a rule specifically wants a walk-in.
    "walk-in-closet": {"closet"},
    "linen-press": {"closet"},

    # sanitary. The asymmetry this ruling exists for: a primary bathroom satisfies a request for
    # a bathroom, and a hall bath does not satisfy a primary bedroom's request for a primary
    # bathroom -- which is the difference between a suite and a house with a bathroom in it.
    "primary-bathroom": {"bathroom"},

    # dining. A breakfast room or an eat-in area will serve where a rule wants somewhere to eat;
    # neither is a dining room where one is specifically required.
    "breakfast-room": {"dining-room"},
    "eat-in-kitchen-area": {"dining-room"},

    # the parlor family. All of these are the principal sitting room under different names and
    # different centuries, and a rule that names one will take another -- with the exception of
    # best-parlor and drawing-room, which are the FORMAL room in a house that also has an
    # everyday one, so they satisfy a request for a parlor and a request for one of them is not
    # satisfied by the family room.
    "parlor": {"living-room", "sitting-room"},
    "living-room": {"parlor", "sitting-room"},
    "sitting-room": {"parlor", "living-room"},
    "family-room": {"living-room", "parlor", "sitting-room"},
    "great-room": {"living-room", "parlor", "sitting-room"},
    "best-parlor": {"parlor", "living-room", "sitting-room"},
    "drawing-room": {"parlor", "living-room", "sitting-room"},

    # service.
    "scullery": {"kitchen"},
    "butlers-pantry": {"pantry"},
    "larder": {"pantry"},

    # sleeping. A bedchamber is a bedroom in an older word and substitutes freely; a primary
    # bedroom satisfies a request for a bedroom and the reverse is the same error as the
    # bathroom case above.
    "bedchamber": {"bedroom"},
    "bedroom": {"bedchamber"},
    "primary-bedroom": {"bedroom", "bedchamber"},
    # A garret chamber is a bedroom inside the roof -- its own record: "a sleeping room inside
    # the roof, with sloping ceilings on two sides and a knee wall" -- and it is what a Cape
    # sleeps in. Without this, a Cape's closets fail `closet must_adjoin bedroom` while doored
    # to exactly the room they serve. A bedroom is not a garret chamber, which is why it runs
    # one way. `nursery` and `sleeping-porch` are also function_class `sleeping` and are NOT
    # here: a nursery is a room for a child too young to have a bedroom and a sleeping porch is
    # seasonal, so neither answers a rule that wants the household's bedroom.
    "garret-chamber": {"bedroom", "bedchamber"},
}


def satisfies(have, want):
    """Can a room of type `have` stand in where a rule asked for `want`? (OQ 43)"""
    return have == want or want in SUBSTITUTES.get(have, ())


def satisfied_by(want):
    """Every room type that would SATISFY a rule asking for `want`.

    Ask this when the question is "the rule wants a `want`; would anything the plan HAS do?"
    """
    return {want} | {have for have, wants in SUBSTITUTES.items() if want in wants}


def serves(have):
    """Every request a room of type `have` can answer -- itself, and what it substitutes for.

    Ask this when the question is "this room is next to me; which rules does its presence
    satisfy?" It is the other direction from `satisfied_by`, and before OQ 43 the two were one
    function, which is precisely the bug."""
    return {have} | set(SUBSTITUTES.get(have, ()))


def _alias(t):
    """Kept as the name the rest of this file and the tests already use, and it means
    `satisfied_by`. The other direction is `serves`."""
    return satisfied_by(t)

def load_corpus():
    C = {"rooms": {}, "groupings": {}, "styles": {}, "faults": {}, "massings": {}, "slots": {}, "kits": {}}
    for f in sorted(glob.glob(f"{ROOT}/rooms/*.json")): r = json.load(open(f)); C["rooms"][r["id"]] = r
    for f in sorted(glob.glob(f"{ROOT}/groupings/*.json")): g = json.load(open(f)); C["groupings"][g["id"]] = g
    for f in sorted(glob.glob(f"{ROOT}/styles/*.json")): s = json.load(open(f)); C["styles"][s["id"]] = s
    for f in sorted(glob.glob(f"{ROOT}/faults/*.json")): x = json.load(open(f)); C["faults"][x["id"]] = x
    for f in sorted(glob.glob(f"{ROOT}/kits/*.kit.json")): k = json.load(open(f)); C["kits"][k["style"]] = k
    C["massings"] = {m["id"]: m for m in json.load(open(f"{ROOT}/massings/catalog.json"))}
    for g in json.load(open(f"{ROOT}/elements/slots.json"))["groups"]:
        for s in g["slots"]: C["slots"][s["id"]] = s
    return C

_RESOLVED_SLOTS = {}


def _resolved_slots(style):
    """The CASCADE-RESOLVED slot record, not the node's own kit file.

    THE STYLE LAYER WAS BLIND TO 879 FORBIDDEN BINDINGS AND 3,661 FORBIDDEN VARIANTS. It read
    `C["kits"][style]["slots"]` -- the node's OWN file -- while every forbidden call the
    lineage delivers lives in the resolved record, and `resolve_slots` stops its walk only on
    `specified` or `forbidden`, so a slot the node leaves `open` takes its ancestor's
    prohibition in full. Measured across all 132 buildable nodes: every one of them had at
    least one prohibition the critic could not see. `cape-cod-colonial` forbids the whole
    classical-apparatus group at the family and a plan declaring a pilaster on it went
    unremarked here while `build/elevation.py` refused to draw one -- two layers disagreeing
    about the same record, which is the shape WP-6.2 was written to end.

    Measured before changing it, per the WP-8.4 ruling that a new conviction is a suspect
    until read: sweeping the Tidewater reference plan's declared block over all 132 nodes
    gives 110 styles unchanged, 19 gaining one finding and 3 gaining two, and every one of
    those is a true call -- a Tidewater Georgian's side-gable roof and brick cladding really
    are forbidden on a Craftsman Bungalow. BOTH SHIPPED PLANS GAIN NOTHING, which is exactly
    why this was not found by running them: verifying a corpus-wide change on the plans that
    happen to ship is verifying it on 2 of 164 styles.

    NOT WRAPPED IN `except Exception`, and the first version of this function was. A bare
    catch here degraded silently to the raw kit -- which is the very behaviour being fixed --
    and it swallowed a NameError in this function's own first line (`_mod` for `_load`) so
    that the fix appeared to work and changed nothing. A cascade this corpus cannot resolve
    is a defect, and it is loud. The caller reaches this only inside `if st:`, so the style
    is known to exist.

    Cached per style because `plan_check` runs inside the composer's scoring loop.
    """
    if style in _RESOLVED_SLOTS:
        return _RESOLVED_SLOTS[style]
    rk = _load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
    g = rk.load_graph()
    slots, _ = rk.resolve_slots(g, rk.chain_for(g, style), rk.scope_for(g, style))
    _RESOLVED_SLOTS[style] = slots
    return slots


# ---------------------------------------------------------------- helpers
def style_chain(style_id, C):
    """Every id that 'this style' legitimately answers to: itself, its containers, its kit ancestors."""
    out, cur = set(), C["styles"].get(style_id)
    for _ in range(8):
        if not cur: break
        out.add(cur["id"])
        for e in cur.get("lineage", []):
            if e.get("inherits_kit"): out.add(e["target"])
        cur = C["styles"].get(cur.get("member_of") or "")
    return out

def excepted(rule, chain):
    return bool(set(rule.get("exceptions") or []) & chain)


def kit_suppressions(chain, C):
    """Universal room rules the style's kit declares it switches OFF (OQ 15).

    `room_adjacency_overrides`'s own note has said since ontology 0.4.0 that the slot holds
    "only what a style ADDS or SUPPRESSES" -- and nothing read it, so a suppression existed as
    prose while the validator went on enforcing the rule the kit said should not apply. A rule
    a style legitimately breaks is not reported: that is this file's own closing sentence, and
    until now it was true only of the `exceptions` list on the room record, which is the room
    catalogue's side of the same statement. This is the kit's side.

    Read across the whole inheritance chain, because a suppression is a fact about a tradition
    and a descendant that did not restate it has not thereby reinstated the rule.

    Returns a set of (room, key, target) triples."""
    out = set()
    for sid in chain:
        slot = ((C.get("kits", {}).get(sid) or {}).get("slots") or {}).get("room_adjacency_overrides")
        for r in ((slot or {}).get("rules") or []):
            sup = r.get("suppresses")
            if r.get("effect") == "suppresses" and sup:
                out.add((sup.get("room"), sup.get("key"), sup.get("target")))
    return out

def derive_constraint_vars(plan):
    """Narrow, conservative auto-derivation of a handful of constraint-vocabulary variables
    (build/constraint_vocabulary.py) directly from unambiguous plan structure.

    Deliberately small. Everything else a constraint's test.expression might reference has
    to come from an explicit plan.measurements entry, or the constraint stays unjudged --
    'unjudged is not passed' applies to constraints exactly as it already does to slots and
    faults elsewhere in this validator. Adding a derivation here is a real claim that the
    value is unambiguous from plan structure alone; when it isn't, leave it out."""
    v = {}
    levels = plan.get("levels") or []
    if levels:
        v["storey_count"] = len(levels)
        ground_idx = min(lv.get("index", 0) for lv in levels)
        ground_lv = next(lv for lv in levels if lv.get("index", 0) == ground_idx)
        ground_rooms = ground_lv.get("rooms", [])
        v["room_count_ground_floor"] = len(ground_rooms)
        gc = ground_lv.get("floor_to_ceiling_ft") or next(
            (r.get("ceiling_ft") for r in ground_rooms if r.get("ceiling_ft")), None)
        if gc:
            v["ceiling_height_ground_in"] = gc * 12
        cp = next((r for r in ground_rooms if r.get("type") == "centre-passage"), None)
        if cp and cp.get("width_ft") and cp.get("length_ft"):
            v["centre_passage_width_ft"] = min(cp["width_ft"], cp["length_ft"])
    ctx = plan.get("context") or {}
    if ctx.get("lot_width_ft") is not None: v["lot_width_ft"] = ctx["lot_width_ft"]
    if ctx.get("lot_depth_ft") is not None: v["lot_depth_ft"] = ctx["lot_depth_ft"]
    # WP-2.4: `site` is unambiguous plan structure exactly the way `context` already is --
    # every field on it is a fact about the lot the plan record itself asserts, not something
    # inferred from geometry -- so every key present passes straight through by name. A plan
    # that omits `site` entirely (nothing required it) simply leaves these unjudged, same as
    # any other constraint variable no measurement supplies.
    site = plan.get("site") or {}
    for k, val in site.items():
        if k == "note" or val is None: continue
        v[k] = val
    return v

class Findings:
    """The finding collector. Every finding is minted with a stable `id` (OQ 32).

    WHY THE ID IS NOT A HASH OF THE SENTENCE. The workbench needed to diff findings across a
    re-evaluation -- which rows opened, which cleared -- and to make one citable, and with no id
    to hand it derived one client-side from `hash(layer|statement|room)`. That works exactly
    until somebody improves the wording of a finding, at which point every open row, every
    citation and every diff silently points at nothing, and the UI reports a finding cleared and
    a new one opened when the only thing that changed was an adjective. A finding's identity is
    WHAT IT IS ABOUT, not how it is currently phrased.

    So the id is built from the durable parts: the layer, the room it is about, and the rule or
    fault id where the finding has one. Where a layer produces several findings about one room
    with no rule id to separate them, an ordinal disambiguates within that group -- stable for a
    given plan and a given checker, which is what a diff between two evaluations of the same
    record needs. It is deliberately NOT a global unique id: two different plans may produce the
    same finding id for the same defect in the same room, and that is a feature, not a collision.
    """

    def __init__(self):
        self.items = []
        self._seq = collections.Counter()

    # `rule` carries an id on some layers and a whole paragraph of prose on others (an
    # adjacency rule's `rule` is its reasoning). Only an id-shaped value may enter the key --
    # otherwise the id would embed the very prose it exists to be independent of, which is the
    # bug with extra steps.
    _ID_LIKE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,39}$")

    def add(self, severity, layer, statement, **kw):
        parts = [layer, str(kw.get("room") or "")]
        for key in ("rule", "constraint", "fault"):
            v = kw.get(key)
            if isinstance(v, str) and self._ID_LIKE.match(v):
                parts.append(v)
                break
        base = ":".join(p for p in parts if p)
        n = self._seq[base]
        self._seq[base] += 1
        fid = base if not n else f"{base}#{n}"
        self.items.append({"id": fid, "severity": severity, "layer": layer,
                           "statement": statement, **kw})
    def sorted(self):
        return sorted(self.items, key=lambda f: (SEV_ORDER.index(f["severity"]) if f["severity"] in SEV_ORDER else 9,
                                                 f["layer"], f.get("room") or ""))

# ---------------------------------------------------------------- the checker
# ---------------------------------------------------------------- the drawn house
HABITABLE = {"public", "living", "dining", "sleeping", "work", "circulation",
             "threshold", "sanitary", "service"}


def drawn_layer(plan, rooms, level_of, C, F):
    """Judge the house that was PLACED, not the one that was declared.

    Three states, like every other checker here: a plan with no placement returns
    `{"evaluated": False, ...}` and one `info` finding saying so. It is never a pass. The
    checks are the ones the reported defects needed and nothing had:

      · REACHABILITY. Nothing in this system has ever checked that you can walk from the
        front door to every room. A room with no doors at all produced no finding, and a
        room whose declared doors the placement could not realise produced none either --
        which is how a chamber bath with no way in shipped on a reference sheet.
      · The drawn size against the declared one, in both directions.
      · The landing over its own stair, which `stacks_over` has never been read for.
      · Passage clear width against groupings/centre-passage-core.json's own band.
      · Wet-room fixtures that will not fit together on real walls.
    """
    placed = {rid: r["geometry"] for rid, r in rooms.items() if r.get("geometry")}
    if not placed:
        F.add("info", "drawn",
              "The drawn layer could not evaluate: this record carries no placement. "
              "Run build/geometry.py to place it, then re-check.",
              fix="python3 build/geometry.py <plan>")
        return {"evaluated": False, "reason": "no placement on this record",
                "rooms_placed": 0}

    out = {"evaluated": True, "rooms_placed": len(placed), "unreachable": [],
           "diverged": [], "unplaced_openings": 0}

    # --- reachability over the openings that were actually PLACED
    ok_edges = {rid: set() for rid in rooms}
    outside = set()
    unplaced_pairs = set()
    for rid, r in rooms.items():
        for d in (r.get("doors") or []):
            if d.get("unplaced"):
                # counted per PAIR: a door is one door, and it is written on both of its
                # rooms, so counting records would report every one of them twice
                unplaced_pairs.add(tuple(sorted((rid, d["to"]))))
                continue
            t = d["to"]
            if t == "exterior":
                outside.add(rid)
                continue
            if t in ok_edges:
                ok_edges[rid].add(t)
                ok_edges[t].add(rid)
    out["unplaced_openings"] = len(unplaced_pairs)
    # a stair connects its two levels: a landing over a stair is a way up, and without it
    # every upper room reads as unreachable on a house whose only link between floors is
    # the stair everybody uses
    st = plan.get("stair")
    if st and st.get("room") in ok_edges:
        for rid, r in rooms.items():
            if r.get("stacks_over") == st["room"]:
                ok_edges[rid].add(st["room"])
                ok_edges[st["room"]].add(rid)
    for a in plan.get("adjacencies", []):
        if a.get("relation") in ("above", "below") and a["a"] in ok_edges and a["b"] in ok_edges:
            ok_edges[a["a"]].add(a["b"])
            ok_edges[a["b"]].add(a["a"])

    seen = set(outside)
    stack = list(outside)
    while stack:
        cur = stack.pop()
        for nxt in ok_edges.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    if outside:
        for rid, r in rooms.items():
            if rid in seen or rid not in placed:
                continue
            fc = (C["rooms"].get(r["type"], {}) or {}).get("function_class")
            if fc not in HABITABLE:
                continue
            name = r.get("name") or rid
            declared = len([d for d in (r.get("doors") or [])])
            out["unreachable"].append(rid)
            F.add("fatal", "drawn",
                  f"{name} cannot be reached from outside the house on the drawing. "
                  + (f"The record declares {declared} door(s) to it and the placement "
                     f"realised none of them."
                     if declared else "The record declares no door to it at all."),
                  room=rid,
                  fix=("Place the plan again, or move the rooms so the declared doors have "
                       "a wall to sit in — build/openings.py names each one it could not "
                       "place and why."))
    else:
        F.add("info", "drawn",
              "Reachability could not be evaluated: no exterior door on this plan is placed, "
              "so there is no outside to walk in from.")

    # A room the drawing joins to NOTHING INSIDE the house. It passes reachability whenever
    # it has an exterior door of its own, and it is still wrong: this is the reported
    # symptom in its exact form — "the door to the kitchen is only from the outside, and the
    # kitchen is connected to no other rooms through doors or casement openings". The
    # declared graph is fine, which is why every existing layer is silent about it.
    out["cut_off"] = []
    for rid, r in rooms.items():
        if rid not in placed:
            continue
        interior_declared = [d for d in (r.get("doors") or []) if d["to"] != "exterior"]
        if not interior_declared or ok_edges.get(rid):
            continue
        fc = (C["rooms"].get(r["type"], {}) or {}).get("function_class")
        if fc == "outdoor":
            continue
        # a room already reported UNREACHABLE is not also reported cut off: that is one
        # defect, and saying it twice would inflate the count of a plan's troubles with a
        # restatement rather than a second fact
        if rid not in seen:
            continue
        name = r.get("name") or rid
        out["cut_off"].append(rid)
        F.add("serious", "drawn",
              f"{name} joins no other room on the drawing — the only way in is from outside. "
              f"The record declares {len(interior_declared)} interior door(s) and the "
              f"placement realised none of them.",
              room=rid,
              fix=("Place the plan again, or move these rooms so their declared doors have a "
                   "wall to sit in — build/openings.py names each door it could not place "
                   "and why."))

    # --- drawn against declared
    for rid, r in rooms.items():
        g = placed.get(rid)
        dw, dl = r.get("width_ft"), r.get("length_ft")
        if not g or not dw or not dl:
            continue
        da, pa = dw * dl, g["width_ft"] * g["depth_ft"]
        if da <= 0:
            continue
        pct = (pa - da) / da * 100.0
        # a tenth OR MORE. The boundary is real rather than hypothetical: on the shipped
        # Tidewater placement the kitchen and the library both land at exactly -10.00%.
        if abs(pct) < 10 - 1e-9:
            continue
        name = r.get("name") or rid
        out["diverged"].append({"room": rid, "pct": round(pct, 1)})
        sev = "serious" if abs(pct) >= 25 else "minor"
        F.add(sev, "drawn",
              f"{name} is drawn at {round(pa)} sf against the {round(da)} sf the record "
              f"declares ({pct:+.0f}%).",
              room=rid,
              fix=("Accept the drawn size into the record, or constrain the placement — "
                   "the sheet prints the drawn figure, so the record and the drawing "
                   "disagree until one of them moves."))

    # --- EVERY stacks_over claim, against the room it names. `stacks_over` is in the
    # schema, the partis declare it (14 of the 21, 50 claims, so every plan composed from
    # one carries them), and the plan records declare it.
    #
    # BOTH ENGINES CHARGE IT SINCE WP-7.4, AND THIS LAYER STILL REPORTS IT. A charge is a
    # preference the search trades off; this is the arbiter, and the two are not the same
    # job. The test below is `geometry.vertical_score`'s and `geometry_cp`'s -- strict
    # positive rectangle intersection -- deliberately, so the search and the critic cannot
    # convict and acquit the same house. Change it here and change it there in the same
    # commit.
    #
    # THREE PUBLISHED REFUSALS DIED ON THE WAY HERE AND THE ORDER MATTERS. WP-6.3 built a
    # charge, measured byte-identical output at 100x and 10,000x, and concluded "the search
    # can only re-rank candidates produced blind"; that charge keyed on landing-over-stair,
    # a pair neither shipped plan declares. WP-7.1 made the generator level-aware, moved
    # transfer beams 166 -> 109 corpus-wide and left broken stacks flat at 26/47 -> 27/47,
    # and wrote that no generator change fixes stacking -- true, and not an argument against
    # a score term. WP-7.4 found the actual cause: the charge was being measured against a
    # 250-candidate pool too thin to contain the alternative, and over 2,000 candidates the
    # better-stacking placements are there and keep the porch on the entrance front. The CP
    # side needed no hard pin at all, so OQ 95's "a stacking constraint outranks every
    # authored exterior wall" -- true of a pin, which creates an assumption literal and
    # enters conflict cores -- never applied to the penalty that was actually built.
    #
    # Re-measure before quoting any figure here; an earlier draft of this comment said
    # "two", measured on a placement two packages out of date.
    out["stacks_broken"] = []
    for rid, r in rooms.items():
        so = r.get("stacks_over")
        if not so:
            continue
        g = placed.get(rid)
        below = placed.get(so)
        name = r.get("name") or rid
        if not g:
            continue
        if not below:
            F.add("info", "drawn",
                  f"{name} declares it stacks over '{so}', which this placement does not "
                  f"place — the claim could not be evaluated.", room=rid)
            continue
        if level_of.get(rid) == level_of.get(so):
            continue                      # a same-level claim is not a stack
        ox = min(g["x_ft"] + g["width_ft"], below["x_ft"] + below["width_ft"]) \
            - max(g["x_ft"], below["x_ft"])
        oy = min(g["y_ft"] + g["depth_ft"], below["y_ft"] + below["depth_ft"]) \
            - max(g["y_ft"], below["y_ft"])
        if ox <= 0 or oy <= 0:
            out["stacks_broken"].append(rid)
            F.add("serious", "drawn",
                  f"{name} declares it stacks over '{so}' and is drawn clear of it "
                  f"entirely — a stack with nothing under it.",
                  room=rid,
                  fix="Place the two together, or drop the stacks_over claim.")
        elif st and so == st.get("room") and st.get("well"):
            # the landing's own rule is about the WELL, not the room that holds it: a
            # landing may sit squarely inside the stair hall and still miss the opening the
            # flight arrives at. Measured against the room, this check passed on a landing
            # that overlapped the well by nothing at all.
            w = st["well"]
            wx = min(g["x_ft"] + g["width_ft"], w["x_ft"] + w["width_ft"]) \
                - max(g["x_ft"], w["x_ft"])
            wy = min(g["y_ft"] + g["depth_ft"], w["y_ft"] + w["depth_ft"]) \
                - max(g["y_ft"], w["y_ft"])
            got = max(0.0, wx) * max(0.0, wy)
            if got < (st.get("width_ft") or 3.0) ** 2:
                F.add("minor", "drawn",
                      f"{name} overlaps the stair well by only {got:.0f} sf; a landing not "
                      f"less than the stair's own width is "
                      f"groupings/stair-and-landing-core.json's hard rule.",
                      room=rid)
    if st and st.get("unplaced"):
        F.add("serious", "drawn",
              f"The stair is not drawn: {st['unplaced']['reason']}",
              room=st.get("room"),
              fix="Give the stair hall the run its own storey height needs.")

    # --- the passage, against its own grouping's band
    band = None
    cp = (C["groupings"].get("centre-passage-core") or {})
    for rule in (cp.get("rules") or []):
        t = rule.get("test") or ""
        if "passage_width_ft" in t and "between" in t:
            band = rule
            break
    for rid, r in rooms.items():
        if r["type"] not in ("centre-passage", "cross-passage"):
            continue
        g = placed.get(rid)
        if not g:
            continue
        wft = min(g["width_ft"], g["depth_ft"])
        name = r.get("name") or rid
        if wft < 6.0:
            F.add("serious", "drawn",
                  f"{name} is drawn {wft:.1f} ft wide. rooms/centre-passage.json: "
                  f"\"SIX TO SEVEN FEET is a passage that circulates\" — below that it does "
                  f"not.", room=rid)
        elif 8.0 <= wft <= 9.0:
            F.add("minor", "drawn",
                  f"{name} is drawn {wft:.1f} ft wide, in the dead zone its own record names: "
                  f"\"too wide to be economical and too narrow to furnish\".", room=rid)

    # --- fixtures that will not fit together
    for rid, r in rooms.items():
        for f in (r.get("fixture_layout") or []):
            if not f.get("unplaced"):
                continue
            name = r.get("name") or rid
            F.add("serious", "drawn",
                  f"{name}: {f['item']} is not placed — {f['unplaced']['reason']}",
                  room=rid,
                  fix="Widen the room, or drop the fixture from the record.")

    # --- a run of wall the room's own words demand, unbroken by the openings just placed
    #
    # WP-7.2, and the scope is deliberately exactly what the corpus states. `rooms/*.json`
    # carries 278 furniture items and ONE of them names a wall run in words:
    # `dining-room`'s sideboard, *"Needs an uninterrupted wall of at least 6 ft. This is what
    # the second window usually kills."* That sentence is the basis and the number sits beside
    # it in the same record, so the two cannot drift. Every item carrying
    # `needs_uninterrupted_wall_ft` is measured here; no rule is invented for a room that
    # states none, which is where Lucas drew the line between the corpus and the architect.
    #
    # This is an ARRANGEMENT rule and never a sizing one. Room size comes from the program and
    # the catalogue band, never from the furniture — ruled 27 Aug 2026, OQ 92. A room that
    # fails this has a window in the wrong place, not a size problem.
    for rid, r in rooms.items():
        g = placed.get(rid)
        rt = C["rooms"].get(r["type"]) or {}
        if not g:
            continue
        wants = [it for it in (rt.get("furniture") or []) if it.get("needs_uninterrupted_wall_ft")]
        if not wants:
            continue
        # what each wall has left once this room's placed openings have taken their runs
        spans = {w: [] for w in ("N", "S", "E", "W")}
        for o in list(r.get("doors") or []) + list(r.get("windows") or []):
            if o.get("unplaced") or not o.get("wall"):
                continue
            wd = o.get("width_ft") or 3.0
            for pos in (o.get("positions_ft") or ([o["position_ft"]] if o.get("position_ft") is not None else [])):
                spans[o["wall"]].append((pos - wd / 2.0, pos + wd / 2.0))
        best = 0.0
        for w, taken in spans.items():
            along_x = w in ("N", "S")
            lo = g["x_ft"] if along_x else g["y_ft"]
            hi = lo + (g["width_ft"] if along_x else g["depth_ft"])
            free = [(lo, hi)]
            for a, b in sorted(taken):
                nxt = []
                for s0, e0 in free:
                    if b <= s0 or a >= e0:
                        nxt.append((s0, e0)); continue
                    if a > s0: nxt.append((s0, min(a, e0)))
                    if b < e0: nxt.append((max(b, s0), e0))
                free = nxt
            best = max([best] + [e0 - s0 for s0, e0 in free])
        name = r.get("name") or rid
        for it in wants:
            need = float(it["needs_uninterrupted_wall_ft"])
            if best + 1e-6 < need:
                F.add("minor", "drawn",
                      f"{name} has no unbroken run of wall for its {it['item']}: the longest "
                      f"its walls have left once the doors and windows are placed is "
                      f"{best:.1f} ft, and rooms/{r['type']}.json asks for {need:g} ft — "
                      f"\"{(it.get('note') or '').split('.')[0]}.\"",
                      room=rid,
                      fix="Move a window off that wall, or accept the piece elsewhere.")

    out["unreachable_count"] = len(out["unreachable"])
    out["diverged_count"] = len(out["diverged"])
    return out


def check(plan, C=None, strict=False):
    C = C or load_corpus()
    core = _load("tdlcore", f"{ROOT}/mcp_server/core.py")
    F = Findings()
    seen_pairs = set()
    style = plan.get("style")
    chain = style_chain(style, C)
    suppressed = kit_suppressions(chain, C)
    if style not in C["styles"]:
        F.add("fatal", "style", f"Unknown style '{style}'.", fix="Use a style id from the taxonomy.")

    # ---- index rooms and build the adjacency graph
    rooms, level_of = {}, {}
    for lv in plan["levels"]:
        for r in lv.get("rooms", []):
            if r["id"] in rooms:
                F.add("fatal", "plan", f"Duplicate room id '{r['id']}'.", room=r["id"])
            rooms[r["id"]] = r; level_of[r["id"]] = lv.get("index", 0)
    adj = {rid: set() for rid in rooms}
    rel = {}
    for rid, r in rooms.items():
        for d in r.get("doors", []):
            t = d["to"]
            if t == "exterior": continue
            if t not in rooms:
                F.add("serious", "plan", f"Door from '{rid}' to unknown room '{t}'.", room=rid)
                continue
            adj[rid].add(t); adj[t].add(rid)
            rel[(rid, t)] = rel[(t, rid)] = "direct-door"
    # ONE DOOR, TWO RECORDS, AND THEY MUST AGREE (WP-6.4). A door is declared on both
    # rooms it joins, so its width, type and rank exist twice; `compose.symmetrise_doors`
    # mirrors them and `compose.derive_openings` decides once per PAIR and writes both
    # sides. Nothing checked it. A hand-authored or hand-edited record whose two halves
    # disagree gives each renderer a different door to draw and the exporters a third,
    # and `compose.py` carried a comment saying "a door disagreeing with itself across its
    # two rooms is a corruption the drawn layer now reports" -- it reported nothing of the
    # kind. This is a DECLARED-layer check on purpose: it compares two records against each
    # other and never reads a placement, so it stays legal under OQ 54's ruling.
    _seen_pair = {}
    for rid, r in sorted(rooms.items()):
        for d in r.get("doors", []):
            t = d["to"]
            if t == "exterior" or t not in rooms:
                continue
            key = tuple(sorted((rid, t)))
            first = _seen_pair.get(key)
            if first is None:
                _seen_pair[key] = (rid, d)
                continue
            frid, fd = first
            for field, label in (("width_ft", "width"), ("type", "type"), ("rank", "rank")):
                a, b = fd.get(field), d.get(field)
                if a is None or b is None or a == b:
                    continue      # absent on one side is a gap, not a contradiction
                F.add("minor", "plan",
                      f"The door between {rooms[frid].get('name') or frid} and "
                      f"{r.get('name') or rid} disagrees with itself about its {label}: "
                      f"{frid} says {a}, {rid} says {b}.",
                      room=rid,
                      fix=("Give both records the same value — one door is one opening, and "
                           "each renderer picks whichever record it reaches first."))
    # Declared relations are kept beside the door-derived ones, not merged under
    # them: a pair can legitimately be joined by a door AND declared
    # not-visible-from (the door sits around a jog). The must-not-adjoin skip
    # below consults both; entered_from keeps reading the door-derived map only.
    # Before this, rel.setdefault meant a direct-door pair could NEVER satisfy
    # "record the relation as 'not-visible-from' if the separation is real" --
    # the exact interaction the finding's own fix text promises.
    declared_rel = {}
    for a in plan.get("adjacencies", []):
        if a["a"] in rooms and a["b"] in rooms:
            adj[a["a"]].add(a["b"]); adj[a["b"]].add(a["a"])
            rel.setdefault((a["a"], a["b"]), a["relation"]); rel.setdefault((a["b"], a["a"]), a["relation"])
            declared_rel[(a["a"], a["b"])] = declared_rel[(a["b"], a["a"])] = a["relation"]
    types_present = {r["type"] for r in rooms.values()}
    # OQ 42, ruled 24 Aug 2026. Every adjacency target already runs through `_alias()` when the
    # question is what a room is NEXT TO; the question of whether the plan CONTAINS the room at
    # all was asked against raw types, so a plan with a centre passage was told it models no
    # entrance hall and a plan with a living room that it models no parlor. 774 of 3,219
    # completeness findings across the catalogue were false in exactly that way.
    #
    # `types_modelled` is the aliased set and is used ONLY to decide whether the claim "and the
    # plan models none" is true. It deliberately does NOT re-route these findings into the
    # adjacency branch at the rule's own severity, which is the obvious-looking fix and is
    # worse: measured, it turns 170 of the 774 FATAL across 87 styles. The cause is that
    # EQUIVALENT is asymmetric in practice -- a primary bathroom satisfies a request for a
    # bathroom, and a hall bathroom does not satisfy a primary bedroom's request for a primary
    # bathroom -- and until each pairing states which direction it satisfies, promoting these is
    # trading 774 false minors for 170 false fatals. So the severity is unchanged and only the
    # sentence is corrected. The directional question stays open as OQ 43.
    def types_modelled(rid):
        """The aliased types the plan models, NOT counting the room doing the asking.

        A room cannot satisfy its own adjacency rule. Without this the kitchen's rule to adjoin
        a scullery was answered by the kitchen being a kitchen, which is true of the alias group
        and nonsense as a statement about the plan."""
        out = set()
        for x, rr in rooms.items():
            if x == rid: continue
            out |= serves(rr["type"])
        return out
    def types_adjacent(rid):
        out = set()
        for x in adj[rid]: out |= serves(rooms[x]["type"])
        return out

    def circulation(x):
        """Does this room carry the plan's movement?

        Normally that is its function_class. But a whole family of house types -- the courtyard
        corredor, the Creole gallery, the Charleston piazza -- run their entire circulation
        through a room the catalogue types as `outdoor`, because it is roofed and open rather
        than enclosed. In those plans the gallery IS the corridor: every room opens onto it and
        onto nothing else. Judged on function_class alone the validator cannot see that, and
        reports every bedroom in a courtyard house as failing to reach a bathroom -- which is
        the corridor, the correct answer, being read as a fault. The test is what the plan does
        with the room rather than what the room is: an outdoor room with doors to three or more
        rooms is being used as circulation. Two doors is a porch you pass through; three is a
        gallery. (WP-4.5)"""
        t = C["rooms"].get(rooms[x]["type"])
        if not t: return False
        if t["function_class"] in ("circulation", "threshold"): return True
        if t["function_class"] == "outdoor":
            return len([d for d in adj[x] if d in rooms]) >= 3
        return False

    def types_on_level(delta_from):
        """Room types on a given level. The vertical half of adjacency (OQ 57)."""
        out = {}
        for x, rr in rooms.items():
            out.setdefault(level_of.get(x, 0), set()).update(serves(rr["type"]))
        return out

    _by_level = None

    def types_vertically_from(rid, direction):
        """Types on the storey directly above or below this room.

        OQ 57, ruled 24 Aug 2026. Adjacency was evaluated within a level only, which made two
        real arrangements unstateable: an overlook is open to the hall BELOW it, and a great
        chamber over the parlour is a drawing room whose dining room is a storey down. Both were
        being worked around -- one rule softened so a right answer was not called a defect, one
        room retyped to dodge a rule it could never satisfy -- and both workarounds now come out.

        Deliberately checks the LEVEL rather than plan-position overlap: a plan record carries
        geometry only after the geometry pass has run, and this layer is hand-authorable and runs
        first. Being on the storey below is the claim the corpus can actually make."""
        nonlocal _by_level
        if _by_level is None:
            _by_level = types_on_level(0)
        lv = level_of.get(rid, 0)
        want = lv - 1 if direction == "below" else lv + 1
        return _by_level.get(want, set())

    def types_near(rid):
        """Directly adjacent, plus anything one hop further through a hall.

        Rooms in a real house connect THROUGH circulation — a bedroom reaches its bathroom
        across a landing, not through a shared door. Requiring a shared wall for every
        should_adjoin turns the corridor, which is the correct answer, into a fault."""
        out = set(types_adjacent(rid))
        for mid in adj[rid]:
            if circulation(mid):
                for x in adj[mid]:
                    if x != rid: out |= serves(rooms[x]["type"])
        return out

    # ============================================================ ROOM LAYER
    for rid, r in rooms.items():
        rt = C["rooms"].get(r["type"])
        if not rt:
            F.add("fatal", "room", f"Unknown room type '{r['type']}'.", room=rid,
                  fix="Use an id from the room catalogue, or add the room type.")
            continue
        label = r.get("name") or rt["name"]
        w, l = r.get("width_ft"), r.get("length_ft")
        area = (w * l) if (w and l) else None
        if w and l and w > l: w, l = l, w                     # width is the SHORT dimension

        # dimension bands
        if area:
            lo, hi = rt["dimensions"]["area_sf"]
            if area < lo * 0.9:
                F.add("serious", "room", f"{label} is {area:.0f} sf; the catalogue band for a {rt['name'].lower()} is {lo}-{hi} sf.",
                      room=rid, rule=rt["dimensions"].get("critical_dimension"))
            elif area > hi * 1.25:
                F.add("minor", "room", f"{label} is {area:.0f} sf, well above the {lo}-{hi} sf band. Confirm it is not a room that has stopped being a room.",
                      room=rid)
        if w and rt["dimensions"].get("width_ft"):
            lo, hi = rt["dimensions"]["width_ft"]
            if w < lo:
                F.add("serious", "room", f"{label} is {w} ft in its short dimension; below the {lo} ft floor for a {rt['name'].lower()}.",
                      room=rid, rule=rt["dimensions"].get("critical_dimension"))
        cmin = rt["dimensions"].get("ceiling_min_ft")
        ch = r.get("ceiling_ft") or next((lv.get("floor_to_ceiling_ft") for lv in plan["levels"]
                                          if any(x["id"] == rid for x in lv.get("rooms", []))), None)
        if cmin and ch and ch < cmin:
            F.add("serious", "room", f"{label} ceiling {ch} ft is under the {cmin} ft the room type wants.", room=rid)

        # ---- furniture fit: the check most plans have never had run on them
        for it in rt.get("furniture", []):
            if not it.get("essential", True) or not (w and l): continue
            fw, fl = sorted(it["footprint_in"])
            # Some catalogue entries use clearance_in for a VIEWING or standing distance rather
            # than a physical gap — a television and a hung picture are both about four inches
            # deep. Nothing four inches deep constrains the width of a room, so anything without
            # real bulk is not a fit constraint.
            if fw < 8:
                continue
            # Read, never coerced. `or 0` here turned an unstated clearance into a measured zero
            # (OQ 52's smaller member): the catalogue's twenty nulls all meant zero, but so would
            # an item whose clearance an author forgot, and nothing told them apart. clearance_in
            # is now a required number in schema/room.schema.json, so a missing one fails
            # check_rooms rather than passing this check silently.
            cl = it["clearance_in"]
            # A table needs clearance on both sides; a counter, bench, sideboard or run of
            # casework is against a wall and needs it on one. Treating them alike fails every
            # galley kitchen and butler's pantry against its own rule.
            # WP-7.2: READ, never inferred. `placement` is declared in
            # schema/room.schema.json and was authored on all 278 furniture items; until then
            # it was on 0 of them and this line guessed from the item's NAME with a regex --
            # a guess in code where the schema has a field, which is the pattern this project
            # keeps paying for. The regex called 84 items against-wall; the authored data
            # calls 159, so it had been demanding two-sided clearance for a sideboard, a
            # nightstand and a console table alike. `check_rooms.py` now requires the field,
            # so it cannot silently go missing again.
            place = it.get("placement") or "freestanding"
            sides = 1 if place in ("against-wall", "corner", "built-in") else 2
            need_short = (fw + sides * cl) / 12.0
            need_long = (fl + 2 * min(cl, 36)) / 12.0     # ends take chair pull, not full passage
            if w + 1e-6 < need_short:
                F.add("serious", "furniture",
                      f"{label} cannot take its {it['item']}: needs {need_short:.1f} ft across ({fw} in item + {sides} x {cl} in clearance, {place}), has {w} ft.",
                      room=rid, rule=rt["dimensions"].get("critical_dimension"),
                      fix=f"Widen to {need_short:.1f} ft, or accept that the room will not hold a {it['item']}.")
            elif l + 1e-6 < need_long:
                F.add("minor", "furniture",
                      f"{label} is tight along its length for its {it['item']}: needs about {need_long:.1f} ft, has {l} ft.", room=rid)

        # ---- daylight
        # Depth is measured FROM the lit wall, so the rule has to account for how the room is lit:
        # a room with glass on two opposite walls is lit from both ends and only half as deep as it
        # measures, and a cross-lit room tolerates roughly half again the depth of a single-sided one.
        dm = rt["daylight"]["depth_multiplier"]
        wh = r.get("window_head_ft")
        walls = {win.get("wall") for win in r.get("windows", []) if win.get("wall")}
        OPP = {"N": "S", "S": "N", "E": "W", "W": "E", "NE": "SW", "SW": "NE", "NW": "SE", "SE": "NW"}
        two_ended = any(OPP.get(w) in walls for w in walls)
        effective_depth = (l / 2.0) if (two_ended and l) else l
        reach = dm * wh * (1.5 if len(walls) >= 2 and not two_ended else 1.0) if wh else None
        # OQ 31, ruled 24 Aug 2026: a room may declare that this rule does not govern it. That is
        # a THIRD state, not a pass -- the depth was never in question for a garage, which is
        # deeper than any window can light and is not thereby defective. Reported at `info` so it
        # appears in the record as a rule deliberately not applied, rather than vanishing, because
        # a rule that quietly stops looking is exactly what this corpus refuses elsewhere.
        governs = rt["daylight"].get("depth_governs", True)
        if not governs and wh and effective_depth and reach and effective_depth > reach * 1.05:
            F.add("info", "daylight",
                  f"{label} is deeper than its daylight would reach, and the depth rule does not "
                  f"govern this room type — not evaluated rather than passed.",
                  room=rid, rule="rooms/%s.json daylight.depth_governs is false" % r["type"])
        if governs and wh and effective_depth and dm < 10 and reach and effective_depth > reach * 1.05:
            how = ("lit from both ends, so measured at half its length" if two_ended
                   else "cross-lit, so the reach is relaxed by half" if len(walls) >= 2
                   else "lit from one side")
            F.add("serious", "daylight",
                  f"{label} is {effective_depth:.0f} ft deep against a {wh} ft window head ({how}); useful daylight reaches about {reach:.1f} ft.",
                  room=rid, fix="Raise the head, light the far end from another side, or accept the back of the room as a service zone.")
        want_sides = rt["daylight"].get("sides_lit") or 1
        lit_walls = {win.get("wall") for win in r.get("windows", []) if win.get("wall")}
        if r.get("windows") and len(lit_walls) < want_sides:
            F.add("minor", "daylight", f"{label} is lit from {len(lit_walls)} side(s); the room type wants {want_sides}.", room=rid)
        if not r.get("windows") and rt["function_class"] in ("public", "living", "dining", "sleeping", "work"):
            F.add("serious", "daylight", f"{label} has no windows.", room=rid)

        # ---- adjacency, honouring style exceptions
        for kind, key in (("must_adjoin", "must_adjoin"), ("should_adjoin", "should_adjoin")):
            for rule in rt["adjacency"].get(key, []):
                if excepted(rule, chain): continue
                if (r["type"], key, rule["room"]) in suppressed: continue
                relation = rule.get("relation")
                # --- vertical relations (OQ 57). A rule that IS vertical is satisfied only
                # vertically; a horizontal rule marked vertical_ok may be satisfied either way.
                if relation in ("open-to-below", "open-to-above"):
                    d = "below" if relation == "open-to-below" else "above"
                    if rule["room"] in types_vertically_from(rid, d): continue
                    sev = STRENGTH_SEV.get(rule.get("strength", "strong"), "serious")
                    if key == "should_adjoin": sev = "minor" if sev == "fatal" else sev
                    F.add(sev, "adjacency",
                          f"{label} should be open to a {rule['room'].replace('-', ' ')} on the "
                          f"storey {d} it, and there is none.",
                          room=rid, rule=rule["why"])
                    continue
                direct = key == "must_adjoin" and relation == "direct-door"
                near = types_adjacent(rid) if direct else types_near(rid)
                if rule["room"] in near: continue
                if rule.get("vertical_ok") and (
                        rule["room"] in types_vertically_from(rid, "below")
                        or rule["room"] in types_vertically_from(rid, "above")):
                    continue
                # A named intermediary satisfies the rule. The butler's pantry is not a failure
                # to connect the kitchen to the dining room; it is the connection.
                if rule.get("via"):
                    ok = False
                    for mid in adj[rid]:
                        if rooms[mid]["type"] in rule["via"] and rule["room"] in types_adjacent(mid):
                            ok = True; break
                    if ok: continue
                sev = STRENGTH_SEV.get(rule.get("strength", "strong"), "serious")
                if key == "should_adjoin": sev = "minor" if sev == "fatal" else sev
                _modelled = types_modelled(rid)
                if rule["room"] not in _modelled:
                    # Absence is a different claim from non-adjacency. A plan record that does not
                    # model closets is coarse, not wrong, and reporting that at the same severity as
                    # a genuine adjacency failure buries the findings that matter.
                    F.add("minor" if not strict else sev, "completeness",
                          f"{label} wants to adjoin a {rule['room'].replace('-', ' ')} and the plan models none.",
                          room=rid, rule=rule["why"],
                          fix="Either the plan is missing the room, or the record simply does not model it. Run with --strict to treat absence as a failure.")
                else:
                    # OQ 43: the plan models a room that WOULD satisfy this rule -- itself, or
                    # something that substitutes for it in the right direction -- and the subject
                    # does not reach it. That is an adjacency failure and it lands at the rule's
                    # own severity, which is what "make it directional and report them" means.
                    #
                    # Before the direction existed, 542 findings of this shape were held at
                    # `minor` because 294 of them were the substitution running backwards -- a
                    # general room offered where a specific one was asked for -- and promoting
                    # those would have been reporting a room the plan does not have. Those 294
                    # now fall to the branch above and say the true thing. The 214 that remain
                    # are real, and 115 of them are fatal across 67 styles.
                    _eq = sorted(satisfied_by(rule["room"]) & {rooms[x]["type"] for x in rooms if x != rid}
                                 - {rule["room"]})
                    under = ""
                    if _eq:
                        under = (" The plan models it as "
                                 + " and ".join(x.replace("-", " ") for x in _eq) + ".")
                    F.add(sev, "adjacency",
                          f"{label} does not reach a {rule['room'].replace('-', ' ')}"
                          + (" through a direct door." if rule.get("relation") == "direct-door"
                             else " directly or across a hall.") + under,
                          room=rid, rule=rule["why"])
        for rule in rt["adjacency"].get("must_not_adjoin", []):
            if excepted(rule, chain): continue
            if (r["type"], "must_not_adjoin", rule["room"]) in suppressed: continue
            if rule["room"] not in types_adjacent(rid): continue
            relation = rule.get("relation", "")
            for other in adj[rid]:
                if rooms[other]["type"] != rule["room"]: continue
                if relation in ("acoustically-separated", "not-visible-from") and (
                        rel.get((rid, other)) == relation
                        or declared_rel.get((rid, other)) == relation):
                    continue
                pair = tuple(sorted((rid, other)))
                if pair in seen_pairs: continue          # a mutual prohibition is one finding, not two
                seen_pairs.add(pair)
                F.add(STRENGTH_SEV.get(rule.get("strength", "strong"), "serious"), "adjacency",
                      f"{label} adjoins {rooms[other].get('name') or rule['room'].replace('-', ' ')}, which it should not.",
                      room=rid, rule=rule["why"],
                      fix=f"Separate them, or record the relation as '{relation}' if the separation is real.")
        ef = rt["adjacency"].get("entered_from")
        if ef:
            froms = {rooms[x]["type"] for x in adj[rid] if rel.get((rid, x)) == "direct-door"}
            ext = any(d["to"] == "exterior" for d in r.get("doors", []))
            if ext: froms.add("exterior")
            bad = froms - set(ef)
            if bad and froms:
                F.add("minor", "adjacency",
                      f"{label} is entered from {', '.join(sorted(b.replace('-', ' ') for b in bad))}; the catalogue expects entry from {', '.join(ef[:4])}.",
                      room=rid)
        if rt["adjacency"].get("never_a_through_room") and len(adj[rid]) > 1:
            F.add("minor", "circulation", f"{label} has {len(adj[rid])} connections and the room type should not be a through room.", room=rid)

        # ---- servicing
        if rt["servicing"].get("plumbing") in ("light", "heavy") and not r.get("fixtures"):
            F.add("info", "servicing", f"{label} is a plumbed room type with no fixtures listed.", room=rid)

    # ---- privacy gradient
    for rid, r in rooms.items():
        rt = C["rooms"].get(r["type"])
        if not rt: continue
        for other in adj[rid]:
            ot = C["rooms"].get(rooms[other]["type"])
            if not ot or rel.get((rid, other)) != "direct-door": continue
            # Circulation is RANK-TRANSPARENT. A corridor at rank 1 opening onto bedrooms at
            # rank 4 is what a corridor is for — it IS the buffer. Flagging it inverts the rule.
            if rt["function_class"] in ("circulation", "threshold") or ot["function_class"] in ("circulation", "threshold"):
                continue
            gap = ot["privacy_rank"] - rt["privacy_rank"]
            if gap >= 3:
                F.add("serious", "privacy",
                      f"A door runs straight from {r.get('name') or rt['name']} (rank {rt['privacy_rank']}) to "
                      f"{rooms[other].get('name') or ot['name']} (rank {ot['privacy_rank']}), jumping {gap} ranks.",
                      room=rid, rule="The public-to-private gradient: 0 street, 1 threshold, 2 public, 3 family, 4 private, 5 intimate.",
                      fix="Insert a buffer — a hall, a vestibule, a closet wall. A plan that scrambles the gradient feels wrong however well it is detailed.")

    # ---- wet-room stacking
    wet = [rid for rid, r in rooms.items()
           if set(r.get("fixtures") or []) & {"wc", "lavatory", "tub", "shower", "sink", "washer", "dishwasher"}]
    for rid in wet:
        r = rooms[rid]
        near = any(x in wet for x in adj[rid]) or (r.get("stacks_over") in wet)
        if not near and len(wet) > 1:
            F.add("minor", "servicing",
                  f"{r.get('name') or rid} is a wet room with no other wet room adjacent or below it.",
                  room=rid, fix="Stack or pair wet rooms. An isolated bath on the far side of a plan is the most expensive plumbing decision most clients make without knowing it.")

    # ============================================================ GROUPING LAYER
    for gid in plan.get("groupings", []):
        g = C["groupings"].get(gid)
        if not g:
            # rule=gid: without it the finding names no rule, and a consumer keyed by rule
            # (compose.py's canon axis) credits the grouping as clean while still counting it.
            F.add("serious", "grouping", f"Unknown grouping '{gid}'.", rule=gid,
                  fix="Use an id from groupings/.")
            continue
        sv = next((v for v in g.get("style_variation", []) if v["style"] in chain), None)
        if sv and sv.get("present") is False:
            F.add("serious", "grouping", f"The plan declares {g['name']}, which {style} does not have: {sv['note']}", rule=gid)
        for want in g["rooms"]:
            # satisfied_by(), not a raw membership test. Every other layer in this file asks
            # the substitution table whether something the plan HAS would answer the rule
            # (OQ 43); the grouping layer asked whether the exact type was present, and so
            # convicted a centre-passage plan of having no entrance hall — a serious finding,
            # on the top-ranked candidate of the shipped Georgian brief, produced by a table
            # this file already carries and already trusts everywhere else.
            if want["role"] in ("primary",) and not (satisfied_by(want["room"]) & types_present):
                F.add("serious", "grouping",
                      f"{g['name']} requires a {want['room'].replace('-', ' ')} and the plan has none.", rule=gid)
        if plan.get("massing"):
            att = next((a for a in g["attaches_to"] if a["massing"] == plan["massing"]), None)
            if att and att.get("fit") == "forbidden":
                F.add("serious", "grouping",
                      f"{g['name']} is marked forbidden in a {plan['massing'].replace('-', ' ')}: {att.get('note','')}", rule=gid)
            elif not att:
                F.add("info", "grouping", f"{g['name']} has no recorded fit for massing '{plan['massing']}'.", rule=gid)
        span = g.get("privacy_span")
        if span:
            ranks = [C["rooms"][rooms[x]["type"]]["privacy_rank"] for x in rooms
                     if rooms[x]["type"] in {y["room"] for y in g["rooms"]} and rooms[x]["type"] in C["rooms"]]
            if ranks and (min(ranks) < span[0] or max(ranks) > span[1]):
                F.add("minor", "grouping",
                      f"{g['name']} spans privacy ranks {min(ranks)}-{max(ranks)}; the grouping is defined for {span[0]}-{span[1]}.", rule=gid)
        for ir in g["internal_rules"]:
            if ir.get("severity") == "hard" and not ir.get("test"):
                F.add("info", "grouping", f"[{g['name']}] check by hand: {ir['statement']}", rule=gid)

    # ============================================================ CODE LAYER (advisory)
    juris = (plan.get("context") or {}).get("jurisdiction")
    for rid, r in rooms.items():
        rt = C["rooms"].get(r["type"])
        if not rt: continue
        w, l = r.get("width_ft"), r.get("length_ft")
        label = r.get("name") or rt["name"]
        habitable = rt["function_class"] in ("public", "living", "dining", "sleeping", "work")
        if habitable and w and l:
            if w * l < 70: F.add("advisory", "code", f"{label} is {w*l:.0f} sf; IRC R304.1 wants 70 sf for a habitable room.", room=rid, rule="IRC R304.1")
            if min(w, l) < 7: F.add("advisory", "code", f"{label} is {min(w,l)} ft in one dimension; IRC R304.2 wants 7 ft.", room=rid, rule="IRC R304.2")
        ch = r.get("ceiling_ft")
        if habitable and ch and ch < 7:
            F.add("advisory", "code", f"{label} ceiling {ch} ft; IRC R305.1 wants 7 ft.", room=rid, rule="IRC R305.1")
        if rt["function_class"] == "sleeping":
            if not any(win.get("egress") for win in r.get("windows", [])) and not any(d["to"] == "exterior" for d in r.get("doors", [])):
                F.add("advisory", "code", f"{label} has no emergency escape opening. IRC R310.1 requires one in every sleeping room.",
                      room=rid, rule="IRC R310.1", fix="A fixed or high transom window does not count.")
        if r["type"] == "garage":
            for other in adj[rid]:
                ot = C["rooms"].get(rooms[other]["type"])
                if ot and ot["function_class"] == "sleeping":
                    F.add("serious", "code", f"{label} adjoins a sleeping room. IRC R302.5.1 forbids a garage opening into a sleeping room and requires rated separation.",
                          room=rid, rule="IRC R302.5.1")
    if any(f["layer"] == "code" for f in F.items):
        F.add("info", "code", f"Code findings are ADVISORY and jurisdictional{' (' + juris + ' declared)' if juris else ''}. "
                              "They are the IRC model text, routinely amended locally, and must never be treated as a permit review.")

    # ============================================================ STYLE LAYER
    st = C["styles"].get(style)
    constraint_summary = {"present": 0, "clear": 0, "unjudged": 0}
    if st:
        kit = _resolved_slots(style)
        for slot_id, choice in (plan.get("declared") or {}).items():
            if slot_id not in C["slots"]:
                F.add("minor", "style", f"Declared slot '{slot_id}' is not in the ontology.", rule=slot_id); continue
            rec = kit.get(slot_id) or {}
            if rec.get("binding") == "forbidden":
                F.add("serious", "style", f"{style} forbids the slot '{slot_id}' outright, and the plan declares '{choice}'.", rule=slot_id)
            # A slot of cardinality `many` (elements/slots.json) may declare an OBJECT rather than
            # a bare variant id -- `declared.dormer` is the first, stating a count and a face as
            # well as a variant. Comparing the whole object against a variant id can never match,
            # so a record declaring a forbidden `shed-dormer` sailed past this check while
            # build/elevation.py refused it: two layers disagreeing about the same record. Read
            # the variant out of the object where there is one.
            chosen = choice.get("variant") if isinstance(choice, dict) else choice
            for v in rec.get("variants", []):
                if v.get("id") == chosen and v.get("status") == "forbidden":
                    F.add("serious", "style", f"'{chosen}' is a forbidden variant of {C['slots'][slot_id]['name'].lower()} in {style}.",
                          rule=slot_id, fix=v.get("note"))
        cvars = derive_constraint_vars(plan)
        # plan.measurements takes precedence over a derived value, mirroring the fault layer's
        # own practice a few dozen lines below: a number the plan record actually states beats
        # an inference from room geometry.
        c_namespace = {**cvars, **dict(plan.get("measurements") or {})}
        for c in st.get("constraints", []):
            if c.get("deprecated_in_favour_of"):
                continue
            test = c.get("test")
            if not test:
                # No formalised test -- either scope: judgment (schema/constraint.schema.json
                # forbids a test there), or this constraint just hasn't been migrated yet
                # (WP-1.1 migrated 140 of ~660). Unchanged from pre-WP-1.2 behaviour: only a
                # hard constraint gets a check-by-hand note, so the ~520 still-prose constraints
                # produce exactly the findings they always did.
                if c.get("severity") == "hard":
                    # rule is the constraint's own id when it has one (every migrated constraint
                    # does); falls back to style.kind for the pre-migration shape some styles'
                    # constraints may still be in, where no stable per-constraint id exists yet.
                    F.add("info", "style", f"Check by hand: {c['statement']}", rule=c.get("id") or f"{style}.{c['kind']}")
                continue
            r = core._eval_test(test, c_namespace)
            if not r or r["status"] != "evaluated":
                constraint_summary["unjudged"] += 1
                missing = r.get("missing") if r else None
                F.add("info", "style",
                      f"Cannot evaluate {c['id']} ({c['kind']}): {c['statement']}"
                      + (f" [needs {', '.join(missing)}]" if missing else ""),
                      rule=c["id"])
                continue
            if r["passes"]:
                constraint_summary["clear"] += 1
            else:
                constraint_summary["present"] += 1
                sev = CONSTRAINT_SEV.get(c.get("severity", "hard"), "serious")
                units = f" {r['units']}" if r.get("units") else ""
                F.add(sev, "style",
                      f"{c['statement']} (measured {r['value']}{units}, required {r['required']}{units}).",
                      rule=c["id"], fix=test.get("note"))
        if plan.get("massing"):
            aff = next((m for m in st.get("massing_affinities", []) if m["massing"] == plan["massing"]), None)
            if aff and aff["affinity"] == "forbidden":
                F.add("serious", "style", f"{st['name']} marks the {plan['massing'].replace('-', ' ')} massing forbidden: {aff.get('note','')}", rule="massing")
            elif not aff:
                F.add("minor", "style", f"{st['name']} records no affinity for the massing '{plan['massing']}'.", rule="massing")

    # ============================================================ FAULT LAYER
    meas = dict(plan.get("measurements") or {})
    for rid, r in rooms.items():                                  # derive what the plan can supply
        w, l = r.get("width_ft"), r.get("length_ft")
        if w and l:
            meas.setdefault(f"{rid}_width_ft", min(w, l)); meas.setdefault(f"{rid}_length_ft", max(w, l))
    if rooms:
        first = next(iter(rooms.values()))
        if first.get("ceiling_ft"): meas.setdefault("ceiling_height_in", first["ceiling_ft"] * 12)
    # ELEVATION LAYER (WP-3.2): build/elevation.py's own measurements dict is folded in here,
    # under the SAME setdefault precedence as everything else above -- a plan's own declared
    # measurements always win over what the generator derived. Wrapped: a plan that structure.py
    # or geometry.py cannot solve (an incomplete draft, say) should not take the whole validator
    # down with it; it just gets no elevation-derived measurements, same as "unjudged is not
    # passed" everywhere else in this corpus.
    try:
        EL = _load("elevation", f"{ROOT}/build/elevation.py")
        elev = EL.build_elevation(plan)
        if "error" not in elev:
            for k, v in elev.get("measurements", {}).items():
                # A None is the elevation layer saying it could not judge that quantity, and it
                # must not enter the measurements dict at all: a key present with a None value
                # is a measurement the fault evaluator will try to compare, and the only reason
                # that did not already produce nonsense is that it threw and was swallowed.
                # Absent is what "unjudged" looks like here (OQ 59).
                if v is None: continue
                meas.setdefault(k, v)
    except Exception:
        pass
    # limit lifted from the API default of 40: faults_present was never truncated, and the
    # could_not_judge list (surfaced as fault_unjudged below) has to be the whole list or
    # "unjudged is not passed" degrades into "the first forty unjudged are not passed".
    # WP-8.4: hand the fault corpus what this HOUSE is, not only what its style permits.
    # An exception's `granted_when` asks about the wall, the roof and the date, and a style
    # id can rarely answer -- most styles permit several constructions. A plan record
    # already declares the ones it chose (`declared.construction_type`,
    # `declared.primary_cladding`) and dates itself (`context.date_of_representation`), so
    # a licence that is merely undecidable against a style becomes a real yes or no here.
    _ctx = {"declared": plan.get("declared") or {}}
    _date = (plan.get("context") or {}).get("date_of_representation")
    if isinstance(_date, (int, float)):
        _ctx["date"] = int(_date)
    fr = core.check_measurements(meas, style=style, limit=10**6, context=_ctx) if meas else {"faults_present": [], "summary": {"present": 0, "clear": 0, "unjudged": 0}}
    for x in fr.get("faults_present", []):
        # Quote the test that FAILED, not the first one that ran. A fault carrying secondary
        # tests can have its primary pass and a secondary fail; reading results[0] then printed
        # the passing measurement as the evidence for the fault -- "The House With No Fire: 2
        # against at-least 1" on a Cape that has two chimneys. core.check_measurements now
        # hands back `failing` beside `results`; the fallback keeps this working against an
        # older core.
        ev = (x.get("failing") or x["results"])[0]
        F.add(x["severity"] if x["severity"] in SEV_ORDER else "serious", "fault",
              f"{x['name']}: {ev.get('value')} against {ev.get('required')}.",
              rule=x["fault"], fix=x.get("fix_cheap"))

    # ---- the DRAWN layer (WP-6.2). Everything above this line judges the plan the record
    # DECLARES. This layer judges the house that was actually placed, and it is the only
    # layer permitted to read `geometry` — a separation kept deliberately, so that a plan
    # nobody has placed is never failed for facts about a placement that does not exist.
    #
    # OQ 54 ruled in August that plan_check must NOT read room.geometry, and Lucas reopened
    # that ruling for this package. The reason is in the report: the critic scored the
    # declared house while the sheet drew the solved one, so a landing that misses its own
    # stair, a room drawn at 63% of its declared area, and a bathroom no door reaches all
    # produced no finding at all. Each of those is now a finding, and a record with no
    # placement gets a single `info` saying the layer could not evaluate — never a pass.
    drawn = drawn_layer(plan, rooms, level_of, C, F)

    counts = {}
    for f in F.items: counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    return {"plan": plan["id"], "style": style, "rooms": len(rooms), "drawn_summary": drawn,
            "counts": counts, "fault_summary": fr.get("summary"), "constraint_summary": constraint_summary,
            # The could-not-judge detail, not just its count. fault_summary already counts
            # unjudged; without the list itself a caller cannot say WHICH faults were
            # beyond evaluation, and unjudged-is-not-passed needs the which. Additive.
            "fault_unjudged": fr.get("could_not_judge", []),
            # NOT APPLICABLE is a fourth state and not a fifth kind of pass. Every test of the
            # fault is preconditioned on a measurement this house does not meet -- a house that
            # states it carries no dormers has no dormer rhythm to be off -- so no test ran.
            # Before core.check_measurements grew this list such a fault appeared in none of the
            # others, which reads to a caller exactly like clear.
            "fault_not_applicable": fr.get("not_applicable", []),
            "findings": F.sorted(),
            "note": ("Style exceptions are honoured throughout — a rule a style legitimately breaks is not reported. "
                     "Code findings are advisory. Anything the fault corpus could not judge is unknown, not passed.")}

# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--layer"); ap.add_argument("--min-severity", default="info")
    ap.add_argument("--strict", action="store_true", help="treat an absent room type as a failure, not a gap in the record")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    import jsonschema
    jsonschema.validate(plan, json.load(open(f"{ROOT}/schema/plan.schema.json")))
    res = check(plan, strict=a.strict)
    if a.json: print(json.dumps(res, indent=1, ensure_ascii=False)); return
    cut = SEV_ORDER.index(a.min_severity)
    print(f"\n  {plan['name']}   [{res['style']}]   {res['rooms']} rooms")
    print("  " + "  ".join(f"{k} {v}" for k, v in sorted(res["counts"].items(), key=lambda kv: SEV_ORDER.index(kv[0]))))
    last = None
    for f in res["findings"]:
        if SEV_ORDER.index(f["severity"]) > cut: continue
        if a.layer and f["layer"] != a.layer: continue
        if f["layer"] != last: print(f"\n  {f['layer'].upper()}"); last = f["layer"]
        print(f"    [{f['severity']:<8}] {f['statement']}")
        if f.get("rule"): print(f"               why: {f['rule'][:150]}")
        if f.get("fix"): print(f"               fix: {f['fix'][:150]}")
    print()

if __name__ == "__main__":
    main()
