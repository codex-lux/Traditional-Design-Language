"""WP-11.10 — the depth a roof needs, inverted from the fault's own rule and NOT enforced.

The hardest thing to test here is the refusal. A number that is computed and acted on can be
checked by its effect; a number that is computed and deliberately acted on by nothing has no
effect to check, so `TestItIsNotEnforced` checks the absence directly. An unenforced figure that
quietly starts steering the placer is exactly the failure this package refused to risk.
"""
import glob
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


DF = _load("depth_floor", f"{ROOT}/build/depth_floor.py")
ST = _load("structure", f"{ROOT}/build/structure.py")
GEO = _load("geometry", f"{ROOT}/build/geometry.py")
PC = _load("plan_check", f"{ROOT}/build/plan_check.py")
FAULT = f"{ROOT}/faults/truss-flattened-pitch.json"


@pytest.fixture
def faked_fault(tmp_path, monkeypatch):
    """Point `depth_floor` at a COPY of the fault record, never at the record itself.

    **THE FIRST VERSION OF THESE TESTS WROTE TO `faults/truss-flattened-pitch.json` AND RESTORED
    IT IN A `finally`.** That is a git-tracked corpus data file, and a `finally` does not run if
    the process is killed -- this session alone had two container restarts mid-run. The failure
    mode is the worst kind this repository has: a corrupted threshold sitting in the corpus,
    looking exactly like an authored change, in the file every other reader of that fault trusts.

    `_FAULT` is a module-level constant precisely so it can be redirected. Nothing here writes
    inside the repository.
    """
    def _fake(mutate):
        d = json.loads(open(f"{ROOT}/faults/truss-flattened-pitch.json").read())
        mutate(d)
        p = tmp_path / "truss-flattened-pitch.json"
        p.write_text(json.dumps(d, indent=2) + "\n")
        monkeypatch.setattr(DF, "_FAULT", str(p))
        return p
    return _fake


def _plans():
    out = []
    for p in sorted(glob.glob(f"{ROOT}/plans/**/*.json", recursive=True)):
        d = json.loads(open(p).read())
        if "levels" in d:
            out.append((os.path.basename(p)[:-5], d))
    return out


# --------------------------------------------------------------- read, never transcribed
class TestTheRuleIsRead:
    def test_the_threshold_comes_from_the_fault_record(self):
        thr, direction, expr = DF.fault_threshold()
        f = json.loads(open(FAULT).read())
        assert thr == f["test"]["threshold"]
        assert direction == f["test"]["direction"] == "at-least"
        assert expr == f["test"]["expression"]

    def test_the_threshold_is_not_a_literal_in_the_code(self):
        """A checker carrying a copy of the number it checks is one rule in two places -- the
        defect WP-11.7 records for `facade_share`. If the threshold appears as a CONSTANT here,
        the read is decorative.

        **The first version of this guard read lines and was wrong**: it stripped lines starting
        with `#` or a quote and so kept every prose line INSIDE the module docstring, where the
        rule is quoted three times on purpose. It reads the AST now -- docstrings and comments
        are not code, and the question is only ever about code.
        """
        import ast
        tree = ast.parse(open(f"{ROOT}/build/depth_floor.py").read())
        thr = json.loads(open(FAULT).read())["test"]["threshold"]
        nums = [n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
                and not isinstance(n.value, bool)]
        assert thr not in nums, (
            f"the fault's threshold {thr} appears as a numeric constant in build/depth_floor.py; "
            f"it must be READ from the record, never transcribed")

    def test_moving_the_fault_moves_the_floor(self, faked_fault):
        # The strongest form: change the DATA and the derived number must follow. A read that
        # cannot be shown to follow its source is indistinguishable from a literal.
        plan = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        before = DF.evaluate(plan)["min_outside_span_ft"]
        faked_fault(lambda d: d["test"].__setitem__("threshold", 0.90))
        after = DF.evaluate(plan)["min_outside_span_ft"]
        # `abs` rather than `rel`: the returned figure is rounded to three places, so an exact
        # ratio is not available and demanding one tests the rounding rather than the read.
        assert after == pytest.approx(before * 2, abs=0.005), (
            "doubling the fault's own threshold must double the span it implies")

    def test_a_fault_that_states_a_different_rule_is_refused(self, faked_fault):
        faked_fault(lambda d: d["test"].__setitem__("expression", "something_else / entirely"))
        v = DF.evaluate(json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read()))
        assert v["verdict"] == "unjudged"
        assert "no longer states the rule" in v["reason"]


# ------------------------------------------------------- the third spelling agrees with the others
class TestTheThirdSpellingAgrees:
    def test_the_pitch_reading_matches_structures_on_every_style(self):
        # `structure._style_roof_pitch` and `roof._style_roof_pitch` are already one rule in two
        # places -- roof.py's own comment says so. This is a THIRD, and it exists only because
        # depth_floor must stay a leaf. Agreement is the guard, on all of them, not on a sample.
        ids = [os.path.basename(p)[:-5] for p in sorted(glob.glob(f"{ROOT}/styles/*.json"))]
        assert len(ids) > 150, "the style corpus did not load; this test would pass vacuously"
        disagree = []
        for sid in ids:
            mine = DF.style_roof_pitch(sid)
            theirs, _id, _stmt = ST._style_roof_pitch(sid)
            if mine != theirs:
                disagree.append((sid, mine, theirs))
        assert disagree == [], f"the third spelling has drifted: {disagree[:5]}"

    def test_it_reproduces_the_between_branch(self, tmp_path, monkeypatch):
        """The `between` midpoint, DRIVEN and against an ORACLE (audit, 7 Sep 2026).

        The first version of the reading dropped `direction == "between"` entirely, and that is
        half of why it returned None where `structure` returned 8.0. The first version of this
        TEST said it was driven and was not: it globbed the shipped corpus, `pytest.skip`ped if
        no style used `between` -- a skip is a silent pass -- and then asserted agreement with
        `structure`, which `test_the_pitch_reading_matches_structures_on_every_style` above
        already asserts over all 164 styles. It could not fail in a way that test would not.

        Two things are different here. It writes its own style record, so the branch is
        exercised whatever the corpus does; and it asserts the ARITHMETIC (`between 6 and 10` is
        8.0) rather than agreement, so both spellings dropping the branch together would be
        caught. Agreement proves consistency; only an oracle proves correctness.
        """
        sid = "zz-driven-band-pitch"
        d = tmp_path / "styles"
        d.mkdir()
        (d / f"{sid}.json").write_text(json.dumps({
            "id": sid, "name": "Driven",
            "constraints": [{"id": "c1", "kind": "roof", "statement": "A band, not a figure.",
                             "test": {"expression": "roof_pitch_rise_per_12",
                                      "direction": "between", "threshold": 6, "upper": 10}}]}))
        monkeypatch.setattr(DF, "ROOT", str(tmp_path))
        assert DF.style_roof_pitch(sid) == 8.0, (
            "a pitch stated as a band must read as the midpoint of the band; None here is the "
            "branch dropped, and a wrong number is the midpoint computed wrongly")

    def test_the_foundation_cancels_out_of_the_denominator(self):
        """The identity `wall_height_ft` rests on, run rather than asserted about a constant.

        This test replaced one that compared `depth_floor.DEFAULT_GRADE_TO_FIRST_FLOOR_FT` with
        `structure`'s. Both were 2.0 and the comparison was green -- and NOTHING IN
        `depth_floor` READ ITS COPY, because the foundation cancels: `structure.roof_heights`
        adds it to the storey heights and `elevation.py` subtracts the ground storey's
        `grade_to_floor_ft`, which is the same number. The transcription could not drift into a
        wrong answer because it was not in an answer. What CAN drift is the cancellation -- a
        foundation that stopped being the same on both sides would move this file's denominator
        with nothing comparing two 2.0s to notice.

        So: build the storeys and the roof heights the way `structure` does, subtract the way
        `elevation` does, and hold the result against `wall_height_ft`. Mutation-checked --
        changing either side of the subtraction turns this red.
        """
        plan = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        storeys = ST.storey_heights(plan)
        fp = plan.get("footprint") or {}
        heights = ST.roof_heights(plan, storeys,
                                  {"width_ft": fp.get("width_ft") or 40.0,
                                   "depth_ft": fp.get("depth_ft") or 30.0})
        # build_section's own datum loop (structure.py:549-553), which is where a storey gets
        # its `grade_to_floor_ft` -- `storey_heights` does not carry one.
        running = ST.DEFAULT_GRADE_TO_FIRST_FLOOR_FT
        for st in sorted([x for x in storeys if (x.get("index") or 0) >= 0],
                         key=lambda x: x["index"]):
            st["grade_to_floor_ft"] = round(running, 3)
            if st.get("storey_height_ft") is not None:
                running += st["storey_height_ft"]
        # elevation.py:1796's own subtraction, in feet.
        elevation_wall_ft = heights["grade_to_eave_ft"] - storeys[0]["grade_to_floor_ft"]
        got, why = DF.wall_height_ft(plan)
        assert got is not None, why
        assert got == pytest.approx(elevation_wall_ft, abs=0.02), (
            f"the foundation no longer cancels: structure/elevation give {elevation_wall_ft} ft "
            f"of wall and depth_floor derives {got} ft, so the fault's denominator and this "
            f"file's inversion are measuring two different walls")
        assert got == pytest.approx(sum(s["storey_height_ft"] for s in storeys), abs=0.02)


# ------------------------------------------------------- the inversion agrees with the forward rule
class TestTheInversionAgreesWithTheFault:
    def test_no_plan_the_floor_judges_disagrees_with_the_faults_own_verdict(self):
        """The only real correctness test: solve the rule forwards and backwards and compare.

        It found a genuine defect on its first run -- `good-03-parlor-drawing-room-house` read
        `ok` while the fault CONVICTED it, because `greek-revival-american` carries an exception
        whose `bounds_test` REPLACES the primary. The floor was right about the primary and the
        primary was not the rule in force.
        """
        agree = unjudged = 0
        disagree = []
        for name, d in _plans():
            q = json.loads(json.dumps(d))
            GEO._SOLVE_CACHE.clear()
            GEO.solve(q, engine="heuristic")
            sec = ST.build_section(q)
            t = (sec.get("wall") or {}).get("exterior_in") or 0.0
            fp = q["footprint"]
            v = DF.evaluate(q, exterior_wall_in=t,
                            clear_span_ft=min(fp["width_ft"], fp["depth_ft"]))
            convicted = any("The Truss Default" in f.get("statement", "")
                            for f in PC.check(q)["findings"])
            if v["verdict"] == "unjudged":
                unjudged += 1
                continue
            expect = (v["verdict"] == "below")
            # COLLECTED, NOT RAISED IN THE LOOP (audit, 7 Sep 2026). This asserted inside the
            # loop, so `disagree` could never be incremented and `(agree, disagree) == (2, 0)`
            # was half a tautology -- and worse, the first disagreement stopped the sweep, so a
            # reader learned about one plan where the point of the sweep is how many.
            if expect != convicted:
                disagree.append(
                    f"{name}: the floor says {v['verdict']} and the fault says "
                    f"{'CONVICTS' if convicted else 'clear'} -- the inversion and the forward "
                    f"rule disagree, so one of them is not the rule the corpus states")
            else:
                agree += 1
        assert disagree == [], "\n".join(disagree)
        assert agree == 2
        assert unjudged == 14, "the judged/unjudged split moved; re-measure and say what changed"

    def test_a_substituted_bounds_test_is_unjudged_and_not_ok(self):
        sub = DF.substituted_bounds_test("greek-revival-american")
        assert sub is not None, "the exception this test drives has gone from the fault record"
        d = json.loads(open(f"{ROOT}/plans/reference/"
                            f"good-03-parlor-drawing-room-house.json").read())
        v = DF.evaluate(d, clear_span_ft=1000.0)   # absurdly wide: would be `ok` if it were judged
        assert v["verdict"] == "unjudged"
        assert "REPLACES the primary" in v["reason"]

    def test_a_style_with_no_pitch_is_unjudged_and_not_ok(self):
        d = json.loads(open(f"{ROOT}/plans/spec-builder-colonial.json").read())
        v = DF.evaluate(d, clear_span_ft=1.0)      # absurdly narrow: would be `below` if judged
        assert v["verdict"] == "unjudged"
        assert "no migrated roof_pitch_rise_per_12" in v["reason"]


# --------------------------------------------------------------------- the denominator
class TestTheDenominator:
    def test_it_is_the_storey_height_and_not_the_ceiling(self):
        """The bug this signature was changed to prevent: the first version took a list and its
        own CLI passed `floor_to_ceiling_ft` (21 ft on the Tidewater plan) where the fault's
        denominator wants the STOREY heights storeys.py derives (23.44). An 11.6% error in the
        flattering direction."""
        plan = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        wall, why = DF.wall_height_ft(plan)
        assert why is None
        ceilings = sum(lv["floor_to_ceiling_ft"] for lv in plan["levels"])
        assert wall > ceilings, "the denominator is the ceiling height, not the storey height"
        sec = ST.build_section(json.loads(json.dumps(plan)))
        theirs = sec["roof"]["grade_to_eave_ft"] - sec["storeys"][0]["grade_to_floor_ft"]
        assert wall == pytest.approx(theirs, abs=0.02), (
            "the denominator disagrees with the one the elevation actually publishes")

    def test_a_level_with_no_ceiling_is_unjudged_rather_than_summed_as_zero(self):
        plan = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        for lv in plan["levels"]:
            lv.pop("floor_to_ceiling_ft", None)
            for r in lv.get("rooms", []):
                r.pop("ceiling_ft", None)
        wall, why = DF.wall_height_ft(plan)
        assert wall is None and "state no ceiling height" in why
        assert DF.evaluate(plan, clear_span_ft=1.0)["verdict"] == "unjudged"


# ------------------------------------------------------------------ it is REPORTED, not enforced
class TestItIsNotEnforced:
    def test_the_placer_does_not_read_it_even_transitively(self):
        """The refusal is the package, so the guard must cover the whole reach of a solve.

        **THE FIRST VERSION OF THIS GUARD READ THREE FILES' SOURCE AND WAS EVADABLE TWO WAYS**,
        found by an adversarial audit of this session's own work. `build/geometry.py` loads
        `plan_check.py`, `openings.py`, `check_openings.py`, `structure.py` and `geometry_cp.py`;
        NONE of those was in the guarded triple, so `import depth_floor` inside `structure.py`
        called from `roof_heights` would cap the placer with this test still green -- which is
        exactly what the open question refuses. And a rename of `build/depth_floor.py` silently
        defused the whole thing, because a negative substring assertion over a name that no
        longer exists cannot fail.

        So it runs a solve and asks what was actually LOADED. That catches a transitive import, a
        rename, and any spelling of the import -- `importlib`, `_mod`, `from . import` alike.
        """
        import sys as _sys
        MC = _load("modcache", f"{ROOT}/build/modcache.py")
        for mod in list(_sys.modules):
            if "depth_floor" in mod:
                del _sys.modules[mod]
        cache = getattr(MC, "_CACHE", None)
        if isinstance(cache, dict):
            for k in [k for k in cache if "depth_floor" in str(k)]:
                cache.pop(k)
        q = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        GEO._SOLVE_CACHE.clear()
        GEO.solve(q, engine="heuristic")
        PC.check(q)
        loaded = [m for m in _sys.modules if "depth_floor" in m]
        cached = ([k for k in cache if "depth_floor" in str(k)] if isinstance(cache, dict) else [])
        assert not loaded and not cached, (
            f"a solve loaded depth_floor ({loaded or cached}). That makes an unenforced "
            f"diagnostic into a constraint on the placer, which "
            f"oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced refuses until the "
            f"licence question is ruled.")

    def test_no_build_module_but_the_instrument_names_it(self):
        """The source half, kept beside the behavioural one because they fail on different
        mutations: an import added but not yet exercised on this plan is invisible to a solve and
        visible here. The allow-list is the two files entitled to read it."""
        import glob as _glob
        allowed = {"depth_floor.py", "diagnose_sheet.py"}
        offenders = [os.path.basename(f) for f in sorted(_glob.glob(f"{ROOT}/build/*.py"))
                     if os.path.basename(f) not in allowed
                     and "depth_floor" in open(f).read()]
        assert offenders == [], (
            f"{offenders} name depth_floor. Only the module itself and the instrument may.")

    def test_the_footprint_is_byte_identical_with_the_module_present(self):
        # The complement of the source guard: the numbers, not the imports.
        want = {"tidewater-georgian-careful": (63, 38.17), "spec-builder-colonial": (50.0, 30.75)}
        for name, (w, dpt) in want.items():
            q = json.loads(open(f"{ROOT}/plans/{name}.json").read())
            GEO._SOLVE_CACHE.clear()
            GEO.solve(q, engine="heuristic")
            assert (q["footprint"]["width_ft"], q["footprint"]["depth_ft"]) == (w, dpt)

    def test_the_instrument_reports_it(self):
        DS = _load("diagnose_sheet", f"{ROOT}/build/diagnose_sheet.py")
        q = json.loads(open(f"{ROOT}/plans/tidewater-georgian-careful.json").read())
        GEO._SOLVE_CACHE.clear()
        GEO.solve(q, engine="heuristic")
        rf = DS.roof_depth_floor(q)
        assert rf["verdict"] == "ok"
        assert rf["min_clear_span_ft"] < rf["min_outside_span_ft"], (
            "the wall thickness was not applied; the fault measures the OUTSIDE envelope and the "
            "placer works in clear extent")
