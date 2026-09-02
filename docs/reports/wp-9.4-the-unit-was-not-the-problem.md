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

## 2. WHAT THE OBJECTIVE COULD NOT SEE

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

**READ §8 FOR THE MEASUREMENT, NOT THIS PARAGRAPH.** The first sweep of this change was taken on
a tree that also carried the clamp fix of §4 and a `spanning()` refusal that broke the shipped
reference plan, and it read 127 → 119 — an improvement that DOES NOT REPRODUCE once `spanning()`
is fixed. The corrected figure is neutral. The table is not repeated here; §8 carries it with the
tree state it was taken on, which is the only form in which a number from this package should be
quoted.

## 3. THE WIDTH-FLOOR CHARGE IS A TRADE, AND THE ONE TERM THAT MOVES WHAT IT AIMS AT

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

*(Swept on the same contaminated tree as §2's table — the ABSOLUTE figures are superseded by §8.
The SHAPE of the columns is what this section is about and it reproduces: monotone in what the
term targets, non-monotone in fatals.)*

Rooms drawn below their own floor fall **monotonically, 100 → 69**, and rooms over their
proportion band **134 → 111**, while fatals rise. The mechanism is not mysterious: widening a
cramped room takes wall from its neighbour, which breaks a shared-wall door contact, which makes
a room unreachable. The term is not inert and it is not free, and the setting is a ruling rather
than a sweep result — see the open question.

Note the shape of the fatal column: 119 → 118 → 124 → 126 → 135. **Worse in the middle of its
range than at the bottom, and worst at the top.** WP-7.4 published exactly that hazard for
`SPAN_W` and it recurs here, which is why zero and both extremes were swept.

## 4. THE CLAMP FIX REMOVES A SHIELD — REFUSED, see §9.2

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
the slicer cannot solve — a rectangle too narrow to hold the rooms assigned to it.

**It is REFUSED and left in the file uncalled**, with a third regression found after this section
was first written: it takes the entry porch from 10.0 × 6.0 ft to 5.0 × 8.3, dropping its clear
depth below the 6 ft `porch-nobody-can-sit-on` requires — a fault WP-7.4 had cleared. §9.2 has
the full account.

## 5. READING THE GRAMMAR FOR DOOR MEANING CHANGES NOTHING, AND THE REASON IS THE FINDING

Lucas ruled that a door is a hard adjacency where `openings/grammar.json` dimensions it as a real
opening, and a connectivity wish otherwise — reading the grammar he had already authored over all
1,890 room pairs rather than inventing a rule. The grammar draws that line itself: `open`
(5.0–6.5 and 6.0–10.0 ft), `double` (5.0–6.0) and `cased-opening` (4.0–6.0) are openings two rooms
can only have by being one architectural volume, while a `swing` at 2.0–3.7 ft is the
connectivity case. `openings.required_wall_ft` — how much shared wall
an opening needs, spelled deliberately three times and held to one contract by
`tests/fixtures/sheet_symbols/` — supplies the scale.

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

## 7. THE ENGINE, WHICH IS THE LARGEST FACT IN THIS REPORT

The same 21 partis, the same brief, the same arbiter — the only variable is which engine places
the house:

| engine | fatal | serious | **rooms you cannot walk to** | engines actually used | time |
|---|---|---|---|---|---|
| heuristic | 123 | 1078 | **121** | 21 × heuristic | 20 s |
| **auto** | **36** | 1051 | **34** | 16 × cp-sat, 3 × heuristic, 2 × least-bad | 438 s |

**Fatals fall 123 → 36 and unreachable rooms 121 → 34 by changing nothing but the engine.**
Decomposed rather than assumed: of 123 fatals on the heuristic, **121 are one finding — "X
cannot be reached from outside the house on the drawing"** — and 2 come from the fault layer.
The guillotine slicer cannot draw a house you can walk through. CP-SAT largely can, and
CLAUDE.md has said since Phase 6 that *"two placement engines, and the default is the weaker
one."*

**The sheet that raised Phase 9 was already CP-drawn** — its caption reads *"proven … no
placement exists"* — so this is not the explanation of Lucas's seven complaints. It is the
explanation of the fatal column in every table above, and it means that column was never the
right acceptance criterion for a scoring package.

## 8. AND THE SCORING CHANGES DID NOT DELIVER

Measured on the corrected tree — `spanning()` fixed, clamp refused — over the 21 partis:

| engine | setting | fatal | rooms below floor | rooms over ratio |
|---|---|---|---|---|
| heuristic | control (universal 2.6) | 121 | 106 | 134 |
| heuristic | each room's own band | 121 | 105 | 137 |
| heuristic | own band + width floor at 6 | 125 | **95** | **126** |
| auto | control (universal 2.6) | 39 | 113 | 145 |
| auto | each room's own band | 39 | 114 | 154 |
| auto | own band + width floor at 6 | 42 | 112 | 147 |

**Reading each room's own proportion band is neutral**, on both engines. It is shipped anyway,
and the reason is not the ledger: the universal 2.6 belonged to no room, it was spelled TWICE
(here and as the `26` in CP's linearised `10*mx - 26*mn`), and a placer that reads
`dimensions.area_sf` from a dict while ignoring `dimensions.proportion` in the same dict is
reading one key of three. The corpus deciding is worth a neutral ledger; a magic number spelled
twice is not.

**An earlier version of this report claimed 127 → 119 for that change. It did not reproduce.**
That measurement was taken while `spanning()` carried a refusal-on-ambiguity that broke the
shipped reference plan, and the improvement was an artifact of the broken tree. It is recorded
here rather than quietly corrected, because the lesson is the one this repository already
states: a measurement taken while somebody else's experiment is in the tree is not a
measurement of anything — and the somebody else can be you, four edits ago.

**The width floor moves what it aims at, on the weaker engine only, and is SHIPPED AT ZERO.**
On the heuristic it takes rooms below their own floor 106 → 95 and rooms over their band
134 → 126, against fatals 121 → 125 in a column that is 121/123 unreachability. On `auto`,
which is what draws the sheets, it is a bad trade: **fatal 39 → 42 to move rooms below their
floor 113 → 112.** CP already holds every room inside 0.88–1.20 of its programme as a HARD
constraint, so a soft floor has little left to say there, and the three fatals are real. The
term, its full sweep and this reason are kept in `geometry.py` at `WIDTH_W = 0.0` rather than
deleted, so the next reader has the measurement instead of rebuilding it.

**So the honest summary of the scoring work is that none of it moves the ledger on the engine
that ships.** The shape bands are neutral, the width floor is a bad trade there, and the door
weights are neutral. What ships from §2 and §5 ships because the corpus should decide rather
than a constant that belongs to no room — not because the numbers got better. They did not.

---

## 9. WHAT WAS REFUSED, WITH THE MEASUREMENT

1. **`parti_slice()`, the package's own premise.** The tree is already stated (§1); a probe of
   it took fatals 3 → 8.
2. **`_clamp_cut`, a correct fix for a real defect.** Built, measured, and left **in the file
   and not called**, with its arithmetic and its numbers, so the next reader does not
   rediscover the inversion and ship it. It costs: fatals 114 → 127; the entry porch drawn
   10.0 × 6.0 becomes 5.0 × 8.3 so its clear depth falls 6.0 → 5.0 and
   `porch-nobody-can-sit-on` fires again, a fault WP-7.4 had cleared; and the relaxation count
   moves 7 → 8, pinned verbatim in two files. Against that: **no winning placement at HEAD
   contains a negative-dimension room, on any of the 21 partis** — the defect never reached a
   sheet. It was eliminating 22.3% of candidates before they could be scored, and they were the
   cramped ones. *A fix that removes a shield is a fix that has to look at what the shield was
   covering.* Wiring it in is a package of its own and must replace the accidental filter with
   a stated one in the same change.
3. **Grammar-weighted door charges as a SCORING change.** The charges are right and read the
   corpus (passage-to-stair 25.8 as an `open`, drawing-to-library 24.8 as a `double`,
   bedroom-to-closet 11.8 as a swing) and the ledger does not move: fatal 119 → 119. The
   heuristic cannot act on the distinction — floor of 12 broken door-ends over 4,000 candidates
   where CP achieves 0 of 30. Kept, because the charge now means what the corpus says rather
   than one flat number, and disclosed as score-neutral.
4. **Refusing on `spanning()` ambiguity.** The first draft returned None on a tie. It broke the
   shipped reference plan: `passage` (S,N) and `backhall` (N,S) both qualify, the slab never
   formed, and the entry porch left the entrance wall. The tie is now BROKEN by the corpus —
   the larger circulation room, because `rooms/back-hall.json` calls itself "the second
   circulation system … designed to be invisible from the formal plan" — with an id tie-break
   so the answer no longer depends on dict order.

## 10. TWO DEFECTS FOUND ON THE WAY, BOTH SHIPPED FIXED

- **`render_plan.py` drew the wrong level's relaxation marks.** The plate loop is
  `for i, lv in enumerate(levels)` and an inner label-wrapping loop at line 367 **rebound `i`**,
  so `level_marks[i]` read a stale text-line index. Measured on the Tidewater sheet: the upper
  plate drew the ground level's six marks a second time and neither of its own two — twelve
  triangles for eight recorded relaxations. A drawing lying about the record is the whole
  subject of Phase 6, and this one had been doing it wherever a room's label happened not to
  wrap to the plate's own index.
- **`spanning()` answered in file order.** Three `five-part-palladian` level-0 rooms satisfy its
  test identically (`passage`, `westhyphen`, `easthyphen`), and it returned `passage` because
  the parti lists it first — `easthyphen` after a shuffle. The spine of the house was decided by
  JSON key order.

## 11. VERIFYING

```
python3 -m pytest tests/ -q                     # the suite
python3 build/geometry_cp.py selftest           # both engines still prove what they place
```

The 21-parti ledger is `scratchpad`-only by design: it takes 20 s on the heuristic and 440 s on
`auto`, and pinning a number that costs seven minutes to reproduce is how a pin stops being run.
The numbers above are quoted with their engine and their tree state, which is the discipline
that matters more than the pin.
