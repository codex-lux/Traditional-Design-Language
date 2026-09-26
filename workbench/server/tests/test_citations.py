from workbench.server import citations


def test_corpus_kinds_validate_against_real_ids():
    assert citations.validate("style:tidewater-georgian")[0]
    assert citations.validate("fault:porch-too-shallow-to-inhabit")[0]
    assert citations.validate("slot:roof_pitch")[0]
    assert not citations.validate("style:no-such-style")[0]
    assert not citations.validate("banana:whatever")[0]
    assert not citations.validate("style tidewater")[0]


def test_kit_fragment_is_a_slot():
    assert citations.validate("kit:tidewater-georgian#roof_pitch")[0]
    assert not citations.validate("kit:tidewater-georgian#no_such_slot")[0]


def test_candidate_scoped_by_context():
    assert citations.validate("candidate:2", {"candidate_count": 4})[0]
    assert not citations.validate("candidate:9", {"candidate_count": 4})[0]
    assert citations.validate("candidate:2")[0]  # no context → benefit of the doubt


# ------------------------------------------------------------------ WP-14.3
# `term` is a citation kind, and a `style:` fragment may name a dossier section as well as a
# slot (PRD phase 14, §E.6). The grammar -- REF_RE -- is untouched; what moved is which ids the
# validator knows and which fragments it accepts.

def test_a_term_citation_resolves_against_the_glossary():
    from workbench.server import corpus
    ids = sorted(corpus.core._data()["glossary"])
    assert ids, "the premise: the glossary is loaded"
    for i in ids:
        assert citations.validate("term:" + i) == (True, None), i
    ok, why = citations.validate("term:no-such-term")
    assert not ok and why == "unknown term id 'no-such-term'", why


def test_a_style_fragment_is_a_slot_or_a_dossier_section():
    for s in citations.DOSSIER_SECTIONS:
        assert citations.validate("style:tidewater-georgian#" + s) == (True, None), s
    assert citations.validate("style:tidewater-georgian#roof_pitch") == (True, None)
    ok, why = citations.validate("style:tidewater-georgian#no-such-section")
    assert not ok and why == "unknown slot or section fragment 'no-such-section'", why


def test_a_kit_fragment_is_a_slot_only():
    """A kit has no sections, so a section name is not a kit fragment. Every section is asked,
    so a validator that let the kit share the style's rule cannot pass on the one it missed."""
    for s in citations.DOSSIER_SECTIONS:
        ok, why = citations.validate("kit:tidewater-georgian#" + s)
        assert not ok and why == f"unknown slot fragment '{s}'", (s, why)


def test_the_grammar_itself_did_not_move():
    """REF_RE is spelled in three places by standing decision and WP-14.3 changes none of them:
    the id and fragment classes are byte-for-byte what test_grammar_agreement.py holds the other
    two to."""
    assert citations.ID_CHARS == r"A-Za-z0-9_.-"
    assert citations.FRAG_CHARS == r"A-Za-z0-9_-"
    assert citations.REF_RE.pattern == rf"^([a-z]+):([{citations.ID_CHARS}]+)(?:#([{citations.FRAG_CHARS}]+))?\Z"
