"""WP-13.4 — the refusal to draw, at the leaf and at the record.

Lucas ruled 15 Sep 2026: **a placement that breaks a hard fact of the type is REFUSED, not
drawn; the bench shows the conflict set; the brief or the parti is what changes.** That
reverses the 25 Aug ruling this repository pinned in `tests/test_solver.py` -- "the partner
hears the refusal and still sees a drawing" -- for every user-facing surface. The RECORD keeps
the search's least-bad placement, because it is the conflict set's own explanation and the wall
drag's working sketch; no surface a person reads draws it.

THE CONTRACT, in one place so both slices of the package were built against one text:

    build/typefacts.py::refusal(plan) -> None | {
        "kind": "infeasible" | "type-fact-downgraded",
        "facts":     [names of the type facts whose status is "downgraded"],
        "conflicts": [the prover's own conflict entries, or one row per downgraded fact],
        "lines":     [one reader-facing sentence per conflict],
        "engine":    geometry_report.solver.engine,
        "status":    geometry_report.solver.status}

UNJUDGED DOES NOT REFUSE, and that is the half most likely to be lost: a house stating no
hearth is not refused for its hearth, a one-level house is not refused for bearing continuity
it cannot have, and a record carrying no stacking tally is not refused for stacks nobody could
judge. Only a fact MEASURED and found not to hold, or a PROVEN infeasibility, refuses. The
three states are held, downgraded and unjudged; collapsing the third into either of the others
is what this corpus names first, and a refusal on unjudged would refuse most of this corpus for
facts its records do not state.

The HTTP half of the contract is `workbench/server/tests/test_refusal_routes.py`.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import modcache as mc  # noqa: E402

TF = mc.load("typefacts", os.path.join(ROOT, "build", "typefacts.py"))
GEO = mc.load("geometry", os.path.join(ROOT, "build", "geometry.py"))


def _plan(name="tidewater-georgian-careful"):
    d = "plans" if os.path.exists(os.path.join(ROOT, "plans", f"{name}.json")) \
        else os.path.join("plans", "reference")
    return json.load(open(os.path.join(ROOT, d, f"{name}.json"), encoding="utf-8"))


# ---------------------------------------------------------------- the three states

def test_a_record_with_no_type_facts_is_not_refused():
    """No measurement, no verdict. An empty record is UNJUDGED and unjudged does not refuse --
    the alternative would refuse every record that has never been placed."""
    assert TF.refusal({}) is None
    assert TF.refusal({"geometry_report": {}}) is None


def test_every_fact_unjudged_does_not_refuse():
    """The half a reader loses first, driven on all four facts at once. A house that states no
    hearth, no stack and one storey measures three unjudged facts and one held; refusing it
    would be the fake-unjudged collapse wearing its other face."""
    rec = {"geometry_report": {"type_facts": {"status": {
        "tiling": "held", "stacks": "unjudged", "bearing": "unjudged", "hearth": "unjudged"}}}}
    assert TF.refusal(rec) is None
    rec["geometry_report"]["type_facts"]["status"] = {
        k: "unjudged" for k in ("tiling", "stacks", "bearing", "hearth")}
    assert TF.refusal(rec) is None, "a record nothing could judge is not a record refused"


def test_one_downgraded_fact_refuses_and_names_it():
    """And the sentence it prints is the FACT'S OWN, not a second rendering of it: `stacks`
    states its detail where the measurement is made, and a refusal that restated it would be
    the second spelling this corpus keeps meeting."""
    detail = "5 of 5 judged declared stack(s) are drawn clear of the room they name"
    rec = {"geometry_report": {"type_facts": {
        "status": {"tiling": "held", "stacks": "downgraded",
                   "bearing": "unjudged", "hearth": "unjudged"},
        "stacks": {"status": "downgraded", "detail": detail}}}}
    ref = TF.refusal(rec)
    assert ref is not None
    assert ref["kind"] == "type-fact-downgraded"
    assert ref["facts"] == ["stacks"], "the refusal must name WHICH fact did not hold"
    assert len(ref["lines"]) == 1 and detail in ref["lines"][0]
    assert ref["conflicts"][0]["fact"] == "stacks"
    assert ref["conflicts"][0]["detail"] == detail


def test_the_facts_are_named_in_a_stable_order():
    """Two downgraded facts must come back in one order however the status dict was built, or a
    client diffing two refusals of one house reports a change nothing made."""
    a = {"geometry_report": {"type_facts": {"status": {
        "bearing": "downgraded", "stacks": "downgraded"}}}}
    b = {"geometry_report": {"type_facts": {"status": {
        "stacks": "downgraded", "bearing": "downgraded"}}}}
    assert TF.refusal(a)["facts"] == TF.refusal(b)["facts"] == ["bearing", "stacks"]


def test_a_proven_infeasibility_refuses_even_where_every_fact_holds():
    """The prover showed the declared facts cannot all hold, so the placement on the record is
    a labelled relaxation of a brief with no solution -- `infeasible` is the stronger statement
    and wins the `kind`, and the downgraded facts are still named beside it."""
    rec = {"geometry_report": {
        "type_facts": {"status": {k: "held" for k in ("tiling", "stacks", "bearing", "hearth")}},
        "infeasible": {"proven": True, "conflicts": ["r0 and r1 share a door"],
                       "note": "CP-SAT proved these requirements cannot all hold together."},
        "solver": {"engine": "heuristic (least-bad, labelled)"}}}
    ref = TF.refusal(rec)
    assert ref["kind"] == "infeasible"
    assert ref["facts"] == []
    assert ref["lines"][0] == "r0 and r1 share a door"
    assert ref["lines"][-1].startswith("CP-SAT proved")
    assert ref["engine"] == "heuristic (least-bad, labelled)"


def test_an_unproven_infeasible_block_does_not_refuse():
    """`proven` is the field, and a block that does not claim a proof is not one. The condition
    is asserted rather than assumed because `infeasible` being PRESENT is the obvious reading
    and it is not the record's."""
    rec = {"geometry_report": {"infeasible": {"proven": False, "conflicts": ["x"]}}}
    assert TF.refusal(rec) is None


# ---------------------------------------------------------------- one spelling

def test_the_refusal_lines_agree_with_the_cli_printer():
    """`typefacts.refusal` and `geometry.conflict_lines` must say the same thing about one
    infeasibility, and NOTHING IMPORTS ACROSS THAT LINE: the leaf may not import `geometry.py`
    (which loads `plan_check`, which is two rungs up the same ladder), so this test reads both
    and holds them to one sentence. That is the answer this repository already uses where an
    import is unavailable -- `test_grammar_agreement.py` reads the JavaScript and
    `engineClaim.test.mjs` reads the Python -- and it is a test rather than a comment because a
    comment cannot fail.

    The two READ DIFFERENT KEYS and that is real rather than a slip: `conflict_lines` takes the
    TOP-LEVEL `infeasible`, which is the shape `_solve_uncached`'s error path attaches, and the
    refusal takes `geometry_report.infeasible`, which is the shape every placed record carries.
    One block, two homes; the assertion is that the CONTENT agrees."""
    block = {"proven": True,
             "conflicts": ["r0 and r1 share a door", "r2 and r3 share a door"],
             "note": "CP-SAT proved these requirements cannot all hold together."}
    printed = GEO.conflict_lines({"infeasible": copy.deepcopy(block)})
    ref = TF.refusal({"geometry_report": {"infeasible": copy.deepcopy(block)}})
    # every conflict the CLI prints is a line of the refusal, and the note travels with them
    for c in block["conflicts"]:
        assert any(c in line for line in printed), f"the CLI printer dropped {c!r}"
        assert c in ref["lines"], f"the refusal dropped {c!r}"
    assert any(block["note"] in line for line in printed)
    assert block["note"] in ref["lines"]
    assert len(ref["lines"]) == len(printed), (
        "the two readers disagree about how many things there are to say")


def test_judge_writes_both_keys_and_returns_the_verdict():
    """`judge` is the one spelling with three callers -- `geometry._disclose`,
    `corpus._placed`'s short circuit and `export_dxf._solved_copy`'s. It writes the measurement
    AND the verdict, so a caller cannot get one without the other."""
    rec = {}
    got = TF.judge(rec)
    assert "type_facts" in rec["geometry_report"]
    assert "refused" in rec["geometry_report"]
    assert rec["geometry_report"]["refused"] is got


def test_typefacts_is_still_a_leaf():
    """It is written onto the record from inside `geometry._disclose` and read back by
    `disclosures.py` and by `plan_check`, which sit on different rungs of one import ladder --
    so a sibling import here closes a cycle. WP-13.4 added a function that had every reason to
    reach for `geometry.conflict_lines` and did not; this is what stops the next one."""
    import ast
    src = open(os.path.join(ROOT, "build", "typefacts.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    # READ THE STRUCTURE, NOT THE CHARACTERS. The first version of this guard searched the text
    # for "geometry.py" and went red on the module's own DOCSTRING, which explains the import
    # ladder it may not climb -- a source-text guard convicting the sentence that states the
    # rule. That is this repository's own most-repeated test defect, met while writing the
    # guard against it.
    STDLIB = {"json", "os", "collections", "math", "itertools", "functools", "__future__"}
    named = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            named |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            named.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            f = node.func
            name = getattr(f, "id", None) or getattr(f, "attr", None)
            assert name not in ("spec_from_file_location", "_mod", "_load"), (
                f"build/typefacts.py loads a module by path ({name}) -- it is a LEAF, and a "
                f"sibling load here closes the geometry -> plan_check -> structure cycle")
    assert named <= STDLIB, (
        f"build/typefacts.py has stopped being a leaf: it imports {sorted(named - STDLIB)}")


# ---------------------------------------------------------------- the record writers

def test_both_record_writers_carry_the_verdict():
    """`geometry_report.refused` is written by `_disclose`, which both record writers call --
    the defect that function exists for is a block wired into one writer and not the other
    (OQ 40's disclosure shipped that way for two phases). Asserted on the SEARCH here because
    it is deterministic; the prover's half is the `auto` sweep in the package report."""
    out = GEO.solve(_plan(), None, 60, engine="heuristic")
    gr = out["geometry_report"]
    assert "type_facts" in gr and "refused" in gr
    # and the verdict agrees with the measurement beside it, which is what makes it a reading
    down = sorted(k for k, v in gr["type_facts"]["status"].items() if v == "downgraded")
    assert (gr["refused"] or {}).get("facts", []) == down or not down


def test_the_corpus_still_refuses_something_so_the_ruling_is_live():
    """The premise every other guard in this package rests on. A tree where nothing is refused
    would leave `workbench/server/tests/drawable.py` picking the first record it tries and every
    drawing test passing for the wrong reason; a tree where nothing is DRAWABLE makes that
    module skip. The two assertions together cannot both go quiet.

    Measured 16 Sep 2026 on the search: **14 of the 16 shipped plan records are refused**, every
    one of them for `bearing`. Not pinned as a count, because the count is a property of the
    placer and moves with it; pinned as the two facts the rest of the package needs."""
    refused, drawable = [], []
    for d in ("plans", os.path.join("plans", "reference")):
        for name in sorted(os.listdir(os.path.join(ROOT, d))):
            if not name.endswith(".json"):
                continue
            plan = json.load(open(os.path.join(ROOT, d, name), encoding="utf-8"))
            out = GEO.solve(plan, None, 60, engine="heuristic")
            if "error" in out:
                continue
            (refused if (out["geometry_report"].get("refused")) else drawable).append(name)
    assert refused, (
        "no shipped record is refused on the search: the 15 Sep ruling has stopped biting, and "
        "every guard in this package that drives a refusal is now about nothing")
    assert drawable, (
        f"every one of the {len(refused)} shipped records is refused: there is no drawable "
        f"house left in this corpus, and the drawing suites can only skip")


# ---------------------------------------------------------------- the exporters

def test_the_dxf_refuses_a_refused_placement_on_both_paths():
    """`_solved_copy` has two ways in and both are judged: the short circuit (a record a client
    already had placed, which never reached a record writer) and its own `GEO.solve` for the CLI
    and library path. A guard on one alone is half a guard, and the short circuit is the one
    that had none."""
    EX = mc.load("export_dxf", os.path.join(ROOT, "build", "export_dxf.py"))
    plan = _plan()
    _orig, solved = EX._solved_copy(copy.deepcopy(plan), None, 60)
    if "refused_placement" not in solved:
        pytest.skip("COULD NOT EVALUATE: this record is not refused on this tree")
    assert "refused" not in solved, (
        "the DXF refusal set the `refusal` key, which `app.py` maps to a 501 -- the "
        "missing-library answer, and a lie about a refused house")
    assert solved["refused_placement"]["lines"]
    # and the short circuit, on the same house carried in already placed
    carried = GEO.solve(copy.deepcopy(plan), None, 60, engine="heuristic")
    _orig2, solved2 = EX._solved_copy(carried, None, 60)
    assert "refused_placement" in solved2, (
        "a record carrying a refused placement was accepted by the short circuit")


def test_the_dxf_forwards_its_refusal_rather_than_flattening_it(tmp_path):
    """AND THE FRAME ABOVE `_solved_copy` MUST NOT DROP IT, which the guard above cannot see.

    Found by mutation: rewriting `export_plan_dxf`'s wrap back to `{"error": solved["error"],
    "unexported": True}` left the test above GREEN, because that test reads `_solved_copy`'s
    own return and the flattening happens one frame up. Four sites in `export_dxf.py` carried
    that rewrap and the conflict set died at every one of them -- the same defect
    `corpus.drawing` had at four call sites, in a second file.

    So this drives the PUBLIC entry point and reads what a caller gets."""
    EX = mc.load("export_dxf", os.path.join(ROOT, "build", "export_dxf.py"))
    pytest.importorskip("ezdxf", reason="COULD NOT EVALUATE: ezdxf is not installed")
    out = EX.export_plan_dxf(copy.deepcopy(_plan()), str(tmp_path / "refused.dxf"),
                             candidates=60)
    if "refused_placement" not in out and "error" not in out:
        pytest.skip("COULD NOT EVALUATE: this record is not refused on this tree")
    assert out["refused_placement"]["lines"], (
        "the exporter's public entry flattened its refusal to a sentence: a refusal is "
        "content, and the reader it is for is one frame up")
    assert out.get("unexported") is True
    assert not (tmp_path / "refused.dxf").exists(), "a refused placement produced a file"
