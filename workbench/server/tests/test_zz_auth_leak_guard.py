"""No test may leave this process gated behind it.

OQ 64. `test_mcp_http.py`'s `live` fixture was session-scoped and set
WORKBENCH_API_TOKEN directly, restoring it only at session teardown — so from the moment
its first test ran, `auth.required()` was true for the rest of the process and every test
file sorting after it ran against a gated server. A plain `client.get("/api/…")` in one
got a 401 that had nothing to do with the route under test. It was found by accident:
`test_search_index.py` passed alone and failed in the suite.

The class is worth a guard rather than a memory, because the failure mode is silent in the
worst way — it does not break the file that causes it, it breaks whichever file happens to
sort after it, and it moves when files are renamed.

THE `zz` IN THE FILENAME IS LOAD-BEARING, which is why it is worth explaining rather than
tidying away. pytest collects files in directory order, so a guard against "something
earlier leaked" only works if it runs after everything it guards. Named `test_no_auth_leak`
it sorted between `test_mcp_http` and `test_rail_loop`, and would have missed a leak from
either of the two files after it. `test_zz_…` sorts last, and stays last as files are
added, which no more descriptive name can promise.
"""
import os

import pytest

pytest.importorskip("fastapi")

from workbench.server import auth  # noqa: E402

GATE_VARS = ("WORKBENCH_PASSWORD", "WORKBENCH_API_TOKEN")


def test_no_earlier_test_left_this_process_gated():
    leaked = {k: os.environ[k] for k in GATE_VARS if os.environ.get(k)}
    assert not leaked, (
        f"a test that ran before this one left {sorted(leaked)} set in os.environ, so "
        f"every later test file is running against a gated server and any unauthenticated "
        f"request in one will get a 401 unrelated to its own route. Scope the variable to "
        f"the test that needs it — monkeypatch.setenv restores after each test — rather "
        f"than setting it in a module- or session-scoped fixture. See OQ 64.")
    assert not auth.required(), \
        "auth.required() is true with no gate variable set, which means it is reading " \
        "configuration from somewhere this guard does not know about"


def test_the_guard_would_actually_catch_it(monkeypatch):
    """A guard that cannot fail is not a guard. This proves the detection works, in the
    one way that is safe: set the variable through monkeypatch, observe that the check
    would fire, and let monkeypatch put it back."""
    monkeypatch.setenv("WORKBENCH_API_TOKEN", "leaked")
    leaked = {k: os.environ[k] for k in GATE_VARS if os.environ.get(k)}
    assert leaked == {"WORKBENCH_API_TOKEN": "leaked"}
    assert auth.required()


# ------------------------------------------------------------------ WP-14.3: the one sentence
# RULED 24 Sep 2026: the Gate says one sentence. Exactly `/api/glossary/about-tdl` answers a
# stranger, and nothing else under `/api/glossary` does. These live HERE rather than beside the
# glossary routes because this file is where a reader looks for what a stranger can reach, and
# because each sets its gate variable with monkeypatch and so cannot be the leak the two tests
# above exist to catch -- the file still ends with the process ungated.
#
# THE PREFIX MUTATION IS THE ONE THESE ARE WRITTEN AGAINST. The gate compares whole paths with
# `in`; a gate that compared with `startswith` would open `/api/glossary/about-tdl/` and
# `/api/glossary/about-tdl-anything` while every term id in the corpus stayed shut, so asking only
# the real ids would pass over it. The two longer paths are asked by name for that reason.

OPEN_EXACTLY = ("/api/health", "/api/login", "/api/glossary/about-tdl")


def _stranger(monkeypatch):
    from fastapi.testclient import TestClient
    from workbench.server.app import app
    monkeypatch.setenv("WORKBENCH_PASSWORD", "hunter2")
    monkeypatch.delenv("WORKBENCH_API_TOKEN", raising=False)
    assert auth.required(), "the premise: this server is gated"
    return TestClient(app)


def test_the_open_paths_are_exactly_the_ruled_three():
    assert auth.OPEN_PATHS == OPEN_EXACTLY, auth.OPEN_PATHS


def test_signed_out_the_about_record_answers_and_says_only_its_own_words(monkeypatch):
    c = _stranger(monkeypatch)
    r = c.get("/api/glossary/about-tdl")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["term"]["id"] == "about-tdl"
    assert body["confusable"] == [] and body["see"] == [], (
        "the ungated body resolved another record -- build/check_glossary.py forbids about-tdl "
        "a see and a confusable_with so that it cannot")
    assert body["term"]["reads"] == ["VISION.md"]


def test_signed_out_the_glossary_and_every_other_term_are_refused(monkeypatch):
    from workbench.server import corpus
    c = _stranger(monkeypatch)
    ids = sorted(corpus.core._data()["glossary"])
    assert "about-tdl" in ids and len(ids) > 1, "the premise: there is something else to refuse"
    asked = ["/api/glossary", "/api/glossary/"]
    asked += ["/api/glossary/" + i for i in ids if i != "about-tdl"]
    # the shapes a prefix gate would open, and a miss, which must not answer a stranger with a
    # did_you_mean list of real ids
    asked += ["/api/glossary/about-tdl/", "/api/glossary/about-tdl-anything",
              "/api/glossary/about-tdl.json", "/api/glossary/nosuch", "/api/glossary/about"]
    leaked = [(p, s) for p in asked if (s := c.get(p).status_code) != 401]
    assert not leaked, f"answered a stranger: {leaked}"


def test_signed_in_the_glossary_answers_as_usual(monkeypatch):
    """The control for the test above: the 401s are the gate and not a broken route."""
    c = _stranger(monkeypatch)
    token = auth.mint()
    c.cookies.set(auth.COOKIE, token)
    assert c.get("/api/glossary").status_code == 200
    assert c.get("/api/glossary/judgment-unjudged").status_code == 200
