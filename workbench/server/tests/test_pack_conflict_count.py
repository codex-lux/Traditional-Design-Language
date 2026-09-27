"""WP-14.31: the pack index states each pack's own recorded conflicts, so a page can COUNT them.

The Export page's details-library card typed "all 262 recorded pack conflicts" -- true on the day
it was typed and silently false after any pack gained or lost one, which is how the Kit's header
once said 95 slots against an ontology holding 97. `GET /api/proportions` carries `conflicts` on
every row now, and the page sums the rows.

THE FIGURE IS THE RAW PACK'S AND THAT IS ASSERTED, NOT ASSUMED. A resolved overlay repeats its
base's conflicts, so summing over resolved packs counts one recorded conflict once per overlay
that inherits it (measured on this tree: 262 raw against 340 resolved). The expectation below is
computed from the pack files on disk -- no count is written down -- and the premise that the two
readings differ is asserted, so a route that switched to the resolved list would fail here rather
than pass by coincidence.
"""
import glob
import json
import os

from workbench.server import corpus

ROOT = corpus.core.ROOT


def _files():
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "**", "*.json"), recursive=True)):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        if isinstance(d, dict) and "id" in d and "conflicts" in d:
            out[d["id"]] = len(d.get("conflicts") or [])
    return out


def test_every_row_states_its_packs_own_recorded_conflicts(client):
    r = client.get("/api/proportions")
    assert r.status_code == 200
    rows = r.json()["packs"]
    assert rows, "the premise: the list serves packs"
    on_disk = _files()
    assert sum(on_disk.values()) > 0, "the premise: the corpus records pack conflicts at all"
    for p in rows:
        assert isinstance(p.get("conflicts"), int), p["id"]
        assert p["conflicts"] == on_disk.get(p["id"], 0), p["id"]
    assert sum(p["conflicts"] for p in rows) == sum(on_disk.values())


def test_the_count_is_the_raw_packs_and_not_the_resolved_one(client):
    """An overlay's resolved list repeats its base's, so the two readings must differ on this
    corpus for the equality above to mean the raw one was taken."""
    pe = corpus.core._data()["engine"]
    raw = sum(len(p.get("conflicts") or []) for p in pe.PACKS.values())
    resolved = sum(len(pe.resolve(k).get("conflicts") or []) for k in pe.PACKS)
    assert resolved != raw, "the premise: an overlay inherits its base's conflicts"
    rows = client.get("/api/proportions").json()["packs"]
    assert sum(p["conflicts"] for p in rows) == raw
