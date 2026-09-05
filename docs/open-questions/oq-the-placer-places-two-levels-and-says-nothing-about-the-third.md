# oq/the-placer-places-two-levels-and-says-nothing-about-the-third — a declared storey came back with no geometry, no finding and no note

*Status: OPEN · Raised in: WP-11.6, the record says what it means (5 September 2026)*

**OPEN — both placement engines are written against level 0 and level 1. A record declaring a
third level is accepted, two of its levels are placed, and until this package nothing anywhere
said that a storey had been left out of the drawing.**

## The measurement

`plans/reference/bad-03-narrow-lot-townhome.json` is the only three-level record in the corpus.
It declares one level-2 room, the Gameroom, a `great-room`. Solved on either engine:

```
level 0  rooms 4  placed 4
level 1  rooms 9  placed 9
level 2  rooms 1  placed 0
```

The eight findings naming the Gameroom were **all declared-layer findings** — its adjacencies,
its ceiling height, its daylight, its furniture fit. Not one of them was about the drawing,
because there was no drawing of it to judge, and no layer said so. `geometry_report` carried no
note; `plan_check`'s drawn summary counted `rooms_placed` and had no counterpart for the rooms
it did not place; the sheet drew the house without its top floor.

## Where the ceiling actually is

Two places in `build/geometry.py`, and both are structural rather than incidental:

- `_finish` (the CP record writer) does
  `src = best["ground"] if idx == 0 else (best["upper"] if idx == 1 else {})` — a literal empty
  dict for every level above the first.
- `solve_heuristic` is written throughout against `prep[0]` / `prep[1]` and `levels[0]` /
  `levels[1]`; `slice_rect` is called twice, and `vertical_score(g, u, …)` takes exactly two
  rectangle dicts.

`geometry_cp.py` is the same shape one layer down: its stacking penalty keys `(1, r["id"])` and
`(0, so)`, so "below" is level 0 by construction there too.

## What WP-11.6 did, and deliberately did not do

**Did:** disclosed it, on `multi_element_disclosure`'s exact precedent (OQ 40 — the layer cannot
do the thing, so it says so on the record rather than reporting numbers from an instrument
pointed at half the building). `build/stacking.py` states `PLACED_LEVEL_INDICES = (0, 1)`;
`geometry_report.multi_level` names the levels not placed, the rooms on them, and why every
drawn judgment about them is unjudged; `plan_check.drawn`'s `rooms_unplaced` carries a `serious`
finding per room; and `build/check_stacking.py` reports any record declaring a level outside the
ceiling. A stacking claim onto or off such a level is `unjudged` with its own named reason
rather than counted as landing.

**Did not:** place a third level. That is not a small change — it is `vertical_score`'s
signature, the candidate generator's level-awareness (`slice_rect(…, below=…)` currently takes
one level below, which generalises, but `solve_heuristic`'s loop does not), the CP model's room
keys, and the two-dict shape that `bias`, `wall_lines` and the relaxation counter all assume.

## What must be ruled before it is built

1. **Is a three-level house in scope at all?** Every parti in the corpus declares two levels;
   `bad-03` is a reference plan authored to demonstrate faults, and its third storey may be
   incidental to what it was written to show. If the answer is no, the honest fix is for the
   plan schema to REFUSE a third level rather than for the placer to accept and drop it.
2. **Does "below" mean the next level down, or the next PLACED level down?** A record with
   levels 0, 1 and 3 (a mezzanine numbered loosely) makes those different answers, and
   `stacking.judge` currently takes the first, reporting a two-level gap as unjudged.
3. **What does a cellar do?** `index: -1` is documented in the plan schema (*"0 ground, 1 first
   above, -1 cellar"*) and no record uses it. A cellar is below level 0, so `PLACED_LEVEL_INDICES`
   is not simply "the first N": it is a window, and nobody has said where it starts.
4. **Is the disclosure enough?** A `serious` finding per unplaced room and a `multi_level` block
   may be the right permanent answer for a record the placer cannot honour, in which case this
   question closes at the disclosure and the schema question (1) is the live one.

## The rule this is an instance of

*Unjudged is not passed*, applied to a whole storey. Nothing here was wrong in the sense of
computing a bad number — every layer computed correctly over the rooms it was given. What was
wrong is that no layer said which rooms those were.
