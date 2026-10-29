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
    # a forged verdict on the posted record is not read: the carried placement is re-judged
    posted = copy.deepcopy(out)
    posted["geometry_report"]["refused"] = {"kind": "forged", "facts": ["tiling"]}
    res = evaluate.evaluate(posted, place=True, engine="auto")
    assert calls == [], "a placement of the record itself is not re-solved"
    assert "error" not in res["check"], res["check"].get("error")
    kept = corpus.carried(posted)
    assert kept is not None and kept["geometry_report"].get("refused") != {"kind": "forged", "facts": ["tiling"]}
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
