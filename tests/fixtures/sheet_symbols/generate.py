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

def main():
    for pid in ("tidewater-georgian-careful", "spec-builder-colonial"):
        out = HERE / f"{pid}.json"
        out.write_text(json.dumps(freeze(pid), indent=1, sort_keys=True) + "\n")
        d = json.loads(out.read_text())
        n_i = sum(len(l["expected"]["interior"]) for l in d["levels"])
        n_e = sum(len(l["expected"]["exterior"]) for l in d["levels"])
        n_u = sum(len(l["expected"]["undrawable"]) for l in d["levels"])
        print(f"{pid}: {n_i} interior, {n_e} exterior, {n_u} undrawable -> {out.name}")

if __name__ == "__main__":
    main()
