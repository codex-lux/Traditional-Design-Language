# oq/the-app-still-writes-paragraphs-the-ratchet-does-not-read — the copy ratchet reads zero, and it reads titles and counts only

*Status: OPEN · Raised in: WP-14.31 (25 September 2026)*

**The finding.** WP-14.31 emptied `workbench/app/src/copy_ratchet.test.mjs`'s baseline, so no
`title=` of eight or more words and no typed count survives in the app's live source. That ratchet
reads two shapes and no others. The rule it serves is wider — *every definition is a glossary record
and the app writes none* — and the app still writes paragraphs of body text.

Measured on WP-14.31's tree with a deliberately crude reader: JSX text runs of twelve or more words,
taken between a closing `>` and the next `<`, outside braces, after comments are stripped.
It finds 48 runs in 19 files. Ten are code fragments, where the reader was fooled by a `>` inside an
arrow function or a comparison. The other 38 are prose, and read by hand they split about evenly:

- **19 are disclosures of the payload in hand.** They say what this record or this placement did.
  Examples: ConflictSet's *"Nothing is drawn from this placement"*, the plan sheet's engine lines,
  the atlas's *"Fetching the … outline for this scale"*, and the Proportions plate's *"this pack gives
  rules, not an assembly"*. Most read their figures from data already.
- **19 are explanations of the product.** They say what a surface, an export or a principle is,
  whatever record is on screen. Examples: ExportDetails' four card descriptions (*"The IR itself —
  the record every drawing and finding renders from …"*), CandidateSet's *"A plan with no fatal
  findings is not therefore good"* and its account of the decision log, Transcription's and the Plan
  Workbench's empty-state paragraphs, and ShortcutCard's account of the citation address.

**One of the 19 explanations is a corpus fact typed as prose.** The Phylogeny's *"Japanese, Islamic,
South Asian and African traditions are absent"* is true of today's graph. It becomes silently false
the day a node for any of them is added. That is the typed-count failure, spelled in words the count
scanner cannot see.

**Why it is a question and not a fix.** Where the line falls between a definition and a disclosure
is a ruling. The readings available are:

1. **Only a sentence that defines a term is a definition.** The ratchet's scope is right, and the 19
   explanations are the product's own voice, which the app may keep.
2. **An explanation that holds whatever record is on screen is a definition.** It belongs in a
   record, and the app reads it through `Term` or `describeTerm`, as the palette's three sentences
   and the Export page's not-built cards now do.
3. **Split by what the sentence claims about the corpus.** A sentence stating a fact about the
   corpus, like the Phylogeny's list of absent traditions, is derived or recorded. A sentence about
   how the workbench behaves stays.

The reader behind the 48 is crude on purpose: it is a census and not a guard. A guard needs the
ruling first. Built before it, a guard would ratchet the disclosures that are right beside the
explanations that may not be. Its own false positives, the ten code fragments, would read as
debt too.
