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

## Lucas's ruling, 2 Sep 2026: the PACK is authoritative — 7.25 in

`storey-graduation.json`'s `ceil(storey / 7.25)` governs. Both Python spellings already followed
it, so the ruling redraws no stair by itself; what moves is the prose.

## BUILT, 2 Sep 2026 (WP-9.6), in the order Lucas asked for: the input first, then the reader

**`build/storeys.py` is the one derivation of storey height from the ceiling a plan states**, and
it is a LEAF on purpose: `structure.py` loads `geometry.py`, which calls `openings.stair_pass`, so
openings importing structure would close a cycle. `structure.py` re-exports `storey_heights` and
`STOREY_CEILING_FRACTION` under their old names, so its three existing test callers are untouched
and there is exactly one implementation.

`openings.stair_pass` now reads `storeys.ground_storey_in(plan)`. **Both invented constants are
gone in one move**, and the two spellings agree by construction: measured, `tidewater-georgian-careful`
21 and 21, `spec-builder-colonial` 17 and 17. Where a plan states no ceiling anywhere on the ground
level the pass **refuses the stair with a stated reason** rather than assuming 9.0 — a stated
absence, not a stair of assumed height. No shipped plan takes that branch today, which is recorded
so the refusal is not mistaken for dead code.

`tests/test_storeys.py` holds five guards, including one that pins the transcribed
`STOREY_CEILING_FRACTION` against the pack's own `ceiling_height_rule` expression (it is a
transcription, not a read, and that is defensible only while something holds them together) and
one that asserts the two spellings agree on every shipped plan. Mutation-checked: restoring the
old `(ch + 1.0) * 12` with its `or 9.0` turns the agreement test red.

**The prose is NOT yet rewritten.** `rooms/stair-hall.json`'s `critical_dimension` still works its
example at 7.5 in with a 12 in assembly. Under the ruling the pack governs, so that example should
be reworked — but it is prose stating a worked example rather than a rule the code reads, and
rewriting it is an authoring change with a source question attached (see below).

## What must not happen## What must not happen

Do not reconcile by editing whichever file is easiest and leaving the third. There are three, the
third was invisible to two audit passes, and a fix that lands in two of them reproduces this entry
exactly. And do not change the prose to 7.25 without also reading whether 7.5 is the figure the
period sources actually support — the ruling settles which record GOVERNS, not which number is
architecturally right, and if 7.5 is right then the pack is what should move. **That is the one
piece left open here**, and it is an authoring question about a source, not a code question.
