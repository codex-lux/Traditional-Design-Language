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
    """Drive the shipped function and return (errors, unjudged reasons, counters).

    `flag_unjudged` is the SECOND list the function fills (WP-12.9) -- the snapshots whose
    source rule could not be found at all, which are a different population from the ones whose
    VALUE could not be re-derived. It is dropped here because these tests are about the value;
    `_run_flags` below is its reader."""
    import collections
    ck = _ck()
    errs, unjudged, flag_unjudged, stats = [], [], [], collections.Counter()
    ck.check_baked_snapshots(errs, unjudged, flag_unjudged, nid, kit, stats)
    return errs, unjudged, stats


def _run_flags(kit, nid="probe"):
    """The same drive, returning the FLAG question's own errors and unjudged list."""
    import collections
    ck = _ck()
    errs, unjudged, flag_unjudged, stats = [], [], [], collections.Counter()
    ck.check_baked_snapshots(errs, unjudged, flag_unjudged, nid, kit, stats)
    return errs, flag_unjudged, stats


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
    errs, unjudged, flag_unjudged, stats = [], [], [], collections.Counter()
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        kit = json.load(open(p, encoding="utf-8"))
        ck.check_baked_snapshots(errs, unjudged, flag_unjudged,
                                 os.path.basename(p).split(".")[0], kit, stats)
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


# ------------------------------------------------------------------ run modes

def test_a_corpus_wide_bound_is_not_judged_on_a_single_kit_run():
    """SHIPPED BROKEN IN WP-8.8 AND FOUND BY A TEST ABOUT SOMETHING ELSE. The two bounds are
    corpus-wide claims — 135 judged, 8 unjudged — and they were asserted unconditionally, so
    `check_kits.py <one-style>` saw ~10 snapshots against a floor of 135 and errored on every
    node in the corpus. The floor was working correctly on a question nobody had asked it.

    It did not show on `check_kits.py` with no argument, which is how the package verified. It
    showed on `test_kit_cascade.py`'s dangling-replace test, whose CLEANUP re-runs one kit and
    asserts the corpus is clean again — a test about `replace` ops, on the full suite, after the
    targeted suites were green. Same shape as the unsorted glob WP-8.7 shipped."""
    import subprocess
    one = subprocess.run([sys.executable, "build/check_kits.py", "tidewater-georgian"],
                         cwd=ROOT, capture_output=True, text=True)
    assert one.returncode == 0, one.stdout[-800:]
    assert "ERROR" not in one.stdout.upper(), one.stdout[-800:]
    assert "corpus-wide" in one.stdout, (
        "a single-kit run must SAY the bounds were not judged, not silently skip them — "
        "unjudged is not passed")
    whole = subprocess.run([sys.executable, "build/check_kits.py"],
                           cwd=ROOT, capture_output=True, text=True)
    assert whole.returncode == 0, whole.stdout[-800:]
    assert "135 re-derived" in whole.stdout, (
        "the corpus run must still judge them, or scoping the bound turned it off")
    assert "corpus-wide" not in whole.stdout, whole.stdout[-400:]


# ------------------------------------------- the FLAGS, which are a second question (WP-12.9)
def _flagkit(judgment, expr="ceil(module / 7.5)", slot="stair_type",
             pname="risers_per_storey", source="storey-graduation", value=16.0):
    """A kit whose one snapshot names a REAL pack rule, so the flag question can be asked of it.

    The value question and the flag question are asked of the same parameter and answered
    separately; this fixture is built so the value half is quiet and only the flag half speaks.
    """
    par = {"expr": expr, "unit": "count", "kind": "derived", "source": source,
           "computed_at": {"ceiling_height_in": 108.0, "storey_height_in": 120.0,
                           "opening_width_in": 36.0, "value": value}}
    if judgment is not None:
        par["judgment"] = judgment
    return {"slots": {slot: {"parameters": {pname: par}}}}


def _rule_for(source, slot, expr):
    """The source rule this fixture's snapshot claims to be a snapshot OF -- read, so the test
    is about the corpus's real rule rather than about a rule this file made up."""
    ck = _ck()
    pk = ck.pe.resolve(source)
    return next((r for r in pk.get("derived_rules", [])
                 if r.get("target_slot") == slot and r.get("expression") == expr), None)


def test_a_snapshot_that_drops_its_source_rules_judgment_is_an_error():
    """THE DEFECT THIS CHECK EXISTS FOR, DRIVEN. Measured over the 93 snapshots that can be
    matched to a source rule at all, THIRTEEN carried a rule flagged `judgment: true` and ZERO
    of them carried the flag -- the bake has never carried it, and `check_baked_snapshots` was
    green over every one because it re-derives the VALUE and compares nothing else.

    A judgment laundered as a derived figure is the thing this corpus names as the worst that
    can be done to it, arriving through a FIELD rather than through a number: `brick-course`
    says 22 in "is between sizes; the mason will build 18 or 27", and the snapshot of that said
    `kind: derived` and nothing else, so `build/threshold.py` read a settled measurement out of
    a deferred decision and the plan sheet published it as one.
    """
    slot, pname, expr, src = "chimney", "stack_plan_in", "part * 8", "brick-course"
    rule = _rule_for(src, slot, expr)
    assert rule is not None and rule.get("judgment") is True, (
        "this test's premise is that the corpus really flags this rule a judgment; it does not, "
        "so the test would pass for the wrong reason")

    errs, _unj, stats = _run_flags(_flagkit(None, expr, slot, pname, src, 22.0))
    assert stats["baked_flag_judged"] == 1, stats
    assert len(errs) == 1, errs
    assert "judgment: true" in errs[0] and pname in errs[0], errs[0]

    errs, _unj, stats = _run_flags(_flagkit(True, expr, slot, pname, src, 22.0))
    assert errs == [], errs
    assert stats["baked_flag_judged"] == 1, stats


def test_a_judgment_claimed_where_the_corpus_settled_the_figure_is_also_an_error():
    """The OTHER direction, and it is not symmetry for its own sake. A flag added where the rule
    carries none is the fake-unjudged collapse -- the corpus saying "somebody still owes this"
    about a figure it has in fact settled -- which this project treats as exactly as dishonest
    as a fake pass. Without this half the check could be satisfied by flagging everything."""
    slot, pname, expr, src = "stair_type", "risers_per_storey", "ceil(module / 7.5)", "storey-graduation"
    rule = _rule_for(src, slot, expr)
    assert rule is not None and not rule.get("judgment"), (
        "premise: this rule is NOT a judgment. If the corpus flags it, this test is vacuous.")

    errs, _unj, _stats = _run_flags(_flagkit(True, expr, slot, pname, src))
    assert len(errs) == 1, errs
    assert "fake-unjudged" in errs[0] or "as dishonest" in errs[0], errs[0]

    errs, _unj, _stats = _run_flags(_flagkit(None, expr, slot, pname, src))
    assert errs == [], errs


def test_a_snapshot_whose_rule_cannot_be_found_is_UNJUDGED_and_never_an_error():
    """50 of 143 snapshots name a `source` pack that states no rule for their slot with that
    expression -- `english-georgian.door_surround.order_height_ratio` cites `gibbs-ionic`, which
    carries ZERO rules targeting that slot. Loosening the match until those resolve would pair a
    snapshot with a rule that is not its source, which is OQ 48's error one layer up. They are
    counted and printed as could-not-compare: unjudged is not passed, and it is not failed."""
    # value 22.0 so `part * 8` re-derives exactly: the VALUE question must stay quiet here, or
    # this test would pass on an error raised by the other half of the function.
    errs, unj, stats = _run_flags(_flagkit(None, expr="part * 8", slot="composition_parti",
                                           pname="invented", source="brick-course", value=22.0))
    assert errs == [], errs
    assert stats["baked_flag_unjudged"] == 1 and stats["baked_flag_judged"] == 0, stats
    assert "states no rule on slot" in unj[0], unj[0]


def test_the_corpus_carries_no_snapshot_that_drops_a_judgment(corpus_flags):
    """The corpus-wide half. It is SECOND deliberately: a green run here says nothing about
    whether the check can fire, which is why the three driven cases above come first."""
    errs, flag_unjudged, stats = corpus_flags
    assert errs == [], errs
    assert stats["baked_flag_judged"] > 80, (
        f"only {stats['baked_flag_judged']} snapshots were matched to a source rule -- this "
        f"number falls when the matcher goes blind, not only when the corpus shrinks")


@pytest.fixture(scope="module")
def corpus_flags():
    import collections
    import glob
    import json
    ck = _ck()
    errs, unjudged, flag_unjudged, stats = [], [], [], collections.Counter()
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        kit = json.load(open(p, encoding="utf-8"))
        ck.check_baked_snapshots(errs, unjudged, flag_unjudged,
                                 os.path.basename(p).split(".")[0], kit, stats)
    # only the FLAG errors: a stale value is the other question and has its own test
    return [e for e in errs if "judgment" in e], flag_unjudged, stats
