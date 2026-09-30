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
    ancestor. Found in the corpus while a case exists: colonial-revival's `cornice_return` and
    georgian-revival's `water_table` were the only two, and WP-16.2's adjudication bound both in
    the styles' own kits (30 Sep 2026). So this sweep skips on today's corpus, and the driven
    twin below carries the property."""
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


def test_a_forbidden_slot_extended_by_the_style_names_the_base_DRIVEN(client, monkeypatch):
    """The property the sweep above guards, DRIVEN, because the corpus no longer holds a case.

    The record is built by the REAL resolver over synthetic kits: a base binding the slot
    forbidden, and the style extending it with a delta, which cannot change a binding. It is
    served as the style's resolved slot, and the route must name the BASE as `bound_by`, never
    the style whose delta is the nearest record (`_source`). A guard that goes quiet when its
    corpus case is fixed is no guard; this one cannot."""
    rk, _g = core._kit_graph()
    sid, slot, base = "colonial-revival", "cornice_return", "gothic-revival-american"
    kits = {base: {slot: {"binding": "forbidden", "note": "bargeboards"}},
            sid: {slot: {"binding": "extends", "rule_append": "a return is permitted"}}}
    graph = {"nodes": {sid: {}, base: {}},
             "slots": [{"id": slot, "group": "massing-and-roof", "name": "Cornice return"}]}
    with monkeypatch.context() as m:
        m.setattr(rk, "load_kit", lambda nid: kits.get(nid, {}))
        rec = rk.resolve_slots(graph, [sid, base])[0][slot]
    # the premise: the resolver itself credits the base, and the nearest record is the style's
    assert (rec["binding"], rec["_source"], rec["_bound_by"]) == ("forbidden", sid, base), rec
    real = core._resolved_kit
    monkeypatch.setattr(core, "_resolved_kit",
                        lambda s: {**(real(s) or {}), slot: rec} if s == sid else real(s))
    got = client.get(f"/api/kit/{sid}/slot/{slot}").json()
    assert got["bound_by"] == base, got
    assert got["binding"] == "forbidden", got
