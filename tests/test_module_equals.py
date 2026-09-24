"""WP-14.4: `module.equals` -- a pack's statement that its module IS a building input -- is
lie-checked, and the check is proved able to fail.

The workbench dimensions a pack declaring `module.equals: ceiling_height` AT the reader's
ceiling, and draws its assemblies and prints its rules as one wall on the strength of it
(workbench/server/corpus.py::proportions_with_members, PRD §H.1). So the declaration is a
claim a surface acts on, and `build/check_systems.py` check 19 holds it to the pack's own
rules through ONE function, `module_equals_errors`. Two things are tested here:

  1. every pack in proportions/ -- not only systems/, which is all check_systems opens, so a
     declaration written into modules/ or orders/ cannot escape the check -- passes it;
  2. the check can FAIL: a declaration on a pack whose rules never read the ceiling is refused
     by the checker's own CLI. The copy is written to a temporary directory; nothing here
     writes inside the repository.

Every expectation is computed from the corpus; nothing names a count.
"""
import copy
import glob
import json
import os
import subprocess
import sys

import pytest

from conftest import ROOT

pytest.importorskip("jsonschema")
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CS = modcache.load("check_systems", os.path.join(ROOT, "build", "check_systems.py"))
CHECKER = os.path.join(ROOT, "build", "check_systems.py")
SYSTEMS = os.path.join(ROOT, "proportions", "systems")


def _packs():
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "**", "*.json"), recursive=True)):
        p = json.load(open(f, encoding="utf-8"))
        out[p["id"]] = (os.path.relpath(f, ROOT), p)
    return out


def _run(directory):
    r = subprocess.run([sys.executable, CHECKER, "--dir", str(directory)],
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def _a_pack_whose_rules_never_read(var):
    """A system pack whose derived rules never mention `var`, with the premise CHECKED rather
    than assumed. `trim-prairie` is the one the PRD names and is tried first; if its rules ever
    come to read the ceiling, the next pack of that shape takes its place rather than the
    mutation silently becoming a declaration the rules DO bear out."""
    packs = _packs()
    order = sorted(packs, key=lambda k: (k != "trim-prairie", k))
    for pid in order:
        rel, p = packs[pid]
        if not rel.startswith(os.path.join("proportions", "systems")):
            continue
        rules = p.get("derived_rules") or []
        if rules and "equals" not in p["module"] and not any(
                var in CS.rule_expr_vars(r["expression"]) for r in rules):
            return pid, rel, p
    pytest.fail(f"no system pack's rules avoid '{var}'; the mutation needs another subject")


class TestEveryDeclarationIsBorneOutByItsOwnRules:
    def test_every_pack_in_the_corpus_passes_check_19(self):
        bad = {pid: CS.module_equals_errors(p) for pid, (_, p) in _packs().items()}
        bad = {k: v for k, v in bad.items() if v}
        assert not bad, f"a module.equals declaration its own rules do not bear out: {bad}"

    def test_the_check_has_something_to_check(self):
        declaring = [pid for pid, (_, p) in _packs().items() if "equals" in p["module"]]
        assert declaring, "no pack declares module.equals, so the test above is vacuous"
        for pid in declaring:
            _, p = _packs()[pid]
            v = p["module"]["equals"]
            readers = [r for r in p["derived_rules"]
                       if v in CS.rule_expr_vars(r["expression"])]
            assert readers, pid
            assert not any({"module", "part"} & CS.rule_expr_vars(r["expression"])
                           for r in readers), pid

    def test_the_declaration_restates_what_the_module_name_already_says(self):
        """`trim-classical` declares its module is the ceiling because its own `module.name`
        says so in prose -- the field makes an authored sentence machine-readable, it does
        not add a fact. Held for every declarer: the name must speak of a ceiling."""
        for pid, (_, p) in _packs().items():
            if p["module"].get("equals") == "ceiling_height":
                assert "ceiling" in p["module"]["name"].lower(), \
                    f"{pid} declares its module is the ceiling and its own name does not say so"


class TestEachConditionCanFail:
    """Each of the four conditions, driven on an in-memory copy of a real declarer."""

    def _declarer(self):
        for pid, (_, p) in sorted(_packs().items()):
            if p["module"].get("equals"):
                return pid, copy.deepcopy(p)
        pytest.fail("no declarer to mutate")

    def test_a_clean_declarer_returns_no_error(self):
        _, p = self._declarer()
        assert CS.module_equals_errors(p) == []

    def test_a_value_the_engine_does_not_bind(self):
        _, p = self._declarer()
        p["module"]["equals"] = "chimney_height"
        errs = CS.module_equals_errors(p)
        assert any("not a variable the engine binds" in e for e in errs), errs

    def test_no_rule_reads_it(self):
        _, p = self._declarer()
        v = p["module"]["equals"]
        p["derived_rules"] = [r for r in p["derived_rules"]
                              if v not in CS.rule_expr_vars(r["expression"])]
        errs = CS.module_equals_errors(p)
        assert any("no derived rule reads" in e for e in errs), errs

    def test_a_rule_reads_it_together_with_the_module(self):
        _, p = self._declarer()
        v = p["module"]["equals"]
        i = next(i for i, r in enumerate(p["derived_rules"])
                 if v in CS.rule_expr_vars(r["expression"]))
        p["derived_rules"][i]["expression"] = f"{v} / module * part"
        errs = CS.module_equals_errors(p)
        assert any(f"derived_rules[{i}]" in e and "counted twice" in e for e in errs), errs

    def test_no_default_size(self):
        _, p = self._declarer()
        p["module"]["default_size_in"] = None
        errs = CS.module_equals_errors(p)
        assert any("default_size_in" in e for e in errs), errs


class TestTheCheckerRefusesALieThroughItsOwnCLI:
    """The mutation the PRD names, on a COPY in a temporary directory: the lone unmutated copy
    checks clean FIRST, so the red that follows is the declaration's and not the lone pack's."""

    def test_the_declaration_on_a_pack_that_never_reads_the_ceiling_fails_check_systems(
            self, tmp_path):
        pid, rel, p = _a_pack_whose_rules_never_read("ceiling_height")
        target = tmp_path / f"{pid}.json"
        target.write_text(json.dumps(p, indent=2), encoding="utf-8")
        code, out = _run(tmp_path)
        assert code == 0, f"the unmutated copy of {pid} does not check clean alone:\n{out}"
        mutated = copy.deepcopy(p)
        mutated["module"]["equals"] = "ceiling_height"
        target.write_text(json.dumps(mutated, indent=2), encoding="utf-8")
        assert json.loads(target.read_text())["module"]["equals"] == "ceiling_height", \
            "the mutation did not land"
        code, out = _run(tmp_path)
        assert code == 1, f"check_systems passed a lie on {pid}:\n{out}"
        assert "no derived rule reads 'ceiling_height'" in out, out

    def test_the_real_declarer_checks_clean_alone(self, tmp_path):
        """And the converse, so the CLI half is not merely a checker that fails everything."""
        for pid, (rel, p) in sorted(_packs().items()):
            if p["module"].get("equals") and rel.startswith(os.path.join("proportions",
                                                                         "systems")):
                (tmp_path / f"{pid}.json").write_text(json.dumps(p), encoding="utf-8")
        assert sorted(tmp_path.iterdir()), "no declarer in systems/ to check"
        code, out = _run(tmp_path)
        assert code == 0, out
