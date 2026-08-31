"""The corpus's own asset files are served, and NOT from the bundle's namespace.

`/assets` is mounted on Vite's content-hashed output at workbench/app/dist/assets. The corpus
directory is also called `assets/`, and shares nothing else with it. An asset record's
`file.path` is repository-relative and begins "assets/", so the obvious `src="/" + file.path`
lands in the bundle mount, 404s, and does it behind ImmutableStatic's cache headers. The corpus
files are on `/corpus/` for that reason.

Written because eleven records gained real files in WP-4.4 and the first version of the image
branch pointed at the colliding path.
"""
import os
import sys

import pytest

# FOUR levels: this file is workbench/server/tests/, one deeper than app.py, whose own
# CORPUS_ASSETS uses three. Getting this wrong points at workbench/assets/, which does not exist.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from workbench.server.app import app  # noqa: E402

client = TestClient(app)


def test_a_generated_plate_is_served():
    r = client.get("/corpus/assets/generated/vignola-doric-cornice-profile.svg")
    assert r.status_code == 200, r.status_code
    assert r.content.lstrip().startswith(b"<svg"), r.content[:60]
    assert b"NOT A DRAWING OF A REAL BUILDING" in r.content, \
        "the plate is served without its own disclosure"


def test_every_sourced_records_file_actually_resolves():
    """A record claiming a file the server cannot serve is a broken image in the app, and the
    manifest is the only place that says where the file is."""
    import json
    manifest = json.load(open(os.path.join(ROOT, "assets", "manifest.json")))
    checked = 0
    for a in manifest["assets"]:
        f = a.get("file")
        if not f or not f.get("path"):
            continue
        checked += 1
        r = client.get("/corpus/" + f["path"])
        assert r.status_code == 200, "%s: /corpus/%s -> %s" % (a["id"], f["path"], r.status_code)
        assert int(r.headers.get("content-length") or len(r.content)) == f["bytes"], a["id"]
    assert checked == 73, checked


def test_the_bundle_namespace_is_not_the_corpus_namespace():
    """If this ever returns 200, the two mounts have been merged and a record's path is
    ambiguous between them."""
    r = client.get("/assets/generated/vignola-doric-cornice-profile.svg")
    assert r.status_code != 200, \
        "the corpus's assets are reachable under the bundle's mount; the namespaces have merged"


def test_the_corpus_mount_refuses_traversal():
    r = client.get("/corpus/assets/../../CLAUDE.md")
    assert r.status_code != 200, r.status_code
