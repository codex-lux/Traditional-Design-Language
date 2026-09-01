#!/usr/bin/env python3
"""The composer. Template-seeded, validator-scored, and it returns several plans rather than one.

  read a brief -> pick partis native to the style -> instantiate at the target size
  -> repair against the validator until it stops improving -> emit N contrasting candidates

Objective: fatal-free first, then highest score — a composite out of 100 where every axis is
a share of its own denominator, with a fatal finding carried beside it as a stated
disqualification rather than folded into it (see SCORE_AXES). Where the brief underdetermines something the composer decides it and SAYS SO in
the decision log rather than presenting the choice as a fact. Judgment slots are surfaced, never silently resolved — a plan that violates
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

# ---------------------------------------------------------------- the score
#
# What a candidate is worth OUT OF 100, and why it is a composite rather than a total.
#
# It used to be the demerit sum above: 100 a fatal, 8 a serious, 1 a minor, less 20 a point
# of style fidelity, LOWER IS BETTER. Three things were wrong with publishing that as a
# "score". It had no ceiling, so the figure was only ever comparative while the workbench's
# big numeral invited an absolute reading it could not support. It ran in the unintuitive
# direction under a label that promises the other one. And its magnitude tracked corpus
# density and plan size rather than quality -- bungalow-small's candidates run -66 to 146
# and family-georgian's 176 to 283, for plans of comparable merit -- because a bigger house
# is simply checked more times, 27 rooms against 14.
#
# The composite fixes all three by scoring each axis as a SHARE of its own denominator:
# what came back clean out of what was actually checked. A bigger house puts more rooms in
# the numerator and the same rooms in the denominator, so size cancels. Every axis lands
# between 0 and 1, the weights sum to 100, and the whole arithmetic is published on the
# record so the number can be argued with rather than believed.
#
# UNJUDGED IS NOT PASSED, and here that means an axis with no evidence neither scores zero
# nor scores full marks: its weight is DROPPED and the total renormalised over the weight
# that could be evaluated, with the dropped weight reported beside the score. A candidate
# whose style constraints were every one unjudged is scored out of 94, and says so.
#
# A FATAL FINDING DISQUALIFIES A CANDIDATE, and that is carried BESIDE the score rather than
# inside it. The guarantee -- that a plan carrying a fatal never outranks a clean one, however
# native its diagram (WP-4.5's NATIVITY_W argument) -- lives in the sort's primary key, which
# is the fatal count and is never traded against anything. The score does not have to enforce
# it a second time.
#
# This was first built the other way, withholding the score entirely on a fatal, and MEASURING
# IT KILLED IT: composed across eight briefs, five returned candidate sets in which EVERY
# candidate carried a fatal -- `cape-cod-colonial` and `greek-revival` among them, which OQ 63
# already records as styles that cannot return a clean plan under their own native diagram.
# Every column then read "—" and the four plans could not be told apart at all, which is
# strictly less than the demerit total gave. Withholding an aggregate while publishing all
# eight of its components is not a refusal; it is a number hidden from the one reader who
# needed it most. So the score is always computed, `disqualified` is always stated, and the
# ordering enforces what the disqualification means.
#
# Within the axes a fatal spends its room exactly as a serious does (SEV_CREDIT), because the
# axes measure the share of checks that came back clean and that is what a failed check costs.
# The difference between wrong and worse is carried by `disqualified`, in words.
#
# THE WEIGHTS ARE EDITORIAL, with ONE exception that is measured. They are a judgement about
# what matters in a house, stated once here rather than buried inside a sum. The fault corpus
# and the two room-level axes are still more than half the score because they are what a
# fluent reader notices walking through. The code layer is deliberately absent: it is advisory
# and jurisdictional and plan_check.py says so in its own note, so scoring a house on it would
# be scoring it against a jurisdiction nobody named.
#
# FIDELITY AT 25 IS THE MEASURED ONE, and it is 25 rather than 18 because 18 reproduced the
# exact failure WP-4.5 exists to prevent. The composite is NOT order-equivalent to the demerit
# total it replaced -- it cannot be, because `demerits` charges 1 a minor without limit while
# an axis charges half a room however many minors land on it, and no weighting reconciles
# those. So the ruling had to be preserved deliberately rather than inherited. At 18, a
# tidewater-georgian brief returned `tower-villa` and `octagon-radial` (fit 2.0, both borrowed)
# over `side-hall-townhouse` (fit 3.6, native) -- an OCTAGON for a Tidewater Georgian, which is
# the sentence WP-4.5's own NATIVITY_W comment uses to describe the bug it fixed.
#
# The number comes from a measurement, not from the answer it produces. Across both shipped
# briefs' full pick windows, the spread of the whole NON-FIDELITY subtotal between clean
# candidates is 18.0 points on family-georgian and 22.0 on bungalow-small. Fidelity's full
# swing is its weight, so at 18 it could not span the field its own axis was supposed to
# outweigh; at 25 it can, with the larger of the two measured spreads cleared. That is the
# composite expressing WP-4.5's ruling -- the right diagram wins unless another is genuinely
# much worse -- rather than approximating it by luck. Re-measure before moving it: the script
# is in the report, and the spread is a property of the corpus, not a constant.
SCORE_AXES = [
    ("solecisms",   20, "the fault corpus \u2014 the named things that read as wrong to someone fluent"),
    ("rooms",       18, "each room against its catalogue band, its furniture, its daylight and its servicing"),
    ("connections", 16, "each room against the adjacency, circulation, privacy and completeness rules"),
    ("fidelity",    25, "how native the diagram is to the style and how canonical its massing"),
    ("area",         7, "how close the plan lands to the area the brief asked for"),
    ("bedrooms",     4, "whether the bedrooms the brief asked for are actually in the plan"),
    ("canon",        5, "declared slots, groupings, massing affinity and the style's own constraints"),
    ("buildability", 5, "the footprint against the bay module and the depth a plan can daylight"),
]
assert sum(w for _, w, _ in SCORE_AXES) == 100

# Which axis each of plan_check.py's finding layers belongs to. None means deliberately
# unscored, and there is exactly one of those. A layer missing from this map is reported on
# the record as `score_unclassified` rather than silently dropped -- a new layer in the
# validator must not quietly stop counting.
SCORE_LAYERS = {
    "fault": "solecisms",
    "room": "rooms", "furniture": "rooms", "daylight": "rooms", "servicing": "rooms",
    "plan": "rooms",
    "adjacency": "connections", "circulation": "connections", "privacy": "connections",
    "completeness": "connections",
    "style": "canon", "grouping": "canon",
    "code": None,
    # WP-6.2. The drawn layer judges the PLACED house, and this composer does not place its
    # candidates — so on everything it scores today the layer can say only "could not
    # evaluate", which is an `info` and is pulled out of every axis's fraction already.
    # Mapping it changes no number now and is the right answer the moment a placed plan is
    # scored: the layer exists because the declared door graph and the drawn one disagree,
    # and `connections` is the axis about whether the house hangs together. The compromise,
    # stated rather than hidden: the layer's drawn-against-declared SIZE findings ride on
    # `connections` too, and they are not connection facts. Splitting one layer across two
    # axes is the alternative, and it would mean re-weighting a composite whose weights are
    # already flagged as editorial and whose returned set has changed once as a side effect
    # (OQ 66, OQ 67). Not worth doing silently in a package about something else.
    "drawn": "connections",
}

# What a room is still worth once something has been found against it. A serious finding
# spends the room; a minor halves it; advisory and info leave it whole, because the corpus
# calls those advisory and unjudged respectively and neither is a failure.
SEV_CREDIT = {"fatal": 0.0, "serious": 0.0, "minor": 0.5, "advisory": 1.0, "info": 1.0}

# The most pick_partis() can award: 3.0 native + 2.0 canonical massing + 1.0 bedroom range
# + 1.0 area range. It can go NEGATIVE (a forbidden massing costs 4.0), which is why the
# share is clamped at the bottom rather than allowed to drag the composite below zero.
MAX_FIT = 7.0

# The two tests footprint() runs on a candidate that fits its lot: is it deeper than a plan
# can daylight, and has it reached the width the diagram grows to. The third note it can
# emit is lot_infeasible, and a candidate carrying that one is dropped rather than scored.
FOOTPRINT_TESTS = 2

# What the brief means by "4 bed". function_class 'sleeping' also holds the dressing room
# and the sleeping porch, and neither is a bedroom anybody counts.
BEDROOM_TYPES = {"bedroom", "primary-bedroom", "bedchamber", "garret-chamber", "nursery"}


def _num(x, default=0.0):
    """A float, or the default. Every number reaching score_candidate comes from compose()'s
    own arithmetic today, but score_candidate is called directly by tests and by anything
    that wants to score a candidate it built itself -- and compose() has NO per-candidate
    try/except, so one TypeError here does not spoil one candidate, it fails the whole job
    and returns four plans as a single error string. Cheaper to be total."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return default
    return default if f != f or f in (float("inf"), float("-inf")) else f


def _axis_from_layers(res, axis, n_rooms):
    """A per-room axis: every room is an opportunity, the worst finding against it decides
    what it still scores. A finding in these layers that names no room becomes its own
    opportunity, so nothing lands outside the denominator."""
    per_room, loose, unjudged = {}, [], 0
    for f in res.get("findings") or []:
        if SCORE_LAYERS.get(f.get("layer")) != axis: continue
        # An `info` finding is the validator saying it could not judge, or asking for a check
        # by hand. It is pulled OUT of the fraction here exactly as _axis_canon and the
        # solecisms axis pull it out of theirs. It used to take SEV_CREDIT 1.0 and count as a
        # room that passed, which is the one direction this corpus must never round in --
        # three treatments of the same severity across three axes, one of them "unjudged is
        # passed".
        if f.get("severity") == "info":
            unjudged += 1; continue
        credit = SEV_CREDIT.get(f.get("severity"), 0.0)
        rid = f.get("room")
        if rid: per_room[rid] = min(per_room.get(rid, 1.0), credit)
        else: loose.append(credit)
    of = n_rooms + len(loose)
    if not of: return None
    kept = sum(per_room.values()) + sum(loose) + max(0, n_rooms - len(per_room))
    return {"share": max(0.0, min(1.0, kept / of)), "of": of,
            "clean": round(kept, 2), "flagged": len(per_room) + len(loose),
            "unjudged": unjudged or None,
            "denominator": f"{n_rooms} rooms" + (f" + {len(loose)} plan-wide" if loose else "")}


def _axis_buildability(fp):
    """The two tests footprint() actually runs, read from footprint()'s own tally."""
    run = fp.get("tests_run", FOOTPRINT_TESTS)
    failed = fp.get("tests_failed")
    if failed is None:                       # a footprint dict from before the tally existed
        failed = min(run, len(fp.get("notes") or []))
    failed = max(0, min(run, failed))
    return {"share": 1.0 - failed / run if run else None, "of": run,
            "clean": run - failed, "flagged": failed,
            "denominator": f"{run} footprint tests"}


def _axis_canon(res, plan):
    """Not per room: per RULE. Every declared slot, every grouping, every constraint the
    style layer could actually evaluate and the massing affinity is one opportunity. The
    info-level findings here are 'cannot evaluate' and 'check by hand' -- unjudged, counted
    as such, and kept out of both halves of the fraction."""
    cs = res.get("constraint_summary") or {}
    of = (len(plan.get("declared") or {}) + len(plan.get("groupings") or [])
          + cs.get("present", 0) + cs.get("clear", 0) + (1 if plan.get("massing") else 0))
    # plan_check.py increments constraint_summary["unjudged"] AND emits an `info` finding for
    # the SAME constraint, so seeding the tally from the summary and then adding every info
    # finding counted each of them twice -- the workbench read "17 canon could not be
    # evaluated" where the true figure was 13. Every unjudged constraint has an info finding,
    # so the info count already covers them; max() keeps the number honest if that invariant
    # ever stops holding rather than silently under-reporting.
    per_rule, loose, info_findings = {}, [], 0
    for f in res.get("findings") or []:
        if SCORE_LAYERS.get(f.get("layer")) != "canon": continue
        if f.get("severity") == "info":
            info_findings += 1; continue
        credit = SEV_CREDIT.get(f.get("severity"), 0.0)
        k = f.get("rule")
        if k: per_rule[k] = min(per_rule.get(k, 1.0), credit)
        else: loose.append(credit)
    unjudged = max(cs.get("unjudged", 0), info_findings)
    of = max(of, len(per_rule)) + len(loose)
    if not of: return {"share": None, "of": 0, "unjudged": unjudged}
    kept = sum(per_rule.values()) + sum(loose) + max(0, of - len(loose) - len(per_rule))
    return {"share": max(0.0, min(1.0, kept / of)), "of": of, "clean": round(kept, 2),
            "flagged": len(per_rule) + len(loose), "unjudged": unjudged,
            "denominator": "declared slots, groupings, evaluated constraints and the massing"}


def score_candidate(res, plan, brief, fit, fp, miss, tol):
    """The composite, itemised. Returns the score out of 100, every axis with its own share
    and denominator, the weight that could not be evaluated at all, and whether a fatal
    finding DISQUALIFIES the candidate -- which is stated beside the score and enforced by
    the ordering, never by withholding the number. `score` is None only in the unreachable
    case where no axis had any evidence at all."""
    n_rooms = res.get("rooms") or 0
    fs = res.get("fault_summary") or {}
    judged = fs.get("clear", 0) + fs.get("present", 0)
    # int(): `bedrooms` reaches here from a brief that the CLI does NOT schema-validate
    # (build/compose.py's main() validates, `compose()` called as a library does not), and a
    # string "4" used to raise TypeError inside the division below -- which aborts the whole
    # compose job, because there is no per-candidate guard anywhere up the stack. A brief
    # that cannot say how many bedrooms it wants leaves the axis unevaluated instead.
    try:
        beds_want = int(brief.get("bedrooms", 3) or 0)
    except (TypeError, ValueError):
        beds_want = 0
    # .get throughout: a malformed record must leave the bedrooms axis at nothing found,
    # not raise. score_candidate runs inside compose()'s per-candidate loop and
    # workbench/server/jobs.py::_run has no per-candidate guard — one KeyError here fails
    # the whole compose job, and the axis it would have set is worth 4 points of 100.
    beds_have = sum(1 for lv in (plan.get("levels") or [])
                    for r in (lv.get("rooms") or []) if r.get("type") in BEDROOM_TYPES)

    raw = {
        "solecisms": ({"share": fs.get("clear", 0) / judged, "of": judged, "clean": fs.get("clear", 0),
                       "flagged": fs.get("present", 0), "unjudged": fs.get("unjudged", 0),
                       "denominator": f"{judged} faults the corpus could judge on this plan"}
                      if judged else {"share": None, "of": 0, "unjudged": fs.get("unjudged", 0)}),
        "rooms": _axis_from_layers(res, "rooms", n_rooms),
        "connections": _axis_from_layers(res, "connections", n_rooms),
        "fidelity": {"share": _num(fit) / MAX_FIT, "of": MAX_FIT,
                     "clean": round(_num(fit), 2), "flagged": 0,
                     "denominator": f"fit {_num(fit)} of a possible {MAX_FIT}"},
        "area": {"share": ((1.0 - _num(miss) / _num(tol)) if _num(tol)
                           else (1.0 if _num(miss) == 0 else 0.0)),
                 "of": 1, "clean": None, "flagged": 0,
                 "denominator": f"{round(_num(miss) * 100, 1)}% off target against the brief's "
                                f"{round(_num(tol) * 100, 1)}% tolerance"},
        "bedrooms": ({"share": beds_have / beds_want, "of": beds_want,
                      "clean": beds_have, "flagged": max(0, beds_want - beds_have),
                      "denominator": f"{beds_have} of {beds_want} asked for"}
                     if beds_want else {"share": None, "of": 0}),
        "canon": _axis_canon(res, plan),
        "buildability": _axis_buildability(fp),
    }

    axes, earned, evaluable = [], 0.0, 0
    for name, weight, _what in SCORE_AXES:
        a = raw.get(name) or {"share": None, "of": 0}
        share = a.get("share")
        if share is not None:
            # THE CEILING IS ENFORCED HERE, ONCE, and nowhere else. `area`, `bedrooms` and
            # `fidelity` deliberately return their raw ratios above and are clamped only here.
            # Each of them used to clamp itself as well, and two clamped only one end: `area`
            # clamped the bottom, so a brief with a NEGATIVE area_tolerance -- which the schema
            # permitted until this commit -- gave 1 - miss/tol above 1 and published a score of
            # 902.8 "out of 100"; `bedrooms` clamped the top and could go negative the same way.
            # Restoring a per-axis clamp is not harmless: it makes THIS line unreachable, and a
            # mutation run proved that with both in place, deleting the ceiling changes nothing
            # any test can see. One enforcement point, tested, beats two and neither.
            try:
                share = max(0.0, min(1.0, float(share)))
            except (TypeError, ValueError):
                share = None
        row = {"axis": name, "weight": weight,
               "share": None if share is None else round(share, 4),
               "of": a.get("of"), "clean": a.get("clean"), "flagged": a.get("flagged"),
               "unjudged": a.get("unjudged"), "denominator": a.get("denominator")}
        if share is None:
            row["points"] = None
            row["note"] = "could not be evaluated on this plan — its weight is dropped, not passed"
        else:
            row["points"] = round(weight * share, 1)
            earned += weight * share; evaluable += weight
        axes.append(row)

    unclassified = sorted({f.get("layer") for f in (res.get("findings") or [])
                           if f.get("layer") not in SCORE_LAYERS} - {None})
    fatal = res["counts"].get("fatal", 0)
    out = {"score": round(100 * earned / evaluable, 1) if evaluable else None,
           "score_axes": axes,
           "score_weight_evaluated": evaluable, "score_weight_unevaluated": 100 - evaluable,
           "score_unclassified_layers": unclassified,
           "disqualified": bool(fatal)}
    if fatal:
        out["disqualified_because"] = (
            f"{fatal} fatal finding{'s' if fatal != 1 else ''}. A fatal is a thing that is wrong, "
            f"not a thing that is worse: this candidate cannot outrank a plan with none, whatever "
            f"it scores, and its score is not a case for building it.")
    if not evaluable:
        # Unreachable as the axes stand -- fidelity, area and buildability always have a
        # denominator, so `evaluable` is at least 31. Kept because "no evidence" must never
        # arrive as a silent 0.0, and a future axis set could reach it.
        out["score_unscored_because"] = "nothing on this plan could be evaluated — unjudged, not passed."
    return out

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
            # list(): the plan used to take a REFERENCE to the parti's own groupings list,
            # and attach_garage() below appends "garage-and-hyphen" to plan["groupings"] --
            # which is to say, to PARTIS[parti_id]["groupings"], permanently, for the life of
            # the process. One brief asking for a garage therefore left five of twenty-one
            # partis declaring a garage grouping for every LATER brief, on plans that have no
            # garage, and the grouping layer duly reported it. Measured: composing
            # bungalow-small, then family-georgian, then bungalow-small again moved
            # connected-farmstead's demerits from 146.0 to 155.0 in one process. The workbench
            # runs every compose job on one long-lived worker, so it is exactly where this
            # bites. Pre-existing; found by the adversarial audit of the score change, which
            # needed stable numbers to calibrate against and did not get them.
            "groupings": list(p.get("groupings") or []),
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
    # WP-6.2 — after symmetrise, so a door is dimensioned ONCE and both of its records
    # agree. Before this, every composed door was `{"to": id}` and the renderers guessed.
    derive_openings(plan, brief["style"], log)
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

# --------------------------------------------------------------- the opening grammar
# WP-6.2. Until this package every door a composed plan carried was `{"to": id}` -- no
# width, no type, no rank -- and every window was a hardcoded 3.2 ft unit, twice, on every
# lit wall of every room in every style. Both renderers then invented what the record did
# not hold. None of what follows is NEW knowledge: opening-proportion derives an entry leaf
# from the storey height and says in its own note why a wide one becomes a pair, sash-light
# derives the lights, the kits grade the doors `principal 84 in, secondary 80 in, service
# 78 in`, and 53 of 60 room records carry a glazing_fraction band. The corpus knew all of
# it and the composer read none of it.

_GRAMMAR = None

def grammar():
    global _GRAMMAR
    if _GRAMMAR is None:
        with open(f"{ROOT}/openings/grammar.json", "r", encoding="utf-8") as fh:
            _GRAMMAR = json.load(fh)
    return _GRAMMAR

_WGRAMMAR = None

def window_grammar():
    global _WGRAMMAR
    if _WGRAMMAR is None:
        with open(f"{ROOT}/openings/window-grammar.json", "r", encoding="utf-8") as fh:
            _WGRAMMAR = json.load(fh)
    return _WGRAMMAR


def window_rule(room_type, wall_exposure="exterior"):
    """The window grammar's rule for a room against a wall. First match, stated order."""
    g = window_grammar()
    rt = C["rooms"].get(room_type) or {}
    for r in (g.get("room_rules") or []):
        w = r.get("when") or {}
        if room_type in ((w.get("room") or {}).get("type") or []) \
           and w.get("wall", wall_exposure) == wall_exposure:
            return r
    for r in (g.get("class_defaults") or []):
        w = r.get("when") or {}
        if rt.get("function_class") in ((w.get("room") or {}).get("function_class") or []) \
           and w.get("wall", wall_exposure) == wall_exposure:
            return r
    return g["default"]


_WT_CACHE = {}

def kit_window_type(style):
    """The SASH KIND the style says, or None if nobody has authored one — never a guess.

    WP-7.3 (OQ 91). The grammar decides a window's ROLE and the kit decides its KIND, and
    neither may answer for the other.

    RESOLVED THROUGH THE LINEAGE, not read off the flat kit file, and the difference is the
    whole answer. `kits/*.json` carries `window_type` as `status: empty` on 120 of 159 —
    `tidewater-georgian`, the corpus's own worked example, among them. `resolve_kit` walks
    the cascade and finds it: `double-hung`, specified by `georgian-colonial-american`, with
    six variants forbidden. A first version of this function read the flat file and would
    have reported COULD NOT EVALUATE for a style the corpus can answer for perfectly well —
    the "unjudged is not passed" rule run backwards, which is its own kind of lie.

    The provenance travels with the answer because the cascade delivers things nobody bound
    (OQ 51): a reader has to be able to see that Tidewater's sash kind is its Georgian
    ancestor's and not its own."""
    if style in _WT_CACHE:
        return _WT_CACHE[style]
    RK = _mod("resolve_kit", f"{ROOT}/build/resolve_kit.py")
    try:
        graph = RK.load_graph()
        slots, _sav = RK.resolve_slots(graph, RK.chain_for(graph, style),
                                       RK.scope_for(graph, style))
    except Exception:
        slots = {}
    slot = (slots or {}).get("window_type") or {}
    if slot.get("binding") == "forbidden":
        out = (None, None, "the kit forbids a window_type outright")
    else:
        allowed = [v for v in (slot.get("variants") or [])
                   if (v.get("status") or "") != "forbidden"]
        if allowed:
            out = (allowed[0].get("id"), slot.get("from") or slot.get("source"), None)
        elif slot.get("variants"):
            out = (None, None, "every window_type variant this kit names is forbidden")
        else:
            out = (None, None, None)
    _WT_CACHE[style] = out
    return out


def _side_matches(side, room_id, room):
    if side.get("any"): return True
    if "type" in side: return side["type"] == room_id
    fc = side.get("function_class")
    if fc is None: return False
    return (room or {}).get("function_class") in ([fc] if isinstance(fc, str) else fc)

def opening_rule(a_type, b_type):
    """The grammar rule governing an opening between two room types. Unordered."""
    g = grammar()
    a_room = C["rooms"].get(a_type)
    b_room = C["rooms"].get(b_type)
    for rule in (g.get("pair_rules") or []) + (g.get("class_defaults") or []) + [g["default"]]:
        w = rule.get("when")
        if w is None: return rule
        if (_side_matches(w["a"], a_type, a_room) and _side_matches(w["b"], b_type, b_room)) or \
           (_side_matches(w["a"], b_type, b_room) and _side_matches(w["b"], a_type, a_room)):
            return rule
    return g["default"]

# the kits state the graduation; this is where it finally reaches a record
_RANK_HEIGHT_IN = {"principal": 84.0, "secondary": 80.0, "service": 78.0,
                   "chamber": 80.0, "closet": 78.0}

def _pack_rule(pack_id, quantity):
    """The named rule out of a proportion pack, read from the pack itself."""
    for sub in ("systems", "modules", "orders", "overlays"):
        p = f"{ROOT}/proportions/{sub}/{pack_id}.json"
        if not os.path.exists(p): continue
        d = json.load(open(p))
        for r in (d.get("derived_rules") or []):
            if r.get("quantity") == quantity:
                return d, r
    return None, None

def _pack_width_ft(rule, storey_ft):
    """Where a proportion pack states this opening's width, the pack wins and the grammar's
    band only clamps it. The corpus deriving its own dimension always beats a band fitted
    by hand -- that is the whole argument of the proportion layer.

    The pack's EXPRESSION is read and evaluated, never restated here. opening-proportion
    gives `storey_height / 3.5` for the entry leaf, with Palladio ch. XXV quoted beside it;
    copying that constant into this file would be the same fact in two places, which is the
    duplication the proportion layer exists to remove."""
    spec = rule.get("derive_width_from")
    if not spec or not storey_ft: return None
    pack, r = _pack_rule(spec.get("pack"), spec.get("quantity"))
    if not r: return None
    try:
        PE = _mod("proportion_engine", f"{ROOT}/build/proportion_engine.py")
        val_in = PE.evaluate_expr(r["expression"], {"storey_height": storey_ft * 12.0})
    except Exception:
        return None
    band = r.get("range")
    if isinstance(band, list) and len(band) == 2:
        val_in = min(band[1], max(band[0], val_in))
    return round(val_in / 12.0, 2)

def derive_openings(plan, style, log):
    """Give every declared door a width, a type and a rank, and every window a real count
    and width. Runs after symmetrise_doors so both directions of one door agree."""
    g = grammar()
    idx = {r["id"]: r for lv in plan["levels"] for r in lv["rooms"]}
    lvl_of = {r["id"]: lv for lv in plan["levels"] for r in lv["rooms"]}
    editorial = {}

    # doors, resolved once per PAIR and written to both records: a door disagreeing with
    # itself across its two rooms is a corruption `plan_check`'s DECLARED layer reports
    # (WP-6.4). This comment named the drawn layer for a package and a half and the drawn
    # layer never checked it -- nothing in the repo compared a door's two records until the
    # check was actually written. Deciding once per pair here is what keeps a COMPOSED plan
    # clean; the check is what catches a hand-authored or hand-edited one.
    decided = {}
    for r in list(idx.values()):
        for d in (r.get("doors") or []):
            to = d["to"]
            key = tuple(sorted((r["id"], to)))
            if key in decided: continue
            a_t = r["type"]
            b_t = "exterior" if to == "exterior" else (idx.get(to, {}).get("type"))
            if b_t is None: continue
            rule = opening_rule(a_t, b_t)
            lo, hi = rule["opening"]["width_band_ft"]
            # storey height is floor to floor: the ceiling plus its assembly, which is
            # the datum Palladio's rule is stated against (see the pack's own note)
            storey = (lvl_of[r["id"]].get("floor_to_ceiling_ft") or 9.0) + 1.0
            w = _pack_width_ft(rule, storey)
            if w is None:
                w = round((lo + hi) / 2.0, 2)
                editorial[rule["id"]] = editorial.get(rule["id"], 0) + 1
            w = round(min(hi, max(lo, w)), 2)
            rank = rule["opening"]["rank"]
            decided[key] = {"width_ft": w, "type": rule["opening"]["type"], "rank": rank,
                            "height_ft": round(_RANK_HEIGHT_IN[rank] / 12.0, 2),
                            "rule": rule["id"]}
    for r in idx.values():
        for d in (r.get("doors") or []):
            spec = decided.get(tuple(sorted((r["id"], d["to"]))))
            if not spec: continue
            # a door the parti or attach_garage already dimensioned keeps its own numbers:
            # an authored figure outranks a derived one, always
            d.setdefault("width_ft", spec["width_ft"])
            d.setdefault("type", spec["type"])
            d.setdefault("rank", spec["rank"])
            d.setdefault("height_ft", spec["height_ft"])

    if editorial:
        top = sorted(editorial.items(), key=lambda kv: -kv[1])[:4]
        log.append("JUDGMENT: " + str(sum(editorial.values())) + " door(s) took the midpoint of "
                   "an EDITORIAL band from openings/grammar.json because no proportion pack "
                   "states that opening's width — " +
                   ", ".join(f"{n}x {rid}" for rid, n in top) +
                   ". Each band is a reading of this corpus's own room prose, quoted in the "
                   "rule's `basis`, and none of it is sourced (OQ 18's form).")

    # windows. The count is the room's own glazing_fraction against the wall it is on --
    # a derivation the corpus has carried on 53 of 60 records and never once run.
    derived = capped = sized = 0
    _, wrule = _pack_rule("opening-proportion", "window_width_from_room")
    _, prule = _pack_rule("opening-proportion", "opening_height_over_width")
    PE = _mod("proportion_engine", f"{ROOT}/build/proportion_engine.py")
    for lv in plan["levels"]:
        ch = lv.get("floor_to_ceiling_ft") or 9.0
        for r in lv["rooms"]:
            wins = r.get("windows") or []
            if not wins: continue
            rt = C["rooms"].get(r["type"], {})
            gf = (rt.get("daylight") or {}).get("glazing_fraction")
            head = r.get("window_head_ft") or (ch - 1.2)
            # THE WINDOW FROM THE ROOM IT LIGHTS. opening-proportion's own note calls this
            # "THE RULE MODERN PRACTICE HAS ENTIRELY LOST", derives 42 2/3 in for a 16 ft
            # room, and has never once been run: every window this composer emitted was
            # 3.2 ft wide whatever room it lit.
            room_w_in = (r.get("width_ft") or 12) * 12.0
            unit_w_pack = unit_h_pack = None
            if wrule:
                try:
                    v = PE.evaluate_expr(wrule["expression"], {"room_width": room_w_in})
                    lo_w, hi_w = wrule.get("range") or [20.0, 72.0]
                    unit_w_pack = round(min(hi_w, max(lo_w, v)) / 12.0, 2)
                except Exception:
                    unit_w_pack = None
            if unit_w_pack and prule:
                try:
                    ratio = PE.evaluate_expr(prule["expression"], {})
                    unit_h_pack = round(unit_w_pack * float(ratio), 2)
                except Exception:
                    unit_h_pack = None
            for win in wins:
                if unit_w_pack and win.get("width_ft") in (None, 3.2):
                    win["width_ft"] = unit_w_pack
                    # the head is where the corpus puts it; the sill follows from the
                    # canonical proportion rather than from a habit
                    if unit_h_pack:
                        win["height_ft"] = min(unit_h_pack, round(head - 1.5, 1))
                    sized += 1
                unit_w = win.get("width_ft") or 3.2
                unit_h = win.get("height_ft") or max(3.0, round(head - 2.5, 1))
                wall = win.get("wall")
                run = (r.get("width_ft") or 12) if wall in ("N", "S") else (r.get("length_ft") or 14)
                if isinstance(gf, list) and len(gf) == 2 and unit_w and unit_h:
                    target = ((gf[0] + gf[1]) / 2.0) * run * ch
                    n = int(round(target / (unit_w * unit_h)))
                    n = max(1, n)
                    derived += 1
                else:
                    n = win.get("count") or 1
                # minimum_solid_between_openings (sash-light: opening_width * 1.4) bounds
                # how many units a wall can actually carry, whatever the daylight asks for
                cap_n = max(1, int((run + unit_w * 1.4) // (unit_w * 2.4)))
                if n > cap_n:
                    n = cap_n
                    capped += 1
                win["count"] = n
    if sized:
        log.append(f"{sized} window unit(s) sized from the room they light, by "
                   f"opening-proportion's `window_width_from_room` (room_width / 4.5) and its "
                   f"canonical height-over-width of 13/6 — the rule that pack's own note calls "
                   f"'THE RULE MODERN PRACTICE HAS ENTIRELY LOST'. Nothing in this system had "
                   f"ever run it: every composed window was 3.2 ft wide in every room.")
    # --- WP-7.3 (OQ 91): every window unit gets a ROLE from the grammar and a KIND from the
    # kit, and where the kit has not been authored it gets no kind at all.
    roled = kinded = kindless = 0
    kinds = {}
    for r in idx.values():
        rt = C["rooms"].get(r["type"]) or {}
        for win in (r.get("windows") or []):
            rule = window_rule(r["type"], "exterior")
            role = (rule.get("unit") or {}).get("role")
            if role in (None, "none"):
                continue
            win["role"] = role
            win["role_rule"] = rule["id"]
            roled += 1
            kind, whence, refusal = kit_window_type(plan.get("style"))
            if kind:
                win["unit_type"] = kind
                if whence and whence != plan.get("style"):
                    win["unit_type_from"] = whence
                kinds[kind] = kinds.get(kind, 0) + 1
                kinded += 1
            else:
                # THREE-STATE, and this is the load-bearing half of the ruling
                win["unit_type_unresolved"] = {
                    "reason": refusal or (f"kits/{plan.get('style')}.kit.json states no "
                                          f"window_type, so this corpus does not know what "
                                          f"kind of sash this style uses")}
                kindless += 1
    if roled:
        log.append(f"{roled} window unit(s) given a ROLE by openings/window-grammar.json — "
                   f"which opening is an ordinary lit window, a high transom band, a borrowed "
                   f"light or a bay. The grammar decides the role and the kit decides the sash "
                   f"kind; neither may state the other's (OQ 91).")
    if kinded:
        log.append(f"{kinded} unit(s) given a sash kind by the style's own kit: "
                   + ", ".join(f"{k} x{v}" for k, v in sorted(kinds.items())) + ".")
    if kindless:
        log.append(f"JUDGMENT WITHHELD: {kindless} window unit(s) carry a role and NO "
                   f"`unit_type`, because this style's kit states no window_type. "
                   f"`window_type` is drafted on 39 of 159 kits. Drawing them as double-hung "
                   f"because that is the commonest would be a guess wearing a fact.")
    if derived:
        log.append(f"Window counts on {derived} wall(s) derived from each room's own "
                   f"daylight.glazing_fraction band against that wall's area, and bounded by "
                   f"sash-light's minimum_solid_between_openings"
                   + (f" ({capped} wall(s) bounded by the solid rather than by daylight)" if capped else "")
                   + ". Before WP-6.2 every window in every composed plan was 3.2 ft wide, "
                     "two to a wall, in every room and every style.")
    return plan

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

# OQ 34 — the decision log, structured, WITHOUT the prose being replaced.
#
# The workbench's DecisionLogEntry renders {field, chose, because}; this log is prose lines, so
# the component has been rendering a shape the data does not have. The entry recorded it rather
# than fixing it because there is a judgment inside: which lines are DECISIONS the composer took
# and which are narration of what it did. Ruled 26 Aug 2026 — structure it and mark the judgment.
#
# THE RULE USED, stated so it can be argued with. The log already classifies itself: a line the
# composer meant as a decision carries a prefix it wrote itself, and those prefixes are the
# corpus's own vocabulary, not a taxonomy imposed here. Everything else is an assumption the
# composer took where the brief was silent — which the result's own `how_to_read_this` already
# calls "the assumptions, not facts", so it is a decision too, of a quieter kind.
#
# WHAT IS NOT DONE, deliberately: `field` and `chose` are DERIVED from the sentence and are absent
# where the sentence does not carry them. They are not re-authored at the 25 call sites, because
# re-writing those sentences would change prose that tests and reports quote, and because a
# derived value that says it is derived is honest where a re-parsed one presented as authored
# would not be. Every entry carries `derived: true` and its original `statement` verbatim; nothing
# reading `decisions` sees any change at all.
_DECISION_KINDS = (
    ("JUDGMENT:", "judgment"),
    ("REFUSED:", "refusal"),
    ("AUTHORED:", "authored"),
    ("NOT SOLVED:", "unsolved"),
    ("KNOWN FINDING, not a defect:", "disclosure"),
)

# The log's own vocabulary, read off it rather than imagined. Across every brief in `briefs/`
# the composer emits 58 distinct sentences from these fourteen shapes; each pattern names the
# BRIEF FIELD or plan quantity the decision settled, and the groups give `chose`. A sentence
# matching nothing keeps `field: null` and `chose: null` rather than being force-fitted -- a
# derived value that is wrong is worse than one that is absent, and the prose is right there.
_DECISION_PATTERNS = (
    (r"^(\d+) garage bays placed as a dependency off (?P<a>[^,(]+)", "garage_bays", r"\1 bays off \g<a>"),
    (r"^the brief asks for (\d+) garage bays", "garage_bays", r"not placed (\1 asked for)"),
    (r"^Ceiling heights (?P<a>[\d.]+) ft ground and (?P<b>[\d.]+) ft above", "ceiling_heights",
     r"\g<a> ft ground, \g<b> ft above"),
    (r"^Dropped optional rooms to reach the area target: (?P<a>[^.]+)", "optional_rooms", r"dropped \g<a>"),
    (r"^Dropped (?P<a>.+?): the brief excludes", "optional_rooms", r"dropped \g<a>"),
    (r"^the brief requires a (?P<a>[a-z ]+) and this diagram has no place", "required_room", r"\g<a>: not added"),
    (r"^at a (\d+) sf target this diagram's own area weights make (?P<a>\d+) room", "room_areas",
     r"\g<a> room(s) outside their catalogue band"),
    (r"^Sized from the room catalogue.*?; (?P<a>[\d.]+) sf against a (?P<b>[\d.]+) sf target", "target_area_sf",
     r"\g<a> sf against \g<b> sf"),
    (r"^Kit's orientation_rule \((?P<a>[^)]+)\)", "orientation_rule", r"from \g<a>'s kit"),
    (r"^Kit leaves setback_rule open", "setback_rule", "left open"),
    (r"^Raised the window head in (?P<a>.+?) to (?P<b>[\d.]+) ft", "window_head_ft", r"\g<a> to \g<b> ft"),
    (r"^Shortened (?P<a>\d+) rooms that were not complaining, to give back (?P<b>\d+) sf", "room_lengths",
     r"\g<a> rooms, \g<b> sf returned"),
    (r"^Shortened (?P<a>.+?) to (?P<b>[\d.]+) ft;", "room_length_ft", r"\g<a> to \g<b> ft"),
    (r"^Widened (?P<a>\d+) rooms to take their furniture", "room_widths", r"\g<a> rooms"),
    (r"^Widened (?P<a>.+?) from (?P<b>[\d.]+) to (?P<c>[\d.]+) ft", "room_width_ft", r"\g<a>: \g<b> to \g<c> ft"),
    (r"^Widened (?P<a>.+?) to the (?P<b>[\d.]+) ft floor", "room_width_ft", r"\g<a> to the \g<b> ft floor"),
    # WP-6.2. Three lines the composer did not use to emit at all, because it took none of
    # these decisions: every door was `{"to": id}` and every window 3.2 ft wide, twice.
    (r"^(?P<a>\d+) door\(s\) took the midpoint of an EDITORIAL band", "door_widths",
     r"\g<a> from an editorial band"),
    (r"^(?P<a>\d+) window unit\(s\) sized from the room they light", "window_widths",
     r"\g<a> sized from their rooms"),
    (r"^Window counts on (?P<a>\d+) wall\(s\) derived from each room's own", "window_counts",
     r"\g<a> walls from glazing fraction"),
)

def structure_decisions(lines):
    """Prose decision lines -> {kind, field, chose, because, statement}, prose kept verbatim.

    OQ 34. The workbench's DecisionLogEntry renders {field, chose, because} and this log was
    prose, so the component has been rendering a shape the data does not have. The entry recorded
    it rather than fixing it because there is a judgment inside -- which lines are DECISIONS the
    composer took and which are narration. Ruled 26 Aug 2026: structure it, and mark the judgment.

    THE RULE USED, stated so it can be argued with. The log already classifies itself: a line the
    composer meant as a decision carries a prefix it wrote itself -- JUDGMENT, REFUSED, AUTHORED,
    NOT SOLVED, KNOWN FINDING -- and those are the corpus's own words, not a taxonomy imposed
    here. Everything else is an assumption taken where the brief was silent, which the result's
    own `how_to_read_this` already calls "the assumptions, not facts", so it is a decision too, of
    a quieter kind. That is the whole judgment, and it is one line of code: prefix or no prefix.

    WHAT IS DELIBERATELY NOT DONE. `field` and `chose` are DERIVED and say so. They are not
    re-authored at the twenty-five call sites, because rewriting those sentences would change
    prose that tests and reports quote. Every entry carries its `statement` verbatim and
    `derived: true`; nothing reading `decisions` sees any change at all. A sentence outside the
    table keeps null fields rather than a forced guess."""
    import re as _re
    out = []
    for line in lines:
        kind, rest = "assumption", line
        for prefix, k in _DECISION_KINDS:
            if line.startswith(prefix):
                kind, rest = k, line[len(prefix):].strip()
                break
        field = chose = None
        for pat, fld, tmpl in _DECISION_PATTERNS:
            m = _re.search(pat, rest)
            if m:
                field = fld
                try:
                    chose = m.expand(tmpl).strip() if "\\" in tmpl or "\\g" in tmpl else tmpl
                except Exception:
                    chose = None
                break
        # The reason clause, taken from the connective the sentence actually uses. The marker is
        # KEPT in the text where it carries the sense ("to reach the back of the room" is the
        # reason; "the back of the room" is not), which is why these are matched rather than
        # split blindly. A sentence with no connective keeps `because: null` -- the statement is
        # right there and carries the whole thought.
        because = None
        for marker in (" because ", " so that ", " so it ", " so the ",
                       ", taken from ", " to reach the ", " to give back ",
                       " for its room type", " \u2014 ", " -- ", "; the ", ": the "):
            if marker in rest:
                tail = rest.split(marker, 1)[1].strip().rstrip(".")
                lead = marker.strip(" ,;:")
                because = (f"{lead} {tail}" if lead.replace(" ", "").isalpha() and
                           lead not in ("the",) else tail) or None
                if because:
                    break
        out.append({"kind": kind, "field": field, "chose": chose, "because": because,
                    "statement": line, "derived": True})
    return out

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
            elif f["layer"] == "style" and f.get("rule") == "circulation_parti" and "ft wide" in f["statement"]:
                # THE PASSAGE FLOOR THE STYLE STATES, WHICH THE CATALOGUE'S DOES NOT COVER
                # (WP-9.1). The branch above widens a room to `rooms/<type>.json`'s own
                # `width_ft` floor, and for a centre passage that floor is 6 ft -- correct for
                # the northern vernacular passage the record describes, and 4 ft short of what
                # tidewater-georgian's own kit asks for. This brief was composing a 7.9 ft
                # passage and being convicted of `passage-that-is-a-corridor` (fatal for a
                # formal centre-passage style), which disqualified all three NATIVE partis and
                # handed a Tidewater Georgian brief to a side-hall townhouse -- WP-4.5's
                # deleted sentence walking back in. Nothing had ever supplied
                # `passage_clear_width_ft`, so the fault could not fire and the defect was
                # three phases old.
                #
                # The figure is parsed from the finding rather than re-derived here, the same
                # way the furniture branch above reads its own: the style layer resolved the
                # cascade and this must not resolve it a second time and disagree.
                try:
                    need = float(f["statement"].split(" own kit states a passage of ")[1].split("-")[0])
                except Exception:
                    continue
                if 0 < r.get("width_ft", 0) < need:
                    log.append(f"Widened {r.get('name') or rid} from {r['width_ft']} to {need:g} ft — "
                               f"the floor this style's own kit states, not the catalogue's vernacular one.")
                    r["width_ft"] = need; moved = True
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
    notes, lot_note = [], None
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
            # Kept by name, not by position. compose() published notes[-1] as the reason a
            # candidate was dropped, and by the time the drop happens the LAST note is
            # usually "at N bays this diagram is at the width it grows to" -- because an
            # infeasible lot forces bays past mx, which fires that test every time. Measured
            # on a 30 ft lot: 4 of 4 dropped candidates published a reason that was not why
            # they were dropped, into the record the MCP tool and the workbench both read.
            lot_note = (f"This diagram needs at least {mn} bays ({mn*bm:.0f} ft) and the lot clears only "
                        f"{usable:.0f} ft usable width after side setbacks. It does not fit this lot.")
            notes.append(lot_note)
    bays = max(mn, min(mx, round(math.sqrt(a0 * 1.6) / bm)))
    width = round(bays * bm, 1)
    depth = round(a0 / width, 1) if width else 0
    # `failed_tests` is NOT len(notes). Two of the notes above are FAILED TESTS of the plan;
    # the other two are statements about the LOT -- "the lot caps this diagram at 4 bays" is
    # not something the plan did wrong, and the buildability axis was charging 2.5 points of
    # 100 for it. Reachable on briefs/bungalow-small.json today, where it moved a candidate
    # against a 1.6-point margin. Counted here, where the tests are, rather than inferred
    # downstream from a list length that has never meant what the count needed.
    failed = 0
    if depth > 38:
        failed += 1
        notes.append(f"Footprint {width} x {depth} ft — deeper than about 38 ft, which needs a double-pile section and will leave interior rooms unlit.")
    if bays >= mx and a0 / (bays * bm) > 34:
        failed += 1
        notes.append(f"At {bays} bays this diagram is at the width it grows to; further area wants a dependency, not more room.")
    return {"level_0_area_sf": round(a0), "bays": bays, "bay_module_ft": bm,
            "footprint_ft": [width, depth], "notes": notes, "lot_infeasible": lot_infeasible,
            "lot_note": lot_note, "tests_run": FOOTPRINT_TESTS, "tests_failed": failed}

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
        fp = footprint(plan, parti)
        if fp["lot_infeasible"]:
            # WP-2.4 acceptance: a candidate that cannot physically fit the stated lot is
            # never returned, however well it would otherwise have scored — dropped here,
            # not merely outscored, so it can never appear even as the only candidate.
            dropped_lot.append({"parti": pick["parti"], "parti_name": parti["name"],
                                "why": fp.get("lot_note") or fp["notes"][-1]})
            continue
        # `demerits` is the old lower-is-better total, kept because it is a real quantity and
        # because a report or a commit written before this change quotes it. It no longer
        # ranks anything: see SCORE_AXES above for what does, and why a sum with no ceiling
        # could not honestly be published under the word "score".
        demerits = round(score(res) + (60 if miss > tol else 0) - pick["fit"] * NATIVITY_W, 1)
        card = score_candidate(res, plan, brief, pick["fit"], fp, miss, tol)
        out.append({
            "parti": pick["parti"], "parti_name": parti["name"],
            "demerits": demerits, "style_fit": pick["fit"], **card,
            "counts": counts, "area_sf": round(area), "area_miss_pct": round(miss * 100, 1),
            "footprint": fp,
            "trades_away": parti["trades_away"],
            "why_this_diagram": pick["why"],
            "decisions": log + _summarise(rlog),
            # The same lines, structured (OQ 34). The prose list above is unchanged and stays
            # the thing to read; this is what the workbench's DecisionLogEntry renders.
            "decisions_structured": structure_decisions(log + _summarise(rlog)),
            "worst": [{"severity": f["severity"], "layer": f["layer"], "statement": f["statement"]}
                      for f in res["findings"] if f["severity"] in ("fatal", "serious")][:8],
            "plan": plan})
        if on_candidate:
            on_candidate({k: v for k, v in out[-1].items() if k != "plan"})
    # Fatal-free first, then highest score. The two keys are separate on purpose and the
    # first one is the one that must not be traded away: a plan carrying a fatal never
    # displaces a clean one from the returned set, however native its diagram and however
    # well it scores. That is the whole of WP-4.5's NATIVITY_W guarantee, and it lives HERE
    # rather than in the score, which is why the score does not need to refuse to exist on a
    # fatal. Candidates with an equal fatal count are then ordered by score, disqualified
    # ones included -- four plans that all carry a fatal still differ, and a reader facing
    # that set needs the difference more than anyone.
    #
    # Tie-break by parti id for the same reason pick_partis does: the score is rounded to 1dp
    # and built from integer counts, so collisions are reachable — especially between two
    # diagrams from the same fit tie group, which share a fidelity axis. A stable sort would
    # then fall back to insertion order, and the slice below would be deciding again.
    # Determinism here must not be borrowed from the previous stage.
    out.sort(key=lambda c: (c["counts"].get("fatal", 0),
                            -(c["score"] if c["score"] is not None else -1e9),
                            c["demerits"], c.get("parti") or ""))
    # `score` is None only in the unreachable no-evidence case above; the sentinel keeps such
    # a candidate last within its fatal group rather than sorting None against a float.
    # The axis definitions ride on the RESULT, not on every candidate. They are constant
    # across a run, and repeating `what` and `score_of` in eight rows per candidate added
    # 2,361 bytes of pure duplication, measured on the real tdl_compose payload for both
    # shipped briefs, to something the MCP tool bills a model for. (An earlier version of
    # this comment guessed "about 1.4 KB" -- 69% under. Figures here are measured.)
    score_model = {"of": 100, "axes": [{"axis": n, "weight": w, "what": t} for n, w, t in SCORE_AXES]}
    result = {"brief": brief.get("id") or brief.get("name"), "style": brief["style"],
            "score_model": score_model,
            "target_area_sf": brief["target_area_sf"], "bedrooms": brief.get("bedrooms", 3),
            "candidates": out[:candidates],
            "how_to_read_this": [
              "Score is out of 100 and HIGHER IS BETTER. It is not a total of what is wrong: it is a weighted composite of eight axes, each one a share of its own denominator -- what came back clean out of what was actually checked -- so a bigger house is not penalised for being checked more times. score_axes carries every axis, its weight, its share and the denominator that share was taken over.",
              "An axis nothing could be evaluated on has its WEIGHT DROPPED and the total renormalised over the rest, never scored as a pass and never as a zero. score_weight_unevaluated says how much of the hundred that was, so a score computed over 94 points of evidence cannot be read as one computed over 100.",
              "A fatal finding DISQUALIFIES a candidate, and that is carried beside the score rather than inside it: `disqualified` is true and `disqualified_because` says so in words. A disqualified candidate never outranks a clean one whatever it scores -- that is enforced by the ordering, not by the number -- and its score is not a case for building it. It is still scored because whole sets come back disqualified on styles the fault corpus cannot clear, and four plans that all carry a fatal still differ.",
              "Candidates are RETURNED fatal-free first and then by score, so a plan carrying a fatal never displaces a clean one from the set even where its fidelity would outscore it. How the ones that came back are then ORDERED for reading is a separate choice -- by score, by nativity, or fatal-first -- and the reading order is named above them.",
              "demerits is the old lower-is-better total -- 100 a fatal, 8 a serious, 1 a minor, less 20 a point of fidelity. It is kept because it is a real quantity and because earlier reports quote it. It ranks nothing now.",
              "trades_away is the honest part. Every diagram gives something up, and the one that scores best is not always the one you want.",
              "decisions lists what the composer chose where the brief was silent. Read it — those are the assumptions, not facts.",
              "decisions_structured is the same list with a kind on each line (judgment, refusal, authored, unsolved, disclosure, assumption) and field/chose/because DERIVED from the sentence — absent where the sentence does not carry them, and marked derived so nothing reads them as authored.",
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
        head = f"score {c['score']} of 100" if c["score"] is not None else "NOT SCORED"
        dq = "   DISQUALIFIED" if c.get("disqualified") else ""
        print(f"\n  {i}. {c['parti_name']}   {head}{dq}   "
              f"fatal {cc.get('fatal',0)}  serious {cc.get('serious',0)}  minor {cc.get('minor',0)}")
        for k in ("disqualified_because", "score_unscored_because"):
            if c.get(k): print(f"     ! {c[k]}")
        for ax in c["score_axes"]:
            pts = f"{ax['points']:>5.1f} / {ax['weight']:<2}" if ax["points"] is not None \
                else f"{'--':>5} / {ax['weight']:<2}"
            share = f"{ax['share'] * 100:.0f}%" if ax["share"] is not None else "not evaluated"
            unj = f"  ({ax['unjudged']} unjudged)" if ax.get("unjudged") else ""
            print(f"     {pts}  {ax['axis']:<13} {share:>13}  {ax.get('denominator') or ''}{unj}")
        if c["score_weight_unevaluated"]:
            print(f"     scored over {c['score_weight_evaluated']} of 100 points of evidence; "
                  f"{c['score_weight_unevaluated']} could not be evaluated")
        print(f"     {c['area_sf']} sf ({c['area_miss_pct']}% off target) · footprint {c['footprint']['footprint_ft'][0]} x {c['footprint']['footprint_ft'][1]} ft in {c['footprint']['bays']} bays")
        print(f"     why: {'; '.join(c['why_this_diagram'][:2])}")
        print(f"     trades away: {c['trades_away'][:170]}")
        for n in c["footprint"]["notes"]: print(f"     ! {n}")
        for w in c["worst"][:4]: print(f"     [{w['severity']}] {w['statement'][:120]}")
    print("\n  " + "\n  ".join(res["how_to_read_this"]) + "\n")

if __name__ == "__main__":
    main()
