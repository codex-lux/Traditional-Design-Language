"""A caller-supplied parti id must never open a file outside partis/.

The first fix for this landed in `core.place_plan` on 25 Aug and its comment claimed to
cover "/api/plan/evaluate and /api/drawings/{kind}". It covered the first. /api/drawings
and /api/export do not route through `place_plan` at all — `workbench/server/corpus.py`
carried its own two copies of the join, both unsanitised, and an audit found them still
live a day later.

So these tests are written against the property rather than against the one function that
had the bug: every path from a request body to the filesystem is confined, and no module
may spell the join itself. A test that only exercised `place_plan` is exactly the test
that passed while two other endpoints were open.

Each assertion below fails if `os.path.basename` is removed from `core.load_parti` — that
was checked by removing it, not assumed.
"""
import json
import os

import pytest

from workbench.server import corpus

core = corpus.core
ROOT = corpus.ROOT

# A traversal that lands on a file which really exists AND really parses as JSON. Pointing
# at a nonexistent path would pass whether or not the fix is present: load_parti returns
# None for a miss, so the test has to be able to tell "confined" from "read the wrong file".
ESCAPES = [
    pytest.param("../schema/plan.schema", id="relative"),
    pytest.param(os.path.join(ROOT, "schema", "plan.schema"), id="absolute"),
    pytest.param("../../etc/passwd", id="outside-the-repo"),
    pytest.param("..%2f..%2fschema%2fplan.schema", id="percent-encoded"),
]


def test_the_escape_targets_are_real():
    """Guard on the guard: if schema/plan.schema.json stopped existing or stopped parsing,
    every case below would pass vacuously — confined and not-found look identical here."""
    p = os.path.join(ROOT, "schema", "plan.schema.json")
    assert os.path.exists(p), "the traversal target must exist for these tests to mean anything"
    assert json.load(open(p)), "and must parse, or an unsanitised load would fail anyway"


@pytest.mark.parametrize("parti", ESCAPES)
def test_load_parti_is_confined(parti):
    assert core.load_parti(parti) is None


def test_load_parti_still_loads_a_real_parti():
    """The confinement must not have been bought by breaking the feature."""
    pt = core.load_parti("centre-passage-double-pile")
    assert pt and pt["id"] == "centre-passage-double-pile"


# --------------------------------------------------------------------------------------
# The endpoints. These are written as SPIES, not as status-code assertions, and the reason
# is worth recording: the first version of this file asserted `status_code != 500` on each
# endpoint, and all three of those assertions PASSED with the basename removed. A foreign
# JSON file does not crash the pipeline — the solver simply ignores a template whose keys
# it does not recognise — so there is no observable difference at the HTTP boundary to
# assert on. Three tests that could not fail, guarding the exact bug that had shipped.
#
# The property that was actually violated is narrower and testable: corpus.py did not CALL
# the confined loader, it spelled its own join. So each endpoint is asserted to route
# through `core.load_parti`, which fails the moment an inline join comes back.
# --------------------------------------------------------------------------------------

ENDPOINTS = [
    pytest.param("/api/drawings/plan", {"candidates": 1}, id="drawings"),
    pytest.param("/api/export/dxf", {"candidates": 1}, id="export"),
    # place=True deliberately: with place=False, evaluate() never calls place_plan and so
    # never loads a parti at all, and this test passed vacuously against an endpoint it
    # was not exercising.
    pytest.param("/api/plan/evaluate", {"place": True, "candidates": 1}, id="evaluate"),
]


@pytest.mark.parametrize("path,extra", ENDPOINTS)
def test_endpoint_routes_its_parti_through_the_confined_loader(client, monkeypatch, path, extra):
    seen = []
    real = core.load_parti

    def spy(parti):
        seen.append(parti)
        return real(parti)

    monkeypatch.setattr(core, "load_parti", spy)
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    client.post(path, json={"plan": plan, "parti": "../schema/plan.schema", **extra})
    assert seen == ["../schema/plan.schema"], (
        f"{path} did not reach core.load_parti — it is loading the parti some other way, "
        "which is how /api/drawings and /api/export stayed vulnerable after the first fix")


def test_no_module_spells_the_parti_join_itself():
    """The class, not the instance.

    Three copies of this join existed and two were wrong. `core.load_parti` is now the only
    one allowed; this fails when a fourth appears, in the way test_grammar_agreement.py
    fails when the citation grammar grows a fourth spelling.
    """
    import glob as _glob
    import re
    # sorted glob over the four source trees, which is the idiom tests/test_determinism.py
    # uses and enforces. os.walk from ROOT would have to prune node_modules, and wrapping it
    # in sorted() to satisfy that check materialises the whole tree BEFORE the prune can
    # run — deterministic and slow, which is not the trade this test wants.
    pattern = re.compile(r'["\']partis["\']\s*,\s*f?["\']\{')
    offenders = []
    for sub in ("build", "mcp_server", "workbench", "tests"):
        for path in sorted(_glob.glob(os.path.join(ROOT, sub, "**", "*.py"), recursive=True)):
            for n, line in enumerate(open(path, encoding="utf-8"), 1):
                if pattern.search(line):
                    offenders.append(f"{os.path.relpath(path, ROOT)}:{n}")
    # By FILE, not by file:line. The first version pinned "mcp_server/core.py:859" and went
    # red the moment an unrelated function was added above it — a guard that cries wolf on
    # every edit is a guard people learn to silence.
    files = sorted({o.rsplit(":", 1)[0] for o in offenders})
    assert files == ["mcp_server/core.py"], (
        "a parti id became a path outside core.load_parti — route it through that instead: "
        + ", ".join(offenders))
    assert len(offenders) == 1, (
        "core.load_parti should spell the join exactly once: " + ", ".join(offenders))
