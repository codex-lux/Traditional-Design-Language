"""WP-13.5 — a duplicate key in a JSON record is invisible to every reader in this tree.

THE DEFECT THIS EXISTS FOR, and it was shipped. `plans/tidewater-georgian-careful.json` stated
`"stacks_over"` TWICE on `landing` and twice on `upperpassage`, and had since WP-11.2 authored
those two claims. `json.load` keeps the LAST occurrence and says nothing. `jsonschema` validates
the PARSED object, so the first copy is gone before any schema sees it. Both engines, both
renderers, `check_plans.py`, `check_stacking.py` and `plan_check` therefore agreed with one
another about a record that says one thing twice — and they agreed CORRECTLY, because on this
instance the two copies carried the same value. Nothing in this corpus has ever behaved
differently, which is precisely why it survived: the failure needs the two copies to DISAGREE,
and the first reader to notice would then have been a person reading a sheet.

It was found by round-tripping the file — parse, edit, dump — and reading the diff, which
collapsed the pair and showed as the deletion of a line nobody had deleted.

WHAT IS DRIVEN HERE AND WHAT IS READ, because the two are not the same evidence:

  * the DETECTION is driven, on temp files outside the repository, against the real function
    lifted out of `build/validate.py` by AST so it cannot drift from the shipped one;
  * the WIRING — that a duplicate reddens the build rather than printing a line — is read from
    the source, and mutation-checked in the package's own harness rather than by a test;
  * the PREMISE — that the sweep really opened the corpus and found none — is asserted against
    a real run, because a sweep that reads nothing reports zero exactly as a clean tree does.

**NOTHING HERE WRITES INSIDE THE REPOSITORY.** The obvious end-to-end drive is to put a
duplicate into a tracked record and restore it in a `finally`, and `tests/test_ontology.py` has
two tests that do exactly that. CLAUDE.md's WP-11.10 entry forbids it and gives the measured
reason: a `finally` does not run when the process is killed, and that session alone had two
container restarts mid-run, which would leave a corrupted record in the corpus looking exactly
like an authored change.
"""
import ast
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATE = os.path.join(ROOT, "build", "validate.py")


def _lifted(name, also=()):
    """The real function out of `build/validate.py`, compiled from its own source.

    `validate.py` is a script: importing it runs the whole taxonomy check and the scene
    selftest. Lifting the one definition by AST exercises the SHIPPED text — rename it, change
    its body, or delete it and this file goes red — without a second copy to keep in step.

    `also` lifts the helpers the named function calls into the SAME namespace, so a lifted
    caller runs the shipped callee rather than a stub (WP-13.7, for `duplicate_keys_over`).
    """
    tree = ast.parse(open(VALIDATE, encoding="utf-8").read())
    ns = {"json": json, "os": os, "ROOT": ROOT}
    for want in (*also, name):
        fn = next((n for n in tree.body
                   if isinstance(n, ast.FunctionDef) and n.name == want), None)
        assert fn is not None, f"build/validate.py no longer defines {want}"
        exec(compile(ast.Module(body=[fn], type_ignores=[]), VALIDATE, "exec"), ns)
    return ns[name]


def _tmp(text):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    fh.write(text); fh.close()
    return fh.name


class TestTheDetection:
    def test_a_key_stated_twice_is_found_and_the_object_is_named(self):
        """The shipped defect, reproduced verbatim: the second `stacks_over` is what every
        reader in this tree got, and the first was invisible to all of them."""
        dup = _lifted("_duplicate_keys")
        p = _tmp('{"id": "landing", "stacks_over": "stair", "width_ft": 9, '
                 '"stacks_over": "stair"}')
        try:
            assert dup(p) == [("landing", "stacks_over")]
        finally:
            os.unlink(p)

    def test_the_two_copies_DISAGREEING_is_found_too(self):
        """The case that would have been a real defect, and the reason equal copies are still
        refused: nothing downstream can tell this file from the one above, because `json.load`
        has discarded the evidence by the time anybody looks."""
        dup = _lifted("_duplicate_keys")
        p = _tmp('{"id": "landing", "stacks_over": "stair", "stacks_over": "library"}')
        try:
            assert dup(p) == [("landing", "stacks_over")]
            assert json.load(open(p))["stacks_over"] == "library", \
                "the LAST wins, which is what makes the first invisible"
        finally:
            os.unlink(p)

    def test_a_clean_record_reports_nothing(self):
        """The other direction, and it is not a formality: a detector that fires on everything
        would have been green on the corpus for the wrong reason."""
        dup = _lifted("_duplicate_keys")
        p = _tmp('{"id": "landing", "stacks_over": "stair", "width_ft": 9}')
        try:
            assert dup(p) == []
        finally:
            os.unlink(p)

    def test_a_nested_object_is_reached_and_named_by_its_own_id(self):
        """The defect was two levels down, inside `levels[].rooms[]`. A sweep that read only
        the top-level object would have found nothing and reported a clean corpus."""
        dup = _lifted("_duplicate_keys")
        p = _tmp('{"id": "plan", "levels": [{"rooms": [{"id": "kitchen", '
                 '"block": "service", "block": "service"}]}]}')
        try:
            assert dup(p) == [("kitchen", "block")]
        finally:
            os.unlink(p)


class TestTheWiringAndThePremise:
    def test_the_sweep_enumerates_with_git_and_never_by_walking(self):
        """WP-13.2 met the other way round: a checker that walked the directory found the first
        agent worktree under `.claude/worktrees/` — a git-ignored copy of the whole repository
        inside itself — and went red on 2,031 files it was never written to open. Read as a
        property of the source rather than of today's tree, because today's tree may have no
        worktree in it and the defect would still be waiting."""
        src = open(VALIDATE, encoding="utf-8").read()
        i = src.index("def _duplicate_keys")
        tail = src[i:]
        assert "ls-files" in tail, "the duplicate-key sweep must enumerate with git ls-files"
        assert "os.walk" not in tail, "a checker that walks the tree reads its own worktrees"

    def test_a_duplicate_fails_the_build_rather_than_printing_a_line(self):
        """The whole value is in the exit code: this corpus's standing complaint is a check
        whose greenness reads as a verdict. Source-read and mutation-checked, because driving
        it end to end means writing a bad record into the repository."""
        src = open(VALIDATE, encoding="utf-8").read()
        assert "_dup_bad = 1 if _dups else 0" in src
        assert "if _scene_bad or _dup_bad:" in src, \
            "the duplicate sweep's verdict must reach sys.exit"

    def test_the_sweep_really_opened_the_corpus_and_found_none(self):
        """UNJUDGED IS NOT PASSED, applied to the instrument. A sweep that enumerated nothing
        prints `duplicates: 0` exactly as a clean corpus does, so the count of files READ is
        asserted first. The floor is deliberately far below the 1,439 measured at WP-13.5 — it
        is here to catch an enumerator that broke, not to pin a corpus size no checker derives.
        """
        proc = subprocess.run([sys.executable, VALIDATE], cwd=ROOT,
                              capture_output=True, text=True)
        line = next((l for l in proc.stdout.splitlines()
                     if l.startswith("json records read for duplicate keys:")), None)
        assert line, f"the sweep printed no census line: {proc.stdout[-400:]}"
        read = int(line.split(":")[1].split()[0])
        dups = int(line.rsplit(":", 1)[1])
        assert read > 1000, f"the sweep opened only {read} records — the enumerator is broken"
        assert dups == 0, f"{dups} duplicate key(s) in the corpus: {proc.stdout[-600:]}"

    def test_the_record_this_was_found_in_states_each_claim_once(self):
        """The instance, pinned where a reader will look for it. Both copies said `stair` and
        `passage`, so the values below are what the corpus always delivered; what changed is
        that the record now says each of them once."""
        raw = open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"),
                   encoding="utf-8").read()
        dup = _lifted("_duplicate_keys")
        p = _tmp(raw)
        try:
            assert dup(p) == []
        finally:
            os.unlink(p)
        rooms = {r["id"]: r for lv in json.loads(raw)["levels"] for r in lv["rooms"]}
        assert rooms["landing"]["stacks_over"] == "stair"
        assert rooms["upperpassage"]["stacks_over"] == "passage"


class TestTheWiringIsDrivenWithAKnownBadInput:
    """WP-13.7. The detection was driven and the WIRING was not, and the gap was measurable:
    replacing `_found = _duplicate_keys(_abs)` with `_found = []` in `build/validate.py` left
    every test in this file GREEN. `test_the_sweep_really_opened_the_corpus_and_found_none`
    asserts `read > 1000` and `dups == 0`, and a DETECTOR that returns nothing satisfies both
    exactly as a clean corpus does -- which is that test's own docstring ("a sweep that
    enumerated nothing prints `duplicates: 0` exactly as a clean corpus does") arriving one
    level down, about the judge instead of the enumerator.

    The loop is `validate.duplicate_keys_over(rels, root=)` now, so it can be handed a list
    containing a file that really does state a key twice. NOTHING HERE WRITES INSIDE THE
    REPOSITORY -- the files are temporary and the root is the temp directory."""

    def _sweep(self):
        return _lifted("duplicate_keys_over", also=("_duplicate_keys",))

    def test_the_loop_reports_a_duplicate_the_detector_finds(self):
        import shutil
        d = tempfile.mkdtemp()
        try:
            open(os.path.join(d, "clean.json"), "w", encoding="utf-8").write(
                '{"id": "a", "rooms": [{"id": "kitchen", "block": "service"}]}')
            open(os.path.join(d, "bad.json"), "w", encoding="utf-8").write(
                '{"id": "b", "rooms": [{"id": "kitchen", "block": "service",'
                ' "block": "main"}]}')
            sweep = self._sweep()
            # THE CONTROL FIRST: a sound file is read and convicts nothing, so a sweep that
            # convicted everything would not pass this either.
            assert sweep(["clean.json"], root=d) == (1, []), "the control file is not clean"
            read, dups = sweep(["clean.json", "bad.json"], root=d)
            assert read == 2, f"the loop parsed {read} of 2 files"
            assert dups == ["bad.json: object 'kitchen' states 'block' twice"], dups
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_a_path_that_is_not_a_file_is_skipped_and_never_counted_as_read(self):
        """The census is the premise assertion the corpus run rests on, so a path the sweep
        did not open must not inflate it."""
        import shutil
        d = tempfile.mkdtemp()
        try:
            open(os.path.join(d, "clean.json"), "w", encoding="utf-8").write('{"id": "a"}')
            sweep = self._sweep()
            assert sweep(["clean.json", "gone.json"], root=d) == (1, [])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_a_file_the_detector_cannot_parse_is_not_counted_as_read_either(self):
        """A malformed record is the schema's finding and not this sweep's, and it may not be
        counted as a record this sweep read."""
        import shutil
        d = tempfile.mkdtemp()
        try:
            open(os.path.join(d, "broken.json"), "w", encoding="utf-8").write("{not json")
            sweep = self._sweep()
            assert sweep(["broken.json"], root=d) == (0, [])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_the_corpus_run_goes_through_this_very_function(self):
        """Otherwise the three drives above are about a function nothing calls. Read from the
        source, because the module-level block cannot be imported without running the whole
        script."""
        src = open(VALIDATE, encoding="utf-8").read()
        assert "_read, _dups = duplicate_keys_over(_tracked)" in src, (
            "the corpus sweep no longer runs through `duplicate_keys_over`, so the drives in "
            "this class are about a function nothing calls")
