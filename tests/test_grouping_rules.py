"""The grouping rule held against the room record it constrains (WP-9.7).

`oq/a-grouping-rule-and-a-room-record-can-disagree`, ruled 2 Sep 2026 as shape (1): a checker on
the `check_addresses.py` model, reporting agrees / disagrees / cannot-compare and reconciling no
number. Six instances were known and the count had gone from four to six while the register entry
was being audited, which is the argument for counting rather than looking.

THE GUARD THAT MATTERS MOST HERE IS THE ONE ON THE WORD "AGREES". Measured before the checker was
written, of the six known instances a band comparison catches three, misses one whose figure lives
in prose, and reports one -- the sleeping porch -- as AGREEING, because the grouping's 8 and the
band's floor of 8 coincide exactly while the record's own prose says "NINE FEET OF DEPTH IF THE BED
RUNS ACROSS". So several tests below exist to prove the checker cannot quietly turn a
could-not-compare into a pass.
"""
import glob
import importlib.util
import json
import os
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CG = _mod("build/check_grouping_rules.py", "check_grouping_rules_t")


@pytest.fixture(scope="module")
def corpus():
    return CG.load()


# --------------------------------------------------------------- the annotation itself
def test_every_tested_grouping_rule_carries_measures():
    """26 of 26 when this shipped. A tested rule that arrives unannotated is invisible to the
    checker, and an invisible rule reads exactly like an agreeing one."""
    bare = []
    # `sorted(` on the same line as the read (tests/test_determinism.py checks per line)
    for f in sorted(glob.glob(str(ROOT / "groupings" / "*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        for i, ru in enumerate(d["internal_rules"]):
            if ru.get("test") and not ru.get("measures"):
                bare.append(f"{d['id']}[{i}]: {ru['test']}")
    assert not bare, ("a grouping rule carries a test and no `measures`, so nothing can hold it "
                      "against the record it constrains:\n  " + "\n  ".join(bare))


def test_a_measures_naming_a_room_names_a_room_that_exists_and_a_band_it_states():
    """A binding to a band the record does not state is a silent uncomparable, which is the
    state this whole checker exists to stop being invisible."""
    rooms = {json.loads(pathlib.Path(f).read_text(encoding="utf-8"))["id"]: f
             for f in sorted(glob.glob(str(ROOT / "rooms" / "*.json")))}
    bad = []
    for f in sorted(glob.glob(str(ROOT / "groupings" / "*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        for i, ru in enumerate(d["internal_rules"]):
            m = ru.get("measures") or {}
            if not m.get("room"):
                continue
            if m["room"] not in rooms:
                bad.append(f"{d['id']}[{i}] names room '{m['room']}', which has no record")
                continue
            dims = json.loads(pathlib.Path(rooms[m["room"]]).read_text(encoding="utf-8"))["dimensions"]
            if m.get("band") and m["band"] not in dims:
                bad.append(f"{d['id']}[{i}] names {m['room']}.{m['band']}, which that record "
                           f"does not state")
    assert not bad, "\n  ".join(bad)


# --------------------------------------------------------------- does it do its job
def test_the_registers_own_instances_are_actually_found(corpus):
    """A checker built for six named instances that finds none of them is a checker nobody has
    run. These three are instances 1, 2 and 3, and they are the deliverable rather than a debt."""
    groupings, rooms, _partis = corpus
    hits, _unc, _n = CG.rule_vs_band(groupings, rooms)
    found = {(w.split("[")[0], room, direction) for w, _s, _t, room, _b, _e, _rv, _bv, direction in hits}
    for want in (("centre-passage-core", "centre-passage", "rule-stricter"),
                 ("piazza-and-single-house-core", "piazza", "rule-stricter"),
                 ("secondary-bedroom-cluster", "bedroom", "rule-looser")):
        assert want in found, f"{want} is not in the band disagreements: {sorted(found)}"


def test_the_ridge_pair_is_found_across_co_carried_groupings(corpus):
    """Instance 6: one measure spelled twice, `wing_ridge_ft` against `dependency_ridge_ft`,
    latent only because 0.6-0.8 is a subset of <=0.85. The register said ONE pair; there are two,
    because `five-part-palladian` carries `georgian-service-core` alongside both hyphen
    groupings."""
    groupings, _rooms, partis = corpus
    hits, _u, _unc = CG.rule_vs_rule(groupings, partis)
    pairs = {(gx, gy) for gx, _ix, _tx, gy, _iy, _ty, _q, _w, _e, _u, _v in hits}
    assert ("dependency-and-hyphen", "georgian-service-core") in pairs, sorted(pairs)
    assert ("garage-and-hyphen", "georgian-service-core") in pairs, sorted(pairs)


def test_the_prose_meter_reads_a_figure_spelled_in_WORDS(corpus):
    """The meter's first version scanned digits only and MISSED the one case it exists for.
    `rooms/sleeping-porch.json` states its real floor as "NINE FEET OF DEPTH IF THE BED RUNS
    ACROSS" while its band floor is 8 and the grouping rule agrees with the band exactly -- so
    without this the checker's only word about the sleeping porch would be "agrees"."""
    groupings, rooms, _p = corpus
    got = CG.prose_meter(groupings, rooms)
    nine = [r for r in got if r[0] == "room" and r[1].startswith("sleeping-porch")
            and abs(r[2] - 9.0) < 1e-9]
    assert nine, ("the sleeping porch's NINE FEET is not in the prose meter; it is spelled in "
                  "words and a digits-only scan silently drops it")


def test_the_sleeping_porch_agrees_on_the_band_and_that_is_the_point(corpus):
    """Stated as a test so the next reader cannot mistake the silence for a clean bill. The band
    comparison genuinely agrees here -- 8 against a floor of 8 -- and the disagreement the
    register records is with the record's PROSE. Two meters, one instance."""
    groupings, rooms, _p = corpus
    hits, _unc, _n = CG.rule_vs_band(groupings, rooms)
    assert not [h for h in hits if h[0].startswith("sleeping-porch-cluster")], (
        "the sleeping porch now disagrees on its band; if a number moved, the prose meter's "
        "reading of this instance needs re-reading too")
    assert [r for r in CG.prose_meter(groupings, rooms)
            if r[0] == "room" and r[1].startswith("sleeping-porch")]


# --------------------------------------------------------------- unjudged is not passed
def test_a_rule_with_no_measures_is_UNCOMPARABLE_and_never_agreement():
    """The corpus's first rule, in the one place this checker could break it."""
    rule = {"statement": "x", "kind": "dimension", "severity": "hard",
            "test": "piazza_depth_ft at-least 10"}
    g = {"g": {"id": "g", "internal_rules": [rule]}}
    rooms = {"piazza": {"id": "piazza", "dimensions": {"width_ft": [8, 14]}}}
    hits, unc, compared = CG.rule_vs_band(g, rooms)
    assert hits == [] and compared == 0
    assert len(unc) == 1 and "no `measures`" in unc[0][2]


def test_units_are_never_converted_even_when_the_conversion_is_safe():
    """ft<->in is arithmetically safe and is still refused, so that a cross-unit pair is VISIBLE
    rather than silently absorbed. OQ 53 is what a quantity compared without its units does: it
    reported 60 DEGREES against 1.7321, which is tan 60 -- the same slope, called a
    contradiction."""
    rule = {"statement": "x", "kind": "dimension", "severity": "hard",
            "test": "piazza_depth_in at-least 120",
            "measures": {"quantity": "piazza_depth", "units": "in",
                         "room": "piazza", "band": "width_ft"}}
    g = {"g": {"id": "g", "internal_rules": [rule]}}
    rooms = {"piazza": {"id": "piazza", "dimensions": {"width_ft": [8, 14]}}}
    hits, unc, compared = CG.rule_vs_band(g, rooms)
    assert hits == [] and compared == 0, "120 in was silently compared against a band in feet"
    assert "UNIT SPLIT" in unc[0][2]


def test_only_the_bound_the_rule_states_is_compared():
    """`at-least 10` claims a floor and says NOTHING about a ceiling. Comparing whole intervals
    would report every one-sided rule as looser than its band and bury the real findings."""
    rule = {"statement": "x", "kind": "dimension", "severity": "hard",
            "test": "d_ft at-least 8",
            "measures": {"quantity": "d", "units": "ft", "room": "r", "band": "width_ft"}}
    g = {"g": {"id": "g", "internal_rules": [rule]}}
    rooms = {"r": {"id": "r", "dimensions": {"width_ft": [8, 99]}}}
    hits, _unc, compared = CG.rule_vs_band(g, rooms)
    assert compared == 1
    assert hits == [], ("the rule states no ceiling, so the band's 99 is not a disagreement "
                        "with it; got " + repr(hits))


def test_stated_bounds_does_not_invent_a_bound():
    assert CG.stated_bounds({"direction": "at-least", "threshold": 8.0}) == (8.0, None)
    assert CG.stated_bounds({"direction": "at-most", "threshold": 8.0}) == (None, 8.0)
    assert CG.stated_bounds({"direction": "between", "threshold": 8.0, "upper": 14.0}) == (8.0, 14.0)


# --------------------------------------------------------------- the ratchets
def test_the_ratchets_hold_on_the_live_corpus(corpus):
    groupings, rooms, partis = corpus
    band_hits, band_unc, compared = CG.rule_vs_band(groupings, rooms)
    rr_hits, rr_units, _rr_unc = CG.rule_vs_rule(groupings, partis)
    prose = CG.prose_meter(groupings, rooms)
    for key, got in (("rule_vs_band", len(band_hits)), ("rule_vs_rule", len(rr_hits)),
                     ("unit_splits", len(rr_units)), ("uncomparable", len(band_unc)),
                     ("prose_uncompared", len(prose))):
        assert got <= CG.RATCHET[key], f"{key}: ratchet {CG.RATCHET[key]} -> {got}"
    assert compared >= CG.RATCHET["compared"], (
        f"compared FELL to {compared} against a floor of {CG.RATCHET['compared']}")


def test_the_compared_FLOOR_catches_an_annotation_being_deleted(corpus):
    """The one way a may-only-fall ratchet lies: delete a `measures` and every ceiling above
    looks better because the instrument stopped looking. `check_addresses` guards the same hole
    by failing on a node that would not resolve."""
    groupings, rooms, _p = corpus
    stripped = json.loads(json.dumps(groupings))
    for ru in stripped["piazza-and-single-house-core"]["internal_rules"]:
        if ru.get("test", "").startswith("piazza_depth_ft"):
            ru.pop("measures")
            break
    else:
        raise AssertionError("the piazza depth rule is gone; this test needs rewriting")
    hits, _unc, compared = CG.rule_vs_band(stripped, rooms)
    assert compared < CG.RATCHET["compared"], (
        "deleting an annotation did not lower `compared`, so the floor cannot fire")
    assert len(hits) < CG.RATCHET["rule_vs_band"], (
        "and the disagreement ceiling would have looked BETTER for it, which is the lie")


# --------------------------------------------------------------- one parser, not two
def test_the_test_sentence_is_parsed_by_arrangement_and_not_a_second_spelling():
    """`arrangement.parse_rule_test`'s own comment reads "ONE PARSER, and it lives here", and
    `roof.py` already delegates. A second spelling of one rule is what this corpus has been
    bitten by three times -- the citation grammar, the parti path join, the riser divisor."""
    src = (ROOT / "build" / "check_grouping_rules.py").read_text()
    body = src.split('"""', 2)[2]        # past the module docstring, which quotes the grammar
    for token in ("at-least", "at-most", '"between"'):
        assert f're.search' not in body or token not in body.split("def figures_in")[0], (
            f"{token} is being matched in check_grouping_rules.py; the grammar has one parser "
            f"and it is arrangement.parse_rule_test")
    assert "parse_rule_test" in src


def test_the_checker_exits_nonzero_only_under_strict():
    """`--strict` is how check_all runs it. Without the flag it reports and returns 0, so an
    author can measure without failing their build."""
    src = (ROOT / "build" / "check_grouping_rules.py").read_text()
    assert "sys.exit(1 if failed else 0)" in src
    assert 'ap.add_argument("--strict"' in src
