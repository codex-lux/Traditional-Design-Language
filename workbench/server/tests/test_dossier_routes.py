"""WP-14.4 (PRD §H.3, §H.4, §H.6, §D.2): a style's packs by provenance, the dossier's section
counts, and the lineage edges' slot scope.

THE RULE UNDER THE DOSSIER IS THAT A SECTION STRIP MAY NOT PROMISE WHAT THE SECTION DOES NOT
DELIVER. So every count `/api/styles/{id}/dossier` serves is held here to the figure ITS OWN
ENDPOINT gives -- the kit's to `/api/kit`, the proportions' to `/api/styles/{id}/packs`, the
faults' to `/api/faults`, the evidence to `/api/styles` and `/api/assets` -- through the HTTP
routes a reader's surface calls, not through the function that computed the count. And a zero
count omits its section rather than listing it empty; `identify` is always first and carries no
count. Every expectation is computed; no count is written down.
"""
import json
import os
import re

import pytest

from workbench.server import corpus

core = corpus.core


def _styles():
    return core._data()["styles"]


def _one_of_each_rank():
    """The first node of every rank, by id -- so the route tests reach a tradition, a family,
    a style and a variant, which is where the rank-awareness lives."""
    out = {}
    for sid in sorted(_styles()):
        out.setdefault(_styles()[sid]["rank"], sid)
    assert set(out) >= {"tradition", "family", "style", "variant"}, out
    return sorted(out.values()) + ["tidewater-georgian"]


def _get(client, url, **params):
    r = client.get(url, params=params or None)
    assert r.status_code == 200, (url, r.status_code, r.text[:200])
    return r.json()


# ------------------------------------------------------------------------ /packs
def _a_style_whose_ancestor_delivers_out_of_alphabetical_order():
    """The first node, by id, to which one ancestor delivers two or more packs by cascade in a
    binding order that is NOT alphabetical -- chosen from `resolve_packs` and the ancestor's own
    record, never from the route under test, so the binding-order assertion has a subject a
    sort by id would get wrong."""
    rk, g = core._kit_graph()
    for sid in sorted(g.get("nodes") or {}):
        if sid not in _styles():
            continue
        opted = set(g["nodes"][sid].get("inherits_packs") or [])
        groups = {}
        for pid, rec in rk.resolve_packs(g, rk.chain_for(g, sid)).items():
            if rec["_source"] != sid and pid not in opted:
                groups.setdefault(rec["_source"], []).append(pid)
        for src, pids in groups.items():
            order = [pb["pack"] for pb in g["nodes"][src].get("proportion_packs") or []]
            bound = sorted(pids, key=lambda p: order.index(p) if p in order else len(order))
            if len(bound) > 1 and bound != sorted(bound):
                return sid
    pytest.fail("no ancestor delivers two packs out of alphabetical order; the order check is vacuous")


def test_a_styles_packs_are_the_five_lists_and_the_counts_are_their_lengths(client):
    rk, g = core._kit_graph()
    for sid in _one_of_each_rank() + [_a_style_whose_ancestor_delivers_out_of_alphabetical_order()]:
        sp = _get(client, f"/api/styles/{sid}/packs")
        assert sp["style"] == sid
        c = sp["counts"]
        assert c["own"] == len(sp["own"]) and c["opted_in"] == len(sp["opted_in"])
        assert c["withheld"] == len(sp["withheld"]) and c["declined"] == len(sp["declined"])
        assert c["delivered"] == sum(len(gr["packs"]) for gr in sp["delivered"])
        node = g["nodes"][sid]
        own_ids = {pb["pack"] for pb in node.get("proportion_packs") or []}
        assert {x["pack"] for x in sp["own"]} == own_ids, sid
        assert all(x["pack"] in (node.get("inherits_packs") or []) for x in sp["opted_in"])
        chain = rk.chain_for(g, sid)
        dists = [gr["distance"] for gr in sp["delivered"]]
        assert dists == sorted(dists) and all(chain[gr["distance"]] == gr["from"]
                                              for gr in sp["delivered"]), sid
        # within an ancestor, its packs come in THAT ancestor's own binding order (§H.3) --
        # asserted against the ancestor's record, because an alphabetical sort went green here
        # over a corpus where 598 of 693 multi-pack groups are not alphabetical (WP-14.4 harness)
        for gr in sp["delivered"]:
            order = [pb["pack"] for pb in g["nodes"][gr["from"]].get("proportion_packs") or []]
            ids = [x["pack"] for x in gr["packs"]]
            assert ids == sorted(ids, key=lambda p: order.index(p) if p in order else len(order)), \
                (sid, gr["from"], ids)
        for lst in ("own", "opted_in"):
            keys = [(x["precedence"] is None, x["precedence"] or 0, x["pack"]) for x in sp[lst]]
            assert keys == sorted(keys), (sid, lst)
        # one pack, one provenance: nothing appears in two of the five lists
        seen = [x["pack"] for x in sp["own"] + sp["opted_in"] + sp["withheld"] + sp["declined"]]
        seen += [x["pack"] for gr in sp["delivered"] for x in gr["packs"]]
        assert len(seen) == len(set(seen)), sid


def test_the_style_in_the_contract_binds_four_and_opts_into_four(client):
    """PRD §H.3's one measured sentence, re-derived: Tidewater's own and opted-in lists are its
    own record's `proportion_packs` and `inherits_packs`, and trim-classical arrives opted in
    from the ancestor that binds it."""
    node = _styles()["tidewater-georgian"]
    sp = _get(client, "/api/styles/tidewater-georgian/packs")
    assert len(sp["own"]) == len(node["proportion_packs"])
    assert {x["pack"] for x in sp["opted_in"]} == set(node["inherits_packs"])
    tc = next(x for x in sp["opted_in"] if x["pack"] == "trim-classical")
    binder = _styles()[tc["from"]]
    assert any(pb["pack"] == "trim-classical" for pb in binder["proportion_packs"])
    assert tc["from_name"] == binder["name"]


def test_declined_and_withheld_are_read_off_the_one_reader_each(client):
    rk, g = core._kit_graph()
    decliner = next(sid for sid in sorted(_styles())
                    if _styles()[sid].get("declined_packs") and sid in g["nodes"])
    sp = _get(client, f"/api/styles/{decliner}/packs")
    want = rk.refusals_for(g, decliner)
    assert [x["pack"] for x in sp["declined"]] == [d["pack"] for d in want]
    assert [x["basis"] for x in sp["declined"]] == [d["basis"] for d in want]
    assert [x["from"] for x in sp["declined"]] == [d["_would_have_come_from"] for d in want]
    withholder = next((sid for sid in sorted(_styles())
                       if sid in g["nodes"] and rk.withheld_for(g, sid)), None)
    assert withholder, "no node has a pack withheld; the withheld list is never exercised"
    sp = _get(client, f"/api/styles/{withholder}/packs")
    want = rk.withheld_for(g, withholder)
    assert [x["pack"] for x in sp["withheld"]] == list(want)
    assert all(x["why"] == want[x["pack"]]["_why"] for x in sp["withheld"])


def test_an_unknown_style_is_a_404_in_get_styles_own_words(client):
    for route in ("packs", "dossier"):
        r = client.get(f"/api/styles/not-a-style/{route}")
        assert r.status_code == 404, route
        assert r.json()["detail"] == core.get_style("not-a-style"), route


# ------------------------------------------------------------------------ /dossier
def _endpoint_counts(client, sid):
    """Each section's figure, asked of the endpoint that section will show -- never of
    corpus.style_dossier."""
    st = _get(client, f"/api/styles/{sid}", sections="lineage,constraints,exemplars,sources,"
                                                    "massing,summary")
    rank = st["summary"]["rank"]
    taxa = _get(client, "/api/phylogeny")["taxa"]
    packs = _get(client, f"/api/styles/{sid}/packs")
    faults = _get(client, "/api/faults", style=sid, limit=300)
    groupings = 0
    for gr in core._data()["groupings"].values():
        if any(sv.get("style") == sid and sv.get("present") is not False
               for sv in gr.get("style_variation") or []):
            groupings += 1
    if rank in ("style", "variant"):
        fault_count = faults["matches"]
    else:
        d = _get(client, f"/api/styles/{sid}/dossier")["faults"]
        fault_count = len(d["verdict_here"]) + len(d["lineage"])
    return {
        "members": sum(1 for t in taxa if t["member_of"] == sid),
        "lineage": len(st["lineage"]) + len(st["descendants"]),
        "kit": _get(client, f"/api/kit/{sid}")["slots_returned"],
        "proportions": sum(packs["counts"].values()),
        "plans": (len(st["massing_affinities"]) + _get(client, "/api/partis", style=sid)["count"]
                  + groupings),
        "rules": len(st["constraints"]),
        "faults": fault_count,
        "evidence": (len(st["exemplars"]) + len(st["sources"])
                     + _get(client, "/api/assets", style=sid)["matches"]),
    }


def test_every_section_count_is_its_own_endpoints_figure(client):
    for sid in _one_of_each_rank():
        dos = _get(client, f"/api/styles/{sid}/dossier")
        want = _endpoint_counts(client, sid)
        got = {s["id"]: s["count"] for s in dos["sections"]}
        assert got.pop("identify", "absent") is None, f"{sid}: identify missing or counted"
        for section, n in want.items():
            if n:
                assert got.get(section) == n, (sid, section, got.get(section), n)
            else:
                assert section not in got, f"{sid}: {section} listed at zero"


def test_sections_come_in_the_vocabularys_order_identify_first_and_no_zero_listed():
    order = corpus.dossier_sections()
    assert order[0] == "identify"
    ranks_seen = set()
    for sid in sorted(_styles()):
        secs = corpus.style_dossier(sid)["sections"]
        ids = [s["id"] for s in secs]
        assert ids[0] == "identify" and secs[0]["count"] is None, sid
        assert ids == [x for x in order if x in ids], f"{sid}: out of order {ids}"
        assert all(s["count"] for s in secs[1:]), f"{sid}: a zero-count section is listed"
        ranks_seen.add(_styles()[sid]["rank"])
    assert ranks_seen >= {"tradition", "family", "style", "variant"}


def test_a_tradition_omits_what_a_tradition_does_not_have_by_data_not_by_rule():
    """No rank table exists: a tradition has no kit slots, no rules and no packs, so those
    sections fall out of the omission rule by themselves. The one rank rule is the faults'."""
    for sid, n in sorted(_styles().items()):
        if n["rank"] != "tradition":
            continue
        dos = corpus.style_dossier(sid)
        ids = {s["id"] for s in dos["sections"]}
        if not core.resolve_kit(sid).get("slots_returned"):
            assert "kit" not in ids, sid
        if not n.get("constraints"):
            assert "rules" not in ids, sid
        f = dos["faults"]
        want = len(f["verdict_here"]) + len(f["lineage"])
        assert ("faults" in ids) == bool(want), sid


def test_the_three_fault_lists_partition_the_matches(client):
    for sid in _one_of_each_rank():
        f = _get(client, f"/api/styles/{sid}/dossier")["faults"]
        assert len(f["verdict_here"]) + len(f["lineage"]) + f["universal_count"] == f["matches"]
        assert f["matches"] == _get(client, "/api/faults", style=sid, limit=300)["matches"]
        assert not set(f["verdict_here"]) & set(f["lineage"])
        faults = core._data()["faults"]
        for fid in f["lineage"]:
            assert "universal" not in faults[fid]["applies_to"], (sid, fid)


def test_a_verdict_here_is_a_card_that_says_something_about_this_style(client):
    keys = corpus._VERDICT_KEYS
    sid = "tidewater-georgian"
    cards = {c["id"]: c for c in _get(client, "/api/faults", style=sid, limit=300)["faults"]}
    here = _get(client, f"/api/styles/{sid}/dossier")["faults"]["verdict_here"]
    assert here, "no verdict for the contract's own style; the check is vacuous"
    for fid in here:
        rec = core._data()["faults"][fid]
        assert any(k in cards[fid] for k in keys) or any(
            s["style"] == sid for s in rec.get("severity_by_style") or []), fid


def test_the_chain_is_the_member_of_ancestry_root_first(client):
    for sid in _one_of_each_rank():
        dos = _get(client, f"/api/styles/{sid}/dossier")
        chain = dos["chain"]
        n = _styles()[sid]
        if n.get("member_of"):
            assert chain[-1]["id"] == n["member_of"], sid
            assert chain[0]["rank"] == "tradition", sid
            for a, b in zip(chain, chain[1:]):
                assert _styles()[b["id"]]["member_of"] == a["id"], sid
        else:
            assert chain == [], sid


def test_members_and_buildable_descendants(client):
    for sid in _one_of_each_rank():
        dos = _get(client, f"/api/styles/{sid}/dossier")
        n = _styles()[sid]
        kids = [m["id"] for m in dos["members"]]
        assert sorted(kids) == sorted(k for k, v in _styles().items() if v.get("member_of") == sid)
        starts = [_styles()[k]["period"]["floruit_start"] for k in kids]
        assert starts == sorted(starts), sid
        if n["rank"] in ("tradition", "family"):
            assert dos["buildable_at"], sid
            assert all(b["rank"] in ("style", "variant") for b in dos["buildable_at"])
            for b in dos["buildable_at"]:                 # a transitive member of this node
                cur, hops = _styles()[b["id"]], 0
                while cur.get("member_of") != sid and hops < 8:
                    cur, hops = _styles()[cur["member_of"]], hops + 1
                assert cur.get("member_of") == sid, (sid, b["id"])
        else:
            assert dos["buildable_at"] == [], sid


def _styles_a_grouping_marks_absent():
    """Every style some grouping's `style_variation` names with `present: false` -- read off the
    corpus, because the first-of-each-rank fixture names none of them, and a mutation counting
    an ABSENT grouping went green over that fixture alone (WP-14.4's harness, mutation 30)."""
    out = sorted({sv["style"] for gr in core._data()["groupings"].values()
                  for sv in gr.get("style_variation") or [] if sv.get("present") is False})
    assert out, "no grouping marks any style absent; the discriminating half below is vacuous"
    return out


def test_plan_types_are_the_lists_the_plans_count_counts(client):
    for sid in _one_of_each_rank() + _styles_a_grouping_marks_absent():
        dos = _get(client, f"/api/styles/{sid}/dossier")
        pt = dos["plan_types"]
        n = _styles()[sid]
        assert [m["massing"] for m in pt["massing_affinities"]] == \
            [m["massing"] for m in n.get("massing_affinities") or []]
        assert [p["id"] for p in pt["partis"]] == \
            [p["id"] for p in _get(client, "/api/partis", style=sid)["partis"]]
        for gr in pt["groupings"]:
            rec = core._data()["groupings"][gr["id"]]
            sv = [x for x in rec["style_variation"] if x["style"] == sid]
            assert sv and sv[0].get("present") is not False, (sid, gr["id"])


# ------------------------------------------------------------------------ one section vocabulary
def test_the_section_order_agrees_with_every_other_spelling_that_exists():
    """PRD §D.1 spells the vocabulary in `citations.js` and `citations.py` and nowhere else.
    Until WP-14.3 this module carries a fallback; this holds it to whichever real spelling
    exists, so the fallback can never quietly become a third one."""
    from workbench.server import citations
    ours = list(corpus.dossier_sections())
    others = 0
    if hasattr(citations, "DOSSIER_SECTIONS"):
        assert list(citations.DOSSIER_SECTIONS) == ours
        others += 1
    js = os.path.join(corpus.ROOT, "workbench", "app", "src", "citations.js")
    m = re.search(r"export const DOSSIER_SECTIONS = Object\.freeze\((\[[^\]]*\])\);",
                  open(js, encoding="utf-8").read())
    if m:
        assert json.loads(m.group(1).replace("'", '"')) == ours
        others += 1
    if not others:
        pytest.skip("COULD NOT EVALUATE: neither citations.py nor citations.js spells "
                    "DOSSIER_SECTIONS yet (WP-14.3 and WP-14.5 add them)")


# ------------------------------------------------------------------------ phylogeny edges
def test_every_phylogeny_edge_carries_its_lineage_records_slot_scope(client):
    edges = _get(client, "/api/phylogeny")["edges"]
    assert all("slots" in e for e in edges)
    stated = {(n["id"], e["target"], e["type"]): e.get("slots")
              for n in _styles().values() for e in n.get("lineage") or []}
    scoped = 0
    for e in edges:
        want = stated[(e["from"], e["to"], e["type"])]
        assert e["slots"] == want, e
        scoped += want is not None
    assert scoped, "no lineage edge states a slot scope; the served key is never exercised"


# --------------------------------------------------------------- descendants (WP-14.12)
def test_a_descendant_carries_its_edges_own_flag_and_scope(client):
    """`/api/styles/{id}`'s `descendants` serves each edge's `inherits_kit` and `slots` (added by
    `corpus.style`, the route's adapter), and each is held here to what `/api/phylogeny` serves for
    the SAME edge -- the one spelling the app's `lineage/carry.js` reads. Without the flag the dossier's lineage section could only colour a
    descendant by its edge's TYPE, which is the table WP-14.11 removed from three surfaces and
    which is wrong wherever a `hybridizes_with` edge carries the kit.

    Read through the HTTP routes, for every style some edge points AT (a style no edge names has
    no descendants to check), and the premise is asserted both ways: some descendant carries and
    some does not, so a route serving one constant cannot pass."""
    edges = _get(client, "/api/phylogeny")["edges"]
    served = {(e["from"], e["to"], e["type"]): e for e in edges}
    targets = sorted({e["to"] for e in edges})
    seen = {True: 0, False: 0}
    for sid in targets:
        rows = _get(client, f"/api/styles/{sid}", sections="lineage")["descendants"]
        for d in rows:
            e = served[(d["id"], sid, d["type"])]
            assert d["inherits_kit"] is e["inherits_kit"], (sid, d, e)
            assert d["slots"] == e["slots"], (sid, d, e)
            seen[d["inherits_kit"]] += 1
    assert seen[True] and seen[False], f"every descendant reads one way: {seen}"


def test_the_descendant_flag_is_the_workbench_routes_and_not_the_mcp_tools():
    """The MCP payloads are held byte-stable, and `tdl_get_style` serves `core.get_style`'s own
    output: the addition lives in `corpus.style`, the workbench route's adapter, and the core
    function's descendants stay `{id, type}`. A move of the enrichment into core -- which is
    where it was first written -- changes an MCP tool's output and fails here."""
    with_desc = next(sid for sid in sorted(_styles())
                     if core.get_style(sid, sections=["lineage"]).get("descendants"))
    rows = core.get_style(with_desc, sections=["lineage"])["descendants"]
    assert all(set(r) == {"id", "type"} for r in rows), rows[:3]
    enriched = corpus.style(with_desc, sections=["lineage"])["descendants"]
    assert [(r["id"], r["type"]) for r in enriched] == [(r["id"], r["type"]) for r in rows]
    assert all({"inherits_kit", "slots"} <= set(r) for r in enriched)
    # and the adapter did not reach back into the core's own copy
    assert all(set(r) == {"id", "type"}
               for r in core.get_style(with_desc, sections=["lineage"])["descendants"])
