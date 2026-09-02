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
    res = comp.compose(brief, 2, on_candidate=lambda c: seen.append(c), revise=False)
    assert len(seen) >= len(res["candidates"])  # dropped-for-lot may reduce the kept set
    assert all("plan" not in c for c in seen)   # summaries only, never the whole plan
    assert all("score" in c and "parti" in c for c in seen)
    # The keys workbench/server/jobs.py::on_candidate actually reads, and the reason it reads
    # them: the progress strip publishes a score, and a disqualified candidate's score can be
    # the highest number on the screen. Asserting only "score" in c would not notice
    # `disqualified` or `counts` vanishing from the summary, which is the one way that line
    # can go back to publishing a 99.9 beside a plan carrying two fatals.
    for c in seen:
        assert "counts" in c, "jobs.py reads summary['counts'] for the fatal count"
        assert "disqualified" in c, "jobs.py streams the disqualification beside the score"
        assert isinstance(c["disqualified"], bool)
        assert c["disqualified"] == (c["counts"].get("fatal", 0) > 0), c["parti"]


def test_compose_without_callback_unchanged():
    comp = _load("compose")
    brief = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
    res = comp.compose(brief, 2, revise=False)
    assert res["candidates"]


def test_declared_relation_clears_must_not_adjoin():
    """A declared not-visible-from clears the adjacency finding EVEN when the pair is
    joined by a door — the finding's own fix text ("record the relation as
    'not-visible-from' if the separation is real") promises exactly this, and before
    the workbench audit the door-derived relation silently always won."""
    pc = _load("plan_check")
    plan = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json")))
    target = "Dining Room adjoins Powder Room, which it should not."
    assert target in [f["statement"] for f in pc.check(plan)["findings"]]
    plan2 = json.loads(json.dumps(plan))
    plan2.setdefault("adjacencies", []).append(
        {"a": "dining", "b": "powder", "relation": "not-visible-from"})
    res = pc.check(plan2)
    assert target not in [f["statement"] for f in res["findings"]]
    # and entered_from logic is untouched: same finding count delta of exactly one
    assert sum(pc.check(plan)["counts"].values()) - sum(res["counts"].values()) == 1


def test_modcache_concurrent_cold_load_is_safe():
    """Two threads racing the same cold load must both receive a fully-executed
    module — the register-before-exec cycle guard must not leak a half-built module
    across threads (the workbench serves these loads from a threadpool)."""
    import threading
    import textwrap
    import tempfile

    src = textwrap.dedent("""
        import time
        time.sleep(0.3)
        MARKER = 42
    """)
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(src)
        path = f.name
    try:
        results, errors = [], []

        def worker():
            try:
                m = modcache.load("slowmod_test", path)
                results.append(m.MARKER)
            except Exception as e:
                errors.append(repr(e))

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, errors
        assert results == [42, 42, 42, 42]
    finally:
        modcache.invalidate(path)
        os.unlink(path)
