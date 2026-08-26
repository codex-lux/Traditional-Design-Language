#!/usr/bin/env python3
"""Single entry point for the whole check suite: every data checker, then the
behaviour-test suite (tests/, pytest), then the workbench server suite.

    python3 build/check_all.py
    make check          # same thing

Exits nonzero if anything fails. Runs everything even after a failure so one
red checker doesn't hide a second one — the summary at the end lists exactly
what failed.
"""
import shutil
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
    # check_gazetteer guards OQ 65: every style must be placeable on the Phylogeny's map
    # from its own regions and hearth. The map already reports a style it cannot place —
    # but as a line in a panel, which is where a new style goes quietly missing.
    ("check_gazetteer.py", ["--strict"]),
    # The workbench's pure-function suites (router, citation grammar, search scorer). They
    # shipped with WP-5.6 wired into nothing and were cited as verification anyway.
    ("check_frontend.py", []),
    ("proportion_engine.py", ["selftest"]),
    # WP-5.7: the moulding constructions prove themselves -- convexity, tangency at a cyma's
    # join, a half round returning to its springing, scale invariance, and the OQ 65 datum rule.
    ("profiles.py", ["selftest"]),
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
    # `sys.executable -m pytest`, not the bare `pytest` on PATH. Every checker above already
    # runs under this interpreter, and a `pytest` from somewhere else runs the suite against a
    # different set of installed packages. Two sessions found this independently and it is worth
    # keeping both instances: WP-2.3 found the suite quietly SKIPPING all sixteen solver tests
    # while they passed when run directly, because the `pytest` first on PATH belonged to an
    # environment with no OR-Tools; the deployment work found an isolated pytest without the CAD
    # libs silently skipping the export tests while the selftests two lines up ran them. A skipped
    # test reports success, so the whole point of the entry point was being lost without a word.
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

    # The workbench APP's own suite. Its pure ranking logic decides which candidate column
    # reads as first, and it had no tests of any kind until 26 Aug 2026 -- the array-rendered-
    # as-a-string defect that made a "why" line read "native to tidewater-georgianfour-over-
    # four" shipped and stayed shipped. node is optional here exactly as the CAD libraries
    # are: absent -> N/EV, stated, never a pass.
    print("\n=== node --test workbench/app " + "=" * 30)
    app = ROOT / "workbench" / "app"
    node = shutil.which("node")
    if not node:
        print("COULD NOT EVALUATE — node is not on PATH")
        print("    install Node 20+ (the app suite needs no npm install; it imports no packages)")
        results.append(("node --test workbench/app", COULD_NOT_EVALUATE))
    else:
        specs = sorted(str(p) for p in (app / "src").glob("*.test.mjs"))
        # A node too old to know --test exits nonzero, which reads as a FAILING suite. That
        # is the unjudged-reported-as-failed direction, which is the safer one but still
        # wrong: the suite did not run, so it neither passed nor failed.
        ver = subprocess.run([node, "--version"], capture_output=True, text=True)
        major = 0
        try:
            major = int((ver.stdout or "").strip().lstrip("v").split(".")[0])
        except ValueError:
            pass
        if major < 18:
            print(f"COULD NOT EVALUATE — node {ver.stdout.strip() or '?'} has no --test runner")
            print("    install Node 18+ (20 is what CI uses)")
            results.append(("node --test workbench/app", COULD_NOT_EVALUATE))
        elif not specs:
            print("COULD NOT EVALUATE — no *.test.mjs under workbench/app/src")
            results.append(("node --test workbench/app", COULD_NOT_EVALUATE))
        else:
            node_proc = subprocess.run([node, "--test", *specs], cwd=str(app))
            results.append(("node --test workbench/app",
                            0 if node_proc.returncode == 0 else 1))

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
