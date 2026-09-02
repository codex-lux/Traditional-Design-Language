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
# EVERY entry must resolve, under the PRE-FIX spelling, to a file that exists and parses as
# JSON. Two of the original four did not: "../../etc/passwd" lands one level above the repo on
# a path that does not exist, and "..%2f..%2f..." contains no "/" at all so os.path.basename is
# the identity function on it and nothing in this stack percent-decodes. Both returned None
# because the file was MISSING, not because it was refused — they passed identically with the
# basename removed. The docstring one line above them warned about precisely that, which is
# how they got written anyway.
ESCAPES = [
    pytest.param("../schema/plan.schema", id="relative"),
    pytest.param(os.path.join(ROOT, "schema", "plan.schema"), id="absolute"),
    pytest.param("../plans/tidewater-georgian-careful", id="sibling-directory"),
    pytest.param("../../Traditional-Design-Language/schema/brief.schema", id="up-and-back"),
    pytest.param("./../schema/plan.schema", id="dot-slash-prefixed"),
]


@pytest.mark.parametrize("parti", ESCAPES)
def test_each_escape_target_would_really_be_read_without_the_fix(parti):
    """The guard on the guard, and it has teeth now.

    For a confinement test to mean anything, the unsanitised path must land on a file that
    EXISTS and PARSES — otherwise `None` proves a miss rather than a refusal. This asserts
    that for every parameter, so a case can never again be decorative.
    """
    unsafe = os.path.join(ROOT, "partis", f"{parti}.json")
    assert os.path.exists(unsafe), (
        f"{parti!r} does not resolve to a real file ({unsafe}) — without the fix it would "
        "return None anyway, so it cannot distinguish confinement from a miss")
    assert json.load(open(unsafe)), "and it must parse, or an unsanitised load would fail too"


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
    # WP-9.3: the analyst places once through critique.py, which loads the parti by id
    pytest.param("/api/plan/critique", {"place": True, "candidates": 1, "engine": "heuristic"}, id="critique"),
]


@pytest.mark.parametrize("path,extra", ENDPOINTS)
def test_endpoint_routes_its_parti_through_the_confined_loader(client, monkeypatch, path, extra):
    seen = []
    real = core.load_parti

    def spy(parti):
        seen.append(parti)
        return real(parti)

    monkeypatch.setattr(core, "load_parti", spy)
    # WP-9.3: build/critique.py reaches core through modcache BY PATH, which is a second
    # module object from the server's `import core` (same file, two instances -- named in
    # the WP-9.3 report and left for the audit). The confined loader is the one it calls;
    # the spy has to be installed on that instance too or this case fails for a reason that
    # is not a traversal.
    import sys
    build = os.path.join(ROOT, "build")
    if build not in sys.path:
        sys.path.insert(0, build)
    import modcache
    tdlcore = modcache.load("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))
    if tdlcore is not core:
        monkeypatch.setattr(tdlcore, "load_parti", spy)
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    client.post(path, json={"plan": plan, "parti": "../schema/plan.schema", **extra})
    assert seen == ["../schema/plan.schema"], (
        f"{path} did not reach core.load_parti — it is loading the parti some other way, "
        "which is how /api/drawings and /api/export stayed vulnerable after the first fix")


PARTI_JOIN = None      # compiled below; several spellings, see the test


def _parti_join_sites(subtrees):
    """Every line in `subtrees` that turns something into a path under partis/."""
    import glob as _glob
    import re
    # The first version matched only `"partis", f"{`. The form most likely to appear next —
    # f"{ROOT}/partis/{x}.json" — is used by seven files in build/ and sailed straight through,
    # so the docstring's promise that "this fails when a fourth appears" held for exactly one
    # spelling. sorted glob is the idiom tests/test_determinism.py enforces.
    pattern = re.compile(
        r'["\']partis["\']\s*,\s*(f?["\']\{|[A-Za-z_])'    # os.path.join(ROOT, "partis", x)
        r'|/partis/\{'                                      # f"{ROOT}/partis/{x}.json"
        r'|["\']partis["\']\s*\)\s*,\s*[A-Za-z_]')        # join(join(ROOT,"partis"), x)
    out = []
    for sub in subtrees:
        for path in sorted(_glob.glob(os.path.join(ROOT, sub, "**", "*.py"), recursive=True)):
            if os.path.basename(path) == os.path.basename(__file__):
                continue                       # this file quotes the spellings to look for them
            for n, line in enumerate(open(path, encoding="utf-8"), 1):
                if pattern.search(line):
                    out.append((os.path.relpath(path, ROOT), n, line.strip()))
    return out


def test_no_server_reachable_module_spells_the_parti_join_itself():
    """The class, not the instance, scoped to the code a REQUEST can reach.

    Three copies of this join existed and two were wrong. `core.load_parti` is now the only
    one allowed anywhere a request body can reach, and this fails when a fourth appears — the
    way test_grammar_agreement.py fails when the citation grammar grows a fourth spelling.
    """
    sites = _parti_join_sites(("mcp_server", "workbench"))
    files = sorted({f for f, _n, _l in sites})
    assert files == ["mcp_server/core.py"], (
        "a parti id became a path outside core.load_parti — route it through that instead: "
        + ", ".join(f"{f}:{n}" for f, n, _l in sites))
    assert len(sites) == 1, (
        "core.load_parti should spell the join exactly once: "
        + ", ".join(f"{f}:{n}" for f, n, _l in sites))


def test_the_build_cli_parti_joins_are_all_argparse_fed():
    """build/ has seven of these and they are deliberately NOT offenders — but that has to be
    checked rather than assumed, or the exemption becomes the hiding place.

    Each is `json.load(open(f"{ROOT}/partis/{a.parti}.json"))` inside a module's main(), where
    `a` is an argparse namespace: the path comes from the operator's own command line, not from
    a request body. Nothing in workbench/ or mcp_server/ calls these main() functions — the
    server imports these modules and calls their library functions directly. If one of these
    lines ever reads from anything but `a.<name>`, it has stopped being a CLI path and this
    fails.
    """
    sites = _parti_join_sites(("build",))
    assert sites, "the build/ CLI joins vanished — if they moved, re-scope the guard above"
    for f, n, line in sites:
        assert "a.parti" in line, (
            f"{f}:{n} builds a parti path from something other than an argparse namespace: "
            f"{line!r} — if a request can reach it, it must go through core.load_parti")


def test_the_schema_loader_confines_its_name_too():
    """core.schema() was added in the very commit that reduced the parti join to one
    sanitised site, and it reintroduced the same shape one screen above load_parti's
    docstring — os.path.join(ROOT, "schema", f"{name}.schema.json"), no basename.

    NOT A LIVE HOLE, and this test says so rather than implying otherwise. Two things confine
    it already: no caller passes user input (it is schema("plan") and schema("brief")), and
    every *.schema.json in the repo lives in schema/, so the mandatory suffix means a
    traversal cannot reach a file the plain join would not have reached anyway. Checked, not
    assumed.

    The basename is therefore consistency and defence in depth, and the assertion is
    structural for the same reason — there is no behavioural difference to observe. What it
    buys is that the rule "a caller-supplied name is basenamed before it becomes a path" holds
    everywhere in this module, so the next helper written from this one inherits it.
    """
    import inspect
    src = inspect.getsource(core.schema)
    doc = inspect.getdoc(core.schema) or ""
    for line in doc.splitlines():
        src = src.replace(line, "")
    assert "os.path.basename" in src, (
        "core.schema builds a path from its argument without confining it")
    # and the confinement must not have broken the two real lookups
    assert core.schema("plan")["type"] == "object"
    assert core.schema("brief")
    # a name that resolves nowhere still fails loudly rather than silently returning nothing
    import pytest as _pytest
    with _pytest.raises(FileNotFoundError):
        core.schema("../plans/tidewater-georgian-careful")
