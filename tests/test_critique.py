"""WP-9.1 — the critique: one building inside the critic, the evidence contract, and the
analyst's classes.

Every test is named for the finding it protects. The one that matters most is the first:
until Phase 9, `plan_check.check()` derived its elevation from a FRESH heuristic placement of
the declared record while its drawn layer read the placement the record carried -- two
buildings in one verdict -- and the block that did it was `except Exception: pass`, so an
elevation that could not be derived was indistinguishable from one that had nothing to say.
"""
import json
import os
import re
import sys

import pytest

from conftest import load_plan, minimal_plan

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)
import modcache as mc  # noqa: E402

PC = mc.load("plan_check", os.path.join(BUILD, "plan_check.py"))
GEO = mc.load("geometry", os.path.join(BUILD, "geometry.py"))
ST = mc.load("structure", os.path.join(BUILD, "structure.py"))
EL = mc.load("elevation", os.path.join(BUILD, "elevation.py"))


def _placed(pid, engine="heuristic"):
    return GEO.solve(load_plan(pid), engine=engine)


# ------------------------------------------------------------------ one building
class TestOneBuildingInsideTheCritic:
    def test_the_elevation_is_of_the_placement_the_record_carries_not_a_fresh_one(self, monkeypatch, corpus):
        """Revert the WP-9.1 block in plan_check.check and build_section receives
        `geometry_result=None` -- a fresh heuristic placement of the declared record, not
        the one the drawn layer is judging two hundred lines below."""
        seen = []
        real = ST.build_section

        def spy(plan, parti=None, geometry_result=None, engine="heuristic"):
            seen.append(geometry_result)
            return real(plan, parti, geometry_result=geometry_result, engine=engine)

        monkeypatch.setattr(ST, "build_section", spy)
        placed = _placed("tidewater-georgian-careful")
        res = PC.check(placed, corpus)
        assert seen, "plan_check's elevation layer never reached build_section"
        assert seen[0] is placed, "the section was not built from the record's own placement"
        assert res["elevation_summary"]["basis"] == "placement"
        assert res["elevation_summary"]["engine"] == "heuristic"
        assert res["elevation_summary"]["evaluated"] is True
        basis = [f for f in res["findings"] if f.get("rule") == "elevation-basis"]
        assert len(basis) == 1 and basis[0]["severity"] == "info"
        assert "the placement this record carries" in basis[0]["statement"]

    def test_a_declared_record_says_its_elevation_came_from_a_fresh_placement(self, corpus):
        res = PC.check(load_plan("tidewater-georgian-careful"), corpus)
        assert res["elevation_summary"] == {"evaluated": True, "basis": "declared",
                                            "engine": "heuristic", "reason": None}
        basis = [f for f in res["findings"] if f.get("rule") == "elevation-basis"]
        assert len(basis) == 1 and "fresh heuristic placement" in basis[0]["statement"]

    def test_an_elevation_that_cannot_be_derived_is_a_named_info_finding_not_silence(self, monkeypatch, corpus):
        """The old `except Exception: pass`. Reverting it makes this test fail: the finding
        is gone and `elevation_summary` says nothing."""
        def boom(*a, **k):
            raise RuntimeError("no roof for you")
        monkeypatch.setattr(EL, "build_elevation", boom)
        res = PC.check(load_plan("tidewater-georgian-careful"), corpus)
        f = [x for x in res["findings"] if x.get("rule") == "elevation-not-derived"]
        assert len(f) == 1 and f[0]["severity"] == "info"
        assert "RuntimeError: no roof for you" in f[0]["statement"]
        assert res["elevation_summary"]["evaluated"] is False
        assert "no roof for you" in res["elevation_summary"]["reason"]

    def test_a_style_outside_the_elevation_scope_is_stated_not_passed(self, corpus):
        plan = minimal_plan([{"id": "hall", "type": "hall", "width_ft": 14, "length_ft": 16,
                              "exterior_walls": ["S"], "doors": [{"to": "exterior"}]}],
                            style="craftsman-bungalow", massing="bungalow")
        res = PC.check(plan, corpus)
        f = [x for x in res["findings"] if x.get("rule") == "elevation-not-applicable"]
        assert len(f) == 1 and f[0]["severity"] == "info"
        assert res["elevation_summary"]["evaluated"] is False
        assert "scope" in res["elevation_summary"]["reason"]

    def test_the_elevation_findings_are_info_and_never_enter_the_scored_counts(self, corpus):
        res = PC.check(load_plan("spec-builder-colonial"), corpus)
        for f in res["findings"]:
            if str(f.get("rule", "")).startswith("elevation-"):
                assert f["severity"] == "info", f


# ------------------------------------------------------------------ the evidence contract
class TestTheEvidenceContract:
    _CHECKED_KINDS = {"furniture-fit", "width-below-floor", "ceiling-below-min",
                      "stair-not-drawn", "fixture-unplaced", "wall-run", "passage-narrow",
                      "passage-dead-zone"}

    @pytest.mark.parametrize("pid", ["spec-builder-colonial", "tidewater-georgian-careful"])
    def test_every_figure_a_move_would_read_is_the_figure_the_sentence_states(self, pid, corpus):
        """A number a move reads must be the number the reader sees. Rounded to one place
        (the sentences print `.1f`), or printed bare (`%g`) where the sentence does."""
        res = PC.check(_placed(pid), corpus)
        checked = 0
        for f in res["findings"]:
            if f.get("kind") not in self._CHECKED_KINDS:
                continue
            for key in ("need_ft", "have_ft"):
                v = f.get(key)
                vals = v if isinstance(v, list) else [v]
                for x in vals:
                    if not isinstance(x, (int, float)):
                        continue
                    forms = {f"{x:.1f}", f"{x:g}", f"{x:.0f}", str(x)}
                    # as a whole figure: "12.3" inside "112.3" is not the sentence stating 12.3
                    assert any(re.search(rf"(?<![\d.]){re.escape(t)}(?![\d])", f["statement"]) for t in forms), \
                        (f["id"], key, x, f["statement"])
                    checked += 1
        assert checked > 5, f"{pid}: too few figures were held against their sentences ({checked})"

    def test_the_furniture_need_is_unrounded(self, corpus):
        """compose.repair read `12.3` out of a sentence for a room needing 12.333 and declared
        12.3, and `12.3 > 12.3` was false. The field carries the real figure."""
        res = PC.check(load_plan("spec-builder-colonial"), corpus)
        fits = [f for f in res["findings"] if f.get("kind") == "furniture-fit" and f.get("axis") == "width"]
        assert fits
        for f in fits:
            assert f["need_ft"] > f["have_ft"], f
            assert f["need_ft"] == round(f["need_ft"], 3)
        assert any(abs(f["need_ft"] - round(f["need_ft"], 1)) > 1e-9 for f in fits), \
            "every need happened to be a round number, so this test could not see the rounding"

    def test_a_fault_finding_names_what_it_read_and_whether_the_house_declared_it(self, corpus):
        res = PC.check(load_plan("spec-builder-colonial"), corpus)
        faults = [f for f in res["findings"] if f["layer"] == "fault" and f["severity"] != "info"]
        assert faults
        for f in faults:
            assert f["kind"] == "fault-present" and f["fault"] == f["rule"]
            assert f["expression"] and f["reads"], f
            assert f["source"] in ("declared", "derived")
            assert "fix_right" in f and "fix_cheap" in f
        # the spec Colonial DECLARES its half-width shutter; that finding is the record's own
        shutter = next(f for f in faults if f["fault"] == "shutter-half-width-leaf")
        assert shutter["source"] == "declared", shutter
        # and a cornice figure is the generator's
        derived = [f for f in faults if f["source"] == "derived"]
        assert derived

    def test_every_evaluated_row_from_check_measurements_names_its_expression(self, core_module):
        r = core_module.check_measurements({"shutter_leaf_width_in": 12, "window_opening_width_in": 32},
                                           style="colonial-revival")
        rows = [x for p in r["faults_present"] for x in p["results"]]
        assert rows and all(x.get("expression") for x in rows)

    def test_the_finding_id_is_unchanged_by_the_evidence_it_carries(self):
        """OQ 32: an id is what a finding is ABOUT. Evidence rides beside it and must never
        enter it, or every citation and every open/cleared diff breaks on a number."""
        a, b = PC.Findings(), PC.Findings()
        a.add("serious", "furniture", "X cannot take its bed", room="bed2", rule="prose here")
        b.add("serious", "furniture", "X cannot take its bed", room="bed2", rule="prose here",
              kind="furniture-fit", need_ft=10.667, have_ft=9.5, axis="width", item="bed")
        assert a.items[0]["id"] == b.items[0]["id"] == "furniture:bed2"

    def test_the_style_layer_names_the_cascades_single_canonical_beside_a_forbidden_variant(self, corpus):
        plan = minimal_plan([{"id": "hall", "type": "hall", "width_ft": 14, "length_ft": 16,
                              "exterior_walls": ["S"], "doors": [{"to": "exterior"}]}],
                            style="colonial-revival", massing="four-over-four")
        # find a forbidden variant colonial-revival's cascade carries, and declare it
        kit = PC._resolved_slots("colonial-revival")
        target = None
        for slot_id, rec in kit.items():
            forb = [v["id"] for v in rec.get("variants", []) if v.get("status") == "forbidden"]
            if forb:
                target = (slot_id, forb[0], rec)
                break
        if not target:
            pytest.skip("COULD NOT EVALUATE — colonial-revival's cascade forbids no variant")
        slot_id, forb, rec = target
        plan["declared"] = {slot_id: forb}
        res = PC.check(plan, corpus)
        f = next(x for x in res["findings"] if x.get("kind") == "variant-forbidden")
        assert f["slot"] == slot_id and f["variant"] == forb
        canon = [v["id"] for v in rec.get("variants", []) if v.get("status") == "canonical"]
        assert f["canonical"] == (canon[0] if len(canon) == 1 else None)


# ------------------------------------------------------------------ the drawn layer's engine
class TestDrawnFindingsCarryTheEngineThatPlacedThem:
    def test_every_drawn_finding_names_the_engine_that_ran(self, corpus):
        res = PC.check(_placed("tidewater-georgian-careful", engine="heuristic"), corpus)
        drawn = [f for f in res["findings"] if f["layer"] == "drawn"]
        assert drawn
        assert all(f.get("engine") == "heuristic" for f in drawn), {f.get("engine") for f in drawn}
        assert all(f.get("kind") for f in drawn), [f for f in drawn if not f.get("kind")]

    def test_the_engine_named_is_the_one_that_ran_not_the_one_requested(self, corpus):
        """`auto` may fall back. The label must read geometry_report.solver.engine, never the
        request -- a caption naming a proof that never happened is worse than none."""
        placed = _placed("tidewater-georgian-careful", engine="auto")
        ran = placed["geometry_report"]["solver"]["engine"]
        res = PC.check(placed, corpus)
        drawn = [f for f in res["findings"] if f["layer"] == "drawn"]
        assert drawn and all(f.get("engine") == ran for f in drawn)
        assert res["elevation_summary"]["engine"] == ran

    def test_a_stranded_room_names_the_placed_rooms_a_door_could_reach(self, corpus):
        res = PC.check(_placed("tidewater-georgian-careful", engine="heuristic"), corpus)
        stranded = [f for f in res["findings"] if f.get("kind") in ("unreachable", "cut-off")]
        if not stranded:
            pytest.skip("COULD NOT EVALUATE — the heuristic stranded nothing on this run")
        for f in stranded:
            assert isinstance(f["adjacent_placed"], list)
            assert isinstance(f["unplaced_pairs"], list)
            assert f["room"] not in f["adjacent_placed"]


# ------------------------------------------------------------------ the corpus fix that rode along
class TestWingPitchDriftDeclinesOnOneSlope:
    def test_one_slope_is_not_two_slopes_eight_degrees_apart(self, core_module):
        r = core_module.check_measurements(
            {"count_of_distinct_roof_slope_angles_on_the_building": 1,
             "min_absolute_difference_between_distinct_slope_angles_deg": 0.0},
            style="tidewater-georgian")
        present = [x["fault"] for x in r["faults_present"]]
        assert "wing-pitch-drift" not in present
        # and the primary still judges the count: three slopes IS the fault
        r2 = core_module.check_measurements(
            {"count_of_distinct_roof_slope_angles_on_the_building": 3,
             "min_absolute_difference_between_distinct_slope_angles_deg": 2.0},
            style="tidewater-georgian")
        assert "wing-pitch-drift" in [x["fault"] for x in r2["faults_present"]]


# ------------------------------------------------------------------ the analyst
class TestTheAnalyst:
    @pytest.fixture(scope="class")
    def crit(self):
        CR = mc.load("critique", os.path.join(BUILD, "critique.py"))
        return CR, CR.critique(load_plan("tidewater-georgian-careful"), engine="heuristic")

    def test_every_finding_lands_in_exactly_one_class_or_could_not_evaluate(self, crit):
        CR, res = crit
        ids = [i["id"] for c in CR.CLASSES for i in res["assessment"][c]]
        cne = [x["id"] for x in res["could_not_evaluate"]["findings"]]
        assert len(ids) == len(set(ids)), "a finding was classified twice"
        assert set(ids).isdisjoint(cne)
        assert sorted(ids + cne) == sorted(f["id"] for f in res["check"]["findings"])
        assert sum(res["counts_by_class"].values()) == len(ids)

    def test_the_key_is_the_checks_own_counts(self, crit):
        CR, res = crit
        c = res["check"]["counts"]
        assert res["key"] == [c.get("fatal", 0), c.get("serious", 0), c.get("minor", 0),
                              res["check"]["fault_summary"]["present"]]

    def test_a_fault_whose_failing_test_reads_a_source_literal_is_a_suspect_with_its_line(self, crit):
        CR, res = crit
        sus = res["assessment"]["critic_suspect"]
        assert sus, "no suspect on the Tidewater plan -- the instrument stopped seeing"
        lit = [i for i in sus if i["evidence"][0]["instrument"] == "source-literal"]
        assert lit, [i["evidence"] for i in sus]
        ev = lit[0]["evidence"][0]
        assert isinstance(ev["line"], int) and ev["line"] > 0 and "value" in ev
        # the surround-that-lies fault reads window_reveal_depth_in = 4.0, a literal
        assert any(i["finding"]["fault"] == "surround-that-lies-about-the-wall" for i in lit)
        # and the editorial entry reaches the parallel shaft
        ed = [i for i in sus if any(e["instrument"] == "editorial" for e in i["evidence"])]
        assert any(i["finding"]["fault"] == "column-without-entasis" for i in ed)

    def test_a_suspect_is_never_actionable_and_never_architect(self, crit):
        CR, res = crit
        sus = {i["id"] for i in res["assessment"]["critic_suspect"]}
        for c in ("actionable", "architect", "placement"):
            assert sus.isdisjoint({i["id"] for i in res["assessment"][c]})

    def test_a_placement_finding_names_the_engine_and_its_lever(self, crit):
        CR, res = crit
        pl = res["assessment"]["placement"]
        assert pl, "the heuristic left nothing to the engine on this run"
        for i in pl:
            assert i["engine"] == "heuristic"
            assert i["lever"] in ("engine", "candidates")
            assert i["move"] in ("prove-it", "search-harder")
            assert i["why"]

    def test_a_stair_the_declared_hall_would_have_held_is_placement_not_actionable(self, crit):
        CR, res = crit
        stair = [i for c in CR.CLASSES for i in res["assessment"][c] if i["kind"] == "stair-not-drawn"]
        if not stair:
            pytest.skip("COULD NOT EVALUATE — the heuristic drew the stair on this run")
        i = stair[0]
        if i["finding"].get("declared_fits"):
            assert i["class"] == "placement"
        else:
            assert i["class"] in ("actionable", "architect")
            assert (i.get("move") or i.get("intended_move")) == "grow-stair-hall-to-its-run"

    def test_an_architect_item_carries_the_faults_own_right_fix_or_the_rules_why(self, crit):
        CR, res = crit
        arch = res["assessment"]["architect"]
        faults = [i for i in arch if i["layer"] == "fault"]
        assert faults and all("fix_right" in i for i in faults)
        adj = [i for i in arch if i["layer"] == "adjacency"]
        assert adj
        prose = [i for i in adj if isinstance(i["finding"].get("rule"), str) and " " in i["finding"]["rule"]]
        assert prose and all(i["rule_why"] == i["finding"]["rule"] for i in prose)

    def test_the_declared_mode_reports_the_drawn_layer_as_not_evaluated(self):
        CR = mc.load("critique", os.path.join(BUILD, "critique.py"))
        res = CR.critique(load_plan("tidewater-georgian-careful"), place=False)
        assert res["placement"]["placed"] is False
        assert res["could_not_evaluate"]["drawn"] is False
        assert res["assessment"]["placement"] == []
        assert res["engine"]["ran"] is None

    def test_a_carried_placement_is_reused_never_re_solved(self):
        CR = mc.load("critique", os.path.join(BUILD, "critique.py"))
        placed = _placed("tidewater-georgian-careful")
        before = json.dumps(placed, sort_keys=True)
        res = CR.critique(placed, engine="cp")
        assert res["placement"]["reused"] is True
        assert res["engine"]["ran"] == "heuristic", "the carried placement was replaced"
        assert json.dumps(placed, sort_keys=True) == before, "critique mutated its argument"

    def test_the_analyst_never_mutates_its_argument(self):
        CR = mc.load("critique", os.path.join(BUILD, "critique.py"))
        plan = load_plan("spec-builder-colonial")
        before = json.dumps(plan, sort_keys=True)
        CR.critique(plan, engine="heuristic")
        assert json.dumps(plan, sort_keys=True) == before


# ------------------------------------------------------------------ the suspect instrument
class TestTheSuspectInstrument:
    def test_the_literal_instrument_finds_the_constants_and_ratchets(self):
        CS = mc.load("critic_suspects", os.path.join(BUILD, "critic_suspects.py"))
        CK = mc.load("check_critic_suspects", os.path.join(BUILD, "check_critic_suspects.py"))
        lits = CS.source_literals()
        assert "window_reveal_depth_in" in lits and lits["window_reveal_depth_in"]["value"] == 4.0
        assert "min_absolute_difference_between_distinct_slope_angles_deg" in lits
        assert 0 < len(lits) <= CK.LITERALS_CEILING
        ratios = CS.literal_ratios()
        assert "window_casing_width_in" in ratios and ratios["window_casing_width_in"]["factor"] == 0.6
        assert len(ratios) <= CK.RATIOS_CEILING

    def test_the_instrument_reads_the_shapes_it_claims_to(self):
        CS = mc.load("critic_suspects", os.path.join(BUILD, "critic_suspects.py"))
        src = '''
def _derive_measurements(elev):
    m = {}
    m.update({"a": 4.0, "b": x["q"] * 0.6, "c": x["q"], "d": round(x["q"] * 12.0, 2)})
    m["e"] = 0
    m["f"] = round(y * 0.14, 1)
    return m
'''
        lits, ratios = CS.source_literals(src), CS.literal_ratios(src)
        assert set(lits) == {"a", "e"}
        assert set(ratios) == {"b", "f"}, "a unit conversion (x 12) is not a proportion"

    def test_the_checker_passes_today_and_refuses_a_ceiling_breach(self, monkeypatch, capsys):
        """The first version's name promised a refusal and induced no breach (the session's
        audit): the checker is run again here with one literal more than its ceiling."""
        import subprocess
        proc = subprocess.run([sys.executable, os.path.join(BUILD, "check_critic_suspects.py"), "--no-sweep"],
                              capture_output=True, text=True, cwd=ROOT)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        CK = mc.load("check_critic_suspects", os.path.join(BUILD, "check_critic_suspects.py"))
        CS = mc.load("critic_suspects", os.path.join(BUILD, "critic_suspects.py"))
        assert CK.LITERALS_CEILING == len(CS.source_literals()), \
            "the ceiling is not the measurement; lower it in the same commit that lowers the count"
        real = CS.source_literals()
        more = dict(real, **{"an_invented_measurement_in": {"value": 1.0, "line": 0, "shape": "Constant"}})
        monkeypatch.setattr(CS, "source_literals", lambda *a, **k: more)
        monkeypatch.setattr(sys, "argv", ["check_critic_suspects.py", "--no-sweep"])
        assert CK.main() == 1, "one literal over the ceiling did not fail the checker"
        assert "against a ceiling" in capsys.readouterr().out

    def test_an_editorial_suspect_with_a_misquoted_basis_is_refused(self):
        CO = mc.load("check_openings", os.path.join(BUILD, "check_openings.py"))
        rep = CO.Report()
        entry = {"id": "cs-x", "basis": "build/elevation.py: \"upper and lower diameter are genuinely identical\""}
        CO.check_basis(rep, entry, source="critique/suspects.json")
        assert rep.errors == []
        rep2 = CO.Report()
        bad = {"id": "cs-x", "basis": "build/elevation.py: \"upper and lower diameter are genuinely different\""}
        CO.check_basis(rep2, bad, source="critique/suspects.json")
        assert rep2.errors, "a quote that is not in the file passed the basis check"


CS = mc.load("critic_suspects", os.path.join(BUILD, "critic_suspects.py"))
CK = mc.load("check_critic_suspects", os.path.join(BUILD, "check_critic_suspects.py"))


class TestTheInstrumentOnTheRealFile:
    """WP-9.4. `test_the_instrument_reads_the_shapes_it_claims_to` feeds a toy string; the
    only real-file guard was the count equality, which a same-commit ceiling change satisfies.
    These read build/elevation.py itself and name the shapes the first instrument was blind
    to -- each one a literal measurement that had been below the 35.

    Corrected by the session's audit: the first version pinned the AST shape a real-file
    name is detected by and the ceiling at exactly 44, which forbade the ratchet's own
    sanctioned direction -- modelling a literal away, or reading it from the record with the
    literal as a fallback, failed the test. Each shape is pinned on a fixture string; the
    real file is held to a FROZEN list its names may only leave, never join."""

    # every name the instrument found on 2 Sep 2026, after the five shapes were added. A name
    # may LEAVE this list (modelled, or moved to NOT_MODELLED); a name not on it is a new
    # invented constant and fails below. The six the audit named are pinned by value too.
    FROZEN = {
        "belt_course_projection_in", "count_of_distinct_ridge_heights_on_the_main_block",
        "count_of_distinct_roof_slope_angles_on_the_building", "count_of_interruptions_in_the_eave_line",
        "count_of_material_changes_on_the_elevation",
        "count_of_non_chimney_non_dormer_objects_on_the_entrance_roof_slope",
        "count_of_openings_without_a_mirror_twin_about_the_facade_centreline",
        "count_of_perforations_visible_in_the_cornice_soffit_frieze_or_fascia", "count_of_volumes_on_the_elevation",
        "distinct_head_datums_per_storey_per_elevation", "distinct_head_datums_within_one_wall_plane_and_storey",
        "distinct_light_proportions_across_the_elevation", "distinct_meeting_rail_heights_per_storey_per_elevation",
        "distinct_mouldings_within_4ft_of_the_entrance", "distinct_sill_datums_per_storey_per_elevation",
        "distinct_style_vocabularies_on_one_elevation", "distinct_window_shapes_on_the_street_elevation",
        "equipment_units_visible_on_the_entrance_elevation", "escutcheon_width_in", "faces_of_volume",
        "faces_of_volume_clad_in_primary_material", "faces_of_volume_in_one_body_colour",
        "front_door_plane_setback_behind_garage_door_plane_ft", "jamb_reveal_depth_in",
        "max_abs_offset_between_upper_and_lower_opening_centrelines_in",
        "max_distinct_mouldings_elsewhere_on_the_elevation", "max_head_offset_from_datum_in",
        "min_absolute_difference_between_distinct_slope_angles_deg", "orders_present_in_one_storey",
        "reveal_depth_in", "sash_bottom_rail_height_in", "sash_meeting_rail_height_in", "sash_stile_width_in",
        "sash_top_rail_height_in", "shutter_leaves_with_a_leaf_width_of_clear_hinge_side_wall",
        "sidelight_width_in", "solar_array_area_sqft", "total_shutter_leaves", "transom_head_rise_in",
        "vent_terminal_height_above_roof_surface_in", "visible_hardware_items_per_window",
        "visible_surface_hinges_per_leaf", "width_of_the_largest_asymmetric_element_in", "window_reveal_depth_in",
    }
    AUDIT_NAMED = {"sash_stile_width_in", "sash_meeting_rail_height_in", "transom_head_rise_in",
                   "distinct_mouldings_within_4ft_of_the_entrance", "belt_course_projection_in",
                   "max_distinct_mouldings_elsewhere_on_the_elevation"}

    def test_each_shape_is_detected_on_a_fixture_string(self):
        src = '''
K = {"a": 2.0, "b": 1.25}
D = 7.5
def _derive_measurements(elev):
    m = {}
    m["sub"] = K["a"]
    m["name"] = D
    m["tern"] = elev["x"] if elev.get("x") else 0.0
    m["fallback"] = elev.get("y") or 3
    m["floor"] = max(1, elev["z"])
    m["nested"] = 4 * elev["w"] * elev["k"]
    m["real"] = elev["q"]
    return m
'''
        lits = CS.source_literals(src)
        assert lits["sub"]["value"] == 2.0 and lits["sub"]["shape"] == "Subscript"
        assert lits["name"]["value"] == 7.5 and lits["name"]["shape"] == "Name"
        assert lits["tern"]["value"] == 0.0 and lits["tern"]["shape"] == "IfExp"
        assert lits["fallback"]["value"] == 3 and lits["fallback"]["shape"] == "BoolOp"
        assert lits["floor"]["value"] == 1 and lits["floor"]["shape"] == "Call"
        assert "real" not in lits
        assert CS.literal_ratios(src)["nested"]["factor"] == 4, "a literal one level down a BinOp"

    def test_the_real_file_names_are_a_subset_of_the_frozen_list_and_the_audits_six_are_still_literals(self):
        lits = CS.source_literals()
        assert len(self.FROZEN) == 44
        new = set(lits) - self.FROZEN
        assert not new, f"new invented constants in elevation.py: {sorted(new)}"
        for name in self.AUDIT_NAMED:
            assert name in lits, f"{name} is no longer detected -- if it was modelled, remove it here in the same commit"
        assert lits["sash_stile_width_in"]["value"] == 2.0 and lits["sash_meeting_rail_height_in"]["value"] == 1.25
        assert lits["transom_head_rise_in"]["value"] == 0.0
        assert lits["distinct_mouldings_within_4ft_of_the_entrance"]["value"] == 3
        assert lits["belt_course_projection_in"]["value"] == 1.0
        assert lits["max_distinct_mouldings_elsewhere_on_the_elevation"]["value"] == 1

    def test_a_literal_one_level_down_a_binop_and_a_half_are_ratios(self):
        ratios = CS.literal_ratios()
        assert ratios["total_opening_width_in"]["factor"] == 4, "4 * a window width is a bay count the generator invented"
        assert ratios["net_clear_opening_height_in"]["factor"] == 0.5, "half a sash is an egress rule, not a unit conversion"
        assert 12 not in {r["factor"] for r in ratios.values()} and 144 not in {r["factor"] for r in ratios.values()}

    def test_the_ceilings_were_re_baselined_upward_once_and_may_only_fall_since(self):
        src = open(os.path.join(ROOT, "build", "check_critic_suspects.py"), encoding="utf-8").read()
        assert "35 -> 44" in src and "4 -> 7" in src
        assert CK.LITERALS_CEILING <= 44 and CK.RATIOS_CEILING <= 7, "a ceiling went UP after the one public re-baseline"


class TestTheStairTheDeclaredHallCouldNotHold:
    """`_is_placement` reads `declared_fits` for `stair-not-drawn`; on both shipped plans the
    declared hall holds the stair, so the only branch a real critique exercised was
    `placement`, and a mutation making every stair finding placement stayed green (the
    session's audit). A synthetic check with `declared_fits: False` reaches the other branch."""

    def test_a_stair_the_declared_hall_could_not_hold_is_the_records_and_the_hall_move_answers(self, corpus):
        CR = mc.load("critique", os.path.join(BUILD, "critique.py"))
        MV = mc.load("moves", os.path.join(BUILD, "moves.py"))
        plan = _placed("tidewater-georgian-careful")
        stair = next(r for lv in plan["levels"] for r in lv["rooms"] if r["type"] == "stair-hall")
        f = {"id": "drawn:stair:stair-not-drawn", "layer": "drawn", "severity": "serious", "rule": "stair-not-drawn",
             "kind": "stair-not-drawn", "room": stair["id"], "engine": "heuristic", "declared_fits": False,
             "need_ft": [max(stair["width_ft"], stair["length_ft"]) + 4.0, min(stair["width_ft"], stair["length_ft"]) + 1.0],
             "have_ft": [stair["length_ft"], stair["width_ft"]], "risers": 14, "form": "dog-leg",
             "statement": "the stair could not be drawn in the hall"}
        check = {"findings": [f], "counts": {"serious": 1}}
        assessment, _cne = CR.classify(plan, check, MV, corpus, {"engine": "heuristic", "candidates": 120})
        assert not assessment["placement"], "a stair the declared hall could not hold is not the engine's"
        item = (assessment["actionable"] + assessment["architect"])[0]
        assert (item.get("move") or item.get("intended_move")) == "grow-stair-hall-to-its-run"
        assert item["class"] == "actionable", item.get("why")
