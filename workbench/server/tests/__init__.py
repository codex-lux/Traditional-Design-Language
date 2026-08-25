"""Package marker, and it is load-bearing.

Without it this directory's conftest.py claims the top-level module name `conftest`, and
so does tests/conftest.py. Collect both suites in one pytest invocation — `pytest` at the
repo root, or `pytest tests/ workbench/server/tests` — and whichever loads second loses:
tests/test_*.py then does `from conftest import ROOT` and gets THIS conftest, which has no
such name. Nine collection errors, none of them about the code under test.

check_all.py and CI run the two suites as separate processes, which is why nothing caught
it. A contributor typing `pytest` did.
"""
