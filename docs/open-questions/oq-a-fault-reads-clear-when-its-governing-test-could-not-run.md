# oq/a-fault-reads-clear-when-its-governing-test-could-not-run — clear on whatever ran

*Status: CLOSED 29 September 2026 (ruled that day; executed by WP-16.1) · Raised in: WP-15.8, the audit of Phase 15 (28 September 2026)*

**OPEN — `core.check_measurements` calls a fault clear when at least one of its tests ran and
none of those failed, whatever did not run.** `_judge` in `mcp_server/core.py` evaluates the
fault's tests: the primary, or the `bounds_test` of an exception the style has earned, and every
secondary. It returns `clear` when the tests that were EVALUATED contain no failure. A test that
wanted a measurement nobody supplied is not among them. So a fault whose governing test could not
run is reported clear on a secondary that could.

The corpus's own rule for a fault is that it is present when ANY of its tests fails. On that rule
an unrun test might have failed. A clear resting on part of the list is an unjudged verdict
reported as a pass, which is the collapse this corpus names first.

**Measured at `2467585`, on the sixteen shipped plans**, each placed on `engine="heuristic"`
(deterministic) and checked by `plan_check.check` as the bench checks it. The instrument is
`tests/fault_clears.py`; re-derive with it rather than quoting these:

- **550** fault verdicts read clear.
- **142** of them (26%) never ran their governing test, every one for want of a measurement.
  None was scoped to another style, none was declined by an `applies_when`, none errored.
  - By severity: **48 are verdicts on fatal faults**, 62 serious, 32 minor.
  - They fall on 19 faults and 15 of the 16 plans. `bad-04-log-cabin` has none.
  - **70 of the 142 also sit on `fault_clear_on_a_generator_constant`.** The one secondary
    that ran is a figure `build/elevation.py` states as its own constant, so about half of these
    clears rest on nothing measured at all.
- **284** (52%) left at least one applicable test unrun, counting secondaries.

What a clear rests on, read off the rows. Each fatal fault below clears on the secondary named,
while its governing test wants the measurement named:

| fault (fatal) | plans | clears on | governing test wants |
|---|---:|---|---|
| `pork-chop-return` | 11 | `count_of_moulding_profiles_carried_around_onto_the_return` | `return_projection_from_wall_in` |
| `architrave-that-is-not-there` | 10 | `casing_face_width_in / opening_width_in` | `casing_projection_in` |
| `veneer-reveal-collapse` | 11 | `reveal_depth_in` | `brick_stretcher_length_in` (10), or its exception's `architrave_face_width_in` (1) |
| `truss-flattened-pitch` | 8 | `count_of_distinct_roof_slope_angles_on_the_building` | `roof_height_eave_to_ridge` |
| `storeys-out-of-vertical-alignment` | 7 | `bay_count_on_the_principal_front at-least 3` | `max_abs_offset_between_upper_and_lower_opening_centrelines_in` |
| `window-squarer-than-the-style-permits` | 1 | the head and sill ratios | `frieze_window_height_in`, `frieze_depth_in` |

`storeys-out-of-vertical-alignment` shows the defect most plainly. Its seven clears are on
one-storey houses, where the alignment question does not arise, and the honest verdict is not
applicable. It reads clear instead, on a floor on the bay count that says nothing about alignment.

**It has been met once as an instance and never as a mechanism.** OQ 84 recorded
`cornice-that-is-a-fascia` coming back *"clear" on its wall-height ratio alone while its primary
and two of its four secondaries were skipped for want of a name rather than a number*. It was
closed by supplying the measurement. The rule that made that clear possible was not touched.

**How it was found.** WP-15.8's audit set out to withhold the symmetry and alignment figures on a
front the record does not describe (`oq/the-elevation-measures-a-front-the-drawn-layer-refuses-to-judge`).
Measured before it was applied, withholding them turned `storeys-out-of-vertical-alignment` from
PRESENT to CLEAR on the plans it reached, not to unjudged. With the offset and the matching count
withheld, the only test left to run was the bay-count floor, and it passed. The fix would have made
a fatal fault a pass on four plans (48 false clears on fatal faults became 52). It was not applied.

**What must be ruled before anything is built:**

1. **What a fault is when its governing test cannot run.** Unjudged, with the secondaries that ran
   carried as evidence, is the reading "unjudged is not passed" gives. The alternative is that a
   secondary may stand in for the primary where it states the same rule another way.
   `storeys-out-of-vertical-alignment`'s "list form" secondary says of itself that it is *"what a
   model should actually compute"*; its bay-count floor is a different rule. **No record says which
   of its secondaries are the same rule and which are other symptoms**, so an evaluator cannot tell
   them apart today. That is a field nobody has authored.
2. **Whether a clear needs the governing test (142 move) or every applicable test (284 move).**
3. **What the composer does with the verdicts that move.** `compose._sort_key` reads fatal counts
   off the findings, and an unjudged fatal is not a finding, so moving a fault from clear to
   unjudged changes no ranking by itself. What it changes is the certificate: `fault_summary` stops
   calling 142 unjudged verdicts clear. Whether an unjudged fatal should cost a candidate anything
   is `oq/the-composer-ranks-first-a-house-that-may-not-be-drawn`'s family, and it is not answered
   here.

**Not done, and why.** The code change is small: `_judge` would return `needed` where the
governing test did. Its blast radius is not small. It moves the fault summary on 15 of the 16
plans, it moves the critique's and the revision loop's reading of what is clear, and it would move
every pinned count downstream. Which of the two readings in item 2 to build is a ruling. A package
that did both at once could only be reasoned about as one.

## Corrected 28 September 2026 (the audit of WP-15.8's own diff)

**"Its seven clears are on one-storey houses" is wrong for one of the seven.** Re-derived with
`tests/fault_clears.py` on the tree before this correction, six of the seven are on one-level
houses: `bad-01`, `bad-02`, `bad-07`, `good-02`, `good-03` and `good-07`. The seventh,
`good-05-lobby-gallery-mansion`, has two storeys. Its record declares four windows on its S front
at the ground floor and none on the upper floor, so the alignment question does arise there, and
the honest verdict is unjudged rather than not applicable. The fault reads clear on the bay-count
floor in both cases. Auditor ab601 found it; the other figures in this entry re-derive exactly.
The sentence above is left as written.

## Ruled 29 September 2026 (Lucas, asked directly): the governing test decides

Asked: *when a fault's governing test can't run because its measurement isn't modelled, what
should the fault read?* Lucas chose **Governing test decides**:

> A clear needs the governing test to have run: the primary, or the exception's bounds test the
> style has earned. 142 verdicts become 'could not evaluate', with the tests that did run kept as
> evidence, and a clear names any secondary that did not run.

**What the ruling answers.**

- **Item 2:** the governing test, not every applicable test.
- **Item 1** follows from it: a secondary does not stand in for the primary.
- **Item 3** was ruled the same day in
  `oq/the-elevation-measures-a-front-the-drawn-layer-refuses-to-judge`: an unjudged fatal breaks
  ties against a candidate.
- **A failed test still makes a fault present.** The ruling is about clear.

**A correction to the option as it was put.** It said *"no ranking moves by itself"*. The planning
pass found that `compose.py`'s solecism share, clear / (clear + present) at weight 20, can reorder
candidates with equal fatal counts. WP-16.1 measures that and reports it, rather than leaving the
sentence standing. Executed by WP-16.1.

## Executed 29 September 2026 (WP-16.1)

`core._judge` takes the governing test first: the primary, or the bounds test of an exception the
style earns. A fault is clear only where that test ran and passed. Where it could not run and
another test did, the fault is could-not-evaluate and carries the tests that ran as `ran`, with
`governing_not_run` naming what it wanted. A clear lists every applicable secondary that did not run
as `secondaries_not_run`. A failed test of any kind still makes the fault present, as ruled.

**Measured over the sixteen shipped plans placed on `engine="heuristic"`, against a worktree of
`a4abb85`.** Every one of the 3,273 (plan, fault) verdicts is accounted for:

| Movement | Rows | Cause |
|---|---:|---|
| clear -> could-not-evaluate | 134 | this ruling: the governing test did not run |
| clear -> not applicable | 8 | two data gates the ruling made necessary (below) |
| present -> not applicable | 12 | the same gates: convictions on a phantom second storey |
| present -> could-not-evaluate | 15 | R12, `oq/the-elevation-measures-a-front-the-drawn-layer-refuses-to-judge` |

**The option said 142 verdicts would become could-not-evaluate; 134 did.** The other 8 were clear on
a precondition nobody had written: `overscaled-dormer` on the two houses that state no dormers (a
dormer's scale is not a question about a house without one), and `storeys-out-of-vertical-alignment`
on six one-storey plans. Both faults now carry `applies_when` on the premise, on
`dormer-off-the-bay`'s precedent, so those rows are not applicable rather than unjudged.
`tests/fault_clears.py` re-derives the figures and is the instrument to run, not this table. On a
tree with this ruling it reports 0 clears whose governing test did not run, 138 could-not-evaluate
rows carrying evidence, and 142 clears naming an unrun secondary. **That last 142 is not the 142
above:** on `a4abb85`, 284 clears had some applicable test unrun, 142 of them the governing test and
142 only secondaries. The first 142 left the clear list, and the second 142 stay clear and now say
what did not run.

**The solecism share.** The correction above said `compose.py`'s solecism share can reorder
candidates with equal fatal counts. It moved on every candidate, because clears left the
denominator. See WP-16.1's report §III for what it did to the returned sets.

Report: `docs/reports/wp-16.1-the-governing-test-decides.md`.

