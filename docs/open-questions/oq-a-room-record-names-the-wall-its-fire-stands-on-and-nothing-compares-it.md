# oq/a-room-record-names-the-wall-its-fire-stands-on-and-nothing-compares-it — two records do, and a prose reader would be 40% precise

*Status: OPEN — item 4 ruled 26 September 2026 (WP-14.33); items 1 to 3 remain · Raised in: WP-11.4, the hearth (4 September 2026)*

## The instance, which was a false claim in this package's own data

`plans/tidewater-georgian-careful.json` puts the dining room's fire on the **W** gable, and
`rooms/dining-room.json` says *"Historically a fireplace on the interior wall opposite the
sideboard."* Those disagree. The hearth I authored carried a note saying the disagreement *"is
reported by build/hearths.py rather than resolved silently"* — and it is not. `hearth_report` holds
a stated hearth against the **massing's** stack walls and against nothing else, so W passes:
W is exactly where `gable-end-paired` puts its stacks. The note has been corrected to say so.

That is the shape this project keeps finding in its own prose — a sentence describing a check
nobody wrote — arriving inside the package built to remove a version of it one layer down.

## Why the obvious fix was not taken

The obvious fix is a reader over `servicing.heat` looking for a named wall. Measured over all 60
room records, a regex for `interior wall|gable-end|corner|chimney breast|party wall|centre`
restricted to records that also mention a fire returns **five hits, of which two are the thing
being looked for**:

| record | matched | is it a wall for this room's fire? |
|---|---|---|
| `dining-room` | interior wall | **yes** — *"a fireplace on the interior wall opposite the sideboard"* |
| `bedchamber` | corner, gable-end | **yes** — *"A corner or gable-end fireplace"* |
| `drawing-room` | centre | no — *"it is the room's compositional centre"*, about composition |
| `library` | chimney breast | no — *"the shelving must be clear of the chimney breast"*, a clearance |
| `breezeway` | gable-end | no — *"each pen has its own gable-end hearth"*, about the pens |

Two of five. That is `oq/a-room-records-prose-states-a-floor-its-own-band-does-not` exactly: four
different jobs sharing one syntax, and a checker that tightens its regex until the number looks
better has made the corpus quieter rather than truer. Shipping it inside WP-11.4 would have
delivered a comparison wrong three times in five, against a package whose entire subject is not
inventing facts about fires.

## What must be ruled

1. **Does the wall become an authored field on the room record**, the way `hearth.wall` is authored
   on the plan? Two records would state one. That is the `measures` answer `check_grouping_rules.py`
   took to the same problem — an authored join beats a parsed one — and it is the only form in
   which a comparison can be trusted.
2. **Is `bedchamber`'s statement a disjunction that may not be resolved?** *"A corner or gable-end
   fireplace"* is a compound in the same sense `massings/catalog.json`'s *"gable-end-paired or
   central-stack"* is, which `build/hearths.py` refuses by name. If the field is authored it needs
   to admit both, and then a plan naming either satisfies it.
3. **Is `dining-room`'s `interior` a wall at all, or a relation?** *"opposite the sideboard"* names
   the wall by what faces it, and `build/hearths.py::breast` already declines to draw an `interior`
   hearth for want of knowing which of four sides that is. A comparison that cannot say which wall
   `interior` means cannot say whether W contradicts it.
4. **Whose statement outranks whose?** The massing pairs its stacks on the gables; the room record
   puts the dining fire inside. On a five-bay double pile both are period-correct and the plan is
   the thing that has to choose. This is the same shape as
   `oq/a-grouping-rule-and-a-room-record-can-disagree`, whose ruled answer is that a checker must
   REPORT and never reconcile by picking a side.

## The trap

**Do not close this by deleting the dining room's disagreement.** Moving the Tidewater fire to an
interior wall would make the corpus green and would remove the one instance anybody has looked at.
The disagreement is the specimen.

## Amendment (WP-14.21, 25 September 2026): item 4 now decides whether the worked house can place

WP-14.21 tried to author a Tidewater plan that places, and could not. Report:
`docs/reports/wp-14.21-the-worked-house-and-the-dining-fire.md`. The fact that decides it is this
entry's specimen.

**With the dining room's fire on the W gable, where the massing's paired end stacks put it**, the
dining room must span the whole west range to reach the passage. The butler's pantry must door it,
and then has no place inside its own size bands: it would need a side as long as the drawing room's
sixteen-foot floor, against its fourteen-foot length ceiling. The proof is in the report's §III, and
a solver model agrees. **With only the drawing room's fire on the gable**, the model finds a proper
four-over-four at once: the dining room is set in from the gable, and the pantry stands on the gable
in the hyphen's band. That is the house `rooms/dining-room.json` describes.

**The trap below held, and it was measured once rather than taken.** One control put the dining
room's fire on `interior`, labelled as the move this entry forbids.

- The fire then reads **unjudged** under the massing's flue walls: `typefacts.hearth` has no flue to
  hold an interior fire against.
- The house was still refused, on tiling and bearing on the prover and on stacks on the search.

So item 4 has a third half the entry did not list. If the room record's statement outranks the
massing's, the massing must state a flue for an interior fire before the hearth fact can judge one.
Until then that answer converts a downgraded fact into an unjudged one, which the WP-14.21 ruling
names as laundering.

`oq/the-worked-house-has-no-plan-that-places` is closed on this evidence, with its owner named as
item 4 of this entry.

## Ruled 26 September 2026: item 4, the style's statement governs (WP-14.33)

Lucas ruled item 4 on the day it was put to him, after WP-14.21 had made it the fact that decides
whether the worked house can be drawn: **the massing and the kit govern, and the room type's generic
record does not.** The Tidewater kit's `hearth_position` states the rule for this style in its own
words -- *"Hearths are at the gable ends, on the outside walls of the end rooms, so the mass of the
stack sits outside the heated volume in summer."* -- and `massings/catalog.json`'s four-over-four
pairs its stacks on the gables. `rooms/dining-room.json`'s *"interior wall opposite the sideboard"*
is a statement about the dining room as a type, across every style that has one, and a style that
states where its own fires stand outranks it.

**What the ruling changes, and what it does not.**

- **Nothing in the data moves.** `plans/tidewater-georgian-careful.json` already puts the dining
  fire on the W gable, which is what the ruling says it should. The trap below still holds: the
  dining room's record is not edited, because its sentence is true of the type and the disagreement
  is the specimen.
- **The worked house stays refused, and the refusal is now the house's own on a ruled reading.**
  Followed as the style says, the butler's pantry has no place inside its own size bands
  (WP-14.21 §III). The guided example stops at the brief, as it did; `glossary/guided-example.json`
  says the question is ruled rather than open. WP-14.28, the tour, stays NOT BUILT.
- **Items 1 to 3 are not answered by this**, so the entry stays open. A checker that REPORTS the
  disagreement, naming both walls, is what `oq/a-grouping-rule-and-a-room-record-can-disagree`'s
  ruling asks of any two records that disagree; it needs the wall as an authored field on the room
  record (item 1), a way to state a disjunction (item 2) and a reading of `interior` as a relation
  (item 3). None is built, and the prose reader this entry measured at two hits in five is still
  refused.

