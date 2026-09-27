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
    G = core._data()["glossary"]
    for e in index["entries"]:
        assert e["cite"].startswith(e["kind"] + ":"), e
        assert e["id"] and e["name"], e
        assert isinstance(e["hay"], str) and e["hay"] == e["hay"].lower(), e
        # The name must be findable by typing it: the haystack is what match.js reads.
        #
        # A glossary term's NAME carries its sense in parentheses (PRD phase 14, §C.5) -- two
        # records share the word "variant" and a list of two identical names is no answer -- so
        # the whole displayed name is not a substring of the haystack and the property is held
        # in its parts: the word itself, and the sense, each findable. (match.js compares the
        # typed query with the NAME before it reads the haystack, so the whole name still finds
        # itself; what this asserts is that each half does on its own.)
        if e["kind"] == "term":
            rec = G[e["id"]]
            assert rec["term"].lower() in e["hay"], f"{e['cite']} cannot be found by its word"
            if rec.get("sense"):
                assert e["name"] == rec["term"] + " (" + rec["sense"] + ")", e["name"]
                assert rec["sense"].lower() in e["hay"], f"{e['cite']} cannot be found by its sense"
            else:
                assert e["name"] == rec["term"], e["name"]
        else:
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
    # WP-14.3. The glossary's words, less the families a reader meets as places -- computed here
    # from the loaded records, never pinned, so a record added is a record expected.
    want_terms = sum(1 for t in D["glossary"].values()
                     if t["family"] not in ("surface", "section", "nav-group"))
    assert want_terms, "the premise: some glossary record is in an indexed family"
    assert got["term"] == want_terms
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


def test_a_glossary_definition_is_carried_for_display_and_never_matched(index):
    """§C.5: the haystack never includes the definition; `short` carries it for display only.
    A definition is prose -- the boundary this whole index keeps -- and in the haystack it would
    make "wall" find every term whose definition happens to mention a wall."""
    G = core._data()["glossary"]
    terms = [e for e in index["entries"] if e["kind"] == "term"]
    assert terms, "the premise: terms are indexed"
    for e in terms:
        t = G[e["id"]]
        assert e["short"] == t["definition"], e["cite"]
        assert t["definition"].lower() not in e["hay"], f"{e['cite']}'s definition is in its haystack"
        # and not a word of it by any other route: the haystack is the term, the id, the akas
        # and the sense, and nothing else
        allowed = set(" ".join([t["term"], t["id"], *(t.get("aka") or []),
                                t.get("sense") or ""]).lower().split())
        assert set(e["hay"].split()) <= allowed, (e["cite"], sorted(set(e["hay"].split()) - allowed))


def test_the_place_families_are_not_indexed_as_terms(index):
    """A surface, a dossier section and a rail group are places the rail and the page head name;
    the palette does not list them a second time as words (§C.5)."""
    G = core._data()["glossary"]
    place_ids = {i for i, t in G.items() if t["family"] in ("surface", "section", "nav-group")}
    assert place_ids, "the premise: some record is a place"
    indexed = {e["id"] for e in index["entries"] if e["kind"] == "term"}
    assert not (place_ids & indexed), sorted(place_ids & indexed)


def test_endpoint_serves_it(client):
    """Served on an open server, with no ceremony.

    This used to build its own client and clear two environment variables first, because
    `test_mcp_http.py`'s session-scoped fixture left WORKBENCH_API_TOKEN set for the rest
    of the process and every file sorting after it saw a gated server (OQ 64). That
    fixture is function-scoped now, so the workaround is gone and this test is what it
    should always have been: a GET against the shared client.
    """
    r = client.get("/api/search/index")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] > 600
    assert body["entries"][0]["cite"]


def test_the_index_is_gated_like_every_other_api_route(monkeypatch):
    """It carries the whole corpus's names in one response, so it must not be the one
    route that answers a stranger."""
    from fastapi.testclient import TestClient
    from workbench.server.app import app

    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    monkeypatch.delenv("WORKBENCH_API_TOKEN", raising=False)
    assert TestClient(app).get("/api/search/index").status_code == 401
