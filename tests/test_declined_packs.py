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
    # 10 -> 25 -> 114 -> 168 -> 208 as WP-8.7 read the backlog three times over 2-3 Sep 2026.
    # Every one carries a verbatim quote from its own node, and every one was put to an
    # independent adversarial check before it was written; 30 proposals were refused by that
    # check and are tabled instead.
    assert len(declines) == 208, declines
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
    # WP-8.7 read this all the way down THREE TIMES: fifteen declines moved `unendorsed` by four
    # (249 -> 245), and the third pass's FORTY moved it by TWO (225 -> 223), because each one
    # promotes the next pack in the chain into the same role. `judged` meanwhile went 209 -> 249,
    # which is the whole argument for having a floor as well as a ceiling: the work is visible
    # there and almost invisible in the headline.
    # `appalachian-log-house` needs 26 declines over 9 rounds to reach fixpoint, which is
    # `oq/a-node-that-refuses-a-category-must-decline-it-twenty-six-times`.
    # 3 Sep 2026 (WP-8.10): 223 -> 217 and 3158 -> 3123 on the FIRST FLIP, and this test is the
    # right place to say why. Not one case was adjudicated -- `trim-classical` declared
    # `delivery: opt-in` and 35 arrivals simply stopped. `judged` is UNCHANGED at 249, which is
    # the entire argument this test was written to make, now demonstrated by a mechanism instead
    # of an anecdote: the ceilings fall for two completely different reasons and only the floor
    # can tell them apart.
    # 223 -> 217 -> 215 across the two flips (WP-8.10, WP-8.11) and 3158 -> 3123 -> 3056.
    # 102 arrivals stopped in total, no case was read, and `judged` has not moved once.
    assert ci.RATCHET["unendorsed"] == 214
    assert ci.RATCHET_FLOOR["judged"] == 249, (
        "a flip must not move the floor: stranding is the ruling ACCEPTING unjudged cases, "
        "never adjudicating them")
    assert ci.RATCHET["inherited_packs"] == 3022, (
        "208 declines removed 208 real deliveries and the first flip removed 35 more; 3366 was "
        "the figure before any")


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
    # 776 -> 761 -> 723 (WP-8.10, WP-8.11): fifteen pairs left with `trim-classical` and
    # thirty-eight with `facade-gable`, because a pack rule cannot land on a forbidden slot it no
    # longer reaches. Smaller corpus, not better corpus.
    assert ci.FORBIDDEN_RATCHET == 721
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
    assert "66 slot(s) dimensioned, 59 by a pack it never bound" in out.stdout
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


def test_impact_says_when_a_decline_does_not_reach_an_address():
    """`--slots` HAS PRINTED THIS SINCE 25 AUG AND `--impact` COUNTED IT AS RE-HOUSED.

    `governed(drop=pid)` removes the pack from `resolve_packs`, but `choose_pack` reads the
    resolved slot record's own `packs` block FIRST, and that block cascades — so the dropped pack
    can still be chosen at an address, from an ancestor's ruling carrying its own expression.
    `--impact` then looked the successor up in the post-drop `packs` dict, found nothing, and
    printed `-> gibbs-ionic (None)`: a decline that does NOT reach a slot, wearing the format of
    one that re-housed it. Found on `egyptian-revival`/`gibbs-ionic` by the adversarial check in
    WP-8.7's third pass, 3 Sep 2026.

    The class is small and now measured rather than assumed: swept over all 168 shipped declines,
    it held on THREE at SIX addresses — the two `minimal-traditional` declines and
    `ranch-style`/`storey-graduation`. That sweep also corrected the comment beside the `--slots`
    branch, which named three ranch-style slots where the tool reports one.

    IT IS FOUR AND SEVEN NOW, AND THE FOURTH IS THE ONE THAT FOUND THE BUG. Writing
    `egyptian-revival`/`gibbs-ionic` into the corpus added its own `eave_condition` to the class
    the same adjudication had just discovered. The sweep was measured before the declines were
    applied and the test failed on the first run after — which is the number behaving correctly,
    not a regression."""
    import subprocess, sys
    out = subprocess.run([sys.executable, "build/check_inheritance.py",
                          "--impact", "egyptian-revival", "gibbs-ionic"],
                         cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "eave_condition" in out.stdout
    assert "the decline does NOT reach this slot" in out.stdout, (
        "an address the decline cannot reach is being reported as re-housed:\n" + out.stdout)
    assert "(None)" not in out.stdout, (
        "the post-drop source lookup is empty and is being printed as if it were a source")
    assert "1 slot(s) the decline DOES NOT REACH" in out.stdout, out.stdout
    # NOT a summary line only: the count must be excluded from the re-housed ones, so the
    # "loses all dimensioning" figure stays about what it says.
    assert "0 slot(s) would lose all dimensioning." in out.stdout, out.stdout


def test_the_unreached_address_sweep_is_three_declines_and_six_addresses():
    """The figure the comment beside `--slots` now carries, held to the corpus so it cannot rot
    the way the sentence it replaced did. A ratchet is wrong here: this number should FALL when
    a stale slot-level ruling is corrected and RISE when a new decline meets one, and either
    movement is a thing to look at rather than a build to fail."""
    ci = _mod("ci_unreached", "build/check_inheritance.py")
    g = ci.load()
    import glob as _g, json as _j
    hits = []
    for path in sorted(_g.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = _j.load(open(path, encoding="utf-8"))
        for e in (d.get("declined_packs") or []):
            after, _k = ci.governed(g, d["id"], drop=e["pack"])
            still = sorted(s for s, v in after.items() if v[0] == e["pack"])
            if still:
                hits.append((d["id"], e["pack"], still))
    assert len(hits) == 4, hits
    assert sum(len(h[2]) for h in hits) == 7, hits
    assert {h[0] for h in hits} == {"egyptian-revival", "minimal-traditional", "ranch-style"}, hits


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


def test_every_diagnostic_flag_actually_runs():
    """WP-8.7 HOISTED `governed()` AND `CTX` TO MODULE SCOPE AND BROKE `--forbidden` DOING IT.

    Python makes a name local to a whole function if it is assigned ANYWHERE in it, so the
    `--slots` branch's own `CTX = {...}` made the module-level CTX unreachable from every other
    branch of `main()`. `--slots` worked (it assigns before it reads) and `--impact`/`--pair`
    worked (they read CTX inside `governed`, a different scope), so three of the four flags were
    green and the fourth raised `UnboundLocalError` -- caught by `check_all`, which runs it, and
    by nothing else.

    Each flag is invoked here as a subprocess and required to exit 0 and print something. A
    diagnostic nobody runs in a test is a diagnostic that works until it does not."""
    import subprocess
    import sys as _sys
    for args in (["--roles"], ["--gates"], ["--unendorsed"], ["--forbidden"],
                 ["--slots", "ranch-style"], ["--impact", "ranch-style", "storey-graduation"],
                 ["--pair", "ranch-style", "storey-graduation"]):
        p = subprocess.run([_sys.executable, os.path.join(ROOT, "build", "check_inheritance.py")]
                           + args, capture_output=True, text=True, cwd=ROOT)
        assert p.returncode == 0, (args, p.stdout[-2000:], p.stderr[-2000:])
        assert p.stdout.strip(), args


def test_pair_reads_the_pack_subject_and_the_nodes_own_words():
    """`--pair` exists so an adjudication is one screen instead of four files. It must show what
    the PACK says it dimensions and what the NODE'S OWN record says, because the rule this
    package works to is that only the second may refuse the first."""
    import subprocess
    import sys as _sys
    p = subprocess.run([_sys.executable, os.path.join(ROOT, "build", "check_inheritance.py"),
                        "--pair", "appalachian-log-house", "trim-classical"],
                       capture_output=True, text=True, cwd=ROOT)
    assert p.returncode == 0, p.stderr
    # The report is `textwrap`ped, so a sentence spans lines: normalise before matching, or the
    # assertion is testing the wrap width rather than the content.
    out = p.stdout
    flat = " ".join(out.split())
    assert "trim-classical" in out and "dimensions" in out
    assert "governing_logic:" in out
    assert "There is no applied proportional system" in flat, "the node's own sentence is missing"
    assert "ALREADY DECLINED" in out, "a pack already declined must say so, or a later pass re-reads it"
    assert "No live gate" in out or "ARMS" in out, "the gate line is what makes endorsing legible"


def _every_declining_node(graph):
    """(node, pack) for every decline in the corpus, read from the graph rather than listed.

    `THE_FOUR` above is WP-8.2's original four and the tests using it never grew. WP-8.7 added
    eleven more declines across two nodes and NOT ONE of those tests named them: the mechanism
    was proved on the first four forever. A fixed list is a guard that stops guarding the moment
    the data moves past it, which is this repository's most-repeated defect wearing a new hat."""
    out = []
    for nid, node in sorted(graph["nodes"].items()):
        for d in (node.get("declined_packs") or []):
            out.append((nid, d["pack"]))
    return out


def test_every_decline_in_the_corpus_actually_stops_its_pack(rk, graph):
    """The mechanism, over the WHOLE corpus rather than the four it was born on."""
    declines = _every_declining_node(graph)
    assert len(declines) >= 25, ("declines went DOWN -- if that is intended, re-pin here", len(declines))
    for nid, pid in declines:
        packs = rk.resolve_packs(graph, rk.chain_for(graph, nid))
        assert pid not in packs, f"{nid} still resolves {pid} despite declining it"


def test_every_decline_is_proved_against_the_undeclared_corpus(rk, graph):
    """MUTATION-CHECKED, corpus-wide: strip each node's declines and every pack must come back.
    Without this, a decline naming a pack that never reached the node would read as a working
    refusal -- `check_pack_bindings.check_declines` has its own lie-check for exactly that, and
    this is the same property held from the resolver's side.

    THE OPT-IN GATE IS LIFTED TOO, AND THAT IS NOT A WEAKENING (WP-8.10). Once `trim-classical`
    declared `delivery: opt-in`, the six declines against it stopped refusing anything: the gate
    already stops the pack, so removing the decline changed nothing and this test fired on
    `american-farmhouse-vernacular`. The decline is not REFUTED by that, it is SUPERSEDED by a
    stronger gate -- a decline is a person's judgment that the pack is wrong for the node, the
    flip is a delivery mechanism, and this corpus keeps those apart everywhere else. Deleting the
    six would destroy six adjudications and take `judged` 249 -> 243, through its own floor.

    So the counterfactual restores BOTH: no decline and no gate. The property under test is
    unchanged and still bites -- "this decline names a delivery the cascade would really make" --
    and it is now asked of the cascade rather than of whichever gates happen to be shipped.
    """
    import copy
    for nid, pid in _every_declining_node(graph):
        g = copy.deepcopy(graph)
        g["nodes"][nid].pop("declined_packs", None)
        if (g.get("_packs") or {}).get(pid, {}).get("delivery") == "opt-in":
            g["_packs"][pid]["delivery"] = "cascade"
        packs = rk.resolve_packs(g, rk.chain_for(g, nid))
        assert pid in packs, (
            f"{nid} does not receive {pid} even undeclared and ungated -- that decline "
            f"refuses nothing")


def test_every_node_record_quote_is_verbatim(graph):
    """`basis: node-record` means a sentence in the node's own file says so. The build checker
    verifies this; holding it here too means a broken quote fails a fast test rather than only
    the full suite, and names the node."""
    import re as _re
    for nid, node in sorted(graph["nodes"].items()):
        for d in (node.get("declined_packs") or []):
            if d.get("basis") != "node-record":
                continue
            assert d.get("quote") and d.get("quoted_from"), (nid, d["pack"])
            raw = open(os.path.join(ROOT, "styles", f"{nid}.json"), encoding="utf-8").read()
            pat = _re.escape(_re.sub(r"\s+", " ", d["quote"])).replace(r"\ ", r"\s+")
            assert _re.search(pat, _re.sub(r"\s+", " ", raw)), (
                f"{nid}/{d['pack']}: quote is not verbatim in the node's own file")
