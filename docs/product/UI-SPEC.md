# Traditional Design Language — Product Spec Sheet for the Workbench

*Written 24 August 2026 for a UI/UX design engagement. Every count, vocabulary and output
shape in this document was read out of the repository or produced by running the toolchain,
not taken from prose. Where the system is weaker than its documentation, this document says
so, because the interface has to render that weakness honestly rather than hide it.*

Companion document: **`UI-PROMPT.md`** — the brief to paste into Claude Design. This file is
the reference it points back to.

---

## 1. What is being designed

**The Workbench** — the human interface to the Traditional Design Language, a system that
encodes traditional architecture as an executable language and compiles a brief into a
buildable, coherent house.

The system exists and runs. What does not exist is any way for a human to drive it other than
a command line and an MCP server. `STATE-OF-THE-PROJECT.md` Part IV names this precisely:

> **A human interface for plans.** The taxonomy and the orders have interactive tools; the
> plan layers are CLI and MCP only. Given that the stated collaborators are plan development
> leads rather than engineers, this is a gap in the working relationship as much as in the
> software.

That gap is the product. `PLAN-OF-ACTION.md` WP-5.2 scopes a first version of it; this spec
scopes the whole surface, of which WP-5.2 is the centre.

### The thesis the interface must carry

A traditional house is a sentence in a language, and the language can be written down.

- **Elements are the alphabet** — 95 universal slots every style draws from and none owns.
- **Proportioning systems are the grammar** — 36 packs implemented as functions, not tables.
- **A style is a vocabulary and a set of bindings** on that alphabet — 164 taxa, 159 kits.
- **A plan is a sentence, a grouping is a phrase, a parti is a sentence pattern.**
- **And there are solecisms** — 209 named, testable errors: the things that read as *wrong*
  to someone fluent even when no written rule was broken.

The last one is the differentiator and the hardest thing to get right in an interface. A
system that can generate houses but cannot recognise its own solecisms produces what Chomsky
called colorless green ideas sleeping furiously: syntactically valid, and dead. **The
interface's job is to make fluency legible** — to let a plan-development lead at a production
builder ship a house that *belongs* to its place, climate and lineage without a senior
classicist standing over every drawing.

---

## 2. The user and the job

### Primary user — the plan-development lead

Works at or with a production builder. Owns a catalogue of plans. Fluent in plans, framing,
cost and code; **not** fluent in classical proportion, period detailing, or graph databases.
Reads a floor plan faster than a paragraph. Is judged on plans that sell, price, permit and
build — and increasingly on plans that do not embarrass the brand.

**What they are trying to do, in their words:**

1. "Give me four plans for this lot and this buyer, and tell me what's wrong with each."
2. "Why is this plan wrong? Show me, don't lecture me."
3. "What does this style actually require, and what does it forbid?"
4. "What will this cost me to get wrong?"
5. "Get it out of here in a format my drafter opens."

**What they will not tolerate:** being told a plan is good when it isn't; being told a rule
without being told the exception; a number with no source; a tool that hides how it decided.

### Secondary users (design for, do not optimise for)

| User | What they need from the same surfaces |
|---|---|
| **Architect / classicist reviewer** | The provenance chain, the sources, the authority comparison. Must be able to audit and disagree. |
| **Builder principal / exec** | The Console and the Candidate Set only. Cost-of-fault, cycle time, brand risk. |
| **Drafter** | The Drawing Set and Export. Layer names, TDL ids in property sets, what dimensions are clear vs structural. |
| **Agent (LLM) via MCP** | Not a screen, but the 24-tool API the AI rail itself drives. |

---

## 3. Nine product principles, derived from the corpus's own ethics

These are not UX preferences. Each is a rule the system already enforces internally, and the
interface breaks the product if it violates one. `PLAN-OF-ACTION.md` §1 calls the underlying
set "the eleven decisions not to undo."

### P1 — Unjudged is not passed. Three states, never two.

Every checker in this system distinguishes **evaluated-and-failed**, **evaluated-and-passed**,
and **could-not-evaluate**, and is forbidden from collapsing the third into the second.

The interface must do the same, everywhere, visually. A green tick and a red cross is a
two-state design and it is *wrong here*. There must be a third mark that reads as neither
good nor bad — an honest absence of judgment — and it must be as prominent as the other two.
Of 660 style constraints, **295 carry no test at all** (`scope: judgment` — the sources do not
determine them). Those are not a gap to be papered over; they are the moments the tool hands
the decision back to the human, and they are the most valuable interactions in the product.

> "A rules engine that cannot admit ignorance will produce houses that violate no constraint
> and are still dead." — `mcp_server/README.md`

### P2 — Provenance is a column, not a tooltip.

Every value in a resolved kit carries **which ancestor it came from**. Tidewater Georgian
resolves through a 29-level cascade; `appalachian-log-house` reaches 34. `resolve_kit.py`
already prints a source column, and the interface must too — visible by default, not on hover.

Every numeric parameter carries a `kind`, and the distribution is the point:

| kind | count | means | must read as |
|---|---|---|---|
| `measured` | 1,166 | taken from a source or a real building | authoritative |
| `editorial` | 216 | an honest judgment call, marked as one | trustworthy but human |
| `derived` | 163 | computed from another value | secondary |
| `invented` | 14 | **no precedent exists** | conspicuous |
| `code` | 10 | a building-code minimum | non-negotiable |

`invented` at 14 out of 1,569 is a claim about integrity. Make it visible enough that the
number stays small.

### P3 — Refusals are content, not errors.

The composer refuses on purpose. It will not invent a room the parti has no place for. It
will not drop a room that is load-bearing for a rule. It will not present an assumption as a
fact. **It will not tell you a plan is good.**

A refusal gets a card with a statement and a reason, in the flow of work, at the same visual
weight as a result. It never gets a toast, a red banner, or an empty state. `CLAUDE.md` is
explicit: *"Do not 'fix' a refusal into a guess."*

### P4 — Four candidates, never one. No winner's badge.

`compose.py` returns N contrasting candidates ranked fatal-first then by style fidelity, and
the ranking is deliberately not an endorsement:

> "A plan with no fatal findings is not therefore good. The corpus can tell you what is wrong
> and cannot tell you what is alive."

So: rank them, yes. Never crown one. And **`trades_away` must sit adjacent to the score at
all times** — the honest cost of each diagram travels with its number, or the number lies.

### P5 — Exceptions are surfaced before rules.

Faults hang off *slots*, not styles, because the half-width shutter is wrong on every house
that has shutters. Style enters through **846 exceptions**, 496 of them with numeric bounds. A
Georgian five-foot portico is fatal by Craftsman rules and correct by its own.

When a fault applies to the style in view, its `EXCEPTION_FOR_THIS_STYLE` must render *above*
the general rule, not in a footnote. Repeating a rule at a client when the style legitimately
exempts it is the specific failure mode this principle prevents.

### P6 — The drawing is a render of the data. Every mark is inspectable.

`docs/geometry.md`: *"Nothing is drawn that is not in the plan record, so the drawing and the
data cannot disagree."* The interface inherits the contract in both directions — **click any
line, room, window, dimension or hatch and get the record that produced it.** There is no
decorative linework anywhere in this product.

### P7 — Compromises are counted, and they appear on the drawing.

The geometry solver counts every cut that falls off the bay line, because a cut off the bay
line is a joist run that does not land on a bearing wall. A real report reads: *"11 upper wall
lines do not continue to a wall below; each is a transfer beam."*

Eleven transfer beams is a number a builder prices. It belongs **on the drawing, marked at its
location**, not in a panel someone might scroll to.

### P8 — Cost is the builder's language.

32 of 209 faults carry a `cost_saved` — what was saved by getting it wrong. The Four-Foot
Porch: *"3 ft of extra depth on a 30 ft front is roughly 8,000–16,000 USD. This is the single
largest saving in the threshold group and the reason the fault is endemic."*

Every fault carries three tiers of fix — **`right`, `cheap`, `dishonest`** — and the tiers are
named that plainly on purpose. Show all three. The `cheap` fix is what actually gets built,
and naming the `dishonest` one is how the corpus keeps its integrity while staying useful.

Fault causes are not moral failings. Of 209 drivers: cost 57, stock-size 31, trade-sequence
31, catalog-default 29, code 25, material-substitution 18, drafting-convention 14, maintenance
3, **and exactly one is `ignorance`.** The tone of every fault surface follows from that
statistic: this is a system explaining an economy, not scolding a builder.

### P9 — Massing is not style. Rooms are not style. Keep the namespaces apart.

An American Foursquare can be dressed Craftsman, Colonial Revival, Prairie or Mission with no
change to the volume. The interface must never let a style filter silently constrain the
massing or room catalogues, and must never let a user believe a style "owns" a room type.
Where a style and a massing are compared, the corpus prefixes `massing:` to disambiguate — the
UI needs an equivalent visual separation.

---

## 4. The domain in one page (for the designer)

Nine layers. Each is a precondition for the one above it.

```
BRIEF  (area, bedrooms, lot, style, household)
  ↓
STYLE resolves to →  KIT (95 slots)  +  CONSTRAINTS (660)  +  PROPORTION PACKS (36)
  ↓
PARTIS (12) seed candidate PLANS assembled from GROUPINGS (16) of ROOMS (58) on a MASSING (40)
  ↓
VALIDATOR scores each against rooms, adjacency, faults (209), code, style constraints, elevation
  ↓
COMPOSER repairs and ranks  →  4 candidates + decision log + trades-away
  ↓
GEOMETRY places and dimensions on the bay grid, both levels together, relaxations counted
  ↓
STRUCTURE, ROOF, ELEVATION  →  walls, a covering, a composed front
  ↓
[DETAILS, EXPORT — not yet built]
  ↓
DOCUMENTS a builder can price and permit
```

The compiler metaphor is exact and worth carrying into the interface's own language: the
schemas are the language specification, the checkers are linters, the validator is the type
checker, the composer and geometry pass are the compiler front-end.

### Verified inventory (24 Aug 2026)

| Layer | Artefact | Count |
|---|---|---|
| Alphabet | element slots | **95** in 8 groups (ontology 0.5.0) |
| Alphabet | massings | **40**, all with expansion logic |
| Alphabet | rooms | **58**, all with `style_variation` |
| Grammar | proportion packs | **36**, 158 recorded conflicts with building today; bound to **129 of 132** buildable nodes |
| Vocabulary | style taxa | **164** (5 traditions, 27 families, 90 styles, 42 variants), 476 lineage edges, 700 BC–2026 |
| Vocabulary | constraints | **660** migrated; 365 tested, **295 `scope: judgment`** |
| Vocabulary | massing affinities / exemplars | 624 / 482 |
| Bindings | kit files | **159** (132 style/variant + 27 family), all populated |
| Bindings | slot bindings | 1,558 `specified` · 332 `extends` · 223 `forbidden` · 12,992 `open` |
| Solecisms | faults | **209**, 846 style exceptions (496 with numeric bounds) |
| Phrases | groupings / partis | **16** / **12** — partis native to only **39 of 132** styles |
| Critic | reference plans | **14** transcribed (7 good, 7 bad) |
| Evidence | image records | **322 wanted, 0 sourced** |
| Interface | MCP tools | **24** |
| Governance | open questions | **31** |

### The eight slot groups

`massing-and-roof` (13) · `envelope` (18) · `openings` (17) · `classical-apparatus` (8) ·
`threshold` (7) · `interior` (15) · `plan-logic` (10) · `site` (7)

These eight are the primary navigation of the Kit surface and should be recognisable as a set
across the product.

### The five traditions (and their existing accent colours)

The taxonomy tool already assigns one hue per tradition: `#D8B26A` brass, `#7FB3A3` verdigris,
`#8FA8D8` slate-blue, `#C4734A` copper, `#CFA2C4` mauve. Keep the mapping stable — users learn
it.

---

## 5. Exact vocabularies the interface must render

Do not invent parallel vocabularies. These strings appear in the data and in tool output.

### 5.1 Finding severity (validator output)

`fatal` · `serious` · `minor` · `advisory` · `info`

A real header line: `fatal 4  serious 70  minor 59  advisory 1  info 13`. Note the shape of
the distribution — **serious findings dominate by an order of magnitude.** A design that gives
each finding a full card produces a 130-item scroll. Density is a hard requirement, not a
preference. Grouping, collapsing and severity-thresholding (`--min-severity`) are core, not
advanced, features.

### 5.2 Finding layer (the tag on every finding)

`room` · `furniture` · `daylight` · `circulation` · `adjacency` · `privacy` · `servicing` ·
`grouping` · `code` · `style` · `fault` · `elevation` · `plan` · `info`

Layer is the primary organising axis of the critique surface; severity is the secondary one.
The user must be able to pivot between "show me everything fatal" and "show me everything the
daylight layer says."

### 5.3 Kit slot binding

`specified` (this node states the value) · `extends` (adds to an ancestor's) ·
`forbidden` (this style forbids it) · `open` (inherits, or nobody has said)

And slot authoring status: `empty` · `stub` · `drafted` · `reviewed`.

`forbidden` is not "empty." **223 forbidden bindings are positive knowledge** — a gambrel roof
on a Tidewater Georgian is not undecided, it is wrong, and the note says why: *"Northern and
Hudson Valley. Effectively absent in the Chesapeake."* Give `forbidden` a strong, distinct
treatment. It is one of the corpus's best assets and the easiest thing for a UI to lose.

### 5.4 Variant status (within a slot)

`canonical` (1,085) · `permitted` (580) · `atypical` (87) · `forbidden` (851)

Four states, roughly a quarter of them forbidden. This is a ladder, not a binary — render it
as one.

### 5.5 Massing affinity strength

`canonical` · `common` · `possible` · `atypical` · `forbidden`

### 5.6 Fault taxonomy

- **severity:** `fatal` (25) · `serious` (155) · `minor` (29)
- **frequency:** `endemic` (147) · `common` (59) · `occasional` (3)
- **category:** `proportion` (42) · `composition` (33) · `assembly` (27) · `profile-depth`
  (22) · `material` (18) · `alignment` (17) · `anachronism` (16) · `scale` (13) · `omission`
  (13) · `sequence` (8)
- **cause driver:** `cost` (57) · `stock-size` (31) · `trade-sequence` (31) · `catalog-default`
  (29) · `code` (25) · `material-substitution` (18) · `drafting-convention` (14) ·
  `maintenance` (3) · `ignorance` (1)
- **fix tiers:** `right` · `cheap` · `dishonest`
- Two severity axes: **how it reads** and **how it lives.** A fault can be visually mild and
  functionally punishing, or the reverse. Two axes want a two-axis display, not one badge.

Faults have names, and the names are the product's voice: *The Four-Foot Porch*, *The
Half-Width Shutter*, *The Square Window*, *The Chimney That Is Not One*, *The Cardboard
Gable*, *Dormers Off the Rhythm*, *The Blank Wall On The Public Side*, *Flemish bond that
cannot exist*, *The Hatch In The Twelve-Foot Room*, *A Light Count The Glasshouse Could Not
Have Supplied*. Each carries `aka` alternates — *"the rocking-chair test"*, *"the porch you
cannot sit on"*. Typeset the names. They are how a builder will actually refer to these.

### 5.7 Lineage edge types

`descends_from` · `regional_of` (**these two carry the kit cascade**) ·
`references` · `reacts_against` · `revives` (**these do not**)

The distinction is the single most important modelling decision in the project and it must be
visible in the graph. Greek Revival *references* Periclean Athens and *descends from* Federal
carpentry — same author, same trade, new plates, and only the second one transmits practice.
Two edge kinds, two visual treatments, always. Also: `member_of` is a strict single-parent
hierarchy that exists **for browsing only** and carries no inheritance — do not let the UI
imply otherwise.

### 5.8 Confidence

Recorded per node: `high` · `medium` · `low`. Vernacular dating is genuinely uncertain and
several nodes are honestly marked down. Show it.

---

## 6. Information architecture — ten surfaces

```
┌─ CONSOLE ──────────────────────────────────────────────────────────┐
│  projects in flight · recent briefs · corpus health                 │
└────────────────────────────────────────────────────────────────────┘
   │
   ├── EXPLORE ───────────────────────────────────────────────────────
   │     1. THE PHYLOGENY      164 taxa, two hierarchies, typed edges
   │     2. STYLE RECORD       one node, nine sections
   │     3. THE KIT            95 slots resolved, with provenance
   │     9. THE FAULT CORPUS   209 solecisms, element-first
   │    10. PROPORTIONS        36 packs, live drawing, authority compare
   │
   └── COMPOSE ───────────────────────────────────────────────────────
         4. BRIEF INTAKE       the brief, the site, the household
         5. CANDIDATE SET      four contrasting plans, ranked, honest
         6. PLAN WORKBENCH     the canvas — findings inline on the drawing
         7. DRAWING SET        elevation · section · roof · structure
         8. DETAILS & EXPORT   generated guidelines, DXF/IFC/PDF
```

**The AI rail is persistent across all ten** (§8).

---

## 7. Surface specifications

Each surface below gives: purpose · what data it reads · required states · the components it
needs · the interactions that matter · and the edge cases that will break a naive design.

---

### Surface 1 — The Phylogeny

**Purpose.** Find a style, understand where it sits, and see who its real ancestors are.

**Reads.** `dist/taxonomy.json` — 164 nodes, 476 typed edges, precomputed `_cascade` per node.

**Precedent.** `dist/taxonomy.html` exists and works: bars on a time axis, click to light full
ancestry and descent. Do not discard it — evolve it into the product's shell.

**Must show.**
- A time axis spanning **700 BC – AD 2026**. Nearly all the density is 1600–2026 with a long
  classical tail; a linear axis wastes 80% of its width. Solve this — a broken axis, a
  logarithmic run-up, or a two-register layout.
- Four ranks: **tradition → family → style → variant.** Rank is a browsing hierarchy
  (`member_of`), *not* inheritance.
- **Both hierarchies at once, distinguished.** `member_of` is the drawer a node lives in.
  `lineage` is actual descent, and nodes routinely have several parents. Shingle Style has at
  least four ancestors of comparable weight arriving by four different mechanisms.
- Typed edges rendered distinctly (§5.7). Cascade-carrying edges must look structurally
  different from claimed-ancestry edges — weight, not just hue, since one is load-bearing.
- Geography. 5 traditions, styles that are regional variants of one another.
- Confidence, where it is `medium` or `low`.

**Interactions.** Search · filter by rank/region/year/tradition · select a node to light its
ancestry and descent · **select two nodes to compare** (`tdl_compare_styles` — this is a real
job: disambiguating two styles a client or a photograph is between).

**Edge cases.**
- One chronology warning survives by design: `mexican-colonial` (1550) descends from
  `churrigueresque` (1700), because Churrigueresque is a phase *inside* Mexican Colonial's
  three-century span. The UI must render a documented exception as a documented exception, not
  a data error.
- Five traditions is deep on the North American lineage and its European roots. Japanese,
  Islamic, South Asian and African traditions are **acknowledged missing peer trunks**.
  `cape-dutch` already points at an ancestor the graph cannot name. Design an honest empty
  region rather than implying the graph is complete.

---

### Surface 2 — Style Record

**Purpose.** Everything the corpus knows about one taxon, at the depth the reader asks for.

**Reads.** `styles/<id>.json` via `tdl_get_style`. Nine sections; the API **defaults to four**
— progressive disclosure is deliberate and the UI should honour it rather than dumping all
nine.

**Sections.** Identity & dates · geography · description (written to be read by a person) ·
defining characteristics · **diagnostic tells** · **`distinguished_from`** (disambiguation
against nearest neighbours) · proportional system & pack bindings · massing affinities (graded
`canonical`→`forbidden`) · constraints (660 across the corpus) · exemplars (482 real
buildings) · sources.

**Design notes.**
- **Tells and `distinguished_from` are the highest-value content on this screen** for the
  actual job — "is this Federal or Greek Revival?" Give them more room than the description.
- `distinguished_from` entries that compare against a *massing* carry a `massing:` prefix,
  because the two live in separate namespaces (P9). Render the distinction.
- Constraints render in three states (P1): tested-and-passing, tested-and-failing, and
  `scope: judgment` — **295 of 660 are the third.** Where a constraint is a judgment, the UI
  should offer to put the question to the human rather than hide the row.
- Exemplars: roughly 90 of 299 North American rows were individually web-verified, weighted
  toward the obscure. Verified and read-but-unverified should be distinguishable.
- Three nodes are **deliberately unbound** to any proportion pack — `egyptian-revival`
  (trabeated, no arch) and `moorish-andalusian` / `mudejar` (Islamic geometric setting-out).
  This is a named exception in the checker, not a hole. Render it as a stated position with
  its reason, and link to OQ 29.

---

### Surface 3 — The Kit

**Purpose.** The address a design conversation resolves to once a client picks a style. 95
slots, materialised, with the source of every value.

**Reads.** `kits/<id>.kit.json` resolved through the cascade — `tdl_resolve_kit`, which
returns a source column.

**This is the surface where P2 lives.** Real cascade output for `tidewater-georgian`:

```
CASCADE  (nearest first)
  *  0  tidewater-georgian            24 bindings (8 specified, 16 extends, 0 forbidden)
  *  1  georgian-colonial-american    90 bindings (86 specified, 2 extends, 2 forbidden)
  *  2  american-colonial              4 bindings
  *  3  english-georgian               8 bindings
  ...
  * 28  dutch-urban-gable-house       15 bindings
```

Twenty-nine levels. `appalachian-log-house` reaches thirty-four. **The cascade is a first-class
object and needs its own display** — not a breadcrumb, not a tooltip. Craftsman resolved 91 of
95 slots from ancestors before a single line of its own was written; that fact should be
visible and, frankly, delightful.

**Must show, per slot.**
- Group (one of eight), slot id, human name.
- Binding state (§5.3) with `forbidden` given real weight.
- **Source: which ancestor in the cascade supplied this**, at what distance.
- Variants with their four-state status (§5.4), each with its note.
- Parameters with value, unit, and **`kind`** (§5.2) — `invented` and `editorial` visually
  distinct from `measured`.
- The `rule` — the human-readable sentence. *Prose stays beside the test.* Never replace the
  statement with the number.
- The `note` — often the most interesting field in the file, containing the authoring finding.
- Proportion-pack precedence where the slot is governed by one (33 slots on Georgian Colonial).
- Faults filed against this slot, with style exceptions surfaced first (P5).

**Interactions.** Filter to specified-only (the API defaults to it — 95 slots with 12,992
corpus-wide `open` bindings will drown a naive list) · trace a value to its origin · diff two
styles' kits · flip the cascade view between "resolved" and "who said what."

**Edge cases.**
- Depth of authoring varies enormously by node — a variant may carry a handful of
  distinguishing deltas while its family carries dozens. **This is correct**, not incomplete:
  a style only states what the cascade doesn't already give it. The UI must not shame a thin
  kit.
- `composition_parti` is `status: empty` across all 132 nodes. It is read by the geometry
  solver and nothing branches on it yet. An honest "read but unspecified" state.
- `hybridizes_with` transmits a donor's **whole kit**, not the one trait the edge was drawn
  for. ~26 real merge problems surfaced this way and were patched node by node. Where a value
  arrives through a hybridisation edge, that provenance is worth flagging — it is the class of
  error most likely to look right and be wrong.

---

### Surface 4 — Brief Intake

**Purpose.** Capture what the composer needs, and make the *silences* visible before they
become assumptions.

**Reads/writes.** `schema/brief.schema.json`. The shipped brief is short:

```json
{
  "id": "family-georgian",
  "name": "Family house, Tidewater Georgian",
  "style": "tidewater-georgian",
  "target_area_sf": 3200,
  "bedrooms": 4, "bathrooms": 3.5,
  "must_have": ["library", "breakfast-room"],
  "context": { "climate_zone": "3A", "lot_width_ft": 120, "entrance_faces": "S",
               "jurisdiction": "IRC model text, advisory", "budget_tier": "custom",
               "garage_bays": 2 },
  "household": "Two adults, three children, one grandparent visiting often. They eat every
                meal together and want a room that can be shut.",
  "candidates": 4
}
```

**Design notes.**
- **`household` is prose and must stay prose.** *"They eat every meal together and want a room
  that can be shut"* is the most design-relevant sentence in the file. Give it a real writing
  affordance, not a 40-character input.
- The **site** sub-record is what made the Charleston piazza and the Pennsylvania bank-house
  constraints evaluable: street bearing, setbacks, slope, prevailing wind, piazza bearing,
  party-wall condition. It wants a small plan diagram, not six number fields.
- `entrance_faces` accepts diagonals (`SE` satisfied by either adjacent cardinal). A compass
  control, not a dropdown.
- **Live feasibility as the brief is typed.** Before composing: does this style have a native
  parti? (only 39 of 132 do). Does the target area fall inside the parti's `area_range_sf`?
  Does `lot_width_ft` admit the massing's pile? Warn early — "an infeasible brief returns the
  least-bad plan rather than a named conflict set" is the system's own admitted weakness, and
  the interface can partly compensate for it *here*.
- **Every field left blank becomes a decision-log entry.** Show that contract at intake:
  "3 fields unstated — the composer will choose and tell you what it chose."

---

### Surface 5 — Candidate Set

**Purpose.** Four contrasting plans, ranked but not crowned (P4).

**Reads.** `compose.py` / `tdl_compose`. Real output, `family-georgian`:

```
1. Side-Hall Town House          score 291.0   fatal 0  serious 30  minor 63
   3319 sf (3.7% off target) · footprint 24 x 54.0 ft in 3 bays
   why: NOT native to this style — the composer is borrowing a diagram
   trades away: Cross ventilation and daylight on two long walls. In exchange it halves
                the envelope, works on a 20 ft lot, and makes a street wall.
   ! Footprint deeper than about 38 ft — needs a double-pile section; interior rooms unlit.
   ! At 3 bays this diagram is at the width it grows to; further area wants a dependency.

4. Centre Passage, Single Pile    score 472.0   fatal 2  serious 32  minor 58
   why: native to tidewater-georgian; center-passage-single-pile is a canonical massing
   trades away: Floor area for a given envelope, and a great deal of exterior wall. In
                exchange every room has light and air from two sides.
```

**Note what this output teaches the design.** The lowest-scoring candidate is the one *native
to the style*. The best-scoring one is a borrowed diagram the style records no affinity for.
**Score and rightness are not the same axis, and the interface must not conflate them.** Show
`why` (nativeness) as a separate dimension from `score`, side by side.

**Must show, per candidate.** Parti name · score with its arithmetic exposed (100/fatal,
8/serious, 1/minor, less a style-fidelity bonus) · the finding counts · area and % off target ·
footprint and bay count · **`why`** — native, or borrowed and honestly labelled · **`trades
away`** — always adjacent to score, never behind a disclosure · warnings (`!` lines — expansion
limits, pile depth) · the top findings.

**Plus, once and prominently: the decision log.** *"decisions lists what the composer chose
where the brief was silent. Read it — those are the assumptions, not facts."*

**And the closing statement, which should be furniture on this screen, not a footnote:**
*"A plan with no fatal findings is not therefore good. The corpus can tell you what is wrong
and cannot tell you what is alive."*

**Edge cases.**
- A brief may return **fewer than N** candidates: lot-infeasible ones are dropped rather than
  outscored. Design the "we returned 3 of 4, here is why" state.
- A style with **no native parti** (93 of 132) can only be composed for with borrowed diagrams,
  and every candidate will carry the `NOT native` label. This is currently the common case.
  It must read as an honest limitation of the corpus, not as a bad result.
- Comparison across four candidates on ~10 attributes each is a table problem, and a table of
  four dense columns is the right answer more often than four cards. Consider both.

---

### Surface 6 — Plan Workbench *(the centre of the product — WP-5.2)*

**Purpose.** The drawing, with the critique on it. This is where the plan-development lead
lives.

**Reads/writes.** `schema/plan.schema.json`; `plan_check.py` for findings; `geometry.py` for
placement; `render_plan.py` for SVG.

**Plan record shape** (`levels[].rooms[]`):

```json
{ "id": "passage", "type": "centre-passage", "name": "Centre Passage",
  "width_ft": 12, "length_ft": 34, "ceiling_ft": 11, "window_head_ft": 9.5,
  "exterior_walls": ["S","N"],
  "windows": [{ "wall":"S","width_ft":3.5,"height_ft":7,"count":1,"operable":true }],
  "doors":   [{ "to":"drawing","width_ft":3.5 }, { "to":"exterior","width_ft":3.5 }] }
```

Top level carries `style`, `massing`, `groupings[]`, `context` (climate zone, lot width,
`entrance_faces`, jurisdiction, `date_of_representation`, budget tier), `adjacencies`,
`declared`.

**The canvas draws only what is in the record** (P6): rooms, walls, **bay lines**, windows on
exterior walls, door marks with swing arcs where two rooms share an edge, dimensions, a scale
bar, the lot boundary, the setback envelope, a north arrow.

**Findings render on the drawing, at their location.** A real finding:

```
[fatal] Dining Room adjoins Powder Room, which it should not.
  why: A lavatory door opening into or directly visible from a dining room is the single
       most avoidable plan error of the last forty years.
  fix: Separate them, or record the relation as 'not-visible-from' if the separation is real.
```

Note the shape: **statement · why · fix**, and the `fix` frequently offers *"or record the
relation as X if the separation is real."* That is a real interaction — **the user can answer
back**, asserting a fact the record didn't carry. The workbench must let them, and must record
who asserted it.

**Required displays.**
- **Level toggle** — ground and upper, solved *together*. Vertical alignment is a constraint,
  not an afterthought. A ghost of the level below, always available.
- **Relaxation markers (P7)** — each cut off the bay line, each unsupported upper wall line,
  marked *in place*, with a running count: *"11 upper wall lines do not continue to a wall
  below; each is a transfer beam."*
- **The bay grid**, as a real drawing layer. Rooms snap to the structural module the parti
  declares, because traditional houses *are* built on one.
- **Findings by layer** (§5.2), filterable, with a severity threshold. At `fatal 4 / serious
  70 / minor 59 / advisory 1 / info 13` for one ordinary plan, this is a **density problem
  first**. Solve it with grouping and thresholds, not with pagination.
- **Wet-stack, daylight-reach and privacy-gradient as toggleable overlays.** The corpus knows
  useful daylight reaches ~2.25× the window head; it knows which rooms want to share a wet
  wall; it knows a six-rank privacy gradient. Each is a diagram waiting to be drawn.

**Interactions.**
- **Drag a wall on the bay grid and re-score.** The defining interaction of WP-5.2. On release,
  re-run the validator and animate what changed — findings appearing and clearing are the
  feedback loop that teaches fluency.
- **Switch style and watch the constraints change.** Same plan, Craftsman rules instead of
  Georgian: findings appear and vanish. This one interaction demonstrates the entire thesis in
  three seconds and is the most persuasive thing the product can do. **Design it as a feature,
  not a debug affordance.**
- Click any mark → its record (P6).
- Assert a fact the record lacks (`not-visible-from`, `acoustically-separated`) and re-score.

**Edge cases.**
- The solver is a **hill-climb, not an optimiser.** More candidates give better results
  (537 → 489 → 463 from 40 to 800 candidates) — the signature of hill-climbing. Two
  consequences the UI must handle: (a) results are **not deterministic across runs**, so
  "re-solve" must be an explicit, visible action with the candidate count exposed, and
  (b) **an infeasible brief returns the least-bad plan, not a named conflict set.** Until
  WP-2.3 lands, the interface must never let a returned plan imply feasibility was proved.
  When WP-2.3 does land, it returns a *minimal infeasible subset* — design the conflict-set
  display now so the surface is ready.
- Doors are centred on the shared wall. "Never visible from the lavatory" and "never in a
  window bay" are **not yet checked** and the docs say so.
- `room-harmonic` proportions are bound but not yet scored against placement.
- A documented data conflict ships in the reference plan: `dining` declares rear exterior
  walls while the acceptance text wants it on the front. A room's own declared
  `exterior_walls` is authoritative over every compositional preference **by design**. The UI
  should surface such conflicts as *a choice for the human*, which is exactly what the test
  suite pins it as.

---

### Surface 7 — The Drawing Set

**Purpose.** Elevation, section, roof plan and structure — siblings of the plan, generated
from the same record.

**Reads.** `elevation.py`, `structure.py`, `roof.py`, `render_*.py`.

**What exists and must be shown.**
- **Front elevation**, composed: five bays, a centred doorway composed to Gibbs, sash lights
  correct for the declared date, **one head datum per storey**, and a cornice regenerated as
  the style's own entablature reduction at the plan's real storey height. Not a stock
  elevation — a derived one.
- **Structure:** outside-to-outside footprints, wall lines, a bearing-line diagram,
  floor-to-floor heights from the `storey-graduation` pack. *"No 2×10 spans 18 ft silently."*
- **Roof plan:** wing ridges stepping down, pitch inside the style band, chimneys satisfying
  the style constraint.
- **Section**, cut from the same record.

**The honest number this surface must carry.** The elevation generator evaluates **83 of the
177 applicable photograph-measurable faults** — short of its own acceptance target of 100, and
disclosed rather than closed by fabricating data. So the elevation critique panel needs a
permanent, unembarrassed statement: *"83 of 177 applicable faults evaluated; 94 have no model
at this layer."* That is P1 at the scale of a whole surface.

**Design note.** Elevation is where proportion becomes visible, so this surface should be able
to **overlay the governing proportion pack on the drawing** — the order's own divisions, the
head datum, the bay module — turning the grammar from a table into a diagram.

---

### Surface 8 — Details & Export

**Purpose.** Get it out, in a form somebody else can use. Currently the largest unbuilt gap
(WP-5.1, WP-5.3).

**Three deliverables, all generated from data so they cannot drift:**

1. **Design guidelines, per style.** Constraints, forbidden variants, faults with exceptions,
   pack bindings, rendered orders and details. HTML and PDF.
2. **Standard details library.** Every measured-detail asset rendered by the engine, every one
   of the **158 pack conflicts with its ranked substitutions**, the `cheap` fix for every
   fault.
3. **Modelling conventions.** How a drafter models against TDL ids in CAD/BIM: layer naming,
   the bay grid, **which dimensions are clear and which are structural** (a real source of
   error — rooms in this system are clear dimensions).

**Export formats.** DXF (plan, elevation, section, roof, layers per element group) · IFC
(walls, slabs, openings, roof, spaces, **carrying TDL ids as property sets**) · PDF plan set ·
the plan record JSON itself.

**Design note.** The pack conflicts are unusually good material: 158 recorded conflicts between
a historical proportioning system and building today — the 8-foot ceiling against a Corinthian
entablature, the insulated glass unit that cannot take true divided lites — each with a
severity and a **ranked set of honest and dishonest substitutions.** This is described in the
project's own words as *"the project's most commercially defensible material: the knowledge
that lives only in senior architects' heads, written down as executable rules."* It deserves
better than a table.

---

### Surface 9 — The Fault Corpus

**Purpose.** Browse and study the 209 solecisms. The corpus is **element-first**: faults hang
off slots, not styles.

**Reads.** `faults/*.json`, `tdl_find_faults`, `tdl_get_fault`.

**A fault record carries:** `name` · `aka[]` · `slots[]` · severity · frequency · category ·
**`symptom`** (long, specific, and excellent prose) · **`cause`** with `driver`, `explanation`
and `cost_saved` · `rule_violated[]` (each with `kind`, `ref` and a human `statement`) ·
three-tier fix (`right`/`cheap`/`dishonest`) · detection method · `test` · style `exceptions`.

**Read one `symptom` before designing this screen:**

> "A porch that runs the width of the house, has columns, a rail, a ceiling and a roof, and is
> 4 to 6 ft deep. Nobody can sit on it: a rocking chair is 30 to 34 in deep and needs 12 to 18
> in behind it to rock and 30 in in front of it to pass, so a 5 ft porch with a rail on one
> side and a door swinging out on the other has no usable dimension left."

That is the product's voice: specific, dimensioned, unsentimental, and it *shows its
arithmetic.* The typography must be able to carry a paragraph like that — this is not a
badge-and-chip screen.

**Must show.** Filter by slot / style / severity / frequency / category / driver · **style
exceptions surfaced before the general rule** (P5) · `cost_saved` where it exists (32 faults) ·
the good/bad image pair where one exists · the two severity axes (reads / lives) · the `test`,
beside the statement, never instead of it.

**Edge case.** **322 image records exist and zero images are sourced.** Every record carries a
shot spec, alt text written to be reasoned from, and provenance requirements. The interface
must render a *specified-but-unsourced* image as a legible object — the shot spec is real,
usable content — rather than a broken thumbnail. This is P1 applied to the evidence layer, and
it affects every surface that would otherwise show a photograph.

---

### Surface 10 — Proportions & Orders

**Purpose.** The grammar, drawn live.

**Reads.** `proportion_engine.py`, 36 packs; `tdl_get_proportions`, `tdl_compare_authorities`.

**Precedent.** `dist/orders.html` exists — a live order-drawing tool where **every line is
generated by the engine, not traced**, running a JavaScript port checked to agree with the
Python to 0.02 inches. Keep that discipline and that claim.

**Must show.**
- Any pack dimensioned at a real size, **member by member**, with profiles.
- **Authority comparison at a common column diameter** — never a common module; that is one of
  the eleven settled decisions. Real output:

```
                        vignola-doric    gibbs-doric
  column_height_in            8'-0"          8'-0"
  pedestal                    2'-8"          2'-6"
  frieze                        9"             9"
```

- The **non-classical** packs as equal citizens: brick course, timber bay, sash light, storey
  graduation, log module. *Most traditional buildings were proportioned from a material module
  and not from a column* — a UI that puts the five orders front and centre and buries brick
  coursing misrepresents the corpus.
- Each pack's **invariants as evaluable expressions**, proved against the data. The engine
  encodes what the authorities *drew*, not what they said — Vignola's pedestal at 0.35 in
  Corinthian and Composite is the proof that the engine is honest, and that kind of fact
  deserves a place to live.
- The 158 conflicts with building today, with ranked honest and dishonest substitutions.

---

## 8. The AI rail — persistent across all ten surfaces

**What it is.** A design partner that drives the same 24 MCP tools the corpus already exposes,
occupying a rail beside the canvas rather than a modal or a separate page.

**The 24 tools, grouped as the server groups them:**

| Group | Tools |
|---|---|
| Orientation | `tdl_overview` |
| Vocabulary | `tdl_find_style` · `tdl_get_style` · `tdl_compare_styles` |
| Alphabet | `tdl_get_slot` · `tdl_get_massing` · `tdl_find_room` · `tdl_get_room` |
| Bindings | `tdl_resolve_kit` |
| Grammar | `tdl_get_proportions` · `tdl_compare_authorities` |
| Solecisms | `tdl_find_faults` · `tdl_get_fault` · `tdl_measurement_vocabulary` · `tdl_check_measurements` · `tdl_check_style_constraints` |
| Phrases | `tdl_get_grouping` · `tdl_list_partis` |
| Critic | `tdl_plan_schema` · `tdl_check_plan` |
| Generator | `tdl_brief_schema` · `tdl_compose` · `tdl_place_plan` |
| Evidence | `tdl_find_assets` |

**Behavioural requirements — these are the product, not the wrapper.**

1. **Every claim cites its record**, and the citation is a link that navigates the main canvas.
   No unsourced assertions in the rail, ever.
2. **The rail shows what it consulted.** Tool calls are visible as a compact trace — "read
   `tidewater-georgian` kit, 3 faults on `porch_depth`" — because the user's trust is built on
   watching it check rather than on its confidence.
3. **It refuses out loud** (P3). *"You asked for a garage; this parti has no place for one.
   Position matters more than presence."* That is a card, not a failure.
4. **It distinguishes unjudged from passed** in every sentence it writes (P1). The MCP README
   instructs the agent explicitly: *"Tell the human which is which."*
5. **It puts judgment slots back to the human** rather than filling them. 295 constraints and
   every `judgment: true` slot are questions, and asking one well is a feature.
6. **Progressive disclosure is deliberate.** `tdl_overview` is ~1,300 tokens on purpose;
   `tdl_get_style` returns four of nine sections by default. The rail should feel like it is
   *reading further* when asked, and the UI can show that.
7. It never calls a plan good.

**Voice.** The corpus's own: specific, dimensioned, dry, willing to say "I don't know," and
never scolding — remember that exactly one of 209 faults has `driver: ignorance`.

---

## 9. Cross-cutting components (the design system's real work)

These recur on five or more surfaces. Get them right and the product is coherent.

| Component | Carries | Notes |
|---|---|---|
| **Judgment mark** | pass · fail · **unjudged** | P1. Three states. The unjudged mark must read as neutral, not as a warning. Used thousands of times. |
| **Finding row** | severity · layer · statement · why · fix | Must be dense enough for 130 on a screen and expandable to full prose. |
| **Provenance trace** | ancestor · distance · binding · kind | P2. Up to 34 levels. Needs a compact form and a full form. |
| **Source chip** | `measured` / `editorial` / `derived` / `invented` / `code` | Attaches to every number in the product. |
| **Slot row** | group · id · binding · variants · parameters · rule | 95 per kit. |
| **Variant pill** | `canonical`/`permitted`/`atypical`/`forbidden` | A four-rank ladder, not a binary. |
| **Candidate card / column** | score · counts · area · footprint · why · trades-away | P4. Trades-away never collapses. |
| **Fault card** | name · aka · symptom · cause · cost · three fixes · exceptions | P5, P8. Prose-capable. |
| **Refusal card** | statement · reason · what would change it | P3. Same weight as a result. |
| **Decision-log entry** | what was assumed · because the brief was silent | Never styled as a warning; it is a receipt. |
| **Relaxation marker** | on-drawing, at location, counted | P7. |
| **Unsourced-image record** | shot spec · alt text · provenance required | 322 of these. Must look intentional. |
| **Edge glyph** | `descends_from` / `regional_of` vs `references` / `reacts_against` / `revives` | Cascade-carrying edges are structurally heavier. |
| **Dimension string** | feet-and-inches, architectural | `8'-0"`, `2'-8"`, `3'-6"`. Never decimal feet in a drawing context. |

---

## 10. Visual system — extend the existing language

`dist/taxonomy.html` and `dist/orders.html` already establish a coherent language. **Carry it
forward rather than replacing it.** These tokens are lifted verbatim from the shipped file.

```css
--ground:#0B1B29;  --ground-2:#0F2536;  --ground-3:#14304a;
--rule:#24455E;    --rule-soft:#1A3549;
--ink:#EDE7DA;     --ink-2:#9FB3C2;     --ink-3:#63808F;
--copper:#C4734A;  --verdigris:#7FB3A3; --brass:#D8B26A;  --iron:#C4553A;
/* tradition hues, stable mapping */
--t0:#D8B26A; --t1:#7FB3A3; --t2:#8FA8D8; --t3:#C4734A; --t4:#CFA2C4;

--display:"Bodoni Moda", 'Didot', Georgia, serif;   /* names, titles, fault names */
--body:"Archivo", system-ui, sans-serif;            /* prose */
--mono:"IBM Plex Mono", ui-monospace, monospace;    /* every number, id, dimension */
```

**Existing conventions worth keeping.** Mono eyebrows at ~10px, `.16em` tracking, uppercase.
Italic brass for the emphasised word in the masthead. Hairline `--rule` borders instead of
shadows. A 236px left rail. Body at 14px / 1.55.

**Why it fits.** Deep ink-blue ground with warm ivory text is the palette of a drawing office
at night; Bodoni is a plate-engraving face contemporary with Gibbs and Chambers; the copper /
verdigris / brass / iron accents are *building materials* and each ages the way its name does.
This is not decoration — it is the same argument the corpus makes, in colour.

**Semantic colour assignments to establish (currently unfixed):**
- `--iron` (#C4553A) reads as fatal. It is already the most alarming hue in the set.
- `--copper` for serious, `--brass` for minor — a natural descending ladder.
- `--verdigris` for cleared/passing.
- **Unjudged needs its own treatment and it must not be a colour** — a colour will be read as
  a verdict. Use a form instead: an open or hatched mark against `--ink-3`. This is the single
  most important visual decision in the product.
- `forbidden` bindings and `forbidden` variants want a shared, unmistakable treatment — this
  is knowledge, not absence.

**Drawing conventions.** The plan and elevation SVGs are architectural drawings and should
obey drawing convention, not chart convention: line weights that mean something (cut, seen,
hidden, grid), poché or hatch at cut walls, architectural dimension strings with ticks rather
than arrowheads, a real scale bar, a north arrow. Bay lines are a distinct, lighter grid. The
drawing surface may want to invert to a light ground — a measured drawing on ivory inside a
dark instrument is a legitimate and probably correct move, and it makes the drawing the
brightest object on the screen, which it should be.

---

## 11. What is live today vs. what the interface must anticipate

The interface should be designed for the finished system **and must render today's honest
states without embarrassment.** Both columns are real design work.

| Capability | Today | Design implication |
|---|---|---|
| Style graph, kits, faults, rooms, packs | **Live, complete** | Full fidelity. |
| Constraints executable | **660 migrated; 365 tested, 295 judgment** | Three-state everywhere (P1). |
| Plan validator | **Live**, 14 layer tags | Density is the problem to solve. |
| Composer | **Live**, ~30s per brief pre-cache | Needs a real progress state, not a spinner. |
| Geometry solver | **Hill-climb, not an optimiser** | Non-deterministic; cannot prove infeasibility. Never imply it did. |
| Named conflict set on infeasible brief | **Not built** (WP-2.3) | Design the display now; the solver will return a minimal infeasible subset. |
| Partis | **39 of 132 styles** | "No native parti" is the common case, and must read as a corpus limit. |
| Proportion pack bindings | **129 of 132**, 3 deliberately unbound | Render a named exception as a position, not a hole. |
| Elevation fault coverage | **83 of 177 applicable** | Permanent honest statement on the surface. |
| Images | **322 records, 0 sourced** | The record is the object; design it. |
| Export (DXF/IFC/PDF) | **Not built** (WP-5.1) | Design the surface; mark it forthcoming. |
| Generated guidelines & details | **Not built** (WP-5.3) | Same. |
| Drawing-to-record ingestion | **Not built** (WP-5.5) | Design an entry point; 14 plans were transcribed by hand. |
| Cost model | **Seed only** — `cost_saved` on 32 faults | Do not imply a costing engine exists. |
| Code layer | **Advisory IRC model text** | Must be labelled advisory, always. Never render as compliance. |

---

## 12. Success criteria

The design succeeds if:

1. A plan-development lead can go **brief → four candidates → a critiqued drawing** without
   reading documentation.
2. **Unjudged is never mistaken for passed**, at a glance, anywhere, by anyone.
3. Every number on screen can be traced to **its source and its `kind`** in one interaction.
4. A **130-finding plan is legible** rather than a wall of red.
5. **Switching the style on a fixed plan and watching constraints change** demonstrably teaches
   the thesis in under ten seconds.
6. A refusal reads as **the system working**, not failing.
7. A builder recognises **`cost_saved` and the `cheap` fix** as written in their language.
8. The corpus's **prose survives** — symptoms, notes, trades-away and household descriptions
   are the product's soul and must not be compressed into chips.
9. A classicist can **audit and disagree** — every claim reaches its source.
10. Nothing on screen implies a completeness the corpus does not have.

## 13. Explicitly out of scope

Marketing site · authentication and account management · multi-tenant permissions · pricing ·
mobile-first layouts (this is a desktop instrument; tablet review is a nice-to-have) · anything
that would require inventing data the corpus does not carry · any screen that renders a
building-code result as compliance rather than advice.

---

*Source files behind this spec: `README.md`, `STATE-OF-THE-PROJECT.md`, `PLAN-OF-ACTION.md`,
`CLAUDE.md`, `docs/{model,inheritance,compose,geometry,faults,rooms,constraints,plans,assets,proportion}.md`,
`mcp_server/README.md`, `docs/reports/*`, and live output from `plan_check.py`, `compose.py`,
`resolve_kit.py` and `proportion_engine.py`.*
