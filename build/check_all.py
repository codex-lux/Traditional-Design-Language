#!/usr/bin/env python3
"""Single entry point for the whole check suite: every data checker, then the
behaviour-test suite (tests/, pytest), then the workbench server suite.

    python3 build/check_all.py            # the whole thing, serially, as it always was
    make check                            # same thing
    python3 build/check_all.py --shard 2/6    # one sixth of it, for a CI runner
    python3 build/check_all.py --list-units   # what the work is, and what it is thought to cost

Exits nonzero if anything fails. Runs everything even after a failure so one
red checker doesn't hide a second one — the summary at the end lists exactly
what failed.

WHY IT SHARDS (WP-11.12, 7 Sep 2026)
------------------------------------
The `corpus` job was ONE serial step and had reached 39 min 32 s, which is the whole
wall-clock of a pull request -- the other two jobs finish in eight minutes and one.
Measured before anything was changed:

    pytest tests/        2,070 s   87%
    the 44 checkers        197 s    8%

So the suite is not slow because any one thing is slow; it is slow because 2,267 s of
independent work runs on one core. `--shard i/N` splits it across N runners. (Those are the
figures the problem was raised on. Merging Phase 11 took the total to 2,490 s and the checkers
to 45 -- which is the point: the number only ever goes up, and it went up 10% in the three days
this took to write.)

THE SPLIT IS BY PROCESS, AND THAT IS THE POINT RATHER THAN AN IMPLEMENTATION DETAIL.
Six test files mutate repository data in place and restore it in a `finally`
(test_kit_cascade, test_manifest_io, test_render_profile, test_ontology,
test_constraints, test_open_question_ids). A thread- or xdist-parallel suite would let
one worker read `assets/manifest.json` while another has it truncated, and the failure
would be intermittent and blamed on the reader. Each shard is a separate GitHub job
with its own checkout, and WITHIN a shard the tests run serially in one pytest process
exactly as they do today, so the isolation this suite already relies on is untouched.

WHAT CANNOT GO MISSING. Every unit is discovered -- the CHECKS list and a glob of
`tests/test_*.py` -- and `assign()` is a total function onto 0..N-1, so a unit lands in
exactly one shard by construction rather than by a list somebody has to remember to
extend. `tests/test_check_all_shards.py` holds that as a partition for every N it could
plausibly be run at, and mutation-checks it. A hand-written split of this suite would
be the shape this repository keeps finding: a check that went quiet behind a green tick.
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
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
    # The register's ids and the report filenames. Cheap (no corpus load) and it guards the
    # one id family that has ever collided -- four times in four days, because open questions
    # lived in a single shared file where two branches' answers to "what is the next number"
    # both survived a merge. See build/check_ids.py.
    ("check_ids.py", []),
    # The index is generated from docs/open-questions/; --check fails if the committed copy
    # has drifted, which is the same guarantee dist/taxonomy.json needed and did not have.
    ("gen_open_questions.py", ["--check"]),

    # The asset manifest, which FIVE tools write and none read. gen_assets.py validates it at
    # generation time only, so every edit after that -- the 786 building names, the 73 files,
    # the 209 fault links -- went in unchecked. Reports COULD NOT EVALUATE without jsonschema,
    # which CI installs, so it is judged there.
    ("check_assets.py", []),
    # WP-11.1. The building behind every exemplar, held to a record a checker can resolve: an
    # exemplar's `precedent` and the record's `nodes[]` in both directions, every reference's id
    # shape, `retrieved` and `via` on every URL, no `license` key at any depth, and kit figures
    # citing a survey quote that exists. Reads styles/ and precedents/ directly, not dist/.
    ("check_precedents.py", ["--strict"]),
    # WP-11.1. How deep the research under each node goes -- measured, because the corpus was
    # templated on the surface when it was surveyed (2-4 exemplars, 4-5 sources, 5 constraints on
    # every buildable node; the exemplar clause has since moved and the other two have not)
    # and the things that DO discriminate were tracked nowhere: exemplars a checker can resolve,
    # nodes citing only works ANOTHER NODE cites, `measured` figures with no source at all, split by
    # whether a generator reads the slot. Ratcheted.
    ("check_research.py", ["--strict"]),

    ("check_orders.py", []),
    ("check_modules.py", ["--eval"]),
    ("check_systems.py", []),
    ("check_kits.py", []),
    ("check_constraints.py", []),
    ("check_pack_bindings.py", ["--strict"]),
    ("check_faults.py", []),
    # Every dividing test against every measurement a generator supplies as ZERO. The corpus's
    # flagship failure is a rule that presupposes the thing it measures -- `dormer_count % 2`
    # on a house stating no dormers -- and the standing rule that any dividing test needs an
    # `applies_when` has been enforced by memory since WP-5.13. This is the meter. Its LIVE
    # figure is pinned at zero and goes non-zero the moment a generator starts supplying a new
    # zero, which is exactly what WP-5.13 did.
    ("check_division_guards.py", []),
    # WP-9.1: which measurements the elevation generator states as its own constants, and which
    # faults read them -- the analyst's critic-suspect list, ratcheted so it can only shrink
    ("check_critic_suspects.py", []),
    # WP-9.2: the move registry against its own code -- every id has an apply and vice versa,
    # every basis quote is really in the record it names, no move touches a placement key
    ("check_moves.py", []),
    ("check_rooms.py", []),
    # WP-9.7. Holds a grouping's `internal_rules` against the room record it constrains, and
    # against a grouping some parti carries alongside it -- the axis `check_addresses.py`
    # cannot see, because it reads packs and kits and not groupings, room bands or fault
    # tests. `--strict` because every ratchet here was measured on the first run rather than
    # inherited from a backlog: the three band disagreements are the register's own instances
    # and are the DELIVERABLE, not a debt to pay down.
    # `oq/a-grouping-rule-and-a-room-record-can-disagree`.
    ("check_grouping_rules.py", ["--strict"]),
    # WP-6.2. Not folded into check_rooms.py: that checker globs rooms/*.json against the
    # room schema, and the opening grammar is a different document in a different directory
    # for exactly that reason.
    ("check_openings.py", []),
    # WP-9.1. The arrangement layer's own selftest: that every derivation still moves when
    # the house it measures changes (a check that cannot fail is worse than none), that no
    # name in NOT_DERIVABLE reaches the returned measurements, and that every route in the
    # editorial route model still quotes a record that exists -- verified by calling
    # check_openings.check_basis rather than a copy of it.
    ("arrangement.py", ["selftest"]),
    ("check_windows.py", []),
    ("check_partis.py", []),
    # WP-11.2: a plan record against the PARTI it names. `check_partis.py` above holds a parti
    # to the styles it claims; this holds a hand-authored plan to the diagram it claims to be an
    # instance of, which nothing did -- the composer copies a parti's `stacks_over` onto every
    # candidate it emits, so a composed plan is right by construction and both SHIPPED reference
    # plans are hand-authored. The Tidewater plan had dropped the two claims that organise its
    # upper floor.
    ("check_plans.py", []),
    ("check_counts.py", []),
    # Citations, not counts. check_counts.py guards a NUMBER computed from the data;
    # this guards a REFERENCE -- that every `OQ N` resolves, that no cited id hides
    # behind a bare continuation number where a renumbering regex cannot see it, and
    # that the reissue tables still land somewhere. Added after three stale citations
    # were found on main, two written by this session and one by another.
    ("check_citations.py", []),
    # --strict on both, added 25 Aug 2026 after an audit found neither could fail the build.
    # check_addresses was default-off deliberately while OQ 48 carried 139 collisions; that
    # question closed at 0, so the ratchet that stops a 1st new one is now the whole point.
    # check_inheritance guards OQ 51's three numbers, which the ruling says must only go down.
    ("check_addresses.py", ["--strict"]),
    ("check_inheritance.py", ["--strict"]),
    # OQ 51's neighbour, ratcheted separately and deliberately not folded into the line above:
    # 776 (node, slot) pairs where the resolved kit binds a slot `forbidden` and a pack
    # dimensions it anyway, over 118 of 132 nodes, and NOT ONE of them was chosen by a human --
    # every one resolves by precedence. It counts a kit binding overruled by a pack, not a role
    # nobody bound, so it moves independently of the backlog. 4 s. Reports; fixing it changes
    # dimensions on most of the corpus and is its own package.
    ("check_inheritance.py", ["--forbidden", "--strict"]),
    # A FIFTH NUMBER, AND IT MEASURES A CHANGE THAT HAS NOT LANDED. OQ 51 was re-ruled 3 Sep 2026
    # -- pack inheritance becomes opt-in, staged pack by pack -- and this is what that costs:
    # 2,899 slots losing ALL dimensioning across 124 of 132 nodes, against the ~223 the ruling
    # was taken on, which counts ROLE GAPS and not deliveries. It runs in the build so that each
    # stage of the flip has to re-pin it deliberately and nobody can land one silently. 6.5 s.
    # Pinned as EQUALITIES rather than a ceiling: every one of these falls as the flip lands,
    # and a may-only-fall bound is satisfied by measuring less.
    ("check_inheritance.py", ["--stranding", "--strict"]),
    # check_gazetteer guards OQ 65: every style must be placeable on the Phylogeny's map
    # from its own regions and hearth. The map already reports a style it cannot place —
    # but as a line in a panel, which is where a new style goes quietly missing.
    ("check_gazetteer.py", ["--strict"]),
    # The workbench's pure-function suites (router, citation grammar, search scorer). They
    # shipped with WP-5.6 wired into nothing and were cited as verification anyway.
    ("check_frontend.py", []),
    ("proportion_engine.py", ["selftest"]),
    # WP-5.11: the moulding constructions prove themselves -- convexity, tangency at a cyma's
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
    # WP-9.2: the composer revises its returned candidates by default; here on the search
    # engine for two rounds, so the corpus job stays bounded (measured: 29 s against 12 s
    # with --no-revise). The proof-backed loop is exercised by tests/test_revise.py.
    ("compose.py", ["briefs/family-georgian.json", "--revise-engine", "heuristic", "--revise-rounds", "2"]),
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


# The three suites the runner appends AFTER the CHECKS loop. They are named here rather than
# only appearing as `results.append(...)` calls inside main() because CLAUDE.md publishes a
# check TOTAL, and that number has now been wrong three times for exactly one reason: whoever
# updated it measured `len(CHECKS)`, which is the loop and not the run. WP-5.11 found it saying
# 32 against a suite of 33; the 27 Aug merge resolved a conflict here and wrote 32 again, in
# the very sentence that describes the bug, and check_all.py printed "1 of 35" against it an
# hour later. TOTAL_CHECKS is what the runner actually reports, and
# tests/test_counts_guard.py holds CLAUDE.md to it -- so the next person to add a suite breaks
# a test instead of quietly making a published number wrong.
EXTRA_SUITES = (
    "pytest tests/",
    "pytest workbench/server/tests",
    "node --test workbench/app",
)

TOTAL_CHECKS = len(CHECKS) + len(EXTRA_SUITES)

# ------------------------------------------------------------------ the schedulable work

# The two `("build.py", [])` entries are FRAMING, not shardable units, and both run in
# EVERY shard. The first writes dist/taxonomy.json, which check_kits, check_addresses and
# check_inheritance all read -- a shard that got a reader without the writer would validate
# whatever artefact the checkout happened to carry, which is the exact defect the audit of
# 25 Aug found when build.py ran LAST. The second proves nothing in the run mutated it, and
# under sharding it proves that of the shard's own checkers, which is what it can honestly
# prove. Together they cost 0.84 s a shard.
BUILD = ("build.py", [])

# A HINT AND NOT A CLAIM. Measured seconds per unit, used only to decide which shard a unit
# lands in. A stale entry makes one shard finish later than another; it cannot make a unit
# run twice or not at all, because `assign()` is total over `units()` whatever the costs say.
# Refresh it from the `--- measured ... (paste into build/check_costs.json) ---` block every
# run prints at the end. Deliberately NOT
# policed by check_counts.py: that checker guards numbers DERIVED FROM THE CORPUS, and a
# wall-clock second on one machine is not one.
COSTS_PATH = ROOT / "build" / "check_costs.json"
DEFAULT_COST = 5.0


def test_files():
    """Every behaviour-test file, as a repo-relative path. Globbed, never listed: a suite
    that has to be enumerated by hand is a suite a new file can silently fall out of."""
    return sorted(str(p.relative_to(ROOT)) for p in sorted((ROOT / "tests").glob("test_*.py")))


def units():
    """(kind, key) for every piece of work a shard can be given, in run order.

    kind is "check" (a build/ script), "testfile" (one tests/test_*.py) or "suite".
    The pytest files are units for ASSIGNMENT and one invocation for EXECUTION -- a shard
    runs `pytest <its files>` once, not once per file, so the session-scoped fixtures in
    tests/conftest.py are still paid once per shard rather than once per file.
    """
    u = [("check", f"{s} {' '.join(a)}".strip()) for s, a in CHECKS if (s, a) != BUILD]
    u += [("testfile", f) for f in test_files()]
    u += [("suite", s) for s in EXTRA_SUITES if s != "pytest tests/"]
    return u


def costs():
    try:
        return json.loads(COSTS_PATH.read_text(encoding="utf-8"))["seconds"]
    except (OSError, ValueError, KeyError, TypeError):
        return {}


def assign(n):
    """{shard index 0..n-1: [(kind, key), ...]} -- longest-processing-time-first packing.

    LPT because the makespan is bounded below by the single largest unit whatever we do
    (tests/test_score.py is 422 s of the suite's 2,504), so the only thing a scheduler can
    win is the tail: place the big ones first and let the small ones fill in behind them.
    That floor is why six shards is where the curve goes flat: 6, 7 and 8 all land 422 s.
    `--list-units` re-derives it whenever anyone asks again.

    THE COSTS ARE THE RUNNER'S NOW, AND THE FIRST SET WERE NOT. Measured on a 4-core
    container, the table's TOTAL was right to 0.2% (2,503 against CI's 2,499) and its
    DISTRIBUTION was wrong enough to cost four minutes: the first sharded CI run came back
    306, 315, 346, 423, 465, 645 against a predicted flat 421. Two opposite measurement
    errors cancelled in the sum -- the per-file sweep ran three files at a time, inflating
    most of them (shards 4-6 came in at 0.73-0.82 of prediction), while the CP-SAT-bound
    files are far slower on a smaller runner (shard 3 at 1.62). **An aggregate that agrees is
    not evidence that the parts do**, and only the aggregate was ever checked.
    Ties break on the key so the partition is deterministic -- two shards computing this
    independently on two runners must agree, and a wall-clock-dependent split would be a
    race that shows up as a unit running twice.
    """
    c = costs()
    load = [0.0] * n
    out = {i: [] for i in range(n)}
    for kind, key in sorted(units(), key=lambda u: (-c.get(u[1], DEFAULT_COST), u[1])):
        i = min(range(n), key=lambda j: (load[j], j))
        out[i].append((kind, key))
        load[i] += c.get(key, DEFAULT_COST)
    return out


def pytest_target(my_files):
    """(argv-tail, label) for a shard's pytest invocation.

    A PURE FUNCTION AND NOT THREE LINES INSIDE run(), because it got this wrong once and
    nothing could see it. `my_files` arrives from `assign()` in longest-first order, so at
    1/1 -- which holds every file -- `my_files == test_files()` was FALSE, the whole-suite
    branch never fired, and the unsharded run invoked pytest with 78 explicit paths in cost
    order rather than `tests/`. It ran all 1,923 tests and passed. What it was not was the
    run this script did before it could shard, which is what the module docstring promises.
    The only surface that said so was the label in the log ("pytest tests/ (78 of 78
    files)"), and a claim whose only witness is a line of output nobody diffs is not guarded.

    Sorting is not tidiness either: alphabetical is the order `pytest tests/` collects in,
    and every claim this suite makes about order-independence was measured against it.
    """
    files = sorted(my_files)
    if not files:
        return [], None
    if files == test_files():
        return ["tests/"], "pytest tests/"
    return files, f"pytest tests/ ({len(files)} of {len(test_files())} files)"


def parse_shard(text):
    """"i/n" -> (i, n), 1-based and inclusive. Refuses anything else rather than guessing:
    a mistyped shard that silently ran everything, or ran nothing, would report a green
    build for a fraction of the work -- six times over, once per runner."""
    try:
        i, n = (int(p) for p in str(text).split("/"))
    except ValueError:
        raise SystemExit(f"--shard wants i/n (e.g. 2/6), not {text!r}")
    if not (1 <= i <= n) or n < 1:
        raise SystemExit(f"--shard {text}: i must be between 1 and n, and n at least 1")
    return i, n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--shard", default="1/1", metavar="i/n",
                    help="run only shard i of n (default 1/1: everything, as before)")
    ap.add_argument("--list-units", action="store_true",
                    help="print the shard assignment and the cost each unit is thought to "
                         "carry, then exit 0 without running anything")
    args = ap.parse_args(argv)
    shard_i, shard_n = parse_shard(args.shard)

    if args.list_units:
        c, plan = costs(), assign(shard_n)
        for i in range(shard_n):
            total = sum(c.get(k, DEFAULT_COST) for _kind, k in plan[i])
            print(f"\n--- shard {i + 1}/{shard_n}   {len(plan[i])} units   "
                  f"{total:.0f}s expected " + "-" * 20)
            for kind, k in plan[i]:
                known = "" if k in c else "   (no measurement; DEFAULT_COST)"
                print(f"  {c.get(k, DEFAULT_COST):8.2f}s  {kind:9s} {k}{known}")
        return

    mine = assign(shard_n)[shard_i - 1]
    my_checks = [k for kind, k in mine if kind == "check"]
    my_files = [k for kind, k in mine if kind == "testfile"]
    my_suites = [k for kind, k in mine if kind == "suite"]
    return run(shard_i, shard_n, my_checks, my_files, my_suites)


def run(shard_i, shard_n, my_checks, my_files, my_suites):
    results = []
    t0 = time.time()
    timings = {}
    sharded = shard_n > 1
    if sharded:
        print(f"### shard {shard_i}/{shard_n}: {len(my_checks)} checker(s), "
              f"{len(my_files)} test file(s), {len(my_suites)} suite(s). "
              f"build.py frames every shard and is not one of them.")

    def step(label, argv, cwd=ROOT, unit=None):
        print(f"\n=== {label} " + "=" * max(0, 60 - len(label)))
        t = time.time()
        rc = subprocess.run(argv, cwd=str(cwd)).returncode
        timings[unit or label] = time.time() - t
        return rc

    def check(label):
        script, _, argtext = label.partition(" ")
        args = argtext.split() if argtext else []
        return step(label, [sys.executable, str(ROOT / "build" / script)] + args, unit=label)

    # build.py FIRST, not last. It writes dist/taxonomy.json, and check_kits.py,
    # check_addresses.py and check_inheritance.py all READ that artefact. With build.py last,
    # every one of them validated the PREVIOUS run's graph: edit a lineage edge or a binding, and
    # the run that introduced the change measured the corpus as it was before it. The OQ 51 meter
    # -- whose whole purpose is to catch the cascade papering over something new -- was the worst
    # placed of the three. Only pytest caught it, and only because pytest happens to run after.
    # Found by audit 25 Aug 2026. It still runs at the end too, so a checker that mutates nothing
    # is proved not to have, and the artefact committed to git is the one the run just verified.
    # UNDER SHARDING both run in every shard: a shard is a whole checkout and the reader needs
    # the writer, and the closing run proves the shard's OWN checkers mutated nothing.
    results.append(("build.py", check("build.py")))

    # The checkers, in the order CHECKS states them -- `mine` is a set, and running a shard's
    # checkers in assignment order rather than corpus order would make a run's output depend on
    # the cost table, which is a hint. Order is the file's, always.
    for script, args in CHECKS:
        if (script, args) == BUILD:
            continue
        label = f"{script} {' '.join(args)}".strip()
        if label in my_checks:
            results.append((label, check(label)))

    if my_files:
        # ONE pytest for the shard's whole set, not one per file: tests/conftest.py's
        # session-scoped fixtures load plan_check, geometry, compose and the corpus, and paying
        # that per FILE would hand back most of what the sharding bought.
        #
        # A shard holding every file runs `pytest tests/` verbatim, so the unsharded run is
        # byte-identical to what this script did before it could shard -- the degenerate case
        # reproduces the old behaviour rather than approximating it.
        target, label = pytest_target(my_files)
        # `sys.executable -m pytest`, not the bare `pytest` on PATH. Every checker above already
        # runs under this interpreter, and a `pytest` from somewhere else runs the suite against a
        # different set of installed packages. Two sessions found this independently and it is worth
        # keeping both instances: WP-2.3 found the suite quietly SKIPPING all sixteen solver tests
        # while they passed when run directly, because the `pytest` first on PATH belonged to an
        # environment with no OR-Tools; the deployment work found an isolated pytest without the CAD
        # libs silently skipping the export tests while the selftests two lines up ran them. A skipped
        # test reports success, so the whole point of the entry point was being lost without a word.
        print(f"\n=== {label} " + "=" * max(0, 60 - len(label)))
        t = time.time()
        rc = subprocess.run([sys.executable, "-m", "pytest"] + target, cwd=str(ROOT)).returncode
        elapsed = time.time() - t
        # ONE PYTEST RUN MEASURES ONE PYTEST RUN. The first version of this divided `elapsed`
        # evenly across the shard's files and wrote that into the refreshable block -- so a
        # paste-back from an unsharded run would have flattened all 78 per-file figures to
        # their mean and destroyed the very balance the table exists to provide, while looking
        # exactly like a measurement. That is inventing a number and calling it measured, in
        # the file that says not to. A per-file figure needs a per-file run, so the block
        # carries one only when the shard held exactly one file, and says so otherwise.
        if len(my_files) == 1:
            timings[my_files[0]] = elapsed
        # normalized: pytest's own exit 3 means "internal error", not our
        # could-not-evaluate protocol — only the build/ checks speak that code
        results.append((label, 0 if rc == 0 else 1))

    if "pytest workbench/server/tests" in my_suites:
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
            wb = step("pytest workbench/server/tests",
                      [sys.executable, "-m", "pytest", "workbench/server/tests", "-q"])
            results.append(("pytest workbench/server/tests", 0 if wb == 0 else 1))

    if "node --test workbench/app" in my_suites:
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
                nrc = step("node --test workbench/app", [node, "--test", *specs], cwd=app,
                           unit="node --test workbench/app")
                results.append(("node --test workbench/app", 0 if nrc == 0 else 1))

    # build.py again, closing the frame: whatever this shard ran, dist/taxonomy.json is
    # still what the corpus says it should be.
    results.append(("build.py", check("build.py")))

    print("\n" + "=" * 60)
    print("SUMMARY")
    failed = [label for label, rc in results if rc not in (0, COULD_NOT_EVALUATE)]
    unjudged = [label for label, rc in results if rc == COULD_NOT_EVALUATE]
    for label, rc in results:
        state = "OK  " if rc == 0 else ("N/EV" if rc == COULD_NOT_EVALUATE else "FAIL")
        print(f"  {state}  {label}")

    # What this shard actually assembled, stated independently of what it ran, so a unit
    # dropped between assignment and execution fails the build instead of vanishing. Two
    # build.py framings, the shard's checkers, one pytest invocation if it holds any files,
    # and its suites.
    expected = 2 + len(my_checks) + (1 if my_files else 0) + len(my_suites)
    # TOTAL_CHECKS is a second statement of what this function assembles, and a second
    # statement is a thing that drifts -- this codebase's most-repeated defect. So the runner
    # holds itself to it: add or remove a suite without touching EXTRA_SUITES and check_all
    # fails here, loudly, instead of letting a published total quietly go wrong again.
    if shard_n == 1 and len(results) != TOTAL_CHECKS:
        print(f"\nFAIL: check_all ran {len(results)} checks but TOTAL_CHECKS says "
              f"{TOTAL_CHECKS}. A suite was added or removed without updating EXTRA_SUITES; "
              f"CLAUDE.md's published check total is derived from it.", file=sys.stderr)
        sys.exit(1)
    if len(results) != expected:
        print(f"\nFAIL: shard {shard_i}/{shard_n} was assigned {expected} pieces of work and "
              f"reported {len(results)}. A unit was dropped between assign() and run().",
              file=sys.stderr)
        sys.exit(1)

    # The block a cost-table refresh is pasted from. Printed on every run, in the shape
    # build/check_costs.json wants, because a table nobody can regenerate is a table that
    # rots into an imbalance nobody can explain. Only real measurements go in it: a shard
    # that ran many test files in one pytest process measured that process, not its files.
    unmeasured = [f for f in my_files if f not in timings]
    print(f"\n--- measured, {time.time() - t0:.0f}s in this shard "
          f"(merge into build/check_costs.json's \"seconds\") ---")
    print(json.dumps({k: round(v, 2) for k, v in sorted(timings.items())}, indent=1))
    if unmeasured:
        print(f"    {len(unmeasured)} test file(s) ran inside one pytest process and carry no "
              f"figure of their own here.\n"
              f"    For those: python3 -m pytest <file> -q, one at a time. An even split of "
              f"the run would look\n"
              f"    like a measurement and would flatten the table it was pasted into.")

    if failed:
        print(f"\n{len(failed)} of {len(results)} checks failed.")
        sys.exit(1)
    passed = len(results) - len(unjudged)
    where = "" if shard_n == 1 else f" in shard {shard_i}/{shard_n}"
    if unjudged:
        print(f"\n{passed} of {len(results)} checks passed{where}; {len(unjudged)} COULD NOT "
              f"EVALUATE (not a pass): {', '.join(unjudged)}")
    else:
        print(f"\nAll {len(results)} checks passed{where}.")


if __name__ == "__main__":
    main()
