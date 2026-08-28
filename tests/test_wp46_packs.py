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

`adobe-module` (second tranche, 25 Aug 2026) -- the gap FOUR STYLE NODES named in their own
binding notes, in so many words, before anyone went looking: `spanish-colonial-american`,
`new-mexico-adobe`, `california-mission-colonial` and `monterey-colonial` each said a dedicated
mass-wall/adobe module was missing from the corpus and that their numbered wall constraints had
no pack behind them. Confirmed independently by three WP-4.1 batches besides.

`opening-pointed` (second tranche) -- the opening half of WP-4.1's "Gothic Revival facade and
opening system", confirmed by PB-7a and PB-8, with PB-7a recording that `rural-gothic-villa` was
left with NO OPENING-ROLE PACK AT ALL as a direct result. The facade half was measured and found
already served by facade-picturesque on all four revival nodes; what remains of it is real for
exactly one node, `english-gothic`, and for a different reason -- see the pack's own notes.

`opening-craftsman` (second tranche) -- the opening half of WP-4.1's "Craftsman opening system and
Prairie trim family", confirmed by PB-4. The measured gap was SEVEN nodes with no opening-role
pack, not the five the list estimated; this binds five and refuses two for stated reasons.

`trim-prairie` (second tranche) -- the OTHER half of that item, and the third gap in this package
the corpus had already written into a binding note of its own. It binds one node, which is the
lowest leverage of anything here; it was built because a wrong binding is worse than a missing one,
which is the argument that justified `greek-doric` too.

`dutch-gambrel` (third tranche, 25 Aug 2026) -- WP-4.1's "Dutch gambrel roof geometry system
(break point, slope ratio, eave kick)", confirmed by PB-1a and PB-6c. It carries TWO devices, not
one, because the corpus's own records show they are independent -- and its central finding is that
three style records give the break point three different ways and none of them says from where.

`balcony-gallery` (third tranche) -- WP-4.1's "cast-iron/ironwork system", and the measurement said
cast iron is not the system. The three nodes whose records talk about ironwork most are two Monterey
variants and Regency, and the Monterey balcony is WOOD. What they share with the Creole galerie and
the Italianate porch is a horizontal deck applied to a wall, carried one of three ways, with a rail.

`stone-course` (third tranche) -- WP-4.1's "stone-coursing equivalent of brick-course", and by a
wide margin the largest item left on the list when it was measured: 60 buildable nodes describe
stone walling and 34 carry three packs or fewer, against 31 and 23 for the next-largest. It cannot
have brick-course's module, and its central rule is stated twice in the corpus, independently, in
nearly the same words.

`facade-arcade` (fourth tranche, 25 Aug 2026) -- NOT on WP-4.1's candidate list, and that is the
finding it opens with: three packs in this work package asked for it independently, two of them
under the mistaken impression it was already listed. Measured, it was the largest remaining item at
33 nodes and 24 thinly bound. It is the only pack in this package claiming `confidence: high`,
because nine unrelated records converge on its central ratio.
"""
import glob
import json
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def _register_text():
    """The whole open-question register as one string, for the tests that assert a sentence
    is somewhere in it.

    The register became a DIRECTORY on 28 Aug 2026 (WP-8.1) -- one file per question, because a
    single shared file is where two parallel sessions' answers to "what is the next id" both
    survive a merge, which happened four times in four days. `docs/open-questions.md` is a
    generated INDEX now and does not carry entry text, so a test reading it would assert against
    an empty haystack and pass vacuously -- the exact shape of the negative-assertion trap
    CLAUDE.md records ("a NEGATIVE assertion whose selector breaks inverts into a tautology").

    Each entry is rebuilt with its `<id>. ` prefix, which the files drop because the id is their
    filename. That keeps every existing assertion in this file meaningful and unchanged.
    """
    qdir = os.path.join(ROOT, "docs", "open-questions")
    parts = []
    for name in sorted(os.listdir(qdir)):
        if name == "README.md" or not name.endswith(".md"):
            continue
        text = open(os.path.join(qdir, name), encoding="utf-8").read()
        body = text.split("\n", 3)[3] if text.count("\n") >= 3 else text
        parts.append(f"{int(name[:3])}. " + body.lstrip("\n"))
    assert parts, "the register is empty -- this helper is reading the wrong place"
    return "\n\n".join(parts) + "\n\n" + open(
        os.path.join(qdir, "README.md"), encoding="utf-8").read()


def _rk():
    """resolve_kit, through modcache -- never a local by-path loader (CLAUDE.md's standing trap).
    Behavioural tests need the real module: asserting on its SOURCE protects the comment, not the
    code, which an audit demonstrated by neutering the scope filter and passing 366 tests."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    return modcache.load("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))


def _pe_mod():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    return modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))


def pack(pid):
    hits = [p for p in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json")))
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


def test_the_allowlist_shrank_to_one_node_and_then_to_none():
    """Retiring an allowlist entry when the thing it excused is fixed is the point of having one.
    Leaving it would let the next real gap hide behind it. `moorish-arch` retired two of the three;
    OQ 49's scoped binding retired the last, so the set is now empty -- and it is KEPT rather than
    deleted, because the mechanism it names is still the right answer for a node that genuinely
    fits nothing."""
    src = open(os.path.join(ROOT, "build", "check_pack_bindings.py")).read()
    assert "DELIBERATELY_UNBOUND = set()" in src
    assert "EMPTIED 25 Aug 2026 by OQ 49" in src


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
    """RE-POINTED 26 Aug 2026 (OQ 68). The band and the value it bands were one rule, and the
    engine compared a band on the RETURN AS A FRACTION OF THE RADIUS against a value in
    inches — incommensurable, and reported out of band on every evaluation. They are two
    rules now; the band lives on the ratio, and so does the sentence that explains it. The
    claim this test makes is unchanged: the return is a BAND because the fabric is."""
    p = pack("moorish-arch")
    r = next(x for x in p["derived_rules"] if x.get("dimension") == "return_ratio")
    assert r["range"] == [0.33, 0.5]
    assert r["units"] == "ratio"
    assert "0.375 is a default inside it and not a measurement" in r["note"]
    # and the rule that turns it into inches carries no band of its own any more
    dim = next(x for x in p["derived_rules"] if x.get("dimension") == "return")
    assert "range" not in dim


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


# ---------------------------------------------------------------- adobe-module


ADOBE_ASKED = ("spanish-colonial-american", "new-mexico-adobe",
               "california-mission-colonial", "monterey-colonial")


@pytest.mark.parametrize("nid", ADOBE_ASKED)
def test_every_node_that_named_the_gap_is_now_bound(nid):
    """The four nodes did not have the gap found for them -- they wrote it down themselves. A pack
    that fills a gap the corpus named and then does not bind to the nodes that named it has filled
    a different gap."""
    b = binding(nid, "adobe-module")
    assert b is not None, nid
    assert b["role"] in ("primary", "secondary"), (nid, b["role"])


@pytest.mark.parametrize("nid", ADOBE_ASKED)
def test_no_node_still_says_the_module_is_missing_from_the_corpus(nid):
    """A stale 'missing from the corpus' claim is worse than no claim: it is the corpus lying
    about itself to the next author, who will either build a second pack or believe the first one
    does not exist. Each of the four sentences was superseded in place rather than deleted, so the
    record of what was asked for stays legible beside what was delivered -- which is the same rule
    PLAN-OF-ACTION.md applies to its own work packages."""
    for b in node(nid)["proportion_packs"]:
        if b["pack"] == "adobe-module":
            continue
        note = b["note"]
        if "missing from the corpus" in note or "mass-wall gap" in note:
            # A note that QUOTES the old claim while announcing it closed is not stale -- that is
            # the supersede-in-place convention working. What must not survive is an unmarked claim.
            assert ("SUPERSEDED" in note or "CLOSED as of" in note or "AMENDED" in note
                    or "This is that pack." in note), (nid, b["pack"])


def test_the_reveal_equals_the_wall_and_that_is_the_whole_point():
    """The one figure that cannot be faked. A stucco-on-frame revival gives 5 1/2 in where the
    mass wall gives 29, and no other move on the elevation recovers it -- so the pack states the
    reveal and the wall thickness with the SAME expression rather than two figures that happen to
    agree, because two figures can drift apart and one cannot."""
    rules = {(r["target_slot"], r["dimension"]): r for r in pack("adobe-module")["derived_rules"]}
    wall = rules[("wall_thickness_masonry", "width")]
    reveal = rules[("reveal_masonry", "width")]
    assert reveal["expression"] == wall["expression"]
    assert reveal["range"] == wall["range"]


def test_the_slenderness_band_is_a_disagreement_and_not_an_average():
    """14.7.4 NMAC says ten; `california-mission-colonial`'s own record says eight. The band holds
    both because both are right for their own case -- the code assumes a bond beam the mission
    builders did not have. Averaging to nine and calling it a measurement is exactly the laundering
    this corpus forbids, so the point value is nine but the RANGE is what the rule claims."""
    r = next(x for x in pack("adobe-module")["derived_rules"]
             if x["target_slot"] == "height_proportion")
    assert r["range"] == [8.0, 10.0]
    assert "8" in r["authority_note"] and "10" in r["authority_note"]
    node_txt = json.dumps(node("california-mission-colonial"))
    assert "eight times wall thickness" in node_txt


def test_the_slenderness_rule_says_it_is_a_ceiling_and_not_a_generator():
    """The commonest misreading. For a two-adobe house wall the ratio is nowhere near binding, so
    nothing about a house's height comes from it; what sets the wall height is the viga and the
    ceiling. A rule that does not say which of those it is will be used as both."""
    r = next(x for x in pack("adobe-module")["derived_rules"]
             if x["target_slot"] == "height_proportion")
    assert "CEILING" in r["note"] and "not a generator" in r["note"]


def test_the_bracing_length_is_what_makes_the_plan_a_chain():
    """The exact analogue of the log pen's sixteen feet, and the pack's central consequence: an
    unbraced earth wall fails out of plane past about ten times its thickness, so the building is
    a chain of ~24 ft ranges whose party walls are structure. Both packs put that statement on
    `wing_strategy`, which is what makes them comparable."""
    a = next(x for x in pack("adobe-module")["derived_rules"] if x["target_slot"] == "wing_strategy")
    log = next(x for x in pack("log-module")["derived_rules"] if x["target_slot"] == "wing_strategy")
    assert a["units"] == log["units"] == "in"
    assert "CENTRAL CONSEQUENCE" in a["note"]


def test_the_base_course_is_an_invariant_because_the_wall_fails_at_the_bottom():
    """Earth walls fail from rising damp and splash-back within a foot of the ground, not from
    anything at the top. The member most often lost in imitation is the one the pack refuses to
    let go below eight inches."""
    p = pack("adobe-module")
    base = next(m for m in p["assemblies"]["wall_section"]["members"] if m["id"] == "base_course")
    assert base["height_parts"] >= 8.0
    assert any("base_course" in inv["expression"] for inv in p["invariants"])


def test_the_zapata_is_held_to_being_structural():
    """It is the portal's diagnostic member and the one revival work keeps as pure decoration,
    applied under a beam it is not carrying. The invariant is what distinguishes the two."""
    p = pack("adobe-module")
    z = next(m for m in p["assemblies"]["portal"]["members"] if m["id"] == "zapata")
    inv = next(i for i in p["invariants"] if "zapata" in i["expression"])
    floor = p["assemblies"]["portal"]["height_modules"] * p["module"]["parts"] / 12
    assert z["height_parts"] >= floor
    assert "structural member" in inv["statement"]


def test_rammed_earth_is_carried_and_the_pack_says_where_it_differs():
    """The pack's own module is a moulded brick, so the whole-brick argument that makes a New
    Mexico wall come in 14 in steps does not apply to tapia at all. Carrying rammed earth without
    saying that would make the module's discreteness look like a fact about earth walls rather
    than a fact about bricks."""
    p = pack("adobe-module")
    assert "RAMMED EARTH" in p["module"]["note"]
    wall = next(x for x in p["derived_rules"]
                if x["target_slot"] == "wall_thickness_masonry" and x["dimension"] == "width")
    assert "Rammed earth is the exception" in wall["note"]


def test_the_revival_bindings_do_not_claim_the_wall_is_earth():
    """`pueblo-revival` and `spanish-colonial-revival` are stucco on frame and the notes say so.
    Binding a mass-wall pack to them is defensible only as a statement of what they are imitating,
    and a note that does not say that is an assertion the corpus cannot support."""
    for nid in ("pueblo-revival", "spanish-colonial-revival"):
        b = binding(nid, "adobe-module")
        assert b is not None, nid
        assert b["role"] in ("secondary", "optional"), (nid, b["role"])
        assert "frame" in b["note"], nid


def test_the_glazed_fraction_defers_because_it_is_where_the_client_and_the_wall_collide():
    """Nine per cent against the 15-25 a modern house assumes. There is no defensible way to say
    from here which argument wins in a given house, so the pack supplies a start and says so --
    and names the point past which the result should stop being called an adobe proportion."""
    r = next(x for x in pack("adobe-module")["derived_rules"]
             if x["target_slot"] == "daylight_strategy")
    assert r["judgment"] is True
    assert r["range"] == [0.06, 0.12]


def test_the_pack_names_the_three_systems_it_deliberately_does_not_carry():
    """The portada/retablo ornament panel, the placita geometry, and the mud plaster's coat and
    renewal cycle. Each is left out for a stated reason; a pack that quietly stops at its own
    edge teaches the next author that the edge is the end of the subject."""
    n = pack("adobe-module")["notes"]
    for phrase in ("portada", "placita", "mud plaster"):
        assert phrase in n


def test_check_modules_addresses_assembly_members_by_id_like_check_orders_does():
    """Found while authoring: the same invariant expression was legal in an order pack and a
    NameError in a module pack, because check_orders.py's SafeEval resolved a list of dicts by
    `id` and check_modules.py's Ref did not. Two checkers over one schema field disagreeing about
    the expression language makes an author write the weaker of two true statements -- and the
    weaker one is the one that does not name the member it is about."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_cm_ref", os.path.join(ROOT, "build", "check_modules.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    r = mod.Ref({"assemblies": {"a": {"members": [{"id": "sill", "height_parts": 3.0}]}}})
    assert r.assemblies.a.members.sill.height_parts == 3.0
    with pytest.raises(AttributeError):
        r.assemblies.a.members.nosuch


@pytest.mark.parametrize("pid", ["moorish-arch", "greek-doric", "adobe-module", "opening-pointed"])
def test_each_new_pack_marks_at_least_one_rule_as_judgment(pid):
    """check_orders.py warns when no rule is marked judgment: true -- a pack that claims to know
    everything is suspect. Both of these are reconstructions from measured fabric, so at least
    one call in each is ours."""
    assert any(r.get("judgment") for r in pack(pid)["derived_rules"])


@pytest.mark.parametrize("pid", ["moorish-arch", "greek-doric", "adobe-module", "opening-pointed"])
def test_no_new_pack_claims_to_be_canonical(pid):
    """None of these traditions reduced itself to a parametric table the way Vignola did, so none
    of them may claim `canonical` -- that would be inventing a treatise. What they may claim
    differs: three are `reconstructed` from fabric and `opening-pointed` is `documented`, because
    Pugin, Rickman and Downing did write theirs down without codifying it."""
    assert pack(pid)["authority"]["strength"] in ("reconstructed", "documented")
    assert pack(pid)["authority"]["strength"] != "canonical"


# ------------------------------------------------------------- opening-pointed


GOTHIC_NODES = ("gothic-revival-american", "gothic-revival-british",
                "carpenter-gothic", "rural-gothic-villa", "english-gothic")


def test_the_node_pb7a_named_now_has_an_opening_role_pack():
    """PB-7a's finding was not that a pack was missing in the abstract -- it was that one named
    node came out of WP-4.1 with an empty role. That is the thing to assert."""
    roles = {b["role"] for b in node("rural-gothic-villa")["proportion_packs"]}
    assert "opening" in roles
    assert binding("rural-gothic-villa", "opening-pointed")["role"] == "opening"


@pytest.mark.parametrize("nid", GOTHIC_NODES)
def test_every_gothic_node_is_bound_in_the_opening_role(nid):
    b = binding(nid, "opening-pointed")
    assert b is not None and b["role"] == "opening", nid


def test_the_span_is_the_module_and_the_height_is_the_consequence():
    """The essential move of the pack. A pointed opening's height is not an independent dimension;
    it follows from the span and the ratio the head is struck at. A module defined as the height
    would make the system a table of window sizes instead of a generator."""
    m = pack("opening-pointed")["module"]
    assert m["name"].lower().startswith("the span")
    assert "not the height" in m["note"]


def test_the_strike_ratio_band_covers_drop_equilateral_and_lancet_and_stops_there():
    """Rickman's families expressed as one number: radius over span. The band stops at 2.0 because
    past a true Early English lancet the opening is ecclesiastical, and a house wearing one looks
    like a chapel -- a statement the pack makes and should be held to."""
    r = next(x for x in pack("opening-pointed")["derived_rules"]
             if x["target_slot"] == "arch" and x["dimension"] == "ratio")
    assert r["range"] == [0.75, 2.0] and r["expression"] == "1.0"
    for word in ("drop", "equilateral", "lancet"):
        assert word in r["note"]


def test_the_rise_is_the_equilateral_triangle_and_the_invariant_holds_it_there():
    """sqrt(3)/2 of the span. The pack is a generator rather than a table exactly to the extent
    that this is checked rather than written down, so it is checked twice -- once by the pack's own
    invariant and once here, against the arithmetic rather than against the stated figure."""
    import math
    p = pack("opening-pointed")
    arch = next(m for m in p["assemblies"]["pointed_opening"]["members"] if m["id"] == "arch_zone")
    assert abs(arch["height_parts"] / p["module"]["parts"] - math.sqrt(3) / 2) < 0.002
    rule = next(x for x in p["derived_rules"]
                if x["target_slot"] == "arch" and x["dimension"] == "height")
    mod = p["module"]["default_size_in"]
    assert abs(math.sqrt(mod * mod - (mod / 2) ** 2) - mod * math.sqrt(3) / 2) < 1e-9
    assert rule["units"] == "in"


def test_the_light_zone_is_a_remainder_and_the_pack_refuses_to_round_it():
    """A pointed opening is set out head-first: span, then strike ratio, then mouldings, and the
    vertical light is what is left. 17.108 parts is not a tidy number and making it one would mean
    the head no longer lands where the arch says it does."""
    p = pack("opening-pointed")
    a = p["assemblies"]["pointed_opening"]
    by = {m["id"]: m["height_parts"] for m in a["members"]}
    total = a["height_modules"] * p["module"]["parts"]
    assert abs(by["light_zone"] - (total - by["arch_zone"] - by["sill"] - by["hood_mould"])) < 1e-6
    assert by["light_zone"] != round(by["light_zone"])
    assert any("light_zone" in inv["expression"] for inv in p["invariants"])


def test_the_egress_conflict_blames_the_mullion_and_not_the_arch():
    """The obvious answer is the wrong one, and an overstated conflict is a fabricated one. Run the
    arithmetic on the pack's own default and a single-light pointed casement clears R310 with about
    10 sq ft; a two-light one fails on minimum clear WIDTH and no amount of height recovers it."""
    import math
    c = next(x for x in pack("opening-pointed")["conflicts"] if x["with"] == "egress-code")
    assert "MULLION IS FATAL AND THE ARCH IS NOT" in c["statement"]
    span = 36.0
    y20 = math.sqrt(span ** 2 - ((20.0 + span) / 2) ** 2)        # where clear width falls to 20 in
    clear_h = 2.5 * span - 3.0 - 4.5                             # less sill and hood
    area_sf = 20.0 * (clear_h - (span * math.sqrt(3) / 2 - y20)) / 144.0
    assert 9.5 < area_sf < 11.0                                  # the "about 10 sq ft" in the text
    assert 22.0 < y20 < 23.0                                     # the "22 1/2 in above the springing"


def test_the_pack_is_the_opening_half_only_and_says_why_the_facade_half_was_not_built():
    """WP-4.1's line item asks for a facade AND opening system. All four revival nodes already
    carry facade-picturesque in the facade role, so a second facade pack would have been
    duplication dressed as coverage -- which is a measurement, and it is checked here rather than
    asserted in prose only."""
    for nid in ("gothic-revival-american", "gothic-revival-british",
                "carpenter-gothic", "rural-gothic-villa"):
        assert binding(nid, "facade-picturesque"), nid
    assert pack("opening-pointed")["kind"] == "opening-system"
    assert "OPENING HALF ONLY" in pack("opening-pointed")["notes"]


def test_english_gothic_is_the_one_node_whose_facade_gap_was_real_and_it_is_now_closed():
    """RE-PINNED. `opening-pointed` stated this gap and handed it to the candidate list rather than
    binding the nearest available thing to close a count: `english-gothic` is the medieval building
    and not a revival of it, so `facade-picturesque`'s nineteenth-century argument is an anachronism
    against it. Eight packs later `facade-medieval-english` is the pack that item became, and the
    part of the assertion that still matters -- that the WRONG pack was never bound -- holds."""
    assert binding("english-gothic", "facade-picturesque") is None
    assert "english-gothic" in pack("opening-pointed")["notes"]
    facades = [b for b in node("english-gothic")["proportion_packs"] if b["role"] == "facade"]
    assert [b["pack"] for b in facades] == ["facade-medieval-english"]


def test_the_four_centred_tudor_arch_is_excluded_on_the_geometry_and_says_so():
    """It is struck from four centres with two radii, so a single strike ratio cannot express it.
    That is why the two obvious neighbours are absent from applies_to, and the absence has to be a
    stated boundary rather than an oversight the next author has to rediscover."""
    p = pack("opening-pointed")
    assert "tudor" not in p["applies_to"] and "tudor-revival" not in p["applies_to"]
    assert "FOUR-CENTRED TUDOR ARCH" in p["notes"]


def test_gothic_is_documented_where_the_other_two_are_reconstructed():
    """Pugin, Rickman, Downing and Davis wrote this one down; the Moorish and adobe systems were
    never written down at all. Neither is canonical, because none of the four reduced it to a
    parametric table the way Vignola did -- and flattening that three-way distinction to one word
    would be the easy lie."""
    assert pack("opening-pointed")["authority"]["strength"] == "documented"
    assert pack("moorish-arch")["authority"]["strength"] == "reconstructed"
    assert pack("adobe-module")["authority"]["strength"] == "reconstructed"


# ----------------------------------------------------------- opening-craftsman


CRAFTSMAN_NODES = ("craftsman", "craftsman-bungalow", "california-bungalow",
                   "prairie-school", "arts-and-crafts-american")


@pytest.mark.parametrize("nid", CRAFTSMAN_NODES)
def test_every_bound_craftsman_node_gets_the_opening_role(nid):
    b = binding(nid, "opening-craftsman")
    assert b is not None and b["role"] == "opening", nid


def test_the_module_is_the_framing_bay_and_two_nodes_name_it_from_opposite_ends():
    """The pack's one real idea. `craftsman` names 16 or 24 in on centre from the structure;
    `prairie-school` names a ~2 ft casement unit from the opening. They coincide because the
    mullion lands on a stud, which is why a Prairie band of five casements is 10 ft exactly."""
    m = pack("opening-craftsman")["module"]
    assert m["default_size_in"] == 24.0
    assert "framing bay" in m["name"].lower()
    assert "16 or 24 inches on centre" in json.dumps(node("craftsman"))
    assert "roughly 2 ft" in json.dumps(node("prairie-school"))


def test_the_head_datum_is_an_absolute_length_and_not_a_ratio():
    """Every other opening pack in the library gives an opening a proportion. This one sets one
    horizontal line and every opening dies into it, so an opening's height is the datum minus its
    sill. If this rule ever acquires a ratio, the pack has stopped being what it is."""
    r = next(x for x in pack("opening-craftsman")["derived_rules"]
             if x["target_slot"] == "window_grouping_rule" and x["dimension"] == "height")
    assert r["units"] == "in" and r["range"] == [76.0, 84.0]
    assert "THE HEAD DATUM" in r["note"]


def test_three_style_records_state_the_head_datum_independently():
    """The pack asserts the datum on the strength of the corpus agreeing with itself, so the
    agreement is what the test checks -- not the pack's own sentence about it."""
    for nid in ("craftsman", "craftsman-bungalow", "arts-and-crafts-american"):
        assert "6 ft 8 in" in json.dumps(node(nid)), nid


def test_the_assembly_puts_the_datum_where_the_records_do():
    """Two inches to the part, forty parts to the datum: 6 ft 8 in. Held by the pack's own
    invariant and recomputed here from the members rather than read off the invariant's text."""
    p = pack("opening-craftsman")
    by = {m["id"]: m["height_parts"] for m in p["assemblies"]["datum_stack"]["members"]}
    part_in = p["module"]["default_size_in"] / p["module"]["parts"]
    assert part_in == 2.0
    datum = (by["wall_below_sill"] + by["sill_band"] + by["light_zone"]) * part_in
    assert datum == 80.0
    plate = sum(by.values()) * part_in
    assert plate == 102.0                                   # 8 ft 6 in, craftsman-bungalow's figure


def test_the_porch_and_the_wall_come_to_one_plate_line():
    """Why a Craftsman porch reads as part of the house rather than attached to it: the two stacks
    are the same height, so the eave crosses both without a step."""
    p = pack("opening-craftsman")
    a = p["assemblies"]
    assert a["porch_pier"]["height_modules"] == a["datum_stack"]["height_modules"] == 4.25


def test_the_pack_records_the_datum_disagreement_instead_of_overruling_a_style_record():
    """`styles/craftsman.json` calls the porch beam the LOW datum and the heads the high one; a 7 ft
    clear porch cannot have its beam at 6 ft 8. The invariant asserts only what both accounts agree
    on -- that there are two lines and they are close -- and says why it declines to pick."""
    inv = next(i for i in pack("opening-craftsman")["invariants"]
               if "two lines" in i["statement"])
    assert "declines to assert which is on top" in inv["note"]
    assert "low datum" in json.dumps(node("craftsman"))


def test_the_single_unit_is_tall_and_the_horizontality_is_in_the_grouping():
    """The figure most often got backwards. One unit is 2:1 tall; three side by side under one head
    and one sill make the band. A designer who reaches for a wide window produces a 1950s ranch
    opening and loses the counter-rhythm."""
    r = next(x for x in pack("opening-craftsman")["derived_rules"]
             if x["target_slot"] == "window_proportion")
    assert float(r["expression"]) >= 1.5
    assert "TALL AND NARROW" in r["note"] and "grouping" in r["note"].lower()


def test_the_two_refusals_are_stated_as_findings():
    """`mission-revival` shares the interior trim and nothing about its openings. `arts-and-crafts-
    british` looks like an obvious fit and denies this pack's central assertion in its own words --
    'there is no repeating bay and no vertical alignment requirement' -- so binding it would have
    meant asserting an alignment rule against the node's explicit denial of one."""
    p = pack("opening-craftsman")
    assert "mission-revival" not in p["applies_to"]
    assert "arts-and-crafts-british" not in p["applies_to"]
    assert binding("arts-and-crafts-british", "opening-craftsman") is None
    assert "no vertical alignment requirement" in json.dumps(node("arts-and-crafts-british"))
    assert "leaded-casement-and-mullion system of its own" in p["notes"]


def test_the_prairie_only_rules_say_they_are_prairie_only():
    """The band length and the compression-and-release ceiling ratio belong to one branch. A
    bungalow has one ceiling height throughout and gets its shelter from the eave instead; giving
    it Prairie's ratio would be the pack inventing a practice for a node that does not have one."""
    r = next(x for x in pack("opening-craftsman")["derived_rules"]
             if x["target_slot"] == "ceiling_height_rule" and x["dimension"] == "ratio")
    assert "Prairie branch alone" in r["note"]
    assert "should not be given it" in r["note"]
    assert "compression" in json.dumps(node("prairie-school"))


def test_the_rafter_tail_conflict_names_the_choice_rather_than_hiding_it():
    """A true tail is the rafter run through the wall plane at every bay, so the air barrier is
    interrupted forty times. Structure or trim is a real decision and the pack refuses to let it be
    made by default -- including refusing the option of drawing one and building the other."""
    c = next(x for x in pack("opening-craftsman")["conflicts"] if x["with"] == "energy-code")
    assert c["severity"] == "blocking"
    assert "structure or trim" in c["resolution"].lower()


def test_the_prairie_trim_family_is_still_on_the_list():
    """WP-4.1 asked for two things. This is one of them, and saying so is what keeps the other from
    being quietly absorbed into a paragraph."""
    n = pack("opening-craftsman")["notes"]
    assert "THIS IS THE OPENING HALF" in n
    assert "Prairie trim family is a separate item and remains on the list" in n


@pytest.mark.parametrize("pid", ["opening-pointed", "opening-craftsman"])
def test_neither_new_opening_pack_displaced_a_facade_pack(pid):
    """Both packs were built as one half of a two-part line item, and in both cases the other half
    was measured before being built. A node that lost its facade binding to one of these would mean
    the measurement was wrong."""
    for nid in pack(pid)["applies_to"]:
        entries = node(nid)["proportion_packs"]
        opening = [e for e in entries if e["pack"] == pid]
        assert len(opening) == 1 and opening[0]["role"] == "opening", nid
        precs = [e["precedence"] for e in entries]
        assert len(precs) == len(set(precs)), nid


# ---------------------------------------------------------------- trim-prairie


def test_the_corpus_had_written_this_gap_down_too():
    """`prairie-school`'s own trim-craftsman note said no pack owned a first-principles, non-catalog
    Prairie interior system. Third time in this work package that the gap was named by the data
    before anyone went looking for it -- and, like the other two, the sentence is superseded in
    place rather than deleted."""
    b = binding("prairie-school", "trim-craftsman")
    assert b is not None
    assert "no pack here owns a first-principles, non-catalog Prairie interior system" in b["note"]
    assert "SUPERSEDED IN PART" in b["note"]


def test_the_two_trim_families_share_a_module_on_purpose():
    """The finding, not a collision. Both come out of the same American mill in the same decade and
    both are built from the same dressed 1x4 at the same quarter-inch part, so the two packs can be
    diffed member for member. What differs is what the board does."""
    a, c = pack("trim-prairie"), pack("trim-craftsman")
    assert a["module"]["default_size_in"] == c["module"]["default_size_in"] == 3.5
    assert a["module"]["parts"] == c["module"]["parts"] == 14
    assert "IDENTICAL TO `trim-craftsman`" in a["module"]["note"]


def test_one_family_overhangs_and_the_other_recesses():
    """Craftsman makes its lines with a head casing that projects past everything; Prairie makes
    them with a band held back between two proud strips. Both packs assert their own half as an
    invariant, and the pair read together is the whole distinction."""
    a = pack("trim-prairie")
    band = {m["id"]: m for m in a["assemblies"]["lintel_band"]["members"]}
    assert band["prb_band_bed"]["projection_parts"] > band["prb_band_board"]["projection_parts"]
    assert any("shadow reveals" in i["statement"] for i in a["invariants"])
    c = pack("trim-craftsman")
    assert any("overhang" in i["statement"] for i in c["invariants"])


def test_the_prairie_band_is_off_the_stock_series_and_the_craftsman_members_are_on_it():
    """A dressed 1x6 is 22 quarter-inches and a 1x8 is 29. Craftsman's head casing is 22 and its
    base board 29, exactly on the series, because that family was bought from a catalogue. The
    Prairie band is 24 -- neither -- because every Prairie house was a mill order. That is the
    cleanest separation between a bought tradition and a drawn one that this library has."""
    a = pack("trim-prairie")
    c = pack("trim-craftsman")
    band = next(m for m in a["assemblies"]["lintel_band"]["members"] if m["id"] == "prb_band_board")
    assert band["height_parts"] == 24.0
    head = next(m for m in c["assemblies"]["door_trim_head"]["members"] if m["id"] == "crf_head_board")
    base = next(m for m in c["assemblies"]["base_craftsman"]["members"] if m["id"] == "crf_base_board")
    assert head["height_parts"] == 22.0 and base["height_parts"] == 29.0
    assert a["authority"]["strength"] == "reconstructed"
    assert c["authority"]["strength"] == "documented"


def test_the_band_assembly_is_symmetrical_because_a_datum_has_no_direction():
    """Turn a Craftsman head casing over and it is obviously wrong -- the bevelled cap is
    underneath. Turn this one over and nothing has happened."""
    a = pack("trim-prairie")
    m = {x["id"]: x for x in a["assemblies"]["lintel_band"]["members"]}
    assert m["prb_band_bed"]["height_parts"] == m["prb_band_top"]["height_parts"]
    assert m["prb_band_bed"]["projection_parts"] == m["prb_band_top"]["projection_parts"]
    assert all(x["profile"] != "bevel" for x in a["assemblies"]["lintel_band"]["members"])


def test_the_head_casing_equals_the_leg_where_craftsman_insists_it_must_not():
    """There is no head: the band runs over the opening and keeps going. Any kit that resolves a
    Prairie head wider than its leg has resolved the wrong family, and the rule exists to make that
    visible rather than to be used."""
    rules = {(r["target_slot"], r["dimension"]): r for r in pack("trim-prairie")["derived_rules"]}
    assert rules[("casing", "width")]["expression"] == rules[("casing", "height")]["expression"]
    craft = {(r["target_slot"], r["dimension"]): r for r in pack("trim-craftsman")["derived_rules"]}
    assert craft[("casing", "width")]["expression"] != craft[("casing", "height")]["expression"]


def test_the_wainscot_goes_to_the_lintel_band_and_not_to_waist_height():
    """The inversion. A wainscot everywhere else in this library is a dado at 32-42 in; here the
    whole field from base band to lintel band is one surface, so it goes to 6 ft 8 and the wall
    above it is a 13 in frieze. A kit reading 36 in would put a line across a Prairie room at
    exactly the height the design most wants to leave empty."""
    r = next(x for x in pack("trim-prairie")["derived_rules"]
             if x["target_slot"] == "wainscot" and x["dimension"] == "height")
    assert r["range"][0] >= 60.0
    assert "INVERSION" in r["note"]


def test_the_strap_spacing_is_the_casement_module_from_the_opening_pack():
    """The interior half of `opening-craftsman`'s framing bay: straps in the solid wall line up with
    mullions in the window band, so the elevation reads as one grid whether it is glazed or not."""
    strap = next(x for x in pack("trim-prairie")["derived_rules"]
                 if x["target_slot"] == "wainscot" and x["dimension"] == "width")
    p = pack("trim-prairie")
    part_in = p["module"]["default_size_in"] / p["module"]["parts"]
    assert 96 * part_in == 24.0 == pack("opening-craftsman")["module"]["default_size_in"]
    assert "casement module" in strap["authority_note"]


def test_the_compression_default_is_the_lowest_compliant_height_not_the_historical_mean():
    """The historical figure runs to 6 ft 10, which is below IRC R305.1's 7 ft for a habitable room
    or a hallway. Encoding the historical mean as the default would put a non-compliant number in
    front of every user of the pack, so the default is 7 ft 0 in and the note says why."""
    r = next(x for x in pack("trim-prairie")["derived_rules"]
             if x["target_slot"] == "ceiling_height_rule")
    p = pack("trim-prairie")
    part_in = p["module"]["default_size_in"] / p["module"]["parts"]
    assert 336 * part_in == 84.0
    assert "6 ft 10 in to 7 ft 4 in" in json.dumps(node("prairie-school"))
    c = next(x for x in p["conflicts"] if x["with"] == "accessibility-code")
    assert c["severity"] == "blocking" and "R305.1" in c["statement"]


def test_the_old_pack_is_kept_rather_than_struck_because_it_describes_a_real_house():
    """Same shape as greek-doric beside benjamin-doric: one pack for what the architects drew, one
    for what the trade built. The plan-book 'Prairie box' really was trimmed out of the same
    regional catalogue sections as the bungalow next door."""
    assert "prairie-school" in pack("trim-craftsman")["applies_to"]
    assert binding("prairie-school", "trim-craftsman")["role"] == "optional"
    assert binding("prairie-school", "trim-prairie")["role"] == "interior"
    assert "benjamin-doric" in pack("trim-prairie")["notes"]


def test_the_ranch_is_refused_and_its_own_record_gives_the_reason():
    """`ranch-style` descends from prairie-school at 0.35 with inherits_kit true, but its own record
    says its trim is the same as its Minimal Traditional parent at 0.7 and draws the distinction in
    its own words: 'Prairie has a centre; the ranch has an extent'."""
    assert "ranch-style" not in pack("trim-prairie")["applies_to"]
    assert binding("ranch-style", "trim-prairie") is None
    assert "Prairie has a centre; the ranch has an extent" in json.dumps(node("ranch-style"))


def test_the_pack_states_its_own_leverage_as_the_lowest_in_the_package():
    """One node, and no movement in role coverage at all, because prairie-school already had an
    interior-role binding -- the wrong one. Saying so is what stops a one-node pack from being
    presented as coverage."""
    n = pack("trim-prairie")["notes"]
    assert "LEVERAGE, STATED PLAINLY" in n
    assert "It binds ONE node" in n
    assert len(pack("trim-prairie")["applies_to"]) == 1


def test_the_art_glass_is_left_out_and_handed_to_the_candidate_list():
    """A set-out with rules about asymmetry, colour and the placement of the few coloured pieces
    that this pack has no figures for and would have to invent."""
    assert "art glass itself" in pack("trim-prairie")["notes"]


# --------------------------------------------------------------- dutch-gambrel


def test_the_gambrel_and_the_sprung_eave_are_carried_as_two_independent_devices():
    """`hudson-valley-dutch` has a sprung eave over a STRAIGHT gable and no gambrel; the Jersey
    branch has both. Treating them as one thing called 'the Dutch roof' would have hidden that, so
    the pack names both and every rule says which device it belongs to."""
    p = pack("dutch-gambrel")
    assert "gambrel_section" in p["assemblies"] and "sprung_eave" in p["assemblies"]
    hv = json.dumps(node("hudson-valley-dutch"))
    assert "the Hudson branch uses a steep straight gable" in hv
    assert "spring eave" in hv or "sweep radius" in hv
    b = binding("hudson-valley-dutch", "dutch-gambrel")
    assert b["role"] == "secondary"
    assert "BOUND FOR THE EAVE AND NOT FOR THE GAMBREL" in b["note"]


def test_the_break_point_states_a_datum_because_the_corpus_does_not():
    """The pack's central finding. Two records say 'break at 55-70 percent of the half-span' and one
    says '55-65 percent of the total roof height'; neither says from where. Read naively as
    from-the-eave the first is wrong by nearly a factor of two."""
    r = next(x for x in pack("dutch-gambrel")["derived_rules"]
             if x["target_slot"] == "roof_form" and x["dimension"] == "width")
    assert "MEASURED HORIZONTALLY FROM THE OUTSIDE FACE OF THE WALL" in r["note"]
    for nid in ("dutch-colonial-american", "new-jersey-dutch-gambrel"):
        assert "break at 55\u201370% of the half-span" in json.dumps(node(nid)) \
            or "55–70% of the half-span" in json.dumps(node(nid), ensure_ascii=False), nid
    assert "55-65 percent of the total roof height" in json.dumps(node("dutch-colonial-revival"))


def test_the_reconciled_break_satisfies_every_band_all_three_records_give():
    """Not asserted from the pack's prose -- recomputed. At the encoded defaults the break must land
    inside the colonial 55-70% (measured from the ridge) AND the revival's 55-65% of roof height,
    with both slopes inside every stated band. If those cannot all hold at once the reconciliation
    is wrong and the pack is guessing."""
    import math
    p = pack("dutch-gambrel")
    S = p["module"]["default_size_in"]
    rules = {(r["target_slot"], r["dimension"]): r for r in p["derived_rules"]}
    f = 0.35                                             # module * 0.35, from the eave
    tan_lo = float(rules[("roof_pitch", "gambrel_lower_slope")]["expression"])
    tan_up = float(rules[("roof_pitch", "upper_ratio")]["expression"])
    h_break = f * S * tan_lo
    H = h_break + (1 - f) * S * tan_up
    assert 0.55 <= (1 - f) <= 0.70                       # colonial band, measured from the ridge
    assert 0.55 <= h_break / H <= 0.65                   # revival band, as a height fraction
    assert 60.0 <= math.degrees(math.atan(tan_lo)) <= 72.0
    assert 18.0 <= math.degrees(math.atan(tan_up)) <= 30.0
    assert 0.75 <= H / S <= 1.20                         # and the roof-height-to-half-span band


def test_height_modules_is_the_roof_proportion_itself():
    """Because the module is the half-span, the section's height in modules is not an arbitrary
    number -- it IS roof height over half-span, so nothing else has to be stated to know how tall
    the roof is."""
    import math
    p = pack("dutch-gambrel")
    sec = p["assemblies"]["gambrel_section"]
    total = sum(m["height_parts"] for m in sec["members"])
    assert abs(total / p["module"]["parts"] - sec["height_modules"]) < 1e-9
    ratio = next(x for x in p["derived_rules"]
                 if x["target_slot"] == "height_proportion" and x["dimension"] == "roof_height_over_half_span")
    assert float(ratio["expression"]) == sec["height_modules"]


def test_the_colonial_has_no_shed_dormer_and_the_count_says_zero():
    """`dutch-colonial-american`'s own words: the revival 'fixed on the gambrel roof and the
    full-width shed dormer -- a combination that almost never occurs in the colonial original'. Same
    move greek-doric makes with ornament, and for the same reason: absence is the broken rule."""
    r = next(x for x in pack("dutch-gambrel")["derived_rules"]
             if x["target_slot"] == "dormer" and x["dimension"] == "count")
    assert r["expression"] == "0" and r["range"][0] == 0.0
    assert "almost never occurs in the colonial original" in json.dumps(node("dutch-colonial-american"))


def test_every_revival_only_rule_is_labelled_as_one():
    """The pack carries two regimes and must never let a consumer take one for the other. Each of
    the three shed-dormer rules is the revival's alone."""
    revival = [x for x in pack("dutch-gambrel")["derived_rules"]
               if x["target_slot"] == "dormer" and x["dimension"] != "count"]
    assert len(revival) == 3
    assert all(r["note"].startswith("REVIVAL RULE") for r in revival)


def test_the_two_regimes_split_the_plate_height_band():
    """Colonial 7-9 ft against revival 9-12 ft, and the band holds both rather than averaging them.
    The plate is the single change that separates a one-and-a-half-storey house from a two-storey
    one wearing the same roof."""
    r = next(x for x in pack("dutch-gambrel")["derived_rules"]
             if x["target_slot"] == "height_proportion" and x["dimension"] == "height")
    assert r["range"] == [84.0, 144.0]
    assert "makes it a full second storey, which the originals never did" in \
        json.dumps(node("dutch-colonial-revival"))


def test_the_upper_slope_gets_a_named_dimension_with_a_precedent():
    """A gambrel has two pitches and the ontology has one roof_pitch slot. Naming the dimension is
    better than inventing a second slot for the second half of one roof, and moorish-arch set the
    precedent with `return`. A consumer reading only `ratio` gets the lower slope, which is the
    right default because it is the one that shows."""
    p = pack("dutch-gambrel")
    dims = {r["dimension"] for r in p["derived_rules"] if r["target_slot"] == "roof_pitch"}
    assert dims == {"gambrel_lower_slope", "upper_ratio"}   # `ratio` renamed by OQ 48
    assert any(r["dimension"] == "return" for r in pack("moorish-arch")["derived_rules"])


def test_the_sweep_must_start_below_the_plate_or_it_is_an_ogee():
    """A sweep beginning at the plate curves the entire lower slope and gives a roof from a
    different tradition. Held by an invariant because it is hard to see on a drawing and obvious on
    a building."""
    p = pack("dutch-gambrel")
    inv = next(i for i in p["invariants"] if "begins below the plate" in i["statement"])
    tail = next(m for m in p["assemblies"]["sprung_eave"]["members"] if m["id"] == "tail_straight")
    assert tail["height_parts"] >= 1.5
    assert "ogee" in inv["note"]


def test_the_h_bent_is_left_to_timber_bay():
    """Two packs asserting one number is how a corpus starts disagreeing with itself. timber-bay
    owns the 8-12 ft bent spacing and stays bound primary on both colonial nodes."""
    p = pack("dutch-gambrel")
    assert not any(r["target_slot"] == "wing_strategy" for r in p["derived_rules"])
    assert "`timber-bay` owns it" in p["notes"]
    for nid in ("dutch-colonial-american", "hudson-valley-dutch"):
        assert binding(nid, "timber-bay") is not None, nid


def test_the_gable_grammar_item_is_not_reduced_by_this_pack():
    """A gable profile is an elevation outline and a gambrel is a roof section. Nothing here helps
    with a holbol curve or a bell gable's shoulders, and saying so stops the candidate-list item
    from looking closed."""
    p = pack("dutch-gambrel")
    assert "does NOT reduce it" in p["notes"]
    assert binding("dutch-urban-gable-house", "dutch-gambrel") is None


def test_multiple_primary_bindings_are_an_established_pattern_not_an_accident():
    """Two of the Dutch nodes now carry this pack primary beside timber-bay -- the roof and the
    frame. That is deliberate, and `charleston-georgian` carried three primaries long before this
    package, so the pattern is the corpus's and not a new invention."""
    import glob as _glob
    multi = []
    for f in sorted(_glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = json.load(open(f))
        if len([e for e in d.get("proportion_packs") or [] if e["role"] == "primary"]) > 1:
            multi.append(d["id"])
    assert "charleston-georgian" in multi
    assert {"dutch-colonial-american", "new-jersey-dutch-gambrel"} <= set(multi)


# ------------------------------------------------------------- balcony-gallery


def test_the_system_is_the_balcony_and_not_the_iron():
    """The measurement. Ranked by how much their records talk about ironwork the corpus puts two
    Monterey variants and Regency at the top -- and the Monterey balcony is wood. So the pack is
    named for the deck, not the material, and iron is one of the materials it is made in."""
    p = pack("balcony-gallery")
    assert "balcony" in p["name"].lower() and "iron" not in p["name"].lower()
    assert "cast iron is not the system" in p["notes"]
    mont = json.dumps(node("monterey-revival"))
    assert "iron or turned-wood balcony rail" in mont


def test_depth_follows_carrying_strategy_and_gets_three_rules_not_one():
    """The central claim. Hung on brackets: 30-48 in. Cantilevered on the floor joists: 5-8 ft.
    Posted to grade: 6-14 ft. The three bands barely overlap, and a designer who wants an 8 ft
    Monterey balcony has to add posts and has thereby changed the style."""
    rules = {(r["target_slot"], r["dimension"]): r for r in pack("balcony-gallery")["derived_rules"]}
    bracket = rules[("eave_condition", "projection")]["range"]
    cantilever = rules[("porch_depth", "projection")]["range"]
    posted = rules[("porch_depth", "width")]["range"]
    assert bracket == [30.0, 48.0]
    assert cantilever == [60.0, 96.0]
    assert posted[1] > cantilever[1] and posted[0] < cantilever[1]
    assert bracket[1] < cantilever[0]          # the bracket regime does not reach the cantilever one


def test_the_cantilever_ratio_is_a_structural_rule_the_corpus_states_as_a_proportion():
    """`monterey-colonial` gives the balcony as 'roughly one-fifth to one-quarter of the building
    depth'. That is the cantilever-to-backspan limit found by feel: the joists run the depth of the
    house, so the balcony's backspan is the building, and one third is where uplift starts."""
    r = next(x for x in pack("balcony-gallery")["derived_rules"]
             if x["target_slot"] == "porch_depth" and x["dimension"] == "ratio")
    assert r["range"] == [0.18, 0.33]
    assert 0.20 <= float(r["expression"]) <= 0.25       # inside the corpus's own one-fifth to one-quarter
    assert "one-fifth to one-quarter of the building depth" in json.dumps(node("monterey-colonial"))


def test_two_traditions_give_the_bracket_regime_the_same_band_independently():
    """A Louisiana abat-vent on iron rods and a Brighton cast-iron balconette look nothing alike and
    are the same structure at the same depth. Neither record mentions the other."""
    creole = json.dumps(node("creole-cottage-vernacular"))
    regency = json.dumps(node("regency"))
    assert "abat-vent projecting 30" in creole and "with no posts" in creole
    assert "900-1200 mm" in regency or "900\u20131200" in regency
    r = next(x for x in pack("balcony-gallery")["derived_rules"]
             if x["target_slot"] == "eave_condition")
    assert r["range"][0] <= 35.4 and r["range"][1] >= 47.2   # holds the metric Regency band too


def test_the_floating_deck_is_held_as_a_ratio_so_thickening_it_costs_something():
    """'The balcony floats' as a number: the deck projects more than ten times its own depth. A
    designer who thickens the edge to hide a waterproof build-up and an insulated soffit watches
    that fall toward four to one, and the style's diagnostic tell goes with it."""
    p = pack("balcony-gallery")
    j = next(m for m in p["assemblies"]["cantilever_edge"]["members"] if m["id"] == "joist_end")
    assert j["projection_parts"] >= j["height_parts"] * 6
    assert any("thin for its reach" in i["statement"] for i in p["invariants"])
    assert "the balcony floats" in json.dumps(node("monterey-colonial"))


def test_the_guard_conflict_gives_both_numbers_and_both_failures():
    """The rail is too low AND the panel has holes in it, and the two need different answers. Square
    pickets at a 4 in pitch pass the sphere rule; a cast anthemion panel does not, and the pack
    refuses to redesign the pattern to make it."""
    c = next(x for x in pack("balcony-gallery")["conflicts"] if x["with"] == "egress-code")
    assert c["severity"] == "blocking"
    assert "36 in" in c["statement"] and "4 in sphere" in c["statement"]
    assert "never redesign the pattern" in c["resolution"].lower()
    pitch = next(x for x in pack("balcony-gallery")["derived_rules"]
                 if x["target_slot"] == "porch_rail" and x["dimension"] == "spacing")
    width = next(x for x in pack("balcony-gallery")["derived_rules"]
                 if x["target_slot"] == "porch_rail" and x["dimension"] == "width")
    p = pack("balcony-gallery")
    part_in = p["module"]["default_size_in"] / p["module"]["parts"]
    gap = 1 * part_in - 0.44 * part_in                  # pitch less baluster section
    assert gap < 4.0                                    # the historical picket railing already passes


def test_the_galerie_roof_break_is_a_position_rule_like_the_gambrels():
    """'Main roof 40-50 degrees; galerie slope 20-30 degrees; break at the outer wall plane.' The
    break's POSITION is the rule, and a gallery roof carried down from the ridge at one pitch is a
    different building -- the same class of finding as dutch-gambrel's."""
    import math
    r = next(x for x in pack("balcony-gallery")["derived_rules"]
             if x["target_slot"] == "roof_pitch")
    assert 20.0 <= math.degrees(math.atan(float(r["expression"]))) <= 30.0
    assert "break at the outer wall plane" in json.dumps(node("french-colonial-american"))
    assert "break at the outer wall plane" in r["authority_note"]


def test_the_floor_length_window_is_stated_by_two_unrelated_traditions():
    """It is what the balcony is for. Regency's sash goes to the floor so a person can walk out onto
    the iron; the Creole casement pair does the same onto the galerie, and neither has heard of the
    other."""
    r = next(x for x in pack("balcony-gallery")["derived_rules"]
             if x["target_slot"] == "special_window")
    assert "Floor-length windows" in json.dumps(node("regency")) \
        or "floor-length windows" in json.dumps(node("regency"))
    assert "full-height French casement doors" in json.dumps(node("french-colonial-american"))
    assert r["range"][0] >= 72.0


def test_the_ornament_half_of_the_item_is_left_open():
    """WP-4.1 asked for a cast-iron/ironwork system. This closes the dimensional half. The anthemion,
    lyre, heart and trellis patterns, the New Orleans foliate panels and PB-6a's wrought grilles are
    a pattern repertoire, not a proportional system -- left on the list on the same principle that
    kept muqarnas out of moorish-arch."""
    n = pack("balcony-gallery")["notes"]
    assert "WHAT IS NOT CLOSED" in n
    assert "anthemion" in n and "moorish-arch" in n
    assert "muqarnas" in pack("moorish-arch")["notes"]


def test_the_two_refusals_name_what_governs_instead():
    """A Greek Revival plantation's two-tier gallery is a colonnade with entasis, which
    benjamin-doric already governs and which italianate-american's own diagnostic explicitly
    excludes. A Swiss chalet's Lauben is a real gallery and its own candidate item."""
    p = pack("balcony-gallery")
    for nid in ("greek-revival-southern-plantation", "swiss-chalet"):
        assert nid not in p["applies_to"]
        assert binding(nid, "balcony-gallery") is None, nid
    assert "never classical columns with entasis" in json.dumps(node("italianate-american"))
    assert binding("greek-revival-southern-plantation", "benjamin-doric") is not None


def test_the_head_bracket_carries_the_same_warning_as_the_zapata():
    """Both shorten a beam's span and turn a corner, and both survive into imitation as pure
    decoration applied under a beam they are not carrying. Both packs hold them with an invariant."""
    b = pack("balcony-gallery")
    a = pack("adobe-module")
    assert any("head bracket reaches" in i["statement"] for i in b["invariants"])
    assert any("zapata" in i["expression"] for i in a["invariants"])
    br = next(m for m in b["assemblies"]["standard"]["members"] if m["id"] == "head_bracket")
    assert br["projection_parts"] >= 2.0


def test_every_new_pack_in_this_package_binds_only_nodes_that_already_had_bindings():
    """A coverage claim that would be false if any of these packs had been used to paper over an
    unbound node. The count of bound nodes has not moved since WP-4.1's 131 for exactly that reason,
    and the reports say so rather than presenting role coverage as node coverage."""
    for pid in ("adobe-module", "opening-pointed", "opening-craftsman", "trim-prairie",
                "dutch-gambrel", "balcony-gallery"):
        for nid in pack(pid)["applies_to"]:
            others = [e for e in node(nid)["proportion_packs"] if e["pack"] != pid]
            assert others, (pid, nid)


# ---------------------------------------------------------------- stone-course


def test_the_module_cannot_be_a_course_of_the_wall_and_the_pack_says_why():
    """A brick wall has a gauge rod and every course is the same height. A rubble wall has no gauge
    at all, because the stone arrives as the quarry bed gives it -- so the module is a course of the
    DRESSING, the only stone in the building with a dimension before it is laid."""
    st, br = pack("stone-course"), pack("brick-course")
    assert "gauge rod" in br["module"]["note"]
    assert "no gauge" in st["module"]["note"]
    assert "dressed stone" in st["module"]["name"].lower()
    assert st["module"]["default_size_in"] != br["module"]["default_size_in"]


def test_the_central_rule_is_stated_twice_independently_by_the_corpus():
    """Two records, four centuries and two building types apart, giving the same rule with the same
    word -- RESERVED -- and neither aware of the other. That agreement is the pack's authority for
    its whole dressed/field division, so the test checks the corpus rather than the pack's prose."""
    cots = json.dumps(node("cotswold-vernacular"))
    norm = json.dumps(node("norman-romanesque-english"))
    assert "dressed ashlar reserved for mullions, jambs, lintels, quoins" in cots
    assert "ashlar reserved for quoins, jambs, voussoirs, string courses" in norm
    assert "RESERVED" in pack("stone-course")["notes"]


def test_the_reveal_is_not_the_wall_which_is_the_opposite_of_adobe():
    """adobe-module states reveal and wall thickness with the SAME expression because they are the
    same number. Here the jamb is dressed and rebated, so the reveal is about two-thirds of the
    wall -- and that difference is what makes internal lining tolerable here and fatal there."""
    st = {(r["target_slot"], r["dimension"]): r for r in pack("stone-course")["derived_rules"]}
    ad = {(r["target_slot"], r["dimension"]): r for r in pack("adobe-module")["derived_rules"]}
    assert ad[("reveal_masonry", "width")]["expression"] == ad[("wall_thickness_masonry", "width")]["expression"]
    assert st[("reveal_masonry", "width")]["expression"] != st[("wall_thickness_masonry", "width")]["expression"]
    assert "THE REVEAL IS NOT THE WALL" in st[("reveal_masonry", "width")]["note"]


def test_the_two_packs_give_opposite_energy_advice_and_both_say_why():
    """adobe-module says exterior insulation destroys the building and internal throws away the
    mass. stone-course says line it internally. The reason is the reveal rule, and a corpus whose
    two mass-wall packs disagreed without explaining themselves would be worse than one pack."""
    st = next(c for c in pack("stone-course")["conflicts"] if c["with"] == "energy-code")
    ad = next(c for c in pack("adobe-module")["conflicts"] if c["with"] == "energy-code")
    assert "OPPOSITE of the advice in `adobe-module`" in st["resolution"]
    assert "reveal" in st["resolution"]
    assert st["severity"] == ad["severity"] == "blocking"


def test_the_opening_is_capped_by_what_a_lintel_will_span():
    """`french-provincial-farmhouse` says it outright: openings are 'sized by the lintel or
    relieving arch available'. Everything about the elevation follows -- few openings, wide piers,
    a mullion instead of a wider head, and no picture window."""
    r = next(x for x in pack("stone-course")["derived_rules"]
             if x["target_slot"] == "window_head_masonry" and x["dimension"] == "width")
    assert "sized by the lintel or relieving arch available" in json.dumps(node("french-provincial-farmhouse"))
    assert "CENTRAL PLAN CONSEQUENCE" in r["note"]


def test_the_lintel_depth_is_tied_to_the_span_by_an_invariant():
    """Widening the opening deepens the head, which raises the wall above it. Held as an invariant
    so that anyone who widens the opening finds out, rather than discovering it on site."""
    p = pack("stone-course")
    lintel = next(m for m in p["assemblies"]["dressed_opening"]["members"] if m["id"] == "lintel")
    span_modules = 5.0                                    # module * 5, the head rule
    assert abs(lintel["height_parts"] * 6 - span_modules * p["module"]["parts"]) < 1.0
    assert any("sixth of its span" in i["statement"] for i in p["invariants"])


def test_the_quoin_alternates_and_the_invariant_holds_equal_beds():
    """Equal beds, unequal faces. A run where every stone shows the same face is a corner cladding
    and says at fifty yards that the stones were ordered from a list rather than cut for the job."""
    p = pack("stone-course")
    m = {x["id"]: x for x in p["assemblies"]["quoin_run"]["members"]}
    assert m["quoin_long"]["height_parts"] == m["quoin_short"]["height_parts"]
    assert m["quoin_long"]["projection_parts"] > m["quoin_short"]["projection_parts"]
    ratio = next(r for r in p["derived_rules"]
                 if r["target_slot"] == "corner_quoin" and r["dimension"] == "ratio")
    assert ratio["judgment"] is True


def test_twelve_nodes_bound_not_thirty_four_and_the_criterion_is_stated():
    """The measurement found 34 thinly-bound stone nodes. Binding all of them would have raised a
    number and told the corpus something false about eleven. The criterion is whether the stone wall
    GOVERNS or merely occurs, and the notes name where each excluded group went instead."""
    p = pack("stone-course")
    assert len(p["applies_to"]) == 12
    assert "WHY TWELVE NODES AND NOT THIRTY-FOUR" in p["notes"]
    for nid in ("mexican-hacienda", "spanish-colonial-american", "greek-classical",
                "mid-atlantic-georgian", "tudor", "english-medieval-timber-frame"):
        assert nid not in p["applies_to"], nid
    for nid in ("mexican-hacienda", "spanish-colonial-american"):
        assert binding(nid, "adobe-module") is not None, nid   # where they went instead
    assert binding("greek-classical", "greek-doric") is not None


def test_the_three_systems_it_declines_are_named_with_their_figures():
    """The moulded sections, the Scottish crow-step and bartizan, and the Tuscan loggia arcade. Each
    has real numbers in a style record and none of them is walling; quoting them in the notes is how
    the next author finds them instead of rediscovering them."""
    n = pack("stone-course")["notes"]
    for phrase in ("ovolo", "crow-step", "0.4-0.6 of the clear opening"):
        assert phrase in n
    assert "crow-step tread 300" in json.dumps(node("scottish-baronial")).replace("\u2013", "-") \
        or "Crow-step tread 300" in json.dumps(node("scottish-baronial"), ensure_ascii=False)


def test_the_wall_thickness_band_is_three_records_agreeing():
    """500-700 mm given independently by a Cotswold cottage, a Tuscan farmhouse and a Provencal one.
    Three unrelated records in three countries is a stronger agreement than any single source, which
    is why the figure carries no hedge."""
    r = next(x for x in pack("stone-course")["derived_rules"]
             if x["target_slot"] == "wall_thickness_masonry" and x["dimension"] == "width")
    for nid in ("cotswold-vernacular", "tuscan-vernacular", "french-provincial-farmhouse"):
        t = json.dumps(node(nid), ensure_ascii=False)
        assert "500" in t and "700 mm" in t, nid
    assert r["range"][0] < 500 / 25.4 and r["range"][1] > 700 / 25.4


def test_lime_not_cement_is_stated_as_the_blocking_structural_rule():
    """A cement mortar is stronger and less permeable than the stone, so water leaves through the
    stone's face instead and the face spalls. Still routinely specified, so the pack says it in
    capitals in a blocking conflict rather than in a note."""
    c = next(x for x in pack("stone-course")["conflicts"] if x["with"] == "structural")
    assert c["severity"] == "blocking"
    assert "NEVER POINT OR BED IN CEMENT" in c["resolution"]
    assert "through-stone" in c["statement"].lower() or "through-stones" in c["resolution"]


def test_the_module_carries_its_own_warning_about_the_local_stone():
    """Nine inches is oolitic limestone and most sandstones. A granite or thin-flagstone tradition
    wants a different number with every figure in the pack moving behind it -- which is the one
    thing a reader most needs told, so it is in the module note, the availability conflict and the
    closing notes alike."""
    p = pack("stone-course")
    assert "granite" in p["module"]["note"]
    c = next(x for x in p["conflicts"] if x["with"] == "material-availability")
    assert "change the module" in c["resolution"]
    assert "nine inches is oolitic limestone" in p["notes"]


# --------------------------------------------------------------- facade-arcade


def test_three_packs_in_this_package_asked_for_the_arcade_independently():
    """Two of them said it was 'still in WP-4.1's candidate list', which was wrong -- it was never on
    it. A gap that three separate pieces of work reach for and that the list does not name is worth
    recording as a fact about the list."""
    for nid in ("spanish-colonial-american", "california-mission-colonial"):
        assert any("arcade" in e["note"] for e in node(nid)["proportion_packs"]), nid
    assert "portal/arcade system are both missing" in json.dumps(node("spanish-colonial-american"))
    assert "0.4-0.6 of the clear opening" in pack("stone-course")["notes"]
    assert "THREE PACKS IN THIS WORK PACKAGE ASKED FOR IT INDEPENDENTLY" in pack("facade-arcade")["notes"]


def test_nine_unrelated_records_give_the_same_pier_to_span_ratio():
    """Five countries, six centuries, no route by which any could have got it from the others. The
    test checks the corpus rather than the pack's claim about the corpus."""
    r = next(x for x in pack("facade-arcade")["derived_rules"]
             if x["target_slot"] == "porch_support" and x["dimension"] == "ratio")
    assert r["range"] == [0.25, 0.60]
    thirds = 0
    for nid in ("italian-renaissance", "italian-renaissance-revival", "mediterranean-revival",
                "norman-romanesque-english"):
        assert "1/3 to 1/2" in json.dumps(node(nid)), nid
        thirds += 1
    assert thirds == 4
    assert "0.35-0.5" in json.dumps(node("italian-villa-vernacular"))
    assert "0.4-0.6" in json.dumps(node("tuscan-vernacular"))
    assert "1:3.5" in json.dumps(node("mission-revival"))


def test_it_is_the_only_pack_in_the_package_claiming_high_confidence():
    """And the reason is the agreement rather than the sources. When the corpus agrees with itself
    that strongly the pack is reporting rather than reconstructing, and the strength should say so."""
    assert pack("facade-arcade")["confidence"] == "high"
    for pid in ("adobe-module", "opening-pointed", "opening-craftsman", "trim-prairie",
                "dutch-gambrel", "balcony-gallery", "stone-course"):
        assert pack(pid)["confidence"] == "medium", pid


def test_the_arch_shape_is_deliberately_not_in_this_pack():
    """What makes it composable. Bay, pier, springing and rhythm are identical whether the arch is
    semicircular, equilateral, four-centred or horseshoe -- so the rise rule says to take its figure
    from whichever arch pack the node binds."""
    r = next(x for x in pack("facade-arcade")["derived_rules"]
             if x["target_slot"] == "arch" and x["dimension"] == "height")
    assert "ANOTHER PACK SHOULD OVERRIDE" in r["note"]
    assert "opening-pointed" in r["note"] and "moorish-arch" in r["note"]
    for nid in ("moorish-andalusian", "mudejar", "andalusian-courtyard-vernacular"):
        assert binding(nid, "moorish-arch") and binding(nid, "facade-arcade"), nid


def test_the_two_packs_that_share_the_impost_collide_on_the_rise_and_nothing_else():
    """facade-arcade and moorish-arch both make the impost their diagnostic member, and three nodes
    bind both. Writing this test found a real corruption: both packs were writing to
    porch_support/height, but moorish-arch meant the impost BLOCK's own height (about 6 in) and
    facade-arcade meant the springing LINE above the floor (84 in). Two packs putting different
    quantities into one address is silent -- whichever resolves last wins and nothing reports it --
    so the arcade's rule was renamed to the `springing` dimension.

    What they may still share is arch/height, and that one is correct: both mean the arch's rise,
    the same quantity with different values by tradition, which is exactly what precedence is for."""
    arc_slots = {(r["target_slot"], r["dimension"]) for r in pack("facade-arcade")["derived_rules"]}
    moor_slots = {(r["target_slot"], r["dimension"]) for r in pack("moorish-arch")["derived_rules"]}
    assert arc_slots & moor_slots == {("arch", "height")}
    assert ("porch_support", "springing") in arc_slots
    assert ("porch_support", "height") in moor_slots
    for nid in ("moorish-andalusian", "mudejar", "andalusian-courtyard-vernacular"):
        assert binding(nid, "moorish-arch") and binding(nid, "facade-arcade"), nid


def test_no_binding_anywhere_outranks_a_primary_one():
    """WP-4.6 introduced this fault twelve times by inserting every new binding at the first unused
    precedence, which is nearly always 0. Nothing caught it: precedence was checked for being a
    total order and never for agreeing with role, so the two fields could say opposite things and
    the build stayed green. check_pack_bindings.py now errors on it; this pins the data."""
    import glob as _glob
    for f in sorted(_glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = json.load(open(f))
        es = d.get("proportion_packs") or []
        prims = [e for e in es if e["role"] == "primary"]
        if not prims:
            continue
        lo = min(e["precedence"] for e in prims)
        ahead = [e for e in es if e["role"] != "primary" and e["precedence"] < lo]
        assert not ahead, (d["id"], [(e["pack"], e["role"], e["precedence"]) for e in ahead])


def test_the_narrow_rule_is_enforced_and_the_wide_one_only_warned():
    """Measured over all 132 buildable nodes, `secondary` sits ahead of a role pack in 253 places
    across 59 nodes -- which is the corpus's own convention (order packs first, then role packs),
    not a bug. Enforcing a tidier ordering would have meant churning 59 nodes to satisfy a rule
    nobody had agreed to. The checker errors only on the rule the corpus actually holds."""
    src = open(os.path.join(ROOT, "build", "check_pack_bindings.py")).read()
    i = src.index("Precedence must not contradict role")
    block = src[i:i + 4000]
    assert "errors.append" in block and "warnings.append" in block
    assert "253 places across 59 nodes" in block


def test_four_records_say_the_arcade_is_the_circulation():
    """The pack's largest plan consequence, and none of the four treats it as remarkable."""
    r = next(x for x in pack("facade-arcade")["derived_rules"]
             if x["target_slot"] == "circulation_parti")
    assert "serving as all circulation" in json.dumps(node("california-mission-colonial"))
    assert "not from corridors" in json.dumps(node("mexican-colonial"))
    assert "circulation, shade and social space" in json.dumps(node("mexican-hacienda"))
    assert "serving as the building's circulation" in json.dumps(node("spanish-colonial-american"))
    assert "LARGEST PLAN CONSEQUENCE" in r["note"]


def test_the_end_pier_rule_exists_because_an_arcade_is_not_in_equilibrium_at_its_ends():
    """The one thing an arcade drawn in CAD always gets wrong. Intermediate piers take two thrusts
    that cancel; the end pier takes one. A run of identical piers ending in air has never been built."""
    r = next(x for x in pack("facade-arcade")["derived_rules"]
             if x["dimension"] == "end_ratio")
    assert r["judgment"] is True and r["range"] == [1.0, 2.0]
    c = next(x for x in pack("facade-arcade")["conflicts"] if x["with"] == "structural")
    assert c["severity"] == "blocking"
    assert "equilibrium in the middle and not at the ends" in c["statement"]


def test_english_gothic_is_refused_and_its_own_record_gives_the_number():
    """It has the best-stated arcade ratios in the corpus and states them to say how DIFFERENT they
    are: 1:4 to 1:6 pier to bay against Norman's 1:2 to 1:3. A Gothic arcade sends its thrust to a
    buttress rather than into the pier, so proportioning one here would produce a building that
    cannot stand in a way this pack cannot detect."""
    assert "english-gothic" not in pack("facade-arcade")["applies_to"]
    assert binding("english-gothic", "facade-arcade") is None
    assert "1:4 to 1:6" in json.dumps(node("english-gothic"))
    assert "cannot stand up in a way this pack cannot detect" in pack("facade-arcade")["notes"]


def test_the_energy_conflict_names_the_consequence_of_having_no_corridor():
    """Every room's door is an exterior door. A range of eight rooms entered from a corredor has
    eight exterior doors on one elevation and no lobby anywhere -- a problem no other type in the
    library has at this scale, and one that follows directly from the circulation rule."""
    c = next(x for x in pack("facade-arcade")["conflicts"] if x["with"] == "energy-code")
    assert "Every room's door is an exterior door" in c["statement"]
    assert "changes the type" in c["resolution"]


def test_it_moved_the_facade_role_count_for_the_first_time_in_the_package():
    """Six packs before it closed opening, interior and threshold gaps and left the facade role
    untouched at 67. This one is a facade-system and binds nine nodes in the facade role."""
    facade_bound = [nid for nid in pack("facade-arcade")["applies_to"]
                    if binding(nid, "facade-arcade")["role"] == "facade"]
    assert len(facade_bound) == 9, "the docstring says nine; pin the achieved value, not a floor"
    src = open(os.path.join(ROOT, "README.md")).read()
    m = re.search(r"(\d+) no facade-role pack", src)
    # TIGHT, not `< 67`. 67 was the PRE-package baseline and the achieved figure is 46, so this
    # ratchet carried 21 units of silence: twenty-one nodes could lose their facade-role pack and
    # it stayed green. That is the same defect as check_inheritance's 329-against-294 threshold,
    # in the test that is supposed to be the headline movement's own guard. Found by audit.
    assert m, "README no longer states the facade-role figure -- the guard has rotted"
    assert int(m.group(1)) == 46, (
        f"facade-role gap is {m.group(1)}, pinned at 46. It should only go DOWN; if it did, "
        f"lower the pin here deliberately rather than leaving slack under it.")


# ---------------------------------------------------------------- timber-panel


def test_the_panel_pack_restates_nothing_that_timber_bay_already_owns():
    """WP-4.1's item asks for a panel module 'distinct from timber-bay's larger structural framing
    bay'. Setting out to write it, six of sixteen planned rules were already that pack's -- the bay,
    the storey height, the range depth, the storey diminution, the roof pitch and the frame reveal --
    and timber-bay is already bound to seven of the fifteen nodes this one binds. Two packs asserting
    one number is how a corpus starts disagreeing with itself."""
    panel = {(r["target_slot"], r["dimension"]) for r in pack("timber-panel")["derived_rules"]}
    bay = {(r["target_slot"], r["dimension"]) for r in pack("timber-bay")["derived_rules"]}
    assert not (panel & bay), sorted(panel & bay)
    shared = [nid for nid in pack("timber-panel")["applies_to"]
              if nid in pack("timber-bay")["applies_to"]]
    assert len(shared) == 7, shared        # measured, not estimated


def test_the_panel_proportion_is_regional_and_one_record_holds_two_regions():
    """The pack's central rule, and unusual in this library for having no correct value -- only a
    correct value for a place. 1:1 is German, 1.2 English south-east, 2 to 4 East Anglian or Norman."""
    r = next(x for x in pack("timber-panel")["derived_rules"]
             if x["target_slot"] == "primary_cladding" and x["dimension"] == "ratio")
    assert r["range"] == [1.0, 4.0]
    assert "roughly square in the south-east" in json.dumps(node("english-medieval-timber-frame"))
    assert "1:3 to 1:4 vertical in East Anglian close studding" in json.dumps(node("english-medieval-timber-frame"))
    assert "1:1 to 2:3" in json.dumps(node("german-fachwerk"))
    assert "1:2 to 1:4" in json.dumps(node("norman-vernacular"))
    assert "from nowhere" in r["note"]


def test_the_projection_rule_is_what_separates_applied_work_from_stripes():
    """`french-normandy-revival` states it as a minimum rather than a figure: members 'projecting at
    least 1 in. from the stucco plane'. Without it there is no shadow and no reason for the timber."""
    r = next(x for x in pack("timber-panel")["derived_rules"]
             if x["target_slot"] == "expressed_frame" and x["dimension"] == "projection")
    assert r["range"][0] >= 0.75
    assert "projecting at least 1 in. from the stucco plane" in json.dumps(node("french-normandy-revival"))


def test_the_jetty_rule_holds_two_records_that_disagree():
    """`english-medieval-timber-frame` puts the jetty at about four thirds of the joist depth;
    `tudor-revival` caps it at one. Both are warning against the same thing from opposite
    directions, and both use the word 'never', which is rare in this corpus."""
    r = next(x for x in pack("timber-panel")["derived_rules"]
             if x["target_slot"] == "material_change_rule" and x["dimension"] == "ratio")
    assert r["range"] == [0.8, 2.0]
    assert "never the exaggerated overhang of revival work" in json.dumps(node("english-medieval-timber-frame"))
    assert "never more than the depth of a plausible joist" in json.dumps(node("tudor-revival"))
    assert "TWO RECORDS DISAGREE" in r["authority_note"]


def test_the_two_refusals_are_explicit_negatives_in_the_records():
    """A node mentioning a thing is not a node having it. Both of these are found by a regex sweep
    for half-timbering and both say in their own words that they have none."""
    p = pack("timber-panel")
    for nid in ("jacobethan-revival", "cotswold-cottage-revival"):
        assert nid not in p["applies_to"], nid
        assert binding(nid, "timber-panel") is None, nid
    assert "no half-timbering" in json.dumps(node("jacobethan-revival"))
    assert "without applied half-timbering" in json.dumps(node("cotswold-cottage-revival"))
    count = next(x for x in p["derived_rules"]
                 if x["target_slot"] == "material_change_rule" and x["dimension"] == "count")
    assert count["range"][0] == 0.0


def test_the_framed_wall_is_a_quarter_the_thickness_of_its_masonry_contemporaries():
    """One record measures cob, rubble and frame in a single sentence. Every consequence follows: no
    reveal, no thermal mass, and a wall that can be pierced anywhere between two studs."""
    t = json.dumps(node("english-cottage-vernacular"))
    assert "450-600 mm in cob" in t and "150 mm in a daub-panelled frame" in t
    r = next(x for x in pack("timber-panel")["derived_rules"]
             if x["target_slot"] == "wall_thickness_frame")
    assert r["range"] == [4.0, 10.0]


def test_stick_style_is_bound_with_the_caveat_that_it_is_not_infill():
    """It applies boards to a clapboarded balloon-framed wall and the boards express a frame that is
    not there -- which is the type's own argument, since what they express is the balloon frame
    behind them. It supplies the corpus's only brace figure."""
    b = binding("stick-style", "timber-panel")
    assert b["role"] == "optional"
    assert "THIS IS NOT INFILL" in b["note"]
    assert "brace length 0.3 to 0.5 of post height" in json.dumps(node("stick-style"))


def test_the_missing_slot_was_raised_as_an_open_question_and_is_now_closed():
    """RE-PINNED. Four of this pack's rules routed the exposed timber through `corner_board` -- a
    board at a corner -- because the ontology had no slot for a structural member expressed on a
    wall face, and the compromise was RAISED rather than worked around. It was ruled on 25 Aug 2026
    and the four rules moved. What the test still protects is the thing that mattered: the gap was
    stated in the data, not hidden, and it is the statement that got it closed."""
    p = pack("timber-panel")
    routed = [r for r in p["derived_rules"] if r["target_slot"] == "expressed_frame"]
    assert len(routed) == 4
    assert not any(r["target_slot"] == "corner_board" for r in p["derived_rules"])
    oq = _register_text()
    assert "47. **CLOSED 25 Aug 2026 — `expressed_frame` added at ontology 0.7.0" in oq
    assert "**OPEN — the ontology has no slot for an exposed structural member" in oq  # kept, superseded


def test_the_pack_says_the_exposed_frame_is_substantially_a_victorian_taste():
    """Four records in the corpus describe the frame being covered -- tile-hung, weatherboarded,
    stuccoed, limewashed. The climate conflict says plainly that covering it is what the buildings
    did rather than a modern compromise."""
    c = next(x for x in pack("timber-panel")["conflicts"] if x["with"] == "climate")
    assert "THE TRADITIONS THEMSELVES CONCLUDED THAT THIS WALL SHOULD BE COVERED" in c["statement"]
    assert "tile-hung upper storey" in json.dumps(node("queen-anne-british"))
    assert "stuccoed or weatherboarded" in json.dumps(node("creole-cottage-vernacular"))


# ------------------------------------------------------------ opening-mullioned


def test_the_two_list_items_turned_out_to_be_one_system():
    """WP-4.1 lists the four-centred Tudor arch and a leaded-casement-and-mullion system separately,
    and both were raised again from inside this work package -- by opening-pointed's own boundary and
    by opening-craftsman's refusal of arts-and-crafts-british. A Tudor window IS a four-centred head
    over a mullioned band of leaded lights, and separating them would have produced two packs neither
    of which described a window."""
    assert "FOUR-CENTRED TUDOR ARCH" in pack("opening-pointed")["notes"]
    assert "leaded-casement-and-mullion system of its own" in pack("opening-craftsman")["notes"]
    p = pack("opening-mullioned")
    slots = {(r["target_slot"], r["dimension"]) for r in p["derived_rules"]}
    assert ("arch", "ratio") in slots and ("window_lite_pattern", "width") in slots


def test_the_window_is_counted_and_not_measured():
    """The central rule, stated by the corpus in five words. A Georgian window has a proportion; this
    one has a COUNT, so its width is quantised at the light and there is nothing in between."""
    assert "window width is a whole number of lights" in json.dumps(node("tudor"))
    r = next(x for x in pack("opening-mullioned")["derived_rules"]
             if x["target_slot"] == "window_grouping_rule" and x["dimension"] == "lights_per_window")
    assert r["range"][0] == 2.0, "a single-light mullioned window is a contradiction"
    assert "COUNTED RATHER THAN MEASURED" in r["note"]


def test_eight_records_converge_on_the_light_and_the_module_is_their_middle():
    p = pack("opening-mullioned")
    assert p["module"]["default_size_in"] == 18.0
    for nid, frag in (("tudor", "400-500 mm"), ("elizabethan", "400-550 mm"),
                      ("jacobean", "450-550"), ("cotswold-vernacular", "300-450 mm"),
                      ("arts-and-crafts-british", "350-450 mm"),
                      ("jacobethan-revival", "18-24 in"), ("tudor-revival", "16-22 in")):
        assert frag in json.dumps(node(nid)), (nid, frag)


def test_the_four_centred_head_is_outside_what_a_strike_ratio_can_express():
    """opening-pointed's flattest arch, the drop arch, still rises 0.707 of its span. A four-centred
    head rises a quarter to a third, because it is struck from four centres with two radii."""
    tudor_arch = next(x for x in pack("opening-mullioned")["derived_rules"]
                      if x["target_slot"] == "arch" and x["dimension"] == "ratio")
    pointed = next(x for x in pack("opening-pointed")["derived_rules"]
                   if x["target_slot"] == "arch" and x["dimension"] == "ratio")
    assert tudor_arch["range"][1] < 0.5 < pointed["range"][0]
    assert "1:3 to 1:4" in json.dumps(node("tudor"))


def test_the_tall_unit_in_a_wide_band_is_the_same_inversion_craftsman_found():
    """Two unrelated traditions four centuries apart, both building a horizontal band out of vertical
    units, and both got wrong the same way by designers who absorb the band and draw a squat unit."""
    for pid in ("opening-mullioned", "opening-craftsman"):
        unit = next(x for x in pack(pid)["derived_rules"] if x["target_slot"] == "window_proportion")
        assert float(unit["expression"]) >= 1.5, pid
    band = next(x for x in pack("opening-mullioned")["derived_rules"]
                if x["target_slot"] == "window_grouping_rule" and x["dimension"] == "ratio")
    assert band["range"][0] > 1.0                      # wide overall
    assert "the exact inverse of the Georgian vertical punched opening" in \
        json.dumps(node("arts-and-crafts-british"))


def test_both_traditional_opening_packs_fail_r310_on_the_mullion_not_the_head():
    """A fact about the code as much as about the windows, and worth stating as a pattern rather than
    twice as a coincidence."""
    for pid in ("opening-pointed", "opening-mullioned"):
        c = next(x for x in pack(pid)["conflicts"] if x["with"] == "egress-code")
        assert c["severity"] == "blocking", pid
        assert "mullion" in c["statement"].lower(), pid
    assert "four centuries apart" in \
        next(x for x in pack("opening-mullioned")["conflicts"] if x["with"] == "egress-code")["statement"]


def test_the_glazing_band_is_a_history_and_the_records_say_so():
    """Elizabethan 45-60 and higher at Hardwick; Jacobean explicitly a retreat to 30-45; the revival
    back at 35-55 because glass was cheap by 1910. A designer should pick a decade, not a number."""
    r = next(x for x in pack("opening-mullioned")["derived_rules"]
             if x["target_slot"] == "daylight_strategy")
    assert r["judgment"] is True and r["range"] == [0.25, 0.6]
    assert "higher at Hardwick" in json.dumps(node("elizabethan"))
    assert "reduced from Elizabethan extremes" in json.dumps(node("jacobean"))
    assert "far higher than any other revival" in json.dumps(node("jacobethan-revival"))


def test_english_gothic_now_has_both_halves_of_its_window():
    """opening-pointed holds the arch and this pack the Perpendicular mullion grid beneath it, which
    is the direct ancestor of every Tudor and Jacobean window here."""
    assert binding("english-gothic", "opening-pointed")["role"] == "opening"
    assert binding("english-gothic", "opening-mullioned")["role"] == "secondary"
    assert "mullions running unbroken from sill to arch head" in json.dumps(node("english-gothic"))


# ----------------------------------------------------------------- facade-gable


def test_the_library_had_no_gable_geometry_of_any_kind_and_two_packs_said_so():
    """WP-4.1 records this gap in the strongest terms it uses anywhere. dutch-gambrel says plainly it
    does NOT reduce the item -- 'a gable profile is an elevation outline and a gambrel is a roof
    section' -- and stone-course quoted the Scottish crow-step figures into its own notes purely so
    they would not be lost."""
    assert "does NOT reduce it" in pack("dutch-gambrel")["notes"]
    assert "crow-step" in pack("stone-course")["notes"]
    assert "NO GABLE GEOMETRY SYSTEM OF ANY KIND" in pack("facade-gable")["notes"]


def test_a_gable_is_three_different_objects_and_four_records_distinguish_them():
    """Roof end, parapet, or screen -- and deciding which is prior to any dimension in the pack. None
    of the four records is talking about the others."""
    assert "genuinely the end of a roof rather than a screen in front of one" in json.dumps(node("flemish-vernacular"))
    assert "the wall carries up past the roof plane" in json.dumps(node("jacobethan-revival"))
    assert "standing free above the eave line" in json.dumps(node("cape-dutch"))
    assert "gable screen" in json.dumps(node("dutch-urban-gable-house"))
    m = pack("facade-gable")["module"]["note"]
    assert "THREE DIFFERENT OBJECTS" in m and "prior to any dimension" in m


def test_the_crow_step_ratio_disagreement_is_kept_as_a_band():
    """Flemish steps are square and Scottish ones broader than high. The two read quite differently
    and neither record has heard of the other."""
    r = next(x for x in pack("facade-gable")["derived_rules"]
             if x["target_slot"] == "rake_condition" and x["dimension"] == "ratio")
    assert r["range"] == [1.0, 2.25]
    assert "rise to tread roughly 1:1" in json.dumps(node("flemish-vernacular"))
    assert "tread 300" in json.dumps(node("scottish-baronial")).replace("\u2013", "-")
    assert "TWO RECORDS DISAGREE" in r["authority_note"]


def test_three_unrelated_records_agree_on_the_apex_ratio():
    """Tudor Revival, British Gothic Revival and Jacobean land within a tenth of each other on a
    proportion nobody wrote down."""
    r = next(x for x in pack("facade-gable")["derived_rules"]
             if x["target_slot"] == "gable_treatment" and x["dimension"] == "ratio")
    assert 0.55 <= float(r["expression"]) <= 1.05
    assert "the triangle reads taller than half its base" in json.dumps(node("tudor-revival"))
    assert "1:0.7 to 1:1" in json.dumps(node("gothic-revival-british"))
    assert "0.6-0.8 of the gable width" in json.dumps(node("jacobean"))


def test_the_same_gable_count_carries_opposite_instructions():
    """Jacobean ranges its gables symmetrically; the Gothic villa says equal widths are a failure and
    calls them 'a builder's composition'. Same number, opposite compositional rule."""
    hier = next(x for x in pack("facade-gable")["derived_rules"]
                if x["target_slot"] == "wing_strategy")
    assert hier["range"] == [1.4, 2.2]
    assert "equal gables indicate a builder's composition" in json.dumps(node("rural-gothic-villa"))
    assert "ranged symmetrically along a front" in json.dumps(node("jacobean"))
    count = next(x for x in pack("facade-gable")["derived_rules"]
                 if x["target_slot"] == "gable_treatment" and x["dimension"] == "count")
    assert "opposite compositional rule" in count["note"]


def test_the_third_self_refusal_in_the_package():
    """arts-and-crafts-british: 'no classical order, no pointed arch, no shaped gable, no period
    quotation of any kind: the absence of quotation is itself the tell.' After jacobethan-revival and
    cotswold-cottage-revival refused half-timbering in their own words."""
    assert "arts-and-crafts-british" not in pack("facade-gable")["applies_to"]
    assert binding("arts-and-crafts-british", "facade-gable") is None
    assert "no shaped gable" in json.dumps(node("arts-and-crafts-british"))


def test_the_gable_pack_shares_no_address_meaning_a_different_quantity():
    """Writing this test found four collisions with packs facade-gable co-binds with, and three were
    DIFFERENT quantities at one address: opening-pointed writes gable_treatment/height for a FINIAL,
    dutch-gambrel writes it for the gable-end SILHOUETTE, opening-pointed writes
    ornament_vocabulary/count for a cusped motif set and rake_condition/height for a BARGEBOARD.
    Three packs meaning three things at one address is the corruption facade-arcade found, and
    precedence cannot settle it. All three are renamed to named dimensions.

    dormer/width is left shared on purpose: both packs mean the dormer's width, which is the same
    quantity with different values by tradition, and that is exactly what precedence is for."""
    gable = {(r["target_slot"], r["dimension"]) for r in pack("facade-gable")["derived_rules"]}
    for other in ("timber-bay", "opening-pointed", "stone-course", "dutch-gambrel"):
        shared = gable & {(r["target_slot"], r["dimension"]) for r in pack(other)["derived_rules"]}
        assert shared <= {("dormer", "width")}, (other, sorted(shared))
    for named in (("gable_treatment", "facade_ratio"), ("gable_treatment", "parapet_height"),
                  ("ornament_vocabulary", "curve_count"), ("rake_condition", "step_rise")):
        assert named in gable, named


def test_the_intra_pack_duplicate_addresses_are_menus_and_must_not_be_fixed():
    """Measuring the collisions corpus-wide found 1,922 instances, and the largest entries are packs
    colliding with THEMSELVES -- room-harmonic writing room_adjacency_overrides/width ten times. Those
    are not defects: they are a MENU at one address, authored deliberately and labelled as such
    ('SHAPE 1 OF 7', 'METHOD 1 OF 3'). A naive uniqueness check would flag 1,710 correct rules, which
    is why this package raised OQ 48 instead of shipping one."""
    rh = pack("room-harmonic")["derived_rules"]
    shapes = [r for r in rh if (r["target_slot"], r["dimension"]) == ("room_adjacency_overrides", "width")]
    assert len(shapes) >= 7
    assert any("1 OF 7" in r["note"] for r in shapes)
    # OQ 48's migration moved room-harmonic's vaulted menu to its own dimension, which is the fix
    # working: the MENU is intact and now sits at an address nothing else writes to.
    heights = [r for r in rh if r["target_slot"] == "ceiling_height_rule"]
    assert any("METHOD 1 OF 3" in r["note"] for r in heights)
    oq = _register_text()
    # RE-PINNED: OQ 48 is now partly closed -- the menu reading is what kept a naive uniqueness
    # check from being shipped, and it is still the reason `check_addresses.py` compares MEANINGS.
    # RE-PINNED: OQ 48 is now fully closed. The menu reading is still what kept a naive uniqueness
    # check from shipping, and it is why `check_addresses.py` compares MEANINGS rather than counting.
    assert "48. **CLOSED 25 Aug 2026 — 139 to 0" in oq and "menu" in oq


def test_the_flush_faced_dormer_decides_which_pack_applies():
    """A dormer whose front is in the plane of the wall below is a gable of the wall; one set back on
    the roof slope is a box with a roof on it. One record states the distinction."""
    assert "faces flush with the wall below" in json.dumps(node("cotswold-vernacular"))
    r = next(x for x in pack("facade-gable")["derived_rules"] if x["target_slot"] == "dormer")
    assert "FLUSH FACE" in r["note"]


# ------------------------------------------------------------------- trim-sawn


def test_four_list_items_are_one_family_because_of_two_machines():
    """The list separately asks for sawn Gothic ornament, sawn-bracket Victorian trim, turned Queen
    Anne millwork and Alpine carved timber. The first three are the scroll saw and the lathe, steam-
    powered from the 1840s, producing three members ordered from the same catalogue."""
    n = pack("trim-sawn")["notes"]
    assert "FOUR ITEMS ON WP-4.1'S CANDIDATE LIST, BUILT AS ONE PACK" in n
    assert "scroll saw and the lathe" in pack("trim-sawn")["module"]["note"]


def test_the_style_is_decided_by_which_members_are_present():
    """The corpus states the discrimination as a decision procedure, not a description."""
    assert ("bargeboard on the rake with no bracket under the eave: Gothic Revival"
            in json.dumps(node("gothic-revival-american")))
    r = next(x for x in pack("trim-sawn")["derived_rules"]
             if x["dimension"] == "member_count")
    assert r["range"] == [1.0, 3.0]
    assert "WHAT DECIDES THE STYLE" in r["note"]


def test_three_records_refuse_the_pack_and_one_gives_a_decision_procedure_for_it():
    """stick-style: 'if the applied woodwork curves, turns, or scrolls, the building has moved to
    Queen Anne or Eastlake.' Two Queen Anne subtypes refuse the ornament their own siblings are named
    for, which is a sharper distinction than any dimension could draw."""
    p = pack("trim-sawn")
    for nid in ("stick-style", "queen-anne-free-classic", "queen-anne-patterned-masonry"):
        assert nid not in p["applies_to"], nid
        assert binding(nid, "trim-sawn") is None, nid
    assert "no turned spindles, no scrolled brackets" in json.dumps(node("stick-style"))
    assert "Absence of turned spindlework" in json.dumps(node("queen-anne-free-classic"))
    assert "no porch spindlework" in json.dumps(node("queen-anne-patterned-masonry"))


def test_the_alpine_item_is_not_merged_and_the_reason_is_the_machine():
    """swiss-chalet is bound for its SAWN balustrades and bargeboards only. Carving is a hand craft
    with a gouge and this pack is about machines, so the Alpine carved-timber item stays on the list."""
    b = binding("swiss-chalet", "trim-sawn")
    assert b["role"] == "optional"
    assert "AND FOR HALF OF WHAT THIS NODE HAS" in b["note"]
    assert "carving is a hand craft" in b["note"] or "carving is a hand craft" in pack("trim-sawn")["notes"]


def test_the_bracket_is_square_because_the_saw_cuts_a_square_blank():
    """A fact about the machine rather than the design, and why brackets across four styles and fifty
    years sit at 45 degrees."""
    p = pack("trim-sawn")
    b = next(m for m in p["assemblies"]["porch_head"]["members"] if m["id"] == "bracket_zone")
    assert b["projection_parts"] == b["height_parts"]
    assert any("square blank" in i["statement"] for i in p["invariants"])
    assert "on the diagonal" in json.dumps(node("queen-anne-spindled"))


def test_the_authoring_aid_exists_and_the_pack_shares_only_same_quantity_addresses():
    """build/pack_addresses.py was written after this package hand-ran the same query three times.
    Four of trim-sawn's addresses were renamed after it reported them -- frieze/height meant a
    classical entablature frieze AND a suspended spindle valance, and eave_condition/height meant an
    eave's height above ground AND a verge's overhang, the latter on ten nodes."""
    assert os.path.exists(os.path.join(ROOT, "build", "pack_addresses.py"))
    mine = {(r["target_slot"], r["dimension"]) for r in pack("trim-sawn")["derived_rules"]}
    for named in (("frieze", "valance_depth"), ("eave_condition", "verge_overhang"),
                  ("cornice", "eave_projection"), ("rake_condition", "stock_thickness"),
                  ("ornament_vocabulary", "member_count")):
        assert named in mine, named
    assert ("frieze", "height") not in mine and ("eave_condition", "height") not in mine


def test_the_two_role_lists_agree_and_nothing_uses_a_role_the_schema_forbids():
    """Found by binding trim-sawn with role 'trim': check_pack_bindings.VALID_ROLES allowed it and
    schema/style-node.schema.json's own enum did not, so the binding passed --strict and failed
    validate.py. The schema is the authority; the checker's list is now identical to it.

    The cascade is the part worth pinning. A node failing schema validation is DROPPED from
    validate.py's node set, so every lineage reference pointing at it reports 'target does not
    exist'. Nine nodes with an illegal role produced FORTY-SEVEN errors, thirty-eight of which named
    entirely innocent nodes and none of which mentioned a role."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_cpb", os.path.join(ROOT, "build", "check_pack_bindings.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    schema = json.load(open(os.path.join(ROOT, "schema", "style-node.schema.json")))
    enum = None
    def walk(o):
        nonlocal enum
        if isinstance(o, dict):
            if o.get("enum") and set(o["enum"]) & {"primary", "secondary", "facade"}:
                enum = set(o["enum"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(schema)
    assert enum is not None, "could not find the role enum in the style-node schema"
    assert m.VALID_ROLES == enum, (sorted(m.VALID_ROLES ^ enum))
    src = open(os.path.join(ROOT, "build", "check_pack_bindings.py")).read()
    assert "look at the top of the list for a SCHEMA error first" in src


def test_the_collision_rate_is_recorded_honestly_in_oq_48():
    """144 WP-4.6 pairs adjudicated, eight were real -- about five per cent. The first measurement's
    1,922 was mostly menus, and saying so is what stops the next person 'fixing' 1,710 correct rules."""
    oq = _register_text()
    assert "about **five per cent**" in oq
    assert "deliberately not built; an authoring aid was" in oq


# ------------------------------------------------------------ octagon-geometry


def test_the_keyword_measurement_overcounted_this_item_for_the_fourth_time():
    """A regex put it at 17 nodes and 11 thinly bound, which would have made it the largest
    remaining item. Reading them, the octagon AS A PLAN is one node and most of the rest match on an
    octagonal chimney shaft, ceiling panel or window shape. Fourth time in this package that a
    keyword measurement of mine over-counted its own work list."""
    n = pack("octagon-geometry")["notes"]
    assert "THE MEASUREMENT THAT PICKED THIS ITEM WAS WRONG" in n
    assert "fourth time" in n.lower()
    assert "a regex proposes and reading disposes" in n


def test_the_pack_carries_two_different_uses_of_one_geometry():
    """Fowler's octagon is a whole building generated from its side. Jefferson's is a ROOM, made by
    cutting a square's corners back by a third, and it reaches most of the corpus as a canted bay on
    a building with no octagonal plan whatever."""
    rules = {(r["target_slot"], r["dimension"]) for r in pack("octagon-geometry")["derived_rules"]}
    assert ("depth_and_pile", "inscribed_diameter") in rules   # Fowler; renamed by OQ 48
    assert ("wing_strategy", "canted_corner") in rules       # Jefferson: the corner cut
    assert "canted corners at 1/3 of the side" in json.dumps(node("jeffersonian-classicism"))
    assert "closed-form" in json.dumps(node("octagon-house"))


def test_the_inscribed_diameter_is_the_geometry_and_the_record_agrees():
    """1 + root 2 = 2.4142. A 12 ft side gives 29 ft and a 20 ft side gives 48, exactly as the
    record states -- so the multiplier is checkable rather than asserted."""
    import math
    r = next(x for x in pack("octagon-geometry")["derived_rules"]
             if x["target_slot"] == "depth_and_pile" and x["dimension"] == "inscribed_diameter")
    k = float(r["expression"].split("*")[1])
    assert abs(k - (1 + math.sqrt(2))) < 0.001
    assert abs(12 * k - 29) < 0.5 and abs(20 * k - 48.3) < 0.5
    assert "29 to 48 ft" in json.dumps(node("octagon-house"))


def test_fowlers_arithmetic_was_right_and_his_conclusion_was_wrong():
    """An octagon really does enclose its floor for nine per cent less wall than a square -- the
    pack computes it -- and the type still failed, because the labour in eight 45-degree corners
    rises faster than the material falls. A useful corrective to the assumption that a traditional
    form is always the economical answer to something."""
    import math
    r = next(x for x in pack("octagon-geometry")["derived_rules"]
             if x["target_slot"] == "depth_and_pile" and x["dimension"] == "ratio")
    # regular octagon: A = 2(1+root2)s^2, P = 8s. square of equal area: P = 4 root A.
    ratio = 8 / (4 * math.sqrt(2 * (1 + math.sqrt(2))))
    assert abs(float(r["expression"]) - ratio) < 0.01
    c = next(x for x in pack("octagon-geometry")["conflicts"] if x["with"] == "cost")
    assert "Fowler's arithmetic was right and his conclusion was wrong" in c["statement"]


def test_an_octagon_cannot_be_added_to_and_the_count_says_zero():
    """Same kind of statement greek-doric makes about ornament and dutch-gambrel about the colonial
    shed dormer. Every face is part of the rhythm and there is no back -- an octagon has eight
    fronts."""
    r = next(x for x in pack("octagon-geometry")["derived_rules"]
             if x["target_slot"] == "wing_strategy" and x["dimension"] == "count")
    assert r["expression"] == "0"
    assert "eight fronts" in r["note"]


def test_the_never_executed_warning_path_caught_a_real_error_the_first_time_it_could():
    """check_modules --eval warns when a rule lands outside its own declared range, and that path
    used a tuple key -- b['opening_width', 'opening_height'] -- so it raised KeyError every time it
    ran. Which means it never ran, because no module pack had been out of band until this one wrote
    `part * 102` with a one-foot part and got 1,224 inches."""
    src = open(os.path.join(ROOT, "build", "check_modules.py")).read()
    assert "was a TUPLE KEY, not a fallback" in src
    assert "b['opening_width', 'opening_height']" not in src.split("# `b[")[0].split("W(f\"derived_rules")[-1]
    r = next(x for x in pack("octagon-geometry")["derived_rules"]
             if x["target_slot"] == "porch_depth")
    p = pack("octagon-geometry")
    part = p["module"]["default_size_in"] / p["module"]["parts"]
    assert 84.0 <= eval(r["expression"], {"part": part}) <= 120.0


# --- facade-pavilion: the travee, the pavilion and the mansard --------------------------------
# Three items of WP-4.1's list in one pack, because they turned out to be one system: the mansard's
# dormer is proportioned against the travee, and the pavilion is what breaks the travee's repetition.


def test_the_travee_is_a_vertical_unit_and_that_is_the_whole_claim():
    """`facade-classical` composes in horizontal layers and the bays fall between them. This system
    composes in vertical strips running from the ground to the finial of a lucarne. The pack says so
    in its module note, because everything else in it follows from the direction."""
    m = pack("facade-pavilion")["module"]
    assert "THE TRAVEE IS A VERTICAL UNIT" in m["note"]
    assert "horizontal, Anglo/Italian-derived logic" in m["note"]   # WP-4.1's own words
    assert m["default_size_in"] / m["parts"] == 16.0


def test_two_rules_carry_a_single_permitted_value_because_they_have_no_partial_version():
    """Unusual in this library and deliberate. Every opening in a travee shares ONE axis, and the
    cornice is continuous with the lucarne passing through it. An elevation an inch out of alignment
    has not slightly broken the system, it has abandoned it -- so the band is [1.0, 1.0]."""
    rules = {(r["target_slot"], r["dimension"]): r for r in pack("facade-pavilion")["derived_rules"]}
    for addr in [("window_grouping_rule", "alignment"), ("cornice", "continuity")]:
        r = rules[addr]
        assert r["range"] == [1.0, 1.0], addr
        assert float(r["expression"]) == 1.0, addr
    assert rules[("window_grouping_rule", "alignment")]["judgment"] is True


def test_one_lucarne_per_travee_and_the_count_says_exactly_one():
    """The commonest way a modern French-styled elevation goes wrong: dormers get placed by what the
    attic plan wants rather than by what the facade requires. Stated as a single value because there
    is no second correct answer."""
    r = next(x for x in pack("facade-pavilion")["derived_rules"]
             if x["target_slot"] == "dormer" and x["dimension"] == "count")
    assert r["expression"] == "1" and r["range"] == [1.0, 1.0]
    assert "roof light behind the ridge, not a second dormer" in r["note"]


def test_the_mansard_and_the_gambrel_differ_entirely_in_the_break_and_in_its_datum():
    """The same idea in two countries. `dutch-gambrel` had to reconcile three records that gave the
    break three different ways with none saying from where; `styles/french-baroque.json` says 'of
    total roof height' in those words. That is why a mansard reads as a storey wearing a hat."""
    brk = next(x for x in pack("facade-pavilion")["derived_rules"]
               if x["target_slot"] == "roof_form" and x["dimension"] == "break_ratio")
    assert brk["range"] == [0.6, 0.7]
    assert "of total roof height" in brk["authority_note"]
    assert "break point at 0.6 to 0.7 of total roof height" in json.dumps(node("french-baroque"))
    # and both packs name the shallow slope the same thing, so the two are comparable
    for pid in ("facade-pavilion", "dutch-gambrel"):
        assert any(x["dimension"] == "upper_ratio" for x in pack(pid)["derived_rules"]), pid


def test_the_break_the_pack_encodes_is_inside_the_band_it_declares():
    """7.2 and 3.6 parts of rise. Computed rather than asserted -- the members are the evidence for
    the invariant, and if either moves the ratio must still land in 0.6-0.7."""
    a = pack("facade-pavilion")["assemblies"]["mansard_section"]["members"]
    lo = next(m for m in a if m["id"] == "lower_slope")["height_parts"]
    up = next(m for m in a if m["id"] == "upper_slope")["height_parts"]
    assert 0.6 <= lo / (lo + up) <= 0.7


def test_the_two_slopes_land_in_the_degrees_the_record_gives():
    """65-75 for the lower and 20-30 for the upper. The pack states them as rise-over-run, which is
    what a compiler can use, so the check is the trigonometry both ways."""
    import math
    rules = {(r["target_slot"], r["dimension"]): r for r in pack("facade-pavilion")["derived_rules"]}
    low = math.degrees(math.atan(float(rules[("roof_pitch", "mansard_lower_slope")]["expression"])))
    up = math.degrees(math.atan(float(rules[("roof_pitch", "upper_ratio")]["expression"])))
    assert 65.0 <= low <= 75.0, low
    assert 20.0 <= up <= 30.0, up
    assert "lower slope 65 to 75 degrees" in json.dumps(node("french-baroque"))


def test_the_avant_corps_is_the_shallower_projection_and_the_pavilion_also_rises():
    """A French front commonly has both, and giving them the same projection flattens the hierarchy
    the composition depends on. The pavilion's extra one to two metres of height is a separate rule
    precisely so the two cannot be conflated."""
    rules = {(r["target_slot"], r["dimension"]): r for r in pack("facade-pavilion")["derived_rules"]}
    assert ("composition_parti", "projection") in rules      # avant-corps, 1/8 to 1/6 of its width
    assert ("composition_parti", "ratio") in rules           # pavilion, 1/4 to 1/3 of its width
    h = rules[("wing_strategy", "pavilion_height")]
    assert "1 to 2 m of additional height" in h["authority_note"]
    assert 39.0 <= h["range"][0] and h["range"][1] <= 79.0   # one to two metres, in inches


def test_the_pavilion_is_measured_against_itself_and_not_against_the_range():
    """Worth noticing, because it is the French system's way of stating a projection: a wide pavilion
    projects further and stays in proportion. The corpus states it that way too."""
    r = next(x for x in pack("facade-pavilion")["derived_rules"]
             if x["target_slot"] == "composition_parti" and x["dimension"] == "ratio")
    assert "of its own width" in r["authority_note"]
    assert "1/4 to 1/3 of its own width" in json.dumps(node("french-renaissance-chateau"))


def test_the_baroque_curved_wall_is_not_attempted_and_the_pack_says_why():
    """WP-4.1 asks for 'a facade system for Baroque's curved-wall, accelerating bay rhythm'. Not one
    of the twenty-two Baroque-matching nodes gives a figure for an undulating elevation. The pack
    builds the avant-corps half of that item and leaves the curve on the list with a stated reason
    -- which is the project's rule about unjudged not being passed, applied to a whole list item."""
    n = pack("facade-pavilion")["notes"]
    assert "THE CURVED WALL IS NOT SUPPORTABLE FROM THIS CORPUS" in n
    assert "stays on the list, unbuilt and now with a stated reason" in n


def test_two_dimension_names_were_renamed_off_collisions_the_authoring_aid_found():
    """`roof_form`/`ratio` is `facade-picturesque`'s fraction of the elevation's width under the
    dominant roof, and `dormer`/`height` is `storey-graduation`'s dormer WINDOW. Both co-bind with
    this pack on three nodes apiece. Precedence would have resolved each silently in favour of
    whichever bound second, which is not a proportioning decision."""
    dims = {(r["target_slot"], r["dimension"]) for r in pack("facade-pavilion")["derived_rules"]}
    assert ("roof_form", "break_ratio") in dims and ("roof_form", "ratio") not in dims
    assert ("dormer", "lucarne_height") in dims and ("dormer", "height") not in dims
    assert ("roof_form", "ratio") in {(r["target_slot"], r["dimension"])
                                      for r in pack("facade-picturesque")["derived_rules"]}
    assert ("dormer", "height") in {(r["target_slot"], r["dimension"])
                                    for r in pack("storey-graduation")["derived_rules"]}


def test_the_pack_binds_to_eight_nodes_and_leads_the_two_that_had_no_facade_system():
    """`french-renaissance-chateau` had no facade pack at all -- WP-4.1's list said so -- and
    `french-eclectic` had `facade-picturesque` and two optionals, so its dormers had nothing saying
    where they go. Both now lead with this pack."""
    import glob as _glob
    bound = []
    for f in sorted(_glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = json.load(open(f))
        if any(e["pack"] == "facade-pavilion" for e in d.get("proportion_packs", [])):
            bound.append(d)
    assert len(bound) == 8
    assert set(pack("facade-pavilion")["applies_to"]) == {n["id"] for n in bound}
    for nid in ("french-renaissance-chateau", "french-eclectic", "chateauesque", "french-manoir"):
        entries = sorted(node(nid)["proportion_packs"], key=lambda e: e["precedence"])
        first_facade = next(e for e in entries if e["role"] == "facade")
        assert first_facade["pack"] == "facade-pavilion", nid


def test_second_empire_keeps_its_classical_primary_and_gains_the_roof_it_was_missing():
    """The American Second Empire front really is composed in classical layers. What
    `facade-classical` cannot express is a storey INSIDE the roof: its logic terminates the elevation
    at the cornice, and here the building continues for another sixty per cent of a storey above it."""
    entries = sorted(node("second-empire")["proportion_packs"], key=lambda e: e["precedence"])
    assert entries[0]["pack"] == "facade-classical" and entries[0]["role"] == "primary"
    assert entries[1]["pack"] == "facade-pavilion"
    assert "terminates the elevation at the cornice" in entries[1]["note"]
    attic = next(x for x in pack("facade-pavilion")["derived_rules"]
                 if x["target_slot"] == "height_proportion" and x["dimension"] == "attic_ratio")
    assert attic["range"] == [0.5, 0.7]


# --- jetty-overhang: the framed overhang, and four rules of thumb that disagree ----------------


def test_the_corpus_wrote_this_gap_down_itself_before_anyone_went_looking():
    """Fifth time in this package. `garrison-colonial`'s own binding note to `timber-bay` says no
    pack in the corpus dimensions a framed overhang and that its own figures are not recoverable
    from any of the 36 packs then available."""
    notes = " ".join(e.get("note", "") for e in node("garrison-colonial")["proportion_packs"])
    assert "no pack in this corpus dimensions a framed overhang" in notes
    assert "not recoverable from any of the 36 packs available" in notes
    assert any(e["pack"] == "jetty-overhang" for e in node("garrison-colonial")["proportion_packs"])


def test_the_module_is_the_joist_and_not_the_bay():
    """A jetty is not a division of a bay -- it is a cantilever, and a cantilever is dimensioned by
    the member cantilevering. Every record that gives a RULE rather than a number says so."""
    m = pack("jetty-overhang")["module"]
    assert m["default_size_in"] / m["parts"] == 1.0
    assert "THE MODULE IS THE JOIST AND NOT THE BAY" in m["note"]
    # and the pack declares the module as a rule, so a node can override it
    r = next(x for x in pack("jetty-overhang")["derived_rules"]
             if x["target_slot"] == "wall_thickness_frame")
    assert r["expression"] == "module" and r["range"] == [7.0, 18.0]


def test_four_records_give_four_multiples_and_the_pack_does_not_average_them():
    """2x from both garrisons, 1.33x from the English medieval frame, 1.0x from Tudor Revival. The
    reconciliation is that the three multiples measure three DIFFERENT failures -- sag, load, and
    plausibility -- so the rule is a band and it is marked judgment."""
    r = next(x for x in pack("jetty-overhang")["derived_rules"]
             if x["dimension"] == "joist_multiple")
    assert r["range"] == [1.0, 2.2] and r["judgment"] is True
    assert "THE THREE MULTIPLES MEASURE THREE DIFFERENT FAILURES" in r["note"]
    # each rule of thumb is checked against the record that states it, not against my summary
    for phrase, nid in [
        ("without a visible sag", "garrison-colonial"),
        ("one third of the joist depth times its span-to-depth allowance", "garrison-revival"),
        ("one third of the floor joist depth times four", "english-medieval-timber-frame"),
        ("never more than the depth of a plausible joist", "tudor-revival"),
    ]:
        assert phrase in json.dumps(node(nid)), (phrase, nid)
        assert phrase in json.dumps(pack("jetty-overhang")), phrase


def test_each_of_the_four_multiples_is_recomputed_from_its_own_records_figures():
    """Not asserted from the pack's prose -- derived from the style records themselves, so the
    reconciliation stands or falls on the corpus rather than on my summary of it."""
    # garrison-colonial: 14-20 in off a 7-9 in joist
    assert "Framed overhang 14–20 in" in json.dumps(node("garrison-colonial"), ensure_ascii=False)
    assert 1.5 <= 14 / 9 and 20 / 9 <= 2.3          # the band straddles 2x
    # english-medieval: 350-600 mm at a stated four thirds -> a 260-450 mm joist
    assert "350-600 mm" in json.dumps(node("english-medieval-timber-frame"))
    joist_mm_lo, joist_mm_hi = 350 / (4 / 3), 600 / (4 / 3)
    assert 250 <= joist_mm_lo and joist_mm_hi <= 460
    # and that is TWICE the colonial joist, which is why the longer jetty is the smaller multiple
    assert (joist_mm_lo / 25.4) > 9.0


def test_the_absolute_ceiling_of_two_feet_is_stated_twice_independently():
    """`garrison-colonial` 'never more than 24 in'; `garrison-revival` 'over 24 in. is implausible
    as joist cantilever'. Two authors, two centuries of subject matter, one number."""
    r = next(x for x in pack("jetty-overhang")["derived_rules"]
             if x["dimension"] == "jetty_projection")
    assert r["range"][1] == 24.0
    assert "never more than 24 in" in json.dumps(node("garrison-colonial"))
    assert "over 24 in. is implausible as joist cantilever" in json.dumps(node("garrison-revival"))


def test_the_floor_is_stated_twice_and_the_two_disagree_by_a_factor_of_two():
    """6 in (the detail stops reading as a soffit) against 300 mm (the shadow stops registering).
    Different walls, different tests; the band holds both rather than choosing."""
    r = next(x for x in pack("jetty-overhang")["derived_rules"]
             if x["dimension"] == "jetty_minimum")
    assert r["range"] == [6.0, 12.0]
    assert 300 / 25.4 <= r["range"][1]
    assert "reads as a siding error" in r["authority_note"]
    assert "the shadow line fails to register" in r["authority_note"]


def test_two_devices_and_the_second_one_is_not_a_cantilever_at_all():
    """The hewn overhang is a chamfer cut out of a single continuous post: no cantilever, no
    bressumer, and nothing for a drop to be the bottom of. Same shape of finding as
    `dutch-gambrel`'s two devices."""
    p = pack("jetty-overhang")
    assert set(p["assemblies"]) == {"framed_jetty", "hewn_overhang"}
    framed = next(m for m in p["assemblies"]["framed_jetty"]["members"] if m["id"] == "bressumer")
    hewn = next(m for m in p["assemblies"]["hewn_overhang"]["members"] if m["id"] == "post_shoulder")
    assert framed["projection_parts"] >= hewn["projection_parts"] * 3
    assert "look for the shadow, then measure" in json.dumps(p).lower().replace("--", "--")


def test_the_pendant_is_the_post_and_not_an_ornament_on_the_soffit():
    """Which is why 'applied plastic or foam drops void the variant' is a structural statement. The
    two records agree on the LENGTH exactly, three centuries apart, and differ on the diameter."""
    rules = {r["dimension"]: r for r in pack("jetty-overhang")["derived_rules"]}
    assert rules["pendant_length"]["range"] == [8.0, 14.0]
    assert rules["pendant_diameter"]["range"] == [4.0, 8.0]
    assert "8-14 in, diameter 4-6 in" in rules["pendant_length"]["authority_note"]
    assert "8-14 in. long" in rules["pendant_length"]["authority_note"]
    drop = next(m for m in pack("jetty-overhang")["assemblies"]["framed_jetty"]["members"]
                if m["id"] == "drop_pendant")
    assert "the carved lower end of the upper-storey post" in drop["name"]


def test_one_rule_is_the_exact_inverse_of_facade_pavilions_and_both_carry_one_value():
    """Same slot, same machinery, opposite instruction. There every opening must share one vertical
    axis; here the pendant rhythm and the window rhythm must NOT be reconciled, because one is the
    frame and the other is the fenestration."""
    mine = next(r for r in pack("jetty-overhang")["derived_rules"]
                if r["target_slot"] == "window_grouping_rule")
    theirs = next(r for r in pack("facade-pavilion")["derived_rules"]
                  if r["target_slot"] == "window_grouping_rule")
    assert mine["dimension"] == "post_independence" and theirs["dimension"] == "alignment"
    assert mine["range"] == theirs["range"] == [1.0, 1.0]
    assert mine["judgment"] is True and theirs["judgment"] is True
    assert "do not coincide with the window rhythm" in mine["authority_note"]


def test_the_dragon_beam_is_stated_as_a_length_because_the_angle_tells_a_compiler_nothing():
    """Root two times the projection. The beam bisects a right angle and the two jetties it serves
    are equal, so the arithmetic carries the 45 degrees and somebody gets a member to cut."""
    import math
    r = next(x for x in pack("jetty-overhang")["derived_rules"] if x["dimension"] == "dragon_length")
    p = pack("jetty-overhang")
    part = p["module"]["default_size_in"] / p["module"]["parts"]
    val = eval(r["expression"], {"module": p["module"]["default_size_in"], "part": part,
                                 "sqrt": math.sqrt})
    proj = next(x for x in p["derived_rules"] if x["dimension"] == "jetty_projection")
    projval = eval(proj["expression"], {"module": p["module"]["default_size_in"], "part": part})
    assert abs(val - projval * math.sqrt(2)) < 0.01
    assert r["range"][0] <= val <= r["range"][1]


def test_you_cannot_jetty_four_faces_because_the_joists_run_one_way():
    """Each corner turned costs a dragon beam. Which is why the town house jetties the street front
    and one flank, and the garrison jetties the front and returns at the ATTIC floor line, where a
    separate floor makes the other direction available again."""
    r = next(x for x in pack("jetty-overhang")["derived_rules"] if x["dimension"] == "jetty_faces")
    assert r["expression"] == "2" and r["judgment"] is True
    assert "every corner turned costs a dragon beam" in r["note"].lower()
    assert "sits at the attic floor line rather than the second-floor line" in \
        json.dumps(node("garrison-colonial"))


def test_the_projection_is_renamed_off_facade_classicals_string_band():
    """A belt course and a jetty are both horizontals at a floor line and they differ by a factor of
    seven. `facade-classical` co-binds on `garrison-revival`."""
    dims = {(r["target_slot"], r["dimension"]) for r in pack("jetty-overhang")["derived_rules"]}
    assert ("belt_course", "jetty_projection") in dims
    assert ("belt_course", "projection") not in dims
    assert ("belt_course", "projection") in {(r["target_slot"], r["dimension"])
                                             for r in pack("facade-classical")["derived_rules"]}


def test_the_revival_is_led_by_the_pack_because_nothing_else_defines_it():
    """'This is the parent style with a jettied second storey. Remove the overhang and the drops and
    nothing distinguishes it.' A variant defined by one device is led by that device's pack."""
    entries = sorted(node("garrison-revival")["proportion_packs"], key=lambda e: e["precedence"])
    assert entries[0]["pack"] == "jetty-overhang" and entries[0]["role"] == "primary"
    assert "nothing distinguishes it" in json.dumps(node("garrison-revival"))


def test_three_nodes_are_refused_and_each_refusal_has_a_stated_reason():
    """`french-normandy-revival` consumes one rule without being an instance of the type -- which is
    OQ 49. `new-england-colonial` has a jetty in one example record and not in the type.
    `english-cottage-vernacular` refuses itself in its own words."""
    n = pack("jetty-overhang")["notes"]
    assert "NOT BOUND, with reasons rather than silence" in n
    for nid in ("french-normandy-revival", "new-england-colonial", "english-cottage-vernacular"):
        assert nid in n, nid
    # RE-PINNED: OQ 49 was ruled and `french-normandy-revival` is now bound SCOPED to the one rule
    # it states -- which is what the refusal asked for. The other two stay refused.
    for nid in ("new-england-colonial", "english-cottage-vernacular"):
        assert not any(e["pack"] == "jetty-overhang"
                       for e in node(nid).get("proportion_packs", [])), nid
    fnr = next(e for e in node("french-normandy-revival")["proportion_packs"]
               if e["pack"] == "jetty-overhang")
    assert fnr["slots"] == ["material_change_rule"]
    assert "no jetty, no display" in json.dumps(node("english-cottage-vernacular"))
    assert "49." in _register_text()


# --- facade-portada: the panel as module, and a rationing rule stated as a count ---------------


def test_the_node_that_named_this_pack_by_name():
    """Sixth time the corpus wrote the gap down itself, and this one is explicit: Plateresque's
    `moorish-arch` binding note ends 'WP-4.1's own portada/retablo gap is the pack Plateresque
    actually needs and it is still missing.'"""
    notes = " ".join(e.get("note", "") for e in node("spanish-plateresque")["proportion_packs"])
    assert "portada/retablo gap is the pack Plateresque actually needs" in notes
    assert "no order pack in the library should be forced onto" in notes
    assert any(e["pack"] == "facade-portada"
               for e in node("spanish-plateresque")["proportion_packs"])


def test_the_module_is_the_panel_which_makes_it_the_only_top_down_pack_here():
    """Every other pack in the library derives from something small and real -- a diameter, a brick,
    an adobe, a joist, a light, a board. This one derives from the whole, because the corpus says
    so: a column inside a portada has not been proportioned, it has been FITTED."""
    m = pack("facade-portada")["module"]
    assert "THE MODULE IS THE PANEL AND NOT A MEMBER" in m["note"]
    assert "dimensioned to fill their register rather than to any canonical ratio" in \
        json.dumps(node("spanish-plateresque"))
    assert m["default_size_in"] / m["parts"] == 12.0


def test_the_two_parent_styles_disagree_about_the_module_and_that_is_the_difference():
    """Plateresque says the module is the panel. Churrigueresque says the estipite is 'the only
    continuous dimension in the design' -- a member module, bottom-up, of exactly the kind
    Plateresque abolished. The later, wilder style is in this one respect the more regular."""
    assert "the module is the ornamental panel and its frame" in \
        json.dumps(node("spanish-plateresque")).lower()
    assert "the only continuous dimension in the design is the estipite itself" in \
        json.dumps(node("churrigueresque"))
    assert "the more regular of the two" in pack("facade-portada")["notes"]


def test_the_rationing_rule_is_a_count_and_it_is_what_separates_the_styles():
    """Nine records state it and four state it as a count. The corpus itself calls mission-revival
    and spanish-colonial-revival 'the single most frequently confused pair in American
    architecture', and the difference between them is an integer."""
    r = next(x for x in pack("facade-portada")["derived_rules"]
             if x["dimension"] == "event_count")
    assert r["range"] == [0.0, 2.0] and r["judgment"] is True
    for phrase, nid in [
        ("permitted at exactly one location per building", "spanish-colonial-american"),
        ("Not more than one elaborated ornamental event per elevation", "andalusian-spanish-revival"),
        ("Not more than two elevations may carry worked ornament", "spanish-colonial-revival"),
        ("No ornament at the entrance", "mission-revival"),
    ]:
        assert phrase in json.dumps(node(nid)), (phrase, nid)
    assert "most frequently confused pair in American architecture" in json.dumps(node("mission-revival"))


def test_one_rule_gives_absence_a_minimum_size():
    """Twelve feet of unornamented wall on each side. The only rule in the corpus that dimensions
    the silence rather than the ornament -- and the effect of the whole system is contrast, so the
    plain wall is a designed element with a minimum, exactly as the panel is."""
    r = next(x for x in pack("facade-portada")["derived_rules"] if x["dimension"] == "plain_run")
    assert r["range"][0] == 144.0
    assert "minimum 12'0" in json.dumps(node("spanish-colonial-revival"))
    assert "run of unornamented wall on each side" in json.dumps(node("spanish-colonial-revival"))


def test_the_entablature_rule_is_the_exact_inverse_of_facade_pavilions_cornice_rule():
    """Same quantity, opposite extremes, both single-valued because neither has a partial version.
    A French cornice runs unbroken and the lucarne passes through it; a retablo facade's entablature
    is broken at every vertical and a continuous one converts the building into something else."""
    mine = next(r for r in pack("facade-portada")["derived_rules"]
                if r["target_slot"] == "entablature" and r["dimension"] == "continuity")
    theirs = next(r for r in pack("facade-pavilion")["derived_rules"]
                  if r["target_slot"] == "cornice" and r["dimension"] == "continuity")
    assert float(mine["expression"]) == 0.0 and mine["range"] == [0.0, 0.0]
    assert float(theirs["expression"]) == 1.0 and theirs["range"] == [1.0, 1.0]
    assert "become Italian Renaissance or Herreran" in mine["authority_note"]


def test_three_packs_in_this_tranche_now_write_to_window_grouping_rule_and_two_deny_alignment():
    """`facade-pavilion` requires the elevation's systems to coincide exactly; `jetty-overhang` and
    this one require them to stay apart. The library could previously state neither."""
    addrs = {pid: {(r["target_slot"], r["dimension"]) for r in pack(pid)["derived_rules"]}
             for pid in ("facade-pavilion", "jetty-overhang", "facade-portada")}
    assert ("window_grouping_rule", "alignment") in addrs["facade-pavilion"]
    assert ("window_grouping_rule", "post_independence") in addrs["jetty-overhang"]
    assert ("window_grouping_rule", "portada_independence") in addrs["facade-portada"]
    r = next(x for x in pack("facade-portada")["derived_rules"]
             if x["dimension"] == "portada_independence")
    assert r["range"] == [1.0, 1.0] and r["judgment"] is True
    # three records state it, and one declines to treat the mismatch as a problem at all
    assert "the conflict is not resolved" in r["authority_note"]


def test_the_estipite_is_definitional_and_its_arithmetic_is_recomputed_not_asserted():
    """Slenderness 1:8 to 1:11, pyramidal base 0.25-0.35 of shaft. Computed off the assembly's own
    members, so the encoded figures have to agree with the bands the record gives."""
    p = pack("facade-portada")
    est = p["assemblies"]["estipite"]
    shaft = sum(m["height_parts"] for m in est["members"])
    assert abs(shaft - est["height_modules"] * p["module"]["parts"]) < 1e-6
    assert 8.0 <= shaft <= 11.0                                    # one part wide
    base = next(m for m in est["members"] if m["id"] == "pyramid_base")["height_parts"]
    assert 0.25 <= base / shaft <= 0.35
    assert "not Churrigueresque" in json.dumps(node("churrigueresque"))


def test_the_panel_aspect_and_the_register_count_come_from_the_records():
    """1:2 to 1:3 in two to five registers, and the two parent records' register bands differ at the
    top because a Churrigueresque register is set by an estipite and is taller."""
    p = pack("facade-portada")
    assert 2.0 <= p["assemblies"]["retablo_registers"]["height_modules"] <= 3.0
    assert "Portada width to height roughly 1:2 to 1:3" in json.dumps(node("spanish-plateresque"))
    r = next(x for x in p["derived_rules"] if x["dimension"] == "register_count")
    assert r["range"] == [2.0, 5.0]
    assert "two to five stacked horizontal registers" in json.dumps(node("spanish-plateresque"))
    assert "height two to four registers" in json.dumps(node("churrigueresque"))


def test_the_thinnest_node_in_the_family_had_one_pack_and_its_own_note_doubted_it():
    """`churrigueresque` carried only `room-harmonic`, bound as a judgment 'with real doubt' and
    explicitly NOT for the portada. It now leads with the pack that is."""
    entries = sorted(node("churrigueresque")["proportion_packs"], key=lambda e: e["precedence"])
    assert entries[0]["pack"] == "facade-portada" and entries[0]["role"] == "facade"
    assert len(entries) == 2
    assert "real doubt" in entries[1]["note"]


def test_mission_revival_is_refused_and_it_is_oq_49_for_the_second_time_in_two_packs():
    """Its record carries a rule about this pack's subject stating that there is none -- the shape
    OQ 46 described for egyptian-revival's arch rule. Binding for that one rule would hand the node
    fourteen others including an estipite slenderness."""
    n = pack("facade-portada")["notes"]
    assert "NOT BOUND: `mission-revival`" in n
    assert "second instance of OQ 49 in two packs" in n
    # RE-PINNED: ruled 25 Aug 2026. Bound scoped to the single rule it carries.
    mr = next(e for e in node("mission-revival")["proportion_packs"]
              if e["pack"] == "facade-portada")
    assert mr["slots"] == ["ornament_vocabulary/event_count"]
    assert "Churrigueresque relief are forbidden" in json.dumps(node("mission-revival"))


def test_every_node_the_pack_binds_states_a_rationing_rule_of_its_own():
    """The pack's claim is that this family is defined by where ornament is NOT. Checked against all
    eight records rather than asserted -- if one of them says nothing about concentration, the
    binding is doing something other than what the pack says it does."""
    import re
    for nid in pack("facade-portada")["applies_to"]:
        blob = json.dumps(node(nid)).lower()
        assert re.search(r"ornament (is )?(confined|concentrated|rationed|permitted|almost wholly"
                         r" absent)|ornament budget|otherwise (blank|plain)|budget at the portada",
                         blob), nid


# --- facade-peristyle: the screen and the wall ------------------------------------------------


def test_the_two_antique_sources_had_no_facade_pack_at_all():
    """Eleven order packs proportion a column and not one says how many columns there are, where
    they stand, what they stand on, or what the wall behind them is doing."""
    for nid in ("greek-classical", "roman-classical"):
        entries = node(nid)["proportion_packs"]
        assert any(e["pack"] == "facade-peristyle" and e["role"] == "facade" for e in entries), nid
        others = [e for e in entries if e["pack"] != "facade-peristyle"]
        assert not any(e["role"] == "facade" for e in others), nid


def test_the_only_closed_form_count_rule_in_the_corpus():
    """n_flank = 2 x n_front + 1. A Greek peristyle's plan proportion is computed from one integer
    rather than chosen, and the expression keeps the formula visible in the data."""
    r = next(x for x in pack("facade-peristyle")["derived_rules"]
             if x["dimension"] == "flank_count")
    assert r["expression"] == "2 * 6 + 1"
    assert eval(r["expression"]) == 13
    for front, flank in [(6, 13), (8, 17)]:                      # both pairs the record gives
        assert 2 * front + 1 == flank
        assert r["range"][0] <= flank <= r["range"][1]
    assert "n_flank = 2 x n_front + 1 (6x13, 8x17)" in json.dumps(node("greek-classical"))


def test_the_only_rule_that_is_a_function_and_its_residual_is_reported_not_tuned_away():
    """Vitruvius gives three points -- (1.5,10), (2.25,9.5), (4.0,8) -- and they fall on a line. The
    pack states the line and returns 9.4 at eustyle against a recorded 9.5."""
    r = next(x for x in pack("facade-peristyle")["derived_rules"]
             if x["dimension"] == "height_by_spacing")
    f = lambda d: 11.2 - 0.8 * d
    assert abs(f(1.5) - 10.0) <= 0.1 and abs(f(4.0) - 8.0) <= 0.1
    assert abs(f(2.25) - 9.5) <= 0.15                            # the residual, stated in the note
    assert abs(eval(r["expression"]) - f(2.25)) < 1e-9
    assert "9.4 against the record's 9.5" in r["note"]
    assert "pycnostyle, 9.5 at eustyle, 8 at araeostyle" in json.dumps(node("roman-classical"))


def test_five_independent_records_put_the_intercolumniation_floor_at_2_point_25_exactly():
    """The strongest agreement found in this work package, and it shows the revival is more uniform
    than either of its sources -- because 2.25 is Vitruvius's eustyle and the revival worked from
    the book while the ancients worked from the buildings."""
    r = next(x for x in pack("facade-peristyle")["derived_rules"]
             if x["dimension"] == "intercolumniation_revival")
    assert r["range"] == [2.25, 3.0]
    for nid in ("neoclassical-revival", "english-palladian", "greek-revival-american",
                "greek-revival-northern", "jeffersonian-classicism"):
        assert "2.25" in json.dumps(node(nid)), nid
    greek = next(x for x in pack("facade-peristyle")["derived_rules"]
                 if x["dimension"] == "intercolumniation_greek")
    roman = next(x for x in pack("facade-peristyle")["derived_rules"]
                 if x["dimension"] == "intercolumniation_roman")
    # narrower than either source
    assert (r["range"][1] - r["range"][0]) < (greek["range"][1] - greek["range"][0]) + 0.3
    assert (r["range"][1] - r["range"][0]) < (roman["range"][1] - roman["range"][0])


def test_the_screen_and_the_wall_has_four_settlements_and_the_corpus_gives_all_four():
    """Greece: nothing to reconcile. Rome: the wall governs. The Southern plantation: the wall
    governs the other way. Neoclassical Revival: neither, and the mismatch is characteristic."""
    r = next(x for x in pack("facade-peristyle")["derived_rules"]
             if x["dimension"] == "screen_offset")
    assert r["judgment"] is True and r["range"] == [0.0, 2.0]
    assert "characteristic mismatch between screen and wall" in json.dumps(node("neoclassical-revival"))
    assert "reconciled by choosing an intercolumniation that suits the required arch span" in \
        json.dumps(node("roman-classical"))
    assert "column spacing is set by the bay of the house behind" in \
        json.dumps(node("greek-revival-southern-plantation"))
    assert "sets the bay module for the wall behind it" in json.dumps(node("greek-revival-northern"))
    # four columns over five bays, six over seven: the offset is one in both cases
    for cols, bays in [(4, 5), (6, 7)]:
        assert bays - cols == 1


def test_four_packs_in_this_tranche_now_write_to_window_grouping_rule():
    """One requires exact alignment, two require independence, and this one says the answer is a
    design decision with four historical precedents."""
    dims = {pid: {r["dimension"] for r in pack(pid)["derived_rules"]
                  if r["target_slot"] == "window_grouping_rule"}
            for pid in ("facade-pavilion", "jetty-overhang", "facade-portada", "facade-peristyle")}
    assert dims["facade-pavilion"] == {"alignment"}
    assert dims["jetty-overhang"] == {"post_independence"}
    assert dims["facade-portada"] == {"portada_independence"}
    assert dims["facade-peristyle"] == {"screen_offset"}


def test_the_corner_contraction_is_forced_rather_than_chosen():
    """A triglyph over every axis AND a triglyph flush at the corner are geometrically incompatible
    at constant spacing. Nobody decided it; it fell out -- which is why its absence dates a
    building at a glance."""
    r = next(x for x in pack("facade-peristyle")["derived_rules"]
             if x["dimension"] == "corner_contraction")
    assert "geometrically impossible at constant spacing" in json.dumps(node("greek-classical"))
    assert "single most reliable proof of authentic Doric grammar" in r["authority_note"]
    assert "almost never contract" in json.dumps(node("greek-classical"))


def test_the_greek_assembly_reproduces_the_parthenon_and_the_roman_one_vitruvius():
    """Recomputed from the members, not asserted: 5.48 diameters and a third of the column for
    Greece, 9.5 diameters and a quarter for Rome."""
    p = pack("facade-peristyle")
    g = {m["id"]: m["height_parts"] for m in p["assemblies"]["peristyle_bay"]["members"]}
    col = g["shaft"] + g["capital"]
    ent = g["architrave"] + g["frieze"] + g["cornice"]
    assert abs(col / p["module"]["parts"] * 2.45 - 5.48) < 0.02      # Parthenon Doric
    assert 0.30 <= ent / col <= 0.34                                  # about one third
    r = {m["id"]: m["height_parts"] for m in p["assemblies"]["arch_order_bay"]["members"]}
    rcol = r["engaged_shaft"] + r["engaged_capital"]
    assert abs(rcol / p["module"]["parts"] * 3.25 - 9.5) < 0.02       # eustyle
    assert 0.24 <= r["entablature"] / rcol <= 0.26                    # about one quarter
    assert 0.20 <= r["podium"] / rcol <= 0.333                        # the podium band


def test_the_pack_states_no_portico_depth_rule_and_says_why():
    """That wall-face-to-column-centreline dimension is `balcony-gallery`'s gallery depth, and
    neoclassical-revival's own constraint note already says so. A collision avoided by not writing
    the rule at all, which is the cleanest form of the fix."""
    dims = {(r["target_slot"], r["dimension"]) for r in pack("facade-peristyle")["derived_rules"]}
    assert not any(s == "porch_depth" for s, _ in dims)
    c = next(x for x in pack("facade-peristyle")["conflicts"] if x["with"] == "climate")
    assert "balcony-gallery" in c["resolution"]
    assert "gallery_depth_ft applies" in json.dumps(node("neoclassical-revival"))


def test_the_podium_is_the_argument_and_the_accessibility_conflict_follows_from_it():
    """One face is what made the Roman temple front adaptable as a courthouse and the Greek one not
    -- and it is also why the accessible entrance lands on the elevation the composition calls the
    back."""
    r = next(x for x in pack("facade-peristyle")["derived_rules"]
             if x["dimension"] == "podium_ratio")
    assert r["range"] == [0.2, 0.333]
    assert "loses the frontality that distinguishes it from Greek work" in r["authority_note"]
    c = next(x for x in pack("facade-peristyle")["conflicts"] if x["with"] == "accessibility-code")
    assert c["severity"] == "blocking"
    assert "adaptable as a facade for a courthouse or a bank" in json.dumps(node("roman-classical"))


def test_egyptian_revival_stays_unbound_and_it_is_oq_49_for_the_third_time():
    """Two of the pack's rules fit it exactly and thirteen do not. It is the corpus's one
    deliberately unbound buildable node, and OQ 49's proposal would bind the last one."""
    n = pack("facade-peristyle")["notes"]
    assert "THIRD INSTANCE OF OQ 49 IN THREE PACKS" in n
    # RE-PINNED: the ruling landed and the pack's own prediction came true -- the corpus's last
    # unbound node is bound, scoped to the two rules that fit.
    er = next(e for e in node("egyptian-revival")["proportion_packs"]
              if e["pack"] == "facade-peristyle")
    assert er["slots"] == ["column/front_count", "column/intercolumniation_roman"]
    assert "Column height 4 to 5.5 shaft diameters" in json.dumps(node("egyptian-revival"))
    assert "never a repeating march of equal bays" in json.dumps(node("egyptian-revival"))
    # and the overlap the pack claims is real: Archaic Doric is squatter than the "squattest revival"
    assert "Archaic Paestum ~4.3" in json.dumps(node("greek-classical"))
    assert 4.3 < 4.5


# --- corbel-course: how a masonry wall gets an overhang ---------------------------------------


def test_three_records_wrote_this_gap_down_and_one_kept_the_figures_for_it():
    """`mudejar`'s own binding note, `queen-anne-patterned-masonry`'s constraint note, and
    `stone-course`, which declined the Scottish bartizan and quoted its numbers into its own notes
    so they would not be lost."""
    assert "whole-brick corbelling and offsetting" in \
        " ".join(e.get("note", "") for e in node("mudejar")["proportion_packs"])
    assert "no chimney-cap-projection concept" in json.dumps(node("queen-anne-patterned-masonry"))
    assert "entirely missing" in pack("stone-course")["notes"]
    for nid in ("mudejar", "queen-anne-patterned-masonry", "scottish-baronial"):
        assert any(e["pack"] == "corbel-course" for e in node(nid)["proportion_packs"]), nid


def test_the_list_named_one_instance_of_a_class_again():
    """WP-4.1 asked for 'a Mudejar brick corbelling module'. Measured, the device is in four
    unrelated traditions with figures -- Spanish brick, Scottish stone, Anglo-American moulded
    brick, and Mediterranean tile -- because a masonry wall has one way to get an overhang."""
    p = pack("corbel-course")
    assert set(p["applies_to"]) == {"mudejar", "moorish-andalusian", "scottish-baronial",
                                    "queen-anne-patterned-masonry", "tuscan-vernacular",
                                    "french-provincial-farmhouse"}
    assert "THE LIST NAMED ONE INSTANCE OF A CLASS" in p["notes"]


def test_this_packs_module_is_brick_courses_part_exactly():
    """`brick-course`'s module is four courses on the mason's gauge rod, 11 in in 4 parts. This
    pack's module is one of those parts. The two interlock rather than compete."""
    mine = pack("corbel-course")["module"]
    theirs = pack("brick-course")["module"]
    assert abs(mine["default_size_in"] - theirs["default_size_in"] / theirs["parts"]) < 1e-9
    assert mine["default_size_in"] / mine["parts"] == 0.25


def test_it_is_jetty_overhangs_sibling_and_the_reconstruction_has_the_same_shape():
    """A timber wall cantilevers a joist; a masonry wall steps a course. Both packs recover a
    per-unit multiple by dividing each record's total by its own count, and both find three
    traditions agreeing and one outlier explained by what is actually being resisted."""
    mine = next(r for r in pack("corbel-course")["derived_rules"]
                if r["dimension"] == "step_ratio")
    theirs = next(r for r in pack("jetty-overhang")["derived_rules"]
                  if r["dimension"] == "joist_multiple")
    assert mine["judgment"] is True and theirs["judgment"] is True
    assert mine["range"] == [0.4, 1.2] and theirs["range"] == [1.0, 2.2]
    assert "A TILE CORBEL IS NOT LIMITED BY ITS BED DEPTH BUT BY ITS LENGTH" in mine["note"]
    assert "`jetty-overhang`'S SIBLING" in pack("corbel-course")["notes"]


def test_the_step_ratio_is_recomputed_from_each_records_own_figures():
    """Queen Anne 3-6 in over 2-3 courses of 2.5-3 in; Tuscan 300-600 mm over 2-3 tile courses. The
    first lands in the band and the second does not, which is the finding."""
    r = next(x for x in pack("corbel-course")["derived_rules"] if x["dimension"] == "step_ratio")
    lo, hi = r["range"]
    # Queen Anne: the record's own two figures
    assert "brick course height 2.5 to 3 in" in json.dumps(node("queen-anne-patterned-masonry"))
    assert "projecting 3 to 6 in" in json.dumps(node("queen-anne-patterned-masonry"))
    qa_lo, qa_hi = (3.0 / 3) / 3.0, (6.0 / 2) / 2.5          # 0.33 .. 1.2
    assert qa_hi <= hi + 1e-9
    # Tuscan: 300-600 mm over 2-3 courses of a ~40 mm canal tile -- far outside
    assert "300-600 mm" in json.dumps(node("tuscan-vernacular"))
    assert (300.0 / 3) / 40.0 > hi


def test_the_dogtooth_projection_is_arithmetic_and_not_a_choice():
    """A unit turned 45 degrees in plan projects (root2 - 1) / 2 of its width -- 0.2071. On a 140 mm
    ladrillo that is 29 mm and a designer cannot adjust it without changing the brick."""
    import math
    k = (math.sqrt(2) - 1) / 2
    assert abs(k - 0.2071) < 0.001
    r = next(x for x in pack("corbel-course")["derived_rules"]
             if x["dimension"] == "dogtooth_projection")
    assert "0.2071" in r["authority_note"]
    assert abs(140 * k - 29) < 1.0                            # the Mudejar ladrillo, in mm
    p = pack("corbel-course")
    part = p["module"]["default_size_in"] / p["module"]["parts"]
    assert r["range"][0] <= eval(r["expression"], {"part": part}) <= r["range"][1]


def test_two_traditions_forbid_the_moulded_unit_and_one_is_defined_by_it():
    """A switch, not a scale, and the pack does not reconcile them. A Mudejar band built from
    moulded specials has lost the argument it exists to make."""
    r = next(x for x in pack("corbel-course")["derived_rules"]
             if x["dimension"] == "moulded_units")
    assert r["range"] == [0.0, 1.0] and r["judgment"] is True
    assert "Carved, moulded or cast brick profiles are prohibited" in json.dumps(node("mudejar"))
    assert "moulded brick panels set into a brick field" in \
        json.dumps(node("queen-anne-patterned-masonry"))


def test_one_rule_is_a_social_fact_and_is_kept_as_one():
    """The genoise's course count. The only quantity in this library stated as a declaration of
    wealth rather than as a consequence of structure, material or optics."""
    r = next(x for x in pack("corbel-course")["derived_rules"]
             if x["dimension"] == "corbel_courses")
    assert "statement of the owner's standing" in r["note"]
    assert "a statement of the owner's standing" in json.dumps(node("french-provincial-farmhouse"))
    assert r["range"] == [2.0, 5.0]


def test_the_rationing_finding_is_now_four_traditions_and_looks_general():
    """`facade-portada` found nine Spanish records saying ornament works by being bounded and read
    it as Iberian. Mudejar, Queen Anne and Scottish Baronial say it too, with nothing in common."""
    n = pack("corbel-course")["notes"]
    assert "It is not: four traditions with nothing in common" in n
    assert "not more than 25 percent of any elevation" in json.dumps(node("queen-anne-patterned-masonry"))
    assert "The lower two storeys must remain plain walling" in json.dumps(node("scottish-baronial"))
    assert any(r["dimension"] == "wall_head_share" for r in pack("corbel-course")["derived_rules"])
    assert any(r["dimension"] == "event_count" for r in pack("facade-portada")["derived_rules"])


def test_the_word_corbel_names_two_things_and_the_pack_owns_one():
    """`pueblo-revival` and `new-mexico-adobe` corbels are zapatas -- carved wooden brackets under a
    portal beam, 30-42 in long. A bracket, not a stepped course. The fifth time in this package a
    keyword measurement over-counted, and the first by ambiguity rather than by breadth."""
    n = pack("corbel-course")["notes"]
    assert "It is a homonym" in n
    for nid in ("pueblo-revival", "new-mexico-adobe", "chateauesque"):
        assert not any(e["pack"] == "corbel-course"
                       for e in node(nid).get("proportion_packs", [])), nid
    assert "corbels 30-42 in. long" in json.dumps(node("pueblo-revival"))
    assert "corbelled turrets" in json.dumps(node("chateauesque"))


def test_chateauesque_is_refused_because_lending_it_a_scottish_figure_would_invent_one():
    """It has corbelled turrets and massive corbelled chimneys and gives no dimension for either."""
    assert "lending it to a French-derived turret would be inventing a measurement" in \
        pack("corbel-course")["notes"]
    blob = json.dumps(node("chateauesque"))
    import re
    assert not re.search(r"corbel[^\".]{0,80}\d+\s*(mm|in\b|ft)", blob)


def test_the_two_thinnest_bound_nodes_gain_a_pack():
    """`mudejar` and `moorish-andalusian` carried two apiece and their own notes named this gap."""
    for nid in ("mudejar", "moorish-andalusian"):
        entries = node(nid)["proportion_packs"]
        assert len(entries) == 3, nid
        assert {e["pack"] for e in entries} == {"moorish-arch", "corbel-course", "facade-arcade"}, nid


# --- facade-medieval-english: the facade generated from behind ---------------------------------


def test_four_records_say_the_facade_is_not_the_unit_of_composition():
    """Every classical pack here composes an elevation and lets the plan follow. This one says the
    elevation is a RESULT -- and four records, spanning four centuries, say so independently."""
    r = next(x for x in pack("facade-medieval-english")["derived_rules"]
             if x["dimension"] == "bay_primacy")
    assert r["range"] == [1.0, 1.0] and r["judgment"] is True
    for phrase, nid in [
        ("the bay, not the facade, is the unit of composition", "english-gothic"),
        ("dictated by the frame rather than the other way round", "english-medieval-timber-frame"),
        ("Windows do not establish a rhythm of their own", "norman-romanesque-english"),
        ("Windows are placed where rooms need them", "tudor"),
    ]:
        assert phrase in json.dumps(node(nid)), (phrase, nid)
    # and facade-classical's module really is an elevation-first quantity
    assert "principal elevation" in pack("facade-classical")["module"]["name"]


def test_the_english_medieval_bay_is_the_length_of_a_tree():
    """Four records, four centuries, four structural systems -- groin vault, rib vault, oak box
    frame, shaped gable -- and one band, because all four are limited by the same timber."""
    m = pack("facade-medieval-english")["module"]
    assert 118.0 <= m["default_size_in"] <= 217.0            # 3.0 - 5.5 m
    assert "length of sound oak a carpenter could get, roughly 4.5 m at the limit" in \
        json.dumps(node("english-medieval-timber-frame"))
    for nid in ("norman-romanesque-english", "english-gothic", "english-medieval-timber-frame"):
        assert "3.0-5.0 m" in json.dumps(node(nid)) or "3.5-5.0 m" in json.dumps(node(nid)), nid
    assert "3.5-5.5 m" in json.dumps(node("jacobean"))       # arrived at as a gable width


def test_two_mechanisms_of_convergence_one_textual_and_one_material():
    """`facade-peristyle`'s five revival records converge on 2.25 diameters because they were all
    reading Vitruvius. These four converge on four metres because they were all buying from the same
    forest."""
    assert "TWO MECHANISMS OF CONVERGENCE" in pack("facade-medieval-english")["notes"]
    assert "learns from a text converges" in pack("facade-peristyle")["notes"]


def test_the_pointed_arch_halves_the_pier_and_the_record_states_its_own_comparison():
    """1:4 to 1:6 Gothic 'against 1:2 to 1:3 in Norman work'. The whole structural dividend of
    Gothic as a number, and the Perpendicular window is where the process ends."""
    rules = {r["dimension"]: r for r in pack("facade-medieval-english")["derived_rules"]}
    g, n = rules["pier_ratio_gothic"], rules["pier_ratio_norman"]
    assert g["range"][1] <= n["range"][0]                     # the bands do not overlap
    assert abs(float(g["expression"]) * 2 - float(n["expression"])) < 1e-9   # exactly half
    assert "against 1:2 to 1:3 in Norman work" in json.dumps(node("english-gothic"))
    # and the two window proportions bracket the same three centuries
    assert rules["lancet_ratio"]["range"] == [4.0, 6.0]
    assert rules["perpendicular_ratio"]["range"] == [2.0, 3.0]


def test_the_norman_rise_is_a_definition_not_a_judgment():
    """A semicircle has one rise. What makes it a rule is the consequence: span sets height
    throughout, so the elevation is determined by the plan's spans."""
    r = next(x for x in pack("facade-medieval-english")["derived_rules"]
             if x["dimension"] == "norman_rise")
    assert float(r["expression"]) == 0.5 and r["range"] == [0.5, 0.5]
    assert r["judgment"] is False
    assert "the defining and non-negotiable ratio" in json.dumps(node("norman-romanesque-english"))
    assert "freedom from a fixed rise:span ratio" in json.dumps(node("english-gothic"))


def test_one_rule_runs_backwards_and_nothing_else_in_the_library_does():
    """Elizabethan storeys increase upward to mark the ascent to the state rooms -- 'the exact
    inverse of the Georgian rule'. Storey graduation is usually explained as an optical correction;
    here is a tradition doing the opposite for a ceremonial reason."""
    r = next(x for x in pack("facade-medieval-english")["derived_rules"]
             if x["dimension"] == "ascent_ratio")
    assert r["range"] == [1.0, 1.4] and float(r["expression"]) > 1.0
    assert "the exact inverse of the Georgian rule" in json.dumps(node("elizabethan"))
    # and the pack also carries the rule that refuses graduation outright
    eq = next(x for x in pack("facade-medieval-english")["derived_rules"]
              if x["dimension"] == "storey_equality")
    assert eq["range"] == [1.0, 1.1]
    assert "most clearly separates Tudor from Georgian at a glance" in json.dumps(node("tudor"))


def test_the_glazing_band_is_a_history_and_the_retreat_is_deliberate():
    """Elizabethan 45-60 and higher at Hardwick; Jacobean 30-45. The next generation heard the
    jibe. `opening-mullioned` found the same retreat from the window's side."""
    r = next(x for x in pack("facade-medieval-english")["derived_rules"]
             if x["dimension"] == "glazed_share")
    assert r["range"] == [0.3, 0.6]
    assert "45-60 percent" in json.dumps(node("elizabethan"))
    assert "30-45 percent" in json.dumps(node("jacobean"))


def test_the_fifth_instance_of_the_mismatch_and_the_second_use_of_the_word_characteristic():
    """Jacobean gables against window bays, and Neoclassical Revival's screen against its wall. Two
    centuries and two countries apart, almost the same sentence."""
    r = next(x for x in pack("facade-medieval-english")["derived_rules"]
             if x["dimension"] == "gable_alignment")
    assert r["judgment"] is True
    assert "the mismatch is characteristic rather than a fault" in json.dumps(node("jacobean"))
    assert "the characteristic mismatch between screen and wall" in \
        json.dumps(node("neoclassical-revival"))
    # five packs in this tranche now write to the slot
    writers = [pid for pid in ("facade-pavilion", "jetty-overhang", "facade-portada",
                               "facade-peristyle", "facade-medieval-english")
               if any(x["target_slot"] == "window_grouping_rule"
                      for x in pack(pid)["derived_rules"])]
    assert len(writers) == 5


def test_the_pack_writes_one_slot_twice_and_says_it_is_a_menu_not_a_collision():
    """OQ 48's case (i): several rules at one address within one pack, deliberately, with the notes
    saying so. Here they are about two different pairs of systems on one wall."""
    dims = [r["dimension"] for r in pack("facade-medieval-english")["derived_rules"]
            if r["target_slot"] == "window_grouping_rule"]
    assert sorted(dims) == ["bay_primacy", "gable_alignment"]
    assert "deliberate menu OQ 48 describes" in pack("facade-medieval-english")["notes"]


def test_the_buttress_projection_is_measured_against_itself_like_the_french_pavilion():
    """Two unrelated traditions stating a projection the same way, and for the same reason: the
    element is a mass in its own right rather than a modulation of the wall."""
    mine = next(x for x in pack("facade-medieval-english")["derived_rules"]
                if x["dimension"] == "buttress_projection")
    theirs = next(x for x in pack("facade-pavilion")["derived_rules"]
                  if x["target_slot"] == "composition_parti" and x["dimension"] == "ratio")
    assert "of its own width" in mine["authority_note"]
    assert "of its own width" in theirs["authority_note"]
    # and the buttress diminishes, which is the half that revival work gets wrong
    m = {x["id"]: x["projection_parts"]
         for x in pack("facade-medieval-english")["assemblies"]["buttress_stage"]["members"]}
    assert m["base_stage"] > m["middle_stage"] > m["upper_stage"]


def test_the_great_hall_is_as_high_as_it_is_wide_and_got_there_from_a_fire():
    """`room-harmonic` would derive a cubical room from the arithmetic mean. This one is that shape
    because it was heated by an open hearth in the middle of the floor."""
    r = next(x for x in pack("facade-medieval-english")["derived_rules"]
             if x["dimension"] == "hall_plate")
    assert r["range"] == [0.9, 1.1]
    assert "wall-plate height roughly equal to width" in json.dumps(node("english-gothic"))
    assert "got there from a fire" in r["note"]


def test_five_of_the_six_nodes_had_no_facade_role_pack():
    """The last item on WP-4.1's list, and it was new only in that two existing items turned out to
    be one pack seen from two sides."""
    p = pack("facade-medieval-english")
    assert len(p["applies_to"]) == 6
    without = [nid for nid in p["applies_to"]
               if not any(e["role"] == "facade" and e["pack"] != "facade-medieval-english"
                          for e in node(nid)["proportion_packs"])]
    assert len(without) == 5, without          # only jacobean already carried facade-gable
    assert "LAST ITEM ON WP-4.1'S LIST" in p["notes"]


def test_the_rationing_pattern_reaches_five_traditions():
    """Nine Spanish records, then Mudejar, Queen Anne and Scottish Baronial, and now the Elizabethan
    frontispiece. It should be treated as a property of this corpus and tested properly."""
    r = next(x for x in pack("facade-medieval-english")["derived_rules"]
             if x["dimension"] == "frontispiece_share")
    assert r["range"] == [0.25, 0.333]
    assert "frontispiece only" in json.dumps(node("elizabethan"))
    assert "Five traditions with nothing in common" in pack("facade-medieval-english")["notes"]
    assert "four traditions with nothing in common" in pack("corbel-course")["notes"]


# --- the sixth over-count, corrected -----------------------------------------------------------


def test_the_oq47_evidence_was_inflated_and_the_corrected_set_is_seven_rules_in_three_packs():
    """The worst of this package's six keyword over-counts, because it happened inside the sentence
    arguing FOR a ruling. `trim-sawn`'s brackets are on `modillion_dentil` -- a modillion IS a
    bracket -- and `facade-portada`'s estipite is a genuine pilaster. Neither was a compromise."""
    import glob
    routed = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
        d = json.load(open(f))
        for r in d.get("derived_rules", []):
            if r["target_slot"] in ("corner_board", "pilaster"):
                routed.setdefault(d["id"], []).append(r["dimension"])
    # the three that were genuinely compromised (dimensions as they were before the migration)
    # RE-PINNED after the migration: the seven now sit on `expressed_frame`, and what the test
    # still protects is that facade-portada and trim-sawn were never part of the set.
    compromised = {"timber-panel", "jetty-overhang", "facade-medieval-english"}
    moved = {pid: [r["dimension"] for r in pack(pid)["derived_rules"]
                   if r["target_slot"] == "expressed_frame"] for pid in compromised}
    assert sum(len(v) for v in moved.values()) == 7
    assert not any(k in routed for k in compromised)
    # and the two that were miscounted are on the right slots
    assert set(routed["facade-portada"]) == {"slenderness", "base_ratio"}     # a real pilaster
    assert "trim-sawn" not in routed
    brackets = [r["target_slot"] for r in pack("trim-sawn")["derived_rules"]
                if "bracket" in r["note"].lower()]
    assert "modillion_dentil" in brackets


def test_the_correction_is_recorded_where_the_wrong_number_was_stated():
    """Prose stays beside the test, and a superseded claim is corrected in place rather than
    deleted, so what was believed stays legible beside what is true."""
    oq = _register_text()
    assert "CORRECTED 25 Aug 2026, and the correction is the point" in oq
    assert "7 rules in 3 packs" in oq
    assert "An earlier draft of this note said FIVE PACKS and was wrong" in \
        json.dumps(pack("facade-medieval-english"))


def test_oq_7_through_11_are_environment_blocked_with_the_probe_recorded():
    """All five need a legible facsimile, not code. Recording the probe stops them reading as
    unstarted work, and the warning against closing them from a secondary source is the point."""
    oq = _register_text()
    assert "7 through 11 are ENVIRONMENT-BLOCKED, not unstarted" in oq
    assert "babel.hathitrust.org" in oq
    assert "Do not close any of them from a\nsecondary source or a modern redrawing" in oq


# --- OQ 47 closed: expressed_frame at ontology 0.7.0 -------------------------------------------


def _slot(sid):
    d = json.load(open(os.path.join(ROOT, "elements", "slots.json")))
    return next(s for g in d["groups"] for s in g["slots"] if s["id"] == sid)


def test_the_slot_exists_in_the_envelope_group_beside_the_one_it_stood_in_for():
    d = json.load(open(os.path.join(ROOT, "elements", "slots.json")))
    env = next(g for g in d["groups"] if g["id"] == "envelope")
    ids = [s["id"] for s in env["slots"]]
    assert ids.index("expressed_frame") == ids.index("corner_board") + 1
    assert d["version"] == "0.7.0"


def test_member_status_is_the_field_the_slot_was_added_for():
    """`structural`, `structural-and-expressed`, `applied`, `none`. Without it the corpus cannot
    tell a frame from a picture of one."""
    f = next(x for x in _slot("expressed_frame")["fields"] if x["id"] == "member_status")
    assert f["required"] is True
    assert set(f["examples"]) == {"structural", "structural-and-expressed", "applied", "none"}
    assert "THE FIELD THE SLOT WAS ADDED FOR" in f["note"]
    assert "legitimate tradition and not an accusation" in f["note"]


def test_the_seven_rules_moved_and_left_nothing_behind():
    """timber-panel 4, jetty-overhang 2, facade-medieval-english 1. Nothing of that class is left
    on corner_board, and the migration is recorded in each rule's own note."""
    moved = {}
    for pid in ("timber-panel", "jetty-overhang", "facade-medieval-english"):
        p = pack(pid)
        moved[pid] = [r["dimension"] for r in p["derived_rules"]
                      if r["target_slot"] == "expressed_frame"]
        assert not any(r["target_slot"] == "corner_board" for r in p["derived_rules"]), pid
        for r in p["derived_rules"]:
            if r["target_slot"] == "expressed_frame":
                assert "MIGRATED to `expressed_frame` at ontology 0.7.0" in r["note"], (pid, r)
    assert sorted(moved["timber-panel"]) == ["brace_ratio", "face_width", "projection", "spacing"]
    assert sorted(moved["jetty-overhang"]) == ["dragon_length", "return_depth"]
    assert moved["facade-medieval-english"] == ["buttress_projection"]
    # and facade-portada's estipite stayed on pilaster, where it was always right
    assert all(r["target_slot"] == "pilaster"
               for r in pack("facade-portada")["derived_rules"]
               if r["dimension"] in ("slenderness", "base_ratio"))


def test_fourteen_kits_bind_it_and_five_of_them_forbid_the_member():
    """A rule ABOUT the member which states that there is none is the same argument that got `arch`
    built at 0.6.0. Five styles define themselves partly by refusing it."""
    import glob
    bound = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        k = json.load(open(path))
        e = k["slots"]["expressed_frame"]
        if e.get("binding") in ("specified", "forbidden"):
            bound[k["style"]] = (e["binding"], e["variants"][0]["id"])
    assert len(bound) == 14
    forbidden = {n for n, (b, _) in bound.items() if b == "forbidden"}
    assert forbidden == {"jacobethan-revival", "prairie-school", "shingle-style",
                         "mediterranean-revival", "spanish-colonial-revival"}
    assert all(bound[n][1] == "none" for n in forbidden)


def test_three_sibling_revivals_take_three_positions_on_one_member():
    """tudor-revival applies it, jacobethan-revival forbids it and is DEFINED by the absence, and
    english-medieval-timber-frame has the real thing. That is what the field is for."""
    import glob
    st = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        k = json.load(open(path))
        e = k["slots"]["expressed_frame"]
        if e.get("variants"):
            st[k["style"]] = e["variants"][0]["id"]
    assert st["english-medieval-timber-frame"] == "structural"
    assert st["tudor-revival"] == "applied"
    assert st["jacobethan-revival"] == "none"
    assert "defined by its absence" in json.dumps(node("jacobethan-revival"))
    # and the Spanish revival family is told apart at the eave by this field
    assert st["mission-revival"] == "structural-and-expressed"
    assert st["spanish-colonial-revival"] == "none"
    assert st["mediterranean-revival"] == "none"


def test_member_status_is_a_variant_not_a_parameter_because_it_carries_no_unit():
    """The kit checker insists every dimensional parameter carries a unit and is right to. A
    categorical belongs in `variants`, where `construction_type` already puts one."""
    import glob
    for path in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        e = json.load(open(path))["slots"]["expressed_frame"]
        assert "parameters" not in e, path


# --- OQ 49 closed: scoped bindings, and 132 of 132 --------------------------------------------


def test_a_binding_can_be_scoped_to_slots_or_to_single_rules():
    """Slot-level alone was too coarse for two of the three cases that motivated the field, so an
    entry is either a bare slot id or `slot/dimension`."""
    s = json.load(open(os.path.join(ROOT, "schema", "style-node.schema.json")))
    f = s["properties"]["proportion_packs"]["items"]["properties"]["slots"]
    assert f["items"]["pattern"] == "^[a-z_]+(/[a-z_]+)?$"
    assert "BOTH GRANULARITIES ARE NEEDED" in f["description"]


def test_the_three_scoped_bindings_name_only_rules_their_packs_actually_write():
    """A scope naming something the pack does not write is a silent no-op -- the node gets nothing
    and the binding still reads as though it delivered a rule, which is a smaller version of the
    problem the field was added to solve. check_pack_bindings errors on it; this pins the data."""
    for nid, pid, scope in [
        ("french-normandy-revival", "jetty-overhang", ["material_change_rule"]),
        ("mission-revival", "facade-portada", ["ornament_vocabulary/event_count"]),
        ("egyptian-revival", "facade-peristyle",
         ["column/front_count", "column/intercolumniation_roman"]),
    ]:
        e = next(b for b in node(nid)["proportion_packs"] if b["pack"] == pid)
        assert e["slots"] == scope, nid
        written = {r["target_slot"] for r in pack(pid)["derived_rules"]}
        written |= {f"{r['target_slot']}/{r['dimension']}" for r in pack(pid)["derived_rules"]}
        for entry in scope:
            assert entry in written, (nid, entry)


def test_the_scope_excludes_the_rule_the_node_forbids():
    """`egyptian-revival` c04: shafts 'shall never carry classical fluting or entasis'. Binding the
    whole pack would have handed it `column/entasis_swell`. The scope excludes it, along with a
    peristyle count it has no peristyle for and a Vitruvian column-height function."""
    e = next(b for b in node("egyptian-revival")["proportion_packs"]
             if b["pack"] == "facade-peristyle")
    admitted = set(e["slots"])
    all_column = {f"column/{r['dimension']}" for r in pack("facade-peristyle")["derived_rules"]
                  if r["target_slot"] == "column"}
    assert "column/entasis_swell" in all_column
    assert "column/entasis_swell" not in admitted
    assert "column/flank_count" not in admitted
    assert "column/height_by_spacing" not in admitted
    assert len(all_column - admitted) == 6
    assert "never carry classical fluting or entasis" in json.dumps(node("egyptian-revival"))


def test_every_buildable_node_now_carries_a_binding_and_the_allowlist_is_empty():
    """132 of 132. The set is kept rather than deleted because the mechanism it names is still the
    right answer for a node that genuinely fits nothing."""
    src = open(os.path.join(ROOT, "build", "check_pack_bindings.py")).read()
    assert "DELIBERATELY_UNBOUND = set()" in src
    assert "EMPTIED 25 Aug 2026 by OQ 49" in src
    import glob
    unbound = [json.load(open(f))["id"] for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json")))
               if json.load(open(f)).get("rank") in ("style", "variant")
               and not json.load(open(f)).get("proportion_packs")]
    assert unbound == []


def test_the_resolver_filters_on_the_scope_and_it_is_the_only_place_it_can():
    """BEHAVIOURAL, deliberately. This test used to assert that three strings appeared in
    resolve_kit.py's source. An audit on 25 Aug 2026 neutered the filter (`scope = None`) while
    leaving every asserted string in place and ran the suite: 366 tests passed, and in that mutant
    `egyptian-revival` received all 17 facade-peristyle rules including the entasis its own c04
    forbids. A source-string assert protects the comment, not the behaviour. So: call eval_packs.
    """
    rk = _rk()
    pk_rules = _pe_mod().resolve("facade-peristyle")["derived_rules"]
    ctx = {"ceiling_height": 108.0, "storey_height": 120.0, "opening_width": 36.0,
           "opening_height": 80.0, "span": 540.0, "wall_thickness": 13.5}

    unscoped = {"facade-peristyle": {"role": "facade", "_source": "t", "precedence": 1}}
    wide, _ = rk.eval_packs(unscoped, ctx, None)
    n_wide = sum(len(v) for v in wide.values())
    assert n_wide > 2, "an unscoped binding must still deliver the whole pack"

    target = pk_rules[0]["target_slot"]
    scoped = {"facade-peristyle": {"role": "facade", "_source": "t", "precedence": 1,
                                   "slots": [target]}}
    narrow, _ = rk.eval_packs(scoped, ctx, None)
    assert set(narrow) == {target}, f"scope admitted {sorted(narrow)}, not just {target}"
    assert sum(len(v) for v in narrow.values()) < n_wide

    # A scope naming something the pack does not write admits NOTHING -- it must never fall back
    # to delivering everything, which is the direction that would be silent and wrong.
    bogus = {"facade-peristyle": {"role": "facade", "_source": "t", "precedence": 1,
                                  "slots": ["no_such_slot_exists"]}}
    empty, _ = rk.eval_packs(bogus, ctx, None)
    assert sum(len(v) for v in empty.values()) == 0


def test_the_scope_actually_keeps_the_entasis_off_egyptian_revival():
    """The finding that produced OQ 49, asserted end to end on the shipped corpus rather than on
    a comment: the node's binding is scoped to two rules, and the rule its own c04 forbids is not
    among what it receives."""
    rk = _rk()
    g = rk.load_graph()
    ctx = {"ceiling_height": 108.0, "storey_height": 120.0, "opening_width": 36.0,
           "opening_height": 80.0, "span": 540.0, "wall_thickness": 13.5}
    packs = rk.resolve_packs(g, rk.chain_for(g, "egyptian-revival"))
    by_slot, _ = rk.eval_packs(packs, ctx, None)
    delivered = [(sid, r["dimension"], r.get("quantity"))
                 for sid, rows in by_slot.items() for r in rows
                 if r["pack"] == "facade-peristyle"]
    assert delivered, "the scoped binding must still deliver its two rules"
    assert len(delivered) == 2, delivered
    assert not [d for d in delivered if "entasis" in str(d)], delivered


# --- OQ 51, found while closing OQ 49 ----------------------------------------------------------


def test_the_cascade_delivers_packs_nobody_bound_and_it_is_raised_not_papered_over():
    """`egyptian-revival` was held out of DELIBERATELY_UNBOUND on the reasoning that nothing fitted
    its trabeated order -- while the lineage cascade was handing it `facade-peristyle` unscoped from
    five ancestors, entasis rule included. The refusal was cosmetic, and the same mechanism reaches
    every node in the corpus."""
    g = json.load(open(os.path.join(ROOT, "dist", "taxonomy.json")))
    n = g["nodes"]["egyptian-revival"]
    chain = [b for b in n.get("_cascade", [])]
    binders = [a for a in chain
               if any(pb["pack"] == "facade-peristyle"
                      for pb in (g["nodes"][a].get("proportion_packs") or []))]
    assert len(binders) == 5, binders
    assert all((next(pb for pb in g["nodes"][a]["proportion_packs"]
                     if pb["pack"] == "facade-peristyle").get("slots") is None) for a in binders)
    oq = _register_text()
    # Re-pinned 25 Aug 2026: OQ 51 was ruled that day, so "still OPEN" is no longer the right guard.
    # What must not regress is that the entry is still there and still says the MECHANISM is
    # unchanged -- a ruling is not a fix, and the cascade delivers exactly what it delivered before.
    assert "51. **RULED" in oq
    assert "adjudicate first" in oq


# --- OQ 48: quantity, and the ratchet ----------------------------------------------------------


def _addresses():
    import subprocess, re
    out = subprocess.run([os.sys.executable, os.path.join(ROOT, "build", "check_addresses.py")],
                         capture_output=True, text=True, cwd=ROOT).stdout
    # Four numbers since 26 Aug 2026, not three: OQ 53 added a state between agreement and
    # collision -- two packs that agree on the quantity and differ on the UNITS they say it in.
    m = re.search(r"(\d+) co-binding pack pair\(s\); (\d+) address\(es\)[^;]*; (\d+) where they "
                  r"agree on the quantity and differ on its units; (\d+) could not", out)
    assert m, out
    return tuple(int(x) for x in m.groups())


def test_the_real_collision_count_is_pinned_and_cannot_grow_silently():
    """139 addresses where two co-binding packs measure DIFFERENT quantities, against the ~20 a 5%
    rate over 453 predicted -- a seven-fold under-estimate, and the seventh time in this work that
    a measurement was wrong once it was read. Fixing them is a migration and is not done here; the
    pinned count is what protects the corpus meanwhile, because a new pack adding a 140th fails."""
    pairs, real, unit_splits, unjudged = _addresses()
    # RE-PINNED after the migration: 139 -> 0. The 74 minority rules at the 27 genuinely
    # conflicted addresses took their `quantity` as their `dimension`, so both meanings survive
    # instead of one being set aside. What the pin protects now is that it STAYS zero.
    assert (pairs, real) == (442, 0)
    assert unjudged == 14
    # OQ 53's number, pinned the day it was measured rather than left to drift. These 68 are not
    # collisions -- the two rules agree about what they measure -- but they say it in different
    # units, and until 26 Aug 2026 precedence could deliver either, so a bare ratio could be
    # written into a kit as a dimension. resolve_kit now prefers the measurement and records the
    # demotion; this pin is what stops the underlying class from growing while the referents stay
    # in prose. It may go DOWN as ratio rules gain a machine-readable referent, never up.
    assert unit_splits == 68


def test_unjudged_is_reported_separately_and_never_as_agreement():
    """A rule with no `quantity` cannot be compared. The checker counts those apart from the
    collisions, which is the discipline the whole corpus runs on."""
    src = open(os.path.join(ROOT, "build", "check_addresses.py")).read()
    assert "UNJUDGED IS NOT PASSED" in src
    assert "could not be judged" in src
    _, _, _, unjudged = _addresses()
    assert unjudged > 0                       # and it is a real number, not an empty branch


def test_the_checker_reports_by_default_and_only_fails_under_strict():
    """A known, counted, documented backlog must not block all work. What protects the corpus is
    the pinned count above, not a red build."""
    src = open(os.path.join(ROOT, "build", "check_addresses.py")).read()
    assert '"--strict"' in src
    assert "OFF by default, deliberately" in src
    import subprocess
    p = subprocess.run([os.sys.executable, os.path.join(ROOT, "build", "check_addresses.py")],
                       capture_output=True, text=True, cwd=ROOT)
    assert p.returncode == 0
    q = subprocess.run([os.sys.executable, os.path.join(ROOT, "build", "check_addresses.py"),
                        "--strict"], capture_output=True, text=True, cwd=ROOT)
    assert q.returncode == 0        # nothing left for --strict to fail on, which is the point


def test_the_resolver_names_what_it_sets_aside_instead_of_discarding_it():
    """BEHAVIOURAL. Precedence decides which of two accounts of ONE quantity to believe; it cannot
    decide between two quantities, and the loser used to vanish with nothing said. Feed choose_pack
    two packs meaning different things at one address and require it to say so."""
    rk = _rk()
    ctx = {"ceiling_height": 108.0}
    rows = [
        {"pack": "pack-a", "role": "facade", "from": "x", "style_precedence": 1,
         "dimension": "height", "quantity": "plinth_block_height", "expression": "1",
         "value": 1.0, "units": "in", "judgment": False, "calibrated_for": None},
        {"pack": "pack-b", "role": "facade", "from": "y", "style_precedence": 2,
         "dimension": "height", "quantity": "head_casing_height", "expression": "2",
         "value": 2.0, "units": "in", "judgment": False, "calibrated_for": None},
    ]
    ch = rk.choose_pack({}, rows, ctx)
    others = ch.get("other_quantities") or []
    assert len(others) == 1, others
    assert others[0]["kind"] == "set-aside"
    assert others[0]["cross_pack"] is True
    assert "head_casing_height" in others[0]["quantity"]

    # UNJUDGED IS NOT DECIDED. A rule with no `quantity` cannot be compared, so it must never be
    # reported as having lost to something -- 268 of 751 rules have none, and the schema's own
    # text calls this could-not-evaluate.
    rows[1] = dict(rows[1], quantity=None)
    ch2 = rk.choose_pack({}, rows, ctx)
    o2 = (ch2.get("other_quantities") or [])[0]
    assert o2["kind"] == "could-not-judge", o2
    assert "COULD NOT BE JUDGED" in o2["quantity"]
    assert "set aside in favour of" not in o2["quantity"]

    # Two quantities at a dimension that is NOT the one delivered were BOTH dropped; claiming one
    # prevailed over the other is a decision that did not happen.
    rows2 = rows[:1] + [dict(rows[0], pack="pack-c", dimension="width",
                             quantity="casing_face_width", style_precedence=3),
                        dict(rows[0], pack="pack-d", dimension="width",
                             quantity="muntin_width", style_precedence=4)]
    ch3 = rk.choose_pack({}, rows2, ctx)
    kinds = {o["kind"] for o in (ch3.get("other_quantities") or [])}
    assert "both-dropped" in kinds, ch3.get("other_quantities")


def test_quantity_survives_the_proportion_engine():
    """BEHAVIOURAL, and generalised to every schema field. `quantity` did not survive `evaluate`
    at first and the grouping silently did nothing. The same bug was still live for
    `calibrated_for` -- which resolve_kit READS, so `stale_calibration` was permanently False --
    and for `diagnostic`. A row rebuilt key-by-key drops whatever nobody re-listed, so assert the
    whole schema rather than one field."""
    pe = _pe_mod()
    declared = set(json.load(open(os.path.join(ROOT, "schema", "proportion-pack.schema.json")))
                   ["properties"]["derived_rules"]["items"]["properties"])
    ctx = {"ceiling_height": 108.0, "opening_width": 36.0, "opening_height": 80.0,
           "span": 540.0, "wall_thickness": 13.5, "storey_height": 120.0}
    missing = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
        pid = json.load(open(f))["id"]
        rows = pe.evaluate(pe.resolve(pid), None, ctx)["rules"]
        if not rows:
            continue
        gap = declared - set(rows[0])
        if gap:
            missing[pid] = sorted(gap)
    assert not missing, f"schema fields dropped by evaluate(): {missing}"

    # and the values actually arrive, not just the keys
    live = [r for r in pe.evaluate(pe.resolve("trim-classical"), None, ctx)["rules"]
            if r.get("calibrated_for")]
    assert live, "trim-classical states a calibration band; it must reach the row"


def test_quantity_survives_the_proportion_engine():
    """It is set on the rule and read at resolution, so it has to come through `evaluate`. It did
    not, at first, and the grouping silently did nothing -- which is the same class of failure the
    field exists to catch."""
    src = open(os.path.join(ROOT, "build", "proportion_engine.py")).read()
    assert '"quantity": r.get("quantity"),' in src


def test_the_worst_addresses_are_annotated_and_their_quantities_differ():
    """`window_head_masonry/height` held five quantities -- head height above floor, lintel depth,
    flat-arch camber, segmental rise, hood mould depth -- and 44 nodes bind two or more of the
    packs involved. `height_proportion/ratio` held seven."""
    def qs(slot, dim):
        out = set()
        import glob
        for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
            for r in json.load(open(f)).get("derived_rules", []):
                if r["target_slot"] == slot and r["dimension"] == dim and r.get("quantity"):
                    out.add(r["quantity"])
        return out
    # RE-PINNED after the migration. The quantities did not go away -- they moved out of one
    # address into their own, which is the fix. Check the SLOT rather than the old address.
    def slot_qs(slot):
        out = set()
        import glob
        for f in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
            for r in json.load(open(f)).get("derived_rules", []):
                if r["target_slot"] == slot and r.get("quantity"):
                    out.add(r["quantity"])
        return out
    assert len(slot_qs("window_head_masonry")) >= 5
    assert len(slot_qs("height_proportion")) >= 6
    assert "head_height_above_floor" in slot_qs("window_head_masonry")
    assert "lintel_or_arch_depth" in slot_qs("window_head_masonry")
    assert qs("window_head_masonry", "height") == {"lintel_or_arch_depth"}   # one meaning left


# --- OQ 50: the rationing pattern, measured ----------------------------------------------------


def test_no_node_in_the_corpus_requires_ornament_to_be_evenly_distributed():
    """The strong form of OQ 50's claim, and the one worth a test: eight nodes say in their own
    words that distributing ornament destroys the style, and none says the opposite."""
    import glob, re
    NEG = re.compile(r"(distribut\w*|evenly|uniformly)[^.]{0,90}ornament"
                     r"|ornament[^.]{0,90}(evenly|uniformly|distribut)", re.I)
    condemn = set()
    for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        d = json.load(open(f))
        if d.get("rank") not in ("style", "variant"):
            continue
        blob = [c.get("statement", "") for c in (d.get("constraints") or [])]
        for k in ("defining_characteristics", "diagnostic_tells"):
            blob += [t for t in (d.get(k) or []) if isinstance(t, str)]
        for t in blob:
            for m in NEG.finditer(t or ""):
                seg = t[max(0, m.start() - 60):m.end() + 90]
                if re.search(r"forbid|convert|misread|destroy|never|imitation|voids", seg, re.I):
                    condemn.add(d["id"])
    assert len(condemn) >= 6, sorted(condemn)
    for nid in ("california-mission-colonial", "churrigueresque", "mexican-colonial",
                "scottish-baronial", "spanish-colonial-american", "spanish-plateresque"):
        assert nid in condemn, nid


def test_the_pattern_has_exactly_one_control_case_and_it_is_named_by_its_opposite():
    """`spanish-plateresque` names Italian work as the tradition that distributes, and
    `italian-renaissance`'s own bay rhythm agrees. A pattern with a boundary is a finding; one
    without is an artefact of how the records were written."""
    assert "distributes ornament across it" in json.dumps(node("spanish-plateresque"))
    assert "even, additive and non-hierarchical" in \
        json.dumps(node("italian-renaissance")).lower()


def test_oq_50_states_what_it_does_not_claim():
    """26 of 132 is not most of the corpus, and the other 106 are silent rather than disagreeing.
    A conditional claim stated as a universal one is how a finding becomes folklore."""
    oq = _register_text()
    # RE-PINNED: OQ 50 was ruled on 25 Aug to stop at the principle. It stays open on one point
    # only -- if the elevation layer ever models ornament zones, the fault should be written.
    assert "50. **RULED 25 Aug 2026" in oq
    assert "**OPEN — ornament works by being bounded" in oq
    assert "**What is NOT claimed.**" in oq
    assert "has not voted" in oq
    assert "reading disposed of 14 of them" in oq


def test_claude_md_open_question_list_is_derived_from_the_file_not_asserted_against_a_literal():
    """CLAUDE.md described five closed questions as open for a day: OQ 54, 40, 41, 42 and 43 were
    ruled or closed on 24 Aug and the summary went on listing three of them as needing a ruling.
    `check_counts.py` polices NUMBERS in prose and has no view on claims about rulings, so this is
    the guard for that class -- both the list and the count in front of it."""
    import re, importlib.util
    md = open(os.path.join(ROOT, "CLAUDE.md")).read()

    # DERIVED, not hardcoded. The first version of this test computed the true set from the file
    # and then asserted against a literal list anyway, so it went red on the next ruling rather
    # than on the next piece of drift -- which is the opposite of what it is for.
    #
    # THE REGISTER IS A DIRECTORY SINCE 28 Aug 2026 (WP-8.1), one file per question, because a
    # single shared file is where two parallel sessions' answers to "what is the next id" both
    # survive a merge -- four times in four days. So this reads `build/check_ids.py`'s own reader
    # rather than re-parsing anything, and it does NOT restate the status vocabulary. It used to:
    # SETTLED_WORDS and OPEN_WORDS were spelled here AND in the register, which is the same
    # duplication that let check_inheritance.py's RATCHET drift stale-high while its own comment
    # claimed the test imported it. One list, one place, and an unrecognised word is a FAILURE in
    # check_ids.py rather than a default -- a guard whose unknown case is "assume fine" is not a
    # guard.
    spec = importlib.util.spec_from_file_location(
        "check_ids_for_test", os.path.join(ROOT, "build", "check_ids.py"))
    ci = importlib.util.module_from_spec(spec); spec.loader.exec_module(ci)
    qs, errors = ci.read_questions()
    assert not errors, f"the register does not check out, so this list cannot be trusted: {errors}"
    assert qs, "read_questions() found nothing -- the register moved and this guard is reading air"
    live = {str(k) for k, v in qs.items() if v["state"] == "open"}

    claimed = set(re.findall(r"of which \d+ are open\*\*\s*\n?\s*\(([\d, ]+)\)", md))
    assert claimed, md[md.index("Open questions are live"):][:300]
    listed = {x.strip() for x in list(claimed)[0].split(",") if x.strip()}
    assert listed == live, f"CLAUDE.md says {sorted(listed)}, the file says {sorted(live)}"
    n_claimed = int(re.search(r"of which (\d+) are open", md).group(1))
    assert n_claimed == len(live), f"CLAUDE.md counts {n_claimed}, the file has {len(live)}"
    # And the five CLAUDE.md used to mis-describe as open are still absent. Re-pinned at the
    # 25 Aug merge: this read ("32", "40", "41", "42", "43") when those ids were this branch's
    # rulings. Both branches had issued 32-41, so this branch's block was reissued as 54-63 and
    # main's ten -- which ARE genuinely open -- now hold 32-41. Pinning the old numbers here would
    # have asserted that main's open questions are closed, which is the failure this test exists
    # to catch, committed by the test itself.
    for n in ("54", "62", "63", "42", "43"):
        assert n not in listed, f"OQ {n} is ruled/closed and must not be listed as open"
    assert "was stale for a day" in md


# --- OQ 51: the inheritance ratchet ------------------------------------------------------------


def _inheritance():
    import subprocess, re
    out = subprocess.run([os.sys.executable, os.path.join(ROOT, "build", "check_inheritance.py")],
                         capture_output=True, text=True, cwd=ROOT).stdout
    # Anchored to line starts. Unanchored, a prose line elsewhere in the output containing
    # "unendorsed <number>" would be matched instead of the table row, silently returning the
    # wrong number to a test whose whole job is to pin numbers.
    def n(label):
        m = re.search(r"^\s*%s\s+(\d+)" % label, out, re.M)
        assert m, f"{label} row missing from check_inheritance output"
        return int(m.group(1))
    return n("role_gaps"), n("inherited_packs"), n("unendorsed"), n("endorsed")


def test_the_inheritance_backlog_is_pinned_and_cannot_grow_silently():
    """OQ 51's three numbers. `role_gaps` is (node, role) pairs where an ancestor fills a role the
    node never bound; `inherited_packs` is packs arriving purely by descent; `unendorsed` is the
    subset of gaps no pack's own applies_to vouches for. None fails the build -- this is a measured
    backlog, not a regression -- and the pin is what protects it. All three should go DOWN as the
    corpus is worked; a rise means the cascade papered over something new."""
    gaps, packs, unendorsed, _endorsed = _inheritance()
    # 233 -> 222 on 26 Aug 2026: the first adjudication pass against the ruling. Eleven
    # storey-graduation gaps were judged against each node's own record and endorsed; the pack's
    # applies_to now names them. gaps and packs do not move on an endorsement -- the cascade
    # delivers what it always delivered, and what changed is that somebody read it.
    # 294 -> 293 gaps and 3367 -> 3366 packs on 27 Aug 2026 (WP-5.14), and this is the meter
    # moving the RIGHT way for once. `colonial-revival` bound its own `dormer` slot, so the role
    # it had been letting `english-cottage-vernacular` fill by descent is one it now fills itself:
    # one gap fewer, one inherited pack fewer. `unendorsed` does not move, because that gap was an
    # ENDORSED one -- see the test below. Binding a slot natively is strictly better than an
    # endorsement even so: an endorsement records that somebody read the cascade and agreed with
    # it, and a binding means the node says it in its own voice.
    assert (gaps, packs, unendorsed) == (293, 3366, 222)


def test_unendorsed_is_the_number_the_ruling_moves_and_endorsed_is_not_a_fault():
    """OQ 51 was ruled adjudicate-first: work the unendorsed gaps, adding a node to the inherited
    pack's `applies_to` where the pack is right and binding or scoping where it is wrong, then flip
    inheritance to opt-in once unendorsed approaches zero. That only works if the two halves are
    told apart -- a gap the pack author vouched for is the cascade delivering what was INTENDED,
    and counting it as a fault would make the meter unreadable and the work list wrong."""
    gaps, _, unendorsed, endorsed_printed = _inheritance()
    # Two INDEPENDENT computations, not one restated. Deriving `endorsed` as `gaps - unendorsed`
    # here reproduces the checker's own arithmetic, so the printed line was never read and could
    # not be contradicted -- break the endorsement predicate's reporting and this could not notice.
    assert endorsed_printed == gaps - unendorsed, "the checker's own two numbers disagree"
    # 72 -> 71 on 27 Aug 2026 (WP-5.14): `colonial-revival`'s dormer gap was endorsed, and the
    # style binds the slot itself now, so it is not a gap at all any more.
    assert endorsed_printed == 71, "71 of the 293 gaps are endorsed by the pack's own applies_to"

    # And the predicate means what it says: a named gap whose pack `applies_to` lists the node is
    # endorsed, and one whose pack does not is not. `assert unendorsed < gaps` was vacuous --
    # unendorsed is a subset filter of gaps, so it could only fail if literally nothing were
    # endorsed. Check the actual relation instead, on real records.
    import importlib.util as _il
    spec = _il.spec_from_file_location("ci", os.path.join(ROOT, "build", "check_inheritance.py"))
    ci = _il.module_from_spec(spec); spec.loader.exec_module(ci)
    applies = ci.applies_to_index()
    _, all_gaps, _ = ci.measure(ci.load())
    end = [t for t in all_gaps if t[0] in applies.get(t[3], ())]
    une = [t for t in all_gaps if t[0] not in applies.get(t[3], ())]
    assert len(end) == endorsed_printed and len(une) == unendorsed
    assert end and une, "both sides must be non-empty or the split measures nothing"
    nid, _role, _anc, pid = end[0]
    assert nid in applies[pid], "an endorsed gap's pack must name the node in applies_to"
    nid2, _r2, _a2, pid2 = une[0]
    assert nid2 not in applies.get(pid2, ()), "an unendorsed gap's pack must NOT name the node"


def test_the_diagnostic_names_the_ancestor_because_that_is_the_actionable_part():
    """Knowing a role is inherited is half of it; knowing WHICH ancestor decided it is what lets
    somebody either bind the node or scope the edge."""
    import subprocess
    out = subprocess.run([os.sys.executable, os.path.join(ROOT, "build", "check_inheritance.py"),
                          "--roles"], capture_output=True, text=True, cwd=ROOT).stdout
    assert "egyptian-revival" in out
    assert "<-greek-revival-american" in out


def test_a_ranch_is_dimensioned_by_a_gothic_arch_pack_and_the_slot_report_says_so():
    """The finding at its sharpest. 69 of `ranch-style`'s 78 dimensioned slots are governed by
    packs it never bound, and the report names the pack AND the ancestor it was bound on."""
    import subprocess
    out = subprocess.run([os.sys.executable, os.path.join(ROOT, "build", "check_inheritance.py"),
                          "--slots", "ranch-style"], capture_output=True, text=True, cwd=ROOT).stdout
    assert "78 slot(s) dimensioned, 69 by a pack it never bound" in out
    assert "opening-pointed" in out and "gothic-revival-british" in out
    assert "gibbs-ionic" in out


def test_the_checker_says_what_the_binding_count_never_measured():
    src = open(os.path.join(ROOT, "build", "check_inheritance.py")).read()
    assert '"132 of 132 bound" counts a node\'s own array' in src
    assert "it has never measured what a node RECEIVES" in src


# --- OQ 18: every editorial parameter now says it is one ---------------------------------------


def test_no_editorial_parameter_is_silent_any_more():
    """162 carried neither a source nor a note. The count of silent editorial values is now 0, and
    not one was given a source it does not have."""
    import glob
    silent = sourced = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        for sid, v in (json.load(open(f)).get("slots") or {}).items():
            for pn, p in ((v.get("parameters") or {}).items()):
                if not isinstance(p, dict) or p.get("kind") != "editorial":
                    continue
                if not p.get("source") and not p.get("note"):
                    silent += 1
                if "OQ 18, annotated" in (p.get("note") or "") and p.get("source"):
                    sourced += 1     # an annotated one must NOT have gained a source
    assert silent == 0
    # and the note must not have quietly become a source: the source half is still blocked
    assert sourced == 0
    oq = _register_text()
    assert "The source half is ENVIRONMENT-BLOCKED" in oq
    assert "may be given a source from a secondary work" in oq


def test_the_notes_say_they_are_not_citations():
    """The failure mode this whole entry is about is a judgment reading as a measurement. A note
    that explained the figure without saying it is unsourced would be a smaller version of it."""
    import glob
    checked = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        for sid, v in (json.load(open(f)).get("slots") or {}).items():
            for pn, p in ((v.get("parameters") or {}).items()):
                if not isinstance(p, dict) or p.get("kind") != "editorial":
                    continue
                n = p.get("note") or ""
                if "OQ 18, annotated" in n:
                    assert "NO SOURCE IS RECORDED" in n, (f, sid, pn)
                    assert "which is the reasoning, not a citation" in n, (f, sid, pn)
                    checked += 1
    assert checked == 162


def test_the_57_that_looked_like_placeholders_were_correct_records():
    """The ninth over-count of this work package, and the first that would have damaged good data:
    a script looked only at `value`, found null, and reported 57 mis-tagged placeholders. 55 carry
    a `range` and 2 a `set`. Reading them is the only reason they survived."""
    import glob
    banded = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        for sid, v in (json.load(open(f)).get("slots") or {}).items():
            for pn, p in ((v.get("parameters") or {}).items()):
                if not isinstance(p, dict) or p.get("kind") != "editorial":
                    continue
                if "OQ 18, annotated" not in (p.get("note") or ""):
                    continue
                if p.get("value") is None and (p.get("range") or p.get("set")):
                    banded += 1
    assert banded == 57
    oq = _register_text()
    assert "ninth" in oq and "would have DAMAGED correct records" in oq


# --- the build artefact, and the seventeen tests that trusted it -------------------------------


def test_dist_taxonomy_is_fresh_because_seventeen_tests_read_it_as_if_it_were_source():
    """`dist/taxonomy.json` is a BUILD ARTEFACT, git-tracked, and 17 tests read it -- including
    every OQ 51 pin. Nothing in the pytest path regenerated it. An audit on 25 Aug 2026 emptied
    `proportion_packs` on 20 style records WITHOUT rebuilding: the ratchet still read
    294 / 3367 / 233 and all three pins stayed green. After `build.py` the true figures were
    369 / 3390 / 265. So the meter for the largest open question in the corpus could be pointed at
    a graph that no longer existed, and nothing said so.

    `check_all.py` now runs `build.py` FIRST rather than last, which fixes `make check`. This test
    is the other half, for a bare `pytest tests/`: rebuild, and require the artefact not to move.
    It is deliberately self-healing -- if it fails, the tree is left correct and the next run is
    green -- because the failure it reports is "you forgot to rebuild", not "the data is wrong".
    """
    import subprocess
    import sys as _sys
    p = os.path.join(ROOT, "dist", "taxonomy.json")
    before = open(p, "rb").read()
    r = subprocess.run([_sys.executable, os.path.join(ROOT, "build", "build.py")],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr[-2000:]
    after = open(p, "rb").read()
    assert before == after, (
        "dist/taxonomy.json was STALE -- a source file changed and the artefact was not rebuilt. "
        "It has now been regenerated, so this test will pass on the next run; commit the artefact "
        "with the change that caused it. 17 tests read this file, including every OQ 51 pin.")
