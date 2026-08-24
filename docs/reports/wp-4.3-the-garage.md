# WP-4.3 — the garage

*24 August 2026. Closes the package. Companion to `groupings/garage-and-hyphen.json` (new), `build/compose.py`'s `attach_garage()`, and `tests/test_garage.py`.*

## The acceptance line, and why it is about the composer rather than the validator

`PLAN-OF-ACTION.md` asks for something unusually specific: *"The spec Colonial's garage-beside-primary-bedroom fatal cannot be reproduced by the composer."*

That fatal is real and already caught. `plans/spec-builder-colonial.json` puts a two-car garage against the primary bedroom, and `plan_check` reports it fatal because `rooms/garage.json` forbids the adjacency outright — "a bedroom over or beside a garage is a noise, fume and fire-separation problem in one, and the fire separation is code." The validator has always seen it.

The package is about the generator, not the critic. A composer that *can* produce that plan and then gets told off is not the same as one that cannot produce it, and the difference is structural rather than a matter of adding a check. Placing a garage **by adjacency** asks "what may this room touch?" — and every locally plausible answer to that question is exactly how the spec plan ended up as it is: the garage wants the mudroom, the mudroom wants the kitchen, the primary suite wants the quiet end, and on a single-storey plan those pressures put the bays against a bedroom wall with no individual step looking wrong. Placing it **by attachment** asks a different question — "where does a dependency land on this skeleton?" — and the answer comes from the massing's own expansion logic. The garage ends up with exactly one interior neighbour, that neighbour is a threshold room, and the bedroom question never arises.

## What was built

**`groupings/garage-and-hyphen.json`** — a new grouping, narrowing `dependency-and-hyphen` to the one modern function no traditional style has a rule for. It exists separately because the garage is the only dependency whose *placement* has to be constrained rather than merely preferred: a library in a flanking wing that lands beside a bedroom is an oddity; a garage that does is three failures at once. Eight internal rules (the bedroom prohibition and the service-side approach are `hard`), and 14 `attaches_to` entries giving position and fit per massing — from `five-part-palladian` (canonical: the one traditional composition that already has a place for a subordinate volume at the end of a link) through `foursquare` (atypical: the cube resists subordination, its whole dignity is that it is one volume) to `townhouse-row` (**forbidden**: party walls on both flanks and a facade that belongs to the street). Proportions — ridge at 60–80% of the main ridge, hyphen 12–20 ft — are taken unchanged from `dependency-and-hyphen` rather than invented a second time; the prohibitions come from `rooms/garage.json` and IRC R302.5.1; the positions are marked editorial.

**`build/compose.py`'s `attach_garage()`** — replaces the old refusal ("it is not being invented here — pick a parti that carries one") with real placement. It runs after the plan record exists, because the massing is not settled until then. It looks up the chosen massing in the grouping's `attaches_to`; places the garage where that entry says; refuses with a stated reason where the entry is `forbidden` or absent; and doors the garage to exactly one room.

**Four `garage_strategy` bindings** on the living nodes that lacked one — `french-provincial-farmhouse`, `shingle-style`, `new-mexico-adobe`, `norman-vernacular` — taking the corpus to 58 bindings (50 `specified`, 8 `extends`) and every living style covered.

## What the corpus turned out to already know, and the two dead ends worth recording

The hyphen was first modelled as its own room, typed `back-hall`. That fails. Then as a `mudroom`. That fails too, and for the same instructive reason: **every service room in the catalogue that could plausibly be a hyphen carries a hard `must_adjoin` on the kitchen** — the back hall because "the back hall's entire reason for existing is to connect the kitchen to the rest of the house," the mudroom because "the groceries have to reach the kitchen without crossing a living space." A 14 ft link out to a detached dependency cannot also touch the kitchen. Any hyphen modelled as one of those rooms is born failing a hard rule.

The catalogue has no room type for a pure link, and inventing one here would mean a room with no furniture, no daylight rule and no privacy rank — WP-4.5's business, not this package's. So the hyphen is modelled as what it physically is: **a property of the attachment**, its length carried on the garage record and governed by the grouping's own 12–20 ft rule, rather than a node in the plan graph.

That turned out to be what the corpus already said. `rooms/back-hall.json` states the modern sequence outright — *"in the modern plan they are consecutive: garage, mudroom, back hall, kitchen, and the sequence is the same one the tradesman's entrance had"* — so the room the garage lands on is the **mudroom**, which is also exactly what `rooms/garage.json`'s own `must_adjoin` requires by direct door. Both rules are satisfied without amending either. An earlier attempt did amend `rooms/garage.json` (adding `via: ["back-hall"]` to relax the direct-door reading) and was reverted once the sequence in `back-hall.json` was found: a speculative schema loosening that the data did not need is worse than no change.

Where a diagram has no mudroom, the composer adds one — doored to the kitchen (its own hard rule) *and* to the back hall where one exists, because adding a mudroom the existing back hall cannot reach would satisfy the garage's rule by breaking the back hall's.

## Verified against the acceptance criteria

- **The fatal is unreproducible.** `tests/test_garage.py` runs both shipped briefs, all four candidates each, every level, and asserts no garage shares a door or declared adjacency with any sleeping room. It also asserts the *structural* property the guarantee rests on — a composed garage has **exactly one** interior neighbour, and that neighbour is a mudroom — because a garage with several neighbours is back to being placed by adjacency even if a particular run comes out clean.
- **A guard on the guard:** a test asserts the hand-authored spec Colonial *still* trips the fatal. Without it, the acceptance test could pass because the rule stopped working rather than because the composer got better.
- **Refusal is tested too.** `side-hall-double-pile` — a party-walled town-house diagram the grouping deliberately does not receive — must produce a stated `JUDGMENT` in the decision log and no garage, rather than a garage tucked somewhere plausible.
- **The rule lives in the data.** A test asserts `garage-and-hyphen` states the bedroom prohibition as a hard rule of its own, so a second generator written against this corpus inherits it without reading `compose.py`.
- **Every living style specifies a strategy** — tested against `dist/taxonomy.json` rather than a hand-maintained list.
- 8 new tests; full suite 304 passed. `check_all.py`: all 21 checks green. Both briefs still rank identically (Side-Hall Town House first at 0 fatal), so placing a garage did not perturb the composer's judgment about anything else.

## One finding left standing on purpose

A correctly-sized, correctly-glazed garage reports one `serious` daylight-depth finding that cannot be designed away. Two bays are 20 ft × 22 ft at the *shallow* end of the room catalogue's own band — a 16 ft car plus clearance — and no window arrangement inside the room's own 0–10% glazing band reaches the back wall. The finding is unsatisfiable rather than wrong.

The garage is deliberately not distorted to silence it: not made shallower than a car, not over-glazed past its own band, and the rule is not suppressed. The composer states in its decision log that it knows, and the question of where the fix belongs — exempt non-habitable rooms, add an opt-out to the room record, or leave it — is recorded as **OQ 31**. It is a new category for this corpus: not "unjudged," which the system handles well, but *judged, and the judgment does not apply*.

## Not done

The vehicle-door orientation rule ("turned off the principal elevation... never forward of the facade plane") is stated in the grouping and carried in the garage's note, but nothing enforces it — that needs the geometry solver to know which wall faces the approach, which is WP-2.3 territory. Likewise "no habitable room above the bays": the composer places rooms, not volumes, and says so in the log rather than pretending to have checked. Both are real gaps, flagged in the output rather than left for a reader to discover.
