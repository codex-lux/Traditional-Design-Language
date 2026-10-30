"""WP-17.0 — the drawability instrument and the whole-run continuity audit.

`build/drawability.py` reports, beside the one verdict `typefacts.judge` writes, the numbers the
Phase 17 investigation needed for every house and computed by hand five ways: which facts hold,
on what evidence each released fact was released, rooms over their own band, unplaced doors, and
whether each upper bearing wall stands on a ground bearing wall over its WHOLE run (ruled by Lucas,
29 Oct 2026; `typefacts.bearing_extents`, report-only until WP-17.7).
"""
import copy
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


TF = _mod("build/typefacts.py", "typefacts_dr")
DR = _mod("build/drawability.py", "drawability_t")


def _room(rid, x, y, w, h, rtype="parlor"):
    return {"id": rid, "type": rtype, "geometry": {"x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": h}}


def _house(ground, upper, W=20, H=10, bay=10):
    return {"id": "t", "footprint": {"width_ft": W, "depth_ft": H, "bay_module_ft": bay},
            "levels": [{"index": 0, "rooms": ground}, {"index": 1, "rooms": upper}]}


UPPER_FULL = [_room("c", 0, 0, 10, 10, "bedroom"), _room("d", 10, 0, 10, 10, "bedroom")]


def test_an_upper_wall_over_a_ground_wall_its_whole_run_is_held():
    plan = _house([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)], UPPER_FULL)
    ext = TF.bearing_extents(plan)
    assert ext["status"] == TF.HELD, ext
    (line,) = ext["lines"]
    assert (line["axis"], line["position_ft"], line["run_ft"], line["supported_ft"]) == ("x", 10, 10, 10)


def test_the_positional_check_passes_a_wall_half_over_open_floor_and_the_audit_does_not():
    """The false pass the audit exists for: the ground's x=10 wall runs 5 ft, the upper's 10 ft.
    Positionally both stand at x=10, so `bearing()` reads HELD; over its run the upper wall stands
    half on open floor."""
    ground = [_room("a", 0, 0, 10, 5), _room("b", 10, 0, 10, 5), _room("e", 0, 5, 20, 5)]
    plan = _house(ground, UPPER_FULL)
    assert not TF.bearing(plan)["unsupported_upper_lines"], "the premise: the positional reading passes it"
    ext = TF.bearing(plan)["extents"]
    assert ext["status"] == TF.DOWNGRADED, ext
    (line,) = [r for r in ext["lines"] if r["axis"] == "x"]
    assert line["supported_ft"] == 5 and line["fraction"] == 0.5 and not line["whole_run"]


def test_a_run_short_by_the_raster_quantum_is_still_the_whole_run():
    ground = [_room("a", 0, 0, 10, 9.95), _room("b", 10, 0, 10, 9.95), _room("e", 0, 9.95, 20, 0.05)]
    ext = TF.bearing_extents(_house(ground, UPPER_FULL))
    line = next(r for r in ext["lines"] if r["axis"] == "x")
    assert line["whole_run"], line


def test_a_ground_wall_of_staggered_pairs_covers_its_whole_run():
    """THE AUDIT OF PHASE 17 (30 Oct 2026). The ground wall at x = 10 runs unbroken from y 0 to 14,
    but it is built of three PAIRS -- a|b, then k|b for 1 ft, then k|c -- and the cover kept only
    pairs sharing more than MIN_SHARED_RUN_FT, the positional reading's test for a wall LINE. The
    short pair fell out and the house read "13 of 14 ft on a ground wall", refused, where the
    prover's own whole-run model (no ground room straddles the line under an upper wall) holds it.
    On the prover's integer grid a 1 ft stagger is exactly this case."""
    ground = [_room("a", 0, 0, 10, 9), _room("k", 0, 9, 10, 5), _room("b", 10, 0, 10, 10), _room("c", 10, 10, 10, 4)]
    upper = [_room("u1", 0, 0, 10, 14, "bedroom"), _room("u2", 10, 0, 10, 14, "bedroom")]
    plan = _house(ground, upper, H=14)
    rects = {r["id"]: (r["geometry"]["x_ft"], r["geometry"]["y_ft"], r["geometry"]["width_ft"],
                       r["geometry"]["depth_ft"]) for r in ground}
    assert ("x", 10, 9, 10) not in TF._interior_segments(rects), \
        "the premise: the line reader's own floor drops the 1 ft pair k|b"
    assert ("x", 10, 9, 10) in TF._interior_segments(rects, min_run=0.0)
    ext = TF.bearing_extents(plan)
    (line,) = [r for r in ext["lines"] if r["axis"] == "x"]
    assert (line["run_ft"], line["supported_ft"], line["whole_run"]) == (14, 14, True), line
    assert TF.bearing(plan)["status"] == TF.HELD


def test_a_ground_wall_made_only_of_short_pairs_still_covers():
    """The ground side reads every shared run whether or not its line passes the line reader's
    floor anywhere: a wall is a wall over the run it has. Driven, because no placement here builds
    a ground wall of 1 ft pairs alone -- and a cover read off the LINE map would leave this upper
    wall over nothing (the mutation that read the ground through `per_level` stayed green on the
    staggered case above, whose x = 10 line has a long pair too)."""
    ground = [_room("a", 0, 0, 10, 1), _room("b", 10, 0, 10, 1), _room("c", 0, 1, 10, 1), _room("d", 10, 1, 10, 1)]
    upper = [_room("u1", 0, 0, 10, 2, "bedroom"), _room("u2", 10, 0, 10, 2, "bedroom")]
    plan = _house(ground, upper, H=2)
    rects = {r["id"]: (r["geometry"]["x_ft"], r["geometry"]["y_ft"], r["geometry"]["width_ft"],
                       r["geometry"]["depth_ft"]) for r in ground}
    assert not [sg for sg in TF._interior_segments(rects) if sg[0] == "x"], \
        "the premise: no ground pair at x = 10 passes the line reader's floor"
    (line,) = [r for r in TF.bearing_extents(plan)["lines"] if r["axis"] == "x"]
    assert (line["run_ft"], line["supported_ft"], line["whole_run"]) == (2, 2, True), line


def test_an_upper_wall_counts_its_short_pieces_too():
    """And the other side of the same reading, which a fix to the ground alone would leave lenient:
    the upper wall at x = 10 runs 14 ft, 1 ft of it a short pair over open floor, and that foot is
    run that must stand on something. Ground: a wall under 13 ft of it, one room across the last foot."""
    ground = [_room("a", 0, 0, 10, 13), _room("b", 10, 0, 10, 13), _room("e", 0, 13, 20, 1)]
    upper = [_room("u1", 0, 0, 10, 13, "bedroom"), _room("u3", 0, 13, 10, 1, "bedroom"),
             _room("u2", 10, 0, 10, 12, "bedroom"), _room("u4", 10, 12, 10, 2, "bedroom")]
    ext = TF.bearing_extents(_house(ground, upper, H=14))
    (line,) = [r for r in ext["lines"] if r["axis"] == "x"]
    assert (line["run_ft"], line["supported_ft"]) == (14, 13) and not line["whole_run"], line


def test_the_audit_decides_since_wp_17_7():
    """Ruling 8 of 29 Oct 2026: continuity covers a wall's whole run. Report-only at WP-17.0; the
    refusal reads it now. A wall standing half over open floor is DOWNGRADED, and the detail says
    by how much."""
    ground = [_room("a", 0, 0, 10, 5), _room("b", 10, 0, 10, 5), _room("e", 0, 5, 20, 5)]
    plan = _house(ground, UPPER_FULL)
    plan["geometry_report"] = {"stacking": {"claims": 0, "kept": [], "broken": [], "unjudged": []}}
    TF.judge(plan)
    assert plan["geometry_report"]["type_facts"]["status"]["bearing"] == TF.DOWNGRADED
    b = TF.bearing(plan)
    assert "ruling 8" in b["detail"] and "5 of 10 ft" in b["detail"], b["detail"]
    whole = _house([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)], UPPER_FULL)
    assert TF.bearing(whole)["status"] == TF.HELD


# --- the refusal class ---------------------------------------------------------------------

def _refused_record(engine, refinements=(), prover_fact=None):
    # bearing holds (x=10 on both floors, whole run), so the stack is the ONLY refused fact:
    # the chamber over `a` claims to stand over `b`
    plan = _house([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)], copy.deepcopy(UPPER_FULL))
    plan["levels"][1]["rooms"][0]["stacks_over"] = "b"
    STK = _mod("build/stacking.py", "stacking_dr")
    plan["geometry_report"] = {"stacking": STK.report(plan),
                               "solver": {"engine": engine, "refinements": list(refinements),
                                          "facts": {"stack": prover_fact or {"status": "downgraded"}}}}
    return plan


PROOF_NOTE = "(proven — restored alone, no placement exists)"   # the prover's `how` for a proof


def test_a_carried_release_is_undecided_even_though_its_note_says_re_proven():
    """The first version matched "proven" and read every carried release as PROVEN, because the
    carried note reads "not individually re-proven in budget". Since the audit of Phase 17
    (finding 14) the class is read from the prover's structure, and a carried label is UNDECIDED
    whatever its note says."""
    note = ("Landing's declared stack over Stair Hall could not land together with the other "
            "declared facts (carried — off a conflict core or an undecided round, not "
            "individually re-proven in budget) — downgraded")
    fact = {"status": "downgraded", "downgraded": ["L1 c"], "proven": [], "carried": ["L1 c"]}
    a = DR.assess(_refused_record("cp-sat", [note], fact))
    assert a["refusal_class"] == {"stacks": DR.UNDECIDED}, a["refusal_class"]


def test_a_release_with_the_provers_proof_is_proven():
    """Structure alone: the label is in `proven` and nothing is carried. No note is handed over,
    so a reader that went back to the prose could not find the proof."""
    fact = {"status": "downgraded", "downgraded": ["L1 c"], "proven": ["L1 c"], "carried": []}
    assert DR.assess(_refused_record("cp-sat", [], fact))["refusal_class"] == {"stacks": DR.PROVEN}


# --- the class read from structure, never from prose (the audit of Phase 17, finding 14) -----
# `geometry_cp.facts_account` files every downgraded label `proven` or `carried`, from the set
# its per-pin notes are written from. Each record below hands the reader a note the OLD prose
# reading -- any(PROOF_PHRASE in note and kind in note.lower()) -- would decide on, so each test
# is red on that reader for its own reason.

def _bearing_refused(prover_fact, refinements=()):
    """One ground room spans 20 ft and the upper floor puts a wall at x = 10 over open floor:
    bearing is DOWNGRADED and is the only refused fact (the fire on the W gable holds)."""
    plan = _every_fact_held()
    plan["levels"][0]["rooms"] = [_room("a", 0, 0, 20, 10)]
    plan["levels"][0]["rooms"][0]["hearth"] = [{"wall": "W"}]
    for r in plan["levels"][1]["rooms"]:
        r.pop("stacks_over", None)
    STK = _mod("build/stacking.py", "stacking_dr_bear")
    plan["geometry_report"] = {"stacking": STK.report(plan),
                               "solver": {"engine": "cp-sat", "refinements": list(refinements),
                                          "facts": {"bearing": prover_fact}}}
    return plan


def _hearth_refused(prover_fact, refinements=(), name="Parlor"):
    """The fire moves to room b's W wall, ten feet inboard of the gable the massing puts its
    flues on: hearth is DOWNGRADED and is the only refused fact."""
    plan = _every_fact_held()
    plan["levels"][0]["rooms"][0].pop("hearth")
    plan["levels"][0]["rooms"][1]["hearth"] = [{"wall": "W"}]
    plan["levels"][0]["rooms"][1]["name"] = name
    STK = _mod("build/stacking.py", "stacking_dr_hearth")
    plan["geometry_report"] = {"stacking": STK.report(plan),
                               "solver": {"engine": "cp-sat", "refinements": list(refinements),
                                          "facts": {"hearth": prover_fact}}}
    return plan


def test_one_proven_and_one_carried_bearing_axis_is_undecided():
    """(a) The old reader found the proof note for the x axis and called the whole fact PROVEN,
    though the y axis was carried off a conflict core and never re-proven."""
    fact = {"status": "downgraded", "downgraded": ["element 0 x", "element 0 y"],
            "proven": ["element 0 x"], "carried": ["element 0 y"]}
    note = f"Bearing line element 0 x could not co-hold with the other declared facts {PROOF_NOTE}"
    a = DR.assess(_bearing_refused(fact, [note]))
    assert a["downgraded"] == ["bearing"], a
    assert a["refusal_class"] == {"bearing": DR.UNDECIDED}, a["refusal_class"]


def test_a_proven_hearth_release_is_proven_though_its_note_never_says_hearth():
    """(b) The prover's note for a hearth pin names the room's fire, not the word "hearth", so the
    old reader read a proven hearth release UNDECIDED."""
    fact = {"status": "downgraded", "downgraded": ["L0 b W"], "proven": ["L0 b W"], "carried": []}
    note = f"Parlor's fire on its W wall could not stand on the flue face {PROOF_NOTE}"
    assert "hearth" not in note.lower()
    a = DR.assess(_hearth_refused(fact, [note]))
    assert a["downgraded"] == ["hearth"], a
    assert a["refusal_class"] == {"hearth": DR.PROVEN}, a["refusal_class"]


def test_a_carried_hearth_in_a_room_named_hearth_room_is_undecided():
    """(c) The old reader's bare substring: a room NAMED "Hearth Room" whose note carries the proof
    phrase (for some other pin) made a carried hearth release read PROVEN."""
    fact = {"status": "downgraded", "downgraded": ["L0 b W"], "proven": [], "carried": ["L0 b W"]}
    note = f"Hearth Room's declared W wall could not hold with the other declared facts {PROOF_NOTE}"
    a = DR.assess(_hearth_refused(fact, [note], name="Hearth Room"))
    assert a["refusal_class"] == {"hearth": DR.UNDECIDED}, a["refusal_class"]


def test_a_record_from_before_the_split_is_undecided_whatever_its_prose_says():
    """(d) A prover record with no `proven`/`carried` lists carries no structure, and prose is not
    read for a proof: UNDECIDED, even beside a note the old reader would have taken."""
    fact = {"status": "downgraded", "downgraded": ["L0 b W"]}
    note = f"the hearth of Parlor on its W wall {PROOF_NOTE}"
    a = DR.assess(_hearth_refused(fact, [note]))
    assert a["refusal_class"] == {"hearth": DR.UNDECIDED}, a["refusal_class"]


def test_a_downgraded_label_filed_in_neither_list_is_no_proof():
    """EVERY downgraded label must be in `proven`. On a record the prover wrote whole, `proven`
    and `carried` partition `downgraded`, so "nothing carried" and "all proven" coincide; this
    record files one axis in neither list, and the reader must not read the other axis's proof
    as the fact's. (Written because a mutation reading ANY proven label stayed green on (a): the
    carried clause shielded it.)"""
    fact = {"status": "downgraded", "downgraded": ["element 0 x", "element 0 y"],
            "proven": ["element 0 x"], "carried": []}
    a = DR.assess(_bearing_refused(fact))
    assert a["refusal_class"] == {"bearing": DR.UNDECIDED}, a["refusal_class"]


def test_assess_carries_how_the_prover_ran():
    """Finding 13: a portfolio's verdict is a statement about the workers it had, so the row names
    them beside the status -- and a record that does not say reads None, never a guess."""
    plan = _hearth_refused({"status": "downgraded", "downgraded": ["L0 b W"]})
    plan["geometry_report"]["solver"].update(workers=4, workers_available=4, mode="portfolio")
    a = DR.assess(plan)
    assert (a["workers"], a["workers_available"], a["mode"]) == (4, 4, "portfolio"), a
    b = DR.assess(_hearth_refused({"status": "downgraded", "downgraded": ["L0 b W"]}))
    assert (b["workers"], b["workers_available"], b["mode"]) == (None, None, None), b


def test_a_fact_the_prover_held_and_the_gate_refused_is_a_mismatch():
    a = DR.assess(_refused_record("cp-sat", [], {"status": "held"}))
    assert a["refusal_class"] == {"stacks": DR.MISMATCH}


def test_the_search_is_named_as_the_search():
    assert DR.assess(_refused_record("heuristic"))["refusal_class"] == {"stacks": DR.SEARCH}


def test_assess_rejudges_and_ignores_a_stale_verdict_on_its_input():
    """Its subject is the stale `refused`, which `typefacts.judge` overwrites. Re-cut by the audit
    of Phase 17 (30 Oct 2026): this record's stacks and hearth are UNJUDGED (it declares no stack
    and states no fire), and the test asserted `drawable` on it -- the one test that pinned the
    collapse of unjudged into held (a mutation requiring every fact HELD turned exactly it red).
    It reads DRAWABLE WHERE JUDGED now, with the two facts named, and is not `drawable`."""
    plan = _house([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)], UPPER_FULL)
    plan["geometry_report"] = {"stacking": {"claims": 0, "kept": [], "broken": [], "unjudged": []},
                               "refused": {"kind": "infeasible", "facts": ["tiling"]}}
    a = DR.assess(plan)
    assert a["refused_kind"] is None, a
    assert a["facts"] == {"tiling": "held", "stacks": "unjudged", "bearing": "held",
                          "hearth": "unjudged"}, a["facts"]
    assert a["verdict"] == DR.DRAWABLE_WHERE_JUDGED and a["unjudged"] == ["stacks", "hearth"], a
    assert not a["drawable"], "an unjudged fact was counted as held (ruling 10, 30 Oct 2026)"


def _every_fact_held():
    """Two stacks that land, a fire on the W gable under a massing that puts its flues there,
    a whole-run bearing wall at x = 10 over a ground wall at x = 10, and both floors tiled."""
    ground = [_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)]
    ground[0]["hearth"] = [{"wall": "W"}]
    upper = copy.deepcopy(UPPER_FULL)
    upper[0]["stacks_over"], upper[1]["stacks_over"] = "a", "b"
    plan = _house(ground, upper)
    plan["massing"] = "four-over-four"
    STK = _mod("build/stacking.py", "stacking_dr_held")
    plan["geometry_report"] = {"stacking": STK.report(plan)}
    return plan


def test_a_house_with_every_fact_held_is_drawable_in_the_strict_sense():
    a = DR.assess(_every_fact_held())
    assert a["facts"] == {k: "held" for k in DR.FACTS}, a["facts"]
    assert a["continuity_whole_run"] == "held"
    assert a["verdict"] == DR.DRAWABLE and a["unjudged"] == [] and a["drawable"], a


def test_one_unjudged_fact_takes_a_house_from_drawable_to_drawable_where_judged():
    """The control for the case above: the same house with its fire withdrawn reads its hearth
    UNJUDGED ("states no hearth"), and that alone moves the verdict. An unjudged fact is never
    held, and it is not a refusal either -- `refused_kind` stays None."""
    plan = _every_fact_held()
    plan["levels"][0]["rooms"][0].pop("hearth")
    a = DR.assess(plan)
    assert a["facts"]["hearth"] == "unjudged" and a["refused_kind"] is None
    assert a["verdict"] == DR.DRAWABLE_WHERE_JUDGED and a["unjudged"] == ["hearth"]
    assert not a["drawable"]


def test_a_record_with_no_placement_could_not_be_evaluated_and_is_never_drawable():
    """THE AUDIT OF PHASE 17 (30 Oct 2026). A record with no placed room read every fact unjudged,
    and an unjudged fact blocked nothing, so the shipped Tidewater record AS DECLARED and an empty
    record both read DRAWABLE -- and `main --brief` counted a candidate the set's budget never
    placed in "n of N drawable"."""
    for plan in ({"id": "x", "levels": []},
                 json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())):
        a = DR.assess(plan)
        assert a["verdict"] == DR.COULD_NOT_EVALUATE and not a["drawable"], (plan["id"], a)
        assert "no placed room" in a["could_not_evaluate"]
    placed_by_nobody = _house([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)], UPPER_FULL)
    a = DR.assess(placed_by_nobody)
    assert a["verdict"] == DR.COULD_NOT_EVALUATE and "geometry_report" in a["could_not_evaluate"]


def test_main_prints_both_counts_and_the_four_add_up():
    rows = [DR.assess(_every_fact_held())]
    held_but_hearth = _every_fact_held()
    held_but_hearth["levels"][0]["rooms"][0].pop("hearth")
    rows.append(DR.assess(held_but_hearth))
    rows.append(DR.assess(_refused_record("heuristic")))
    rows.append(DR.assess({"id": "x", "levels": []}))
    line = DR.summary(rows)
    assert line.startswith("1 of 4 DRAWABLE (every fact held); 1 of 4 drawable where judged "
                           "(hearth unjudged on 1)"), line
    assert line.endswith("1 not drawable; 1 could not evaluate"), line
    assert [a["verdict"] for a in rows] == list(DR.VERDICTS)


def test_a_room_drawn_past_its_band_is_counted_and_one_declared_past_it_is_not():
    G = _mod("build/geometry.py", "geometry_dr")
    ceil, src = G.shape_band("dining-room")
    assert src == "corpus"
    r = _room("d", 0, 0, 30, 6, "dining-room")
    plan = _house([r], [], W=30)
    assert [o["room"] for o in DR.rooms_over_band(plan)] == ["d"]
    declared = copy.deepcopy(plan)
    declared["levels"][0]["rooms"][0].update(width_ft=6, length_ft=30)
    assert DR.rooms_over_band(declared) == [], "a room DECLARED past its band is the author's call"
    plan2 = copy.deepcopy(plan)
    plan2["levels"][0]["rooms"][0]["geometry"].update(width_ft=12, depth_ft=10)
    assert DR.rooms_over_band(plan2) == []


def test_a_room_declared_past_its_band_is_held_to_its_declared_ratio_and_no_further():
    """THE AUDIT OF PHASE 17 (30 Oct 2026). The declared-over exemption SKIPPED the room whatever
    was drawn: good-07's living room, declared 16 x 26 (1.62 against a ceiling of 1.6), drawn
    8 x 52 (6.5 to 1) read as no room over band -- and `no_worse` reads this count for ruling 6."""
    G = _mod("build/geometry.py", "geometry_dr2")
    ceil, src = G.shape_band("living-room")
    assert src == "corpus" and ceil < 26 / 16, "the premise: 16 x 26 is declared past the ceiling"
    r = _room("l", 0, 0, 8, 52, "living-room")
    r.update(width_ft=16, length_ft=26)
    sliver = _house([r], [], W=8, H=52)
    (row,) = DR.rooms_over_band(sliver)
    assert row["room"] == "l" and row["declared_ratio"] == 1.62 and row["ratio"] == 6.5, row
    as_declared = copy.deepcopy(sliver)
    as_declared["levels"][0]["rooms"][0]["geometry"].update(width_ft=16, depth_ft=26)
    assert DR.rooms_over_band(as_declared) == [], "drawn AT its declared ratio is the record's call"
    the_dining = _house([dict(_room("d", 0, 0, 3, 60, "dining-room"), width_ft=6, length_ft=30)], [])
    assert [o["room"] for o in DR.rooms_over_band(the_dining)] == ["d"], (
        "declared 6 x 30 and drawn 3 x 60 is past its declared 5 to 1")


def test_the_tenth_is_the_drawn_layers_and_an_exact_tenth_is_counted_by_both():
    """THE AUDIT OF PHASE 17 (30 Oct 2026). `rooms_undersize` carried its own `got < want * 0.9`
    (strictly more than a tenth) while the drawn layer convicts at a tenth OR MORE; a room drawn at
    exactly -10% was a finding on the sheet and 0 in ruling 6's comparison. One comparison now,
    `plan_check.drawn_vs_declared_pct`, held here against the drawn layer's own finding."""
    PC = _mod("build/plan_check.py", "plan_check_dr")
    plan = {"id": "t", "style": "tidewater-georgian",
            "footprint": {"width_ft": 20, "depth_ft": 10, "bay_module_ft": 10},
            "levels": [{"index": 0, "rooms": [
                dict(_room("k", 0, 0, 9, 10, "kitchen"), width_ft=10, length_ft=10),
                dict(_room("p", 9, 0, 11, 10), width_ft=11, length_ft=10)]}]}
    assert PC.drawn_vs_declared_pct(100.0, 90.0) == -10.0
    assert PC.drawn_vs_declared_pct(100.0, 90.01) is None
    found = [f["room"] for f in PC.check(plan)["findings"] if f.get("kind") == "drawn-vs-declared"]
    assert found == ["k"], found
    assert [r["room"] for r in DR.rooms_undersize(plan)] == ["k"], (
        "the drawn layer convicts an exact tenth and the never-downgrade count did not")


def test_doors_unplaced_are_counted_once_per_pair():
    plan = _house([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)], UPPER_FULL)
    plan["levels"][0]["rooms"][0]["doors"] = [{"to": "b", "unplaced": {"why": "x"}}]
    plan["levels"][0]["rooms"][1]["doors"] = [{"to": "a", "unplaced": {"why": "x"}}]
    assert DR.doors_unplaced(plan) == [("a", "b")]
