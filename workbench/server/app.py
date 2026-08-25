"""The Workbench server — a thin HTTP skin over mcp_server/core.py.

Read routes are pass-throughs returning core's JSON shapes unchanged (the frontend
types mirror core.py, not the other way round). The server is stateless except the
compose job registry; the plan record is a document the browser owns.

Binds 127.0.0.1 only. No auth, no network beyond the Anthropic API for the rail.
"""
import os

from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import corpus, evaluate, jobs

core = corpus.core

app = FastAPI(title="TDL Workbench", docs_url=None, redoc_url=None, openapi_url=None)


def _ok(result):
    """core returns {"error": ...} dicts rather than raising; map them to 404s so the
    client can tell a missing id from a server fault."""
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result)
    return result


# ----------------------------------------------------------------- health
@app.get("/api/health")
def health():
    try:
        import jsonschema  # noqa: F401 — without it every check "fails schema"
        schema_ok = True
    except ImportError:
        schema_ok = False
    counts = core.overview()["counts"]
    return {"ok": schema_ok, "jsonschema": schema_ok, "counts": counts,
            "rail": bool(os.environ.get("ANTHROPIC_API_KEY")),
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


# ----------------------------------------------------------------- the workbench loop
@app.post("/api/plan/evaluate")
def plan_evaluate(body: dict = Body(...)):
    plan = body.get("plan")
    if not plan:
        raise HTTPException(status_code=422, detail={"error": "body.plan is required"})
    return evaluate.evaluate(plan,
                             strict=bool(body.get("strict", False)),
                             place=bool(body.get("place", True)),
                             parti=body.get("parti"),
                             candidates=int(body.get("candidates", 250)))


# ----------------------------------------------------------------- compose jobs
@app.post("/api/compose")
def compose(body: dict = Body(...)):
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
    return StreamingResponse(jobs.events(job_id), media_type="text/event-stream")


@app.get("/api/jobs/{job_id}/candidates/{n}/plan")
def job_candidate_plan(job_id: str, n: int):
    plan = jobs.candidate_plan(job_id, n)
    if plan is None:
        raise HTTPException(status_code=404, detail={"error": "unknown job or candidate"})
    return plan


# ----------------------------------------------------------------- drawings
@app.post("/api/drawings/{kind}")
def drawings(kind: str, body: dict = Body(...)):
    plan = body.get("plan")
    if not plan:
        raise HTTPException(status_code=422, detail={"error": "body.plan is required"})
    res = corpus.drawing(kind, plan, parti=body.get("parti"), face=body.get("face"),
                         candidates=int(body.get("candidates", 250)))
    if "error" in res:
        raise HTTPException(status_code=422, detail=res)
    return res


# ----------------------------------------------------------------- export (WP-5.1)
@app.post("/api/export/{fmt}")
def export_cad(fmt: str, body: dict = Body(...)):
    plan = body.get("plan")
    if not plan:
        raise HTTPException(status_code=422, detail={"error": "body.plan is required"})
    res = corpus.export_cad(fmt, plan, kind=body.get("kind"), parti=body.get("parti"),
                            face=body.get("face"), candidates=int(body.get("candidates", 250)))
    if "error" in res:
        # 501 for the honest missing-library refusal, 422 for everything else —
        # the client shows the stated reason either way
        raise HTTPException(status_code=501 if res.get("unexported") else 422, detail=res)
    return res


# ----------------------------------------------------------------- the AI rail
@app.post("/api/rail/messages")
async def rail_messages(request: Request):
    from . import rail
    body = await request.json()
    return StreamingResponse(rail.stream_turn(body), media_type="text/event-stream")


# ----------------------------------------------------------------- dev
@app.post("/api/dev/reload")
def dev_reload():
    return corpus.invalidate()


# ----------------------------------------------------------------- static app
APP_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "app", "dist")
if os.path.isdir(APP_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(APP_DIST, "assets")),
              name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        candidate = os.path.join(APP_DIST, path)
        if path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(APP_DIST, "index.html"))
