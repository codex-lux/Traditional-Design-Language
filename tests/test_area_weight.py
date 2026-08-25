"""OQ 40 -- `area_weight` was read as a boolean and never as a share.

`instantiate()` nudged a room 10% if it carried a weight AT ALL and then reached the target with
one global factor, so the number itself decided nothing. A parti's weights read as a considered
distribution and were not one -- tuning the courtyard corredor in the package before this had to
be done by measuring the output, because nothing consumed the numbers.

Ruled: a room WITH a weight takes that share of the brief's target, clamped to its own catalogue
band. Partial coverage is allowed and is the normal case -- only the ten partis WP-4.5 authored
carry weights at all, and their sums run from 0.35 to 1.13.
"""
import glob
import json
import math
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def compose_mod():
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import compose
    return compose


def brief(style, target, **kw):
    b = {"id": "t", "name": "t", "style": style, "target_area_sf": target,
         "bedrooms": 3, "bathrooms": 2.0,
         "context": {"climate_zone": "3A", "lot_width_ft": 160, "entrance_faces": "S",
                     "jurisdiction": "IRC model text, advisory", "budget_tier": "custom"},
         "household": "t"}
    b.update(kw)
    return b


def sized(pid, style, target):
    c = compose_mod()
    plan, log, parti = c.instantiate(pid, brief(style, target))
    rooms = {r["id"]: r for lv in plan["levels"] for r in lv["rooms"]}
    return c, plan, log, parti, rooms


def band(c, rtype):
    return (c.C["rooms"].get(rtype, {}).get("dimensions", {}).get("area_sf") or [40, 900])


# ---------------------------------------------------------------- the share is real


def test_a_weighted_room_gets_its_share_of_the_target():
    """0.18 of a 3,000 sf brief is 540 sf, and it used to be whatever one global factor left."""
    c, plan, log, parti, rooms = sized("courtyard-and-portal", "spanish-colonial-revival", 3000)
    weights = {r["id"]: r.get("area_weight") for r in parti["rooms"] if r.get("area_weight")}
    assert weights, "this parti is the one that carries weights"
    checked = 0
    for rid, w in weights.items():
        if rid not in rooms: continue
        lo, hi = band(c, rooms[rid]["type"])
        want = min(max(w * 3000, lo), hi)
        got = rooms[rid]["width_ft"] * rooms[rid]["length_ft"]
        assert abs(got - want) / want < 0.06, (rid, w, want, got)
        checked += 1
    assert checked >= 8, checked


def test_the_share_scales_with_the_brief():
    """The test that fails if the field goes back to being a boolean: double the brief and a
    weighted room that is not against its band doubles with it."""
    c1, _p, _l, _pa, small = sized("courtyard-and-portal", "spanish-colonial-revival", 2000)
    c2, _p, _l, _pa, big = sized("courtyard-and-portal", "spanish-colonial-revival", 3000)
    lo, hi = band(c1, small["study"]["type"])
    a = small["study"]["width_ft"] * small["study"]["length_ft"]
    b = big["study"]["width_ft"] * big["study"]["length_ft"]
    assert lo < a < hi and lo < b < hi, "pick a room that is not against its band in either run"
    assert abs((b / a) - 1.5) < 0.08, (a, b)


def test_a_weight_is_not_renegotiated_by_the_global_factor():
    """A real share is not a starting suggestion. The weighted rooms are frozen before the
    scaling loop runs, which is the whole of what this ruling changes."""
    src = open(os.path.join(ROOT, "build", "compose.py")).read()
    i = src.index("OQ 40, ruled 24 Aug 2026")
    j = src.index("for _ in range(4):", i)
    assert "frozen.add(r[\"id\"])" in src[i:j]


# ---------------------------------------------------------------- partial coverage


def test_a_parti_with_no_weights_behaves_exactly_as_before():
    """Eleven of twenty-one partis state no weights at all, and this ruling must not move them."""
    c, plan, log, parti, rooms = sized("centre-passage-single-pile", "georgian-colonial-american", 2300)
    assert not any(r.get("area_weight") for r in parti["rooms"])
    heated = sum(r["width_ft"] * r["length_ft"] for r in rooms.values()
                 if c.C["rooms"].get(r["type"], {}).get("function_class") != "outdoor")
    assert abs(heated - 2300) / 2300 < 0.02, heated


@pytest.mark.parametrize("pid,style", [
    ("dogtrot-open-passage", "dogtrot-vernacular"),
    ("single-cell-hall", "log-vernacular-american"),
    ("tower-villa", "italian-villa-vernacular"),
])
def test_a_partly_weighted_parti_still_reaches_a_target_inside_its_own_range(pid, style):
    """The unweighted rooms split whatever is left. Measured at the midpoint of each parti's own
    `area_range_sf`, because a brief outside that range missing is the diagram telling the truth
    rather than the mechanism failing."""
    d = json.load(open(os.path.join(ROOT, "partis", "%s.json" % pid)))
    lo, hi = d["area_range_sf"]
    target = round((lo + hi) / 2)
    c, plan, log, parti, rooms = sized(pid, style, target)
    heated = sum(r["width_ft"] * r["length_ft"] for r in rooms.values()
                 if c.C["rooms"].get(r["type"], {}).get("function_class") != "outdoor")
    assert abs(heated - target) / target < 0.12, (pid, target, heated)


# ---------------------------------------------------------------- when it cannot be honoured


def test_a_weight_its_own_band_cannot_honour_is_reported_not_split_quietly():
    """A weight the room's catalogue band cannot honour is the diagram and the brief
    disagreeing, and saying which is the composer's job. The area miss that follows is then an
    explained number instead of a mysterious one."""
    c, plan, log, parti, rooms = sized("courtyard-and-portal", "spanish-colonial-revival", 5400)
    j = [l for l in log if l.startswith("JUDGMENT") and "area weights" in l]
    assert len(j) == 1, log
    assert "Sala wants" in j[0] and "band gives" in j[0]
    assert "it grows by having more of them" in j[0]


def test_a_void_is_weighted_against_the_brief_and_not_against_the_block():
    """The court is 0.18 of the house the brief asked for. That the house also has a court is
    what makes the block bigger than the brief (OQ 33); sizing the court against the block would
    be circular."""
    c, plan, log, parti, rooms = sized("courtyard-and-portal", "spanish-colonial-revival", 3000)
    court = rooms["court"]
    lo, hi = band(c, "courtyard")
    want = min(max(0.18 * 3000, lo), hi)
    assert abs(court["width_ft"] * court["length_ft"] - want) / want < 0.06


def test_every_authored_weight_is_between_zero_and_one():
    """A share outside 0-1 is not a share. Nothing enforced this while the field was a boolean."""
    for p in sorted(glob.glob(os.path.join(ROOT, "partis", "*.json"))):
        for r in json.load(open(p))["rooms"]:
            w = r.get("area_weight")
            if w is None: continue
            assert 0.0 < w < 1.0, (p, r["id"], w)
