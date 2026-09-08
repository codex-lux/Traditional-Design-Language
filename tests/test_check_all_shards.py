"""`build/check_all.py --shard i/N` must be a PARTITION, and CI's N must be check_all's N.

WP-11.12. The corpus job was one 39 min 32 s serial step and is five parallel ones. The
whole risk of that change is in one sentence: a unit that lands in no shard runs nowhere,
and a suite that runs nowhere reports success. This repository has shipped that defect
before under several names -- the CI id gate whose loop body was unreachable, the
gazetteer ratchet that went quiet for want of a runtime, the walk CLAUDE.md called a guard
while no job ran it -- so the split is guarded rather than trusted.

Four things are held here, and the third is the one a reader should look at first:

1. `units()` covers everything there is to cover, and `assign()` is a partition of it.
2. The partition is deterministic, because two runners compute it independently.
3. **CI's matrix and CI's `--shard i/N` argument agree.** They are two numbers in one file
   and nothing else compares them. `matrix: [1,2,3,4,5]` against `--shard ${{...}}/6` runs
   five sixths of the suite and reports five green ticks.
4. The cost table names units that exist -- a stale key is a unit silently costed at
   DEFAULT_COST, which is a balance bug and not a correctness one, so it warns in the
   assertion message rather than being inferred from an imbalance six months later.
"""
import importlib.util
import json
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CI = os.path.join(ROOT, ".github", "workflows", "ci.yml")


def _check_all():
    spec = importlib.util.spec_from_file_location(
        "check_all_shard_mod", os.path.join(ROOT, "build", "check_all.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# The N CI runs at, and every N a person might reasonably type. 1 is the important one:
# it is `make check`, and it must still be the whole suite.
SHARD_COUNTS = (1, 2, 3, 4, 5, 6, 8, 13)


def test_every_unit_is_in_exactly_one_shard():
    """Total and disjoint, for every N. `assign()` places each unit at the argmin of a
    load vector, which is always in range 0..n-1 -- so this cannot fail today. It exists
    for the version of assign() somebody writes next: a filter, a skip, a `continue` on a
    unit whose cost is missing, and a fifth of the suite stops running behind five green
    ticks."""
    m = _check_all()
    all_keys = [k for _kind, k in m.units()]
    assert all_keys, "units() is empty -- the whole suite would run nowhere"
    for n in SHARD_COUNTS:
        plan = m.assign(n)
        assert sorted(plan) == list(range(n)), f"n={n}: shards are not 0..{n - 1}"
        placed = [k for i in range(n) for _kind, k in plan[i]]
        assert len(placed) == len(set(placed)), (
            f"n={n}: a unit is in more than one shard -- it would run twice and, worse, "
            f"two runners would mutate the same corpus file believing they were alone")
        assert sorted(placed) == sorted(all_keys), (
            f"n={n}: the shards do not cover units(). Missing: "
            f"{sorted(set(all_keys) - set(placed))}")


def test_one_shard_is_the_whole_suite():
    """`--shard 1/1` is `make check`, and every unit must be in it."""
    m = _check_all()
    assert [k for _kind, k in m.assign(1)[0]] != []
    assert sorted(k for _kind, k in m.assign(1)[0]) == sorted(k for _kind, k in m.units())


def test_the_partition_is_deterministic():
    """Five runners compute this independently and must agree. A tie broken on anything
    that varies between machines -- a dict order, a wall clock, a filesystem order --
    would show up as a unit running twice in one run and never in the next."""
    m = _check_all()
    assert m.assign(5) == m.assign(5)
    assert m.assign(5) == _check_all().assign(5)          # and across a fresh module load


def test_units_are_the_checks_the_test_files_and_the_suites():
    """The three sources, named, so adding a fourth kind of work without teaching units()
    about it fails here rather than running nowhere."""
    m = _check_all()
    kinds = {}
    for kind, key in m.units():
        kinds.setdefault(kind, []).append(key)

    expected_checks = [f"{s} {' '.join(a)}".strip() for s, a in m.CHECKS if (s, a) != m.BUILD]
    assert kinds["check"] == expected_checks
    assert len(expected_checks) == len(m.CHECKS) - 2, (
        "exactly the two build.py entries are framing rather than shardable units")

    on_disk = sorted(f for f in os.listdir(os.path.join(ROOT, "tests"))
                     if f.startswith("test_") and f.endswith(".py"))
    assert kinds["testfile"] == [f"tests/{f}" for f in on_disk]
    assert len(on_disk) > 50, "the tests/ glob matched almost nothing -- check test_files()"

    # "pytest tests/" is not a unit: the files are, and a shard runs one pytest over its own.
    assert kinds["suite"] == [s for s in m.EXTRA_SUITES if s != "pytest tests/"]
    assert "pytest tests/" not in kinds["suite"]


def test_ci_runs_as_many_shards_as_it_tells_check_all_there_are():
    """THE ONE THAT WOULD ACTUALLY CATCH SOMETHING. The matrix and the `--shard i/N`
    argument are two independent numbers in ci.yml, and a mismatch is silent in the
    dangerous direction: a matrix of 5 against `--shard i/6` runs five sixths of the
    suite and every shard is green."""
    ci = open(CI, encoding="utf-8").read()
    matrix = re.search(r"matrix:\s*\n\s*shard:\s*\[([0-9,\s]+)\]", ci)
    assert matrix, "ci.yml no longer declares a shard matrix"
    shards = [int(x) for x in matrix.group(1).split(",")]
    assert shards == list(range(1, len(shards) + 1)), (
        f"the matrix must be 1..N with no gaps; it is {shards}")

    denominators = set(re.findall(r"--shard \$\{\{ matrix\.shard \}\}/(\d+)", ci))
    assert denominators, "no `--shard ${{ matrix.shard }}/N` invocation found in ci.yml"
    assert denominators == {str(len(shards))}, (
        f"ci.yml runs a matrix of {len(shards)} shards and passes --shard i/{denominators} "
        f"to check_all.py. The suite would be split {denominators} ways and only "
        f"{len(shards)} of the pieces would ever run.")

    # And the job name a branch-protection rule is configured against still exists.
    assert re.search(r"name: corpus — check_all\.py", ci), (
        "the aggregate job's name changed. A required status check that stops existing "
        "stops being required, silently.")


def test_the_cost_table_names_units_that_exist():
    """A hint, so a stale entry is not a failure of correctness -- but a key naming a file
    that was renamed means that file is now costed at DEFAULT_COST, and the only symptom
    is one shard finishing five minutes after the others."""
    m = _check_all()
    known = {k for _kind, k in m.units()}
    table = json.load(open(m.COSTS_PATH, encoding="utf-8"))["seconds"]
    strays = sorted(set(table) - known)
    assert not strays, (
        f"build/check_costs.json costs {len(strays)} thing(s) that are not units: {strays}. "
        f"Renamed or removed; drop them, and re-measure whatever replaced them.")
    # Not the converse: a NEW unit with no measurement is fine and gets DEFAULT_COST. It is
    # reported rather than asserted, because failing the build for an uncosted new test file
    # would make adding a test file a two-step operation for no correctness gain.


def _junit(tmp_path, cases):
    """A JUnit report of `(classname, seconds)` pairs, written OUTSIDE the repository."""
    body = "".join(
        f'<testcase classname="{c}" name="t{n}" time="{t}"/>' for n, (c, t) in enumerate(cases))
    path = tmp_path / "pytest.xml"
    path.write_text(f'<?xml version="1.0"?><testsuites><testsuite name="pytest" '
                    f'tests="{len(cases)}">{body}</testsuite></testsuites>', encoding="utf-8")
    return str(path)


def test_the_refresh_block_never_invents_a_per_file_figure():
    """A shard runs its whole set in ONE pytest process, and TWICE now a per-file cost has been
    derived from that one number instead of measured. The first divided `elapsed` evenly, which
    would have flattened all 78 figures to their mean. The second -- shipped, and the reason
    this test was rewritten -- scaled each file by its own shard's ratio of measured to
    predicted: that makes every shard's TOTAL right by construction and leaves the shape inside
    it exactly as assumed as before, so the aggregate agreed while the distribution was four
    minutes wrong. Both looked like measurements.

    The figures come from pytest's own report now. This holds the source against the two
    retired instruments; the four tests below hold the reader itself."""
    body = open(os.path.join(ROOT, "build", "check_all.py"), encoding="utf-8").read()
    assert "elapsed / len(my_files)" not in body, (
        "the per-file timing is an even split of one pytest run again; pasting that back "
        "flattens build/check_costs.json to a single value per test file")
    assert "--junitxml=" in body and "per_file_seconds(junit" in body, (
        "the shard no longer costs its files from pytest's own report, so whatever figure it "
        "now prints into the refresh block is derived from the one number it measured")


def test_a_test_files_cost_is_its_own_cases_and_not_a_share_of_the_run(tmp_path):
    """The whole point: two files in one pytest process come back with their OWN times."""
    ca = _check_all()
    per, unattributed = ca.per_file_seconds(
        _junit(tmp_path, [("tests.test_axis.TestA", 1.0), ("tests.test_axis", 2.0),
                          ("tests.test_compass.TestB", 7.0)]),
        ["tests/test_axis.py", "tests/test_compass.py"])
    assert per == {"tests/test_axis.py": 3.0, "tests/test_compass.py": 7.0}
    assert unattributed == 0.0


def test_a_longer_module_name_is_not_credited_to_a_shorter_one(tmp_path):
    """THE TRAP A SUBSTRING TEST WALKS INTO, and there is a real pair: `tests.test_score` is a
    prefix of `tests.test_scoreboard`, and test_score.py is the 422 s file the whole makespan
    is bounded by. Crediting a sibling's cases to it would inflate the one figure that decides
    how many shards are worth running."""
    ca = _check_all()
    per, unattributed = ca.per_file_seconds(
        _junit(tmp_path, [("tests.test_scoreboard.TestX", 5.0), ("tests.test_score.TestY", 2.0)]),
        ["tests/test_score.py"])
    assert per == {"tests/test_score.py": 2.0}, "a sibling module's time landed on test_score.py"
    assert unattributed == 5.0, "the sibling's time must be reported, not silently dropped"


def test_time_that_cannot_be_attributed_is_reported_and_never_spread(tmp_path):
    """`unattributed` exists so that a reader whose classname-to-module reading has stopped
    matching the suite's layout sees a number rather than files that quietly grew. It must not
    be shared out over the files that DID match -- that is the invented figure again, wearing
    the clothes of a correction."""
    ca = _check_all()
    per, unattributed = ca.per_file_seconds(
        _junit(tmp_path, [("something.else.Entirely", 9.0), ("tests.test_axis.TestA", 1.0)]),
        ["tests/test_axis.py", "tests/test_compass.py"])
    assert per == {"tests/test_axis.py": 1.0, "tests/test_compass.py": 0.0}
    assert unattributed == 9.0


def test_a_file_that_contributed_no_case_costs_zero_rather_than_going_missing(tmp_path):
    """A file whose every test skipped is cheap, and that is a measurement. Leaving it out of
    the block would send it back to DEFAULT_COST on the next refresh -- a file silently
    re-costed by its own absence."""
    ca = _check_all()
    per, _ = ca.per_file_seconds(_junit(tmp_path, [("tests.test_axis.TestA", 1.0)]),
                                 ["tests/test_axis.py", "tests/test_compass.py"])
    assert per["tests/test_compass.py"] == 0.0
    assert set(per) == {"tests/test_axis.py", "tests/test_compass.py"}


def test_the_shard_holds_itself_to_what_it_was_assigned():
    """`run()` counts what it reported against what it was given, the same way the whole
    run counts itself against TOTAL_CHECKS. Source-read, like test_counts_guard.py's own
    guard on that arithmetic, because the alternative is running six shards in a test."""
    body = open(os.path.join(ROOT, "build", "check_all.py"), encoding="utf-8").read()
    assert "expected = 2 + len(my_checks)" in body, (
        "run() no longer derives what the shard was assigned; a unit dropped between "
        "assign() and run() would go unreported")
    assert re.search(r"len\(results\) != expected:\s*\n(?:.*\n)*?\s*sys\.exit\(1\)", body), (
        "the shard mismatch is detected but does not fail the run")


def test_the_unsharded_run_is_pytest_tests_verbatim():
    """THE BUG THIS TEST EXISTS FOR SHIPPED AND PASSED. `assign()` returns a shard's files in
    longest-first order, and the whole-suite branch compared that list against a SORTED one --
    so at 1/1, which holds every file, it was False, and the unsharded run invoked pytest with
    78 explicit paths in cost order rather than `tests/`. All 1,923 tests ran and passed; what
    it was not was the run `make check` did before this script could shard, which the module
    docstring promises. The only witness was the label in the log, and a claim whose only
    witness is a line of output nobody diffs is not guarded at all."""
    m = _check_all()
    every = [k for kind, k in m.assign(1)[0] if kind == "testfile"]
    assert every != sorted(every), (
        "assign() now returns files already sorted, so this test can no longer tell a sorted "
        "comparison from an unsorted one -- it has gone vacuous, not green")
    target, label = m.pytest_target(every)
    assert target == ["tests/"], (
        f"the unsharded run invokes pytest with {len(target)} argument(s) instead of `tests/`; "
        f"it is no longer the run it was before sharding")
    assert label == "pytest tests/"


def test_a_partial_shard_names_pytest_with_its_own_files_in_order():
    m = _check_all()
    some = [k for kind, k in m.assign(6)[0] if kind == "testfile"]
    target, label = m.pytest_target(some)
    assert target == sorted(some), "a shard must collect in the order `pytest tests/` would"
    assert target != ["tests/"]
    assert label.startswith("pytest tests/ (") and f"of {len(m.test_files())} files" in label


def test_a_shard_with_no_test_files_runs_no_pytest():
    """Not an empty `pytest` invocation, which collects the whole rootdir and would run the
    suite a seventh time."""
    m = _check_all()
    assert m.pytest_target([]) == ([], None)


@pytest.mark.parametrize("bad", ["6/5", "0/5", "oops", "5", "-1/5", "1/0"])
def test_a_shard_argument_that_cannot_be_honoured_is_refused(bad):
    """Never guessed at. A mistyped shard that quietly ran everything would report a green
    build for a fifth of the work -- or, worse, five identical green builds."""
    m = _check_all()
    with pytest.raises(SystemExit):
        m.parse_shard(bad)


def test_a_good_shard_argument_is_read_as_written():
    m = _check_all()
    assert m.parse_shard("3/5") == (3, 5)
    assert m.parse_shard("1/1") == (1, 1)
