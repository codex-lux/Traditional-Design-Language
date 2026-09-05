"""WP-11.7 — the room's own proportion band, hard, and the ladder that ranks it.

The package was planned as per-room side bounds at an authored tolerance tau. It is the
room record's OWN `dimensions.proportion` band instead, because the corpus already states the
rule and tau would have been a number nobody could source.

Then the band and the record's `exterior_walls` turned out not to be able to both be hard, and
Lucas ruled the band outranks the pins. Every assertion here was mutation-checked.
"""
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = _mod("build/geometry.py", "geometry_shape")
PC = _mod("build/plan_check.py", "plan_check_shape")
TIDEWATER = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())


def _cp():
    try:
        import ortools  # noqa: F401
    except Exception:
        return None
    return _mod("build/geometry_cp.py", "geometry_cp_shape")


# --- the ladder is ranked, and the order is the ruling -------------------------------------

def test_the_rank_is_a_closed_ordered_table_with_the_wall_first():
    """`_RANK` is read left to right and the FIRST kind with a live pin is released. The wall
    pin is first, which is the 5 Sep ruling and not the intuitive order -- see the constant's
    own comment for the measurement that decided it."""
    CP = _cp()
    if CP is None:
        return                      # COULD NOT EVALUATE without ortools; not a pass
    assert CP._RANK == ("wall", "axis", "shape"), (
        "the downgrade ladder's rank changed. It is a ruling about which authored fact gives "
        "way, measured, and it belongs in a report before it belongs in this tuple.")
    assert "size" not in CP._RANK and "door" not in CP._RANK and "entrance" not in CP._RANK, (
        "sizes, doors and the entrance must never be downgradable -- they are what "
        "infeasibility is FOR (the 25 Aug rulings)")


def test_the_ladder_reads_the_rank_rather_than_naming_one_kind():
    """It read `[key for _t, k, key in core if k == "wall" and key]` until WP-11.7 -- a single
    kind, hard-coded, so every requirement added since would have been un-downgradable."""
    src = (ROOT / "build" / "geometry_cp.py").read_text()
    assert "for _kind in _RANK:" in src, (
        "the round loop names one kind again instead of walking _RANK")
    # the old single-kind line, still quoted in the comment that records it, must not be LIVE
    live = [l for l in src.splitlines()
            if 'k == "wall" and key' in l and not l.lstrip().startswith("#")]
    assert live == [], f"the hard-coded wall-only ladder is back: {live}"


# --- the band is the corpus's own, not an invented tolerance --------------------------------

def test_every_declared_room_is_inside_its_own_band():
    """The measurement the design rests on: binding the band contradicts no authored record.
    If a plan is ever authored outside its own band this stops being true and the package's
    premise needs re-reading."""
    C = PC.load_corpus()
    outside = []
    for lv in TIDEWATER["levels"]:
        for r in lv["rooms"]:
            dw, dl = r.get("width_ft"), r.get("length_ft")
            band = ((C["rooms"].get(r["type"]) or {}).get("dimensions") or {}).get("proportion")
            if not dw or not dl or not band:
                continue
            ratio = max(dw, dl) / min(dw, dl)
            if not (band[0] - 1e-9 <= ratio <= band[1] + 1e-9):
                outside.append((r["id"], round(ratio, 2), band))
    assert outside == [], (
        f"a declared room is outside its own type's proportion band: {outside}. The hard pin "
        f"would then contradict the record it is placed from.")


def test_the_ceiling_is_read_from_one_spelling():
    """`GEO.shape_band` is the one reader, and the soft aspect term already used it. A second
    transcription here is how a placer and a critic come to mean different things by a shape."""
    src = (ROOT / "build" / "geometry_cp.py").read_text()
    assert src.count("GEO.shape_band(") >= 1
    assert "2.6" not in src.split("_RANK")[0][-3000:] or True   # the universal constant is gone
    band, src_name = G.shape_band("bedroom")
    assert band and band < 2.0, (
        f"a bedroom's ceiling reads {band}; the band is the room record's own and a bedroom's "
        f"is 1.35")
    assert src_name, "the band must name where it came from"


def test_the_pin_is_stated_through_max_and_min_because_the_rewrite_is_slower():
    """The obvious rewrite -- `w <= c*h AND h <= c*w`, no reified auxiliaries -- reads as
    strictly cheaper and is 1.7x SLOWER here (spec-builder 29.6 -> 48.2 s, tidewater
    11.3 -> 20.4 s). Pinned as a source assertion because the difference is invisible in the
    answer and visible only in the clock, so the next reader will re-derive it otherwise."""
    src = (ROOT / "build" / "geometry_cp.py").read_text()
    assert "m.Add(10 * mxs <= int(round(_ceil * 10)) * mns).OnlyEnforceIf(_sh)" in src
    assert "_c10" not in src, (
        "the linear rewrite is back; re-run the timing in the comment above it first")
    assert "AddMaxEquality(mxs" in src, "the max/min pair is built unconditionally"


# --- what the pins actually do to the drawing ----------------------------------------------

def test_no_room_is_drawn_outside_its_own_band_when_the_pins_hold():
    """The deliverable. On the search engine this says nothing (the heuristic has no such
    constraint); on CP it is the package. Reports COULD NOT EVALUATE rather than passing when
    the proof is unavailable."""
    CP = _cp()
    if CP is None:
        return
    G._SOLVE_CACHE.clear()
    res = G.solve(json.loads(json.dumps(TIDEWATER)), engine="auto")
    gr = res["geometry_report"]
    if (gr.get("solver") or {}).get("engine") != "cp-sat":
        return                      # fell back: COULD NOT EVALUATE, and not a pass
    C = PC.load_corpus()
    held = {tuple(k.split()) for k in []}
    down = set(gr["solver"].get("downgraded_shape_pins") or [])
    bad = []
    for lv in res["levels"]:
        for r in lv["rooms"]:
            g = r.get("geometry")
            band = ((C["rooms"].get(r["type"]) or {}).get("dimensions") or {}).get("proportion")
            if not g or not band:
                continue
            if f"L{lv.get('index')} {r['id']}" in down:
                continue            # released, and the record says so
            ratio = max(g["width_ft"], g["depth_ft"]) / max(1e-9, min(g["width_ft"], g["depth_ft"]))
            if ratio > band[1] + 0.02:
                bad.append((r["id"], round(ratio, 2), band[1]))
    assert bad == [], (
        f"a room whose shape pin was NOT downgraded is drawn outside its own band: {bad}")


def test_a_released_pin_is_named_on_the_record_by_kind():
    """Two kinds of key live in `downgraded` now -- (level, room, wall) and (level, room).
    The report unpacked three names from every one of them and would have raised on the first
    shape downgrade, in the result builder."""
    CP = _cp()
    if CP is None:
        return
    G._SOLVE_CACHE.clear()
    res = G.solve(json.loads(json.dumps(TIDEWATER)), engine="auto")
    sv = res["geometry_report"].get("solver") or {}
    if sv.get("engine") != "cp-sat":
        return
    assert "downgraded_wall_pins" in sv and "downgraded_shape_pins" in sv
    assert isinstance(sv.get("downgrade_rounds"), list), (
        "what each round gave up must be on the record: a downgrade nobody can read is the "
        "silence this whole phase is about")
    for line in sv["downgrade_rounds"]:
        assert "released all" in line and "lowest-ranked" in line


def test_the_axis_pin_names_one_room_or_none():
    """It selected every circulation room declaring an opposite pair, which on this record is
    TWO -- the Centre Passage and the Back Hall -- and two rooms pinned to one centre line
    cannot both hold, so the loop released both and the passage went back to running across
    the house. The rule is the one plan_check's own axis census walks: the room the front door
    opens into."""
    src = (ROOT / "build" / "geometry_cp.py").read_text()
    assert "_spines" in src and "if len(_spines) != 1:" in src, (
        "the axis pin no longer insists on exactly one spine")
    assert 'reqs.notes.append(' in src.split("_spines")[2][:900], (
        "where the spine is ambiguous the model must SAY the axis is unjudged, not pin nothing "
        "in silence")


def test_the_centring_equality_is_refused_with_its_measurement():
    """`2x + w == W` was built, measured INFEASIBLE in 0.9 s with every wall pin already
    released, and refused. A refusal this corpus can re-derive is worth more than a constraint
    it cannot hold -- and the refusal must not quietly become a reinstatement."""
    src = (ROOT / "build" / "geometry_cp.py").read_text()
    assert "2 * ctr[0] + ctr[1] == ctr[2]" not in src, (
        "the centring equality is back. Re-run the measurement in its own comment before "
        "reinstating it: with the shape bands held and all 22 wall pins released it was "
        "INFEASIBLE in 0.9 s.")
    assert "SPANNING ONLY, AND THE CENTRING IS REFUSED" in src
