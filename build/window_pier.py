#!/usr/bin/env python3
"""window_pier.py -- the wall between two windows: its floor, its aim, and the styles the floor
spares (WP-16.6; R5 and R5b, ruled 29 Sep 2026).

Until this package the placer kept ONE FOOT between two windows (`openings.MIN_SOLID_FT`), inside
one room only, and the corpus states the pier three ways:

  the fault       `faults/pier-narrower-than-the-opening.json`: pier / opening at least 1.0,
                  "the measured lower bound across surviving Anglo-American fronts";
  the pack        sash-light's `minimum_solid_between_openings`: `opening_width * 1.4`, the
                  "number that looks right" (its own note), 1.2 to 2.0 across the tradition;
  a style's kit   georgian-colonial-american's `pier_measured_ratio`, an editorial 0.6 to 1.0.

Measured on the sixteen shipped plans before this package (`tests/window_piers.py`): 35 piers
between two drawn windows, 24 narrower than the wider window beside them, 12 exactly the placer's
foot. Lucas ruled (R5): a FLOOR of 1.0 x the wider window, an AIM of 1.4 x where the wall allows,
and a window that cannot be seated is refused by name. R5b: the floor spares the five styles the
pier fault licenses, and the placer reads the licence's style list, not its checks.

THIS FILE IS THE ONE READER of all three, for the placer (`openings._place_windows`), the
composer's window cap (`compose`) and the census (`tests/svg_census.py` V26), so no reader carries
a transcribed 1.0 or 1.4:

  the floor   READ from the fault's primary test (at-least, a ratio), as
              `elevation._load_alignment_tolerance` reads the alignment fault's figure. A fault
              that states no such figure leaves the floor UNJUDGED, and the placer then keeps its
              old foot and says why: a floor nobody stated is not a floor of zero.
  the aim     sash-light's rule, evaluated at the wider window's width, WHERE IT IS DELIVERED to
              the style (the approved plan's reading of R5: "the 1.4 x aim is read from sash-light
              where it is delivered"). `resolve_kit.eval_packs` is the reader, so a pack the
              opt-in gate withholds, the style declines or the kit forbids at that slot gives no
              aim, and the reason is the cascade's own sentence. 53 of 164 nodes receive it,
              measured 1 Oct 2026; on the shipped plans `italian-renaissance-revival`,
              `new-classical`, `new-urbanist-traditional`, `log-vernacular-american` and
              `contemporary-traditional` do not, and their windows are seated to the floor alone.
  the spared  the styles the fault's `exceptions[].style` name, read by EXACT id -- the reading
              every licence in this corpus has
              (`oq/a-licence-matches-the-style-id-exactly-and-never-its-descendants`), stated
              here so it is not mistaken for a choice. Their
              `bounds_test`s and `granted_when`s are the fault's to judge and are NOT read: R5b
              says the placer reads the list, not the checks.

A LEAF beside `doorcase.py`: it loads `proportion_engine` and `resolve_kit`, and nothing that
loads `openings` (geometry loads openings, so openings may not load anything that loads geometry).
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAULT_PATH = os.path.join(ROOT, "faults", "pier-narrower-than-the-opening.json")
AIM_PACK = "sash-light"
AIM_SLOT = "window_grouping_rule"
AIM_DIMENSION = "minimum_solid_between_openings"

_CACHE = {}


def _mod(name, path):
    # build/modcache.py, never a local loader (OQ 28; tests/test_modcache.py counts loads)
    b = os.path.join(ROOT, "build")
    if b not in sys.path:
        sys.path.insert(0, b)
    import modcache as _mc
    return _mc.load(name, path)


def _shown(path):
    return os.path.relpath(path, ROOT) if os.path.abspath(path).startswith(ROOT) else path


def _fault(path=None):
    path = path or FAULT_PATH
    key = ("fault", path)
    if key not in _CACHE:
        try:
            with open(path, encoding="utf-8") as fh:
                _CACHE[key] = (json.load(fh), None)
        except (OSError, ValueError) as e:
            _CACHE[key] = (None, f"{_shown(path)} could not be read ({e})")
    return _CACHE[key]


def floor(path=None):
    """`(ratio, source)`, or `(None, reason)` where the fault states no at-least ratio on its
    primary test. The ratio is pier over the WIDER window."""
    rec, err = _fault(path)
    shown = _shown(path or FAULT_PATH)
    if rec is None:
        return None, err
    t = rec.get("test") or {}
    if t.get("direction") == "at-least" and t.get("units") == "ratio" and \
            isinstance(t.get("threshold"), (int, float)):
        return float(t["threshold"]), f"{shown}#test.threshold"
    return None, (f"{shown} states no at-least ratio on its primary test, so no floor between two "
                  f"windows is stated anywhere")


def spared(path=None):
    """`{style: source}`: the styles the fault's exceptions name, by exact id (R5b)."""
    rec, _err = _fault(path)
    shown = _shown(path or FAULT_PATH)
    out = {}
    for i, e in enumerate((rec or {}).get("exceptions") or []):
        if e.get("style"):
            out[e["style"]] = f"{shown}#exceptions[{i}].style"
    return out


def _aim_row(style):
    """sash-light's delivered row at `window_grouping_rule`, or `(None, reason)`."""
    if ("aim", style) in _CACHE:
        return _CACHE[("aim", style)]
    RK = _mod("resolve_kit", os.path.join(ROOT, "build", "resolve_kit.py"))
    try:
        g = RK.load_graph()
        if style not in g.get("nodes", {}):
            out = (None, f"'{style}' is not a node of the style graph, so no pack reaches it")
        else:
            chain = RK.chain_for(g, style)
            slots, _ = RK.resolve_slots(g, chain, RK.scope_for(g, style))
            by_slot, _errs = RK.eval_packs(RK.resolve_packs(g, chain), {}, None, slots,
                                           withheld=RK.withheld_for(g, style))
            rows = [r for r in by_slot.get(AIM_SLOT, [])
                    if r.get("pack") == AIM_PACK and r.get("dimension") == AIM_DIMENSION]
            live = [r for r in rows if not r.get("withheld_by_opt_in") and not r.get("refused_by_kit")]
            if live:
                out = (live[0], None)
            elif rows:
                r = rows[0]
                out = (None, r.get("withheld_because") or r.get("refused_because")
                       or f"{AIM_PACK}'s {AIM_DIMENSION} is not delivered to '{style}'")
            else:
                out = (None, f"{AIM_PACK} does not reach '{style}' at {AIM_SLOT}, so no pack the "
                             f"style receives states an aim for the wall between two windows")
    except SystemExit:
        out = (None, f"the kit of '{style}' could not be resolved")
    _CACHE[("aim", style)] = out
    return out


def rule(style, path=None):
    """Everything the placer needs to seat a window beside another, for one style, with sources.

    `{"floor": ratio|None, "floor_source": str|None, "floor_unjudged": reason|None,
      "aim": {"expression", "pack", "from", "range"}|None, "aim_why": reason|None,
      "spared": bool, "spared_source": str|None}`"""
    key = ("rule", style, path)
    if key in _CACHE:
        return _CACHE[key]
    f, fsrc = floor(path)
    sp = spared(path)
    row, why = _aim_row(style)
    out = {"style": style,
           "floor": f, "floor_source": fsrc if f is not None else None,
           "floor_unjudged": None if f is not None else fsrc,
           "aim": ({"expression": row["expression"], "pack": row["pack"], "from": row.get("from"),
                    "range": row.get("range"),
                    "source": f"proportions/modules/{AIM_PACK}.json ({AIM_SLOT}, {AIM_DIMENSION})"}
                   if row else None),
           "aim_why": why,
           "spared": style in sp, "spared_source": sp.get(style)}
    _CACHE[key] = out
    return out


def floor_ft(rule_, wider_ft):
    """The least wall between two windows, the wider `wider_ft` wide; None where none is stated."""
    if rule_ is None or rule_.get("floor") is None:
        return None
    return rule_["floor"] * wider_ft


def aim_ft(rule_, wider_ft):
    """The wall the pack aims at between two windows, never below the floor; None where no aim
    reaches the style. The pack's expression is evaluated at the wider window's width in inches,
    because that is its unit (`opening_width * 1.4`, `units: in`)."""
    if rule_ is None or not rule_.get("aim"):
        return None
    PE = _mod("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
    try:
        v = float(PE.evaluate_expr(rule_["aim"]["expression"], {"opening_width": wider_ft * 12.0}))
    except Exception:
        return None
    fl = floor_ft(rule_, wider_ft)
    return max(v / 12.0, fl) if fl is not None else v / 12.0


def words(rule_):
    """The rule in one sentence, for a refusal and a report."""
    if rule_ is None:
        return "no pier rule"
    if rule_.get("spared"):
        return (f"the floor between two windows spares '{rule_['style']}' "
                f"({rule_['spared_source']}, R5b)")
    if rule_.get("floor") is None:
        return f"no floor between two windows is stated: {rule_['floor_unjudged']}"
    s = f"the wall between two windows at least {rule_['floor']:g} x the wider ({rule_['floor_source']})"
    if rule_.get("aim"):
        s += f", aiming at {rule_['aim']['expression']} where the wall allows ({rule_['aim']['source']})"
    else:
        s += f"; no aim, because {rule_['aim_why']}"
    return s
