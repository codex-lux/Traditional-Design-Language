"""A variant id may appear twice in one slot only as a condition (WP-14.33).

Ruled 26 Sep 2026: `georgian-colonial-american` carried seventeen repeated variant ids. Twelve
restate a variant under an `applies_when` -- a status that depends on the region, the date or the
wall -- and are legitimate. Five restated it with no condition at all, a bare row beside a noted
one; those were deleted, the noted row kept, and `build/check_kits.py::check_duplicate_variants`
refuses the shape. Measured across the deletion: 18 of 164 styles resolve differently, every
difference being the bare row gone -- `corinthian` and `composition-shingle` no longer resolve
BOTH permitted and atypical -- or, for `door_surround`, the same rows in a different order.

AND THE KIT FILES WERE NOT THE WHOLE OF IT (WP-14.33's audit). The resolver indexed each id to
its LAST row, so a child's `replace` over an id its parent states twice overwrote only the
conditional row and left the parent's plain row standing: `tidewater-georgian`'s gambrel resolved
`permitted` AND `forbidden`, neither conditional -- the shape R8 ruled out, surviving in the
resolved record every consumer reads. Six (style, slot, id) triples over three styles; the fix
moved nothing else in the 164. The checker's three loopholes (a note-only condition, one condition
spelled two ways, a `remove` sharing its id) and a driven wiring guard came from the same audit.
"""
import ast
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ck():
    if os.path.join(ROOT, "build") not in sys.path:
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


def test_main_runs_it_on_every_kit_and_its_errors_decide_the_exit(monkeypatch, capsys):
    """The join, DRIVEN (WP-14.33's audit). The first version read `main()`'s source for the
    name, which passes with the call under an `if False:`, handed a throwaway list, or made once
    outside the loop. A spy standing in for the rule reports one error per kit it is shown; if
    `main()` passes it the kit, passes it the list that decides the exit, and does so inside the
    loop, the run fails naming the kit."""
    import pytest
    ck = _ck()
    seen = []

    def spy(errs, nid, kit):
        seen.append(nid)
        assert isinstance(kit, dict) and kit.get("style") == nid
        errs.append("%s: SPY-ERROR" % nid)

    monkeypatch.setattr(ck, "check_duplicate_variants", spy)
    monkeypatch.setattr(sys, "argv", ["check_kits.py", "georgian-colonial-american"])
    with pytest.raises(SystemExit) as ex:
        ck.main()
    assert ex.value.code not in (0, None)
    assert seen == ["georgian-colonial-american"]
    out = capsys.readouterr()
    assert "georgian-colonial-american: SPY-ERROR" in out.out + out.err


def test_a_note_alone_conditions_on_nothing():
    """`applies_when: {"note": ...}` has no key a reader could test, so it is a bare row wearing a
    condition. Fifteen kit rows carry exactly that shape today, none of them on a repeat."""
    errs = _errs([{"id": "gabled", "status": "permitted"},
                  {"id": "gabled", "status": "atypical", "applies_when": {"note": "rear only"}}])
    assert len(errs) == 1 and "row 2" in errs[0], errs


def test_one_condition_spelled_two_ways_is_one_condition():
    """Compared by what it conditions on: a region list in another order, or the same condition
    with a different note, is the same condition twice."""
    assert len(_errs([{"id": "slate", "status": "permitted"},
                      {"id": "slate", "status": "atypical", "applies_when": {"regions": ["A", "B"]}},
                      {"id": "slate", "status": "forbidden", "applies_when": {"regions": ["B", "A"]}}])) == 1
    assert len(_errs([{"id": "slate", "status": "permitted"},
                      {"id": "slate", "status": "atypical",
                       "applies_when": {"regions": ["A"], "note": "one"}},
                      {"id": "slate", "status": "forbidden",
                       "applies_when": {"regions": ["A"], "note": "two"}}])) == 1
    # and a date range is an ordered pair, not a set
    assert _errs([{"id": "fanlight", "status": "permitted"},
                  {"id": "fanlight", "status": "atypical", "applies_when": {"date_range": [1700, 1780]}},
                  {"id": "fanlight", "status": "canonical", "applies_when": {"date_range": [1780, 1700]}}]) == []


def test_a_remove_may_not_share_its_id():
    """`remove` then `add` of one id resolves by which op the resolver meets first."""
    errs = _errs([{"id": "gambrel", "op": "remove"},
                  {"id": "gambrel", "status": "atypical", "op": "add",
                   "applies_when": {"regions": ["New England"]}}])
    assert len(errs) == 1 and "remove" in errs[0], errs


def test_the_condition_keys_are_the_schemas_less_its_note():
    """A key the schema adds must be named here, or a condition on it reads as no condition and
    a legitimate repeat is refused -- loud, but for the wrong reason."""
    schema = json.load(open(os.path.join(ROOT, "schema", "kit.schema.json"), encoding="utf-8"))
    keys = set(schema["$defs"]["applies_when"]["properties"]) - {"note"}
    assert set(_ck().CONDITION_KEYS) == keys


def test_no_resolved_kit_states_one_variant_twice_without_a_condition():
    """THE RESOLVED RECORD, which is what every consumer reads (WP-14.33's audit). The kit files
    were clean and the resolver still produced the defect: a child's `replace` over a parent id
    stated twice overwrote only the conditional row, so `tidewater-georgian`'s gambrel resolved
    `permitted` AND `forbidden`, neither conditional -- 6 (style, slot, id) triples over 3
    styles. Swept over all 164 styles; the premise asserts the conditional repeats survive, so an
    empty result cannot come from the resolver dropping every repeat."""
    if os.path.join(ROOT, "build") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    rk = modcache.load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
    ck = _ck()
    graph = rk.load_graph()
    bad, conditional, styles = [], 0, 0
    for nid in sorted(graph["nodes"]):
        try:
            slots = rk.resolve_slots(graph, rk.chain_for(graph, nid), rk.scope_for(graph, nid))[0]
        except SystemExit:
            continue
        styles += 1
        for sid, rec in slots.items():
            if not isinstance(rec, dict):
                continue
            byid = {}
            for v in rec.get("variants") or []:
                if isinstance(v, dict):
                    byid.setdefault(v.get("id"), []).append(ck.condition_key(v.get("applies_when")))
            for vid, conds in byid.items():
                if len(conds) < 2:
                    continue
                if None in conds[1:] or len(set(conds)) != len(conds):
                    bad.append((nid, sid, vid))
                else:
                    conditional += 1
    assert styles == 164, styles
    assert bad == [], bad[:10]
    assert conditional >= 100, conditional


def _ops(base, deltas):
    if os.path.join(ROOT, "build") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    rk = modcache.load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
    return rk.apply_variant_ops(base, deltas)[0]


def _rows(vs):
    return [(v["id"], v.get("status"), (v.get("applies_when") or {}).get("regions")) for v in vs]


PARENT = [{"id": "gambrel", "status": "permitted"},
          {"id": "side-gable", "status": "canonical"},
          {"id": "gambrel", "status": "atypical", "applies_when": {"regions": ["New England"]}}]


def test_a_replace_supersedes_every_inherited_row_of_its_id_at_the_first():
    """The defect's own shape: the child's one row is the child's whole answer, standing where
    the parent's first row stood, and neither of the parent's two rows survives beside it."""
    got = _ops(PARENT, [{"id": "gambrel", "status": "forbidden", "op": "replace"}])
    assert _rows(got) == [("gambrel", "forbidden", None), ("side-gable", "canonical", None)]


def test_an_add_over_an_inherited_id_supersedes_it_too():
    got = _ops(PARENT, [{"id": "gambrel", "status": "atypical"}])
    assert _rows(got) == [("gambrel", "atypical", None), ("side-gable", "canonical", None)]


def test_a_remove_removes_every_row_of_its_id():
    assert _rows(_ops(PARENT, [{"id": "gambrel", "op": "remove"}])) == [("side-gable", "canonical", None)]


def test_a_child_may_state_a_variant_plainly_and_again_under_a_condition():
    """Rows the same delta list writes are the child's own statement and sit side by side --
    the second must not supersede the first, or a child could never say what R8 ruled legitimate."""
    got = _ops(PARENT, [{"id": "gambrel", "status": "forbidden", "op": "replace"},
                        {"id": "gambrel", "status": "permitted", "op": "add",
                         "applies_when": {"regions": ["Hudson Valley"]}}])
    assert _rows(got) == [("gambrel", "forbidden", None), ("side-gable", "canonical", None),
                          ("gambrel", "permitted", ["Hudson Valley"])]


def test_an_inherited_list_is_not_mutated():
    before = json.dumps(PARENT, sort_keys=True)
    _ops(PARENT, [{"id": "gambrel", "status": "forbidden", "op": "replace"}])
    assert json.dumps(PARENT, sort_keys=True) == before
