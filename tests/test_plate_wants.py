"""The plates wanted list is generated from the packs and says only what the packs say (WP-14.5).

`Plan Examples/Plates/WANTED.md` is the source leg's other half: the figures a plate would
settle, for a person to fetch, because every host the packs cite refuses a CONNECT from here.
These tests hold the file to its generator and the generator to the five rules its docstring
states -- the row belongs to the pack that states the assembly, a summary entablature is not a
gap, "apportioned" is the transcribers' own word, a disputed figure is one census N1 pins, and
nothing claims a host was reached.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

GW = modcache.load("gen_plate_wants", os.path.join(ROOT, "build", "gen_plate_wants.py"))
PE = GW.PE


def test_the_committed_list_is_current():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "build", "gen_plate_wants.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_every_row_is_listed_under_the_pack_that_states_its_assembly():
    rows = GW.rows()
    assert rows, "premise: the packs have gaps to list"
    for r in rows:
        assert PE.assembly_owner(r["pack"], r["assembly"]) == r["pack"], r
    keys = [(r["cls"], r["pack"], r["assembly"], r.get("member")) for r in rows]
    assert len(keys) == len(set(keys)), "a wanted figure is listed twice"


def test_a_summary_entablature_is_not_a_gap_and_its_detail_would_be():
    """palladio-ionic states its entablature's division and inherits nothing it divides with a
    projection of its own -- the premise that makes the rule bite."""
    raw = PE.PACKS["palladio-ionic"]["assemblies"]["entablature"]
    assert all(m.get("projection_parts") is None for m in raw["members"]), "premise"
    assert {m["id"] for m in raw["members"]} == {"architrave", "frieze", "cornice"}
    one = {(r["pack"], r["assembly"]) for r in GW.rows() if r["cls"] == 1}
    assert ("palladio-ionic", "entablature") not in one
    assert ("palladio-ionic", "cornice") in one, "the detailed assembly is the gap"


def test_apportioned_is_the_transcribers_word_and_every_use_of_it_is_listed():
    stated = [m for pid in GW._order_packs()
              for a in (PE.PACKS[pid].get("assemblies") or {}).values()
              for m in a.get("members", [])]
    said = [m for m in stated if "apportion" in (m.get("note") or "").lower()]
    three = [r for r in GW.rows() if r["cls"] == 3]
    assert len(three) == len(said) and len(said) > 0
    assert all("apportion" in r["note"].lower() for r in three)


def test_a_low_confidence_member_is_listed_once():
    rows = GW.rows()
    listed = {(r["pack"], r["assembly"], r.get("member")) for r in rows if r["cls"] in (2, 3)}
    for r in rows:
        if r["cls"] == 4:
            assert (r["pack"], r["assembly"], r["member"]) not in listed, r


def test_the_list_claims_no_host_was_reached():
    text = GW.render()
    assert "Nothing here was verified reachable" in text
    assert GW.PROBED_ON in text
    for h in GW.PROBED:
        assert "`%s`" % h in text


def test_the_first_clause_marks_what_it_cuts():
    assert GW._first_clause("Apportioned.") == "Apportioned"
    assert GW._first_clause("Apportioned. The plate is lost.") == "Apportioned …"
    long = "word " * 60
    out = GW._first_clause(long)
    assert out.endswith(" …") and len(out) < 170 and not out[:-2].endswith("wor")


def _disputed():
    return [r for r in GW.rows() if r["cls"] == 0]


def test_class_0_is_what_census_n1_pins_and_nothing_else():
    """Joined through the NOTE, which is census N1's subject: every pinned N1 disagreement states
    some disputed figure, and every disputed figure is stated by a pinned N1 disagreement. A row
    dropped or a row invented fails here, and so does a figure the note and record agree on."""
    pin = json.load(open(os.path.join(ROOT, "tests", "fixtures", "ink_known_disagreements.json"),
                         encoding="utf-8"))["disagreements"]
    pinned = {k.split(":", 1)[1] for k in pin if k.startswith("N1:")}
    zero = _disputed()
    assert pinned and zero, "premise: census N1 pins disagreements, and the list carries them"
    assert {n["in"] for r in zero for n in r["notes"]} == pinned
    for r in zero:
        for n in r["notes"]:
            assert not GW.PR.agrees(n["value"], r["record"]), (r, n)


def test_one_figure_is_one_row_however_many_notes_state_it():
    """Benjamin's Doric states its annulet's projection twice, under the necking and under the
    abacus: one figure, one page to read. Vignola's Doric base note states two figures: two rows."""
    ben = [r for r in _disputed() if r["pack"] == "benjamin-doric"]
    assert len(ben) == 1 and len(ben[0]["notes"]) == 2, ben
    vd = [r for r in _disputed() if (r["pack"], r["assembly"]) == ("vignola-doric", "base")]
    assert len(vd) == 2 and len({n["in"] for r in vd for n in r["notes"]}) == 1, vd


def test_a_note_about_another_packs_record_is_listed_under_that_pack():
    """palladio-corinthian's base note states what Palladio gives the Doric base; the figure is
    palladio-doric's, and so is the book that settles it."""
    rows = [r for r in _disputed() if any(n["in"].startswith("palladio-corinthian/") for n in r["notes"])]
    assert rows and all(r["pack"] == "palladio-doric" for r in rows), rows
