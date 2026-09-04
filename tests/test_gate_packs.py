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
    # THE SET IS PINNED, NOT ASSERTED EMPTY, AND IT STOPPED BEING EMPTY ON 2 Sep 2026.
    # When this was written no pending node sat in the other pack's list, so endorsing either
    # alone armed nothing. Sixteen declines later the facade role on two nodes had re-attributed
    # to `facade-classical`, and both are already inside `opening-proportion` -- so for THOSE two,
    # an endorsement would switch the whole elevation generator on. That is the backlog refilling
    # changing what an endorsement MEANS, not just where it lands, and the guard caught it on the
    # first run after the batch. Anything joining this set has to be swept
    # (`build/sweep_gates.py opening-proportion --json`, diffed) before it is endorsed.
    # AND IT WENT BACK TO EMPTY ON 4 Sep 2026, BY A DIFFERENT MECHANISM AGAIN (WP-8.13). Both
    # packs declared `delivery: opt-in` in the five-pack flip, so neither reaches
    # `folk-victorian` or `greek-revival-upland-vernacular` any more and neither node carries a
    # pending gap attributed to `facade-classical`. **The two are not endorsed and nothing was
    # decided** -- the question of whether that endorsement should arm the generator is still
    # open, it has simply stopped being reachable through this pack. Empty here now means
    # "no pending node is in the other pack's list", which is what it meant when the test was
    # written; it does NOT mean the 2 Sep finding was retracted. The set is still pinned rather
    # than asserted empty, because the refill can put a node back into it at any flip.
    ARMS_IF_ENDORSED = {"facade-classical": set(),
                        "opening-proportion": set()}
    assert (op_pending & fc) == ARMS_IF_ENDORSED["opening-proportion"], (
        "the set of opening-proportion gaps that would arm the generator changed -- sweep and "
        "re-pin", sorted(op_pending & fc))
    assert (fc_pending & op) == ARMS_IF_ENDORSED["facade-classical"], (
        "the set of facade-classical gaps that would arm the generator changed -- sweep and "
        "re-pin", sorted(fc_pending & op))


def test_the_sweeper_can_tell_an_armed_gate_from_an_unarmed_one():
    """THE INSTRUMENT MUST BE ABLE TO MOVE. The first version of `sweep_gates.py` read
    `build_section()["graduation"]` — the key is `storey_graduation` — so it reported "off, 0
    findings" for all 128 styles including the 43 the pack already endorses, and would have shown
    NO CHANGE after any endorsement. An instrument that cannot move is worse than a test that
    cannot fail, because its output is a number rather than a green tick.

    THE TWO DIRECTIONS NEED TWO PACKS NOW, AND THE FLIP IS WHY (WP-8.13). Until
    `storey-graduation` declared `delivery: opt-in`, the sweep ran over all 128 styles the pack
    REACHED — 43 in its `applies_to` and 85 not — so one pack showed both verdicts and
    `not all(...)` was a real vacuity guard. The gate stops the pack at every node that has not
    opted in, so the swept population is now exactly the 43, and all 43 are armed **because the
    two populations have become the same set**. That is the gate working, and it is the
    "counterfactual becomes the status quo" shape this repository keeps meeting: the assertion's
    discriminating power came from a difference the flip removed.

    So the ARMED direction is proved on the gate pack and the UNARMED direction on a pack that is
    not a gate pack at all — `timber-panel`, which the flip programme does not cover, sweeps 23
    styles and arms none. Two packs, one control each, and the per-style equality below is
    unchanged and is still the real property."""
    sw = _mod("_sw2", "build/sweep_gates.py")
    res = sw.sweep("storey-graduation")
    verdicts = {s: any(v.get("applicable") for v in per.values())
                for s, per in res["styles"].items()}
    assert any(verdicts.values()), "the sweeper reports every style unarmed — it is reading the wrong key"
    listed = set(_pack("storey-graduation").get("applies_to") or [])
    for style, armed in verdicts.items():
        assert armed == (style in listed), (style, armed)
    assert set(verdicts) == listed, (
        "the swept population is no longer the pack's own `applies_to`; if the gate has been "
        "lifted this test needs its `not all(...)` guard back")

    unarmed = sw.sweep("timber-panel")
    uv = {s: any(v.get("applicable") for v in per.values())
          for s, per in unarmed["styles"].items()}
    assert uv, "the sweeper returned no styles for a pack that is on `cascade`"
    assert not any(uv.values()), (
        "the sweeper reports a style armed for a pack that arms no gate — it is not reading the "
        "gate at all")
