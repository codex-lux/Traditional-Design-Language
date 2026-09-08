"""WP-11.3 — the centre line, the bay the door stands in, and the mirror about it.

`build/plan_check.py` said it in its own comment: *"There is no axis vocabulary anywhere in this
codebase."* `docs/reports/tidewater-layout-diagnosis-2026-09-04.md` B1 is what that cost — the
sheet's "centre passage" was the whole WEST bay of a six-bay house, and the one executable rule
the corpus has about a passage (its width as a share of the facade, 0.18 to 0.27) PASSED it at
11/60 = 0.183, because that rule measures the passage's WIDTH and not its PLACE.

Every test here asserts BOTH directions where there are two, and the third state where there is
one: a house with an even bay count has no middle bay, and that is could-not-evaluate with a
finding rather than a pass.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

AX = modcache.load("axis", os.path.join(ROOT, "build", "axis.py"))
GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))


def _placed(name="tidewater-georgian-careful", engine="heuristic"):
    plan = json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))
    return GEO.solve(plan, None, 250, engine=engine)


def _fixture(bays=5, bay=10.0, passage_x=20.0, passage_w=10.0, door_x=25.0):
    """A minimal placed record with a through-passage and a front door, so a test can move one
    number and watch one verdict."""
    W = bays * bay
    return {
        "id": "fx", "name": "Fixture", "style": "tidewater-georgian",
        "massing": "four-over-four",
        "context": {"entrance_faces": "S"},
        "footprint": {"width_ft": W, "depth_ft": 40.0, "bays": bays, "bay_module_ft": bay},
        "levels": [{"id": "ground", "index": 0, "rooms": [
            {"id": "passage", "type": "centre-passage", "name": "Centre Passage",
             "geometry": {"x_ft": passage_x, "y_ft": 0.0, "width_ft": passage_w,
                          "depth_ft": 40.0, "area_sf": passage_w * 40},
             "doors": [{"to": "exterior", "wall": "S", "position_ft": door_x, "width_ft": 3.5},
                       {"to": "exterior", "wall": "N", "position_ft": door_x, "width_ft": 3.5}]},
        ]}],
        "geometry_report": {"solver": {"engine": "heuristic"}},
    }


# ------------------------------------------------------------------ the spine
class TestTheCentreLine:
    def test_a_passage_on_the_centre_line_is_on_centre(self):
        sp = AX.spine(_fixture(passage_x=20.0, passage_w=10.0))   # centre 25 of a 50 ft front
        assert sp["verdict"] == "on-centre" and sp["off_ft"] == 0.0

    def test_a_passage_in_an_end_bay_is_off_centre(self):
        """The sheet's own case: the passage was the whole west bay and every rule the corpus
        could execute about it passed."""
        sp = AX.spine(_fixture(passage_x=0.0, passage_w=10.0))
        assert sp["verdict"] == "off-centre" and sp["off_ft"] == 20.0

    def test_the_tolerance_is_half_a_bay_and_admits_the_periods_own_off_centre_passages(self):
        """Westover's and Wilton's passages are *"slightly off-center"*, which every survey
        records as a deliberate asymmetry making one pair of rooms larger. Half a bay module
        admits that and refuses an end bay. EDITORIAL: no source states the figure, and it is
        marked so wherever it is reported."""
        near = AX.spine(_fixture(passage_x=24.0))       # 1 ft off a 5 ft tolerance
        far = AX.spine(_fixture(passage_x=14.0))        # 6 ft off
        assert near["verdict"] == "on-centre" and far["verdict"] == "off-centre"
        assert near["tol_ft"] == 5.0
        assert "editorial" in near["tol_basis"]

    def test_a_passage_reaching_one_end_only_is_unjudged(self):
        """A room that does not span the block has no through-axis to be off, and the question
        does not arise. It is not a pass: `verdict` says could-not-evaluate and says why."""
        p = _fixture()
        p["levels"][0]["rooms"][0]["doors"] = [
            {"to": "exterior", "wall": "S", "position_ft": 25.0, "width_ft": 3.5}]
        sp = AX.spine(p)
        assert sp["verdict"] == "could-not-evaluate" and "both ends" in sp["why"]

    def test_a_plan_with_no_footprint_is_unjudged(self):
        p = _fixture()
        p["footprint"] = {}
        assert AX.spine(p)["verdict"] == "could-not-evaluate"


# ------------------------------------------------------------------ the door's bay
class TestTheBayTheDoorStandsIn:
    def test_a_door_in_the_middle_bay(self):
        d = AX.door_bay(_fixture(bays=5, bay=10.0, door_x=25.0))
        assert d["verdict"] == "in-the-centre-bay" and d["bay"] == 2 and d["centre_bay"] == 2

    def test_a_door_in_an_end_bay(self):
        d = AX.door_bay(_fixture(bays=5, bay=10.0, door_x=5.0))
        assert d["verdict"] == "off-the-centre-bay" and d["bay"] == 0

    def test_an_even_bay_count_has_no_middle_bay_at_all(self):
        """THE STATE THIS FILE EXISTS FOR. Six bays cannot carry a centred door, so the
        question does not arise — and the reason it does not arise is that the placement made
        the answer impossible before the door was placed. Not a pass."""
        d = AX.door_bay(_fixture(bays=6, bay=10.0, door_x=30.0))
        assert d["verdict"] == "could-not-evaluate"
        assert "even count" in d["why"] and "no middle bay" in d["why"]

    def test_no_placed_front_door_is_unjudged(self):
        p = _fixture()
        p["levels"][0]["rooms"][0]["doors"] = [
            {"to": "exterior", "wall": "N", "position_ft": 25.0, "width_ft": 3.5}]
        assert AX.door_bay(p)["verdict"] == "could-not-evaluate"

    def test_the_bay_index_is_clamped_to_the_front(self):
        """A door at the very end of the last bay must not index past it."""
        p = _fixture(bays=5, bay=10.0)
        assert AX.bay_of(50.0, p) == 4
        assert AX.bay_of(0.0, p) == 0


# ------------------------------------------------------------------ the mirror
class TestTheMirror:
    def _with_front(self, xs, level=0):
        p = _fixture()
        p["levels"][0]["rooms"][0]["windows"] = [
            {"wall": "S", "count": 1, "positions_ft": [x], "width_ft": 3.0} for x in xs]
        p["levels"][0]["rooms"][0]["doors"] = [
            {"to": "exterior", "wall": "S", "position_ft": 25.0, "width_ft": 3.5},
            {"to": "exterior", "wall": "N", "position_ft": 25.0, "width_ft": 3.5}]
        return p

    def test_a_symmetrical_front_is_mirrored(self):
        m = AX.mirror(self._with_front([10.0, 40.0]))
        assert m["verdict"] == "mirrored" and m["unmatched"] == []

    def test_one_opening_without_a_partner_is_not(self):
        m = AX.mirror(self._with_front([10.0, 33.0]))
        assert m["verdict"] == "not-mirrored" and len(m["unmatched"]) == 2

    def test_a_front_with_nothing_placed_is_unjudged(self):
        p = _fixture()
        p["levels"][0]["rooms"][0]["doors"] = []
        assert AX.mirror(p)["verdict"] == "could-not-evaluate"

    def test_a_gable_entrance_front_is_refused_rather_than_guessed(self):
        """The mirror runs the other way on a house entered on its end, and this reader has
        not been shown to be right about that case. Refusing beats a plausible answer.

        THE REASON IS ASSERTED, NOT ONLY THE VERDICT, and a mutation is why. Deleting the
        gable guard left this test green: the reader then looked for openings on the E wall,
        found none, and returned could-not-evaluate for a completely different reason. A test
        that accepts the right answer for the wrong reason is a test that cannot fail when the
        reason goes away."""
        p = self._with_front([10.0, 40.0])
        p["context"]["entrance_faces"] = "E"
        m = AX.mirror(p)
        assert m["verdict"] == "could-not-evaluate"
        assert "gable end" in m["why"], m["why"]


# ------------------------------------------------------------------ vertical alignment
class TestTheVerticalAlignment:
    def _two_storeys(self, ground_xs, upper_xs):
        p = _fixture()
        p["levels"][0]["rooms"][0]["windows"] = [
            {"wall": "S", "count": 1, "positions_ft": [x], "width_ft": 3.0} for x in ground_xs]
        p["levels"].append({"id": "upper", "index": 1, "rooms": [
            {"id": "up", "type": "centre-passage", "name": "Upper Passage",
             "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 50, "depth_ft": 40, "area_sf": 2000},
             "windows": [{"wall": "S", "count": 1, "positions_ft": [x], "width_ft": 3.0}
                         for x in upper_xs]}]})
        return p

    def test_openings_over_openings_are_aligned(self):
        a = AX.alignment(self._two_storeys([10.0, 40.0], [10.0, 40.0]))
        assert a["verdict"] == "aligned" and a["unaligned"] == 0

    def test_an_upper_opening_over_nothing_is_not(self):
        a = AX.alignment(self._two_storeys([10.0, 40.0], [10.0, 22.0]))
        assert a["verdict"] == "not-aligned" and a["unaligned"] == 1

    def test_a_bare_ground_front_is_unjudged(self):
        p = self._two_storeys([], [10.0])
        p["levels"][0]["rooms"][0]["doors"] = []
        assert AX.alignment(p)["verdict"] == "could-not-evaluate"

    def test_a_single_storey_house_is_unjudged(self):
        assert AX.alignment(_fixture())["verdict"] == "could-not-evaluate"


# ------------------------------------------------------------------ the critic
class TestTheCriticReadsIt:
    """The findings, on the real shipped plan. These assert the CENSUS as well as the
    findings, because a check that cannot fire reads as a check that passed (WP-8.6) and three
    of these four deliberately decline to judge an incomplete front."""

    @pytest.fixture(scope="class")
    @classmethod
    def checked(cls):
        placed = _placed()
        return placed, PC.check(placed)

    def test_the_census_is_published(self, checked):
        _, c = checked
        ax = (c.get("drawn_summary") or {}).get("axis")
        assert ax and ax["wants_centre_bay"] is True
        assert ax["why"], "the census must say WHY this diagram wants a centre bay"
        for k in ("spine", "door", "mirror", "alignment"):
            assert k in ax

    def test_the_shipped_passage_is_on_centre_after_wp_11_2(self, checked):
        """It was the whole west bay of a six-bay house when the diagnosis was written. The
        odd bay count and the diagram's own module put it on the centre line."""
        _, c = checked
        assert (c["drawn_summary"]["axis"]["spine"]) == "on-centre"

    def test_the_door_is_named_when_it_misses_the_middle_bay(self, checked):
        _, c = checked
        kinds = [f.get("kind") for f in c["findings"]]
        if c["drawn_summary"]["axis"]["door"] == "off-the-centre-bay":
            assert "drawn-door-off-the-centre-bay" in kinds
        else:
            assert "drawn-door-off-the-centre-bay" not in kinds

    def test_symmetry_is_refused_on_an_incomplete_front_rather_than_convicted(self, checked):
        """A facade missing seven of its declared units is not the facade the record
        describes, and convicting it of asymmetry would charge the house twice for one cause:
        the undrawn windows are already their own disclosure. The refusal is a finding, so it
        cannot read as a pass."""
        _, c = checked
        ax = c["drawn_summary"]["axis"]
        if ax["mirror"] == "could-not-evaluate":
            f = next(f for f in c["findings"]
                     if f.get("kind") == "drawn-facade-symmetry-unjudged")
            assert f["severity"] == "info" and "not a pass" in f["statement"]

    def test_a_diagram_that_wants_no_centre_bay_is_not_judged_by_any_of_this(self):
        """`rooms/centre-passage.json` records the Charleston single house — entered sideways
        off a piazza — as a real exception. The block binds on the DIAGRAM's own claim to a
        centre bay, which is why it does not simply fire on every plan."""
        placed = _placed()
        placed["massing"] = "charleston-single"
        placed.pop("parti", None)
        c = PC.check(placed)
        ax = c["drawn_summary"]["axis"]
        assert ax["wants_centre_bay"] is False
        assert not any(f.get("kind", "").startswith("drawn-door-off") for f in c["findings"])
        assert not any(f.get("kind", "").startswith("drawn-passage-off") for f in c["findings"])
