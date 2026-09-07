#!/usr/bin/env python3
"""check_plans.py — a plan record against the parti it names (WP-11.2).

THE DEFECT THIS EXISTS FOR. `partis/centre-passage-double-pile.json` states five `stacks_over`
claims, and the shipped `plans/tidewater-georgian-careful.json` carries three. The two it does not
carry are **the upper passage over the lower one** and **the landing over the stair** — the two
that organise the floor — so `plan_check`'s stacking layer, which reads `stacks_over` faithfully
and reports a broken stack as `serious`, had nothing to read for either. The sheet duly drew a
landing over the library and an upper passage across the entrance front, and no check anywhere
said the record had stopped describing its own diagram.

It could not have been noticed. `build/compose.py` copies every `stacks_over` the parti states onto
the candidates it emits, so a composed plan is correct by construction — and **nothing checked a
plan the composer did not write**. Both shipped reference plans are hand-authored.

    python3 build/check_plans.py [--strict] [plans/x.json ...]

Exit 0 clean, 1 on a finding. With no arguments it reads every `plans/*.json` and
`plans/reference/*.json`.

WHAT IT CHECKS, and each is a claim the parti makes about the diagram rather than about a house:
  · every room id the parti names as `required` (the default) exists in the plan;
  · every `stacks_over` the parti states for a room the plan carries is stated by the plan too;
  · every `exterior_walls` side the parti states for a room the plan carries is declared by it;
  · every door the parti's room states to another room the plan carries is declared by it;
  · the plan's style is one the parti names, and its massing is the parti's or an alternate.

WHAT IT DELIBERATELY DOES NOT CHECK. Dimensions, in either direction: decision #3 says a parti
specifies topology and roles ONLY and never dimensions, so a plan that differs from its parti in
width is not thereby wrong — it is a plan. And a plan may carry rooms the parti does not name (a
cellar stair, a terrace): a diagram is a skeleton, not a census.

AND ONE KIND OF FINDING IS REPORTED RATHER THAN FAILED, for the same reason. A parti's
`exterior_walls` is not topology: `geometry_cp.py`'s own docstring says the field *"speaks EXPOSURE
in the fully-massed house"*, and a plan that recasts a room's exposure is making a MASSING
statement, which decision #3 puts outside a parti's authority. The shipped Tidewater plan is the
case: its back hall is a hyphen (N and S, the two long sides of a link) and its kitchen a detached
dependency (N, S and W), where the parti — which has no hyphen and no dependency — puts both on E
and N inside one block. That disagreement is `oq/the-parti-dissolved-its-own-dependencies` showing
through, and erasing it to make this checker quiet would delete the record's own account of the
house. It is counted and ratcheted instead. `stacks_over`, doors and room existence ARE topology
and they fail.

UNJUDGED IS NOT PASSED. A plan naming no parti is reported as UNJUDGED and counted, never as
clean: the whole finding above is a plan that said nothing about its diagram, and a checker that
read silence as agreement would reproduce it.
"""
from __future__ import annotations

import argparse
import glob
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


def load_parti(pid):
    """Through `core.load_parti`, never a join of our own — the id in a plan record is
    caller-supplied exactly as a POST body's is (the bench posts plan records), and this
    repository keeps that join in one place on purpose."""
    core = _mod("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))
    return core.load_parti(pid)


def plan_paths(args):
    if args:
        return list(args)
    out = sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))
    out += sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json")))
    return out


def rooms_of(plan):
    out = {}
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            out.setdefault(r["id"], r)
    return out


def check_plan(plan, parti):
    """Findings for one plan against one parti record. Each is a dict with `kind`, `room` and a
    `statement` in the corpus's own voice."""
    found = []
    pr = rooms_of(plan)
    for room in parti.get("rooms", []):
        rid = room.get("id")
        # `repeats_with_bedrooms` rooms are a TEMPLATE the composer instantiates as chamber2,
        # chamber3 …; the id in the parti is never in the plan and its absence is not a finding.
        if room.get("repeats_with_bedrooms"):
            continue
        if rid not in pr:
            if room.get("required") is not False:
                found.append({"kind": "missing-room", "room": rid,
                              "statement": f'the parti names {rid} ({room.get("type")}) and the '
                                           f'plan has no room with that id'})
            continue
        have = pr[rid]

        so = room.get("stacks_over")
        if so and have.get("stacks_over") != so:
            found.append({"kind": "stacks-over", "room": rid,
                          "statement": f'the parti says {rid} stacks over {so} and the plan '
                                       f'says {have.get("stacks_over") or "nothing"} — '
                                       f'plan_check reads this field and had nothing to read'})

        want_walls = set(room.get("exterior_walls") or [])
        got_walls = set(have.get("exterior_walls") or [])
        missing = sorted(want_walls - got_walls)
        if missing:
            found.append({"kind": "exterior-walls", "room": rid,
                          "statement": f'the parti puts {rid} on {"/".join(sorted(want_walls))} '
                                       f'and the plan declares {"/".join(sorted(got_walls)) or "none"}'})

        want_doors = {d for d in (room.get("doors") or [])}
        got_doors = {d.get("to") for d in (have.get("doors") or [])}
        # only doors to rooms the plan actually carries: a door to a room the plan left out is
        # already reported as a missing room, and saying it twice makes one defect read as two
        for d in sorted(want_doors - got_doors):
            if d != "exterior" and d not in pr:
                continue
            found.append({"kind": "door", "room": rid,
                          "statement": f'the parti gives {rid} a door to {d} and the plan '
                                       f'declares none'})

    styles = parti.get("styles") or []
    if styles and plan.get("style") and plan["style"] not in styles:
        found.append({"kind": "style", "room": None,
                      "statement": f'the plan is judged as {plan["style"]} and the parti names '
                                   f'{len(styles)} styles, not including it'})
    massings = [parti.get("massing")] + list(parti.get("alternate_massings") or [])
    if plan.get("massing") and parti.get("massing") and plan["massing"] not in massings:
        found.append({"kind": "massing", "room": None,
                      "statement": f'the plan is massed {plan["massing"]} and the parti is '
                                   f'{parti.get("massing")}'
                                   + (f' (or {", ".join(m for m in massings[1:])})' if massings[1:] else "")})
    return found


# Findings a parti may not fail a plan on, and the count that may only fall. Two today, both on
# `plans/tidewater-georgian-careful.json`, both the hyphen-and-dependency reading the parti has no
# vocabulary for: `backhall` N/S against the parti's E/N, and `kitchen` N/S/W against E/N. They go
# to zero when WP-11.6 gives the diagram the elements its exemplars have.
REPORTED = {"exterior-walls"}
EXPOSURE_CEILING = 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plans", nargs="*")
    ap.add_argument("--strict", action="store_true",
                    help="a plan that names no parti is a FAILURE rather than an unjudged")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rows, unjudged, bad, exposure = [], [], 0, 0
    for path in plan_paths(a.plans):
        try:
            plan = json.load(open(path, encoding="utf-8"))
        except Exception as e:  # a malformed plan is validate.py's finding, not this one's
            continue
        rel = os.path.relpath(path, ROOT)
        pid = plan.get("parti")
        if not pid:
            unjudged.append(rel)
            continue
        parti = load_parti(pid)
        if parti is None:
            rows.append((rel, [{"kind": "no-such-parti", "room": None,
                                "statement": f'the plan names the parti {pid} and no such record '
                                             f'exists'}]))
            bad += 1
            continue
        found = check_plan(plan, parti)
        if found:
            rows.append((rel, found))
            hard = [f for f in found if f["kind"] not in REPORTED]
            exposure += len(found) - len(hard)
            if hard:
                bad += 1

    if a.json:
        print(json.dumps({"findings": {r: f for r, f in rows}, "unjudged": unjudged}, indent=1))
    else:
        for rel, found in rows:
            print(f"\n{rel}")
            for f in found:
                where = f"{f['room']}: " if f.get("room") else ""
                print(f"  · [{f['kind']}] {where}{f['statement']}")
        if unjudged:
            print(f"\nUNJUDGED — {len(unjudged)} plan(s) name no parti, so nothing here could be "
                  f"held against a diagram:")
            for rel in unjudged:
                print(f"  · {rel}")
            print("  A plan that names its parti is a plan whose diagram can be checked; naming "
                  "one is an authoring act and this is not a failure.")
        n = len(plan_paths(a.plans))
        print(f"\n{n - len(unjudged)} of {n} plan(s) checked against a named parti; "
              f"{bad} with a topology finding, {exposure} exposure finding(s) reported "
              f"(ceiling {EXPOSURE_CEILING}), {len(unjudged)} unjudged.")
    if exposure > EXPOSURE_CEILING:
        print(f"\nRATCHET: {exposure} exposure finding(s) against a ceiling of "
              f"{EXPOSURE_CEILING}. This number may go DOWN when a plan or a parti is corrected "
              f"and may not go up: a new one means a record has quietly stopped describing its "
              f"own diagram, which is the whole subject of this file.", file=sys.stderr)
        return 1
    if a.strict and unjudged:
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
