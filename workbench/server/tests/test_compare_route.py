"""WP-14.26 (tranche 2 PRD §C.7): `GET /api/compare/{a}/{b}`, two styles side by side.

The kit half is the one that could quietly become a third answer, so it is held to the two
`/api/kit` payloads a reader could fetch for themselves: every row the route serves, and no row it
does not, is the difference of those two payloads on the binding, the canonical set, the forbidden
set or the source, computed here by a reader written out in this file. The pairs swept are every
style whose kit answer the rebase MOVED (`tests/fixtures/kit_authority_moved_pairs.json`), each
set beside one other style -- the pairs where a compare reading any other resolver would differ.

The other three parts are held to the endpoints they repeat: `identify` to
`/api/styles/compare`, `proportions` to each style's `/packs`, `plans` to the partis the dossier's
Plan types section serves. Every expectation is computed; no count is written down.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "kit_authority_moved_pairs.json")
FIELDS = ("binding", "canonical", "forbidden", "source")
PARTNER = "craftsman"       # set beside every moved style; itself moved by nothing


def _get(client, url, **params):
    r = client.get(url, params=params or None)
    assert r.status_code == 200, (url, r.status_code, r.text[:200])
    return r.json()


def _pairs():
    with open(FIXTURE, encoding="utf-8") as fh:
        moved = json.load(fh)
    styles = sorted({p["style"] for p in moved["pairs"]})
    assert styles, "the premise: the rebase moved some style's kit"
    assert PARTNER not in styles, "the partner is itself a moved style; pick another"
    return [(s, PARTNER) for s in styles] + [(PARTNER, "tidewater-georgian")]


def _independent_difference(client, a, b):
    """The rows a compare of `a` and `b` must serve, from the two `/api/kit` payloads alone."""
    ka = {r["slot"]: r for r in _get(client, f"/api/kit/{a}", only_specified="false")["slots"]}
    kb = {r["slot"]: r for r in _get(client, f"/api/kit/{b}", only_specified="false")["slots"]}
    assert set(ka) == set(kb), "the two kits do not answer the same slots"
    want = {}
    for slot in ka:
        on = []
        for f in FIELDS:
            x, y = ka[slot][f], kb[slot][f]
            if isinstance(x, list):
                x, y = sorted(x), sorted(y)
            if x != y:
                on.append(f)
        if on:
            want[slot] = {"differs_on": on,
                          "a": {f: ka[slot][f] for f in FIELDS},
                          "b": {f: kb[slot][f] for f in FIELDS}}
    return want


def test_the_kit_rows_are_the_difference_of_the_two_kit_payloads(client):
    swept_a_moved_slot = 0
    with open(FIXTURE, encoding="utf-8") as fh:
        moved = {(p["style"], p["slot"]) for p in json.load(fh)["pairs"]}
    for a, b in _pairs():
        got = _get(client, f"/api/compare/{a}/{b}")
        assert (got["a"], got["b"]) == (a, b)
        rows = {r["slot"]: r for r in got["kit"]["rows"]}
        assert len(rows) == len(got["kit"]["rows"]), f"{a}/{b}: a slot served twice"
        want = _independent_difference(client, a, b)
        assert set(rows) == set(want), (a, b, sorted(set(rows) ^ set(want))[:6])
        for slot, w in want.items():
            r = rows[slot]
            assert r["differs_on"] == w["differs_on"], (a, b, slot)
            for side in ("a", "b"):
                for f in FIELDS:
                    x, y = r[side][f], w[side][f]
                    if isinstance(x, list):
                        x, y = sorted(x), sorted(y)
                    assert x == y, (a, b, slot, side, f, r[side][f], w[side][f])
            if (a, slot) in moved:
                swept_a_moved_slot += 1
        answer = sum(1 for r in rows.values() if r["differs_on"] != ["source"])
        assert got["kit"]["differ_in_answer"] == answer
        assert got["kit"]["differ_in_source_only"] == len(rows) - answer
        assert got["kit"]["slots_compared"] == len(_get(client, f"/api/kit/{a}",
                                                        only_specified="false")["slots"])
    # not vacuous: the sweep served rows for slots the rebase moved, which is where a compare
    # reading the other resolver would part from the kit payloads
    assert swept_a_moved_slot, "no compare row fell on a moved slot -- the sweep guards nothing"


def test_identify_proportions_and_plans_are_the_endpoints_they_repeat(client):
    a, b = PARTNER, "tidewater-georgian"
    got = _get(client, f"/api/compare/{a}/{b}")
    assert got["identify"] == _get(client, "/api/styles/compare", a=a, b=b)
    for side, sid in (("a", a), ("b", b)):
        assert got["proportions"][side] == _get(client, f"/api/styles/{sid}/packs"), side
        dossier = _get(client, f"/api/styles/{sid}/dossier")
        assert got["plans"][side] == dossier["plan_types"]["partis"], side
    assert set(got) == {"a", "b", "identify", "kit", "proportions", "plans"}


def test_an_unknown_style_is_refused_by_name(client):
    for a, b, missing in (("no-such-style", PARTNER, ["no-such-style"]),
                          (PARTNER, "nor-this-one", ["nor-this-one"]),
                          ("no-such-style", "nor-this-one", ["no-such-style", "nor-this-one"])):
        r = client.get(f"/api/compare/{a}/{b}")
        assert r.status_code == 404, (a, b, r.status_code)
        assert r.json()["detail"]["missing"] == missing, r.json()


def test_a_style_beside_itself_differs_nowhere(client):
    got = _get(client, f"/api/compare/{PARTNER}/{PARTNER}")
    assert got["kit"]["rows"] == []
    assert got["kit"]["differ_in_answer"] == got["kit"]["differ_in_source_only"] == 0
