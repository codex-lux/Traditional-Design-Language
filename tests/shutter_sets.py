"""THE SHUTTER-LEAF FIGURES OF `oq/a-leaf-refused-for-a-neighbour-that-is-itself-refused`,
RE-DERIVED ON THE TREE THIS RUNS ON (WP-16.7). Committed so they can be re-derived rather than
quoted: the question published 232 of 255 against the placement before WP-16.6, and WP-16.6's pier
floor re-seated every window those figures were read off.

Over the census's elevation sheets that carry leaved windows -- every shipped-plan face and every
style's front, `svg_census._elev_and_sweep`, the population the question was measured on -- it
counts the windows refused their leaves three ways, all from the record the sheet is drawn from:

  * AS COMPOSED: every pair judged against every other pair as composed, the rule until WP-16.7;
  * ONE PASS: in the rects' own order, a refused pair withdrawn before the next window is judged
    (the second audit's mutation M3c, the question's middle row);
  * R7: what the record now refuses -- the largest set that can all be hung (ruled 29 Sep 2026).

A window refused for an opening or for the corner is refused in all three, and is counted in all
three. It also reports how many sheets offer more than one largest set, so that a tie-break key
decided which windows keep their leaves, and how each contended window was decided.

    python3 tests/shutter_sets.py [--json]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "build"))
import svg_census as C  # noqa: E402

EL = C.SURF._mod("elevation")


def _leaf(r):
    return r.get("shutter_leaf_width_in") or r.get("shutter_leaf_width_refused_in")


def _vo(a, b):
    return min(a["head_in"], b["head_in"]) - max(a["sill_in"], b["sill_in"]) > 0.01


def _clash(a, b):
    la, lb = _leaf(a), _leaf(b)
    sa = ((a["x0_in"] - la, a["x0_in"]), (a["x1_in"], a["x1_in"] + la))
    sb = ((b["x0_in"] - lb, b["x0_in"]), (b["x1_in"], b["x1_in"] + lb))
    return _vo(a, b) and any(min(a1, b1) - max(a0, b0) > 0.01 for a0, a1 in sa for b0, b1 in sb)


def measure():
    sheets = leaved = composed = one_pass = r7 = tied = 0
    keys = {}
    per = []
    for subject, el, _svg in C._elev_and_sweep():
        face = subject.split("/")[-1] if "/" in subject else el.get("entrance_face")
        rects = EL.opening_rects(el, face)["rects"]
        wins = [r for r in rects if r["kind"] == "window" and _leaf(r)]
        if not wins:
            continue
        sheets += 1
        leaved += len(wins)
        hard = {id(r) for r in wins
                if {"opening", "corner"} & set(r.get("shutters_refused_by") or ())}
        c = sum(1 for r in wins if id(r) in hard or any(_clash(r, o) for o in wins if o is not r))
        hung = []
        for r in wins:
            if id(r) not in hard and not any(_clash(r, o) for o in hung):
                hung.append(r)
        p = len(wins) - len(hung)
        n = sum(1 for r in wins if r.get("shutters_refused"))
        for r in wins:
            k = r.get("shutters_decided_by")
            if k:
                keys[k] = keys.get(k, 0) + 1
        t = any(r.get("shutters_decided_by") in ("symmetry", "outward", "face-order") for r in wins)
        tied += t
        composed += c
        one_pass += p
        r7 += n
        if c or p or n:
            per.append({"sheet": subject, "leaved": len(wins), "as_composed": c, "one_pass": p,
                        "r7": n, "tie_decided": t})
    return {"sheets_with_leaved_windows": sheets, "leaved_windows": leaved,
            "refused_as_composed": composed, "refused_one_pass": one_pass, "refused_r7": r7,
            "sheets_where_a_tie_break_decided": tied, "decided_by": keys, "sheets": per}


if __name__ == "__main__":
    got = measure()
    if "--json" in sys.argv:
        print(json.dumps(got, indent=1))
    else:
        print("%d sheets carry %d leaved windows; refused their leaves: as composed %d, one pass %d, "
              "R7 %d; a tie-break decided on %d sheet(s); decided by %s" % (
                  got["sheets_with_leaved_windows"], got["leaved_windows"], got["refused_as_composed"],
                  got["refused_one_pass"], got["refused_r7"], got["sheets_where_a_tie_break_decided"],
                  json.dumps(got["decided_by"], sort_keys=True)))
        for s in got["sheets"]:
            print("  %(sheet)s: %(leaved)d leaved, as composed %(as_composed)d, one pass %(one_pass)d, "
                  "R7 %(r7)d%(t)s" % dict(s, t=" (a tie-break decided)" if s["tie_decided"] else ""))
