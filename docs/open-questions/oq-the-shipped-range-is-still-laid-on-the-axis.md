# oq/the-shipped-range-is-still-laid-on-the-axis — the one shipped record with a dependency does not state the laying Lucas ruled

*Status: OPEN · Raised in: the garage is its own mass (26 to 27 November 2026)*

**OPEN — Lucas ruled that a house with dependencies on one flank stands that range against its rear
wall. `plans/tidewater-georgian-careful.json` is such a house, and it is still laid on the main
block's axis, because stating the laying there moves a shipped placement and that was not done
inside a package about a composed diagram.**

## What was ruled, and how it was built

The ruling is recorded in `oq/the-double-piles-service-wing-cannot-tile-on-its-hyphens-face`
(asked and answered, 3). Its basis is `groupings/dependency-and-hyphen.json`, hard: "Where
dependencies are paired they are symmetrical about the main block's axis; where there is one, it
does not sit on the entrance elevation."

The first build read the laying off the flank alone, so it reached every record with one range.
The second, which shipped, makes it a statement of the record: `plan.flank_laying` (plan schema
0.14.0), `rear` or `axis`, absent meaning `axis`. The composer writes `rear` on every house it
composes with a `block` tag. The shipped record carries no such key.

## What was measured on the shipped record before the statement was made a field

One run each, 27 November 2026, against a worktree of the parent commit `cc98832`.

| engine | on the axis (parent) | against the rear wall |
|---|---|---|
| search (`engine="heuristic"`), refused for | bearing, stacks | bearing, hearth, stacks |
| search, findings | 6 fatal, 59 serious, 100 minor | 9 fatal, 65 serious, 96 minor |
| search, hearth fact | held | downgraded |
| prover (40 s, four workers), refused for | bearing, hearth, tiling, PROVEN | the same three, PROVEN |
| prover, findings | 1 fatal, 45 serious, 98 minor | 1 fatal, 45 serious, 99 minor |
| prover, rooms past their band | kitchen, pantry | kitchen |

With the range against the rear wall, 14 of the 361 tests in the seventeen element test files went
red, every one on this record's moved placement. The whole suite was not run that way.

The prover's wing-sizing step (`geometry_cp.size_wings`) was also asked of this record's wing on
the axis: none of the 50 boxes in its window held the wing's own rooms and doors, in 4.5 s, so the
derived 27 x 23 ft box stands and the record says so.

## Why it was left

Moving a shipped placement re-derives every pin that reads it, and this project has kept that out
of a package about something else each time it came up: WP-11.13 left the `block` tags to
WP-11.16, and Phase 17 left `oq/a-shipped-record-files-a-wet-stack-as-structural` at a ceiling of
one. The plan Lucas approved for this package said the record would move and be re-derived. It was
not, and that is a deviation from the approved plan, taken on that precedent and on the table
above: on the engine that draws the sheet the record is no better for it, and on the search it is
worse.

## What would close it

One key on the record, `"flank_laying": "rear"`, in its own package: the placement, the openings,
the sheets and the findings re-derived per plan against a control, with the search's three more
fatal findings named rather than netted off. Or a ruling that this record keeps the axis, with the
reason written beside the grouping's sentence.

## What it is not

It is not a second rule. `geometry.flank_laying` is the one reader, and a record that states
`rear` is laid the same way whoever wrote it.
