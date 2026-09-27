"""Where two massing elements abut, the wall between them is ONE wall (WP-14.4).

`render_plan.wall_bands` drew each element's envelope outward from its own rooms. At a hyphen --
an element that ABUTS the two it joins (WP-11.9, ruling 3) -- that put the main block's west wall
over the hyphen's floor, the hyphen's east wall over the main block's, and `wall_lines` drew a
third body centred between them: on `tidewater-georgian-careful`, the one shipped plan with a
dependency, 21 pairs of wall bodies drawn over one another. The join is drawn once now, centred on
the shared line at the envelope's thickness -- the court wall's convention -- and an S or N run
stops at the wall it meets instead of running through it.

Every assertion below is DRIVEN with hand-built blocks as well as read off the shipped plan,
because the corpus holds one multi-element plan and it has only one kind of join (a hyphen whose
neighbours both run past it). The flush join and the detached element are cases no shipped record
reaches.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache as mc  # noqa: E402

RP = mc.load("render_plan", os.path.join(ROOT, "build", "render_plan.py"))
G = mc.load("geometry", os.path.join(ROOT, "build", "geometry.py"))

WALL = {"exterior_in": 12.0, "bearing_interior_in": 8.0, "partition_in": 4.0}
EXT = 1.0


def _room(rid, x, y, w, h, typ="parlor"):
    return {"id": rid, "type": typ, "geometry": {"x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": h}}


def _bands(rooms, blocks, gaps=()):
    bands, _stray = RP.wall_bands(rooms, blocks, 40.0, 30.0, 10.0, WALL, list(gaps))
    return bands


def _overlaps(bands):
    bad = []
    for i, a in enumerate(bands):
        for b in bands[i + 1:]:
            ox = min(a["x_ft"] + a["width_ft"], b["x_ft"] + b["width_ft"]) - max(a["x_ft"], b["x_ft"])
            oy = min(a["y_ft"] + a["depth_ft"], b["y_ft"] + b["depth_ft"]) - max(a["y_ft"], b["y_ft"])
            if ox > 0.01 and oy > 0.01:
                bad.append((a["wall"], b["wall"], round(ox, 2), round(oy, 2)))
    return bad


class TestWhereElementsJoin:
    def test_a_hyphen_joins_both_elements_it_links_over_its_own_depth(self):
        blocks = [(0.0, 0.0, 40.0, 30.0), (-10.0, 10.0, 10.0, 10.0), (-30.0, 5.0, 20.0, 20.0)]
        got = sorted((a, p, lo, hi) for a, p, lo, hi, _i, _j in RP.element_joins(blocks))
        assert got == [("x", -10.0, 10.0, 20.0), ("x", 0.0, 10.0, 20.0)], got

    def test_a_detached_element_and_a_corner_touch_are_not_joins(self):
        # a gap between the two faces, and two elements that share only a point
        assert RP.element_joins([(0.0, 0.0, 20.0, 20.0), (-12.0, 0.0, 10.0, 20.0)]) == []
        assert RP.element_joins([(0.0, 0.0, 20.0, 20.0), (-10.0, -10.0, 10.0, 10.0)]) == []

    def test_a_one_rectangle_house_has_no_join_and_its_four_bands_are_unchanged(self):
        # the premise the fifteen one-rectangle sheets rest on: the S and N runs take the corners
        bands = [b for b in _bands([_room("a", 0, 0, 40, 30)], [(0.0, 0.0, 40.0, 30.0)])
                 if b["wall"] == "exterior"]
        s = [b for b in bands if abs(b["y_ft"] + EXT) < 1e-9]
        w = [b for b in bands if abs(b["x_ft"] + EXT) < 1e-9 and b["depth_ft"] > b["width_ft"]]
        assert len(bands) == 4 and len(s) == 1 and len(w) == 1
        assert (s[0]["x_ft"], s[0]["width_ft"]) == (-EXT, 40.0 + 2 * EXT)
        assert (w[0]["y_ft"], w[0]["depth_ft"]) == (0.0, 30.0)


class TestTheJoinIsOneWall:
    BLOCKS = [(0.0, 0.0, 40.0, 30.0), (-10.0, 10.0, 10.0, 10.0), (-30.0, 5.0, 20.0, 20.0)]
    ROOMS = [_room("a", 0, 0, 20, 30), _room("b", 20, 0, 20, 30),
             _room("h", -10, 10, 10, 10, "back-hall"), _room("k", -30, 5, 20, 20, "kitchen")]

    def test_no_wall_body_is_drawn_over_another(self):
        assert _overlaps(_bands(self.ROOMS, self.BLOCKS)) == []

    def test_each_join_is_one_body_centred_on_its_line_at_the_envelopes_thickness(self):
        joins = [b for b in _bands(self.ROOMS, self.BLOCKS) if b["wall"] == "join"]
        assert len(joins) == 2
        for b in joins:
            assert b["t_ft"] == EXT and b["width_ft"] == EXT
            assert b["x_ft"] + EXT / 2 in (0.0, -10.0)          # centred on the shared line
            assert (b["y_ft"], b["depth_ft"]) == (10.0, 10.0)   # over the shared span, no further

    def test_the_hyphens_south_wall_stops_at_the_walls_it_meets(self):
        south = [b for b in _bands(self.ROOMS, self.BLOCKS)
                 if b["wall"] == "exterior" and abs(b["y_ft"] - (10.0 - EXT)) < 1e-9]
        assert len(south) == 1, south
        # both neighbours' faces run on past the hyphen's corners, so their own walls stand
        # there: the hyphen's south wall runs between them, a thickness short at each end
        assert (south[0]["x_ft"], south[0]["x_ft"] + south[0]["width_ft"]) == (-10.0 + EXT, 0.0 - EXT)

    def test_a_segment_of_a_room_wall_on_a_join_is_not_drawn_again(self):
        bands = _bands(self.ROOMS, self.BLOCKS)
        on_join = [b for b in bands if b["wall"] in ("bearing", "partition") and b["width_ft"] < b["depth_ft"]
                   and abs(b["x_ft"] + b["width_ft"] / 2) < 1e-6 and 10.0 < b["y_ft"] + b["depth_ft"] / 2 < 20.0]
        assert on_join == [], on_join

    def test_a_flush_join_meets_without_overlap_or_a_gap(self):
        """Two elements of one depth side by side: the south faces are one line and the south
        runs meet at the join exactly -- no corner extension into the neighbour and no gap."""
        blocks = [(0.0, 0.0, 20.0, 20.0), (-10.0, 0.0, 10.0, 20.0)]
        rooms = [_room("a", 0, 0, 20, 20), _room("k", -10, 0, 10, 20, "kitchen")]
        bands = _bands(rooms, blocks)
        assert _overlaps(bands) == []
        south = sorted((b["x_ft"], b["x_ft"] + b["width_ft"]) for b in bands
                       if b["wall"] == "exterior" and abs(b["y_ft"] + EXT) < 1e-9)
        assert south == [(-10.0 - EXT, 0.0), (0.0, 20.0 + EXT)], south

    def test_a_wing_off_the_middle_of_a_face_meets_its_walls(self):
        """A rear ell standing on the middle of the main block's north face: the north wall is
        broken where the ell joins it, and each piece stops a thickness short of the ell's own
        side wall, which runs outward from that point. No shipped record has a wing off the middle
        of a face; this is the fixture that makes the rule a rule rather than a comment."""
        blocks = [(0.0, 0.0, 40.0, 30.0), (10.0, 30.0, 20.0, 10.0)]
        rooms = [_room("a", 0, 0, 40, 30), _room("e", 10, 30, 20, 10, "kitchen")]
        bands = _bands(rooms, blocks)
        assert _overlaps(bands) == []
        north = sorted((b["x_ft"], b["x_ft"] + b["width_ft"]) for b in bands
                       if b["wall"] == "exterior" and abs(b["y_ft"] - 30.0) < 1e-9 and b["depth_ft"] == EXT)
        assert north == [(-EXT, 10.0 - EXT), (30.0 + EXT, 40.0 + EXT)], north

    def test_an_opening_on_a_join_is_cut_from_it(self):
        bands = _bands(self.ROOMS, self.BLOCKS, gaps=[("x", 0.0, 14.0, 17.0)])
        runs = sorted((b["y_ft"], b["y_ft"] + b["depth_ft"]) for b in bands
                      if b["wall"] == "join" and abs(b["x_ft"] + EXT / 2) < 1e-9)
        assert runs == [(10.0, 14.0), (17.0, 20.0)], runs


@pytest.fixture(scope="module")
def placed():
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    G._SOLVE_CACHE.clear()
    return G.solve(copy.deepcopy(plan), engine="heuristic")


class TestTheShippedPlan:
    def _level_bands(self, placed):
        ST = mc.load("structure", os.path.join(ROOT, "build", "structure.py"))
        EL = mc.load("elements", os.path.join(ROOT, "build", "elements.py"))
        fp = placed["footprint"]
        W, H = fp["width_ft"], fp["depth_ft"]
        lv = placed["levels"][0]
        blocks = [EL.bounds_of(e) for e in EL.elements_on_level(placed, lv["rooms"])]
        op = RP.openings_of_level(placed, lv, 0)
        bands, stray = RP.wall_bands(lv["rooms"], blocks, W, H, fp.get("bay_module_ft"),
                                     ST.wall_thickness(placed), RP.opening_gaps(op, W, H))
        return blocks, op, bands, stray

    def test_the_premise_the_plan_has_two_joins(self, placed):
        blocks, _op, _bands, _stray = self._level_bands(placed)
        assert len(blocks) == 3 and len(RP.element_joins(blocks)) == 2

    def test_no_wall_body_is_drawn_over_another(self, placed):
        _blocks, _op, bands, _stray = self._level_bands(placed)
        assert _overlaps(bands) == []

    def test_every_exterior_opening_is_cut_from_its_own_elements_face(self, placed):
        """The holes, not the frames: the frames have stood at `edge_ft` since WP-11.14, and the
        holes were cut at the footprint's face -- the dependency's windows stood on uncut wall."""
        _blocks, op, bands, stray = self._level_bands(placed)
        assert not stray, stray
        off_the_footprint = 0
        for d in op["exterior"] + op["windows"]:
            e, at = d["edge_ft"], d["at_ft"]
            if d["wall"] in "SN" and e not in (0.0, placed["footprint"]["depth_ft"]):
                off_the_footprint += 1
            if d["wall"] in "WE" and e not in (0.0, placed["footprint"]["width_ft"]):
                off_the_footprint += 1
            for b in bands:
                if b["wall"] != "exterior":
                    continue
                if d["wall"] in "SN":
                    mid_y = e - b["t_ft"] / 2 if d["wall"] == "S" else e + b["t_ft"] / 2
                    assert not (b["x_ft"] < at < b["x_ft"] + b["width_ft"]
                                and b["y_ft"] < mid_y < b["y_ft"] + b["depth_ft"]), (d["room"], d["wall"], at)
                else:
                    mid_x = e - b["t_ft"] / 2 if d["wall"] == "W" else e + b["t_ft"] / 2
                    assert not (b["y_ft"] < at < b["y_ft"] + b["depth_ft"]
                                and b["x_ft"] < mid_x < b["x_ft"] + b["width_ft"]), (d["room"], d["wall"], at)
        assert off_the_footprint >= 5, (
            "the premise: this plan places openings on faces that are not the footprint's -- the "
            "dependency's and the hyphen's -- or this test cannot tell the two faces apart")
