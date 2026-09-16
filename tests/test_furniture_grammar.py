"""WP-13.6 -- the furniture is arranged to its own grammar, and every rule is DRIVEN.

WP-11.3 gave `furniture/grammar.json` ten rules of which four were executed: a placement
default, a wall run, a corner and a centre. Catalogue items state a POSITION in their own note
or name -- "at the foot", "between the windows", "flanking the chimney breast", "opposite the
bed", "facing down the hall", "sofas, pair, facing" -- and the packer read none of them; it
seated each against the first wall with a run. TEN items are reached by the nine positioned
rules and EIGHT of them are drawable, measured by running `rule_for` over all 278.

This file drives every rule the package added, and it drives them BY HAND rather than off the
shipped plans, for three separate reasons which are worth keeping apart:

  * two rules -- `fg-opposite-the-bed` and `fg-on-the-end-wall` -- are UNREACHED BY THE WHOLE
    CORPUS, because the one catalogue item stating each is a 4 in television and a 3 in mirror
    and `fg-too-thin-to-draw` refuses both before any placement rule is consulted. A guard
    over the shipped plans would be green with the code deleted (WP-8.11's rule);
  * `fg-flanking-the-chimney-breast` IS reached -- eighteen pieces over nine living rooms --
    and every one of them is REFUSED, because not one living room in the corpus draws a
    chimney breast. Its placing branch is what no plan reaches, so the breast is hand-built;
  * a shipped plan is a statement about one placement. `test_furniture_pass.py` owns the
    corpus rows; the rows here are about the RULE.

The one guard that does read the corpus is the last: it holds
`grammar.executed_but_unreached_in_the_corpus` to the sixteen plans IN BOTH DIRECTIONS, so
neither a rule that has quietly become reachable nor a rule that has quietly stopped being
reached can sit in that list unnoticed. It is the list's only reader that can fail.

Every figure here is `engine="heuristic"` where an engine is involved at all.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build"))
import modcache  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name):
    return modcache.load(name, os.path.join(ROOT, "build", f"{name}.py"))


F = _load("furniture")


_CENSUS = {}


def _rule_census():
    """`{rule id: [placed, refused]}` over the sixteen plans on the deterministic engine.

    ONE SPELLING, TWO READERS (WP-13.7). The both-directions guard below built this loop and
    the scope-A figure asserted a STRING in the rule's own note -- so when WP-13.5's container
    moved three items on `tidewater-georgian-careful`, the note went on saying 648 placed and
    the guard went on agreeing with it. A figure a test reads out of the prose it is guarding
    is not a measurement. Cached because two tests read it and a solve of all sixteen plans is
    about 2.5 s."""
    if not _CENSUS:
        import glob
        import pathlib as _pl
        G = _load("geometry")
        for pf in (sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))
                   + sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json")))):
            d = json.loads(_pl.Path(pf).read_text())
            if "levels" not in d:
                continue
            G._SOLVE_CACHE.clear()
            out = G.solve(json.loads(json.dumps(d)), engine="heuristic")
            for lv in out["levels"]:
                for r in lv["rooms"]:
                    for f in (r.get("furniture_layout") or []):
                        rid = f.get("rule")
                        if rid:
                            _CENSUS.setdefault(rid, [0, 0])[1 if f.get("unplaced") else 0] += 1
    return _CENSUS
RP = _load("render_plan")
GRAMMAR = json.load(open(os.path.join(ROOT, "furniture", "grammar.json")))


# ------------------------------------------------------------------ the driving harness

def arrange(items, rect=(0.0, 0.0, 24.0, 18.0), breasts=None, room=None, occupied=None):
    """One room's furniture, from a hand-built catalogue. No plan, no placement, no engine."""
    room = dict({"id": "r1", "doors": [], "windows": []}, **(room or {}))
    return F.arrange_room(room, {"furniture": list(items)}, rect, occupied or {}, [],
                          breasts=breasts)[0]


def by_rule(layout, rule):
    return [e for e in layout if e.get("rule") == rule]


def drawn(layout, rule):
    return [e for e in layout if e.get("rule") == rule and not e.get("unplaced")]


def refusal(layout, rule):
    r = [e for e in layout if e.get("rule") == rule and e.get("unplaced")]
    return r[0]["unplaced"]["reason"] if r else None


def rect_of(e):
    return (e["x_ft"], e["y_ft"], e["width_ft"], e["depth_ft"])


KING_BED = {"item": "king bed", "kind": "object", "footprint_in": [76, 80],
            "clearance_in": 30, "placement": "against-wall",
            "note": "Two people getting out of a bed on different schedules, so 30 in each side."}
NIGHTSTANDS = {"item": "nightstands, pair", "kind": "object", "footprint_in": [24, 18],
               "footprint_of": "piece", "count": 2, "clearance_in": 0,
               "placement": "against-wall"}
BENCH = {"item": "bench or blanket chest at the foot", "kind": "object",
         "footprint_in": [48, 18], "clearance_in": 0, "placement": "against-wall"}
BOOKCASES = {"item": "bookcases or built-ins flanking the chimney breast", "kind": "object",
             "footprint_in": [30, 12], "footprint_of": "piece", "count": 2,
             "clearance_in": 30, "placement": "built-in"}
SOFAS = {"item": "sofas, pair, facing", "kind": "object", "footprint_in": [84, 34],
         "footprint_of": "piece", "count": 2, "clearance_in": 30, "placement": "against-wall",
         "note": "they face each other across no more than 10 ft"}
TABLE8 = {"item": "dining table, seats 8", "kind": "object", "footprint_in": [40, 96],
          "clearance_in": 54, "placement": "freestanding"}
# THE CHAIR'S OWN COUNT IS FOUR AND THE TABLE SEATS EIGHT, ON PURPOSE. A fixture where the
# catalogue's count and the table's seats are the same number guards neither -- WP-11.15's
# rule, and a mutation counting the chairs from the catalogue stayed green over the first
# draft of this file, which stated 8 in both places.
CHAIRS = {"item": "dining chairs", "kind": "object", "footprint_in": [20, 22],
          "footprint_of": "piece", "count": 4, "clearance_in": 0, "placement": "freestanding"}
PIER_TABLE = {"item": "pier tables and glasses between the windows", "kind": "object",
              "footprint_in": [42, 18], "clearance_in": 0, "placement": "against-wall"}


def breast(wall="S", x=9.0, y=0.0, w=2.0, d=1.5, drawn_=True):
    return {"level": 0, "room": "r1", "wall": wall, "drawn": drawn_,
            "x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": d}


# ------------------------------------------------------------------ the readings

def test_a_rules_reach_is_read_from_the_grammar_and_spelled_nowhere_else():
    """`rule_for` matches on `applies_to`, which lives in the data beside the quoted basis.

    Guarded two ways, because neither half is enough on its own. BEHAVIOURALLY: retarget a
    rule's `applies_to` and the reach must follow -- a second spelling in the code would not.
    AND IN THE SOURCE, over `rule_for`'s own body only: every string constant in it is a KEY
    it reads out of a record, and not one is a value it compares against. A whole-file text
    guard was tried first and is wrong in both directions -- it convicts the word "nightstand"
    in a COMMENT explaining the aisle, and it would acquit a phrase spelled in another case
    or joined out of two pieces."""
    import ast
    import inspect
    body = ast.parse(inspect.getsource(F.rule_for))
    fn = body.body[0]
    doc = fn.body[0].value if (fn.body and isinstance(fn.body[0], ast.Expr)
                               and isinstance(fn.body[0].value, ast.Constant)) else None
    assert doc is not None, "rule_for has lost its docstring; prose stays beside the test"
    lits = {n.value for n in ast.walk(body)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and n is not doc}
    keys = {"item", "note", "placement_rules", "applies_to", "id",
            "item_contains", "item_startswith", "note_contains"}
    stray = sorted(lits - keys - {""})
    assert not stray, f"rule_for carries a string that is not a record key: {stray}"
    # and it really does reach: the phrase decides, not the item's placement field
    assert F.rule_for(BENCH) == "fg-at-the-foot"
    assert F.rule_for(NIGHTSTANDS) == "fg-beside-the-bed"
    assert F.rule_for(KING_BED) is None, "a bed is seated by its placement default"
    saved = F._GRAMMAR or F.grammar()
    try:
        g = json.loads(json.dumps(F.grammar()))
        for r in g["placement_rules"]:
            if r["id"] == "fg-beside-the-bed":
                r["applies_to"] = {"item_contains": "king bed"}
        F._GRAMMAR = g
        assert F.rule_for(KING_BED) == "fg-beside-the-bed", "the mutation did not land"
        assert F.rule_for(NIGHTSTANDS) is None, (
            "the reach followed the data, but the retired phrase still matches: a second "
            "spelling of the reach lives in build/furniture.py")
    finally:
        F._GRAMMAR = saved
    assert F.rule_for(NIGHTSTANDS) == "fg-beside-the-bed", "the restore did not land"


def test_a_table_states_its_seats_and_a_band_states_none():
    """The count of chairs is the RECORD's, read from the table's own name -- and a band is
    not a count, so `for six to eight` seats none rather than six."""
    assert F.seats_of("dining table, seats 8") == 8
    assert F.seats_of("dining table for eight") == 8
    assert F.seats_of("outdoor dining table for six to eight") is None
    assert F.seats_of("dining table, seats 6 to 10") is None
    assert F.seats_of("console table") is None


def test_a_count_is_drawn_only_where_the_footprint_is_one_piece():
    """fg-count. The twin beds' [100, 80] IS both beds and the aisle between them, so 'pair'
    there is one rectangle; the nightstands' [24, 18] is one nightstand, so it is two."""
    assert F.piece_count(NIGHTSTANDS) == 2
    assert F.piece_count({"item": "twin beds, pair", "footprint_of": "group", "count": 2}) == 1
    assert F.piece_count({"item": "twin beds, pair"}) == 1
    assert F.piece_count({"item": "six to eight side chairs", "footprint_of": "piece"}) == 1, (
        "a band carries no count and is drawn once")


def test_a_rules_figure_is_read_from_the_rule_and_absence_is_a_refusal_not_a_default():
    """`fg-pair-facing`'s 10 ft is in the sentence it was read from and on the rule beside it.
    A rule stating no such figure returns None, and `arrange_room` refuses rather than picking
    a number -- the branch below drives that."""
    assert F.rule_figure("fg-pair-facing", "max_gap_ft") == 10.0
    assert F.rule_figure("fg-pair-facing", "hearth_standoff_ft") == 1.0
    assert F.rule_figure("fg-at-the-foot", "max_gap_ft") is None
    assert F.rule_figure("fg-no-such-rule", "max_gap_ft") is None


def test_the_pair_is_refused_by_name_where_the_grammar_states_no_gap():
    """Driven, because the shipped grammar states both figures: strip one and the pair must be
    REFUSED naming the missing figure, never placed at some default gap."""
    saved = dict(F._GRAMMAR or F.grammar())
    try:
        g = json.loads(json.dumps(F.grammar()))
        for r in g["placement_rules"]:
            if r["id"] == "fg-pair-facing":
                r.pop("max_gap_ft")
        F._GRAMMAR = g
        assert F.rule_figure("fg-pair-facing", "max_gap_ft") is None, "the mutation did not land"
        lay = arrange([SOFAS])
        assert not drawn(lay, "fg-pair-facing")
        assert "states no max_gap_ft" in refusal(lay, "fg-pair-facing")
    finally:
        F._GRAMMAR = saved
    assert F.rule_figure("fg-pair-facing", "max_gap_ft") == 10.0, "the restore did not land"


# ------------------------------------------------------------------ the positioned rules

def test_a_chest_at_the_foot_stands_on_the_beds_foot_edge_and_turns_its_back_to_it():
    lay = arrange([KING_BED, BENCH], rect=(0.0, 0.0, 20.0, 16.0))
    bed = drawn(lay, "fg-against-wall")[0]
    e = drawn(lay, "fg-at-the-foot")[0]
    bx, by, bw, bd = rect_of(bed)
    x, y, w, d = rect_of(e)
    assert bed["wall"] == "S"
    assert abs(y - (by + bd)) < 1e-6, "it touches the bed's foot edge"
    # 1 mm of a foot: `to_record` rounds every written rectangle to three places (WP-11.8),
    # so an exactly-centred seat is written up to 0.0005 ft off centre on each edge
    assert abs((x + w / 2) - (bx + bw / 2)) < 1.1e-3, "centred on the bed"
    assert e.get("wall") is None and e["back"] == "S", (
        "it is on no wall; `back` is what orients its symbol")
    assert e["by"] == "king bed", "the record names the thing it was seated by"
    assert e["grade"] == "editorial-from-prose"


def test_a_room_with_no_bed_refuses_the_things_the_bed_would_have_seated():
    """Both bedside rules name the missing fact rather than falling back to a wall."""
    lay = arrange([BENCH, NIGHTSTANDS], rect=(0.0, 0.0, 20.0, 16.0))
    for rule in ("fg-at-the-foot", "fg-beside-the-bed"):
        assert not drawn(lay, rule), f"{rule} placed something with no bed to place it by"
        assert "no bed seated against a wall" in refusal(lay, rule)


def test_a_pair_of_nightstands_takes_both_sides_of_the_bed_and_stands_in_its_aisles():
    lay = arrange([KING_BED, NIGHTSTANDS], rect=(0.0, 0.0, 20.0, 16.0))
    bed = drawn(lay, "fg-against-wall")[0]
    ns = drawn(lay, "fg-beside-the-bed")
    assert len(ns) == 2 and {e["piece"] for e in ns} == {1, 2} and {e["of"] for e in ns} == {2}
    bx, _by, bw, _bd = rect_of(bed)
    left = [e for e in ns if e["x_ft"] < bx]
    right = [e for e in ns if e["x_ft"] >= bx + bw]
    assert len(left) == 1 and len(right) == 1, "one either side"
    assert abs(right[0]["x_ft"] - (bx + bw)) < 1e-6, "touching the bed's side"
    assert abs((left[0]["x_ft"] + left[0]["width_ft"]) - bx) < 1e-6
    # and the aisle the bed's own clearance reserved is exactly where they stand: the record
    # puts them there ("within the bedside aisle"), so the aisle does not refuse them
    aisles = F.aisle_rects(bed, 30.0 / 12.0)
    assert len(aisles) == 2
    for e in ns:
        assert any(F._overlaps(rect_of(e), a) for a in aisles), (
            "a nightstand stands inside the aisle its own record names")


def test_the_bed_keeps_its_aisle_along_the_wall_and_not_in_front_of_itself():
    """fg-bed-aisle. The first draft reserved it AT THE FOOT, which packed the chest of drawers
    flush against the bed's side in every bedroom and refused every nightstand. Two records
    state the direction: 'each side' and 'plus 24 at each outer side'."""
    lay = arrange([KING_BED], rect=(0.0, 0.0, 20.0, 16.0))
    bed = drawn(lay, "fg-against-wall")[0]
    assert bed["wall"] == "S"
    assert abs(bed["x_ft"] - 30.0 / 12.0) < 1e-6, (
        "the bed starts one aisle in from the wall's own low end, not at it")
    a = F.aisle_rects(bed, 30.0 / 12.0)
    assert [round(r[0], 3) for r in a] == [0.0, round(bed["x_ft"] + bed["width_ft"], 3)]
    assert all(abs(r[3] - bed["depth_ft"]) < 1e-6 for r in a), (
        "the aisle is the bed's own depth: it is beside the bed, not in front of it")
    # a wall too short to hold the bed AND two aisles takes neither
    narrow = arrange([KING_BED], rect=(0.0, 0.0, 10.0, 7.0))
    assert not drawn(narrow, "fg-against-wall")
    assert "aisle either side" in refusal(narrow, "fg-against-wall")


def test_a_pier_table_stands_between_two_placed_sashes_and_is_refused_where_there_is_no_pier():
    """The pier is read from the record's own PLACED sashes, never from a declared count."""
    two = {"id": "r1", "doors": [], "windows": [
        {"wall": "S", "width_ft": 3.0, "positions_ft": [4.0, 16.0]}]}
    lay = arrange([PIER_TABLE], room=two)
    e = drawn(lay, "fg-between-the-windows")[0]
    assert e["wall"] == "S"
    assert abs((e["x_ft"] + e["width_ft"] / 2) - 10.0) < 1e-6, "centred on the pier 5.5 to 14.5"
    one = {"id": "r1", "doors": [], "windows": [
        {"wall": "S", "width_ft": 3.0, "positions_ft": [4.0]}]}
    lay2 = arrange([PIER_TABLE], room=one)
    assert not drawn(lay2, "fg-between-the-windows")
    assert "pier between two placed sashes" in refusal(lay2, "fg-between-the-windows")
    # an UNPLACED sash is not a sash: it makes no pier
    unpl = {"id": "r1", "doors": [], "windows": [
        {"wall": "S", "width_ft": 3.0, "positions_ft": [4.0]},
        {"wall": "S", "width_ft": 3.0, "position_ft": 16.0, "unplaced": {"reason": "x"}}]}
    assert not drawn(arrange([PIER_TABLE], room=unpl), "fg-between-the-windows")


def test_the_bookcases_flank_a_breast_the_hearth_pass_drew_and_refuse_where_it_drew_none():
    """THE PLACING BRANCH IS UNREACHABLE FROM THE CORPUS and is driven here. Nine living rooms
    over nine of the sixteen plans carry this item and not one draws a breast, so all eighteen
    pieces are refused; the last guard in this file holds that measurement."""
    lay = arrange([BOOKCASES], breasts=[breast(wall="S", x=9.0, w=2.0)])
    got = drawn(lay, "fg-flanking-the-chimney-breast")
    assert len(got) == 2, [e.get("unplaced") for e in by_rule(lay, "fg-flanking-the-chimney-breast")]
    xs = sorted(round(e["x_ft"], 3) for e in got)
    assert xs == [6.5, 11.0], "one either side of a breast running 9.0 to 11.0"
    assert all(e["wall"] == "S" and e["by"] == "the chimney breast" for e in got)
    # a breast the pass did not DRAW is not a thing to flank
    assert not drawn(arrange([BOOKCASES], breasts=[breast(drawn_=False)]),
                     "fg-flanking-the-chimney-breast")
    assert "draws no chimney breast to flank" in refusal(arrange([BOOKCASES]),
                                                         "fg-flanking-the-chimney-breast")


def test_the_television_takes_the_wall_opposite_the_bed_and_no_other():
    """UNREACHED BY THE CORPUS: the one item stating it is a 4 in television that
    `fg-too-thin-to-draw` refuses first. Driven at a drawable depth."""
    tv = {"item": "media cabinet", "kind": "object", "footprint_in": [60, 20],
          "clearance_in": 0, "placement": "against-wall",
          "note": "the only wall that works is the one opposite the bed"}
    lay = arrange([KING_BED, tv], rect=(0.0, 0.0, 20.0, 16.0))
    bed = drawn(lay, "fg-against-wall")[0]
    e = drawn(lay, "fg-opposite-the-bed")[0]
    assert bed["wall"] == "S" and e["wall"] == "N", "the wall opposite the bed's, and no other"
    # with the bed's own wall the only one clear, the rule REFUSES rather than taking it
    tight = arrange([KING_BED, dict(tv, footprint_in=[60, 200])], rect=(0.0, 0.0, 20.0, 16.0))
    assert not drawn(tight, "fg-opposite-the-bed")
    assert "the wall opposite the bed (N)" in refusal(tight, "fg-opposite-the-bed")


def test_the_mirror_takes_an_end_wall_and_the_end_walls_are_the_rooms_short_ones():
    """UNREACHED BY THE CORPUS: a 3 in mirror, refused by `fg-too-thin-to-draw`."""
    mirror = {"item": "cheval glass", "kind": "object", "footprint_in": [24, 12],
              "clearance_in": 0, "placement": "against-wall",
              "note": "Put the mirror on the END wall looking down the length of the room"}
    assert F._short_walls((0.0, 0.0, 24.0, 18.0)) == ("W", "E")
    assert F._short_walls((0.0, 0.0, 18.0, 24.0)) == ("S", "N")
    e = drawn(arrange([mirror]), "fg-on-the-end-wall")[0]
    assert e["wall"] in ("W", "E")
    e2 = drawn(arrange([mirror], rect=(0.0, 0.0, 18.0, 24.0)), "fg-on-the-end-wall")[0]
    assert e2["wall"] in ("S", "N"), "the end wall follows the room's shape, not the compass"


def test_the_high_table_takes_an_end_wall_of_the_hall_and_says_the_choice_is_not_a_reading():
    high = {"item": "high table on the dais", "kind": "object", "footprint_in": [96, 30],
            "clearance_in": 30, "placement": "freestanding"}
    e = drawn(arrange([high]), "fg-facing-down-the-hall")[0]
    assert e["wall"] in F._short_walls((0.0, 0.0, 24.0, 18.0))
    rule = next(r for r in GRAMMAR["placement_rules"] if r["id"] == "fg-facing-down-the-hall")
    assert "not a reading" in rule["rule"], (
        "which end is the dais is a fact the corpus does not carry, and the rule must say so")
    assert "fg-hall-high-table-one-side" in GRAMMAR["stated_not_executed"], (
        "the DAIS half stays unexecuted; only the facing half is done")


def test_two_sofas_face_each_other_astride_the_hearths_axis_where_a_breast_is_drawn():
    br = breast(wall="W", x=0.0, y=7.0, w=1.5, d=4.0)
    got = drawn(arrange([SOFAS], breasts=[br]), "fg-pair-facing")
    assert len(got) == 2
    axis = br["y_ft"] + br["depth_ft"] / 2.0
    lo, hi = sorted(got, key=lambda e: e["y_ft"])
    assert abs(((lo["y_ft"] + lo["depth_ft"]) + hi["y_ft"]) / 2.0 - axis) < 1e-6, (
        "the gap straddles the hearth's axis")
    gap = hi["y_ft"] - (lo["y_ft"] + lo["depth_ft"])
    assert gap <= F.rule_figure("fg-pair-facing", "max_gap_ft") + 1e-6
    assert all(e["by"] == "the hearth's axis" for e in got)
    assert {e["back"] for e in got} == {"N", "S"}, "each turns its back to the other"
    stand = br["x_ft"] + br["width_ft"] + F.rule_figure("fg-pair-facing", "hearth_standoff_ft")
    assert all(abs(e["x_ft"] - stand) < 1e-6 for e in got), "they run out from the breast's face"


def test_the_pair_falls_back_to_the_rooms_centre_line_and_the_entry_says_which():
    got = drawn(arrange([SOFAS]), "fg-pair-facing")
    assert len(got) == 2 and all(e["by"] == "the room's centre line" for e in got)
    assert all(e.get("wall") is None for e in got), "a facing pair is on no wall"
    shallow = arrange([SOFAS], rect=(0.0, 0.0, 24.0, 6.0))
    assert not drawn(shallow, "fg-pair-facing")
    assert "no clear floor for two sofas facing each other" in refusal(shallow, "fg-pair-facing")


def test_the_chairs_a_table_seats_are_pulled_up_to_it_ends_first():
    lay = arrange([TABLE8, CHAIRS])
    table = drawn(lay, "fg-freestanding")[0]
    got = drawn(lay, "fg-chairs-around-the-table")
    assert len(got) == 8 and [e["piece"] for e in got] == list(range(1, 9))
    assert {e["of"] for e in got} == {8}, "the TABLE decides the count, not the chair's own"
    assert F.piece_count(CHAIRS) == 4, (
        "the fixture must straddle the branch: the catalogue says four and the table eight")
    tx, ty, tw, td = rect_of(table)
    for e in got:
        x, y, w, d = rect_of(e)
        touch = (abs(x + w - tx) < 1e-6 or abs(x - (tx + tw)) < 1e-6
                 or abs(y + d - ty) < 1e-6 or abs(y - (ty + td)) < 1e-6)
        assert touch, f"a chair stands off the table's edge: {rect_of(e)} against {rect_of(table)}"
        assert e["by"] == "dining table, seats 8" and e.get("wall") is None
    backs = [e["back"] for e in got]
    assert backs[:2] == ["W", "E"], "one at each end first"
    assert sorted(backs[2:]) == ["N", "N", "N", "S", "S", "S"], "the rest split along the sides"


def test_a_room_with_no_seating_table_refuses_the_chairs_and_states_no_count():
    lay = arrange([CHAIRS])
    assert not drawn(lay, "fg-chairs-around-the-table")
    why = refusal(lay, "fg-chairs-around-the-table")
    assert "no table stating its seats is placed" in why
    assert "no count for them either" in why, (
        "the number of chairs is the table's; with no table it is unjudged and must say so")
    assert not re.search(r"\b\d+ chair", why), "and it must not publish a number it did not read"
    # a table naming a BAND states no count, so it seats no chairs by this rule
    band = arrange([dict(TABLE8, item="outdoor dining table for six to eight"), CHAIRS])
    assert not drawn(band, "fg-chairs-around-the-table")


def test_a_chair_with_nowhere_to_stand_is_counted_and_never_moved_somewhere_plausible():
    """One aggregated refusal row, carrying `piece`/`of`, so the key can say `x5 OF 8`."""
    lay = arrange([TABLE8, CHAIRS], rect=(0.0, 0.0, 11.0, 11.0))
    got = drawn(lay, "fg-chairs-around-the-table")
    ref = [e for e in by_rule(lay, "fg-chairs-around-the-table") if e.get("unplaced")]
    assert got and ref, (len(got), len(ref))
    assert len(ref) == 1 and ref[0]["of"] == 8 and ref[0]["piece"] == len(got) + 1
    assert f"{8 - len(got)} of the 8 chairs" in ref[0]["unplaced"]["reason"]


# ------------------------------------------------------------------ the counted item

def test_a_counted_piece_is_drawn_that_many_times_and_a_group_once():
    two = drawn(arrange([KING_BED, NIGHTSTANDS], rect=(0.0, 0.0, 20.0, 16.0)), "fg-beside-the-bed")
    assert len(two) == 2
    group = {"item": "twin beds, pair", "kind": "object", "footprint_in": [100, 80],
             "footprint_of": "group", "clearance_in": 24, "placement": "against-wall"}
    one = drawn(arrange([group], rect=(0.0, 0.0, 20.0, 16.0)), "fg-against-wall")
    assert len(one) == 1 and one[0].get("piece") is None and one[0].get("of") is None


def test_the_wall_packer_carries_piece_and_of_and_no_shipped_plan_reaches_that_line():
    """DRIVEN, because the corpus cannot reach it: every counted catalogue item resolves to
    `fg-freestanding` or to a positioned rule, so `pack_against_walls` is handed no counted
    spec by any of the sixteen plans and the line below is byte-identical on all of them.
    Without it the key draws one numeral per chair instead of one numeral on a set."""
    chairs = {"item": "two hall chairs", "kind": "object", "footprint_in": [20, 20],
              "footprint_of": "piece", "count": 2, "clearance_in": 18,
              "placement": "against-wall"}
    got = drawn(arrange([chairs], rect=(0.0, 0.0, 12.0, 10.0)), "fg-against-wall")
    assert len(got) == 2
    assert [e["piece"] for e in got] == [1, 2] and {e["of"] for e in got} == {2}
    # and a REFUSED piece keeps them, so the key can say how many of the stated number stand
    tight = by_rule(arrange([dict(chairs, footprint_in=[200, 200])], rect=(0.0, 0.0, 12.0, 10.0)),
                    "fg-against-wall")
    assert tight and all(e["of"] == 2 and e.get("unplaced") for e in tight)


# ------------------------------------------------------------- what the catalogue may say

def test_a_count_is_admitted_only_beside_a_piece_footprint_and_never_on_a_band():
    """`build/check_rooms.py`'s two new rules, DRIVEN: NO shipped record breaks either, so a
    guard over `rooms/` would be green with both deleted -- which is the state a reader mistakes
    for a verdict. The rules are that a `count` on a GROUP footprint would be a count of groups,
    which no record means, and that a name stating a band ('six to eight side chairs') may not
    carry one, because a band is not a count."""
    CR = _load("check_rooms")
    sound = json.load(open(os.path.join(ROOT, "rooms", "primary-bedroom.json")))
    u = CR.build_universe()

    def errs(room):
        rep = CR.Report()
        CR.check_room(rep, os.path.join(ROOT, "rooms", "primary-bedroom.json"), room, u, {room["id"]})
        return [m for _w, m in rep.errors]

    assert not [m for m in errs(json.loads(json.dumps(sound))) if "count" in m], (
        "the control record already fails one of these rules; the fixture proves nothing")
    on_a_group = json.loads(json.dumps(sound))
    on_a_group["furniture"][0].update({"footprint_of": "group", "count": 2})
    assert any("count of groups" in m for m in errs(on_a_group)), errs(on_a_group)
    on_a_band = json.loads(json.dumps(sound))
    on_a_band["furniture"][0].update({"item": "six to eight side chairs",
                                      "footprint_of": "piece", "count": 8})
    assert any("a band is not a count" in m for m in errs(on_a_band)), errs(on_a_band)


# ------------------------------------------------------------------ the clearance strip

def test_a_clearance_strip_moves_a_positioned_item_and_lets_a_freestanding_one_through():
    """fg-clear-in-front's SCOPE is the discriminator, and both halves are asserted: a test
    that only showed the refusal would pass with the freestanding exemption deleted, and a
    test that only showed the exemption would pass with the strip deleted.

    The room is 12 x 6 ft: a sideboard packs onto the S wall at x 0-5.5, and its 36 in strip
    is (0, 1.667, 5.5, 3.0) -- the floor its drawers open into."""
    sideboard = {"item": "sideboard", "kind": "object", "footprint_in": [66, 20],
                 "clearance_in": 36, "placement": "against-wall"}
    mirror = {"item": "cheval glass", "kind": "object", "footprint_in": [24, 12],
              "clearance_in": 0, "placement": "against-wall",
              "note": "Put the mirror on the END wall looking down the length of the room"}
    room = (0.0, 0.0, 12.0, 6.0)
    sb = drawn(arrange([sideboard], rect=room), "fg-against-wall")[0]
    strip = F._front_strip(sb, 3.0)
    assert strip is not None and abs(strip[1] - (sb["y_ft"] + sb["depth_ft"])) < 1e-6, (
        "the strip is off the face AWAY from the wall")
    # WITHOUT the clearance the mirror takes the W end wall, standing in that floor
    free = drawn(arrange([dict(sideboard, clearance_in=0), mirror], rect=room),
                 "fg-on-the-end-wall")[0]
    assert free["wall"] == "W" and F._overlaps(rect_of(free), strip), (
        "the control does not exercise the strip: the mirror is not in it")
    # WITH it the positioned rule is pushed off that wall onto the other end
    held = drawn(arrange([sideboard, mirror], rect=room), "fg-on-the-end-wall")[0]
    assert held["wall"] == "E" and not F._overlaps(rect_of(held), strip), (
        "a strip must refuse a positioned item the floor it reserved")
    # ... and a freestanding item in the same floor is let through, because the record puts it
    # there: the coffee table stands "16 to 18 in from the sofa", inside the sofa's own 30
    coffee = {"item": "coffee table", "kind": "object", "footprint_in": [40, 20],
              "clearance_in": 0, "placement": "freestanding"}
    got = drawn(arrange([sideboard, coffee], rect=room), "fg-freestanding")
    assert got, "a strip must not refuse a freestanding item"
    assert F._overlaps(rect_of(got[0]), strip), (
        "the fixture does not exercise the exemption: the table is not in the strip")


def test_the_rule_says_what_the_code_does_about_the_wall_pack():
    """WP-13.6 tried two wider readings and refused both. The rule's text may not go on
    claiming what was refused, and the cost of each refusal has to be on the rule WITH ITS
    SCOPE NAMED -- the package's first draft published a pair of figures whose scope was not
    stated, which is a number the next reader applies to the wrong one."""
    rule = next(r for r in GRAMMAR["placement_rules"] if r["id"] == "fg-clear-in-front")
    assert "no later POSITIONED item" in rule["rule"]
    assert "does NOT reach the wall pack" in rule["rule"]
    for want in ("79 drawn items lost over 39 rooms", "88 drawn items lost over 44 rooms"):
        assert want in rule["note"], f"the refused readings' cost is published: {want}"
    # SCOPE A IS DERIVED FROM THE CORPUS, NOT READ OUT OF THE NOTE (WP-13.7). This asserted
    # `"648 placed" in rule["note"]` -- the note agreeing with itself -- and WP-13.5's container
    # then moved three items on `tidewater-georgian-careful` and took A to 645/155 while the
    # note and this guard went on saying 648. A published measurement whose only reader is the
    # prose it is published in is the shape this corpus names first.
    census = _rule_census()
    placed = sum(v[0] for v in census.values())
    refused = sum(v[1] for v in census.values())
    assert f"{placed} placed, {refused} refused on the merged tree" in rule["note"], (
        f"scope A measures {placed} placed / {refused} refused on this tree and the rule's note "
        f"does not say so. Re-derive (it is one solve of the sixteen plans on the deterministic "
        f"engine) and correct furniture/grammar.json, docs/reports/"
        f"wp-13.6-furniture-to-its-own-grammar.md and CLAUDE.md together.")
    # B and C cannot be re-measured without rebuilding the two readings they describe, so the
    # note may keep their figures only while it names the tree they were taken on.
    assert "560 placed" in rule["note"] and "c5d9bbd" in rule["note"], (
        "the refused readings keep their figures and must name the tree they were measured on")


# ------------------------------------------------------------------ the record and the plate

def test_a_mark_is_oriented_by_back_where_an_item_stands_on_no_wall():
    """`marks_for` reads `back or wall`. A chair pulled up to a table, a sofa of a facing pair
    and a bench at the foot of a bed are on no wall and still have a front and a back."""
    base = {"item": "sofa", "symbol": "sofa", "x_ft": 2.0, "y_ft": 3.0,
            "width_ft": 6.0, "depth_ft": 2.5}
    n = F.marks_for(dict(base, back="N"))
    s = F.marks_for(dict(base, back="S"))
    assert n and s and n != s, "the two orientations must draw differently"
    assert F.marks_for(dict(base, wall="N")) == n, "`wall` and `back` orient the same way"
    assert F.marks_for(base) != n, "and an entry stating neither is not oriented by accident"


def test_the_pieces_of_a_counted_item_share_one_numeral_in_both_spellings():
    """`render_plan.py::_key_groups` and `furnitureKey.js::keyEntries` are the two spellings;
    nothing imports across the language boundary, so the JS is read as text."""
    room = {"furniture_layout": [
        {"item": "dining chairs", "piece": 1, "of": 8, "marks": [{"kind": "rect"}],
         "x_ft": 0, "y_ft": 0, "width_ft": 1, "depth_ft": 1},
        {"item": "dining chairs", "piece": 2, "of": 8, "marks": [{"kind": "rect"}],
         "x_ft": 2, "y_ft": 0, "width_ft": 1, "depth_ft": 1},
        {"item": "sideboard", "marks": [{"kind": "rect"}],
         "x_ft": 4, "y_ft": 0, "width_ft": 1, "depth_ft": 1}]}
    groups = RP._key_groups(room)
    assert [(n, len(fs)) for n, fs, _k in groups] == [(1, 2), (2, 1)], (
        "two chairs are one key line and one numeral; the sideboard is the next")
    assert RP.key_pieces(room)[1] == room["furniture_layout"][:2]
    lines = RP.key_lines(RP.key_entries(room), RP.key_pieces(room))
    assert lines == ["1 DINING CHAIRS x2 OF 8", "2 SIDEBOARD"], lines
    # a set drawn whole says x8 and no shortfall
    whole = {"furniture_layout": [dict(f, of=2) for f in room["furniture_layout"][:2]]}
    assert RP.key_lines(RP.key_entries(whole), RP.key_pieces(whole)) == ["1 DINING CHAIRS x2"]
    # THE FIXTURE IS SPELLED IN BOTH FILES AND EACH SUITE DRIVES ITS OWN PORT. Nothing imports
    # across the language boundary, so what is held here is that the JS suite really is about
    # this fixture and expects these lines; `node --test workbench/app` is what fails when
    # `furnitureKey.js` stops grouping. A grep of the JS SOURCE was the first draft and is the
    # weaker guard -- it goes quietly blind on any rewording of the code it reads.
    jst = open(os.path.join(ROOT, "workbench", "app", "src", "furnitureKey.test.mjs")).read()
    assert "item: 'dining chairs', piece: 1, of: 8" in jst and \
           "item: 'dining chairs', piece: 2, of: 8" in jst, (
        "the browser suite must drive the same counted fixture")
    for want in lines:
        assert f"'{want}'" in jst, f"the browser suite does not expect {want!r}"
    assert "'1 DINING CHAIRS x2', '2 SIDEBOARD'" in jst, (
        "and must expect the no-shortfall form from the same fixture")


def test_the_positioned_rules_reach_ten_catalogue_items_and_eight_are_drawable():
    """THE CENSUS THREE FILES QUOTE, DERIVED HERE SO IT CANNOT ROT IN THE PROSE. `check_counts.py`
    polices numbers derived from the CORPUS in Markdown, and this one is not on its list -- which
    is WP-8.14's finding exactly: of the figures a layer publishes, the one nobody derives is the
    one that goes stale. The package's opening survey counted every item whose note MENTIONS a
    place and reported a larger, looser number; what the grammar executes is this."""
    import glob
    reached, drawable_n = [], 0
    total = 0
    for rf in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))):
        for it in (json.load(open(rf)).get("furniture") or []):
            total += 1
            if F.rule_for(it):
                reached.append((os.path.basename(rf), it["item"]))
                drawable_n += F.drawable(it) is None
    assert total == 278, f"{total} catalogue items, not 278: re-derive this whole census"
    assert (len(reached), drawable_n) == (10, 8), (
        f"the positioned rules now reach {len(reached)} catalogue items of which {drawable_n} are "
        f"drawable, against 10 and 8: {reached}. Re-derive and correct the figure in "
        f"docs/reports/wp-13.6-furniture-to-its-own-grammar.md, in CLAUDE.md and in this file's "
        f"own docstring -- all three quote it and none of them can compute it.")


def test_every_level_of_every_plan_has_an_index_equal_to_its_position():
    """THE PREMISE BEHIND ONE ARGUMENT CARRYING TWO MEANINGS. `openings.furniture_pass` takes
    one `level_index`: the breasts are matched on it (`threshold.hearth_pass` writes the
    record's own `index`) and the stair well is matched on it too (`stair_pass` writes a
    literal `level: 0`, meaning the ground level). The two coincide only while every level's
    `index` IS its position, and `schema/plan.schema.json` documents `index: -1` for a cellar,
    which no record uses. When one does, this fails and sends the reader to the comment at
    `openings.place`'s furniture call rather than letting a stair well quietly stop blocking."""
    import glob
    import pathlib
    n = 0
    for pf in (sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))
               + sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json")))):
        d = json.loads(pathlib.Path(pf).read_text())
        if "levels" not in d:
            continue
        n += 1
        idx = [lv.get("index") for lv in d["levels"]]
        assert idx == list(range(len(idx))), (os.path.basename(pf), idx)
    assert n == 16, f"{n} plans, not 16: the premise is being read off a different corpus"


# ------------------------------------------------------------------ the list, against the corpus

def test_the_unreached_list_is_held_to_the_corpus_in_both_directions():
    """`executed_but_unreached_in_the_corpus` is a CLAIM about the sixteen plans and this is
    its only reader that can fail. Both directions, because each catches a different lie: an
    id on the list that the corpus reaches is a rule being driven by hand for no reason, and a
    positioned rule off the list that the corpus never reaches is a guard nobody knows is
    vacuous. `fg-flanking-the-chimney-breast` is the case that decided the shape -- it is
    reached, eighteen times, and every one is a refusal, so it is NOT on the list."""
    seen = _rule_census()
    listed = list(GRAMMAR["executed_but_unreached_in_the_corpus"])
    assert listed, "an empty list makes both halves below vacuous"
    for rid in listed:
        assert rid not in seen, (
            f"{rid} is listed as unreached and the corpus reaches it: {seen.get(rid)}")
    for rid in F.POSITIONED:
        if rid not in listed:
            assert rid in seen, (
                f"{rid} is a positioned rule the corpus never reaches and it is not in "
                f"`executed_but_unreached_in_the_corpus`; the guards on it are vacuous")
    assert seen.get("fg-flanking-the-chimney-breast") == [0, 18], (
        f"the rule that decided the list's shape now reads "
        f"{seen.get('fg-flanking-the-chimney-breast')}: re-derive before re-pinning")
