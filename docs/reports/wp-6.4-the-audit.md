# WP-6.4 — the audit of the plan-semantics program, and the eleven claims it falsified

*27 August 2026. Branch `claude/floor-plan-design-issues-1x19t3`.*

## Why

WP-6.1, 6.2 and 6.3 shipped and the suite was green. Lucas asked for a comprehensive
re-check before calling any of it deployment ready. Three parallel audits went through the
package text item by item against the code, and every number below was re-measured rather
than taken from the reports.

**The program's own founding failure mode had come back inside it.** The whole point of
6.1–6.3 was drawings making claims the record could not support. The audit found **eleven
claims in the source, schema and docs that this very program falsified and nobody updated** —
a comment promising work that was afterwards measured and refused, a schema advertising a
field nothing has ever produced, a doc saying a renderer omits exterior doors that has drawn
them since WP-6.1. Under this project's own rules that is the most serious class of finding
here, and every one of them was cheap to fix.

It also found **one real product defect**, one asymmetry, and one check that was claimed and
never written.

## The product defect: a drawing set was not one building

`corpus.drawing(kind="plan")` went through `engine="auto"` after WP-6.3. Two other paths did
not:

- **`export_dxf._solved_copy` forced `engine="heuristic"`**, under a comment reading *"the
  sheet is a DERIVATION of the record, drawn the same way the workbench draws it — the
  heuristic."* The premise is the right rule; WP-6.3 made the second half false and left the
  code following it. `ExportDetails.jsx` posts the DECLARED record, so the exporter's
  has-geometry short-circuit never fired. **A reader looking at a CP-proved plan sheet
  downloaded a DXF of a different placement of the same house.**
- **`structure.build_section` took its own heuristic default** at `corpus.py`'s section and
  bearing SVGs and at the section DXF. So the Drawing Set shipped a plan sheet placed by
  CP-SAT and a section of the same house placed by the hill-climb, with nothing saying so.

Ruled by Lucas: solve once, reuse everywhere. `corpus._placed()` places the plan once on
`auto` and every sheet in the set takes it — plan SVG, section, bearing, plan DXF, section
DXF. A record that already carries `geometry` is returned untouched, so a bench plan the
reader has already had placed is never re-solved out from under the sheet on their screen.

`build_section` **keeps** its heuristic default, and the docstring now says what the default
is for: it is the derivation step inside `plan_check`'s elevation layer and the composer's
scoring loop, where a CP proof per candidate would put 25 s × N into `check_all`. What
changed is that every user-facing caller now passes `geometry_result`. *A default that is
right for a scoring loop and wrong for a drawing is a default that has to name which it is
for.*

`test_one_drawing_set_is_one_building` and
`test_a_placed_record_is_never_re_solved_out_from_under_the_sheet` are the guards.

## The eleven claims

| Where | It said | It is |
|---|---|---|
| `build/geometry.py` docstring | "It is scored for real in WP-6.3; until that lands…" | WP-6.3 measured the charge and **refused** it. Now says so, and points at OQ 76. |
| `build/geometry.py` `vertical_score` | a dead loop assigning `st` and discarding it | **Removed.** Dead code under a comment is an invitation to the next person to finish it, and finishing it does not work. |
| `build/compose.py` | "a corruption **the drawn layer now reports**" | The drawn layer reported nothing of the kind. The check is now built — in the *declared* layer, where it belongs. |
| `Sheet.jsx` plate caption | "exterior door openings are drawn at conventional mid-wall position … **the record does not state which**" | Since 0.3.0 it does. The sentence is now conditional and counts the legacy cases. |
| `build/check_partis.py` | "this lint … is the **ONLY** reachability guard in the system … arrives with WP-6.2" | It arrived. The lint is now described as what it uniquely is: the guard over the 21 authored **partis**, before any plan exists. |
| `schema/plan.schema.json` | `geometry_report` advertises "**severed doors**" | Never produced by anything. Superseded by `opening_report.unplaced`. |
| `build/export_dxf.py` | "drawn the same way the workbench draws it — **the heuristic**" | Fixed above. |
| `requirements.txt` | promises `engine: "heuristic-fallback"` | The code writes `"heuristic"` plus a `reason`, always has. A comment that names a token the code never emits invites someone to test for it. |
| `docs/workbench.md` | "(**`render_plan.py` omits them entirely**)" | It has drawn every exterior door since WP-6.1. |
| `docs/plans.md` | "neither placement engine read it **until WP-6.3**" | Neither reads it now, and that is settled. Directly contradicted `docs/geometry.md`. |
| `docs/plans.md`, `docs/README.md` | "**Six** layers" | Seven are listed. |

Two more of the same kind were corrected alongside: `docs/README.md` and `docs/ingestion.md`
left a reader to infer the plan schema is still 0.2.0, and WP-6.3's own report called page
prose "the caption" when in this codebase's vocabulary that names the plate's.

## What was built

**The engine disclosure is on the PLATE now, both renderers.** WP-6.3 put it in the page
prose beside the drawing, which is the one place it cannot travel: a plate that is printed,
screenshotted or exported leaves the prose behind, and the reader then cannot tell a proof
from a search. `Sheet.jsx`'s caption and `render_plan.py`'s banner stack both read
`geometry_report.solver` and name the fall-back reason when `auto` tried the proof and did
not get one. `e2e/walk.mjs` measures the plate's own caption against the API's report.

**`under_band` reads the declaration.** `over_band` has carried `declared_over_ceiling` since
it was written, so a room the *brief* made oversized is not blamed on the placement.
`under_band` read only the catalogue band — the looser of the two tests for a generously
declared room — so a room placed far under what the brief asked for was invisible unless it
also crossed the catalogue floor. Measured on `spec-builder-colonial`: the dining room is
**26% under its catalogue floor and 40% under its own declaration**; the foyer 49% and
**64%**. Both figures ship, each saying which question it answers.

**One door, two records, and they must agree.** A door is declared on both rooms it joins, so
its width, type and rank exist twice. `compose.derive_openings` decides once per pair and
writes both sides, which keeps a *composed* plan clean — and nothing caught a hand-authored
or hand-edited one. A declared-layer check now reports a disagreement as `minor`, naming both
values. It reads no placement, so it stays legal under OQ 54's ruling. Zero findings across
the shipped corpus; verified to fire on an injected disagreement.

## What was retracted rather than built

- **`geometry_report.severed_doors` was superseded, not skipped.** It was planned before
  WP-6.2, and WP-6.2 built the same thing better: `opening_report.unplaced` carries every
  opening the placement could not realise *with its reason*, both renderers banner it, and
  the drawn layer counts it. A second tally of one fact, keyed differently, is how two
  counters come to disagree.
- **The `_absorb` growth cap** stays at `max(1.20, fill × 1.22)`. The reasoning was already
  in WP-6.3's report but sat under "false claims corrected" rather than in the refusals, so a
  reader scanning for what was skipped would not find it. Moved.

## Lucas's eleven, scored honestly

Nine fixed, two open with numbers on them:

| | |
|---|---|
| Kitchen reachable only from outside | **fixed** — six doors placed |
| Dining room's massive door | **fixed** — a 5 ft *double* into the drawing room is an enfilade pair, correctly drawn as two leaves |
| Door sizes arbitrary | **fixed** — 2.2 / 2.5 / 2.6 / 2.8 / 3.0 / 3.5, plus 5 ft double, 5 ft cased, 6 ft open |
| Stair hall with no stair | **fixed** — dog-leg, 20 risers at 7.2 in, well placed |
| Passage rear door reads as a window | **fixed** — porch door S, exterior door N, both placed |
| Arrows pointing at anything and everything | **fixed** — nine marks, every one on a wall it is true of |
| Passage way oversized | **fixed by the engine flip** — the upper passage is now 325 sf against 360 declared (−10%); it was +63% on the hill-climb |
| No access to the chamber bath | **fixed** — a 2.6 ft door to the upper passage |
| Bathroom unpopulated | **fixed** — WC, lavatory and tub placed; five rooms carry a `fixture_layout` |
| Landing does not stack over the stair | **open, reported, OQ 76** — the generator is blind to the other level and no score term can see past that |
| Furniture layouts not considered | **half** — wet rooms and the kitchen have fixtures; **furniture-driven room *sizing* is not built**, OQ 73 |

Also asked for and not built: the per-opening window **type** — single, double, triple, bay,
double-hung, casement. Windows get a width and a count, never a type. **OQ 72.**

## What was deliberately not done

OQ 72 (window type and bay windows), OQ 73 (furniture-driven sizing), OQ 74 (the door's
hand), OQ 75 (the reference plan that cannot satisfy its own hard passage rule), OQ 76 (the
level-aware generator), OQ 77 (`_shared`'s corner-kiss ordering). All six are numbered and
argued in the register; none is a silent gap. No new engine work, no score terms, no schema
version bump — 0.3.0 stands.

## The finding worth keeping

Three tranches removed the drawings' false claims about the record and **left eleven false
claims about themselves**, most of them written by the same packages in the same week. A
comment that says "until X lands" becomes a lie the moment X lands and is refused; a schema
description naming a planned field becomes a lie the moment the plan changes. Neither is
caught by any test, because both are prose. The only defence found here was reading the
package text back against the code afterwards — which is what this package was.
