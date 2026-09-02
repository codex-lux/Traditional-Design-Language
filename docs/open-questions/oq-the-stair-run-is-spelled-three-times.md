# oq/the-stair-run-is-spelled-three-times — 16, 17 and 21 risers for one house, and the section draws the third

*Status: CLOSED 2 Sep 2026 · Raised in: WP-9.6 (2 Sep 2026), from a WP-9.2 finding upgraded twice and then corrected*

**THE FIGURES THIS ENTRY FIRST PUBLISHED WERE WRONG, AND THE CORRECTION IS THE FIRST THING TO
READ.** It reported 16 / 17 / 21 risers and "3.3 ft" of disagreement, and cited a hardcoded 9.0 ft
ceiling as the cause. **The 17 was never measured on this plan**: it came from feeding `stair_pass`
a 9 ft ceiling by hand — the prose's own worked example — and was then written up as what the plan
produces. `plans/tidewater-georgian-careful.json` declares `floor_to_ceiling_ft: 11`, so the `or
9.0` fallback never fired on it at all. Measured by execution:

| spelling | input | result |
|---|---|---|
| `rooms/stair-hall.json` `critical_dimension` | its own worked example: a 9 ft ceiling, 12 in assembly | 16 risers at 7.5 in — **an example, not a claim about this plan** |
| `build/openings.py::stair_pass` | `(11 + 1.0) × 12` = **144.0 in** | **20 risers at 7.2 in** |
| `build/structure.py::stair_geometry` | `storey_height_ft` 12.279 × 12 = **147.3 in** | **21 risers at 7.017 in** |

**The gap was 3.3 INCHES, not 3.3 ft** — out by a factor of twelve — and it is a disagreement
about the FLOOR ASSEMBLY, not about the ceiling. `structure.py` derives the assembly by inverting
`storey-graduation.json`'s own `ceiling_height_rule`: 15.35 in at an 11 ft ceiling, 11.86 in at
8.5 ft. `openings.py` used a flat **12.00 in**. Both readings of the same house, one step apart.

That the wrong numbers survived a commit message, a report, `CLAUDE.md` and this entry is the
session's own lesson landing on its author: **a figure obtained by feeding a function a
hypothetical input is not a measurement of anything**, and the fix was to run it.

## Two defects, and the smaller one was the headline

**(a) The floor assembly.** `structure.py` inverts the pack rule; `openings.py` used a flat 12 in.
This is what produced 20 against 21, and it is the OQ 52 class — a generator supplying a constant
where the corpus has a derivation.

**(b) The `or 9.0` ceiling fallback.** Real, and latent rather than live: **all 16 shipped plans
state a ground ceiling**, so it fired on none of them. It was still a second invented number on
the same line.

## Lucas's ruling, 2 Sep 2026, in two parts — and the second moved the number

**First: the PACK is authoritative.** `storey-graduation.json`'s `stair_type` rule governs, and
both Python spellings already followed it, so that half redrew no stair by itself; what moved was
the prose.

**Then, the same day, on the open question this entry ends with:** *"7.5 in is right — move the
pack."* So the pack's expression is `ceil(module / 7.5)` now, its baked copy in
`kits/georgian-colonial-american.kit.json` moved with it, and **`build/storeys.py::riser_divisor_in`
READS the expression** rather than transcribing it — the two Python literals that used to carry
7.25, each commented with the name of the pack it was copied from, are gone. A reader that does
not recognise the expression's shape **refuses**; it does not fall back to a number.

**What that costs, measured rather than assumed.** Only two of the sixteen shipped plans place a
stair hall at all, and neither leaves the legal band:

| plan | at 7.25 in | at 7.5 in | IRC advisory max |
|---|---|---|---|
| `tidewater-georgian-careful` (147.34 in storey) | 21 risers at 7.017 in | **20 at 7.367 in** | 7.75 |
| `spec-builder-colonial` (120.56 in storey) | 17 at 7.092 in | **17 at 7.092 in** — unmoved | 7.75 |

And the pack's own worked example now reproduces the prose it was always meant to: a 120 in
default storey gives **sixteen risers at exactly 7.500 in**, which is the figure
`rooms/stair-hall.json`'s `critical_dimension` has worked its example at all along. That
agreement is the whole argument for the ruling.

**THE DISAGREEMENT THE RULING LEAVES, STATED RATHER THAN RECONCILED.** The same room record's
`conflict` note says *"The historic comfortable band is a 7 to 7.25 in rise on an 11 to 11.5 in
tread"*. The corpus's default stair now sits at 7.5 — legal everywhere, and just outside a band
the corpus states about itself. **That is two statements about comfort in one record, and picking
one to silence the other is the move this corpus names first.** It is recorded in the pack's own
note, in the room record's `conflict` note, and here. It is an instance of
`oq/a-grouping-rule-and-a-room-record-can-disagree`'s class one layer over — a rule and a record
under different names — and the checker Lucas ruled for that question is where it should surface,
not in a number edited to make the two agree.

## BUILT, 2 Sep 2026 (WP-9.6), in the order Lucas asked for: the input first, then the reader

**`build/storeys.py` is the one derivation of storey height from the ceiling a plan states**, and
it is a LEAF on purpose: `structure.py` loads `geometry.py`, which calls `openings.stair_pass`, so
openings importing structure would close a cycle. `structure.py` re-exports `storey_heights` and
`STOREY_CEILING_FRACTION` under their old names, so its three existing test callers are untouched
and there is exactly one implementation.

`openings.stair_pass` now reads `storeys.ground_storey_in(plan)`. **Both invented constants are
gone in one move**, and the two spellings agree by construction: measured at the ruled 7.5 in
divisor, `tidewater-georgian-careful` **20 and 20**, `spec-builder-colonial` **17 and 17**. (At
7.25 the same guard read 21 and 21 — the agreement is what the change bought; the count is the
pack's, and it moved when the pack did.) Where a plan states no ceiling anywhere on the ground
level the pass **refuses the stair with a stated reason** rather than assuming 9.0 — a stated
absence, not a stair of assumed height. No shipped plan takes that branch today, which is recorded
so the refusal is not mistaken for dead code.

`tests/test_storeys.py` holds seven guards, including one that pins the transcribed
`STOREY_CEILING_FRACTION` against the pack's own `ceiling_height_rule` expression (it is a
transcription, not a read, and that is defensible only while something holds them together), one
that asserts the two spellings agree on every shipped plan, one that **scans every file in
`build/` for a stray riser divisor** and one that proves an unrecognised `stair_type` expression
is refused rather than defaulted. Mutation-checked, all four directions: restoring the old
`(ch + 1.0) * 12` with its `or 9.0` turns the agreement test red; putting a bare `/ 7.25)` back
in `structure.py` turns the stray scan red; making `riser_divisor_in` return a literal turns both
divisor tests red; making the reader fall back instead of raising turns the refusal test red.

**~~The prose is NOT yet rewritten.~~ SETTLED THE OTHER WAY, and that is the point of the second
ruling.** `rooms/stair-hall.json`'s `critical_dimension` works its example at 7.5 in, and rather
than rework the prose to match a pack, Lucas moved the pack to match the prose. The example stands
as written. What is NOT settled by that is the same record's `conflict` note, which states a
historic comfortable band the new default sits just outside — see the ruling above.

## What must not happen

Do not reconcile by editing whichever file is easiest and leaving the third. There are three, the
third was invisible to two audit passes, and a fix that lands in two of them reproduces this entry
exactly. ~~And do not change the prose to 7.25 without also reading whether 7.5 is the figure the
period sources actually support — the ruling settles which record GOVERNS, not which number is
architecturally right, and if 7.5 is right then the pack is what should move. **That is the one
piece left open here.**~~ **CLOSED the same day: Lucas ruled 7.5 right and the pack moved.** The
sentence is kept struck rather than deleted because it named the correct next question and got
the correct answer, which is the only reason this entry's number is the pack's and not a
transcription's. What it did NOT settle, and nothing here does, is whether 7.5 in has a period
source: it is the figure the corpus already worked its own example at, which is consistency, not
evidence. If a source is ever read for a comfortable riser, this is the number it has to test.
