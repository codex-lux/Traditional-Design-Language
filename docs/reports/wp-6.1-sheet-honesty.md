# WP-6.1 — The sheet stops lying

*26 August 2026. Tranche 1 of three. Branch `claude/floor-plan-design-issues-1x19t3`.*

## Why

Lucas read the two shipped sheets of `plans/tidewater-georgian-careful.json` and found a
house nobody could live in: a kitchen whose only door is to the outside; a "massive" door
into the dining room; door sizes varying with no rhyme or reason; a stair hall with no
stair; a centre passage whose rear door is a window; triangular arrows that "seem to point
to anything and everything"; a chamber bath with no way in. His diagnosis was the
project's own founding one — *colorless green ideas sleep furiously*: every part
individually well-formed, the whole meaningless.

Three explorations reproduced every symptom by execution. The findings split cleanly in
two, and that split is what made a three-tranche program possible rather than one
enormous change:

- **Some of it is the drawing lying about the record.** The record HAS the kitchen's five
  doors; the renderer drops them in silence. The record SAYS the dining-room door is a
  pair of leaves; no renderer reads the field. That is this tranche.
- **Some of it is the record having nothing to say.** A door has no wall, no position, no
  hand, no height, no rank; composed plans emit `{"to": id}` and nothing else. That is
  WP-6.2, and no amount of drawing fixes it.

Settled decision 11 — *"the drawing is a render of the data and nothing is drawn that is
not in the record"* — is not reopened by any of this. It is what was being violated, in
both directions at once: the sheet invented what the record did not hold, and discarded
what it did.

## What was found

**The triangles are honest data wearing an illegible symbol.** They are relaxation marks
— guillotine cuts that missed the structural bay, `geometry_report.relaxations.marks`,
eleven of them on the Tidewater ground floor with the worst 4.81 ft off. They sit on
partitions because an off-grid cut IS a partition line. They were defined only in the
caption's running prose, so a reader meeting one on the drawing had nothing to read it by.
Nothing was wrong with the mark except that the sheet never said what it was.

**Ten of twenty-seven interior doors on the Tidewater plan were dropped in silence**, and
thirteen of twenty-three on the spec Colonial. The rule was a flat 3.2 ft of shared wall,
applied to a 2.2 ft closet door and a 6 ft cased opening alike, with `continue` as the
entire error path. All five of the kitchen's interior doors fail it. So does the chamber
bath's only door — which is exactly why the reader found a bathroom with no access, and
why `plan_check` reported nothing: **it validates the declared graph, and the declared
graph is fine.** Only `build/export_dxf.py` has ever owned up to this class, since WP-5.1.

**`door.type` was read by nothing.** Not by `render_plan.py`, not by `derive.js`, not by
either exporter. The Tidewater plan's 5 ft `double` between drawing room and dining room —
a pair of 2 ft 6 in leaves, the withdrawing enfilade — and its 6 ft `open` cased opening
into the stair hall were both drawn as one hinged leaf with a swing arc of the full
opening width. Those two marks are the "massive door" and most of the "no rhyme or reason".

**The rear door really is drawn as a window.** Exterior doors and single windows were both
placed at the midpoint of the room's wall run, by two passes that never looked at each
other. Measured on the placed ground floor: the passage's exterior door at x = 25.39 and
its S window at x = 25.39; the kitchen's back door at x = 10.00 and its N window at
x = 10.00. `WindowMark` paints a filled rect, `DoorMark` paints a 0.7 ft break — so the
window swallows the door, twice, on the shipped sheet.

**`build/render_plan.py` drew no exterior doors at all** (`if t == "exterior": continue`),
so every front and back door in the corpus was missing from every Python-rendered sheet,
and the DXF and IFC exports inherited the gap.

**The two renderers had already drifted, under a comment saying they could not.**
`derive.js` has claimed since WP-5.2 to be a port of `render_plan.py` "so the two renders
of the same record cannot quietly disagree". Measured, they disagreed about exterior doors
(one drew none), about door width (one hardcoded 3 ft, the other read the record), and
about type (neither read it). The claim was in a comment and nothing held it to account.

**Three claims in the tree were false, and two of them were about the same missing
feature.** `build/geometry.py`'s module docstring and `docs/geometry.md` both advertise
"a stair that lands where it left" among the vertical-alignment terms. `vertical_score`'s
stair branch assigns a variable and discards it; it scores nothing, and `stacks_over` is
read by neither engine. On the Tidewater plan the ground stair sits at y 16.00–26.62 and the upper landing at
y 30.00–40.08: **zero overlap, and not one point charged.**

*(Corrected after this report was first written: that plan states the stair-to-landing
relationship as an `above`/`below` adjacency, which only `plan_check` reads;
`landing.stacks_over = "stair"` is declared in `partis/five-part-palladian.json`, so every
plan composed from that diagram carries it. Neither engine reads either field, so the
finding is unchanged — but an earlier draft named the wrong mechanism for a right
measurement, which is the more dangerous half to get wrong, and this corpus has a
standing record of exactly that error inflating the evidence for a change somebody wanted.
Measured properly, across both shipped plans six rooms declare `stacks_over` and **four are
placed with zero overlap on the room they name**.)* Separately,
`check_partis.py` carried a comment asserting that the plan validator reports unreachable
rooms. It does not; that lint over the 21 authored partis is the only reachability guard
in the system, and it never sees a composed plan.

## What was built

**Both renderers, moved in lockstep.** A door is now measured against its own leaf and
jambs (`required_wall_ft(w) = w + 2 × 0.35`), so a closet door draws at 2.2 ft where the
flat test refused it — the renderer half of **OQ 41/63**, which asked whether the
renderers should learn narrow doors or the solver's floor should rise. They have learned
them, and the exporters with them. Door `type` is drawn as the kind of opening it is: a
`double` as two leaves meeting at the middle, a `cased-opening`/`open` as a lining with no
leaf, a `pocket` as the slot it runs in, `garage` and `bulkhead` as a leaf on the wall line
with no plan swing. `render_plan.py` draws exterior doors. Both honour `width_ft`.

**Openings share a wall by rule.** Doors take their positions first; windows are
distributed into what is left, by the same k+1-of-n+1 spacing as before but measured
against the free run rather than the whole wall. A window with nowhere left to go is
reported, never drawn on top of a door.

**Nothing is dropped in silence any more.** `derive_openings` returns `undrawable`
alongside the openings it placed, each with the reason it could not be drawn, and both
sheets print it in the DXF exporter's own words: *"N DECLARED DOOR(S) WITHOUT A DRAWABLE
OPENING — IN THE RECORD, NOT THE LINEWORK"*, followed by the pairs.

**The △ has a legend**, on the sheet that uses it, in both renderers.

**A room drawn at a size its record does not declare says so** — `∗` on its dimension
string, the declared figure in its tooltip, and a count in the caption. This is OQ 54's
silence closed on the drawing side. The critic still does not read placed geometry; that
is WP-6.2's drawn layer, per Lucas's ruling to reopen OQ 54.

**The plate title survives its own line-wrapping.** It had `flex: 0 1 auto` beside a
`1 1 34ch` note, so a narrow plate folded it at its interpuncts and a reader saw
*"WATER GEORGIAN, FIVE CAREFULLY PLANNED"* — a different house, with nothing to say the
name had been cut. The title now takes the space it needs and the note yields.

**The three false claims are corrected in place**, each stating what is true today and
naming the tranche that will make the advertised thing real, rather than being quietly
deleted.

### The guard, which is the durable half

`tests/fixtures/sheet_symbols/*.json` freezes a placement and the openings both renderers
must derive from it; `tests/test_sheet_symbols.py` drives the Python one and
`workbench/app/src/derive.test.mjs` the JavaScript one. Change one without the other and
**both** suites fail. The placement inside a fixture is frozen rather than solved at test
time on purpose: `geometry.solve()` reaches for CP-SAT and falls back to the hill-climb
when CP-SAT does not answer inside its budget, so a fixture built by solving would pin
this machine's speed alongside the code.

`e2e/walk.mjs` asserts the new affordances in a real browser, and asserts them against
things the page computed rather than numbers written down twice: that door marks carry
their type and that a `double` and a cased opening are among them; that the undrawable
list names as many doors as it claims; that the △ has a legend; that the divergence count
in the caption equals the marks on the drawing; that the title is whole.

## Measured, before and after

On `plans/tidewater-georgian-careful.json` (heuristic placement, deterministic):

| | before | after |
|---|---|---|
| interior doors drawn | 16 | 16 |
| interior doors **dropped in silence** | **10** | **0** |
| doors named as undrawable, with a reason | 0 | 11 |
| exterior doors drawn (`render_plan.py`) | **0** | 4 |
| doors drawn at their declared width | 0 of 20 (all 3 ft) | 20 of 20 |
| doors drawn as their declared type | 0 | 20 |
| window/door collisions on one masonry | 2 | 0 |
| rooms drawn off their declaration, disclosed | 0 of 23 | 23 of 23 |

The eleventh undrawable door is `breakfast–terrace`, whose other room is an outdoor room
the placement does not carry at all. Naming it is right, and the e2e assertion had to be
corrected to allow it: *one* end of an undrawable pair must be a room on the sheet, not
both, because "the other room is not placed on this level" is one of the reasons a door
cannot be drawn. A check that demanded both would have made the sheet unable to name the
very doors it most needs to name.

**The interior count did not move, and that is the honest result.** This tranche makes the
sheet tell the truth about the placement; it does not improve the placement. The kitchen
still has no drawable interior door — it now says so, loudly, instead of presenting a
kitchen reachable only from the garden as a finished drawing. Making those doors real is
WP-6.2 (openings with declared positions) and WP-6.3 (a solver that must honour them).

## What was deliberately not done

- **No third rendering engine.** A server-derived "symbol plan" was considered and refused:
  it is a third implementation to keep honest. WP-6.2 shrinks the invented surface to
  almost nothing by moving positions into the record, which is the real cure for the drift.
- **The exterior-door wall is still inferred**, from the first declared `exterior_wall`
  the placement put on the boundary — now skipping walls already carrying a door, so two
  exterior doors cannot land on top of each other. The sheet says the wall is inferred.
  The record has no field for it until WP-6.2, and inventing one here would be the
  laundering this corpus forbids. **This is why the centre passage still has no rear
  door**: its record declares one `exterior` door and a window on N, and `tidewater-georgian`
  c03 — *"exterior doors at both ends, aligned on axis and both operable"* — is a hard
  constraint the hand-authored reference plan does not satisfy. That finding belongs to
  WP-6.2 and is recorded here so it is not lost.
- **No stair and no fixtures.** Both need record objects that do not exist yet (WP-6.2),
  and drawing either from the room catalogue at render time would be inventing plan
  content in the renderer — exactly the fault being fixed.
- **The △ was not redesigned**, only defined. Changing a symbol the corpus already uses is
  a Drawn Language decision, not a bug fix.
- **No change to `DragHandle`'s commit semantics** beyond the divergence disclosure. It
  still writes a placed dimension into the declared record; that is worth a ruling and is
  not this tranche's to take.

## A note on the environment

`requirements.txt` installed cleanly here, **ortools included** — so unlike the last
several packages, the CP engine is genuinely available this session and WP-6.3 can be
proved rather than reported N/EV. Two things surfaced while establishing the baseline and
are recorded because they change what "green" means:

- **CP-SAT cannot solve the Tidewater plan in its 25 s budget.** It returns UNKNOWN and
  falls back to the hill-climb, which is why the sheet Lucas was reading came from the
  weaker engine. On the spec Colonial, where CP-SAT does answer, **zero** declared doors
  are undrawable against the heuristic's ten. That is the sharpest argument yet for
  WP-6.3's default flip — and a warning that the flip alone will not rescue this plan.
- `workbench/server/tests/test_endpoints.py::test_example_plan_no_traversal` asserted
  Starlette's *routing mechanism* (that a traversal falls through to the SPA catch-all and
  serves `index.html`) rather than the security property beside it. Newer Starlette
  normalises the path and 404s instead — a **stricter** refusal — and the test failed. It
  now asserts that the target file's content is never served, which is what it means to
  test. The property held throughout.
