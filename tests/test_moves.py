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
        # WP-9.4: the first assertion here was `"changed" in res or "refused" in res`, which
        # every apply satisfies. The closet's band ceiling (rooms/closet.json) admits 5.2 x 6
        # = 31 sf, so the move must APPLY, to the unrounded need, and say so
        assert "changed" in res, res
        assert _room(plan, "cl")["width_ft"] >= 5.2
        assert any(c["path"].endswith("width_ft") and c["to"] >= 5.2 for c in res["changed"])

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



# ------------------------------------------------------------------ WP-9.4: what the audit found
class TestTheDeclarationIsEnforced:
    """`touches` was documentation checked against an allow-list; nothing compared it to what
    an apply function WROTE, and the WP-9.2 report said a test did. Three of twenty-one wrote
    outside their declaration -- one of them nine authored window counts on the Tidewater plan
    through a plan-wide re-derivation. `apply()` diffs the record now and refuses, restoring
    it, on a write outside `touches` or a write `changed` does not report."""

    def test_the_registry_counts_are_pinned(self):
        """Delete a move and its apply entry together and every other test stayed green.

        21 -> 22 at the PR #19 / PR #20 merge, and the guard earned itself there: the
        arrangement branch's style-layer passage-floor repair lived inside the forty-line
        `compose.repair` this registry replaced, so taking either side of that conflict whole
        would have dropped it. It is ported as `passage-to-the-styles-own-floor` -- the
        sibling `passage-to-its-band` widens to the room catalogue's 6 ft, a Georgian kit's
        own cascade asks for 10, and `passage-that-is-a-corridor` between them is FATAL.
        """
        reg = MV.registry()
        assert len(reg["moves"]) == 22, [m["id"] for m in reg["moves"]]
        assert len(reg["refusals"]) == 9
        names = " ".join(json.dumps(r) for r in reg["refusals"])
        for wanted in ("shorten-for-daylight", "align-upper-walls-to-the-room-below", "move-door-to-a-shared-wall"):
            assert wanted in names, wanted

    def test_a_move_that_writes_outside_its_touches_is_refused_and_the_record_restored(self, monkeypatch):
        plan = minimal_plan([{"id": "cl", "type": "closet", "name": "Closet", "width_ft": 2.1, "length_ft": 6,
                              "doors": [{"to": "exterior"}]}])
        before = json.dumps(plan, sort_keys=True)

        def rogue(p, f, C, ctx):
            r = _room(p, "cl")
            r["width_ft"] = 5.2
            r["ceiling_ft"] = 12.0          # not in widen-for-furniture's touches
            return {"changed": [{"path": "levels[].rooms[cl].width_ft", "from": 2.1, "to": 5.2}], "log": "x"}
        monkeypatch.setitem(MV.APPLY, "widen-for-furniture", rogue)
        f = {"id": "furniture:cl", "layer": "furniture", "kind": "furniture-fit", "room": "cl",
             "need_ft": 5.2, "have_ft": 2.1, "axis": "width", "item": "coat closet at the entry"}
        res = MV.apply("widen-for-furniture", plan, f)
        assert "refused" in res and "ceiling_ft" in res["refused"] and "outside its touches" in res["refused"]
        assert json.dumps(plan, sort_keys=True) == before, "the record is restored byte-identically"

    def test_a_write_the_move_does_not_report_is_refused(self, monkeypatch):
        plan = minimal_plan([{"id": "cl", "type": "closet", "name": "Closet", "width_ft": 2.1, "length_ft": 6,
                              "doors": [{"to": "exterior"}]}])

        def quiet(p, f, C, ctx):
            _room(p, "cl")["width_ft"] = 5.2
            return {"changed": [], "log": "x"}
        monkeypatch.setitem(MV.APPLY, "widen-for-furniture", quiet)
        f = {"id": "furniture:cl", "layer": "furniture", "kind": "furniture-fit", "room": "cl",
             "need_ft": 5.2, "have_ft": 2.1, "axis": "width", "item": "coat closet at the entry"}
        res = MV.apply("widen-for-furniture", plan, f)
        assert "refused" in res and "without reporting" in res["refused"]
        assert _room(plan, "cl")["width_ft"] == 2.1

    def test_paths_written_spells_rooms_by_id_and_lists_by_addition(self):
        a = minimal_plan([{"id": "x", "type": "closet", "name": "X", "width_ft": 2, "length_ft": 6, "doors": [], "windows": [{"wall": "S", "count": 1}]}])
        b = copy.deepcopy(a)
        _room(b, "x")["width_ft"] = 3
        _room(b, "x")["windows"][0]["wall"] = "N"
        _room(b, "x")["doors"].append({"to": "exterior"})
        got = MV._paths_written(a, b)
        assert set(map(MV._norm_path, got)) == {"levels[].rooms[].width_ft", "levels[].rooms[].windows[].wall", "levels[].rooms[].doors[]"}

    def test_passage_to_its_band_on_a_passage_shorter_than_six_feet_long(self):
        """4.5 x 5: the first version wrote 5 x 6 (the sort made 6.0 the LENGTH), left the
        short side under its own band, and logged "widened to 6.0"."""
        plan = minimal_plan([{"id": "p", "type": "centre-passage", "name": "Passage", "width_ft": 4.5, "length_ft": 5.0,
                              "doors": [{"to": "exterior"}]}])
        f = {"id": "drawn:p", "layer": "drawn", "kind": "passage-narrow", "room": "p", "have_ft": 4.5,
             "band": [6.0, 7.0], "declared_ft": 4.5}
        res = MV.apply("passage-to-its-band", plan, f)
        assert "changed" in res, res
        r = _room(plan, "p")
        assert min(r["width_ft"], r["length_ft"]) >= 6.0
        assert {c["path"].split(".")[-1] for c in res["changed"]} == {"width_ft", "length_ft"}

    def test_add_the_grammar_door_leaves_every_other_room_and_every_authored_window_count_alone(self, corpus):
        """On the placed Tidewater plan the first version wrote 253 paths in 25 rooms for one
        door, nine authored window counts among them (dining 2 -> 1, drawing 2 -> 3)."""
        plan = load_plan("tidewater-georgian-careful")
        counts_before = {(r["id"], i): w.get("count") for lv in plan["levels"] for r in lv["rooms"]
                         for i, w in enumerate(r.get("windows") or [])}
        porch = next(r for lv in plan["levels"] for r in lv["rooms"] if r["id"] == "porch")
        stair = next(r for lv in plan["levels"] for r in lv["rooms"] if r["id"] == "stair")
        porch["doors"] = [d for d in porch.get("doors", []) if d["to"] != "stair"]
        stair["doors"] = [d for d in stair.get("doors", []) if d["to"] != "porch"]
        snapshot = copy.deepcopy(plan)
        f = {"id": "drawn:porch", "layer": "drawn", "kind": "unreachable", "room": "porch", "adjacent_placed": ["stair"]}
        res = MV.apply("add-the-grammar-door", plan, f, corpus)
        assert "changed" in res, res
        counts_after = {(r["id"], i): w.get("count") for lv in plan["levels"] for r in lv["rooms"]
                        for i, w in enumerate(r.get("windows") or [])}
        assert counts_after == counts_before, "an authored window count is never overwritten by a door"
        written = {MV._norm_path(p) for p in MV._paths_written(snapshot, plan)}
        assert written == {"levels[].rooms[].doors[]"}, written
        touched_rooms = {p.split("rooms[")[1].split("]")[0] for p in MV._paths_written(snapshot, plan)}
        assert touched_rooms == {"porch", "stair"}
        # and the PRE-EXISTING doors of both rooms are byte-identical: the first version of
        # this test bit by fixture luck -- the passage's authored doors happened to lack `type`,
        # so a plan-wide re-derivation that rewrote them was visible only there (the session's
        # audit). Only the appended door carries derived fields.
        for rid in ("porch", "stair"):
            before = next(r for lv in snapshot["levels"] for r in lv["rooms"] if r["id"] == rid).get("doors", [])
            after = next(r for lv in plan["levels"] for r in lv["rooms"] if r["id"] == rid).get("doors", [])
            assert after[:len(before)] == before, f"{rid}'s pre-existing doors were rewritten"
            assert len(after) == len(before) + 1
            assert after[-1]["to"] == ("stair" if rid == "porch" else "porch")
            assert "width_ft" in after[-1] and "type" in after[-1], "the appended door is the derived one"

    def test_move_window_off_the_needed_wall_never_reaches_into_placement_keys(self):
        plan = minimal_plan([{"id": "din", "type": "dining-room", "name": "Dining", "width_ft": 14, "length_ft": 18,
                              "exterior_walls": ["S", "E"], "doors": [{"to": "exterior"}],
                              "windows": [{"wall": "S", "count": 2, "width_ft": 3.0, "position_ft": 4.0, "positions_ft": [4.0, 9.0]}]}])
        f = {"id": "drawn:din", "layer": "drawn", "kind": "wall-run", "room": "din", "item": "sideboard",
             "walls_with_windows": ["S"], "need_ft": 8.0, "have_ft": 3.0}
        res = MV.apply("move-window-off-the-needed-wall", plan, f)
        assert "changed" in res, res
        w = _room(plan, "din")["windows"][0]
        assert w["wall"] == "E"
        # the stale placement stays on the record for the strip before re-placement to remove;
        # the move itself writes only what it declares
        assert w.get("position_ft") == 4.0 and w.get("positions_ft") == [4.0, 9.0]
        assert MV.move("move-window-off-the-needed-wall")["requires"] == "re-place"

    def test_the_four_moves_the_sweep_never_reached_apply_on_a_fixture_that_triggers_them(self, corpus):
        # widen-wet-room-for-fixture
        plan = minimal_plan([{"id": "b", "type": "bathroom", "name": "Bath", "width_ft": 4, "length_ft": 4.5, "doors": [{"to": "exterior"}]}])
        f = {"id": "drawn:b", "layer": "drawn", "kind": "fixture-unplaced", "room": "b", "item": "tub", "need_ft": [5.0, 2.5]}
        res = MV.apply("widen-wet-room-for-fixture", plan, f, corpus)
        assert "changed" in res and max(_room(plan, "b")["width_ft"], _room(plan, "b")["length_ft"]) >= 5.0, res
        assert "refused" in MV.apply("widen-wet-room-for-fixture", minimal_plan([{"id": "b", "type": "bathroom", "name": "Bath", "width_ft": 4, "length_ft": 6, "doors": [{"to": "exterior"}]}]),
                                     dict(f, need_ft=[5.0, 2.5]), corpus), "the declared room would hold it: the engine's"
        # grow-to-band-floor
        plan = minimal_plan([{"id": "bed", "type": "bedroom", "name": "Bed", "width_ft": 8, "length_ft": 10, "doors": [{"to": "exterior"}]}])
        f = {"id": "room:bed", "layer": "room", "kind": "area-below-band", "room": "bed", "have_sf": 80, "need_sf": 130, "band": [130, 220]}
        res = MV.apply("grow-to-band-floor", plan, f, corpus)
        assert "changed" in res, res
        r = _room(plan, "bed")
        assert r["width_ft"] * r["length_ft"] >= 130 - 1
        # give-the-room-a-window (scoped to its own room; a neighbour's windows untouched)
        plan = minimal_plan([{"id": "lib", "type": "library", "name": "Library", "width_ft": 14, "length_ft": 18,
                              "exterior_walls": ["S"], "doors": [{"to": "pass"}]},
                             {"id": "pass", "type": "centre-passage", "name": "Passage", "width_ft": 7, "length_ft": 30,
                              "doors": [{"to": "exterior"}, {"to": "lib"}], "windows": [{"wall": "N", "count": 2, "width_ft": 3.0}]}])
        f = {"id": "daylight:lib", "layer": "daylight", "kind": "no-window", "room": "lib"}
        snapshot = copy.deepcopy(plan)
        res = MV.apply("give-the-room-a-window", plan, f, corpus)
        assert "changed" in res, res
        assert _room(plan, "lib")["windows"] and _room(plan, "lib")["windows"][0]["wall"] == "S"
        assert _room(plan, "pass") == _room(snapshot, "pass"), "the neighbour is not re-derived"
        assert any(c["path"].endswith("window_head_ft") for c in res["changed"])
        # ... and on a style that is not a node it REFUSES rather than exits the interpreter
        plan = minimal_plan([{"id": "lib", "type": "library", "name": "Library", "width_ft": 14, "length_ft": 18,
                              "exterior_walls": ["S"], "doors": [{"to": "exterior"}]}], style="no-such-style")
        res = MV.apply("give-the-room-a-window", plan, f, corpus)
        assert "refused" in res and "no-such-style" in res["refused"]
        assert not _room(plan, "lib").get("windows") and "window_head_ft" not in _room(plan, "lib")
        # move-window-off-the-needed-wall: the test above


class TestNoMoveReadsProse:
    def test_no_apply_function_reads_a_findings_statement(self):
        """The analogous guard covered only compose.repair. Read the CODE through the AST, not
        the file's text: a docstring that names the word is not a read of it."""
        import ast
        src = open(os.path.join(BUILD, "moves.py"), encoding="utf-8").read()
        tree = ast.parse(src)
        hits = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) and node.slice.value == "statement":
                hits.append(node.lineno)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get" \
                    and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == "statement":
                hits.append(node.lineno)
        assert not hits, f"build/moves.py reads a finding's prose at lines {hits}"


class TestTheDiffSeesPastAnAddedRoom:
    """The session's own audit: `_paths_written` returned at any list-length change, so a move
    that added a room hid every write to every OTHER room behind the one path
    `levels[].rooms[]` -- and split-per-grouping, unscoped, rewrote the same nine authored
    window counts the door move had, under the guard built to catch it."""

    def test_paths_written_descends_into_the_rooms_both_sides_share_when_one_was_added(self):
        a = minimal_plan([{"id": "x", "type": "closet", "name": "X", "width_ft": 2, "length_ft": 6, "doors": [],
                           "windows": [{"wall": "S", "count": 2}]}])
        b = copy.deepcopy(a)
        b["levels"][0]["rooms"].append({"id": "y", "type": "closet", "name": "Y", "width_ft": 2, "length_ft": 6, "doors": []})
        _room(b, "x")["windows"][0]["count"] = 9
        got = {MV._norm_path(p) for p in MV._paths_written(a, b)}
        assert got == {"levels[].rooms[]", "levels[].rooms[].windows[].count"}, got

    def test_split_per_grouping_leaves_every_other_room_and_every_authored_window_count_alone(self, corpus):
        plan = load_plan("tidewater-georgian-careful")
        plan.setdefault("groupings", []).append("library-study-pair")
        counts_before = {(r["id"], i): w.get("count") for lv in plan["levels"] for r in lv["rooms"]
                         for i, w in enumerate(r.get("windows") or [])}
        snapshot = copy.deepcopy(plan)
        f = {"id": "room:library", "layer": "room", "kind": "area-above-band", "room": "library"}
        res = MV.apply("split-per-grouping", plan, f, corpus)
        assert "changed" in res, res
        counts_after = {(r["id"], i): w.get("count") for lv in plan["levels"] for r in lv["rooms"]
                        for i, w in enumerate(r.get("windows") or []) if r["id"] != "library-2"}
        assert counts_after == counts_before
        touched = {p.split("rooms[")[1].split("]")[0] for p in MV._paths_written(snapshot, plan) if "rooms[" in p}
        assert touched - {""} <= {"library", "library-2"}, touched   # "" is the added room, spelled rooms[]
        # both halves door to each other, and the door is dimensioned once for the pair
        lib = _room(plan, "library"); lib2 = _room(plan, "library-2")
        d = next(x for x in lib["doors"] if x["to"] == "library-2"); e = next(x for x in lib2["doors"] if x["to"] == "library")
        assert d.get("width_ft") and d.get("width_ft") == e.get("width_ft")


# ------------------------------------------------------------------ the session's audit of the guard
class TestTheSessionAuditOfTheGuard:
    """Three independent auditors read the WP-9.4 guard and found what it could not see: a
    rewrite of an existing element in a list a move appended to, a write to the first of two
    rooms sharing an id, a dict added whole reported as a bare key, an adjacency row a move
    removed without declaring it; and beside the guard, two moves reading the LONG side as the
    width, a narrowing move that widened, a door duplicated on an asymmetric record, a
    SystemExit out of one of three re-deriving moves, and three successor moves unreachable
    once their predecessor was tabu. Each test here went red on the tree the auditors read."""

    def test_the_diff_sees_a_rewrite_inside_a_list_the_move_appended_to(self):
        before = {"doors": [{"to": "a"}, {"to": "b"}]}
        after = {"doors": [{"to": "a", "width_ft": 3.0}, {"to": "b"}, {"to": "c"}]}
        written = MV._paths_written(before, after)
        assert "doors[]" in written and "doors[0].width_ft" in written, written

    def test_the_diff_sees_a_write_to_the_first_of_two_rooms_sharing_an_id(self):
        before = {"rooms": [{"id": "foyer", "ceiling_ft": 9}, {"id": "foyer", "ceiling_ft": 9}]}
        after = {"rooms": [{"id": "foyer", "ceiling_ft": 12}, {"id": "foyer", "ceiling_ft": 9}]}
        written = MV._paths_written(before, after)
        assert any(p.endswith("ceiling_ft") for p in written), written

    def test_a_dict_added_whole_is_its_leaves_not_a_bare_key(self):
        written = MV._paths_written({"measurements": {}}, {"measurements": {}, "declared": {"shutter": "none"}})
        assert written == ["declared.shutter"], written
        assert MV._paths_written({}, {"declared": {}}) == ["declared"], "an EMPTY dict added is still a write"

    def test_delete_the_shutters_applies_on_a_record_with_no_declared_key(self):
        plan = minimal_plan([{"id": "p", "type": "parlor", "name": "Parlour", "width_ft": 14, "length_ft": 16}])
        plan.pop("declared")
        plan["measurements"] = {"shutter_leaf_width_in": 12.0, "window_opening_width_in": 36.0}
        f = {"id": "fault:shutter-half-width-leaf", "layer": "fault", "fault": "shutter-half-width-leaf",
             "source": "declared", "required": "between 0.45 and 0.55", "value": 0.33}
        res = MV.apply("delete-the-shutters", plan, f)
        assert "changed" in res, res
        assert plan["declared"]["shutter"] == "none"

    def test_drop_optional_room_removes_the_adjacency_row_and_declares_it(self):
        plan = minimal_plan([{"id": "hall", "type": "stair-hall", "name": "Hall", "width_ft": 8, "length_ft": 16,
                              "doors": [{"to": "den"}]},
                             {"id": "den", "type": "study", "name": "Den", "width_ft": 10, "length_ft": 12,
                              "doors": [{"to": "hall"}]}])
        plan["adjacencies"] = [{"a": "hall", "b": "den", "relation": "adjacent"}]
        ctx = {"parti": {"rooms": [{"id": "hall"}, {"id": "den", "required": False}]}}
        f = {"id": "drawn:den", "layer": "drawn", "kind": "unreachable", "room": "den"}
        res = MV.apply("drop-optional-room", plan, f, None, ctx)
        assert "changed" in res, res
        assert plan["adjacencies"] == []
        assert any(c["path"] == "adjacencies[]" for c in res["changed"])
        assert not any(d["to"] == "den" for d in _room(plan, "hall")["doors"])

    def test_drop_optional_room_without_an_adjacencies_key_invents_none(self):
        plan = minimal_plan([{"id": "hall", "type": "stair-hall", "name": "Hall", "width_ft": 8, "length_ft": 16},
                             {"id": "den", "type": "study", "name": "Den", "width_ft": 10, "length_ft": 12}])
        plan.pop("adjacencies")
        ctx = {"parti": {"rooms": [{"id": "hall"}, {"id": "den", "required": False}]}}
        res = MV.apply("drop-optional-room", plan, {"id": "drawn:den", "layer": "drawn", "kind": "unreachable", "room": "den"}, None, ctx)
        assert "changed" in res, res
        assert "adjacencies" not in plan

    def test_split_per_grouping_leaves_the_parlours_authored_window_counts_alone(self):
        """The auditor's fixture: two rooms with authored counts 7 and 9, one split. The
        first version re-derived every window on the plan and the guard saw one path."""
        plan = minimal_plan([{"id": "library", "type": "library", "name": "Library", "width_ft": 14, "length_ft": 24,
                              "exterior_walls": ["S"], "windows": [{"wall": "S", "count": 7, "width_ft": 3.0}],
                              "doors": [{"to": "parlour", "type": "swing", "rank": "principal"}]},
                             {"id": "parlour", "type": "parlor", "name": "Parlour", "width_ft": 14, "length_ft": 16,
                              "exterior_walls": ["S"], "windows": [{"wall": "S", "count": 9, "width_ft": 3.0}],
                              "doors": [{"to": "library", "type": "swing", "rank": "principal"}]}])
        plan["groupings"] = ["library-study-pair"]
        snapshot = copy.deepcopy(plan)
        f = {"id": "room:library", "layer": "room", "kind": "area-above-band", "room": "library"}
        res = MV.apply("split-per-grouping", plan, f)
        assert "changed" in res, res
        assert _room(plan, "parlour") == _room(snapshot, "parlour"), "the parlour was rewritten by the split"
        assert _room(plan, "library")["windows"][0]["count"] == 7
        lib_doors = _room(plan, "library")["doors"]
        assert lib_doors[0] == snapshot["levels"][0]["rooms"][0]["doors"][0], "the library's authored door was rewritten"
        assert _room(plan, "library-2") is not None

    def test_the_widen_moves_read_the_short_side_as_plan_check_judges_it(self):
        """A 16 x 9 dining room needing 12: `widen-to-room-floor` refused it as already at
        its floor and `widen-for-furniture` logged 16 -> 12.4 while growing the SHORT side to
        16 -- both read `width_ft` raw where plan_check swaps the two before judging."""
        plan = minimal_plan([{"id": "din", "type": "dining-room", "name": "Dining", "width_ft": 16, "length_ft": 9}])
        f = {"id": "room:din", "layer": "room", "kind": "width-below-floor", "room": "din", "need_ft": 12.0, "have_ft": 9.0}
        res = MV.apply("widen-to-room-floor", copy.deepcopy(plan), f)
        assert "changed" in res, res
        f2 = {"id": "furniture:din", "layer": "furniture", "kind": "furniture-fit", "room": "din", "axis": "width",
              "need_ft": 12.0, "have_ft": 9.0, "item": "table"}
        p2 = copy.deepcopy(plan)
        res2 = MV.apply("widen-for-furniture", p2, f2)
        assert "changed" in res2, res2
        r = _room(p2, "din")
        assert min(r["width_ft"], r["length_ft"]) == 12.1 and max(r["width_ft"], r["length_ft"]) == 16
        assert "from 9 to 12.1" in res2["log"], res2["log"]

    def test_narrow_the_window_never_widens_a_window(self):
        plan = minimal_plan([{"id": "bath", "type": "bathroom", "name": "Bath", "width_ft": 6, "length_ft": 9,
                              "windows": [{"wall": "N", "count": 1, "width_ft": 2.0}]},
                             {"id": "parlour", "type": "parlor", "name": "Parlour", "width_ft": 14, "length_ft": 16,
                              "windows": [{"wall": "S", "count": 2, "width_ft": 3.5}]}])
        plan["measurements"] = {"window_opening_width_in": 42.0, "window_opening_height_in": 60.0}
        f = {"id": "fault:window-squarer-than-the-style-permits", "layer": "fault", "source": "declared",
             "fault": "window-squarer-than-the-style-permits", "required": "at-least 1.8", "value": 1.43}
        res = MV.apply("narrow-the-window-and-keep-the-height", plan, f)
        assert "changed" in res, res
        assert _room(plan, "bath")["windows"][0]["width_ft"] == 2.0, "a narrowing move widened the bath window"
        assert _room(plan, "parlour")["windows"][0]["width_ft"] < 3.5
        assert "1 already narrower" in res["log"], res["log"]

    def test_add_the_grammar_door_on_an_asymmetric_record_adds_no_duplicate(self, corpus):
        plan = minimal_plan([{"id": "hall", "type": "stair-hall", "name": "Hall", "width_ft": 8, "length_ft": 16,
                              "doors": [{"to": "study"}]},
                             {"id": "study", "type": "study", "name": "Study", "width_ft": 10, "length_ft": 12}])
        f = {"id": "drawn:study", "layer": "drawn", "kind": "unreachable", "room": "study", "adjacent_placed": ["hall"]}
        res = MV.apply("add-the-grammar-door", plan, f, corpus)
        assert "changed" in res, res
        assert [d["to"] for d in _room(plan, "hall")["doors"]] == ["study"], "the hall's door to the study was duplicated"
        assert [d["to"] for d in _room(plan, "study")["doors"]] == ["hall"]

    def test_a_move_that_raises_is_a_refusal_naming_the_exception_and_the_record_is_restored(self, monkeypatch):
        """`resolve_kit` raises SystemExit on an unknown style, and the job worker catches
        Exception: two of the three re-deriving moves let it out (the auditor measured
        `SystemExit escaped apply(): no such node`). One guard, in apply, for every move."""
        plan = minimal_plan([{"id": "p", "type": "parlor", "name": "Parlour", "width_ft": 14, "length_ft": 16}])
        snapshot = copy.deepcopy(plan)

        def boom(plan, f, C, ctx):
            plan["levels"][0]["rooms"][0]["width_ft"] = 99
            raise SystemExit("no such node: not-a-style")
        monkeypatch.setitem(MV.APPLY, "widen-to-room-floor", boom)
        res = MV.apply("widen-to-room-floor", plan, {"id": "x", "layer": "room", "room": "p", "need_ft": 15})
        assert "refused" in res and "SystemExit" in res["refused"] and "no such node" in res["refused"], res
        assert plan == snapshot

    def test_a_successor_move_is_offered_once_its_predecessor_is_tabu_on_the_finding(self):
        """`light-the-far-end` follows `raise-window-head`; once the head move was refused BY
        MEASUREMENT and made tabu, the next round offered only the tabu move and `_choose`
        skipped it -- the successor was unreachable (the auditor's finding)."""
        plan = minimal_plan([{"id": "p", "type": "parlor", "name": "Parlour", "width_ft": 14, "length_ft": 30,
                              "exterior_walls": ["S", "N"], "window_head_ft": 7.0,
                              "windows": [{"wall": "S", "count": 2, "width_ft": 3.0}]}])
        f = {"id": "daylight:p", "layer": "daylight", "kind": "daylight-depth", "room": "p",
             "need_head_ft": 7.5, "ceiling_ft": 9.0, "need_ft": 15.0, "have_ft": 30.0}
        plain = [m["id"] for m in MV.answering(f, plan, None, {})]
        assert plain == ["raise-window-head"], plain
        tabu = {("raise-window-head", "daylight:p")}
        after = [m["id"] for m in MV.answering(f, plan, None, {"tabu": tabu})]
        assert "light-the-far-end" in after and "raise-window-head" not in after, after

    def test_a_basis_under_a_wrong_but_walkable_key_errors_and_an_unwalkable_key_is_unjudged(self):
        """The WP-9.4 key-path check had no test of its own (the auditor skipped the block and
        every basis test stayed green). A real sentence cited under the wrong key is an error;
        a key the walker cannot follow is unjudged -- counted, never a pass."""
        import re
        rec = json.load(open(os.path.join(ROOT, "rooms", "centre-passage.json"), encoding="utf-8"))
        sentence = re.split(r"(?<=[.!?])\s+", rec["description"])[0]
        assert len(sentence) >= 20 and '"' not in sentence
        rep = CO.Report()
        CO.check_basis(rep, {"id": "m", "basis": f'rooms/centre-passage.json description: "{sentence}"'}, source="moves/registry.json")
        assert not rep.errors and not rep.unjudged_items, (rep.errors, rep.unjudged_items)
        rep2 = CO.Report()
        CO.check_basis(rep2, {"id": "m", "basis": f'rooms/centre-passage.json dimensions: "{sentence}"'}, source="moves/registry.json")
        assert rep2.errors and "does not say it" in rep2.errors[0], rep2.errors
        rep3 = CO.Report()
        CO.check_basis(rep3, {"id": "m", "basis": f'rooms/centre-passage.json no.such.key: "{sentence}"'}, source="moves/registry.json")
        assert rep3.unjudged_items and not rep3.errors, (rep3.unjudged_items, rep3.errors)
        assert CK.UNJUDGED_CEILING == 0, "the registry's unjudged citations are ratcheted at zero"


# ------------------------------- the two grouping keys `_split_per_grouping` used to read (WP-12.9)
def test_the_grouping_room_key_is_room_and_the_schema_makes_it_the_only_one():
    """`_split_per_grouping` read `x.get("type") or x.get("room")` and unioned
    `g.get("required_rooms")`. WP-12.8's audit called both dead; censused over all 17 grouping
    records they are dead, and the schema makes them IMPOSSIBLE rather than merely absent --
    which is the difference between deleting a dead fallback and deleting a live one.

    THIS CORPUS DISTINGUISHES THE TWO CASES AND THE DISTINCTION DECIDED THE FIX. A CHECK that
    cannot fire is a hazard, because its greenness reads as a verdict; a FALLBACK that cannot
    fire is a decision about a malformed record, and WP-12.2 kept one for exactly that reason
    (a bay the record calls a door on a wall with no entrance composition). This one is neither:
    `additionalProperties: false` at BOTH levels with `room` required means a record carrying
    `type` or `required_rooms` fails validation and never reaches the reader at all. The schema
    is the guard, so this test asserts the schema.
    """
    schema = json.load(open(os.path.join(ROOT, "schema", "grouping.schema.json"),
                            encoding="utf-8"))
    assert schema.get("additionalProperties") is False
    assert "required_rooms" not in schema["properties"], (
        "the schema now admits `required_rooms`, so build/moves.py's union of it is no longer "
        "provably dead -- restore the reader or keep the key out")

    item = schema["properties"]["rooms"]["items"]
    assert item.get("additionalProperties") is False
    assert "room" in (item.get("required") or []), (
        "`room` is no longer required, so a rooms[] entry can name nothing and "
        "`{x.get('room') for x in ...}` would silently collect a None")
    assert "type" not in item["properties"], (
        "the schema now admits `type` on a grouping room, so dropping the `or x.get('type')` "
        "fallback would make `_split_per_grouping` blind to it")


def test_no_grouping_record_carries_either_retired_key():
    """The corpus half. The schema forbids them; this says the corpus agrees, so a schema
    loosened by accident cannot go unnoticed until a record uses it."""
    import glob
    seen_rooms = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "groupings", "*.json"))):
        g = json.load(open(f, encoding="utf-8"))
        assert "required_rooms" not in g, f
        for x in (g.get("rooms") or []):
            seen_rooms += 1
            assert "type" not in x, (f, x)
            assert x.get("room"), (f, x)
    assert seen_rooms > 50, (
        f"only {seen_rooms} grouping rooms were read -- a selector matching almost nothing "
        f"makes this pass vacuously")


def test_split_per_grouping_still_selects_the_room_it_is_meant_to():
    """And the behaviour, because the two above are both about the SHAPE of the data. Deleting
    the union and the `or` must not change which rooms the move selects: driven on a real
    grouping that carries the split logic, against a room type it really names."""
    import glob
    groupings = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "groupings", "*.json"))):
        g = json.load(open(f, encoding="utf-8"))
        groupings[g["id"]] = g
    hits = []
    for gid, g in groupings.items():
        if not (g.get("expansion_logic") or "").startswith("Split rather than enlarge"):
            continue
        types = {x.get("room") for x in (g.get("rooms") or [])}
        assert types and None not in types, (gid, types)
        hits.append((gid, types))
    assert hits, (
        "no grouping carries `Split rather than enlarge`, so `_split_per_grouping` selects "
        "nothing on this corpus and this guard is about a branch that cannot run")
