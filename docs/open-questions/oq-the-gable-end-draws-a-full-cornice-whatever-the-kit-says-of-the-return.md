# oq/the-gable-end-draws-a-full-cornice-whatever-the-kit-says-of-the-return — what a gable end shows at the eave

*Status: CLOSED 30 September 2026 (ruled 29 September 2026; executed by WP-16.5; the rake is `oq/the-rake-is-drawn-as-an-edge-and-carries-no-member`) · Raised in: Phase 15, WP-15.7, the cornice drawn with its members (28 September 2026)*

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

## Ruled 29 September 2026 (Lucas, asked directly): draw what the kit says, and a return as long as the cornice is tall

- **What the gable end draws.** *Draw what the kit says*:
  - where the kit forbids a return or makes `none` canonical, no band crosses the gable;
  - a stated return runs out and stops;
  - where the kit is silent, the band stays and the sheet says the return is unstated;
  - Tidewater takes its canonical return.
- **How long a stated return is.** *As far as the cornice is tall*: the pork-chop fault's own rule
  for a correct return, 24.6 in on Tidewater, labelled a judgment. The kit's 12–24 in band is noted
  as written for a smaller cornice. This was asked because the kit's band was written for a cornice
  of about 11.7 in (the stunted-return fault's own note). Against this elevation's 24.56 in cornice,
  every length in the band fails the pork-chop ratio.

**Read, not ruled:** cape-cod-colonial's plain 6–12 in return is licensed by the stunted-return
fault's own exception, so it keeps its own band, drawn at the band's midpoint and labelled a
judgment.

**Left open:** the rake half of this entry is not ruled.

**Order of work:** decision 4's adjudication (WP-16.2) runs before this package. The planning pass
traced the bans on eight of the nine shipped plans that would lose their band to
`gothic-revival-american`'s bargeboard rule, reaching them through an `extends` base, so no band is
removed on a ban that is itself wrong. Executed by WP-16.5.

## Executed 30 September 2026 (WP-16.5): the gable end draws what the kit says

- **One reading of the return.** `resolve_kit.return_at(rec, date)` reads the style's resolved
  `cornice_return` at the house's date and names who said it. Over the 41 styles the elevation
  draws, undated: 12 state a return, 6 forbid one, 3 make `none` canonical, 1 states a plain return
  (cape-cod-colonial), 5 permit one and settle none, and 14 say nothing. At the Tidewater record's
  1765 the three `none` rows, dated 1620–1700, are out of period, so those three read unsettled.
- **What each gable end draws.** `elevation.cornice_return`, and `cornice_marks` for the sheet and
  the DXF:
  - a stated return at each corner, as far as the cornice is tall (24.56 in on Tidewater, R8a's
    judgment), carrying its members. The kit's 12–24 in band is noted as written for an 11.7 in
    cornice;
  - a plain return at the middle of the record's own band, 9 in on cape-cod-colonial, a judgment;
  - where the kit forbids one or makes `none` canonical: the cornice's end profile at each corner,
    the wall running up to the rake, and the eave faces' cornice stopping at the corners;
  - where the kit permits one and settles none, or is silent: the band, and the sheet says the
    return is unstated and whose kit left it so. Where the kit permits one only over a deeper
    cornice than the drawn one, as colonial-revival's does, the sheet says that too, and the
    drawing is unchanged: `oq/a-return-permitted-only-over-a-deeper-cornice-is-drawn-over-a-shallower-one`.
- **Which faces are gable ends** is read off the roof record's form and ridge
  (`elevation.gable_faces`). The renderer's `is_gable_end = face in ("E", "W")`, which this entry
  quoted, had been read by nothing since WP-14.6 and is removed.
- **What moved on the shipped plans.**
  - Tidewater and good-03 draw their returns, and `return-that-never-returns` clears.
  - good-05 forbids its return (A4) and draws end profiles, and the same fault now convicts it.
    That conviction rests on a roof drawn side-gabled by a fallback its style's kit does not make
    canonical: `oq/the-roof-is-drawn-side-gabled-whatever-the-style-says`.
  - The other eight drawn plans keep the band and say why.
  - The pork-chop and stunted-return faults are gated on a drawn return: not applicable where none
    is drawn.
- **The stack.** The Tidewater gable stacks stand clear of the returns, and census V25 holds the
  paint order wherever a stack meets a return or a band.

**The rake half is not ruled, so it leaves this entry**:
`oq/the-rake-is-drawn-as-an-edge-and-carries-no-member`. The gable end draws the rake as the roof's
edge. `rake_overhang_in`, which since WP-3.2 published the eave cornice's projection and convicted
all eleven drawn plans of The Cardboard Gable, is withheld.

**Both ruled halves are executed, so this question is closed.** Report:
`docs/reports/wp-16.5-one-cornice-and-the-gable-end.md`.
