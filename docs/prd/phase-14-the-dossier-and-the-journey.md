# PRD — Phase 14: The Dossier and the Journey — the frozen contracts

*Written 24 September 2026 against commit `d565dea` of `codex-lux/Traditional-Design-Language`, as
WP-14.0's second deliverable beside the analysis it answers,
`docs/reports/ux-first-principles-2026-09-24.md`. That report says why the workbench is being
rebuilt and what was chosen; this document says, exactly, what every parallel package builds
against. Several agents work at once in separate git worktrees, so every id, route, payload field,
prop and store key a second package depends on is fixed here, verified against the tree, and not
re-decided in a worktree.*

*Every fact about the current code carries a `file:line` read at `d565dea`. Every figure that can
move is dated "measured 24 Sep 2026 at d565dea" and is a snapshot, never a standing claim. Future
package reports are named as "WP-14.N's report" and never by path, because
`build/check_ids.py::check_reports` fails the build on a report path that does not yet exist.*

---

## 0. Read this first

1. **Authority.** The rulings of 24 Sep 2026 (practitioners first; definitions in new glossary
   records the app never writes; rebuild the navigation now around a Style Dossier and a House
   Journey with the current surfaces as indexes and the URL-as-citation-grammar kept; the dossier
   section names; the assistant's name; the narrow-screen fold; the one ungated sentence on the
   Gate) are recorded verbatim in the report's §II and are not restated as arguments here.
2. **These contracts are frozen for tranche 1.** A package that finds one wrong does not change
   it in its worktree: it stops, says so in its report, and the lead amends this file in one
   commit that every open lane then rebases onto. Where this file and the repository disagree
   about the *current* code, the repository is right and this file is stale; where they disagree
   about what a package *builds*, this file is right until amended.
3. **The operating rules in `CLAUDE.md` and `PLAN-OF-ACTION.md` §1 apply in full**: unjudged is
   not passed; sources or `kind: editorial`; ids never reused; a guard moves with its subject and
   is re-cut to its property, never re-pinned; every package ends with its report; new questions
   are `docs/open-questions/oq-<slug>.md` files and the index is regenerated, never hand-edited.
4. **Before starting a package**, record `python3 build/check_all.py` on your base; the WP-14.0
   baseline reds are in the report's §XI. A package may add no red that is absent from it.

### 0.1 What the synthesis said that the tree does not, found while freezing these contracts

Each of these was measured, and each changes a contract below.

| # | The synthesis said | The tree says (measured 24 Sep 2026 at `d565dea`) | Where it lands |
|---|---|---|---|
| 1 | VISION's layer words are eight: alphabet, grammar, vocabulary, bindings, solecisms, **phrases**, critic, generator | **Nine** (`VISION.md:196-224`): the sixth item is **the phrase layer**, not "phrases", and the ninth, **the interfaces**, was dropped | §B `layer-*` |
| 2 | `check_basis` has five callers whose stdout must stay identical | **Seven** call sites: `check_openings.py:275`, `check_windows.py:90`, `check_furniture.py:118`, **`check_threshold.py:110`**, `check_moves.py:97`, `check_critic_suspects.py:130`, and **`arrangement.py:890`**, which `check_all` runs as `arrangement.py selftest` (`check_all.py:149`) | §A.5, §J |
| 3 | `precedents/` records carry `sources` lists usable as a bibliography | **0 of 695** carry a `sources` key; they carry archival `refs`. The bibliography is `sources` in `styles/`, `faults/`, `rooms/`, `proportions/**`, `groupings/`, `partis/` | §A.5 rule 3 |
| 4 | A trim plate's bands equal the served members | True of `trim-classical` (71 and 71) and **not in general**: `pack_geometry` draws one face per stacked member and only the first of a side-by-side group, so over the 27 stackless packs it draws **235 faces for 237 members** — the two missing are `moorish-arch`'s `arch` and `alfiz` (`sums_check: false`) | §I.6 |
| 5 | `fmt.js` is "a faithful port" of `_fmt_in` | Faithful means two things the port will otherwise get wrong: Python's `round()` is **round-half-to-even** (`0.03125` in → `0"`; JavaScript's `Math.round` gives `0 1/16"`), and the sixteenth carry **does not carry into the foot** (`23.99` → `1'-12"`) | §I.8 |
| 6 | The Candidates step reads "composing k of N" | The `candidate` event (`workbench/server/jobs.py:128-133`) carries `n` in **arrival** order over every diagram scored and no total; N is not knowable from the stream | §G |
| 7 | The walk guards that move are listed at `walk.mjs:58-68`, `70-79`, … | Also **`walk.mjs:1463-1464`** — `rail present on every surface` reads `/the rail/i` from the assistant pane's whole text (`aside` `.last()`), which today matches the head "the rail" (`AiRail.jsx:135`) and, on a server with no key, the off-state copy too (`RailHost.jsx:18-19`); renaming the head and rewording that copy leaves it matching by accident or not at all | §J.1 |
| 8 | `search-unit.mjs:74-78` loses `kit` | That list has no `kit`; `KIND_ORDER` at `workbench/app/src/search/match.js:25-28` does | §J.1 |
| 9 | The palette's first option can be asserted by `data-id` | Palette options carry **no `data-id`** today (`CommandPalette.jsx:166`); WP-14.13 adds it | §I.12, §J.1 |
| 10 | "A Term is never nested in a button" | A `<button>` inside an `<a>` is invalid HTML too; rail items, section strips, map nodes and journey steps are anchors | §I.1 |
| 11 | The transcription rail item reads "or trace a drawing" | A rail label equals its surface record's `term` (navModel.test); a glossary term cannot begin "or" | §B, §F |
| 12 | The dossier's Plan types count comes from existing endpoints | `GET /api/groupings?style=` returns every grouping not marked absent for the style (`core.py:1414-1416`), not the groupings that *name* it; no endpoint returns those, so the dossier payload carries the lists | §H.4 |
| 13 | Every glossary `see[]` item and `surface.try` validates through `citations.validate` | Which rejects a section fragment — `citations.validate('style:craftsman#lineage')` is `(False, "unknown slot fragment 'lineage'")` — and knows no `term:` kind, until WP-14.3 lands, and WP-14.2 merges before WP-14.3 | §A.5 rule 7 |
| 14 | The four family batches share no file and author in parallel | They share no *file*, but cross-batch homonyms (`rank-variant`/`slot-variant`, `surface-workbench`/`plan-record`) would make each batch fail the checker alone; two records move batch | §B.0 |

---

## A. The glossary record

### A.1 Where records live

`glossary/<id>.json` at the repository root, one term per file, filename equal to `id` plus
`.json`. `glossary/README.md` carries the authoring rules (§A.6). The app writes no definition:
every tooltip, page head, rail description, palette line, plate key and edge caption reads a
record. **The set's version** is `"<schema version>+<content digest>"` (§C.1).

### A.2 The schema — `schema/glossary-term.schema.json`, version 0.1.0

Draft 2020-12, `additionalProperties: false`, a top-level `"version": "0.1.0"` key as
`schema/kit.schema.json` and `schema/fault.schema.json` carry theirs. The skeleton below is the
contract; WP-14.1 adds the `description` strings.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://traditional-design-language.org/schema/glossary-term.schema.json",
  "title": "Glossary term",
  "version": "0.1.0",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "term", "family", "definition", "kind"],
  "properties": {
    "id":         {"$ref": "#/$defs/id"},
    "term":       {"type": "string", "minLength": 1},
    "family":     {"enum": ["product", "surface", "section", "nav-group", "layer", "rank",
                            "edge", "carry", "binding", "variant-status", "param-kind",
                            "pack-kind", "severity", "judgment", "constraint-state",
                            "proportion", "pack-relation", "model", "fault", "house",
                            "figure"]},
    "definition": {"type": "string", "minLength": 1},
    "kind":       {"enum": ["sourced", "editorial"]},
    "sources":    {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
    "basis":      {"type": "string", "minLength": 25},
    "sense":      {"type": "string", "minLength": 1},
    "aka":        {"type": "array", "uniqueItems": true, "items": {"type": "string", "minLength": 1}},
    "order":      {"type": "integer", "minimum": 0},
    "analogy":    {"type": "string", "minLength": 1},
    "more":       {"type": "string", "minLength": 1},
    "binds":      {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/bind"}},
    "confusable_with": {"type": "array", "uniqueItems": true, "items": {"$ref": "#/$defs/id"}},
    "see":        {"type": "array", "uniqueItems": true, "items": {"type": "string", "minLength": 3}},
    "surface":    {"type": "object", "additionalProperties": false, "required": ["what"],
                   "properties": {
                     "what": {"type": "string", "minLength": 1},
                     "read": {"type": "array", "minItems": 1, "maxItems": 5,
                              "items": {"type": "string", "minLength": 1}},
                     "try":  {"type": "string", "minLength": 3}}},
    "readers":    {"type": "array", "minItems": 1,
                   "items": {"type": "object", "additionalProperties": false,
                             "required": ["who", "line"],
                             "properties": {"who": {"type": "string", "minLength": 1},
                                            "line": {"type": "string", "minLength": 1}}}},
    "is_not":     {"type": "array", "minItems": 1, "maxItems": 5,
                   "items": {"type": "string", "minLength": 1}}
  },
  "$defs": {
    "id":   {"type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"},
    "bind": {"type": "object", "additionalProperties": false,
             "required": ["field", "schema", "pointer", "value"],
             "properties": {
               "field":   {"enum": ["style.rank", "lineage.type", "kit.binding",
                                    "kit.variant_status", "kit.parameter_kind", "pack.kind",
                                    "fault.severity"]},
               "schema":  {"type": "string", "pattern": "^schema/[a-z-]+\\.schema\\.json$"},
               "pointer": {"type": "string", "pattern": "^/"},
               "value":   {"type": "string", "minLength": 1}}}
  },
  "allOf": [
    {"if": {"properties": {"kind": {"const": "sourced"}}, "required": ["kind"]},
     "then": {"required": ["sources"], "not": {"required": ["basis"]}}},
    {"if": {"properties": {"kind": {"const": "editorial"}}, "required": ["kind"]},
     "then": {"required": ["basis"], "not": {"required": ["sources"]}}}
  ]
}
```

### A.3 The fields

| Field | Req. | Type | What it is |
|---|---|---|---|
| `id` | yes | slug | One sense per id. Filename. Never reused (a wrong id is superseded, not renamed). |
| `term` | yes | string | The words the reader meets, as they appear on screen. A rail label, section label and page eyebrow ARE this string. |
| `family` | yes | enum (21) | The group the Glossary page lists it under. The enum is the synthesis's list, **unchanged**: no family was added or removed while freezing. |
| `definition` | yes | string | Plain, practitioner register, never agent-voiced, **at most 45 words** (the checker counts). No digits, no counts, no build history, no snake_case. |
| `kind` | yes | `sourced` or `editorial` | `sourced` requires `sources` and forbids `basis`; `editorial` the reverse. The glossary's own word "editorial" is shown in the popover as plain text and is never a `Term` (it is not a record; `param-kind-editorial` is a different word). |
| `sources` | if sourced | string[] | Each string must already appear verbatim in a corpus bibliography (§A.5 rule 3). |
| `basis` | if editorial | string | Names the file(s) it read and quotes at least one passage of **25 characters or more** verbatim (§A.5 rule 4). |
| `sense` | when colliding | string | Mandatory on both records whenever a `term` or `aka` collides case-insensitively with another record's. |
| `aka` | no | string[] | Other words for the same sense. Joins the homonym check and the search haystack. |
| `order` | see rule 5 | integer ≥ 0 | Order within the family. Required on every record that `binds`, equal to the bound value's index in its schema enum. |
| `analogy` | no | string | One sentence, where apt, at most 30 words. |
| `more` | no | string | A longer paragraph shown only on the term's own page (`#/glossary/<id>`), never in a popover. |
| `binds` | no | bind[] | Ties the word to a real schema enum member (§A.4). |
| `confusable_with` | when colliding | id[] | Symmetric. Required between colliding records; permitted between non-colliding ones in the same batch (§B.0). |
| `see` | no | cite[] | Citations in the grammar, validated (§A.5 rule 7). |
| `surface` | no | object | `{what, read[], try}` — **only** on families `surface` and `section`. `what` is the page head's line; `read[]` the "How to read this page" list; `try` one cite shown as a link. |
| `readers` | no | `{who, line}`[] | **Only on `about-tdl`.** |
| `is_not` | no | string[] | **Only on `about-tdl`**: VISION §X's "what this is not" in the reader's register. |

A served record may carry one key no file may: `reads` (§C.1), derived by the server.

### A.4 `binds` — the seven fields, their pointers and their complete enums

`build/check_glossary.py` holds this table as `FIELDS` and `workbench/app/src/glossary/fields.js`
holds the same seven keys; each is verified below by resolving the pointer in the named file.

| `field` | `schema` | `pointer` | Enum values (complete, in schema order) | Family | Id of the record binding value `v` |
|---|---|---|---|---|---|
| `style.rank` | `schema/style-node.schema.json` | `/properties/rank` | `tradition`, `family`, `style`, `variant` | `rank` | `rank-<v>` |
| `lineage.type` | `schema/style-node.schema.json` | `/properties/lineage/items/properties/type` | `descends_from`, `references`, `reacts_against`, `hybridizes_with`, `regional_of`, `revives` | `edge` | `edge-<v with _ as ->` |
| `kit.binding` | `schema/kit.schema.json` | `/properties/slots/additionalProperties/properties/binding` | `specified`, `extends`, `open`, `forbidden` | `binding` | `binding-<v>` |
| `kit.variant_status` | `schema/kit.schema.json` | `/properties/slots/additionalProperties/properties/variants/items/properties/status` | `canonical`, `permitted`, `atypical`, `forbidden` | `variant-status` | `variant-status-<v>` |
| `kit.parameter_kind` | `schema/kit.schema.json` | `/$defs/parameter/properties/kind` | `measured`, `derived`, `editorial`, `invented`, `code` | `param-kind` | `param-kind-<v>` |
| `pack.kind` | `schema/proportion-pack.schema.json` | `/properties/kind` | `order-system`, `module-system`, `facade-system`, `room-system`, `trim-system`, `opening-system` | `pack-kind` | `pack-kind-<v>` |
| `fault.severity` | `schema/fault.schema.json` | `/properties/severity` | `fatal`, `serious`, `minor` | `severity` | `severity-<v>` |

`member_of` is **not** a value of `lineage.type` (it is its own field,
`schema/style-node.schema.json` `/properties/member_of`), so `member-of` is an unbound record in
family `edge`.

### A.5 The checker — `build/check_glossary.py`

Structured like `build/check_faults.py`. Exit **0** pass, **1** any error, **3** could not
evaluate — never 0 when it could not. Registered in `build/check_all.py` directly after
`("check_faults.py", [])` (`check_all.py:101`), which moves `TOTAL_CHECKS` **53 → 54**
(`check_all.py:243`); `build/check_costs.json` is not edited, so the new unit takes
`DEFAULT_COST` (`check_all.py:264`). The rules, in order:

1. **Could not evaluate.** `import jsonschema` fails, or `workbench.server.citations` cannot be
   imported (it imports without fastapi — verified by importing it with `fastapi` blocked), or
   `build/schema_validators.py` cannot compile the schema → print why, exit 3.
2. **Shape.** Every `glossary/*.json` validates through `schema_validators.compiled` /
   `raise_first`; filename equals `id`; an absent or empty `glossary/` is an error.
3. **Sourced.** Every `sources[]` string equals, character for character, an item of a `sources`
   list in some record under `styles/`, `faults/`, `rooms/`, `proportions/**/`, `groupings/` or
   `partis/` (all lists of strings — verified; `precedents/` carries no `sources` key, 0 of 695,
   and is not a bibliography). This is the no-invented-source guard.
4. **Editorial.** `check_openings.check_basis(rep, record, source="glossary/<id>.json",
   rec_re=check_openings.GLOSSARY_REC_RE)` passes, and at least **one** quotation of 25+
   characters was verified (`check_basis` returns that count; `_QUOTE_RE` at
   `check_openings.py:118` only sees quotes of 25 or more). A basis that names
   `docs/open-questions.md` (generated) or any `glossary/` file is an error. A key path the
   checker cannot walk is an **error** here, not an unjudged count: the glossary has no backlog,
   so the ceiling is zero.
5. **Binds.** For every bind: `field` is a `FIELDS` key; `schema` and `pointer` equal that row;
   the pointer resolves to an object with an `enum`; `value` is in it; the record's `family` is
   the row's family; its `id` is `<family>-<value with "_" replaced by "-">`; its `order` is the
   value's index in the enum; each `(field, value)` is bound by exactly one record.
   **Family completeness**: if any value of a field is bound, every value of its enum is bound,
   and each missing value is printed as an error, never a warning.
6. **Homonyms.** Compare, case-insensitively and trimmed, the set `{term} ∪ aka` of every record
   against every other's. A collision requires `sense` on both and each naming the other in
   `confusable_with`. `confusable_with` is symmetric everywhere it appears; every id it names
   exists; no record names itself.
7. **Cites.** Every `see[]` item and `surface.try` is parsed with `citations.REF_RE` (no new
   regex). `term:<id>` must name a glossary record **in the set being checked** (the checker is
   the authority on its own ids, so this does not wait for WP-14.3's `term` kind);
   `brief:<id>` must name `briefs/<id>.json` (`citations.validate` accepts any brief id —
   verified); every other kind must return `(True, None)` from `citations.validate(ref)`.
   **In tranche 1 no glossary record cites a dossier-section fragment** (`style:<id>#<section>`):
   the server accepts one only from WP-14.3, which merges after WP-14.2.
8. **Hygiene** over `term`, `sense`, `aka[]`, `definition`, `analogy`, `more`, `surface.what`,
   `surface.read[]`, `readers[].who`, `readers[].line`, `is_not[]`: no match of `WP-\d`,
   `\bOQ\s*\d`, `(^|\s)--[a-z]`, a snake_case token `\b[a-z0-9]+_[a-z0-9_]+\b`, or **any digit**.
9. **Required records and placement.** `about-tdl`, `judgment-passed`, `judgment-failed`,
   `judgment-unjudged` and `judgment-not-applicable` exist and have distinct terms. `readers` and
   `is_not` appear only on `about-tdl`; `about-tdl` carries no `see`, `confusable_with`, `binds`
   or `surface` (it is served ungated, §C.3, and must resolve no other record). `surface` appears
   only in families `surface` and `section`.
10. **Lengths.** `definition` ≤ 45 words; `analogy`, `surface.what`, each `surface.read[]` and
    each `is_not[]` ≤ 30 words; each `readers[].line` ≤ 45 words (words split on whitespace).
11. **Naming.** Families `surface`, `section`, `nav-group`, `layer` and `judgment` require the id
    prefix `<family>-`, and an id carrying one of those prefixes must be in that family.

`build/check_openings.py` changes, in WP-14.1 only:

- `check_basis(rep, rule, source="openings/grammar.json", rec_re=None)` (today
  `check_openings.py:160`) returns the number of quotations it verified in full. With
  `rec_re=None` it uses `_REC_RE` exactly as today, so **the stdout of all seven callers —
  `check_openings.py`, `check_windows.py`, `check_furniture.py`, `check_threshold.py`,
  `check_moves.py`, `check_critic_suspects.py` and `arrangement.py selftest` — is byte-identical
  before and after**, and WP-14.1's verification diffs all seven. The key-path reader `_KEYPATH_RE` is not widened.
- New module constant, the one spelling of which files a glossary basis may name:

```python
GLOSSARY_REC_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])("
    r"(?:rooms|kits|styles|faults|groupings|proportions|partis)/[A-Za-z0-9_.\-/]+\.json"
    r"|build/[A-Za-z0-9_]+\.py"
    r"|massings/catalog\.json|elements/slots\.json|mcp_server/core\.py"
    r"|schema/[A-Za-z0-9_.\-]+\.json"
    r"|VISION\.md|README\.md|docs/[A-Za-z0-9_.\-]+\.md)")
```

The lookbehind keeps `workbench/README.md` from being read as the root `README.md`; `docs/` is
top level only, so `docs/reports/…` and `docs/open-questions/…` are never admitted.

### A.6 `glossary/README.md` — the authoring rules

Plain practitioner register; at most 45 words; never agent-voiced (`core.overview().the_model`,
`core.py:142-166`, is rewritten for people and survives only as a basis quote); the basis quotes
its file verbatim at 25+ characters; `sourced` only where the string already sits in a corpus
bibliography; homonyms paired; no counts, no digits, no colours, no build history; app strings
being retired (SourceChip glosses, `EdgeGlyph` verbs, `KIND_LABEL`, `Chrome.surfaces()` metas,
Overview `DOORS`, `staticEntries` short lines) are wording seeds only and never a basis.

---

## B. The tranche-1 term list — 121 ids

### B.0 Batches, seeds and merging

- **Seeds (WP-14.1)**: `about-tdl`, `judgment-passed`, `judgment-failed`, `judgment-unjudged`,
  `judgment-not-applicable`. No WP-14.2 batch creates these five files.
- **WP-14.2 batches**: A (product, surface, section, nav-group, layer), B (rank, edge, member-of,
  carry, binding, variant-status, param-kind), C (proportion, pack-relation, pack-kind, figure),
  D (judgment, constraint-state, severity, fault and exception, model, house). **Two records move
  batch, against their family, so that every pair of records whose terms collide is authored in
  one batch**: `slot-variant` (family `model`) is authored by **B** beside `rank-variant`, and
  `plan-record` (family `house`) by **A** beside `surface-workbench` and `section-plans`.
- **Each batch must pass `check_glossary` alone** on top of the seeds, after rebasing onto the
  integration branch at or after WP-14.1's merge. So `confusable_with` is declared only between
  records of one batch; conceptual partners in different batches that do not collide as strings
  (`member`/`member-of`/`section-members`; `derived-rule`/`constraint`/`section-rules`) are
  **not** declared in tranche 1; and a `term:` cite may name only an id in its own batch or a
  seed.
- `order`: required on bound records (rule 5); recommended elsewhere — `section-*` in
  `DOSSIER_SECTIONS` order, `surface-*` in navModel order, `judgment-*` as listed below.

In the tables, *binds* gives `field = value`; *conf.* is `confusable_with`. A blank sense means
none is required. `term` is the exact string the screen shows.

### B.1 Seeds — WP-14.1

| id | term | family | notes |
|---|---|---|---|
| `about-tdl` | Traditional Design Language | product | `readers[]` three lines, from `VISION.md:343` (the production builder), `:349` (the plan-development lead), `:354` (the architect and the classicist). **No line for `:359`** (the people who live there). `is_not[]` from `VISION.md:371-386` (§X). Basis quotes `VISION.md`. Served ungated. |
| `judgment-passed` | passed | judgment | order 0 |
| `judgment-failed` | failed | judgment | order 1 |
| `judgment-unjudged` | unjudged | judgment | aka `could not evaluate`; order 2 |
| `judgment-not-applicable` | not applicable | judgment | order 3 |

### B.2 Batch A — 37 records

| id | term | family | sense | conf. | notes |
|---|---|---|---|---|---|
| `guided-example` | the guided example | product | | | `see: ["style:tidewater-georgian", "brief:family-georgian"]` — read by navModel, the front door and the dossier banner; no JSX names a style id for it |
| `assistant` | Ask the corpus · AI assistant | product | | | aka `the rail`. The pane head and the folded spine read `term` (§I.11) |
| `surface-overview` | Front door | surface | | | |
| `surface-style` | Find a style | surface | | | |
| `surface-phylogeny` | Family tree & map | surface | | | |
| `surface-proportions` | Proportions | surface | the library of every proportion pack | `section-proportions` | |
| `surface-faults` | Faults | surface | the library of every named error | `section-faults` | |
| `surface-glossary` | Glossary | surface | | | |
| `surface-brief` | Brief | surface | | | |
| `surface-candidates` | Candidates | surface | | | |
| `surface-workbench` | Plan | surface | step three: the house on the bench | `plan-record`, `section-plans` | aka `the bench` |
| `surface-drawings` | Drawings | surface | | | |
| `surface-export` | Export | surface | | | |
| `surface-transcription` | Trace a drawing | surface | | | the rail nests it under step three with no connective (§F) |
| `section-identify` | Identify | section | | | order 0 |
| `section-members` | Filed under this | section | | | order 1 |
| `section-lineage` | Lineage | section | | | order 2 |
| `section-kit` | Kit | section | | | order 3; its definition says what a kit is — there is no separate `kit` record |
| `section-proportions` | Proportions | section | the packs that reach this style | `surface-proportions` | order 4 |
| `section-plans` | Plan types | section | | `surface-workbench`, `plan-record` | order 5 |
| `section-rules` | Constraints | section | | | order 6 |
| `section-faults` | Faults | section | the named errors filed for this style | `surface-faults` | order 7 |
| `section-evidence` | Evidence | section | | | order 8 |
| `nav-group-start` | Start | nav-group | | | |
| `nav-group-styles` | Styles | nav-group | | | |
| `nav-group-a-house` | A house | nav-group | | | |
| `nav-group-library` | Library | nav-group | | | |
| `layer-alphabet` | The alphabet | layer | | | `VISION.md:199` |
| `layer-grammar` | The grammar | layer | | | `:205` |
| `layer-vocabulary` | The vocabulary | layer | | | `:210` |
| `layer-bindings` | The bindings | layer | | | `:212` |
| `layer-solecisms` | The solecisms | layer | | | `:216` |
| `layer-phrase` | The phrase layer | layer | | | `:217` |
| `layer-critic` | The critic | layer | | | `:220` |
| `layer-generator` | The generator | layer | | | `:222` |
| `layer-interfaces` | The interfaces | layer | | | `:223` — the one the synthesis dropped |
| `plan-record` | plan | house | the record of one house | `surface-workbench`, `section-plans` | authored by A (§B.0) |

The nine `layer-*` records are seeded last and may slip to a later commit of WP-14.2 without
blocking anything: the Glossary lists them first as a group, and nothing else reads a `layer-*`
id. (The line numbers in the notes column are the list items' first lines in `VISION.md` at
`d565dea`, given only to find them.)

### B.3 Batch B — 28 records

| id | term | family | binds | sense | conf. |
|---|---|---|---|---|---|
| `rank-tradition` | tradition | rank | `style.rank = tradition` | | |
| `rank-family` | family | rank | `style.rank = family` | | |
| `rank-style` | style | rank | `style.rank = style` | | |
| `rank-variant` | variant | rank | `style.rank = variant` | the finest rank, where a kit is buildable | `slot-variant` |
| `edge-descends-from` | descends from | edge | `lineage.type = descends_from` | | |
| `edge-references` | references | edge | `lineage.type = references` | | |
| `edge-reacts-against` | reacts against | edge | `lineage.type = reacts_against` | | |
| `edge-hybridizes-with` | hybridizes with | edge | `lineage.type = hybridizes_with` | | |
| `edge-regional-of` | regional of | edge | `lineage.type = regional_of` | | |
| `edge-revives` | revives | edge | `lineage.type = revives` | | |
| `member-of` | filed under | edge | — | | aka `member of` |
| `carries-the-kit` | carries the kit | carry | — | | |
| `carries-named-slots` | carries named slots only | carry | — | | |
| `carries-nothing` | carries nothing | carry | — | | |
| `binding-specified` | specified | binding | `kit.binding = specified` | | |
| `binding-extends` | extends | binding | `kit.binding = extends` | | |
| `binding-open` | open | binding | `kit.binding = open` | | |
| `binding-forbidden` | forbidden | binding | `kit.binding = forbidden` | a slot the style prohibits outright | `variant-status-forbidden` |
| `variant-status-canonical` | canonical | variant-status | `kit.variant_status = canonical` | | |
| `variant-status-permitted` | permitted | variant-status | `kit.variant_status = permitted` | | |
| `variant-status-atypical` | atypical | variant-status | `kit.variant_status = atypical` | | |
| `variant-status-forbidden` | forbidden | variant-status | `kit.variant_status = forbidden` | a variant the style rules out | `binding-forbidden` |
| `param-kind-measured` | measured | param-kind | `kit.parameter_kind = measured` | | |
| `param-kind-derived` | derived | param-kind | `kit.parameter_kind = derived` | | |
| `param-kind-editorial` | editorial | param-kind | `kit.parameter_kind = editorial` | | |
| `param-kind-invented` | invented | param-kind | `kit.parameter_kind = invented` | | |
| `param-kind-code` | code | param-kind | `kit.parameter_kind = code` | | |
| `slot-variant` | variant | model | — | one option a slot may take | `rank-variant` |

The carry words are what `EdgeGlyph` prints (§I.13); 42 `hybridizes_with` edges carry the kit
and 2 of those carry named slots only — measured 24 Sep 2026 at `d565dea`
(`monterey-colonial → new-england-colonial`, `octagon-house → italianate-american`).

### B.4 Batch C — 24 records

| id | term | family | binds | notes |
|---|---|---|---|---|
| `proportion-pack` | proportion pack | proportion | — | aka `pack` |
| `module` | module | proportion | — | basis may quote `proportions/systems/trim-classical.json` `module.name` |
| `part` | part | proportion | — | |
| `assembly` | assembly | proportion | — | |
| `member` | member | proportion | — | a moulding member; no string collision with `member of`, so no sense required |
| `invariant` | invariant | proportion | — | |
| `derived-rule` | derived rule | proportion | — | aka `rule` |
| `pack-conflict` | conflict with building today | proportion | — | |
| `authority` | authority | proportion | — | |
| `your-building` | at your building | proportion | — | |
| `wall-plane` | wall plane | proportion | — | basis may quote the casing member notes of `trim-classical` |
| `pack-own` | bound by this style | pack-relation | — | |
| `pack-opted-in` | opted in | pack-relation | — | |
| `pack-delivered` | delivered | pack-relation | — | |
| `pack-withheld` | withheld | pack-relation | — | |
| `pack-declined` | declined | pack-relation | — | |
| `pack-kind-order-system` | classical order | pack-kind | `pack.kind = order-system` | order 0 |
| `pack-kind-module-system` | material module | pack-kind | `pack.kind = module-system` | order 1 |
| `pack-kind-facade-system` | facade system | pack-kind | `pack.kind = facade-system` | order 2 |
| `pack-kind-room-system` | room system | pack-kind | `pack.kind = room-system` | order 3 |
| `pack-kind-trim-system` | trim family | pack-kind | `pack.kind = trim-system` | order 4 |
| `pack-kind-opening-system` | opening system | pack-kind | `pack.kind = opening-system` | order 5 |
| `figure-drawn-from-record` | drawn from the record | figure | — | the plate's foot line |
| `figure-drawn-upright` | drawn upright | figure | — | the plate's foot line; `oq/casings-are-measured-across-and-drawn-upright` |

### B.5 Batch D — 27 records

| id | term | family | binds | sense | conf. |
|---|---|---|---|---|---|
| `judgment-yours-to-judge` | yours to judge | judgment | — (order 4) | | |
| `judgment-refused` | refused | judgment | — (order 5) | a placement the corpus will not draw | `exception-refused` |
| `constraint-executable` | executable | constraint-state | — | | |
| `constraint-no-test-yet` | no test yet | constraint-state | — | | |
| `severity-fatal` | fatal | severity | `fault.severity = fatal` | | |
| `severity-serious` | serious | severity | `fault.severity = serious` | | |
| `severity-minor` | minor | severity | `fault.severity = minor` | | |
| `fault` | fault | fault | — | | |
| `exception` | exception | fault | — | | |
| `exception-granted` | granted | fault | — | | |
| `exception-refused` | refused | fault | — | an exception whose condition this style does not meet | `judgment-refused` |
| `slot` | slot | model | — | | |
| `slot-group` | slot group | model | — | | |
| `cascade` | cascade | model | — | | |
| `cascade-source` | source | model | — | the ancestor a kit value came from | `bibliographic-source` |
| `bibliographic-source` | source | model | — | a published work the corpus cites | `cascade-source` |
| `thin-kit` | thin kit | model | — | | |
| `diagnostic-tell` | diagnostic tell | model | — | | |
| `exemplar` | exemplar | model | — | | |
| `taxon` | taxon | model | — | | |
| `constraint` | constraint | model | — | | |
| `binding` | binding | model | — | | |
| `rank` | rank | model | — | | |
| `parti` | parti | house | — | | |
| `massing` | massing | house | — | | |
| `grouping` | grouping | house | — | | |
| `on-the-bench` | On the bench | house | — | | |

Aka on batch D: `fault` → `solecism`, `named error`; `slot` → `element slot`.

The three exception verdicts `core.grant_exception` returns — `granted`, `refused`, `unjudged`
(`core.py:688-768`) — map to `exception-granted`, `exception-refused` and `judgment-unjudged`.
The three constraint states map as §I.9 says.

### B.6 The collisions the checker will see, complete

| Colliding string | Records | Same batch |
|---|---|---|
| proportions | `surface-proportions`, `section-proportions` | A |
| faults | `surface-faults`, `section-faults` | A |
| plan | `surface-workbench`, `plan-record` | A |
| variant | `rank-variant`, `slot-variant` | B |
| forbidden | `binding-forbidden`, `variant-status-forbidden` | B |
| source | `cascade-source`, `bibliographic-source` | D |
| refused | `judgment-refused`, `exception-refused` | D |

Any other collision a batch introduces is a defect in that batch. Count by family: product 3,
surface 12, section 9, nav-group 4, layer 9, rank 4, edge 7, carry 3, binding 4,
variant-status 4, param-kind 5, pack-kind 6, severity 3, judgment 6, constraint-state 2,
proportion 11, pack-relation 5, model 13, fault 4, house 5, figure 2 — **121**.

---

## C. The glossary API

### C.1 `GET /api/glossary`

Built by `workbench/server/corpus.py::glossary_payload()` from `core._data()["glossary"]`
(WP-14.3 loads `glossary/*.json` there, keyed by id, exactly as `faults/` is loaded at
`core.py:38-40`). Cached in a module global `_GLOSSARY_PAYLOAD`, cleared by
`reset_glossary_payload()`, which `corpus.invalidate()` (`corpus.py:924-956`) calls beside
`reset_search_index()`.

```json
{
  "version": "0.1.0+<digest>",
  "schema_version": "0.1.0",
  "digest": "<16 hex characters>",
  "count": "<len(terms)>",
  "terms": [ { "...the record as authored...": "", "reads": ["VISION.md"] } ],
  "by_family": { "product": ["about-tdl", "guided-example", "assistant"], "...": [] },
  "by_field": { "kit.binding": { "specified": "binding-specified", "extends": "binding-extends",
                                 "open": "binding-open", "forbidden": "binding-forbidden" },
                "...": {} }
}
```

| Key | Exact rule |
|---|---|
| `schema_version` | the schema file's `version` |
| `digest` | the first 16 hex characters of SHA-256 over `json.dumps([records sorted by id], sort_keys=True, separators=(",", ":"), ensure_ascii=False)`, the records as authored (no `reads`) |
| `version` | `schema_version + "+" + digest` |
| `count` | `len(terms)` |
| `terms` | every record, sorted by (index of `family` in the schema enum, `order` if present else +∞, `id`), each with one added key `reads`: the files `check_openings.GLOSSARY_REC_RE` finds in `basis` (in order of first appearance, de-duplicated), `[]` for a sourced record. `reads` is the popover's provenance line; the app does not parse a basis |
| `by_family` | every family in the schema enum is a key, in enum order; each value lists that family's ids in `terms` order; `[]` where none |
| `by_field` | all seven `FIELDS` keys; each maps every bound value to its record id; `{}` where the field is unbound |

### C.2 `GET /api/glossary/{term_id}`

Through `_ok()` (`app.py:207-212`), so a miss is HTTP 404 with FastAPI's `detail` wrapper:

```json
{"version": "0.1.0+…",
 "term": { "…the record…": "", "reads": [] },
 "confusable": [ {"id": "slot-variant", "term": "variant", "sense": "one option a slot may take"} ],
 "see": [ {"cite": "style:tidewater-georgian", "name": "Tidewater Georgian"},
          {"cite": "brief:family-georgian", "name": null} ]}
```

```json
{"detail": {"error": "no glossary term 'nosuch'", "did_you_mean": []}}
```

`confusable` resolves `confusable_with` in declared order; `see` resolves each cite's `name` from
`corpus.search_index()` by `cite`, `null` where the kind is not indexed. `did_you_mean` is
`[k for k in glossary if term_id.lower() in k][:8]`, the rule `core.get_fault` uses
(`core.py:889-890`).

### C.3 Gating — exactly one path opens

Both routes are gated like every `/api/` route (`app.py:109`). **`auth.OPEN_PATHS`
(`auth.py:38`, today `("/api/health", "/api/login")`) gains exactly `"/api/glossary/about-tdl"`**
and nothing else; the gate compares whole paths, so no other term, no trailing-slash form and not
`/api/glossary` becomes public. `about-tdl` resolves no other record (§A.5 rule 9), so the
ungated body carries only `VISION.md`'s own words. The Gate (`Gate.jsx`) fetches it with
`api.glossaryTerm('about-tdl')` and shows `term.definition` and nothing else; if the fetch fails it
shows nothing. `app.py`'s module docstring paragraph "WHAT THE UNGATED SURFACE CARRIES"
(`app.py:15-23`) gains the sentence saying so, in the same commit.

### C.4 What stays byte-identical

| Surface | Held by |
|---|---|
| `core.overview()` — no `glossary` key, no glossary count, `what_this_is` (`core.py:124-127`) and `how_to_use_it` unchanged | `test_glossary_routes.py`: `"glossary" not in core.overview()` and not in its `counts` |
| Every MCP tool payload, including `tdl_get_proportions` (still `assemblies: []` for `trim-classical`) | `test_mcp_http.py` unchanged; `test_pack_plates.py` asserts the MCP half |
| `workbench/server/rail.py` — the file, its `SYSTEM` kind list and `CITE_RE` | a byte comparison in WP-14.3's and WP-14.13's verification |
| `GET /api/health` — its keys and its `counts == core.overview()["counts"]` | `test_glossary_routes.py` |
| `auth.OPEN_PATHS` beyond the one ruled path | `test_zz_auth_leak_guard.py` extension (§J.1) |

### C.5 The search index gains terms

`corpus.search_index()` (`corpus.py:190-295`) appends, for every record whose family is **not**
`surface`, `section` or `nav-group`:

```python
{"cite": "term:" + t["id"], "kind": "term", "id": t["id"],
 "name": t["term"] + (" (" + t["sense"] + ")" if t.get("sense") else ""),
 "meta": t["family"],
 "hay": _hay(t["term"], t["id"], t.get("aka"), t.get("sense")),
 "short": t["definition"]}
```

The haystack never includes the definition; `short` carries it for display only.
`citations._known_ids("term")` returns `core._data()["glossary"]`. The palette's `KIND_ORDER`
(`match.js:25-28`) becomes `surface, action, style, slot, pack, fault, term, room, massing, parti,
grouping` (`kit` dropped — no index or static entry carries that kind at `d565dea`; the Kit's
palette entry is kinded `surface`) and `KIND_LABEL.term = 'glossary'` (`CommandPalette.jsx:18-22`).
**That app half is WP-14.13's** (with `search-unit.mjs`, §J.1). Between 14.3 and 14.13 the served
`term` entries rank after every listed kind under the group label `term`, because `kindRank` returns
`KIND_ORDER.length` for an unlisted kind (`match.js:30-33`) and the group header falls back to the
kind name (`CommandPalette.jsx:161-162`) — visible and harmless, and no package fills the gap early. The index count
(666, measured 24 Sep 2026 at `d565dea`) moves by the indexed terms; `CLAUDE.md:743` moves by
`check_counts.py --fix`, never by hand.

---

## D. `DOSSIER_SECTIONS`

### D.1 The vocabulary

Spelled in exactly two places, pinned together by `test_grammar_agreement.py`: in
`workbench/app/src/citations.js`, on one line, exactly

```js
export const DOSSIER_SECTIONS = Object.freeze(['identify', 'members', 'lineage', 'kit', 'proportions', 'plans', 'rules', 'faults', 'evidence']);
```

and in `workbench/server/citations.py` as the tuple `DOSSIER_SECTIONS` with the same nine strings
in the same order.

| # | URL id | Label (`term` of) | What it shows |
|---|---|---|---|
| 0 | `identify` | `section-identify` "Identify" | description, diagnostic tells, distinguished-from as links; one summary card per other listed section with its count |
| 1 | `members` | `section-members` "Filed under this" | `member_of` inverted; for tradition and family ranks, the buildable descendants |
| 2 | `lineage` | `section-lineage` "Lineage" | edges from `/api/phylogeny` (`from` or `to` this id), descendants as links, the cascade ladder |
| 3 | `kit` | `section-kit` "Kit" | the embedded kit; a slot opens `#/style/<id>/kit/<slot>` |
| 4 | `proportions` | `section-proportions` "Proportions" | packs by provenance from `/api/styles/{id}/packs` (§H.3), each a link to `#/proportions/<pack>?style=<id>` |
| 5 | `plans` | `section-plans` "Plan types" | massing affinities, native partis and naming groupings — a list only |
| 6 | `rules` | `section-rules` "Constraints" | each constraint in one of three states (§I.9); `?constraint=` highlighted |
| 7 | `faults` | `section-faults` "Faults" | verdict-for-this-style first, then lineage, then a count of universal faults linking to `#/faults?style=<id>` |
| 8 | `evidence` | `section-evidence` "Evidence" | exemplars, sources, image records with their status |

No slot id equals a section id — 97 slots, 0 collisions, measured 24 Sep 2026 at `d565dea`
(`elements/slots.json`, ontology 0.7.0). That disjointness is what lets `style:<id>#<fragment>`
mean a section or a slot without ambiguity, and WP-14.3 pins it as a test.

### D.2 Counts, and the omission rule

**A section is listed only when its count is greater than zero; `identify` is always listed and
has no count (`null`).** Rank-awareness is this rule over the counts below plus one rank rule for
faults; no other rank table exists.

| Section | Count, computed by `corpus.style_dossier` |
|---|---|
| `members` | nodes whose `member_of` is this id |
| `lineage` | `len(node.lineage)` + edges in any node's `lineage` whose `target` is this id (= `len(get_style(id, ["lineage"]).lineage) + len(…descendants)`) |
| `kit` | `core.resolve_kit(id)["slots_returned"]` at its defaults (`only_specified=True`) — the figure `/api/kit/{id}` returns |
| `proportions` | the sum of the five list lengths of `/api/styles/{id}/packs` (delivered counted by pack, not by group) |
| `plans` | `len(node.massing_affinities)` + `core.list_partis(style=id)["count"]` + groupings with a `style_variation` entry whose `style` is this id and whose `present` is not `false` |
| `rules` | `len(node.constraints)` |
| `faults` | at rank `style` or `variant`: `core.find_faults(style=id, limit=300)["matches"]`; at rank `tradition` or `family`: `len(verdict_here) + len(lineage)` only — a universal fault is about a house, and a tradition or family is not built |
| `evidence` | `len(exemplars) + len(sources) + core.find_assets(style=id)["matches"]` |

Measured 24 Sep 2026 at `d565dea`, the nodes at each rank with each section listed:

| Rank (nodes) | identify | members | lineage | kit | proportions | plans | rules | faults | evidence |
|---|---|---|---|---|---|---|---|---|---|
| tradition (5) | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| family (27) | 27 | 27 | 0 | 27 | 0 | 0 | 0 | 8 | 27 |
| style (90) | 90 | 18 | 90 | 90 | 90 | 90 | 90 | 90 | 90 |
| variant (42) | 42 | 0 | 42 | 42 | 42 | 42 | 42 | 42 | 42 |

So `#/style/north-american` lists identify, filed under this and evidence, and omits rules and
faults, by data rather than by a special case.

---

## E. Routes and citations

The grammar stays spelled in exactly three places — `REF_RE` (`citations.py:29`), `CITE_RE`
(`rail.py:186`), `parseCite` (`citations.js:21-27`) — and **no regex changes**. `ID_CHARS` and
`FRAG_CHARS` stay byte-identical. Only `SURFACE_PATHS`, `SELECTION_KEYS`, `routeCite`, `citeFor`
and `validate`'s fragment rule move.

### E.1 `SURFACE_PATHS` (`router.js:20-33`)

| Surface | Path | Path keys today | After WP-14.5 | After WP-14.12 |
|---|---|---|---|---|
| `overview` | (empty) | — | — | — |
| `phylogeny` | `phylogeny` | `style` | `style` | `style` |
| `style` | `style` | `style` | `style`, `section`, `slot` | `style`, `section`, `slot` |
| `kit` | `kit` | `style`, `slot` | unchanged | **removed** — `LEGACY_PATHS.kit` |
| `faults` | `faults` | `fault` | `fault` | `fault` |
| `proportions` | `proportions` | `pack` | `pack` | `pack` |
| `glossary` | `glossary` | — | **new**: `term` | `term` |
| `candidates` | `candidates` | `candidate` | `candidate` | `candidate` |
| `workbench`, `brief`, `drawings`, `export`, `transcription` | own names | — | — | — |

`SELECTION_KEYS` (`router.js:46-49`) gains `'section'` and `'term'`, appended in that order after
`'asset'`, so `formatHash`'s query order for every existing key is unchanged. `NUMERIC_KEYS` is
unchanged. Between WP-14.5's and WP-14.8's merges, `#/glossary` has a route and no surface, and
`App.jsx:158` renders the bench for it; nothing links there before WP-14.8.

**WP-14.12's legacy table.** `router.js` exports

```js
export const LEGACY_PATHS = Object.freeze({ kit: { keys: ['style', 'slot'], to: 'style', section: 'kit' } });
export function isLegacyHash(hash) { /* true when the first path segment is a LEGACY_PATHS key */ }
```

`parseHash` reads `#/kit/<style>/<slot>` positionally with the same `-` placeholder, returns
surface `style`, and sets `section: 'kit'` **only when a style or a slot is present**:

| Legacy hash | Parses to | Canonical |
|---|---|---|
| `#/kit/craftsman/cornice` | `style` `{style, section:'kit', slot}` | `#/style/craftsman/kit/cornice` |
| `#/kit/craftsman` | `style` `{style, section:'kit'}` | `#/style/craftsman/kit` |
| `#/kit/-/cornice` | `style` `{section:'kit', slot}` | `#/style/-/kit/cornice` |
| `#/kit` | `style` `{}` | `#/style` — the index |

`nav.canonicalize` (`nav.js:32-40`) rewrites a legacy hash with `history.replaceState` exactly as
it rewrites `#/cite/` today: when `isLegacyHash(location.hash)`, it replaces with
`formatHash(state.surface, state.selection, state.params)`, so a refresh keeps the new address.

### E.2 The places

| Place | Address |
|---|---|
| Styles index | `#/style` (also `#/style/-` and any section with no style and no slot) |
| Dossier, identify | `#/style/<id>` — **a writer never emits `#/style/<id>/identify`**; a reader treats that form and the bare one alike |
| Dossier section | `#/style/<id>/<section>` |
| A slot in a style's kit | `#/style/<id>/kit/<slot>` |
| One slot across styles (interim, on the existing `GET /api/slots/{id}`) | `#/style/-/kit/<slot>` |
| A constraint | `#/style/<style>/rules?constraint=<style>.<suffix>` |
| Glossary / a term | `#/glossary` · `#/glossary/<term>` |
| Pack index / a pack | `#/proportions` (no default pack) · `#/proportions/<pack>` |

`slot` is honoured only when `section` is `kit`. `StyleDossier` decides from the selection in this
order: a style present → the dossier (section absent means `identify`); no style, `section` `kit`
and a slot present → the slot panel; anything else → the Styles index.

### E.3 `routeCite` and `citeFor` (`citations.js:30-53`, `63-89`)

| Citation | At WP-14.5 → `{surface, selection}` | Final (WP-14.12) | `citeFor` returns |
|---|---|---|---|
| `style:<id>` | `style` `{style}` | same | `style:<id>` |
| `style:<id>#identify` | `style` `{style}` — **alias**, no section key | same | `style:<id>` |
| `style:<id>#<section>`, section ∉ {identify, kit} | `style` `{style, section}` | same | `style:<id>#<section>` |
| `style:<id>#kit` | `style` `{style, section:'kit'}` (an identity at 14.5) | same selection — **alias** | 14.5: `style:<id>#kit`; final: `kit:<id>` |
| `style:<id>#<slot>` | `style` `{style}` (fragment dropped, as today) | `style` `{style, section:'kit', slot}` — **alias** | final: `kit:<id>#<slot>` |
| `kit:<id>` / `kit:<id>#<slot>` | `kit` `{style, slot}` (unchanged) | `style` `{style, section:'kit', slot}` | `kit:<id>[#<slot>]` |
| `slot:<id>` | `kit` `{slot}` (unchanged) | `style` `{section:'kit', slot}` | `slot:<id>` |
| `constraint:<style>.<suffix>` | `style` `{style: text before the last '.', section:'rules', constraint}`; `null` if the id has no dot | same | `constraint:<id>` |
| `term:<id>` | `glossary` `{term}` | same | `term:<id>` |
| every other kind | unchanged | unchanged | unchanged |

The constraint rule is exact over the corpus: 660 of 660 constraint ids are
`<style id>.<suffix>`, measured 24 Sep 2026 at `d565dea`. Today it routes to the bench, which
reads nothing (`citations.js:44`).

**`citeFor('style', s)`, in this order** — final form; WP-14.5 has every branch but the second:

1. `s.constraint` → `constraint:<s.constraint>`
2. `s.section === 'kit'` → `s.style ? 'kit:' + s.style + (s.slot ? '#' + s.slot : '') : (s.slot ? 'slot:' + s.slot : null)`
3. no `s.style` → `null`
4. `s.section` present and not `identify` → `style:<s.style>#<s.section>`
5. otherwise → `style:<s.style>`

`citeFor('glossary', s)` → `s.term ? 'term:' + s.term : null`. **`style:<id>#identify` is never
minted.** Aliases are asserted in `router-unit.mjs` as aliases and are never added to its `KINDS`
identity list; `style:craftsman#lineage` and `term:judgment-unjudged` join `KINDS`.

### E.4 The query keys each surface honours

| Surface | Path keys | Selection keys read from the query | Params (filters, views) |
|---|---|---|---|
| `style` | `style`, `section`, `slot` | `constraint` | `q` (on the index: filters the tree; in the kit section: the kit's text filter), `group`, `all` (kit section, `KitSurface.jsx:57`) |
| `phylogeny` | `style` | — | `view`, `rank`, `q`, `claims` (unchanged, `Phylogeny.jsx:39`) |
| `proportions` | `pack` | `style` — on the index narrows the list to that style's packs; on a pack marks it in *used by* and prints the reach line | `q`, `ceiling`, `opening`, `diameter` — all through `useSurfaceFilters`, replace. With no `ceiling` the slider shows the payload's `at.ceiling_height` and the request sends none |
| `faults` | `fault` | `style` (unchanged, `FaultCorpus.jsx:19`) | `sev`, `driver`, `q` |
| `glossary` | `term` | — | `q` (over term, aka, sense, id), `family` |
| `brief` | — | `style` — seeds the brief's style | `example` — a `briefs/` name; loads `/api/briefs/examples/<name>` |
| `candidates` | `candidate` | `parti` (unchanged) | unchanged |
| `workbench`, `drawings`, `export`, `transcription` | — | unchanged | unchanged |

Index rows and cross-record links are `RecordLink`s, which navigate by `nav.cite` and therefore
drop the source place's params — a `?q=` on the Styles index does not become the kit filter of the
dossier it opens.

### E.5 Context carry — `CONTEXT_KEYS`, `withContext`, `nav.cite(ref, ctx)`

In `router.js`:

```js
export const CONTEXT_KEYS = Object.freeze({ proportions: ['style'], faults: ['style'], brief: ['style'] });
export function withContext(target, ctx) { /* see below */ }
export function hrefFor(cite, ctx) { /* formatHash of withContext(routeCite(cite), ctx), or null */ }
```

`withContext({surface, selection}, ctx)` returns a new target whose selection gains `ctx[k]` for
each `k` in `CONTEXT_KEYS[surface]` where `ctx[k]` is a non-empty string and the target's own
selection has no value for `k`. The target always wins; keys not listed are dropped; a surface
with no entry returns the target unchanged. `nav.cite(ref, ctx)` (`nav.js:128-132`) becomes
`write(withContext(routeCite(ref), ctx))` with no params. **`nav.go` is unchanged** (`nav.js:89-91`):
a rail link carries exactly the selection it names, and a surface boundary drops selection and
filters.

### E.6 The server's fragment rule (`citations.py:77-98`, WP-14.3)

- kind `style`: a fragment is valid when it is a slot id **or** in `DOSSIER_SECTIONS`.
- kind `kit`: a fragment is valid only when it is a slot id.
- kind `term`: `_known_ids("term")` returns `core._data()["glossary"]`. No fragment rule is added
  for `term`, as none exists for `fault` or `pack`.
- `REF_RE` is untouched.

---

## F. `navModel` — the site map, in one pure module

`workbench/app/src/nav/navModel.js` feeds the rail, the crumbs, the front-door map, the palette's
surface entries and the walk. It retires `Chrome.surfaces()` (`Chrome.jsx:28-58`), Overview's
`DOORS` (`Overview.jsx:24`) and the `short` lines of `search/staticEntries.js:12-78`.

### F.1 Groups and items

| Group id | Heading (`term` of) | Item id (`data-nav`) | Surface | `href` | Label | Meta |
|---|---|---|---|---|---|---|
| `start` | `nav-group-start` | `overview` | overview | `#/` | `surface-overview` | none |
| `styles` | `nav-group-styles` | `style` | style | `#/style` | `surface-style` | `/api/overview` `counts.styles` |
| | | `in-hand` | style | `#/style/<in-hand id>` | the style's name; when it is the guided example, the name then ` · ` then the `guided-example` term | none |
| | | `in-hand:<section>` (nested) | style | `#/style/<id>` for identify, else `#/style/<id>/<section>` | `section-<section>` | the section's `count` from `/api/styles/{id}/dossier` (none for identify) |
| | | `phylogeny` | phylogeny | `#/phylogeny` | `surface-phylogeny` | none |
| `a-house` | `nav-group-a-house` | `brief` | brief | `#/brief` | `surface-brief`, step 1 | journey `words` |
| | | `candidates` | candidates | `#/candidates` | `surface-candidates`, step 2 | journey `words` |
| | | `workbench` | workbench | `#/workbench` | `surface-workbench`, step 3 | journey `words` |
| | | `transcription` (nested under `workbench`) | transcription | `#/transcription` | `surface-transcription`, no step number | none |
| | | `drawings` | drawings | `#/drawings` | `surface-drawings`, step 4 | journey `words` |
| | | `export` | export | `#/export` | `surface-export`, step 5 | journey `words` |
| `library` | `nav-group-library` | `proportions` | proportions | `#/proportions` | `surface-proportions` | sum of `/api/overview` `counts.proportion_packs` |
| | | `faults` | faults | `#/faults` | `surface-faults` | `/api/overview` `counts.faults` |
| | | `glossary` | glossary | `#/glossary` | `surface-glossary` | `/api/glossary` `count` |

Step numbers are the `JOURNEY` index plus one (§G), never literals. A meta is a bare figure from the
API or a journey word; its meaning is the item's description (`aria-describedby` from the surface
record, §I.2). Library links are bare — `#/proportions`, never `#/proportions?style=` — because a
rail link carries exactly what it names.

### F.2 The function

```js
export const NAV = /* the frozen table above, termIds and surfaces only */;
export function navModel({ lookup, counts, glossaryCount, inHand, dossier, journey, place }) →
  { groups: [ { id, termId, label, items: [
      { id, surface, href, termId, label, missing, step, meta, current, note, children } ] } ] }
export function headTermFor(place) → string   // the PageHead's record id
export function guidedExampleStyle(lookup) → string | null  // first `style:` cite in guided-example's see[]
```

- `label` is `lookup.term(termId).term`; where the record is missing `label` is `null` and
  `missing` is the id, and the rail renders `noEntry(id)` (§I.1).
- `inHand` is `{ id, name, guided }`: `prefs.styleInHand` with its name, or — when prefs holds none —
  `guidedExampleStyle(lookup)` with `guided: true`. Memory only offers: the `in-hand` item is a
  link, and nothing reads `styleInHand` into a URL or a selection.
- `children` of `in-hand` exist **only while** `place.surface === 'style'` and
  `place.selection.style === inHand.id` and `dossier` is that style's dossier payload; one child
  per entry of `dossier.sections`, in its order.
- `current`: `overview`/`phylogeny`/house/library items when `place.surface` equals theirs;
  `style` when the place is the Styles index or the slot panel; on the in-hand style's dossier,
  the child `in-hand:<s>` with `(place.selection.section || 'identify') === s` when children are
  listed, else `in-hand` itself. At most one item is current.
- `headTermFor(place)`: surface `style` with a style → `section-<section or identify>`; with no
  style, section `kit` and a slot → `section-kit`; otherwise `surface-style`; every other surface →
  `surface-<surface>`.

### F.3 Crumbs and the page title — `nav/crumbs.js`

`crumbsFor(place, { lookup, dossier, names, journey })` → `[{ label, href, termId }]`; the last
crumb is the place (`href` null, `aria-current="page"`); group crumbs have `href` null.

| Place | Crumbs |
|---|---|
| Front door | none |
| Styles index | Styles › Find a style |
| Dossier | Styles › *each `dossier.chain` name, root first, linking to its dossier* › *style name* › *section term* (omitted for identify) › *slot name* (kit section with a slot) |
| Slot panel | Styles › Find a style › Kit › *slot name* |
| Family tree | Styles › Family tree & map [› *style name*] |
| House step | A house › *step term* (transcription: A house › Trace a drawing) |
| Library | Library › Proportions [› *pack name*] · Library › Faults [› *fault name*] · Library › Glossary [› *term*] |

The dossier chain follows `member_of`, **never lineage**. Example, verified against
`styles/*.json` and `elements/slots.json`: *Styles › North American › American Colonial ›
Georgian Colonial American › Tidewater Georgian › Kit › Main cornice*.
`titleFor(crumbs, lookup)` = the non-group crumb labels from last to first joined by ` · `, then
` — ` and the `about-tdl` term; on the front door, the `about-tdl` term alone. `index.html:6`'s
static title becomes `Traditional Design Language`.

### F.4 The rule under all of it

**The URL decides what is read; per-browser memory only offers.** A bare `#/style`,
`#/proportions` or `#/glossary` shows an index, never a remembered or hard-coded record.
`StyleRecord.jsx:15`, `KitSurface.jsx:17` and `Proportions.jsx:19` (`DEFAULT_STYLE`,
`DEFAULT_PACK`) and `BriefIntake.jsx:43`'s default `style: 'tidewater-georgian'` go; the style in
hand is offered as a link or an `ActionChip` and never applied.
`FaultCorpus.jsx:16` (`DEFAULT_FAULT`) and `Phylogeny.jsx:20` (`DEFAULT_TAXON`) are not rebuilt in
tranche 1 and keep their defaults (§L).

---

## G. The house journey — `workbench/app/src/journey/journey.js`

Pure, React-free, tested at `src/journey.test.mjs`; reads refusal only through
`../sheet/refusal.js` (`evaluateRefusal`, `placementRefusal`, `sketchOf`), never re-derives it, and
is added to `refusal.test.mjs`'s `READERS` as `['journey/journey.js', '../sheet/refusal.js']`.

```js
export const JOURNEY = Object.freeze([
  { id: 'brief',      surface: 'brief' },
  { id: 'candidates', surface: 'candidates' },
  { id: 'plan',       surface: 'workbench' },
  { id: 'drawings',   surface: 'drawings' },
  { id: 'export',     surface: 'export' },
]);
export const ALTERNATE = Object.freeze({ transcription: 'plan' });   // joins at the plan step
export const JOURNEY_WORDS = /* frozen table of the words below, one spelling */;
export function journeyState({ session, plan, lastEval }) → {
  steps: [ { id, surface, n, href, state, words, canProceed, reason, counts, origin } ],
  alternate: { id: 'transcription', surface: 'transcription', joins: 'plan', href: '#/transcription' },
  resume: null | { id, n, href } };
```

`session` is `session.get()` (brief, jobId, result, progress, planFrom, jobError); `plan` is
`planDoc.get()`; `lastEval` is the shell's. `n` is the index plus one; `href` is
`formatHash(surface, {}, {})`. `lastEval` counts only when `lastEval.check.plan === plan.id`
(`plan_check.py:2748` returns the plan id); otherwise the plan is `unevaluated`.

| Step | `state` | `words` | Rule |
|---|---|---|---|
| brief | `todo` | to do | otherwise |
| | `stated` | stated | `session.brief.style` a non-empty string and `target_area_sf` a finite number > 0 — the schema's two required fields (`brief.schema.json` `required`) |
| candidates | `ready` | *k* candidates | `session.result` holds a `candidates` array; *k* its length |
| | `failed` | failed | `session.jobError.state === 'failed'`; `reason` is `jobError.reason` |
| | `expired` | expired | `session.jobError.state === 'expired'` |
| | `composing` | composing · *k* scored | `session.jobId` set, no result; *k* = progress entries carrying a numeric `n` and no `revised` flag. **No "of N"**: the stream carries no total (§0.1 #6) |
| | `none` | none yet | otherwise |
| plan | `empty` | no plan on the bench | no plan |
| | `refused` | the `judgment-refused` term, then the counts | `evaluateRefusal(lastEval) \|\| placementRefusal(lastEval.placement)` — the two readers `PlanWorkbench.jsx:504` and `ExportDetails.jsx:43` call |
| | `evaluated` | the counts | `lastEval.check` present for this plan |
| | `unevaluated` | not yet evaluated | a plan and no evaluation of it |
| drawings | `needs-plan` · `refused` · `ready` | needs a plan · blocked: refused · ready | `refused` when the plan step is refused. A working sketch does **not** block drawings: the Drawing Set re-places the record itself |
| export | `needs-plan` · `refused` · `sketch` · `ready` | needs a plan · blocked: refused · blocked: a working sketch · ready | `sketch` when `sketchOf(lastEval.placement)`, mirroring `ExportDetails.jsx:43-51` |

**Precedence** among candidate states: `ready`, then `failed`, then `expired`, then `composing`,
then `none`.

**Counts** (plan step, `evaluated` or `refused`): `{ fatal: check.counts.fatal ?? 0, serious:
check.counts.serious ?? 0, unjudged: check.constraint_summary.unjudged }` — `plan_check` writes a
severity key only when a finding carries it (`plan_check.py:2746-2747`), so an absent key after a
completed check is a real zero; `unjudged` is the figure the masthead has printed since before
this phase (`App.jsx:160`). The fault summary's own unjudged figure is a different population and
is **not** added in. The bar renders the three apart, `unjudged` and the severities as Terms.

**Origin** (plan step, whenever a plan is present): `planFrom` when `planFrom.planId === plan.id`,
else `{ kind: 'unrecorded' }` ("origin not recorded").

**`canProceed`/`reason`** — whether the reader may go on to the *next* step:

| From | `canProceed` when | `reason` otherwise |
|---|---|---|
| brief | candidates is not `none` | compose the brief first |
| candidates | plan is not `empty` | open a candidate on the bench |
| plan | drawings is `ready` | the drawings step's words |
| drawings | export is `ready` | the export step's words |
| export | never (last step) | null |

**`resume`**: the plan step when a plan is present; else candidates when its state is not `none`;
else brief when `stated`; else `null`. The front door's "Continue: <plan name>, step N" reads it.

### G.1 `session` additions (`state/session.js`, WP-14.10)

The `'tdl-workbench-session'` key (`session.js:6`) is unchanged; the persisted object becomes
`{ brief, jobId, planFrom, jobError }`.

```js
planFrom: null | { kind: 'candidate' | 'example' | 'traced', planId: string,
                   jobId: string | null, n: number | null, briefName: string | null }
jobError: null | { state: 'failed' | 'expired', reason: string, jobId: string | null }
```

| Writer | Writes |
|---|---|
| `CandidateSet.openInWorkbench` (`CandidateSet.jsx:170-179`) | `planFrom {kind:'candidate', planId: plan.id, jobId, n, briefName}` before `go('workbench')`; `n` is the 0-based index `api.candidatePlan(jobId, n)` was called with; the bar shows `n + 1` |
| the bench's example load (`PlanWorkbench.jsx`, one line) | `planFrom {kind:'example', planId, jobId:null, n:null, briefName:null}` |
| Transcription's "send to the bench" (one line) | `planFrom {kind:'traced', …}` |
| `BriefIntake` compose start | `{ result: null, progress: [], jobError: null, jobId }` |
| the job stream's `error` in `BriefIntake` and `CandidateSet` (`CandidateSet.jsx:112`, today `() => {}`) | `jobError {state:'failed', reason: d.error, jobId}` |
| reattach, `api.job` status `error` | `{ jobId: null, jobError {state:'failed', reason: j.error} }` |
| reattach, `api.job` 404 | `{ jobId: null, jobError {state:'expired', reason: errorText(e)} }` |

`BriefIntake`'s budget options come from `briefSchema().schema.properties.context.properties
.budget_tier.enum` — `value`, `mid`, `custom`, `unlimited` (`brief.schema.json:31`); today three of
the four offered (`BriefIntake.jsx:238`: `entry`, `move-up`, `estate`) are off-enum and refuse the
whole brief.

---

## H. Server payload additions

### H.1 `GET /api/proportions/{pack_id}?members=true` — `corpus.proportions_with_members`

Signature `proportions_with_members(pack_id, column_diameter=None, module=None,
ceiling_height=None, opening_width=None)` (today `corpus.py:317-358`). The route (`app.py:357-367`)
takes `ceiling_height: float = None, opening_width: float = None`; its non-members branch passes
`108.0` and `36.0` exactly as before when they are `None`. `core.get_proportions` is untouched.

1. Resolve the pack. `equals = pk["module"].get("equals")`.
2. `ceiling` = `ceiling_height` if given; else `module.default_size_in` when `equals ==
   "ceiling_height"`; else `108.0`. `opening` = `opening_width` if given, else `36.0`.
3. For a pack whose module is bound (`equals == "ceiling_height"`) the module **is** the ceiling:
   `core.get_proportions(pack_id, module=ceiling, ceiling_height=ceiling, opening_width=opening)`,
   and the `module` argument is not read. Otherwise the call is today's, with `ceiling` and
   `opening`. So the plate and the rules table describe one wall, and the slider moves both.
4. Add the keys below; choose `drawing`.

| Key | Value |
|---|---|
| `drawing` | `"stack"` when `pe.stack_for(pk)` is non-empty — **the existing path, every existing key's value byte for byte**; `"assemblies"` when `not pe.stack_for(pk) and pk.get("assemblies")` (so `moorish-arch`, an order pack with no stack, is drawn); `null` otherwise |
| `at` | `{ceiling_height: ceiling, opening_width: opening, module_in: out["module_in"]}` |
| `module_name` | `pk["module"]["name"]` |
| `module_bound_to` | `equals` or `null` |
| `kind` | `pk["kind"]` |
| `used_by` | §H.2 |
| `assemblies` | `"assemblies"` drawing: the list below, in the pack's declaration order. `null` drawing: `[]` (today's value) |
| `geometry` | `"stack"`: unchanged. `"assemblies"` and `null`: `null` (each assembly carries its own) |

Per assembly, for `drawing == "assemblies"`, with `d = pe.dimension(pk, out["module_in"], [aid])`
and `g = prof.pack_geometry(d, datum="wall")`:

```json
{"id": "casing_georgian", "height_modules": 0.0526315789, "height_in": 6.0, "height_in_stated": 6.0,
 "sums_check": true, "members": ["…dimension()'s member dicts, y measured from 0…"],
 "owner": "trim-classical", "geometry": "…g.assemblies[0]…", "unconstructed": []}
```

`height_in` is `height_in_summed` (the drawn extent), `height_in_stated` the stated height;
`owner` is `pe.assembly_owner(pk["id"], aid)`; `unconstructed` is `g["unconstructed"]` — a profile
the engine could not construct is reported, not drawn as something else.

Measured 24 Sep 2026 at `d565dea`: 57 packs — **25** `"stack"`, **27** `"assemblies"` (26 non-order
packs and `moorish-arch`; 50 assemblies, 237 members, 235 faces), **5** `null`
(`opening-proportion`, `room-harmonic`, `room-vernacular`, `storey-graduation`, `timber-bay`).
`trim-classical`: 20, 21, 12, 7, 7, 4 members = 71; at no ceiling `module_in == at.ceiling_height
== 114`; at `ceiling_height=108` the baseboard rule is `108 × 1.5 / 19` (8 1/2") and every member
height scales by 108/114.

**`build/profiles.py`**: `pack_geometry(dim, column=None, projection_datum=None, taper_steps=14,
datum="order")` (today `profiles.py:493`). Under `datum="wall"`: `R = r_top = die_naked = 0`;
every group's axis reading is `False`; `datum_for` returns `0.0` for every assembly and no
assembly takes the shaft's taper branch; so each face path is `M 0,y0 L x_from,y0 … L 0,y1 Z`
measured from the wall plane, and `naked_in` is 0; the output gains `"datum": "wall"`. **Under the
default no key is added and nothing changes**, which `test_profiles.py`, `test_render_profile.py`,
`test_drawn_geometry.py`, `check_orders.py` and a `render_profile.py` dry run hold for
`render_profile`, `render_orders`, `elevation`, `check_orders` and the workbench order plate.

### H.2 `used_by` — `corpus.pack_users(pack_id)`

Inverts `resolve_kit.resolve_packs` over every node of `core._kit_graph()` — no second cascade.

```json
{"own": ["beaux-arts-french", "…"],
 "delivered": [{"style": "tidewater-georgian", "from": "georgian-colonial-american",
                "role": "interior", "opted_in": true}],
 "applies_to_only": ["cape-cod-colonial", "…"],
 "bound_not_in_applies_to": ["beaux-arts-french", "…"]}
```

`own`: nodes where the pack's `_source` is the node itself, sorted. `delivered`: nodes where
`_source` is an ancestor, sorted by `style`; `opted_in` is whether the node names the pack in
`inherits_packs`. `applies_to_only`: the pack's `applies_to` less `own` less delivered styles.
`bound_not_in_applies_to`: `own` less `applies_to`. For `trim-classical`, measured 24 Sep 2026 at
`d565dea`: own **36**, delivered **6** (all six opted in, all `interior`), `applies_to` names
**42**, applies-to-only **7**, bound-not-named **7**.

### H.3 `GET /api/styles/{style_id}/packs` — `corpus.style_packs`

```json
{"style": "tidewater-georgian",
 "own":      [{"pack": "brick-course", "name": "…", "kind": "module-system", "role": "…", "precedence": 1}],
 "opted_in": [{"pack": "trim-classical", "name": "The Classical Trim Family", "kind": "trim-system",
               "role": "interior", "precedence": 3, "from": "georgian-colonial-american",
               "from_name": "Georgian Colonial American"}],
 "delivered": [{"from": "…", "from_name": "…", "distance": 2,
                "packs": [{"pack": "…", "name": "…", "kind": "…", "role": "…", "precedence": 4}]}],
 "withheld": [{"pack": "…", "name": "…", "kind": "…", "role": "…", "from": "…", "from_name": "…",
               "why": "…"}],
 "declined": [{"pack": "…", "name": "…", "kind": "…", "from": null, "from_name": null,
               "reason": "…", "basis": "node-record"}],
 "counts": {"own": 4, "opted_in": 4, "delivered": 0, "withheld": 0, "declined": 0}}
```

From `resolve_packs(g, chain_for(g, id))`: `own` where `_source == id`; `opted_in` where `_source`
is an ancestor and the node names the pack in `inherits_packs`; `delivered` the rest, grouped by
`_source`, groups nearest first by `distance` (the index of `from` in `chain_for(g, id)`), packs in
that ancestor's binding order. `withheld` from `withheld_for` (`from` = `_would_have_come_from`,
`why` = `_why`); `declined` from `refusals_for` (`from` = `_would_have_come_from`, possibly
`null`). `own` and `opted_in` are sorted by (`precedence`, absent last, then `pack`). An unknown
style is a 404 through `_ok` with `get_style`'s own error shape. (The figures in the example are
illustrative except those measured: Tidewater binds four packs and opts into four, among them
`trim-classical` from `georgian-colonial-american`.)

### H.4 `GET /api/styles/{style_id}/dossier` — `corpus.style_dossier`

```json
{"id": "tidewater-georgian", "name": "Tidewater Georgian", "rank": "variant",
 "member_of": "georgian-colonial-american",
 "chain": [{"id": "north-american", "name": "North American", "rank": "tradition"},
           {"id": "american-colonial", "name": "American Colonial", "rank": "family"},
           {"id": "georgian-colonial-american", "name": "Georgian Colonial American", "rank": "style"}],
 "members": [],
 "buildable_at": [],
 "sections": [{"id": "identify", "count": null}, {"id": "lineage", "count": 5},
              {"id": "kit", "count": 94}, "…"],
 "faults": {"verdict_here": ["…fault ids…"], "lineage": ["…"], "universal_count": 175,
            "matches": 206},
 "plan_types": {"massing_affinities": [{"massing": "center-passage-single-pile",
                                        "massing_name": "…", "affinity": "canonical"}],
                "partis": [{"id": "centre-passage-double-pile", "name": "…"}],
                "groupings": [{"id": "dependency-and-hyphen", "name": "…", "note": "…"}]}}
```

- `chain`: `member_of` ancestors, **root first**, excluding the node.
- `members`: `[{id, name, rank}]` of nodes whose `member_of` is this id, sorted by
  `period.floruit_start` then id. `buildable_at`: for rank `tradition` or `family`, every
  transitive `member_of` descendant of rank `style` or `variant`, same order; `[]` otherwise.
- `sections`: §D.2, in `DOSSIER_SECTIONS` order, zero counts omitted, `identify` first with `null`.
- `faults`, from `core.find_faults(style=id, limit=300)`: `verdict_here` = cards carrying any of
  `EXCEPTION_FOR_THIS_STYLE`, `EXCEPTION_NOT_EARNED_BY_THIS_STYLE`,
  `EXCEPTION_WHOSE_CONDITION_COULD_NOT_BE_JUDGED`, `INVERTED_FOR_THIS_STYLE` (`core.py:844-854`),
  or whose record's `severity_by_style` names this id; `lineage` = the other cards whose fault's
  `applies_to` does not contain `universal`; `universal_count` = the rest; the three partition
  `matches`. The example's Tidewater figures (8 + 23 + 175 = 206) were measured 24 Sep 2026 at
  `d565dea`.
- `plan_types`: the three lists counted in §D.2 — massing affinities from the node, partis from
  `core.list_partis(style=id)`, groupings whose `style_variation` names this id with `present` not
  `false` (with that entry's `note`).

### H.5 `GET /api/briefs/examples/{name}`

Mirrors `example_plan` (`app.py:466-480`): `os.path.basename(name)`, `.json` appended when absent,
so both `family-georgian` and `family-georgian.json` (the form `/api/schema/brief`'s `examples`
lists, `core.py:1583-1590`) load; a missing file is 404 `{"detail": {"error": "no example brief
'<name>'"}}`; unreadable JSON is 422 `{"detail": {"error": "example brief '<name>' is not readable
JSON", "detail": "…"}}`; the body is the file as stored.

### H.6 `GET /api/phylogeny` edges gain `slots`

Every edge (`corpus.py:63-68`) gains `"slots": e.get("slots")` — the lineage record's list where
it states one, `null` otherwise. `inherits_kit` keeps its rule (`bool(inherits_kit) or type in
CASCADE_EDGES`), which is the one spelling of "this edge carries the cascade"; the app reads the
served flag and never re-derives it.

### H.7 `module.equals` and its lie check

- `schema/proportion-pack.schema.json` `/properties/module/properties` gains
  `"equals": {"enum": ["ceiling_height"], "description": "The pack's own statement that its module IS this building input …"}`.
  The `module` object is `additionalProperties: false` today, so this is a schema edit.
- `proportions/systems/trim-classical.json` `module.equals = "ceiling_height"`, restating its own
  `module.name` ("The finished ceiling height of the room, …").
- `build/check_systems.py` gains check **19** and the docstring list gains it. The one spelling is
  a module-level `module_equals_errors(pack) -> list[str]`; a pack declaring `module.equals = V`
  errs unless **(a)** `V` is in `RULE_VARS` (a variable the engine binds); **(b)** at least one
  `derived_rules[].expression` references `V`; **(c)** no expression references `V` together with
  `module` or `part` (that would count the input twice); **(d)** `module.default_size_in` is a
  number (the ceiling default comes from it).
- `tests/test_module_equals.py` calls `module_equals_errors` over every pack in
  `proportions/**/*.json` (so a declaration outside `systems/` cannot escape), and a mutation that
  declares `equals` on a temporary copy of `trim-prairie` (whose rules never mention
  `ceiling_height`) makes `check_systems.py --dir <tmp>` exit 1 — **and the same copy without the
  declaration exits 0 first**, so the red is the declaration's and not the lone pack's (measured
  24 Sep 2026 at `d565dea`: `trim-prairie` alone in a directory checks clean, exit 0). The
  declaration on `trim-classical` passes all four: 13 of its 18 `derived_rules` read
  `ceiling_height` and none of those reads `module` or `part`.

---

## I. Client module contracts

These are the exports and props other lanes build against. A package may add; it may not rename.

### I.1 `components/Term.jsx` (WP-14.8)

```jsx
<Term id="binding-forbidden" />            // visible word = record.term
<Term field="kit.binding" value="open" />  // resolved through by_field
<Term id="judgment-unjudged">not judged</Term>   // children replace the visible word only
export function useTermDescription(id) → { describedBy, title, element }
export function noEntry(id) → string       // "no entry: <id>", the one spelling
```

- **Props: `id`, or `field` + `value`, and optional `children`. There is no definition prop and no
  fallback text.** A missing record renders `noEntry(id)` visibly; `glossary.test.mjs` makes every
  literal id resolve, so it is unreachable from shipped code.
- Renders a real `<button type="button" class="tdl-term" data-term="<id>" aria-expanded
  aria-controls>`; click, tap, Enter or Space opens a **non-modal** `role="dialog"` popover
  labelled by the term (`aria-labelledby`), never `aria-modal`; hover opens after 400 ms; Esc
  closes and returns focus to the button. One popover at a time (`help/popoverStore.js`, which
  also closes all on `hashchange` and when the palette opens).
- Popover content, in order: the definition; the analogy in italic; the provenance line (`kind` as
  plain text, then the first source, or `reads`); "not to be confused with" as links to the
  confusables; "more" as `<a href="#/cite/term:<id>">`.
- **A Term is never nested inside a `<button>` or an `<a>`.** Inside one — rail items, chips,
  section strips, map nodes, journey step links — use `useTermDescription(id)`: spread
  `aria-describedby={describedBy}` and `title={title}` on the control and render `element` (a
  visually hidden `<span id={describedBy}>` holding the definition, or `noEntry(id)`) beside it.

### I.2 `api/useGlossary.js` and `glossary/lookup.js`

`useGlossary()` → `{ status: 'loading' | 'ready' | 'failed', lookup, error }`, fetched once for the
app in the `useStyles` idiom (`api/useStyles.js`): a failure is reported, never an empty success.

`glossary/lookup.js` (pure, WP-14.6) — **no strings of its own**:

```js
export function indexTerms(payload) → lookup   // frozen
lookup.version                     // payload.version
lookup.term(id)                    // record | { missing: id }
lookup.termFor(field, value)       // record | { missing: `${field}:${value}` }   (reads payload.by_field)
lookup.confusables(id)             // records named by confusable_with, in order; a missing id yields { missing }
lookup.family(name)                // records of that family, in payload order
```

`glossary/fields.js` exports `FIELDS`, the seven keys of §A.4 with `{ family, schema, pointer }`.
`src/glossary.test.mjs` (node:fs only) holds it both ways to the records: every `FIELDS` key is
bound by at least one record with that schema and pointer, and every bound field is a key.

### I.3 `components/RecordLink.jsx` (WP-14.8)

`<RecordLink cite="pack:trim-classical" ctx={{ style: 'tidewater-georgian' }}>` —
props `cite` (required), `ctx` (optional, §E.5), `children` (optional; replaces the name). Renders
`<a href={hrefFor(cite, ctx)} data-cite={cite}>`: the name first in the serif (from `useNames`),
then the id as a Courier `ink-2` margin note. A plain primary click calls `nav.cite(cite, ctx)` and
prevents default; a modified or non-primary click is left to the browser. A cite `routeCite` cannot
read renders the name as plain text with `data-unresolved`, never as an anchor.

`names/names.js` (pure, WP-14.6): `nameFor(cite, entries)` → `{ name, note, resolved }` over
`/api/search/index` entries matched by `cite`; a `constraint:` cite takes its style's name with the
constraint id as `note`; an unknown cite returns the cite as `name` with `resolved: false`, never an
invented name. `names/useNames.js` is its React hook.

### I.4 `components/PageHead.jsx` (WP-14.8; mounted by the shell in WP-14.13)

`<PageHead termId={headTermFor(place)} />` — one prop. Renders `<header data-page-head="<termId>">`:
the record's `term` as the eyebrow (plain text, not a Term), `surface.what`, and a "How to read
this page" disclosure listing `surface.read[]` with `surface.try` as a `RecordLink`. The disclosure
is open on the first visit to each record and folded afterwards (prefs `seen`/`folds`, §I.10),
never in the URL or `useFilters`.

### I.5 `components/JourneyBar.jsx` (WP-14.10)

`<JourneyBar surface={surface} lastEval={lastEval} />`, reading the `session` and `planDoc` stores
itself and calling `journeyState`. Mounted **once, by `App.jsx`, above `<main>`**, only when
`surface` is `brief`, `candidates`, `workbench`, `drawings`, `export` or `transcription`, and not in
full screen. Renders `<nav aria-label="house journey">`; each step is an anchor with
`data-step="<step id>"` (the current one `aria-current="step"`) and its state words **outside** the
anchor; Next is an anchor only when `canProceed`; a blocked step is a `<span data-step
data-blocked="<state>">` saying why; the provenance line links back to the origin.

### I.6 `components/AssemblyPlate.jsx` (WP-14.9) — its data attributes

- One `<svg role="img" data-plate="<frame index>">` per frame from `assemblyLayout`, with a
  `<title>`.
- **One band per served face**: `<path data-asm="<assembly id>" data-member="<member id>">`, drawn
  from the face's served `path` through `translate`/`scale` only — `OrderPlate`'s idiom
  (`Proportions.jsx:149-177`), with no arc arithmetic. The count of `path[data-asm]` equals the sum
  of `geometry.faces` lengths, which equals the sum of `members` lengths except where an assembly
  has `sums_check: false` (§0.1 #4; for `trim-classical` both are 71).
- A chain line at `x = 0` (the wall plane) and a nominal hatched wall strip marked as interface
  furniture; leaders in the serif giving member name and `feetInches16(height_in)`; members too
  small to letter get numerals and a key below; module-part ticks along the wall when there are
  60 or fewer; an in-frame key whose words come from glossary records (`member`, `wall-plane`,
  `part`); the foot line from `figure-drawn-from-record` and `figure-drawn-upright`.
- `test_grammar_agreement.py`'s `_JS_SURFACES` gains `workbench/app/src/components/AssemblyPlate.jsx`,
  and a new assertion requires every app file emitting `data-asm` to be listed.

`plate/assemblyLayout.js` (pure, WP-14.6):
`assemblyLayout(assemblies) → { frames: [{ index, heightIn, widthIn, items: [{ id, xIn }] }] }`.
Assemblies are taken tallest first; an assembly joins the current frame when the frame's tallest
is at most twice its `height_in`, else it opens a new frame; within a frame, items sit side by side
on one baseline in the payload's declaration order and share one scale. `trim-classical` gives two
frames: the three wall sections (114 in each) and the three casings (6.9, 6.0, 4.5 in).
`placeLabels(labels, { minGapPx })` de-collides leader labels. Gutter and label constants are the
module's own, tested there.

### I.7 `styles/taxa.js` and `styles/styleTree.js` (pure, WP-14.6)

`taxa.js`: `TRADITION_HUES` (moved from `Phylogeny.jsx:30`, which imports it at WP-14.11),
`traditionOf(id, byId)`, `memberChain(id, byId)` (root first), `membersOf(id, taxa)`.
`styleTree.js`: `styleTree(taxa, traditionOrder) → { rows: [{ id, rank, depth }], orphans: [id] }`,
a port of `build/render_html.py:24-35` generalised to `member_of` recursion: traditions in
`overview.traditions` order (`core.py:169-171`), children by `floruit_start` then id, orphans
listed, never dropped.

### I.8 `fmt.js` — `feetInches16(x)` (WP-14.6)

A port of `proportion_engine._fmt_in` (`proportion_engine.py:659-669`) that must agree with it on
every input, **including its two behaviours a natural port gets wrong**: `frac × 16` is rounded
half-to-even (Python's `round`), and a sixteenth that rounds up to 16 increments the inch without
carrying into the foot. Output uses ASCII `'` and `"`; `null`/`undefined` → `-`.

`src/fmt.test.mjs` holds the vector table **as a JSON array literal between the marker comments
`/* VECTORS-BEGIN */` and `/* VECTORS-END */`**, which `tests/test_fmt_parity.py` extracts with
`json.loads` and asserts against `_fmt_in`. The table contains at least these, each verified
against `_fmt_in` at `d565dea`:

```json
[[6.875, "6 7/8\""], [114, "9'-6\""], [8.526315789473685, "8 1/2\""], [8.5263, "8 1/2\""],
 [24, "2'-0\""], [12.5, "1'-0 1/2\""], [0, "0\""], [0.03125, "0\""], [0.53125, "0 1/2\""],
 [0.59375, "0 5/8\""], [23.99, "1'-12\""], [11.97, "12\""], [-3.5, "-1'-8 1/2\""], [null, "-"]]
```

`23.99 → 1'-12"` and `11.97 → 12"` are the engine's carry behaviour reproduced, not endorsed:
changing `_fmt_in` changes every CLI and plate that prints it and is outside tranche 1 (§L).

### I.9 `judgment.js` (pure, WP-14.6)

```js
export function judgmentOf(holds) → 'passed' | 'failed' | 'unjudged'   // true / false / null or undefined
export const JUDGMENT_MARK = Object.freeze({ passed: 'pass', failed: 'fail', unjudged: 'unjudged' }); // JudgmentMark states
export function constraintStateOf(c) → 'constraint-executable' | 'judgment-yours-to-judge' | 'constraint-no-test-yet'
```

Never two states. The term id of a judgment is `'judgment-' + state`. `constraintStateOf`: a `test`
present → executable; else `scope === 'judgment'` → yours to judge; else no test yet — the state
`schema/constraint.schema.json` allows and no record takes today (660 constraints: 365 executable,
295 yours to judge, **0** no test yet, measured 24 Sep 2026 at `d565dea`). It is named so a record
that gains no test is not shown as executable. `Proportions.jsx:530`'s `holds ? 'pass' : 'fail'`
becomes `JUDGMENT_MARK[judgmentOf(holds)]`.

### I.10 `state/prefs.js` (WP-14.8)

localStorage key **`'tdl-workbench-prefs'`**, in `state/layout.js`'s idiom (read on load, a corrupt
or absent entry gives the defaults, a write failure keeps a working in-memory store):

```json
{"styleInHand": null, "seen": {}, "folds": {}}
```

| Key | Type | Written by | Meaning |
|---|---|---|---|
| `styleInHand` | style id or `null` | `StyleDossier`, on rendering a dossier the API resolved | offered by the rail and indexes; never applied |
| `seen` | `{ [key]: true }` | the component that showed the thing | `front-door` (the cold-link banner dismissed or the front door visited); `head:<termId>` (that PageHead shown once) |
| `folds` | `{ [key]: boolean }` | a reader's toggle | `head:<termId>`, `proof` (Proportions' "How this was checked"), `delivered` (the dossier's farther ancestors) |

Store API: `prefs.subscribe`, `prefs.get`, `prefs.setStyleInHand(id)`, `prefs.markSeen(key)`,
`prefs.isSeen(key)`, `prefs.setFold(key, open)`, `prefs.fold(key)` (→ `true`, `false` or
`undefined` when never set). Nothing in it enters the URL or `useFilters`. A package adding a
`seen` or `folds` key names it in its report.

### I.11 The assistant's name and the narrow-screen fold (WP-14.13)

- **Pane head.** `AiRail.jsx:135` prints the literal "the rail". `AiRail` gains a `title` prop
  rendered there; `RailHost` passes the `assistant` record's **`term`** ("Ask the corpus · AI
  assistant"), or `PANES.rail.label` while the glossary is loading, or `noEntry('assistant')` if it
  answered without the record. The aside's `aria-label` ("the rail — ask the corpus",
  `AiRail.jsx:127`) and `FoldControl`'s label stay, because `walk.mjs:1712-1770` selects on them.
- **Folded spine.** `App.jsx:186`'s `PaneStub pane="rail" label="the rail"` gains
  `spine={<the same term>}`; `label` stays `PANES.rail.label`, so the button's accessible name is
  still "show the rail".
- **Greeting and off-state copy** (`RailHost.jsx:15-24`) may be re-worded to say it is an AI
  assistant; `rail.py` and what it is sent are untouched (`oq/the-assistant-is-blind-to-the-page`).
- **`state/layout.js` exports `NARROW_FOLD_PX = 1500`.** `readStored` records whether the stored
  entry's `collapsed` object has an own property `rail` whose value is a boolean — *a stored
  choice*. On the store's **first** `clampAll(w)` call, if there is no stored choice and
  `w < NARROW_FOLD_PX`, `collapsed.rail` becomes `true`, published with `save = false` like every
  `clampAll`. No later resize folds or unfolds anything. A reader's toggle persists as today, and
  the next load honours it. Because `persist` writes the whole object, the fold is also written the
  next time the reader persists any layout act; that is a stored choice from then on. `PANES` —
  every label, and `PANES.kit` — is unchanged.
- `layout.test.mjs` is **extended, not re-pinned**: nothing stored + first `clampAll(1280)` →
  folded; nothing stored + `clampAll(1680)` → open; stored `collapsed.rail: false` + `clampAll(1280)`
  → open; stored `true` + `clampAll(1680)` → folded; nothing stored, `clampAll(1680)` then
  `clampAll(1280)` → open; `clampAll(1499)` folds and `clampAll(1500)` does not; the fold performs
  no localStorage write.

### I.12 The shell's other attachments (WP-14.13)

- Rail items become anchors `<a data-nav="<item id>" href aria-current>` inside the existing
  `nav[aria-label="surfaces"]` (`Chrome.jsx:156`), each with `useTermDescription(<termId>)`.
- `CrumbStrip`: `<nav aria-label="crumbs"><ol>`, between the masthead and the three-pane row,
  full width. `PageHead` then `JourneyBar` sit inside the centre column above `<main>`. All three
  are hidden in full screen.
- Masthead (`Chrome.jsx:60-101`): the wordmark becomes `<a href="#/">`; the "the workbench" eyebrow
  goes; `plan.id` and `plan.style` as bare text (`Chrome.jsx:85-86`) become "On the bench:
  <plan.name>" as a link to `#/workbench` with `data-bench-link`, with fatal and serious from
  `lastEval.check.counts` and unjudged as a Term; a visible "Keys ?" button opens the existing
  `ShortcutCard`; the inert Export and Settings icons (`Chrome.jsx:97`) go.
- `App.jsx`: `lastEval` clears when `plan.id` changes; a failed `/api/health` renders
  `role="status"` "Cannot reach the server · Retry" instead of `null` (`App.jsx:162`); an effect
  sets `data-reflow` on `document.getElementById('root')` on `overview` and `glossary`, which
  `tokens.css`'s `#root[data-reflow]{min-width:0}` (WP-14.8) releases from the 1380px floor
  (`tokens.css:455`); `document.title` from `titleFor`.
- `ColdLinkBanner` (`data-cold-link`): once per browser, when the first place loaded is not the
  front door and `prefs.seen['front-door']` is unset; shows the `about-tdl` definition and the
  current crumbs, with Front door, Guided example and Dismiss.
- Palette options gain `data-id="<entry id>"` and, for record entries, `data-cite`
  (`CommandPalette.jsx:166`); the opening hand follows navModel order and includes the front door;
  `SURFACE_ENTRIES` are derived from navModel names plus the kept synonym haystacks, and the `short`
  literals go.

### I.13 `components/EdgeGlyph.jsx` (WP-14.11)

Props become `{ edge, width, style }` with `edge = { type, inherits_kit, slots, from, target, note }`
in the served key names; `type` is a `lineage.type` value or `member_of`. The carry word:
`member_of` → the `member-of` record; otherwise `inherits_kit === true` → `carries-named-slots`
(listing the slots) when `slots` is a non-empty array, else `carries-the-kit`; otherwise
`carries-nothing`. The verb is `termFor('lineage.type', type)`. The `CARRIES` and `VERB` tables
(`EdgeGlyph.jsx:6-17`) and `Phylogeny.jsx:28`'s `CARRIES` are deleted. Both surfaces pass edges
from `/api/phylogeny`, whose `inherits_kit` is the one spelling (§H.6). `StyleRecord.jsx:217`'s
call site passes the edge until WP-14.12 deletes the file.

---

## J. What moves, who owns what, and in what order

### J.1 Guards that move — each re-cut to its property and proved able to fail

| Guard today | Re-cut to | Package |
|---|---|---|
| `walk.mjs` rail clicks at `:86`, `:974`, `:981`, `:993`, `:1001`, `:1075`, `:1084`, `:1095`, `:1102`, `:1434`, `:1444`, `:1494`, `:1936`, `:1946` | `visit(hash)` to the **same** surface's address in the unchanged app (`:1494` visits `#/kit` at 14.7 and `#/style` at 14.12), plus one loop proving every current rail item reaches its surface | 14.7 |
| `walk.mjs:1503-1511` palette found as `[role="dialog"]` | `[role="dialog"][aria-label="Search the corpus"]` (Term popovers are dialogs too); at 14.13 the first option's `data-id` is `faults` for "mistakes" | 14.7, 14.13 |
| `walk.mjs:58-68` rail block (live style count; `/Overview/ … /Transcription/`) | every navModel item renders as `[data-nav]` inside `nav[aria-label="surfaces"]` and reaches its `href`; the `style` meta equals `counts.styles`; no circled numerals or `WP-`/`OQ` in rail, masthead or crumbs | 14.13 |
| **`walk.mjs:1463-1464`** `rail present on every surface` (`/the rail/i` in the aside's text) | `aside[aria-label*="the rail"]` count is 1 and its head text equals the `assistant` record's `term` from `/api/glossary/assistant` | 14.13 |
| `walk.mjs:70-79` Overview (`what_this_is` on the landing) | main contains the `about-tdl` definition; inventory figures equal `counts.by_rank`; ontology version and Search stay in main; `what_this_is` stays served | 14.14 |
| `walk.mjs:981-989` Kit, `:993-997` Style Record | dossier: tell count = API `diagnostic_tells`; kit section renders the `thin-kit` definition live and its shown/bound figures equal `/api/kit`; rules rows = scope-judgment constraints | 14.12 |
| `walk.mjs:1000-1005` Proportions (`five authorities`, `/material modules/`, `/conflicts with building today/`) | authorities heading = `/api/authorities/<order>` rows (composite has 4); kind headings = `termFor('pack.kind')` words; conflict count = payload's | 14.9 |
| `walk.mjs:1016-1071` `readPlate` | clicks `[data-cite="pack:<id>"]` and asserts `location.hash`; `readPlate(null)` visits `#/proportions/gibbs-doric`; plus a `trim-classical` block (§I.6) | 14.9 |
| `walk.mjs:1477-1482` `#/kit/craftsman` refresh | canonicalises to `#/style/craftsman/kit` by `replaceState` and survives a refresh | 14.12 |
| `walk.mjs:1591-1596` W5 bare `#/kit` | `#/style/craftsman` then bare `#/style` shows the index and no dossier head; the 400-character regex goes | 14.12 |
| `walk.mjs:1751` `goto('#/kit')` in the full-screen block | `#/style`; full screen also hides crumbs, PageHead and JourneyBar | 14.12, 14.13 |
| `walk.mjs:96-162`, `:1831-1963` refusal contract | kept; plus Drawings and Export read blocked, and are not links, for a refused plan | 14.10 |
| `walk.mjs:1084-1091` Brief anchors | kept; plus every budget option is in the `/api/schema/brief` enum and their counts agree | 14.10 |
| `walk.mjs:1435-1440` Export `WP-5.3` and `262` | untouched in tranche 1, counted by the copy ratchet | — |
| `walk.mjs:1712-1824` pane labels, `:1584-1587` "searched" | unchanged | — |
| `router-unit.mjs:36-37` constraint → bench | lands on its style's `rules` section with `constraint` selected; `citeFor` inverts it | 14.5 |
| `router-unit.mjs:42-104` `KINDS` identity | gains `style:craftsman#lineage`, `term:judgment-unjudged`; aliases asserted separately; every `DOSSIER_SECTIONS` value round-trips a URL; `withContext` keeps only allowed keys | 14.5, 14.12 |
| `router-unit.mjs:109-119` `#/kit/…` shapes | `#/style/tidewater-georgian/kit/cornice`, `#/style/-/kit/cornice`, and the legacy parses of §E.1 | 14.12 |
| `router-unit.mjs:197-223` table agreement | kept verbatim; holds because `SELECTION_KEYS` gains `section` and `term` | — |
| `search-unit.mjs:74-78` kinds covered | the list gains `term` (it has no `kit`; `match.js:25-28` drops it) | 14.13 |
| `search-unit.mjs:123-142` synonyms `elements`/`bindings` → `kit` | → `style` | 14.12 |
| `search-unit.mjs:145-154` names find themselves | kept; names come from navModel | 14.13 |
| `test_grammar_agreement.py` | gains `DOSSIER_SECTIONS` agreement and "no slot id is a section" (14.3); `_JS_SURFACES` + the `data-asm` emitter rule (14.9) | 14.3, 14.9 |
| `test_search_index.py`, `test_citations.py`, `test_compression_and_caching.py` | `term` count computed in the test; section and term fragments; `invalidate()` leaves `corpus._GLOSSARY_PAYLOAD is None` | 14.3 |
| `check_counts.py` `CLAIMS` | `CLAUDE.md:743` moves by `--fix`; new rows police `workbench/README.md:18` and `docs/workbench.md:171`/`:178` (665 against 666 today) | 14.3 |
| `test_counts_guard.py` | 53 → 54, and in the same commit **both** figures it reads from `CLAUDE.md`: `:757`'s `**N checks, M tests**` with the test count re-measured, **and** a new dated `"51 of 54 checks passed"` illustration beside `:789`'s `"50 of 53 checks passed"`, because the largest quoted `of M` must equal `TOTAL_CHECKS` (`test_counts_guard.py:154-159`) | 14.1 |
| `test_zz_auth_leak_guard.py` | extended with `monkeypatch.setenv` only: signed out, `/api/glossary/about-tdl` answers 200 and `/api/glossary` and `/api/glossary/<any other id>` answer 401; `auth.OPEN_PATHS == ("/api/health", "/api/login", "/api/glossary/about-tdl")` | 14.3 |
| `layout.test.mjs` | extended per §I.11; `PANES.kit` kept | 14.13 |
| `refusal.test.mjs` `READERS` | gains `journey/journey.js` | 14.6 |
| `sse_handlers.test.mjs` | a behaviour check that `CandidateSet`'s error handler writes `jobError` | 14.10 |
| `test_profiles.py`, `test_render_profile.py`, `test_drawn_geometry.py` | the default datum unchanged for every consumer; the wall datum's faces start and close at x = 0 | 14.4 |
| `check_systems.py` | check 19, proved able to fail by `test_module_equals.py` | 14.4 |
| `test_schema_validators.py` | the glossary schema with one real record joins the loop | 14.1 |
| `test_check_all_shards.py` | new units take `DEFAULT_COST`; `check_costs.json` gains no key without a measurement | 14.1 |

**Unchanged by design**: the refusal-contract checks, `PANES` labels and `PANES.kit`, every file a
test reads by path (`PlanWorkbench`, `CandidateSet`, `BriefIntake`, `DrawingSet`, `ExportDetails`,
`Sheet`, `Proportions`), the `engineClaim`-pinned walk lines (`engineClaim.test.mjs:218-230`),
`Spotlight`, and the `?` card.

### J.2 Merge order

**14.7 → 14.6 → 14.5 → 14.1 → 14.4 → 14.2 → 14.3**, then **14.8 → {14.9, 14.10, 14.11} → 14.12 →
14.13 → 14.14 → 14.15**. Sequential only where files collide: 14.4 then 14.3 (one server agent);
14.1 before 14.2 merges (14.2's four batches author in parallel against §B and each verifies alone
after rebasing, §B.0); 14.8 before 14.9–14.11; 14.12 before 14.13; 14.13 before 14.14's merge.
Nothing in §A–§I requires a different order: the two dependencies that would have forced one — a
section-fragment cite in a glossary record, and a cross-batch homonym — are ruled out by §A.5
rule 7 and §B.0.

### J.3 Shared files and their owners

| File | Owners, in merge order |
|---|---|
| `workbench/app/src/App.jsx` | 14.8 one line (`SURFACES.glossary`); 14.10 one hunk (JourneyBar); 14.12 the `SURFACES` map (`style` → `StyleDossier`, `kit` removed); 14.13 the rest |
| `workbench/app/src/api/client.js` | append-only, lane L2: 14.4 `stylePacks(id)`, `styleDossier(id)`, `exampleBrief(name)` (fresh); 14.3 `glossary()`, `glossaryTerm(id)` |
| `workbench/app/e2e/walk.mjs` | after 14.7, each package edits only its own blocks (§J.1) and appends; never the `engineClaim`-pinned lines |
| `workbench/app/src/theme/tokens.css` | 14.8 only |
| `router.js`, `citations.js`, `state/nav.js`, `e2e/router-unit.mjs` | 14.5, then 14.12 |
| `search/staticEntries.js` | 14.12 (the kit entry becomes the style surface, synonyms kept), then 14.13 |
| `Chrome.jsx` | 14.8 deletes the unused `SurfaceHead` (`Chrome.jsx:316-330`); 14.13 the rest |
| `workbench/server/corpus.py`, `app.py` | lane L2 only: 14.4 then 14.3 |
| `workbench/server/citations.py`, `auth.py`, `mcp_server/core.py` (`_data` only) | 14.3 |
| `test_grammar_agreement.py` | 14.3 the `DOSSIER_SECTIONS` tests; 14.9 one `_JS_SURFACES` line and the emitter test |
| `CLAUDE.md` | 14.1 line 757 and the `N of 54 checks passed` illustration beside line 789; 14.3 line 743 by `--fix`; 14.15 the prose |
| `search/match.js`, `palette/CommandPalette.jsx`, `e2e/search-unit.mjs` | 14.12 the `kit` synonyms (`search-unit.mjs:123-142`); 14.13 `KIND_ORDER`, `KIND_LABEL.term`, option `data-id`/`data-cite`, the opening hand |
| `build/check_openings.py`, `build/check_all.py` | 14.1 |
| `glossary/*.json` | 14.1 the five seeds; 14.2 the rest, by batch |
| `surfaces/StyleRecord.jsx` | 14.11 the `EdgeGlyph` call-site line; 14.12 deletes it |

### J.4 Must not

- A fourth spelling of the citation grammar: no regex in `Term`, navModel, crumbs, `names.js`,
  `RecordLink`, `check_glossary` or any linkifier. `REF_RE`, `CITE_RE`, `ID_CHARS`, `FRAG_CHARS`
  stay byte-identical; `DOSSIER_SECTIONS` is a pinned vocabulary, not a pattern.
- A definition written in the app: no definition prop, no fallback gloss, no app-written rail
  description, page head, palette line, edge caption, kind heading or plate-key word. The copy
  ratchet only goes down.
- An invented source, or an editorial sentence presented as the corpus's.
- Collapsing unjudged: `holds: null` is unjudged; `out_of_calibration` and `scope_unjudged` read as
  not judged; fatal, serious and unjudged stay three counts; refused is its own state; a checker or
  walk that could not evaluate exits 3.
- Count literals in JSX or pinned literals in tests (`9 sections`, `4 formats`, `five
  authorities`, `71 bands`, `36 styles`): figures come from the API or the payload in hand.
- Memory deciding what a URL shows; help, fold or first-visit state, or the style in hand, in the
  URL or `useFilters`.
- Changing an MCP payload, `core.overview()`, `rail.py`, `/api/health`, or `auth.OPEN_PATHS`
  beyond the one ruled path.
- Renaming or removing a surface id `rail.py` reports (other than `kit` becoming an alias), a file a
  test reads by path, the keys `'tdl-workbench-plan'`, `'tdl-workbench-session'`,
  `'tdl-workbench-layout'`, or any `PANES` entry or label.
- `Chip` as an act or `ActionChip` as a filter: section strips, journey steps and rail items are
  anchors; Compose is a button; "for <style> ×" is a `Chip`.
- A tooltip, popover or router library; a static `three.js` import; glossary JSON imported into
  the bundle; a `src/*.test.mjs` in a subfolder or reaching `node_modules` or React.
- Arc or sweep arithmetic in JavaScript, or any change to `OrderPlate` or the order datum.
- Drawing what the record does not hold: the 4 + 12 + 3 zones, turned casings, a plate at the
  reader's building for a pack without `module.equals`, pictures for the five packs with no
  assemblies, photographs without files.
- A parti bridge or `?parti` brief seed; a tour that promises a house it cannot show; a "desk"
  beside "the bench"; new colours or inks, or readable text in `ink-4` in new components; a
  homeowner reader line on `about-tdl` (`VISION.md:359`).
- Citing a report before it exists, numbering a new question, hand-editing
  `docs/open-questions.md`, or re-pinning a moved guard to its new strings.

---

## K. Where each rule is spelled once

| Rule | The one spelling | Held to its other readers by |
|---|---|---|
| The citation grammar | `REF_RE` (`citations.py:29`), `CITE_RE` (`rail.py:186`), `parseCite` (`citations.js:21-27`) — three, by standing decision | `test_grammar_agreement.py` |
| Dossier section ids | `DOSSIER_SECTIONS` in `citations.js` and `citations.py` | `test_grammar_agreement.py` |
| What any word means | `glossary/<id>.json` | `check_glossary.py`; `glossary.test.mjs` |
| Which glossary record names an enum value | the records' `binds`, served as `by_field` | `check_glossary.py` rule 5 |
| The seven bound fields | `check_glossary.py` `FIELDS` and `glossary/fields.js` `FIELDS` | `glossary.test.mjs` against the records |
| Which files a glossary basis may read | `check_openings.GLOSSARY_REC_RE` (checker and served `reads`) | `test_check_glossary.py` |
| Basis verification | `check_openings.check_basis` | its seven callers' byte-identical stdout |
| Routes and legacy routes | `router.js` `SURFACE_PATHS`, `LEGACY_PATHS` | `router-unit.mjs` |
| Context carry | `router.js` `CONTEXT_KEYS`, `withContext`, `hrefFor`; `nav.cite` | `router-unit.mjs` |
| The site map | `nav/navModel.js` | `navModel.test.mjs`; the walk |
| Crumbs and titles | `nav/crumbs.js` | `crumbs.test.mjs` |
| Journey states and words | `journey/journey.js` | `journey.test.mjs` |
| May this be drawn or exported | `sheet/refusal.js` | `refusal.test.mjs` `READERS` |
| Draughtsman's notation | `proportion_engine._fmt_in` ↔ `fmt.js` `feetInches16` | `test_fmt_parity.py` |
| Judgment and constraint states | `judgment.js` | `judgment.test.mjs` |
| Which edge carries the cascade | `corpus.phylogeny` `CASCADE_EDGES` → served `inherits_kit` | the walk's lineage check (14.11) |
| Who uses a pack; a style's packs | `corpus.pack_users`, `corpus.style_packs` over `resolve_kit.resolve_packs` / `withheld_for` / `refusals_for` | `test_dossier_routes.py` |
| Section counts | `corpus.style_dossier` | `test_dossier_routes.py`: each equals its own endpoint's figure |
| Profile geometry | `build/profiles.py::pack_geometry` | `test_profiles.py`; the plate draws served paths only |
| A module bound to a building input | the pack's `module.equals`, lie-checked by `check_systems.module_equals_errors` | `test_module_equals.py` |
| Per-browser preferences | `state/prefs.js` (`'tdl-workbench-prefs'`) | `prefs` tests |
| Pane widths, folds, the narrow fold | `state/layout.js`, `NARROW_FOLD_PX` | `layout.test.mjs` |
| Popover placement; one popover open | `help/placePopover.js`; `help/popoverStore.js` | `popover.test.mjs` |
| The taxonomy tree; tradition hues | `styles/styleTree.js`; `styles/taxa.js` | `styleTree.test.mjs` |
| What is public | `auth.OPEN_PATHS` | `test_zz_auth_leak_guard.py` |

`help/placePopover.js`'s signature, for the lanes that call it:
`placePopover({ anchor: {x, y, width, height}, popover: {width, height}, viewport: {x, y, width,
height}, gap = 6, margin = 8 }) → { left, top, side: 'below' | 'above', maxWidth }` — below by
default, above when the popover would overflow the bottom and there is more room above; `left`
clamped into the viewport less `margin`; `maxWidth` set to the viewport width less twice `margin`
when the popover is wider; coordinates in the visual viewport. Tested at all four edges at
1280 × 720.

---

## L. What waits, and why

Filed by WP-14.0 as slug files; none is numbered.

| Question | What it holds back in tranche 1 |
|---|---|
| `oq/a-brief-cannot-name-a-parti` | "Start a brief from this parti": `brief.schema.json` is closed and has no `parti`; the dossier lists plan types as information only |
| `oq/the-assistant-is-blind-to-the-page` | telling the assistant what the reader has selected, and starter questions; its name ships, `rail.py` does not change |
| `oq/casings-are-measured-across-and-drawn-upright` | turned casings and the 4 + 12 + 3 dimension string; every assembly is drawn upright and captioned so |
| `oq/one-duty-per-hatch` | a product-wide key; the plate's nominal wall strip is marked as interface furniture meanwhile |
| `oq/mcp-proportions-serve-no-assemblies-for-non-order-packs` | MCP parity: `tdl_get_proportions` still serves `assemblies: []` for `trim-classical`, asserted |
| `oq/the-worked-house-has-no-plan-that-places` | the house half of the guided example; it stops at the style and the example brief |
| `oq/which-packs-module-is-a-building-input` | `module.equals` beyond `trim-classical`; `opening-proportion`'s door leaf is the obvious next and has no assemblies to draw |

Named here and not filed, because each is a known consequence rather than an open question:
`FaultCorpus.jsx:16`'s and `Phylogeny.jsx:20`'s hard-coded default records survive tranche 1 (the
Faults and Phylogeny surfaces are not rebuilt until tranche 2); `_fmt_in`'s sixteenth carry does
not carry into the foot and the port reproduces it (§I.8); the stale `665` in `Spotlight.jsx:3`'s
comment leaves with `Spotlight` in tranche 2; the `composing` state cannot say "of N" until the
job stream carries a total (§G).
