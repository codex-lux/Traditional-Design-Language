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
