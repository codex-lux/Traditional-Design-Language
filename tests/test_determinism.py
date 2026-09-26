"""The corpus must load in the same order on every machine.

The finding these pin, from the first CI run this project ever had (PR #2, 25 Aug 2026):
two composer tests passed on the authoring machine and failed on the runner. Neither the
composer nor the geometry solver is random — `geometry.solve` is seeded at 7 and
`compose.py` imports no RNG — but the corpus was loaded through unsorted `glob.glob`,
which returns directory order, and `pick_partis` then sorted on `fit` alone.

Python's sort is stable, so a tie fell back to insertion order, and `out[:limit]` cut
through the middle of it. For `briefs/family-georgian.json` four diagrams tie at fit 2.00
and only three survived the cut — so *which* diagram the composer never even scored was
decided by readdir. On this machine `side-hall-townhouse` survived and won; on the runner
it did not, and the assertion that it ranks first failed.

The tests below defend the two halves of the fix independently, because either one alone
leaves the other failure mode live.
"""
import glob as glob_module
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def compose_mod():
    import compose
    return compose


def _brief(name):
    with open(os.path.join(ROOT, "briefs", f"{name}.json")) as f:
        return json.load(f)


def test_corpus_globs_are_sorted():
    """Every corpus-loading glob in the toolchain is wrapped in sorted().

    Greps rather than introspects, because the failure is a *missing* wrapper — there is
    nothing to call once it is absent, and the next unsorted glob someone adds is exactly
    the regression this file exists to catch.
    """
    # Every way this codebase can read a directory. The first version of this test
    # matched only the literal "glob.glob(", which would have missed the next unsorted
    # read spelled any other way — and two really did survive it, in tests/ itself,
    # which is where the original cross-machine failure actually surfaced.
    readers = ("glob.glob(", "iglob(", "os.listdir(", "os.scandir(", "os.walk(",
               ".iterdir(", ".rglob(")
    offenders = []
    for sub in ("build", "mcp_server", "workbench", "tests"):
        for path in sorted(glob_module.glob(os.path.join(ROOT, sub, "**", "*.py"),
                                            recursive=True)):
            if os.path.basename(path) == os.path.basename(__file__):
                continue          # this file names the readers in order to look for them
            with open(path) as f:
                for n, line in enumerate(f, 1):
                    for r in readers:
                        i = line.find(r)
                        if i == -1:
                            continue
                        # Guarded when a sorted( opens before the read — which covers
                        # sorted(os.listdir(x)) and also sorted(f for f in os.listdir(x)),
                        # the comprehension form a literal "sorted(os.listdir(" match
                        # flagged as an offender when it was already correct.
                        s = line.find("sorted(")
                        if s != -1 and s < i:
                            continue
                        rel = os.path.relpath(path, ROOT)
                        offenders.append(f"{rel}:{n}: {line.strip()}")
    assert not offenders, (
        "unsorted directory read — the order is machine-specific:\n  "
        + "\n  ".join(offenders))


def test_pick_partis_expansion_is_bounded(compose_mod):
    """A narrow tie is kept whole; a wide one is not, because expanding it costs compose
    time proportional to the pool and adds nothing the fit function actually knows.

    adam-style has no native parti and no massing affinity — the majority case in this
    corpus — so ten diagrams tie at the cut. Before the bound, limit=6 returned all 12
    and doubled the composer's work."""
    wide = compose_mod.pick_partis(
        {"style": "adam-style", "target_area_sf": 6000, "bedrooms": 3}, limit=6)
    assert len(wide) == 6, f"wide tie must take the deterministic cut, got {len(wide)}"

    # bungalow-small, not family-georgian: see the note on the previous test. Six diagrams
    # tie at fit 2.0 there and the group is kept whole; family-georgian's tie went wide when
    # the catalogue grew and is now the deterministic-cut case, not the narrow one.
    narrow = compose_mod.pick_partis(_brief("bungalow-small"), limit=6)
    assert 6 < len(narrow) <= 6 + compose_mod.MAX_TIE_EXPANSION


def test_pick_partis_rejects_a_nonpositive_limit(compose_mod):
    """out[limit-1] with limit=0 indexes from the END and returned the whole corpus."""
    assert compose_mod.pick_partis(_brief("family-georgian"), limit=0) == []
    assert compose_mod.pick_partis(_brief("family-georgian"), limit=-3) == []


def test_pick_partis_is_totally_ordered(compose_mod):
    """Sorted by fit descending, then by id — with NO reliance on insertion order.

    The first version of this test asserted the output was sorted by (-fit, id) and was
    theatre: every file in partis/ is named <id>.json, so sorted(glob(...)) already gives
    id order, Python's sort is stable, and the output is id-ordered whether or not the
    tie-break key exists. Reverting the key alone left the whole file green.

    So the premise is attacked instead: PARTIS is reordered to the WORST case — reverse id
    order — and the result must still come back in id order. That can only hold if the key
    is really in the sort.
    """
    original = dict(compose_mod.PARTIS)
    hostile = dict(reversed(list(original.items())))
    compose_mod.PARTIS.clear()
    compose_mod.PARTIS.update(hostile)
    try:
        picked = compose_mod.pick_partis(_brief("family-georgian"), limit=99)
    finally:
        compose_mod.PARTIS.clear()
        compose_mod.PARTIS.update(original)

    keys = [(-p["fit"], p["parti"]) for p in picked]
    assert keys == sorted(keys), (
        "pick_partis fell back to insertion order — the tie-break key is missing")


def test_pick_partis_never_cuts_through_a_tie(compose_mod):
    """Diagrams that fit equally well are indistinguishable to this function, so the
    slice must not be what decides between them. Take the whole tie group; let the
    validator rank it."""
    # Re-pointed at the 25 Aug merge, per this test group's own instruction: WP-4.5 took the
    # catalogue from 12 partis to 21 and the tie this was written against MOVED. On
    # family-georgian at limit=6 the cut now lands on a singleton (fit 2.3), so returning
    # exactly 6 is correct and `len(picked) > 6` was asserting a property of the old
    # catalogue rather than of the mechanism. bungalow-small at limit=6 is the live narrow
    # tie: six diagrams at fit 2.0, expanded whole to 9.
    brief = _brief("bungalow-small")
    full = compose_mod.pick_partis(brief, limit=99)
    picked = compose_mod.pick_partis(brief, limit=6)

    edge = picked[-1]["fit"]
    tied = [p for p in full if p["fit"] == edge]
    assert len(tied) > 1, (
        "this brief no longer ties at the cut — re-point the test at one that does, "
        "rather than letting it pass by testing nothing")

    dropped_at_edge = [p["parti"] for p in full
                       if p["fit"] == edge and p not in picked]
    assert not dropped_at_edge, (
        f"dropped {dropped_at_edge} while keeping others at the same fit {edge}")


def test_the_tie_the_other_two_tests_rest_on_is_still_there(compose_mod):
    """The tie is the reason the other two tests exist. If a scoring change ever breaks it
    apart, they stop testing anything and should be re-pointed at a live tie.

    It did not break apart — it GREW, which is the same hazard from the other direction.
    WP-4.5 took the catalogue from 12 partis to 21 and family-georgian's four-way tie at
    fit 2.0 became a SEVEN-way one, wide enough that `pick_partis` now takes the
    deterministic cut there instead of expanding it. Re-pinned to the seven, and renamed,
    because a test called `four_way` that guards seven is a small lie in the suite."""
    full = compose_mod.pick_partis(_brief("family-georgian"), limit=99)
    at_two = sorted(p["parti"] for p in full if p["fit"] == 2.0)
    assert at_two == ["charleston-single-piazza", "connected-farmstead",
                      "courtyard-and-portal", "living-hall-picturesque",
                      "octagon-radial", "ranch-tripartite", "tower-villa"], at_two


# ---------------------------------------------------------------- the solve cache and a patch
# WP-14.33. `geometry._SOLVE_CACHE` is keyed on the plan, the parti, the candidate count, the
# seed, the engine and the budget -- and on NOTHING a test can patch. So a test that patches a
# module the solve reads, and then solves, leaves behind a result computed under the patch at a
# key any later caller can ask for. `tests/test_hearths_on_flue.py` did exactly that on the
# SHIPPED Tidewater record at the DEFAULT key, with `hearths.stack_axes` raising; clearing the
# cache BEFORE its solve did not help, because the poison is what the solve itself writes. The
# next file to ask for that plan was `tests/test_openings.py`, whose fixture pin then read the
# hall bath's tub as fitting -- no stack run had been reserved -- and went red ONLY in a shard
# order that put the hearth file first. Measured: those two tests alone, in that order, fail on
# WP-14.33's tree AND on WP-14.32's; reversed, both pass. It surfaced when this package's two
# new test files repacked the shards, which is `check_all`'s own note that the shard a red lands
# in is the packing and not the defect. An order dependence is a determinism defect of exactly
# the kind this file exists for: the result depended on something that is not the input.

def _patch_and_solve_functions():
    """Every test function that patches something and calls a solve, with whether it isolates
    the solve cache. A guard on ONE ROUTE IN: a solve reached through a helper the function
    calls is invisible here, which is why the behavioural test below exists beside it."""
    import ast
    out = []
    roots = [os.path.join(ROOT, "tests"), os.path.join(ROOT, "workbench", "server", "tests")]
    for root in roots:
        for path in sorted(glob_module.glob(os.path.join(root, "test_*.py"))):
            src = open(path, encoding="utf-8").read()
            tree = ast.parse(src)
            for fn in ast.walk(tree):
                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                seg = ast.get_source_segment(src, fn) or ""
                patches = any(s in seg for s in ("setattr(", "setitem(", "mock.patch"))
                solves = ".solve(" in seg or "solve_heuristic(" in seg
                if not (patches and solves):
                    continue
                private = ('"_SOLVE_CACHE", {}' in seg) or ("'_SOLVE_CACHE', {}" in seg)
                cleared_in_finally = any(
                    "_SOLVE_CACHE.clear()" in (ast.get_source_segment(src, b) or "")
                    for t in ast.walk(fn) if isinstance(t, ast.Try) for b in t.finalbody)
                out.append((os.path.relpath(path, ROOT), fn.name, private or cleared_in_finally))
    return out


def test_a_test_that_patches_and_solves_isolates_the_solve_cache():
    found = _patch_and_solve_functions()
    names = {n for _p, n, _ok in found}
    # The premise: the scanner reaches the three functions it was written from, so a scanner
    # that stopped matching cannot pass by finding nothing.
    for known in ("test_an_unreadable_hearth_is_recorded_by_the_placer_and_republished_by_the_roof",
                  "test_A_RECONCILIATION_THAT_CANNOT_BE_READ_IS_A_FOURTH_STATE",
                  "test_without_ortools_the_fallback_says_so"):
        assert known in names, f"the scanner no longer reaches {known}; it has gone blind"
    bad = [f"{p}::{n}" for p, n, ok in found if not ok]
    assert not bad, (
        "a test patches something and solves without isolating geometry's solve cache, so a "
        "result computed under the patch outlives it at a key a later test file can ask for. "
        "Use monkeypatch.setattr(GEO, \"_SOLVE_CACHE\", {}) before the solve, or clear the "
        "cache in a `finally` after it:\n  " + "\n  ".join(bad))


def test_the_private_cache_idiom_really_isolates(monkeypatch):
    """Behavioural half: the idiom works only because `solve` reads the module global at call
    time. Solve the shipped record under a patch with a private cache, then solve it again
    after: the second answer must be the unpatched one."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
    HE = modcache.load("hearths", os.path.join(ROOT, "build", "hearths.py"))
    path = os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")

    def boom(plan, C):
        raise ValueError("patched for the isolation test")

    with monkeypatch.context() as m:
        m.setattr(HE, "stack_axes", boom)
        m.setattr(GEO, "_SOLVE_CACHE", {})
        patched = GEO.solve(json.load(open(path)), None, 250, engine="heuristic")
    assert patched["hearths"].get("hearths_unreadable"), "the patch did not reach the solve"
    after = GEO.solve(json.load(open(path)), None, 250, engine="heuristic")
    assert not after["hearths"].get("hearths_unreadable"), (
        "a result solved under the patch was served after the patch was undone")
    assert after["hearths"]["breasts"], "the unpatched record draws its breasts"
