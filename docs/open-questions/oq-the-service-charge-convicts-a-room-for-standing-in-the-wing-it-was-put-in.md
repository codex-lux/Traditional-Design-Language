# oq/the-service-charge-convicts-a-room-for-standing-in-the-wing-it-was-put-in — the OQ 52 family in the placer's own objective

*Status: OPEN · Raised in: WP-13.5, the container (16 September 2026)*

**`geometry.principal_and_service_score` charges a service room 2.0 points for not reaching the
wall opposite the entrance front, and decides "reaching" with
`_touches_wall(rect, wall, W, H)` where `W, H` are the MAIN BLOCK's. A kitchen in a west
dependency reaches no wall of the main block at all, so no laying of that dependency can avoid
the charge. It is charged anyway, every candidate, and nothing anywhere says the question could
not be answered.**

That is the OQ 52 family — a defect reported where none is possible — and it is a SEVENTH layer
reading the main block as the whole building, after the six WP-11.9 taught and the eighth
(`axis.front_openings`) raised beside this one.

## The measurement

`plans/tidewater-georgian-careful.json`, `engine="heuristic"` (deterministic), read two ways:

| | main block | butlers | kitchen | total service charge |
|---|---|---|---|---|
| one rectangle | 63.00 × 38.17 | 2.0 | **0.0** | **2.0** |
| as shipped (container) | 45.00 × 37.24 | 3.0 | **2.0** | **5.0** |

The two halves are different in kind and must not be quoted as one number:

- **The kitchen's 0.0 → 2.0 is the defect.** It stood on the main block's N wall before and is
  now in the `service` dependency (x −21.81 to −7.00, y 5.28 to 26.56), where `_touches_wall`
  against a 45.00 × 37.24 box can only ever answer no.
- **The butler's pantry's 2.0 → 3.0 is a real move**, not the instrument: it is drawn as a
  4.95 × 37.24 ft strip spanning the whole depth of the block, so it touches the S front (+3.0)
  as well as the N rear (which clears the +2.0). Nothing is wrong with that reading.

Within its own element the kitchen is not at the rear either — the `service` box runs y 5.28 to
31.96, midline 18.62, and the kitchen's centre is 15.92 — so an element-aware version of this
term would still charge it. **The question is not whether the kitchen is well placed; it is that
today the term cannot tell "in the wrong half" from "in another building".**

## The precedent, which is in this corpus already

WP-11.6's layer 3 found exactly this shape in `vertical_score`: a `stacks_over` claim naming a
room in another element was *"CHARGED 40 points and told 'is drawn clear of it', for a failure
no placement could avoid"*. It was fixed by returning COULD NOT EVALUATE with its reason, and
`vertical_score` fell 114 → 74 on the driven fixture. The same repair is available here and it
is a ruling rather than an edit, because **a score is not a checker**: an unjudged verdict has an
obvious spelling in `plan_check` and none in a float a hill-climb ranks on.

## What has to be ruled

1. **What a soft term does with a question it cannot ask.** Charging zero makes a wing room
   strictly cheaper than a block room that fails the same preference, which is a thumb on the
   scale for putting service in a wing — and this corpus does not want the objective arguing for
   a massing decision. Charging the current 2.0 keeps a constant that is the same for every
   candidate and therefore decides nothing, which is defensible and is a false report. Charging
   against the room's OWN element asks a real question and needs (3).
2. **What the rear of a dependency means.** The main block's rear is defined against
   `context.entrance_faces`. A detached wing has no entrance front of its own, and the one
   available reading — the face away from the main block — is a different rule, not the same one
   in a smaller box.
3. **Whether the term should see a wing at all.** `five-part-palladian` puts the whole service
   programme beyond a hyphen; on that diagram *every* service room is exempt and the term does
   nothing. A term that is inert on the type it was written about is worth knowing about before
   it is repaired rather than after.

## What is NOT the question

**Do not close this by deleting the charge**, and do not close it by re-weighting: either moves
a placement on every plan in the corpus, and WP-13.5 is a record edit. Do not "fix" the kitchen
by moving it back into the block — the ruling of 15 September put it in the dependency and the
measurement above is a fact about the instrument, not about where the kitchen belongs.

## Related

- `oq/the-entrance-porch-can-be-drawn-on-the-back-and-no-layer-says-so` — the same package, the
  same function's neighbour, and the opposite failure: there the charge is real and nothing
  REPORTS it.
- `oq/the-facade-layer-counts-a-dependencys-windows-as-bays-of-the-front` — the eighth layer.
- `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` — the standing question
  about the layers BELOW the placer. This one is INSIDE it.
