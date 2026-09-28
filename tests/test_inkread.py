"""The instrument's own tests (WP-14.1). An instrument that cannot fail is worse than a test
that cannot fail, because its output is a number rather than a green tick -- so every reading
`tests/inkread.py` makes is held here to a value worked out by hand, and each of the traps a
reader of SVG falls into is driven on purpose.
"""
import json
import math

import pytest

import inkread as IR


# ---------------------------------------------------------------- the path grammar
class TestThePathGrammar:
    def test_relative_commands_become_absolute(self):
        got = IR.parse_path("m 10 20 l 5 0 l 0 5 z")
        assert got == [("M", 10.0, 20.0), ("L", 15.0, 20.0), ("L", 15.0, 25.0), ("Z",)]

    def test_the_implicit_lineto_after_a_moveto(self):
        # "M 0 0 10 0 10 10" is a move and two LINES, and the relative form stays relative.
        assert IR.parse_path("M 0 0 10 0 10 10") == [("M", 0.0, 0.0), ("L", 10.0, 0.0), ("L", 10.0, 10.0)]
        assert IR.parse_path("m 1 1 2 0 0 2") == [("M", 1.0, 1.0), ("L", 3.0, 1.0), ("L", 3.0, 3.0)]

    def test_compact_numbers_split_where_svg_says_they_split(self):
        # `1.5.5` is two numbers and `-1-2` is two numbers: SVG's grammar, not a typo.
        assert IR.parse_path("M1.5.5L-1-2") == [("M", 1.5, 0.5), ("L", -1.0, -2.0)]

    def test_arc_flags_need_no_separator(self):
        got = IR.parse_path("M0 0A10 10 0 015 5")
        assert got[1] == ("A", 10.0, 10.0, 0.0, 0, 1, 5.0, 5.0)

    def test_a_relative_arc_ends_relative_to_the_pen_and_keeps_its_radii(self):
        """WP-14.6, auditor C. Only the absolute `A` was driven, so a reader that forgot to add
        the pen to a relative `a`'s END -- or added it to the radii too -- stayed green. The
        radii, the rotation and both flags are not coordinates and must pass through unmoved."""
        got = IR.parse_path("M 10 20 a 5 7 30 1 0 10 -4")
        assert got[1] == ("A", 5.0, 7.0, 30.0, 1, 0, 20.0, 16.0)
        # and a second relative arc is relative to the FIRST's end, not to the subpath's start
        got = IR.parse_path("m 10 20 a 5 5 0 0 1 10 0 a 5 5 0 0 1 10 0")
        assert got[1][-2:] == (20.0, 20.0) and got[2][-2:] == (30.0, 20.0)

    def test_horizontal_and_vertical_carry_the_other_coordinate(self):
        assert IR.parse_path("M 2 3 H 9 V 7 h -1 v -1") == [
            ("M", 2.0, 3.0), ("L", 9.0, 3.0), ("L", 9.0, 7.0), ("L", 8.0, 7.0), ("L", 8.0, 6.0)]

    def test_smooth_curves_reflect_the_last_control_point(self):
        got = IR.parse_path("M 0 0 C 0 10 10 10 10 0 S 20 -10 20 0")
        assert got[2] == ("C", 10.0, -10.0, 20.0, -10.0, 20.0, 0.0)
        got = IR.parse_path("M 0 0 Q 5 10 10 0 T 20 0")
        assert got[2] == ("Q", 15.0, -10.0, 20.0, 0.0)

    def test_z_returns_the_pen_to_the_subpath_start(self):
        got = IR.parse_path("M 1 1 L 5 1 Z l 1 1")
        assert got[-1] == ("L", 2.0, 2.0)

    def test_a_bad_path_is_refused_not_guessed(self):
        with pytest.raises(ValueError):
            IR.parse_path("M 0 0 L 5")
        with pytest.raises(ValueError):
            IR.parse_path("M 0 0 A 5 5 0 2 1 3 3")     # a flag must be 0 or 1


# ---------------------------------------------------------------- transforms
class TestTransforms:
    def test_a_list_composes_left_to_right(self):
        # translate then scale: a point at (1, 1) goes to (2*1 + 10, 2*1 + 0)
        m = IR.parse_transform("translate(10,0) scale(2)")
        assert IR.apply(m, 1, 1) == (12.0, 2.0)
        # the other order is a different place, which is the whole point of testing it
        m2 = IR.parse_transform("scale(2) translate(10,0)")
        assert IR.apply(m2, 1, 1) == (22.0, 2.0)

    def test_rotate_about_a_centre(self):
        m = IR.parse_transform("rotate(90 10 10)")
        x, y = IR.apply(m, 20, 10)
        assert x == pytest.approx(10.0) and y == pytest.approx(20.0)

    def test_the_y_flip_the_order_plates_use(self):
        m = IR.parse_transform("translate(0,100) scale(2,-2)")
        assert IR.apply(m, 3, 4) == (6.0, 92.0)
        assert IR.det(m) < 0

    def test_nested_groups_compose_outermost_first(self):
        ink = IR.Ink('<svg xmlns="http://www.w3.org/2000/svg"><g transform="translate(100,0)">'
                     '<g transform="scale(2)"><line x1="1" y1="1" x2="2" y2="1"/></g></g></svg>')
        (ln,) = ink.select("line")
        assert ln.points() == [(102.0, 2.0), (104.0, 2.0)]


# ---------------------------------------------------------------- arcs
class TestArcCentre:
    def test_a_quarter_circle(self):
        cx, cy, rx, ry, th1, dth = IR.arc_centre(10, 0, 10, 10, 0.0, 0, 1, 0, 10)
        assert (cx, cy) == (pytest.approx(0.0, abs=1e-9), pytest.approx(0.0, abs=1e-9))
        assert dth == pytest.approx(math.pi / 2)

    def test_the_sweep_flag_picks_the_other_centre(self):
        a = IR.arc_centre(10, 0, 10, 10, 0.0, 0, 1, 0, 10)
        b = IR.arc_centre(10, 0, 10, 10, 0.0, 0, 0, 0, 10)
        assert (b[0], b[1]) == (pytest.approx(10.0), pytest.approx(10.0))
        assert a[5] > 0 > b[5]

    def test_radii_too_small_are_scaled_up_not_refused(self):
        # F.6.6: endpoints 20 apart with a radius of 5 draw a half circle of radius 10
        cx, cy, rx, ry, _t, dth = IR.arc_centre(0, 0, 5, 5, 0.0, 0, 1, 20, 0)
        assert rx == pytest.approx(10.0) and ry == pytest.approx(10.0)
        assert abs(dth) == pytest.approx(math.pi)

    def test_degenerate_arcs_do_not_divide_by_zero(self):
        assert IR.arc_centre(0, 0, 0, 5, 0.0, 0, 1, 3, 4)[5] == 0.0
        assert IR.arc_centre(2, 2, 5, 5, 0.0, 0, 1, 2, 2)[5] == 0.0

    def test_the_sampled_arc_lies_on_its_circle(self):
        cmds = IR.parse_path("M 10 0 A 10 10 0 0 1 0 10")
        (pts,) = IR.sample_commands(cmds, n=8)
        for x, y in pts:
            assert math.hypot(x, y) == pytest.approx(10.0)


class TestFitCircle:
    def test_points_on_a_circle_fit_exactly(self):
        pts = [(3 + 5 * math.cos(t), -2 + 5 * math.sin(t)) for t in (0.1, 0.7, 1.3, 2.0, 2.6)]
        cx, cy, r, rms = IR.fit_circle(pts)
        assert (cx, cy, r) == (pytest.approx(3.0), pytest.approx(-2.0), pytest.approx(5.0))
        assert rms < 1e-9

    def test_a_parabola_is_not_a_circle(self):
        # A quadratic Bezier through the same ends and apex as a circular segment: the reader
        # must be able to tell them apart, because that is the question a drawn arch head asks.
        span, rise = 40.0, 4.0
        (par,) = IR.sample_commands(IR.parse_path("M 0 0 Q 20 %s 40 0" % (2 * rise)), n=32)
        r = (span * span / 4 + rise * rise) / (2 * rise)
        a0 = math.asin((span / 2) / r)
        circ = [(20 + r * math.sin(t), rise - r + r * math.cos(t)) for t in
                [(-a0 + 2 * a0 * i / 32) for i in range(33)]]
        assert IR.fit_circle(circ)[3] < 1e-9
        assert IR.fit_circle(par)[3] > 1e-3

    def test_collinear_points_are_refused(self):
        with pytest.raises(ValueError):
            IR.fit_circle([(0, 0), (1, 1), (2, 2)])


# ---------------------------------------------------------------- the style cascade
SHEET = ('<svg xmlns="http://www.w3.org/2000/svg"><style>'
         '.w-med{stroke-width:1.2}.mt{stroke-width:1.0;stroke:#111}'
         'text{font-size:9px}.big{font-size:12px}.k{stroke-width:3 !important}'
         '.g .inner{stroke:#f00}</style>'
         '<line class="mt w-med" x1="0" y1="0" x2="1" y2="0"/>'
         '<line class="w-med mt" x1="0" y1="0" x2="1" y2="0"/>'
         '<line class="mt" stroke-width="7" x1="0" y1="0" x2="1" y2="0"/>'
         '<line class="mt" style="stroke-width:5" x1="0" y1="0" x2="1" y2="0"/>'
         '<line class="k" style="stroke-width:5" x1="0" y1="0" x2="1" y2="0"/>'
         '<g class="g" stroke-width="4"><line class="inner" x1="0" y1="0" x2="1" y2="0"/></g>'
         '<text class="big" x="1" y="2">A</text><text x="1" y="2">B</text>'
         '</svg>')


class TestTheCascade:
    def test_source_order_decides_between_equal_selectors_whatever_the_class_order(self):
        # The trap the single-class matcher cannot see: `.mt` is written after `.w-med`, so it
        # wins on an element carrying both, in whichever order the element lists them.
        ink = IR.Ink(SHEET)
        a, b = ink.select("line")[:2]
        assert a.style["stroke-width"] == "1.0" and b.style["stroke-width"] == "1.0"

    def test_a_presentation_attribute_loses_to_any_rule(self):
        ink = IR.Ink(SHEET)
        assert ink.select("line")[2].style["stroke-width"] == "1.0"

    def test_inline_beats_a_rule_and_important_beats_inline(self):
        ink = IR.Ink(SHEET)
        assert ink.select("line")[3].style["stroke-width"] == "5"
        assert ink.select("line")[4].style["stroke-width"] == "3"

    def test_inherited_properties_inherit_and_descendant_selectors_match(self):
        ink = IR.Ink(SHEET)
        inner = ink.select("line", cls="inner")[0]
        assert inner.style["stroke-width"] == "4"      # from the group, inherited
        assert inner.style["stroke"] == "#f00"         # `.g .inner`

    def test_a_descendant_rule_beats_a_later_rule_of_lower_specificity(self):
        """WP-14.6, auditor C. `.g .inner` was the only rule the sheet above gives `.inner`, so a
        cascade that scored a selector by its LAST compound alone -- `.inner`, (0,1,0) -- could
        not be told from a correct one. Here a less specific rule comes later: `.g .x` is (0,2,0)
        and wins whatever the source order; `.x` alone decides only outside the group."""
        ink = IR.Ink('<svg xmlns="http://www.w3.org/2000/svg"><style>'
                     '.g .x{stroke:#f00}.x{stroke:#00f}</style>'
                     '<g class="g"><line class="x" x1="0" y1="0" x2="1" y2="0"/></g>'
                     '<line class="x" x1="0" y1="0" x2="1" y2="0"/></svg>')
        inside, outside = ink.select("line")
        assert inside.style["stroke"] == "#f00", "the descendant rule is more specific"
        assert outside.style["stroke"] == "#00f"

    def test_a_class_beats_a_tag(self):
        ink = IR.Ink(SHEET)
        big, plain = [t[2] for t in ink.texts()]
        assert big.style["font-size"] == "12px" and plain.style["font-size"] == "9px"


# ---------------------------------------------------------------- the frame
class TestTheFrame:
    def test_to_model_inverts_the_documented_affine(self):
        plate = {"id": "S", "px_per_ft": 24.0, "origin_px": [46, 34], "at_origin_ft": [0.0, 40.0]}
        assert IR.to_model(plate, 46, 34) == (0.0, 40.0)
        u, v = IR.to_model(plate, 46 + 24 * 3, 34 + 24 * 10)
        assert (u, v) == (3.0, 30.0)
        assert IR.from_model(plate, u, v) == (46 + 72.0, 34 + 240.0)

    def test_the_frame_is_read_off_the_root_attribute(self):
        frames = {"plates": [{"id": "0", "proj": "plan", "px_per_ft": 13, "origin_px": [5, 6],
                              "at_origin_ft": [0, 30]}]}
        svg = ("<svg xmlns='http://www.w3.org/2000/svg' data-frame='%s'></svg>"
               % json.dumps(frames).replace("'", "&apos;"))
        ink = IR.Ink(svg)
        assert ink.frame("0")["px_per_ft"] == 13
        assert ink.frame("nope") is None
