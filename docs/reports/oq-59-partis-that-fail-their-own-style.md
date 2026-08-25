# OQ 59 — five partis that could not be recommended for the styles they were written for

*24 Aug 2026. Ruled by Lucas: "Fix all five + add the check."*

## The finding

Instantiating each parti against the first style in its own `styles` array and running
`plan_check` on the result: **five of twenty-one carried FATAL findings**. A fatal is 100 points
in the composer's ranking and full nativity is worth at most 140, so the composer — working
exactly as designed — would not recommend them. A `charleston-single-house` brief came back with
a centre-passage single pile. A Creole brief came back with a bungalow.

Nothing looked at this. `check_partis.py` (WP-4.5) checks that a parti is well **formed**: the
schema, the ids, the door graph closing, the styles being buildable ranks. It never checked that
the diagram **works** — that it satisfies the room catalogue's own hard adjacency rules, which is
what `plan_check` will hold any plan built from it to.

| parti | fatal | what |
|---|---|---|
| `cape-central-chimney` | 4 | none of them the parti's — see below |
| `five-part-palladian` | 4 | both hyphens typed `back-hall` |
| `charleston-single-piazza` | 2 | no door between the two ground rooms; landing rule |
| `creole-gallery` | 2 | duplicate room ids |
| `ranch-tripartite` | 1 | family room not reaching the kitchen |

## The check, and why it had to be differential

`check_partis.py` gains check 10. It composes each parti against its own first native style and
reports fatals as errors. Six seconds for the whole catalogue; `--no-compose` skips it.

Three of `cape-central-chimney`'s four fatals fire **identically for every parti** composed for
`cape-cod-colonial` — they are facts about that style's kit and elevation, not about any diagram.
A check that blamed the parti for them would generate false accusations against exactly the files
it exists to protect. So each parti is compared against a control diagram run on the same style,
keyed on the **requirement** rather than the measured value: the same style-level test fires for
every parti and each measures its own house, so the numbers differ while the failure is identical.
Fatals the control also produces are reported as a warning naming them as the style's.

## What was actually the partis'

- **`charleston-single-piazza`** — no door between drawing room and dining room. A single house
  is one room wide with the stair hall on the piazza side, so the two principal rooms share the
  wall between them and are connected through it; the hall is the second way between them, not
  the only one.
- **`creole-gallery`** — the repeating `chamber` generated `chamber1`, `chamber2`, which are the
  ids of the two chambers the parti already named. Every Creole brief for more than two bedrooms
  built a plan with duplicate room ids.
- **`ranch-tripartite`** — the family room reached the kitchen only across the eat-in area, and
  the validator counts a hop only through *circulation*. The tripartite ranch's whole point is
  that the three are one open zone; the door is the diagram saying what it always meant.
- **`five-part-palladian`** — both hyphens typed `back-hall`, whose own hard rule is *must_adjoin
  kitchen by direct door*. So both wings demanded a kitchen at their own end and only one wing
  has one. **An unsatisfiable requirement produced by naming a room wrongly, not by drawing it
  wrongly.** A hyphen is a connecting gallery: retyped `gallery-corridor`, with the service rooms
  regrouped into the one dependency that has the kitchen, and the butler's pantry moved into the
  block beside the dining room, where it belongs once it exists at all.

## Three validator facts that had to change with them

Each is a rule asking a correct plan for something it structurally cannot have.

- **`landing` → `stair-hall` is now `vertical_ok`.** A landing is the top of a stair and the
  stair hall is a storey *below* it. Read as a same-floor rule, only a house with a second stair
  hall upstairs could satisfy it. OQ 57 built this mechanism in the last package; nothing had
  used it.
- **`butlers-pantry` → `kitchen` gains `via: [back-hall, gallery-corridor]`.** Where the kitchen
  is in a dependency, the pantry is in the block and the kitchen is in another building. Without
  the via, the rule asked the pantry to be in two buildings at once. The dining-room rule keeps
  no via deliberately: a pantry that cannot touch its dining room is a pantry not doing its job.
- **`centre-passage` joins the `entrance-hall` EQUIVALENT group.** The front door opens into it
  and every principal room opens off it, which is the definition that group holds. It removed 2
  and 3 spurious *minor* findings from the two shipped plans, with fatal and serious unmoved —
  which is what says it removed noise and not signal. Two tests that used a centre passage as a
  stand-in for "not an entrance hall" were re-pinned to a back hall; their assertions are unchanged.

## Two of the five were not adjacency at all — they were unjudged reported as failed

These are the more dangerous kind, because the corpus's first discipline is that unjudged is not
passed, and this is that discipline inverted.

**`visible_chimney_count` was 0 when it should have been None.** `roof.py` models gable-end
stacks only, and every branch that returns an empty position list says in its own note that it
did *not* model the case — a central stack, a hipped roof with no gable end, a ridge it could not
judge. `elevation.py` reported that as a count of zero, which handed the fault corpus an evaluated
measurement where it had none, and `faults/chimney-omitted.json` duly fired **fatal on a parti
named `cape-central-chimney` for having no chimney**. It is None now, and `plan_check` drops a
None measurement rather than letting the evaluator throw on it and swallowing the exception.

**A fault finding quoted the wrong test.** A fault with `secondary_tests` can have its primary
*pass* and a secondary fail; `plan_check` read `results[0]` and printed the passing number as the
evidence — *"The House With No Fire: 2 against at-least 1"* on a Cape with two chimneys. Every
number in that sentence is right and the claim is nonsense.
`core.check_measurements` now returns `failing` beside `results`.

## Outcome

**21 of 21 composable.** A Charleston brief returns the Charleston single; a Creole brief the
Creole gallery; a Cape brief the central-chimney Cape.

A `ranch-style` brief still returns `bungalow-open-linear`. The ranch parti carries 15 serious
findings against the bungalow's 3 and no fatal is involved, so that is the composer's weighting
working as designed on a diagram that is genuinely rougher. Left as it is, and said here rather
than quietly tuned.

## Raised, not fixed

- **OQ 63** — a fault's secondary tests are written for one style and applied to every style.
  `chimney-omitted`'s two secondaries name their own scope in their notes ("The Tudor Revival
  rule", "The Prairie test") and are being run against a Cape. That is why `cape-cod-colonial`
  cannot currently return a clean plan under any diagram, and the reason is not in its own data.
- **OQ 42** — `types_present` is not aliased, so the branch deciding whether an unmet rule is a
  *completeness* or an *adjacency* finding still tells a plan with a centre passage that it
  models no entrance hall. One line to fix, and its blast radius is a change in what the
  validator *says*, so it wants measuring against the reference corpus first.

## Verification

`python3 build/check_all.py` — 22 checks, 395 tests green. `tests/test_parti_composability.py`
is new (16 tests) and pins the whole-catalogue result, the differential attribution, each of the
five repairs, the three validator changes, and both unjudged-reported-as-failed bugs.
