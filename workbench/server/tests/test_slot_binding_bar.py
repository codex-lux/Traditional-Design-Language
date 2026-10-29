"""Phase 17 (WP-17.13): who binds a slot across every style, as four parts that partition them."""
import pytest

pytest.importorskip("fastapi")


@pytest.mark.parametrize("slot_id", ["cornice", "dormer", "shutter"])
def test_the_four_parts_partition_the_styles(slot_id):
    from workbench.server import corpus
    b = corpus.slot(slot_id)["bindings"]
    spec, forb, ext, opn = set(b["specified"]), set(b["forbidden"]), set(b["extends"]), set(b["open"])
    assert ext <= spec, "an extended binding is a specified one with a later writer"
    assert not (spec & forb) and not (spec & opn) and not (forb & opn)
    assert len(spec) + len(forb) + len(opn) == b["of"] == len(corpus.core._data()["styles"])


def test_an_extended_binding_is_a_proper_part_of_the_specified():
    """Phase 17's audit: only `extends <= specified` was held, so counting every specified style as
    extended stayed green. The cornice has both kinds, and each is pinned by a style of its own."""
    from workbench.server import corpus
    b = corpus.slot("cornice")["bindings"]
    spec, ext = set(b["specified"]), set(b["extends"])
    assert ext and ext < spec, "some specified styles are extended, and not all of them"
    chain = lambda sid: (corpus.core._resolved_kit(sid).get("cornice") or {}).get("_source_chain") or []
    assert all(len(chain(s)) > 1 for s in ext)
    assert all(len(chain(s)) <= 1 for s in spec - ext), "a style one node settled is not extended"
