# WP-5.2 — The Workbench

*Report, 25 Aug 2026. Package text: "A self-contained HTML tool in `dist/` in the
manner of `orders.html`…". Delivered as a served app in `workbench/` instead, with
Lucas's explicit approval of the divergence (25 Aug) — the reasons are §2.*

## 1. What was built

- **`workbench/server/`** — FastAPI over `mcp_server/core.py`, 127.0.0.1 only. All 24
  capabilities as JSON routes; three aggregations no core function returned (the full
  phylogeny graph, row-per-ancestor cascade counts, a slot's full variant ladder);
  `POST /api/plan/evaluate` (validator + placement per edit gesture, with
  `fault_unjudged` and per-room-type overlay metadata joined in); compose as an
  in-memory job with SSE progress; an explicit `POST /api/dev/reload` for corpus
  edits; and the AI rail — an Anthropic tool loop whose 24 tool definitions are
  `mcp_server/server.py`'s own decorated wrappers collected through a stub `FastMCP`,
  with every model citation validated against live corpus ids before streaming and
  typed tags (`<unjudged>`, `<question>`, `<refusal>`) parsed into typed events.
- **`workbench/app/`** — Vite + React, ported from the Claude Design mockup: the
  Drawn Language token system verbatim, the 19-component design system (decompiled
  from the mockup bundle), and six live surfaces — Phylogeny (all 164 taxa on the
  broken time axis, cascade-carrying edges structurally heavier, shift-click compare
  backed by the real tells), Kit (cascade as a first-class display, lazy full slot
  records, the four-rank variant ladder), Fault Corpus (the Four-Foot Porch's prose
  carried whole; exceptions above the rule; fix tiers named plainly), Brief Intake
  (household as prose; silences named as future decision-log entries; advisory
  feasibility; the WP-2.3 conflict-set panel designed and marked forthcoming),
  Candidate Set (ranked, never crowned; trades-away beside the score;
  `dropped_lot_infeasible` as its own honest strip; decisions rendered as the prose
  they are), and the Plan Workbench — the record-owning edit loop: click any mark to
  its record, drag a wall (snapping to the bay grid) and watch the validator
  re-score, switch the style and watch constraints appear and clear, assert
  `not-visible-from` and have it clear only if the validator clears it, with the
  could-not-evaluate panel drawn from three kept-distinct sources.
- **Verification** — 24 pytest tests (endpoints, CLI parity finding-for-finding, rail
  loop on a fake transport, citations), a smoke script that diffs the HTTP results
  against the CLI's own `--json` output live, and a Playwright walk that asserts the
  honesty affordances on every surface. `build/check_all.py`: all 21 checks green.

Two `build/` files were touched, both additively, both pinned by
`tests/test_workbench_touches.py`:

1. `plan_check.py` — `check()` now returns `fault_unjudged` (the fault layer's
   could-not-judge list, previously computed and discarded; only its count survived
   in `fault_summary`), and the internal `check_measurements` call lifts the API's
   limit of 40 so the list is whole (§3.2).
2. `compose.py` — `compose(…, on_candidate=None)`, invoked once per kept candidate
   with its summary, plan excluded. Default `None` leaves behaviour identical; the
   CLI never passes it.

## 2. Why not a self-contained `dist/` HTML tool

The package text predates two facts. First, the workbench's defining interactions —
re-score on a wall drag, compose on demand, style-switch re-evaluation — are calls
into `plan_check`/`geometry`/`compose`; a self-contained file would need JS ports of
all three, compounding the dual-engine agreement tax the repo already pays once
(`proportion_engine.py` ↔ `orders_template.html` ↔ `render_elevation.py`, held to
0.02 in). Second, OQ 28's fix is what makes interactivity real, and it is a
*process-warm* cache: a long-lived server keeps `check()` at ~0.3 s, where any
subprocess-per-request or static design pays the cold path. The MCP README's own
line — "`core.py` is pure functions with no protocol dependency, so it is usable
from a notebook or a platform directly" — described the architecture before the
package did. `dist/taxonomy.html` and `dist/orders.html` are untouched.

## 3. What was found

1. **`check()` throws away the *which* of fault-layer ignorance.** It kept
   `fault_summary.unjudged` (a count) and discarded `could_not_judge` (the list). A
   surface obliged to say *which* faults were beyond evaluation could not, without
   duplicating `check()`'s elevation-derived measurement assembly. Hence the additive
   key. Related: the API default `limit=40` truncated the list while the summary
   counted all (~122 on the careful Tidewater plan) — "unjudged is not passed"
   degrading quietly into "the first forty unjudged are not passed".
2. **Findings have no ids.** `{severity, layer, statement, room?, rule?, fix?}` —
   nothing stable to diff, cite, or animate against. The client derives
   `hash(layer|statement|room)`; it works, but a server-side id would let the rail
   cite findings robustly (OQ 32).
3. **Relaxations have no positions.** `geometry_report.relaxations` is
   `{count, max_off_grid_ft, note}`; the mockup's positioned on-drawing markers were
   its own invention (`[G]`). The sheet renders the honest tally at the plate caption
   instead. Marking them *at their location* (P7) needs `geometry.solve()` to record
   `{level, x, y, off_ft}` per cut (OQ 33).
4. **A missing `jsonschema` masquerades as data.** `core.check_plan`'s lazy import
   sits inside the `try` whose `except` returns "plan does not match the plan
   schema" — with the package absent, every plan "fails schema" with detail
   `No module named 'jsonschema'`. `/api/health` asserts the import instead (OQ 35).
5. **Composer decisions are prose lines**, not structured records — the mockup's
   `{field, chose, because}` `DecisionLogEntry` had imagined structure the log does
   not carry. Rendered as prose; structuring is OQ 34.
6. **`resolve_kit` flattens the variant ladder.** Its rows carry `canonical[]` and
   `forbidden[]` id lists; `permitted` and `atypical` — half the four-rank ladder,
   851 forbidden against 580 permitted and 87 atypical corpus-wide — exist only in
   the kit files. The `/api/kit/{style}/slot/{slot}` aggregation walks the cascade to
   the binding kit for the full list rather than changing core.
7. **The mockup's finding-layer vocabulary was partly invented.** Real layers on a
   checked plan: `adjacency, circulation, completeness, daylight, fault, furniture,
   grouping, room, servicing, style` — no `privacy`/`code`/`plan` rows on the example
   plans, and `completeness` (absence-is-not-failure) the mockup didn't know. The
   layer strip enumerates what the response actually contains.
8. **The compose teaching example reproduces live**: side-hall-townhouse 291.0
   scores best and is not native; centre-passage-single-pile 472.0 is native and
   scores worst. Score and rightness render as separate axes because the corpus's own
   output insists on it.

## 4. What was deliberately not done

- No JS ports of validator/composer/geometry/proportions; no DXF/IFC (WP-5.1); no
  cost engine (WP-5.4); no drawing ingestion (WP-5.5); no auth or multi-tenancy.
- Style Record ③, Proportions ⑩, Drawing Set ⑧ and Details & Export are designed-for
  but unbuilt, listed as *forthcoming* in the left rail (never hidden). The Drawing
  Set will re-tokenize the Python renderers' dark-palette SVG server-side rather than
  porting them.
- No file-watcher on the corpus: reload is explicit (`/api/dev/reload`), because
  auto-invalidation per request would reintroduce the OQ-28 tax.
- The composer's `decisions` and the finding-id gap were left upstream as open
  questions rather than patched around further.
- Windows the placement layer cannot situate (a declared wall the solver put
  elsewhere) are omitted from the sheet rather than invented — the drawing stays a
  render of the record.

## 5. Milestone 2 — Style Record ③ and Proportions ⑩ (25 Aug 2026)

Two more surfaces live, bringing the count to eight of ten.

**③ Style Record.** All nine sections of `get_style` on one page, with the room given
to what the job actually needs: diagnostic tells and `distinguished_from` outrank the
description, `massing:`-prefixed neighbours are labelled as a separate namespace, and
the constraint table renders the three states without inventing verdicts — an
executable test is marked *executable* (not "passing": nothing was evaluated), a
statement awaiting a test says so, and a `scope: judgment` row takes the hatched mark
with the corpus's refusal stated. The three deliberately unbound nodes
(`egyptian-revival`, `moorish-andalusian`, `mudejar`) render their OQ-29 exception as
a position, not a hole. `style:` citations now land here (the full record beats the
graph panel); the Phylogeny keeps its own selection behaviour and links across.

**⑩ Proportions.** The JS engine port is deliberately **not** reused: the surface
speaks HTTP to `proportion_engine.py`, ending the dual-engine tax for this surface
(`dist/orders.html` is untouched and remains the place for full moulded profiles —
the workbench plate draws the engine's member stack plainly, every band a member
`dimension()` emitted, hover for its note). The non-classical packs lead the
navigation as equal citizens; authorities compare at a common column diameter with
the never-a-common-module rule printed on the strip; invariants render proved
(`holds`) against the data; `judgment: true` rules take the hatch and say "yours to
decide"; and the pack conflicts render with their `resolution` prose whole. Server
additions: `GET /api/proportions` (the pack list — no core function returned it) and
a `members=true` variant of the pack route (the plate needs every assembly's members
at once; the API's one-assembly shape is right for an agent's context budget, wrong
for a drawing).

Found in M2: nothing that changes the corpus — the one modelling note worth recording
is that `get_style`'s constraint rows distinguish tested from judgment cleanly, but a
*tested* constraint on this surface must not borrow the pass mark: pass/fail belongs
to evaluation against a plan, and the record page shows capability, not verdicts.
Five new pytest tests pin the M2 endpoints, including a cross-check that the HTTP
members and totals are byte-equal to `proportion_engine.dimension()`'s own.

## 6. Milestone 3 — Drawing Set ⑧ and Details & Export (25 Aug 2026)

All ten surfaces are now live.

**⑧ Drawing Set.** `POST /api/drawings/{kind}` runs the same generators the CLI
drives — `geometry.solve` + `render_plan`, `build_elevation` + `render_elevation`,
`build_section` + `render_section`/`render_bearing_diagram`, `build_roof` +
`render_roof` — to a tempfile, reads the SVG back, and passes it through
`workbench/server/svg_theme.py`: a value-by-value hex map from each renderer's dark
palette to Graphic Standard № 1's tokens (glazing to coal, verdigris to green-deep,
iron to brick, the room fills to pale warm washes), fonts included. Re-rendered,
never redrawn — the two-registers rule applied to a whole pipeline, with zero
`build/` edits; a proper `palette=` parameter upstream stays noted as future work.
The elevation sheet carries WP-3.2's disclosure permanently and on-sheet ("83 of its
named 100 photograph-measurable faults; the remainder have no model at this layer
yet"). A generator that refuses (a record without what it needs) renders as a
refusal card, not an error. A test pins the mapping as *total* over the four
renderers' palettes, so a new renderer colour cannot ship half-dark.

**Details & Export.** What leaves the system today leaves plainly: the plan record,
the brief, the validator's full report (could-not-judge list included) and all five
SVG sheets, re-generated at download, never screen-snapshotted. What is not built is
present, disabled, and named with its work package — DXF/IFC (WP-5.1), the
guidelines book and details library (WP-5.3), drawing ingestion (WP-5.5) — over the
hatched forthcoming treatment. The closing line states that no costing engine
exists and that code findings are advisory, always.

The left rail now lists no forthcoming surfaces; the honesty moved into the Export
surface's cards, and the e2e walk's assertion moved with it (20 checks green;
30 server tests green).

## 7. Open questions raised

Appended to `docs/open-questions.md` as OQ 32–35: stable finding ids; relaxation
positions in `geometry.solve()`; structured composer decisions; and
`check_plan` distinguishing "jsonschema unavailable" from "schema invalid".
