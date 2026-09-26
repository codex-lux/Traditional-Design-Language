"""WP-14.19 -- a brief may name a parti (`oq/a-brief-cannot-name-a-parti`, ruled 25 Sep 2026).

The server's half of the contract (`docs/prd/phase-14-tranche-2.md` §C.5): the brief is checked for
the parti it names BEFORE a job exists, through `jobs.submit` and the route alike; `core.list_partis`
carries each parti's nativity and lists lineage partis beside native ones; `GET /api/partis/{id}` is
one parti and the styles it belongs to; and a compose job's stage events carry `total`, with every
diagram the compose considers heard from once, so a count of them reaches it.

The composer's half -- the guarantee itself, displacing nothing, the lot's refusal -- is in
`tests/test_composer.py`, where the composer is. Nothing here asserts a count of partis: every
expectation is read off the catalogue, so a parti added tomorrow moves no literal.
"""
import json
import os

import pytest

from workbench.server import corpus, jobs

core = corpus.core
ROOT = corpus.ROOT


def _brief(**extra):
    with open(os.path.join(ROOT, "briefs", "family-georgian.json"), encoding="utf-8") as f:
        b = json.load(f)
    b.update(extra)
    return b


# ------------------------------------------------------------------ refused before a job exists
@pytest.mark.parametrize("brief, named", [
    (_brief(parti="no-such-parti"), ["'no-such-parti'"]),
    (_brief(massing="four-over-four", parti="octagon-radial"), ["'octagon-radial'", "'four-over-four'"]),
])
def test_jobs_submit_refuses_a_brief_whose_parti_cannot_be_honoured(brief, named):
    before = set(jobs._JOBS)
    res = jobs.submit(brief, candidates=1, options={"revise": False})
    assert "error" in res and "job_id" not in res, res
    assert res["error"] == core._composer().BRIEF_REF_ERROR
    for n in named:
        assert n in res["detail"], res["detail"]
    assert set(jobs._JOBS) == before, "a refused brief must not leave a job behind"


def test_the_compose_route_refuses_it_with_a_422_naming_the_parti(client):
    before = set(jobs._JOBS)
    r = client.post("/api/compose", json={"brief": _brief(parti="no-such-parti"), "candidates": 1,
                                          "revise": False})
    assert r.status_code == 422, r.text
    assert "'no-such-parti'" in r.json()["detail"]["detail"]
    assert set(jobs._JOBS) == before


def test_the_mcp_compose_refuses_it_the_same_way():
    res = core.compose(_brief(massing="four-over-four", parti="octagon-radial"), 1, revise=False)
    assert res.get("error") == core._composer().BRIEF_REF_ERROR
    assert "'octagon-radial'" in res["detail"] and "candidates" not in res


def test_a_brief_naming_a_real_parti_passes_the_door():
    assert jobs._validate_brief(_brief(parti="centre-passage-double-pile")) is None
    assert jobs._validate_brief(_brief()) is None


# ------------------------------------------------------------------ the list and the record
def test_list_partis_carries_nativity_and_lists_lineage_beside_native(client):
    catalogue = {p["id"] for p in core._all_partis()}
    nat = core._composer().nativity
    for style in ("tidewater-georgian", "craftsman-bungalow", "egyptian-revival"):
        r = client.get("/api/partis", params={"style": style}).json()
        want = {p: nat(p, style) for p in catalogue}
        assert {p["id"]: p["nativity"] for p in r["partis"]} == \
            {p: n for p, n in want.items() if n != "borrowed"}, style
        assert r["count"] == len(r["partis"])
        every = client.get("/api/partis", params={"style": style, "include_borrowed": "true"}).json()
        assert {p["id"]: p["nativity"] for p in every["partis"]} == want, style
    # the premise that makes the list worth carrying: somewhere a style gains a lineage parti,
    # and somewhere one has none native at all and still has plan types
    lineage = [s for s in core._data()["styles"] if any(nat(p, s) == "lineage" for p in catalogue)]
    assert lineage, "premise: some style has a lineage parti"
    no_native = [s for s in lineage if not any(nat(p, s) == "native" for p in catalogue)]
    assert no_native, "premise: some style has lineage partis and no native one"


def test_without_a_style_there_is_no_relation_to_state(client):
    r = client.get("/api/partis").json()
    assert r["count"] == len(core._all_partis())
    assert all("nativity" not in p for p in r["partis"])


def test_one_parti_and_the_styles_it_belongs_to(client):
    r = client.get("/api/partis/centre-passage-double-pile")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["parti"]["id"] == "centre-passage-double-pile"
    by = body["nativity_by_style"]
    assert set(by) == {"native", "lineage"}
    nat = core._composer().nativity
    styles = sorted(core._data()["styles"])
    assert by["native"] == [s for s in styles if nat("centre-passage-double-pile", s) == "native"]
    assert by["lineage"] == [s for s in styles if nat("centre-passage-double-pile", s) == "lineage"]
    assert "tidewater-georgian" in by["native"] and by["lineage"], by


def test_an_unknown_parti_is_a_404_naming_it(client):
    r = client.get("/api/partis/no-such-parti")
    assert r.status_code == 404
    assert r.json()["detail"]["error"] == "no parti 'no-such-parti'"


def test_the_record_route_adds_no_path_of_its_own():
    """`core.get_parti` reads through `core.load_parti`, whose basename would turn a smuggled
    directory into the real file; the id must name the record it reads, or it is refused."""
    assert "error" in core.get_parti("x/centre-passage-double-pile")
    assert "error" in core.get_parti("../partis/centre-passage-double-pile")
    assert core.get_parti("centre-passage-double-pile")["parti"]["id"] == "centre-passage-double-pile"


def test_the_dossier_lists_what_the_style_list_lists_with_its_nativity(client):
    for sid in ("tidewater-georgian", "egyptian-revival"):
        pt = client.get(f"/api/styles/{sid}/dossier").json()["plan_types"]
        listed = client.get("/api/partis", params={"style": sid}).json()["partis"]
        assert [(p["id"], p["nativity"]) for p in pt["partis"]] == \
            [(p["id"], p["nativity"]) for p in listed], sid


# ------------------------------------------------------------------ k of N
def test_every_stage_event_carries_the_total_and_every_diagram_is_heard_from():
    """Run a real compose job synchronously on a brief whose lot drops one of the diagrams it
    considers: every `stage` event carries `total`; the candidate events and the lot's `dropped`
    stage events together number exactly `total`; and `considered` counts up to it."""
    brief = _brief(massing="four-over-four")
    brief["context"] = dict(brief["context"], lot_width_ft=30)
    total = len(core._composer().considered(brief, 1))
    job = jobs.Job(brief, 1, {"revise": False})
    jobs._JOBS[job.id] = job
    try:
        jobs._run(job)
        events = list(job.events.queue)
    finally:
        jobs._JOBS.pop(job.id, None)
    assert job.status == "done", job.error
    # the premise is read off the composer's own RESULT, not off the stream under test, so a
    # stream that stops reporting the dropped diagram fails the assertion about the stream and
    # not this one
    lot_dropped = {d["parti"] for d in job.result.get("dropped_lot_infeasible") or []}
    assert lot_dropped, "premise: a 30 ft lot drops a diagram this brief considers"
    stages = [e["data"] for e in events if e["event"] == "stage"]
    assert stages and all(s.get("total") == total for s in stages), stages
    dropped = [s for s in stages if s["stage"] == "dropped"]
    scored = [e["data"] for e in events if e["event"] == "candidate"]
    assert {d["parti"] for d in dropped} == lot_dropped, "every diagram the lot drops is heard from"
    assert len(scored) + len(dropped) == total
    heard = sorted(d["considered"] for d in scored + dropped)
    assert heard == list(range(1, total + 1)), heard
    assert all("n" not in d for d in dropped), "a dropped diagram is never counted as scored"
    assert [e["event"] for e in events][-1] == "done"
