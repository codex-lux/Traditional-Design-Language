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


# THE STATUSES ARE MEASURED ONES, AND THE PASSING FIXTURE CARRIES THEM (the audit of Phase 17,
# 30 Oct 2026, finding 40). `_rec("heuristic")` carried no `type_facts` at all -- every fact
# UNJUDGED -- and the test that the search is drawn over a refused proof passed on it, so the guard
# certified exactly the substitution ruling 1 forbids: unjudged drawn as held. A search record now
# states the four statuses `typefacts.report` writes, and the proof states its own.
HELD = {"tiling": "held", "stacks": "held", "bearing": "held", "hearth": "held"}
PROOF_STATUS = dict(HELD, stacks="downgraded")


def _rec(engine, refused=None, rooms=None, status=None):
    rooms = rooms if rooms is not None else [_room("a", 0, 0, 12, 12, dw=12, dl=12),
                                             _room("b", 12, 0, 12, 12, dw=12, dl=12)]
    rep = {"solver": {"engine": engine, "status": "OPTIMAL"}}
    if refused:
        rep["refused"] = refused
    if status is None:
        status = PROOF_STATUS if refused else HELD
    if status:
        rep["type_facts"] = {"status": dict(status)}
    return {"id": "t", "footprint": {"width_ft": 24, "depth_ft": 12},
            "levels": [{"index": 0, "rooms": rooms}], "geometry_report": rep}


REFUSED = {"kind": "type-fact-downgraded", "facts": ["stacks"]}


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
    assert sv["facts"] == {"held": ["bearing", "hearth", "stacks", "tiling"], "unjudged": []}
    assert "holds every type fact" not in sv["reason"], "the reason is written from the statuses"


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
    """RE-CUT BY THE AUDIT OF PHASE 17 (30 Oct 2026, finding 8). This test hand-built records that
    already carried `unplaced` marks -- a shape production never hands this function, because
    `openings.place` writes those marks in `solve()` AFTER the substitution is decided. So on every
    real path both records read 0 unplaced doors here and the door half of ruling 6 could not fail,
    while this test drove the branch. The records are the real shape now: a declared door and NO
    marks, the search's two rooms 4 ft apart (no shared wall for the leaf) and the proof's abutting.
    The function must place the openings on copies of both before it counts."""
    gap = [_room("a", 0, 0, 10, 12, dw=10, dl=12, doors=[{"to": "b"}]),
           _room("b", 14, 0, 10, 12, dw=10, dl=12, doors=[{"to": "a"}])]
    abut = [_room("a", 0, 0, 12, 12, dw=10, dl=12, doors=[{"to": "b"}]),
            _room("b", 12, 0, 12, 12, dw=10, dl=12, doors=[{"to": "a"}])]
    alt, proof = _rec("heuristic", rooms=gap), _rec("cp-sat", REFUSED, rooms=abut)
    # the premise, both halves: unplaced, the counts cannot tell the two apart; placed, they do
    assert DR.never_downgrade(alt) == DR.never_downgrade(proof) == {
        "rooms_undersize": 0, "rooms_over_band": 0, "doors_unplaced": 0}
    OP = G._mod("openings", str(ROOT / "build" / "openings.py"))
    pa, pp = copy.deepcopy(alt), copy.deepcopy(proof)
    OP.place(pa, G.C)
    OP.place(pp, G.C)
    assert DR.never_downgrade(pa)["doors_unplaced"] == 1 and DR.never_downgrade(pp)["doors_unplaced"] == 0
    _with_search(monkeypatch, alt)
    assert G._the_search_where_it_holds_the_facts(proof, {}, None, 250, 7) is None


def test_the_doors_are_counted_on_placed_copies_and_the_returned_record_is_unplaced(monkeypatch):
    """The comparison places openings on COPIES; the record handed back is the search's own, which
    `solve()` places exactly as it places every result -- so a substituted record does not arrive
    with openings already on it, and the proof passed in is not written to."""
    abut = [_room("a", 0, 0, 12, 12, dw=10, dl=12, doors=[{"to": "b"}]),
            _room("b", 12, 0, 12, 12, dw=10, dl=12, doors=[{"to": "a"}])]
    _with_search(monkeypatch, _rec("heuristic", rooms=copy.deepcopy(abut)))
    proof = _rec("cp-sat", REFUSED, rooms=copy.deepcopy(abut))
    before = copy.deepcopy(proof)
    drawn = G._the_search_where_it_holds_the_facts(proof, {}, None, 250, 7)
    assert drawn is not None
    assert proof == before, "the proof handed in was written to"
    assert "opening_report" not in drawn, "the returned record carries the comparison's openings"
    assert drawn["geometry_report"]["solver"]["never_downgrade"]["drawn"]["doors_unplaced"] == 0


def test_where_the_openings_cannot_be_placed_the_doors_were_not_compared_and_the_proof_stays(monkeypatch):
    class _Raises:
        @staticmethod
        def place(plan, C=None):
            raise RuntimeError("no corpus")
    real = G._mod
    monkeypatch.setattr(G, "_mod", lambda n, p: _Raises if n == "openings" else real(n, p))
    _with_search(monkeypatch, _rec("heuristic"))
    proof = _rec("cp-sat", REFUSED)
    assert G._the_search_where_it_holds_the_facts(proof, {}, None, 250, 7) is None
    # AND THE PROOF SAYS WHY (the second audit of Phase 17, 30 Oct 2026): a fact-holding search
    # that could not be compared no longer vanishes in silence
    why = proof["geometry_report"]["solver"].get("search_not_compared")
    assert why and "RuntimeError: no corpus" in why and "stacks" in why, why


def test_a_search_that_does_not_hold_the_facts_leaves_no_comparison_note(monkeypatch):
    """The control: `search_not_compared` names a comparison that was owed and not made, so a search
    that never held the facts (and so was never to be compared) writes nothing."""
    _with_search(monkeypatch, _rec("heuristic", status=PROOF_STATUS))
    proof = _rec("cp-sat", REFUSED)
    assert G._the_search_where_it_holds_the_facts(proof, {}, None, 250, 7) is None
    assert "search_not_compared" not in proof["geometry_report"]["solver"]


def test_a_search_whose_refused_fact_is_only_unjudged_is_not_drawn(monkeypatch):
    """Finding 40: the proof MEASURED the stacks broken; a search that cannot judge them has not
    held them. No refusal on the search means nothing was downgraded -- unjudged does not refuse a
    drawing -- and that is right for the gate and wrong for ranking: ruling 1 says HOLDS."""
    _with_search(monkeypatch, _rec("heuristic", status=dict(HELD, stacks="unjudged")))
    assert G._the_search_where_it_holds_the_facts(_rec("cp-sat", REFUSED), {}, None, 250, 7) is None


def test_a_fact_the_proof_held_is_not_traded_for_one_the_search_cannot_judge(monkeypatch):
    """The proof held the bearing lines and was refused for its stacks; a search that holds the
    stacks and cannot judge the bearing has traded a measured fact for an unmeasured one, which is
    unjudged collapsed into held one fact over. Every fact the proof JUDGED must be held."""
    _with_search(monkeypatch, _rec("heuristic", status=dict(HELD, bearing="unjudged")))
    assert G._the_search_where_it_holds_the_facts(_rec("cp-sat", REFUSED), {}, None, 250, 7) is None


def test_a_fact_neither_placement_could_judge_is_named_unjudged_and_never_called_held(monkeypatch):
    """Finding 11: the reason said "the search's placement holds every type fact" whatever the
    search's statuses were -- and the hearth was unjudged on every composed run the audit made. A
    fact neither engine could judge (here a house stating no fire) does not block the substitution,
    because the proof could not judge it either; the reason NAMES it unjudged, and the record carries
    the two lists beside the sentence."""
    _with_search(monkeypatch, _rec("heuristic", status=dict(HELD, hearth="unjudged")))
    drawn = G._the_search_where_it_holds_the_facts(
        _rec("cp-sat", REFUSED, status=dict(PROOF_STATUS, hearth="unjudged")), {}, None, 250, 7)
    assert drawn is not None
    sv = drawn["geometry_report"]["solver"]
    assert sv["facts"] == {"held": ["bearing", "stacks", "tiling"], "unjudged": ["hearth"]}
    assert "holds every type fact" not in sv["reason"], sv["reason"]
    assert "hearth could not be judged on either placement" in sv["reason"], sv["reason"]
    assert "holds bearing, stacks, tiling, each measured held" in sv["reason"], sv["reason"]


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
