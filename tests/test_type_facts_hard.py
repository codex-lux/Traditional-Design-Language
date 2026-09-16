"""WP-13.3 -- the prover learns the type: the four facts as hard, downgradable literals.

Lucas ruled on 15 Sep 2026 that the type's facts become HARD on the prover in a stated
precedence, each downgrade named. This file holds the prover to that: the ladder's order, the
typed downgrade key, each fact's literal on the reference plan, the three states (held /
downgraded / unjudged, and unjudged never held), the relation each literal states held to the
corpus's one spelling of the rule, the objective ranking the candidates, and the budget shares.

Solves are on a SMALL two-storey fixture (one of `geometry_cp`'s own, given an upper floor, a
massing and a fire), not on the shipped plans -- a CP solve of the reference plan is forty
seconds and its status is a fact about this machine's load; every assertion here about a
shipped plan is about the MODEL it is handed, which is deterministic and free.
"""
import copy
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the CP-SAT engine needs OR-Tools")
from ortools.sat.python import cp_model  # noqa: E402

GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
CP = modcache.load("geometry_cp", os.path.join(ROOT, "build", "geometry_cp.py"))
STK = modcache.load("stacking", os.path.join(ROOT, "build", "stacking.py"))
TF = modcache.load("typefacts", os.path.join(ROOT, "build", "typefacts.py"))
HE = modcache.load("hearths", os.path.join(ROOT, "build", "hearths.py"))

TIDEWATER = os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")


def _tidewater():
    return json.load(open(TIDEWATER))


def _model(plan, downgraded=frozenset(), objective=False):
    levels, prep = GEO.prep_rooms(plan)
    fpd = CP._snap_fpd(GEO.derive_footprint(plan, None, prep))
    ew = GEO.entrance_walls(plan)
    m, rooms, reqs = CP._build(plan, prep, fpd, ew, frozenset(downgraded), objective=objective)
    return m, rooms, reqs, fpd, prep


def _two_storey_fixture():
    """`geometry_cp._feasible_fixture` with an upper floor whose rooms stack over the ground,
    a massing that puts its flues on the gable ends, and one stated fire on the parlor's
    declared W wall. Small enough to prove in seconds; every fact is stated on it."""
    p = CP._feasible_fixture()
    p["massing"] = "four-over-four"
    p["levels"][0]["rooms"][2]["hearth"] = [{"wall": "W", "width_in": 40.0}]
    p["levels"].append({"id": "upper", "index": 1, "floor_to_ceiling_ft": 9, "rooms": [
        {"id": "landing", "type": "landing", "width_ft": 8, "length_ft": 12,
         "stacks_over": "hall", "doors": [{"to": "chamber"}, {"to": "chamber2"}]},
        {"id": "chamber", "type": "bedroom", "width_ft": 13, "length_ft": 16,
         "exterior_walls": ["S", "W"], "stacks_over": "parlor", "doors": [{"to": "landing"}]},
        {"id": "chamber2", "type": "bedroom", "width_ft": 12, "length_ft": 14,
         "exterior_walls": ["N"], "stacks_over": "kitchen", "doors": [{"to": "landing"}]},
        # the bath is what lets the upper floor TILE the block: the fixture's footprint is
        # 50 x 12 ft, a bedroom's band (1.35) caps a 12 ft deep chamber at 16 ft wide, so
        # landing + two chambers reach 44 ft of the 50 and the exact-tiling literal was a
        # proven refusal (its core named `L1 element 0`) before this room existed
        {"id": "bath", "type": "bathroom", "width_ft": 8, "length_ft": 10,
         "exterior_walls": ["N", "E"], "doors": [{"to": "landing"}]},
    ]})
    return p


def _kinds(reqs):
    out = {}
    for _b, _t, k, key in reqs.lits:
        out.setdefault(k, []).append(key)
    return out


# ------------------------------------------------------------------ the ladder and the key
def test_the_rank_is_the_ruled_seven_with_the_wall_first_and_the_shape_last():
    """The 5 Sep order at both ends and the 15 Sep sequence between: authored walls, the
    parti's axis, then tiling > declared stacks > bearing continuity > hearth on its flue,
    then the room's own band. Sizes, doors, the entrance and capacity are never here."""
    assert CP._RANK == ("wall", "axis", "tiling", "stack", "bearing", "hearth", "shape")
    assert CP._RANK[0] == "wall" and CP._RANK[-1] == "shape"
    assert CP.TYPE_FACTS == ("tiling", "stack", "bearing", "hearth")
    assert CP._RANK.index("hearth") > CP._RANK.index("wall"), (
        "the hearth's wall must outrank a bare exterior_walls aspiration")
    for never in ("size", "door", "entrance", "void", "wall-soft"):
        assert never not in CP._RANK


def test_a_downgrade_key_carries_its_kind_so_an_axis_release_is_not_a_shape_release():
    """`downgraded` used to hold bare keys read by ARITY, and the axis pin and the shape pin
    share `(level, room)`: releasing the passage's axis read as releasing its proportion band.
    Typed, the two are distinct -- and the premise is asserted first."""
    plan = _tidewater()
    assert CP._dk("axis", (0, "passage")) != CP._dk("shape", (0, "passage"))
    _m, _r, reqs, _f, _p = _model(plan, downgraded={CP._dk("axis", (0, "passage"))})
    kinds = _kinds(reqs)
    assert (0, "passage") in kinds["shape"], "the passage's shape pin was released with its axis"
    assert "axis" not in kinds, "the axis pin was not released"
    _m, _r, reqs2, _f, _p = _model(plan, downgraded={CP._dk("shape", (0, "passage"))})
    kinds2 = _kinds(reqs2)
    assert (0, "passage") not in kinds2["shape"] and (0, "passage") in kinds2["axis"]


def test_every_kind_has_a_label_and_a_wall_keeps_its_old_spelling():
    assert CP._label("wall", (0, "hall", "N")) == "L0 hall N"       # parsed by hard_fact_violations
    assert CP._label("shape", (1, "chamber3")) == "L1 chamber3"
    assert CP._label("stack", (1, "landing")) == "L1 landing"
    assert CP._label("tiling", (0, 0)) == "L0 element 0"
    assert CP._label("bearing", (0, "x")) == "element 0 x"
    assert CP._label("hearth", (0, "dining", "W")) == "L0 dining W"


# ------------------------------------------------------------------ the facts, stated
def test_the_reference_plan_states_all_four_facts_by_key():
    """What the prover is ASKED on the shipped record, which is deterministic and free to
    build: two tiling literals (one per placed level), five stacks, two bearing axes, three
    hearths on the two flue walls. Nothing is unjudged on this record."""
    _m, _r, reqs, _f, _p = _model(_tidewater())
    kinds = _kinds(reqs)
    assert kinds["tiling"] == [(0, 0), (1, 0)]
    assert sorted(kinds["stack"]) == sorted([(1, "landing"), (1, "upperpassage"), (1, "primary"),
                                             (1, "primarybath"), (1, "hallbath")])
    assert sorted(kinds["bearing"]) == [(0, "x"), (0, "y")]
    assert sorted(kinds["hearth"]) == [(0, "dining", "W"), (0, "drawing", "W"), (0, "library", "E")]
    assert reqs.unjudged == []


def test_a_fact_the_model_cannot_state_is_unjudged_by_name_and_never_held():
    plan = _tidewater()
    # a fire on a wall the massing puts no flue on
    plan["levels"][0]["rooms"][3]["hearth"][0]["wall"] = "N"        # drawing, W -> N
    _m, _r, reqs, _f, _p = _model(plan)
    assert (0, "drawing", "N") not in _kinds(reqs).get("hearth", [])
    unj = [(k, key) for k, key, why in reqs.unjudged]
    assert ("hearth", (0, "drawing", "N")) in unj
    why = next(w for k, key, w in reqs.unjudged if key == (0, "drawing", "N"))
    assert "flues on E/W" in why and "not this model's fact" in why
    # no massing at all: every fire is unjudged with THAT reason
    plan = _tidewater()
    del plan["massing"]
    _m, _r, reqs, _f, _p = _model(plan)
    assert "hearth" not in _kinds(reqs)
    assert len([1 for k, _key, _w in reqs.unjudged if k == "hearth"]) == 3
    assert all("names no massing" in w for k, _key, w in reqs.unjudged if k == "hearth")
    # a stack whose target is not on the level below
    plan = _tidewater()
    plan["levels"][1]["rooms"][0]["stacks_over"] = "no-such-room"    # landing
    _m, _r, reqs, _f, _p = _model(plan)
    assert (1, "landing") not in _kinds(reqs)["stack"]
    assert ("stack", (1, "landing")) in [(k, key) for k, key, _w in reqs.unjudged]
    # the framing catalogue unreadable: no capacity, no bearing fact
    saved = CP._span_capacity
    CP._span_capacity = lambda plan: None
    try:
        _m, _r, reqs, _f, _p = _model(_tidewater())
    finally:
        CP._span_capacity = saved
    assert "bearing" not in _kinds(reqs)
    assert any(k == "bearing" and "catalogue" in w for k, _key, w in reqs.unjudged)
    # and every refusal reaches the notes the record prints
    assert any("COULD NOT BE STATED" in n for n in reqs.notes)


def test_the_capacity_is_read_the_way_span_check_decides_it():
    """`_span_capacity` mirrors `structure.span_check`: 20 ft for a timber-bay style, the
    joist table's deepest member otherwise. Held to the table rather than to a number."""
    ST = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))
    tbl = ST.load_construction()["floor"]["light_frame_joist_spans"]
    assert CP._span_capacity({"style": "tidewater-georgian"}) == 20.0
    assert "tidewater-georgian" in ST._timber_bay_applies_to()
    assert CP._span_capacity({"style": "georgian-colonial-american"}) == max(
        m["max_clear_span_ft"] for m in tbl)
    assert "georgian-colonial-american" not in ST._timber_bay_applies_to()


# ------------------------------------------------------------------ the relations, driven
def _assume_only(m, reqs, kinds_and_keys):
    """Clear every assumption and assert only the literals named -- so a constraint can be
    driven against its own literal with nothing else hard but the model's plain facts."""
    m.ClearAssumptions()
    keep = [lit for lit, _t, k, key in reqs.lits if (k, key) in kinds_and_keys]
    assert len(keep) == len(kinds_and_keys), (kinds_and_keys, _kinds(reqs))
    m.AddAssumptions(keep)


def _solve(m, seconds=10.0):
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_search_workers = 1
    s.parameters.random_seed = 7
    return s.Solve(m), s


def test_the_stack_literal_states_the_relation_stacking_lands_judges():
    """Under the literal the smaller of the two DRAWN rectangles lies at least
    `stacking.LANDS_FRACTION` inside the larger -- the rule itself, not the full-containment
    proxy (which was measured jointly infeasible on the reference plan while the rule is not).
    Driven three ways on the chamber over the parlor, with only this literal asserted: pushed
    entirely clear of the parlor it is INFEASIBLE; pushed 1 ft past the parlor's east face on
    one axis (12 x 8 of 13 x 8 inside, 92%) it is ADMITTED -- the proxy would have refused
    it, so this row is the discriminator between the two statements; and pushed 2 ft past the
    same face (11 x 8 of 13 x 8, 85%) it is refused. The fraction is asserted to be READ off
    stacking.py, and every admitted placement is re-judged by `stacking.lands` itself."""
    assert CP.STK is STK or CP.STK.LANDS_FRACTION == STK.LANDS_FRACTION
    assert CP._ceil_scaled(STK.LANDS_FRACTION) == (100, 90), "the premise: the rule is 90%"
    src = open(os.path.join(ROOT, "build", "geometry_cp.py"), encoding="utf-8").read()
    assert "STK.LANDS_FRACTION" in src and "0.9" not in src[src.index("def _lands_literal"):
                                                            src.index("def _span_capacity")]
    plan = _two_storey_fixture()
    # the fixture's block is 50 x 12 ft, so every drive keeps both rooms inside 12 ft of depth
    # AND leaves the ground's hard coverage floor a strip the porch can fill: the parlor is
    # held at 14 x 8 from y = 4 and the chamber at 13 x 8 (104 sf, the smaller of the two)
    def _sizes(ch, pa, m):
        m.Add(pa["w"] == 14), m.Add(pa["h"] == 8), m.Add(pa["y"] == 4)
        m.Add(ch["w"] == 13), m.Add(ch["h"] == 8)
    cases = (
        ("clear of the parlor",
         lambda ch, pa, m: (_sizes(ch, pa, m), m.Add(ch["x"] >= pa["x"] + pa["w"])),
         cp_model.INFEASIBLE),
        # 1 ft past the parlor's east face, inside it in y: 12 x 8 of 13 x 8 = 92%, LANDS
        ("1 ft past on one axis",
         lambda ch, pa, m: (_sizes(ch, pa, m), m.Add(ch["x"] + ch["w"] == pa["x"] + pa["w"] + 1),
                            m.Add(ch["y"] == pa["y"])),
         None),
        # 2 ft past the same face: 11 x 8 of 13 x 8 = 85%, refused (a y-protrusion on this
        # 12 ft block leaves a 2 ft strip no room's side floor can fill, so the ground's hard
        # coverage floor refuses it before the literal can -- measured, and not used)
        ("2 ft past on one axis",
         lambda ch, pa, m: (_sizes(ch, pa, m), m.Add(ch["x"] + ch["w"] == pa["x"] + pa["w"] + 2),
                            m.Add(ch["y"] == pa["y"])),
         cp_model.INFEASIBLE),
    )
    for label, drive, want in cases:
        m, rooms, reqs, _f, _p = _model(plan)
        _assume_only(m, reqs, {("stack", (1, "chamber"))})
        ch, pa = rooms[(1, "chamber")], rooms[(0, "parlor")]
        drive(ch, pa, m)
        st, s = _solve(m)
        if want is None:
            assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), label
            a = tuple(s.Value(ch[k]) for k in ("x", "y", "w", "h"))
            b = tuple(s.Value(pa[k]) for k in ("x", "y", "w", "h"))
            assert STK.lands(a, b), (label, a, b)
        else:
            assert st == want, (label, cp_model.CpSolver().StatusName(st))
            # and the discriminator is not blind: with the literal dropped the drive is admitted
            m2, rooms2, reqs2, _f, _p = _model(plan)
            _assume_only(m2, reqs2, set())
            drive(rooms2[(1, "chamber")], rooms2[(0, "parlor")], m2)
            st2, s2 = _solve(m2)
            assert st2 in (cp_model.OPTIMAL, cp_model.FEASIBLE), f"{label}: the discriminator is blind"
            a = tuple(s2.Value(rooms2[(1, "chamber")][k]) for k in ("x", "y", "w", "h"))
            b = tuple(s2.Value(rooms2[(0, "parlor")][k]) for k in ("x", "y", "w", "h"))
            assert not STK.lands(a, b), (label, a, b)


def test_the_proportion_ceiling_is_stated_to_the_hundredth():
    """The pre-existing red on main: `int(round(1.35 * 10))` is 14, so a bedroom at exactly
    1.40 to 1 (chamber3 drawn 21 x 15 on the reference plan) satisfied its own 1.35 pin.
    Driven on the chamber (a bedroom, band 1.35) at sizes the fixture's 12 ft deep block
    admits: 11 x 8 (1.375) is refused under the pin and 10 x 8 (1.25) is admitted. Under the
    old rounding 1.375 <= 1.4 passed."""
    assert CP.RATIO_SCALE == 100 and CP._ceil_scaled(1.35) == (100, 135)
    assert CP._ceil_scaled(1.35, 10) == (10, 14), "the defect's own rounding, kept for the charge only"
    band, _src = GEO.shape_band("bedroom")
    assert band == 1.35, "the premise: a bedroom's own ceiling is 1.35"
    assert 11 / 8 > band and 11 / 8 <= 1.4 and 10 / 8 <= band, "the drives straddle the two roundings"
    for w, h, want in ((11, 8, cp_model.INFEASIBLE), (10, 8, None)):
        m, rooms, reqs, _f, _p = _model(_two_storey_fixture())
        _assume_only(m, reqs, {("shape", (1, "chamber"))})
        m.Add(rooms[(1, "chamber")]["w"] == w)
        m.Add(rooms[(1, "chamber")]["h"] == h)
        st, _s = _solve(m)
        if want is None:
            assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), (w, h)
        else:
            assert st == want, (w, h)


def test_the_tiling_literal_is_exact_and_the_capacity_floor_stands_beneath_it():
    """`TILING` is 1.0 and is the fact; `COVERAGE` is 0.97 and is the floor infeasibility is
    measured against. Driven: under the tiling literal a 1 sf hole is refused; with the
    literal dropped the same hole is admitted (the floor is 3%)."""
    assert CP.TILING == 1.0 and CP.COVERAGE == 0.97
    plan = _two_storey_fixture()
    for keep, want in (({("tiling", (0, 0))}, cp_model.INFEASIBLE), (set(), None)):
        m, rooms, reqs, fpd, prep = _model(plan)
        _assume_only(m, reqs, keep)
        Wi, Hi = int(round(fpd["W"])), int(round(fpd["H"]))
        m.Add(sum(rooms[(0, r["id"])]["a"] for r in prep[0]) <= Wi * Hi - 1)
        st, _s = _solve(m)
        if want is None:
            assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        else:
            assert st == want


def test_the_bearing_literal_states_continuity_and_capacity():
    """Driven on the fixture's x axis. Capacity: with no room edge of either storey on any
    inner grid line the block is one clear span wider than the capacity, refused. Continuity:
    an upper edge on a grid line with no ground edge on it is refused. Both admitted with the
    literal dropped, and the premise (the block is wider than the capacity) asserted."""
    plan = _two_storey_fixture()
    m, rooms, reqs, fpd, prep = _model(plan)
    cap = CP._span_capacity(plan)
    bay = int(round(fpd["bay"]))
    inner = list(range(bay, int(round(fpd["W"])), bay))
    assert fpd["W"] > cap and inner, (fpd, cap)
    # capacity
    _assume_only(m, reqs, {("bearing", (0, "x"))})
    for (lvl, rid), v in rooms.items():
        for L in inner:
            m.Add(v["x"] != L)
            m.Add(v["x"] + v["w"] != L)
    st, _s = _solve(m)
    assert st == cp_model.INFEASIBLE
    m2, rooms2, reqs2, _f, _p = _model(plan)
    _assume_only(m2, reqs2, set())
    for (lvl, rid), v in rooms2.items():
        for L in inner:
            m2.Add(v["x"] != L)
            m2.Add(v["x"] + v["w"] != L)
    st2, _s = _solve(m2)
    assert st2 in (cp_model.OPTIMAL, cp_model.FEASIBLE), "the capacity discriminator is blind"
    # continuity: the landing's west edge on the first grid line, no ground edge on it
    L = inner[0]
    m3, rooms3, reqs3, _f, _p = _model(plan)
    _assume_only(m3, reqs3, {("bearing", (0, "x"))})
    m3.Add(rooms3[(1, "landing")]["x"] == L)
    for (lvl, rid), v in rooms3.items():
        if lvl == 0:
            m3.Add(v["x"] != L)
            m3.Add(v["x"] + v["w"] != L)
    st3, _s = _solve(m3)
    assert st3 == cp_model.INFEASIBLE
    m4, rooms4, reqs4, _f, _p = _model(plan)
    _assume_only(m4, reqs4, set())
    m4.Add(rooms4[(1, "landing")]["x"] == L)
    for (lvl, rid), v in rooms4.items():
        if lvl == 0:
            m4.Add(v["x"] != L)
            m4.Add(v["x"] + v["w"] != L)
    st4, _s = _solve(m4)
    assert st4 in (cp_model.OPTIMAL, cp_model.FEASIBLE), "the continuity discriminator is blind"


def test_the_hearth_literal_pins_the_fires_wall_to_the_face_and_outranks_the_wall_pin():
    plan = _two_storey_fixture()
    m, rooms, reqs, _f, _p = _model(plan)
    assert _kinds(reqs)["hearth"] == [(0, "parlor", "W")]
    _assume_only(m, reqs, {("hearth", (0, "parlor", "W"))})
    m.Add(rooms[(0, "parlor")]["x"] >= 1)
    st, _s = _solve(m)
    assert st == cp_model.INFEASIBLE
    # the same pin with the parlor's declared W wall released and the hearth held: the wall
    # is still pinned, which is what ranking the hearth above the wall means
    m2, rooms2, reqs2, _f, _p = _model(plan, downgraded={CP._dk("wall", (0, "parlor", "W")),
                                                          CP._dk("wall", (0, "parlor", "S"))})
    assert (0, "parlor", "W") not in _kinds(reqs2).get("wall", [])
    _assume_only(m2, reqs2, {("hearth", (0, "parlor", "W"))})
    m2.Add(rooms2[(0, "parlor")]["x"] >= 1)
    st2, _s = _solve(m2)
    assert st2 == cp_model.INFEASIBLE


def test_a_released_fact_keeps_its_charge_in_the_objective():
    """A downgraded stack, bearing axis or hearth is scored as the search scores it rather
    than forgotten: the objective gains terms and the notes say the charge."""
    plan = _two_storey_fixture()
    held, _r, _q, _f, _p = _model(plan, objective=True)
    n_held = len(held.Proto().objective.vars)
    for kind, key, phrase in (("stack", (1, "chamber"), f"{GEO.STACK_W:g} points"),
                              ("bearing", (0, "x"), f"{GEO.SPAN_W:g} points"),
                              ("hearth", (0, "parlor", "W"), "14 points")):
        m, _r, reqs, _f, _p = _model(plan, downgraded={CP._dk(kind, key)}, objective=True)
        assert key not in _kinds(reqs).get(kind, []), kind
        assert any(phrase in n and "downgraded" in n for n in reqs.notes), (kind, reqs.notes)
        assert len(m.Proto().objective.vars) > n_held, f"a released {kind} adds no charge"


# ------------------------------------------------------------------ a solve, end to end
@pytest.fixture(scope="module")
def solved():
    GEO._SOLVE_CACHE.clear()
    out = GEO.solve(_two_storey_fixture(), None, 80, engine="cp", time_limit_s=40)
    if "error" in out:
        pytest.skip(f"COULD NOT EVALUATE: the fixture did not prove on this machine: {out['error']}")
    return out


def test_the_fixture_proves_and_the_verifier_agrees_fact_for_fact(solved):
    """The measured end state of the fixture (1.1 s on a quiet core): the ladder released, by
    proof, the walls, then bearing, tiling, stacks and the shape band -- and the reinstatement
    pass won back the stacks (all three, as one kind), the tiling (both levels), seven of the
    eight shape pins, and left `element 0 x` REFUSED BY PROOF: a 50 ft front over a 24 ft
    capacity needs an on-grid wall on both storeys at 10, 20, 30 or 40, and the porch, hall,
    parlor and kitchen cannot make one inside their own size floors and bands. The y axis
    holds vacuously (12 ft deep, no window over 24 ft). So this fixture exercises BOTH branches
    of the bearing fact and every other fact HELD -- and the point of the test is the agreement:
    what the model calls held the leaf verifies held, what the model refused the leaf does not
    call held, and no fact is held by absence."""
    sv = solved["geometry_report"]["solver"]
    assert sv["engine"] == "cp-sat"
    facts = sv["facts"]
    assert facts["tiling"] == {"held": ["L0 element 0", "L1 element 0"], "downgraded": [],
                               "unjudged": [], "status": "held"}
    assert facts["stack"]["held"] == ["L1 chamber", "L1 chamber2", "L1 landing"]
    assert facts["stack"]["status"] == "held"
    assert facts["hearth"] == {"held": ["L0 parlor W"], "downgraded": [], "unjudged": [],
                               "status": "held"}
    assert facts["bearing"]["held"] == ["element 0 y"]
    assert facts["bearing"]["downgraded"] == ["element 0 x"] and facts["bearing"]["status"] == "downgraded"
    # the refusal is PROVEN (restored alone, no placement) and says so on the record
    notes = [n for n in sv["refinements"] if n.startswith("element 0 (main), x axis")]
    assert notes and "proven — restored alone" in notes[0], notes
    assert not any("COULD NOT BE STATED" in n for n in sv["refinements"])
    # the verifier, reading the placed record alone, agrees fact for fact
    tf = solved["geometry_report"]["type_facts"]
    assert tf["status"] == {"tiling": "held", "stacks": "held", "bearing": "downgraded",
                            "hearth": "held"}, tf["status"]
    assert tf["tiling"]["uncovered_sf"] == 0.0
    assert tf["bearing"]["halves"]["capacity"] == "downgraded"
    assert tf["hearth"]["fires"][0]["inboard_ft"] == 0.0
    kept, broken, unjudged = STK.judge(solved)
    assert (len(kept), len(broken), len(unjudged)) == (3, 0, 0)


def test_a_held_stack_survives_the_absorb_pass(solved):
    """`_absorb` runs after the solve and is outside its proof (the fifth entry of that name in
    geometry_cp.py). Measured before the guard: the landing proved 90% inside the hall came
    off the absorb pass at 83% of it. With a stack or bearing fact HELD the level's proved
    rectangles are left as proved, so the record the verifier reads IS the record the model
    proved. The proved solution is not on the record, so this asserts the consequence the
    guard exists for and the premise that makes it non-vacuous: three claims held, all land."""
    sv = solved["geometry_report"]["solver"]
    assert sv["facts"]["stack"]["held"], "premise: a stack is held on this fixture"
    by = STK.rooms_by_level(solved)
    for rid, so in (("landing", "hall"), ("chamber", "parlor"), ("chamber2", "kitchen")):
        a, b = STK._rect(by[1][rid]), STK._rect(by[0][so])
        assert STK.lands(a, b), (rid, a, b)
    src = open(os.path.join(ROOT, "build", "geometry_cp.py"), encoding="utf-8").read()
    body = src[src.index("def _rects_scored(fpd, vals):"):src.index("def _polish(fpd, hint, budget, tag):")]
    assert 'k in ("bearing", "stack") and key and _dk(k, key) not in downgraded' in body, (
        "the absorb guard no longer keys on a held bearing or stack fact")


def test_the_objective_ranks_the_candidates_and_the_search_score_is_disclosure(solved):
    sv = solved["geometry_report"]["solver"]
    cands = sv["candidates"]
    assert cands and cands[0]["label"] == "hard-only phase A" and cands[0]["objective"] is None
    with_obj = [c["objective"] for c in cands if c["objective"] is not None]
    if not with_obj:
        assert "did not run" in sv["status"] and sv["objective"] is None
        pytest.skip("COULD NOT EVALUATE the ranking: no polish produced a placement on this machine")
    assert sv["objective"] == min(with_obj)
    assert "by the CP objective" in sv["status"]
    assert all("search_score" in c for c in cands)


def test_the_ladder_is_core_guided_and_never_releases_a_kind_its_core_does_not_name(solved):
    """A conflict core is a set of literals infeasible together with the model's plain facts, so
    releasing a kind the core does not name leaves the core intact: that round proves nothing
    and costs a solve. The first seven-rank ladder released the first LIVE kind in rank order
    whatever the core said, and on the reference plan spent three rounds that way. On the
    fixture every round's note carries how many of the released kind the core named, and it is
    at least one on every round -- under the old rule round 1 would have released the tiling
    (live, rank 2) on a core that named only the bearing."""
    rounds = solved["geometry_report"]["solver"]["downgrade_rounds"]
    assert len(rounds) >= 3, rounds
    for note in rounds:
        m = re.search(r"released all (\d+) live (\w+) pin\(s\).*?the conflict core named (\d+) of them", note)
        assert m, note
        assert int(m.group(3)) >= 1, f"a kind the core did not name was released: {note[:120]}"
    released = [re.search(r"live (\w+) pin", n).group(1) for n in rounds]
    assert released[0] == "wall" and "bearing" in released and "tiling" in released, released
    # NOT asserted: that the release order is the rank order. Measured, it is not -- round 1
    # released the bearing (rank 4) on a core that named it and not the tiling (rank 2), and
    # round 2 then released the tiling on a core that did. A core-guided ladder follows the
    # cores, and a core names what the solver happened to prove, so the sequence is the rank
    # order only among the kinds each core names. The first draft of this test asserted the
    # sorted order and went red on the correct behaviour.


def test_the_budget_shares_are_named_once_and_sum_to_one():
    assert abs(GEO.BUDGET_SHARE_FEASIBILITY + GEO.BUDGET_SHARE_REINSTATE
               + GEO.BUDGET_SHARE_POLISH - 1.0) < 1e-9
    src = open(os.path.join(ROOT, "build", "geometry_cp.py"), encoding="utf-8").read()
    for name in ("BUDGET_SHARE_FEASIBILITY", "BUDGET_SHARE_REINSTATE", "BUDGET_SHARE_POLISH"):
        assert f"GEO.{name}" in src, f"solve_cp does not read {name}"
    assert "time_limit_s - (time.monotonic() - started)) * 0.5" not in src, (
        "the feasibility rounds are sized off the whole budget again rather than their share")


def test_the_stack_relation_and_the_tally_agree_on_the_solved_fixture(solved):
    """One spelling: every claim the model held lands by `stacking.lands` on the record, and
    the tally the record carries (`geometry_report.stacking`, stacking.judge's own) agrees
    with the leaf's reading of it."""
    by = STK.rooms_by_level(solved)
    for rid, so in (("landing", "hall"), ("chamber", "parlor"), ("chamber2", "kitchen")):
        assert STK.lands(STK._rect(by[1][rid]), STK._rect(by[0][so])), rid
    tally = solved["geometry_report"]["stacking"]
    assert len(tally["kept"]) == 3 and not tally["broken"] and not tally["unjudged"]
    tf = solved["geometry_report"]["type_facts"]["stacks"]
    assert [r["room"] for r in tf["claims"]] == [e["room"] for e in tally["kept"]]
    assert all(r["fraction"] >= STK.LANDS_FRACTION for r in tf["claims"]), tf["claims"]
