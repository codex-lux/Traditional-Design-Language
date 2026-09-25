"""WP-14.23 (tranche 2 PRD §C.6): the record pages' data, and each relation held from BOTH sides.

A record page shows its record's relations from the other side: a massing lists the styles that
name it among their massing affinities, a parti the styles it is native or lineage to, a grouping
the partis that carry it, a room the groupings that contain it. Each inverse is COMPUTED from the
forward relation, and a page whose inverse disagreed with the forward record would tell a reader
two different things about one fact depending on which page they came from. So every pair is
held here, IN BOTH DIRECTIONS, through the HTTP routes the pages call, against the forward
relation read the way the OTHER page reads it (the style dossier's plan types, a parti's own
record, a grouping's own record). A one-way test would pass over an inverse that listed too much.

And the MCP payloads the routes are built on are held byte-stable: `tdl_get_slot` and
`tdl_get_grouping` serve `core.get_slot` and `core.get_grouping`, which gain nothing.

Every expectation is computed; no count is written down.
"""
import json

from workbench.server import corpus

core = corpus.core


def _get(client, url, **params):
    r = client.get(url, params=params or None)
    assert r.status_code == 200, (url, r.status_code, r.text[:200])
    return r.json()


def _independent_resolved_specifiers(slot_id):
    """The styles whose RESOLVED kit specifies the slot, read here from `core._resolved_kit`
    with the binding rule written out rather than by calling the function under test: a
    `specified` record, or a dangling `extends` the resolver honours "as if specified"."""
    out = []
    for sid in sorted(core._data()["styles"]):
        kit = core._resolved_kit(sid) or {}
        rec = kit.get(slot_id) or {}
        b = rec.get("binding")
        if b == "specified" or (b == "extends" and rec.get("_dangling_extends")):
            out.append(sid)
    return out


# ------------------------------------------------------------------------ slots
def test_the_slots_index_serves_every_slot_once_as_get_slot_serves_it_plus_a_computed_count(client):
    D = core._data()
    got = _get(client, "/api/slots")
    rows = got["slots"]
    assert [r["id"] for r in rows] == list(D["slots"]), "the index lost, added or reordered a slot"
    assert {g["id"] for g in got["groups"]} == {s["group"] for s in D["slots"].values()}
    for r in rows:
        served = core.get_slot(r["id"])["slot"]
        extra = {k: v for k, v in r.items() if k not in served}
        assert extra == {"specified_by": r["specified_by"]}, f"{r['id']}: carries {sorted(extra)}"
        assert {k: r[k] for k in served} == served, f"{r['id']}: the row is not get_slot's slot"


def test_specified_by_is_the_resolved_count_and_the_slot_page_lists_the_same_styles(client):
    rows = {r["id"]: r for r in _get(client, "/api/slots")["slots"]}
    # A spread of slots across the groups, not one: every slot group's first slot.
    firsts = {}
    for sid, s in core._data()["slots"].items():
        firsts.setdefault(s["group"], sid)
    assert len(firsts) > 1
    for sid in firsts.values():
        want = _independent_resolved_specifiers(sid)
        page = _get(client, f"/api/slots/{sid}")
        assert page["bindings"]["specified"] == want, sid
        assert rows[sid]["specified_by"] == len(want), sid
        # the two lists are disjoint: no style both specifies and forbids one slot
        assert not set(page["bindings"]["specified"]) & set(page["bindings"]["forbidden"]), sid


def test_the_resolved_list_is_not_the_mcp_tools_own_kit_list_and_the_tool_is_unchanged(client):
    """The premise of `oq/the-slot-tool-lists-a-style-that-forbids-a-slot-as-specifying-it`: on the
    corpus as it stands, `core.get_slot`'s own-kit list and the resolved list disagree, and the
    MCP payload carries none of the workbench's additions. Measured, never assumed: were the two
    lists ever to agree everywhere the question would be answered and this would say so."""
    differs = [sid for sid in core._data()["slots"]
               if sorted(core.get_slot(sid)["specified_by_styles"]) != _independent_resolved_specifiers(sid)]
    assert differs, "the own-kit list and the resolved list agree on every slot -- close the question"
    sid = differs[0]
    page = _get(client, f"/api/slots/{sid}")
    tool = core.get_slot(sid)
    assert "bindings" not in tool, "the MCP payload gained the workbench's field"
    assert set(tool) == {"slot", "specified_by_styles", "faults_on_this_slot", "note"}
    assert page["specified_by_styles"] == tool["specified_by_styles"]
    # and the index did not write its count into core's own slot record
    corpus.slots_index()
    assert "specified_by" not in core._data()["slots"][sid]


def test_an_unknown_slot_is_a_404(client):
    assert client.get("/api/slots/no-such-slot-at-all").status_code == 404


# ------------------------------------------------------------------------ massing
def test_a_massings_styles_are_the_styles_that_name_it_in_both_directions(client):
    """The forward relation is each style's own `massing_affinities`, as the style dossier's plan
    types serve it; the inverse is the massing page's `used_by`."""
    D = core._data()
    forward = set()
    for sid in sorted(D["styles"]):
        for a in corpus.dossier_plan_types(sid)["massing_affinities"]:
            forward.add((a["massing"], sid, a["affinity"]))
    assert forward, "no style names a massing -- the sweep saw nothing"
    inverse = set()
    for mid in sorted(D["massings"]):
        page = _get(client, f"/api/massings/{mid}")
        assert page["massing"]["id"] == mid
        for u in page["used_by"]:
            inverse.add((mid, u["style"], u["affinity"]))
    assert inverse == forward, (sorted(forward - inverse)[:5], sorted(inverse - forward)[:5])


# ------------------------------------------------------------------------ parti
def test_a_partis_styles_are_the_styles_whose_plan_types_list_it_in_both_directions(client):
    """The forward relation is a style's own plan types (`dossier_plan_types`, which reads
    `core.list_partis(style=...)` and so `compose.nativity`); the inverse is the parti page's
    `nativity_by_style`. Native and lineage only: a borrowed diagram is the complement and is
    listed on neither side."""
    D = core._data()
    forward = set()
    for sid in sorted(D["styles"]):
        for p in corpus.dossier_plan_types(sid)["partis"]:
            forward.add((p["id"], sid, p["nativity"]))
    assert {n for _p, _s, n in forward} == {"native", "lineage"}, "the sweep reached one nativity only"
    inverse = set()
    for p in core._all_partis():
        page = _get(client, f"/api/partis/{p['id']}")
        for nativity, styles in page["nativity_by_style"].items():
            for sid in styles:
                inverse.add((p["id"], sid, nativity))
    assert inverse == forward, (sorted(forward - inverse)[:5], sorted(inverse - forward)[:5])


# ------------------------------------------------------------------------ grouping
def test_a_groupings_partis_are_the_partis_that_carry_it_in_both_directions(client):
    forward = {(g, p["id"]) for p in core._all_partis() for g in (p.get("groupings") or [])}
    assert forward, "no parti carries a grouping -- the sweep saw nothing"
    inverse = set()
    for gid in sorted(core._data()["groupings"]):
        page = _get(client, f"/api/groupings/{gid}")
        names = {p["id"]: p["name"] for p in core._all_partis()}
        for c in page["carried_by"]:
            assert c["name"] == names[c["id"]], c
            inverse.add((gid, c["id"]))
        assert [c["id"] for c in page["carried_by"]] == sorted(c["id"] for c in page["carried_by"])
    assert inverse == forward, (sorted(forward - inverse)[:5], sorted(inverse - forward)[:5])


def test_the_grouping_tool_is_unchanged(client):
    gid = sorted(core._data()["groupings"])[0]
    before = json.dumps(core.get_grouping(grouping_id=gid), sort_keys=True)
    _get(client, f"/api/groupings/{gid}")
    tool = core.get_grouping(grouping_id=gid)
    assert "carried_by" not in tool, "the MCP payload gained the workbench's field"
    assert json.dumps(tool, sort_keys=True) == before, "the route wrote into core's record"


# ------------------------------------------------------------------------ room
def test_a_rooms_groupings_are_the_groupings_that_contain_it_in_both_directions(client):
    D = core._data()
    forward = {(x["room"], gid) for gid, g in D["groupings"].items() for x in g["rooms"]}
    assert forward
    inverse = set()
    for rid in sorted(D["rooms"]):
        page = _get(client, f"/api/rooms/{rid}")
        for gid in page["appears_in_groupings"]:
            inverse.add((rid, gid))
    # A grouping may name a room type the catalogue does not hold; that half is a data defect
    # for check_rooms.py, and the page of a room that does not exist cannot list it.
    forward_known = {(r, g) for r, g in forward if r in D["rooms"]}
    assert inverse == forward_known, (sorted(forward_known - inverse)[:5], sorted(inverse - forward_known)[:5])
