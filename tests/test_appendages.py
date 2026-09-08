"""WP-11.10 — the terrace at grade.

`PLAN-OF-ACTION.md` gated this package on
`oq/the-proving-engine-cannot-place-a-second-massing-element`, on the assumption that an
at-grade unroofed thing on the wall of the room it serves is a third massing ROLE. Ruled
7 September 2026: it is not. An at-grade appendage is a plan-level record on
`plan.threshold`'s precedent -- derived after the solve, drawn outside the block by both
renderers, read by no structural layer, carrying no `block` tag. So the CP refusal (which
keys on the tag) never fires, no plan trades its proof for a search, and the question stays
open and untouched.

**THE GUARANTEE THIS FILE HOLDS IS THE INVERSE OF WP-11.9'S.** That package held the
placement AND the openings byte-identical, because it taught six layers a concept no plan
exercises. This one holds the PLACEMENT byte-identical and moves the OPENINGS on purpose,
on the five plans that declare a terrace and on no others -- one refused door becoming a
placed door is the whole deliverable.
"""
import glob
import hashlib
import json
import re
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(name, sub="build"):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, ROOT / sub / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = _mod("appendages")
G = _mod("geometry")
PC = _mod("plan_check")
OP = _mod("openings")


def _plans():
    return (sorted(glob.glob(str(ROOT / "plans" / "*.json")))
            + sorted(glob.glob(str(ROOT / "plans" / "reference" / "*.json"))))


_SOLVED = {}


def _solved(pf):
    if pf not in _SOLVED:
        d = json.loads(pathlib.Path(pf).read_text())
        G._SOLVE_CACHE.clear()
        _SOLVED[pf] = G.solve(json.loads(json.dumps(d)), engine="heuristic")
    return _SOLVED[pf]


def _all():
    for pf in _plans():
        d = json.loads(pathlib.Path(pf).read_text())
        if "levels" not in d:
            continue
        yield pathlib.Path(pf).name, _solved(pf)


# --------------------------------------------------------------- the reading itself

def test_only_a_room_whose_own_record_puts_it_outside_the_block_is_an_appendage():
    """`void.within_footprint: false` is the field OQ 55 authored for this question and the
    only one that answers it. A room with NO `void` block defaults to that value in
    `geometry.void_spec`, and the default deliberately does NOT make it an appendage: the
    default means nobody has judged the room, and promoting an unjudged room to a drawn
    rectangle outside the house is OQ 55's own silent promotion from the other side."""
    rooms = {}
    for rf in sorted(glob.glob(str(ROOT / "rooms" / "*.json"))):
        r = json.loads(pathlib.Path(rf).read_text())
        rooms[r["id"]] = r
    got = sorted(t for t in rooms if A.is_at_grade_appendage(t, rooms))
    assert got == ["terrace"], f"the corpus's at-grade appendages are {got}"
    # every OTHER outdoor room is a reserved void inside the block, and must not be one
    outdoor = sorted(t for t, r in rooms.items() if r.get("function_class") == "outdoor")
    assert outdoor == ["courtyard", "loggia", "piazza", "terrace"]
    # and a room with no `void` block at all is not promoted
    assert not A.is_at_grade_appendage("kitchen", rooms)
    assert not A.is_at_grade_appendage(
        "x", {"x": {"function_class": "outdoor"}}), "an unjudged outdoor room was promoted"


def test_the_face_is_the_one_both_readings_of_exterior_walls_admit():
    """THE MEASUREMENT THAT FORCED THE INTERSECTION. `exterior_walls` means two different
    things across the six terrace records in this corpus: `tidewater-georgian-careful`
    declares E, N and S, which can only be *the free faces* (a rectangle cannot be attached
    on three sides), while `good-02`, `good-04` and `good-07` each declare exactly one,
    which reads as *the side of the house it is on*. Measured: neither reading resolves the
    six on its own -- the free-face reading turns one declared wall into three candidates,
    the side-of-the-house reading turns three declared walls into three. Both admit `w`
    exactly when `w` is declared and its opposite is not, and that is what is taken."""
    # three free faces: only E survives, because N and S are opposite each other
    assert A.served_face({"exterior_walls": ["E", "N", "S"]}, [{"E": (0, 1), "N": (0, 1)}]) == "E"
    # one declared face, and the served room is on two boundaries: the field decides
    assert A.served_face({"exterior_walls": ["W"]}, [{"N": (0, 1), "W": (0, 1)}]) == "W"
    # BOTH readings on their own get this wrong, and that is the point
    assert A.served_face({"exterior_walls": ["E", "N"]}, [{"E": (0, 1), "N": (0, 1)}]) is None, (
        "two candidates is UNJUDGED; taking the first would be a guess"
    )
    # a face the placement did not put outside is not a candidate however it is declared
    assert A.served_face({"exterior_walls": ["E"]}, [{"N": (0, 1)}]) is None
    # nothing declared says nothing
    assert A.served_face({"exterior_walls": []}, [{"N": (0, 1)}]) is None
    # opposite pairs cancel: a rectangle attached on neither of two opposite faces
    assert A.served_face({"exterior_walls": ["N", "S"]}, [{"N": (0, 1), "S": (0, 1)}]) is None


def test_the_rules_quote_the_records_they_name():
    """Reused rather than rewritten: `check_openings.check_basis` already verifies that a
    basis names a record that exists, quotes something that record really says, AND that the
    quote lives under the key path cited. `build/check_furniture.py` calls it for the same
    reason. A second copy of that machinery is the thing this corpus keeps being bitten by."""
    CO = _mod("check_openings")

    class _Rep:
        def __init__(self):
            self.errs, self.unj = [], []

        def err(self, where, msg):
            self.errs.append((where, msg))

        def unjudged(self, where, msg):
            self.unj.append((where, msg))

    rep = _Rep()
    for rule in A.RULES:
        assert rule["grade"] in ("reading", "editorial-from-prose", "editorial")
        CO.check_basis(rep, rule, source="build/appendages.py")
    assert not rep.errs, rep.errs
    assert not rep.unj, rep.unj


# --------------------------------------------------------------- what the corpus does

PLACED, REFUSED = 4, 2


def test_the_corpus_places_four_appendages_and_refuses_two_by_name():
    placed, refused = [], []
    for name, sol in _all():
        ap = sol.get("appendages") or {}
        placed += [(name, e["room"], e["wall"]) for e in ap.get("placed", [])]
        refused += [(name, e["room"], e["code"]) for e in ap.get("unplaced", [])]
    assert len(placed) == PLACED, placed
    assert len(refused) == REFUSED, refused
    assert sorted(placed) == [
        ("good-02-portico-library-house.json", "terrace", "W"),
        ("good-04-rambling-porch-farmhouse.json", "terrace", "N"),
        ("good-07-diamond-plan-house.json", "terrace", "N"),
        ("tidewater-georgian-careful.json", "terrace", "E"),
    ]
    # THE TWO REFUSALS ARE THE HONEST HALF and neither is patched into a placement:
    # `wood-deck-w` declares no door at all, and `wood-deck-e` declares two rooms whose
    # boundary faces leave E and N both admissible. Reading `should_adjoin` for the first,
    # or taking the first candidate for the second, would each be a guess wearing a figure.
    assert sorted(refused) == [
        ("bad-07-octagon-dinette-colonial.json", "wood-deck-e", "no-face-both-readings-admit"),
        ("bad-07-octagon-dinette-colonial.json", "wood-deck-w", "no-door"),
    ]


def test_a_roofed_appendage_is_refused_rather_than_placed():
    """NO RECORD IN THIS CORPUS TAKES THIS BRANCH, and a first mutation pass found it could
    not fire: deleting the refusal left the suite green. It is kept, and tested here on a
    synthetic catalogue, because the moment a record says `within_footprint: false` and
    `roofed: true` -- an appended roofed porch -- it is a mass with a roof over it and belongs
    to `oq/the-proving-engine-cannot-place-a-second-massing-element`, not to this pass. A
    branch that cannot fire is worse than no branch; a branch that cannot fire on the SHIPPED
    corpus and is proved to bite on a fixture is a guard."""
    cat = {"deck": {"function_class": "outdoor",
                    "void": {"within_footprint": False, "roofed": True}},
           "kitchen": {"function_class": "service"}}
    plan = {"levels": [{"index": 0, "rooms": [
        {"id": "deck", "type": "deck", "name": "Deck", "width_ft": 10, "length_ft": 12,
         "exterior_walls": ["N"], "doors": [{"to": "kit"}]},
        {"id": "kit", "type": "kitchen", "name": "Kitchen",
         "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 20, "depth_ft": 20}}]}]}
    rep = {}
    rects = A.appendage_pass(plan, cat, rep, lambda p, rooms: {"kit": (0.0, 0.0, 20.0, 20.0)},
                             lambda rect, bounds: {"N": (0.0, 20.0)})
    assert rects == {}
    assert [e["code"] for e in plan["appendages"]["unplaced"]] == ["roofed"]
    assert rep["appendages_placed"] == 0 and rep["appendages_unplaced"] == 1
    # and with the SAME record unroofed it places, so the fixture proves the branch and not
    # some other refusal standing in front of it
    cat["deck"]["void"]["roofed"] = False
    plan2 = json.loads(json.dumps(plan))
    for lv in plan2["levels"]:
        for r in lv["rooms"]:
            r.pop("geometry", None) if r["id"] == "deck" else None
    A.appendage_pass(plan2, cat, {}, lambda p, rooms: {"kit": (0.0, 0.0, 20.0, 20.0)},
                     lambda rect, bounds: {"N": (0.0, 20.0)})
    assert [e["room"] for e in plan2["appendages"]["placed"]] == ["deck"]
    assert plan2["appendages"]["placed"][0]["wall"] == "N"


def _synthetic(**over):
    """One served room 20 x 20 at the origin, its N face on the element boundary, and one
    appendage hanging off it. The shipped corpus exercises neither the missing-figure refusal
    nor the clamp -- every terrace record states both figures and none asks for more run than
    its face has -- so both are proved here rather than left as branches nothing can reach."""
    room = {"id": "deck", "type": "deck", "name": "Deck", "width_ft": 10, "length_ft": 12,
            "exterior_walls": ["N"], "doors": [{"to": "kit"}]}
    room.update(over)
    plan = {"levels": [{"index": 0, "rooms": [room,
            {"id": "kit", "type": "kitchen", "name": "Kitchen",
             "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 20, "depth_ft": 20}}]}]}
    cat = {"deck": {"function_class": "outdoor",
                    "void": {"within_footprint": False, "roofed": False}},
           "kitchen": {"function_class": "service"}}
    A.appendage_pass(plan, cat, {}, lambda p, rooms: {"kit": (0.0, 0.0, 20.0, 20.0)},
                     lambda rect, bounds: {"N": (0.0, 20.0)})
    return plan["appendages"]


def test_a_figure_the_record_does_not_state_is_a_refusal_and_never_a_band_midpoint():
    """`rooms/terrace.json` bands `width_ft [10, 30]`, and taking an end or a midpoint of that
    band for a record that states no width is exactly the laundering this corpus refuses."""
    assert [e["code"] for e in _synthetic(width_ft=None)["unplaced"]] == ["no-depth"]
    assert [e["code"] for e in _synthetic(length_ft=None)["unplaced"]] == ["no-run"]
    assert not _synthetic(width_ft=None)["placed"]


def test_a_run_longer_than_the_face_is_clamped_and_the_clamp_is_disclosed():
    """A terrace may run past the room it opens from -- along the garden front, which is what
    a terrace does -- but not past the element it is appended to. The clamp is a `need`/`have`
    on the record, in the shape every other refusal in this corpus takes, so a reader sees the
    figure the record asked for beside the one the placement could give."""
    ap = _synthetic(length_ft=40)["placed"][0]
    assert ap["rect"]["width_ft"] == 20.0, "the run was not clamped to the element's face"
    clamp = ap["figures"]["run_ft"]["clamped"]
    assert clamp["need"] == 40.0 and clamp["have"] == 20.0
    # and an unclamped run carries no clamp block at all
    assert "clamped" not in _synthetic()["placed"][0]["figures"]["run_ft"]


def test_every_refusal_code_is_in_the_closed_set_and_carries_its_reason():
    """build/construction_vocabulary.py's precedent: a table that is CLOSED, and a reason
    per entry. A refusal outside the set is a silence with a name on it."""
    for name, sol in _all():
        for e in ((sol.get("appendages") or {}).get("unplaced") or []):
            assert e["code"] in A.REFUSALS, (name, e["code"])
            assert e["reason"] == A.REFUSALS[e["code"]]
    # AND EVERY ENTRY CARRIES THE ROOM'S DECLARED NAME, because both renderers draw it and
    # neither may look it up: an appendage has no `room.geometry`, so the label loop that
    # names every other room never reaches it. `bad-07` is the case that proves it -- its
    # decks are named "Wood Deck (west)" and "Wood Deck (east)" against ids that are neither,
    # so a renderer falling back to the id would be visibly wrong there and invisibly right
    # on every plan whose terrace is called "Terrace".
    sol = _solved(str(ROOT / "plans" / "reference" / "bad-07-octagon-dinette-colonial.json"))
    got = {e["room"]: e["name"] for e in sol["appendages"]["unplaced"]}
    assert got == {"wood-deck-w": "Wood Deck (west)", "wood-deck-e": "Wood Deck (east)"}, got


def test_no_appendage_room_is_given_a_rectangle_and_that_is_what_keeps_six_layers_blind():
    """THE MECHANISM OF THE RULING. `structure.wall_lines` filters `r.get("geometry")`,
    `plan_check`'s `rooms_unplaced` filters `takes_a_rectangle`, and
    `geometry._record_prep`/`blocks_record` filter `is_placed` -- so long as the appendage's
    room carries no `geometry`, all three are blind to it BY CONSTRUCTION and WP-11.9's six
    taught layers are not reopened. Writing a rectangle onto the room would be the whole
    package's one real defect, and it would be invisible: the drawing would look right."""
    for name, sol in _all():
        ids = {e["room"] for e in ((sol.get("appendages") or {}).get("placed") or [])}
        for lv in sol["levels"]:
            for r in lv["rooms"]:
                if r["id"] in ids:
                    assert not r.get("geometry"), (
                        f"{name}: {r['id']} was given a rectangle; six layers can now see it")
    # and the block record still holds no appendage
    for name, sol in _all():
        ids = {e["room"] for e in ((sol.get("appendages") or {}).get("placed") or [])}
        for b in ((sol.get("footprint") or {}).get("blocks") or []):
            assert not (set(b.get("rooms") or []) & ids), f"{name}: an appendage entered a block"


def test_a_plan_with_no_appendage_gets_no_key_written_into_any_room():
    for name, sol in _all():
        ap = sol.get("appendages") or {}
        if ap.get("placed") or ap.get("unplaced"):
            continue
        assert ap["note"] == "No at-grade appendage on this plan."


def test_strip_placement_removes_the_appendages():
    """The DXF round trip must return the AUTHORED record. `appendages` is solver output in
    exactly the sense `threshold` and `hearths` are."""
    assert "appendages" in OP.PLACEMENT_PLAN_KEYS
    sol = json.loads(json.dumps(_solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))))
    assert sol.get("appendages")
    OP.strip_placement(sol)
    assert "appendages" not in sol


# --------------------------------------------------------------- the door, which is the point

def test_the_terrace_door_is_placed_and_the_windows_moved_round_it():
    """`breakfast` declares two doors and BOTH were refused: one to the kitchen for want of
    a shared wall (the placer's, and untouched here) and one to the terrace because the
    terrace had no rectangle. This package removes the second reason only, and the report
    must say so rather than claim the fatal."""
    sol = _solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))
    rooms = {r["id"]: r for lv in sol["levels"] for r in lv["rooms"]}
    d = next(x for x in rooms["breakfast"]["doors"] if x["to"] == "terrace")
    assert "unplaced" not in d and d["wall"] == "E"
    k = next(x for x in rooms["breakfast"]["doors"] if x["to"] == "kitchen")
    assert "unplaced" in k, "the kitchen door is the placer's failure and is NOT this package's"
    # the other side of the same door, on the terrace's own record
    t = next(x for x in rooms["terrace"]["doors"] if x["to"] == "breakfast")
    assert t.get("wall") == "W" and t["position_ft"] == d["position_ft"]
    # and the two authored E windows re-seated around it rather than being overwritten
    w = next(x for x in rooms["breakfast"]["windows"] if x["wall"] == "E")
    assert w["count"] == 2 and len(w["positions_ft"]) == 2
    assert all(abs(p - d["position_ft"]) > 1.5 for p in w["positions_ft"])


def test_place_interior_reads_the_appendage_rects_and_rect_is_left_alone():
    """`_rect` has six other call sites and every one of them must go on seeing a terrace as
    unplaced. The rectangle is threaded into the ONE reader that needs it, on WP-11.9's
    `bounds=` precedent."""
    src = (ROOT / "build" / "openings.py").read_text()
    assert "def _place_interior(level_rooms, occupied, report, appendages=None):" in src
    assert "ra, rb = _r(a), _r(b)" in src
    assert src.count("def _rect(r):") == 1
    body = src[src.index("def _rect(r):"):src.index("def _shared(")]
    assert "appendage" not in body, "_rect learned about appendages; six readers now see one"


def test_the_pass_runs_before_the_level_loop():
    """FORCED, not tidy: `_place_interior` is the first pass inside the loop, so an
    appendage derived after it can never seat the door it exists for. `entrance_pass` runs
    last for the opposite reason -- it reads placed doors."""
    src = (ROOT / "build" / "openings.py").read_text()
    assert src.index("apx = _appd().appendage_pass(") < src.index('for _li, lv in enumerate(plan["levels"]):')
    assert src.index("apx = _appd().appendage_pass(") < src.index("th = _thresh().entrance_pass(")


# --------------------------------------------------------------- outside

def test_a_placed_at_grade_appendage_is_outside_for_the_reachability_walk():
    """A person standing on a terrace is outside the house, and `outside` was seeded from
    placed `to: "exterior"` doors alone. The guard is narrow and every clause is read off the
    record: PLACED (a refused appendage mints no way in), `at_grade`, and NOT `roofed`."""
    def _plan(**ap):
        return {
            "id": "t", "name": "t", "style": "tidewater-georgian",
            "footprint": {"width_ft": 20, "depth_ft": 20},
            "appendages": {"placed": [dict({"room": "yard", "at_grade": True, "roofed": False},
                                           **ap)], "unplaced": []},
            "levels": [{"index": 0, "rooms": [
                {"id": "yard", "type": "terrace", "name": "Yard", "width_ft": 10, "length_ft": 10,
                 "doors": [{"to": "kit", "width_ft": 3, "wall": "E", "position_ft": 5}]},
                {"id": "kit", "type": "kitchen", "name": "Kitchen", "width_ft": 20, "length_ft": 20,
                 "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 20, "depth_ft": 20, "area_sf": 400},
                 "doors": [{"to": "yard", "width_ft": 3, "wall": "W", "position_ft": 5}]}]}]}
    def _kinds(res):
        return {f.get("kind") for f in res["findings"] if f["layer"] == "drawn"}

    res = PC.check(_plan())
    assert res["drawn_summary"]["unreachable"] == [], "the terrace is not being read as outside"
    assert "no-outside" not in _kinds(res)
    assert "outside-is-only-an-appendage" in _kinds(res), (
        "the one way in is a terrace door and nothing says so")
    # A ROOFED appendage is a mass with a roof over it and must not let anyone in as a garden.
    # With it refused there is no outside at all, so the walk reports COULD NOT EVALUATE --
    # which is the honest verdict and NOT an empty `unreachable` standing for a pass.
    res = PC.check(_plan(roofed=True))
    assert "no-outside" in _kinds(res)
    assert "outside-is-only-an-appendage" not in _kinds(res)
    # nor one that is not at grade
    assert "no-outside" in _kinds(PC.check(_plan(at_grade=False)))
    # and an appendage that was REFUSED rather than placed mints no way in either
    pl = _plan()
    pl["appendages"] = {"placed": [], "unplaced": [{"room": "yard", "code": "no-door"}]}
    assert "no-outside" in _kinds(PC.check(pl))


def test_the_one_cause_of_twenty_seven_fatals_is_named_once_beside_them():
    """Seeding `outside` from a terrace clears one fatal on `tidewater-georgian-careful` and
    turns three COULD-NOT-EVALUATE verdicts into 27 `unreachable` fatals -- `good-02` 7,
    `good-04` 10, `good-07` 10 -- which is *unjudged is not passed* working, because those three
    plans have NO placed exterior door at all and the walk had nowhere to start. Every one of
    the 27 is true of the drawing. But ten fatals whose single cause is one missing front door
    is a report a reader has to reconstruct, so the cause gets its own line."""
    named = []
    for name, sol in _all():
        for f in PC.check(sol)["findings"]:
            if f.get("kind") == "outside-is-only-an-appendage":
                named.append(name)
    assert sorted(named) == ["good-02-portico-library-house.json",
                             "good-04-rambling-porch-farmhouse.json",
                             "good-07-diamond-plan-house.json"], named
    # AND THE NUMBER IS PINNED, because the report quotes it and a quoted number nothing holds
    # goes stale in silence. The first draft of that report said "26" -- the NET, one cleared
    # against twenty-seven created -- and published it as the number created. Both halves are
    # here so neither can be quoted for the other. `engine="heuristic"`, deterministic.
    per = {}
    for name, sol in _all():
        n = len([f for f in PC.check(sol)["findings"] if f.get("kind") == "unreachable"])
        if n:
            per[name] = n
    assert per["good-02-portico-library-house.json"] == 7
    assert per["good-04-rambling-porch-farmhouse.json"] == 10
    assert per["good-07-diamond-plan-house.json"] == 10
    assert per["tidewater-georgian-careful.json"] == 8, (
        "9 before the package; the one cleared is `breakfast`, and it was cleared by the "
        "reachability ruling and NOT by seating the terrace door -- its kitchen door is "
        "still refused for want of a shared wall")
    # and NOT on the Tidewater plan, which has a placed front door as well
    sol = _solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))
    assert not [f for f in PC.check(sol)["findings"]
                if f.get("kind") == "outside-is-only-an-appendage"]


# --------------------------------------------------------------- the disclosure

def test_the_ground_an_appendage_covers_is_beside_the_built_extent_and_not_in_it():
    """WP-11.9 ruling 2 put the lot cap on the BUILT EXTENT, elements only. An at-grade
    appendage is not an element, so it does not enter that figure -- and a terrace fourteen
    feet past the east wall while `fits_lot` reads green is the OQ 52 family wearing the
    safe-looking sign. Two questions, two numbers."""
    sol = _solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))
    row = sol["geometry_report"]["lot_extent"]
    assert row["built_extent_width_ft"] == 60.0
    ag = row["at_grade"]
    assert ag["appendages"] == 1 and ag["in_the_built_extent"] is False
    assert ag["covered_width_ft"] == 74.0, "the terrace's 14 ft is not in the covered figure"
    # and a plan with no appendage carries no such row
    sol2 = _solved(str(ROOT / "plans" / "spec-builder-colonial.json"))
    assert "at_grade" not in sol2["geometry_report"]["lot_extent"]


# --------------------------------------------------------------- the drawing

def test_both_renderers_read_the_record_and_derive_nothing():
    py = (ROOT / "build" / "render_plan.py").read_text()
    js = (ROOT / "workbench" / "app" / "src" / "sheet" / "Sheet.jsx").read_text()
    assert py.count("def appendage_rects(plan):") == 1
    assert 'out = appendage_rects(plan)' in py, "the plate is not sized to hold the appendage"
    assert 'data-appendage=' in py and 'data-appendage={ap.room}' in js
    # AND BOTH TAKE THE APPENDAGE INTO THE DOOR LOOKUP, in the same argument position. Without
    # it, `derive_openings`/`doors` find no room for a door the record says is SEATED and report
    # it undrawable: the record and the sheet holding two answers about one door.
    dj = (ROOT / "workbench" / "app" / "src" / "sheet" / "derive.js").read_text()
    # WP-11.14 RE-CUT THESE TWO FROM WHOLE SIGNATURE STRINGS TO THE PROPERTY THEY MEAN. They
    # pinned `"def derive_openings(rooms, W, H, tol=0.6, appendages=None):"` and its JS twin
    # verbatim, so adding an argument AFTER `appendages` -- which is what WP-11.14 did, to teach
    # the drawing about massing elements -- broke a guard that has nothing to do with elements.
    # The property is that both take `appendages` at the same ORDINAL, which is what "the same
    # argument position" in the comment above says. Third instance of a guard reading a literal
    # rather than a property in two packages; the others are named in CLAUDE.md.
    import inspect
    RP = _mod("render_plan")
    py_params = list(inspect.signature(RP.derive_openings).parameters)
    assert py_params[:4] == ["rooms", "W", "H", "tol"] and py_params[4] == "appendages", (
        f"derive_openings takes {py_params}; `appendages` must stay the fifth")
    m = re.search(r"export function doors\(([^)]*)\)", dj)
    assert m, "derive.js no longer exports doors()"
    js_params = [q.split("=")[0].strip() for q in m.group(1).split(",")]
    assert js_params[:4] == ["rooms", "W", "H", "tol"] and js_params[4] == "appendages", (
        f"doors() takes {js_params}; the two renderers disagree about the argument order")
    assert "for (const a of appendages || []) if (!idx.has(a.id)) idx.set(a.id, a);" in dj
    assert "const drs = doors(rooms, W, H, 0.6, appendages.map((a) => ({" in js
    # Neither renderer may decide a face or a size: those are the record's. Scoped to the
    # appendage block in each file rather than to the whole of it -- `render_plan.py` reads
    # `exterior_walls` legitimately for the openings it derives, and a whole-file assertion
    # here would have been a guard that could only ever have been deleted.
    py_block = py[py.index("def appendage_rects(plan):"):py.index("def threshold_rects(plan):")]
    py_draw = py[py.index('data-appendage="'):]
    py_draw = py_draw[:py_draw.index("for st in ((plan.get(\"threshold\")")]
    js_block = js[js.index("{appendages.map((ap, i) => ("):]
    js_block = js_block[:js_block.index("{levelIndex === 0 && ((placement?.threshold?.steps)")]
    for src, where in ((py_block, "render_plan.appendage_rects"), (py_draw, "render_plan draw"),
                       (js_block, "Sheet.jsx")):
        for banned in ("exterior_walls", "OPPOSITE", "width_ft / 2 +"):
            assert banned not in src, f"{where} is deriving what the record already states"
    assert 'const appendages = ((placement?.appendages?.placed) || [])' in js
    assert '.filter((a) => (a.level ?? 0) === levelIndex);' in js, (
        "the JS draws every appendage on every plate")
    assert "...appendages.map((a) => a.rect)," in js, "the JS plate is not sized for it"


def test_derive_openings_draws_a_door_to_an_appendage_and_refuses_it_without_one():
    """THE DEFECT THIS BRANCH REMOVES, AND IT WAS FOUND BY LOOKING AT THE SHEET. The pass seated
    `family`→`terrace` on `good-02` and the plate went on printing it under *"6 DECLARED DOOR(S)
    WITHOUT A DRAWABLE OPENING … FAMILY–TERRACE"* — because `derive_openings` builds its lookup
    from rooms carrying `geometry`, and an appendage's room deliberately carries none. The record
    said seated and the drawing said undrawable: two records of one door, WP-6.1's own finding.

    HAND-BUILT rather than driven off `tests/fixtures/sheet_symbols/`, and the reason is on the
    record: that fixture predates this pass, and its own README says regenerating it re-solves the
    placement — eight hundred lines of solver noise for a branch two rectangles prove.
    `workbench/app/src/derive.test.mjs` carries the same numbers on the JavaScript side."""
    RP = _mod("render_plan")
    rooms = [{"id": "kit", "type": "kitchen", "name": "Kitchen", "exterior_walls": ["E"],
              "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 20, "depth_ft": 20, "area_sf": 400},
              "doors": [{"to": "yard", "width_ft": 3, "wall": "E", "position_ft": 10}]}]
    yard = {"yard": {"x_ft": 20, "y_ft": 4, "width_ft": 12, "depth_ft": 12}}

    without = RP.derive_openings(rooms, 20, 20)
    assert without["interior"] == []
    assert [u["reason"] for u in without["undrawable"]] == [
        "the other room is not placed on this level"]

    got = RP.derive_openings(rooms, 20, 20, appendages=yard)
    assert got["undrawable"] == []
    assert len(got["interior"]) == 1
    d = got["interior"][0]
    assert d["horiz"] is False and d["at_ft"] == 20 and d["pos_ft"] == 10.0
    assert d["swing_positive"] is True, "the swing reads the appendage rectangle"
    # and the shipped plates say it: the two plans whose terrace door was refused report one
    # fewer undrawable door than they did, and neither names the terrace any more
    for pf, n in ((ROOT / "plans" / "tidewater-georgian-careful.json", 13),
                  (ROOT / "plans" / "reference" / "good-02-portico-library-house.json", 5)):
        sol = _solved(str(pf))
        fp = sol["footprint"]
        apx = {}
        for a in sol["appendages"]["placed"]:
            apx.setdefault(a.get("level", 0), {})[a["room"]] = a["rect"]
        und = []
        for i, lv in enumerate(sol["levels"]):
            if not any(r.get("geometry") for r in lv["rooms"]):
                continue
            und += RP.derive_openings(lv["rooms"], fp["width_ft"], fp["depth_ft"],
                                      appendages=apx.get(lv.get("index", i)))["undrawable"]
        assert len(und) == n, [f'{u["from"]}-{u["to"]}' for u in und]
        assert not [u for u in und if "terrace" in (u["from"], u["to"])]


def test_the_appendage_is_drawn_open_and_not_as_a_mass():
    """An at-grade appendage is a FLOOR: the paper is the terrace, exactly as the paper is
    every room. Giving it the wall's body would say the house is that shape, which is the one
    thing `rooms/terrace.json`'s own note is at pains to deny."""
    RP = _mod("render_plan")
    sol = _solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))
    out = ROOT / "tests" / "_tmp_appendage.svg"
    try:
        RP.render(sol, str(out))
        svg = out.read_text()
    finally:
        out.unlink(missing_ok=True)
    assert svg.count('data-appendage="terrace"') == 1
    assert svg.count('<rect class="ap"') == 1
    assert ">TERRACE<" in svg, "the appendage is drawn without its name"
    # `.ap` is the fine pen with no fill -- not poché, which is what `.st` (the stoop) takes
    style = svg[svg.index("<style>"):svg.index("</style>")]
    ap = [ln for ln in style.split("}") if ".ap{" in ln][0]
    assert "fill:none" in ap and "poche" not in ap.lower()
    assert "var(--lw" not in ap


def test_the_appendage_rect_is_inside_the_drawn_plate():
    """WP-11.4's own lesson: a thing outside the block that the plate was not sized for
    leaves the sheet with no error anywhere."""
    import re
    RP = _mod("render_plan")
    sol = _solved(str(ROOT / "plans" / "tidewater-georgian-careful.json"))
    rects = RP.appendage_rects(sol)
    assert len(rects) == 1 and rects[0]["x_ft"] == 60.0 and rects[0]["width_ft"] == 14.0
    assert rects[0]["area_sf"] == round(rects[0]["width_ft"] * rects[0]["depth_ft"])
    # AND THE DRAWN MARK IS ON THE PLATE, which is the question `appendage_rects` exists to
    # answer. Reading the function's return would pass with the call removed from `_pts`.
    out = ROOT / "tests" / "_tmp_appendage_plate.svg"
    try:
        RP.render(sol, str(out))
        svg = out.read_text()
    finally:
        out.unlink(missing_ok=True)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    m = re.search(r'<rect class="ap" x="([-0-9.]+)" y="([-0-9.]+)" '
                  r'width="([0-9.]+)" height="([0-9.]+)"', svg)
    assert m, "the appendage is not drawn"
    x, y, w, h = (float(g) for g in m.groups())
    assert vb[0] <= x and x + w <= vb[0] + vb[2] + 0.6, (
        f"the terrace runs off the plate: {x}+{w} against a viewBox of {vb}")
    assert vb[1] <= y and y + h <= vb[1] + vb[3] + 0.6
    # AND THE PLATE'S OWN SCHEDULE SAYS THE TERRACE DOOR IS DRAWN. `render()` has to hand the
    # appendages to `derive_openings`, and a test reading only `derive_openings` passes with that
    # call site reverted — measured, on the first mutation pass.
    line = re.search(r">(\d+) DECLARED DOOR\(S\) WITHOUT A DRAWABLE OPENING", svg)
    assert line and line.group(1) == "13", (
        "the schedule reports a different number of undrawable doors than the record does")
    tail = svg.split("DRAWABLE OPENING", 1)[1][:600]
    assert "TERRACE" not in tail, "the plate still calls the placed terrace door undrawable"


# --------------------------------------------------------------- the guarantee

CORPUS_PLACEMENT_SHA = "151126d0269bbc61"


def test_placing_the_terrace_moved_no_shipped_placement():
    """THE GUARANTEE. Measured on a `git archive HEAD` checkout before the package and on the
    working tree after it. The appendage pass runs inside `openings.place()`, which runs after
    both engines have finished, and it writes nothing to a room -- so a movement here is a
    defect and not a trade. `tests/test_elements.py` carries the same pin and the openings one
    beside it, which this package moves on purpose."""
    h = hashlib.sha256()
    for pf in _plans():
        d = json.loads(pathlib.Path(pf).read_text())
        if "levels" not in d:
            continue
        sol = _solved(pf)
        geo = [(lv.get("index"), r["id"], r.get("geometry"))
               for lv in sol["levels"] for r in lv["rooms"]]
        h.update(json.dumps(geo, sort_keys=True).encode())
        h.update(json.dumps(sol.get("footprint"), sort_keys=True).encode())
    assert h.hexdigest()[:16] == CORPUS_PLACEMENT_SHA


def test_every_definition_this_package_added_landed_once():
    """WP-11.9 left TWO `def multi_element_disclosure`s in one file, new above old, and Python
    took the last: the record went on carrying the old text under the new docstring while the
    edit had unambiguously landed. Assert that an edit landed, and assert it landed ONCE."""
    for fn, src in (("appendage_pass", (ROOT / "build" / "appendages.py").read_text()),
                    ("served_face", (ROOT / "build" / "appendages.py").read_text()),
                    ("appendage_rects", (ROOT / "build" / "render_plan.py").read_text()),
                    ("_disclose_at_grade", (ROOT / "build" / "geometry.py").read_text())):
        assert src.count(f"def {fn}(") == 1, f"{fn} is defined more than once"
    js = (ROOT / "workbench" / "app" / "src" / "sheet" / "Sheet.jsx").read_text()
    assert js.count("const appendages =") == 1
