"""What is DRAWN, not what was modelled — the layer WP-5.7 left unguarded.

WP-5.7 replaced a set of hand-tuned Beziers with real constructions and asserted them thoroughly:
convexity, tangency at a cyma's join, scale invariance, the datum rule. Every one of those tests
passes on the model. None of them looks at the path the renderer actually emits, and an
adversarial audit of that package found six construction and serialiser bugs that ship green
through all 34 checks, 970 tests, the selftest AND the browser walk — the headline being that
`svg_path()` emitted an inverted sweep flag, so every arc in the corpus was drawn as its own
mirror image about its chord.

That is the same disease as the `TestSegTo` block WP-5.7 deleted, one layer out. TestSegTo pinned
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
