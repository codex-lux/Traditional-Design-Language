"""WP-16.6: the wall between two windows, and the storey above on the storey below.

Lucas ruled on 29 Sep 2026 (`oq/the-placer-seats-windows-a-foot-apart-and-the-corpus-states-the-pier-three-ways`):

  R5   a floor of 1.0 x the wider window between two windows, an aim of 1.4 x where the wall
       allows, and a window that cannot be seated refused by name;
  R5a  the centre holds -- windows nearer the entrance, or on other faces nearer the face's
       centre, keep their places, and the outer window moves along its own wall or is refused;
  R5b  the five styles the pier fault licenses are spared, read off the licence's style list;
  R6   the upper window moves onto the axis of the ground opening below it, or is refused by name
       where its own room cannot take it there;
  R6a  an upper window with no ground opening under its room's run stays where it is placed.

`build/window_pier.py` is the one reader of the floor, the aim and the spared styles, and
`openings._place_windows` seats to them. These tests hold the reader to the records it reads and
drive the seating on hand-built rooms, because the shipped corpus reaches some of the branches
and not others: no shipped plan places a spared style on two storeys, and no shipped fault states
a different floor.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _b(name):
    return modcache.load(name, os.path.join(ROOT, "build", name + ".py"))


WP, OP, EL = _b("window_pier"), _b("openings"), _b("elevation")
FAULT = os.path.join(ROOT, "faults", "pier-narrower-than-the-opening.json")


def _fault():
    with open(FAULT, encoding="utf-8") as fh:
        return json.load(fh)


def _write(tmp_path, rec):
    p = tmp_path / "pier.json"
    p.write_text(json.dumps(rec))
    return str(p)


# ------------------------------------------------------------------ the one reader
class TestTheReader:
    def test_the_floor_is_the_faults_own_threshold(self):
        f, src = WP.floor()
        t = _fault()["test"]
        assert (t["direction"], t["units"]) == ("at-least", "ratio")
        assert f == t["threshold"] == 1.0
        assert src == "faults/pier-narrower-than-the-opening.json#test.threshold"

    def test_the_floor_follows_the_fault_and_is_never_transcribed(self, tmp_path):
        rec = _fault()
        rec["test"]["threshold"] = 1.25
        assert WP.floor(_write(tmp_path, rec))[0] == 1.25

    def test_a_fault_stating_no_at_least_ratio_leaves_the_floor_unjudged(self, tmp_path):
        rec = _fault()
        rec["test"]["direction"] = "at-most"
        p = _write(tmp_path, rec)
        f, why = WP.floor(p)
        assert f is None and "states no at-least ratio" in why
        r = WP.rule("tidewater-georgian", p)
        assert r["floor"] is None and r["floor_unjudged"] == why and r["floor_source"] is None
        assert WP.floor_ft(r, 3.0) is None
        assert "no floor between two windows is stated" in WP.words(r)

    def test_the_spared_styles_are_the_licences_style_list_by_exact_id(self):
        sp = WP.spared()
        assert set(sp) == {e["style"] for e in _fault()["exceptions"] if e.get("style")} == {
            "craftsman", "prairie-school", "tudor-revival", "richardsonian-romanesque", "shingle-style"}
        assert all(v.startswith("faults/pier-narrower-than-the-opening.json#exceptions[") for v in sp.values())
        # by EXACT id, as every licence in this corpus is read: a descendant is not spared
        assert WP.rule("craftsman")["spared"] is True
        assert WP.rule("tidewater-georgian")["spared"] is False

    def test_the_aim_is_sash_lights_where_the_pack_reaches_the_style(self):
        r = WP.rule("tidewater-georgian")
        assert r["aim"]["pack"] == "sash-light" and r["aim"]["expression"] == "opening_width * 1.4"
        assert WP.floor_ft(r, 3.5) == pytest.approx(3.5)
        assert WP.aim_ft(r, 3.5) == pytest.approx(4.9)

    def test_a_style_the_pack_does_not_reach_has_no_aim_and_says_why(self):
        r = WP.rule("new-classical")
        assert r["aim"] is None and r["aim_why"]
        assert WP.aim_ft(r, 3.0) is None
        assert "no aim, because" in WP.words(r)

    def test_the_aim_never_falls_below_the_floor(self):
        r = copy.deepcopy(WP.rule("tidewater-georgian"))
        r["aim"]["expression"] = "opening_width * 0.5"
        assert WP.aim_ft(r, 3.0) == pytest.approx(3.0)

    def test_the_aim_reaches_fifty_three_of_164_nodes(self):
        """The module's own figure, measured 1 Oct 2026 and held here so its docstring cannot
        rot: sash-light's rule at `window_grouping_rule`, live (not withheld by the opt-in gate,
        not refused by a kit), on 53 of the style graph's 164 nodes."""
        g = _b("resolve_kit").load_graph()
        nodes = sorted(g["nodes"])
        assert len(nodes) == 164
        assert sum(1 for n in nodes if WP.rule(n)["aim"]) == 53


# ------------------------------------------------------------------ the seating, driven
def _room(rid, x, w, wins, d=15.0, typ="parlor"):
    return {"id": rid, "type": typ, "geometry": {"x_ft": x, "y_ft": 0.0, "width_ft": w, "depth_ft": d},
            "windows": wins}


def _seat(rooms, W, H, style="tidewater-georgian", centres=None, below=None, level=0, pier=None):
    rep = {"windows_unplaced": 0, "windows_placed": 0}
    OP._place_windows(rooms, {}, W, H, rep, None, {"breasts": [], "stacks": []}, level,
                      pier=pier if pier is not None else WP.rule(style),
                      centres=centres or {}, below=below)
    return rep


def _gaps(pos, w):
    pos = sorted(pos)
    return [round(b - a - w, 3) for a, b in zip(pos, pos[1:])]


class TestThePier:
    def test_three_windows_on_a_long_wall_stand_at_the_aim_or_wider(self):
        r = _room("a", 0.0, 30.0, [{"wall": "S", "count": 3, "width_ft": 3.0}])
        rep = _seat([r], 30.0, 15.0)
        w = r["windows"][0]
        assert "unplaced" not in w and len(w["positions_ft"]) == 3
        assert all(g >= 4.2 - 1e-6 for g in _gaps(w["positions_ft"], 3.0)), w["positions_ft"]
        (line,) = rep["window_seating"]
        assert line["mode"] == "pier" and line["seated"] == {"aim": 3}

    def test_a_short_wall_refuses_by_name_the_window_the_floor_cannot_seat(self):
        r = _room("a", 0.0, 10.0, [{"wall": "S", "count": 3, "width_ft": 3.0}])
        _seat([r], 10.0, 15.0)
        w = r["windows"][0]
        assert w["count"] == 3, "the declared count is never overwritten (WP-6.2)"
        assert w["unplaced"]["rule"] == "pier"
        assert w["unplaced"]["needs"]["pier_over_the_wider_window"] == 1.0
        assert "would leave a wall below 1 x the wider window" in w["unplaced"]["reason"]
        assert len(w["positions_ft"]) + 2 == 3

    def test_the_aim_is_taken_only_where_it_costs_no_window(self):
        """U3: the aim is read pier by pier, never face by face (taken as recommended under
        Lucas's standing instruction of 1 Oct 2026, never put). On a 22.6 ft wall four 3 ft windows
        all stand at the floor. The aim's 4.2 ft wall beside the second window seated would leave
        no room for the fourth, so that pier takes the floor and every window is seated, while the
        pier where the aim costs nothing keeps the aim. The mutation that takes the aim wherever it
        fits went green against every other test in this file."""
        r = _room("a", 0.0, 22.6, [{"wall": "S", "count": 4, "width_ft": 3.0}])
        rep = _seat([r], 22.6, 15.0)
        w = r["windows"][0]
        assert "unplaced" not in w and len(w["positions_ft"]) == 4, w
        gaps = _gaps(w["positions_ft"], 3.0)
        assert min(gaps) >= 3.0 - 1e-6 and max(gaps) >= 4.2 - 1e-6, gaps
        assert rep["window_seating"][0]["seated"] == {"aim": 2, "floor": 2}

    def test_the_floor_is_read_and_a_wider_floor_seats_fewer(self, tmp_path):
        """The placer reads `window_pier.rule`: the same wall under a floor of 2.0 seats one
        window where 1.0 seats two."""
        wins = lambda: [{"wall": "S", "count": 2, "width_ft": 3.0}]
        r1 = _room("a", 0.0, 14.0, wins())
        _seat([r1], 14.0, 15.0)
        assert len(r1["windows"][0]["positions_ft"]) == 2
        rec = _fault()
        rec["test"]["threshold"] = 2.0
        pier2 = WP.rule("tidewater-georgian", _write(tmp_path, rec))
        r2 = _room("a", 0.0, 9.5, wins())
        _seat([r2], 9.5, 15.0, pier=pier2)
        assert r2["windows"][0]["unplaced"]["rule"] == "pier"
        assert r2["windows"][0]["unplaced"]["needs"]["pier_over_the_wider_window"] == 2.0

    def test_the_wall_is_held_across_a_partition_on_one_face_line(self):
        """R5 reads the wall between two windows on one FACE, whichever rooms stand behind them:
        a window either side of a partition is held to the floor too."""
        a = _room("a", 0.0, 10.0, [{"wall": "S", "count": 1, "width_ft": 3.0}])
        b = _room("b", 10.0, 10.0, [{"wall": "S", "count": 1, "width_ft": 3.0}])
        # each alone would stand at its own room's middle, 5 and 15 ft: 7 ft apart, a wall of 4
        _seat([a, b], 20.0, 15.0)
        pa, pb = a["windows"][0]["positions_ft"][0], b["windows"][0]["positions_ft"][0]
        assert pb - pa - 3.0 >= 3.0 - 1e-6

    def test_a_licensed_style_keeps_the_old_foot(self):
        r = _room("a", 0.0, 11.5, [{"wall": "S", "count": 3, "width_ft": 3.0}])
        rep = _seat([r], 11.5, 15.0, style="craftsman")
        w = r["windows"][0]
        assert len(w["positions_ft"]) == 2 and min(_gaps(w["positions_ft"], 3.0)) == pytest.approx(
            OP.MIN_SOLID_FT, abs=1e-6)
        assert "rule" not in w["unplaced"], "a spared style's refusal is the old pass's, for want of run"
        assert rep["window_seating"][0]["mode"] == "foot"
        # and the same wall under the floor seats fewer, so the sparing is what moved it
        r2 = _room("a", 0.0, 11.5, [{"wall": "S", "count": 3, "width_ft": 3.0}])
        _seat([r2], 11.5, 15.0)
        assert len(r2["windows"][0]["positions_ft"]) < 2

    def test_a_floor_nobody_states_keeps_the_old_foot_and_says_why(self, tmp_path):
        rec = _fault()
        rec["test"]["direction"] = "at-most"
        pier = WP.rule("tidewater-georgian", _write(tmp_path, rec))
        r = _room("a", 0.0, 11.5, [{"wall": "S", "count": 3, "width_ft": 3.0}])
        rep = _seat([r], 11.5, 15.0, pier=pier)
        assert rep["window_seating"][0]["mode"] == "foot"
        assert len(r["windows"][0]["positions_ft"]) == 2


class TestTheWiderWindowSetsThePier:
    """R5: "a floor of 1.0 x the WIDER window". Every placer fixture above seats 3 ft windows, so a
    pier held to the NARROWER of two windows passed this file whole (WP-16.8, the audit of Phase 16,
    auditor E: mutation E35, `max` -> `min` in `_seat_line`, 103 passed)."""

    def test_a_narrow_and_a_wide_window_keep_the_wider_ones_pier(self):
        """A 3 ft window in an 8 ft room beside a 5 ft window in a 6 ft room on one face line. The
        5 ft window needs 5 ft of wall to the 3 ft one, and its room cannot give it that: refused
        by name. Held to the narrower window's 3 ft it would stand, at 11.0 ft."""
        a = _room("a", 0.0, 8.0, [{"wall": "S", "count": 1, "width_ft": 3.0}])
        b = _room("b", 8.0, 6.0, [{"wall": "S", "count": 1, "width_ft": 5.0}])
        _seat([a, b], 14.0, 15.0)
        assert a["windows"][0]["positions_ft"] == [pytest.approx(4.0)]
        u = b["windows"][0]["unplaced"]
        assert u["rule"] == "pier" and "positions_ft" not in b["windows"][0]
        assert u["needs"]["pier_over_the_wider_window"] == 1.0
        # the premise: the 6 ft room can hold the 5 ft window 3 ft (the narrower's floor) from the
        # other and cannot hold it 5 ft (the wider's) from it
        assert 8.0 + 2.5 <= 4.0 + 1.5 + 3.0 + 2.5 <= 14.0 - 2.5
        assert 4.0 + 1.5 + 5.0 + 2.5 > 14.0 - 2.5


class TestTheCentreHolds:
    @staticmethod
    def _pair(centre_ft):
        a = _room("a", 0.0, 8.0, [{"wall": "S", "count": 1, "width_ft": 3.0}])
        b = _room("b", 8.0, 4.0, [{"wall": "S", "count": 1, "width_ft": 3.0}])
        rep = _seat([a, b], 12.0, 15.0, centres={("S", 0.0): (centre_ft, "a test door")})
        return a["windows"][0]["positions_ft"][0], b["windows"][0]["positions_ft"][0], rep

    def test_the_window_nearer_the_entrance_keeps_its_place_and_the_other_moves(self):
        """R5a, driven both ways on one wall. Two rooms' windows, each at its old place (4 and 10
        ft), stand 3 ft apart: at the floor, short of the 4.2 ft aim. With the entrance at the
        east end the east window keeps its place and the west one moves out to take the aim; with
        it at the west end the west window keeps its place, and the east one, which cannot move
        far enough for the aim, stands at the floor."""
        a, b, rep = self._pair(12.0)
        assert rep["window_seating"][0]["centre"] == "a test door"
        assert b == pytest.approx(10.0) and a == pytest.approx(10.0 - 3.0 - 4.2, abs=0.002)
        a, b, rep = self._pair(0.0)
        assert a == pytest.approx(4.0) and b == pytest.approx(4.0 + 3.0 + 3.0, abs=0.002)
        assert rep["window_seating"][0]["seated"] == {"aim": 1, "floor": 1}

    def test_a_garage_door_gives_the_face_its_centre(self):
        """U4 (taken as recommended under Lucas's standing instruction of 1 Oct 2026, never put):
        where the widest door on the entrance front is a garage door, no doorcase frames it and it
        is no entrance, so the face's centre holds. DRIVEN, because the shipped corpus cannot tell
        the two apart: six of the sixteen shipped plans put a garage door widest on their entrance
        front (measured 1 Oct 2026), and removing this branch moved no window on any of them, so
        the corpus openings digest stayed green."""
        def level(door_type):
            r = _room("g", 0.0, 20.0, [], typ="garage")
            r["doors"] = [{"to": "exterior", "wall": "S", "position_ft": 6.0, "width_ft": 16.0,
                           "type": door_type}]
            return [r]
        plan = {"context": {"entrance_faces": "S"}}
        got, why = OP.window_centres(plan, level("garage"), 40.0, 15.0, None)
        assert got == {} and "a garage door is no entrance" in why
        got, why = OP.window_centres(plan, level(None), 40.0, 15.0, None)
        assert got == {("S", 0.0): (6.0, "the entrance door's axis (g)")} and why is None

    def test_the_outer_window_yields_and_the_inner_keeps_its_place(self):
        """A 10 ft room holding three 3 ft windows: the middle one is nearest the face's centre and
        keeps its place, and both outer ones are refused by name. The floor alone would seat two
        -- at 1.5 and 8.5 -- if the middle one moved; R5a keeps it, and this is the cost of that,
        stated (`oq/the-centre-holds-and-refuses-a-window-the-floor-would-seat`)."""
        r = _room("a", 0.0, 10.0, [{"wall": "S", "count": 3, "width_ft": 3.0}])
        _seat([r], 10.0, 15.0)
        w = r["windows"][0]
        assert w["positions_ft"] == [pytest.approx(5.0)]
        assert w["unplaced"]["rule"] == "pier" and w["unplaced"]["have"]["units_placed"] == 1


class TestTheUpperFollowsTheGround:
    LINE = ("S", 0.0)

    def test_an_upper_window_stands_exactly_on_the_axis_below(self):
        up = _room("u", 0.0, 12.0, [{"wall": "S", "count": 1, "width_ft": 3.0}])
        rep = _seat([up], 30.0, 15.0, below={self.LINE: [(4.25, "window", "g")]}, level=1)
        assert up["windows"][0]["positions_ft"] == [4.25]
        assert rep["window_seating"][0]["seated"] == {"aligned": 1}

    def test_a_door_below_is_an_opening_to_align_to(self):
        up = _room("u", 0.0, 12.0, [{"wall": "S", "count": 1, "width_ft": 3.0}])
        _seat([up], 30.0, 15.0, below={self.LINE: [(7.0, "door", "g")]}, level=1)
        assert up["windows"][0]["positions_ft"] == [7.0]

    def test_an_axis_the_room_cannot_take_is_refused_by_name(self):
        up = _room("u", 0.0, 12.0, [{"wall": "S", "count": 1, "width_ft": 3.0}])
        _seat([up], 30.0, 15.0, below={self.LINE: [(0.5, "window", "g")]}, level=1)
        u = up["windows"][0]["unplaced"]
        assert u["rule"] == "alignment" and "positions_ft" not in up["windows"][0]
        assert u["axes"] == [{"axis_ft": 0.5, "opening": "window",
                              "why": "it would run past the end of its own room's wall"}]

    def test_nothing_below_the_rooms_run_leaves_the_window_where_the_pier_rule_puts_it(self):
        """R6a: the opening below stands under ANOTHER room's run, so this one is not aligned and
        not refused; the alignment fault judges it."""
        up = _room("u", 0.0, 12.0, [{"wall": "S", "count": 1, "width_ft": 3.0}])
        rep = _seat([up], 30.0, 15.0, below={self.LINE: [(20.0, "window", "g")]}, level=1)
        assert up["windows"][0]["positions_ft"] == [6.0] and "unplaced" not in up["windows"][0]
        assert "aligned" not in rep["window_seating"][0]["seated"]

    def test_r5_with_r6_refuses_the_aligned_window_the_floor_cannot_take(self):
        """Read together: two axes below 2 ft apart, two 3 ft windows above. Both cannot stand on
        them a window's width apart, so one is refused by name for its alignment, saying why."""
        up = _room("u", 0.0, 12.0, [{"wall": "S", "count": 2, "width_ft": 3.0}])
        _seat([up], 30.0, 15.0, below={self.LINE: [(5.0, "window", "g"), (7.0, "window", "g")]},
              level=1)
        w = up["windows"][0]
        assert len(w["positions_ft"]) == 1 and w["positions_ft"][0] in (5.0, 7.0)
        assert w["unplaced"]["rule"] == "alignment"
        assert w["unplaced"]["axes"][0]["why"] == (
            "the wall to the window beside it would fall below 1 x the wider window")

    def test_the_inner_window_holds_against_an_outer_aligned_one(self):
        """R5a and "R5 with R6, read together" (WP-16.8, the audit of Phase 16, auditor A). A 13.5 ft
        upper room holds two 3 ft windows preferring 4.5 and 9.0 ft, and the face's centre is at
        25.0 ft; the window below stands at 6.745 ft, so the unit preferring 4.5 is paired with
        that axis. The two cannot both stand a window's width apart. R5a: "on other faces those
        nearer the face's centre keep their places; the outer window moves along its own wall, or
        is refused by name" -- so the unit at 9.0, nearer the centre, holds, and the aligned outer
        one is refused for its alignment, which is the ruled refusal of R5 with R6.

        This is spec-builder-colonial's primary chamber on its upper south face, measured. Until
        WP-16.8 every aligned unit was seated before any other, an order no ruling states, so the
        aligned outer window held and the INNER one was refused for the pier."""
        up = _room("u", 0.0, 13.5, [{"wall": "S", "count": 2, "width_ft": 3.0}])
        rep = _seat([up], 50.0, 15.0, below={self.LINE: [(6.745, "window", "g")]}, level=1)
        w = up["windows"][0]
        assert w["positions_ft"] == [pytest.approx(9.0)]
        assert w["unplaced"]["rule"] == "alignment"
        assert w["unplaced"]["axes"][0]["why"] == (
            "the wall to the window beside it would fall below 1 x the wider window")
        assert rep["window_seating"][0]["refused"] == {"alignment": 1}

    def test_an_inner_window_seated_first_still_leaves_an_outer_axis_it_can_share(self):
        """The other half of one queue: the inner window takes its place first, and the outer
        aligned window still stands on its axis wherever the floor allows beside it -- Tidewater's
        third chamber, measured, where the inner window holds 33.0 ft and the outer one stands on
        the door axis at 40.5 ft, 4.0 ft of wall between them against a 3.5 ft floor."""
        up = _room("c3", 27.0, 18.0, [{"wall": "S", "count": 2, "width_ft": 3.5}])
        _seat([up], 63.0, 15.0, centres={self.LINE: (18.0, "the entrance door's axis (passage)")},
              below={self.LINE: [(40.5, "door", "g")]}, level=1)
        assert up["windows"][0]["positions_ft"] == [pytest.approx(33.0), pytest.approx(40.5)]
        assert "unplaced" not in up["windows"][0]

    def test_a_unit_takes_an_axis_its_room_can_take_before_one_it_cannot(self):
        """U2 (taken as recommended under Lucas's standing instruction of 1 Oct 2026, never put):
        the pairing seats every unit it can on an axis its room CAN take before it gives one an
        axis it cannot. Three axes below a 20 ft room's run, the last at 18.6 ft, where a 3 ft
        window would run past the room's end. By distance alone the nearest pairing takes 7.6 and
        18.6, and refuses the second window; the room can take 1.5 and 7.6, so both stand.

        RE-CUT 1 OCT 2026 (WP-16.6's mutation pass): the first fixture put ONE window between an
        axis it could take and one at its end wall, and a single window sits at its room's centre,
        so the axis it can take is always at least as near as the one it cannot. The mutation
        that removes the cost of an untakeable axis left it green. This fixture needs two windows."""
        up = _room("u", 0.0, 20.0, [{"wall": "S", "count": 2, "width_ft": 3.0}])
        rep = _seat([up], 40.0, 15.0, below={self.LINE: [(1.5, "window", "g"), (7.6, "window", "g"),
                                                         (18.6, "window", "g")]}, level=1)
        assert up["windows"][0]["positions_ft"] == [1.5, 7.6] and "unplaced" not in up["windows"][0]
        assert rep["window_seating"][0]["seated"] == {"aligned": 2}


class TestTheOrderPreservingPairing:
    def test_it_pairs_in_order_at_the_least_cost(self):
        cost = lambda i, j: abs([1.0, 5.0][i] - [0.9, 3.0, 5.2][j])
        assert OP._order_assign(2, 3, cost) == [(0, 0), (1, 2)]

    def test_more_units_than_axes_pairs_as_many_as_there_are_axes(self):
        cost = lambda i, j: abs([1.0, 2.0, 9.0][i] - [8.8][j])
        assert OP._order_assign(3, 1, cost) == [(2, 0)]

    def test_a_tie_goes_to_the_lower_index(self):
        assert OP._order_assign(1, 2, lambda i, j: 1.0) == [(0, 0)]

    def test_nothing_to_pair_is_an_empty_pairing(self):
        assert OP._order_assign(0, 3, lambda i, j: 0.0) == []
        assert OP._order_assign(2, 0, lambda i, j: 0.0) == []


# ------------------------------------------------------------------ the words and the measurement
class TestTheWordsAndTheMeasurement:
    def test_the_sheet_and_the_record_group_a_ruled_refusal_by_its_rule(self):
        D = _b("disclosures")
        assert D._group("any words at all", "pier", 1.0) == "too near the next window for a wall of 1 × the wider"
        assert D._group("any words at all", "pier", None) == "too near the next window for the pier floor"
        assert D._group("any words", "alignment") == "unable to stand on the axis of the opening below"

    def test_a_window_refused_for_two_causes_counts_each_part_under_its_own_rule(self):
        """DRIVEN: no shipped window is refused for two causes at once, so the plate's `parts`
        branch was reached by nothing, and dropping it went green (WP-16.6's mutation pass). A
        window of three units, one seated, one refused for the floor and one for the axis below,
        counts one under each rule's bucket, and the buckets sum to the headline."""
        D = _b("disclosures")
        u = {"reason": "two causes", "needs": {"pier_over_the_wider_window": 1.0},
             "have": {"units_placed": 1},
             "parts": [{"rule": "pier", "units": 1,
                        "reason": "1 of 3 unit(s) would leave a wall below 1 x the wider window"},
                       {"rule": "alignment", "units": 1,
                        "reason": "1 of 3 unit(s) could not stand on the axis of the opening below"}]}
        plan = {"opening_report": {"windows_unplaced": 2},
                "levels": [{"index": 0, "rooms": [{"id": "a", "windows": [
                    {"wall": "S", "count": 3, "positions_ft": [5.0], "unplaced": u}]}]}]}
        got = D.windows_not_drawn(plan)
        assert got["detail"] == {"too near the next window for a wall of 1 × the wider": 1,
                                 "unable to stand on the axis of the opening below": 1}
        assert got["text"].startswith("2 OF 3 DECLARED WINDOW UNIT(S) NOT DRAWN"), got["text"]

    def test_the_elevation_has_words_for_both_ruled_causes(self):
        words = dict(EL.REFUSAL_WORDS)
        assert "pier" in EL.REFUSAL_CAUSES and "alignment" in EL.REFUSAL_CAUSES
        assert words["pier"].endswith("THE PIER FLOOR") and "1 × THE WIDER WINDOW" in words["pier"]
        assert "AXIS OF THE OPENING BELOW" in words["alignment"]

    def test_a_window_pier_is_measured_glass_to_glass_and_a_door_breaks_the_pair(self):
        def rect(i, x0, w, kind="window", glass=True):
            r = {"id": i, "storey": "ground", "kind": kind, "x0_in": x0, "x1_in": x0 + w, "width_in": w}
            if glass:
                r["sash"] = {"members": [{"kind": "stile", "side": "L", "x1": x0 + 2.0},
                                         {"kind": "stile", "side": "R", "x0": x0 + w - 2.0}]}
            return r
        piers = EL.window_piers([rect("a", 0.0, 36.0), rect("b", 72.0, 36.0)])
        assert len(piers) == 1
        p = piers[0]
        assert p["opening_pier_in"] == 36.0 and p["glass_pier_in"] == 40.0 and p["wider_glass_in"] == 32.0
        assert p["ratio"] == pytest.approx(1.25)
        assert EL.window_piers([rect("a", 0.0, 36.0), rect("d", 50.0, 36.0, kind="door", glass=False),
                                rect("b", 100.0, 36.0)]) == []

    def test_a_pier_beside_a_window_with_no_glass_is_unjudged_and_never_a_number(self):
        def rect(i, x0, w, glass):
            r = {"id": i, "storey": "ground", "kind": "window", "x0_in": x0, "x1_in": x0 + w, "width_in": w}
            r["sash"] = ({"members": [{"kind": "stile", "side": "L", "x1": x0 + 2.0},
                                      {"kind": "stile", "side": "R", "x0": x0 + w - 2.0}]}
                         if glass else {"refused": "driven"})
            return r
        (p,) = EL.window_piers([rect("a", 0.0, 36.0, True), rect("b", 72.0, 36.0, False)])
        assert p["ratio"] is None and "draws no glass" in p["unjudged"]


    def test_a_pier_that_draws_no_glass_withholds_the_narrowest_and_says_why(self, monkeypatch):
        """DRIVEN, because every pier the shipped plans draw has glass both sides (24 of 24), so
        the withholding was reached by nothing: publishing the narrowest of the judged pairs
        anyway went green against every test (WP-16.6's mutation pass). One front pier is made to
        draw no glass on the Tidewater house: the count is published, the narrowest is withheld
        with its reason, and the upper storey's count still reaches the faults. Before this test
        the same front raised a KeyError, because the withheld dict's upper-storey line read a key
        only the two upper-storey branches write.

        ON A FRONT DRAWN WHOLE SINCE WP-16.8 (the audit of Phase 16, auditor B): the Tidewater
        front is incomplete, and the two pier figures are withheld there whole now (U8, the next
        test), so the drive declares the front complete to reach the glass branch alone."""
        real = EL.window_piers
        GEO, ST, RF = _b("geometry"), _b("structure"), _b("roof")
        # The front is patched before the house is solved, so the solve keeps to a private cache
        # and nothing computed under the patch outlives it (tests/test_determinism.py).
        monkeypatch.setattr(GEO, "_SOLVE_CACHE", {})
        AX = _b("axis")
        monkeypatch.setattr(AX, "front_complete",
                            lambda rec: {"front": "S", "undrawn": {}, "total_undrawn": 0,
                                         "complete": True, "why": None})

        def one_unjudged(rects):
            got = real(rects)
            if got:
                got[0] = dict(got[0], ratio=None, unjudged="driven: a window of the pair draws no glass")
            return got
        with open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"), encoding="utf-8") as fh:
            plan = json.load(fh)
        placed = GEO.solve(copy.deepcopy(plan), engine="heuristic")
        sec = ST.build_section(placed, None, geometry_result=placed)
        rf = RF.build_roof(placed, None, section=sec)
        monkeypatch.setattr(EL, "window_piers", one_unjudged)
        ev = EL.build_elevation(placed, None, section=sec, roof=rf)
        m = ev["measurements"]
        assert ev["front"]["piers"] and ev["front"]["piers"][0]["ratio"] is None, "the drive landed"
        assert m["count_of_window_piers_on_the_front"] == len(ev["front"]["piers"])
        assert "narrowest_pier_over_wider_adjacent_window" not in m
        assert "draw no glass" in ev["front"]["withheld"]["narrowest_pier_over_wider_adjacent_window"]
        assert m.get("upper_floor_opening_count") and "total_upper_storey_openings" not in ev["front"]["withheld"]

    def test_an_incomplete_front_withholds_both_pier_figures_with_its_reason(self):
        """U8 (WP-16.8, the audit of Phase 16, auditor B; taken as recommended under Lucas's
        standing instruction of 1 Oct 2026, never put): R12's reading of an incomplete front,
        carried to the pier fault. The drawn piers of a front the placer cut down are the ones its
        refusals left -- good-02 cleared at 1.26 with two of its living room's three windows
        refused FOR the floor this fault holds -- so neither the count nor the narrowest is
        handed to the fault, and the row says the front's own reason."""
        GEO, ST, RF = _b("geometry"), _b("structure"), _b("roof")
        with open(os.path.join(ROOT, "plans", "reference", "good-02-portico-library-house.json"),
                  encoding="utf-8") as fh:
            plan = json.load(fh)
        placed = GEO.solve(copy.deepcopy(plan), engine="heuristic")
        sec = ST.build_section(placed, None, geometry_result=placed)
        rf = RF.build_roof(placed, None, section=sec)
        ev = EL.build_elevation(placed, None, section=sec, roof=rf)
        fc = ev["front"]["complete"]
        assert fc["complete"] is False and ev["front"]["piers"], "the premise: an incomplete front with piers"
        m, wh = ev["measurements"], ev["front"]["withheld"]
        for k in ("count_of_window_piers_on_the_front", "narrowest_pier_over_wider_adjacent_window"):
            assert k not in m, k
            assert wh[k] == fc["why"], k
        r = _b("plan_check").check(placed)
        row = next(x for x in r["fault_unjudged"] if x["fault"] == "pier-narrower-than-the-opening")
        assert {w["name"] for w in row.get("withheld") or []} >= {"count_of_window_piers_on_the_front"}


# ------------------------------------------------------------------ the composer's cap
class TestTheComposerCountsToTheFloor:
    """`compose.derive_openings` bounds how many windows a wall carries. It read sash-light's
    1.4 x as a transcribed literal -- the placer's AIM, not the floor below which it refuses a
    window -- and reads `window_pier.floor` now, the placer's own reading."""

    @staticmethod
    def _count(monkeypatch, floor):
        CO = _b("compose")
        monkeypatch.setattr(WP, "floor", lambda path=None: (floor, "driven") if floor is not None
                            else (None, "driven: no floor"))
        plan = {"id": "t", "style": "tidewater-georgian", "levels": [{
            "index": 0, "floor_to_ceiling_ft": 10,
            "rooms": [{"id": "s", "type": "sunroom", "width_ft": 12, "length_ft": 14,
                       "windows": [{"wall": "S", "count": 1}], "doors": []}]}]}
        log = []
        CO.derive_openings(plan, "tidewater-georgian", log, doors=False)
        return plan["levels"][0]["rooms"][0]["windows"][0]["count"], log

    def test_a_wider_floor_carries_fewer_windows(self, monkeypatch):
        n1, log = self._count(monkeypatch, 1.0)
        n3, _ = self._count(monkeypatch, 3.0)
        assert n1 > n3 >= 1, (n1, n3)
        assert any("at least 1 x the wider (driven)" in l for l in log), log

    def test_a_floor_nobody_states_bounds_the_count_by_the_wall_and_says_so(self, monkeypatch):
        n0, log = self._count(monkeypatch, None)
        n1, _ = self._count(monkeypatch, 1.0)
        assert n0 > n1, (n0, n1)
        assert any("bounded by the wall alone: driven: no floor" in l for l in log), log
        assert any("bounded by the wall's length alone" in l for l in log), log


def test_the_cap_counts_n_windows_and_n_minus_one_piers():
    """n windows of width w need n w + (n - 1) p of wall, not n (w + p): on the 12 x 14 room's
    14 ft E wall, 2.67 ft windows at the 1.0 x floor fit three (8.0 + 2 x 2.67 = 13.3 ft), and
    counting a pier per window would cap it at two. (WP-16.8, auditor E's E46: the tests above
    compare orderings on the 12 ft wall, where both forms give two.)"""
    CO = _b("compose")
    plan = {"id": "t", "style": "tidewater-georgian", "levels": [{
        "index": 0, "floor_to_ceiling_ft": 10,
        "rooms": [{"id": "s", "type": "sunroom", "width_ft": 12, "length_ft": 14,
                   "windows": [{"wall": "E", "count": 1}], "doors": []}]}]}
    CO.derive_openings(plan, "tidewater-georgian", [], doors=False)
    w = plan["levels"][0]["rooms"][0]["windows"][0]
    f = WP.floor()[0]
    n = w["count"]
    assert n * w["width_ft"] + (n - 1) * f * w["width_ft"] <= 14 + 0.05, w
    assert n == 3, w


# ------------------------------------------------------------------ the Georgian band, in line
def test_the_georgian_kits_pier_band_is_held_to_the_floor():
    """R5: "the Georgian 0.6-1.0 band is brought into line". It reads from the ruled floor up, is
    still editorial (no record this style cites states its own figure), and says when it moved."""
    with open(os.path.join(ROOT, "kits", "georgian-colonial-american.kit.json"), encoding="utf-8") as fh:
        p = json.load(fh)["slots"]["window_grouping_rule"]["parameters"]["pier_measured_ratio"]
    assert p["range"][0] == WP.floor()[0], p["range"]
    assert p["range"][1] >= p["range"][0]
    assert p["kind"] == "editorial" and p["note"].startswith("BROUGHT INTO LINE 1 Oct 2026 (WP-16.6)")
