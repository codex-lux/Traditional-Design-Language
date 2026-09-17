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
  · every `block` and `hyphen` tag the parti states for a room the plan carries is stated by it;
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
dependency (N, S and W), where the parti puts both on E and N. It is counted and ratcheted
instead. `stacks_over`, doors, room existence and the massing tags ARE topology and they fail.

**THE CLAUSE THIS PARAGRAPH USED TO CARRY WAS TRUE UNTIL THE COMMIT THAT CORRECTS IT.** It read
*"the parti — which has no hyphen and no dependency"*, and at WP-13.5 the parti has both: the
kitchen, pantry, breakfast room and powder room carry `block: service` and the back hall carries
`hyphen: true`. The DISAGREEMENT survives and the ceiling does not move, because it was never
about the elements existing — the parti states its service wing to the EAST (`kitchen` E/N) and
this plan builds it to the WEST (`kitchen` N/S/W), and `geometry.flank_sizes` reads the side off
those very letters, so the two records really do describe mirror-image houses. Both are instances
of the diagram and neither is wrong; that is why this kind reports. Erasing either to make the
count fall would delete a record's own account of its house, which is the move this file exists
to refuse. `oq/the-parti-dissolved-its-own-dependencies` is no longer what shows through here.

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


def _element_tag(room):
    """Which massing element the PLAN puts this room in, read from its own declared tag.

    `geometry.is_block_tag` is the ONE rule for whether a `block` field is an element id, and it
    is borrowed rather than re-spelled: its own docstring records that two readers answering
    this differently is how a room comes to be sized into one element and placed in another.
    An untagged room is in the main block, which is the answer a record written before the field
    existed already gets."""
    g = _mod("geometry", os.path.join(ROOT, "build", "geometry.py"))
    return room.get("block") if g.is_block_tag(room.get("block")) else "main"


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

        # THE MASSING TAGS, and they are topology rather than exposure. `build/compose.py`
        # copies `block` and `hyphen` onto every candidate it writes, exactly as it copies
        # `stacks_over` — so a composed plan is correct by construction and a HAND-AUTHORED one
        # is checked by nothing, which is the defect at the head of this file arriving in a
        # second field. They are not dimensions (decision #3's limit on a parti's authority):
        # `block` says which rooms share a volume and `hyphen` says which single room is the
        # link, and `geometry.blocks_for` lays the house out from both. A plan that answers
        # differently from its diagram is describing a different composition, not a different
        # size, so unlike `exterior_walls` this FAILS.
        #
        # The comparison is two-sided on purpose. A plan that drops the tag puts the room back
        # in the main block; a plan that names ANOTHER element puts it in a volume the diagram
        # does not have; and `hyphen` without `block` is meaningless (the parti schema says so
        # in as many words). All three are one question — which element is this room in — and
        # reporting only the first would let the other two through in silence.
        for field, prose in (("block", "in massing element"), ("hyphen", "the hyphen of")):
            want, got = room.get(field), have.get(field)
            if want in (None, False) or want == got:
                continue
            found.append({"kind": "massing-element", "room": rid,
                          "statement": f'the parti puts {rid} {prose} '
                                       f'{want if field == "block" else "its element"} and the '
                                       f'plan says {got if got not in (None, False) else "nothing"} '
                                       f'— geometry.blocks_for lays the house out from this field'})

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
            # A DOOR BETWEEN TWO MASSING ELEMENTS IS THE SAME KIND OF STATEMENT AS AN EXPOSURE,
            # and the paragraph in this file's own docstring that carved `exterior_walls` out is
            # the argument for it (WP-11.16). A parti states topology; whether two rooms CAN
            # share a door is a consequence of the MASSING, which decision #3 puts outside a
            # parti's authority. `centre-passage-double-pile` has no dependency and gives the
            # butler's pantry a direct door to the kitchen; the shipped Tidewater plan puts the
            # kitchen in a detached dependency, where `rooms/butlers-pantry.json` has said since
            # OQ 59 that in this type "the pantry is in the block and the kitchen is in another
            # building". Keeping the door to satisfy the diagram would put a door in the record
            # that BOTH engines report unplaced for ever -- measured, 2 of the 4 unplaced doors
            # on the proved placement -- and would let the servicing layer pass those two rooms
            # as a wet pair across a 27 ft gap. Erasing it to make this checker quiet would
            # delete the record's own account of the house, which is the sentence above.
            # NARROW ON PURPOSE: only where the PLAN ITSELF puts the two rooms in different
            # elements. Same element, or a one-rectangle plan, and a missing door still FAILS.
            kind = "door"
            if d in pr and _element_tag(have) != _element_tag(pr[d]):
                kind = "door-across-elements"
            found.append({"kind": kind, "room": rid,
                          "statement": f'the parti gives {rid} a door to {d} and the plan '
                                       f'declares none'
                                       + ('' if kind == "door" else
                                          f' — the plan puts them in different massing elements '
                                          f'({_element_tag(have)} and {_element_tag(pr[d])}), '
                                          f'which the parti has no vocabulary for')})

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


# Findings a parti may not fail a plan on, and the counts that may only fall. There are TWO kinds
# and they keep separate ceilings, because the two parallel lines added one each and they measure
# different things: `exterior-walls` is an exposure the plan recast, `door-across-elements` is a
# door the parti declares between two rooms the PLAN puts in different massing elements. One
# number for both would let a new door hide behind a corrected exposure.
#
# TWO PREDICTIONS WERE FALSIFIED HERE AND BOTH ARE KEPT, because each was wrong its own way.
# This comment used to say the exposure findings *"go to zero when WP-11.6 gives the diagram the
# elements its exemplars have"*. WP-11.6 tried exactly that and `check_partis.py` refused all three
# arrangements, each by a HARD room rule -- the butler's pantry must directly door both the dining
# room and the kitchen, and no boundary can be drawn that keeps both. The elements arrived on the
# PLAN instead -- WP-11.16 on one line and WP-13.5 on the other, the same edit made twice by two
# sessions that could not see each other -- and the exposure count was then MEASURED unmoved at 2,
# because the disagreement is about which SIDE of the house the wing stands on: the parti states
# its service wing E/N, this plan builds it N/S/W, and `geometry.flank_sizes` reads the side off
# those very letters. Both records describe an instance of the diagram and neither is wrong, which
# is why this kind reports. `oq/the-parti-dissolved-its-own-dependencies` is what takes the
# exposure count to zero and it is a ruling nobody has given.
#
# AND THE CROSS-ELEMENT DOOR CEILING IS A THIRD VALUE AT THIS MERGE, BELONGING TO NEITHER PARENT.
# The kind was added for the two halves of the direct `butlers`-`kitchen` door, which one parent
# dropped from the PLAN while the parti went on declaring it -- two findings. The other parent
# dropped it from `partis/centre-passage-double-pile.json` as well, for
# `rooms/butlers-pantry.json`'s own OQ 59 reason, so on the merged corpus the parti declares no
# such door and there is nothing left to report. The ceiling is re-derived below rather than taken
# from either side. The kind is NOT deleted: a ceiling of zero on a corpus that cannot reach the
# branch is exactly the shape that reads as a guard passing, so it is DRIVEN by a hand-built pair
# in `tests/test_check_plans.py` instead of resting on the corpus.
REPORTED = {"exterior-walls", "door-across-elements"}
EXPOSURE_CEILING = 2
# RE-DERIVED ON THE MERGED TREE, not taken from either parent: `python3 build/check_plans.py`
# reads "2 exposure finding(s) reported, 0 cross-element door finding(s)". One parent measured 2
# here and the other never had the kind; 0 is the third value, and it is a ceiling that may only
# fall, so it falls. See the comment above for why the kind is kept at zero rather than deleted.
CROSS_ELEMENT_DOOR_CEILING = 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plans", nargs="*")
    ap.add_argument("--strict", action="store_true",
                    help="a plan that names no parti is a FAILURE rather than an unjudged")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rows, unjudged, bad, exposure, xdoor = [], [], 0, 0, 0
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
            exposure += sum(1 for f in found if f["kind"] == "exterior-walls")
            xdoor += sum(1 for f in found if f["kind"] == "door-across-elements")
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
              f"(ceiling {EXPOSURE_CEILING}), {xdoor} cross-element door finding(s) reported "
              f"(ceiling {CROSS_ELEMENT_DOOR_CEILING}), {len(unjudged)} unjudged.")
    if xdoor > CROSS_ELEMENT_DOOR_CEILING:
        print(f"\nRATCHET: {xdoor} cross-element door finding(s) against a ceiling of "
              f"{CROSS_ELEMENT_DOOR_CEILING}. A door the parti declares between two rooms the "
              f"plan puts in different massing elements is REPORTED rather than failed, and the "
              f"licence is bounded: a new one means a diagram and a record have drifted further "
              f"apart, not that the licence has grown.", file=sys.stderr)
        return 1
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
