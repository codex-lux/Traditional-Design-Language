"""Pins the module-cache fix for OQ 28 (24 Aug 2026).

The finding: every module in this corpus loads its siblings by file path
(`_mod(name, path)` / `_load(name, path)` built on
`importlib.util.spec_from_file_location`), which returns a BRAND NEW module
object every call. Those loads are module-level and they nest -- elevation
loads plan_check, geometry, structure, roof and the engine; roof loads
plan_check, geometry and structure; structure loads plan_check and geometry;
geometry loads plan_check -- so the tree was re-walked from scratch at every
entry point, and `core._data()`'s lru_cache (which parses the whole corpus:
164 styles, 209 faults, 159 kits, 58 rooms) started cold each time.

Measured before the fix, a SINGLE plan_check.check() call performed
plan_check x16, geometry x8, structure x4, roof x2, core x2, elevation x2,
proportion_engine x2 -- about 3 s per call, 30-40 s per compose() brief, and
a 291-test suite that had to be chunked into three runs.

These tests protect the fix at the level that actually matters: not "the cache
returns the same object" (trivially true) but "the corpus is not re-parsed",
which is the property that regressed silently for weeks and would regress
silently again if someone reinstated a local loader for a good-looking reason.
"""
import importlib.util
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)


def test_same_path_returns_the_same_module_object():
    import modcache
    a = modcache.load("plan_check", os.path.join(BUILD, "plan_check.py"))
    b = modcache.load("plan_check", os.path.join(BUILD, "plan_check.py"))
    assert a is b


def test_cache_is_keyed_by_path_not_by_name():
    """The same file is loaded under different names across this corpus
    (`plan_check` from six callers, `elevation` vs `elevation_for_render` in
    render_elevation.py). Those are the same module and must share one warm
    cache, or the fix only half works."""
    import modcache
    p = os.path.join(BUILD, "geometry.py")
    a = modcache.load("geometry", p)
    b = modcache.load("geometry_under_another_name", p)
    assert a is b


def test_a_module_that_fails_to_execute_is_not_left_in_the_cache(tmp_path):
    """A half-built module must not be inherited by every later caller, and the
    real traceback must not be swallowed -- otherwise one bad edit poisons the
    process and reports the wrong error."""
    import modcache
    bad = tmp_path / "explodes.py"
    bad.write_text("raise RuntimeError('boom')\n")
    for _ in range(2):
        try:
            modcache.load("explodes", str(bad))
            assert False, "expected the module body to raise"
        except RuntimeError as e:
            assert "boom" in str(e)
    assert os.path.realpath(str(bad)) not in modcache.stats()["paths"]


def test_one_check_call_does_not_reload_the_corpus_seven_times_over():
    """The regression that OQ 28 named. Counts real module executions during a
    single check() and asserts each module is executed at most once -- before
    the fix this was 16 for plan_check alone."""
    import plan_check

    corpus = plan_check.load_corpus()
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    plan_check.check(plan, corpus)  # warm, so we measure steady state

    counts = {}
    original = importlib.util.spec_from_file_location

    def counting(name, path, *a, **k):
        counts[name] = counts.get(name, 0) + 1
        return original(name, path, *a, **k)

    importlib.util.spec_from_file_location = counting
    try:
        plan_check.check(plan, corpus)
    finally:
        importlib.util.spec_from_file_location = original

    assert not counts, f"warm check() re-executed modules: {counts}"


def test_check_is_fast_enough_that_the_suite_fits_one_run():
    """WP-0.3's acceptance line is `make check` green in under five minutes.
    OQ 28 broke it: check() at ~3 s meant compose() at 30-40 s and pytest in
    three chunks. The bound here is deliberately loose (10x the measured 0.31 s)
    so it fails on a real architectural regression, not on a slow machine."""
    import plan_check

    corpus = plan_check.load_corpus()
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    plan_check.check(plan, corpus)  # warm

    start = time.time()
    for _ in range(3):
        plan_check.check(plan, corpus)
    each = (time.time() - start) / 3
    assert each < 3.0, f"warm check() took {each:.2f}s each; OQ 28 has regressed"
