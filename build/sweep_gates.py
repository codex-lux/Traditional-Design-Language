#!/usr/bin/env python3
"""sweep_gates.py — what endorsing a pack actually TURNS ON, measured before and after.

WHY THIS IS NOT IN `check_inheritance.py`. Five of the packs in OQ 51's backlog are read at
runtime by `structure.py`, `elevation.py` and `geometry_cp.py`: their `applies_to` list is not
bookkeeping, it is a live gate. Adding a node to one of them is a code change with no diff --
`graduation_check` starts running on that style and its plans can now FAIL it; `span_check`
switches its capacity from the light-frame joist table to the timber bay module; the elevation
generator starts composing a classical front. WP-8.2 named this in `--gates` and could only say
WHICH function; nothing measured WHAT MOVED.

So this file restyles the two reference plans onto every style the pack reaches and reports the
gate's own verdict per style. Run it BEFORE an endorsement and again after, and diff:

    python3 build/sweep_gates.py storey-graduation --json > /tmp/before.json
    # ... author the endorsement ...
    python3 build/sweep_gates.py storey-graduation --json > /tmp/after.json
    diff /tmp/before.json /tmp/after.json

It lives here rather than in the meter because it imports the generators (elevation, structure,
geometry_cp) and the meter deliberately does not -- `check_all` runs the meter 42 times a build
and this takes minutes.

THE RULE THIS SERVES, from CLAUDE.md: verifying a corpus-wide change on the plans that happen to
ship is verifying it on 2 of 164 styles. The probe is `probe = dict(plan); probe["style"] = s`,
which is `check_division_guards.py::measured_zeros`' own method.

UNJUDGED IS NOT PASSED. A style whose probe raises is reported `"error"`, never omitted and never
counted as applicable:false -- an exception is a state this tool could not evaluate, and silently
dropping it would make an endorsement look inert when it may not be.
"""
import argparse
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

PLANS = ("plans/spec-builder-colonial.json", "plans/tidewater-georgian-careful.json")

# Which gate each pack arms. Mirrors `check_inheritance.GATES`, which names the FILE and FUNCTION;
# this table says how to ASK the gate. A pack absent here has no live gate and the tool says so
# rather than pretending to measure one.
GATED = ("storey-graduation", "timber-bay", "opening-proportion", "facade-classical", "gibbs-ionic")


def _mod(name, rel):
    return modcache.load(name, os.path.join(ROOT, rel))


def pack_record(pid):
    import glob
    for p in sorted(glob.glob(os.path.join(ROOT, "proportions", "*", "*.json"))):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if d.get("id") == pid:
            return d
    return None


def styles_to_sweep(pid):
    """The pack's own applies_to, PLUS every node the backlog says it reaches unendorsed.

    Both halves matter: the first is what the gate fires on today, the second is what an
    endorsement would add. Sweeping only the first cannot show a change."""
    pack = pack_record(pid)
    if pack is None:
        sys.exit(f"no such pack: {pid}")
    have = set(pack.get("applies_to") or [])
    ci = _mod("check_inheritance", "build/check_inheritance.py")
    g = ci.load()
    _b, gaps, _p, _d = ci.measure(g)
    applies = ci.applies_to_index()
    pending = {t[0] for t in gaps if t[3] == pid and t[0] not in applies.get(t[3], ())}
    return sorted(have | pending), have, pending


def probe_for(plan, style):
    p = dict(plan)
    p["style"] = style
    return p


def sweep(pid, verbose=False):
    structure = _mod("structure", "build/structure.py")
    elevation = _mod("elevation", "build/elevation.py")
    styles, have, pending = styles_to_sweep(pid)
    plans = [(rel, json.load(open(os.path.join(ROOT, rel)))) for rel in PLANS]

    out = {"pack": pid, "endorsed_today": sorted(have), "unendorsed_reaching": sorted(pending),
           "styles": {}}
    for s in styles:
        per_plan = {}
        for rel, plan in plans:
            probe = probe_for(plan, s)
            try:
                if pid == "storey-graduation":
                    # THE KEY IS `storey_graduation`, AND THE FIRST VERSION OF THIS READ
                    # `graduation`. `.get()` returned None on every style, so the sweep printed
                    # "off, 0 findings" for all 128 -- including the styles the pack already
                    # endorses -- and would have shown NO CHANGE after an endorsement. An
                    # instrument that cannot move is worse than a test that cannot fail, because
                    # its output is a number rather than a green tick (`workbench/scripts/load.py`
                    # misreported three times the same way). Caught by noticing that an endorsed
                    # style read the same as an unendorsed one.
                    sec = structure.build_section(probe)
                    grad = sec.get("storey_graduation") or {}
                    fs = grad.get("findings") or []
                    per_plan[rel] = {"applicable": bool(grad.get("applicable")),
                                     "findings": len(fs),
                                     # A finding that PASSES is the check working, not a defect.
                                     # Counting only the total would call an armed, satisfied
                                     # check identical to an unarmed one.
                                     "failures": sum(1 for f in fs if f.get("ok") is False)}
                elif pid == "timber-bay":
                    # The list itself is the gate; report what span_check would read.
                    applies = structure._timber_bay_applies_to()
                    per_plan[rel] = {"applicable": s in applies,
                                     "capacity_basis": "timber bay module" if s in applies
                                                       else "light-frame joist table"}
                elif pid in ("opening-proportion", "facade-classical"):
                    el = elevation.build_elevation(probe)
                    per_plan[rel] = {"applicable": bool(el.get("applicable")),
                                     "measurements": len(el.get("measurements") or {})}
                elif pid == "gibbs-ionic":
                    el = elevation.build_elevation(probe)
                    m = el.get("measurements") or {}
                    per_plan[rel] = {"applicable": bool(el.get("applicable")),
                                     "gibbs_order_applies_to_style":
                                         m.get("gibbs_order_applies_to_style")}
                else:
                    per_plan[rel] = {"applicable": None,
                                     "note": "no live gate — endorsing moves the meter only"}
            except Exception as e:                     # noqa: BLE001 — reported, never swallowed
                per_plan[rel] = {"error": "%s: %s" % (type(e).__name__, str(e)[:160])}
        out["styles"][s] = per_plan
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pack")
    ap.add_argument("--json", action="store_true", help="machine-readable, for diffing")
    a = ap.parse_args()

    if a.pack not in GATED:
        print(f"{a.pack} arms no live gate. Endorsing it moves the OQ 51 meter and changes no "
              f"behaviour; there is nothing here to sweep.\nGated packs: {', '.join(GATED)}")
        return 0

    res = sweep(a.pack)
    if a.json:
        print(json.dumps(res, indent=1, sort_keys=True))
        return 0

    print(f"{res['pack']}: {len(res['endorsed_today'])} style(s) endorsed today, "
          f"{len(res['unendorsed_reaching'])} reaching it unendorsed")
    tally = collections.Counter()
    for s, per in sorted(res["styles"].items()):
        bits = []
        for rel, v in per.items():
            short = os.path.basename(rel).replace(".json", "")
            if "error" in v:
                tally["error"] += 1
                bits.append(f"{short}=COULD NOT EVALUATE ({v['error']})")
            else:
                tally["applicable" if v.get("applicable") else "not applicable"] += 1
                extra = {k: x for k, x in v.items() if k != "applicable"}
                bits.append(f"{short}={'ON' if v.get('applicable') else 'off'}"
                            + (f" {extra}" if extra else ""))
        mark = " *" if s in res["unendorsed_reaching"] else "  "
        print(f"{mark}{s:36s} " + " | ".join(bits))
    print("\n* = reaching this pack unendorsed; endorsing it flips these rows.")
    print("   " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
