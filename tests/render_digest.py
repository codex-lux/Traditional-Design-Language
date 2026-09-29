"""render_digest.py -- hash every sheet the four renderers draw for every shipped plan.

The instrument behind every "N of 128 sheets moved" in the Phase 15 reports. Until 28 Sep 2026 it
lived in a session's scratch directory, so no later reader could re-derive a single one of those
counts from the tree (WP-15.8's audit, auditor C). It is committed here, beside the census, and the
reports cite it by path.

For each plan in `plans/` and `plans/reference/`, placed on the heuristic engine (deterministic,
so a digest is a statement about the code and not about the clock), it renders:

  the plan sheet in each register     `<plan>/plan-<register>`
  the section                         `<plan>/section`
  the roof                            `<plan>/roof`
  the elevation, all four faces       `<plan>/elev-<face>`
  the elevation DXF, all four faces   `<plan>/dxf-elev-<face>`   (where ezdxf is installed)
  the scene record                    `<plan>/scene`

A DXF is hashed by its ENTITIES, not its bytes: ezdxf stamps every file with its creation time
and fresh GUIDs, so two exports of one drawing never share a byte digest. Each modelspace entity
contributes its type, its layer, its geometry rounded to a thousandth and its text. The scene is
hashed as its JSON with the keys sorted. Both were added by WP-16.3 (29 Sep 2026), whose faces
move on all three surfaces at once; a digest of the sheet alone could not have said that the DXF
and the model moved with it.

and records the first 16 hex digits of each sheet's sha256. A sheet whose renderer raised is
recorded as `ERR <exception type>`, never dropped: a sheet missing from one side of a diff would
read as a sheet that did not move.

    python3 tests/render_digest.py [--root TREE] [--out FILE]   hash every sheet (JSON to FILE or stdout)
    python3 tests/render_digest.py --diff A.json B.json          list the sheets that differ

`--root` hashes another checkout -- a `git worktree` of the parent, never a tar extract, because
several builders ask git for the tracked population. Run one tree per process: each tree's
modules are loaded from that tree. Nothing is written inside any repository; the sheets are drawn
into a temporary directory and removed.
"""
import argparse
import glob
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def digest(root):
    """{"<plan>/<sheet>": sha16 or "ERR <type>"} for every shipped plan under `root`."""
    root = os.path.abspath(root)
    sys.path.insert(0, os.path.join(root, "build"))
    import modcache  # noqa: E402  -- the tree's own loader, after its build/ is first on the path

    def mod(name):
        return modcache.load(name, os.path.join(root, "build", name + ".py"))

    here = os.getcwd()
    os.chdir(root)
    tmp = tempfile.mkdtemp(prefix="tdl-render-digest-")
    try:
        GEO, ST, RF, EL = mod("geometry"), mod("structure"), mod("roof"), mod("elevation")
        RP, RE, RS, RR = (mod("render_plan"), mod("render_elevation"), mod("render_section"),
                          mod("render_roof"))
        out = {}

        def sha(path):
            with open(path, "rb") as fh:
                return hashlib.sha256(fh.read()).hexdigest()[:16]

        SC = mod("scene")
        try:
            import ezdxf  # noqa: F401  -- optional; the DXF sheets are left out, and said so
            DX = mod("export_dxf")
        except ImportError:
            DX = None
            print("ezdxf is not installed: the DXF sheets are not hashed", file=sys.stderr)

        def _r(v):
            return round(float(v), 3)

        def dxf(key, elev, face):
            """An elevation DXF's entities, in drawing order: type, layer, rounded geometry and
            text. Byte-hashing a DXF hashes its creation time."""
            import ezdxf
            path = os.path.join(tmp, "sheet.dxf")
            if os.path.exists(path):
                os.remove(path)        # a refusal writes nothing, so never hash the last face's file
            try:
                res = DX.export_elevation_dxf(elev, path, face=face)
                if isinstance(res, dict) and (res.get("error") or res.get("refusal")):
                    out[key] = "REFUSED"
                    return
                doc = ezdxf.readfile(path)
                rows = []
                for e in doc.modelspace():
                    d = e.dxf
                    row = [e.dxftype(), d.get("layer", "")]
                    for attr in ("start", "end", "insert", "center"):
                        if d.hasattr(attr):
                            row.append([_r(c) for c in d.get(attr)])
                    for attr in ("radius", "height", "start_angle", "end_angle", "width"):
                        if d.hasattr(attr):
                            row.append(_r(d.get(attr)))
                    if e.dxftype() == "LWPOLYLINE":
                        row.append([[_r(c) for c in p] for p in e.get_points()])
                    elif e.dxftype() == "HATCH":
                        row.append([[[_r(c) for c in v] for v in path.vertices]
                                    for path in e.paths if hasattr(path, "vertices")])
                    elif e.dxftype() in ("TEXT", "MTEXT"):
                        row.append(e.dxf.text if e.dxftype() == "TEXT" else e.text)
                    rows.append(row)
                out[key] = hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:16]
            except Exception as e:  # recorded, never dropped
                out[key] = "ERR " + type(e).__name__

        def draw(key, fn, *args, **kw):
            path = os.path.join(tmp, "sheet.svg")
            try:
                fn(*args, path, **kw)
                out[key] = sha(path)
            except Exception as e:  # recorded, never dropped
                out[key] = "ERR " + type(e).__name__

        paths = sorted(glob.glob("plans/*.json")) + sorted(glob.glob("plans/reference/*.json"))
        for f in paths:
            pid = os.path.basename(f)[:-5]
            with open(f, encoding="utf-8") as fh:
                placed = GEO.solve(json.load(fh), engine="heuristic")
            for reg in RP.REGISTERS:
                draw(f"{pid}/plan-{reg}", RP.render, placed, register=reg)
            sec = ST.build_section(placed, None, geometry_result=placed)
            if "error" in sec:
                continue
            draw(f"{pid}/section", RS.render_section, sec)
            roof = RF.build_roof(placed, None, section=sec)
            if "error" not in roof:
                draw(f"{pid}/roof", RR.render_roof, roof)
            elev = EL.build_elevation(placed, None, section=sec)
            if "error" not in elev:
                for face in "SNEW":
                    draw(f"{pid}/elev-{face}", RE.render_elevation, elev, face=face)
                if DX is not None:
                    for face in "SNEW":
                        dxf(f"{pid}/dxf-elev-{face}", elev, face)
            if "error" not in roof:
                try:
                    sc = SC.build_scene(placed, sec, roof, elev if "error" not in elev else None)
                    out[f"{pid}/scene"] = hashlib.sha256(json.dumps(
                        sc, sort_keys=True, default=str).encode()).hexdigest()[:16]
                except Exception as e:  # recorded, never dropped
                    out[f"{pid}/scene"] = "ERR " + type(e).__name__
        return out
    finally:
        os.chdir(here)
        shutil.rmtree(tmp, ignore_errors=True)


def diff(a, b):
    """The sheets that differ between two digests, and the sheets on one side only."""
    moved = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
    only_a = sorted(a.keys() - b.keys())
    only_b = sorted(b.keys() - a.keys())
    return {"moved": moved, "only_in_first": only_a, "only_in_second": only_b,
            "sheets": len(a.keys() | b.keys())}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.dirname(HERE),
                    help="the checkout to hash (default: this one)")
    ap.add_argument("--out", help="write the digest here as JSON (default: stdout)")
    ap.add_argument("--diff", nargs=2, metavar=("A", "B"), help="compare two digests")
    args = ap.parse_args(argv)
    if args.diff:
        with open(args.diff[0], encoding="utf-8") as fa, open(args.diff[1], encoding="utf-8") as fb:
            d = diff(json.load(fa), json.load(fb))
        print(f'{len(d["moved"])} of {d["sheets"]} sheets moved')
        for k in d["moved"]:
            print("  moved  ", k)
        for k in d["only_in_first"]:
            print("  gone   ", k)
        for k in d["only_in_second"]:
            print("  new    ", k)
        return 0
    res = digest(args.root)
    text = json.dumps(res, indent=0, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        print(text)
    errs = sum(1 for v in res.values() if str(v).startswith("ERR"))
    print(f"{len(res)} sheets hashed; {errs} errors", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
