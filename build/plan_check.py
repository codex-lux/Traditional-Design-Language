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

    # AND `kind` IS PART OF THE IDENTITY, WHICH IT WAS NOT (audit, 7 Sep 2026).
    #
    # The docstring above says a finding's identity is WHAT IT IS ABOUT. `kind` is the field
    # that says what it is about, in one machine-readable token, and `add()` was the one reader
    # in the tree that did not look at it -- so two findings of DIFFERENT kinds about one room
    # in one layer were separated only by the order they happened to be minted in, and an
    # ordinal is not an identity.
    #
    # MEASURED, because the cost was live rather than theoretical. Shrink `backhall` on the
    # Tidewater record until its depth finding clears and the aspect finding beneath it -- which
    # did not change at all -- moved from `daylight:backhall#1` to `daylight:backhall`. The
    # bench diffs on `f.id` (`PlanWorkbench.jsx`, "N findings new since the last evaluation"),
    # so it reported a finding cleared and a new one opened for a row nothing had touched. The
    # same mechanism churned six ids at the merge of WP-11.9, for findings whose statements were
    # byte-identical either side.
    #
    # This CHURNS every id carrying a kind, once, and that is the right trade: the ids are
    # per-process and per-plan by construction (the docstring says so -- two plans may mint the
    # same id and that is a feature), nothing on disk holds one, and the alternative is a
    # namespace that reshuffles itself every time a layer grows a finding.
    def add(self, severity, layer, statement, **kw):
        parts = [layer, str(kw.get("room") or "")]
        for key in ("rule", "constraint", "fault"):
            v = kw.get(key)
            if isinstance(v, str) and self._ID_LIKE.match(v):
                parts.append(v)
                break
        kind = kw.get("kind")
        if isinstance(kind, str) and self._ID_LIKE.match(kind):
            parts.append(kind)
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


def furniture_shortfalls(rt, w, l):
    """Which essential items of `rt` will not fit a `w` x `l` ft rectangle, and by how much.

    ONE spelling of the fit arithmetic with TWO callers -- the room layer, which hands it the
    DECLARED width and length, and the drawn layer, which hands it the PLACED rectangle. Until
    WP-9.6 only the first existed, so a room declared adequate and drawn as a sliver passed its
    own furniture check: over the sixteen plans the furniture layer emitted 137 findings whether
    or not the plan carried geometry, which is the measurement of a check that cannot see the
    drawing. Callers differ in WORDING and LAYER and never in arithmetic; do not transcribe these
    expressions anywhere else. (`openings.required_wall_ft` is NOT the precedent for this -- that
    rule is deliberately spelled three times, one of them JavaScript, and held together by
    tests/fixtures/sheet_symbols/. The discipline transfers; the mechanism does not.)

    `w` is the SHORT dimension and `l` the LONG one, and the item is paired the same way: its
    short side is charged against the room's width and its long side against the room's length.
    WP-9.2 s8 published that `sorted()` here "assumes every item rotates" and so turned the
    kitchen island sideways; that was wrong, and reading this function rather than that sentence
    is what found it. The pairing is the rule, not a defect -- an 84 x 27 in island in a 12 x 16
    ft kitchen needs 9.25 ft across and 13.0 ft along, and gets both.
    """
    out = []
    for it in rt.get("furniture", []):
        if not it.get("essential", True) or not (w and l):
            continue
        fw, fl = sorted(it["footprint_in"])
        # Some catalogue entries use clearance_in for a VIEWING or standing distance rather
        # than a physical gap - a television and a hung picture are both about four inches
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
        # TWO INDEPENDENT CHECKS, NOT AN `elif`. Until WP-9.6 the long axis was tested only
        # when the short axis had PASSED, so a room failing both was told about one of them:
        # 41 long-axis shortfalls on the declared record and 15 on the drawn one were computed
        # here and dropped. They are not silences -- the room still took its short-axis finding
        # -- but the second fact was never stated, and a room too narrow for a bed is very often
        # also too short for it.
        short = w + 1e-6 < need_short
        long_ = l + 1e-6 < need_long
        if short:
            out.append({"axis": "short", "item": it["item"], "need_ft": need_short,
                        "have_ft": w, "sides": sides, "clearance_in": cl,
                        "placement": place, "item_in": fw, "footprint_in": [fw, fl]})
        if long_:
            out.append({"axis": "long", "item": it["item"], "need_ft": need_long,
                        "have_ft": l, "sides": sides, "clearance_in": cl,
                        "placement": place, "item_in": fl, "footprint_in": [fw, fl]})
    return out


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
    # WHICH ENGINE PLACED THIS (WP-9.1). Every finding of this layer is a finding about a
    # placement, and on the workbench the drag path places with the search by name while
    # everything else takes the proof -- a fatal that appears mid-drag and clears on the
    # proof must not read as the house changing. Set once, passed through one wrapper, so
    # no call site can omit it.
    engine = ((plan.get("geometry_report") or {}).get("solver") or {}).get("engine")

    def _add(severity, layer, statement, **kw):
        F.add(severity, layer, statement, engine=engine, **kw)

    placed = {rid: r["geometry"] for rid, r in rooms.items() if r.get("geometry")}

    def _adjacent_placed(rid, tol=0.4):
        """Rooms on the same level whose placed rectangle shares a run of wall with this
        one at least as long as a door and its jambs -- what `add-the-grammar-door` may join
        a stranded room to. Read off the placement, which is this layer's licence."""
        g = placed.get(rid)
        if not g:
            return []
        OP = _load("openings", f"{ROOT}/build/openings.py")
        need = OP.required_wall_ft(3.0)
        out = []
        for oid, h in placed.items():
            if oid == rid or level_of.get(oid) != level_of.get(rid):
                continue
            ox = min(g["x_ft"] + g["width_ft"], h["x_ft"] + h["width_ft"]) - max(g["x_ft"], h["x_ft"])
            oy = min(g["y_ft"] + g["depth_ft"], h["y_ft"] + h["depth_ft"]) - max(g["y_ft"], h["y_ft"])
            touch_x = abs(g["x_ft"] + g["width_ft"] - h["x_ft"]) <= tol or abs(h["x_ft"] + h["width_ft"] - g["x_ft"]) <= tol
            touch_y = abs(g["y_ft"] + g["depth_ft"] - h["y_ft"]) <= tol or abs(h["y_ft"] + h["depth_ft"] - g["y_ft"]) <= tol
            if (touch_x and oy >= need) or (touch_y and ox >= need):
                out.append(oid)
        return sorted(out)

    if not placed:
        _add("info", "drawn",
             "The drawn layer could not evaluate: this record carries no placement. "
             "Run build/geometry.py to place it, then re-check.",
             fix="python3 build/geometry.py <plan>", kind="no-placement")
        return {"evaluated": False, "reason": "no placement on this record",
                "rooms_placed": 0}

    out = {"evaluated": True, "rooms_placed": len(placed), "unreachable": [],
           "diverged": [], "unplaced_openings": 0}

    # The envelope the rooms were placed in. Taken from the plan's own footprint where it
    # states one, and otherwise from the union of the placed rectangles — which IS the
    # envelope, because the slicer tiles the block exactly. Used only to say which boundary
    # a room reaches; nothing here promotes it to a constraint.
    _fp = plan.get("footprint") or {}
    fp_w = _fp.get("width_ft") or max((g["x_ft"] + g["width_ft"] for g in placed.values()), default=0.0)
    fp_h = _fp.get("depth_ft") or max((g["y_ft"] + g["depth_ft"] for g in placed.values()), default=0.0)

    # WP-11.6 LAYER 5: THE ENVELOPE IS THE ROOM'S OWN MASSING ELEMENT, NOT THE MAIN BLOCK.
    # Ruling 4 of `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`. The four
    # `touches` tests below read the main block's scalars until this, so a kitchen sitting on its
    # own dependency's south and west faces was convicted of being "drawn in the middle of the
    # house": the critic and the renderer wrong in OPPOSITE directions about the same wall.
    # Measured on the reference fixture, with the dependency's windows forced unplaced so the test
    # is reached at all -- main-block read `[]` for both dependency rooms, element read `['S','W']`
    # and `['S','E']`, while the two genuine interior rooms (`chamber2`, `stair`) read `[]` on
    # both. The control is what makes it a fix rather than a loosening.
    #
    # `envelopes` is `openings`' -- layer 1's own map, not a second spelling of the `block`-tag
    # join -- and it returns `{}` below two elements, so all sixteen one-rectangle plans fall back
    # to the main block by construction rather than by a branch.
    _OP = _load("openings", f"{ROOT}/build/openings.py")
    _envs = _OP.envelopes(plan)

    def _envelope(rid):
        return _envs.get(rid) or (0.0, 0.0, fp_w, fp_h)

    # Which element a room is in, for the finding to NAME. The predicate is `geometry`'s own
    # `is_block_tag` and not an inline truth test -- that function exists precisely because three
    # places ask this question and two of them answering differently is how a plan comes to be
    # refused by one layer for an element another layer does not build.
    _GEOM = _load("geometry", f"{ROOT}/build/geometry.py")
    _element_of = {r["id"]: r["block"] for lv in plan.get("levels", [])
                   for r in lv.get("rooms", []) if _GEOM.is_block_tag(r.get("block"))}

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
            _add("fatal", "drawn",
                  f"{name} cannot be reached from outside the house on the drawing. "
                  + (f"The record declares {declared} door(s) to it and the placement "
                     f"realised none of them."
                     if declared else "The record declares no door to it at all."),
                  room=rid,
                  fix=("Place the plan again, or move the rooms so the declared doors have "
                       "a wall to sit in — build/openings.py names each one it could not "
                       "place and why."),
                  kind="unreachable", declared_doors=declared,
                  unplaced_pairs=sorted(p for p in unplaced_pairs if rid in p),
                  adjacent_placed=_adjacent_placed(rid))
    else:
        _add("info", "drawn",
             "Reachability could not be evaluated: no exterior door on this plan is placed, "
             "so there is no outside to walk in from.", kind="no-outside")

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
        _add("serious", "drawn",
              f"{name} joins no other room on the drawing — the only way in is from outside. "
              f"The record declares {len(interior_declared)} interior door(s) and the "
              f"placement realised none of them.",
              room=rid,
              fix=("Place the plan again, or move these rooms so their declared doors have a "
                   "wall to sit in — build/openings.py names each door it could not place "
                   "and why."),
              kind="cut-off", declared_doors=len(interior_declared),
              unplaced_pairs=sorted(p for p in unplaced_pairs if rid in p),
              adjacent_placed=_adjacent_placed(rid))

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
        _add(sev, "drawn",
              f"{name} is drawn at {round(pa)} sf against the {round(da)} sf the record "
              f"declares ({pct:+.0f}%).",
              room=rid,
              fix=("Accept the drawn size into the record, or constrain the placement — "
                   "the sheet prints the drawn figure, so the record and the drawing "
                   "disagree until one of them moves."),
              kind="drawn-vs-declared", declared_sf=round(da, 1), drawn_sf=round(pa, 1),
              pct=round(pct, 1))

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
            _add("info", "drawn",
                  f"{name} declares it stacks over '{so}', which this placement does not "
                  f"place — the claim could not be evaluated.", room=rid,
                  kind="stack-unplaced", over=so)
            continue
        if level_of.get(rid) == level_of.get(so):
            continue                      # a same-level claim is not a stack
        ox = min(g["x_ft"] + g["width_ft"], below["x_ft"] + below["width_ft"]) \
            - max(g["x_ft"], below["x_ft"])
        oy = min(g["y_ft"] + g["depth_ft"], below["y_ft"] + below["depth_ft"]) \
            - max(g["y_ft"], below["y_ft"])
        if ox <= 0 or oy <= 0:
            out["stacks_broken"].append(rid)
            _add("serious", "drawn",
                  f"{name} declares it stacks over '{so}' and is drawn clear of it "
                  f"entirely — a stack with nothing under it.",
                  room=rid,
                  fix="Place the two together, or drop the stacks_over claim.",
                  kind="stack-broken", over=so)
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
                _add("minor", "drawn",
                      f"{name} overlaps the stair well by only {got:.0f} sf; a landing not "
                      f"less than the stair's own width is "
                      f"groupings/stair-and-landing-core.json's hard rule.",
                      room=rid, kind="landing-off-well", over=so,
                      overlap_sf=round(got, 1), need_sf=round((st.get("width_ft") or 3.0) ** 2, 1))
    if st and st.get("unplaced"):
        _add("serious", "drawn",
              f"The stair is not drawn: {st['unplaced']['reason']}",
              room=st.get("room"),
              fix="Give the stair hall the run its own storey height needs.",
              kind="stair-not-drawn",
              need_ft=[(st["unplaced"].get("needs") or {}).get("long_ft"),
                       (st["unplaced"].get("needs") or {}).get("short_ft")],
              have_ft=[(st["unplaced"].get("have") or {}).get("long_ft"),
                       (st["unplaced"].get("have") or {}).get("short_ft")],
              declared_fits=(st["unplaced"].get("needs") or {}).get("declared_fits"),
              form=(st["unplaced"].get("needs") or {}).get("form"),
              risers=(st["unplaced"].get("needs") or {}).get("risers"))

    # --- the passage, against its own record's words
    #
    # THE BAND LOOKUP HERE WAS DEAD CODE FROM THE DAY IT WAS WRITTEN, and it is worth
    # keeping the shape of the mistake in view. It read `cp.get("rules")`; the key in
    # groupings/centre-passage-core.json is `internal_rules`, so `band` was None on every
    # plan this checker has ever run. It was then never read: the two thresholds below are
    # hardcoded, and they came out of the ROOM record's prose rather than the grouping's
    # test, so the dead lookup changed no verdict and nothing noticed for three phases.
    # A lookup whose result is never used cannot fail loudly; it just quietly stops being
    # a lookup. The grouping's own ratio rule IS evaluated now -- in the grouping layer,
    # where the rest of its rules are judged, against `arrangement.grouping_vars` -- and
    # what stays here is the pair of checks that quote rooms/centre-passage.json directly.
    for rid, r in rooms.items():
        if r["type"] not in ("centre-passage", "cross-passage"):
            continue
        g = placed.get(rid)
        if not g:
            continue
        wft = min(g["width_ft"], g["depth_ft"])
        name = r.get("name") or rid
        if wft < 6.0:
            _add("serious", "drawn",
                  f"{name} is drawn {wft:.1f} ft wide. rooms/centre-passage.json: "
                  f"\"SIX TO SEVEN FEET is a passage that circulates\" — below that it does "
                  f"not.", room=rid, kind="passage-narrow", have_ft=round(wft, 1), band=[6.0, 7.0],
                  declared_ft=min(r.get("width_ft") or 0, r.get("length_ft") or 0) or None)
        elif 8.0 <= wft <= 9.0:
            _add("minor", "drawn",
                  f"{name} is drawn {wft:.1f} ft wide, in the dead zone its own record names: "
                  f"\"too wide to be economical and too narrow to furnish\".", room=rid,
                  kind="passage-dead-zone", have_ft=round(wft, 1), band=[6.0, 7.0],
                  declared_ft=min(r.get("width_ft") or 0, r.get("length_ft") or 0) or None)

    # --- fixtures that will not fit together
    for rid, r in rooms.items():
        for f in (r.get("fixture_layout") or []):
            if not f.get("unplaced"):
                continue
            name = r.get("name") or rid
            _add("serious", "drawn",
                  f"{name}: {f['item']} is not placed — {f['unplaced']['reason']}",
                  room=rid,
                  fix="Widen the room, or drop the fixture from the record.",
                  kind="fixture-unplaced", item=f["item"],
                  need_ft=[(f["unplaced"].get("needs") or {}).get("width_ft"),
                           (f["unplaced"].get("needs") or {}).get("depth_ft")],
                  have=f["unplaced"].get("have"))

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
                _add("minor", "drawn",
                      f"{name} has no unbroken run of wall for its {it['item']}: the longest "
                      f"its walls have left once the doors and windows are placed is "
                      f"{best:.1f} ft, and rooms/{r['type']}.json asks for {need:g} ft — "
                      f"\"{(it.get('note') or '').split('.')[0]}.\"",
                      room=rid,
                      fix="Move a window off that wall, or accept the piece elsewhere.",
                      kind="wall-run", item=it["item"], need_ft=need, have_ft=round(best, 2),
                      walls_with_windows=sorted({o["wall"] for o in (r.get("windows") or [])
                                                 if o.get("wall") and not o.get("unplaced")}))

    # --- THE SHAPE THE PLACEMENT GAVE THE ROOM (WP-9.1)
    #
    # This is the check that names the sheet Lucas read. The room layer above reads the same
    # bands, but it reads them off the DECLARED record -- and the declaration was fine. The
    # Tidewater brief declares a 16 x 20 kitchen; the placement drew it 10 x 30, kept the
    # area within 6% so the drawn-divergence check below stayed quiet, and shipped a sliver.
    # The declared house and the drawn house are two different houses, and until this block
    # only one of them was ever measured against the catalogue.
    #
    # That is OQ 54's own sentence -- "the critic scored the declared house while the sheet
    # drew the solved one" -- surviving in the one place the drawn layer had not reached.
    # Same bands, same two-tier severity, no new number: what changes is which rectangle is
    # held against them.
    for rid, r in rooms.items():
        g = placed.get(rid)
        rt = C["rooms"].get(r.get("type"))
        if not g or not rt:
            continue
        dims = rt.get("dimensions") or {}
        gw, gl = min(g["width_ft"], g["depth_ft"]), max(g["width_ft"], g["depth_ft"])
        name = r.get("name") or rid
        if dims.get("width_ft") and gw + 1e-6 < dims["width_ft"][0]:
            lo = dims["width_ft"][0]
            short = (lo - gw) / lo
            _add("serious" if short > 0.1 else "minor", "drawn",
                  f"{name} is DRAWN {gw:.1f} ft in its short dimension, below the {lo} ft "
                  f"floor for a {rt['name'].lower()} — the record declares "
                  f"{r.get('width_ft')} x {r.get('length_ft')} ft and the placement did not "
                  f"keep it.",
                  room=rid, rule=dims.get("critical_dimension"),
                  kind="drawn-width-below-floor", need_ft=lo, have_ft=round(gw, 2),
                  band=list(dims["width_ft"]), axis="width",
                  fix="The placement, not the record, is what has to change here.")
        if dims.get("proportion") and gw > 0:
            plo, phi = dims["proportion"]
            ar = round(gl / gw, 2)
            if ar > phi:
                over = (ar - phi) / phi
                _add("serious" if over > 0.25 else "minor", "drawn",
                      f"{name} is DRAWN {gw:.1f} x {gl:.1f} ft — {ar} to 1, against the "
                      f"{plo}-{phi} band a {rt['name'].lower()} is drawn to. The record "
                      f"declares {r.get('width_ft')} x {r.get('length_ft')} ft; the "
                      f"placement kept the area and lost the room.",
                      room=rid, rule=dims.get("critical_dimension"),
                      kind="drawn-proportion-above-band", have=ar, band=[plo, phi],
                      axis="proportion",
                      fix="The placement, not the record, is what has to change here.")

        # WP-9.6: the same catalogue arithmetic the room layer runs, against the rectangle that
        # was DRAWN. `furniture_shortfalls` is the one spelling of it; this caller differs from
        # the room layer's in wording and layer and in nothing else. Until this block the
        # furniture layer emitted 137 findings across the sixteen plans whether or not the plan
        # carried geometry -- so `breakfast`, declared 12 x 14 and drawn 7.0 x 27.0, passed a
        # check whose own arithmetic says it cannot take its essential table. That is Lucas's
        # second complaint, computed and never stated.
        for s_ in furniture_shortfalls(rt, gw, gl):
            if s_["axis"] == "short":
                _add("serious", "drawn",
                      f"{name} is DRAWN {s_['have_ft']:.1f} ft across and cannot take its "
                      f"{s_['item']}: needs {s_['need_ft']:.1f} ft ({s_['item_in']} in item + "
                      f"{s_['sides']} x {s_['clearance_in']} in clearance, {s_['placement']}). "
                      f"The record declares {r.get('width_ft')} x {r.get('length_ft')} ft, which "
                      f"holds it.",
                      room=rid, rule=dims.get("critical_dimension"),
                      kind="drawn-furniture-fit", need_ft=round(s_["need_ft"], 3),
                      have_ft=s_["have_ft"], axis="width", item=s_["item"],
                      sides=s_["sides"], clearance_in=s_["clearance_in"],
                      footprint_in=s_["footprint_in"],
                      fix="The placement, not the record, is what has to change here.")
            else:
                _add("minor", "drawn",
                      f"{name} is DRAWN {s_['have_ft']:.1f} ft along its length and is tight for "
                      f"its {s_['item']}: needs about {s_['need_ft']:.1f} ft.",
                      room=rid, rule=dims.get("critical_dimension"),
                      kind="drawn-furniture-fit", need_ft=round(s_["need_ft"], 3),
                      have_ft=s_["have_ft"], axis="length", item=s_["item"],
                      fix="The placement, not the record, is what has to change here.")

    # --- THE ROOM THE PLACEMENT LEFT IN THE DARK (WP-9.1)
    #
    # Lucas's complaint, verbatim: "There's a dining room off of the center passage, but it
    # doesn't get any light because it's directly in the middle of the house." Nothing in
    # this system could see that. The daylight layer above reads the room's DECLARED window
    # list, and build/compose.py writes a window for every wall the parti declares, so the
    # record claims windows on a room the placement put on no boundary wall at all.
    #
    # The fact was already in the record and had no reader. build/openings.py has written
    # `win["unplaced"] = {"reason": "the placement puts this room on no such boundary wall"}`
    # since WP-6.2, and `report["windows_unplaced"]` beside it, and a grep for either found
    # zero call sites in the whole tree. The drawn layer even SKIPS unplaced windows when it
    # measures a wall run, so an unplaced window made the sideboard check easier to pass.
    #
    # NOT DERIVED FROM `exterior_walls`. A plan's exterior_walls are aspirations, not
    # rectangle edges -- three Tidewater ground rooms each declare opposite walls, so each
    # would have to span the full depth of the house -- and promoting them to a constraint
    # here would convict houses of a wish. What this reads is what the placement DID: a
    # window the placement could not seat on any boundary, on a room whose own catalogue
    # record says it must be lit.
    for rid, r in rooms.items():
        g = placed.get(rid)
        if not g:
            continue
        rt = C["rooms"].get(r["type"]) or {}
        dl = rt.get("daylight") or {}
        if dl.get("depth_governs") is False:          # OQ 31's vocabulary: judged, and it does not apply
            continue
        if not dl.get("sides_lit"):
            continue
        wins = list(r.get("windows") or [])
        if not wins:
            continue                                   # the declared daylight layer owns this one
        seated = [w for w in wins if not w.get("unplaced")]
        if seated:
            continue
        name = r.get("name") or rid
        # TWO SITUATIONS WEAR ONE SYMPTOM, and they want different fixes. A room that touches
        # no boundary at all cannot be lit where it stands -- that is Lucas's dining room,
        # "directly in the middle of the house". A room that touches a boundary but not the
        # one its record names could be lit tomorrow by moving the window. Both are serious;
        # only the first is a plan that cannot work.
        env = _envelope(rid)
        ex0, ey0, ex1, ey1 = env
        touches = []
        if abs(g["y_ft"] - ey0) < 0.6: touches.append("S")
        if abs(g["y_ft"] + g["depth_ft"] - ey1) < 0.6: touches.append("N")
        if abs(g["x_ft"] - ex0) < 0.6: touches.append("W")
        if abs(g["x_ft"] + g["width_ft"] - ex1) < 0.6: touches.append("E")
        units = sum(int(w.get("count") or 1) for w in wins)
        # Which of those walls take the weather and still look at the side of the house. Empty on
        # a one-rectangle plan, so the sentence below is unchanged for every plan in this corpus.
        across = _OP.faces_across_a_gap(plan, env) if _envs else {}
        el = _element_of.get(rid)
        where = f" of the {el} element" if el and el != "main" else ""
        if not touches:
            _add("serious", "drawn",
                  f"{name} is drawn in the middle of the house{where}: it reaches no exterior "
                  f"wall on any side, so none of the {units} window(s) the record declares "
                  f"could be placed. rooms/{r['type']}.json wants {dl['sides_lit']} side(s) lit.",
                  room=rid, kind="drawn-landlocked", have=0, need=dl["sides_lit"],
                  element=el,
                  fix="Place the room on the perimeter, or accept it as an interior room and "
                      "take the windows out of the record.")
        else:
            why = next((w["unplaced"].get("reason") for w in wins if w.get("unplaced")), "unplaced")
            # RULING 4'S SECOND HALF, AND IT IS A SENTENCE RATHER THAN A SEVERITY. A wall facing
            # the gap is a real exterior wall -- it takes the weather and it can hold a window --
            # and it is also the wall that stares at the side of the house. Saying only "exterior"
            # loses the half a reader needs to judge the window.
            gap = [d for d in touches if d in across]
            note = ("" if not gap else
                    f" Its {'/'.join(gap)} wall(s) are exterior to the weather and interior to "
                    f"the view: they look across the gap at the "
                    f"{'/'.join(sorted({across[d] for d in gap}))} element.")
            _add("serious", "drawn",
                  f"{name} is drawn with no window: it stands on the "
                  f"{'/'.join(touches)} wall(s){where} and the record declares its {units} "
                  f"unit(s) of glass on "
                  f"{'/'.join(sorted({w.get('wall') or '?' for w in wins}))} — {why}. "
                  f"rooms/{r['type']}.json wants {dl['sides_lit']} side(s) lit.{note}",
                  room=rid, kind="drawn-window-off-the-placed-wall",
                  lit_walls=sorted(touches), need=dl["sides_lit"],
                  element=el, walls_across_a_gap=sorted(gap),
                  fix="Move the windows to the wall the placement actually gave the room.")

    # --- THE DOOR YOU COME IN BY, AND THE AXIS IT IS SUPPOSED TO BE ON (WP-9.1)
    #
    # "The entrance portico is ridiculously narrow and not even aligned with the center
    # passage." There is no axis vocabulary anywhere in this codebase: `entrance_score` in
    # build/geometry.py is a pair of boolean touch tests -- is the threshold room on an
    # entrance wall, is the circulation room behind it -- so a porch and a passage sitting
    # side by side, both touching the front, satisfy it completely and the search pays
    # nothing for the jog between them.
    #
    # The corpus states the rule twice and neither statement had a reader:
    #   rooms/entrance-hall.json adjacency.should_adjoin[centre-passage].why -- "where the
    #     plan has a passage the hall is its front end, and the axis must continue to a rear
    #     opening"
    #   openings/grammar.json placement_rules[op-passage-axis] -- "Where a circulation room
    #     reaches the boundary at both ends, its two exterior doors sit on one axis"
    #
    # PARAMETER-FREE, deliberately. The tolerance is the door's OWN leaf: two openings that
    # overlap at all read as one axis, and two that stand clear of each other are a jog you
    # walk. Every figure comes from the record, so there is no new threshold here to be
    # wrong about -- which is the condition WP-9.1 works under.
    # WIDENED IN WP-9.4, BECAUSE ITS ZERO WAS A SKIP AND NOT A PASS.
    #
    # The first version compared the threshold room's OWN two doors and gave up whenever they
    # sat on perpendicular walls, on the true observation that a position on an N or S wall
    # runs in x and one on an E or W wall runs in y. Measured over the 21 partis it fired
    # ZERO times: no_threshold 3, no_exterior_door 10, PERPENDICULAR-SKIPPED 7, compared 1,
    # fired 0. The seven it discarded are the case where you come in one way and leave the
    # porch another -- a worse jog than any offset the check could measure, and plausibly the
    # one on the sheet that raised Phase 9. A check that cannot fire reads as a check that
    # passed, which is the WP-8.6 finding wearing this package's own badge.
    #
    # The corpus decides the shape of the widened rule, and it is narrower than "a turn is
    # wrong". groupings/entry-sequence.json says a change of DIRECTION is a legitimate
    # threshold device in its own right ("Each step changes at least one condition: level,
    # enclosure, light, or direction"), and rooms/centre-passage.json records the Charleston
    # single house as a real exception -- a SIDE passage entered from the piazza, where
    # arriving on the flank is correct. So the rule binds exactly where
    # openings/grammar.json[op-passage-axis] says it binds: "Where a circulation room reaches
    # the boundary at BOTH ENDS, its two exterior doors sit on one axis, one at each end."
    # A passage with a through-axis must be entered ON that axis; a passage without one is
    # NOT JUDGED, and the census below says how many those were.
    def _reaches_outside(room, wall):
        """An opening on `wall` that gets you out of the house -- directly, or through a
        threshold room (a porch) that has its own placed exterior door."""
        for d in (room.get("doors") or []):
            if d.get("unplaced") or d.get("wall") != wall:
                continue
            if d.get("to") == "exterior":
                return d
            nb = rooms.get(d.get("to"))
            if nb and (C["rooms"].get(nb["type"]) or {}).get("function_class") == "threshold":
                if any(x.get("to") == "exterior" and not x.get("unplaced")
                       for x in (nb.get("doors") or [])):
                    return d
        return None

    axis_census = {"no_threshold_room": 0, "no_exterior_door": 0,
                   "entry_door_unplaced": 0,
                   "passage_has_no_through_axis": 0, "compared": 0, "found": 0}
    for rid, r in rooms.items():
        if (C["rooms"].get(r["type"]) or {}).get("function_class") != "threshold":
            continue
        if not placed.get(rid):
            continue
        ext = next((d for d in (r.get("doors") or [])
                    if d.get("to") == "exterior" and not d.get("unplaced")
                    and d.get("position_ft") is not None), None)
        if not ext:
            axis_census["no_exterior_door"] += 1
            continue
        # A SEVERED ENTRY IS NOT A SKIP EITHER, AND IT IS THE WORST OF THE THREE.
        # Measured while widening this check: on `centre-passage-double-pile` composed against
        # its own native style, the porch's door INTO THE PASSAGE comes back
        # `unplaced: the placement leaves these two rooms no shared wall`. You enter the
        # portico and there is no door from it into the passage at all -- to reach the passage
        # you walk back out and round to the rear door. The first census called that
        # "nothing to compare" and reported a zero, which is the same lie one layer down.
        for d in (r.get("doors") or []):
            t = d.get("to")
            if t == "exterior":
                continue
            nxt = rooms.get(t)
            if not nxt or (C["rooms"].get(nxt["type"]) or {}).get("function_class") != "circulation":
                continue
            if d.get("unplaced") or d.get("position_ft") is None:
                axis_census["entry_door_unplaced"] += 1
                _add("serious", "drawn",
                      f"The entrance sequence is severed: {r.get('name') or rid} has the front "
                      f"door but its opening into {nxt.get('name') or t} is not drawn — "
                      f"{(d.get('unplaced') or {}).get('reason', 'no position')}. You arrive "
                      f"and cannot get in the way the diagram says you do.",
                      room=rid, kind="drawn-entrance-severed",
                      fix="Place the threshold room against the circulation room it serves.")
                continue
            # Does the circulation room have a through-axis at all? Only then does the rule
            # bind, and only then can "on the axis" mean anything.
            through = None
            for a, b in (("N", "S"), ("E", "W")):
                if _reaches_outside(nxt, a) and _reaches_outside(nxt, b):
                    through = (a, b)
                    break
            if not through:
                axis_census["passage_has_no_through_axis"] += 1
                continue
            axis_census["compared"] += 1
            # The axis runs along x when the passage goes through N to S.
            axis_runs_x = through[0] in ("N", "S")
            if (ext.get("wall") in ("N", "S")) != axis_runs_x:
                # THE CASE THE OLD GUARD THREW AWAY. The front door is in a wall square to the
                # passage's own through-axis, so no offset exists to measure: you do not enter
                # the passage at its end, you enter its flank and turn.
                axis_census["found"] += 1
                _add("serious", "drawn",
                      f"The front door is in the {ext.get('wall')} wall while "
                      f"{nxt.get('name') or t} runs {through[0]} to {through[1]} — you arrive "
                      f"on its flank and turn, rather than at the end of its axis. "
                      f"rooms/entrance-hall.json: \"the hall is its front end, and the axis "
                      f"must continue to a rear opening\"; "
                      f"openings/grammar.json[op-passage-axis] binds because this passage "
                      f"does reach the boundary at both ends.",
                      room=rid, kind="drawn-entrance-off-axis",
                      fix="Bring the entrance onto the end of the passage, or accept a side "
                          "passage and say so in the record as the Charleston single house does.")
                continue
            off = abs(float(ext["position_ft"]) - float(d["position_ft"]))
            # Two openings overlap iff their centres are closer than the SUM OF THEIR
            # HALF-WIDTHS. The first draft compared against max(w1, w2), which is a
            # different quantity and is wrong in the direction that matters: on the sheet
            # that raised this package the front door sits 3.5 ft from the passage door and
            # both leaves are 3.5 ft, so the two openings are exactly edge to edge --
            # touching at a point, overlapping by nothing, no straight walk between them --
            # and `off > max(w)` let it through by a hair. There is still no authored
            # number here; the unit is the doors' own leaves.
            clear = (float(ext.get("width_ft") or 3.0) + float(d.get("width_ft") or 3.0)) / 2.0
            if off >= clear:
                axis_census["found"] += 1
                _add("serious", "drawn",
                      f"The front door is {off:.1f} ft off the axis of "
                      f"{nxt.get('name') or t} — the two openings do not overlap at all "
                      f"({clear:.1f} ft would just touch), so you enter the house and step "
                      f"sideways to reach the passage. rooms/entrance-hall.json: \"the hall "
                      f"is its front end, and the axis must continue to a rear opening\".",
                      room=rid, kind="drawn-entrance-off-axis", off_ft=round(off, 2),
                      clear_ft=round(clear, 2),
                      fix="Centre the entrance opening on the circulation room it serves.")

    # --- THE BOTTOM RISER AND THE FRONT DOOR (WP-9.1, op-stair-setback implemented at last)
    #
    # openings/grammar.json has carried this rule since WP-6.2 with a number, a basis naming
    # three records that agree, and a note explaining why nothing evaluated it: "Nothing
    # could evaluate it, because no plan record held a stair." A plan record has held a
    # stair since WP-6.2 -- the note went stale in the package that wrote it, and the rule
    # stayed unimplemented for three phases. The other three placement_rules are in
    # build/openings.py; this is the fourth.
    #
    # The 6.0 ft is the corpus's own, in three places: faults/stair-at-the-front-door.json's
    # test, kits/georgian-colonial-american.kit.json's stair_position, and
    # rooms/stair-hall.json's own prose. Read from the grammar so there is ONE spelling.
    st = plan.get("stair")
    if st and not st.get("unplaced") and st.get("flights"):
        setback_rule = None
        try:
            _g = json.load(open(f"{ROOT}/openings/grammar.json"))
            setback_rule = next((p for p in (_g.get("placement_rules") or [])
                                 if p.get("id") == "op-stair-setback"), None)
        except Exception:
            setback_rule = None
        front = None
        for rid, r in rooms.items():
            if not placed.get(rid):
                continue
            fc = (C["rooms"].get(r["type"]) or {}).get("function_class")
            if fc not in ("threshold", "circulation"):
                continue
            for d in (r.get("doors") or []):
                if d.get("to") == "exterior" and not d.get("unplaced") and d.get("wall"):
                    g = placed[rid]
                    # the face of the front door, as a point on the wall it sits in
                    if d["wall"] in ("N", "S"):
                        pt = (float(d.get("position_ft") or g["x_ft"]),
                              g["y_ft"] + (g["depth_ft"] if d["wall"] == "N" else 0.0))
                    else:
                        pt = (g["x_ft"] + (g["width_ft"] if d["wall"] == "E" else 0.0),
                              float(d.get("position_ft") or g["y_ft"]))
                    if front is None:
                        front = pt
        if front and setback_rule and setback_rule.get("min_setback_ft"):
            need = float(setback_rule["min_setback_ft"])
            fl = st["flights"][0]
            # the nearest point of the bottom flight to the front door
            fx0, fy0 = fl["x_ft"], fl["y_ft"]
            fx1, fy1 = fx0 + fl.get("width_ft", 3.0), fy0 + fl.get("depth_ft", 3.0)
            dx = max(fx0 - front[0], 0.0, front[0] - fx1)
            dy = max(fy0 - front[1], 0.0, front[1] - fy1)
            got = (dx * dx + dy * dy) ** 0.5
            out["first_riser_setback_ft"] = round(got, 2)
            if got + 1e-6 < need:
                _add("serious", "drawn",
                      f"The bottom riser stands {got:.1f} ft from the front door face; "
                      f"openings/grammar.json[op-stair-setback] asks for {need:g} ft. "
                      f"rooms/stair-hall.json: \"set back from the front door so the front "
                      f"door's swing and the bottom riser do not fight\".",
                      room=st.get("room"), kind="drawn-stair-setback",
                      need_ft=need, have_ft=round(got, 2),
                      fix="Move the stair back down its hall, or turn the bottom flight.")

    if not any((C["rooms"].get(r["type"]) or {}).get("function_class") == "threshold"
               for r in rooms.values()):
        axis_census["no_threshold_room"] = 1
    # PUBLISH THE CENSUS. The instrument reported 0 across 21 partis and the 0 was a skip;
    # a reader cannot tell a check that passed from one that never ran unless the checker
    # says which. This is the same discipline as `fault_not_applicable` -- the question did
    # not arise is a fourth state, not a pass.
    out["entrance_axis"] = axis_census

    # --- THE CENTRE LINE, THE BAY THE DOOR STANDS IN, AND THE MIRROR (WP-11.3)
    #
    # The block above asks whether the front door lines up with the passage it opens into.
    # This asks the questions one level out, which nothing has ever asked: is the "centre
    # passage" in the CENTRE, is the door in the middle BAY, is the front mirrored about the
    # axis, and does an upper opening stand over a lower one. `docs/reports/
    # tidewater-layout-diagnosis-2026-09-04.md` B1: the sheet's centre passage was the whole
    # WEST bay of a six-bay house, and the one executable rule the corpus has about a passage
    # -- its width as a share of the facade -- PASSED it at 11/60 = 0.183, because that rule
    # measures the passage's width and not its place.
    #
    # `build/axis.py` is the vocabulary and this is its only critic reader. It binds where the
    # DIAGRAM asks for a centre bay (`geometry.wants_a_centre_bay`, from the massing's own
    # stated bay count or the parti's circulation type), so a Charleston single house entered
    # sideways off a piazza is not judged by it -- that is the corpus's own exception, in
    # rooms/centre-passage.json, and it is why this does not simply fire on every plan.
    AX = _load("axis", f"{ROOT}/build/axis.py")
    GEOM = _load("geometry", f"{ROOT}/build/geometry.py")
    ax_census = {"wants_centre_bay": False, "spine": None, "door": None,
                 "mirror": None, "alignment": None}
    try:
        _parti = GEOM.parti_for(plan)
        _massing = (C.get("massings") or {}).get(plan.get("massing") or "") or {}
        _wants, _why = GEOM.wants_a_centre_bay(plan, _parti, _massing)
    except Exception:
        _wants, _why = False, None
    ax_census["wants_centre_bay"] = bool(_wants)
    ax_census["why"] = _why
    if _wants:
        sp = AX.spine(plan, 0, C)
        ax_census["spine"] = sp["verdict"]
        if sp["verdict"] == "off-centre":
            _add("serious", "drawn",
                 f'{sp["name"]} is drawn {sp["off_ft"]} ft off the footprint\'s own centre '
                 f'line, which is more than the {sp["tol_ft"]} ft this diagram allows — '
                 f'{_why}, and groupings/centre-passage-core.json says the passage "makes the '
                 f'facade symmetrical because the door is now genuinely in the middle". A '
                 f'passage that is not in the middle cannot do that.',
                 room=sp["room"], kind="drawn-passage-off-centre",
                 off_ft=sp["off_ft"], need_ft=sp["tol_ft"],
                 fix="Place the through-passage on the footprint's centre line; the period's "
                     "own off-centre passages (Westover, Wilton) move the ROOMS either side, "
                     "not the passage.")

        dr = AX.door_bay(plan)
        ax_census["door"] = dr["verdict"]
        if dr["verdict"] == "off-the-centre-bay":
            _add("serious", "drawn",
                 f'The front door stands in bay {dr["bay"] + 1} of {dr["bays"]}, not the '
                 f'middle bay ({dr["centre_bay"] + 1}). {_why}, and a centre-door front is '
                 f'the one move this type cannot do without: two windows either side of the '
                 f'door is what makes the elevation read.',
                 room=dr.get("room"), kind="drawn-door-off-the-centre-bay",
                 fix="Bring the entrance to the middle bay, or state a diagram that does not "
                     "put its door in the centre.")
        elif dr["verdict"] == "could-not-evaluate" and "even count" in (dr.get("why") or ""):
            # NOT a pass, and the loudest of the three states here: a house with an even bay
            # count has no middle bay for any door to stand in, so the question does not
            # arise -- because the answer was made impossible before the door was placed.
            _add("serious", "drawn",
                 f'This diagram wants a door in its middle bay and the front has '
                 f'{dr.get("bays")} bays, an EVEN count with no middle bay at all. {_why}. '
                 f'Nothing about the door can be judged: the placement removed the question.',
                 kind="drawn-no-centre-bay",
                 fix="An odd bay count. build/geometry.py grows by two on a diagram that wants "
                     "a centre bay; an even count here means the lot or the program forced it.")

        # SYMMETRY AND ALIGNMENT ARE JUDGED ONLY ON A COMPLETE FRONT, and that is a refusal
        # rather than a gap. A facade missing seven of its eleven declared units is not the
        # facade the record describes, and convicting it of asymmetry would charge the house
        # twice for one cause -- the undrawn windows are already a disclosure of their own
        # (WP-11.1). The census says how many plans went unjudged and why, so a check that
        # cannot fire cannot read as a check that passed (WP-8.6).
        mi = AX.mirror(plan, 0)
        al = AX.alignment(plan)
        incomplete = (mi.get("declared_but_unplaced") or 0)
        if mi["verdict"] == "could-not-evaluate" or incomplete:
            ax_census["mirror"] = "could-not-evaluate"
            _add("info", "drawn",
                 f'Facade symmetry could not be judged: {incomplete or "no"} declared window '
                 f'unit(s) on the entrance front were not drawn, so the drawn front is not the '
                 f'one the record describes. massings/catalog.json calls symmetry "a hard '
                 f'constraint, not a preference" and this is a refusal to judge it on an '
                 f'incomplete elevation, not a pass.',
                 kind="drawn-facade-symmetry-unjudged")
        else:
            ax_census["mirror"] = mi["verdict"]
            if mi["verdict"] == "not-mirrored":
                _add("serious", "drawn",
                     f'{len(mi["unmatched"])} of {mi["openings"]} opening(s) on the entrance '
                     f'front have no partner reflected about the centre line. '
                     f'massings/catalog.json: "Facade symmetry is a hard constraint, not a '
                     f'preference."',
                     kind="drawn-facade-unmirrored")
        if al["verdict"] == "could-not-evaluate" or incomplete:
            ax_census["alignment"] = "could-not-evaluate"
        else:
            ax_census["alignment"] = al["verdict"]
            if al["verdict"] == "not-aligned":
                _add("serious", "drawn",
                     f'{al["unaligned"]} upper opening(s) on the entrance front stand over no '
                     f'opening below. massings/catalog.json: "Window bays must align '
                     f'vertically; a misaligned upper window is a structural admission that '
                     f'the plan is not really Georgian."',
                     kind="drawn-windows-unaligned")
    out["axis"] = ax_census

    # THE FIRE IS **NOT** JUDGED HERE, AND THE FIRST DRAFT PUT IT HERE (WP-11.4). It reads a
    # room's authored `hearth`, the massing's `hearth` and the room type's `servicing.heat`, and
    # NOT ONE of those is a placement. Sitting in this layer it fell behind the early return at
    # the top of the function, so on an unplaced record it produced no finding, no census and no
    # reason -- a check that could not fire reading exactly like a check that passed, in the
    # package written to stop that. It runs in `check()` with the other declared-record layers;
    # `hearths.breast` and `hearths.stack_axes` DO read placement and are the renderer's and the
    # roof's, not this layer's. If a placed hearth check is ever wanted -- a breast overlapping a
    # door, a fixture, or the room's own furniture run -- it belongs here and this one stays
    # where it is.
    # ---- THE FACADE AS A RESULT (WP-11.7, oq/the-facade-is-a-result-not-an-input).
    #
    # It belongs in THIS layer and the reason is WP-11.4's rule -- ask what a check READS, not
    # what it is about. Every one of these reads the PLACEMENT: `front_openings` walks the placed
    # openings on the entrance front, `room_front_bays` reads each room's placed rectangle, and
    # the passage's share is measured off its placed width. The derived RHYTHM is a statement
    # about the record (`footprint.bays`), but nothing here judges it alone.
    #
    # AND EVERY FINDING IS A REPORT, NEVER AN INSTRUCTION. The ruling's own trap: "a derived
    # facade is a facade the generator can be WRONG about with confidence ... the window that
    # gets invented to complete a rhythm is this ruling's version of the invented measurement
    # OQ 52 swept out of the elevation." So an empty bay is stated as empty; a declared window
    # count is never overwritten with a derived one (WP-6.2's rule stands); and where the plan
    # names no parti -- FIFTEEN of the sixteen records in this tree -- the whole block is one
    # `info` naming the reason, which is not a pass.
    try:
        FA = _load("facade", f"{ROOT}/build/facade.py")
        fac = {"rhythm": FA.rhythm(plan, C)}
        if fac["rhythm"]["verdict"] != "derived":
            # `_add`, NEVER `F.add`. Every finding of this layer is a finding about a
            # placement and must carry the engine that produced it -- WP-9.1 set it once and
            # passed it through one wrapper "so no call site can omit it", and this call site
            # omitted it. `test_evaluate_matches_cli` caught it: a drawn finding with no engine
            # breaks the bench-versus-CLI parity that exists so a fatal appearing mid-drag does
            # not read as the house changing.
            _add("info", "drawn",
                 f'The front\'s bay rhythm could not be derived: {fac["rhythm"]["why"]} '
                 f'(oq/the-facade-is-a-result-not-an-input). Not a pass -- this house\'s '
                 f'facade is unjudged.', kind="facade-rhythm-unjudged")
        else:
            for lvl in sorted({(lv.get("index") or 0) for lv in plan.get("levels", [])}):
                cmp_ = FA.compare(plan, lvl, C)
                fac[f"level_{lvl}"] = {k: v for k, v in cmp_.items() if k != "findings"}
                for f_ in cmp_["findings"]:
                    # A bay with no opening is MINOR and the door off its centre bay is SERIOUS,
                    # and the split is the ruling's: the rhythm is a consequence to be reported,
                    # while the door standing somewhere other than the plan's own middle bay is
                    # the organising move itself not landing.
                    sev = "serious" if f_["kind"] == "front-door-off-the-centre-bay" else "minor"
                    _add(sev, "drawn", f_["statement"], room=f_.get("room"), kind=f_["kind"])
                rfb = FA.room_front_bays(plan, lvl, C)
                fac[f"level_{lvl}"]["front_rooms"] = len(rfb["rooms"])
                fac[f"level_{lvl}"]["window_count_disagreements"] = len(rfb["disagreements"])
                for d in rfb["disagreements"]:
                    _add("minor", "drawn",
                         f'{d["room"]} spans {len(d["bays"])} bay(s) of the front and declares '
                         f'{d["declares"]} window(s) there, where the rhythm the plan\'s own '
                         f'bays imply wants {d["wants"]}. REPORTED, not corrected: the declared '
                         f'count is the author\'s and is never overwritten (WP-6.2).',
                         room=d["room"], kind="front-window-count-against-the-bays")
            fac["share"] = FA.facade_share(plan, C)
        out["facade"] = fac
    except Exception as e:
        # Stated, never swallowed -- `roof.py` wrapped its own hearth reconciliation in a bare
        # `except: pass` and then asserted there was nothing to stand over (WP-11.4).
        out["facade"] = {"verdict": "could-not-evaluate",
                         "why": f"{type(e).__name__}: {e}"}
        _add("info", "drawn",
             f"The facade layer could not be read ({type(e).__name__}: {e}). Not a pass.",
             kind="facade-unreadable")

    out["unreachable_count"] = len(out["unreachable"])
    out["diverged_count"] = len(out["diverged"])
    return out


def check(plan, C=None, strict=False):
    C = C or load_corpus()
    core = _load("tdlcore", f"{ROOT}/mcp_server/core.py")
    # build/arrangement.py (WP-9.1) serves three layers below -- the grouping rules' own
    # variables, the fault namespace, and nothing in the drawn layer, which reads placement
    # directly. Loaded once here rather than per-layer: modcache returns the same module
    # either way, but three separate try/excepts hid which layer had lost it.
    try:
        ARR = _load("arrangement", f"{ROOT}/build/arrangement.py")
    except Exception:
        ARR = None
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
                      room=rid, rule=rt["dimensions"].get("critical_dimension"),
                      kind="area-below-band", need_sf=lo, have_sf=round(area, 1), band=[lo, hi], axis="area")
            elif area > hi * 1.25:
                F.add("minor", "room", f"{label} is {area:.0f} sf, well above the {lo}-{hi} sf band. Confirm it is not a room that has stopped being a room.",
                      room=rid, kind="area-above-band", have_sf=round(area, 1), band=[lo, hi], axis="area")
        if w and rt["dimensions"].get("width_ft"):
            lo, hi = rt["dimensions"]["width_ft"]
            if w < lo:
                F.add("serious", "room", f"{label} is {w} ft in its short dimension; below the {lo} ft floor for a {rt['name'].lower()}.",
                      room=rid, rule=rt["dimensions"].get("critical_dimension"),
                      kind="width-below-floor", need_ft=lo, have_ft=w, band=[lo, hi], axis="width")
        # ---- THE SHAPE OF THE ROOM, NOT ONLY ITS SIZE (WP-9.1).
        # Until this package the room layer read `area_sf` and the FLOOR of `width_ft`, and
        # nothing else. So a kitchen drawn 10 x 30 passed silently -- 300 sf sits inside the
        # 120-340 band and 10 ft is exactly the width floor -- while the record it was
        # measured against states `length_ft [12, 22]` and `proportion [1.05, 1.8]`, and a
        # kitchen at 3.0 is nearly twice as long as its own catalogue permits. 54 of the 60
        # room records declare a proportion band. Not one of them was read by anything.
        #
        # No new threshold is authored here: every figure quoted is the room record's own.
        # ONE DIRECTION ONLY, AND THE FIRST DRAFT OF THIS BLOCK IS WHY. It also charged a
        # room for being SQUARER than its band and WIDER than its band, and on the first
        # corpus run it convicted the plans this project holds up as good: an 18 x 18 dining
        # room, a living room 1.62 against a ceiling of 1.6, a 3 ft closet against a 2-2.33
        # band. No record in this corpus says a room may not be square -- the prose runs the
        # other way, and the complaint that raised this package was a room stretched into a
        # band, never one that was too nearly square. A check that convicts the reference
        # plans is miscalibrated, and the fix was to delete the direction the corpus does not
        # state rather than to loosen the one it does.
        #
        # Severity is the file's OWN two-tier convention for a figure that has drifted from
        # the one it should be (the drawn-divergence check below: 10% minor, 25% serious),
        # not a new tolerance. A room 1% over its band is a decision to defend; one 67% over
        # is the kitchen Lucas was sent.
        def _over(got, ceiling):
            return (got - ceiling) / ceiling if ceiling else 0.0

        if w and l and rt["dimensions"].get("length_ft"):
            llo, lhi = rt["dimensions"]["length_ft"]
            if l > lhi:
                F.add("serious" if _over(l, lhi) > 0.25 else "minor", "room",
                      f"{label} runs {l} ft; the catalogue band for a {rt['name'].lower()} is "
                      f"{llo}-{lhi} ft long. A room can hold its area and stop being the room.",
                      room=rid, rule=rt["dimensions"].get("critical_dimension"),
                      kind="length-above-band", have_ft=l, band=[llo, lhi], axis="length")
        if w and l and rt["dimensions"].get("proportion"):
            plo, phi = rt["dimensions"]["proportion"]
            ar = round(l / w, 2)
            if ar > phi:
                F.add("serious" if _over(ar, phi) > 0.25 else "minor", "room",
                      f"{label} is {w} x {l} ft — {ar} to 1, against the {plo}-{phi} band a "
                      f"{rt['name'].lower()} is drawn to. It has the area and not the shape.",
                      room=rid, rule=rt["dimensions"].get("critical_dimension"),
                      kind="proportion-above-band", have=ar, band=[plo, phi], axis="proportion")
        cmin = rt["dimensions"].get("ceiling_min_ft")
        ch = r.get("ceiling_ft") or next((lv.get("floor_to_ceiling_ft") for lv in plan["levels"]
                                          if any(x["id"] == rid for x in lv.get("rooms", []))), None)
        if cmin and ch and ch < cmin:
            F.add("serious", "room", f"{label} ceiling {ch} ft is under the {cmin} ft the room type wants.", room=rid,
                  kind="ceiling-below-min", need_ft=cmin, have_ft=ch, axis="ceiling")

        # ---- furniture fit: the check most plans have never had run on them
        for s_ in furniture_shortfalls(rt, w, l):
            if s_["axis"] == "short":
                F.add("serious", "furniture",
                      f"{label} cannot take its {s_['item']}: needs {s_['need_ft']:.1f} ft across ({s_['item_in']} in item + {s_['sides']} x {s_['clearance_in']} in clearance, {s_['placement']}), has {s_['have_ft']} ft.",
                      room=rid, rule=rt["dimensions"].get("critical_dimension"),
                      fix=f"Widen to {s_['need_ft']:.1f} ft, or accept that the room will not hold a {s_['item']}.",
                      # THE EVIDENCE CONTRACT (PR #19). The figure a move needs, UNROUNDED --
                      # compose.repair read `12.3` back out of this sentence for a room needing
                      # 12.333 and declared 12.3, and `12.3 > 12.3` was false, so the dining room
                      # never moved and the finding could never clear. Supplied from
                      # `furniture_shortfalls`, which is the ONE spelling of the arithmetic
                      # (WP-9.6) -- the two packages meet here and neither is dropped.
                      kind="furniture-fit", need_ft=round(s_["need_ft"], 3), have_ft=s_["have_ft"],
                      axis="width", item=s_["item"], sides=s_["sides"],
                      clearance_in=s_["clearance_in"], footprint_in=s_["footprint_in"])
            else:
                F.add("minor", "furniture",
                      f"{label} is tight along its length for its {s_['item']}: needs about {s_['need_ft']:.1f} ft, has {s_['have_ft']} ft.", room=rid,
                      kind="furniture-fit", need_ft=round(s_["need_ft"], 3),
                      have_ft=s_["have_ft"], axis="length", item=s_["item"])

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
                  room=rid, rule="rooms/%s.json daylight.depth_governs is false" % r["type"],
                  kind="depth-not-governed")
        if governs and wh and effective_depth and dm < 10 and reach and effective_depth > reach * 1.05:
            how = ("lit from both ends, so measured at half its length" if two_ended
                   else "cross-lit, so the reach is relaxed by half" if len(walls) >= 2
                   else "lit from one side")
            F.add("serious", "daylight",
                  f"{label} is {effective_depth:.0f} ft deep against a {wh} ft window head ({how}); useful daylight reaches about {reach:.1f} ft.",
                  room=rid, fix="Raise the head, light the far end from another side, or accept the back of the room as a service zone.",
                  kind="daylight-depth", depth_ft=round(effective_depth, 2), reach_ft=round(reach, 2),
                  # the head that WOULD reach the back of the room at this lighting -- what
                  # `raise-window-head` sets, and what it refuses when it is above the ceiling
                  need_head_ft=round(effective_depth / (dm * (1.5 if len(walls) >= 2 and not two_ended else 1.0)), 2),
                  window_head_ft=wh, ceiling_ft=ch, lit_walls=sorted(walls), two_ended=two_ended,
                  multiplier=dm, exterior_walls=list(r.get("exterior_walls") or []))
        want_sides = rt["daylight"].get("sides_lit") or 1
        lit_walls = {win.get("wall") for win in r.get("windows", []) if win.get("wall")}
        if r.get("windows") and len(lit_walls) < want_sides:
            F.add("minor", "daylight", f"{label} is lit from {len(lit_walls)} side(s); the room type wants {want_sides}.", room=rid,
                  kind="sides-lit", need=want_sides, have=len(lit_walls), lit_walls=sorted(lit_walls),
                  exterior_walls=list(r.get("exterior_walls") or []))
        if not r.get("windows") and rt["function_class"] in ("public", "living", "dining", "sleeping", "work"):
            F.add("serious", "daylight", f"{label} has no windows.", room=rid,
                  kind="no-window", exterior_walls=list(r.get("exterior_walls") or []))

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

    # ---- THE ASPECT, WHICH SIXTY RECORDS STATE AND NOTHING HAS EVER READ (WP-11.9)
    #
    # Part VI of the Tidewater diagnosis lists four compass rules the corpus states and cannot
    # execute -- the library's north, the kitchen's east, the drawing room's south and west, the
    # closet's north or east. Reading them found that all SIXTY room records answer the
    # orientation question and nothing in the tree read a single one; `build/compass.py` and the
    # authored `daylight.aspect` beside each sentence are that reading.
    #
    # THE LAYER IS CHOSEN BY WHAT IT READS (WP-11.4's rule). A window's `wall` is AUTHORED and a
    # door's is solver output, so this is a fact of the declared record and belongs here rather
    # than in the drawn layer -- which is also why it can speak on all sixteen plan records
    # instead of the two that carry a placement. Whether the placement could SEAT those windows
    # where the author put them is a different question and `drawn-window-off-the-placed-wall`
    # already answers it.
    #
    # PLAN-N IS TRUE-N UNLESS A BEARING SAYS OTHERWISE, ruled 5 Sep 2026, and the ruling's stated
    # cost is that the assumption is printed in every finding rather than merely held.
    _CMP = _load("compass", f"{ROOT}/build/compass.py")
    _north = _CMP.plan_north(plan)
    _assume = _CMP.assumption(_north)
    _aspect_census = {"satisfied": 0, "avoided": 0, "unwanted": 0,
                      "not_applicable": 0, "unstated": 0, "unjudged": 0, "no_record": 0}
    for rid, r in rooms.items():
        rt = C["rooms"].get(r["type"])
        if not rt:
            # A ROOM WITH NO CATALOGUE RECORD LEFT THE CENSUS ALTOGETHER (audit, 7 Sep 2026),
            # through the very door the comment eight lines below says this block refuses: the
            # `continue` shrank the denominator silently, so a plan carrying an unknown room
            # type printed a census one room short with nothing saying so. The unknown type is
            # separately fatal at the room layer, so this needs no second finding -- but it is
            # counted and named, because the census's whole job is that a reader can tell a
            # clear from a question nobody asked.
            _aspect_census["no_record"] += 1
            continue
        label = r.get("name") or rt["name"]
        v = _CMP.read((rt.get("daylight") or {}).get("aspect"), _CMP.lit_faces(r), _north)
        # KeyError rather than `.get(..., 0)` ON PURPOSE: a verdict `compass.read` grows and this
        # block does not know about would be counted into a key the message never prints, and a
        # room would vanish from its own census. Loud is the only safe direction here.
        _aspect_census[v["verdict"]] += 1
        if v["verdict"] == "unstated":
            F.add("info", "daylight",
                  f"{label}: rooms/{r['type']}.json states no daylight.aspect, so its orientation "
                  f"prose has not been read into tokens and this room's aspect is UNJUDGED. "
                  f"Not a pass.", room=rid, kind="aspect-unstated")
            continue
        if v["verdict"] in ("not_applicable", "unjudged"):
            continue
        # `strength: hard` HERE IS NOT `severity: hard` AT LINE 15, and the two mappings are
        # deliberate rather than an oversight (audit, 7 Sep 2026). `STRENGTH_SEV` maps a
        # GROUPING rule's severity, where hard means the diagram does not hold. A room record's
        # aspect strength is the force of a preference about light -- `rooms/larder.json`'s
        # "NORTH, and it is not a preference" is the strongest thing any of the sixty records
        # says, and a north larder is still a buildable house. Fatal would disqualify the
        # candidate outright in `compose.SEV_CREDIT`; WP-11.9 measured that serious and fatal
        # are unmoved on both shipped plans and that was the intent, not an accident.
        sev = "serious" if v.get("strength") == "hard" else "minor"
        tok = ", ".join(f"plan-{f} is {v['tokens'][f]}" for f in sorted(v.get("faces") or []))
        if v["verdict"] == "avoided":
            F.add(sev, "daylight",
                  f"{label} is glazed on an aspect its own record rules out: {tok}, and "
                  f"rooms/{r['type']}.json avoids {'/'.join(v['avoid'])} — \"{v['basis']}\" "
                  f"({v['strength']}). {_assume}",
                  room=rid, kind="room-on-an-aspect-its-record-avoids",
                  aspect_faces=sorted(v["faces"]), aspect_avoid=v["avoid"],
                  plan_north_stated=_north["stated"],
                  fix="Move the room to a wall the record admits, or move its glass to another "
                      "wall of the same room.")
        elif v["verdict"] == "unwanted":
            F.add(sev, "daylight",
                  f"{label} takes none of the light its record asks for: {tok}, and "
                  f"rooms/{r['type']}.json wants {'/'.join(v['prefer'])} — \"{v['basis']}\" "
                  f"({v['strength']}). {_assume}",
                  room=rid, kind="room-off-the-aspect-its-record-wants",
                  aspect_faces=sorted(v["faces"]), aspect_prefer=v["prefer"],
                  plan_north_stated=_north["stated"],
                  fix="Give the room a window on one of the walls the record names, or accept "
                      "the aspect and say so on the record.")
    # THE CENSUS IS THE DELIVERABLE AS MUCH AS THE FINDINGS ARE. Twenty-five of the sixty records
    # answer the orientation question with something that is not a compass, and a reader who sees
    # no aspect finding on a plan must be able to tell "clear" from "nothing was asked".
    #
    # IT FIRES WHENEVER ANY ROOM WAS READ, not only where something was unjudged. A first version
    # gated it on `unjudged or not_applicable`, which would have let a plan whose rooms were all
    # judged show two convictions and no denominator -- the reader cannot then tell three
    # satisfied from three never asked, which is the whole distinction this block exists to keep.
    # IT FIRES ON EVERY PLAN THAT HAS ROOMS AT ALL, gated on `rooms` and not on the census
    # total: gating on the total meant a plan whose every room was outside the catalogue -- the
    # census then all zeroes -- printed nothing, which is again "clear" and "nothing was asked"
    # wearing one face.
    if rooms:
        F.add("info", "daylight",
              f"Aspect: {_aspect_census['satisfied']} satisfied, "
              f"{_aspect_census['avoided'] + _aspect_census['unwanted']} against the record, "
              f"{_aspect_census['not_applicable']} room(s) whose record answers with something "
              f"that is not a compass, {_aspect_census['unjudged']} that could not be evaluated, "
              f"{_aspect_census['unstated']} unstated, "
              f"{_aspect_census['no_record']} whose type has no room record to read. {_assume}",
              kind="aspect-census")

    # ============================================================ GROUPING LAYER
    # The variables the groupings' own tests name. The placement is passed in where there is
    # one, because a handful of these rules (the passage against its facade, above all) are
    # only answerable once the house is drawn -- and this is a reading of the placement, not
    # a judgment of it: the finding it feeds is the GROUPING's rule, quoted, and the drawn
    # layer keeps its own separate job below.
    gvars = {}
    if ARR:
        try:
            _fp = plan.get("footprint") or {}
            _placed = {rid: r["geometry"] for rid, r in rooms.items() if r.get("geometry")}
            gvars = ARR.grouping_vars(
                plan, C,
                placed=_placed or None,
                footprint=((_fp.get("width_ft"), _fp.get("depth_ft")) if _fp.get("width_ft") else None))
        except Exception:
            gvars = {}
    for gid in plan.get("groupings", []):
        g = C["groupings"].get(gid)
        if not g:
            # rule=gid: without it the finding names no rule, and a consumer keyed by rule
            # (compose.py's canon axis) credits the grouping as clean while still counting it.
            F.add("serious", "grouping", f"Unknown grouping '{gid}'.", rule=gid,
                  kind="grouping-unknown", fix="Use an id from groupings/.")
            continue
        sv = next((v for v in g.get("style_variation", []) if v["style"] in chain), None)
        if sv and sv.get("present") is False:
            F.add("serious", "grouping", f"The plan declares {g['name']}, which {style} does not have: {sv['note']}", rule=gid,
                  kind="grouping-absent-in-style")
        for want in g["rooms"]:
            # satisfied_by(), not a raw membership test. Every other layer in this file asks
            # the substitution table whether something the plan HAS would answer the rule
            # (OQ 43); the grouping layer asked whether the exact type was present, and so
            # convicted a centre-passage plan of having no entrance hall — a serious finding,
            # on the top-ranked candidate of the shipped Georgian brief, produced by a table
            # this file already carries and already trusts everywhere else.
            if want["role"] in ("primary",) and not (satisfied_by(want["room"]) & types_present):
                F.add("serious", "grouping",
                      f"{g['name']} requires a {want['room'].replace('-', ' ')} and the plan has none.", rule=gid,
                      kind="grouping-room-missing")
        if plan.get("massing"):
            att = next((a for a in g["attaches_to"] if a["massing"] == plan["massing"]), None)
            if att and att.get("fit") == "forbidden":
                F.add("serious", "grouping",
                      f"{g['name']} is marked forbidden in a {plan['massing'].replace('-', ' ')}: {att.get('note','')}", rule=gid,
                      kind="grouping-forbidden-in-massing")
            elif not att:
                F.add("info", "grouping", f"{g['name']} has no recorded fit for massing '{plan['massing']}'.", rule=gid,
                      kind="grouping-massing-fit-unrecorded")
        span = g.get("privacy_span")
        if span:
            ranks = [C["rooms"][rooms[x]["type"]]["privacy_rank"] for x in rooms
                     if rooms[x]["type"] in {y["room"] for y in g["rooms"]} and rooms[x]["type"] in C["rooms"]]
            if ranks and (min(ranks) < span[0] or max(ranks) > span[1]):
                F.add("minor", "grouping",
                      f"{g['name']} spans privacy ranks {min(ranks)}-{max(ranks)}; the grouping is defined for {span[0]}-{span[1]}.", rule=gid,
                      kind="grouping-privacy-span")
        # THE RULES THAT CARRY A TEST WERE THE ONES BEING SKIPPED (WP-9.1).
        #
        # This loop read `if severity == "hard" and not ir.get("test")` and emitted an info
        # finding for each -- so a hard rule WITHOUT a machine test was handed to a human,
        # and a hard rule WITH one was passed over in silence by every layer of this
        # checker. Twenty-six of the eighty-four internal rules carry a test; nineteen of
        # those are hard; exactly two were evaluated anywhere in the tree, both in
        # build/roof.py for the ridge step-down. `centre-passage-core`'s own
        # "passage_width_ft / facade_width_ft between 0.18 and 0.27" -- the rule that says
        # a passage is a fifth to a quarter of the front -- had never been run on anything.
        #
        # Three states, like everything else here. A rule whose variables this house cannot
        # supply is UNJUDGED and says which name was missing; it is not a pass.
        for ir in g["internal_rules"]:
            hard = ir.get("severity") == "hard"
            test = ir.get("test")
            if not test:
                # A RULE THAT REPORTS IS NOT A RULE NOBODY EXECUTES, AND MUST NOT READ LIKE ONE.
                # `measures.reported_by` exists for exactly this (WP-11.7, when
                # `centre-passage-core`'s facade-share test became a report) and the schema's own
                # description says so -- and the first version of that change wired the field
                # nowhere, so the rule went SILENT in this layer: no evaluation, no unjudged note,
                # nothing. `test_arrangement.py::test_a_hard_grouping_rule_with_a_test_is_
                # evaluated_not_skipped` caught it, which is the guard doing its job on a rule
                # that had stopped being a rule.
                rep = (ir.get("measures") or {}).get("reported_by")
                if rep:
                    band = (ir.get("measures") or {}).get("advisory_band")
                    F.add("info", "grouping",
                          f"[{g['name']}] REPORTED, not required — {ir['statement']} "
                          + (f"Observed band {band[0]}–{band[1]}, advisory. " if band else "")
                          + f"Measured by {rep}.", rule=gid, kind="grouping-rule-reported")
                else:
                    # AND THE BRANCH USED TO READ `elif hard`, WHICH LEFT 28 OF 86 RULES SILENT
                    # (WP-11.9). 28 carry a test, 29 hard ones were handed to a human by name,
                    # one reports -- and the remaining 28, every `strong` and `preferred` rule in
                    # the corpus, emitted NOTHING: no evaluation, no note, no hand-off. A rule
                    # nobody executes and nobody is told about reads exactly like a rule that
                    # passed, which is the same defect `measures.reported_by` was added for one
                    # rule at a time. The severity is named because it is what a reader needs to
                    # know how hard to look.
                    F.add("info", "grouping",
                          f"[{g['name']}] check by hand ({ir.get('severity', 'strong')}, no "
                          f"machine test): {ir['statement']}", rule=gid,
                          kind="grouping-rule-by-hand")
                continue
            parsed = ARR.parse_rule_test(test) if ARR else None
            if not parsed:
                F.add("info", "grouping",
                      f"[{g['name']}] could not evaluate: this rule's test is not in a form "
                      f"the reader knows — \"{test}\". Checked by hand or not at all.", rule=gid,
                      kind="grouping-rule-unparsed")
                continue
            row = core._eval_test(parsed, gvars)
            if not row or row.get("status") == "need_measurements":
                miss = ", ".join((row or {}).get("missing") or ["?"])
                F.add("info", "grouping",
                      f"[{g['name']}] could not evaluate \"{test}\": this plan supplies no "
                      f"{miss}. Not a pass — the rule is unjudged.", rule=gid,
                      kind="grouping-rule-needs-measurements")
                continue
            if row.get("status") != "evaluated":
                F.add("info", "grouping",
                      f"[{g['name']}] could not evaluate \"{test}\": "
                      f"{row.get('detail') or row.get('status')}.", rule=gid,
                      kind="grouping-rule-unevaluable")
                continue
            if row.get("passes") is False:
                sev = "serious" if hard else "minor"
                F.add(sev, "grouping",
                      f"[{g['name']}] {ir['statement']} — measured {row.get('value')} "
                      f"against {row.get('required')}.", rule=gid, kind="grouping-rule-failed")

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

        # --- THE PASSAGE FLOOR THIS STYLE STATES, WHICH IS NOT THE CATALOGUE'S (WP-9.1)
        #
        # `rooms/centre-passage.json` bands the width at [6, 14] and it is right to: six to
        # seven feet is a northern vernacular passage that circulates, and the record says so
        # in as many words. A FORMAL centre-passage plan is a different rule, and this corpus
        # states it in three places nobody read together --
        #   faults/passage-that-is-a-corridor.json's test: at-least 8.0, whose own note says
        #     "8 ft for a formal centre-passage plan and 6 ft for a northern vernacular one";
        #   groupings/centre-passage-core.json: "Passage width 8 to 14 ft";
        #   and the style's OWN kit, which for tidewater-georgian resolves
        #     circulation_parti.parameters.passage_width_ft to a range of [10, 14].
        # The composer sized this brief's passage at 7.9 ft, under all three, and nothing said
        # so: the room layer read the catalogue's 6 and passed it.
        #
        # Read from the RESOLVED kit, never `C["kits"][style]` -- `oq/the-raw-kit-read`, the
        # trap WP-8.4 and WP-8.6 each found a live instance of. No new number is authored here;
        # the floor is whatever this style's own cascade states, and a style that states none
        # gets no finding.
        _cp = (kit.get("circulation_parti") or {})
        _band = ((_cp.get("parameters") or {}).get("passage_width_ft") or {}).get("range")
        _floor = _band[0] if isinstance(_band, list) and _band else None
        if _floor:
            for _rid, _r in rooms.items():
                if _r.get("type") not in ("centre-passage", "cross-passage"):
                    continue
                _w, _l = _r.get("width_ft"), _r.get("length_ft")
                if not (_w and _l):
                    continue
                _got = min(_w, _l)
                if _got + 1e-6 < _floor:
                    F.add("serious", "style",
                          f"{_r.get('name') or _rid} is {_got} ft wide; {style}'s own kit states "
                          f"a passage of {_band[0]}-{_band[1]} ft. A formal centre-passage plan "
                          f"is not bound by the catalogue's 6 ft vernacular floor — "
                          f"faults/passage-that-is-a-corridor.json calls anything under 8 ft a "
                          f"corridor, and this style asks for more.",
                          room=_rid, rule="circulation_parti",
                          fix=f"Widen the passage to {_floor} ft.",
                          # The evidence contract PR #19 introduced. `need_ft` is the STYLE's
                          # own floor read from the resolved cascade, not the catalogue's --
                          # the whole point of the finding -- and the move that answers it
                          # (`passage-to-the-styles-own-floor`) reads it from here rather than
                          # re-resolving the kit and risking a second, different answer.
                          kind="passage-below-style-floor", need_ft=_floor, have_ft=_got,
                          band=list(_band), axis="width")

        for slot_id, choice in (plan.get("declared") or {}).items():
            if slot_id not in C["slots"]:
                F.add("minor", "style", f"Declared slot '{slot_id}' is not in the ontology.", rule=slot_id,
                      kind="slot-not-in-ontology", slot=slot_id); continue
            rec = kit.get(slot_id) or {}
            # the ONE canonical variant the cascade delivers, if there is exactly one: what a
            # revision move may put in place of a forbidden declaration. Two canonicals, or
            # none, is a judgment and the field is None (WP-9.1).
            _canon = [v.get("id") for v in rec.get("variants", []) if v.get("status") == "canonical"]
            canonical = _canon[0] if len(_canon) == 1 else None
            if rec.get("binding") == "forbidden":
                F.add("serious", "style", f"{style} forbids the slot '{slot_id}' outright, and the plan declares '{choice}'.", rule=slot_id,
                      kind="slot-forbidden", slot=slot_id, variant=choice, canonical=None)
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
                          rule=slot_id, fix=v.get("note"),
                          kind="variant-forbidden", slot=slot_id, variant=chosen, canonical=canonical)
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
                    F.add("info", "style", f"Check by hand: {c['statement']}", rule=c.get("id") or f"{style}.{c['kind']}",
                          kind="constraint-unformalised", constraint=c.get("id"))
                continue
            r = core._eval_test(test, c_namespace)
            if not r or r["status"] != "evaluated":
                constraint_summary["unjudged"] += 1
                missing = r.get("missing") if r else None
                F.add("info", "style",
                      f"Cannot evaluate {c['id']} ({c['kind']}): {c['statement']}"
                      + (f" [needs {', '.join(missing)}]" if missing else ""),
                      rule=c["id"], kind="constraint-unjudged", constraint=c["id"], needs=missing or [])
                continue
            if r["passes"]:
                constraint_summary["clear"] += 1
            else:
                constraint_summary["present"] += 1
                sev = CONSTRAINT_SEV.get(c.get("severity", "hard"), "serious")
                units = f" {r['units']}" if r.get("units") else ""
                F.add(sev, "style",
                      f"{c['statement']} (measured {r['value']}{units}, required {r['required']}{units}).",
                      rule=c["id"], fix=test.get("note"),
                      kind="constraint-present", constraint=c["id"], expression=test.get("expression"),
                      value=r["value"], required=r["required"], direction=test.get("direction"),
                      threshold=test.get("threshold"), units=r.get("units"))
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
    # ONE BUILDING (WP-9.1). Until Phase 9 this called `build_elevation(plan)` with no
    # placement, so `structure.build_section` solved a FRESH heuristic placement of the
    # declared record inside the critic while the drawn layer below read the placement the
    # record carries -- two buildings in one verdict, the defect WP-6.4 fixed for the drawing
    # set (`corpus._placed`) and not here. When the record carries a placement, the section,
    # the roof and the elevation are derived from THAT placement: a solved record is a
    # `geometry_result` (it carries `footprint` and every room's `geometry`). When it carries
    # none, the fresh heuristic is what the elevation is derived from, and the record says so.
    #
    # And never silent. The old `except Exception: pass` turned an elevation that could not
    # be derived into an absence indistinguishable from a style outside the generator's
    # scope, or from a house with nothing to measure. Each is an `info` finding now -- could
    # not evaluate, never a pass -- and `elevation_summary` says which.
    placed_any = any(r.get("geometry") for r in rooms.values())
    elevation_summary = {"evaluated": False, "basis": None, "engine": None, "reason": None}
    try:
        EL = _load("elevation", f"{ROOT}/build/elevation.py")
        if placed_any:
            ST = _load("structure", f"{ROOT}/build/structure.py")
            section = ST.build_section(plan, geometry_result=plan)
            elev = EL.build_elevation(plan, section=section)
            engine = ((plan.get("geometry_report") or {}).get("solver") or {}).get("engine")
            elevation_summary.update(basis="placement", engine=engine)
        else:
            elev = EL.build_elevation(plan)
            elevation_summary.update(basis="declared", engine="heuristic")
        if "error" in elev:
            elevation_summary["reason"] = elev["error"]
            F.add("info", "fault", f"The elevation could not be derived: {elev['error']}",
                  rule="elevation-not-derived", kind="elevation-not-derived")
        elif elev.get("applicable") is False:
            elevation_summary["reason"] = "style outside the elevation generator's scope"
            F.add("info", "fault", f"The elevation generator does not cover '{style}': "
                  f"{(elev.get('note') or '')[:160]}",
                  rule="elevation-not-applicable", kind="elevation-not-applicable")
        else:
            elevation_summary["evaluated"] = True
            for k, v in elev.get("measurements", {}).items():
                # A None is the elevation layer saying it could not judge that quantity, and it
                # must not enter the measurements dict at all: a key present with a None value
                # is a measurement the fault evaluator will try to compare, and the only reason
                # that did not already produce nonsense is that it threw and was swallowed.
                # Absent is what "unjudged" looks like here (OQ 59).
                if v is None: continue
                meas.setdefault(k, v)
            F.add("info", "fault",
                  "Elevation measurements were derived from "
                  + ("the placement this record carries" + (f" ({elevation_summary['engine']})" if elevation_summary["engine"] else "")
                     if placed_any else
                     "a fresh heuristic placement of the declared record, which carries none")
                  + ".",
                  rule="elevation-basis", kind="elevation-basis",
                  elevation_basis=elevation_summary["basis"], engine=elevation_summary["engine"])
    except Exception as exc:
        elevation_summary["reason"] = f"{type(exc).__name__}: {exc}"
        F.add("info", "fault", f"The elevation could not be derived: {type(exc).__name__}: {exc}",
              rule="elevation-not-derived", kind="elevation-not-derived")
    # ARRANGEMENT LAYER (WP-9.1): build/arrangement.py::declared() folded in under the SAME
    # setdefault precedence as everything above it. Twenty-eight faults carry a test whose
    # `measurable_from` is `plan` -- the passage that is a corridor, the service route through
    # the formal plan, the room nobody enters -- and twenty-seven of them came back UNJUDGED on
    # this corpus's own most carefully authored plan, because nothing had ever supplied a single
    # plan-arrangement variable. The named-error corpus had the vocabulary and no measurement
    # layer underneath it.
    #
    # `declared()` is geometry-blind by construction and this layer must keep it that way: the
    # drawn half of the same module is folded in inside drawn_layer(), where OQ 54's ruling
    # permits reading a placement. A fault is evaluated in exactly ONE of the two.
    #
    # It sits AFTER the elevation block's own except handler rather than inside it, so that an
    # elevation that could not be derived does not also silence the arrangement measurements --
    # they share nothing but a measurements dict.
    #
    # AND NEVER SILENT, which this block was (audit, 7 Sep 2026). It carried a bare
    # `except Exception: pass` -- the construct the elevation block sixty lines above condemns
    # in as many words: "the old `except Exception: pass` turned an elevation that could not be
    # derived into an absence indistinguishable from a style outside the generator's scope."
    # The elevation block was rewritten to emit an `info` on every failure path and this one was
    # left as it was. It supplies the plan-arrangement variables that 28 faults read, so a throw
    # here turned 28 faults into unjudged-for-missing-measurements with nothing anywhere saying
    # the measurement layer had fallen over -- a real failure wearing the face of a corpus gap.
    try:
        for k, v in (ARR.declared(plan, C) if ARR else {}).items():
            if v is None: continue
            meas.setdefault(k, v)
    except Exception as exc:                      # noqa: BLE001 -- reported, never swallowed
        F.add("info", "plan",
              f"The plan-arrangement measurements could not be derived ({type(exc).__name__}: "
              f"{str(exc)[:160]}). Every fault reading one is UNJUDGED for want of a "
              f"measurement below, and the reason is this failure rather than a gap in the "
              f"record. Not a pass.", kind="arrangement-measurements-unavailable")
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
        # THE EVIDENCE CONTRACT (WP-9.1): which quantity failed, which names it reads, and
        # whether those names came from the plan's OWN `measurements` (a figure the record
        # states, and a revision move may move) or from the elevation generator (a figure
        # the generator derived, which is not the record's to overwrite -- and which may be
        # the generator's own constant, see build/critic_suspects.py).
        _expr = ev.get("expression") or ""
        _reads = sorted({n for n in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", _expr)
                         if n not in ("and", "or", "not", "min", "max", "abs", "round")})
        _declared_meas = plan.get("measurements") or {}
        F.add(x["severity"] if x["severity"] in SEV_ORDER else "serious", "fault",
              f"{x['name']}: {ev.get('value')} against {ev.get('required')}.",
              rule=x["fault"], fix=x.get("fix_cheap"),
              kind="fault-present", fault=x["fault"], expression=_expr, reads=_reads,
              value=ev.get("value"), required=ev.get("required"),
              fix_right=x.get("fix_right"), fix_cheap=x.get("fix_cheap"),
              exception=x.get("exception_applied") or x.get("exception_not_applied"),
              source=("declared" if _reads and all(n in _declared_meas for n in _reads) else "derived"))

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

    # --- THE FIRE (WP-11.4), a DECLARED-record layer
    #
    # `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` D1: there was no fireplace anywhere
    # in the plan layer, while `massings/catalog.json` said `hearth: gable-end-paired` and "Paired
    # end chimneys serve four fireplaces per floor" and `roof.py` drew the stacks. This reads what
    # the massing states and what the ROOM TYPE's own `servicing.heat` states, and reports where
    # they and the record disagree. It never infers a hearth: `rooms/bedchamber.json` says an
    # unheated chamber is historically normal and "should be said out loud rather than quietly
    # given a register", so a checker that demanded a fire wherever a type usually has one would
    # be inventing exactly what that sentence forbids.
    HE = _load("hearths", f"{ROOT}/build/hearths.py")
    hr = HE.hearth_report(plan, C)
    hearth_summary = {"massing": hr["massing_hearth"], "readable": hr["readable"],
                      "walls": hr["walls"], "census": hr["census"], "why": hr["why"]}
    for row in hr["rooms"]:
        if row["state"] == "absent":
            F.add("minor", "hearth",
                 f'{row["name"]} has no hearth in the record and rooms/{row["type"]}.json says '
                 f'this room has one: "{(row.get("quote") or "")[:120]}". The massing states '
                 f'{hr["massing_hearth"]!r}, so there is a stack for it to vent into.',
                 room=row["room"], kind="room-without-a-hearth",
                 fix="State the hearth on the room, or say in the record that this one is "
                     "unheated — the corpus asks for the choice to be made out loud.")
        elif row.get("off_the_stack_wall"):
            F.add("minor", "hearth",
                 f'{row["name"]} states a hearth on '
                 f'{"/".join(row["off_the_stack_wall"])} and this massing puts its stacks on '
                 f'{"/".join(hr["walls"] or [])}. Both may be right — rooms/dining-room.json '
                 f'puts the dining fire on "the interior wall opposite the sideboard" whatever '
                 f'the massing pairs — and the disagreement is reported rather than resolved.',
                 room=row["room"], kind="hearth-off-the-stack-wall")

    drawn = drawn_layer(plan, rooms, level_of, C, F)

    counts = {}
    for f in F.items: counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    return {"plan": plan["id"], "style": style, "rooms": len(rooms), "drawn_summary": drawn,
            # The hearth census is NOT under drawn_summary and that is deliberate: it reads the
            # authored record, the massing and the room type, never a placement, so it is
            # published beside the other declared-record summaries and is present on an unplaced
            # record. See the note where drawn_layer's fire block used to be.
            "hearth_summary": hearth_summary,
            "elevation_summary": elevation_summary,
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
