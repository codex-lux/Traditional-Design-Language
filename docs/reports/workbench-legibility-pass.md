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
half section. It first took its datum rule from the corpus's own order tool
(`build/orders_template.html::buildGeometry`), and **that rule is wrong for twelve of the
twenty-six packs — see §VII, which is the audit's finding and the largest thing in this
report**. Corrected, the datum is:

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
| `a wall handle can still be grasped through the loupe` | no drag preview: the handle was under a partition |
| `the sheet draws the record's rooms` | — |

The last one is not decoration. The label check's first form selected nothing and passed
vacuously; the room count is asserted before the spill is, because a selector that matches
nothing is the one way an honesty check can lie.

**Two claims made here on 26 August were overstated and are withdrawn.** This table
originally also listed *the order stands as one stack* ("the gap was there") and *no member
is drawn outside the plate* ("**30 members** clipped"). Both numbers came from a negative
test that broke the NEW code's arithmetic, not from the code as it stood at HEAD~1 — where
the bands were `<rect>` elements the checks did not select at all, so both would have passed
on zero bands rather than failing. Worse, as written the second could not fail for any
input: the frame was computed as `max(dieNaked, …bands)`, so it was fitted to the very
members it was asked to contain. Both checks are rebuilt in §VII against the engine's own
stated stack height and measured in model inches; the sentence above them — that a check
run only against the code that passes it is not evidence — is the one this pass got wrong
about itself.

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


---

# VII. The adversarial audit, 26 August 2026

Four independent read-only auditors were run over the commit — on regressions and
consumers, on whether the new tests could actually fail, on second-order risk, and on
second occurrences of each fixed pattern elsewhere. Between them they found one thing that
made the plate wrong on twelve packs, one class of silent data corruption that this commit
made reachable, one denial of service, three checks that could not fail, and a claim in
§V above that was not reproducible. All of it is fixed below except where it says
otherwise.

## The datum was wrong on twelve of twenty-six packs — and the order tool still is

`projection_parts` means two different things in this corpus and no pack says which.
Measured across all 26 order packs at a 36-inch diameter:

| reading | packs | the shaft body's own `projection_in` |
|---|---|---|
| an offset **from the member's own naked** | 13 — every Doric and Tuscan | `0` |
| an absolute radius **from the axis** | 12 — every Ionic, Corinthian, Composite | exactly `r0` |

No pack lands between the two. The split runs by order and not by authority, across all
five authorities, which is the signature of two data-entry passes rather than of an
architectural distinction — and `check_orders.py` cannot see it because both readings are
internally consistent. That is now **OQ 65**.

Adding a naked to a figure that is already a radius draws the twelve at two radii: the
shaft's own apophyge, astragal and fillet standing a whole semidiameter clear of the shaft
they sit on — which is exactly the fault §I claims to have fixed, reintroduced by the
correction. It shipped green because `Proportions.jsx` defaults to `gibbs-doric`, which is
one of the thirteen, and the walk never changed pack.

The plate now reads the convention off each pack's own shaft: the shaft's outer face at
its foot IS the column's radius, so whichever reading puts it at `r0` is that pack's
reading. That is a derivation from the corpus's own definition, not a guess, and
`tests/test_drawn_labels.py` fails if any pack ever lands between the two. Where a
radius-convention pack records a projection of `0` — eight assemblies do, including
`palladio-corinthian`'s whole cornice — that is an **absent figure, not a flush face**: the
band is drawn at its naked and the plate says on the sheet how many of its own edges the
pack does not give, rather than drawing a cornice that recedes behind its own column.

**`dist/orders.html` still has the fault**, in `buildGeometry`, which is where the rule was
copied from. It is named in OQ 65 and deliberately not fixed here: the order tool is a
separate shipped artefact with its own moulding-profile geometry, and changing its datum is
a change to a drawing nobody asked about in a pass that was asked about two others.

## A click was a silent record edit, and this commit made it reachable

`DragHandle`'s `pointerup` committed unconditionally, with no movement threshold. A press
and release with zero delta still ran `Math.round(size * 2) / 2` — quantising an off-grid
dimension to the half-foot — and then snapped it up to 0.75 ft to the nearest bay line,
from a gesture nobody made. It writes the *placement's* dimension onto the *declared*
record and persists it to `localStorage`, so a stray click baked the solver's own
relaxation in and the sheet's `△` marks quietly went away with it.

The code is pre-existing and untouched by the diff. What the diff changed is that the
handle was previously painted over by the partition on the very wall line it was offered
for, so the gesture could not be started at all — §IV called that a dead affordance and
made it live, without noticing what the paint had been covering. A movement threshold now
gates the commit, and the walk presses and releases the handle without moving to prove it.

## A room name was a denial of service

`_fit_lines` searches every arrangement of the name across up to three lines: `C(W-1, 2)`
splits each costed over all `W` words, which is `O(W³)`. Measured: 400 words 9.2 s, **800
words 73 seconds of pure CPU**. Nothing bounds a room's name — `schema/plan.schema.json`
types it as an unconstrained string, `POST /api/drawings/{kind}` takes the plan record
verbatim, and the endpoint is synchronous, so a handful of such requests starves the whole
thread pool. The browser mirror in `label.js` freezes the tab on the same input.

Both are capped at twelve words, past which the name is chunked rather than balanced —
linear, still drawn whole, still shrunk to fit. 4000 words now costs 0.003 s, and the
suite pins it.

## The void disclosure, dropped by the fix that was supposed to make labels honest

OQ 55's `open to sky` / `roofed, unheated` rode on the dimension string as a tail. Because
the tail *lengthens* that string, the new fit dropped the whole line for any room under
about 19 ft wide — which is every loggia and every piazza in the catalogue. `test_voids.py`
kept passing because its courtyard fixture happens to have a 20-ft court. It is its own
line now, with its own size and its own floor, drawn for every void whatever else fits.

## Pattern C survived in the file the pass fixed it in

A computed value written as an SVG **presentation attribute** is beaten by any class rule
in the same document's `<style>`. §IV fixed `font-size` on the room labels and walked past
three more in the same and neighbouring files:

- `render_plan.py` — the relaxation banner's copper-vs-verdigris and the **infeasibility
  alarm's** `fill`, both discarded, so a proven-infeasible plan was captioned in the same
  quiet grey as everything else. The comment above that line reads *"the label is data, not
  decoration."* It was decoration.
- `render_plan.py` — every interior room outline drawn at the building perimeter's own
  weight, because a `stroke-width="1.0"` lost to `.wl`'s 2.2, in a system whose entire
  grammar is line weight.
- `render_plan.py`, `render_section.py` — both scale bars drawn as partition and floor
  lines rather than in brass.
- `render_section.py` — the sheet's own legend promises `RED = SPAN EXCEEDS CAPACITY` and
  the failing span's figure was drawn grey.

All five are fixed, and `tests/test_drawn_labels.py` now asserts the general form against
the document rather than against a list of known sites: for every property a class sets, no
element carrying that class may also set it as an attribute.

## Pattern B survived one surface over

`Transcription.jsx` drew every traced room's name at a **constant 1.35 model feet** with no
reference to the room's width at all — the pre-fix `Sheet.jsx` bug, worse, on the surface
whose whole business is turning a drawing into a record. It uses the same fitter now.
`render_elevation.py`'s refusal card printed `[:140]` of a ~660-character note, mid-word,
with no ellipsis, into a box wide enough for ~138 — two amputations stacked, on the one
drawing whose entire content is the refusal. It wraps and the card grows.
`render_roof.py`'s legend was wider than its own canvas on any house under ~56 ft, so the
reader was never told what the red dot means; the canvas is sized to hold it.

## Three checks that could not fail, and one that lied about its own history

Rebuilt in `walk.mjs`, all measured in **model inches off `getBBox`** rather than in screen
pixels — the plate is fitted to its pane, so a real gap at a small fit factor read as under
the old two-pixel tolerance. The frame is compared against the engine's stated stack
height, not against the drawn extent, because a frame derived from the bands can never be
smaller than the bands. Bands are addressable (`data-asm`, `data-member`), the confidence
outline is marked so a band count is a band count, and the plate checks run over **three
packs, one of each reading**, because checking only the default is how a datum wrong on
twelve packs shipped green.

Two more the audit caught in passing, both real:

- The magnify check asserted that a toolbar had rendered. Made to measure the SVG, it
  failed: **two presses of `+` moved 93% to 93% to 100%**, because `fit` had been put in
  the ladder as a rung and the first press stepped onto a rounded copy of where the reader
  already was. `fit` is a floor now, not a rung.
- A second press within a render of the first landed on the same rung, because both
  handlers closed over the `z` of the render that created them. The ladder is walked from a
  ref.

## The walk ran nowhere

`e2e/walk.mjs` was in no CI job — `CLAUDE.md` described it as a guard and nothing enforced
it. `workbench/scripts/walk.sh` serves the built app and runs it; the workbench job runs
that after the smoke test, and `playwright` is a devDependency so the browser resolves on a
runner as it does here.

## Fixed without ceremony

The loupe's window listeners are torn down on `pointercancel` and on unmount, not only on
`pointerup`; the swallow-click is armed on `window` and disarmed on the next tick, because
a pan very often ends outside the pane and a `once` listener bound to the scroller was
never spent and ate the reader's next real click; `overscroll-behavior: contain` is gone,
which had trapped the page wheel under a two-thirds-of-a-screen pane with the rules table
below it; the anchor correction moved from a `requestAnimationFrame` racing React's commit
into a layout effect that also accounts for the centring margin; `fit` is no longer clamped
to the ladder's floor, which used to leave a very tall plate "fitted" with its foot off the
bottom and the `fit` button disabled; a pan sets `user-select: none` and the cursor reads
`grab` when there is something to pan; the label cache is bounded; the Proportions grid
drops to one column instead of overflowing at the app's own minimum width; the Drawing
Set's caption gets the same zero-width-space treatment as the sheet's; and the `column`
payload ships the one field the plate reads instead of five, one of which was a paragraph
of prose.

## Deliberately not fixed

- **`dist/orders.html`'s datum** — named above and in OQ 65. A separate artefact, a
  separate drawing, and its own profile geometry to re-verify.
- **`export_dxf.py`'s room text**, centred by a character count against a hardcoded
  40-inch offset. It is a real DXF on its own annotation layer that a drafter moves; the
  fix wants the DXF layer's own pass.
- **`Sheet.jsx`'s lot labels** can leave a viewBox whose left and right margins are frozen
  while its top and bottom grow with the lot. Dormant — neither shipped plan declares a lot
  depth — and it is `render_plan.py`'s `extra_left` that shows how it should be done.
- **`build/template.html`'s tradition headers** lose their per-tradition colour to a class
  rule, in the built `dist/taxonomy.html` too. Same pattern, a different layer, and it
  should go with a taxonomy pass rather than be smuggled in here.
- **ctrl/cmd-wheel captures the browser's own zoom gesture** over the plate. It is the
  convention every canvas uses, the `−`/`+`/`fit`/`1:1` keys are the keyboard-reachable
  path, and changing the modifier is a call for whoever owns the interaction, not a bug fix.
- **`tests/test_solver.py::test_check_plans_solve_with_stated_downgrades`** still fails on
  this machine at 16 downgrades against a pinned 8, as it did on the pristine tree before
  any of this. CP-SAT wall-clock nondeterminism, named in the test's own docstring, and
  somebody's finding rather than this pass's to bury.
