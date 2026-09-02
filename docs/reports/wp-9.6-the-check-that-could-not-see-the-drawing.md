# WP-9.6 — The check that could not see the drawing, and a finding that could not see the code

*Status: complete, 2 Sep 2026. Built the two items the WP-9.5 audit deferred that needed no
ruling, and withdrew a third that turned out not to be a defect at all. Cite reports by filename,
never the bare WP number (OQ 90).*

## The measurement that says it best

Over the sixteen plans, the furniture layer emitted **exactly 137 findings whether or not the plan
carried geometry.** Solve the plan, hand the solved record to `plan_check`, and the number does not
move. That is a check reading the declared record and nothing else, stated as a number rather than
as an accusation.

It is now 178 on the declared record and the drawn layer carries **86 across-shortfalls and 69
along-shortfalls** beside it.

## What Lucas gets out of it

His second complaint was a breakfast room "far too narrow". On `auto` — the engine that drew the
sheet he read — the Tidewater breakfast room is declared 12 × 14 and **drawn 7.0 × 27.0**, and the
critic now says:

> Breakfast Room is DRAWN 7.0 ft across and cannot take its table, seats 4: needs 9.0 ft
> (36 in item + 2 × 36 in clearance, freestanding). The record declares 12 × 14 ft, which holds it.

The arithmetic that convicts it has been in the corpus since WP-6.2. It was pointed at the wrong
rectangle. Complaints 3 and 6 gained drawn furniture findings in the same change — the Entrance
Portico at 6.0 ft cannot take a rocking chair, and the Stair Hall at 6.0 ft cannot take its own
stair.

**On `engine="heuristic"` that same breakfast room is drawn 12.6 × 15.4 and is fine.** The sliver
is an `auto` outcome on this plan. Every figure in this report names its engine for that reason,
and the ratchet pins the heuristic ones only.

## 1. One function, two callers

`plan_check.furniture_shortfalls(rt, w, l)` is the one spelling of the fit arithmetic. The room
layer hands it the declared width and length; the drawn layer hands it the placed rectangle,
immediately after the width-floor and proportion checks that already have it. The callers differ in
**wording and layer and in nothing else**.

**`openings.required_wall_ft` is NOT the precedent for this and three documents said it was.** That
rule is deliberately spelled three times — `openings.py`, `render_plan.py`, `derive.js` — because
one of them is JavaScript and the app suite may import nothing, and `tests/fixtures/sheet_symbols/`
holds all three to one contract. The discipline transfers; the mechanism does not. Here both
callers are Python in one file, so a shared function is available and duplication would be a
choice rather than a constraint.

The extraction was verified **byte-identical** before anything else changed: all sixteen plans,
1,479 findings, identical file. Only then did behaviour move.

## 2. The `elif` — 41 facts computed and discarded

The long axis was tested only where the short axis had **passed**:

```python
if   w + 1e-6 < need_short: ... serious
elif l + 1e-6 < need_long:  ... minor
```

So a room failing both was told about one of them. Split into two independent checks:

| | declared record | drawn (heuristic) |
|---|---|---|
| short-axis failures | 75 | 86 |
| long-axis failures | 104 | 69 |
| **dropped by the `elif`** | **41** | **15** |

These were never silences — the room still took its short-axis finding — but the second fact was
computed and thrown away, and a room too narrow for a bed is very often also too short for it.

Totals: declared furniture 137 → 178 (+41). Drawn layer 419 → 574 (+155 = 140 from the new call
site, 15 from the split). Every figure deterministic on `engine="heuristic"`, identical on cold
runs.

**And the strongest evidence in the package is what did NOT move.** `tests/test_plan_validator.py`
pins the finding counts on both shipped reference plans, and it caught this change — correctly:

| | fatal | serious | minor |
|---|---|---|---|
| `tidewater-georgian-careful` | 0 → **0** | 30 → **30** | 61 → **65** |
| `spec-builder-colonial` | 4 → **4** | 57 → **57** | 62 → **74** |

**Every point of movement is in `minor` and nothing was re-graded.** Long-axis shortfalls are
minor by the rule that was already there, so a change that surfaced dropped facts should move that
column and only that column — and it did, on both houses, without touching a single fatal or
serious. Had the split changed a judgement rather than revealed one, `serious` would have moved.
The careful plan takes four where the ordinary one takes twelve, which is the ratio that pair of
tests exists to watch.

## 3. The finding that was wrong, and how it survived three audits

WP-9.2 §8 published a "second defect": that `fw, fl = sorted(it["footprint_in"])` "assumes every
item rotates", turning the kitchen island `[84, 27]` sideways so a 10 ft kitchen passes at 9.25 ft
where an island along its counter run needs 14.0. WP-9.5's second pass measured three formulations
of a fix and recommended "pairing each axis with its own clearance". CLAUDE.md and
`PLAN-OF-ACTION.md` both carried it, the latter as a live work instruction.

**All of it was wrong, and the pairing it recommended already existed.** `sorted()` assigns the
item's short side to the room's **width** and its long side to the room's **length**:

```python
need_short = (fw + sides * cl) / 12.0          # short side vs room WIDTH
need_long  = (fl + 2 * min(cl, 36)) / 12.0     # long side  vs room LENGTH
```

The island's long axis is checked at 13.0 ft and it **fires** — on `bad-03` (10 × 11) and `bad-04`
(10 × 12). A 12 × 16 kitchen holds an 84 in island with two 36 in aisles and passes, correctly. And
the 10 × 30 sliver Lucas named is caught by the drawn **proportion** band (3.0 against a 1.8
ceiling), not by furniture at all. The three-formulation table measured formulations neither the
code nor any fix uses.

**How it survived.** Three passes re-read the sentence; each found it coherent, and it was — it
named a real function, a real field, a real item with real dimensions, and drew a plausible
conclusion. It died the first time anyone executed the function it described, which took about
four minutes. That is WP-9.5's own closing rule earned once more, and this is the cleanest instance
of it in the phase: **every finding that survived came from running something; every finding that
had to be withdrawn came from reading.**

**A typed orientation field on furniture items is therefore NOT wanted.** Authoring a schema field
to fix a non-defect would have been the more expensive half of the mistake.

## 4. The citation guard opens 11 more files

`check_citations.tracked_files()` is a `git grep`, and it selected on `OQ [0-9]+` alone — so a file
carrying no **numbered** citation was never opened and nothing in it was checked in any context,
plain prose included. Because the numbers froze at 99, every new named question is born without an
`OQ <n>`, so the hole grew with the namespace.

The pattern is `OQ [0-9]+|oq/[a-z0-9][a-z0-9-]*` now: **392 → 403 files**, eight of the eleven being
entries in the register itself. Pinned as a PROPERTY over the real tree — every file containing a
slug citation must be opened — so the test cannot go stale as files are added.

**It cost exactly one repair, and that repair is a third instance of a gotcha this corpus keeps
paying for.** `build/harvest_habs.py` wrapped a real slug across a Python string-literal line
break; the checker reads line by line and saw a truncated id. The string was rewrapped so the slug
sits on one line. **The checker was not taught to rejoin hyphen-ended lines** — that would make a
second rule out of a formatting accident, and CLAUDE.md already records the same line-by-line
behaviour twice (the WP-8.5 commit subject, and a code span straddling a newline).

## 5. Guards, and that they can fail

Four mutations, each reverting one fix, each producing a red suite; control green.

| mutation | result |
|---|---|
| revert the `git grep` pattern | `test_citations.py` — 1 failed |
| (and an existing guard caught ME) | `test_determinism.py::test_corpus_globs_are_sorted` — three unsorted directory reads in the new tests, one of them a `sorted(` that opened on the line above, which that guard also reads line by line |
| revert the `elif` split | `test_furniture_drawn.py` — 2 failed |
| revert the drawn call site | `test_furniture_drawn.py` — 1 failed |
| add a second transcription of the fit arithmetic to `geometry.py` | `test_furniture_drawn.py` — 1 failed |

The source-reading test asserts a **count and a location** (`len(hits) == 1`, and it is in
`plan_check.py`) rather than comparing against a list that would be empty if the selector broke —
this repository has shipped that exact inversion before, in `assert 'class="ch"' not in text`.

The corpus ratchet runs `furniture_shortfalls` against placed rectangles directly rather than
through `plan_check`, which keeps the whole file at ~5 s; the wiring is proved separately on one
plan end to end. Both are needed: the ratchet cannot see the call site being deleted, and the
wiring test cannot see the arithmetic drifting.

## 6. A third of the upper floor was not being drawn, and Lucas found it by looking

Added after the package was pushed, because he read the sheet the way Phase 6 and Phase 9 both
began — by looking at it — and said the upper floor was cut off and should line up with the floor
below. Both halves were one defect.

`render_plan.render()` computes the sheet's top margin ONCE:

```python
top = max(96, (84 if plan.get("geometry_report") else 70) + 14 * _n_banner + 8)
total_h = top + extra_top + ph + extra_bottom + 84
...
for i, lv in enumerate(levels):
    ox = pad + i*(panel_w+gap) + extra_left; oy = top + extra_top
```

and then, deep inside the level loop, the room-label block did **`top = cy - block/2`** — the
same name. So the first plate was positioned from the real margin and every plate after it from
wherever the last room's label happened to begin. Measured on `tidewater-georgian-careful`,
`engine="auto"`: ground plate at y=134, **upper plate at y=378.2**, running to y=658 on a canvas
`total_h` had already sized at **498**. **160 px of the upper floor was outside the viewBox and
simply not drawn**, and the two levels no longer shared a top edge.

**The sharpest part is eight lines long.** Directly below that assignment sits a paragraph
explaining that an inner loop had rebound `i`, that this made the upper plate draw the ground
level's relaxation marks, and that "a drawing lying about the record is the whole subject of
Phase 6". Someone found and fixed the `i` rebinding and did not notice the `top` rebinding two
lines above it — same defect, same block, one instance carrying a written warning about the
other.

The fix is the rename: `label_top`. **Two guards, and their sensitivities differ**, which is
stated in the test file because a reader would otherwise assume the first one caught it:

| guard | catches this bug? |
|---|---|
| `test_every_level_plate_shares_one_top_edge` | **yes** — reverting the rename turns it red (`spec-builder-colonial`, plates at 134.0 and 152.1) |
| `test_no_drawn_rect_leaves_the_declared_canvas` | **no**, on `heuristic` — the drift there is ~18 px and stays inside the sheet's 84 px of bottom padding. It fires when the canvas is undersized past that padding (mutation-checked at −100 and −160 px), which is the 160 px overflow `auto` actually produced. |

Both are kept because they fail on different mutations. **The canvas guard was nearly deleted for
passing the obvious mutation**, which would have been the wrong call for the right reason: it does
not guard the margin, it guards the class.

**And this is the answer to "the before and after SVGs are the exact same".** They were, and that
was correct — WP-9.6 changed the critic and not the generator, and `render_plan.py`, `geometry.py`
and `geometry_cp.py` are all absent from the `6a01225..464afdc` diff. The sheets being identical
was the honest result. What it also meant is that nothing in this package was looking at the ink,
and a plate had been landing off the canvas the whole time.

## 7. The stair: the input first, then the reader — and the figures that sent me here were wrong

Lucas ruled the pack authoritative and asked for the ceiling fallback fixed first, then the
shared reader. Doing the first made the second nearly free — but the numbers that framed the
question did not survive being run. **And the ruling then arrived in two parts**: the pack governs,
and then, on the one question this package left open, *"7.5 in is right — move the pack."*

**What had been published, in a commit message, two reports, `CLAUDE.md` and a register entry:**
three spellings giving 16 / 17 / 21 risers, "3.3 ft apart on one house", caused by `openings.py`
falling back to a hardcoded 9.0 ft ceiling. **Measured:**

| spelling | input | result |
|---|---|---|
| `rooms/stair-hall.json` `critical_dimension` | its own worked example, a 9 ft ceiling | 16 at 7.5 in — an example, not a claim about this plan |
| `openings.py::stair_pass` | `(11 + 1.0) × 12` = 144.0 in | **20 at 7.2 in** |
| `structure.py::stair_geometry` | `storey_height_ft` 12.279 × 12 = 147.3 in | **21 at 7.017 in** |

The 17 came from feeding `stair_pass` a 9 ft ceiling **by hand**; the plan declares
`floor_to_ceiling_ft: 11`, so the `or 9.0` fallback never fired on it. The gap is **3.3 inches of
floor assembly**, not 3.3 ft of ceiling — out by a factor of twelve. `structure.py` derives the
assembly by inverting `storey-graduation.json`'s own `ceiling_height_rule` (15.35 in at 11 ft,
11.86 in at 8.5 ft); `openings.py` used a flat 12.00 in.

**The audit that first produced the 17 was honest about it** — it wrote "fed the prose's own
input". The next pass quoted the figure without that clause, and from there it travelled as a
measurement. **A caveat that survives one paragraph and then drops is worse than no caveat**,
because downstream the number looks measured. It was caught by executing the function.

**Built.** `build/storeys.py` holds the one derivation and is a **leaf on purpose**:
`structure.py` loads `geometry.py`, which calls `openings.stair_pass`, so openings importing
structure would close a cycle. `structure.py` re-exports `storey_heights` and
`STOREY_CEILING_FRACTION` under their old names, so its three existing test callers are untouched
and there is exactly one implementation. `stair_pass` reads `storeys.ground_storey_in(plan)`;
**both invented constants go in one move** and the two spellings agree by construction —
`tidewater-georgian-careful` 20/20, `spec-builder-colonial` 17/17. Where no ceiling is stated
anywhere on the ground level the pass **refuses the stair with a reason** rather than assuming
9.0; **0 of 16 plans take that branch today**, recorded so the refusal is not read as dead code.

### 7b. Then the divisor moved, and the point is that only one file had to change

**`build/storeys.py::riser_divisor_in` READS `storey-graduation.json`'s `stair_type` expression**
with a strict `ceil(module / <number>)` match and **refuses any other shape** rather than falling
back to a number. That is what made the second half of the ruling a one-line data edit: the two
Python literals that used to carry 7.25 — one in `openings.py`, one in `structure.py`, each
commented with the name of the pack it was copied from, so that moving the pack would have moved
neither — no longer exist. The pack moved and the code followed by construction.

Two records had to move by hand and both are data: the pack's `derived_rules[stair_type]`
expression, and its **baked copy** in `kits/georgian-colonial-american.kit.json` at
`/slots/stair_type/parameters/risers_per_storey` — which is
`oq/a-baked-pack-value-is-a-second-delivery-path` appearing in the course of ordinary work, and
worth noting because nothing in the corpus would have failed had the second been missed.

**Measured, and only two of sixteen plans place a stair hall at all:**

| plan | storey | at 7.25 in | at 7.5 in |
|---|---|---|---|
| `tidewater-georgian-careful` | 147.34 in | 21 risers at 7.017 in | **20 at 7.367 in** |
| `spec-builder-colonial` | 120.56 in | 17 at 7.092 in | **17 at 7.092 in**, unmoved |

Neither leaves the IRC advisory maximum of 7.75 in; the worst shipped riser is 7.367. And the
pack's own default — a 120 in storey — now gives **sixteen risers at exactly 7.500 in**, which is
the example `rooms/stair-hall.json`'s `critical_dimension` has always worked. Reproducing the
corpus's own worked example is the argument for the number.

**The disagreement it leaves is recorded in three places and reconciled in none.** That same room
record's `conflict` note calls the historic comfortable band *"7 to 7.25 in rise on an 11 to 11.5
in tread"*, so the corpus's default stair now sits just outside a band the corpus states about
itself. It is written into the pack's note, into the room record's own `conflict` note, and into
the register entry. **Editing either number to make the two agree is the move this corpus names
first**, and the ruling for `oq/a-grouping-rule-and-a-room-record-can-disagree` — a checker that
reports agree / disagree / cannot-compare — is where a disagreement like this should surface.

### 7c. Moving the pack broke a snapshot of the pack, and the open question had predicted it

**The baked copy carries the expression AND the value the expression produced, and I moved one.**
After the edit, `kits/georgian-colonial-american.kit.json` read
`{"expr": "ceil(module / 7.5)", "computed_at": {"storey_height_in": 120.0, "value": 17}}` — the
same object stating 7.5 and 17, where 7.5 on a 120 in module gives **16**.

**Nothing caught it, and that is by construction rather than by oversight.** `check_kits.py`
holds the `computed_at` CONTEXT keys consistent across a slot family and explicitly `continue`s
on `"value"`; `check_addresses.py::baked_vs_refused` measures a snapshot delivering a value the
live rule REFUSES, which is a different question. Both were run with the defect in place and both
came back exactly as before — `check_kits` OK, `check_addresses --strict` at its ratchet of 32.

**`oq/a-baked-pack-value-is-a-second-delivery-path` had already written this down**, in its own
closing paragraph: *"A derived snapshot is a cached computation with no cache invalidation… it
cannot see the case where the rule's VALUE has changed and the snapshot has not."* That was
written on 28 Aug as a general shape with no instance. This is the instance, and it arrived four
days later in the commit that moved the rule — which is a better argument for the entry than any
number in it.

**Measured across all 159 kits: 143 baked derived parameters carry both an `expr` and a
`computed_at.value`. Exactly ONE is of a shape a narrow reader can evaluate** — `ceil(module / D)`
against a stated `storey_height_in` — and that one is the one that broke. **The other 142 are
UNJUDGED, not passing**: their expressions and contexts are shapes this reader does not parse. A
general checker is that open question's to rule on, and authoring one here would be inventing the
mechanism the question exists to decide, so the guard added is scoped to the single rule this
package moved.

**And the mutation check for that guard passed on the first attempt, which was wrong.** The
sed-style replacement it used matched an earlier occurrence in the file and never touched
`risers_per_storey`, so the test stayed green and read as a test that cannot fail. Re-run with an
anchored replacement and an assertion that the mutation applied, it goes red on both directions:
the stale value restored, and the baked expression drifted from the pack's. **A mutation that
silently does not apply is indistinguishable from a guard that does not work** — assert the
mutation landed before believing the colour.

`tests/test_storeys.py`, eight guards: the transcribed `STOREY_CEILING_FRACTION` pinned against
the pack's own expression (it is a transcription, not a read, and that is defensible only while
something holds the two together); an unjudged level that says so; the floor assembly proved not
to be a constant; the two spellings agreeing on every shipped plan; the divisor read rather than
transcribed, **with a scan of every file in `build/` for a stray one**; an unrecognised
`stair_type` expression refused rather than defaulted; the baked kit copy held against its own
expression; and the re-export under the old name.
**Mutation-checked in six directions**, each proved red: restoring `(ch + 1.0) * 12` with its
`or 9.0`; putting a bare `/ 7.25)` back in `structure.py`; making `riser_divisor_in` return a
literal; making the reader fall back instead of raising.

The pinned reference-plan finding counts did not move at either divisor (30/65 and 57/74/4) —
`plan_check` has no stair-riser finding, which is itself worth knowing: **the number changed on
both engines and no critic layer noticed.**

## What was deliberately not done

- **No new numeric threshold.** Severities are unchanged (short axis `serious`, long axis `minor`).
- **`min(cl, 36)` is refused rather than fixed, with its number.** It caps the long axis's
  clearance; its comment reads *"ends take chair pull, not full passage"*, which is right for a
  table and arguable for an island. **Four drawn items** fail the long axis at full clearance and
  pass at the cap. Changing it is authoring a threshold.
- **No generator change.** Neither engine was touched. The drawn check reports what the search
  draws; it does not change what it draws. Both reference plans place identically.
- **Two of the three items that needed a ruling stay deferred**: the authored-and-unenforced
  12 ft `start_setback_from_front_door_ft` ceiling, and the 268 of 761 derived rules carrying no
  `quantity`. The third — the stair divisor — was ruled during the package and is built; §7b.
- **The stair divisor was NOT sourced, and the ruling does not claim it was.** 7.5 in is the
  figure the corpus already worked its own example at. That is consistency, not evidence. No
  period source for a comfortable riser has been read here, and the record's rival 7–7.25 in band
  is equally unsourced in this tree.
- **The code-span half of the citation question stays open.** 120 of 164 mentions still sit in
  backticks and are exempt; the twelve that resolve to nothing are all deliberate illustrations.
  Only the file-selection half is closed.

## New open questions

None. WP-9.6 closed half of `oq/a-slug-in-a-code-span-is-not-checked` and withdrew a finding;
it raised nothing that needs a ruling.
