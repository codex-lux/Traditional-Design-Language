# oq/a-room-record-names-the-wall-its-fire-stands-on-and-nothing-compares-it — two records do, and a prose reader would be 40% precise

*Status: OPEN · Raised in: WP-11.4, the hearth (4 September 2026)*

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
