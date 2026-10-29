"""The shipped record a surface may still DRAW, found rather than assumed (WP-13.4).

Lucas ruled 15 Sep 2026 that a placement breaking a hard fact of the type is REFUSED, not
drawn. Measured on this tree the moment that landed: **15 of the 16 shipped plan records are
refused on `auto` and 14 of 16 on the heuristic** -- every one of them for `bearing` (continuity
plus `structure.span_check`'s over-capacity count), most also for `tiling`, and the two shipped
plans additionally for `stacks`. That is the honest cost of the ruling and it is reported in the
package's own report beside WP-13.3's infeasible-now-named count.

So every server test that asks a drawing route for a picture stopped being a test of the picture
and became a test of the refusal -- which is not what those files are about. They take a
DRAWABLE record from here instead, and the record is **searched for rather than named**: a
literal filename would be one plan's luck, and the day that plan's placement moves the file
would go red on something it is not about (this repository has re-cut four guards for exactly
that, and the fixture rule is written down in CLAUDE.md).

**IT SKIPS RATHER THAN PASSING WHERE NOTHING IS DRAWABLE.** If every shipped record is refused
there is no picture to assert anything about, and a green tick over that would be a claim about
a drawing nobody made. `tests/test_refusal.py` and `workbench/server/tests/test_refusal_routes.py`
assert the OTHER half -- that the refusal is live on this corpus -- so the two together cannot
both go quiet: a tree where nothing is refused reddens there, and a tree where nothing is
drawable skips here with its reason printed.

The search is ordered cheapest-first and stops at the first record that holds, because `_placed`
runs `auto` and a cold CP solve is tens of seconds. `ORDER` is a HINT about cost and never a
claim about which record draws -- `_find` reads the verdict, so a stale order costs seconds and
can cost nothing else."""
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

# THE SEARCH IS `corpus.first_drawable` SINCE PHASE 17: the front door's hero plate is the same
# record, so the rule lives in the server once and this helper reads it.
def _find():
    """`(path, tried)`: the first shipped record `corpus._placed` does not refuse, and how many
    were tried -- `corpus.first_drawable`, memoised there for the process."""
    from workbench.server import corpus
    return corpus.first_drawable()


def drawable_plan():
    """A shipped plan record whose type facts HOLD, so a surface may draw it. Skips, naming the
    count it swept, where the ruling leaves nothing in this corpus drawable."""
    p, tried = _find()
    if p is None:
        pytest.skip(f"COULD NOT EVALUATE: none of the {tried} shipped plan records is drawable "
                    f"under the 15 Sep 2026 ruling -- every one carries a downgraded type fact, "
                    f"so there is no picture for this file to assert anything about. See "
                    f"workbench/server/tests/test_refusal_routes.py for the census.")
    return json.load(open(p, encoding="utf-8"))


def drawable_plan_id():
    """Which record `drawable_plan()` found, for a failure message that says which house."""
    p, _ = _find()
    return None if p is None else os.path.splitext(os.path.basename(p))[0]


def skip_if_refused(res, what):
    """Skip, in the refusal's own words, where a route or a corpus call refused to draw.

    A test about WHICH FACE the pen drew, or about two plates naming one input, is not a test
    of the refusal -- and the record it needs may be one the 15 Sep 2026 ruling no longer lets
    any surface draw. COULD NOT EVALUATE is the honest verdict there; a green tick would be a
    claim about a drawing nobody made, and deleting the test would lose the question.

    Takes an httpx `Response` or a plain dict, so the same reader serves both sides."""
    body = res if isinstance(res, dict) else res.json()
    if not isinstance(body, dict):
        return body
    # A refusal reaches a caller two ways: straight off `corpus._placed`, and wrapped in
    # FastAPI's `detail` by the route that raised the 422. Written out rather than as one
    # `or` chain with a ternary in it, which is how the first draft of this line bound its
    # `if` to the whole expression and quietly read the wrong half.
    detail = body.get("detail")
    ref = body.get("refused_placement")
    if ref is None and isinstance(detail, dict):
        ref = detail.get("refused_placement")
    if ref:
        pytest.skip(f"COULD NOT EVALUATE -- {what}: this placement is refused under the "
                    f"15 Sep 2026 ruling and no surface draws it. "
                    + " ".join(ref.get("lines") or [])[:300])
    return body
