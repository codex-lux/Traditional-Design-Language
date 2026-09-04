# oq/the-partis-bay-module-contradicts-its-own-exemplars — a 9 ft bay on a diagram whose every exemplar measures about twelve

*Status: OPEN · Raised in: WP-11.2, measured when the parti's module first reached the placer (4 Sep 2026)*

**`partis/centre-passage-double-pile.json` states `scaling.bay_module_ft: 9`. Its three named
exemplars measure about 12 ft a bay. Nothing had ever read the number, so nothing had ever
noticed.**

WP-11.2 let a plan record name the parti it is an instance of, which is what finally carried the
diagram's own bay module into `derive_footprint`. On the shipped Tidewater plan the 9 ft module
produces a **seven-bay** house where the plan's own title says five, the massing says
`bays: "5"`, and the style's `bay_rhythm` says *"Five or seven bays, unaccented, the centre marked
only by the doorway."*

## The measured disagreement

| source | figure | derived bay |
|---|---|---|
| `partis/centre-passage-double-pile.json` | `bay_module_ft: 9` | 9.0 ft |
| Gunston Hall, HABS VA-141 (measured) | 60'-10" over five bays | **12.17 ft** |
| George Wythe House, 1801 insurance policy | 54 ft over five bays | **10.8 ft** |
| `styles/tidewater-georgian.json` `typical_ratios` | *"Facade 48–72 ft, five or seven bays"* | 9.6–14.4 at five bays; 6.9–10.3 at seven |
| the shipped plan as placed before WP-11.2 | 60 ft over six bays | 10.0 ft (the placer's default, not a statement) |

The style's own band contains both readings, which is the point: **at five bays it says 9.6 to
14.4 and at seven it says 6.9 to 10.3, so the module is not independent of the count.** A single
`bay_module_ft` on a diagram used by fifteen styles cannot be right for all of them, and 9 ft is
the folk end of a range whose polite end is twelve — which is `oq/register-is-not-style`'s subject
arriving in the placer.

## Why this is a question and not a patch

**Changing 9 to 12 would be authoring a number.** The parti serves fifteen styles from
`federal-style` to `dutch-colonial-revival`; a figure right for Gunston Hall is not thereby right
for a New England Georgian, whose passages the corpus itself calls *"8 to 10 ft, tighter"*. The
honest shapes are a band, a per-style override, or a derivation — and each is a different ruling:

1. **A band on the parti** (`bay_module_ft: [9, 13]`), with the placer choosing inside it. Cheapest,
   and it makes the module a preference rather than a fact.
2. **A style-level override**, which is where the corpus already states the figure in prose. It
   needs `styles/*.json`'s `typical_ratios` to become executable, and that is the class
   `oq/a-room-records-prose-states-a-floor-its-own-band-does-not` names.
3. **A derivation** — the facade is a RESULT (`oq/the-facade-is-a-result-not-an-input`, ruled 4 Sep
   2026), so the bay count and module fall out of the plan's own breadth and the diagram's parity
   rather than being asserted. This is the answer the tradition gives and the most work.

**Do not rule it by picking the exemplars' 12.** The exemplars house six enclosed ground rooms and
this parti names eleven (`oq/the-parti-dissolved-its-own-dependencies`), so its program is larger
and its facade would be wider at the same bay module. Fixing the module against exemplars whose
program the diagram does not share would move one number to match a building this diagram cannot
produce.

## The cost of leaving it, measured

Naming the parti takes the shipped Tidewater plan from six bays of 10 ft (60.0 x 40.1) to seven of
9 ft (63.0 x 38.2). Over **eight seeds** on the hill-climb:

| footprint | fatal findings | score (mean) |
|---|---|---|
| 6 x 10 ft = 60.0 x 40.1 (before) | 2, 3, 5, 6, 8, 8, 8, 10 — **mean 6.2** | 692 |
| 7 x 9 ft = 63.0 x 38.2 (the parti's module) | 8, 8, 9, 9, 9, 10, 10, 11 — **mean 9.2** | 662 |
| 7 x 10 ft = 70.0 x 34.4 (odd count, old module) | 5, 9, 9, 10, 10, 10, 11, 12 — **mean 9.5** | 693 |

**The odd bay count costs about three fatal findings whichever module it takes, and the 9 ft module
buys thirty points of score at the same count.** Every one of those fatals is an unreachable room
— a door the search could not realise — so the cost is the SEARCH's, not the record's: on CP-SAT at
a budget that reaches its second phase the same plan reports **zero** fatal findings before and
after, with serious 73 → 67, transfers 30 → 17 and undrawn windows 27 → 20. The regression is one
engine's, on a plan whose container is known wrong
(`oq/the-parti-dissolved-its-own-dependencies`, ruled and unbuilt), and it is recorded here rather
than avoided by leaving the diagram unable to reach its own placement.

**And the seed spread is the reason this table has eight rows and not one.** At three seeds the
before-and-after read 3 → 8 and looked decisive; the fuller sample shows two overlapping
distributions whose means differ by three. A single-seed comparison of a hill-climb number is a
comparison of two draws, which is why `build/diagnose_sheet.py --seeds` exists at all.
