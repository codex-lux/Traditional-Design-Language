"""WP-9.2 — the move registry. Every test is named for the finding it protects.

A move is a corpus rule made executable against a plan RECORD. The registry (moves/registry.json)
is data and quotes the sentence each move executes; build/moves.py is the code; build/check_moves.py
holds the two together. These tests pin the discipline: a move reads structured evidence and never
prose, touches declared fields and never a placement key, refuses with a reason and never skips in
silence, and executes the corpus's own fix rather than an opinion.
"""
import copy
import json
import os
import subprocess
import sys

import pytest

from conftest import load_plan, minimal_plan

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
import modcache as mc  # noqa: E402

MV = mc.load("moves", os.path.join(BUILD, "moves.py"))
PC = mc.load("plan_check", os.path.join(BUILD, "plan_check.py"))
CK = mc.load("check_moves", os.path.join(BUILD, "check_moves.py"))
CO = mc.load("check_openings", os.path.join(BUILD, "check_openings.py"))


def _room(plan, rid):
    return next(r for lv in plan["levels"] for r in lv["rooms"] if r["id"] == rid)


# ------------------------------------------------------------------ the registry and its code
class TestTheRegistryAndItsCodeAgree:
    def test_every_registered_move_has_an_apply_and_every_apply_is_registered(self):
        ids = {m["id"] for m in MV.registry()["moves"]}
        assert ids == set(MV.APPLY), (ids ^ set(MV.APPLY))

    def test_the_checker_passes_today(self):
        proc = subprocess.run([sys.executable, os.path.join(BUILD, "check_moves.py")],
                              capture_output=True, text=True, cwd=ROOT)
        assert proc.returncode == 0, proc.stdout + proc.stderr

    def test_every_basis_quotes_a_sentence_really_in_the_record_it_names(self):
        rep = CO.Report()
        for m in MV.registry()["moves"]:
            CO.check_basis(rep, m, source="moves/registry.json")
        assert rep.errors == []

    def test_a_basis_altered_by_one_word_is_refused(self):
        m = copy.deepcopy(MV.move("passage-to-its-band"))
        m["basis"] = m["basis"].replace("two people pass", "three people pass")
        rep = CO.Report()
        CO.check_basis(rep, m, source="moves/registry.json")
        assert rep.errors, "a misquoted basis passed the verifier"

    def test_no_move_may_touch_a_placement_key(self):
        for m in MV.registry()["moves"]:
            for t in m["touches"]:
                assert t in CK.ALLOWED_TOUCHES, (m["id"], t)
                assert not any(w in t for w in CK.PLACEMENT_WORDS), (m["id"], t)
        # and the allow-list itself admits none
        for t in CK.ALLOWED_TOUCHES:
            assert not any(w in t for w in CK.PLACEMENT_WORDS), t

    def test_shorten_for_daylight_is_retired_and_the_refusal_is_recorded(self):
        assert "shorten-for-daylight" not in MV.APPLY
        assert any(r["id"] == "shorten-for-daylight" and "OQ 92" in r["why"]
                   for r in MV.registry()["refusals"])

    def test_the_ruled_authority_is_recorded_with_what_it_may_not_do(self):
        a = MV.registry()["authority"]
        assert a["ruled"] == "1 Sep 2026"
        assert any("judgment slot" in x for x in a["may_not"])
        assert any("parti has no place for" in x for x in a["may_not"])


# ------------------------------------------------------------------ the dimension moves
class TestTheDimensionMoves:
    def _dining(self):
        return minimal_plan([{"id": "dining", "type": "dining-room", "name": "Dining Room",
                              "width_ft": 12.3, "length_ft": 16, "exterior_walls": ["S"],
                              "windows": [{"wall": "S", "width_ft": 3.0, "count": 2}],
                              "doors": [{"to": "exterior"}]}])

    def test_widen_for_furniture_reads_the_unrounded_need(self):
        """compose.repair read `12.3` out of the sentence for a room needing 12.333, and
        `12.3 > 12.3` was false. The move reads the field and the dining room moves."""
        plan = self._dining()
        f = {"id": "furniture:dining", "layer": "furniture", "kind": "furniture-fit", "room": "dining",
             "need_ft": 12.333, "have_ft": 12.3, "axis": "width", "item": "dining table, seats 8"}
        res = MV.apply("widen-for-furniture", plan, f)
        assert "changed" in res, res
        assert _room(plan, "dining")["width_ft"] == 12.4
        assert res["log"].startswith("Widened Dining Room from 12.3 to 12.4 ft")
        assert res["requires"] == "re-place" and res["kind"] == "measured"

    def test_a_closet_needing_more_than_1_8x_its_width_is_moved_or_refused_never_skipped(self):
        plan = minimal_plan([{"id": "cl", "type": "closet", "name": "Closet", "width_ft": 2.1, "length_ft": 6,
                              "doors": [{"to": "exterior"}]}])
        f = {"id": "furniture:cl", "layer": "furniture", "kind": "furniture-fit", "room": "cl",
             "need_ft": 5.2, "have_ft": 2.1, "axis": "width", "item": "coat closet at the entry"}
        res = MV.apply("widen-for-furniture", plan, f)
        assert ("changed" in res) or ("refused" in res and res["refused"])
        if "changed" in res:
            assert _room(plan, "cl")["width_ft"] >= 5.2

    def test_a_widening_past_the_band_ceiling_is_refused_with_the_reason(self):
        plan = minimal_plan([{"id": "cl", "type": "closet", "name": "Closet", "width_ft": 3, "length_ft": 30,
                              "doors": [{"to": "exterior"}]}])
        f = {"id": "furniture:cl", "layer": "furniture", "kind": "furniture-fit", "room": "cl",
             "need_ft": 40, "have_ft": 3, "axis": "width", "item": "a wardrobe the size of a house"}
        res = MV.apply("widen-for-furniture", plan, f)
        assert "refused" in res and "band ceiling" in res["refused"]
        assert _room(plan, "cl")["width_ft"] == 3, "a refused move must not have written"

    def test_a_dimension_move_never_touches_geometry(self):
        GEO = mc.load("geometry", os.path.join(BUILD, "geometry.py"))
        plan = GEO.solve(load_plan("tidewater-georgian-careful"), engine="heuristic")
        r = _room(plan, "butlers")
        g = copy.deepcopy(r["geometry"])
        f = {"id": "furniture:butlers", "layer": "furniture", "kind": "furniture-fit", "room": "butlers",
             "need_ft": 9.1, "have_ft": r["width_ft"], "axis": "width", "item": "a place to stage a whole course"}
        MV.apply("widen-for-furniture", plan, f)
        assert r["geometry"] == g

    def test_passage_to_its_band_reads_the_passage_record_not_a_constant_of_its_own(self):
        plan = minimal_plan([{"id": "p", "type": "centre-passage", "name": "Passage", "width_ft": 4.5, "length_ft": 30,
                              "doors": [{"to": "exterior"}]}])
        f = {"id": "drawn:p", "layer": "drawn", "kind": "passage-narrow", "room": "p", "have_ft": 4.5,
             "band": [6.0, 7.0], "declared_ft": 4.5}
        res = MV.apply("passage-to-its-band", plan, f)
        assert "changed" in res and _room(plan, "p")["width_ft"] == 6.0
        assert "SIX TO SEVEN FEET" in MV.move("passage-to-its-band")["basis"]

    def test_the_stair_hall_grows_to_the_run_the_refusal_states_and_not_when_the_record_would_have_held_it(self):
        plan = minimal_plan([{"id": "st", "type": "stair-hall", "name": "Stair Hall", "width_ft": 6, "length_ft": 8,
                              "doors": [{"to": "exterior"}]}])
        f = {"id": "drawn:st", "layer": "drawn", "kind": "stair-not-drawn", "room": "st",
             "need_ft": [11.7, 6.5], "have_ft": [8, 6], "declared_fits": False, "risers": 20}
        res = MV.apply("grow-stair-hall-to-its-run", plan, f)
        assert "changed" in res
        r = _room(plan, "st")
        assert r["length_ft"] >= 11.7 and r["width_ft"] >= 6.5
        f2 = dict(f, declared_fits=True)
        assert "refused" in MV.apply("grow-stair-hall-to-its-run", minimal_plan([dict(r)]), f2)

    def test_trade_width_for_depth_keeps_the_area_and_executes_the_faults_own_cheap_fix(self):
        plan = load_plan("tidewater-georgian-careful")
        porch = _room(plan, "porch")
        area = porch["width_ft"] * porch["length_ft"]
        f = {"id": "fault:porch-too-shallow-to-inhabit", "layer": "fault", "kind": "fault-present",
             "fault": "porch-too-shallow-to-inhabit", "value": 6.0, "required": "at-least 7.0"}
        res = MV.apply("trade-width-for-depth-at-constant-area", plan, f)
        assert "changed" in res and res["tier"] == "cheap"
        assert porch["width_ft"] == 7.0
        assert abs(porch["width_ft"] * porch["length_ft"] - area) < 0.5


# ------------------------------------------------------------------ the declared moves
class TestTheDeclaredMoves:
    def test_the_canonical_variant_is_the_one_the_finding_carries_from_the_cascade(self):
        plan = minimal_plan([{"id": "h", "type": "hall", "width_ft": 14, "length_ft": 16, "doors": [{"to": "exterior"}]}],
                            style="colonial-revival", massing="four-over-four")
        plan["declared"] = {"dormer": "shed-dormer"}
        f = {"id": "style:dormer", "layer": "style", "kind": "variant-forbidden", "slot": "dormer",
             "variant": "shed-dormer", "canonical": "gable-dormer"}
        res = MV.apply("replace-forbidden-declared-variant", plan, f)
        assert "changed" in res and plan["declared"]["dormer"] == "gable-dormer"
        assert "refused" in MV.apply("replace-forbidden-declared-variant", plan, dict(f, canonical=None))

    def test_a_declared_measurement_move_never_writes_a_name_the_plan_did_not_declare(self):
        plan = load_plan("tidewater-georgian-careful")
        assert "measurements" not in plan or "shutter_leaf_width_in" not in plan["measurements"]
        f = {"id": "fault:shutter-half-width-leaf", "layer": "fault", "kind": "fault-present",
             "fault": "shutter-half-width-leaf", "value": 0.33, "required": "at-least 0.48"}
        res = MV.apply("shutter-leaf-at-half-the-opening", plan, f)
        assert "refused" in res
        assert "shutter_leaf_width_in" not in (plan.get("measurements") or {})

    def test_the_spec_colonials_declared_half_width_shutter_is_set_to_half_the_opening(self):
        plan = load_plan("spec-builder-colonial")
        m = plan["measurements"]
        assert m["shutter_leaf_width_in"] == 12 and m["window_opening_width_in"] == 36
        f = {"id": "fault:shutter-half-width-leaf", "layer": "fault", "kind": "fault-present",
             "fault": "shutter-half-width-leaf", "value": 0.333, "required": "at-least 0.48", "source": "declared"}
        res = MV.apply("shutter-leaf-at-half-the-opening", plan, f)
        assert "changed" in res and m["shutter_leaf_width_in"] == 18.0 and res["tier"] == "right"

    def test_the_dormer_count_comes_down_to_odd_and_never_from_none(self):
        plan = load_plan("tidewater-georgian-careful")
        f = {"id": "fault:dormer-off-the-bay", "layer": "fault", "kind": "fault-present",
             "fault": "dormer-off-the-bay", "expression": "dormer_count % 2"}
        assert "refused" in MV.apply("reduce-the-dormer-count-to-the-rhythm", plan, f)   # declares none
        plan["declared"]["dormer"] = {"variant": "gable-dormer", "count": 4}
        res = MV.apply("reduce-the-dormer-count-to-the-rhythm", plan, f)
        assert "changed" in res and plan["declared"]["dormer"]["count"] == 3


# ------------------------------------------------------------------ the ruled authority
class TestOpeningsAndRoomsUnderTheRuling:
    def test_add_the_grammar_door_refuses_a_pair_the_catalogue_says_must_not_adjoin(self, corpus):
        pair = None
        for t, rt in corpus["rooms"].items():
            for rule in (rt.get("adjacency") or {}).get("must_not_adjoin") or []:
                if rule["room"] in corpus["rooms"]:
                    pair = (t, rule["room"]); break
            if pair: break
        assert pair, "the catalogue states no must_not_adjoin pair"
        a, b = pair
        plan = minimal_plan([{"id": "a", "type": a, "width_ft": 12, "length_ft": 12, "doors": []},
                             {"id": "b", "type": b, "width_ft": 12, "length_ft": 12, "doors": [{"to": "exterior"}]}])
        f = {"id": "drawn:a", "layer": "drawn", "kind": "unreachable", "room": "a", "adjacent_placed": ["b"]}
        res = MV.apply("add-the-grammar-door", plan, f, corpus)
        assert "refused" in res and "must not adjoin" in res["refused"]
        assert not _room(plan, "a").get("doors")

    def test_add_the_grammar_door_adds_the_grammars_door_on_both_rooms_and_dimensions_it(self, corpus):
        plan = minimal_plan([{"id": "lib", "type": "library", "name": "Library", "width_ft": 14, "length_ft": 18, "doors": []},
                             {"id": "pass", "type": "centre-passage", "name": "Passage", "width_ft": 7, "length_ft": 30,
                              "doors": [{"to": "exterior"}]}])
        f = {"id": "drawn:lib", "layer": "drawn", "kind": "unreachable", "room": "lib", "adjacent_placed": ["pass"]}
        res = MV.apply("add-the-grammar-door", plan, f, corpus)
        assert "changed" in res, res
        d = next(x for x in _room(plan, "lib")["doors"] if x["to"] == "pass")
        e = next(x for x in _room(plan, "pass")["doors"] if x["to"] == "lib")
        assert d.get("width_ft") and d.get("type") and e.get("width_ft") == d["width_ft"]
        assert res["basis"] and "og-" in res["log"]

    def test_drop_optional_room_needs_the_diagram_and_refuses_a_must_have(self, corpus):
        plan = minimal_plan([{"id": "study", "type": "study", "name": "Study", "width_ft": 10, "length_ft": 12, "doors": []},
                             {"id": "hall", "type": "hall", "width_ft": 14, "length_ft": 16, "doors": [{"to": "exterior"}, {"to": "study"}]}])
        f = {"id": "drawn:study", "layer": "drawn", "kind": "unreachable", "room": "study", "adjacent_placed": []}
        assert "refused" in MV.apply("drop-optional-room", plan, f, corpus, {})
        parti = {"id": "p", "rooms": [{"id": "study", "type": "study", "required": False}]}
        assert "refused" in MV.apply("drop-optional-room", plan, f, corpus, {"parti": parti, "must_have": ["study"]})
        res = MV.apply("drop-optional-room", plan, f, corpus, {"parti": parti, "must_have": []})
        assert "changed" in res
        assert all(r["id"] != "study" for lv in plan["levels"] for r in lv["rooms"])
        assert all(d["to"] != "study" for d in _room(plan, "hall")["doors"])

    def test_split_per_grouping_only_where_a_grouping_says_to(self, corpus):
        plan = minimal_plan([{"id": "lib", "type": "library", "name": "Library", "width_ft": 16, "length_ft": 30,
                              "doors": [{"to": "exterior"}]}])
        f = {"id": "room:lib", "layer": "room", "kind": "area-above-band", "room": "lib", "have_sf": 480}
        assert "refused" in MV.apply("split-per-grouping", plan, f, corpus)
        plan["groupings"] = ["library-study-pair"]
        res = MV.apply("split-per-grouping", plan, f, corpus)
        assert "changed" in res, res
        ids = [r["id"] for lv in plan["levels"] for r in lv["rooms"]]
        assert "lib-2" in ids and _room(plan, "lib")["length_ft"] == 15
        assert "Split rather than enlarge" in res["basis"]


# ------------------------------------------------------------------ the levers
class TestTheLevers:
    def test_search_harder_changes_the_candidates_and_never_the_record(self):
        plan = load_plan("tidewater-georgian-careful")
        before = json.dumps(plan, sort_keys=True)
        r1 = MV.apply("search-harder", plan, {}, None, {"candidates": 250})
        r2 = MV.apply("search-harder", plan, {}, None, {"candidates": 1000})
        r3 = MV.apply("search-harder", plan, {}, None, {"candidates": 2000})
        assert r1["lever"] == {"candidates": 1000} and r2["lever"] == {"candidates": 2000}
        assert "refused" in r3
        assert json.dumps(plan, sort_keys=True) == before

    def test_prove_it_refuses_when_the_proof_was_already_asked_for(self):
        """Three states, not two. `cp`: the proof was already asked for. `heuristic`: the search
        was asked for BY NAME (the bench's drag path, check_all's bounded composer run) and the
        lever does not take a 25 s proof behind that request -- the first version did, under
        an explicit --revise-engine heuristic. Only `auto` leaves the engine to the lever."""
        pytest.importorskip("ortools")
        assert "refused" in MV.apply("prove-it", {}, {}, None, {"engine": "cp"})
        assert "refused" in MV.apply("prove-it", {}, {}, None, {"engine": "heuristic"})
        assert MV.apply("prove-it", {}, {}, None, {"engine": "auto"})["lever"] == {"engine": "cp"}


# ------------------------------------------------------------------ answering
class TestAnswering:
    def test_answering_matches_structured_fields_and_never_the_statement(self):
        plan = minimal_plan([{"id": "dining", "type": "dining-room", "width_ft": 12.3, "length_ft": 16, "doors": [{"to": "exterior"}]}])
        f = {"id": "furniture:dining", "layer": "furniture", "kind": "furniture-fit", "room": "dining",
             "need_ft": 12.333, "have_ft": 12.3, "axis": "width", "item": "dining table",
             "statement": "THIS SENTENCE SAYS NOTHING A MOVE MAY READ"}
        ans = MV.answering(f, plan)
        assert [m["id"] for m in ans] == ["widen-for-furniture"]
        assert ans[0]["would"].startswith("Widened")
        g = dict(f, kind="area-below-band")
        assert MV.answering(g, plan) == []

    def test_a_move_whose_precondition_fails_on_this_record_is_not_offered(self):
        plan = load_plan("tidewater-georgian-careful")
        f = {"id": "fault:shutter-half-width-leaf", "layer": "fault", "kind": "fault-present",
             "fault": "shutter-half-width-leaf", "value": 0.33, "required": "at-least 0.48"}
        ans = MV.answering(f, plan)
        assert "shutter-leaf-at-half-the-opening" not in [m["id"] for m in ans]

    def test_answering_writes_nothing(self):
        plan = load_plan("spec-builder-colonial")
        before = json.dumps(plan, sort_keys=True)
        f = {"id": "fault:shutter-half-width-leaf", "layer": "fault", "kind": "fault-present",
             "fault": "shutter-half-width-leaf", "value": 0.333, "required": "at-least 0.48", "source": "declared"}
        ans = MV.answering(f, plan)
        assert [m["id"] for m in ans] == ["shutter-leaf-at-half-the-opening"]
        assert json.dumps(plan, sort_keys=True) == before
