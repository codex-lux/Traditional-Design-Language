"""The Workbench server — a thin HTTP skin over mcp_server/core.py.

Read routes are pass-throughs returning core's JSON shapes unchanged (the frontend
types mirror core.py, not the other way round). The server is stateless except the
compose job registry; the plan record is a document the browser owns.

Binds 127.0.0.1 by default; set WORKBENCH_HOST=0.0.0.0 to face a platform proxy. The
only network call it makes is to the Anthropic API, for the rail.

Auth is a shared password (`auth.py`) and is *optional* — unset WORKBENCH_PASSWORD and
the server is open, exactly as it was before it could be deployed, with /api/health
saying so. Only /api/* and /mcp are gated: the static shell has to load in order to draw
the password screen.

WHAT THE UNGATED SURFACE CARRIES, stated exactly, because this sentence used to read "and
it carries no corpus data" and briefly stopped being true. Besides the shell it serves
`/corpus/assets/generated/*.svg` — the 73 moulding-profile plates the engine draws from the
proportion packs. They are derived corpus content and they are ungated on purpose: they are
drawings of figures published in treatises between 1562 and 1830, they are what the app puts
on the page, and none of them carries provenance, review notes or building names. The record
data behind them is behind /api/. When the first of anything else lands under assets/, this
paragraph is the thing to re-read before widening the mount.
"""
import os
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.body_limit import RequestBodyLimitMiddleware

from . import auth, corpus, evaluate, jobs, limits, mcp_mount

core = corpus.core

# Built BEFORE the FastAPI instance, because the session manager is created lazily inside
# streamable_http_app() and the lifespan below has to be able to reach it.
MCP_APP, MCP_STATE = mcp_mount.build()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """A mounted sub-application's own lifespan never runs, so the session manager has to
    be started here or every /mcp call raises 'Task group is not initialized'."""
    if MCP_APP is None:
        yield
        return
    from mcp_server import server as tdl_mcp
    async with tdl_mcp.mcp.session_manager.run():
        yield


app = FastAPI(title="TDL Workbench", docs_url=None, redoc_url=None, openapi_url=None,
              lifespan=lifespan)


# A request body is bounded by Starlette's own RequestBodyLimitMiddleware, registered below.
#
# THIS WAS A HAND-ROLLED ASGI MIDDLEWARE AND IT WAS WRONG IN FOUR WAYS. Its comment claimed
# nothing at any layer bounded a body — "not uvicorn, not Starlette, not FastAPI" — and that was
# false for the Starlette this project installs, which ships exactly this middleware. What the
# hand-rolled one got wrong that the built-in gets right:
#
#   * It returned {"type": "http.disconnect"} on an oversize chunk and rewrote the outgoing
#     status to 413. That works only where the handler's own error handling turns the resulting
#     ClientDisconnect into a response. `rail_messages` calls `await request.json()` directly
#     rather than through FastAPI's Body(...) machinery, so there is no such conversion: the
#     exception propagated past the rewrite and the caller got a 500 with a traceback in the
#     log. Reproduced before replacing it.
#   * Where the rewrite did fire, the BODY was still the handler's own parse error — "There was
#     an error parsing the body" — so the actionable message never reached anyone.
#   * It bounded nothing on a handler that never reads its body: a 5x oversize chunked POST to
#     /api/dev/reload returned 200.
#   * Its only test used TestClient, which always sends Content-Length, so the whole streaming
#     half was uncovered — delete the middleware and the test still passed. That is this audit's
#     own headline defect, committed inside the fix that closes it.
#
# 8 MB is far above any real plan (the largest in plans/ is 26 KB) and far below what makes the
# box sweat. Note it is a JSON-STRING ceiling for /api/ingest/dxf, where escaping inflates a DXF
# by ~1.21x, so the real limit there is ~6.6 MB of drawing.
MAX_BODY_BYTES = int(os.environ.get("WORKBENCH_MAX_BODY_BYTES") or 8 * 1024 * 1024)


# Registered BEFORE the gate, which puts it INSIDE it — Starlette applies middleware in reverse
# order of addition, so the last one added is outermost. Inside is required, not preferred: the
# gate is a BaseHTTPMiddleware, which wraps `receive` in its own anyio task group, and an
# exception raised inside that wrapper surfaces as an ExceptionGroup. The limiter answers 413
# by catching its own _RequestBodyTooLarge, so wrapped that way it never matches and the caller
# gets a 500 with a traceback instead. Measured both orders before choosing this one.
#
# The consequence is that auth runs first, so an unauthenticated oversize body is refused 401
# rather than 413 — which is also the better answer: it stops an anonymous caller learning the
# limit from a gated route.
app.add_middleware(RequestBodyLimitMiddleware, max_body_size=MAX_BODY_BYTES)


@app.middleware("http")
async def gate(request: Request, call_next):
    path = request.url.path
    # Starlette's Mount("/mcp") compiles to ^/mcp(?P<path>/.*)$ — it does not match a bare
    # "/mcp", which would fall through to the SPA catch-all and answer 405 to a POST.
    # Clients are handed ".../mcp" without a slash, so normalise here, before routing.
    if path == "/mcp" and MCP_APP is not None:
        request.scope["path"] = path = "/mcp/"
    # /mcp is gated exactly like /api — auth.authorised already accepts a bearer token,
    # which is what an agent client sends via `claude mcp add --header`.
    gated = path.startswith("/api/") or path == "/mcp" or path.startswith("/mcp/")
    if gated and path not in auth.OPEN_PATHS:
        if not auth.authorised(request):
            return JSONResponse(status_code=401,
                                content={"detail": {"error": "a password is required",
                                                    "auth": auth.state()}})
    return await call_next(request)


class GZipExceptSSE:
    """Compression, with the one exemption that has to be deliberate rather than discovered.

    Nothing here compressed anything. The app bundle, the 214 KB search index, every corpus
    response and the atlas's 1.17 MB fine coastline tier all went out whole — three times the
    bytes on a platform that bills egress, and three times the transfer time on every call,
    which is a share of what a reader experiences as lag.

    Starlette's GZipMiddleware would do it, but it buffers a streaming response, and this
    server has THREE that must arrive incrementally: /api/rail/messages, the compose event
    stream, and /mcp — the MCP streamable-HTTP transport, which the first version of this list
    missed. Buffering any of them turns a live progress line into a long pause and then
    everything at once — the rail's whole point is that it answers as it thinks. So they are
    exempted by path BEFORE the middleware sees the request, rather than hoping the content
    type saves us after the fact.
    """

    # /assets is exempt for a DIFFERENT reason from the SSE routes, and it is the sharper of
    # the two. Compressing the 1.19 MB bundle per request cost 569 ms at Starlette's default
    # level 9, and 38 ms even at level 4, against 8 ms served plain — on a route outside both
    # the auth gate (the shell must load to draw the password screen) and _heavy(). At level 9
    # one anonymous caller at 1.76 req/s saturated the core, making a static GET five times
    # more expensive than /api/plan/evaluate, the endpoint this audit calls the ceiling. And it
    # blocked the EVENT LOOP rather than a worker: FileResponse streams in 64 KiB chunks and
    # Starlette only offloads a chunk of 128 KiB or more, so every chunk compressed inline.
    # These files are content-hashed and immutable, so they are compressed ONCE at build time
    # instead — see ImmutableStatic and workbench/scripts/precompress.py.
    EXEMPT_PREFIXES = ("/assets/", "/corpus/")

    # LEVEL 4, NOT Starlette's default of 9. For /api/search/index, 214,229 bytes raw: level 9
    # costs 9.01 ms and emits 52,293 bytes; level 4 costs 2.58 ms and emits 54,937. That is
    # 3.5x the CPU for 4.6% fewer bytes, on a server measured at one core and ~2 evaluates a
    # second. The first version passed only minimum_size and so inherited 9 without choosing it.
    COMPRESSLEVEL = 4

    def __init__(self, app, minimum_size=600, compresslevel=COMPRESSLEVEL):
        from starlette.middleware.gzip import GZipMiddleware
        self.plain = app
        self.zipped = GZipMiddleware(app, minimum_size=minimum_size,
                                     compresslevel=compresslevel)

    def _exempt(self, path):
        """True for anything that must not go through the compressor."""
        if path.startswith(self.EXEMPT_PREFIXES):
            return True                                   # compressed at build time instead
        # /mcp is the MCP streamable-HTTP transport and it is text/event-stream too. It was
        # missing from the first version of this list, which survived only because this
        # Starlette excludes that content type by default — the very mechanism this class
        # exists in order not to rely on, and one no requirements pin guarantees.
        if path == "/mcp" or path.startswith("/mcp/"):
            return True
        if path.startswith("/api/rail/messages"):
            return True
        return path.startswith("/api/jobs/") and path.endswith("/events")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.plain(scope, receive, send)
        if self._exempt(scope.get("path", "")):
            return await self.plain(scope, receive, send)
        return await self.zipped(scope, receive, send)


app.add_middleware(GZipExceptSSE)


@app.post("/api/login")
async def login(request: Request, body: dict = Body(...)):
    if not auth.required():
        return {"ok": True, "note": "this server has no password set"}
    ok, retry = auth.login_allowed(request)
    if not ok:
        raise HTTPException(status_code=429,
                            detail={"error": "too many attempts — wait and try again",
                                    "retry_after_s": retry})
    if not auth.check_password(body.get("password")):
        raise HTTPException(status_code=401, detail={"error": "wrong password"})
    response = JSONResponse(content={"ok": True})
    response.set_cookie(auth.COOKIE, auth.mint(), max_age=auth.TTL_S, httponly=True,
                        samesite="lax", secure=request.url.scheme == "https")
    return response


def _heavy(request):
    """Gate a compute-heavy endpoint, or raise 429 with an honest reason."""
    reason = limits.check_heavy(auth.identity(request))
    if reason:
        raise HTTPException(status_code=429, detail={"error": reason, "limited": True})


def _ok(result):
    """core returns {"error": ...} dicts rather than raising; map them to 404s so the
    client can tell a missing id from a server fault."""
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result)
    return result


# ----------------------------------------------------------------- health
@app.get("/api/health")
def health(request: Request, response: Response):
    try:
        import jsonschema  # noqa: F401 — without it every check "fails schema"
        schema_ok = True
    except ImportError:
        schema_ok = False
    counts = core.overview()["counts"]
    # rail.key(), not a second reading of the environment: two readers of one variable can
    # disagree, and the one the browser believes would be the one that never runs a turn.
    from . import rail
    # An operator refreshes this endpoint to see whether a change took effect, and it
    # carries no validators — a heuristically cached 200 answers with the state before the
    # change and reads as the change not working.
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return {"ok": schema_ok, "jsonschema": schema_ok, "counts": counts,
            "rail": bool(rail.key()),
            "auth": auth.state(), "limits": limits.state(),
            # /api/health is deliberately ungated (the platform healthcheck has no
            # credentials), so it must not enumerate hostnames. allowed_hosts can carry
            # internal service names, so the list is shown only to an authorised caller;
            # everyone else gets the yes/no an operator actually needs.
            "mcp": (MCP_STATE if auth.authorised(request)
                    else {k: v for k, v in MCP_STATE.items() if k != "allowed_hosts"}
                         | {"platform_host_detected": bool(mcp_mount._platform_hosts())}),
            "note": None if schema_ok else
            "jsonschema is not installed — plan checks and compose will fail. "
            "pip install -r workbench/requirements.txt"}


# ----------------------------------------------------------------- orientation
@app.get("/api/overview")
def overview():
    return core.overview()


@app.get("/api/search/index")
def search_index():
    """Everything nameable, once, for the command palette. Fetched on first open and
    matched in the browser — see corpus.search_index for what is and is not indexed."""
    return corpus.search_index()


# ----------------------------------------------------------------- styles
@app.get("/api/styles")
def styles(query: str = "", rank: str = None, region: str = None,
           year: int = None, tradition: str = None, limit: int = 20):
    return core.find_style(query=query, rank=rank, region=region,
                           year=year, tradition=tradition, limit=limit)


@app.get("/api/styles/compare")
def styles_compare(a: str, b: str):
    return _ok(core.compare_styles(a, b))


@app.get("/api/styles/{style_id}")
def style(style_id: str, sections: str = None):
    secs = sections.split(",") if sections else None
    return _ok(core.get_style(style_id, sections=secs))


@app.get("/api/phylogeny")
def phylogeny():
    return corpus.phylogeny()


# ----------------------------------------------------------------- slots & kits
@app.get("/api/slots/{slot_id}")
def slot(slot_id: str):
    return _ok(core.get_slot(slot_id))


@app.get("/api/kit/{style_id}/cascade")
def cascade(style_id: str):
    return _ok(corpus.kit_cascade(style_id))


@app.get("/api/kit/{style_id}/slot/{slot_id}")
def kit_slot(style_id: str, slot_id: str):
    return _ok(corpus.slot_detail(style_id, slot_id))


@app.get("/api/kit/{style_id}")
def kit(style_id: str, group: str = None, slot: str = None,
        ceiling_height: float = 108.0, only_specified: bool = True):
    return _ok(core.resolve_kit(style_id, group=group, slot=slot,
                                ceiling_height=ceiling_height,
                                only_specified=only_specified))


# ----------------------------------------------------------------- proportion
@app.get("/api/proportions")
def proportions_list():
    return corpus.pack_list()


@app.get("/api/proportions/{pack_id}")
def proportions(pack_id: str, column_diameter: float = None, module: float = None,
                ceiling_height: float = 108.0, opening_width: float = 36.0,
                assembly: str = None, members: bool = False):
    if members:
        return _ok(corpus.proportions_with_members(
            pack_id, column_diameter=column_diameter, module=module,
            ceiling_height=ceiling_height, opening_width=opening_width))
    return _ok(core.get_proportions(pack_id, column_diameter=column_diameter,
                                    module=module, ceiling_height=ceiling_height,
                                    opening_width=opening_width, assembly=assembly))


@app.get("/api/authorities/{order}")
def authorities(order: str, column_diameter: float = 12.0):
    return _ok(core.compare_authorities(order, column_diameter=column_diameter))


# ----------------------------------------------------------------- faults
@app.get("/api/faults")
def faults(style: str = None, slot: str = None, group: str = None,
           severity: str = None, frequency: str = None,
           measurable_from: str = None, query: str = None, limit: int = 25):
    return core.find_faults(style=style, slot=slot, group=group, severity=severity,
                            frequency=frequency, measurable_from=measurable_from,
                            query=query, limit=limit)


@app.get("/api/faults/{fault_id}")
def fault(fault_id: str, style: str = None):
    return _ok(core.get_fault(fault_id, style=style))


@app.get("/api/vocabulary")
def vocabulary(slot: str = None, style: str = None, include_constraints: bool = True):
    return core.measurement_vocabulary(slot=slot, style=style,
                                       include_constraints=include_constraints)


@app.post("/api/check/measurements")
def check_measurements(body: dict = Body(...)):
    return core.check_measurements(body.get("measurements") or {},
                                   style=body.get("style"), slot=body.get("slot"),
                                   limit=_clamp(body.get("limit"), default=40, cap=1000))


@app.post("/api/check/constraints")
def check_constraints(body: dict = Body(...)):
    return _ok(core.check_style_constraints(body.get("style"),
                                            body.get("measurements") or {}))


# ----------------------------------------------------------------- alphabet
@app.get("/api/massings")
def massings(style: str = None, limit: int = 25):
    return core.get_massing(style=style, limit=limit)


@app.get("/api/massings/{massing_id}")
def massing(massing_id: str):
    return _ok(core.get_massing(massing_id=massing_id))


@app.get("/api/rooms")
def rooms(query: str = "", function_class: str = None, style: str = None,
          massing: str = None, limit: int = 25):
    return core.find_room(query=query, function_class=function_class,
                          style=style, massing=massing, limit=limit)


@app.get("/api/rooms/{room_id}")
def room(room_id: str, style: str = None):
    return _ok(core.get_room(room_id, style=style))


@app.get("/api/groupings")
def groupings(massing: str = None, style: str = None, scale: str = None,
              limit: int = 20):
    return core.get_grouping(massing=massing, style=style, scale=scale, limit=limit)


@app.get("/api/groupings/{grouping_id}")
def grouping(grouping_id: str, style: str = None):
    return _ok(core.get_grouping(grouping_id=grouping_id, style=style))


@app.get("/api/assets")
def assets(slot: str = None, style: str = None, fault: str = None,
           role: str = None, status: str = None, limit: int = 20):
    return core.find_assets(slot=slot, style=style, fault=fault, role=role,
                            status=status, limit=limit)


@app.get("/api/partis")
def partis(style: str = None, massing: str = None):
    return core.list_partis(style=style, massing=massing)


# ----------------------------------------------------------------- schemas
@app.get("/api/schema/plan")
def plan_schema():
    return core.plan_schema()


@app.get("/api/schema/brief")
def brief_schema():
    return core.brief_schema()


@app.get("/api/plans/examples/{name}")
def example_plan(name: str):
    """The shipped example plans, loadable into the workbench. Name only — no paths."""
    import json
    safe = os.path.basename(name)
    path = os.path.join(corpus.ROOT, "plans", safe if safe.endswith(".json") else safe + ".json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail={"error": f"no example plan '{safe}'"})
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:  # a malformed shipped example is a clean 422, not a 500
        raise HTTPException(status_code=422,
                            detail={"error": f"example plan '{safe}' is not readable JSON",
                                    "detail": str(e)[:200]})


def _clamp(value, default, cap, floor=1):
    """An int from a request body, or the default, bounded and never raising.

    /api/check/measurements read `body.get("limit", 40)` raw. The commit that clamped
    /api/compose said it was fixing "the one heavy route reading the value raw" — it was not
    the one, and this was the sibling it walked past. Same failure on a non-numeric value: an
    unhandled ValueError into a 500.
    """
    try:
        return max(floor, min(cap, int(value if value is not None else default)))
    except (TypeError, ValueError):
        return default


def _candidates(body, default=250, cap=2000):
    """Clamp the search width: it multiplies a full placement loop, so an
    unbounded value is a self-inflicted denial of service on a local tool."""
    try:
        return max(1, min(cap, int(body.get("candidates", default))))
    except (TypeError, ValueError):
        return default


# ----------------------------------------------------------------- the workbench loop
@app.post("/api/plan/evaluate")
def plan_evaluate(request: Request, body: dict = Body(...)):
    _heavy(request)
    plan = body.get("plan")
    if not plan:
        raise HTTPException(status_code=422, detail={"error": "body.plan is required"})
    # WP-6.3: `auto`, not `heuristic`. This default shadowed evaluate.evaluate()'s own, so
    # flipping that one alone changed nothing a browser could see — the sheet a reader
    # judges the house by went on coming from the fallback engine. Measured on the shipped
    # Tidewater plan: heuristic draws a kitchen with none of its five interior doors and
    # strands three rooms; CP draws all of them and strands none.
    engine = body.get("engine", "auto")
    if engine not in ("heuristic", "cp", "auto"):
        # anything unrecognized would silently take the auto->CP branch and
        # burn a 15s+ solve on a typo — refuse it, stated
        raise HTTPException(status_code=422, detail={
            "error": f"unknown engine {engine!r} — one of heuristic, cp, auto"})
    return evaluate.evaluate(plan,
                             strict=bool(body.get("strict", False)),
                             place=bool(body.get("place", True)),
                             parti=body.get("parti"),
                             candidates=_candidates(body),
                             engine=engine)


# ----------------------------------------------------------------- compose jobs
@app.post("/api/compose")
def compose(request: Request, body: dict = Body(...)):
    _heavy(request)
    brief = body.get("brief")
    if not brief:
        raise HTTPException(status_code=422, detail={"error": "body.brief is required"})
    # _candidates, like every sibling endpoint: this was the one heavy route reading the
    # value raw, so a non-numeric `candidates` raised ValueError into an unhandled 500. The
    # work is catalogue-bounded anyway (pick_partis cannot exceed the 21 partis), so the cap
    # is about consistency and the 500, not about a large attack surface.
    res = jobs.submit(brief, candidates=_candidates(body, default=4, cap=24))
    if "error" in res:
        raise HTTPException(status_code=422, detail=res)
    return res


@app.get("/api/jobs/{job_id}")
def job(job_id: str):
    res = jobs.get(job_id)
    if res is None:
        raise HTTPException(status_code=404, detail={"error": "unknown job"})
    return res


@app.get("/api/jobs/{job_id}/events")
def job_events(job_id: str):
    # Proxies buffer by default, which would hold compose progress until the job ended.
    return StreamingResponse(jobs.events(job_id), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


@app.get("/api/jobs/{job_id}/candidates/{n}/plan")
def job_candidate_plan(job_id: str, n: int):
    plan = jobs.candidate_plan(job_id, n)
    if plan is None:
        raise HTTPException(status_code=404, detail={"error": "unknown job or candidate"})
    return plan


# ----------------------------------------------------------------- drawings
@app.post("/api/drawings/{kind}")
def drawings(kind: str, request: Request, body: dict = Body(...)):
    _heavy(request)
    plan = body.get("plan")
    if not plan:
        raise HTTPException(status_code=422, detail={"error": "body.plan is required"})
    res = corpus.drawing(kind, plan, parti=body.get("parti"), face=body.get("face"),
                         candidates=_candidates(body))
    if "error" in res:
        raise HTTPException(status_code=422, detail=res)
    return res


# ----------------------------------------------------------------- export (WP-5.1)
@app.post("/api/export/{fmt}")
def export_cad(fmt: str, request: Request, body: dict = Body(...)):
    _heavy(request)  # an export solves the plan first — same class as /drawings
    plan = body.get("plan")
    if not plan:
        raise HTTPException(status_code=422, detail={"error": "body.plan is required"})
    res = corpus.export_cad(fmt, plan, kind=body.get("kind"), parti=body.get("parti"),
                            face=body.get("face"), candidates=_candidates(body))
    if "error" in res:
        # 501 ONLY for the honest missing-library refusal ("refusal" marks it);
        # a plan the solver refused is a 422 failure, not a missing capability
        raise HTTPException(status_code=501 if res.get("refusal") else 422, detail=res)
    return res


# ----------------------------------------------------------------- ingest (WP-5.5)
@app.post("/api/ingest/dxf")
def ingest_dxf(request: Request, body: dict = Body(...)):
    _heavy(request)  # ezdxf's tolerant parse over an uploaded body is unbounded work
    dxf = body.get("dxf")
    if not dxf or not isinstance(dxf, str):
        raise HTTPException(status_code=422, detail={"error": "body.dxf (the file's text) is required"})
    res = corpus.ingest_dxf(dxf, units=body.get("units"))
    if "error" in res:
        # 501 for the missing-library refusal (marked "refusal" by the
        # extractor); 422 for an unreadable file or ambiguous units — either
        # way the reason is stated, not swallowed
        code = 501 if res.get("refusal") else 422
        raise HTTPException(status_code=code, detail=res)
    return res


# ----------------------------------------------------------------- the AI rail
@app.post("/api/rail/messages")
async def rail_messages(request: Request):
    from . import rail
    body = await request.json()
    # Identity, not the session cookie itself: a Cloudflare Access email outranks it, and
    # a caller with neither still gets a stable-enough key. See auth.identity.
    # Bridged onto a dedicated thread rather than handed to StreamingResponse directly.
    # stream_turn is a SYNC generator making blocking SDK calls, and Starlette would wrap it in
    # iterate_in_threadpool — one anyio token per next(), held for a whole API round trip, out
    # of a pool 40 wide for the whole application, with no timeout to release it between
    # rounds. Same mechanism jobs.events was fixed for, and strictly worse; see
    # jobs.bridge_sync_stream for why the rail is bridged rather than rewritten.
    identity = auth.identity(request)
    stream = jobs.bridge_sync_stream(lambda: rail.stream_turn(body, identity=identity))
    return StreamingResponse(stream, media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


# ----------------------------------------------------------------- dev
@app.post("/api/dev/reload")
def dev_reload(request: Request):
    # Metered, because it is the most expensive thing an authorised caller can ask for and it
    # was the one heavy route outside the heavy bucket. invalidate() drops the module cache,
    # core._data and the search index, so the NEXT request re-globs and re-parses the whole
    # corpus — measured at ~600 ms — and a loop here is high-amplification for a caller who
    # pays almost nothing. Whether the route should exist in a production build at all is a
    # separate question, recorded rather than decided here.
    _heavy(request)
    return corpus.invalidate()


# ----------------------------------------------------------------- MCP over HTTP
# Mounted BEFORE the SPA catch-all below: Starlette matches routes in registration order,
# and "/{path:path}" would otherwise swallow every request to /mcp.
if MCP_APP is not None:
    app.mount("/mcp", MCP_APP, name="mcp")


# ----------------------------------------------------------------- static app
APP_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "app", "dist")
class ImmutableStatic(StaticFiles):
    """Content-hashed assets, cached for a year and compressed once rather than per request.

    Vite content-hashes every filename under /assets, so a given URL's bytes can never change
    — a new build means a new name. That makes a year-long immutable cache exactly true rather
    than merely convenient, and it stops the browser revalidating the bundle and the 1.17 MB
    fine coastline tier on every load.

    PRE-COMPRESSED, and that half is a fix rather than an optimisation. Running the dynamic
    gzip over these files cost 569 ms a request at Starlette's default level 9 and 38 ms even
    at level 4, against 8 ms plain, ON THE EVENT LOOP, on a route outside both the auth gate
    and the rate limiter. `workbench/scripts/precompress.py` writes a `<name>.gz` beside each
    asset at build time (the Dockerfile and CI both run it) and this serves that file when the
    caller accepts gzip. Measured after: 9.6 ms, and the client gets level-9 bytes rather than
    the level-4 the dynamic path had to settle for.

    When no `.gz` exists the original is served uncompressed, so a tree that skipped the build
    step still works; it simply ships more bytes.
    """

    def file_response(self, full_path, stat_result, scope, status_code=200):
        gz = str(full_path) + ".gz"
        # 200 only: a 206 Range response must describe the range of the resource the client
        # asked for, and a 304 carries no body at all.
        if status_code == 200 and _accepts_gzip(scope) and os.path.isfile(gz):
            resp = super().file_response(gz, os.stat(gz), scope, status_code)
            resp.headers["Content-Encoding"] = "gzip"
            resp.headers["Vary"] = "Accept-Encoding"
            # The ETag must belong to the RESOURCE, not to the .gz, or a client switching
            # between encodings revalidates against the wrong validator.
            resp.headers["ETag"] = f'"{stat_result.st_mtime_ns:x}-{stat_result.st_size:x}"'
        else:
            resp = super().file_response(full_path, stat_result, scope, status_code)
        resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return resp


def _accepts_gzip(scope):
    for k, v in scope.get("headers") or ():
        if k == b"accept-encoding":
            return b"gzip" in v.lower()
    return False


# THE CORPUS'S OWN ASSET FILES, AND THEY MAY NOT LIVE UNDER `/assets`. That path is mounted on
# Vite's content-hashed bundle output at workbench/app/dist/assets -- an unrelated namespace that
# happens to share the corpus directory's name. A record whose `file.path` is
# "assets/generated/x.svg" served from "/assets/generated/x.svg" would land in the bundle mount
# and 404, with immutable cache headers on the miss. `/corpus/` is a separate route.
#
# MOUNTED ON assets/generated AND NOT ON assets/, and the difference is three defects wide. The
# first version mounted the whole corpus directory, which put `assets/manifest.json` -- 3.4 MB,
# all 1,850 records with every provenance block, review note and hand-assigned building name --
# on an UNAUTHENTICATED route. The gate at the top of this file matches only `/api/` and `/mcp`,
# so `/api/assets` answered 401 while `/corpus/assets/manifest.json` answered 200 with the same
# data unbounded and unprojected. This module's own docstring says the static shell "carries no
# corpus data"; that sentence had quietly become false.
#
# It was also 33.5 ms of server CPU per request, because 3.4 MB compresses INLINE on the event
# loop: FileResponse streams 64 KiB chunks and GZipMiddleware only offloads above 128 KiB, which
# is the exact mechanism `/assets` is exempted from at EXEMPT_PREFIXES above. 31.5 requests a
# second from one anonymous caller saturated the deployment's single core, and each one shipped
# 286 KB -- a ~35,000x amplification against the request.
#
# And it exposed by DEFAULT: `harvest_habs.py` exists to put downloaded archive material into
# this corpus, and the day it runs, a remote file under assets/ would have become same-origin
# active content on this origin. Serving only the directory the app actually asks for -- the app
# requests `/corpus/assets/generated/*.svg` and nothing else -- keeps the URLs identical and
# closes all three.
CORPUS_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "assets", "generated")


class CorpusStatic(StaticFiles):
    """Generated plates, served as inert files.

    `nosniff` because these are SVG on the workbench's own origin, and a browser navigated
    directly at one executes any script inside it in this origin. Nothing under assets/generated
    is anything but engine output today; the header is here so that stays true of whatever is
    added next. `sandbox` is the same argument in CSP form."""

    def file_response(self, *a, **kw):
        r = super().file_response(*a, **kw)
        r.headers["X-Content-Type-Options"] = "nosniff"
        r.headers["Content-Security-Policy"] = "sandbox; default-src 'none'"
        # NOT `immutable`, and not left to heuristic freshness either. These paths are STABLE
        # across regenerations -- `<pack>-<assembly>-profile.svg` -- so a corrected moulding
        # would never reach a returning viewer under the heuristic caching RFC 9111 allows when
        # only ETag and Last-Modified are present. `must-revalidate` with a zero lifetime means
        # the ETag is still used and the bytes are still not re-sent, but a changed plate is.
        r.headers["Cache-Control"] = "no-cache, must-revalidate"
        return r


if os.path.isdir(CORPUS_ASSETS):
    app.mount("/corpus/assets/generated", CorpusStatic(directory=CORPUS_ASSETS),
              name="corpus-assets")

if os.path.isdir(APP_DIST):
    app.mount("/assets", ImmutableStatic(directory=os.path.join(APP_DIST, "assets")),
              name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        # os.path.join(APP_DIST, "../../../etc/passwd") escapes APP_DIST, os.path.isfile
        # agrees, and FileResponse serves it — an unauthenticated arbitrary file read,
        # because this catch-all is deliberately outside the gate so the password screen
        # can load. Harmless while the server bound 127.0.0.1; a hole the moment it binds
        # 0.0.0.0. Resolve the path and require it to stay inside APP_DIST. realpath, not
        # normpath: a symlink inside dist/ would otherwise still lead out.
        # (Both 25 Aug sessions' audits found this independently; one fix kept.)
        if path:
            candidate = os.path.realpath(os.path.join(APP_DIST, path))
            root = os.path.realpath(APP_DIST)
            if (candidate == root or candidate.startswith(root + os.sep)) \
                    and os.path.isfile(candidate):
                return FileResponse(candidate)
        # no-cache, because the docstring above used to CLAIM the shell "must stay
        # revalidated" and nothing made it so: FileResponse sets only ETag/Last-Modified, so
        # RFC 9111 heuristic freshness lets a browser serve a stale shell without asking.
        # Now that /assets is immutable for a year, this response is the only thing that can
        # carry a deploy to a returning visitor. no-cache means "revalidate", not "do not
        # store", so the ETag still saves the bytes on an unchanged deploy.
        return FileResponse(os.path.join(APP_DIST, "index.html"),
                            headers={"Cache-Control": "no-cache"})
