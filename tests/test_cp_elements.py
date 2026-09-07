"""WP-11.11 — the proving engine places a second massing element.

`oq/the-proving-engine-cannot-place-a-second-massing-element` recorded the refusal and named
three things to rule. Ruled 7 September 2026, taking the question's own first reading:

  1. ONE coordinate space, each room bounded by its OWN element's box. CP-SAT integer
     variables take negative lower bounds, so a west dependency at x = -34 needs no shift and
     no second origin -- the alternative the question offered and this does not use.
  2. AN ELEMENT BOUNDARY IS NOT DOWNGRADABLE. `_RANK` is ("wall", "axis", "shape") and an
     element edge is none of those: it is the massing, and a room drawn outside the mass the
     record states is the record and the drawing disagreeing about where the house is. It is
     stated as a plain `m.Add`, never a `reqs.lit`, so it cannot enter a conflict core and
     cannot be relaxed.
  3. AFFORDABILITY, measured rather than assumed: the three-element fixture below solves
     OPTIMAL in about half a second, and both shipped plans keep their status at the batch
     budget.

**THE GUARANTEE IS THAT THE MODEL FOR A ONE-RECTANGLE HOUSE IS BYTE-IDENTICAL** -- not the
placement, the MODEL -- because every plan in this corpus is one rectangle and a package that
teaches the prover a new concept must be invisible on all sixteen.
"""
import hashlib
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
pytest.importorskip("ortools")


def _mod(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, ROOT / "build" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CP = _mod("geometry_cp")
GEO = _mod("geometry")
EL = _mod("elements")


# --------------------------------------------------------------- the guarantee

MODEL_SHAS = {
    ("tidewater-georgian-careful", False): "b51561f2924f1720",
    ("tidewater-georgian-careful", True): "6d5a6779e293f7a2",
    ("spec-builder-colonial", False): "dc3527d9347b96e6",
    ("spec-builder-colonial", True): "947589fc1c88444d",
}


def test_the_model_for_a_one_rectangle_house_is_byte_identical():
    """THE GUARANTEE, and it is stronger than a placement hash: CP-SAT under a wall-clock
    budget is not reproducible, so pinning what it FINDS would be pinning this machine. What is
    reproducible is what it is ASKED. These four are the serialized CpModel proto for both
    shipped plans in both phases, measured on a `git archive HEAD` checkout before the package
    and on the working tree after it. Every guard in `_build` that reads `gx0 < ex`,
    `len(els[lvl]) > 1` or `if base:` exists to keep them.
    """
    for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
        plan = json.loads((ROOT / "plans" / f"{pid}.json").read_text())
        levels, prep = GEO.prep_rooms(plan)
        fpd = CP._snap_fpd(GEO.derive_footprint(plan, None, prep))
        ew = GEO.entrance_walls(plan)
        for obj in (False, True):
            m, _r, _q = CP._build(plan, prep, fpd, ew, frozenset(), objective=obj)
            got = hashlib.sha256(str(m.Proto()).encode()).hexdigest()[:16]
            assert got == MODEL_SHAS[(pid, obj)], (
                f"{pid} objective={obj}: the model the prover builds for a one-rectangle house "
                f"moved. WP-11.11 teaches it a concept no plan in this corpus exercises, so "
                f"any movement here is a defect and not a trade.")


def test_the_refusal_is_gone_from_the_dispatcher():
    src = (ROOT / "build" / "geometry.py").read_text()
    assert "CP model places every room in a\n" not in src
    assert "_blocked" not in src, "the WP-11.9 multi-element refusal is still in solve()"
    assert "CP-SAT PLACES A SECOND MASSING ELEMENT SINCE WP-11.11" in src


# --------------------------------------------------------------- what it can now do

def _solved_fixture():
    if not hasattr(_solved_fixture, "_v"):
        _solved_fixture._v = CP.solve_cp(CP._multi_element_fixture(), time_limit_s=25)
    return _solved_fixture._v


def test_three_massing_elements_are_placed_and_every_room_is_inside_its_own():
    res = _solved_fixture()
    assert "best" in res, f"the multi-element fixture did not solve: {str(res)[:200]}"
    plan = CP._multi_element_fixture()
    _levels, prep = GEO.prep_rooms(plan)
    els = GEO.blocks_for(plan, res["fpd"], prep, 0)
    assert sorted(e["role"] for e in els) == ["dependency", "hyphen", "main"]
    owner = {rid: e for e in els for rid in e["rooms"]}
    assert len(res["best"]["ground"]) == 6
    for rid, (x, y, w, h) in res["best"]["ground"].items():
        e = owner[rid]
        assert x >= e["x"] - 0.01 and y >= e["y"] - 0.01, f"{rid} starts outside its element"
        assert x + w <= e["x"] + e["W"] + 0.01, f"{rid} runs past its element's east face"
        assert y + h <= e["y"] + e["H"] + 0.01, f"{rid} runs past its element's north face"
    # and at least one of them really is outside the main block, or this proves nothing
    main = next(e for e in els if e["role"] == "main")
    assert any(x + w <= main["x"] + 0.01 or x >= main["x"] + main["W"] - 0.01
               for x, y, w, h in res["best"]["ground"].values())


def test_and_it_is_affordable_which_is_the_question_that_had_to_be_measured():
    """Item 3 of the open question: *"three elements is three coordinate spaces and an abutment
    constraint per pair. `BUDGET_BATCH_S` is 40 s. Measure before building, not after."* One
    coordinate space rather than three, and the fixture is proved in well under a second."""
    res = _solved_fixture()
    assert res["solver"]["wall_time_s"] < 10.0, res["solver"]


# --------------------------------------------------------------- the three defects found

def test_the_lower_bound_is_a_constraint_whenever_the_domain_is_wider_than_the_element():
    """THE GUARD WRITTEN FOR BYTE-IDENTITY CREATED THE DEFECT IT WAS GUARDING AGAINST. The
    first version tested `if ex:` -- "on a one-rectangle house ex is 0 and `x >= 0` is already
    the domain" -- which was true of the OLD domain and false of the new one, because `gx0` is
    the leftmost element's edge and a west dependency puts it at -34. Every MAIN-BLOCK room
    then had a domain reaching 34 ft west of the house with nothing holding it back: measured
    on a hand-tagged Tidewater, FIVE untagged rooms were placed or absorbed at a negative x, in
    no element at all. Caught by a probe that ran `elements.element_of` over every placed room
    -- not by a test, and not by reading."""
    src = (ROOT / "build" / "geometry_cp.py").read_text()
    assert "if gx0 < ex:" in src and "if gy0 < ey:" in src
    assert "\n            if ex:\n" not in src, "the `if ex:` guard is back"
    # and the behaviour: no room in the fixture is west of its own element
    res = _solved_fixture()
    plan = CP._multi_element_fixture()
    _levels, prep = GEO.prep_rooms(plan)
    owner = {rid: e for e in GEO.blocks_for(plan, res["fpd"], prep, 0) for rid in e["rooms"]}
    for rid, (x, y, w, h) in res["best"]["ground"].items():
        assert x >= owner[rid]["x"] - 0.01, f"{rid} is west of its element"


def test_the_integer_box_is_a_subset_of_the_stated_element_never_a_superset():
    """This model is integer at 1 ft and a dependency's edges are not -- `dependency_sizes`
    lands on 4.6 or -3.7. Rounding to the NEAREST foot let CP place a room half a foot outside
    the mass the record states, which is the record and the drawing disagreeing about where the
    house is: the exact defect the refusal this package removes was put there to prevent."""
    els = {0: [{"id": "d", "x": -3.7, "y": 4.6, "W": 10.4, "H": 12.9, "rooms": ["k"]}]}
    box, gx0, gy0, gx1, gy1 = CP._element_boxes(els, 40, 40)
    ex, ey, eW, eH = box[(0, "k")]
    assert (ex, ey) == (-3, 5), (ex, ey)
    assert ex >= -3.7 and ey >= 4.6
    assert ex + eW <= -3.7 + 10.4 + 1e-9 and ey + eH <= 4.6 + 12.9 + 1e-9
    # a one-rectangle house is the identity: the main block is integral (`_snap_fpd`)
    box2, *_ = CP._element_boxes({0: [{"id": "main", "x": 0, "y": 0, "W": 60.0, "H": 40.0,
                                       "rooms": ["a"]}]}, 60, 40)
    assert box2[(0, "a")] == (0, 0, 60, 40)


def test_absorb_cannot_grow_a_room_out_of_its_element():
    """THE FOURTH TIME `_absorb` HAS BEEN CAUGHT UNDOING A PROOF, and its own docstring records
    the other three. CP proved the breakfast room at y >= 4.95, the west dependency's own south
    edge; this pass grew it to y = 1.6 -- 3.35 ft of drawn floor outside the mass it belongs to,
    in a record that looks exactly like a solved plan."""
    rects = {"k": (10.0, 10.0, 5.0, 5.0)}
    bounds = {"k": (10.0, 10.0, 20.0, 20.0)}
    grown = CP._absorb(dict(rects), 100.0, 100.0, bounds=bounds)
    x, y, w, h = grown["k"]
    assert x >= 10.0 - 1e-9 and y >= 10.0 - 1e-9
    assert x + w <= 30.0 + 1e-9 and y + h <= 30.0 + 1e-9
    # WITHOUT the bounds it grows to the block, which is what it used to do everywhere
    loose = CP._absorb(dict(rects), 100.0, 100.0)
    assert loose["k"][2] > w or loose["k"][3] > h, (
        "the unbounded call must still grow further, or this test proves nothing")


def test_the_bay_modulo_is_shifted_so_a_negative_edge_stays_feasible():
    """`AddModuloEquality` truncates toward zero, so a negative dividend gives a negative
    remainder and `emod`'s [0, bay-1] domain would make a SOFT term infeasible on a west
    dependency -- a scoring preference silently deciding a plan cannot be built."""
    src = (ROOT / "build" / "geometry_cp.py").read_text()
    assert "base = (dlo // bayU) * bayU" in src
    assert "evp = ev          # every plan in the corpus; no extra variable" in src
    # the fixture is solved WITH the objective on, which is the phase that runs this term
    res = CP.solve_cp(CP._multi_element_fixture(), time_limit_s=25)
    assert "best" in res


def test_the_coverage_floor_is_per_element():
    """A floor over the union would let a dependency sit half empty while the main block
    over-filled to make up the total, which is the "two elements flattened into one" reading
    this model refuses.

    WP-11.13 RE-CUT THIS FROM A SOURCE GREP TO THE BEHAVIOUR. It asserted the literal
    `">= int(COVERAGE * _eW * _eH)"` and so broke on the fix to the defect it was guarding --
    that expression rounded the element's box a SECOND way, `int(round(...))` where containment
    used `ceil`/`floor`, and the model then demanded 97% of the larger be packed inside the
    smaller. A guard that reads a selector rather than a property goes blind on the next edit,
    and this one went red on the right edit instead, which is the same fault wearing the other
    sign: it can neither survive a rewording nor tell a fix from a regression.

    The property is that EVERY element is full of its own rooms, not that the total is.
    """
    res = _solved_fixture()
    assert "best" in res, f"the multi-element fixture did not solve: {str(res)[:200]}"
    plan = CP._multi_element_fixture()
    _levels, prep = GEO.prep_rooms(plan)
    els = GEO.blocks_for(plan, res["fpd"], prep, 0)
    placed = res["best"]["ground"]
    seen = 0
    for e in els:
        ids = [rid for rid in e["rooms"] if rid in placed]
        if not ids:
            continue
        seen += 1
        got = sum(placed[rid][2] * placed[rid][3] for rid in ids)
        box = e["W"] * e["H"]
        # the floor a non-main element is held to is stated against its rooms' OWN declared
        # area (WP-11.13), so read the guarantee the same way the model states it
        want = (box if e["role"] == "main"
                else sum(r["_area"] for r in prep[0] if r["id"] in ids))
        assert got >= CP.COVERAGE * want - 1.0, (
            f"{e['id']} ({e['role']}) is drawn {got:.0f} sf against {want:.0f} -- an element "
            "sitting half empty while another over-fills is the union floor's own defect")
    assert seen == 3, f"expected all three elements to hold rooms, judged {seen}"


def test_every_block_fact_in_the_model_reads_the_rooms_own_element():
    """Containment, the coverage floor, a declared exterior wall, a spanning room's
    through-axis, an exterior door reaching the envelope, the bay grid and the span capacity.
    Held on the source because each is one line inside a model builder that cannot be
    interrogated after the fact."""
    src = (ROOT / "build" / "geometry_cp.py").read_text()
    for needle, what in (
            ('pins = {"S": v["y"] == _ey, "N": v["y"] + v["h"] == _ey + _eH,', "declared walls"),
            ('span, ctr, ext = (v["y"], v["h"], _eH), (v["x"], v["w"], _eW), "N-S"', "the spine"),
            ('for cond in (v1["y"] == _ey, v1["y"] + v1["h"] == _ey + _eH,', "an exterior door"),
            ('for axis, lo0, extent in (("x", _ex, _ex + _eW), ("y", _ey, _ey + _eH)):', "spans"),
    ):
        assert needle in src, f"{what} is measured against the block again"


def test_an_element_boundary_is_not_downgradable():
    """Ruling 2, stated. `_RANK` is ("wall", "axis", "shape"); an element edge is none of them
    and is above all three, because a room outside its own mass is not a compromise -- it is a
    different building. It is a plain `m.Add`, so it creates no assumption literal, cannot
    appear in a conflict core and cannot be relaxed by the ladder."""
    src = (ROOT / "build" / "geometry_cp.py").read_text()
    for line in ("m.Add(x >= ex)", "m.Add(y >= ey)",
                 "m.Add(x + w <= ex + eW)", "m.Add(y + h <= ey + eH)"):
        assert f"                {line}\n" in src or f"            {line}\n" in src, line
        # a bare Add and nothing else on the line: no `.OnlyEnforceIf(lit)`, so no assumption
        # literal, so it can never enter a conflict core and can never be downgraded
        for row in src.splitlines():
            if row.strip().startswith(line):
                assert row.strip() == line, f"the element boundary is conditional: {row.strip()}"
    assert CP._RANK == ("wall", "axis", "shape"), (
        "the ladder gained a rank; an element edge must not be one of them")
