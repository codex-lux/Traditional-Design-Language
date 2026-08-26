"""The palette's index. Two things matter here and they are both about honesty:

  1. Every entry must be reachable. The palette dispatches by citation, so an entry whose
     cite does not validate is a search result that goes nowhere when clicked — the exact
     failure the citation validator exists to prevent on the rail.
  2. The index must not quietly stop covering a kind. The counts are cross-checked against
     core.overview(), so adding styles without reindexing them fails here rather than
     showing a searcher an incomplete corpus that looks complete.
"""
import pytest

pytest.importorskip("fastapi")

from workbench.server import citations, corpus  # noqa: E402

core = corpus.core


@pytest.fixture(scope="module")
def index():
    return corpus.search_index()


def test_every_cite_parses_and_resolves(index):
    """A result that cannot be cited cannot be navigated to."""
    bad = []
    for e in index["entries"]:
        ok, reason = citations.validate(e["cite"])
        if not ok:
            bad.append((e["cite"], reason))
    assert not bad, f"{len(bad)} entries cite something unresolvable: {bad[:5]}"


def test_entry_shape(index):
    for e in index["entries"]:
        assert e["cite"].startswith(e["kind"] + ":"), e
        assert e["id"] and e["name"], e
        assert isinstance(e["hay"], str) and e["hay"] == e["hay"].lower(), e
        # The name must be findable by typing it: the haystack is what match.js reads.
        assert e["name"].lower() in e["hay"], f"{e['cite']} cannot be found by its own name"
        assert e["id"].lower() in e["hay"], f"{e['cite']} cannot be found by its own id"


def test_covers_every_kind_completely(index):
    """Counts come from the corpus, not from a literal, so the two cannot drift."""
    counts = core.overview()["counts"]
    got = {}
    for e in index["entries"]:
        got[e["kind"]] = got.get(e["kind"], 0) + 1

    D = core._data()
    assert got["style"] == counts["styles"] == len(D["styles"])
    assert got["slot"] == counts["element_slots"] == len(D["slots"])
    assert got["fault"] == counts["faults"] == len(D["faults"])
    assert got["room"] == counts["rooms"] == len(D["rooms"])
    assert got["massing"] == counts["massings"] == len(D["massings"])
    assert got["grouping"] == len(D["groupings"])
    assert got["pack"] == len(D["engine"].PACKS)
    assert got["parti"] == len(citations._parti_ids())
    assert index["count"] == len(index["entries"]) == sum(got.values())


def test_ids_are_unique_within_a_kind(index):
    seen = set()
    for e in index["entries"]:
        assert e["cite"] not in seen, f"{e['cite']} indexed twice"
        seen.add(e["cite"])


def test_says_what_it_does_not_index(index):
    """The boundary is documented in the payload rather than left for a caller to
    discover by missing results. Prose is deliberately out — see corpus.search_index."""
    assert index["does_not_index"]
    assert index["indexes"]
    # And the boundary is real: no entry carries a tell or a remedy paragraph.
    longest = max(len(e["hay"]) for e in index["entries"])
    assert longest < 600, f"a haystack of {longest} chars means prose crept back in"


def test_endpoint_serves_it(client):
    r = client.get("/api/search/index")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] > 600
    assert body["entries"][0]["cite"]
