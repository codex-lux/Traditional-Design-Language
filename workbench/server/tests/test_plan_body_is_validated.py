"""A caller-supplied plan record reaches build/geometry.py, and nine of its fields crashed it.

WP-10.1's audit, 3 Sep 2026. `/api/plan/evaluate`, `/api/drawings/{kind}` and `/api/export/{fmt}`
read `body.plan` and handed it straight to the solver, while their siblings `/api/plan/critique`
and `/api/plan/revise` validate it inside `core`. Fuzzed at `geometry.solve()`'s entry, **9 of 16
probed fields raise** on a value of the wrong type -- `C["rooms"].get(rtype, {})` on a dict is
`TypeError: unhashable type`, which is a 500 and a traceback from an unauthenticated route, for a
field the schema types `string`.

A tenth, `room.block`, was fixed at the geometry layer instead, because the block machinery is new
and ignoring a malformed tag is a conservative reading that is actually available there. There is
no conservative reading of a room whose `type` is a list.
"""
import copy
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _plan():
    return json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))


# The nine the fuzz found, each with a value of a type the schema forbids. `block` is the tenth
# and is deliberately absent: it is answered at the geometry layer, and
# tests/test_geometry.py::...::test_a_block_field_that_is_not_a_string_is_ignored... holds it.
BAD = [
    (["levels", 0, "rooms", 0, "type"], {"evil": True}),
    (["levels", 0, "rooms", 0, "id"], ["a"]),
    (["levels", 0, "rooms", 0, "width_ft"], {"n": 1}),
    (["levels", 0, "rooms", 0, "length_ft"], ["x"]),
    (["levels", 0, "rooms", 0, "exterior_walls"], {"N": True}),
    (["levels", 0, "rooms", 0, "doors"], {"to": "hall"}),
    (["style"], {"id": "tidewater-georgian"}),
    (["massing"], ["four-over-four"]),
    (["levels"], {"0": {}}),
]

ROUTES = [("post", "/api/plan/evaluate"), ("post", "/api/drawings/plan"), ("post", "/api/export/dxf")]


@pytest.mark.parametrize("path,val", BAD, ids=[".".join(str(x) for x in p) for p, _ in BAD])
@pytest.mark.parametrize("method,url", ROUTES, ids=[u for _m, u in ROUTES])
def test_a_malformed_plan_is_a_422_and_never_a_500(client, method, url, path, val):
    plan = _plan()
    o = plan
    for k in path[:-1]:
        o = o[k]
    o[path[-1]] = val
    r = client.request(method, url, json={"plan": plan})
    assert r.status_code != 500, (
        f"{url} answered 500 for a malformed {'.'.join(str(x) for x in path)} -- an "
        "unauthenticated caller can crash the solver with a field the schema types")
    assert r.status_code == 422, f"{url} answered {r.status_code}, expected 422"
    body = r.json().get("detail") or {}
    assert "schema" in str(body).lower(), f"the 422 does not say why: {body}"


@pytest.mark.parametrize("method,url", ROUTES, ids=[u for _m, u in ROUTES])
def test_the_gate_refuses_none_of_the_traffic_it_is_meant_to_carry(client, method, url):
    """The half that matters more than the refusals: a gate that rejects the client's own
    records is worse than the crash it replaces. The bench posts the DECLARED record, and both
    shipped plans are declared records with placement, so the shipped plan is the fixture."""
    r = client.request(method, url, json={"plan": _plan()})
    assert r.status_code != 422 or "schema" not in str(r.json()).lower(), (
        f"{url} refused a shipped reference plan as schema-invalid: {r.json()}")


def test_a_missing_plan_is_still_the_older_and_more_specific_refusal(client):
    r = client.post("/api/plan/evaluate", json={})
    assert r.status_code == 422
    assert "required" in str(r.json()).lower()
