# oq/a-kit-binding-propagates-to-descendants-nobody-read — binding a slot on one node states it for every node under it, and nothing compares the result against those nodes' own records

*Status: OPEN · Raised in: The WP-8.4 adversarial audit (28 Aug 2026)*

**OPEN — a slot bound on an ancestor is an assertion about every descendant that left it `open`,
and no checker, test or reviewer ever compares that assertion with what those descendants' own
records say.** Binding `transom_sidelight` on `colonial-revival` in WP-8.3 — correct on its own
node, quoted from `defining_characteristics[1]`, and made to close a forbidden-slot exposure —
carried `elliptical-fanlight` and `sidelights` CANONICAL to ten descendants. Three of them say
otherwise in their own files: `minimal-traditional`'s *"Ornament reduced to three items at most:
a chimney, a pair of decorative shutters, and a simple door surround"*, `modern-farmhouse-
traditional`'s *"no applied classical elements"*, and `ranch-style`, which names entry sidelights
only inside `diagnostic_tells` as part of *"the 1955-1970 traditionalizing overlay"*.

**It is not a bookkeeping error, because the binding is READ.** `build/elevation.py:318` computes
`sidelights_forbidden` from exactly this resolved record, so the generator went from drawing
nothing to drawing an Adamesque fanlight-and-sidelight entry assembly on a single-storey ranch.
The corpus stated something false and then drew it.

**And the fix propagates too.** Binding the three descendants on their own records carried `none`
CANONICAL one hop further, to `neo-eclectic` — which `styles/neo-eclectic.json` itself calls
ranch-style's *"structural parent"*, and whose defining characteristic is *"an entry element
inflated in height and width relative to the wall that carries it, frequently rising through two
storeys"*. The last node in the corpus that should inherit "no entry light" from a single-storey
one. Four nodes were bound in the end, each on its own evidence, and the only reason the fourth
was found is that the audit re-measured its own fix.

**What is unbuilt.** A checker that reads a kit's canonical variants against the node's own
`defining_characteristics`, `diagnostic_tells` and `distinguished_from` cannot exist — that is a
judgment about meaning, and one that pretended otherwise would be "unjudged reported as passed"
in a new place. What CAN exist, and does not:

- **A propagation report.** `build/check_kits.py --propagates <node> <slot>` printing every
  descendant whose resolved record would change, so an author sees the blast radius before
  committing. Every binding in this session was made without one, and the sweep that found this
  had to be written by hand three times.
- **A convention that a binding note states its downstream sweep.** All three kit notes written
  in WP-8.3 and WP-8.4 justify the binding from the node's own record and record no sweep at all,
  which is exactly how this passed review — including mine.

**Related but not the same.** OQ 87 is about a slot bound `open` inheriting its ancestor's record;
that is the MECHANISM this rides on. This question is about the author's side of it: the moment
you bind a slot, you have spoken for everyone below you, and the corpus gives you no way to see
who that is.

**A second instance in the same session, unfixed.** Binding `roof_material` on
`spanish-colonial-revival` propagated `clay-tile-barrel` CANONICAL to `pueblo-revival`, whose own
record reads *"Flat roof drained through projecting canales behind an irregular, gently undulating
parapet"*. The corpus now states that a flat-roofed, parapeted Pueblo Revival house is canonically
roofed in red barrel tile. It is not a regression in severity — the value it replaced was French
Baroque `slate`, also wrong — and it is left standing rather than patched, because patching
instances one at a time is what this question exists to stop.
