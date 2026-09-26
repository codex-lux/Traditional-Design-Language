"""WP-14.4 (PRD §H.1, §H.2): every pack the engine can draw is served with its members and its
geometry, the module that IS the ceiling is dimensioned at the ceiling, and a pack says who
uses it.

`GET /api/proportions/{pack}?members=true` used to serve members only for the 25 packs with a
column stack, because `pe.dimension(pk, mod, None)` dimensions `stack_for(pk)` and that knows
only order assembly names -- so `trim-classical`, whose three wall sections and three casings
the same engine dimensions happily one at a time, came back with no assemblies at all.

Every expectation here is COMPUTED from the engine, the corpus or another endpoint -- no count
is written down -- and the stacked path is held to what it served before, key by key.

WP-14.18 (PRD tranche 2 §C.4) lifts tranche 1's freeze on the `tdl_get_proportions` payload for
exactly one item, MCP parity, and this file's MCP guard is RE-CUT to it rather than re-pinned:
a stackless pack lists its own assemblies with member counts, its hint names them, and no column
diameter is served without a stack or a column -- while every STACKED pack's payload is held
byte-identical by a digest derived first on a `git archive` of the base commit, `f0dc52a`.
"""
import hashlib
import json
import os

import pytest

from workbench.server import corpus

core = corpus.core

NEW_KEYS = ("drawing", "at", "module_name", "module_bound_to", "kind", "used_by", "sources")

# THE STACKED MCP PAYLOADS, BYTE FOR BYTE (WP-14.18). Derived on a `git archive` of `f0dc52a` --
# the commit before this package -- with the harness below, and reproduced on this tree before
# any edit: sha256 over every stacked pack's `core.get_proportions` payload, serialised exactly
# as mcp_server/server.py's J() serialises it, at each of STACKED_KWS. The argument sets are the
# ones valid on BOTH trees (the base took ceiling_height=108.0 as a default, so it is always
# passed explicitly or not at all). A movement here is a changed MCP payload for an order, which
# no ruling in tranche 2 permits.
STACKED_DIGEST = "7ac8e89730301b1d"
STACKED_KWS = ({}, {"column_diameter": 12.0}, {"module": 9.0},
               {"ceiling_height": 96.0, "opening_width": 42.0}, {"assembly": "cornice"},
               {"assembly": "capital", "column_diameter": 18.0}, {"include_rules": False})


def stacked_digest(get=None):
    """-> (16-hex digest, payloads hashed). `get` defaults to core.get_proportions; a test hands
    in a wrapped one to prove the pin can fail."""
    get = get or core.get_proportions
    pe = _pe()
    h, n = hashlib.sha256(), 0
    for pid in sorted(p for p in pe.PACKS if pe.stack_for(pe.resolve(p))):
        for kw in STACKED_KWS:
            out = get(pid, **kw)
            h.update(pid.encode() + b"\0" + json.dumps(kw, sort_keys=True).encode() + b"\0")
            h.update(json.dumps(out, ensure_ascii=False, indent=1).encode())
            n += 1
    return h.hexdigest()[:16], n


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


# ------------------------------------------------------------------------ MCP parity (WP-14.18)
# This block replaces WP-14.4's `test_the_mcp_payload_is_unchanged_and_still_serves_no_assemblies_
# for_trim_classical`, which asserted `assemblies == []` and said in its own message that a change
# "must be ruled there" -- in oq/mcp-proportions-serve-no-assemblies-for-non-order-packs. It was,
# on 25 Sep 2026, answer 1; the guard fired on this package's first run exactly as written, and
# is re-cut to the ruled property rather than re-pinned to the new output.

def _stackless():
    pe = _pe()
    return [(pid, pk) for pid, pk in _all() if not pe.stack_for(pk)]


def test_every_stacked_packs_mcp_payload_is_byte_identical_to_the_base():
    """THE PIN. Every stacked pack at every argument set, hashed as the MCP client receives it.
    Its premise is asserted too: a digest over nothing would hash to a constant."""
    pe = _pe()
    stacked = [p for p in pe.PACKS if pe.stack_for(pe.resolve(p))]
    assert stacked, "no stacked pack; the digest below would be over nothing"
    got, n = stacked_digest()
    assert n == len(stacked) * len(STACKED_KWS)
    assert got == STACKED_DIGEST, (
        f"a stacked pack's tdl_get_proportions payload moved ({STACKED_DIGEST} -> {got}). "
        f"Tranche 2 lifts that freeze for STACKLESS packs only (PRD §C.4); find the key that "
        f"moved on an order before touching this pin")


def test_the_pin_can_fail():
    """A digest that cannot move proves nothing. One key added to ONE stacked payload -- the shape
    a careless `axis` or `zones` pass-through would take -- must change it."""
    victim = sorted(p for p in _pe().PACKS if _pe().stack_for(_pe().resolve(p)))[0]

    def leaky(pid, **kw):
        out = core.get_proportions(pid, **kw)
        if pid == victim and out.get("assemblies"):
            out["assemblies"][0]["axis"] = "up-the-wall"
        return out
    assert stacked_digest(leaky)[0] != STACKED_DIGEST


def test_a_stackless_pack_lists_its_own_assemblies_with_member_counts():
    """Answer 1's first clause: `{id, height_modules, height_in, members: <count>, axis?, zones?}`
    for every assembly, in the pack's own declaration order, each dimensioned on its own -- the
    workbench plate's own call -- and `axis`/`zones` exactly where the pack declares them."""
    pe = _pe()
    carrying = zoned = turned = 0
    for pid, pk in _stackless():
        got = core.get_proportions(pid)
        assert [a["id"] for a in got["assemblies"]] == list(pk.get("assemblies") or {}), pid
        for a in got["assemblies"]:
            da = pe.dimension(pk, got["module_in"], [a["id"]])["assemblies"][0]
            rec = pk["assemblies"][a["id"]]
            assert a["members"] == len(da["members"]), (pid, a["id"])
            assert a["height_in"] == da["height_in_stated"], (pid, a["id"])
            assert a["height_modules"] == da["height_modules"], (pid, a["id"])
            for k in ("axis", "zones"):
                assert (k in a) == (k in rec), f"{pid}/{a['id']}: {k} served or dropped"
                if k in rec:
                    assert a[k] == rec[k], (pid, a["id"], k)
            zoned += "zones" in a
            turned += "axis" in a
        carrying += bool(got["assemblies"])
    assert carrying, "no stackless pack has assemblies; the census above is vacuous"
    assert zoned and turned, "no served assembly carries zones or an axis; the pass-through is unexercised"


def test_the_hint_names_the_packs_own_assemblies_and_never_an_order_it_lacks():
    order_words = ("cornice", "capital", "base", "entablature", "pedestal")
    for pid, pk in _stackless():
        hint = core.get_proportions(pid)["hint"]
        own = list(pk.get("assemblies") or {})
        for aid in own:
            assert aid in hint, f"{pid}: the hint does not name its own assembly {aid!r}"
        for w in order_words:
            if w not in (pk.get("assemblies") or {}):
                assert f"assembly='{w}'" not in hint, f"{pid}: the hint offers an order's {w!r}"
        if not own:
            assert "no assemblies" in hint, f"{pid}: a pack with nothing to list says so"


def test_no_column_diameter_is_served_without_a_stack_or_a_column():
    """`dimension()` divides the module by diameters-per-module for every pack, so a pack with no
    column was served one -- `trim-classical`'s 9 ft 6 in ceiling as a 19 ft shaft. Withheld in
    core exactly where there is neither a stack nor a column, on the plain call and on an
    assembly call alike, and kept wherever there is one."""
    pe = _pe()
    withheld = kept = 0
    for pid, pk in _all():
        has = bool(pe.stack_for(pk) or pk.get("column"))
        calls = [{}] + [{"assembly": a} for a in list(pk.get("assemblies") or {})[:1]]
        for kw in calls:
            got = core.get_proportions(pid, **kw)
            assert ("lower_diameter_in" in got["totals"]) == has, (pid, kw)
        withheld += not has
        kept += has
    assert withheld and kept, "one side of the rule has no pack in it"


def test_no_workbench_only_key_leaks_into_the_mcp_payload():
    """`module_bound_to` is the one key the two payloads share, and it rides on the MCP payload
    only where a pack declares `module.equals` -- with `module_from` beside it."""
    for pid, pk in _all():
        got = core.get_proportions(pid)
        leaked = set(got) & (set(NEW_KEYS) - {"module_bound_to"})
        assert not leaked, f"{pid}: workbench-only key(s) {leaked} in the MCP payload"
        bound = pk["module"].get("equals")
        assert got.get("module_bound_to") == bound, pid
        assert ("module_from" in got) == bool(bound), pid


def test_the_mcp_tool_itself_reads_zero_as_not_given():
    """The tool's signature, not only core's: `tdl_get_proportions` with no size given serves a
    bound pack at its own module and an unbound one at 108 and 36 -- the same payload core gives
    with nothing passed."""
    from workbench.server import tools
    for pid in ("trim-classical", "gibbs-ionic", "sash-light"):
        via_tool = json.loads(tools.run_tool("tdl_get_proportions", {"pack_id": pid}))
        assert via_tool == json.loads(json.dumps(core.get_proportions(pid))), pid


def test_the_detail_route_serves_the_packs_own_sources_in_its_own_order(client):
    """WP-14.15. The page's sources section could print only the authority line, because this
    route served no `sources` although most packs carry them. Held pack by pack against the
    RECORD's own list, not a count, and the premise asserted so an empty corpus cannot pass it."""
    carrying = 0
    for pid, pk in _all():
        own = [s for s in (pk.get("sources") or []) if isinstance(s, str)]
        carrying += bool(own)
        assert _members(client, pid)["sources"] == own, pid
    assert carrying > 0, "no pack carries sources, so this test has nothing to hold"


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


def _names(expr):
    import ast
    return {n.id for n in ast.walk(ast.parse(expr, mode="eval")) if isinstance(n, ast.Name)}


def _any_bound():
    b = [(pid, pk) for pid, pk in _all() if pk["module"].get("equals")]
    assert {pk["module"]["equals"] for _, pk in b} - {"ceiling_height"}, \
        "no pack binds its module to anything but the ceiling; the generic test is the ceiling one"
    return b


def test_every_bound_pack_is_worked_at_its_own_dimension_on_both_payloads(client):
    """WP-14.18: the binding is ONE spelling (`core.module_binding`) and both payloads read it.
    For every pack declaring `module.equals = V`, whatever V is: with nothing given, the module is
    the pack's own default and `module_from` says so; given V, the module IS V, the workbench's
    `at` carries V, and every rule reading V is evaluated at that same number."""
    pe = _pe()
    for pid, pk in _any_bound():
        v, want = pk["module"]["equals"], pk["module"]["default_size_in"]
        plain = core.get_proportions(pid)
        assert plain["module_in"] == want and plain["module_from"] == "default", pid
        size = want * 1.25
        for got in (core.get_proportions(pid, **{v: size}),
                    _members(client, pid, **{v: size})):
            assert got["module_in"] == size and got["module_from"] == v, pid
            readers = [r for r in got["derived_rules"]
                       if r.get("value") is not None and v in _names(r["expression"])]
            assert readers, f"{pid}: no rule reads {v}; check 19 should have refused the declaration"
            for r in readers:
                env = dict(pe.DEFAULT_BINDINGS, **{v: size, "module": size,
                                                   "part": size / got["parts"]})
                try:
                    exp = pe.evaluate_expr(r["expression"], env)
                except Exception:
                    continue
                assert r["value"] == pytest.approx(exp, abs=1e-3), (pid, r["target_slot"])
        at = _members(client, pid, **{v: size})["at"]
        assert at[v] == at["module_in"] == size, (pid, at)


def test_a_contradictory_call_is_refused_by_name_and_the_route_answers_422(client):
    """Two sizes for one quantity -- a module and a different figure for the dimension it IS --
    and a column diameter on a pack whose module is a building dimension are refused, never
    resolved by picking one. The route answers 422: the caller's to correct, not a missing pack."""
    for pid, pk in _any_bound():
        v, d = pk["module"]["equals"], pk["module"]["default_size_in"]
        both = core.get_proportions(pid, module=d, **{v: d * 1.5})
        assert both.get("refused") == ["module"] and v.replace("_", " ") in both["error"], pid
        col = core.get_proportions(pid, column_diameter=12.0)
        assert col.get("refused") == ["column_diameter"], pid
        agree = core.get_proportions(pid, module=d * 1.5, **{v: d * 1.5})
        assert "error" not in agree and agree["module_in"] == d * 1.5, pid
        for members in ("true", "false"):
            r = client.get(f"/api/proportions/{pid}",
                           params={"members": members, "module": d, v: d * 1.5})
            assert r.status_code == 422 and r.json()["detail"]["refused"] == ["module"], pid


def test_the_members_route_passes_axis_and_zones_through_exactly_where_declared(client):
    for pid, pk in _stackless():
        if not pk.get("assemblies"):
            continue
        for a in _members(client, pid)["assemblies"]:
            rec = pk["assemblies"][a["id"]]
            for k in ("axis", "zones"):
                assert (k in a) == (k in rec) and a.get(k) == rec.get(k), (pid, a["id"], k)


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


def test_the_non_members_path_is_cores_own_call_and_an_unbound_pack_still_gets_108_and_36(client):
    """RE-CUT BY WP-14.18. This route forced 108 and 36 into core, which was right for an unbound
    pack and was the 108-against-114 disagreement for a bound one: `trim-classical`'s members at
    its 114 in module and its rules at 108. It passes what it was given now and lets
    `core.module_binding` say what a missing input means. Two halves, both held: an UNBOUND pack's
    payload is exactly what the old call produced, and a BOUND pack's rules read its own module."""
    for pid in ("trim-classical", "gibbs-ionic"):
        r = client.get(f"/api/proportions/{pid}")
        assert r.status_code == 200
        assert r.json() == json.loads(json.dumps(core.get_proportions(pid)))
        r2 = client.get(f"/api/proportions/{pid}", params={"ceiling_height": 96})
        assert r2.json() == json.loads(json.dumps(core.get_proportions(pid, ceiling_height=96.0)))
    old = core.get_proportions("gibbs-ionic", ceiling_height=108.0, opening_width=36.0)
    assert client.get("/api/proportions/gibbs-ionic").json() == json.loads(json.dumps(old))
    tc = client.get("/api/proportions/trim-classical").json()
    base = next(r for r in tc["derived_rules"]
                if r["target_slot"] == "baseboard" and r["dimension"] == "height")
    assert tc["module_in"] == _pe().resolve("trim-classical")["module"]["default_size_in"]
    assert base["value"] == pytest.approx(
        _pe().evaluate_expr(base["expression"], {"ceiling_height": tc["module_in"]}), abs=1e-3), \
        "the plain route's baseboard rule is not read at the module its members are drawn at"


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
