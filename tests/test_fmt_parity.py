"""The workbench's feet-inches notation is the engine's, held from both sides (WP-14.6).

`build/proportion_engine.py::_fmt_in` writes every inch figure a CLI or a printed plate in this
corpus prints. `workbench/app/src/fmt.js::feetInches16` is its port for the workbench, and a port is
a second spelling of a rule, so the two are held to one answer here rather than trusted to agree.

Two halves, and they catch different things:

1. THE TABLE. `workbench/app/src/fmt.test.mjs` carries a vector table as a JSON array literal
   between `/* VECTORS-BEGIN */` and `/* VECTORS-END */`. That file asks the JS port for each
   string; this one extracts the same text and asks `_fmt_in`. So a row is a claim about both
   functions, and neither side can be edited to make it true alone. It needs nothing but Python.

2. THE SWEEP. A few thousand inputs -- every sixty-fourth of an inch across eighty inches, the
   values that sit exactly on a half-sixteenth (where round-half-to-even and round-half-up part),
   the values a hair either side of a carry, vanishing negatives, and a seeded spread of arbitrary
   floats -- are run through BOTH languages and compared one by one. A port that rounds a half up
   passes most of a hand-written table and fails this in hundreds of places. It needs `node`; where
   there is none it is SKIPPED, by name, as COULD NOT EVALUATE, which is not a pass.

THE CARRY WAS FIXED ON BOTH SIDES AT WP-14.20. Until then `_fmt_in` carried a sixteenth into the
inch and stopped there, so 23.99 printed `1'-12"` -- reproduced by the port, not endorsed (PRD
§I.8). A twelve-inch figure is a foot, and both functions carry it into the foot now: 23.99 prints
`2'-0"`. `test_the_sixteenth_carries_through_the_inch_into_the_foot` is that row, and the
invariant under it -- no output in the sweep has an inch figure of twelve -- is what makes it a rule
rather than one value. Every other output the engine prints was measured before and after the
change and none moved (docs/reports/wp-14.20-small-server-truths.md).
"""
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache  # noqa: E402

PE = modcache.load("proportion_engine", os.path.join(ROOT, "build", "proportion_engine.py"))
APP = os.path.join(ROOT, "workbench", "app", "src")
TABLE_FILE = os.path.join(APP, "fmt.test.mjs")
PORT = os.path.join(APP, "fmt.js")

BEGIN, END = "/* VECTORS-BEGIN */", "/* VECTORS-END */"

# An inch figure of twelve: a whole foot prints as the foot and "0", so "12\"" at the end of an
# output is a foot left in the inches. Since WP-14.20 it must never appear.
TWELVE_INCHES = re.compile(r"(^|-)12\"$")


def _on_a_half_sixteenth(x):
    """True where `_fmt_in` hands `round()` an exact half -- read off the engine's own divmod."""
    if not math.isfinite(x):
        return False
    rem = divmod(x, 12)[1]
    return ((rem - int(rem)) * 16) % 1 == 0.5


def _carries_into_the_foot(x):
    """True where the remainder `_fmt_in` hands on reaches twelve inches -- by a sixteenth rounding up
    to sixteen, or with no sixteenth at all when `divmod` itself returns 12.0 for a vanishing
    negative. Read off the engine's own divmod and round, as `_on_a_half_sixteenth` is."""
    if not math.isfinite(x):
        return False
    rem = divmod(x, 12)[1]
    whole = int(rem)
    return whole + (round((rem - whole) * 16) == 16) == 12


def _table():
    src = open(TABLE_FILE, encoding="utf-8").read()
    b, e = src.find(BEGIN), src.find(END)
    assert b > 0 and e > b, f"{TABLE_FILE} must carry {BEGIN} ... {END}, in that order"
    return json.loads(src[b + len(BEGIN):e])


def test_the_table_is_what_the_engine_prints():
    rows = _table()
    assert len(rows) >= 14, "the table must carry at least the fourteen rows PRD §I.8 names"
    wrong = [(x, want, PE._fmt_in(x)) for x, want in rows if PE._fmt_in(x) != want]
    assert not wrong, "the table says something _fmt_in does not:\n" + "\n".join(
        f"  _fmt_in({x!r}) = {got!r}, the table says {want!r}" for x, want, got in wrong)


def test_the_table_exercises_both_behaviours_a_natural_port_gets_wrong():
    """A table that happened to hold no half-sixteenth and no carry would agree with a naive port
    too, and the first half of this file would then be proving nothing about the two behaviours
    PRD §I.8 names. So the premise is asserted from the ENGINE, not from the table's own words."""
    rows = _table()
    halves = [x for x, _ in rows if isinstance(x, float) and _on_a_half_sixteenth(x)]
    assert halves, "no row sits exactly on a half-sixteenth, so round-half-up would pass the table"
    carries = [x for x, _ in rows if isinstance(x, float) and _carries_into_the_foot(x)]
    assert carries, "no row carries a remainder of twelve inches into the foot"
    assert any(x < 0 and divmod(x, 12)[1] == 12.0 for x in carries), (
        "no row reaches twelve inches with no sixteenth at all, so a carry tested on the sixteenth "
        "rather than on the inch would pass the table")


def test_the_sixteenth_carries_through_the_inch_into_the_foot():
    """WP-14.20. Twelve inches is a foot, so a sixteenth that rounds the inch up to twelve carries
    on into the foot: 23.99 in is `2'-0"`, never `1'-12"`. The three rows the old behaviour got wrong
    in three different ways, then the invariant over the whole sweep -- a rule, not three values."""
    assert PE._fmt_in(23.99) == "2'-0\""
    assert PE._fmt_in(11.97) == "1'-0\""
    assert PE._fmt_in(-1e-20) == '0"', "divmod's 12.0 remainder with no sixteenth carries too"
    twelve = [(x, PE._fmt_in(x)) for x in _sweep_inputs() if TWELVE_INCHES.search(PE._fmt_in(x))]
    assert not twelve, (f"{len(twelve)} outputs still print twelve inches; the first five: "
                        + ", ".join(f"{x!r} -> {o}" for x, o in twelve[:5]))


def test_the_engine_refuses_what_the_port_refuses():
    """The port throws on NaN and the infinities rather than printing `-`, which is the corpus's
    mark for a figure that is ABSENT. That is only honest if the engine refuses them as well."""
    for x in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises((ValueError, OverflowError)):
            PE._fmt_in(x)
    with pytest.raises(TypeError):
        PE._fmt_in("8.5")


def _sweep_inputs():
    xs = []
    xs += [k / 64 for k in range(-40 * 64, 40 * 64 + 1)]                 # every 1/64 in, +/-40 in
    xs += [(2 * k + 1) / 32 + 12 * f for k in range(16) for f in (-3, -1, 0, 1, 7)]  # half-16ths
    for whole in range(-24, 25):                                            # either side of a carry
        for d in (1e-9, 1e-6, 0.001, 0.01, 0.03):
            xs += [whole + 1 - d, whole + 1 + d, whole + 15.5 / 16 - d, whole + 15.5 / 16 + d]
    xs += [1e-20, -1e-20, 5e-324, -5e-324, 1e-300, -1e-300, 0.0, -0.0, 1e15 + 0.5, -1e15 - 0.5,
           1e20, -1e20, 2.0 ** 53, -(2.0 ** 53), 114.0, 108.0, 102.3157894736842]
    rng = random.Random(146)
    xs += [rng.uniform(-600, 600) for _ in range(3000)]
    xs += [rng.uniform(-2, 2) for _ in range(1000)]
    return [float(x) for x in xs]


NODE_SCRIPT = r"""
import { readFileSync } from 'node:fs';
const { feetInches16 } = await import(process.argv[1]);
const xs = JSON.parse(readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(xs.map((x) => {
  try { return feetInches16(x); } catch (e) { return { raises: e.name }; }
})));
"""


def _node():
    node = shutil.which("node")
    if not node:
        return None, "node is not on PATH"
    ver = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
    try:
        major = int(ver.lstrip("v").split(".")[0])
    except ValueError:
        return None, f"node reported no version ({ver!r})"
    if major < 18:
        return None, f"node {ver} predates the module features the sweep uses"
    return node, None


def test_the_port_and_the_engine_agree_on_a_sweep():
    node, why = _node()
    if not node:
        pytest.skip(f"COULD NOT EVALUATE -- {why}; the table half above still ran")
    xs = _sweep_inputs()
    # json.dumps writes a float by repr, which JSON.parse reads back to the same double, so both
    # languages are handed bit-identical inputs.
    payload = json.dumps(xs)
    url = "file://" + PORT
    r = subprocess.run([node, "--input-type=module", "-e", NODE_SCRIPT, url],
                       input=payload, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"node could not run the port:\n{r.stderr}"
    got = json.loads(r.stdout)
    assert len(got) == len(xs), "node answered a different number of inputs than it was asked"
    wrong = [(x, g, PE._fmt_in(x)) for x, g in zip(xs, got) if g != PE._fmt_in(x)]
    assert not wrong, (f"{len(wrong)} of {len(xs)} inputs disagree; the first ten:\n"
                       + "\n".join(f"  {x!r}: port {g!r}, _fmt_in {w!r}" for x, g, w in wrong[:10]))


def test_the_sweep_covers_what_it_claims_to():
    """The sweep's value is the inputs where a naive port parts from the engine. Count them from
    the ENGINE's side -- the values whose sixteenths land exactly on a half, and the values whose
    sixteenth carries -- so a sweep that quietly lost them cannot pass for one that has them."""
    xs = _sweep_inputs()
    on_half = [x for x in xs if _on_a_half_sixteenth(x)]
    carried = [x for x in xs if _carries_into_the_foot(x)]
    assert len(on_half) >= 100, f"only {len(on_half)} sweep inputs sit on a half-sixteenth"
    assert len(carried) >= 50, f"only {len(carried)} sweep inputs carry twelve inches into the foot"
