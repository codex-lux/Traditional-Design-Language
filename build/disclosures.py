#!/usr/bin/env python3
"""disclosures.py — what the placement gave up, in one place, for every surface that draws it.

WP-11.1, from `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` findings J1, J2, J3, J5,
F1 and G1. The sheet said

    PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS

over a placement whose own solver record carried SIXTEEN declared exterior walls set aside to
reach feasibility — both ends of the centre passage among them — `objective: null`, and "best of
1 hard-valid placements". Twenty-seven of thirty-five declared window units were not drawn and no
line said so. Thirty upper wall lines landed on no wall below and no line said so. Each of those
facts was already IN the record the sheet was rendering; nothing read them.

WP-6.4's lesson, one layer out: *"a drawing set is ONE building"*, and a reader who cannot see
what the placement gave up cannot tell a proof from a compromise. **Relaxed is not proved.**

    from disclosures import banner
    lines = banner(placed_plan, undrawable=..., diverged=..., unlocated=...)
    # -> [{"id": ..., "text": ..., "tone": "iron"|"copper"|"verd", "detail": [...]}, ...]

ONE SPELLING, TWO SURFACES. `build/render_plan.py` draws these lines on the plate; the workbench
gets the same list through `core.placement_summary` and renders it in the disclosure strip, so the
app displays what Python computed rather than re-deriving it in JavaScript. The three lines the
renderer already owned (undrawable doors, diverged rooms, unlocated relaxation marks) are computed
from ITS derivation and passed in — this module does not re-derive them, because a second
derivation of a drawn fact is how `openings.required_wall_ft` came to be spelled three times.

WHAT THIS MODULE MAY NOT DO. It may not decide anything, and it may not soften anything. Every
line here is a count already in the record, printed. If a number is absent from the record the
line is ABSENT — never a zero, because a zero here reads as "nothing was given up".
"""
from __future__ import annotations

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The tones the plate paints these in; the app maps them to its own tokens. `iron` is the
# sheet's alarm red, `copper` its warning, `verd` its green.
IRON, COPPER, VERD = "iron", "copper", "verd"


def _plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


# ---------------------------------------------------------------- the individual disclosures
def engine_line(plan):
    """Which engine placed this, and — new in WP-11.1 — AGAINST HOW MUCH of the record.

    The old line asserted the proof was against "the record's declared facts". On the shipped
    Tidewater plan sixteen of those facts had been set aside to reach feasibility. A proof
    against a relaxed hard set is a true statement about a different question, printed where a
    reader will take it for the answer to this one.

    AND THE ENGINE'S NAME IS NOT A PROOF (WP-13.2). The green line printed on
    `engine == "cp-sat"` alone, and the gate found it over a record reading
    `status: FEASIBLE — kept polish from the heuristic hint (best of 2 hard-valid placements)`,
    `objective: 518.9`, the compositional phase having run for four seconds of a forty-second
    budget. What CP-SAT proved there is that the hard set is satisfiable; what it did not prove
    is that this placement is the best one, and a FEASIBLE truncation is exactly the kind of
    placement a reader takes for a proof when the line says PROVED. So the green line prints
    ONLY where the solver's own status begins OPTIMAL, its objective was evaluated, and no
    declared wall was set aside. Anything else prints the status the record has, verbatim, in
    copper; where the objective is null, `objective_not_run` prints beside it. A status the
    record does not carry is UNJUDGED, not proved."""
    s = (plan.get("geometry_report") or {}).get("solver") or {}
    engine = s.get("engine")
    if not engine:
        return None
    if engine == "cp-sat":
        status = str(s.get("status") or "")
        proved = status.upper().startswith("OPTIMAL") and s.get("objective") is not None
        dropped = len(s.get("downgraded_wall_pins") or [])
        held = None
        if dropped:
            total = _declared_wall_count(plan)
            kept = (total - dropped) if total is not None else None
            held = (f"{kept} OF THE RECORD'S {total} DECLARED EXTERIOR WALLS"
                    if kept is not None
                    else f"THE RECORD'S DECLARED EXTERIOR WALLS BUT {dropped}")
        detail = {"status": s.get("status"), "objective": s.get("objective"),
                  "downgraded_wall_pins": dropped}
        if proved and dropped:
            return {"id": "engine", "tone": COPPER, "detail": detail,
                    "text": f"PLACEMENT PROVED (CP-SAT) AGAINST {held}"}
        if proved:
            return {"id": "engine", "tone": VERD, "detail": detail,
                    "text": "PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS"}
        what = status.upper() if status else "SOLVER STATUS NOT RECORDED"
        return {"id": "engine", "tone": COPPER, "detail": detail,
                "text": f"PLACEMENT BY CP-SAT, NOT PROVED AT THE OPTIMUM — {what}"
                        + (f" — AGAINST {held}" if held else "")}
    reason = s.get("reason")
    tail = f" — {reason.upper()}" if reason and reason != "requested" else ""
    return {"id": "engine", "tone": COPPER,
            "text": f"PLACEMENT SEARCHED, NOT PROVED — HILL-CLIMB{tail}"}


def _declared_wall_count(plan):
    """How many exterior-wall declarations the record makes, so the engine line can say how
    many survived. Counts a room-and-side pair, which is the unit `downgraded_wall_pins`
    names (`L0 drawing S`)."""
    n = 0
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            n += len(r.get("exterior_walls") or [])
    return n or None


def walls_set_aside(plan):
    """The pins the CP engine proved could not co-hold, and dropped. `refinements` says of each
    whether it was individually re-proven or carried from the conflict core; the plate has room
    for the count and the rooms, and the full account rides in the record."""
    s = (plan.get("geometry_report") or {}).get("solver") or {}
    pins = s.get("downgraded_wall_pins") or []
    if not pins:
        return None
    names = {}
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            names[r["id"]] = r.get("name") or r["id"]
    rooms, seen = [], set()
    for pin in pins:
        # `L0 drawing S` -> level, room id, side
        m = re.match(r"^L(\d+)\s+(\S+)\s+(\S+)$", pin)
        rid = m.group(2) if m else pin
        if rid not in seen:
            seen.add(rid)
            rooms.append(names.get(rid, rid))
    shown = ", ".join(rooms[:4])
    more = f" (+{len(rooms) - 4} MORE)" if len(rooms) > 4 else ""
    return {"id": "walls-set-aside", "tone": IRON, "detail": pins,
            "text": f"{_plural(len(pins), 'DECLARED EXTERIOR WALL').upper()} SET ASIDE TO REACH "
                    f"A PLACEMENT — {shown.upper()}{more}"}


def objective_not_run(plan):
    """CP-SAT's phase A proves the hard set; phase B carries every compositional term the
    corpus has. On the shipped Tidewater plan phase B timed out, so the drawn house is the
    first feasible one CP-SAT reached and NO term for the front, the axis, the mirror pair or
    the stack was evaluated on it. `objective: null` is the record of that and nothing read it.

    Only the CP engine can leave its objective unevaluated: the hill-climb's score IS its
    objective, summed for every candidate it looks at, so this line must never appear for it."""
    s = (plan.get("geometry_report") or {}).get("solver") or {}
    if s.get("engine") != "cp-sat" or s.get("objective") is not None:
        return None
    return {"id": "objective", "tone": COPPER,
            "text": "FIRST FEASIBLE PLACEMENT — THE COMPOSITIONAL OBJECTIVE DID NOT RUN, SO NO "
                    "TERM FOR THE FRONT, THE AXIS OR THE STACK WAS EVALUATED ON IT"}


def alternative_offered(plan):
    """The search's placement, offered beside a proof whose objective did not run.

    WP-11.8, the second half of `oq/a-proof-of-feasibility-is-not-a-proof-of-composition`: *"the
    bench draws both and labels both, and the plate says which it drew and why."* The line above
    says the objective did not run; this one says what the reader is being offered instead, and it
    exists as a SEPARATE line rather than a longer version of that one because a reader can face
    the first without the second — the alternative is not always computable, and it says so.

    **BOTH NUMBERS OR NEITHER.** The demerit score alone reads as "the search is 197 points
    better" and that is the misleading half: on `spec-builder-colonial` the search buys those
    points by violating sixteen hard facts the proof honours. `geometry._offer_the_alternative`
    records the pair and this prints the pair. A future editor shortening this line to fit should
    drop the line, not one of its numbers."""
    s = (plan.get("geometry_report") or {}).get("solver") or {}
    alt = s.get("alternative")
    if not alt:
        return None
    if alt.get("verdict") != "offered":
        return {"id": "alternative", "tone": COPPER,
                "text": ("THE SEARCH'S PLACEMENT COULD NOT BE COMPUTED FOR COMPARISON — "
                         + (alt.get("why") or "no reason recorded").upper())}
    return {"id": "alternative", "tone": COPPER,
            "detail": alt,
            "text": (f"THE SEARCH PLACES THIS HOUSE AT {alt['score']} DEMERITS AGAINST THIS "
                     f"DRAWING'S {alt['drawn_score']}, AND BREAKS "
                     f"{alt['hard_fact_violations']} DECLARED FACT(S) THIS ONE HOLDS "
                     f"({alt['drawn_hard_fact_violations']}) — A LOWER SCORE IS NOT ON ITS OWN "
                     f"A BETTER HOUSE")}


def windows_not_drawn(plan):
    """Declared window units the placement could not place, with the reasons grouped.

    `openings.py` has written `windows_unplaced` and a per-window `unplaced.reason` since
    WP-6.2 and a grep for a reader found none. Twenty-seven of thirty-five on the shipped
    Tidewater plan, on a house of a type recognised BY its fenestration."""
    op = plan.get("opening_report") or {}
    n = op.get("windows_unplaced")
    if not n:
        return None
    total, reasons = 0, {}
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            for w in r.get("windows", []) or []:
                units = int(w.get("count") or 1)
                total += units
                if w.get("unplaced"):
                    reasons[_group(w["unplaced"].get("reason"))] = \
                        reasons.get(_group(w["unplaced"].get("reason")), 0) + units
    why = ", ".join(f"{v} {k}" for k, v in sorted(reasons.items(), key=lambda kv: -kv[1]))
    return {"id": "windows", "tone": IRON, "detail": reasons,
            "text": f"{n} OF {total} DECLARED WINDOW UNIT(S) NOT DRAWN — {why.upper()}"}


# The reasons `openings.py` writes are sentences, which is right in a record and too long for a
# banner: the first version of this line ran 160 characters and was CLIPPED BY THE CANVAS EDGE on
# the first sheet it was drawn on -- a disclosure the sheet does not show, which is the failure
# this whole package is about, introduced by the package. The renderer wraps a long line now and
# a test holds every line inside the plate; these short forms keep the common ones to one row.
def _group(reason):
    """One bucket per KIND of reason, not per sentence.

    `openings.py` parameterises one of them -- *"1 of 2 unit(s) had no clear run left on this
    wall"* -- so a straight count-by-sentence produced the line "2 1 OF 2 UNIT(S) HAD NO CLEAR
    RUN…", which reads as a typo and is really two counts in a row. The leading clause is
    stripped before grouping, so every partial-placement reason lands in one bucket and the
    count in front of it is the disclosure's own."""
    r = (reason or "unstated").strip()
    m = re.match(r"^\d+ of \d+ unit\(s\) (had .*)$", r)
    if m:
        r = "some units " + m.group(1)
    return SHORT_REASON.get(r, r)


SHORT_REASON = {
    "some units had no clear run left on this wall": "no clear run left on the wall",
    "the placement puts this room on no such boundary wall": "on no such wall",
    "the wall has no clear run left beside its doors": "no clear run beside the doors",
    "one of the two rooms is not placed on this level": "a room not placed on this level",
}


def span_capacity(plan):
    """Clear spans over the framing capacity, from `geometry_report.span_capacity`.

    WP-11.12 (OQ 98's reporting half) put this line on the plate, spelled in `render_plan.py`;
    WP-13.2 moved it here so the bench's strip reads the same line, because a count the printed
    plate carries and the bench does not is the two-surfaces drift this module exists to stop.
    Three states, exactly as the plate printed them: `None` under `over_capacity` is COULD NOT
    EVALUATE (the construction catalogue could not be read), a count is a count, and the ZERO is
    printed too -- with the same caveat -- because "no span exceeds capacity" is exactly the claim
    the credited-across-the-plate reading can make falsely. Every published count is a FLOOR:
    `span_check` credits a bearing wall across the whole plate however short it runs."""
    gr = plan.get("geometry_report") or {}
    if not gr:
        return None
    sp = gr.get("span_capacity") or {}
    if sp.get("over_capacity") is None:
        return {"id": "span", "tone": COPPER,
                "text": "CLEAR SPAN NOT EVALUATED — THE CONSTRUCTION CATALOGUE COULD NOT BE "
                        "READ; NO SPAN IS CLAIMED CLEAR"}
    if sp.get("over_capacity"):
        return {"id": "span", "tone": IRON, "detail": sp,
                "text": f'{sp["over_capacity"]} CLEAR SPAN(S) OVER THE FRAMING CAPACITY, WORST '
                        f'{sp.get("worst_span_ft", 0):g} FT — AT LEAST THAT MANY: A BEARING LINE '
                        f'IS CREDITED ACROSS THE WHOLE PLATE HOWEVER SHORT THE WALL RUNS'}
    return {"id": "span", "tone": VERD,
            "text": "0 CLEAR SPAN(S) OVER THE FRAMING CAPACITY — AT LEAST NONE FOUND: A BEARING "
                    "LINE IS CREDITED ACROSS THE WHOLE PLATE HOWEVER SHORT THE WALL RUNS"}


def _count(v):
    """A tally `openings.py` writes as an int, or as the list or dict it counted -- read
    defensively, because the report is open by its own schema description and a reader that
    assumed one shape would crash the plate on the other."""
    if v is None:
        return 0
    if isinstance(v, dict):
        return sum(_count(x) for x in v.values())
    if isinstance(v, (list, tuple, set)):
        return len(v)
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def furniture_not_drawn(plan):
    """Furniture the pass refused, skipped or never reached, from `opening_report`.

    `openings.py` has counted these since WP-11.3 and `furniture.py` says "a skipped item is a
    verdict here, never a silence" -- and the counts were read by nothing: the gate measured 39
    silent refusals on the shipped Tidewater sheet (6 unplaced, 22 skipped, 11 not reached) and
    50 on the composer's own candidate. Three counts, named apart, because they mean three
    things: UNPLACED is an item the room could not hold, SKIPPED is an item a grammar rule
    declined to draw (the rule ids ride in `detail`), NOT REACHED is a catalogue item in a
    sanitary or service room that the fixture pass owns and did not place."""
    op = plan.get("opening_report") or {}
    unplaced = _count(op.get("furniture_unplaced"))
    skipped_raw = op.get("furniture_skipped")
    skipped = _count(skipped_raw)
    not_reached = _count(op.get("furniture_not_reached"))
    total = unplaced + skipped + not_reached
    if not total:
        return None
    why = ""
    if isinstance(skipped_raw, dict) and skipped_raw:
        why = " (" + ", ".join(f"{k} {_count(v)}" for k, v in
                               sorted(skipped_raw.items(), key=lambda kv: -_count(kv[1]))) + ")"
    return {"id": "furniture", "tone": COPPER,
            "detail": {"unplaced": unplaced, "skipped": skipped_raw, "not_reached": not_reached},
            "text": (f"{total} FURNITURE ITEM(S) NOT DRAWN — {unplaced} UNPLACED, {skipped} "
                     f"SKIPPED{why}, {not_reached} NOT REACHED").upper()}


def stacking(plan):
    """Declared stacks that do not land, from `geometry_report.stacking` -- the leaf's tally,
    never re-derived here.

    The plate printed cuts off the bay line, clear spans and undrawable doors from the report and
    omitted this block, so three declared stacks drawn clear of the room they name on the shipped
    Tidewater search sheet (landing over the stair among them) reached no line. A compromise is
    counted AND appears on the sheet (OQ 33). Three states: broken claims in iron, naming each
    pair; a tally with nothing broken in verd, with the count it holds; and an unjudged count
    beside either, because unjudged is not kept. A record with no claim takes no line -- there
    is nothing to disclose about a house that stacks nothing."""
    st = (plan.get("geometry_report") or {}).get("stacking") or {}
    if "claims" not in st:
        return None
    claims = _count(st.get("claims"))
    if not claims:
        return None
    broken = st.get("broken") or []
    unjudged = st.get("unjudged") or []
    kept = st.get("kept") or []
    tail = f"; {len(unjudged)} COULD NOT BE EVALUATED" if unjudged else ""
    if broken:
        pairs = ", ".join(f'{b.get("room")}/{b.get("over")}' for b in broken)
        return {"id": "stacking", "tone": IRON, "detail": st,
                "text": f"{len(broken)} OF {claims} DECLARED STACK(S) DRAWN CLEAR OF THE ROOM "
                        f"THEY NAME — {pairs.upper()}{tail}"}
    if not kept:
        return {"id": "stacking", "tone": COPPER, "detail": st,
                "text": f"{len(unjudged)} OF {claims} DECLARED STACK(S) COULD NOT BE EVALUATED — "
                        f"NONE IS KNOWN TO LAND"}
    return {"id": "stacking", "tone": VERD, "detail": st,
            "text": f"{len(kept)} OF {claims} DECLARED STACK(S) LAND ON THE ROOM THEY NAME{tail}"}


# The residual void below which a level is said to tile: the raster's own quantum is 0.01 sf
# and the gate's tiling row reads a level as tiled at or under this figure, so the plate and the
# gate agree on what a sliver is.
TILED_SF = 0.05


def residual_void(plan):
    """Floor inside no room, per placed level, from `geometry_report.type_facts.tiling` --
    `build/typefacts.py`'s measurement, never re-derived here.

    The prover's 0.97 coverage floor left 26.5 sf of the shipped Tidewater ground floor and
    48.8 sf of its upper floor inside no room, and `wall_bands` draws an interior wall only where
    two rooms SHARE an edge, so the powder room's south side was a 6 ft hole with nothing drawn
    across it and nothing on the plate said so. One line per level that carries a void, in iron,
    with the strip count and the worst strip; a verd line where every judged level tiles, because
    a reader must be able to tell evaluated-and-tiled from never-evaluated. ABSENT where the
    block is absent -- a record placed before the fact was measured says nothing, never zero."""
    tf = (plan.get("geometry_report") or {}).get("type_facts") or {}
    t = tf.get("tiling")
    if not t or not t.get("levels"):
        return None
    lines = []
    for lv in t["levels"]:
        sf = lv.get("uncovered_sf") or 0.0
        if sf <= TILED_SF:
            continue
        strips = [s for b in (lv.get("blocks") or []) for s in (b.get("strips") or [])]
        worst = max((s.get("area_sf") or 0.0) for s in strips) if strips else 0.0
        name = str(lv.get("id") or f"level {lv.get('level')}").upper()
        lines.append({"id": f"void-{lv.get('id') or lv.get('level')}", "tone": IRON,
                      "detail": lv,
                      "text": f"{sf:g} SF OF {name} IS NO ROOM — {_plural(len(strips), 'strip').upper()} "
                              f"OF FLOOR INSIDE NO ROOM, WORST {worst:g} SF, ACROSS WHICH NO "
                              f"WALL IS DRAWN"})
    if lines:
        return lines
    return [{"id": "void", "tone": VERD, "detail": t,
             "text": f"EVERY PLACED LEVEL TILES ITS BLOCK — {t.get('uncovered_sf', 0):g} SF IS "
                     f"NO ROOM"}]


def transfers(plan):
    """Upper wall lines landing on no wall below. Each is a transfer beam, and the count lives
    only inside an English sentence in `geometry_report.vertical`."""
    for line in ((plan.get("geometry_report") or {}).get("vertical") or []):
        m = re.match(r"^(\d+) upper wall line", line)
        if m and int(m.group(1)):
            return {"id": "transfers", "tone": COPPER,
                    "text": f"{m.group(1)} UPPER WALL LINE(S) LAND ON NO WALL BELOW — EACH IS A "
                            f"TRANSFER BEAM"}
    return None


def stack_plan_judgment(plan):
    """The chimney's plan size is a decision somebody still owes, drawn as though it were not.

    WP-12.9. `brick-course`'s rule for it is flagged `judgment: true` and its own note says why:
    twenty-two inches on the default coursing is between sizes, and a mason will build 18 or 27.
    THREE SURFACES DRAW THAT FIGURE AND UNTIL NOW ONLY TWO SAID SO -- `render_elevation.py` puts
    it in the plate's own legend, `build/scene.py` refuses to draw a solid at all and files a
    `judgment` naming it, and the PLAN drew a poche square whose tooltip read "22.0 in square"
    with nothing anywhere to say the number is not settled.

    IT IS READ AND NOT RE-DERIVED, which is this module's own standing rule: `build/threshold.py`
    put `stack_plan_judgment` and `stack_plan_basis` on each stack when it placed it, and this
    prints them. The BASIS travels with the flag because a judgment with no basis named is what
    this corpus forbids one step further than a figure with no source."""
    stacks = [sk for sk in ((plan.get("hearths") or {}).get("stacks") or [])
              if sk.get("stack_plan_judgment") and sk.get("stack_plan_in") is not None]
    if not stacks:
        return None
    sk = stacks[0]
    # CUT AT A CLAUSE AND MARK THE ELISION, which is WP-11.5's rule for exactly this: OQ 18's
    # first version cut a quoted basis at a hard 150 characters and landed mid-word 148 times.
    raw = (sk.get("stack_plan_basis") or "").strip()
    basis, elided = raw, False
    for stop in (";", ". ", ":"):
        if stop in basis:
            basis, elided = basis.split(stop, 1)[0], True
    basis = basis.strip().rstrip(".")
    return {"id": "stack-judgment", "tone": COPPER,
            "text": f'{_plural(len(stacks), "stack").upper()} DRAWN {sk["stack_plan_in"]}″ '
                    f'SQUARE — A JUDGMENT, NOT A MEASUREMENT'
                    + (f': {basis.upper()}' + (" …" if elided else "") if basis else '')}


def style_disagreement(plan, styles=None, partis=None):
    """The plate is judged against `plan.style` and nothing else, and the reader has no way to
    see when that disagrees with the plan's own title or with the parti it names.

    The sheet Lucas read in September 2026 was titled *"Tidewater Georgian, five bays,
    carefully planned"* and carried the style slot `palladian`: a different node, a different
    cascade, a different fault set. Three fields, three writers, no comparison.

    Two comparisons, both conservative — each fires only on a POSITIVE disagreement, never on
    a silence, because most plan titles name no style at all:
      · the title names a style that is not this plan's style;
      · the plan names a parti whose `styles` list does not include this plan's style.
    """
    style = plan.get("style")
    if not style:
        return None
    name = (plan.get("name") or "")
    out = []

    if styles:
        mine = ((styles.get(style) or {}).get("name") or "").lower()
        low = name.lower()
        if not (mine and mine in low):
            for sid, rec in styles.items():
                if sid == style:
                    continue
                other = (rec.get("name") or "").lower()
                # A short or generic name ("Palladian" inside "English Palladian") would match
                # loosely; require the whole word and at least two words of a name, so the line
                # fires on a real disagreement rather than on a substring.
                if len(other.split()) >= 2 and re.search(rf"\b{re.escape(other)}\b", low):
                    out.append(f"THE TITLE SAYS {other.upper()}")
                    break

    pid = plan.get("parti")
    if pid and partis:
        p = partis.get(pid) or {}
        if p.get("styles") and style not in p["styles"]:
            out.append(f"THE PARTI {pid.upper()} DOES NOT NAME IT")

    if not out:
        return None
    return {"id": "style", "tone": COPPER,
            "text": f"JUDGED AS {style.upper()} — " + "; ".join(out)}


# ---------------------------------------------------------------- the banner
def banner(plan, undrawable=None, diverged=None, unlocated=None, styles=None, partis=None,
           marked=True):
    """Every disclosure line the plate owes, in the order it prints them.

    `undrawable`, `diverged` and `unlocated` are the RENDERER's derivations, passed in rather
    than recomputed here: a second derivation of a drawn fact is how one rule comes to be
    spelled three times. Pass None to omit that line (the workbench's disclosure strip has its
    own reader for the first two and takes only the record-derived lines from here). `marked`
    says whether the surface draws the divergence mark on the field: the plate's presentation
    register does not, and a line saying MARKED ∗ over a sheet with no ∗ on it is a disclosure
    that points at nothing.

    THE PLATE READS THIS LIST NOW (WP-13.2). `render_plan.py` imported this module, called
    nothing from it, and spelled its own copies of two of these lines -- which is how it came to
    print PLACEMENT PROVED on the engine's name after this module had stopped saying that
    (`oq/the-plate-does-not-read-the-disclosure-module-it-imports`). The plate maps the tones
    onto its inks and appends the three lines that are the SHEET's rather than the placement's
    (the stair, openings on no wall line, the wall assembly and the face); everything a record
    can say about what it gave up is here, once, for both surfaces."""
    gr = plan.get("geometry_report") or {}
    lines = []

    rl = gr.get("relaxations") or {}
    if gr:
        n = rl.get("count", 0)
        lines.append({"id": "relaxations", "tone": COPPER if n else VERD,
                      "text": f"{n} CUT(S) OFF THE BAY LINE"
                              + (f", WORST {rl.get('max_off_grid_ft')} FT" if n else "")})

    inf = gr.get("infeasible")
    if inf:
        lines.append({"id": "infeasible", "tone": IRON,
                      "text": f'INFEASIBLE AS DECLARED — {len(inf.get("conflicts", []))} '
                              f'CONFLICT(S) PROVEN; THIS DRAWING IS THE LEAST-BAD RELAXATION '
                              f'(SEE GEOMETRY_REPORT.INFEASIBLE)'})

    line = span_capacity(plan)
    if line:
        lines.append(line)

    if undrawable:
        names = ", ".join(f'{u["from"]}–{u["to"]}' for u in undrawable[:6])
        more = f" (+{len(undrawable) - 6} MORE)" if len(undrawable) > 6 else ""
        lines.append({"id": "undrawable", "tone": IRON,
                      "text": f"{len(undrawable)} DECLARED DOOR(S) WITHOUT A DRAWABLE OPENING — "
                              f"IN THE RECORD, NOT THE LINEWORK: {names.upper()}{more}"})

    # `alternative_offered` comes straight after `objective_not_run` deliberately: it is the
    # second half of one disclosure and a reader meeting the first without the second has
    # been told the composition was not evaluated and not told what else is available. The
    # furniture, the stacks and the residual void follow the windows because all four are
    # things the record asked for and the placement did not deliver.
    for fn in (walls_set_aside, objective_not_run, alternative_offered, windows_not_drawn,
               furniture_not_drawn, stacking):
        line = fn(plan)
        if line:
            lines.append(line)
    lines.extend(residual_void(plan) or [])

    if diverged:
        w0 = diverged[0]
        mark = ", MARKED ∗" if marked else ""
        lines.append({"id": "diverged", "tone": COPPER,
                      "text": f'{len(diverged)} ROOM(S) DRAWN AT A SIZE THE RECORD DOES NOT '
                              f'DECLARE{mark} — WORST {(w0["name"] or "").upper()} '
                              f'{"+" if w0["pct"] > 0 else ""}{w0["pct"]:.0f}% BY AREA'})

    line = transfers(plan)
    if line:
        lines.append(line)

    line = stack_plan_judgment(plan)
    if line:
        lines.append(line)

    line = engine_line(plan)
    if line:
        lines.append(line)

    line = style_disagreement(plan, styles, partis)
    if line:
        lines.append(line)

    if unlocated:
        lines.append({"id": "unlocated", "tone": IRON,
                      "text": f"{len(unlocated)} CUT(S) OFF THE BAY LINE THE SOLVER LOCATED ON "
                              f"NO WALL OF THEIR LEVEL — COUNTED, NOT DRAWN"})
    return lines
