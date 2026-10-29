"""WP-17.6, rulings 1 and 6 of 29 Oct 2026: which placement `solve(engine="auto")` draws.

Ruling 1: a placement that holds the type's facts outranks one that releases them, whichever
engine (re-ruling 4 Sep). Ruling 6: two placements are compared on the NEVER-DOWNGRADE facts first
-- rooms drawn to their declared size, rooms inside their own band, doors placed -- and a house
that holds the facts by giving one of those up is never drawn. So the search's placement replaces a
REFUSED proof only where it holds every fact AND is no worse on each of the three counts.
"""
import copy
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = _mod("build/geometry.py", "geometry_fhw")
DR = _mod("build/drawability.py", "drawability_fhw")


def _room(rid, x, y, w, h, rtype="parlor", dw=None, dl=None, doors=None):
    r = {"id": rid, "type": rtype, "geometry": {"x_ft": x, "y_ft": y, "width_ft": w, "depth_ft": h}}
    if dw:
        r.update(width_ft=dw, length_ft=dl)
    if doors:
        r["doors"] = doors
    return r


def _rec(engine, refused=None, rooms=None):
    rooms = rooms if rooms is not None else [_room("a", 0, 0, 12, 12, dw=12, dl=12),
                                             _room("b", 12, 0, 12, 12, dw=12, dl=12)]
    rep = {"solver": {"engine": engine, "status": "OPTIMAL"}}
    if refused:
        rep["refused"] = refused
    return {"id": "t", "footprint": {"width_ft": 24, "depth_ft": 12},
            "levels": [{"index": 0, "rooms": rooms}], "geometry_report": rep}


REFUSED = {"kind": "downgraded", "facts": ["stacks"]}


def _with_search(monkeypatch, alt):
    calls = []

    def fake(plan, parti, candidates, seed):
        calls.append(1)
        return copy.deepcopy(alt)
    monkeypatch.setattr(G, "solve_heuristic", fake)
    return calls


def test_a_proof_that_may_be_drawn_is_drawn_and_the_search_is_not_run(monkeypatch):
    calls = _with_search(monkeypatch, _rec("heuristic"))
    assert G._the_search_where_it_holds_the_facts(_rec("cp-sat"), {}, None, 250, 7) is None
    assert calls == [], "the search costs nothing where the proof is not refused"


def test_a_refused_proof_gives_way_to_a_search_that_holds_the_facts_and_is_no_worse(monkeypatch):
    _with_search(monkeypatch, _rec("heuristic"))
    drawn = G._the_search_where_it_holds_the_facts(_rec("cp-sat", REFUSED), {}, None, 250, 7)
    assert drawn is not None
    sv = drawn["geometry_report"]["solver"]
    assert sv["engine"] == "heuristic" and sv["chosen_over_the_proof"] is True
    assert sv["proof"]["refused"] == REFUSED, "the proof's refusal travels with the drawing"
    assert set(sv["never_downgrade"]) == {"drawn", "proof"}
    assert "stacks" in sv["reason"]


def test_a_search_that_is_refused_too_is_not_drawn(monkeypatch):
    _with_search(monkeypatch, _rec("heuristic", {"kind": "downgraded", "facts": ["tiling"]}))
    assert G._the_search_where_it_holds_the_facts(_rec("cp-sat", REFUSED), {}, None, 250, 7) is None


def test_a_search_that_holds_the_facts_by_drawing_a_room_past_its_band_is_not_drawn(monkeypatch):
    ceil, src = G.shape_band("dining-room")
    assert src == "corpus"
    sliver = [_room("a", 0, 0, 30, 6, "dining-room", dw=12, dl=14), _room("b", 0, 6, 12, 12, dw=12, dl=12)]
    _with_search(monkeypatch, _rec("heuristic", rooms=sliver))
    assert DR.never_downgrade(_rec("heuristic", rooms=sliver)) == {
        "rooms_undersize": 0, "rooms_over_band": 1, "doors_unplaced": 0}, "the premise: band alone"
    assert G._the_search_where_it_holds_the_facts(_rec("cp-sat", REFUSED), {}, None, 250, 7) is None


def test_a_search_that_holds_the_facts_by_shrinking_a_room_is_not_drawn(monkeypatch):
    small = [_room("a", 0, 0, 9, 12, dw=12, dl=12), _room("b", 9, 0, 15, 12, dw=12, dl=12)]
    _with_search(monkeypatch, _rec("heuristic", rooms=small))
    assert DR.never_downgrade(_rec("heuristic", rooms=small))["rooms_undersize"] == 1
    assert G._the_search_where_it_holds_the_facts(_rec("cp-sat", REFUSED), {}, None, 250, 7) is None


def test_a_search_that_holds_the_facts_by_leaving_a_door_unplaced_is_not_drawn(monkeypatch):
    rooms = [_room("a", 0, 0, 12, 12, dw=12, dl=12, doors=[{"to": "b", "unplaced": {"why": "x"}}]),
             _room("b", 12, 0, 12, 12, dw=12, dl=12, doors=[{"to": "a", "unplaced": {"why": "x"}}])]
    _with_search(monkeypatch, _rec("heuristic", rooms=rooms))
    assert G._the_search_where_it_holds_the_facts(_rec("cp-sat", REFUSED), {}, None, 250, 7) is None


def test_the_counts_are_compared_one_by_one_and_never_summed():
    """A placement that buys a door with a room out of band is not no-worse, even though its total
    is the same."""
    a = _rec("heuristic", rooms=[_room("a", 0, 0, 30, 6, "dining-room", dw=12, dl=14),
                                 _room("b", 0, 6, 12, 12, dw=12, dl=12)])
    b = _rec("cp-sat", rooms=[_room("a", 0, 0, 12, 12, dw=12, dl=12, doors=[{"to": "b", "unplaced": {"why": "x"}}]),
                              _room("b", 12, 0, 12, 12, doors=[{"to": "a", "unplaced": {"why": "x"}}])])
    ok, na, nb = DR.no_worse(a, b)
    assert sum(na.values()) == sum(nb.values()) and not ok


def test_only_auto_takes_the_search_and_a_forced_proof_never_does():
    import inspect
    src = inspect.getsource(G._solve_uncached)
    assert 'if engine == "auto":\n        drawn = _the_search_where_it_holds_the_facts(' in src
