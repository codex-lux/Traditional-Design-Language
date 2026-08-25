"""WP-4.6 -- the missing proportion packs, first tranche.

WP-4.1 bound 129 of 132 buildable nodes and produced a consolidated list of 30-odd packs the
library does not have, with which batches independently confirmed each. Two are authored here,
chosen by measured leverage rather than by order of listing:

`moorish-arch` -- OQ 30's item, and the only gap that unblocks a node with NO BINDING AT ALL.
Three separate WP-4.1 batches, working unrelated file lists, independently reported that nothing
in the library encoded a horseshoe arch, an impost block or an alfiz.

`greek-doric` -- the gap whose absence WP-4.1 had already written down as a wrong binding:
`greek-classical` was bound to `benjamin-doric` under a note calling it "the least-bad available
approximation" and listing four specific defects.
"""
import glob
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pack(pid):
    hits = [p for p in glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))
            if json.load(open(p))["id"] == pid]
    assert len(hits) == 1, (pid, hits)
    return json.load(open(hits[0]))


def node(nid):
    return json.load(open(os.path.join(ROOT, "styles", "%s.json" % nid)))


def binding(nid, pid):
    return next((b for b in (node(nid).get("proportion_packs") or []) if b["pack"] == pid), None)


# ---------------------------------------------------------------- moorish-arch


def test_the_two_nodes_that_had_no_binding_at_all_now_have_one():
    """`moorish-andalusian` and `mudejar` were left unbound by WP-4.1 on purpose, because binding
    them would have meant forcing a Vignola order onto nodes whose own text rules one out. The
    pack that removes the reason is the only thing that should ever have removed the exemption."""
    for nid in ("moorish-andalusian", "mudejar"):
        b = binding(nid, "moorish-arch")
        assert b and b["role"] == "primary", nid
        assert node(nid)["proportion_packs"], nid


def test_the_allowlist_shrank_to_the_one_node_that_still_earns_it():
    """Retiring an allowlist entry when the thing it excused is fixed is the point of having one.
    Leaving it would let the next real gap hide behind it."""
    src = open(os.path.join(ROOT, "build", "check_pack_bindings.py")).read()
    i = src.index("DELIBERATELY_UNBOUND = {")
    line = src[i:src.index("\n", i)]
    assert "egyptian-revival" in line
    assert "moorish-andalusian" not in line and "mudejar" not in line


def test_the_moorish_pack_asserts_no_column_proportion_and_says_why():
    """The finding, not an omission. At Cordoba the shafts are spolia brought to a common
    springing by the impost block, so the system has no column-height rule to state -- and every
    other order pack in this library carries a column block, so a reader who did not know that
    would take its absence for an authoring gap."""
    p = pack("moorish-arch")
    assert "column" not in p
    assert "no `column` block at all" in p["module"]["note"].lower()
    assert p["authority"]["strength"] == "reconstructed"


def test_the_impost_block_is_a_member_the_pack_will_not_let_you_drop():
    """The member most often lost when this system is imitated, and losing it turns the arcade
    into a classical one wearing a horseshoe."""
    p = pack("moorish-arch")
    ids = [m["id"] for m in p["assemblies"]["impost"]["members"]]
    assert "impost_block" in ids
    assert any("impost" in i["expression"] for i in p["invariants"])
    assert any(r["target_slot"] == "porch_support" for r in p["derived_rules"])


def test_the_horseshoe_return_is_a_band_because_the_fabric_is():
    p = pack("moorish-arch")
    r = next(x for x in p["derived_rules"] if x.get("dimension") == "return")
    assert r["range"] == [0.33, 0.5]
    assert "0.375 is a default inside it and not a measurement" in r["note"]


def test_the_moorish_pack_names_what_it_does_not_cover():
    """Muqarnas, the tile/plaster/timber stratification and the Mudejar brick corbelling are all
    real and all absent. Silence would read as coverage."""
    n = pack("moorish-arch")["notes"]
    for missing in ("muqarnas", "stratification", "corbelling"):
        assert missing in n.lower(), missing


# ---------------------------------------------------------------- greek-doric


def test_greek_doric_fixes_the_four_defects_wp41_named():
    """WP-4.1's binding note listed them precisely: 7 diameters against a 4-to-6.5 range, entasis
    at the foot, annulets in 'Roman character', mutules halved to one per triglyph."""
    g, b = pack("greek-doric"), pack("benjamin-doric")
    assert g["column"]["height_modules"] / 2 <= 6.5 < b["column"]["height_modules"] / 2
    assert g["column"]["entasis_begins_at"] > 0 and b["column"]["entasis_begins_at"] == 0
    ann = next(m for m in g["assemblies"]["capital"]["members"] if m["id"] == "annulets")
    assert "Roman character" in ann["note"] and "departure" in ann["note"]
    mut = next(r for r in g["derived_rules"] if r["target_slot"] == "modillion_dentil")
    assert mut["expression"] == "2"


def test_it_has_no_base_and_the_invariant_says_so():
    """The invariant that separates this pack from every Vignola-derived Doric in the library,
    all of which have a moulded base -- which greek-classical's own c02 makes a hard error."""
    g = pack("greek-doric")
    assert "base" not in g["assemblies"]
    inv = g["invariants"][0]
    assert "no base" in inv["statement"].lower()
    assert g["column"]["height_modules"] == (
        g["column"]["shaft_height_modules"] + g["assemblies"]["capital"]["height_modules"])


def test_benjamin_is_demoted_and_not_deprecated():
    """Both packs are true and they are not the same thing. An American Greek Revival building
    WAS built from Benjamin's plates, and a plan checked against the Parthenon alone would fail
    it for being what it is."""
    b = binding("greek-classical", "benjamin-doric")
    assert b is not None, "benjamin-doric must not be removed"
    assert b["role"] == "secondary"
    assert binding("greek-classical", "greek-doric")["role"] == "primary"
    for nid in ("greek-revival-american", "greek-revival-northern"):
        assert binding(nid, "greek-doric")["role"] == "secondary", nid


def test_the_corner_conflict_is_recorded_as_having_no_solution():
    """The one place a classical order is provably inconsistent with itself, and exactly the kind
    of thing this corpus exists to carry."""
    c = next(x for x in pack("greek-doric")["conflicts"] if "CORNER CONFLICT" in x["statement"])
    assert "no solution" in c["statement"]
    assert "contracted the corner intercolumniation" in c["resolution"]


def test_the_order_states_its_absence_of_ornament_as_a_rule():
    """Absence is this order's most-broken rule, so the range leaves no room for it."""
    r = next(x for x in pack("greek-doric")["derived_rules"]
             if x["target_slot"] == "ornament_vocabulary")
    assert r["expression"] == "0" and r["range"] == [0.0, 0.0]


# ---------------------------------------------------------------- both


@pytest.mark.parametrize("pid", ["moorish-arch", "greek-doric"])
def test_each_new_pack_marks_at_least_one_rule_as_judgment(pid):
    """check_orders.py warns when no rule is marked judgment: true -- a pack that claims to know
    everything is suspect. Both of these are reconstructions from measured fabric, so at least
    one call in each is ours."""
    assert any(r.get("judgment") for r in pack(pid)["derived_rules"])


@pytest.mark.parametrize("pid", ["moorish-arch", "greek-doric"])
def test_each_new_pack_is_reconstructed_not_canonical(pid):
    """Neither tradition codified itself. Claiming `canonical` for either would be inventing a
    treatise that does not exist."""
    assert pack(pid)["authority"]["strength"] == "reconstructed"
