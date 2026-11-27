# oq/one-worker-runs-one-search-and-the-seed-decides-as-much-as-the-house — on one core a hard step's time is heavy-tailed, and one search cannot cover the tail

*Status: OPEN · Raised in: the one-worker search (27 November 2026)*

**OPEN — on one worker a walls-released hard step runs one search, and whether it answers inside
its slice depends on the seed about as much as on the house. Lucas ruled the no-LP search for one
worker on 27 Nov 2026, which meets his bar on the stock brief 3 runs of 3. It also cost the second
brief one drawable house on the one run measured.**

## What was measured (27 Nov 2026, one four-core container, one run at a time)

The stock Georgian brief's composed double pile, the record the declared loop hands on, one
walls-released hard step at +2 ft, one worker, the default search:

| seed | result |
|---|---|
| 7 | OPTIMAL 46.9 s |
| 3 | OPTIMAL 31.5 s |
| 1 | UNKNOWN at 100 s |
| 2 | UNKNOWN at 100 s |

The same model under the no-LP search: OPTIMAL in 8.2 to 8.6 s on seeds 7, 1 and 2. Four workers,
which run three searches side by side: 14.3 s.

`bungalow-small`'s `bungalow-open-linear`, the record the compose of four places, one worker, 30 s
cap, seeds 7, 1 and 2:

| depth | default search | no-LP search |
|---|---|---|
| +0 ft | OPTIMAL 26.4, 21.5, 4.5 s | UNKNOWN, OPTIMAL 21.8 s, OPTIMAL 1.0 s |
| +2 ft | UNKNOWN, OPTIMAL 8.4 s, UNKNOWN | OPTIMAL 11.3, 3.2, 19.7 s |

In the compose, at seed 7, that house held at its derived depth under the default search and was
drawable. Under no LP it held 2 ft deeper and the house placed there is NOT DRAWABLE. The set went
from 5 not refused and 5 drawable in 439 s to 4 and 3 in 287 s, one run each.

Over all fourteen diagrams composed for the stock brief at 25 s a step, no LP gains the double
pile and three refutations and loses one refutation at the cap (tower villa at +4 ft).

## What has to be decided

1. **Whether one worker should run more than one search.** The option put to Lucas and not taken
   was to split each hard step's time between no LP and the default. It halves what either gets:
   the double pile's 8 to 11 s then sits near the edge of a 16 s step.
2. **Whether the seed should be part of the answer.** A step that is UNKNOWN at one seed and
   OPTIMAL in a second at another is asking for a restart, which a single-worker search does not
   do across strategies.
3. **Why the bungalow placed 2 ft deeper is not drawable.** It was not read. If the deeper house
   is refused a drawing for a reason the derived depth does not have, the step order matters to
   that house and not only the search.

## What must not be done

- A share, a cap or a seed must not be tuned until one run turns green. Every figure here is a
  draw, and the heavy tail is the finding.
- `linearization_level` must not be set at a solve site that was not measured. The line grid's
  own history is the precedent: added at every site, it cost the shipped Tidewater record four
  facts.

Report: `docs/reports/the-one-worker-search-2026-11-27.md`.
