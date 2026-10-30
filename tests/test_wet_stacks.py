"""WP-17.1 — a bath over a wet room is a plumbing claim, and it is still judged.

Lucas ruled on 29 Oct 2026 (ruling 5) that the BATH-OVER-WET-ROOM claims the partis filed as
`stacks_over` (STRUCTURAL: the smaller room at least 90% inside the larger, one of the type's facts,
refuses a drawing) are `wet_stack_with` (SERVICING: the two rooms share a chase, WP-11.6's split).
Measured first: on the composed centre-passage-double-pile the bath-over-butler's-pantry claim was
the one claim that made the house unplaceable with its rooms in band.

WHAT WAS EXECUTED WAS WIDER THAN WHAT WAS RULED, AND TWO CLAIMS WENT BACK (corrected 30 Oct 2026).
WP-17.1 moved every claim whose CLAIMANT is a bath -- 17 in 13 partis -- and this file held that
class and called it the ruled one. The audit of Phase 17 (findings 33 and 43) found two targets
outside "wet room": octagon-radial's `hallbath` over a dry `pantry` (plumbing 'none'), and
connected-farmstead's `hallbath` over a `back-hall` (circulation; plumbing 'light', wet by one of the
tree's two spellings and not the other). Lucas ruled on 30 Oct 2026 (R9) that both go BACK to
`stacks_over`. The class is 15 claims in 12 partis now, and it is held to the TARGET's wetness, not
the claimant's type alone.

Moving a claim out of a refusing fact must not silence it. These tests hold three things:
  * the class is fully moved, and nothing else was (a chamber over a parlour stays structural);
  * the composer carries the servicing claim onto the plan record, as it carries `stacks_over`;
  * the placed house is judged for it (`stacking.wet_judge`), reported as a minor finding by the
    drawn layer, and never counted by `typefacts`, so it refuses nothing.
"""
import copy
import glob
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


STK = _mod("build/stacking.py", "stacking_wet")
TF = _mod("build/typefacts.py", "typefacts_wet")

BATH_TYPES = {"primary-bathroom", "bathroom"}


def _partis():
    return [json.loads(pathlib.Path(f).read_text()) for f in sorted(glob.glob(str(ROOT / "partis" / "*.json")))]


def _rect(x, y, w, h):
    return {"x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": h}


# --- the class is moved, and only the class -------------------------------------------------

# The room types `plan_check`'s servicing layer reads as plumbed: `rt["servicing"].get("plumbing")
# in ("light", "heavy")` (its "plumbed room type with no fixtures" check). It is a predicate, not a
# function anything exposes, so it is spelled here with its source named; the workbench's
# `overlayRules.isWet` reads heavy-or-sanitary and the two disagree on the back hall and the
# butler's pantry, which is pre-existing and not this file's subject.
PLUMBED = ("light", "heavy")

# R9 (Lucas, 30 Oct 2026): the two claims WP-17.1 re-filed past ruling 5's text, returned to the
# structural field. Named, because connected-farmstead's back hall is plumbed by the predicate above
# and is structural anyway -- by ruling, not by the predicate.
REVERTED_BY_R9 = {("octagon-radial", "hallbath"): "pantry",
                  ("connected-farmstead", "hallbath"): "backhall"}


def _plumbing(parti, rid):
    rtype = next(r["type"] for r in parti["rooms"] if r["id"] == rid)
    rec = json.loads((ROOT / "rooms" / f"{rtype}.json").read_text())
    return (rec.get("servicing") or {}).get("plumbing")


def test_no_parti_files_a_bath_over_a_wet_room_as_a_structural_stack():
    left = [(p["id"], r["id"]) for p in _partis() for r in p["rooms"]
            if r.get("stacks_over") and r["type"] in BATH_TYPES
            and _plumbing(p, r["stacks_over"]) in PLUMBED
            and (p["id"], r["id"]) not in REVERTED_BY_R9]
    assert not left, f"a bath over a wet room still claims a STRUCTURAL stack (ruling 5): {left}"


def test_the_two_claims_reverted_by_r9_are_structural_and_say_so():
    """R9 (Lucas, 30 Oct 2026). Each note says the claim was REVERTED and why, and never that ruling
    5 ruled it -- the note WP-17.1 wrote said "ruled by Lucas, 29 Oct 2026" of a claim the ruling's
    text did not reach."""
    partis = {p["id"]: p for p in _partis()}
    for (pid, rid), target in REVERTED_BY_R9.items():
        r = next(r for r in partis[pid]["rooms"] if r["id"] == rid)
        assert r.get("stacks_over") == target and not r.get("wet_stack_with"), (pid, rid, r)
        note = r.get("note") or ""
        assert "REVERTED" in note and "30 Oct 2026" in note, (pid, rid, note)
        assert "(ruled by Lucas, 29 Oct 2026)" not in note, (pid, rid, note)


def test_the_moved_class_is_fifteen_claims_in_twelve_partis_and_every_target_is_wet():
    """The executed class was "the claimant is a bath", 17 in 13, and this test held only the
    claimant (finding 33). It holds the TARGET to plumbing now -- a `wet_stack_with` whose room below
    is dry is the wider class ruling 5 did not rule -- and the count to what is left after R9."""
    moved = [(p["id"], r["id"]) for p in _partis() for r in p["rooms"] if r.get("wet_stack_with")]
    assert len(moved) == 15 and len({pid for pid, _ in moved}) == 12, moved
    for p in _partis():
        for r in p["rooms"]:
            if r.get("wet_stack_with"):
                assert r["type"] in BATH_TYPES, (p["id"], r["id"], r["type"])
                assert _plumbing(p, r["wet_stack_with"]) in PLUMBED, (
                    f"{p['id']}/{r['id']}: a wet stack over a DRY room is outside ruling 5's class")
                assert "WP-17.1" in (r.get("note") or ""), (
                    f"{p['id']}/{r['id']}: a reclassified claim carries no dated note saying so")


def test_the_structural_claims_that_are_not_baths_stay_structural():
    kinds = {(p["id"], r["id"]) for p in _partis() for r in p["rooms"] if r.get("stacks_over")}
    assert ("centre-passage-double-pile", "primary") in kinds
    assert ("centre-passage-double-pile", "landing") in kinds
    assert ("side-hall-townhouse", "primary") in kinds
    # 49 parti claims before WP-17.1: 32 structural stayed and 17 moved; R9 (30 Oct 2026) returned
    # two, so 34 structural and 15 servicing. (`check_stacking` prints 40 because it also counts the
    # plan records' own six.)
    assert len(kinds) == 34, len(kinds)


# --- the one reader on a placed house ---------------------------------------------------------

def _wet_plan(bath_geom, target_geom, same_level=False):
    tgt = {"id": "pantry", "type": "butlers-pantry", "fixtures": ["sink"],
           "geometry": _rect(*target_geom)}
    bath = {"id": "bath", "type": "primary-bathroom", "wet_stack_with": "pantry",
            "fixtures": ["wc"], "geometry": _rect(*bath_geom)}
    if same_level:
        return {"id": "t", "levels": [{"index": 0, "rooms": [tgt, bath]}]}
    return {"id": "t", "levels": [{"index": 0, "rooms": [tgt]}, {"index": 1, "rooms": [bath]}]}


def test_across_levels_any_overlap_shares_a_chase_and_none_does_not():
    k, b, u = STK.wet_judge(_wet_plan((5, 5, 8, 10), (0, 0, 7, 12)))
    assert (len(k), len(b), len(u)) == (1, 0, 0), "a 2 x 7 ft overlap leaves a chase room to rise"
    k, b, u = STK.wet_judge(_wet_plan((20, 0, 8, 10), (0, 0, 7, 12)))
    assert (len(k), len(b), len(u)) == (0, 1, 0), "plans 13 ft apart share no chase"


def test_across_levels_a_corner_sliver_is_not_a_chase():
    """THE AUDIT OF PHASE 17 (30 Oct 2026). Across levels the test was `overlaps`, strict positive
    area with no minimum, so a 0.1 x 0.1 ft corner -- 0.01 sf -- read kept. The overlap must exceed
    CHASE_MIN_RUN_FT on BOTH axes now, the same-level branch's own figure. A strip 7 ft long and
    0.5 ft deep is no chase either: a chase needs a room's width of floor to rise through."""
    k, b, _ = STK.wet_judge(_wet_plan((6.9, 11.9, 5, 5), (0, 0, 7, 12)))
    assert (len(k), len(b)) == (0, 1), "a 0.1 x 0.1 ft corner across levels is not a shared chase"
    k, b, _ = STK.wet_judge(_wet_plan((0, 11.5, 7, 5), (0, 0, 7, 12)))
    assert (len(k), len(b)) == (0, 1), "a 7 x 0.5 ft strip is not a shared chase"
    assert STK.shares_chase((0, 0, 7, 12), (5, 5, 8, 10), False), "the 2 x 7 ft overlap stays kept"


def test_on_one_level_a_shared_wall_shares_a_chase_and_a_corner_does_not():
    k, b, _ = STK.wet_judge(_wet_plan((7, 2, 8, 6), (0, 0, 7, 12), same_level=True))
    assert (len(k), len(b)) == (1, 0), "a 6 ft common wall"
    k, b, _ = STK.wet_judge(_wet_plan((7, 12, 8, 6), (0, 0, 7, 12), same_level=True))
    assert (len(k), len(b)) == (0, 1), "touching at a corner is not a shared wall"


def test_an_unplaced_or_missing_room_is_unjudged_by_name():
    plan = _wet_plan((5, 5, 8, 10), (0, 0, 7, 12))
    plan["levels"][1]["rooms"][0].pop("geometry")
    assert STK.wet_judge(plan)[2][0]["reason"] == STK.THIS_ROOM_UNPLACED
    plan = _wet_plan((5, 5, 8, 10), (0, 0, 7, 12))
    plan["levels"][0]["rooms"][0].pop("geometry")
    assert STK.wet_judge(plan)[2][0]["reason"] == STK.TARGET_UNPLACED
    plan = _wet_plan((5, 5, 8, 10), (0, 0, 7, 12))
    plan["levels"][1]["rooms"][0]["wet_stack_with"] = "nobody"
    assert STK.wet_judge(plan)[2][0]["reason"] == STK.NO_SUCH_ROOM


def test_the_tally_carries_wet_stacks_beside_the_structural_ones_and_not_among_them():
    rep = STK.report(_wet_plan((20, 0, 8, 10), (0, 0, 7, 12)))
    assert rep["claims"] == 0 and not rep["broken"], "a wet stack entered the STRUCTURAL tally"
    assert rep["wet"]["claims"] == 1 and len(rep["wet"]["broken"]) == 1
    assert "wet" not in STK.report({"id": "t", "levels": [{"index": 0, "rooms": []}]}), (
        "a record declaring no wet stack carries no wet block")


def test_a_broken_wet_stack_refuses_nothing():
    """The ruling's point: servicing is not one of the type's facts."""
    plan = _wet_plan((20, 0, 8, 10), (0, 0, 7, 12))
    plan["geometry_report"] = {"stacking": STK.report(plan)}
    st = TF.stacks(plan)
    assert st["status"] != TF.DOWNGRADED, st
    assert not st["claims"], "typefacts counted a servicing claim as a structural one"


# --- the composer carries it, and the drawn layer reports it ----------------------------------

def test_the_composer_carries_the_servicing_claim_onto_the_plan_record():
    CO = _mod("build/compose.py", "compose_wet")
    brief = {"id": "t", "style": "tidewater-georgian", "target_area_sf": 3200, "bedrooms": 4,
             "bathrooms": 3.5}
    plan, _log, _p = CO.instantiate("centre-passage-double-pile", brief)
    rooms = {r["id"]: r for lv in plan["levels"] for r in lv["rooms"]}
    assert rooms["primarybath"].get("wet_stack_with") == "butlers", (
        "instantiate dropped the wet_stack_with claim on the way to the plan record")
    assert not rooms["primarybath"].get("stacks_over")


def test_the_drawn_layer_reports_a_wet_stack_that_shares_no_chase():
    PC = _mod("build/plan_check.py", "plan_check_wet")
    G = _mod("build/geometry.py", "geometry_wet")
    CO = _mod("build/compose.py", "compose_wet2")
    brief = {"id": "t", "style": "tidewater-georgian", "target_area_sf": 3200, "bedrooms": 4}
    plan, _log, _p = CO.instantiate("foursquare-quadrant", brief)
    placed = G.solve(copy.deepcopy(plan), CO.PARTIS["foursquare-quadrant"], engine="heuristic")
    assert "error" not in placed, placed.get("error")
    rooms = {r["id"]: r for lv in placed["levels"] for r in lv["rooms"]}
    assert rooms["hallbath"].get("wet_stack_with") == "kitchen"
    # drive the broken branch: the bath moved clear of the kitchen's plan
    kg = rooms["kitchen"]["geometry"]
    hb = rooms["hallbath"]["geometry"]
    hb["x_ft"] = kg["x_ft"] + kg["width_ft"] + 50.0
    res = PC.check(placed)
    kinds = [f.get("kind") for f in res["findings"]]
    assert "wet-stack-shares-no-chase" in kinds, sorted(set(k for k in kinds if k))
    f = next(f for f in res["findings"] if f.get("kind") == "wet-stack-shares-no-chase")
    assert f["severity"] == "minor" and f.get("room") == "hallbath"


def test_the_critique_reads_a_wet_stack_finding_with_its_own_reason():
    """THE AUDIT OF PHASE 17 (30 Oct 2026). `critique._intended_move`'s drawn branch had no case for
    `wet-stack-shares-no-chase` and handed it the fall-through about a room's SIZE -- a true sentence
    about a different rule (WP-11.9's aspect findings, met again)."""
    CR = _mod("build/critique.py", "critique_wet")
    f = {"id": "drawn:hallbath#wet", "layer": "drawn", "kind": "wet-stack-shares-no-chase",
         "severity": "minor", "engine": "heuristic", "room": "hallbath",
         "statement": "Bath and Kitchen share no chase"}
    plan = {"id": "t", "levels": [{"index": 1, "rooms": [{"id": "hallbath", "type": "bathroom"}]}]}
    move, why = CR._intended_move(plan, f)
    assert move is None and "wet_stack_with" in why and "servicing" in why, why
    assert "drawn-against-declared size" not in why, why
    got, _cne = CR.classify(plan, {"findings": [f]})
    (issue,) = [i for c in CR.CLASSES for i in got[c] if i["id"] == f["id"]]
    assert issue["class"] == "architect" and "servicing" in issue["why"], issue


def test_check_plans_holds_a_plan_to_its_partis_wet_stack():
    """`build/check_plans.py` joins a hand-authored plan to the parti it names. The careful record
    names centre-passage-double-pile, whose primary bath claims a WET stack with the butler's pantry
    since ruling 5; the SHIPPED record still files it as `stacks_over` on purpose (re-filing it moves
    the shipped placement, which is its own package), and that is REPORTED under its own ceiling of
    one. A plan that drops the claim is a topology finding; one that re-files it is clean."""
    import os
    import sys
    sys.path.insert(0, str(ROOT / "build"))
    import modcache
    CPL = modcache.load("check_plans", os.path.join(str(ROOT), "build", "check_plans.py"))
    plan = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())
    parti = CPL.load_parti("centre-passage-double-pile")

    def kinds(p):
        return [f["kind"] for f in CPL.check_plan(p, parti) if f["kind"].startswith("wet-stack")]
    assert kinds(plan) == ["wet-stack-filed-as-structural"]
    assert "wet-stack-filed-as-structural" in CPL.REPORTED
    assert CPL.WET_FILED_AS_STRUCTURAL == {("plans/tidewater-georgian-careful.json", "primarybath")}

    def edit(fn):
        p = json.loads(json.dumps(plan))
        for lv in p["levels"]:
            for r in lv["rooms"]:
                if r["id"] == "primarybath":
                    fn(r)
        return p
    refiled = edit(lambda r: r.update(wet_stack_with=r.pop("stacks_over")))
    assert kinds(refiled) == []
    dropped = edit(lambda r: r.pop("stacks_over"))
    assert kinds(dropped) == ["wet-stack-with"] and "wet-stack-with" not in CPL.REPORTED


def test_the_wet_filed_ratchet_is_by_identity_and_does_not_net(tmp_path):
    """THE AUDIT OF PHASE 17 (30 Oct 2026). The ratchet was a CEILING OF 1 on a total: re-file the
    careful record and give a second plan naming the same parti a structural copy of the claim in
    the same commit, and the count stayed 1 and the check green -- the identity moved and nothing
    noticed. It is a set of `(plan, room)` now, WP-11.4's grandfather-by-identity shape, and that
    exact pair must fail."""
    import os
    import subprocess
    import sys
    sys.path.insert(0, str(ROOT / "build"))
    import modcache
    CPL = modcache.load("check_plans", os.path.join(str(ROOT), "build", "check_plans.py"))
    careful = ("plans/tidewater-georgian-careful.json", "primarybath")
    assert CPL.wet_filed_verdict({careful}) == ([], [])
    moved = ("plans/another.json", "primarybath")
    assert CPL.wet_filed_verdict({moved}) == ([moved], [careful]), "a moved identity is NEW"

    plan = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())
    a = json.loads(json.dumps(plan))
    for lv in a["levels"]:
        for r in lv["rooms"]:
            if r["id"] == "primarybath":
                r["wet_stack_with"] = r.pop("stacks_over")
    b = json.loads(json.dumps(plan))
    b["id"] = "another-careful"
    (tmp_path / "a.json").write_text(json.dumps(a))
    (tmp_path / "b.json").write_text(json.dumps(b))
    r = subprocess.run(["timeout", "120", sys.executable, str(ROOT / "build" / "check_plans.py"),
                        str(tmp_path / "a.json"), str(tmp_path / "b.json")],
                       capture_output=True, text=True, cwd=str(ROOT))
    assert "1 wet stack(s) still filed as structural" in r.stdout, r.stdout[-400:]
    assert r.returncode == 1 and "not in `WET_FILED_AS_STRUCTURAL`" in r.stderr, (
        r.returncode, r.stderr[-600:])
    assert "b.json primarybath" in r.stderr, r.stderr[-600:]
