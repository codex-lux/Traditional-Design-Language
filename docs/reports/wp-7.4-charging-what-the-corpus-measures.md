# WP-7.4 — charging what the corpus already measures

*27 August 2026. OQ 76's stacking half, OQ 78, and the vocabulary half of OQ 72 and the
arrangement half of OQ 73. Five commits.*

---

## What this package is

Phase 7 half-closed three questions and opened a fourth. The generator became level-aware and
fixed **bearing** rather than **stacking** (OQ 76); arrangement was built to one authored wall
run (OQ 73); the window's authority was split two ways and the kit vocabulary left unruled
(OQ 72); and the search was found to have no span term at all (OQ 78).

Lucas ruled four things: a **soft** stacking term in **both** engines; charge the **real** span
check and mirror it in CP; raise the candidate depth by measurement; merge the duplicate window
spellings and turn the existing checker on.

**Three of the four rulings survived contact with measurement and one did not survive intact.**
What follows says which, and why, in the order the work was done.

---

## 1. The span check was not measuring clear spans (commit `6743a63`)

`build/structure.py::span_check`'s docstring says *"Bay-by-bay clear span between consecutive
bearing lines"*. Its line 207 read every wall's `position_ft` and **never touched the `bearing`
flag that `bearing_lines()` had computed one call earlier** — so the `why: "not on the bay grid
— a partition"` string that function writes onto every off-grid interior wall was produced and
discarded, and the floor was leaned on walls the same module had just called partitions.

On `plans/tidewater-georgian-careful.json`:

| axis | lines used | worst gap reported | real bearing lines | true clear span |
|---|---|---|---|---|
| x | 7 | 23.37 ft | 3 | **49.93 ft** |
| y | 9 | 10.00 ft | 4 | 20.00 ft |

Corpus-wide over the 16 plan records: spans **236 → 126** (the phantom break points disappear),
over-capacity spans **9 → 20**, worst **36.57 ft → 60.00 ft**.

This is the OQ 52 family wearing the sign that looks safe — not a refusal overwritten by a
confident number, but a defect **reported smaller than it is**. Both shipped reference plans now
fail their own structural capacity loudly. That is the check working: their interior walls
mostly do not land on the bay grid, and a partition carries no floor.

**It had to be first.** A span charge laid on this measurement would have taught the search to
aim at partition placement. Nothing pinned the behaviour, which is why it survived three
packages; two tests now do, and the first was confirmed to fail against the old code.

---

## 2. The fixture packer used one wall, and that hid which wall it drew against (commit `241a448`)

WP-7.2 made `fixture_pass` choose the wall with the longest **clear** run rather than simply the
longest wall, on the principle that *"a fixture refused on a wall nobody tried is a false
cannot-fit"* — and then packed every fixture onto that one wall, which is the same error one
level up. The score terms below moved a room and it surfaced at once: `spec-builder-colonial`'s
primary bath is **9 × 18 ft**, its four fixtures want **22 ft**, its longest clear run is
**17.2 ft**, and its other three walls stood empty. A 162 sf bathroom reporting a shower that
will not fit is the well-formed-and-meaningless drawing this programme exists to remove.

Each wall now keeps its own cursor and a fixture tries the wall it is already on first, so a room
whose fixtures all fit on one wall packs byte-identically to before. The corner reserve is crude
on purpose — a newly opened wall starts past the deepest fixture placed anywhere in the room,
which **over**-reserves, and over-reserving is the safe direction: the failure it prevents is a
drawn collision and the failure it causes is a named refusal.

**And the off-wall coordinate was the room's low edge for all four walls.** A fixture on the N
wall was written at the room's *south* edge, one on the E wall at its *west* edge — drawn against
the opposite wall from the one its own record names. It could not show while everything went on
one wall: they were all wrong together, so nothing overlapped and the drawing merely put the bath
on the wrong side of the room. Letting the run turn the corner made it visible immediately as 5
overlapping pairs. **15 of 67 placed fixtures across the 16 plans sit on N or E, in 6 of the 24
rooms that place any.** *A fix that removes a shield is a fix that has to look at what the shield
was covering* is in CLAUDE.md; this is that, exactly.

After both: 67 placed fixtures, **0 unplaced, 0 outside their room, 0 doors drawn through one**,
and no real overlaps — 4 abutting pairs share an edge by up to 0.0030 ft (0.036 in), which is the
record's own 3-decimal rounding.

**A test was pinning a nondeterministic solve.** `test_a_fixture_is_tried_on_every_wall_before_
it_is_refused` asserted 0 refusals on the default engine, which is `auto`, and CP-SAT is
wall-clock bounded: four consecutive runs of spec-builder alternated between 13 placed / 0
refused and 12 / 1 depending on which branch finished in budget. That is OQ 71's error. The three
tests replacing it assert on the deterministic engine, or assert behaviour.

---

## 3. Three spellings of one window, and a vocabulary that is a ratchet now (commit `7497734`)

OQ 72's open half, ruled: merge the exact duplicates and turn the existing checker on.

`double-hung-sash` → `double-hung` (the spelling `elements/slots.json` already gave as an
example), `round-arched` → `round-arch`, `round-headed-window` → `round-headed`. The flat
vocabulary went **44 → 41** distinct ids and the consumed one **22 → 21**; `double-hung` now
carries the **54 of 119** resolving styles that were described two ways.

**The hazard was list order, not spelling.** `compose.kit_window_type` takes the first
non-forbidden variant, so merging two ids inside one kit could silently re-pick that kit's window
type. The consumed pick and the full resolved variants list were snapshotted through the lineage
for **all 164 styles** before and after: **0 differed beyond the rename**. No kit carried both
spellings of a pair, and no `op` anywhere targets a renamed id.

`check_kits.py::check_slot_fields` has read `fields[].examples` as a permitted vocabulary since
OQ 47, and `expressed_frame` was the only slot declaring one — so a `window_type` variant id was
validated by nothing, the kit schema typing it as a free string. It now declares its 41, and a
`dubble-hung` typo errors.

**The list is every id the corpus uses, not an idealised one, and the slot says so.** Twenty of
the 41 are on the wrong **axis** rather than merely spelled oddly: they describe an opening's
head shape or its surround — `clean-rectangle-flat-architrave` (8 styles), `horseshoe-arch` (7),
`round-arched-paired` (5) — and this corpus already has the slots that own them: `arch`, added at
0.7.0 for exactly this, plus `window_head_*` and `window_surround_*`. Two more name a glazing
treatment or a relative date. All 22 are listed one by one under the slot's `off_axis` key with
the slot each belongs to, because **24 of the 119 resolving styles are handed one as their window
type** and migrating them changes what those styles resolve as. That is OQ 72's remaining half.

---

## 4. "Exactly one" was five, and the sixth was mine (commit `c720102`)

OQ 73 published that `needs_uninterrupted_wall_ft` was authored *"where a furniture item's own
note states a run in words — **exactly one does**"*. Four more state one outright, with a figure:

| room | item | ft | the sentence |
|---|---|---|---|
| kitchen | range, 30 in | 5.0 | *"15 in of landing each side, so a range needs 60 in of wall minimum and wants 72"* |
| living-room | sofa | 11.0 | *"needs 132 in of wall with the end tables; this is the dimension that decides where the doors can go"* |
| bedroom | desk | 6.0 | *"It needs 6 ft of wall, and the only walls a bedroom has spare are the ones the closet and the door are not on"* |
| study | the camera wall | 5.0 | *"5 ft of wall BEHIND the sitter that is not a window and is fit to be seen"* |

These are **readings**. The number is in the sentence; nothing is decided here that the corpus
had not already written down, which is the line OQ 73's ruling drew.

**A sixth was a judgment and the new basis test caught it.** `keeping-room`'s hearth was authored
at 9.0 ft from *"its chimney breast is 9 to 10 ft; on a 14 ft wall that leaves almost nothing
either side"* — a band explaining why first-period halls are wider than their successors, not a
run the hearth requires. Taking its low end was a judgment wearing a reading. **The figure was
withdrawn rather than the test loosened.**

The check went from **13 placed rooms of one type to 61 across five**, still 0 findings on the 16
plans — and the population is asserted before the clean run is believed, because a rule that
fires on nothing passes vacuously. Nothing in the repo had referenced the field at all.

---

## 5. The two score terms

### What OQ 76 and OQ 78 each got wrong about their own subject

**OQ 78's cost premise was false.** It said putting the span check in a 250-candidate loop is
*"the 25 s × N cost that `build_section`'s own docstring exists to avoid"*. That 25 s is the
**solve** inside `build_section`, which the candidate loop already has. The check itself —
`wall_lines → bearing_lines → span_check` over rects that already exist — measures **0.026 s for
250 iterations**. So the corpus's real structural check is affordable as a search term and the
"cheap proxy" OQ 78 speculated about is not needed. It would also have been wrong:
`geometry.wall_lines` collects every room edge and cannot tell bearing from partition, so its
widest gap **under**-estimates the clear span — the exact error §1 removed.

**OQ 76's blocker applied to a mechanism nobody had to use.** It recorded that a CP stacking
constraint *"outranks every authored exterior wall in the corpus"*, because the downgrade loop
takes `[key for _t, k, key in core if k == "wall" and key]`. True **of a hard pin**. A penalty
creates no assumption literal, never enters a conflict core, and cannot displace anything —
and `geometry_cp.py` already carried the template, in the soft wet-over-wet term. The blocker is
sidestepped rather than solved.

**And the refusal I published in WP-6.3 was inert for a reason I got wrong.** It measured
byte-identical output at 100× and 10,000× and concluded *"the search can only re-rank blind
candidates"*. That charge keyed on landing-over-stair, a pair **neither shipped plan declares**.
Measured over 2,000 candidates rather than the shipped 250 at one seed: on tidewater, 12
candidates beat the winner's 3 broken claims **while keeping the porch on the entrance front**,
at +41.3 points; on spec-builder, 6 at +2.1. In the thin 250-candidate pool the only
better-stacking candidates move the porch off the front (`entrance_score` 0 → 100, WP-2.2's
founding bug), which is why the break-even there reads 378 and 52. **A sampling artefact, not a
property of the charge.**

### The weights were chosen by sweep, and the sweep found a trap

Both weights were swept over the 14 partis that declare `stacks_over`, composed against their own
first native style — the population WP-7.1 published 27/47 against.

**The span term alone is inert below weight 2 and *worse* between 2 and 20 than at either end:**

| SPAN_W | spans over cap | worst | relax | fatal |
|---|---|---|---|---|
| 0 – 1.5 | 29/125 | 80.0 ft | 76 | 89 (byte-identical) |
| 2 | 28/126 | 80.0 ft | 74 | 94 |
| 10 | 22/137 | 50.0 ft | 68 | 100 |
| 30 – 60 | 18/139 | 50.0 ft | 66 | 90 |

A weight sweep that stopped at "small weights are safe" would have shipped the worst setting.
A new term in a hill-climb can perturb the search into a worse basin long before it is strong
enough to steer it into a better one.

**And the two terms have to be balanced against each other, not tuned separately.** At
SPAN_W = 40 a 60 ft span over a 20 ft capacity costs 40 × 3 = 120 points — the scale
`entrance_score` reserves for fatal-tier facts — and it swamped the stack term completely:
`STACK_W = 16, SPAN_W = 40` produced output **identical to SPAN_W = 40 alone**.

| STACK_W | SPAN_W | stacks broken | relax | spans over cap | worst | under_band | serious | fatal |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 27/49 | 76 | 29/125 | 80.0 | 17 | 703 | 89 |
| 16 | 40 | 25/49 | 66 | 18/139 | 50.0 | 19 | 699 | 90 |
| 40 | 40 | 17/49 | 62 | 18/142 | 60.0 | 19 | 687 | 94 |
| 24 | 20 | 19/49 | 72 | 24/132 | 60.0 | 19 | 696 | 93 |
| 40 | 10 | 15/49 | 74 | 25/132 | 60.0 | 20 | 692 | 93 |
| **40** | **20** | **15/49** | 75 | **23/134** | 60.0 | 19 | **685** | **90** |
| 56 | 20 | 12/49 | 70 | 24/137 | 60.0 | 20 | 686 | 94 |
| 160 | 20 | 6/49 | 55 | 24/135 | 60.0 | 17 | 670 | 112 |

**`STACK_W = 40, SPAN_W = 20`.** Broken stacks **27 → 15 (−44%)**, over-capacity spans
**29 → 23 (−21%)** with the worst falling **80 → 60 ft**, and total `serious` findings
**703 → 685**. It is the only setting in the neighbourhood that is best on `serious` and `fatal`
at once.

### What it costs, stated

**Fatal findings 89 → 90, and that +1 is within the neighbourhood's own spread.** Nearby weights
run 93–94, so the honest reading is *+1 to +5 in this region*, not a clean +1. The composition is
better than the count: **6 new and 5 removed**, every one of them the same "cannot be reached
from outside the house on the drawing" finding, on plans that already carried 89 of them. The
terms reshuffle which room ends up unreachable rather than systematically severing circulation.

**Rooms below their catalogue band 17 → 19.** Two rooms are shrunk under their own floor to buy
a stack or a bearing line. That is a defect that survives the life of the building and it is the
real price here; it is counted, and `geometry_cp.py` refuses the trade entirely (OQ 54).

### Both engines, and CP keeps its proof

The heuristic term is in `vertical_score`; the CP terms are penalties in the `if objective:`
block beside the existing wet-over-wet one. The CP span term is affordable because the bearing
set there is **finite and small**: the model is on a 1-ft integer grid, `bearing_lines` calls an
interior wall bearing within 0.75 ft of a bay multiple, and on whole feet the only qualifying
positions *are* the multiples — seven lines on a 60 ft frontage. The line bools are
**half-reified** (`f → face == L`, nothing in the other direction), so a line may only be claimed
bearing if a wall is really on it, while leaving it unclaimed is free; false is the penalised
direction, so the solver can never buy a bearing line it has not placed a wall on, and the
expensive `!=` half is never built.

### A third place had to learn the span charge, and its own docstring said so

`geometry_cp._score` opens *"The heuristic's OWN scoring of this placement, term for term, so the
acceptance comparison is apples to apples"* — and `_finish_feasible` chooses among its hard-valid
placements by that score. The span charge lives in `solve_heuristic`'s candidate loop rather than
inside a scorer function, so adding it there left `_score` blind to it: a term the heuristic
charges and the CP acceptance does not is a term the CP path cannot act on, however well the CP
model is steered by the penalty. `_score` now calls `_span_charge` too, and the docstring's claim
is true again. Caught by reading the function rather than by any test — it is prose, which is
WP-6.4's whole point.

**THE CP TERMS CHANGE NOTHING IN ANY PLACEMENT MEASURED, AND THAT HAS TO BE SAID PLAINLY.**
Six placements were run twice, once with both weights at zero and once at the shipped values:

| placement | terms off | terms on |
|---|---|---|
| `tidewater-georgian-careful` | OPTIMAL, spans 4/9, stacks 2/3 | OPTIMAL ×3, spans 4/9, stacks 2/3 |
| `spec-builder-colonial` | FEASIBLE, spans 4/6, stacks 1/2 | FEASIBLE ×3, spans 4/6, stacks 1/2 |
| `cape-central-chimney` | FEASIBLE, spans 2/9, stacks 2/3 | identical |
| `centre-passage-double-pile` | FEASIBLE, spans 3/5, stacks 3/5 | identical |

Identical in every case. On Tidewater the reason is structural: the winner is `hard-only phase A`
— the placement from the feasibility phase, which the objective never touches — so no CP
objective term can reach that drawing at all. On the others the polish phase does win and the
outcome still does not move.

**So the CP half of this ruling is built, sound, proof-preserving and so far inert**, and the
honest state is that its effect is unmeasured rather than demonstrated. It is kept rather than
removed because the alternative is two engines that disagree about what matters, and because
`_score` — which decides the CP path's *acceptance* — does now carry the span charge, which is
the route by which it can act. Whether it ever does is a measurement nobody has made; four
placements is not a corpus. That is the shape of WP-6.3's stair charge all over again, and this
time it is recorded as inert on the way in rather than discovered two packages later.

### The ruling's order had to be inverted, and the measurement says why

Lucas ruled: raise the candidate depth, chosen by measurement, then add the terms. Measured
**before** the terms, deepening the search makes the corpus **worse** on exactly the quantities
this package targets — score falls monotonically 3388 → 2881 from 250 to 8000 candidates while
over-capacity spans go 20 → 26 at 2000 and relaxations do not improve at all. The search spends
its extra candidates buying score at the cost of structure, because the score did not contain
structure. So the terms had to land first, and the depth is chosen against a search that is
aiming at the right things.

---

## 6. The candidate depth was raised by measurement, and the measurement said no

Lucas ruled: **raise it, chosen by measurement, re-pinning every moved number.** The measurement
was made twice — once before the terms and once after — and it does not support the raise.

**Before the terms**, deepening the search makes the corpus *worse* on exactly the quantities
this package targets. Over the 16 plan records, score falls monotonically 3388 → 2881 from 250 to
8000 candidates, while over-capacity spans go **20 → 26** at 2000 and relaxations do not improve
at all. The search spends its extra candidates buying score at the cost of structure, because the
score did not contain structure. That is why the ruling's order had to be inverted: the terms
land first, so the depth is chosen against a search aiming at the right things.

**After the terms**, on the 14-parti population — the instrument with 49 stack claims rather than
the plan records' 5:

| candidates | wall clock | stacks broken | relax | spans over cap | worst | under_band | serious | fatal |
|---|---|---|---|---|---|---|---|---|
| **250** | 11 s | 15/49 | 75 | 23/134 | 60.0 | 19 | 685 | **90** |
| 500 | 11 s | 16/49 | 73 | 23/134 | 60.0 | 18 | 684 | 94 |
| 1000 | 20 s | 14/49 | 71 | 24/134 | 50.0 | 19 | 685 | 92 |
| 2000 | 37 s | 15/49 | 69 | 20/137 | 50.0 | 14 | 683 | 92 |

Broken stacks are **15, 16, 14, 15** — flat within noise across an eightfold increase. Spans move
only at 2000. What does improve monotonically is relaxations (75 → 69) and, at 2000, rooms below
their band (19 → 14); the cost is fatal +2 and 3.4× the wall clock.

**And there is an interactive cost the corpus-wide tables do not show.** `solve_heuristic` is what
the workbench's wall drag calls **by name** (`PlanWorkbench.jsx:141`, debounced at 400 ms).
Measured on the Tidewater plan: 250 candidates 0.45 s, 1000 1.46 s, 4000 5.75 s. Raising the
default would take the drag's response from about a second to over six.

**So the default stays at 250, and that is the ruling executed rather than declined** — the
ruling asked for a measurement and the measurement says the raise buys total score and
relaxations, not the structural quantities it was meant to buy, at a cost the one interactive
path in the product cannot absorb. A caller that can afford depth already passes `candidates=`.

### One cost that was worth removing

The span check is the most expensive thing in the candidate loop — it rebuilds each level's room
records and runs `structure.wall_lines`' O(n²) shared-segment scan — and it took a 250-candidate
solve from **0.21 s to 0.57 s**. `_span_charge` can only ever *add*, so a candidate whose partial
score already meets the incumbent cannot win however few spans it has. Skipping the check for
those is **exact, not an approximation**: verified over all 16 plan records, **0 scores differ**
with the early-out disabled. It returns the solve to **0.45 s**.

## Verification, and the one thing that could not be confirmed

**Every checker green**, with both address ratchets unmoved: `validate`, `check_kits`,
`check_constraints`, `check_rooms` (0 errors), `check_partis` (0 errors), `check_faults`,
`check_addresses` (own 442 pairs / 0 collisions; cascade 1,264 / 9 — the ratchet values),
`check_openings` (1,890/1,890 pairs named), `check_windows`, `check_pack_bindings --strict`,
`check_inheritance`, `check_counts` (24 claims, 0 stale), `proportion_engine selftest` (57
packs, 0 problems).

**36 of the 37 test files pass**, run in batches: 894-odd tests including `test_solver.py`
(8 passed, 2 skipped — the CP proof pin holds), `test_wp46_packs.py` (281, the open-question
register guard among them), `test_geometry`, `test_structure`, `test_openings`, `test_site`,
`test_plan_validator`, `test_export`, `test_measurement_honesty`.

**`tests/test_score.py` could not be run to completion in this container, and it is not this
package's doing.** It reaches test 43 of 46 and then crawls; the same file behaves identically
**at commit `b8b8f36`, before any of WP-7.4**, and identically again with `_span_charge`
short-circuited to return zero and both weights set to 0. Three of its last four tests
(`TestTheComposerIsDeterministic`) pass in 42 s when run as a class. Whatever this is —
environmental, or an ordering-dependent cost in the composer — it predates the package and is
reported rather than papered over. It is the one gap in this verification.

**Five pinned numbers moved and each carries what moved it**: relaxations 9 → 7 on Tidewater in
three files; the under-band test's named room (the dining room is in band now, the stair hall is
not); and serious findings on spec-builder 54 → 53, which diffing finding-by-finding shows is
entirely the porch coming out 6.00 ft instead of 5.71 and clearing
`porch-nobody-can-sit-on`.

## What this package did not do

- **No hard CP stacking pin.** Soft only; the `wall_keys` downgrade loop is untouched, so an
  inferred stack can never displace an authored exterior wall. OQ 76's stated blocker is true of
  a pin and never applied to a penalty.
- **No span proxy.** The real check costs 0.1 ms per candidate against the loop's own 0.85 ms, so
  OQ 78's stated cost premise — *"the 25 s × N cost that `build_section`'s own docstring exists to
  avoid"* — was false: that 25 s is the **solve** inside `build_section`, which the candidate loop
  already has. A proxy would also have been wrong, since `geometry.wall_lines` cannot tell bearing
  from partition and its widest gap under-estimates the clear span — the exact error §1 removed.
- **No re-axis of the 20 shape/surround `window_type` ids.** Recorded, counted, ratcheted, and
  left for its own ruling.
- **No furniture-driven room sizing** (OQ 73, refused) and no bay/bow/oriel geometry (OQ 72).
- OQ 74 (the door's hand), OQ 75 (the passage that cannot satisfy its own hard rule) and OQ 77
  (`_shared`'s corner-kiss ordering) are untouched and open.
