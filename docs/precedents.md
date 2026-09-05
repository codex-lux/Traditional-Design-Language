# The precedent layer

*WP-11.1, 4 September 2026. The building behind every exemplar, as a record a checker can resolve.*

A style is known by its buildings the way a language is known by its literature. Until this
package the corpus had a grammar (57 packs), a vocabulary (164 nodes) and a critic (47 checks) and
almost no literature: an exemplar was `{name, location, year, note}` and nothing else — 482 of
them across 164 nodes, 410 distinct buildings, and **not one carried a HABS number, a register
reference or a link**. A reader could find Westover; a checker could resolve nothing. Not one
period building was transcribed in `plans/`; the only measured arrangement dataset lived in a
markdown table inside a report.

## The record

`precedents/<id>.json`, one file per BUILDING, id == filename, shared by every node that names it
(the Stanley-Whitman House stands for three). `schema/precedent.schema.json`. What it carries:

- **`refs[]`** — the locators: `habs` (VA-141), `loc-item` (va0433), `nrhp` (66000701), `nhl`,
  `state-register`, `wikipedia`, `wikidata`, `historic-england`, `institution`, `monograph`.
  Every one records **`retrieved`** (ISO date) and **`via`** (`tavily-search`, `tavily-extract`,
  `github-actions`, `manual`). A reference nobody read on a stated day by a stated route was typed
  from memory, which is how a wrong id is laundered as a citation — and the only routes that reach
  the archives from this project's tiers are those four (`oq/fetching-through-a-tier-the-proxy-denies`).
- **`survey`** — the Historic American Buildings Survey's WRITTEN historical and descriptive data,
  quoted verbatim in contiguous spans with the page marker each was read beside, by the survey's
  own outline (`overall_dimensions`, `foundations`, `walls`, `chimneys`, `openings`, `roof`,
  `plan`, `stairways` …), which maps onto the ontology's slots nearly one for one. It states the
  ENVELOPE as a surveyor measured it. It is a poor source for room dimensions, which live on the
  measured drawings — the study said so (`wp-9.2-what-the-tradition-actually-does.md` §7 Q10) and
  it is still true.
- **`measurements[]`** — every figure a quote states, carried **`as_printed`** beside the parsed
  value, because the OCR reads `h0` for 40 and a parse is a reading.
- **`rights_evidence`**, verbatim, with its URL — and **never a `license`**. A licence is a
  conclusion a person draws; `docs/assets.md` says why, and the same rule holds here.

The exemplar on the style node names its record through **`precedent`** and states a
**`standing`** — `icon` (the building the style is known by), `canonical` (a type specimen the
node's figures can be held against), `regional`, `documentary` (surveyed, useful to measure and
not to admire) — with a one-sentence **`why`** saying whose judgment it is. Standing is editorial
by nature and says so.

## The checker

`build/check_precedents.py --strict` holds the two directions to each other (an exemplar naming a
record that does not exist; a record listing a node whose exemplars do not name it), holds the
exemplar's `name` and `location` to the record's exactly (they are the join keys
`build/check_assets.py` reads), checks every id's shape against its kind, refuses a `license` at
any depth, and resolves every kit `source` of the form `precedents/<id>#survey.<field>` or
`precedents/<id>#measurements[<n>]` — the convention by which a kit figure cites a survey. Its
ratchets are floors that may only rise (records; exemplars carrying a `precedent`; records carrying
a survey) and ceilings pinned at zero, because deleting a `precedent` key makes every ceiling look
better and the floors are what stop that reading as progress.

**What it does not do, and says so on every run:** verify a survey quote against its source. The
data page is a PDF on `tile.loc.gov` that this container cannot open; `--live` probes that each URL
still answers and returns COULD NOT EVALUATE when the proxy denies the host. The adversarial
re-extraction each tranche's report carries is the check the machine cannot make. Tranche 1 ran one
auditor over the whole tranche; Tranche 2 ran **one per cluster**, starting as each cluster landed,
and found 57 defects to Tranche 1's 8.

**Three limits of the guard, each found by exercising it (WP-11.3), and none of them closable here.**

1. **`as_printed`-must-be-a-substring proves internal consistency and NOT fidelity.** A quote silently
   edited to fit its own figure passes: `emlen-physick-estate` printed `60' x 52 1` where the data form
   prints `60' x 521` and both measurements were written from that same wrong reading. Only a second
   read of the source catches it.
2. **A quotation in a ref `note` is prose, and prose is unchecked.** The verbatim discipline reaches
   `survey.quotes[]` and stops there. Three records printed a search-result summary — which the tier
   builds by concatenating discontinuous spans — as though it were running prose, manufacturing
   sentences their pages do not contain. A capital letter after a comma is the tell.
3. **A locator that does not resolve is not a locator, and nothing checks that one does.** The
   reference rules test an id's SHAPE and that a URL is present, never that it answers; one record
   stored a percent-encoded URL that had been dead since it was written.

## What a record may BE (WP-11.4, ruled 5 Sep 2026)

A precedent record is normally one building, and `record_kind` says when it is not: `building`
(the default when the key is absent), **`district`** — a listed area covering many buildings,
**`type-model`** — a builder's or developer's repeated model where the type IS the record and no
single address is it, or **`group`** — a named, documented set. Thirteen records already were one
of these before the ruling and said so only in each record's `note`: six districts, the two
Levittown models, four groups and one magazine house. For `minimal-traditional` and `ranch-style`
— post-war tract types outside HABS's charter entirely — a district or model listing is the ONLY
archival record that exists, so this is not a loosening but the practice written down.

**The field is authoritative and `DISTRICT_RE` is the fallback**, and the order runs both ways: a
record declaring `district` may share a National Register number with another (one listing covers
many contributing buildings), and a record declaring `building` may NOT — even when a ref title
carries the word "District", because a real house called "District House" would otherwise lose its
identity to a word in its name. Both directions are mutation-checked and pinned in
`tests/test_research.py`. The declaration does not license a vaguer record: a district still needs
its own listing reference and a type model still needs a source for the model.

**A refusal is a field, not prose.** An exemplar that carries no `precedent` because of a DECISION
says so in `no_precedent`, a closed vocabulary: `archive` (a drawings collection, not a building),
`body-of-work` (an architect's output rather than one work), `phase` (the building has a record and
this row names a phase that record is not about), `not-yet-researched` (an honest gap, and the
meaning when the key is absent). It exists because one number carried both: without it the count of
unresolved exemplars would read about 191 after Tranche 3 whether that were 191 gaps or 188 gaps and
three decisions. A row carrying `precedent` may not carry it, and the checker prints the split on
every run — 3 stated refusals against 185 gaps today.

**One building, one record** is the fourth rule and it is checked: two records sharing an archival
`refs[].id` of kind `habs`, `haer`, `nrhp`, `nhl` or `loc-item` are a hard error, because those ids name
one building and are evidence rather than judgment — except on a **district** listing, which legitimately
covers many buildings and is exempt by name. Two records sharing a normalised name are REPORTED with both
locations, never merged, because several American houses share a name; the corpus holds a Mount Airy, a
Mount Pleasant and a Mount Vernon as three buildings. Both counters are ratcheted at zero and were zero
across 415 records on the guard's first live exercise, six candidates raised and all six cleared.

## The meter

`build/check_research.py` measures what the surface counts cannot. When WP-11.1 surveyed it every
buildable node carried 2–4 exemplars, 4–5 sources, 5 constraints and 3 distinctions — a composite of
those spread 1.5× across all 132. The research tranches have moved the exemplar clause and nothing
else (693 exemplars, 3 to 9 a node), so the things that DO separate a researched node from a skeletal one are
computed on every run: exemplars carrying a `precedent`; nodes citing only works a sibling also
cites; `measured` kit parameters with no source on the parameter or its slot, split by whether a
generator reads the slot (the read set is derived from the generators' own string constants, an
upper bound, printed and pinned by equality in `tests/test_research.py` so a change is noticed);
constraints carrying a test against those `scope: judgment`; pack authority strengths over the
node's bindings. `--table` prints every node. `check_kits.py`'s provenance census prints the
`measured-bare` figure beside the `editorial-bare` one it had printed alone for a year.

## The tool

`tdl_precedents(style=…)` lists a node's exemplars with their records joined; where the node
records none of its own (32 families and traditions, every one by convention) it walks the
membership tree down and answers with its members', icons first, labelled as a reading — the
corpus has not ruled that a descendant's precedent may stand for its parent
(`oq/a-family-node-has-no-exemplar`). `precedent_id=` returns one record; `query=` searches.
`tdl_get_style(..., sections=["exemplars"])` joins the record's card onto each exemplar, and an
exemplar with none says `precedent_record: null` rather than looking like one that has.

## What a research pass does, per building

1. Resolve the ids from two surfaces where possible — the Wikipedia infobox and the state
   register, or the data page's own header — copying each from a tool result with the date.
2. Extract the HABS data page at
   `https://tile.loc.gov/storage-services/master/pnp/habshaer/<st>/<st>NN00/<item>/data/<item>data.pdf`
   (NN00 is the item number rounded down to the hundred) more than once with different queries,
   because one extract returns one span; confirm the header carries the survey number.
3. Quote verbatim; carry every figure `as_printed`; never join spans; never invent a date, a
   dimension or an attribution; where sources disagree, record both and change neither.
4. Add the exemplar to the node (append, never rename — the asset layer reads the names) with its
   standing and why.
5. Run `python3 build/check_precedents.py --strict` and `python3 build/validate.py`.

## Open

`oq/a-surveyors-prose-may-source-an-envelope-figure` — may a survey quote source a `measured` kit
parameter of the envelope class? Until it is ruled, the kit pointer convention exists and
nothing uses it. `oq/a-family-node-has-no-exemplar` — 32 nodes, 72 asset records waiting on them.
`oq/a-measured-parameter-with-no-source-is-not-metered` — 542, now metered, none yet sourced.
