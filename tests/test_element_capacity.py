"""WP-11.13 — the element box that could not hold its own rooms.

`geometry.dependency_sizes` sized a non-main massing element's box to EXACTLY its rooms'
declared area (`H = need / W`), and `geometry_cp._element_boxes` then rounded that box INWARD
to the model's integer grid -- deliberately and rightly, so nothing CP proves sits outside the
mass the record states. Composed, the box the proving model worked in was strictly smaller than
the rooms it had to hold: measured on a hand-tagged `tidewater-georgian-careful`, coverage
**1.016 needed for the dependency and 1.067 for the hyphen**, against a floor of 0.97.

Beside it, the coverage floor computed the element's box a SECOND way -- `int(round(...))`
where containment used `ceil`/`floor` -- so the model demanded 97% of the larger box be packed
inside the smaller one. On the hyphen that is 108.6 sf into a box holding 105: infeasible by
construction, before any declared fact was read, and the conflict core duly blamed the tiling.

Both are fixed here. The corpus is BYTE-IDENTICAL across the package because 0 of its 16 plan
records carry a `block` tag -- `tests/test_elements.py` holds that -- so every assertion below
runs on a hand-tagged or synthetic record, and each says so.
"""
import glob
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, ROOT / "build" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


GEO = _mod("geometry")
EL = _mod("elements")

SERVICE = ["kitchen", "pantry", "breakfast", "powder", "cellarstair"]


def _tagged(drop_direct=True):
    """`tidewater-georgian-careful` with its service programme in a west dependency.

    THE BUTLER'S PANTRY STAYS IN THE MAIN BLOCK, and that is the record's own reading rather
    than a convenience: `rooms/butlers-pantry.json`'s `must_adjoin kitchen` carries
    `via: [back-hall, gallery-corridor]` and its note says, in as many words, that in "a
    Tidewater plantation house ... the pantry is in the block and the kitchen is in another
    building". WP-11.11 tagged it into the dependency and CP refused, correctly, naming the
    dining-room door -- a hard `must_adjoin` that carries no `via` and so cannot cross.
    """
    p = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())
    for lv in p["levels"]:
        for r in lv["rooms"]:
            if r["id"] in SERVICE:
                r["block"] = "west-dependency"
            elif r["id"] == "backhall":
                r["block"] = "west-dependency"
                r["hyphen"] = True
            if drop_direct and r["id"] in ("butlers", "kitchen"):
                other = "kitchen" if r["id"] == "butlers" else "butlers"
                r["doors"] = [d for d in r["doors"] if d.get("to") != other]
    return p


# --------------------------------------------------------------- one grid, one spelling

def test_the_grid_quantum_is_spelled_once_and_the_two_files_agree():
    """`geometry.ELEMENT_GRID_FT` is the feet-per-quantum and `geometry_cp.U` its reciprocal.
    Two files, one fact, and nothing else holds them together -- the allowance derived from one
    would be silently wrong if the other moved."""
    CP = _mod("geometry_cp")
    assert GEO.ELEMENT_GRID_FT == 1.0 / CP.U
    assert GEO.grid_allowance_ft() == 2.0 * GEO.ELEMENT_GRID_FT, (
        "two quanta, one per inward-rounded edge of the axis")


def test_the_model_and_the_disclosure_round_the_box_the_same_way():
    """`_element_boxes` reads `elements.integer_box` now. A SECOND transcription of an inward
    rounding is what this package found wrong in the coverage floor, so the guard is that the
    model's own boxes equal the leaf's, element for element, on a real multi-element fixture."""
    CP = _mod("geometry_cp")
    plan = CP._multi_element_fixture()
    _levels, prep = GEO.prep_rooms(plan)
    fpd = CP._snap_fpd(GEO.derive_footprint(plan, None, prep))
    els = GEO.blocks_for(plan, fpd, prep, 0)
    boxes = CP._element_boxes({0: els}, int(round(fpd["W"] * CP.U)),
                              int(round(fpd["H"] * CP.U)))[0]
    seen = 0
    for e in els:
        want = EL.integer_box(e["x"], e["y"], e["W"], e["H"], CP.U)
        for rid in e["rooms"]:
            if (0, rid) in boxes:
                seen += 1
                assert boxes[(0, rid)] == want, f"{e['id']}: the model rounds its own box a second way"
    assert seen >= 6, f"the fixture put only {seen} rooms in boxes; it is not exercising this"


# --------------------------------------------------------------- the box holds its rooms

@pytest.mark.parametrize("role", ["dependency", "hyphen"])
def test_a_non_main_element_still_holds_its_rooms_after_the_grid_rounds_it(role):
    """THE FIX. `H = need / W` made the stated box exactly the rooms' area and the grid then
    took up to two quanta off each axis, so the box the prover worked in was smaller than its
    contents. Measured before: dependency 1.016, hyphen 1.067, against a floor of 0.97.

    THIS IS THE WEAKER OF THE TWO GUARDS AND THE MUTATION PASS SAID SO. Deleting the depth
    term from `dependency_sizes` leaves the WIDTH half of the allowance in place, and on this
    plan the actual rounding then loses less than the worst case, so the dependency row still
    fits and only `test_the_allowance_is_derived_from_the_rounding_and_not_chosen` below goes
    red -- it asserts `(W - g)(H - g) >= need`, which is the guarantee, where this asserts one
    plan's luck. Both are kept because they fail on different mutations; do not read a green
    row here as the arithmetic being proved.
    """
    plan = _tagged()
    _levels, prep = GEO.prep_rooms(plan)
    fpd = GEO.derive_footprint(plan, None, prep)
    els = GEO.blocks_for(plan, fpd, prep, 0)
    decl = {r["id"]: (float(r["width_ft"]) * float(r["length_ft"]))
            for lv in plan["levels"] if (lv.get("index") or 0) == 0
            for r in lv["rooms"] if r.get("width_ft") and r.get("length_ft")}
    members = {}
    for e in els:
        members[e["id"]] = {rid: decl.get(rid) for rid in e["rooms"]}
    rows = EL.capacity_report(els, members, GEO.ELEMENT_GRID_FT)
    row = next(r for r in rows if r["role"] == role)
    assert row["fits_on_the_proving_grid"] is True, (
        f"{row['id']} needs {row.get('coverage_needed_on_the_proving_grid')} of the box the "
        f"prover works in -- the element is smaller than the rooms it holds")
    assert row["coverage_needed_on_the_proving_grid"] <= 1.0


def test_the_allowance_is_derived_from_the_rounding_and_not_chosen():
    """`(W - 2g)(H - 2g) >= need` solved for H, and nothing else. Driven on a synthetic
    element so the assertion is about the arithmetic rather than about one plan."""
    g = GEO.grid_allowance_ft()
    rooms = [{"id": "a", "type": "kitchen", "_area": 617.0, "block": "d",
              "exterior_walls": ["W"]}]
    # `dependency_sizes` is `flank_sizes` in the merged spelling (the other Phase 11's name for
    # the same function, dicts rather than tuples); the arithmetic this asserts is unchanged.
    row = GEO.flank_sizes({0: rooms}, 10.0)[0]
    W, H = row["W"], row["H"]
    assert (W - g) * (H - g) >= 617.0 - 0.5, (
        f"{W} x {H}: the usable box after two inward roundings per axis is smaller than the "
        "617 sf it was sized for")


# --------------------------------------------------------------- unjudged is not a fit

def test_an_element_with_no_membership_is_unjudged_and_never_a_fit():
    """THE FIRST VERSION OF `capacity_report` RETURNED `fits: true` HERE, on an empty sum --
    and it was not hypothetical: `footprint.blocks` on a placed record carries no room list, so
    every element read `rooms: 0, fits: true` on the first run of the disclosure."""
    els = [{"id": "d", "role": "dependency", "x": 0, "y": 0, "W": 10, "H": 10, "rooms": []}]
    (row,) = EL.capacity_report(els, {}, 1.0)
    assert row["fits_stated"] is None and row["fits_on_the_proving_grid"] is None
    assert row["unjudged_because"]
    (row2,) = EL.capacity_report(els, {"d": {}}, 1.0)
    assert row2["fits_stated"] is None, "an element no room stands in is unjudged, not full"


def test_a_room_stating_no_dimensions_leaves_its_element_unjudged_and_names_it():
    els = [{"id": "d", "role": "dependency", "x": 0, "y": 0, "W": 10, "H": 10,
            "rooms": ["a", "b"]}]
    (row,) = EL.capacity_report(els, {"d": {"a": 50.0, "b": None}}, 1.0)
    assert row["fits_stated"] is None and row["fits_on_the_proving_grid"] is None
    assert row["area_not_stated_for"] == ["b"]


def test_the_main_block_is_not_judged_on_the_grid_and_says_why():
    """`geometry_cp._snap_fpd` makes the footprint integral before any element is built, so a
    grid figure computed from an unsnapped record describes a box CP never uses. A first version
    reported one and duly convicted the main block of not holding its own rooms on every
    heuristic placement -- the rooms tile the block exactly, so any inward rounding loses."""
    els = [{"id": "main", "role": "main", "x": 0, "y": 0, "W": 40.0, "H": 41.9,
            "rooms": ["a"]}]
    (row,) = EL.capacity_report(els, {"main": {"a": 1676.0}}, 1.0)
    assert row["grid_box_sf"] is None and row["fits_on_the_proving_grid"] is None
    assert "snaps the footprint" in row["grid_unjudged_because"]
    assert row["fits_stated"] is True, "the stated box holds its rooms and is judged"


def test_the_stated_box_is_forgiven_its_own_depth_rounding_and_nothing_more():
    """FOUND AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026). A stated box's depth is
    `round(<quotient>, 2)`, and the MAIN BLOCK's quotient is its own rooms' area over its own
    width -- so `fits_stated` on the main block is decided by which way the second decimal
    went, not by any mass. It read True for three packages on one plan's luck and read False
    the moment main's WP-11.2 centre-bay parity changed the Tidewater's bay count: 1,675.8 sf
    stated for 1,676.0 sf of rooms, 0.012% short, and no rectangle moved.

    The tolerance is `W * 0.01 / 2`, DERIVED from that rounding. The guard is that it forgives
    exactly that and not a foot more, and that a row leaning on it SAYS SO -- a box that holds
    its rooms only inside the record's own precision must not read like one with room to
    spare."""
    els = [{"id": "main", "role": "main", "x": 0, "y": 0, "W": 45.0, "H": 37.24,
            "rooms": ["a"]}]
    tol = 45.0 * EL.DEPTH_ROUNDING_FT / 2.0          # 0.225 sf on a 45 ft front
    stated = 45.0 * 37.24
    (row,) = EL.capacity_report(els, {"main": {"a": stated + tol * 0.5}}, 1.0)
    assert row["fits_stated"] is True
    assert row["fits_stated_only_within_the_depth_rounding"] == round(tol, 4), (
        "a box that holds its rooms only inside its own rounding must say so on the row")
    (over,) = EL.capacity_report(els, {"main": {"a": stated + tol * 2.0}}, 1.0)
    assert over["fits_stated"] is False, (
        "one whole quantum of depth over is a real overrun and the tolerance may not eat it")
    assert "fits_stated_only_within_the_depth_rounding" not in over
    (clear,) = EL.capacity_report(els, {"main": {"a": stated - 100.0}}, 1.0)
    assert clear["fits_stated"] is True
    assert "fits_stated_only_within_the_depth_rounding" not in clear, (
        "a box with real slack does not carry the rounding note")


def test_an_element_too_small_for_its_rooms_is_detected_and_named():
    """The detector has to bite, or the disclosure is decoration. No record in this corpus can
    reach it now, so it is proved on a synthetic element rather than deleted."""
    els = [{"id": "d", "role": "dependency", "x": 0.0, "y": 0.5, "W": 10.0, "H": 10.0,
            "rooms": ["a"]}]
    (row,) = EL.capacity_report(els, {"d": {"a": 99.0}}, 1.0)
    assert row["fits_stated"] is True, "99 sf fits the stated 100 sf box"
    assert row["fits_on_the_proving_grid"] is False, (
        "a half-foot origin costs a whole quantum of depth, so the box the prover works in is "
        "90 sf and cannot hold 99")


# --------------------------------------------------------------- on the record

def test_the_disclosure_carries_a_capacity_row_for_every_element():
    plan = _tagged()
    GEO._SOLVE_CACHE.clear()
    sol = GEO.solve(plan, engine="heuristic")
    me = (sol.get("geometry_report") or {}).get("multi_element") or {}
    rows = me.get("element_capacity")
    assert rows and len(rows) == 3, f"three elements, {rows and len(rows)} capacity rows"
    assert {r["role"] for r in rows} == {"main", "dependency", "hyphen"}
    for r in rows:
        assert "stated_box_sf" in r and "rooms_declared_sf" in r
    assert not me.get("elements_too_small_for_their_own_rooms"), (
        "the hand-tagged Tidewater's elements all hold their own rooms since WP-11.13")


def test_the_shipped_corpus_cannot_reach_any_of_this():
    """Why the package is inert: 0 of 16 records carry a `block` tag, so `dependency_sizes`
    returns [] and every element rule above is unreachable from the corpus. That is what makes
    `tests/test_elements.py`'s two hashes a real guarantee rather than a hopeful one."""
    n = tagged = 0
    for pf in sorted(glob.glob(str(ROOT / "plans" / "*.json"))) + \
            sorted(glob.glob(str(ROOT / "plans" / "reference" / "*.json"))):
        d = json.loads(pathlib.Path(pf).read_text())
        if "levels" not in d:
            continue
        n += 1
        if any(r.get("block") for lv in d["levels"] for r in lv.get("rooms") or []):
            tagged += 1
    assert n == 16 and tagged == 0


# --------------------------------------------------------------- what it buys

def test_the_tagged_tidewater_is_provable_now():
    """THE HEADLINE, and it is why the box arithmetic mattered rather than being tidiness.
    Before WP-11.13 every tagging of this record came back INFEASIBLE with an
    all-requirements-dropped core -- "the rooms cannot tile any footprint this parti and lot
    allow" -- because the boxes could not hold their contents whatever the declared facts said.
    The service programme in a real dependency joined by a hyphen is Part I.A item 4 of the
    Phase 11 diagnosis, and it is proved.

    COULD NOT EVALUATE without ortools, which is a named unjudged state and never a pass.
    """
    pytest.importorskip("ortools", reason="CP-SAT absent: this cannot be evaluated here")
    GEO._SOLVE_CACHE.clear()
    sol = GEO.solve(_tagged(), engine="cp")
    rep = sol.get("geometry_report") or {}
    status = ((rep.get("solver") or {}).get("engine") or "")
    assert status.startswith("cp-sat"), (
        f"the tagged record fell back to {status!r}; conflicts: "
        f"{[c for c in ((rep.get('infeasible') or {}).get('conflicts') or [])][:3]}")
