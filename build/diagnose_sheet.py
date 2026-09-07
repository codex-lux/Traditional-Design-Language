#!/usr/bin/env python3
"""diagnose_sheet.py — the sheet's own diagnosis, generated rather than pixel-read (WP-11.11).

`docs/reports/tidewater-layout-diagnosis-2026-09-04.md` Part I was produced by reading a
screenshot and re-placing the record by hand. That is a thing worth doing once and a bad way to
start the next twenty: the next parti's diagnosis should begin from a GENERATED Part I. This file
generates it.

    python3 build/diagnose_sheet.py plans/tidewater-georgian-careful.json
                                    [--engine auto|cp|heuristic] [--candidates N] [--json]
                                    [--baseline]

`--baseline` prints ONE line of six numbers and nothing else. Those six are the measurement every
Phase 11 package is held to, before and after, on both shipped plans and BOTH ENGINES:

    key           the critic's [fatal, serious, minor] on the placed record
    diverged      rooms drawn at a size the record does not declare
    windows       declared window units the placement could not place, of the total declared
    downgraded    declared exterior walls the CP solver set aside to reach feasibility
    transfers     upper wall lines landing on no wall below
    score         the placement's demerit total, lower better

**Both engines, because a package that improves the proof and worsens the search — or the
reverse — has to say so.** WP-9.6 measured the two disagreeing by 50% on one furniture count, and
`docs/reports/tidewater-layout-diagnosis-2026-09-04.md` J2 found the engine the bench draws by
default returning its FIRST feasible placement with the compositional objective unevaluated, which
the heuristic beats on the corpus's own score. A single-engine number would have hidden both.

UNJUDGED IS NOT PASSED, and this file has two places to honour it. Asked for `cp` without OR-Tools
installed it prints COULD NOT EVALUATE and exits 3 — it does not quietly measure the hill-climb and
call it the proof. And a plan the placer cannot solve prints the solver's own error rather than a
row of zeros, because a zero here reads as a house with no findings.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, path):
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


PC = _mod("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
GEO = _mod("geometry", os.path.join(ROOT, "build", "geometry.py"))

EXIT_COULD_NOT_EVALUATE = 3


def cp_available():
    try:
        from ortools.sat.python import cp_model  # noqa: F401
        return True
    except Exception:
        return False


def has_placement(plan):
    return any(r.get("geometry") for lv in plan.get("levels", []) for r in lv.get("rooms", []))


# ------------------------------------------------------------------ the six numbers
def baseline(plan, check=None):
    """The six numbers, from a PLACED plan and its check. Every value is read from a record
    the placer or the critic wrote — nothing here re-derives a quantity another layer owns,
    which is the mistake `plan_check`'s elevation layer made until WP-9.1 (two buildings, one
    verdict)."""
    check = check if check is not None else PC.check(plan)
    counts = check.get("counts") or {}
    drawn = check.get("drawn_summary") or {}
    gr = plan.get("geometry_report") or {}
    solver = gr.get("solver") or {}
    op = plan.get("opening_report") or {}

    declared_units = 0
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            for w in r.get("windows", []) or []:
                declared_units += int(w.get("count") or 1)

    return {
        "key": [counts.get("fatal", 0), counts.get("serious", 0), counts.get("minor", 0)],
        "diverged": len(drawn.get("diverged") or []),
        "windows_unplaced": op.get("windows_unplaced"),
        "windows_declared": declared_units,
        "downgraded": len(solver.get("downgraded_wall_pins") or []),
        "transfers": _transfer_count(gr),
        "score": gr.get("score"),
        "engine": solver.get("engine"),
        # ONLY the CP engine can leave its objective unevaluated. The hill-climb's score IS its
        # objective -- every compositional term is summed for every candidate it looks at -- so
        # reading `objective is not None` for both engines would publish "the objective did not
        # run" about the one engine that always runs it. A first version of this file did exactly
        # that, on its first run, in the line a reader would have quoted.
        "objective_ran": (solver.get("objective") is not None
                          if solver.get("engine") == "cp-sat" else True),
        # A placement whose drawn layer could not be evaluated has NO drawn findings, so its
        # key falls by absence and reads as an improvement. WP-9.4 met this exact trap in the
        # revision loop; the flag travels with the numbers so no reader compares across it.
        "drawn_evaluated": bool(drawn.get("evaluated")),
    }


def _transfer_count(gr):
    """Upper wall lines landing on no wall below. `vertical` is a list of English sentences —
    the count lives inside the first of them and nowhere else, which is why this reads it out
    rather than asking for a field that does not exist."""
    import re
    for line in (gr.get("vertical") or []):
        m = re.match(r"^(\d+) upper wall line", line)
        if m:
            return int(m.group(1))
    return 0 if gr.get("vertical") is not None else None


def baseline_line(b):
    key = "/".join(str(x) for x in b["key"])
    win = f'{b["windows_unplaced"]}/{b["windows_declared"]}'
    obj = "" if b["objective_ran"] else " objective:DID-NOT-RUN"
    drawn = "" if b["drawn_evaluated"] else " drawn:COULD-NOT-EVALUATE"
    return (f'engine={b["engine"]} key={key} diverged={b["diverged"]} windows_unplaced={win} '
            f'downgraded={b["downgraded"]} transfers={b["transfers"]} score={b["score"]}'
            f'{obj}{drawn}')


# ------------------------------------------------------------------ Part I, generated
def _walls_touched(g, fp, tol=0.01):
    """Which boundary walls a placed rectangle reaches. South is y=0 by the model's own
    convention (`render_plan.py`'s window-wall convention and `geometry.py`'s origin: x east,
    y north, origin at the building's SW corner)."""
    if not g:
        return []
    W, H = fp.get("width_ft"), fp.get("depth_ft")
    out = []
    if abs(g["y_ft"]) < tol: out.append("S")
    if W is not None and abs(g["x_ft"] + g["width_ft"] - W) < tol: out.append("E")
    if H is not None and abs(g["y_ft"] + g["depth_ft"] - H) < tol: out.append("N")
    if abs(g["x_ft"]) < tol: out.append("W")
    return out


def room_table(plan):
    """Every room's drawn rectangle beside the one the record declares — the table Part I.1 of
    the diagnosis was transcribed by hand from a screenshot."""
    fp = plan.get("footprint") or {}
    rows = []
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            g = r.get("geometry")
            dw, dl = r.get("width_ft"), r.get("length_ft")
            row = {
                "level": lv.get("id"), "id": r.get("id"), "name": r.get("name"),
                "type": r.get("type"),
                "declared": [dw, dl],
                "declared_sf": (dw * dl) if (dw and dl) else None,
                "declared_walls": r.get("exterior_walls") or [],
                "drawn": [g["width_ft"], g["depth_ft"]] if g else None,
                "drawn_sf": round(g["width_ft"] * g["depth_ft"]) if g else None,
                "drawn_walls": _walls_touched(g, fp),
                "block": r.get("block"),
            }
            if g:
                w, d = g["width_ft"], g["depth_ft"]
                row["drawn_ratio"] = round(max(w, d) / min(w, d), 2) if min(w, d) else None
                if row["declared_sf"]:
                    row["pct"] = round((row["drawn_sf"] - row["declared_sf"])
                                       / row["declared_sf"] * 100)
            rows.append(row)
    return rows


def front_openings(plan):
    """What the entrance front shows, per storey, and whether anything lines up.

    The entrance front is the record's own `context.entrance_faces`, defaulting to S. An
    opening is counted where the placement PLACED it: a declared window the placer could not
    place is not on the elevation, which is the whole of finding G1 and is why this counts
    `positions_ft` rather than `count`."""
    faces = ((plan.get("context") or {}).get("entrance_faces") or "S").upper()
    out = []
    for lv in plan.get("levels", []):
        placed, unplaced = [], 0
        for r in lv.get("rooms", []):
            for w in r.get("windows", []) or []:
                if (w.get("wall") or "").upper() != faces:
                    continue
                if w.get("unplaced"):
                    unplaced += int(w.get("count") or 1)
                    continue
                for x in (w.get("positions_ft") or []):
                    placed.append({"room": r.get("id"), "x_ft": round(x, 2), "kind": "window"})
            for d in r.get("doors", []) or []:
                if d.get("to") == "exterior" and (d.get("wall") or "").upper() == faces \
                        and not d.get("unplaced"):
                    placed.append({"room": r.get("id"), "x_ft": round(d["position_ft"], 2),
                                   "kind": "door"})
        placed.sort(key=lambda o: o["x_ft"])
        out.append({"level": lv.get("id"), "face": faces,
                    "openings": placed, "declared_but_unplaced": unplaced})
    # Alignment: for every opening above the ground storey, is there one below within a foot?
    if len(out) > 1:
        ground = [o["x_ft"] for o in out[0]["openings"]]
        for lvl in out[1:]:
            aligned = sum(1 for o in lvl["openings"]
                          if any(abs(o["x_ft"] - gx) <= 1.0 for gx in ground))
            lvl["aligned_over_ground"] = aligned
            lvl["unaligned"] = len(lvl["openings"]) - aligned
    return out


def solver_account(plan):
    gr = plan.get("geometry_report") or {}
    s = gr.get("solver") or {}
    return {
        "engine": s.get("engine"),
        "status": s.get("status"),
        "objective": s.get("objective"),
        "objective_ran": s.get("objective") is not None,
        "wall_time_s": s.get("wall_time_s"),
        "downgraded_wall_pins": s.get("downgraded_wall_pins") or [],
        "reason": s.get("reason"),
        "relaxations": (gr.get("relaxations") or {}).get("count"),
        "worst_off_grid_ft": (gr.get("relaxations") or {}).get("max_off_grid_ft"),
        "vertical": gr.get("vertical") or [],
        "multi_element": gr.get("multi_element"),
    }


def roof_depth_floor(plan):
    """The depth this block's roof needs before it reads as a truss default (WP-11.10).

    **A DIAGNOSTIC, NOT A CAP, AND THE INSTRUMENT IS WHERE A DIAGNOSTIC BELONGS.**
    `build/depth_floor.py` inverts `faults/truss-flattened-pitch.json`'s own test to give the
    shortest span whose roof still clears it. It is reported here and acted on NOWHERE, because
    three measurements refused the cap -- read that file's docstring for all three; the sharpest
    is that `good-05-lobby-gallery-mansion`, a `good-*` reference plan, is convicted FATALLY by
    this fault today at 0.2509, its licence naming a SIBLING style, and the floor that implies is
    69.31 ft against a drawn 38.64. A cap would make a known-broken licence a hard constraint on
    the placer. `oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced`.

    The wall thickness comes from `structure.wall_thickness`, which this file may read because it
    is an instrument and not a leaf; `depth_floor.py` takes it as an argument for exactly that
    reason and never reaches for it itself.
    """
    DF = _mod("depth_floor", f"{ROOT}/build/depth_floor.py")
    fp = plan.get("footprint") or {}
    w, dp = fp.get("width_ft"), fp.get("depth_ft")
    span = min(w, dp) if (w and dp) else None
    # THE `try` WRAPPED THE IMPORT AS WELL AS THE CALL (audit, 7 Sep 2026), so an ImportError or
    # a SyntaxError in `structure.py` -- a broken module, an environment fault -- was reported on
    # the sheet as "the exterior wall thickness could not be read", a soft COULD NOT EVALUATE
    # about this plan. That is a dependency problem laundered as a data judgment, which is OQ 35's
    # own complaint. The import is outside now and raises; only the reading of a plan is caught.
    ST = _mod("structure", f"{ROOT}/build/structure.py")
    t = 0.0
    try:
        t = (ST.wall_thickness(plan) or {}).get("exterior_in") or 0.0
    except Exception as exc:                      # noqa: BLE001 -- reported, never swallowed
        return {"verdict": "unjudged",
                "reason": f"the exterior wall thickness could not be read ({exc}); the fault "
                          f"measures the OUTSIDE envelope and a clear span cannot be compared "
                          f"to it without one"}
    return DF.evaluate(plan, exterior_wall_in=t, clear_span_ft=span)


def diagnose(plan, engine="auto", candidates=250, time_limit_s=25.0):
    """Place (or reuse a placement), check, and return the whole account."""
    if not has_placement(plan):
        placed = GEO.solve(plan, None, candidates, engine=engine, time_limit_s=time_limit_s)
        if "error" in placed:
            return {"error": placed["error"]}
        plan = placed
    check = PC.check(plan)
    return {
        "plan": plan.get("id"), "name": plan.get("name"), "style": plan.get("style"),
        "massing": plan.get("massing"), "parti": plan.get("parti"),
        "footprint": plan.get("footprint"),
        "baseline": baseline(plan, check),
        "solver": solver_account(plan),
        "roof_depth_floor": roof_depth_floor(plan),
        "rooms": room_table(plan),
        "front": front_openings(plan),
    }


# ------------------------------------------------------------------ printing
def _fmt_pair(p):
    if not p or p[0] is None:
        return "—"
    return f"{p[0]:g} x {p[1]:g}"


def report(d):
    fp = d.get("footprint") or {}
    print(f'\n  {d["name"]}')
    print(f'  {d["plan"]} · style {d["style"]} · massing {d["massing"]}'
          + (f' · parti {d["parti"]}' if d.get("parti") else " · parti NOT NAMED BY THE RECORD"))
    print(f'  footprint {fp.get("width_ft")} x {fp.get("depth_ft")} ft, '
          f'{fp.get("bays")} bays of {fp.get("bay_module_ft")} ft, {fp.get("area_sf")} sf')
    b = d["baseline"]
    print(f"\n  BASELINE  {baseline_line(b)}")

    rf = d.get("roof_depth_floor") or {}
    if rf:
        if rf.get("verdict") == "unjudged":
            print(f'\n  ROOF FLOOR  COULD NOT EVALUATE — {rf.get("reason")}')
        else:
            print(f'\n  ROOF FLOOR  {rf["verdict"].upper()}: this block\'s shortest span is '
                  f'{rf.get("clear_span_ft")} ft clear against a floor of '
                  f'{rf.get("min_clear_span_ft")} ft, inverted from '
                  f'faults/truss-flattened-pitch.json at {rf.get("threshold")} '
                  f'(pitch {rf.get("pitch")}:12, wall {rf.get("wall_height_ft")} ft). '
                  f'REPORTED AND NOT ENFORCED — oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced')

    s = d["solver"]
    print(f'\n  SOLVER    {s["engine"]} — {s["status"]}')
    if not s["objective_ran"]:
        print("            OBJECTIVE DID NOT RUN — this is the first feasible placement, and "
              "no compositional")
        print("            term (the front, the axis, the mirror, the stack) was evaluated on it.")
    if s["downgraded_wall_pins"]:
        print(f'            {len(s["downgraded_wall_pins"])} declared exterior wall(s) SET ASIDE '
              f'to reach feasibility:')
        for pin in s["downgraded_wall_pins"]:
            print(f"              · {pin}")
    for line in s["vertical"]:
        print(f"            · {line}")
    if s.get("multi_element"):
        print(f'            MULTI-ELEMENT: {json.dumps(s["multi_element"])[:200]}')

    print("\n  ROOMS — drawn against declared")
    print(f'  {"level":6s} {"id":13s} {"declared":13s} {"drawn":13s} {"ratio":>5s} '
          f'{"%":>5s}  walls decl→drawn')
    for r in d["rooms"]:
        pct = f'{r["pct"]:+d}' if r.get("pct") is not None else ""
        ratio = f'{r["drawn_ratio"]:.2f}' if r.get("drawn_ratio") else ""
        dw = "".join(r["declared_walls"]) or "-"
        gw = "".join(r["drawn_walls"]) or "-"
        flag = "  ✗" if (dw != "-" and gw == "-") else ""
        print(f'  {str(r["level"]):6s} {str(r["id"]):13s} {_fmt_pair(r["declared"]):13s} '
              f'{_fmt_pair(r["drawn"]):13s} {ratio:>5s} {pct:>5s}  {dw}→{gw}{flag}')

    print("\n  THE ENTRANCE FRONT")
    for lvl in d["front"]:
        marks = " ".join(f'{o["x_ft"]:g}{"D" if o["kind"] == "door" else ""}'
                         for o in lvl["openings"]) or "(nothing placed)"
        line = f'  {str(lvl["level"]):6s} {len(lvl["openings"])} opening(s) at {marks}'
        if lvl.get("declared_but_unplaced"):
            line += f' · {lvl["declared_but_unplaced"]} declared and not placed'
        if "aligned_over_ground" in lvl:
            line += f' · {lvl["aligned_over_ground"]} over an opening below, {lvl["unaligned"]} not'
        print(line)
    print()


# ------------------------------------------------------------------ the spread
def spread(plan, engine="heuristic", candidates=250, seeds=(7, 11, 23), time_limit_s=25.0):
    """The six numbers at several seeds, because ONE seed is not a measurement.

    Found by using this file. WP-11.2 named the Tidewater plan's parti, which moved its
    footprint, and the fatal count went 3 -> 8 -- which reads as a regression until the same
    footprint is run at three seeds and returns 8, 9 and 10 while the OLD footprint returns 5,
    12 and 10. The hill-climb's fatal count is dominated by which slicing tree its seed happens
    to find, and a single-seed before-and-after compares two draws from two distributions.

    WP-9.6 published the rule for the drawn furniture counts -- ratchet the deterministic
    figures, never the ones that drift -- and this is the same rule one layer up: a heuristic
    number is a SPREAD and must be reported as one. The CP engine is deterministic on one
    machine at one budget, so `seeds` does nothing there and the budget is what varies."""
    rows = []
    for seed in seeds:
        placed = GEO.solve(json.loads(json.dumps(plan)), None, candidates, seed=seed,
                           engine=engine, time_limit_s=time_limit_s)
        if "error" in placed:
            rows.append({"seed": seed, "error": placed["error"]})
            continue
        b = baseline(placed)
        b["seed"] = seed
        rows.append(b)
    return rows


def spread_line(rows):
    ok = [r for r in rows if "error" not in r]
    if not ok:
        return f'COULD NOT EVALUATE at every seed — {rows[0].get("error", "")[:80]}'
    def rng(get):
        vals = [get(r) for r in ok if get(r) is not None]
        if not vals:
            return "—"
        return f"{min(vals)}" if min(vals) == max(vals) else f"{min(vals)}–{max(vals)}"
    fat = rng(lambda r: r["key"][0]); ser = rng(lambda r: r["key"][1])
    mnr = rng(lambda r: r["key"][2])
    n = len(ok)
    tail = "" if n == len(rows) else f' ({len(rows) - n} seed(s) COULD NOT EVALUATE)'
    return (f'engine={ok[0]["engine"]} seeds={n} key={fat}/{ser}/{mnr} '
            f'diverged={rng(lambda r: r["diverged"])} '
            f'windows_unplaced={rng(lambda r: r["windows_unplaced"])}/'
            f'{ok[0]["windows_declared"]} '
            f'downgraded={rng(lambda r: r["downgraded"])} '
            f'transfers={rng(lambda r: r["transfers"])} '
            f'score={rng(lambda r: r["score"])}{tail}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--engine", choices=["auto", "cp", "heuristic"], default="auto")
    ap.add_argument("--candidates", type=int, default=250)
    ap.add_argument("--time", type=float, default=25.0, help="CP budget, seconds")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--baseline", action="store_true",
                    help="one line of the six numbers, nothing else")
    ap.add_argument("--seeds", default=None,
                    help="comma-separated seeds: report each column as a SPREAD, which is what "
                         "a hill-climb number is. One seed is not a measurement.")
    a = ap.parse_args()

    if a.engine == "cp" and not cp_available():
        print("COULD NOT EVALUATE: --engine cp was asked for and ortools is not installed. "
              "Measuring the hill-climb and calling it the proof is the one thing this file "
              "must not do.", file=sys.stderr)
        return EXIT_COULD_NOT_EVALUATE

    plan = json.load(open(a.plan, encoding="utf-8"))
    if a.seeds:
        seeds = tuple(int(x) for x in a.seeds.split(",") if x.strip())
        print(spread_line(spread(plan, engine=a.engine, candidates=a.candidates, seeds=seeds,
                                 time_limit_s=a.time)))
        return 0
    d = diagnose(plan, engine=a.engine, candidates=a.candidates, time_limit_s=a.time)
    if "error" in d:
        print(f'COULD NOT EVALUATE: {d["error"]}', file=sys.stderr)
        return EXIT_COULD_NOT_EVALUATE
    if a.json:
        print(json.dumps(d, indent=1))
    elif a.baseline:
        print(baseline_line(d["baseline"]))
    else:
        report(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
