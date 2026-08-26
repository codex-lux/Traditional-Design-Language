#!/usr/bin/env python3
"""check_rooms.py - validate the room catalogue and the room-grouping catalogue.

Checks, in order:
  1. every rooms/*.json against schema/room.schema.json
  2. every groupings/*.json against schema/grouping.schema.json
  3. id matches filename, ids unique across the catalogue
  4. room-to-room adjacency references resolve (must_adjoin / should_adjoin /
     must_not_adjoin / entered_from), and grouping.rooms[].room references resolve
  5. massing ids resolve against massings/catalog.json
  6. slot ids resolve against elements/slots.json
  7. style ids resolve against styles/*.json
  8. fault ids resolve against faults/*.json
  9. privacy_rank sits in the band its function_class allows
 10. dimension sanity - area band consistent with width x length, proportion band
     consistent with width/length, daylight depth against the 2.25 rule
 11. coverage report by function_class

Unresolved references to rooms owned by another author are reported as WARN with
an explicit "not yet written" note rather than as an error, so the three room
authors can land files independently.

    python3 build/check_rooms.py            # everything
    python3 build/check_rooms.py --strict   # warnings become errors
    python3 build/check_rooms.py --only rooms/parlor.json rooms/hall.json
"""

import json
import os
import sys
import glob
import argparse
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# privacy_rank bands. 0 street, 1 threshold, 2 public, 3 family, 4 private, 5 intimate.
# Circulation is the wide one on purpose: circulation carries the rank of whatever
# it serves, so a front passage is 1-2 and an upstairs bedroom corridor is 4.
PRIVACY_BANDS = {
    "threshold":   (0, 2),
    "outdoor":     (0, 3),
    "circulation": (1, 4),
    "public":      (1, 3),
    "living":      (2, 4),
    "dining":      (2, 3),
    "service":     (2, 4),
    "work":        (2, 4),
    "storage":     (2, 5),
    "sanitary":    (2, 5),
    "sleeping":    (4, 5),
}

ADJ_KEYS = ("must_adjoin", "should_adjoin", "must_not_adjoin")

# Rooms assigned to other authors in this catalogue pass. Referencing one of these
# before its file lands is a WARN, not an ERROR.
EXPECTED_ELSEWHERE = {
    "kitchen", "scullery", "larder", "pantry", "laundry", "utility-room",
    "powder-room", "bathroom", "primary-bathroom", "wc", "bath-chamber",
    "primary-bedroom", "bedroom", "chamber", "guest-bedroom", "nursery",
    "dressing-room", "sleeping-porch", "attic", "cellar", "basement",
    "garage", "workshop", "home-office", "sewing-room", "servants-hall",
    "wine-cellar", "closet", "linen-closet", "boot-room", "dairy",
    "smokehouse", "springhouse", "summer-kitchen", "wash-house",
    "plant-room", "mechanical-room", "storeroom", "root-cellar",
    "great-chamber", "solar", "buttery", "cabinet", "garret",
    # --- added by the service/sanitary/sleeping/work-and-storage author -------
    # ids owned by the public/living/circulation author and by the groupings
    # author. Referencing one before its file lands is a WARN, not an ERROR.
    "parlor", "best-parlor", "dining-room", "living-room", "hall",
    "keeping-room", "great-room", "family-room", "den", "library", "study",
    "morning-room", "breakfast-room", "music-room", "drawing-room",
    "sitting-room", "sunroom", "conservatory", "porch", "piazza", "loggia",
    "veranda", "portico", "breezeway", "terrace", "dogtrot-passage",
    "mudroom", "landing", "back-stair", "service-stair",
    # ids owned by this author, listed so cross-references resolve while the
    # catalogue is landing file by file
    "butlers-pantry", "cold-room", "detached-kitchen", "bath-house", "privy",
    "water-closet", "garret-chamber", "walk-in-closet", "linen-press",
    "study-workroom", "woodshed", "bedchamber", "primary-bedroom",
    # outdoor and site rooms that the service catalogue has to point at
    "kitchen-garden", "service-yard", "pool-terrace", "garden", "drying-yard",
    "carriage-house", "smokehouse", "springhouse", "dairy", "icehouse",
}


# entered_from may name a circulation TYPE rather than a room id, and may name the
# outside. These are the legal non-room tokens.
CIRCULATION_TYPES = {
    "exterior", "street", "garden", "yard", "court", "courtyard", "drive",
    "passage", "corridor", "hall", "lobby", "landing", "gallery", "stair",
    "enfilade", "service-corridor", "any-circulation", "any-room",
    # A threshold or outdoor space is a legitimate thing to be entered from, and
    # for the service and sanitary rooms it is very often the ONLY legitimate
    # one - a privy, a woodshed, a summer kitchen and a pool bath are all
    # reached from outside on purpose.
    "porch", "piazza", "veranda", "gallery-porch", "breezeway", "portico",
    "loggia", "terrace", "dogtrot", "areaway", "bulkhead", "covered-way",
}

# Known naming collisions between concurrent authors, surfaced as WARN so they get
# reconciled rather than silently accepted. Left -> right is the catalogue id.
ALIAS_COLLISIONS = {
    "entry-hall": "entrance-hall",
    "front-hall": "entrance-hall",
    "foyer": "entrance-hall",
    "center-passage": "centre-passage",
    "living-hall": "hall",
    "parlour": "parlor",
    "sun-room": "sunroom",
    "mud-room": "mudroom",
    "butler-pantry": "butlers-pantry",
    "great-hall": "hall",
}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []

    def err(self, where, msg):
        self.errors.append((where, msg))

    def warn(self, where, msg):
        self.warnings.append((where, msg))

    def note(self, msg):
        self.notes.append(msg)


def build_universe():
    u = {}
    massings = load(os.path.join(ROOT, "massings", "catalog.json"))
    u["massings"] = {m["id"] for m in massings}

    slots = load(os.path.join(ROOT, "elements", "slots.json"))
    u["slots"] = {s["id"] for g in slots["groups"] for s in g["slots"]}

    u["styles"] = {
        os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json")))
    }
    u["faults"] = {
        os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(ROOT, "faults", "*.json")))
    }
    return u


def validate_schema(rep, kind, path, doc, validator):
    if validator is None:
        return
    for e in sorted(validator.iter_errors(doc), key=lambda x: list(x.path)):
        loc = "/".join(str(p) for p in e.path) or "<root>"
        rep.err(f"{kind}:{os.path.basename(path)}", f"schema at {loc}: {e.message}")


def check_room(rep, path, room, u, room_ids):
    where = f"room:{room['id']}"
    fname = os.path.basename(path)[:-5]
    if room["id"] != fname:
        rep.err(where, f"id '{room['id']}' does not match filename '{fname}.json'")

    fc = room["function_class"]
    pr = room["privacy_rank"]
    lo, hi = PRIVACY_BANDS.get(fc, (0, 5))
    if not (lo <= pr <= hi):
        rep.err(where, f"privacy_rank {pr} outside band {lo}-{hi} for function_class '{fc}'")

    # --- reference resolution -------------------------------------------------
    def ref_room(target, ctx):
        if target in room_ids:
            return
        if target in ALIAS_COLLISIONS:
            rep.warn(where, f"{ctx} -> '{target}' is an alias; the catalogue id is "
                            f"'{ALIAS_COLLISIONS[target]}' - reconcile")
            return
        if target in EXPECTED_ELSEWHERE:
            rep.warn(where, f"{ctx} -> '{target}' not yet written (expected from another author)")
        else:
            rep.err(where, f"{ctx} -> unresolved room id '{target}'")

    adj = room.get("adjacency", {})
    for key in ADJ_KEYS:
        for a in adj.get(key, []):
            ref_room(a["room"], f"adjacency.{key}")
            if a["room"] == room["id"]:
                rep.err(where, f"adjacency.{key} points at itself")
    for target in adj.get("entered_from", []):
        # entered_from may name a circulation *type* as well as a room id
        if target in room_ids or target in EXPECTED_ELSEWHERE:
            continue
        if target in ALIAS_COLLISIONS:
            rep.warn(where, f"adjacency.entered_from -> '{target}' is an alias; the "
                            f"catalogue id is '{ALIAS_COLLISIONS[target]}' - reconcile")
            continue
        if target in CIRCULATION_TYPES or target.startswith("type:"):
            continue
        rep.err(where, f"adjacency.entered_from -> unresolved '{target}'")

    for m in room.get("massing_fit", []):
        if m not in u["massings"]:
            rep.err(where, f"massing_fit -> unknown massing '{m}'")
    for s in room.get("slots", []):
        if s not in u["slots"]:
            rep.err(where, f"slots -> unknown slot '{s}'")
    for f in room.get("faults", []):
        if f not in u["faults"]:
            rep.err(where, f"faults -> unknown fault '{f}'")
    for sv in room.get("style_variation", []):
        if sv["style"] not in u["styles"]:
            rep.err(where, f"style_variation -> unknown style '{sv['style']}'")

    # --- dimension sanity -----------------------------------------------------
    d = room.get("dimensions", {})
    area, w, l, prop = d.get("area_sf"), d.get("width_ft"), d.get("length_ft"), d.get("proportion")
    for name, band in (("area_sf", area), ("width_ft", w), ("length_ft", l), ("proportion", prop)):
        if band and band[0] > band[1]:
            rep.err(where, f"dimensions.{name} band is inverted: {band}")
    if w and l:
        if w[0] > l[0] or w[1] > l[1]:
            rep.warn(where, f"width band {w} is not <= length band {l}")
        if area:
            lo_a, hi_a = w[0] * l[0], w[1] * l[1]
            if area[0] < lo_a * 0.6 or area[1] > hi_a * 1.6:
                rep.warn(where, f"area_sf {area} sits outside w x l ({lo_a:.0f}-{hi_a:.0f})")
        if prop:
            lo_p, hi_p = l[0] / w[1], l[1] / w[0]
            if prop[1] < lo_p * 0.75 or prop[0] > hi_p * 1.25:
                rep.warn(where, f"proportion {prop} inconsistent with w x l ({lo_p:.2f}-{hi_p:.2f})")

    # --- daylight -------------------------------------------------------------
    dl = room.get("daylight", {})
    dm = dl.get("depth_multiplier")
    if dm is not None:
        if dm == 0:
            pass  # a legitimately windowless room - closet, larder, interior WC
        elif not (1.0 <= dm <= 3.0):
            rep.err(where, f"daylight.depth_multiplier {dm} outside the defensible band 1.0-3.0")
        elif dm > 2.6:
            rep.warn(where, f"daylight.depth_multiplier {dm} above the room-vernacular pack ceiling of 2.6")
    ch = d.get("ceiling_min_ft")
    if ch and dm and w:
        head = ch * 0.78          # storey-graduation head-height factor
        reach = head * dm
        if w[1] > reach * 1.35:
            rep.warn(
                where,
                f"width band tops out at {w[1]} ft but single-sided daylight reaches "
                f"{reach:.1f} ft at a {ch} ft ceiling; confirm sides_lit > 1",
            )
    if dm and 0 < dm < 2.0 and "porch" not in json.dumps(dl).lower() \
            and "loggia" not in json.dumps(dl).lower() \
            and "gallery" not in json.dumps(dl).lower() \
            and "piazza" not in json.dumps(dl).lower() \
            and "eave" not in json.dumps(dl).lower() \
            and "shad" not in json.dumps(dl).lower() \
            and "borrow" not in json.dumps(dl).lower():
        rep.warn(where, f"depth_multiplier {dm} is below 2.0 but daylight.note gives no shading reason")

    # --- furniture ------------------------------------------------------------
    for f in room.get("furniture", []):
        fp = f["footprint_in"]
        if fp[0] <= 0 or fp[1] <= 0:
            rep.err(where, f"furniture '{f['item']}' has a non-positive footprint")
        if max(fp) > 240:
            rep.warn(where, f"furniture '{f['item']}' is over 20 ft long - check units are inches")
    if room["function_class"] in ("public", "living", "dining", "sleeping", "threshold") \
            and not room.get("furniture"):
        rep.warn(where, "no furniture list on an inhabited room - the furniture IS the constraint")
    if not d.get("critical_dimension"):
        rep.warn(where, "no dimensions.critical_dimension")


def check_grouping(rep, path, g, room_ids):
    where = f"grouping:{g['id']}"
    fname = os.path.basename(path)[:-5]
    if g["id"] != fname:
        rep.err(where, f"id '{g['id']}' does not match filename '{fname}.json'")
    seen = set()
    for r in g.get("rooms", []):
        rid = r["room"]
        if rid in seen:
            rep.err(where, f"room '{rid}' listed twice")
        seen.add(rid)
        if rid not in room_ids:
            if rid in EXPECTED_ELSEWHERE:
                rep.warn(where, f"rooms -> '{rid}' not yet written (expected from another author)")
            else:
                rep.err(where, f"rooms -> unresolved room id '{rid}'")


def check_cross_catalogue(rep, rooms):
    """Adjacency is directional but must_adjoin should not contradict must_not_adjoin."""
    by_id = {r["id"]: r for r in rooms}
    for r in rooms:
        adj = r.get("adjacency", {})
        pos = {a["room"] for k in ("must_adjoin", "should_adjoin") for a in adj.get(k, [])}
        neg = {a["room"] for a in adj.get("must_not_adjoin", [])}
        for t in pos & neg:
            rep.err(f"room:{r['id']}", f"'{t}' is both a positive and a negative adjacency")
        for t in neg:
            other = by_id.get(t)
            if not other:
                continue
            oadj = other.get("adjacency", {})
            opos = {a["room"] for k in ("must_adjoin", "should_adjoin") for a in oadj.get(k, [])}
            if r["id"] in opos:
                rep.err(
                    f"room:{r['id']}",
                    f"must_not_adjoin '{t}' but '{t}' claims it should adjoin this room",
                )
        # hard must_adjoin should be reciprocated or at least not contradicted
        for a in adj.get("must_adjoin", []):
            other = by_id.get(a["room"])
            if other and a.get("strength") == "hard":
                oadj = other.get("adjacency", {})
                back = {x["room"] for k in ADJ_KEYS for x in oadj.get(k, [])}
                back |= set(oadj.get("entered_from", []))
                if r["id"] not in back:
                    rep.warn(
                        f"room:{r['id']}",
                        f"hard must_adjoin '{a['room']}' is not mentioned back on that room",
                    )
        # a room may not be entered from a room more than one privacy rank below it
        for src in adj.get("entered_from", []):
            other = by_id.get(src)
            # A closet, a store or a WC takes the rank of whatever it opens off:
            # a coat closet in the entrance hall and a linen press on the landing
            # are correct, not gradient failures. The rule is meant to catch a
            # BEDROOM off a formal hall, so exempt non-through service volumes.
            exempt = (
                r["function_class"] in ("storage", "service", "sanitary")
                and adj.get("never_a_through_room") is True
            )
            if exempt:
                continue
            if other and r["privacy_rank"] - other["privacy_rank"] > 2:
                rep.warn(
                    f"room:{r['id']}",
                    f"entered_from '{src}' jumps {r['privacy_rank'] - other['privacy_rank']} "
                    f"privacy ranks - the gradient is being scrambled",
                )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="warnings are errors")
    ap.add_argument("--only", nargs="*", help="limit to these files")
    args = ap.parse_args()

    rep = Report()
    u = build_universe()

    try:
        from jsonschema import Draft202012Validator
        room_v = Draft202012Validator(load(os.path.join(ROOT, "schema", "room.schema.json")))
        grp_v = Draft202012Validator(load(os.path.join(ROOT, "schema", "grouping.schema.json")))
    except ImportError:
        rep.warn("<setup>", "jsonschema not installed - schema validation skipped")
        room_v = grp_v = None

    room_paths = sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json")))
    grp_paths = sorted(glob.glob(os.path.join(ROOT, "groupings", "*.json")))
    if args.only:
        keep = {os.path.abspath(p) for p in args.only}
        room_paths = [p for p in room_paths if p in keep]
        grp_paths = [p for p in grp_paths if p in keep]

    rooms, groupings = [], []
    for p in room_paths:
        try:
            doc = load(p)
        except Exception as e:
            rep.err(f"room:{os.path.basename(p)}", f"unparseable JSON: {e}")
            continue
        validate_schema(rep, "room", p, doc, room_v)
        rooms.append((p, doc))
    for p in grp_paths:
        try:
            doc = load(p)
        except Exception as e:
            rep.err(f"grouping:{os.path.basename(p)}", f"unparseable JSON: {e}")
            continue
        validate_schema(rep, "grouping", p, doc, grp_v)
        groupings.append((p, doc))

    # ids present across the WHOLE catalogue, not only the --only subset
    all_room_ids = {os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json")))}
    dupes = [k for k, v in Counter(d.get("id") for _, d in rooms).items() if v > 1]
    for dpe in dupes:
        rep.err("<catalogue>", f"duplicate room id '{dpe}'")

    for p, doc in rooms:
        if "id" in doc and "function_class" in doc and "privacy_rank" in doc:
            check_room(rep, p, doc, u, all_room_ids)
    for p, doc in groupings:
        if "id" in doc:
            check_grouping(rep, p, doc, all_room_ids)

    check_cross_catalogue(rep, [d for _, d in rooms if "id" in d and "privacy_rank" in d])

    # --- coverage -------------------------------------------------------------
    cov = defaultdict(list)
    for _, d in rooms:
        cov[d.get("function_class", "?")].append(d.get("id"))
    ranks = Counter(d.get("privacy_rank") for _, d in rooms)

    print(f"rooms: {len(rooms)}   groupings: {len(groupings)}")
    print("\ncoverage by function_class")
    for fc in sorted(PRIVACY_BANDS) + [k for k in cov if k not in PRIVACY_BANDS]:
        ids = cov.get(fc, [])
        flag = "" if ids else "   <- EMPTY"
        print(f"  {fc:<12} {len(ids):>3}  {' '.join(sorted(ids))}{flag}")
    print("\nprivacy_rank histogram")
    for r in range(6):
        print(f"  {r}  {'#' * ranks.get(r, 0)} ({ranks.get(r, 0)})")

    if rep.warnings:
        print(f"\nWARNINGS ({len(rep.warnings)})")
        for w, m in rep.warnings:
            print(f"  {w}: {m}")
    if rep.errors:
        print(f"\nERRORS ({len(rep.errors)})")
        for w, m in rep.errors:
            print(f"  {w}: {m}")

    bad = len(rep.errors) + (len(rep.warnings) if args.strict else 0)
    print(f"\n{'FAIL' if bad else 'OK'}  errors={len(rep.errors)} warnings={len(rep.warnings)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
