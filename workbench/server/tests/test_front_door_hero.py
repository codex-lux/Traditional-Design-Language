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
    assert body.get("failed") is True and "no plan could be read" in body["reason"]
    corpus.front_door_hero_now()
    assert len(runs) == 1, "a failed sweep is said, not started again on each poll"
    corpus.reset_front_door()
    assert corpus._HERO_ERROR == [], "a reload clears the failure"
