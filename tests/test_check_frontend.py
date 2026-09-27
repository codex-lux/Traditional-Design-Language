"""The frontend checker, which had nine behaviours and no test file at all (WP-13.2).

Two defects are pinned here. Both were found by reading the checker's own build output
against the thing it was looking at, not by reading its source:

  1. IT ASSERTED A FALSE CAUSE. A `dist/` built before the code it judges printed
     `FAIL: three.js is not a separate chunk -- round/three-scene.js has been imported
     statically somewhere` about a bundle in which that chunk could not possibly appear.
     Measured on this tree 15 Sep 2026: dist built 7 Sep 17:11, `round/three-scene.js`
     committed 9 Sep by WP-12.4, 22 sources newer than the bundle. No file in the tree
     statically imports it, so a reader acting on the message hunts for a line that does
     not exist. Two states where three are needed.
  2. IT NAMED THE WRONG POPULATION. `bad` counted the lazy-tier check and the node suites
     in one variable, so the run printed `FAIL: 1 of 2 frontend suite(s) failed` two lines
     under `router-unit: 63 checks passed` and `search-unit: 13 checks passed`.

Neither state is reachable from a correct checkout, so BOTH are DRIVEN -- `verdict()` is a
pure function and every state is called directly, and each staleness fixture builds its own
tree in a tmpdir and passes it as `root=`. Nothing here reads the repository's own `dist/`,
which is gitignored and therefore a property of whoever last ran `npm run build` rather than
of the corpus.
"""
import os
import sys
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache  # noqa: E402

CF = modcache.load("check_frontend", os.path.join(ROOT, "build", "check_frontend.py"))


def _tree(src_mtime, dist_mtime, index=True):
    """A minimal workbench tree with the two mtimes the reader compares."""
    d = tempfile.mkdtemp()
    src = os.path.join(d, "workbench", "app", "src", "round")
    dist = os.path.join(d, "workbench", "app", "dist")
    os.makedirs(src)
    os.makedirs(os.path.join(dist, "assets"))
    f = os.path.join(src, "three-scene.js")
    open(f, "w").write("import * as THREE from 'three';\n")
    os.utime(f, (src_mtime, src_mtime))
    idx = os.path.join(dist, "index.html")
    if index:
        open(idx, "w").write("<html></html>")
        os.utime(idx, (dist_mtime, dist_mtime))
    return d, idx


class TestTheStaleBundleIsAThirdState(unittest.TestCase):
    def test_a_source_newer_than_the_bundle_is_named(self):
        now = time.time()
        d, idx = _tree(src_mtime=now, dist_mtime=now - 3600)
        self.assertEqual(
            CF.sources_newer_than(os.path.getmtime(idx), root=d),
            ["workbench/app/src/round/three-scene.js"],
            "the stale source must be NAMED -- a bare count sends a reader nowhere")

    def test_a_bundle_newer_than_every_source_is_current(self):
        """The discriminator. Without it the branch above separates nothing, and the check
        would be unjudged on every run -- which is the fake-unjudged direction and exactly
        as dishonest as the false FAIL it replaces."""
        now = time.time()
        d, idx = _tree(src_mtime=now - 3600, dist_mtime=now)
        self.assertEqual(CF.sources_newer_than(os.path.getmtime(idx), root=d), [],
                         "a freshly built bundle is not stale, or every run goes unjudged")

    def test_the_heuristic_never_errs_toward_a_pass(self):
        """The property that makes an mtime comparison admissible at all.

        It may call a current bundle stale -- unjudged, and safe. It may never call a stale
        bundle current, because that would let a real regression read as a pass. A freshly
        built dist is newer than every source by construction, so a genuine static import
        still reaches the FAIL branch.
        """
        now = time.time()
        d, idx = _tree(src_mtime=now - 1, dist_mtime=now)
        self.assertEqual(CF.sources_newer_than(os.path.getmtime(idx), root=d), [])


class TestTheWiringBetweenTheReaderAndTheVerdict(unittest.TestCase):
    """`bundle_unjudged_reason` exists because a mutation sweep found the inline version of
    this logic BLIND three ways -- deleting the staleness test, inverting it, and loosening
    `>` to `>=` all left the suite green, because nothing drove the wiring. Every branch is
    called directly here."""

    def test_a_current_bundle_is_judgeable(self):
        now = time.time()
        d, _ = _tree(src_mtime=now - 3600, dist_mtime=now)
        self.assertEqual(CF.bundle_unjudged_reason(root=d), "",
                         "a current bundle must be JUDGED, or the check is permanently unjudged")

    def test_a_stale_bundle_is_refused_with_its_reason(self):
        now = time.time()
        d, _ = _tree(src_mtime=now, dist_mtime=now - 3600)
        why = CF.bundle_unjudged_reason(root=d)
        self.assertIn("built before", why)
        self.assertIn("three-scene.js", why, "the reason must NAME a file")

    def test_a_bundle_built_at_the_same_instant_is_current(self):
        """THE `>` / `>=` DISCRIMINATOR, and it needs an EQUALITY fixture.

        Every other fixture here leaves a whole second between the two mtimes, and at a
        gap of one second `>` and `>=` return the same answer -- so a mutation loosening the
        comparison was green. Under `>=`, a source written in the same instant as the bundle
        reads stale, and on a fast machine that is EVERY build: the check would go
        permanently unjudged, which is the fake-unjudged direction and exactly as dishonest
        as the false FAIL this package removed.
        """
        now = time.time()
        d, _ = _tree(src_mtime=now, dist_mtime=now)
        self.assertEqual(CF.bundle_unjudged_reason(root=d), "")

    def test_an_absent_dist_is_refused_and_not_failed(self):
        import tempfile
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "workbench", "app", "src"))
        self.assertIn("no dist/", CF.bundle_unjudged_reason(root=d))

    def test_a_bundle_that_cannot_be_dated_is_refused(self):
        now = time.time()
        d, _ = _tree(src_mtime=now, dist_mtime=now, index=False)
        self.assertIn("cannot be dated", CF.bundle_unjudged_reason(root=d))


class TestTheVerdictNamesTheRightPopulation(unittest.TestCase):
    """Driven against `verdict()`, the pure function, so each state is a real call."""

    def test_a_tier_failure_does_not_report_a_suite_failure(self):
        """THE DEFECT, driven. This is the exact state the build was in."""
        code, msg = CF.verdict(tier_bad=1, suite_bad=[], tier_unjudged="")
        self.assertEqual(code, 1)
        self.assertIn("lazy-tier", msg)
        self.assertNotIn("frontend suite(s)", msg,
                         "a lazy-tier failure may not be reported as a suite failure")

    def test_a_suite_failure_names_the_suite(self):
        code, msg = CF.verdict(tier_bad=0, suite_bad=["router-unit.mjs"], tier_unjudged="")
        self.assertEqual(code, 1)
        self.assertIn("router-unit.mjs", msg)
        self.assertNotIn("lazy-tier", msg)

    def test_both_populations_are_reported_when_both_fail(self):
        code, msg = CF.verdict(tier_bad=1, suite_bad=["search-unit.mjs"], tier_unjudged="")
        self.assertEqual(code, 1)
        self.assertIn("lazy-tier", msg)
        self.assertIn("search-unit.mjs", msg)

    def test_an_unjudged_tier_check_is_not_a_pass(self):
        """One check, one verdict. Returning 0 here collapses unjudged into passed."""
        code, msg = CF.verdict(tier_bad=0, suite_bad=[], tier_unjudged="dist/ is stale")
        self.assertEqual(code, CF.COULD_NOT_EVALUATE)
        self.assertIn("COULD NOT EVALUATE", msg)
        self.assertIn("dist/ is stale", msg, "the verdict must carry the reason, not just the state")

    def test_a_real_failure_outranks_an_unjudged_half(self):
        """A stale bundle does not excuse a broken suite."""
        code, _ = CF.verdict(tier_bad=0, suite_bad=["router-unit.mjs"], tier_unjudged="stale")
        self.assertEqual(code, 1)

    def test_everything_green_is_a_pass(self):
        code, msg = CF.verdict(tier_bad=0, suite_bad=[], tier_unjudged="")
        self.assertEqual(code, 0)
        self.assertTrue(msg.startswith("OK"))


class TestMainReportsTheStateItReads(unittest.TestCase):
    """THE JOIN, and it was the one thing eleven mutations could not see.

    Every part above is driven and every part went red -- and a mutation that made `main()`
    stop calling `bundle_unjudged_reason()` at all left the whole suite green, because each
    half was tested and the wiring between them was not. These drive `main()` itself through
    the `root=` seam, so both states are reached on any machine rather than whichever one
    this checkout's gitignored `dist/` happens to be in.

    `main()` runs the two node suites for real, so these are the slowest tests in the file
    (about a second each). That is the price of testing the join rather than asserting it.
    """

    def test_an_unjudged_bundle_can_never_produce_a_pass(self):
        now = time.time()
        d, _ = _tree(src_mtime=now, dist_mtime=now - 3600)   # stale
        self.assertTrue(CF.bundle_unjudged_reason(root=d), "premise: this tree must be stale")
        self.assertNotEqual(CF.main(root=d), 0,
                            "main() ignored the bundle state and called a stale build a pass")

    def test_an_absent_bundle_can_never_produce_a_pass(self):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "workbench", "app", "src"))
        self.assertNotEqual(CF.main(root=d), 0)

    def test_a_current_but_empty_bundle_is_failed_and_not_refused(self):
        """The discriminator for the two above: a bundle that CAN be judged and fails must
        FAIL, not go unjudged. Without this, returning COULD NOT EVALUATE unconditionally
        would satisfy both tests above -- a fake unjudged, which this corpus treats as
        exactly as dishonest as a fake pass."""
        now = time.time()
        d, _ = _tree(src_mtime=now - 3600, dist_mtime=now)   # current, but assets/ is empty
        self.assertEqual(CF.bundle_unjudged_reason(root=d), "", "premise: this tree is judgeable")
        self.assertEqual(CF.main(root=d), 1,
                         "a judgeable bundle with no entry chunk is a FAILURE, not an unjudged state")


DEFINITION = ("The style refuses this slot outright, and a kit that binds it anyway is "
              "convicted by the checker rather than quietly allowed.")


def _full_tree(entry_text, glossary=True):
    """A CURRENT, judgeable tree whose bundle passes every lazy-tier check, so the only thing
    left to decide is the glossary probe (WP-14.8)."""
    import json
    now = time.time()
    d, _ = _tree(src_mtime=now - 3600, dist_mtime=now)
    assets = os.path.join(d, "workbench", "app", "dist", "assets")
    for name, text in (("index-abc.js", entry_text), ("coastlines-medium-1.js", "x"),
                       ("coastlines-fine-2.js", "x"), ("three-scene-3.js", "x")):
        with open(os.path.join(assets, name), "w") as f:
            f.write(text)
    if glossary:
        g = os.path.join(d, "glossary")
        os.makedirs(g)
        with open(os.path.join(g, "binding-forbidden.json"), "w") as f:
            json.dump({"id": "binding-forbidden", "term": "forbidden", "definition": DEFINITION}, f)
    return d


class TestTheGlossaryIsFetchedNotBundled(unittest.TestCase):
    """WP-14.8: a glossary record imported into the bundle is a second copy of the corpus frozen
    at build time, and Vite would fold it in without a warning. The probe is driven on built
    trees here, in both directions, and through `main()` so the WIRING is under test too -- the
    join this file's own history says goes blind first."""

    def test_a_probe_is_a_long_plain_run_of_the_definition(self):
        import json
        d = tempfile.mkdtemp()
        for name, rec in (("a.json", {"id": "a", "definition": DEFINITION}),
                          ("short.json", {"id": "short", "definition": "A slot."}),
                          ("README.md", None)):
            with open(os.path.join(d, name), "w") as f:
                f.write("# not a record" if rec is None else json.dumps(rec))
        with open(os.path.join(d, "broken.json"), "w") as f:
            f.write("{not json")
        probes = CF.glossary_probes(d)
        self.assertEqual(sorted(probes), ["a"], "short, broken and non-JSON records give no probe")
        self.assertGreaterEqual(len(probes["a"]), CF.PROBE_MIN)
        self.assertIn(probes["a"], DEFINITION)

    def test_a_bundled_definition_is_found_in_the_chunk_that_carries_it(self):
        d = _full_tree("const g = JSON.parse('{\"definition\":\"" + DEFINITION + "\"}');")
        assets = os.path.join(d, "workbench", "app", "dist", "assets")
        hits, probed = CF.bundled_glossary_text(assets, os.path.join(d, "glossary"))
        self.assertEqual(probed, 1)
        self.assertEqual(hits, [("binding-forbidden", "index-abc.js")])

    def test_a_clean_bundle_is_not_convicted(self):
        """The discriminator: a probe that fired on every chunk would convict an honest build."""
        d = _full_tree("fetch('/api/glossary').then((r) => r.json());")
        assets = os.path.join(d, "workbench", "app", "dist", "assets")
        self.assertEqual(CF.bundled_glossary_text(assets, os.path.join(d, "glossary")), ([], 1))

    def _run(self, root):
        import contextlib
        import io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = CF.main(root=root)
        return code, out.getvalue(), err.getvalue()

    def test_main_fails_a_bundled_glossary_and_clears_a_fetched_one(self):
        code, _out, err = self._run(_full_tree("var x = '" + DEFINITION + "';"))
        self.assertEqual(code, 1, "main() did not fail a bundle carrying a record")
        self.assertIn("FAIL: 1 glossary definition(s) are in the bundle", err)
        self.assertIn("binding-forbidden", err, "the failure must NAME the record")
        # The discriminator, read off what main() printed rather than its exit code, so the
        # node suites it also runs cannot decide this half.
        _code, out, err = self._run(_full_tree("fetch('/api/glossary');"))
        self.assertIn("glossary fetched, not bundled: 1 definitions probed", out)
        self.assertNotIn("glossary definition(s) are in the bundle", err)

    def test_a_glossary_with_nothing_to_probe_is_unjudged_and_never_a_pass(self):
        d = _full_tree("fetch('/api/glossary');", glossary=False)
        self.assertEqual(CF.main(root=d), CF.COULD_NOT_EVALUATE)

    def test_the_corpus_gives_the_probe_something_to_look_for(self):
        """The premise on the real records: most definitions carry a plain run long enough to
        probe for, so the check is judging the glossary rather than a handful of it."""
        g = os.path.join(ROOT, "glossary")
        n = len([f for f in sorted(os.listdir(g)) if f.endswith(".json")])
        probes = CF.glossary_probes(g)
        self.assertGreater(n, 0)
        self.assertGreaterEqual(len(probes), n * 0.9, f"{len(probes)} of {n} records probed")


class TestTheSourceGuaranteeThisCheckerCannotSee(unittest.TestCase):
    """The bundle half is unjudged without a build; the SOURCE half never is.

    `three` reaches the app through exactly one module, and that module is reached through
    exactly one dynamic import. `workbench/app/src/round.test.mjs` pins both directions in
    JavaScript; these assert the same two facts in Python, so a machine with no node -- and
    a checkout with no dist -- still learns whether the invariant the lazy-tier check exists
    to protect is held by the code that would be bundled. That is what makes the FAIL this
    package removed a FALSE accusation rather than an unverifiable one.
    """

    def _walk(self, pattern):
        import re
        rx = re.compile(pattern, re.M)
        hits = []
        src_dir = os.path.join(ROOT, "workbench", "app", "src")
        # sorted(os.walk(...)) -- tests/test_determinism.py forbids an unsorted directory
        # read anywhere in the toolchain, this file included, and it caught both of these.
        for dirpath, _dirs, files in sorted(os.walk(src_dir)):
            for name in sorted(files):
                if not name.endswith((".js", ".jsx", ".mjs")):
                    continue
                path = os.path.join(dirpath, name)
                if rx.search(open(path, encoding="utf-8").read()):
                    hits.append(os.path.relpath(path, ROOT))
        return sorted(hits)

    def test_three_is_imported_by_exactly_one_module(self):
        importers = [p for p in self._walk(r"""^\s*import[^\n]*from\s+['"]three(/[^'"]*)?['"]""")
                     if not p.endswith("round/three-scene.js")]
        self.assertEqual(importers, [],
                         f"three must reach the bundle only through round/three-scene.js: {importers}")

    def test_three_scene_is_reached_only_by_a_dynamic_import(self):
        statics = [p for p in self._walk(r"""^\s*import[^\n]*from\s+['"][^'"]*three-scene\.js['"]""")
                   if not p.endswith("round.test.mjs")]
        self.assertEqual(statics, [],
                         f"a static import of three-scene.js folds three into the entry chunk: {statics}")

    def test_the_dynamic_import_really_exists(self):
        """The premise. Without it the two guards above pass on an app that never loads the
        Round at all, which is this repository's own 'a guard reading air'."""
        p = os.path.join(ROOT, "workbench", "app", "src", "round", "Round.jsx")
        self.assertIn("import('./three-scene.js')", open(p, encoding="utf-8").read())

    def test_three_is_really_a_dependency(self):
        """And the premise under that one: if `three` left package.json, all three guards
        above would pass on an app that cannot draw the Round."""
        import json
        pkg = json.load(open(os.path.join(ROOT, "workbench", "app", "package.json")))
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        self.assertIn("three", deps)


if __name__ == "__main__":
    unittest.main()
