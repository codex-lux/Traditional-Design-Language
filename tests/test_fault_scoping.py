"""OQ 63 -- a fault's secondary tests were written for one style and run against every style.

`check_measurements` reports a fault present when ANY of its tests fails, and a secondary test
scoped in its own note to one style was therefore failing houses of every other. Measured before
the fix: **17 of 129 styles could not return a clean plan under their own native diagram**, and
the largest single cause was `truss-flattened-pitch`, whose own note reads "The Georgian band,
8:12 to 10:12. Substitute the style's own band: Cape 36.9-45, Tudor Revival 39.8-53.1, ..." --
an instruction to substitute that nothing performed.

WP-14.5 (20 Sep 2026) performed it, and this file carries both halves. A scope is not a
substitution -- OQ 63 said so in writing -- and the measurement of the difference is that a
scope naming three Georgian ids reaches 77 of 164 styles through the kit cascade, so seven
styles went on being failed for having their own correct pitch. The pitch secondary carries
`band_from_style` now and no band of its own.
"""
import glob
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def core():
    sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
    import core
    return core


def fault(fid):
    return json.load(open(os.path.join(ROOT, "faults", "%s.json" % fid)))


# ---------------------------------------------------------------- the mechanism


def test_absent_applies_to_styles_means_every_style():
    """The behaviour before the field existed, so every fault already in the corpus stays valid."""
    c = core()
    D = c._data()
    assert c._test_applies({"expression": "x"}, "cape-cod-colonial", D) is True
    assert c._test_applies({"expression": "x"}, None, D) is True


def test_a_scoped_test_is_matched_against_the_inheritance_chain():
    """A test scoped to a parent still applies to its descendants -- tidewater-georgian is a
    variant of georgian-colonial-american and inherits its pitch band with everything else."""
    c = core()
    D = c._data()
    t = {"expression": "x", "applies_to_styles": ["georgian-colonial-american"]}
    assert c._test_applies(t, "georgian-colonial-american", D)
    assert c._test_applies(t, "tidewater-georgian", D)
    assert not c._test_applies(t, "cape-cod-colonial", D)
    assert not c._test_applies(t, None, D), "no style means it cannot be shown to apply"


def test_a_test_for_another_style_is_not_run_and_that_is_not_the_same_as_passing():
    """A test that is not for this house says nothing about this house. It must not appear in
    the evaluated results, in either direction -- reported as passing would be as wrong as
    reported as failing."""
    c = core()
    f = {"id": "t", "name": "T", "slots": [], "severity": "fatal", "symptom": "s", "fixes": {},
         "applies_to": ["universal"],
         "test": {"expression": "a", "threshold": 1, "direction": "at-least"},
         "secondary_tests": [{"expression": "b", "threshold": 10, "direction": "at-least",
                              "applies_to_styles": ["tudor-revival"]}]}
    real = c._data
    c._data = lambda: {"faults": {"t": f}, "styles": {"cape-cod-colonial": {"id": "cape-cod-colonial"}}}
    try:
        r = c.check_measurements({"a": 2, "b": 1}, style="cape-cod-colonial")
        assert r["faults_present"] == [], "the Tudor test must not fail a Cape"
        assert len(r["faults_clear"][0]["results"]) == 1, "and must not be reported as passing"
        r2 = c.check_measurements({"a": 2, "b": 1}, style="tudor-revival")
        assert r2["faults_present"], "and must still fail a Tudor"
    finally:
        c._data = real


# ---------------------------------------------------------------- the sweep


@pytest.mark.parametrize("fid,idx,want", [
    ("chimney-omitted", 0, "tudor-revival"),
    ("chimney-omitted", 1, "prairie-school"),
    ("parapet-as-stage-flat", 3, "pueblo-revival"),
    ("return-shallower-than-tall", 1, "georgian-colonial-american"),
    ("sunken-dormer", 1, "georgian-colonial-american"),
])
def test_each_scoped_test_says_so_and_says_why(fid, idx, want):
    t = fault(fid)["secondary_tests"][idx]
    assert want in t["applies_to_styles"], (fid, idx)
    assert "OQ 63" in t["note"], "a scoping with no stated reason is a scoping nobody can check"


def test_the_pueblo_parapet_test_is_the_one_that_fails_a_house_for_being_level():
    """The only inverted test in the corpus. Applied universally it failed every correctly-built
    Territorial, Mediterranean and commercial parapet there is."""
    t = fault("parapet-as-stage-flat")["secondary_tests"][3]
    assert t["applies_to_styles"] == ["pueblo-revival"]
    assert t["expression"] == "parapet_top_deviation_from_horizontal_deg"
    assert t["direction"] == "at-least"


def test_a_fault_already_scoped_to_its_styles_was_left_alone():
    """raised-cape-eave's secondary tests all name a Cape, and its `applies_to` is already four
    Cape-family styles. Scoping a test inside a fault that is already scoped buys nothing and
    risks narrowing it below what its own fault says. Only tests NARROWER than their fault were
    touched."""
    f = fault("raised-cape-eave")
    assert f["applies_to"] == ["cape-cod-colonial", "cape-cod-revival",
                               "new-england-colonial", "minimal-traditional"]
    for t in f["secondary_tests"]:
        assert "applies_to_styles" not in t


def test_five_tests_are_scoped_and_the_sixth_became_a_substitution():
    """Twenty-four of 273 secondary tests name a style in their note. Six of them named it as a
    SCOPE; the rest name it as context, as a reference band, or as the case the test exists to
    discriminate -- `frieze-as-fascia-board` separates a genuine Greek Revival frieze-band
    window from a collision, and scoping it to Greek Revival would remove the very case it is
    for. Scoping on a keyword match would have been worse than scoping nothing.

    IT IS FIVE NOW, AND THE SIXTH WAS NOT UNSCOPED -- IT WAS REPLACED BY SOMETHING STRONGER.
    `truss-flattened-pitch`'s pitch secondary asked in its own note for the style's own band to
    be SUBSTITUTED, and OQ 63 recorded that a scope is not a substitution: *"the right direction
    and not the destination"*. WP-14.5 measured the distance -- over the 41 styles the elevation
    layer speaks for, 10 of the 15 that supply a pitch failed the Georgian band, the scope
    removed 3, and all 10 sit inside the band their own style node states, so seven went on
    being failed for having their own correct pitch. That test now carries `band_from_style` and
    no band of its own; the test below asserts it, so this count falling to five cannot be read
    as a scoping being quietly dropped.
    """
    n = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "faults", "*.json"))):
        for t in (json.load(open(p)).get("secondary_tests") or []):
            if t.get("applies_to_styles"): n += 1
    assert n == 5, n


def test_the_pitch_test_carries_no_band_of_its_own():
    """The other half of the count above, so the pair cannot both be satisfied by deletion.

    A test asking for the style's band may state no `threshold` and no `upper`: two numbers for
    one quantity is the stale copy the field exists to prevent, and the schema refuses it. What
    IS asserted here is that this particular test really made the trade -- a `band_from_style`
    added beside a surviving hardcoded band would be schema-invalid but would also satisfy a
    test that only looked for the field.
    """
    t = fault("truss-flattened-pitch")["secondary_tests"][0]
    assert t["expression"] == "roof_slope_angle_deg"
    assert t["band_from_style"]["expression"] == "roof_pitch_rise_per_12"
    assert t["band_from_style"]["convert"] == "rise_per_12_to_degrees"
    assert "applies_to_styles" not in t, "a substitution needs no scope; the band IS the scope"
    assert "threshold" not in t and "upper" not in t, (
        "the Georgian band is still here -- one quantity, two numbers, which is the copy this "
        "mechanism exists to remove")
    assert "WP-14.5" in t["note"]


def test_three_georgian_ids_reach_seventy_seven_styles():
    """WHY A SCOPE WAS NOT ENOUGH, as a number rather than as an argument.

    `_test_applies` matches `applies_to_styles` against `_style_chain`, which is the resolve_kit
    cascade plus six hops of `member_of`. A scope naming three Georgian ids therefore reaches
    nearly half the corpus -- Greek Revival, the Federal styles, Jeffersonian Classicism,
    Italian Renaissance Revival, Minimal Traditional and Neoclassical Revival among them, every
    one of which states a pitch band of its own.

    Two scoped tests still rest on exactly that list (`return-shallower-than-tall` and
    `sunken-dormer`), which is why this is asserted rather than left in a report:
    `oq/a-test-scope-is-matched-against-the-kit-cascade`.
    """
    c = core()
    D = c._data()
    want = {"georgian-colonial-american", "english-georgian", "georgian-revival"}
    reach = [s for s in D["styles"] if c._style_chain(s, D) & want]
    assert len(D["styles"]) == 164, "the corpus did not load; this would pass vacuously"
    assert len(reach) == 77, len(reach)
    for s in ("greek-revival-american", "new-england-federal", "jeffersonian-classicism",
              "italian-renaissance-revival", "minimal-traditional", "neoclassical-revival"):
        assert s in reach, s
