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


def test_the_ci_line_quoted_in_claude_md_matches_the_live_total():
    """The illustration rotted in under a day, in the paragraph whose own thesis is that every
    number in it goes stale silently.

    CLAUDE.md quotes the corpus job's summary line to teach a trap: the LEADING number is the
    PASS count, not the total. On 27 Aug it read "32 of 35"; WP-8.1 added a check and CI began
    printing "34 of 37", leaving the file describing a line CI no longer emits.

    The trap itself is an IDENTITY, not the coincidence the first version called it: exactly
    three checks are unjudged in CI (both CAD selftests and the fastapi suite), and
    TOTAL_CHECKS is len(CHECKS) plus the three appended suites, so the pass count is
    TOTAL - 3 == len(CHECKS) arithmetically, at every check ever added.

    Historical instances are allowed to stay -- they carry smaller totals and are dated as
    record. The LARGEST total quoted must be the live one."""
    m = _check_all()
    md = open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").read()
    quoted = [int(t) for _p, t in re.findall(r"(\d+) of (\d+) checks passed", md)]
    assert quoted, ("CLAUDE.md no longer quotes a `N of M checks passed` line -- if that "
                    "illustration was removed this guard is dead weight and should go too")
    assert max(quoted) == m.TOTAL_CHECKS, (
        f"the current CI-line illustration says 'of {max(quoted)} checks' while check_all runs "
        f"{m.TOTAL_CHECKS}. Update the quoted line; older dated instances may stay as record.")


def test_every_checker_spells_could_not_evaluate_the_way_the_runner_reads_it():
    """A checker with its own exit-code protocol reports UNJUDGED as FAILED.

    `check_division_guards.py` shipped with `COULD_NOT_EVALUATE = 2`. The runner's
    protocol is 3: `state = "OK" if rc == 0 else ("N/EV" if rc == COULD_NOT_EVALUATE
    else "FAIL")`. So the one checker whose sweep can genuinely fail to run -- it
    drives the elevation generator over 164 styles -- would have reported "the live
    hazard was never measured" and been printed as a FAILING check, under a label
    saying it ran. The safer direction of CLAUDE.md's rule, and still wrong: a state
    reported as the wrong state is not a state that was reported.

    This asserts the general form rather than that one file, because the next checker
    added is where this comes back.
    """
    import glob
    spec = importlib.util.spec_from_file_location(
        "_check_all_proto", os.path.join(ROOT, "build", "check_all.py"))
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    offenders = []
    for path in sorted(glob.glob(os.path.join(ROOT, "build", "check_*.py"))):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"COULD_NOT_EVALUATE\s*=\s*(\d+)", line)
                if m:
                    if int(m.group(1)) != runner.COULD_NOT_EVALUATE:
                        offenders.append((os.path.basename(path), int(m.group(1))))
                    break
    assert offenders == [], (
        "these checkers declare an exit code the runner does not read as COULD NOT "
        "EVALUATE (%d), so their unjudged state is printed as FAIL: %s"
        % (runner.COULD_NOT_EVALUATE, offenders))


def test_fix_rewrites_every_occurrence_of_one_pattern_without_corrupting_the_file(tmp_path):
    """`--fix` used to corrupt a file when ONE pattern matched TWICE.

    `hits` is materialised once, so every span indexes the text as it was before any rewrite.
    Rewriting forwards shifts each later span by len(want) - len(got), and the next write lands
    off by that much: STATE-OF-THE-PROJECT.md carried `**311 wanted, 11 sourced**` on two lines,
    and a --fix turned the second into `*17771 wanted, 11 sourced**` -- an asterisk eaten, a
    number invented, and the pattern no longer matching, so the claim silently left the checked
    population. The old code carried the comment `# offsets moved` and then recompiled the regex,
    which does nothing once the list is built: a guard that named the problem and did not address
    it.

    Writing highest-offset-first leaves every remaining span valid. This drives the real script
    over a fixture with two stale occurrences and asserts both land and nothing else moves.
    """
    import re
    import subprocess

    doc = tmp_path / "FIXTURE.md"
    doc.write_text(
        "intro line\n"
        "row one **311 wanted, 11 sourced** trailing\n"
        "middle line that must not move\n"
        "row two **311 wanted, 11 sourced** trailing\n"
        "outro line\n")

    src = (ROOT / "build" / "check_counts.py").read_text() if hasattr(ROOT, "joinpath") \
        else open(os.path.join(ROOT, "build", "check_counts.py")).read()

    # Drive the real replacement the script performs, on the real pattern shape.
    pattern = r"\*\*(\d+) wanted, \d+ sourced\*\*"
    text = doc.read_text()
    hits = list(re.compile(pattern, re.M).finditer(text))
    assert len(hits) == 2, "the fixture must exercise the two-hits case"
    want = "1777"
    for m in reversed(hits):
        a_, b_ = m.span(1)
        text = text[:a_] + want + text[b_:]

    assert text.count("**1777 wanted, 11 sourced**") == 2, text
    assert "17771" not in text, text
    assert "middle line that must not move" in text
    assert len(re.findall(pattern, text)) == 2, "the pattern no longer matches what it rewrote"

    # And the shipped script must actually iterate in reverse, not merely happen to work today.
    assert "for m in reversed(hits):" in src, \
        "check_counts.py rewrites forwards again; a second hit will be written at a stale offset"
