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


def test_the_limiter_is_starlettes_and_sits_inside_the_gate():
    """Two things an audit had to establish the hard way, both worth pinning.

    (1) This was a hand-rolled ASGI middleware whose comment claimed nothing at any layer
    bounded a body — "not uvicorn, not Starlette, not FastAPI" — which was false for the
    Starlette this project installs. The hand-rolled one answered 500 on /api/rail/messages
    (which reads its body directly, so nothing converted the resulting ClientDisconnect),
    delivered the wrong body where it did fire, and bounded nothing on a handler that never
    reads its body.

    (2) ORDER. The limiter answers 413 by catching its own _RequestBodyTooLarge. The auth gate
    is a BaseHTTPMiddleware, which wraps `receive` in an anyio task group, so an exception
    raised inside that wrapper surfaces as an ExceptionGroup and never matches. Registered
    outside the gate it produced a 500 with a traceback; inside, a clean 413. Both measured.
    """
    import inspect
    from starlette.middleware.body_limit import RequestBodyLimitMiddleware
    src = inspect.getsource(app_mod)
    assert not hasattr(app_mod, "BodyLimit"), "the hand-rolled body limiter is back"
    classes = [m.cls for m in app_mod.app.user_middleware]
    assert RequestBodyLimitMiddleware in classes, "the body limit is not registered"
    # user_middleware is built with insert(0), so LAST-added is FIRST in the list and
    # outermost. The gate must therefore appear BEFORE the limiter in this list.
    names = [c.__name__ for c in classes]
    assert names.index("BaseHTTPMiddleware") < names.index("RequestBodyLimitMiddleware"), (
        f"the body limiter is outside the auth gate ({names}) — there its 413 becomes a 500")


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


def test_a_long_name_is_still_drawn_whole():
    """NOT a guard on the cap — a guard that the cap did not break the rule above _fit_lines.

    Named honestly after an audit: this used to be called
    test_the_fitter_bounds_the_search_not_the_text, and it passes byte-identically with
    MAX_CHARS reverted. It asserts the name was not TRUNCATED, and _fit_lines has never
    truncated anything in either world, so it could not fail on the bug it appeared to guard.
    The cap itself is guarded by the timing ratio below, which discriminates 4.0x from 46.2x.
    Kept because "a reader can see cramped and cannot see truncated" is a real project rule
    and this is the only thing checking it.
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
    # The non-empty assertion matters: without it this passes on a silently empty loop, which
    # is one early return in solve() away from being the state of things.
    assert len(geo._SOLVE_CACHE) == 2, "nothing was cached, so the loop below proves nothing"
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

def test_a_non_numeric_count_is_clamped_rather_than_raised():
    """Asserted on the CLAMP, not on a status code, and that is the correction.

    The first version posted to /api/compose and asserted `status_code != 500`. TestClient
    defaults to raise_server_exceptions=True, so a reverted int() propagates OUT of the client
    and the test errors — it can never observe a 500 through that client, so the assertion as
    written was a fiction. It also queued a real ~8 s compose job onto the single worker that
    nothing ever reaped.

    _clamp and _candidates are pure, so test them directly.
    """
    from workbench.server import app as app_mod
    assert app_mod._candidates({"candidates": "not-a-number"}, default=4, cap=24) == 4
    assert app_mod._candidates({"candidates": None}, default=4, cap=24) == 4
    assert app_mod._candidates({"candidates": 0}, default=4, cap=24) == 1      # floor
    assert app_mod._candidates({"candidates": 9999}, default=4, cap=24) == 24  # cap
    assert app_mod._candidates({"candidates": 7}, default=4, cap=24) == 7
    # and the sibling the first pass missed entirely: /api/check/measurements read
    # body.get("limit", 40) raw, with no clamp and no int() guard.
    assert app_mod._clamp("nonsense", default=40, cap=1000) == 40
    assert app_mod._clamp(None, default=40, cap=1000) == 40
    assert app_mod._clamp(10**9, default=40, cap=1000) == 1000
    assert app_mod._clamp(12, default=40, cap=1000) == 12


def test_compose_and_measurements_survive_a_hostile_count(client):
    """And the endpoints themselves do not 500 on it. Asserted with server exceptions
    surfaced, so a raise is a failure rather than an invisible pass."""
    r = client.post("/api/check/measurements",
                    json={"measurements": [], "limit": "not-a-number"})
    assert r.status_code != 500


def test_dev_reload_is_metered():
    """invalidate() forces the next request to re-parse the whole corpus (~600 ms). It was
    the one heavy route outside the heavy bucket."""
    import inspect
    src = inspect.getsource(app_mod.dev_reload)
    doc = inspect.getdoc(app_mod.dev_reload) or ""
    for line in doc.splitlines():
        src = src.replace(line, "")
    assert "_heavy(request)" in src, "/api/dev/reload is unmetered"
