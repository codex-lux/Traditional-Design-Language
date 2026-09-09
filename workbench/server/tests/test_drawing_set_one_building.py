"""WP-12.0 — a drawing set is one building, and the elevation and roof were not in it.

WP-6.4 established the rule and wrote it down: *"one drawing set is one building or it is
nothing."* It moved the plan, section and bearing sheets onto `corpus._placed` -- one placement
per set, on the proving engine. It did not move the elevation or the roof, and nothing noticed
for eleven weeks, because both were called as `build_elevation(plan, pt)` / `build_roof(plan,
pt)` -- no section -- and each then built its own from `structure.build_section`, whose engine
default is the HEURISTIC and whose own comment says that default is *"for INTERNAL callers
ONLY"* (plan_check's elevation layer, the composer's scoring loop).

WHAT IT ACTUALLY DREW, measured before the fix rather than argued:

  spec-builder-colonial   auto reaches a CP proof      footprint 51.33 x 32.08 -> 51.33 x 32.33
    faces S, N   identical    the front is drawn on the WIDTH, and the width did not move
    faces E, W   DIFFER       the gable ends are drawn on the DEPTH, and the depth did
    porch_clear_depth_ft  4.75 -> 4.00   the measurement `porch-too-shallow-to-inhabit`
                                         reads: 0.75 ft in the flattering direction
  tidewater-georgian-careful   auto spends its budget and falls back
    all four faces identical -- the two placements coincide, so the defect is invisible here

So the drawn consequence is a GABLE END of a proved house drawn from a searched placement --
**and it could never have been seen, because no client has ever been able to ask for a gable
end.** `render_elevation` has taken a `face` since WP-3.2 and `corpus.drawing` has forwarded
`body.face` since WP-5.1; the surface sent none. Two defects wearing one symptom: the one face
that shows the bug is the one face nobody could request.

A NOTE ON THE FIRST VERSION OF THESE TESTS, BECAUSE IT IS THE FINDING WORTH KEEPING. They
asserted that the plates report one `solver.drawn_by.input_digest` and one engine -- and they
PASSED WITH THE FIX REVERTED, because the metadata is read from `_placed` whatever the plate
was built on. A test of what a plate REPORTS is not a test of what it was DRAWN from. These
assert the drawing.
"""
import hashlib
import json
import os
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BUILD = os.path.join(ROOT, "build")


def _plan(name="spec-builder-colonial"):
    return json.load(open(os.path.join(ROOT, "plans", f"{name}.json")))


def _digest(payload):
    return ((payload.get("solver") or {}).get("drawn_by") or {}).get("input_digest")


def _elevation_built_without_the_sets_placement(plan, face):
    """The pre-WP-12.0 call, rendered: `build_elevation(plan, parti)` with no section, so it
    falls into `build_section`'s internal heuristic default. Reproduced here rather than
    described, so the assertion below is a comparison of two drawings and not of a claim."""
    from mcp_server import core
    EL = core._mod("elevation", f"{BUILD}/elevation.py")
    RE = core._mod("render_elevation", f"{BUILD}/render_elevation.py")
    elev = EL.build_elevation(core.copy_json(plan), None)
    assert "error" not in elev, elev.get("error")
    fd, p = tempfile.mkstemp(suffix=".svg")
    os.close(fd)
    try:
        RE.render_elevation(elev, p, face=face)
        return open(p).read()
    finally:
        os.unlink(p)


def _engines_differ_on(plan):
    """Whether this plan is one the defect can be SEEN on. `auto` reaching a proof is what
    makes the set's placement different from the elevation's own heuristic; where it falls
    back to the budget the two coincide and every assertion below would pass vacuously.

    Returns the set's engine, so a test can say COULD NOT EVALUATE by name instead of
    quietly passing -- which is this corpus's first rule about a third state.
    """
    from mcp_server import core
    from workbench.server import corpus
    placed = corpus._placed(core.copy_json(plan), None, 250)
    if "error" in placed:
        return None
    return (placed["geometry_report"].get("solver") or {}).get("engine")


def test_every_plate_in_a_set_names_the_input_it_was_drawn_from(client):
    """WP-11.8's J6, extended to the two plates that could not carry it: two sheets of "the
    same house" that disagree differ because the INPUT differed, and a reader needs to be able
    to tell. This is a test of the METADATA and says so -- on its own it does not prove the
    plates were built on one placement (the first version of this file thought it did)."""
    plan = _plan()
    digests = {}
    for kind in ("plan", "elevation", "roof"):
        r = client.post(f"/api/drawings/{kind}", json={"plan": plan})
        assert r.status_code == 200, (kind, r.text[:200])
        d = _digest(r.json())
        assert d, f"{kind} names no input digest — a reader cannot tell two plates apart"
        digests[kind] = d
    assert len(set(digests.values())) == 1, f"the plates name different inputs: {digests}"


def test_the_gable_end_is_drawn_from_the_sets_own_placement(client):
    """THE ONE THAT CATCHES THE DEFECT.

    The route's east elevation must not equal the elevation built the pre-WP-12.0 way. On
    `spec-builder-colonial` the set proves 50.0 x 31.0 while `build_section`'s own default
    searches, and the gable end is drawn on the depth, so the two drawings differ. Reverting
    either `section=` argument in `corpus.drawing` makes them equal and turns this red.
    """
    plan = _plan()
    engine = _engines_differ_on(plan)
    if engine != "cp-sat":
        pytest.skip(f"COULD NOT EVALUATE — the set placed with {engine!r}, not a proof, so "
                    f"the set's placement and build_section's own default coincide and this "
                    f"assertion would pass vacuously. Not a pass.")
    r = client.post("/api/drawings/elevation", json={"plan": plan, "face": "E"})
    assert r.status_code == 200, r.text[:200]
    drawn = r.json()["svg"]
    stale = _elevation_built_without_the_sets_placement(plan, "E")
    # Both are re-tokenized by the route and not by the helper, so compare the GEOMETRY the
    # two carry rather than the ink: the helper's SVG is the dark palette, the route's is the
    # Drawn Language, and an equality over the whole string would be true of neither.
    from workbench.server import svg_theme
    assert drawn != svg_theme.retokenize(stale), (
        "the east elevation the route drew is byte-identical to one built with no section — "
        "the elevation is still taking build_section's internal heuristic default while the "
        "plan sheet beside it is a proof, which is WP-6.4's defect in the two plates it missed")


def test_the_roof_plan_is_drawn_from_the_sets_own_placement(client):
    """The roof had the same defect and needs its own drawn guard: the metadata test above
    reads `_placed`'s solver record, which is reported whatever the plate was built on, so it
    passes with the roof reverted. The roof plan draws the eave rectangle from the footprint,
    and the footprint's depth is what moves between the two placements."""
    plan = _plan()
    if _engines_differ_on(plan) != "cp-sat":
        pytest.skip("COULD NOT EVALUATE — the set did not reach a proof, so the two "
                    "placements coincide and this would pass vacuously. Not a pass.")
    from mcp_server import core
    from workbench.server import svg_theme
    RF = core._mod("roof", f"{BUILD}/roof.py")
    RR = core._mod("render_roof", f"{BUILD}/render_roof.py")
    roof = RF.build_roof(core.copy_json(plan), None)          # the pre-WP-12.0 call
    fd, p = tempfile.mkstemp(suffix=".svg")
    os.close(fd)
    try:
        RR.render_roof(roof, p)
        stale = svg_theme.retokenize(open(p).read())
    finally:
        os.unlink(p)
    drawn = client.post("/api/drawings/roof", json={"plan": plan}).json()["svg"]
    assert drawn != stale, (
        "the roof plan the route drew is byte-identical to one built with no section — it is "
        "still taking build_section's internal heuristic default")


def test_the_front_elevation_is_unmoved_and_that_is_why_nobody_saw_it(client):
    """The control, and the reason this went eleven weeks unnoticed. The front is drawn on the
    WIDTH; on both shipped plans the width is the same under either engine, so the one face a
    client could ask for is byte-identical before and after. A fix that moved this too would
    be doing something else."""
    plan = _plan()
    if _engines_differ_on(plan) != "cp-sat":
        pytest.skip("COULD NOT EVALUATE — no proof, so there is no before-and-after here")
    from workbench.server import svg_theme
    r = client.post("/api/drawings/elevation", json={"plan": plan, "face": "N"})
    stale = svg_theme.retokenize(_elevation_built_without_the_sets_placement(plan, "N"))
    assert r.json()["svg"] == stale, (
        "the front elevation moved. It is drawn on the width and the width does not move "
        "between these two placements; if this changed, the change was not WP-12.0's")


def test_a_face_that_is_accepted_is_actually_drawn(client):
    """`render_elevation` has taken `face` since WP-3.2 and the route has forwarded it since
    WP-5.1; no client ever sent one, so nothing had ever checked that the argument reaches the
    pen. Four faces must give four drawings: asserting only that each returns 200 would pass
    with the argument dropped on the floor."""
    plan = _plan("tidewater-georgian-careful")
    svgs = {}
    for face in ("S", "N", "E", "W"):
        r = client.post("/api/drawings/elevation", json={"plan": plan, "face": face})
        assert r.status_code == 200, (face, r.text[:200])
        svgs[face] = hashlib.sha256(r.json()["svg"].encode()).hexdigest()
    assert len(set(svgs.values())) == 4, (
        f"only {len(set(svgs.values()))} distinct drawings for four faces — a `face` that is "
        f"accepted and ignored looks exactly like one that works")


def test_the_default_face_is_still_the_entrance_front(client):
    """Sending no face must draw what it has always drawn: the server's own
    `face or elev["entrance_face"]`. The surface arrives with no face chosen, so this is the
    plate a reader who changes nothing sees."""
    plan = _plan("tidewater-georgian-careful")
    none = client.post("/api/drawings/elevation", json={"plan": plan}).json()
    front = client.post("/api/drawings/elevation",
                        json={"plan": plan, "face": none["entrance_face"]}).json()
    assert none["svg"] == front["svg"]
    assert none["entrance_face"] in ("S", "N", "E", "W")


def test_an_unknown_face_does_not_crash_the_renderer(client):
    """A face is a caller-supplied string. `render_elevation` falls back to the entrance face
    for anything it does not recognise -- a conservative reading, which is available here and
    is not available for a room's `type` (WP-10.1's gate). This pins that it stays a drawing
    rather than a traceback from an unauthenticated route."""
    r = client.post("/api/drawings/elevation",
                    json={"plan": _plan("tidewater-georgian-careful"), "face": "NNW"})
    assert r.status_code in (200, 422), r.text[:200]
    if r.status_code == 200:
        assert r.json()["svg"].startswith("<svg")
