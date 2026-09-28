import pytest

# Contributors without the web dependencies still get a green root suite: these
# tests only run where the workbench server can actually import.
pytest.importorskip("fastapi")
pytest.importorskip("jsonschema")


@pytest.fixture(autouse=True)
def _a_fresh_heavy_budget():
    """EVERY TEST STARTS WITH THE WHOLE HEAVY-CALL BUDGET (WP-14.6).

    `limits` keeps its counters in the process, 60 composing/checking calls an hour per identity,
    and the session's one TestClient is one identity -- so a test's verdict depended on how many
    heavy calls the tests before it in the order had made. At the phase's parent
    `test_a_parti_record_is_refused_not_used_as_the_template[revise]` was answered 429 where it
    asserts 422, a refusal of a parti RECORD it never reached; WP-14.4 added heavy calls to
    `test_drawing_set_one_building.py` and `[critique]` joined it. A red that depends on the
    order a suite runs in is a red nobody can act on. The files that test the limiter itself
    reset it inside their own tests, as they always have; nothing here stops them."""
    try:
        from workbench.server import limits
    except Exception:                      # noqa: BLE001 -- the suite's own skips handle this
        yield
        return
    limits.reset()
    yield


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from workbench.server.app import app
    return TestClient(app)
