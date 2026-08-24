# The plan validator

The critic, built before the composer — because a composer needs a fitness function, and this is it.

## What it reads

`schema/plan.schema.json`: a topology plus approximate dimensions. Rooms with a type, a width and length, a window head, doors, fixtures. Doors imply adjacency in both directions and the validator derives the graph from them. Deliberately hand-authorable — you should be able to type a sketch into it in five minutes and find out whether the rules are right.

```
python3 build/plan_check.py plans/spec-builder-colonial.json --min-severity serious
python3 build/plan_check.py plans/tidewater-georgian-careful.json --layer daylight
```

Two example plans ship with it. One is a deliberately ordinary production Colonial, every decision in it something that gets built. The other is the same corpus applied carefully.

| | fatal | serious | minor |
|---|---|---|---|
| Spec Builder Colonial | **3** | 49 | 51 |
| Tidewater Georgian, careful | **0** | 18 | 60 |

*(These counts are pinned by `tests/test_plan_validator.py` — run `make check` rather than trust this table if the two ever disagree.)*

The three fatals on the first are the powder-room door off the dining room, the primary bedroom over the garage, and a half-width shutter at 0.33 where the corpus wants 0.48.

## Five layers

**Room** — dimension bands, ceiling minimums, **furniture fit with real clearances**, daylight depth against window head. The furniture check is the one most plans have never had run on them: a dining table for eight plus chair pull plus passage needs 12 ft 4 in across, so an 11 ft 6 in dining room fails before anything is drawn.

**Adjacency and privacy** — typed directional rules with their style exceptions, and the public-to-private gradient. Two subtleties earned their place by producing false positives on a correct plan: connection is checked **two hops through a hall**, because that is how houses work and requiring a shared wall makes the corridor a fault; and **circulation is rank-transparent**, because a corridor at rank 1 opening onto bedrooms at rank 4 *is* the buffer.

**Grouping** — declared groupings' required rooms, massing fit, privacy span.

**Fault** — the 209-fault corpus against whatever measurements the plan supplies, style exceptions honoured.

**Code** — IRC model text, **advisory and jurisdictional**, never a permit review. Labelled as such in every run.

**Style** — declared choices checked against the resolved kit's forbidden variants. A constraint that has been migrated to `schema/constraint.schema.json`'s `test` object (WP-1.1/WP-1.2, 140 of ~660 as of 23 Aug 2026 — see `docs/constraints.md`) is actually evaluated: `plan.measurements`, plus a small set of values `plan_check.derive_constraint_vars` reads directly off unambiguous plan structure (storey count, ground-floor room count and ceiling height, a `centre-passage` room's width), feed `core._eval_test`. A passing constraint is silent; a failing one is a finding at a severity `CONSTRAINT_SEV` maps from the constraint's own hard/soft/advisory (hard → serious, soft → minor, advisory → advisory — a wrong roof pitch is not grounds to fail the whole plan the way a duplicate room id is); a constraint whose variables aren't available is an `info` finding naming what's missing, never silently passed. `result["constraint_summary"]` gives the present/clear/unjudged counts. The remaining ~520 unmigrated constraints, and any `scope: judgment` constraint, keep the pre-WP-1.2 behaviour: a hard one is listed for hand review, nothing else is asserted about it.

## Absence is not failure

A plan record that does not model closets is coarse, not wrong. Those findings go to a separate `completeness` layer at `minor`; `--strict` promotes them. Getting this wrong buried the findings that mattered under sixty that did not.

## What the daylight check learned

Depth is measured from the lit wall, so the rule has to know how the room is lit. A room with glass on two opposite walls is lit from both ends and is only half as deep as it measures. A cross-lit room tolerates about half again the depth of a single-sided one. Without both corrections, a correctly planned Georgian drawing room with windows on two walls fails its own rule.

## What the three-level cascade test found

Filling `english-georgian` put a third level in Georgian's chain — and it contributed **0%**, because Georgian specified all eight of those slots itself. **A fully-specified child makes its ancestors dead weight.** The cascade only pays where the middle layer `extends` rather than restates.

Converting two Georgian slots to `extends` made the third level appear in the provenance immediately. It also tripped the failure mode flagged when `extends` was designed: nine variant `op: replace` records naming ids no ancestor defines, which silently become `add`. `check_kits.py` caught all nine. The mechanism works; it needs the checker to be safe.

## Next

The composer. It now has a scoring function, two worked examples of what good and bad look like against it, and a target: assemble groupings into a plan record that scores zero fatal.


## The room-type alias groups (`EQUIVALENT`)

Some room types are interchangeable *for the purpose of an adjacency rule* and for no other
purpose. A rule that says the entry porch must reach an entrance hall is satisfied by a
vestibule or a stair hall, because what the rule is protecting against is a front door that
leads nowhere, and any of the three receives a person. `build/plan_check.py` holds eight such
groups in `EQUIVALENT`, and `_alias()` widens every adjacency test through them.

| group | what it protects |
|---|---|
| `stair-hall`, `landing` | the stair, read as one thing across its two levels |
| `entrance-hall`, `vestibule`, `stair-hall`, `gallery-corridor` | the room that receives a person at the door |
| `parlor`, `living-room`, `sitting-room`, `family-room`, `great-room`, `drawing-room`, `best-parlor` | the principal sitting room, whatever a period calls it |
| `dining-room`, `eat-in-kitchen-area`, `breakfast-room` | where the household eats |
| `bedroom`, `bedchamber`, `primary-bedroom` | a room slept in |
| `bathroom`, `primary-bathroom` | a room washed in |
| `kitchen`, `scullery` | where food is cooked |
| `pantry`, `butlers-pantry`, `larder` | food store and service between kitchen and dining |
| `closet`, `walk-in-closet`, `linen-press` | enclosed storage |

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
