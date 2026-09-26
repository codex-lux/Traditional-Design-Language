"""A variant id may appear twice in one slot only as a condition (WP-14.33).

Ruled 26 Sep 2026: `georgian-colonial-american` carried seventeen repeated variant ids. Twelve
restate a variant under an `applies_when` -- a status that depends on the region, the date or the
wall -- and are legitimate. Five restated it with no condition at all, a bare row beside a noted
one; those were deleted, the noted row kept, and `build/check_kits.py::check_duplicate_variants`
refuses the shape. Measured across the deletion: 18 of 164 styles resolve differently, every
difference being the bare row gone -- `corinthian` and `composition-shingle` no longer resolve
BOTH permitted and atypical -- or, for `door_surround`, the same rows in a different order.
"""
import ast
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ck():
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import check_kits
    return check_kits


def _errs(variants):
    errs = []
    _ck().check_duplicate_variants(errs, "k", {"slots": {"s": {"variants": variants}}})
    return errs


def test_a_repeat_under_a_condition_is_a_condition_and_passes():
    """The twelve legitimate pairs have this shape: stated plainly, then again where it differs."""
    assert _errs([
        {"id": "gambrel", "status": "permitted"},
        {"id": "gambrel", "status": "atypical", "applies_when": {"regions": ["New England"]}},
        {"id": "gambrel", "status": "forbidden", "applies_when": {"regions": ["Chesapeake"]}},
    ]) == []


def test_a_bare_repeat_is_a_second_answer_and_is_refused_by_row():
    """The shipped defect: `order/corinthian` permitted and then atypical with a note, and the
    resolver kept both rows, so the answer depended on which one a reader took."""
    errs = _errs([{"id": "corinthian", "status": "permitted"},
                  {"id": "corinthian", "status": "atypical", "note": "richest interiors only"}])
    assert len(errs) == 1 and "'corinthian' 2 times" in errs[0] and "row 2" in errs[0], errs


def test_two_op_rows_for_one_id_are_held_to_the_same_rule():
    """`apply_variant_ops` lets the last `replace` silently win, which is the same two-answers
    defect with the choice made by position -- the `door_surround` pair was this shape."""
    errs = _errs([{"id": "broken-scroll-pediment", "status": "permitted", "op": "replace"},
                  {"id": "broken-scroll-pediment", "status": "permitted", "op": "replace",
                   "note": "Doorways only."}])
    assert len(errs) == 1, errs


def test_two_rows_under_the_same_condition_are_refused():
    errs = _errs([{"id": "slate", "status": "permitted"},
                  {"id": "slate", "status": "permitted", "applies_when": {"construction": ["x"]}},
                  {"id": "slate", "status": "atypical", "applies_when": {"construction": ["x"]}}])
    assert len(errs) == 1 and "same `applies_when`" in errs[0], errs


def test_the_corpus_holds_none_and_the_permitted_branch_is_really_reached():
    """No kit carries an unconditional repeat, AND the corpus carries conditional ones -- without
    the second half an empty result would say nothing about whether the rule lets a legitimate
    repeat through, which is the half a too-strict rule would break."""
    ck = _ck()
    errs, conditional = [], 0
    for path in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        kit = json.load(open(path, encoding="utf-8"))
        ck.check_duplicate_variants(errs, os.path.basename(path), kit)
        for rec in (kit.get("slots") or {}).values():
            ids = [v.get("id") for v in (rec.get("variants") or []) if isinstance(v, dict)]
            conditional += sum(1 for i in set(ids) if ids.count(i) > 1)
    assert errs == []
    assert conditional >= 10, f"only {conditional} repeated ids in the corpus"


def test_main_runs_it_on_every_kit():
    """The join, which a driven function cannot see: `main()` must call it."""
    src = open(os.path.join(ROOT, "build", "check_kits.py"), encoding="utf-8").read()
    main = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "main")
    called = {c.func.id for c in ast.walk(main) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
    assert "check_duplicate_variants" in called
