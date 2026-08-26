"""Pins the parti catalogue and the coverage WP-4.5 closed.

Partis were the one catalogue nothing checked before WP-4.5: schema/parti.schema.json existed
and was referenced by no code, so a malformed file surfaced as a KeyError inside compose.py at
the moment a brief happened to reach it. build/check_partis.py now validates them, and this
file pins the two properties that matter behaviourally — that every buildable style with a
canonical massing has a diagram of its own, and that the composer prefers it.
"""
import glob
import json
import os

import pytest

from conftest import ROOT


def _partis():
    return [json.load(open(p)) for p in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json")))]


def _styles():
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = json.load(open(p))
        out[d["id"]] = d
    return out


class TestCoverage:
    """The number WP-4.5 exists to move. It went 39 -> 129 named, 90 -> 0 uncovered."""

    def test_every_buildable_style_with_a_canonical_massing_has_a_native_parti(self):
        styles = _styles()
        named = set()
        for p in _partis():
            named.update(p.get("styles") or [])
        uncovered = []
        for sid, d in styles.items():
            if d.get("rank") not in ("style", "variant"):
                continue
            canonical = {a["massing"] for a in (d.get("massing_affinities") or [])
                         if a.get("affinity") == "canonical"}
            if canonical and sid not in named:
                uncovered.append(sid)
        assert not uncovered, (
            f"{len(uncovered)} buildable style(s) have a canonical massing and no parti naming "
            f"them, so the composer can only serve them another style's diagram: "
            f"{sorted(uncovered)[:10]}")

    def test_a_parti_is_never_native_to_a_rank_that_has_no_kit(self):
        """A parti native to a family or a tradition is a category error: only styles and
        variants resolve to a kit, so only they can be composed for."""
        styles = _styles()
        for p in _partis():
            for s in (p.get("styles") or []):
                assert s in styles, f"{p['id']} names unknown style {s}"
                assert styles[s].get("rank") in ("style", "variant"), (
                    f"{p['id']} is native to {s}, which is a {styles[s].get('rank')}")


class TestReferentialIntegrity:
    """What build/check_partis.py enforces, pinned here so the checker cannot be quietly
    weakened without the suite noticing."""

    def test_every_room_type_and_grouping_resolves(self, corpus):
        for p in _partis():
            for r in p["rooms"]:
                assert r["type"] in corpus["rooms"], f"{p['id']}: unknown room type {r['type']}"
            for g in (p.get("groupings") or []):
                assert g in corpus["groupings"], f"{p['id']}: unknown grouping {g}"

    def test_every_door_lands_on_a_room_in_the_same_parti(self):
        for p in _partis():
            ids = {r["id"] for r in p["rooms"]}
            for r in p["rooms"]:
                for d in (r.get("doors") or []):
                    assert d == "exterior" or d in ids, (
                        f"{p['id']}: {r['id']} has a door to {d}, which is not a room here")

    def test_no_room_is_unreachable(self):
        """A room no door reaches would be placed by the composer and then reported unreachable
        by the validator, on every plan, forever."""
        for p in _partis():
            if len(p["rooms"]) < 2:
                continue
            reachable = set()
            for r in p["rooms"]:
                if r.get("doors"):
                    reachable.add(r["id"])
                    reachable |= {d for d in r["doors"] if d != "exterior"}
            for r in p["rooms"]:
                assert r["id"] in reachable, f"{p['id']}: {r['id']} has no door to or from anything"


class TestTheComposerPrefersTheNativeDiagram:
    """WP-4.5 raised compose.py's NATIVITY_W from 6 to 20 because at 6 it did not work: five
    serious findings outweighed being the right diagram, and a tidewater-georgian brief came
    back recommending an octagon."""

    # Each brief is sized to the diagram's own area_range_sf. A 3,000 sf brief is not a
    # Scandinavian log house, and asking for one would test the area gate rather than nativity.
    @pytest.mark.parametrize("style,expect_parti,area,beds", [
        ("spanish-colonial-revival", "courtyard-and-portal", 3200, 4),
        ("shingle-style", "living-hall-picturesque", 4200, 4),
        # tudor-revival's own canonical massing is massed-picturesque, not h-plan-manor,
        # so the living hall leading for it is the right answer; `tudor` is the H-plan style.
        ("tudor-revival", "living-hall-picturesque", 5200, 5),
        ("tudor", "great-hall-h-plan", 5200, 5),
        ("scandinavian-log-vernacular", "single-cell-hall", 700, 2),
        ("italianate-villa", "tower-villa", 3400, 4),
        ("shotgun-house", "shotgun-linear", 900, 2),
    ])
    def test_a_style_with_its_own_diagram_is_offered_it_first(self, compose_module,
                                                             style, expect_parti, area, beds):
        brief = {"id": "t", "name": "t", "style": style, "target_area_sf": area, "bedrooms": beds,
                 "site": {"lot_width_ft": 120, "setback_side_ft": 10}}
        picks = compose_module.pick_partis(brief, limit=3)
        assert picks[0]["parti"] == expect_parti, (
            f"{style} should lead with its own diagram, got {picks[0]['parti']}")

    def test_nativity_outweighs_a_handful_of_serious_findings_but_not_a_fatal(self, compose_module):
        """The calibration itself — and as of 26 Aug 2026 it lives somewhere else, which is
        the point of the second half of this test.

        NATIVITY_W still computes `demerits`, and `demerits` no longer ranks anything: the
        composer orders by the composite score, where being the right diagram is the FIDELITY
        AXIS's weight. A test that greps for `NATIVITY_W = 20` and stops was therefore pinning
        a vestige — it would have stayed green through any re-weighting of the thing that
        actually decides which plan a client is shown. Both are asserted now, and the
        behavioural claim is asserted as behaviour rather than as source text."""
        import inspect
        src = inspect.getsource(compose_module.compose)
        assert "NATIVITY_W = 20" in src
        assert 'pick["fit"] * NATIVITY_W' in src

        fidelity = next(w for n, w, _ in compose_module.SCORE_AXES if n == "fidelity")
        assert fidelity == 25, (
            "the fidelity axis is what ranks candidates now; NATIVITY_W only feeds the "
            "superseded demerit total. See docs/reports/candidate-score-composite.md for how "
            "25 was measured, and re-measure before moving it.")
        # never enough to carry a fatal: a fatal DISQUALIFIES, which no weight can offset
        assert fidelity < 100
