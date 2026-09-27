"""The internal half of a plate's review judges the record against its own notes (WP-14.5).

Every branch is DRIVEN with a planted table, because the corpus reaches most of them only when
something has gone wrong: a quote that has left its note, a claim whose figure differs, a note
nobody read, a conversion stated wrongly. A guard that runs only where the bug cannot occur is not
a guard.
"""
import copy
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

PR = modcache.load("plate_review", os.path.join(ROOT, "build", "plate_review.py"))
PE = PR.PE


@pytest.fixture
def planted():
    """Hand the reviewer a copy of the real table to edit, and forget it afterwards."""
    PR.reset()
    t = copy.deepcopy(PR.table())
    PR._TABLE = t
    PR._MEMO.clear()
    yield t
    PR.reset()


def _entry(t, pack, asm, mid):
    for e in t["members"]:
        if (e["pack"], e["assembly"], e["member"]) == (pack, asm, mid):
            return e
    e = {"pack": pack, "assembly": asm, "member": mid, "claims": []}
    t["members"].append(e)
    return e


def _verdict(pack, asm, mid):
    return next(e for e in PR.member_entries()
                if (e["pack"], e["assembly"], e["member"]) == (pack, asm, mid))


# The palladio-ionic architrave is the worked example: Ware's own words divide it 1 : 4 and the
# four into 3 : 4 : 5, and the record carries 7.2, 9.6 and 12 of 36.
QUOTE = "three of which are given to the first fascia and its astragal"


def test_premise_the_worked_example_is_a_numeric_note():
    assert ("palladio-ionic", "architrave", "arch_fascia_1") in PR.numeric_member_notes()
    assert QUOTE in PR._member("palladio-ionic", "architrave", "arch_fascia_1")["note"]


def test_a_claim_that_matches_the_record_agrees(planted):
    e = _entry(planted, "palladio-ionic", "architrave", "arch_fascia_1")
    e["claims"] = [{"quote": QUOTE, "target": "h_arch_fascia_1", "states": "asm_parts * 4/5 * 3/12"}]
    assert _verdict("palladio-ionic", "architrave", "arch_fascia_1")["verdict"] == "agrees"


def test_a_claim_that_does_not_match_disagrees_with_both_figures(planted):
    e = _entry(planted, "palladio-ionic", "architrave", "arch_fascia_1")
    e["claims"] = [{"quote": QUOTE, "target": "h_arch_fascia_1", "states": "asm_parts * 4/5 * 4/12"}]
    v = _verdict("palladio-ionic", "architrave", "arch_fascia_1")
    assert v["verdict"] == "disagrees"
    c = v["claims"][0]
    assert abs(c["record"] - 7.2) < 1e-9 and abs(c["note"] - 9.6) < 1e-9


def test_a_quote_that_has_left_its_note_is_stale_and_never_judged(planted):
    e = _entry(planted, "palladio-ionic", "architrave", "arch_fascia_1")
    e["claims"] = [{"quote": "a sentence nobody wrote", "target": "h_arch_fascia_1", "states": "7.2"}]
    v = _verdict("palladio-ionic", "architrave", "arch_fascia_1")
    assert v["verdict"] == "stale" and v["claims"] == []


def test_a_name_the_record_no_longer_has_is_stale(planted):
    e = _entry(planted, "palladio-ionic", "architrave", "arch_fascia_1")
    e["claims"] = [{"quote": QUOTE, "target": "h_no_such_member", "states": "7.2"}]
    assert _verdict("palladio-ionic", "architrave", "arch_fascia_1")["verdict"] == "stale"


def test_a_numeric_note_with_no_entry_is_not_read_and_never_agrees(planted):
    planted["members"] = [e for e in planted["members"]
                          if (e["pack"], e["assembly"], e["member"]) != ("palladio-ionic", "architrave", "arch_fascia_1")]
    assert _verdict("palladio-ionic", "architrave", "arch_fascia_1")["verdict"] == "not-read"


def test_an_entry_with_no_claim_is_its_own_answer_and_needs_a_reason(planted):
    e = _entry(planted, "palladio-ionic", "architrave", "arch_fascia_1")
    e["claims"], e["why"] = [], "driven"
    v = _verdict("palladio-ionic", "architrave", "arch_fascia_1")
    assert v["verdict"] == "no-claim" and v["why"] == "driven"


def test_a_wrongly_stated_conversion_disagrees(planted):
    planted["modules"]["chambers-ionic"]["part_factor"] = "2"
    c = next(x for x in PR.conversions() if x["pack"] == "chambers-ionic")
    assert c["verdict"] == "disagrees" and c["off"]


def test_a_conversion_quote_that_has_left_its_note_is_stale(planted):
    planted["modules"]["chambers-ionic"]["quotes"] = ["words the module note never said"]
    c = next(x for x in PR.conversions() if x["pack"] == "chambers-ionic")
    assert c["verdict"] == "stale"


def test_an_overlay_with_no_stated_factor_is_not_read(planted):
    del planted["modules"]["chambers-ionic"]
    c = next(x for x in PR.conversions() if x["pack"] == "chambers-ionic")
    assert c["verdict"] == "not-read"


def test_a_shaft_resized_to_the_overlays_own_column_is_a_derivation_not_a_conversion():
    """benjamin-corinthian's column is 22 modules and its shaft took the difference (WP-14.2):
    reading the body's height as a converted figure would convict a correct engine."""
    sh = PE.resolve("benjamin-corinthian")["assemblies"]["shaft"]
    assert sh.get("_height_from_column"), "premise: the shaft was re-sized to the overlay's column"
    c = next(x for x in PR.conversions() if x["pack"] == "benjamin-corinthian")
    assert c["verdict"] == "agrees", c


def test_the_tolerance_is_the_notes_precision():
    assert PR.agrees(7.2, 7.2) and PR.agrees(7.2, 7.205)
    assert not PR.agrees(7.2, 7.3)
    assert PR.agrees(0.3, 0.305) and not PR.agrees(0.3, 0.32)


def test_a_plate_with_a_disagreeing_figure_disagrees(planted):
    e = _entry(planted, "palladio-ionic", "architrave", "arch_fascia_1")
    e["claims"] = [{"quote": QUOTE, "target": "h_arch_fascia_1", "states": "10"}]
    r = PR.plate_review("palladio-ionic", "architrave")
    assert r["verdict"] == "disagrees"
    assert ("the figures notes state about its record", "disagrees") in [(n, v) for n, v, _d in r["checks"]]


def test_the_review_note_evaluates_no_source_and_approves_nothing():
    note = PR.review_note("palladio-ionic", "base", "12 in", "Palladio 1570", ())
    assert "SOURCE: COULD NOT EVALUATE" in note and "Palladio 1570" in note
    assert "NOT approved" in note
    assert "INTERNAL: " in note


CROSS = "greater than the sixth Palladio gives the Tuscan and Doric bases"


def test_a_claim_about_another_pack_is_judged_over_that_packs_record(planted):
    """palladio-corinthian's base note states what Palladio gives the Tuscan and the Doric base.
    Judged over each target's own record and units: the Tuscan's 10 minutes of a 60-minute
    diameter agrees; the Doric's module is the SEMIdiameter, so a sixth of a diameter is
    2 x 30 / 6 = 10 minutes, against a record of 20."""
    assert CROSS in PR._member("palladio-corinthian", "base", "base_plinth")["note"], "premise"
    e = _entry(planted, "palladio-corinthian", "base", "base_plinth")
    e["claims"] = [
        {"quote": CROSS, "target_pack": "palladio-tuscan", "target_assembly": "base",
         "target": "p_base_plinth", "states": "parts / 6"},
        {"quote": CROSS, "target_pack": "palladio-doric", "target_assembly": "base",
         "target": "p_base_plinth", "states": "2 * parts / 6"},
    ]
    v = _verdict("palladio-corinthian", "base", "base_plinth")
    tus, dor = v["claims"]
    assert tus["agrees"] and tus["record"] == 10 and abs(tus["note"] - 10) < 1e-9
    assert not dor["agrees"] and dor["record"] == 20 and abs(dor["note"] - 10) < 1e-9
    assert v["verdict"] == "disagrees"


FIGURES = "the figures notes state about its record"


def _check(pid, aid):
    return {n: (v, d) for n, v, d in PR.plate_review(pid, aid)["checks"]}[FIGURES]


def test_a_claim_about_another_packs_record_counts_on_that_packs_plate():
    """palladio-corinthian's base note disputes the DORIC base's plinth. Counted where the note
    sat, the Corinthian plate read DISAGREES over a record nobody disputes and the Doric plate,
    which draws the 20 minutes in question, read AGREES."""
    claims = next(e for e in PR.table()["members"]
                  if (e["pack"], e["assembly"], e["member"]) == ("palladio-corinthian", "base", "base_plinth"))["claims"]
    assert any(c.get("target_pack") == "palladio-doric" for c in claims), "premise: the cross claim is read"
    dor, cor = _check("palladio-doric", "base"), _check("palladio-corinthian", "base")
    assert dor[0] == "disagrees" and "p_base_plinth: the record 20, a note 10" in dor[1], dor
    assert cor[0] == "agrees", cor


def test_an_inherited_figure_says_whose_record_and_parts_it_is():
    """benjamin-tuscan's capital plate draws Vignola's abacus, converted. The disputed figure is
    judged over Vignola's record in Vignola's parts, and "the record 5" alone would read as
    Benjamin's."""
    got = _check("benjamin-tuscan", "capital")
    assert got[0] == "disagrees" and "vignola-tuscan/capital p_cap_abacus: the record 5" in got[1], got


def test_a_clipped_quote_says_it_was_clipped():
    assert PR._clip("short") == "short"
    out = PR._clip("word " * 30)
    assert out.endswith(" …") and not out[:-2].endswith("wor") and len(out) <= 62


# ------------------------------------------------------------------ the plate's own branches
# WP-14.6, auditor C. Every test above drives an ENTRY; the plate's verdict is composed from those
# and from two checks no entry reaches -- the members' sum and the pack's invariants -- and the
# three routes by which a plate stops agreeing were asserted by no test. Each is planted here on
# the worked example's plate, whose checks all agree as shipped (asserted first, so a plant that
# changes nothing cannot pass for one that bit).
def _checks(r):
    return {n: v for n, v, _d in r["checks"]}


def test_premise_the_worked_example_plate_agrees_as_shipped():
    r = PR.plate_review("palladio-ionic", "architrave")
    assert r["verdict"] == "agrees" and set(_checks(r).values()) == {"agrees"}, r


def test_an_invariant_that_could_not_be_judged_is_not_counted_as_holding(monkeypatch):
    """`check_invariants` answers True, False or None -- None where the invariant's expression
    could not be evaluated. A plate whose every invariant held but one that could not be judged
    must not say its invariants agree."""
    real = PE.check_invariants(PE.resolve("palladio-ionic"))
    assert real and all(r.get("holds") is True for r in real), "premise: every invariant holds"
    monkeypatch.setattr(PE, "check_invariants", lambda res: [dict(real[0]), dict(real[0], holds=None)])
    r = PR.plate_review("palladio-ionic", "architrave")
    assert _checks(r)["the pack's invariants"] == "could-not-evaluate", r
    # and the headline says so: the plate still AGREES where it was judged, and not in general
    note = PR.review_note("palladio-ionic", "architrave", "12 in", "Palladio 1570", ())
    assert "INTERNAL: AGREES WHERE JUDGED, 1 OF %d CHECKS COULD NOT BE EVALUATED" % len(r["checks"]) in note, note


def test_a_quote_that_has_left_its_note_makes_the_plate_disagree(planted):
    """A stale entry is not merely unread on the entry's own row: the plate that draws its member
    reads DISAGREES and names the member, because a table that no longer describes its note has
    stopped vouching for the figure on the plate."""
    e = _entry(planted, "palladio-ionic", "architrave", "arch_fascia_1")
    e["claims"] = [{"quote": "a sentence this note has never contained", "target": "h_arch_fascia_1",
                    "states": "7.2"}]
    r = PR.plate_review("palladio-ionic", "architrave")
    assert r["verdict"] == "disagrees", r
    detail = dict((n, d) for n, _v, d in r["checks"])["the figures notes state about its record"]
    assert "arch_fascia_1: the table no longer describes the note" in detail, detail


def test_a_member_height_that_breaks_the_assemblys_sum_makes_the_plate_disagree(monkeypatch):
    """The members' sum is the one check the plate makes of the record against itself. Planted by
    handing the reviewer a pack whose first architrave member is one part taller."""
    real = PE.resolve

    def taller(pid, *a, **k):
        res = copy.deepcopy(real(pid, *a, **k))
        if pid == "palladio-ionic":
            res["assemblies"]["architrave"]["members"][0]["height_parts"] += 1
        return res

    monkeypatch.setattr(PE, "resolve", taller)
    r = PR.plate_review("palladio-ionic", "architrave")
    assert _checks(r)["the members sum to the assembly"] == "disagrees", r
    assert r["verdict"] == "disagrees"


def test_an_agreement_with_nothing_unjudged_carries_the_plain_headline():
    note = PR.review_note("palladio-ionic", "architrave", "12 in", "Palladio 1570", ())
    assert "INTERNAL: AGREES -- " in note and "WHERE JUDGED" not in note, note


# THE HEADLINE'S TWO OTHER VERDICTS, EACH BESIDE A CHECK THAT COULD NOT RUN (WP-14.6's second audit,
# W6). `review_note` qualifies an AGREEMENT whose checks include an unjudged one, and the only
# thing keeping that qualifier off a disagreement is `r["verdict"] == "agrees" and` in its guard:
# measured, deleting those words left every test above green, because each drives the qualifier on
# an agreeing plate and none on a plate that disagrees or could judge nothing. Without them a plate
# disagreeing on its figures would carry "INTERNAL: AGREES WHERE JUDGED" in the note filed on it.
# The headline is read as the token between "INTERNAL: " and " -- ", because "DISAGREES" contains
# "AGREES" and a substring test cannot tell the two apart.
def _headline(note):
    import re
    m = re.search(r"INTERNAL: (.*?) -- ", note)
    assert m, note
    return m.group(1)


def test_a_disagreement_beside_an_unjudged_check_is_headed_disagrees(planted, monkeypatch):
    e = _entry(planted, "palladio-ionic", "architrave", "arch_fascia_1")
    e["claims"] = [{"quote": QUOTE, "target": "h_arch_fascia_1", "states": "10"}]
    real = PE.check_invariants(PE.resolve("palladio-ionic"))
    assert real and all(r.get("holds") is True for r in real), "premise: every invariant holds"
    monkeypatch.setattr(PE, "check_invariants", lambda res: [dict(real[0]), dict(real[0], holds=None)])
    r = PR.plate_review("palladio-ionic", "architrave")
    assert r["verdict"] == "disagrees", r
    assert "could-not-evaluate" in _checks(r).values(), "premise: a check beside it could not run"
    note = PR.review_note("palladio-ionic", "architrave", "12 in", "Palladio 1570", ())
    assert _headline(note) == "DISAGREES", note
    assert "WHERE JUDGED" not in note, note


def test_a_plate_whose_every_check_could_not_run_is_headed_could_not_evaluate(planted, monkeypatch):
    """`vignola-doric`'s frieze is the plate whose members' sum is unjudged as shipped (its
    author's members do not sum to it, and a note says why); take away the figures its notes state
    and let no invariant be judged, and nothing is left to agree."""
    for e in planted["members"]:
        if (e["pack"], e["assembly"]) == ("vignola-doric", "frieze"):
            e["claims"], e["why"] = [], "driven"
        e["claims"] = [c for c in e["claims"]
                       if (c.get("target_pack"), c.get("target_assembly")) != ("vignola-doric", "frieze")]
    real = PE.check_invariants(PE.resolve("vignola-doric"))
    assert real, "premise: the pack states invariants"
    monkeypatch.setattr(PE, "check_invariants", lambda res: [dict(x, holds=None) for x in real])
    r = PR.plate_review("vignola-doric", "frieze")
    assert r["verdict"] == "could-not-evaluate", r
    assert set(_checks(r).values()) == {"could-not-evaluate"}, "premise: every check unjudged: %s" % r
    note = PR.review_note("vignola-doric", "frieze", "12 in", "Vignola 1562", ())
    assert _headline(note) == "COULD NOT EVALUATE", note
    assert "AGREES" not in _headline(note), note


# THE POPULATION N2 READS, PINNED PER OVERLAY (WP-14.6, promised by WP-14.5's report). N2 says every
# overlay converts what it inherits by the factor its own module note states, over 968 figures --
# and nothing held the 968: dropping `projection_parts` from the comparison cut it to 541 with all
# eighteen overlays still agreeing and the census unmoved, because an agreement over fewer figures
# is still an agreement. A count that moves is not a failure of the corpus; it is a change to
# account for, in the commit that makes it.
N2_FIGURES = {
    "benjamin-corinthian": 76, "benjamin-ionic": 73, "benjamin-tuscan": 39,
    "chambers-composite": 91, "chambers-corinthian": 84, "chambers-doric": 62,
    "chambers-ionic": 65, "chambers-tuscan": 54,
    "gibbs-composite": 41, "gibbs-corinthian": 37, "gibbs-doric": 42, "gibbs-ionic": 23,
    "gibbs-tuscan": 26,
    "palladio-composite": 84, "palladio-corinthian": 45, "palladio-doric": 55,
    "palladio-ionic": 43, "palladio-tuscan": 28,
}


def test_every_overlay_is_judged_over_the_figures_it_was_judged_over():
    got = {c["pack"]: c.get("figures") for c in PR.conversions()}
    assert got == N2_FIGURES, {k: (N2_FIGURES.get(k), got.get(k)) for k in set(got) | set(N2_FIGURES)
                               if got.get(k) != N2_FIGURES.get(k)}
    assert sum(N2_FIGURES.values()) == 968
