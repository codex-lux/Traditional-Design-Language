"""WP-14.3: the glossary, served (PRD phase 14, §C).

Every expectation here is DERIVED -- from the files in glossary/, from the glossary schema, or
from build/check_glossary.py's own FIELDS -- and never from a literal count, because a pinned
"121" would be a test of the batch that happened to be merged last rather than of the rule that
serves it. The rules held:

  * §C.1 the payload: its seven keys, the version rule, the digest recomputed here from the
    files AS AUTHORED, the term order, `reads` as a property of each basis, `by_family` complete
    over the schema enum, `by_field` complete over the seven fields;
  * §C.2 one term: the record, its confusables in declared order, its `see` names from the
    search index, and a miss as a 404 carrying `core.get_fault`'s `did_you_mean` rule;
  * §C.4 what must NOT move: `core.overview()` gains no glossary key and no glossary count, and
    `/api/health`'s counts are still exactly the overview's.

The gate half -- that `/api/glossary/about-tdl` is the one ungated path -- lives in
test_zz_auth_leak_guard.py, which is where a reader looks for what a stranger can reach.
"""
import glob
import hashlib
import json
import os

import pytest

pytest.importorskip("fastapi")

from workbench.server import corpus  # noqa: E402

core = corpus.core
ROOT = corpus.ROOT

PAYLOAD_KEYS = {"version", "schema_version", "digest", "count", "terms", "by_family", "by_field"}


def _files():
    """The records as authored, read from disk here and not through core, so the payload is
    held against the directory rather than against the loader it was built by."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "glossary", "*.json"))):
        with open(f, encoding="utf-8") as fh:
            rec = json.load(fh)
        out[rec["id"]] = rec
    return out


def _schema():
    with open(os.path.join(ROOT, "schema", "glossary-term.schema.json"), encoding="utf-8") as f:
        return json.load(f)


def _fields():
    return core._mod("check_glossary", os.path.join(ROOT, "build", "check_glossary.py")).FIELDS


@pytest.fixture(scope="module")
def payload():
    return corpus.glossary_payload()


# ------------------------------------------------------------------ §C.1 the payload

def test_the_payload_carries_exactly_its_seven_keys(payload):
    assert set(payload) == PAYLOAD_KEYS, sorted(payload)


def test_the_version_is_the_schema_version_and_a_digest_of_the_records_as_authored(payload):
    files = _files()
    assert files, "glossary/ holds no record -- the premise of every test below"
    assert payload["schema_version"] == _schema()["version"]
    want = hashlib.sha256(json.dumps([files[k] for k in sorted(files)], sort_keys=True,
                                     separators=(",", ":"), ensure_ascii=False)
                          .encode("utf-8")).hexdigest()[:16]
    assert payload["digest"] == want, (
        "the digest is over the records AS AUTHORED, sorted by id, with no `reads` -- a digest "
        "that took the served form would change version every time the derivation did")
    assert payload["version"] == payload["schema_version"] + "+" + payload["digest"]


def test_every_record_is_served_once_and_as_authored(payload):
    files = _files()
    ids = [t["id"] for t in payload["terms"]]
    assert payload["count"] == len(payload["terms"]) == len(files)
    assert len(set(ids)) == len(ids), "a term is served twice"
    assert set(ids) == set(files)
    for t in payload["terms"]:
        served = {k: v for k, v in t.items() if k != "reads"}
        assert served == files[t["id"]], f"{t['id']} is not served as it is authored"


def test_the_terms_are_in_family_then_order_then_id_order(payload):
    families = _schema()["properties"]["family"]["enum"]
    inf = float("inf")
    keys = [(families.index(t["family"]), t["order"] if "order" in t else inf, t["id"])
            for t in payload["terms"]]
    assert keys == sorted(keys)
    # and the ordering is doing work: a family whose records carry an `order` is not simply in
    # id order, or this test would pass with the middle key deleted
    assert any([t["id"] for t in payload["terms"] if t["family"] == f]
               != sorted(t["id"] for t in payload["terms"] if t["family"] == f)
               for f in families), "no family's `order` differs from its id order -- the premise"


def test_reads_is_every_admissible_file_the_basis_names_in_order_once(payload):
    """A PROPERTY of each basis rather than the production expression restated: every file
    listed is in the basis, exists, and is admitted by the pattern the checker verifies against;
    none is listed twice; they come in order of first appearance; and none admitted is missing."""
    rx = core._mod("check_openings", os.path.join(ROOT, "build", "check_openings.py")).GLOSSARY_REC_RE
    for t in payload["terms"]:
        basis = t.get("basis") or ""
        reads = t["reads"]
        assert len(set(reads)) == len(reads), f"{t['id']} lists a file twice"
        for f in reads:
            assert f in basis, f"{t['id']} reads {f}, which its basis does not name"
            assert os.path.exists(os.path.join(ROOT, f)), f"{t['id']} reads {f}, which is not a file"
            assert rx.fullmatch(f), f"{t['id']} reads {f}, which a basis may not name"
        firsts = [basis.find(f) for f in reads]
        assert firsts == sorted(firsts), f"{t['id']}: reads are not in order of first appearance"
        assert set(reads) == set(rx.findall(basis)), f"{t['id']}: an admissible file is missing"
    # the one record served to a stranger read exactly one file, and it is VISION.md
    about = next(t for t in payload["terms"] if t["id"] == "about-tdl")
    assert about["reads"] == ["VISION.md"]


def test_by_family_is_every_schema_family_in_enum_order(payload):
    families = _schema()["properties"]["family"]["enum"]
    assert list(payload["by_family"]) == families
    order = [t["id"] for t in payload["terms"]]
    for fam, ids in payload["by_family"].items():
        assert ids == [t["id"] for t in payload["terms"] if t["family"] == fam], fam
        assert ids == sorted(ids, key=order.index)
    assert sorted(i for ids in payload["by_family"].values() for i in ids) == sorted(order)


def test_by_field_is_every_field_and_every_bound_value(payload):
    fields = _fields()
    assert list(payload["by_field"]) == list(fields), "all seven FIELDS keys, in their order"
    want = {f: {} for f in fields}
    for rec in _files().values():
        for b in rec.get("binds") or []:
            want[b["field"]][b["value"]] = rec["id"]
    assert payload["by_field"] == want
    # the PRD's own example row, so a mis-keyed map cannot pass by being self-consistent
    assert payload["by_field"]["kit.binding"] == {
        "specified": "binding-specified", "extends": "binding-extends",
        "open": "binding-open", "forbidden": "binding-forbidden"}


def test_the_payload_is_built_once_and_reset_clears_it():
    """Built once, shared, and cleared by its own reset. That `corpus.invalidate()` calls the
    reset is held where every other cache's clearing is held,
    test_compression_and_caching.py::test_invalidate_clears_every_cache_it_claims_to."""
    corpus.reset_glossary_payload()
    assert corpus._GLOSSARY_PAYLOAD is None
    a = corpus.glossary_payload()
    assert corpus.glossary_payload() is a, "built twice without a reset"
    corpus.reset_glossary_payload()
    assert corpus._GLOSSARY_PAYLOAD is None


# ------------------------------------------------------------------ §C.2 one term

def test_a_term_is_served_with_its_confusables_and_its_see(client):
    files = _files()
    r = client.get("/api/glossary/rank-variant")
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"version", "term", "confusable", "see"}
    assert body["version"] == corpus.glossary_payload()["version"]
    rec = files["rank-variant"]
    assert {k: v for k, v in body["term"].items() if k != "reads"} == rec
    assert body["confusable"] == [
        {"id": o, "term": files[o]["term"], "sense": files[o].get("sense")}
        for o in rec["confusable_with"]]
    names = {e["cite"]: e["name"] for e in corpus.search_index()["entries"]}
    assert body["see"] == [{"cite": c, "name": names.get(c)} for c in rec["see"]]


def test_every_record_with_confusables_resolves_them_in_declared_order():
    files = _files()
    carrying = [i for i, r in files.items() if r.get("confusable_with")]
    assert carrying, "no record declares a confusable -- the premise"
    for rid in carrying:
        got = corpus.glossary_term(rid)["confusable"]
        assert [c["id"] for c in got] == files[rid]["confusable_with"], rid
        for c in got:
            assert c["term"] == files[c["id"]]["term"], (rid, c)


def test_a_see_cite_is_named_from_the_index_and_null_where_its_kind_is_not_indexed():
    files = _files()
    indexed = {e["cite"]: e["name"] for e in corpus.search_index()["entries"]}
    named = unnamed = 0
    for rid, rec in files.items():
        for s in corpus.glossary_term(rid)["see"]:
            assert s["name"] == indexed.get(s["cite"]), (rid, s)
            named += s["name"] is not None
            unnamed += s["name"] is None
    # both halves must occur in the corpus, or one branch is being asserted vacuously
    assert named and unnamed, (named, unnamed)


def test_a_miss_is_a_404_with_the_did_you_mean_rule_of_get_fault(client):
    r = client.get("/api/glossary/nosuch")
    assert r.status_code == 404
    assert r.json() == {"detail": {"error": "no glossary term 'nosuch'", "did_you_mean": []}}
    files = _files()
    r = client.get("/api/glossary/JUDGMENT")
    assert r.status_code == 404
    want = [k for k in files if "judgment" in k][:8]
    assert want, "the premise: some id contains the fragment"
    assert r.json()["detail"]["did_you_mean"] == want


def test_the_index_route_serves_the_payload(client):
    r = client.get("/api/glossary")
    assert r.status_code == 200
    assert r.json()["version"] == corpus.glossary_payload()["version"]
    assert r.json()["count"] == len(_files())


# ------------------------------------------------------------------ §C.4 what does not move

def test_the_overview_gains_no_glossary_key_and_no_glossary_count():
    ov = core.overview()
    assert "glossary" not in ov
    assert "glossary" not in ov["counts"]
    assert not any("glossary" in k or "term" in k for k in ov["counts"]), sorted(ov["counts"])
    # and the MCP half: no tool reads the glossary, because every MCP payload is byte-stable in
    # tranche one and the server module is where a tool would be added
    src = open(os.path.join(ROOT, "mcp_server", "server.py"), encoding="utf-8").read()
    assert "glossary" not in src


def test_health_counts_are_still_exactly_the_overviews(client):
    body = client.get("/api/health").json()
    assert body["counts"] == core.overview()["counts"]
    assert "glossary" not in body and "glossary" not in body["counts"]
