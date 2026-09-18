"""WP-13.8 — the entrance front's population is the MAIN BLOCK's.

`axis.front_openings` swept every room on the level with no element filter of any kind. The
moment WP-13.5 gave `plans/tidewater-georgian-careful.json` a west dependency, that wing's four
south-facing openings joined the main block's front at x -27.9, -18.4, -14.4 and -10.4 on a block
that starts at 0 — and two layers convicted them:

  * `axis.mirror` reflected each about `footprint_centre` (22.5 ft), found the twin would have to
    stand at 55 to 73 ft on a 45 ft block, and returned all four as `unmatched`. `elevation.py`
    turns that count into `count_of_openings_without_a_mirror_twin_about_the_facade_centreline`,
    which `faults/one-bay-symmetry-break.json` tests `at-most 0` at severity FATAL.
  * `facade.compare` emitted four `front-opening-in-no-bay` minors naming the same four.

A wing's window measured against the main block's centre line is a defect reported where none is
possible — the OQ 52 family — and the remedy is the one applied since WP-11.9: read
`build/elements.py`, which is the corpus's ONE reader of which element a room stands in.

WHAT THIS DID NOT DO, MEASURED AND NOT ASSUMED. The fatal does NOT clear. On the shipped Tidewater
plan the mirror's unmatched count falls 7 → 3 and the fault still fires, because the main block's
own front really is asymmetric on the search placement (10.95, 16.95, 27.21, 35.98, 40.49 about a
centre of 22.5, where only one pair matches). Removing a false conviction is not the same as
clearing a true one, and a report claiming otherwise would be the flattering direction.

WHY THESE GUARDS ARE DRIVEN. Fifteen of the sixteen shipped plans are one rectangle, so the
branch that matters is unreachable on them — a guard that runs only where the bug cannot occur is
not a guard. The fixtures below are hand-built on WP-11.10's stated precedent, with the dependency
at NEGATIVE x on purpose: the defect published negative coordinates, and a fixture with both
elements at positive x lets a wrong answer look plausible.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
import modcache  # noqa: E402

AX = modcache.load("axis", str(ROOT / "build" / "axis.py"))
EL = modcache.load("elements", str(ROOT / "build" / "elements.py"))
FA = modcache.load("facade", str(ROOT / "build" / "facade.py"))
GEO = modcache.load("geometry", str(ROOT / "build" / "geometry.py"))
DS = modcache.load("diagnose_sheet", str(ROOT / "build" / "diagnose_sheet.py"))

MAIN = {"id": "main", "role": "main", "x_ft": 0.0, "y_ft": 0.0,
        "width_ft": 40.0, "depth_ft": 42.0, "area_sf": 1680}
DEP = {"id": "service", "role": "dependency", "x_ft": -37.0, "y_ft": 0.0,
       "width_ft": 30.0, "depth_ft": 24.0, "area_sf": 720, "attached_to": "main"}


def _room(rid, rtype, x, y, w, d, block=None, windows=None, doors=None):
    r = {"id": rid, "type": rtype, "width_ft": w, "length_ft": d,
         "geometry": {"x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": d}}
    if block:
        r["block"] = block
    if windows:
        r["windows"] = windows
    if doors:
        r["doors"] = doors
    return r


def _win(wall, *positions, width=3.0):
    return {"wall": wall, "count": len(positions), "width_ft": width,
            "positions_ft": list(positions)}


def _two_element_plan():
    """A placed record whose WEST dependency has south-facing openings of its own.

    The main block runs x 0..40 and the wing x -37..-7, so every wing coordinate is negative and
    cannot be mistaken for one inside the block. The main block's two front windows are placed
    SYMMETRICALLY about its centre (20.0) so that the only thing the mirror can be unhappy about
    is the wing — otherwise a falling unmatched count would not tell us which openings left.
    """
    return {
        "id": "fixture-two-element", "style": "tidewater-georgian",
        "parti": "centre-passage-double-pile",
        "context": {"entrance_faces": "S"},
        "footprint": {"width_ft": 40.0, "depth_ft": 42.0, "bays": 5, "bay_module_ft": 8.0,
                      "blocks": [MAIN, DEP]},
        "levels": [
            {"index": 0, "id": "ground", "rooms": [
                _room("drawing", "drawing-room", 0.0, 0.0, 20.0, 21.0,
                      windows=[_win("S", 12.0)]),
                _room("dining", "dining-room", 20.0, 0.0, 20.0, 21.0,
                      windows=[_win("S", 28.0)]),
                _room("library", "library", 0.0, 21.0, 40.0, 21.0),
                _room("kitchen", "kitchen", -37.0, 0.0, 30.0, 12.0, block="service",
                      windows=[_win("S", -30.0, -20.0)]),
                _room("pantry", "pantry", -37.0, 12.0, 30.0, 12.0, block="service"),
            ]},
        ],
    }


def _one_element_plan():
    """The same house with no wing at all — every shipped plan but one is this shape."""
    return {
        "id": "fixture-one-element", "style": "tidewater-georgian",
        "context": {"entrance_faces": "S"},
        "footprint": {"width_ft": 40.0, "depth_ft": 42.0, "bays": 5, "bay_module_ft": 8.0},
        "levels": [
            {"index": 0, "id": "ground", "rooms": [
                _room("drawing", "drawing-room", 0.0, 0.0, 20.0, 21.0,
                      windows=[_win("S", 12.0)]),
                _room("dining", "dining-room", 20.0, 0.0, 20.0, 21.0,
                      windows=[_win("S", 28.0)]),
            ]},
        ],
    }


def _blind_sweep(plan, level=0):
    """An INDEPENDENT element-blind reader, kept here on purpose.

    WP-12.7's rule: a guard that re-uses the function under test to compute its own expectation
    proves nothing. This is the arithmetic `front_openings` USED to do, written out, so the
    one-rectangle assertion below compares against something that is not the code being guarded.
    """
    front = ((plan.get("context") or {}).get("entrance_faces") or "S").upper()
    out = []
    for lv in plan.get("levels", []):
        if (lv.get("index") or 0) != level:
            continue
        for r in lv.get("rooms", []):
            for w in (r.get("windows") or []):
                if (w.get("wall") or "").upper() != front or w.get("unplaced"):
                    continue
                for x in (w.get("positions_ft") or []):
                    out.append((r["id"], round(x, 3)))
            for d in (r.get("doors") or []):
                if d.get("to") != "exterior" or d.get("unplaced"):
                    continue
                if (d.get("wall") or "").upper() != front or d.get("position_ft") is None:
                    continue
                out.append((r["id"], round(d["position_ft"], 3)))
    return sorted(out, key=lambda t: t[1])


# --------------------------------------------------------------- the filter itself
def test_a_wings_front_openings_are_not_the_main_blocks():
    fo = AX.front_openings(_two_element_plan(), 0)
    assert fo["element_filter"] == "main-block"
    assert fo["elements"] == 3 - 1, "the fixture states two elements"

    xs = sorted(o["pos_ft"] for o in fo["openings"])
    assert xs == [12.0, 28.0], (
        f"the main block's front is its own two windows; got {xs}. A negative coordinate here is "
        f"the wing's opening, which is the whole defect this file is about.")

    off = fo["off_the_main_block"]
    assert sorted(o["pos_ft"] for o in off) == [-30.0, -20.0]
    assert {o.get("element") for o in off} == {"service"}, (
        "an opening that is not the main block's must say WHICH element it stands in -- reported, "
        "not judged, and not silently dropped")
    assert fo["element_unresolved"] == []


def test_the_mirror_reads_the_main_blocks_own_front():
    """The fatal's own measurement. `one-bay-symmetry-break` tests it `at-most 0`."""
    mi = AX.mirror(_two_element_plan(), 0)
    assert mi["verdict"] == "mirrored", (
        f"the fixture's two main-block windows are symmetric about the block's centre of 20.0, so "
        f"nothing should be unmatched; got {mi.get('unmatched')}")
    assert mi["openings"] == 2


def test_the_facade_does_not_convict_a_wings_opening_of_standing_in_no_bay():
    cm = FA.compare(_two_element_plan(), 0)
    assert cm.get("verdict") == "compared", (
        f"premise: this fixture must REACH the comparison, or the assertion below is about "
        f"nothing. {cm.get('why')}")
    orphans = [f for f in cm["findings"] if f["kind"] == "front-opening-in-no-bay"]
    assert not orphans, (
        f"the wing's openings are not bays of the main block's front: {orphans}")


# --------------------------------------------------------------- what must not move
def test_a_one_rectangle_house_is_untouched_by_the_filter():
    """Fifteen of sixteen shipped plans are this shape and none of them may move."""
    plan = _one_element_plan()
    fo = AX.front_openings(plan, 0)
    assert [(o["room"], o["pos_ft"]) for o in fo["openings"]] == _blind_sweep(plan), (
        "on one element the filtered population must equal the element-blind one, computed here "
        "by an independent reader rather than by the function under test")
    assert fo["off_the_main_block"] == [] and fo["element_unresolved"] == []
    assert fo["element_filter"] == "main-block" and fo["elements"] == 1


def test_a_record_with_no_footprint_is_not_filtered_rather_than_filtered_to_nothing():
    """REFUSING to filter is not the same as filtering to nothing, and the difference is a front.

    `elements()` returns [] where the record states no width or depth, so every room would fall
    to `element_of() is None` and the whole front would come back EMPTY -- a new defect of exactly
    the kind this package exists to remove, introduced by its own fix. The premise is asserted
    first so this cannot pass by the fixture quietly acquiring a footprint.
    """
    plan = _one_element_plan()
    plan.pop("footprint")
    assert EL.elements(plan) == [], "premise: a record with no footprint has no element model"
    fo = AX.front_openings(plan, 0)
    assert fo["element_filter"] == "not-applied"
    assert [(o["room"], o["pos_ft"]) for o in fo["openings"]] == _blind_sweep(plan)
    assert fo["openings"], "the front is not empty merely because the elements could not be read"


def test_a_room_in_no_element_is_unresolved_and_never_the_main_blocks():
    """WP-11.9's rule: a room in NO element is unjudged, never assigned to element zero."""
    plan = _two_element_plan()
    stray = _room("stray", "porch", -6.0, 0.0, 8.0, 8.0, windows=[_win("S", -2.0)])
    plan["levels"][0]["rooms"].append(stray)
    assert EL.element_of(plan, stray) is None, (
        "premise: this rectangle straddles the gap and lies in neither element")
    fo = AX.front_openings(plan, 0)
    assert [o["pos_ft"] for o in fo["element_unresolved"]] == [-2.0]
    assert all(o["room"] != "stray" for o in fo["openings"]), (
        "a room the element model cannot place must not be defaulted into the main block -- "
        "defaulting there is the defect itself")
    assert all(o["room"] != "stray" for o in fo["off_the_main_block"]), (
        "nor may it be asserted to be OUTSIDE the main block; unjudged is a third answer")


# --------------------------------------------------------------- the readers downstream
def test_door_bay_names_the_wing_rather_than_reporting_no_door():
    """Two causes, two messages (WP-11.4). 'No door on the front' is a true sentence about a
    different house, and handing it to a reader whose door is simply in the wing is the shape
    that entry forbids."""
    plan = _two_element_plan()
    kitchen = next(r for r in plan["levels"][0]["rooms"] if r["id"] == "kitchen")
    kitchen["doors"] = [{"to": "exterior", "wall": "S", "position_ft": -22.0, "width_ft": 3.0}]
    db = AX.door_bay(plan)
    assert db["verdict"] == "could-not-evaluate"
    assert "another massing element" in db["why"] and "service" in db["why"], db["why"]

    bare = _two_element_plan()          # the control: no front door anywhere
    assert AX.door_bay(bare)["why"].startswith("no exterior door is placed"), (
        "the other cause must keep its own message, or one of the two is unreachable")


def test_diagnose_sheet_takes_the_population_from_axis_and_does_not_spell_it_again():
    """One rule, one spelling. `diagnose_sheet` keeps its own per-storey and alignment logic --
    a different question keeps its own code -- but the answer to 'which openings are on the
    entrance front' is `axis.front_openings`' alone."""
    plan = _two_element_plan()
    rows = DS.front_openings(plan)
    ground = next(r for r in rows if r["level"] == "ground")
    fo = AX.front_openings(plan, 0)
    assert [o["x_ft"] for o in ground["openings"]] == [o["pos_ft"] for o in fo["openings"]]
    assert [o["x_ft"] for o in ground["off_the_main_block"]] == \
           [o["pos_ft"] for o in fo["off_the_main_block"]]
    assert ground["off_the_main_block"], (
        "the diagnostic must SAY what it set aside; a table whose count silently shrank is the "
        "fake-unjudged shape in the one surface a reader opens to find out what the sheet shows")


# --------------------------------------------------------------- the corpus, and the premise
def test_some_shipped_plan_states_a_container_so_these_fixtures_are_not_redundant():
    """WP-11.15's rule. Until WP-13.5 no shipped plan carried a `block` tag and this whole file
    would have been about a case the corpus cannot reach. Exactly one does now; if that stops
    being true, the fixtures above are the only coverage and this says so."""
    tagged = []
    for p in sorted((ROOT / "plans").glob("*.json")) + \
             sorted((ROOT / "plans" / "reference").glob("*.json")):
        d = json.loads(p.read_text())
        if any(r.get("block") or r.get("hyphen")
               for lv in d.get("levels", []) for r in lv.get("rooms", [])):
            tagged.append(p.name)
    assert tagged == ["tidewater-georgian-careful.json"], (
        f"the shipped container set moved: {tagged}. Re-measure the corpus control in "
        f"docs/reports/wp-13.8-*.md rather than trusting its 15-of-16 figure.")


def test_the_shipped_container_plan_convicts_no_wing_opening_of_standing_in_no_bay():
    """The corpus half, on the deterministic engine. Four `front-opening-in-no-bay` minors on
    this plan were the wing's, every one of them, and they are the measured 107 → 103."""
    plan = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())
    sol = GEO.solve(plan, engine="heuristic")
    rec = sol if sol.get("levels") else sol.get("plan", sol)
    fo = AX.front_openings(rec, 0)
    assert fo["elements"] > 1, "premise: this record places more than one massing element"
    assert fo["off_the_main_block"], (
        "premise: the wing really does carry openings on the entrance face -- without them this "
        "test passes while proving nothing")
    assert all(o["pos_ft"] >= 0 for o in fo["openings"]), (
        f"a negative coordinate on a block that starts at 0 is a wing opening in the main block's "
        f"front: {[o for o in fo['openings'] if o['pos_ft'] < 0]}")
    cm = FA.compare(rec, 0)
    assert cm.get("verdict") == "compared", (
        f"premise: the shipped container plan must reach the facade comparison. {cm.get('why')}")
    assert not [f for f in cm["findings"] if f["kind"] == "front-opening-in-no-bay"], (
        "these four were the wing's, and they are the measured minor 107 -> 103")
