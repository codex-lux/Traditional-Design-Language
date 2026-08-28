"""Guards for build/check_citations.py (WP-8.1, 28 Aug 2026).

The bug this exists for: every renumbering pass after an open-question collision has used a
regex of the form `\\bOQ (7[89]|8[0-5])\\b`, and that regex cannot see the second number in a
list. `OQ 82 and 84` renumbers the 82 and leaves the 84, and because the stale number still
names a REAL entry nothing dangles and no existence check fires. Three live instances were on
main, and one of them was written by a different session on a different branch -- which is what
makes it a class.

Every test here was verified to FAIL with the thing it guards reverted. That is the standard
the WP-7.5 audit set after it found six tests passing byte-identically on the code they were
written to protect, and the reason each test below drives the checker over a crafted fixture
rather than only over the live tree: a test that merely asserts the live tree is clean passes
just as well when the checker has stopped checking.
"""
import importlib.util
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod():
    spec = importlib.util.spec_from_file_location(
        "check_citations", os.path.join(ROOT, "build", "check_citations.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _run(*args):
    p = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_citations.py"), *args],
                       cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout


# ------------------------------------------------------------------ the live tree

def test_the_corpus_has_no_bare_dangling_or_broken_citation():
    rc, out = _run()
    assert rc == 0, out


def test_the_checker_is_actually_reading_something():
    """A checker that finds no citations reports 0 faults and exits 0, which is
    indistinguishable from a clean tree. The register's own shape has changed twice this
    week; if `N. **STATUS` stops parsing, this fires rather than the suite going quietly
    green on an empty population."""
    rc, out = _run("--verbose")
    n = int(re.search(r"^(\d+) citation\(s\) checked", out, re.M).group(1))
    rows = int(re.search(r"reissue rows\s+(\d+)", out).group(1))
    entries = int(re.search(r"register entries\s+(\d+)", out).group(1))
    assert n > 1000, f"only {n} citations found -- the detector has stopped matching"
    assert rows >= 20, f"only {rows} reissue rows -- the table parser has stopped matching"
    assert entries > 90, f"only {entries} register entries parsed"


# ------------------------------------------------------------------ check B, the load-bearing one

def test_a_bare_continuation_number_is_reported(tmp_path):
    """THE BUG ITSELF. `OQ 95 and 84` is what CLAUDE.md:286 actually said."""
    m = _mod()
    hits = [c.group(2) for c in m.CONT.finditer(
        m.CITE.search("(WP-7.4, OQ 95 and 84 CLOSED)").group(2))]
    assert hits == ["84"], hits


def test_a_fully_prefixed_list_is_not_reported():
    m = _mod()
    tail = m.CITE.search("(WP-7.4, OQ 95 and OQ 97 CLOSED)").group(2)
    assert not m.CONT.findall(tail or ""), "a correctly written list was flagged"


def test_a_date_after_a_citation_is_not_a_continuation_number():
    """The trap that made the first version of this detector useless: it reported 68 hits of
    which 46 were dates. `OQ 18, 24 Aug 2026` is correct prose and appears throughout the kit
    files. Pinned so a future tightening of the regex cannot quietly start convicting it."""
    m = _mod()
    for s in ("(OQ 18, 24 Aug 2026: reclassified from ...)",
              "(OQ 68, 26 Aug 2026). The band the author states ...",
              "(OQ 58, 24 Aug 2026) to the dress this node wears"):
        tail = m.CITE.search(s).group(2)
        assert not m.CONT.findall(tail or ""), f"date read as a citation list: {s}"


def test_fix_inserts_the_missing_prefixes_and_changes_nothing_else(tmp_path):
    """--fix must add `OQ ` and must not renumber, reorder or drop anything."""
    m = _mod()
    before = "raised OQ 47, 48 and 49 in WP-4.6, and OQ 18, 24 Aug 2026 stands"
    fixed = m.CITE.sub(
        lambda mm: mm.group(0)[:mm.start(2) - mm.start(0)]
        + m.CONT.sub(lambda c: f"{c.group(1)}OQ {c.group(2)}", mm.group(2) or ""),
        before)
    assert fixed == "raised OQ 47, OQ 48 and OQ 49 in WP-4.6, and OQ 18, 24 Aug 2026 stands"
    assert re.findall(r"\d+", before) == re.findall(r"\d+", fixed), "a number moved"


# ------------------------------------------------------------------ check A, the ratchet

def test_a_citation_naming_no_entry_is_reported():
    m = _mod()
    ids = m.entry_ids(open(os.path.join(ROOT, "docs", "open-questions.md"),
                           encoding="utf-8").read())
    assert 999 not in ids and max(ids) < 999
    assert int(m.CITE.search("see OQ 999 for this").group(1)) not in ids


def test_check_a_would_not_have_caught_this_bug_and_the_file_says_so():
    """Honesty about coverage, enforced. Both wrong ids named real entries, so the existence
    check was blind to all three. If someone strengthens check A they may delete this test;
    what they may not do is let the module imply it guards something it does not."""
    src = open(os.path.join(ROOT, "build", "check_citations.py"), encoding="utf-8").read()
    assert "would have caught NONE of them" in src


# ------------------------------------------------------------------ check C, the audit trail

def test_a_reissue_row_landing_on_no_entry_is_reported():
    m = _mod()
    rows = m.conversion_rows("| 72 | 78 | **911** | a subject |\n")
    assert rows and rows[0][2] == 911


def test_the_live_reissue_tables_all_land_on_real_entries():
    m = _mod()
    reg = open(os.path.join(ROOT, "docs", "open-questions.md"), encoding="utf-8").read()
    ids = m.entry_ids(reg)
    rows = m.conversion_rows(reg)
    assert len(rows) >= 20, f"table parser found only {len(rows)} rows"
    for ln, froms, to, subject in rows:
        assert to in ids, f"line {ln}: row lands on {to}, which no entry defines"


def test_the_four_collisions_are_all_still_recorded():
    """The conversion tables are the only thing that makes a pre-merge commit message
    readable -- a bare `OQ 78` in this branch's history means one thing before the third
    collision and another after. Losing a table silently would strand that history.

    THIS COUNTS TABLES, NOT HEADINGS, and the first version of it counted headings and
    failed: the register records its four collisions in two different forms, two under a
    `## Reissued ...` heading and the third under a bold `A THIRD PARALLEL-SESSION
    COLLISION` paragraph. All four mappings are present and correct; only the presentation
    is inconsistent. Pinning the heading would have been pinning a house style nobody
    agreed to, and would break the moment someone tidied it."""
    m = _mod()
    reg = open(os.path.join(ROOT, "docs", "open-questions.md"), encoding="utf-8").read()
    rows = m.conversion_rows(reg)
    groups, prev = 1, rows[0][0]
    for ln, _f, _t, _s in rows[1:]:
        if ln - prev > 3:          # a gap of prose means a new table
            groups += 1
        prev = ln
    assert groups >= 4, (
        f"found {groups} conversion table(s) in {len(rows)} rows; four collisions have "
        f"happened and each needs its mapping kept")


def test_the_tally_list_stays_bare_and_the_two_guards_do_not_contradict_each_other():
    """A TENSION BETWEEN TWO GUARDS, pinned before it bites someone.

    `test_wp46_packs.py`'s derivation test reads CLAUDE.md's open-question list with the
    character class `[\\d, ]+`, so that list MUST be bare numbers -- `OQ 7, OQ 8` contains
    letters, matches nothing, and fires the assertion on an empty set. Check B in
    check_citations.py forbids the opposite: a bare number following an `OQ N` citation.

    They coexist only because the tally line carries no `OQ` prefix at all, so check B's
    `OQ \\d+` anchor never engages on it. Someone tidying that line into `OQ 7, OQ 8, ...`
    would satisfy the instinct check B teaches and break the derivation test. This test says
    so out loud, and fails if the line stops being bare."""
    md = open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").read()
    m = re.search(r"of which \d+ are open\*\*\s*\n?\s*\(([^)]+)\)", md)
    assert m, "the tally list is no longer where either guard looks for it"
    assert re.fullmatch(r"[\d, ]+", m.group(1)), (
        f"the open-question tally must stay BARE numbers for test_wp46_packs.py's "
        f"derivation regex; found {m.group(1)[:60]!r}")
    m2 = _mod()
    assert not m2.CITE.search("(" + m.group(1) + ")"), (
        "the tally list has acquired an OQ prefix -- check B will now flag it and the "
        "derivation test will stop matching")


def test_the_specimen_exemption_is_exactly_two_files_and_no_more():
    """This checker exempts its own source and this test file, because both hold the malformed
    shape on purpose -- a checker that convicts its own specification cannot be kept. That
    exemption is also the obvious place to hide a real violation, so it is pinned at exactly
    two paths. This package's own report tripped check B during development and was FIXED
    rather than added here, which is the behaviour this test protects."""
    m = _mod()
    assert m.SPECIMEN == {"build/check_citations.py", "tests/test_citations.py"}, (
        f"the specimen exemption has changed: {sorted(m.SPECIMEN)}. Anything beyond the "
        f"checker and its fixtures must comply with the rule, not be excused from it.")


def test_untracked_files_are_scanned():
    """A NEW file is exactly where a fresh citation lives, and `git grep` without --untracked
    reads only committed ones. During this package the report quoted the bug form and was
    invisible to the checker until `git add` -- the worst possible moment to start checking."""
    src = open(os.path.join(ROOT, "build", "check_citations.py"), encoding="utf-8").read()
    assert '"--untracked"' in src, "the checker has stopped seeing uncommitted files"
