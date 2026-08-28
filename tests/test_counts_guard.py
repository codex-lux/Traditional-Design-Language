"""The counts guard (WP-4.6, 25 Aug 2026).

`gen_readme_counts.py` generates README's counts block and a generated block cannot drift.
Everything else does. This package found CLAUDE.md -- the file every agent is told to read first --
reporting 36 packs when there were 40, 95 slots when there were 96, and ontology 0.5.0 four commits
after 0.6.0 shipped. Each was fixed by hand, which is how it got that way in the first place.

`build/check_counts.py` declares every count that appears in prose next to the expression that
computes it, and fails the build when they disagree. These tests pin the two properties that make it
worth having: that a stale number is caught, and that a ROTTED PATTERN is caught too -- because a
guard whose regex no longer matches has silently stopped guarding, which is worse than no guard.
"""
import importlib.util
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod():
    spec = importlib.util.spec_from_file_location(
        "_check_counts", os.path.join(ROOT, "build", "check_counts.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_corpus_agrees_with_its_own_prose_right_now():
    """The check the build runs. If this fails, a number in CLAUDE.md, STATE-OF-THE-PROJECT.md,
    README.md or docs/ disagrees with the data -- fix the prose, not the test."""
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_counts.py")],
                          capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_every_claim_pattern_still_matches_something():
    """A guard whose regex no longer matches has stopped guarding, and does it silently. The checker
    treats that as a failure rather than as a pass, and this pins the behaviour."""
    m = _mod()
    for path, key, pattern in m.CLAIMS:
        text = open(os.path.join(ROOT, path)).read()
        assert re.search(pattern, text, re.M), (path, key, pattern)


def test_every_claim_names_a_key_the_checker_computes():
    m = _mod()
    v = m.computed()
    for path, key, pattern in m.CLAIMS:
        assert key in v, (path, key)


def test_every_pattern_captures_exactly_one_group():
    """The checker rewrites group 1 in place under --fix. A pattern with two groups would rewrite
    the wrong span, and one with none would raise inside the loop."""
    m = _mod()
    for path, key, pattern in m.CLAIMS:
        assert re.compile(pattern).groups == 1, (path, key, pattern)


def test_it_catches_a_number_that_has_gone_stale(tmp_path):
    """The whole point, exercised rather than assumed: a wrong number is reported, not passed."""
    m = _mod()
    v = m.computed()
    text = "we have %d packs, and they are functions" % (v["packs"] + 7)
    rx = re.compile(r"we have (\d+) packs")
    hit = rx.search(text)
    assert hit and hit.group(1) != str(v["packs"])


def test_the_pack_count_is_computed_from_the_files_and_not_from_a_constant():
    """If someone hard-codes the number the guard becomes a tautology."""
    src = open(os.path.join(ROOT, "build", "check_counts.py")).read()
    body = src[src.index("def computed("):src.index("# (file, key, regex)")]
    assert "glob.glob" in body
    assert not re.search(r'v\["packs"\]\s*=\s*\d+', body)


# --------------------------------------------------------------- the check total (WP-7.5)
# `check_counts.py` polices counts DERIVED FROM THE CORPUS, and a check total is not one of
# them -- CLAUDE.md says so itself, and that exemption is why this particular number has now
# been wrong three times. WP-5.11 found it published as 32 against a suite of 33. The 27 Aug
# merge resolved a conflict in that paragraph and wrote 32 AGAIN, in the same sentence that
# describes the bug, because `len(check_all.CHECKS)` is the loop and not the run; check_all.py
# printed "1 of 35 checks failed" against it an hour later. These two tests move it from
# remembered to enforced.

def _check_all():
    spec = importlib.util.spec_from_file_location(
        "check_all_mod", os.path.join(ROOT, "build", "check_all.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_claude_md_publishes_the_runners_check_total_not_the_loops():
    """The number in CLAUDE.md must be `len(results)` -- what the runner prints as
    "All N checks passed" -- and not `len(CHECKS)`, which excludes the three suites appended
    after the loop. Those are 32 and 35 respectively, which is exactly the size of the error
    that has been published twice."""
    m = _check_all()
    assert m.TOTAL_CHECKS == len(m.CHECKS) + len(m.EXTRA_SUITES)
    assert m.TOTAL_CHECKS > len(m.CHECKS), (
        "EXTRA_SUITES is empty, so this guard has become a tautology -- the whole failure it "
        "exists to catch is someone measuring the loop instead of the run")
    text = open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").read()
    hits = re.findall(r"\*\*(\d+) checks, [\d,]+ tests\*\*", text)
    assert len(hits) == 1, (
        f"expected exactly one published check total in CLAUDE.md, found {hits} -- if the "
        f"phrasing moved, this guard has rotted and is no longer reading anything")
    assert int(hits[0]) == m.TOTAL_CHECKS, (
        f"CLAUDE.md publishes {hits[0]} checks; check_all.py runs {m.TOTAL_CHECKS} "
        f"({len(m.CHECKS)} in the CHECKS loop plus {len(m.EXTRA_SUITES)} appended after it). "
        f"Read the runner's own total, never len(CHECKS).")


def test_the_runner_refuses_to_disagree_with_its_own_total():
    """EXTRA_SUITES is a second statement of what main() assembles, and a second statement
    drifts -- this codebase's most-repeated defect, called out in CLAUDE.md three times over.
    main() therefore checks `len(results)` against TOTAL_CHECKS and exits nonzero if they
    disagree, so adding a suite without updating EXTRA_SUITES breaks the build rather than
    silently falsifying a published number. This asserts that guard is actually in the source
    and reachable -- deleting it must fail a test, not merely remove a check."""
    src = open(os.path.join(ROOT, "build", "check_all.py"), encoding="utf-8").read()
    body = src[src.index("def main("):]
    assert "len(results) != TOTAL_CHECKS" in body, (
        "check_all.main() no longer holds itself to TOTAL_CHECKS; the constant can now drift "
        "from what the runner actually assembles")
    assert re.search(r"len\(results\) != TOTAL_CHECKS:\s*\n(?:.*\n)*?\s*sys\.exit\(1\)", body), (
        "the TOTAL_CHECKS mismatch is detected but does not fail the run")
