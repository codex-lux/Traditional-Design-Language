"""A refused candidate is repaired, then retried (ruled by Lucas, 19 Nov 2026).

Four rulings, asked and answered as four acts:
  1. a broken stack's upper room may take the declared size of the room it declares it stacks
     over, as a judgment (`size-the-upper-room-to-the-room-it-stacks-over`);
  2. a fire on a wall the massing puts no stack on may move to the flue wall the massing names
     (`put-the-fire-on-the-flue-wall`);
  3. bearing continuity and tiling get no move;
  4. repair first, placed at the compose budget and adopted only where not refused and judged no
     worse; otherwise the retry runs on the record as composed.

The moves are held on hand-built records against the real corpus; the gate is a pure function;
the wiring is driven through a real `compose` with the refusal and the evidence injected at the
placement the revision loop returns, on the search for speed.
"""
import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
TF = modcache.load("typefacts", os.path.join(ROOT, "build", "typefacts.py"))
RV = modcache.load("revise", os.path.join(ROOT, "build", "revise.py"))
MV = modcache.load("moves", os.path.join(ROOT, "build", "moves.py"))
PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
CR = modcache.load("critique", os.path.join(ROOT, "build", "critique.py"))
C = PC.load_corpus()

STACK = "size-the-upper-room-to-the-room-it-stacks-over"
FIRE = "put-the-fire-on-the-flue-wall"


def _stack_plan(below=(13.0, 16.0), upper=(11.0, 12.0), upper_type="bedroom"):
    return {"id": "t", "style": "georgian-colonial-american", "levels": [
        {"id": "g", "index": 0, "rooms": [
            {"id": "parlor", "type": "parlor", "width_ft": below[0], "length_ft": below[1]}]},
        {"id": "u", "index": 1, "rooms": [
            {"id": "bed", "type": upper_type, "width_ft": upper[0], "length_ft": upper[1],
             "stacks_over": "parlor"}]}]}


def _stack_finding():
    return {"layer": "drawn", "kind": "stack-broken", "room": "bed", "over": "parlor",
            "id": "drawn:bed"}


class TestTheStackMove:
    def test_the_upper_room_takes_the_declared_size_of_the_room_below(self):
        plan = _stack_plan()
        res = MV.apply(STACK, plan, _stack_finding(), C)
        assert "refused" not in res, res
        bed = plan["levels"][1]["rooms"][0]
        assert (bed["width_ft"], bed["length_ft"]) == (13.0, 16.0)
        assert res["kind"] == "editorial" and "judgment" in res["log"]

    def test_it_refuses_where_the_room_below_is_outside_the_upper_rooms_own_band(self):
        plan = _stack_plan(below=(18.0, 26.0))          # 468 sf against a bedroom's 130-220
        res = MV.apply(STACK, plan, _stack_finding(), C)
        assert "refused" in res and "band" in res["refused"]
        assert plan == _stack_plan(below=(18.0, 26.0)), "a refusal wrote the record"

    def test_the_area_band_is_held_on_its_own(self):
        """14 x 16 is inside a bedroom's 11-14 ft width band and outside its 130-220 sf area band,
        so only the area guard can refuse it (the 18 x 26 fixture above is outside both, and the
        width guard alone kept it red under a mutation deleting the area guard)."""
        res = MV.apply(STACK, _stack_plan(below=(14.0, 16.0)), _stack_finding(), C)
        assert "refused" in res and "sf band" in res["refused"]

    def test_the_width_band_is_held_on_its_own(self):
        """10 x 13 is 130 sf and 1.3 : 1, inside a bedroom's area and proportion bands, and 10 ft
        wide against its 11 ft floor -- only the width guard can refuse it."""
        res = MV.apply(STACK, _stack_plan(below=(10.0, 13.0)), _stack_finding(), C)
        assert "refused" in res and "width band" in res["refused"]

    def test_it_refuses_past_the_upper_rooms_proportion_ceiling(self):
        plan = _stack_plan(below=(11.0, 19.0))          # 209 sf, 11 wide, 1.73 : 1 against 1.35
        res = MV.apply(STACK, plan, _stack_finding(), C)
        assert "refused" in res and "proportion" in res["refused"]

    def test_it_refuses_where_the_room_below_states_no_dimensions(self):
        plan = _stack_plan()
        del plan["levels"][0]["rooms"][0]["width_ft"]
        res = MV.apply(STACK, plan, _stack_finding(), C)
        assert "refused" in res and "states no declared" in res["refused"]

    def test_it_refuses_where_the_two_are_already_one_size(self):
        plan = _stack_plan(upper=(13.0, 16.0))
        res = MV.apply(STACK, plan, _stack_finding(), C)
        assert "refused" in res and "already" in res["refused"]

    def test_the_registry_answers_the_finding_and_the_critique_names_the_move(self):
        ans = [m["id"] for m in MV.answering(_stack_finding(), _stack_plan(), C)]
        assert ans == [STACK]
        move, why = CR._intended_move(_stack_plan(), _stack_finding())
        assert move == STACK and why is None

    def test_the_old_refusal_is_lifted_and_its_reason_is_kept_in_the_new_moves_note(self):
        reg = MV.registry()
        assert "align-upper-walls-to-the-room-below" not in {r["id"] for r in reg["refusals"]}
        m = MV.move(STACK)
        assert m["judgment"] is True and "align-upper-walls-to-the-room-below" in m["note"]
        assert "19 Nov 2026" in m["note"]


def _fire_plan(walls=("W", "N"), fire_wall="N", massing="four-over-four"):
    return {"id": "t", "style": "georgian-colonial-american", "massing": massing, "levels": [
        {"id": "g", "index": 0, "rooms": [
            {"id": "dining", "type": "dining-room", "width_ft": 14, "length_ft": 16,
             "exterior_walls": list(walls), "hearth": [{"wall": fire_wall}]}]}]}


def _fire_finding():
    return {"layer": "hearth", "kind": "hearth-off-the-stack-wall", "room": "dining",
            "id": "hearth:dining"}


class TestTheHearthMove:
    def test_the_fire_moves_to_the_one_flue_wall_the_room_declares(self):
        plan = _fire_plan()
        res = MV.apply(FIRE, plan, _fire_finding(), C)
        assert "refused" not in res, res
        assert plan["levels"][0]["rooms"][0]["hearth"] == [{"wall": "W"}]

    def test_it_refuses_where_the_room_declares_both_flue_walls(self):
        res = MV.apply(FIRE, _fire_plan(walls=("E", "W")), _fire_finding(), C)
        assert "refused" in res and "choosing" in res["refused"]

    def test_it_refuses_where_the_room_declares_no_flue_wall(self):
        res = MV.apply(FIRE, _fire_plan(walls=("N", "S"), fire_wall="N"), _fire_finding(), C)
        assert "refused" in res and "none of the flue walls" in res["refused"]

    def test_it_refuses_a_central_stack_and_a_plan_with_no_massing(self):
        res = MV.apply(FIRE, _fire_plan(massing="saltbox"), _fire_finding(), C)
        assert "refused" in res and "central" in res["refused"]
        plan = _fire_plan()
        del plan["massing"]
        res = MV.apply(FIRE, plan, _fire_finding(), C)
        assert "refused" in res and "names no massing" in res["refused"]

    def test_a_fire_already_on_a_flue_wall_is_not_moved(self):
        res = MV.apply(FIRE, _fire_plan(walls=("W", "N"), fire_wall="W"), _fire_finding(), C)
        assert "refused" in res and "already" in res["refused"]

    def test_the_critique_names_the_move_for_this_kind_only(self):
        assert CR._intended_move(_fire_plan(), _fire_finding())[0] == FIRE
        other = dict(_fire_finding(), kind="room-without-a-hearth")
        assert CR._intended_move(_fire_plan(), other)[0] is None

    def test_the_basis_is_a_sentence_really_in_the_hearth_reader(self):
        src = open(os.path.join(ROOT, "build", "hearths.py")).read()
        assert "The style's massing and kit govern the wall a fire stands on." in src
        assert MV.move(FIRE)["touches"] == ["levels[].rooms[].hearth[].wall"]


def _ref(cls, facts=("stacks",)):
    return {"kind": "type-fact-downgraded", "facts": list(facts), "conflicts": [], "lines": ["x"],
            "engine": "cp-sat", "status": None, "classes": {f: cls for f in facts}, "class": cls,
            "proven": cls == TF.PROVEN}


def _placed(claims=(), fires=()):
    return {"geometry_report": {"type_facts": {
        "stacks": {"claims": [dict(c) for c in claims]},
        "hearth": {"fires": [dict(f) for f in fires]}}}}


class TestTheGate:
    BROKEN = ({"room": "bed", "over": "parlor", "verdict": "broken"},
              {"room": "hall2", "over": "hall", "verdict": "kept"})

    def test_a_native_stacks_refusal_with_a_broken_claim_is_repaired_whatever_its_class(self):
        for cls in (TF.UNDECIDED, TF.SEARCH, TF.PROVEN):
            d = CO.repair_decision({"refused": _ref(cls), "nativity": "native"},
                                   _placed(self.BROKEN), "auto", None, 60.0)
            assert d["repair"] is True, (cls, d)
            assert [f["room"] for f in d["findings"]] == ["bed"], "a kept claim is not repaired"

    def test_bearing_and_tiling_have_no_move(self):
        d = CO.repair_decision({"refused": _ref(TF.UNDECIDED, ("bearing", "tiling")),
                                "nativity": "native"}, _placed(self.BROKEN), "auto", None, 60.0)
        assert d["repair"] is False and "bearing continuity or tiling" in d["why"]

    def test_only_a_native_diagram_is_repaired(self):
        for nat in ("borrowed", "lineage", None):
            d = CO.repair_decision({"refused": _ref(TF.UNDECIDED), "nativity": nat},
                                   _placed(self.BROKEN), "auto", None, 60.0)
            assert d["repair"] is False and "native" in d["why"]

    def test_the_search_by_name_is_not_repaired(self):
        d = CO.repair_decision({"refused": _ref(TF.UNDECIDED), "nativity": "native"},
                               _placed(self.BROKEN), "heuristic", None, 60.0)
        assert d["repair"] is False and "by name" in d["why"]

    def test_a_refusal_with_no_evidence_to_read_is_not_repaired(self):
        d = CO.repair_decision({"refused": _ref(TF.UNDECIDED), "nativity": "native"},
                               _placed(), "auto", None, 60.0)
        assert d["repair"] is False and "no broken claim" in d["why"]

    def test_a_repair_the_set_cannot_hold_is_refused_and_said(self):
        d = CO.repair_decision({"refused": _ref(TF.UNDECIDED), "nativity": "native"},
                               _placed(self.BROKEN), "auto", 50.0, 60.0)
        assert d["repair"] is False and d["why"].startswith("REPAIR NOT BEGUN")

    def test_a_house_that_is_not_refused_is_not_repaired(self):
        d = CO.repair_decision({"refused": None, "nativity": "native"}, _placed(self.BROKEN),
                               "auto", None, 60.0)
        assert d["repair"] is False and d["why"] == "not refused"

    def test_the_hearth_evidence_is_read_from_the_downgraded_fires_only(self):
        fires = ({"room": "dining", "verdict": TF.DOWNGRADED}, {"room": "parlor", "verdict": TF.HELD})
        fs = CO.repair_findings(_placed(fires=fires))
        assert [(f["kind"], f["room"]) for f in fs] == [("hearth-off-the-stack-wall", "dining")]

    def test_the_key_comparison_never_adopts_an_unjudged_key(self):
        assert CO._key_no_worse([1, 2, 3, 0], [1, 2, 4, 0])
        assert CO._key_no_worse([1, 2, 3, 0], [1, 2, 3, 0])
        assert not CO._key_no_worse([1, 3, 0, 0], [1, 2, 9, 0])
        assert not CO._key_no_worse(None, [1, 2, 3, 0])


def _brief():
    with open(os.path.join(ROOT, "briefs", "family-georgian.json")) as fh:
        return json.load(fh)


class TestTheComposerRepairs:
    TARGET = "centre-passage-double-pile"

    def _compose(self, compose_module, monkeypatch, first_class, repair_refused, repair_key):
        calls, applied_to = [], []
        orig = RV.revise

        def spy(plan, **kw):
            is_target = str(plan.get("id", "")).startswith(self.TARGET) and kw.get("place")
            kw = dict(kw, engine="heuristic")
            out = orig(plan, **kw)
            if is_target:
                calls.append(plan)
                gr = out["plan"].setdefault("geometry_report", {})
                n = len(calls)
                if n == 1:
                    gr["refused"] = copy.deepcopy(_ref(first_class))
                    gr.setdefault("type_facts", {})["stacks"] = {
                        "claims": [{"room": "x", "over": "y", "verdict": "broken"}]}
                    out["key_after"] = [2, 5, 5, 5]
                elif n == 2:
                    gr["refused"] = copy.deepcopy(_ref(TF.UNDECIDED)) if repair_refused else None
                    out["key_after"] = repair_key
                else:
                    gr["refused"] = None
            return out

        def fake_apply(plan, findings, C_):
            if not str(plan.get("id", "")).startswith(self.TARGET):
                # another candidate in the set the search also refused: not this test's subject
                return [], [{"move": STACK, "room": "-", "why": "not the target"}]
            applied_to.append((plan, findings))
            return ([{"move": STACK, "room": findings[0]["room"], "log": "Sized X to Y.",
                      "changed": [{"path": "p", "from": 1, "to": 2}]}], [])

        monkeypatch.setattr(RV, "revise", spy)
        monkeypatch.setattr(compose_module, "apply_repair", fake_apply)
        res = compose_module.compose(_brief(), candidates=4, revise=True, revise_rounds=0,
                                     revise_engine="auto", revise_budget_s=900)
        card = next((c for c in res["candidates"] if c["parti"] == self.TARGET), None)
        assert card is not None, [c["parti"] for c in res["candidates"]]
        assert card.get("nativity") == "native"
        return card, calls, applied_to

    def test_a_repair_that_places_replaces_the_record_and_no_retry_runs(self, compose_module,
                                                                        monkeypatch):
        card, calls, applied = self._compose(compose_module, monkeypatch, TF.UNDECIDED,
                                             repair_refused=False, repair_key=[1, 5, 5, 5])
        assert len(calls) == 2, f"placed {len(calls)} time(s)"
        assert calls[1] is applied[0][0], "the second placement was not of the repaired record"
        assert applied[0][1][0]["room"] == "x", "the repair did not read the refusal's evidence"
        rep = card["repair"]
        assert rep["repaired"] is True and rep["as_composed"] is False and rep["outcome"] == "placed"
        assert rep["moves"][0]["id"] == STACK
        assert card["retry"]["retry"] is False and "repaired record placed" in card["retry"]["why"]
        assert CO.placement_standing(card) == "placed"
        assert any(d.startswith("REPAIRED:") for d in card["decisions"])
        assert any(d.startswith("REPAIR PLACED") for d in card["decisions"])

    def test_a_refused_repair_falls_back_to_the_retry_on_the_record_as_composed(
            self, compose_module, monkeypatch):
        card, calls, applied = self._compose(compose_module, monkeypatch, TF.UNDECIDED,
                                             repair_refused=True, repair_key=[1, 5, 5, 5])
        assert len(calls) == 3, f"placed {len(calls)} time(s): repair, then the retry"
        assert calls[2] is not applied[0][0], "the retry ran on the repaired record"
        assert card["repair"]["outcome"] == "refused" and card["repair"]["as_composed"] is True
        assert card["retry"]["outcome"] == "placed"
        assert any(d.startswith("REPAIR REFUSED") for d in card["decisions"])

    def test_a_repair_judged_worse_is_discarded(self, compose_module, monkeypatch):
        card, calls, _ = self._compose(compose_module, monkeypatch, TF.UNDECIDED,
                                       repair_refused=False, repair_key=[3, 0, 0, 0])
        assert card["repair"]["outcome"] == "worse" and card["repair"]["repaired"] is False
        assert len(calls) == 3, "the retry did not run after a worse repair"

    def test_a_proven_refusal_is_repaired_and_never_retried(self, compose_module, monkeypatch):
        card, calls, _ = self._compose(compose_module, monkeypatch, TF.PROVEN,
                                       repair_refused=True, repair_key=[1, 5, 5, 5])
        assert len(calls) == 2, "a proven refusal is repaired once and not retried"
        assert card["repair"]["outcome"] == "refused"
        assert card["retry"]["retry"] is False and "proof" in card["retry"]["why"]
        assert CO.placement_standing(card) == "refused"
