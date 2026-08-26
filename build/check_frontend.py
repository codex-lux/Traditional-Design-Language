#!/usr/bin/env python3
"""Run the workbench's pure-function suites — the ones nobody was running.

    python3 build/check_frontend.py

`workbench/app/e2e/router-unit.mjs` and `search-unit.mjs` are plain-assert suites over the
router, the citation grammar and the search scorer. They were written with WP-5.6 and wired
into NOTHING: not `check_all.py`, not a `Makefile`, not a `package.json` script. They existed
only as prose commands in two documents, so 74 checks ran exactly when somebody remembered to
type them, and the report that cited them as verification was citing a suite CI never saw. An
adversarial audit found it.

Node is not a dependency of the corpus — the data and every checker below `workbench/` run on
the standard library alone, deliberately. So a machine without node cannot judge these, and
this exits 3 (COULD NOT EVALUATE) rather than passing, the same way the CAD selftests do
without ezdxf. An unjudged suite is never a green one.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E2E = os.path.join(ROOT, "workbench", "app", "e2e")
COULD_NOT_EVALUATE = 3

SUITES = ["router-unit.mjs", "search-unit.mjs"]


def main():
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("COULD NOT EVALUATE: node is not installed, so the workbench's pure-function "
              "suites cannot run. They are not optional checks — they pin the router and the "
              "citation grammar — but a machine that cannot run them has not shown them to "
              "pass.", file=sys.stderr)
        return COULD_NOT_EVALUATE

    bad = 0
    for suite in SUITES:
        path = os.path.join(E2E, suite)
        if not os.path.exists(path):
            print(f"FAIL: {suite} is missing", file=sys.stderr)
            bad += 1
            continue
        print(f"--- {suite}")
        proc = subprocess.run([sys.executable and "node", path], cwd=E2E)
        if proc.returncode != 0:
            bad += 1
    if bad:
        print(f"\nFAIL: {bad} of {len(SUITES)} frontend suite(s) failed", file=sys.stderr)
        return 1
    print(f"\nOK — {len(SUITES)} frontend suites green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
