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

THERE ARE TWO ROUTES TO THAT 3 AND THE SECOND WAS ADDED BY WP-13.2. The lazy-tier block reads
`workbench/app/dist/`, which is GITIGNORED — so it is a property of whoever last ran
`npm run build`, not of the corpus. Judged against a bundle older than the code, it printed
`FAIL: three.js is not a separate chunk — round/three-scene.js has been imported statically
somewhere` about a file no module in the tree imports statically: the bundle was built 7 Sep
and `three-scene.js` was committed 9 Sep. A checker that accuses a named, innocent line is
worse than one that merely goes red. `bundle_unjudged_reason` is the third state.

So this check has three verdicts and its exit code carries all three: 0 only when the suites
pass AND the bundle was judged, 1 when either really failed, and 3 when the bundle could not
be judged at all — one check, one verdict, and the verdict of a check half of which could not
be evaluated is not a pass.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E2E = os.path.join(ROOT, "workbench", "app", "e2e")
COULD_NOT_EVALUATE = 3

SUITES = ["router-unit.mjs", "search-unit.mjs"]


def bundle_unjudged_reason(root=None):
    """Why this `dist/` cannot be judged, or `""` if it can.

    A function rather than four branches inside `main()` because a mutation sweep found the
    inline version BLIND three ways: deleting the staleness test, inverting it, and
    loosening `>` to `>=` all left the suite green, since nothing drove the wiring between
    `sources_newer_than` and the verdict. A guard that runs only where the bug cannot occur
    is not a guard.
    """
    base = root or ROOT
    dist = os.path.join(base, "workbench", "app", "dist", "assets")
    index = os.path.join(base, "workbench", "app", "dist", "index.html")
    if not os.path.isdir(dist):
        return "no dist/ — run npm run build first"
    if not os.path.exists(index):
        return "dist/ has no index.html, so the bundle cannot be dated"
    newer = sources_newer_than(os.path.getmtime(index), root=base)
    if newer:
        # `newer[0]` is first BY PATH and is named as such. The first draft called it the
        # "oldest offender", which the sort does not deliver -- a small false label on a
        # diagnostic is how a reader is sent to the wrong file.
        return (f"dist/ was built before {len(newer)} of the sources it would be judged "
                f"against (first by path: {newer[0]}) — run npm run build")
    return ""


def verdict(tier_bad, suite_bad, tier_unjudged, suites=SUITES):
    """The check's ONE verdict, as a pure function so every state can be driven.

    Returns `(exit_code, message)`. It is a function rather than four lines at the foot of
    `main()` because the defect it replaces was invisible to everything except a person
    reading the output: `bad` counted the lazy-tier check and the node suites in ONE
    variable, so a stale bundle printed

        FAIL: 1 of 2 frontend suite(s) failed

    two lines under `router-unit: 63 checks passed` and `search-unit: 13 checks passed`.
    A message that names the wrong population sends a reader to two green files. Tested
    against the PROPERTY -- drive a tier failure with no suite failure and the message may
    not say a suite failed -- rather than by grepping this file for a format string, which
    survives no rewording and tells a fix from a regression not at all.

    An unjudged tier check returns COULD NOT EVALUATE and never 0: one check, one verdict,
    and the verdict of a check half of which could not be evaluated is not a pass.
    """
    if tier_bad or suite_bad:
        parts = []
        if tier_bad:
            parts.append(f"{tier_bad} lazy-tier check(s)")
        if suite_bad:
            parts.append(f"{len(suite_bad)} of {len(suites)} frontend suite(s) "
                         f"({', '.join(suite_bad)})")
        return 1, f"FAIL: {' and '.join(parts)} failed"
    if tier_unjudged:
        return COULD_NOT_EVALUATE, (
            f"COULD NOT EVALUATE: {len(suites)} frontend suites are green and the "
            f"lazy-tier check was not judged — {tier_unjudged}")
    return 0, f"OK — {len(suites)} frontend suites green, and the lazy tiers hold."


def sources_newer_than(built_at, root=None):
    """The `workbench/app/src` files modified after the bundle was built.

    THE THIRD STATE, and it exists because this check had two. A `dist/` built before the
    code it is asked to judge reports `FAIL: three.js is not a separate chunk` about a
    bundle in which that chunk could not possibly appear -- `round/three-scene.js` did not
    exist when the bundle was written. That reads exactly like a real regression, and this
    repository's own rule is that a red build nobody can act on is worse than no build,
    because the next real failure arrives inside it. Measured on this tree 15 Sep 2026:
    dist built 7 Sep 17:11, `three-scene.js` committed 9 Sep, 22 sources newer.

    An mtime comparison is a HEURISTIC and it errs toward UNJUDGED in both directions that
    matter: a checkout that rewrites a source's mtime over a current bundle reads stale and
    is reported so, and a bundle built from a different tree with older mtimes reads current.
    It never errs toward a PASS, which is the direction that would matter -- a freshly built
    dist is newer than every source, so a real regression on a fresh build still FAILS.
    """
    # `root=` is the seam, so a test drives this over a tree it built rather than mutating
    # a module global and hoping its `finally` runs. modcache hands every reader the SAME
    # module object, so a mutated ROOT outlives the test that set it.
    base = root or ROOT
    src_dir = os.path.join(base, "workbench", "app", "src")
    out = []
    # sorted(os.walk(...)), not just sorted(files): tests/test_determinism.py forbids an
    # unsorted directory read anywhere in the toolchain, and it CAUGHT THIS ONE -- the first
    # draft sorted the file list on the next line, which is deterministic in the result and
    # invisible to a line-based guard. Sorting the walk is the stronger claim anyway: it
    # fixes the traversal order too, not only the order within each directory.
    for dirpath, _dirs, files in sorted(os.walk(src_dir)):
        for name in sorted(files):
            path = os.path.join(dirpath, name)
            try:
                if os.path.getmtime(path) > built_at:
                    # `base`, not ROOT. The first draft walked the seam and reported against
                    # the module global, so a driven tree came back as ../../../tmp/... --
                    # a seam wired in one place and not its neighbour, caught by this
                    # function's own first test run.
                    out.append(os.path.relpath(path, base))
            except OSError:          # a file that vanished under the walk is not evidence
                continue
    return sorted(out)


def main(root=None):
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("COULD NOT EVALUATE: node is not installed, so the workbench's pure-function "
              "suites cannot run. They are not optional checks — they pin the router and the "
              "citation grammar — but a machine that cannot run them has not shown them to "
              "pass.", file=sys.stderr)
        return COULD_NOT_EVALUATE

    # TWO POPULATIONS, COUNTED APART. They were one `bad` and the summary printed
    # "N of 2 frontend suite(s) failed" -- so a dist failure sent a reader to read
    # `router-unit.mjs` and `search-unit.mjs`, both of which were green. A message naming
    # the wrong population is this repository's "one reason for three causes" one layer up.
    tier_bad = 0
    suite_bad = []
    # `root=` mirrors the seam on the two readers below, and it is here because a mutation
    # sweep found the WIRING blind: main() could stop calling bundle_unjudged_reason()
    # altogether and every part-test stayed green. Each half was driven and the join was
    # not, which is WP-11.14's finding in a new place.
    base = root or ROOT

    # ── the atlas's heavy tiers must stay lazy ────────────────────────────────────
    # An audit noted that nothing enforced this: the fine coastline tier is 1.17 MB, and if
    # a future edit ever statically imports it from the entry graph, Vite folds it into
    # index-*.js, prints the SAME "chunk larger than 900 kB" warning it already prints, and
    # exits 0. CI would stay green while every reader of the workbench downloaded a
    # megabyte of coastline to look at a fault list.
    dist = os.path.join(base, "workbench", "app", "dist", "assets")
    # Read ONCE. The first draft called sources_newer_than in the condition and again in
    # the body -- two readings of a mutable tree under one name, which is this repository's
    # own "one quantity, two derivations" inside four lines of its own fix.
    tier_unjudged = bundle_unjudged_reason(root=base)
    if tier_unjudged:
        print(f"--- lazy tiers: COULD NOT EVALUATE ({tier_unjudged})")
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
            tier_bad += 1
        elif len(tiers) < 2:
            print(f"FAIL: the medium and fine tiers are not separate chunks (found {tiers}) — "
                  "they have been folded into the entry graph", file=sys.stderr)
            tier_bad += 1
        elif not model:
            print("FAIL: three.js is not a separate chunk — `round/three-scene.js` has been "
                  "imported statically somewhere, so every reader now downloads a 3D engine "
                  "to look at a flat plate", file=sys.stderr)
            tier_bad += 1
        else:
            size = os.path.getsize(os.path.join(dist, entry[0]))
            if size > 700_000:
                print(f"FAIL: the entry chunk is {size/1024:.0f} KB; a tier has probably been "
                      "statically imported", file=sys.stderr)
                tier_bad += 1
            else:
                msize = os.path.getsize(os.path.join(dist, model[0]))
                print(f"  entry {size/1024:.0f} KB, {len(tiers)} tier chunks kept out of it, "
                      f"three {msize/1024:.0f} KB in its own chunk")

    for suite in SUITES:
        path = os.path.join(E2E, suite)
        if not os.path.exists(path):
            print(f"FAIL: {suite} is missing", file=sys.stderr)
            suite_bad.append(suite)
            continue
        print(f"--- {suite}")
        proc = subprocess.run(["node", path], cwd=E2E)
        if proc.returncode != 0:
            suite_bad.append(suite)
    code, message = verdict(tier_bad, suite_bad, tier_unjudged)
    print("\n" + message, file=sys.stdout if code == 0 else sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
