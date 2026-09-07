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

## The archival vocabulary, and the ids nobody checks (WP-11.5)

`refs[].kind` is a closed enum and `ID_SHAPES` in `build/check_precedents.py` holds each kind's id
to a shape. Europe needed seven more kinds — `niah`, `merimee`, `bic`, `rijksmonument`,
`denkmalliste`, `vincolo`, `unesco` — beside the `historic-england`, `cadw` and `historic-scotland`
that were already there and that no record used.

**A shape is written from the register's own statement of its format, never from a remembered
example.** Historic England's *Understanding List Entries* says *"Every List entry has a unique
7-figure reference number"*, corroborated against fifteen sampled numbers, so `HE_LIST_RE` is
`^1\d{6}$`. The counter-example is in this repository's own history: `NRHP_RE` was written from the
legacy 8-digit form and rejected a valid 2019 listing on the first corpus that contained one.

**A kind with no shape rule is NAMED, not left to a silent miss.** `ID_SHAPES.get(kind)` returns
`None` for an unknown kind and no check runs, so an unshaped kind is an id nobody validates and
nobody knows about. `UNSHAPED_ID_KINDS` lists them, the checker prints the count every run, and it
is ratcheted. It read **58 on its first run** — every one a `state-register` id from the American
tranches, carried unchecked since Tranche 1. The ceiling falls by adding a shape with its evidence,
never by inventing one. A test asserts that every kind the schema admits is either shaped or named
unshaped, so there is no third, silent category.

**A national heritage list entry may BE the `survey` block.** Measured 5 Sep 2026: Historic
England's `Details` section prints MATERIALS, PLAN and EXTERIOR paragraphs stating storeys, bays,
roof covering, string-course positions and window lights — the same job as a HABS Part II and often
richer. For such a record `item` is the List Entry Number, `data_url` the entry URL, `prepared` the
`Date first listed` and any amendment date, and `survey_no` is absent because there is no HABS
number; the `page` marker names the section, since a list entry is not paginated. The quote-field
enum gained `materials`.

**And the block says WHICH REGISTER issued its `item`, because widening the description without
widening the code refused 268 European surveys on the first global run.** `survey.register` is a
closed enum — `loc-item` (the default, the Library of Congress item id an American HABS survey
carries), `historic-england`, `historic-scotland`, `cadw`, `niah`, `merimee`, `bic`,
`rijksmonument`, `denkmalliste`, `vincolo`, `unesco`, `state-register`, `institution`, `wikipedia`,
`other` — and it does two jobs. It selects which id-shape rule the `item` is checked against, so a
7-figure Historic England number is not held to the Library's `xx0000` form. And it decides whether
the `item` may be an IDENTITY at all: `unesco`, `institution`, `wikipedia` and `other` are declared
**SERIAL** in `SERIAL_REGISTERS` and are never one, because a UNESCO inscription names a serial
PROPERTY exactly as a National Register district does — inscription 175 covers a dozen Medici
villas, so five of them sharing it is evidence of nothing, and before the field existed it read as
one building written five times.

## A kit figure may cite a building (WP-11.4, Ruling A, 5 Sep 2026)

A `measured` kit parameter may carry `source: "precedents/<id>#measurements[<n>]"` at
`confidence: medium`, and **`check_precedents.py::kit_source_agrees` holds its number against the
measurement's** in three verdicts, never a bool: **agrees**, **contradicts** (a hard error — a
source that disagrees with the figure it is cited for is worse than none, because it reads as
provenance), and **could not compare** (a warning; a categorical parameter, an unparsed
measurement, or a unit mismatch, and never read as agreement).

**A number cites a number.** The `#survey.<field>` form still resolves and still supports a
CATEGORICAL call, but a `kind: measured` parameter using it is refused: a quote cannot be held
against a figure. This is what makes the ruling's own caution — *"a source pointer that resolves is
not a source that agrees"* — mechanical rather than a reader's job. `measurements[]` carries a typed
`value` and a `unit` from a closed enum matching the kit's own, which is the whole reason the
comparison is possible.

**Six figures cite a building today**, each adjudicated by hand and each carrying a `note` arguing
the pairing: `dutch-colonial-american`'s wall thickness (22 in, corroborated by a second exemplar at
20), `garrison-colonial`'s framed overhang (14 in), `italianate-american`'s first-floor ceiling
(12 ft), `appalachian-log-house`'s pen width and depth (16 × 18 ft, with the survey stating the
CAUSE — the longest log a sash-saw mill will cut), and `shotgun-house`'s room count (3).
`source_agrees` is a **floor**: it is the one counter that reads worse when a citation is deleted,
and the three ceilings beside it all read better.

**What the ruling does not license.** A band is not a fact about one building. A survey sources a
BAND only where the band is the fact restated or several surveyed exemplars agree; a figure sitting
INSIDE a band it did not set is a non-violation, not a source, which is why
`garrison-colonial.overhang_max` 24 in is deliberately uncited beside the 14 in that is. And the
guard compares numbers, not meanings — `oq/a-source-that-agrees-numerically-may-be-the-wrong-quantity`.

## A new `measured` figure must say where it came from (WP-11.4, ruled 5 Sep 2026)

`build/check_kits.py` refuses a `kind: measured` parameter that carries no `source` and whose slot
carries no `sources[]`, unless its `(node, slot, parameter)` triple is in
`build/measured_unsourced_grandfathered.json` — the 542 that predate the gate. Removing a triple
from that list is a one-way door: it means the parameter now cites something.

**The gate is per-parameter because the ratchet that preceded it was a NET COUNT, and that hole is
measured rather than argued.** `check_research.RATCHET["measured_unsourced"]` is a ceiling on a
total, so a commit that sources one figure and adds an unsourced one leaves the total at 542 and
passes. Run against exactly that mutation, `check_research --strict` returned **0** with an
unsourced `measured` parameter sitting in the tree, and `check_kits.py` returned **1**. A counter
that nets out is this repository's commonest blind guard; refusal by identity cannot net.

**Part 1 of the ruling was not given and nothing is re-kinded.** The 542 keep their label and
`check_research.py`'s ceilings keep counting them down. The gate stops 542 becoming 543; it does
not pretend the 542 are sourced.

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

**A REGIONAL POPULATION IS A `type-model` RECORD, NOT A REFUSAL** (ruled 5 Sep 2026, the day the
refusal field was added and the day Europe raised it). An exemplar row naming *"the Leopoldine
farmhouses of the Val di Chiana"* — several hundred surviving under one land-reclamation programme —
or *"the farmhouses of the Simmental"* names a type, not a building, and the type carries its own
record with the programme's or the region's own sources. It is **not** `no_precedent`: the closed
refusal vocabulary has no word for a population and does not need one. Two such rows were marked
`body-of-work` and withdrawn, because that value means an architect's output and these have no
architect. The Levittown ranch model is the working precedent for the shape.

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

## A family carries type specimens, derived (WP-11.6, Ruling B, ruled 5 Sep 2026)

*"Families carry type specimens, DERIVED from members' `standing: icon` exemplars — a report of the
members, not a second authoring. The 5 traditions stay empty."* Cardinality ruled the same day: **one
per member node**, deduplicated by building. 121 rows over all 27 families.

**A family's exemplars are not authored and must not be hand-edited.** `build/family_specimens.py`
derives them — each member's first `standing: icon` row, in rank-then-id order, skipping a building
an earlier member already claimed — and `--apply` writes them. `check_precedents.py` fails the build
when a family's stored rows are not the derived ones (`family_specimens_drifted`, a hard 0), because
a member that changes which building it calls its icon changes what its family stands for, and a
derived record nothing re-derives is a snapshot of a judgment that has since moved.

The `why` names the member and points at that node for the reason rather than copying its sentence.
A copied sentence is a second spelling, and this repository has been caught by that in
`openings.required_wall_ft`, in the citation grammar and in the riser divisor. Nothing new is
asserted about any building in a family's rows.

**A building may stand for two families and that is not a duplicate.** Larkin House is the icon of
`monterey-colonial` and of `monterey-revival`; the American Gothic House of
`american-farmhouse-vernacular` and of `folk-victorian`. A style and the revival that quotes it name
one building, and both families' rows point at the one record.

**The five traditions stay empty by the ruling**, so `nodes_with_a_precedent` may never reach 164.
`tdl_precedents` walks the membership tree for a tradition and its note says the walk is the answer
rather than that nobody has decided — but it still says it is a reading: what stands for a member
does not automatically stand for everything above it.

## The meter

`build/check_research.py` measures what the surface counts cannot. When WP-11.1 surveyed it every
buildable node carried 2–4 exemplars, 4–5 sources, 5 constraints and 3 distinctions — a composite of
those spread 1.5× across all 132. The research tranches have moved the exemplar clause and nothing
else (800 exemplars, 4 to 9 a node), so the things that DO separate a researched node from a skeletal one are
computed on every run: exemplars carrying a `precedent`; nodes citing only works ANOTHER NODE also
cites (corpus-wide, not by family: the word was "a sibling" until WP-11.7 and the true sibling
reading is 9); `measured` kit parameters with no source on the parameter or its slot, split by whether a
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

**All four of this layer's founding questions were ruled on 5 Sep 2026 and three are executed**, so
what stood here is in the sections above rather than in this list: A (a kit figure may cite a
building), C part 2 (a new `measured` figure must carry a source), D (a record may be a district or
a type model) and B (a family carries derived type specimens). **C part 1 is NOT ruled**: the 536
existing unsourced `measured` figures are metered and none is re-kinded.

What is open here now:

`oq/a-source-that-agrees-numerically-may-be-the-wrong-quantity` — `kit_source_agrees` compares a
`unit` and cannot compare a QUANTITY, so two counts of different things agree if the numbers do.
`oq/a-parameter-has-one-source-field-so-a-building-cannot-corroborate-a-reasoned-figure` — 489
`measured` parameters already cite an internal source, so Ruling A can never reach the corpus's
most-reasoned figures.
`oq/a-survey-contradicts-a-kit-figure-and-nothing-decides-it` — 20 contradictions, three by a node's
own exemplar, and nothing says what a contradiction obliges anyone to do.
`oq/a-district-number-on-a-contributing-property-is-not-that-buildings-identity` — 51 archival ids
the duplicate guard drops, of which 27 are an individual building's own listing number.
**And a locator that does not resolve is not a locator**: `--live` exists and no tranche has run it,
so nothing in this tree checks that one does.
