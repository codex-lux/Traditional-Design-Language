# oq/the-parti-dissolved-its-own-dependencies — a Georgian main block asked to hold a service program the type put in outbuildings

*Status: RULED 2 Sep 2026 · Raised in: WP-9.2, the precedents measured (1 Sep 2026)*

**`partis/centre-passage-double-pile.json` names eleven enclosed ground-floor rooms and a porch,
and the plan built from it places twelve enclosed spaces. Gunston Hall — the one exemplar whose
first-floor spaces its survey enumerates — has six, in a clear extent about 3 ft smaller on each
dimension than the generated one.** That is the whole of the Chomsky complaint, measured.

| | source | main block | bays | ft/bay | enclosed ground spaces |
|---|---|---|---|---|---|
| Drayton Hall, 1738–42 | HABS SC-377 | 70'-5" × 52'-2" | 7 | 10.06 | 6 (named in the survey) |
| Gunston Hall, 1755–59 | HABS VA-141 | 60'-10" × 40'-11½" | 5 — **inferred**, see below | 12.17 | **6** |
| Hammond-Harwood, 1774–77 | HABS MD-251; width from the house's own institution | **49 ft wide** (HABS's 1940 "approximately 44x42'" is low) | 5 | 9.80 | — (five-part; not established) |
| `tidewater-georgian-careful` as placed | this corpus | 60.0 × 40.0 | 6 | 10.0 | **12** |

Gunston Hall's first floor, from the survey: a central passage, a narrow side passage, and four
rooms — the Palladian Room, the Chinese Room, the Chamber, the Little Parlour.

**Gunston Hall's bay count is a reading of the survey's fenestration prose, not a quotation from
it**, and the table's ft/bay column divides by it. HABS VA-141 says *"There are four large windows
on each of the north and south facades, with a pair of smaller windows flanking the main doors"*
and *"five dormer windows each"*; two large windows either side of a centre carrying the door reads
as five bays and the dormer count corroborates it. Drayton Hall's 7 and Hammond-Harwood's 5 ARE
quoted (*"7-bay front"*, *"Central portion five bays wide"*). The distinction is marked here
because the whole point of the row is that the corpus's module is below all three, and one of the
three divisors is mine.

**Compare clear area to clear area, which an audit forced.** Gunston Hall's 2,492 sf is an
*exterior foundation* measurement and its walls are "about two feet thick", so its clear area is
2,100–2,195 sf and its mean space **350–366 sf**. The corpus's placement carries no wall thickness
at all — its rectangles sum to 2,341 sf of a 2,400 sf footprint — so its twelve spaces average
**~195 sf**. The ratio is about **1.8**, not the 2.08 an earlier version of this entry printed by
dividing an exterior-foundation figure by six.

**And the parti's declared `bay_module_ft: 9` is below all three exemplars** (9.80, 10.06, 12.17),
which is the wrong direction for the type. **It is not, however, the mechanism of the slivers, and
an audit struck that claim**: no plan record declares a parti (`plan.schema.json` sets
`additionalProperties: false` and has no such property), so the placed sheet used
`derive_footprint`'s own 10.0 ft default; and the module is area-neutral anyway, since `H = need /
W`. The mechanism is the room count.

**Six of the parti's eleven rooms are service** — butler's pantry, back hall, powder room,
kitchen, pantry, breakfast room — and **all three exemplars house their service somewhere else.**
Gunston Hall's kitchen was a separate building. Drayton Hall's service is in the raised basement
around a Servant's Hall with an 8'-0" fireplace. Hammond-Harwood puts its service in wings:
*"the end wings are about 34' x 18, and the connecting links are 18 long."*

**The corpus already says so, three times, and nothing can act on any of it.**

- `massings/catalog.json`, `four-over-four` — the massing this plan declares — `expansion_logic`:
  *"Flanking dependencies connected by hyphens (the five-part scheme), or a rear service ell.
  Growth must respect the axis or the whole logic fails."* Read by a counter, an HTML dump and an
  API echo; nothing acts on it.
- The parti's own `scaling.note`: *"Grows to seven bays and then wants dependencies rather than
  more width."* `grows_by` has exactly one reader, `mcp_server/core.py:1364`, echoing it into a
  response.
- `partis/five-part-palladian.json` does it correctly — `westhyphen` and `easthyphen`, both typed
  `gallery-corridor`, with kitchen, pantry, breakfast, butler's, powder, mud, laundry and garage
  beyond them, and the groupings `dependency-and-hyphen` and `garage-and-hyphen`.

So the corpus holds a faithful diagram of the type with its service in dependencies, and a second
diagram calling itself the same type with the dependencies dissolved into the main block. **And the placer cannot grow the house at all**: `derive_footprint`
sets `H = need / W`, so adding a bay trades depth for width **at constant area** — measured 2,405.0
sf at every bay count from 4 to 10 on this plan. Its exit test is a DEPTH test; shape has no vote.
The one thing that can make a room bigger is `compose.repair()`, which widens a declared `width_ft`
on a furniture or width-floor finding — **in the composer, and from the DECLARED record, so it
never sees the room that was drawn as a sliver.** Neither can build a dependency, and no room type
for one exists outside `five-part-palladian`'s two hyphens.

**Why this matters more than any scoring change.** WP-9.4 swept the search terms and moved
nothing, and this is why. Area was never the binding constraint — the ground program's own bands
sum to 1,376–4,402 sf against a 2,400 sf floor, so it fits. **Nine of the eleven slivers Lucas named are rooms INSIDE their area band and
OUTSIDE their width or proportion band** — the kitchen at 10 × 30 = 300 sf sits inside its
120–340 sf band while standing 67% over its proportion ceiling of 1.8. (Two are outside their area
band as well: `breakfast` at 189 sf against [80, 180] and `cl3` at 38 against [6, 24]. An earlier
version of this paragraph said "every one".) You cannot
score your way out of a program that does not fit the type; a stated macro-tree would arrange the
wrong twelve rooms more tidily.

## Lucas's ruling, 2 Sep 2026: (1) — strip the service out and build the dependency

**Chosen against its own cost, which was stated at the time and is the largest of the three.**
The diagram is to name what its exemplars are: a Georgian main block whose service is somewhere
else. That means the six service rooms leave `centre-passage-double-pile`, and the generator
learns to place a hyphen and a wing — which nothing today can produce.

**What the ruling commits the corpus to, and none of it is small.**

- **A dependency and a hyphen have to be placeable.** `derive_footprint` today has ONE growth mode
  (add a bay, at constant area) and its exit test is a depth test. A dependency is a second
  massing element with its own footprint, its own roof and a stated ridge relation to the main
  block — so the placer gains a choice where it now has none.
- **`expansion_logic` and `grows_by` get their first real readers.** `four-over-four`'s
  *"flanking dependencies connected by hyphens (the five-part scheme), or a rear service ell.
  Growth must respect the axis or the whole logic fails"* has a counter, an HTML dump and an API
  echo today. So does the parti's own *"Grows to seven bays and then wants dependencies rather
  than more width."* Both become executable.
- **`five-part-palladian` is the working model, not a rival.** It already carries two
  `gallery-corridor` hyphens with the whole service program beyond them, and it composes. Read it
  before designing anything: the vocabulary this ruling needs mostly exists there.
- **The exemplar list stays, and that is the point of choosing (1).** Under (2) it would have had
  to go.

**What was NOT ruled and still has to be decided before code:** whether a dependency is a second
plan LEVEL, a second massing element, or a new record kind; whether the hyphen is a room
(`gallery-corridor`, as five-part has it) or a connector with its own schema; and what a brief
says when the site cannot take a dependency. Those are authoring decisions and this ruling does
not make them.

**Three answers were offered, and they cost very different amounts.**

1. **Strip the service out of the diagram and teach the generator to build a dependency.** The
   honest one and by far the most work: it needs a hyphen and a wing in the placement, which
   nothing today can produce, and it turns `derive_footprint`'s single growth mode into a choice.
   It would also give `expansion_logic` and `grows_by` their first real readers.
2. **Keep the diagram and say what it is.** `centre-passage-double-pile` becomes an explicitly
   modern house in a Georgian envelope — legitimate, widely built, and it would need the parti's
   own prose to say so rather than naming three eighteenth-century exemplars it cannot produce.
3. **Make the composer prefer `five-part-palladian` when the brief's service program will not
   fit.** Cheapest, and it uses a diagram that already exists and is already correct. It needs a
   measure of "will not fit" — a room count or a service-area fraction against the massing's own
   `bays` — which is a threshold this corpus would have to author.

**The exemplars are not evidence for (2).** A parti that names Drayton Hall, Gunston Hall and
Hammond-Harwood is claiming to be the diagram those buildings are instances of. If the answer is
(2), the exemplar list is the thing that has to change.

**Related, and deliberately not folded in.** `oq/a-massing-states-its-structure-and-nothing-reads-it`
is the other half of the same reading — the stair hall's structural job — and
`oq/the-passage-is-divided-and-the-corpus-has-no-word-for-it` is a third. They are separable: this
one is about how many rooms, those are about where the walls go.


## The three open items, ruled 3 Sep 2026

The 2 September ruling chose option (1) — strip the service out and build the dependency — and left
three things explicitly undecided "before code". All three are settled now.

**1. A dependency is a SECOND MASSING ELEMENT**, not a second plan level and not a new record kind.
Ruled jointly with **OQ 40**, whose entry carries the full costing and the two refusals; the two are
the same question from opposite ends and ruling either alone is how they drift. In short: a level
would be silently drawn nowhere (`geometry.py` hands any index above 1 an empty source) and would
add its storey height to the main block's eave, making the dependency a third storey on top of the
house; a new record kind forfeits the `via` bridge and `attaches_to` for nothing.

**2. The hyphen is a ROOM, and WHICH room is chosen by style.** `breezeway` where the style's own
`style_variation` names it an open colonnade; `gallery-corridor` where the link is enclosed.

*That it must be a room at all is forced rather than preferred.* `rooms/butlers-pantry.json` carries
a HARD `must_adjoin kitchen` with `via: ["back-hall", "gallery-corridor"]`, and `plan_check`'s `via`
clause matches on the room TYPE of a room in `levels[].rooms[]`. A hyphen that is a connector with
its own schema is not in that array, so the bridge breaks and a hard rule fires **fatal on every
five-part plan**. The one existing precedent for the other answer argues against itself:
`compose.attach_garage` models the hyphen as a property of the attachment, and its
`hyphen_length_ft` is a **local variable used only inside two f-strings** — which is why that
figure, a `strong` machine-tested rule in *both* hyphen groupings, has never been evaluated on any
plan this composer has produced.

*That it is chosen by style is what the records already say.* `rooms/breezeway.json` **is** the
hyphen and nothing in the code knows: its `style_variation` for `english-palladian` gives
`name_in_style: "hyphen"` — *"always subordinate in height and in bay rhythm — the fault
`dependency-that-is-not-subordinate` is what happens when it is not"* — and for
`tidewater-georgian`, `"hyphen or colonnade"`, *"frequently an open colonnaded walk to a detached
kitchen"*. Its `faults` already list `dependency-that-is-not-subordinate` and `co-equal-mass`; its
`slots` already include `wing_strategy`; its `massing_fit` already includes `five-part-palladian`.
Its own description says the dogtrot, the ranch breezeway and the Palladian hyphen *"are the same
idea at three social altitudes"* — which is the ruling, written by the corpus before the question
was asked. `gallery-corridor` is the enclosed case and is what `five-part-palladian` uses today.

**`build/compose.py` states the opposite in a comment and must be corrected in the same change**:
*"The catalogue has no room type for a pure link, and inventing one here would be a room with no
furniture, no daylight rule and no privacy rank."* That is false — `breezeway` has all three — and
the objection it rests on (that every candidate room hard-requires a kitchen door) is true of
`back-hall` and `mudroom` and false of `breezeway` and `gallery-corridor`.

Two record fixes come with the ruling. `breezeway`'s `must_adjoin hall` exception is **prose**, and
`plan_check` intersects a rule's `exceptions` with the style-id chain, so it is inert — the OQ 59
failure mode again, a record stating the right thing where no checker can read it. And `breezeway`
carries no `void` block, so it would be placed and heated as a solid rectangle despite its own
`critical_dimension` saying **BOTH ENDS MUST BE OPEN**.

**3. What a brief says when the site cannot take a dependency: it REFUSES, in the shape the corpus
already has for exactly this.** `plan.schema.json`'s `$defs.unplaced` — a prose `reason` plus
`needs` and `have` objects carrying the same figures as fields — is the settled form for "declared,
could not be placed, and here is why", and a refused dependency is that. The arithmetic is
`main_W + hyphen_length_ft + dependency_W` against `compose.lot_usable_width_ft`, which already
exists; what is missing is only that nothing knows a dependency's width. `compose.py` already writes
the sentence *"At {bays} bays this diagram is at the width it grows to; further area wants a
dependency, not more room"* and nothing acts on it.

### The constraint that decides this package's scope, found while costing it

**Stripping the six service rooms DELETES THE GARAGE.** `attach_garage` anchors on a mudroom, or on
a kitchen to build one beside, and `centre-passage-double-pile` has neither once the kitchen leaves;
the function then refuses with *"this diagram has neither a mudroom for the car to land in nor a
kitchen to put one beside"*. So on the shipped Georgian brief the ruling to build dependencies
would, before any new code, remove the one dependency this corpus can currently place. **The strip
and the dependency placement cannot ship as separate packages**, and the garage becoming a
dependency is what makes the strip survivable.

Two things measured while costing, both worth having: the stripped ground floor is `porch, passage,
stair, drawing, dining, library` — **five enclosed spaces plus the portico, against Gunston Hall's
six**, which is this entry's own target hit exactly. And three of the four contested corners
`geometry_cp` reports on this parti are service rooms the strip removes, so some of the wing
pressure resolves for free.

One thing the strip breaks that no score will notice: the shipped brief's `must_have:
"breakfast-room"` stops being satisfiable, and `SCORE_AXES` has no program axis, so it degrades in a
log line. That is to be stated, not quietly fixed by widening `must_have`.
