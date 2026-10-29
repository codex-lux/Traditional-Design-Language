"""WP-17.0 — the drawability instrument and the whole-run continuity audit.

`build/drawability.py` reports, beside the one verdict `typefacts.judge` writes, the numbers the
Phase 17 investigation needed for every house and computed by hand five ways: which facts hold,
on what evidence each released fact was released, rooms over their own band, unplaced doors, and
whether each upper bearing wall stands on a ground bearing wall over its WHOLE run (ruled by Lucas,
29 Oct 2026; `typefacts.bearing_extents`, report-only until WP-17.7).
"""
import copy
import importlib.util
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


def test_a_carried_release_is_undecided_even_though_its_note_says_re_proven():
    """The first version matched "proven" and read every carried release as PROVEN, because the
    carried note reads "not individually re-proven in budget"."""
    note = ("Landing's declared stack over Stair Hall could not land together with the other "
            "declared facts (carried — off a conflict core or an undecided round, not "
            "individually re-proven in budget) — downgraded")
    a = DR.assess(_refused_record("cp-sat", [note]))
    assert a["refusal_class"] == {"stacks": DR.UNDECIDED}, a["refusal_class"]


def test_a_release_with_the_provers_proof_is_proven():
    note = ("Landing's declared stack over Stair Hall could not land together with the other "
            "declared facts (proven — restored alone, no placement exists) — downgraded")
    assert DR.assess(_refused_record("cp-sat", [note]))["refusal_class"] == {"stacks": DR.PROVEN}


def test_a_fact_the_prover_held_and_the_gate_refused_is_a_mismatch():
    a = DR.assess(_refused_record("cp-sat", [], {"status": "held"}))
    assert a["refusal_class"] == {"stacks": DR.MISMATCH}


def test_the_search_is_named_as_the_search():
    assert DR.assess(_refused_record("heuristic"))["refusal_class"] == {"stacks": DR.SEARCH}


def test_assess_rejudges_and_ignores_a_stale_verdict_on_its_input():
    plan = _house([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)], UPPER_FULL)
    plan["geometry_report"] = {"stacking": {"claims": 0, "kept": [], "broken": [], "unjudged": []},
                               "refused": {"kind": "infeasible", "facts": ["tiling"]}}
    a = DR.assess(plan)
    assert a["refused_kind"] is None and a["drawable"], a


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


def test_doors_unplaced_are_counted_once_per_pair():
    plan = _house([_room("a", 0, 0, 10, 10), _room("b", 10, 0, 10, 10)], UPPER_FULL)
    plan["levels"][0]["rooms"][0]["doors"] = [{"to": "b", "unplaced": {"why": "x"}}]
    plan["levels"][0]["rooms"][1]["doors"] = [{"to": "a", "unplaced": {"why": "x"}}]
    assert DR.doors_unplaced(plan) == [("a", "b")]
