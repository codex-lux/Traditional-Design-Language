# oq/the-gable-end-draws-a-full-cornice-whatever-the-kit-says-of-the-return — what a gable end shows at the eave

*Status: OPEN · Raised in: Phase 15, WP-15.7, the cornice drawn with its members (28 September 2026)*

**The elevation draws the eave cornice across every face it draws, gable ends included.** On a
side-gable house that means a horizontal cornice the whole width of the gable, standing on the eave
line under the rake, on all 41 styles the elevation draws. WP-15.7 gave that band its members and
left its extent as it was, because the extent is not the elevation's to decide. Each style's
resolved kit says what the cornice does at the gable, in the `cornice_return` slot, and nothing
reads that slot. *(Corrected 28 Sep 2026, WP-15.8's audit: 27 of the 41 say something there, and
14 say nothing at all. See the corrected table.)*

**Measured on the 41 styles the elevation draws** (the census's style sweep):

| what the resolved kit says of `cornice_return` | styles |
|---|---:|
| forbidden: the cornice does not return | 11 |
| `none` canonical | 3 |
| `full-return-carrying-complete-profile` canonical, with `return_depth_in` 12 to 24 in | 12 |
| ~~specified, with no canonical variant~~ | ~~15~~ |
| specified, with no variant and a `return_depth` of 6 to 12 in, measured (`cape-cod-colonial`) | 1 |
| bound `open` and resolving `empty`: no kit in the chain states anything about the return | 14 |

*The last two rows replace one row that read "specified, with no canonical variant: 15" (corrected
28 Sep 2026, WP-15.8's audit, re-derived with `threshold.resolved_slots`). The 14 are adam-style,
beaux-arts-american, beaux-arts-french, dutch-colonial-american, english-baroque,
english-classical, english-georgian, english-georgian-country-house, english-georgian-townhouse,
english-palladian, french-neoclassical, italian-renaissance, palladian and regency. For them the
gable band is drawn where the record is SILENT, which is a different question from the 11 and the
3, where it is drawn against what the record says.*

- **The 11 are decision 4's class.** The elevation draws something the resolved kit forbids.
  Two forbid it in their own kit (`cape-cod-revival`, `colonial-revival`). Nine inherit the ban:
  - from `colonial-revival`: `georgian-revival`, `minimal-traditional`, `neoclassical-revival`,
    `new-classical`;
  - from `gothic-revival-american`: `italian-renaissance-revival`, `italianate-townhouse`,
    `renaissance-revival-american`, `second-empire`;
  - from `american-farmhouse-vernacular`: `new-urbanist-traditional`.

  Census V2 does not count it, because its closed feature table has no row for the return and it
  reads only the front. It is a further instance for
  `oq/an-inherited-ban-decides-what-the-elevation-may-draw`, with the same own-against-inherited
  split, and waits on the same ruling.
- **The 3 are the same, stated the other way.** `garrison-colonial`, `new-england-colonial` and
  `saltbox-colonial` make `none` canonical.
- **The 12 state a return that stops.** Their rule, from `georgian-colonial-american`: *"The
  cornice returns across the full depth of the gable end carrying its complete profile, including
  the modillion or dentil band, for 12 to 24 in before dying into the wall."* Its own note then
  says the other thing: *"the Southern brick houses often return the cornice all the way round
  instead, which is a different and also correct answer."* The Tidewater record is a Southern
  brick house, so the full band on its gable is the note's reading and not the rule's. The record
  states both, and a drawing can draw only one.

**Two more things the gable end does not draw, for the same reason: no record the elevation reads
states them.**

- **The rake.** The raking cornice is not modelled (`raking_cornice_member_count` is in
  `elevation.NOT_MODELLED`: *"eave_cornice() dimensions the horizontal entablature only"*). So
  the gable's roof edge is the roof polygon's edge, whatever the kit's `pediment.raking_cornice`
  says (*"the full cornice profile raked, with the corona level and the bed mould raked"*,
  editorial).
- **Which faces are gable ends.** `render_elevation` takes E and W to be the gable ends
  (`is_gable_end = face in ("E", "W")`), which is true of a side-gable house on this corpus's
  placements and is an assumption on any other.

**The stack is moot on every shipped plan.** The Tidewater record's gable stacks stand 6 to 7 ft
from the corners, beyond the kit's 12 to 24 in return. Where the band runs across the gable, the
stack stands in front of it and is painted over it. Census V25 holds that paint order on every
face.

**What is wanted.**

- Whether decision 4 covers the return, for the 14 styles whose kit says there is none (the 11
  that forbid it and the 3 that make `none` canonical).
- What the gable end draws for the 14 styles whose kit says nothing about the return at all
  *(added 28 Sep 2026 with the corrected table)*.
- Which reading of the 12 to 24 in return governs a house its own kit's note says may return the
  cornice all the way round.
- Whether the gable end draws the rake at all, before any pack dimensions a raking cornice.

**Until it is ruled, nothing moves.** The gable band is drawn as it has been, with its members,
and this question is the record of what it does not read.
