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

SHARED_ONLY = {
    "carpenter-gothic", "colonial-revival", "creole-cottage-vernacular", "dutch-colonial-american",
    "dutch-colonial-revival", "elizabethan", "folk-victorian", "french-normandy-revival",
    "french-provincial-farmhouse", "georgian-colonial-american", "georgian-revival", "hudson-valley-dutch",
    "italian-renaissance-revival", "italianate-american", "italianate-villa", "neoclassical-revival",
    "new-england-colonial", "norman-vernacular", "queen-anne-american", "queen-anne-free-classic",
    "raised-creole-plantation", "saltbox-colonial", "spanish-colonial-american", "stick-style",
}
UNTESTED = {"queen-anne-free-classic", "queen-anne-spindled", "roman-classical"}
# WIDENED AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026), AND THE GENERATOR IS NAMED, as this
# set's own rule requires: `build/threshold.py` joined `check_research.GENERATOR_FILES`, because
# the other branch's WP-11.4 moved `roof_form_for`, the ridge axis and the gable-end points out
# of `roof.py` and into it. `roof_form` was about to leave this set -- the walk found no reader
# -- and it has one; `hearth_position`, `porch_support` and `steps_and_stoop` were never in it
# and always read. Four slots ARRIVED; none left.
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
    "hearth_position",
    "height_proportion",
    "orientation_rule",
    "pilaster",
    "porch_depth",
    "porch_support",
    "porch_type",
    "reveal_frame",
    "reveal_masonry",
    "roof_form",
    "room_adjacency_overrides",
    "setback_rule",
    "shutter",
    "stair_type",
    "steps_and_stoop",
    "transom_sidelight",
    "water_table",
    "window_grouping_rule",
    "window_head_masonry",
    "window_head_wood",
    "window_lite_pattern",
    "window_proportion",
    "window_type",
}


def _counts():
    """`check_counts.py`, loaded the way this file loads every other checker. It is the OWNER of
    the corpus node count -- `computed()["nodes"]` is `len(nodes)` -- and reading it is what keeps
    the non-vacuity assertion below from being a literal pinned to itself."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_counts_for_test", os.path.join(ROOT, "build", "check_counts.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_no_node_in_the_corpus_cites_nothing():
    """THE SUBJECT IS DISCHARGED AND THE PIN IS TIGHT AT ZERO. This test used to hold a
    32-name literal -- every family and every tradition, the only nodes citing no source -- and
    assert that each was higher rank. WP-11.7 gave all 32 a literature, so the set is empty and
    the literal described a corpus that no longer exists. It is deleted rather than emptied in
    place: an inert wrong list is an instruction to the next reader, which is the lesson the
    proportion-floor ruling was taken on.

    What remains is the property the literal was standing in for, and it is stronger: NO node,
    at any rank, cites nothing. A node appearing here is a regression whoever wrote it, and the
    remedy is to source it, never to re-pin this ceiling upward.

    The rank check the old test carried is gone with the set. It said "and every one of these is
    higher rank", which is a claim about WHICH nodes are sourceless; with none, there is nothing
    to be higher rank."""
    m = CR.measure()
    assert m["totals"]["sourceless_nodes"] == [], m["totals"]["sourceless_nodes"]
    # NON-VACUITY, held against a DERIVED figure and not a literal. An empty assertion is satisfied
    # by a measure() that read no nodes at all, which is how a guard goes quiet -- but the first
    # version of this line wrote `== 164` under a comment saying "check_counts.py owns the figure",
    # and check_counts owns no such literal: it computes `v["nodes"] = len(nodes)`. So the number
    # was pinned to ITSELF, which is the pattern this same file refuses two hundred lines below
    # (`assert n == CP.RATCHET[...]`), and it went red on a corpus of 165 -- a legitimate addition
    # breaking a test that has no opinion about node counts. Read the owner instead.
    assert len(m["per_node"]) == _counts().computed()["nodes"], len(m["per_node"])
    assert all(n["sources"] for n in m["per_node"].values())


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
        "sourceless_nodes": len(m["sourceless_nodes"]),
        "untested_nodes": len(m["untested_nodes"]),
        "exemplars_with_precedent": m["exemplars_with_precedent"],
        "nodes_with_a_precedent": m["nodes_with_a_precedent"],
    }
    # THE REBUILD IS PINNED, because this dict is rebuilt key-by-key and a new RATCHET entry would
    # otherwise reach it as a KeyError deep in the loop -- the shape `proportion_engine.evaluate()`
    # was caught by, where a new rule field was silently dropped by a hand-written rebuild. It DID
    # fire here when WP-11.7 added `sourceless_nodes`; this says what happened instead of raising.
    assert set(got) == set(CR.RATCHET), (
        "the ratchet and this rebuild disagree; add the key here too: %s"
        % sorted(set(CR.RATCHET) ^ set(got)))
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


# ---------------------------------------------------------------------------------------------
# WP-11.7. The guard that makes authoring a higher-rank node's literature safe.

def _hazard():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "family_source_hazard_for_test", os.path.join(ROOT, "build", "family_source_hazard.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_hazard_guard_and_check_research_agree_about_shared_only():
    """TWO INDEPENDENT READERS OF ONE RULE. `family_source_hazard.shared_only` exists so an author
    can be told BEFORE writing a source what `check_research.py` will say after; a guard that
    predicts the checker wrongly is worse than none, because its output is advice.

    The first version of that module read `shared_only` over BUILDABLE nodes only, and
    `check_research` reads it over all 164 -- so it advised "prefer a work the corpus already
    cites", which is the one thing that makes a FAMILY `shared_only` itself. That died the first
    time the advice was applied and the real checker run, not on any re-reading. This holds the two
    populations together so it cannot come back."""
    H = _hazard()
    nodes = H.load_nodes()
    mine = H.shared_only(nodes)
    # check_research's own reader, not a transcription of it
    theirs = set(CR.measure()["totals"]["shared_only_nodes"]) if hasattr(CR, "measure") else None
    assert theirs is not None, "check_research.measure() moved; this guard is reading air"
    assert mine == theirs, sorted(mine ^ theirs)
    assert mine, "nobody is shared_only -- the comparison is vacuous"

    # AND THE LIVE CORPUS CANNOT PROVE THE POINT, which mutation-checking is how we know: with no
    # higher-rank node citing anything, restricting `shared_only` to buildable nodes changes
    # nothing and the comparison above stays green on the very defect it exists for. So the
    # population is driven through a CONSTRUCTED case -- a family citing only already-shared works,
    # which is what the rank restriction would wrongly acquit.
    counts = H.cited_by(nodes)
    shared = sorted(s for s, n in counts.items() if n >= 2)
    assert shared, "no work is cited twice; this fixture is reading a different corpus"
    fam = "english-classical"
    assert nodes[fam]["rank"] == "family"
    probe = {i: dict(n) for i, n in nodes.items()}
    probe[fam]["sources"] = [shared[0]]
    assert fam in H.shared_only(probe), (
        "a family citing only already-cited works must read as shared_only -- it does in "
        "check_research, whose population is all 164 nodes")


def test_a_higher_rank_node_needs_a_work_of_its_own():
    """The rule the package is authored under, asserted on the real corpus rather than a fixture:
    a list made entirely of already-cited works is refused, and one carrying a work nobody else
    cites is accepted. Both verdicts are needed -- a guard that only ever says `unsafe` would pass
    the first assertion alone."""
    H = _hazard()
    nodes = H.load_nodes()
    counts = H.cited_by(nodes)
    shared = [s for s, n in counts.items() if n >= 2]
    assert shared, "no work is cited twice; this fixture is reading a different corpus"
    fam = "english-classical"
    assert nodes[fam]["rank"] == "family"

    v, why = H.judge_list(fam, [shared[0]], nodes)
    assert v == "unsafe", (v, why)
    assert any("shared_only" in w for w in why), why

    v, why = H.judge_list(fam, ["A Work No Other Node Cites (2026)", shared[0]], nodes)
    assert v == "ok", (v, why)


def _hazard_violations(H, nodes):
    """THE SWEEP'S RULE, IN ONE PLACE, WITH TWO CALLERS -- the live corpus and the injected one.

    It is a function rather than a loop inside each test for a reason this repo has paid for twice:
    a rule restated in a test is a rule the test can hold while the shipped one is broken
    (`test_asset_provenance.py`: "a branch only a test copy reaches is not a guard on anything").
    The first repair of the tautology below put the corrected rule in a NEW test and left the sweep
    to restate it, and a mutation reverting the sweep's scoping stayed green in both -- the fix was
    unfalsifiable in exactly the way the defect had been. Both callers read this now, so reverting
    the population here turns the injection test RED.

    THE BASELINE IS THE CORPUS WITH THE NODES UNDER TEST REMOVED, and getting there took two
    goes. `hazards()` drops a string two ways once a higher-rank node cites it: `cited_by` reaches
    2, and the victim itself lands in `already` (it is `shared_only` now, so it is no longer at
    risk -- the damage is done). Scoping by RANK alone fixed only the first, and the second
    reproduced the tautology exactly. Both close only if the higher-rank sources are not in the
    corpus the set is derived from at all.

    So: blank every higher-rank node's sources, take the hazards of THAT, and hold the real
    higher-rank sources against it. The baseline cannot be moved by the thing it is judging."""
    baseline = {}
    for i, n in nodes.items():
        if n.get("rank") in H.HIGHER:
            n = dict(n)
            n["sources"] = []
        baseline[i] = n
    haz = H.hazards(baseline)
    return haz, [(i, s, haz[s.strip()])
                 for i, n in nodes.items() if n.get("rank") in H.HIGHER
                 for s in (n.get("sources") or []) if s.strip() in haz]


def test_no_higher_rank_node_may_cite_one_of_the_hazard_strings():
    """Each is some buildable node's ONLY unique citation, so a second citation anywhere flips that
    node. Asserted over the corpus as it stands, so it keeps holding as more sources are written."""
    H = _hazard()
    nodes = H.load_nodes()

    # THE HAZARD SET MUST BE DERIVED FROM A POPULATION THAT EXCLUDES THE NODES UNDER TEST, AND THE
    # FIRST VERSION OF THIS SWEEP DID NOT -- it was a mathematical tautology and could not fail at
    # any corpus state. `hazards()` admits a string only when `cited_by[s] == 1` and its sole citer
    # is buildable; so the moment a HIGHER-RANK node cites one, the count is 2 and the string drops
    # out of the set BEFORE the loop reads it. `assert s not in haz` was `x not in (a set defined
    # to exclude x)`. Measured on the real corpus: adding a hazard string to `english-classical`
    # takes `shared_only` 24 -> 25 -- which breaks RATCHET["shared_only_nodes"] -- while the hazard
    # set merely shrinks 38 -> 37 and the sweep says nothing.
    #
    # The mutation that "proved" the old version was the wrong mutation: it skipped every node and
    # watched a `checked > 0` counter go red, which exercises the ITERATION and never the
    # ASSERTION. Assert the mutation lands on the thing under test, not next to it.
    #
    # `hazards()` itself is deliberately unchanged: for the WRITER, a string a family already cites
    # is correctly no longer a hazard, because that damage is already done. The writer and this
    # sweep ask genuinely different questions, so each states its own population rather than
    # sharing one and being wrong for one of them.
    haz, violations = _hazard_violations(H, nodes)
    assert haz, "no hazardous string found -- the guard has gone blind"
    assert violations == [], violations

    # THE DRIVEN CASE. `judge_list` must REFUSE a hazard string on a family even when the family
    # also carries a work of its own -- otherwise the only thing refusing it is the absence of any
    # family sources at all -- which Tranche 4 removed, which is why this case is not optional.
    victim = sorted(haz.items())[0]
    v, why = H.judge_list("english-classical",
                          ["A Work No Other Node Cites (2026)", victim[0]], nodes)
    assert v == "unsafe", (v, why)
    assert any(victim[1] in w for w in why), (victim[1], why)


def test_the_hazard_sweep_fires_when_a_family_cites_one():
    """THE MUTATION AS A TEST, because a commit message saying a guard was mutation-checked is not
    a guard. The sweep above asserted nothing for as long as it existed and every check was green;
    what makes that impossible to repeat is not the fix but this case, which plants the exact
    defect and requires the sweep's own rule to reject it.

    The corpus was never unprotected -- `RATCHET["shared_only_nodes"] = 24` catches this injection
    too, and is asserted here so the two guards are known to agree rather than assumed to. What was
    broken was the guard that names the offending node and string, which is the difference between
    a located question and a bare ratchet break."""
    H = _hazard()
    nodes = H.load_nodes()
    haz, clean = _hazard_violations(H, nodes)
    assert clean == [], clean
    string, victim_node = sorted(haz.items())[0]

    bad = {i: dict(n) for i, n in nodes.items()}
    bad["english-classical"] = dict(bad["english-classical"])
    bad["english-classical"]["sources"] = list(bad["english-classical"]["sources"]) + [string]

    # The damage is real: the buildable node loses its only unique citation.
    assert victim_node not in H.shared_only(nodes)
    assert victim_node in H.shared_only(bad), (
        "the injection did not land -- this test is proving nothing")

    # THE SWEEP'S OWN RULE, through the SAME function the live sweep calls. Reverting that
    # function's population to the whole corpus makes this assertion fail, which is the property
    # the first repair lacked.
    _, fired = _hazard_violations(H, bad)
    assert [(i, s) for i, s, _ in fired] == [("english-classical", string)], fired

    # And the ratchet catches it too, so the corpus was never unprotected -- what the sweep adds is
    # the NAME of the offending node and string. Asserted rather than assumed, because "the other
    # guard covers it" is exactly the belief that let this one go unfixed.
    assert len(H.shared_only(bad)) > len(H.shared_only(nodes)) == CR.RATCHET["shared_only_nodes"]

    # And the tautology itself, pinned: derived from the WHOLE corpus the set no longer contains
    # the string, so a sweep scoped that way would stay silent. If this stops holding, `hazards()`
    # has changed shape and the comment above needs rewriting rather than this test deleting.
    assert string not in H.hazards(bad), (
        "hazards() no longer drops a string once a family cites it; re-read why the sweep "
        "scopes its population, because the reason may have expired")


# ---------------------------------------------------------------------------------------------
# The audit of WP-11.7 (7 Sep 2026). Everything below covers a behaviour that shipped with NO test
# at all, or a mutant that survived every test the package landed with. Each was found by
# reverting the code and watching the suite stay green -- never by re-reading it.

def _sandbox(tmp_path):
    """A COPY of `styles/` for the writer tests, used through `set_sources(..., root=)`.

    THE SEAM IS IN THE PRODUCTION FUNCTION, not a rewritten copy of it. Every READ in that module
    takes an injectable `nodes` dict and the WRITE derived its path from module-level `ROOT`, so
    the only way to exercise the write was to write to the real corpus. That is not a theoretical
    objection: mutation-testing the refusals -- deliberately removing the gates keeping the writer
    away from `styles/` -- destroyed authored research in three style files, twice, before this
    seam existed. A writer whose only reachable test target is the live corpus is a writer whose
    tests are the hazard.

    The earlier version of this helper rewrote the module source with ROOT replaced, which works
    but tests a copy; `root=` tests the shipped function."""
    import shutil
    if not (tmp_path / "styles").exists():
        shutil.copytree(os.path.join(ROOT, "styles"), str(tmp_path / "styles"))
    return str(tmp_path)


def test_the_writer_refuses_every_way_a_list_can_be_wrong(tmp_path):
    """`set_sources` is the WRITER, and it shipped with no test and no caller. Its docstring calls
    it "the one function that writes the field ... a rule none of them can get past", and nothing
    held it to that: every refusal path below was unexercised, including the one the function
    exists for.

    IT RUNS AGAINST A COPY, AND THE FIRST VERSION DID NOT -- which is a defect this test earned by
    being mutation-checked. Driving a WRITER at the live tree is safe only while its refusals work,
    and the whole point of mutating them is to break exactly that: neutering the rank gate and the
    unsafe-list gate made this test WRITE THREE REAL `styles/*.json` FILES, replacing authored
    research with fixture strings. `assert after == before` catches it afterwards, which is a
    report of the damage rather than a guard against it. A test that proves a writer refuses must
    not hand it anything it would be a disaster to write to."""
    H = _hazard()
    root = _sandbox(tmp_path)
    nodes = H.load_nodes()
    before = json.load(open(str(tmp_path / "styles" / "english-classical.json"), encoding="utf-8"))

    # 1. unknown node -- could-not-judge, never a bool and never "unsafe" (the question does not arise)
    w, v, why = H.set_sources("no-such-node-at-all", ["A Work (2026)"], nodes, root=root)
    assert (w, v) == (False, "could-not-judge"), (w, v, why)

    # 2. a BUILDABLE node -- this writer is for higher rank only; also could-not-judge
    w, v, why = H.set_sources("tidewater-georgian", ["A Work (2026)"], nodes, root=root)
    assert (w, v) == (False, "could-not-judge"), (w, v, why)
    assert any("rank" in x for x in why), why

    # 3. a repeated work -- unsafe, and it must be caught BEFORE judge_list, because a duplicate
    #    would otherwise read as two citations of one work and inflate `own`.
    w, v, why = H.set_sources("english-classical", ["A Work (2026)", "A Work (2026)"], nodes, root=root)
    assert (w, v) == (False, "unsafe"), (w, v, why)
    assert any("repeats" in x for x in why), why

    # 4. a hazard string -- the refusal the module exists for
    haz = H.hazards(nodes, ranks=H.BUILDABLE)
    victim = sorted(haz)[0]
    w, v, why = H.set_sources("english-classical", ["A Work No Other Node Cites (2026)", victim], nodes, root=root)
    assert (w, v) == (False, "unsafe"), (w, v, why)

    # 5. a list of nothing but already-cited works -- the node flips ITSELF; the defect the
    #    approved protocol would have produced on every one of the 32 nodes.
    counts = H.cited_by(nodes)
    shared = sorted(s for s, n in counts.items() if n >= 2)
    w, v, why = H.set_sources("english-classical", [shared[0], shared[1]], nodes, root=root)
    assert (w, v) == (False, "unsafe"), (w, v, why)
    assert any("shared_only" in x for x in why), why

    # 6. an empty list -- could-not-judge: a node citing nothing is the GAP, not a flip.
    w, v, why = H.set_sources("english-classical", [], nodes, root=root)
    assert (w, v) == (False, "could-not-judge"), (w, v, why)

    # NOTHING WAS WRITTEN. Asserted rather than trusted, because every case above is one line away
    # from the `open(path, "w")` that truncates the file.
    after = json.load(open(str(tmp_path / "styles" / "english-classical.json"), encoding="utf-8"))
    assert after == before, "set_sources wrote on a refusal path"


def test_the_writer_places_sources_after_exemplars_and_writes_atomically(tmp_path):
    """The happy path, and the two properties nothing checked: WHERE the key lands, and that the
    write cannot truncate the record.

    Run against a COPY of the corpus so the real tree is untouched -- `ROOT` is repointed, which is
    the same shim `tests/test_asset_provenance.py` uses to drive a checker over a fixture."""
    H = _hazard()
    root = _sandbox(tmp_path)
    nodes = H.load_nodes()
    unique = "A Work Written For This Test And Cited By No Other Node (2026)"
    w, v, why = H.set_sources("english-classical", [unique], nodes, root=root)
    assert (w, v) == (True, "ok"), (w, v, why)

    doc = json.load(open(str(tmp_path / "styles" / "english-classical.json"), encoding="utf-8"))
    assert doc["sources"] == [unique]
    keys = list(doc)
    assert keys.index("sources") == keys.index("exemplars") + 1, keys
    # every other key keeps its position -- the diff is the field and nothing else
    orig = list(json.load(open(os.path.join(ROOT, "styles", "english-classical.json"),
                               encoding="utf-8")))
    assert [k for k in keys if k != "sources"] == [k for k in orig if k != "sources"]
    # ATOMIC: no .tmp survives a successful write, and the file is valid JSON (it is, above).
    assert not list((tmp_path / "styles").glob("*.tmp")), "a temp file was left behind"


def test_cited_by_counts_every_rank_and_that_is_where_the_invariant_lives():
    """THE MUTANT THAT SURVIVED EVERYTHING. Restricting `cited_by` to buildable nodes leaves all
    three of WP-11.7's tests green while INVERTING the guard's advice -- and `cited_by`'s own
    docstring names that as the defect the module exists to prevent.

    The existing agreement test cannot see it: its fixture is drawn from `H.cited_by` itself, so
    the fixture moves with the mutation. This asserts the population directly, on a real pair --
    a work cited ONLY by two higher-rank nodes, which a buildable-only counter reads as cited by
    nobody."""
    H = _hazard()
    nodes = H.load_nodes()
    counts = H.cited_by(nodes)

    both_higher = [
        s for s, n in counts.items() if n >= 2
        and all(s not in (d.get("sources") or [])
                for d in nodes.values() if d.get("rank") in H.BUILDABLE)]
    assert both_higher, (
        "no work is cited only by higher-rank nodes, so this guard is vacuous -- the fixture it "
        "needs is a real pair, and Tranche 4 created two (Cuisenier and Baumgarten)")

    for s in both_higher:
        assert counts[s] >= 2, (s, counts[s])
        citers = [i for i, d in nodes.items() if s in (d.get("sources") or [])]
        assert all(nodes[i]["rank"] in H.HIGHER for i in citers), (s, citers)

    # And the consequence, which is what a buildable-only counter would get wrong: a node whose
    # every source is one of these is `shared_only`, and a guard that counted only buildable citers
    # would call it safe.
    probe = {i: dict(n) for i, n in nodes.items()}
    probe["english-classical"] = dict(probe["english-classical"])
    probe["english-classical"]["sources"] = [both_higher[0]]
    assert "english-classical" in H.shared_only(probe)
    v, why = H.judge_list("english-classical", [both_higher[0]], nodes)
    assert v == "unsafe", (v, why)


def test_hazards_admits_only_a_node_with_exactly_one_unique_citation():
    """M9: `len(uniq) == 1` -> `>= 1` survived every test. A node with SEVERAL unique citations is
    not hazardous -- losing one still leaves it others -- so admitting it produces refusals of
    perfectly safe works. Pinned by the property, not by the count of 38."""
    H = _hazard()
    nodes = H.load_nodes()
    counts = H.cited_by(nodes)
    haz = H.hazards(nodes, ranks=H.BUILDABLE)
    for s, node in haz.items():
        uniq = [x for x in (nodes[node].get("sources") or []) if counts[x] == 1]
        assert uniq == [s], (node, s, uniq)
    # non-vacuity: some buildable node really does carry more than one unique citation, so the
    # `== 1` test is doing work rather than being trivially true of the corpus.
    multi = [i for i, n in nodes.items() if n.get("rank") in H.BUILDABLE
             and len([x for x in (n.get("sources") or []) if counts[x] == 1]) > 1]
    assert multi, "no node has two unique citations; this guard cannot distinguish == 1 from >= 1"
    assert not (set(multi) & set(haz.values())), sorted(set(multi) & set(haz.values()))


def test_the_writer_gates_traditions_as_well_as_families(tmp_path):
    """M13: `HIGHER = ("family",)` survived every test, silently un-gating all five traditions --
    the nodes with the LEAST literature of their own, and so the ones most likely to be handed a
    list of already-cited works. A tradition must reach the same refusals a family does.

    Shimmed onto a COPY like every other writer test: under the M13 mutation the rank gate is gone,
    and an unshimmed run wrote a real tradition file."""
    H = _hazard()
    root = _sandbox(tmp_path)
    nodes = H.load_nodes()
    trads = [i for i, n in nodes.items() if n.get("rank") == "tradition"]
    assert len(trads) == 5, trads
    counts = H.cited_by(nodes)
    shared = sorted(s for s, n in counts.items() if n >= 2)
    for t in trads:
        w, v, why = H.set_sources(t, [shared[0], shared[1]], nodes, root=root)
        assert (w, v) == (False, "unsafe"), (t, w, v, why)
        assert any("shared_only" in x for x in why), (t, why)


def test_the_verdict_simulates_the_whole_corpus_not_a_list_of_thirty_eight_strings():
    """THE THREE HOLES THE STRING-BY-STRING MODEL HAD, each found by an auditor reverting the code
    and each proved against the live corpus before it was fixed.

    The rule is a property of the corpus AFTER the write, and approximating it string by string
    missed every case the strings did not cover."""
    H = _hazard()
    nodes = H.load_nodes()
    counts = H.cited_by(nodes)

    # HOLE 1: a HIGHER-RANK node's only unique work is never in `hazards()` (it admits buildable
    # victims only), so citing it from another family was judged `ok` -- and the package's own
    # report names `northern-european-vernacular` as the node with zero headroom.
    nev = [s for s in (nodes["northern-european-vernacular"].get("sources") or [])
           if counts[s] == 1]
    assert len(nev) == 1, nev
    # The advisory list SEES it now (that was C1, fixed): buildable-only was the same population
    # mistake the module docstring says it had already learned once.
    assert nev[0] in H.hazards(nodes), "the advisory set went buildable-only again"
    assert nev[0] not in H.hazards(nodes, ranks=H.BUILDABLE), "the sweep population must exclude it"
    v, why = H.judge_list("english-classical", ["A Brand New Work (2026)", nev[0]], nodes)
    assert v == "unsafe", (v, why)
    assert any("northern-european-vernacular" in w for w in why), why

    # HOLE 2: a victim with TWO unique works is invisible to any per-string test -- cite both and
    # it flips anyway. 43 buildable nodes were exposed.
    two = [(i, [s for s in (d.get("sources") or []) if counts[s] == 1])
           for i, d in nodes.items() if d.get("rank") in H.BUILDABLE]
    two = [(i, u) for i, u in two if len(u) == 2]
    assert two, "no buildable node has exactly two unique citations; this guard is vacuous"
    victim, uniques = two[0]
    assert not any(u in H.hazards(nodes) for u in uniques), (
        "a node with two unique works is in no per-string hazard set, at any population -- which "
        "is exactly why the verdict has to simulate the corpus instead of looking strings up")
    v, why = H.judge_list("english-classical", uniques, nodes)
    assert v == "unsafe", (victim, v, why)
    assert any(victim in w for w in why), (victim, why)

    # HOLE 3: a repeated string counted twice toward "works of its own".
    v, why = H.judge_list("english-classical", ["New Work Z (2026)", "New Work Z (2026)"], nodes)
    assert v == "unsafe", (v, why)
    assert any("repeats" in w for w in why), why

    # AND THE CORPUS AS IT STANDS IS OK ON EVERY HIGHER-RANK NODE -- without this the three
    # assertions above are satisfied by a judge that refuses everything.
    for i, d in nodes.items():
        if d.get("rank") in H.HIGHER:
            assert H.judge_list(i, d.get("sources"), nodes)[0] == "ok", i


def test_judge_list_answers_could_not_judge_and_never_crashes():
    """Three verdicts, never a bool -- and never a traceback. `None` raised TypeError; a BUILDABLE
    node was judged as though the rule applied to it, so `--check colonial-revival` printed
    "UNSAFE ... `--strict` would break its ceiling" about a node that is ratcheted `shared_only`
    and perfectly green. A tool asserting the opposite of the checker, in the imperative."""
    H = _hazard()
    nodes = H.load_nodes()
    for bad_input in (None, [], ["   "], ["", None]):
        v, why = H.judge_list("english-classical", bad_input, nodes)
        assert v == "could-not-judge", (bad_input, v, why)
    v, why = H.judge_list("no-such-node-xyz", ["A Work (2026)"], nodes)
    assert v == "could-not-judge", (v, why)
    v, why = H.judge_list("colonial-revival", nodes["colonial-revival"]["sources"], nodes)
    assert v == "could-not-judge", (v, why)
    assert any("rank" in w for w in why), why


def test_the_cli_tells_a_typo_from_a_regression_and_exits_two_for_neither():
    """`--check <typo>` printed "CITES NOTHING -- a regression: the ceiling is 0" and exited 0: a
    mistyped argument reported as corpus damage, and reported as success. Both directions wrong at
    once, in the branch added to retire a spent claim.

    Exit codes: 1 UNSAFE, 2 COULD NOT EVALUATE, 0 clean -- 2 being the code `check_all.py` already
    uses for the third state."""
    def run(*args):
        return subprocess.run([sys.executable, os.path.join(ROOT, "build", "family_source_hazard.py")]
                              + list(args), capture_output=True, text=True, cwd=ROOT)
    r = run("--check", "no-such-node-xyz")
    assert r.returncode == 2, (r.returncode, r.stdout)
    assert "no such node" in r.stdout and "regression" not in r.stdout, r.stdout

    r = run("--check", "colonial-revival")          # buildable: the rule does not apply
    assert r.returncode == 2, (r.returncode, r.stdout)
    assert "COULD NOT JUDGE" in r.stdout, r.stdout
    assert "would break its ceiling" not in r.stdout, r.stdout

    r = run("--check", "victorian")                 # a real family, as it stands
    assert r.returncode == 0, (r.returncode, r.stdout)

    r = run("--sweep")                              # the whole corpus is clean
    assert r.returncode == 0, (r.returncode, r.stdout[-800:])


def test_the_corpus_counter_does_not_strip_so_it_cannot_drift_from_check_research():
    """M14: `cited_by` counted `s.strip()` while `check_research.py:160` counts the raw string, so
    a whitespace-carrying source would be MERGED here and counted apart there. 0 strings in the
    corpus need stripping, so the two agreed by luck and every mutation stayed green -- the
    divergence could only be shown on a constructed case, which is what this is."""
    H = _hazard()
    nodes = H.load_nodes()
    work = "A Work Cited Twice With Different Whitespace (2026)"
    probe = {i: dict(n) for i, n in nodes.items()}
    probe["english-classical"] = dict(probe["english-classical"]); probe["english-classical"]["sources"] = [work]
    probe["victorian"] = dict(probe["victorian"]); probe["victorian"]["sources"] = [work + " "]

    counts = H.cited_by(probe)
    assert counts[work] == 1 and counts[work + " "] == 1, dict(counts)

    # check_research's own counter, over the same probe -- the two must agree string for string.
    theirs = collections.Counter()
    for d in probe.values():
        for s in d.get("sources") or []:
            theirs[s] += 1
    assert counts[work] == theirs[work] and counts[work + " "] == theirs[work + " "]
    assert "" == "".strip() and work != work + " ", "the fixture must actually differ by whitespace"


def test_the_schema_refuses_a_blank_or_repeated_source():
    """`sourceless_nodes` counts LIST LENGTH, so a node citing `[""]` read as one source and
    satisfied the ceiling pinned tight at 0, the new `check_counts` CLAIM, and this file's own
    `assert all(n["sources"] ...)` -- all three, with the node citing nothing. Nothing in `build/`
    rejected a blank string. The ratchet became a load-bearing guarantee in WP-11.7 and the
    validation under it did not move; this is that gap closed at the schema, where `validate.py`
    enforces it for every node at once."""
    import copy
    import jsonschema
    schema = json.load(open(os.path.join(ROOT, "schema", "style-node.schema.json"), encoding="utf-8"))
    doc = json.load(open(os.path.join(ROOT, "styles", "victorian.json"), encoding="utf-8"))
    jsonschema.validate(doc, schema)          # the real record must still pass
    for bad in ([""], ["   "], ["A Work (2026)", "A Work (2026)"]):
        probe = copy.deepcopy(doc); probe["sources"] = bad
        try:
            jsonschema.validate(probe, schema)
            raise AssertionError("schema accepted %r" % (bad,))
        except jsonschema.ValidationError:
            pass
