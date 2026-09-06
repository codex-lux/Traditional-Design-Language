# oq/the-proving-engine-cannot-place-a-second-massing-element — the tag that costs a plan its proof

*Status: OPEN · Raised in: WP-11.9, the six layers that read one rectangle (6 September 2026)*

**OPEN — `build/geometry_cp.py` builds every room as `x = NewIntVar(0, Wi)` with `x + w <= Wi`:
one rectangle, one non-negative coordinate space. Handed a plan with a dependency it REFUSES,
and `auto` falls back to the hill-climb naming the reason. So on any plan with a second massing
element the engine that PROVES is unavailable and the engine that SEARCHES carries every
finding.**

That refusal is correct and was built deliberately — WP-10.1 found the alternative was worse.
Given a tagged plan the CP model had placed a garage at x = 50 of a 0–70 block while
`footprint.blocks` described an element at x = 84–114, and it **flattered the fatal count**,
because rooms crammed into one rectangle are all trivially reachable. Refusing beats lying.

## What makes this a question now rather than a note

WP-11.9 taught the six layers below the placer about massing elements, and measured the effect
of hand-tagging `plans/tidewater-georgian-careful.json`'s six service rooms as a west dependency
with the back hall as its hyphen:

| `heuristic` | untagged | tagged |
|---|---|---|
| fatal | 9 | **6** |
| serious | 61 | **53** |
| relaxations | 8 | **6** |
| rooms outside their own band | 6 | **2** |
| service rooms drawn ≥10% off their declared area | 5 / 6 | **3 / 6** |

WP-10.1 measured the same tags **trebling the fatals**; after the six layers they improve the
plan on every axis but one. So the tag is now the right description of that house — a Tidewater
Georgian with its service in a dependency joined by a hyphen is what the parti's own three
exemplars are — and `PLAN-OF-ACTION.md`'s WP-11.9 ends with *"then the tags on the shipped
record"*.

**It was not authored, and this is the only reason.** `tidewater-georgian-careful` is one of the
two plans this corpus proves. Verified on the tagged record:

```
engine="cp"   -> "could not solve with CP-SAT: this plan has more than one massing element
                  (a dependency), and the CP model places every room in a single rectangle."
engine="auto" -> {"engine": "heuristic", "fallback": "engine", "reason": "...fell back to the
                  hill-climb, which places each element in its own"}
```

Tagging trades a proved reference plan for a searched one. That is a precondition, not a cost a
drawing package may absorb on its own.

## What must be ruled

1. **Does the CP model get one coordinate space per element, or one shifted space?** Each room's
   `x` bounded by its own element's `[x, x+W]` is the direct reading and costs nothing in the
   objective; it does mean the model no longer has a single origin, and `geometry_cp` reads its
   slicing tree off a heuristic layout (WP-2.3), which already knows the elements.
2. **What does the relaxation ladder do with an element boundary?** `_RANK` is
   `("wall", "axis", "shape")` and an element edge is none of those. It is not a declared wall —
   it is the massing — so it is arguably above all three and undowngradable, which is a claim
   worth stating before it is coded.
3. **Is a multi-element proof affordable?** The two shipped plans take 11.3 s and 29.6 s at one
   rectangle; three elements is three coordinate spaces and an abutment constraint per pair.
   `BUDGET_BATCH_S` is 40 s. Measure before building, not after.

## What is NOT the question

Whether the six layers should know about elements — WP-11.9 answered that, and they do. Nor
whether a hyphen is an element: ruled 5 September 2026, it is. And **do not close this by
removing the refusal**: a CP model that flattens two elements into one rectangle reports a lower
fatal count than the truth, which is the OQ 52 family in the most expensive place in the tree.
