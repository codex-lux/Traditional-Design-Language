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
