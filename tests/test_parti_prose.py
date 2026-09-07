"""WP-11.11 — the per-parti Part VI, generated rather than read out.

The instrument makes no pass/fail claim, so it is not a `check_all` check. That makes a test the
only thing standing between it and silent rot, and an instrument that rots is worse than a test
that rots: its output is a NUMBER rather than a green tick, and a number is believed.
"""
import collections
import glob
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PP = _load("parti_prose", f"{ROOT}/build/parti_prose.py")


@pytest.fixture(scope="module")
def corpus():
    return PP._load()


@pytest.fixture(scope="module")
def survey(corpus):
    CGR, partis, groupings, rooms, massings = corpus
    return PP.survey("centre-passage-double-pile", partis, groupings, rooms, massings, CGR)


class TestTheStates:
    def test_three_states_and_none_is_a_pass_or_a_fail(self, survey):
        # `by hand` is not a defect and `executed` is not a verdict on the house -- the instrument
        # counts what is EXECUTABLE, which is a different question from what is true.
        states = {r[2] for r in survey["grouping_rules"] + survey["massing_prose"]
                  + survey["orientation"]}
        assert states <= {PP.EXECUTED, PP.REPORTED, PP.BY_HAND}

    def test_a_rule_with_a_test_is_executed_and_one_with_a_reporter_is_reported(self, corpus,
                                                                               survey):
        # `centre-passage-core` carries one of each after WP-11.7 and WP-11.9, which is why it is
        # the fixture: the facade-share rule REPORTS by ruling and the passage-ends rule tests.
        by_id = {r[0]: r for r in survey["grouping_rules"]}
        assert by_id["centre-passage-core[0]"][2] == PP.EXECUTED
        assert by_id["centre-passage-core[2]"][2] == PP.REPORTED    # the facade share
        assert by_id["centre-passage-core[1]"][2] == PP.BY_HAND     # the alignment half

    def test_the_published_split_is_what_the_instrument_returns(self, survey):
        # The precedents report quotes these four numbers. A number in a report is worth what a
        # test holds it to -- and this file's own first draft said the orientation block was 26
        # rows where it is 20, caught by re-deriving rather than re-reading.
        assert PP.counts(survey) == {PP.EXECUTED: 24, PP.REPORTED: 6, PP.BY_HAND: 20,
                                     "prose figures nothing carries": 7}
        assert len(survey["grouping_rules"]) == 26
        assert len(survey["massing_prose"]) == 4
        assert len(survey["orientation"]) == 20

    def test_every_room_type_the_parti_names_reaches_the_orientation_block(self, corpus, survey):
        """RENAMED, because the assertion is about the BLOCK and not about the aspect (audit,
        7 Sep 2026). `orientation_rows` appends a row for every type whose record carries
        `daylight.orientation`, INCLUDING the no-aspect case, so the length equality held
        whether or not one of the twenty stated an aspect at all -- the name and the premise
        promised something the assertion did not check.

        Both facts are worth having, so both are asserted: every named type reaches the block,
        and the split between the states is the one the report publishes.
        """
        _, partis, _, rooms, _ = corpus
        types = sorted({r["type"] for r in partis["centre-passage-double-pile"]["rooms"]
                        if r.get("type")})
        assert len(types) == 20
        assert len(survey["orientation"]) == len(types), \
            "a room type whose record states no orientation would be missing from this block"
        states = collections.Counter(r[2] for r in survey["orientation"])
        assert states == {PP.EXECUTED: 15, PP.REPORTED: 5}, (
            f"the orientation block's split moved to {dict(states)}. All twenty rows left "
            f"`by hand` at WP-11.9, which is the finding the precedents report publishes; a "
            f"row back in BY_HAND means a room record stopped stating a readable aspect")


class TestWhatItReads:
    def test_the_massing_prose_nothing_reads_is_named(self, survey):
        # WP-9.2 measured the readers: `structural_logic` has zero corpus-wide. All four rows are
        # `by hand` and two of them are rows 1 and 2 of the diagnosis's own hand-made table.
        wheres = [r[0] for r in survey["massing_prose"]]
        assert wheres.count("four-over-four.constraints") == 2
        assert "four-over-four.structural_logic" in wheres
        assert all(r[2] == PP.BY_HAND for r in survey["massing_prose"])

    def test_the_prose_meter_is_imported_and_not_transcribed(self):
        # `check_grouping_rules.prose_meter` is the ONE spelling; its own docstring records what
        # its first version cost. A second crude regex is how a corpus ends up with two different
        # upper bounds for one question.
        src = open(f"{ROOT}/build/parti_prose.py").read()
        assert "CGR.prose_meter(" in src
        for token in ("re.finditer", "re.compile", "_WORDS", "_UNIT"):
            assert token not in src, f"parti_prose.py has grown its own figure scanner ({token})"

    def test_the_prose_meter_is_the_same_meter_behaviourally(self, corpus):
        """AND A SOURCE READING IS NOT ENOUGH ON ITS OWN (audit, 7 Sep 2026).

        The assertions above are a blocklist of four spellings and a positive substring: the
        substring passes on a commented-out call, and a hand-rolled scanner using `str.split()`,
        `regex` or `re.search` evades all four names. So the equality is asserted too --
        `room_figures` returns exactly what `prose_meter` returns for the same scope, which no
        second implementation can satisfy by accident.
        """
        CGR, partis, groupings, rooms, massings = corpus
        p = partis["centre-passage-double-pile"]
        sub_g = {g: groupings[g] for g in p["groupings"] if g in groupings}
        want = {r["type"] for r in p["rooms"] if r.get("type")}
        direct = CGR.prose_meter(sub_g, {k: v for k, v in rooms.items() if k in want})
        assert direct, "the meter returned nothing; the equality below would be vacuous"
        assert PP.room_figures(p, rooms, groupings, CGR) == direct

    def test_it_is_scoped_to_the_parti_and_not_the_corpus(self, corpus):
        # A Part VI is about ONE diagram. A version that swept corpus-wide would return the same
        # table for every parti, which reads exactly like a working instrument.
        CGR, partis, groupings, rooms, massings = corpus
        a = PP.survey("centre-passage-double-pile", partis, groupings, rooms, massings, CGR)
        b = PP.survey("shotgun-linear", partis, groupings, rooms, massings, CGR)
        assert PP.counts(a) != PP.counts(b)
        assert {r[0] for r in a["grouping_rules"]} & {r[0] for r in b["grouping_rules"]} == set()

    def test_every_parti_in_the_corpus_surveys(self, corpus):
        CGR, partis, groupings, rooms, massings = corpus
        assert len(partis) == 21
        for pid in sorted(partis):
            c = PP.counts(PP.survey(pid, partis, groupings, rooms, massings, CGR))
            assert sum(c.values()) > 0, f"{pid} returned an empty survey"


class TestTheReportQuotesIt:
    def test_the_generated_section_is_in_the_precedents_file(self, survey):
        # The report embeds the generated markdown. If the instrument's output shape moves and the
        # file is not regenerated, this is what says so.
        md = PP.report(survey, md=True)
        doc = open(f"{ROOT}/docs/reports/precedents-centre-passage-double-pile.md").read()
        assert "## Part VI — what `centre-passage-double-pile` says and cannot execute" in doc
        head = md.split("\n")[0]
        assert head in doc
        # every grouping-rule row of the generated table really appears in the file
        for where, _sev, _state, _text in survey["grouping_rules"]:
            assert f"`{where}`" in doc, f"{where} is in the survey and not in the report"

    def test_the_four_numbers_the_report_quotes(self, survey):
        """The report's figures against the INSTRUMENT, not against themselves.

        The second assertion used to compare a literal in this file with the same literal in the
        document -- it could only fail if someone edited the doc, which is the one case where a
        human is already looking (audit, 7 Sep 2026). Both pairs are derived from `survey` now,
        so the document is held to what the instrument returns.
        """
        doc = open(f"{ROOT}/docs/reports/precedents-centre-passage-double-pile.md").read()
        c = PP.counts(survey)
        assert (f"**Fifty rows: {c[PP.EXECUTED]} executed, {c[PP.REPORTED]} reported, "
                f"{c[PP.BY_HAND]} handed to a reader, and "
                f"{c['prose figures nothing carries']} prose") in doc
        o = collections.Counter(r[2] for r in survey["orientation"])
        assert f"**{o[PP.EXECUTED]} `executed` and {o[PP.REPORTED]} `reported`**" in doc


class TestTheGuardThatCouldNotFail:
    """One of six mutations was BLIND and it is recorded rather than patched.

    Replacing `room_figures`' room filter with the whole corpus leaves the suite green. That is
    not a hole to plug with a test that would pass for the wrong reason -- it is a MEASUREMENT
    about `check_grouping_rules.prose_meter`, and this pins the measurement so that if the meter
    ever grows a room-side population of its own the claim stops being true loudly.
    """

    def test_the_room_scope_is_currently_inert_and_the_reason_is_the_grouping_scope(self, corpus):
        CGR, partis, groupings, rooms, massings = corpus
        p = partis["centre-passage-double-pile"]
        sub_g = {g: groupings[g] for g in p["groupings"] if g in groupings}
        want = {r["type"] for r in p["rooms"] if r.get("type")}
        scoped = CGR.prose_meter(sub_g, {k: v for k, v in rooms.items() if k in want})
        wide = CGR.prose_meter(sub_g, rooms)
        assert scoped == wide, (
            "the room filter in parti_prose.room_figures has become load-bearing. That is FINE "
            "and is what it was written for -- but the comment above it says it is inert, and "
            "an inert-looking line that is actually doing work is worse than either. Update the "
            "comment and re-measure.")
        # AND NOT `<= want`, WHICH HELD BY CONSTRUCTION (audit, 7 Sep 2026). `prose_meter`
        # skips any room id absent from the dict it is handed, and the dict was filtered to
        # `want` two lines above -- so the subset relation was a property of this test's own
        # input and could not fail for any implementation. Equality of the room SET is the real
        # claim: the scoped call reaches every one of the parti's room types that carries a
        # prose figure, and no other.
        got = {w.split(".")[0] for k, w, _f, _s in scoped if k == "room"}
        assert got == {w.split(".")[0] for k, w, _f, _s in wide if k == "room"} and got <= want
        assert got, "no room row at all; the equality above would be vacuous"

    def test_the_grouping_scope_is_the_one_that_bites(self, corpus):
        # The complement of the test above: widening the GROUPINGS does change the answer, which
        # is why that mutation is caught and this one is not.
        CGR, partis, groupings, rooms, massings = corpus
        p = partis["centre-passage-double-pile"]
        sub_g = {g: groupings[g] for g in p["groupings"] if g in groupings}
        want = {r["type"] for r in p["rooms"] if r.get("type")}
        sub_r = {k: v for k, v in rooms.items() if k in want}
        assert CGR.prose_meter(sub_g, sub_r) != CGR.prose_meter(groupings, sub_r)
