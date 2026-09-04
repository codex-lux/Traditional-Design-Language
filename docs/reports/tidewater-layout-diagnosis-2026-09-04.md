# The Tidewater sheet, read as an architect reads it — a diagnosis, 4 September 2026

*Lucas put the workbench's rendered sheet for `plans/tidewater-georgian-careful.json` in front of
this session and asked for a diagnosis first, before saying what he sees wrong with it: research
how the period laid out this kind of house, state the rules of thumb, compare, and list every issue
in detail. This document is that diagnosis. It is written to be the brief for the next round of
work on the composer and the workbench, so each finding names the layer that owns it and what a
fix would have to touch. Where a finding was already recorded somewhere in this tree it says so and
cites the place; where it is new it says that too.*

*Provenance discipline, stated first. Three things were read: the screenshot Lucas supplied; the
declared record in `plans/tidewater-georgian-careful.json`, unchanged; and two fresh placements of
that record made here on 4 Sep — one on the CP-SAT engine (`--engine cp`, the engine the sheet
names) and one on the hill-climb (`--engine heuristic`). The period facts in Part II come from a
research pass whose every figure carries its source; where the source is a museum's or HABS's own
statement it is marked measured, where it is an author's characterisation it is marked so, and
where nothing could be reached the gap is named rather than filled. No facsimile was read. Nothing
in this document was quoted from `CLAUDE.md` alone.*

---

## 0. The short version

The sheet is not a Georgian house drawn badly. It is a different building — a two-storey box
subdivided into twenty-four spaces by a solver that was given the right room list and the wrong
container, and that preserves one quantity, area, while it loses every other one the type is made
of: the axis, the front, the square, the hearth, the stack, the bay. Every one of Lucas's likely
complaints traces to one of eight causes, and five of the eight are not defects in the placer at
all. They are things the model has no word for.

The eight, in the order a builder would meet them:

1. **The programme was never the type's.** The parti asks a four-room-per-floor box to hold eleven
   enclosed ground spaces and a portico (the shipped record adds a cellar stair and a terrace) and
   eleven upper ones, with the kitchen, hyphen and dependencies drawn
   inside the block they are named as being outside of. That is recorded and ruled
   (`oq/the-parti-dissolved-its-own-dependencies`) and nothing has yet been built on the ruling.
2. **The record as declared cannot be built in a 60 x 40 rectangle, and the "proved" placement is
   the record with sixteen of its exterior-wall declarations set aside.** Both ends of the passage
   are among the sixteen. The sheet says *"placement proved against the record's declared facts"*.
3. **The placer's compositional objective never ran.** The CP-SAT solve returns the first
   hard-valid placement it finds (phase A, "best of 1"); the polish phase that carries every
   compositional term timed out, so on the proving engine there is no term at all for the front,
   the axis, the mirror pair or the stack. The hill-climb, which does run those terms, produces a
   better house on the corpus's own score (712.6 against 835.0) and the workbench chooses the
   worse one by design.
4. **There is no axis in the model.** Nothing knows which bay the door is in, whether the passage is
   central, or that an even bay count has no centre. The footprint is six bays of 10 ft under a
   title that says five.
5. **There is no hearth in the plan layer.** No room record, no placer reservation, no line on the
   plate. The massing says paired end chimneys and four fireplaces a floor; the roof and elevation
   layers draw the stacks; the plan they stand on has no fireplace in any room.
6. **The upper floor is placed as a second, unrelated plan.** Thirty upper wall lines land on no
   wall below; the passage upstairs is not over the passage downstairs; the landing is not over
   the stair.
7. **The facade is not a result of anything.** Windows are placed per room after the fact, 27 of
   35 declared ones cannot be placed at all, and the sheet does not say so.
8. **Area is the one thing the placement conserves.** Twenty-three of the twenty-four rooms drawn
   are at a size the record does not declare, and the slivers among them are inside their area
   band and outside their width or proportion band — nine of eleven when WP-9.2 measured it, and
   the same shape here.

The rest of this document is the evidence. Part I transcribes the sheet. Part II states what the
type does, with sources. Part III is the itemised diagnosis, fifty-one findings in ten tiers. Part
IV maps each to the layer that owns it. Part V is the root causes. Part VI is what the corpus
already says in prose and cannot execute. Part VII is the order of work.

---

## I. The house on the sheet

### I.1 The screenshot, transcribed

The plate is the workbench's plan sheet: title *"Tidewater Georgian, five bays, carefully
planned"*, subtitle `palladian · 6 BAYS OF 10.0 FT · 60' x 40' · 2400 SF GROSS`, four disclosure
lines (12 cuts off the bay line, worst 5.0 ft; one declared door without a drawable opening,
breakfast–terrace; 23 rooms drawn at a size the record does not declare, worst chamber bath +81%
by area; placement proved (CP-SAT) against the record's declared facts). North is up; the entrance
front is south, at the bottom of each plate. Dimensions below are the plate's own labels, feet and
inches as printed; where a room's label was unreadable the figure is scaled off the 10 ft bar and
marked ≈.

**Ground floor, west to east.**

| Room as labelled | Drawn | Where it sits | Exterior walls it reaches |
|---|---|---|---|
| Entrance Portico | 7' x 11' · 77 sf | SW corner, INSIDE the block | S (carries a window tick) |
| Centre Passage | 11' x 33' · 363 sf | the whole WEST bay, portico at its south end | W, N |
| Stair Hall | 7' x 21'-11" · 153 sf | along the NORTH wall, stair E–W, "UP 20R" | N |
| unlabelled room | ≈ 6' x 7' | between stair hall and powder room | N |
| Powder Room | ≈ 6' x 7' | N wall, entered from the unlabelled room | N |
| Drawing Room | 11' x 34' · 374 sf | dead centre of the block | none |
| Dining Room | 9' x 34' · 306 sf | dead centre, south of the drawing room | none |
| Library | 13' x 19' · 247 sf | S front, second and third bays | S |
| Butler's Pantry | ≈ 20' x 4' | between dining and breakfast | none |
| Breakfast Room | 9' x 20' · 180 sf | S front, fourth and fifth bays | S |
| Back Hall (Hyphen) | 5' x 27' · 135 sf | a north–south slot east of the drawing room | N |
| Cellar Stair | ≈ 4' x 9' | NE, between back hall and pantry | N |
| Pantry | ≈ 6' x 9' | NE corner | N, E |
| Kitchen (Dependency) | 10' x 31' · 310 sf | the whole EAST bay below the pantry | E, S |
| Terrace | not drawn | — | — |

**Upper floor, west to east.**

| Room as labelled | Drawn | Where it sits | Exterior walls it reaches |
|---|---|---|---|
| Principal Chamber | 10' x 40' · 400 sf | the whole WEST bay, full depth | W, N, S |
| unlabelled room | ≈ 9' x 4' | N wall, west of the closet | N |
| Closet | ≈ 9' x 4' | N wall | N |
| Dressing Room | 9' x 19' · 171 sf | interior | none |
| Principal Bath | 13' x 19' · 247 sf | interior | none |
| Stair Landing | 5' x 19' · 95 sf | interior, over the library's north edge, not over the stair | none |
| Chamber 2 | 13' x 31' · 403 sf | N front to the upper passage | N |
| Chamber Bath | 5'-2" x 31' · 159 sf | a slot between Chamber 2 and Chamber 3 | N |
| Chamber 3 | 12'-1" x 31' · 376 sf | NE | N, E |
| Upper Passage | 9' x 43' · 387 sf | along the SOUTH (entrance) front | S |
| Linen Press | ≈ 3' x 8' | SE, off the passage | S |
| Closet | ≈ 3' x 8' | SE corner, with a window on the entrance front | S, E |

**What the entrance front shows, read off the two plates.** Ground storey, west to east: a window
in the portico's front wall, two windows to the library, one to the breakfast room, one to the
kitchen — five openings, and the front door is not legible on the plate as a door swing at all.
Upper storey: one window to the principal chamber, one to the upper passage, one to the closet in
the corner — three openings, none over the ones below. The gable ends carry one window each on the
upper storey and a chimney nowhere.

### I.2 The same record, placed again here

The record was placed twice more on 4 Sep, from `plans/tidewater-georgian-careful.json` unchanged,
by `build/geometry.py` on the CP-SAT engine with its default budget and then on the heuristic.

**The CP-SAT placement is a different house from the screenshot's** — the passage lands in the
FIFTH bay (x 40–50) instead of the first, the portico becomes a 23 x 3 ft strip along the front,
the drawing room goes to the rear wall and the dining room to the middle, and the upper passage is
a 31 x 20 ft blob of 620 sf. Two CP-SAT runs here were byte-identical to each other (25 of 25
rooms, same score, same downgrade list), so the solver is stable on one machine with one input;
the difference from the screenshot is in what the bench sent — the sheet's style slot reads
`palladian`, which is a different style node from the record's `tidewater-georgian`, and the
bench's drawing route can hand the solver a parti (`body.get("parti")`) where this CLI run passed none. **The defect classes are the same
in both placements and in the heuristic's third one**, which is the point: this is not one bad
seed.

| | screenshot (CP-SAT, via the bench) | CP-SAT here | heuristic here |
|---|---|---|---|
| passage position | west bay, 11 ft | fifth bay, 10 ft, 3 ft short of the front | x 20–30.7, through S–N |
| portico | 7 x 11 inside the block | 23 x 3 strip on the front | 10 x 6 on the front |
| drawing room | 11 x 34, no exterior wall | 25 x 16 on the REAR wall | 20 x 16.6, SW, front and gable |
| dining room | 9 x 34, no exterior wall | 17 x 17, no exterior wall | 20 x 13.4, W gable |
| kitchen | 10 x 31 in the E bay | 10 x 30 in the W bay, on the FRONT | 20 x 10 NW |
| upper passage | 9 x 43 along the FRONT | 31 x 20, 620 sf, interior | 16.7 x 40 through |
| principal chamber | 10 x 40, W bay | 29 x 14, no exterior wall | 20 x 24 SW |
| rooms diverged from record | 23 | 24 | (not counted) |
| corpus score, lower is better | not printed | **835.0** | **712.6** |

The heuristic's house is, on the corpus's own demerit total, the better of the three by a wide
margin, and it is the one the workbench refuses to draw because it is not a proof. That trade is
examined in III.J.

### I.3 What the solver itself recorded, and the sheet did not print

`geometry_report.solver` on the CP-SAT placement here:

```
status:  OPTIMAL (hard-only) — kept hard-only phase A (best of 1 hard-valid placements)
objective: null
attempts: 6b r0 INFEASIBLE · r1 INFEASIBLE · r2 INFEASIBLE · r3 UNKNOWN · r3+ OPTIMAL ·
          restore backhall N OPTIMAL · restore backhall S INFEASIBLE ·
          restore butlers N UNKNOWN · restore dining N UNKNOWN · restore dining W UNKNOWN ·
          polish-h UNKNOWN
downgraded_wall_pins (16):
  L0 backhall S · butlers N · dining N · dining W · drawing S · drawing W · passage N · passage S
  L1 chamber2 N · chamber2 W · chamber3 S · dressing W · primary S · primary W · primarybath N ·
  upperpassage S
```

Read plainly: the record as declared was proven infeasible in the 60 x 40 rectangle at three
successive relaxation rounds; at the fourth the solver set aside a conflict core of sixteen
exterior-wall declarations, found ONE placement that satisfies what was left, tried to restore
five of the sixteen individually and managed one, and then ran out of budget before the weighted
objective — every compositional term the engine has — could run at all. `objective: null`. The
sheet's line for this is *"PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS"*, in
the reassuring colour. It is true of the hard constraints that survived. It is not true of the
passage's two end walls, the drawing room's two window walls, the dining room's two, the principal
chamber's two, or the upper passage's front — every one of which is a declared fact the sheet
claims the placement was proved against.

**Why the declared record is infeasible is itself diagnostic.** On the west side alone the drawing
room declares S and W, the dining room N and W, the kitchen N, S and W: three rooms claiming the
same gable, one of them claiming the full depth. The porch declares S, E and W — three sides
exposed — which is a description of a thing that PROJECTS, not a corner of a rectangle. The back
hall declares N and S, which is a hyphen's two long sides. The breakfast room declares E and S and
so does the library. These are the exterior walls of a five-part house — main block, hyphen,
dependency, portico, terrace — written on rooms that are then handed to a solver holding one
rectangle. `geometry_cp.py`'s own docstring says it: *"`exterior_walls` speaks EXPOSURE in the
fully-massed house."* The infeasibility is the model reporting, correctly, that the programme is
not a box; the solver's remedy is to delete the exposure and keep the box.

---

## II. What the type does — the yardstick, with sources

Two research passes were run for this document: one over the Chesapeake exemplars through the
HABS written data at `tile.loc.gov` (the route `oq/fetching-through-a-tier-the-proxy-denies`
records) and the houses' own institutions, one over the treatises and the modern pattern
literature. Every figure below is quoted from the sentence it came from. **M** marks a survey or
museum measurement; **A** an author's or owner's figure; **via** means the passage was read in a
work quoting it, not in the original. What could not be reached is in Part VIII. The agents'
method finding from WP-9.2 applies throughout — *"an agent's 'not in the source' is a search
result, not evidence of absence"* — so "not stated" below means not stated in the span reached.

### II.1 The exemplars

| House | Envelope | Front | Passage | Stair | Chimneys and hearths | Kitchen | Upper floor |
|---|---|---|---|---|---|---|---|
| **Gunston Hall** 1755–59, HABS VA-141 (M) | *"a rectangle of 40 feet 11-1/2 inches by 60 feet 10 inches, exterior foundation measurements"*; walls *"about two feet thick"* | *"four large windows on each of the north and south facades, with a pair of smaller windows flanking the main doors"*; gables *"three windows in their gables"* between the stacks | *"a central passage running north and south"*, door at each end (fantail transoms); width not stated by HABS, "12-foot-wide" (A) | **In the passage**: *"located in the north end of the center passage, and starts against the east wall. It has one landing against the north wall and returns against the west wall"* | *"four tall chimney stacks on the house, two at each end. All fireplaces are against the end walls, and are centered in the rooms, with either a pair of closets or cupboards flanking them"* | detached, foundation NE of the house | a garret under dormers: *"a long narrow central gallery through the middle, running from east to west"*, six rooms |
| **George Wythe House** 1752–54, CW report RR1483 (M, 1801 policy) | *"Dimensions 36' x 54'"*; *"a wooden kitchen 33' x 18'"* as a dependency | *"two windows on each side of the door, and five windows in alignment with the bottom windows on the second floor"* (Wythepedia, A) | *"standard center-passage, double-pile plan"*; *"The hall contains four doors leading to the rooms"* | *"A staircase rises on the left side of the passage"* | *"Two great chimneys between the paired rooms afford a fireplace in all eight rooms"* (CW, A) | detached frame kitchen | four chambers, *"Each of these rooms has a fireplace"* |
| **Westover** c.1750, HABS VA-402 (A) | not stated | *"front seven bays … center door; front and rear similar except for doorway"* | *"off center through hall; pair of large rooms toward east; smaller rooms toward west"* | not stated | *"two chimneys each end"* | brick dependency, *"end chimneys; story and a half"* | not stated |
| **Wilton** 1750–53, DHR 127-0141 (A) | *"shares its plan and dimensions with nearby Westover"* | *"five-bay house with a shallow hipped roof"* | *"central-passage, double-pile … the passage is slightly off-center, making the east rooms smaller than the west"* | **In the passage**: *"The broad passage accommodates a handsome walnut left-to-right, triple-run stair"* | *"four tall interior end chimneys"* | not stated | not stated |
| **Carter's Grove** 1751–55, HABS VA-351 (A) | not stated | *"north front is five bays wide with a center door, and the south front seven bays. Each end has two windows on each floor"* | entrance hall on the axis | **Separate stair hall, on the axis**: *"a large rectangular room with an arch in the north wall leading to the stair hall"*; SAH: *"a T-shaped stair hall flanked by two entertaining rooms on the front and two private rooms on the rear"* | not stated in span | two detached dependencies, *"three bays long with a center door"*, connections added 1928 | not stated |
| **Kenmore** 1770s, HABS VA-305 (A) | *"about 4,700 square feet"* (A) | *"facade five bays; center door; lower windows 9 over 9 lights, upper 6 over 9"* | *"center hall in front; two unequal rooms at rear"* — not through | not stated | *"pair of inside end-chimneys each end"* | separate dependency | not stated |
| **Mount Vernon** (frame), museum (M) | 11,028 sf total with wings | — | *"Central Passage 13' 3" x 30' 8" long x 10' 7 ½" high"* | in the passage | — | in a wing, by quadrant colonnade | chambers 17 x 14, 17 x 17'6", 16'6" x 15'4" |
| **Hammond-Harwood** 1774, HABS MD-251 (A) | *"approximately 44x42'"* main block, wings 34 x 18, links 18 | *"A pedimented three bay central pavilion"* | *"central entrance hall, with a room on each side"*; *"two doorways on each long wall and one centered on each end wall"* | separate: *"A stair hall is located just behind the west parlor … an open well, 10 risers to the first landing, 3 to the second landing and 10 to the second floor"* | not stated in span | in a wing, *"A large central chimney divides this into a larger and smaller area used as a kitchen"* | *"The second floor plan is identical to that of the first floor"* |
| **Chase-Lloyd** 1769–74 (A) | *"54 feet wide and 43 feet deep … 18 inches thick walls"* | — | *"four room, center hall type, but on a very large scale"* | *"a central stair rises to the large Palladian window at the landing"* | — | — | — |
| **Berkeley** 1726, HABS VA-363 (A) | walls *"36 inches thick"* (owner) | *"the door being in the center with two windows on either side"* | *"a spacious central hall divides the home"* | — | — | — | *"each [floor] containing four grand rooms"* (owner) |
| **Drayton Hall** 1742, HABS SC-377 (M) | *"70'-5" x 52'-2", excluding portico; 7-bay front"* | — | Great Hall then *"the two-story stair Hall"* behind it | in its own hall behind the great hall | *"Fireplaces are centered in each bedroom"* | — | drawing room *"flanked on each side by two bedrooms"* |

**Mount Vernon's room shapes**, museum figures, width x length as the museum states: Front
Parlor 16'9" x 16'6" (1.02); Dining Room 15' x 17' (1.13); Little Parlor 16'9" x 13' (1.29);
Old Chamber 15' x 13' (1.15); Study 19'6" x 16'9" (1.16); the three named upper chambers 1.21,
1.03 and 1.08. The one room past 1.3 is the passage at 2.31. These are the only room-by-room
dimensions any pass reached, and the study of 2 Sep already warned that a distribution built on
one house may be characteristic of Mount Vernon and not of the tradition.

### II.2 What the exemplars agree on

Read across the table, seven things hold in every centre-passage house reached whose source
speaks to them, and every one is contradicted by the sheet:

1. **The door is in the centre of the front, and the front is odd-bayed** — five or seven — with the
   windows *"in alignment"* storey over storey (Wythe), two windows either side of the door
   (Berkeley, Kenmore, Carter's Grove).
2. **The passage takes the centre of the plan and runs to a door at each end** where it is a
   passage at all. It may be *"slightly off-center"* (Westover, Wilton) so that one pair of rooms
   is larger than the other — that asymmetry is the period's, and it is an asymmetry of ROOM
   size about a centred door, never a passage moved to the side.
3. **The stair is either in the passage (Gunston, Wythe, Wilton, Mount Vernon, Chase-Lloyd), in
   its own hall on the axis behind the entrance hall (Carter's Grove, Drayton, Shirley), or in a
   stair hall behind one parlour (Hammond-Harwood).** Nowhere is it in a slot along the rear wall
   off the end of a side passage.
4. **Every room has a fireplace, and the fireplaces are on the end walls, centred, closets either
   side (Gunston), or on the cross-wall between the paired rooms (Wythe), with the stacks paired
   at each gable.** The gable is composed around the stacks: *"three windows in their gables"*
   between them at Gunston, *"two windows on each floor"* at Carter's Grove.
5. **The kitchen is a separate building** at every house whose source says where it is, or in a
   wing reached by a link
   (Hammond-Harwood, Mount Vernon); the UVA thesis on the detached kitchen gives the reasons —
   smoke, fire, and the labour system — and the distance, *"at least 20 feet from the house."*
6. **Four principal rooms a floor, near-square where measured (Mount Vernon, 1.02 to 1.29)**,
   front pair for entertaining and rear pair
   private (Carter's Grove), unequal in size across the passage (Westover, Gunston, Kenmore),
   never a corridor-shaped one among them.
7. **The upper floor repeats the ground plan** in the full two-storey houses (Hammond-Harwood
   *"identical"*, Wythe four chambers each with a fireplace). Gunston's cross-wise garret gallery
   is a storey-and-a-half under dormers and this plan states it has none.

### II.3 The rules of thumb, period and modern

Numbered so Part III can cite them. **PERIOD** is a pre-1900 treatise in the edition named;
**MODERN** is scholarship or practice since.

**Symmetry, axis and front.**
R1. *"those on the right-hand side must correspond to, and be equal to, those on the left … the
walls will take the weight of the roof equally."* Palladio, *Quattro Libri* II.ii, Hersey and
Freedman's translation. PERIOD.
R2. *"In the centre of this exactly must be placed the door, and on each side of this there is to
be one window in the middle, and two windows are to be in each of the sides."* Ware, *Complete
Body of Architecture* (1756). PERIOD.
R3. *"The door being placed in the centre of the house, the ascent to it must be by a flight of
steps: these should be so broad as to occupy the whole centre of the front."* Ware 1756. PERIOD.
R4. *"keep the window widths aligned from floor to floor and increase the height as necessary."*
Cusato, *Fine Homebuilding*. MODERN.
R5. *"Not only should everything on the outside align, but windows or pairs of windows should be
centered in interior rooms, too."* Mouzon, *A Living Tradition*. MODERN.
R6. The front-door bay *"may be equal to or wider than the others"*, never narrower. Mouzon.
MODERN.

**The passage and the stair.**
R7. The passage was *"inserted between the two principal rooms"* as *"an architectural baffle, or
zone of transition"*. Upton 1982 via Wells 1998. MODERN, via.
R8. *"first introduced to channel movement … it gradually evolved, on account of the doors
positioned at each end, into a light and cool summer living area. After 1750 gentry planters began
to widen, bisect, and embellish"* it. Wenger 1986 via Wells 1998. MODERN, via.
R9. *"we may consider any width from 6 to 12 feet as belonging to a Corridor; the suitable width
for a Gallery being from 14 to 20 feet."* Kerr, *The Gentleman's House* (1864). PERIOD.
R10. *"the Staircase ought to be so placed as to afford direct passage … from the Public-rooms to
the Bedrooms; and secondly, the access from the Entrance ought to be equally direct."* Kerr 1864.
PERIOD.
R11. *"The Library is marred by being made a thoroughfare to the Breakfast-room"* — no sitting
room a thoroughfare. Kerr 1864. PERIOD.
R12. *"Place the main stair in a key position, central and visible. Treat the whole staircase as
a room."* Alexander, *A Pattern Language* 133. MODERN.
R13. *"Keep passages short. Make them as much like rooms as possible."* Alexander 132. MODERN.

**Room shape.**
R14. The seven shapes: *"round … or square, or their length will be the diagonal line of the
square, or the square and a third, or of one square and a half, or of one square and two-thirds,
or of two squares."* Palladio I.xxi, Ware's 1738 wording. PERIOD.
R15. *"that the Length of no Room exceed a Double Cube … the nearer a Room (in particular a Hall)
is to a Square, the more uniform and commodious."* Morris, *Lectures* (1734), reporting Palladio.
PERIOD, and already in this tree with the caution that Morris is Palladio at one remove.
R16. *"there be large, middle-siz'd, and small Rooms; and that they be all near one another."*
Palladio II.ii, Leoni. PERIOD.
R17. *"from fifteen to two and twenty foot, is the measure of breadth for a gallery … Its length
may be from four to eight times its breadth."* Ware 1756 — which is the category a 3:1 or 4:1
room falls into. PERIOD.
R18. *"a room of medium dimensions and ordinary proportions, say 24 feet by 18."* Kerr 1864.
PERIOD.

**Daylight and aspect.**
R19. *"the Summer-rooms be large and spacious, and open to the North; and the Winter ones smaller
and open to the South and West … Studies and Closets must also have the same prospect [east],
because the Morning is the best time."* Palladio II.ii, Leoni; Ware 1756 repeats it. PERIOD.
R20. *"South-east the Drawing-room Façade, North-west that of the Dining-room, and North-east
the Offices"*; west *"the worst in the whole compass."* Kerr 1864. PERIOD.
R21. *"The evils of borrowed lights, skylights, and wells."* Kerr 1864, ch. VII. PERIOD.
R22. *"Locate each room so that it has outdoor space outside it on at least two sides."*
Alexander 159, Light on Two Sides of Every Room. MODERN.
R23. *"Make each wing long and as narrow as you can — never more than 25 feet wide."* Alexander
107. MODERN.

**Hearths.**
R24. *"the door should be far from both the fire and the window …; the window should be near the
fire …; the door should not come between the fire and the window; the window should light both
sides of the fire; and the fire should have a central position in the room. Accordingly the
fireplace, in ordinary cases, is best situated in the middle of one side."* Kerr 1864. PERIOD.
R25. The chimney opening is sized to the room — a 12 ft cube takes a 3'0" x 3'0" x 1'6"
opening, a 22 ft cube 4'1" x 4'1" x 2'0¼". Morris, Lecture 6, table. PERIOD.
R26. *"end chimneys, which provided a distribution of heat toward the center of the house in
colder months while creating space for the flow of air between them during the hot and humid
summers, had replaced the central chimney"* by 1700 in Virginia and Carolina. Wenger, via a
South Carolina dissertation. MODERN, via.

**Service and privacy.**
R27. *"The family constitute one community: the servants another … each class is entitled to
shut its door upon the other."* Kerr 1864. PERIOD.
R28. *"the dinner-route simply as bad as bad could be, — through the Principal Staircase, in
direct view of the Entrance."* Kerr 1864. PERIOD.
R29. *"the two principal rooms upon a first floor communicate by a door in the centre of the
partition … it becomes as one apartment."* Ware 1756. PERIOD.
R30. *"most detached kitchens were at least 20 feet from the house, although they were also
usually the closest of secondary buildings."* UVA thesis on the detached kitchen. MODERN.
R31. Intimacy gradient: *"a sequence which begins with the entrance and the most public parts …
and finally to the most private domains."* Alexander 127. MODERN.

**The upper floor.**
R32. *"On the Chamber Floor the Plan is continued after the same manner, the Stairs being open
to a Gallery as a Communication to the Apartments."* Morris, Lecture 14. PERIOD.
R33. *"there must be for this reason nothing over the two great rooms."* Ware 1756. PERIOD.
R34. *"The Chambers of the second Story are … a little broader than the lower ones, because of
the diminution of the Walls."* Palladio II, Leoni. PERIOD.
R35. Wet rooms stack on one plumbing wall and bearing walls stack — attributed to *Architectural
Graphic Standards*; passage NOT reached; stated here as practice, not as a standard. MODERN,
attributed.

**Thresholds.**
R36. *"mark it with a change of light, a change of sound, a change of direction, a change of
surface, a change of level … and above all with a change of view."* Alexander 112. MODERN.
R37. *"the visitor's experience upon entering a Georgian house, where one was welcomed by an
unheated central hall, showing only doors."* Deetz on Glassie. MODERN.

---

## III. The diagnosis, itemised

Each finding carries: what the sheet shows; what the type does (Part II gives the sources); which
layer owns it; and its standing in the tree — KNOWN with a citation, PARTLY, or NEW. Severity is
the corpus's own vocabulary where a finding is one the critic already makes, and an architect's
reading where it is not. The tiers run from the decision a builder makes first to the one made
last, because that is the order in which fixing them pays.

### Tier A — the programme and its container

**A1. The programme is not the type's, and the container was never going to hold it.** The
parti `centre-passage-double-pile` names twelve ground spaces (eleven enclosed and a portico)
and eleven upper for a massing whose own description is *"Four rooms per floor around a central
stair hall."* Every exemplar the parti names houses six enclosed spaces on the ground floor where
the count is established, with the service in a basement, a wing or a separate building. Twelve
rooms in a four-room box can only be twelve slivers; no arrangement of them is the type.
*Owner: parti and composer. KNOWN and RULED — `oq/the-parti-dissolved-its-own-dependencies`,
`docs/reports/wp-9.2-the-parti-is-not-the-type.md`; the ruling (strip the service, build the
dependency) is unbuilt.*

**A2. The record describes a five-part house and the solver holds one rectangle, so the record is
infeasible as declared and the proof is of something else.** The porch declares S, E and W
exposure (a projecting thing); the kitchen N, S and W (a free-standing dependency); the back hall
N and S (a hyphen's two long sides); the breakfast room E and S; the library E and S; the drawing
room S and W; the dining room N and W. Three ground rooms claim the west gable and two the
south-east corner. `geometry_cp.py`'s docstring says `exterior_walls` *"speaks EXPOSURE in the
fully-massed house"*; the engine then proves the exposures cannot co-hold in a box and deletes
sixteen of them (I.3). The correct reading of that infeasibility is *the massing is wrong*, and
the engine says so in its own notes — *"the massing likely has a wing the flat footprint cannot
hold"* — twice, about the breakfast room and the library, and then draws the box.
*Owner: massing and placer. PARTLY KNOWN — `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it`
records that `blocks_for` can place a dependency and six layers cannot read
it, and that the composer writes no `block`; that the CP engine's whole downgrade ladder is the
same fact arriving from the other side is NEW.*

**A3. Six bays of 10 ft, under a title that says five, on a massing that says five.** An even bay
count has no centre bay, so a five-bay Georgian's one non-negotiable move — the door in the middle
bay with two windows either side — is unavailable before a single room is placed. The parti
declares `bay_module_ft: 9` and `max_bay_count: 7`; the footprint derivation used its own 10 ft
default because no plan record may name a parti. The sheet prints the six and the five on the
same plate, two lines apart, and nothing compares them.
*Owner: composer (`derive_footprint`) and sheet. PARTLY KNOWN — the 9-never-reached-the-sheet
half is in `oq/the-parti-dissolved-its-own-dependencies`; that an even count has no centre bay,
and that the massing's `bays: "5"` has no reader, is NEW.*

**A4. No wall thickness, so a 60 x 40 house has more clear floor than Gunston Hall's exterior
envelope.** Every rectangle is clear extent; 2,400 sf of room tiles a 2,400 sf footprint. Gunston
Hall is 60'-10" x 40'-11½" OVER two-foot brick walls, about 2,100 to 2,195 sf clear. The plan is
therefore about 10 to 14% larger inside than the house it is sized like, and every "the room does
not fit" result downstream is measured in a house that has no walls to fit between.
*Owner: geometry model. KNOWN — `docs/geometry.md` states it; the Gunston comparison is in
`oq/the-parti-dissolved-its-own-dependencies`. No ruling to add thickness.*

**A5. Area was never the binding constraint, so area is what got satisfied.** The ground
programme's own bands sum to 1,376 to 4,402 sf against a 2,400 sf floor (WP-9.2's own figure);
four bands over two free variables leave a thousand rectangles per room; the placer keeps the
area and lets the shape go. Twenty-three rooms diverge from the record on the screenshot's sheet,
twenty-four on the placement here, and the drawn-layer critic's own words for eleven of them are
*"the placement kept the area and lost the room."*
*Owner: placer. KNOWN — the study's diagnosis, `wp-9.2-what-the-tradition-actually-does.md` §0.*

### Tier B — the axis, the front, the door

**B1. The "centre passage" is in an end bay.** On the screenshot it is the whole west bay, 11 ft
of a 60 ft front, running north–south with the portico as its south end; on the placement here it
is the fifth bay. In neither is it on the axis. The type's passage is central by definition — the
grouping's own description: *"it makes the facade symmetrical because the door is now genuinely
in the middle."* Nothing in the model can see this. `plan_check.py` says so in a comment:
*"There is no axis vocabulary anywhere in this codebase."* The one executable passage rule the
grouping carries — width as a share of the facade, 0.18 to 0.27 — PASSES the screenshot's side
passage at 11/60 = 0.183, because it measures the passage's width and not its place.
`geometry.centre_hall_symmetry_score` charges 1.5 points per same-type room not mirrored about
wherever the passage happens to be, which on a side passage is nothing to mirror.
*Owner: placer and critic. NEW at the centrality half; the off-axis DOOR is checked
(`drawn-entrance-off-axis`).*

**B2. The front door is not in the centre bay, and on the screenshot it is not legible as a door
at all.** The entrance sequence is street, then a 7 x 11 "portico" in the south-west corner of the
block whose south wall carries a window tick, then the passage entered from its corner. On the
placement here the door is 3.5 ft off the passage axis, which the critic does name. In the type the
door is the middle of the composition, and the passage is the door's continuation through the
house; the two are one decision.
*Owner: placer (`entrance_score`, which never ran on the proving engine — see J2) and sheet.
PARTLY KNOWN.*

**B3. The portico is inside the block.** A 7 x 11 room with a window, in the corner of the
rectangle, labelled Entrance Portico; on the placement here it is a 23 x 3 ft strip along the front
that the fault corpus convicts three ways (*"The Porch Nobody Can Sit On"*, *"The Four-Foot
Porch"*, the rocking chair). A portico projects; its three declared exposures say so; the
rectangle cannot honour them. `geometry.entrance_score` charges 100 points for exactly this and
quotes `PLAN-OF-ACTION.md` naming *"the current rendered Tidewater plan puts the portico inside
the footprint"* — and on the proving engine the objective in which that 100 lives was never
evaluated (I.3).
*Owner: massing (a portico is an ELEMENT, not a room) and placer. KNOWN, and the charge that was
meant to cure it is inert on the engine the sheet uses — that link is NEW.*

**B4. The passage does not run through, and where it does it runs through the wrong place.** On
the placement here both end-wall declarations were downgraded; the passage stops 3 ft short of the
front behind the portico strip and neither of its declared windows could be placed. On the
screenshot it reaches the north wall and has a rear door, but its front end is the portico's back
wall. The corpus's own statement is unambiguous — *"Both ends of the passage have doors, and they
are aligned. A passage closed at the back is a corridor and loses the reason the type exists"* —
and carries no `test`.
*Owner: placer and critic. KNOWN as a prose rule, NOT EXECUTABLE — Part VI.*

**B5. Facade symmetry, which the massing calls "a hard constraint, not a preference", has no
reader.** Not in `plan_check`, not in either engine, not in the sheet. The nearest term is the
1.5-point mirror charge in B1.
*Owner: critic. NEW.*

**B6. The front is given to the wrong rooms.** On the screenshot the entrance front is, west to
east, the portico, the library, the breakfast room and the kitchen; the drawing room and dining
room are buried in the middle. On the placement here the kitchen occupies the whole front west bay
and the drawing room is on the rear wall. `principal_and_service_score` prefers principal rooms
forward at 3.5 points a room — soft, and on the proving engine unevaluated.
*Owner: placer. PARTLY KNOWN (the term exists); that the type's front-room hierarchy is nowhere
stated as a rule is NEW.*

### Tier C — the principal rooms

**C1. The drawing room and the dining room have no exterior wall and no window.** The two rooms
the house exists to show are interior rooms: drawing 11 x 34 and dining 9 x 34 on the screenshot,
each with the passage on one side, the other on a second, the back hall on a third, and the stair
hall or the butler's pantry on the fourth. The record declares four windows on the drawing room
(S and W) and three on the dining room (N and W); none could be placed. The drawing-room record
asks for two sides lit and says why — *"South and west, and the reason is the hour."*
*Owner: placer. KNOWN and checked (`drawn-landlocked`, `drawn-window-off-the-placed-wall`);
the fix is upstream of the check.*

**C2. Both are slivers past the double cube.** 34/11 = 3.1 and 34/9 = 3.8 against bands whose
ceilings are 2.0 and 1.8; Morris's *"the Length of no Room exceed a Double Cube"* and Scamozzi's
reason for it — beyond two squares a room becomes *"halls, galleries or passageways rather than
rooms to live in"* — are both in the tree already. A 9 ft dining room cannot take its own table:
the corpus's arithmetic wants 40 + 2 x 54 in = 12.33 ft across, and the room record's own first
sentence is that this room *"is the most rigidly dimensioned room in the house and the one most
often drawn a foot too small."* It is drawn seven feet too small.
*Owner: placer. KNOWN — the sliver table in `wp-9.2-the-parti-is-not-the-type.md`, the drawn
proportion and furniture checks of WP-9.1 and WP-9.6.*

**C3. The rooms have no hierarchy in plan.** In the type the front pair are the entertaining
rooms and the rear pair the private ones (Carter's Grove), and where the pairs differ in size they
differ ACROSS the passage, one side larger than the other (Westover, Wilton, Gunston). Here the largest ground
room is the passage (363 sf), then the drawing room, then the kitchen (310) and the dining room
(306); the library at 247 sf is on the front and the dining room is not. Nothing reads rank
against position except the soft term in B6.
*Owner: composer and placer. NEW as a stated rule.*

**C4. The library takes the front and two front windows; the type puts books on the north.** The
room record says *"NORTH, AND FOR TWO REASONS THAT POINT THE SAME WAY"* and lights the room from
one side. A south library with two front windows is a parlour with shelves, and it has displaced
the drawing room from the front to get there.
*Owner: placer (aspect is nowhere a placement term). NEW.*

### Tier D — the hearth

**D1. There is no fireplace anywhere in the plan.** Not in a room record field, not as a thing
the placer reserves, not as a line on the plate. `grep -i "hearth|fireplace|chimney"` over
`plan_check.py`, `geometry.py`, `geometry_cp.py`, `compose.py`, `openings.py` and
`render_plan.py` finds one comment and one measurement note; `build/arrangement.py` declares the
chimney-breast measurement NOT_DERIVABLE *"because the plan has no chimney footprint."* The massing
this plan declares says `hearth: "gable-end-paired"` and *"Paired end chimneys serve four
fireplaces per floor."* Every principal room in the type has a fireplace and every chamber over it
has one stacked on the same flue. A Tidewater Georgian plan with no hearth is a plan of a house
with no heat, no cooking and no gable composition — the chimneys ARE the gable end of this type.
*Owner: room schema, placer, sheet. NEW at the plan layer; the class ("the massing states its
structure and nothing reads it") is `oq/a-massing-states-its-structure-and-nothing-reads-it`.*

**D2. The gable ends are given to rooms that cannot take the stack.** On the screenshot the whole
west gable is the passage below and the principal chamber above; the east gable is the kitchen
and pantry below and Chamber 3 above. A paired end stack on the west gable would serve a passage.
On the placement here the west gable is the kitchen, full depth. The type's gable-end room is a
parlour or a chamber with its fireplace centred on the gable and a window either side.
*Owner: placer. NEW.*

**D3. The drawing set contradicts itself about the chimneys.** `roof.py` puts the stacks on the
gable ends at the centre line (OQ 85 made the bay under them blind); the elevation draws them;
the plan under them has no fireplace, and the room under each stack on this sheet is a passage or a
kitchen. Two records of one house, and nothing compares them for the hearth as OQ 85 did for the
window.
*Owner: cross-layer (roof, elevation, plan). NEW.*

### Tier E — the stair

**E1. The stair is in a slot along the rear wall, at right angles to the axis, off the end of a
side passage.** The screenshot's stair hall is 7 x 22 ft along the north wall, its single flight
running east–west, entered through a 6 ft opening from the passage's north end. The exemplars
admit two arrangements and this is neither: the stair IN the passage, in its rear half against
one wall (Gunston — *"located in the north end of the center passage, and starts against the east
wall"* — Wythe, Wilton, Mount Vernon, Chase-Lloyd), or a separate stair hall ON THE AXIS behind
the entrance hall through an arch (Carter's Grove, Drayton, Shirley; Hammond-Harwood's is behind
the west parlour). The corpus
knows the first in three places (*"The stair rises in the passage or in a hall opening off it,
never through a room"*; `stair-and-landing-core.attaches_to.four-over-four: "in the passage or a
hall off it"`; the Tidewater style note, *"a breezeway with a stair in it"*) and the parti chose
the separate hall, which the grouping allows at count 0–1. The parti's choice is period; what the
placer did with it is not — nothing says the stair hall must continue the axis, so it went where
a 9 x 14 rectangle happened to fit. Kerr's rule (R10) is the one that bites: *"the access from the
Entrance ought to be equally direct"*, and here the walk from the front door to the first riser is
the whole passage and a right-angle turn.
*Owner: parti (the hall's position is unstated) and placer. PARTLY KNOWN — the WP-9.2 mapping
records the stair "being in a corner is not named by anything".*

**E2. The stair hall is drawn 7 ft wide against a 9 ft record and a 9.5 ft need.** The room
record's dog-leg wants 78 in plus 36 in clearance; the drawn run is a single straight flight of
twenty risers along the rear wall under the stair hall's only window — the window the grouping
calls the house's best is over the treads.
*Owner: placer. KNOWN (drawn furniture check fires).*

**E3. The landing is not over the stair, and the upper plate draws no stair.** The ground stair
is at the north wall; the "Stair Landing" upstairs is a 5 x 19 interior strip over the library's
north edge, with no down-flight drawn. A person climbing the drawn stair arrives in the dressing
room. The record declares `stair`/`landing` as a below/above adjacency and the critic checks
`stacks_over`; the parti carries `landing.stacks_over: stair` and the plan record does not.
*Owner: placer and the parti→plan hand-off. KNOWN for the check; that the parti's stacking claims
did not travel into this record is NEW.*

**E4. The first riser is 27 ft from the front door.** The corpus's Georgian kit sets a ceiling of
12 ft on that setback and the critic enforces only the floor of 6. On the screenshot the walk is
the full passage and a turn.
*Owner: critic. KNOWN — `wp-9.2-the-parti-is-not-the-type.md` names the unenforced ceiling.*

**E5. No back stair.** The service core's rule — *"The back stair is separate from the main stair
and lands in the back hall"* — is unmet, which for a dependency-kitchen house of the period is
right only because the servants' stair is in the dependency; with the kitchen in the block the rule
applies and nothing raises it.
*Owner: parti. NEW (minor, follows from A1).*

### Tier F — the upper floor

**F1. The upper floor is a second, unrelated plan.** On the placement here thirty upper wall
lines land on no wall below; every one is a transfer beam in a house whose type has *"the second
floor plan … identical to that of the first"* (Hammond-Harwood) and whose treatise says *"On the
Chamber Floor the Plan is continued after the same manner"* (R32). Both engines charge vertical
discontinuity at 2 points an edge and broken stacks at 40; neither term ran on the proving engine
(J2). The screenshot prints no count for this at all.
*Owner: placer and sheet. KNOWN as a class (`vertical_score`, WP-7.4); that the sheet does not
disclose the transfer count is NEW.*

**F2. The upper passage runs along the entrance front.** 9 x 43 ft on the screenshot, taking the
whole south elevation; it is not over the lower passage, it is at right angles to it. The
chambers open off a corridor whose windows are the facade's second storey, so the front of the
house upstairs is a hallway. On the placement here it is a 31 x 20 ft interior blob of 620 sf with
no window at all, +72% on its record. The parti declares `upperpassage.stacks_over: passage` and
`landing.stacks_over: stair`; **the plan record carries neither**, so the critic — which checks
`stacks_over` faithfully — has nothing to check. Three of the parti's five stacking claims travelled
into this record, the record added one of its own (powder over the cellar stair), and the two
that organise the floor — passage over passage, landing over stair — did not.
*Owner: the parti→plan hand-off, then placer. NEW.*

**F3. The chambers are galleries.** Principal Chamber 10 x 40 (4.0) the full depth of the west
bay, with a window on three of its four walls; Chamber 2 13 x 31 (2.4); Chamber 3 12'-1" x 31 (2.6). Ware's category
for a room four to eight times its breadth is *gallery* (R17). The primary-bedroom record says
a king bed with its two 30 in aisles wants 140 in; a 10 ft room has 120. The bedroom record's
own diagnosis of a 16 ft deep single-window room — *"the far third of the room is where the bed
goes, in the dark"* — is here a 40 ft one.
*Owner: placer. KNOWN as a class (WP-9.6's drawn furniture check, the sliver table).*

**F4. The shared bath is a 5'-2" x 31' corridor between two chambers.** 159 sf against an 88 sf
record (+81%, the sheet's own "worst"), its three fixtures strung down a slot, entered from the
front passage; over the powder room by declaration and *"drawn clear of it entirely"* by
placement. The bathroom record's whole argument is that the 5 x 8 rectangle is *"the tightest
arrangement in which three fixtures each get their code clearance off a single 8 ft wet wall"*;
a 31 ft wet wall is not a bathroom that grew, it is a passage with plumbing.
*Owner: placer. KNOWN (drawn band and stack checks).*

**F5. The closets take front bays and carry front windows.** The south-east corner closet on the
screenshot has a window on the entrance front; the north-wall closet and the unlabelled space
beside it each have a north window. The walk-in-closet record: *"In a symmetrical style, a walk-in
gets its daylight from a borrowed light or a transom over its door, never from the front
elevation."* A closet on the facade is a bay of the composition spent on a cupboard. On the
placement here `cl3` is drawn 2 x 19 ft (9.5 to 1).
*Owner: placer. PARTLY KNOWN (the 2 ft closet is in the sliver table); the front-bay half is NEW.*

**F6. The two baths sit over no wet room.** Principal Bath declares `stacks_over: butlers`,
Chamber Bath `stacks_over: powder`, and both are *"drawn clear of it entirely"* on both
placements; the solver's own note is *"its stack has nowhere to land."* R35 is practice rather than
a standard and it is universal practice.
*Owner: placer. KNOWN and checked.*

**F7. The principal suite consumes a gable bay full-depth.** The primary-bedroom record predicts
it exactly: *"bedroom plus bath plus closet is 30 to 40 ft of plan depth … In a double-pile block it
does not fit without a wing, and drawing it into a four-over-four is the commonest reason a
traditional plan comes out 46 ft deep."* Here it did not deepen the house; it took the whole west
bay instead, which is the same admission in the other axis. The suite is a wing's programme
written as three block rooms — A2 again, upstairs.
*Owner: parti. PARTLY KNOWN (the room record says it; nothing acts on it).*

### Tier G — fenestration and the facade

**G1. Most of the declared windows are not on the sheet, and the sheet does not say so.** The
record declares 35 window units. On the placement here 27 are unplaced — 24 because *"the
placement puts this room on no such boundary wall"*, 3 because *"the wall has no clear run left
beside its doors"*. On the screenshot about fifteen ticks are drawn, so about twenty are missing.
`openings.py` counts `windows_unplaced` and nothing reads the count; the sheet's banner stack
prints cuts, undrawable doors, resized rooms and the engine, and not one word about windows. A
plate showing a Georgian front with the wrong number of windows on it is the WP-6.1 failure — the
sheet lying about the record — in the one element the type is recognised by.
*Owner: sheet (`render_plan.py`), workbench. NEW.*

**G2. Nothing aligns storey over storey, and the massing's own constraint on it has no reader.**
`massings/catalog.json`: *"Window bays must align vertically; a misaligned upper window is a
structural admission that the plan is not really Georgian."* Not read by `plan_check`, either
engine, `openings.py` or the sheet. Windows are placed per room after the rooms are placed, so
alignment could only be an accident. Wythe's *"five windows in alignment with the bottom
windows"* and R4 are the rule; here the front has five openings below and three above and none
over another.
*Owner: openings (a facade is not derived from rooms one at a time) and critic. NEW.*

**G3. A window where the door should be.** The portico's south wall on the screenshot carries a
window tick; the front door — the porch's declared `{to: exterior}` — is not legible as a swing.
On the placement here the door is drawn, 3.5 ft off the passage axis, in a 3 ft deep strip. R2
and R3: the door *"exactly"* in the centre, with a flight of steps *"so broad as to occupy the
whole centre of the front."*
*Owner: placer and sheet. PARTLY KNOWN (the off-axis check).*

**G4. The kitchen is on the entrance front.** On the screenshot the kitchen's south wall is the
facade and carries a front window; on the placement here the kitchen is the whole front west bay.
The kitchen record wants east for the morning and *"avoids a west aspect"*; the service core
wants it *"kept out of sight and often out of the main block entirely"*; the Tidewater note says
*"Kitchen detached in the yard."* The soft term that prefers service to the rear
(`principal_and_service_score`, 2.0 a room) is the only thing that speaks to it and it did not run.
*Owner: parti (A1) then placer. PARTLY KNOWN.*

**G5. The gable ends are not composed.** The type's gable carries the paired stacks with windows
between them (*"three windows in their gables"*, Gunston; *"two windows on each floor"*,
Carter's Grove). Here the west gable is a passage below and a 40 ft chamber above with one window
each; the east is a kitchen and a chamber. There is no stack for the windows to flank because
there is no hearth (D1), and `roof.py` will nevertheless draw one at the gable's centre line.
*Owner: cross-layer. NEW.*

### Tier H — the service side

**H1. The kitchen "(Dependency)" and the back hall "(Hyphen)" are inside the block, and their
labels say otherwise.** The names are the type's; the rectangles are a 10 x 31 slot and a 5 x 27
slot in the main block. A reader who trusts the label is told there is a dependency; a builder
who trusts the linework builds a kitchen in the parlour range. Every exemplar reached has the
kitchen out of the house, and the UVA thesis gives *"at least 20 feet"* as the distance.
*Owner: parti. KNOWN and RULED (2 Sep); unbuilt.*

**H2. The powder room opens off the formal side.** On the screenshot the WC is on the north wall
between the stair hall and the cellar stair, entered from an unlabelled space beside the stair
hall; the record puts it off the back hall. The critic's adjacency layer complains only that it
does not reach an entrance hall, which is backwards.
*Owner: placer (declared door adjacency was kept, room position was not). NEW, minor.*

**H3. The butler's pantry is a 4 ft strip and the breakfast room a 9 x 20 front room.** The
butler's pantry record wants 9.1 ft across to *"stage a whole course"*; the breakfast room record
wants east light and a 9 ft table across; both are drawn as the leftover between larger rooms.
*Owner: placer. KNOWN (drawn furniture checks).*

**H4. The terrace is never placed and its door is the sheet's one undrawable opening.** Correct
behaviour for a terrace under OQ 55, stated on the sheet; noted here because it is the one element
of the outside the record even tries to state, and it is the only one the sheet is honest about.
*Owner: —. KNOWN.*

**H5. The cellar stair is a 4 to 5 ft slot on the north wall between kitchen and pantry, with no
cellar in the record.** Fine for the type (the cellar is under the house); not a finding against
the placer, but the plan has no level below ground and the stair goes to one.
*Owner: record. NEW, minor.*

### Tier I — circulation and thresholds

**I1. The entry sequence is a windowed room in the corner of the block.** Street, then a 7 x 11
"portico" inside the rectangle with a window in its front wall, then the passage entered from
that room's end. The entry-sequence grouping asks for two thresholds each changing a condition —
*"level, enclosure, light, or direction"* — and R36 the same; the type's are a flight of steps, a
projecting portico or a stoop, then the front door on axis into a passage that shows *"only
doors"* (R37). Here the first threshold is a room and the second a corner.
*Owner: massing (portico as element) and placer. PARTLY KNOWN.*

**I2. Two areas of floor belong to no room.** On the screenshot, between the stair hall and the
powder room on the ground floor (≈ 6 x 7 ft) and west of the north-wall closet upstairs
(≈ 9 x 4 ft), there are outlined spaces in the paper colour with no name — and the upper one has
a window tick on its north wall. Either they are rooms the label fitter could not name or they
are floor the tiling left over; the plate does not say which, and a proving engine whose hard
set includes *"coverage"* should have produced neither. A window in a space nobody owns is a
window on the facade that lights nothing.
*Owner: placer and sheet. NEW; not reproduced here (the placement here tiles fully), so
attributed to the bench's input and left as a question.*

**I3. Every chamber door opens off the front corridor.** The parti's upper passage has four
doors; the drawn one has six, plus the linen press, all along a 43 ft run against the facade. The
secondary-bedroom rule *"No bedroom is entered through another"* holds; the privacy gradient (R31)
does not, since the most private floor's corridor is the most public elevation.
*Owner: placer. NEW.*

**I4. The dinner route is right and the withdrawing route is a corridor.** Dining → butler's
pantry → kitchen exists and crosses no formal room, which is the service core's one hard rule
satisfied. But the drawing room and dining room, being interior slivers side by side, make the
enfilade's *"withdraw"* a step from one 34 ft corridor into the next; R29's centred communicating
door is there in the record (5 ft double) and the rooms it joins are not rooms.
*Owner: placer. PARTLY KNOWN.*

### Tier J — the sheet and the engines as instruments

**J1. "PLACEMENT PROVED (CP-SAT) AGAINST THE RECORD'S DECLARED FACTS" is printed over a placement
that set aside sixteen declared facts.** Section I.3 lists them. The line is true of the hard
constraints that survived and false of the passage's two end walls, the drawing room's two window
walls, the dining room's two, the principal chamber's two and the upper passage's front. The
solver records every downgrade in `geometry_report.solver.downgraded_wall_pins` and in a
`refinements` sentence apiece; the sheet reads `solver.engine` and nothing else. WP-6.4 made the
plate say which engine ran; it did not make it say what the engine gave up.
*Owner: sheet. NEW.*

**J2. The compositional objective never ran, and the sheet shows the first feasible placement as
if it were the best.** `status: "OPTIMAL (hard-only) — kept hard-only phase A (best of 1
hard-valid placements)"`, `objective: null`, `polish-h: UNKNOWN`. Phase A proves feasibility of
the hard set; phase B, which carries every compositional term the corpus has — the 100-point
portico-inside charge, the 40-point stack, the front-for-principal-rooms preference, the mirror
pairing, the span capacity — timed out in the 55% share of the remaining budget it is given, inside a
26 s solve. So on the engine the
bench uses by default, the house is whatever CP-SAT reached first. The heuristic, which runs all
of those terms, scores 712.6 against the proof's 835.0 on the corpus's own demerit total and is
the better house in every tier above; the bench draws the proof because a proof is not a search
(WP-6.3), which is the right principle applied to the wrong quantity. **A proof of feasibility
against a relaxed hard set carries no compositional information at all.**
*Owner: bench (`corpus._placed`) and `geometry_cp.py`. NEW; OQ 71 records the budget-edge
fallback, not this.*

**J3. The sheet is silent on the twenty-odd windows it does not draw.** G1. *NEW.*

**J4. The sheet's style slot read `palladian`.** The record declares `tidewater-georgian`; the
plate Lucas read carries `palladian`, a different style node, in the position `render_plan.py`
prints the style — which is what the bench's `StylePicker` writes to `plan.style`. Every fault
and kit check on that sheet was made against the wrong node. Not a defect of the engine; a defect
of a plate that does not say when its title and its style disagree.
*Owner: bench. NEW, input observation.*

**J5. The plate prints only the drawn size.** "Dining Room 9' x 34' · 306 sf ∗" is honest about
the drawing and silent about the record's 16 x 20; the ∗ is the only trace of the asking. A reader
cannot see, on the plate, what was asked for and refused, and so cannot tell a room the placer
ruined from a room the author drew small.
*Owner: sheet. PARTLY KNOWN (the ∗ is WP-6.1's).*

**J6. The bench's proof and this CLI's proof are different houses, and on this machine the proof
is stable.** Two CP-SAT runs here agree to the foot on all 25 rooms; OQ 44's *"reproducible by
default"* holds. The screenshot differs because its input did — the style, a parti, or an edited
record — and the plate carries nothing that would let a reader tell which.
*Owner: bench. NEW as a disclosure gap; NOT a solver defect.*

**J7. The critic already says a great deal of this and none of it reaches the sheet.** On the
placement here `plan_check` raises 73 serious and 80 minor findings, 57 of them in the drawn
layer (42 serious): landlocked rooms, slivers, furniture that does not fit, stacks with nothing under them,
the off-axis door. The plate carries four banner lines and the ∗. The reader of the sheet is the
one person the critic is not talking to.
*Owner: workbench. PARTLY KNOWN (WP-9.3 put the critique on the bench beside the sheet, not on
it).*

---

## IV. Who owns what

The same fifty-one findings sorted by the layer that would have to change. A finding that appears
under two layers is one whose fix in the lower layer is unreachable until the upper one moves.

| Layer | Findings | What it would have to learn |
|---|---|---|
| **Massing / parti** (`massings/catalog.json`, `partis/centre-passage-double-pile.json`) | A1, A2, A3, B3, E1, E5, F7, G4, H1, I1 | That a five-part house is five elements, each with its own rooms; that a portico, a hyphen, a dependency and a terrace are ELEMENTS with a position relative to the block and not rooms with three exposures; that the bay count is odd and the module is the parti's; where the stair hall is (on the axis) and not only that there is one |
| **Composer** (`build/compose.py`, `derive_footprint`) | A3, A5, C3, F2 | To carry the parti's `bay_module_ft` and every `stacks_over` into the record; to size from the type's commitments (Part V) rather than from area |
| **Placer** (`build/geometry.py`, `build/geometry_cp.py`) | B1, B2, B4, B6, C1, C2, C4, D2, E2, E3, F1, F3, F4, F5, F6, G3, G4, H2, H3, I2, I3, I4 | An axis; the front as a fact and not a 3.5-point preference; hard stacking on this parti; the square as the direction (the 3 Sep ruling) and not only a ceiling; the hearth as a reserved thing; that the objective must run or the sheet must say it did not |
| **Openings / facade** (`build/openings.py`) | G1, G2, G5 | That a facade is composed and windows derived from it, not the reverse; vertical alignment; the blind bay under the stack, in the plan too |
| **Room and plan schema** | D1, D3, H5 | A hearth (wall, width, flue) on a room; a level below ground |
| **Critic** (`build/plan_check.py`) | B1, B4, B5, C3, E4, G2 | Passage centrality, the door's bay index, an odd bay count for a centre-door type, facade symmetry, the stair setback ceiling, window alignment — every one a rule the corpus already states in prose (Part VI) |
| **Sheet** (`build/render_plan.py`) | F1, G1, J1, J2, J3, J5, J7 | The downgrade count and the objective status beside the engine line; the unplaced-window count; the record's figure beside the drawn one; the transfer count |
| **Bench** (`workbench/server/corpus.py`, `PlanWorkbench.jsx`) | J2, J4, J6 | Not to prefer a proof that carries no composition over a search that does, or to say so on the plate; to disclose a style that disagrees with the title |

The distribution is the diagnosis in one table: **twenty-two placer findings are downstream of ten
massing-and-parti findings**, and the six critic findings are all prose the corpus wrote and
never made executable. Fixing the placer first would move slivers around inside the wrong box.

---

## V. The root causes, from first principles

The tradition's sequence of commitments, as `wp-9.2-what-the-tradition-actually-does.md` §1
reconstructed it from Glassie, Ware, Palladio-and-Scamozzi and Kerr, is: establishment →
storey height → breadth, from span, hearth and daylight → pile → hall and stair → length of each
room from its own arithmetic → doors → **facade as a result** → bands as the test. The generator
that drew this sheet runs the list backwards and skips half of it. Read against that order:

**1. The container is decided before the programme, and decided wrong.** `derive_footprint` sets
the area from the rooms' declared areas and the width from a default bay of 10 ft, then hands one
rectangle to a solver. The parti had already said its module is 9 ft and its growth is
*"widening, adding-bays, adding-a-link"*; the massing had said *"Flanking dependencies connected
by hyphens … or a rear service ell. Growth must respect the axis or the whole logic fails."* Both
were readable and both were read by nothing that places. The programme is a five-part house; the
container is a box; the solver proves the box cannot hold the programme and then holds it anyway
by discarding what does not fit. Every sliver, every windowless principal room and every kitchen
on the facade follows from this one inversion. *(Findings A1–A3, B3, C1, G4, H1, I1.)*

**2. Area is conserved and nothing else is.** Four bands over two free variables leave the shape
free; the exact-tiling slicer conserves area to the tenth of a square foot; so area is what the
placement satisfies. The 3 Sep ruling — every proportion floor to 1.0, the square as the
preferred direction — is the first move against this, and it is a critic's move: `WIDTH_W` still
ships at 0.0 and the search still charges a flat 12 for an under-band room and wins while paying
it. The tradition never chose two numbers at once; it chose a breadth from the span and the hearth
and let the length follow. *(A5, C2, F3, F4, F5.)*

**3. There is no axis.** Not as a term, not as a check, not as a word. The type's whole logic is
*"Symmetry is not applied to this plan; it is generated by it"* — the massing's own sentence —
and the model has no object that could generate it: no centre line, no bay index for a door, no
notion that a passage is the door continued. `centre_hall_symmetry_score` measures mirroring
about wherever the passage landed, at 1.5 points a room, which is the cost of a bad
window-wall choice, not of losing the type. *(B1, B2, B4, B5, G2, G3.)*

**4. The front is a preference.** `principal_and_service_score` at 3.5 and 2.0 points a room,
`exterior_score` at 14 a wall, `entrance_score` at 100 for the portico — soft terms in a demerit
total, and on the proving engine not evaluated at all. In the tradition the front is a FACT that
precedes the rooms: it is the thing the door is centred on, the elevation the best rooms take,
the face the kitchen never shows. *(B6, C3, C4, G4, J2.)*

**5. There is no hearth.** The plan layer has no fireplace, no chimney breast, no flue; the roof
and elevation layers have stacks and put them on the gables with a blind bay under each. A
Georgian room is composed around its fireplace — Kerr's five rules for door, window and fire (R24)
are rules of ROOM composition, and the massing's *"four fireplaces per floor"* is a rule of PLAN
composition: which wall each room's hearth is on decides which wall its windows are on, which
decides where the room can stand. Without a hearth the placer has lost the type's second strongest
constraint after the axis, and the elevation is drawing chimneys over a house that has none.
*(D1, D2, D3, G5.)*

**6. Stacking is a charge, not a rule, and half the claims never reached the record.** The parti
says passage over passage and landing over stair; the record does not; the placer charges 40 for a
broken stack it can see and nothing for one it cannot; the proving engine's charge did not run.
The type stacks by construction — Morris's *"the Plan is continued after the same manner"* — and
on masonry walls two feet thick it could not do otherwise. *(E3, F1, F2, F6.)*

**7. The facade is derived from the rooms instead of the rooms from the facade.** Windows are
placed per room, on whatever boundary wall the room reached, after placement; the front therefore
has whatever number of openings the rooms that happened to reach it declared. Wenger's finding
that *"advanced, raised, or pedimented central bays gained popularity in Virginia only after the
central passage had achieved status"* is the historical form of the same dependency: the facade
follows the plan's organising move, and the plan's organising move is the centred passage, so the
facade follows the passage — not the rooms. *(G1, G2, G3, G5, J3.)*

**8. The instrument reports a proof of the wrong proposition.** "Proved against the declared
facts" over sixteen discarded facts and a null objective is not a lie the solver told; it is a
true sentence about a different question, printed where a reader will take it for the answer to
this one. The corpus's own rule — *unjudged is not passed* — has a corollary this sheet needs:
**relaxed is not proved.** *(J1, J2, J3, J5, J6, J7.)*

---

## VI. What the corpus already says and cannot execute

Every rule below is in the tree today, in prose, with no `test`, and this sheet breaks it. This is
the cheapest list in the document: none of it needs a source, because the source is already cited
on the record it lives in.

| Where | Statement | Broken on the sheet by |
|---|---|---|
| `massings/catalog.json` four-over-four | *"Facade symmetry is a hard constraint, not a preference."* | B1, B2, G2 |
| same | *"Window bays must align vertically; a misaligned upper window is a structural admission that the plan is not really Georgian."* | G2 |
| same | *"Paired end chimneys serve four fireplaces per floor."* | D1 |
| same | `bays: "5"` | A3 |
| `groupings/centre-passage-core.json` | *"Both ends of the passage have doors, and they are aligned. A passage closed at the back is a corridor and loses the reason the type exists."* | B4 |
| same | *"Flanking rooms are equal or near-equal, and their windows align vertically with those above."* | C3, G2 |
| same | *"The stair rises in the passage or in a hall opening off it, never through a room."* | E1 (met in letter, not in position) |
| same, description | *"it makes the facade symmetrical because the door is now genuinely in the middle."* | B1, B2 |
| `groupings/entry-sequence.json` | *"Each step changes at least one condition: level, enclosure, light, or direction."* | I1 |
| `groupings/stair-and-landing-core.json` | *"A window on the half-pace or at the head. A stair lit only from the floors it connects is a shaft."* | E2 |
| `groupings/georgian-service-core.json` | *"Ridge and eave of a service wing sit below the main block"*, and the Tidewater note *"Kitchen detached in the yard"* | H1 |
| `groupings/public-enfilade.json` | *"Rooms diminish or grow in one direction, never alternate."* | C3 |
| `rooms/drawing-room.json` | *"South and west, and the reason is the hour."* | C1, B6 |
| `rooms/library.json` | *"NORTH, AND FOR TWO REASONS THAT POINT THE SAME WAY."* | C4 |
| `rooms/kitchen.json` | *"EAST for the morning … avoids a west aspect"* | G4 |
| `rooms/walk-in-closet.json` | *"never from the front elevation"* | F5 |
| `rooms/primary-bedroom.json` | *"In a double-pile block it does not fit without a wing"* | F7 |
| `rooms/centre-passage.json` (Tidewater) | *"12 to 14 ft wide, furnished … a rear door to the garden as important as the front door to the road."* | B1, B4 |
| `kits/georgian-colonial-american.kit.json` | stair setback ceiling of 12 ft | E4 |
| `partis/centre-passage-double-pile.json` | `bay_module_ft: 9`; `upperpassage.stacks_over: passage`; `landing.stacks_over: stair` | A3, F2 |

Twenty statements, none executable, every one contradicted by a sheet that passes every
executable check on its own passage width. That ratio — twenty prose rules to one executed —
is the measure of how far the plan layer's grammar lags its vocabulary.

---

## VII. The order of work

Stated as a sequence because the findings are nested, and because the study's §6 and WP-9.4's
refusals bound what may be built without a ruling. Nothing here proposes a score term: WP-9.4
swept the terms and moved nothing, and Part IV shows why — twenty-two placer findings sit under
ten that are not the placer's.

**1. Build the container the programme describes** — the ruled and unbuilt half of
`oq/the-parti-dissolved-its-own-dependencies` and the four rulings
`oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` still needs. The parti
states which of its rooms live in which element (main block, hyphen, dependency, portico,
terrace); `blocks_for` places the elements; the block solves four rooms and a passage a floor.
Until this is done every other item below is applied to the wrong box. *Needs: the four rulings
in that entry; then the parti record gains a `block` per room.*

**2. Give the model an axis, and make the odd bay count and the centred door hard for this
parti.** An entrance bay index, a passage centre line, and a mirror about it; the parti's
`bay_module_ft` and an odd `max_bay_count` carried into `derive_footprint`; passage centrality
and door-in-the-centre-bay as hard constraints in both engines for `circulation_parti:
center-hall`, with the period's tolerance — Westover's and Wilton's *"slightly off-center"*
passage and unequal flanking pairs — stated as an allowed asymmetry of ROOM size about a centred
door, not of the passage. *Needs no new source; the massing calls symmetry hard already. Needs
one ruling: whether "slightly off-center" is a number, and whose.*

**3. Put the hearth in the plan.** A `hearth` on a room record (which wall, opening width per
Morris's table R25 as an editorial start, flue id); the massing's `hearth: gable-end-paired`
read as a placement rule (each gable-end room's hearth on the gable, chambers stacked over);
the placer reserving the breast; the sheet drawing it; `roof.py`'s stacks derived from the plan's
flues rather than from the gable's centre line, closing D3 the way OQ 85 closed the window. *Needs
a ruling on the field and its schema; the Morris table is PERIOD and quotable but is a London
figure and must carry `judgment: true` on an American record (§6 item 6).*

**4. Make stacking a rule on this parti and carry the parti's claims into the record.** Passage
over passage, landing over stair, wall over wall, wet over wet — hard in the CP model for
`four-over-four`, and the composer copies every `stacks_over` the parti states. *Needs no ruling;
the massing's `structural_logic` and OQ 40's mechanism already exist.*

**5. Derive the facade before the windows.** For a centre-door type: the bay rhythm from the bay
count and module, the door in the centre bay, one window per bay per storey aligned, the blind
bay under each stack — and then each room's windows are the bays its front wall spans. This is
Q2 of the study's questions for Lucas (*"Do you accept that the facade is a result?"*) and it
inverts `centre-passage-core`'s facade-share test. *Needs Lucas's answer to Q2 and Q5 (pipeline
or constraint system).*

**6. Make the sheet say what the solver gave up.** Beside the engine line: the number of
declared exterior walls set aside and the rooms they belong to; whether the objective ran
(`objective: null` → "FIRST FEASIBLE PLACEMENT, NOT OPTIMISED"); the count of declared windows not
drawn; the transfer-beam count; and on each ∗ room the record's figure beside the drawn one.
*Needs no ruling. This is the WP-6.1 and WP-6.4 discipline applied to three more fields the
solver already writes.*

**7. Let the bench choose the better house, or say which it chose and why.** When phase B does
not run, the "proof" carries no composition; the search does. Draw the search with its label, or
draw both, or extend the budget until the polish returns — but do not draw phase A as the sheet
without saying it is phase A. *Needs a ruling: WP-6.3's principle (a proof outranks a search) was
about feasibility, and this is about composition; Lucas should say whether it transfers.*

**8. Execute the prose in Part VI.** Six critic findings (B1, B4, B5, C3, E4, G2) and the
massing's two constraints, each a `test` on a rule that already has a `statement` — the rule
that prose stays beside the test, applied. *Needs no ruling for any of them except the number in
item 2.*

**9. Only then, the placer's shape terms** — `WIDTH_W`, the flat 12, the direction-to-the-square
the 3 Sep ruling opened — measured on the right box.

**What not to do, and why.** No score term for the axis (item 2 says hard, and WP-9.4 measured
that a term is inert until phase B runs anyway). No Kerr dimension imported into a Chesapeake
record (§6 item 6). No daylight cap made generative (§6 item 5). No band conditioned on register
before `oq/register-is-not-style`'s four consequences are ruled. No "fix" of the sixteen
downgrades by loosening the exposure declarations on the rooms: they are correct declarations of
a five-part house and the box is what is wrong.

---

## VIII. What this diagnosis could not establish

- **The screenshot's own solver record.** The bench does not expose `geometry_report.solver` on
  the plate, so the downgrade list and objective status for the placement Lucas read are
  inferred from the placement here, which shares its defect classes and not its arrangement.
- **Why the two placements differ.** The style slot (`palladian`), a parti on the drawing route,
  or an edited record; any of the three would do it and the plate names none of them.
- **The two unlabelled spaces (I2).** Not reproduced here; either rooms the fitter could not
  label or floor the tiling left.
- **Passage widths as a distribution.** Mount Vernon's 13'3" is the one museum figure; Gunston's
  "12 ft" is a newspaper's; the study's fifteen figures are enough to refute a gap and not to
  publish a band.
- **Room-by-room dimensions for any brick exemplar.** HABS written data gives envelopes; the room
  figures are on the measured drawings, which are raster, and were not read.
- **Wenger 1986, Upton 1982, Glassie 1975, Lounsbury's *Glossary*, Palladio I.xxiii/xxvii/xxviii,
  Ware on the chimney's position, Loudon, Halfpenny, Langley, the *Graphic Standards* stacking
  rule.** Reached via citing works or not at all; every rule above that rests on one says "via" or
  "attributed". Nothing here should be promoted from `editorial` on the strength of this document.
- **Whether the workbench's "coverage" hard constraint admits unowned floor.** The engine's hard
  set names coverage; the screenshot appears to show two gaps; not reconciled.
