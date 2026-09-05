#!/usr/bin/env python3
"""The facade as a RESULT — the front's bay rhythm derived from the plan's own organising move.

WP-11.7, executing `oq/the-facade-is-a-result-not-an-input` (RULED 4 Sep 2026). The bay rhythm
follows from the plan's organising move — for a centre-door diagram, the centred passage — and not
the other way round. Wenger's chronology is the historical form of the same dependency: Virginia
houses with advanced or pedimented central bays gained popularity *"only after the central passage
had achieved status as an important social space"*.

**THE GENERATOR RUNS IT BACKWARDS TODAY AND THIS MODULE DOES NOT FIX THAT BY COMPOSING A FACADE.**
`elevation._face_bays` builds the front from `facade-classical.json`'s own bay-count formula
against the face's outside width, with no reference to the bay count the PLAN states; `openings.py`
then places each room's declared windows on whatever boundary wall the room happened to reach. So
the front has whatever openings the rooms that reached it declared, at whatever spacing the
placement gave them.

What this module does is the half the ruling actually authorises: it DERIVES the rhythm the plan's
own bays imply, COMPARES the drawn front against it, and REPORTS the difference. The second half of
the ruling is why it stops there — *"the ordering of commitments is how findings are EXPLAINED, not
how they are resolved"*. The system stays a constraint system; Glassie is explicit that his own
rule sets are order-independent (*"It may start at any point, take any route, and yet come to the
same end"*), and a pipeline cannot backtrack when a dependency will not fit the lot.

**THE TRAP THE RULING NAMES, AND THE RULE THIS FILE IS WRITTEN AROUND.** *"A derived facade is a
facade the generator can be WRONG about with confidence. Today the front elevation is an accident
and reads as one; after this it is a claim. Every bay it states must be traceable to a bay the plan
states, and where the plan cannot say, the facade must report COULD NOT EVALUATE rather than
composing something plausible. The window that gets invented to complete a rhythm is this ruling's
version of the invented measurement OQ 52 swept out of the elevation."* So: every function here
returns a verdict with a reason, never a zero and never a filled-in bay, and `rhythm()` refuses
outright rather than guessing on any of five stated grounds.

**SCOPE IS `center-hall` AND NOTHING ELSE, BY NAME.** The ruling is stated for diagrams whose
`circulation_parti` is `center-hall` and says the generalisation to the other twenty partis is NOT
made: *"A Charleston single house is entered sideways off a piazza; a shotgun's front is one bay
and a door; a Craftsman's front is composed around a porch."* Four partis qualify. Every other
diagram gets `could-not-evaluate` naming its own circulation parti — which is a refusal to judge,
not a pass, and not an assertion that its facade is wrong.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

AX = modcache.load("axis", os.path.join(ROOT, "build", "axis.py"))

# The rhythm this ruling is stated for. A string set rather than a truthiness test, because the
# refusal has to be able to NAME the parti it declined -- "side-hall is not center-hall" is a
# useful sentence and "not applicable" is not.
CENTRE_DOOR_PARTIS = ("center-hall",)

# Half a bay module, matching `axis.CENTRE_TOL_BAYS` exactly and for the same reason: an opening
# is IN a bay or it is not, and the only question is how far off a bay's centre it may sit and
# still be that bay's opening. Editorial, ruled 4 Sep 2026; no source states it. It is imported
# rather than re-spelled so the two layers cannot drift -- this repository's most-repeated defect
# is one rule written twice.
BAY_TOL = AX.CENTRE_TOL_BAYS


def _parti_id(plan):
    return plan.get("parti") if isinstance(plan.get("parti"), str) else None


def circulation_parti(plan, C=None):
    """The diagram's own `circulation_parti`, or None with the reason it could not be read.

    Loaded through `core.load_parti` -- the ONE place a caller-supplied parti id becomes a path
    in this repository (`test_parti_confinement.py` scans the tree for a second). Lazily, because
    `core` loads `geometry`, which loads this file's neighbours."""
    pid = _parti_id(plan)
    if not pid:
        return None, "the plan record names no parti, so its circulation diagram is unknown"
    try:
        core = modcache.load("core", os.path.join(ROOT, "mcp_server", "core.py"))
        rec = core.load_parti(pid)
    except Exception as e:                       # unreadable id, missing file, bad JSON
        return None, f"the parti {pid!r} could not be read ({type(e).__name__})"
    if not rec:
        return None, f"the parti {pid!r} could not be read"
    cp = rec.get("circulation_parti")
    if not cp:
        return None, f"the parti {pid!r} states no circulation_parti"
    return cp, None


def rhythm(plan, C=None):
    """The bay rhythm the PLAN's own bays imply for its entrance front — a claim, or a refusal.

    Every bay it states is traceable to `footprint.bays`, which `derive_footprint` computed and
    WP-11.2 made odd where the diagram wants a centre bay. Nothing here reads a pack formula and
    nothing here reads the placement, so this is a statement about the record.

    FIVE STATED GROUNDS FOR REFUSING, and each names what a reader would have to author to get an
    answer, because a refusal whose reason serves three causes has stopped being one (WP-11.4):
    no parti; a parti that is not a centre-door diagram; no bay count; an even bay count (six bays
    have no middle bay for any door to stand in — WP-11.3's own reading); no bay module."""
    fp = plan.get("footprint") or {}
    front = AX.front_of(plan)
    base = {"front": front, "bays": fp.get("bays"), "module_ft": fp.get("bay_module_ft")}

    cp, why = circulation_parti(plan, C)
    if cp is None:
        return {**base, "verdict": "could-not-evaluate", "why": why}
    if cp not in CENTRE_DOOR_PARTIS:
        return {**base, "verdict": "could-not-evaluate", "circulation_parti": cp,
                "why": f"this diagram's circulation parti is {cp!r}, and the ruling derives a "
                       f"front this way only for a centre-door diagram ({'/'.join(CENTRE_DOOR_PARTIS)}). "
                       f"Its facade rule is that parti's own to state and is not written here."}

    bays, module = fp.get("bays"), fp.get("bay_module_ft")
    if not bays:
        return {**base, "verdict": "could-not-evaluate", "circulation_parti": cp,
                "why": "the placement states no bay count, so there is no rhythm to derive"}
    if bays % 2 == 0:
        return {**base, "verdict": "could-not-evaluate", "circulation_parti": cp,
                "why": f"{bays} bays is an even count and has no middle bay, so a centre-door "
                       f"diagram's own organising move has nowhere to land"}
    if not module:
        return {**base, "verdict": "could-not-evaluate", "circulation_parti": cp,
                "why": "the placement states no bay module"}

    W = (fp.get("width_ft") or 0.0)
    if not W:
        return {**base, "verdict": "could-not-evaluate", "circulation_parti": cp,
                "why": "the placement states no width, so no bay can be given a centre"}
    # Bay centres across the block's OWN width, which is what the plan states -- not across a
    # face span the elevation re-derives. Evenly spaced, because a centre-door diagram's bays are
    # the module repeated and the realised spacing is the width divided by the count.
    span = W / bays
    mid = bays // 2
    out = []
    for i in range(bays):
        out.append({"bay": i, "centre_ft": round((i + 0.5) * span, 3),
                    "kind": "door" if i == mid else "window"})
    return {**base, "verdict": "derived", "circulation_parti": cp, "centre_bay": mid,
            "realised_bay_width_ft": round(span, 3), "bays_out": out,
            "note": (f"The rhythm the plan's own {bays} bays imply: the door in bay {mid}, one "
                     f"window per remaining bay per storey. Derived from footprint.bays and the "
                     f"block's own width, never from a pack's bay-count formula -- the facade is "
                     f"a result (oq/the-facade-is-a-result-not-an-input).")}


def blind_bays(plan, C=None):
    """Which derived bays a chimney stack stands on, from the plan's own stated hearths.

    OQ 85's rule one layer up: the bay a stack stands on is `blind`, no opening at either storey.
    This reads `hearths.stack_axes`, which derives from the plan's stated hearths and returns None
    where the plan states none -- so a plan with no hearths gets an empty list AND a reason, never
    a silent zero. `roof.py`'s own centre-line fallback is deliberately NOT read here: a stack the
    plan did not state is not a bay the plan states, and blinding a bay on it would be composing
    something plausible, which is the trap this ruling names."""
    r = rhythm(plan, C)
    if r["verdict"] != "derived":
        return {"verdict": "could-not-evaluate", "why": r["why"], "bays": []}
    try:
        H = modcache.load("hearths", os.path.join(ROOT, "build", "hearths.py"))
        axes = H.stack_axes(plan, C)
    except Exception as e:
        return {"verdict": "could-not-evaluate", "bays": [],
                "why": f"the plan's hearths could not be read ({type(e).__name__}: {e})"}
    if not axes:
        return {"verdict": "none-stated", "bays": [],
                "why": "this record states no hearth, so no bay is blinded by a stack. That is "
                       "not a house with no fires -- it is a record that does not say where they "
                       "are (oq/fourteen-of-sixteen-plans-name-no-massing)."}
    front = r["front"]
    tol = r["realised_bay_width_ft"] * BAY_TOL
    hit = []
    for a in axes:
        if (a.get("wall") or "").upper() == front and a.get("position_ft") is not None:
            for b in r["bays_out"]:
                if abs(b["centre_ft"] - a["position_ft"]) <= tol:
                    hit.append(b["bay"])
    return {"verdict": "read", "bays": sorted(set(hit)),
            "why": (f"{len(set(hit))} bay(s) of the front carry a stated flue and are blind."
                    if hit else
                    "every stated flue is on a wall other than the front, so no front bay is blind")}


def compare(plan, level=0, C=None):
    """What the front CARRIES against what the plan's bays say it should — findings, never a fix.

    The declared count is never overwritten (WP-6.2's rule stands) and no opening is ever invented
    to complete a rhythm. Three kinds of disagreement, each stated separately because they call
    for different actions: a bay the plan implies and the drawing leaves empty; an opening the
    drawing places in no bay at all; and the door standing somewhere other than the middle bay."""
    r = rhythm(plan, C)
    if r["verdict"] != "derived":
        return {"verdict": "could-not-evaluate", "why": r["why"], "findings": []}
    fo = AX.front_openings(plan, level)
    blind = set((blind_bays(plan, C) or {}).get("bays") or [])
    tol = r["realised_bay_width_ft"] * BAY_TOL

    filled, orphans = {}, []
    for o in fo["openings"]:
        near = [b for b in r["bays_out"] if abs(b["centre_ft"] - o["pos_ft"]) <= tol]
        if not near:
            orphans.append(o)
            continue
        b = min(near, key=lambda b: abs(b["centre_ft"] - o["pos_ft"]))
        filled.setdefault(b["bay"], []).append(o)

    findings = []
    for b in r["bays_out"]:
        if b["bay"] in blind:
            continue
        if b["bay"] not in filled:
            findings.append({
                "kind": "front-bay-with-no-opening", "bay": b["bay"],
                "centre_ft": b["centre_ft"], "level": level,
                "statement": (f"Bay {b['bay']} of the {r['front']} front carries no opening on "
                              f"level {level}. The plan states {r['bays']} bays; a centre-door "
                              f"diagram wants one opening in each that no stack blinds. NOT a "
                              f"instruction to add a window: the bay is reported empty, and "
                              f"whether the room behind it can carry one is the room's question.")})
    for o in orphans:
        findings.append({
            "kind": "front-opening-in-no-bay", "room": o["room"], "level": level,
            "position_ft": o["pos_ft"],
            "statement": (f"{o['room']}'s {o['kind']} sits at {o['pos_ft']} ft on the "
                          f"{r['front']} front, which is more than half a bay from every one of "
                          f"the {r['bays']} bay centres the plan implies.")})
    # THE DOOR'S BAY IS DELIBERATELY NOT A FINDING OF THIS FUNCTION, AND THE FIRST DRAFT MADE IT
    # ONE. `plan_check`'s drawn layer already emits `drawn-door-off-the-centre-bay` from WP-11.3's
    # axis reading, so a second one here is the same rule spelled twice -- this repository's
    # most-repeated defect, and it arrived in the package whose own ruling is about not saying a
    # thing twice in two vocabularies.
    #
    # **AND THE TWO DISAGREED ABOUT THE NUMBER.** The existing finding reads *"the front door
    # stands in bay 5 of 7, not the middle bay (4)"* and this one read *"bay 4 of 7 ... puts it in
    # bay 3"*: `axis.door_bay` returns a ZERO-based index and the older finding adds one for the
    # reader. A sheet carrying both would have given one door two bay numbers.
    #
    # It was found because the SERIOUS count did not move when it should have: the inversion of
    # `centre-passage-core`'s facade-share test removed one serious finding and this duplicate
    # added one back, so 63 stayed 63 and both changes were invisible. Two errors cancelling,
    # which is the shape CLAUDE.md records at corpus scale for the arc sweep flag.
    _ = AX.door_bay  # the reader that owns this question; see the note above
    return {"verdict": "compared", "front": r["front"], "bays": r["bays"],
            "centre_bay": r["centre_bay"], "level": level,
            "bays_filled": len(filled), "bays_blind": sorted(blind),
            "declared_but_unplaced": fo["declared_but_unplaced"], "findings": findings}


def room_front_bays(plan, level=0, C=None):
    """For each room whose front wall is ON the entrance front: the bays that wall spans, beside
    the window count the room DECLARES.

    The ruling's fourth commitment — *"a room's windows become the bays its front wall spans. Not
    a declared count placed where it fits."* — and the sentence right after it is why this
    function reports instead of writing: *"The DECLARED count is still never overwritten (WP-6.2's
    rule stands); where the two disagree the record says so, which is a finding and not a silent
    correction."* Losing an author's intent to a derived rhythm is the same silent overwrite
    WP-6.2 removed, arriving from the other direction.

    A room is on the front when its placed rectangle reaches the front wall within the same
    tolerance `openings._boundary_walls` uses, and the bays it spans are the derived bay centres
    that fall inside its own x-extent. A room with no placement is skipped and counted, because a
    room whose rectangle nobody drew cannot be said to span anything."""
    r = rhythm(plan, C)
    if r["verdict"] != "derived":
        return {"verdict": "could-not-evaluate", "why": r["why"], "rooms": [], "unplaced_rooms": 0}
    fp = plan.get("footprint") or {}
    W, H = fp.get("width_ft") or 0.0, fp.get("depth_ft") or 0.0
    front = r["front"]
    tol = 0.6                     # openings._boundary_walls' own tolerance, deliberately equal
    rows, skipped = [], 0
    for lv in plan.get("levels", []):
        if (lv.get("index") or 0) != level:
            continue
        for rm in lv.get("rooms", []):
            g = rm.get("geometry")
            if not g:
                skipped += 1
                continue
            x0, x1 = g["x_ft"], g["x_ft"] + g["width_ft"]
            y0, y1 = g["y_ft"], g["y_ft"] + g["depth_ft"]
            on = ((front == "S" and y0 <= tol) or (front == "N" and y1 >= H - tol)
                  or (front == "W" and x0 <= tol) or (front == "E" and x1 >= W - tol))
            if not on:
                continue
            spans = [b["bay"] for b in r["bays_out"] if x0 - 1e-9 <= b["centre_ft"] <= x1 + 1e-9]
            declared = sum(int(w.get("count") or 1) for w in (rm.get("windows") or [])
                           if (w.get("wall") or "").upper() == front)
            has_door = any(d.get("to") == "exterior" and (d.get("wall") or "").upper() == front
                           for d in (rm.get("doors") or []))
            # The door's bay is not a window bay, so a room carrying the front door wants one
            # fewer window than it spans bays. Stated rather than folded in silently.
            want = max(0, len(spans) - (1 if has_door else 0))
            # A ROOM ON THE FRONT THAT SPANS NO BAY CENTRE IS NOT A ROOM THAT AGREES. It is
            # narrower than a bay and sitting between two centres, and with no windows declared
            # it would otherwise read `wants 0, declares 0, agrees` -- a trivial pass hiding a
            # room whose front wall the rhythm cannot account for. Its own state, named.
            rows.append({"room": rm["id"], "bays": spans, "wants": want, "declares": declared,
                         "carries_front_door": has_door,
                         "agrees": (want == declared) if spans else None,
                         "spans_no_bay": not spans})
    return {"verdict": "read", "front": front, "level": level, "rooms": rows,
            "unplaced_rooms": skipped,
            "disagreements": [x for x in rows if x["agrees"] is False],
            "span_no_bay": [x for x in rows if x["spans_no_bay"]]}


def _advisory_band(quantity="passage_width_to_facade_width"):
    """The observed band, from the grouping rule that states it — one spelling.

    Returns None where it cannot be read, and the caller then reports `within_advisory: None`
    rather than defaulting to a band: a share judged against a number nobody could find is the
    fake-pass direction, and this whole package is about a rule that was stated in two places."""
    try:
        g = json.load(open(os.path.join(ROOT, "groupings", "centre-passage-core.json")))
    except Exception:
        return None
    for r in g.get("internal_rules") or []:
        m = r.get("measures") or {}
        if m.get("quantity") == quantity and m.get("advisory_band"):
            return list(m["advisory_band"])
    return None


def facade_share(plan, C=None):
    """The passage's share of the front, REPORTED rather than required.

    This is the ruling's first commitment and the one place it makes a currently-executable rule
    LESS executable, deliberately: `groupings/centre-passage-core.json`'s hard test
    `passage_width_ft / facade_width_ft between 0.18 and 0.27` sizes the passage FROM the facade,
    which under this ruling is backwards. The passage takes a bay; its share of the front is a
    consequence. The band stays as an ADVISORY, because the ratio is a real observation about the
    type, and the prose `statement` is untouched.

    Returns the share and whether it falls in the observed band, and `could-not-evaluate` where
    the plan has no passage or no width -- never a pass."""
    fp = plan.get("footprint") or {}
    W = fp.get("width_ft")
    if not W:
        return {"verdict": "could-not-evaluate", "why": "the placement states no width"}
    pw = None
    for lv in plan.get("levels", []):
        if (lv.get("index") or 0) != 0:
            continue
        for rm in lv.get("rooms", []):
            if "centre-passage" in (rm.get("type") or "") or "center-passage" in (rm.get("type") or ""):
                g = rm.get("geometry")
                pw = (min(g["width_ft"], g["depth_ft"]) if g else
                      min(rm.get("width_ft") or 0, rm.get("length_ft") or 0)) or None
    if not pw:
        return {"verdict": "could-not-evaluate",
                "why": "this plan has no centre passage, so it has no share to report"}
    share = pw / W
    # THE BAND IS READ FROM THE RECORD, NEVER TRANSCRIBED. A first draft wrote the pair as a
    # literal here, which is the grouping's own number spelled a second time -- the defect this
    # corpus keeps meeting, committed inside the function whose whole subject is one rule stated
    # twice. `check_rooms.py` caught the schema half of the same change and this half was found
    # chasing it. `advisory_band` exists on the rule for exactly this reader.
    #
    # **AND THIS COMMENT DELIBERATELY DOES NOT REPEAT THE FIGURES**, which is not fastidiousness:
    # the first version quoted them to explain the defect and `test_no_second_transcription_of_
    # the_band_in_the_tree` duly flagged this file -- the note demonstrating the finding by
    # committing it. CLAUDE.md records the identical move for the citation guard, whose own entry
    # says it "does not repeat the offending string, because writing it here would raise the
    # unchecked count by one in the paragraph reporting the unchecked count."
    band = _advisory_band()
    return {"verdict": "reported", "passage_width_ft": round(pw, 2), "facade_width_ft": round(W, 2),
            "share": round(share, 4), "advisory_band": band,
            "advisory_band_source": "groupings/centre-passage-core.json"
                                    if band else "COULD NOT BE READ",
            "within_advisory": (band[0] <= share <= band[1]) if band else None,
            "note": ("Reported, not required (oq/the-facade-is-a-result-not-an-input). The passage "
                     "takes a bay and its share of the front follows; the band is the observed "
                     "range for the type, kept as an advisory because the observation is real.")}


def main():
    import argparse
    ap = argparse.ArgumentParser(description="the front's bay rhythm, derived from the plan")
    ap.add_argument("plan")
    ap.add_argument("--engine", default="heuristic", choices=["auto", "cp", "heuristic"])
    a = ap.parse_args()
    GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
    plan = json.load(open(a.plan))
    out = GEO.solve(plan, engine=a.engine)
    print(json.dumps({"rhythm": rhythm(out), "blind": blind_bays(out),
                      "ground": compare(out, 0), "upper": compare(out, 1),
                      "facade_share": facade_share(out)}, indent=2))


if __name__ == "__main__":
    main()
