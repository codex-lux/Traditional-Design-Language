"""WP-14.4 (PRD §H.1, §H.2): every pack the engine can draw is served with its members and its
geometry, the module that IS the ceiling is dimensioned at the ceiling, and a pack says who
uses it.

`GET /api/proportions/{pack}?members=true` used to serve members only for the 25 packs with a
column stack, because `pe.dimension(pk, mod, None)` dimensions `stack_for(pk)` and that knows
only order assembly names -- so `trim-classical`, whose three wall sections and three casings
the same engine dimensions happily one at a time, came back with no assemblies at all.

Every expectation here is COMPUTED from the engine, the corpus or another endpoint -- no count
is written down -- and the stacked path is held to what it served before, key by key.
"""
import os

import pytest

from workbench.server import corpus

core = corpus.core

NEW_KEYS = ("drawing", "at", "module_name", "module_bound_to", "kind", "used_by")


def _pe():
    return core._data()["engine"]


def _prof():
    return core._mod("profiles", os.path.join(corpus.ROOT, "build", "profiles.py"))


def _expected_drawing(pk):
    pe = _pe()
    if pe.stack_for(pk):
        return "stack"
    return "assemblies" if pk.get("assemblies") else None


def _all():
    pe = _pe()
    return [(pid, pe.resolve(pid)) for pid in sorted(pe.PACKS)]


def _members(client, pid, **params):
    r = client.get(f"/api/proportions/{pid}", params=dict(members="true", **params))
    assert r.status_code == 200, r.text
    return r.json()


# ------------------------------------------------------------------------ which path
def test_every_pack_takes_the_path_its_own_record_implies(client):
    seen = set()
    for pid, pk in _all():
        out = _members(client, pid)
        assert out["drawing"] == _expected_drawing(pk), pid
        seen.add(out["drawing"])
        for k in NEW_KEYS:
            assert k in out, f"{pid}: {k} missing"
        assert out["kind"] == pk["kind"] and out["module_name"] == pk["module"]["name"], pid
        assert out["module_bound_to"] == pk["module"].get("equals"), pid
        assert out["at"]["module_in"] == out["module_in"], pid
    assert seen == {"stack", "assemblies", None}, \
        f"a drawing state has no pack in it ({seen}); the census below would be partly vacuous"


# ------------------------------------------------------------------------ the stack, unchanged
def test_a_stacked_pack_keeps_every_key_and_value_it_served_before():
    """The existing path, byte for byte on every pre-existing key: core.get_proportions' own
    payload, the members it always merged in, the column record, the datum and the geometry
    on the ORDER datum. The members payload may only ADD the six new keys."""
    pe, prof = _pe(), _prof()
    stacked = [(pid, pk) for pid, pk in _all() if pe.stack_for(pk)]
    assert stacked
    for pid, pk in stacked:
        for kw in ({}, {"column_diameter": 12.0}, {"module": 9.0}):
            out = corpus.proportions_with_members(pid, **kw)
            base = core.get_proportions(pid, ceiling_height=corpus.CEILING_DEFAULT_IN,
                                        opening_width=corpus.OPENING_DEFAULT_IN, **kw)
            extra = set(out) - set(base)
            assert extra <= set(NEW_KEYS) | {"column", "projection_datum", "geometry"}, extra
            for k, v in base.items():
                if k == "assemblies":
                    assert [{kk: vv for kk, vv in a.items() if kk != "members"}
                            for a in out[k]] == [
                        {kk: vv for kk, vv in a.items() if kk != "members"} for a in v], pid
                else:
                    assert out[k] == v, f"{pid} {kw}: {k} moved"
            d = pe.dimension(pk, out["module_in"], None)
            assert [a["members"] for a in out["assemblies"]] == \
                [a["members"] for a in d["assemblies"]], pid
            assert out["geometry"] == prof.pack_geometry(d, pk.get("column"),
                                                         pk.get("projection_datum")), pid
            assert "datum" not in out["geometry"], f"{pid}: the order plate got the wall datum"


def test_the_mcp_payload_is_unchanged_and_still_serves_no_assemblies_for_trim_classical():
    """MCP parity is NOT this package's. `tdl_get_proportions` serves the pack as it always
    has -- no assemblies for a pack with no column stack -- and that is asserted, not assumed,
    so the day somebody changes it the question it belongs to is named."""
    got = core.get_proportions("trim-classical")
    assert got["assemblies"] == [], (
        "core.get_proportions now serves assemblies for trim-classical; that is the MCP half "
        "of oq/mcp-proportions-serve-no-assemblies-for-non-order-packs and must be ruled there, "
        "not changed silently under the workbench's package")
    assert not set(NEW_KEYS) & set(got), "a workbench-only key leaked into the MCP payload"


# ------------------------------------------------------------------------ every drawable pack
def test_every_stackless_pack_with_assemblies_is_served_whole_on_the_wall_datum(client):
    pe = _pe()
    packs = [(pid, pk) for pid, pk in _all() if _expected_drawing(pk) == "assemblies"]
    assert packs
    faces = members = 0
    for pid, pk in packs:
        out = _members(client, pid)
        assert out["geometry"] is None, f"{pid}: a pack-level geometry on the order datum"
        assert [a["id"] for a in out["assemblies"]] == list(pk["assemblies"]), \
            f"{pid}: not the pack's own declaration order"
        for a in out["assemblies"]:
            d = pe.dimension(pk, out["module_in"], [a["id"]])
            da = d["assemblies"][0]
            assert a["members"] == da["members"], (pid, a["id"])
            assert a["members"][0]["y_bottom_in"] == 0.0, f"{pid}/{a['id']}: y not from 0"
            assert a["height_in"] == da["height_in_summed"], (pid, a["id"])
            assert a["height_in_stated"] == da["height_in_stated"], (pid, a["id"])
            assert a["sums_check"] == da["sums_check"], (pid, a["id"])
            assert a["owner"] == pe.assembly_owner(pk["id"], a["id"]), (pid, a["id"])
            g = a["geometry"]
            assert g["id"] == a["id"] and g["naked_in"] == 0.0, (pid, a["id"])
            assert g["faces"] and g["faces"][0]["x_from"] == 0.0, \
                f"{pid}/{a['id']}: the first face does not start at the wall plane"
            # one face per member, except side-by-side members, which draw only the first
            side = sum(1 for m in a["members"] if m.get("side_by_side"))
            assert len(g["faces"]) == len(a["members"]) - max(0, side - 1), (pid, a["id"])
            assert all(u["assembly"] == a["id"] for u in a["unconstructed"]), (pid, a["id"])
            faces += len(g["faces"])
            members += len(a["members"])
    assert faces <= members


def _a_stackless_pack():
    pe = _pe()
    pid = next(p for p, pk in _all() if _expected_drawing(pk) == "assemblies" and
               any(a.get("sums_check", True) for a in pk["assemblies"].values()))
    return pe, pid, pe.resolve(pid)


def test_the_drawn_height_is_the_summed_one_where_a_record_states_another():
    """DRIVEN, because no shipped record reaches it: all 50 stackless assemblies have a summed
    extent equal to their stated height (side-by-side members are given the stated height by
    `dimension()`, and check_systems check 11 refuses a stacked record that does not sum). So
    `height_in` could read either field on the corpus and nothing would tell. A copy whose
    stated height is raised and whose members are not is the case that tells: the plate draws
    the members, and `height_in` is what it draws."""
    import copy
    pe, pid, pk = _a_stackless_pack()
    aid, asm = next((a, v) for a, v in pk["assemblies"].items() if v.get("sums_check", True))
    pk = copy.deepcopy(pk)
    pk["assemblies"][aid]["height_modules"] = asm["height_modules"] * 1.25
    mod = pk["module"]["default_size_in"]
    row = next(r for r in corpus._wall_assemblies(pk, pe, mod) if r["id"] == aid)
    assert row["height_in_stated"] != row["height_in"], \
        "the driven copy did not separate the two heights; the assertion below proves nothing"
    assert row["height_in"] == round(sum(m["height_in"] for m in row["members"]), 4)
    assert row["height_in_stated"] == round(asm["height_modules"] * 1.25 * mod, 4)


def test_an_overlays_assembly_names_the_pack_that_states_it(monkeypatch):
    """DRIVEN, because no stackless pack is an overlay today (0 of 50 owners differ from the
    pack), so `owner` could be the pack's own id on the corpus and nothing would tell. An
    in-memory overlay of a real stackless pack, stating none of its assemblies, inherits them
    all -- and every one must name the BASE as its owner, which is `pe.assembly_owner`'s rule."""
    import copy
    pe, base, _ = _a_stackless_pack()
    raw = copy.deepcopy(pe.PACKS[base])
    raw["id"], raw["overlay_of"], raw["assemblies"] = "wp-14-4-driven-overlay", base, {}
    monkeypatch.setitem(pe.PACKS, raw["id"], raw)
    pk = pe.resolve(raw["id"])
    rows = corpus._wall_assemblies(pk, pe, pk["module"]["default_size_in"])
    assert rows and [r["id"] for r in rows] == list(pe.resolve(base)["assemblies"])
    assert all(r["owner"] == base for r in rows), {r["id"]: r["owner"] for r in rows}


def test_a_pack_with_nothing_to_draw_draws_nothing(client):
    empty = [pid for pid, pk in _all() if _expected_drawing(pk) is None]
    assert empty
    for pid in empty:
        out = _members(client, pid)
        assert out["assemblies"] == [] and out["geometry"] is None, pid


# ------------------------------------------------------------------------ the module IS the ceiling
def _bound():
    b = [(pid, pk) for pid, pk in _all() if pk["module"].get("equals") == "ceiling_height"]
    assert b, "no pack declares its module is the ceiling; the tests below would be vacuous"
    return b


def test_a_bound_pack_defaults_to_its_own_module_not_to_the_routes_108(client):
    for pid, pk in _bound():
        out = _members(client, pid)
        want = pk["module"]["default_size_in"]
        assert out["module_in"] == out["at"]["ceiling_height"] == want, pid
        assert out["module_bound_to"] == "ceiling_height", pid


def test_at_a_given_ceiling_the_plate_and_the_rules_describe_one_wall(client):
    """trim-classical at 108 in: the module is 108, the baseboard rule is the expression's own
    value at 108, and every member height is the default's scaled by 108 over the default --
    the plate and the table are one wall, and the slider moves both."""
    pe = _pe()
    for pid, pk in _bound():
        base = _members(client, pid)
        ceiling = 108.0
        out = _members(client, pid, ceiling_height=ceiling)
        assert out["module_in"] == out["at"]["ceiling_height"] == ceiling, pid
        k = ceiling / base["module_in"]
        assert k != 1.0, "the chosen ceiling IS the default; this test would prove nothing"
        for a, b in zip(out["assemblies"], base["assemblies"]):
            for ma, mb in zip(a["members"], b["members"]):
                assert ma["height_in"] == pytest.approx(mb["height_in"] * k, abs=1e-3), \
                    (pid, a["id"], ma["id"])
        # every rule whose expression reads the ceiling is evaluated AT the served ceiling
        readers = [r for r in out["derived_rules"] if "ceiling_height" in r["expression"]
                   and r.get("value") is not None]
        assert readers, pid
        env = {"ceiling_height": out["at"]["ceiling_height"],
               "opening_width": out["at"]["opening_width"],
               "module": out["module_in"], "part": out["part_in"]}
        for r in readers:
            try:
                want = pe.evaluate_expr(r["expression"], env)
            except Exception:
                continue                          # reads a binding `at` does not carry
            assert r["value"] == pytest.approx(want, abs=1e-3), (pid, r["target_slot"])
        base_rule = next(r for r in out["derived_rules"]
                         if r["target_slot"] == "baseboard" and r["dimension"] == "height")
        assert base_rule["value"] == pytest.approx(
            pe.evaluate_expr(base_rule["expression"], {"ceiling_height": ceiling}), abs=1e-3)


def test_the_non_members_path_passes_108_and_36_exactly_as_before(client):
    for pid in ("trim-classical", "gibbs-ionic"):
        r = client.get(f"/api/proportions/{pid}")
        assert r.status_code == 200
        assert r.json() == core.get_proportions(pid, ceiling_height=108.0, opening_width=36.0)
        r2 = client.get(f"/api/proportions/{pid}", params={"ceiling_height": 96})
        assert r2.json() == core.get_proportions(pid, ceiling_height=96.0, opening_width=36.0)


def test_an_unknown_pack_is_a_404_in_cores_own_words(client):
    r = client.get("/api/proportions/no-such-pack", params={"members": "true"})
    assert r.status_code == 404
    assert r.json()["detail"] == core.get_proportions("no-such-pack")


# ------------------------------------------------------------------------ who uses a pack
def _nodes():
    return core._data()["styles"]


def test_used_by_agrees_with_every_node_record_and_with_the_style_packs_route(client):
    """`own` is exactly the nodes whose OWN record binds the pack -- read off styles/, which is
    not the function under test -- and every delivery and every own binding is what that
    node's own /api/styles/{id}/packs says, from the same ancestor, with the same opt-in."""
    nodes = _nodes()
    for pid in ("trim-classical", "sash-light", "gibbs-ionic"):
        u = _members(client, pid)["used_by"]
        binders = sorted(n for n, rec in nodes.items()
                         if any(pb["pack"] == pid for pb in rec.get("proportion_packs") or []))
        assert u["own"] == binders, pid
        assert u["delivered"] == sorted(u["delivered"], key=lambda d: d["style"])
        assert not {d["style"] for d in u["delivered"]} & set(u["own"])
        for d in u["delivered"]:
            sp = client.get(f"/api/styles/{d['style']}/packs").json()
            opted = [x for x in sp["opted_in"] if x["pack"] == pid]
            cascaded = [g for g in sp["delivered"] if any(x["pack"] == pid for x in g["packs"])]
            if d["opted_in"]:
                assert opted and opted[0]["from"] == d["from"], (pid, d)
            else:
                assert cascaded and cascaded[0]["from"] == d["from"], (pid, d)
            assert d["opted_in"] == (pid in (nodes[d["style"]].get("inherits_packs") or []))
        applies = set(_pe().resolve(pid).get("applies_to") or [])
        reached = set(u["own"]) | {d["style"] for d in u["delivered"]}
        assert set(u["applies_to_only"]) == applies - reached, pid
        assert set(u["bound_not_in_applies_to"]) == set(u["own"]) - applies, pid


def test_used_by_on_trim_classical_is_the_opt_in_gate_at_work(client):
    """trim-classical declares `delivery: opt-in`, so EVERY delivery of it is to a node that
    names it -- a delivered row with `opted_in: false` would be the gate failing open."""
    u = _members(client, "trim-classical")["used_by"]
    assert u["delivered"], "no delivery at all; the assertion below would be vacuous"
    assert all(d["opted_in"] for d in u["delivered"])
