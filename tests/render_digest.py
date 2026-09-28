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
