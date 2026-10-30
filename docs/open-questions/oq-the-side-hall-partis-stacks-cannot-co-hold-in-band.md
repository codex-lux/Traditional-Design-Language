# oq/the-side-hall-partis-stacks-cannot-co-hold-in-band — the side hall's three stacks and its rooms' bands do not fit one house

*Status: OPEN · Raised in: Phase 17, the investigation of Lucas's refused candidates (29 October 2026)*

**OPEN, RE-SCOPED 30 OCT 2026 (the audit of Phase 17, finding 42): read the amendment below
first.** *What this paragraph said, and what no longer holds:* "`partis/side-hall-townhouse.json`
declares three structural stacks (the landing over the stair hall, the primary chamber over the
front parlour, a chamber over the back parlour), and a read-only feasibility spike that held every
fact, every proportion band, every declared size and every door HARD on CP-SAT proved that no
placement holds any two of them with every room inside its own band ... The refusal the composer
returns for this diagram is therefore the house's own refusal on its parti's claims, not the
instrument's." There was never a back-parlour claim; the third claim was a BATH over the powder
room, which ruling 5 moved to `wet_stack_with` in the same tranche; the spike's core named two of
the three and so did not establish "any two"; and on the parti as it stands the prover finds a
placement holding every judged fact. The refusal is the instrument's at the compose budget, not a
proof about the house.

## Amendment, 30 October 2026 (the audit of Phase 17, finding 42)

- **The parti carries two structural stacks and one servicing claim.** At `739ff29`:
  `landing stacks_over stair`, `primary stacks_over frontparlor`, and `primarybath wet_stack_with
  powder` -- the last re-filed by ruling 5 (29 Oct 2026; bath over a wet room). At `6fcc665`, before
  the tranche, all three were `stacks_over`, the third being that same bath over the powder room.
  Neither tree carries "a chamber over the back parlour"; the description above was wrong when it
  was written.
- **The spike was taken on the pre-ruling-5 parti** (three structural stacks) and an in-memory
  model, and its core named two of the three. That establishes the pair it named, not "any two", so
  the "any two of its three declared stacks are incompatible" reading is WITHDRAWN rather than
  restated; nothing re-proved it pair by pair.
- **Measured on the parti as it stands:** the side hall instantiated on Lucas's brief (tidewater-georgian, 3,200 sf, four bedrooms, 3.5 baths) and placed by `engine="cp"` at 110 s returns FEASIBLE ("kept polish from phase A") in 111 s, with tiling, both stacks and bearing HELD and the hearth UNJUDGED (the parti states no fire); `drawability.assess` re-judges it DRAWABLE WHERE JUDGED (hearth unjudged), whole run held, no room over band, every door placed, not refused. Only declared exterior-wall pins were carried, the lowest rank. Measured twice, by the audit's verifier and again on the batch that writes this, one seed each on a shared four-core box, so the 111 s is a band; a found placement needs no repetition to exist. The product's refusal at the compose budget (the search's fallback, refused on `bearing, stacks`, after the prover returned UNKNOWN) is therefore UNDECIDED, the instrument's, and not PROVEN, the house's.
- **So the question is re-scoped.** It is no longer "the side hall's stacks cannot co-hold in band"
  but "the prover does not decide the side hall at the compose budget", which is the instrument's
  and a budget question (whether the compose budget should be long enough to find this house is a
  ruling, beside R11 and R12 of 30 Oct 2026). Option 2 below is also overtaken: one of the three
  WAS a plumbing claim, and ruling 5 moved it.

## What was measured

- The spike (session scratchpad, 29 Oct 2026): the side hall composed on Lucas's brief
  (tidewater-georgian, 3,200 sf, four bedrooms), facts + bands + sizes + doors hard, four workers,
  120 s, several seeds: INFEASIBLE, with a core naming two of the three stacks and the bands of the
  rooms they join. +1 bay: INFEASIBLE.
- On the product after Phase 17's first tranche (`scratchpad/measure.py 60`, quiet box): the prover
  does not decide at the compose budget and the search's fallback is refused on `bearing, stacks`.

## What a ruling would choose between

1. **Leave it.** The diagram is refused, said with its conflict set, and the composer fills the set
   from the pool (ruling 3); the side hall is passed over and named.
2. **Reclassify one of the claims.** *(Overtaken 30 Oct 2026: this said "None is a plumbing claim
   -- all three are rooms over rooms", and one was a bath over the powder room; ruling 5 moved it.)*
   The two that remain are rooms over rooms, and releasing one is an authoring act on the parti.
3. **Widen the side hall's bands or its rooms.** Not available: a band is the room record's, and
   loosening one to make a diagram fit is the move this corpus refuses.

## Not done

Nothing is edited. The plan of Phase 17 said in as many words that the side hall's refusal is
proven and is the house's; *corrected 30 Oct 2026:* it was proven on a parti this tranche changed,
and on the parti as it stands the refusal at the compose budget is undecided, not proven.
