"""WP-14.4 (PRD §H.5): the shipped example briefs are loadable by name, and only by name.

`/api/schema/brief` has listed `briefs/*.json` as `examples` since the brief schema was served,
and nothing could fetch one: Brief Intake had a list of names and no route behind them. The
route mirrors `/api/plans/examples/{name}` exactly -- `os.path.basename`, `.json` appended when
absent, 404 for a name with no file, 422 for a file that is not JSON -- because a second rule
for the same question is how two surfaces come to disagree about what a name may reach.

Every expectation is read off the corpus or the schema route; nothing names a brief the list
does not. Nothing here writes inside the repository: the unreadable-JSON case points the
route's root at a temporary directory.
"""
import json
import os

import pytest

from workbench.server import corpus


def _examples(client):
    names = client.get("/api/schema/brief").json()["examples"]
    assert names, "the schema route lists no example brief; every test below would be vacuous"
    return names


def _on_disk(name):
    with open(os.path.join(corpus.ROOT, "briefs", name), encoding="utf-8") as f:
        return json.load(f)


def test_every_listed_example_loads_with_and_without_its_extension(client):
    """The list carries `.json` and a reader types the stem: both must reach the same file, and
    what comes back is the file as stored -- the route adds nothing and takes nothing away."""
    for name in _examples(client):
        assert name.endswith(".json"), name
        want = _on_disk(name)
        for asked in (name, name[: -len(".json")]):
            r = client.get(f"/api/briefs/examples/{asked}")
            assert r.status_code == 200, (asked, r.text)
            assert r.json() == want, f"{asked}: the route served something other than the file"


def test_the_listed_examples_are_every_brief_on_disk(client):
    """The list is the population the route serves -- a brief on disk the list omits is one a
    reader cannot find, and a listed name the route cannot load is a dead link."""
    on_disk = sorted(f for f in os.listdir(os.path.join(corpus.ROOT, "briefs"))
                     if f.endswith(".json"))
    assert sorted(_examples(client)) == on_disk


def test_a_missing_brief_is_a_404_that_names_it(client):
    r = client.get("/api/briefs/examples/no-such-brief")
    assert r.status_code == 404
    assert r.json()["detail"] == {"error": "no example brief 'no-such-brief'"}


def test_a_path_is_never_a_name():
    """The handler strips any directory a caller smuggles in -- asserted on the HANDLER, because
    whether the URL form reaches it at all is a Starlette routing detail that has changed
    version to version (test_endpoints.py's example-plan twin records why)."""
    from fastapi import HTTPException
    from workbench.server.app import example_brief
    for probe in ("../../CLAUDE.md", "../plans/tidewater-georgian-careful",
                  os.path.join(corpus.ROOT, "CLAUDE.md")):
        with pytest.raises(HTTPException) as e:
            example_brief(probe)
        assert e.value.status_code == 404, probe
        assert e.value.detail["error"] == f"no example brief '{os.path.basename(probe)}'"


def test_a_path_in_the_url_never_serves_the_file(client):
    r = client.get("/api/briefs/examples/../../CLAUDE.md")
    assert r.status_code in (200, 404)
    assert "working notes for Claude Code" not in r.text


def test_an_unreadable_brief_is_a_422_not_a_500(tmp_path, monkeypatch):
    """A malformed example is the corpus's defect, reported cleanly -- and the root is moved to
    a temporary directory, so the malformed file never exists inside the repository."""
    from fastapi.testclient import TestClient
    from workbench.server.app import app
    (tmp_path / "briefs").mkdir()
    (tmp_path / "briefs" / "bad.json").write_text("{ not json", encoding="utf-8")
    monkeypatch.setattr(corpus, "ROOT", str(tmp_path))
    tc = TestClient(app)
    # the message names the brief as the caller ASKED for it, as example_plan's does (§H.5's
    # `<name>`), so both spellings are driven
    for asked in ("bad", "bad.json"):
        r = tc.get(f"/api/briefs/examples/{asked}")
        assert r.status_code == 422, r.text
        d = r.json()["detail"]
        assert d["error"] == f"example brief '{asked}' is not readable JSON"
        assert d["detail"]                           # the parser's own words, truncated


@pytest.mark.parametrize("path", [
    "/api/briefs/examples/family-georgian",
    "/api/styles/tidewater-georgian/packs",
    "/api/styles/tidewater-georgian/dossier",
    "/api/proportions/trim-classical?members=true",
])
def test_every_new_route_is_behind_the_gate(path, monkeypatch):
    """The auth gate covers every `/api/` path by prefix, so the new routes are gated by
    construction -- asserted rather than assumed, because a route registered outside the prefix
    would be open and nothing else would say so."""
    from fastapi.testclient import TestClient
    from workbench.server.app import app
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    assert TestClient(app).get(path).status_code == 401, path
    monkeypatch.delenv("WORKBENCH_PASSWORD", raising=False)
    monkeypatch.delenv("WORKBENCH_API_TOKEN", raising=False)
    assert TestClient(app).get(path).status_code == 200, \
        f"{path}: open with no password set, or the 401 above proved nothing"
