"""WP-13.4 — the refusal to draw, end to end over HTTP.

Lucas ruled 15 Sep 2026: a placement that breaks a hard fact of the type is REFUSED, not drawn;
the bench shows the conflict set; the brief or the parti is what changes. The RECORD keeps the
search's least-bad placement -- it is the conflict set's own explanation and the wall drag's
working sketch -- and NO user-facing surface draws it.

WHAT IS DRIVEN HERE, and why each one is a separate assertion rather than one sweep: the four
surfaces reach the placement by four different routes, and a guard on one says nothing about
the others. `/api/drawings` and `/api/scene` go through `corpus._placed`; `/api/export/dxf`
goes through `export_dxf._solved_copy`, which has its OWN short circuit and its own solve;
`/api/export/ifc` did not go through `_placed` at all until this package, and took
`build_section`'s internal heuristic default instead. `/api/plan/evaluate` does not use
`_placed` and answers 200 rather than 422, because the bench needs the findings beside the
refusal.

THE FIXTURE IS READ FROM THE CORPUS AND NOT NAMED. Which records are refused is a property of
the placer and moves with it; a literal filename here would go red on a placement change it is
not about. `_refused_plan` sweeps and skips, and `test_the_ruling_is_live_on_this_corpus` below
asserts the premise both halves rest on -- that something is refused AND something is drawable.
"""
import json
import os

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("jsonschema")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))


def _shipped():
    for d in ("plans", os.path.join("plans", "reference")):
        for name in sorted(os.listdir(os.path.join(ROOT, d))):
            if name.endswith(".json"):
                yield os.path.join(ROOT, d, name)


@pytest.fixture(scope="module")
def refused_plan():
    """A shipped record the ruling refuses, found by reading the verdict. Skips where the
    corpus holds none -- there is then nothing for this file to be about, and a green tick
    would be a claim about a refusal nobody made."""
    from workbench.server import corpus
    for p in (os.path.join(ROOT, "plans", "tidewater-georgian-careful.json"),
              os.path.join(ROOT, "plans", "spec-builder-colonial.json")):
        plan = json.load(open(p, encoding="utf-8"))
        if "refused_placement" in corpus._placed(corpus.core.copy_json(plan), None, 60):
            return plan
    pytest.skip("COULD NOT EVALUATE: no shipped plan is refused on this tree")


def test_the_ruling_is_live_on_this_corpus():
    """The premise every other guard in this package rests on, stated once and measured.

    A tree where NOTHING is refused makes every driven refusal here vacuous; a tree where
    nothing is DRAWABLE makes `drawable.py` skip every drawing suite. Both are real states this
    corpus could reach, and neither may go unnoticed, so the two counts are asserted together
    and the census is printed in the failure.

    Measured 16 Sep 2026 on `auto`: **15 of the 16 shipped records refused, 1 drawable**. Not
    pinned as a count -- the count is a property of the placer -- but as the two facts."""
    from workbench.server import corpus
    refused, drawable = [], []
    for p in _shipped():
        plan = json.load(open(p, encoding="utf-8"))
        res = corpus._placed(corpus.core.copy_json(plan), None, 60)
        if "refused_placement" in res:
            refused.append(os.path.basename(p))
        elif "error" not in res:
            drawable.append(os.path.basename(p))
    assert refused, ("nothing in this corpus is refused: the 15 Sep ruling has stopped biting "
                     "and every driven refusal in this package is now about nothing")
    assert drawable, (f"all {len(refused)} shipped records are refused: there is no drawable "
                      f"house left, and every drawing suite can only skip")


# ---------------------------------------------------------------- the drawing surfaces

@pytest.mark.parametrize("kind", ["plan", "elevation", "section", "bearing", "roof"])
def test_no_drawing_route_returns_an_svg_for_a_refused_placement(client, refused_plan, kind):
    """All five kinds, because they take three different paths through `corpus.drawing` -- the
    plan branch, the elevation/roof branches that build a section first, and section/bearing --
    and a refusal that reaches one of them says nothing about the others."""
    r = client.post(f"/api/drawings/{kind}", json={"plan": refused_plan})
    assert r.status_code == 422, (kind, r.status_code, r.text[:200])
    d = r.json()["detail"]
    assert "svg" not in d, f"{kind}: a refused placement was drawn"
    assert d["refused_placement"]["lines"], f"{kind}: refused with no reason given"
    assert d["refused_placement"]["kind"] in ("infeasible", "type-fact-downgraded")


def test_the_conflict_set_survives_the_frame_it_was_computed_in(client, refused_plan):
    """`corpus.drawing` read `{"error": placed["error"]}` at four call sites, so the refusal
    was flattened to its sentence one frame above where it was made and the route answered 422
    with prose and no evidence. A refusal is CONTENT: it names what could not hold, and the
    bench draws that list where the house would have been."""
    r = client.post("/api/drawings/plan", json={"plan": refused_plan})
    ref = r.json()["detail"]["refused_placement"]
    assert set(ref) == {"kind", "facts", "conflicts", "lines", "engine", "status"}, (
        f"the refusal's shape has moved: {sorted(ref)}. Both slices of WP-13.4 were built "
        f"against one written contract and neither may change it silently.")
    assert ref["conflicts"], "the evidence is gone and only the sentence survived"


def test_the_scene_route_refuses(client, refused_plan):
    r = client.post("/api/scene", json={"plan": refused_plan, "plates": False})
    assert r.status_code == 422, r.text[:200]
    d = r.json()["detail"]
    assert "scene" not in d and d["refused_placement"]["lines"]


def test_a_refusal_never_carries_the_key_that_means_a_missing_library(client, refused_plan):
    """`app.py` maps a `refusal` key to **501 Not Implemented**, which is the honest answer for
    an absent ezdxf or ifcopenshell. A placement refusal wearing that key would tell a reader
    the server lacks a capability it has -- two words one letter apart, opposite in meaning.
    Swept over every route that can produce either."""
    bodies = [("/api/drawings/plan", {"plan": refused_plan}),
              ("/api/scene", {"plan": refused_plan, "plates": False}),
              ("/api/export/dxf", {"plan": refused_plan, "kind": "plan"}),
              ("/api/export/ifc", {"plan": refused_plan})]
    for path, body in bodies:
        r = client.post(path, json=body)
        assert r.status_code == 422, (path, r.status_code, r.text[:160])
        d = r.json()["detail"]
        assert d.get("refusal") is not True, (
            f"{path} answered with the missing-library key on a refused house")


# ---------------------------------------------------------------- evaluate, and the sketch

def test_evaluate_answers_200_with_the_refusal_and_no_placement(client, refused_plan):
    """The bench needs the findings BESIDE the refusal -- a refused house is exactly the one a
    reader most needs judged -- so this route is a 200 rather than a 422. What it may not do is
    return a placement: a surface handed both will draw the placement."""
    r = client.post("/api/plan/evaluate",
                    json={"plan": refused_plan, "place": True, "candidates": 60})
    assert r.status_code == 200, r.text[:200]
    j = r.json()
    assert "placement" not in j, "the route returned a refusal AND the house to draw"
    assert j["placement_refused"]["lines"]
    assert j["check"]["counts"], "the findings went with the placement -- they must not"


def test_the_wall_drag_keeps_its_sketch_and_says_it_is_one(client, refused_plan):
    """The ruling's one exemption, named by ENGINE. `PlanWorkbench.jsx` asks for the heuristic
    by name on the drag path only; a drag that cannot see the rectangle it is dragging is not a
    drag. The marking is written on EVERY heuristic evaluate, so a client cannot read its
    absence as a proof, and it carries the refusal inside it rather than beside it."""
    r = client.post("/api/plan/evaluate",
                    json={"plan": refused_plan, "place": True, "engine": "heuristic",
                          "candidates": 60}).json()
    assert "placement" in r, "the wall drag lost its sketch"
    sk = r["placement"]["sketch"]
    assert sk["working"] is True and sk["reason"]
    assert sk["refused"] and sk["refused"]["lines"], (
        "the sketch of a refused house says nothing about the refusal -- a marking with no "
        "reason in it is decoration")


def test_a_record_that_holds_is_not_marked_refused_anywhere(client):
    """The control, and without it every assertion above passes on a route that refuses
    everything. The drawable record must come back with a picture, no `placement_refused`, and
    a sketch whose `refused` is null on the drag path."""
    from . import drawable
    plan = drawable.drawable_plan()
    r = client.post("/api/drawings/plan", json={"plan": plan})
    assert r.status_code == 200, r.text[:200]
    assert r.json()["svg"].lstrip().startswith("<svg")
    ev = client.post("/api/plan/evaluate",
                     json={"plan": plan, "place": True, "candidates": 60}).json()
    assert "placement_refused" not in ev and "placement" in ev
    drag = client.post("/api/plan/evaluate",
                       json={"plan": plan, "place": True, "engine": "heuristic",
                             "candidates": 60}).json()
    assert drag["placement"]["sketch"]["refused"] is None, (
        "a drawable record's sketch claims a refusal: the marking is not reading the record")


# ---------------------------------------------------------------- the MCP tool

def test_tdl_place_plan_returns_the_refusal_and_writes_no_file(refused_plan, tmp_path):
    """`core.place_plan` returned coordinates on a refused placement and wrote an SVG beside
    them -- the drawing surface a model hands to a person. It refuses in `_metered`'s own shape
    now, told apart from a rate limit by `why`, and the file is the assertion that matters:
    a tool that refuses in its JSON and writes the picture anyway has refused nothing."""
    import sys
    if os.path.join(ROOT, "mcp_server") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
    import core
    out = tmp_path / "refused.svg"
    res = core.place_plan(core.copy_json(refused_plan), None, 60, svg_path=str(out))
    assert res["refused"] is True and res["why"] == "placement"
    assert res["placement_refused"]["lines"]
    assert "footprint" not in res and "rooms" not in res, (
        "the tool refused and returned the coordinates anyway")
    assert not out.exists(), "the tool refused and wrote the drawing"


def test_the_two_mcp_refusals_are_told_apart_by_why():
    """A rate limit and a refused house share a shape so a client needs one reader, and they
    mean opposite things -- "come back later" against "this house cannot be drawn". `why` is
    the discriminator and the prose is not; asserted on the rate-limit half here, since the
    placement half is asserted above."""
    import sys
    if os.path.join(ROOT, "mcp_server") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "mcp_server"))
    pytest.importorskip("mcp")
    import server as mcp_server
    mcp_server.set_limiter(lambda tool: "over the cap")
    try:
        got = json.loads(mcp_server._metered("tdl_place_plan"))
    finally:
        mcp_server.set_limiter(None)
    assert got["refused"] is True and got["why"] == "rate-limit"
    assert got["why"] != "placement"


def test_the_two_mcp_refusal_words_are_written_down_and_differ():
    """The source half of the test above, and it exists because that one CANNOT RUN HERE.

    `mcp_server/server.py` imports the MCP SDK, which is absent on this machine, so the
    behavioural guard skips -- and a skipped guard is a COULD NOT EVALUATE, not a pass. Found
    by mutation: rewriting `_metered`'s `why` to "placement" left that test green because it
    never ran. This half reads the two files and holds the two words apart with no import at
    all, so the discriminator cannot be collapsed silently on a machine without the SDK."""
    import ast

    def _whys(path, func):
        """Every `"why"` a named function's dict literals set. READ FROM THE AST, because the
        first version of this guard searched the TEXT and went red on the comment in `_metered`
        that explains the very rule -- a source guard convicting the sentence that states it,
        which is this repository's own most-repeated test defect."""
        tree = ast.parse(open(path, encoding="utf-8").read())
        out = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func:
                for d in ast.walk(node):
                    if not isinstance(d, ast.Dict):
                        continue
                    for k, v in zip(d.keys, d.values):
                        if isinstance(k, ast.Constant) and k.value == "why" \
                                and isinstance(v, ast.Constant):
                            out.add(v.value)
        return out

    metered = _whys(os.path.join(ROOT, "mcp_server", "server.py"), "_metered")
    placed = _whys(os.path.join(ROOT, "mcp_server", "core.py"), "place_plan")
    assert metered == {"rate-limit"}, (
        f"`_metered` names its refusal {sorted(metered)}: a client cannot tell a rate limit "
        f"from a house that cannot be drawn")
    assert placed == {"placement"}, f"`place_plan` names its refusal {sorted(placed)}"
    assert not (metered & placed), (
        "the rate limit and the placement refusal are wearing one word: they mean opposite "
        "things to a caller, and the shape they share is exactly why the word must differ")
