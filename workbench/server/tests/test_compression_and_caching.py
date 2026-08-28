"""What the server stops re-doing, and the one thing compression must not touch.

Nothing here compressed anything: the app bundle, the 214 KB search index, every corpus
response and the atlas's 1.17 MB fine coastline tier all went out whole — three times the
bytes on a platform that bills egress, and three times the transfer time on every call.

And several structures were rebuilt per request that cannot change under a running server.
"""
import importlib.util
import json
import os

# This module calls `pytest.skip` at four places and for a while imported nothing to call it
# with, so every COULD-NOT-EVALUATE branch raised NameError instead of reporting. CI never
# reached them: the workflow builds the frontend and runs precompress.py before this suite, so
# all four guards are false there, and the file stayed green while unable to say "I could not
# judge this". TWO SESSIONS FOUND IT WITHIN AN HOUR OF EACH OTHER on 27 Aug and wrote the same
# one-line fix, which is worth recording -- it only shows when the suite is run locally without
# a built frontend, so the thing that hid it from CI is the thing that made it easy to hit.
import pytest

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

    cases = [
        # exempt, and why
        ("/api/rail/messages", True, "SSE"),
        ("/api/jobs/abc123/events", True, "SSE"),
        ("/mcp", True, "SSE — the MCP streamable-HTTP transport, missed by the first list"),
        ("/mcp/", True, "SSE"),
        ("/assets/index-abc123.js", True, "precompressed at build time"),
        # compressed
        ("/api/search/index", False, "ordinary JSON"),
        ("/api/jobs/abc123", False, "ordinary JSON — a job POLL is not its event stream"),
        ("/", False, "the shell"),
    ]
    for path, exempt, why in cases:
        routed.clear()
        asyncio.run(go(path))          # asyncio.run closes its loop; new_event_loop leaked one
        went_plain = routed == [path]
        assert went_plain is exempt, (
            f"{path} went to the {'plain app' if went_plain else 'compressor'} but should "
            f"have gone to the {'plain app' if exempt else 'compressor'} ({why})")


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
    # By FILE, not by count. `<= 1` tolerated the single permitted read moving anywhere,
    # which is not what the rule says.
    assert offenders and offenders[0].startswith("mcp_server/core.py"), (
        "the one permitted schema parse is not core.schema(): " + ", ".join(offenders))
    assert len(offenders) == 1, (
        "a schema file is parsed outside core.schema(): " + ", ".join(offenders))


def test_phylogeny_is_deliberately_not_cached():
    """The cache that was here made it 7.8x SLOWER, and the revert needs a guard.

    An audit added a module-level cache on the argument that this was "the same bug as the
    search index, one endpoint over". Measured: the rebuild walks already-in-memory
    core._data() and costs 0.23 ms; returning a cached copy cost 1.79 ms, because
    core.copy_json is json.loads(json.dumps(o)) over 157 KB. The endpoint costs ~20 ms end
    to end, so the build was 1.1% of it and the rest is FastAPI's encoder.

    This asserts the RELATION rather than a wall-clock number, so it cannot flake on a busy
    runner: rebuilding must not cost more than a copy of the result would have.
    """
    import time
    build = min(_time(corpus.phylogeny) for _ in range(5))
    built = corpus.phylogeny()
    copy = min(_time(lambda: core.copy_json(built)) for _ in range(5))
    assert build < copy, (
        f"rebuilding costs {build*1000:.2f} ms and copying {copy*1000:.2f} ms — if that ever "
        "inverts, caching phylogeny() becomes worth reconsidering; today it is not")
    assert not hasattr(corpus, "_PHYLOGENY"), (
        "the phylogeny cache is back; it was measured as a 7.8x pessimisation")


def _time(fn):
    import time
    t0 = time.perf_counter()
    fn()
    return time.perf_counter() - t0


def test_invalidate_clears_every_cache_it_claims_to():
    """/api/dev/reload exists so on-disk edits are seen. A cache it forgets is a cache that
    serves stale corpus data for the life of the process."""
    from workbench.server import citations
    # EVERY cache primed explicitly. The first version asserted _SEARCH_INDEX was None after
    # invalidating without ever filling it — it was only non-None because an unrelated test
    # 130 lines earlier had hit /api/search/index, so the assertion passed on a cache that was
    # never cleared because it was never filled. Order-dependent, and green for the wrong
    # reason: exactly the "populated rather than used" trap this file complains about.
    core.schema("plan")
    core.schema("brief")
    corpus.search_index()
    core._all_partis()
    citations._parti_ids()
    citations._constraint_ids()
    assert corpus._SEARCH_INDEX is not None
    assert core.schema.cache_info().currsize > 0
    assert core._all_partis.cache_info().currsize > 0
    assert citations._parti_ids.cache_info().currsize > 0

    corpus.invalidate()

    assert corpus._SEARCH_INDEX is None, "invalidate() left the search index cached"
    assert core.schema.cache_info().currsize == 0, "invalidate() left the schemas cached"
    assert core._all_partis.cache_info().currsize == 0, "invalidate() left the partis cached"
    # These two were missed by the first version, so /api/dev/reload left a newly added parti
    # uncitable for the life of the process — the rail downgraded the citation silently.
    assert citations._parti_ids.cache_info().currsize == 0, "invalidate() left parti ids cached"
    assert citations._constraint_ids.cache_info().currsize == 0, \
        "invalidate() left constraint ids cached"


def test_invalidate_clears_every_cache_that_exists_and_not_only_the_named_ones():
    """THE ENUMERATION IS THE BUG. The test above names each cache, so it can only catch a
    cache someone remembered to add to it — and three of core.py's five have now been missed
    on their way into `invalidate()`. WP-8.4 added `_kit_graph` and `_resolved_kit` and did
    not add them there, so after a reload every fault-exception precondition was still
    resolved against the PRE-EDIT kit graph for the life of the process: the bench showed an
    author's kit change everywhere except in whether a licence was granted on it.

    This walks the module instead of naming anything, so the fourth cannot be missed.
    """
    from workbench.server import citations
    modules = {"core": core, "citations": citations}
    caches = [(mod_name + "." + name, obj)
              for mod_name, mod in modules.items()
              for name, obj in vars(mod).items()
              if callable(obj) and hasattr(obj, "cache_clear") and hasattr(obj, "cache_info")]
    assert len(caches) >= 5, f"found only {[n for n, _ in caches]} -- the walk is broken"

    # Prime every one that takes no required argument; the rest are primed by the corpus
    # reads below, which is why this does not simply skip them.
    core._data()
    core.schema("plan")
    core._all_partis()
    citations._parti_ids()
    citations._constraint_ids()
    core._kit_graph()
    core._resolved_kit("tidewater-georgian")
    primed = [n for n, c in caches if c.cache_info().currsize > 0]
    assert len(primed) == len(caches), (
        f"could not prime {sorted(set(n for n, _ in caches) - set(primed))}; an unprimed "
        f"cache reads as cleared and the assertion below would pass vacuously")

    corpus.invalidate()

    left = [n for n, c in caches if c.cache_info().currsize > 0]
    assert left == [], f"invalidate() left these caches populated: {left}"


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

def test_hashed_assets_carry_the_immutable_header(client):
    """Asserted on a real RESPONSE, because the first version grepped inspect.getsource for
    the word "immutable" — which also appears in the docstring, so deleting the whole
    file_response override left the assertion green. It also never touched index.html despite
    saying so in its own name."""
    import os as _os
    from workbench.server import app as app_mod
    if not _os.path.isdir(app_mod.APP_DIST):
        pytest.skip("needs a built frontend")
    name = sorted(_os.listdir(_os.path.join(app_mod.APP_DIST, "assets")))
    hashed = next((n for n in name if not n.endswith(".gz")), None)
    assert hashed, "no assets to check"
    r = client.get(f"/assets/{hashed}")
    assert r.status_code == 200
    assert r.headers.get("cache-control") == "public, max-age=31536000, immutable", (
        f"/assets/{hashed} is not immutably cached: {r.headers.get('cache-control')!r}")


def test_the_shell_is_revalidated_so_a_deploy_reaches_a_returning_visitor(client):
    """The other half, which had no header and no test at all.

    ImmutableStatic's docstring claimed index.html "must stay revalidated" and nothing made
    it so: FileResponse sets only ETag/Last-Modified, and RFC 9111 heuristic freshness lets a
    browser serve a stale shell without asking. With /assets immutable for a year, this
    response is the only thing that can carry a deploy to someone who has been here before.
    """
    import os as _os
    from workbench.server import app as app_mod
    if not _os.path.isdir(app_mod.APP_DIST):
        pytest.skip("needs a built frontend")
    r = client.get("/")
    assert r.status_code == 200
    cc = (r.headers.get("cache-control") or "").lower()
    assert "no-cache" in cc or "no-store" in cc or "max-age=0" in cc, (
        f"the shell may be served stale from cache: cache-control={cc!r}")
    assert "immutable" not in cc, "the shell must never be immutable"


def test_assets_are_precompressed_rather_than_compressed_per_request(client):
    """The critical one. Dynamic gzip over the 1.19 MB bundle cost 569 ms at level 9 and
    38 ms at level 4, against 8 ms plain — on the event loop, on a route outside both the
    auth gate and the rate limiter, where one anonymous caller could saturate the core."""
    import os as _os
    from workbench.server import app as app_mod
    if not _os.path.isdir(app_mod.APP_DIST):
        pytest.skip("needs a built frontend")
    assert "/assets/" in app_mod.GZipExceptSSE.EXEMPT_PREFIXES, (
        "/assets is going through the dynamic compressor again")
    big = max((n for n in sorted(_os.listdir(_os.path.join(app_mod.APP_DIST, "assets")))
               if n.endswith(".js") and not n.endswith(".gz")),
              key=lambda n: _os.path.getsize(_os.path.join(app_mod.APP_DIST, "assets", n)))
    if not _os.path.isfile(_os.path.join(app_mod.APP_DIST, "assets", big + ".gz")):
        pytest.skip("assets not precompressed — run workbench/scripts/precompress.py")
    r = client.get(f"/assets/{big}", headers={"Accept-Encoding": "gzip"})
    assert r.headers.get("content-encoding") == "gzip", "the .gz sibling was not served"
    assert r.headers.get("vary") == "Accept-Encoding"


def test_the_compression_level_is_chosen_not_inherited():
    """Starlette's default is 9. For /api/search/index that is 9.01 ms and 52,293 bytes
    against level 4's 2.58 ms and 54,937 — 3.5x the CPU for 4.6% fewer bytes, on a server
    measured at one core. The first version of GZipExceptSSE passed only minimum_size."""
    from starlette.middleware.gzip import GZipMiddleware
    from workbench.server import app as app_mod
    import inspect
    starlette_default = inspect.signature(GZipMiddleware.__init__).parameters["compresslevel"].default
    assert app_mod.GZipExceptSSE.COMPRESSLEVEL < starlette_default, (
        "the compression level is back to Starlette's default")
    assert inspect.signature(app_mod.GZipExceptSSE.__init__).parameters[
        "compresslevel"].default == app_mod.GZipExceptSSE.COMPRESSLEVEL
