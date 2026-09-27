# oq/the-search-is-refused-on-type-facts-nothing-tells-it — the gate reads four facts and the search scores one of them

*Status: OPEN · Raised in: WP-14.21, the worked house, attempted (25 September 2026)*

**The finding.** WP-13.3 told the PROVER the type: tiling, declared stacks, bearing continuity on the
bay grid, and the hearth on its flue wall, each a hard, downgradable literal. WP-13.4 then refused to
draw any placement that breaks one, on either engine. The SEARCH was told of none of them as a fact.

| fact | what `typefacts` asks | what the search scores |
|---|---|---|
| tiling | every element tiles exactly | tiles exactly by construction (guillotine slicing), and holds on every variant WP-14.21 tried |
| stacks | each declared `stacks_over` lands, at 90% of the smaller room | a soft charge, `STACK_W = 40.0`. The strict incumbent exists and ships off (`STACK_HARD = False`) |
| bearing | every upper **on-grid** interior line stands within 0.75 ft of a ground **on-grid** line, and the upper floor has one | `vertical_score` charges 2.0 for each upper wall line not within 0.75 ft of **any** ground wall line, on or off the grid |
| hearth | each stated fire's room stands on its flue wall's face | nothing: `build/geometry.py` does not contain the word |

**Measured by WP-14.21, and run as diagnostics, never as criteria.**

On the careful record's copy and on four variants of it, the search's own placement was refused on
every one. Across twenty seeds, it found no refusal-free placement in any of these pools:

- the default pool of 250;
- a pool of 2,000 with the strict-stacking incumbent switched on in-process.

The four pools were V0 and V1 at 250, and V1 and V3 at 2,000.

With strict stacking on, the stacks hold and the hearth and the bearing lines break instead. On V1,
12 of 20 seeds were refused for {bearing, hearth} alone. The one variant whose deterministic run was
refused on stacks alone (V1) held its hearth because its passage runs east–west across the house.
That is not the parti.

Figures: `docs/reports/wp-14.21-the-worked-house-and-the-dining-fire.md` §V, D1.

## Why it matters

WP-14.21's first criterion for a worked house that places was *the heuristic's `refused` is
`None`*. On a record stating fires and stacks, the search can meet that only by the luck of a draw,
because three of the four facts it is refused on are ones it is not steered towards.

The search is also what the bench's wall drag asks for by name, and it is drawn as a working sketch
(WP-13.4). So a reader who drags a wall on a Tidewater record meets refusals that are partly the
search's and partly the house's, and nothing on the sketch says which is which.

## What must be ruled

1. **Is the search held to the type facts at all?** The alternative is that its refusal is a
   disclosure on a sketch, and the proof (`auto`) is the bar a house is judged by. If so, a
   criterion like WP-14.21's first is the wrong criterion, and it should be said where the next one
   is written.
2. **If it is held to them, as what?** The options are soft terms at weights that must be swept
   (WP-7.4's *"worse in the middle of its range than at either end"*), or hard incumbents like
   `STACK_HARD`. The measurement that defaulted `STACK_HARD` off is already an open question, and
   it has inverted: `oq/the-measurement-that-defaulted-the-stacking-rule-has-inverted`.
3. **The hearth first, or not at all?** It is the only fact the search has no term for, and the one
   a room's own record states.

## What must not happen

- `typefacts` must not be taught to judge the search more leniently than the prover. It verifies the
  same four facts on either engine's placement (WP-13.3), and that is what makes a refusal mean the
  same thing on both.
- The search's refusal must not be reported as the house's. Where the prover holds a fact that the
  search breaks, the refusal is the instrument's, and every report citing a search figure must say
  which engine it is.
