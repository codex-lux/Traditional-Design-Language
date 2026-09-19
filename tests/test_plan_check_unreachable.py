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

from conftest import load_plan

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
import modcache as mc  # noqa: E402

PC = mc.load("plan_check", os.path.join(BUILD, "plan_check.py"))
GEO = mc.load("geometry", os.path.join(BUILD, "geometry.py"))


@pytest.fixture(scope="module")
def rows():
    placed = GEO.solve(load_plan("tidewater-georgian-careful"), engine="heuristic")
    return [f for f in PC.check(placed)["findings"] if f.get("kind") == "unreachable"]


def test_the_premise_holds_this_plan_strands_rooms(rows):
    assert len(rows) >= 5, f"no stranded rooms to describe: {len(rows)}"


def test_every_stranded_room_states_what_was_realised_and_the_arithmetic_holds(rows):
    for f in rows:
        assert "realised_doors" in f, f["id"]
        assert f["realised_doors"] == max(0, f["declared_doors"] - len(f["unplaced_pairs"])), f["id"]
        assert 0 <= f["realised_doors"] <= f["declared_doors"]


def test_a_room_whose_doors_were_all_placed_is_not_told_none_of_them_were(rows):
    """The defect, in its exact form. `primary` declares three doors, its `unplaced_pairs` is
    empty, and it was told the placement realised none of them."""
    allplaced = [f for f in rows if f["realised_doors"] == f["declared_doors"] and f["declared_doors"]]
    assert allplaced, "premise: some stranded room had all its declared doors placed"
    for f in allplaced:
        assert "realised none of them" not in f["statement"], f["id"]
        assert "realised all of them" in f["statement"], f["statement"]


def test_a_room_whose_doors_were_partly_placed_says_how_many(rows):
    partial = [f for f in rows if 0 < f["realised_doors"] < f["declared_doors"]]
    assert partial, "premise: some stranded room had some of its doors placed"
    for f in partial:
        assert f"realised {f['realised_doors']}" in f["statement"], f["statement"]
        assert "realised none of them" not in f["statement"]


def test_a_room_whose_doors_were_all_unplaced_keeps_the_original_sentence(rows):
    """The old wording was right for this case and is unchanged: a sentence that was true of
    four of the ten must not be lost in correcting it for the other six."""
    none_ = [f for f in rows if f["declared_doors"] and f["realised_doors"] == 0]
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
