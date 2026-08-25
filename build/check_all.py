#!/usr/bin/env python3
"""Single entry point for the whole check suite: every data checker, then the
behaviour-test suite (tests/, pytest).

    python3 build/check_all.py
    make check          # same thing

Exits nonzero if anything fails. Runs everything even after a failure so one
red checker doesn't hide a second one — the summary at the end lists exactly
what failed.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHECKS = [
    # build.py FIRST, not last. It writes dist/taxonomy.json, and check_kits.py,
    # check_addresses.py and check_inheritance.py all READ that artefact. With build.py last,
    # every one of them validated the PREVIOUS run's graph: edit a lineage edge or a binding, and
    # the run that introduced the change measured the corpus as it was before it. The OQ 51 meter
    # -- whose whole purpose is to catch the cascade papering over something new -- was the worst
    # placed of the three. Only pytest caught it, and only because pytest happens to run after.
    # Found by audit 25 Aug 2026. It still runs at the end too, so a checker that mutates nothing
    # is proved not to have, and the artefact committed to git is the one the run just verified.
    ("build.py", []),
    ("validate.py", []),
    ("check_orders.py", []),
    ("check_modules.py", ["--eval"]),
    ("check_systems.py", []),
    ("check_kits.py", []),
    ("check_constraints.py", []),
    ("check_pack_bindings.py", ["--strict"]),
    ("check_faults.py", []),
    ("check_rooms.py", []),
    ("check_partis.py", []),
    ("check_counts.py", []),
    # --strict on both, added 25 Aug 2026 after an audit found neither could fail the build.
    # check_addresses was default-off deliberately while OQ 48 carried 139 collisions; that
    # question closed at 0, so the ratchet that stops a 1st new one is now the whole point.
    # check_inheritance guards OQ 51's three numbers, which the ruling says must only go down.
    ("check_addresses.py", ["--strict"]),
    ("check_inheritance.py", ["--strict"]),
    ("proportion_engine.py", ["selftest"]),
    ("plan_check.py", ["plans/spec-builder-colonial.json"]),
    ("plan_check.py", ["plans/tidewater-georgian-careful.json"]),
    ("structure.py", ["plans/spec-builder-colonial.json"]),
    ("structure.py", ["plans/tidewater-georgian-careful.json"]),
    ("roof.py", ["plans/spec-builder-colonial.json"]),
    ("roof.py", ["plans/tidewater-georgian-careful.json"]),
    ("elevation.py", ["plans/spec-builder-colonial.json"]),
    ("elevation.py", ["plans/tidewater-georgian-careful.json"]),
    ("compose.py", ["briefs/family-georgian.json"]),
    ("build.py", []),
]


def main():
    results = []
    for script, args in CHECKS:
        label = f"{script} {' '.join(args)}".strip()
        print(f"\n=== {label} " + "=" * max(0, 60 - len(label)))
        proc = subprocess.run(
            [sys.executable, str(ROOT / "build" / script)] + args,
            cwd=str(ROOT),
        )
        results.append((label, proc.returncode == 0))

    print("\n=== pytest tests/ " + "=" * 42)
    # `sys.executable -m pytest`, not the bare `pytest` on PATH. Every checker above already
    # runs under this interpreter, and a `pytest` from somewhere else runs the suite against a
    # different set of installed packages -- which is not a hypothetical: WP-2.3 found the
    # suite quietly SKIPPING all sixteen of its solver tests here while they passed when run
    # directly, because the `pytest` first on PATH belonged to another environment that had no
    # OR-Tools in it. A skipped test reports success, so the whole point of the entry point was
    # being lost without a word.
    pytest_proc = subprocess.run([sys.executable, "-m", "pytest", "tests/"], cwd=str(ROOT))
    results.append(("pytest tests/", pytest_proc.returncode == 0))

    print("\n" + "=" * 60)
    print("SUMMARY")
    failed = [label for label, ok in results if not ok]
    for label, ok in results:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}")
    if failed:
        print(f"\n{len(failed)} of {len(results)} checks failed.")
        sys.exit(1)
    print(f"\nAll {len(results)} checks passed.")


if __name__ == "__main__":
    main()
