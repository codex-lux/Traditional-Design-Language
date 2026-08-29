# oq/the-raw-kit-read — six places read a node's own kit file where the corpus's answer lives in its cascade

*Status: OPEN · Raised in: The WP-8.4 adversarial audit (28 Aug 2026)*

**OPEN — `C["kits"][style]["slots"]` and `RK.resolve_slots(...)` are different records, the
second is the one the corpus means, and the codebase reads the first in six places.** A slot a
node leaves `open` inherits its nearest bound ancestor's record in full (OQ 87), so the node's own
file is a partial statement of what the style is. Measured across all 132 buildable nodes: the
cascade states variants for a **mean of 29.6 slots per style, up to 64,** that the node's own file
says nothing about.

## The distinction that decides each site, found by getting one of them wrong

**An inherited `forbidden` is a prohibition an ancestor made and the descendant never
overturned. An inherited CANONICAL variant is a positive claim the descendant never made.**
The first is safe to read from the cascade. The second is not, until somebody has adjudicated
that slot on that node.

This was not obvious in advance and was found by measuring a fix rather than reasoning about
it. Making `roof.py`'s chimney read the cascade — which its own docstring had claimed since it
was written — is right in principle and **measurably worse in fact**: `colonial-revival` states
nothing about chimneys, so the cascade hands it `tall-multiple-vertical-accent` from
`british-picturesque`, a Gothic Revival clustered stack *"thin and numerous and well out of
proportion"*, seven steps up its chain. Reading it put a Gothic stack on
`plans/spec-builder-colonial.json` and took that plan's placed chimney positions **from 1 to
0**. Its own record carries nothing that would let it be bound honestly, so there is no fix at
the node either, and the massing's `hearth` — the existing fallback — is the better answer.

**The change was reverted and the reason pinned as a test.** The docstring now says the node's
own kit is deliberate. That is the shape of the remaining work here: each site has to be judged
by WHICH KIND of statement it reads, and a site that reads a positive claim needs the slot
adjudicated first. OQ 87 is why: a slot left `open` takes its nearest bound ancestor's record in
full, and nobody has judged whether that ancestor speaks for the descendant.

**Two were fixed in this audit, because the fix was contained and provable — and both read only
prohibitions or measured bands, never an inherited canonical:**

- **`build/plan_check.py`'s style layer.** It decided "is this declared slot or variant
  forbidden?" from the raw kit, and was therefore blind to **879 forbidden bindings and 3,661
  forbidden variants** — on every one of the 132 nodes. `cape-cod-colonial` forbids the whole
  classical-apparatus group at the family level and a plan declaring a balustrade on it went
  unremarked, while `build/elevation.py` refused to draw one: two layers disagreeing about the
  same record. Sweeping the Tidewater reference plan's declared block over all 132 styles gives
  110 unchanged, 19 gaining one finding, 3 gaining two, and every one is a true call.
- **`build/elevation.py`'s window reveal.** It sat six lines above the block that resolves the
  cascade, still reading `C["kits"]`, while that block's own comment explained why the raw kit is
  the wrong record — written for `shutter` and `window_head_masonry` in the same function. Seven
  (style, slot) pairs over six styles state a reveal band only through their lineage
  (`pueblo-revival` at 12–24 in among them) and were drawn with no reveal at all. A measured
  band, not a canonical claim, so the distinction above permits it.

**In both cases both shipped plans are byte-identical before and after**, which is exactly why
neither was caught. Verifying a corpus-wide change on the plans that happen to ship is verifying
it on 2 of 164 styles.

**Four are NOT changed. Three because each moves composed output broadly enough to be a package
rather than an audit fix; the fourth because reading the cascade there is actively wrong:**

| where | what it reads raw | measured size |
|---|---|---|
| `build/compose.py::ceiling_heights` | `ceiling_height_rule` parameters | **85 styles** state a figure only through the cascade and compose at the 9.0 ft default |
| `build/compose.py::canonical_choices` | every slot, to build `plan["declared"]` | ~30 fewer declared slots per style, so every downstream layer judges a thinner record |
| `workbench/server/corpus.py::slot_detail` | stops the walk at the FIRST kit binding the slot, though its docstring promises "the FULL variant ladder" | **410 forbidden rungs are not shown, across 175 (node, slot) pairs on 76 of 132 nodes** — measured by replicating the function's own walk, not by approximating it (see the note below) |
| `build/roof.py::chimney_positions` | the chimney's canonical variant | 64 styles state one only through the lineage — **and reading it is WRONG here**, per the distinction above; reverted, with the reason pinned as a test |

**A note on that 410, because getting it wrong twice is the point.** An auditor reported 757 and
a first probe of mine reported 3,661; both were measuring something adjacent rather than the
function. `slot_detail` does not compare the raw kit to the cascade — it walks
`[style] + core._cascade(style)` and stops at the first kit whose record for that slot has a
binding of `specified`/`extends`/`forbidden` AND a non-empty `variants` list. Only replicating
that exact walk gives 410. A number for a defect in a specific function has to come from that
function's own control flow; anything else is a different measurement wearing its name, which is
this register's most repeated mistake.

A ceiling height is the elevation's governing datum; moving it on 85 styles moves every drawn
sheet and every score those styles produce. That is worth doing and it is worth doing with a
published diff, which is what a package is for.

**The general fix, unbuilt:** there is no reason for six call sites to each decide which record to
read. One accessor — `resolved_slots(style)`, cached, raising rather than degrading — and a
source-reading test that fails when `C["kits"]` is subscripted anywhere outside it. That test is
the piece that would have prevented all six, and it is cheap; what is not cheap is the corpus-wide
diff that flipping the four remaining sites publishes.

**Related.** OQ 87 is the MECHANISM (`resolve_slots` stops only on `specified` or `forbidden`).
`oq/a-kit-binding-propagates-to-descendants-nobody-read` is the authoring side of the same fact.
This one is the READING side: every consumer that asks the node instead of the corpus.
