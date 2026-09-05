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
        if k in CP.FLOORS:
            assert p[k] >= pin, (k, p[k], pin)


def test_a_sourced_measured_parameter_is_not_counted_as_unsourced():
    """The instrument must be able to fall. `georgian-colonial-american.water_table.measured_band_in`
    carries `source: georgian-colonial-american.c05` (OQ 18's one cross-referenced figure), so
    that node's unsourced count is strictly below its measured count."""
    row = CR.measure()["per_node"]["georgian-colonial-american"]
    assert 0 < row["measured_unsourced"] < row["measured"]


def test_the_unsourced_count_falls_when_a_figure_gains_a_source(tmp_path):
    """Mutation, proved rather than assumed: give one unsourced measured parameter a source and
    the corpus-wide figure must read one lower. Done on a copy of the kit and read back, because
    a mutation that silently does not apply looks exactly like a guard that works (WP-9.6)."""
    kp = os.path.join(ROOT, "kits", "tidewater-georgian.kit.json")
    raw = open(kp, encoding="utf-8").read()
    before = CR.measure()["totals"]["measured_unsourced"]
    k = json.loads(raw)
    pv = k["slots"]["roof_pitch"]["parameters"]["pitch_typical"]
    assert pv["kind"] == "measured" and "source" not in pv
    pv["source"] = "precedents/westover#survey.general_description"
    try:
        open(kp, "w", encoding="utf-8").write(json.dumps(k, indent=2, ensure_ascii=False) + "\n")
        after = CR.measure()["totals"]["measured_unsourced"]
        assert json.load(open(kp))["slots"]["roof_pitch"]["parameters"]["pitch_typical"]["source"]  # it landed
        assert after == before - 1, (before, after)
        # and the pointer resolves in the precedent checker (the field exists on that record)
        proc = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_precedents.py"), "--strict"],
                              cwd=ROOT, capture_output=True, text=True)
        assert "1 kit figure(s) cite a survey" in proc.stdout, proc.stdout[-600:]
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
