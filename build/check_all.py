#!/usr/bin/env python3
"""Single entry point for the whole check suite: every data checker, then the
behaviour-test suite (tests/, pytest), then the workbench server suite.

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
    # WP-5.1: the exporters' selftests. ezdxf/ifcopenshell are OPTIONAL
    # dependencies — without them these exit 3, reported below as COULD NOT
    # EVALUATE: a named unjudged state, never collapsed into a pass.
    ("export_dxf.py", ["selftest"]),
    ("export_ifc.py", ["selftest"]),
    # WP-2.3: the CP-SAT solver's fixtures. ortools is OPTIONAL like the CAD
    # libs — without it this exits 3 (COULD NOT EVALUATE) and geometry.solve()
    # falls back to the hill-climb, saying so in geometry_report.solver.
    ("geometry_cp.py", ["selftest"]),
]

# exit code 3 from a check means "could not evaluate" (e.g. an optional
# dependency is absent). It is reported distinctly and does not fail the
# suite, but it is never printed as OK — unjudged is not passed.
COULD_NOT_EVALUATE = 3


def main():
    results = []
    for script, args in CHECKS:
        label = f"{script} {' '.join(args)}".strip()
        print(f"\n=== {label} " + "=" * max(0, 60 - len(label)))
        proc = subprocess.run(
            [sys.executable, str(ROOT / "build" / script)] + args,
            cwd=str(ROOT),
        )
        results.append((label, proc.returncode))

    print("\n=== pytest tests/ " + "=" * 42)
    # same interpreter as every check above — a standalone `pytest` on PATH can
    # be a different environment entirely (found the hard way: an isolated
    # pytest without the optional CAD libs silently skipped the export tests
    # while the selftests two lines up ran them)
    pytest_proc = subprocess.run([sys.executable, "-m", "pytest", "tests/"], cwd=str(ROOT))
    # normalized: pytest's own exit 3 means "internal error", not our
    # could-not-evaluate protocol — only the build/ checks speak that code
    results.append(("pytest tests/", 0 if pytest_proc.returncode == 0 else 1))

    # the workbench server suite is part of "must be green", not a side suite —
    # a broken /api/export or /api/ingest fails THIS gate. Its deps (fastapi,
    # httpx) are optional the same way the CAD libs are: absent → N/EV, stated.
    # Probe and run in the SAME interpreter (a bare `pytest` on PATH can belong
    # to a different environment; probing here and running there would report
    # a missing dependency as a failure — the one thing this must not do).
    print("\n=== pytest workbench/server/tests " + "=" * 26)
    probe = subprocess.run(
        [sys.executable, "-c", "import fastapi, httpx, pytest"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    if probe.returncode != 0:
        why = probe.stderr.strip().splitlines()[-1] if probe.stderr.strip() else "not importable"
        print(f"COULD NOT EVALUATE — {why}")
        print("    pip install -r workbench/requirements.txt")
        results.append(("pytest workbench/server/tests", COULD_NOT_EVALUATE))
    else:
        wb_proc = subprocess.run(
            [sys.executable, "-m", "pytest", "workbench/server/tests", "-q"], cwd=str(ROOT))
        results.append(("pytest workbench/server/tests", 0 if wb_proc.returncode == 0 else 1))

    print("\n" + "=" * 60)
    print("SUMMARY")
    failed = [label for label, rc in results if rc not in (0, COULD_NOT_EVALUATE)]
    unjudged = [label for label, rc in results if rc == COULD_NOT_EVALUATE]
    for label, rc in results:
        state = "OK  " if rc == 0 else ("N/EV" if rc == COULD_NOT_EVALUATE else "FAIL")
        print(f"  {state}  {label}")
    if failed:
        print(f"\n{len(failed)} of {len(results)} checks failed.")
        sys.exit(1)
    passed = len(results) - len(unjudged)
    if unjudged:
        print(f"\n{passed} of {len(results)} checks passed; {len(unjudged)} COULD NOT "
              f"EVALUATE (not a pass): {', '.join(unjudged)}")
    else:
        print(f"\nAll {len(results)} checks passed.")


if __name__ == "__main__":
    main()
