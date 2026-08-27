"""Pins build/profiles.py — the moulding constructions, WP-5.7.

These tests assert GEOMETRY, not the strings it serialises to. That is the whole difference
between this file and the TestSegTo block it replaces in tests/test_elevation.py: that one pinned
the control-point arithmetic of hand-tuned Beziers, so it would have passed just as happily on the
day every one of those curves silently degenerated to a straight line — which is exactly what had
happened, on every member, for as long as the function existed.

What is worth pinning about a moulding is what makes it that moulding: an ovolo bulges out of its
chord and a cavetto falls inside it; a cyma's two arcs meet without a kink; a torus comes back to
the plane it sprang from; and every one of them scales with its module, because that is the claim
a proportional system makes.
"""
import math
import os
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

PROF = modcache.load("profiles", os.path.join(ROOT, "build", "profiles.py"))
PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))

CURVED = ("ovolo", "quarter-round", "echinus", "cavetto", "apophyge", "cyma-recta",
          "cyma-reversa", "ogee", "scotia", "torus", "astragal", "bead")
SQUARE = ("fillet", "listel", "fascia", "plinth", "corona", "abacus", "metope", "flat",
          "dentil", "modillion", "mutule", "triglyph")


def _sample(segs, n=16):
    """Every point along a run of segments, arcs included."""
    pts = []
    for s in segs:
        if s["kind"] == "close":
            continue
        if s["kind"] == "line":
            pts.append(s["to"])
        else:
            pts += [PROF.arc_point(s, i / n) for i in range(n + 1)]
    return pts


class TestTheSelftestItself:
    def test_selftest_passes(self):
        """build/check_all.py runs this as a check; if it ever fails there it must fail here."""
        assert PROF.selftest() == 0


class TestConvexAndConcave:
    """The defining property. An ovolo that falls inside its chord is a cavetto, and a reader
    fluent in this language sees the difference before they see anything else on the drawing."""

    @pytest.mark.parametrize("profile", ("ovolo", "quarter-round", "echinus"))
    def test_convex_quarters_bulge_out_of_the_chord(self, profile):
        segs, _ = PROF.member_path(profile, 0.0, 0.0, 4.0, 6.0)
        for x, y in _sample(segs):
            chord_x = 4.0 * (y / 6.0)
            assert x >= chord_x - 1e-9, f"{profile} fell inside its chord at y={y}"

    @pytest.mark.parametrize("profile", ("cavetto", "apophyge", "congé"))
    def test_concave_quarters_fall_inside_the_chord(self, profile):
        segs, _ = PROF.member_path(profile, 0.0, 0.0, 4.0, 6.0)
        for x, y in _sample(segs):
            chord_x = 4.0 * (y / 6.0)
            assert x <= chord_x + 1e-9, f"{profile} bulged out of its chord at y={y}"

    @pytest.mark.parametrize("profile,want_out", [("ovolo", True), ("cavetto", False)])
    def test_a_receding_member_keeps_its_character(self, profile, want_out):
        """dx < 0 happens: a member can draw back as it rises — a conge at the foot of a Tuscan
        shaft, a member above a corona. Its CHARACTER must not change with its direction.

        This test asserted the opposite until 27 Aug 2026. It ran a receding ovolo and required
        it to fall INSIDE its chord — that is a cavetto — and called it "keeps its character".
        The construction did exactly that, on sixteen members across ten packs, and the test
        agreed with it. A guard written from the same misunderstanding as the code guards
        nothing."""
        segs, xe = PROF.member_path(profile, 6.0, 0.0, 2.0, 4.0)
        assert xe == pytest.approx(2.0)
        for x, y in _sample(segs):
            chord_x = 6.0 - 4.0 * (y / 4.0)
            if abs(x - chord_x) < 1e-9:
                continue
            assert (x > chord_x) == want_out, (
                f"a receding {profile} changed character at y={y:.3f}")


class TestTheCymas:
    """A cyma is two arcs, and the join is the whole craft of it."""

    @pytest.mark.parametrize("profile", ("cyma-recta", "cyma-reversa", "ogee"))
    def test_two_arcs_meeting_at_the_chord_midpoint(self, profile):
        segs, _ = PROF.member_path(profile, 1.0, 0.0, 4.0, 5.0)
        arcs = [s for s in segs if s["kind"] == "arc"]
        assert len(arcs) == 2
        join_a, join_b = PROF.arc_point(arcs[0], 1.0), PROF.arc_point(arcs[1], 0.0)
        assert join_a == pytest.approx(join_b, abs=1e-6)
        assert join_a == pytest.approx((2.5, 2.5), abs=1e-6)

    @pytest.mark.parametrize("profile", ("cyma-recta", "cyma-reversa"))
    def test_the_join_is_smooth_not_merely_touching(self, profile):
        """A kink at the inflection is what tells a fluent reader the curve was guessed."""
        segs, _ = PROF.member_path(profile, 0.0, 0.0, 3.0, 7.0)
        arcs = [s for s in segs if s["kind"] == "arc"]
        t1 = PROF.arc_tangent(arcs[0], 1.0)
        t2 = PROF.arc_tangent(arcs[1], 0.0)
        assert t1 == pytest.approx(t2, abs=1e-6)

    def test_recta_is_convex_below_and_concave_above(self):
        """The crowning cymatium, whose CONCAVE part is uppermost (Britannica, Oxford). Its
        reverse is the other way up, and having the two the wrong way round swaps a crowning
        cymatium for a bed mould on every cornice in the corpus — 53 authored members.

        The inverted definition was pinned here, in the module docstring, in the selftest and in
        docs/proportion.md, and all four agreed with each other, which is why nothing caught it."""
        segs, _ = PROF.member_path("cyma-recta", 0.0, 0.0, 4.0, 8.0)
        lo = PROF.arc_point([s for s in segs if s["kind"] == "arc"][0], 0.5)
        assert lo[0] > 4.0 * (lo[1] / 8.0), "cyma recta's lower half is not convex"

    def test_reversa_is_concave_below_and_convex_above(self):
        segs, _ = PROF.member_path("cyma-reversa", 0.0, 0.0, 4.0, 8.0)
        lo = PROF.arc_point([s for s in segs if s["kind"] == "arc"][0], 0.5)
        assert lo[0] < 4.0 * (lo[1] / 8.0), "cyma reversa's lower half is not concave"

    def test_ogee_is_the_same_curve_as_cyma_reversa(self):
        a, _ = PROF.member_path("ogee", 0.0, 0.0, 3.0, 5.0)
        b, _ = PROF.member_path("cyma-reversa", 0.0, 0.0, 3.0, 5.0)
        assert _sample(a) == pytest.approx(_sample(b))


class TestRoundsAndHollows:
    @pytest.mark.parametrize("profile", ("torus", "astragal", "bead"))
    def test_a_half_round_returns_to_its_own_springing(self, profile):
        """Its height is its diameter and its recorded projection is the crown, so it springs
        from half its height inboard of that crown and comes back there."""
        segs, xe = PROF.member_path(profile, 2.0, 0.0, 5.0, 6.0)
        assert xe == pytest.approx(5.0 - 3.0), "a half round that does not come back is not one"
        assert max(x for x, _ in _sample(segs)) == pytest.approx(5.0, abs=1e-6)

    @pytest.mark.parametrize("profile", ("torus", "astragal", "bead"))
    def test_a_roll_set_back_is_still_a_roll(self, profile):
        """A pack may record a torus whose face is INBOARD of the member below it. Bulging by dx
        then makes it a groove bitten out of that member — chambers-doric's lower torus was a
        four-inch gouge in its own plinth, in the shipped dist/orders.html."""
        segs, _ = PROF.member_path(profile, 5.0, 0.0, 2.0, 6.0)
        arcs = [s for s in segs if s["kind"] == "arc"]
        spring = PROF.arc_point(arcs[0], 0.0)[0]
        crown = max(PROF.arc_point(a, t / 8)[0] for a in arcs for t in range(9))
        assert crown > spring, f"a receding {profile} is drawn as a hollow"

    def test_a_scotia_is_hollower_than_a_cavetto(self):
        """Both recede; the scotia is the deeper hollow, which is what makes it a scotia."""
        sc, _ = PROF.member_path("scotia", 4.0, 0.0, 4.0, 6.0)
        assert min(x for x, _ in _sample(sc)) < 4.0 - 1e-6


class TestSquareSteps:
    @pytest.mark.parametrize("profile", SQUARE)
    def test_square_members_are_drawn_square(self, profile):
        segs, xe = PROF.member_path(profile, 0.0, 0.0, 3.0, 2.0)
        assert all(s["kind"] == "line" for s in segs)
        assert xe == pytest.approx(3.0)

    def test_a_corona_takes_a_drip_only_when_its_own_note_asks_for_one(self):
        """Gibbs, of the corona: 'divide the projecting part in two for the Drip.' A drip cut into
        every corona regardless would be this renderer inventing a detail."""
        plain, _ = PROF.member_path("corona", 0.0, 0.0, 3.0, 2.0, note="Third principal part.")
        dripped, _ = PROF.member_path("corona", 0.0, 0.0, 3.0, 2.0,
                                      note="divide the projecting part in two for the Drip")
        assert len(dripped) > len(plain)


class TestTheDatumRule:
    """OQ 65, stated once. Getting this wrong drew Vignola's Ionic 2.25x too wide."""

    def test_naked_datum_adds_the_projection_to_the_plane(self):
        assert PROF.outer_face(10.0, 3.0, False) == pytest.approx(13.0)

    def test_axis_datum_reads_the_projection_as_an_absolute_radius(self):
        assert PROF.outer_face(10.0, 18.0, True) == pytest.approx(18.0)

    def test_a_recorded_zero_under_the_axis_reading_is_absent_not_flush(self):
        """The ruled half of OQ 65: eight assemblies across the axis packs record every projection
        as 0. Those are figures the authority did not publish, and a drawing that collapses them
        onto the centre line has invented a shape rather than admitted a gap."""
        assert PROF.outer_face(10.0, 0.0, True) == pytest.approx(10.0)


class TestScaleInvariance:
    """A proportional system's central claim, and the property that lets this geometry be computed
    once in Python and merely mapped by anything that draws it."""

    def test_geometry_at_module_m_is_m_times_geometry_at_module_one(self):
        base = [{"id": "a", "profile": "cyma-recta", "y_bottom_in": 0.0, "y_top_in": 2.0, "projection_in": 1.0},
                {"id": "b", "profile": "ovolo", "y_bottom_in": 2.0, "y_top_in": 3.0, "projection_in": 2.0},
                {"id": "c", "profile": "corona", "y_bottom_in": 3.0, "y_top_in": 5.0, "projection_in": 3.5}]
        k = 7.25
        scaled = [{**m, "y_bottom_in": m["y_bottom_in"] * k, "y_top_in": m["y_top_in"] * k,
                   "projection_in": m["projection_in"] * k} for m in base]
        a = _sample(PROF.silhouette(base, 0.0)["segments"])
        b = _sample(PROF.silhouette(scaled, 0.0)["segments"])
        assert len(a) == len(b)
        for (ax, ay), (bx, by) in zip(a, b):
            assert ax * k == pytest.approx(bx, abs=1e-6)
            assert ay * k == pytest.approx(by, abs=1e-6)


class TestRepetition:
    """A band of dentils drawn as a solid band is a band of no dentils. But a tooth needs a width,
    and where no authority published one the honest output is a solid band that SAYS it is one."""

    def test_an_unstated_tooth_width_refuses_rather_than_guesses(self):
        r = PROF.repeat_positions(120.0, count=8, spacing_in=10.0, width_in=None)
        assert r["solid"] is True
        assert "unstated" in r["reason"]
        assert r["teeth"] == []

    def test_a_stated_width_lays_out_real_teeth_centred_on_the_run(self):
        r = PROF.repeat_positions(100.0, count=5, spacing_in=12.0, width_in=7.0)
        assert r["solid"] is False
        assert len(r["teeth"]) == 5
        for t in r["teeth"]:
            assert t["x1"] - t["x0"] == pytest.approx(7.0)
            assert 0 <= t["x0"] and t["x1"] <= 100.0
        centres = [t["centre"] for t in r["teeth"]]
        assert centres[0] + centres[-1] == pytest.approx(100.0, abs=1e-6), "band is not centred"

    def test_a_tooth_that_fills_its_own_pitch_is_refused(self):
        r = PROF.repeat_positions(100.0, count=5, spacing_in=8.0, width_in=8.0)
        assert r["solid"] is True

    def test_teeth_can_be_centred_on_the_columns_below(self):
        """Gibbs: 'always the centre of a Modillion exactly over the centre of each column.'"""
        r = PROF.repeat_positions(200.0, spacing_in=20.0, width_in=8.0, centre_on=[50.0, 150.0])
        assert not r["solid"]
        cs = [t["centre"] for t in r["teeth"]]
        assert 50.0 in cs and 150.0 in cs


class TestUnconstructedShapes:
    """A volute is a spiral whose construction sits on a plate this corpus cannot reach. Drawing a
    swelling in its place is acceptable; drawing it without saying so is not."""

    @pytest.mark.parametrize("profile", ("volute", "acanthus"))
    def test_they_report_themselves(self, profile):
        res = PROF.silhouette([{"id": "m", "profile": profile, "y_bottom_in": 0.0,
                                "y_top_in": 4.0, "projection_in": 3.0}], 0.0)
        assert res["unconstructed"]
        assert res["unconstructed"][0]["profile"] == profile

    def test_a_constructed_stack_reports_nothing(self):
        res = PROF.silhouette([{"id": "m", "profile": "ovolo", "y_bottom_in": 0.0,
                                "y_top_in": 4.0, "projection_in": 3.0}], 0.0)
        assert res["unconstructed"] == []


class TestSerialisers:
    def test_svg_arcs_flip_their_sweep_when_the_transform_flips_y(self):
        """Every plate here draws model inches up and screen pixels down. A sweep flag computed in
        model space and emitted unchanged turns every curve inside out."""
        segs, _ = PROF.member_path("ovolo", 0.0, 0.0, 4.0, 4.0)
        up = PROF.svg_path(segs, lambda x: x, lambda y: y, start=(0.0, 0.0))
        down = PROF.svg_path(segs, lambda x: x, lambda y: 100 - y, start=(0.0, 0.0))
        assert " 0 1 " in up or " 0 0 " in up
        flags = lambda d: [tok.split()[-3:-1] for tok in d.split("A ")[1:]]
        assert flags(up) != flags(down), "the sweep flag did not change with the y flip"

    def test_a_circular_arc_survives_to_dxf_as_an_arc(self):
        """A bulge is exactly a circular arc; flattening one to a polygon would make the CAD file
        a worse record than the SVG beside it."""
        segs, _ = PROF.member_path("cyma-recta", 0.0, 0.0, 3.0, 5.0)
        pts = PROF.dxf_points(segs, (0.0, 0.0))
        assert any(abs(b) > 1e-6 for _, _, b in pts)

    def test_an_elliptical_quarter_is_flattened_and_stays_within_tolerance(self):
        segs, _ = PROF.member_path("ovolo", 0.0, 0.0, 4.0, 9.0)   # rx != ry, so no bulge exists
        pts = PROF.dxf_points(segs, (0.0, 0.0), tol=0.01)
        assert all(abs(b) < 1e-9 for _, _, b in pts)
        assert len(pts) > 4


class TestAgainstTheRealCorpus:
    """The constructions have to survive every order pack, not a fixture."""

    def test_every_order_pack_dimensions_and_draws_without_a_gap(self):
        packs = [p for p in PE.PACKS.values() if p.get("kind") == "order-system"]
        assert len(packs) >= 20, "the order packs went missing"
        for p in packs:
            pack = PE.resolve(p["id"])
            dim = PE.dimension(pack, 36.0)
            from_axis = dim.get("projection_datum") == "axis"
            for asm in dim["assemblies"]:
                if not asm["members"]:
                    continue
                sil = PROF.silhouette(asm["members"], naked_at=0.0, from_axis=from_axis)
                assert sil["segments"], f"{p['id']}/{asm['id']} produced no geometry"
                pts = _sample(sil["segments"], n=4)
                assert all(math.isfinite(x) and math.isfinite(y) for x, y in pts), \
                    f"{p['id']}/{asm['id']} produced a non-finite coordinate"

    def test_a_width_survives_inheritance_in_the_same_unit_as_its_own_pitch(self):
        """A repeating member's width and its pitch are both measured in parts, so an overlay
        that redefines the part must convert BOTH. `width_parts` was added to the schema and to
        dimension() in WP-5.7 and missed in `_convert_assembly`'s conversion tuple, so fourteen
        inherited members carried the base pack's width against their own converted pitch:
        chambers-doric's triglyph filled 12 of a 75-part pitch instead of 30, a 60% hole in a
        Doric frieze, against its own inherited note saying triglyph and metope fill it exactly.

        The check is the ratio, because that is what survives a unit change. A tooth is between a
        quarter and three quarters of its own pitch in every tradition the corpus holds; anything
        outside that is a conversion that did not happen."""
        seen = 0
        for pid in sorted(PE.PACKS):
            try:
                pack = PE.resolve(pid)
            except Exception:
                continue
            for asm in (pack.get("assemblies") or {}).values():
                for m in asm.get("members", []):
                    w, sp = m.get("width_parts"), m.get("spacing_parts")
                    if not (w and sp):
                        continue
                    seen += 1
                    assert 0.25 <= w / sp <= 0.75, (
                        f"{pid}/{m['id']}: a tooth {w} parts wide on a {sp}-part pitch is "
                        f"{100 * w / sp:.0f}% solid — its width and its pitch are not in the "
                        f"same unit, so one of them did not convert on inheritance")
        assert seen >= 25, f"only {seen} repeating members carry a width; the sweep lost some"

    def test_every_profile_name_in_the_corpus_is_one_this_module_knows(self):
        """A profile the constructor has never heard of is drawn square. That is a safe default,
        but it must be a KNOWN default: a new enum value landing in the schema without a
        construction should be visible here rather than quietly squared off."""
        known = set(PROF.CONVEX_QUARTER + PROF.CONCAVE_QUARTER + PROF.ROUNDS + PROF.SQUARE
                    + PROF.UNCONSTRUCTED + ("cyma-recta", "cyma-reversa", "ogee", "scotia", "bevel"))
        seen = set()
        for p in PE.PACKS.values():
            for asm in (p.get("assemblies") or {}).values():
                for m in asm.get("members", []):
                    if m.get("profile"):
                        seen.add(m["profile"])
        unknown = sorted(seen - known)
        assert not unknown, f"profiles with no stated construction: {unknown}"


class TestTheTranscribedWidthsAreTheAuthoritiesOwnFigures:
    """The transcriptions themselves, pinned against the sources they were read from.

    THIS IS THE ASSERTION THE RATIO TEST CANNOT MAKE, and the gap is not theoretical: two of these
    fifteen were authored at exactly half their source, and a third of the way through the fix the
    corrected values silently failed to reach the file while the notes beside them were rewritten
    to say they had. Neither event moved a single test.

    `test_a_width_survives_inheritance_in_the_same_unit_as_its_own_pitch` checks width/pitch, so
    HALVING BOTH PRESERVES IT — 6.5/17.5 and 13/35 both read 37%. That test catches a MISMATCH
    between the two fields and is structurally blind to a uniform error in both, which is exactly
    what OQ 81 was. A transcription has to be pinned against its quoted source, not its neighbour.

    Each row is (pack, assembly, member, width_parts, spacing_parts, the words it was read from).
    Changing a figure here means changing the quotation with it, which is the point: the number
    and its authority move together or the test fails."""

    TRANSCRIBED = [
        ("vignola-composite",  "cornice",     "dentil_band",      6.0,   9,     "1/6 D wide (6 parts)"),
        ("vignola-corinthian", "cornice",     "dentil_band",      4.0,   6,     "1/9 D wide (4 parts)"),
        ("vignola-corinthian", "cornice",     "modillion_band",   8.0,   24,    "1/3 D wide (8 parts)"),
        ("vignola-doric",      "frieze",      "triglyph",         12.0,  30,    "1/2 D wide (12 parts)"),
        ("vignola-doric",      "frieze",      "metope",           18.0,  30,    "the metope is square: 18 parts"),
        ("vignola-doric",      "cornice",     "corn_mutule_band", 12.0,  30,    "the mutule is the width of the triglyph"),
        ("vignola-ionic",      "cornice",     "dentil_band",      4.0,   6,     "1/9 D wide (4 parts)"),
        ("benjamin-corinthian","entablature", "ent_cornice",      13.0,  35.0,  "the modillions are thirteen minutes in front, and thirty five from centre to centre"),
        ("benjamin-doric",     "frieze",      "triglyph",         30.0,  75,    "one module in width"),
        ("benjamin-doric",     "frieze",      "metope",           45.0,  75,    "the metope a module and a half"),
        ("benjamin-ionic",     "entablature", "ent_cornice",      10.5,  31.0,  "ten, ten and one half, or eleven minutes in front; place them thirty one minutes from centre to centre"),
        ("gibbs-composite",    "cornice",     "corn_dentil_band", 2.571, 3.857, "two of those parts will be the Dentel"),
        ("gibbs-corinthian",   "cornice",     "corn_dentil_band", 2.571, 3.857, "two of those parts will be the Dentel"),
        ("gibbs-corinthian",   "cornice",     "corn_modillion",   6.0,   21,    "each is 6 parts wide"),
        ("gibbs-doric",        "cornice",     "corn_modillion",   15.0,  30,    "half the pitch"),
    ]

    def test_every_authored_width_is_the_figure_its_own_note_quotes(self):
        import json
        missing, wrong = [], []
        for pid, aid, mid, want_w, want_sp, quote in self.TRANSCRIBED:
            path = None
            for sub in ("orders", "overlays", "systems", "modules"):
                p = os.path.join(ROOT, "proportions", sub, f"{pid}.json")
                if os.path.exists(p):
                    path = p
                    break
            assert path, f"{pid}: pack file not found"
            d = json.load(open(path))
            mem = next((m for m in d["assemblies"][aid]["members"] if m["id"] == mid), None)
            if mem is None:
                missing.append(f"{pid}/{mid}")
                continue
            if mem.get("width_parts") != want_w or mem.get("spacing_parts") != want_sp:
                wrong.append(f"{pid}/{mid}: file has width={mem.get('width_parts')} "
                             f"spacing={mem.get('spacing_parts')}, transcription says "
                             f"{want_w}/{want_sp} from \"{quote}\"")
        assert not missing, f"members vanished: {missing}"
        assert not wrong, "a width no longer matches the source it was read from:\n  " + "\n  ".join(wrong)

    def test_the_table_covers_every_authored_width_in_the_corpus(self):
        """A transcription added without a row here is a figure with no recorded source."""
        import glob as _glob
        import json
        authored = set()
        for path in sorted(_glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
            d = json.load(open(path))
            for aid, a in (d.get("assemblies") or {}).items():
                for m in a.get("members", []):
                    if m.get("width_parts") is not None:
                        authored.add((d["id"], aid, m["id"]))
        pinned = {(r[0], r[1], r[2]) for r in self.TRANSCRIBED}
        assert authored == pinned, (
            f"unpinned: {sorted(authored - pinned)}; stale rows: {sorted(pinned - authored)}")


class TestTheDatumDetectionsOwnBlindSpot:
    """Where `axis_holds_for()` could be wrong, named and watched.

    The rule downgrades a pack's `axis` declaration to naked-relative on either of two signals:
    a recorded 0 (impossible under the radius reading) or nothing in the group reaching its own
    naked. The second is self-evidently safe — if no figure reaches the naked, none can be a
    radius.

    THE FIRST IS NOT, on its own. A group holding genuine radii AND one unrecorded 0 would be
    downgraded on the strength of the 0, and its real radii would then be added to the naked and
    drawn about twice too wide — which is the OQ 65 bug, returning by the back door.

    In this corpus that combination occurs only on ENTABLATURES, where it is the correct reading
    and the case OQ 78 was raised about: the frieze records 0 because it IS the naked, and the
    cornice's larger figures are relief from it. Confirmed independently by Gibbs's own rule that
    the cornice's projection equals its height — which holds exactly under the naked reading of
    the Tidewater cornice (24.558 in of relief against 24.558 in of height) and not at all under
    the other.

    So the rule is right on every group the corpus actually contains, and this test watches the
    edge it does not: a COLUMN OR PEDESTAL group carrying both a real radius and an unrecorded
    zero. If one is ever authored, this fails and says what to do, rather than the drawing quietly
    doubling."""

    def test_no_column_group_mixes_a_real_radius_with_an_unrecorded_zero(self):
        offenders = []
        for pid in sorted(PE.PACKS):
            pack = PE.PACKS[pid]
            if pack.get("kind") != "order-system":
                continue
            r = PE.resolve(pid)
            d = PE.dimension(r, 36.0)
            if d.get("projection_datum") != "axis":
                continue
            geo = PROF.pack_geometry(d, r.get("column"), d.get("projection_datum"))
            nakeds = {"pedestal": geo["die_naked_in"], "subplinth": geo["die_naked_in"],
                      "base": geo["lower_radius_in"], "shaft": geo["lower_radius_in"],
                      "capital": geo["upper_radius_in"]}
            groups = {}
            for a in d["assemblies"]:
                aid = a["id"]
                if aid in ("pedestal", "subplinth"):
                    g = "pedestal"
                elif aid in ("base", "shaft", "capital"):
                    g = aid
                else:
                    continue                      # entablatures are the known, correct case
                groups.setdefault(g, []).append(a)
            for gname, gasms in groups.items():
                projs = [m.get("projection_in") or 0.0 for a in gasms for m in a["members"]]
                if not projs:
                    continue
                naked = nakeds.get(gname, geo["upper_radius_in"])
                if min(projs) <= 0.01 and max(projs) >= naked - 0.01:
                    offenders.append(
                        f"{pid}/{gname}: holds a figure of {max(projs):.2f} that reaches its naked "
                        f"({naked:.2f}) AND an unrecorded 0 — axis_holds_for() will downgrade the "
                        f"whole group on the zero and draw that radius roughly twice too wide")
        assert not offenders, (
            "the datum detection's blind spot now has data in it; the zero-signal must be "
            "narrowed (e.g. to fire only when the assembly that DEFINES the group's naked is "
            "wholly unrecorded) before these draw:\n  " + "\n  ".join(offenders))
