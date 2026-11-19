"""The reinstatement pass offers a kind back as "everything no core named" before it goes pin by pin.

Found 19 Nov 2026 by `tests/test_composition.py`'s service-room row. On
`plans/tidewater-georgian-careful.json` the ladder released all 24 shape pins on round 4. A round
releases the whole of a kind (WP-11.7), and the core that round named three of them. The whole
restore came back INFEASIBLE, and the singles are budget-bound: the pass's 6 s window reached two of
them. So 22 rooms were drawn free of their own proportion band:

- the drawing room 45 x 10 across the whole rear;
- the butler's pantry on the entrance front, which its own record forbids.

Meanwhile the lower-ranked hearth, offered whole next, came back. That inverted the ladder's own
precedence, which ranks a room's band above the hearth (`geometry_cp._RANK`).

The pass now offers the kind less the pins any core named, in one solve, before the singles. On the
same record that restores 17 shape pins at once. 6 or 7 stay down where 22 or 23 did. The house
returns to `6fcc665`'s layout (the drawing room 18 x 22 at the front, the butler's pantry at the
rear), and the proof is refused for the hearth as well as the tiling. That is the stated
precedence's cost, and the report records it.

Measured on all sixteen shipped plans, serially on each tree: only this record takes the new step.
The prover's timing noise moves wall counts on others with or without the change.

CP-SAT under a wall clock is not reproducible, so these assert the pass's own record of what it
tried, and the outcome only in the direction the measurement separates by a factor of three. With no
proof, they are COULD NOT EVALUATE, never a pass.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "build"))
import modcache as mc  # noqa: E402

GEO = mc.load("geometry", os.path.join(ROOT, "build", "geometry.py"))


@pytest.fixture(scope="module")
def proof():
    plan = json.load(open(os.path.join(ROOT, "plans", "tidewater-georgian-careful.json")))
    out = GEO.solve(plan, engine="cp")
    s = (out.get("geometry_report") or {}).get("solver") or {}
    if s.get("engine") != "cp-sat":
        pytest.skip(f"COULD NOT EVALUATE: the proof did not place this record ({s.get('reason')})")
    return s


def test_a_kind_whose_whole_restore_fails_is_offered_back_less_its_cored_pins(proof):
    att = [a for a in (proof.get("attempts") or []) if a[1].startswith("R:")]
    whole = [i for i, a in enumerate(att)
             if a[0] == "restore shape x24" and a[1] == "R:INFEASIBLE"]
    if not whole:
        pytest.skip("COULD NOT EVALUATE: this run's ladder did not release the whole shape rank, "
                    f"so the step has nothing to follow ({[a[0] for a in att][:6]})")
    nxt = att[whole[0] + 1][0] if whole[0] + 1 < len(att) else ""
    assert nxt.startswith("restore shape x") and nxt.endswith("outside the cores"), (
        f"the whole shape restore failed and the next attempt is {nxt!r}, not the kind less its "
        f"cored pins -- the step that keeps 17 room bands is gone")


def test_most_room_bands_come_back(proof):
    down = proof.get("downgraded_shape_pins") or []
    assert len(down) <= 12, (
        f"{len(down)} of 24 room bands stay released ({down}). Before the step it was 22 or 23, "
        f"and with it 6 or 7, so over half released means the pass stopped winning the bands back")
