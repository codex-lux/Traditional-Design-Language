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
    assert corpus["before"] == 7516, corpus
    assert corpus["after"] == 4931, corpus
    assert corpus["before"] - corpus["after"] == corpus["stranded"] == 2585, corpus
    assert corpus["nodes"] == 124 and corpus["buildable"] == 132, corpus


def test_the_buckets_are_pinned_because_the_headline_cannot_see_them(corpus):
    """Deleting the `unreached` branch leaves `before`/`after` IDENTICAL and moves 179 slots into
    `stranded`. Every assertion in the test above still passes on that mutation except the
    stranded one, and it passes only because `before - after` is checked against it — which is an
    accident of arithmetic, not a guard. These three are the guard."""
    assert corpus["stranded"] == 2585, corpus
    assert corpus["rehoused"] == 1895, corpus     # 1980 for three packages; the five moved it at last
    assert corpus["unreached"] == 47, corpus      # the five took 49 more out of the counterfactual


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
    assert corpus["unreached"] == 47
    assert corpus["unreached"] > 20, (
        "if this collapses toward the decline-scale figure the sweep has probably stopped "
        "detecting the condition rather than the corpus having been cleaned")


# ---------------------------------------------------------------- staging

def test_a_single_pack_can_be_measured_because_that_is_how_the_flip_is_staged():
    """The flip was staged pack by pack, so the meter has to answer one pack at a time.

    That staging was Lucas's 3 Sep ruling and it was SUPERSEDED on 4 Sep, when he ruled the last
    five packs flipped together -- the per-pack question outlived the per-pack schedule, which is
    why this test does.

    THE CASE HAS MOVED THREE TIMES AND THE THIRD MOVE RETIRES THE RULE THAT CAUSED THE FIRST
    TWO. WP-8.11 moved it from `facade-gable` to `sash-light` because gable had been flipped and
    a flipped pack's counterfactual is zero. WP-8.12 flipped `sash-light` and moved it to
    `opening-proportion` under the rule "name a pack scheduled LAST". WP-8.13 flipped all five
    remaining packs at once, so "scheduled last" named a pack that was about to be flipped for
    the third time running.

    **THE RULE IS NOT "SCHEDULED LAST", IT IS "NOT SCHEDULED AT ALL", AND IT ONLY BECAME
    STATEABLE WHEN THE SCHEDULE EMPTIED.** The flip programme covered eight packs —
    `trim-classical`, `facade-gable`, `sash-light`, then the five live-gate packs — and it is
    finished. The other 49 packs on disk are on `cascade` because nothing plans to move them,
    which is what a driven counterfactual needs and what "last in a queue" only ever approximated.

    `timber-panel` is the case now: outside the programme, and the largest counterfactual the
    corpus still offers at 129 slots over 91 nodes."""
    g = _nums(_run("timber-panel"))
    assert g["before"] == 7516, g          # the denominator stays the corpus
    assert g["stranded"] == 131, g         # 129 before the five flipped and stopped competing
    assert g["rehoused"] == 39, g
    assert g["unreached"] == 0, g
    assert g["nodes"] == 91, g


def test_the_per_pack_numbers_say_which_flips_would_actually_do_anything():
    """THE MOST USEFUL THING THE METER PRODUCES, and it is not the headline. The pair moved to
    two packs OUTSIDE the flip programme when WP-8.13 flipped the last five, and the new pair
    states the finding more sharply than the old one did.

    `brick-course` strands **one slot** and leaves 66 addresses governed by inherited
    `slot.packs` rulings the flip cannot reach — 66 survivors against 1 casualty.
    `timber-panel` strands 131 over 91 nodes. Their backlog counts after the five-pack flip are
    15 gaps and 9 — adjacent, and in the WRONG order if a reader took them as a guide to what a
    flip is worth.

    `brick-course` measured 0 and 68 before WP-8.13 flipped the five, and 1 is the better pin:
    a zero is what this finding looks like AND what a broken instrument prints. `timber-panel`
    is asserted in the same test as the positive control proving the sweep can move at all —
    the discipline `sweep_gates.py` earned by shipping unable to."""
    quiet = _nums(_run("brick-course"))
    wide = _nums(_run("timber-panel"))
    assert quiet["stranded"] == 1, quiet     # 0 before the five flipped; 1 is the stronger pin
    assert quiet["unreached"] == 66, quiet
    assert quiet["unreached"] > 60, (quiet, "the finding has gone")
    assert wide["stranded"] == 131, (wide, "the positive control has stopped moving")
    assert wide["unreached"] < wide["stranded"], (wide, "the contrast has gone")
    assert quiet["unreached"] > quiet["stranded"] * 50, (quiet, "the contrast has gone")


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
    # 64 -> 63 -> 62 across the two flips: each one already stranded a slot this counterfactual
    # can no longer take.
    assert worst.get("egyptian-revival") == 57, worst
    assert worst.get("ranch-style") == 41, worst   # 44 -> 42 -> 41 across the four flips


def test_a_pack_that_reaches_nobody_unvouched_reports_zero_rather_than_erroring():
    """The other half of being able to move: a clean answer must be reachable too, or every zero
    is ambiguous between "nothing to report" and "the sweep broke"."""
    g = _nums(_run("no-such-pack-id"))
    assert g["stranded"] == 0 and g["rehoused"] == 0 and g["unreached"] == 0, g
    assert g["before"] == g["after"] == 7516, g


def test_the_sweep_refuses_rather_than_printing_a_satisfying_zero():
    """A sweep that finds no dimensioned slot at all and a corpus with none print the same
    number. `--forbidden` carries this guard; so does this. Driven by handing the checker an
    empty node set rather than by reading the source."""
    ci = _ci()
    src = open(os.path.join(ROOT, "build", "check_inheritance.py"), encoding="utf-8").read()
    assert "COULD NOT EVALUATE — the sweep ran over" in src
    assert "sys.exit(COULD_NOT_EVALUATE)" in src
    assert ci.COULD_NOT_EVALUATE == 3, ci.COULD_NOT_EVALUATE


def test_unreached_is_pinned_where_the_prose_can_be_held_to_it(corpus):
    """THE ONE OQ 51 FIGURE NOBODY POLICED IS THE ONE THAT ROTTED (WP-8.14).

    `check_counts.py` derives six values from the corpus -- role_gaps, inherited_packs,
    unendorsed, endorsed, declined, judged -- and `unreached` was not among them. CLAUDE.md
    carried **111** for three flips after it stopped being true (179 before any flip, 111 after
    `trim-classical`, then 96, then 47) while THIS FILE was re-pinned at every one. A number
    corrected in the test and not in its prose neighbour: WP-9.5's second-commonest shape,
    occurring inside the register entry that documents that shape.

    The chain is prose -> `STRANDING["unreached"]` -> corpus. `check_counts.py` reads the
    constant (deliberately, rather than re-running a 6.5 s sweep on every build) and
    `check_inheritance.py --stranding --strict` holds the constant to the corpus, failing on
    drift because its check is generic over `STRANDING.items()` -- which is why adding the key
    was the whole of the fix.

    This test is the third link: it asserts the key is IN the dict, so a future flip cannot
    re-pin `unreached` by deleting it from the pinned set and leaving the prose unguarded."""
    ci = _ci()
    assert "unreached" in ci.STRANDING, (
        "`unreached` left STRANDING -- `check_counts.py` reads it from there to hold CLAUDE.md's "
        "figure, so removing it silently unguards the one number that has already rotted once")
    assert ci.STRANDING["unreached"] == corpus["unreached"] == 47, (
        ci.STRANDING.get("unreached"), corpus["unreached"])


def test_the_pinned_counts_are_equalities_and_say_why(corpus):
    """`STRANDING` is not a ratchet, deliberately. A ceiling that may only fall is satisfied by
    measuring less, and every one of these numbers falls as the flip lands — which is the flip
    working, not the corpus improving. Held to the shipped dict so the two cannot drift."""
    ci = _ci()
    assert ci.STRANDING == {"stranded": 2585, "rehoused": 1895, "nodes_touched": 124,
                            "dimensioned_before": 7516, "dimensioned_after": 4931,
                            # joined in WP-8.14 -- see the test above for why
                            "unreached": 47}, ci.STRANDING
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
