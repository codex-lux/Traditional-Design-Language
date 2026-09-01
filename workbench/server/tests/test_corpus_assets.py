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


def test_the_manifest_is_not_served_on_the_ungated_route():
    """THE MOUNT WAS THE WHOLE `assets/` DIRECTORY AND THIS IS WHY THAT MATTERED.

    The auth gate matches only `/api/` and `/mcp`, so `/api/assets` answered 401 while
    `/corpus/assets/manifest.json` answered 200 with 3.4 MB -- all 1,850 records, every
    provenance block, review note, habs_number and hand-assigned building name -- unbounded,
    unprojected and unauthenticated. It also cost 33.5 ms of server CPU per request because
    3.4 MB compresses inline on the event loop, so 31.5 requests a second from one anonymous
    caller saturated the deployment's single core.

    The mount is `assets/generated` now. Whatever answers this URL must not be corpus records."""
    r = client.get("/corpus/assets/manifest.json")
    assert b'"provenance"' not in r.content and b'"assets"' not in r.content, \
        "the manifest is reachable on the ungated corpus route"
    assert len(r.content) < 50_000, "something large is served here: %d bytes" % len(r.content)


def test_nothing_outside_generated_is_reachable_under_corpus():
    """`harvest_habs.py` exists to put downloaded archive material into this corpus. Mounting
    the parent directory would have made the first such file same-origin active content on this
    origin the day it landed. Only the engine's own output is served."""
    import json as _json
    import os as _os
    root = _os.path.join(ROOT, "assets")
    for name in sorted(_os.listdir(root)):
        if name == "generated":
            continue
        r = client.get("/corpus/assets/" + name)
        assert b'"assets"' not in r.content, "%s is reachable under /corpus/" % name


def test_the_plates_are_served_inert():
    """SVG on this origin executes in this origin if a browser is navigated at it directly."""
    r = client.get("/corpus/assets/generated/vignola-doric-cornice-profile.svg")
    assert r.status_code == 200
    assert r.headers.get("x-content-type-options") == "nosniff"
    assert "sandbox" in (r.headers.get("content-security-policy") or "")


def test_the_corpus_route_is_exempt_from_gzip():
    """Same reason `/assets/` is exempt: FileResponse streams 64 KiB chunks and GZipMiddleware
    only offloads above 128 KiB, so compression here runs on the event loop."""
    from workbench.server.app import GZipExceptSSE
    assert "/corpus/" in GZipExceptSSE.EXEMPT_PREFIXES
    r = client.get("/corpus/assets/generated/vignola-doric-cornice-profile.svg",
                   headers={"Accept-Encoding": "gzip"})
    assert r.headers.get("content-encoding") is None


def test_the_bundle_namespace_is_not_the_corpus_namespace():
    """If this ever returns 200, the two mounts have been merged and a record's path is
    ambiguous between them."""
    r = client.get("/assets/generated/vignola-doric-cornice-profile.svg")
    assert r.status_code != 200, \
        "the corpus's assets are reachable under the bundle's mount; the namespaces have merged"


def test_the_corpus_mount_refuses_traversal():
    """ASSERT ON THE BYTES, NOT ON THE STATUS, and the first version of this got it wrong.

    It asserted `status_code != 200` for `/corpus/assets/../../CLAUDE.md`, and passed -- but only
    because `workbench/app/dist` did not exist in the environment it was written in, so app.py
    had not mounted its SPA catch-all. Build the app, as CI does, and the same request returns
    200: the HTTP client normalises `../..` before sending, so it never reaches `/corpus/` at all
    and lands on the catch-all as `/CLAUDE.md`, which serves index.html by design.

    A status code could therefore mean "refused" or "SPA shell", and the test could not tell them
    apart -- it was pinned to an accident of the environment. What actually matters is that no
    repository file OUTSIDE assets/ ever comes back, so that is what is asserted, and the encoded
    forms (which DO reach the mount, because the client cannot normalise them away) are covered
    too."""
    sentinel = "Traditional Design Language"      # appears in CLAUDE.md, not in index.html
    for url in ("/corpus/assets/generated/../../../CLAUDE.md",
                "/corpus/assets/generated/%2e%2e/%2e%2e/%2e%2e/CLAUDE.md",
                "/corpus/assets/generated/..%2f..%2f..%2fCLAUDE.md",
                "/corpus/assets/generated/....//....//....//CLAUDE.md",
                "/corpus/assets/generated/%2e%2e/manifest.json",
                "/corpus/assets/../../CLAUDE.md"):
        r = client.get(url)
        assert not (r.status_code == 200 and sentinel.encode() in r.content
                    and not r.content.lstrip().lower().startswith(b"<!doctype")), \
            "%s served a repository file outside assets/generated/" % url

    # The encoded forms DO reach the mount (the client cannot normalise them away) and must be
    # refused there. The prefix has to be the REAL mount point: when the mount was narrowed from
    # `assets/` to `assets/generated`, an encoded URL under the old prefix stopped reaching any
    # mount at all and fell through to the SPA, so an assertion written against the old prefix
    # started passing for a reason that had nothing to do with traversal.
    assert client.get(
        "/corpus/assets/generated/%2e%2e/%2e%2e/CLAUDE.md").status_code == 404
    assert client.get("/corpus/assets/generated/%2e%2e/manifest.json").status_code == 404


def test_the_spa_catch_all_is_mounted_when_the_app_is_built():
    """The test above is only meaningful when the catch-all exists -- without it the traversal
    URLs 404 for a reason that has nothing to do with the corpus mount, and the assertions pass
    vacuously. This states which regime the suite is running in."""
    import os as _os
    from workbench.server import app as _appmod
    built = _os.path.isdir(_appmod.APP_DIST)
    if not built:
        pytest.skip("workbench/app/dist absent: the SPA catch-all is not mounted, so the "
                    "traversal assertions above are not exercising the case that matters")
    assert client.get("/definitely-not-a-route").status_code == 200
