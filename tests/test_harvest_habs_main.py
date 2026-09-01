"""`harvest_habs.main()` — the only code that groups, skips, writes or touches the network.

WHY THIS FILE EXISTS. `tests/test_harvest_habs.py` opens by claiming every test in it was
mutation-checked, and eleven of its fifteen were. But the four defects the harvester's own
docstring says are "ALL FIXED HERE" live in `main()`, and `main()` had no test at all: an
adversarial audit reverted each fix INSIDE main() and the whole file stayed green.

  - one request per RECORD instead of per building        -> 16 passed
  - drop the jurisdiction skip and query foreign buildings -> 16 passed
  - write `status = "sourced"` on every enriched record    -> 16 passed
  - write a `license` conclusion onto every record         -> 16 passed

`test_records_are_grouped_by_building_so_one_building_is_one_request` is the sharpest case: its
name and docstring are entirely about the grouping, and it only calls `query_for` in a loop. The
grouping is in `main()`.

These drive the real `main()` over a fake transport and a temp manifest, and assert on what it
REQUESTED and what it WROTE.
"""
import json
import os
import shutil
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

H = modcache.load("harvest_habs", os.path.join(ROOT, "build", "harvest_habs.py"))


def _payload(pk="va0315", title="Westover, Charles City County, VA", brief="Photo(s): 73",
             call="HABS VA,19-WEST,1-"):
    return {"results": [{"id": pk, "url": "https://www.loc.gov/pictures/item/%s/" % pk,
                         "title": title, "medium_brief": brief, "call_number": call,
                         "rights_information": "No known restrictions on images made by the "
                                               "U.S. Government; images copied from other "
                                               "sources may be restricted."}]}


@pytest.fixture()
def rig(tmp_path, monkeypatch):
    """A temp manifest, a recording fake fetch, and no sleeping."""
    src = json.load(open(os.path.join(ROOT, "assets", "manifest.json")))
    # Six records over two US buildings and one English one, so grouping and jurisdiction both bite.
    keep = []
    for a in src["assets"]:
        b = (a.get("provenance") or {}).get("building")
        if b in ("Westover", "Drayton Hall", "Queen Square") and a.get("kind") == "photograph":
            keep.append(a)
    doc = {"schema": src["schema"], "version": src["version"],
           "counts": {"total": len(keep), "by_status": {"wanted": len(keep)}}, "assets": keep}
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(doc, indent=2))
    monkeypatch.setattr(H, "ASSETS", str(path))
    monkeypatch.setattr(H, "CONTACT", "audit@example.invalid")
    monkeypatch.setattr(H, "pause", lambda: None)
    seen = []
    monkeypatch.setattr(H, "fetch", lambda url, timeout=30: (seen.append(url), _payload())[1])
    return {"path": str(path), "requests": seen,
            "doc": lambda: json.loads(open(path).read())}


def _run(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["harvest_habs.py"] + list(argv))
    return H.main()


# ------------------------------------------------- defect 4: one request per BUILDING

def test_one_request_per_building_not_per_record(rig, monkeypatch, capsys):
    rc = _run(monkeypatch, "--live")
    assert rc == 0, capsys.readouterr().out
    n_records = len(rig["doc"]()["assets"])
    assert n_records > 10, "the fixture must hold more records than buildings"
    # Westover and Drayton Hall are in charter; Queen Square is not.
    assert len(rig["requests"]) == 2, (len(rig["requests"]), rig["requests"])


def test_a_building_outside_the_survey_costs_no_request(rig, monkeypatch, capsys):
    _run(monkeypatch, "--live")
    joined = " ".join(rig["requests"])
    assert "Queen" not in joined, "spent a rate-limited request on a building HABS cannot hold"
    assert "OUTSIDE" in capsys.readouterr().out


# ------------------------------------ defect 2 and the sourced claim, at the WRITE site

def test_write_never_sets_sourced_and_never_concludes_a_licence(rig, monkeypatch, capsys):
    before = {a["id"]: (a.get("provenance") or {}).get("license") for a in rig["doc"]()["assets"]}
    _run(monkeypatch, "--live", "--write")
    out = rig["doc"]()["assets"]
    touched = [a for a in out if a.get("review_note")]
    assert touched, "nothing was enriched; this test would pass vacuously"
    for a in touched:
        assert a["status"] != "sourced", "%s was marked sourced with no file" % a["id"]
        # `unknown` is gen_assets.py's pre-existing default, not something the harvester wrote.
        # What must never happen is a machine CONCLUDING a licence from the Library's rights
        # boilerplate -- the same sentence sits on a government photograph and on a HABS
        # photograph of a third party's copyrighted drawing.
        assert (a.get("provenance") or {}).get("license") == before[a["id"]], \
            "%s: the harvester changed the licence" % a["id"]
        assert (a["provenance"].get("license") or "unknown") == "unknown"
        assert (a["provenance"].get("rights_evidence") or "").startswith("No known restrictions"), \
            "the rights sentence was not recorded verbatim as evidence"


def test_write_does_not_overwrite_the_curated_building_name(rig, monkeypatch):
    before = {a["id"]: (a.get("provenance") or {}).get("building") for a in rig["doc"]()["assets"]}
    _run(monkeypatch, "--live", "--write")
    after = rig["doc"]()["assets"]
    for a in after:
        assert (a.get("provenance") or {}).get("building") == before[a["id"]], \
            ("%s: the curated name was replaced by the archive's title. query_for searches ON "
             "this field, so the next run's query would be worse than the first." % a["id"])
    enriched = [a for a in after if a.get("review_note")]
    assert enriched and all("found_title" in a["provenance"] for a in enriched), \
        "the archive's title was discarded rather than kept beside the curated name"


# --------------------------------------------------------------- the exit code means something

def test_a_run_whose_every_request_fails_does_not_report_success(rig, monkeypatch):
    monkeypatch.setattr(H, "fetch", lambda url, timeout=30: (_ for _ in ()).throw(
        ValueError("served HTML, not JSON")))
    rc = _run(monkeypatch, "--live")
    assert rc != 0, "the harvester fetched nothing and exited 0"


def test_three_consecutive_failures_stop_the_run(rig, monkeypatch, capsys):
    monkeypatch.setattr(H, "fetch", lambda url, timeout=30: (_ for _ in ()).throw(
        ValueError("blocked")))
    # Widen the fixture so there are more buildings than the breaker's threshold.
    doc = rig["doc"]()
    src = json.load(open(os.path.join(ROOT, "assets", "manifest.json")))
    doc["assets"] = [a for a in src["assets"]
                     if (a.get("provenance") or {}).get("building") and a.get("kind") == "photograph"][:400]
    open(rig["path"], "w").write(json.dumps(doc, indent=2))
    rc = _run(monkeypatch, "--live")
    assert rc == 4, rc
    assert "STOP" in capsys.readouterr().out
    assert len(rig["requests"]) == 0     # fetch was replaced; the breaker fired on failures


def test_live_refuses_without_a_contact(rig, monkeypatch):
    monkeypatch.setattr(H, "CONTACT", "")
    assert _run(monkeypatch, "--live") == 5


def test_dry_run_touches_neither_network_nor_file(rig, monkeypatch):
    before = open(rig["path"]).read()
    assert _run(monkeypatch, "--dry-run") == 0
    assert rig["requests"] == []
    assert open(rig["path"]).read() == before
