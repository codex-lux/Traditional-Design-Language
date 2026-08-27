# WP-6.3 — Geometry truth: one change built, three refused, and the refusals are the finding

*26–27 August 2026. Tranche 3 of three. Branch `claude/floor-plan-design-issues-1x19t3`.*

## Why

WP-6.1 made the sheet honest about the placement. WP-6.2 gave the record something to be
honest about — openings with walls and positions, a stair, fixtures — and a `drawn` layer
that turned every one of Lucas's reported symptoms into a finding. What neither did was
change the placement. At the end of WP-6.2 the Tidewater sheet still said, loudly and
correctly, that eleven declared doors had nowhere to go and that three rooms could not be
reached at all.

This tranche was planned as four changes to the two placement engines. **Three of the four
were refused on measured evidence, and one of the three was refused because the defect it
proposed to fix does not exist.** The fourth turned out to fix the reported problem
outright.

Verifying that fourth change in a browser then turned up a fifth defect nobody had planned
for, and it is one of Lucas's own reported ones: the relaxation marks were not over walls.
That is the last section below.

## What was refused, and why

Each proposal was given to an adversarial reviewer whose instruction was to refute it. The
measurements below are theirs, re-checked here.

### The stair-stacking charge — REFUTED, both halves

The plan was to replace `vertical_score`'s dead stair branch (it assigns a variable and
discards it) with a real charge, and to add a hard CP constraint.

**In the heuristic it is inert at every weight.** `geometry.py` generates the upper level
with `slice_rect(copy.deepcopy(prep[1]), 0, 0, W, H, …)` — **no reference to the ground
placement at all**. The generator is blind, so a score term can only re-rank candidates
that were produced without knowledge of the level below; it can never produce a stacking
one. Raising the weight 100× and 10,000× produced **byte-identical output**, with
`primarybath` still short. What the charge did produce was relaxations 11 → 16, breaking
three pinned counts, and `under_band` 0 → 1. A tax the search pays forever and cannot act
on.

It would also have double-billed: `hallbath` is *already* charged 8 points by the
wet-over-wet term, and a `stacks_over` charge bills the same physical defect a second time
through a term that uses different geometry (centre-containment versus rectangle overlap).

**In the CP engine a hard constraint is unsafe.** The downgrade loop reads
`wall_keys = [key for _t, k, key in core if k == "wall" and key]` and breaks when it is
empty — **only wall pins are downgradable**. A stacking constraint would therefore be
non-downgradable by construction and would outrank every declared exterior wall in the
corpus. Measured on a conflicting case: it did not refuse, it **downgraded an authored
kitchen wall** and stated a refinement that blames the wall while never naming the
constraint that displaced it. An authored fact losing silently to an inferred one is the
OQ 52 family of error.

### The over-size penalty — REFUTED by an identity

The plan was to mirror `under_band` with an over-band charge. Because the slicer tiles the
footprint **exactly**, with `Σgot` fixed at the block area `T`:

```
Σ max(0, got − hi)  ≡  (T − Σ hi)  +  Σ max(0, hi − got)
   over-band excess      constant        unused headroom
```

That is an identity, verified to under 0.5 sf on both levels. **"Penalise a room over its
ceiling" IS "penalise a room under its ceiling", plus a constant.** It pushes every room
up; it does not oppose `under_band`, it amplifies it. On the Tidewater upper level the term
is 96.3% constant — an irreducible floor of 671 sf against 697 placed — with a coefficient
of variation across all 250 candidates of 4.67%.

Run through the whole search in three formulations (flat 12 a room, proportional, per
square foot): **not one room changed size**, and the score moved by exactly the predicted
constant.

Over-size is also **already charged**. `level_score` bills `abs(got − want)/want * 10`,
symmetric; the upper passage already pays 6.3 of it. What produces the +63% is that
`1/want` weighting deliberately routing unavoidable slack to the *largest* room — and an
over-band charge normalised by `hi` has the same gradient, so it would reinforce exactly
what it was meant to fix.

And the slack is the **record's**, not the placement's: the Tidewater upper storey is
programmed at 1,621 sf inside a block sized by the 2,405 sf ground floor. No placement can
absorb 784 sf. Six rooms on that plan are over their band ceiling **as declared, before any
placement runs** — the landing at 108 against 60, the hall bath at 88 against 70, the linen
press at 15 against 6, and the passage, powder room and second chamber besides. Charging for
any of it would convict the solver of the brief's arithmetic.

That six is *not* the five reported further down, and the difference is the point of
reporting both. Six rooms are declared over their ceiling; the placement then puts twelve
over theirs; five rooms are in both sets. The passage is declared at 408 against a 400
ceiling and is then placed *under* it. Two questions, two answers, and each now says which
one it is answering — in `over_band`'s docstring as well as here.

### The `_absorb` keep-out — REFUTED; the defect does not exist

OQ 55's precedent is real: the CP engine proved no upper room sat over the open court and
`_absorb` then grew one straight through it. The proposal was to extend that discipline to
door contacts and stair stacks.

It cannot happen. Every branch of `_absorb` moves exactly one face outward, and
`max(w, cap/h)` floors each candidate at the current extent, so **there is no shrink path**.
In the `-x`/`-y` branches the origin moves but `x_new + w_new = x + w` exactly — the
opposite face is algebraically invariant. Each pass replaces a rectangle with one that
strictly contains it. Two rooms that touch therefore cannot be separated: the shared face is
frozen (A's limiter finds B and sets `lim = B.x`, so the guard fails), and even if it were
not, both rectangles only expand, so their shared run is monotone non-decreasing.

Fuzzed over 4,000 randomised guillotine layouts plus the real solve: **78,936 door-scale
contacts, worst shrink 0.0141 ft**; **119,509 cross-level overlaps, worst 0.0142 ft** —
against a 0.4 ft tolerance, 28× the jitter, and the entire residue is `round(x, 2)` and
`round(w, 2)` rounding origin and extent independently.

**The general rule, which is the durable finding:** `_absorb` can violate a keep-out (an
upper bound on where a room may be) and can never violate a contact or a stack (a lower
bound on overlap). Growth is monotone, so lower bounds are safe by construction. That is
what OQ 55 actually established, and it is already fully enforced. Building the proposed
keep-out would have been inventing a defect in order to fix it.

## What was built

### The per-pair door floor — and it fixes the reported problem

`geometry_cp.py` required `min(4, max(2, floor(0.9 · min(maxside))))` feet of shared wall
for every interior door, under a comment saying it "scales to the smaller room: a linen
press's whole side may be 2 ft — its door is narrower than a parlor's, and demanding 4 ft
would refuse real closets."

**That branch has never once fired.** `maxside` is `max(width_ft, length_ft)` — the *longer*
side — so dropping below 4 needs a room whose long side is under 3.34 ft, and there are
**0 such rooms in all 16 plan records** (238 rooms measured). Every interior pair in the
corpus got a flat 4 ft. The 3 × 5 linen press the comment names got a parlour's
requirement, and so did `bed2cl`, which is literally 2 × 6. OQ 41's own text quotes the
same dead expression as though it described behaviour.

The floor is now the door's own leaf and its jambs — `openings.required_wall_ft`, the one
number both renderers and both exporters have measured against since WP-6.1 — taken from
the record, which supplies a width on **469 of the corpus's 471 doors**. It is capped at
what the smaller room can physically offer, so a wide opening between two small rooms
becomes a finding rather than an infeasibility. Per pair across the corpus: **102 tighter,
3 looser, 128 unchanged.**

The second copy mattered as much as the first. `hard_fact_violations` — the arbiter that
counts violations on the finished record — carried its own transcription of the old
expression. A second copy of a rule is how an arbiter comes to convict placements the
solver proved legal; both now call one function.

**Measured on `plans/tidewater-georgian-careful.json`, three runs each, deterministic:**

| | before | after |
|---|---|---|
| engine | heuristic (CP returned UNKNOWN at budget) | **cp-sat, OPTIMAL** |
| openings placed | 20 | **30** |
| declared doors with nowhere to go | **11** | **1** |
| rooms unreachable from outside | **3** (fatal) | **0** |
| rooms joined to nothing indoors | **1** (the kitchen) | **0** |
| fatal findings | **3** | **0** |
| relaxations | 11 | 13 |
| downgraded wall pins | — | 17 |

The kitchen has all six of its doors. The chamber bath has its door. The library and the
breakfast room are reachable. **Every access defect in the original report is now fixed
rather than disclosed**, and the one remaining unplaced door is `breakfast → terrace`,
whose other room the record puts on no level at all.

The counter-intuitive part is worth stating plainly: a *stricter* rule for most pairs made
the model **easier** to solve, because the flat 4 ft was demanding a parlour's shared wall
for every closet in the plan. Relaxing exactly the pairs that never needed it let CP-SAT
finish inside its budget on a plan it had never once solved.

**What it costs, stated:** 17 declared exterior-wall pins are downgraded, each with its own
refinement naming the room and wall, and the first of them is *proven* ("restored alone, no
placement exists"). CLAUDE.md's own standing trap already says what those pins are — *"a
plan's `exterior_walls` are aspirations, not rectangle edges … they are weights"* — so this
is trading a documented aspiration for a hard fact, in the open. Relaxations rise 11 → 13.

### The workbench stops running the weaker engine

`workbench/server/evaluate.py` and the Drawing Set endpoint both defaulted to
`engine="heuristic"`, chosen for latency behind a 400 ms debounce. **The sheet Lucas was
reading came from the fallback engine, and every access defect he reported was an artefact
of that.** All three now default to `auto` — the third being `app.py`, whose route default
shadowed the other two, so flipping either alone changed nothing a browser could see. The
fast path is still available to a caller that asks for it by name, and the wall drag is the
one caller that does, because a gesture cannot wait for a proof.

**The flip made the caption false, in the dangerous direction.** The paragraph under the
sheet said flatly that *"each edit re-scores on the fast search, which is a hill-climb and
not an optimiser … nothing it draws asserts that feasibility was proved."* True while the
default was the hill-climb; false the moment it was not — and a reader could no longer tell
a proof from a search, which is the one distinction that surface exists to keep. The caption
now reads `geometry_report.solver.engine` off the record and says which ran, names the
fall-back reason when `auto` tried the proof and did not get one, and `e2e/walk.mjs` checks
the claim against the API's own report rather than against a phrase. The re-solve tooltip
carried the same stale assertion and was corrected with it.

*(Corrected by WP-6.4: this section said "the caption", and in this codebase's vocabulary
that names the plate's own caption — `Sheet.jsx`'s and `render_plan.py`'s. What WP-6.3
actually changed was the page prose beside the plate, which is the one place the disclosure
cannot travel: a printed or exported sheet leaves it behind. Both plate captions carry the
engine line now.)*

### Two false claims corrected

`geometry_report.solver.hard` asserted "rooms at program size". The solve does prove that —
and `_absorb` then grows rooms to `max(1.20, fill × 1.22)` of programme area, measured at
1.22× on both ground levels and **2.27×** on one upper. The record shipped a proof of
programme size on a drawing that no longer held it. The cap is not the defect; the claim
was. It now says the drawn size is a floor rather than an equality.

And the `drawn` layer's divergence threshold said "more than a tenth" while testing `>= 10%`
— on this placement the kitchen and the library both land at *exactly* −10.00%, so the
boundary was live rather than hypothetical. Both sides now say the same thing.

### `over_band`, reported and not charged

A mirror of `under_band` in the report only, carrying `declared_over_ceiling` per room so a
reader can tell the two cases apart: 12 rooms over their ceiling on the Tidewater placement,
**5 of them over it as declared too**. (Six rooms are declared over their ceiling; the
passage is one of them and is placed under it, which is why that count is not this one.)
Reporting a room as oversized when the brief asked for it oversized would be the OQ 52 error
in a new place.

### The △ was not over a wall — and that is the "arrows pointing at anything and everything"

Lucas's sixth reported defect was *"the arrows over walls between spaces, I don't know what
they mean since they seem to point to anything and everything."* WP-6.1 read that as a
missing legend and gave it one. The legend was owed, but it was the smaller half.

`_count_relaxations` in the CP engine emitted `{off_ft, axis, at_ft, level}` and no extent,
under a note refusing to invent one: *"an edge here is a wall line shared by however many
rooms abut it, and inventing an extent for it would be a drawn claim nobody measured."*
Correct about the invention, wrong that there was nothing to measure — the counter is
looping over the room rectangles at the moment it finds the line, and it knew exactly which
faces lay on it. Both renderers, having no extent, fell back to a 5 ft tick **centred on the
plan**. So the marks were not over walls at all: they were drawn down the middle of the
sheet, wherever that happened to land.

On the Tidewater placement it landed inside the drawing room. The mark on the horizontal
line at y = 27 belongs to walls running x 51 → 60; it was drawn at x = 30, six feet clear of
any wall of the room it sat in, over that room's own name.

`runs` is the measured answer — the union of the room faces on that line, as disjoint
intervals, because a line may be a wall in two places with a doorway between them. The mark
is drawn along them with the △ on the longest. **A mark the solver can locate on no wall of
its own level is now named in the caption and not drawn**; the caption also stops claiming
"each marked △ where it falls" and counts what it actually marked.

The one-rule discipline holds: `relaxation_marks` (Python) and `relaxationMarks`
(`derive.js`) are checked against each other by both suites, and `e2e/walk.mjs` now measures
the drawn triangles against the drawn rooms — every △ within 12 px of a wall of any room it
falls inside. Nine marks on the Tidewater ground floor, none adrift.

**And it was eating clicks.** The dashed run is a hairline annotation with no handler, drawn
after the rooms, and `elementFromPoint` at the drawing room's centre returned *it* rather
than the room. The click that selects a room — and therefore the wall-drag handles the
caption offers — could not be made at all. Four e2e interaction checks had been failing since
the engine flip and were misread here as CP latency; a settle timer was written for that
wrong diagnosis and made things worse before the measurement was taken. The run now carries
`pointerEvents: none`; the triangle keeps its own, because it is a visible glyph with a
tooltip and clicking a mark is a thing a reader means to do.

Two lessons, both already in this project's ledger under other names: **an affordance
painted over is an affordance that does not exist** (CLAUDE.md's own wall-handle trap, in a
new place), and a failure whose cause you have not measured will attract a plausible fix for
the cause you assumed.

### Every `stacks_over` claim is checked

The drawn layer checked only stacks over the stair. It now checks every claim against the
room it names, across levels, and reports an unevaluable one as `info` rather than passing
it. On the CP placements one broken stack survives on each shipped plan — `primarybath` over
`butlers`, `hallbath` over `laundry` — each a waste stack with nothing under it.

## A process finding

**A verification agent left an experimental edit in the working tree.** The refuted CP
stair constraint was still in `build/geometry_cp.py` when the workflow returned, and a
second agent reported that its own baseline had been contaminated by it. It was reverted
before any of this work was written. Two lessons: an agent asked to *verify* will patch
files to measure, which is how it earned these numbers and is exactly why it must not be
trusted to leave the tree as it found it; and a measurement taken while somebody else's
experiment is in the tree is not a measurement of anything.

## What was deliberately not done

- **No stair-stacking charge and no hard stair constraint**, for the measured reasons above.
  The real fix is a generator that can see the other level while it slices, which is its own
  package (**OQ 82**).
- **No over-size penalty.** The identity above says it cannot work; the existing symmetric
  area term already bills it.
- **No `_absorb` keep-out for doors or stacks.** The defect does not exist.
- **`MIN_DOOR_OVERLAP` is kept**, as the fallback for a door that declares no width — two in
  the whole corpus, both exterior.
- **The `_shared` first-match-wins wart is recorded, not fixed** (**OQ 83**): under its own
  0.4 ft tolerance a degenerate corner contact can be reported on one wall before another,
  and a 3-inch corner kiss can read as a shared edge. It is 21× short of the narrowest door
  in the corpus, so nothing draws on it today.
- **The `_absorb` growth cap is left at `max(1.20, fill × 1.22)`** rather than tightened to
  `min(1.15 × declared, catalogue hi)` as the package text asked. The reasoning is in "Two
  false claims corrected" above — the cap is what stops a 2.8 sf linen press reaching 8, and
  an honest empty floor beats an inflated room — but it belongs here, in the refusals, where
  a reader scanning for what was skipped will find it. *(Added by WP-6.4's audit, which
  found it named only in a fix narrative.)*

*Added by WP-6.4's audit — two items this report should have carried and did not:*

- **`geometry_report.severed_doors {count, pairs}` was SUPERSEDED, not skipped.** The
  package asked for it and it does not exist. It was planned before WP-6.2, and WP-6.2 built
  the same thing better: `opening_report.unplaced` carries every opening the placement could
  not realise **with its reason**, both renderers banner it, the DXF exporter has stated it
  since WP-5.1, and `plan_check`'s drawn layer counts it. A second tally of the same fact,
  keyed differently, is how two counters come to disagree. `schema/plan.schema.json` was
  advertising the field to every consumer of the schema and has been corrected.
- **`under_band` was not compared against the declaration.** The package asked for it in the
  same breath as the over-size penalty, and only the over-size half was adjudicated — so
  `over_band` shipped reading the declaration (`declared_over_ceiling`) while `under_band`
  read only the catalogue band, and a room placed far under what the *brief* asked for was
  invisible unless it also crossed the looser catalogue floor. Built in WP-6.4. Measured on
  `spec-builder-colonial`: the dining room is 26% under its catalogue floor and **40% under
  its own declaration**; the foyer 49% and **64%**.
