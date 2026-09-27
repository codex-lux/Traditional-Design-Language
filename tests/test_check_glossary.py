"""build/check_glossary.py must be able to FAIL, on each rule, for the rule's own reason (WP-14.1).

The glossary is the one place every definition the workbench shows is written, so a checker that
passed a bad record would put an invented source or an unverified quotation in front of every
reader at once. Every mutation below is made on a TEMPORARY COPY -- nothing here writes inside the
repository -- and the checker is pointed at the copy with `--glossary`.

Three disciplines, each learned the hard way elsewhere in this tree:

* **A control that passes.** Every mutation starts from `control`, a copy of the five seeds plus
  a small synthetic set that exercises the rules the seeds cannot (a completely bound field, a
  declared homonym pair, a sourced record, one citation of each checked kind). `test_the_control_
  passes` holds it green; a mutation that goes red on a fixture already red proves nothing.
* **The mutation landed.** Each one is read back before the checker runs. A mutation that silently
  does not apply looks exactly like a guard that works.
* **The failure is for the stated reason.** Each asserts the rule's own message, not merely a
  nonzero exit -- a record broken two ways would otherwise be convicted by the other rule.

The seeds are copied BY ID rather than the whole directory, so this file does not change meaning
when WP-14.2's batches land: the control is the same set of records on every tree.
"""
import contextlib
import glob
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys

import pytest

pytest.importorskip("jsonschema")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS = ("about-tdl", "judgment-passed", "judgment-failed", "judgment-unjudged",
         "judgment-not-applicable")

# A quotation that is really in VISION.md, for synthetic editorial records.
BASIS = 'VISION.md: "A traditional house is a sentence in a language, and the language can be written down."'


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def CG():
    return _load("check_glossary_under_test", "build/check_glossary.py")


def run(CG, *dirs, extra=()):
    """The checker over these directories, in process. Returns (exit code, printed output)."""
    argv = [a for d in dirs for a in ("--glossary", str(d))] + list(extra)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = CG.main(argv)
    return rc, buf.getvalue()


def write(d, rec, name=None):
    path = os.path.join(str(d), (name or rec["id"]) + ".json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=2, ensure_ascii=False)
    return path


def read(d, rid):
    with open(os.path.join(str(d), rid + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def mutate(d, rid, fn):
    """Apply fn to a record in place, write it back, and PROVE it landed."""
    before = read(d, rid)
    after = json.loads(json.dumps(before))
    fn(after)
    assert after != before, f"the mutation of {rid} changed nothing -- it would prove nothing"
    write(d, after)
    assert read(d, rid) == after, f"the mutation of {rid} did not land on disk"
    return after


def a_bibliography_string():
    """A `sources` string really in the corpus, found WITHOUT the checker's own reader -- building
    the fixture with the function under test would make the sourced rule agree with itself."""
    for path in sorted(glob.glob(os.path.join(ROOT, "faults", "*.json"))):
        src = json.load(open(path, encoding="utf-8")).get("sources") or []
        if src and isinstance(src[0], str):
            return src[0]
    pytest.skip("no fault record carries a sources list -- the sourced fixture has nothing to cite")


def a_brief_id():
    briefs = sorted(glob.glob(os.path.join(ROOT, "briefs", "*.json")))
    assert briefs, "no briefs/ record -- the brief-citation fixture has nothing to name"
    return os.path.basename(briefs[0])[:-5]


def a_fault_id():
    return os.path.basename(sorted(glob.glob(os.path.join(ROOT, "faults", "*.json")))[0])[:-5]


def _editorial(rid, term, family, **kw):
    rec = {"id": rid, "term": term, "family": family,
           "definition": "A word defined for a test, in plain prose and well under the limit.",
           "kind": "editorial", "basis": BASIS}
    rec.update(kw)
    return rec


RANK = ("style.rank", "schema/style-node.schema.json", "/properties/rank")
RANK_VALUES = ("tradition", "family", "style", "variant")


@pytest.fixture
def control(tmp_path):
    """The five seeds, plus: `style.rank` bound completely; one declared homonym pair; one
    sourced record; one record citing a term, a brief, a style and a fault."""
    d = tmp_path / "glossary"
    d.mkdir()
    for rid in SEEDS:
        shutil.copy(os.path.join(ROOT, "glossary", rid + ".json"), d / (rid + ".json"))
    # WP-14.29 gave the four judgment seeds their real `mark`s. Rule 13's tests drive a SYNTHETIC
    # stylesheet declaring only what each test names, so a seed carrying a real mark would be
    # judged against a stylesheet that never declared it and every such test would be red for a
    # reason it is not about. The control starts with no mark; the real marks are held to the real
    # stylesheet by the checker's own run over the corpus, and by workbench/app/src/marks.test.mjs.
    for rid in SEEDS:
        rec = read(d, rid)
        if rec.pop("mark", None) is not None:
            write(d, rec)
            assert "mark" not in read(d, rid), f"the control could not clear {rid}'s mark"
    field, schema, pointer = RANK
    for i, v in enumerate(RANK_VALUES):
        write(d, _editorial(f"rank-{v}", f"rank word {v}", "rank", order=i,
                            binds=[{"field": field, "schema": schema, "pointer": pointer,
                                    "value": v}]))
    write(d, _editorial("test-arris-edge", "arris", "model", sense="the sharp edge of a moulding",
                        confusable_with=["test-arris-rail"]))
    write(d, _editorial("test-arris-rail", "Arris", "model", sense="a rail of triangular section",
                        confusable_with=["test-arris-edge"]))
    write(d, {"id": "test-sourced", "term": "sourced word", "family": "model",
              "definition": "A word whose source the corpus already cites.",
              "kind": "sourced", "sources": [a_bibliography_string()]})
    write(d, _editorial("test-cites", "citing word", "model",
                        see=["term:judgment-unjudged", "brief:" + a_brief_id(),
                             "style:tidewater-georgian", "fault:" + a_fault_id()]))
    return d


def test_the_control_passes(CG, control):
    rc, out = run(CG, control)
    assert rc == 0, out
    # and it exercised what it exists to exercise, rather than passing by checking nothing
    # The denominator is the checker's own table, never a typed count (WP-14.17 added the eighth).
    assert f"bound fields: 1 of {len(CG.FIELDS)} (style.rank)" in out, out
    assert "homonym pairs: 1" in out, out
    assert "sources checked against the bibliography: 1" in out, out
    assert "citations checked: 4" in out, out


def test_the_real_set_passes(CG):
    rc, out = run(CG, os.path.join(ROOT, "glossary"))
    assert rc == 0, out
    rc2, out2 = run(CG)                       # no argument is the repository's own glossary/
    assert rc2 == 0 and out2 == out, "the default directory is not glossary/"


def test_the_real_set_is_what_the_build_runs(CG):
    """Registered where the contract says: directly after check_faults.py, with no arguments."""
    ca = _load("check_all_for_glossary", "build/check_all.py")
    names = list(ca.CHECKS)
    i = names.index(("check_faults.py", []))
    assert names[i + 1] == ("check_glossary.py", []), names[i:i + 3]


# ------------------------------------------------------------------ the twelve named mutations

def test_an_editorial_record_with_sources_fails(CG, control):
    mutate(control, "judgment-passed", lambda r: r.__setitem__("sources", [a_bibliography_string()]))
    rc, out = run(CG, control)
    assert rc == 1
    assert re.search(r"judgment-passed\.json: schema at \(root\)", out), out


def test_a_basis_quote_that_is_not_in_its_file_fails(CG, control):
    fake = "The corpus has never said this sentence about the four judgment states."
    mutate(control, "judgment-failed",
           lambda r: r.__setitem__("basis", 'VISION.md: "' + fake + '"'))
    rc, out = run(CG, control)
    assert rc == 1
    assert "glossary/judgment-failed.json[judgment-failed]: basis quotes" in out, out
    assert "which is not in VISION.md" in out, out


def test_a_basis_whose_only_quote_is_twenty_characters_fails(CG, control):
    q = "Unjudged is not pass"                          # really in VISION.md, and too short
    assert len(q) == 20
    assert q in open(os.path.join(ROOT, "VISION.md"), encoding="utf-8").read()
    mutate(control, "judgment-unjudged", lambda r: r.__setitem__("basis", f'VISION.md: "{q}"'))
    rc, out = run(CG, control)
    assert rc == 1
    assert "judgment-unjudged.json: basis verified no quotation of 25 characters" in out, out


def test_a_source_in_no_bibliography_fails(CG, control):
    mutate(control, "test-sourced",
           lambda r: r.__setitem__("sources", [r["sources"][0] + " (a second edition nobody cites)"]))
    rc, out = run(CG, control)
    assert rc == 1
    assert "test-sourced.json: source" in out and "is in no `sources` list" in out, out


def test_a_bind_to_a_value_not_in_the_enum_fails(CG, control):
    mutate(control, "rank-variant", lambda r: r["binds"][0].__setitem__("value", "subvariant"))
    rc, out = run(CG, control)
    assert rc == 1
    assert "rank-variant.json: binds style.rank = 'subvariant', which is not in its enum" in out, out


def test_a_half_bound_field_fails(CG, control):
    for v in ("style", "variant"):
        os.remove(control / f"rank-{v}.json")
    assert not (control / "rank-style.json").exists()
    rc, out = run(CG, control)
    assert rc == 1
    assert "binds style.rank: 'style' is bound by no record" in out, out
    assert "binds style.rank: 'variant' is bound by no record" in out, out


def test_an_asymmetric_confusable_with_fails(CG, control):
    mutate(control, "test-arris-rail", lambda r: r.__setitem__("confusable_with", []))
    rc, out = run(CG, control)
    assert rc == 1
    assert ("test-arris-edge.json: names test-arris-rail in `confusable_with` and "
            "test-arris-rail does not name it back") in out, out


def test_a_colliding_term_without_a_sense_fails(CG, control):
    mutate(control, "test-arris-rail", lambda r: r.pop("sense"))
    rc, out = run(CG, control)
    assert rc == 1
    assert "test-arris-rail.json: collides with test-arris-edge on 'arris' and states no `sense`" in out, out


def test_a_work_package_number_in_a_definition_fails(CG, control):
    mutate(control, "judgment-passed",
           lambda r: r.__setitem__("definition", r["definition"] + " Built in WP-4."))
    rc, out = run(CG, control)
    assert rc == 1
    assert "judgment-passed.json: definition carries a work-package number ('WP-4')" in out, out


def test_a_digit_in_a_definition_fails(CG, control):
    mutate(control, "judgment-failed",
           lambda r: r.__setitem__("definition", r["definition"] + " It has 3 causes."))
    rc, out = run(CG, control)
    assert rc == 1
    assert "judgment-failed.json: definition carries the numeral '3'" in out, out


def test_a_filename_that_is_not_its_id_fails(CG, control):
    os.rename(control / "judgment-failed.json", control / "judgment-fails.json")
    assert (control / "judgment-fails.json").exists()
    rc, out = run(CG, control)
    assert rc == 1
    assert "judgment-fails.json: filename does not match its id 'judgment-failed'" in out, out


def test_an_empty_directory_fails(CG, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "README.md").write_text("records go here\n")   # a README is not a record
    rc, out = run(CG, empty)
    assert rc == 1
    assert "holds no record -- an empty glossary is an error" in out, out


def test_an_absent_directory_fails(CG, tmp_path):
    rc, out = run(CG, tmp_path / "nowhere")
    assert rc == 1
    assert "no such directory" in out, out


# ------------------------------------------------------------------ the rest of the contract

def test_a_basis_naming_the_generated_index_fails(CG, control):
    mutate(control, "judgment-passed",
           lambda r: r.__setitem__("basis", r["basis"] + " See docs/open-questions.md too."))
    rc, out = run(CG, control)
    assert rc == 1
    assert "basis names docs/open-questions.md, which is GENERATED" in out, out


def test_a_basis_naming_another_definition_fails(CG, control):
    mutate(control, "judgment-passed",
           lambda r: r.__setitem__("basis", r["basis"] + " As glossary/judgment-failed.json says."))
    rc, out = run(CG, control)
    assert rc == 1
    assert "basis names glossary/judgment-failed.json: a definition may not rest on another" in out, out


def test_an_unwalkable_key_path_is_an_error_and_not_an_unjudged_count(CG, control):
    """check_openings counts this as unjudged against a ratchet; the glossary has no backlog."""
    rec = json.load(open(os.path.join(ROOT, "rooms", "kitchen.json"), encoding="utf-8"))
    prose = next(v for v in rec.values() if isinstance(v, str) and len(v) >= 60 and '"' not in v[:60])
    q = prose[:60].strip()
    mutate(control, "judgment-passed",
           lambda r: r.__setitem__("basis", f'rooms/kitchen.json no.such.key: "{q}"'))
    rc, out = run(CG, control)
    assert rc == 1
    assert "a key path this checker cannot walk -- a glossary basis may not cite" in out, out


def test_a_bind_with_the_wrong_order_id_or_pointer_fails(CG, control):
    mutate(control, "rank-family", lambda r: r.__setitem__("order", 3))
    mutate(control, "rank-style", lambda r: r["binds"][0].__setitem__("pointer", "/properties/rankk"))
    rc, out = run(CG, control)
    assert rc == 1
    assert "rank-family.json: binds style.rank = 'family', whose index in the enum is 1; its `order` is 3" in out, out
    assert "rank-style.json: binds style.rank at schema/style-node.schema.json /properties/rankk" in out, out


def test_a_bound_value_under_the_wrong_name_or_twice_fails(CG, control):
    rec = read(control, "rank-tradition")
    rec["id"] = "rank-trad"
    write(control, rec)
    rc, out = run(CG, control)
    assert rc == 1
    assert "rank-trad.json: binds style.rank = 'tradition' and must be named 'rank-tradition'" in out, out
    assert "binds style.rank = 'tradition': bound by 2 records" in out, out


def test_a_bind_to_a_field_outside_the_table_fails_by_the_checkers_own_rule(CG, control):
    """The schema's enum refuses the field too, so a nonzero exit alone would not show the
    checker's rule ran at all -- a code mutation deleting it stayed green until this asserted the
    checker's own message (WP-14.1's mutation run)."""
    mutate(control, "rank-style", lambda r: r["binds"][0].__setitem__("field", "style.period"))
    rc, out = run(CG, control)
    assert rc == 1
    assert "rank-style.json: binds field 'style.period', which is not one of" in out, out


def test_a_bound_record_in_the_wrong_family_fails(CG, control):
    mutate(control, "rank-tradition", lambda r: r.__setitem__("family", "model"))
    rc, out = run(CG, control)
    assert rc == 1
    assert ("rank-tradition.json: binds style.rank and is in family 'model'; a record binding "
            "that field is in family 'rank'") in out, out


def test_a_collision_declared_on_neither_side_fails(CG, control):
    """Distinct from the asymmetric case: with `confusable_with` gone from BOTH records the
    symmetry rule has nothing to compare, and only the collision rule can see it."""
    for rid in ("test-arris-edge", "test-arris-rail"):
        mutate(control, rid, lambda r: r.pop("confusable_with"))
    rc, out = run(CG, control)
    assert rc == 1
    assert ("test-arris-edge.json: collides with test-arris-rail on 'arris' and does not name it "
            "in `confusable_with`") in out, out
    assert ("test-arris-rail.json: collides with test-arris-edge on 'arris' and does not name it "
            "in `confusable_with`") in out, out


def test_a_confusable_with_naming_nothing_or_itself_fails(CG, control):
    mutate(control, "test-sourced", lambda r: r.__setitem__("confusable_with", ["no-such-record"]))
    mutate(control, "test-cites", lambda r: r.__setitem__("confusable_with", ["test-cites"]))
    rc, out = run(CG, control)
    assert rc == 1
    assert "test-sourced.json: `confusable_with` names 'no-such-record', which is not a record" in out, out
    assert "test-cites.json: names itself in `confusable_with`" in out, out


def test_citations_are_held_to_the_grammar(CG, control):
    mutate(control, "test-cites", lambda r: r.__setitem__("see", [
        "term:no-such-term", "brief:no-such-brief", "style:no-such-style",
        "style:tidewater-georgian#no-such-section", "kit:tidewater-georgian#lineage",
        "style:tidewater-georgian#lineage", "not a citation"]))
    rc, out = run(CG, control)
    assert rc == 1
    assert "see 'term:no-such-term' names no record in this glossary" in out, out
    assert "see 'brief:no-such-brief' names no file briefs/no-such-brief.json" in out, out
    assert "see 'style:no-such-style' does not resolve: unknown style id" in out, out
    # THE FRAGMENT RULE IS THE SERVER'S, and this checker defers to it rather than spelling a
    # fourth grammar (PRD phase 14, §A.5 rule 7 and §E.6). Until WP-14.3 the server knew no
    # dossier section, so `style:<id>#lineage` was refused here -- this assertion read "no
    # dossier-section fragment until the server accepts one", which is the "until X lands" shape,
    # and WP-14.3 is X. Re-cut to the property it was always about: a `style:` fragment must be a
    # slot OR a section, a `kit:` fragment a slot only, and neither is decided in this file.
    assert ("see 'style:tidewater-georgian#no-such-section' does not resolve: unknown slot or "
            "section fragment") in out, out
    assert "see 'kit:tidewater-georgian#lineage' does not resolve: unknown slot fragment" in out, out
    assert "'style:tidewater-georgian#lineage'" not in out, out
    assert "see 'not a citation' is not a citation in the grammar" in out, out


def test_hygiene_catches_each_shape(CG, control):
    oq = "OQ " + "4"          # spelled apart so the citation checker does not read this file as citing it
    mutate(control, "test-cites", lambda r: r.update({
        "analogy": "Like a flag, --strict, on the command line.",
        "sense": "the build_section helper",
        "more": "Raised as " + oq + ".",
        "aka": ["⑤ the fifth"]}))
    rc, out = run(CG, control)
    assert rc == 1
    assert "analogy carries a command-line flag" in out, out
    assert "sense carries a snake_case identifier ('build_section')" in out, out
    assert "more carries an open-question number" in out, out
    assert "aka[0] carries the numeral '⑤'" in out, out


def test_lengths_are_counted(CG, control):
    mutate(control, "judgment-passed", lambda r: r.__setitem__(
        "definition", " ".join(["word"] * 46)))
    rc, out = run(CG, control)
    assert rc == 1
    assert "judgment-passed.json: definition is 46 words; the most is 45" in out, out


def test_the_about_record_and_placement_rules(CG, control):
    mutate(control, "about-tdl", lambda r: r.__setitem__("see", ["term:judgment-passed"]))
    mutate(control, "judgment-passed", lambda r: r.__setitem__(
        "readers", [{"who": "Somebody", "line": "A line for somebody."}]))
    mutate(control, "test-cites", lambda r: r.__setitem__("surface", {"what": "A page head."}))
    rc, out = run(CG, control)
    assert rc == 1
    assert "about-tdl.json: carries `see`: about-tdl is served to a signed-out reader" in out, out
    assert "judgment-passed.json: carries `readers`, which only about-tdl may carry" in out, out
    assert "test-cites.json: carries `surface` in family 'model'" in out, out


def test_a_required_record_missing_fails(CG, control):
    os.remove(control / "judgment-not-applicable.json")
    rc, out = run(CG, control)
    assert rc == 1
    assert "the required record judgment-not-applicable.json is missing" in out, out


def test_the_judgment_states_must_be_told_apart(CG, control):
    mutate(control, "judgment-failed", lambda r: r.__setitem__("term", "Passed"))
    rc, out = run(CG, control)
    assert rc == 1
    assert "judgment-failed.json: shares its term 'passed' with another required record" in out, out


def test_prefixed_families_are_named_by_their_prefix(CG, control):
    write(control, _editorial("layer-alphabet", "an alphabet", "model"))
    write(control, _editorial("the-critic", "a critic", "layer"))
    rc, out = run(CG, control)
    assert rc == 1
    assert "layer-alphabet.json: its id begins 'layer-' and it is in family 'model'" in out, out
    assert "the-critic.json: is in family 'layer' and its id does not begin 'layer-'" in out, out


def test_the_new_prefixed_families_are_named_by_their_prefix(CG, control):
    """Glossary schema 0.2.0 (WP-14.17) added three families that head a page's parts, and all three
    join rule 11: a `family-*` id outside family `family` is refused, and so is the reverse."""
    for fam in ("glossary-field", "mark", "family"):
        assert fam in CG.PREFIXED_FAMILIES
    write(control, _editorial("glossary-field-aka", "a label", "model"))
    write(control, _editorial("a-heading", "a heading", "family"))
    rc, out = run(CG, control)
    assert rc == 1
    assert "glossary-field-aka.json: its id begins 'glossary-field-' and it is in family 'model'" in out, out
    assert "a-heading.json: is in family 'family' and its id does not begin 'family-'" in out, out


# ------------------------------------------------------------------ rule 12: the starter questions

def _surface(rid, **surface):
    return _editorial(rid, "a page word " + rid, "surface", surface=dict({"what": "A page head."}, **surface))


def test_a_page_with_starter_questions_passes_and_is_counted(CG, control):
    write(control, _surface("surface-test", ask=["Where should I begin on this page?"]))
    rc, out = run(CG, control)
    assert rc == 0, out
    assert "starter questions checked: 1;" in out, out


def test_a_page_without_starter_questions_fails(CG, control):
    """`surface.ask` is required on a PAGE (family `surface`), and allowed on a dossier section."""
    write(control, _surface("surface-test"))
    write(control, _editorial("section-test", "a section word", "section",
                              surface={"what": "A section head."}))
    rc, out = run(CG, control)
    assert rc == 1
    assert "surface-test.json: is a page (family 'surface') and carries no `surface.ask`" in out, out
    assert "section-test.json" not in out, "a section may carry starter questions and need not"


def test_each_starter_question_is_held_to_its_rules(CG, control):
    too_long = " ".join(["word"] * 20) + " more?"
    write(control, _surface("surface-long", ask=[too_long]))
    write(control, _surface("surface-flat", ask=["This is a statement and not a question."]))
    write(control, _surface("surface-count", ask=["Why are there 3 fatal findings on this plan?"]))
    write(control, _surface("surface-many", ask=["One?", "Two?", "Three?", "Four?"]))
    rc, out = run(CG, control)
    assert rc == 1
    assert "surface-long.json: surface.ask[0] is 21 words; the most is 20" in out, out
    assert "surface-flat.json: surface.ask[0] does not end with a question mark" in out, out
    assert "surface-count.json: surface.ask[0] carries the numeral '3'" in out, out
    assert "surface-many.json: `surface.ask` holds 4 question(s); a page offers from 1 to 3" in out, out


# ------------------------------------------------------------------ rule 13: marks

def _tokens(tmp_path, css):
    p = tmp_path / "tokens.css"
    p.write_text(css, encoding="utf-8")
    return str(p)


def test_a_mark_naming_a_property_the_stylesheet_does_not_define_fails(CG, control):
    """The real stylesheet: a word may not name a mark the workbench cannot draw."""
    mutate(control, "judgment-passed", lambda r: r.__setitem__("mark", "--mark-no-such-token"))
    rc, out = run(CG, control)
    assert rc == 1
    assert ("judgment-passed.json: `mark` --mark-no-such-token is a property "
            "workbench/app/src/theme/tokens.css does not define") in out, out


def test_a_mark_is_held_to_what_the_stylesheet_declares_not_to_what_it_mentions(CG, control, tmp_path):
    """Defined means DECLARED: a property only used through var(), or only named in a comment,
    defines nothing -- and the declared one passes, which is the control for the other two."""
    css = (":root {\n  --mark-passed: var(--green-deep);\n}\n"
           ".x { background: var(--mark-used-only); }\n"
           "/* --mark-in-a-comment: a note, not a declaration; */\n")
    tokens = _tokens(tmp_path, css)
    mutate(control, "judgment-passed", lambda r: r.__setitem__("mark", "--mark-passed"))
    rc, out = run(CG, control, extra=("--tokens", tokens))
    assert rc == 0, out
    assert "marks held to the stylesheet: 1" in out, out
    mutate(control, "judgment-failed", lambda r: r.__setitem__("mark", "--mark-used-only"))
    mutate(control, "judgment-unjudged", lambda r: r.__setitem__("mark", "--mark-in-a-comment"))
    rc, out = run(CG, control, extra=("--tokens", tokens))
    assert rc == 1
    assert "judgment-failed.json: `mark` --mark-used-only is a property" in out, out
    assert "judgment-unjudged.json: `mark` --mark-in-a-comment is a property" in out, out
    assert "judgment-passed.json" not in out, out


def test_one_mark_named_by_two_records_fails(CG, control, tmp_path):
    tokens = _tokens(tmp_path, ":root { --mark-shared: var(--ink); }\n")
    for rid in ("judgment-passed", "judgment-failed"):
        mutate(control, rid, lambda r: r.__setitem__("mark", "--mark-shared"))
    rc, out = run(CG, control, extra=("--tokens", tokens))
    assert rc == 1
    assert "mark --mark-shared: named by 2 records" in out, out


def test_a_mark_outside_its_families_or_its_shape_fails(CG, control, tmp_path):
    tokens = _tokens(tmp_path, ":root { --mark-x: var(--ink); --hatch-45: none; }\n")
    mutate(control, "test-cites", lambda r: r.__setitem__("mark", "--mark-x"))
    mutate(control, "judgment-passed", lambda r: r.__setitem__("mark", "--hatch-45"))
    rc, out = run(CG, control, extra=("--tokens", tokens))
    assert rc == 1
    assert "test-cites.json: carries `mark` in family 'model'" in out, out
    assert "judgment-passed.json: `mark` '--hatch-45' is not a custom property named --mark-<name>" in out, out


def test_an_unreadable_stylesheet_is_could_not_evaluate_and_never_a_pass(CG, control, tmp_path):
    mutate(control, "judgment-passed", lambda r: r.__setitem__("mark", "--mark-passed"))
    rc, out = run(CG, control, extra=("--tokens", str(tmp_path / "no-such-tokens.css")))
    assert rc == CG.COULD_NOT_EVALUATE, out
    assert "UNJUDGED 1 record(s) carry a `mark`" in out, out
    assert "COULD NOT EVALUATE" in out, out
    # and a failure elsewhere is still a failure, not hidden behind the unjudged rule
    mutate(control, "judgment-failed", lambda r: r.__setitem__("definition", "Has 7 digits."))
    rc, out = run(CG, control, extra=("--tokens", str(tmp_path / "no-such-tokens.css")))
    assert rc == 1, out


def test_an_id_in_two_directories_is_a_duplicate(CG, control, tmp_path):
    other = tmp_path / "batch"
    other.mkdir()
    shutil.copy(control / "test-sourced.json", other / "test-sourced.json")
    rc, out = run(CG, control, other)
    assert rc == 1
    assert "duplicate id 'test-sourced'" in out, out
    rc2, _ = run(CG, control)                      # and each directory alone is fine
    assert rc2 == 0


def test_a_batch_outside_the_tree_is_checked_on_top_of_the_seeds(CG, control, tmp_path):
    """How WP-14.2's batches are meant to verify alone: the seeds' directory and the batch's,
    named together, checked as one set."""
    batch = tmp_path / "batch"
    batch.mkdir()
    shutil.move(str(control / "test-cites.json"), str(batch / "test-cites.json"))
    rc, out = run(CG, control, batch)
    assert rc == 0, out
    rc2, out2 = run(CG, batch)                      # the batch alone lacks the seeds
    assert rc2 == 1 and "the required record about-tdl.json is missing" in out2


def test_a_key_stated_twice_in_one_file_fails(CG, control):
    path = control / "judgment-passed.json"
    text = path.read_text(encoding="utf-8")
    doubled = text.replace('"term": "passed",', '"term": "passed",\n  "term": "passed",', 1)
    assert doubled != text
    path.write_text(doubled, encoding="utf-8")
    rc, out = run(CG, control)
    assert rc == 1
    assert "judgment-passed.json: states the key 'term' twice in one object" in out, out


def test_a_kit_provenance_note_is_not_a_bibliography(CG, control):
    """Rule 3's scope, measured: kits/ carries slot-level `sources` that are provenance notes
    ("Authored, not retrieved") and the contract does not admit them. A string found only there
    must fail."""
    six = set()
    for pattern in ("styles/*.json", "faults/*.json", "rooms/*.json", "groupings/*.json",
                    "partis/*.json", "proportions/**/*.json"):
        for p in sorted(glob.glob(os.path.join(ROOT, pattern), recursive=True)):
            six.update(s for s in (json.load(open(p, encoding="utf-8")).get("sources") or [])
                       if isinstance(s, str))
    kit_only = None

    def walk(o):
        nonlocal kit_only
        if kit_only is not None:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "sources" and isinstance(v, list):
                    for s in v:
                        if isinstance(s, str) and s not in six:
                            kit_only = s
                            return
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.json"))):
        walk(json.load(open(p, encoding="utf-8")))
    if kit_only is None:
        pytest.skip("every kit source string is also in the bibliography -- nothing to separate")
    mutate(control, "test-sourced", lambda r: r.__setitem__("sources", [kit_only]))
    rc, out = run(CG, control)
    assert rc == 1
    assert "test-sourced.json: source" in out and "is in no `sources` list" in out, out


# ------------------------------------------------------------------ could not evaluate

def _subprocess(block):
    code = ("import sys, runpy\n" + block +
            "sys.argv = ['check_glossary.py']\n"
            "runpy.run_path('build/check_glossary.py', run_name='__main__')\n")
    return subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)


def test_without_jsonschema_it_could_not_evaluate():
    p = _subprocess("sys.modules['jsonschema'] = None\n")
    assert p.returncode == 3, p.stdout + p.stderr
    assert "COULD NOT EVALUATE" in p.stdout and "jsonschema" in p.stdout, p.stdout


def test_without_the_citation_validator_it_could_not_evaluate():
    p = _subprocess("sys.modules['workbench.server.citations'] = None\n")
    assert p.returncode == 3, p.stdout + p.stderr
    assert "workbench.server.citations cannot be imported" in p.stdout, p.stdout


def test_it_does_not_need_fastapi():
    """The contract's premise: the citation validator imports without the web framework, so a
    checkout with no server dependencies still judges the glossary rather than giving up."""
    p = _subprocess("sys.modules['fastapi'] = None\n")
    assert p.returncode == 0, p.stdout + p.stderr


# ------------------------------------------------------------------ the shared spellings

def test_glossary_rec_re_admits_what_the_contract_names_and_nothing_else():
    CO = _load("check_openings_for_glossary", "build/check_openings.py")
    rx = CO.GLOSSARY_REC_RE
    admitted = ["VISION.md", "README.md", "docs/geometry.md", "schema/kit.schema.json",
                "mcp_server/core.py", "partis/five-part-palladian.json", "build/roof.py",
                "massings/catalog.json", "elements/slots.json", "proportions/systems/x.json",
                # WP-14.29: the one app file, by its exact path -- the duty-block comments are
                # the written meaning of every `--mark-*` the `mark-*` records name.
                "workbench/app/src/theme/tokens.css"]
    for p in admitted:
        assert rx.findall(f"read {p} here") == [p], p
    # Real paths, on purpose: build/check_ids.py reads every file for `docs/reports/<name>.md` and
    # fails the build on one that does not exist -- which an invented specimen here did, on this
    # file's first run of that checker.
    for p in ("workbench/README.md", "docs/reports/ux-first-principles-2026-09-24.md",
              "docs/open-questions/oq-one-duty-per-hatch.md",
              "CLAUDE.md", "glossary/about-tdl.json", "precedents/x.json",
              # ...and nothing else of the app: not a neighbour of the stylesheet, not a CSS
              # file by suffix, not the module that draws the marks.
              "workbench/app/src/marks.js", "workbench/app/src/theme/fonts.css"):
        assert p not in rx.findall(f"read {p} here"), p
    assert rx.findall("read workbench/README.md here") == []


def test_check_basis_counts_what_it_verified_and_rec_re_changes_what_it_reads():
    CO = _load("check_openings_for_count", "build/check_openings.py")

    class Rep:
        def __init__(self):
            self.errors, self.unj = [], []

        def err(self, w, m):
            self.errors.append(m)

        def unjudged(self, w, m):
            self.unj.append(m)

    two = {"id": "t", "basis": 'VISION.md "A traditional house is a sentence in a language" and '
                               '"the language can be written down."'}
    rep = Rep()
    assert CO.check_basis(rep, two, source="x", rec_re=CO.GLOSSARY_REC_RE) == 2 and not rep.errors
    one_bad = dict(two, basis=two["basis"].replace("can be written down", "cannot be written down"))
    rep = Rep()
    assert CO.check_basis(rep, one_bad, source="x", rec_re=CO.GLOSSARY_REC_RE) == 1
    assert len(rep.errors) == 1
    # the default pattern is the grammar files' own and does not admit VISION.md at all
    rep = Rep()
    assert CO.check_basis(rep, two, source="x") == 0
    assert rep.errors == ["basis names no record — an editorial call must say what it read"]
