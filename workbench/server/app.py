"""The Workbench server — a thin HTTP skin over mcp_server/core.py.

Read routes are pass-throughs returning core's JSON shapes unchanged (the frontend
types mirror core.py, not the other way round). The server is stateless except the
compose job registry; the plan record is a document the browser owns.

Binds 127.0.0.1 by default; set WORKBENCH_HOST=0.0.0.0 to face a platform proxy. The
only network call it makes is to the Anthropic API, for the rail.

Auth is a shared password (`auth.py`) and is *optional* — unset WORKBENCH_PASSWORD and
the server is open, exactly as it was before it could be deployed, with /api/health
saying so. Only /api/* is gated: the static shell has to load in order to draw the
password screen, and it carries no corpus data.
"""
import os
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

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
                                   limit=body.get("limit", 40))


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
    engine = body.get("engine", "heuristic")
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
    res = jobs.submit(brief, candidates=int(body.get("candidates", 4)))
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
    stream = rail.stream_turn(body, identity=auth.identity(request))
    return StreamingResponse(stream, media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


# ----------------------------------------------------------------- dev
@app.post("/api/dev/reload")
def dev_reload():
    return corpus.invalidate()


# ----------------------------------------------------------------- MCP over HTTP
# Mounted BEFORE the SPA catch-all below: Starlette matches routes in registration order,
# and "/{path:path}" would otherwise swallow every request to /mcp.
if MCP_APP is not None:
    app.mount("/mcp", MCP_APP, name="mcp")


# ----------------------------------------------------------------- static app
APP_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "app", "dist")
if os.path.isdir(APP_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(APP_DIST, "assets")),
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
        return FileResponse(os.path.join(APP_DIST, "index.html"))
