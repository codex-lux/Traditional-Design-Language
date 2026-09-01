# oq/the-parti-dissolved-its-own-dependencies — a Georgian main block asked to hold a service program the type put in outbuildings

*Status: OPEN · Raised in: WP-9.2, the precedents measured (1 Sep 2026)*

**`partis/centre-passage-double-pile.json` names eleven enclosed ground-floor rooms and a porch,
and the plan built from it places twelve enclosed spaces. Gunston Hall — the one exemplar whose
first-floor spaces its survey enumerates — has six, in a footprint within a foot of the generated
one.** That is the whole of the Chomsky complaint, measured.

| | source | main block | bays | ft/bay | enclosed ground spaces |
|---|---|---|---|---|---|
| Drayton Hall, 1738–42 | HABS SC-377 | 70'-5" × 52'-2" | 7 | 10.06 | 6 (named in the survey) |
| Gunston Hall, 1755–59 | HABS VA-141 | 60'-10" × 40'-11½" | 5 | 12.17 | **6** |
| Hammond-Harwood, 1774–77 | HABS MD-251; width from the house's own institution | **49 ft wide** (HABS's 1940 "approximately 44x42'" is low) | 5 | 9.80 | — (five-part; not established) |
| `tidewater-georgian-careful` as placed | this corpus | 60.0 × 40.0 | 6 | 10.0 | **12** |

Gunston Hall's first floor, from the survey: a central passage, a narrow side passage, and four
rooms — the Palladian Room, the Chinese Room, the Chamber, the Little Parlour.

**Compare clear area to clear area, which an audit forced.** Gunston Hall's 2,492 sf is an
*exterior foundation* measurement and its walls are "about two feet thick", so its clear area is
2,100–2,195 sf and its mean space **350–366 sf**. The corpus's placement carries no wall thickness
at all — its rectangles sum to 2,341 sf of a 2,400 sf footprint — so its twelve spaces average
**~195 sf**. The ratio is about **1.8**, not the 2.08 an earlier version of this entry printed by
dividing an exterior-foundation figure by six.

**And the parti's declared `bay_module_ft: 9` is below all three exemplars** (9.80, 10.06, 12.17),
which is the direction that produces slivers.

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

**Three answers, and they cost very different amounts.**

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
