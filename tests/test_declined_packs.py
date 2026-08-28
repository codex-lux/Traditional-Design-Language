"""`declined_packs` — OQ 51's refusal half (WP-8.2).

The 26 August adjudication pass found that the ruling's three moves were really one: endorsing
is a line in `applies_to`, binding a different pack does not displace the wrong one (the cascade
still delivers it and the new binding merely competes on precedence), and scoping the edge was
not implementable because `inherits_kit` gates the KIT cascade and nothing gated the PACK
cascade. So a node the pack fits could be settled in a line, and a node it does not fit could
not be settled at all — and the corruption the meter exists to measure is concentrated in
exactly the cases the meter could not be moved on.

A PER-EDGE deny was designed and REFUSED on measurement, which is worth recording because the
argument for it was mine and it was wrong. Only 111 of 222 gaps had a direct lineage edge to
their delivering ancestor at all; `english-georgian`'s 40 were 4 direct and 36 transitive, so
there is no "the english-georgian edge"; a subtree deny there would have touched 26 receivers to
fix 18, undoing five of the eleven endorsements the 26 August pass had just made; and OQ 58's
edge scope is node-local anyway (`build/build.py:111` only picks up edges whose SOURCE is the
node), so mirroring it would not have given subtree semantics.

Every assertion here is mutation-checked against the code it guards.
"""
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def rk():
    return _mod("resolve_kit_d", "build/resolve_kit.py")


@pytest.fixture(scope="module")
def graph():
    return json.load(open(os.path.join(ROOT, "dist", "taxonomy.json"), encoding="utf-8"))


THE_FOUR = ("ranch-style", "craftsman-bungalow", "california-bungalow", "minimal-traditional")


def test_a_declined_pack_does_not_reach_the_node(rk, graph):
    """The mechanism, in one assertion. All four of these receive `storey-graduation` — a
    second-to-first-storey ratio — through the cascade, and all four say in their own records
    that they have one storey or one and a half."""
    for nid in THE_FOUR:
        chain = rk.chain_for(graph, nid)
        packs = rk.resolve_packs(graph, chain)
        assert "storey-graduation" not in packs, (
            f"{nid} still resolves storey-graduation despite declining it")


def test_the_decline_is_proved_against_the_undeclared_corpus(rk, graph):
    """MUTATION-CHECKED: strip the declines and the pack comes back. Without this the test
    above passes on a corpus where `storey-graduation` never reached these nodes at all, which
    would make it a tautology rather than a guard."""
    import copy
    g = copy.deepcopy(graph)
    for nid in THE_FOUR:
        g["nodes"][nid].pop("declined_packs", None)
    for nid in THE_FOUR:
        packs = rk.resolve_packs(g, rk.chain_for(g, nid))
        assert "storey-graduation" in packs, (
            f"{nid} does not receive storey-graduation even undeclared — this test is vacuous")


def test_a_node_may_not_decline_a_pack_it_binds_itself(rk, graph):
    """`resolve_packs` takes the node's own binding at chain[0], so such a decline would refuse
    nothing. It is a binding to delete, not a decline to write."""
    cpb = _mod("cpb_d", "build/check_pack_bindings.py")
    node = json.loads(json.dumps(graph["nodes"]["ranch-style"]))
    own = (node.get("proportion_packs") or [])
    assert own, "ranch-style binds nothing, so this case cannot be constructed"
    node["declined_packs"] = [{"pack": own[0]["pack"], "reason": "x", "basis": "editorial"}]
    errors = []
    cpb.check_declines(node, cpb._all_pack_ids(), graph, errors)
    assert any("BINDS it as well" in e for e in errors), errors


def test_a_decline_that_refuses_nothing_is_an_error(rk, graph):
    """The failure the check exists for: a decline naming a pack that does not reach the node
    appears in the record, counts as judged, and does nothing — which is worse than never having
    been written, because the gap now looks settled. Same shape and deliberately the same words
    as the `slots_except`-that-refuses-nothing check it sits beside."""
    cpb = _mod("cpb_d2", "build/check_pack_bindings.py")
    node = json.loads(json.dumps(graph["nodes"]["ranch-style"]))
    node["declined_packs"] = [{"pack": "moorish-arch", "reason": "x", "basis": "editorial"}]
    errors = []
    cpb.check_declines(node, cpb._all_pack_ids(), graph, errors)
    assert any("does not reach it by descent" in e for e in errors), errors


def test_a_node_record_basis_must_quote_the_node_and_the_quote_is_checked(graph):
    """`check_openings.py`'s discipline: a citation that cannot be checked is a guess wearing a
    citation. All four live declines quote their own node verbatim."""
    cpb = _mod("cpb_d3", "build/check_pack_bindings.py")
    packs = cpb._all_pack_ids()
    for nid in THE_FOUR:
        node = json.load(open(os.path.join(ROOT, "styles", f"{nid}.json"), encoding="utf-8"))
        errors = []
        cpb.check_declines(node, packs, graph, errors)
        assert not errors, (nid, errors)

    node = json.load(open(os.path.join(ROOT, "styles", "ranch-style.json"), encoding="utf-8"))
    node["declined_packs"][0]["quote"] = "a sentence this node does not contain anywhere"
    errors = []
    cpb.check_declines(node, packs, graph, errors)
    assert any("does not appear in" in e for e in errors), errors


def test_a_decline_counts_as_judged_and_not_as_unendorsed():
    """The meter's third bucket. A declined gap is JUDGED — somebody read the record and
    refused — and must never be counted as a gap nobody has looked at."""
    ci = _mod("ci_d", "build/check_inheritance.py")
    _, gaps, inherited, declines = ci.measure(ci.load())
    assert len(declines) == 10, declines
    applies = ci.applies_to_index()
    unendorsed = [t for t in gaps if t[0] not in applies.get(t[3], ())]
    judged = (len(gaps) - len(unendorsed)) + len(declines)
    assert judged == ci.RATCHET_FLOOR["judged"], (judged, ci.RATCHET_FLOOR)
    for nid, pid in declines:
        assert not any(t[0] == nid and t[3] == pid for t in gaps), (
            f"{nid} still carries a role gap attributed to the pack it declined")


def test_unendorsed_did_not_move_and_that_is_the_point():
    """FOUR CORRECT REFUSALS MOVED THE HEADLINE NUMBER BY ZERO. Each node's massing role simply
    re-attributed to the next ancestor, which nobody has judged either. That is why `judged` is
    the ratchet that may only go up and `unendorsed` is a work list rather than a score — and
    why a falling `unendorsed` does not mean a corpus getting more correct at the same rate,
    which is the objection OQ 51's own first pass raised against the ruling."""
    ci = _mod("ci_d2", "build/check_inheritance.py")
    assert ci.RATCHET["unendorsed"] == 249
    assert ci.RATCHET_FLOOR["judged"] == 48
    assert ci.RATCHET["inherited_packs"] == 3356, (
        "ten declines removed ten real deliveries; 3366 was the figure before them")


def test_the_schema_requires_a_reason_and_a_basis():
    s = json.load(open(os.path.join(ROOT, "schema", "style-node.schema.json"), encoding="utf-8"))
    dp = s["properties"]["declined_packs"]
    assert dp["items"]["required"] == ["pack", "reason", "basis"]
    assert dp["items"]["additionalProperties"] is False
    assert set(dp["items"]["properties"]["basis"]["enum"]) == {"node-record", "editorial"}


# ---------------------------------------------------------------- the adjudication tooling


def test_the_gates_table_names_files_that_still_contain_those_packs():
    """`applies_to` is a live behavioural gate in three files and NOTHING said so — not OQ 51,
    not the adjudication report, not CLAUDE.md. The 26 August pass endorsed eleven nodes into
    `storey-graduation` and thereby switched `graduation_check` ON for eleven styles, recorded
    nowhere.

    A table of gates is only worth having if it cannot quietly go false, which is WP-6.4's
    lesson: "until X lands" is a lie the moment X lands. So this asserts each pack id still
    occurs in each file the table names — a gate that MOVES fails here instead of leaving the
    table wrong."""
    ci = _mod("ci_g", "build/check_inheritance.py")
    assert ci.GATES, "the gates table is empty and this guard is vacuous"
    for pack, sites in ci.GATES.items():
        assert sites, pack
        for path, symbol, _why in sites:
            src = open(os.path.join(ROOT, path), encoding="utf-8").read()
            assert pack in src, (
                f"{path} no longer mentions {pack!r}: the gate moved and check_inheritance.py's "
                f"GATES table is now a false claim about the code")


def test_ancestors_reports_direct_edges_because_that_is_what_refused_the_edge_mechanism():
    """The DIRECT column is the flag's whole reason for existing. `english-georgian` delivers
    the largest group and almost none of it through an edge you could write a refusal on."""
    ci = _mod("ci_a", "build/check_inheritance.py")
    g = ci.load()
    _, gaps, _, _ = ci.measure(g)
    applies = ci.applies_to_index()
    unendorsed = [t for t in gaps if t[0] not in applies.get(t[3], ())]
    rows = [t for t in unendorsed if t[2] == "english-georgian"]
    assert rows, "english-georgian delivers nothing — the fixture has moved"
    direct = sum(1 for t in rows
                 if any(e.get("target") == "english-georgian"
                        for e in ((g["nodes"].get(t[0]) or {}).get("lineage") or [])))
    assert direct < len(rows) / 2, (
        f"{direct} of {len(rows)} english-georgian gaps are on a direct edge. The per-edge deny "
        f"was refused BECAUSE most are transitive; if that has changed, re-open the decision "
        f"rather than leaving this comment standing.")


def test_the_forbidden_slot_meter_is_ratcheted_separately_from_the_backlog():
    """776 (node, slot) pairs where the resolved kit binds a slot `forbidden` and a pack
    dimensions it anyway. NOT the OQ 51 backlog: it counts a kit binding overruled by a pack,
    not a role nobody bound, and declining packs will not close it — the slot is handed to the
    next pack, which the kit forbids just as much."""
    ci = _mod("ci_f", "build/check_inheritance.py")
    assert ci.FORBIDDEN_RATCHET == 776
    assert ci.FORBIDDEN_RATCHET not in (ci.RATCHET["role_gaps"], ci.RATCHET["unendorsed"],
                                        ci.RATCHET["inherited_packs"]), (
        "the forbidden-slot figure has collided with a backlog figure; they measure different "
        "things and must not be read as one number")


def test_a_decline_beats_an_inherited_slot_level_packs_ruling_and_says_so():
    """FOUND BY THE FIRST DECLINE, as a crash: `choose_pack` consults the resolved slot record's
    own `packs` block — a person's explicit ruling — BEFORE precedence, and that block cascades
    like everything else in the kit. So `ranch-style` declines `storey-graduation` on its own
    record while its `chair_rail` still carries an ANCESTOR's ruling naming that pack.

    The decline wins, because `resolve_packs` never delivers the pack and the rule does not exist
    to be chosen. But the stale ruling is real and is now printed rather than crashed on. Same
    class as OQ 87: a slot record inherited in full, including a decision the descendant has
    since made differently."""
    import subprocess, sys
    out = subprocess.run([sys.executable, "build/check_inheritance.py", "--slots", "ranch-style"],
                         cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "68 slot(s) dimensioned, 61 by a pack it never bound" in out.stdout
    assert "DECLINED by this node" in out.stdout, (
        "the contradiction between a decline and an inherited slot-level ruling is no longer "
        "surfaced — it used to be a KeyError, and silence would be worse")
    ci = _mod("ci_s", "build/check_inheritance.py")
    g = ci.load()
    rk = _mod("rk_s", "build/resolve_kit.py")
    chain = rk.chain_for(g, "ranch-style")
    kit, _ = rk.resolve_slots(g, chain, rk.scope_for(g, "ranch-style"))
    named = [sid for sid, rec in kit.items()
             if any(x.get("pack") == "storey-graduation" for x in (rec.get("packs") or []))]
    assert named, "no slot-level ruling names storey-graduation — this test is now vacuous"


# --------------------------------------------- the decline's SECOND delivery path
#
# A decline removes a pack from `resolve_packs`. It does not remove the value that pack
# already wrote into an ancestor's kit file as `kind: derived, source: <pack>`, and the
# meter built for exactly that escape -- `check_addresses.baked_vs_refused` -- could not
# see a decline at all. It recognised two refusal shapes: a row MARKED `refused_by_kit`,
# and a rule DROPPED by scope with its drop recorded. A declined pack leaves neither: it
# is simply not in `packs`, so there is no row to mark and no drop to record, and the
# pair vanished. `check_pack_bindings.check_declines` passed too, because it asks only
# whether the pack REACHES the node, which it does -- through the kit, not the cascade.
#
# So `check_inheritance.py --impact ranch-style storey-graduation` printed "It currently
# GOVERNS 1 slot(s): chair_rail" for a pack that node had already declined. That is the
# failure `check_declines`' own docstring exists to prevent, one layer down.

def _baked(nid_filter=None):
    ca = _mod("ca_bvr", "build/check_addresses.py")
    nodes = ca.style_nodes() if hasattr(ca, "style_nodes") else None
    if nodes is None:                       # go through main()'s own node source
        import json as _j
        g = _j.load(open(os.path.join(ROOT, "dist", "taxonomy.json"), encoding="utf-8"))
        nodes = [{"id": k} for k, v in g["nodes"].items()
                 if v.get("rank") in ("style", "variant")]
    hits, unjudged = ca.baked_vs_refused(nodes)
    if nid_filter:
        hits = [h for h in hits if h[0] == nid_filter]
    return hits, unjudged


def test_a_baked_value_from_a_declined_pack_is_counted_as_refused():
    hits, _ = _baked("ranch-style")
    from_declined = [h for h in hits if h[3] == "storey-graduation"]
    assert from_declined, (
        "ranch-style declines storey-graduation and still resolves baked parameters from "
        "it; baked_vs_refused counted none of them, so the decline is invisible to the one "
        "meter written for this escape")
    assert any("DECLINED" in (h[4] or "") for h in from_declined), (
        "the reason must name the decline -- a pair counted under the wrong refusal shape "
        "is a pair nobody can act on")
    slots = {h[1] for h in from_declined}
    assert "chair_rail" in slots, (
        "chair_rail/from_storey is the instance `--impact` reports as governed by the "
        "declined pack; if it is gone, re-pin this test on whatever replaced it")


def test_a_node_that_will_not_resolve_is_reported_and_never_lowers_the_ceiling():
    """`except Exception: continue`, silently, under a may-only-fall ratchet.

    A change that broke resolution on the nodes carrying the baked `projection_in` would
    have taken this count DOWN and satisfied the ratchet -- because the corpus was not
    measured, not because the collisions were fixed. The count and the reason are the
    same integer; only the state differs.
    """
    ca = _mod("ca_unj", "build/check_addresses.py")
    import json as _j
    g = _j.load(open(os.path.join(ROOT, "dist", "taxonomy.json"), encoding="utf-8"))
    nodes = [{"id": k} for k, v in g["nodes"].items()
             if v.get("rank") in ("style", "variant")]
    clean, clean_unjudged = ca.baked_vs_refused(nodes)
    assert clean_unjudged == [], f"the live corpus has unresolvable nodes: {clean_unjudged}"

    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import resolve_kit as _rk
    orig = _rk.chain_for
    victim = "ranch-style"

    def boom(graph, nid, *a, **k):
        if nid == victim:
            raise RuntimeError("simulated resolution failure")
        return orig(graph, nid, *a, **k)

    _rk.chain_for = boom
    try:
        hits, unjudged = ca.baked_vs_refused(nodes)
    finally:
        _rk.chain_for = orig
    assert [n for n, _ in unjudged] == [victim], (
        f"a node that raised was not reported as unjudged: {unjudged}")
    assert len(hits) < len(clean), "the sanity of this test depends on the victim having hits"
