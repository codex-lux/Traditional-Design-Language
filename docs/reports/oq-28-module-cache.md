# OQ 28 — the module cache

*24 August 2026. Not a work package: a small enabler taken before WP-4.3 and WP-2.3 because every verification pass in both of them pays this tax. Fixes the performance ceiling diagnosed during WP-1.1 and deferred as open question 28.*

## What was wrong

Every module in `build/` and `mcp_server/` loads its siblings **by file path** rather than by `import`, using a local `_mod(name, path)` or `_load(name, path)` built on `importlib.util.spec_from_file_location`. That convention is correct and deliberate: this repository is a data corpus with scripts beside it, not an installed package, and each script must also run standalone (`python3 build/roof.py <plan>`). Nothing about the convention is the problem.

The problem is that `spec_from_file_location` + `module_from_spec` + `exec_module` returns a **brand new module object every call**. Nothing is reused, so every `functools.lru_cache` inside the loaded module starts cold — most consequentially `mcp_server/core.py`'s `_data()`, which globs and parses the entire corpus (164 style nodes, 209 faults, 159 kits, 58 rooms, the slot ontology, the massing catalog) on its first call.

WP-1.1 recorded that as "`plan_check` re-imports `core` per `check()` call." Profiling it properly for this fix showed the real shape is considerably worse, because the by-path loads are **module-level and they nest**:

```
elevation.py  → plan_check, geometry, structure, roof, proportion_engine
roof.py       → plan_check, geometry, structure
structure.py  → plan_check, geometry
geometry.py   → plan_check
compose.py    → plan_check
render_plan.py→ plan_check
```

So the whole tree is re-walked from scratch at every entry point. Measured on `plans/tidewater-georgian-careful.json`, a **single** `plan_check.check()` call executed:

| module | executions per `check()` |
|---|---|
| plan_check | 16 |
| geometry | 8 |
| structure | 4 |
| roof | 2 |
| core | 2 |
| elevation | 2 |
| proportion_engine | 2 |

This is a cost, not a correctness bug — every answer was right, just recomputed.

## What was built

`build/modcache.py`: one process-wide cache, `load(name, path)`, keyed by `os.path.realpath`. Every local `_mod`/`_load` in `elevation.py`, `geometry.py`, `structure.py`, `roof.py`, `compose.py`, `render_plan.py`, `plan_check.py` and the five loaders in `mcp_server/core.py` now delegates to it, keeping its own signature and standalone behaviour unchanged.

Keyed by path rather than name because the same file is loaded under several different names across this corpus (`plan_check` from six callers; `elevation` and `elevation_for_render` in `render_elevation.py`) and those are the same module — they should share one instance and one warm cache.

The module is registered in the cache *before* `exec_module` runs, which is what CPython's own import system does, so a future circular dependency degrades to a partially-initialised module rather than unbounded recursion. There is no cycle today — `plan_check` loads `elevation` lazily inside `check()`, never at module level, so the by-path graph is a DAG — but the guard is free. A module whose body raises is removed from the cache rather than left half-built for every later caller.

## Why not the two fixes OQ 28 proposed

The open question suggested either caching the loaded `core` module at `plan_check`'s own module scope, or having `core._data()` cache to a file keyed on corpus mtimes. Neither was taken.

Caching `core` at `plan_check`'s scope fixes **one edge** of the dependency graph above and leaves the other fifteen loads in place — it addresses the symptom WP-1.1 happened to notice rather than the mechanism. An mtime-keyed disk cache would work, but it introduces a staleness class this corpus does not otherwise have (a cache file that can disagree with the data on disk), for a problem that is entirely in-process. Delegation stops the re-execution without changing the loading convention, the call-site signatures, or the standalone-script guarantee.

## Results

| | before | after |
|---|---|---|
| `check()`, first call | 6.44 s | 1.71 s |
| `check()`, warm | 3.06 s | **0.31 s** |
| `compose()` per brief | 30-40 s | **7-9 s** |
| full pytest suite | ~12 min, 3 chunks | **2 min 24 s, one run** |
| `check_all.py` (21 checks incl. pytest) | did not fit one run | **3 min 0 s** |
| module executions per warm `check()` | 36 | **0** |

WP-0.3's acceptance line — "`make check` green from a clean checkout in under five minutes" — is met again; it had been broken since the constraint migration landed.

## Verified

- `check_all.py`: all 21 checks pass, including both shipped plans, both composer briefs, structure/roof/elevation on both plans, and `build.py`.
- `pytest tests/`: 291 passed in one run, plus 5 new (296 total).
- No output changed anywhere: both plans' fatal/serious/minor counts, both composer briefs' rankings, and every pinned test are identical. This was a pure execution-count change.

## The one behavioural change, and why it is safe

A cached module is not re-executed, so a process that mutates a corpus file on disk and then re-loads in-process will not see the change. Nothing in this corpus does that: the tests that deliberately break a data file (`tests/test_ontology.py`'s bad `derives_from_module`, `tests/test_constraints.py`'s duplicate constraint id) all run the checker under test as a **subprocess**, which gets a fresh process and therefore a fresh cache. `modcache.invalidate(path=None)` exists for anything that ever needs it.

## Pinned

`tests/test_modcache.py`, 5 tests: same object per path; keyed by path not name; a failing module body is not left cached and its real traceback survives; **a warm `check()` executes no module at all** (the counter that would have caught this class of regression); and a loose 3 s ceiling on warm `check()` that fails on an architectural regression rather than on a slow machine.

## Not done

The by-path convention itself is untouched — this fix makes it cheap rather than replacing it. Turning `build/` into a real package with ordinary imports would be a larger, more invasive change, would break the standalone-script guarantee every one of these files currently honours, and was not worth bundling into a performance fix.
