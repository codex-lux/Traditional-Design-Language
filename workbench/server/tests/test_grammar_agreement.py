"""The three copies of the citation grammar must agree — checked, not asserted in prose.

There are three regexes for one grammar, in two languages:

  * `workbench/server/citations.py::REF_RE`   validates a ref against the corpus
  * `workbench/server/rail.py::CITE_RE`       EXTRACTS `[[cite:...]]` from model output
  * `workbench/app/src/citations.js::parseCite`  parses it in the browser

WP-5.6 found the client narrower than the server — it rejected the dot in a constraint id like
`tidewater-georgian.c01` — widened the client, and published that as "660 citations un-broken".
It was not: an adversarial audit found `rail.py`'s extractor carried a THIRD copy, also without
the dot, so a constraint citation never reached `validate()` at all and streamed to the reader
as literal bracket text. Widening the parser could not help, because the parser was never
handed anything to parse.

The lesson is not "widen the third one" — it is that a grammar spelled three times will drift
again. The server pair now share `ID_CHARS`/`FRAG_CHARS`, so this pins the remaining seam: the
JavaScript, which cannot import a Python constant.

The previous guard, `router-unit.mjs`, asserted ONE hand-written example against the client
alone and the docs described it as pinning the two against each other. It did not, and could
not: it never read the server at all.
"""
import re

import pytest

from workbench.server import citations, rail

CLIENT = "workbench/app/src/citations.js"


@pytest.fixture(scope="module")
def client_classes():
    """The character classes the browser's parseCite actually uses."""
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    src = open(os.path.join(root, CLIENT), encoding="utf-8").read()
    ids = re.search(r"export const ID_CHARS = '([^']+)'", src)
    frags = re.search(r"export const FRAG_CHARS = '([^']+)'", src)
    m = ids and frags
    assert m, ("could not find parseCite's regex in citations.js — if it was reformatted, "
               "update this reader rather than deleting the check: an unread guard is the "
               "state this test exists to prevent")
    return ids.group(1), frags.group(1)


def test_client_and_server_id_classes_are_identical(client_classes):
    ids, frags = client_classes
    assert ids == citations.ID_CHARS, (
        f"the browser accepts [{ids}] in an id and the server accepts "
        f"[{citations.ID_CHARS}]. A ref one half accepts and the other rejects is a citation "
        f"that validates and then renders as dead text, which is how all 660 constraint ids "
        f"were inert.")
    assert frags == citations.FRAG_CHARS, (ids, frags)


def test_the_rail_extractor_accepts_every_id_the_validator_does():
    """The seam that was actually broken. `[[cite:...]]` must reach validate()."""
    cases = [
        "style:craftsman",
        "constraint:tidewater-georgian.c01",     # the dot — the whole finding
        "slot:door-main-entry#head",
        "fault:porch-too-shallow-to-inhabit",
        "pack:gibbs-doric",
    ]
    for ref in cases:
        assert citations.REF_RE.match(ref), f"REF_RE should accept {ref}"
        wrapped = f"[[cite:{ref}]]"
        m = rail.CITE_RE.search(wrapped)
        assert m, (f"rail.CITE_RE does not extract {wrapped}, so validate() never sees it and "
                   f"the reader gets raw bracket syntax instead of a citation")
        assert m.group(1) == ref


def test_a_real_constraint_citation_streams_as_a_citation_not_as_text():
    """End to end, because the regex agreeing is not the same as the reader seeing it."""
    events = rail._emit_text(
        "The rule is [[cite:constraint:tidewater-georgian.c01]].", {})
    kinds = {name for name, _ in events}
    assert "cites" in kinds, f"no cites event was emitted: {events}"
    refs = [d["refs"] for name, d in events if name == "cites"][0]
    assert "constraint:tidewater-georgian.c01" in refs
    text = [d["text"] for name, d in events if name == "text"][0]
    assert "[[cite:" not in text, f"the bracket syntax reached the reader: {text!r}"


def test_trailing_newline_is_rejected_the_same_way_on_both_sides():
    """Python's `$` also matches before a trailing newline; JavaScript's does not. `\\Z`
    closes that, so a ref with a trailing newline is refused by both rather than by one."""
    assert not citations.REF_RE.match("style:craftsman\n")
