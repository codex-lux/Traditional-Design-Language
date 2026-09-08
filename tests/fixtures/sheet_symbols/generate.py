#!/usr/bin/env python3
"""Freeze a solved placement and the openings both renderers must derive from it.

Read tests/fixtures/sheet_symbols/README.md first. The placement is frozen rather than
solved at test time on purpose: build/geometry.solve() reaches for CP-SAT and falls back
to the hill-climb when CP-SAT does not answer inside its budget, so a fixture built by
solving would pin this machine's speed alongside the code.

  python3 tests/fixtures/sheet_symbols/generate.py
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "build"))

import importlib.util
def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "build" / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

geometry = _load("geometry")
render_plan = _load("render_plan")

# the fields a renderer is allowed to read off a placed room; anything else is not part
# of the contract and does not belong in a fixture
ROOM_KEYS = ("id", "type", "name", "width_ft", "length_ft", "exterior_walls",
             "windows", "doors", "geometry")
# WP-11.3 CONSIDERED ADDING `furniture_layout` HERE AND DID NOT, for two reasons worth
# recording. This fixture exists to hold TWO implementations of one derivation to one answer,
# and furniture has only one: the marks are computed in build/furniture.py at placement time
# and written onto the record, so both renderers draw them and neither derives anything.
# Second, `freeze()` re-solves with the LIVE solver, so regenerating it on a machine where
# CP-SAT answers rewrites the frozen placement -- measured here, 4,104 lines of diff moving
# every door and window position, which is precisely what the README warns this file must
# never absorb. The furniture guards are tests/test_furniture_pass.py and the browser walk.

def freeze(plan_id):
    plan = json.loads((ROOT / "plans" / f"{plan_id}.json").read_text())
    solved = geometry.solve(plan)
    fp = solved["footprint"]
    W, H = fp["width_ft"], fp["depth_ft"]
    levels = []
    for lv in solved["levels"]:
        rooms = [{k: r[k] for k in ROOM_KEYS if k in r} for r in lv["rooms"] if r.get("geometry")]
        if not rooms: continue
        levels.append({
            "id": lv["id"], "index": lv.get("index", 0), "rooms": rooms,
            "expected": render_plan.derive_openings(rooms, W, H),
            "expected_divergence": [d["id"] for d in render_plan.declared_divergence(rooms)],
        })
    return {"plan": plan_id, "footprint": {"width_ft": W, "depth_ft": H},
            "note": "frozen placement — see README.md; regenerate with generate.py",
            "levels": levels}

def refresh_expected(pid):
    """Re-derive `expected` from the ROOMS ALREADY COMMITTED. Never solves. WP-11.14.

    `freeze()` above re-solves to obtain the rooms and only then derives `expected` from them
    -- so on a machine where CP-SAT answers, regenerating rewrites the frozen placement.
    The README measures that at 825 insertions and 804 deletions ON THE PRISTINE TREE WITH NO
    CODE CHANGE, and tells the reader not to regenerate to keep the fixture current.

    That warning made a renderer change to `derive_openings`' OUTPUT SHAPE look impossible to
    land: the contract is an exact dict comparison, so adding a key needs `expected` rewritten,
    and rewriting it meant absorbing eight hundred lines of solver noise. It does not. The
    rooms are contract INPUT and are already in the file; `expected` is a pure function of them
    and the footprint. Re-deriving it touches no solver, is deterministic, and produces a diff
    that is exactly the renderer's change and nothing else.

    Verified before this function was written: on the unchanged tree it is a NO-OP on both
    fixtures, which is the property that makes it trustworthy.
    """
    out = HERE / f"{pid}.json"
    fx = json.loads(out.read_text())
    W, H = fx["footprint"]["width_ft"], fx["footprint"]["depth_ft"]
    for lv in fx["levels"]:
        lv["expected"] = render_plan.derive_openings(lv["rooms"], W, H)
        lv["expected_divergence"] = [d["id"] for d in render_plan.declared_divergence(lv["rooms"])]
    out.write_text(json.dumps(fx, indent=1, sort_keys=True) + "\n")
    return fx


def main():
    # `--expected-only` re-derives the openings from the committed rooms and leaves the frozen
    # placement alone; the bare command re-solves and rewrites everything, which is what the
    # README warns about. The narrow mode is the one a renderer change wants.
    expected_only = "--expected-only" in sys.argv
    for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
        out = HERE / f"{pid}.json"
        if expected_only:
            refresh_expected(pid)
        else:
            out.write_text(json.dumps(freeze(pid), indent=1, sort_keys=True) + "\n")
        d = json.loads(out.read_text())
        n_i = sum(len(l["expected"]["interior"]) for l in d["levels"])
        n_e = sum(len(l["expected"]["exterior"]) for l in d["levels"])
        n_u = sum(len(l["expected"]["undrawable"]) for l in d["levels"])
        print(f"{pid}: {n_i} interior, {n_e} exterior, {n_u} undrawable -> {out.name}")

if __name__ == "__main__":
    main()
