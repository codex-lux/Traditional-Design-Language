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


def test_english_gothic_is_the_one_node_whose_facade_gap_is_real_and_it_is_left_open():
    """It is the medieval building, not the revival of it, so facade-picturesque's nineteenth-
    century argument is an anachronism against it. Binding the nearest available thing to close a
    count is what this corpus does not do; the gap is stated and handed to the candidate list."""
    assert binding("english-gothic", "facade-picturesque") is None
    assert not any(b["role"] == "facade" for b in node("english-gothic")["proportion_packs"])
    assert "english-gothic" in pack("opening-pointed")["notes"]


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
    tan_lo = float(rules[("roof_pitch", "ratio")]["expression"])
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
                 if x["target_slot"] == "height_proportion" and x["dimension"] == "ratio")
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
    assert dims == {"ratio", "upper_ratio"}
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
    for f in _glob.glob(os.path.join(ROOT, "styles", "*.json")):
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
    for f in _glob.glob(os.path.join(ROOT, "styles", "*.json")):
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
    assert len(facade_bound) >= 8
    src = open(os.path.join(ROOT, "README.md")).read()
    m = re.search(r"(\d+) no facade-role pack", src)
    assert m and int(m.group(1)) < 67


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
             if x["target_slot"] == "corner_board" and x["dimension"] == "projection")
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


def test_the_missing_slot_is_raised_as_an_open_question_not_worked_around():
    """Four rules route the exposed timber through `corner_board`, a board at a corner, because the
    ontology has no slot for an exposed structural member on a wall face. Same class as OQ 46."""
    p = pack("timber-panel")
    routed = [r for r in p["derived_rules"] if r["target_slot"] == "corner_board"]
    assert len(routed) == 4
    assert "no slot for AN EXPOSED STRUCTURAL MEMBER ON THE WALL FACE" in \
        next(r for r in routed if r["dimension"] == "spacing")["note"]
    oq = open(os.path.join(ROOT, "docs", "open-questions.md")).read()
    assert "47. **OPEN — the ontology has no slot for an exposed structural member" in oq
    assert "expressed_frame" in oq


def test_the_pack_says_the_exposed_frame_is_substantially_a_victorian_taste():
    """Four records in the corpus describe the frame being covered -- tile-hung, weatherboarded,
    stuccoed, limewashed. The climate conflict says plainly that covering it is what the buildings
    did rather than a modern compromise."""
    c = next(x for x in pack("timber-panel")["conflicts"] if x["with"] == "climate")
    assert "THE TRADITIONS THEMSELVES CONCLUDED THAT THIS WALL SHOULD BE COVERED" in c["statement"]
    assert "tile-hung upper storey" in json.dumps(node("queen-anne-british"))
    assert "stuccoed or weatherboarded" in json.dumps(node("creole-cottage-vernacular"))
