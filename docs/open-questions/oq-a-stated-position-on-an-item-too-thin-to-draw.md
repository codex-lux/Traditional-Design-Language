# oq/a-stated-position-on-an-item-too-thin-to-draw — the record's plainest positions are on things the plan never draws

*Status: OPEN · Raised in: WP-13.6, furniture to its own grammar (16 September 2026)*

**Two catalogue items state their position more plainly than any other item in the corpus, and
the plan draws neither.** `fg-too-thin-to-draw` refuses an item whose lesser footprint
dimension is under 8 in — `build/plan_check.py`'s own scale rule, `fw < 8`, which WP-11.3 made
a rule about SCALE rather than a `kind` — and it runs before any placement rule is consulted:

| item | record | footprint (in) | the sentence |
|---|---|---|---|
| television | `rooms/primary-bedroom.json` | `[60, 4]` | *"the only wall that works is the one opposite the bed"* |
| full-length mirror | `rooms/walk-in-closet.json` | `[24, 3]` | *"Put the mirror on the END wall looking down the length of the room"* |

So `fg-opposite-the-bed` and `fg-on-the-end-wall` are **executed and unreached by the whole
corpus** — not a placement, not a refusal, nothing on any of the sixteen plans, measured on the
deterministic engine. Both are driven by hand in `tests/test_furniture_grammar.py`, and
`furniture/grammar.json`'s `executed_but_unreached_in_the_corpus` names them so a reader is not
misled by a green suite. That is WP-8.11's rule working; it is not an answer.

**The refusal is right at plan scale and the loss is real.** A 4 in television drawn at 13
px/ft is a third of a pixel of body, and drawing it would be a mark a reader cannot tell from
ink. But the record's statement about WHERE it goes is not about its thickness, and it is
thrown away with it: a reader of the plan is told nothing about the wall the television takes,
and the wall opposite the bed is a real fact about how the room works.

## What has to be ruled

1. **Is a thin item a thing with no mark, or a thing with no place?** Today it is neither: it
   is skipped, counted in the plate's `N FURNITURE ITEM(S) NOT DRAWN` line under
   `FG-TOO-THIN-TO-DRAW`, and its position rule never runs. A third state — *placed and drawn
   as a line* — is available and is what a draughtsman does with a mirror, a television and a
   wall-hung shelf; it needs a `line` primitive in `furniture/symbols.json` and a ruling that a
   zero-bulk item may carry a position.
2. **Or is the position the thing to keep?** An item could be REFUSED a rectangle and still
   have its rule run, so the record says *"the television takes the N wall and is too thin to
   draw"* rather than *"the television was skipped"*. That costs nothing in ink and is a
   different claim from (1).
3. **And it changes what `executed_but_unreached_in_the_corpus` means.** Either ruling makes
   two entries leave that list, which is the measurement that would say the ruling landed.

**Do not close this by thickening a footprint.** `[60, 4]` is a measured depth and the reason
the item is refused; editing it to clear a rule is the laundering this corpus forbids.
