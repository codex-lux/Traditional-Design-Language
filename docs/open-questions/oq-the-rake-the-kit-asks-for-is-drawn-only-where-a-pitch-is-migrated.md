# oq/the-rake-the-kit-asks-for-is-drawn-only-where-a-pitch-is-migrated — the gable end has no slope where the roof judges no ridge

*Status: OPEN · Raised in: WP-16.9, the roof, the rake and the deeper cornice (1 October 2026)*

**B5 draws the rake the kit states, or The Cardboard Gable's where it says nothing. A rake runs along
the gable's slope, and a roof that judges no ridge has none.** roof.py takes a style's pitch from a
MIGRATED roof-pitch constraint and nowhere else. Where none is migrated it leaves the ridge height
unjudged, *"rather than computed off an invented pitch"*, and the gable end's outline is then the
eave line alone. So the rake the kit asks for is not drawn there. The face says *"NOT DRAWN — THE
ROOF JUDGES NO RIDGE (NO ROOF-PITCH CONSTRAINT IS MIGRATED FOR COLONIAL-REVIVAL), SO THE GABLE END
HAS NO SLOPE TO CARRY IT"*, and its eave faces do not say the gable ends draw a rake.

**THE KITS DO STATE A PITCH, AND ROOF.PY DOES NOT READ IT.** The cause was first worded "NO PITCH IS
STATED", and the second independent check of WP-16.9 found that false of every style reaching it on
the shipped plans. Each resolved kit states a pitch in its `roof_pitch` slot:

- colonial-revival and georgian-revival read queen-anne-american's: a minimum of 9:12, typically
  9:12 to 14:12, measured;
- new-urbanist-traditional reads folk-victorian's 6:12 to 12:12;
- new-classical reads greek-classical's 12 to 17 degrees.

Each of those reaches the style through the cascade, so whether it is the style's own pitch is an
OQ 51 question as well as this one.

**Measured on 1 October 2026, over the 41 styles the elevation draws: 26 have no migrated pitch,
and on 16 of them the kit asks for a rake that cannot be drawn.** Those 16 are beaux-arts-american,
beaux-arts-french, charleston-georgian, colonial-revival, dutch-colonial-american, english-classical,
federal-style, garrison-colonial, georgian-revival, greek-revival-southern-plantation,
italian-renaissance, new-classical, new-urbanist-traditional, palladian, saltbox-colonial and
southern-federal.

**On the shipped plans the rake is drawn on 2 of the 10 with a gable end.** The elevation draws
eleven plans, and good-05's hip has no gable end. The rake is drawn on tidewater-georgian and
good-03, whose styles have a migrated pitch. It is asked for and not drawn on the other eight: the
five colonial-revival plans (spec-builder-colonial, bad-01, bad-02, bad-05, bad-07), good-02,
good-07 and bad-03.

**What is not ruled.** This is `oq/the-depth-a-roof-needs-is-known-and-cannot-be-enforced`'s missing
pitch reaching the rake. Whether roof.py reads the kit's `roof_pitch` as B1 reads its `roof_form`
(and from which writer), whether those styles' pitches are migrated as sourced constraints, or
whether the rake waits for either.
