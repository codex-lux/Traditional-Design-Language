"""WP-14.5 -- the band comes from the style, or the test does not run.

OQ 63 scoped `truss-flattened-pitch`'s pitch secondary to the Georgian family and recorded in
writing that a scope is *"the right direction and not the destination"*: the test's own note
asks the engine to *"Substitute the style's own band"*, and a scope performs no substitution.

WHAT THE SCOPE REALLY DID, measured before anything moved. Over the 41 styles the elevation
layer speaks for, 15 supply a pitch at all; 10 of those 15 failed the Georgian band; the scope
removed 3; and ALL TEN -- scoped away or still convicted -- sit INSIDE the band their own style
node states. Seven styles went on being failed for having their own correct pitch, because
`_test_applies` matches against the KIT CASCADE and three Georgian ids reach 77 of 164 styles.

The numbers were never missing: `build/elevation.py` DERIVES the `roof_slope_angle_deg` the
fault reads from the style's own migrated `roof_pitch_rise_per_12` constraint, and the fault
then judged it against another tradition's band.
"""
import copy
import glob
import json
import math
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache as MC  # noqa: E402

CORE = MC.load("core", os.path.join(ROOT, "mcp_server", "core.py"))
FT = MC.load("fault_thresholds", os.path.join(ROOT, "build", "fault_thresholds.py"))
EL = MC.load("elevation", os.path.join(ROOT, "build", "elevation.py"))

PITCH = "roof_pitch_rise_per_12"
ASK = {"expression": "roof_slope_angle_deg", "units": "deg",
       "band_from_style": {"expression": PITCH, "convert": "rise_per_12_to_degrees"}}


def deg(rise):
    return round(math.degrees(math.atan(rise / 12.0)), 1)


# ------------------------------------------------------------------ the reader


def test_the_band_reader_answers_all_three_directions_and_takes_the_direction_too():
    """`between`, `at-least` and `at-most` are three different bands and not one with holes.

    The `at-most` case is the one that bites: the evaluator reads `threshold` for every
    direction but `between`, so a constraint stated as an upper bound has to move its number
    across. Getting that wrong turns `jeffersonian-classicism`'s `at-most 4:12` into an
    `at-most None` that compares against nothing.
    """
    D = CORE._data()
    assert CORE.style_band("cape-cod-colonial", PITCH, D)[:3] == ("between", 9, 12)
    assert CORE.style_band("tudor-revival", PITCH, D)[:3] == ("at-least", 10, None)
    assert CORE.style_band("jeffersonian-classicism", PITCH, D)[:3] == ("at-most", None, 4)

    cape = CORE._test_for_style(ASK, "cape-cod-colonial", D)
    assert (cape["direction"], cape["threshold"], cape["upper"]) == ("between", 36.9, 45.0)
    tud = CORE._test_for_style(ASK, "tudor-revival", D)
    assert (tud["direction"], tud["threshold"], tud["upper"]) == ("at-least", 39.8, None), (
        "an `at-least` constraint is open above and must stay open -- the note this replaces "
        "said 'Tudor Revival 39.8-53.1' and 53.1 is in no record in this corpus")
    jef = CORE._test_for_style(ASK, "jeffersonian-classicism", D)
    assert (jef["direction"], jef["threshold"], jef["upper"]) == ("at-most", 18.4, None)


def test_a_style_stating_no_band_is_not_run_and_that_is_not_a_pass():
    """The three-state discipline. A style with no migrated pitch constraint must not fall back
    to the band written for somebody else, and must not be reported as clear either."""
    D = CORE._data()
    assert CORE.style_band("art-deco", PITCH, D) is None
    assert CORE._test_for_style(ASK, "art-deco", D) is None
    assert CORE._test_for_style(ASK, None, D) is None, (
        "no style means no band; substituting anything here would be inventing one")

    f = {"id": "t", "name": "T", "slots": [], "severity": "fatal", "symptom": "s", "fixes": {},
         "applies_to": ["universal"], "test": dict(ASK)}
    real = CORE._data
    CORE._data = lambda: {"faults": {"t": f}, "styles": {"nb": {"id": "nb"}}}
    try:
        r = CORE.check_measurements({"roof_slope_angle_deg": 5.0}, style="nb")
        assert r["faults_present"] == [], "a band nobody wrote cannot convict"
        assert r["faults_clear"] == [], "and must not be reported clear either"
    finally:
        CORE._data = real


def test_the_substitution_does_not_write_into_the_shared_cache():
    """`_data()` is cached and shared. Rebanding a test in place would make the first style's
    band the corpus's band for every caller after it -- silently, and in whichever order the
    styles happened to be visited."""
    D = CORE._data()
    before = copy.deepcopy(D["faults"]["truss-flattened-pitch"]["secondary_tests"][0])
    for sid in ("cape-cod-colonial", "greek-revival-american", "tudor-revival"):
        CORE._test_for_style(D["faults"]["truss-flattened-pitch"]["secondary_tests"][0], sid, D)
    assert D["faults"]["truss-flattened-pitch"]["secondary_tests"][0] == before


def test_an_unknown_conversion_is_an_error_and_never_an_identity():
    """Comparing degrees against rise-in-12 raw would convict every house on earth. The
    conversion table is CLOSED; a name nobody has written is could-not-evaluate, which is the
    state the corpus already has a word for."""
    D = CORE._data()
    t = {"expression": "roof_slope_angle_deg",
         "band_from_style": {"expression": PITCH, "convert": "no-such-conversion"}}
    out = CORE._test_for_style(t, "cape-cod-colonial", D)
    assert out is not None and out.get("_band_error"), "a bad conversion must not read as unrun"
    ev = CORE._eval_test(out, {"roof_slope_angle_deg": 40.0})
    assert ev["status"] == "error" and "no-such-conversion" in ev["detail"]


def test_the_band_carries_its_provenance():
    """A substituted band that does not say where it came from is a number with no author --
    which is the whole complaint against the band it replaced."""
    D = CORE._data()
    out = CORE._test_for_style(ASK, "greek-revival-american", D)
    assert out["band_from"]["style"] == "greek-revival-american"
    assert out["band_from"]["rule"] == "greek-revival-american.c05"
    assert out["band_from"]["states"] == PITCH


# ------------------------------------------------------------------ the corpus


JUDGED_STYLES = 41
PITCH_STYLES = 15
WRONGLY_FAILED = [
    # style, its own band in degrees, the pitch the elevation derives for it
    ("greek-revival-american", (18.4, 26.6), 22.6),
    ("greek-revival-northern", (18.4, 26.6), 22.6),
    ("italian-renaissance-revival", (14.0, 22.6), 18.4),
    ("jeffersonian-classicism", (None, 18.4), 18.4),
    ("minimal-traditional", (18.4, 26.6), 22.6),
    ("neoclassical-revival", (18.4, 26.6), 22.6),
    ("new-england-federal", (26.6, 33.7), 30.3),
]


@pytest.fixture(scope="module")
def swept():
    """One plan, the style label swapped, which is what `check_division_guards.py` already does.

    The house is held CONSTANT on purpose: this measures the THRESHOLD, and a different house
    per style would measure the house.
    """
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    D = CORE._data()
    out = {}
    for sid in sorted(D["styles"]):
        m, _why = FT.reading(sid, plan, EL)
        if m is None:
            continue
        out[sid] = (m, CORE.check_measurements(m, style=sid, limit=10 ** 6))
    return out


def test_the_denominator_is_stated_and_the_other_hundred_and_twenty_three_are_not_clean(swept):
    """The census's own limit, asserted so it cannot quietly widen.

    123 of 164 styles supply no measurement at all -- outside `opening-proportion`'s and/or
    `facade-classical`'s calibration -- and are wholly UNJUDGED. A table that counted them as
    clean would be the fake-pass direction at corpus scale.
    """
    D = CORE._data()
    assert len(D["styles"]) == 164
    assert len(swept) == JUDGED_STYLES, len(swept)
    withpitch = [s for s, (m, _) in swept.items() if m.get("roof_slope_angle_deg") is not None]
    assert len(withpitch) == PITCH_STYLES, sorted(withpitch)


def test_the_measurement_and_the_band_come_from_the_same_record(swept):
    """The finding that makes the substitution obviously right rather than merely defensible.

    `build/elevation.py` derives `roof_slope_angle_deg` from the style's own migrated
    constraint, so a style supplies a pitch EXACTLY when it states a band -- measured, all 15
    with a measurement have one and all 26 without have none. The two halves already met in one
    place and the fault was judging one against another tradition's band.
    """
    D = CORE._data()
    for sid, (m, _r) in swept.items():
        has_m = m.get("roof_slope_angle_deg") is not None
        has_b = CORE.style_band(sid, PITCH, D) is not None
        assert has_m == has_b, (sid, has_m, has_b)


def test_no_style_is_failed_on_a_pitch_inside_its_own_band(swept):
    """The package's whole subject, over the corpus rather than over an example.

    Before: seven styles convicted by `truss-flattened-pitch` on a pitch their own node calls
    correct. The three the scope had already removed (`cape-cod-colonial`,
    `french-neoclassical`, `new-england-colonial`) were inside their own bands too, which is
    why a scope was the right direction and not the destination.
    """
    D = CORE._data()
    bad = []
    for sid, (m, r) in swept.items():
        v = m.get("roof_slope_angle_deg")
        band = CORE.style_band(sid, PITCH, D)
        if v is None or band is None:
            continue
        _d, lo, hi, _rule = band
        inside = ((lo is None or v >= deg(lo) - 1e-9) and (hi is None or v <= deg(hi) + 1e-9))
        if not inside:
            continue
        for row in r["faults_present"]:
            if row["fault"] != "truss-flattened-pitch":
                continue
            for ev in row.get("failing") or []:
                if ev.get("expression") == "roof_slope_angle_deg":
                    bad.append((sid, v, ev.get("required")))
    assert bad == [], bad
    assert {s for s, _b, _v in WRONGLY_FAILED} <= set(swept), (
        "the seven styles this guard exists for are not in the sweep; it would pass vacuously")


def test_the_five_bands_the_retired_note_named_reproduce_from_the_corpus(swept):
    """Why the note is a transcription of this data and not a second source.

    Four of the five reproduce to a tenth of a degree. The fifth is the finding and is NOT
    closed: `tudor-revival`'s constraint is `at-least 10:12`, open above -- its 39.8 lower
    reproduces and the note's 53.1 upper is in no record in this corpus, so under the
    substitution a Tudor is judged open above, which is what its own node says.
    """
    D = CORE._data()
    for sid, lo, hi in [("cape-cod-colonial", 36.9, 45.0),
                        ("greek-revival-american", 18.4, 26.6),
                        ("craftsman", 14.0, 26.6),
                        ("prairie-school", 14.0, 18.4)]:
        t = CORE._test_for_style(ASK, sid, D)
        assert t is not None, sid
        assert (t["threshold"], t["upper"]) == (lo, hi), (sid, t["threshold"], t["upper"])
    tud = CORE._test_for_style(ASK, "tudor-revival", D)
    assert tud["threshold"] == 39.8 and tud["upper"] is None, (
        "53.1 has been invented into the data")
    assert CORE.style_band("tudor-revival", PITCH, D)[0] == "at-least"


def test_the_georgian_band_was_one_style_node_transcribed():
    """33.7-39.8 is `georgian-colonial-american.c02` (8:12 to 10:12) converted, which is the
    last piece of the argument: the number was never the fault's own."""
    D = CORE._data()
    d, lo, hi, rule = CORE.style_band("georgian-colonial-american", PITCH, D)
    assert (d, lo, hi, rule) == ("between", 8, 10, "georgian-colonial-american.c02")
    assert (deg(lo), deg(hi)) == (33.7, 39.8)


def test_the_diagnostic_delegates_its_band_reader(monkeypatch):
    """`build/fault_thresholds.py` must not respell the reader the engine substitutes with.

    A diagnostic walking the constraint list itself could report a band the engine does not
    use, which is the defect this package is about committed by its own instrument.
    """
    calls = []
    real = CORE.style_band
    monkeypatch.setattr(CORE, "style_band", lambda *a: (calls.append(a), real(*a))[1])
    FT.style_band("cape-cod-colonial", PITCH, CORE._data())
    assert calls, "the diagnostic did not go through core.style_band"


def test_the_band_reader_agrees_with_the_three_pitch_spellings():
    """`structure._style_roof_pitch` and its copies in `roof.py` and `depth_floor.py` return a
    representative VALUE; this returns the BAND. It is not a fourth spelling of them and the
    guard is arithmetic over all 164 styles, which is what CLAUDE.md's standing instruction
    about that function asks for."""
    ST = MC.load("structure", os.path.join(ROOT, "build", "structure.py"))
    D = CORE._data()
    ids = [os.path.basename(p)[:-5] for p in sorted(glob.glob(os.path.join(ROOT, "styles", "*.json")))]
    assert len(ids) > 150, "the style corpus did not load; this would pass vacuously"
    seen = 0
    for sid in ids:
        theirs, _rid, _stmt = ST._style_roof_pitch(sid)
        band = CORE.style_band(sid, PITCH, D)
        if theirs is None:
            assert band is None, (sid, band)
            continue
        assert band is not None, sid
        d, lo, hi = band[0], band[1], band[2]
        mine = (lo + hi) / 2.0 if d == "between" else float(lo if lo is not None else hi)
        assert mine == theirs, (sid, mine, theirs)
        seen += 1
    assert seen == 48, seen
