"""WP-14.24 (PRD tranche 2 §C.9, §0.3 default 6): the pack index's thumbnails, and the two keys
the page's class-A slider and its thumbnails read off the list route.

`GET /api/proportions` gains three keys per row: `drawing` (which plate the pack is drawn on),
`module_bound_to` (the building dimension its module IS, where it declares one) and `thumb` (its
first assembly at the wall datum, or null). Every expectation below is COMPUTED from the detail
route or the engine -- no count is written down -- because the list and the pack page answer the
same questions and must not answer them twice.

THE THUMBNAIL IS THE PLATE'S FIRST DRAWING, NOT A SECOND ONE. It is the first assembly
`/api/proportions/{pack}?members=true` serves, face for face, at the pack's own module. Only a pack
drawn at the wall datum has one: a stacked order is drawn on its column's axis, and its first
assembly at the wall datum measured NO WIDTH on 10 of the 25 stacked packs and would read the 14
`axis`-datum packs' radii as projections off a wall (the report's §II).

THE BUDGET IS MEASURED AND ASSERTED. The brief moves the thumbnails to their own route if they
grow the list by more than about 60 KB gzipped. Measured at the level `GZipExceptSSE` deploys (4):
the list is 20,709 bytes on the base and 29,360 with the thumbnails, 8,651 more. The guard
compresses the served list with and without its thumbnails, so it measures the thumbnails and
nothing else.
"""
import gzip
import json

import pytest

from workbench.server import corpus

core = corpus.core

BUDGET_GZ = 60 * 1024


def _body(obj):
    # exactly Starlette's JSONResponse.render
    return json.dumps(obj, ensure_ascii=False, allow_nan=False, indent=None,
                      separators=(",", ":")).encode("utf-8")


@pytest.fixture(scope="module")
def listed(client):
    r = client.get("/api/proportions")
    assert r.status_code == 200
    return r.json()["packs"]


@pytest.fixture(scope="module")
def detail(client, listed):
    out = {}
    for p in listed:
        r = client.get(f"/api/proportions/{p['id']}", params={"members": "true"})
        assert r.status_code == 200, p["id"]
        out[p["id"]] = r.json()
    return out


def test_the_list_says_which_plate_each_pack_is_drawn_on_as_the_pack_page_does(listed, detail):
    assert listed, "the premise: the list serves packs"
    for p in listed:
        assert p["drawing"] == detail[p["id"]]["drawing"], p["id"]
    kinds = {p["drawing"] for p in listed}
    assert {"stack", "assemblies", None} <= kinds, \
        f"the premise: all three states are in the corpus ({kinds})"


def test_the_list_says_which_building_dimension_a_module_is_as_the_pack_page_does(listed, detail):
    for p in listed:
        assert p["module_bound_to"] == detail[p["id"]].get("module_bound_to"), p["id"]
    assert any(p["module_bound_to"] for p in listed), "the premise: some pack binds its module"


def test_a_thumbnail_is_the_plates_first_assembly_face_for_face(listed, detail):
    drawn = [p for p in listed if p["thumb"]]
    assert drawn, "the premise: the index draws thumbnails"
    for p in drawn:
        first = detail[p["id"]]["assemblies"][0]
        t = p["thumb"]
        assert t["assembly"] == first["id"], p["id"]
        assert t["height_in"] == first["height_in"], p["id"]
        assert t["geometry"]["faces"] == first["geometry"]["faces"], \
            f"{p['id']}: the thumbnail is not the served first assembly"
        # the axis rides where the pack declares one, and only there
        assert t.get("axis") == first.get("axis"), p["id"]
        # trimmed to what a thumbnail reads: no members, no zones
        assert set(t) <= {"assembly", "height_in", "geometry", "axis"}, p["id"]


def test_only_a_pack_drawn_at_the_wall_datum_carries_a_thumbnail(listed):
    for p in listed:
        if p["drawing"] == "assemblies":
            assert p["thumb"], f"{p['id']} is drawn at the wall datum and has no thumbnail"
        else:
            assert p["thumb"] is None, f"{p['id']} ({p['drawing']}) carries a thumbnail"
    assert any(p["drawing"] is None for p in listed), "the premise: some pack has no assembly"
    assert any(p["drawing"] == "stack" for p in listed), "the premise: some pack is stacked"


def test_the_stacked_first_assembly_at_the_wall_datum_is_why_an_order_has_none():
    """The measurement the refusal rests on, re-derived here so it cannot outlive its reason: at
    the wall datum some stacked pack's first assembly has no width at all, and some are
    `axis`-datum packs whose projections are radii from the column's axis."""
    pe = core._data()["engine"]
    prof = corpus._profiles()
    no_width, axis_datum = [], []
    for pid in pe.PACKS:
        pk = pe.resolve(pid)
        stack = pe.stack_for(pk)
        if not stack:
            continue
        d = pe.dimension(pk, core.module_binding(pk)["module_in"], [stack[0]])
        faces = prof.pack_geometry(d, datum="wall")["assemblies"][0]["faces"]
        xs = [v for f in faces for v in (f.get("x"), f.get("x_from")) if isinstance(v, (int, float))]
        if not xs or max(xs) - min(0, *xs) <= 1e-9:
            no_width.append(pid)
        if pk.get("projection_datum") == "axis":
            axis_datum.append(pid)
    assert no_width, "every stacked first assembly has a width at the wall datum: revisit the refusal"
    assert axis_datum, "no stacked pack measures from its axis: revisit the refusal"


def test_the_thumbnails_cost_the_list_less_than_the_budget(listed):
    with_thumbs = gzip.compress(_body({"packs": listed}), 4)
    without = gzip.compress(_body({"packs": [{**p, "thumb": None} for p in listed]}), 4)
    cost = len(with_thumbs) - len(without)
    assert cost > 0, "the premise: the thumbnails are in the list"
    assert cost < BUDGET_GZ, (
        f"the thumbnails add {cost} gzipped bytes to the list, over the ~60 KB the brief allows: "
        "serve them from GET /api/proportions/thumbs instead")


def test_the_list_is_built_once_and_a_reload_rebuilds_it():
    a = corpus.pack_list()
    assert corpus.pack_list() is a, "the thumbnails are built on every request"
    corpus.invalidate()
    assert corpus._PACK_LIST is None
    b = corpus.pack_list()
    assert b is not a and b == a


def test_the_mcp_payload_is_untouched_by_the_index(listed):
    """The index's keys are the workbench route's. `core.get_proportions` -- the MCP payload,
    whose stacked packs `test_pack_plates.py` pins byte for byte -- carries none of them."""
    for pid in ("trim-classical", "room-harmonic", "gibbs-doric"):
        got = core.get_proportions(pid)
        assert "thumb" not in got and "drawing" not in got, pid
