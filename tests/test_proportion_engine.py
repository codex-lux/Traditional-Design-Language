"""Pins the proportion engine's selftest and cross-checker results — see
docs/proportion.md. `selftest` must keep resolving and dimensioning every
pack with zero problems; the individual checkers (orders, modules, systems)
must stay green. These are invoked as subprocesses because that's the
documented, supported entry point (`build/proportion_engine.py selftest`) and
the checkers are argv-driven scripts, not library functions.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run(*args):
    # Deliberately the "python3" the documented commands use (README.md,
    # PLAN-OF-ACTION.md section 1.3), NOT sys.executable — the test runner's
    # own interpreter may be a separate, minimal tool venv without this
    # project's dependencies (jsonschema) installed.
    return subprocess.run(
        ["python3", os.path.join(ROOT, "build", args[0])] + list(args[1:]),
        capture_output=True, text=True, cwd=ROOT,
    )


class TestProportionEngineSelftest:
    def test_selftest_resolves_every_pack_with_zero_problems(self):
        """The count is read off the library rather than hard-coded: it was 36 and is 38 after
        WP-4.6 added greek-doric and moorish-arch, and a test that has to be edited every time a
        pack lands teaches the next author to edit tests rather than to read them. What is pinned
        is the invariant -- every pack resolves, none has a problem."""
        import glob
        n = len(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json")))
        assert n >= 38, n
        proc = _run("proportion_engine.py", "selftest")
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "%d packs resolved and dimensioned, 0 problem(s)" % n in proc.stdout


class TestCheckers:
    def test_check_orders_zero_errors(self):
        proc = _run("check_orders.py")
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "0 error(s)" in proc.stdout

    def test_check_modules_zero_errors(self):
        proc = _run("check_modules.py")
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "0 error(s)" in proc.stdout

    def test_check_systems_zero_errors(self):
        proc = _run("check_systems.py")
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "0 error(s)" in proc.stdout


class TestVignolaPedestalIsNotOneThird:
    """One of the sharpest findings on record: Vignola's 'pedestal = 1/3
    column' rule of thumb is FALSE in his own Corinthian and Composite plates
    — the engine encodes what the authority drew (7 modules of a 20-module
    column, i.e. 0.35), not the folklore about what he wrote. If this pack
    ever gets 'corrected' back to a clean 1/3 by someone who hasn't read
    docs/proportion.md, this test catches it."""

    def _ratio(self, order_id):
        sys.path.insert(0, os.path.join(ROOT, "build"))
        import proportion_engine as pe
        result = pe.resolve(order_id)
        pedestal_modules = result["assemblies"]["pedestal"]["height_modules"]
        column_modules = result["column"]["height_modules"]
        return pedestal_modules / column_modules

    def test_corinthian_pedestal_is_035_not_one_third(self):
        ratio = self._ratio("vignola-corinthian")
        assert abs(ratio - 0.35) < 0.001
        assert abs(ratio - (1 / 3)) > 0.01, "drifted back toward the folklore 1/3"

    def test_composite_pedestal_is_also_035(self):
        ratio = self._ratio("vignola-composite")
        assert abs(ratio - 0.35) < 0.001
