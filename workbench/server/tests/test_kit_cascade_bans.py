"""Phase 17 (WP-17.10): each ban in the cascade column credited to its writer."""
import pytest

pytest.importorskip("fastapi")

def test_the_cascade_credits_each_ban_to_the_node_that_wrote_it():
    """WP-17.10: the Kit's cascade column says which level forbade what, off the resolved kit's own
    writers -- colonial-revival's whole-slot bans are shingle-style's and queen-anne-british's
    (WP-16.2), never colonial-revival's own."""
    from workbench.server import corpus
    out = corpus.kit_cascade("colonial-revival")
    by = {r["id"]: r["bans"] for r in out["cascade"]}
    resolved = corpus.core._resolved_kit("colonial-revival")
    slot_bans = sorted((s, r["_bound_by"]) for s, r in resolved.items()
                       if isinstance(r, dict) and r.get("binding") == "forbidden" and r.get("_bound_by"))
    assert slot_bans, "the premise: the resolved kit carries a whole-slot ban"
    for slot, writer in slot_bans:
        assert {"slot": slot, "variant": None} in by.get(writer, []), (slot, writer)
    credited = sum(len(v) for v in by.values())
    assert credited >= len(slot_bans)
    assert all(b["slot"] in resolved for v in by.values() for b in v)
