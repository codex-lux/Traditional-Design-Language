"""What is DRAWN, not what was modelled — the layer WP-5.11 left unguarded.

WP-5.11 replaced a set of hand-tuned Beziers with real constructions and asserted them thoroughly:
convexity, tangency at a cyma's join, scale invariance, the datum rule. Every one of those tests
passes on the model. None of them looks at the path the renderer actually emits, and an
adversarial audit of that package found six construction and serialiser bugs that ship green
through all 34 checks, 970 tests, the selftest AND the browser walk — the headline being that
`svg_path()` emitted an inverted sweep flag, so every arc in the corpus was drawn as its own
mirror image about its chord.

That is the same disease as the `TestSegTo` block WP-5.11 deleted, one layer out. TestSegTo pinned
the control-point arithmetic of a curve that had silently degenerated to a straight line; these
tests pin the constructions of a curve that was silently being drawn backwards. In both cases the
model was interrogated and the drawing was not.

So this file starts from the emitted string and works backwards:

  * `_svg_arc_centre` is the W3C SVG 1.1 F.6.5 endpoint-to-centre parameterisation, implemented
    here rather than imported from the code under test, because a guard that shares an
    implementation with its subject cannot catch that implementation being wrong.
  * `drawn_points` renders a member through the real `svg_path()` and returns where the ink
    actually goes.
  * The convexity assertions then ask the only question that matters to a reader: on the SHEET,
    does an ovolo bulge out and a cavetto hollow in?

A cheaper version of this file would compare `svg_path()` output to a stored string. That is what
TestSegTo did, and it is why nobody noticed.
"""
import json
import math
import os
import re
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

PROF = modcache.load("profiles", os.path.join(ROOT, "build", "profiles.py"))
PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))

# A real plate's transforms: x scaled, y FLIPPED (model inches up, screen pixels down). Every
# drawing surface in this corpus does this, which is exactly why the sweep flag is easy to get
# backwards and impossible to notice from the model side.
K, OX, OY = 4.0, 100.0, 500.0
SX = lambda x: OX + x * K          # noqa: E731
SY = lambda y: OY - y * K          # noqa: E731


def _svg_arc_centre(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    """W3C SVG 1.1 F.6.5. Deliberately an independent implementation."""
    cphi, sphi = math.cos(phi), math.sin(phi)
    dx2, dy2 = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p, y1p = cphi * dx2 + sphi * dy2, -sphi * dx2 + cphi * dy2
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        rx *= math.sqrt(lam)
        ry *= math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den))
    if fa == fs:
        co = -co
    cxp, cyp = co * (rx * y1p / ry), co * (-ry * x1p / rx)
    cx = cphi * cxp - sphi * cyp + (x1 + x2) / 2.0
    cy = sphi * cxp + cphi * cyp + (y1 + y2) / 2.0

    def ang(ux, uy, vx, vy):
        d = (ux * vx + uy * vy) / (math.hypot(ux, uy) * math.hypot(vx, vy))
        a = math.acos(max(-1.0, min(1.0, d)))
        return -a if (ux * vy - uy * vx) < 0 else a

    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if fs == 0 and dth > 0:
        dth -= 2 * math.pi
    if fs == 1 and dth < 0:
        dth += 2 * math.pi
    return cx, cy, rx, ry, th1, dth


_TOK = re.compile(r"([MLA])\s*([-\d.,\s]+)")


def drawn_points(segments, start, n=24):
    """Every point the emitted path actually puts ink on, in SCREEN coordinates."""
    d = PROF.svg_path(segments, SX, SY, start=start)
    pts, cur = [], None
    for kind, body in _TOK.findall(d):
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", body)]
        if kind == "M":
            cur = (nums[0], nums[1])
            pts.append(cur)
        elif kind == "L":
            cur = (nums[0], nums[1])
            pts.append(cur)
        elif kind == "A":
            rx, ry, _rot, fa, fs, x2, y2 = nums[0], nums[1], nums[2], int(nums[3]), int(nums[4]), nums[5], nums[6]
            cx, cy, rx, ry, th1, dth = _svg_arc_centre(cur[0], cur[1], rx, ry, 0.0, fa, fs, x2, y2)
            for i in range(1, n + 1):
                th = th1 + dth * (i / n)
                pts.append((cx + rx * math.cos(th), cy + ry * math.sin(th)))
            cur = (x2, y2)
    return pts


def _member(profile, x_from=0.0, y0=0.0, x_face=4.0, y1=6.0, note=None):
    segs, _ = PROF.member_path(profile, x_from, y0, x_face, y1, note=note)
    return segs, PROF.arc_point(segs[0], 0.0) if segs and segs[0]["kind"] == "arc" else (x_from, y0)


def _side_of_chord(pts, p_start, p_end):
    """+1 where the drawn curve lies OUTBOARD of its own chord, -1 inboard, on the sheet.

    'Outboard' is +x in screen space, which is away from the wall/axis on every plate here."""
    out = []
    for x, y in pts:
        if abs(p_end[1] - p_start[1]) < 1e-9:
            continue
        t = (y - p_start[1]) / (p_end[1] - p_start[1])
        if not (0.02 < t < 0.98):
            continue
        chord_x = p_start[0] + (p_end[0] - p_start[0]) * t
        if abs(x - chord_x) > 1e-6:
            out.append(1 if x > chord_x else -1)
    return out


class TestTheDrawnArcIsTheArcThatWasModelled:
    """The round trip. An arc emitted and read back must land where the engine put it.

    This is the assertion that was missing, and the one that catches an inverted sweep flag —
    a bug invisible from the model side, invisible in the path string, and visible only if you
    ask where the ink goes."""

    @pytest.mark.parametrize("profile", ["ovolo", "cavetto", "cyma-recta", "cyma-reversa", "ogee",
                                         "torus", "astragal", "scotia", "apophyge", "echinus",
                                         "quarter-round", "bead"])
    def test_every_construction_draws_where_it_was_built(self, profile):
        segs, _ = PROF.member_path(profile, 0.0, 0.0, 4.0, 6.0)
        arcs = [s for s in segs if s["kind"] == "arc"]
        if not arcs:
            pytest.skip(f"{profile} draws no arc at this geometry")
        for i, seg in enumerate(arcs):
            model_mid = PROF.arc_point(seg, 0.5)
            want = (SX(model_mid[0]), SY(model_mid[1]))
            start = PROF.arc_point(seg, 0.0)
            got = drawn_points([seg], start, n=2)[1]   # the midpoint of a 2-step walk
            assert got[0] == pytest.approx(want[0], abs=0.05), (
                f"{profile} arc {i}: drawn at x={got[0]:.2f}, modelled at x={want[0]:.2f} — "
                f"the arc is being drawn as its own mirror about its chord")
            assert got[1] == pytest.approx(want[1], abs=0.05)

    def test_the_whole_corpus_round_trips(self):
        """Not one construction at one size: every arc of every order pack, as drawn.

        Judged by WHICH SIDE OF ITS OWN CHORD the ink lands on, because that is what mirroring
        is. Comparing positions exactly would fail on arcs that are numerically degenerate rather
        than wrong — chambers-tuscan's shaft conge is an ellipse of aspect 1341:1 spanning three
        thousandths of an inch, and reconstructing its parameter through the W3C rule loses half
        a pixel to float error while its side is never in doubt.

        An arc whose sagitta is under a fifth of a pixel cannot be told from a straight line on
        any sheet, so it is COUNTED AND NAMED rather than judged — could-not-evaluate kept
        distinct from passed, which is this corpus's first rule."""
        mirrored, unjudgeable = [], 0
        for pid, pack in PE.PACKS.items():
            if pack.get("kind") != "order-system":
                continue
            resolved = PE.resolve(pid)
            dim = PE.dimension(resolved, 36.0)
            geo = PROF.pack_geometry(dim, resolved.get("column"), dim.get("projection_datum"))
            for asm in geo["assemblies"]:
                for seg in asm["segments"]:
                    if seg["kind"] != "arc":
                        continue
                    p0, p1 = PROF.arc_point(seg, 0.0), PROF.arc_point(seg, 1.0)
                    model_mid = PROF.arc_point(seg, 0.5)
                    chord = ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0)
                    sagitta = math.hypot(model_mid[0] - chord[0], model_mid[1] - chord[1]) * K
                    if sagitta < 0.2:
                        unjudgeable += 1
                        continue
                    want_side = math.copysign(1.0, (model_mid[0] - chord[0]) or (chord[1] - model_mid[1]))
                    got = drawn_points([seg], p0, n=2)[1]
                    gchord = ((SX(p0[0]) + SX(p1[0])) / 2.0, (SY(p0[1]) + SY(p1[1])) / 2.0)
                    got_side = math.copysign(1.0, (got[0] - gchord[0]) or (gchord[1] - got[1]))
                    if want_side != got_side:
                        mirrored.append(f"{pid}/{asm['id']}")
                        break
        assert not mirrored, (
            f"{len(mirrored)} assemblies draw arcs on the wrong side of their own chord: "
            f"{sorted(set(mirrored))[:8]}")
        assert unjudgeable < 40, (
            f"{unjudgeable} arcs are too flat to judge — that is more than this corpus should "
            f"contain, and suggests projections are collapsing somewhere upstream")


class TestTheDrawnShapeIsTheClassicalShape:
    """Convexity, judged on the SHEET.

    The classical definitions, which are what a reader fluent in this language sees first:
      ovolo / echinus / quarter-round   convex — bulges out of its chord
      cavetto / apophyge / conge        concave — falls inside it
      cyma recta                        CONCAVE ABOVE, convex below (the crowning cymatium)
      cyma reversa / ogee               CONVEX ABOVE, concave below (the bed mould)
      torus / astragal / bead           a half round standing proud of its own plane
      scotia                            a hollow, and its throat is the deepest point
    """

    @pytest.mark.parametrize("profile", ["ovolo", "quarter-round", "echinus"])
    def test_a_convex_quarter_bulges_out_on_the_sheet(self, profile):
        segs, _ = PROF.member_path(profile, 0.0, 0.0, 4.0, 6.0)
        pts = drawn_points(segs, (0.0, 0.0))
        sides = _side_of_chord(pts, (SX(0.0), SY(0.0)), (SX(4.0), SY(6.0)))
        assert sides and all(s > 0 for s in sides), f"{profile} is drawn hollow"

    @pytest.mark.parametrize("profile", ["cavetto", "apophyge", "congé"])
    def test_a_concave_quarter_hollows_in_on_the_sheet(self, profile):
        segs, _ = PROF.member_path(profile, 0.0, 0.0, 4.0, 6.0)
        pts = drawn_points(segs, (0.0, 0.0))
        sides = _side_of_chord(pts, (SX(0.0), SY(0.0)), (SX(4.0), SY(6.0)))
        assert sides and all(s < 0 for s in sides), f"{profile} is drawn bulging"

    @pytest.mark.parametrize("profile", ["ovolo", "cavetto"])
    def test_a_receding_member_keeps_its_own_character(self, profile):
        """A member may draw BACK as it rises (above a corona, at the foot of a shaft). An ovolo
        that recedes is still convex; letting the sign of dx decide convexity turns every congé
        at the foot of a Tuscan shaft into a bulge."""
        segs, _ = PROF.member_path(profile, 6.0, 0.0, 2.0, 4.0)
        pts = drawn_points(segs, (6.0, 0.0))
        sides = _side_of_chord(pts, (SX(6.0), SY(0.0)), (SX(2.0), SY(4.0)))
        want = 1 if profile == "ovolo" else -1
        assert sides and all(s == want for s in sides), (
            f"a receding {profile} changed character: the sign of dx must not decide convexity")

    def test_cyma_recta_is_concave_above_and_convex_below(self):
        """The crowning cymatium. Britannica and Oxford both: the cyma recta has its CONCAVE part
        uppermost. Getting this backwards draws every cornice in the corpus upside down in its
        curves and is invisible to any test that only asks whether two arcs meet smoothly."""
        segs, _ = PROF.member_path("cyma-recta", 0.0, 0.0, 4.0, 8.0)
        pts = drawn_points(segs, (0.0, 0.0))
        p0, p1 = (SX(0.0), SY(0.0)), (SX(4.0), SY(8.0))
        lower = [p for p in pts if p[1] > (p0[1] + p1[1]) / 2]     # screen y down: larger = lower
        upper = [p for p in pts if p[1] < (p0[1] + p1[1]) / 2]
        assert all(s > 0 for s in _side_of_chord(lower, p0, p1)), "cyma recta: lower half is not convex"
        assert all(s < 0 for s in _side_of_chord(upper, p0, p1)), "cyma recta: upper half is not concave"

    @pytest.mark.parametrize("profile", ["cyma-reversa", "ogee"])
    def test_cyma_reversa_is_convex_above_and_concave_below(self, profile):
        segs, _ = PROF.member_path(profile, 0.0, 0.0, 4.0, 8.0)
        pts = drawn_points(segs, (0.0, 0.0))
        p0, p1 = (SX(0.0), SY(0.0)), (SX(4.0), SY(8.0))
        lower = [p for p in pts if p[1] > (p0[1] + p1[1]) / 2]
        upper = [p for p in pts if p[1] < (p0[1] + p1[1]) / 2]
        assert all(s < 0 for s in _side_of_chord(lower, p0, p1)), f"{profile}: lower half is not concave"
        assert all(s > 0 for s in _side_of_chord(upper, p0, p1)), f"{profile}: upper half is not convex"

    @pytest.mark.parametrize("profile", ["torus", "astragal", "bead"])
    def test_a_half_round_stands_proud_of_its_own_plane(self, profile):
        """A torus is a roll, and it stands proud of ITS OWN springing plane — not necessarily of
        the member below it, which may well project further and leave the roll set back. Drawn
        inward it is a groove bitten into that member, which is what a signed bulge produces when
        a pack records the face inboard of where the pen currently stands."""
        for x_from, x_face in ((2.0, 5.0), (5.0, 2.0), (3.0, 3.0)):
            segs, _ = PROF.member_path(profile, x_from, 0.0, x_face, 6.0)
            arcs = [s for s in segs if s["kind"] == "arc"]
            assert arcs, f"{profile} drew no roll at all"
            springs = [PROF.arc_point(arcs[0], 0.0), PROF.arc_point(arcs[-1], 1.0)]
            crown = max(PROF.arc_point(a, t / 8)[0] for a in arcs for t in range(9))
            assert crown > max(p[0] for p in springs) + 1e-6, (
                f"{profile} from {x_from} to {x_face} is drawn as a hollow, not a roll")
            assert springs[0][0] == pytest.approx(springs[1][0], abs=1e-6), (
                f"{profile} does not return to the plane it sprang from")

    def test_a_scotia_has_a_throat_and_not_a_beak(self):
        """The deepest point of a scotia is a throat: the curve turns through it. Two arcs meeting
        with opposing horizontal tangents give a cusp — a beak sticking into the hollow."""
        segs, _ = PROF.member_path("scotia", 4.0, 0.0, 4.0, 6.0)
        pts = drawn_points(segs, (4.0, 0.0), n=48)
        xs = [p[0] for p in pts]
        i = xs.index(min(xs))
        assert 2 < i < len(pts) - 3, "the scotia's deepest point is at one of its ends"
        # Around a throat the curve advances in y monotonically; at a cusp it stalls and reverses.
        ys = [p[1] for p in pts[i - 2:i + 3]]
        steps = [b - a for a, b in zip(ys, ys[1:])]
        assert all(s < 0 for s in steps) or all(s > 0 for s in steps), (
            "the scotia reverses direction at its deepest point — that is a beak, not a throat")


class TestTheCadFileAndTheSheetAgreeOnTheCurve:
    """docs/export.md says the cornice in the CAD file is the same curve as the cornice on the
    sheet rather than a polygon approximating it. That claim is only true if the two serialisers
    agree about which way the arc turns — and they derive it independently."""

    @pytest.mark.parametrize("profile", ["ovolo", "cavetto", "cyma-recta", "cyma-reversa", "torus"])
    def test_dxf_bulges_and_svg_arcs_describe_the_same_curve(self, profile):
        segs, _ = PROF.member_path(profile, 0.0, 0.0, 4.0, 6.0)
        arcs = [s for s in segs if s["kind"] == "arc" and abs(s["rx"] - s["ry"]) < 1e-6]
        for seg in arcs:
            start = PROF.arc_point(seg, 0.0)
            end = PROF.arc_point(seg, 1.0)
            pts = PROF.dxf_points([seg], start)
            bulge = pts[0][2]
            # A bulge is tan(theta/4) of the included angle, signed CCW-positive in MODEL space.
            # Reconstruct the arc's midpoint from the bulge and compare to the model's own.
            cx, cy = (start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0
            dx, dy = (end[0] - start[0]) / 2.0, (end[1] - start[1]) / 2.0
            # A positive bulge is a counter-clockwise arc, and its sagitta stands off the chord
            # to the RIGHT of the direction of travel — the half-chord turned -90 degrees, not
            # +90. Checked against a plain CCW quarter circle before it was trusted here.
            mid = (cx + dy * bulge, cy - dx * bulge)
            want = PROF.arc_point(seg, 0.5)
            assert mid[0] == pytest.approx(want[0], abs=1e-6), (
                f"{profile}: the DXF bulge and the model disagree about which way the arc turns")
            assert mid[1] == pytest.approx(want[1], abs=1e-6)


class TestTheRoofIsOnTheSheet:
    """WP-5.13. The front elevation of a side-gable house had no roof on it at all.

    `roof.py::elevation_profile` returned two points, both at the eave, for a long face, on the
    reasoning that "the ridge is behind the near roof plane, not visible". That is a PERSPECTIVE
    argument applied to an ORTHOGRAPHIC projection: the near plane slopes away from the viewer and
    parallel projection maps it to a full-width band from eave to ridge. The Tidewater reference
    sheet was 14.22 ft short — the whole roof — which is why a five-bay Georgian read as a box.

    Nothing caught it because every roof test asked the RECORD for the ridge height, and the
    record had it right. Only the profile was wrong, and only the drawing consumed the profile."""

    # `section=`, NOT POSITIONAL, and the keyword is the whole of a defect WP-11.2 exposed.
    # `build_roof(plan, parti=None, section=None)` binds a positional second argument to
    # PARTI, so `build_roof(plan, st.build_section(plan))` handed the section in as the parti
    # and build_roof then derived a SECOND section of its own from it. Two buildings, one
    # test -- WP-6.4's finding inside a test written after it. It was invisible for as long as
    # nothing in a parti reached the footprint: both sections came out identical. WP-11.2 made
    # the parti's bay module reach `derive_footprint`, and the roof was then built over a
    # 70.0 x 34.4 ft house while the assertions read the footprint of a 63.0 x 38.2 one.
    def _profiles(self):
        rf = modcache.load("roof", os.path.join(ROOT, "build", "roof.py"))
        st = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))
        import json as _j
        plan = _j.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        return rf, st, plan

    def test_a_side_gable_front_reaches_the_ridge(self):
        rf, st, plan = self._profiles()
        roof = rf.build_roof(plan, section=st.build_section(plan))
        ridge_ft = max(h for _, h in roof["elevation_profiles"]["E"])   # the gable end knows it
        front = roof["elevation_profiles"]["S"]
        assert max(h for _, h in front) == pytest.approx(ridge_ft, abs=0.01), (
            "the front elevation stops at the eave: the roof is missing from the sheet")
        assert len(front) >= 4, "a roof plane is an area, not a line"

    def test_a_hip_front_is_a_trapezoid_whose_ridge_is_length_minus_depth(self):
        """The one construction that settles a hip: for an equal-pitch hip the ridge is exactly
        (length - depth), because each hip runs in at 45 degrees in PLAN. If the drawn ridge is
        any other length the hips are not at the roof's own pitch and the silhouette is a
        different building."""
        import copy
        import json as _j
        rf, st, plan = self._profiles()
        hip = copy.deepcopy(plan)
        hip["declared"]["roof_form"] = "hip"
        roof = rf.build_roof(hip, section=st.build_section(hip))
        front = roof["elevation_profiles"]["S"]
        top = max(h for _, h in front)
        at_ridge = [x for x, h in front if abs(h - top) < 1e-6]
        assert len(at_ridge) == 2, "a hip front should meet the ridge along a run, not at a point"
        fp = st.build_section(hip)["footprint"]
        assert max(at_ridge) - min(at_ridge) == pytest.approx(
            fp["width_ft"] - fp["depth_ft"], abs=0.05), "the hip ridge is not (length - depth)"

    def test_the_gable_end_is_still_a_triangle(self):
        rf, st, plan = self._profiles()
        roof = rf.build_roof(plan, section=st.build_section(plan))
        end = roof["elevation_profiles"]["E"]
        top = max(h for _, h in end)
        assert len([x for x, h in end if abs(h - top) < 1e-6]) == 1, "a gable end peaks at a point"


class TestTheGaugedArchIsDrawnAsBrickwork:
    """HABS 4.6.2 names round, jack and flat arches as the one place individual bricks are drawn
    even where the rest of the wall carries only coursing. A gauged arch drawn as a plain block is
    the detail a fluent reader checks first on a Chesapeake front."""

    def _svg(self, tmp_path):
        import json as _j
        e = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        r = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
        plan = _j.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        elev = e.build_elevation(plan)
        out = str(tmp_path / "e.svg")
        r.render_elevation(elev, out)
        return open(out).read(), elev

    def test_every_arch_carries_radiating_voussoir_joints(self, tmp_path):
        import re
        svg, elev = self._svg(tmp_path)
        arches = len(re.findall(r'class="arch', svg))
        joints = len(re.findall(r'class="vsr', svg))
        assert arches, "no arch is drawn at all"
        per = joints / arches
        # A voussoir is a rubbed brick on edge, so its soffit width is one course. Over these
        # openings that is eleven to fifteen bricks; anything far outside says the count is being
        # taken off the wrong dimension (off the arch DEPTH it came out at five: eight-inch
        # voussoirs, which are not bricks).
        assert 9 <= per <= 17, f"{per:.1f} joints per arch: the voussoirs are not brick-sized"

    def test_the_flat_arch_splays_to_its_skewback(self, tmp_path):
        """A gauged flat arch's extrados is WIDER than its soffit -- the skewbacks are cut at 60
        degrees, so the arch runs out past the opening by depth/tan(60) at each end. Drawn square
        it hides the joint that makes a flat arch stand up, and the outer voussoir joints run off
        into the wall with nothing to stop them."""
        import re
        svg, elev = self._svg(tmp_path)
        m = re.search(r'class="arch[^"]*" d="M ([\d.]+),([\d.]+) Q [\d.]+,[\d.]+ ([\d.]+),[\d.]+ '
                      r'L ([\d.]+),([\d.]+) L ([\d.]+),', svg)
        assert m, "no flat-arch path found in the expected form"
        x_soffit_l, x_soffit_r = float(m.group(1)), float(m.group(3))
        x_ext_r, x_ext_l = float(m.group(4)), float(m.group(6))
        assert x_ext_r > x_soffit_r + 1.0, "the extrados does not splay to the right"
        assert x_ext_l < x_soffit_l - 1.0, "the extrados does not splay to the left"
        splay = ((x_ext_r - x_soffit_r) + (x_soffit_l - x_ext_l)) / 2.0
        depth = float(m.group(2)) - float(m.group(5))
        assert splay == pytest.approx(depth / math.tan(math.radians(60.0)), rel=0.05), (
            "the skewback is not at 60 degrees")


class TestRelieflsDrawnInLineNotInTone:
    """WP-5.13. A projection drawn at its true width against a flat wall is still a flat wall on
    the sheet — which is most of why this elevation read as a diagram rather than a building.

    The convention is not decorative and it is not free-hand: the light comes over the viewer's
    left shoulder at 45 degrees, so every projecting member is lit on its top and left and dark on
    its underside and right, and the depth of the cast shadow equals the member's own projection
    exactly. HABS prohibits shading in elevation outright and blesses this instead — accenting the
    shadowed edge is the line-only way to get relief.

    Guarded because it is the class of thing that silently stops happening: nothing else in the
    suite would notice if every shade line vanished, and the drawing would go back to flat."""

    def _svg(self, tmp_path, plan_id="tidewater-georgian-careful"):
        import json as _j
        e = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        r = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
        elev = e.build_elevation(_j.load(open(os.path.join(ROOT, "plans", f"{plan_id}.json"))))
        out = str(tmp_path / f"{plan_id}.svg")
        r.render_elevation(elev, out)
        return open(out).read(), elev

    def test_every_projecting_band_carries_a_shade_line(self, tmp_path):
        import re
        svg, elev = self._svg(tmp_path)
        n = len(re.findall(r'class="shade', svg))
        # water table, belt course, cornice -- the three bands that project from the wall plane
        assert n >= 3, f"only {n} shade lines: the projecting bands are drawn flat"

    def test_a_masonry_reveal_shades_its_head_and_left_jamb(self, tmp_path):
        """The recess is what makes a brick elevation read as a mass with holes in it. Light from
        the upper left puts the shadow on the head and the LEFT jamb — not the right, which is the
        lit side, and drawing it there would light the building from the wrong quarter."""
        import re
        svg, elev = self._svg(tmp_path)
        band = elev["storey_windows"][0].get("reveal_band_in")
        assert band, "the masonry kit states a reveal and the record dropped it"
        # nine openings, each contributing a head and a jamb, on top of the three bands
        assert len(re.findall(r'class="shade', svg)) >= 3 + 2 * 9

    def test_a_frame_wall_gets_no_reveal_shadow(self, tmp_path):
        """A frame house has an architrave standing PROUD of the sheathing, not a recess cut into
        a 13 1/2 in wall. Drawing a reveal shadow on it would assert a detail of the wrong
        construction — and the corpus says so: `reveal_frame` carries no figure for this style."""
        import re
        svg, elev = self._svg(tmp_path, "spec-builder-colonial")
        assert not elev["storey_windows"][0].get("reveal_band_in")
        assert len(re.findall(r'class="shade', svg)) <= 4, (
            "a frame wall is being given a masonry reveal's shadow")


class TestNoOpeningIsDrawnWhereAStackStands:
    """OQ 85, closed 27 Aug 2026 (WP-5.14).

    `roof.py` puts this house's stacks at `y_ft` 21.33 on a gable end 42.66 ft deep — its exact
    centre line — and `_face_bays()` independently spaces an odd bay count evenly, which puts a
    window centre at 21.33 too. Two records built from different rules, never compared, so the
    elevation drew a window where a chimney stands. It was found by drawing the stack from grade
    for one revision; no test of either record could see it, because each is right on its own.
    """

    def _rec(self, style_plan="tidewater-georgian-careful"):
        import json as _j
        e = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        return e.build_elevation(_j.load(open(os.path.join(ROOT, "plans", f"{style_plan}.json"))))

    def test_the_gable_end_centre_bay_is_blind_and_the_flanks_are_not(self):
        rec = self._rec()
        for f in ("E", "W"):
            kinds = rec["faces"][f]["kinds"]
            assert kinds == ["window", "blind", "window"], f"{f}: {kinds}"
            # 20.375, moved from 21.33 by WP-11.2: the stack stands on the gable end's own
            # centre line, and that depth moved when the plan began taking its parti's bay
            # module (40.75 ft outside, from 42.66). The NUMBER is not the subject here --
            # the subject is that the blind bay's centre and the stack's axis are still ONE
            # number, which is what OQ 85 closed. So this reads the roof's own stack axis
            # rather than a literal, and cannot go stale again with the footprint.
            rf = modcache.load("roof", os.path.join(ROOT, "build", "roof.py"))
            st = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))
            import json as _j2
            _plan = _j2.load(open(os.path.join(ROOT, "plans",
                                               "tidewater-georgian-careful.json")))
            _roof = rf.build_roof(_plan, section=st.build_section(_plan))
            axes = sorted({round(c["y_ft"], 3) for c in _roof["chimneys"]["positions"]
                           if c.get("y_ft") is not None})
            assert axes, "the fixture is blind: this roof places no stack with an axis"
            assert rec["faces"][f]["blind_bay_centres_ft"] == [pytest.approx(axes[0], abs=0.01)]
            assert rec["faces"][f].get("blind_bay_reason")

    def test_the_long_faces_lose_nothing(self):
        """The rule must be a collision test, not "gable ends have a blind centre". Both stacks
        are at mid-DEPTH, so they stand in the gable walls and in neither long wall, and the front
        keeps all five bays."""
        rec = self._rec()
        for f in ("S", "N"):
            assert "blind" not in rec["faces"][f]["kinds"], f
            assert rec["faces"][f].get("blind_bay_centres_ft") is None

    def test_the_blind_bay_draws_no_opening_at_either_storey(self, tmp_path):
        """An exterior end stack runs the full height of the wall, so BOTH storeys lose the
        opening. Asserted off the emitted SVG, and the bay count is asserted first so a selector
        matching nothing cannot pass this vacuously."""
        import re
        r = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
        rec = self._rec()
        out = str(tmp_path / "e.svg")
        r.render_elevation(rec, out, face="E")
        svg = open(out).read()
        assert len(rec["faces"]["E"]["centres_ft"]) == 3, "three bays, or this test proves nothing"
        # x AND width, because the first version compared a LEFT EDGE against a bay CENTRE with a
        # 24 px threshold — and an opening is 33.8-38.6 in wide, so a window drawn dead on the
        # stack's axis has a left edge 34-39 px away and passed. Proven by no-op'ing the blinder:
        # all six openings appeared, the centre bay was glazed, and every iteration still passed.
        opens = [(float(a), float(b)) for a, b in
                 re.findall(r'<rect class="op"[^>]*x="([-\d.]+)"[^>]*width="([-\d.]+)"', svg)]
        assert len(opens) == 4, f"two glazed bays x two storeys, got {len(opens)}"
        blind_px = 46.0 + 21.33 * 24.0                      # the same pad and scale the sheet uses
        stack_half_px = (rec.get("chimney_stack_plan_in") or 22.0) / 24.0 * 24.0
        for x, w in opens:
            centre = x + w / 2.0
            assert abs(centre - blind_px) > stack_half_px, (
                f"an opening is centred at {centre:.1f}, on the stack's own axis ({blind_px:.1f})")
        assert "BAY BLIND WHERE A STACK STANDS ON IT" in svg

    def test_the_generator_publishes_that_it_resolved_the_collision(self):
        """A measured zero, not an absence. The count is what `window-on-the-chimney-axis` tests,
        so any other producer — an ingested drawing, a hand-authored record — gets checked against
        the same rule instead of being trusted."""
        m = self._rec()["measurements"]
        assert m["count_of_openings_on_the_axis_of_a_chimney_stack"] == 0
        assert m["visible_chimney_count"] == 2

    def test_a_door_on_a_stack_axis_is_not_blinded_but_IS_reported(self):
        """The one bay the blinding rule deliberately does not touch, and the half of that
        decision that was never written down or tested.

        A door on a stack's axis is exactly as impossible as a window on one, but deleting an
        entrance is not a decision this generator may take on its own — the entrance is the
        composition's subject, and a facade silently missing its door is a worse drawing than one
        showing a conflict. So the bay is left alone AND the collision still reaches the
        measurement, so `window-on-the-chimney-axis` fires and a human decides. Refusing to
        resolve is not the same as failing to report."""
        import copy
        import json as _j
        e = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        plan = _j.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        base = e.build_elevation(plan)
        face = base["entrance_face"]
        door_cx = [c for c, k in zip(base["faces"][face]["centres_ft"],
                                     base["faces"][face]["kinds"]) if k == "door"][0]
        roof = copy.deepcopy(base["roof_record"])
        roof["chimneys"]["positions"] = [{"x_ft": door_cx, "y_ft": 0.0,
                                          "grade_to_ridge_ft": 39.66,
                                          "height_above_ridge_ft": 8.0,
                                          "total_height_grade_ft": 47.66}]
        rec = e.build_elevation(plan, roof=roof)
        f = rec["faces"][face]
        assert "blind" not in f["kinds"], "the entrance was silently deleted"
        assert f.get("blind_bay_centres_ft") is None
        assert rec["measurements"]["count_of_openings_on_the_axis_of_a_chimney_stack"] == 1, (
            "the collision was neither resolved nor reported — it just vanished")

    def test_the_fault_fires_on_a_record_that_states_the_collision(self):
        """Without this the zero above could be produced by a rule that can never return anything
        else, which is a measurement that proves nothing."""
        import json as _j
        core = modcache.load("core", os.path.join(ROOT, "mcp_server", "core.py"))
        f = _j.load(open(os.path.join(ROOT, "faults", "window-on-the-chimney-axis.json")))
        hit = core._eval_test(f["test"], {"visible_chimney_count": 2,
                                          "count_of_openings_on_the_axis_of_a_chimney_stack": 1})
        assert hit["status"] == "evaluated" and hit["passes"] is False
        none = core._eval_test(f["test"], {"visible_chimney_count": 0,
                                           "count_of_openings_on_the_axis_of_a_chimney_stack": 1})
        assert none["status"] == "not_applicable", "a house with no chimney has no stack axis"


class TestTheStacksAreDrawnWhereTheRecordPutsThem:
    """WP-5.13, second half. The chimney block carried a twelve-line comment saying the front
    elevation COULD NOT show the stacks, because `roof.py`'s long-face silhouette was flat at the
    eave and modelled no roof mass above the cornice. That was true when it was written and
    stopped being true earlier in the same package — `elevation_profile` returns the near roof
    plane on a long face now, because parallel projection fills the band from eave to ridge.
    Prose asserting what the code no longer does is the failure this corpus polices hardest, and
    it was sitting in the renderer's own comment.

    Underneath it were two invented constants of exactly the class OQ 52 swept out of the
    measurements: the stack was drawn 3 ft from the gable wall's front corner and based 2 ft
    below the ridge, while the record states `y_ft` (21.33 here — mid-depth, on the ridge line)
    and `total_height_grade_ft`. On the sheet the 3 ft put a brick bar in the sky at the
    top-left corner, touching no roof at all, on every gable elevation this corpus has ever
    drawn."""

    def _rects(self, svg, cls="ch"):
        import re
        out = []
        for m in re.finditer(r'<rect class="' + cls + r'[^"]*"([^>]*)/>', svg):
            a = dict(re.findall(r'(\w+)="([-\d.]+)"', m.group(1)))
            out.append({k: float(v) for k, v in a.items()})
        return out

    def _draw(self, tmp_path, face):
        import json as _j
        e = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        r = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
        plan = _j.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        rec = e.build_elevation(plan)
        out = str(tmp_path / f"{face}.svg")
        r.render_elevation(rec, out, face=face)
        return rec, open(out).read()

    def test_the_front_elevation_shows_both_end_stacks(self, tmp_path):
        """The kit calls the paired stacks "visible from a mile away and conclusive against New
        England", and the sheet everyone actually looks at drew neither."""
        rec, svg = self._draw(tmp_path, "S")
        stacks = self._rects(svg)
        assert len(stacks) == 2, "two gable-end stacks, one at each end of the ridge"
        xs = sorted(r["x"] for r in stacks)
        assert xs[1] - xs[0] > 1000, "they are at opposite ends of the front, not stacked together"

    def test_a_gable_end_draws_one_stack_at_the_position_the_record_states(self, tmp_path):
        rec, svg = self._draw(tmp_path, "E")
        stacks = self._rects(svg)
        assert len(stacks) == 1, "one stack per gable end; the record carries one at each"
        roof = rec["roof_record"]
        y_ft = roof["chimneys"]["positions"][0]["y_ft"]
        depth_ft = rec["footprint"]["depth_ft"]
        # the drawn centre, back through the same 24 px/ft and 46 px pad the sheet uses
        centre_px = stacks[0]["x"] + stacks[0]["width"] / 2.0
        assert abs((centre_px - 46.0) / 24.0 - y_ft) < 0.2, (
            f"the stack is drawn at {(centre_px-46)/24:.2f} ft along the gable end and the record "
            f"puts it at {y_ft} ft — the 3 ft constant is back")
        assert abs(y_ft - depth_ft / 2.0) < 0.5, "on this house that position is the ridge line"

    def test_no_stack_is_drawn_below_the_roof_it_comes_through(self, tmp_path):
        """Only the part above the roof is drawn, and that is a claim about EVIDENCE rather than
        about visibility: these stacks are exterior, so nothing hides the breast — but the only
        width this corpus states is the STACK's, and a chimney breast is several feet across. 47
        ft of 22 in brick asserts a chimney nobody measured. The sheet says so in its legend."""
        rec, svg = self._draw(tmp_path, "E")
        roof = rec["roof_record"]
        c = roof["chimneys"]["positions"][0]
        above_ft = c["total_height_grade_ft"] - c["grade_to_ridge_ft"]
        st = self._rects(svg)[0]
        assert abs(st["height"] / 24.0 - above_ft) < 0.05, (
            f"drawn {st['height']/24:.2f} ft of stack; {above_ft} ft clears the ridge")
        assert "BREAST BELOW" in svg.upper(), "the sheet must say what it is not drawing"


class TestDormersHaveThreeStatesAndTheThirdIsThePoint:
    """WP-5.13. Dormers were the last thing in this corpus that could not be stated at all.

    `build/roof.py::dormer_rhythm_check` read a field it had invented for itself
    (`declared_dormers`) because the plan schema had none, and `build/elevation.py` refused
    `dormer_count` outright — both for the same reason, stated in both files: an absent dormer and
    an UNSTATABLE one were indistinguishable, so any figure at all was a guess.

    `declared.dormer` separates them, and the separation is the whole feature:
        absent   the record does not say -> every dormer measurement withheld
        "none"   a house stated to have none -> dormer_count is a MEASURED zero
        {count}  a house that has them -> the full set

    The middle state is what the cape-central-chimney incident (OQ 59) was about: a refusal
    published as a zero, which then convicted a parti named for the very thing it had refused."""

    def _elev(self, declared):
        import copy
        import json as _j
        e = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        plan = _j.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
        plan = copy.deepcopy(plan)
        if declared == "DROP":
            plan["declared"].pop("dormer", None)
        else:
            plan["declared"]["dormer"] = declared
        return e.build_elevation(plan)

    def test_an_unstated_record_withholds_every_dormer_measurement(self):
        m = self._elev("DROP")["measurements"]
        for k in ("dormer_count", "sum_of_dormer_face_widths_in", "dormer_window_width_in"):
            assert k not in m, f"{k} was supplied for a plan that says nothing about dormers"

    def test_a_stated_none_is_a_measured_zero(self):
        m = self._elev("none")["measurements"]
        assert m["dormer_count"] == 0
        assert m["sum_of_dormer_face_widths_in"] == 0
        # ...but nothing PER-DORMER, because there is no dormer to measure
        assert "dormer_window_width_in" not in m
        assert "visible_cheek_width_in" not in m

    def test_both_shipped_plans_state_their_dormers(self):
        """They state none, and the reason is in each record's own note. A reference plan that
        stayed silent would leave the whole dormer layer untested on every run."""
        import json as _j
        for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
            plan = _j.load(open(os.path.join(ROOT, "plans", f"{pid}.json")))
            assert plan["declared"].get("dormer") == "none", pid

    def test_a_dormered_house_lands_inside_every_band_the_fault_corpus_states(self):
        """The fault corpus specifies a dormer completely, and the generator is built from it:
        window 0.75-1.0 of the sash below (`overscaled-dormer`), cheek at most 0.25 of the sash
        (`fat-cheek-dormer`), at least 12 in of roof in front and 18-36 preferred
        (`sunken-dormer`), faces together at most 0.4 of the building width (`dormer-wall`)."""
        elev = self._elev({"count": 3, "variant": "gabled"})
        d, m = elev["dormers"], elev["measurements"]
        below = m["window_width_directly_below_in"]
        assert 0.75 <= d["window_width_in"] / below <= 1.0
        assert 0.12 <= d["cheek_width_in"] / d["window_width_in"] <= 0.25
        # AND the rule that fault states in prose but does not encode in its test: "the finished
        # cheek width should not exceed the width of the window casing beside it". The kit band's
        # own midpoint breaks it on this house (6 in against a 4.21 in casing) and the drawing is
        # where that showed -- a strip of bare board outboard of the casing, two members where
        # the tradition wants one read as one.
        assert d["cheek_width_in"] <= d["casing_width_in"] + 1e-9
        assert 18.0 <= d["roof_run_in_front_in"] <= 36.0
        assert m["sum_of_dormer_face_widths_in"] / (elev["front"]["outside_width_in"]) <= 0.4
        assert d["count_parity_ok"] is True, "three is odd and the kit's parity rule says odd"

    def test_a_variant_the_style_forbids_is_refused_through_the_CASCADE(self):
        """`tidewater-georgian` binds the dormer slot EMPTY, exactly as it binds `shutter`, so the
        variants live on `georgian-colonial-american` and reach it only through the lineage.
        Checking the raw kit would let a shed dormer onto a Georgian front."""
        d = self._elev({"count": 3, "variant": "shed-dormer"})["dormers"]
        assert d.get("refused") is True
        assert "forbid" in d["note"].lower()

    def test_a_parity_breach_is_reported_and_not_refused(self):
        """An even count on a tradition that wants odd is a finding, not an invalid record. The
        corpus reports breaches; it does not refuse to draw the house."""
        d = self._elev({"count": 4, "variant": "gabled"})["dormers"]
        assert d["count"] == 4 and d.get("refused") is not True
        assert d["count_parity_ok"] is False

    # ---------------------------------------------------------------- the INK, not the record
    def _svg(self, tmp_path, declared, name="d.svg"):
        r = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
        out = str(tmp_path / name)
        r.render_elevation(self._elev(declared), out)
        return open(out).read()

    @staticmethod
    def _polys(svg, cls, n=None):
        """Polygons of a class, optionally only those with n vertices.

        The vertex filter is not decoration: the MAIN roof carries the same `rf w-prof` class as a
        dormer roof, and it is a four-point band while a dormer's is a three-point gable. Counting
        without it made "three dormer roofs" read four and, worse, made "a pediment shows no roof
        plane" fail on the roof of the house."""
        import re
        out = []
        for m in re.finditer(r'<polygon class="' + cls + r'[^"]*" points="([^"]+)"', svg):
            pts = [tuple(float(v) for v in p.split(",")) for p in m.group(1).split()]
            if n is None or len(pts) == n:
                out.append(pts)
        return out

    def test_dormers_are_drawn_on_the_roof_plane(self, tmp_path):
        import re
        svg = self._svg(tmp_path, {"count": 3, "variant": "gabled"})
        assert len(re.findall(r'class="pf w-prof" x=', svg)) >= 3, "three faces, one per dormer"
        assert len(self._polys(svg, "rf w-prof", n=3)) == 3, "three dormer roofs at the main pitch"
        # and a house that states none draws none
        n = self._svg(tmp_path, "none", "n.svg")
        assert not self._polys(n, "rf w-prof", n=3)

    def test_a_gabled_dormer_draws_no_cornice_return(self, tmp_path):
        """A cornice RETURN runs perpendicular to the picture plane, so orthographic projection
        gives it no width — the same reason the cheeks vanish. It was drawn for one revision as
        two stubs standing above the level cornice at the eave corners: a real member seen in
        perspective, on an orthographic sheet.

        REWRITTEN 28 Aug 2026. The first version scanned for `<rect class="pf w-fine">`, a class
        the gabled path never emits — `pf w-fine` is only ever a POLYGON (the pediment's tympanum).
        The loop body never executed and the only live assertion was `assert roofs`. Re-adding the
        stubs in the class the renderer actually uses passed it. This version asserts over EVERY
        element drawn above the cornice line inside the dormer's own x-span, whatever its class,
        and permits only the set the docstring names: the roof polygon and its shingle lines."""
        import re
        svg = self._svg(tmp_path, {"count": 3, "variant": "gabled"})
        roofs = self._polys(svg, "rf w-prof", n=3)
        assert len(roofs) == 3, f"expected three dormer roofs, got {len(roofs)}"
        # every drawn element, with its class and a y to test, whatever the tag
        drawn = []
        for m in re.finditer(r'<(rect|polygon|line)\s+class="([^"]*)"([^>]*)/?>', svg):
            tag, cls, attrs = m.group(1), m.group(2), m.group(3)
            if tag == "rect":
                a = dict(re.findall(r'(\w+)="([-\d.]+)"', attrs))
                if "x" in a and "y" in a:
                    drawn.append((cls, float(a["x"]), float(a["x"]) + float(a.get("width", 0)),
                                  float(a["y"])))
            elif tag == "polygon":
                pts = re.search(r'points="([^"]+)"', attrs)
                if pts:
                    p = [tuple(float(v) for v in q.split(",")) for q in pts.group(1).split()]
                    drawn.append((cls, min(x for x, _ in p), max(x for x, _ in p),
                                  min(y for _, y in p)))
            else:
                a = dict(re.findall(r'(\w+)="([-\d.]+)"', attrs))
                if {"x1", "x2", "y1"} <= set(a):
                    drawn.append((cls, min(float(a["x1"]), float(a["x2"])),
                                  max(float(a["x1"]), float(a["x2"])), float(a["y1"])))
        assert drawn, "nothing parsed out of the sheet — this test would pass vacuously"
        ALLOWED = ("rf w-prof", "shingle")
        for pts in roofs:
            base_y = max(p[1] for p in pts)          # SVG y grows down: the cornice line
            x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
            for cls, ex0, ex1, ey in drawn:
                if cls in ALLOWED:
                    continue
                inside = ex0 >= x0 - 1 and ex1 <= x1 + 1
                if inside and ey < base_y - 1:
                    raise AssertionError(
                        f"'{cls}' is drawn above the dormer's cornice line at y={ey:.1f} "
                        f"(cornice at {base_y:.1f}), inside its own x-span — a cornice return in "
                        "perspective on an orthographic sheet")

    def test_a_pedimented_dormers_tympanum_sits_inside_its_raking_cornice(self, tmp_path):
        """The two canonical variants differ here and nowhere else. A pediment is an outer gable
        bounded by a raking cornice with the tympanum inside it, and the rake must be the SAME
        assembly as the level cornice — `raking-cornice-that-does-not-match` is a fault in this
        corpus precisely because it usually is not.

        The measurement that matters is PERPENDICULAR. An inner triangle offset in y alone gives
        a rake thinner than the level cornice by the cosine of the pitch, and thinner the steeper
        the pediment; two stroked lines give a notch at the apex and two tails below the eaves.
        Both were drawn before this test existed, and both passed every test of the record."""
        import math
        svg = self._svg(tmp_path, {"count": 3, "variant": "pedimented"}, "p.svg")
        outer = self._polys(svg, "pf w-prof", n=3)
        inner = self._polys(svg, "pf w-fine", n=3)
        assert outer and inner, "a pedimented dormer draws an outer gable and a tympanum"
        assert not self._polys(svg, "rf w-prof", n=3), "a pediment closes the gable; no dormer roof plane shows"
        # the level cornice's own thickness, from the record
        d = self._elev({"count": 3, "variant": "pedimented"})["dormers"]
        for o, i in zip(outer, inner):
            oap = min(o, key=lambda p: p[1])
            iap = min(i, key=lambda p: p[1])
            assert iap[1] > oap[1], "the tympanum's apex must sit BELOW the raking cornice's"
            ox0, ox1 = min(p[0] for p in o), max(p[0] for p in o)
            ix0, ix1 = min(p[0] for p in i), max(p[0] for p in i)
            assert ix0 > ox0 and ix1 < ox1, "the tympanum must be inset at the eaves too"
            # perpendicular thickness of the left rake, measured as the distance from the inner
            # eave corner to the outer rake line
            rise, run = oap[1] - o[0][1], oap[0] - ox0
            ln = math.hypot(run, rise) or 1.0
            perp = abs((ix0 - ox0) * rise) / ln
            assert perp > 0.5, "the raking cornice has no thickness at all"
            # and it equals the LEVEL cornice's thickness, which is what "the same assembly" means
            lvl = None
            import re as _re
            for m in _re.finditer(r'<rect class="pf w-prof"[^>]*y="([-\d.]+)"[^>]*height="([-\d.]+)"', svg):
                h = float(m.group(2))
                if abs(float(m.group(1)) - o[0][1]) < 0.6:
                    lvl = h
                    break
            assert lvl is not None, "no level cornice found under the pediment"
            assert abs(perp - lvl) < 0.75, (
                f"the raking cornice is {perp:.2f} px thick and the level cornice {lvl:.2f} px — "
                "a rake that is not the level cornice is the fault this corpus names")

    def test_the_dormer_sash_carries_all_its_glazing_bars(self, tmp_path):
        """\"6/6\" is six lights in EACH sash, not six in the window. Reading the first number as
        the whole opening put half the glazing bars in.

        REWRITTEN 28 Aug 2026. The first version computed the expected bar count, discarded it,
        and asserted on `class="mt w-med"` — the MEETING RAIL, which `_window` emits exactly once
        per window whatever the light counts are. So it asserted \"twelve windows are drawn\",
        which was true before the fix and after it. Proven: forcing the dormer sashes to 1x1
        deleted all 18 dormer glazing bars and the test still passed. It now counts the bars
        themselves, differentially against a sheet with no dormers."""
        import re
        d = self._elev({"count": 3, "variant": "gabled"})["dormers"]
        per = int(str(d["sash_pattern"]).split("/")[0])
        assert d["lights_across"] * d["lights_high_per_sash"] == per, (
            f'{d["sash_pattern"]}: {d["lights_across"]}x{d["lights_high_per_sash"]} is not {per}')
        # interior muntins per dormer: (across-1) verticals x 2 sashes + (high-1) horizontals x 2
        want = (d["lights_across"] - 1) * 2 + (d["lights_high_per_sash"] - 1) * 2
        assert want == 6, f"6/6 in a 2x3 sash is six bars per dormer, not {want}"
        bars = lambda svg: len(re.findall(r'class="mt"', svg))
        none_svg = self._svg(tmp_path, "none", "nb.svg")
        three_svg = self._svg(tmp_path, {"count": 3, "variant": "gabled"}, "wb.svg")
        assert bars(three_svg) == bars(none_svg) + 3 * want, (
            f"{bars(three_svg)} glazing bars with three dormers against "
            f"{bars(none_svg)} without — expected {bars(none_svg) + 3 * want}")
        # and the meeting rail is still there, which is a DIFFERENT claim about the same sash
        assert len(re.findall(r'class="mt w-med"', three_svg)) == \
            len(re.findall(r'class="mt w-med"', none_svg)) + 3

    def test_a_variant_the_record_did_not_choose_is_not_chosen_for_it(self):
        """Picking the first canonical variant is dict order dressed as a decision. Tidewater makes
        BOTH `gabled` and `pedimented` canonical, so a record that names neither has not chosen;
        the drawing shows the plain gabled form and the sheet says the variant is undeclared."""
        d = self._elev({"count": 3})["dormers"]
        assert d["variant"] is None
        assert sorted(d["variant_undeclared_choices"]) == ["gabled", "pedimented"]
        d2 = self._elev({"count": 3, "variant": "pedimented"})["dormers"]
        assert d2["variant"] == "pedimented" and d2["variant_undeclared_choices"] is None

    def test_a_variant_the_cascade_delivered_says_where_it_came_from(self):
        """OQ 51 in the KIT layer. A style that binds a slot nothing gets its nearest ancestor's
        record in full, and the drawing must say so rather than asserting the result.

        REWRITTEN 27 Aug 2026 (WP-5.14). This test used to pin `spec-builder-colonial`, whose
        `colonial-revival` bound `dormer` as `open` and therefore resolved a thatched cottage's
        dormer from `english-cottage-vernacular` — with `boxed-dormer`, the only dormer such a
        house is built with, FORBIDDEN. That instance was fixed (OQ 87), so pinning it would now
        assert the bug. Twenty-nine other styles still inherit a dormer slot the same way; the
        mechanism is tested on one of them, chosen from the corpus at test time rather than named,
        so this cannot go stale the same way twice."""
        rk = modcache.load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
        g = rk.load_graph()
        inherited = []
        for nid, n in g["nodes"].items():
            if n.get("rank") not in ("style", "variant"):
                continue
            try:
                chain = rk.chain_for(g, nid)
                slots, _ = rk.resolve_slots(g, chain, rk.scope_for(g, nid))
            except Exception:
                continue
            d = slots.get("dormer") or {}
            if d.get("_source") and d["_source"] != nid and d.get("variants"):
                inherited.append((nid, d["_source"]))
        assert len(inherited) > 5, (
            f"only {len(inherited)} styles inherit a dormer slot — if the cascade has been made "
            "opt-in (OQ 51/81), this test has served its purpose and should be retired, not tuned")
        # and the style that raised it now owns its own
        chain = rk.chain_for(g, "colonial-revival")
        slots, _ = rk.resolve_slots(g, chain, rk.scope_for(g, "colonial-revival"))
        assert slots["dormer"]["_source"] == "colonial-revival"

    def test_an_inherited_variant_is_disclosed_on_the_sheet(self, tmp_path):
        """The disclosure itself, driven directly: where the variant came from a node that is not
        the style, the legend says which node and names OQ 51."""
        import copy
        import json as _j
        e = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        r = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
        plan = copy.deepcopy(_j.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"))))
        plan["declared"]["dormer"] = {"count": 3, "variant": "gabled"}
        rec = e.build_elevation(plan)
        # tidewater-georgian binds the slot empty; the spec lives on georgian-colonial-american
        assert rec["dormers"]["variant_source_node"] == "georgian-colonial-american"
        out = str(tmp_path / "inh.svg")
        r.render_elevation(rec, out)
        svg = open(out).read()
        assert "IS INHERITED FROM" in svg and "OQ 51" in svg

    def test_a_sash_pattern_the_kit_does_not_state_is_not_invented(self):
        """A glazing pattern nobody stated must not be asserted: `_dormer_lights` returns
        (None, None) and the sash is drawn as glass with the reason on the sheet."""
        e = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        assert e._dormer_lights(None) == (None, None)
        assert e._dormer_lights([]) == (None, None)
        assert e._dormer_lights(["not-a-pattern"]) == (None, None)
        # and a stated one is read as lights PER SASH, not as the whole opening
        assert e._dormer_lights(["6/6"]) == (2, 3)
        assert e._dormer_lights(["12/12"]) == (3, 4)

    def test_the_undeclared_sash_is_drawn_as_glass_and_the_sheet_says_so(self, tmp_path):
        """The END-TO-END half, restored 28 Aug 2026. The WP-5.14 rewrite moved this test off
        `colonial-revival` (correctly — that style states a pattern now) and in doing so retreated
        to a unit test of `_dormer_lights`, dropping the drawing assertion its own docstring
        promised. Neither the bare-glass sash nor the `DORMER SASH PATTERN UNDECLARED` legend was
        asserted anywhere in the suite, and **46 styles still resolve a dormer slot with no
        `sash_pattern`**, so the branch is live.

        The style is chosen from the corpus at test time rather than named, which is the lesson
        from the rewrite that broke it."""
        import copy
        import json as _j
        import re
        rk = modcache.load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
        e = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        r = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
        g = rk.load_graph()
        # Keep looking until one both lacks a sash pattern AND is inside this generator's own
        # scope gate — a skipped test guards nothing, and picking the alphabetically first
        # candidate landed on a style the elevation layer refuses to draw.
        base = _j.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json")))
        pick, rec = None, None
        for nid, node in sorted(g["nodes"].items()):
            if node.get("rank") not in ("style", "variant"):
                continue
            try:
                slots, _ = rk.resolve_slots(g, rk.chain_for(g, nid), rk.scope_for(g, nid))
            except Exception:
                continue
            d = slots.get("dormer") or {}
            if not d.get("variants") or (d.get("parameters") or {}).get("sash_pattern"):
                continue
            plan = copy.deepcopy(base)
            plan["style"] = nid
            plan["declared"]["dormer"] = {"count": 3}
            try:
                cand = e.build_elevation(plan)
            except Exception:
                continue
            if cand.get("applicable", True) and "error" not in cand and cand["dormers"].get("count"):
                pick, rec = nid, cand
                break
        assert pick, ("no style both lacks a dormer sash pattern and is drawable — if the corpus "
                      "has authored one everywhere, retire this test rather than tuning it")
        assert rec["dormers"]["sash_pattern"] is None
        assert rec["dormers"]["lights_across"] is None
        out = str(tmp_path / "bare.svg")
        r.render_elevation(rec, out)
        svg = open(out).read()
        assert "SASH PATTERN UNDECLARED" in svg, "the sheet drew bare glass and did not say why"

    def test_an_undeclared_variant_is_also_said_on_the_sheet(self, tmp_path):
        """Its neighbour `IS INHERITED FROM` is asserted and `DORMER VARIANT UNDECLARED` was not —
        an inconsistency rather than a decision. Tidewater makes two variants canonical, so a
        record naming neither has not chosen."""
        svg = self._svg(tmp_path, {"count": 3}, "undec.svg")
        assert "DORMER VARIANT UNDECLARED" in svg

    def test_dormers_the_roof_cannot_carry_are_declared_not_drawn_and_SAID(self, tmp_path):
        """A dormer needs a roof to stand on, and `spec-builder-colonial`'s roof record judges
        neither a pitch nor a ridge — so `elevation_profile` honestly returns a flat eave line
        with nothing invented above it. The renderer then skipped every dormer with no note while
        the measurements went on reporting three to the fault corpus: the critic judging three
        dormers on a sheet that drew none. Found by looking at the sheet, not by any test."""
        import copy
        import json as _j
        import re
        e = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))
        r = modcache.load("render_elevation", os.path.join(ROOT, "build", "render_elevation.py"))
        plan = copy.deepcopy(_j.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json"))))
        plan["declared"]["dormer"] = {"count": 3, "variant": "boxed-dormer"}
        rec = e.build_elevation(plan)
        assert rec["dormers"]["count"] == 3, "the record still states them"
        assert rec["dormers"]["placeable"] is False
        assert "not_drawn_reason" in rec["dormers"]
        out = str(tmp_path / "np.svg")
        r.render_elevation(rec, out)
        svg = open(out).read()
        assert not self._polys(svg, "rf w-prof", n=3), "a dormer roof drawn on a roof nobody judged"
        assert "DECLARED BUT NOT DRAWN" in svg, (
            "three dormers vanished from the sheet and it said nothing")

    def test_a_roof_that_can_carry_them_draws_them_and_says_nothing(self):
        """The other half: the disclosure must not become permanent furniture."""
        elev = self._elev({"count": 3, "variant": "gabled"})
        assert elev["dormers"]["placeable"] is True
        assert "not_drawn_reason" not in elev["dormers"]

    def test_the_dormer_cornice_is_the_house_cornice_at_the_houses_own_ratio(self):
        """The kit's rule for this slot: dormers "carry the same order as the house at reduced
        scale". `cornice-that-is-a-fascia` states the ratio the house's own cornice obeys — one
        twelfth to one fourteenth of the wall it crowns. The dormer's cornice is that same ratio
        over the dormer's own face, so the rule is used twice rather than invented once."""
        elev = self._elev({"count": 3, "variant": "gabled"})
        d, m, c = elev["dormers"], elev["measurements"], elev["eave_cornice"]
        house_ratio = c["cornice_height_in"] / m["wall_height_water_table_to_cornice_in"]
        assert 0.0714 <= house_ratio <= 0.0833, "the house's own cornice must obey the rule first"
        face_in = d["window_height_in"] + 2 * d["casing_width_in"]
        assert abs(d["cornice_height_in"] - house_ratio * face_in) < 0.01
        assert d["cornice_projection_in"] > 0
        assert "reduced scale" in (d["cornice_source"] or "")


class TestEveryPlateStatesTheFrameItWasDrawnIn:
    """WP-12.4. The Round lays a 2D plate over the 3D model at the same view, and it can only do
    that if the plate says what its own pixels mean in feet. `data-frame` is that statement.

    THE POINT OF PINNING IT HERE RATHER THAN IN THE VIEWER is that the attribute is a claim the
    RENDERER makes about its own arithmetic, and the failure it guards against is the attribute
    and the ink drifting apart — which no test on the JavaScript side can see, because the
    JavaScript believes the attribute. So the assertions below hold the attribute against a
    number the same file emits by a different path.

    A PLAN CARRIES ONE PLATE PER LEVEL, side by side in one SVG, each with its own origin. That
    is why `plates` is a list: measured on the Tidewater plan the two origins are 44.0 and
    1177.2 px, so a single root frame would have described the ground floor and mis-registered
    the upper one by eleven hundred pixels — the whole width of a plate.
    """

    KEYS = {"id", "proj", "px_per_ft", "origin_px", "at_origin_ft"}
    # `data-plate-top` is PRINTED at one decimal and the frame carries full precision,
    # because a viewer registering a plate on a model needs the number and a reader of the
    # plate needs a legible one. So they agree to within that printing and not to the bit —
    # rounding the frame to match would throw away 0.05 px of registration to make a test
    # tidier, which is the WP-12.2 residue lesson in a new place.
    PRINTED_TOL_PX = 0.05 + 1e-9

    def _frame(self, svg):
        m = re.search(r"data-frame='([^']*)'", svg)
        assert m, "the plate states no data-frame"
        import json as _json
        return _json.loads(m.group(1).replace("&apos;", "'"))

    def _plates(self, svg):
        f = self._frame(svg)
        assert isinstance(f.get("plates"), list) and f["plates"], "data-frame carries no plates"
        for p in f["plates"]:
            assert self.KEYS <= set(p), f"a plate frame is missing {self.KEYS - set(p)}"
            assert isinstance(p["px_per_ft"], (int, float)) and p["px_per_ft"] > 0
            assert len(p["origin_px"]) == 2 and len(p["at_origin_ft"]) == 2
        return f["plates"]

    def test_the_plan_states_one_frame_per_level_and_agrees_with_its_own_plate_top(self, tmp_path):
        """`data-plate-top` and `data-frame.origin_px[1]` are two independent emissions about one
        edge — the plate's top. They must agree exactly, and if the origin hoist ever drifts they
        stop agreeing, which is the only cheap way to catch that from outside the file."""
        rp = modcache.load("render_plan", f"{ROOT}/build/render_plan.py")
        g = modcache.load("geometry", f"{ROOT}/build/geometry.py")
        plan = json.load(open(f"{ROOT}/plans/tidewater-georgian-careful.json"))
        placed = g.solve(plan, engine="heuristic")
        out = str(tmp_path / "plan.svg")
        rp.render(placed, out)
        svg = open(out).read()
        plates = self._plates(svg)
        tops = re.findall(r'data-plate="([^"]*)" data-plate-top="([^"]*)"', svg)
        assert len(tops) == len(plates) >= 2, (
            f"{len(plates)} frames against {len(tops)} plates — a level is drawn with no frame")
        by_id = {p["id"]: p for p in plates}
        for pid, top in tops:
            assert pid in by_id, f"the plate {pid!r} is drawn and has no frame"
            assert abs(by_id[pid]["origin_px"][1] - float(top)) <= self.PRINTED_TOL_PX, (
                f"{pid}: data-frame says the plate starts at {by_id[pid]['origin_px'][1]} and "
                f"data-plate-top says {top} — the attribute has drifted from the ink")
        # The levels stand side by side, so their origins must DIFFER on x. A frame that gave
        # them the same origin would lay every plate on the first one and look plausible.
        xs = [p["origin_px"][0] for p in plates]
        assert len(set(xs)) == len(xs), f"two plates claim one origin: {xs}"

    def test_the_frame_follows_the_plate_when_a_lot_pushes_it_down(self, tmp_path):
        """DRIVEN, and it has to be: NO PLAN IN THIS CORPUS STATES A LOT (0 of 16, swept), so
        `render_plan`'s whole site block — the setbacks and the four `extra_*` terms — is
        unreachable from the shipped records, and `oy` equals `top` on every plate this tree
        draws. A mutation replacing the frame's `oy` with `top` is therefore INVISIBLE on the
        corpus: measured, it left this class green.

        That is WP-10.1's lesson (choose a fixture that straddles the branch) meeting WP-8.11's
        (a guard that runs only where the bug cannot occur is not a guard). So the lot is stated
        by hand, and the premise is asserted below, so the day a plan grows one the fixture stops
        being the only route rather than quietly becoming redundant."""
        rp = modcache.load("render_plan", f"{ROOT}/build/render_plan.py")
        g = modcache.load("geometry", f"{ROOT}/build/geometry.py")
        plan = json.load(open(f"{ROOT}/plans/tidewater-georgian-careful.json"))
        placed = g.solve(plan, engine="heuristic")

        flat = str(tmp_path / "flat.svg")
        rp.render(placed, flat)
        base = self._plates(open(flat).read())[0]["origin_px"][1]

        # a lot deeper than the house, so `extra_top` is a real number rather than a zero
        placed = json.loads(json.dumps(placed))
        placed["site"] = {"lot_width_ft": 140.0, "lot_depth_ft": 120.0,
                          "setback_front_ft": 20.0, "setback_side_ft": 30.0}
        out = str(tmp_path / "lot.svg")
        rp.render(placed, out)
        svg = open(out).read()
        plates = self._plates(svg)
        assert plates[0]["origin_px"][1] > base + 1.0, (
            f"the lot must push the plate down the sheet: {base} -> {plates[0]['origin_px'][1]}; "
            "if it did not, this fixture no longer drives the branch it exists for")
        tops = re.findall(r'data-plate="([^"]*)" data-plate-top="([^"]*)"', svg)
        by_id = {p["id"]: p for p in plates}
        for pid, top in tops:
            assert abs(by_id[pid]["origin_px"][1] - float(top)) <= self.PRINTED_TOL_PX, (
                f"{pid}: with a lot stated, data-frame says {by_id[pid]['origin_px'][1]} and the "
                f"plate says {top} — the frame is reading the sheet margin, not the plate")

    def test_no_shipped_plan_states_a_lot_so_the_case_above_must_stay_driven(self):
        """The premise of the fixture above, asserted rather than assumed. If this ever fails, a
        plan has grown a lot and the driven case is no longer the only route — read it again."""
        import glob
        withlot = []
        for f in sorted(glob.glob(f"{ROOT}/plans/**/*.json", recursive=True)):
            r = json.load(open(f))
            site, ctx = r.get("site") or {}, r.get("context") or {}
            if (site.get("lot_width_ft") or ctx.get("lot_width_ft")) and \
               (site.get("lot_depth_ft") or ctx.get("lot_depth_ft")):
                withlot.append(os.path.basename(f))
        assert withlot == [], f"a plan now states a lot ({withlot}) — see the driven test above"

    def test_the_scale_is_the_scale_the_caller_asked_for(self, tmp_path):
        """DRIVEN at a non-default scale, because `px_per_ft` transcribed as the module's default
        would be right on every plate this corpus ships and wrong for anyone who passes one."""
        rp = modcache.load("render_plan", f"{ROOT}/build/render_plan.py")
        g = modcache.load("geometry", f"{ROOT}/build/geometry.py")
        plan = json.load(open(f"{ROOT}/plans/tidewater-georgian-careful.json"))
        placed = g.solve(plan, engine="heuristic")
        assert rp.PX_PER_FT != 9.0, "pick a scale the renderer does not already default to"
        out = str(tmp_path / "plan9.svg")
        rp.render(placed, out, scale=9.0)
        for p in self._plates(open(out).read()):
            assert p["px_per_ft"] == 9.0, f"{p['id']} states {p['px_per_ft']} at a 9.0 scale"

    def test_the_elevation_the_roof_and_the_section_each_state_theirs(self, tmp_path):
        """One shape across four renderers. The elevation's frame is also the one the Round reads
        most, because four of its six named views are elevations."""
        g = modcache.load("geometry", f"{ROOT}/build/geometry.py")
        st = modcache.load("structure", f"{ROOT}/build/structure.py")
        rf_m = modcache.load("roof", f"{ROOT}/build/roof.py")
        el_m = modcache.load("elevation", f"{ROOT}/build/elevation.py")
        re_r = modcache.load("render_elevation", f"{ROOT}/build/render_elevation.py")
        rs_r = modcache.load("render_section", f"{ROOT}/build/render_section.py")
        rr_r = modcache.load("render_roof", f"{ROOT}/build/render_roof.py")
        plan = json.load(open(f"{ROOT}/plans/tidewater-georgian-careful.json"))
        placed = g.solve(plan, engine="heuristic")
        sec = st.build_section(placed, None, geometry_result=placed)
        rf = rf_m.build_roof(placed, None, section=sec)
        ev = el_m.build_elevation(placed, None, section=sec, roof=rf)
        if "error" in ev:
            pytest.skip(f"COULD NOT EVALUATE: this plan builds no elevation ({ev['error']})")

        # every face, because render_elevation has taken a `face` since WP-3.2 and three of the
        # four were never looked at until WP-12.0
        for face in ("S", "N", "E", "W"):
            out = str(tmp_path / f"e{face}.svg")
            re_r.render_elevation(ev, out, face=face)
            ps = self._plates(open(out).read())
            assert len(ps) == 1 and ps[0]["proj"] == "elevation"
            assert ps[0]["id"] == face and ps[0]["face"] == face, (
                f"the {face} elevation's frame names {ps[0]['id']!r}")
            assert ps[0]["at_origin_ft"][0] == 0.0, "a face is measured from its own left edge"
            assert ps[0]["at_origin_ft"][1] > 0, "and its origin is the top of the drawn height"

        out = str(tmp_path / "roof.svg")
        rr_r.render_roof(rf, out)
        ps = self._plates(open(out).read())
        assert len(ps) == 1 and ps[0]["proj"] == "roof"

        out = str(tmp_path / "sec.svg")
        rs_r.render_section(sec, out)
        assert self._plates(open(out).read())[0]["proj"] == "section"

        # The bearing diagram is a plan-shaped drawing in the CLEAR frame rather than the outside
        # one, and `proj` is the only thing that tells a reader which — so it is pinned.
        out = str(tmp_path / "bear.svg")
        rs_r.render_bearing_diagram(sec, out)
        bp = self._plates(open(out).read())
        assert bp and all(p["proj"] == "bearing" for p in bp)
        assert len(bp) == len(sec["levels"]), "one frame per level, as the plan states"
