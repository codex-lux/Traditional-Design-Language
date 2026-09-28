# oq/the-openings-are-not-set-to-the-brick-courses — two packs state a window's head in a brick wall, and the elevation draws the one that is not in courses

*Status: OPEN · Raised in: WP-14.3, trim, openings, eave, section, roof (27 September 2026)*

**The Tidewater elevation draws brick-course's coursing behind every opening, and not one sill
or head on it lands on a course.** Measured on the WP-14.3 tree, heuristic placement: on the S
face 10 of 10 sill and head lines miss the 2.75 in courses, by up to 1.00 in; on the N face 10 of
10, by up to 1.00 in; on the W face 2 of 2, by up to 0.60 in. (A line can miss by at most half a
course, 1.375 in.)

brick-course says why that is wrong, in its own notes:

> in a brick building there are no free horizontal dimensions above the water table. Storey
> height, sill height, head height, belt course and plate are all whole numbers of courses off a
> single datum

> The opening height is not a design number — it is whatever whole multiple of the course lands
> nearest the intended proportion, because the head of the opening has to be a bed joint.

> Modern practice does the reverse, which is why modern traditional brickwork so often has a cut
> course under a sill or a belt that misses the floor line by two inches.

It states a rule for the head in whole courses, `head_height_above_floor = round(opening_width *
2.05 / part) * part`. **The elevation does not read it.** `elevation._storey_window` sets the head
from opening-proportion's `window_head_wood`, a rule of the ceiling height, and the sill at
`TARGET_SILL_IN`, the 30 in midpoint of storey-graduation's 28 to 32 in convention. Neither is a
number of courses. Both are applied to every style, brick or frame.

## What WP-14.3 did

It measures the misses and says them on the sheet: *"N OF M SILLS AND HEADS MISS THE 2.75″
COURSES BY UP TO X″ — BRICK-COURSE SETS SILL AND HEAD HEIGHT IN WHOLE COURSES; THE OPENINGS KEEP
THEIR STOREY’S OWN HEAD AND SILL, AND SNAPPING THEM IS AN OPEN QUESTION"*. Census check V11 holds
the sheet to it. Nothing is moved.

## Why this is a question and not a patch

Three answers are available, and each moves a different record:

1. **brick-course governs a masonry wall.** The head and the sill snap to whole courses, or the
   head is taken from brick-course's own rule. Every Tidewater window moves by up to half a
   course. The window's height, its lights and every fault that reads a head or a sill move with
   it, and a frame-built style has to be told apart from a brick one first (the construction
   scope WP-8.4 built can do that).
2. **The storey is set first.** brick-course's notes also say *"The belt course lands on the
   course line nearest the second-floor structure, and then the storey height is adjusted to
   match — not the other way round."* The storey height itself comes from the plan's stated
   ceilings through `build/storeys.py`. Snapping the openings without the storey leaves the belt
   and the plate where they are. Doing it properly moves the section too.
3. **The drawing is not modelled at course precision.** Then the courses should not be drawn as
   though it were, or the sheet should call them schematic.

The first reads brick-course's rule as governing; the second reads its own procedure as the rule;
the third declines both. None of them is a figure this package may choose.

## Where it lives

`build/elevation.py` (`_storey_window`, `TARGET_SILL_IN`), `proportions/modules/brick-course.json`
(`head_height_above_floor` and its notes), `opening-proportion.json`'s `window_head_wood`,
`build/storeys.py`, and `build/render_elevation.py`'s coursing and its note. Census check V11
measures it.
