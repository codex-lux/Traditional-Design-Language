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

**Style** — declared choices checked against the resolved kit's forbidden variants, plus the style's own hard constraints listed for hand review.

## Absence is not failure

A plan record that does not model closets is coarse, not wrong. Those findings go to a separate `completeness` layer at `minor`; `--strict` promotes them. Getting this wrong buried the findings that mattered under sixty that did not.

## What the daylight check learned

Depth is measured from the lit wall, so the rule has to know how the room is lit. A room with glass on two opposite walls is lit from both ends and is only half as deep as it measures. A cross-lit room tolerates about half again the depth of a single-sided one. Without both corrections, a correctly planned Georgian drawing room with windows on two walls fails its own rule.

## What the three-level cascade test found

Filling `english-georgian` put a third level in Georgian's chain — and it contributed **0%**, because Georgian specified all eight of those slots itself. **A fully-specified child makes its ancestors dead weight.** The cascade only pays where the middle layer `extends` rather than restates.

Converting two Georgian slots to `extends` made the third level appear in the provenance immediately. It also tripped the failure mode flagged when `extends` was designed: nine variant `op: replace` records naming ids no ancestor defines, which silently become `add`. `check_kits.py` caught all nine. The mechanism works; it needs the checker to be safe.

## Next

The composer. It now has a scoring function, two worked examples of what good and bad look like against it, and a target: assemble groupings into a plan record that scores zero fatal.
