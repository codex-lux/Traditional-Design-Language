# oq/the-slot-tool-lists-a-style-that-forbids-a-slot-as-specifying-it — `tdl_get_slot`'s `specified_by_styles` reads each style's own kit file, counts a forbidden binding as a specification, and misses every inherited one

*Status: OPEN · Raised in: WP-14.23 (25 September 2026)*

**The finding.** `mcp_server/core.py::get_slot` builds `specified_by_styles` this way: it walks
`D["kits"]`, which is each node's OWN kit file, and it lists a style whenever that style's record
for the slot has a `status` other than `empty`. It never reads `binding`. The field has two
consumers. The first is the MCP tool `tdl_get_slot`. The second was the tranche-1 slot panel at
`#/style/-/kit/<slot>` (WP-14.12), which printed the list under the heading "specified by". The
list is wrong in two directions at once, and both errors are large:

- **It lists styles that FORBID the slot.** A forbidden binding carries a `status` (usually
  `drafted`) because the forbidding is authored. Swept over all 97 slots, **228 entries across
  41 slots are styles whose own kit binds the slot `forbidden`.** Another 8 are bound `open`,
  and 2 are an `extends` that the cascade resolves to `forbidden`, because the ancestor it
  extends forbids the slot (`colonial-revival.cornice_return`, `georgian-revival.water_table`).
  That makes **238 entries naming a style whose resolved kit does not specify the slot.**
- **It omits every style that inherits the slot.** A style that specifies a cornice by
  descending from one that does never appears. **6,380 styles are missing** from the lists: the
  own-kit lists hold 2,145 entries, and the resolved kits specify 8,287.

**All 97 of 97 slots disagree.** Three specimens, each giving own list against resolved specified:

- `cornice`: 35 against 85. 10 own entries are not resolved-specified, all 10 forbidden in their
  own kit, and 60 resolved specifiers are missing. The resolved kits forbid the cornice on
  24 styles.
- `construction_type`: 64 against 149. 85 are missing.
- `roof_form`: 62 against 118. 57 are missing, and 1 listed style is not a specifier.

**Measured 25 Sep 2026** on the WP-14.23 tree. The measurement runs every `core.get_slot`
against `workbench/server/corpus.py::_resolved_bindings`, which reads `core._resolved_kit` for
all 164 styles. It is re-derivable in a dozen lines; re-derive it rather than quote it.

## What WP-14.23 did, and deliberately did not do

The record page at `#/elements/<slot>` no longer reads `specified_by_styles`. `GET
/api/slots/{id}` now serves `bindings` beside it: `specified` and `forbidden`, each read from the
style's RESOLVED kit (the cascade) by `corpus._slot_binding`. That function honours a dangling
`extends` as specified, because `resolve_kit.resolve_slots` does. The page lists the forbidding
styles under their own heading and never under "specified". `GET /api/slots` counts `specified_by`
the same way. `workbench/server/tests/test_record_pages.py` holds both readings to an independent
reader and **asserts the premise**, which is that the own-kit list still differs. Without that
assertion, a later fix to `get_slot` would leave the test comparing two equal lists and proving
nothing.

**`core.get_slot` is not changed.** The tranche-2 PRD holds the MCP payloads byte-stable. A
tool's answer changing under an agent that already relies on it is a ruling, not a repair. The
defect therefore stands in `tdl_get_slot` and nowhere else.

## What must be ruled

1. **Does `tdl_get_slot` move to the resolved reading?** If it does, the payload changes for
   every slot, so the move is a version bump of that tool's contract. The alternative is to keep
   `specified_by_styles` as the *own-file* reading, rename what it means in the tool's own
   `note`, and add the resolved lists beside it, as the workbench route does.
2. **What does "specifies" mean for a slot the style binds `open`?** The own-kit reading counts
   an `open` record that carries a status. The resolved reading takes the ancestor's binding
   (OQ 87: `open` does not mean open). Neither of those is "this style says nothing".
3. **Should the forbidding styles be served at all?** A slot record that names the styles which
   refuse it is useful: a reader choosing a cornice should know which traditions decline one.
   It is also a second list for every consumer to keep correct.

**Do not "fix" the own-kit list by filtering out `binding == "forbidden"` alone.** That removes
the 228 and leaves the 6,380 missing entries in place. The result is a list that looks right and
answers a narrower question than its name.
