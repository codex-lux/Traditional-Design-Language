# oq/a-variant-status-conditioned-on-a-region-or-a-construction-is-never-applied — a kit states where a status holds, and every reader reads it as holding everywhere

*Status: OPEN · Raised in: WP-14.33 (26 September 2026)*

**The finding.** A kit variant may carry an `applies_when`, which says under what condition its
status holds. The condition can name a date range, a region, a construction or a climate zone.
`schema/kit.schema.json` introduces the field as conditionality that "in 0.1.0 … had to be buried
in nested objects no engine could act on."

**One of those conditions is acted on, and only on request.** `build/resolve_kit.py::in_period`
reads `date_range` when a caller passes `--date`. No reader in `build/` or `mcp_server/` applies
`regions` or `construction`. The resolver copies the condition onto the resolved row, and the CLI
prints it after the word "when", so a person reading the terminal sees it. Every other reader
takes the row's status and ignores its condition.

It surfaced in WP-14.33 while ruling on repeated variant ids. The twelve legitimate repeats in
`georgian-colonial-american` state a variant plainly and then again under a condition. That is
correct only if something reads the condition.

**Measured on 26 September 2026:**

- **155 kit variant rows carry an `applies_when`, across 24 kits.** By key: 93 `date_range`,
  39 `regions`, 15 `construction`, and 15 a `note` inside the condition.
- **53 rows are conditioned on a region or a construction.** 22 of them are canonical, 23
  permitted, 7 atypical and 1 forbidden.
- **After the cascade, 249 resolved rows are canonical or forbidden under a condition no reader
  applies.** 187 are canonical under a construction and 51 canonical under a region, over 72 of
  164 styles. 11 are forbidden under a region, over 11 styles.
- **The sharpest case is `none-masonry-reveal`.** It is canonical under
  `construction: solid-masonry-two-wythe` in the Georgian kit's two window-surround slots. The row's
  own note says "it is the masonry answer". **It resolves canonical on 61 styles, clapboard houses
  among them.**

**How this relates to OQ 17.** OQ 17 ruled *which mechanism to use*: `applies_when.regions` on a
parameter for a single differing value, and a variant node when enough diverges to deserve an
identity. It did not rule *whether a reader applies the condition*. The same field on a variant row
has had no reader for its region or construction half since it was written.

**Why it is a question and not a fix.** Applying a condition needs a context. The corpus has one
half of it: `build/construction_vocabulary.py` resolves a style's construction (WP-8.4). A plan
record states no region the kit's region names could be matched against. The readings are:

1. **Apply it at resolution.** Hand `resolve_slots` the house's region and construction. Resolve a
   conditioned row only where the condition holds. Report it as could-not-evaluate where the
   context is missing, never as holding. This is the reading the schema's own wording implies. It
   needs a region on the plan record, which no plan states today.
2. **Treat a conditioned row as conditional wherever a status is read.** A canonical row under a
   condition is "canonical where …" and is never counted as canonical outright. A checker that
   needs the answer reports could-not-evaluate. This needs no new context. It changes what every
   status reader counts, the elevation's three by-id readers among them.
3. **Declare the condition documentation.** Say in the schema that `regions` and `construction` are
   prose for a reader and no engine applies them. Leave every reader as it is.

**What was deliberately not done.** Nothing reads a condition it did not read before. The five
unconditional repeats were deleted, and `check_kits.py::check_duplicate_variants` keeps a repeat
legitimate only as a condition. Whether that condition is ever applied is this question.
