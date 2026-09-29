"""The slot page's variant ladder is the RESOLVED one, each row with its writer (WP-16.2, R3).

`corpus.slot_detail` walked the cascade to the nearest kit FILE with a `variants` list and served
that list whole. Where that file `extends` the slot, the list is the style's delta rows alone, so
the page hid every inherited row, the bans among them, and credited the ladder to the wrong node.
The subject is found in the corpus rather than named, because WP-16.2's own adjudication binds
some of these slots in the style's own kit and a named case would go quiet the day it is fixed.
"""
import pytest

from workbench.server import corpus

core = corpus.core


def _an_extended_slot_with_an_inherited_ban():
    """The first (style, slot), by id, whose style's own kit file EXTENDS the slot with variants
    of its own and whose resolved ladder carries a forbidden row an ancestor wrote."""
    D = core._data()
    for sid in sorted(D["styles"]):
        own = ((D["kits"].get(sid) or {}).get("slots") or {})
        rk = core._resolved_kit(sid) or {}
        for slot in sorted(own):
            r = own[slot]
            if r.get("binding") != "extends" or not r.get("variants"):
                continue
            rows = (rk.get(slot) or {}).get("variants") or []
            if any(v.get("status") == "forbidden" and v.get("_written_by") != sid for v in rows):
                return sid, slot, rows
    pytest.skip("no style extends a slot over an inherited ban; the premise has moved")


def test_the_ladder_is_the_resolved_one_with_its_writers(client):
    sid, slot, rows = _an_extended_slot_with_an_inherited_ban()
    r = client.get(f"/api/kit/{sid}/slot/{slot}")
    assert r.status_code == 200, r.text[:200]
    got = r.json()
    served = [(v["id"], v.get("status"), v.get("written_by")) for v in got["variants"]]
    assert served == [(v["id"], v.get("status"), v.get("_written_by")) for v in rows]
    # the rows the delta list alone would have hidden are served, with the ancestor named
    assert any(w != sid and st == "forbidden" for _i, st, w in served), served
    assert got["bound_by"] == (core._resolved_kit(sid) or {})[slot]["_bound_by"]
    assert "variants_from" not in got
    # nothing internal leaks: the writer is served as `written_by`, never as `_written_by`
    assert not [k for v in got["variants"] for k in v if k.startswith("_")]


def test_a_forbidden_slot_names_the_node_that_bound_it(client):
    """A slot bound forbidden by an ancestor and extended by the style reads `bound_by` as the
    ancestor. Found in the corpus: colonial-revival's `cornice_return` is this shape today."""
    D = core._data()
    for sid in sorted(D["styles"]):
        rk = core._resolved_kit(sid) or {}
        for slot, rec in sorted(rk.items()):
            if rec.get("binding") == "forbidden" and rec.get("_source") == sid \
                    and rec.get("_bound_by") != sid:
                got = client.get(f"/api/kit/{sid}/slot/{slot}").json()
                assert got["bound_by"] == rec["_bound_by"], got
                assert got["binding"] == "forbidden"
                return
    pytest.skip("no style extends a slot an ancestor forbids; the premise has moved")
