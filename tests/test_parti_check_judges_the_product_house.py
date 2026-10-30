"""check_partis' composability check judges the house the product builds, and an unjudged fatal
fault is not a pass (16 Oct 2026).

`docs/reports/the-side-hall-front-is-the-placers-2026-10-16.md` is the account, and
`oq/the-parti-check-places-a-house-the-product-does-not-build` the question. Two facts:

1. The check handed `plan_check` a plan that named no parti, so the placer laid the house on its own
   defaults (side-hall-townhouse: FOUR bays at the placer's 10 ft module) where the product names
   the parti and the placer reads the diagram's own 8 ft module.
2. On the product's house the fault that convicted the parti is not failed but UNEVALUATED. A check
   counting fatal findings reads that as a pass, so naming the parti alone would have turned 20 of
   21 into 21 of 21 by making the fault stop being asked. An unjudged fatal fault is reported, with
   its reason, differential against the control, and it is NOT composable.

The branches are driven with a stand-in composer (`check_composability(..., compose=...)` is the
seam), because the only parti the shipped catalogue lets reach them is two, and a branch reached by
two records whose states may change cannot be guarded by them (WP-8.11).
"""
import os
import re
import subprocess
import sys
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))

import check_partis as CP                                              # noqa: E402

CONTROL = "hall-and-parlor"


def _row(fault="even-bay-front", severity="fatal", why="the upper storey draws no opening",
         needs=None, name="The Front With No Centre"):
    r = {"fault": fault, "name": name, "severity": severity, "needs": needs or ["upper_floor_opening_count"]}
    if why:
        r["withheld"] = [{"name": "upper_floor_opening_count", "by": "elevation.front.withheld", "why": why}]
    return r


def _fake(by_pid, seen=None):
    """A composer whose PC.check answers from `by_pid[pid] = (findings, fault_unjudged)`, and which
    records the `parti` each plan carried when it was judged."""
    def instantiate(pid, brief):
        return {"id": pid, "style": brief["style"]}, [], {}

    def check(plan, C):
        if seen is not None:
            seen[plan["id"]] = plan.get("parti")
        findings, unjudged = by_pid[plan["id"]]
        return {"findings": findings, "fault_unjudged": unjudged}
    return types.SimpleNamespace(instantiate=instantiate, PC=types.SimpleNamespace(check=check), C={})


def _run(by_pid, pids=("side-hall-townhouse",), seen=None):
    rep = CP.Report()
    partis = [{"id": CONTROL, "styles": ["adam-style"]}] + [{"id": p, "styles": ["adam-style"]} for p in pids]
    by_pid = {CONTROL: ([], []), **by_pid}
    counts, unjudged = CP.check_composability(rep, partis, compose=_fake(by_pid, seen))
    return rep, counts, unjudged


# ---------------------------------------------------------------- the parti is named


def test_the_plan_names_its_parti_when_it_is_judged():
    """Both the parti and the control: the control is the baseline the parti is subtracted from, and
    a baseline built on a different house subtracts the wrong things."""
    seen = {}
    _run({"side-hall-townhouse": ([], [])}, seen=seen)
    assert seen == {CONTROL: CONTROL, "side-hall-townhouse": "side-hall-townhouse"}, seen


# ---------------------------------------------------------------- an unjudged fatal fault is not a pass


def test_an_unjudged_fatal_fault_the_control_judges_is_an_error_of_the_parti():
    rep, counts, unjudged = _run({"side-hall-townhouse": ([], [_row()])})
    assert counts["side-hall-townhouse"] == 0, "no fatal FINDING: the fault was never evaluated"
    assert set(unjudged["side-hall-townhouse"]) == {"even-bay-front"}
    msgs = [m for w, m in rep.errors if w == "parti:side-hall-townhouse"]
    assert len(msgs) == 1 and "UNJUDGED" in msgs[0] and "even-bay-front" in msgs[0], rep.errors
    assert "Unjudged is not passed" in msgs[0]


def test_the_error_says_why_it_could_not_be_judged():
    rep, _c, _u = _run({"side-hall-townhouse": ([], [_row(why="the upper storey draws no opening on the front")])})
    assert "the upper storey draws no opening on the front" in rep.errors[0][1]


def test_a_fault_withheld_for_want_of_a_measurement_names_the_measurement():
    row = _row(why=None, needs=["visible_chimney_count"], name="The House With No Fire", fault="chimney-omitted")
    rep, _c, _u = _run({"side-hall-townhouse": ([], [row])})
    assert "it needs visible_chimney_count" in rep.errors[0][1], rep.errors


def test_an_unjudged_fatal_fault_the_control_shares_is_the_styles_and_not_the_partis():
    """Twenty-odd fatal faults are unjudged for EVERY diagram because nothing supplies the
    measurement. Blaming a parti for one the control has too is the false accusation the fatal
    differential exists to prevent."""
    shared = _row(fault="pork-chop-return", why=None, needs=["count_of_cornice_returns_drawn_at_the_gable_ends"])
    rep, _c, unjudged = _run({"side-hall-townhouse": ([], [shared]), CONTROL: ([], [shared])})
    assert rep.errors == [], rep.errors
    assert unjudged["side-hall-townhouse"] == {}


def test_the_control_has_no_unjudged_fault_of_its_own():
    """The control is the definition of a standing gap. Attributing its twenty to it would put twenty
    errors on the one diagram everything else is subtracted against."""
    rep, _c, unjudged = _run({CONTROL: ([], [_row(), _row(fault="pork-chop-return")]),
                              "side-hall-townhouse": ([], [])})
    assert rep.errors == [], rep.errors
    assert unjudged[CONTROL] == {}


def test_only_a_fatal_unjudged_fault_counts():
    rep, _c, unjudged = _run({"side-hall-townhouse": ([], [_row(severity="serious"), _row(severity="minor")])})
    assert rep.errors == [] and unjudged["side-hall-townhouse"] == {}


def test_a_fatal_finding_is_still_an_error_of_the_parti_and_counts_as_one():
    fatal = {"severity": "fatal", "layer": "fault", "rule": "even-bay-front", "room": None,
             "statement": "The Front With No Centre: 1 against between 3 and 7."}
    rep, counts, unjudged = _run({"side-hall-townhouse": ([fatal], [])})
    assert counts["side-hall-townhouse"] == 1 and unjudged["side-hall-townhouse"] == {}
    assert any("FATAL against its own style" in m for _w, m in rep.errors), rep.errors


# ---------------------------------------------------------------- the shipped catalogue, run for real


@pytest.fixture(scope="module")
def shipped():
    proc = subprocess.run([sys.executable, os.path.join(ROOT, "build", "check_partis.py")],
                          cwd=ROOT, capture_output=True, text=True)
    return proc


def _listed(out):
    """The pids printed under the composable line, with the kind of reason each was listed for."""
    return {m.group(2): m.group(1) for m in
            re.finditer(r"^\s+\d+ (fatal|unjudged fatal fault\(s\))\s+(\S+?):?(?:\s|$)", out, re.M)}


def test_composable_excludes_every_parti_listed_under_it(shipped):
    """`N of M` is M minus the parti printed under it, whichever reason they were printed for. A
    summary that counted only the FATAL ones would say 20 of 21 over two parti it lists as unsure."""
    m = re.search(r"composable against their own first native style: (\d+) of (\d+)", shipped.stdout)
    assert m, shipped.stdout[-2000:]
    n, total = int(m.group(1)), int(m.group(2))
    listed = _listed(shipped.stdout)
    assert listed, "the shipped catalogue lists at least one parti under the summary (premise)"
    assert n == total - len(listed), (n, total, listed)


def test_the_shipped_catalogue_carries_exactly_these_unjudged_fatal_faults(shipped):
    """Pinned BY IDENTITY, so a fix must remove its entry and a new one fails. Each is a real
    state of the product: side-hall-townhouse's placed upper storey draws no opening on the front,
    and cape-central-chimney's central stack is not modelled (roof.py models gable-end stacks only),
    which `test_parti_composability.py::test_an_unmodelled_chimney_is_unjudged_not_absent` pins as
    the correct state of that measurement."""
    got = {(m.group(1), m.group(2)) for m in
           re.finditer(r"parti:(\S+): UNJUDGED fatal fault against its own style '[^']+': '[^']+' \(([^)]+)\)", shipped.stdout)}
    # THE SIDE HALL LEAVES THIS LIST AT PHASE 17 (29 Oct 2026) BY BEING JUDGED, NOT BY BEING FIXED.
    # A composed plan names its parti and its entrance front now (WP-17.2), so the elevation judges
    # the side hall's front: its even-bay fault is a FATAL verdict on the drawn front, "1 against
    # between 3 and 7". The finding is asserted in its new state, so it cannot leave both lists.
    assert got == {("cape-central-chimney", "chimney-omitted")}, got
    assert re.search(r"parti:side-hall-townhouse: FATAL against its own style '[^']+': "
                     r"The Front With No Centre", shipped.stdout), shipped.stdout[-3000:]


def test_naming_the_parti_gives_the_house_the_product_builds():
    """The reason the plan is named, held on the real placer with the check's own brief (a 120 ft lot,
    so the lot does not cap the count): unnamed, the diagram is laid on the placer's 10 ft module;
    named, on its own 8 ft one. The MODULE is the stable fact: the bay count follows it (four bays
    unnamed, five named, at the same 40 ft), and on a 30 ft townhouse lot the same naming gives
    the three bays at 24 ft that the type is."""
    import compose
    geo = compose.PC._load("geometry", os.path.join(ROOT, "build", "geometry.py"))
    parti = compose.PARTIS["side-hall-townhouse"]

    def footprint(named, lot):
        brief = {"id": "t", "name": "t", "style": "adam-style", "target_area_sf": 2600, "bedrooms": 3,
                 "bathrooms": 2.0,
                 "context": {"climate_zone": "3A", "lot_width_ft": lot, "entrance_faces": "S",
                             "jurisdiction": "IRC model text, advisory", "budget_tier": "custom"},
                 "household": "t"}
        plan, _l, _p = compose.instantiate("side-hall-townhouse", brief)
        # THE COMPOSER NAMES THE PARTI ITSELF SINCE PHASE 17 (29 Oct 2026, WP-17.2), so the
        # UNNAMED reading is the record with the name taken off
        assert plan.get("parti") == "side-hall-townhouse", "the composer names the parti (WP-17.2)"
        if not named:
            plan.pop("parti")
        placed = geo.solve(plan, parti=parti if named else None, engine="heuristic")
        pl = placed if "levels" in placed else placed.get("plan", placed)
        return pl.get("footprint") or {}
    unnamed, named = footprint(False, 120), footprint(True, 120)
    assert unnamed.get("bay_module_ft") == 10 and named.get("bay_module_ft") == 8, (unnamed, named)
    assert named.get("bays") != unnamed.get("bays"), (unnamed, named)
    townhouse = footprint(True, 30)
    assert (townhouse.get("bays"), townhouse.get("width_ft")) == (3, 24), townhouse


def _side_hall_even_bay(type_pass, structural, monkeypatch):
    """even-bay-front's verdict on the composed side hall under check_partis' own brief (adam-style,
    2,600 sf, a 120 ft lot), the plan naming its parti, `plan_check` on the declared record -- the
    deterministic heuristic placement. `type_pass` False stands `compose_to_the_type` down;
    `structural` True puts the bath's claim back as `stacks_over`, the field it had before ruling 5's
    re-filing. Returns "present", "unjudged", "not-applicable" or "clear"."""
    import compose
    geo = compose.PC._load("geometry", os.path.join(ROOT, "build", "geometry.py"))
    # a PRIVATE solve cache before any solve: this test changes what the composer writes, and a
    # record placed under one cell must not be read back under another (WP-14.33's trap)
    monkeypatch.setattr(geo, "_SOLVE_CACHE", {})
    brief = {"id": "check", "name": "check", "style": "adam-style", "target_area_sf": 2600,
             "bedrooms": 3, "bathrooms": 2.0,
             "context": {"climate_zone": "3A", "lot_width_ft": 120, "entrance_faces": "S",
                         "jurisdiction": "IRC model text, advisory", "budget_tier": "custom"},
             "household": "check"}
    if not type_pass:
        monkeypatch.setattr(compose, "compose_to_the_type", lambda *a, **k: None)
    plan, _l, _p = compose.instantiate("side-hall-townhouse", brief)
    plan["parti"] = "side-hall-townhouse"
    bath = next(r for lv in plan["levels"] for r in lv["rooms"] if r["id"] == "primarybath")
    assert bath.get("wet_stack_with") == "powder" and not bath.get("stacks_over"), (
        "premise: the shipped parti files the bath over the powder room as a wet stack", bath)
    if structural:
        bath["stacks_over"] = bath.pop("wet_stack_with")
    res = compose.PC.check(plan, compose.C)
    if any(f.get("layer") == "fault" and (f.get("fault") or f.get("id")) == "even-bay-front"
           for f in res["findings"]):
        return "present"
    if any(r["fault"] == "even-bay-front" for r in res["fault_unjudged"]):
        return "unjudged"
    if any(r["fault"] == "even-bay-front" for r in res["fault_not_applicable"]):
        return "not-applicable"
    return "clear"


def test_the_side_halls_conviction_has_two_sufficient_causes(monkeypatch):
    """THE AUDIT OF PHASE 17 (30 Oct 2026, finding 49), a MEASUREMENT PIN over four cells. The side
    hall's even-bay fault went from unjudged to judged-and-failing at Phase 17. 01f11b2's message
    gave the type pass as the cause; the report's section IX and the open question's amendment gave
    ruling 5's re-filing of the bath's claim, "with the type pass switched off, the conviction
    stands, so the type pass is not the cause". Measured both ways on one instrument, EITHER change
    alone convicts: only with the type pass off AND the claim back as `stacks_over` does the fault
    read unjudged, the parent's state. So "buying the unjudged back" needs both undone, not one. If
    this table changes, every account of the cause has to be re-read."""
    cells = {}
    for type_pass in (True, False):
        for structural in (False, True):
            cells[(type_pass, structural)] = _side_hall_even_bay(type_pass, structural, monkeypatch)
            monkeypatch.undo()
    assert cells == {(True, False): "present", (False, False): "present",
                     (True, True): "present", (False, True): "unjudged"}, cells
