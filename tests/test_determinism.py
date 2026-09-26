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
import ast
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
# module the solve reads, and then solves, leaves behind a result computed under the patch, and
# any later call AT THE SAME KEY is served it. `tests/test_hearths_on_flue.py` did exactly that
# on the SHIPPED Tidewater record at the heuristic engine's key, with `hearths.stack_axes`
# raising; clearing the cache BEFORE its solve did not help, because the poison is what the
# solve itself writes. The next file to ask for that plan at that key was `tests/test_openings.py`,
# whose fixture pin then read the hall bath's tub as fitting -- no stack run had been reserved
# -- and went red ONLY in a shard order that put the hearth file first. Measured: run as that
# pair, in that order, the second fails (1 failed, 1 passed) on WP-14.33's tree AND on
# WP-14.32's; reversed, both pass. It surfaced when this package's two new test files repacked
# the shards, which is `check_all`'s own note that the shard a red lands in is the packing and
# not the defect. An order dependence is a determinism defect of exactly the kind this file
# exists for: the result depended on something that is not the input.
#
# THE FIRST SCANNER READ TEXT, AND WP-14.33's AUDIT DROVE THE DEFECT PAST IT FOUR WAYS: the
# isolation surviving only as a `# comment`, the isolation moved AFTER the solve (the pair then
# went red again with the scanner green), a patch by `unittest.mock.patch.object`, and a patch by
# direct assignment (`GEO.X = ...`). It reads the AST now: a patch is a call or an assignment,
# the isolation is a real `setattr(<module>, "_SOLVE_CACHE", {})` CALL on a line BEFORE the first
# solve the patch precedes, or a `_SOLVE_CACHE.clear()` in the `finally` of a `try` whose body
# solves. It also stopped costing eighteen seconds: `ast.get_source_segment` re-split the whole
# file once per function.
#
# WHAT IT STILL CANNOT SEE, stated: a solve reached through a helper the function calls, and a
# patch made in a fixture the test requests. The behavioural test below it is the other half.

SOLVE_NAMES = ("solve", "solve_heuristic")
PATCH_METHODS = ("setattr", "setitem", "delattr", "delitem", "setenv", "delenv")


def _is_private_cache(call):
    return (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
            and call.func.attr == "setattr" and len(call.args) >= 3
            and isinstance(call.args[1], ast.Constant) and call.args[1].value == "_SOLVE_CACHE"
            and isinstance(call.args[2], ast.Dict) and not call.args[2].keys)


def _is_cache_clear(call):
    return (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
            and call.func.attr == "clear" and isinstance(call.func.value, ast.Attribute)
            and call.func.value.attr == "_SOLVE_CACHE")


def _calls_solve(node):
    for c in ast.walk(node):
        if isinstance(c, ast.Call):
            f = c.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if name in SOLVE_NAMES:
                yield c.lineno


def _patch_sites(fn):
    """`[(line, what)]`: every way this function patches something a solve might read."""
    out = []
    for d in fn.decorator_list:
        for c in ast.walk(d):
            if isinstance(c, ast.Call) and "patch" in ast.unparse(c.func).split("."):
                out.append((fn.lineno, "@" + ast.unparse(c.func)))
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and not _is_private_cache(n):
            f = ast.unparse(n.func)
            if isinstance(n.func, ast.Attribute) and n.func.attr in PATCH_METHODS:
                out.append((n.lineno, f))
            elif "patch" in f.split("."):
                out.append((n.lineno, f))
        elif isinstance(n, (ast.Assign, ast.AugAssign)):
            for t in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                # `mod.attr = ...` on a name: a module patched by hand. `self.x` is the test's own
                # state, and `fn._v` on the enclosing function is a memo, not a patch.
                if (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                        and t.value.id not in ("self", "cls", fn.name)):
                    out.append((n.lineno, ast.unparse(t) + " ="))
    return out


def solve_cache_verdicts(path, src):
    """`[(path, function, verdict)]` for every function in `src` that patches and then solves.
    The verdict is "private", "cleared-in-finally" or None. Pure, so it can be driven."""
    tree = ast.parse(src)
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        patches = _patch_sites(fn)
        if not patches:
            continue
        first_patch = min(line for line, _ in patches)
        solves = sorted(line for line in _calls_solve(fn) if line >= first_patch)
        if not solves:
            continue
        verdict = None
        if any(_is_private_cache(n) and n.lineno < solves[0] for n in ast.walk(fn)):
            verdict = "private"
        else:
            for t in ast.walk(fn):
                if (isinstance(t, ast.Try) and any(True for b in t.body for _ in _calls_solve(b))
                        and any(_is_cache_clear(c) for b in t.finalbody for c in ast.walk(b))):
                    verdict = "cleared-in-finally"
        out.append((path, fn.name, verdict))
    return out


def _patch_and_solve_functions():
    out = []
    for root in (os.path.join(ROOT, "tests"), os.path.join(ROOT, "workbench", "server", "tests")):
        for path in sorted(glob_module.glob(os.path.join(root, "test_*.py"))):
            out += solve_cache_verdicts(os.path.relpath(path, ROOT),
                                        open(path, encoding="utf-8").read())
    return out


def test_a_test_that_patches_and_solves_isolates_the_solve_cache():
    found = _patch_and_solve_functions()
    names = {n for _p, n, _ok in found}
    # The premise: the scanner reaches the functions it was written from, so a scanner that
    # stopped matching cannot pass by finding nothing.
    for known in ("test_an_unreadable_hearth_is_recorded_by_the_placer_and_republished_by_the_roof",
                  "test_A_RECONCILIATION_THAT_CANNOT_BE_READ_IS_A_FOURTH_STATE",
                  "test_without_ortools_the_fallback_says_so",
                  "test_the_solver_hands_exterior_score_the_per_element_bounds"):
        assert known in names, f"the scanner no longer reaches {known}; it has gone blind"
    bad = [f"{p}::{n}" for p, n, ok in found if not ok]
    assert not bad, (
        "a test patches something and solves without isolating geometry's solve cache, so a "
        "result computed under the patch outlives it at a key a later test file can ask for. "
        "Use monkeypatch.setattr(GEO, \"_SOLVE_CACHE\", {}) BEFORE the solve, or clear the "
        "cache in the `finally` of the `try` that solves:\n  " + "\n  ".join(bad))


def test_the_scanner_sees_the_shapes_the_first_one_could_not():
    """Driven over sources written here, one per shape the audit used, so a scanner that went
    blind to one of them fails by name rather than reading the tree as clean."""
    head = "def test_x(monkeypatch):\n"
    cases = {
        "isolated before": (head + "    monkeypatch.setattr(GEO, '_SOLVE_CACHE', {})\n"
                            "    monkeypatch.setattr(HE, 'f', g)\n    GEO.solve(p)\n", "private"),
        "comment only": (head + "    # monkeypatch.setattr(GEO, '_SOLVE_CACHE', {})\n"
                         "    monkeypatch.setattr(HE, 'f', g)\n    GEO.solve(p)\n", None),
        "isolated after": (head + "    monkeypatch.setattr(HE, 'f', g)\n    GEO.solve(p)\n"
                           "    monkeypatch.setattr(GEO, '_SOLVE_CACHE', {})\n", None),
        "patch.object": ("def test_x():\n    with unittest.mock.patch.object(HE, 'f', g):\n"
                         "        GEO.solve(p)\n", None),
        "decorator": ("@mock.patch('hearths.f')\ndef test_x(m):\n    GEO.solve(p)\n", None),
        "direct assignment": ("def test_x():\n    GEO.STACK_HARD = True\n    GEO.solve(p)\n", None),
        "cleared in finally": ("def test_x():\n    GEO.f = spy\n    try:\n        GEO.solve(p)\n"
                               "    finally:\n        GEO.f = real\n        GEO._SOLVE_CACHE.clear()\n",
                               "cleared-in-finally"),
        "cleared before": ("def test_x():\n    GEO.f = spy\n    GEO._SOLVE_CACHE.clear()\n"
                           "    GEO.solve(p)\n", None),
    }
    for name, (src, want) in cases.items():
        got = solve_cache_verdicts("x.py", src)
        assert len(got) == 1 and got[0][2] == want, (name, got)
    # and the two shapes that are NOT a patch of a module
    assert solve_cache_verdicts("x.py", "def f():\n    f._v = GEO.solve(p)\n") == []
    assert solve_cache_verdicts("x.py", "def f(self):\n    self.v = 1\n    GEO.solve(p)\n") == []


def test_the_private_cache_idiom_really_isolates(monkeypatch):
    """Behavioural half: the idiom works only because `solve` reads the module global at call
    time. Solve the shipped record under a patch with a private cache, then solve it again
    after: the second answer must be the unpatched one."""
    import sys
    if os.path.join(ROOT, "build") not in sys.path:
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
