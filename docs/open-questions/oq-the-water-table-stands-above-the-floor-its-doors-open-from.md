# oq/the-water-table-stands-above-the-floor-its-doors-open-from — the floor and the water table are dimensioned from different packs, and nothing relates them

*Status: OPEN · Raised in: WP-16.8, the audit of Phase 16 (3 October 2026), found while attributing the bands the audit gave the CAD elevation*

**On every drawn shipped plan the elevation puts the water table's top above the ground floor.**
Measured on the audit's tree, heuristic placement, over the sixteen plans:

- **The floor** is 2.0 ft above grade on all sixteen. No plan states its own; it is the section's
  `structure.DEFAULT_GRADE_TO_FIRST_FLOOR_FT`.
- **The water table's top** is 33.75 in on the ten elevations the code reads as not masonry, and
  27.5 in on the Tidewater's brick one. Five plans draw no elevation.
- **So a door's bottom 9.75 in, or 3.5 in, stands below the water table's top.** Seven doors over
  five of the eleven drawn plans:
  - the Tidewater's passage door and porch door, on S;
  - the spec Colonial's porch door, on N;
  - four garage doors (bad-02, bad-03, bad-07 and the spec Colonial). Each is drawn with its sill
    at the house's floor, 24 in above the drive.

**Neither surface shows the crossing for what it is.** The sheet paints each door over the band, so
the band looks as though it stops at the jamb. The CAD elevation drew no band at all until this
audit gave it the sheet's (`elevation.band_marks`), and it now masks the band behind each opening
the band crosses. Neither surface says that the floor is below the water table.

**What the corpus states, in its own words:**

1. `facade-classical`'s rule `water_table.height = part * 3`, quantity
   `water_table_top_above_grade`: *"TOP OF THE WATER TABLE ABOVE FINISHED GRADE. Twenty-seven
   inches."* Its authority note: *"First floor above finished grade runs 18-30 in in ordinary
   Anglo-American work; the water table sits at or just below the first-floor structure."*
2. The same pack's elevation assembly: a `foundation` member of 3.0 parts, then a `water_table`
   member of 0.75 parts, then `storey_one`. **The elevation draws this one, not the rule, wherever the wall is not masonry.**
   `elevation.water_table_and_belt` sums the two members, "facade-classical's own foundation +
   water_table members, summed", to 33.75 in at the pack's 9 in part. So one pack puts the water
   table's top at 27 in in its rule and at 33.75 in in its assembly.
3. The same pack's `foundation_expression.height = part * 2`: *"Eighteen inches of exposed
   foundation below the water table."*
4. `brick-course`'s `water_table.height = module * 2.5`: *"Two and a half modules — ten courses —
   puts the top of the water table at 27 1/2 in on the default coursing."*
5. `storey-graduation`'s `foundation_expression.height = part * 2.4`, quantity
   `exposed_foundation_height`: *"Two feet on the default."* That is the figure `structure.py`
   takes as the floor: `DEFAULT_GRADE_TO_FIRST_FLOOR_FT = 2.0`, commented *"storey-graduation.json's
   foundation_expression default"*. **An exposed foundation's height is read as the floor's.**

So the floor comes from one pack's exposed foundation, and the water table from another pack's
assembly or from the brick coursing. No reader holds the two against each other.
`check_addresses.py` cannot see it, because the two figures are written at different slots.

**What moving either would move.** Raising the floor to the water table moves the section, the
scene's floor slabs, every elevation's storey datums, and every opening's sill and head. It also
moves the scene's check of the stoop against the floor: WP-12.7 measured the stoop's risers
stopping short of this 2.0 ft floor. Lowering the water table to the floor, or drawing
facade-classical's rule in place of its assembly, moves every drawn elevation's base.

**What is wanted:**

- which datum governs: the floor raised to the water table (facade-classical's *"at or just below
  the first-floor structure"*), or the water table drawn at or below the floor;
- whether the frame elevation reads facade-classical's rule (27 in) or its assembly (33.75 in);
- how a band meets a door it crosses: stopped at the jamb, or carried under a step.

*Taken as recommended under Lucas's standing instruction of 1 Oct 2026, never put: raised and left
open. Nothing is moved, because every answer moves every drawn elevation and the section with it.*
