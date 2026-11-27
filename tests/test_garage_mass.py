"""The garage as its own mass, the range against the rear wall, and the wing sized for its door set.

Four rulings of 26 to 27 November 2026, asked of Lucas and answered as separate acts, recorded in
`docs/open-questions/oq-the-double-piles-service-wing-cannot-tile-on-its-hyphens-face.md`:

1. the garage of a house with a service wing is its own mass beyond the wing, linked by the mudroom;
2. the wing is sized for its door set;
3. a house with dependencies on ONE flank lays that range against its rear wall
   (`groupings/dependency-and-hyphen.json`: "where there is one, it does not sit on the entrance
   elevation"); paired dependencies keep the axis;
4. the prover finds the wing's box, smallest whole-foot box first.

Every test here asserts its own premise, because the corpus has exactly one composed diagram that
reaches these branches (`centre-passage-double-pile` with a garage in the brief) and a fixture that
stops reaching them would otherwise go green for nothing.
"""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))
import modcache  # noqa: E402

G = modcache.load("geometry", str(ROOT / "build" / "geometry.py"))
CO = modcache.load("compose", str(ROOT / "build" / "compose.py"))

BRIEF = json.loads((ROOT / "briefs" / "family-georgian.json").read_text())
PARTI = "centre-passage-double-pile"


def _composed(brief=None):
    plan, _log, _p = CO.instantiate(PARTI, copy.deepcopy(brief or BRIEF))
    _levels, prep = G.prep_rooms(plan)
    fp = G.derive_footprint(plan, None, prep)
    return plan, prep, fp


def _snapped(fp, **more):
    """The footprint as the prover poses it: an integral depth (`geometry_cp._snap_fpd`)."""
    return dict(fp, H=float(round(fp["H"])), **more)


def _els(plan, prep, fp):
    return {e["id"]: e for e in G.blocks_for(plan, fp, prep, 0)}


# ---------------------------------------------------------------- ruling 1: the chain

def test_the_composed_double_pile_is_a_chain_of_five_elements_on_one_flank():
    plan, prep, fp = _composed()
    els = G.blocks_for(plan, fp, prep, 0)
    assert [e["id"] for e in els] == ["main", "service-hyphen", "service", "garage-hyphen", "garage"]
    by = {e["id"]: e for e in els}
    assert by["service-hyphen"]["attached_to"] == "main" and by["service"]["attached_to"] == "main"
    assert by["garage-hyphen"]["attached_to"] == "service" and by["garage"]["attached_to"] == "service"
    assert {e["side"] for e in els[1:]} == {"E"}, "one flank, and the garage takes its parent's side"
    # outward in order, no two elements sharing ground
    xs = [(e["x"], e["x"] + e["W"]) for e in els]
    assert all(a[1] <= b[0] + 1e-6 for a, b in zip(xs, xs[1:])), xs
    assert by["garage"]["rooms"] == ["garage"] and by["garage-hyphen"]["rooms"] == ["garage-mudroom"]
    assert "garage" not in by["service"]["rooms"] and "garage-mudroom" not in by["service"]["rooms"]


def test_a_one_room_element_is_its_rooms_own_rectangle_and_does_not_grow_with_the_house():
    plan, prep, fp = _composed()
    garage = next(r for r in prep[0] if r["id"] == "garage")
    assert (garage["width_ft"], garage["length_ft"]) == (22, 20), "the premise: a two-car garage"
    base = _els(plan, prep, _snapped(fp))
    assert (base["garage"]["W"], base["garage"]["H"]) == (22.0, 20.0)
    grown = _els(plan, prep, _snapped(fp, flank_grow_ft=4.0))
    assert (grown["garage"]["W"], grown["garage"]["H"]) == (22.0, 20.0)
    # the control: a wing of several rooms at its derived box does take the growth
    assert grown["service"]["H"] == base["service"]["H"] + 4.0


def test_a_threshold_room_may_be_a_link_and_a_working_room_may_not():
    assert "threshold" in G.LINK_CLASSES and "circulation" in G.LINK_CLASSES
    mud = {"id": "m", "type": "mudroom", "hyphen": True}
    kit = {"id": "k", "type": "kitchen", "hyphen": True}
    assert G._is_link(mud) is True
    assert G._is_link(kit) is False, "a kitchen tagged as a link is not one: it is a room of the wing"
    assert G._is_link({"id": "m2", "type": "mudroom"}) is False, "the tag is the statement, not the type"


# ---------------------------------------------------------------- ruling 3: against the rear wall

def test_the_laying_is_read_off_the_flank_and_the_stated_entrance_front():
    rows_e = [{"side": "E"}, {"side": "E"}]
    rear = {"flank_laying": "rear"}
    assert G.flank_laying({**rear, "context": {"entrance_faces": "S"}}, rows_e) == ("rear", "N")
    assert G.flank_laying({**rear, "context": {"entrance_faces": "N"}}, rows_e) == ("rear", "S")
    # a reading declined, not a default taken: no front, or a front on the flank's own axis
    assert G.flank_laying({**rear, "context": {}}, rows_e) == ("axis", None)
    assert G.flank_laying(rear, rows_e) == ("axis", None)
    assert G.flank_laying({**rear, "context": {"entrance_faces": "E"}}, rows_e) == ("axis", None)
    # paired dependencies keep the axis: the grouping's own sentence
    assert G.flank_laying({**rear, "context": {"entrance_faces": "S"}},
                          [{"side": "W"}, {"side": "E"}]) == ("axis", None)
    # AND THE RECORD STATES IT: a record that does not say `rear` is laid as every record was
    assert G.flank_laying({"context": {"entrance_faces": "S"}}, rows_e) == ("axis", None)
    assert G.flank_laying({"flank_laying": "axis", "context": {"entrance_faces": "S"}},
                          rows_e) == ("axis", None)


def test_the_composer_states_the_laying_and_the_shipped_record_does_not():
    """The statement is the record's (plan schema 0.14.0). The composer writes it on a house with a
    dependency and says so in its log; a one-rectangle house states nothing. The ONE shipped record
    with a dependency does not carry it, so its placement is exactly what it was: stating it there
    is a record edit with its own measurement, `oq/the-shipped-range-is-still-laid-on-the-axis`."""
    plan, log, _p = CO.instantiate(PARTI, copy.deepcopy(BRIEF))
    assert plan["flank_laying"] == "rear"
    said = [ln for ln in log if isinstance(ln, str) and ln.startswith("RULED") and "rear wall" in ln]
    assert len(said) == 1 and "does not sit on the entrance elevation" in said[0]
    one, _l, _q = CO.instantiate("side-hall-townhouse", copy.deepcopy(BRIEF))
    assert not any(r.get("block") for lv in one["levels"] for r in lv["rooms"]), "the premise"
    assert "flank_laying" not in one
    shipped = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())
    assert any(r.get("block") for r in shipped["levels"][0]["rooms"]), "the premise: it has a range"
    assert "flank_laying" not in shipped
    _levels, prep = G.prep_rooms(shipped)
    fp = _snapped(G.derive_footprint(shipped, None, prep))
    for e in G.blocks_for(shipped, fp, prep, 0)[1:]:
        assert e["laid"] == "axis" and e["y"] == (fp["H"] - e["H"]) / 2.0, e
    schema = json.loads((ROOT / "schema" / "plan.schema.json").read_text())
    assert schema["properties"]["flank_laying"]["enum"] == ["rear", "axis"]


def test_the_rule_quotes_a_sentence_the_grouping_really_states():
    g = json.loads((ROOT / "groupings" / "dependency-and-hyphen.json").read_text())
    want = ("Where dependencies are paired they are symmetrical about the main block's axis; where "
            "there is one, it does not sit on the entrance elevation.")
    hit = [r for r in g["internal_rules"] if r.get("statement") == want]
    assert hit and hit[0]["severity"] == "hard", "the basis of ruling 3 has moved or been reworded"
    assert "does not sit on the entrance elevation" in G.block_note({"laid": "rear"})


def test_the_one_range_stands_on_the_main_blocks_rear_wall_and_each_link_inside_both_masses():
    plan, prep, fp = _composed()
    assert (plan.get("context") or {}).get("entrance_faces") == "S", "the premise: a stated south front"
    fp = _snapped(fp)
    by = _els(plan, prep, fp)
    main_h = fp["H"]
    for k in ("service", "garage"):
        assert by[k]["laid"] == "rear"
        assert by[k]["y"] + by[k]["H"] == main_h, (k, by[k], "its rear wall is the main block's")
        assert by[k]["y"] > 0, "and so it stands back from the entrance front"
    for link, a, b in (("service-hyphen", "main", "service"), ("garage-hyphen", "service", "garage")):
        lo, hi = by[link]["y"], by[link]["y"] + by[link]["H"]
        for m in (a, b):
            assert by[m]["y"] <= lo and hi <= by[m]["y"] + by[m]["H"], (link, m, by[link], by[m])
        assert by[link]["H"] <= min(by[a]["H"], by[b]["H"]), "shallower than both it joins"
        small = by[a] if by[a]["H"] <= by[b]["H"] else by[b]
        assert lo - small["y"] == small["y"] + small["H"] - hi, (link, "centred on the smaller mass")
        assert float(lo).is_integer(), "on the whole-foot grid, so the prover rounds nothing off it"


def test_an_entrance_on_the_north_puts_the_range_on_the_south_wall():
    brief = copy.deepcopy(BRIEF)
    brief["context"]["entrance_faces"] = "N"
    plan, prep, fp = _composed(brief)
    by = _els(plan, prep, _snapped(fp))
    assert by["service"]["laid"] == "rear" and by["service"]["y"] == 0.0 and by["garage"]["y"] == 0.0


def test_with_no_stated_front_the_range_keeps_the_axis_exactly_as_it_was_laid_before():
    plan, prep, fp = _composed()
    # taken off the composed RECORD: the composer states a front for every house it makes
    plan["context"].pop("entrance_faces")
    assert G.entrance_walls(plan) == set(), "the premise: this record states no entrance front"
    fp = _snapped(fp)
    by = _els(plan, prep, fp)
    for k in ("service-hyphen", "service", "garage-hyphen", "garage"):
        assert by[k]["laid"] == "axis"
        assert by[k]["y"] == (fp["H"] - by[k]["H"]) / 2.0, (k, "exactly centred on the main block")
        assert G.block_note(by[k]) is None, "an element on the axis at its derived box says nothing new"


def test_paired_dependencies_keep_the_axis_whatever_the_front():
    plan, prep, fp = _composed()
    plan = copy.deepcopy(plan)
    # a second range on the other flank: a west dependency of two rooms, hand-built
    lib = next(r for r in plan["levels"][0]["rooms"] if r["id"] == "library")
    plan["levels"][0]["rooms"] += [
        {"id": "office", "type": "study", "block": "west", "width_ft": 12, "length_ft": 14,
         "exterior_walls": ["W", "N"], "doors": [{"to": "store", "width_ft": 2.5}]},
        {"id": "store", "type": "pantry", "block": "west", "width_ft": 6, "length_ft": 8,
         "exterior_walls": ["W", "S"], "doors": [{"to": "office", "width_ft": 2.5}]}]
    assert lib is not None
    _levels, prep = G.prep_rooms(plan)
    fp = _snapped(G.derive_footprint(plan, None, prep))
    els = G.blocks_for(plan, fp, prep, 0)
    assert {e["side"] for e in els[1:]} == {"E", "W"}, "the premise: a range on each flank"
    for e in els[1:]:
        assert e["laid"] == "axis" and e["y"] == (fp["H"] - e["H"]) / 2.0, e


def test_a_one_rectangle_house_is_one_element_and_its_record_states_no_blocks():
    plan = json.loads((ROOT / "plans" / "spec-builder-colonial.json").read_text())
    _levels, prep = G.prep_rooms(plan)
    fp = G.derive_footprint(plan, None, prep)
    els = G.blocks_for(plan, fp, prep, 0)
    assert [e["id"] for e in els] == ["main"] and "laid" not in els[0]
    assert G.blocks_record(plan, fp, prep) is None


# ---------------------------------------------------------------- rulings 2 and 4: the wing's box

def test_a_box_found_for_a_wing_replaces_the_derived_one_and_does_not_grow():
    plan, prep, fp = _composed()
    fp = _snapped(fp)
    base = _els(plan, prep, fp)
    sized = _els(plan, prep, dict(fp, flank_box={"service": (22, 21)}))
    assert (sized["service"]["W"], sized["service"]["H"]) == (22.0, 21.0)
    assert sized["service"]["sized"] == "door-set" and "sized" not in base["service"]
    # everything beyond it moves out by the same four feet, and nothing overlaps
    assert sized["garage"]["x"] - base["garage"]["x"] == 22.0 - base["service"]["W"]
    grown = _els(plan, prep, dict(fp, H=fp["H"] + 4, flank_grow_ft=4.0, flank_box={"service": (22, 21)}))
    assert (grown["service"]["W"], grown["service"]["H"]) == (22.0, 21.0), "a sized wing does not grow"
    assert grown["service"]["y"] + grown["service"]["H"] == fp["H"] + 4, "and stays on the rear wall"
    rec = {b["id"]: b for b in G.blocks_record(plan, dict(fp, flank_box={"service": (22, 21)}), prep)}
    assert "smallest the prover found" in rec["service"]["note"]
    assert "smallest the prover found" not in rec["garage"]["note"]


def test_the_candidate_boxes_are_whole_feet_smallest_first_and_inside_a_stated_window():
    GC = modcache.load("geometry_cp", str(ROOT / "build" / "geometry_cp.py"))
    c = GC.wing_box_candidates(18.0, 20.0, 9.0, 39.0)
    assert c[0] == (18, 20), "the derived box is asked first"
    assert [w * h for w, h in c] == sorted(w * h for w, h in c), "smallest first"
    assert {w for w, _h in c} == set(range(18, 28)), "from the derived width to one bay wider"
    assert {h for _w, h in c} == set(range(20, 25)), "from the derived depth to four feet deeper"
    assert len(c) == len(set(c)) == 50
    # the narrower on a tie: width is lot and depth is not
    ties = [b for b in c if b[0] * b[1] == 462]
    assert ties == sorted(ties) and ties[0][0] < ties[-1][0], ties
    # never deeper than the main block
    assert max(h for _w, h in GC.wing_box_candidates(18.0, 20.0, 9.0, 22.0)) == 22
    assert GC.wing_box_candidates(18.0, 20.0, 9.0, 12.0)[0] == (18, 20), "a shallow block keeps the derived box"


def test_the_sizing_note_says_which_of_three_things_happened():
    GC = modcache.load("geometry_cp", str(ROOT / "build" / "geometry_cp.py"))
    base = {"derived_ft": [18, 20], "boxes_in_window": 50, "tried": 19, "undecided": 0,
            "past_the_lot": 0, "seconds": 3.8}
    found = GC.wing_sizing_note({"service": dict(base, taken_ft=[21, 22])})
    assert "21 x 22 ft" in found and "18 x 20 ft" in found and "19 posed" in found
    assert "not shown smaller boxes fail" not in found
    hedged = GC.wing_sizing_note({"service": dict(base, taken_ft=[21, 22], undecided=2)})
    assert "2 undecided and so not shown smaller boxes fail" in hedged
    stands = GC.wing_sizing_note({"service": dict(base, taken_ft=[18, 20], tried=1)})
    assert "derived 18 x 20 ft box holds" in stands and "sized for its door set" not in stands
    none = GC.wing_sizing_note({"service": dict(base, taken_ft=None, tried=50, past_the_lot=3)})
    assert "no box of the 50" in none and "3 past the lot" in none and "stands" in none
    assert "kept from an earlier solve" in GC.wing_sizing_note(
        {"service": dict(base, taken_ft=[21, 22], cached=True)})


def _prover():
    pytest.importorskip("ortools", reason="COULD NOT EVALUATE: the prover (ortools) is not installed")
    return modcache.load("geometry_cp", str(ROOT / "build" / "geometry_cp.py"))


def test_the_prover_sizes_the_wing_and_releases_nothing_of_the_wings_own(monkeypatch):
    """The step poses the wing ALONE. What it may set aside is the main block's business; the wing's
    own tiling and its own rooms' bands are held in every box it poses, and `TILING` and `COVERAGE`
    are what they were. A step that found a box by releasing the wing's own facts would have found
    nothing."""
    GC = _prover()
    assert (GC.TILING, GC.COVERAGE) == (1.0, 0.97)
    plan, prep, fp = _composed()
    fpd = GC._snap_fpd(fp)
    els = G.blocks_for(plan, fpd, prep, 0)
    wi = next(i for i, e in enumerate(els) if e["id"] == "service")
    chain = {rid for e in els[1:] for rid in e["rooms"]}
    seen = []
    real = GC._build

    def spy(plan_, prep_, fpd_, ewalls_, downgraded=frozenset(), **kw):
        seen.append((dict(fpd_).get("flank_box"), frozenset(downgraded)))
        return real(plan_, prep_, fpd_, ewalls_, downgraded, **kw)

    monkeypatch.setattr(GC, "_build", spy)
    monkeypatch.setattr(GC, "_WING_BOXES", {})
    boxes, report = GC.size_wings(plan, prep, fpd, G.entrance_walls(plan), 60.0, workers=1)
    posed = [(fb, rel) for fb, rel in seen if fb]
    assert posed, "the premise: the step posed at least one box"
    for fb, rel in posed:
        assert ("tiling", 0, wi) not in rel, "the wing's own tiling is held"
        assert not [k for k in rel if k[0] == "shape" and k[1] == 0 and k[2] in chain], \
            "every band of the wing's rooms, its links' and the garage's is held"
        assert ("tiling", 0, 0) in rel, "the main block is set aside: this is the wing alone"
        assert all(k[0] != "size" and k[0] != "door" for k in rel)
    r = report["service"]
    assert r["derived_ft"] == [int(els[wi]["W"]), int(els[wi]["H"])]
    assert r["taken_ft"] is not None and r["undecided"] == 0, r
    assert r["taken_ft"] != r["derived_ft"], "the premise: the derived box does not hold this wing"
    assert boxes == {"service": tuple(r["taken_ft"])}
    tw, th = r["taken_ft"]
    assert tw * th >= r["derived_ft"][0] * r["derived_ft"][1]
    # smallest first: the box taken is the LAST one posed, and no larger one was asked before it
    order = [fb["service"] for fb, _rel in posed]
    assert order[-1] == (tw, th) and [w * h for w, h in order] == sorted(w * h for w, h in order)
    assert r["tried"] == len(order)
    # and a decided search is kept: the second call poses nothing
    n = len(seen)
    boxes2, report2 = GC.size_wings(plan, prep, fpd, G.entrance_walls(plan), 60.0, workers=1)
    assert boxes2 == boxes and report2["service"].get("cached") is True and len(seen) == n


def test_a_house_with_no_wing_of_several_rooms_is_not_sized_and_builds_no_model(monkeypatch):
    GC = _prover()
    plan = json.loads((ROOT / "plans" / "spec-builder-colonial.json").read_text())
    _levels, prep = G.prep_rooms(plan)
    fpd = GC._snap_fpd(G.derive_footprint(plan, None, prep))

    def boom(*a, **k):
        raise AssertionError("a one-rectangle house posed a wing box")

    monkeypatch.setattr(GC, "_build", boom)
    assert GC.size_wings(plan, prep, fpd, G.entrance_walls(plan), 10.0) == ({}, {})


def test_a_box_past_the_lot_is_not_posed(monkeypatch):
    GC = _prover()
    plan, prep, fp = _composed()
    fpd = GC._snap_fpd(fp)
    assert fpd.get("lot_usable") is not None and fpd.get("flank") is not None, "the premise: a lot"
    tight = dict(fpd, lot_usable=fpd["W"] + fpd["flank"])        # not one foot to spare
    monkeypatch.setattr(GC, "_WING_BOXES", {})
    boxes, report = GC.size_wings(plan, prep, tight, G.entrance_walls(plan), 60.0, workers=1)
    r = report["service"]
    assert boxes == {} and r["taken_ft"] is None, "no wider box may be taken on a lot with no room"
    assert r["past_the_lot"] > 0 and r["tried"] + r["past_the_lot"] == r["boxes_in_window"], r
    assert "stands" in GC.wing_sizing_note(report)


def test_the_whole_house_holds_every_fact_at_four_feet_deeper_with_the_wing_sized():
    """The measurement the rulings rest on, as a test: every type fact and every band HARD, the
    authored walls and the axis released as the prover's own hard steps release them, the line grid
    on. Bounded by deterministic time, so a loaded runner gets the same answer; where that bound is
    reached undecided the test reports COULD NOT EVALUATE and never a pass."""
    GC = _prover()
    from conftest import deterministic_solver
    from ortools.sat.python import cp_model
    plan, prep, fp = _composed()
    fpd0 = GC._snap_fpd(fp)
    ew = G.entrance_walls(plan)
    boxes, _report = GC.size_wings(plan, prep, fpd0, ew, 120.0, workers=1)
    assert boxes, "the premise: the wing was sized"
    fpd = dict(fpd0, H=fpd0["H"] + 4.0, flank_grow_ft=4.0, flank_box=boxes)
    _m, _r, q = GC._build(plan, prep, fpd, ew, frozenset(), objective=False)
    rel = frozenset(GC._dk(k, key) for _l, _t, k, key in q.lits if k in ("wall", "axis") and key)
    m, r, q = GC._build(plan, prep, fpd, ew, rel, objective=False)
    live = {k for _l, _t, k, key in q.lits if key}
    assert {"tiling", "stack", "bearing", "shape"} <= live, "the premise: the type's facts are posed"
    GC._line_grid(m, r, q, plan, prep, fpd)
    GC._harden(m, q)
    sv = deterministic_solver(400)
    st = sv.Solve(m)
    if st == cp_model.UNKNOWN:
        pytest.skip("COULD NOT EVALUATE: undecided inside the deterministic bound")
    assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), sv.StatusName(st)
