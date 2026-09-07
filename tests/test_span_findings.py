"""WP-11.12 — the clear span reaches the critic and the sheet (OQ 98's reporting half).

`build/structure.py::span_check` has measured the clear span between bearing lines since
WP-3.1 and `build/geometry.py` has CHARGED it since WP-7.4. `build/plan_check.py` had **no
span or structural-capacity finding of any kind**, so a 60 ft unsupported joist run on the
Tidewater upper floor reached no sheet, no critique and no `revision_report` — a plan with a
run three times its framing capacity got a clean verdict on every surface a person reads.

WP-11.8 took the corpus figure from 11 to 23 by ranking room shape above the score, and the
only reason anyone saw it was two tests in `tests/test_structure.py` that happened to pin one
plan. Had they been written against any other, it would have been invisible.

**THE MEASUREMENT HALF OF OQ 98 IS NOT BUILT HERE and the reported number says so**:
`span_check` credits a bearing wall across the whole plate however short it actually runs, so
every count below is a FLOOR. Publishing it without saying so would be the OQ 52 family in a
new place.
"""
import glob
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, ROOT / "build" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = _mod("geometry")
PC = _mod("plan_check")


def _plans():
    return (sorted(glob.glob(str(ROOT / "plans" / "*.json")))
            + sorted(glob.glob(str(ROOT / "plans" / "reference" / "*.json"))))


_SOLVED = {}


def _solved(pf):
    if pf not in _SOLVED:
        d = json.loads(pathlib.Path(pf).read_text())
        G._SOLVE_CACHE.clear()
        _SOLVED[pf] = G.solve(json.loads(json.dumps(d)), engine="heuristic")
    return _SOLVED[pf]


def _all():
    for pf in _plans():
        if "levels" not in json.loads(pathlib.Path(pf).read_text()):
            continue
        yield pathlib.Path(pf).name, _solved(pf)


# --------------------------------------------------------------- the record names them

def test_the_record_names_every_over_capacity_span_and_the_count_still_agrees():
    """`span_capacity` has carried a COUNT and a CHARGE since WP-7.4 and nothing a reader
    could act on. `marks` is the key `relaxations` already uses one block above, for the
    identical reason stated there: *counted AND locatable*."""
    for name, sol in _all():
        sc = sol["geometry_report"]["span_capacity"]
        assert "understated" in sc, f"{name}: the record does not say the count is a floor"
        n = sc["over_capacity"]
        assert n is not None, f"{name}: unjudged is a state this corpus can reach, but not here"
        marks = sc.get("marks") or []
        assert len(marks) == n, f"{name}: {len(marks)} marks against a count of {n}"
        assert sc.get("worst_span_ft", 0) == max((m["span_ft"] for m in marks), default=0.0)
        for m in marks:
            assert m["span_ft"] > m["max_span_ft"], f"{name}: a mark that is not over capacity"
            assert m["axis"] in ("x", "y") and m["level"] in (0, 1)
            assert m["from_ft"] < m["to_ft"]
            # `member` is None where NO member in the catalogue covers the run, which is a
            # real state and a different sentence — the first version of this asserted it
            # truthy and the first version of the finding interpolated the None into prose.
            assert m["member"] is None or isinstance(m["member"], str)


# The deterministic figure, on `engine="heuristic"`. WP-11.8's report published "13 -> 25" for
# this pair with no engine named; re-derived on a `git archive` checkout of its own commit the
# deterministic pair is **11 -> 23**, and `auto` gave 28 on one run here. CLAUDE.md's own rule:
# RATCHET THE DETERMINISTIC FIGURES ONLY.
CORPUS_SPANS = 23
CORPUS_WORST_FT = 60.0


def test_the_corpus_figure_is_what_the_report_publishes():
    n = sum((s["geometry_report"]["span_capacity"]["over_capacity"] or 0) for _p, s in _all())
    worst = max((s["geometry_report"]["span_capacity"].get("worst_span_ft") or 0.0)
                for _p, s in _all())
    assert n == CORPUS_SPANS, n
    assert worst == CORPUS_WORST_FT, worst


def test_the_charge_and_the_count_are_summed_from_the_same_list():
    """WP-11.12 split the list out of `_span_charge` rather than adding a second loop over the
    same `span_check` results — that is the third-spelling defect this file's neighbours keep
    recording. The two must therefore agree by construction, and the arithmetic must not have
    moved: the Tidewater charge is 130.2 as it was before the split."""
    src = (ROOT / "build" / "geometry.py").read_text()
    assert src.count("ST.span_check(") == 1, "span_check is called from two places again"
    sol = _solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))
    sc = sol["geometry_report"]["span_capacity"]
    assert sc["over_capacity"] == 4 and sc["charge"] == 130.2


# --------------------------------------------------------------- the critic says it

def test_the_drawn_layer_emits_one_finding_per_over_capacity_span():
    total = 0
    for name, sol in _all():
        want = sol["geometry_report"]["span_capacity"]["over_capacity"]
        got = [f for f in PC.check(sol)["findings"] if f.get("kind") == "span-over-capacity"]
        assert len(got) == want, f"{name}: {len(got)} findings against {want} spans"
        total += len(got)
        for f in got:
            assert f["severity"] == "serious" and f["layer"] == "drawn"
            # the structured evidence WP-9.1 requires beside the prose
            assert f["need_ft"] and f["have_ft"] and f["have_ft"] > f["need_ft"]
            assert f["axis"] in ("x", "y") and f["level"] in (0, 1)
            assert "credited across the whole plate" in f["statement"], (
                "the finding does not say the count is a floor")
    assert total == CORPUS_SPANS


def test_the_drawn_layer_reads_the_record_and_never_recomputes_it():
    """AND THE FIRST VERSION OF THIS TEST ASSERTED A FALSE REASON. It said `plan_check` cannot
    load `structure.py`; it can and does, lazily and inside a try, in the elevation block at the
    foot of the file, and has since WP-3.2. What is actually true is better: these spans are the
    ones the SEARCH scored and `geometry.SPAN_W` charged, so a second computation here could
    convict a placement on numbers it was not chosen by — and `span_check` is called from
    exactly ONE place in the tree."""
    src = (ROOT / "build" / "plan_check.py").read_text()
    assert "span_check(" not in src, "plan_check computes the span instead of reading it"
    assert 'span_capacity' in src and '_sc.get("marks")' in src
    # CALLS, not mentions, and read with `ast` rather than by string: `build/render_section.py`
    # names the function twice in its own DOCSTRINGS. The first version of this counted every
    # occurrence and the second skipped only `#` lines — a guard that fails on prose is a guard
    # that will be deleted rather than believed.
    import ast
    calls = []
    for f in sorted(glob.glob(str(ROOT / "build" / "*.py"))):
        if pathlib.Path(f).name == "structure.py":
            continue          # its own definition and its own `build_section`
        tree = ast.parse(pathlib.Path(f).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                nm = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
                if nm == "span_check":
                    calls.append(f"{pathlib.Path(f).name}:{node.lineno}")
    assert len(calls) == 1 and calls[0].startswith("geometry.py:"), (
        f"span_check is called from {len(calls)} places outside structure.py: {calls}")


def test_an_unevaluated_span_is_info_and_never_a_silent_pass():
    """`over_capacity: None` is the third state — the construction catalogue was unreadable
    when the plan was placed. A zero there would read as *nothing exceeds capacity*, which is
    the OQ 52 lie in the cheapest possible place, and a SILENCE reads the same way."""
    sol = json.loads(json.dumps(_solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))))
    sol["geometry_report"]["span_capacity"] = {"over_capacity": None, "charge": None,
                                               "weight": 20.0, "note": "x"}
    kinds = {f.get("kind") for f in PC.check(sol)["findings"]}
    assert "span-unjudged" in kinds and "span-over-capacity" not in kinds
    unj = [f for f in PC.check(sol)["findings"] if f.get("kind") == "span-unjudged"]
    assert unj[0]["severity"] == "info" and "none is claimed clear" in unj[0]["statement"]
    # and a plan whose spans ARE all within capacity says nothing at all
    sol["geometry_report"]["span_capacity"] = {"over_capacity": 0, "marks": [], "charge": 0.0}
    kinds = {f.get("kind") for f in PC.check(sol)["findings"]}
    assert "span-unjudged" not in kinds and "span-over-capacity" not in kinds


def test_a_span_no_member_covers_reads_as_a_sentence_and_not_as_none():
    """`span_check` returns `member: None` where NO member in the catalogue covers the run, and
    its `max_span_ft` is then the largest one there is. NO PLAN IN THIS CORPUS TAKES THAT
    BRANCH — a first mutation pass proved it could not fire — so it is exercised on a fixture
    rather than left as prose nothing can reach. The first version of the finding interpolated
    the None straight into the sentence: *"...states for a None."*"""
    sol = json.loads(json.dumps(_solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))))
    sol["geometry_report"]["span_capacity"] = {
        "over_capacity": 1, "charge": 40.0, "weight": 20.0,
        "worst_span_ft": 31.0, "understated": "A bearing line is credited across the whole "
                                              "plate however short the wall runs (OQ 98).",
        "marks": [{"axis": "x", "from_ft": 0.0, "to_ft": 31.0, "span_ft": 31.0,
                   "member": None, "max_span_ft": 26.0, "level": 0, "note": "x"}]}
    f = next(x for x in PC.check(sol)["findings"] if x.get("kind") == "span-over-capacity")
    assert "None" not in f["statement"], f["statement"]
    assert "none of them covers it" in f["statement"]
    assert f["need_ft"] == 26.0 and f["have_ft"] == 31.0


def test_a_span_is_a_placement_finding_with_a_lever():
    """It stretches `critique._is_placement`'s own definition and the code says so: every other
    kind is decided against something the record DECLARES, and a plan record states no wall
    positions at all. It is classed on the other half — an engine setting really does change
    it, and WP-11.8 demonstrated that by moving the corpus figure from 11 to 23."""
    CR = _mod("critique")
    res = CR.critique(json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text()),
                      engine="heuristic")
    placed = [i for i in res["assessment"]["placement"]
              if i.get("kind") == "span-over-capacity"]
    assert len(placed) == 4, res["assessment"].keys()
    assert placed[0].get("lever"), "a placement-class finding with no lever"
    for cls in ("actionable", "architect", "advisory", "critic_suspect"):
        assert not [i for i in res["assessment"][cls] if i.get("kind") == "span-over-capacity"]


# --------------------------------------------------------------- the sheet says it

def test_both_plates_print_the_span_and_say_the_count_is_a_floor():
    import re
    RP = _mod("render_plan")
    sol = _solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))
    out = ROOT / "tests" / "_tmp_span.svg"
    try:
        RP.render(sol, str(out))
        svg = out.read_text()
    finally:
        out.unlink(missing_ok=True)
    m = re.search(r">(\d+) CLEAR SPAN\(S\) OVER THE FRAMING CAPACITY, WORST ([0-9.]+) FT[^<]*<", svg)
    assert m, "the plate does not print the span"
    assert m.group(1) == "4" and m.group(2) == "60"
    assert "HOWEVER SHORT THE WALL RUNS" in svg, "the plate does not say the count is a floor"
    js = (ROOT / "workbench" / "app" / "src" / "sheet" / "Sheet.jsx").read_text()
    assert "placement?.geometry_report?.span_capacity" in js
    assert "however short the wall runs" in js
    assert "Clear span not evaluated" in js, "the JS plate has no COULD-NOT-EVALUATE state"


def test_the_understatement_is_named_on_the_record_the_finding_and_the_plate():
    """OQ 98 has two halves and only the reporting one is built. A count published without
    its known understatement is a defect reported smaller than it is — which is the class the
    measurement half belongs to in the first place."""
    sol = _solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))
    assert "OQ 98" in sol["geometry_report"]["span_capacity"]["understated"]
    f = next(x for x in PC.check(sol)["findings"] if x.get("kind") == "span-over-capacity")
    assert "floor and not a ceiling" in f["statement"]
