import pytest

# Contributors without the web dependencies still get a green root suite: these
# tests only run where the workbench server can actually import.
pytest.importorskip("fastapi")
pytest.importorskip("jsonschema")


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from workbench.server.app import app
    return TestClient(app)
