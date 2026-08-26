# The workbench legibility pass — the order that came apart, and the labels through the walls

*26 August 2026. Raised from use rather than from an audit: two screenshots and four
sentences. Everything below was reproduced before it was fixed, and every fix carries a
test that fails against the old behaviour.*

---

## What was reported

Of the Proportions surface (⑩):

> * The column is separated from the base.
> * The column is separated from the plinth.
> * It extends past the top of the frame if the diameter is large enough.
> * You can't zoom into those windows, so you can never really actually read the dimensions.

Of the Plan Workbench (⑦):

> You can't zoom in to really be able to read much of the dimensions. Also, the room labels
> clearly are cut off by some of the walls and difficult to read. Where the room is tight
> enough, these titles should wrap on each other and become two lines of text.

Four of the six are one drawing bug apiece. The remaining two are the same missing
instrument.

---

## I. The order came apart, and it was one line

`proportion_engine.dimension()` returns each member with `y_bottom_in` and `y_top_in`
**already summed through the whole stack** — the pedestal's plinth runs 0″ to 22.5″, the
base's plinth 90″ to 96″, the shaft's body 108″ to 355.5″. `OrderPlate` kept its own
running total of the assemblies' stated heights and added it to those numbers again:

```js
y0: y + (m.y_bottom_in || 0)          // y is the assembly's own base. It is already in there.
```

At a 36″ diameter that put the base 90 inches above the plinth it sits on, the shaft
another 108 above that, and the cornice at 822″ in a frame 450″ tall — which is the third
report, *extends past the top of the frame*, and it was never about the frame. The
assembly captions down the left were drawn from a **separate and correct** running total,
so the plate labelled a gap CAPITAL and pointed at nothing.

Verified before the fix, across all 26 order packs at a 36″ diameter: the engine's members
are contiguous from 0 to the stack height with **no gaps and no assembly whose summed
members disagree with its stated height** — 26 of 26 clean. The corpus was right; the
plate's reading of it was not.

Second, smaller, and the reason the column read as a stick: every band was drawn `16 + projection`
units wide **whatever the order's diameter**, so the shaft — whose whole business is to be
one diameter thick — came out narrower than the mouldings on it. The plate now draws a
half section, and it takes its datum rule from the corpus's own order tool
(`build/orders_template.html::buildGeometry`) rather than inventing one:

| assembly | a projection is measured from |
|---|---|
| pedestal, subplinth | the die's naked (`R` + the base plinth's projection) |
| base, shaft, capital | the column's radius **at that height** — which diminishes, and each authority says where |
| architrave, frieze, cornice | the naked of the frieze (`R_top`) |

`entasis_begins_at` differs between authorities — Gibbs starts the diminution at a third
of the shaft, Chambers at the base — so the workbench's `proportions_with_members` now
passes the `column` record through rather than the plate assuming a taper. Every band is a
polygon, not a rectangle, so the shaft tapers instead of stepping.

Every annotation on the plate is now sized in **hundredths of the stack**, which means the
plate is identical at any column diameter. That is the claim a proportional system makes,
and it is also why the plate can no longer overflow its frame at 36 inches: it does not
change shape at 36 inches.

One thing corrected on the way: the engine flags `side_by_side` off an assembly's
`sums_check`, and a **derived** shaft — an authority that publishes a column height and no
shaft, like Benjamin's Greek Doric — carries `sums_check: false` with a single member. One
member cannot stand beside anything. The plate was filling it as a triglyph-and-metope pair;
it now marks side-by-side only where there is more than one member, and the derived shaft
keeps the dashed medium-confidence mark that says nobody published it.

## II. Labels that would not fit in the room

`Sheet.jsx` set every room's name on one line at a size derived from the room's **width
alone** (`1.25 × min(1, w / 12.5)`), with no reference to how long the name was. So
BUTLER'S PANTRY, seven and a half feet wide, was drawn about eleven feet long and crossed
two partitions to get there. Measured on `tidewater-georgian-careful`: **9 of 13 rooms had
a label outside the room it named.**

`workbench/app/src/sheet/label.js` fits it the way a draughtsman would, in that order:

1. **Break before shrinking.** Words are split into 1–3 lines by exhaustive search for the
   arrangement whose widest line is narrowest, and the fewest lines that hold the preferred
   size wins.
2. **Shrink only as far as it stays readable**, to a floor of 0.55 ft.
3. **Turn it where the room is a slot.** A room more than 1.3× as deep as it is wide gets
   its name along its length if that buys a materially larger letter (15%) — which is how
   BACK HALL (HYPHEN), 7′-4″ × 40′-1″, gets read.
4. **Never truncate.** A floor is a floor: a name that will not fit at it is still drawn,
   cramped and whole, because a reader can see cramped and cannot see amputated.

Widths are **measured**, not guessed from character counts — a hidden canvas measures the
sheet's own face at a reference size and the result is cached per string. EB Garamond's
capitals are narrow, and a guess wide enough to be safe for W would break lines that fit.
The webfont arrives after first paint, so `useFontMetrics()` drops the cache and re-fits
once the real face lands.

The dimension string is fitted too, and shown only where the name still reads at a working
size beside it. It is never wrapped: a dimension broken across two lines reads as two
dimensions.

## III. The loupe

`components/PlateViewer.jsx`. Fit is the resting state and is recomputed as the pane
resizes; a chosen magnification is held until *fit* is asked for again. Zoom by the ±
keys, by ⌘/ctrl-scroll (anchored on the cursor), or *1:1*; pan by drag, scrollbar or
wheel. It scales the **whole plate** — title block, sheet and caption together, as a sheet
moves under a loupe — rather than the SVG alone, so the lettering never drifts out of
register with the drawing it labels.

Two things it was built around:

- The scale is a CSS transform, so `getScreenCTM()` still maps screen pixels back to model
  feet and **the wall-drag handles keep working at any magnification**.
- The **pane** is measured, never the scroller. A scrollbar appearing inside the scroller
  would narrow it, which would re-fit the plate, which could make the scrollbar go away
  again; measuring the outer box breaks that loop before it can oscillate.

It is mounted on the Proportions plate, the Plan Workbench sheet and — not asked for, but
the same complaint one surface over — the five sheets of the Drawing Set.

The Proportions surface's own layout changed with it. The plate used to sit in a wrapping
flex row, and at any pane narrower than about 830 px it wrapped **below** the invariants
and the authorities table, a screen and a half down, where a reader looking for the drawing
would not find it. It has a column of its own now, and the rules table spans the full width
underneath — which is what a five-column table with a paragraph of note per row wanted all
along.

## IV. Two things found while fixing those, and fixed

**The wall handle could not be grasped.** The sheet's caption offers a wall drag; the
handle was drawn with the rooms, and the partition on the very wall line it was offered for
was drawn after it. `elementFromPoint` at the handle returned the partition. The gesture
had been dead — verified against the pristine tree, so this is not a regression from the
loupe — and it matters more now, because with the loupe mounted a drag on that pixel pans
instead of doing nothing. The handles are drawn last. Confirmed working end to end: the
Drawing Room goes 20′-0″ × 16′-7″ → 23′-5″ × 20′-0″ and the plan re-solves around it.

**`build/render_plan.py` had the same label defect and a worse one.** It is the renderer
behind the Drawing Set's *solved plan* and the SVG export, so the fix would otherwise have
been half-applied inside the same product. It set names on one line at a fixed 9.5 px, and
its answer for a small room was `nm[:9]` — which does not shorten a name, it amputates one:
*Butler's Pantry* was drawn *Butler's* and read as the room's actual name. It now wraps,
shrinks, turns and never truncates, by the same rule as the sheet.

Its widths are **estimated** rather than measured — that renderer has no font metrics — from
a per-character advance table for the face it sets names in. An estimate that runs a few
percent wide is a label with air around it; the old fixed size was a label through a wall.

One trap worth carrying: the fitted size must be written as `style="font-size:…"`, not as
the `font-size` attribute. A presentation attribute loses to the sheet's own `.nm`/`.dm`
rules, so a correctly computed size written as an attribute is computed, ignored, and the
label overflows anyway. That was live for one build and is the reason the dimension strings
still ran through the walls after the first fix.

## V. What guards this

Added to `workbench/app/e2e/walk.mjs`, all three failing against the old behaviour before
they were committed to passing against the new:

| check | what it measured on the old code |
|---|---|
| `no room label leaves the room it names` | **9 of 13 rooms** named outside themselves |
| `the order stands as one stack — no gap between its assemblies` | the gap was there |
| `no member is drawn outside the plate` | **30 members** clipped out of the frame |
| `a wall handle can still be grasped through the loupe` | no drag preview: the handle was under a partition |
| `the sheet draws the record's rooms` | — |

The last one is not decoration. The label check's first form selected nothing and passed
vacuously; the room count is asserted before the spill is, because a selector that matches
nothing is the one way an honesty check can lie.

## VI. What was deliberately not done

- **The plate is still bands, not mouldings.** Its own header says so and that stays true:
  the ovolo is drawn as a step out, not as a quarter round. The profile geometry lives in
  `dist/orders.html` and the two should not diverge by being reimplemented twice.
- **`render_plan.py` still estimates text widths.** Measuring would mean shipping metrics
  for the face or rendering through a layout engine, for a renderer whose output is read at
  one size.
- **Nothing was done about `tests/test_solver.py::test_check_plans_solve_with_stated_downgrades`**,
  which fails on this machine — 16 downgrades against a pinned 8. Verified failing on the
  pristine tree before any of this work, and nothing here touches `build/geometry*.py`. It is
  CP-SAT wall-clock nondeterminism of the kind the test's own docstring names, and it is
  somebody's finding, not this pass's to bury.
- **The loupe magnifies the pen with the drawing.** That is a departure from the Drawn
  Language's own rule and it is **OQ 64**, raised rather than decided.
