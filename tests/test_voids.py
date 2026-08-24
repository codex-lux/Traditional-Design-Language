"""OQ 33 -- reserved voids.

Ruled 24 Aug 2026: both placement engines carry outdoor rooms as placed, dimensioned voids,
excluded from the area budget and the heated envelope, drawn open. Before the ruling every
outdoor room was dropped before placement, so a courtyard house composed, scored, placed and
rendered as a solid block with rooms packed where the court should be -- the drawing showing a
house the record does not describe.

These pin the pieces that make the ruling true rather than merely intended: that the void takes
a rectangle, that the rectangle is enclosed on a courtyard massing, that nothing sits over one
that is open to the sky, that the heated area is stated separately from the block, that the
walls facing an open court are exterior, and that a terrace -- which is appended at grade and
NOT within the block -- still stays out of placement, because for a terrace that is the right
answer rather than a limitation.
"""
import copy
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def court_plan():
    """A courtyard plan, composed from the parti rather than hand-written, so this tests what
    the composer actually hands the geometry engine."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import compose
    brief = {"id": "t", "name": "Courtyard test", "style": "spanish-colonial-revival",
             "target_area_sf": 3000, "bedrooms": 3, "bathrooms": 2.5,
             "context": {"climate_zone": "3B", "lot_width_ft": 140, "entrance_faces": "S",
                         "jurisdiction": "IRC model text, advisory", "budget_tier": "custom"},
             "household": "Two adults, two children.", "candidates": 3}
    out = compose.compose(brief) if hasattr(compose, "compose") else None
    assert out is not None, "compose.py no longer exposes compose(); update this fixture"
    cand = next(c for c in out["candidates"] if c["parti"] == "courtyard-and-portal")
    return cand["plan"]


# ---------------------------------------------------------------- the room data


def test_the_four_outdoor_rooms_each_declare_what_kind_of_void_they_are():
    """within_footprint and roofed are independent facts and both are needed to place one: the
    first decides whether it takes a rectangle in the block, the second whether anything may
    sit above it."""
    want = {"courtyard": (True, False), "loggia": (True, True),
            "piazza": (True, True), "terrace": (False, False)}
    for rid, (within, roofed) in want.items():
        d = json.load(open(os.path.join(ROOT, "rooms", "%s.json" % rid)))
        assert d["function_class"] == "outdoor", rid
        v = d.get("void")
        assert v, "%s carries no void block" % rid
        assert v["within_footprint"] is within, rid
        assert v["roofed"] is roofed, rid
        assert v.get("note"), "%s's void block states no reason" % rid


def test_a_room_with_no_void_block_is_not_promoted_into_the_footprint(geometry_module):
    """The default is the pre-ruling behaviour. A room nobody has judged must not be silently
    placed -- unjudged is not passed, here as everywhere else."""
    assert geometry_module.void_spec("terrace") is None
    assert geometry_module.void_spec("kitchen") is None
    assert geometry_module.void_spec("courtyard") is not None
    assert geometry_module.is_placed("courtyard") is True
    assert geometry_module.is_placed("terrace") is False


def test_the_terrace_on_the_tidewater_plan_is_still_not_placed(geometry_module):
    """The reference plan that has a terrace: it is appended at grade, the block is the same
    shape without it, and it stays out. Nothing about this plan moved."""
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    out = geometry_module.solve(copy.deepcopy(plan))
    terrace = next(r for r in out["levels"][0]["rooms"] if r["type"] == "terrace")
    assert "geometry" not in terrace
    assert out["geometry_report"]["voids"]["count"] == 0
    assert "void_area_sf" not in out["footprint"]


# ---------------------------------------------------------------- placement


def test_the_court_is_placed_and_the_heated_area_is_stated_apart_from_the_block(geometry_module, court_plan):
    out = geometry_module.solve(copy.deepcopy(court_plan),
                                json.load(open(os.path.join(ROOT, "partis", "courtyard-and-portal.json"))))
    court = next(r for r in out["levels"][0]["rooms"] if r["type"] == "courtyard")
    assert "geometry" in court, "the court was not placed"
    assert court["geometry"]["void"] == {"heated": False, "roofed": False}
    fp = out["footprint"]
    assert fp["void_area_sf"] > 0
    assert fp["heated_area_sf"] == fp["area_sf"] - fp["void_area_sf"]
    assert fp["heated_area_sf"] < fp["area_sf"], "the block must be larger than what it heats"


def test_the_court_is_enclosed_not_a_notch_in_the_corner(geometry_module, court_plan):
    """The first drawing the ruling produced put the court in the block's SW corner against two
    exterior walls. That is the right area in the right block and it is not a courtyard --
    rooms/courtyard.json's own first sentence is that the room is defined by what encloses it.
    Four thousand candidates of the ordinary slicer never fixed it, which is why
    courtyard_slice() states the ring as a guillotine tree instead of searching for one."""
    out = geometry_module.solve(copy.deepcopy(court_plan),
                                json.load(open(os.path.join(ROOT, "partis", "courtyard-and-portal.json"))))
    fp, g = out["footprint"], next(r for r in out["levels"][0]["rooms"]
                                   if r["type"] == "courtyard")["geometry"]
    W, H = fp["width_ft"], fp["depth_ft"]
    assert g["x_ft"] > 0.6, "court reaches the west wall"
    assert g["y_ft"] > 0.6, "court reaches the south wall"
    assert g["x_ft"] + g["width_ft"] < W - 0.6, "court reaches the east wall"
    assert g["y_ft"] + g["depth_ft"] < H - 0.6, "court reaches the north wall"
    assert out["geometry_report"]["voids"]["ring_layout"]["used"] > 0


def test_the_courts_proportion_lands_in_its_own_catalogue_band(geometry_module, court_plan):
    """rooms/courtyard.json calls the court's proportion the number the whole diagram turns on
    and bands it 1.0-2.2. The bay count is chosen against that band, because the growth loops
    are written for a block that holds rooms and left alone they made the court a 16 x 40 slot:
    in band for area, out of band for the one ratio that matters."""
    out = geometry_module.solve(copy.deepcopy(court_plan),
                                json.load(open(os.path.join(ROOT, "partis", "courtyard-and-portal.json"))))
    g = next(r for r in out["levels"][0]["rooms"] if r["type"] == "courtyard")["geometry"]
    ar = max(g["width_ft"], g["depth_ft"]) / min(g["width_ft"], g["depth_ft"])
    lo, hi = json.load(open(os.path.join(ROOT, "rooms", "courtyard.json")))["dimensions"]["proportion"]
    assert lo - 0.05 <= ar <= hi + 0.05, "court aspect %.2f outside the room's own %s band" % (ar, [lo, hi])


def test_ring_depth_refuses_a_block_that_cannot_hold_the_court(geometry_module):
    """A real answer, not a fallback dressed as one: when the discriminant goes negative or the
    ranges come out too shallow to be rooms, ring_depth returns None and the caller draws the
    ordinary way and says so in the report."""
    assert geometry_module.ring_depth(40, 30, 5000) is None      # court larger than the block
    assert geometry_module.ring_depth(40, 30, 1150) is None      # ranges under 7 ft deep
    d = geometry_module.ring_depth(55, 54, 650)
    assert d is not None and 7.0 < d < 20.0


# ---------------------------------------------------------------- nothing over an open void


def test_nothing_may_sit_over_a_void_open_to_the_sky(geometry_module):
    """A room over a court has no floor under it and the roof it needs is the hole. Charged 40
    -- an order above the 12 a room under its band pays -- and named in the report."""
    prep = {0: [{"id": "court", "type": "courtyard", "name": "Patio", "_area": 400,
                 "_void": {"within_footprint": True, "roofed": False}},
                {"id": "sala", "type": "living-room", "name": "Sala", "_area": 400, "_void": False}],
            1: [{"id": "chamber", "type": "bedroom", "name": "Chamber", "_area": 200, "_void": False}]}
    g = {"court": (0, 0, 20, 20), "sala": (20, 0, 20, 20)}
    over = {"chamber": (2, 2, 14, 14)}
    clear = {"chamber": (22, 2, 14, 14)}
    s_over, notes = geometry_module.vertical_score(g, over, prep[0], prep[1], {})
    s_clear, _ = geometry_module.vertical_score(g, clear, prep[0], prep[1], {})
    assert s_over - s_clear >= 40
    assert any("open to the sky" in n for n in notes)


def test_a_roofed_void_will_carry_an_upper_storey(geometry_module):
    """The reason `roofed` is a separate fact: a Charleston single's upper piazza sits on its
    lower one, and charging that would be the check misfiring on the case it was written for."""
    prep0 = [{"id": "piazza", "type": "piazza", "name": "Piazza", "_area": 400,
              "_void": {"within_footprint": True, "roofed": True}}]
    prep1 = [{"id": "upperpiazza", "type": "piazza", "name": "Upper Piazza", "_area": 400,
              "_void": {"within_footprint": True, "roofed": True}}]
    g = {"piazza": (0, 0, 20, 20)}
    u = {"upperpiazza": (0, 0, 20, 20)}
    s, notes = geometry_module.vertical_score(g, u, prep0, prep1, {})
    assert not any("open to the sky" in n for n in notes)


# ---------------------------------------------------------------- downstream passes


def test_a_wall_facing_an_open_court_is_an_exterior_wall(structure_module):
    """The structural point of a courtyard house, and it was invisible while the court was not
    placed: the wall between a room and the court is weather-facing, on the thermal envelope,
    and bearing. Calling it an interior partition would put the court inside the envelope."""
    rooms = [
        {"id": "court", "type": "courtyard",
         "geometry": {"x_ft": 10, "y_ft": 0, "width_ft": 20, "depth_ft": 20, "area_sf": 400,
                      "void": {"heated": False, "roofed": False}}},
        {"id": "sala", "type": "living-room",
         "geometry": {"x_ft": 30, "y_ft": 0, "width_ft": 10, "depth_ft": 20, "area_sf": 200}},
        {"id": "comedor", "type": "dining-room",
         "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 10, "depth_ft": 20, "area_sf": 200}},
    ]
    walls = structure_module.wall_lines(rooms, 40, 20)
    court_walls = [w for w in walls if w.get("wall") == "court"]
    assert len(court_walls) == 2, [w.get("wall") for w in walls]
    assert all(w["role"] == "exterior" for w in court_walls)
    bearing = structure_module.bearing_lines(walls, 10.0)
    assert all(w["bearing"] for w in bearing if w.get("wall") == "court")


def test_the_roof_pass_records_the_hole_rather_than_spanning_it_silently(roof_module):
    """This file computes ONE ridge over one rectangle. Over a court it does not. The opening's
    dimensions go into the record so nobody reads the single-ridge figures as a complete
    description of the roof."""
    plan = {"levels": [{"index": 0, "rooms": [
        {"id": "court", "name": "Patio",
         "geometry": {"x_ft": 10, "y_ft": 10, "width_ft": 20, "depth_ft": 20, "area_sf": 400,
                      "void": {"heated": False, "roofed": False}}},
        {"id": "walk", "name": "Corredor",
         "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 10, "depth_ft": 10, "area_sf": 100,
                      "void": {"heated": False, "roofed": True}}},
    ]}]}
    op = roof_module._roof_openings(plan)
    assert op["count"] == 1 and op["rooms"][0]["room"] == "court"
    assert "SCHEMATIC" in op["note"]
    assert roof_module._roof_openings({"levels": []})["count"] == 0


def test_the_drawing_shows_the_court_open(geometry_module, court_plan, tmp_path):
    """The drawing is a render of the data (decision #11). A court drawn as a dark room is the
    picture disagreeing with the record it is supposed to be a view of."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import render_plan
    out = geometry_module.solve(copy.deepcopy(court_plan),
                                json.load(open(os.path.join(ROOT, "partis", "courtyard-and-portal.json"))))
    path = tmp_path / "court.svg"
    render_plan.render(out, str(path))
    svg = path.read_text()
    assert 'url(#openvoid)' in svg, "the court is not hatched open"
    assert "open to sky" in svg
    assert "roofed, unheated" in svg
    import xml.dom.minidom
    xml.dom.minidom.parseString(svg)          # and it is still well-formed SVG


# ---------------------------------------------------------------- the constraint solver


def test_the_solver_states_the_open_void_as_a_constraint_not_a_preference():
    """geometry.py charges 40 points and can still buy its way out; solver.py cannot. A room
    over a court is not a preference the optimiser may trade against anything."""
    pytest.importorskip("ortools")
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import solver
    prep = {0: [{"id": "court", "type": "courtyard", "name": "Patio", "_area": 400,
                 "_void": {"within_footprint": True, "roofed": False}}],
            1: [{"id": "chamber", "type": "bedroom", "name": "Chamber", "_area": 200,
                 "_void": False}]}
    ground = {"court": (0.0, 0.0, 20.0, 20.0)}
    upper = {"chamber": (2.0, 2.0, 14.0, 14.0)}
    unmet = solver.unmet_requirements(ground, upper, prep, {"levels": []}, 40.0, 20.0)
    assert "open-void:chamber~court" in unmet
    clear = solver.unmet_requirements(ground, {"chamber": (22.0, 2.0, 14.0, 14.0)},
                                      prep, {"levels": []}, 40.0, 20.0)
    assert not any(u.startswith("open-void") for u in clear)


def test_the_conflict_prose_can_say_what_an_open_void_requirement_means():
    """Making a rule executable adds a test; it does not replace the statement."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import solver
    assert "open-void" in solver._KIND_PROSE
    assert "open to the sky" in solver._KIND_PROSE["open-void"]


def test_both_engines_report_the_reservation_the_same_way(geometry_module):
    """The drawing is a render of the data, and two engines describing one court two different
    ways would put that guarantee back in doubt -- so the report is built once and shared."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import solver
    # Not an identity check: build/ loads siblings by path through modcache, so solver.GEO and
    # a plain `import geometry` are two module objects of the same file. What matters is that
    # solver.py holds no second implementation and calls geometry.py's.
    assert not hasattr(solver, "voids_report")
    src = open(os.path.join(ROOT, "build", "solver.py")).read()
    assert "def voids_report" not in src
    assert "GEO.voids_report(" in src
    assert solver.GEO.voids_report.__code__.co_filename == geometry_module.voids_report.__code__.co_filename
    empty = geometry_module.voids_report({0: {}}, {0: []})
    assert empty["count"] == 0 and empty["ring_layout"] is None


# ---------------------------------------------------------------- OQ 39, the portal ring


def test_the_portal_is_four_records_one_per_range():
    """A continuous roofed walk around four sides of a court cannot be one rectangle. It was
    one, so the engines placed it along one side and the other three ranges were entered from
    nothing -- and the validator missed it, because the door graph was satisfied by the record
    and plan_check.py never reads room.geometry."""
    d = json.load(open(os.path.join(ROOT, "partis", "courtyard-and-portal.json")))
    walks = [r for r in d["rooms"] if r["type"] == "loggia"]
    assert [w["id"] for w in walks] == ["walk-s", "walk-w", "walk-e", "walk-n"], \
        "the four walks must be listed in geometry.py's own band order S W E N"
    for w in walks:                      # the ring is continuous
        assert sum(1 for x in w["doors"] if x.startswith("walk-")) == 2, w["id"]
        assert "court" in w["doors"]
    served = {t for w in walks for t in w["doors"] if not t.startswith("walk-") and t != "court"}
    others = {r["id"] for r in d["rooms"] if r["type"] not in ("loggia", "courtyard")}
    # every room either opens off a range, or off a room that does (a larder off its kitchen)
    reach = set(served)
    for _ in range(3):
        for r in d["rooms"]:
            if r["id"] in reach: continue
            if any(t in reach for t in (r.get("doors") or [])): reach.add(r["id"])
    assert others <= reach, others - reach


def test_every_range_is_served_by_its_own_walk(geometry_module, court_plan):
    """The placement each range assignment produces: four walks, one per band, and the rooms
    that door to each sitting in that band rather than wherever the area happened to fall."""
    out = geometry_module.solve(copy.deepcopy(court_plan),
                                json.load(open(os.path.join(ROOT, "partis", "courtyard-and-portal.json"))))
    rects = {r["id"]: r["geometry"] for r in out["levels"][0]["rooms"] if r.get("geometry")}
    for wid in ("walk-s", "walk-w", "walk-e", "walk-n"):
        assert wid in rects, wid
        assert rects[wid]["void"] == {"heated": False, "roofed": True}
    # each walk touches the court
    court = rects["court"]
    for wid in ("walk-s", "walk-w", "walk-e", "walk-n"):
        w = rects[wid]
        ox = min(w["x_ft"] + w["width_ft"], court["x_ft"] + court["width_ft"]) - max(w["x_ft"], court["x_ft"])
        oy = min(w["y_ft"] + w["depth_ft"], court["y_ft"] + court["depth_ft"]) - max(w["y_ft"], court["y_ft"])
        assert ox > -0.5 and oy > -0.5, "%s does not reach the court" % wid


def test_the_range_assignment_reads_doors_to_a_walk_before_doors_to_a_neighbour(geometry_module):
    """The bug this ordering fixes: assigning rooms in one pass let a room inherit a range from
    a sibling assigned earlier in the same pass, which put the kitchen in the street range
    because it happened to list the dining room before its own corredor."""
    def room(rid, area, doors, void=False):
        # doors on a PLAN record are {"to": id} dicts; in a parti file they are bare strings
        return {"id": rid, "type": "loggia" if void else "kitchen", "name": rid, "_area": area,
                "doors": [{"to": x} for x in doors],
                "_void": ({"within_footprint": True, "roofed": True} if void else False)}
    ring = [room("w0", 90, ["court"], True), room("w1", 90, ["court"], True),
            room("w2", 90, ["court"], True), room("w3", 90, ["court"], True),
            room("dining", 200, ["w0"]), room("kitchen", 200, ["dining", "w1"]),
            room("larder", 80, ["kitchen"]),
            room("a", 200, ["w2"]), room("b", 200, ["w3"])]
    court = {"id": "court", "type": "courtyard", "name": "court", "_area": 500, "doors": [],
             "_void": {"within_footprint": True, "roofed": False}}
    out, relax = {}, []
    import random
    ok = geometry_module.courtyard_slice([court] + ring, 56.0, 56.0, 8.0, 2.0,
                                         random.Random(3), out, relax, 4)
    assert ok
    # the kitchen sits in w1's band, not w0's -- measured by which walk it touches
    def touch(a, b):
        ax, ay, aw, ah = out[a]; bx, by, bw, bh = out[b]
        return (min(ax + aw, bx + bw) - max(ax, bx) > -0.6
                and min(ay + ah, by + bh) - max(ay, by) > -0.6)
    assert touch("kitchen", "w1")
    assert touch("larder", "kitchen")


# ---------------------------------------------------------------- the brief's target


def test_the_briefs_target_is_heated_area_not_the_block():
    """instantiate() scaled every room against the target, outdoor rooms included, while
    reclaim() measured area with outdoor rooms excluded: two passes sizing against two different
    quantities, only one of them the brief's. Invisible on a plan with no placed void. On the
    courtyard parti, whose court and corredor are a third of the block, a 3,000 sf brief came
    back as an 1,834 sf house that the composer reported as 38.9% off and could not fix."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import compose
    brief = {"id": "t", "name": "t", "style": "spanish-colonial-revival", "target_area_sf": 3000,
             "bedrooms": 3, "bathrooms": 2.5,
             "context": {"climate_zone": "3B", "lot_width_ft": 140, "entrance_faces": "S",
                         "jurisdiction": "IRC model text, advisory", "budget_tier": "custom"},
             "household": "x"}
    plan, log, parti = compose.instantiate("courtyard-and-portal", brief)
    heated = sum(r["width_ft"] * r["length_ft"] for lv in plan["levels"] for r in lv["rooms"]
                 if compose.C["rooms"].get(r["type"], {}).get("function_class") != "outdoor")
    assert abs(heated - 3000) / 3000 < 0.20, heated
    void = sum(r["width_ft"] * r["length_ft"] for lv in plan["levels"] for r in lv["rooms"]
               if compose.C["rooms"].get(r["type"], {}).get("function_class") == "outdoor")
    assert void > 0, "the voids should still be sized, just not out of the brief's budget"
