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
    """Every building name in the manifest traces to an exemplar of a node the record depicts.
    If this fails, a name was added that no node's exemplars record -- fix the name, never the
    check. No count here: it read 786 when the guard was added and 858 after WP-11.6, and
    `check_counts.computed()` owns `image_building_named`."""
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


def _run_checker_over(rec, tmp_path, label):
    """Run the REAL `build/check_assets.py` over a one-record manifest holding `rec`.

    THE POINT, AND IT IS WHY THIS REPLACED A LOCAL COPY OF THE RULE. The first version of this
    file carried a `_refuse()` restatement and drove three of its four mutations through THAT,
    not through the checker. Deleting the entire provenance block from `build/check_assets.py`
    left nine of these ten tests green -- the exact "test that could not fail" WP-8.6 found nine
    of, in a file whose own docstring cites WP-8.6 as its reason for existing. An adversarial
    audit caught it. Every branch is driven through the shipped binary now.

    The manifest is a one-record temp file and ROOT is pinned to the real repo, so the schema and
    the corpus's exemplars are the real ones while the record under test is ours.
    """
    doc = {"schema": "asset", "version": "0.1.0",
           "counts": {"total": 1, "by_status": {rec.get("status"): 1}}, "assets": [rec]}
    path = tmp_path / ("manifest_%s.json" % label)
    path.write_text(json.dumps(doc))
    src = open(os.path.join(ROOT, "build", "check_assets.py")).read().replace(
        'ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
        'ROOT = %r' % ROOT).replace(
        'ASSETS = os.path.join(ROOT, "assets", "manifest.json")', 'ASSETS = %r' % str(path))
    shim = tmp_path / ("shim_%s.py" % label)
    shim.write_text(src)
    return subprocess.run([sys.executable, str(shim)], capture_output=True, text=True, cwd=ROOT)


@pytest.mark.parametrize("label,mutate,expect", [
    ("untraceable", lambda r: r["provenance"].__setitem__("building", "Nowhere House"),
     "not an exemplar of any node it depicts"),
    ("wrongkind", lambda r: r.__setitem__("kind", "line-diagram"),
     "nothing to go and look at"),
    ("faultrole", lambda r: r.__setitem__("role", "incorrect"),
     "exemplify a fault"),
    ("badplace", lambda r: r["provenance"].__setitem__("location", "Atlantis"),
     "location is half the query"),
])
def test_the_check_refuses_each_way_a_name_can_be_wrong(assets, tmp_path, label, mutate, expect):
    """Every branch entered THROUGH THE SHIPPED CHECKER, because a branch only a test copy reaches
    is not a guard on anything. Each mutation must make `check_assets.py` exit 1 and say why."""
    rec = json.loads(json.dumps(next(
        a for a in _named(assets) if (a.get("provenance") or {}).get("location"))))
    mutate(rec)
    proc = _run_checker_over(rec, tmp_path, label)
    # ASSERT ON THE MESSAGE, NOT THE EXIT CODE. A one-record manifest also orphans the 73 SVGs
    # on disk, so this harness exits 1 whatever the record says -- the control test below proves
    # exactly that, and it is the reason the exit code is worthless as evidence here. The
    # provenance rule's own sentence is the only thing that distinguishes the branches.
    assert expect in proc.stdout, (label, proc.stdout, proc.stderr)


def test_the_unmutated_record_passes_the_same_harness(assets, tmp_path):
    """The control. Without it the four mutations above could all be passing because the harness
    itself is broken -- a one-record manifest that fails for an unrelated reason would satisfy
    every one of them. This is the arm of the experiment that proves the instrument works."""
    rec = json.loads(json.dumps(next(
        a for a in _named(assets) if (a.get("provenance") or {}).get("location"))))
    proc = _run_checker_over(rec, tmp_path, "control")
    # It exits 1 -- the one-record manifest orphans every generated SVG -- and that is precisely
    # the point: the exit code carries no information here, so the four mutations above must be
    # (and are) judged on the rule's own message. NONE of those messages may appear for a record
    # that is correct.
    for phrase in ("not an exemplar of any node it depicts", "nothing to go and look at",
                   "exemplify a fault", "location is half the query"):
        assert phrase not in proc.stdout, (phrase, proc.stdout)


def test_deleting_the_provenance_block_is_caught(assets, tmp_path):
    """THE MUTATION THE AUDIT USED, kept as a test. Strip the building rule out of the checker's
    source and the untraceable record must stop being refused -- which proves these tests are
    bound to that block and not to something else in the file."""
    rec = json.loads(json.dumps(next(
        a for a in _named(assets) if (a.get("provenance") or {}).get("location"))))
    rec["provenance"]["building"] = "Nowhere House"
    src = open(os.path.join(ROOT, "build", "check_assets.py")).read()
    start = src.index('        building = prov.get("building")')
    end = src.index('        lic = prov.get("license")')
    neutered = (src[:start] + '        building = None' + chr(10) + src[end:]).replace(
        'ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))', 'ROOT = %r' % ROOT)
    doc = {"schema": "asset", "version": "0.1.0",
           "counts": {"total": 1, "by_status": {rec.get("status"): 1}}, "assets": [rec]}
    path = tmp_path / "m.json"
    path.write_text(json.dumps(doc))
    neutered = neutered.replace('ASSETS = os.path.join(ROOT, "assets", "manifest.json")',
                                'ASSETS = %r' % str(path))
    shim = tmp_path / "neutered.py"
    shim.write_text(neutered)
    proc = subprocess.run([sys.executable, str(shim)], capture_output=True, text=True, cwd=ROOT)
    assert "not an exemplar of any node it depicts" not in proc.stdout, (
        "the provenance block was removed and the checker still refused the record -- these "
        "tests are not bound to the block they claim to guard", proc.stdout)


def test_no_record_is_left_unnamed_for_want_of_an_exemplar():
    """THE RESIDUAL IS ZERO AND THE PIN IS TIGHT AT ZERO. It was 72 -- records depicting
    higher-rank nodes that recorded no exemplars, which WP-4.4 could not name offline. This test
    asked for `<= 72` and, because the reason line only prints when the count is non-zero, ALSO
    asserted the line existed; when WP-11.6 took the count to zero the ceiling was satisfied and
    the test failed on its own scaffolding.

    The docstring said naming them needed "sources this container cannot reach, or a ruling that a
    child's exemplar may stand for its parent". That ruling arrived -- Ruling B, 5 Sep 2026 -- and
    was executed: every family carries type specimens derived from its members' icons, so the 18
    nodes had exemplars to deal from and `name_asset_buildings.py` named all 72 on the first run.
    Kept in the past tense rather than left as advice for a decision nobody can make again.

    A ceiling that has reached its floor is pinned tight, as `exemplars_unresearched` is. A node
    whose asset records depict it and whose family carries no specimens goes red here, which is
    the signal wanted -- and the remedy is one command, `build/family_specimens.py --apply`."""
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "build", "name_asset_buildings.py")],
        capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith("0 record(s) would gain a building"), proc.stdout
    # The bucket is printed only when non-empty, so its ABSENCE is the zero. Read it that way
    # rather than requiring the line, which is exactly how this test came to fail on success.
    residual = [l for l in proc.stdout.splitlines() if "records no exemplars" in l]
    assert not residual, proc.stdout
    # Non-vacuity: the reason breakdown must be there at all, or a program that printed nothing
    # after its first line would satisfy the assertion above by saying nothing.
    assert "still unnamed, by reason:" in proc.stdout, proc.stdout
