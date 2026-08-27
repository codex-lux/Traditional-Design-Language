# WP-5.9 — The roof layer, and the facade drawn rather than indicated

*27 August 2026. Raised by Lucas: "do the roof layer next — ALL these items are exceptionally
important to me in getting this measured drawing to look remotely right. I don't want a schematic
— I want a FULLY fleshed out, beautiful drawing with accurate representations of shutters, window
sashes, brickmoulds, dormers etc. Research these details as necessary to draw them correctly."*

Six research passes and three recon passes, every figure graded primary / secondary / convention /
judgment, and every figure claimed as sourced then attacked by a skeptic. Four rulings taken before
any code was written. This report records the first phase.

---

## The four findings that reframed the package

**1. The front elevation was not thin. It was missing 14.22 ft of building.**
`build/roof.py::elevation_profile` returned two points, both at the eave, for a long face — with
the comment *"ridge is behind the near roof plane, not visible."* That is a **perspective** argument
applied to an **orthographic** projection. The near plane slopes away from the viewer, and parallel
projection maps it to a full-width band from the eave up to the ridge; the ridge at 39.66 ft is the
top edge of the drawing, not the eave at 25.44. Every front elevation this corpus has ever drawn of
a side-gable house had no roof on it.

Nothing caught it because every roof test asks the RECORD for the ridge height, and the record had
it right all along. Only the *profile* was wrong, and only the *drawing* consumes the profile.

**2. The sheet was at 1/16″ = 1′-0″, and every detail asked for is below the pen at that scale.**
`scale=6.0` px/ft is exactly 1:192 — half of HABS's smallest working scale and a quarter of its
stated default. A 7/8 in muntin is **0.44 px**, narrower than the line then being drawn for it; a
4 in reveal is 2 px; a brick course is 1.4 px. No amount of authoring fixes a drawing at that scale.
**Ruled: 1/4″ = 1′-0″**, HABS's own default for elevations.

**3. Six measurements were fabricated and two faults were judging houses on them.**
`elevation.py` published `sash_stile_width_in = muntin × 4` — **3.5 in against the corpus's own
stated 2 in**, on the very dimension `muntin-wider-than-its-date` measures — plus a meeting rail at
muntin × 1.5 and four shutter figures from ratios (0.8, 0.4, 0.18, ×3) that exist in no pack, kit or
element file. `faults/shutter-panel-scale.json` consumed two of them directly.

This is the second half of OQ 52, and `tests/test_measurement_honesty.py` could not see it: that
test checks whether a **refused** name leaks through the `NOT_MODELLED` filter. These were not
refused names. They were supplied numbers with no author.

**4. None of the research could be authored as `measured`.** The researchers could not open a single
cited document — colonialwilliamsburg.org, dhr.virginia.gov, nps.gov, classicist.org all return 403
at the proxy, the same block that holds OQ 7–11 open. The skeptic then caught a thesis credited to
the wrong author and a belt-course rule that is geometrically impossible against this corpus's own
brick heights. **Ruled: everything editorial, judgment, quoting the excerpt and stating plainly that
it was read as a search-index excerpt and is not verified at source.**

## What was built

**The roof.** `elevation_profile` now returns the plane: a side-gable long face is a rectangle from
eave to ridge (and its blankness is correct — there is nothing in it but the covering), a hip is an
isosceles trapezoid whose ridge is exactly *length − depth* because each hip runs in at 45° in plan,
and a gable end stays a triangle. All three come from one rule. The renderer draws it as a closed
plane with shingle coursing at a 5½–6 in exposure, foreshortened by `exposure × sin(pitch)` and
drawn only where a course clears 2 px — below that a course is a tone, not a line, and HABS's own
rule is a vignette of the covering rather than a generated hatch.

**The gauged arch, drawn brick by brick** (HABS 4.6.2 names round, jack and flat arches as the one
place individual bricks are always drawn). A flat arch is a **trapezoid**, not a rectangle: its
skewbacks are cut at 60° so the extrados runs out past the soffit by *depth/tan 60* at each end.
Drawing it square hid the joint that makes a flat arch stand up and left the outer voussoir joints
running off into the wall with nothing to stop them. The voussoirs radiate to a strike point below
and are **one brick wide at the soffit** — the corpus's own 2.75 in course, the only brick dimension
it states — giving thirteen to fifteen over these openings. Deriving the count from the arch *depth*
instead gave five: an eight-inch voussoir, which is not a brick.

**Glass as a tone.** HABS 4.6.6 and the older drawn practice the manual praises: *"Glass areas are
black."* A pane left the colour of the sheet reads as a gap in the wall. The muntins are drawn light
against it, and the meeting rail — 1¼ in against a 7/8 in bar — takes a heavier rung, because it is
the line that says the sash is double-hung rather than a fixed grid.

**One line ladder, on HABS's rungs.** 0.1 mm joint lines, 0.2 light edges, 0.3 medium, 0.4 heavy,
0.5 cut, 0.6 the ground line — 6:1 end to end, adjacent rungs about √2 apart. The five class names
predate this package and are kept; `w-ground` is the sixth rung, which the sheet did not have. The
grade line carried its weight as an inline attribute and so sat off the ladder entirely; it is now
the heaviest line on the sheet and runs past the building at both ends, because it is the ground.

**The six-panel door**, drawn as the arrangement it is — two short over two long over two short.
Two horizontal lines across the leaf, which is what was there, is a *three*-panel door.

## The shutters, which is the interesting one

Four independent records say a solid-masonry Chesapeake house of 1765 carried **no exterior
shutters**: Colonial Williamsburg's report on the Ludwell-Paradise House answers it for a brick
house of exactly this class — *"None. (Being a brick building in colonial times shutters appeared
only in interiors.)"* — the Public Records Office's were examined and discarded as not original, and
neither Pembroke Manor nomination describes any. The photograph shows none.

`tidewater-georgian` bound the shutter slot **empty**, and the cascade delivered its parent's
raised-panel pair — so every elevation of this style had been drawn with shutters it should not
have. That is the OQ 51 trap, adjudicated here as OQ 51's own ruling directs: `shutter: none`
canonical on the masonry style, `raised-panel-pair` demoted to atypical rather than forbidden
because it is correct on the frame houses of the tradition, and the geometry built regardless — the
frame plan draws it, with three panels below and two above.

**Three below, two above** is itself a correction: the code hardcoded four, and the corpus's own
pack rule says *"a 12/12 window gets a two- or three-panel leaf, a 6/6 gets two."* Colonial
Williamsburg's reports on the Prentis and John Blair shutters give three. The drawing got more
correct by losing something.

## What was found

**A perspective argument inside an orthographic renderer survives because it sounds right.** The
comment on that line of `roof.py` was confident, specific, and wrong, and it stood through three
work packages that all read it.

**A test that guards a filter does not guard the values that pass through it.** `NOT_MODELLED` and
its test are a good mechanism aimed at exactly one failure — a refused name leaking. Six invented
numbers walked past it for four packages because they were never refused in the first place.

**The scale was the whole argument.** Every one of the details in the brief was below the pen. It is
worth stating as a general rule for this corpus: *before authoring detail, check that the sheet can
hold it* — otherwise the authoring is real and the drawing is a lie about it.

## What is deliberately not done, and what is still owed

- **Dormers: none, and that is the answer.** Pembroke's dormer is a 20th-c addition since removed;
  the Wythe House records *"Dormer Windows / None"*; Carter's Grove's original roof was unbroken and
  took a 1928 campaign to dormer. Houses that carry them have 47–50° roofs; this one is 33.7°. The
  plan should declare zero and say why — **not yet written**, and the plan schema still has no field.
- **The Flemish bond chequer** is not drawn. The geometry is now known (a 13½ in repeat, each course
  offset exactly half of it), but the glazed-header question is a date decision and the sourced
  evidence argues *against* a chequer at 1765.
- **Shadow** is not drawn. HABS prohibits tone in elevation and prescribes the **shade line**
  instead — a heavier line on the shadowed edge — which suits this corpus's line discipline and does
  not worsen OQ 64. Not yet built.
- **The window sill may be wrong in the data.** The kit **forbids** `wood-sill-sloped` and makes
  brick sills canonical; the sourced evidence says brick sills are not a Chesapeake colonial detail
  and that Pembroke Manor has *"molded frames and sills"*. The kit's note gives a specific reason for
  its choice, so this is a corpus-truth question and needs Lucas's ruling rather than a quiet edit.
- **The cornice band, the doorcase pilasters and the water table** are still drawn as plain bands at
  a scale that could now carry their real profiles.
