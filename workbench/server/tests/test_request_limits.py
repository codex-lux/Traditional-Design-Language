"""The bounds on what one request may cost, and the escapes each one closed.

Every heavy endpoint's cost scales with the body it is handed — the solver in room count,
both renderers in the text they set — and nothing at any layer bounded a body: not uvicorn,
not Starlette, not FastAPI, and not schema/plan.schema.json, which carries no maxItems on
levels[].rooms and no maxLength on a name.
"""
import importlib.util
import json
import os

import pytest

from workbench.server import app as app_mod
from workbench.server import corpus

ROOT = corpus.ROOT


def _plan():
    return json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))


# ------------------------------------------------------------------ body size

def test_an_oversized_body_is_refused_with_413(client):
    fat = {"plan": _plan(), "pad": "x" * (app_mod.MAX_BODY_BYTES + 1024)}
    r = client.post("/api/plan/evaluate", json=fat)
    assert r.status_code == 413, "an unbounded body is the cheapest way to spend someone's CPU"


def test_a_real_plan_is_nowhere_near_the_limit():
    """The cap must not be one a genuine record can trip. The largest plan in plans/ is
    the measure of that, not a number picked for looking round."""
    biggest = max(os.path.getsize(os.path.join(ROOT, "plans", f))
                  for f in sorted(os.listdir(os.path.join(ROOT, "plans"))) if f.endswith(".json"))
    assert biggest * 20 < app_mod.MAX_BODY_BYTES, (
        f"largest real plan is {biggest} B against a {app_mod.MAX_BODY_BYTES} B cap — "
        "too close to be comfortable")


def test_a_normal_request_still_passes(client):
    r = client.post("/api/plan/evaluate", json={"plan": _plan(), "place": False})
    assert r.status_code == 200


# ------------------------------------------------------------------ the label fitter

def _render_plan():
    spec = importlib.util.spec_from_file_location("rp", os.path.join(ROOT, "build",
                                                                     "render_plan.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_fitter_bounds_the_search_not_the_text():
    """MAX_WORDS capped how many ARRANGEMENTS are searched, never how much text each is
    costed over — so twelve words of twenty thousand characters still cost 1.4 s, per room,
    with room count unbounded. The rule above _fit_lines is that a name is drawn whole, so
    the cap had to fall on the search.
    """
    rp = _render_plan()
    text = " ".join(["a" * 20000] * 12)
    out = rp._fit_lines(text, 120.0, 40.0, 9.0, 4.0)
    assert out, "a long name must still be drawn"
    kept = sum(len(line) for line in out[0])
    assert kept >= len(text) - 12, "the name was truncated — a reader cannot see truncated"


def test_the_fitter_searches_a_long_name_no_harder_than_a_short_one():
    """The discriminating comparison, and the first version of this test was not it.

    It compared 12 words of 200 chars against 12 words of 4000 chars and allowed a 60x
    rise. Both of those are long, so BOTH take the same path whether the cap is present or
    not, and the ratio is ~linear in either world — the test passed with the fix reverted.

    What actually changes is how many ARRANGEMENTS a long name is costed over: 12 words is
    C(11,2)=55 of them without the cap, and 3 pre-chunked runs with it. So compare a 12-word
    name against the 3-word name it chunks into, at the same per-word length. Measured:
    4.0x with the cap, 46.2x without.
    """
    import time
    rp = _render_plan()

    def cost(words, chars):
        text = " ".join([("a" * chars)] * words)
        best = float("inf")
        for _ in range(3):
            t0 = time.perf_counter()
            rp._fit_lines(text, 120.0, 40.0, 9.0, 4.0)
            best = min(best, time.perf_counter() - t0)
        return best

    twelve, three = cost(12, 4000), cost(3, 4000)
    ratio = twelve / max(three, 1e-9)
    assert ratio < 15, (
        f"a 12-word name cost {ratio:.0f}x the 3-word name it chunks into — the search cap "
        "is not holding (4x is the fixed figure, 46x the unfixed one)")


# ------------------------------------------------------------------ the solve cache

def test_solve_cache_key_is_constant_size():
    """The key used to BE the serialised plan, and 64 were retained — so a caller posting a
    large record pinned 64 copies of it in the keys alone."""
    spec = importlib.util.spec_from_file_location("geo", os.path.join(ROOT, "build",
                                                                      "geometry.py"))
    geo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geo)
    small, big = _plan(), _plan()
    big["levels"][0]["rooms"][0]["name"] = "x" * 50000
    geo.solve(small, None, 8, engine="heuristic")
    geo.solve(big, None, 8, engine="heuristic")
    for key in geo._SOLVE_CACHE:
        assert len(str(key)) < 400, "the plan is being stored inside its own cache key"


def test_an_oversized_plan_is_solved_but_not_remembered():
    """Bounding the key does nothing about a large VALUE. An oversized record still solves
    and still returns — it is simply not kept."""
    spec = importlib.util.spec_from_file_location("geo", os.path.join(ROOT, "build",
                                                                      "geometry.py"))
    geo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geo)
    huge = _plan()
    huge["levels"][0]["rooms"][0]["name"] = "y" * (geo.MAX_CACHEABLE_BYTES + 1)
    out = geo.solve(huge, None, 8, engine="heuristic")
    assert out and "geometry_report" in out, "an oversized plan must still be solved"
    assert len(geo._SOLVE_CACHE) == 0, "and must not be retained"


# ------------------------------------------------------------------ compose clamp

def test_compose_candidates_is_clamped_not_raw(client):
    """Every sibling endpoint used _candidates; this one read the value raw, so a
    non-numeric value raised ValueError into an unhandled 500."""
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    r = client.post("/api/compose", json={"brief": brief, "candidates": "not-a-number"})
    assert r.status_code != 500, "a non-numeric candidates count crashed the endpoint"


def test_dev_reload_is_metered():
    """invalidate() forces the next request to re-parse the whole corpus (~600 ms). It was
    the one heavy route outside the heavy bucket."""
    import inspect
    src = inspect.getsource(app_mod.dev_reload)
    doc = inspect.getdoc(app_mod.dev_reload) or ""
    for line in doc.splitlines():
        src = src.replace(line, "")
    assert "_heavy(request)" in src, "/api/dev/reload is unmetered"
