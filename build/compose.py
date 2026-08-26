#!/usr/bin/env python3
"""The composer. Template-seeded, validator-scored, and it returns several plans rather than one.

  read a brief -> pick partis native to the style -> instantiate at the target size
  -> repair against the validator until it stops improving -> emit N contrasting candidates

Objective: fewest fatal findings first, then style fidelity. Where the brief underdetermines
something the composer decides it and SAYS SO in the decision log rather than presenting the
choice as a fact. Judgment slots are surfaced, never silently resolved — a plan that violates
nothing can still be dead, and the human is the one who can tell.

  python3 build/compose.py briefs/<id>.json [--json] [--candidates 4]
"""
from __future__ import annotations
import json, os, glob, copy, math, argparse, importlib.util, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _mod(name, path):
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

PC = _mod("plan_check", f"{ROOT}/build/plan_check.py")
C = PC.load_corpus()
PARTIS = {}
for f in sorted(glob.glob(f"{ROOT}/partis/*.json")):
    p = json.load(open(f)); PARTIS[p["id"]] = p

SEV_W = {"fatal": 100, "serious": 8, "minor": 1, "advisory": 0.5, "info": 0}

# How many diagrams past `limit` a tie at the cut may add. Small on purpose — see
# pick_partis. Enough to keep a genuine near-tie whole; not enough to let a style whose
# fit function discriminated nothing double the composer's work.
MAX_TIE_EXPANSION = 3

# ---------------------------------------------------------------- selection
def pick_partis(brief, limit=12):
    style = brief["style"]
    chain = PC.style_chain(style, C)
    st = C["styles"].get(style, {})
    aff = {m["massing"]: m["affinity"] for m in st.get("massing_affinities", [])}
    beds = brief.get("bedrooms", 3)
    area = brief["target_area_sf"]
    out = []
    for p in PARTIS.values():
        if brief.get("massing") and p["massing"] != brief["massing"] and brief["massing"] not in p.get("alternate_massings", []):
            continue
        br = p.get("bedroom_range") or [1, 9]
        ar = p.get("area_range_sf") or [0, 99999]
        fit, why = 0.0, []
        if style in p["styles"]: fit += 3.0; why.append(f"native to {style}")
        elif set(p["styles"]) & chain: fit += 1.6; why.append("native to an ancestor or relative of the style")
        else: why.append("NOT native to this style — the composer is borrowing a diagram")
        # The affinity of the BEST massing this parti can be built on, not only its
        # primary. A parti reached through its alternate_massings is still that
        # style's canonical diagram -- 23 of the nodes WP-4.5 covers reach their
        # parti that way, and reading only p["massing"] gave them the nativity bonus
        # while withholding the canonical-massing one, so they still lost to a
        # lineage relative sitting on a canonical primary (1.6 + 2.0 > 3.0).
        RANK = {"canonical": 4, "common": 3, "acceptable": 2, "rare": 1, "forbidden": 0}
        cands = [aff.get(m) for m in ({p["massing"]} | set(p.get("alternate_massings") or []))]
        cands = [c for c in cands if c]
        a = max(cands, key=lambda c: RANK.get(c, 1)) if cands else None
        if a and "forbidden" in cands: a = "forbidden"   # a forbidden massing taints the pick
        if a == "canonical": fit += 2.0; why.append(f"{p['massing']} is a canonical massing for the style")
        elif a == "common": fit += 1.2; why.append(f"{p['massing']} is a common massing for the style")
        elif a == "forbidden": fit -= 4.0; why.append(f"the style marks {p['massing']} FORBIDDEN")
        elif a: fit += 0.3
        else: why.append(f"the style records no affinity for {p['massing']}")
        if br[0] <= beds <= br[1]: fit += 1.0
        else: fit -= 1.0 * min(2, abs(beds - (br[0] if beds < br[0] else br[1]))); why.append(f"{beds} bedrooms is outside the diagram's usual {br[0]}-{br[1]}")
        if ar[0] * 0.8 <= area <= ar[1] * 1.2: fit += 1.0
        else: fit -= 1.5; why.append(f"{area:.0f} sf is outside the diagram's range of {ar[0]:.0f}-{ar[1]:.0f}")
        gset = set(p.get("groupings", []))
        out.append({"parti": p["id"], "fit": round(fit, 2), "why": why, "groupings": sorted(gset)})

    # Tie-break by id so the order is the same on every machine. Without it the sort is
    # stable over PARTIS insertion order, which is directory order, which differs by
    # filesystem — and the cut below then kept different diagrams on different machines.
    out.sort(key=lambda x: (-x["fit"], x["parti"]))

    if limit <= 0:
        return []          # out[limit-1] would index from the END and return everything
    if len(out) <= limit:
        return out

    # Never cut THROUGH a narrow tie. Diagrams that fit equally well are, by this
    # function's own measure, indistinguishable; dropping some at an arbitrary index lets
    # the slice decide what the score is supposed to decide. For a Georgian family house
    # four diagrams tie at 2.00 and which one "wins" was previously settled by readdir.
    #
    # But the expansion is bounded, because a WIDE tie is a different thing. A style with
    # no native parti and no massing affinity — the majority of the corpus — leaves every
    # diagram on the same score, and returning all of them doubles compose time (each pick
    # is instantiated, repaired and plan-checked before the final cut) while adding no
    # information the fit function actually has. Past the margin, take the deterministic
    # cut: the id tie-break above means it is reproducible, not arbitrary-by-filesystem.
    edge = out[limit - 1]["fit"]
    above = [x for x in out if x["fit"] > edge]
    tied = [x for x in out if x["fit"] == edge]
    room = limit - len(above)
    if len(tied) - room <= MAX_TIE_EXPANSION:
        return above + tied
    return above + tied[:room]

# ---------------------------------------------------------------- instantiation
def room_default_dims(room_type):
    rt = C["rooms"].get(room_type)
    if not rt: return 10.0, 12.0
    lo, hi = rt["dimensions"]["area_sf"]
    a = (lo + hi) / 2.0
    pr = rt["dimensions"].get("proportion") or [1.2, 1.4]
    ratio = (pr[0] + pr[1]) / 2.0
    w = math.sqrt(a / ratio)
    return round(w, 1), round(w * ratio, 1)

def _as_feet(m):
    """A ceiling height in whatever unit the kit's author wrote it in.

    Kits state these in feet, in inches and (in the medieval British nodes) in millimetres.
    Anything that lands outside a plausible storey height after conversion is refused rather
    than guessed at, because a number this function cannot read is better dropped than turned
    into a ceiling nobody meant."""
    if m is None: return None
    if m > 200: m = m / 304.8          # millimetres
    elif m > 20: m = m / 12.0          # inches
    return m if 6.0 <= m <= 24.0 else None


def ceilings_for(style):
    """Ceiling heights from the style's own kit, falling back to a sensible default.

    Two passes, and the second one is WP-4.5's. The first reads storey-specific keys. The
    second accepts a generic one, because half the kits that trouble to state a ceiling height
    at all do not name a storey in the key: shotgun-house says `ceiling_height_min_ft`,
    norman-vernacular says `storey_height_range_ft`, swiss-chalet says
    `stube_ceiling_height_max`. Thirteen kits were read and thirteen were ignored, and the
    ignored ones silently got the 9.0 ft default — which is how a shotgun house, whose own kit
    specifies a 10 ft minimum and 11-12 ft preferred and whose whole character is a tall room
    on a small footprint, was composed with nine-foot ceilings and then failed its own style's
    transom-datum constraint at fatal. The style had spoken and nothing was listening."""
    kit = (C["kits"].get(style) or {}).get("slots", {})
    rec = kit.get("ceiling_height_rule") or {}
    params = (rec.get("parameters") or {})
    g = u = None
    generic = None
    for k, v in params.items():
        val = v.get("range") or ([v["value"]] if isinstance(v.get("value"), (int, float)) else None)
        if not val: continue
        m = _as_feet(sum(val) / len(val))
        if m is None: continue
        if "first" in k or "ground" in k or "principal" in k: g = g or m
        elif "second" in k or "upper" in k or "chamber" in k: u = u or m
        elif "ceiling" in k or "storey" in k or "story" in k:
            # prefer a stated preference over a stated minimum, which is what the kits mean
            if generic is None or "preferred" in k or "typical" in k: generic = m
    g = g or generic
    return (g or 9.0, u or (g or 9.0) - 1.0)

def instantiate(parti_id, brief):
    p = PARTIS[parti_id]
    beds = brief.get("bedrooms", 3)
    must = set(brief.get("must_have") or [])
    never = set(brief.get("must_not_have") or [])
    log = []
    rooms = []
    n_extra = max(0, beds - 1)                      # principal chamber is one of them
    for r in p["rooms"]:
        if r["type"] in never:
            log.append(f"Dropped {r.get('name') or r['id']}: the brief excludes {r['type']}."); continue
        if r.get("repeats_with_bedrooms"):
            for i in range(n_extra):
                q = copy.deepcopy(r); q["id"] = f"{r['id']}{i+1}"
                q["name"] = f"{r.get('name') or r['id']} {i+2}"
                q["doors"] = [(f"{d}{i+1}" if any(x["id"] == d and x.get("repeats_with_bedrooms") for x in p["rooms"]) else d)
                              for d in (r.get("doors") or [])]
                rooms.append(q)
            continue
        rooms.append(copy.deepcopy(r))
    # The garage is attached after the plan record exists, because it is placed by the
    # grouping's `attaches_to` against the chosen MASSING (WP-4.3) and the massing is not
    # settled until then. See attach_garage() below.
    for m in must:
        if not any(r["type"] == m for r in rooms):
            log.append(f"JUDGMENT: the brief requires a {m.replace('-', ' ')} and this diagram has no place for one. Not added — the position matters more than the presence.")

    # --- size everything, then scale to the target
    dims = {}
    for r in rooms:
        w, l = room_default_dims(r["type"])
        dims[r["id"]] = [w, l]
    target = brief["target_area_sf"]
    tol = brief.get("area_tolerance", 0.12)

    # Scale, then clamp each room to its own catalogue band, then rescale what is still free.
    # A global factor alone cannot reach a small house, because the catalogue midpoints are
    # generous; and an unclamped factor produces rooms below their own stated floor.
    def band(rid, rtype):
        rt = C["rooms"].get(rtype, {})
        lo, hi = (rt.get("dimensions", {}).get("area_sf") or [40, 900])
        return lo, hi
    # OQ 55: the brief's target is HEATED area, and a reserved void does not spend it.
    #
    # This loop used to scale every room in `dims` against the target, outdoor rooms included,
    # while reclaim() below measures area with outdoor rooms excluded -- so the two passes were
    # sizing against two different quantities and only one of them was the brief's. On a plan
    # with no placed void the difference was a rounding error and nobody saw it. On the
    # courtyard parti, whose court and four-range corredor are 40% of the block, it made a
    # 3,000 sf brief come back as an 1,834 sf house that the composer reported, correctly, as
    # 38.9% off its own target and could not fix, because from its point of view the area had
    # been spent. A void is now held out of the scaling entirely: it keeps the size its own
    # weight and catalogue give it, and the ranges around it are scaled to the brief.
    voids = {r["id"] for r in rooms
             if C["rooms"].get(r["type"], {}).get("function_class") == "outdoor"}

    # OQ 62, ruled 24 Aug 2026: `area_weight` is a SHARE OF THE BRIEF'S TARGET, and until now it
    # was read as a boolean -- "nudge this room 10% if it has a weight at all" -- after which one
    # global factor reached the target and the number itself decided nothing. So a parti's
    # weights read as a considered distribution and were not one, and tuning them (the courtyard
    # corredor, in the package before this) had to be done by measuring the output.
    #
    # PARTIAL COVERAGE IS ALLOWED, and is the normal case: only the ten partis WP-4.5 authored
    # carry weights at all, and their sums run from 0.35 to 1.13. A room WITH a weight takes that
    # share and is frozen -- a real share is not renegotiated by a global factor, which is the
    # whole of what the ruling changes. Rooms WITHOUT one split whatever is left by the loop
    # below, exactly as they did before, so the eleven partis that state no weights behave
    # identically to yesterday.
    #
    # A void's weight is a share of the same number, not of a gross the brief never states. The
    # court is 0.18 of the house the brief asked for; that the house also has a court is what
    # makes the block bigger than the brief (OQ 55), and sizing the court against the block would
    # be circular.
    frozen = set()
    clamped_up, clamped_down = [], []
    for r in rooms:
        w = r.get("area_weight")
        if not w: continue
        want = w * target
        lo, hi = band(r["id"], r["type"])
        if want < lo:
            clamped_down.append((r.get("name") or r["id"], want, lo)); want = lo
        elif want > hi:
            clamped_up.append((r.get("name") or r["id"], want, hi)); want = hi
        ratio = (dims[r["id"]][1] / dims[r["id"]][0]) if dims[r["id"]][0] else 1.3
        side = math.sqrt(want / ratio)
        dims[r["id"]] = [round(side, 1), round(side * ratio, 1)]
        frozen.add(r["id"])
    # A weight the room's own catalogue band cannot honour is the diagram and the brief
    # disagreeing, and it is the composer's job to say which -- not to split the difference
    # quietly and report a target it missed for reasons nobody can see. The area miss that
    # follows is then an explained number rather than a mysterious one.
    for label, rows, sense in (("larger", clamped_up, "than its catalogue band allows"),
                               ("smaller", clamped_down, "than its catalogue band allows")):
        if not rows: continue
        bits = ", ".join(f"{n} wants {a:.0f} sf, band gives {b:.0f}" for n, a, b in rows[:4])
        log.append(
            f"JUDGMENT: at a {target:.0f} sf target this diagram's own area weights make "
            f"{len(rows)} room(s) {label} {sense} — {bits}. Held at the band and the "
            f"difference left to the rooms the diagram does not weight. If the shortfall below "
            f"is large, the brief is asking this diagram for a house it does not grow into by "
            f"making its rooms bigger; it grows by having more of them.")
    for _ in range(4):
        total = sum(w * l for rid, (w, l) in dims.items() if rid not in voids)
        free = sum(dims[r][0] * dims[r][1] for r in dims if r not in frozen and r not in voids)
        fixed = total - free
        if free <= 0: break
        k = max(0.4, min(1.8, (target - fixed) / free)) ** 0.5
        for r in list(dims):
            if r in frozen or r in voids: continue
            w, l = dims[r][0] * k, dims[r][1] * k
            rtype = next(x["type"] for x in rooms if x["id"] == r)
            lo, hi = band(r, rtype)
            a = w * l
            if a < lo: f = math.sqrt(lo / a); w, l = w * f, l * f; frozen.add(r)
            elif a > hi: f = math.sqrt(hi / a); w, l = w * f, l * f; frozen.add(r)
            dims[r] = [round(w, 1), round(l, 1)]
        heated = sum(w * l for rid, (w, l) in dims.items() if rid not in voids)
        if abs(heated - target) / target <= tol: break

    # If it is still too big, drop optional rooms from the back — the diagram says which may go.
    dropped = []
    def area_now(): return sum(dims[r["id"]][0] * dims[r["id"]][1] for r in rooms
                               if r["id"] in dims and r["id"] not in voids)
    # A room that satisfies a HARD adjacency is not optional however the parti marked it.
    # Dropping the butler's pantry to save area severs the kitchen from the dining room.
    load_bearing = set()
    present_types = {r["type"] for r in rooms}
    for t in present_types:
        for rule in (C["rooms"].get(t, {}).get("adjacency", {}).get("must_adjoin") or []):
            if rule.get("strength", "strong") == "hard": load_bearing.add(rule["room"])
    optional = [r for r in reversed(rooms)
                if r.get("required") is False and r["type"] not in must and r["type"] not in load_bearing]
    for r in optional:
        if (area_now() - target) / target <= tol: break
        dims.pop(r["id"], None); dropped.append(r.get("name") or r["id"])
    if dropped:
        rooms = [r for r in rooms if r["id"] in dims]
        log.append(f"Dropped optional rooms to reach the area target: {', '.join(dropped)}. "
                   f"The diagram marks these as droppable; if any matters, say so in the brief and it will be kept.")
    final = area_now()
    log.append(f"Sized from the room catalogue and clamped each room to its own band; {final:.0f} sf against a {target:.0f} sf target"
               + (f", {abs(final-target)/target*100:.0f}% out — this diagram does not comfortably reach that size." if abs(final-target)/target > tol else "."))

    gc, uc = ceilings_for(brief["style"])
    log.append(f"Ceiling heights {gc:.1f} ft ground and {uc:.1f} ft above, taken from the style's own kit.")
    log += site_kit_log(brief["style"])

    levels = {}
    for r in rooms:
        lv = r["level"]
        levels.setdefault(lv, [])
        w, l = dims[r["id"]]
        ch = gc if lv == 0 else uc
        wh = round(ch - 1.2, 1)
        rec = {"id": r["id"], "type": r["type"], "name": r.get("name"),
               "width_ft": min(w, l), "length_ft": max(w, l), "ceiling_ft": round(ch, 1)}
        ext = r.get("exterior_walls") or []
        lit = r.get("lit_from") or ext
        if ext: rec["exterior_walls"] = ext
        if lit:
            rec["window_head_ft"] = wh
            rec["windows"] = [{"wall": wall, "width_ft": 3.2, "height_ft": round(wh - 2.4, 1),
                               "count": 2, "operable": True,
                               "egress": C["rooms"].get(r["type"], {}).get("function_class") == "sleeping"}
                              for wall in lit]
        if r.get("fixtures"): rec["fixtures"] = r["fixtures"]
        if r.get("stacks_over"): rec["stacks_over"] = r["stacks_over"]
        doors = [{"to": d} for d in (r.get("doors") or [])]
        if doors: rec["doors"] = doors
        levels[lv].append(rec)

    plan = {"id": f"{parti_id}-{brief.get('id','brief')}", "name": f"{p['name']} for {brief.get('name') or brief['style']}",
            "style": brief["style"], "massing": brief.get("massing") or p["massing"],
            "groupings": p.get("groupings", []),
            "context": brief.get("context", {}),
            "site": brief.get("site", {}),
            "levels": [{"id": {0: "ground", 1: "upper", -1: "cellar"}.get(lv, f"level{lv}"),
                        "index": lv, "floor_to_ceiling_ft": round(gc if lv == 0 else uc, 1),
                        "rooms": levels[lv]} for lv in sorted(levels)],
            "adjacencies": [a for a in p.get("adjacencies", [])
                            if any(a["a"] == x["id"] for x in rooms) and any(a["b"] == x["id"] for x in rooms)],
            "note": f"Composed from the {p['name']} parti. {p['trades_away']}"}
    attach_garage(plan, brief, log)
    symmetrise_doors(plan)
    plan["declared"] = canonical_choices(brief["style"])
    return plan, log, p

# --------------------------------------------------------------------- the garage
# WP-4.3. The garage is the one function no traditional style has a rule for, so it is the
# one room this composer AUTHORS a position for rather than retrieving one. The rule the
# plan of action asks for: it is placed by the `garage-and-hyphen` grouping's own
# `attaches_to` against the chosen massing, NEVER by adjacency. That distinction is the
# whole point. Placing by adjacency asks "what may the garage touch?", which is how the
# spec-builder Colonial ended up with a two-car garage against the primary bedroom -- every
# individual adjacency was locally plausible and the result is a code, noise and fume
# failure. Placing by attachment asks "where does a dependency land on this skeleton?", and
# the answer comes from the massing's own expansion logic, so the bedroom question never
# arises: the garage's only neighbour is the hyphen it arrived through.

# WHERE THE GARAGE LANDS, and why the hyphen is not a room.
#
# The first attempt here modelled the hyphen as its own room, typed `back-hall` and then
# `mudroom`. Both fail, and they fail for the same instructive reason: every service room
# in the catalogue that could plausibly BE a hyphen carries a hard `must_adjoin` on the
# kitchen (back-hall: "the back hall's entire reason for existing is to connect the kitchen
# to the rest of the house"; mudroom: "the groceries have to reach the kitchen without
# crossing a living space"). A 14 ft link out to a detached dependency cannot also touch
# the kitchen, so any hyphen modelled as one of those rooms is born failing a hard rule.
#
# The catalogue has no room type for a pure link, and inventing one here would be a room
# with no furniture, no daylight rule and no privacy rank -- WP-4.5's business, not this
# package's. So the hyphen is modelled as what it physically is: a property of the
# ATTACHMENT (its length is carried on the garage record and governed by the grouping's own
# 12-20 ft rule), not a room in the plan graph.
#
# That turns out to be what the corpus already said. rooms/back-hall.json states the modern
# sequence outright -- "garage, mudroom, back hall, kitchen, and the sequence is the same one
# the tradesman's entrance had" -- so the room the garage lands on is the MUDROOM, which is
# also exactly what rooms/garage.json's own must_adjoin requires by direct door. The garage
# then has precisely one interior neighbour, that neighbour is a threshold room, and the
# bedroom question cannot arise.
GARAGE_ANCHOR = "mudroom"

def attach_garage(plan, brief, log):
    """Attach garage-and-hyphen to the plan's massing, or refuse and say why."""
    bays = (brief.get("context") or {}).get("garage_bays")
    if not bays:
        return
    ground = next((lv for lv in plan["levels"] if lv.get("index") == 0), None)
    if ground is None:
        return
    if any(r["type"] == "garage" for lv in plan["levels"] for r in lv["rooms"]):
        return

    path = f"{ROOT}/groupings/garage-and-hyphen.json"
    if not os.path.exists(path):
        return
    G = json.load(open(path))
    massing = plan.get("massing")
    entry = next((a for a in G["attaches_to"] if a["massing"] == massing), None)

    if entry is None:
        log.append(f"JUDGMENT: the brief asks for {bays} garage bays and `garage-and-hyphen` "
                   f"records no attachment for the {massing} massing. Not placed — a garage put "
                   f"somewhere the grouping has no rule for is exactly the guess this package "
                   f"exists to stop.")
        return
    if entry.get("fit") == "forbidden":
        log.append(f"REFUSED: the brief asks for {bays} garage bays and `garage-and-hyphen` marks "
                   f"the {massing} massing FORBIDDEN — {entry.get('note', 'no flank and no lane')}. "
                   f"Not placed. The honest answer is a rear-lane detached structure that is not "
                   f"part of this house's composition, or a different massing.")
        return

    anchor = next((r for r in ground["rooms"] if r["type"] == GARAGE_ANCHOR), None)
    made_anchor = False
    if anchor is None:
        kitchen = next((r for r in ground["rooms"] if r["type"] == "kitchen"), None)
        if kitchen is None:
            log.append(f"JUDGMENT: the brief asks for {bays} garage bays and this diagram has "
                       f"neither a mudroom for the car to land in nor a kitchen to put one beside. "
                       f"Not placed — the alternative is dooring the garage into a formal room, "
                       f"which garage-and-hyphen forbids outright.")
            return
        # Doored onto the kitchen (its own hard rule) and, where the diagram has one, onto the
        # back hall as well -- which is not decoration. rooms/back-hall.json states the modern
        # sequence explicitly, "garage, mudroom, back hall, kitchen, and the sequence is the
        # same one the tradesman's entrance had", and it carries its own should_adjoin on the
        # mudroom. Adding a mudroom that the existing back hall cannot reach would satisfy the
        # garage's rule by breaking the back hall's.
        doors = [{"to": kitchen["id"], "width_ft": 3.0}]
        back = next((r for r in ground["rooms"] if r["type"] == "back-hall"), None)
        if back:
            doors.append({"to": back["id"], "width_ft": 3.0})
        anchor = {"id": "garage-mudroom", "type": "mudroom", "name": "Mudroom",
                  "width_ft": 7.0, "length_ft": 9.0, "ceiling_ft": 8.5,
                  "doors": doors,
                  "note": "Added with the garage. Without it the kitchen becomes the mudroom, "
                          "which is the failure rooms/garage.json names. Sits on the service "
                          "sequence the back hall's own record describes: garage, mudroom, "
                          "back hall, kitchen."}
        made_anchor = True

    w, l = room_default_dims("garage")
    bay_w = 11.0                                   # rooms/garage.json width band starts at 11
    width = round(max(w, bay_w * int(bays)), 1)
    # Clamp depth into the catalogue's own 20-26 ft band. The midpoint-derived figure runs
    # past it, and a garage deeper than it needs to be is the room that then fails its own
    # daylight rule -- a detached dependency has flanks to light from, so use them.
    lo_l, hi_l = (C["rooms"].get("garage", {}).get("dimensions", {}).get("length_ft") or [20, 26])
    l = lo_l   # the shallow end of the band: 20 ft takes a 16 ft car with clearance,
               # and every foot past that is depth the room cannot daylight
    hyphen_len = 14.0                              # inside the grouping's own 12-20 ft rule

    garage = {"id": "garage", "type": "garage", "name": f"{int(bays)}-Car Garage",
              "width_ft": width, "length_ft": round(l, 1), "ceiling_ft": 9.0,
              "exterior_walls": ["N", "E", "S"],
              # A window in the side wall, not a glazed vehicle door: rooms/garage.json is
              # explicit that "glazed garage doors are a contemporary convention with no
              # traditional precedent; where light is wanted, a window in the side wall costs
              # less and reads correctly." Kept inside the room's own 0-10% glazing band.
              "window_head_ft": 7.5,
              "windows": [{"wall": wall, "width_ft": 2.8, "height_ft": 3.6,
                           "count": 2, "operable": True, "egress": False}
                          for wall in ("E", "N")],
              "doors": [{"to": anchor["id"], "width_ft": 3.0}]
                       + [{"to": "exterior", "width_ft": 9.0, "type": "garage",
                           "note": "Turned off the principal elevation; two 9 ft openings with a "
                                   "pier between them rather than one wide door."}
                          for _ in range(int(bays))],
              "note": (f"Placed as a dependency on the {massing} massing "
                       f"({entry.get('position', 'per garage-and-hyphen.attaches_to')}), not by adjacency. "
                       f"Linked back by a {hyphen_len:g} ft hyphen — inside garage-and-hyphen's own "
                       f"12-20 ft rule; the link is a property of the attachment, not a room, because "
                       f"every service room that could model it hard-requires a kitchen door it cannot "
                       f"have. Ridge 60-80% of the main ridge, per the same grouping. Authored, not "
                       f"retrieved — no traditional style has a rule for this room.")}
    if made_anchor:
        ground["rooms"].append(anchor)
    ground["rooms"].append(garage)

    plan.setdefault("groupings", [])
    if "garage-and-hyphen" not in plan["groupings"]:
        plan["groupings"].append("garage-and-hyphen")

    log.append(f"AUTHORED: {int(bays)} garage bays placed as a dependency off the "
               f"{anchor.get('name') or anchor['type']}"
               f"{' (added with it)' if made_anchor else ''}, per garage-and-hyphen.attaches_to for the "
               f"{massing} massing ({entry.get('fit', 'possible')} fit: {entry.get('position', 'unspecified position')}). "
               f"Placed by attachment, never by adjacency — the garage's only interior neighbour is "
               f"that one threshold room, which is why it cannot land against a bedroom. Linked back "
               f"by a {hyphen_len:g} ft hyphen. No traditional style has a rule for this room; this is "
               f"invented and should be shown to a client as such.")
    if any(lv.get("index", 0) > 0 for lv in plan["levels"]):
        log.append("NOT SOLVED: whether an upper-storey room ends up over the garage is a geometry "
                   "question this composer does not answer — it places rooms, not volumes. "
                   "garage-and-hyphen forbids a habitable room above the bays; check the placed plan.")
    log.append("KNOWN FINDING, not a defect: the garage will report a daylight-depth failure. Two "
               "bays are 20 ft by 22 ft at the shallow end of the catalogue's own band, and no real "
               "two-car garage is shallow enough for daylight to reach its back wall — the finding "
               "is unsatisfiable rather than wrong, and the room is not distorted to silence it. "
               "Daylight depth is a habitability rule and the garage is not habitable. Recorded as "
               "OQ 31 rather than suppressed.")

def symmetrise_doors(plan):
    """A parti declares each door once; a plan needs it on both rooms."""
    idx = {r["id"]: r for lv in plan["levels"] for r in lv["rooms"]}
    for r in list(idx.values()):
        for d in list(r.get("doors") or []):
            t = d["to"]
            if t == "exterior" or t not in idx: continue
            o = idx[t]
            if not any(x["to"] == r["id"] for x in (o.get("doors") or [])):
                o.setdefault("doors", []).append({"to": r["id"]})
    for r in idx.values():
        r["doors"] = [d for d in (r.get("doors") or []) if d["to"] == "exterior" or d["to"] in idx]
        if not r["doors"]: r.pop("doors")

def site_kit_log(style):
    """WP-2.4: 'consume the seven site-and-settlement slots where a kit specifies them.'
    Five of the seven (street_relationship, outbuilding_types, fence_wall, landscape_idiom,
    grade_relationship) are `binding: specified` with a single canonical variant wherever a
    style's kit gives one, and canonical_choices() already folds those into plan['declared']
    — that mechanism is generic across every slot group, not site-specific, and predates this
    package. The other two are not variant-shaped: orientation_rule is `parameters`-only
    editorial prose (a chimney axis, a passage axis — not a value compose.py's own room
    placement reads yet, so it is surfaced, not silently acted on), and setback_rule is
    deliberately `binding: open` on the one style that specifies anything about it at all
    (georgian-colonial-american's own note calls it 'the cleanest open in the kit' — the same
    style is sited on the street line in Annapolis and at the end of a half-mile approach at
    Westover). Both would otherwise vanish with no record the kit was even asked."""
    kit = (C["kits"].get(style) or {}).get("slots") or {}
    log = []
    rec = kit.get("orientation_rule")
    if rec and rec.get("parameters"):
        bits = [f"{k.replace('_', ' ')}: {v.get('value')}" for k, v in rec["parameters"].items() if v.get("value")]
        if bits:
            log.append(f"Kit's orientation_rule ({style}): " + "; ".join(bits) + ". Editorial, not yet computed into the plan's own orientation.")
    rec = kit.get("setback_rule")
    # binding: open + status: empty is just an untouched slot (every style's kit has one until
    # authored) -- only a status past "empty" means a style deliberately drafted reasoning for
    # leaving it open, which is the case worth surfacing.
    if rec and rec.get("binding") == "open" and rec.get("status") not in (None, "empty"):
        log.append(f"Kit leaves setback_rule open for {style}"
                    + (f": {rec['note'][:160]}" if rec.get("note") else "")
                    + " — a settlement-pattern decision, not a style rule. The brief's own site.setback_front_ft/setback_side_ft govern, not the kit.")
    return log

def canonical_choices(style):
    kit = (C["kits"].get(style) or {}).get("slots", {})
    out = {}
    for sid, rec in kit.items():
        if rec.get("binding") != "specified": continue
        can = [v["id"] for v in rec.get("variants", []) if v.get("status") == "canonical"]
        if len(can) == 1: out[sid] = can[0]
    return out

# ---------------------------------------------------------------- repair
def _summarise(lines):
    widened = [l for l in lines if l.startswith("Widened")]
    other = [l for l in lines if not l.startswith("Widened")]
    if len(widened) > 4:
        names = sorted({l.split("Widened ")[1].split(" from")[0].split(" to the")[0] for l in widened})
        other.insert(0, f"Widened {len(widened)} rooms to take their furniture or reach their room type's floor: "
                        + ", ".join(names[:12]) + ("…" if len(names) > 12 else "") + ".")
    else: other = widened + other
    return other

def score(res):
    s = sum(SEV_W.get(f["severity"], 0) for f in res["findings"])
    return s

def repair(plan, rounds=6):
    """Hill-climb: read the findings and apply the move each one implies."""
    log, best = [], PC.check(plan, C)
    for _ in range(rounds):
        idx = {r["id"]: r for lv in plan["levels"] for r in lv["rooms"]}
        moved = False
        for f in best["findings"]:
            rid = f.get("room")
            if rid not in idx: continue
            r = idx[rid]
            if f["layer"] == "furniture" and "needs" in f["statement"]:
                try: need = float(f["statement"].split("needs ")[1].split(" ft")[0])
                except Exception: continue
                if need > r.get("width_ft", 0) and need < r.get("width_ft", 0) * 1.8:
                    log.append(f"Widened {r.get('name') or rid} from {r['width_ft']} to {need:.1f} ft so it takes its furniture.")
                    r["width_ft"] = round(need + 0.2, 1); moved = True
            elif f["layer"] == "daylight" and "window head" in f["statement"]:
                ch = r.get("ceiling_ft") or 9
                if r.get("window_head_ft", 0) < ch - 0.7:
                    r["window_head_ft"] = round(ch - 0.6, 1)
                    log.append(f"Raised the window head in {r.get('name') or rid} to {r['window_head_ft']} ft to reach the back of the room.")
                    moved = True
                elif r.get("length_ft", 0) > r.get("width_ft", 0) * 1.15:
                    r["length_ft"] = round(r["length_ft"] * 0.92, 1)
                    log.append(f"Shortened {r.get('name') or rid} to {r['length_ft']} ft; the room was deeper than its light could reach.")
                    moved = True
            elif f["layer"] == "room" and "short dimension" in f["statement"]:
                rt = C["rooms"].get(r["type"], {})
                lo = (rt.get("dimensions", {}).get("width_ft") or [r.get("width_ft", 10)])[0]
                if r.get("width_ft", 0) < lo:
                    r["width_ft"] = lo
                    log.append(f"Widened {r.get('name') or rid} to the {lo} ft floor for its room type."); moved = True
        if not moved: break
        cand = PC.check(plan, C)
        if score(cand) < score(best): best = cand
        else: best = cand; break
    return best, log

def reclaim(plan, target, tol, res):
    """Repair widens rooms to clear findings and overshoots the area. Give the area back from
    rooms that are not complaining, shortening length rather than width — width is what the
    furniture and daylight checks care about."""
    idx = {r["id"]: r for lv in plan["levels"] for r in lv["rooms"]}
    flagged = {f.get("room") for f in res["findings"] if f["severity"] in ("fatal", "serious")}
    def area():
        return sum(r.get("width_ft", 0) * r.get("length_ft", 0) for r in idx.values()
                   if C["rooms"].get(r["type"], {}).get("function_class") != "outdoor")
    log = []
    for _ in range(4):
        over = area() - target
        if over / target <= tol: break
        free = [r for rid, r in idx.items() if rid not in flagged
                and r.get("length_ft", 0) > r.get("width_ft", 0) * 1.05]
        if not free: break
        pool = sum(r["width_ft"] * r["length_ft"] for r in free)
        if pool <= 0: break
        f = max(0.85, 1 - min(over, pool * 0.25) / pool)
        for r in free:
            lo = (C["rooms"].get(r["type"], {}).get("dimensions", {}).get("area_sf") or [40])[0]
            newl = max(r["width_ft"] * 1.02, round(r["length_ft"] * f, 1))
            if r["width_ft"] * newl >= lo: r["length_ft"] = newl
        log.append(f"Shortened {len(free)} rooms that were not complaining, to give back {over:.0f} sf the repair pass had taken.")
        res = PC.check(plan, C)
    return res, log

# ---------------------------------------------------------------- footprint
def lot_usable_width_ft(plan):
    """WP-2.4: the width a parti's bays actually have to fit inside -- lot_width_ft (from
    `site`, falling back to the older `context` location) less both side setbacks. Returns
    None when the plan states no lot width at all, which means 'unconstrained,' not zero."""
    site = plan.get("site") or {}
    ctx = plan.get("context") or {}
    lot_width = site.get("lot_width_ft")
    if lot_width is None: lot_width = ctx.get("lot_width_ft")
    if lot_width is None: return None
    side = site.get("setback_side_ft") or 0
    return max(0.0, lot_width - 2 * side)

def footprint(plan, parti):
    lv0 = next((l for l in plan["levels"] if l.get("index") == 0), plan["levels"][0])
    a0 = sum(r.get("width_ft", 0) * r.get("length_ft", 0) for r in lv0["rooms"]
             if C["rooms"].get(r["type"], {}).get("function_class") != "outdoor")
    bm = (parti.get("scaling") or {}).get("bay_module_ft") or 10
    mx = (parti.get("scaling") or {}).get("max_bay_count") or 5
    # The floor a diagram cannot go below. Three is right for almost everything and is the
    # default, but a one-room hall house is 250-500 sf and one or two bays wide by its own
    # catalogue entry; floored at three it was not merely inflated, it was declared
    # lot-infeasible and DROPPED. geometry.py has always used a floor of 2 here, so the two
    # engines disagreed; the parti now says which it means. (WP-4.5)
    mn = (parti.get("scaling") or {}).get("min_bay_count") or 3
    notes = []
    # WP-2.4: a lot caps how many bays this diagram may ever reach here, regardless of what
    # the parti's own catalogue maximum allows -- "a 24 ft town-house parti for a 30 ft lot;
    # not a five-bay Georgian on a 40 ft lot" (PLAN-OF-ACTION.md, WP-2.4).
    usable = lot_usable_width_ft(plan)
    lot_infeasible = False
    if usable is not None:
        lot_mx = max(1, int(usable // bm))
        if lot_mx < mx:
            notes.append(f"Lot caps this diagram at {lot_mx} bays instead of its usual {mx}: "
                          f"{usable:.0f} ft usable width ({bm:.0f} ft bays) after side setbacks.")
        mx = min(mx, lot_mx)
        if lot_mx < mn:
            lot_infeasible = True
            notes.append(f"This diagram needs at least {mn} bays ({mn*bm:.0f} ft) and the lot clears only "
                          f"{usable:.0f} ft usable width after side setbacks. It does not fit this lot.")
    bays = max(mn, min(mx, round(math.sqrt(a0 * 1.6) / bm)))
    width = round(bays * bm, 1)
    depth = round(a0 / width, 1) if width else 0
    if depth > 38: notes.append(f"Footprint {width} x {depth} ft — deeper than about 38 ft, which needs a double-pile section and will leave interior rooms unlit.")
    if bays >= mx and a0 / (bays * bm) > 34: notes.append(f"At {bays} bays this diagram is at the width it grows to; further area wants a dependency, not more room.")
    return {"level_0_area_sf": round(a0), "bays": bays, "bay_module_ft": bm,
            "footprint_ft": [width, depth], "notes": notes, "lot_infeasible": lot_infeasible}

# ---------------------------------------------------------------- compose
def compose(brief, candidates=4, on_candidate=None):
    # on_candidate: optional callable invoked once per completed (kept) candidate with its
    # summary dict, plan excluded. Added for the workbench's compose progress stream;
    # None leaves behaviour identical and the CLI never passes it.
    #
    # The window is max(candidates + 4, 12), widened by WP-4.5 when the parti catalogue
    # reached the twenties: at +2 a new parti could evict an existing one merely by tying
    # with it, and 6 searched a twentieth of the catalogue. Kept over main's +2/6 at the
    # 25 Aug merge because the catalogue it was sized for is the one on this branch.
    picks = pick_partis(brief, limit=max(candidates + 4, 12))
    out, dropped_lot = [], []
    for pick in picks:
        plan, log, parti = instantiate(pick["parti"], brief)
        res, rlog = repair(plan)
        res, clog = reclaim(plan, brief["target_area_sf"], brief.get("area_tolerance", 0.12), res)
        rlog += clog
        area = sum(r.get("width_ft", 0) * r.get("length_ft", 0)
                   for lv in plan["levels"] for r in lv["rooms"]
                   if C["rooms"].get(r["type"], {}).get("function_class") != "outdoor")
        tol = brief.get("area_tolerance", 0.12)
        miss = abs(area - brief["target_area_sf"]) / brief["target_area_sf"]
        counts = res["counts"]
        # NATIVITY_W: what a native diagram is worth against the validator's own findings.
        #
        # It was 6, and at 6 it did not work. fit runs about 0 to 7 (native +3.0, canonical
        # massing +2.0, beds and area +1.0 each), so full nativity bought 42 points against 8
        # for a serious finding: five serious findings outweighed being the right diagram
        # entirely. The composer duly said "NOT native to this style -- the composer is
        # borrowing a diagram" in the decision log and then ranked the borrowed one first, and
        # WP-4.5 made that visible by adding nine partis for it to borrow from: a tidewater-
        # georgian brief came back recommending an OCTAGON, on 27 serious against the native
        # side-hall town house's 30.
        #
        # At 20 the same spread is worth 140 against 40 -- roughly twelve serious findings --
        # so the right diagram wins unless it is genuinely much worse. It is deliberately NOT
        # enough to outrank a fatal, which is 100 apiece: a native plan with a fatal in it
        # should still lose to a clean borrowed one, because a fatal is a thing that is wrong
        # rather than a thing that is foreign. (WP-4.5)
        NATIVITY_W = 20
        total = score(res) + (60 if miss > tol else 0) - pick["fit"] * NATIVITY_W
        fp = footprint(plan, parti)
        if fp["lot_infeasible"]:
            # WP-2.4 acceptance: a candidate that cannot physically fit the stated lot is
            # never returned, however well it would otherwise have scored — dropped here,
            # not merely outscored, so it can never appear even as the only candidate.
            dropped_lot.append({"parti": pick["parti"], "parti_name": parti["name"], "why": fp["notes"][-1]})
            continue
        out.append({
            "parti": pick["parti"], "parti_name": parti["name"],
            "score": round(total, 1), "style_fit": pick["fit"],
            "counts": counts, "area_sf": round(area), "area_miss_pct": round(miss * 100, 1),
            "footprint": fp,
            "trades_away": parti["trades_away"],
            "why_this_diagram": pick["why"],
            "decisions": log + _summarise(rlog),
            "worst": [{"severity": f["severity"], "layer": f["layer"], "statement": f["statement"]}
                      for f in res["findings"] if f["severity"] in ("fatal", "serious")][:8],
            "plan": plan})
        if on_candidate:
            on_candidate({k: v for k, v in out[-1].items() if k != "plan"})
    # Tie-break by parti id for the same reason pick_partis does: score is rounded to 1dp
    # and is a weighted sum of integer counts, so collisions are reachable — especially
    # between two diagrams from the same fit tie group, which share the -fit*6 term. A
    # stable sort would then fall back to insertion order, and the slice below would be
    # deciding again. Determinism here must not be borrowed from the previous stage.
    out.sort(key=lambda c: (c["counts"].get("fatal", 0), c["score"], c.get("parti") or ""))
    result = {"brief": brief.get("id") or brief.get("name"), "style": brief["style"],
            "target_area_sf": brief["target_area_sf"], "bedrooms": brief.get("bedrooms", 3),
            "candidates": out[:candidates],
            "how_to_read_this": [
              "Candidates are ordered by fatal findings first, then by score. Score is 100 per fatal, 8 per serious, 1 per minor, less a bonus for style fidelity.",
              "trades_away is the honest part. Every diagram gives something up, and the one that scores best is not always the one you want.",
              "decisions lists what the composer chose where the brief was silent. Read it — those are the assumptions, not facts.",
              "A plan with no fatal findings is not therefore good. The corpus can tell you what is wrong and cannot tell you what is alive."]}
    if dropped_lot:
        result["dropped_lot_infeasible"] = dropped_lot
        result["how_to_read_this"].append(
            f"{len(dropped_lot)} diagram(s) were considered and dropped because they cannot fit the stated "
            f"lot at all, even at their minimum bay count — see dropped_lot_infeasible, not silently omitted.")
    return result

# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief"); ap.add_argument("--json", action="store_true"); ap.add_argument("--candidates", type=int)
    a = ap.parse_args()
    brief = json.load(open(a.brief))
    import jsonschema
    jsonschema.validate(brief, json.load(open(f"{ROOT}/schema/brief.schema.json")))
    res = compose(brief, a.candidates or brief.get("candidates", 4))
    if a.json: print(json.dumps(res, indent=1, ensure_ascii=False)); return
    print(f"\n  {brief.get('name') or brief['id']}   {brief['style']}   {brief['target_area_sf']:.0f} sf   {brief.get('bedrooms',3)} bed")
    for i, c in enumerate(res["candidates"], 1):
        cc = c["counts"]
        print(f"\n  {i}. {c['parti_name']}   score {c['score']}   "
              f"fatal {cc.get('fatal',0)}  serious {cc.get('serious',0)}  minor {cc.get('minor',0)}")
        print(f"     {c['area_sf']} sf ({c['area_miss_pct']}% off target) · footprint {c['footprint']['footprint_ft'][0]} x {c['footprint']['footprint_ft'][1]} ft in {c['footprint']['bays']} bays")
        print(f"     why: {'; '.join(c['why_this_diagram'][:2])}")
        print(f"     trades away: {c['trades_away'][:170]}")
        for n in c["footprint"]["notes"]: print(f"     ! {n}")
        for w in c["worst"][:4]: print(f"     [{w['severity']}] {w['statement'][:120]}")
    print("\n  " + "\n  ".join(res["how_to_read_this"]) + "\n")

if __name__ == "__main__":
    main()
