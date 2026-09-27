# oq/no-tool-answers-which-styles-use-a-pack — the assistant is told which pack is on the page, and no tool it has can say which styles use it

*Status: OPEN · Raised in: WP-14.22 (25 September 2026)*

**The finding.** WP-14.22 tells the assistant the record on the page: on
`#/proportions/trim-classical` its context now names `pack:trim-classical`, and the model fetches
the record with the tools it already has, as ruled on 25 September
(`oq/the-assistant-is-blind-to-the-page`). The first thing a reader asks on a pack page is often
*"which styles use this?"*, and none of the 27 tools answers it.

- `tdl_get_proportions` returns `assemblies`, `authority`, `conflicts`, `derived_rules`,
  `diameters_per_module`, `hint`, `invariants`, `judgment_rules`, `module_bound_to`,
  `module_from`, `module_in`, `name`, `pack`, `part_in`, `parts`, `resolved_from` and `totals`.
  None of these lists a style. Measured on this tree by calling the tool.
- The workbench's own proportions route does answer it. `workbench/server/corpus.py` adds
  `used_by = pack_users(pack_id)` to the page's payload by inverting
  `build/resolve_kit.resolve_packs` over every node. That makes it the one reader of pack
  membership, so declines and the opt-in gate are included. The MCP payload is held byte-stable
  and does not carry it, and tranche 1's comment on the `sources` field says so in as many words.
- The other direction is answerable. `tdl_get_style` gives a style's own `proportion_packs`, so
  the model can get from a style to its packs, but not from a pack to its styles without
  fetching every style.

For `trim-classical` the corpus's answer has four parts, re-derived on this tree: 36 styles name
it in `proportion_packs`, 6 opt in through `inherits_packs`, 6 decline it through
`declined_packs`, and the pack's own `applies_to` names 42. `pack_users` keeps those apart.

**Why it is a question and not a fix.** The ruling chose the citation and the tools the model
already has, and it lifted the tranche-1 freeze for the prompt, the context and the tool
DESCRIPTIONS only. MCP tool payloads stay byte-stable. The available answers each move a frozen
surface or add one:

1. **Serve `used_by` on `tdl_get_proportions`.** This is the page's own reader, so there is no
   second spelling. It changes a frozen MCP payload, and the tranche-2 contract's own rule means
   it needs a named item and a re-cut byte-stability pin.
2. **A new tool for the reverse relation**, for example one that takes a pack and returns
   `pack_users`. The tool count moves, and so does everything that counts the tools. The prompt
   and the registry test read that count now, not type it.
3. **Leave it, stated.** On a pack page the assistant can dimension the pack and read its rules,
   and it says it cannot list the pack's styles. The prompt would need a sentence saying so, or
   the model will try to answer from `tdl_get_style` one style at a time.

## Related

- `oq/the-assistant-is-blind-to-the-page`, closed by WP-14.22, whose evidence first named this.
- `oq/mcp-proportions-serve-no-assemblies-for-non-order-packs`, which is another place a machine client
  gets less than the page shows.
