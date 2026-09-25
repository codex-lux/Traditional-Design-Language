# Phase 14, tranche 2 — the contracts

*Frozen by WP-14.16 on 25 September 2026. Tranche 1's contracts are
`docs/prd/phase-14-the-dossier-and-the-journey.md`. Every section here either extends that document
or states where it stops binding. A lane that needs something this document does not freeze asks the
lead. It does not invent the contract.*

## 0. Read this first

### 0.1 What tranche 2 is for

Tranche 1 gave the workbench one site map, a dossier per style, a journey per house, a plaque on
every page, and a glossary for every word. What it left unfinished, and what this tranche closes:

- **138 named things** (rooms, massings, groupings and partis) end on a "searched" banner.
- **Two styles** cannot be read side by side.
- **Marks carry several meanings each** and have no key.
- **A plan type cannot start a brief.**
- **The assistant** does not know what page it is on.
- **The machine client** tells a different story about a pack from the one the workbench tells.
- **Every reading surface** scrolls sideways on a laptop.
- **The guided example stops at a refusal.**

The analysis is `docs/reports/ux-first-principles-2026-09-24.md` §IX. The packages and waves are
under "Tranche 2" in the Phase 14 section of `PLAN-OF-ACTION.md`.

### 0.2 The rulings (Lucas, 25 September 2026)

| Question | Ruling |
|---|---|
| Tranche 1's freezes (MCP payloads, `rail.py`, `/api/health`, `core.overview()`) | **Lifted per item, and named.** A package may change exactly the frozen surface its item needs. Its report names the change, and it re-cuts that surface's byte-stability test so the test covers the new key and nothing else. Every other frozen surface stays byte-stable. §J.4 of the tranche-1 PRD is amended to this and no further. |
| The worked house | **Try to author a Tidewater plan that places, with a stop rule.** No declared fact may be edited merely to clear a refusal. If the attempt fails, the refusal stays the example and `oq/the-worked-house-has-no-plan-that-places` closes on the evidence. Either way, `glossary/guided-example.json` changes its `more` and its `basis` in the same commit. |
| The parti bridge | **In the brief, guaranteed a place.** Brief schema 0.2.0 gains an optional `parti`. The composer guarantees that parti one candidate among the contrasting set. A parti not native to the style is borrowed, and says so. |
| The assistant | **The page's citation, plus starter questions.** The context gains one line naming the record in view, and the model fetches it with the tools it already has. Starter questions come from each page's `surface-*` record. The same commit corrects the prompt's stale facts. |
| Plate declarations | **Axis and zones as data.** An assembly may declare `axis` and `zones`. A checker holds each zone boundary to the cumulative member heights. The plate draws casings turned and prints the zone string. |
| Marks | **One meaning per hatch, one product key.** §D is the duty table. |
| Width | **Reading surfaces reflow.** §E is the list. |

### 0.3 Defaults taken with the plan's approval

Each of these follows from a ruling or from a standing rule. Each is recorded here so that a later
reader can see it was a choice and not an accident.

1. **Floors.** Transcription keeps a width floor, because it traces a drawing. Export reflows,
   because it is a form.
2. **Glossary labels.** The Glossary's family headings and its term page's eight field labels are
   glossary records (§A.3). Standing rule: a label the app needs is a record. This answers
   `oq/a-glossary-family-has-no-name-of-its-own`, which WP-14.17 closes.
3. **The t3 swatch.** `--t3` becomes `var(--salmon)`, an existing ink whose luminance against
   `--brick` differs by 1.89 : 1, the widest margin of any existing ink.
4. **A contradictory brief.** A brief whose named parti contradicts its own `massing` is refused by
   name before a job starts. It is never silently re-picked.
5. **FaultGauge and PartiDiagram are deferred to tranche 3.** A finding carries no extent for a
   gauge to span, and a parti states topology and no positions, so drawing either would invent
   geometry. Both are filed as open questions (§H). Meanwhile the parti record page shows its
   topology as a table.
6. **Thumbnails.** Wall-datum thumbnails in the Proportions pack index are drawn from served
   geometry only (§C.9).

## A. The glossary, version 0.2.0 — owned by WP-14.17

### A.1 Schema changes (`schema/glossary-term.schema.json`, `"version": "0.2.0"`)

- **`family` gains three values, appended in this order after `figure`:**
  - `glossary-field` — the parts of a glossary record, which label the term page;
  - `mark` — a mark on screen that is not a judgment;
  - `family` — the families themselves.
  - All three join the prefixed families: an id must begin `<family>-`.
- **`binds[].field` gains `glossary.family`**, whose enum is `schema/glossary-term.schema.json`
  at `/properties/family`, with family `family`.
  - The eighth row lands in `build/check_glossary.py`'s `FIELDS` and in
    `workbench/app/src/glossary/fields.js` together.
  - Rule 5 then requires every family value to be bound by exactly one `family-*` record. That makes
    24 records, and `order` equals the value's enum index.
- **`surface.ask`** is an array of 1–3 strings. Each is at most twenty words and ends with "?". It is
  required on family `surface` and allowed on family `section`.
  - These are the starter questions (§C.10).
  - The hygiene rules apply: no digits, no work-package or question numbers, no snake_case.
- **`mark`** is a string matching `^--mark-[a-z0-9-]+$`, allowed on families `judgment`, `mark`,
  `severity` and `variant-status`.
  - The checker holds each value to a custom property that `workbench/app/src/theme/tokens.css`
    defines.
  - Each `--mark-*` property is named by exactly one record.
  - This is the only file outside the corpus directories the checker reads, and it reads it as
    data.

### A.2 Records, and which package authors them

A record is authored by the package that writes the code or data its `basis` quotes, so no basis
quotes code that does not yet exist.

| Records | Author | Basis reads |
|---|---|---|
| 24 `family-*` (one per family value) | 14.17 | `schema/glossary-term.schema.json` descriptions |
| 8 `glossary-field-*`: `aka`, `confusable-with`, `readers`, `is-not`, `surface`, `see`, `binds`, `basis` — the term page's *Also called*, *Not to be confused with*, *Who it is for*, *What it is not*, *The page*, *See*, *Names the value*, *Rests on* | 14.17 | the same schema's field descriptions |
| `fault-section-correct-practice`, `-detection`, `-symptom`, `-cause`, `-cost-saved`, `-rule-violated`, `-fix`, `-test`; `fix-tier-right`, `-cheap`, `-dishonest`; and the card's axis labels (`fault-axis-frequency`, `-category`, `-driver`, `-filed-against`, `-how-it-lives`) | 14.17 | `schema/fault.schema.json` |
| `room` | 14.17 | `schema/room.schema.json` or the rooms README |
| 6 surfaces: `surface-elements`, `surface-room`, `surface-massing`, `surface-grouping`, `surface-parti`, `surface-compare` | 14.17. The `what` and `read` wording describes what the page SHOWS, from the §C payloads; a `try` link to a record is added by 14.23 or 14.26 once the route exists. | the corpus files for each kind |
| `ask` on all 18 `surface-*` records | 14.17 | — |
| `front-door-holds`, `front-door-is-not` (headings for the front door's inventory and "what it is not" sections) | 14.17 | `VISION.md` |
| cross-batch `confusable_with` pairs (the nine in the WP-14.2 report §VI) | 14.17 | — |
| `zone`, `assembly-axis`, `figure-drawn-turned` | 14.18 | `schema/proportion-pack.schema.json` 's new fields |
| `parti-native`, `parti-lineage`, `parti-borrowed`, `named-by-the-brief` | 14.19 | `build/compose.py` |
| `mark-loading`, `mark-low-confidence`, `mark-not-built`, `mark-wanted`, `mark-set-aside`, and `mark` values on the existing judgment, severity and variant-status records | 14.29 | `workbench/app/src/theme/tokens.css` comments |

**Merge rule for other lanes.** A lane other than 14.17 that adds a record adds only a new file. It
never edits the schema, the checker or `fields.js`, and it uses only 0.1.0 fields. It also runs
`python3 build/check_glossary.py` on its own tree.

### A.3 Consumers (14.17)

- **Glossary index.** Family headings read `family-<value>.term`.
- **Term page.** Its eight labels read the `glossary-field-*` records.
- **FaultCard.** Every label, tier word and axis label becomes a `Term`, through
  `faults/licence.js`'s `FAULT_CARD_ORDER` mapped to record ids. This retires the copy ratchet's
  "three tiers" row.
- **Overview.** The inventory and "is not" sections gain `h2` headings from `front-door-holds` and
  `front-door-is-not`.

## B. Routes and citations — owned by WP-14.23; `compare` by WP-14.26

The citation grammar keeps its three spellings (`REF_RE` and `CITE_RE` in `workbench/server/`, and
`parseCite` in the app). No regex changes. Routes change.

### B.1 `SURFACE_PATHS` rows added (`workbench/app/src/router.js`)

| Surface | Path | Positional keys | Address |
|---|---|---|---|
| `elements` | `elements` | `['slot']` | `#/elements` (the index) · `#/elements/<slot>` (a slot's record page) |
| `room` | `room` | `['roomType']` | `#/room/<room-type>` |
| `massing` | `massing` | `['massing']` | `#/massing/<id>` |
| `grouping` | `grouping` | `['grouping']` | `#/grouping/<id>` |
| `parti` | `parti` | `['parti']` | `#/parti/<id>` |
| `compare` (14.26) | `compare` | `['style', 'compare', 'section']` | `#/compare/<a>/<b>[/<section>]` |

- **`SELECTION_KEYS`.** `'compare'` is appended, at the end, never inserted (14.26). 14.27 appends
  `'sheet'` and `'face'` only if they become selection keys. The default is filters (§C.12).
- **A bare record surface** (`#/room`, `#/massing`, `#/grouping`, `#/parti`) shows that kind's
  index: the list the API already serves. It never shows a default record.

### B.2 `routeCite` and `citeFor` (`workbench/app/src/citations.js`), repointed together

| Citation | Tranche 1 lands on | Tranche 2 lands on | `citeFor` inverse |
|---|---|---|---|
| `slot:<id>` | `#/style/-/kit/<id>` (interim `SlotPanel`) | `#/elements/<id>` | `slot:<id>` |
| `room:<id>` | the bench with `{roomType}` and a Spotlight | `#/room/<id>` | `room:<id>` |
| `massing:<id>` | the phylogeny with a Spotlight | `#/massing/<id>` | `massing:<id>` |
| `grouping:<id>` | the bench with a Spotlight | `#/grouping/<id>` | `grouping:<id>` |
| `parti:<id>` | the candidates with a Spotlight | `#/parti/<id>` | `parti:<id>` |
| `kit:<style>` / `kit:<style>#<slot>` | the dossier kit section | unchanged | unchanged |
| a compare place | — | — | `null`: the grammar has no two-style kind, and none is added |

- **`plan:` is unchanged.** It names a placed room on the bench, not a room type.
- **`e2e/router-unit.mjs` holds the identity `routeCite ∘ citeFor` for every kind.**

### B.3 Addresses the old `routeCite` wrote, which people have kept

Each of these is read as the new place and rewritten in the address bar by `replaceState`, exactly
as `#/kit/` is today:

- `#/style/-/kit/<slot>`
- `#/workbench?roomType=<id>`
- `#/workbench?grouping=<id>`
- `#/phylogeny?massing=<id>`
- `#/candidates?parti=<id>`

The rule is a table in `router.js` beside `LEGACY_PATHS`: one row per (surface, key) pair, not a
branch. `#/brief?parti=<id>` is NOT legacy. It is the parti bridge's seed (§C.5) and stays.

### B.4 `navModel`

- **Library** gains `elements` after `faults`, labelled by `surface-elements`.
- The record pages and `compare` are places without a rail item.
- Crumbs:
  - a slot: Library › Elements › the slot;
  - a room, massing, grouping or parti: Library › Elements › the record, with the kind as the
    record's eyebrow;
  - compare: Styles › `<a>` › compare with `<b>`.

## C. Payload and data contracts

Each row names its owning package. "Frozen" names a tranche-1 freeze this row lifts under ruling
0.2 (1). A payload not named here is byte-stable.

### C.1 `GET /api/health` gains `session` — 14.20 · frozen: `/api/health`

- `session` is `auth.authorised(request)`, a bool.
- The route stays ungated, and `auth.OPEN_PATHS` is unchanged.
- The boot (`App.jsx boot()`) reads `auth` and `session`. When auth is required and there is no
  session, it makes no gated request.

### C.2 An evaluation names its plan — 14.20

- `workbench/server/evaluate.py` writes `out["plan"] = plan["id"]` before any early return.
- `journey.js` exports `evalPlanOf(lastEval)`, which returns `lastEval.plan ?? lastEval.check?.plan`.
  It is the only reader, and `App.jsx` uses it for the stale-evaluation clear.
- `core.check_plan`'s MCP payload is unchanged.
- This closes `oq/an-evaluation-whose-check-errored-names-no-plan` on its answer 1.

### C.3 Proportion-pack assemblies declare `axis` and `zones` — 14.18

`schema/proportion-pack.schema.json`, assembly object (`additionalProperties` stays false):

```
"axis":  {"enum": ["up-the-wall", "across-from-the-jamb"]}
         absent means up-the-wall, as every stack is today
"zones": [{"name": <string>, "to_parts": <number>}]
         minItems 2, cumulative, bottom to top (or jamb outward)
```

**The checker** (`build/check_orders.py`, beside the assembly sum check, which already covers every
pack) holds each assembly with zones to four rules:
- zones strictly increase;
- every `to_parts` equals a cumulative member-height sum at some member boundary;
- the last equals the assembly's total in parts;
- an assembly with `sums_check: false` may not declare zones.

**The data.**
- `trim-classical`'s three casings take `across-from-the-jamb`. The basis is each casing member's own
  note, which says the height is measured across.
- The Georgian wall section takes zones 4 / 16 / 19 (pedestal, wall field, entablature), because
  the module note gives "Pedestal 4, wall field 12, entablature 3".
- Other sections take zones only where their pack's own words give them. Nothing is authored from
  outside the pack.

The **`module.equals`** enum gains `storey_height`, `room_width` and `opening_width`. They are added
to `storey-graduation`, `room-harmonic` and `opening-pointed` only where check 19(c) of
`check_systems.py` passes. Where it fails, the package stops, files an open question and authors
no number.

### C.4 `tdl_get_proportions` serves what the workbench serves — 14.18 · frozen: that MCP payload

- **A pack with no order stack** lists every assembly as
  `{id, height_modules, height_in, members: <count>, axis?, zones?}`.
- **`hint`** names the pack's own assembly ids.
- **`lower_diameter_in`** is withheld on a pack with neither a stack nor a column.
- **The module binding** (which building dimension `module.equals` reads) has one spelling, in
  `mcp_server/core.py`, and `corpus.proportions_with_members` calls it. A pack whose module is bound
  to the ceiling is evaluated at the module's own default when no ceiling is given, which settles the
  108-against-114 disagreement.
- **A digest pin** holds the payloads of the stacked packs byte-identical.
- This closes `oq/mcp-proportions-serve-no-assemblies-for-non-order-packs` (answer 1) and, with 14.24,
  `oq/casings-are-measured-across-and-drawn-upright` (answer 1).

### C.5 A brief may name a parti — 14.19 · frozen: `tdl_brief_schema`, `tdl_compose`, `tdl_list_partis`

- **Schema.** `schema/brief.schema.json` becomes version 0.2.0 and gains
  `"parti": {"type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"}`.
- **`compose.nativity(parti, style)`** returns `native`, `lineage` or `borrowed`. It is the one
  spelling of that relation:
  - `native` means the style is in the parti's `styles`;
  - `lineage` means one of the style's `plan_check.style_chain` is;
  - `borrowed` means neither.
  - `core.list_partis` and `compose.pick_partis` both read it.
- **`compose.check_brief_refs(brief)`** refuses, by name, an unknown `parti`, and a `parti` whose own
  massing contradicts the brief's `massing`. `core.compose`, `jobs._validate_brief` and
  `compose.main` all call it, before a job starts.
- **The guarantee.** The named parti is scored by the same arithmetic but kept past the cut. After
  `_sort_key` and the revision loop, if it is not among the returned candidates it is appended as
  candidate N+1. It displaces nothing, which keeps *"a plan carrying a fatal never displaces a clean
  one"* true. If the lot drops it, the result says so. It is never silent.
- **The result** gains `named_parti: {parti, nativity, returned: bool, rank | why}`, and each
  candidate gains `named_by_brief: bool`. A borrowed candidate's `why` says it was borrowed.
- **`core.list_partis(style, include_borrowed=False)`** returns native and lineage partis, each with a
  `nativity` field. `core.get_parti(id)` wraps `core.load_parti` and returns
  `{parti, nativity_by_style: {native: [...], lineage: [...]}}`. The route is
  `GET /api/partis/{id}`.
- **Job stage events** carry `total`, so the journey can say "composing k of N".
- This closes `oq/a-brief-cannot-name-a-parti` (answer 1, guaranteed a place).

### C.6 Record-page data — 14.23

- **`GET /api/slots`** returns every slot row as `core.get_slot` serves its `slot`, plus
  `specified_by`: the count of styles whose resolved kit binds it `specified`. The count is
  computed, never typed.
- **`api/client.js`** appends `massing(id)`, `grouping(id)`, `parti(id)` and `slots()`. It edits no
  existing function.
- **Inverse lists.** Each record page shows the relation from both sides, computed from the forward
  relation, and a test holds the two directions to each other:
  - massing: styles by massing affinity;
  - parti: styles by nativity;
  - grouping: partis carrying it;
  - room: groupings containing it.

### C.7 One kit authority — 14.26 · frozen: `tdl_resolve_kit`, `/api/kit`

- `core.resolve_kit` is rebased on `rk.resolve_slots` and keeps its row shape. The pairs whose
  answer moves are named in the report, measured on the day; about 38 were measured at planning.
- **Fallback, if the provenance strings cannot be kept:** compare reads `core._resolved_kit` alone, a
  named disagreement list may only shrink, and an open question is filed.
- **`GET /api/compare/{a}/{b}`** returns `{a, b, identify, kit, proportions, plans}`:
  - `identify` is `core.compare_styles`;
  - `kit` is one row per slot where the two differ (binding, canonical, forbidden, source);
  - `proportions` is `style_packs` for each style;
  - `plans` is nativity for each style.

### C.8 The assistant's context — 14.22 · frozen: `rail.py`, the `/api/rail/messages` context, MCP tool descriptions

- **Context.** `RailHost` reads the nav store and sends `context.cite`: the page's own
  `citeFor(...)`, or nothing. It also sends a compact `context.candidate_summaries`.
- **The line.** `_context_block` adds one line naming the cite, only when
  `citations.validate` accepts it. Anything else is omitted, never echoed.
- **`SYSTEM`.**
  - It takes its self-description from `glossary/assistant.json`.
  - It computes the fault figure and the tool count instead of typing them.
  - It lists the citation kinds from one vocabulary, `citations.KINDS`. That is a vocabulary, not a
    fourth regex.
- **Stale prose corrected.** "The rail" leaves the prompt, `tools.py`, `limits.py`'s refusal text,
  and the MCP tool descriptions' typed "209".
- **Starter questions** come from the page's `surface-*` record's `ask`, through a pure
  `rail/starters.js`. Nothing is shown while the glossary loads.
- This closes `oq/the-assistant-is-blind-to-the-page` (answers 1 and 3, citation form).

### C.9 Plates at the pack's word — 14.24

- **Drawing.** A turned axis swaps the extent (`plate/assemblyLayout.js extentOf`). The plan gains
  one `rotate` beside its translate and scale. No arc arithmetic is added to JS, and `OrderPlate` is
  unchanged.
- **Zone string.** Where `zones` exist, the plate draws zone ticks and a zone string in parts, with
  inches through `feetInches16`. There is no string where they do not.
- **Captions.** *Drawn upright* is captioned only where no axis is declared. *Drawn turned* is
  captioned where one is.
- **Sliders.** Class-A packs get building-input sliders driven by `module_bound_to`.
- **Thumbnails.** Each drawable pack in the pack index shows its first assembly at the wall datum,
  from served geometry only. If the list route grows by more than a measured budget, stated in the
  report, the thumbnails move to `GET /api/proportions/thumbs`.

### C.10 Starter questions and page heads

A surface record's `ask` is shown verbatim by the assistant pane as buttons that fill the input.
They never send on their own.

### C.11 Worked house — 14.21

The method is the one approved in the plan. The outcome, success or failure, reaches
`glossary/guided-example.json` in the same commit. On success, a tour package (WP-14.28) is built.
On failure, it is not built, and nothing promises a house.

### C.12 URLs — 14.27

- **Filters, not selection keys:**
  - `DrawingSet`'s `sheet` and `face` join its `useSurfaceFilters` spec;
  - `ExportDetails` gains a face picker and sends `face` to `/api/drawings` and `/api/export`;
  - Phylogeny's compare becomes the `compare` key.
- **Selection keys:**
  - Phylogeny's descent and picks write the selection;
  - `CandidateSet`'s pick writes `candidate`.
- **No default record.** `DEFAULT_TAXON` and `DEFAULT_FAULT` go. A bare surface shows its index and
  no record.
- **Faults for one style.** With a style in the URL, the fault list is grouped as verdict here /
  lineage / universal, from `corpus.dossier_faults`.

## D. The mark duty table — owned by WP-14.29

Every hatch has one meaning. Each is named by one glossary record, with `mark` equal to the token.

- **Duty tokens.** The key is the Glossary's `MarkKey`, reachable from the `?` card. Consumers use
  `--mark-*`, never a raw `--hatch-*`. The `--judge-unjudged-fill` alias is retired.
- **Material hatches.** Masonry, crosshatch, water and lawn are drawing materials, one meaning each.
  They are keyed where the sheet keys them.

| Duty token | Form | Meaning | Record | Today's consumers moving onto it |
|---|---|---|---|---|
| `--mark-unjudged` | `--hatch-unjudged` | could not evaluate | `judgment-unjudged` | `JudgmentMark` (unjudged), `Chrome` masthead count, `AiRail`, `FaultCard` licence frame (unjudged licence only) |
| `--mark-yours-to-judge` | an open square outlined in `--gilt-deep`, no hatch | a decision left to the reader | `judgment-yours-to-judge` | `PlanWorkbench` "yours to decide" |
| `--mark-not-applicable` | an em rule, no square | the question does not arise | `judgment-not-applicable` | `PlanWorkbench` "not applicable" |
| `--mark-passed` / `--mark-failed` | filled square, green-deep or brick, plus the word | evaluated | `judgment-passed` / `judgment-failed` | verdict squares (never colour alone: the word reaches assistive tech) |
| `--mark-refused` | brick outline | refused a drawing | `judgment-refused` | refusal marks |
| `--mark-loading` | no square; the word and `aria-busy` | loading | `mark-loading` | `BriefIntake` loading state |
| `--mark-low-confidence` | dashed outline | low confidence in a date or placement | `mark-low-confidence` | `Phylogeny` tree confidence |
| `--mark-not-built` | `--hatch-forthcoming` | planned structure the corpus does not yet hold | `mark-not-built` | `ExportDetails` forthcoming cards |
| `--mark-wanted` | `--hatch-45` | wanted, and absent from the corpus | `mark-wanted` | `UnsourcedImageRecord`, the phylogeny's acknowledged missing trunks |
| `--mark-set-aside` | `--hatch-135` | considered and set aside | `mark-set-aside` | `CandidateSet`'s dropped diagrams |
| `--mark-forbidden` | `--hatch-forbidden` | forbidden by the kit | `variant-status-forbidden` | `SlotRow`, `VariantPill` |

`BriefIntake`'s "conflict set · on the bench, not here" is a pointer, not a state. It becomes a link
and takes no hatch.

`--t3: var(--salmon)`. A test holds `--t3` to differ from `--brick` and to be an existing ink.

This closes `oq/one-duty-per-hatch`. If 14.29 finds a consumer that no row fits, it adds a row with
a record and names it in the report. It never widens an existing row.

## E. Width — owned by WP-14.30

- **Reflow** (no sideways scroll at 1280 × 800, measured `scrollWidth − clientWidth ≤ 1`): the style
  dossier and the Styles index, Proportions, Faults, Phylogeny, Brief, Candidates, Export, the
  Glossary, the front door, Elements and every record page, and Compare.
- **Floor** (a minimum on `<main>`, scrolling inside it, with the masthead held to the window): the
  Plan Workbench sheet, the Drawing Set (including the Round), and Transcription.
- **Mechanism.** The `#root{min-width:1380px}` floor goes. The reflow/floor table lives in
  `state/layout.js`, beside the pane defaults. It replaces the hard-coded pair in `App.jsx`.

## F. Owners of shared files, by wave

| Wave | Owners |
|---|---|
| 1 (14.17–14.21) | **14.20:** `App.jsx`, `journey.js`, `client.js`, `proportion_engine.py`, `fmt.js`, `evaluate.py`, `auth.py`. **Split by function in `app.py`, `mcp_server/core.py`, `corpus.py` and `server.py`:** 14.18 the proportions functions and routes; 14.19 the parti, brief and compose functions and routes; 14.20 health. **14.17:** glossary schema, checker and `fields.js`; `Glossary.jsx`, `FaultCard.jsx`, `Overview.jsx`. **14.21:** its plan file and `guided-example.json` only. |
| 2 (14.22–14.25) | **14.23:** routing, `navModel`, `crumbs`, `App.jsx`, `client.js`, and the server's record routes. **14.23 then 14.25:** `PlanTypes.jsx` and `CandidateSet.jsx`. **14.24:** `Proportions.jsx` and `plate/*`. **14.22:** `rail.py`, `RailHost.jsx`, `tools.py`, `limits.py`, and `server.py`'s docstrings. |
| 3 (14.26–14.29) | **14.26:** routing, and `core`/`corpus`/`app` for compare. **14.27, then 14.29's hatch lines:** Phylogeny, CandidateSet, Export, Faults, DrawingSet. **14.29:** `tokens.css`. |
| 4 (14.30) | `tokens.css` floor, `App.jsx`, `layout.js` |
| 5 (14.31) | all of `src` |

**`walk.mjs`.** Each package edits its own blocks and appends.

**Merge order:**
- wave 1: 14.20 → 14.17 → 14.18 → 14.19, with 14.21 whenever it is ready;
- wave 2: 14.23 → 14.25 → 14.24 → 14.22;
- wave 3: 14.26 → 14.27 → 14.29 → 14.28;
- then 14.30, 14.31, 14.32.

## G. Must not

A fourth citation-grammar spelling. Definitions written in the app. An invented source. Collapsing
unjudged. Count literals in JSX or tests. New colours. Arc geometry in JS, or any change to
`OrderPlate`. Drawing what the record does not hold. A frozen surface changed by a package that does
not name it. Laundering a Tidewater plan into placing. A tour promising a house WP-14.21 did not
deliver. Tests in `src/` subfolders, or tests that import from `node_modules`. Parallel pytest in one checkout.
Numbering an open question, or citing a report before it exists.

## H. Open questions filed by WP-14.16

- `oq/a-fault-gauge-has-no-extent-the-record-states`: a gauge needs both ends of a scale, and a
  finding carries only its value and its threshold.
- `oq/a-parti-states-rooms-and-doors-and-no-positions`: any diagram of a parti invents positions.
- `oq/the-link-ink-reads-below-aa`: `--gilt-deep` on `--paper` reads 4.09 : 1.

The seven questions ruled on 25 September are marked IN PROGRESS, each with its ruling and the
package that executes it. Each is closed by that package.
