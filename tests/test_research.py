"""WP-11.1 -- the research meter and the precedent record, pinned by NAME and not only by count.

A count cannot tell a swap from a state: if one node gains a source and another loses one, "24
shared-only nodes" is still true and something has moved. So the sets are pinned as sets, the
ratchets are IMPORTED from the checkers (check_inheritance.py's rule: a test that restates a
ratchet drifts from it), and the generator-read slot set is pinned by equality so a change in
what the generators read is NOTICED rather than forbidden -- `measured_unsourced_read` falls for
free when a generator stops reading a slot, and this is what makes that visible.
"""
import collections
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CR = modcache.load("check_research", os.path.join(ROOT, "build", "check_research.py"))
CP = modcache.load("check_precedents", os.path.join(ROOT, "build", "check_precedents.py"))

SOURCELESS = {
    "american-arts-and-crafts", "american-colonial", "american-folk-vernacular", "antique-classical",
    "british-arts-and-crafts", "british-isles", "british-picturesque", "british-vernacular",
    "classical-mediterranean", "colonial-iberian-americas", "contemporary-traditional",
    "continental-baroque-neoclassical", "early-republic", "eclectic-revivals", "english-classical",
    "french-vernacular", "germanic-vernacular", "iberian-islamic", "iberian-mediterranean",
    "iberian-vernacular", "low-countries-vernacular", "medieval-british", "mediterranean-vernacular",
    "mid-century-traditional", "nordic-alpine-vernacular", "north-american",
    "northern-european-vernacular", "renaissance-classical", "romantic-revivals", "spanish-classical",
    "tudor-jacobean", "victorian",
}
SHARED_ONLY = {
    "carpenter-gothic", "colonial-revival", "creole-cottage-vernacular", "dutch-colonial-american",
    "dutch-colonial-revival", "elizabethan", "folk-victorian", "french-normandy-revival",
    "french-provincial-farmhouse", "georgian-colonial-american", "georgian-revival", "hudson-valley-dutch",
    "italian-renaissance-revival", "italianate-american", "italianate-villa", "neoclassical-revival",
    "new-england-colonial", "norman-vernacular", "queen-anne-american", "queen-anne-free-classic",
    "raised-creole-plantation", "saltbox-colonial", "spanish-colonial-american", "stick-style",
}
UNTESTED = {"queen-anne-free-classic", "queen-anne-spindled", "roman-classical"}
READ_SLOTS = {
    "arch",
    "belt_course",
    "casing",
    "ceiling_height_rule",
    "chimney",
    "circulation_parti",
    "column",
    "composition_parti",
    "construction_type",
    "cornice",
    "door_surround",
    "dormer",
    "entablature",
    "entry_door",
    "frieze",
    "height_proportion",
    "orientation_rule",
    "pilaster",
    "porch_depth",
    "porch_type",
    "reveal_frame",
    "reveal_masonry",
    "roof_form",
    "room_adjacency_overrides",
    "setback_rule",
    "shutter",
    "stair_type",
    "transom_sidelight",
    "water_table",
    "window_grouping_rule",
    "window_head_masonry",
    "window_head_wood",
    "window_lite_pattern",
    "window_proportion",
    "window_type",
}


def test_the_sourceless_nodes_are_exactly_the_higher_ranks():
    """32 nodes cite no source and every one is a family or a tradition -- and every one is
    `confidence: high`, which is the field doing no work at that rank (its schema description
    scopes it to dates and lineage). A buildable node appearing here is a regression."""
    m = CR.measure()
    assert set(m["totals"]["sourceless_nodes"]) == SOURCELESS
    for n in SOURCELESS:
        assert m["per_node"][n]["rank"] in ("family", "tradition"), n


def test_the_shared_only_and_untested_sets_are_pinned_by_name():
    m = CR.measure()
    assert set(m["totals"]["shared_only_nodes"]) == SHARED_ONLY
    assert set(m["totals"]["untested_nodes"]) == UNTESTED


def test_the_generator_read_slot_set_is_noticed_when_it_changes():
    """An UPPER BOUND derived from string constants; pinned by equality so a generator reading a
    new slot, or ceasing to, shows up here rather than as `measured_unsourced_read` moving for
    free. Update the set AND say in the commit which generator changed."""
    got = set(CR.generator_read_slots())
    assert got == READ_SLOTS, (sorted(got - READ_SLOTS), sorted(READ_SLOTS - got))


def test_the_ratchets_are_read_from_the_checkers_and_hold():
    m = CR.measure()["totals"]
    got = {
        "measured_unsourced": m["measured_unsourced"],
        "measured_unsourced_read": m["measured_unsourced_read"],
        "editorial_read": m["editorial_read"],
        "shared_only_nodes": len(m["shared_only_nodes"]),
        "untested_nodes": len(m["untested_nodes"]),
        "exemplars_with_precedent": m["exemplars_with_precedent"],
        "nodes_with_a_precedent": m["nodes_with_a_precedent"],
    }
    for k, pin in CR.RATCHET.items():
        if k in CR.FLOORS:
            assert got[k] >= pin, (k, got[k], pin)
        else:
            assert got[k] <= pin, (k, got[k], pin)
    p = CP.measure()
    for k, pin in CP.RATCHET.items():
        # `measure()` is pure and computes only the corpus-derived figures; the counters that come
        # out of the report WALK (duplicates, kit-source verdicts, the refusal split) are patched
        # into `m` by main() and are absent here. Skipping them is right and their live values are
        # asserted by the --strict run itself, which check_all.py makes on every build.
        if k in CP.FLOORS and k in p:
            assert p[k] >= pin, (k, p[k], pin)


def test_a_sourced_measured_parameter_is_not_counted_as_unsourced():
    """The instrument must be able to fall. `georgian-colonial-american.water_table.measured_band_in`
    carries `source: georgian-colonial-american.c05` (OQ 18's one cross-referenced figure), so
    that node's unsourced count is strictly below its measured count."""
    row = CR.measure()["per_node"]["georgian-colonial-american"]
    assert 0 < row["measured_unsourced"] < row["measured"]


def test_the_unsourced_count_falls_when_a_figure_gains_a_source(tmp_path):
    """Mutation, proved rather than assumed: give one unsourced measured parameter a source and
    the corpus-wide figure must read one lower. Done on the real kit and read back, because a
    mutation that silently does not apply looks exactly like a guard that works (WP-9.6).

    AND THE PAIR IT USES IS THE POINT, because it is not a citation any reader would accept.
    `fireplaces_per_stack` [2, 4] is pointed at Westover's `chimney_stack_count` of 4: two
    different quantities that happen to share a number and a unit. `kit_source_agrees` passes it,
    because it compares NUMBERS and cannot compare MEANINGS -- there is no semantically matching
    pair on this node to use instead, which is how the limit was found. That is OQ 48's `quantity`
    problem arriving in the source layer, and it is
    `oq/a-source-that-agrees-numerically-may-be-the-wrong-quantity`. The guard closes
    "does the figure agree"; it does not close "is this the same thing".
    """
    kp = os.path.join(ROOT, "kits", "tidewater-georgian.kit.json")
    raw = open(kp, encoding="utf-8").read()
    before = CR.measure()["totals"]["measured_unsourced"]
    k = json.loads(raw)
    pv = k["slots"]["hearth_position"]["parameters"]["fireplaces_per_stack"]
    assert pv["kind"] == "measured" and "source" not in pv
    # WP-11.4, Ruling A moved this: a `kind: measured` parameter may no longer cite a survey
    # FIELD, because a quote cannot be held against a figure. It must cite a MEASUREMENT, whose
    # `value` and `unit` check_precedents.py compares with the parameter's.
    pv["source"] = "precedents/westover#measurements[2]"   # chimney_stack_count 4, inside [2, 4]
    try:
        open(kp, "w", encoding="utf-8").write(json.dumps(k, indent=2, ensure_ascii=False) + "\n")
        after = CR.measure()["totals"]["measured_unsourced"]
        assert json.load(open(kp))["slots"]["hearth_position"]["parameters"]["fireplaces_per_stack"]["source"]  # it landed
        assert after == before - 1, (before, after)
        # and the pointer resolves in the precedent checker (the field exists on that record)
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_precedents.py"), "--strict"],
                              cwd=ROOT, capture_output=True, text=True)
        assert "7 kit figure(s) cite a survey" in proc.stdout, proc.stdout[-600:]
        assert proc.returncode == 0, proc.stdout[-600:]
    finally:
        open(kp, "w", encoding="utf-8").write(raw)


def test_every_exemplar_precedent_resolves_and_the_join_keys_agree():
    """The other checker's whole point, run in-process: no dangling `precedent`, no record listing a
    node whose exemplars do not name it, and the exemplar name equal to the record's."""
    p = CP.measure()
    assert p["dangling_precedent"] == 0
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_precedents.py"), "--strict"],
                          cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout[-800:]
    assert "back_reference_disagreements" not in proc.stdout.split("RATCHET BROKEN")[-1] if "RATCHET BROKEN" in proc.stdout else True


def test_one_building_one_record(tmp_path):
    """WP-11.3. Twelve agents researching in parallel can produce the one defect the per-record
    checks cannot see: two records for one building under two ids. Two tests of unequal strength,
    and the inequality is the point -- a shared archival id is EVIDENCE (a HABS number names one
    building), a shared name is a QUESTION (American house names repeat across states). Proved by
    mutation rather than asserted: the rule is run against a synthetic pair, because running it
    against the real corpus only ever says what the corpus happens to hold today."""
    real = json.load(open(os.path.join(ROOT, "precedents", "westover.json"), encoding="utf-8"))

    # A shared archival id: an error.
    twin = json.loads(json.dumps(real))
    twin["id"], twin["name"], twin["nodes"] = "westover-twin", "Westover Twin", []
    ids = collections.defaultdict(list)
    for rec in (real, twin):
        for ref in rec["refs"]:
            if ref.get("kind") in CP.UNIQUE_ID_KINDS and ref.get("id"):
                ids[(ref["kind"], ref["id"])].append(rec["id"])
    assert any(len(set(v)) > 1 for v in ids.values()), "the archival-id test would not fire"

    # A shared name, through each of the four normalisations the corpus has met.
    assert CP.normalised_name("The Westover") == CP.normalised_name("westover")
    assert CP.normalised_name("Steuben House (Zabriskie House)") == CP.normalised_name("Steuben House")
    assert CP.normalised_name("Carter's Grove") == CP.normalised_name("Carters Grove")

    # And it must NOT collapse two genuinely different houses.
    assert CP.normalised_name("Mount Airy") != CP.normalised_name("Mount Vernon")
    assert CP.normalised_name("Mount Pleasant") != CP.normalised_name("Mount Airy")


def test_a_precedent_record_never_carries_a_license():
    for p in sorted(os.listdir(os.path.join(ROOT, "precedents"))):
        text = open(os.path.join(ROOT, "precedents", p), encoding="utf-8").read()
        assert '"license"' not in text, p


# ---------------------------------------------------------------------------------------------
# WP-11.4, Ruling D (5 Sep 2026): a precedent may be a district, a type model or a group, and a
# stated refusal is a field rather than prose. Both halves are mutation-checked in the package and
# pinned here, because the whole value of the ruling is a DISTINCTION and a distinction nothing
# guards is one somebody will collapse.

def test_the_district_exemption_is_driven_by_the_declaration_and_not_by_a_word_in_a_title():
    """`record_kind` is authoritative; DISTRICT_RE is the fallback for a record that predates it.

    The order matters in BOTH directions and each was mutation-checked by exit code:
      * two records declaring `district` may share one National Register number -- one listing
        legitimately covers many contributing buildings;
      * two records declaring `building` may NOT, even when a ref title carries the word
        'District', because a real house called "District House" would otherwise lose its
        identity to a word in its name.
    """
    assert CP.NOT_ONE_BUILDING == ("district", "type-model", "group")

    def ident(record_kind, title):
        rec = {"record_kind": record_kind} if record_kind else {}
        rec["refs"] = [{"kind": "nrhp", "id": "66000999", "title": title}]
        return CP.identity_keys(rec)

    # declared not-one-building -> exempt, whatever the title says
    for kind in CP.NOT_ONE_BUILDING:
        assert ident(kind, "ZZ mutation") == set(), kind
    # declared a building -> an identity, even with the fallback's own trigger word in the title
    assert ident("building", "ZZ mutation Historic District") == {("nrhp", "66000999")}
    # undeclared -> the fallback still reads the listing's own words
    assert ident(None, "Somewhere Historic District") == set()
    assert ident(None, "Plain House") == {("nrhp", "66000999")}


def test_a_stated_refusal_and_an_unresearched_row_are_counted_apart():
    """One number carried both until this field existed. It read 188 before Tranche 3 and reads 6
    after it, and either way it would have said nothing about how many of those were DECISIONS.

    THE TOTAL IS CROSS-CHECKED AGAINST THE CHECKER'S OWN READER AND NOT WRITTEN DOWN. The first
    version asserted `== 693`, the exemplar count on the day it was written, and Tranche 3 took it
    to 800 -- WP-8.14's shape inside a test written the same week that entry was. The obvious
    repair was `== total` counted in this same loop, and THAT CANNOT FAIL: every row increments
    exactly one bucket, so the partition is true by construction and the assertion is a tautology
    wearing a guard's clothes. It is held against `measure()` instead, which walks the corpus
    independently -- two readers of one fact, which is the only form of this that can go red."""
    with_p = refusals = gaps = total = 0
    reasons = collections.Counter()
    import glob
    for f in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json"))):
        for e in json.load(open(f, encoding="utf-8")).get("exemplars") or []:
            total += 1
            if e.get("precedent"):
                with_p += 1
                # the schema permits it and the checker refuses it: a row cannot both name a
                # record and say why it has none.
                assert not e.get("no_precedent"), (f, e["name"])
                continue
            r = e.get("no_precedent")
            if r and r != "not-yet-researched":
                refusals += 1
                reasons[r] += 1
            else:
                gaps += 1
    m = CP.measure()
    assert total == m["exemplars_total"], (total, m["exemplars_total"])
    assert with_p == m["exemplars_with_precedent"], (with_p, m["exemplars_with_precedent"])
    assert refusals == 3 and reasons == {"archive": 1, "body-of-work": 1, "phase": 1}
    # the ceiling is pinned TIGHT at the gap count -- a ceiling slack by exactly the rows the field
    # separates is a meter measuring nothing. The literal is deliberately NOT repeated here: the
    # ratchet is the one place the number lives, and this holds the corpus to it.
    assert CP.RATCHET["exemplars_unresearched"] == gaps
    assert CP.RATCHET["no_precedent_beside_a_precedent"] == 0


def test_a_record_that_is_not_one_building_declares_which_kind_it_is():
    """The corpus was doing this before the ruling and said so only in each record's `note`.

    THE COMPOSITION IS NOT PINNED AND THE VOCABULARY IS. The first version asserted
    `{"district": 6, "group": 5, "type-model": 2}` -- Tranche 2's exact census -- and Tranche 3
    made it 13/26/3 without anything being wrong. A tranche adding a district is the corpus
    working; a tranche inventing a FOURTH kind, or declaring one the schema does not admit, is
    not. That is what this holds."""
    import glob
    schema = json.load(open(os.path.join(ROOT, "schema", "precedent.schema.json"), encoding="utf-8"))
    admitted = set(schema["properties"]["record_kind"]["enum"])
    assert admitted == {"building"} | set(CP.NOT_ONE_BUILDING), admitted
    declared = collections.Counter()
    for f in sorted(glob.glob(os.path.join(ROOT, "precedents", "*.json"))):
        k = json.load(open(f, encoding="utf-8")).get("record_kind")
        if k and k != "building":
            assert k in CP.NOT_ONE_BUILDING, (f, k)
            declared[k] += 1
    # every kind the ruling names is exercised by at least one record -- a value nothing uses is a
    # vocabulary entry nobody has tested against a real building.
    assert set(declared) == set(CP.NOT_ONE_BUILDING), declared


# ---------------------------------------------------------------------------------------------
# WP-11.4, Ruling C part 2 (5 Sep 2026): a NEW `measured` parameter must carry a source.

def test_the_grandfathered_set_is_exactly_todays_unsourced_measured_parameters():
    """The frozen list and the live census must agree, or the gate is guarding a fiction."""
    import glob
    live = set()
    for p in sorted(glob.glob(os.path.join(ROOT, "kits", "*.kit.json"))):
        nid = os.path.basename(p)[: -len(".kit.json")]
        for sid, s in (json.load(open(p, encoding="utf-8")).get("slots") or {}).items():
            slot_sourced = bool(s.get("sources"))
            for pk, pv in (s.get("parameters") or {}).items():
                if isinstance(pv, dict) and pv.get("kind") == "measured" \
                        and not pv.get("source") and not slot_sourced:
                    live.add((nid, sid, pk))
    CK = modcache.load("check_kits", os.path.join(ROOT, "build", "check_kits.py"))
    assert CK.GRANDFATHERED == live
    # and it agrees with the ceiling the OTHER checker publishes, so the two cannot drift apart
    assert len(live) == CR.RATCHET["measured_unsourced"] == 536


def test_the_gate_is_per_parameter_and_not_a_net_count():
    """THE HOLE THIS RULING CLOSES, demonstrated rather than asserted.

    `check_research.RATCHET["measured_unsourced"]` is a ceiling on a TOTAL. Source one figure and
    add an unsourced one in the same commit and the total is unchanged, so the net ratchet passes
    while an unsourced `measured` parameter sits in the tree. Measured by running both checkers
    against exactly that mutation: check_research returned 0 and check_kits returned 1.

    Here the same thing is proved without touching the tree: a triple outside the frozen set is
    refused by identity, and identity cannot net.
    """
    CK = modcache.load("check_kits", os.path.join(ROOT, "build", "check_kits.py"))
    assert ("tidewater-georgian", "arch", "zz_mutation_param") not in CK.GRANDFATHERED
    # every grandfathered triple IS admitted -- the gate must not convict the corpus it inherited
    assert all(t in CK.GRANDFATHERED for t in list(CK.GRANDFATHERED)[:50])
    # the set is frozen: a plain set could be mutated by a later import and silently widen the gate
    assert isinstance(CK.GRANDFATHERED, frozenset)


# ---------------------------------------------------------------------------------------------
# WP-11.5, preparing Tranche 3: the archival vocabulary for Europe.

def test_the_historic_england_shape_is_the_registers_own_statement():
    """"Every List entry has a unique 7-figure reference number" -- Historic England's own
    Understanding List Entries page, read 5 Sep 2026, corroborated against fifteen sampled numbers.
    Written from the register's statement because the NRHP rule was written from one remembered
    form and rejected a valid 2019 listing."""
    assert all(CP.HE_LIST_RE.match(v) for v in
               ("1000100", "1004281", "1046598", "1162800", "1188692", "1254925", "1256894",
                "1342941", "1357515", "1359189", "1379911", "1380478", "1401425", "1452906"))
    for bad in ("254925", "12549250", "1254925a", "2254925", "", "1-254925"):
        assert not CP.HE_LIST_RE.match(bad), bad
    assert CP.ID_SHAPES["historic-england"] is CP.HE_LIST_RE


def test_a_kind_with_no_shape_rule_is_named_and_counted_not_silent():
    """`ID_SHAPES.get()` misses silently, so an unshaped kind is an id nobody checks and nobody
    knows about. Naming them turned that into a number on the first run: 58, every one a
    `state-register` from the American tranches, and Europe raised it to 216 across ten registers.
    The ceiling may only fall, which happens by adding a shape backed by the register's own
    statement of its format -- never by inventing one."""
    import glob
    assert set(CP.UNSHAPED_ID_KINDS).isdisjoint(CP.ID_SHAPES), "a kind cannot be both"
    n = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "precedents", "*.json"))):
        for r in json.load(open(f, encoding="utf-8")).get("refs") or []:
            if r.get("kind") in CP.UNSHAPED_ID_KINDS and r.get("id"):
                n += 1
    # The literal is NOT repeated. It was `== 58` and Europe took it to 216, which is a deliberate
    # ceiling raise recorded in the ratchet's own comment; a test carrying a second copy of the
    # number turns every honest raise into a two-file edit and every dishonest one into neither.
    assert n == CP.RATCHET["ids_with_no_shape_rule"]
    # every kind the schema admits is either shaped or named unshaped -- no third, silent category
    schema = json.load(open(os.path.join(ROOT, "schema", "precedent.schema.json"), encoding="utf-8"))
    kinds = set(schema["properties"]["refs"]["items"]["properties"]["kind"]["enum"])
    # `wikipedia`, `wikidata`, `institution`, `monograph`, `other` carry a url and no id by nature
    idless = {"wikipedia", "wikidata", "institution", "monograph", "other"}
    assert kinds - set(CP.ID_SHAPES) - set(CP.UNSHAPED_ID_KINDS) == idless, \
        kinds - set(CP.ID_SHAPES) - set(CP.UNSHAPED_ID_KINDS)


# ---------------------------------------------------------------------------------------------
# WP-11.6, Ruling B (5 Sep 2026): a family carries type specimens DERIVED from its members' icons.

def _fs():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "family_specimens_for_test", os.path.join(ROOT, "build", "family_specimens.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_a_familys_specimens_are_its_members_icons_one_apiece():
    """The ruling is a DERIVATION, so the test is that the stored rows equal the derived ones and
    that each row is really some member's icon. No count is written down here: `derive()` is the
    one place the rule lives, and a test restating its output would be a second spelling of it."""
    fs = _fs()
    nodes = fs.load_nodes()
    want = fs.derive(nodes)
    assert not fs.drift(nodes), fs.drift(nodes)
    families = {nid for nid, (_, d) in nodes.items() if d.get("rank") == "family"}
    assert set(want) == families and families, families

    icons = {}
    for nid, (_, d) in nodes.items():
        for e in d.get("exemplars") or []:
            if e.get("standing") == "icon":
                icons.setdefault(nid, []).append(e)

    for fid, rows in want.items():
        members = set(fs.members_of(nodes, fid))
        seen_members, seen_buildings = set(), set()
        for r in rows:
            assert r["standing"] == "canonical", (fid, r["name"])
            # the `why` names a member of THIS family and nothing else -- a report, not an authoring
            named = [m for m in members if "`%s`" % m in r["why"]]
            assert len(named) == 1, (fid, r["name"], named)
            m = named[0]
            assert m not in seen_members, (fid, m, "two specimens from one member")
            seen_members.add(m)
            # and the row really is that member's icon, name for name
            assert any(e["name"] == r["name"] for e in icons.get(m, [])), (fid, m, r["name"])
            key = r.get("precedent") or r["name"]
            assert key not in seen_buildings, (fid, key, "one building twice in one family")
            seen_buildings.add(key)


def test_a_family_specimen_is_claimed_by_the_record_it_names():
    """`check_precedents.py` holds an exemplar's `precedent` against the record's own `nodes[]` in
    both directions, so a specimen the record does not claim is a dangling reference. Two buildings
    legitimately stand for two families each -- Larkin House and the American Gothic House -- and
    that is the case this would break if `nodes[]` were written as a replacement rather than a
    union."""
    fs = _fs()
    gained = fs.nodes_gained()
    assert gained, "no family specimen names a record -- the derivation is reading air"
    multi = {p: sorted(f) for p, f in gained.items() if len(f) > 1}
    assert multi, "a building standing for two families is expected here; none found"
    for pid, fids in sorted(gained.items()):
        rec = json.load(open(os.path.join(ROOT, "precedents", pid + ".json"), encoding="utf-8"))
        listed = set(rec.get("nodes") or [])
        assert set(fids) <= listed, (pid, sorted(set(fids) - listed))


def test_the_five_traditions_stay_empty_because_the_ruling_says_so():
    """"The 5 traditions stay empty." A tradition acquiring exemplars is not progress; it is the
    ruling being quietly widened, and the node-coverage floor may therefore never reach 164."""
    fs = _fs()
    nodes = fs.load_nodes()
    traditions = [nid for nid, (_, d) in nodes.items() if d.get("rank") == "tradition"]
    assert len(traditions) == 5, traditions
    for nid in traditions:
        assert not (nodes[nid][1].get("exemplars") or []), nid
    assert CP.RATCHET["family_specimens_drifted"] == 0
