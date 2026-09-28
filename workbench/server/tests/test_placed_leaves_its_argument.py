"""`corpus._placed` LEAVES THE RECORD IT IS HANDED AS IT WAS, ON A MISS AND ON A HIT (audit, 27 Sep 2026).

`geometry.solve` writes a placement into its argument on a cache miss and returns a copy on a hit.
`_placed` handed it the caller's record, so every drawing branch that goes on to hand `plan` to a
builder beside `geometry_result=placed` handed the PLACED record on a record's first request and
the DECLARED one after -- and the roof's stacks and voids, the section's massing elements and the
IFC's slabs were read off that record, so one request drew one house and the next another. Those
readers take the placement now (`tests/test_the_placement_decides_the_section.py`); this holds the
boundary itself, so a reader added later cannot answer by cache state either.

Both halves are asserted on one private cache: the first request is a miss and the second a hit,
and the premise that the second really was a hit is read off the cache, not assumed.
"""
import json
import os

from . import drawable

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_the_record_handed_is_the_record_after_on_a_miss_and_on_a_hit(monkeypatch):
    from mcp_server import core
    from workbench.server import corpus
    geo = core._mod("geometry", os.path.join(ROOT, "build", "geometry.py"))
    monkeypatch.setattr(geo, "_SOLVE_CACHE", {})
    plan = drawable.drawable_plan()
    for request in ("miss", "hit"):
        entries = len(geo._SOLVE_CACHE)
        arg = core.copy_json(plan)
        before = json.dumps(arg, sort_keys=True)
        out = corpus._placed(arg, None, 250)
        assert "error" not in out, (request, out.get("error"))
        assert out is not arg, request
        assert json.dumps(arg, sort_keys=True) == before, \
            f"{request}: _placed wrote the placement into the caller's record"
        assert any("geometry" in r for lv in out["levels"] for r in lv["rooms"]), request
        if request == "hit":
            assert len(geo._SOLVE_CACHE) == entries >= 1, "the premise: the second request was a hit"
