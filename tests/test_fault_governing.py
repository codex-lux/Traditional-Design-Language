"""A fault is clear only where its governing test ran (WP-16.1, R4 of 29 Sep 2026).

`oq/a-fault-reads-clear-when-its-governing-test-could-not-run` measured 142 of 550 clear verdicts
on the sixteen shipped plans resting on a secondary while the governing test -- the primary, or the
bounds_test of an exception the style earned -- wanted a measurement nobody supplied. Lucas ruled
that the governing test decides. These tests drive `core.check_measurements`'s `_judge` through
every branch with SYNTHETIC faults, because three of the branches cannot be reached from the corpus
as it stands (a declined or scoped governing test beside an ungated secondary, and an errored one),
and a branch the corpus cannot reach is guarded only by a fixture that reaches it.

The synthetic faults are added to the corpus's own cached dict for one test and removed after it,
so `check_measurements` walks them exactly as it walks a record from `faults/`.
"""
import copy
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CORE = modcache.load("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))

STYLE = "tidewater-georgian"


def _t(expr, direction="at-most", threshold=1.0, **kw):
    t = {"expression": expr, "direction": direction, "threshold": threshold,
         "units": "ratio", "measurable_from": "photograph"}
    t.update(kw)
    return t


def _fault(fid, test, secondaries=(), severity="fatal", exceptions=()):
    return {"id": fid, "name": fid.replace("-", " "), "severity": severity,
            "applies_to": ["universal"], "slots": ["cornice"], "symptom": "driven",
            "test": test, "secondary_tests": list(secondaries),
            "exceptions": list(exceptions), "fixes": {}}


@pytest.fixture
def judge(monkeypatch):
    """Run `check_measurements` over ONE synthetic fault and return (state, row)."""
    D = CORE._data()

    def run(fault, meas, style=STYLE, context=None):
        monkeypatch.setitem(D["faults"], fault["id"], fault)
        r = CORE.check_measurements(meas, style=style, limit=10**6, context=context)
        for state, key in (("present", "faults_present"), ("clear", "faults_clear"),
                           ("needed", "could_not_judge"), ("not_applicable", "not_applicable")):
            rows = [x for x in r[key] if x["fault"] == fault["id"]]
            if rows:
                assert len(rows) == 1
                return state, rows[0]
        return None, None
    return run


GOV = _t("gov_a / gov_b", threshold=1.0)
SEC = _t("sec_x", threshold=5.0)


class TestTheGoverningTestDecides:
    def test_a_governing_test_that_could_not_run_is_not_clear_on_a_secondary_that_passed(self, judge):
        """The 142: the secondary ran and passed, the governing test wanted a measurement."""
        state, row = judge(_fault("drv-gov-missing", GOV, [SEC]), {"sec_x": 2.0})
        assert state == "needed", "a secondary that passed must not stand in for the governing test"
        assert row["governing_not_run"] == {"expression": "gov_a / gov_b",
                                            "missing": ["gov_a", "gov_b"]}
        assert [x["expression"] for x in row["ran"]] == ["sec_x"]
        assert row["ran"][0]["passes"] is True, "what ran rides as evidence, with its own result"
        assert row["needs"] == ["gov_a", "gov_b"]
        assert row["severity"] == "fatal", "the row carries the severity the composer ranks on"

    def test_a_secondary_that_failed_still_makes_the_fault_present(self, judge):
        """The ruling is about clear. A failed test is still the fault."""
        state, row = judge(_fault("drv-sec-fails", GOV, [SEC]), {"sec_x": 9.0})
        assert state == "present"
        assert [x["expression"] for x in row["failing"]] == ["sec_x"]

    def test_a_clear_names_every_secondary_that_did_not_run(self, judge):
        sec2 = _t("sec_y + sec_z", threshold=3.0)
        state, row = judge(_fault("drv-clear-unrun", GOV, [SEC, sec2]),
                           {"gov_a": 1.0, "gov_b": 2.0, "sec_x": 1.0})
        assert state == "clear"
        assert row["secondaries_not_run"] == [{"expression": "sec_y + sec_z",
                                               "missing": ["sec_y", "sec_z"]}]

    def test_a_clear_with_nothing_unrun_carries_no_list(self, judge):
        """Absent, never an empty list that a reader must remember means none."""
        state, row = judge(_fault("drv-clear-all", GOV, [SEC]),
                           {"gov_a": 1.0, "gov_b": 2.0, "sec_x": 1.0})
        assert state == "clear" and "secondaries_not_run" not in row

    def test_a_declined_secondary_is_not_named_as_unrun(self, judge):
        """A secondary that declined on its own `applies_when` asks a question that does not
        arise; it is not an uncertainty a clear has to own up to."""
        gated = _t("sec_x", threshold=5.0,
                   applies_when={"expression": "n", "direction": "at-least", "threshold": 1})
        state, row = judge(_fault("drv-sec-declined", GOV, [gated]),
                           {"gov_a": 1.0, "gov_b": 2.0, "n": 0})
        assert state == "clear" and "secondaries_not_run" not in row

    def test_an_errored_governing_test_is_unjudged_with_the_error(self, judge):
        bad = _t("gov_a / gov_b")
        state, row = judge(_fault("drv-gov-error", bad, [SEC]),
                           {"gov_a": 1.0, "gov_b": 0.0, "sec_x": 1.0})
        assert state == "needed"
        assert "division by zero" in row["governing_not_run"]["error"]
        assert row["errors"], "the error is on the row as it always was"

    def test_a_governing_test_with_no_verdict_is_not_read_as_a_pass(self, judge, monkeypatch):
        """`_eval_test` returns `passes: None` for a direction it does not know. The schema
        forbids one, and `failing` has never counted None -- so without this branch an unknown
        direction on a governing test would read clear. Driven by an unknown direction."""
        state, row = judge(_fault("drv-gov-noverdict", _t("gov_a", direction="sideways"), [SEC]),
                           {"gov_a": 1.0, "sec_x": 1.0})
        assert state == "needed"
        assert "no verdict" in row["governing_not_run"]["why"]


class TestTheGoverningTestDeclined:
    def test_every_test_declined_keeps_the_historical_row(self, judge):
        """The one reachable not-applicable shape: every test gated on one premise. Its row is
        unchanged from WP-5.13, so no reader of it moves."""
        w = {"expression": "n", "direction": "at-least", "threshold": 1}
        f = _fault("drv-all-declined", _t("gov_a", applies_when=w), [_t("sec_x", applies_when=w)])
        state, row = judge(f, {"n": 0})
        assert state == "not_applicable"
        assert row["because"] == ["n"] and row["required"] == ["at-least 1"]
        assert row["note"].startswith("Every test of this fault is preconditioned")
        assert "ran" not in row and "secondaries_not_run" not in row

    def test_a_declined_governing_test_beside_an_ungated_secondary_is_not_applicable(self, judge):
        """Unreachable from the corpus (no fault gates its primary and not its secondaries) and
        therefore driven: the governing test decided the question does not arise. What ran is
        carried as evidence, and the note says the governing test decided, not every test."""
        w = {"expression": "n", "direction": "at-least", "threshold": 1}
        state, row = judge(_fault("drv-gov-declined", _t("gov_a", applies_when=w), [SEC]),
                           {"n": 0, "sec_x": 1.0})
        assert state == "not_applicable"
        assert [x["expression"] for x in row["ran"]] == ["sec_x"]
        assert "governing test" in row["note"]

    def test_a_declined_governing_test_does_not_excuse_a_failing_secondary(self, judge):
        w = {"expression": "n", "direction": "at-least", "threshold": 1}
        state, _row = judge(_fault("drv-gov-declined-fail", _t("gov_a", applies_when=w), [SEC]),
                            {"n": 0, "sec_x": 9.0})
        assert state == "present"

    def test_a_governing_test_whose_gate_cannot_be_read_is_unjudged_not_inapplicable(self, judge):
        """A gate whose own measurement is missing cannot say whether the test applies."""
        w = {"expression": "n", "direction": "at-least", "threshold": 1}
        state, row = judge(_fault("drv-gate-missing", _t("gov_a", applies_when=w), [SEC]),
                           {"sec_x": 1.0})
        assert state == "needed"
        assert row["governing_not_run"]["missing"] == ["n"]

    def test_a_governing_test_scoped_to_another_style_is_not_applicable_and_says_so(self, judge):
        """No fault scopes its primary today. Before this, a fault every one of whose tests was
        scoped away came back as the `silent` state and was appended to NO list."""
        scoped = _t("gov_a", applies_to_styles=["prairie-school"])
        state, row = judge(_fault("drv-gov-scoped", scoped), {"gov_a": 1.0})
        assert state == "not_applicable", "a fault must land in exactly one list, never none"
        assert "prairie-school" in row["because"][0]


class TestTheExceptionJudgedBothWays:
    """WP-8.4: a licence whose precondition cannot be resolved is judged both ways. The row said
    "the two rules disagree" with `needs: []` whenever the two states differed -- true where both
    reached a verdict, false where one could not be judged at all, which R4 makes common."""

    @pytest.fixture
    def unjudged_licence(self, monkeypatch):
        monkeypatch.setattr(CORE, "grant_exception",
                            lambda exc, style, context=None: {"verdict": "unjudged",
                                                               "why": "driven", "unevaluated": ["construction"]})

    def _licensed(self, fid, bounds):
        return _fault(fid, GOV, [], exceptions=[{"style": STYLE, "why": "driven",
                                                  "bounds_test": bounds,
                                                  "granted_when": {"construction": ["adobe"]}}])

    def test_one_side_unjudged_names_its_measurements_and_does_not_say_disagree(self, judge, unjudged_licence):
        f = self._licensed("drv-exc-one-unjudged", _t("exc_m", threshold=2.0))
        state, row = judge(f, {"gov_a": 1.0, "gov_b": 2.0})
        assert state == "needed"
        assert row["needs"] == ["exc_m"], "the unjudged side names what would judge it"
        x = row["exception_unjudged"]
        assert (x["under_the_exception"], x["under_the_general_rule"]) == ("needed", "clear")
        assert "disagree" not in x["note"]
        assert "could not be" in x["note"]

    def test_both_sides_decided_and_differing_still_says_they_disagree(self, judge, unjudged_licence):
        f = self._licensed("drv-exc-disagree", _t("exc_m", threshold=2.0))
        state, row = judge(f, {"gov_a": 1.0, "gov_b": 2.0, "exc_m": 9.0})
        assert state == "needed"
        assert row["needs"] == []
        x = row["exception_unjudged"]
        assert (x["under_the_exception"], x["under_the_general_rule"]) == ("present", "clear")
        assert "disagree" in x["note"]
        assert row["severity"] == "fatal"


class TestTheCorpusGates:
    """Four faults ask a question that presupposes a thing the house may not have, and each is
    gated on it: not applicable where it is absent, unjudged where nobody says."""

    @pytest.mark.parametrize("fid,premise", [
        ("storeys-out-of-vertical-alignment", "storey_count"),
        ("top-heavy-second-storey", "storey_count"),
        ("ungraduated-storeys", "storey_count"),
        ("overscaled-dormer", "dormer_count"),
    ])
    def test_every_test_and_every_licence_is_gated_on_the_premise(self, fid, premise):
        f = CORE._data()["faults"][fid]
        tests = [f["test"]] + list(f.get("secondary_tests") or []) + \
            [e["bounds_test"] for e in f.get("exceptions") or [] if e.get("bounds_test")]
        assert len(tests) >= 3
        for t in tests:
            w = t.get("applies_when") or {}
            assert w.get("expression") == premise and w.get("direction") == "at-least", t["expression"]

    @pytest.mark.parametrize("path", [
        "plans/reference/good-02-portico-library-house.json",
        "plans/tidewater-georgian-careful.json",
        "plans/reference/bad-03-narrow-lot-townhome.json"])
    def test_storey_count_is_the_houses_and_not_a_constant(self, path):
        """The gates here read `storey_count`, and the elevation used to read it off a list that
        always holds two entries, so every house it drew was two storeys: the one-storey reference
        plans and the three-storey townhouse alike (WP-16.1). The gate tests below drive the
        measurement by hand and could not see that, so the elevation's own figure is held here
        against each record's own levels, over a house of one, two and three storeys."""
        import json as _json
        plan = _json.load(open(os.path.join(ROOT, path)))
        m = EL.build_elevation(plan)["measurements"]
        assert m["storey_count"] == len({lv["index"] for lv in plan["levels"]}), path

    def test_a_one_storey_house_is_not_applicable_to_the_three_storey_faults(self):
        meas = {"storey_count": 1, "second_floor_sash_height_in": 60.0,
                "first_floor_sash_height_in": 60.0, "bay_count_on_the_principal_front": 5}
        r = CORE.check_measurements(meas, style="colonial-revival", limit=10**6)
        na = {x["fault"] for x in r["not_applicable"]}
        three = {"storeys-out-of-vertical-alignment", "top-heavy-second-storey",
                 "ungraduated-storeys"}
        assert three <= na, three - na
        # the premise: with the storey gate removed, the same figures convict -- a storey
        # compared with itself reads 1.0 against a ceiling of 0.95
        present = {x["fault"] for x in r["faults_present"]}
        assert not (three & present)

    def test_a_house_stating_no_dormers_is_not_applicable_to_their_scale(self):
        r = CORE.check_measurements({"dormer_count": 0, "sum_of_dormer_face_widths_in": 0.0,
                                     "building_width_in": 540.0},
                                    style="colonial-revival", limit=10**6)
        assert "overscaled-dormer" in {x["fault"] for x in r["not_applicable"]}
        assert "overscaled-dormer" not in {x["fault"] for x in r["faults_clear"]}

    def test_a_house_that_does_not_say_is_unjudged_not_inapplicable(self):
        r = CORE.check_measurements({"sum_of_dormer_face_widths_in": 0.0, "building_width_in": 540.0},
                                    style="colonial-revival", limit=10**6)
        row = next(x for x in r["could_not_judge"] if x["fault"] == "overscaled-dormer")
        assert "dormer_count" in row["needs"]


# ------------------------------------------------------------------ R13, the composer's tie-break

CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))


def _cand(parti, fatal, unjudged, score, demerits=0.0):
    return {"parti": parti, "counts": {"fatal": fatal}, "score": score, "demerits": demerits,
            "unjudged_fatal": [{"fault": f"f{i}", "name": f"f{i}"} for i in range(unjudged)]}


class TestTheComposerBreaksTiesAgainstAnUnjudgedFatal:
    def test_judged_fatals_first_then_unjudged_then_the_score(self):
        """The fixture separates the three keys: the best score carries the most unjudged fatals,
        and the one-fatal candidate carries none, so skipping the new key orders the clean pair
        by score and reading it first puts the fatal candidate above a clean one."""
        cands = [_cand("clean-high-many-unjudged", 0, 3, 90.0),
                 _cand("clean-low-few-unjudged", 0, 1, 20.0),
                 _cand("fatal-best-score", 1, 0, 99.0)]
        got = [c["parti"] for c in sorted(cands, key=CO.rank_key)]
        assert got == ["clean-low-few-unjudged", "clean-high-many-unjudged", "fatal-best-score"]
        assert [c["parti"] for c in sorted(reversed(cands), key=CO.rank_key)] == got

    def test_an_unjudged_fatal_never_counts_as_a_fatal(self):
        """It breaks a tie and does nothing else: `disqualified` reads judged fatals alone."""
        res = {"counts": {"fatal": 0}, "findings": [], "rooms": 4,
               "fault_summary": {"present": 0, "clear": 3, "unjudged": 2},
               "fault_unjudged": [{"fault": "a", "name": "A", "severity": "fatal"},
                                  {"fault": "b", "name": "B", "severity": "serious"},
                                  {"fault": "c", "name": "C"}]}
        assert CO.unjudged_fatals(res) == [{"fault": "a", "name": "A"}], (
            "only a row whose severity is fatal counts; a row carrying none is not guessed at")
        plan = {"levels": [], "declared": {}}
        card = CO.score_candidate(res, plan, {"bedrooms": 0}, 1.0,
                                  {"lot_infeasible": False, "notes": []}, 0.0, 0.12)
        assert card["disqualified"] is False

    def test_compose_sorts_on_rank_key_and_carries_the_names(self):
        """A source guard for the one line a behavioural test cannot reach without a compose: the
        set is sorted on `rank_key`, before and after revision, and every card carries its
        unjudged fatals."""
        import inspect
        src = inspect.getsource(CO.compose)
        assert "_sort_key = rank_key" in src
        assert src.count("key=_sort_key") == 2
        assert '"unjudged_fatal": unjudged_fatals(res)' in src
        assert '"unjudged_fatal": unjudged_fatals(res2)' in src


# ------------------------------------------------------------------ R12, the incomplete front

AX = modcache.load("axis", os.path.join(ROOT, "build", "axis.py"))
EL = modcache.load("elevation", os.path.join(ROOT, "build", "elevation.py"))


def _front_plan(upper_unplaced=0, ground_unplaced=0):
    """A one-rectangle house, entered on S, with its ground and upper front windows placed
    except the units driven off."""
    def room(rid, idx, unplaced):
        w = {"wall": "S", "count": 2, "width_ft": 3.0, "positions_ft": [8.0, 22.0]}
        if unplaced:
            w["unplaced"] = "driven"
            w["positions_ft"] = w["positions_ft"][:2 - unplaced]
        return {"id": rid, "type": "parlor", "windows": [w], "doors": [],
                "geometry": {"x_ft": 0.0, "y_ft": 0.0, "width_ft": 30.0, "depth_ft": 20.0}}
    return {"context": {"entrance_faces": "S"},
            "footprint": {"width_ft": 30.0, "depth_ft": 20.0},
            "levels": [{"index": 0, "id": "g", "rooms": [room("a", 0, ground_unplaced)]},
                       {"index": 1, "id": "u", "rooms": [room("b", 1, upper_unplaced)]}]}


class TestOneReaderOfAnIncompleteFront:
    def test_a_complete_front_is_complete(self):
        fc = AX.front_complete(_front_plan())
        assert fc["complete"] is True and fc["total_undrawn"] == 0 and fc["why"] is None

    @pytest.mark.parametrize("up,gr", [(1, 0), (0, 1), (2, 1)])
    def test_an_undrawn_unit_on_any_storey_makes_it_incomplete(self, up, gr):
        """ONE answer for the facade: the drawn layer read the ground storey's count alone, so
        a front missing only an upper window was judged for alignment with the missing window
        counted as "missing or off" -- the one cause charged twice, one storey up."""
        fc = AX.front_complete(_front_plan(upper_unplaced=up, ground_unplaced=gr))
        assert fc["complete"] is False
        assert fc["undrawn"] == {0: gr, 1: up} and fc["total_undrawn"] == up + gr
        assert f"{up + gr} declared window unit(s)" in fc["why"]

    def test_both_layers_read_the_one_reader(self):
        """A source guard over the two call sites: the drawn layer and the elevation each ask
        `axis.front_complete`, and neither reads the mirror's own count for it any more."""
        import inspect
        PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
        dl = inspect.getsource(PC.drawn_layer)
        assert "AX.front_complete(plan)" in dl
        assert 'mi.get("declared_but_unplaced")' not in dl
        be = inspect.getsource(EL.build_elevation)
        assert "front_complete(_placed_rec)" in be

    def test_the_elevation_withholds_the_five_figures_and_says_why(self):
        """Driven on a shipped placement: the same elevation with its completeness reading
        flipped from complete to incomplete must lose exactly the five figures, and state the
        reason for each."""
        import json
        GEO = modcache.load("geometry", os.path.join(ROOT, "build", "geometry.py"))
        ST = modcache.load("structure", os.path.join(ROOT, "build", "structure.py"))
        plan = json.load(open(os.path.join(ROOT, "plans", "spec-builder-colonial.json")))
        q = GEO.solve(plan, engine="heuristic")
        elev = EL.build_elevation(q, section=ST.build_section(q, geometry_result=q))
        five = EL._MIRROR_FIGURES + EL._ALIGNMENT_FIGURES
        whole = copy.deepcopy(elev)
        whole["front"]["complete"] = {"complete": True, "why": None}
        whole["front"]["mirror"] = {"verdict": "not-mirrored", "unmatched": []}
        whole["front"]["alignment"] = {"matching": 3, "max_abs_offset_in": 0.0, "missing_or_off": 0}
        m_whole = EL._derive_measurements(whole)
        assert all(k in m_whole for k in five), [k for k in five if k not in m_whole]
        part = copy.deepcopy(whole)
        part["front"]["complete"] = {"complete": False, "why": "driven"}
        m_part = EL._derive_measurements(part)
        assert [k for k in five if k in m_part] == []
        assert set(m_whole) - set(m_part) == set(five)
        # and the record the elevation wrote for itself names every withheld figure. The premise
        # is asserted rather than branched on: this plan's front IS incomplete on the heuristic
        # (2 ground units and 1 upper unit undrawn, measured 29 Sep 2026), and a guard that ran
        # only where the bug could not occur would not be one.
        assert elev["front"]["complete"]["complete"] is False, elev["front"]["complete"]
        assert elev["front"]["complete"]["undrawn"].get(1), "the upper storey's undrawn unit"
        assert set(five) <= set(elev["front"]["withheld"]), elev["front"]["withheld"]
        assert not any(k in elev["measurements"] for k in five)


# ------------------------------------------------------------------ the loop may not take a lost verdict

RV = modcache.load("revise", os.path.join(ROOT, "build", "revise.py"))


def _critique(key, present=(), unjudged=()):
    """A critique as `revise._improves` reads one: its key, its findings (a fault-present finding
    per id in `present`, fatal) and its unjudged fault rows."""
    return {"key": list(key), "placement": None, "plan": {},
            "check": {"findings": [{"id": f"fault:{fid}", "kind": "fault-present", "fault": fid,
                                    "severity": "fatal", "statement": fid} for fid in present],
                      "fault_unjudged": [{"fault": fid} for fid in unjudged]}}


class TestAVerdictLostIsNotAFaultFixed:
    """Since R4 and R12 a move that leaves a front window undrawn turns the symmetry and
    alignment faults from present to unjudged, and the key falls by two fatals. The declared
    loop compared keys and would have accepted that round; it counts the lost verdicts back now."""

    def test_a_fatal_made_unjudged_does_not_lower_the_key(self):
        old = _critique([2, 5, 3, 4], present=["one-bay-symmetry-break", "other"])
        new = _critique([1, 5, 3, 3], present=["other"], unjudged=["one-bay-symmetry-break"])
        assert RV._judged_key(new, old) == [2, 5, 3, 4]
        assert not RV._improves(new, old), "a verdict lost is not a fault fixed"

    def test_a_fatal_actually_cleared_still_improves(self):
        """The discriminator: the same key fall with the fault CLEAR rather than unjudged is an
        improvement, so the rule refuses the lost verdict and nothing else."""
        old = _critique([2, 5, 3, 4], present=["one-bay-symmetry-break", "other"])
        new = _critique([1, 5, 3, 3], present=["other"])
        assert RV._judged_key(new, old) == [1, 5, 3, 3]
        assert RV._improves(new, old)

    def test_a_lost_verdict_counts_at_the_severity_it_was_filed(self):
        old = _critique([0, 2, 0, 1])
        old["check"]["findings"] = [{"id": "fault:x", "kind": "fault-present", "fault": "x",
                                     "severity": "serious", "statement": "x"}]
        new = _critique([0, 1, 0, 0], unjudged=["x"])
        assert RV._judged_key(new, old) == [0, 2, 0, 1]


class TestTheWithheldReasonReachesTheRow:
    """`plan_check._with_dispositions` attaches the elevation's per-house reasons as `withheld`,
    beside the standing refusals in `refused` (WP-16.1)."""

    PC = modcache.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))

    def test_a_withheld_name_gets_the_elevations_reason_and_nothing_else_moves(self):
        rows = [{"fault": "a", "needs": ["fig_one", "fig_two"]}, {"fault": "b", "needs": ["other"]}]
        out = self.PC._with_dispositions(copy.deepcopy(rows), withheld={"fig_two": "the front is not whole"})
        assert out[0]["withheld"] == [{"name": "fig_two", "by": "elevation.front.withheld",
                                        "why": "the front is not whole"}]
        assert "refused_all" not in out[0], "a withheld figure is not a standing refusal"
        assert out[1] == rows[1], "a row the elevation withheld nothing from is untouched"

    def test_the_reason_still_reaches_the_row_when_the_refusal_reader_fails(self, monkeypatch):
        """The withheld reasons are the elevation's own and do not depend on `detection`, so a
        failure there degrades only the half it owns."""
        DET = self.PC._load("detection", os.path.join(ROOT, "build", "detection.py"))

        def boom():
            raise RuntimeError("driven")
        monkeypatch.setattr(DET, "refusals", boom)
        out = self.PC._with_dispositions([{"fault": "a", "needs": ["fig_two"]}],
                                         withheld={"fig_two": "the front is not whole"})
        assert out[0]["withheld"][0]["why"] == "the front is not whole"
        assert "refused" not in out[0]


# ------------------------------------------------------------------ the reclaim after the loop

class TestTheReclaimIsHeldToTheLoopsRule:
    """`compose.compose` runs the declared loop and then `reclaim`, which gives area back by
    shortening rooms. Until WP-16.1 it kept whatever the reclaim produced; measured at `a4abb85`
    that raised fatals on 4 of the 13 candidates the Georgian brief composes. The placed loop has
    rolled such a reclaim back since WP-9.2, and both now read `revise.raises_fatal_or_serious`."""

    def test_a_reclaim_that_raises_fatal_or_serious_is_worse(self):
        old = _critique([0, 20, 70, 20])
        assert RV.raises_fatal_or_serious(_critique([1, 19, 70, 21]), old), "a fatal raised"
        assert RV.raises_fatal_or_serious(_critique([0, 21, 60, 20]), old), "a serious raised"
        assert not RV.raises_fatal_or_serious(_critique([0, 20, 90, 20]), old), (
            "only the minor axis may pay for the brief's area")
        assert not RV.raises_fatal_or_serious(_critique([0, 19, 70, 19]), old)

    def test_a_fatal_the_reclaim_made_unjudged_is_counted_where_it_stood(self):
        old = _critique([1, 20, 70, 21], present=["one-bay-symmetry-break"])
        new = _critique([0, 20, 70, 20], unjudged=["one-bay-symmetry-break"])
        assert RV.raises_fatal_or_serious(new, old) is False and RV._judged_key(new, old)[:2] == [1, 20]
        # and one lost verdict beside one new serious is worse, not a trade
        worse = _critique([0, 21, 70, 21], unjudged=["one-bay-symmetry-break"])
        assert RV.raises_fatal_or_serious(worse, old)

    @staticmethod
    def _compose_with(monkeypatch, bump):
        """Compose the Georgian brief with `reclaim` replaced by one that shortens nothing and
        reports `bump` added to the repaired counts -- the rule is about what the reclaim did to
        the verdict, so the verdict is what is driven."""
        import json as _json
        brief = _json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json")))
        real = CO.reclaim
        seen = {"n": 0, "lengths": {}}

        def lengths(plan):
            return [(r["id"], r.get("length_ft")) for lv in plan["levels"] for r in lv["rooms"]]

        def fake(plan, target, tol, res):
            out = copy.deepcopy(res)
            for k, v in bump.items():
                out["counts"][k] = out["counts"].get(k, 0) + v
            seen["n"] += 1
            seen["lengths"][id(plan)] = lengths(plan)
            for lv in plan["levels"]:
                for r in lv["rooms"]:
                    if r.get("length_ft"):
                        r["length_ft"] = round(r["length_ft"] * 0.9, 1)
            return out, ["Shortened 3 rooms that were not complaining, to give back 99 sf the "
                         "repair pass had taken."]
        monkeypatch.setattr(CO, "reclaim", fake)
        res = CO.compose(brief, candidates=2, revise=False)
        monkeypatch.setattr(CO, "reclaim", real)
        assert seen["n"], "the premise: the reclaim ran"
        for c in res["candidates"]:
            c["_repaired_lengths"] = seen["lengths"].get(id(c["plan"]))
            c["_lengths"] = lengths(c["plan"])
        return res["candidates"]

    def test_a_reclaim_that_raised_a_fatal_is_rolled_back_and_said(self, monkeypatch):
        for c in self._compose_with(monkeypatch, {"fatal": 1}):
            rc = c["reclaimed"]
            assert rc and rc["rolled_back"] is True, rc
            assert rc["key_after"][0] == rc["key_before"][0] + 1
            assert c["counts"].get("fatal", 0) == rc["key_before"][0], (
                "the card must carry the repaired verdict, not the reclaim's")
            assert any("gave back no area" in d for d in c["decisions"]), c["decisions"]
            assert not any("Shortened 3 rooms" in d for d in c["decisions"]), (
                "a reclaim that was rolled back must not be reported as done")
            assert c["_repaired_lengths"] and c["_lengths"] == c["_repaired_lengths"], (
                "the record returned must carry the repaired sizes, not the shortened ones")

    def test_a_reclaim_that_raised_only_minor_is_kept(self, monkeypatch):
        for c in self._compose_with(monkeypatch, {"minor": 3}):
            rc = c["reclaimed"]
            assert rc and rc["rolled_back"] is False, rc
            assert any("Shortened 3 rooms" in d for d in c["decisions"])
            assert c["_lengths"] != c["_repaired_lengths"], "a kept reclaim keeps its lengths"
