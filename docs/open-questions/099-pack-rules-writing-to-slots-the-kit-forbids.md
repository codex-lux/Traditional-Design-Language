# OQ 99 — 787 pack rules dimension a slot the resolved kit binds `forbidden`, and nobody chose one of them

*Status: OPEN · Raised in: From the inheritance backlog (WP-8.2, 28 Aug 2026)*

**OPEN — the KIT cascade's strongest word is overruled by the PACK cascade, on most of the
corpus, and no human decided any of it.** `docs/inheritance.md`'s own binding table says
`forbidden` means *"This node prohibits the slot. Stops the cascade."* It stops the kit cascade.
It has never stopped the pack cascade. `resolve_kit.eval_packs` filters a pack's rules by the
binding's `slots`/`slots_except` and by nothing else; `choose_pack` consults the slot record's own
`packs` block — a person's explicit ruling — and then falls through to precedence.

**Measured 28 Aug 2026 by `build/check_inheritance.py --forbidden`, ratcheted at 787:**

- **787 (node, slot) pairs** where the resolved kit binds the slot `forbidden` and a proportion
  pack dimensions it anyway, across **118 of 132 buildable nodes**.
- **5,123 (node, slot, pack) triples; 7,118 individual rules.** The PAIR count is what is
  ratcheted; the triples fall as packs are declined without a single pair closing, which is
  itself the point — WP-8.2's ten declines took the triples from 5,155 to 5,123 and left 787
  exactly where it was.
- **787 of 787 resolve by `style.proportion_packs` precedence.** Not one carries a `slot.packs`
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
