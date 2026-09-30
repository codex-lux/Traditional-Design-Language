"""WP-16.5: the gable end draws what the resolved kit says of the cornice's return (R8, R8a), and
the cornice is one cornice at the envelope's depth (R9, R9a). Lucas's rulings of 29 Sep 2026.

R8: forbidden or `none` draws no band across the gable end, a stated return runs out and stops,
and silence keeps the band with the sheet saying so. R8a: a return runs as far as the cornice is
tall, the pork-chop fault's own rule, labelled a judgment, and the kit's 12-24 in band is noted as
written for an 11.7 in cornice. Until this package every gable end drew the eave cornice straight
across, whatever the kit said: 11 of the 41 drawn styles forbid the return.

R9: the envelope's depth (facade-classical's module/14) with Gibbs's shape: heights kept,
projections scaled. R9a: the bed mould's outer face held at 2 1/2 in, bed-mould-omitted's own
figure, a judgment. Until the ruling the face drew the envelope's depth and the inset the order's,
2.3 times apart.

What the corpus reaches is read on three shipped records, one per branch that matters: the
Tidewater house returns its cornice (its kit's full return is canonical), good-05 shows the end
profile (italian-renaissance-revival forbids the return), and the spec Colonial keeps the band
(colonial-revival permits a return and settles none). What it cannot reach is driven, each case
asserting its own premise.
"""
import copy
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import modcache as mc  # noqa: E402
import inkread as IR  # noqa: E402


def _m(name):
    return mc.load(name, os.path.join(ROOT, "build", name + ".py"))


RK = _m("resolve_kit")
EL = _m("elevation")
CORE = mc.load("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))

TIDEWATER = "plans/tidewater-georgian-careful.json"
GOOD05 = "plans/reference/good-05-lobby-gallery-mansion.json"
SPEC = "plans/spec-builder-colonial.json"


def _build(rel):
    G, ST, RF = _m("geometry"), _m("structure"), _m("roof")
    p = G.solve(json.load(open(os.path.join(ROOT, rel))), engine="heuristic")
    sec = ST.build_section(p, None, geometry_result=p)
    rf = RF.build_roof(p, None, section=sec)
    return EL.build_elevation(p, None, section=sec, roof=rf)


@pytest.fixture(scope="module")
def tide():
    return _build(TIDEWATER)


@pytest.fixture(scope="module")
def g05():
    return _build(GOOD05)


@pytest.fixture(scope="module")
def spec():
    return _build(SPEC)


def _slots(style):
    g = RK.load_graph()
    return RK.resolve_slots(g, RK.chain_for(g, style), RK.scope_for(g, style))[0]


def _svg(el, face, tmp_path, tag="g"):
    out = str(tmp_path / f"{tag}-{face}.svg")
    _m("render_elevation").render_elevation(el, out, face=face)
    ink = IR.Ink(open(out, encoding="utf-8").read())
    pl = next(f for f in ink.frames() if f.get("proj") == "elevation")
    said = [" ".join(t.split()).upper() for t, _a, _i in ink.texts() if t and t.strip()]
    return ink, pl, said


def _marks(ink, *classes):
    return [it for it in ink.items if all(c in it.classes for c in classes)]


# ------------------------------------------------------------------ the one reading of the return
class TestTheReading:
    def test_the_corpus_reaches_every_state_and_each_shipped_record_its_own(self):
        """Six states over the 164 nodes, each reached; and the three shipped records each read the
        state their own kit states. The premise of every drawn case below."""
        g = RK.load_graph()
        seen = {}
        for sid in sorted(g["nodes"]):
            slots, _ = RK.resolve_slots(g, RK.chain_for(g, sid), RK.scope_for(g, sid))
            seen.setdefault(RK.return_at(slots.get("cornice_return"))["state"], []).append(sid)
        assert set(seen) == {"forbidden", "none", "stated", "plain", "unsettled", "silent"}, sorted(seen)
        assert "tidewater-georgian" in seen["stated"]
        assert "italian-renaissance-revival" in seen["forbidden"]
        assert "colonial-revival" in seen["unsettled"]
        assert seen["plain"] == ["cape-cod-colonial"]

    def test_each_state_names_who_said_it(self):
        r = RK.return_at(_slots("tidewater-georgian")["cornice_return"])
        assert (r["state"], r["variant"], r["writers"]) == (
            "stated", "full-return-carrying-complete-profile", ["georgian-colonial-american"])
        assert (r["band_in"], r["band_by"]) == ([12.0, 24.0], "georgian-colonial-american")
        r = RK.return_at(_slots("italian-renaissance-revival")["cornice_return"])
        assert (r["state"], r["writers"]) == ("forbidden", ["italian-renaissance-revival"])
        r = RK.return_at(_slots("cape-cod-colonial")["cornice_return"])
        assert (r["state"], r["band_in"], r["band_by"], r["writers"]) == (
            "plain", [6.0, 12.0], "cape-cod-colonial", ["cape-cod-colonial"])
        r = RK.return_at(_slots("colonial-revival")["cornice_return"])
        assert (r["state"], r["writers"]) == ("unsettled", ["colonial-revival"])
        r = RK.return_at(_slots("new-england-colonial")["cornice_return"])
        assert (r["state"], r["writers"], r["dated"]) == ("none", ["new-england-colonial"], [[1620, 1700]])

    def test_a_band_a_descendant_restates_is_the_descendants(self):
        """greek-revival-upland-vernacular restates the return's depth at 10-18 in, measured, from
        its own `typical_ratios`, in an `extends` delta; the canonical row stays the ancestor's. The
        band is named by ITS writer: reading the slot's binder named georgian-colonial-american."""
        rec = _slots("greek-revival-upland-vernacular")["cornice_return"]
        assert rec["_bound_by"] == "georgian-colonial-american"      # the premise
        r = RK.return_at(rec)
        assert (r["state"], r["writers"]) == ("stated", ["georgian-colonial-american"])
        assert (r["band_in"], r["band_by"]) == ([10.0, 18.0], "greek-revival-upland-vernacular")

    def test_a_dated_none_is_read_at_the_house_date_and_an_undated_house_keeps_it(self):
        rec = {"binding": "specified", "_bound_by": "a",
               "variants": [{"id": "none", "status": "canonical", "_written_by": "a",
                             "applies_when": {"date_range": [1620, 1700]}},
                            {"id": "full-return", "status": "canonical", "_written_by": "b",
                             "applies_when": {"date_range": [1701, 1850]}}]}
        r = RK.return_at(rec, 1650)
        assert (r["state"], r["dated"], r["date_unstated"]) == ("none", [[1620, 1700]], False)
        r = RK.return_at(rec, 1750)
        assert (r["state"], r["variant"], r["writers"]) == ("stated", "full-return", ["b"])
        # undated: both rows apply, and the refusal wins, because drawing what the record may rule
        # out is the worse of the two errors (A3, one slot over), and the sheet says the date is unstated
        r = RK.return_at(rec, None)
        assert (r["state"], r["date_unstated"]) == ("none", True)

    def test_a_record_that_says_nothing_is_silent_and_a_permitted_one_unsettled(self):
        assert RK.return_at(None)["state"] == "silent"
        assert RK.return_at({"binding": "open", "status": "empty"})["state"] == "silent"
        rec = {"binding": "specified", "_bound_by": "x",
               "variants": [{"id": "full-return", "status": "permitted", "_written_by": "x"}]}
        assert RK.return_at(rec)["state"] == "unsettled"
        # a band with no unit in inches is not a return depth this reader may draw
        rec["parameters"] = {"return_depth": {"range": [6, 12], "unit": "ft"}}
        assert RK.return_at(rec)["state"] == "unsettled"
        rec["parameters"] = {"return_depth": {"range": [6, 12], "unit": "in"}}
        assert RK.return_at(rec)["state"] == "plain"


class TestWhoWroteEachParameter:
    """`_param_writers` (WP-16.5), as `_written_by` says it of each row: `_extends` records only the
    last merge step, so it cannot say which of several deltas stated a figure."""

    def test_a_delta_takes_the_figures_it_restates_and_leaves_the_rest(self):
        base = {"binding": "specified", "parameters": {"a": {"value": 1}, "b": {"value": 2}},
                "_param_writers": {"a": "root", "b": "root"}}
        out, _ = RK.merge_extends(base, {"parameters": {"a": {"value": 9}}}, "root", "child")
        assert out["_param_writers"] == {"a": "child", "b": "root"}
        out2, _ = RK.merge_extends(out, {"parameters": {"c": {"value": 3}}}, "child", "grandchild")
        assert out2["_param_writers"] == {"a": "child", "b": "root", "c": "grandchild"}
        assert out2["_extends"]["delta_from"] == "grandchild"   # what the last step alone records

    def test_a_base_merged_without_writers_credits_its_own_source(self):
        out, _ = RK.merge_extends({"binding": "specified", "parameters": {"a": {"value": 1}}},
                                  {"parameters": {"b": {"value": 2}}}, "root", "child")
        assert out["_param_writers"] == {"a": "root", "b": "child"}

    def test_every_resolved_parameter_names_a_writer_in_its_chain_that_states_it(self):
        g = RK.load_graph()
        checked = 0
        for sid in ("greek-revival-upland-vernacular", "tidewater-georgian", "cape-cod-colonial",
                    "federal-style"):
            chain = RK.chain_for(g, sid)
            slots, _ = RK.resolve_slots(g, chain, RK.scope_for(g, sid))
            for slot, rec in slots.items():
                for k in rec.get("parameters") or {}:
                    w = (rec.get("_param_writers") or {}).get(k)
                    assert w and w.replace(" (inline)", "") in chain, (sid, slot, k, w)
                    own = (RK.load_kit(w.replace(" (inline)", "")) or {}).get(slot) or \
                        ((g["nodes"][w.replace(" (inline)", "")].get("kit") or {}).get(slot) or {})
                    assert k in (own.get("parameters") or {}), (sid, slot, k, w)
                    checked += 1
        assert checked > 50


# ------------------------------------------------------------------ which faces are gable ends
class TestTheGableFaces:
    @pytest.mark.parametrize("form,axis,want", [
        ("side-gable", "x", ("W", "E")), ("gable", "x", ("W", "E")), ("front-gable", "y", ("S", "N")),
        ("gambrel", "x", ("W", "E")), ("hip", "x", ()), ("gable-on-hip", "x", ()),
        ("mansard", "x", None), ("side-gable", None, None), ("pyramid", "x", None)])
    def test_the_roof_records_own_form_decides(self, form, axis, want):
        assert EL.gable_faces({"main": {"form": form, "ridge": {"axis": axis}}}) == want

    def test_the_shipped_records_are_side_gabled(self, tide, g05, spec):
        for el in (tide, g05, spec):
            assert EL.gable_faces(el["roof_record"]) == ("W", "E")


# ------------------------------------------------------------------ what each state draws and says
class TestTheWords:
    def test_the_rule_the_length_is_read_from_is_the_pork_chop_faults_own(self):
        f, field, quote = EL.RETURN_LENGTH_BASIS
        rec = json.load(open(os.path.join(ROOT, f)))
        assert field == "test.note" and quote in rec["test"]["note"]

    def test_the_band_note_is_the_stunted_return_faults_own_words(self):
        f, field, quote = EL.RETURN_BAND_BASIS
        note = json.load(open(os.path.join(ROOT, f)))["test"]["note"]
        assert field == "test.note" and quote in note
        m = re.search(r"cornice height of ([\d.]+) in .* documented (\d+)-(\d+) in", quote)
        assert float(m.group(1)) == EL.RETURN_BAND_WRITTEN_FOR_CORNICE_IN
        assert (float(m.group(2)), float(m.group(3))) == EL.RETURN_BAND_DOCUMENTED_IN

    def test_a_stated_return_is_the_cornice_height_and_a_judgment(self, tide):
        cr = tide["cornice_return"]
        cor_h = tide["eave_cornice"]["cornice_height_in"]
        assert (cr["state"], cr["draws"], cr["gable_faces"]) == ("stated", "return", ["W", "E"])
        assert cr["length_in"] == cor_h and cr["length_judgment"] is True
        assert cr["length_basis"] == EL.RETURN_LENGTH_BASIS
        assert cr["words"] == (
            f"CORNICE RETURNED {cor_h:.1f} IN AT EACH CORNER, AS FAR AS THE CORNICE IS TALL (THE "
            "PORK-CHOP FAULT'S RULE) — A JUDGMENT; GEORGIAN-COLONIAL-AMERICAN'S KIT STATES 12–24 IN, A "
            "BAND WRITTEN FOR AN 11.7 IN CORNICE")

    def test_another_band_is_named_by_its_writer_and_not_called_the_documented_one(self):
        rd = RK.return_at(_slots("greek-revival-upland-vernacular")["cornice_return"])
        cr = EL.cornice_return(rd, {"cornice_height_in": 20.0},
                               {"main": {"form": "side-gable", "ridge": {"axis": "x"}}})
        assert "GREEK-REVIVAL-UPLAND-VERNACULAR'S KIT STATES 10–18 IN" in cr["words"]
        assert "11.7" not in cr["words"] and "GEORGIAN-COLONIAL-AMERICAN" not in cr["words"]

    def test_a_forbidden_return_says_who_forbade_it(self, g05):
        cr = g05["cornice_return"]
        assert (cr["state"], cr["draws"], cr["length_in"]) == ("forbidden", "end-profile", None)
        assert cr["words"].startswith("NO CORNICE RETURN — FORBIDDEN BY ITALIAN-RENAISSANCE-REVIVAL")
        assert "THE WALL RUNS UP TO THE RAKE" in cr["words"]

    def test_an_unsettled_return_keeps_the_band_and_says_so(self, spec):
        cr = spec["cornice_return"]
        assert (cr["state"], cr["draws"], cr["length_in"]) == ("unsettled", "band", None)
        proj = spec["eave_cornice"]["envelope_projection_in"]
        assert cr["words"] == ("RETURN UNSTATED — COLONIAL-REVIVAL'S KIT PERMITS ONE ONLY OVER A "
                               f"CORNICE OF AT LEAST 10 IN, AND THIS ONE PROJECTS {proj:.1f} IN; THE "
                               "CORNICE IS DRAWN ACROSS THE GABLE END")

    ROOF = {"main": {"form": "side-gable", "ridge": {"axis": "x"}}}

    def test_a_plain_return_is_the_middle_of_its_own_band(self):
        rd = RK.return_at(_slots("cape-cod-colonial")["cornice_return"])
        cr = EL.cornice_return(rd, {"cornice_height_in": 12.0}, self.ROOF)
        assert (cr["draws"], cr["length_in"], cr["length_judgment"]) == ("plain-return", 9.0, True)
        assert cr["words"] == ("PLAIN RETURN 9 IN AT EACH CORNER, THE MIDDLE OF CAPE-COD-COLONIAL'S OWN "
                               "6–12 IN — A JUDGMENT")

    def test_a_dated_none_says_the_date_it_was_read_at_or_that_none_is_stated(self):
        rd = {"state": "none", "writers": ["new-england-colonial"], "dated": [[1620, 1700]],
              "date": None, "date_unstated": True}
        cr = EL.cornice_return(rd, {"cornice_height_in": 12.0}, self.ROOF)
        assert cr["draws"] == "end-profile"
        assert "FOR HOUSES OF 1620–1700; THIS RECORD STATES NO DATE, SO NONE IS DRAWN" in cr["words"]
        cr = EL.cornice_return(dict(rd, date=1690, date_unstated=False), {"cornice_height_in": 12.0}, self.ROOF)
        assert "FOR HOUSES OF 1620–1700, AND THIS HOUSE IS DATED 1690" in cr["words"]

    def test_silence_and_an_unread_kit_keep_the_band_each_in_its_own_words(self):
        cr = EL.cornice_return({"state": "silent"}, {"cornice_height_in": 12.0}, self.ROOF)
        assert cr["draws"] == "band" and "THE KIT SAYS NOTHING OF IT" in cr["words"]
        cr = EL.cornice_return({"state": "unjudged"}, {"cornice_height_in": 12.0}, self.ROOF)
        assert cr["draws"] == "band" and cr["words"].startswith("RETURN UNJUDGED")

    def test_a_roof_whose_form_is_not_modelled_is_unjudged_and_never_no_gable(self):
        cr = EL.cornice_return({"state": "stated", "writers": ["x"]}, {"cornice_height_in": 12.0},
                               {"main": {"form": "mansard", "ridge": {"axis": "x"}}})
        assert (cr["gable_faces"], cr["draws"]) == (None, "band")
        assert cr["words"].startswith("GABLE ENDS UNJUDGED")

    def test_no_cornice_no_return(self):
        for cornice in ({}, {"cornice_height_in": None}, {"cornice_height_in": 12.0,
                                                           "cornice_refused_by": {"writers": ["x"]}}):
            cr = EL.cornice_return({"state": "stated", "writers": ["x"]}, cornice, self.ROOF)
            assert (cr["draws"], cr["words"]) == ("nothing", None)


class TestTheRecordsOwnCondition:
    """colonial-revival's c04 permits a return "only where the eave carries a full classical cornice
    of at least 10 in. projection", as `min_cornice_projection_for_return`, and six nodes receive it
    through the cascade. The cornice this elevation draws is the envelope's, 8.61 in on the spec
    Colonial. The words said the kit "PERMITS ONE" there, which its own condition does not; they say
    the condition and the drawn figure now. Whether a failed condition is a ban is not ruled, so the
    drawing does not move on it."""
    ROOF = {"main": {"form": "side-gable", "ridge": {"axis": "x"}}}
    READING = {"state": "unsettled", "writers": ["colonial-revival"], "min_cornice_in": 10.0,
               "min_cornice_by": "colonial-revival"}

    def test_the_condition_is_read_with_its_writer(self):
        for sid in ("colonial-revival", "georgian-revival", "new-classical"):
            r = RK.return_at(_slots(sid)["cornice_return"])
            assert (r["state"], r["min_cornice_in"], r["min_cornice_by"]) == (
                "unsettled", 10.0, "colonial-revival"), sid
        r = RK.return_at(_slots("new-urbanist-traditional")["cornice_return"])
        assert (r["state"], r["min_cornice_in"], r["min_cornice_by"]) == ("unsettled", None, None)
        # a figure in another unit is not a projection this reader may compare
        rec = {"binding": "specified", "_bound_by": "x",
               "variants": [{"id": "r", "status": "permitted", "_written_by": "x"}],
               "parameters": {"min_cornice_projection_for_return": {"value": 1, "unit": "ft"}}}
        assert RK.return_at(rec)["min_cornice_in"] is None

    def test_the_sheet_says_the_condition_and_the_drawn_figure_both_ways(self):
        below = EL.cornice_return(self.READING, {"cornice_height_in": 20.0,
                                                 "envelope_projection_in": 8.612}, self.ROOF)
        assert below["condition"] == {"min_cornice_projection_in": 10.0, "by": "colonial-revival",
                                      "cornice_projection_in": 8.612, "met": False}
        assert ("PERMITS ONE ONLY OVER A CORNICE OF AT LEAST 10 IN, AND THIS ONE PROJECTS 8.6 IN"
                in below["words"])
        above = EL.cornice_return(self.READING, {"cornice_height_in": 20.0,
                                                 "envelope_projection_in": 11.481}, self.ROOF)
        assert above["condition"]["met"] is True
        assert ("PERMITS ONE OVER A CORNICE OF AT LEAST 10 IN, AS THIS ONE IS (11.5 IN), AND SETTLES "
                "NONE" in above["words"])
        unknown = EL.cornice_return(self.READING, {"cornice_height_in": 20.0}, self.ROOF)
        assert unknown["condition"]["met"] is None
        assert "AND NO RECORD STATES THIS ONE'S PROJECTION" in unknown["words"]
        # and the drawing is not changed by it, in any of the three
        assert {c["draws"] for c in (below, above, unknown)} == {"band"}

    def test_a_condition_another_node_wrote_is_named_by_it(self):
        cr = EL.cornice_return(dict(self.READING, min_cornice_by="y-style"),
                               {"cornice_height_in": 20.0, "envelope_projection_in": 8.0}, self.ROOF)
        assert ("COLONIAL-REVIVAL'S KIT PERMITS ONE, AND Y-STYLE'S ONLY OVER A CORNICE OF AT LEAST "
                "10 IN, AND THIS ONE PROJECTS 8.0 IN" in cr["words"])

    def test_one_shipped_record_fails_it_one_meets_it_and_one_states_none(self, spec):
        assert spec["cornice_return"]["condition"]["met"] is False
        g07 = _build("plans/reference/good-07-diamond-plan-house.json")["cornice_return"]
        assert (g07["draws"], g07["condition"]["met"]) == ("band", True)
        b03 = _build("plans/reference/bad-03-narrow-lot-townhome.json")["cornice_return"]
        assert (b03["draws"], b03["condition"]) == ("band", None)
        assert b03["words"].endswith("PERMITS ONE AND SETTLES NONE; THE CORNICE IS DRAWN ACROSS THE "
                                     "GABLE END")


# ------------------------------------------------------------------ the marks both surfaces draw
class TestTheMarks:
    def test_a_stated_return_runs_out_from_each_corner_and_stops(self, tide):
        cor = tide["eave_cornice"]
        b = cor["envelope_projection_in"] / 12.0
        L = tide["cornice_return"]["length_in"] / 12.0
        for face in ("W", "E"):
            cm = EL.cornice_marks(tide, face)
            span = cm["span_ft"]
            assert (cm["role"], cm["gable_draws"], cm["frieze"], cm["cornice"]) == ("gable", "return", None, None)
            assert [r["side"] for r in cm["returns"]] == ["left", "right"]
            left, right = cm["returns"]
            assert abs(left["cornice"]["u0"] + b) < 1e-9 and abs(left["cornice"]["u1"] - L) < 1e-9
            assert abs(right["cornice"]["u0"] - (span - L)) < 1e-9 and abs(right["cornice"]["u1"] - (span + b)) < 1e-9
            assert not left["plain"] and not right["plain"]
            assert [(w["u0"], w["u1"]) for w in cm["wall_to_rake"]] == [(L, span - L)]
            assert cm["teeth"] is None and not cm["end_profiles"]
            assert tide["cornice_return"]["words"] in cm["notes"]

    def test_the_eave_turns_the_corner_where_the_gable_carries_something_round_it(self, tide, g05, spec):
        for el, turns in ((tide, True), (spec, True), (g05, False)):
            b = el["eave_cornice"]["envelope_projection_in"] / 12.0
            for face in ("S", "N"):
                cm = EL.cornice_marks(el, face)
                assert cm["role"] == "eave" and not cm["returns"] and not cm["end_profiles"]
                co = cm["cornice"]
                assert abs(co["u0"] - (-b if turns else 0.0)) < 1e-9, (el["style"], face)
                assert abs(co["u1"] - (cm["span_ft"] + (b if turns else 0.0))) < 1e-9
                assert el["cornice_return"]["words"] not in cm["notes"]

    def test_a_forbidden_return_shows_the_end_profile_and_the_wall_runs_to_the_rake(self, g05):
        for face in ("W", "E"):
            cm = EL.cornice_marks(g05, face)
            assert (cm["gable_draws"], cm["frieze"], cm["cornice"], cm["returns"]) == ("end-profile", None, None, [])
            ends = cm["end_profiles"]
            assert [(e["side"], e["at_u"], e["outward"]) for e in ends] == [
                ("left", 0.0, -1), ("right", cm["span_ft"], 1)]
            assert [(w["u0"], w["u1"]) for w in cm["wall_to_rake"]] == [(0.0, cm["span_ft"])]

    def test_an_unsettled_return_draws_the_band_across_and_says_the_return_is_unstated(self, spec):
        b = spec["eave_cornice"]["envelope_projection_in"] / 12.0
        for face in ("W", "E"):
            cm = EL.cornice_marks(spec, face)
            assert (cm["role"], cm["gable_draws"]) == ("gable", "band")
            assert abs(cm["cornice"]["u0"] + b) < 1e-9 and not cm["returns"] and not cm["end_profiles"]
            assert any(n.startswith("RETURN UNSTATED") for n in cm["notes"])

    def test_a_hipped_roof_has_no_gable_end_and_the_eave_turns_every_corner(self, tide):
        el = copy.deepcopy(tide)
        el["roof_record"]["main"]["form"] = "hip"
        el["cornice_return"] = EL.cornice_return(
            RK.return_at(_slots("italian-renaissance-revival")["cornice_return"]),
            el["eave_cornice"], el["roof_record"])
        assert el["cornice_return"]["gable_faces"] == []           # the premise: no gable end
        b = el["eave_cornice"]["envelope_projection_in"] / 12.0
        for face in ("S", "N", "E", "W"):
            cm = EL.cornice_marks(el, face)
            assert cm["role"] == "eave" and abs(cm["cornice"]["u0"] + b) < 1e-9, face

    def test_a_return_lays_whole_teeth_along_its_own_run(self, tide):
        """No pack states a tooth width, so every band on every return is refused solid and said;
        a stated width is driven here, and each return carries whole teeth inside its own box."""
        el = copy.deepcopy(tide)
        band = next(m for m in el["eave_cornice"]["members"] if m.get("profile") in EL.TOOTHED_PROFILES)
        assert band.get("spacing_in") and not band.get("width_in")          # the premise
        band["width_in"] = band["spacing_in"] / 3.0
        cm = EL.cornice_marks(el, "W")
        for r in cm["returns"]:
            t = r["teeth"]
            assert t and not t["solid"] and t["teeth"], r["side"]
            box = r["cornice"]
            for tooth in t["teeth"]:
                assert box["u0"] - 1e-6 <= tooth["u0"] < tooth["u1"] <= box["u1"] + 1e-6
                assert abs((tooth["u1"] - tooth["u0"]) * 12.0 - band["width_in"]) < 1e-3
        assert cm["teeth"] is None

    def test_a_plain_return_carries_no_members(self, tide):
        el = copy.deepcopy(tide)
        el["cornice_return"] = EL.cornice_return(
            RK.return_at(_slots("cape-cod-colonial")["cornice_return"]), el["eave_cornice"], el["roof_record"])
        cm = EL.cornice_marks(el, "W")
        assert cm["gable_draws"] == "plain-return"
        assert all(r["plain"] and r["teeth"] is None for r in cm["returns"])
        assert all(abs(r["length_ft"] - 0.75) < 1e-12 for r in cm["returns"])


# ------------------------------------------------------------------ what the faults may read
class TestTheMeasurements:
    NAMES = ("count_of_cornice_returns_drawn_at_the_gable_ends",
             "count_of_moulding_profiles_carried_around_onto_the_return",
             "count_of_horizontal_moulding_members_returning_onto_the_gable_wall")

    def test_a_drawn_return_is_counted_and_never_measured(self, tide):
        m = tide["measurements"]
        n = len(tide["eave_cornice"]["members"])
        assert [m.get(k) for k in self.NAMES] == [4, n, n]
        for k in ("return_projection_from_wall_in", "return_length_along_gable_wall_in",
                  "rake_overhang_in", "bed_mould_projection_in"):
            assert k not in m and EL.NOT_MODELLED.get(k), k

    def test_a_forbidden_return_is_a_measured_zero(self, g05):
        m = g05["measurements"]
        assert m["count_of_cornice_returns_drawn_at_the_gable_ends"] == 0
        assert m["count_of_horizontal_moulding_members_returning_onto_the_gable_wall"] == 0
        assert "count_of_moulding_profiles_carried_around_onto_the_return" not in m

    def test_an_unstated_return_is_not_measured_at_all(self, spec):
        m = spec["measurements"]
        assert not [k for k in self.NAMES if k in m]


class TestTheFaults:
    GATE = {"expression": "count_of_cornice_returns_drawn_at_the_gable_ends", "direction": "at-least",
            "threshold": 1}

    def _tests(self, fid):
        d = json.load(open(os.path.join(ROOT, "faults", fid + ".json")))
        return [d["test"]] + list(d.get("secondary_tests") or []) + \
            [e["bounds_test"] for e in d.get("exceptions") or [] if e.get("bounds_test")]

    @pytest.mark.parametrize("fid", ["pork-chop-return", "return-shallower-than-tall"])
    def test_a_return_fault_is_gated_on_a_drawn_return_at_every_test(self, fid):
        tests = self._tests(fid)
        assert len(tests) >= 6
        for t in tests:
            aw = t.get("applies_when") or {}
            assert {k: aw.get(k) for k in self.GATE} == self.GATE, (fid, t["expression"])

    def test_the_fault_about_a_return_that_is_never_there_is_not_gated(self):
        """R8 leaves `return-that-never-returns` ungated (WP-16.2): a house with no return is its
        subject, and gating it on a drawn return would make it unable to fire."""
        assert not [t for t in self._tests("return-that-never-returns") if t.get("applies_when")]

    def _state(self, el, fid):
        r = CORE.check_measurements(el["measurements"], style=el["style"], limit=10**6)
        for state, key in (("present", "faults_present"), ("clear", "faults_clear"),
                           ("needed", "could_not_judge"), ("not_applicable", "not_applicable")):
            if any(x["fault"] == fid for x in r[key]):
                return state
        return None

    def test_the_verdicts_on_the_three_records(self, tide, g05, spec):
        # a return drawn to R8a's rule cannot be judged against that rule: its length is a
        # judgment, withheld, so the governing test cannot run
        assert self._state(tide, "pork-chop-return") == "needed"
        assert self._state(tide, "return-shallower-than-tall") == "needed"
        assert self._state(tide, "return-that-never-returns") == "clear"
        # no return is drawn, so a fault about how a return is proportioned does not arise
        assert self._state(g05, "pork-chop-return") == "not_applicable"
        assert self._state(g05, "return-shallower-than-tall") == "not_applicable"
        # and the fault about a missing return convicts the gable end its roof layer drew
        assert self._state(g05, "return-that-never-returns") == "present"
        for fid in ("pork-chop-return", "return-shallower-than-tall", "return-that-never-returns"):
            assert self._state(spec, fid) == "needed", fid

    def test_a_rake_that_is_not_modelled_convicts_nobody(self, tide):
        """Until WP-16.5 the elevation published the CORNICE's projection as `rake_overhang_in`,
        and flush-rake convicted eleven shipped plans on it. The roof record models no rake."""
        assert "rake_overhang_in" not in tide["measurements"]
        assert self._state(tide, "flush-rake") == "needed"


# ------------------------------------------------------------------ the ink, on the sheet and in the DXF
class TestTheSheet:
    def test_a_returned_gable_draws_two_returns_their_members_and_the_wall_to_the_rake(self, tide, tmp_path):
        ink, pl, said = _svg(tide, "W", tmp_path)
        n = len(tide["eave_cornice"]["members"])
        boxes = [it for it in _marks(ink, "bd", "w-prof") if it.tag == "rect"]
        assert sorted(it.attrs.get("data-return") for it in boxes) == ["left", "right"]
        lines = _marks(ink, "cm")
        assert len(lines) == 2 * (n - 1) and all(it.attrs.get("data-return") for it in lines)
        walls = _marks(ink, "wf")
        assert len(walls) == 1 and walls[0].tag == "polygon" and walls[0].attrs.get("data-wall-to-rake")
        # the gable's triangle is wall, the roof its rake, and no shingle courses the wall
        assert _marks(ink, "rf", "gw") and _marks(ink, "rk") and not _marks(ink, "shingle")
        assert any(ln.startswith("CORNICE RETURNED 24.6 IN AT EACH CORNER") for ln in said)
        assert not any("NO CORNICE DRAWN" in ln for ln in said)

    def test_the_returns_stand_where_the_record_puts_them(self, tide, tmp_path):
        ink, pl, _said = _svg(tide, "E", tmp_path)
        cm = EL.cornice_marks(tide, "E")
        for it in [it for it in _marks(ink, "bd", "w-prof") if it.tag == "rect"]:
            r = next(r for r in cm["returns"] if r["side"] == it.attrs["data-return"])
            b = it.bbox()
            (u0, h0), (u1, h1) = IR.to_model(pl, b[0], b[3]), IR.to_model(pl, b[2], b[1])
            for got, want in ((min(u0, u1), r["cornice"]["u0"]), (max(u0, u1), r["cornice"]["u1"]),
                              (min(h0, h1), r["cornice"]["h0"]), (max(h0, h1), r["cornice"]["h1"])):
                assert abs(got - want) < 0.03, (it.attrs["data-return"], got, want)

    def test_a_forbidden_return_draws_two_end_profiles_and_no_band(self, g05, tmp_path):
        ink, pl, said = _svg(g05, "E", tmp_path)
        ends = [it for it in _marks(ink, "bd", "w-prof") if it.tag == "path"]
        assert sorted(it.attrs.get("data-end-profile") for it in ends) == ["left", "right"]
        assert not [it for it in _marks(ink, "bd", "w-prof") if it.tag == "rect"]
        cm = EL.cornice_marks(g05, "E")
        left, right = sorted(ends, key=lambda it: it.bbox()[0])
        lu = IR.to_model(pl, left.bbox()[2], 0)[0]
        ru = IR.to_model(pl, right.bbox()[0], 0)[0]
        assert abs(lu - 0.0) < 0.03 and abs(ru - cm["span_ft"]) < 0.03   # each stands out from its corner
        assert any(ln.startswith("NO CORNICE RETURN — FORBIDDEN BY ITALIAN-RENAISSANCE-REVIVAL")
                   for ln in said)
        assert any("SEE INSET FOR PROFILE" in ln for ln in said)

    def test_an_unstated_return_draws_the_band_and_the_wall_to_its_eave(self, spec, tmp_path):
        ink, pl, said = _svg(spec, "W", tmp_path)
        assert [it.tag for it in _marks(ink, "wf")] == ["rect"]
        assert not [it for it in ink.items if it.attrs.get("data-return") or it.attrs.get("data-end-profile")]
        assert any(ln.startswith("RETURN UNSTATED — COLONIAL-REVIVAL'S KIT") for ln in said)


class TestTheDxf:
    def _dxf(self, el, face, tmp_path):
        ezdxf = pytest.importorskip("ezdxf")
        path = str(tmp_path / f"e-{face}.dxf")
        _m("export_dxf").export_elevation_dxf(el, path, face=face)
        return ezdxf.readfile(path).modelspace()

    @staticmethod
    def _x(e):
        try:
            return "".join(str(v) for _c, v in e.get_xdata("TDL"))
        except Exception:   # noqa: BLE001 -- no XDATA is an answer here
            return ""

    def test_a_return_is_said_to_be_a_judgment_in_the_cad_file_too(self, tide, tmp_path):
        msp = self._dxf(tide, "W", tmp_path)
        rets = [e for e in msp.query("LWPOLYLINE") if "TDL::return" in self._x(e)]
        assert len(rets) == 4                          # frieze and cornice, at each corner
        for e in rets:
            x = self._x(e)
            assert '"judgment":true' in x and '"length_in":24.558' in x, x
        walls = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-WALL"]
        assert len(walls) == 1 and '"to_the_rake":true' in self._x(walls[0])
        members = [e for e in msp.query("LINE") if e.dxf.layer == "TDL-ELEV-CORNICE-MEMBER"]
        n = len(tide["eave_cornice"]["members"])
        assert len(members) == 2 * (n - 1) and all('"return"' in self._x(e) for e in members)

    def test_the_left_end_profile_is_the_right_one_mirrored_bulge_for_bulge(self, g05, tmp_path):
        msp = self._dxf(g05, "E", tmp_path)
        ends = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "TDL-ELEV-CORNICE-END"]
        assert len(ends) == 2
        by = {}
        for e in ends:
            side = re.search(r'"side":"(\w+)"', self._x(e)).group(1)
            by[side] = list(e.get_points("xyb"))
        span = EL.cornice_marks(g05, "E")["span_ft"] * 12.0
        assert len(by["left"]) == len(by["right"]) and any(abs(b) > 1e-9 for _x, _y, b in by["right"])
        for (lx, ly, lb), (rx, ry, rb) in zip(by["left"], by["right"]):
            assert abs(lx - (span - rx)) < 1e-6 and abs(ly - ry) < 1e-6 and abs(lb + rb) < 1e-9


# ------------------------------------------------------------------ R9 and R9a: one cornice
class TestOneCornice:
    def test_the_bed_mould_figure_is_the_faults_own_words(self):
        f, expr, quote = EL.BED_MOULD_BASIS
        rec = json.load(open(os.path.join(ROOT, f)))
        t = next(t for t in rec["secondary_tests"] if t["expression"] == expr)
        assert quote in t["note"]
        m = re.search(r"gives (\d+) (\d)/(\d)\b", quote)
        assert int(m.group(1)) + int(m.group(2)) / int(m.group(3)) == EL.BED_MOULD_PROJECTION_IN

    MEMBERS = [{"id": "c_bed_fillet", "height_in": 1.0, "projection_in": 3.0},
               {"id": "c_bed_ovolo", "height_in": 2.0, "projection_in": 4.0},
               {"id": "c_corona", "height_in": 4.0, "projection_in": 16.0},
               {"id": "c_unpublished", "height_in": 1.0, "projection_in": None},
               {"id": "c_crown", "height_in": 3.0, "projection_in": 20.0}]

    def test_heights_kept_the_bed_held_and_the_greatest_relief_on_the_envelope(self):
        out, how = EL.scale_into_envelope(self.MEMBERS, 10.0, naked_in=0.0)
        assert how["mode"] == "bed-mould-held" and how["order_relief_in"] == 20.0
        assert [m["height_in"] for m in out] == [m["height_in"] for m in self.MEMBERS]
        assert [m["order_projection_in"] for m in out] == [m["projection_in"] for m in self.MEMBERS]
        p = {m["id"]: m["projection_in"] for m in out}
        assert p["c_bed_ovolo"] == EL.BED_MOULD_PROJECTION_IN and p["c_crown"] == 10.0
        assert p["c_unpublished"] is None
        # the order's shape: the order of the reliefs is kept, and the members above the bed share
        # the rest of the depth in the order's own proportions
        assert p["c_bed_fillet"] < p["c_bed_ovolo"] < p["c_corona"] < p["c_crown"]
        assert abs((p["c_corona"] - 2.5) / (p["c_crown"] - 2.5) - (16.0 - 4.0) / (20.0 - 4.0)) < 1e-9

    def test_the_naked_is_the_datum(self):
        out, how = EL.scale_into_envelope(
            [dict(m, projection_in=None if m["projection_in"] is None else m["projection_in"] + 7.0)
             for m in self.MEMBERS], 10.0, naked_in=7.0)
        assert how["mode"] == "bed-mould-held"
        assert {m["id"]: m["projection_in"] for m in out}["c_crown"] == 17.0

    def test_where_nothing_can_be_held_one_factor_scales_every_relief_and_says_why(self):
        out, how = EL.scale_into_envelope(self.MEMBERS, 2.0)
        assert how["mode"] == "uniform" and "no deeper than the bed mould" in how["why"]
        assert {m["id"]: m["projection_in"] for m in out}["c_crown"] == 2.0
        no_bed = [m for m in self.MEMBERS if "bed" not in m["id"]]
        out, how = EL.scale_into_envelope(no_bed, 10.0)
        assert how["mode"] == "uniform" and "no bed mould" in how["why"]
        assert EL.scale_into_envelope(self.MEMBERS, None)[1]["mode"] == "not-scaled"

    def test_the_shipped_cornice_projects_the_envelope_in_the_orders_shape(self, tide):
        cor = tide["eave_cornice"]
        naked = cor["frieze_naked_in"]
        pub = [m["projection_in"] - naked for m in cor["members"] if m.get("projection_in") is not None]
        assert abs(max(pub) - cor["envelope_projection_in"]) < 1e-3
        assert cor["order_relief_beyond_frieze_in"] == cor["envelope_projection_in"]
        assert cor["order_own_relief_in"] > 2 * cor["envelope_projection_in"]    # what was scaled
        assert (cor["bed_mould_projection_in"], cor["bed_mould_projection_judgment"]) == (2.5, True)
        assert cor["projection_scaling"]["mode"] == "bed-mould-held"
        assert "bed_mould_projection_in" not in tide["measurements"]

    def test_gibbs_equality_is_said_only_where_it_holds(self, tide):
        """The ruling's sentence says the order's cornice projects as far as it stands tall, which is
        Gibbs's rule. Where the kit refuses the modillions (bad-03, new-urbanist-traditional, A7)
        the members left are read to the envelope's height and their projections grow with them,
        so the two are not equal there, and the sentence names what left instead."""
        cor = tide["eave_cornice"]
        assert abs(cor["order_own_relief_in"] - cor["cornice_height_in"]) < 0.01
        assert "(Gibbs: projection equals height)" in cor["projection_ruling"]
        b03 = _build("plans/reference/bad-03-narrow-lot-townhome.json")["eave_cornice"]
        # the premise: the refusal reached the cornice, and the two figures really differ
        assert b03.get("modillions_refused_by")
        assert b03["order_own_relief_in"] > b03["cornice_height_in"] + 1.0
        ruling = b03["projection_ruling"]
        assert "projection equals height" not in ruling
        assert f"against a height of {round(b03['cornice_height_in'], 2)} in" in ruling
        assert "corn_modillion" in ruling

    def test_the_inset_says_what_was_scaled_and_what_is_a_judgment(self, tide, tmp_path):
        _ink, _pl, said = _svg(tide, "S", tmp_path, tag="inset")
        text = " ".join(said)
        env = tide["eave_cornice"]["envelope_projection_in"]
        assert f"PROJECTIONS SCALED INTO THE ENVELOPE'S {env:.1f}″" in text
        assert "BED MOULD HELD AT 2.5″ — A JUDGMENT" in text
        assert "BOTH SOURCED" not in text
