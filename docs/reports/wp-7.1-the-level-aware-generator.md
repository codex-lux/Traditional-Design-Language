# WP-7.1 — the generator can see the other level now, and it fixed the wrong half

*27 August 2026. Phase 7, package 1 of 3. Branch `claude/floor-plan-design-issues-1x19t3`.*

## Why

OQ 76 said the placement generator was blind to the level below, and that no score term could
see past that. It was right about the blindness. It was wrong about what the blindness was
causing, and this package is mostly the story of finding that out.

Lucas ruled: build the level-aware generator, not a score term.

## The scope, measured before anything was built

`stacks_over` is not a two-plan problem. It is declared by **14 of the 21 partis — 50 claims**
— so every plan composed from one of them carries it. Composed against its own first native
style and placed on both engines:

| | broken |
|---|---|
| heuristic | **26 of 49** (53%) |
| CP-SAT | **23 of 49** (47%) |

Roughly half, on both engines, because neither reads the field. The register's "one on each is
drawn clear" was measuring two hand-authored plans.

## What was built

`build/geometry.py`'s candidate loop fills the ground layout into `gr` and generates the upper
level five lines later, **in the same iteration, with `gr` fully in scope**. It was simply
never passed. Now it is: `slice_rect` carries a `below` dict, and `snap()` — the only source of
cut positions in the file — prefers a wall line below over a bare bay line.

**The relaxation definition had to be corrected in the same commit.** A relaxation is *"a joist
run that does not land on a bearing wall"* in this file's own prose; the code approximated that
as "misses the bay module". Those are not the same test — **18 of 30 ground wall lines on the
shipped plans are themselves off the bay grid** — so a cut landing squarely on a wall below had
been counted a compromise while a cut on a bare bay line with nothing under it counted sound.
A cut that lands on a wall below now returns `off = 0.0`. That is the prose finally executed,
not a loosening of it.

**Measured, heuristic, deterministic:**

| | baseline | WP-7.1 |
|---|---|---|
| transfer beams, 14 composed plans | 166 | **109** (−34%) |
| relaxations, 14 composed plans | 96 | **76** (−21%) |
| total score, 14 composed plans | 6936.8 | **6850.3** (better) |
| transfer beams, 23 plans inc. both shipped | 205 | **128** (−38%) |
| over-capacity spans, 23 plans | 17 | 19 (+2) |
| worst span in the corpus | 47.12 ft | 47.12 ft (unchanged) |
| Tidewater: transfer beams / relaxations / vertical | 21 / 11 / 58.0 | **10 / 9 / 28.0** |

The over-capacity check matters because a transfer beam and an over-capacity joist both mean
"this needs a bigger member" — if the change traded one for the other it would be a shell game.
77 beams removed for 2 spans, worst unchanged: it is not.

## What it did not fix, which is the finding

**`stacks_over` claims broken: 26/47 → 27/47. Flat.**

Moving a cut line moves a wall. It does not move a room over another room. A second half was
built and measured — biasing a room's partition toward the room it stacks over, weighted 2.0
against an exterior wall's 1.0 — and it exactly cancelled the harm the cut-line half did to
stacking (cut-lines alone: 30/49; with the bias: 26/49) and netted zero improvement over
baseline. It is kept because it is the right shape and costs nothing, and it is reported as
having achieved nothing.

**Bearing continuity and declared stacking are two different problems, and OQ 76 conflated
them.** The bearing half is closed for this engine. The stacking half is open and is a
different mechanism.

## Two corrections to WP-6.3 that this package owes

**Its stated refusal reason was false.** WP-6.3 refused the stair-stacking charge because *"the
search can only re-rank blind candidates and can never produce a stacking one."* Measured over
24 seeds, the winning candidate satisfies **1 to 3** of Tidewater's 3 cross-level claims and
**0 to 2** of spec-builder's 2. The search plainly reaches stacking placements. The charge was
inert for a narrower reason — it keyed on landing-over-stair, and neither shipped plan declares
that pair. The conclusion stands; the reason is corrected in `geometry.py`, `docs/geometry.md`,
CLAUDE.md, the register and WP-6.3's own report.

**A test was pinning luck, and the guarantee it named never held.**
`test_no_span_over_capacity_passes_silently_on_the_careful_plan` asserted that the careful plan
has no span over the 20 ft hand-framed capacity — measuring `build_section(plan)`, which
re-solves on the **heuristic**, while the product has shipped CP-SAT since WP-6.3. **On the
default engine that plan carries a 29.00 ft span over capacity, at baseline and after WP-7.1
alike.** The search has no span term at all, so clearing the capacity is luck on either engine
and any change to the search reshuffles it. The test now asserts what is real: spans are
computed, the capacity is checked, an over-capacity span surfaces with a reason. Restoring a
zero assertion would pin luck.

## A trap that cost an afternoon

The spanning-slab branch snaps a **width**; a wall line below is an **absolute position**.
Quietly turning one into the other changed the GROUND placement — which changes which candidate
wins overall, since `vertical_score` is in the total — and cost CP-SAT its proof of
`tidewater-georgian-careful`, the plan WP-6.3 fought to make solvable: OPTIMAL → UNKNOWN at
budget. The blind path now keeps the original width snap byte for byte. Verified 5 runs of 5:
cp-sat OPTIMAL, score 570.7, relaxations 13 — identical to baseline.

**The level-aware run is for the placement and not for the CP hint.**
`solve_heuristic(level_aware=...)` is True everywhere except `geometry_cp._hint_heuristic`. A
hint's only job is to be repairable; a placement's is to be right.

## What this means for the default engine, stated plainly

**CP-SAT is the default, and it is untouched.** It takes only a hint from the heuristic and
builds its own model, so a reader looking at the Tidewater sheet sees exactly what they saw
before. The improvement lands on the fallback engine — which runs whenever CP cannot answer in
budget (2 of 14 partis in this measurement) and on any install without ortools. Making CP
honour bearing continuity or `stacks_over` is its own mechanism and is not this package.

## What was deliberately not done

- **No `stacks_over` score term.** Lucas chose the generator over the term; building both would
  have made it impossible to say which acted.
- **No re-weighting of `vertical_score`** to make the change look better against the search's
  own total.
- **No span term in the search**, though the test rewrite above shows the corpus wants one.
  Raised as a new open question rather than smuggled in here.
