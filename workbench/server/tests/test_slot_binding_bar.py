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
