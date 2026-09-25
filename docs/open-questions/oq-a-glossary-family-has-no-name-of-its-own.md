# oq/a-glossary-family-has-no-name-of-its-own — the Glossary groups every word by family, and no record says what a family is called

*Status: CLOSED 25 Sep 2026 — executed by WP-14.17 · Raised in: WP-14.8 (24 September 2026)*

**The question.** The Glossary index (`#/glossary`, WP-14.8) lists the 121 glossary records
grouped by `family`, in the order of `schema/glossary-term.schema.json`'s `family` enum, which the
server serves as `by_family`. Each group needs a heading. The ruling of 24 September puts every
word the workbench shows into a glossary record, and PRD §J.4 forbids an app-written "kind heading"
by name. **No glossary record defines a family.** So the heading has three possible sources, and
this package could take none of them honestly except the first:

1. **the enum value, printed as it is** — `product`, `param-kind`, `variant-status`,
   `constraint-state`, `pack-relation` — which is what WP-14.8 ships, set in the eyebrow face;
2. **a table of friendlier names in the app** — exactly the app-written kind heading §J.4 refuses,
   and a second vocabulary nothing checks;
3. **a record per family** — which does not exist and cannot be authored without a ruling.

## The evidence, measured on this tree

- The enum has **21** families and all 21 hold at least one record (`build/check_glossary.py`:
  binding 4, carry 3, constraint-state 2, edge 7, fault 4, figure 2, house 5, judgment 6, layer 9,
  model 13, nav-group 4, pack-kind 6, pack-relation 5, param-kind 5, product 3, proportion 11,
  rank 4, section 9, severity 3, surface 12, variant-status 4).
- Some family values are readable as words (`severity`, `binding`, `fault`), several are machine
  compounds a reader has to decode (`param-kind`, `pack-relation`, `constraint-state`,
  `nav-group`), and two collide with a word the glossary itself defines in another sense
  (`surface` is both a family and the thing each `surface-*` record names; `section` likewise).
- The glossary schema already treats five families as NAMESPACES (`surface`, `section`,
  `nav-group`, `layer`, `judgment` require the id prefix `<family>-`), and seven are fixed by the
  enum a record binds (`check_glossary.py` rule 5). A family is therefore not a free label: it is
  structure the checker reads, which is the argument for giving it a record rather than a string.

## The same question, one layer down, on the term page

`#/glossary/<term>` shows one record whole, and its fields need labels — this package wrote eight:
*Also called*, *Not to be confused with*, *Who it is for*, *What it is not*, *The page*, *See*,
*Names the value*, *Rests on*. They name parts of a RECORD rather than define a word, so they were
judged furniture rather than definitions (the popover's own two labels, "not to be confused with"
and "more", are the PRD's). But they are app-written words a reader meets beside the corpus's, and
if a family heading needs a record, the case that a field label does not is weaker than it looks.

## What would have to be ruled

- Whether a family heading is a DEFINITION (so a record per family, 21 new records, and a way to
  bind them — an eighth `FIELDS` key `glossary.family` pointing at the family enum would reuse
  rule 5 exactly, and would move `glossary/fields.js`, `check_glossary.py`'s `FIELDS` and
  `src/glossary.test.mjs` together) or FURNITURE (so the enum values stay, perhaps de-hyphenated
  by a rule rather than a table).
- Whether the term page's field labels are furniture, or records too.
- Until then the enum value is printed, visibly and unchanged, which is the one choice that invents
  nothing. **Do not add a family-name table to `surfaces/Glossary.jsx`**: that is the second
  vocabulary this question exists to avoid, and `src/copy_ratchet.test.mjs` would not see it,
  because a short label is neither an explanation nor a count.

## Ruled 25 September 2026

**Answer 3, a record per family, and the field labels are records too.** Both were taken with the tranche-2 plan's approval, on the standing rule that a label the app needs is a record. `glossary.family` becomes the eighth bindable field, one `family-*` record per family value. The term page's eight labels are `glossary-field-*` records. The contract is `docs/prd/phase-14-tranche-2.md` §A. The question closes when WP-14.17 lands.

## Closed 25 September 2026 (WP-14.17)

**Executed as ruled, and the report is `docs/reports/wp-14.17-every-definition-a-record.md`.**
`schema/glossary-term.schema.json` is at 0.2.0: the family enum gains `glossary-field`, `mark`
and `family`, and `glossary.family` is the eighth bindable field. `build/check_glossary.py`'s
`FIELDS` and `workbench/app/src/glossary/fields.js` gained the same row, and
`src/lookup.test.mjs` now reads the checker's table and holds the two to each other row for row,
where before it pinned the app's copy at a literal count of seven.

- **A record per family**: 24 `family-*` records, one per enum value including the three new
  ones, each binding its value through `glossary.family` with `order` equal to the enum index, so
  rule 5 holds them exactly as it holds a kit binding or a severity. Every basis quotes the
  schema's own gloss for the value.
- **The term page's labels are records**: 8 `glossary-field-*` records, one per label the page
  showed, each quoting the schema's description of the field it names.
- **`surfaces/Glossary.jsx` prints no enum value and types no label.** The group heading and the
  kicker draw `<Term field="glossary.family" value=…>`, the family chips read the bound word
  through `termView.wordForValue`, and the eight field labels are `<Term id="glossary-field-…">`.
  `src/glossary.test.mjs` refuses a literal label or a raw family value by reading the file.

The heading source this question called the only honest one while no record existed, the enum
value printed as it is, is retired. Where a family ever lacks its record, the chip and the heading
say which binding is missing rather than falling back to the value, which is the fallback this
question warned against in another form.
