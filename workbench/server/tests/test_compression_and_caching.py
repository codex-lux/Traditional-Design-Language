"""What the server stops re-doing, and the one thing compression must not touch.

Nothing here compressed anything: the app bundle, the 214 KB search index, every corpus
response and the atlas's 1.17 MB fine coastline tier all went out whole — three times the
bytes on a platform that bills egress, and three times the transfer time on every call.

And several structures were rebuilt per request that cannot change under a running server.
"""
import importlib.util
import json
import os

from workbench.server import corpus

core = corpus.core
ROOT = corpus.ROOT


# ------------------------------------------------------------------ compression

def test_a_large_json_response_is_compressed(client):
    r = client.get("/api/search/index", headers={"Accept-Encoding": "gzip"})
    assert r.status_code == 200
    assert r.headers.get("content-encoding") == "gzip", (
        "the largest routine response on the server is going out uncompressed")


def test_the_minimum_size_is_configured_even_though_nothing_is_under_it(client):
    """A minimum exists because below it gzip costs CPU and adds bytes.

    Worth recording that no current endpoint is under it: the smallest JSON response on the
    server is /api/health at ~1.1 KB, so in practice every API response is compressed. The
    first version of this test asserted /api/health was NOT compressed, on the assumption
    that a health check is small — it carries corpus counts, auth state, limits state and
    the MCP mount state, and it is not.
    """
    import inspect
    from workbench.server import app as app_mod
    sig = inspect.signature(app_mod.GZipExceptSSE.__init__)
    assert sig.parameters["minimum_size"].default > 0
    assert len(client.get("/api/health").content) > sig.parameters["minimum_size"].default


def test_the_sse_paths_bypass_the_compressor_entirely():
    """THE exemption, and the reason this middleware is not just GZipMiddleware.

    Starlette's gzip buffers a streaming response, which turns a live progress line into a
    long pause and then everything at once. The rail's whole point is that it answers as it
    thinks, and compose progress is only progress if it arrives during the compose.

    Asserted on the DISPATCH, not on a response header, and that distinction is the finding.
    The first version opened a real event stream and checked content-encoding was not gzip —
    and it passed with the exemption deleted, because Starlette holds a streaming response
    uncompressed until it exceeds minimum_size and the first SSE chunk is a few dozen bytes.
    A test that reads the right header for the wrong reason certifies nothing.
    """
    import asyncio

    from workbench.server import app as app_mod

    routed = []

    async def sentinel(scope, receive, send):
        routed.append(scope["path"])

    mw = app_mod.GZipExceptSSE(sentinel)
    mw.zipped = _Marker(routed, "ZIPPED")

    async def go(path):
        await mw({"type": "http", "path": path, "headers": []}, None, None)

    for path, expected in [("/api/rail/messages", path_plain := True),
                           ("/api/jobs/abc123/events", True),
                           ("/api/search/index", False),
                           ("/api/jobs/abc123", False)]:
        routed.clear()
        asyncio.get_event_loop_policy().new_event_loop().run_until_complete(go(path))
        went_plain = routed == [path]
        assert went_plain is expected, (
            f"{path} went to the {'compressor' if not went_plain else 'plain app'}, "
            f"which is {'wrong' if expected else 'wrong'} for an "
            f"{'SSE' if expected else 'ordinary'} route")


class _Marker:
    """Stands in for the gzip branch so the dispatch is observable without compressing."""

    def __init__(self, log, tag):
        self.log, self.tag = log, tag

    async def __call__(self, scope, receive, send):
        self.log.append(self.tag)


# ------------------------------------------------------------------ parse-once caches

def test_the_plan_schema_is_parsed_once():
    """check_plan re-read and re-parsed plan.schema.json on EVERY call, and check_plan is
    what /api/plan/evaluate runs behind a 400 ms debounce on every wall drag."""
    core.schema.cache_clear()
    a = core.schema("plan")
    b = core.schema("plan")
    assert a is b, "the schema is being re-parsed per call"
    assert core.schema.cache_info().hits >= 1


def test_the_schema_endpoints_hand_out_a_copy():
    """The cached object is shared, so anything handed onward must be copied or the next
    caller inherits the last one's edits."""
    core.schema.cache_clear()
    shared = core.schema("plan")
    handed = core.plan_schema()["schema"]
    assert handed == shared and handed is not shared


def test_no_module_re_reads_a_schema_file_per_request():
    """The class, not the instance: six sites parsed these two files."""
    import glob as _glob
    import re
    pattern = re.compile(r'json\.load\(open\(.*schema.*\.schema\.json')
    offenders = []
    for sub in ("mcp_server", "workbench"):
        for path in sorted(_glob.glob(os.path.join(ROOT, sub, "**", "*.py"), recursive=True)):
            for n, line in enumerate(open(path, encoding="utf-8"), 1):
                if pattern.search(line):
                    offenders.append(f"{os.path.relpath(path, ROOT)}:{n}")
    assert len(offenders) <= 1, (
        "a schema file is parsed outside core.schema(): " + ", ".join(offenders))


def test_phylogeny_is_built_once(monkeypatch):
    """157 KB rebuilt from core._data() per request, for a structure that cannot change
    under a running server. Same bug as the search index, one endpoint over.

    The second call is made with core._data BOOBY-TRAPPED, because asserting that
    `_PHYLOGENY is not None` afterwards does not test the cache — the uncached version also
    assigns it on the way out, so that assertion passed with the early return deleted. The
    only proof the cache is READ is that a rebuild would now be impossible.
    """
    corpus.reset_phylogeny()
    a = corpus.phylogeny()

    def boom():
        raise AssertionError("phylogeny() rebuilt from the corpus instead of using its cache")

    monkeypatch.setattr(core, "_data", boom)
    b = corpus.phylogeny()
    assert a == b
    assert a is not b, "callers must not share the cached structure"


def test_invalidate_clears_every_cache_it_claims_to():
    """/api/dev/reload exists so on-disk edits are seen. A cache it forgets is a cache that
    serves stale corpus data for the life of the process."""
    corpus.phylogeny()
    core.schema("plan")
    assert corpus._PHYLOGENY is not None
    corpus.invalidate()
    assert corpus._PHYLOGENY is None, "invalidate() left the phylogeny cached"
    assert core.schema.cache_info().currsize == 0, "invalidate() left the schemas cached"
    assert corpus._SEARCH_INDEX is None


# ------------------------------------------------------------------ the rail's client

def test_the_anthropic_client_is_pooled(monkeypatch):
    """It was constructed per turn, and every anthropic.Anthropic() builds its own
    httpx.Client with its own connection pool — a fresh TCP handshake and TLS negotiation
    before the first token of every turn."""
    from workbench.server import rail
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-not-a-real-key")
    rail._POOLED.clear()
    monkeypatch.setattr(rail, "_client_factory", None)
    assert rail._client() is rail._client(), "a client per turn is a handshake per turn"


def test_a_rotated_key_gets_a_new_client(monkeypatch):
    """Pooling must not become the one reader that disagrees with the rest: key() is read
    from the environment at call time everywhere else in rail.py, deliberately."""
    from workbench.server import rail
    rail._POOLED.clear()
    monkeypatch.setattr(rail, "_client_factory", None)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-first")
    first = rail._client()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-second")
    assert rail._client() is not first, "a rotated key kept serving the old client"


# ------------------------------------------------------------------ static assets

def test_hashed_assets_are_immutable_and_index_is_not():
    """Vite content-hashes every name under /assets, so the bytes at a URL can never change.
    index.html must NOT carry it or a deploy would never reach anyone."""
    from workbench.server import app as app_mod
    assert issubclass(app_mod.ImmutableStatic, app_mod.StaticFiles)
    import inspect
    src = inspect.getsource(app_mod.ImmutableStatic)
    assert "immutable" in src and "max-age=31536000" in src
    spa = inspect.getsource(app_mod)
    assert 'app.mount("/assets", ImmutableStatic(' in spa, (
        "the immutable cache is not actually mounted")
