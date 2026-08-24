"""OQ 37 -- every parti must work for the style it was written for.

Measured 24 Aug 2026: five of twenty-one partis carried FATAL findings against their own first
native style, so the composer would not recommend them for those styles. A Charleston-single-
house brief came back with a centre-passage single pile; a Creole brief came back with a
bungalow. That was the composer working exactly as designed -- a fatal is 100 points and
nativity is worth at most 140 -- on data nothing was checking.

Two of the five turned out not to be the partis' fault at all, and both were the corpus's own
first discipline inverted: unjudged reported as evaluated-and-failed. Those are pinned here too,
because they are the more dangerous kind of bug.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _compose():
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import compose
    return compose


def _brief(style, **kw):
    b = {"id": "t", "name": "t", "style": style, "target_area_sf": 2600,
         "bedrooms": 3, "bathrooms": 2.0,
         "context": {"climate_zone": "3A", "lot_width_ft": 120, "entrance_faces": "S",
                     "jurisdiction": "IRC model text, advisory", "budget_tier": "custom"},
         "household": "t"}
    b.update(kw)
    return b


def fatals(pid, style, **kw):
    c = _compose()
    plan, _log, _parti = c.instantiate(pid, _brief(style, **kw))
    res = c.PC.check(plan, c.C)
    return [f["statement"] for f in res["findings"] if f["severity"] == "fatal"]


# ---------------------------------------------------------------- the whole catalogue


def test_check_partis_runs_the_composability_check_and_is_green():
    """The check that would have caught all five at authoring time, and did not exist."""
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_partis.py")],
                          cwd=ROOT, capture_output=True, text=True)
    assert "composable against their own first native style: 21 of 21" in proc.stdout, proc.stdout[-3000:]
    assert proc.returncode == 0, proc.stdout[-3000:]


def test_the_check_can_be_skipped_without_importing_compose():
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_partis.py"),
                           "--no-compose"], cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "composable against their own" not in proc.stdout


def test_the_check_attributes_a_style_fault_to_the_style_and_not_to_the_parti():
    """Three of cape-central-chimney's four original fatals fire identically for EVERY parti
    composed for cape-cod-colonial: they are facts about that style's kit and elevation. A check
    that blamed the parti for them would generate false accusations against exactly the files it
    exists to protect, so it is differential against a control diagram."""
    def keys(pid):
        # keyed on the REQUIREMENT and not the measured value, exactly as check_partis does:
        # the same style-level test fires for every parti and each one measures its own house,
        # so the numbers differ while the failure is identical.
        return {s.split(" against ", 1)[1] for s in fatals(pid, "cape-cod-colonial")
                if " against " in s}
    mine, control = keys("cape-central-chimney"), keys("hall-and-parlor")
    assert mine and control, "the style's own fatals should still be there to be attributed"
    assert not (mine - control), mine - control


# ---------------------------------------------------------------- the five, one by one


@pytest.mark.parametrize("pid,style", [
    ("cape-central-chimney", "cape-cod-colonial"),
    ("charleston-single-piazza", "charleston-single-house"),
    ("creole-gallery", "creole-cottage-vernacular"),
    ("five-part-palladian", "colonial-revival"),
    ("ranch-tripartite", "ranch-style"),
])
def test_each_repaired_parti_has_no_fatal_of_its_own(pid, style):
    def key(s):
        return s.split(" against ", 1)[1] if " against " in s else s
    control = {key(s) for s in fatals("hall-and-parlor", style)}
    own = [f for f in fatals(pid, style) if key(f) not in control]
    assert own == [], own


def test_the_creole_repeating_chamber_no_longer_collides():
    """compose.py generates a repeating room's copies as id + 1, 2, 3..., which produced
    `chamber1` and `chamber2` -- the ids of two chambers the parti already named. Every Creole
    brief for more than two bedrooms therefore built a plan with duplicate room ids."""
    c = _compose()
    plan, _l, _p = c.instantiate("creole-gallery", _brief("creole-cottage-vernacular", bedrooms=5))
    ids = [r["id"] for lv in plan["levels"] for r in lv["rooms"]]
    assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]


def test_the_charleston_upper_hall_reaches_the_stair_hall_below_it():
    """A landing is the top of a stair and the stair hall is on the storey BELOW. Read as a
    same-floor rule it could only be satisfied by a house with a second stair hall upstairs, so
    every two-storey parti with a landing failed it. OQ 35 built the mechanism; this uses it."""
    d = json.load(open(os.path.join(ROOT, "rooms", "landing.json")))
    rule = next(r for r in d["adjacency"]["must_adjoin"] if r["room"] == "stair-hall")
    assert rule.get("vertical_ok") is True


def test_a_hyphen_is_a_gallery_not_a_back_hall():
    """back-hall's own hard rule is must_adjoin kitchen by direct door. Typed as back-halls,
    BOTH of the five-part plan's hyphens demanded a kitchen at their own end and only one wing
    has one -- an unsatisfiable requirement produced by naming the room wrongly, not by drawing
    it wrongly."""
    d = json.load(open(os.path.join(ROOT, "partis", "five-part-palladian.json")))
    hy = [r for r in d["rooms"] if r["id"].endswith("hyphen")]
    assert len(hy) == 2
    assert all(r["type"] == "gallery-corridor" for r in hy)
    # and the service rooms are all in the wing that has the kitchen
    by = {r["id"]: r for r in d["rooms"]}
    assert "kitchen" in by["mud"]["doors"]


def test_the_butlers_pantry_may_reach_its_kitchen_through_a_hyphen():
    """In a plan whose kitchen is in a dependency the pantry is in the block and the kitchen is
    in another building. Read without a via, the rule asked the pantry to be in two buildings at
    once -- and it is the same principle this room already embodies at the other end of the run:
    a named intermediary is the connection, not a failure to connect."""
    d = json.load(open(os.path.join(ROOT, "rooms", "butlers-pantry.json")))
    rule = next(r for r in d["adjacency"]["must_adjoin"] if r["room"] == "kitchen")
    assert "gallery-corridor" in (rule.get("via") or [])
    # the dining-room rule keeps NO via: a pantry that cannot touch its dining room is a pantry
    # that is not doing its job, and that one really is a defect.
    dr = next(r for r in d["adjacency"]["must_adjoin"] if r["room"] == "dining-room")
    assert not dr.get("via")


def test_a_centre_passage_is_an_entrance_hall(plan_check_module):
    """The front door opens into it and every principal room opens off it, which is the
    definition the EQUIVALENT group holds. Without it a hyphen or gallery landing on the passage
    failed gallery-corridor's own must_adjoin stair-hall, and the five-part Palladian -- a
    diagram whose whole structure is a passage with wings off it -- could not be composed."""
    assert "centre-passage" in plan_check_module._alias("entrance-hall")
    assert "entrance-hall" in plan_check_module._alias("centre-passage")


# ---------------------------------------------------------------- unjudged is not failed


def test_an_unmodelled_chimney_is_unjudged_not_absent(roof_module):
    """roof.py models gable-end stacks only, and every branch that returns an empty positions
    list says in its own note that it did NOT model the case -- a central stack, a hipped roof
    with no gable end, a ridge it could not judge. Reporting that as a count of zero handed the
    fault corpus an evaluated measurement where it had none, and faults/chimney-omitted.json
    duly fired FATAL on a parti named cape-central-chimney for having no chimney."""
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import elevation
    c = _compose()
    plan, _l, _p = c.instantiate("cape-central-chimney", _brief("cape-cod-colonial"))
    elev = elevation.build_elevation(plan)
    assert "error" not in elev
    assert elev["measurements"].get("visible_chimney_count") is None


def test_plan_check_drops_a_none_measurement_rather_than_comparing_it(plan_check_module):
    """A key present with a None value is a measurement the fault evaluator will try to compare.
    Absent is what unjudged looks like here."""
    import inspect
    src = inspect.getsource(plan_check_module.check)
    assert "if v is None: continue" in src


def test_a_fault_finding_quotes_the_test_that_failed(plan_check_module, corpus):
    """A fault carrying secondary tests can have its PRIMARY pass and a secondary fail. Reading
    results[0] then printed the passing measurement as the evidence: 'The House With No Fire: 2
    against at-least 1' on a Cape that has two chimneys -- a sentence in which every number is
    right and the claim is nonsense."""
    sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
    import core
    fault = {"id": "f", "name": "F", "slots": [], "severity": "fatal", "symptom": "s",
             "fixes": {}, "test": {"expression": "a", "threshold": 1, "direction": "at-least"},
             "secondary_tests": [{"expression": "b", "threshold": 10, "direction": "at-least"}]}
    real = core._data
    core._data = lambda: {"faults": {"f": fault}, "styles": {}}
    try:
        row = core.check_measurements({"a": 2, "b": 1})["faults_present"][0]
        assert [x["value"] for x in row["failing"]] == [1], row["failing"]
        assert row["results"][0]["value"] == 2, "results[0] is still the passing primary"
    finally:
        core._data = real
