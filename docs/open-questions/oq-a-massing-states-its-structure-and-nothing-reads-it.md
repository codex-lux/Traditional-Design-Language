# oq/a-massing-states-its-structure-and-nothing-reads-it — the stair hall is supposed to be the spine wall, and the search does not know it has a job

*Status: OPEN · Raised in: WP-9.2, the precedents measured (1 Sep 2026)*

**`structural_logic` has zero readers across the whole tree.** Grep it: `build/`, `mcp_server/`,
`workbench/` — nothing. And for `four-over-four`, the massing `plans/tidewater-georgian-careful.json`
itself declares, it says something the placement contradicts on every seed:

> `structural_logic`: **"Two rooms deep requires an interior bearing wall, which the stair hall
> supplies. Paired end chimneys serve four fireplaces per floor."**

The placement puts the stair in a 10 × 13 room at (50, 27) — the far corner — supplying a wall to
nothing. That is Lucas's sixth complaint, *"the stairs are shoved off into the corner"*, and it is
not a matter of taste: in this massing the stair hall is the spine of the house.

**The exemplars agree with the record, in the survey's own words.**

> Gunston Hall (HABS VA-141): *"Gunston Hall has solid brick walls including **all but one
> interior bearing wall**, which is a stud framed wall."*

> Drayton Hall (HABS SC-377): *"In addition to the exterior bearing walls there are **two interior
> brick bearing walls** parallel to the northwest and southeast walls."* And, of the service
> stair: it *"occupies the space between the chimney and **the brick bearing wall between this
> room and the Great Hall**."*

In both, the principal interior partitions ARE the structure — masonry, continuous, and few. A
room is a compartment between two bearing lines. **You cannot make a 10 × 30 sliver in such a
house, because the lines that would bound it do not exist.** The corpus's guillotine slicer can
cut anywhere at any depth of recursion, and the bay module only nudges: `geometry.snap` returns
the raw value unless the nearest bay line is within `tol = bay * 0.28` (`geometry.py:1113`), and
the file's own docstring claims a measured consequence — *"18 of 30 ground wall lines on the
shipped plans are themselves off the bay grid."* **DO NOT QUOTE THAT FIGURE: it is stale and does
not reproduce under any reading.** Re-derived from `bearing_lines()` on the shipped plans, the
current figures are 35 of 45 interior segments, or 19 of 23 distinct interior lines. It is a
source-comment number, and `check_counts.py` polices documentation rather than source comments, so
nothing was going to catch it. The point the docstring is making survives — most wall lines are
off the grid — and the number attached to it does not.

**This is also the unread half of the span problem.** WP-7.4 found a 49.93 ft clear span between
the three real bearing lines of the Tidewater plan against a 20 ft capacity, and OQ 98 records
that `span_check` still credits a bearing wall across the whole plate however short it is. Real
double-pile houses do not span 50 ft **because they have a masonry spine**. The corpus's plans
have no spine because nothing ever asked for one. Drayton Hall's two interior bearing walls divide
a 52'-2" depth into three bands of roughly 17 ft — under the capacity, by construction, because
that is what the walls are for.

**The question is what a structural statement should be allowed to do.** Four positions:

1. **Nothing — delete the field or mark it prose.** Defensible only if we accept that
   `structural_logic` is documentation. It is currently indistinguishable from a rule, which is
   worse than either.
2. **A CHARGE in `level_score`** — a placement whose stair hall does not run the full depth of the
   block pays. Cheap, sweepable, and it composes with the existing terms. WP-7.4's discipline
   applies in full: clear `_SOLVE_CACHE` between settings, sweep zero and both extremes, check the
   interaction with `STACK_W`/`SPAN_W`.
3. **A STATED structure**, on the `courtyard_slice()` precedent (OQ 55): where a massing's
   `circulation` names a stair-hall spine, the macro tree states the spine slab rather than
   searching for it. Strongest, and it is what the corpus's own words describe; but WP-9.4 refused
   a stated macro-tree on measured grounds and those grounds have to be answered, not ignored.
4. **A hard constraint in `geometry_cp.py`.** Refused in advance: WP-6.3 established that only
   wall literals are downgradable, and a pin here would make an unsatisfiable model out of any
   brief whose stair hall cannot span.

**What has to be settled before any of them.** `structural_logic` is a free-text field on 40
massings. It cannot be executed as written — *"the stair hall supplies the interior bearing wall"*
is prose, not a test. Either it gains a typed companion (a `spine` role naming which room carries
the bearing line, on the massing or the parti), or a reader parses the prose — and this project
does not parse prose. **The typed field is the answer if the answer is 2, 3 or 4**, and authoring
it is a schema change with a basis, in the shape OQ 15 ruled.

**Ratchet first, whatever is decided.** The measurable quantity today is: for each parti/massing
whose `structural_logic` names a spine room, does the placement give that room a full-depth or
full-width extent? That is a meter that can be published and pinned before anything is fixed, and
it is the honest way to find out how big the problem is on all 21 partis rather than on the two
plans that ship.
