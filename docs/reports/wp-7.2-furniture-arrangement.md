# WP-7.2 — the door was drawn through the vanity, and the schema had a field nobody filled

*27 August 2026. Phase 7, package 2 of 3.*

## The ruling first, because it decides the shape

Lucas, verbatim: *"room sizing should not be furniture driven — that's the tail wagging the
dog — however furniture arrangements that suit the program / room name and room size should be
placed accordingly."*

So OQ 92's sizing half is **refused**, not deferred, and it is written into `docs/model.md`.
The room catalogue's 22 `critical_dimension` arithmetics — *"40 + 2(36) + 2(18) = 148 in, so
12 ft 4 in is the absolute floor"* — stay prose. They are a designer's argument for where a
band's floor sits, addressed to a person; making one a constraint would let a derived number
overrule an authored one, which is the OQ 52 class. Authority runs one way: a room's size comes
from its programme and its band, and the furniture is arranged into the room as given.

## What the measurement found before anything was built

The dataset splits in two, and the register overstated one half:

- **Arrangement has complete data.** All **278 furniture items carry a real `footprint_in` and
  `clearance_in`**, across 59 of 60 rooms.
- **Anything keyed on `essential` would have been inert.** Only **4 items in 3 rooms** are
  marked essential — 57 of 60 rooms carry none.
- **`schema/room.schema.json` declared a `placement` field that 0 of 278 items carried.**
  `plan_check` therefore inferred it from the item's *name* with a regex
  (`counter|bench|sideboard|…`), which called **84** items against-wall where the authored data
  calls **159**. A guess in code where the schema has a field.

## What was built

### 1. The door placer and the fixture placer can see each other

`openings.place`'s docstring said fixtures ran first *"because a door has to know what is
against the wall it would swing into"* — and `_place_interior`'s `occupied` map never held a
fixture. **The code did not do the thing its own comment gave as the reason.** Measured on the
CP placements: the principal bath's double vanity was drawn with a door through it (2.70 ft of
overlap) and the powder room's basin likewise (1.92 ft), on `spec-builder-colonial`.

The **order was inverted** rather than the map patched, because the precedence is what matters:
a door is **authored** in the plan record, a fixture layout is **derived** here, and an
authored fact must never lose silently to an inferred one. Openings take their runs first; a
fixture that cannot clear them is reported `unplaced` with a reason — the same three-state
treatment every opening gets.

### 2. A fixture is tried on every wall, not only the longest

Packing against the longest wall regardless of what was already on it reported the powder
room's water closet and basin as unfittable — its 11 ft south wall was 9 ft spoken for while
its east wall stood empty. **A fixture refused on a wall nobody tried is a false "cannot
fit"**, and this corpus exists to distinguish evaluated-and-failed from not-looked-at. Ties
break on the longer wall then S/W, so an unobstructed room packs exactly as before.

| | before | after |
|---|---|---|
| door/fixture overlaps, both plans | **2** | **0** |
| fixtures placed / refused, Tidewater | 12 / 0 | 12 / 0 |
| fixtures placed / refused, spec Colonial | 11 / 2 | **13 / 0** |

### 3. All 278 `placement` values authored, and the regex deleted

`against-wall` 159, `freestanding` 94, `built-in` 22, `corner` 3. The name-shape rules got the
easy ones and were corrected by hand against the room's own words for about forty: a console
and a pier table are named for the wall they stand against; *"six to eight side chairs, set
against the walls"* says so outright; an island is deliberately **not** against a wall, which
is what makes it an island; a cradle by the hearth is freestanding however near the chimney it
sits; the hall's *"open central hearth"* is in the middle of the room.

`check_rooms.py` now requires the field, so it cannot silently go missing again. **Furniture
findings on the two shipped plans: 44 → 34** — ten false accusations removed, rooms that had
been failing because a sideboard was being asked for clearance on both sides.

A note on formatting, because it nearly buried the review: nine room files are indented with
one space and two carry hand-inlined arrays, so a `json.dump` round trip reformatted eleven
files — **2,875 lines of diff for 278 one-line additions**. The values were inserted as text
instead. The diff is 545/278: one key per item, nothing else touched.

### 4. The one arrangement rule the corpus states in words

278 furniture notes, and **exactly one** names a wall run with a figure: `dining-room`'s
sideboard, *"Needs an uninterrupted wall of at least 6 ft. This is what the second window
usually kills."* That sentence is the basis, and `needs_uninterrupted_wall_ft: 6` sits beside
it **in the same record** so the two cannot drift — no new grammar file, no citation to verify
against a record elsewhere.

`plan_check`'s drawn layer measures the longest run each wall has left once the placement's
doors and windows have taken theirs, and reports a `minor` finding quoting the room's own
sentence. **A room whose prose states no rule gets no arrangement**, which is where Lucas drew
the line between the corpus and the architect.

Both directions are pinned, because a check that never fires and one that always fires are
equally useless: it **passes** on the shipped Tidewater plan for a measured reason (the dining
room is 23 × 14 with its three doors on N and W, so the whole 23 ft south wall is unbroken),
and it **fires** when the walls really are full.

## What was deliberately not done

- **No furniture-driven sizing**, per the ruling — refused on the record rather than deferred.
- **No arrangement beyond a stated wall run.** The corpus states 8 further placement rules in
  prose and **none of them with a figure**, so each would be an editorial call rather than a
  reading of the record. Seating that makes a group, a bed clear of the door swing, a table
  centred under the fixture: all unbuilt, and named in OQ 92.
- **No `essential` authoring.** 4 of 278 items carry it; filling in the other 274 is a large
  editorial pass whose only consumer would have been the sizing rule that was just refused.

## One thing found and left alone

**Some `furniture` entries are not objects.** "door swing", "towel positions", "clear route
from the street door to the house door", "a standing person", "car" — they are clearance
reservations wearing an item's shape, and they now carry a `placement` value that means nothing
for them. They were classified `freestanding`, the conservative reading (clearance on both
sides), which is what the fit check already assumed. Recorded in OQ 92 rather than fixed,
because re-typing them is a data-model question and not this package's.
