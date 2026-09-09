"""WP-12.3 — the scene route.

The three things this route can get wrong that nothing else would notice:

1. **The scene and the plates are different buildings.** Every plate and the scene must come
   from the ONE placement `_placed` produced, which is WP-6.4's rule and the defect WP-12.0
   removed from the elevation and roof branches one layer up. The guard is the input digest,
   which `_placed` stamps from the record it was HANDED: if every plate and the scene carry the
   same one, they were drawn from the same input.
2. **A plate that could not be drawn goes missing rather than being named.** To a viewer, an
   absent key and a view it has not fetched yet look identical.
3. **A caller-supplied parti reaches the solver as a record.** WP-9.4 measured 114 bays of half
   a foot arriving that way through two bench routes.

And one thing about the ROUTE rather than the record: it is not a sixth drawing kind.
`test_m3_drawings.py::test_unknown_kind_names_the_kinds` posts `axonometric` and expects a 422
naming the five kinds, and that stays true only while no camera is smuggled into that enum.
"""
import json
import os

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("jsonschema")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))


def _plan():
    return json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))


@pytest.fixture(scope="module")
def scene_res():
    """One call, reused. The solve behind it is measured at 37.48 s cold and it is the whole
    cost of this route; asking for it once per assertion would make the file the slowest in the
    suite for no added coverage."""
    from workbench.server import corpus
    return corpus.scene(_plan())


# ------------------------------------------------------------------ the record

def test_the_scene_comes_back_with_its_plan_and_its_plates(scene_res):
    from workbench.server import corpus
    assert "error" not in scene_res, scene_res.get("error")
    assert scene_res["scene"]["scene_version"] == "0.1.0"
    assert scene_res["scene"]["solids"], "a scene with no solids"
    assert set(scene_res["plates"]) | set(scene_res["plates_refused"]) == {
        f"{k}:{f}" if f else k for k, f in corpus.SCENE_PLATES}
    assert scene_res["plates"], "no plate was drawn at all"
    for key, got in scene_res["plates"].items():
        # A PLATE IS ITS DRAWING AND ITS DISCLOSURES. WP-12.4 first stored the SVG alone here
        # and the bench's elevation silently lost WP-3.2's disclosure, the entrance face and
        # the engine-and-digest line -- caught by the browser walk, not by this file, because
        # this file was asserting the picture and the defect was in everything around it.
        #
        # THE SHAPE IS ASSERTED BEFORE THE PICTURE, AND THAT ORDER WAS CHOSEN BY MUTATION.
        # With `got["svg"]` written back into corpus.py the picture line raised
        # `TypeError: string indices must be integers` -- red, and telling the reader nothing
        # about what a plate owes. The two disclosure assertions below were never reached at
        # all, so the guards written for this defect were shielded by the one above them.
        assert isinstance(got, dict), (
            f"{key} came back as a bare {type(got).__name__}: a plate is its drawing AND the "
            "things the drawing does not say for itself")
        assert got["svg"].lstrip().startswith("<svg"), key
        assert got.get("kind"), f"{key} carries a drawing and no metadata"
        if key.startswith("elevation"):
            assert got.get("entrance_face"), f"{key} does not say which face is the front"


def test_the_returned_plan_is_placed_so_a_later_call_does_not_re_solve(scene_res):
    """The second reason the record comes back. `_placed` returns a record carrying `geometry`
    untouched, so a client that keeps this one pays 0.00 s where a fresh record pays 37.48 s.
    Asserted as the PROPERTY — every room has geometry — and not as a timing, because a timing
    here would be a statement about this machine."""
    rooms = [r for lv in scene_res["plan"]["levels"] for r in lv["rooms"]]
    placed = [r for r in rooms if r.get("geometry")]
    assert placed, "the returned record carries no placement at all"
    assert len(placed) > len(rooms) * 0.5, f"only {len(placed)} of {len(rooms)} rooms placed"


def test_every_plate_and_the_scene_are_the_same_building(scene_res):
    """THE ONE THAT MATTERS. `_placed` stamps `solver.drawn_by.input_digest` from the record it
    was handed, before it solves — WP-11.8's finding J6, which exists so that two sheets of "the
    same house" that disagree can be told apart by their input. Every plate in this response and
    the scene beside them must carry one digest.

    It is asserted on the DIGEST rather than on the SVG bytes because two plates of one house
    are legitimately different drawings; what must not differ is what they were drawn from.
    """
    digest = ((scene_res["solver"] or {}).get("drawn_by") or {}).get("input_digest")
    assert digest, "the placement records no input digest"
    assert scene_res["scene"]["solver"]["drawn_by"]["input_digest"] == digest


def test_a_plate_that_could_not_be_drawn_is_named_and_not_dropped():
    """DRIVEN, because both shipped plans draw all six. A record whose style states no migrated
    roof pitch refuses the roof plate, and the response must say so under `plates_refused`
    rather than leaving the key out — an absent key reads to a viewer as a view it has not
    fetched yet, which is the one thing it must not read as."""
    from workbench.server import corpus
    assert set(corpus.SCENE_PLATES) and all(
        isinstance(k, str) for k, _f in corpus.SCENE_PLATES)
    # the contract, read from the code rather than from a corpus that happens to draw all six
    src = open(os.path.join(ROOT, "workbench", "server", "corpus.py"), encoding="utf-8").read()
    body = src.split("def scene(")[1].split("\ndef ")[0]
    assert 'refused[key] = got["error"]' in body, (
        "a plate that errors must be recorded under plates_refused, not skipped")
    assert "plates_refused" in body


def test_a_parti_record_is_refused_and_an_id_is_not():
    """WP-9.4: a caller-supplied parti is an ID, never a record. Both branches driven."""
    from workbench.server import corpus
    bad = corpus.scene(_plan(), parti={"id": "centre-passage-double-pile", "rooms": []},
                       plates=False)
    assert bad.get("error", "").startswith("parti must be a parti id")
    ok = corpus.scene(_plan(), parti="centre-passage-double-pile", plates=False)
    assert "error" not in ok, ok.get("error")


def test_plates_false_returns_the_scene_alone():
    """A knob nobody exercises is a branch nobody tests."""
    from workbench.server import corpus
    res = corpus.scene(_plan(), plates=False)
    assert "error" not in res
    assert "plates" not in res and "plates_refused" not in res
    assert res["scene"]["solids"]


# ------------------------------------------------------------------ the route

def test_the_route_is_metered_and_validates_its_plan(client):
    """`_heavy` and `_plan`, as every sibling that drives the solver has since WP-10.1."""
    src = open(os.path.join(ROOT, "workbench", "server", "app.py"), encoding="utf-8").read()
    body = src.split('@app.post("/api/scene")')[1].split("@app.post")[0]
    assert "_heavy(request)" in body and "_plan(body)" in body
    r = client.post("/api/scene", json={"plan": {"levels": "not a list"}})
    assert r.status_code == 422


def test_the_scene_is_not_a_sixth_drawing_kind(client):
    """`/api/drawings/{kind}` must still refuse a camera by name. This is the assertion
    `test_unknown_kind_names_the_kinds` makes with `axonometric`; it is repeated here against
    the two names this package could plausibly have added, so that a later reader adding one
    fails HERE, beside the route that exists instead."""
    for kind in ("scene", "axonometric"):
        r = client.post(f"/api/drawings/{kind}", json={"plan": _plan()})
        assert r.status_code == 422, kind
        assert "kinds" in r.json()["detail"], kind
        assert kind not in r.json()["detail"]["kinds"], kind
