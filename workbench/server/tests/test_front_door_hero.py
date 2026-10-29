"""Phase 17 (WP-17.3): the front door's hero plate is the first shipped record the product may draw.

The Tidewater record is refused a drawing (WP-13.4), so the hero is never assumed to be it. The
record is FOUND by `corpus.first_drawable`, the RULE `drawable.py` hands every other server test,
asked in a different order: the tests ask the cheapest record first and the hero the good records
first, so the two may find different records (measured: bad-06 and good-03), and agree on the
verdict of every record both ask. The route returns the whole drawing result, so the plate keeps its
disclosures, and only the call that computes it is metered.
"""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("jsonschema")

from . import drawable  # noqa: E402


def test_the_hero_is_drawable_by_the_tests_own_verdict_and_asks_the_good_records_first(client):
    """One RULE, two orders: the tests ask the cheapest record first and the hero the shipped plans
    and the good examples first, because a bad example is no front door. Which record draws is the
    verdict's either way."""
    import json
    import os
    from workbench.server import corpus
    corpus.front_door_hero()          # the sweep, waited for here; the route itself never waits
    r = client.get("/api/front-door/hero")
    assert r.status_code == 200, r.text
    body = r.json()
    path, tried = corpus.first_drawable(corpus.HERO_ORDER)
    if path is None:
        assert drawable.drawable_plan_id() is None, "the two orders disagree about whether anything draws"
        assert body["refused"] is True and body["drawing"] is None and body["tried"] == tried
        return
    assert body["refused"] is False
    assert body["plan_id"] == json.load(open(path, encoding="utf-8"))["id"]
    # every record asked before the hero's was refused, by the same verdict the tests read. On this
    # corpus the hero is the FIRST record asked, so this loop runs over nothing and says so; the
    # skipping itself is driven below, where it can fail.
    order = corpus._shipped_plans(corpus.HERO_ORDER)
    for earlier in order[:order.index(path)]:
        placed = corpus._placed(corpus.core.copy_json(json.load(open(earlier, encoding="utf-8"))), None, 60)
        assert "refused_placement" in placed or "error" in placed, os.path.basename(earlier)
    assert not os.path.basename(path).startswith("bad-") or all(
        "refused_placement" in corpus._placed(corpus.core.copy_json(json.load(open(os.path.join(corpus.ROOT, p), encoding="utf-8"))), None, 60)
        for p in corpus.HERO_ORDER), "a bad example is the hero only where every good record is refused"
    assert isinstance(body["drawing"], dict) and "<svg" in body["drawing"]["svg"]
    # THE PLATE KEEPS ITS DISCLOSURES (Phase 17's audit: a hero reduced to its SVG stayed green)
    assert isinstance(body["drawing"].get("solver"), dict) and body["drawing"]["solver"].get("engine"), body["drawing"].keys()
    assert "relaxations" in body["drawing"], "the sheet's own account of what it relaxed travels with it"


def test_the_route_never_waits_on_the_sweep(client):
    from workbench.server import corpus
    corpus.reset_front_door()
    import time
    t = time.time()
    body = client.get("/api/front-door/hero").json()
    assert time.time() - t < 5, "the route answered at once"
    assert body.get("pending") is True or body.get("refused") in (True, False)
    corpus.front_door_hero()


def test_the_hero_is_memoised_and_a_reload_clears_it(client):
    from workbench.server import corpus
    corpus.front_door_hero()
    client.get("/api/front-door/hero")
    first = corpus._HERO
    assert first is not None
    client.get("/api/front-door/hero")
    assert corpus._HERO is first, "the second call reuses the first plate"
    corpus.invalidate()
    assert corpus._HERO is None and corpus._FIRST_DRAWABLE is None


def test_the_drawable_rule_lives_in_the_server_once():
    import inspect
    src = inspect.getsource(drawable)
    assert "corpus.first_drawable()" in src
    assert "_placed(" not in src.split('"""', 2)[-1], "the helper does not search on its own"



def test_the_sweep_skips_a_refused_record_and_takes_the_next(monkeypatch):
    """Driven, because on the corpus the hero is the first record asked and nothing is skipped."""
    from workbench.server import corpus
    order = corpus._shipped_plans(corpus.HERO_ORDER)[:2]
    calls = []

    def placed(plan, parti, budget):
        calls.append(plan.get("id"))
        return {"refused_placement": {"facts": ["stacks"]}} if len(calls) == 1 else {"geometry_report": {}}
    monkeypatch.setattr(corpus, "_placed", placed)
    monkeypatch.setattr(corpus, "_shipped_plans", lambda o: order)
    path, tried = corpus._sweep(corpus.HERO_ORDER)
    assert (path, tried) == (order[1], 2), "the refused record is skipped and counted"


def test_a_sweep_that_raises_is_said_and_not_restarted_on_every_poll(monkeypatch):
    from workbench.server import corpus
    import time
    corpus.reset_front_door()
    runs = []

    def boom():
        runs.append(1)
        raise RuntimeError("no plan could be read")
    monkeypatch.setattr(corpus, "front_door_hero", boom)
    assert corpus.front_door_hero_now() == {"pending": True}
    for _ in range(50):
        if corpus._HERO_ERROR:
            break
        time.sleep(0.05)
    body = corpus.front_door_hero_now()
    assert body.get("failed") is True and body["reason"] == "RuntimeError", body
    assert "no plan could be read" not in str(body), "the exception's text is logged, not served"
    corpus.front_door_hero_now()
    assert len(runs) == 1, "a failed sweep is said, not started again on each poll"
    # an old failure may be tried again (the second audit: one transient fault was the process's)
    monkeypatch.setattr(corpus, "HERO_RETRY_S", 0.0)
    assert corpus.front_door_hero_now() == {"pending": True}
    for _ in range(50):
        if len(runs) == 2:
            break
        time.sleep(0.05)
    assert len(runs) == 2, "a failure older than the retry window starts a fresh sweep"
    corpus.reset_front_door()
    assert corpus._HERO_ERROR == [], "a reload clears the failure"


def test_the_plate_is_drawn_from_the_placement_the_sweep_judged(monkeypatch):
    """The second audit of Phase 17: the sweep judged at 60 candidates and the plate was drawn at 250,
    a second solve whose placement nobody judged. Both now use SWEEP_CANDIDATES."""
    from workbench.server import corpus
    corpus.reset_front_door()
    path = corpus._shipped_plans(corpus.HERO_ORDER)[0]
    seen = {}
    monkeypatch.setattr(corpus, "first_drawable", lambda order=None: (path, 1))

    def drawing(kind, plan, parti=None, face=None, candidates=250, register="presentation"):
        seen["candidates"] = candidates
        return {"svg": "<svg/>", "solver": {"engine": "heuristic"}, "relaxations": []}
    monkeypatch.setattr(corpus, "drawing", drawing)
    out = corpus._compute_hero()
    assert seen["candidates"] == corpus.SWEEP_CANDIDATES
    assert out["refused"] is False
    src = __import__("inspect").getsource(corpus._sweep)
    assert "SWEEP_CANDIDATES" in src, "the sweep judges at the same budget the plate is drawn at"
    corpus.reset_front_door()


def test_a_judged_house_that_draws_no_plate_is_a_failure_not_an_empty_frame(monkeypatch):
    from workbench.server import corpus
    corpus.reset_front_door()
    path = corpus._shipped_plans(corpus.HERO_ORDER)[0]
    monkeypatch.setattr(corpus, "first_drawable", lambda order=None: (path, 1))
    monkeypatch.setattr(corpus, "drawing", lambda *a, **k: {"error": "refused"})
    with pytest.raises(RuntimeError):
        corpus._compute_hero()
    assert corpus._HERO is None
    corpus.reset_front_door()


def test_a_sweep_that_finishes_after_a_reset_does_not_write_its_answer(monkeypatch):
    """The second audit: a sweep still running when `invalidate` fired wrote its stale hero after
    the reset, and the route served it, because a live thread was taken for this generation's."""
    import threading
    from workbench.server import corpus
    corpus.reset_front_door()
    go = threading.Event()
    path = corpus._shipped_plans(corpus.HERO_ORDER)[0]

    def slow(order):
        go.wait(5)
        return (path, 1)
    monkeypatch.setattr(corpus, "_sweep", slow)
    t = threading.Thread(target=lambda: corpus.first_drawable(corpus.HERO_ORDER))
    t.start()
    corpus.reset_front_door()          # the reload lands while the sweep runs
    go.set()
    t.join(5)
    assert tuple(corpus.HERO_ORDER) not in corpus._FIRST_DRAWABLE_BY, "the stale sweep wrote its answer"
    corpus.reset_front_door()
