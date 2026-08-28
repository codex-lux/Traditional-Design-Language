"""One process-wide cache for the by-path module loads this corpus does everywhere.

WHY THIS EXISTS (OQ 28, fixed 24 Aug 2026)
------------------------------------------
Every module in `build/` and `mcp_server/` loads its siblings *by file path*
rather than by `import`, because this repository is a data corpus with scripts
beside it rather than an installed package, and every one of those scripts must
also run standalone (`python3 build/roof.py <plan>`). The pattern each file
carries -- a local `_mod(name, path)` or `_load(name, path)` built on
`importlib.util.spec_from_file_location` -- is correct for that requirement and
is not the problem.

The problem is that `spec_from_file_location` + `module_from_spec` +
`exec_module` produces a **brand new module object on every call**. Nothing is
shared and nothing is reused. So every `functools.lru_cache` *inside* the module
being loaded starts cold, and the most consequential of those is
`mcp_server/core.py`'s `_data()`, which globs and parses the entire corpus --
164 style nodes, 209 faults, 159 kits, 58 rooms, the slot ontology, the massing
catalog -- on its first call.

Worse, the by-path loads are module-level and they nest. `elevation.py` loads
plan_check, geometry, structure, roof and the proportion engine at import time;
`roof.py` in turn loads plan_check, geometry and structure; `structure.py` loads
plan_check and geometry; `geometry.py` loads plan_check. Without a cache that
tree is re-walked from scratch at every entry point. Measured on
`plans/tidewater-georgian-careful.json` before this module existed, a **single**
`plan_check.check()` call performed:

    plan_check x16, geometry x8, structure x4, roof x2,
    core x2, elevation x2, proportion_engine x2

-- about 3 seconds per call, 30-40 s per `compose()` brief (which calls check()
hundreds of times while it repairs), and a 291-test suite that no longer fit in
a single run and had to be chunked into three ~4-minute groups.

This was diagnosed during WP-1.1 and recorded as open question 28 rather than
fixed at the time, because the fuller constraint payload is what turned a
long-standing but harmless pattern into a measurable one. It is fixed here.

WHAT THIS DOES
--------------
`load(name, path)` returns the same module object for the same real path, for
the life of the process. Callers keep their existing `_mod(name, path)` /
`_load(name, path)` signature and simply delegate here, so no call site changes
shape and every script still runs standalone.

Keyed by `os.path.realpath`, not by name: the same file is loaded under several
different names across this corpus (`plan_check`, `elevation_for_render`, and so
on) and those are the same module, so they should share one instance and one
warm cache. The name is still passed to importlib for `__name__`, and the first
name a path is loaded under wins.

CACHING SEMANTICS AND THE ONE THING TO WATCH
--------------------------------------------
A cached module is *not* re-executed, so a process that mutates a data file on
disk and expects a subsequent `load()` to see the change will not see it. That
is deliberate and safe here: the tests that mutate corpus files
(`tests/test_ontology.py`, `tests/test_constraints.py`, which write a
deliberately broken slots.json or a duplicate constraint id) all run the checker
they are testing as a **subprocess**, which gets its own fresh process and
therefore its own fresh cache. Nothing in this corpus mutates data and then
re-loads in-process. If something ever needs to, call `invalidate()` rather than
reaching into `_CACHE`.

The module is registered in the cache *before* `exec_module` runs, which is what
Python's own import system does, so a future circular dependency degrades to a
partially-initialised module rather than unbounded recursion. There is no cycle
today -- `plan_check` loads `elevation` lazily inside `check()`, never at module
level, so the by-path dependency graph is a DAG -- but the guard costs nothing
and the failure it prevents is nasty.
"""
from __future__ import annotations

import importlib.util
import os
import threading

_CACHE: dict[str, object] = {}

# One process-wide RLock. Every CLI user of this cache is single-threaded, but the
# workbench server (WP-5.2) calls the same loads from FastAPI's threadpool, and the
# register-before-exec convention below means an unlocked reader in a SECOND thread
# could be handed a module whose exec is still running in the first -- an
# AttributeError on whatever name isn't defined yet. An RLock keeps the deliberate
# same-thread re-entrancy (the cycle guard) while making cross-thread cold loads
# wait for a fully-executed module. Warm hits pay one uncontended acquire.
_LOCK = threading.RLock()


def load(name: str, path: str):
    """Return the module at `path`, loading it at most once per process.

    Signature-compatible with the local `_mod`/`_load` helpers it replaces.
    Thread-safe: concurrent cold loads serialize; the same thread may re-enter
    (a load cycle) and receives the partially-initialised module, as before.
    """
    # THE KEY AND THE LOADED FILE MUST BE THE SAME PATH. This keyed on the realpath and
    # loaded from the argument, so a module reached through a SYMLINK was cached under its
    # canonical key while its own `__file__` -- and therefore the `ROOT` almost every module
    # in `build/` derives from it -- pointed at the link. One test fixture symlinked `build/`
    # into a pytest tmpdir; two test files later `check_constraints` was still the tmp-rooted
    # copy and raised `FileNotFoundError: .../pytest-68/.../schema/constraint.schema.json` on
    # a directory that no longer existed. It passed alone and failed in the suite. Loading
    # from the realpath makes the class impossible rather than forbidden.
    key = os.path.realpath(path)
    with _LOCK:
        hit = _CACHE.get(key)
        if hit is not None:
            return hit

        spec = importlib.util.spec_from_file_location(name, key)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {name} from {path}")
        module = importlib.util.module_from_spec(spec)

        # Registered before exec so a re-entrant load of the same path gets the
        # partially-initialised module instead of recursing forever -- the same
        # thing CPython does with sys.modules. See the note above.
        _CACHE[key] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            # A module that failed to execute must not stay cached, or every later
            # caller inherits a half-built object and the real traceback is lost.
            _CACHE.pop(key, None)
            raise
        return module


def invalidate(path: str | None = None) -> None:
    """Drop one path (or the whole cache) so the next load() re-executes it.

    Only needed by a process that mutates corpus files and then re-reads them
    in-process. Nothing does that today; the mutation tests use subprocesses.
    """
    if path is None:
        _CACHE.clear()
    else:
        _CACHE.pop(os.path.realpath(path), None)


def stats() -> dict:
    """What is currently cached -- for diagnosing a slow path, as OQ 28 was."""
    return {"cached": len(_CACHE), "paths": sorted(_CACHE)}
