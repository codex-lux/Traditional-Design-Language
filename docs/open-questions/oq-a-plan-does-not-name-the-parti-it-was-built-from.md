# oq/a-plan-does-not-name-the-parti-it-was-built-from — so no checker can hold a plan to the diagram it is a house of

*Status: OPEN · Raised in: WP-11.6, the record says what it means (5 September 2026)*

**OPEN — a plan record names its style, its massing and its groupings, and not its parti. So
nothing can check that a plan states what its own diagram declares, and WP-11.6's two missing
stacking claims had to be found by a person reading the two files side by side.**

## The measurement

All sixteen records under `plans/` and `plans/reference/`:

```
parti = None   × 16
```

`spec-builder-colonial.json` and `tidewater-georgian-careful.json` carry
`massing: "four-over-four"`; the fourteen reference plans carry neither. The parti reaches the
placement as an ARGUMENT — `geometry.solve(plan, parti)`, `core.load_parti(pid)` — supplied by
whoever is calling, and never written down on the record that results.

## What that costs, concretely

`partis/centre-passage-double-pile.json` declares five `stacks_over` claims:

| room | claim | on the Tidewater plan before WP-11.6 |
|---|---|---|
| `landing` | `stair` | **absent** |
| `upperpassage` | `passage` | **absent** |
| `primary` | `drawing` | present |
| `primarybath` | `butlers` | present |
| `hallbath` | `powder` | present |

Three of five. Nothing detected the gap for the life of the plan, and the two that were missing
are the two the diagram is NAMED for — a centre passage that runs through both storeys and a
stair that lands where it left. `build/check_stacking.py` now holds every claim against the
level relation the field means, and it explicitly cannot hold a plan against its parti, saying
so in its own docstring rather than joining on matching room ids, which would be inventing a
fact from a coincidence.

## The wider shape

This is not only about stacking. A parti states `doors`, `exterior_walls`, `lit_from`,
`level`, `grows_by`, `structural_logic` and `expansion_logic` per room; a plan restates some of
them and drops others, and **no layer compares the two**. `compose.py:662` is the one writer
that copies `stacks_over` across, so a COMPOSED plan carries what its parti declared at the
moment it was composed — and then the parti can change underneath it and nothing notices.

## What must be ruled

1. **Should a plan name its parti?** A `parti` key on the plan record is one schema field and
   makes the whole class of check possible. Against it: a hand-authored plan may legitimately
   be a house of no diagram, and a required field would force an author to name one falsely.
   An OPTIONAL field with a checker that reports *how many plans can be checked* — the
   `check_inheritance.py` shape, a ratchet on the unjudged count — avoids that.
2. **Is a divergence from the parti an ERROR or a FACT?** A plan may drop a parti's claim
   deliberately: the diagram is a type and the house is an instance. If so the plan needs a way
   to say *"declined, and here is why"*, which is `declined_packs` one layer over and a
   precedent worth reusing rather than reinventing.
3. **Which fields are the parti's to govern?** Stacking, adjacency and level are structural and
   travel. Room dimensions do not — the parti states none. Somewhere between them is
   `exterior_walls`, which both documents carry and which CLAUDE.md already records as
   *"aspirations, not rectangle edges"*.

Until it is ruled: **the join does not exist, and no checker may fabricate one.**
