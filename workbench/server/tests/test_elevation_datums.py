"""The second audit of Phase 17: the datum overlay's upper floor exists only on a house with one.

`build/elevation.py` falls back to the ground storey for `upper_storey_id` on a one-storey house, so
reading that id drew an upper floor on good-03 (one storey) 14.28 ft above grade. The elevation's own
`storey_count` decides it now, and both kinds of house are held here on real elevations."""
import pytest

pytest.importorskip("fastapi")


def _elev(name):
    import json
    import os
    from workbench.server import corpus
    plan = json.load(open(os.path.join(corpus.ROOT, "plans", "reference", name), encoding="utf-8"))
    return corpus.core._mod("elevation", os.path.join(corpus.ROOT, "build", "elevation.py")).build_elevation(plan)


@pytest.mark.parametrize("name,upper", [("good-03-parlor-drawing-room-house.json", False)])
def test_an_upper_floor_datum_only_where_the_elevation_counts_two_storeys(name, upper):
    from workbench.server import corpus
    elev = _elev(name)
    assert elev.get("upper_storey_id"), "the premise: the id is truthy on a one-storey house"
    ids = [d["id"] for d in corpus.elevation_datums(elev)]
    assert ("upper-floor" in ids) is upper, ids
    assert "grade" in ids, "grade is the plate's own datum and is always stated"


def test_a_two_storey_elevation_states_its_upper_floor():
    from workbench.server import corpus
    elev = {"storey_count": 2, "ground_grade_to_floor_in": 24.0, "ground_storey_height_in": 120.0,
            "upper_storey_id": "upper"}
    ids = {d["id"]: d["v_ft"] for d in corpus.elevation_datums(elev)}
    assert ids["upper-floor"] == pytest.approx(12.0)
    one = dict(elev, storey_count=1)
    assert "upper-floor" not in [d["id"] for d in corpus.elevation_datums(one)]
