# The plan validator

The critic, built before the composer — because a composer needs a fitness function, and this is it.

## What it reads

`schema/plan.schema.json`: a topology plus approximate dimensions. Rooms with a type, a width and length, a window head, doors, fixtures. Doors imply adjacency in both directions and the validator derives the graph from them. Deliberately hand-authorable — you should be able to type a sketch into it in five minutes and find out whether the rules are right. Since 0.2.0 (WP-5.5) a record may also carry `provenance` — where it came from, how it was transcribed, how much to trust it, and why its style was called what it was; see `docs/ingestion.md`.

**Since 0.3.0 (WP-6.2) it can also hold the PLACED plan.** Until then `additionalProperties: false` at the root forbade `geometry`, `footprint` and `geometry_report`, so a plan the solver had placed could not validate against its own schema and the placement travelled beside the record rather than in it — which is why nothing checked it. An opening now has a `wall`, a `position_ft` (or `positions_ft`, one per unit of a window group), a `hinge`, a `swing_into`, a leaf `height_ft` and a `rank`; a room has a `fixture_layout`; the plan has a `stair`. Everything added is optional, so a hand-authored 0.2.0 record validates unchanged and simply reports COULD NOT EVALUATE on the checks that need a placement.

**Since 0.5.1 (WP-11.2) the footprint carries the WALL ASSEMBLY the house is built of** — `footprint.wall`, from the plan's own `declared.construction_type` against `construction/wall-assemblies.json`, written by `build/openings.py::place` and read by both renderers. It is on the record because it was previously in neither: `render_plan.py` drew no wall body at all and `derive.js` carried `WALL_T = 0.75` and `PART_T = 0.42`, two literals matching no assembly in the catalogue. Additive, and stripped with the rest of the footprint by `strip_placement`, so the DXF round trip still returns the authored record. **Since 0.5.0 (OQ 40) a room may carry a `block`** and the footprint its `blocks`, one per massing element.

**Since 0.4.0 (WP-9.1) an `unplaced` mark carries its figures as fields** — `needs` and `have`, the stair's long and short dimension, a door's shared-wall run, a fixture's footprint — beside the prose and never instead of it, so a revision move reads a number rather than a sentence; and the record admits a `revision_report`, WP-9.2's account of what the loop did to it. **Every finding carries structured evidence beside its statement** (`kind`, `need_ft`, `have_ft`, `slot`, `canonical`, `expression`, `source`, and on the drawn layer the `engine` that placed the house); the id stays what the finding is about (OQ 32), never what it measured. **And the elevation is of the placement the record carries**: until WP-9.1 the fault layer derived it from a fresh heuristic placement while the drawn layer read the carried one — two buildings in one verdict — and the block that did it was silent on failure. `elevation_summary` says which placement and which engine, and an elevation that cannot be derived is a named `info` finding, never nothing. See `docs/reports/wp-9.1-the-critique.md`.

The one rule that governs all of it: **an opening the placement could not realise is marked `unplaced` with a reason, never deleted.** `build/openings.py` writes these, called once from `geometry.solve()` so both engines produce the same kind of record. Note that a window's `unplaced` sits beside its DECLARED `count`, which the placement never overwrites: the shortfall is `count` minus the length of `positions_ft`, and losing an author's declared count to a placement outcome would be the same silent overwrite this layer exists to remove.

```
python3 build/plan_check.py plans/spec-builder-colonial.json --min-severity serious
python3 build/plan_check.py plans/tidewater-georgian-careful.json --layer daylight
```

Two example plans ship with it. One is a deliberately ordinary production Colonial, every decision in it something that gets built. The other is the same corpus applied carefully.

| | fatal | serious | minor |
|---|---|---|---|
| Spec Builder Colonial | **4** | 52 | 60 |
| Tidewater Georgian, careful | **0** | 29 | 60 |

*(These counts are pinned by `tests/test_plan_validator.py` — run `make check` rather than trust this table if the two ever disagree. They are the counts on the DECLARED record; a placed record adds the drawn layer's findings, and the elevation is then derived from that placement rather than from a fresh heuristic one — WP-9.1. This table read 3 / 49 / 51 and 0 / 18 / 60 until 1 Sep 2026, against pins of 4 / 53 and 0 / 30: exactly the drift its own parenthesis warns about, corrected when WP-9.1 moved each serious count by one.)*

The four fatals on the first are the powder-room door off the dining room, the primary bedroom over the garage, a half-width shutter at 0.33 where the corpus wants 0.48, and — since the elevation layer began supplying a window height (WP-3.2) — a window squarer than Colonial Revival permits.

**Since 0.9.0 (WP-11.10) it holds `appendages`, the terrace at grade.** An at-grade appendage is
the one thing this corpus draws that stands outside the block and is NOT a massing element: no
walls, no storey, no roof plane, and not in the built extent the lot cap is measured on. It is
written by `build/appendages.py` after the solve, on `threshold`'s precedent, and its room keeps
`geometry` ABSENT — which is what keeps `structure.wall_lines`, this file's own `rooms_unplaced`
and `geometry`'s block sizing blind to it by construction rather than by six more readers being
taught. Every figure comes off the room record; anything the record does not state is an
`unplaced` entry with a reason from a closed set. The consequence, stated because it is a real
cost: the drawn rectangle is held against no band, since this file's drawn layer reads
`room.geometry` — `oq/an-at-grade-appendage-is-drawn-and-not-judged`.

## Seven layers, and one of them reads the drawing

**Room** — dimension bands, ceiling minimums, **furniture fit with real clearances**, daylight depth against window head. The furniture check is the one most plans have never had run on them: a dining table for eight plus chair pull plus passage needs 12 ft 4 in across, so an 11 ft 6 in dining room fails before anything is drawn.

**Adjacency and privacy** — typed directional rules with their style exceptions, and the public-to-private gradient. Two subtleties earned their place by producing false positives on a correct plan: connection is checked **two hops through a hall**, because that is how houses work and requiring a shared wall makes the corridor a fault; and **circulation is rank-transparent**, because a corridor at rank 1 opening onto bedrooms at rank 4 *is* the buffer.

**Grouping** — declared groupings' required rooms, massing fit, privacy span.

**Fault** — the 209-fault corpus against whatever measurements the plan supplies, style exceptions honoured. A fault comes back in one of four states, and `result` carries all four: present (a test that was for this house ran and failed), clear, `fault_unjudged` (a number the tests need was not supplied), and `fault_not_applicable` (every test declined its own `applies_when` precondition — a house that states it carries no dormers has no dormer rhythm to be off). The fourth exists because such a fault previously appeared in **no list at all**, which reads to a caller exactly like clear. Neither of the last two is a pass. See `docs/faults.md`.

**Code** — IRC model text, **advisory and jurisdictional**, never a permit review. Labelled as such in every run.

**Style** — declared choices checked against the resolved kit's forbidden variants. A constraint that has been migrated to `schema/constraint.schema.json`'s `test` object (WP-1.1/WP-1.2, 140 of ~660 as of 23 Aug 2026 — see `docs/constraints.md`) is actually evaluated: `plan.measurements`, plus a small set of values `plan_check.derive_constraint_vars` reads directly off unambiguous plan structure (storey count, ground-floor room count and ceiling height, a `centre-passage` room's width), feed `core._eval_test`. A passing constraint is silent; a failing one is a finding at a severity `CONSTRAINT_SEV` maps from the constraint's own hard/soft/advisory (hard → serious, soft → minor, advisory → advisory — a wrong roof pitch is not grounds to fail the whole plan the way a duplicate room id is); a constraint whose variables aren't available is an `info` finding naming what's missing, never silently passed. `result["constraint_summary"]` gives the present/clear/unjudged counts. The remaining ~520 unmigrated constraints, and any `scope: judgment` constraint, keep the pre-WP-1.2 behaviour: a hard one is listed for hand review, nothing else is asserted about it.

**Drawn** (WP-6.2) — the house that was PLACED, rather than the one the record declares. This is the only layer permitted to read `geometry`, and every other layer stays geometry-blind, which is the point: a record nobody has placed is judged on what it declares and this layer reports COULD NOT EVALUATE, never a pass.

It exists because the split it crosses was hiding real defects. OQ 54 ruled in August that `plan_check` must not read `room.geometry`, and `workbench/server/evaluate.py` called the separation "a settled fact, not an oversight". While it held, the critic scored the declared house and the sheet drew the solved one, and nothing compared them — so a landing drawn clear of its own stair, a kitchen drawn at 63% of its declared area, and a bathroom whose only declared door the placement could not realise each produced no finding at all. Lucas reopened the ruling for this package. What it checks:

- **Reachability**, over the openings that were actually placed. Nothing in this system had ever checked that you can walk from the front door to every room; a room with no doors produced no finding, and neither did a room whose declared doors had nowhere to go. A stranded habitable room is `fatal`.
- **A room joined to nothing inside the house** — it passes reachability if it has its own exterior door, and it is still wrong. This is the reported symptom in its exact form: *"the door to the kitchen is only from the outside, and the kitchen is connected to no other rooms."*
- **Drawn against declared**, both directions, `minor` past 10% and `serious` past 25%.
- **Every `stacks_over` claim, against the room it names.** The field is in the schema and 14 of the 21 partis declare it (50 claims). **Both engines have charged it since WP-7.4** — a soft term in `geometry.vertical_score` and a penalty in `geometry_cp.py`, never a hard pin — and this layer still checks it, because a charge is a preference the search trades off and this is the arbiter. The test is the same one in all three places, deliberately. A room drawn clear of the room it says it stacks over is a `serious` finding, and **every claim the layer cannot answer is an `info` finding of kind `stack-unjudged` carrying the reason** (WP-11.6) — the target is not a room, is not placed, is on this room's own level, or is not exactly one level below. Before that the same-level case was a bare `continue`: the shipped Tidewater record carried four claims of which three were judged and nothing said which three. The plumbing meaning that case actually had is `wet_stack_with` now, and `plan_check`'s servicing layer is the one reader that takes it. (WP-6.3 refused the charge as inert and WP-7.1 confirmed the level-aware generator did not fix stacking; both measurements stand, and neither was the reason it looked inert — read `vertical_score`'s own comment before quoting either.)
- **Passage clear width** against `rooms/centre-passage.json`'s own two right answers and the dead zone between them.
- **Wet-room fixtures** that will not fit together on real walls, from `room.fixture_layout`.

## Absence is not failure

A plan record that does not model closets is coarse, not wrong. Those findings go to a separate `completeness` layer at `minor`; `--strict` promotes them. Getting this wrong buried the findings that mattered under sixty that did not.

## What the daylight check learned

Depth is measured from the lit wall, so the rule has to know how the room is lit. A room with glass on two opposite walls is lit from both ends and is only half as deep as it measures. A cross-lit room tolerates about half again the depth of a single-sided one. Without both corrections, a correctly planned Georgian drawing room with windows on two walls fails its own rule.

## What the three-level cascade test found

Filling `english-georgian` put a third level in Georgian's chain — and it contributed **0%**, because Georgian specified all eight of those slots itself. **A fully-specified child makes its ancestors dead weight.** The cascade only pays where the middle layer `extends` rather than restates.

Converting two Georgian slots to `extends` made the third level appear in the provenance immediately. It also tripped the failure mode flagged when `extends` was designed: nine variant `op: replace` records naming ids no ancestor defines, which silently become `add`. `check_kits.py` caught all nine. The mechanism works; it needs the checker to be safe.

## Next

The composer. It now has a scoring function, two worked examples of what good and bad look like against it, and a target: assemble groupings into a plan record that scores zero fatal.


## Room-type substitution (`SUBSTITUTES`)

Some room types stand in for others *for the purpose of an adjacency rule* and for no other
purpose. A rule that says the entry porch must reach an entrance hall is satisfied by a vestibule
or a stair hall, because what the rule protects against is a front door that leads nowhere and
any of the three receives a person.

**It runs in one direction (OQ 43, 24 Aug 2026).** This was a list of flat sets and the code
treated membership as mutual: if a primary bathroom counted as a bathroom then a bathroom counted
as a primary bathroom. That is right for some pairings and wrong for exactly the ones that
matter — a primary bedroom's rule to adjoin a **primary** bathroom is not satisfied by the hall
bath being somewhere in the house. `build/plan_check.py` holds a directed map, and two functions
ask the two different questions: `satisfied_by(want)` is "the rule wants this; would anything the
plan HAS do?", and `serves(have)` is "this room is next to me; which rules does it satisfy?".
Before OQ 43 those were one function, which is precisely the bug.

| a room of this type | stands in where a rule asked for | note |
|---|---|---|
| `landing` | `stair-hall` | the stair, read as one thing across its two levels |
| `stair-hall`, `vestibule`, `gallery-corridor`, `centre-passage`, `cross-passage` | `entrance-hall` | the room that receives a person at the door — and mutual, because whichever of them a plan calls its entry, the front door opens into it |
| `hall` | `entrance-hall` | the Anglo-American vernacular hall: the undivided room the front door opens into, not a corridor. One way — an entrance hall is not a hall, which is a room you eat and sleep in |
| `parlor`, `living-room`, `sitting-room` | each other | the principal sitting room, whatever a period calls it |
| `family-room`, `great-room`, `best-parlor`, `drawing-room` | `parlor`, `living-room`, `sitting-room` | one way: the formal or the everyday room answers a request for "the sitting room", and a request for the *best* parlor is not answered by the family room |
| `breakfast-room`, `eat-in-kitchen-area` | `dining-room` | one way: somewhere to eat is not a dining room where one is required |
| `bedchamber` ↔ `bedroom` | each other | the same room in an older word |
| `primary-bedroom`, `garret-chamber` | `bedroom`, `bedchamber` | one way. A garret chamber is a bedroom inside the roof and is what a Cape sleeps in |
| `primary-bathroom` | `bathroom` | one way, and the asymmetry this ruling exists for |
| `walk-in-closet`, `linen-press` | `closet` | one way |
| `scullery` | `kitchen` | one way |
| `butlers-pantry`, `larder` | `pantry` | one way |

**Measured when the direction was added**, across all 129 composable styles: of 542 findings
where the plan modelled *something* the rule would take, 214 were legitimate substitutions and
294 were the table running backwards. The 294 returned to honest absence; the 214 became real
adjacency findings at their own severity, and working through them found two gaps in the table
itself (`hall` and `garret-chamber`), two rules a correct plan structurally cannot satisfy, and
six style traditions the universal rules were not written for — declared as suppressions. Fatal
adjacency findings across the catalogue went 115 → 0.

**This list is data, not convenience.** It is validator data in the same sense a fault or a
style constraint is, and it changes results: WP-0.3 found a test fixture that was passing for
the wrong reason, because a "stair hall standing between two rooms" satisfied an entrance-hall
rule through *aliasing* rather than through the two-hop-through-circulation mechanism the test
was actually written to exercise. If you are writing a fixture, know which of the two you are
testing.

`gallery-corridor` was added to the entrance-hall group by WP-4.5 on WP-2.1's evidence: two of
the reference corpus's good examples use a Gallery as the room the front door and every
principal room open off, which is functionally what an entrance hall *is*, and without it a
grand house whose entrance sequence is a gallery failed a rule written to catch an entry porch
leading nowhere.

**What the groups are NOT.** They do not make two room types the same room. A drawing room and
a family room alias for adjacency and differ in every other respect the corpus models —
dimension band, furniture, privacy rank, trim grade, style variation. Aliasing is a statement
about what a *rule* means, not about what a room is.
