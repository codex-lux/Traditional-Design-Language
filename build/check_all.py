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
    ("validate.py", []),
    ("check_orders.py", []),
    ("check_modules.py", []),
    ("check_systems.py", []),
    ("check_kits.py", []),
    ("check_constraints.py", []),
    ("check_pack_bindings.py", ["--strict"]),
    ("check_faults.py", []),
    ("check_rooms.py", []),
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
    pytest_proc = subprocess.run(["pytest", "tests/"], cwd=str(ROOT))
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
