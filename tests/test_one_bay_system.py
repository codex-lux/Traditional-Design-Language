"""WP-13.3, the one-bay-system slice: the elevation draws the openings the plan PLACED, where
it placed them, and the three bay systems that lived on one face state one datum.

Measured on 840c7f1 before this: `elevation._face_bays` divided the face's OUTSIDE width evenly
by the plan's bay count and `opening_rects` drew one rectangle per bay per storey off those
centres, never reading a placed window -- 0 of 9 plan windows on the S front fell within 3 in
of an elevation bay centre on the prover, the elevation drew 13 openings on a front the plan
had placed 9 on, and `elevation.py` HARD-CODED the storey-over-storey alignment as a constant
(`bays["count"]` matching, offset 0.0, misaligned False) on a front whose upper windows stand
132 in from the ground's. Three bay systems on one face: the sheet's grid at 9/18/27 (clear),
`facade.rhythm()` at 4.5.. (clear, 9.0 pitch), `_face_bays` at 4.684.. (outside, 9.369 pitch).

The gate row this slice owns is `tests/test_sheet_coherence.py::
test_the_elevations_openings_are_the_plans_placed_openings`, on both engines and both sheets.
These are the guards on HOW it went green -- the datum, the refusals, the measurements that
stopped being constants -- each driven where the shipped corpus cannot reach the branch.

Every elevation here is built on the HEURISTIC, which is deterministic; the prover's placement
is not reproducible under a budget (two runs of the Tidewater record on 15 Sep 2026 gave two
placements, digests 916dabffd3c090e5 and 4bec762c97e72f2e, both OPTIMAL (hard-only)), and the
gate row is where the prover is read.
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


def _b(name):
    return modcache.load(name, os.path.join(ROOT, "build", name + ".py"))


G, ST, RF, EL, RP, FA, AX, RE = (_b(n) for n in
                                 ("geometry", "structure", "roof", "elevation", "render_plan",
                                  "facade", "axis", "render_elevation"))
PLANS = ("tidewater-georgian-careful", "spec-builder-colonial")


# ---------------------------------------------------------------- WP-13.5, the container
#
# THESE FIXTURES READ THE TIDEWATER RECORD AS THE ONE-ELEMENT HOUSE IT WAS UNTIL WP-13.5.
# That package moved the service programme into the dependency the record declares, and this
# file's whole subject is the ELEVATION -- which is drawn for the MAIN BLOCK. With a wing in
# the plan, openings the placer seats in the wing are on no face this elevation has, and the
# layer says so by name ("it stands on the S face of another massing element ... and this
# elevation is of the main block"). That refusal is correct, it is the cost WP-13.5 publishes
# as `oq/the-facade-layer-counts-a-dependencys-windows-as-bays-of-the-front`, and it is
# asserted on the SHIPPED record by the gate (`tests/test_sheet_coherence.py`, whose
# `test_the_elevations_openings_are_the_plans_placed_openings` rows are RED on purpose and are
# NOT re-baselined). What this file measures is the bay system on a house the elevation can
# draw whole, so it strips the container and says so.
def _one_element(plan):
    for lv in plan.get("levels", []):
        for r in lv.get("rooms", []):
            r.pop("block", None)
            r.pop("hyphen", None)
    return plan


def _build(pid):
    plan = _one_element(json.load(open(os.path.join(ROOT, "plans", f"{pid}.json"))))
    G._SOLVE_CACHE.clear()
    res = G.solve(plan, None, engine="heuristic")
    section = ST.build_section(res, None, geometry_result=res)
    roof = RF.build_roof(res, None, section=section)
    return res, section, roof, EL.build_elevation(res, None, section=section, roof=roof)


@pytest.fixture(scope="module")
def built():
    return {pid: _build(pid) for pid in PLANS}


def _fresh(built, pid):
    """A deep copy of one plan's elevation, safe to drive."""
    res, section, roof, elev = built[pid]
    return copy.deepcopy(res), copy.deepcopy(elev)


# ------------------------------------------------------------------ one datum

class TestOneDatum:
    def test_the_face_datum_is_stated_once_and_is_the_outside_face(self, built):
        for pid, (res, section, roof, elev) in built.items():
            d = elev["datum"]
            assert d["x"] == EL.X_DATUM == "outside face"
            assert d["wall_thickness_ft"] == round(section["wall"]["exterior_in"] / 12.0, 4)
            assert d["mirrored"] == EL.FACE_MIRRORED == {"S": False, "E": False, "N": False, "W": False}
            for f in "SNEW":
                assert elev["faces"][f]["datum"] == "outside face", (pid, f)
                assert elev["faces"][f]["mirrored"] is EL.FACE_MIRRORED[f]

    def test_the_conversion_is_one_wall_thickness_on_every_face_and_the_mirror_is_a_stated_switch(self):
        """A plan coordinate along a wall reaches the face by adding the exterior wall, on every
        face, and the N and W faces read WITH the plan's axis -- which is what the scene, the
        roof's stack axes and the DXF have always assumed and what `FACE_MIRRORED` states.

        THE FIRST VERSION OF THIS SLICE MIRRORED N AND W to the drafter's convention (a north
        elevation seen from the north has east on the left), and the Round then put the spec
        Colonial's placed front door 44.0 ft from where the plan seats it, because
        `scene._face_extrude` lays every face out unmirrored. One convention across four readers
        is what the record has; the mirror is a ruling and one switch, and this test asserts the
        switch's stated value so that flipping it is a visible decision and not a drift."""
        W, D, t = 63.0, 38.17, 1.2917
        assert EL.FACE_MIRRORED == {"S": False, "E": False, "N": False, "W": False}
        assert EL.face_u_ft("S", 9.0, W, D, t) == pytest.approx(9.0 + t)
        assert EL.face_u_ft("E", 6.689, W, D, t) == pytest.approx(6.689 + t)
        assert EL.face_u_ft("N", 9.5, W, D, t) == pytest.approx(9.5 + t)
        assert EL.face_u_ft("W", 2.264, W, D, t) == pytest.approx(2.264 + t)
        with pytest.raises(ValueError):
            EL.face_u_ft("X", 0.0, W, D, t)
        # and the switch is live: flipped by hand, the same function mirrors from the far end,
        # so the day it is ruled the conversion is already written
        saved = dict(EL.FACE_MIRRORED)
        try:
            EL.FACE_MIRRORED["N"] = True
            assert EL.face_u_ft("N", 9.5, W, D, t) == pytest.approx(W + t - 9.5)
        finally:
            EL.FACE_MIRRORED.clear()
            EL.FACE_MIRRORED.update(saved)

    def test_the_three_bay_systems_agree_on_where_bay_one_is(self, built):
        """The sheet's grid (the module repeated from the clear face), `facade.rhythm()`'s
        centres (clear) and `_face_bays`' centres (outside) are ONE system: the rhythm's centre
        is the midpoint of the grid's bay and the face's centre is the rhythm's plus one wall.
        Until WP-13.3 the face divided its OUTSIDE width by the count instead, 9.369 ft against
        the plan's 9.0, so bay 1 stood at 4.684 ft outside against 4.5 clear -- 13.3 in apart
        at the far end of the front."""
        res, section, roof, elev = built["tidewater-georgian-careful"]
        rh = FA.rhythm(res)
        assert rh["verdict"] == "derived", rh
        fp = res["footprint"]
        module, bays = fp["bay_module_ft"], fp["bays"]
        assert fp["width_ft"] == pytest.approx(module * bays), \
            "the premise: the plan's width is its bays times its module, so the grid and the rhythm can agree"
        t = section["wall"]["exterior_in"] / 12.0
        face = elev["faces"]["S"]
        assert face["spacing_source"] == "facade.rhythm()"
        assert face["clear_centres_ft"] == [o["centre_ft"] for o in rh["bays_out"]]
        for i, (c_clear, c_out) in enumerate(zip(face["clear_centres_ft"], face["centres_ft"])):
            assert c_clear == pytest.approx((i + 0.5) * module, abs=1e-3), "the rhythm's bay is the grid's bay"
            assert c_out == pytest.approx(c_clear + t, abs=1e-3), "the face's centre is the rhythm's plus one wall"
        assert face["actual_bay_width_in"] == pytest.approx(module * 12.0)
        # and the N face is the same set: it reads with the plan's axis (`FACE_MIRRORED`), and a
        # symmetric rhythm would be the same numbers in the same order mirrored or not
        assert elev["faces"]["N"]["mirrored"] is EL.FACE_MIRRORED["N"]
        assert elev["faces"]["N"]["centres_ft"] == face["centres_ft"]

    def test_a_gable_end_and_a_plan_with_no_rhythm_keep_the_formula_and_say_so(self, built):
        res, section, roof, elev = built["tidewater-georgian-careful"]
        for f in "EW":
            assert elev["faces"][f]["spacing_source"] != "facade.rhythm()"
            assert elev["faces"][f]["clear_centres_ft"] is None
        _r, _s, _rf, spec = built["spec-builder-colonial"]
        assert FA.rhythm(_r)["verdict"] == "could-not-evaluate"
        assert all(spec["faces"][f]["spacing_source"] != "facade.rhythm()" for f in "SNEW")


# ------------------------------------------------------------------ the openings are the plan's

class TestTheOpeningsAreThePlans:
    def test_every_drawn_opening_is_a_placed_opening_and_every_placed_one_is_drawn_or_refused(self, built):
        for pid, (res, section, roof, elev) in built.items():
            for f in "SNEW":
                got = EL.opening_rects(elev, f)
                placed = elev["faces"][f]["placed"]
                drawn = {(r["room"], r["storey"], r["along_ft"]) for r in got["rects"]}
                assert len(drawn) == len(got["rects"]), "two rects for one placed opening"
                stack_refused = {(x["room"], x["storey"]) for x in got["refused"]
                                 if x["source"].endswith(".stack_axes_ft")}
                for p in placed:
                    key = (p["room"], p["storey"], p["along_ft"])
                    assert key in drawn or (p["room"], p["storey"]) in stack_refused, (pid, f, key)
                assert len(got["rects"]) <= len(placed), (pid, f, "a rect with no placed opening")
            # and the rhythm is NOT drawn: the Tidewater upper front has four placed windows
            # against a seven-bay rhythm
        elev = built["tidewater-georgian-careful"][3]
        up = [r for r in EL.opening_rects(elev, "S")["rects"] if r["storey"] == "upper"]
        assert len(up) == 4 and elev["faces"]["S"]["count"] == 7

    def test_an_empty_bay_is_stated_empty_and_not_filled_from_the_rhythm(self, built):
        """The ruling's trap: *"the window that gets invented to complete a rhythm is this
        ruling's version of the invented measurement OQ 52 swept out"*. On the Tidewater
        front the plan places no upper window in the two bays either side of the centre; no
        rect stands within half a bay of those centres at the upper storey."""
        res, section, roof, elev = built["tidewater-georgian-careful"]
        face = elev["faces"]["S"]
        up = [r["cx_in"] / 12.0 for r in EL.opening_rects(elev, "S")["rects"] if r["storey"] == "upper"]
        half_bay = face["actual_bay_width_in"] / 24.0
        empty = [c for c in face["centres_ft"] if not any(abs(c - u) < half_bay for u in up)]
        assert len(empty) >= 2, f"the premise: the plan leaves upper bays empty ({empty})"
        placed_up = [p["u_ft"] for p in face["placed"] if p["storey"] == "upper"]
        for c in empty:
            assert not any(abs(c - u) < half_bay for u in placed_up), "the plan placed something there after all"

    def test_a_placer_refusal_reaches_the_refused_list_by_name(self, built):
        """A window the placer declined is named in `placed_refused` with the placer's own
        reason, republished by `opening_rects` so every caller reports it, and the count of
        units is the record's own `count` less what was placed."""
        res, section, roof, elev = built["tidewater-georgian-careful"]
        want = {}
        for i, lv in enumerate(res["levels"]):
            for r in lv["rooms"]:
                for w in r.get("windows") or []:
                    if w.get("unplaced"):
                        n = int(w.get("count") or 1) - len(w.get("positions_ft") or [])
                        if n > 0:
                            want[(w["wall"].upper(), r["id"], i == 1)] = (n, w["unplaced"]["reason"])
        assert want, "the premise: the placer refused something on this plan"
        seen = {}
        for f in "SNEW":
            for x in EL.opening_rects(elev, f)["refused"]:
                if x.get("kind") == "window" and "placer refused" in x["why"]:
                    seen[(f, x["room"], x["storey"] == "upper")] = (x["units"], x["why"])
        assert set(seen) == set(want), (set(seen) ^ set(want))
        for k, (n, reason) in want.items():
            assert seen[k][0] == n and reason in seen[k][1], k

    def test_an_opening_on_another_elements_face_is_refused_by_name(self, built, monkeypatch):
        """The elevation is of the main block. A dependency's window at x = -14 is not on the
        main block's south wall, and a window whose across-the-wall coordinate is not the
        block's face is refused with both coordinates named. Driven, because no shipped plan
        carries a `block` tag (WP-11.14)."""
        res, elev = _fresh(built, "tidewater-georgian-careful")
        section = elev["section"]
        real = RP.openings_of_level

        def off_face(plan, lv, i=None):
            op = real(plan, lv, i)
            if op["windows"]:
                op["windows"][0] = dict(op["windows"][0], edge_ft=5.0)
            return op
        monkeypatch.setattr(RP, "openings_of_level", off_face)
        po = EL.placed_openings(section["geometry"], section, elev["entrance_face"], elev["faces"])
        hit = [x for f in "SNEW" for x in po["faces"][f]["refused"]
               if "another massing element" in x["why"]]
        assert len(hit) == 2, [x["why"] for x in hit]        # one per placed level
        assert all("5.0 ft" in x["why"] for x in hit)

    def test_an_opening_on_a_third_level_is_refused_by_name(self, built):
        res, elev = _fresh(built, "tidewater-georgian-careful")
        section = elev["section"]
        placed = copy.deepcopy(section["geometry"])
        third = copy.deepcopy(placed["levels"][0])
        third["index"] = 2
        third["rooms"] = [r for r in third["rooms"] if r["id"] == "drawing"]
        placed["levels"].append(third)
        po = EL.placed_openings(placed, section, elev["entrance_face"], elev["faces"])
        hit = [x for f in "SNEW" for x in po["faces"][f]["refused"] if "level 2" in x["why"]]
        assert hit and all(x["level_index"] == 2 for x in hit)
        assert all(x["storey"] is None for x in hit)

    def test_the_entrance_is_the_widest_door_and_agrees_with_axis_door_bay(self, built):
        """`axis.door_bay`'s rule -- the widest door on the front is the front door -- restated
        in `placed_openings` because that function returns no door on an even bay count and
        the elevation still has to dress one. Held to it wherever both answer."""
        for pid, (res, section, roof, elev) in built.items():
            face = elev["entrance_face"]
            ents = [p for p in elev["faces"][face]["placed"] if p.get("entrance")]
            assert len(ents) == 1, pid
            db = AX.door_bay(res)
            if db.get("room"):
                assert ents[0]["room"] == db["room"] and ents[0]["along_ft"] == pytest.approx(db["position_ft"]), pid
            rects = [r for r in EL.opening_rects(elev, face)["rects"] if r["entrance"]]
            assert len(rects) == 1 and rects[0]["room"] == ents[0]["room"]

    def test_with_two_front_doors_the_wider_is_the_entrance_whichever_comes_first(self, built, monkeypatch):
        """Driven, because the heuristic seats ONE exterior door on the Tidewater front and a
        first-door rule and a widest-door rule agree on one door. The prover seats two
        (measured 15 Sep 2026: 36 in at 7.79 ft and 42 in at 57.79 ft), so the rule matters
        on the sheet the bench draws; here a narrower door is added WEST of the real one and
        the entrance must stay on the wider."""
        res, elev = _fresh(built, "tidewater-georgian-careful")
        section = elev["section"]
        real = RP.openings_of_level
        face = elev["entrance_face"]

        def two_doors(plan, lv, i=None):
            op = real(plan, lv, i)
            front = [d for d in op["exterior"] if d["wall"] == face]
            if front:
                d = dict(front[0], room="drivenroom", at_ft=front[0]["at_ft"] - 20.0,
                         width_ft=front[0]["width_ft"] - 0.5)
                op["exterior"].insert(0, d)
            return op
        monkeypatch.setattr(RP, "openings_of_level", two_doors)
        po = EL.placed_openings(section["geometry"], section, face, elev["faces"])
        doors = [p for p in po["faces"][face]["placed"] if p["kind"] == "door"]
        assert len(doors) == 2 and doors[0]["room"] == "drivenroom", "the narrower door must come first"
        ents = [p for p in doors if p["entrance"]]
        assert len(ents) == 1 and ents[0]["room"] != "drivenroom", "the entrance is the wider door, not the first"

    def test_the_alignment_tolerance_is_read_from_the_fault_and_moves_with_it(self, tmp_path):
        """A transcribed 2.0 would agree with the record today and stop agreeing the day the
        fault moved; the loader is handed a fault stating 3.5 and must say 3.5, and one
        stating no at-most figure and must refuse by name."""
        rec = json.load(open(os.path.join(ROOT, "faults", "storeys-out-of-vertical-alignment.json")))
        rec["test"]["threshold"] = 3.5
        p = tmp_path / "f.json"
        p.write_text(json.dumps(rec))
        tol, src = EL._load_alignment_tolerance(str(p))
        assert tol == 3.5 and src.endswith("f.json#test.threshold"), (tol, src)
        assert EL.ALIGNMENT_TOL_SOURCE == "faults/storeys-out-of-vertical-alignment.json#test.threshold"
        rec["test"]["direction"] = "at-least"
        p.write_text(json.dumps(rec))
        tol, why = EL._load_alignment_tolerance(str(p))
        assert tol is None and "no at-most figure" in why
        assert EL._load_alignment_tolerance(str(tmp_path / "missing.json"))[0] is None

    def test_build_elevation_reads_the_placement_it_is_handed_and_does_not_re_solve(self, built):
        """THE FINDING OF THE GATE'S FIRST RUN. `build_section`'s default re-solves whatever it
        is handed on the heuristic, so `build_elevation(cp_placed)` with no section drew the
        SEARCH's seven front openings over the prover's three -- WP-12.0's own defect at this
        function's door, invisible while the elevation drew a rhythm. Driven here by moving
        one placed window and handing the record over bare: the elevation follows the record,
        and a re-solve would have put the sash back."""
        res, _elev = _fresh(built, "tidewater-georgian-careful")
        room = next(r for r in res["levels"][0]["rooms"] if r["id"] == "drawing")
        win = next(w for w in room["windows"] if (w.get("wall") or "").upper() == "S")
        old = float(win["positions_ft"][0])
        win["positions_ft"][0] = old + 3.0
        assert EL.carries_a_placement(res)
        elev = EL.build_elevation(res)
        t = elev["section"]["wall"]["exterior_in"] / 12.0
        got = [r["cx_in"] / 12.0 for r in EL.opening_rects(elev, "S")["rects"]
               if r["room"] == "drawing" and r["storey"] == "ground"]
        assert any(abs(u - (old + 3.0 + t)) < 1e-6 for u in got), (got, old + 3.0 + t)
        assert not any(abs(u - (old + t)) < 1e-6 for u in got), "the sash went back: the record was re-solved"
        assert elev["section"]["geometry"] is res, "the section was built on some other record"

    def test_a_secondary_door_carries_no_entrance_and_the_scene_agreement_holds(self, built):
        res, section, roof, elev = built["tidewater-georgian-careful"]
        n = [r for r in EL.opening_rects(elev, "N")["rects"] if r["kind"] == "door"]
        assert len(n) == 3 and all(r["entrance"] is None for r in n)


# ------------------------------------------------------------------ the measurements

class TestTheMeasurementsStoppedBeingConstants:
    def test_the_storey_alignment_is_measured_and_its_tolerance_is_the_faults_own(self, built):
        res, section, roof, elev = built["tidewater-georgian-careful"]
        fault = json.load(open(os.path.join(ROOT, "faults", "storeys-out-of-vertical-alignment.json")))
        assert EL.ALIGNMENT_TOL_IN == fault["test"]["threshold"] == 2.0
        assert EL.ALIGNMENT_TOL_SOURCE.endswith("#test.threshold")
        al = elev["front"]["alignment"]
        rects = EL.opening_rects(elev, elev["entrance_face"])["rects"]
        lo = sorted(r["cx_in"] for r in rects if r["storey"] == "ground")
        up = sorted(r["cx_in"] for r in rects if r["storey"] == "upper")
        # recomputed independently of `storey_alignment`
        want_max = max(min(abs(u - l) for l in lo) for u in up)
        assert al["max_abs_offset_in"] == pytest.approx(want_max, abs=1e-3)
        assert al["max_abs_offset_in"] == pytest.approx(48.396, abs=1e-3), "the figure Lucas read: not 0.0"
        assert al["matching"] == sum(1 for u in up if min(abs(u - l) for l in lo) <= 2.0) == 0
        assert al["missing_or_off"] == sum(1 for l in lo if not any(abs(u - l) <= 2.0 for u in up)) == 7
        m = elev["measurements"]
        assert m["max_abs_offset_between_upper_and_lower_opening_centrelines_in"] == al["max_abs_offset_in"]
        assert m["upper_storey_opening_centres_matching_lower"] == 0
        assert m["upper_storey_windows_missing_or_off_alignment_over_a_lower_bay"] == 7
        assert m["upper_floor_opening_count"] == m["total_upper_storey_openings"] == 4
        assert m["openings_on_the_front_elevation"] == 11

    def test_the_front_counts_are_the_drawn_openings_not_the_bays(self, built):
        for pid, (res, section, roof, elev) in built.items():
            rects = EL.opening_rects(elev, elev["entrance_face"])["rects"]
            m = elev["measurements"]
            assert m["openings_on_the_front_elevation"] == len(rects)
            assert m["upper_floor_opening_count"] == sum(1 for r in rects if r["storey"] == "upper")
            assert m["bay_count"] == elev["front"]["count"], "a bay is still a rhythm fact"
            glazed = sum(r["width_in"] * r["height_in"] for r in rects if r["kind"] == "window") / 144.0
            assert m["glazed_area"] == pytest.approx(glazed, abs=0.01)

    def test_a_one_storey_section_withholds_the_alignment_trio_and_the_upper_count(self, built):
        res, elev = _fresh(built, "tidewater-georgian-careful")
        elev["section"]["storeys"] = [s for s in elev["section"]["storeys"] if s.get("index") == 0]
        elev["front"]["alignment"] = {"why": "driven: one storey"}
        m = EL._derive_measurements(elev)
        for k in ("upper_storey_opening_centres_matching_lower",
                  "max_abs_offset_between_upper_and_lower_opening_centrelines_in",
                  "upper_storey_windows_missing_or_off_alignment_over_a_lower_bay",
                  "upper_floor_opening_count", "total_upper_storey_openings"):
            assert k not in m, k
        assert "openings_on_the_front_elevation" in m

    def test_a_two_storey_front_with_no_upper_opening_withholds_the_parity_count(self, built):
        """A count of zero handed to `even-bay-front`'s `% 2` would convict a house of an
        even-bay front for having no upper opening at all -- zero dormers is not an even
        number of dormers (WP-5.13). Withheld, with the reason on the record, because the two
        faults that read it carry no `applies_when` and are not this slice's files."""
        res, elev = _fresh(built, "tidewater-georgian-careful")
        face = elev["entrance_face"]
        elev["faces"][face]["placed"] = [p for p in elev["faces"][face]["placed"] if p["storey"] != "upper"]
        rects = EL.opening_rects(elev, face)["rects"]
        assert rects and not any(r["storey"] == "upper" for r in rects)
        al = EL.storey_alignment(sorted(r["cx_in"] for r in rects), [], EL.ALIGNMENT_TOL_IN)
        assert al["max_abs_offset_in"] is None and al["matching"] == 0 and al["missing_or_off"] == len(rects)
        elev["front"]["alignment"] = al
        m = EL._derive_measurements(elev)
        assert "upper_floor_opening_count" not in m and "total_upper_storey_openings" not in m
        assert m["upper_storey_windows_missing_or_off_alignment_over_a_lower_bay"] == len(rects)
        assert "max_abs_offset_between_upper_and_lower_opening_centrelines_in" not in m

    def test_the_withheld_names_are_stated_on_the_record(self, built):
        """The two shipped plans withhold nothing (both are two-storey with upper front
        openings), and the record says so with an empty dict rather than silence; a driven
        one-storey record names the two counts it withholds and why."""
        for pid, (res, section, roof, elev) in built.items():
            assert elev["front"]["withheld"] == {}, pid
        one = copy.deepcopy(built["tidewater-georgian-careful"][0])
        one["levels"] = one["levels"][:1]
        section = ST.build_section(one, None, geometry_result=one)
        assert not any(s.get("index") == 1 for s in section["storeys"]), "the premise: one storey"
        elev = EL.build_elevation(one, None, section=section)
        assert set(elev["front"]["withheld"]) >= {"upper_floor_opening_count", "total_upper_storey_openings"}
        assert "one storey" in elev["front"]["withheld"]["upper_floor_opening_count"]
        assert "upper_floor_opening_count" not in elev["measurements"]

    def test_the_mirror_is_axis_mirrors(self, built):
        for pid, (res, section, roof, elev) in built.items():
            mi = AX.mirror(res)
            m = elev["measurements"]
            if mi["verdict"] in ("mirrored", "not-mirrored"):
                assert m["count_of_openings_without_a_mirror_twin_about_the_facade_centreline"] == len(mi["unmatched"])
                widest = max((o.get("width_ft") or 0) for o in mi["unmatched"]) * 12.0 if mi["unmatched"] else 0.0
                assert m["width_of_the_largest_asymmetric_element_in"] == pytest.approx(widest)
            else:
                assert "count_of_openings_without_a_mirror_twin_about_the_facade_centreline" not in m
        # and the Tidewater front is not mirrored: five of seven ground openings have no twin
        m = built["tidewater-georgian-careful"][3]["measurements"]
        assert m["count_of_openings_without_a_mirror_twin_about_the_facade_centreline"] == 5

    def test_a_window_a_stack_stands_on_is_not_counted_as_glass_and_a_door_is_counted(self, built):
        res, elev = _fresh(built, "tidewater-georgian-careful")
        face = elev["entrance_face"]
        win = next(p for p in elev["faces"][face]["placed"] if p["kind"] == "window" and p["storey"] == "ground")
        elev["faces"][face]["stack_axes_ft"] = [win["u_ft"]]
        before = built["tidewater-georgian-careful"][3]["measurements"]["glazed_area"]
        m = EL._derive_measurements(elev)
        assert m["glazed_area"] < before
        assert m["count_of_openings_on_the_axis_of_a_chimney_stack"] == 0, "a refused window is not an opening on the axis"


# ------------------------------------------------------------------ the dormers and the plate

class TestTheDormersAndThePlate:
    def test_a_dormer_centres_on_a_placed_upper_window_and_a_shortfall_is_named(self, built):
        res, elev = _fresh(built, "tidewater-georgian-careful")
        face = elev["entrance_face"]
        ups = sorted(p["u_ft"] for p in elev["faces"][face]["placed"]
                     if p["kind"] == "window" and p["storey"] == "upper")
        assert len(ups) == 4, "the premise: four placed upper windows on the front"
        plan = copy.deepcopy(res)
        plan.setdefault("declared", {})["dormer"] = {"count": 2, "face": face}
        section = ST.build_section(plan, None, geometry_result=plan)
        e2 = EL.build_elevation(plan, None, section=section)
        d = e2["dormers"]
        assert d.get("stated") and d.get("count") == 2 and not d.get("refused"), d
        assert d["positions_source"].startswith(f"elevation.faces.{face}.placed")
        assert len(d["positions_ft"]) == 2 and all(p in ups for p in d["positions_ft"]), (d["positions_ft"], ups)
        assert d["positions_short_why"] is None
        plan["declared"]["dormer"] = {"count": 6, "face": face}
        e3 = EL.build_elevation(plan, None, section=ST.build_section(plan, None, geometry_result=plan))
        d3 = e3["dormers"]
        assert len(d3["positions_ft"]) == 4 and "2 without a window below" in d3["positions_short_why"], d3["positions_short_why"]

    def test_the_plate_names_what_is_not_drawn(self, built, tmp_path):
        res, section, roof, elev = built["tidewater-georgian-careful"]
        face = elev["entrance_face"]
        refused = [x for x in EL.opening_rects(elev, face)["refused"] if x.get("room")]
        assert refused, "the premise: something on the front was refused"
        p = tmp_path / "front.svg"
        RE.render_elevation(elev, str(p), face=face)
        svg = p.read_text()
        line = [t for t in re.findall(r'<text class="dm"[^>]*>([^<]*)</text>', svg) if "NOT DRAWN" in t]
        assert len(line) == 1, line
        units = sum(int(x.get("units") or 1) for x in refused)
        assert line[0].startswith(f"{units} OPENING(S) ON THIS FACE NOT DRAWN")
        for room in {x["room"] for x in refused}:
            assert room.upper() in line[0], room
        # and a face with nothing refused prints no such line
        clean = next((f for f in "SNEW" if not [x for x in EL.opening_rects(elev, f)["refused"] if x.get("room")]), None)
        if clean is not None:
            RE.render_elevation(elev, str(p), face=clean)
            assert "NOT DRAWN" not in p.read_text()
