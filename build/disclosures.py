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
    reader will take it for the answer to this one."""
    s = (plan.get("geometry_report") or {}).get("solver") or {}
    engine = s.get("engine")
    if not engine:
        return None
    if engine == "cp-sat":
        dropped = len(s.get("downgraded_wall_pins") or [])
        if dropped:
            total = _declared_wall_count(plan)
            kept = (total - dropped) if total is not None else None
            held = (f"{kept} OF THE RECORD'S {total} DECLARED EXTERIOR WALLS"
                    if kept is not None
                    else f"THE RECORD'S DECLARED EXTERIOR WALLS BUT {dropped}")
            return {"id": "engine", "tone": COPPER,
                    "text": f"PLACEMENT PROVED (CP-SAT) AGAINST {held}"}
        return {"id": "engine", "tone": VERD,
                "text": "PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS"}
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
def banner(plan, undrawable=None, diverged=None, unlocated=None, styles=None, partis=None):
    """Every disclosure line the plate owes, in the order it prints them.

    `undrawable`, `diverged` and `unlocated` are the RENDERER's derivations, passed in rather
    than recomputed here: a second derivation of a drawn fact is how one rule comes to be
    spelled three times. Pass None to omit that line (the workbench's disclosure strip has its
    own reader for the first two and takes only the record-derived lines from here)."""
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

    if undrawable:
        names = ", ".join(f'{u["from"]}–{u["to"]}' for u in undrawable[:6])
        more = f" (+{len(undrawable) - 6} MORE)" if len(undrawable) > 6 else ""
        lines.append({"id": "undrawable", "tone": IRON,
                      "text": f"{len(undrawable)} DECLARED DOOR(S) WITHOUT A DRAWABLE OPENING — "
                              f"IN THE RECORD, NOT THE LINEWORK: {names.upper()}{more}"})

    # `alternative_offered` comes straight after `objective_not_run` deliberately: it is the
    # second half of one disclosure and a reader meeting the first without the second has
    # been told the composition was not evaluated and not told what else is available.
    for fn in (walls_set_aside, objective_not_run, alternative_offered, windows_not_drawn):
        line = fn(plan)
        if line:
            lines.append(line)

    if diverged:
        w0 = diverged[0]
        lines.append({"id": "diverged", "tone": COPPER,
                      "text": f'{len(diverged)} ROOM(S) DRAWN AT A SIZE THE RECORD DOES NOT '
                              f'DECLARE, MARKED ∗ — WORST {(w0["name"] or "").upper()} '
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
