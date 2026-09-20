# oq/the-opt-out-compose-still-judges-a-house-nobody-placed — WP-14.2 moved the verdict, and `--no-revise` did not come with it

*Status: OPEN · Raised in: WP-14.2, moving the verdict onto the placed house (20 September 2026)*

**Ruled 20 Sep 2026: the composer's verdict is about the PLACED house.** WP-14.2 executes that
for every candidate the revision loop reaches, and for a candidate the set budget skipped, which
is given a placement of its own (`rounds=0`) so `_sort_key` cannot leapfrog a measured candidate
on an unmeasured number. **`compose(revise=False)` is the one path left out, and it is left out
for a reason rather than by oversight.**

## What it costs to leave it

`--no-revise` returns candidates whose `counts`, `disqualified` and score axes are
`plan_check.check` on a record with no placement — so `plan_check.py:2593` derives the elevation
from a fresh heuristic placement solved inside the critic. That is the house nobody draws, and
it is the reading that convicted `truss-flattened-pitch` at **0.4488 against at-least 0.45**
where the placed reading clears it.

The candidate SAYS so — `verdict_basis: "declared"` — and the result says it of the pool with
`selected_on`. So nothing is silent. But a reader who passes `--no-revise` for speed is handed a
`DISQUALIFIED` band computed the old way, and the band's own sentence does not mention it.

## Why it was not simply fixed

Placing the returned set on the opt-out path is one `revise(rounds=0)` per candidate. On
`engine="heuristic"` that is cheap; on the default `revise_engine="auto"` each one is up to a
25 s proof, so a four-candidate opt-out compose could pay a hundred seconds to answer a question
the caller asked it to skip. **The per-candidate cost has NOT been measured here** and should be
before anything is built on this entry — quoting a guess for it would be the shape this corpus
names first.

And `--no-revise` is not only a speed switch: `check_all.py` runs the composer on the fast
engine, and four of `tests/`'s composer rows pin the RANKING through it. Those four are pinning a
SELECTION, which `selected_on` now correctly calls a declared reading — so they are not wrong,
and making the opt-out path place would change what they are about as well as what they cost.

## What has to be ruled

1. **Is `--no-revise` an opt-out from the LOOP or from the PLACEMENT?** If the first, the verdict
   should be placed there too and the cost is the answer to question 2. If the second, the
   declared verdict is correct on that path and the `disqualified` band should say which house it
   is about rather than leaving it to a neighbouring field.
2. **If it places, on which engine?** Taking the verdict on `heuristic` while the revised path
   takes it on `revise_engine` puts the set back on two instruments to save a second, which is
   the defect WP-14.2 removed one layer up.
3. **Does the disqualification sentence carry its own basis?** `disqualified_because` is
   server-authored at `compose.py:373-383` and names a count without naming the house. One
   sentence either way, and it is the sentence a reader acts on.

## What must not be done

- **Do not make the four composer rows green by placing the opt-out path.** Three of them are
  already red from WP-13.3 and WP-13.5 and a fourth from WP-13.3; changing their instrument while
  they are red for another cause is how a package's movement stops being attributable —
  `CLAUDE.md`'s own *a test already red for cause A cannot report cause B*.
- **Do not drop `verdict_basis` once the paths agree.** Its three states include `null`, which is
  a server that predates the field and an elevation that could not be derived, and neither may be
  read as either of the other two.
