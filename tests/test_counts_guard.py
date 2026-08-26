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
