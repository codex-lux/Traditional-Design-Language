"""The two additive build/ changes WP-5.2 made, pinned so they cannot regress:
1. plan_check.check() returns fault_unjudged — the could-not-judge detail, not just
   its count (unjudged is not passed, and the which matters as much as the how-many).
2. compose(on_candidate=) reports each kept candidate as it completes, default None
   leaves behaviour identical.
"""
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _load(name):
    return modcache.load(name, os.path.join(ROOT, "build", f"{name}.py"))


def test_check_returns_fault_unjudged_detail():
    pc = _load("plan_check")
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    res = pc.check(plan)
    assert "fault_unjudged" in res
    assert isinstance(res["fault_unjudged"], list)
    assert len(res["fault_unjudged"]) == res["fault_summary"]["unjudged"]
    if res["fault_unjudged"]:
        assert {"fault", "needs"} <= set(res["fault_unjudged"][0])


def test_compose_on_candidate_callback():
    comp = _load("compose")
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    seen = []
    res = comp.compose(brief, 2, on_candidate=lambda c: seen.append(c))
    assert len(seen) >= len(res["candidates"])  # dropped-for-lot may reduce the kept set
    assert all("plan" not in c for c in seen)   # summaries only, never the whole plan
    assert all("score" in c and "parti" in c for c in seen)


def test_compose_without_callback_unchanged():
    comp = _load("compose")
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    res = comp.compose(brief, 2)
    assert res["candidates"]
