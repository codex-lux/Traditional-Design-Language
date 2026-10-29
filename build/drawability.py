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
whole phase: a candidate is DRAWABLE only when every judged fact holds (bearing continuity over
the whole run included, ruling 8 of 29 Oct), no room is over its own proportion ceiling (except a
room declared over it), and nothing unjudged has been counted as held.

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
  MISMATCH   the prover says it HELD the fact and the gate measures it downgraded -- the model
             and the measurement disagree (e.g. a box tiled on the integer grid and measured on the
             float one). Always the instrument's.
  SEARCH     the placement is the hill-climb's, which is told none of these facts as a fact
             (`oq/the-search-is-refused-on-type-facts-nothing-tells-it`). The instrument's.
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


PROVEN, UNDECIDED, MISMATCH, SEARCH = "PROVEN", "UNDECIDED", "MISMATCH", "SEARCH"

# The prover's own words for a fact it released WITH a proof (`geometry_cp.py`'s `how` strings).
PROOF_PHRASE = "proven — restored alone"

# typefacts' fact name -> the prover's rank name (`geometry_cp._RANK`)
_PROVER_KIND = {"tiling": "tiling", "stacks": "stack", "bearing": "bearing", "hearth": "hearth"}


def rooms_over_band(plan):
    """Placed rooms drawn past the proportion ceiling their own record states, excluding a room
    the RECORD already declares past it (that is the author's statement, not the placement's).
    The rule is `geometry.band_violations`', which the search, the prover and the drawn layer
    share: `shape_band`, corpus bands only, a 0.02 tolerance."""
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
            if max(w, h) <= ceil * max(min(w, h), 1e-9) + 0.02:
                continue
            dw, dl = r.get("width_ft"), r.get("length_ft")
            if dw and dl and max(dw, dl) > ceil * min(dw, dl) + 0.02:
                continue                      # declared over its own band: the record's call
            out.append({"room": r["id"], "type": r.get("type"), "drawn": [round(w, 2), round(h, 2)],
                        "ratio": round(max(w, h) / max(min(w, h), 1e-9), 2), "ceiling": ceil})
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


SIZE_TOL = 0.10   # a room drawn more than a tenth under the area its record declares


def rooms_undersize(plan, tol=SIZE_TOL):
    """Placed rooms drawn more than `tol` under the area their record DECLARES (width x length).
    Under and never over: decision 11 orders the footprint to grow before a room is compromised,
    and a room drawn larger than declared has compromised nothing of its own."""
    out = []
    for lv in plan.get("levels") or []:
        for r in lv.get("rooms") or []:
            g, dw, dl = r.get("geometry"), r.get("width_ft"), r.get("length_ft")
            if not (g and dw and dl):
                continue
            got, want = float(g["width_ft"]) * float(g["depth_ft"]), float(dw) * float(dl)
            if got < want * (1.0 - tol):
                out.append({"room": r["id"], "declared_sf": round(want, 1), "drawn_sf": round(got, 1)})
    return out


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
    rep = plan.get("geometry_report") or {}
    sv = rep.get("solver") or {}
    eng = str(sv.get("engine") or "")
    if (rep.get("infeasible") or {}).get("proven"):
        return PROVEN
    if not eng.startswith("cp"):
        return SEARCH
    kind = _PROVER_KIND.get(fact, fact)
    pf = (sv.get("facts") or {}).get(kind) or {}
    if pf.get("status") == "held":
        return MISMATCH                       # the model held it; the gate measured otherwise
    # A release counts as PROVEN only where the prover wrote the proof down for this kind
    # ("proven -- restored alone, no placement exists"); a release off a conflict core or an
    # undecided scout is "carried", and a release with no word either way is no proof either.
    # THE EXACT PHRASE, and the first version's bare "proven" was a false positive measured on its
    # first run: the CARRIED note reads "not individually re-proven in budget", which contains
    # the word, so every carried release read as proven.
    if any(PROOF_PHRASE in str(n) and kind in str(n).lower()
           for n in (sv.get("refinements") or [])):
        return PROVEN
    return UNDECIDED


def assess(plan):
    """The six numbers for one PLACED record. The record is copied and re-judged by
    `typefacts.judge`, the one verdict, so a stale `refused` on the input cannot leak through."""
    TF = _m("typefacts")
    p = copy.deepcopy(plan)
    refused = TF.judge(p)
    facts = (p.get("geometry_report") or {}).get("type_facts") or {}
    status = facts.get("status") or {}
    ext = ((facts.get("bearing") or {}).get("extents")) or None
    over = rooms_over_band(p)
    doors = doors_unplaced(p)
    down = sorted(k for k, v in status.items() if v == "downgraded")
    classes = {k: _class_of(k, p) for k in down}
    whole_run = None if ext is None else ext.get("status")
    drawable = (not refused and not down and not over
                and whole_run in ("held", "unjudged", None))
    sv = (p.get("geometry_report") or {}).get("solver") or {}
    return {"id": p.get("id"), "engine": sv.get("engine"), "solver_status": sv.get("status"),
            "facts": status, "downgraded": down, "refusal_class": classes,
            "refused_kind": (refused or {}).get("kind"),
            "continuity_whole_run": whole_run,
            "continuity_lines": (ext or {}).get("lines"),
            "rooms_over_band": over, "doors_unplaced": doors,
            "drawable": bool(drawable)}


def _row(a, label=None):
    tag = "DRAWABLE" if a["drawable"] else "refused" if a["downgraded"] or a["refused_kind"] else "not drawable"
    cls = ", ".join(f"{k}:{v}" for k, v in a["refusal_class"].items()) or "-"
    return (f"{(label or a['id'] or '?')[:34]:34s} {tag:12s} engine={a['engine'] or '-':10s} "
            f"facts[{cls}] whole-run={a['continuity_whole_run']} "
            f"over-band={len(a['rooms_over_band'])} doors-unplaced={len(a['doors_unplaced'])}")


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
        n = sum(1 for _, r in rows if r["drawable"])
        print(f"\n{n} of {len(rows)} drawable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
