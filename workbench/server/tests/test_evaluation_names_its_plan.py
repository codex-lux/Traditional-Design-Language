"""WP-14.20 — an evaluation names its plan, on the path where its check could not.

`oq/an-evaluation-whose-check-errored-names-no-plan`, closed on its answer 1. `plan_check` writes
the plan id only on a COMPLETED check, and `core.check_plan`'s two error payloads carry none. The
evaluate route keeps `placement_refused` alive through that early return (WP-13.4), so a record
whose check errored and whose placement was refused reached the journey naming no plan, and the
journey -- which reads an evaluation only for the plan it was of -- read it as "not yet
evaluated" and offered the drawings and the export as ready links over a refused house.

The route states the id at the top of its response now, before the early return. What is held:

  * on the ERRORED path, driven: the check carries no id, the route does, and the refusal travels
    beside it -- the one combination the shipped corpus does not reach on demand (0 of 16 checks
    errored when the question was measured), so it is driven rather than swept;
  * on a COMPLETED check, over the real route: the route's id and the check's own id are one id,
    so the journey's two readings (`evalPlanOf`: the route's first, then the check's) cannot
    disagree about an evaluation that carries both;
  * `core.check_plan`'s payload -- what the MCP tool serves -- gains nothing: the key is the
    workbench route's, and the frozen tool payload is not this package's to change.
"""
import json
import os

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("jsonschema")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

REFUSAL = {
    "kind": "type-fact-downgraded", "facts": ["stacks"],
    "conflicts": [{"kind": "stack", "key": ["primary", "drawing"], "why": "released"}],
    "lines": ["the Drawing Room does not stand under the Primary Bedroom it is declared to carry"],
    "engine": "cp-sat", "status": "OPTIMAL",
}
SCHEMA_ERROR = {"error": "plan does not match the plan schema", "detail": "driven by the test"}


def _shipped(name):
    return json.load(open(os.path.join(ROOT, "plans", name), encoding="utf-8"))


def test_an_errored_check_names_its_plan_beside_the_refusal(monkeypatch):
    from workbench.server import corpus
    from workbench.server import evaluate as EV
    core = corpus.core
    geo = core._mod("geometry", os.path.join(core.ROOT, "build", "geometry.py"))
    # the placer answers with a record the ruling refuses; the check on it then errors, which is
    # what a SOLVED record failing the plan schema looks like (WP-11.3, WP-11.4 and WP-13.6 each
    # shipped one)
    monkeypatch.setattr(geo, "solve", lambda plan, *a, **k: {
        **core.copy_json(plan), "geometry_report": {"refused": REFUSAL}})
    monkeypatch.setattr(core, "check_plan", lambda plan, strict=False: dict(SCHEMA_ERROR))
    plan = {"id": "p-errored", "name": "x", "style": "tidewater-georgian", "levels": []}
    out = EV.evaluate(plan, place=True, engine="auto")
    # the premise, so a green tick is about the errored path and not about a completed check
    assert "error" in out["check"] and "plan" not in out["check"], (
        "the driven check did not error, or it named its plan -- the test is not on the path")
    assert out["placement_refused"] == REFUSAL, "the refusal did not survive the early return"
    assert "placement" not in out
    assert out["plan"] == "p-errored", (
        "an evaluation whose check errored names no plan: the journey cannot tell which house "
        "the refusal was of and reads the drawings and the export as ready")


def test_a_completed_check_and_the_route_name_the_same_plan(client):
    """Over the real route, no placement asked for, so it is cheap and deterministic."""
    plan = _shipped("spec-builder-colonial.json")
    r = client.post("/api/plan/evaluate", json={"plan": plan, "place": False})
    assert r.status_code == 200, r.text[:200]
    j = r.json()
    assert "error" not in j["check"], "the premise: a completed check"
    assert j["plan"] == j["check"]["plan"] == plan["id"]


def test_the_tool_payload_gains_no_key(monkeypatch):
    """The MCP tool serves `core.check_plan`, and its error payload is exactly what it was: the
    route's `plan` is added by the route. A `plan` key appearing in the core's error payload would
    be answer 2 of the question, which changes a frozen payload and was not ruled."""
    from workbench.server import corpus
    core = corpus.core
    bad = {"id": "p-bad", "name": "x", "style": "tidewater-georgian", "levels": "not-a-list"}
    res = core.check_plan(bad)
    assert "error" in res, "the premise: a record failing the plan schema errors in the core"
    assert "plan" not in res, "core.check_plan's error payload grew a key the tool would serve"
