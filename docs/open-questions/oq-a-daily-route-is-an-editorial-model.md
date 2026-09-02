# oq/a-daily-route-is-an-editorial-model — four fault tests ask who walks where, and a door graph cannot answer

*Status: OPEN · Raised in: WP-9.1, the arbiter for arrangement (1 Sep 2026)*

**The corpus has faults about ROUTES and no vocabulary for one.** `ceremonial-front-door` tests
`daily_circulation_routes_through_the_formal_entry_hall`; `the-room-nobody-enters` tests
`principal_room_daily_routes_through_it`; `service-route-through-the-formal-plan` tests
`service_routes_crossing_a_formal_room`; `primary-suite-off-the-formal-hall` counts thresholds
from the public way. Every one of them presupposes a model of household movement — which
origin-and-destination pairs count as journeys people actually make — and **a door graph states
what connects to what, never who walks it.** Until WP-9.1 all four were permanently unjudged.

**What was built, and why it is marked editorial.** `build/arrangement.py::ROUTE_MODEL` is a
closed table of three journeys, each quoting the room record whose prose it reads and each
verified against that record by `check_openings.check_basis` — the same machinery that keeps
`openings/grammar.json` honest:

| route | from → to | read from |
|---|---|---|
| `rt-arrival` | threshold → public | `rooms/centre-passage.json` — *"parlor one side, dining room the other, is the canonical arrangement"* |
| `rt-service-food` | kitchen → dining-room | `rooms/kitchen.json` — *"Food travels hot and the route must not cross the entry sequence or a public circulation"* |
| `rt-family-entry` | mudroom → kitchen | `rooms/kitchen.json` — *"THE SHOPPING ROUTE… walked twice a week with both hands full for the life of the building. Nobody draws it and everybody feels it."* |

It is deliberately small: every route is one the corpus already describes in words, and nothing
was added because it seemed plausible. A route absent from the table is not a route this corpus
denies — it is one nobody has written down, and the fault that needs it stays unjudged.

**The question is where the model should live.** Three positions, and the choice is a real one:

1. **Leave it in `build/arrangement.py`** (today). Cheapest, and honest — it is marked
   `kind: editorial`, it carries a 200-character honesty note, and its citations are checked.
   But it is a piece of *corpus judgment* sitting in a *build script*, which is the shape of
   thing this project has repeatedly regretted: a rule in code is a rule no one browsing the
   corpus can find, argue with, or cite.
2. **Give the fault corpus the field.** A route-bearing fault would declare the journey its test
   counts, beside the test, in `faults/*.json` — the way `applies_when` now sits beside the
   expression it guards. Most faithful to "prose stays beside the test", and it makes each
   fault's presupposition visible at the point of use. Costs a schema change and an edit to four
   records.
3. **A `routes/` layer of its own**, on the `openings/grammar.json` pattern — a document, a
   checker, totality proved by enumeration. Right if the model is going to grow past a handful
   of journeys; considerable overbuild if it is not.

**What decides it is whether the model grows.** At three routes, (1) is proportionate. The moment
a fourth fault wants a journey the table does not hold — or a style wants to say that ITS
tradition walks a different route, which `rooms/centre-passage.json`'s own `style_variation`
block already does in prose for the Charleston single house — the model stops being a small
closed table and (2) or (3) is owed.

**Not to be confused with OQ 92.** That question ruled furniture ARRANGEMENT in and furniture-
driven SIZING out. This is one level up and about circulation rather than furniture: it asks who
moves through the rooms, not what stands in them. The two share only the word "arrangement".
