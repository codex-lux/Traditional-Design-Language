# glossary/ — what every word on the workbench means

One file per sense of one word: `glossary/<id>.json`, the filename equal to the record's `id`,
against `schema/glossary-term.schema.json`. Every tooltip, page head, rail description, palette
line, plate key and edge caption the workbench shows reads one of these records. **The app writes
no definition of its own**: no definition prop, no fallback gloss. If a word on screen has no record
here, the word is bare, and that is a gap to fill here rather than in the app.

`python3 build/check_glossary.py` holds every record to the rules below and exits 0 (pass),
1 (an error) or 3 (could not evaluate — never a pass). To check records authored outside this
directory together with the ones in it, name every directory: `--glossary glossary --glossary
<other>` checks the union as one set. The full contract is
`docs/prd/phase-14-the-dossier-and-the-journey.md` §A and §B.

## The authoring rules

**Write for a practitioner.** An architect, a plan-development lead, a builder: plain words, the
trade's own terms where they are the right ones, never addressed to an AI agent. The corpus has
agent-voiced text of its own (`core.overview()` in `mcp_server/core.py` speaks to a model); rewrite
it for a person, and let it survive only as a quotation in a basis.

**At most forty-five words** in a definition. An `analogy` is one sentence of at most thirty; a
page head (`surface.what`), each "how to read this page" line (`surface.read`) and each `is_not`
at most thirty. The checker counts words split on whitespace.

**No digits, no counts, no colours, no build history.** A definition must still be true when every
number in the repository has changed, so no numeral of any script (a circled figure or a fraction
counts), no count of records, no work-package or open-question number, no command-line flag and
no snake_case identifier appears in any prose a reader sees: `term`, `sense`, `aka`,
`definition`, `analogy`, `more`, `surface.what`, `surface.read`, `readers`, `is_not`. A number
spelled as a word is not caught by the checker and is still a count; write around it. Colours are
the interface's business, not the word's.

**Sourced, or editorial, and never both.**

- `"kind": "sourced"` carries `sources`, and each string must **already** sit, character for
  character, in a `sources` list in some record under `styles/`, `faults/`, `rooms/`,
  `proportions/`, `groupings/` or `partis/`. Copy it from that record; do not retype it. The
  glossary never introduces a source the corpus does not already cite. `precedents/` records carry
  archival references and no `sources` list, and a kit's slot-level `sources` are provenance
  notes, so neither is a bibliography.
- `"kind": "editorial"` carries `basis`: the file or files the definition was read from, named by
  path, with **at least one passage of twenty-five characters or more quoted verbatim in double
  quotes**. The checker opens every file the basis names and refuses the record if a quotation is
  not in it. A quotation shorter than twenty-five characters is not checked at all, so it proves
  nothing and does not count; and because two short quotations close together can make the text
  *between* them read as one long quotation, keep every quotation long. Quote a single run of the
  file's own text — across a line break is fine, across markup (`*`, `**`, a backtick) or a code
  comment's `#` is not, because those characters are in the file and not in your quotation.

  The files a basis may name are exactly the ones `build/check_openings.py`'s `GLOSSARY_REC_RE`
  admits: records under `rooms/`, `kits/`, `styles/`, `faults/`, `groupings/`, `proportions/` and
  `partis/`; scripts in `build/`; `massings/catalog.json`, `elements/slots.json`,
  `mcp_server/core.py`; a `schema/` file; `VISION.md`, the root `README.md`, and a **top-level**
  `docs/` page. Not `docs/reports/`, not `docs/open-questions/`, not the generated
  `docs/open-questions.md`, and never another `glossary/` file: a definition does not rest on a
  definition. A basis may name a JSON key path after the file (`rooms/x.json adjacency.why:
  "..."`); where it does, the quotation must be under that key, and a key path the checker cannot
  walk is an error.

  Editorial is a licence to explain, never a licence to invent. If you cannot find the sentence,
  the definition is not yet supported — say less, or find the record that says it.

**Two hazards the first authors met, both in the basis.** A quotation that carries a corpus
count goes stale without a sound: `build/check_counts.py --fix` rewrites the figures in `README.md`
and `docs/`, and the next corpus change then breaks the quotation, not the definition. Quote the
sentence around the number. And every path the checker finds in a basis becomes the record's
served `reads` provenance line, whether or not anything was quoted from it, so a basis that names
a file it did not read tells the reader something false about where the definition came from.

**Homonyms are paired.** One sense per id. When a `term` or an `aka` collides, case-insensitively,
with another record's, **both** records carry a `sense` (a few words saying which sense) and each
names the other in `confusable_with`. `confusable_with` is symmetric everywhere it appears, names
only records that exist, and never names its own record. The collisions tranche one expects are
listed in the contract's §B.6; any other is a defect in whichever batch introduced it.

**A bound word takes its name from the value.** A record that `binds` a schema enum value (the
seven fields are a closed table in `build/check_glossary.py`) is in that field's family, is named
`<family>-<value>` with underscores as hyphens, carries `order` equal to the value's index in the
enum, and is the only record binding that value. A field is bound completely or not at all.

**Families that head a page are prefixed.** Records in families `surface`, `section`, `nav-group`,
`layer` and `judgment` have ids beginning `<family>-`, and an id with one of those prefixes is in
that family. `surface` (`{what, read, try}`) appears only in families `surface` and `section`.
`readers` and `is_not` appear only on `about-tdl`, which carries no `see`, `confusable_with`,
`binds` or `surface`, because it is the one record served to a reader who is not signed in and it
must resolve no other.

**Citations are the workbench's own grammar.** Each `see` item and `surface.try` is `kind:id`:
`term:<id>` must name a record in this directory, `brief:<id>` a file in `briefs/`, and every other
kind must resolve through the server's citation validator. A `style:` citation's fragment may
name a slot or a dossier section (`style:<id>#<section>`, one of the sections the server's
`DOSSIER_SECTIONS` lists); a `kit:` citation's fragment names a slot only, because a kit has no
sections. Until the server's validator learned the sections, a section fragment was refused here
by that validator and no record could carry one.

**What is not a basis.** The app strings being retired — the source-kind glosses on `SourceChip`,
the edge verbs on `EdgeGlyph`, `KIND_LABEL`, the rail's surface descriptions in `Chrome.jsx`, the
front door's `DOORS`, the palette's short lines in `staticEntries.js` — are wording seeds you may
start from. They are never a basis, because they are the app writing a definition, which is
exactly what this directory replaces.

## The seeds

Five records are required and every other record may lean on them: `about-tdl` (the one sentence
a signed-out visitor is shown, with the readers and the "what this is not" list from `VISION.md`)
and the four judgment states — `judgment-passed`, `judgment-failed`, `judgment-unjudged` and
`judgment-not-applicable`. Unjudged is not passed; the four words must stay four.
