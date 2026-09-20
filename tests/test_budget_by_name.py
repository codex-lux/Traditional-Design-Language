"""WP-14.4 -- a batch caller gets the batch budget, and it must be passed BY NAME.

WP-11.8 ruled two placement budgets with a stated reason: `BUDGET_BATCH_S` (40 s) is
`geometry.solve`'s own default, for `check_all`, `corpus.drawing()`, the CLI and the reference
plans -- *where a proof is worth waiting for* -- and `BUDGET_INTERACTIVE_S` (25 s) is passed BY
NAME by the routes with a person waiting behind a 400 ms debounce.

`build/compose.py` is a BATCH caller and was on the wrong side of that ruling by accident of a
default: it passed no `time_limit_s`, and `revise()` spelled its own default as the bare literal
`25.0`. So a compose -- a job nobody is waiting on -- placed every candidate at the interactive
budget, and `spec-builder-colonial`'s first placement falls back to the SEARCH at 25 s and
reaches CP-SAT at 40.

THIS FILE GUARDS THE WIRING AND NOT THE NUMBERS. The numbers are `geometry`'s and may be re-ruled;
what must not silently change is WHICH of them each caller gets, because that is the ruling.
"""
import ast
import importlib.util
import inspect
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEO = _load("geometry_b", "build/geometry.py")
RV = _load("revise_b", "build/revise.py")
CR = _load("critique_b", "build/critique.py")


def test_the_two_budgets_are_actually_different():
    """THE PREMISE, asserted first.

    Every other assertion in this file compares one budget against the other. If they were ever
    set equal, all of them would pass while saying nothing at all -- WP-11.15's *a fixture where
    both branches return the same number guards neither*, applied to the module constants the
    rest of the file rests on."""
    assert GEO.BUDGET_INTERACTIVE_S != GEO.BUDGET_BATCH_S, (
        "the two budgets are equal, so nothing below this line distinguishes a batch caller "
        "from an interactive one -- re-derive WP-11.8's ruling before deleting these tests")
    assert GEO.BUDGET_BATCH_S > GEO.BUDGET_INTERACTIVE_S, \
        "the batch budget is the larger one; a proof is worth waiting for where nobody waits"


def test_the_loop_defaults_to_the_interactive_budget_and_names_it():
    """The VALUE is unchanged and the SPELLING is the point.

    Both defaults were the bare literal `25.0` -- WP-11.8's ruling written a third and fourth
    time, where a change to the constant would have moved neither. A caller that passes nothing
    gets exactly what it always got; it now gets it from the one place the number lives."""
    for fn in (RV.revise, CR.critique):
        got = inspect.signature(fn).parameters["time_limit_s"].default
        assert got == GEO.BUDGET_INTERACTIVE_S, (
            f"{fn.__module__}.{fn.__name__} defaults to {got!r}, not the interactive budget")


def test_compose_passes_the_batch_budget_by_name_at_every_placing_call():
    """READ THE AST, NOT THE TEXT, and read EVERY placing call site.

    `compose` calls `RV.revise` three times: the declared loop (`place=False`, no placement, so
    the budget is irrelevant), the main placed loop, and WP-14.2's budget-skip branch, which
    places a skipped candidate so its card is of the same kind of house as its siblings'. The
    last two must BOTH pass the batch budget -- a set whose revised cards were placed at 40 s
    and whose skipped ones were placed at 25 would be two instruments again, which is the defect
    WP-14.2 removed one field over.

    A source-text grep would pass on one call site of two. This walks the calls."""
    src = open(os.path.join(ROOT, "build", "compose.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    placing, bare = 0, []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if not (isinstance(f, ast.Attribute) and f.attr == "revise"
                and isinstance(f.value, ast.Name) and f.value.id == "RV"):
            continue
        kw = {k.arg: k for k in node.keywords}
        places = "place" in kw and getattr(kw["place"].value, "value", None) is True
        if not places:
            continue
        placing += 1
        tl = kw.get("time_limit_s")
        ok = (tl is not None and isinstance(tl.value, ast.Attribute)
              and tl.value.attr == "BUDGET_BATCH_S")
        if not ok:
            bare.append(node.lineno)
    assert placing >= 2, (
        f"expected at least two PLACING RV.revise calls in compose.py and found {placing} -- "
        f"if a call site was removed, re-derive which; this test is about all of them")
    assert not bare, (
        f"compose.py line(s) {bare} place a candidate without passing GEO.BUDGET_BATCH_S by "
        f"name, so they fall back to `revise()`'s interactive default. A compose is a job; "
        f"WP-11.8's ruling gives it the batch budget.")


def test_the_interactive_routes_still_pass_the_interactive_one_by_name():
    """The other half of the ruling, and the direction that costs a person their afternoon.

    Raising the batch budget is cheap; raising the interactive one is not, and the infrastructure
    audit measured one person dragging a wall at ~85% of the server's whole evaluate capacity. If
    an interactive route ever stops naming its budget it inherits whatever the default happens to
    be, which is how `compose` came to be on the wrong side of this."""
    hits = 0
    for rel in ("workbench/server/evaluate.py", "mcp_server/core.py"):
        src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        hits += src.count("time_limit_s=geo.BUDGET_INTERACTIVE_S")
    assert hits >= 3, (
        f"expected the interactive routes to name BUDGET_INTERACTIVE_S at every call and found "
        f"{hits}; a route that stops naming it silently inherits the default")


def test_the_heuristic_path_does_not_pay_for_the_larger_budget():
    """Why this change costs `check_all` nothing.

    The build runs the composer on the fast engine, where `time_limit_s` bounds a CP solve that
    never happens. Measured: 0.53 s at 25 and 0.26 s at 40 on `spec-builder-colonial`. Asserted
    as a RELATION rather than a duration, because a timing pin is a fact about the machine."""
    import json
    plan = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json")))
    outs = []
    for tl in (GEO.BUDGET_INTERACTIVE_S, GEO.BUDGET_BATCH_S):
        GEO._SOLVE_CACHE.clear()
        out = GEO.solve(json.loads(json.dumps(plan)), engine="heuristic", time_limit_s=tl)
        outs.append(((out["geometry_report"] or {}).get("solver") or {}).get("engine"))
    assert outs == ["heuristic", "heuristic"], (
        f"the heuristic path must be indifferent to the CP budget; got {outs}")
