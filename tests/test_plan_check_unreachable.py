"""WP-13.9 -- the `unreachable` finding says what the placement actually did with the doors.

The sentence read "The record declares N door(s) to it and the placement realised none of
them" for EVERY stranded room. Measured on `plans/tidewater-georgian-careful.json` at
`engine="heuristic"`, that is false of five of the ten: three rooms had all their declared
doors placed and two had some, and every one of them was told none. The room is cut off
because the cluster it belongs to is, and a reader (or a generator) sent after the wrong cause
by a confident sentence is the defect this corpus names first.

The number to say it with was already in hand: `unplaced_pairs` is computed by the same loop
and was attached to the finding as evidence while the prose contradicted it.
"""
import os
import sys

import pytest

from conftest import load_plan, load_reference_plan

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
import modcache as mc  # noqa: E402

PC = mc.load("plan_check", os.path.join(BUILD, "plan_check.py"))
GEO = mc.load("geometry", os.path.join(BUILD, "geometry.py"))


# BOTH SHIPPED PLANS, AND THE SECOND ONE IS HERE BECAUSE THE FIRST VERSION OF THIS FILE RAN
# ONLY ON THE FIRST. `tidewater-georgian-careful`'s door declarations are symmetric -- every
# door is written on both of its rooms -- and `spec-builder-colonial`'s are not, which is the
# only shipped plan where the arithmetic under test can be wrong. It was wrong, and this file
# certified it: see `test_a_room_whose_doors_were_all_unplaced...` below.
PLANS = ["tidewater-georgian-careful", "spec-builder-colonial"]


def _rows(pid):
    placed = GEO.solve(load_plan(pid), engine="heuristic")
    rooms = {r["id"]: r for lv in placed["levels"] for r in lv["rooms"]}
    out = []
    for f in PC.check(placed)["findings"]:
        if f.get("kind") == "unreachable":
            out.append((f, rooms[f["room"]]))
    return out


@pytest.fixture(scope="module")
def rows():
    return [pair for pid in PLANS for pair in _rows(pid)]


def _truly_realised(room):
    """The answer DERIVED, from the placed record's own door flags -- never from the
    expression under test. The first version of this file asserted
    `realised_doors == max(0, declared_doors - len(unplaced_pairs))`, which is the production
    line character for character: a tautology that could not go red at any state of the code,
    shipped in the same commit whose mutation sweep caught one blind test and named the class.
    `unplaced_pairs` is a deduplicated PAIR set minted by whichever room declared the door;
    this is a count of THIS room's own declarations, which is what the prose claims."""
    return sum(1 for d in (room.get("doors") or []) if not d.get("unplaced"))


def test_the_premise_holds_these_plans_strand_rooms(rows):
    assert len(rows) >= 8, f"no stranded rooms to describe: {len(rows)}"


def test_the_premise_holds_some_room_declares_a_door_its_neighbour_does_not(rows):
    """The condition the miscount needed, asserted so it cannot quietly disappear: if every
    shipped declaration becomes symmetric, the guard below stops being about anything and this
    says so rather than going green."""
    asym = [f["room"] for f, room in rows
            if len(f["unplaced_pairs"]) > sum(1 for d in (room.get("doors") or []) if d.get("unplaced"))]
    assert asym, ("no stranded room is named by a pair it did not declare -- the case "
                  "`realised_doors` was getting wrong is no longer in the corpus")


def test_every_stranded_room_states_what_was_realised(rows):
    for f, room in rows:
        assert "realised_doors" in f, f["id"]
        assert f["realised_doors"] == _truly_realised(room), (
            f"{f['id']}: the finding says {f['realised_doors']} of its declared doors were "
            f"placed and the record says {_truly_realised(room)}")
        assert 0 <= f["realised_doors"] <= f["declared_doors"]


def test_a_room_whose_doors_were_all_placed_is_not_told_none_of_them_were(rows):
    """The defect, in its exact form. `primary` declares three doors, its `unplaced_pairs` is
    empty, and it was told the placement realised none of them.

    SELECTED ON THE DERIVED COUNT, never on `realised_doors`. Selecting on the field under test
    is how the first version of this file certified the falsehood it was written to catch: a
    room miscounted as 0 fell into the "all unplaced" test below, which then asserted it had
    been given the "realised none of them" sentence -- and it had."""
    allplaced = [f for f, room in rows
                 if _truly_realised(room) == f["declared_doors"] and f["declared_doors"]]
    assert allplaced, "premise: some stranded room had all its declared doors placed"
    for f in allplaced:
        assert "realised none of them" not in f["statement"], f["id"]
        assert "realised all of them" in f["statement"], f["statement"]


def test_a_room_whose_doors_were_partly_placed_says_how_many(rows):
    partial = [(f, room) for f, room in rows if 0 < _truly_realised(room) < f["declared_doors"]]
    assert partial, "premise: some stranded room had some of its doors placed"
    for f, room in partial:
        assert f"realised {_truly_realised(room)}" in f["statement"], f["statement"]
        assert "realised none of them" not in f["statement"]


def test_a_room_whose_doors_were_all_unplaced_keeps_the_original_sentence(rows):
    """The old wording was right for this case and is unchanged: a sentence that was true of
    four of the ten must not be lost in correcting it for the other six."""
    none_ = [f for f, room in rows if f["declared_doors"] and _truly_realised(room) == 0]
    assert none_, "premise: some stranded room had none of its doors placed"
    for f in none_:
        assert "realised none of them" in f["statement"], f["statement"]


def test_a_room_declaring_no_door_at_all_is_still_told_so():
    """DRIVEN: every stranded room on the shipped corpus declares at least one door, so this
    branch is unreachable from the data and would otherwise be a promise rather than a
    behaviour (WP-8.11's rule)."""
    plan = load_plan("tidewater-georgian-careful")
    placed = GEO.solve(plan, engine="heuristic")
    for lv in placed["levels"]:
        for r in lv["rooms"]:
            if r["id"] == "library":
                r["doors"] = []
    rows = [f for f in PC.check(placed)["findings"] if f.get("kind") == "unreachable"]
    lib = next((f for f in rows if f["room"] == "library"), None)
    assert lib is not None, "the driven room is still stranded"
    assert lib["declared_doors"] == 0 and lib["realised_doors"] == 0
    assert "declares no door to it at all" in lib["statement"]


# ---------------------------------------------------------------- the cut-off layer's silence
# WP-13.9's adversarial audit. `cut-off` is a SECOND finding kind in the same block, and it
# carried the same false sentence unconditionally -- and, more seriously, it said NOTHING AT ALL
# on a plan where no exterior door is placed, which is where a room joined to nothing most needs
# saying. Both are the reachability layer's, so both are guarded here.

def _cutoff(pid, mutate=None):
    plan = load_reference_plan(pid) if pid.startswith(("bad-", "good-")) else load_plan(pid)
    if mutate:
        mutate(plan)
    placed = GEO.solve(plan, engine="heuristic")
    rooms = {r["id"]: r for lv in placed["levels"] for r in lv["rooms"]}
    found = PC.check(placed)["findings"]
    return ([f for f in found if f.get("kind") == "cut-off"],
            [f for f in found if f.get("kind") == "no-outside"], rooms)


def test_a_plan_with_no_way_in_is_not_silent_about_rooms_joined_to_nothing():
    """THE DEDUP GUARD INVERTED WHERE THERE WAS NO OUTSIDE. The `cut-off` loop skips a room
    already reported `unreachable`, testing `rid not in seen` -- and `seen` is seeded from
    `outside`, so on a plan where not one exterior door is placed it is EMPTY and the line
    skipped EVERY room. The whole layer went quiet on exactly the houses that need it, and
    nothing was reported unreachable there either, so there was no restatement to avoid.

    Measured over the sixteen shipped plans on `engine="heuristic"`: cut-off rows 2 -> 26, the
    24 new ones on five plans (bad-01 7, bad-05 10, good-03 3, good-05 3, bad-04 1). This
    drives the state rather than naming one of those, so a corpus that stops producing it
    fails here rather than going quietly green."""
    rows, noout, rooms = _cutoff("bad-05-two-story-spec-colonial")
    assert noout, "premise: this plan places no exterior door, so the walk has no outside"
    assert rows, "a plan with no way in said nothing about rooms joined to nothing"
    for f in rows:
        r = rooms[f["room"]]
        interior = [d for d in (r.get("doors") or []) if d["to"] != "exterior"]
        assert f["declared_doors"] == len(interior)
        assert f["realised_doors"] == sum(1 for d in interior if not d.get("unplaced"))
        assert "joins no other room on the drawing" in f["statement"]


def test_the_dedup_still_holds_where_there_IS_an_outside():
    """The other half, and the reason the guard exists at all: a room already convicted of
    being unreachable must not be convicted a second time under another name. Loosening the
    condition to drop the dedup entirely would inflate every plan's troubles with a
    restatement, so the two states are asserted together."""
    rows, noout, _ = _cutoff("spec-builder-colonial")
    assert not noout, "premise: this plan places an exterior door"
    placed = GEO.solve(load_plan("spec-builder-colonial"), engine="heuristic")
    unre = {f["room"] for f in PC.check(placed)["findings"] if f.get("kind") == "unreachable"}
    assert unre, "premise: this plan strands rooms"
    assert not (unre & {f["room"] for f in rows}), "a room is reported twice for one defect"


def test_the_cut_off_sentence_says_how_many_were_realised():
    """One spelling of "how many of this room's doors did the placement seat", shared with the
    `unreachable` branch above it. MEASURED over the sixteen plans: 26 rows, 0 with a realised
    interior door, so this changes no sentence in the corpus today -- and the branch is not
    dead, because `ok_edges` mints an edge only where a door's `to` NAMES A ROOM, so a placed
    door pointing at a room the plan does not hold leaves it reachable. DRIVEN for that reason."""
    # Driven AFTER the placement, because `openings.place` cannot seat a door whose target is
    # not a room: the state under test is a PLACED door naming a room the plan does not hold,
    # which is reachable only by editing the placed record. One room is given a seated door to
    # nowhere and every other door of its own is unplaced, so it joins nothing and the count
    # the sentence quotes is not zero.
    placed = GEO.solve(load_plan("spec-builder-colonial"), engine="heuristic")
    victim = None
    for lv in placed["levels"]:
        for r in lv["rooms"]:
            ds = [d for d in (r.get("doors") or []) if d["to"] != "exterior"]
            out = [d for d in (r.get("doors") or []) if d["to"] == "exterior"
                   and not d.get("unplaced")]
            # it must still be REACHABLE, or it is reported `unreachable` and the dedup above
            # correctly keeps it out of this list -- one defect is not said twice
            if ds and out and victim is None:
                victim = r["id"]
                ds[0]["to"] = "no-such-room-on-this-plan"
                ds[0].pop("unplaced", None)
                for d in ds[1:]:
                    d["unplaced"] = "driven: no shared wall"
    assert victim, "premise: some room has a placed exterior door and an interior one"
    rows = [f for f in PC.check(placed)["findings"] if f.get("kind") == "cut-off"]
    some = [f for f in rows if f["room"] == victim and f.get("realised_doors", 0) > 0]
    assert some, ("the driven room places a door that names no room on the plan; "
                  f"cut-off rows {[f['room'] for f in rows]}")
    assert "they open into nothing this drawing holds" in some[0]["statement"]
    assert "realised none of them" not in some[0]["statement"]
