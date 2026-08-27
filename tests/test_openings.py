"""WP-6.2. The opening grammar, the placement pass, and the drawn-house layer.

What is pinned here is the discipline rather than the numbers: an opening is either
placed or it says why not; a rule is either cited or the composer says it took a band's
midpoint; a plan nobody has placed reports COULD NOT EVALUATE on every drawn check and
never a pass.
"""
import glob
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
if BUILD not in sys.path:
    sys.path.insert(0, BUILD)

import modcache as mc  # noqa: E402

CO = mc.load("check_openings", os.path.join(BUILD, "check_openings.py"))
OP = mc.load("openings", os.path.join(BUILD, "openings.py"))
GEO = mc.load("geometry", os.path.join(BUILD, "geometry.py"))
PC = mc.load("plan_check", os.path.join(BUILD, "plan_check.py"))

GRAMMAR = json.load(open(os.path.join(ROOT, "openings", "grammar.json")))


def _plan(pid):
    return json.load(open(os.path.join(ROOT, "plans", f"{pid}.json")))


# ------------------------------------------------------------------ the grammar
def test_every_room_pair_resolves_to_a_named_rule():
    """Totality. The default is itself a named rule, so this cannot fail outright — what it
    guards is that a pair can never resolve to NOTHING, which would leave the composer
    dimensioning a door from no stated reason at all."""
    rooms = CO.rooms_index()
    ids = sorted(rooms) + ["exterior"]
    for i, a in enumerate(ids):
        for b in ids[i:]:
            if a == "exterior" and b == "exterior":
                continue
            rule = CO.resolve(GRAMMAR, a, rooms.get(a), b, rooms.get(b))
            assert rule and rule.get("id"), f"{a} — {b} resolves to no rule"
            assert rule["opening"]["type"]
            assert rule["basis"], f"{rule['id']} states no basis"


def test_the_grammar_is_unordered():
    """A door between two rooms is ONE door. If the grammar answered differently depending
    on which room asked, the two records of one door would disagree with each other."""
    rooms = CO.rooms_index()
    ids = sorted(rooms)[:40]
    for a in ids:
        for b in ids:
            f = CO.resolve(GRAMMAR, a, rooms.get(a), b, rooms.get(b))
            r = CO.resolve(GRAMMAR, b, rooms.get(b), a, rooms.get(a))
            assert f["id"] == r["id"], f"{a}/{b} resolves to {f['id']} one way and {r['id']} the other"


def test_every_basis_quotes_something_the_record_actually_says():
    """The check the file exists for. Editorial is a licence to judge, never a licence to
    invent: a basis naming a record that does not exist, or quoting a sentence that record
    does not contain, is a guess wearing a citation."""
    rep = CO.Report()
    for rule in CO.all_rules(GRAMMAR):
        CO.check_basis(rep, rule)
    assert not rep.errors, "\n".join(rep.errors)


def test_the_grammar_fits_the_hand_authored_door_schedule():
    """plans/tidewater-georgian-careful.json is the only worked example of a GRADED door
    schedule in the corpus — 58 doors an author dimensioned by hand, from a 6 ft cased
    opening down to a 2.2 ft closet leaf. It is the grammar's fit target, and the fit is
    exact rather than approximate.

    plans/spec-builder-colonial.json is deliberately NOT held to this: its own note calls
    it "a deliberately ordinary production plan, written to see what the validator
    catches", and the grammar disagreeing with its 6 ft and 10 ft openings is the grammar
    agreeing with faults/open-plan-in-a-room-based-style.json."""
    rooms = CO.rooms_index()
    plan = _plan("tidewater-georgian-careful")
    types = {r["id"]: r["type"] for lv in plan["levels"] for r in lv["rooms"]}
    seen, out_of_band, n = set(), [], 0
    for lv in plan["levels"]:
        for r in lv["rooms"]:
            for d in (r.get("doors") or []):
                key = tuple(sorted((r["id"], d["to"])))
                if key in seen or d.get("width_ft") is None:
                    continue
                seen.add(key)
                bt = "exterior" if d["to"] == "exterior" else types.get(d["to"])
                if bt is None:
                    continue
                rule = CO.resolve(GRAMMAR, types[r["id"]], rooms.get(types[r["id"]]),
                                  bt, rooms.get(bt))
                lo, hi = rule["opening"]["width_band_ft"]
                n += 1
                if not (lo - 1e-9 <= d["width_ft"] <= hi + 1e-9):
                    out_of_band.append((r["id"], d["to"], d["width_ft"], rule["id"], [lo, hi]))
    assert n >= 25, f"only {n} dimensioned doors compared — the fit target has moved"
    assert not out_of_band, f"{len(out_of_band)} of {n} outside their band: {out_of_band}"


# ------------------------------------------------------------------ the placement pass
@pytest.mark.parametrize("pid", ["tidewater-georgian-careful", "spec-builder-colonial"])
def test_every_opening_is_placed_or_says_why_not(pid):
    """The rule this module exists for. Before WP-6.2 an opening the placement could not
    realise was dropped in silence by both renderers; now it stays in the record carrying a
    reason. There is no third state."""
    solved = GEO.solve(_plan(pid))
    for lv in solved["levels"]:
        for r in lv["rooms"]:
            if not r.get("geometry"):
                continue
            for d in (r.get("doors") or []):
                placed = d.get("wall") is not None and d.get("position_ft") is not None
                if d.get("unplaced"):
                    assert d["unplaced"].get("reason"), f"{r['id']}→{d['to']} unplaced with no reason"
                    assert not placed, f"{r['id']}→{d['to']} is both placed and unplaced"
                else:
                    assert placed, f"{r['id']}→{d['to']} is neither placed nor marked unplaced"
            for w in (r.get("windows") or []):
                if not w.get("unplaced"):
                    assert w.get("positions_ft"), \
                        f"{r['id']} window on {w.get('wall')} neither placed nor marked"
                else:
                    assert w["unplaced"].get("reason")


@pytest.mark.parametrize("pid", ["tidewater-georgian-careful", "spec-builder-colonial"])
def test_no_two_openings_share_masonry(pid):
    """Doors and windows on one wall of one room may not overlap. This is the invariant
    behind the reported symptom "the centre passage shows no door out the back — it's
    really just a window": the door and the window were at the same coordinate and the
    window was painted last."""
    solved = GEO.solve(_plan(pid))
    for lv in solved["levels"]:
        spans = {}
        for r in lv["rooms"]:
            for d in (r.get("doors") or []):
                if d.get("unplaced") or d.get("wall") is None:
                    continue
                w = d.get("width_ft") or 3.0
                spans.setdefault((r["id"], d["wall"]), []).append(
                    ("door", d["position_ft"] - w / 2, d["position_ft"] + w / 2))
            for win in (r.get("windows") or []):
                if win.get("unplaced") and not win.get("positions_ft"):
                    continue
                w = win.get("width_ft") or 3.0
                for p in (win.get("positions_ft") or []):
                    spans.setdefault((r["id"], win["wall"]), []).append(
                        ("window", p - w / 2, p + w / 2))
        for key, items in spans.items():
            items.sort(key=lambda t: t[1])
            for (k1, a1, b1), (k2, a2, b2) in zip(items, items[1:]):
                assert a2 >= b1 - 1e-6, \
                    f"{pid} {key[0]} wall {key[1]}: {k1} [{a1:.2f},{b1:.2f}] overlaps {k2}"


def test_the_passage_takes_its_rear_door():
    """The reported symptom in its exact form: "the centre passage shows no door out the
    back — it's really just a window."

    styles/tidewater-georgian.json c03 is HARD — "exterior doors at both ends, aligned on
    axis and both operable" — and could not be satisfied, because a door had no wall: both
    renderers put every exterior door of a room on the FIRST wall it declared, so the
    passage's rear door was drawn on its front, under the front door.

    This asserts the OUTCOME, which is what must hold of any correct placement: the
    passage's own exterior door sits on a boundary wall it does not already reach the
    outside through. The mechanism that decides it when the passage touches BOTH ends —
    op-passage-axis — is tested separately below, because which rule fires depends on where
    the solver put the room, and pinning that here made this test fail the day the
    placement got BETTER."""
    solved = GEO.solve(_plan("tidewater-georgian-careful"))
    passage = next(r for lv in solved["levels"] for r in lv["rooms"] if r["id"] == "passage")
    ext = [d for d in passage["doors"] if d["to"] == "exterior"]
    assert ext, "the passage declares an exterior door"
    d = ext[0]
    assert not d.get("unplaced"), f"the passage's own exterior door is unplaced: {d.get('unplaced')}"
    assert d.get("wall") in ("N", "E", "S", "W"), "it must be on a stated wall"
    # and not on the wall it already reaches the outside through (the porch door)
    porch = next((x for x in passage["doors"] if x["to"] == "porch"), None)
    if porch and porch.get("wall"):
        assert d["wall"] != porch["wall"], \
            "the passage's two ways out are on the same wall — that is the reported symptom"


def test_the_passage_axis_rule_seats_a_door_at_the_far_end():
    """op-passage-axis itself, on the case it exists for: a circulation room reaching the
    boundary at BOTH ends, already entered through a threshold room at one of them. The
    declared exterior door must take the other end."""
    plan = {
        "id": "axis-probe", "name": "axis probe", "style": "tidewater-georgian",
        "footprint": {"width_ft": 30.0, "depth_ft": 40.0},
        "levels": [{"id": "ground", "index": 0, "rooms": [
            {"id": "passage", "type": "centre-passage", "width_ft": 10, "length_ft": 40,
             "exterior_walls": ["S", "N"],
             "geometry": {"x_ft": 10, "y_ft": 0, "width_ft": 10, "depth_ft": 40, "area_sf": 400},
             "doors": [{"to": "porch", "width_ft": 3.5}, {"to": "exterior", "width_ft": 3.5}]},
            {"id": "porch", "type": "entry-porch", "width_ft": 10, "length_ft": 6,
             "exterior_walls": ["S", "E", "W"],
             "geometry": {"x_ft": 20, "y_ft": 0, "width_ft": 10, "depth_ft": 6, "area_sf": 60},
             "doors": [{"to": "passage", "width_ft": 3.5}, {"to": "exterior", "width_ft": 3.5}]},
        ]}],
    }
    OP.place(plan)
    passage = plan["levels"][0]["rooms"][0]
    d = next(x for x in passage["doors"] if x["to"] == "exterior")
    assert d.get("wall") == "N", (
        f"the passage reaches the boundary at both ends and is entered through the porch at "
        f"the south; its own exterior door belongs at the north end, not on {d.get('wall')}")
    assert any(a.get("rule") == "op-passage-axis" for a in plan["opening_report"]["axis"])


def test_the_stair_is_an_object_or_a_stated_refusal():
    """There has never been a stair in this system: a stair hall was an empty rectangle
    with lettering in it. Now it is either drawn from flights the record carries, or it is
    a named refusal — never an empty room presented as a finished one."""
    solved = GEO.solve(_plan("tidewater-georgian-careful"))
    st = solved.get("stair")
    assert st, "no stair object on a plan with a placed stair hall"
    assert st["risers"] >= 2 and st["riser_in"] > 0 and st["tread_in"] >= 10.0
    assert st.get("well"), "a stair must at least record the well it occupies"
    assert st.get("flights") or st.get("unplaced", {}).get("reason"), \
        "a stair with no flights must say why"


# ------------------------------------------------------------------ the drawn layer
def test_the_drawn_layer_cannot_evaluate_an_unplaced_record():
    """Three states, and the third is the one that matters. A hand-authored record carries
    no placement, and every drawn check must report COULD NOT EVALUATE rather than passing
    — the corpus's first discipline, applied to geometry."""
    res = PC.check(_plan("tidewater-georgian-careful"))
    d = res["drawn_summary"]
    assert d["evaluated"] is False
    assert d["reason"]
    assert not [f for f in res["findings"]
                if f["layer"] == "drawn" and f["severity"] in ("fatal", "serious", "minor")], \
        "an unplaced record must not be FAILED on drawn facts either"
    assert any(f["layer"] == "drawn" and f["severity"] == "info" for f in res["findings"])


# The three tests below assert the MECHANISM against a placement built for the purpose,
# not a defect count against a shipped plan.
#
# They did the latter first, and it cost them: WP-6.3 made the CP engine able to solve
# plans/tidewater-georgian-careful.json (the per-pair door floor is looser for narrow
# doors, so the model fits in budget), the placement stopped stranding rooms, and all
# three tests went RED because the defects they pinned had been FIXED. A guard that fails
# when the code gets better is pointed the wrong way — the same lesson OQ 71 taught
# test_solver.py ("assert the proof, not the count") and that the workbench's
# path-traversal test learned the same week (assert the property, not the mechanism).


def _stranded_plan():
    """A placed two-room plan where the second room's only door has no shared wall."""
    return {
        "id": "stranded", "name": "stranded", "style": "tidewater-georgian",
        "footprint": {"width_ft": 30.0, "depth_ft": 20.0},
        "levels": [{"id": "ground", "index": 0, "rooms": [
            {"id": "hall", "type": "entrance-hall", "width_ft": 10, "length_ft": 20,
             "exterior_walls": ["S"],
             "geometry": {"x_ft": 0, "y_ft": 0, "width_ft": 10, "depth_ft": 20, "area_sf": 200},
             "doors": [{"to": "exterior", "width_ft": 3.5, "wall": "S", "position_ft": 5.0},
                       {"to": "bath", "width_ft": 2.6,
                        "unplaced": {"reason": "the placement leaves these two rooms no shared wall"}}]},
            {"id": "bath", "type": "bathroom", "width_ft": 6, "length_ft": 8,
             "geometry": {"x_ft": 20, "y_ft": 0, "width_ft": 6, "depth_ft": 8, "area_sf": 48},
             "doors": [{"to": "hall", "width_ft": 2.6,
                        "unplaced": {"reason": "the placement leaves these two rooms no shared wall"}}]},
        ]}],
    }


def test_a_room_no_door_reaches_is_a_fatal_finding():
    """Nothing in this system had ever checked that you can walk from the front door to
    every room. build/check_partis.py's comment asserted the plan validator did; it did
    not, and a chamber bath whose only door the placement could not realise shipped on a
    reference sheet with no finding against it."""
    res = PC.check(_stranded_plan())
    d = res["drawn_summary"]
    assert d["evaluated"] is True
    assert d["unreachable"] == ["bath"], f"expected the bath stranded, got {d['unreachable']}"
    fatals = [f for f in res["findings"] if f["layer"] == "drawn" and f["severity"] == "fatal"]
    assert len(fatals) == 1 and "cannot be reached" in fatals[0]["statement"]


def test_a_room_reachable_only_from_outdoors_is_named_as_such():
    """The first reported symptom: "the door to the kitchen is only from the outside, and
    the kitchen is connected to no other rooms". Such a room PASSES reachability — it has
    its own exterior door — and is still wrong, so it is its own finding rather than
    silence."""
    plan = _stranded_plan()
    # give the bath its own way out: now it is reachable, and still joined to nothing
    plan["levels"][0]["rooms"][1]["doors"].append(
        {"to": "exterior", "width_ft": 3.0, "wall": "S", "position_ft": 23.0})
    res = PC.check(plan)
    # BOTH rooms are cut off, and correctly so: the one door between them is the one the
    # placement could not realise, so each is joined to nothing but the outdoors
    assert set(res["drawn_summary"]["cut_off"]) == {"bath", "hall"}
    assert not res["drawn_summary"]["unreachable"], "both ARE reachable — from outdoors"
    said = [f for f in res["findings"]
            if f["layer"] == "drawn" and "only way in is from outside" in f["statement"]]
    assert said, "the isolation must be stated, not merely counted"


def test_drawn_and_declared_sizes_are_reconciled_or_reported():
    """OQ 54's silence, closed. The sheet prints the PLACED rectangle and the record keeps
    the declared one; nothing said they differed, so a room drawn at 63% of its declared
    area read as a measurement of the declared room.

    Asserted as a property of ANY placement rather than as a list of rooms: every room
    whose drawn area departs from its declaration by more than a tenth must appear in the
    summary, and every entry must carry the percentage."""
    solved = GEO.solve(_plan("tidewater-georgian-careful"))
    res = PC.check(solved)
    reported = {d["room"]: d["pct"] for d in res["drawn_summary"]["diverged"]}
    assert reported, "this placement does diverge from the record somewhere"
    declared, placed = {}, {}
    for lv in solved["levels"]:
        for r in lv["rooms"]:
            g = r.get("geometry")
            if g and r.get("width_ft") and r.get("length_ft"):
                declared[r["id"]] = r["width_ft"] * r["length_ft"]
                placed[r["id"]] = g["width_ft"] * g["depth_ft"]
    # the layer reports at a tenth OR MORE, and the boundary is not hypothetical: on this
    # placement the kitchen and the library both land at exactly -10.00%
    expected = {rid for rid in declared
                if abs(placed[rid] - declared[rid]) / declared[rid] >= 0.10 - 1e-9}
    assert set(reported) == expected, (
        f"reported {sorted(set(reported) - expected)} that do not diverge, and missed "
        f"{sorted(expected - set(reported))}")
    for rid, pct in reported.items():
        assert abs(pct) >= 10, f"{rid} reported at {pct}% — under the threshold"


class TestFurnitureIsArrangedAgainstThePlacedOpenings:
    """WP-7.2 (OQ 73). Two defects and one rule, all of them about the same thing: the
    fixtures and the openings were placed as if the other did not exist."""

    def test_no_door_is_drawn_through_a_fixture(self):
        """The reported defect. `openings.place`'s docstring said fixtures ran first
        "because a door has to know what is against the wall it would swing into" -- and
        `occupied` never held a fixture, so the code did not do the thing its own comment
        gave as the reason. Measured on the CP placements before the fix: the powder room's
        basin overlapped its door by 1.92 ft and the principal bath's double vanity by
        2.70 ft on `spec-builder-colonial`."""
        for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
            solved = GEO.solve(_plan(pid))
            for lv in solved["levels"]:
                for r in lv["rooms"]:
                    for d in (r.get("doors") or []):
                        if d.get("unplaced") or d.get("position_ft") is None or not d.get("wall"):
                            continue
                        w = d.get("width_ft") or 3.0
                        lo, hi = d["position_ft"] - w / 2, d["position_ft"] + w / 2
                        horiz = d["wall"] in ("N", "S")
                        for f in (r.get("fixture_layout") or []):
                            if f.get("unplaced") or f.get("x_ft") is None:
                                continue
                            if f.get("wall") != d["wall"]:
                                continue
                            a, b = ((f["x_ft"], f["x_ft"] + f["width_ft"]) if horiz
                                    else (f["y_ft"], f["y_ft"] + f["depth_ft"]))
                            assert min(hi, b) - max(lo, a) <= 0.05, (
                                f"{pid}: the door {r['id']}->{d['to']} is drawn through "
                                f"{f['item']}")

    def test_a_fixture_is_tried_on_every_wall_before_it_is_refused(self):
        """Packing against the longest wall regardless of what is already on it reported the
        powder room's water closet and basin as unfittable while its east wall stood empty.
        A fixture refused on a wall nobody tried is a false "cannot fit", and this corpus
        exists to distinguish evaluated-and-failed from not-looked-at."""
        for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
            solved = GEO.solve(_plan(pid))
            rep = solved.get("opening_report") or {}
            assert rep.get("fixtures_placed", 0) > 0, "vacuous unless fixtures were placed"
            assert rep.get("fixtures_unplaced", 0) == 0, (
                f"{pid}: {rep.get('fixtures_unplaced')} fixture(s) refused")

    def test_every_furniture_item_states_its_own_placement(self):
        """`placement` decides one-sided or two-sided clearance and is the difference between
        a galley kitchen passing its own rule and failing it. The schema declared it and 0 of
        278 items carried one, so `plan_check` guessed from the item's NAME -- calling 84
        against-wall where the authored data calls 159."""
        import glob
        n = against = 0
        for f in sorted(glob.glob(os.path.join(ROOT, "rooms", "*.json"))):
            for it in (json.load(open(f)).get("furniture") or []):
                n += 1
                assert it.get("placement"), f"{f}: {it['item']} states no placement"
                against += it["placement"] in ("against-wall", "corner", "built-in")
        assert n == 278, f"the corpus moved: {n} furniture items"
        assert against > 150, "the authored data should call far more items wall-bound than the old regex did"

    def test_a_stated_wall_run_is_measured_against_the_placed_openings(self):
        """The one arrangement rule the corpus states in words, and it is checked rather than
        assumed. Both directions are pinned, because a check that never fires and a check
        that always fires are equally useless."""
        import copy
        PC = mc.load("plan_check", os.path.join(ROOT, "build", "plan_check.py"))
        solved = GEO.solve(_plan("tidewater-georgian-careful"))

        # it PASSES on the shipped plan, and for a measured reason: the dining room is
        # 23 x 14 with its three doors on N and W, so the whole S wall is unbroken
        clean = [f for f in PC.check(solved)["findings"] if "unbroken run of wall" in f["statement"]]
        assert not clean, clean

        # and it FIRES when the walls really are full
        q = copy.deepcopy(solved)
        for lv in q["levels"]:
            for r in lv["rooms"]:
                if r["type"] != "dining-room":
                    continue
                g = r["geometry"]
                r["doors"] = []
                r["windows"] = [
                    {"wall": "S", "width_ft": g["width_ft"] - 2, "count": 1,
                     "position_ft": g["x_ft"] + g["width_ft"] / 2},
                    {"wall": "N", "width_ft": g["width_ft"] - 2, "count": 1,
                     "position_ft": g["x_ft"] + g["width_ft"] / 2},
                    {"wall": "W", "width_ft": g["depth_ft"] - 2, "count": 1,
                     "position_ft": g["y_ft"] + g["depth_ft"] / 2},
                    {"wall": "E", "width_ft": g["depth_ft"] - 2, "count": 1,
                     "position_ft": g["y_ft"] + g["depth_ft"] / 2}]
        hits = [f for f in PC.check(q)["findings"] if "unbroken run of wall" in f["statement"]]
        assert len(hits) == 1, hits
        # the finding quotes the room's own sentence, which is the basis for the number
        assert "uninterrupted wall of at least 6 ft" in hits[0]["statement"]
        assert hits[0]["severity"] == "minor"


class TestTheWindowGrammar:
    """WP-7.3 (OQ 72). The register's question was never what the window types are — the
    corpus knows them — but WHICH LAYER decides. The answer this package gives: the grammar
    decides the ROLE and the kit decides the KIND, and neither may state the other's."""

    def _g(self):
        return json.load(open(os.path.join(ROOT, "openings", "window-grammar.json")))

    def test_every_basis_quotes_prose_that_is_really_in_the_record(self):
        """The same guarantee the door grammar gives, using the same function rather than a
        second copy. It caught three loose transcriptions while this file was being written,
        which is exactly what it is for: an editorial call whose citation cannot be checked is
        a guess wearing a citation."""
        CO = mc.load("check_openings", os.path.join(ROOT, "build", "check_openings.py"))
        CW = mc.load("check_windows", os.path.join(ROOT, "build", "check_windows.py"))
        g = self._g()
        rep = CO.Report()
        for r in CW.all_rules(g):
            if r["id"] == g["default"]["id"]:
                continue
            CO.check_basis(rep, r, "openings/window-grammar.json")
        assert not rep.errors, rep.errors

    def test_resolution_is_total_and_the_fall_through_is_published(self):
        """Every room type against every wall exposure lands on a named rule, and how many
        reach a mere default is a number the checker prints rather than hides."""
        CW = mc.load("check_windows", os.path.join(ROOT, "build", "check_windows.py"))
        g = self._g()
        C = CW.rooms_corpus()
        assert len(C) == 60, f"the room corpus moved: {len(C)}"
        tiers = {"room": 0, "class": 0, "default": 0}
        for room in C.values():
            for wall in ("exterior", "interior"):
                rule, tier = CW.resolve(g, room, wall)
                assert rule and rule.get("id")
                tiers[tier] += 1
        assert sum(tiers.values()) == 120
        # a grammar that answered nothing would still be "total" via its default, so the
        # share landing on a rule that READ something is what is actually pinned
        assert tiers["room"] + tiers["class"] >= 100, tiers

    def test_no_rule_states_a_sash_kind_and_no_borrowed_light_is_in_an_exterior_wall(self):
        """The two-layer split, enforced rather than described. A room rule carrying a
        `unit_type` would put the kits' vocabulary in a second place."""
        CW = mc.load("check_windows", os.path.join(ROOT, "build", "check_windows.py"))
        g = self._g()
        roles = set(g["roles"])
        for r in CW.all_rules(g):
            u = r.get("unit") or {}
            assert u.get("role") in roles, r["id"]
            assert "unit_type" not in u and "window_type" not in u, r["id"]
            if u["role"] == "borrowed-light":
                assert (r.get("when") or {}).get("wall") == "interior", r["id"]

    def test_the_grammar_publishes_no_closed_enum(self):
        """A first draft invented one — double-hung / casement / fixed — and the kits use ~40
        free strings including `clean-rectangle-flat-architrave` and `horseshoe-arch`. That
        would have been a second spelling of the kits' own vocabulary."""
        g = self._g()
        assert not (g.get("unit_types") or {}).get("values")
        assert (g["unit_types"]["observed"]["styles_resolving"]) == 119

    def test_the_kit_is_resolved_through_the_lineage_and_both_states_are_live(self):
        """The correction that mattered most. `kits/*.json` carries `window_type` as empty on
        120 of 159, so reading the flat file reported COULD NOT EVALUATE for styles the
        corpus answers for perfectly well — `tidewater-georgian` among them, which inherits
        `double-hung` from `georgian-colonial-american`. Through the cascade, 119 of 159
        resolve. Both branches are pinned so neither can become dead code."""
        CO = mc.load("compose", os.path.join(ROOT, "build", "compose.py"))
        kind, _whence, _ref = CO.kit_window_type("tidewater-georgian")
        assert kind == "double-hung", kind
        resolved = sum(1 for f in sorted(glob.glob(os.path.join(ROOT, "kits", "*.json")))
                       if CO.kit_window_type(json.load(open(f))["style"])[0])
        assert resolved == 119, resolved
        # and the withheld state is real, not theoretical
        assert 159 - resolved == 40
