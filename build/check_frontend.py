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

    # ── the atlas's heavy tiers must stay lazy ────────────────────────────────────
    # An audit noted that nothing enforced this: the fine coastline tier is 1.17 MB, and if
    # a future edit ever statically imports it from the entry graph, Vite folds it into
    # index-*.js, prints the SAME "chunk larger than 900 kB" warning it already prints, and
    # exits 0. CI would stay green while every reader of the workbench downloaded a
    # megabyte of coastline to look at a fault list.
    dist = os.path.join(ROOT, "workbench", "app", "dist", "assets")
    if not os.path.isdir(dist):
        print("--- lazy tiers: COULD NOT EVALUATE (no dist/ — run npm run build first)")
    else:
        print("--- lazy tiers")
        # sorted(), because tests/test_determinism.py holds every directory read in this
        # toolchain to a stable order and it caught these two the moment they were added.
        # It matters here beyond tidiness: `entry[0]` below picks one of the matches, and
        # an unsorted listdir would make WHICH one machine-specific.
        names = sorted(os.listdir(dist))
        entry = [f for f in names if f.startswith("index-") and f.endswith(".js")]
        tiers = [f for f in names if f.startswith("coastlines-")]
        # WP-12.4: `three` is the app's third runtime dependency and it must stay OUT of the
        # entry graph. It reaches the bundle only through `round/three-scene.js`, which
        # `Round.jsx` loads with a dynamic import -- so rollup emits it as its own chunk and
        # a reader who never opens the Round never downloads it. Measured at the time:
        # entry 477 KB against this 700 KB ceiling, `three` 564 KB in a chunk of its own
        # (WP-12.8 re-measured; the file that PRINTS these carried 478/545 as a comment).
        model = [f for f in names if f.startswith("three-scene-")]
        if not entry:
            print("FAIL: no entry chunk in dist/assets", file=sys.stderr)
            bad += 1
        elif len(tiers) < 2:
            print(f"FAIL: the medium and fine tiers are not separate chunks (found {tiers}) — "
                  "they have been folded into the entry graph", file=sys.stderr)
            bad += 1
        elif not model:
            print("FAIL: three.js is not a separate chunk — `round/three-scene.js` has been "
                  "imported statically somewhere, so every reader now downloads a 3D engine "
                  "to look at a flat plate", file=sys.stderr)
            bad += 1
        else:
            size = os.path.getsize(os.path.join(dist, entry[0]))
            if size > 700_000:
                print(f"FAIL: the entry chunk is {size/1024:.0f} KB; a tier has probably been "
                      "statically imported", file=sys.stderr)
                bad += 1
            else:
                msize = os.path.getsize(os.path.join(dist, model[0]))
                print(f"  entry {size/1024:.0f} KB, {len(tiers)} tier chunks kept out of it, "
                      f"three {msize/1024:.0f} KB in its own chunk")

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
