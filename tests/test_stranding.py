"""What OQ 51's flip takes away, counted before and after.

Lucas re-ruled OQ 51 on 3 Sep 2026 — pack inheritance becomes opt-in, staged pack by pack — and
the ruling requires the flip to strand LOUDLY, because a node that stops receiving a pack it was
silently receiving loses dimensions on real slots, and a slot reading UNDIMENSIONED rather than
REFUSED is OQ 51's own silent corruption arriving from the other direction.

`check_inheritance.py --stranding` is that count. This file holds it to three things the checker's
own pinned equalities cannot.

**THE HEADLINE CANNOT SEE THE DEFECT.** Deleting the "still governed by the dropped pack" branch
leaves `dimensioned_before` and `dimensioned_after` byte-identical at 7,830 -> 4,931 and moves 179
slots from `unreached` into `stranded`. Only the BUCKET SPLIT shows it. So the buckets are pinned
here, not the totals.

**AND THE DIRECTION OF THAT LIE IS MEASURED, NOT ASSUMED.** The same omission in `--impact` read as
RELIEF — it printed the empty post-drop source as a source and counted the slot re-housed. Here it
reads as COST, 2,899 -> 3,078. One omission, two instruments, opposite lies. A test written from
the expectation rather than from the run would have pinned the wrong direction.

**A SWEEP THAT FINDS NOTHING SATISFIES EVERY BOUND.** `sweep_gates.py` shipped reading the wrong
key and printed "off" for all 128 styles including the 43 already endorsed. So the meter is held to
being able to MOVE: a node known to lose slots must report them, and a pack known to be clean must
report zero.
"""
import collections
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402


def _ci():
    return modcache.load("check_inheritance", os.path.join(ROOT, "build", "check_inheritance.py"))


def _run(*args):
    out = subprocess.run([sys.executable, "build/check_inheritance.py", "--stranding", *args],
                         cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, (out.returncode, out.stdout, out.stderr)
    return out.stdout


def _nums(text):
    """The five reported figures, off the rendered report rather than a second computation."""
    import re
    g = {}
    for key, pat in (
            ("before",    r"slots dimensioned\s+(\d+) ->"),
            ("after",     r"slots dimensioned\s+\d+ ->\s+(\d+)"),
            ("stranded",  r"STRANDED — lose all dimensioning\s+(\d+)"),
            ("rehoused",  r"re-housed on another pack\s+(\d+)"),
            ("unreached", r"still governed by the dropped pack\s+(\d+)"),
            ("nodes",     r"nodes with at least one slot stranded\s+(\d+) of (\d+)")):
        m = re.search(pat, text)
        assert m, (key, text[:400])
        g[key] = int(m.group(1))
        if key == "nodes":
            g["buildable"] = int(m.group(2))
    return g


@pytest.fixture(scope="module")
def corpus():
    return _nums(_run())


# ---------------------------------------------------------------- the measurement

def test_the_corpus_wide_figures_are_the_ones_the_ruling_was_not_taken_on(corpus):
    """The ruling accepted "the unjudged gaps stranded in one commit", recorded as ~223. A role
    gap is not a delivery: 2,963 of 3,158 arrivals stop, and they dimension 2,899 slots across
    124 of 132 nodes. That factor of thirteen is why the flip was staged rather than landed."""
    # RE-PINNED BY THE FIRST FLIP (WP-8.10) AND THE SHAPE OF THE MOVE IS THE LESSON.
    # `trim-classical` is flipped, so its 10 slots are ALREADY undimensioned: the BASELINE
    # shrank, 7830 -> 7820, and `stranded` fell with it. `after` does not move at all -- the end
    # state was always going to be this corpus, whichever order the packs flip in. A ceiling
    # would have read three of these four as improvement.
    assert corpus["before"] == 7820, corpus
    assert corpus["after"] == 4931, corpus
    assert corpus["before"] - corpus["after"] == corpus["stranded"] == 2889, corpus
    assert corpus["nodes"] == 124 and corpus["buildable"] == 132, corpus


def test_the_buckets_are_pinned_because_the_headline_cannot_see_them(corpus):
    """Deleting the `unreached` branch leaves `before`/`after` IDENTICAL and moves 179 slots into
    `stranded`. Every assertion in the test above still passes on that mutation except the
    stranded one, and it passes only because `before - after` is checked against it — which is an
    accident of arithmetic, not a guard. These three are the guard."""
    assert corpus["stranded"] == 2889, corpus
    assert corpus["rehoused"] == 1980, corpus
    assert corpus["unreached"] == 111, corpus


def test_the_flip_does_not_reach_111_slots_and_that_is_a_finding_not_a_rounding(corpus):
    """179 slots stay governed by a pack the flip stopped delivering, because `choose_pack` reads
    the resolved slot record's own `packs` block BEFORE the rows and that block cascades. The
    same condition on the 208 shipped DECLINES is 7 addresses (`tests/test_declined_packs.py`);
    at the scale of the flip it is 179. Whatever ships as `inherits_packs` inherits this hole —
    it is not something the mechanism can close, because the ruling is about delivery and this is
    a slot record naming a pack directly."""
    # 179 -> 111 at the first flip: `trim-classical` carried 119 of the corpus-wide unreached
    # addresses, and once the pack is gated they are no longer part of the counterfactual at all.
    # The condition did not go away, the pack did.
    assert corpus["unreached"] == 111
    assert corpus["unreached"] > 20, (
        "if this collapses toward the decline-scale figure the sweep has probably stopped "
        "detecting the condition rather than the corpus having been cleaned")


# ---------------------------------------------------------------- staging

def test_a_single_pack_can_be_measured_because_that_is_how_the_flip_is_staged():
    """Lucas ruled the flip staged pack by pack, so the meter has to answer one pack at a time.
    `facade-gable` is the clean case: 32 slots stranded, nothing re-housed, nothing surviving."""
    g = _nums(_run("facade-gable"))
    assert g["before"] == 7820, g          # the denominator stays the corpus
    assert g["stranded"] == 32, g
    assert g["unreached"] == 0, g
    assert g["nodes"] == 29, g


def test_the_per_pack_numbers_say_which_flips_would_actually_do_anything():
    """THE MOST USEFUL THING THE METER PRODUCES, and it is not the headline. `storey-graduation`
    strands 9 slots and leaves 45 governed by inherited `slot.packs` rulings the flip cannot
    reach — five times more addresses survive it than it moves. `facade-gable` strands 32 and
    leaves none. A staging order taken off the backlog counts alone (`storey-graduation` 23 gaps
    against `facade-gable` 16) would pick the ineffective one first."""
    grad = _nums(_run("storey-graduation"))
    gable = _nums(_run("facade-gable"))
    assert grad["stranded"] == 9, grad
    assert grad["unreached"] == 45, grad
    assert grad["unreached"] > grad["stranded"] * 3, (grad, "the finding has gone")
    assert gable["unreached"] == 0 and gable["stranded"] > grad["stranded"], (gable, grad)


# ---------------------------------------------------------------- the instrument can move

def test_the_meter_reports_loss_on_a_node_known_to_lose(corpus):
    """`sweep_gates.py` shipped unable to move — wrong key, "off" for all 128 styles including
    the 43 endorsed — so a zero from a fresh instrument is worth nothing until it has been shown
    to report a non-zero. `ranch-style` loses 44 slots and `egyptian-revival` 64."""
    text = _run()
    assert "ranch-style" in text and "egyptian-revival" in text, text
    import re
    worst = dict((m.group(1), int(m.group(2)))
                 for m in re.finditer(r"^    ([a-z0-9-]+)\s+(\d+)$", text, re.M))
    # 64 -> 63: `egyptian-revival` is one of the ten the first flip already stranded, so it has
    # one fewer slot left for the counterfactual to take.
    assert worst.get("egyptian-revival") == 63, worst
    assert worst.get("ranch-style") == 44, worst


def test_a_pack_that_reaches_nobody_unvouched_reports_zero_rather_than_erroring():
    """The other half of being able to move: a clean answer must be reachable too, or every zero
    is ambiguous between "nothing to report" and "the sweep broke"."""
    g = _nums(_run("no-such-pack-id"))
    assert g["stranded"] == 0 and g["rehoused"] == 0 and g["unreached"] == 0, g
    assert g["before"] == g["after"] == 7820, g


def test_the_sweep_refuses_rather_than_printing_a_satisfying_zero():
    """A sweep that finds no dimensioned slot at all and a corpus with none print the same
    number. `--forbidden` carries this guard; so does this. Driven by handing the checker an
    empty node set rather than by reading the source."""
    ci = _ci()
    src = open(os.path.join(ROOT, "build", "check_inheritance.py"), encoding="utf-8").read()
    assert "COULD NOT EVALUATE — the sweep ran over" in src
    assert "sys.exit(COULD_NOT_EVALUATE)" in src
    assert ci.COULD_NOT_EVALUATE == 3, ci.COULD_NOT_EVALUATE


def test_the_pinned_counts_are_equalities_and_say_why(corpus):
    """`STRANDING` is not a ratchet, deliberately. A ceiling that may only fall is satisfied by
    measuring less, and every one of these numbers falls as the flip lands — which is the flip
    working, not the corpus improving. Held to the shipped dict so the two cannot drift."""
    ci = _ci()
    assert ci.STRANDING == {"stranded": 2889, "rehoused": 1980, "nodes_touched": 124,
                            "dimensioned_before": 7820, "dimensioned_after": 4931}, ci.STRANDING
    for k in ("stranded", "rehoused"):
        assert corpus[k] == ci.STRANDING[k], (k, corpus, ci.STRANDING)
    assert corpus["nodes"] == ci.STRANDING["nodes_touched"]


def test_governed_still_takes_a_single_pack_because_impact_passes_one():
    """`drop` was generalised from an id to a set for this sweep. `--impact` passes one id and
    `tests/test_declined_packs.py` sweeps every shipped decline through the same argument, so the
    string form has to keep working — a set of characters is not a set of pack ids."""
    ci = _ci()
    g = ci.load()
    before, _k = ci.governed(g, "egyptian-revival")
    one, _k = ci.governed(g, "egyptian-revival", drop="gibbs-ionic")
    many, _k = ci.governed(g, "egyptian-revival", drop={"gibbs-ionic"})
    assert one == many, "the string and the one-element set must mean the same thing"
    assert len(one) <= len(before)
