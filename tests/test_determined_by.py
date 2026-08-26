"""OQ 19 -- `determined_by` was declarative only.

`porch_ceiling` says it is determined by the order, the entablature and the porch support, which
is better than prose, and nothing resolved it because the schema never said what the
determination MEANS. Giving it three enforceable meanings -- the determiners must be bound, the
graph must be acyclic, and a determined slot may not state a dimensional number as an
independent claim -- found four things in the corpus, and two of them were wrong data rather
than missing notes.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_kits():
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import check_kits
    return check_kits


def kit(style):
    return json.load(open(os.path.join(ROOT, "kits", "%s.kit.json" % style)))


def run(kitdoc, ont_ids=None):
    ck = check_kits()
    errs, warns = [], []
    ids = ont_ids or {s["id"] for g in json.load(
        open(os.path.join(ROOT, "elements", "slots.json")))["groups"] for s in g["slots"]}
    ck.check_determined_by(errs, warns, "t", kitdoc, ids)
    return errs, warns


# ---------------------------------------------------------------- the three meanings


def test_a_determiner_that_is_not_bound_makes_the_slot_unjudged():
    """A slot that says it is whatever the order requires, on a kit whose order slot is empty,
    is unjudged -- and it read as specified, which is this corpus's first discipline inverted."""
    errs, warns = run({"slots": {
        "order": {"binding": "open", "status": "empty"},
        "column": {"binding": "specified", "status": "drafted", "determined_by": ["order"]}}})
    assert errs == []
    assert any("UNJUDGED, not specified" in w for w in warns)


def test_two_slots_that_each_determine_the_other_decide_nothing():
    errs, _w = run({"slots": {
        "order": {"binding": "specified", "status": "drafted", "determined_by": ["column"]},
        "column": {"binding": "specified", "status": "drafted", "determined_by": ["order"]}}})
    assert any("decides nothing" in e for e in errs)


def test_a_slot_cannot_determine_itself():
    errs, _w = run({"slots": {"order": {"binding": "specified", "status": "drafted",
                                        "determined_by": ["order"]}}})
    assert any("names itself" in e for e in errs)


def test_a_determiner_must_be_a_real_slot():
    errs, _w = run({"slots": {"column": {"binding": "specified", "status": "drafted",
                                         "determined_by": ["not-a-slot"]}}})
    assert any("is not a slot" in e for e in errs)


def test_an_unsourced_number_on_a_determined_slot_is_flagged():
    """The schema's own note has always said it: specifying it separately either restates the
    determiner or contradicts it, and an unsourced editorial number is the one case nobody can
    tell those two apart in."""
    base = {"order": {"binding": "specified", "status": "drafted"}}
    def slot(param):
        return {"slots": dict(base, column={"binding": "specified", "status": "drafted",
                                            "determined_by": ["order"],
                                            "parameters": {"w_in": param}})}
    _e, warns = run(slot({"value": 9, "unit": "in", "kind": "editorial"}))
    assert any("restatement and contradiction look identical" in w for w in warns)
    for ok in ({"value": 9, "unit": "in", "kind": "derived"},
               {"value": 9, "unit": "in", "kind": "editorial", "source": "gibbs"},
               {"expr": "module / 8", "unit": "in", "kind": "editorial"},
               {"value": 9, "unit": "in", "kind": "editorial", "note": "why it is independent"}):
        _e, w = run(slot(ok))
        assert not any("restatement and contradiction" in x for x in w), ok
    # a non-dimensional parameter is not a determination claim and is not flagged
    _e, w = run(slot({"value": "flat relief", "unit": "none", "kind": "editorial"}))
    assert not any("restatement and contradiction" in x for x in w)


# ---------------------------------------------------------------- what it found


def test_the_reveal_pair_is_divided_by_trade_and_no_longer_identical():
    """OQ 12's split copied the whole parameter set into both halves rather than dividing it,
    leaving each half carrying the other trade's numbers and the per-parameter
    applies_when.construction doing the discrimination the split was supposed to do."""
    k = kit("georgian-colonial-american")
    m, f = k["slots"]["reveal_masonry"], k["slots"]["reveal_frame"]
    assert m["parameters"] != f["parameters"]
    assert "frame_wall_thickness_in" not in m["parameters"]
    assert "reveal_in" in m["parameters"] and "reveal_in" in f["parameters"]
    assert m["parameters"]["reveal_in"]["range"] == [4, 8]
    assert f["parameters"]["reveal_in"]["range"] == [0.75, 2]
    for s in (m, f):
        for p in s["parameters"].values():
            assert "applies_when" not in p or "construction" not in (p.get("applies_when") or {}), \
                "the slot IS the construction case; saying it again per-parameter is the duplication"


def test_the_tidewater_frame_reveal_no_longer_states_the_masonry_answer():
    """It was a verbatim copy of reveal_masonry, so a frame Tidewater house would have been
    drawn with a 13.5 in wall and a 4-8 in reveal."""
    f = kit("tidewater-georgian")["slots"]["reveal_frame"]
    assert f["binding"] == "extends"
    assert not f.get("parameters"), "it states nothing of its own, because nothing sources one"


def test_the_two_slots_that_disagree_about_the_step_at_a_floor_both_say_so():
    """Recorded, not silently resolved: correcting a number on a guess is worse than recording
    that two slots disagree."""
    k = kit("georgian-colonial-american")
    a = k["slots"]["reveal_masonry"]["parameters"]["step_at_floor_in"]
    b = k["slots"]["construction_type"]["parameters"]["wythe_step_at_floor"]
    assert a["value"] == 4.5 and "13.5" in a["note"]
    assert "SUSPECT" in b["note"] and "4.5" in b["note"]


def test_the_corpus_leaves_exactly_one_determined_by_warning_and_it_is_a_true_one():
    """Every other case is now either derived, sourced, or carries a note saying which of
    restatement and independence it is. The survivor is a real unjudged slot: sod on birch bark
    needs a shallow pitch and a split shingle a steep one, and roof_pitch is empty."""
    ck = check_kits()
    ids = {s["id"] for g in json.load(
        open(os.path.join(ROOT, "elements", "slots.json")))["groups"] for s in g["slots"]}
    errs, warns = [], []
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        d = json.load(open(p))
        ck.check_determined_by(errs, warns, d["style"], d, ids)
    assert errs == [], errs
    oq19 = [w for w in warns if "OQ 19" in w]
    assert len(oq19) == 1, oq19
    assert "scandinavian-log-vernacular" in oq19[0] and "roof_material" in oq19[0]
