"""WP-6.2. The opening grammar, the placement pass, and the drawn-house layer.

What is pinned here is the discipline rather than the numbers: an opening is either
placed or it says why not; a rule is either cited or the composer says it took a band's
midpoint; a plan nobody has placed reports COULD NOT EVALUATE on every drawn check and
never a pass.
"""
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
    """op-passage-axis, and the reported symptom in its exact form.

    styles/tidewater-georgian.json c03 is HARD — "exterior doors at both ends, aligned on
    axis and both operable" — and could not be satisfied, because a door had no wall: both
    renderers put every exterior door of a room on the FIRST wall it declared, so the
    passage's rear door was drawn on its front, under the front door, and the rear
    elevation showed a window where the door should be."""
    solved = GEO.solve(_plan("tidewater-georgian-careful"))
    passage = next(r for lv in solved["levels"] for r in lv["rooms"] if r["id"] == "passage")
    ext = [d for d in passage["doors"] if d["to"] == "exterior"]
    assert ext, "the passage declares an exterior door"
    assert ext[0].get("wall") == "N", \
        f"the passage's exterior door is on {ext[0].get('wall')}, not the rear wall"
    assert any(a.get("rule") == "op-passage-axis"
               for a in solved["opening_report"]["axis"]), "the axis rule did not fire"


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


def test_a_room_no_door_reaches_is_a_fatal_finding():
    """Nothing in this system has ever checked that you can walk from the front door to
    every room. build/check_partis.py's comment asserted the plan validator did; it did
    not, and a chamber bath whose only door the placement could not realise shipped on a
    reference sheet with no finding against it."""
    solved = GEO.solve(_plan("tidewater-georgian-careful"))
    res = PC.check(solved)
    d = res["drawn_summary"]
    assert d["evaluated"] is True
    assert d["unreachable"], "the Tidewater placement strands rooms; the layer must say so"
    assert "hallbath" in d["unreachable"], \
        "the chamber bath is the reported case and must be among them"
    fatals = [f for f in res["findings"] if f["layer"] == "drawn" and f["severity"] == "fatal"]
    assert len(fatals) == len(d["unreachable"])


def test_a_room_reachable_only_from_outdoors_is_named_as_such():
    """The first reported symptom: "the door to the kitchen is only from the outside, and
    the kitchen is connected to no other rooms". It passes reachability — it has its own
    exterior door — and it is still wrong, so it is its own finding rather than silence."""
    solved = GEO.solve(_plan("tidewater-georgian-careful"))
    res = PC.check(solved)
    assert "kitchen" in res["drawn_summary"]["cut_off"]
    said = [f for f in res["findings"]
            if f["layer"] == "drawn" and "only way in is from outside" in f["statement"]]
    assert said, "the kitchen's isolation must be stated, not merely counted"


def test_drawn_and_declared_sizes_are_reconciled_or_reported():
    """OQ 54's silence, closed. The sheet prints the PLACED rectangle and the record keeps
    the declared one; nothing said they differed, so a kitchen drawn at 63% of its declared
    area read as a measurement."""
    solved = GEO.solve(_plan("tidewater-georgian-careful"))
    res = PC.check(solved)
    diverged = {d["room"] for d in res["drawn_summary"]["diverged"]}
    assert "kitchen" in diverged, "the kitchen is drawn far under its declaration"
    assert "upperpassage" in diverged, "the upper passage is drawn far over its declaration"
