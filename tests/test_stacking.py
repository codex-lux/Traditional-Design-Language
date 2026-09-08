"""WP-11.6 — a stacking claim nobody could judge, and the reason it now says so.

`stacks_over` had SEVEN readers and FOUR definitions of "below", and every one of them
declined in silence. `plans/tidewater-georgian-careful.json` carried four claims of which
three were judged and no surface anywhere said which three.

Every assertion here was mutation-checked: the fix reverted, the test watched go red, and the
mutation asserted to have LANDED before the colour was believed (WP-9.6's rule -- a mutation
that silently does not apply looks exactly like a guard that works).
"""
import copy
import glob
import importlib.util
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


STK = _mod("build/stacking.py", "stacking_t")
G = _mod("build/geometry.py", "geometry_stk")
PC = _mod("build/plan_check.py", "plan_check_stk")
TIDEWATER = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())


def _two_level(upper_stacks_over=None, upper_geom=(0, 0, 10, 10), lower_geom=(0, 0, 10, 10),
               levels=None):
    """A minimal placed record. Levels state an `index`, as every shipped plan does."""
    if levels is not None:
        return {"id": "t", "levels": levels}
    lo = {"id": "lo", "type": "parlor",
          "geometry": {"x_ft": lower_geom[0], "y_ft": lower_geom[1],
                       "width_ft": lower_geom[2], "depth_ft": lower_geom[3]}}
    up = {"id": "up", "type": "bedroom",
          "geometry": {"x_ft": upper_geom[0], "y_ft": upper_geom[1],
                       "width_ft": upper_geom[2], "depth_ft": upper_geom[3]}}
    if upper_stacks_over:
        up["stacks_over"] = upper_stacks_over
    return {"id": "t", "levels": [{"index": 0, "rooms": [lo]}, {"index": 1, "rooms": [up]}]}


# --- the tally is total ---------------------------------------------------------------

def test_every_claim_lands_in_exactly_one_bucket():
    """`claims == kept + broken + unjudged`, on every plan in the tree. The bug this package
    is about is a claim that fell out of every bucket, so totality IS the guard."""
    seen = 0
    for pf in sorted(glob.glob(str(ROOT / "plans" / "*.json"))) + \
              sorted(glob.glob(str(ROOT / "plans" / "reference" / "*.json"))):
        d = json.loads(pathlib.Path(pf).read_text())
        if "levels" not in d:
            continue
        declared = sum(1 for lv in d["levels"] for r in lv["rooms"] if r.get("stacks_over"))
        rep = STK.report(d)
        assert rep["claims"] == declared, (
            f"{pf}: the record declares {declared} stacks_over claim(s) and the tally counts "
            f"{rep['claims']}")
        assert rep["claims"] == len(rep["kept"]) + len(rep["broken"]) + len(rep["unjudged"]), (
            f"{pf}: a claim fell out of every bucket, which is the defect WP-11.6 exists for")
        seen += declared
    assert seen > 0, "no plan in the tree declares a stack; this test would pass vacuously"


def test_every_unjudged_reason_is_reachable_and_from_the_closed_set():
    """Both directions. A reason the code can emit that is not in the tuple makes the closed
    set a lie; a reason in the tuple that nothing can emit is a dead branch pretending to be a
    guard. `build/construction_vocabulary.py`'s discipline, applied to a smaller table."""
    cases = {
        "the record declares no room with that id": _two_level("nobody"),
        "the room it names is on this room's own level": {
            "id": "t", "levels": [{"index": 0, "rooms": [
                {"id": "a", "type": "parlor"},
                {"id": "b", "type": "powder-room", "stacks_over": "a"}]}]},
        "the room it names is not below this room at all": {
            "id": "t", "levels": [{"index": 0, "rooms": [
                {"id": "b", "type": "powder-room", "stacks_over": "a"}]},
                {"index": 1, "rooms": [{"id": "a", "type": "parlor"}]}]},
        "the room it names is more than one level below": {
            "id": "t", "levels": [
                {"index": 0, "rooms": [{"id": "a", "type": "parlor"}]},
                {"index": 1, "rooms": [{"id": "m", "type": "bedroom"}]},
                {"index": 2, "rooms": [{"id": "b", "type": "bedroom", "stacks_over": "a"}]}]},
        "this room is not placed": {
            "id": "t", "levels": [
                {"index": 0, "rooms": [{"id": "a", "type": "parlor", "geometry": {
                    "x_ft": 0, "y_ft": 0, "width_ft": 9, "depth_ft": 9}}]},
                {"index": 1, "rooms": [{"id": "b", "type": "bedroom", "stacks_over": "a"}]}]},
        "the room it names is not placed": {
            "id": "t", "levels": [
                {"index": 0, "rooms": [{"id": "a", "type": "parlor"}]},
                {"index": 1, "rooms": [{"id": "b", "type": "bedroom", "stacks_over": "a",
                                        "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 9,
                                                     "depth_ft": 9}}]}]},
    }
    assert set(cases) == set(STK.STACK_UNJUDGED_REASONS), (
        "STACK_UNJUDGED_REASONS and this test's cases have diverged: "
        f"{set(STK.STACK_UNJUDGED_REASONS) ^ set(cases)}")
    for reason, plan in cases.items():
        _k, _b, unj = STK.judge(plan)
        assert len(unj) == 1 and unj[0]["reason"] == reason, (
            f"expected the single unjudged reason {reason!r}, got "
            f"{[u.get('reason') for u in unj]}")


def test_a_kept_stack_and_a_broken_one_are_told_apart_by_strict_overlap():
    k, b, u = STK.judge(_two_level("lo", upper_geom=(9.999, 0, 10, 10)))
    assert (len(k), len(b), len(u)) == (1, 0, 0), "a hair of overlap is a stack that lands"
    k, b, u = STK.judge(_two_level("lo", upper_geom=(10.0, 0, 10, 10)))
    assert (len(k), len(b), len(u)) == (0, 1, 0), (
        "edge-to-edge is NOT overlap -- strict positive intersection is plan_check's own test "
        "and the two must not drift apart")


# --- the shipped record ----------------------------------------------------------------

def test_the_tidewater_record_declares_what_its_parti_declares():
    """WP-11.6 authored the two claims `partis/centre-passage-double-pile.json` has always
    made. Nothing joins a plan to its parti (no plan record names one), so this is pinned by
    hand -- and that absence is itself an open question."""
    up = {r["id"]: r for lv in TIDEWATER["levels"] for r in lv["rooms"]}
    assert up["landing"].get("stacks_over") == "stair"
    assert up["upperpassage"].get("stacks_over") == "passage"
    parti = json.loads((ROOT / "partis" / "centre-passage-double-pile.json").read_text())
    pr = {r["id"]: r for r in parti["rooms"]}
    for rid in ("landing", "upperpassage", "primary", "primarybath", "hallbath"):
        assert up[rid].get("stacks_over") == pr[rid].get("stacks_over"), (
            f"{rid}: the plan and the parti it was built from disagree about the stack")


def test_the_powder_rooms_claim_is_on_the_field_that_can_hold_it():
    """A ground room naming a ground room. `stacks_over` cannot mean it -- there is no vertical
    overlap between two rooms on one floor -- and three readers dropped it in silence."""
    ground = {r["id"]: r for r in TIDEWATER["levels"][0]["rooms"]}
    assert ground["powder"].get("stacks_over") is None, (
        "the powder room's same-level claim is back on the structural field, where it is "
        "unjudgeable")
    assert ground["powder"].get("wet_stack_with") == "cellarstair"
    assert ground["cellarstair"].get("fixtures") is None, (
        "the cellar stair carries no fixtures, and that is the point: a wet stack needs a "
        "CHASE, and a stair shaft is one. Do not 're-point' this record at a bathroom.")


def test_moving_the_powder_rooms_claim_changed_no_verdict():
    """The move is a re-classification of an authored claim, not a new fact -- and that is a
    testable statement, made precisely.

    Measured on the tree as it stood BEFORE this package, putting the claim back on
    `stacks_over` left every finding on the plan byte-identical: no structural reader saw it
    and the servicing layer does not count a stair shaft as plumbing. That is why the move is
    safe. It is no longer byte-identical, and the difference is the whole package: the reverted
    record now draws one `info` finding of kind `stack-unjudged` saying the claim COULD NOT BE
    EVALUATED and naming the field that can hold it. So the assertion is the sharper one --
    **the only difference is the disclosure**, and no verdict of any weight moves either way.

    Written this way on purpose: the first draft asserted byte-identity, failed on its own
    package's new finding, and would have been "fixed" by deleting the comparison.
    """
    def findings(plan):
        solved = G.solve(json.loads(json.dumps(plan)), engine="heuristic")
        rep = PC.check(json.loads(json.dumps(solved)))
        return [(f.get("severity"), f.get("layer"), f.get("kind"), f.get("room"),
                 f.get("statement")) for f in rep["findings"]]
    old = copy.deepcopy(TIDEWATER)
    for r in old["levels"][0]["rooms"]:
        if r["id"] == "powder":
            r["stacks_over"] = r.pop("wet_stack_with")
    G._SOLVE_CACHE.clear()
    a = findings(TIDEWATER)
    G._SOLVE_CACHE.clear()
    b = findings(old)
    G._SOLVE_CACHE.clear()
    only_in_b = [f for f in b if f not in a]
    only_in_a = [f for f in a if f not in b]
    assert only_in_a == [], (
        f"moving the claim to wet_stack_with SILENCED something: {only_in_a}")
    assert [f[2] for f in only_in_b] == ["stack-unjudged"], (
        f"the field move changed more than the disclosure: {only_in_b}")
    assert only_in_b[0][0] == "info" and only_in_b[0][3] == "powder"
    assert [f for f in b if f[0] in ("fatal", "serious", "minor")] == \
           [f for f in a if f[0] in ("fatal", "serious", "minor")], (
        "a weighted verdict moved; the move was measured to change none")


def test_the_two_new_claims_are_judged_and_the_upper_passage_still_stacks():
    """The measurement the package was ruled on -- and WP-11.8 moved half of it, so read the
    second paragraph before restoring anything.

    WP-11.6 authored `landing.stacks_over = "stair"` and `upperpassage.stacks_over = "passage"`
    and measured both KEPT on the search, 3 of 5 claims landing. WP-11.8 ranked each room's own
    band above the search's own score, and the set of three changed rather than its size: the
    upper passage still stacks, `primary` over `drawing` and `primarybath` over `butlers` now
    land, and the LANDING is drawn clear of the stair. Stacking is a 40-point charge in the
    SECOND key, so a candidate that conforms better to the bands outranks it -- and the broken
    claim is reported as `stack-broken` rather than passed over, which is the guarantee WP-11.6
    actually built. What is pinned here is the judging (5 claims, none unjudged) and the
    claim the ranking did not cost; the landing is asserted BROKEN so the trade cannot reverse
    unnoticed in either direction.

    AND THE MERGE OF THE TWO PHASE 11s MOVED THE COUNT AGAIN, 3 KEPT TO 2 (8 Sep 2026), which
    is the third cause in three packages for one number -- main's WP-11.2 resized this house
    from 60.0 x 40.08 to 63 x 38.17 (the massing's own bay count and its parity), and
    `primarybath` over `butlers` no longer lands. `len(kept) == 3` was pinning an outcome the
    placer is free to change, which is the very error the test below this one was re-cut for on
    the same day. What is asserted now is the ACCOUNTING -- every claim judged into exactly one
    list, which is WP-11.6's guarantee and no engine's outcome -- plus the two named claims and
    a FLOOR under the count, so a collapse fails and an improvement does not."""
    G._SOLVE_CACHE.clear()
    solved = G.solve(json.loads(json.dumps(TIDEWATER)), engine="heuristic")
    st = solved["geometry_report"]["stacking"]
    assert st["claims"] == 5 and len(st["unjudged"]) == 0
    kept = {e["room"] for e in st["kept"]}
    broken = {e["room"] for e in st["broken"]}
    assert len(st["kept"]) + len(st["broken"]) + len(st["unjudged"]) == st["claims"], (
        f"a claim is judged into exactly one list, or it is not judged at all: {st}")
    assert len(kept) >= 2, (
        f"2 of 5 kept at the merge, 3 before it; a fall below that is the ranking losing "
        f"stacks rather than trading them: {st}")
    assert "upperpassage" in kept, f"the claim WP-11.8 did not cost is gone too: {st}"
    assert "landing" in broken, (
        "the landing stacks over the stair again -- welcome, and re-derive which key did it "
        f"before moving this line: {st}")
    rep = PC.check(json.loads(json.dumps(solved)))
    kinds = [f.get("kind") for f in rep["findings"]]
    assert "stack-broken" in kinds, "a broken claim must be reported, not passed over"


def test_the_landing_over_the_well_check_fires_on_a_landing_that_is_over_the_well():
    """`landing-off-well` runs only where a room's `stacks_over` names the stair's own room --
    nothing in the corpus said so until WP-11.6, so it had never fired in the life of the
    checker. It hangs off the KEPT list by design (`plan_check.py` says why: a landing drawn
    clear of the stair is already a `stack-broken`, and two findings for one defect is worse
    than one).

    So WHETHER IT FIRES ON A SHIPPED PLAN IS A PROPERTY OF THE PLACER, not of the rule, and
    WP-11.8's ranking stopped it firing on the Tidewater plan by drawing the landing clear.
    Pinning it there pinned an outcome the placer is free to change -- the same error this
    session corrected in `test_openings.py`'s corner test the same day. The landing is moved
    onto the stair here, by hand, so the rule is exercised whatever any engine does."""
    G._SOLVE_CACHE.clear()
    solved = G.solve(json.loads(json.dumps(TIDEWATER)), engine="heuristic")
    stair = solved.get("stair") or {}
    assert stair.get("room") and stair.get("well"), "no stair to sit a landing over"
    ground = {r["id"]: r for lv in solved["levels"] if lv.get("index", 0) == 0
              for r in lv["rooms"]}
    sg = ground[stair["room"]]["geometry"]
    for lv in solved["levels"]:
        for r in lv["rooms"]:
            if r["id"] != "landing":
                continue
            # squarely inside the stair hall and CLEAR OF THE WELL -- which is the case the
            # check exists for, and the one a room-overlap test calls clean. The strip is
            # computed rather than written down, because the well's own position is the
            # placer's: `plan_check.py`'s comment says a landing "may sit squarely inside the
            # stair hall and still miss the opening the flight arrives at", and that is what
            # this rectangle is.
            w = stair["well"]
            strip = sg["x_ft"] + sg["width_ft"] - (w["x_ft"] + w["width_ft"])
            assert strip > 1.0, (
                f"the stair hall has no strip clear of its own well ({strip:.2f} ft), so this "
                "fixture cannot state the case the check is for")
            g = r["geometry"]
            g["x_ft"] = w["x_ft"] + w["width_ft"] + 0.1
            g["y_ft"] = sg["y_ft"]
            g["width_ft"] = strip - 0.2
            g["depth_ft"] = min(g["depth_ft"], sg["depth_ft"])
    st = G.stacking_report(solved)
    assert "landing" in {e["room"] for e in st["kept"]}, st
    rep = PC.check(json.loads(json.dumps(solved)))
    kinds = [f.get("kind") for f in rep["findings"]]
    assert "landing-off-well" in kinds, (
        "the landing-over-the-well check did not run on a landing placed over the stair; it "
        "is armed by the record declaring the claim and by the claim being kept")


# --- the placer's own ceiling ------------------------------------------------------------

def test_a_level_the_placer_never_reaches_is_disclosed_and_its_rooms_named():
    """`bad-03` declares three levels; both engines are written against two. Its Gameroom came
    back with no geometry, no finding and no note -- the house drawn without a storey, in
    silence. Three surfaces say so now."""
    plan = json.loads(
        (ROOT / "plans" / "reference" / "bad-03-narrow-lot-townhome.json").read_text())
    G._SOLVE_CACHE.clear()
    solved = G.solve(json.loads(json.dumps(plan)), engine="heuristic")
    ml = solved["geometry_report"].get("multi_level")
    assert ml and ml["levels_not_placed"] == [2] and ml["rooms_not_placed"] == ["gameroom"]
    assert "COULD NOT EVALUATE" in ml["note"]
    rep = PC.check(json.loads(json.dumps(solved)))
    drawn = rep["drawn_summary"]
    assert [e["room"] for e in drawn["rooms_unplaced"]] == ["gameroom"]
    assert any(f.get("kind") == "room-not-placed" and f.get("room") == "gameroom"
               for f in rep["findings"])


def test_a_room_outside_the_footprint_is_not_reported_as_unplaced():
    """The other direction, and the reason the discriminator is `takes_a_rectangle` rather than
    "has no geometry". The Tidewater terrace is `within_footprint: false` on its OWN record, so
    having no rectangle is correct; collapsing the two states is how a missing storey comes to
    read as a design decision."""
    G._SOLVE_CACHE.clear()
    solved = G.solve(json.loads(json.dumps(TIDEWATER)), engine="heuristic")
    assert not any(r.get("geometry") for lv in solved["levels"]
                   for r in lv["rooms"] if r["id"] == "terrace"), (
        "the terrace is placed now; this test's premise is gone and it proves nothing")
    rep = PC.check(json.loads(json.dumps(solved)))
    assert rep["drawn_summary"]["rooms_unplaced"] == [], (
        "the terrace was reported as a room the placer failed to reach; its own record says it "
        "sits outside the footprint")


def test_the_placed_level_ceiling_is_read_from_the_code_that_enforces_it():
    """`PLACED_LEVEL_INDICES` is a claim about `geometry._finish` and `solve_heuristic`. A
    constant nobody holds against the code it describes is a comment."""
    src = (ROOT / "build" / "geometry.py").read_text()
    assert 'best["ground"] if idx == 0 else (best["upper"] if idx == 1 else {})' in src, (
        "geometry._finish no longer writes only levels 0 and 1; PLACED_LEVEL_INDICES in "
        "build/stacking.py is now a false statement about this code")
    assert STK.PLACED_LEVEL_INDICES == (0, 1)


# --- the two readers that had no level test ------------------------------------------------

def test_a_same_level_claim_cannot_forge_a_way_upstairs():
    """`plan_check`'s reachability reader minted an edge to the stair room for ANY room whose
    `stacks_over` named it, with no level test -- so a same-level claim would have made a way
    UP between two rooms on one floor. Inert on the shipped corpus and wrong the moment it was
    not."""
    src = (ROOT / "build" / "plan_check.py").read_text()
    i = src.index('if st and st.get("room") in ok_edges:')
    window = src[i:i + 1400]
    assert 'level_of.get(rid, 0) - level_of.get(st["room"], 0) == 1' in window, (
        "the stair reachability edge is minted without checking that the claimant is one "
        "level above the stair")


def test_the_servicing_layer_reads_the_plumbing_field():
    src = (ROOT / "build" / "plan_check.py").read_text()
    assert 'r.get("wet_stack_with") in wet' in src, (
        "the servicing layer -- the one reader whose duty wet_stack_with takes over -- does "
        "not read it")
    assert 'r.get("stacks_over") in wet' in src, (
        "it must keep reading stacks_over too: a bath over a bath is genuinely both, and "
        "dropping it would move verdicts on the shipped corpus")


# --- one spelling ---------------------------------------------------------------------------

def test_the_overlap_test_is_not_transcribed_into_the_leafs_callers():
    """`build/stacking.py` exists so the search and the critic cannot convict and acquit the
    same house. A fourth transcription of the rectangle test is the openings.required_wall_ft
    error in a new place."""
    checked = pathlib.Path(ROOT / "build" / "plan_check.py").read_text()
    assert "STACKING.judge(plan)" in checked, (
        "plan_check re-derives the stacking verdict instead of calling the leaf")
    for line in checked.splitlines():
        assert "stacks_broken\"].append" not in line, (
            "plan_check is building its own broken list again")


def test_the_placement_reasons_are_a_subset_of_the_closed_set():
    """`PLACEMENT_REASONS` decides which unjudged claims come out as the OLD kind. If a member
    of it stops being a member of `STACK_UNJUDGED_REASONS` -- a reword, a reorder -- the test
    below still passes and every affected claim silently changes kind."""
    assert set(STK.PLACEMENT_REASONS) < set(STK.STACK_UNJUDGED_REASONS)
    assert len(STK.PLACEMENT_REASONS) == 2


def test_the_two_unjudged_kinds_are_not_merged():
    """`stack-unplaced` is a PLACEMENT outcome and `build/critique.py::_is_placement` returns
    True for it; `stack-unjudged` is a RECORD error and no engine can answer it. Folding the
    new states into the existing kind would have made every one of them silently mis-classed
    as something a re-place might fix."""
    CR = _mod("build/critique.py", "critique_stk")
    # a claim whose target is not placed -> the old kind, still a placement finding
    plan = {"id": "t", "levels": [
        {"index": 0, "rooms": [{"id": "a", "type": "parlor"}]},
        {"index": 1, "rooms": [{"id": "b", "type": "bedroom", "stacks_over": "a",
                                "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 9,
                                             "depth_ft": 9}}]}]}
    _k, _b, unj = STK.judge(plan)
    assert unj and unj[0]["reason"] == "the room it names is not placed"
    assert CR._is_placement(plan, {"layer": "drawn", "kind": "stack-unplaced",
                                   "engine": "heuristic"}) is True
    assert CR._is_placement(plan, {"layer": "drawn", "kind": "stack-unjudged",
                                   "engine": "heuristic"}) is False
    assert CR._is_placement(plan, {"layer": "drawn", "kind": "room-not-placed",
                                   "engine": "heuristic"}) is False
    for kind in ("stack-unjudged", "room-not-placed"):
        move, why = CR._intended_move(plan, {"layer": "drawn", "kind": kind, "room": "b"})
        assert move is None and why and "placement outcome" not in why, (
            f"{kind} fell through to the catch-all, which says the wrong thing about it: {why}")


def test_the_leaf_imports_no_sibling():
    """It is loaded by geometry.py AND by plan_check.py, and geometry.py loads plan_check.py.
    One sibling import here closes a cycle. Same guard as build/storeys.py's."""
    src = (ROOT / "build" / "stacking.py").read_text()
    for bad in ("modcache", "_mod(", "_load(", "import geometry", "import plan_check"):
        assert bad not in src, (
            f"build/stacking.py refers to {bad!r}; it is a LEAF and must import no sibling")
