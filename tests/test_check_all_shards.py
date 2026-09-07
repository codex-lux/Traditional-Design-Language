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


def test_the_shard_holds_itself_to_what_it_was_assigned():
    """`run()` counts what it reported against what it was given, the same way the whole
    run counts itself against TOTAL_CHECKS. Source-read, like test_counts_guard.py's own
    guard on that arithmetic, because the alternative is running five shards in a test."""
    body = open(os.path.join(ROOT, "build", "check_all.py"), encoding="utf-8").read()
    assert "expected = 2 + len(my_checks)" in body, (
        "run() no longer derives what the shard was assigned; a unit dropped between "
        "assign() and run() would go unreported")
    assert re.search(r"len\(results\) != expected:\s*\n(?:.*\n)*?\s*sys\.exit\(1\)", body), (
        "the shard mismatch is detected but does not fail the run")


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
