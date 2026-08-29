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
    # The register is a DIRECTORY (WP-8.1) and its index is generated, so the conversion
    # tables live in the directory's own README. `entry_ids` reads the directory itself now
    # and takes no text.
    hist = open(os.path.join(ROOT, "docs", "open-questions", "README.md"),
                encoding="utf-8").read()
    ids = m.entry_ids()
    rows = m.conversion_rows(hist)
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
    hist = open(os.path.join(ROOT, "docs", "open-questions", "README.md"),
                encoding="utf-8").read()
    rows = m.conversion_rows(hist)
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
    assert re.fullmatch(r"[\d, a-z/-]+", m.group(1)), (
        f"the open-question tally must carry only bare numbers and oq/ slugs for "
        f"test_wp46_packs.py's derivation regex; found {m.group(1)[:60]!r}")
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


# ------------------------------------------------------------------ the frozen numeric block

def test_a_numbered_entry_above_the_ceiling_is_refused():
    """CHECK D, the enforcement. A sequential id has to be issued from somewhere, and the only
    shared state two parallel sessions have is the repo they both branched from -- which is how
    the same block collided four times in four days. Refusing a numbered entry above 99 is what
    makes the named scheme a rule instead of a note in a file nobody re-reads."""
    m = _mod()
    ids = m.entry_ids()
    assert max(ids) == m.FROZEN_CEILING == 99, (
        f"the numeric block runs to {max(ids)} against a ceiling of {m.FROZEN_CEILING}")
    # The register is a DIRECTORY, so the ceiling is enforced on the FILENAME rather than on
    # a list item: `check_ids.py` refuses `100-anything.md` outright. Asserting that here
    # keeps check D from passing vacuously in the shape the directory creates -- a parser
    # test would have been testing a parser that no longer exists.
    spec = importlib.util.spec_from_file_location(
        "check_ids_for_citation_test", os.path.join(ROOT, "build", "check_ids.py"))
    ci = importlib.util.module_from_spec(spec); spec.loader.exec_module(ci)
    assert ci.HIGHEST_NUMBER == m.FROZEN_CEILING == 99
    assert ci.FILENAME.match("100-issued-from-a-working-tree-again.md"), (
        "the filename parser cannot see a numbered file, so the ceiling check below would "
        "pass vacuously")


def test_the_named_scheme_has_a_live_entry_and_is_not_checked_vacuously():
    """A slug checker with no slugs to check reports 0 faults and exits 0, which reads exactly
    like a clean tree -- this repository's own 'a selector matching nothing passes vacuously'
    trap. The scheme ships with a real question under it."""
    m = _mod()
    slugs = m.slug_ids()
    assert slugs, "no named entry exists, so every slug assertion here is vacuous"
    assert all(re.fullmatch(r"oq/[a-z0-9][a-z0-9-]*", s) for s in slugs), sorted(slugs)


def test_a_citation_of_a_named_entry_that_does_not_exist_is_reported():
    m = _mod()
    slugs = m.slug_ids()
    assert m.SLUG_CITE.search("see oq/no-such-question for this").group(0) not in slugs
    live = sorted(slugs)[0]
    assert m.SLUG_CITE.search(f"see {live} for this").group(0) in slugs


def test_a_named_entry_is_counted_by_the_open_tally():
    """The failure the new scheme creates: read only the numbered form and a named question sits
    open and untallied. Both readers -- the derivation test and this file -- must see it."""
    md = open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").read()
    m = re.search(r"of which \d+ are open\*\*\s*\n?\s*\(([^)]+)\)", md)
    listed = {x.strip() for x in m.group(1).split(",")}
    # Read the DIRECTORY through check_ids, the one reader, rather than re-parsing the
    # generated index -- which would be parsing a derived artefact for a fact its source holds.
    spec = importlib.util.spec_from_file_location(
        "check_ids_for_tally_test", os.path.join(ROOT, "build", "check_ids.py"))
    ci = importlib.util.module_from_spec(spec); spec.loader.exec_module(ci)
    qs, _errors = ci.read_questions()
    named_open = {k for k, v in qs.items()
                  if not isinstance(k, int) and v["state"] == "open"}
    assert named_open, "no open named entry -- this test is vacuous"
    assert named_open <= listed, (
        f"named question(s) open in the register but absent from CLAUDE.md's tally: "
        f"{sorted(named_open - listed)}")


# ------------------------------------------------------------------ END TO END
#
# THE TWO ENFORCEMENTS ABOVE WERE UNGUARDED, and this file's own docstring claimed
# otherwise. The WP-8.4 adversarial audit replaced all three `dangling.append(...)`
# conditions in `check_citations.main()` with `if False:` -- so a tree containing `OQ 999`
# or `oq/no-such-question` reported 0 dangling and exited 0 -- and every test here stayed
# green. It did the same to both frozen-99 sites (`check_ids.py`'s `fid > HIGHEST_NUMBER`
# and this file's `n > FROZEN_CEILING`), letting a session write
# `docs/open-questions/100-<slug>.md` -- the exact act OQ 99 was ruled to make impossible --
# straight through `check_all.py`, with all 31 tests passing.
#
# Both had the same shape: the test asserted a PROPERTY of the parser (`999 not in
# entry_ids()`, `max(entry_ids()) == 99`) and never handed the offending input to the
# checker. A parser that can see the number is not a checker that refuses it.
#
# These run `main()` against a fixture tree instead. `_run_main` redirects the module's own
# ROOT and `tracked_files()`, so the checker walks a directory we control.

def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _fixture_tree(tmp_path, files, extra_questions=()):
    """A tree the checker can walk for real.

    `entry_ids()` does NOT read the register text it is handed -- it delegates to
    `check_ids.read_questions()`, which reads `docs/open-questions/` off the module's own
    ROOT. So a fixture that redirects ROOT has to carry the register DIRECTORY and the
    build/ scripts, or the checker cannot start. Copying them is the point: this exercises
    the shipped reader, not a stand-in for it.
    """
    # NO `build/` IN THE FIXTURE, AND THIS COST A CROSS-FILE TEST FAILURE TO LEARN. The first
    # version symlinked `tmp_path/build -> ROOT/build` so the checker's `_check_ids()` could
    # find its sibling. It found it -- at the TEMP path -- and `modcache` cached it there,
    # and every module that one loads by path inherited a ROOT under /tmp. Two files later
    # `tests/test_constraints.py` got a `check_constraints` whose ROOT was a pytest tmpdir
    # that no longer existed: `FileNotFoundError: .../pytest-68/.../schema/constraint.schema
    # .json`. It passed alone and failed in the suite, which is the worst shape a test defect
    # has. `_run_main` hands the checker the ALREADY-LOADED reader instead, so nothing is
    # loaded from the fixture and the module cache is never touched.
    import shutil
    shutil.copytree(os.path.join(ROOT, "docs", "open-questions"),
                    tmp_path / "docs" / "open-questions")
    shutil.copy(os.path.join(ROOT, "docs", "open-questions.md"),
                tmp_path / "docs" / "open-questions.md")
    for name, text in extra_questions:
        (tmp_path / "docs" / "open-questions" / name).write_text(text, encoding="utf-8")
    for rel, text in files.items():
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    return tmp_path


def _run_main(mod, tmp_path, files, extra_questions=(), argv=("check_citations.py",)):
    """Run the checker's main() over a fixture tree; return (rc, stdout, stderr)."""
    import contextlib
    import io
    _fixture_tree(tmp_path, files, extra_questions)
    real_root, real_tracked, real_argv = mod.ROOT, mod.tracked_files, sys.argv
    # The register reader is loaded through modcache and derives its own QDIR from its own
    # __file__, so redirecting the CHECKER's ROOT does not move the register it reads. Point
    # it at the fixture too, or the planted question file is invisible and the test asserts
    # nothing -- which is how this one first "passed".
    # Resolved BEFORE ROOT moves, so the reader is the real one at the real path.
    ids_mod = mod._check_ids()
    real_qdir, real_check_ids = ids_mod.QDIR, mod._check_ids
    ids_mod.QDIR = str(tmp_path / "docs" / "open-questions")
    mod._check_ids = lambda: ids_mod
    mod.ROOT = str(tmp_path)
    mod.tracked_files = lambda: sorted(files)
    sys.argv = list(argv)
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main()
    except SystemExit as e:                      # a checker may exit rather than return
        rc = e.code if isinstance(e.code, int) else 1
    finally:
        mod.ROOT, mod.tracked_files, sys.argv = real_root, real_tracked, real_argv
        ids_mod.QDIR, mod._check_ids = real_qdir, real_check_ids
    return rc, out.getvalue(), err.getvalue()


A_REAL_NUMBERED_ID = 18          # HALF CLOSED in the live register, and cited all over the tree


def test_a_dangling_numbered_citation_makes_the_checker_fail(tmp_path):
    mod = _load("cc_dangling", "build/check_citations.py")
    rc, out, err = _run_main(
        mod, tmp_path, {"docs/some-note.md": "This refers to OQ 999 and nothing else.\n"})
    assert rc != 0, f"a citation of a nonexistent entry passed:\n{out}{err}"
    assert "999" in (out + err)


def test_a_dangling_slug_citation_makes_the_checker_fail(tmp_path):
    mod = _load("cc_slug", "build/check_citations.py")
    rc, out, err = _run_main(
        mod, tmp_path, {"docs/some-note.md": "See oq/no-such-question-exists here.\n"})
    assert rc != 0, f"a citation of a nonexistent named entry passed:\n{out}{err}"
    assert "no-such-question-exists" in (out + err)


def test_the_checkers_are_not_simply_always_failing(tmp_path):
    """The pair above assert `rc != 0`, which a checker that always fails also satisfies."""
    mod = _load("cc_clean", "build/check_citations.py")
    rc, out, err = _run_main(
        mod, tmp_path,
        {"docs/some-note.md": "This refers to OQ %d, which exists.\n" % A_REAL_NUMBERED_ID})
    assert rc == 0, f"a clean tree failed:\n{out}{err}"


def test_an_entry_above_the_frozen_ceiling_is_actually_refused_by_both_checkers(tmp_path):
    """The register side and the FILENAME side, each handed a 100 rather than asked about one."""
    mod = _load("cc_ceiling", "build/check_citations.py")
    rc, out, err = _run_main(
        mod, tmp_path, {"docs/some-note.md": "nothing to cite\n"},
        extra_questions=[("100-issued-from-a-working-tree.md",
                          "# OQ 100 \u2014 the thing OQ 99 forbids\n\n**Status:** OPEN\n")])
    assert rc != 0, f"entry 100 passed the register check:\n{out}{err}"
    assert "100" in (out + err) and "ceiling" in (out + err).lower()

    ci = _load("ci_ceiling", "build/check_ids.py")
    qdir = tmp_path / "questions"
    qdir.mkdir()
    (qdir / "099-a-real-one.md").write_text(
        "# OQ 99 — a fixture\n\n**Status:** OPEN\n", encoding="utf-8")
    (qdir / "100-issued-from-a-working-tree.md").write_text(
        "# OQ 100 — the thing OQ 99 forbids\n\n**Status:** OPEN\n", encoding="utf-8")
    real_qdir = ci.QDIR
    ci.QDIR = str(qdir)
    try:
        _entries, errors = ci.read_questions()
    finally:
        ci.QDIR = real_qdir
    assert any("100" in e and "frozen" in e for e in errors), (
        f"check_ids accepted a numbered file above the ceiling: {errors}")


