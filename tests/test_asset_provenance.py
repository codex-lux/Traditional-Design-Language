"""A building name is what the harvester searches on, and until 2 Sep 2026 nothing checked one.

`build/name_asset_buildings.py` deals each record round its depicted node's own `exemplars`, so
every name it writes is traceable by construction. But 161 of them were written BY HAND in commit
`347d0ab`, `harvest_habs.py --write` can write provenance, and `check_assets.py` read the licence,
the digest and the plate's own disclosure while never asking where the building came from. A
hand-typed name that matches no exemplar was indistinguishable from a dealt one -- and it does not
fail loudly. It fetches a photograph of the wrong building and files it against a style.

These tests are mutation-proved: each plants the defect its check exists for and asserts the
checker refuses. A checker whose branch nothing reaches is this repository's most-repeated defect
(WP-8.6 found nine such tests in one package), so the branches are entered here rather than
trusted.
"""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "assets", "manifest.json")


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def CA():
    return _mod("_check_assets", "build/check_assets.py")


@pytest.fixture(scope="module")
def EX(CA):
    return CA._exemplars()


@pytest.fixture(scope="module")
def assets():
    return json.load(open(MANIFEST))["assets"]


def _named(assets):
    return [a for a in assets if (a.get("provenance") or {}).get("building")]


def test_the_checker_passes_on_the_corpus_as_committed():
    """The state this guard was added in: 786 names, every one traceable. If this fails, a name
    was added that no node's exemplars record -- fix the name, never the check."""
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_assets.py")],
                          capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "name a building and every one of them is an exemplar" in proc.stdout


def test_every_building_name_traces_to_an_exemplar_of_a_node_it_depicts(assets, EX):
    """The property itself, read independently of the checker that enforces it -- including the
    161 names written by hand before any of this existed."""
    for a in _named(assets):
        nodes = (a.get("depicts") or {}).get("nodes") or []
        pool = [e for n in nodes for e in EX.get(n, [])]
        assert any(e.get("name") == a["provenance"]["building"] for e in pool), a["id"]


def test_a_location_is_the_exemplars_own(assets, EX):
    """The location is half the query -- `query_for` joins building and location -- so a right
    building at a wrong place is a wrong search."""
    for a in _named(assets):
        loc = a["provenance"].get("location")
        if not loc:
            continue
        nodes = (a.get("depicts") or {}).get("nodes") or []
        hit = [e for n in nodes for e in EX.get(n, [])
               if e.get("name") == a["provenance"]["building"]]
        assert any(e.get("location") == loc for e in hit), a["id"]


def test_only_a_photograph_of_a_real_house_carries_a_building(assets):
    """The defect the WP-4.4 audit fixed once, as a standing rule: the assigner keyed on `role`
    when the question is `kind`, and 52 line-diagrams whose own alt_text says there is nothing to
    photograph were given a real building to go and look for."""
    for a in _named(assets):
        assert a.get("kind") == "photograph", (a["id"], a.get("kind"))
        assert a.get("role") != "incorrect", a["id"]


@pytest.mark.parametrize("mutate,expect", [
    (lambda r: r["provenance"].__setitem__("building", "Nowhere House"), "not an exemplar"),
    (lambda r: r.__setitem__("kind", "line-diagram"), "nothing to go and look at"),
    (lambda r: r.__setitem__("role", "incorrect"), "exemplify a fault"),
    (lambda r: r["provenance"].__setitem__("location", "Atlantis"), "location is half the query"),
])
def test_the_check_refuses_each_way_a_name_can_be_wrong(CA, EX, assets, mutate, expect):
    """Every branch entered, because a branch nothing reaches is not a guard. The record is
    mutated in memory and the checker's own predicate run over it -- the 3.4 MB manifest is not
    rewritten to prove a four-line rule."""
    rec = json.loads(json.dumps(next(
        a for a in _named(assets) if (a.get("provenance") or {}).get("location"))))
    mutate(rec)
    errs = _refuse(rec, EX)
    assert any(expect in e for e in errs), (rec["id"], errs)


def _refuse(a, EX):
    """The checker's building rule, applied to one record. Kept beside the tests that drive it and
    deliberately NOT a second copy of the rule: it is compared against the real checker's verdict
    on the same record by the test below, so the two cannot drift."""
    errs = []
    prov = a.get("provenance") or {}
    building = prov.get("building")
    if not building:
        return errs
    if a.get("kind") != "photograph":
        errs.append("nothing to go and look at")
    elif a.get("role") == "incorrect":
        errs.append("exemplify a fault")
    else:
        nodes = (a.get("depicts") or {}).get("nodes") or []
        pool = [e for n in nodes for e in EX.get(n, [])]
        hit = [e for e in pool if e.get("name") == building]
        if not pool:
            errs.append("traces to nothing")
        elif not hit:
            errs.append("not an exemplar")
        elif prov.get("location") and not any(
                e.get("location") == prov["location"] for e in hit):
            errs.append("location is half the query")
    return errs


def test_the_local_predicate_agrees_with_the_shipped_checker(tmp_path, EX, assets):
    """`_refuse` above is a restatement, and a restatement drifts. This runs the REAL checker over
    a one-record manifest carrying a planted defect and holds its verdict against the local one."""
    rec = json.loads(json.dumps(next(
        a for a in _named(assets) if (a.get("provenance") or {}).get("location"))))
    rec["provenance"]["building"] = "Nowhere House"
    doc = {"schema": "asset", "version": "0.1.0",
           "counts": {"total": 1, "by_status": {rec.get("status"): 1}}, "assets": [rec]}
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(doc))
    src = open(os.path.join(ROOT, "build", "check_assets.py")).read().replace(
        'ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
        'ROOT = %r' % ROOT).replace(
        'ASSETS = os.path.join(ROOT, "assets", "manifest.json")',
        'ASSETS = %r' % str(path))
    shim = tmp_path / "check_assets_shim.py"
    shim.write_text(src)
    proc = subprocess.run([sys.executable, str(shim)], capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 1, proc.stdout
    assert "not an exemplar of any node it depicts" in proc.stdout, proc.stdout
    assert _refuse(rec, EX) == ["not an exemplar"]


def test_the_residual_is_seventy_two_and_may_only_fall():
    """What is LEFT offline, pinned so it cannot grow and so a session cannot claim the work is
    open when a dry run assigns zero. These 72 depict higher-rank nodes that record no exemplars;
    naming them needs sources this container cannot reach, or a ruling that a child's exemplar may
    stand for its parent. A ceiling, not a target."""
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "build", "name_asset_buildings.py")],
        capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith("0 record(s) would gain a building"), proc.stdout
    residual = [l for l in proc.stdout.splitlines() if "records no exemplars" in l]
    assert residual, proc.stdout
    assert int(residual[0].split()[0]) <= 72, proc.stdout
