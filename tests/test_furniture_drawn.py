"""WP-9.6 -- the furniture rule is one function, and the drawn layer reads the drawing.

Until this package `plan_check`'s furniture block read `r.get("width_ft")` -- the DECLARED
record -- and nothing else. The measurement that says so: over the sixteen plans the furniture
layer emitted exactly 137 findings whether or not the plan carried geometry. A room declared
adequate and drawn as a sliver passed its own furniture check, which is Lucas's second complaint
(a breakfast room declared 12 x 14 and drawn 7.0 x 27.0) computed and never stated.

Every figure here is `engine="heuristic"`, which is deterministic and identical on cold runs.
NEVER ratchet the `auto` figures: `auto` solves 15 of the 16 plans with CP-SAT, which under a
wall-clock budget is not reproducible, and the same sweep returned 130, 132 and 133 on one
unchanged tree. A ratchet on a drifting number is a build that fails for no reason.
"""
import json, glob, os, importlib.util, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _mod(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


G = _mod("build/geometry.py", "geometry_fd")
PC = _mod("build/plan_check.py", "plan_check_fd")

ROOMS = {}
for _fn in sorted(os.listdir(ROOT / "rooms")):
    if _fn.endswith(".json"):
        _d = json.loads((ROOT / "rooms" / _fn).read_text())
        ROOMS[_d["id"]] = _d


def _plans():
    # `sorted(` on the SAME LINE as each read: tests/test_determinism.py checks this per line,
    # so a sort that opens on the line above reads to it as an unsorted glob. Same line-by-line
    # shape as check_citations and a wrapped slug -- write for the reader you have.
    _here = sorted(glob.glob(str(ROOT / "plans" / "*.json")))
    _ref = sorted(glob.glob(str(ROOT / "plans" / "reference" / "*.json")))
    for pf in _here + _ref:
        d = json.loads(pathlib.Path(pf).read_text())
        if "levels" in d:
            yield pf, d


def _sweep():
    """(short-axis, long-axis) drawn shortfalls over every placed room, on the fast engine."""
    short = long_ = 0
    for _pf, d in _plans():
        res = G.solve(json.loads(json.dumps(d)), engine="heuristic")
        for lv in res["levels"]:
            for r in lv["rooms"]:
                rt, g = ROOMS.get(r.get("type")), r.get("geometry")
                if not rt or not g:
                    continue
                gw = min(g["width_ft"], g["depth_ft"])
                gl = max(g["width_ft"], g["depth_ft"])
                for s in PC.furniture_shortfalls(rt, gw, gl):
                    if s["axis"] == "short":
                        short += 1
                    else:
                        long_ += 1
    return short, long_


# --- the arithmetic is spelled ONCE -------------------------------------------------

def test_the_fit_arithmetic_lives_in_exactly_one_function():
    """A second transcription is how an arbiter comes to convict what the solver proved legal.

    This repository's most-repeated wound. The room layer and the drawn layer differ in WORDING
    and LAYER and must never differ in arithmetic.
    """
    hits = []
    for py in sorted((ROOT / "build").glob("*.py")):
        for ln, line in enumerate(py.read_text().splitlines(), 1):
            if "sides * cl" in line:
                hits.append(f"{py.name}:{ln}")
    # Asserted as a COUNT and a LOCATION, never against an empty list: a selector that stops
    # matching would otherwise turn this into a tautology that passes on a codebase where the
    # expression has been renamed out of existence. This repository has shipped that exact
    # inversion before (`assert 'class="ch"' not in text`).
    assert len(hits) == 1, (
        "the clearance expression must appear exactly once in build/; found %d: %s. It belongs "
        "in plan_check.furniture_shortfalls and nowhere else." % (len(hits), hits))
    assert hits[0].startswith("plan_check.py:"), (
        "the one spelling of the fit arithmetic has moved out of plan_check.py: %s" % hits[0])


# --- both axes, independently (the `elif` split) --------------------------------------

def test_both_axes_are_reported_when_a_room_fails_both():
    """Until WP-9.6 the long axis was tested only where the short axis had PASSED."""
    rt = ROOMS["breakfast-room"]
    both = PC.furniture_shortfalls(rt, 4.0, 4.0)
    axes = {s["axis"] for s in both}
    assert axes == {"short", "long"}, (
        "a 4 x 4 ft breakfast room fails its table on both axes and both must be reported; "
        "got %s" % sorted(axes))


def test_a_conforming_room_reports_nothing():
    """The other direction: the check must be silent on a room that fits."""
    rt = ROOMS["breakfast-room"]
    assert PC.furniture_shortfalls(rt, 12.0, 14.0) == [], (
        "the declared 12 x 14 breakfast room holds its catalogue and must draw no finding")


def test_the_short_axis_is_the_rooms_short_dimension():
    """`sorted()` pairs the item's short side with the room's width and its long side with the
    room's length. WP-9.2 s8 called this "assumes every item rotates" and was wrong; the pairing
    IS the rule. An 84 x 27 in island at 42 in clearance needs 9.25 ft across and 13.0 ft along,
    so a 12 x 16 ft kitchen holds it and a 10 x 11 ft one does not."""
    kit = ROOMS["kitchen"]
    assert PC.furniture_shortfalls(kit, 12.0, 16.0) == [] or all(
        s["item"] != "island" for s in PC.furniture_shortfalls(kit, 12.0, 16.0)), (
        "a 12 x 16 ft kitchen holds an 84 x 27 in island with 42 in aisles")
    tight = [s for s in PC.furniture_shortfalls(kit, 10.0, 11.0) if s["item"] == "island"]
    assert tight and tight[0]["axis"] == "long", (
        "a 10 x 11 ft kitchen fails the island on its LENGTH (13.0 ft needed), not its width")


# --- the drawn layer is wired ---------------------------------------------------------

def test_the_drawn_layer_names_a_room_the_declared_record_passes():
    """The wiring, end to end, on the corpus's own most-authored plan."""
    plan = json.loads((ROOT / "plans" / "tidewater-georgian-careful.json").read_text())
    solved = G.solve(json.loads(json.dumps(plan)), engine="heuristic")
    rep = PC.check(json.loads(json.dumps(solved)))
    drawn_furn = [f for f in rep["findings"]
                  if f.get("layer") == "drawn" and "cannot take its" in (f.get("statement") or "")]
    assert drawn_furn, (
        "the drawn layer reports no furniture shortfall at all -- either the call site is gone "
        "or nothing on this plan is drawn too small, and the second has never been true")
    for f in drawn_furn:
        assert "is DRAWN" in f["statement"], (
            "a drawn-layer furniture finding must say it is describing the DRAWING, not the "
            "record: %r" % f["statement"])


# --- ratchets: these may only go DOWN -------------------------------------------------

# 86 + 69 = 155, which is exactly the drawn layer's growth on the sixteen solved plans
# (419 -> 574). Of those, 140 are the new call site (86 across + 54 along) and 15 are long-axis
# shortfalls the old `elif` computed and dropped. The declared furniture layer moved 137 -> 178
# by the same split, +41.
DRAWN_SHORT_CEILING = 86
# 74, RAISED FROM 69 BY WP-11.2, AND THE RAISE IS THE PACKAGE'S COST RATHER THAN A TIDY-UP.
# The plan now names its parti, so the placement takes the diagram's own 9 ft bay module and the
# massing's odd bay count: seven bays of 9 ft where it was six of 10, 63.0 x 38.2 ft where it was
# 60.0 x 40.1. Five more placed rooms fail an essential item ALONG their length in that footprint;
# ACROSS is unmoved at 86. The same change costs about three fatal findings on this engine (8-seed
# means 6.2 -> 9.2, every one an unreachable room) and ZERO on CP-SAT, where serious goes 73 -> 67
# and transfer beams 30 -> 17.
#
# It was taken anyway, and the reason is in `docs/reports/wp-11.2-the-diagram-reaches-the-record.md`:
# a house with a centre bay and more findings from a search that cannot realise doors is closer to
# the type than a house with NO CENTRE BAY, which is where a Georgian door goes. The findings are
# the critic telling the truth about a hill-climb result on a program known to be wrong for its
# container (`oq/the-parti-dissolved-its-own-dependencies`, ruled and unbuilt).
#
# THE DIRECTION IS RECORDED SO THE NEXT READER CAN SEE IT: 69 was the WP-9.6 measurement and this
# is the first time either number has gone UP. If it goes up again, read this comment and the two
# reports before adding a third line to it.
DRAWN_LONG_CEILING = 74


def test_drawn_furniture_shortfalls_are_ratcheted():
    """Measured 1 Sep 2026 on `engine="heuristic"`, identical on three cold runs.

    These are the honest measure of whether a placement change helps. If a change to either
    engine lowers them, lower the ceiling here in the same commit and say so. If it RAISES them,
    the placement got worse and the build should say so rather than absorb it.
    """
    short, long_ = _sweep()
    assert short <= DRAWN_SHORT_CEILING, (
        f"placed rooms failing an essential item ACROSS rose to {short} from "
        f"{DRAWN_SHORT_CEILING}; the placement drew more unbuildable rooms than before")
    assert long_ <= DRAWN_LONG_CEILING, (
        f"placed rooms failing an essential item ALONG rose to {long_} from "
        f"{DRAWN_LONG_CEILING}")
    assert (short, long_) == (DRAWN_SHORT_CEILING, DRAWN_LONG_CEILING), (
        f"the sweep now reads {short}/{long_} against a pinned {DRAWN_SHORT_CEILING}/"
        f"{DRAWN_LONG_CEILING}. An improvement is welcome -- lower the ceilings here and say "
        f"what moved, so the next reader knows the number is current.")
