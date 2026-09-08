# The merge of the two Phase 11s — reconciled by measurement rather than by side

*8 September 2026 · merging `main` (the precedent bench, WP-11.1–11.7) into
`claude/georgian-tidewater-plan-analysis-qbwmqs` (the sheet, WP-11.1–11.15)*

Two Phase 11s ran in parallel from one base commit. Seven work-package numbers name two
packages each, exactly as the two Phase 9s do; nothing is renumbered, and the disambiguator is
the one `CLAUDE.md` already gives — **cite the report by filename**.

This is not a work package. It is the record of what the reconciliation had to decide, what it
measured, what it nearly dropped, and the three defects neither parent had.

## I. The rule the resolution followed

Where both branches built the same thing, **main's spelling survives and this branch's
behaviour is ported into it**. Where only one built something, it is kept. A resolution that
took one side wholesale would have been legible and would have silently deleted work; the two
places that nearly happened are in §IV.

| layer | kept | ported in |
|---|---|---|
| `structure`, `openings`, `plan_check`, `export_ifc` | main's `envelopes()` / `origin=` / `slab_boxes()` / `_envelope()` | this branch's appendage pass and per-element callers |
| `geometry.flank_sizes` | main's name (was `dependency_sizes`) | WP-11.13's derived grid allowance |
| candidate acceptance | main's strict-stacking incumbent | WP-11.8's band-first key |
| `geometry_cp._boxes` | main's corner view | derived from this branch's `_element_boxes`, never computed twice |

Element building stays at level 0. The first resolution built elements on the upper level too,
contradicting this branch's own stated rule in three places.

## II. Every moved pin was re-derived on both parents

**The three-way reading is the finding in almost every case**, and a merged figure equal to
either parent's would have meant one side had been dropped.

| quantity | this branch | main | merged |
|---|---|---|---|
| corpus placement digest | `151126d0269bbc61` | `f9581168be01a1b5` | **`68b102ff6a724e47`** |
| drawn furniture shortfalls (short / long) | 65 / 65 | 86 / 74 | **68 / 82** |
| Tidewater relaxations | 8 | 5 | **7** |
| spec Colonial serious / minor / info | 56 / 74 / 17 | 57 / 80 / 25 | **56 / 80 / 25** |

The placement digest is a third value because the FOOTPRINTS are main's — WP-11.2 reads the
massing's own bay count and its parity, taking the Tidewater from 60.0 × 40.08 to 63 × 38.17
and the spec Colonial from 40.0 × 38.44 to 50.0 × 30.75 — while the room rectangles inside them
are this branch's WP-11.7/11.8 band ranking. The serious/minor/info row is the same shape one
layer up: serious is this branch's figure, minor and info are main's.

### The CP model did not move, and that had to be proved before a number was touched

All four `CpModel` proto hashes changed, and the assertion beside them says in as many words
that any movement there is a defect. Handed **this branch's own `derive_footprint` output**, the
**merged** `geometry_cp._build` reproduces all four previous hashes exactly. The whole movement
is the footprint and none of it is the model.

**And the first control was not a control.** Overriding `W` and `H` in main's footprint dict
reproduced three of the four and not the fourth, because `bay` stayed at main's 9 ft and the
span term lays its grid lines on the bay module. A derived dict's keys are derived together:
substitute the whole dict or none of it.

## III. The one real cost, and it is worse than either parent

Drawn furniture shortfalls go 65/65 → **68/82**, and on the long axis that is worse than main's
74 as well as this branch's 65. **Fourteen of the sixteen plans are byte-identical to this
branch's figures**; the whole movement is the two shipped plans, the only two WP-11.2 resizes.

The mechanism is an interaction rather than an inheritance. `derive_footprint` is area-neutral
in the bay count, so a house that gains a bay loses **depth** at constant area; WP-11.8 then
ranks each room's own proportion band first, drawing rooms **squarer** inside a shallower pile —
which is a **shorter** room, and the long axis is what a dining table and a kitchen island need.

Neither package is undone. Undoing a ruled package while reconciling two branches is a third
change hidden inside a second one, and the numbers that would justify it are exactly the numbers
the merge disturbed. Both ceilings are re-baselined upward, in public, with both parents' figures
beside them: `oq/the-bay-parity-and-the-band-ranking-compose-worse-than-either`.

## IV. Two features were lost in the first resolution and restored

- **Main's WP-11.1 record table** — `WHAT THE RECORD ASKED FOR`, every ∗ room's drawn figure
  against its declared one — vanished when `render_plan.py` took this branch's sheet. **Main's
  own test is what said so.** It is ported into Graphic Standard No. 1, drawn in both registers
  (a presentation sheet that keeps the ∗ and drops its explanation is the state WP-6.1 found the
  relaxation triangle in), with its height computed rather than allowed for.
- **The hearth tooltip's `Morris 1734, judgment`** became a bare `judgment`. A judgment with no
  basis named is what this corpus forbids one line further than a figure with no source.

## V. Three defects neither parent had

- **A bearing wall drawn thinner than a partition.** The guard read `min(width, height)` off the
  drawn rectangle, and `wall_bands` states in its own body why that is a proxy: *a pier between
  two windows is a run SHORTER than the wall is thick*. The merged placement produced a 0.365 ft
  masonry stub and the guard duly convicted the drawing. The band has carried `t_ft` all along
  and the plate had nowhere to put it; it publishes `data-t` now and the guard reads that.
- **A stated box is its own rooms' area, rounded.** `capacity_report` convicted the MAIN BLOCK
  of not holding its own rooms — 1,675.8 sf stated for 1,676.0 sf of rooms, 0.012%, no mass
  moved. `derive_footprint` ends `H = round(need / W, 2)`, so the verdict was decided by which
  way the second decimal went; it read `true` for three packages on one plan's luck. The
  tolerance is derived from that rounding and is reported on the row.
- **`roof_form` had no generator reading it, and that was the instrument.** WP-11.4 moved
  `roof_form_for` out of `roof.py` into `build/threshold.py`, which was not in
  `check_research.GENERATOR_FILES` — so `measured_unsourced_read` was about to fall by four
  slots **for free**, which is the exact failure that ratchet's own docstring exists to prevent,
  arriving through the file list instead of through the data. 267 → 299 and 68 → 78,
  re-baselined upward in the same commit as the widening.

## VI. Four guards pinned a literal — five packages running

The candidate-acceptance key, the CP dispatcher's own comment sentence, the hearth schema
version and the stack-centring precision each asserted characters or digits rather than the
property, and each broke on a rewording or a rounding rather than on a regression. All four are
re-cut against what they are about: the acceptance key is read as a pair whose first term is the
band count; the dispatcher is asserted by RUNNING a multi-element plan through it; the schema
version is asserted at-or-above where the field landed **with the field present**; the centring
tolerance is derived from the record's own three-decimal rounding.

Two more were re-cut against the placement rather than a room id: `test_facade`'s control (which
named `chamber2` and `primary`) now asserts that both states really occur, and
`test_stacking`'s `len(kept) == 3` is the accounting identity plus a floor.

## VII. And a mutation harness interrupted mid-run left `if False:` in the renderer

The sheet digest was re-derived on that tree and looked exactly like a legitimate
re-derivation — the height reserved for a table that was not drawn. `CLAUDE.md` already records
that a mutation which does not REVERT makes every later result meaningless and reads as success;
what this adds is that **the damage outlives the harness**, into any figure measured afterwards.
After an interrupted mutation run, restore the file and re-derive everything taken since. The
finding is recorded beside the pin it corrupted.

## VIII. What was deliberately not done

- **`STACK_HARD` is not flipped.** The argument for its default was a structural measurement on
  `spec-builder-colonial` that now runs the other way — the rule REMOVES two over-capacity spans
  where main measured it introducing two — because the baseline moved, not because the rule
  improved. `oq/the-measurement-that-defaulted-the-stacking-rule-has-inverted`.
- **The two shipped plans are not re-tagged.** That is WP-11.16 and it is its own package.
- **No literal is bumped where a property could be read instead**, and where a figure is
  re-baselined the parents' own numbers are written beside it.

## New open questions

- `oq/the-bay-parity-and-the-band-ranking-compose-worse-than-either`
- `oq/the-measurement-that-defaulted-the-stacking-rule-has-inverted`
