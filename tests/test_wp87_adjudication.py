"""The ruling table is the package's product, and a list nobody checks goes stale like any other.

WP-8.7 read the backlog TWICE, because it refills. 244 pairs in the first pass, then the 73 those
declines surfaced: 317 adjudications, 168 declines and 3 endorsements written into the corpus, and
the 171 the records could not settle in
`docs/open-questions/oq-the-adjudication-cases-the-records-do-not-decide.md` for a human. The
second pass surfaced 50 more, which that file carries under its own heading as NOT YET READ.

These figures were 244/89/152 when this file was written and were left standing through the second
pass -- the exact thing this test exists to prevent, one layer up, in the prose of the guard rather
than in the list it guards.

Two ways that file can lie, and both are held here. A row that has since been CLOSED -- adjudicated,
or re-attributed away by a neighbouring decline -- would put a settled question in front of the
reader. And a live unendorsed gap that appears in NO row would be a gap nobody has looked at,
sitting silently outside the list that claims to be the remainder.
"""
import collections
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
    `e2e/walk.mjs` guards against by counting rooms before checking labels.

    THIS WAS A FLOOR OF 150 AND THE FLOOR WAS THE WRONG INSTRUMENT (WP-8.12). Every opt-in flip
    legitimately WITHDRAWS rows -- 10, then 13, then 11 -- so the population this guards shrinks
    by design, and the count reached 147. Lowering the number each flip is precisely the
    "a floor that drops every time somebody does the ruled thing protects nothing by the end"
    anti-pattern this repository argues against in `test_construction_scope.py` and in
    `check_inheritance`'s own ratchet comments.

    So the guard is a CROSS-CHECK instead of a magic number, and it is strictly stronger. Each
    pack heading states its own row count (`## `pack` — N node(s)`), authored beside the rows; the
    row regex and the heading regex are independent, so a broken row pattern makes the two
    disagree and a heading whose count went stale is caught in the same assertion. Neither can go
    vacuous alone."""
    import re as _re
    rows = _rows()
    claimed = [(m.group(1), int(m.group(2))) for m in
               _re.finditer(r"^## `([a-z0-9-]+)`[^\n]*?— (\d+) node\(s\)",
                            open(TABLE, encoding="utf-8").read(), _re.M)]
    assert claimed, "no pack heading states a row count -- the heading regex found nothing"
    per_pack = collections.Counter(p for _n, p in rows)
    assert sum(n for _p, n in claimed) == len(rows), (
        sum(n for _p, n in claimed), len(rows),
        "the headings' own counts and the parsed rows disagree -- one of the two regexes is "
        "broken, or a heading went stale when rows were withdrawn")
    for pack, n in claimed:
        assert per_pack[pack] == n, (pack, per_pack[pack], n)
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
    adjudicating 317 pairs and declining 168 of them PROMOTED new packs into the roles those
    declines vacated -- gaps that are live and that nobody has read, because they did not exist
    when the reading started. 244 read produced 73; those 73 produced 50. Tabling those as "cases the records do not decide" would be a lie:
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
