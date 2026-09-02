# oq/the-passage-is-divided-and-the-corpus-has-no-word-for-it — the tradition cuts a long passage across its length, and the only move we have is to widen it

*Status: OPEN · Raised in: WP-9.2, the precedents measured (1 Sep 2026)*

**The generated passage is 10.00 × 37.00 ft and it is legal on every band the corpus declares** —
width 10 in [6,14], length 37 in [20,40], proportion 3.70 in [2.0,5.0], area 370 in [130,400].
`faults/passage-that-is-a-corridor.json` tests `passage_clear_width_ft at-least 8.0` **and nothing
else**, so a 10 ft passage passes it at any length whatever. Lucas called it *"huge"*; by the
corpus's own numbers there is nothing to report.

Two things are missing, and the second is the one with no vocabulary at all.

## (a) The record contains the arithmetic that condemns it, unread

`rooms/centre-passage.json`, `daylight.note`:

> *"Light from a fanlight and sidelights at the front reaches about 16 ft; the same at the rear
> reaches back the other 16; the two overlap in the middle and the passage is lit end to end."*

16 + 16 = 32, and the passage is 37 ft long. **By the corpus's own sentence this passage has a
five-foot dark band in its middle.** Nothing computes it. `depth_multiplier` is the field that IS
read — `check_rooms.py:241` as a band check on the record, `plan_check.py:1294` in the daylight
layer — and it is a different quantity. The 16 ft reach is prose.

This half is small and probably not a question at all: it is a derivable measurement
(`passage_length_ft` against twice the stated reach) that the drawn layer could evaluate today.
It is recorded here because it is the same shape as the second half and should be decided with it.

Gunston Hall, incidentally, sets a stronger requirement than a fanlight: *"The center passage has
two small windows flanking the doors at each end of the house."* A door **plus a pair of windows**
at each end.

## (b) The tradition divides the passage, and there is no record of it

In a double-pile house the centre passage is not one long slot. It is divided at the pile line
into an entrance hall in the front pile and a stair hall in the rear:

> Gunston Hall (HABS VA-141): *"The central passage shows French roccoco detail with the carved
> C-scrolls in the spandrels of **the double elliptical arch that spans the center of the
> space**."*

> Drayton Hall (HABS SC-377): *"Entering the Great Hall from the raised open terrace and recessed
> portico on the southwest (land side) … **Immediately behind the Great Hall is the two-story
> stair Hall** with double doors leading to the exterior porch on the northeast."*

A transverse arch at Gunston Hall; a wall and double doors at Drayton. Searching `rooms/`,
`groupings/`, `partis/` and `faults/` for a transverse arch, a divided passage, or a passage
subdivided across its length returns **nothing**.

**So the corpus's answer to a passage that has become a corridor is to widen it, and the
eighteenth century's answer was to cut it in half.** Those are different moves, and only one of
them was ever available to the search. `rooms/centre-passage.json`'s `critical_dimension` is
explicit that width is the question — *"WIDTH, and there are two right answers and no compromise
between them"* — and it is a very good note about width. It has nothing to say about length,
because the type it describes is the single-pile passage, where length is the depth of one pile
and takes care of itself.

## The question

**Is a divided passage a fact about the PLAN or about the SECTION?** The corpus has to choose,
because the two answers put it in different files and give it different powers.

1. **Plan.** The passage becomes two rooms — `entrance-hall` and `stair-hall` — with an opening
   between them whose kind is stated. This costs nothing new: both room types exist,
   `openings/grammar.json` already resolves every room pair to a rule, and
   `rooms/centre-passage.json`'s own `must_adjoin` already names both. The parti would name two
   rooms where it now names one, and the corridor fault could then test length per room. **The
   cost is that it is a different plan** — a re-authoring of the centre-passage partis, and it
   makes `centre-passage` the name of a pair rather than a room.
2. **Section/elevation.** The passage stays one room and gains a property: divided at a stated
   fraction of its length by an arch, a beam, a screen or a pair of columns. This is closer to
   what Gunston Hall actually is — the passage there IS one room, arched across the middle, not
   two rooms — and it keeps the plan record simple. **The cost is a new vocabulary item**: a room
   that is one space and two compartments, which nothing in the schema can currently say.
3. **Both, because they are two different buildings.** Drayton Hall really is two rooms; Gunston
   Hall really is one room with an arch. If the corpus wants to describe both, it needs (1) for
   Drayton and (2) for Gunston, and the parti has to say which it means.

**(3) is probably right and is the most work.** It is recorded that way rather than picked,
because choosing between them is an architectural judgment about what the type IS, and that is
Lucas's to make.

**What must not happen meanwhile.** Do not widen the length band to make the finding go away, and
do not add a `passage_length_ft at-most` threshold invented for the purpose — no source here
supports a number. The measured evidence available is one passage width from physical evidence
(Mount Pleasant, *"10'-11 1/2" brick to brick"*, read from partition racking) and no lengths at
all. A length rule authored today would be a guess wearing a citation.
