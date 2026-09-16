"""WP-11.11 — the proving engine places a second massing element.

`oq/the-proving-engine-cannot-place-a-second-massing-element` recorded the refusal and named
three things to rule. Ruled 7 September 2026, taking the question's own first reading:

  1. ONE coordinate space, each room bounded by its OWN element's box. CP-SAT integer
     variables take negative lower bounds, so a west dependency at x = -34 needs no shift and
     no second origin -- the alternative the question offered and this does not use.
  2. AN ELEMENT BOUNDARY IS NOT DOWNGRADABLE. `_RANK` is the seven-rank ladder (WP-13.3:
     wall, axis, tiling, stack, bearing, hearth, shape) and an
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

# RE-DERIVED AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026), AND THE MODEL BUILDER DID NOT MOVE.
# All four hashes changed, and the assertion below says any movement here is a defect -- so the
# discriminating measurement was run before the numbers were touched. Handed THIS BRANCH's own
# `derive_footprint` output, the MERGED `geometry_cp._build` reproduces all four of the previous
# hashes exactly (b51561f2924f1720 / 6d5a6779e293f7a2 / dc3527d9347b96e6 / 947589fc1c88444d).
# So the whole movement is the FOOTPRINT and none of it is the model: main's WP-11.2 reads the
# massing's own bay count and its parity, which takes the Tidewater from 6 bays of 10 ft to 7 of
# 9 (60.0 x 40.0 -> 63 x 38.0) and the spec Colonial from 4 to 5 (40.0 x 38.0 -> 50.0 x 31.0).
#
# AND THE FIRST CONTROL WAS NOT A CONTROL, which is worth carrying: overriding `W` and `H` in
# main's fpd dict and leaving the rest reproduced three of the four hashes and not the fourth,
# because `bay` stayed at main's 9 and the span term lays its grid lines on the BAY MODULE. A
# derived dict's keys are derived together; substitute the whole dict or none of it.
#
# RE-PINNED AT WP-13.3 (15 Sep 2026), AND THIS TIME THE MODEL DID MOVE, ON PURPOSE. All four
# hashes changed because the model states four more facts as assumption literals -- exact
# tiling per element, each declared stack by `stacking.lands`' own relation, bearing continuity
# on the bay grid within the span capacity, and each stated fire's wall on its element's face --
# and states the shape band at a hundredth rather than a tenth (`RATIO_SCALE`). The previous
# four (fc35a5f9e2048703 / 24d6bf0453c84db8 / 6ad5fa0d6ee72ffd / db49b3bc8d7c8fda) are what the
# model was before it was taught the type. The property this test guards is unchanged: the
# ONE-RECTANGLE house takes the same path as before through the element code, so any further
# movement here that WP-13.3's own tests do not account for is a defect and not a trade.
# WP-13.5 SPLIT THIS PIN IN TWO, BECAUSE THE TIDEWATER PLAN STOPPED BEING A ONE-RECTANGLE HOUSE.
# `spec-builder-colonial` is the one-rectangle control now and its two hashes are UNCHANGED
# (af0b566db578f99f / 68434bafedf92b38), re-derived on a `git archive HEAD` checkout, which is
# what proves `geometry_cp._build` did not move. The Tidewater pair is a new, separate fact: the
# model the prover builds for a THREE-element house, pinned so it cannot drift unremarked.
#
# **AND THE OBVIOUS CONTROL IS NOT ONE HERE, WHICH IS WORTH KNOWING.** `conftest.as_one_element`
# strips the six `block`/`hyphen` tags and gives a THIRD hash, b9ef896282bf7bbd -- not the old
# f499ab415b2add2e -- because WP-13.5 made three edits to that record and the tags are only one
# of them. Undoing them one at a time:
#
#     shipped                                        ed29a965f427f03f
#     tags stripped                                  b9ef896282bf7bbd
#     + the butlers<->kitchen door restored          933320674985d6b5
#     + `hallbath stacks_over powder` restored       f499ab415b2add2e   <- the old pin, exactly
#
# Every step is a fact `_build` states as an assumption literal: a door is a hard abutment, and
# WP-13.3 made each declared stack one through `stacking.lands`' own relation. So the movement is
# fully accounted for, edit by edit, and none of it is the model builder. A control that reverts
# SOME of a package's edits and is quoted as though it reverted all of them is the shape this
# repository keeps catching; it is written out here so nobody reaches for `as_one_element` as a
# model-hash control again.
ONE_RECTANGLE_SHAS = {
    ("spec-builder-colonial", False): "af0b566db578f99f",
    ("spec-builder-colonial", True): "68434bafedf92b38",
}
CONTAINER_SHAS = {
    ("tidewater-georgian-careful", False): "ed29a965f427f03f",
    ("tidewater-georgian-careful", True): "75dbc2bc875d6740",
}
MODEL_SHAS = {**ONE_RECTANGLE_SHAS, **CONTAINER_SHAS}   # tuple keys: `dict(a, **b)` refuses them


def _model_sha(pid, obj):
    plan = json.loads((ROOT / "plans" / f"{pid}.json").read_text())
    levels, prep = GEO.prep_rooms(plan)
    fpd = CP._snap_fpd(GEO.derive_footprint(plan, None, prep))
    ew = GEO.entrance_walls(plan)
    m, _r, _q = CP._build(plan, prep, fpd, ew, frozenset(), objective=obj)
    return hashlib.sha256(str(m.Proto()).encode()).hexdigest()[:16]


def _elements_on_ground(pid):
    """How many massing elements the ground level is laid into, read through `blocks_for`.

    Not the count of distinct `block` tags: a hyphen is its own element and is stated by
    `hyphen: true` rather than by a tag of its own, so on the shipped Tidewater record one tag
    and one hyphen flag become THREE elements. Asking `geometry.blocks_for` is the only reading
    that cannot disagree with the one `_build` uses."""
    plan = json.loads((ROOT / "plans" / f"{pid}.json").read_text())
    levels, prep = GEO.prep_rooms(plan)
    fpd = GEO.derive_footprint(plan, None, prep)
    return len(GEO.blocks_for(plan, fpd, prep, level=0))


def test_the_model_for_a_one_rectangle_house_is_byte_identical():
    """THE GUARANTEE, and it is stronger than a placement hash: CP-SAT under a wall-clock
    budget is not reproducible, so pinning what it FINDS would be pinning this machine. What is
    reproducible is what it is ASKED. Every guard in `_build` that reads `gx0 < ex`,
    `len(els[lvl]) > 1` or `if base:` exists to keep this one.

    On `spec-builder-colonial`, which is the corpus's one-rectangle plan since WP-13.5 moved the
    Tidewater service programme into a wing. The PREMISE is asserted, because a plan that
    quietly grew a container would turn this into a statement about a multi-element model under
    a docstring promising the opposite.
    """
    assert _elements_on_ground("spec-builder-colonial") == 1, (
        "spec-builder-colonial now states a massing container, so it is no longer this file's "
        "one-rectangle control: find one, or drive a stripped record and say so")
    for (pid, obj), want in sorted(ONE_RECTANGLE_SHAS.items()):
        assert _model_sha(pid, obj) == want, (
            f"{pid} objective={obj}: the model the prover builds for a one-rectangle house "
            f"moved. The element code must take a one-rectangle house down the same path it "
            f"always did, so any movement here is a defect and not a trade.")


def test_the_model_for_the_shipped_container_is_pinned():
    """WP-13.5. `plans/tidewater-georgian-careful.json` states three massing elements now, and
    nothing else in the tree pins what the prover is ASKED about one.

    This is not the guarantee above and must not be read as it: a movement here is only a defect
    if no package accounts for it. What it stops is the drift nobody mentions — the element
    domains, the per-element containment and coverage, the `_lands_literal` products for four
    declared stacks and the hearth's face are all in this hash, and every one of them is a fact
    the prover would otherwise stop stating in silence.
    """
    n = _elements_on_ground("tidewater-georgian-careful")
    assert n == 3, (
        f"the shipped Tidewater record states {n} massing element(s), not 3 — this pin is "
        "about the container, so re-read WP-13.5's record edit before touching the hashes")
    for (pid, obj), want in sorted(CONTAINER_SHAS.items()):
        assert _model_sha(pid, obj) == want, (
            f"{pid} objective={obj}: the model the prover builds for the shipped container "
            f"moved. Name what changed it and re-pin with the accounting; do not re-pin bare.")


def test_the_refusal_is_gone_from_the_dispatcher():
    """RE-CUT AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026). The third assertion pinned this
    branch's own sentence, `CP-SAT PLACES A SECOND MASSING ELEMENT SINCE WP-11.11`, and the
    merge kept MAIN's wording of the same paragraph -- so a guard about a refusal failed on a
    change of prose. That is the pinned-literal failure this repository has now met in four
    packages running: it fails loudly on an unrelated edit where a stale SELECTOR goes quietly
    blind, and neither is the property.

    The property is that a multi-element plan reaches CP-SAT rather than being turned away, and
    it is asserted by RUNNING one. The two source checks are kept because they are negative --
    they say the old refusal's own names are gone, which no behavioural test can say."""
    src = (ROOT / "build" / "geometry.py").read_text()
    assert "CP model places every room in a\n" not in src
    assert "_blocked" not in src, "the WP-11.9 multi-element refusal is still in solve()"
    res = CP.solve_cp(CP._multi_element_fixture(), time_limit_s=25)
    assert "error" not in res, (
        f"the dispatcher's CP engine turned a multi-element plan away: {str(res)[:200]}")
    assert "best" in res, f"a multi-element plan reached CP-SAT and got no placement: {res}"


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
    """Ruling 2, stated. `_RANK` is the seven-rank ladder; an element edge is none of them
    and is above all seven, because a room outside its own mass is not a compromise -- it is a
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
    assert CP._RANK == ("wall", "axis", "tiling", "stack", "bearing", "hearth", "shape"), (
        "the ladder's ranks moved; an element edge must not be one of them")
    assert not any("element" in k or "box" in k for k in CP._RANK)
