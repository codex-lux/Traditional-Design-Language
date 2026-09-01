# WP-9.4 — The unit of composition was not the problem

*Four hypotheses, measured. Three refused. The refusals are the finding.*

**Raised by Lucas, 1 September 2026**, and ruled by him as the centrepiece of Phase 9:

> I think it's because it's still being procedurally generated at a lower level than the idiom
> […] the unit of room organization is already established, and that you're playing with units
> at a higher level of sense-making.

The package was scoped to build `parti_slice()` — a stated macro-tree for the centre-passage
family, on `courtyard_slice()`'s precedent — so the solver would compose from established units
instead of placing rooms one at a time. Lucas ruled three design questions in advance (passage
plus quadrants; `exterior_walls` promoted to structure only inside a stated tree; refuse the
tree and fall back when the diagram cannot hold the brief) and then, when the first measurements
came in, ruled **"both, in order"** — fix the objective first, re-measure, and build the tree
only if the arbiter still shows the incoherence.

It does not. Here is what the measurements say instead.

---

## The baseline of record

21 partis, each composed against its own first native style with `check_partis` check 10's own
brief (2,600 sf / 3 bed / 2 bath / entrance S), placed on the **heuristic** at seed 7 —
deterministic, and reproduced byte-identically across two runs. Judged by the WP-9.1 arbiter.

| | fatal | serious | minor | rooms below floor | rooms over ratio | landlocked | no window |
|---|---|---|---|---|---|---|---|
| **HEAD** | **114** | **1078** | 1113 | 86 | 131 | 10 | 61 |

Not the two shipped reference plans, deliberately: three of WP-8.6's four worst findings were
byte-identical on both of them, which is why a 21-parti population is the instrument here.

---

## 1. THE STATED TREE IS REFUSED, BECAUSE IT IS ALREADY STATED

`slice_rect`'s spanning branch (`geometry.py:344-388`) **is** the centre-passage macro-move and
it fires today: `spanning()` selects a `function_class: circulation` room declaring an opposite
exterior-wall pair and lays it as a full-depth slab.

Measured on `plans/tidewater-georgian-careful.json` over **3,000 candidates: two distinct
east/west room signatures**, 2,999 of them identical (`west = dining, drawing, kitchen`). The
quadrant assignment is not being searched — it is already fixed. What varies is the passage's
*position* (x from 20 to 30) and its width (9.40 to 11.00 ft), which is precisely what a stated
tree would freeze. And that position is load-bearing: bucketed under the real objective the
argmin is x = 20 at 714.6, while the centre-line bucket is about 100 points worse. **The shipped
Tidewater passage sits five feet west of centre and is right to.**

A probe that built the stated tree anyway improved the search's own score by 9.4% and took
**fatal findings from 3 to 8**.

There was nothing left for `parti_slice()` to state, and stating it again measured worse.

## 2. WHAT THE OBJECTIVE COULD NOT SEE — and this half earns its place

`level_score` charged a **universal hardcoded** `if ar > 2.6: s += (ar - 2.6) * 6`. Measured over
the 60 room records: **54 declare `dimensions.proportion`; 43 of those have a ceiling BELOW 2.6**
(median 2.0), and the 11 above it are exactly the rooms meant to be long — `gallery-corridor`
12.0, `centre-passage` 5.0, `entry-porch` 5.0. So the constant was looser than the corpus on four
room types in five, and charged the other eleven for being what they are. A passage paid 8.9
points for its own proportion.

`geometry.band()` has read `dimensions.area_sf` from that same dict since the catalogue was
written. **It read one key of three.** Lucas ruled the bands bind at their stated ceiling, per
room type, exactly as written — the corpus deciding rather than the code, and no threshold
authored.

Measured, all rows including the clamp fix of §4:

| | fatal | serious | rooms below floor | rooms over ratio |
|---|---|---|---|---|
| A: constant 2.6, no width charge | 127 | 1106 | 100 | 132 |
| **B: corpus bands, no width charge** | **119** | **1091** | 100 | 134 |
| C: constant 2.6, width 6 | 128 | 1079 | 89 | 127 |
| E: corpus bands, width 6 | 124 | 1077 | 90 | 123 |

**Reading the corpus beats the constant at every setting** (127 → 119 with no width charge,
128 → 124 with one). That is the one change in this package that is better on every axis it was
meant to move and worse on none.

## 3. THE WIDTH-FLOOR CHARGE IS A TRADE, NOT A WIN

`dimensions.width_ft[0]` is stated by 58 of 60 room types. It is what `compose.repair()` already
widens a room to and what `plan_check`'s room layer already convicts a record on; the placer was
the one reader of that dict that could not see it. Charging it does exactly what it was built to
do, and costs something else:

| width weight | fatal | serious | rooms below floor | rooms over ratio |
|---|---|---|---|---|
| 0 | 119 | 1091 | 100 | 134 |
| 2 | **118** | 1088 | 98 | 133 |
| 6 | 124 | 1077 | 90 | 123 |
| 14 | 126 | 1065 | 84 | 119 |
| 30 | 135 | 1052 | **69** | **111** |

Rooms drawn below their own floor fall **monotonically, 100 → 69**, and rooms over their
proportion band **134 → 111**, while fatals rise. The mechanism is not mysterious: widening a
cramped room takes wall from its neighbour, which breaks a shared-wall door contact, which makes
a room unreachable. The term is not inert and it is not free, and the setting is a ruling rather
than a sweep result — see the open question.

Note the shape of the fatal column: 119 → 118 → 124 → 126 → 135. **Worse in the middle of its
range than at the bottom, and worst at the top.** WP-7.4 published exactly that hazard for
`SPAN_W` and it recurs here, which is why zero and both extremes were swept.

## 4. THE CLAMP FIX REMOVES A SHIELD, AND THE SHIELD WAS DOING WORK

`slice_rect`'s cut clamp `max(module*0.6, min(extent - module*0.6, v))` **inverts** when
`extent < 1.2 * module`: the inner `min` returns less than `module*0.6`, the outer `max` returns
`module*0.6`, which exceeds the rectangle, and the second child is handed a NEGATIVE dimension.
Measured over 3,000 Tidewater candidates: **670 layouts (22.3%)** contain at least one
negative-dimension room, and **72 break the exact-tiling identity** by more than 0.5 sf — the
identity `over_band()`'s published refusal rests on.

`_clamp_cut()` fixes it, and is byte-identical where the old expression was already correct.

**And fixing it costs 13 fatals (114 → 127).** Checked directly: **no winning placement at HEAD
contains a negative-dimension room, on any of the 21 partis.** The bug never reached a sheet —
it was silently *eliminating* 22% of candidates, and those candidates were the cramped ones.
Repairing the geometry admits them to the competition, where some now win.

That is this codebase's own trap, in its own words: *a fix that removes a shield is a fix that
has to look at what the shield was covering.* The shield was covering an area-allocation problem
the slicer cannot solve — a rectangle too narrow to hold the rooms assigned to it. The width
charge of §3 is the honest replacement for the accidental filter, which is why the two belong in
one package.

## 5. READING THE GRAMMAR FOR DOOR MEANING CHANGES NOTHING, AND THE REASON IS THE FINDING

Lucas ruled that a door is a hard adjacency where `openings/grammar.json` dimensions it as a real
opening, and a connectivity wish otherwise — reading the grammar he had already authored over all
1,890 room pairs rather than inventing a rule. The grammar draws that line itself: `open`
(5.0–6.5 and 6.0–10.0 ft), `double` (5.0–6.0) and `cased-opening` (4.0–6.0) are openings two rooms
can only have by being one architectural volume, while a `swing` at 2.0–3.7 ft is the
connectivity case. `openings.required_wall_ft` — this corpus's one spelling of how much shared
wall an opening needs — supplies the scale.

It produces charges that differentiate exactly as the corpus states:

| pair | charge | the grammar's reading |
|---|---|---|
| centre-passage ↔ stair-hall | 25.8 | `open` — *"a stair hall a visitor must open a door to reach cannot be visible from arrival"* |
| drawing-room ↔ library | 24.8 | `double` — the formal enfilade |
| kitchen ↔ breakfast-room | 20.8 | `cased-opening` — *"any separation defeats the informality that is the room's purpose"* |
| centre-passage ↔ drawing-room | 15.8 | `swing` |
| bedroom ↔ closet | 11.8 | `swing` |

And measured across the 21 partis it moves **nothing**:

| | fatal | serious | rooms below floor |
|---|---|---|---|
| doors = flat 14 | 119 | 1091 | 100 |
| doors = the grammar's own weights | 119 | 1097 | 102 |

**Because the heuristic cannot act on the distinction.** Its floor is 12 broken door-ends over
4,000 candidates on the Tidewater ground floor; CP-SAT achieves **0 of 30**. Re-ranking which
doors matter cannot help when no candidate in the pool satisfies any of them. A scoring change
cannot repair a structural impossibility — which is OQ 55's finding in a second place, and the
reason `courtyard_slice` exists at all.

## 6. WHAT THE FATAL COUNT ACTUALLY MEASURES

Decomposed rather than assumed: of 123 fatals across the 21 partis, **121 are one finding —
"X cannot be reached from outside the house on the drawing"** — and 2 come from the fault layer.
Not the door score term: its consequence. Rooms you cannot walk to.

So every number in the fatal column of every table above is dominated by a single structural
defect of the guillotine slicer, which no weight in this package can move, and which the other
engine does not have.

---

*Sections 7 (the engine measurement), the refusals list, the open questions and the verification
record are completed below once the heuristic-versus-auto ledger lands.*
