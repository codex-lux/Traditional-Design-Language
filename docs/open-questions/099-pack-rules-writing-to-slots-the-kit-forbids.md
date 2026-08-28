# OQ 99 — 787 pack rules dimension a slot the resolved kit forbids, and nobody chose one of them

*Status: CLOSED 28 Aug 2026 · Raised in: From the inheritance backlog (WP-8.2, 28 Aug 2026)*

**RULED AND BUILT 28 Aug 2026 (WP-8.3) — absolute, with a human override.** A pack rule may not
write to a slot the resolved kit binds `forbidden`, *unless* that slot's own `packs` block names
that pack — which `choose_pack`'s own docstring already calls *"the only place a human has said
which pack wins"*. **Zero of the 776 qualify**, so the override strands nothing today and is not
claimed as coverage; it exists so a node that genuinely wants one dimension from an
otherwise-refused member has a way to say so, rather than leaving the refusal behind a decision
nobody can revisit. A test holds that "zero qualify" claim to the data, so it cannot go stale.

**The refused rule is MARKED, not deleted.** `eval_packs` flags it `refused_by_kit` with the
binding's own note; `choose_pack` will not choose a flagged row and returns
`how: "kit.forbidden"` so a reader sees an explicit refusal rather than an absence
indistinguishable from "no pack writes here". Deleting would have destroyed the measurement
itself — the 787 count IS the marks — and `check_addresses` reads these rows without ever
calling `choose_pack`, so a refusal placed only in the chooser would not have reached it. Same
discipline as `openings.py` marking an unrealisable opening `unplaced` and never removing it.
`eval_packs`' `kit` argument is **required and has no default**: a `kit=None` default would let
every call site keep the old behaviour by saying nothing, which is the failure the fault
schema's own note describes for a mistyped guard.

**THE DRAWN HALF NEEDED ITS OWN FIX, AND HALF OF IT IS STILL OPEN — this is the part to read.**
`build/elevation.py` never calls `resolve_packs` or `eval_packs`. It reaches packs by
`PE.resolve` and reads sixteen slots straight out of pack files, so the resolver-side gate does
not reach **a single figure it draws**. That second path was named in no plan and no open
question until this package. Swept over every style: 40 pass that generator's own scope gate, 15
of them forbid at least one slot it reads, and the exposure is **40 (style, slot) pairs**.

- **16 refused**: `transom_sidelight` 8 and `pilaster` 8. The entrance composition already
  carried a `use_sidelights` branch, so the kit's refusal simply decides it; both figures are now
  **absent rather than zero**, because a zero is a measured claim that the sidelight is nothing
  wide and that is a different statement from "this style does not have one".
- **24 read anyway and DISCLOSED** in the elevation record's `forbidden_slots_read_from_packs`:
  `frieze` 9, `belt_course` 6, `water_table` 6, and one each of `door_surround`, `cornice`,
  `window_head_wood`.

**Those 24 are deliberately not zeroed, and the reason is the open half.** A style whose resolved
kit forbids `frieze` while still passing a *classical* scope gate is two records contradicting
each other, not a number to silence. Zeroing them would pick a winner between the kit and the
pack's `applies_to` without anybody having decided which is right, on nine styles. Named,
counted, and left for a ruling. `cape-cod-colonial` is the case to look at first: its own
`pilaster` note reads *"The whole classical-apparatus group is forbidden at the family"*, and it
appears in this generator's classical gate.

**It shows on a shipped plan immediately.** `spec-builder-colonial` (`colonial-revival`) forbids
`transom_sidelight`; `sidelight_width_in` and `transom_height_in` are now absent from its
measurements and the entrance note says why, while `belt_course`, `frieze` and `water_table` are
listed as read anyway.

**AND THE FIRST THING IT FOUND WAS A DATA ERROR, NOT A PACK ERROR.** Making the refusal bite
turned two faults red on `spec-builder-colonial`, and the cause was that `colonial-revival`'s
resolved `transom_sidelight` binding was **`forbidden`, inherited from `gothic-revival-british`**
on an editorial note — a Gothic Revival prohibition on the one feature Colonial Revival is most
known for, while its own `defining_characteristics[1]` reads *"plus fanlight and/or sidelights"*
and its own c01 dimensions them at *"not wider than 12 in. each"*. **OQ 87's mechanism, for the
second time on this node**: the slot was `open`, and `resolve_slots` stops only on `specified` or
`forbidden`, so it inherited the nearest ancestor's record whole — exactly as this node's
`dormer` slot did until 27 August. It was invisible while nothing read `forbidden` on the pack
path. The slot is bound now on the node's own evidence, both faults cleared, the sidelights draw
again, and **the ratchet fell 787 → 776** — one binding on one node removing eleven pairs.

**So the 776 are not all defects, and that is the standing warning on this number.** Some are a
kit correctly refusing a pack; some are a kit that inherited a refusal it never made, where the
pack was right. The meter counts the DISAGREEMENT, not the verdict, and each one has to be read.

**Corpus effect, measured.** `carpenter-gothic` reported "75 slots dimensioned" and now reports
64 plus 11 named as refused — the meter had been counting a slot with no figure on it as
dimensioned. `ranch-style` moved 78/69 to 67/60 the same way. The `--forbidden` ratchet stays at
787: it now counts the gate's own marks rather than re-deriving the judgment, and the two agree.

*Original entry follows.*<br><br>**OPEN — the KIT cascade's strongest word is overruled by the PACK cascade, on most of the
corpus, and no human decided any of it.** `docs/inheritance.md`'s own binding table says
`forbidden` means *"This node prohibits the slot. Stops the cascade."* It stops the kit cascade.
It has never stopped the pack cascade. `resolve_kit.eval_packs` filters a pack's rules by the
binding's `slots`/`slots_except` and by nothing else; `choose_pack` consults the slot record's own
`packs` block — a person's explicit ruling — and then falls through to precedence.

**Measured 28 Aug 2026 by `build/check_inheritance.py --forbidden`, ratcheted at 787:**

- **776 (node, slot) pairs** where the resolved kit binds the slot `forbidden` and a proportion
  pack dimensions it anyway, across **118 of 132 buildable nodes**.
- **5,123 (node, slot, pack) triples; 7,118 individual rules.** The PAIR count is what is
  ratcheted; the triples fall as packs are declined without a single pair closing, which is
  itself the point — WP-8.2's ten declines took the triples from 5,155 to 5,123 and left 787
  exactly where it was.
- **776 of 776 resolve by `style.proportion_packs` precedence.** Not one carries a `slot.packs`
  ruling, so **no human has ever chosen any of them** — the precedence numbers driving it were
  authored on ANCESTORS, for the ancestors' buildings, with no view of the descendant.
- Worst slots: `entablature` 69, `parapet` 63, `column` 57, `modillion_dentil` 54,
  `transom_sidelight` 49, `cornice_return` 48, `secondary_cladding` 46, `balustrade` 41,
  `pilaster` 40, `ornament_vocabulary` 35, `pediment` 33, `corner_quoin` 27.
- Worst nodes: `american-farmhouse-vernacular`, `folk-victorian`, `new-urbanist-traditional` and
  `prairie-school` at 18 each; `appalachian-log-house`, `dogtrot-vernacular` and
  `log-vernacular-american` at 16.

**The worked case.** `carpenter-gothic`'s resolved `pilaster` record is `binding: "forbidden"`,
note *"No pilaster order."*, inherited from `gothic-revival-american`. `chambers-ionic`
dimensions it at `5/6` anyway. Declining `chambers-ionic` — which WP-8.2 did, on the node's own
tell that *"everything projects less than about two inches, because everything came off a
plank"* — **does not fix it**: `--impact carpenter-gothic chambers-ionic` shows `pilaster` handed
straight to `benjamin-ionic`, on a slot the kit forbids just as much.

**So this is NOT OQ 51 and is deliberately ratcheted apart from it.** OQ 51 counts a ROLE nobody
bound; this counts a KIT BINDING overruled by a pack. The two move independently, and folding
them into one number would make both unreadable. It is OQ 87's sharper neighbour: a slot bound
`open` inheriting its ancestor's constraints is a silence being filled, and this is an explicit
refusal being ignored.

**What a fix looks like, and why it was not done in the package that found it.** One rule, at
`eval_packs`, beside the `slots`/`slots_except` filter that is already the single enforcement
point: a pack rule may not write to a slot the resolved kit binds `forbidden`. That is not a new
grammar — it is the binding table finally meaning what it says. It needs `eval_packs` to take the
resolved kit (a keyword argument defaulting to today's behaviour, so the four callers that
already hold it can pass it and the rest are unchanged). **It changes dimensions on 118 of 132
nodes**, which is not a change to make inside a package doing something else, and the 787 would
need re-pinning against whatever survives.

**The question for a ruling**, since the mechanism is clear and the consequence is not: is
`forbidden` on a slot a statement about the *kit* only — what variants this style admits — or
about the *slot* absolutely, including any dimension any pack might supply for it? The corpus
reads it the second way in prose and the first way in code, and 787 pairs sit in the gap.
