"""The ruling table is the package's product, and a list nobody checks goes stale like any other.

WP-8.7 read all 244 (node, pack) pairs in OQ 51's backlog. 89 declines and 3 endorsements were
written into the corpus; the 152 the records could not settle are in
`docs/open-questions/oq-the-adjudication-cases-the-records-do-not-decide.md` for a human.

Two ways that file can lie, and both are held here. A row that has since been CLOSED -- adjudicated,
or re-attributed away by a neighbouring decline -- would put a settled question in front of the
reader. And a live unendorsed gap that appears in NO row would be a gap nobody has looked at,
sitting silently outside the list that claims to be the remainder.
"""
import importlib.util
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "docs", "open-questions",
                     "oq-the-adjudication-cases-the-records-do-not-decide.md")


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _rows():
    """(node, pack) for every row, read from the rendered table rather than a side file."""
    out, pack = [], None
    for line in open(TABLE, encoding="utf-8"):
        h = re.match(r"^## `([a-z0-9-]+)`", line)
        if h:
            pack = h.group(1)
            continue
        m = re.match(r"^\|\s*(?:↺ )?`([a-z0-9-]+)`\s*\|", line)
        if m and pack:
            out.append((m.group(1), pack))
    return out


@pytest.fixture(scope="module")
def live():
    ci = _mod("_ci_wp87", "build/check_inheritance.py")
    g = ci.load()
    _b, gaps, _p, _d = ci.measure(g)
    applies = ci.applies_to_index()
    return {(t[0], t[3]) for t in gaps if t[0] not in applies.get(t[3], ())}


def test_the_table_parses_at_all():
    """A regex matching nothing would make both tests below pass vacuously -- the failure mode
    `e2e/walk.mjs` guards against by counting rooms before checking labels."""
    rows = _rows()
    assert len(rows) >= 150, len(rows)
    assert len(set(rows)) == len(rows), "a (node, pack) pair is tabled twice"


def test_no_row_is_a_question_that_has_since_been_answered(live):
    """A row whose gap is closed -- endorsed, declined, or re-attributed away by a neighbouring
    decline -- is a settled question put in front of a reader as though it were open."""
    stale = [r for r in _rows() if r not in live]
    assert not stale, ("these rows are no longer live unendorsed gaps: "
                       "re-generate the table or explain each", sorted(stale)[:20])


def test_every_live_gap_is_either_tabled_or_named_as_unread(live):
    """THE DEFINITION OF DONE, AND IT HAS TWO HALVES BECAUSE THE BACKLOG REFILLS.

    Every gap the corpus cannot settle must be in the list that claims to be the remainder. But
    adjudicating 244 pairs and declining 114 of them PROMOTED new packs into the roles those
    declines vacated -- gaps that are live and that nobody has read, because they did not exist
    when the reading started. Tabling those as "cases the records do not decide" would be a lie:
    they are cases nobody has looked at. So the file carries a second, separately headed section
    for them, and this test requires every live gap to be in one section or the other.

    A gap in NEITHER is the failure this test exists for: one sitting silently outside a document
    that claims to be the complete remainder."""
    tabled = set(_rows())
    text = open(TABLE, encoding="utf-8").read()
    unread = set(re.findall(r"^- `([a-z0-9-]+)` / `([a-z0-9-]+)`", text, re.M))
    missing = sorted(live - tabled - unread)
    assert not missing, (
        f"{len(missing)} live unendorsed gap(s) are in neither section -- adjudicate them, table "
        f"them, or list them as unread", missing[:20])
    assert not (tabled & unread), ("a pair is both tabled and listed unread",
                                   sorted(tabled & unread)[:10])


def test_the_gated_packs_are_marked_in_the_table():
    """Five packs' applies_to is a live gate. A reader ruling on one of those rows is authorising
    a behavioural change, and the table has to say so where they will see it."""
    ci = _mod("_ci_wp87b", "build/check_inheritance.py")
    text = open(TABLE, encoding="utf-8").read()
    tabled = {p for _n, p in _rows()}
    for pack in ci.GATES:
        if pack not in tabled:
            continue
        assert re.search(r"^## `%s` ⚡" % re.escape(pack), text, re.M), (
            f"{pack} is a live gate and its heading in the ruling table does not say so")
