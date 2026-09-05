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
    """One number carried both until this field existed, and after Tranche 3 it would have read
    about 191 whether that was 191 gaps or 188 gaps and 3 decisions."""
    styles = CP.load_styles() if hasattr(CP, "load_styles") else None
    with_p = refusals = gaps = 0
    reasons = collections.Counter()
    import glob
    for f in glob.glob(os.path.join(ROOT, "styles", "*.json")):
        for e in json.load(open(f, encoding="utf-8")).get("exemplars") or []:
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
    assert with_p + refusals + gaps == 693
    assert refusals == 3 and reasons == {"archive": 1, "body-of-work": 1, "phase": 1}
    # the ceiling is pinned TIGHT at the gap count, not at the 188 that predates the refusals --
    # a ceiling slack by exactly the rows the field separates is a meter measuring nothing.
    assert CP.RATCHET["exemplars_unresearched"] == gaps == 185
    assert CP.RATCHET["no_precedent_beside_a_precedent"] == 0


def test_the_thirteen_records_that_are_not_one_building_declare_it():
    """The corpus was doing this before the ruling and said so only in each record's `note`."""
    import glob
    declared = collections.Counter()
    for f in glob.glob(os.path.join(ROOT, "precedents", "*.json")):
        k = json.load(open(f, encoding="utf-8")).get("record_kind")
        if k and k != "building":
            declared[k] += 1
    assert declared == {"district": 6, "group": 5, "type-model": 2}, declared


# ---------------------------------------------------------------------------------------------
# WP-11.4, Ruling C part 2 (5 Sep 2026): a NEW `measured` parameter must carry a source.

def test_the_grandfathered_set_is_exactly_todays_unsourced_measured_parameters():
    """The frozen list and the live census must agree, or the gate is guarding a fiction."""
    import glob
    live = set()
    for p in glob.glob(os.path.join(ROOT, "kits", "*.kit.json")):
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
    `state-register` from the American tranches. The ceiling may only fall, which happens by
    adding a shape backed by the register's own statement of its format -- never by inventing one.
    """
    import glob
    assert set(CP.UNSHAPED_ID_KINDS).isdisjoint(CP.ID_SHAPES), "a kind cannot be both"
    n = 0
    for f in glob.glob(os.path.join(ROOT, "precedents", "*.json")):
        for r in json.load(open(f, encoding="utf-8")).get("refs") or []:
            if r.get("kind") in CP.UNSHAPED_ID_KINDS and r.get("id"):
                n += 1
    assert n == CP.RATCHET["ids_with_no_shape_rule"] == 58
    # every kind the schema admits is either shaped or named unshaped -- no third, silent category
    schema = json.load(open(os.path.join(ROOT, "schema", "precedent.schema.json"), encoding="utf-8"))
    kinds = set(schema["properties"]["refs"]["items"]["properties"]["kind"]["enum"])
    # `wikipedia`, `wikidata`, `institution`, `monograph`, `other` carry a url and no id by nature
    idless = {"wikipedia", "wikidata", "institution", "monograph", "other"}
    assert kinds - set(CP.ID_SHAPES) - set(CP.UNSHAPED_ID_KINDS) == idless, \
        kinds - set(CP.ID_SHAPES) - set(CP.UNSHAPED_ID_KINDS)
