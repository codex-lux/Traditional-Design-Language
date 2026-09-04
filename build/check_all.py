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
    # TOTAL_CHECKS is a second statement of what this function assembles, and a second
    # statement is a thing that drifts -- this codebase's most-repeated defect. So the runner
    # holds itself to it: add or remove a suite without touching EXTRA_SUITES and check_all
    # fails here, loudly, instead of letting a published total quietly go wrong again.
    if len(results) != TOTAL_CHECKS:
        print(f"\nFAIL: check_all ran {len(results)} checks but TOTAL_CHECKS says "
              f"{TOTAL_CHECKS}. A suite was added or removed without updating EXTRA_SUITES; "
              f"CLAUDE.md's published check total is derived from it.", file=sys.stderr)
        sys.exit(1)
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
