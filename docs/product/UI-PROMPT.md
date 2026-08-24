# Prompt Doc — Traditional Design Language Workbench

*Paste into Claude Design. Self-contained: everything needed is inline, because the tool will
not have the repository. §0 is the short brief; §1–§10 are the material; §11 is the per-screen
task list; §12 is how to judge the result.*

*Companion: `UI-SPEC.md` — the full product spec, if the design tool can read files.*

---

## 0. The brief, in one paragraph

Design **the Workbench** — a desktop instrument for a plan-development lead at a production
home builder. It sits on top of a system that encodes four centuries of traditional building
practice as an executable language: 164 architectural styles as a graph, 95 universal element
slots, 36 proportioning systems implemented as functions, 58 room types with real furniture
clearances, and **209 named, testable errors** — the things that read as *wrong* to someone
fluent even when no written rule was broken. Given a brief (area, bedrooms, lot, style,
household), the system composes four contrasting floor plans, criticises each across fourteen
layers, places them on a structural bay grid, and generates a composed front elevation. What
it has never had is a human interface: it runs on a command line. Design that interface.

**Ten surfaces. Dark drawing-office palette. A persistent AI rail. And one non-negotiable
rule that shapes everything: this system distinguishes *failed*, *passed* and *could not
evaluate*, and never collapses the third into the second — so a two-state green-tick /
red-cross design is wrong here.**

---

## 1. The thesis (design the interface to make this argument)

**A traditional house is a sentence in a language, and the language can be written down.**

- Elements are the **alphabet** — 95 universal slots every style draws from and none owns.
- Proportioning systems are the **grammar** — 36 packs that are functions, not tables: give
  one a module and a context and it emits a fully dimensioned assembly, member by member.
- A style is a **vocabulary** — a set of bindings and constraints on that universal alphabet.
- A plan is a **sentence**; a grouping is a **phrase**; a parti is a **sentence pattern**.
- And there are **solecisms** — 209 named errors. This is the layer most systems omit and it
  is the whole differentiator. A system that generates houses but cannot recognise its own
  solecisms produces what Chomsky called *colorless green ideas sleeping furiously*:
  syntactically valid, and dead.

The point is not to automate the architect out of the room. It is to make **fluency scalable** —
so a production builder can build a house that *belongs* to its place, its climate and its
lineage without a senior classicist standing over every drawing.

The compiler metaphor is exact and you may use it in the interface's own language: the schemas
are the language specification, the checkers are linters, the validator is the type checker,
the composer is the front end.

---

## 2. The user

A **plan-development lead** at a production builder. Owns a catalogue of plans. Fluent in
plans, framing, cost and code — **not** in classical proportion or period detailing. Reads a
floor plan faster than a paragraph. Judged on plans that sell, price, permit and build.

What they say:

1. "Give me four plans for this lot and this buyer, and tell me what's wrong with each."
2. "Why is this plan wrong? Show me, don't lecture me."
3. "What does this style require, and what does it forbid?"
4. "What will this cost me to get wrong?"
5. "Get it out in a format my drafter opens."

They will not tolerate: being told a plan is good when it isn't; a rule without its exception;
a number with no source; a tool that hides how it decided.

---

## 3. Nine principles that must survive contact with the visual design

**P1 — Unjudged is not passed. Three states, never two.**
Every check reports evaluated-and-failed, evaluated-and-passed, or **could-not-evaluate**, and
is forbidden from collapsing the third into the second. Of 660 style constraints, **295 carry
no test at all** — the sources simply do not determine them. Those are not gaps; they are the
moments the tool hands the decision back to the human, and they are the most valuable
interactions in the product. *"A rules engine that cannot admit ignorance will produce houses
that violate no constraint and are still dead."* **The unjudged mark must not be a colour** — a
colour will be read as a verdict. Give it a form: open, hatched, or outlined, in neutral ink.
This is the single most important visual decision you will make.

**P2 — Provenance is a column, not a tooltip.**
A style resolves its kit through a chain of ancestors — Tidewater Georgian through 29 levels,
one log house through 34 — and every value shows which ancestor supplied it. Every number
carries a `kind`: **`measured`** (1,166 of them), **`editorial`** (216 — an honest judgment
call, marked as one), `derived` (163), **`invented`** (14 — no precedent exists), `code` (10).
Fourteen invented values out of 1,569 is a claim about integrity. Make it visible enough that
the number stays small.

**P3 — Refusals are content, not errors.**
The composer refuses on purpose. It will not invent a room the parti has no place for. It will
not present an assumption as a fact. **It will not tell you a plan is good.** A refusal gets a
card at the same visual weight as a result — never a toast, never a red banner, never an empty
state.

**P4 — Four candidates, never one. No winner's badge.**
Rank them; never crown one. And **`trades away` sits adjacent to the score at all times** — the
honest cost of each diagram travels with its number, or the number lies.

**P5 — Exceptions before rules.**
Faults hang off elements, not styles, because the half-width shutter is wrong on every house
that has shutters. Style enters through **846 exceptions**. A Georgian five-foot portico is
fatal by Craftsman rules and correct by its own. When a fault is exempted for the style in
view, the exception renders *above* the general rule.

**P6 — The drawing is a render of the data.**
Nothing is drawn that is not in the record, so the drawing and the data cannot disagree. Click
any line, room, window, dimension or hatch and get the record that produced it. **There is no
decorative linework in this product.**

**P7 — Compromises are counted, and they appear on the drawing.**
The solver counts every cut that falls off the structural bay line, because such a cut is a
joist run that does not land on a bearing wall. A real report reads: *"11 upper wall lines do
not continue to a wall below; each is a transfer beam."* Eleven transfer beams is a number a
builder prices. Mark them **on the drawing, at their location.**

**P8 — Cost is the builder's language.**
32 faults carry what was saved by getting it wrong. Every fault carries three tiers of fix —
**`right`, `cheap`, `dishonest`** — named that plainly on purpose. Show all three; the `cheap`
one is what actually gets built. And note the tone: of 209 fault causes, 57 are cost, 31 stock
sizes, 31 trade sequence, 29 catalog defaults, 25 code — and **exactly one is ignorance.** This
system explains an economy; it does not scold a builder.

**P9 — Massing is not style. Rooms are not style.**
An American Foursquare can be dressed Craftsman, Colonial Revival, Prairie or Mission with no
change to the volume. Never let a style filter silently constrain the massing or room
catalogues.

---

## 4. Voice — read this and match it

This is a real fault record's `symptom` field. It is the product's voice:

> **The Four-Foot Porch** *(aka "the porch you cannot sit on", "the rocking-chair test")*
> A porch that runs the width of the house, has columns, a rail, a ceiling and a roof, and is
> 4 to 6 ft deep. Nobody can sit on it: a rocking chair is 30 to 34 in deep and needs 12 to 18
> in behind it to rock and 30 in in front of it to pass, so a 5 ft porch with a rail on one
> side and a door swinging out on the other has no usable dimension left. It is furnished, if
> at all, with two chairs pushed against the wall and a table nobody can reach. The house
> advertises an outdoor room and does not provide one.
>
> **Cause — driver: cost.** Porch depth is the cheapest thing on a set of drawings to reduce
> and the last thing anyone measures… **Cost saved: about 90–180 USD per sq ft, so 3 ft of
> extra depth on a 30 ft front is roughly 8,000–16,000 USD.**
>
> **Fix (cheap):** Trade width for depth at constant area, which costs nothing. A 30 ft × 5 ft
> porch and a 19 ft × 8 ft porch are the same 150 sq ft and the same roof area.

Specific. Dimensioned. Dry. Shows its arithmetic. Never sentimental, never scolding.
**Your typography must be able to carry a paragraph like that** — this is not a
badge-and-chip screen. Fault names are typeset, because a builder will say them out loud.

Other names in the corpus, for flavour: *The Half-Width Shutter · The Square Window · The
Chimney That Is Not One · The Cardboard Gable · Dormers Off the Rhythm · The Blank Wall On The
Public Side · The Hatch In The Twelve-Foot Room · Flemish bond that cannot exist · A Light
Count The Glasshouse Could Not Have Supplied · The Stovepipe · The Truss Default · The Front
With No Centre.*

---

## 5. The visual system — extend what exists

Two tools already ship with a coherent language (an interactive phylogeny and a live
order-drawing tool). **Carry it forward.** These tokens are verbatim from the shipped files:

```css
--ground:#0B1B29;  --ground-2:#0F2536;  --ground-3:#14304a;   /* deep ink blue */
--rule:#24455E;    --rule-soft:#1A3549;                        /* hairline borders */
--ink:#EDE7DA;     --ink-2:#9FB3C2;     --ink-3:#63808F;       /* warm ivory → cool grey */
--copper:#C4734A;  --verdigris:#7FB3A3; --brass:#D8B26A;  --iron:#C4553A;
--t0:#D8B26A; --t1:#7FB3A3; --t2:#8FA8D8; --t3:#C4734A; --t4:#CFA2C4;  /* five traditions */

--display:"Bodoni Moda", 'Didot', Georgia, serif;   /* titles, style names, fault names */
--body:"Archivo", system-ui, sans-serif;            /* prose */
--mono:"IBM Plex Mono", ui-monospace, monospace;    /* every number, id, dimension */
```

Existing conventions to keep: mono eyebrows at ~10px with `.16em` tracking, uppercase · italic
brass for the emphasised word in a title · **hairline rules instead of shadows** · a ~236px
left rail · body at 14px / 1.55 · no rounded corners beyond 2px.

**Why it fits:** deep ink-blue with warm ivory is a drawing office at night; Bodoni is a
plate-engraving face contemporary with the pattern books this corpus is built from; and copper,
verdigris, brass and iron are *building materials* that each age the way their name does. The
palette makes the same argument the corpus does.

**Semantic assignments to establish:**
- `--iron` #C4553A → **fatal** · `--copper` → **serious** · `--brass` → **minor** ·
  `--verdigris` → **cleared / passing**
- **unjudged → no colour, a form** (P1)
- `forbidden` → its own unmistakable treatment. 223 forbidden bindings and 851 forbidden
  variants are **positive knowledge**, not absence: *"gambrel — Northern and Hudson Valley.
  Effectively absent in the Chesapeake."* That is a fact, and the easiest thing for a UI to
  lose.

**Drawing conventions.** Plans and elevations are architectural drawings, not charts: line
weights that mean something (cut / seen / hidden / grid), poché or hatch at cut walls,
dimension strings with **ticks not arrowheads**, architectural dimensions (`8'-0"`, `2'-8"`,
never decimal feet), a real scale bar, a north arrow, bay lines as a distinct lighter grid.
**Consider inverting the drawing surface to a light ivory ground inside the dark instrument** —
a measured drawing on paper, lit. It makes the drawing the brightest object on screen, which
it should be.

---

## 6. The exact vocabularies to render (do not invent parallels)

**Finding severity:** `fatal` · `serious` · `minor` · `advisory` · `info`
A real header for one ordinary plan: `fatal 4  serious 70  minor 59  advisory 1  info 13`.
**Serious findings dominate by an order of magnitude — density is a hard requirement.** A
design that gives each finding a card produces a 130-item scroll.

**Finding layer** (the second axis, and the primary organiser):
`room` · `furniture` · `daylight` · `circulation` · `adjacency` · `privacy` · `servicing` ·
`grouping` · `code` · `style` · `fault` · `elevation` · `plan` · `info`

**Kit slot binding:** `specified` · `extends` · `forbidden` · `open`
**Variant status:** `canonical` (1,085) · `permitted` (580) · `atypical` (87) · `forbidden` (851)
**Massing affinity:** `canonical` · `common` · `possible` · `atypical` · `forbidden`
**Parameter kind:** `measured` · `editorial` · `derived` · `invented` · `code`
**Fault severity:** `fatal` (25) · `serious` (155) · `minor` (29)
**Fault frequency:** `endemic` (147) · `common` (59) · `occasional` (3)
**Fix tiers:** `right` · `cheap` · `dishonest`
**Confidence:** `high` · `medium` · `low`

**Lineage edges — and this distinction is the most important in the whole project:**
`descends_from` and `regional_of` **carry** the inheritance cascade.
`references`, `reacts_against` and `revives` **do not**.
Greek Revival *references* Periclean Athens — no American builder had a line of transmission
from Greece. It *descends from* Federal carpentry — the same carpenters, the same shops, the
same author publishing a Federal manual in 1806 and a Grecian one in 1830. Only the second
transmits practice. **Two edge kinds, two visual treatments, weight not just hue.**

**Eight slot groups** (the Kit's primary navigation): `massing-and-roof` (13) · `envelope` (18)
· `openings` (17) · `classical-apparatus` (8) · `threshold` (7) · `interior` (15) ·
`plan-logic` (10) · `site` (7)

---

## 7. Real data — design against these, not against lorem ipsum

**A brief:**
```json
{ "style": "tidewater-georgian", "target_area_sf": 3200, "bedrooms": 4, "bathrooms": 3.5,
  "must_have": ["library", "breakfast-room"],
  "context": { "climate_zone": "3A", "lot_width_ft": 120, "entrance_faces": "S",
               "jurisdiction": "IRC model text, advisory", "budget_tier": "custom",
               "garage_bays": 2 },
  "household": "Two adults, three children, one grandparent visiting often. They eat every
                meal together and want a room that can be shut.",
  "candidates": 4 }
```
*`household` is prose and must stay prose. "They eat every meal together and want a room that
can be shut" is the most design-relevant sentence in the file.*

**Composer output — note what it teaches:**
```
1. Side-Hall Town House        score 291.0   fatal 0  serious 30  minor 63
   3319 sf (3.7% off target) · footprint 24 × 54.0 ft in 3 bays
   why: NOT native to this style — the composer is borrowing a diagram
   trades away: Cross ventilation and daylight on two long walls. In exchange it halves the
                envelope, works on a 20 ft lot, and makes a street wall.
   ! Footprint deeper than about 38 ft — needs a double-pile section; interior rooms unlit.

4. Centre Passage, Single Pile  score 472.0   fatal 2  serious 32  minor 58
   why: native to tidewater-georgian; center-passage-single-pile is a canonical massing
   trades away: Floor area for a given envelope, and a great deal of exterior wall. In
                exchange every room has light and air from two sides.
```
**The lowest-scoring candidate is the one native to the style. The best-scoring one is
borrowed.** Score and rightness are different axes and the interface must not conflate them.

Closing line of every composer run, which should be furniture on that screen rather than a
footnote: *"A plan with no fatal findings is not therefore good. The corpus can tell you what
is wrong and cannot tell you what is alive."*

**Validator findings — note the shape: statement · why · fix:**
```
[fatal]   Dining Room adjoins Powder Room, which it should not.
  why: A lavatory door opening into or directly visible from a dining room is the single most
       avoidable plan error of the last forty years.
  fix: Separate them, or record the relation as 'not-visible-from' if the separation is real.

[serious] Laundry does not reach a walk in closet directly or across a hall.
  why: THE ADJACENCY THAT MATTERS MOST AND IS DESIGNED FOR LEAST. Clothing travels closet to
       laundry to closet and nowhere else.

[serious] Family Room is 20 ft deep against a 6.8 ft window head (lit from one side); useful
          daylight reaches about 15.3 ft.
  fix: Raise the head, light the far end from another side, or accept the back of the room as
       a service zone.
```
*Note that `fix` often says "**or record the relation as X if the separation is real**." That
is a real interaction — the user can answer back, asserting a fact the record didn't carry.*

**A resolved kit's cascade:**
```
Tidewater Georgian  [tidewater-georgian]
CASCADE  (nearest first)
   0  tidewater-georgian            24 bindings (8 specified, 16 extends, 0 forbidden)
   1  georgian-colonial-american    90 bindings (86 specified, 2 extends, 2 forbidden)
   2  american-colonial              4 bindings
   3  english-georgian               8 bindings
   …
  28  dutch-urban-gable-house       15 bindings
PROPORTION PACKS  (24 bound)
  brick-course        primary    from tidewater-georgian          prec 1
  gibbs-ionic         primary    from georgian-colonial-american  prec 1
  sash-light          opening    from georgian-colonial-american  prec 4
```

**A kit slot:**
```
roof_pitch   group: massing-and-roof   binding: specified   confidence: high
  pitch_min      7:12    rise_in_12   measured
  pitch_max      9:12    rise_in_12   measured
  pitch_typical  8:12    rise_in_12   measured
  pitch_degrees  30.3–36.9  deg       derived
  rule: "Rise:run between 7:12 and 9:12 — a full step shallower than the New England band,
         and the reason a Virginia house reads lower at the same width."
```

**A proportion comparison — always at a common column diameter, never a common module:**
```
                        vignola-doric    gibbs-doric
  column_height_in            8'-0"          8'-0"
  pedestal                    2'-8"          2'-6"
  frieze                        9"             9"
```

---

## 8. Scale — what the interface must survive

164 styles · **95 slots per kit** · 12,992 `open` bindings corpus-wide · 209 faults with 846
style exceptions · **660 constraints of which 295 are unjudged** · 58 rooms · 40 massings ·
16 groupings · 12 partis · 36 proportion packs with 158 recorded conflicts · a 29-level
cascade · **130 findings on one ordinary plan** · 322 image records of which **zero have
images**.

Two of these are design problems disguised as numbers:
- **130 findings.** Solve with grouping by layer, a severity threshold, and collapse — not
  pagination.
- **95 slots × mostly `open`.** The API defaults to specified-only for good reason. A flat
  list of 95 rows will drown the user.

---

## 9. Honest states the interface must render without embarrassment

These are real, current, and each is a design opportunity rather than a caveat to hide.

| State | Reality | What the UI must do |
|---|---|---|
| Unjudged constraints | 295 of 660 have no test | Third mark, always (P1) |
| No native parti | only 39 of 132 styles have one | "Borrowing a diagram" reads as a corpus limit, not a bad result |
| Solver is a hill-climb | not an optimiser; non-deterministic | "Re-solve" is an explicit action with candidate count exposed |
| Infeasible brief | returns the least-bad plan, **not** a named conflict set | Never imply feasibility was proved. Design the conflict-set display for when it lands |
| Elevation fault coverage | **83 of 177** applicable faults evaluated | A permanent, unembarrassed statement on that surface |
| Images | 322 records, **0 sourced** | Render the shot spec and alt text as the object. Not a broken thumbnail |
| Proportion bindings | 129 of 132; three deliberately unbound | A named exception with its reason, not a hole |
| Building code | advisory IRC model text | Labelled advisory, always. **Never rendered as compliance** |
| Export, guidelines, ingestion | not built yet | Design the surfaces; mark them forthcoming |
| Cost | 32 faults carry `cost_saved`; no costing engine | Do not imply one exists |
| Missing traditions | Japanese, Islamic, South Asian, African are absent peer trunks | An honest empty region in the graph |

---

## 10. The AI rail — persistent on every surface

A design partner in a rail beside the canvas (not a modal, not a separate page), driving 24
tools over the corpus: find and compare styles, resolve a kit, dimension a proportion pack,
search faults, evaluate measurements, list partis, validate a plan, compose candidates, place
rooms.

**Behaviour is the product, not the wrapper:**
1. **Every claim cites its record**, and the citation navigates the main canvas.
2. **It shows what it consulted** — a compact tool trace: *"read tidewater-georgian kit; 3
   faults on porch_depth."* Trust is built by watching it check, not by its confidence.
3. **It refuses out loud.** *"You asked for a garage; this parti has no place for one. Position
   matters more than presence."* A card, not a failure.
4. **It says which findings it could not evaluate**, every time (P1).
5. **It puts judgment questions back to the human** rather than filling them in. Asking one
   well is a feature.
6. It reads progressively — a short orientation first, deeper sections on request — and the UI
   can show it going deeper.
7. **It never calls a plan good.**

---

## 11. What to design — ten surfaces

Deliver a coherent set. Each entry names the job and the hard part; the hard part is where the
design is won.

**① Console.** Projects in flight, recent briefs, corpus health. *Hard part: making a landing
screen that is an instrument rather than a dashboard.*

**② The Phylogeny.** 164 taxa on a time axis spanning 700 BC – AD 2026, four ranks, both
hierarchies at once (the browsing drawer and the actual descent), typed edges with the
cascade-carrying ones structurally heavier, five traditions by hue, select-two-to-compare.
*Hard part: 90% of the density sits in 1600–2026 with a long classical tail — a linear axis
wastes most of its width. And a node routinely has several parents: Shingle Style has four
ancestors of comparable weight arriving by four different mechanisms.*

**③ Style Record.** One taxon: dates, geography, description, defining characteristics,
**diagnostic tells**, **`distinguished_from`** (disambiguation against nearest neighbours),
proportional system, massing affinities graded canonical→forbidden, constraints in three
states, exemplars, sources. *Hard part: tells and distinguished-from are the highest-value
content for the actual job — "is this Federal or Greek Revival?" — and deserve more room than
the description. Nine sections; show four by default.*

**④ The Kit.** 95 slots in 8 groups, resolved through the cascade, **with a source column
showing which of up to 29 ancestors supplied each value**, four binding states, four variant
statuses, parameters with their `kind`, the human-readable rule beside the number, the
authoring note, pack precedence, and the faults filed against each slot. *Hard part: the
cascade is a first-class object needing its own display, not a breadcrumb. And a thin kit is
correct, not incomplete — a style only states what its ancestors don't already give it.*

**⑤ Brief Intake.** The brief, the site (street bearing, setbacks, slope, prevailing wind,
party wall) and the household as prose. Live feasibility as it is typed. *Hard part: making
every blank field visibly become a decision-log entry — "3 fields unstated; the composer will
choose and tell you what it chose."*

**⑥ Candidate Set.** Four contrasting plans: score with its arithmetic exposed, finding counts,
area and % off target, footprint and bays, **`why`** (native or borrowed), **`trades away`**,
expansion warnings, top findings, and the decision log. *Hard part: rank without crowning, and
keep score and rightness on separate axes — the native diagram often scores worst.*

**⑦ Plan Workbench — the centre of the product.** The drawing with the critique on it. Bay
grid, walls, windows on exterior walls only, doors with swing arcs, dimensions, scale bar, lot
boundary, setback envelope, north arrow. Findings marked at their location, filterable by
fourteen layers and five severities. Level toggle with a ghost of the level below. Relaxation
markers in place with a running count. Toggleable overlays for wet stacks, daylight reach and
the six-rank privacy gradient. **Drag a wall on the bay grid and re-score. Switch the style and
watch the constraints change.** *Hard part: 130 findings must be legible, not a wall of red —
and the style-switch interaction demonstrates the entire thesis in three seconds, so design it
as a feature, not a debug affordance.*

**⑧ Drawing Set.** Front elevation (bays, a doorway composed to Gibbs, sash lights correct for
the declared date, one head datum per storey, a cornice regenerated as the style's own
entablature reduction at the real storey height), section, roof plan with ridges stepping down,
bearing-line diagram. *Hard part: overlay the governing proportion pack on the elevation —
turn the grammar from a table into a diagram — and carry the honest "83 of 177 faults
evaluated" statement without shame.*

**⑨ Fault Corpus.** 209 solecisms, element-first. Filter by slot, style, severity, frequency,
category and cause driver. Style exceptions above the general rule. Symptom as real prose,
cause with its cost, three tiers of fix, two severity axes (how it reads, how it lives), the
good/bad image pair where one exists. *Hard part: typography that can carry the Four-Foot Porch
paragraph in §4 without turning it into chips.*

**⑩ Proportions & Orders.** Any of 36 packs dimensioned at a real size, member by member, drawn
live — every line generated, none traced. Authority comparison at a common column diameter.
The 158 conflicts with building today, each with ranked honest and dishonest substitutions.
*Hard part: the non-classical packs — brick course, timber bay, sash light, storey graduation,
log module — are equal citizens. Most traditional buildings were proportioned from a material
module, not a column, and a UI that buries brick coursing behind the five orders
misrepresents the corpus.*

**Plus the cross-cutting components**, which are where coherence actually lives: the
three-state **judgment mark** · the **finding row** (dense enough for 130, expandable to full
prose) · the **provenance trace** (compact and full) · the **source chip** (measured /
editorial / derived / invented / code) · the **slot row** · the **variant pill** (a four-rank
ladder, not a binary) · the **candidate column** · the **fault card** · the **refusal card** ·
the **decision-log entry** (a receipt, never styled as a warning) · the **relaxation marker** ·
the **unsourced-image record** · the **edge glyph** · the **architectural dimension string**.

---

## 12. How to judge the result

1. A plan-development lead gets from **brief → four candidates → a critiqued drawing** without
   documentation.
2. **Unjudged is never mistaken for passed**, at a glance, anywhere.
3. Any number on screen reaches **its source and its `kind`** in one interaction.
4. A **130-finding plan is legible.**
5. **Switching style on a fixed plan** teaches the thesis in under ten seconds.
6. A **refusal reads as the system working.**
7. A builder recognises `cost_saved` and the `cheap` fix as **written in their language.**
8. **The prose survives** — symptoms, notes, trades-away and household descriptions are the
   product's soul and must not be compressed into chips.
9. A classicist can **audit and disagree.**
10. **Nothing implies a completeness the corpus does not have.**

---

## 13. Out of scope

Marketing site · auth and accounts · permissions · pricing · mobile-first layout (this is a
desktop instrument) · any screen that invents data the corpus does not carry · any screen that
renders a building-code result as compliance rather than advice.

---

## 14. If you only design one screen

Design **⑦ the Plan Workbench**, with the AI rail, at full fidelity — including the three-state
judgment mark, findings grouped by layer at real density, relaxation markers on the drawing,
and the style-switch interaction. It is the surface the user lives in, it exercises nine of the
nine principles, and every other screen inherits its components.
