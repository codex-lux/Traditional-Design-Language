#!/usr/bin/env python3
"""The Proportions plate's fixtures (WP-14.1): what the server serves for three order packs at a
12 in column, trimmed to the fields workbench/app/src/proportions/plate.js reads.

    python3 tests/fixtures/proportions_plate/generate.py           # rewrite the fixtures
    python3 tests/fixtures/proportions_plate/generate.py --check   # exit 1 if any is stale

THREE PACKS, ONE FOR EACH THING THE PLATE CAN GET WRONG: `vignola-ionic` declares the axis datum and
draws its entablature from the naked (OQ 78's per-group reading), `gibbs-doric` declares the naked
throughout, and `palladio-ionic` carries members whose record publishes no projection at all.
Nothing here is solved or searched, so regenerating is deterministic and moves only when the
record or the geometry moves; `tests/test_svg_census.py` holds the committed files to this output.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PACKS = ("vignola-ionic", "gibbs-doric", "palladio-ionic")
DIAMETER = 12
MEMBER_KEYS = ("id", "name", "profile", "y_bottom_in", "y_top_in", "projection_in",
               "side_by_side", "confidence")


def trimmed(pid):
    sys.path.insert(0, os.path.join(ROOT, "workbench", "server"))
    import corpus  # noqa: E402
    d = corpus.proportions_with_members(pid, column_diameter=DIAMETER)
    out = {k: d[k] for k in ("pack", "name", "module_in", "projection_datum", "column", "totals")}
    out["assemblies"] = [{"id": a["id"], "height_in": a["height_in"],
                          "members": [{k: m.get(k) for k in MEMBER_KEYS} for m in a["members"]]}
                         for a in d["assemblies"]]
    g = d["geometry"]
    out["geometry"] = {"module_in": g["module_in"], "assembly_datum": g["assembly_datum"],
                       "assemblies": [{"id": a["id"],
                                       "faces": [{"id": f["id"], "path": f.get("path")}
                                                 for f in a.get("faces", [])]}
                                      for a in g["assemblies"]]}
    return out


def text(pid):
    return json.dumps(trimmed(pid), indent=1, ensure_ascii=False) + "\n"


def main(argv):
    stale = []
    for pid in PACKS:
        path = os.path.join(HERE, "%s@%d.json" % (pid, DIAMETER))
        want = text(pid)
        if "--check" in argv:
            have = open(path, encoding="utf-8").read() if os.path.exists(path) else None
            if have != want:
                stale.append(os.path.basename(path))
        else:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(want)
    if stale:
        print("stale: %s -- run python3 tests/fixtures/proportions_plate/generate.py" % stale)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
