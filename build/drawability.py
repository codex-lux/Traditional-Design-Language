#!/usr/bin/env python3
"""May this house be drawn, and if not, whose fault is the refusal? -- the Phase 17 instrument.

    python3 build/drawability.py --brief briefs/family-georgian.json [--candidates 4] [--json]
    python3 build/drawability.py --plan plans/tidewater-georgian-careful.json [--engine auto]
    python3 build/drawability.py --placed some-placed-record.json

WHY IT EXISTS (Phase 17, WP-17.0). Lucas composed a Tidewater brief on 29 Oct 2026 and all four
candidates came back refused a drawing. The investigation that followed needed, for every house,
the same six numbers -- which type facts hold, which are released and on what evidence, how many
rooms leave their own band, how many doors the placement could not seat, and whether each upper
bearing wall really stands on a ground one -- and every one of them was computed by hand, five
different ways, by five agents. This is the one way, and it is the acceptance instrument of the
whole phase.

FOUR VERDICTS, NEVER TWO (the audit of Phase 17, 30 Oct 2026; Lucas's ruling 10 of the same day:
"an unjudged fact is never called held"):

  DRAWABLE               not refused, no fact downgraded, no room past its own proportion ceiling
                         (a room the record declares past it, only past its DECLARED ratio),
                         bearing continuity held over the whole run (ruling 8 of 29 Oct), every
                         room that takes a rectangle placed, no door pair left unplaced, no room
                         drawn under the prover's own size pin (`geometry.SIZE_PIN_FLOOR` of its
                         declared area; a room a tenth under is still REPORTED in
                         `rooms_undersize`, as the drawn layer reports it), and EVERY one of the four
                         facts HELD.
  DRAWABLE WHERE JUDGED  the same, except that one or more facts could not be judged -- named, in
                         `unjudged`. A composed house stating no fire has its hearth unjudged; a
                         one-storey house has no continuity to judge. Neither is held.
  NOT DRAWABLE           refused, a fact downgraded, a room past its band, a wall over open floor,
                         a room that takes a rectangle left without one (`rooms_unplaced`), a door
                         pair left unplaced (`doors_unplaced`), or a room drawn under the prover's
                         size pin (a `rooms_undersize` entry with `past_size_pin`).
  COULD NOT EVALUATE     the record carries no placed room, or no `geometry_report` -- a declared
                         record, or a candidate whose placement was never made. Never drawable.

THE LAST THREE CONDITIONS ARE THE SECOND AUDIT'S (30 Oct 2026). A partly placed record read
DRAWABLE: a room with no rectangle was skipped by every count here, and
`geometry_report.multi_level.rooms_not_placed` was read by nothing -- `bad-03`'s third-storey game
room, placed on no level, did not stop the verdict. And two of ruling 6's three never-downgrade
counts were measured and not decided on, although the ruling reads "a house that holds the facts
by unplacing doors or blowing up rooms is never drawn": the lead's decision of 30 Oct is that both
`doors_unplaced` and `rooms_undersize` make a house NOT DRAWABLE. (`rooms_over_band`, the third,
already did.) AND THE UNDERSIZE GATE WAS FIRST DRAWN AT THE DRAWN LAYER'S TENTH, which is not the
prover's: `geometry_cp` holds a room to 0.88 of its declared area as a pin it never releases, so on
Lucas's brief every composed house the prover had placed inside that pin read NOT DRAWABLE (0 of 4
drawable where judged, measured the same afternoon) -- the instrument convicting what the model had
held. The gate is the pin now; a room a tenth under is reported and decides nothing.

Until the audit a fact that was UNJUDGED blocked nothing and a record with no placement at all
read DRAWABLE (every fact unjudged), so "n of N drawable" counted houses nobody had measured.
`drawable` keeps the strict meaning, and `main()` prints both counts.

IT DECIDES NOTHING THE PRODUCT READS. The refusal a surface obeys is `typefacts.judge`'s, written
once; this reports beside it, and in particular reports the WHOLE-RUN continuity audit that
`typefacts.bearing_extents` computes and does not yet decide on (WP-17.7 switches it).

THE REFUSAL CLASS. For every fact `typefacts` reads as downgraded, the class is read off what the
ENGINE said about the same fact (`geometry_report.solver.facts`, `refinements`), never guessed:

  PROVEN     the prover released the fact with a proof -- "restored alone, no placement exists" --
             or the record carries a proven infeasibility. Whether the core is the HOUSE's or the
             composer's is a further question this instrument names but cannot settle.
  UNDECIDED  the prover released it without a proof ("carried -- off a conflict core or an
             undecided round"): the budget ran out, which is the instrument's, not the house's.
  MISMATCH   the prover says it HELD the fact, or NEVER POSED it (its own status `unjudged`), and
             the gate measures it downgraded -- the model and the measurement disagree (e.g. a box
             tiled on the integer grid and measured on the float one), or the gate measured what
             the model was never asked. Always the instrument's. (A never-posed fact read
             UNDECIDED until the second audit of Phase 17, whose definition is "the budget ran
             out" -- and no budget was spent on a fact nobody posed.)
  SEARCH     the placement is the hill-climb's, which is told none of these facts as a fact
             (`oq/the-search-is-refused-on-type-facts-nothing-tells-it`). The instrument's.

DEFERRED, AND SAID SO: the class is read per FACT, so a fact with one label proven and one held by
the model but measured broken is UNDECIDED rather than split PROVEN / MISMATCH by label (the second
audit's finding 5; deferred by the lead, 30 Oct 2026).
"""
import argparse
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _m(name):
    return modcache.load(name, os.path.join(ROOT, "build", name + ".py"))


# The four classes are `typefacts`'s (the leaf that writes them onto the refusal); the names are
# kept here because readers of this instrument import them from it.
PROVEN, UNDECIDED, MISMATCH, SEARCH = "PROVEN", "UNDECIDED", "MISMATCH", "SEARCH"


def rooms_over_band(plan):
    """Placed rooms drawn past the proportion ceiling their own record states. The ceiling is
    `geometry.shape_band`'s (corpus bands only) with `band_violations`' 0.02 ft slack on the long
    side, the reading the search, the prover and the drawn layer share.

    A ROOM THE RECORD DECLARES PAST ITS CEILING IS HELD TO ITS DECLARED RATIO, NOT EXEMPTED. That
    exemption is this instrument's own, from the plan's "except rooms declared over" --
    `band_violations` and the drawn layer's `drawn-proportion-above-band` have none -- and until the
    audit of Phase 17 (30 Oct 2026) it SKIPPED such a room whatever was drawn: good-07's living
    room, declared 16 x 26 (1.62 against a ceiling of 1.6), drawn 8 x 52 read as no room over band,
    and on the search's placement of `bad-05` the upper hall, declared 2.40 against 2.2, is drawn
    2.87 and was hidden. `no_worse` reads this count for ruling 6's comparison, so the exemption
    decided whether a search was drawn over a refused proof. The record's call is honoured as the
    record states it and no further: such a room counts once it is drawn past its DECLARED ratio,
    with the same 0.02 ft slack, and the row carries `declared_ratio`."""
    G = _m("geometry")
    out = []
    for lv in plan.get("levels") or []:
        for r in lv.get("rooms") or []:
            g = r.get("geometry")
            if not g:
                continue
            ceil, src = G.shape_band(r.get("type"))
            if src != "corpus":
                continue
            w, h = float(g["width_ft"]), float(g["depth_ft"])
            limit, declared = ceil, None
            dw, dl = r.get("width_ft"), r.get("length_ft")
            if dw and dl and max(dw, dl) > ceil * min(dw, dl) + 0.02:
                declared = max(dw, dl) / min(dw, dl)   # the record's call, and no further
                limit = declared
            if max(w, h) <= limit * max(min(w, h), 1e-9) + 0.02:
                continue
            row = {"room": r["id"], "type": r.get("type"), "drawn": [round(w, 2), round(h, 2)],
                   "ratio": round(max(w, h) / max(min(w, h), 1e-9), 2), "ceiling": ceil}
            if declared is not None:
                row["declared_ratio"] = round(declared, 2)
            out.append(row)
    return out


def doors_unplaced(plan):
    """Door PAIRS the placement could not seat, read off the record's own `unplaced` marks
    (`openings.place` writes one on each side of a pair it refuses)."""
    pairs = set()
    for lv in plan.get("levels") or []:
        for r in lv.get("rooms") or []:
            for d in r.get("doors") or []:
                if d.get("unplaced"):
                    pairs.add(tuple(sorted((r["id"], str(d.get("to"))))))
    return sorted(pairs)


def rooms_undersize(plan):
    """Placed rooms drawn a tenth or more under the area their record DECLARES (width x length).
    Under and never over: decision 11 orders the footprint to grow before a room is compromised,
    and a room drawn larger than declared has compromised nothing of its own.

    THE TENTH IS THE DRAWN LAYER'S, CALLED AND NOT RESTATED (the audit of Phase 17, 30 Oct 2026):
    `plan_check.drawn_vs_declared_pct`. This carried its own `got < want * 0.9`, strictly MORE than
    a tenth, while the drawn layer convicts at a tenth or more -- so a room drawn at exactly -10%
    (the shipped Tidewater kitchen and library land there) was a `drawn-vs-declared` finding on the
    sheet and 0 in the comparison ruling 6 rests on. Only the sign is this function's."""
    PC = _m("plan_check")
    pin = _m("geometry").SIZE_PIN_FLOOR
    out = []
    for lv in plan.get("levels") or []:
        for r in lv.get("rooms") or []:
            g, dw, dl = r.get("geometry"), r.get("width_ft"), r.get("length_ft")
            if not (g and dw and dl):
                continue
            got, want = float(g["width_ft"]) * float(g["depth_ft"]), float(dw) * float(dl)
            pct = PC.drawn_vs_declared_pct(want, got)
            if pct is not None and pct < 0:
                out.append({"room": r["id"], "declared_sf": round(want, 1),
                            "drawn_sf": round(got, 1), "pct": round(pct, 1),
                            "past_size_pin": got < pin * want - PIN_GRID_SF})
    return out


# The prover states its pin on a 1 ft grid as `a >= int(SIZE_PIN_FLOOR * area)`, so a room it held
# can sit up to one square foot under the exact fraction; less than that is the grid, not a breach.
PIN_GRID_SF = 1.0


def rooms_unplaced(plan):
    """Rooms that TAKE A RECTANGLE (`geometry.is_placed`, the one join -- every indoor room and
    OQ 55's reserved voids; a terrace or an appendage takes none) and were given none, plus every
    room the placer's own `geometry_report.multi_level.rooms_not_placed` names. A partly placed
    record is not a drawing of the house: the room left out is the one the sheet does not show."""
    G = _m("geometry")
    out = []
    for lv in plan.get("levels") or []:
        for r in lv.get("rooms") or []:
            if not r.get("geometry") and G.is_placed(r.get("type")):
                out.append(r["id"])
    ml = ((plan.get("geometry_report") or {}).get("multi_level") or {})
    for rid in ml.get("rooms_not_placed") or []:
        if rid not in out:
            out.append(rid)
    return sorted(out)


def never_downgrade(plan):
    """THE NEVER-DOWNGRADE FACTS (ruling 6 of 29 Oct 2026): what a placement may not give up to
    hold the type's facts -- rooms drawn under their declared size, rooms drawn past their own band,
    door pairs left unplaced. Three counts, compared one by one and never summed."""
    return {"rooms_undersize": len(rooms_undersize(plan)),
            "rooms_over_band": len(rooms_over_band(plan)),
            "doors_unplaced": len(doors_unplaced(plan))}


def no_worse(a, b):
    """True where placement `a` is no worse than `b` on EVERY never-downgrade count. Each count is
    compared on its own: a placement that buys a door with a room out of band is not no-worse."""
    na, nb = never_downgrade(a), never_downgrade(b)
    return all(na[k] <= nb[k] for k in na), na, nb


def _class_of(fact, plan):
    """The refusal class of one downgraded fact. ONE SPELLING (30 Oct 2026): it lives in
    `typefacts.refusal_class`, the leaf that writes the refusal, so the class a surface prints and
    the class this instrument reports cannot disagree."""
    return _m("typefacts").refusal_class(fact, plan)


DRAWABLE = "DRAWABLE"
DRAWABLE_WHERE_JUDGED = "DRAWABLE WHERE JUDGED"
NOT_DRAWABLE = "NOT DRAWABLE"
COULD_NOT_EVALUATE = "COULD NOT EVALUATE"
VERDICTS = (DRAWABLE, DRAWABLE_WHERE_JUDGED, NOT_DRAWABLE, COULD_NOT_EVALUATE)
FACTS = ("tiling", "stacks", "bearing", "hearth")


def _not_evaluable(plan):
    """Why this record cannot be assessed at all, or `None`. A record carrying no placed room has
    nothing to measure, and one carrying no `geometry_report` was placed by no engine: re-judging
    either reads every fact it cannot measure as unjudged, which until the audit of Phase 17 counted
    toward DRAWABLE."""
    placed = any((r or {}).get("geometry") for lv in plan.get("levels") or []
                 for r in (lv.get("rooms") or []))
    if not placed:
        return ("the record carries no placed room -- a declared record, or a candidate whose "
                "placement was never made")
    if not plan.get("geometry_report"):
        return "the record carries no geometry_report: no engine placed it"
    return None


def assess(plan):
    """The six numbers for one PLACED record, and one of the four VERDICTS. The record is copied
    and re-judged by `typefacts.judge`, the one verdict, so a stale `refused` on the input cannot
    leak through. `drawable` is True for DRAWABLE alone, the strict state; `unjudged` names every
    fact that could not be judged, which DRAWABLE WHERE JUDGED is conditional on."""
    TF = _m("typefacts")
    why_not = _not_evaluable(plan)
    p = copy.deepcopy(plan)
    refused = TF.judge(p)
    facts = (p.get("geometry_report") or {}).get("type_facts") or {}
    status = facts.get("status") or {}
    ext = ((facts.get("bearing") or {}).get("extents")) or None
    over = rooms_over_band(p)
    doors = doors_unplaced(p)
    under = rooms_undersize(p)
    unplaced = rooms_unplaced(p)
    down = sorted(k for k, v in status.items() if v == "downgraded")
    classes = {k: _class_of(k, p) for k in down}
    whole_run = None if ext is None else ext.get("status")
    # Every fact the status block does not call HELD or DOWNGRADED is unjudged, by name -- a fact
    # missing from the block included, never held by its absence.
    unjudged = [k for k in FACTS if status.get(k) not in (TF.HELD, TF.DOWNGRADED)]
    if whole_run not in (TF.HELD, TF.DOWNGRADED) and "bearing" not in unjudged:
        unjudged.append("continuity_whole_run")   # held positionally, its run never judged
    # an undersize room refuses the drawing only past the prover's own size pin; inside it the
    # drawn layer's finding is reported (`rooms_undersize`) and decides nothing here
    past_pin = [u for u in under if u["past_size_pin"]]
    if why_not:
        verdict = COULD_NOT_EVALUATE
    elif refused or down or over or whole_run == TF.DOWNGRADED or unplaced or doors or past_pin:
        verdict = NOT_DRAWABLE
    elif unjudged:
        verdict = DRAWABLE_WHERE_JUDGED
    else:
        verdict = DRAWABLE
    sv = (p.get("geometry_report") or {}).get("solver") or {}
    return {"id": p.get("id"), "engine": sv.get("engine"), "solver_status": sv.get("status"),
            # how the prover RAN (the audit of Phase 17, finding 13): a portfolio's verdict is a
            # statement about the workers it had, so the row carries them beside the status
            "workers": sv.get("workers"), "workers_available": sv.get("workers_available"),
            "mode": sv.get("mode"),
            "facts": status, "downgraded": down, "refusal_class": classes,
            "refused_kind": (refused or {}).get("kind"),
            "continuity_whole_run": whole_run,
            "continuity_lines": (ext or {}).get("lines"),
            "rooms_over_band": over, "doors_unplaced": doors, "rooms_undersize": under,
            "rooms_unplaced": unplaced,
            "verdict": verdict, "unjudged": unjudged, "could_not_evaluate": why_not,
            "drawable": verdict == DRAWABLE}


def _row(a, label=None):
    tag = a["verdict"]
    if tag == NOT_DRAWABLE and (a["downgraded"] or a["refused_kind"]):
        tag += " (refused)"
    elif tag == DRAWABLE_WHERE_JUDGED:
        tag += " (" + ", ".join(a["unjudged"]) + " unjudged)"
    cls = ", ".join(f"{k}:{v}" for k, v in a["refusal_class"].items()) or "-"
    tail = f" -- {a['could_not_evaluate']}" if a["verdict"] == COULD_NOT_EVALUATE else ""
    return (f"{(label or a['id'] or '?')[:34]:34s} {tag:24s} engine={a['engine'] or '-':10s} "
            f"facts[{cls}] whole-run={a['continuity_whole_run']} "
            f"over-band={len(a['rooms_over_band'])} doors-unplaced={len(a['doors_unplaced'])} "
            f"undersize={len(a['rooms_undersize'])} unplaced={len(a['rooms_unplaced'])}{tail}")


def summary(rows):
    """BOTH counts, never one (ruling 10 of 30 Oct 2026): the houses DRAWABLE with every fact held,
    and the houses drawable only where judged, with the unjudged facts named and counted -- then
    the not drawable and the could-not-evaluate, so the four add up to the whole set."""
    n = len(rows)
    by = {v: [a for a in rows if a["verdict"] == v] for v in VERDICTS}
    unj = {}
    for a in by[DRAWABLE_WHERE_JUDGED]:
        for k in a["unjudged"]:
            unj[k] = unj.get(k, 0) + 1
    where = ", ".join(f"{k} unjudged on {c}" for k, c in sorted(unj.items()))
    return (f"{len(by[DRAWABLE])} of {n} DRAWABLE (every fact held); "
            f"{len(by[DRAWABLE_WHERE_JUDGED])} of {n} drawable where judged"
            + (f" ({where})" if where else "")
            + f"; {len(by[NOT_DRAWABLE])} not drawable; "
              f"{len(by[COULD_NOT_EVALUATE])} could not evaluate")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--brief")
    g.add_argument("--plan")
    g.add_argument("--placed")
    ap.add_argument("--candidates", type=int, default=4)
    ap.add_argument("--engine", default="auto")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows = []
    if a.placed:
        rows.append((None, assess(json.load(open(a.placed)))))
    elif a.plan:
        G = _m("geometry")
        plan = json.load(open(a.plan))
        out = G.solve(plan, engine=a.engine)
        if "error" in out:
            print(out["error"]); return 2
        rows.append((None, assess(out)))
    else:
        CO = _m("compose")
        res = CO.compose(json.load(open(a.brief)), a.candidates)
        for c in res["candidates"]:
            rows.append((c["parti"], assess(c["plan"])))
    if a.json:
        print(json.dumps([dict(r, label=l) for l, r in rows], indent=1))
    else:
        for label, r in rows:
            print(_row(r, label))
        print("\n" + summary([r for _, r in rows]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
