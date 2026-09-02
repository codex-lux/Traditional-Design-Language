"""Five packs' `applies_to` is not bookkeeping — it is a live gate on generated geometry.

`build/check_inheritance.py --gates` names WHICH function each one arms. Nothing measured WHAT
MOVES, so an endorsement authored to close an OQ 51 gap could switch `graduation_check` on for a
style, change `span_check`'s capacity basis, or start the elevation generator composing a
classical front — with no diff anywhere and no test going red.

These pin the gates as SETS, in the shape `tests/test_forbidden_slots.py` uses: the population a
gate fires on, held to the pack record that decides it. An endorsement that changes one has to
come here and say so, which is the whole point — it is a behavioural change wearing a data edit.
"""
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _pack(pid):
    import glob
    for p in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
        d = json.load(open(p))
        if d.get("id") == pid:
            return d
    raise AssertionError("no such pack: " + pid)


@pytest.fixture(scope="module")
def structure():
    return _mod("_structure", "build/structure.py")


def test_the_gates_table_and_the_sweeper_name_the_same_packs():
    """Two lists of gated packs exist — `check_inheritance.GATES` (which function) and
    `sweep_gates.GATED` (how to ask it). Two spellings of one fact drift; this holds them
    together, the way `test_grammar_agreement.py` holds the three citation spellings."""
    ci = _mod("_ci", "build/check_inheritance.py")
    sw = _mod("_sw", "build/sweep_gates.py")
    assert set(ci.GATES) == set(sw.GATED), (sorted(ci.GATES), sorted(sw.GATED))


def test_storey_graduation_fires_on_its_applies_to_and_nowhere_else(structure):
    """`graduation_check` returns applicable:False for a style outside the pack — that IS the
    gate. Endorsing a node into this pack makes every plan of that style answerable to a
    storey-to-storey ratio, and able to FAIL it."""
    listed = set(_pack("storey-graduation").get("applies_to") or [])
    assert len(listed) == 43, len(listed)
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    storeys = structure.storey_heights(plan)
    for style in ("tidewater-georgian", "english-georgian"):
        assert style in listed
        assert structure.graduation_check(storeys, style)["applicable"] is True, style
    for style in ("appalachian-log-house", "ranch-style", "craftsman"):
        assert style not in listed, f"{style} was endorsed — re-pin this test and say why"
        assert structure.graduation_check(storeys, style)["applicable"] is False, style


def test_timber_bay_decides_the_span_capacity_basis(structure):
    """`span_check` reads this list to choose between the light-frame joist table and the bay
    module. A node endorsed here gets a different structural verdict on the same plan."""
    listed = _pack("timber-bay").get("applies_to") or []
    assert set(listed) == set(structure._timber_bay_applies_to()), (
        "structure.py caches this list; the cache and the pack file disagree")
    assert len(listed) == 25, len(listed)
    for style in ("appalachian-log-house", "log-vernacular-american", "ranch-style"):
        assert style not in listed, f"{style} was endorsed — that changes its span capacity"


def test_the_elevation_gate_is_an_AND_and_this_is_why_it_matters():
    """`build_elevation` runs only when the style is in BOTH `opening-proportion` and
    `facade-classical`. WP-8.7 measured that NO node in either pack's unendorsed backlog is in
    the other's `applies_to`, so endorsing either one ALONE arms nothing — the generator still
    returns applicable:false. Anyone costing an endorsement by `--gates` alone will overstate it."""
    op = set(_pack("opening-proportion").get("applies_to") or [])
    fc = set(_pack("facade-classical").get("applies_to") or [])
    ci = _mod("_ci2", "build/check_inheritance.py")
    g = ci.load()
    _b, gaps, _p, _d = ci.measure(g)
    applies = ci.applies_to_index()
    un = [t for t in gaps if t[0] not in applies.get(t[3], ())]
    op_pending = {t[0] for t in un if t[3] == "opening-proportion"}
    fc_pending = {t[0] for t in un if t[3] == "facade-classical"}
    assert not (op_pending & fc), (
        "a node pending on opening-proportion is already in facade-classical: endorsing it now "
        "DOES arm the elevation generator. Sweep it and re-pin.", sorted(op_pending & fc))
    assert not (fc_pending & op), (
        "mirror case: endorsing facade-classical here would arm the generator", sorted(fc_pending & op))


def test_the_sweeper_can_tell_an_armed_gate_from_an_unarmed_one():
    """THE INSTRUMENT MUST BE ABLE TO MOVE. The first version of `sweep_gates.py` read
    `build_section()["graduation"]` — the key is `storey_graduation` — so it reported "off, 0
    findings" for all 128 styles including the 43 the pack already endorses, and would have shown
    NO CHANGE after any endorsement. An instrument that cannot move is worse than a test that
    cannot fail, because its output is a number rather than a green tick."""
    sw = _mod("_sw2", "build/sweep_gates.py")
    res = sw.sweep("storey-graduation")
    verdicts = {s: any(v.get("applicable") for v in per.values())
                for s, per in res["styles"].items()}
    assert any(verdicts.values()), "the sweeper reports every style unarmed — it is reading the wrong key"
    assert not all(verdicts.values()), "the sweeper reports every style armed — it is not reading the gate"
    listed = set(_pack("storey-graduation").get("applies_to") or [])
    for style, armed in verdicts.items():
        assert armed == (style in listed), (style, armed)
