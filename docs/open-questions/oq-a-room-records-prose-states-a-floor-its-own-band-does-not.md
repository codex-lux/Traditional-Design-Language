# oq/a-room-records-prose-states-a-floor-its-own-band-does-not — 35 figures in prose, and nothing can say which are governing

*Status: OPEN · Raised in: WP-9.7, the grouping-rule checker (2 Sep 2026)*

**`build/check_grouping_rules.py` compares a grouping rule against a room band. Building it
surfaced a second population it cannot judge: figures stated in a room's own
`critical_dimension` prose, or in a grouping rule's own `statement`, that no executable number
carries. There are 35, and the checker can tell you they exist and not what they mean.**

The demonstrated instance is `rooms/centre-passage.json`. Its prose says **"SECOND NUMBER: 5 ft
6 in is the floor"** and its `width_ft` band starts at **6**. One record, two floors, six
inches apart, and only one of them is machine-readable. That is the class OQ 48 named at the
pack layer — two records meaning one quantity under two names — with the second record being the
first record's own prose.

## Why the meter cannot settle it, and why tightening the regex is the wrong move

The meter reads figures in the band's own units, digits and number-words both, and reports any
that is neither end of the band. It **overcounts on purpose**, because a room record's prose
legitimately does several different jobs with a number and nothing in the record says which:

- **A governing floor the band does not carry** — `centre-passage`'s 5 ft 6 in. A real
  disagreement.
- **A reasoned two-tier statement, which is not a disagreement at all** —
  `rooms/bedroom.json` says *"a 9 ft 0 in clear width, and that is the ABSOLUTE floor"* and then
  *"11 ft 0 in is the real minimum"*, and its band takes the 11. The record is doing exactly what
  it should: naming the physical limit and the practical one, and banding the practical one.
  **A checker that flagged this would be wrong**, and it is the reason this is a question rather
  than a patch.
- **An arithmetic step** — *"a bed is 6 ft 3 in and needs a passage beside it"*. The 6 constrains
  nothing.
- **A cited measurement of the historical population** — the piazza's *"the measured Charleston
  piazzas run 8 to 12 ft"*, which is evidence for the band rather than a rival to it.

Four jobs, one syntax. **Ratcheting the count down by narrowing the regex would delete the first
category along with the other three**, which is measuring less and calling it agreeing more — the
failure `check_grouping_rules.py`'s own `compared` floor exists to catch one layer over.

## The neighbouring finding, recorded here because it has the same cause

The same pass found **three statements of the keeping room's radiant reach**:
`groupings/keeping-room-hearth-cluster.json` reasons in prose to *"within about 12 ft of the
fire"*, its own test admits `hearth_to_far_wall_ft at-most 14`, and
`rooms/keeping-room.json` says *"THE RADIANT REACH OF THE FIRE, AND IT IS 10 FT"*.
`oq/a-grouping-rule-and-a-room-record-can-disagree` recorded the first two and its entry was
audited twice. The third was found by a machine in the first run of a checker.

And `contemporary-service-core`'s mudroom rule agrees with the room's prose (*"DEPTH ACROSS THE
BENCH, AND IT IS 5 FT, NOT 4"*, rule `at-least 5`) while `rooms/mudroom.json` bands its width
from **6**. The register deliberately declined to claim that pair, on the grounds that "clear
width" may be a different quantity from the band's nominal width — which is right, and is itself
the unresolved half.

## What would have to be decided

1. **Does a room record get a typed second floor?** A `critical_dimension` is prose by design and
   `docs/model.md` wants it that way. An `absolute_floor_ft` beside the band would make
   `centre-passage`'s 5 ft 6 in and `bedroom`'s 9 ft executable and comparable — and would ask a
   number of 60 records, most of which have no such figure and must be allowed to say so.
2. **Or is the band simply wrong where the two differ?** Cheaper and probably wrong: the piazza's
   evidence is on the record's prose and the passage's is split across five files that do not
   agree with each other. **The corpus's first rule applies** — a number authored to settle a
   disagreement, with no source, is `editorial` / `judgment: true` and says so in its own note.
3. **Or is this `oq/register-is-not-style`'s?** `centre-passage`'s prose does not state one floor;
   it states *"SIX TO SEVEN FEET is a passage that circulates … TEN TO TWELVE FEET is a passage
   that is a room"* and calls 8 to 9 ft a dead zone. Those are two populations, not two opinions,
   and the axis that separates them is register. A single floor for both is the thing that cannot
   be right.

## What must not happen

Do not reconcile an instance by moving the band to match the prose, or the prose to match the
band, to make a count fall. And do not narrow the meter: it is an upper bound that says so, and
an upper bound with the sentence printed beside it is worth more here than a smaller number
nobody can audit.
