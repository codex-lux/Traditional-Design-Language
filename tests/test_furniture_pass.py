"""WP-11.3 — the furniture pass, and the packer it shares with the fixtures.

Every assertion here was checked by MUTATION: the code it guards was broken and the test was
watched to go red. WP-11.1 found three guards in this repository that would have passed
vacuously and WP-11.2 found a fourth, so a test written and never seen to fail is not evidence.
"""
import importlib.util
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _mod(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "build", f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


FURN = _mod("furniture")
GEO = _mod("geometry")

PLANS = (sorted(glob.glob(os.path.join(ROOT, "plans", "*.json")))
         + sorted(glob.glob(os.path.join(ROOT, "plans", "reference", "*.json"))))


def _solved():
    """Every plan, on the DETERMINISTIC engine. Never `auto`: tests/test_furniture_drawn.py's
    own header records that the same sweep returned 130, 132 and 133 on one unchanged tree,
    because CP-SAT under a time budget is not reproducible under load."""
    for f in PLANS:
        yield f, GEO.solve(json.loads(open(f).read()), None, 250, engine="heuristic")


def test_the_leaf_imports_no_sibling():
    """build/furniture.py is loaded from build/openings.py, which build/geometry.py calls.
    An import back up closes a cycle -- build/storeys.py (WP-9.6) and build/assemblies.py
    (WP-11.2) are the precedent and both say so in their headers."""
    src = open(os.path.join(ROOT, "build", "furniture.py")).read()
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            assert "build" not in s or s.startswith("from __future__"), \
                f"furniture.py must stay a leaf; found {s!r}"
        assert "_mod(" not in s or s.startswith("#"), \
            f"furniture.py must not load a sibling by path either; found {s!r}"


def test_the_fit_arithmetic_is_not_restated_here():
    """plan_check.furniture_shortfalls is the ONE spelling of whether a room can hold a thing.
    This file answers where the thing goes, which is a different question."""
    src = open(os.path.join(ROOT, "build", "furniture.py")).read()
    assert "need_short" not in src and "need_long" not in src


def test_no_furniture_rectangle_leaves_its_room_or_overlaps_another():
    outside = overlap = total = 0
    for _f, sol in _solved():
        for lv in sol["levels"]:
            for r in lv["rooms"]:
                g = r.get("geometry")
                if not g:
                    continue
                X, Y, W, D = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
                seen = []
                for e in (r.get("furniture_layout") or []):
                    if e.get("unplaced"):
                        continue
                    total += 1
                    x, y, w, d = e["x_ft"], e["y_ft"], e["width_ft"], e["depth_ft"]
                    if x < X - 1e-6 or y < Y - 1e-6 or x + w > X + W + 1e-6 or y + d > Y + D + 1e-6:
                        outside += 1
                    for q in seen:
                        if (min(x + w, q[0] + q[2]) - max(x, q[0]) > 1e-6
                                and min(y + d, q[1] + q[3]) - max(y, q[1]) > 1e-6):
                            overlap += 1
                    seen.append((x, y, w, d))
    assert total > 400, f"only {total} placed items — the sweep is not reaching the corpus"
    assert outside == 0 and overlap == 0, f"{outside} outside their room, {overlap} overlapping"


def test_no_drawn_MARK_leaves_its_room_and_that_is_a_different_test():
    """THE RECTANGLE CHECK ABOVE CANNOT SEE THIS, and that is why both exist. The first draft
    of the piano symbol drew a grand's bent side as an arc whose radius scaled off the item's
    SHORT side; on an upright it swept straight through the wall. Measured: 13 of 1078 marks
    left their room while every item rectangle was inside it the whole time."""
    outside = total = 0
    for _f, sol in _solved():
        for lv in sol["levels"]:
            for r in lv["rooms"]:
                g = r.get("geometry")
                if not g:
                    continue
                X, Y, W, D = g["x_ft"], g["y_ft"], g["width_ft"], g["depth_ft"]
                for e in (r.get("furniture_layout") or []):
                    for m in (e.get("marks") or []):
                        total += 1
                        if "rect" in m:
                            box = m["rect"]
                        elif "circle" in m:
                            cx, cy, rr = m["circle"]
                            box = (cx - rr, cy - rr, 2 * rr, 2 * rr)
                        else:
                            x1, y1, x2, y2 = m["line"]
                            box = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                        if (box[0] < X - 1e-6 or box[1] < Y - 1e-6
                                or box[0] + box[2] > X + W + 1e-6
                                or box[1] + box[3] > Y + D + 1e-6):
                            outside += 1
    assert total > 800, f"only {total} marks — the sweep is not reaching the drawing"
    assert outside == 0, f"{outside} of {total} drawn marks leave the room they belong to"


def test_the_pass_never_writes_a_dimension():
    """docs/model.md, on OQ 92: a room's size comes from its programme and its catalogue band,
    and the furniture is arranged into the room as given. Authority runs one way."""
    for f, sol in _solved():
        declared = json.loads(open(f).read())
        for lv_d, lv_s in zip(declared["levels"], sol["levels"]):
            for rd, rs in zip(lv_d["rooms"], lv_s["rooms"]):
                assert rd.get("width_ft") == rs.get("width_ft"), f"{f}:{rd['id']} width moved"
                assert rd.get("length_ft") == rs.get("length_ft"), f"{f}:{rd['id']} length moved"


def test_only_objects_are_drawn_and_the_rest_are_counted():
    """`kind` decides, never the item's name. Nothing is dropped in silence: a skipped entry
    is counted against the grammar rule that refused it."""
    drawn_kinds = set()
    fired = set()
    C = _mod("plan_check").load_corpus()
    for _f, sol in _solved():
        rep = sol["opening_report"]
        assert rep["furniture_skipped"], "nothing was skipped anywhere — the filter is inert"
        assert set(rep["furniture_skipped"]) <= {"fg-not-an-object", "fg-too-thin-to-draw"}
        fired |= set(rep["furniture_skipped"])
        for lv in sol["levels"]:
            for r in lv["rooms"]:
                rt = C["rooms"].get(r["type"]) or {}
                by_name = {i["item"]: i for i in (rt.get("furniture") or [])}
                for e in (r.get("furniture_layout") or []):
                    it = by_name.get(e["item"])
                    if it:
                        drawn_kinds.add(it.get("kind"))
    assert drawn_kinds == {"object"}, f"a non-object was drawn: {drawn_kinds}"
    # BOTH refusal rules must actually fire somewhere in the corpus. The first draft asserted
    # only that the set was a SUBSET of the two, which a rule that stopped firing altogether
    # satisfies -- deleting the thin-item test left this green, and the mutation pass caught it.
    assert fired == {"fg-not-an-object", "fg-too-thin-to-draw"}, \
        f"a refusal rule never fired over sixteen plans: {fired}"


def test_a_reservation_is_never_drawn_even_though_it_has_a_footprint():
    """The class OQ 92 named: "clearance reservations wearing an item's shape". They carry a
    footprint, a placement and a clearance, and they are not things."""
    C = _mod("plan_check").load_corpus()
    route = next(i for i in C["rooms"]["entry-porch"]["furniture"]
                 if i["item"] == "clear route from step to door")
    assert route["kind"] == "reservation"
    assert FURN.drawable(route) == "fg-not-an-object"
    for _f, sol in _solved():
        for lv in sol["levels"]:
            for r in lv["rooms"]:
                for e in (r.get("furniture_layout") or []):
                    assert "clear route" not in e["item"], f"{r['id']} drew {e['item']!r}"


def test_the_stair_is_not_drawn_twice():
    """rooms/stair-hall.json carries "the stair itself, dog-leg with half landing" as a
    furniture item at 120 x 78 in, and openings.stair_pass already places and draws the stair.
    Unfiltered, the sheet draws two stairs in one room."""
    C = _mod("plan_check").load_corpus()
    it = next(i for i in C["rooms"]["stair-hall"]["furniture"] if i["item"].startswith("the stair"))
    assert it["kind"] == "placed-elsewhere"
    for _f, sol in _solved():
        for lv in sol["levels"]:
            for r in lv["rooms"]:
                for e in (r.get("furniture_layout") or []):
                    assert not e["item"].startswith("the stair"), f"{r['id']} drew the stair again"


def test_a_variant_is_an_alternative_and_only_one_bed_is_drawn():
    """rooms/bedroom.json states a queen bed, a full bed and twin beds. They are three
    alternatives, all `essential` by default, and a naive pass draws three beds in one room."""
    C = _mod("plan_check").load_corpus()
    # "bed" as a substring also matches "any bedroom occupied by anyone under twenty-five",
    # which is a desk. Select on the SYMBOL, which is what the drawing actually keys on.
    beds = [i for i in C["rooms"]["bedroom"]["furniture"]
            if FURN.symbol_for(i["item"]) == "bed"]
    assert len([b for b in beds if b["kind"] == "object"]) == 1, \
        "exactly one of the bedroom's beds is the object; the others are variants"
    for _f, sol in _solved():
        for lv in sol["levels"]:
            for r in lv["rooms"]:
                if r["type"] != "bedroom":
                    continue
                drawn = [e for e in (r.get("furniture_layout") or [])
                         if e.get("symbol") == "bed"]
                assert len(drawn) <= 1, f"{r['id']} drew {len(drawn)} beds"


def test_wet_and_service_rooms_stay_with_the_fixtures_and_the_gap_is_counted():
    """The two gates are exact complements, so no room gets two layouts drawn over each other.
    What the fixture pass does NOT reach in those rooms -- the kitchen's island and table --
    is a number rather than a silence."""
    C = _mod("plan_check").load_corpus()
    for _f, sol in _solved():
        for lv in sol["levels"]:
            for r in lv["rooms"]:
                fc = (C["rooms"].get(r["type"]) or {}).get("function_class")
                if fc in ("sanitary", "service"):
                    assert not r.get("furniture_layout"), \
                        f"{r['id']} is {fc} and got a furniture layout as well as fixtures"
    sol = GEO.solve(json.loads(open(os.path.join(
        ROOT, "plans", "tidewater-georgian-careful.json")).read()), None, 250, engine="heuristic")
    assert sol["opening_report"].get("furniture_not_reached", 0) > 0


def test_the_wall_run_reading_is_honoured():
    """fg-wall-run is the one READING among the placement rules: five items state a run of
    wall unbroken by openings and every figure is in the item's own sentence."""
    C = _mod("plan_check").load_corpus()
    runs = [(rid, i) for rid, rt in C["rooms"].items()
            for i in (rt.get("furniture") or []) if i.get("needs_uninterrupted_wall_ft")]
    assert len(runs) == 5, f"five items carry the field, found {len(runs)}"
    # THE ITEM MUST FIT THE SEGMENTS AND FAIL ONLY THE RUN, or the test proves nothing about
    # the rule. The first draft used the real 5.5 ft sideboard against 4 ft segments, so it was
    # refused for being too WIDE and passed with the run rule deleted -- caught by mutation.
    rect = (0.0, 0.0, 20.0, 12.0)
    spec = {"item": "sideboard", "w_in": 36, "d_in": 20, "min_run_ft": 6.0}
    # a wall chopped into 4 ft pieces cannot hold it; the same wall clear can
    # every wall chopped so that NO run reaches 6 ft -- the first draft of this fixture left
    # the 12 ft W wall with a single 2 ft block and therefore a 6 ft run, so it was asserting
    # that a run existed while claiming none did
    blocked = {("r", "S"): [(4.0, 6.0), (10.0, 12.0), (16.0, 18.0)],
               ("r", "N"): [(4.0, 6.0), (10.0, 12.0), (16.0, 18.0)],
               ("r", "W"): [(4.0, 6.0), (10.0, 12.0)],
               ("r", "E"): [(4.0, 6.0), (10.0, 12.0)]}
    out, _ = FURN.pack_against_walls(rect, "r", blocked, [{"spec": dict(spec)}], noun="furniture")
    assert out[0].get("unplaced"), "a 6 ft run was found on a wall that has none"
    out2, _ = FURN.pack_against_walls(rect, "r", {}, [{"spec": dict(spec)}], noun="furniture")
    assert not out2[0].get("unplaced"), "a clear wall refused a 6 ft run"


def test_every_placed_entry_names_the_rule_and_grade_that_seated_it():
    """A drawn thing whose provenance nobody can read is what furniture/grammar.json's grades
    exist to prevent."""
    grammar = json.load(open(os.path.join(ROOT, "furniture", "grammar.json")))
    ids = {r["id"] for b in ("placement_rules", "refusal_rules", "stated_rules_not_executed")
           for r in grammar.get(b, [])}
    grades = set(grammar["grades"])
    seen = set()
    for _f, sol in _solved():
        for lv in sol["levels"]:
            for r in lv["rooms"]:
                for e in (r.get("furniture_layout") or []):
                    assert e.get("rule") in ids, f"{e['item']!r} names rule {e.get('rule')!r}"
                    assert e.get("grade") in grades, f"{e['item']!r} grade {e.get('grade')!r}"
                    seen.add(e["rule"])
    assert "fg-wall-run" in seen, "the one reading never fired anywhere in the corpus"
    assert len(seen) >= 3, f"only {seen} fired — the rule set is not being exercised"


# ------------------------------------------------------------- WP-13.6: the swing, the corner, the axis
def _rp():
    return _mod("render_plan")


def test_a_pair_blocks_two_half_leaves_and_a_leafless_type_blocks_nothing():
    """`door_swings` reserved one square of the OPENING's width whatever the door type, so a 5 ft
    double door between the drawing and dining rooms took 5 x 5 ft of the dining room's floor
    while both renderers draw two 2.5 ft leaves. The block is the renderer's own leaf rule now:
    two squares of w/2 for a pair, one of w for a single leaf, none for a type drawn with no leaf.
    The renderer's rule is READ from its source beside the packer's, so the two cannot drift."""
    room = {"id": "r", "doors": [
        {"to": "a", "type": "double", "wall": "S", "position_ft": 10.0, "width_ft": 5.0, "swing_into": "r"},
        {"to": "b", "type": "swing", "wall": "W", "position_ft": 6.0, "width_ft": 3.0, "swing_into": "r"},
        {"to": "c", "type": "cased-opening", "wall": "N", "position_ft": 10.0, "width_ft": 6.0, "swing_into": "r"},
        {"to": "d", "type": "swing", "wall": "E", "position_ft": 6.0, "width_ft": 3.0, "swing_into": "a"},
    ]}
    blocks = sorted(FURN.door_swings(room, (0.0, 0.0, 20.0, 12.0)))
    assert blocks == sorted([(7.5, 0.0, 2.5, 2.5), (10.0, 0.0, 2.5, 2.5), (0.0, 4.5, 3.0, 3.0)]), blocks
    # the pair's two squares together cover the opening's width and HALF its width into the room
    pair = [b for b in blocks if b[1] == 0.0]
    assert min(b[0] for b in pair) == 7.5 and max(b[0] + b[2] for b in pair) == 12.5
    assert all(b[3] == 2.5 for b in pair), "a leaf of a pair sweeps its OWN width, not the opening's"
    # the leafless tuple is the renderer's, transcribed because this module is a leaf
    assert FURN.LEAFLESS == _rp().LEAFLESS
    # and the renderer really does draw a pair as two half-radius leaves and a single as one full
    src = open(os.path.join(ROOT, "build", "render_plan.py")).read()
    i = src.index("def _door(")
    door = src[i:i + 12000]                             # the nested function and its branches, comments included
    dbl = door[door.index('if dtype == "double"'):]
    dbl = dbl[:dbl.index("elif ")]
    assert dbl.count("leaf(") == 2 and "half," in dbl and "2 * half" not in dbl, dbl
    single = door[door.index("elif hinge =="):]
    single = single[:single.index("\n\n")]
    assert single.count("2 * half") == 2, "a single leaf sweeps the whole opening, from either jamb"


def test_a_corner_item_is_seated_in_a_corner_with_both_walls_free_and_refused_when_none_is():
    """fg-corner was listed EXECUTED with no code behind it; three catalogue items authored
    `corner` were packed as against-wall items. The first corner whose two walls are both free
    for it, in the packer's wall order; every corner blocked is a named refusal."""
    rect = (0.0, 0.0, 20.0, 12.0)
    spec = {"item": "corner cupboard", "w_in": 42, "d_in": 18, "corner": True, "rule": "fg-corner", "grade": "editorial"}
    out, placed = FURN.pack_against_walls(rect, "r", {}, [{"spec": dict(spec)}], noun="furniture")
    e = out[0]
    assert not e.get("unplaced") and e.get("corner") is True, e
    # it touches two walls: the SW corner, S first in the wall order and W first among the perpendiculars
    assert (e["x_ft"], e["y_ft"]) == (0.0, 0.0) and (e["width_ft"], e["depth_ft"]) == (3.5, 1.5), e
    # block the S wall's low end and the W wall's low end: the SW corner is gone, the SE is next
    occ = {("r", "S"): [(0.0, 2.0)], ("r", "W"): [(0.0, 2.0)]}
    out, _ = FURN.pack_against_walls(rect, "r", occ, [{"spec": dict(spec)}], noun="furniture")
    e = out[0]
    assert not e.get("unplaced") and e["corner"] is True and e["x_ft"] == 16.5 and e["y_ft"] == 0.0, e
    # every corner blocked on one of its two walls -> refused, naming the corner rule
    occ = {("r", "S"): [(0.0, 2.0), (18.0, 20.0)], ("r", "N"): [(0.0, 2.0), (18.0, 20.0)],
           ("r", "W"): [(0.0, 2.0), (10.0, 12.0)], ("r", "E"): [(0.0, 2.0), (10.0, 12.0)]}
    out, _ = FURN.pack_against_walls(rect, "r", occ, [{"spec": dict(spec)}], noun="furniture")
    assert out[0].get("unplaced") and "corner" in out[0]["unplaced"]["reason"], out[0]
    # and a corner seat at a wall's LOW end advances that wall's cursor, so the next wall item
    # does not land on top of it (the vacuity check: the second item must be clear of the first)
    out, _ = FURN.pack_against_walls(rect, "r", {}, [{"spec": dict(spec)},
                                    {"spec": {"item": "sideboard", "w_in": 60, "d_in": 20}}], noun="furniture")
    a, b = out
    assert not b.get("unplaced") and (b["x_ft"] >= a["x_ft"] + a["width_ft"] - 1e-6 or b["wall"] != a["wall"]), (a, b)


def test_the_catalogue_states_the_axis_and_a_run_cannot_be_shorter_than_the_item():
    """`footprint_in` is [along the wall, into the room] (schema, WP-13.6). The nine inverted
    records were re-authored by reading; the checker holds the one thing a number can hold: an
    item stating a wall run cannot need one shorter than its own length along the wall."""
    CR = _mod("check_rooms")
    C = _mod("plan_check").load_corpus()
    dining = C["rooms"]["dining-room"]
    sb = next(i for i in dining["furniture"] if i["item"] == "sideboard")
    assert sb["footprint_in"] == [66, 20], "the sideboard is 66 in ALONG the wall and 20 deep, as read"
    assert sb["footprint_in"][0] / 12.0 <= sb["needs_uninterrupted_wall_ft"]
    cc = next(i for i in dining["furniture"] if i["item"].startswith("china cupboard"))
    assert cc["footprint_in"] == [42, 18] and cc["placement"] == "corner"
    # the guard bites on a run shorter than the item, and only then
    import copy
    room = copy.deepcopy(dining)
    rep = CR.Report(); u = CR.build_universe()
    CR.check_room(rep, os.path.join(ROOT, "rooms", "dining-room.json"), room, u, {"dining-room"})
    before = [e for e in rep.errors if "shorter than itself" in str(e)]
    assert not before, before
    bad = next(i for i in room["furniture"] if i["item"] == "sideboard")
    bad["footprint_in"] = [80, 20]            # 6.67 ft along a 6 ft run
    rep = CR.Report()
    CR.check_room(rep, os.path.join(ROOT, "rooms", "dining-room.json"), room, u, {"dining-room"})
    hits = [e for e in rep.errors if "shorter than itself" in str(e)]
    assert len(hits) == 1 and "sideboard" in str(hits[0]), rep.errors
    # every wall-seated item that states a run passes it today, and the count is the census's
    runs = [(rid, i) for rid, rt in C["rooms"].items() for i in (rt.get("furniture") or [])
            if i.get("needs_uninterrupted_wall_ft")]
    assert len(runs) == 5
    for rid, i in runs:
        assert i["footprint_in"][0] / 12.0 <= i["needs_uninterrupted_wall_ft"] + 1e-9, (rid, i["item"])
