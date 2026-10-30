"""WP-17.2: the composer poses a programme the type's own facts can hold (`compose.compose_to_the_type`).

Measured on Lucas's brief of 29 Oct 2026 (tidewater-georgian, 3,200 sf, four bedrooms, 3.5 baths):
every composed two-storey candidate was refused a drawing, and a read-only spike holding every fact,
band, size and door hard on CP-SAT drew the foursquare with every room in band once its upper gallery
corridor was sized from its own record -- the composer had sized it from the midpoint of a 150-3,000 sf
band, 13.5 x 87.6 ft, 57% of the upper programme. These hold what the pass does to the record.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
OP = modcache.load("openings", os.path.join(ROOT, "build", "openings.py"))

BRIEF = {"id": "lucas-29-oct", "style": "tidewater-georgian", "target_area_sf": 3200,
         "bedrooms": 4, "bathrooms": 3.5}


def _rooms(plan):
    return {r["id"]: (lv["index"], r) for lv in plan["levels"] for r in lv["rooms"]}


def _heated(plan):
    return sum(r["width_ft"] * r["length_ft"] for _l, r in _rooms(plan).values()
               if CO.C["rooms"].get(r["type"], {}).get("function_class") != "outdoor")


def test_an_open_band_corridor_is_sized_from_what_it_is_for():
    plan, log, _p = CO.instantiate("foursquare-quadrant", BRIEF)
    _l, hall = _rooms(plan)["upperhall"]
    area, wb, lb, _pr = CO._bands(hall["type"])
    assert area[1] >= CO.OPEN_BAND_FACTOR * area[0], "the premise: the corridor's band is open"
    assert hall["width_ft"] == wb[0], "its record's working width, the width band's floor"
    run = sum(OP.required_wall_ft(float(d.get("width_ft") or 3.0)) for d in hall.get("doors") or []) / 2
    assert hall["length_ft"] >= run - 0.01 and hall["length_ft"] * hall["width_ft"] >= area[0] - 0.01
    assert hall["width_ft"] * hall["length_ft"] < 0.2 * _heated(plan), (
        "a corridor is not a fifth of the house -- it was 57% of the upper programme")
    assert any(l.startswith("Sized Upper Hall from what it is for") for l in log)


def test_a_closed_band_room_is_not_resized_as_circulation():
    plan, _log, _p = CO.instantiate("centre-passage-double-pile", BRIEF)
    _l, passage = _rooms(plan)["passage"]
    area, _wb, _lb, _pr = CO._bands(passage["type"])
    assert area[1] < CO.OPEN_BAND_FACTOR * area[0], "the premise: the passage's band is closed"
    assert passage["width_ft"] > 4.0, "a centre passage keeps its own width"


def test_a_room_that_stands_over_another_takes_its_plan_inside_its_own_bands():
    seen = 0
    for pid in ("foursquare-quadrant", "centre-passage-double-pile", "side-hall-townhouse"):
        plan, log, _p = CO.instantiate(pid, BRIEF)
        rooms = _rooms(plan)
        for rid, (lvl, r) in rooms.items():
            so = r.get("stacks_over")
            if not so or so not in rooms or rooms[so][0] != lvl - 1:
                continue
            t = rooms[so][1]
            assert (r["width_ft"], r["length_ft"]) == CO._clamp_dims(t["width_ft"], t["length_ft"], r["type"]), (
                pid, rid, so)
            # THE BANDS THE TEST IS NAMED FOR, READ OFF THE RECORD AND NOT THROUGH `_clamp_dims`
            # (the Phase 17 audit's finding 34): the equality above is the function under test on
            # both sides, so deleting every clamp left it green. Each follower is held to its own
            # width, length, proportion and area bands, and where the target already sits inside
            # them the follower IS the target.
            d = CO.C["rooms"][r["type"]].get("dimensions") or {}
            s, g = min(r["width_ft"], r["length_ft"]), max(r["width_ft"], r["length_ft"])
            ts, tg = min(t["width_ft"], t["length_ft"]), max(t["width_ft"], t["length_ft"])
            inside = True
            for key, v, tv in (("width_ft", s, ts), ("length_ft", g, tg)):
                band = d.get(key)
                if band:
                    assert band[0] - 0.01 <= v <= band[1] + 0.01, (pid, rid, key, v, band)
                    inside &= band[0] <= tv <= band[1]
            if d.get("proportion"):
                assert g <= d["proportion"][1] * s + 0.02, (pid, rid, "proportion", g / s, d["proportion"])
                inside &= tg <= d["proportion"][1] * ts
            if d.get("area_sf"):
                assert d["area_sf"][0] - 0.5 <= s * g <= d["area_sf"][1] + 0.5, (pid, rid, "area", s * g)
                inside &= d["area_sf"][0] <= ts * tg <= d["area_sf"][1]
            if inside:
                assert (s, g) == (round(ts, 2), round(tg, 2)), (pid, rid, "a target in band is taken whole")
            seen += 1
        assert any(l.startswith("JUDGMENT (editorial):") and "which it stands over" in l for l in log), pid
    assert seen >= 6, f"the premise: the three diagrams declare structural stacks ({seen})"


def test_bands_that_cannot_co_hold_are_said_and_never_left_in_silence():
    """The latent half of finding 34: the area step runs last and can undo the width floor.
    `_clamp_dims(5, 36, 'landing')` returns 2.89 ft against a 3 ft floor; it is returned as it is
    and SAID, never silently out of the band it was brought into."""
    said = []
    s, g = CO._clamp_dims(5, 36, "landing", said)
    wb = CO.C["rooms"]["landing"]["dimensions"]["width_ft"]
    assert s < wb[0], "the premise: this target is one the bands cannot co-hold"
    assert said and "cannot co-hold" in said[0] and "width" in said[0], said
    ok = []
    CO._clamp_dims(5, 12, "landing", ok)
    assert ok == [], "a target the bands can hold says nothing"


# ------------------------------------------------- finding 2: the windows are sized after the pass
def _pack_unit_ft(room_width_ft):
    PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
    _, rule = CO._pack_rule("opening-proportion", "window_width_from_room")
    lo, hi = rule.get("range") or [20.0, 72.0]
    v = PE.evaluate_expr(rule["expression"], {"room_width": room_width_ft * 12.0})
    return round(min(hi, max(lo, v)) / 12.0, 2)


def test_each_window_is_sized_from_the_room_as_composed_not_as_it_was_before_the_type_pass():
    """The Phase 17 audit's finding 2. The windows were derived BEFORE `compose_to_the_type`
    resized the rooms, so on Lucas's brief the living room went 14.4 -> 17.91 ft wide and kept
    3.2 ft units (14.4 / 4.5) where the rule gives 3.98."""
    for pid in ("foursquare-quadrant", "five-part-palladian", "gable-front-and-wing"):
        plan, log, _p = CO.instantiate(pid, BRIEF)
        held = 0
        for _rid, (_l, r) in _rooms(plan).items():
            for w in r.get("windows") or []:
                want = _pack_unit_ft(r["width_ft"])
                if w.get("width_ft") is None:
                    continue
                assert w["width_ft"] == want, (pid, r["id"], w["width_ft"], want, r["width_ft"])
                held += 1
        assert held, pid
    plan, log, _p = CO.instantiate("foursquare-quadrant", BRIEF)
    living = _rooms(plan)["living"][1]
    assert living["width_ft"] > 14.4, "the premise: the type pass resized the living room"
    assert {w["width_ft"] for w in living["windows"]} == {_pack_unit_ft(living["width_ft"])}


def test_each_wall_carries_no_more_units_than_its_final_run_can_hold():
    """Finding 2's other half: a room the pass SHRINKS kept a count capped on its old run. The cap
    is the composer's own (`window_pier.floor`), on the run the room is composed at."""
    WP = modcache.load("window_pier", os.path.join(ROOT, "build", "window_pier.py"))
    floor, _src = WP.floor()
    checked = 0
    for pid in sorted(CO.PARTIS):
        try:
            plan, _log, _p = CO.instantiate(pid, BRIEF)
        except Exception:
            continue
        for _rid, (_l, r) in _rooms(plan).items():
            for w in r.get("windows") or []:
                unit = w.get("width_ft") or 3.2
                run = r["width_ft"] if w.get("wall") in ("N", "S") else r["length_ft"]
                cap = (max(1, int((run + unit * floor) // (unit * (1.0 + floor)))) if floor is not None
                       else max(1, int(run // unit)))
                assert (w.get("count") or 1) <= cap, (pid, r["id"], w.get("wall"), w.get("count"), cap, run)
                checked += 1
    assert checked > 100, f"the premise: the catalogue declares windows on this brief ({checked})"


# ------------------------------------------- finding 3: the growth reads every ceiling, never shrinks
def test_the_growth_back_toward_the_brief_takes_no_room_past_its_width_or_length_ceiling():
    """The Phase 17 audit's finding 3. The growth loop clamped the area band alone and scaled both
    sides: the foursquare's chamber closets went 2.1 -> 2.61 ft against a 2.33 ft width ceiling,
    and two diagrams' bedrooms 12.9 -> 16.06 ft against a 16 ft length ceiling (plan_check then
    reported `length-above-band` the record did not carry before the pass)."""
    for pid in ("foursquare-quadrant", "gable-front-and-wing", "bungalow-open-linear"):
        plan, log, _p = CO.instantiate(pid, BRIEF)
        assert any(l.startswith("Grew the rooms the type pass did not size") for l in log), (
            "the premise: the pass grows this diagram", pid)
        for _rid, (_l, r) in _rooms(plan).items():
            d = CO.C["rooms"].get(r["type"], {}).get("dimensions") or {}
            s, g = min(r["width_ft"], r["length_ft"]), max(r["width_ft"], r["length_ft"])
            if d.get("width_ft"):
                assert s <= d["width_ft"][1] + 0.01, (pid, r["id"], "width", s, d["width_ft"])
            if d.get("length_ft"):
                assert g <= d["length_ft"][1] + 0.01, (pid, r["id"], "length", g, d["length_ft"])
        res = CO.PC.check(plan, CO.C)
        assert not [f for f in res["findings"] if f.get("kind") == "length-above-band"], pid


def test_the_growth_factor_never_shrinks_a_room_and_stops_at_its_first_ceiling():
    # a closet already at its width ceiling does not grow, and is not shrunk for it
    wb = CO.C["rooms"]["closet"]["dimensions"]["width_ft"]
    assert CO._growth_factor(wb[1], 5.0, "closet", 1.3) == 1.0
    assert CO._growth_factor(wb[1] + 0.5, 5.0, "closet", 1.3) == 1.0, "not shrunk for its width"
    # the one factor under 1 is the area correction the loop always made, named in the docstring
    area = CO.C["rooms"]["bedroom"]["dimensions"]["area_sf"]
    s = (area[1] * 1.01) ** 0.5
    f = CO._growth_factor(s, s, "bedroom", 1.2)
    assert abs((s * f) ** 2 - area[1]) < 1e-6, "a room composed over its area ceiling is brought to it"
    k = CO._growth_factor(2.1, 5.3, "closet", 1.3)
    assert abs(2.1 * k - wb[1]) < 1e-9, "the factor stops exactly at the width ceiling"
    assert CO._growth_factor(10.0, 12.0, "bedroom", 1.05) == 1.05, "inside every band it is the house's"


def test_the_area_the_corridor_gave_back_is_grown_back_toward_the_brief():
    for pid in ("foursquare-quadrant", "side-hall-townhouse"):
        plan, log, _p = CO.instantiate(pid, BRIEF)
        grew = [l for l in log if l.startswith("Grew the rooms the type pass did not size")]
        assert grew, f"the premise: the pass left {pid} short of the brief"
        tol = BRIEF.get("area_tolerance", 0.12)
        assert abs(_heated(plan) - BRIEF["target_area_sf"]) <= tol * BRIEF["target_area_sf"], (pid, _heated(plan))
        for _lid, (_l, r) in _rooms(plan).items():
            area, *_ = CO._bands(r["type"])
            if area:
                assert r["width_ft"] * r["length_ft"] <= area[1] + 0.5, (pid, r["id"])


def test_every_composed_plan_names_its_parti():
    named = 0
    for pid in CO.PARTIS:
        try:
            plan, _log, _p = CO.instantiate(pid, BRIEF)
        except Exception:
            continue                      # a diagram this brief cannot seed is not this test's
        assert plan["parti"] == pid
        named += 1
    assert named >= len(CO.PARTIS) - 2, f"the premise: the catalogue seeds on this brief ({named})"


def test_a_bathroom_shortfall_is_said_and_nothing_is_invented():
    plan, log, _p = CO.instantiate("foursquare-quadrant", BRIEF)
    n_baths = sum(1 for _l, r in _rooms(plan).values() if r["type"] in ("bathroom", "primary-bathroom"))
    said = [l for l in log if "asks for 3.5 bathrooms" in l]
    assert said and "Not added" in said[0]
    plan2, log2, _p = CO.instantiate("foursquare-quadrant", {**BRIEF, "bathrooms": 1})
    assert not [l for l in log2 if "bathrooms and this diagram" in l]
    assert n_baths == sum(1 for _l, r in _rooms(plan2).values() if r["type"] in ("bathroom", "primary-bathroom"))


def test_growing_back_never_takes_a_room_past_its_own_area_band():
    """Driven at a brief larger than the diagram grows into, where the growth meets the bands: on
    Lucas's 3,200 sf no grown room reaches its ceiling, so that brief cannot see the clamp."""
    big = {**BRIEF, "target_area_sf": 6400}
    plan, log, _p = CO.instantiate("foursquare-quadrant", big)
    assert any(l.startswith("Grew the rooms the type pass did not size") for l in log), "the premise"
    at_ceiling = 0
    for _lid, (_l, r) in _rooms(plan).items():
        area, *_ = CO._bands(r["type"])
        if area:
            a = r["width_ft"] * r["length_ft"]
            assert a <= area[1] + 0.5, (r["id"], round(a), area)
            at_ceiling += a >= area[1] - 1.0
    assert at_ceiling, "the premise: some room grew to its band's ceiling"


def test_the_entrance_front_is_read_off_the_diagrams_own_entry():
    """A porch declared S, E and W in front of a passage declared N and S is entered on S. Without
    a stated front every entrance rule downstream -- the search's anchor, the entrance score, the
    hard entry-off-its-front fact -- had nothing to read on a composed plan."""
    plan, log, _p = CO.instantiate("centre-passage-double-pile", BRIEF)
    assert plan["context"]["entrance_faces"] == "S"
    said = [l for l in log if l.startswith("JUDGMENT: the house is entered on its S front")]
    assert said and "into Centre Passage (S/N)" in said[0], said


def test_a_brief_that_states_its_front_keeps_it():
    plan, log, _p = CO.instantiate("centre-passage-double-pile", {**BRIEF, "context": {"entrance_faces": "N"}})
    assert plan["context"]["entrance_faces"] == "N"
    assert not [l for l in log if "entered on its" in l]


def test_a_diagram_whose_entry_does_not_settle_the_front_states_none_and_says_so():
    plan, log, _p = CO.instantiate("bungalow-open-linear", BRIEF)
    assert not plan["context"].get("entrance_faces")
    assert [l for l in log if l.startswith("DISCLOSURE: the diagram's entry does not settle")]


def test_each_diagram_reads_its_own_front_and_the_brief_is_not_written_to():
    """THE AUDIT OF PHASE 17 (30 Oct 2026): `instantiate` handed every plan the BRIEF's own
    `context` dict, so `_entrance_front` wrote the first diagram's front onto the brief and every
    later diagram kept it as though the brief had stated it, with no line in its log. The briefs
    above carry no `context` at all, so `brief.get("context", {})` was a fresh dict on every call
    and these tests could not see it; the workbench's brief form always sends one. Two diagrams,
    in sequence, from one brief that carries a context and states no front: the double pile reads
    S, and the courtyard -- whose entry settles no front -- must still say so."""
    import copy
    brief = {**BRIEF, "context": {"lot_width_ft": 120, "climate_zone": "4A"}}
    before = copy.deepcopy(brief)
    first, log1, _p = CO.instantiate("centre-passage-double-pile", brief)
    second, log2, _p = CO.instantiate("courtyard-and-portal", brief)
    assert brief == before, "the brief came back changed"
    assert first["context"] is not brief["context"] and second["context"] is not first["context"]
    assert first["context"]["entrance_faces"] == "S"
    assert [l for l in log1 if l.startswith("JUDGMENT: the house is entered on its S front")]
    assert not second["context"].get("entrance_faces"), (
        "the courtyard took the double pile's front", second["context"].get("entrance_faces"))
    assert [l for l in log2 if l.startswith("DISCLOSURE: the diagram's entry does not settle")]
    assert second["context"]["lot_width_ft"] == 120, "the brief's own context still reaches the plan"


def test_a_composed_plan_validates_against_the_plan_schema():
    """The entrance front was first written as a LIST and the schema states one compass point;
    `geometry.entrance_walls` then raised on every composed plan. Nothing validated a composed
    record before it was placed."""
    import json
    import jsonschema
    schema = json.load(open(os.path.join(ROOT, "schema", "plan.schema.json"), encoding="utf-8"))
    for pid in ("foursquare-quadrant", "centre-passage-double-pile", "side-hall-townhouse", "bungalow-open-linear"):
        plan, _log, _p = CO.instantiate(pid, BRIEF)
        jsonschema.validate(plan, schema)


# --- R13 (Lucas, 30 Oct 2026, amended the same day): a formal passage is composed to the floor its
# own fault convicts at, read from the corpus. The kit's editorial floor stays the style layer's.
FG = json.load(open(os.path.join(ROOT, "briefs", "family-georgian.json"), encoding="utf-8"))


def _fault_threshold():
    f = json.load(open(os.path.join(ROOT, "faults", "passage-that-is-a-corridor.json"), encoding="utf-8"))
    return float(f["test"]["threshold"])


def test_a_formal_passage_is_composed_to_the_floor_its_fault_convicts_at():
    plan, log, _p = CO.instantiate("five-part-palladian", json.loads(json.dumps(FG)))
    rooms = _rooms(plan)
    floor = _fault_threshold()
    passage = rooms["passage"][1]
    assert min(passage["width_ft"], passage["length_ft"]) == floor, passage
    up = rooms["upperpassage"][1]
    assert up.get("stacks_over") == "passage" and min(up["width_ft"], up["length_ft"]) >= floor, (
        "the passage above follows the widened one")
    said = [l for l in log if l.startswith("Widened Centre Passage to")]
    assert said and "the floor it is judged by" in said[0] and "6.6 ft" in said[0], said
    d = [x for x in CO.structure_decisions(said) if x.get("field")]
    assert d and d[0]["field"] == "room_dims_ft" and "floor it is judged by" in d[0]["chose"], (
        "the decision log classifies the line", d)


def test_the_floor_is_read_from_the_fault_record_and_never_written(monkeypatch):
    import ast
    import inspect
    src = inspect.getsource(CO.passage_floor)
    nums = [n.value for n in ast.walk(ast.parse(src.strip())) if isinstance(n, ast.Constant)
            and isinstance(n.value, (int, float)) and not isinstance(n.value, bool)]
    assert not nums, f"passage_floor carries a number of its own: {nums}"
    CORE = CO._mod("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))
    real = CORE.get_fault

    def moved(fid, style=None):
        rec = real(fid, style)
        rec["test"] = {**rec["test"], "threshold": 9.25}
        return rec
    monkeypatch.setattr(CORE, "get_fault", moved)
    assert CO.passage_floor("tidewater-georgian")[0] == 9.25


def test_a_style_the_fault_does_not_convict_takes_no_floor(monkeypatch):
    assert CO.passage_floor("cape-cod-colonial")[0] is None
    CORE = CO._mod("tdlcore", os.path.join(ROOT, "mcp_server", "core.py"))
    real = CORE.get_fault
    cases = {"not-applicable": ({"severity": "not-applicable"}, None),
             "granted": ({"exception": {"granted": "granted"}}, None),
             "refused": ({"exception": {"granted": "refused"}}, _fault_threshold()),
             "unjudged": ({"exception": {"granted": "unjudged"}}, _fault_threshold())}
    for name, (patch, want) in cases.items():
        def fake(fid, style=None, _p=patch):
            rec = real(fid, style)
            rec["for_this_style"] = {**rec["for_this_style"], **_p}
            return rec
        monkeypatch.setattr(CORE, "get_fault", fake)
        assert CO.passage_floor("tidewater-georgian")[0] == want, name


def test_a_passage_already_at_its_floor_is_not_touched():
    plan, log, _p = CO.instantiate("centre-passage-single-pile", json.loads(json.dumps(FG)))
    passage = [r for _l, r in _rooms(plan).values() if r["type"] == "centre-passage"
               and not r.get("stacks_over")]
    assert passage, "the premise: the single pile composes a centre passage"
    if all(min(r["width_ft"], r["length_ft"]) >= _fault_threshold() for r in passage):
        assert not [l for l in log if l.startswith("Widened Centre Passage to")]
def test_a_composed_house_states_no_fire_so_its_hearth_is_unjudged():
    """THE PREMISE BEHIND "hearth unjudged" ON EVERY COMPOSED CANDIDATE (the audit of Phase 17,
    findings 17 and 44). No parti carries a `hearth` and the composer authors none, so on Lucas's
    brief the composed foursquare -- the house Phase 17 first drew -- states no fire, and
    `typefacts.hearth` reads it UNJUDGED with the reason "states no hearth", never held. Prose
    that calls that house's facts "every fact held" is wrong by this test; if a parti or the
    composer ever states a fire, this goes red and the sentences that say "hearth unjudged" have
    to be re-read rather than left to become silently false."""
    TF = modcache.load("typefacts", os.path.join(ROOT, "build", "typefacts.py"))
    plan, _log, _p = CO.instantiate("foursquare-quadrant", BRIEF)
    fires = [r["id"] for lv in plan["levels"] for r in lv["rooms"] if r.get("hearth")]
    assert fires == [], ("the composed foursquare states a fire now", fires)
    h = TF.hearth(plan)
    assert h["status"] == TF.UNJUDGED, h
    assert "states no hearth" in h["detail"], h["detail"]
    assert h["fires"] == [], h["fires"]


def test_a_floored_passage_is_held_at_its_floor_and_inside_its_area_band_at_every_size():
    """The audit of 30 Oct 2026, finding 1 of the composer pass: the growth loop's area correction
    scaled a widened cross-passage on both sides and handed it back at 7.98 x 20.05 -- under the
    floor R13 holds -- on `courtyard-and-portal`'s zaguan and `great-hall-h-plan`'s screens passage
    at 4,500-6,400 sf. Held now, its area off its length."""
    floor = _fault_threshold()
    seen = 0
    for pid, style in (("courtyard-and-portal", "spanish-colonial-revival"),
                       ("great-hall-h-plan", "jacobethan-revival"),
                       ("five-part-palladian", "tidewater-georgian")):
        assert CO.passage_floor(style)[0] == floor, ("the premise: the fault judges", style)
        for sf in (2400, 3200, 4500, 6400):
            plan, log, _p = CO.instantiate(pid, {"id": "x", "style": style, "target_area_sf": sf,
                                                 "bedrooms": 4, "bathrooms": 3})
            for _l, r in _rooms(plan).values():
                if r["type"] not in CO.PASSAGE_TYPES:
                    continue
                seen += 1
                assert min(r["width_ft"], r["length_ft"]) >= floor - 1e-9, (pid, sf, r["id"], r["width_ft"])
                area, *_ = CO._bands(r["type"])
                if area and not r.get("stacks_over"):
                    assert r["width_ft"] * r["length_ft"] <= area[1] + 0.1, (pid, sf, r["id"])
                    # the LONG side is kept (the tests auditor's mutation: length = floor drew an
                    # 8 x 8 passage, inside every assertion above) -- so the passage never falls
                    # under its own AREA floor. Not its length band: the composer hands the five-part
                    # its passage at 19.7 ft at 2,400 sf before R13 touches it.
                    assert r["width_ft"] * r["length_ft"] >= area[0] - 0.5, (pid, sf, r["id"])
    # 16 measured on this tree (three partis x four sizes); the floor is the premise that the sweep
    # reaches passages at all, not a figure the fix is judged by
    assert seen >= 16, seen


def test_the_new_log_lines_are_classified_and_a_judgments_disclosure_is_its_own_entry():
    """The audit of 30 Oct 2026, finding 7: "ROUND NOT BEGUN" read as an assumption, and a stacked
    room's DISCLOSURE tail reached no structured field."""
    d = CO.structure_decisions(["ROUND NOT BEGUN: 29.5 s of the 90 s budget was left (R12)."])
    assert [x["kind"] for x in d] == ["disclosure"]
    line = ("JUDGMENT (editorial): Landing takes the plan of Stair Hall, which it stands over, inside its "
            "own bands: 3 x 8 ft where its band midpoint gave 4 x 9 ft. DISCLOSURE: width 2.89 against "
            "[3, 8] -- it is composed so and said.")
    d = CO.structure_decisions([line])
    assert [x["kind"] for x in d] == ["judgment", "disclosure"], d
    assert d[1]["statement"].startswith("DISCLOSURE: width 2.89 against [3, 8]")
    d = CO.structure_decisions(["Shortened Zaguán to 20 ft inside its own area band, keeping it 8 ft "
                                "wide -- the floor it is judged by is 8 ft (x)."])
    assert d[0]["field"] == "room_dims_ft" and "8 x 20 ft" in d[0]["chose"], d
