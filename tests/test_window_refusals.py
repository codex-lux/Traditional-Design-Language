"""WHAT A REFUSED WINDOW IS SAID TO BE REFUSED FOR (Phase 15, WP-15.8, the audit).

Three defects in one chain, each measured on the sixteen shipped plans before it was touched:

1. **The placer's reason named doors that were not there.** `openings._place_windows` wrote "the wall
   has no clear run left beside its doors" whatever took the run. 7 of the 9 refusals for want of
   run stand on a wall carrying no door: the Tidewater dining and library walls were taken by the
   chimney breast and its stack, and the five partial refusals by the window's own first units.
   `openings._beside` names what is on the run now.
2. **The plate's line counted a partly refused window at its whole count**, so on five sheets the
   reasons summed past the headline -- the Tidewater plate read "19 OF 35 ... NOT DRAWN" over
   buckets of 16, 2 and 2 -- and the short-form table knew only the bare "beside its doors", its
   partial key having matched nothing since WP-13.2 appended "beside ...".
3. **The critic called a room "drawn with no window" when any unit of its window was refused**, on
   four shipped plans whose sheets draw one or two sashes in that room -- a serious finding the
   drawing contradicts -- and told a room whose window stands on its own lit wall to move the
   window to that wall.

Expectations are read from the placed records and the refusal reasons themselves, never written as
room names: a literal list would be one placement's luck.
"""
import copy
import glob
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _L(n):
    return modcache.load(n, os.path.join(ROOT, "build", n + ".py"))


GEO, OP, PC, DISC = (_L(n) for n in ("geometry", "openings", "plan_check", "disclosures"))

RUN_REASON = re.compile(r"^(?:the wall has no clear run left|\d+ of \d+ unit\(s\) had no clear "
                        r"run left on this wall) beside (.+)$")


def _plans():
    return (sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))
            + sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))))


@pytest.fixture(scope="module")
def corpus():
    out = {}
    saved = GEO._SOLVE_CACHE
    GEO._SOLVE_CACHE = {}
    try:
        for p in _plans():
            with open(p, encoding="utf-8") as fh:
                out[os.path.basename(p)[:-5]] = GEO.solve(json.load(fh), None, 250,
                                                          engine="heuristic")
    finally:
        GEO._SOLVE_CACHE = saved
    assert len(out) == 16, "the premise: the sixteen shipped plans"
    return out


def _windows(placed):
    for lv in placed["levels"]:
        for r in lv["rooms"]:
            for w in r.get("windows") or []:
                yield lv, r, w


# ------------------------------------------------------------------ 1. the placer's reason
def test_a_refusal_names_the_doors_only_where_a_door_stands_on_the_run(corpus):
    """Every refusal for want of run names "its doors" exactly where a door's placed span lies on
    that wall, and names the windows already seated exactly where a unit is seated there."""
    seen = {"doors": 0, "no-doors": 0, "partial": 0}
    for pid, placed in corpus.items():
        for _lv, r, w in _windows(placed):
            reason = (w.get("unplaced") or {}).get("reason") or ""
            m = RUN_REASON.match(reason)
            if not m:
                continue
            names = m.group(1).split(" and ")
            doors = [d for d in (r.get("doors") or [])
                     if d.get("wall") == w.get("wall") and d.get("position_ft") is not None]
            assert ("its doors" in names) == bool(doors), (pid, r["id"], reason, doors)
            seen["doors" if doors else "no-doors"] += 1
            if w.get("positions_ft"):
                assert "the windows already seated on it" in names, (pid, r["id"], reason)
                seen["partial"] += 1
    assert seen["doors"] >= 1 and seen["no-doors"] >= 1 and seen["partial"] >= 1, seen


def _room(wall_ft, windows, doors=()):
    return {"id": "r", "geometry": {"x_ft": 0.0, "y_ft": 0.0, "width_ft": wall_ft, "depth_ft": 12.0},
            "windows": copy.deepcopy(list(windows)), "doors": list(doors)}


def test_each_cause_is_named_and_none_is_invented():
    """DRIVEN, one cause at a time, because the corpus reaches the door and the partial cases and
    no wall too short for its window: a door on the run, the window's own first units, and a bare
    wall shorter than the window, each against a control with the cause removed."""
    # a door took the run
    room = _room(6.0, [{"wall": "S", "count": 1, "width_ft": 3.0}])
    occ = {("r", "S"): [(0.0, 5.0)]}
    OP._place_windows([room], occ, 30.0, 30.0, {"windows_placed": 0, "windows_unplaced": 0})
    assert room["windows"][0]["unplaced"]["reason"] == \
        "the wall has no clear run left beside its doors", room
    # the window's own first unit took it
    room = _room(6.0, [{"wall": "S", "count": 2, "width_ft": 3.0}])
    OP._place_windows([room], {}, 30.0, 30.0, {"windows_placed": 0, "windows_unplaced": 0})
    w = room["windows"][0]
    assert len(w["positions_ft"]) == 1, w
    assert w["unplaced"]["reason"] == ("1 of 2 unit(s) had no clear run left on this wall beside "
                                       "the windows already seated on it"), w
    # nothing took it: the wall is shorter than the window
    room = _room(2.5, [{"wall": "S", "count": 1, "width_ft": 3.0}])
    OP._place_windows([room], {}, 30.0, 30.0, {"windows_placed": 0, "windows_unplaced": 0})
    assert room["windows"][0]["unplaced"]["reason"] == "the wall is shorter than the window", room
    # control: a door on ANOTHER wall is not named
    room = _room(2.5, [{"wall": "S", "count": 1, "width_ft": 3.0}])
    occ = {("r", "N"): [(0.0, 2.0)]}
    OP._place_windows([room], occ, 30.0, 30.0, {"windows_placed": 0, "windows_unplaced": 0})
    assert "doors" not in room["windows"][0]["unplaced"]["reason"], room


# ------------------------------------------------------------------ 2. the plate's line
def _line_counts(text):
    head, _, tail = text.partition(" — ")
    n = int(head.split(" OF ")[0])
    parts = [int(m.group(1)) for m in re.finditer(r"(?:^|, )(\d+) ", tail)]
    return n, parts


def test_the_reasons_on_the_plate_sum_to_the_windows_not_drawn(corpus):
    """On every shipped plan the reason buckets add up to the headline. A partly refused window
    counts the units it did not draw, not its whole count."""
    partial = 0
    for pid, placed in corpus.items():
        line = DISC.windows_not_drawn(placed)
        if not line:
            continue
        n, parts = _line_counts(line["text"])
        assert n == placed["opening_report"]["windows_unplaced"], (pid, line["text"])
        assert sum(parts) == n, (pid, line["text"])
        partial += sum(1 for _lv, _r, w in _windows(placed)
                       if w.get("unplaced") and w.get("positions_ft"))
    assert partial >= 1, "the premise: some shipped window is partly refused"


def test_every_reason_the_placer_writes_has_a_short_form():
    """No run refusal reaches the plate as its whole sentence, and a partial and a whole refusal
    beside the same things share one bucket."""
    names = ["its doors", "the windows already seated on it", "the chimney breast",
             "the chimney stack", "the entrance doorcase"]
    for i in range(1, 1 << len(names)):
        beside = " and ".join(n for k, n in enumerate(names) if i & (1 << k))
        whole = DISC._group(f"the wall has no clear run left beside {beside}")
        part = DISC._group(f"1 of 3 unit(s) had no clear run left on this wall beside {beside}")
        assert whole == part and whole.startswith("no clear run beside "), (beside, whole, part)
        assert "its " not in whole and "on it" not in whole, whole
    assert DISC._group("the wall has no clear run left beside its doors") == \
        "no clear run beside the doors", "the bucket every earlier sheet printed is unchanged"
    assert DISC._group("the wall is shorter than the window") == "a wall shorter than the window"
    assert DISC._group("1 of 2 unit(s) had no clear run left on this wall") == \
        "no clear run left on the wall", "a record written before WP-13.2 still groups"


# ------------------------------------------------------------------ 3. the critic
def test_a_room_that_draws_a_window_is_not_said_to_draw_none(corpus):
    """The finding fires only where no unit of any declared window is drawn; the premise is a room
    whose only window is partly refused, which is the case the old test convicted."""
    convicted, partly = 0, 0
    for pid, placed in corpus.items():
        rooms = {r["id"]: r for lv in placed["levels"] for r in lv["rooms"]}
        for f in PC.check(placed)["findings"]:
            if f.get("kind") != "drawn-window-off-the-placed-wall":
                continue
            wins = rooms[f["room"]].get("windows") or []
            assert not any(w.get("positions_ft") for w in wins), (pid, f["room"], f["statement"])
            convicted += 1
        partly += sum(1 for r in rooms.values() for w in r.get("windows") or []
                      if w.get("unplaced") and w.get("positions_ft"))
    assert convicted >= 1 and partly >= 1, (convicted, partly)


def test_the_fix_follows_the_cause(corpus):
    """A window declared on a wall the room stands on and refused there for want of run is told to
    free the run, never to move to the wall it is already on; one declared on a wall the room does
    not reach keeps the old sentence, word for word."""
    crowded, off = 0, 0
    for pid, placed in corpus.items():
        rooms = {r["id"]: r for lv in placed["levels"] for r in lv["rooms"]}
        for f in PC.check(placed)["findings"]:
            if f.get("kind") != "drawn-window-off-the-placed-wall":
                continue
            walls = {w.get("wall") for w in rooms[f["room"]].get("windows") or []}
            lit = set(f.get("lit_walls") or [])
            if walls & lit:
                assert "does stand on its" in f["fix"], (pid, f["room"], f["fix"])
                for wall in walls & lit:
                    assert wall in f["fix"], (pid, f["room"], wall, f["fix"])
                crowded += 1
            else:
                assert f["fix"] == "Move the windows to the wall the placement actually gave the room."
                off += 1
            for reason in f.get("refused") or []:
                assert reason in f["statement"], (pid, f["room"], reason)
    assert crowded >= 1 and off >= 1, (crowded, off)


# ------------------------------------------- 4. a window refused whole keeps no old positions
def _wholesale(reason):
    """Which of the placer's three WHOLE refusals a reason is, or None for a partial one."""
    if reason == "the room is not placed on this level":
        return "level"
    if reason.startswith("the placement puts this room on no such boundary wall"):
        return "wall"
    if reason.startswith(("the wall has no clear run left", "the wall is shorter than")):
        return "run"
    return None


def test_a_window_refused_whole_keeps_no_positions_it_came_in_with(corpus):
    """WP-15.8's audit (second-order pass). Three readers take `unplaced` beside a non-empty
    `positions_ft` as a PARTIAL refusal -- the critic's "drawn with no window", the plate's windows
    line and the elevation's refused list -- and the placer's three whole-refusal paths left any
    positions a record came in with. The bench's evaluate and MCP `place_plan` place whatever they
    are handed, so a placed record re-solved after an edit carried a refused window's old seat and
    every "drawn with no window" finding vanished, on all sixteen plans, over a sheet that drew no
    such window. Each path is driven from a plan that reaches it, with stale positions put on every
    window, and the findings must be the clean solve's."""
    paths = {os.path.basename(p)[:-5]: p for p in _plans()}
    kinds = {}
    for pid, placed in corpus.items():
        for _lv, _r, w in _windows(placed):
            if w.get("unplaced") and not w.get("positions_ft"):
                k = _wholesale(w["unplaced"]["reason"])
                if k:
                    kinds.setdefault(k, pid)
    assert set(kinds) == {"level", "wall", "run"}, ("the premise: each whole refusal is reached", kinds)

    def findings(placed):
        return sorted((f["room"], f["statement"]) for f in PC.check(placed)["findings"]
                      if f.get("kind") == "drawn-window-off-the-placed-wall")

    for kind, pid in sorted(kinds.items()):
        with open(paths[pid], encoding="utf-8") as fh:
            declared = json.load(fh)
        stale = 0
        for lv in declared["levels"]:
            for r in lv["rooms"]:
                for w in r.get("windows") or []:
                    w["positions_ft"] = [1.0]
                    stale += 1
        saved = GEO._SOLVE_CACHE
        GEO._SOLVE_CACHE = {}
        try:
            placed = GEO.solve(declared, None, 250, engine="heuristic")
        finally:
            GEO._SOLVE_CACHE = saved
        hit = 0
        for _lv, r, w in _windows(placed):
            k = _wholesale(((w.get("unplaced") or {}).get("reason")) or "")
            if k:
                assert not w.get("positions_ft"), (kind, pid, r["id"], w)
                hit += k == kind
        assert stale and hit, (kind, pid, stale, hit)
        assert findings(placed) == findings(corpus[pid]), (kind, pid)
        line = DISC.windows_not_drawn(placed)
        assert line, (kind, pid)
        n, parts = _line_counts(line["text"])
        assert n == placed["opening_report"]["windows_unplaced"] == sum(parts), (kind, pid, line["text"])
