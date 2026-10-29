"""Phase 17 (WP-17.3): the front door's hero plate is the first shipped record the product may draw.

The Tidewater record is refused a drawing (WP-13.4), so the hero is never assumed to be it. The
record is FOUND by `corpus.first_drawable`, the same rule `drawable.py` hands every other server
test, so the hero and the tests cannot disagree about which house draws. The route returns the whole
drawing result, so the plate keeps its disclosures, and only the call that computes it is metered.
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
    # every record asked before the hero's was refused, by the same verdict the tests read
    order = corpus._shipped_plans(corpus.HERO_ORDER)
    for earlier in order[:order.index(path)]:
        placed = corpus._placed(corpus.core.copy_json(json.load(open(earlier, encoding="utf-8"))), None, 60)
        assert "refused_placement" in placed or "error" in placed, os.path.basename(earlier)
    assert not os.path.basename(path).startswith("bad-") or all(
        "refused_placement" in corpus._placed(corpus.core.copy_json(json.load(open(os.path.join(corpus.ROOT, p), encoding="utf-8"))), None, 60)
        for p in corpus.HERO_ORDER), "a bad example is the hero only where every good record is refused"
    assert isinstance(body["drawing"], dict) and "<svg" in body["drawing"]["svg"]


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

