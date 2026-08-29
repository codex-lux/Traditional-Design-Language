"""The register is a directory, and these are the guards that make that mean something.

Four open-question id collisions in four days, every one from the same habit -- read the
working tree, find the highest number, add one -- and every one paid for after the merge
with a sweep of ~1,500 references. The cause was structural: `docs/open-questions.md` was
ONE FILE, so two branches appending id 99 produced a *text* conflict, which git resolves by
juxtaposition. Both entries survive, both numbered 99, and nothing notices.

**Nothing checked for a duplicate id anywhere in this corpus.** The derivation test in
`test_wp46_packs.py` parsed the register with `re.findall` and collected the result into a
**set**, so two entries numbered 78 collapsed to one member and it stayed green. The guard
against the exact failure this project suffered four times was structurally incapable of
seeing it.

Every assertion here is written to FAIL against the code it guards -- the file is
mutation-checked, per the lesson of WP-5.7's audit, which found eleven of forty-three new
assertions passing on the very code they were written to catch.
"""
import importlib.util
import os
import re
import shutil

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QDIR = os.path.join(ROOT, "docs", "open-questions")


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def ci():
    return _mod("check_ids_t", "build/check_ids.py")


def test_the_register_is_a_directory_of_one_file_per_question(ci):
    """The whole fix in one assertion. If this ever reads a single file again, two sessions
    can issue the same id and git will merge them without a word."""
    assert os.path.isdir(QDIR), "the register must be a directory -- see build/check_ids.py"
    files = sorted(f for f in os.listdir(QDIR)
                   if f.endswith(".md") and f != "README.md")
    assert len(files) >= 98, f"only {len(files)} question files"
    qs, errors = ci.read_questions()
    assert not errors, errors
    assert len(qs) == len(files), "every file is exactly one question and vice versa"


def test_every_filename_states_its_own_id_and_no_two_agree(ci):
    """`filename == id` is what turns a collision into an add/add conflict git refuses to
    resolve, instead of two entries under one number inside one file."""
    qs, errors = ci.read_questions()
    assert not errors, errors
    for qid, rec in qs.items():
        # Two namespaces since 28 Aug 2026 (OQ 99): `<nnn>-<slug>.md` for the frozen numeric
        # block, `oq-<slug>.md` for every question raised after it. Both are filename == id,
        # which is the property that makes a duplicate an add/add conflict git refuses rather
        # than a text conflict it merges by juxtaposition.
        text = open(os.path.join(QDIR, rec["file"]), encoding="utf-8").read()
        if isinstance(qid, int):
            assert rec["file"].startswith(f"{qid:03d}-"), rec
            heading = re.search(r"^# OQ (\d+) — ", text, re.M)
            assert heading and int(heading.group(1)) == qid, (
                f"{rec['file']} disagrees with its own heading — the one disagreement a "
                f"directory cannot prevent by itself")
        else:
            assert rec["file"] == "oq-%s.md" % qid[len("oq/"):], rec
            heading = re.search(r"^# (oq/[a-z0-9][a-z0-9-]*) — ", text, re.M)
            assert heading and heading.group(1) == qid, (
                f"{rec['file']} disagrees with its own heading")
    assert len(set(qs)) == len(qs)


def test_a_duplicate_id_is_caught_and_this_assertion_is_proved_against_the_bug(ci, tmp_path):
    """MUTATION-CHECKED, and this is the test that matters most: plant a second file carrying
    an id that already exists and require the checker to name it. Before 28 Aug 2026 nothing
    in this corpus would have. Two sessions issuing id 99 with DIFFERENT slugs create two
    different PATHS, so even a directory does not raise a git conflict -- only this does,
    plus the CI step that compares the branch's ids against its base."""
    victim = sorted(f for f in os.listdir(QDIR)
                    if f.endswith(".md") and f != "README.md")[0]
    planted = os.path.join(QDIR, victim[:4] + "a-planted-duplicate-for-this-test.md")
    shutil.copy(os.path.join(QDIR, victim), planted)
    try:
        _, errors = ci.read_questions()
        assert any("DUPLICATE ID" in e for e in errors), (
            "a second file claiming an id already in use was NOT reported. This is the exact "
            "failure that cost four renumberings; the guard must see it.")
    finally:
        os.remove(planted)
    _, errors = ci.read_questions()
    assert not any("DUPLICATE ID" in e for e in errors), "the planted file was not cleaned up"


def test_an_unrecognised_status_word_fails_rather_than_counting_as_settled(ci):
    """Unjudged is not passed. The vocabulary is a NAMED LIST and an entry outside it stops
    the build -- a guard whose unknown case is "assume fine" is not a guard."""
    # normalise() cuts at the first separator and folds hyphens, then matching is by PREFIX --
    # that is the contract, and it is what lets a date ride along after the word.
    assert ci.normalise("HALF-CLOSED 26 Aug 2026").startswith("HALF CLOSED")
    assert ci.normalise("Half closed, 26 Aug") == "HALF CLOSED"
    assert ci.normalise("OPEN — the sill scope").startswith(ci.OPEN)
    assert ci.normalise("CLOSED 27 Aug 2026").startswith(ci.SETTLED)

    # The failure that matters: a word in NEITHER tuple must be classed unjudged and reported,
    # never quietly settled. Proved against a real file rather than against the helper.
    victim = sorted(f for f in os.listdir(QDIR)
                    if f.endswith(".md") and f != "README.md")[0]
    path = os.path.join(QDIR, victim)
    original = open(path, encoding="utf-8").read()
    try:
        open(path, "w", encoding="utf-8").write(
            re.sub(r"^\*Status: [^ ·]+", "*Status: RETICULATED", original, count=1, flags=re.M))
        qs, errors = ci.read_questions()
        assert any("unrecognised status" in e for e in errors), (
            "a status word outside the vocabulary was accepted. An unclassified entry must "
            "never silently count as settled.")
    finally:
        open(path, "w", encoding="utf-8").write(original)
    _, errors = ci.read_questions()
    assert not errors, "the mutated file was not restored"


def test_the_status_vocabulary_is_spelled_in_exactly_one_place(ci):
    """`check_inheritance.py`'s RATCHET comment claimed the test imported it, the test
    restated it as a literal, and the two drifted stale-high. The same duplication existed
    here: SETTLED_WORDS and OPEN_WORDS were spelled in `test_wp46_packs.py` AND in the
    register. This asserts the test no longer carries its own copy."""
    src = open(os.path.join(ROOT, "tests", "test_wp46_packs.py"), encoding="utf-8").read()
    fn = src[src.index("def test_claude_md_open_question_list_is_derived"):]
    fn = fn[:fn.index("\ndef ")]
    assert "SETTLED_WORDS = (" not in fn and "OPEN_WORDS = (" not in fn, (
        "the derivation test has re-grown its own copy of the status vocabulary. One list, "
        "one place -- check_ids.SETTLED / check_ids.OPEN.")
    assert "check_ids" in fn


def test_the_index_is_generated_and_current():
    """`docs/open-questions.md` is an artefact. Seventeen tests once read dist/taxonomy.json
    as though it were source and it went stale; this is the same guarantee, cheaper."""
    gen = _mod("gen_oq_t", "build/gen_open_questions.py")
    rendered = gen.render()
    have = open(os.path.join(ROOT, "docs", "open-questions.md"), encoding="utf-8").read()
    assert have == rendered, (
        "docs/open-questions.md has drifted from docs/open-questions/. Run "
        "`python3 build/gen_open_questions.py`. Never edit the index by hand.")


def test_no_two_work_package_reports_share_a_slug(ci):
    """OQ 90's own fallback was "cite the report, never the number" -- and
    `wp-5.8-the-four-rulings.md` and `wp-5.10-the-four-rulings.md` were different packages
    with identical slugs, so citing the report distinguished nothing."""
    _, errors = ci.check_reports()
    assert not [e for e in errors if "share the slug" in e], errors


def test_every_cited_report_path_resolves(ci):
    """A dangling citation is the same defect one layer out. Found `wp-2.3-real-solver.md`,
    cited in two files and never existing."""
    _, errors = ci.check_reports()
    assert not [e for e in errors if "does not exist" in e], errors


def test_the_two_wp_5_7s_are_settled_and_the_conversion_table_says_so():
    """OQ 90, executed: this branch's chain moved 5.7-5.10 -> 5.11-5.14 and main's atlas kept
    5.7. A commit subject cannot be changed, so the table is how history is read."""
    reports = sorted(os.listdir(os.path.join(ROOT, "docs", "reports")))
    for name in ("wp-5.11-real-2d-geometry.md",
                 "wp-5.12-the-four-rulings-from-the-geometry-layer.md",
                 "wp-5.13-the-roof-layer.md",
                 "wp-5.14-the-four-rulings-from-the-dormer-layer.md",
                 "wp-5.7-the-atlas-and-the-shell.md"):
        assert name in reports, f"{name} missing"
    for gone in ("wp-5.7-real-2d-geometry.md", "wp-5.8-the-four-rulings.md",
                 "wp-5.9-the-roof-layer.md", "wp-5.10-the-four-rulings.md"):
        assert gone not in reports, f"{gone} should have been renamed by OQ 90"
    readme = open(os.path.join(QDIR, "README.md"), encoding="utf-8").read()
    assert "| WP-5.7 | **WP-5.11** |" in readme, "the conversion table is missing its first row"


def test_section_one_names_open_questions_and_work_packages_as_ids():
    """The seam. §1's never-reuse rule enumerated seven id families and omitted these two,
    which is why four block renumbers felt permissible."""
    poa = open(os.path.join(ROOT, "PLAN-OF-ACTION.md"), encoding="utf-8").read()
    rule = poa[poa.index("**Ids are stable and never reused.**"):][:400]
    assert "open-question" in rule and "work-package" in rule, rule
    assert "never by reading the working tree" in poa


# ---------------------------------------------------------------- the CI gate
#
# THE CROSS-BRANCH GATE IS SHELL IN A YAML FILE AND NOTHING RAN IT. Its first version
# walked the ids this branch ADDED and then asked for the BASE branch's file for that
# id -- which is non-empty only when the id is already in base, i.e. never for a member
# of `added`. The condition was unsatisfiable on every iteration, so the step printed
# "No open-question id on this branch collides" for the one case it exists to catch, and
# `grep -rn ci.yml tests/` returned nothing. A guard nobody runs is a comment.
#
# These two tests extract the step's own shell out of `.github/workflows/ci.yml` and run
# it against stub registers, stubbing ONLY the two git reads. The pair is the point: one
# proves it fires on a collision, the other that it stays quiet without one, and neither
# passes alone -- `exit 1` unconditionally satisfies the first, `exit 0` the second.

def _gate_script():
    """The gate step's shell, with `files()` restubbed to read two fixture files."""
    ci_yml = os.path.join(ROOT, ".github", "workflows", "ci.yml")
    with open(ci_yml, encoding="utf-8") as fh:
        text = fh.read()
    start = text.index("      - name: open-question ids do not collide with the base branch")
    body = text[start:text.index("      - name: ", start + 10)]
    run = body[body.index("run: |") + len("run: |"):]
    lines = [ln[10:] if ln.startswith(" " * 10) else ln for ln in run.splitlines()]
    out = []
    for ln in lines:
        if ln.strip().startswith("git fetch"):
            continue                                   # no network in a test
        if ln.strip().startswith("files ()"):          # the one stubbed read
            out.append('files () { if [ "$1" = "$BASE" ]; then cat "$FIX/base.txt"; '
                       'else cat "$FIX/head.txt"; fi | sort; }')
            continue
        out.append(ln)
    script = "\n".join(out).replace("${{ github.base_ref }}", "main")
    assert "comm -12" in script, "the gate must walk the INTERSECTION, not the difference"
    return script


def _run_gate(tmp_path, base, head):
    import subprocess
    (tmp_path / "base.txt").write_text("\n".join(base) + "\n", encoding="utf-8")
    (tmp_path / "head.txt").write_text("\n".join(head) + "\n", encoding="utf-8")
    env = dict(os.environ, FIX=str(tmp_path))
    return subprocess.run(["bash", "-c", _gate_script()], capture_output=True,
                          text=True, env=env, cwd=str(tmp_path))


CLEAN = ["docs/open-questions/001-a.md", "docs/open-questions/099-atlas.md"]


@pytest.mark.parametrize("head,label", [
    (["docs/open-questions/001-a.md", "docs/open-questions/099-mine.md"], "head-only checkout"),
    (["docs/open-questions/001-a.md", "docs/open-questions/099-atlas.md",
      "docs/open-questions/099-mine.md"], "merge-commit checkout"),
])
def test_the_ci_gate_fires_when_both_branches_carry_one_id_under_different_names(
        tmp_path, head, label):
    # Both shapes matter: `actions/checkout` gives a PR the MERGE commit, so HEAD carries
    # both files and the id is in neither branch's difference. The first version of the
    # gate passed both of these.
    r = _run_gate(tmp_path, CLEAN, head)
    assert r.returncode == 1, f"the gate did not fire on a real collision ({label}): {r.stdout}"
    assert "099" in r.stdout


def test_the_ci_gate_is_quiet_when_nothing_collides(tmp_path):
    # A NAMED id added by this branch is not a collision: the filename IS the id, so two
    # sessions deriving the same slug have raised the same question, and git refuses the
    # add/add rather than merging it by juxtaposition.
    r = _run_gate(tmp_path, CLEAN, CLEAN + ["docs/open-questions/oq-new-thing.md"])
    assert r.returncode == 0, f"the gate fired with nothing to find: {r.stdout}{r.stderr}"
    assert "collide" not in r.stdout.lower() or "No open-question id" in r.stdout
