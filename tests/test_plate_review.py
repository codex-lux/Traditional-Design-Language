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
