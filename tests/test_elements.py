"""WP-11.9 — the six layers that read the main block as the whole building.

`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` measured six of them,
each wrong in its own direction on a dependency room. Lucas ruled the four questions that
package was gated on, on 5 September 2026:

  1. per-element envelope, union reported beside it
  2. the lot cap is on the BUILT EXTENT, elements only, gap excluded
  3. a hyphen is an element, and abutment becomes a constraint
  4. `touches` is measured against the room's own element's face -- exterior is exterior

**THE GUARANTEE THIS FILE EXISTS TO HOLD IS BYTE-IDENTITY.** Every plan in this corpus is one
rectangle, so every one of the six changes must be invisible on all sixteen -- the placement,
the footprint, the openings, the fixtures and the furniture. A package that teaches six layers
a new concept and moves a shipped placement has done two things and can only be reasoned about
as one.
"""
import glob
import hashlib
import json
import os
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, ROOT / "build" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


E = _mod("elements")
G = _mod("geometry")


def _plans():
    return (sorted(glob.glob(str(ROOT / "plans" / "*.json")))
            + sorted(glob.glob(str(ROOT / "plans" / "reference" / "*.json"))))


def _solved(pid):
    d = json.loads((ROOT / "plans" / f"{pid}.json").read_text())
    G._SOLVE_CACHE.clear()
    return G.solve(json.loads(json.dumps(d)), engine="heuristic")


# --------------------------------------------------------------- the reader itself

def test_every_shipped_plan_is_one_element_and_every_placed_room_is_in_it():
    """The premise the whole package rests on. If a shipped plan ever grows a second element,
    every byte-identity assertion below stops meaning what it says, and this fails first."""
    for pf in _plans():
        d = json.loads(pathlib.Path(pf).read_text())
        if "levels" not in d:
            continue
        G._SOLVE_CACHE.clear()
        sol = G.solve(json.loads(json.dumps(d)), engine="heuristic")
        els = E.elements(sol)
        assert len(els) == 1, (pf, [e["id"] for e in els])
        rooms = [r for lv in sol["levels"] for r in lv["rooms"] if r.get("geometry")]
        idx = E.bounds_index(sol, rooms)
        assert len(idx) == len(rooms), (
            f"{pf}: {len(rooms) - len(idx)} placed room(s) stand in no element, which this "
            f"layer reports as COULD NOT EVALUATE -- on a one-rectangle house that is a bug "
            f"in the containment test, not a fact about the plan")


def test_a_room_in_no_element_is_unjudged_and_not_assigned_to_the_main_block():
    """The rule the file's own header states: defaulting a straddling room to element zero is
    exactly the defect the package removes, so `element_of` must answer None."""
    plan = {"footprint": {"blocks": [
        {"id": "main", "role": "main", "x_ft": 0, "y_ft": 0, "width_ft": 40, "depth_ft": 40},
        {"id": "dep", "role": "dependency", "x_ft": 50, "y_ft": 0, "width_ft": 20,
         "depth_ft": 20, "attached_to": "main"}]}}
    straddler = {"id": "x", "geometry": {"x_ft": 30, "y_ft": 0, "width_ft": 30, "depth_ft": 10}}
    assert E.element_of(plan, straddler) is None
    inside = {"id": "y", "geometry": {"x_ft": 52, "y_ft": 2, "width_ft": 10, "depth_ft": 10}}
    assert E.element_of(plan, inside)["id"] == "dep"


def test_the_built_extent_excludes_the_gap_and_the_union_bbox_does_not():
    """Ruling 2 in one assertion, and ruling 1's 'union reported beside it' in the same breath.
    A 40 ft house and a 22 ft garage 20 ft away build 62 ft and span 82."""
    plan = {"footprint": {"blocks": [
        {"id": "main", "role": "main", "x_ft": 0, "y_ft": 0, "width_ft": 40, "depth_ft": 30},
        {"id": "gar", "role": "dependency", "x_ft": 60, "y_ft": 0, "width_ft": 22,
         "depth_ft": 22, "attached_to": "main"}]}}
    assert E.extent_width_ft(plan) == 62.0
    assert E.union_bbox(plan) == (0.0, 0.0, 82.0, 30.0)
    # and a hyphen filling the gap makes the two agree, which is what makes a hyphen an element
    plan["footprint"]["blocks"].append(
        {"id": "hy", "role": "hyphen", "x_ft": 40, "y_ft": 5, "width_ft": 20, "depth_ft": 10,
         "attached_to": "main"})
    assert E.extent_width_ft(plan) == 82.0


def test_a_hyphen_that_fills_the_gap_is_not_a_gap():
    """Ruling 4 asked for the across-a-gap count to be kept separately, so it has to be right
    about what a gap is: a third element standing in the interval closes it."""
    els = [{"id": "a", "role": "main", "x": 0.0, "y": 0.0, "W": 40.0, "H": 40.0},
           {"id": "h", "role": "hyphen", "x": 40.0, "y": 10.0, "W": 10.0, "H": 20.0},
           {"id": "d", "role": "dependency", "x": 50.0, "y": 0.0, "W": 20.0, "H": 40.0}]
    assert E.faces_across_a_gap({}, els) == []
    assert E.faces_across_a_gap({}, [els[0], els[2]]), (
        "with the hyphen removed the same two elements DO look across open ground; if this is "
        "empty the gap test is not testing anything")


def test_the_abutment_detector_fires_and_is_silent_for_the_right_reasons():
    """Ruling 3. Mutation-proof in both directions in one test, because a detector that is
    silent on the whole corpus (as this one is -- see the next test) has to be shown to bite
    somewhere or it is a term that cannot fail."""
    els = [{"id": "main", "role": "main", "x": 0.0, "y": 0.0, "W": 40.0, "H": 40.0},
           {"id": "h", "role": "hyphen", "x": -8.0, "y": 0.0, "W": 8.0, "H": 40.0,
            "attached_to": "main"},
           {"id": "d", "role": "dependency", "x": -28.0, "y": 0.0, "W": 20.0, "H": 40.0,
            "attached_to": "main"}]
    owner = {"m1": "main", "hy": "h", "d1": "d"}
    missed = {"m1": (0.0, 20.0, 40.0, 20.0), "hy": (-8.0, 0.0, 8.0, 20.0),
              "d1": (-28.0, 20.0, 20.0, 20.0)}
    out = E.unabutted_hyphens(els, missed, owner)
    assert len(out) == 1 and out[0]["room"] == "hy"
    assert set(out[0]["unconnected"]) == {"main", "d"}
    joined = {"m1": (0.0, 0.0, 40.0, 40.0), "hy": (-8.0, 0.0, 8.0, 40.0),
              "d1": (-28.0, 0.0, 20.0, 40.0)}
    assert E.unabutted_hyphens(els, joined, owner) == []


def test_the_abutment_term_is_inert_on_what_the_placer_produces_and_that_is_the_finding():
    """MEASURED, and published as a refusal rather than a success.

    The open question records a hyphen missing its neighbour by 0.64 ft with both its doors
    unplaced. Reproducing it through `blocks_for` was tried on a hand-tagged Tidewater at five
    hyphen depths and on a composed five-part-palladian with TWO dependencies and two hyphens,
    and the count is zero every time -- because `blocks_for` clamps the hyphen's depth to the
    dependency's (`hh = min(H, ...)`) and centres all three elements on one axis, so the
    hyphen's y-range lies inside both neighbours', and the slicer tiles each element exactly.
    A shared wall therefore exists by construction.

    So the ranking term added to the search's first key is a GUARD against a regression in
    `blocks_for`, not a fix for a live defect, and the mutation confirms it: deleting the term
    changes no outcome on any fixture in the tree. Recorded here because a term that is inert
    and undocumented reads to the next author as a term that works.
    """
    plan = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())
    service = {"kitchen", "pantry", "breakfast", "butlers", "powder", "cellarstair"}
    for lv in plan["levels"]:
        if (lv.get("index") or 0) != 0:
            continue
        for r in lv["rooms"]:
            if r["id"] in service:
                r["block"] = "west-dependency"
            if r["id"] == "backhall":
                r["block"] = "west-dependency"
                r["hyphen"] = True
    G._SOLVE_CACHE.clear()
    sol = G.solve(json.loads(json.dumps(plan)), engine="heuristic")
    els = E.elements(sol)
    assert len(els) == 3, [e["id"] for e in els]
    ground = [r for lv in sol["levels"] if (lv.get("index") or 0) == 0 for r in lv["rooms"]]
    assert E.unabutted_hyphen_rooms(sol, els=els, level_rooms=ground) == []


# --------------------------------------------------------------- the six layers

def test_openings_reads_the_rooms_own_element_and_the_rule_lives_in_one_place():
    """Layer 1. `openings._boundary_walls` delegates rather than transcribing, because the
    drawn layer's `touches` tests ask the same question and ruling 4 makes it the same rule."""
    # RE-CUT AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026). Both branches taught this layer to
    # read the room's own element and each pinned ITS OWN SPELLING as a source string -- this
    # branch `_elem().boundary_walls(rect, bounds`, main `envelopes(plan)` with an `env=`
    # argument. The merge kept main's, because `plan_check` reuses that same map ("layer 1's own
    # map, not a second spelling of the block-tag join"). A guard reading a selector rather than
    # a property cannot survive the other branch arriving, which is this repository's own
    # most-repeated lesson, so what is asserted is the BEHAVIOUR: the boundary test is told which
    # element the room stands in, and there is exactly ONE reader of that fact.
    OP = _mod("openings")
    src = (ROOT / "build" / "openings.py").read_text()
    assert "envelopes(" in src, "openings no longer maps a room to its own element at all"
    # the property: a room's boundary walls are its ELEMENT's faces, not the footprint's
    rect = (-30.0, 5.0, 20.0, 20.0)
    own = OP._boundary_walls(rect, 60.0, 40.0, env=(-30.0, 5.0, -10.0, 25.0))
    blk = OP._boundary_walls(rect, 60.0, 40.0, env=None)
    assert own and {w[0] for w in own} == {"S", "N", "W", "E"}, (
        f"a room filling its own element stands on all four of ITS faces: {own}")
    assert {w[0] for w in own} != {w[0] for w in blk}, (
        "the element and the footprint must give different answers here, or this fixture "
        f"cannot tell the two apart: element={own} footprint={blk}")


def test_wall_lines_gives_every_element_its_own_envelope():
    """Layer 2. Four exterior walls per element, and NONE for an element with no rooms on this
    level -- a floor's worth of phantom structure is what the first version of that line made,
    12 exterior walls over 0 dependency rooms on the upper storey."""
    ST = _mod("structure")
    one = ST.wall_lines([], 60.0, 40.0)
    assert len([w for w in one if w["role"] == "exterior"]) == 4
    # RE-CUT AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026). Both branches gave every element
    # its own envelope and chose different APIs to do it: this branch passed an element LIST into
    # one call, main runs the function ONCE PER ELEMENT with that element's own origin and merges
    # -- which is the stronger form, because a span across the gap between two masses cannot be
    # computed at all rather than being filtered out afterwards. The merge keeps main's, so this
    # asserts the same property through it: two elements, eight exterior walls, each at its own
    # coordinates.
    ext = ([w for w in ST.wall_lines([], 60.0, 40.0, origin=(0.0, 0.0)) if w["role"] == "exterior"]
           + [w for w in ST.wall_lines([], 20.0, 20.0, origin=(-30.0, 5.0))
              if w["role"] == "exterior"])
    assert len(ext) == 8
    # the second element's own walls are at ITS coordinates, not the block's
    assert any(abs(w["position_ft"] - (-30.0)) < 1e-6 for w in ext)
    assert any(abs(w["position_ft"] - (-10.0)) < 1e-6 for w in ext)


def test_vertical_support_only_counts_ground_walls_under_the_upper_floor():
    """Layer 3, held on the source because the numbers it moves are only reachable on a
    multi-element record. A dependency wall 37 ft west of the house counted as support for an
    upper wall above the main block, where there is no upper floor at all."""
    src = (ROOT / "build" / "geometry.py").read_text()
    assert "under = {rid: v for rid, v in g.items()" in src, (
        "vertical_score reads every ground rect again")
    assert "gx, gy = wall_lines(under)" in src


def test_the_lot_cap_is_on_the_built_extent_and_the_report_says_so():
    """Layer 4, both halves. The main block is sized from its OWN rooms, and the extent is
    reported beside `lot_capped` -- which answers a different question and always did."""
    src = (ROOT / "build" / "geometry.py").read_text()
    assert ("flank_sizes(" in src or 'a0 = sum(r["_area"] for r in prep[0] if r not in _dep)' in src), (
        "the main block is sized for rooms that go in the dependency again")
    # MERGE (8 Sep 2026): this branch reserved the flank as `lot_usable - reserved`; main as
    # `lot_usable - flank` via `flanking_extent_ft`. Same quantity, main's spelling kept.
    assert ("lot_usable - flank" in src or "lot_usable - reserved" in src), (
        "the dependency is not reserved out of the lot")
    sol = _solved("tidewater-georgian-careful")
    row = sol["geometry_report"]["lot_extent"]
    assert row["elements"] == 1
    assert row["built_extent_width_ft"] == sol["footprint"]["width_ft"]
    assert row["fits_lot"] is True
    assert row["union_bbox_ft"][2] == sol["footprint"]["width_ft"]


def test_the_lot_extent_reports_could_not_evaluate_when_no_lot_is_stated():
    """Unjudged is not passed: a plan with no lot cannot be said to fit one."""
    sol = _solved("spec-builder-colonial")
    row = sol["geometry_report"]["lot_extent"]
    if row.get("lot_usable_width_ft") is None:
        assert row["fits_lot"] is None and "COULD NOT EVALUATE" in row["note"]
    else:
        assert row["fits_lot"] in (True, False)


def test_touches_is_measured_against_the_rooms_own_element():
    """Layer 5, ruling 4. Held on the source and on a two-element fixture, because on a
    one-rectangle house the two readings are the same by construction -- which is exactly why
    this went unnoticed."""
    src = (ROOT / "build" / "plan_check.py").read_text()
    # MERGE: main's `_envelope(rid)` reads `openings.envelopes()`; this branch read
    # `elements.bounds_index`. One question, main's spelling kept.
    assert ("_envelope(rid)" in src or "_ebounds.get(rid" in src)
    # MERGE: main's `_envelope(rid)` returns CORNERS (`ey0`), this branch's returned an origin
    # and a size (`_by`). Either way the face is the ELEMENT's and not the footprint's.
    assert ('if abs(g["y_ft"] - ey0) < 0.6' in src
            or 'if abs(g["y_ft"] - _by) < 0.6' in src), "the S face is measured from zero again"
    plan = {"footprint": {"blocks": [
        {"id": "main", "role": "main", "x_ft": 0, "y_ft": 0, "width_ft": 40, "depth_ft": 40},
        {"id": "dep", "role": "dependency", "x_ft": -30, "y_ft": 10, "width_ft": 20,
         "depth_ft": 20, "attached_to": "main"}]},
        "levels": [{"index": 0, "rooms": [
            {"id": "k", "type": "kitchen",
             "geometry": {"x_ft": -30, "y_ft": 10, "width_ft": 20, "depth_ft": 10}}]}]}
    (bx, by, bw, bh) = E.bounds_index(plan, plan["levels"][0]["rooms"])["k"]
    assert (bx, by, bw, bh) == (-30.0, 10.0, 20.0, 20.0)
    # the main-block reading would have said this room touches nothing
    assert not (abs(-30.0) < 0.6 or abs(-30.0 + 20.0 - 40.0) < 0.6)


def test_export_ifc_writes_one_slab_per_element_per_storey():
    """Layer 6. Held on the source: the exporter needs ifcopenshell, which is optional here,
    and its own selftest reports COULD NOT EVALUATE without it."""
    src = (ROOT / "build" / "export_ifc.py").read_text()
    # MERGE: main's `slab_boxes()` computes the per-element slab geometry outside the writer
    # so it can be measured without ifcopenshell -- which this environment and CI both lack.
    assert ("slab_boxes(" in src or "for e in here:" in src), (
        "the slab loop is not per element")
    # MERGE: main's slab geometry comes from `slab_boxes()` as plain numbers, so the writer
    # reads `sb["width_ft"]`; this branch sized it inline from the element dict.
    assert ('_box(f, body, slab, sb["width_ft"], sb["depth_ft"], sb["thickness_ft"])' in src
            or '_box(f, body, slab, e["W"] + 2 * t_ext, e["H"] + 2 * t_ext, depth)' in src)
    # MERGE: main names the element on the slab's Pset as `"element": sb["element"]`; this
    # branch as `"massing_element": e["id"]`. Either way the slab says which element it is
    # under, which is what the guard is for.
    assert ('"element": sb["element"]' in src or '"massing_element": e["id"]' in src), "a slab does not say which element it is under"
    # MERGE: `EL`/`_els` lived in the slab loop main's `slab_boxes` replaced, so the roof
    # loads the reader itself. The property -- the roof spans the UNION -- is unchanged.
    assert ("_EL.union_bbox(plan)" in src or "EL.union_bbox(plan, _els)" in src), (
        "the roof no longer spans the union, which is what ruling 1 gave it")


# --------------------------------------------------------------- the guarantee

# THE TWO DIGESTS MOVED AT THE MERGE OF THE TWO PHASE 11s (8 Sep 2026), AND THAT IS THE ONE
# CASE THIS GUARANTEE WAS NEVER MAKING A CLAIM ABOUT. WP-11.9's promise is that teaching six
# layers a concept no shipped plan exercises moves NO placement -- and it held, on this
# branch, through every package that made it. What arrived here is not a package: it is the
# other Phase 11, which changed the placement itself (its own parti bay module, its stacking
# rule, its candidate row) exactly as this branch did (the band-first key, the span charge).
# Two placement changes meeting cannot leave the placement where either found it.
#
# So these are RE-DERIVED, not bumped, and the old values are kept beside them: any later
# movement is a defect again, measured against the merged corpus rather than against a
# corpus neither parent shipped. `151126d0269bbc61` / `770a886c7387f3ab` were the values
# on this branch up to and including WP-11.15.
CORPUS_PLACEMENT_SHA = "68b102ff6a724e47"
# WP-11.10 MOVED THIS ONE ON PURPOSE, and it is the only thing that package moves here.
# `f7c7430ec31dae3c` -> `770a886c7387f3ab`: the terrace at grade is placed, so the door the
# record has always declared from a room to its terrace is seated instead of refused, on the
# five plans that declare one. `CORPUS_PLACEMENT_SHA` below is UNCHANGED across it, which is
# that package's own guarantee and the inverse of this one's -- WP-11.9 held both because it
# taught six layers a concept no plan exercises; WP-11.10 holds the placement and moves the
# openings because seating a refused door is the whole deliverable.
CORPUS_OPENINGS_SHA = "a81aedcc3ee4b26a"


def test_teaching_six_layers_about_elements_moved_no_shipped_placement():
    """THE GUARANTEE. Measured on a `git archive HEAD` checkout before the package and on the
    working tree after it, and pinned here so the next reader does not have to take it on
    trust. `geometry_report` is deliberately NOT hashed: it grew a `lot_extent` key, which is
    the disclosure, and hashing it would make this test fail for the one reason it should not.
    """
    h1, h2 = hashlib.sha256(), hashlib.sha256()
    for pf in _plans():
        d = json.loads(pathlib.Path(pf).read_text())
        if "levels" not in d:
            continue
        G._SOLVE_CACHE.clear()
        sol = G.solve(json.loads(json.dumps(d)), engine="heuristic")
        geo = [(lv.get("index"), r["id"], r.get("geometry"))
               for lv in sol["levels"] for r in lv["rooms"]]
        h1.update(json.dumps(geo, sort_keys=True).encode())
        h1.update(json.dumps(sol.get("footprint"), sort_keys=True).encode())
        op = [(lv.get("index"), r["id"], r.get("doors"), r.get("windows"),
               r.get("fixture_layout"), r.get("furniture_layout"))
              for lv in sol["levels"] for r in lv["rooms"]]
        h2.update(json.dumps(op, sort_keys=True).encode())
        h2.update(json.dumps(sol.get("stair"), sort_keys=True).encode())
    assert h1.hexdigest()[:16] == CORPUS_PLACEMENT_SHA, (
        "a shipped placement or footprint moved; WP-11.9 teaches six layers a concept no plan "
        "in this corpus exercises, so any movement here is a defect and not a trade")
    assert h2.hexdigest()[:16] == CORPUS_OPENINGS_SHA, (
        "a shipped opening, fixture or furniture layout moved")


def test_the_disclosure_says_what_was_taught_rather_than_what_was_not():
    """WP-6.4's rule -- 'until X lands' is a lie the moment X lands. The function listed all six
    layers as `not_element_aware` with COULD NOT EVALUATE beside them; that was true when it was
    written and became false on 5 Sep 2026."""
    src = (ROOT / "build" / "geometry.py").read_text()
    assert src.count("def multi_element_disclosure(plan):") == 1, (
        "there are two definitions of the disclosure and the second wins -- which is how this "
        "package first shipped the OLD text under the new one")
    plan = {"footprint": {"blocks": [
        {"id": "main", "role": "main", "x_ft": 0, "y_ft": 0, "width_ft": 40, "depth_ft": 40},
        {"id": "dep", "role": "dependency", "x_ft": -30, "y_ft": 10, "width_ft": 20,
         "depth_ft": 20, "attached_to": "main"}]}, "levels": []}
    note = G.multi_element_disclosure(plan)
    # MERGE: main's disclosure carries `not_element_aware` alone and taught its layers down to
    # an empty list; `element_aware` was this branch's key. The invariant both wrote it for is
    # that the second list may only SHRINK and must name a layer that really cannot judge.
    assert set(note.get("element_aware", [])) <= {"openings", "structure", "vertical_score",
                                                  "lot_cap",
                                          "plan_check.drawn", "export_ifc"}
    # WP-11.11 took `engine=cp` off this list: the CP model reads the room's own element
    # now, so the engine that PROVES is available on a multi-element plan for the first time.
    assert set(note["not_element_aware"]) <= {"roof", "composer"}, (
        "the list may only shrink, and a layer named here must really be unable to judge "
        "a multi-element placement: " + str(note["not_element_aware"]))
    assert note["built_extent_width_ft"] == 60.0
    assert note["union_bbox_ft"] == (-30.0, 0.0, 40.0, 40.0)
