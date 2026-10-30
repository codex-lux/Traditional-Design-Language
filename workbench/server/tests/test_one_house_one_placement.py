"""PHASE 17, WP-17.3: ONE HOUSE, ONE PLACEMENT.

A composed candidate is placed by the composer at its own budget, and that placement is the house
its card describes. The bench re-solved every record it was sent at the interactive budget, so a
candidate the composer found drawable could come back refused on the bench, and the Drawing Set --
which keeps a carried placement -- drew a third house beside them. Every placement now carries the
digest of the declared record it was placed from (`geometry_report.solver.input_digest`), and a
surface keeps a carried placement exactly where that digest matches what the record declares now:
the composer's house is drawn as composed, and a record edited since is re-solved, never drawn on
the rectangles of the house before the edit.
"""
import copy
import os

from . import drawable

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _geo():
    from mcp_server import core
    return core._mod("geometry", os.path.join(ROOT, "build", "geometry.py"))


def _placed_heuristic(monkeypatch):
    geo = _geo()
    monkeypatch.setattr(geo, "_SOLVE_CACHE", {})
    plan = drawable.drawable_plan()
    out = geo.solve(copy.deepcopy(plan), engine="heuristic")
    assert "error" not in out
    # the server produced this placement: registered, as `_placed`, evaluate and a compose job
    # register theirs (the audit of Phase 17 -- only a placement the server produced is carried)
    from workbench.server import corpus
    corpus.remember_placement(out)
    return geo, plan, out


def test_every_placement_names_the_declared_record_it_is_of(monkeypatch):
    geo, plan, out = _placed_heuristic(monkeypatch)
    dig = out["geometry_report"]["solver"]["input_digest"]
    assert dig == geo.declared_digest(plan) == geo.declared_digest(out)
    assert geo.carries_its_own_placement(out)
    assert not geo.carries_its_own_placement(plan), "a declared record carries no placement"


def test_an_edit_breaks_the_match_and_a_placement_step_does_not(monkeypatch):
    geo, plan, out = _placed_heuristic(monkeypatch)
    edited = copy.deepcopy(out)
    r = edited["levels"][0]["rooms"][0]
    r["width_ft"] = (r.get("width_ft") or 10) + 1
    assert not geo.carries_its_own_placement(edited)
    # moving a rectangle is not an edit of the declared record -- the placement's own keys are not
    # in the digest -- and nor is the revision loop's account of itself
    moved = copy.deepcopy(out)
    moved["levels"][0]["rooms"][0]["geometry"]["x_ft"] += 1.0
    moved["revision_report"] = {"summary": {}}
    assert geo.carries_its_own_placement(moved)
    unstamped = copy.deepcopy(out)
    unstamped["geometry_report"]["solver"].pop("input_digest")
    assert not geo.carries_its_own_placement(unstamped), "a placement that names no record is not kept"


def test_the_bench_keeps_a_placement_of_the_record_and_rejudges_it(monkeypatch):
    from workbench.server import corpus, evaluate
    geo, plan, out = _placed_heuristic(monkeypatch)
    calls = []
    real = geo.solve

    def spy(*a, **kw):
        calls.append(kw.get("engine"))
        return real(*a, **kw)
    monkeypatch.setattr(geo, "solve", spy)
    res = evaluate.evaluate(copy.deepcopy(out), place=True, engine="auto")
    assert calls == [], "a placement of the record itself is not re-solved"
    assert "error" not in res["check"], res["check"].get("error")
    # a forged verdict on the posted record is not read: since the audit of Phase 17 a record whose
    # whole digest the server did not produce is not carried at all, and is re-solved
    posted = copy.deepcopy(out)
    posted["geometry_report"]["refused"] = {"kind": "forged", "facts": ["tiling"]}
    assert corpus.carried(posted)["state"] == corpus.NOT_CARRIED
    got = corpus.carried(copy.deepcopy(out))
    assert got["state"] == corpus.CARRIED, got
    kept = got["record"]
    assert ([r.get("geometry") for lv in kept["levels"] for r in lv["rooms"]]
            == [r.get("geometry") for lv in out["levels"] for r in lv["rooms"]])


def test_the_bench_resolves_an_edited_record_and_the_drag_always_searches(monkeypatch):
    from workbench.server import evaluate
    geo, plan, out = _placed_heuristic(monkeypatch)
    calls = []
    real = geo.solve

    def spy(*a, **kw):
        calls.append(kw.get("engine"))
        return real(*a, **kw)
    monkeypatch.setattr(geo, "solve", spy)
    edited = copy.deepcopy(out)
    edited["levels"][0]["rooms"][0]["width_ft"] = (edited["levels"][0]["rooms"][0].get("width_ft") or 10) + 1
    evaluate.evaluate(edited, place=True, engine="heuristic")
    evaluate.evaluate(copy.deepcopy(out), place=True, engine="heuristic")
    assert calls == ["heuristic", "heuristic"], "an edit is re-solved, and the drag asks for the search by name"


def test_the_drawing_set_redraws_a_record_edited_since_its_placement(monkeypatch):
    from workbench.server import corpus
    geo, plan, out = _placed_heuristic(monkeypatch)
    same = corpus._placed(copy.deepcopy(out), None, 250)
    assert ([r.get("geometry") for lv in same["levels"] for r in lv["rooms"]]
            == [r.get("geometry") for lv in out["levels"] for r in lv["rooms"]]), \
        "a placement of the record itself is drawn as it stands"
    edited = copy.deepcopy(out)
    rid = edited["levels"][0]["rooms"][0]["id"]
    edited["levels"][0]["rooms"][0]["width_ft"] = (edited["levels"][0]["rooms"][0].get("width_ft") or 10) + 1
    redrawn = corpus._placed(edited, None, 250)
    assert "error" not in redrawn
    assert redrawn["geometry_report"]["solver"]["input_digest"] == geo.declared_digest(edited), \
        "the edited record is placed again, and the new placement names the edited record"
    assert redrawn["geometry_report"]["solver"]["input_digest"] != out["geometry_report"]["solver"]["input_digest"]
    assert any(r["id"] == rid for lv in redrawn["levels"] for r in lv["rooms"])


def _through_the_browser(rec):
    """What the bench does to a record: it holds it as a JavaScript object, which has one number
    type, and posts it back with `JSON.stringify`, so an integral float comes back an integer."""
    import json
    return json.loads(json.dumps(rec), parse_float=lambda s: int(float(s)) if float(s).is_integer() else float(s))


def test_a_placement_survives_the_browsers_round_trip(monkeypatch):
    """THE AUDIT OF PHASE 17 (30 Oct 2026). Every test above posts a Python dict, which keeps `9.0`
    a float; the browser does not, and the digest told `9.0` from `9`, so the bench re-solved every
    composed candidate it was sent. Held on the composer's own record (45 integral floats on the
    foursquare) and on a placed record taken through the browser and back to the server."""
    from workbench.server import corpus
    geo, plan, out = _placed_heuristic(monkeypatch)
    import sys
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
    composed, _log, _p = CO.instantiate("foursquare-quadrant", {"id": "t", "style": "tidewater-georgian",
                                                                 "target_area_sf": 3200, "bedrooms": 4,
                                                                 "bathrooms": 3.5})
    back = _through_the_browser(composed)
    import json
    assert json.dumps(back, sort_keys=True) != json.dumps(composed, sort_keys=True), \
        "the premise: the round trip changes the record's text"
    assert geo.declared_digest(back) == geo.declared_digest(composed)
    posted = _through_the_browser(out)
    assert geo.carries_its_own_placement(posted), "a placement taken through the browser is still of its record"
    got = corpus.carried(posted)
    assert got["state"] == corpus.CARRIED, "the bench keeps the placement the browser posted back"
    # and a real edit still breaks it after the round trip
    posted["levels"][0]["rooms"][0]["width_ft"] = (posted["levels"][0]["rooms"][0].get("width_ft") or 10) + 1
    assert not geo.carries_its_own_placement(posted)


# ------------------------------------------------------------- the audit of Phase 17 (30 Oct 2026)
def _stub_solve(monkeypatch, geo):
    """A solve that records the engine it was asked for and places nothing -- these tests are about
    WHETHER the route solves, not what a solve returns, so they cost no solve at all."""
    calls = []

    def stub(*a, **kw):
        calls.append(kw.get("engine"))
        return {"error": "stub: this test asks whether a solve was called, not what it returns"}
    monkeypatch.setattr(geo, "solve", stub)
    return calls


def test_prove_placement_and_re_solve_solve_a_record_that_carries_its_own_placement(monkeypatch):
    """FINDING 24. 'Prove placement (CP-SAT)' posts `engine: 'cp'` and re-solve posts `auto` WITH
    corrective rounds; both are acts the reader asks for, and both carried the composer's placement
    back unchanged -- the searched house redrawn under the plate's own "Prove placement above is the
    act that proves it". Only the open path (`auto`, no rounds) carries.
    Mutation: carry on `engine != "heuristic"` again -- the first two go red."""
    from workbench.server import evaluate
    geo, plan, out = _placed_heuristic(monkeypatch)
    calls = _stub_solve(monkeypatch, geo)
    evaluate.evaluate(copy.deepcopy(out), place=True, engine="cp")
    assert calls == ["cp"], f"prove placement must solve on CP-SAT, and solved {calls}"
    calls.clear()
    evaluate.evaluate(copy.deepcopy(out), place=True, engine="auto", revise_rounds=2)
    assert calls[:1] == ["auto"], f"re-solve must solve the record afresh before its rounds, and solved {calls}"
    calls.clear()
    res = evaluate.evaluate(copy.deepcopy(out), place=True, engine="auto")
    assert calls == [], "opening a candidate (auto, no rounds) still keeps its own placement (WP-17.3)"
    assert "placement" in res or "placement_refused" in res


def _tidewater_heuristic(monkeypatch):
    import json
    geo = _geo()
    monkeypatch.setattr(geo, "_SOLVE_CACHE", {})
    p = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    out = geo.solve(copy.deepcopy(p), engine="heuristic")
    assert "error" not in out
    from workbench.server import corpus
    corpus.remember_placement(out)
    facts = (out["geometry_report"].get("refused") or {}).get("facts") or []
    assert "stacks" in facts, f"the premise: this placement is refused for its stacks ({facts})"
    return geo, out


def test_a_carried_placement_re_derives_the_stacking_tally_it_is_judged_on(monkeypatch):
    """FINDINGS 25, 30, 45. `typefacts.stacks` READS `geometry_report.stacking`, and the carried path
    handed it the POSTED tally: deleted, stacks read UNJUDGED (which never refuses); with the broken
    claims moved under `kept`, HELD. Either way a house refused for its stacks was drawn. The tally
    is re-derived before the facts are judged, so all three posted forms are judged as placed.
    Mutation: drop the `stacking_report` line in `corpus.carried` -- red."""
    from workbench.server import corpus
    geo, out = _tidewater_heuristic(monkeypatch)
    truth = sorted(out["geometry_report"]["refused"]["facts"])
    deleted = copy.deepcopy(out)
    deleted["geometry_report"].pop("stacking")
    moved = copy.deepcopy(out)
    st = moved["geometry_report"]["stacking"]
    st["kept"], st["broken"] = (st.get("kept") or []) + (st.get("broken") or []), []
    blanked = copy.deepcopy(out)
    blanked["geometry_report"]["stacking"] = {"claims": 0, "kept": [], "broken": [], "unjudged": []}
    blanked["geometry_report"]["refused"] = None
    for name, rec in (("tally deleted", deleted), ("broken moved to kept", moved),
                      ("tally emptied and refusal cleared", blanked)):
        # a client's forgery is not carried at all (the registry, the audit of Phase 17) ...
        assert corpus.carried(rec)["state"] == corpus.NOT_CARRIED, name
        # ... and the re-derivation stays as defence in depth: even a record the server itself
        # had registered is judged on a tally derived here, never on the one it carries
        corpus.remember_placement(rec)
        got = corpus.carried(rec)
        assert got["state"] == corpus.CARRIED, (name, got)
        ref = got["record"]["geometry_report"].get("refused") or {}
        assert sorted(ref.get("facts") or []) == truth, (
            f"{name}: carried refused for {ref.get('facts')} against the placement's own {truth}")
        assert got["record"]["geometry_report"]["type_facts"]["status"]["stacks"] == "downgraded", name


def test_a_stale_tally_on_a_drawable_record_is_refused_for_the_stack_it_breaks(monkeypatch):
    """FINDING 25's constructed case, through the route. A drawable record, a `stacks_over` claim its
    rectangles break added to the declared half, the input digest re-stamped as any client can (the
    digest is an unkeyed hash), and the OLD tally left on: the stale tally names no such claim, so the
    house was answered `placement` and the Drawing Set drew it. Mutation: as above."""
    import json
    from workbench.server import corpus, evaluate
    geo = _geo()
    monkeypatch.setattr(geo, "_SOLVE_CACHE", {})
    p = json.load(open(os.path.join(ROOT, "plans", "reference", "bad-03-narrow-lot-townhome.json")))
    out = geo.solve(copy.deepcopy(p), engine="heuristic")
    assert "error" not in out and not out["geometry_report"].get("refused"), "the premise: drawable"
    rects = {r["id"]: r["geometry"] for lv in out["levels"] for r in lv["rooms"] if r.get("geometry")}
    ground = sorted(r["id"] for r in out["levels"][0]["rooms"] if r.get("geometry"))

    def overlap(a, b):
        ix = min(a["x_ft"] + a["width_ft"], b["x_ft"] + b["width_ft"]) - max(a["x_ft"], b["x_ft"])
        iy = min(a["y_ft"] + a["depth_ft"], b["y_ft"] + b["depth_ft"]) - max(a["y_ft"], b["y_ft"])
        return max(0.0, ix) * max(0.0, iy)
    pair = next(((u["id"], d) for u in out["levels"][1]["rooms"] if u.get("geometry")
                 for d in ground if overlap(rects[u["id"]], rects[d]) == 0.0), None)
    assert pair, "the premise: some upper room stands clear of some ground room"
    up, down = pair
    forged = copy.deepcopy(out)
    for r in forged["levels"][1]["rooms"]:
        if r["id"] == up:
            r["stacks_over"] = down
    forged["geometry_report"]["solver"]["input_digest"] = geo.declared_digest(forged)
    assert geo.carries_its_own_placement(forged), "the premise: a client can re-stamp the digest"
    # the registry (the audit of Phase 17): a re-stamped record is not one the server produced,
    # so it is not carried, and both surfaces place it afresh rather than draw it
    assert corpus.carried(forged)["state"] == corpus.NOT_CARRIED
    calls = _stub_solve(monkeypatch, geo)
    evaluate.evaluate(copy.deepcopy(forged), place=True, engine="auto")
    assert calls == ["auto"], f"the bench must re-solve a forged record, and solved {calls}"
    corpus.forget_recent_placements()
    corpus._placed(copy.deepcopy(forged), None, 250)
    assert calls == ["auto", "auto"], f"the Drawing Set must re-solve it too, and solved {calls}"
    # defence in depth: were such a record ever registered, the re-judge still refuses its stack
    corpus.remember_placement(forged)
    got = corpus.carried(forged)
    assert got["state"] == corpus.CARRIED
    assert "stacks" in ((got["record"]["geometry_report"].get("refused") or {}).get("facts") or []), \
        "the stack the declared record claims and the rectangles break is judged and refused"


def test_a_carried_placement_withholds_the_solver_claim_it_arrived_with(monkeypatch):
    """FINDINGS 25 AND 45, RULED R11 (30 Oct 2026). The solver block on a carried record is the posted
    record's word, and a forged `cp-sat`/`OPTIMAL` printed PLACEMENT PROVED over hand-moved
    rectangles. The server replaces it: `carried: true`, the verified digest, the NAMES of what was
    withheld and never their values, and the plate's line says carried, not proved.
    Mutation: return the client's solver block untouched -- red."""
    from mcp_server import core
    from workbench.server import corpus, evaluate
    geo, plan, out = _placed_heuristic(monkeypatch)
    forged = copy.deepcopy(out)
    forged["geometry_report"]["solver"].update(engine="cp-sat", status="OPTIMAL", objective=1.0,
                                              downgraded_wall_pins=[], alternative={"verdict": "x"})
    got = corpus.carried(forged)
    assert got["state"] == corpus.CARRIED
    sv = got["record"]["geometry_report"]["solver"]
    assert sv["carried"] is True and sv["engine"] == "carried"
    assert sv["input_digest"] == geo.declared_digest(forged)
    for k in ("status", "objective", "downgraded_wall_pins", "alternative"):
        assert k not in sv, f"the withheld claim's {k} rode through"
        assert k in sv["withheld"], f"the withheld claim's {k} is not named as withheld"
    assert geo.carries_its_own_placement(got["record"]), "the server's own record is carried again"
    again = corpus.carried(got["record"])
    assert again["record"]["geometry_report"]["solver"]["withheld"] == sv["withheld"], \
        "a record that went round once keeps the names of what was withheld"
    disc = core.placement_summary(got["record"])["disclosures"]
    assert not any("PLACEMENT PROVED" in d["text"] for d in disc), [d["text"] for d in disc]
    eng = [d["text"] for d in disc if d.get("id") == "engine"]
    assert eng and eng[0].startswith("PLACEMENT CARRIED") and "WITHHELD" in eng[0], eng
    assert not any(w in eng[0] for w in ("HILL-CLIMB", "SEARCHED", "CP-SAT")), \
        f"a carried placement's line names an engine it was not solved by here: {eng[0]}"
    calls = _stub_solve(monkeypatch, geo)
    res = evaluate.evaluate(copy.deepcopy(forged), place=True, engine="auto")
    assert calls == [] and "placement" in res, sorted(res)
    assert res["placement"]["geometry_report"]["solver"].get("carried") is True
    assert not any("PLACEMENT PROVED" in d["text"] for d in res["placement"]["disclosures"])


def test_one_reader_of_a_carried_placement_and_one_answer_when_it_cannot_be_judged(monkeypatch):
    """FINDING 28. The bench (`corpus.carried`) and the Drawing Set (`_placed`'s inline copy) disagreed
    on a carried placement that cannot be judged: the bench re-solved it in silence and drew another
    house, the Drawing Set refused. One reader now, and one answer: could not be judged, with the
    reason, and no solve. Mutation: re-inline `judge` in `_placed` -- the source guard goes red."""
    import inspect
    from workbench.server import corpus, evaluate
    geo, plan, out = _placed_heuristic(monkeypatch)
    TF = corpus._typefacts()

    def boom(p):
        raise RuntimeError("judge cannot measure this record")
    monkeypatch.setattr(TF, "judge", boom)
    got = corpus.carried(copy.deepcopy(out))
    assert got["state"] == corpus.CARRIED_UNJUDGED and "could not be judged" in got["reason"]
    calls = _stub_solve(monkeypatch, geo)
    res = evaluate.evaluate(copy.deepcopy(out), place=True, engine="auto")
    assert calls == [], "an unjudgeable carried placement is not re-solved in silence"
    assert "placement" not in res and "could not be judged" in (res.get("placement_error") or ""), sorted(res)
    drawn = corpus._placed(copy.deepcopy(out), None, 250)
    assert drawn.get("unsolved") and drawn["error"] == got["reason"], drawn
    src = inspect.getsource(corpus._placed)
    assert "carried(plan)" in src and ".judge(" not in src, \
        "_placed must read a carried placement through `carried`, not its own copy of the rule"


def test_the_drawing_set_stamps_who_drew_a_carried_placement_and_leaves_its_argument(monkeypatch):
    """FINDING 28's other halves: the carried branch wrote no `drawn_by` (the Drawing Set's
    one-input reader saw none, or the client's), and judged the caller's dict in place."""
    from workbench.server import corpus
    geo, plan, out = _placed_heuristic(monkeypatch)
    arg = copy.deepcopy(out)
    before = copy.deepcopy(arg)
    drawn = corpus._placed(arg, None, 250)
    assert arg == before, "the caller's record is not judged in place"
    db = drawn["geometry_report"]["solver"].get("drawn_by") or {}
    assert db.get("input_digest") and db.get("engine_requested") == "carried", db


def test_a_composed_candidate_carries_its_own_placement(monkeypatch):
    """FINDING 35. WP-17.3's headline -- a composed candidate is drawn as composed -- rests on the join
    between the composer's LAST write to a card's declared record and the digest `geometry.solve`
    stamped; every test above places a shipped plan directly, so a composer write after the final
    placement would have broken every card and the bench would have re-solved each, with this file
    green. Composed here, and held through the browser's round trip and the server's reader.
    Mutation: a `context` write after `plan2 = rv["plan"]` in `compose._revise_one` -- red."""
    import json
    import sys
    from workbench.server import corpus
    geo = _geo()
    monkeypatch.setattr(geo, "_SOLVE_CACHE", {})
    sys.path.insert(0, os.path.join(ROOT, "build"))
    import modcache
    CO = modcache.load("compose", os.path.join(ROOT, "build", "compose.py"))
    brief = json.load(open(os.path.join(ROOT, "briefs", "bungalow-small.json")))
    res = CO.compose(brief, candidates=2, revise=True, revise_rounds=1, revise_engine="heuristic")
    from workbench.server import jobs
    corpus.forget_placements()
    jobs._remember_plans(res)          # what a compose job does with its result, before a reader can fetch it
    cards = [c for c in res["candidates"] if c.get("revision")]
    assert cards, "the premise: some card was placed by the revision loop"
    for c in cards:
        rec = c["plan"]
        assert any(r.get("geometry") for lv in rec["levels"] for r in lv["rooms"]), \
            f"the premise: {c.get('parti')} carries a placement"
        assert geo.carries_its_own_placement(rec), f"{c.get('parti')}: the card's placement is not of its record"
        posted = _through_the_browser(rec)
        assert geo.carries_its_own_placement(posted), f"{c.get('parti')}: lost through the browser"
        assert corpus.carried(posted)["state"] == corpus.CARRIED, c.get("parti")
