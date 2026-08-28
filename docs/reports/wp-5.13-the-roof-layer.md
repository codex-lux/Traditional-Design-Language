# WP-5.13 — The roof layer, and the facade drawn rather than indicated

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

---

# Addendum, 27 Aug 2026 — the dormer layer

The item at the head of "what is still owed" above said *"Dormers: none, and that is the answer …
the plan should declare zero and say why — **not yet written**, and the plan schema still has no
field."* This addendum is that work, and it turned out to be larger than declaring a zero, because
declaring the zero is what made the rest of the corpus behave badly.

## 1. Three states, and the third is the point

`declared.dormer` — the ontology's own slot id, cardinality `many`, **not** `dormers`; a plural key
read as a slot nobody had heard of and both reference plans picked up a `minor` finding saying so.

| state | means | what the elevation supplies |
|---|---|---|
| key absent | the record does not say | nothing — every dormer measurement withheld |
| `"none"` | a house **stated** to carry none | `dormer_count: 0`, `sum_of_dormer_face_widths_in: 0`, nothing per-dormer |
| `{count, face?, variant?}` | a house that has them | the full set |

Both shipped plans now state `"none"`, with their evidence in their own `note`: Pembroke Manor's
dormer was a 20th-c addition since removed; the George Wythe House records *"Dormer Windows /
None"*; Carter's Grove's original roof was unbroken and took a 1928 campaign to dormer at all; and
the structural reason is the pitch — Chesapeake houses that carry dormers run 47–50°, this one is
8:12, which is 33.7°.

`dormer_count` and `sum_of_dormer_face_widths_in` came off `elevation.py`'s `NOT_MODELLED` list
under that list's own rule: *to take a name off you must model the thing in the same commit.* What
made them refusable was never the geometry. It was that an absent dormer and an unstatable one were
indistinguishable, so any figure at all was a guess.

## 2. Every dimension comes from the fault corpus, which specifies a dormer completely

| figure | source |
|---|---|
| window width | `overscaled-dormer` — 0.75–1.0 of the sash below, taken at 0.85 |
| window height | the kit's own `dormer_window_height_in` expression |
| cheek | three bounds at once (below) |
| face width | window plus two cheeks |
| centres | the kit's own `alignment_rule`, derived from the bays, never authored |
| roof run in front | `sunken-dormer`'s preferred 18–36 in band — **editorial**, named as a choice |
| parity | the kit's `count_parity`, reported as a breach, never used to refuse a record |
| cornice | the ratio the house's own cornice obeys, applied to the dormer's face |

**The cheek needed a third bound, and the drawing is what found it.** The kit gives 4–8 in;
`fat-cheek-dormer`'s *test* caps the cheek at 0.25 of the sash. The kit band's midpoint is 6 in,
which passes both — and on the sheet it showed as a strip of bare board outboard of the window
casing, two members where the tradition wants one. That fault's own `correct_practice` states the
missing rule in prose its test does not encode: *"the finished cheek width should not exceed the
width of the window casing beside it"*, and where a corner board is unavoidable it should be *"the
same width as the window casing so that the two read as one member rather than as two competing
ones."* Clamped to the casing (4.21 in here), the cheek **is** the casing and the dormer face is
the window plus its two casings exactly — which is also the face the cornice is sized from, so the
two derivations now agree by construction rather than by coincidence.

**The cornice is the house's cornice, read small.** The kit's rule for this slot says dormers
*"carry the same order as the house at reduced scale"*, and `overscaled-dormer` says it from the
other side. `cornice-that-is-a-fascia`'s third secondary states the ratio the *house's* cornice
obeys — one twelfth to one fourteenth of the wall it crowns; this house comes out at **0.0781**,
inside that band. The same ratio over the dormer's own face gives **4.58 in** of cornice projecting
**1.96 in**. One rule used twice, not a second rule for dormers that nobody wrote.

## 3. The failure that came back through the door built to stop it

The first run after both houses could state `"none"` convicted both of a **serious** fault:

```
[serious] Dormers Off the Rhythm: 0 against equals 1.
```

`dormer-off-the-bay`'s parity secondary is `dormer_count % 2 == 1`. A stated zero is a real
measurement, so the rule ran on it. **Zero dormers is not an even number of dormers; it is no
dormers.** This is OQ 52's flagship failure — a house convicted of a dormer fault for having no
dormers — arriving through the very field built to prevent it, and it is worth being plain that it
was live in the working tree for several hours before the test suite caught it.

The fix is a fault-schema field, `applies_when`: **a precondition on the MEASUREMENTS**, in the same
shape as a test, standing beside `applies_to_styles`'s precondition on the style. A test whose
precondition fails is **not run** — not passed, not failed — exactly as a test scoped to another
style is not run.

`docs/elevation.md` had already asked for this field, in its own words, after WP-3.2 found *three*
instances of the pattern: *"Should these faults gain an explicit conditional guard (a `depends_on`
or similar field) … so a generator does not have to discover 'this key can only be safely supplied
when a companion condition holds' by tripping a false fatal first?"* That question is now answered
in the affirmative, and two of its three named cases are guarded:

- `entrance-slope-penetration`'s solar-array secondary, on `solar_array_area_sqft >= 0.1` — without
  it, a supplied 0 sqft convicts a house of a patchy array it does not have.
- `shutter-on-an-unshutterable-opening`'s arch-head secondary, on `window_head_radius_in >= 0.1` —
  a square-headed window has no head radius; supply 0 for both and the expression is 0/0.

The third is **not guarded and is not the same problem**. `cornice-that-is-a-fascia` carries two
**rival** secondaries — the domestic boxed eave at 0.35 of its own height, the full
entablature-derived case at 0.85 — so whichever is right, the other fails by construction. Guarding
them needs a measurement stating whether an order is applied to this facade, and no generator in
this corpus takes one. Named rather than papered over with a figure nobody has.

## 4. A fourth state, because a fault could vanish

Guarding all three of `dormer-off-the-bay`'s tests exposed a hole that predates this package.
`check_measurements` appends a fault to `faults_present`, `faults_clear` or `could_not_judge`. A
fault whose every test declines produces no evaluation, no missing measurement and no error — so it
was appended to **nothing**: absent from all three lists and from the summary counts, which reads to
a caller exactly like clear. That is the one collapse this corpus forbids, and the code already had
a comment saying so about the *error* case beside it.

`not_applicable` is now a fourth returned state, carrying which precondition declined and what it
required. `plan_check` surfaces it as `fault_not_applicable`. Not a pass: *the question does not
arise*.

**Movement on the two reference plans**, measured rather than asserted:

| fault | before | after | why |
|---|---|---|---|
| `dormer-off-the-bay` | unjudged | **not applicable** | all three tests preconditioned on `dormer_count >= 1` |
| `dormer-wall` | unjudged | **clear** | 0 in of dormer face over the building width is 0, at most 0.4 — a real measurement |
| `overscaled-dormer` | unjudged | **clear** | on the same measurement (its first secondary is `dormer-wall`'s primary, verbatim — a duplication that predates this package) |
| `fat-cheek-dormer` | unjudged | unjudged | needs a cheek width, and there is no cheek |
| `sunken-dormer` | unjudged | **clear** | no interruptions in the eave line |

Delete the declaration and all four go straight back to unjudged. `tests/test_measurement_honesty.py`
asserts that round trip, because it is the only assertion that can prove the three states are three
and not two.

## 5. What was found in the drawing, which the record could not show

The record was right before the drawing was. Three things were wrong on the sheet and passed every
test of the model:

- **The gable sprang straight off the head casing, with no cornice at all** — the abstraction the
  whole of WP-5.11 to 5.9 exists to remove, reappearing one storey up.
- **The sash carried half its glazing bars.** `"6/6"` is six lights in *each* sash; the renderer
  read the first number as the whole opening and drew a 2×3 grid where a double-hung 6/6 has 2
  across and 3 high twice, with the meeting rail between. The dormer is now drawn by the same
  `_window` as every other opening on the sheet, so the two cannot drift apart again.
- **A cornice return was drawn as two stubs standing above the level cornice** at the eave corners.
  A return runs *perpendicular to the picture plane*, so orthographic projection gives it no width —
  the same reason the cheeks vanish. It is a real member, drawn in the wrong projection: exactly the
  mistake a visible cheek is, made by the same hand ten lines further down.

And the pediment was got wrong twice before it was got right, both times in ways the model could not
see. Two stroked lines centred on the rake gave a notch at the apex and two tails hanging below the
eaves. An inner triangle offset in *y* alone gives a rake thinner than the level cornice by the
cosine of the pitch — and thinner the steeper the pediment. The correct construction insets the
tympanum **perpendicular** to each rake: horizontally by `th·L/rise` at the eaves, and the apex down
by `th·L/run`. `tests/test_drawn_geometry.py` measures that perpendicular thickness off the emitted
polygons and holds it against the level cornice's own: the correct construction gives 9.0 px against
9.0, a y-only inset gives 0.0, a centred stroke gives 4.5.

That is the whole lesson of this file's parent report, at dormer scale: **a green suite proves the
model and says nothing about the ink.**

## 6. Deliberately not done

- **The dormer cornice is drawn as a band with its projection and its shade line, not as its
  moulded profile.** At 1/4 in = 1 ft a 4.58 in cornice is nine pixels; the main cornice makes the
  same choice for the same reason and puts its real profile in a detail inset. A dormer cornice
  inset is a reasonable next piece of work and is not this one.
- **The dormer's cheek is not drawn as a plane**, and must not be: in orthographic projection it has
  no width. `visible_cheek_width_in` still travels in the measurements because `fat-cheek-dormer` is
  a **photograph** test and a photograph is oblique. The elevation and the photograph disagree about
  the cheek on purpose, and each is right about its own projection.
- **No dormer is drawn on the far slope**, and none is drawn where its apex would rise above the
  main ridge — the second is a silent skip and should probably become a stated refusal.
- **The sill's height above the garret floor** is still not derivable and still not stated.

---

# Addendum 2, 27 Aug 2026 — the chimneys, and OQ 80 closed by a comment that had gone false

Drawing the dormers meant reading `render_elevation.py`'s roof block, and twenty lines below it sat
this, in the renderer's own voice:

> The stacks are NOT drawn on the front, and the reason is worth writing down rather than leaving as
> an apparent oversight. … But `build/roof.py`'s long-face silhouette is FLAT AT THE EAVE: for the S
> face of this side-gable house it returns exactly two points, both at 25.44 ft, and models no roof
> mass above the cornice at all.

It returns four points now, and has since earlier in this same package. **The comment was true when
it was written and had gone false before the file was next opened** — prose asserting what the code
no longer does, which is the failure this corpus polices hardest, sitting inside the fix that
falsified it. That is worth more than the drawing it produced: the roof fix and this comment were in
the same working tree for hours, and nothing connected them.

**OQ 80 asked exactly this question** — *"whether `elevation_profiles` should carry the visible roof
PLANE on a long face rather than just its eave line, which is a small piece of geometry with
consequences for every renderer that reads it … The first is almost certainly right and is not a
renderer's call to make."* It was right, and it was four lines. `_profile_top_at()` now answers how
much of a stack a roof hides — for a gable triangle and a long-face rectangle alike, with no special
casing, because the rectangle IS the parallel projection of one sloping plane.

## Two more invented constants, of exactly the OQ 52 class

Under that comment the gable-end stack was drawn at:

```python
cx_ft = 3.0 if near_left else depth_ft - 3.0        # 3 ft from the gable's front corner
cy0, cy1 = c["grade_to_ridge_ft"] - 2.0, ...        # based 2 ft below the ridge
```

The record states `y_ft` — **21.33 ft on this house, which is mid-depth: a stack on the ridge line**
— and `total_height_grade_ft`. Neither constant came from it. On the sheet the 3 ft put a brick bar
in the sky at the top-left corner of every gable elevation this corpus has ever drawn, touching no
roof at all. It had been there since WP-3.2 and nobody looked.

This is the third distinct place in three packages where `elevation.py`/`render_elevation.py` were
found asserting a number no record states, and the second where the guard that exists for the class
could not see it: `NOT_MODELLED` and its test guard the *measurements* dict, and SVG is on the other
side of that line.

## What is drawn now, and why it is less than what is visible

Both stacks appear on the front elevation, at the ends of the ridge, offset outboard by half their
own width because the kit's source string says `gable-end-exterior`. Each gable end draws the one
stack in its own wall plane, at the depth position the record states.

**Only the part above the roof is drawn**, and that is a claim about *evidence*, not about
visibility. These stacks are exterior, so nothing hides the breast and the honest visibility answer
is the whole thing from grade — which is the reading the kit calls *"visible from a mile away and
conclusive against New England"*, and it is a real loss not to have it. But the only width this
corpus states is `brick-course`'s eight courses square, 22 in, itself flagged `judgment: true`, and
that is the width of the **stack**. A chimney breast at the base of an exterior end stack is several
feet across. Drawing 47 ft of 22-inch brick asserts a chimney nobody measured, in the same shape as
the 3 ft and the 2 ft this block just lost. The legend now says what is missing below.

Drawing it from grade for one revision also surfaced something real, which is **OQ 85**: on the
gable end the stack is at mid-depth and ran straight down through the centre window of both storeys.
`roof.py` puts the stack on the centre line and `elevation.py` independently puts a window there,
and nothing relates the two records. Either the gable end has no centre window, or the stack is off
the centre line, or — most likely for the type — the stack is a broad breast with the centre bay
blind. All three are corpus facts and the corpus states none of them.

## Also found

`tests/test_elevation.py` carried this, two lines apart:

```python
# ... a pin on `class="rf"` exactly would fail every time the roof moved a rung on the
# ladder without the roof having changed at all.
assert 'class="rf' in text
assert 'class="ch"' in text
```

The comment explains the mistake and the next line commits it. Fixed to match the token — and
strengthened, because *"a stack is on the sheet"* was true of the version that drew it floating in
the sky. It now reads the position back off the emitted rect and holds it against the record's
`y_ft`.

---

# Addendum 3, 27 Aug 2026 — what the SECOND house showed

The dormer work was developed against `tidewater-georgian-careful` and verified on it at every
step. Running the same code on `spec-builder-colonial` — the other shipped reference plan, three
minutes' work — produced two things the first house could not have shown, and one of them is a
corpus finding rather than a code one.

## The variant was chosen by dict order, and then it was not

`dormers()` took the style's variant as `next(v for v in variants if canonical)` where the record
named none. On Tidewater that returns `gabled`, which is right, and it is right by accident: the
style makes **both** `gabled` and `pedimented` canonical, so *the record has not chosen* and the
generator was choosing for it out of dict order. Fixed — a variant is taken from the record, or
from the style where exactly one is canonical, and otherwise the record is reported as not having
chosen, the plain gabled form is drawn, and the sheet says so. This is the same shape the window
head already uses when the plan's date cannot separate two masonry heads: **an unjudged head is
drawn as no head at all rather than as a definite one.**

## The Colonial Revival's only canonical dormer is formed within thatch

The spec builder's dormers came back as **`eyebrow-swept-dormer-within-thatch`** — and it is *not*
dict order, which is what made it worth chasing. `colonial-revival` binds the `dormer` slot
**nothing**, and the lineage cascade resolves the whole slot from `english-cottage-vernacular`:

```
eyebrow-swept-dormer-within-thatch   canonical   "Formed within the thatch itself, not boxed on top of it"
catslide-over-rear-outshot           permitted
boxed-dormer                         FORBIDDEN   "c01, hard."
```

So on a production Colonial Revival the one canonical dormer is a thatched cottage's, and the boxed
dormer — the only kind such a house is ever built with — is **forbidden**. A record declaring one
would be refused. This is **OQ 51's class arriving in the kit layer rather than the proportion
layer**: the cascade delivering, with full confidence, something nobody bound. OQ 51's own ruling is
*adjudicate first, flip inheritance to opt-in second*, and this is one more entry for that work
list; it is not a renderer's decision and has not been made here.

What the renderer does instead costs one field: the record carries `variant_source_node`, and where
the variant came from a node that is not the style itself the sheet says so — *"DORMER VARIANT
'EYEBROW SWEPT DORMER WITHIN THATCH' IS INHERITED FROM ENGLISH COTTAGE VERNACULAR — THIS STYLE BINDS
THE SLOT NOTHING (OQ 51)"*. The question is on the drawing rather than under it.

## And the glazing pattern was invented

That same cascaded slot states no `sash_pattern`, and `_dormer_lights` defaulted to `"6/6"` — so
the spec builder's dormers were drawn with a confident twelve-light pattern that no record anywhere
had stated. It now returns `(None, None)`, the sash is drawn as glass with no glazing bars, and the
legend says the pattern is undeclared.

Three fabrications in one function, all of them found by running it on a second house rather than by
any test. **The generator was verified on the plan it was written against, which is the weakest
possible verification and had been enough three times in this session.**
