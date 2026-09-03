"""A baked snapshot is a cached computation with no cache invalidation.

`oq/a-baked-pack-value-is-a-second-delivery-path` recorded that 143 kit parameters carry both an
`expr` and the `computed_at.value` that expression produced, that exactly one was of a shape a
narrow reader could evaluate, and that the count of stale snapshots was therefore **unknown, not
zero**. `build/check_kits.py::check_baked_snapshots` makes it knowable: 135 are re-derived at the
context they record and agree; 8 read a binding `computed_at` does not carry and are UNJUDGED.

THE RATCHETS IN THE CHECKER CANNOT GUARD THE INSTRUMENT, WHICH IS WHY THIS FILE EXISTS. Deleting
the gap detection sends those 8 to be judged against `DEFAULT_BINDINGS`, whose `span` is 240.0
where they were baked at 540.0 — measured, it convicts SEVEN of them as stale and lets the eighth
(which reads `room_width`, where the default happens to match) pass in silence. Both wrong
directions from one deletion, and the seven are the worse: *unjudged reported as failed*, which is
this corpus's own named dangerous direction. Meanwhile `baked_judged` rises from 135 to 143, above
its floor, and `baked_unjudged` falls from 8 to 0, below its ceiling — so neither of the checker's
own ratchets notices. The identity of the unjudged eight is therefore pinned here as a set, and
every branch is entered by mutation.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _ck():
    return modcache.load("check_kits", os.path.join(ROOT, "build", "check_kits.py"))


def _run(kit, nid="probe"):
    """Drive the shipped function and return (errors, unjudged reasons, counters)."""
    import collections
    ck = _ck()
    errs, unjudged, stats = [], [], collections.Counter()
    ck.check_baked_snapshots(errs, unjudged, nid, kit, stats)
    return errs, unjudged, stats


def _snapshot(expr, value, source="storey-graduation", **ca):
    ctx = {"ceiling_height_in": 108.0, "storey_height_in": 120.0, "opening_width_in": 36.0}
    ctx.update(ca)
    ctx["value"] = value
    return {"slots": {"s": {"parameters": {"p": {
        "expr": expr, "computed_at": ctx, "unit": "count", "kind": "derived", "source": source}}}}}


# ------------------------------------------------------------------ the corpus

@pytest.fixture(scope="module")
def corpus():
    """Every kit, through the checker's own main-loop inputs rather than a second walk."""
    import collections
    import glob
    import json
    ck = _ck()
    errs, unjudged, stats = [], [], collections.Counter()
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        kit = json.load(open(p, encoding="utf-8"))
        ck.check_baked_snapshots(errs, unjudged, os.path.basename(p).split(".")[0], kit, stats)
    return errs, unjudged, stats


def test_no_baked_snapshot_contradicts_its_own_expression(corpus):
    """The measurement the question was missing: of the snapshots that CAN be judged, how many
    are stale? Zero. That is a different sentence from "none is stale", and the next test is why."""
    errs, _unjudged, _stats = corpus
    assert errs == [], errs


def test_the_unjudged_eight_are_named_and_not_merely_counted(corpus):
    """THE POINT OF THE WHOLE FILE. `computed_at` carries three bindings and these expressions
    read five, so any verdict on them is really a verdict about a number nobody wrote down. They
    reconcile at a span of 540 — which is `check_kits.REF_CTX`'s value and evidently what they
    were baked at — but that is a reconstruction, not a record, and a check may not convict or
    acquit on it.

    Pinned as a SET, not a count, because the count moves the wrong way under mutation: removing
    the gap detection takes `baked_judged` to 143 (above its floor) and `baked_unjudged` to 0
    (below its ceiling), so the checker's own ratchets stay satisfied while seven of these are
    falsely convicted. Every one is on `georgian-colonial-american`, which is a fact about where
    the facade and trim rules were baked rather than a coincidence worth relying on."""
    _errs, unjudged, stats = corpus
    got = {u.split(":")[0] for u in unjudged}
    assert got == {
        "georgian-colonial-american.composition_parti.bay_count_from_span",
        "georgian-colonial-american.composition_parti.front_height_over_width",
        "georgian-colonial-american.gable_treatment.pediment_rise_in",
        "georgian-colonial-american.height_proportion.front_height_over_width",
        "georgian-colonial-american.window_grouping_rule.bay_count",
        "georgian-colonial-american.window_proportion.width_from_room_in",
        "georgian-colonial-american.pediment.rise_over_span",
        "georgian-colonial-american.wainscot.panel_count_on_an_18ft_wall",
    }, sorted(got)
    assert stats["baked_unjudged"] == len(got) == 8
    # Seven read `span` and one reads `room_width`. Naming the binding is the whole remedy: record
    # it in `computed_at` and the snapshot becomes judgeable without anything here changing.
    assert sum(1 for u in unjudged if "reads span" in u) == 7, unjudged
    assert sum(1 for u in unjudged if "reads room_width" in u) == 1, unjudged


def test_the_judged_count_is_the_rest_of_the_corpus(corpus):
    """135 + 8 = 143, the figure the question published. If this drifts, one of the three numbers
    is wrong and the arithmetic says so rather than leaving a reader to notice."""
    _errs, unjudged, stats = corpus
    assert stats["baked_judged"] == 135, stats
    assert stats["baked_judged"] + stats["baked_unjudged"] == 143


# ------------------------------------------------------------------ mutation

def test_it_catches_the_defect_it_was_written_for():
    """WP-9.6 moved `storey-graduation`'s stair expression to `ceil(module / 7.5)` and the baked
    copy kept the old value: one object reading the new expression and `17` where it gives 16.
    `check_kits` came back OK and `check_addresses --strict` came back at its ratchet, both with
    the defect in place. This is the assertion that they were missing."""
    errs, unjudged, stats = _run(_snapshot("ceil(module / 7.5)", 17))
    assert len(errs) == 1, (errs, unjudged)
    assert "stale" in errs[0] and "17" in errs[0] and "16" in errs[0], errs[0]
    assert stats["baked_judged"] == 1 and stats["baked_unjudged"] == 0


def test_the_same_snapshot_passes_when_it_agrees():
    """A check that fires on everything is not a check. 16 is what the expression gives."""
    errs, _unjudged, stats = _run(_snapshot("ceil(module / 7.5)", 16))
    assert errs == [], errs
    assert stats["baked_judged"] == 1


def test_a_snapshot_reading_an_unrecorded_binding_is_unjudged_and_never_passed():
    """`span` is not in `computed_at`; the expression reads it; so the snapshot is outside this
    check rather than inside it and passing. The value given is the one the corpus records (108.0
    at a span of 540), so with the gap detection removed this becomes a false CONVICTION at the
    default span of 240 rather than a false pass — the direction that matters, and the reason
    this asserts `errs == []` and the unjudged path together rather than either alone."""
    errs, unjudged, stats = _run(_snapshot("span / 5.0", 108.0, source="facade-classical"))
    assert errs == [], errs
    assert stats["baked_judged"] == 0
    assert stats["baked_unjudged"] == 1
    assert "reads span" in unjudged[0], unjudged


def test_recording_the_binding_closes_the_gap_without_touching_the_checker():
    """The remedy, proved rather than asserted in prose: add `span_in` to `computed_at` and the
    same snapshot becomes judgeable. The reader maps `<name>_in` to the binding `<name>` for any
    key, not for a list of three, so this needs no change to `check_baked_snapshots`."""
    errs, unjudged, stats = _run(
        _snapshot("span / 5.0", 108.0, source="facade-classical", span_in=540.0))
    assert unjudged == [], unjudged
    assert stats["baked_judged"] == 1 and errs == []
    # ...and it then genuinely judges: the wrong value now fails.
    errs2, _u2, _s2 = _run(
        _snapshot("span / 5.0", 999.0, source="facade-classical", span_in=540.0))
    assert len(errs2) == 1 and "stale" in errs2[0], errs2


def test_a_non_numeric_snapshot_is_unjudged_rather_than_crashed_on():
    errs, unjudged, stats = _run(_snapshot("ceil(module / 7.5)", "sixteen"))
    assert errs == [] and stats["baked_unjudged"] == 1
    assert "not a number" in unjudged[0], unjudged


def test_a_parameter_with_no_stored_value_is_not_counted_at_all():
    """An `expr` with no `computed_at.value` is not a snapshot — there is nothing cached to go
    stale. It must not inflate either counter, or the 143 stops meaning what it says."""
    kit = {"slots": {"s": {"parameters": {"p": {
        "expr": "ceil(module / 7.5)", "unit": "count", "kind": "derived",
        "source": "storey-graduation"}}}}}
    errs, unjudged, stats = _run(kit)
    assert errs == [] and unjudged == []
    assert stats["baked_judged"] == 0 and stats["baked_unjudged"] == 0
