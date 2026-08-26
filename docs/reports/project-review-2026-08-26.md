# Project review — where the language stands against its own vision, 26 August 2026

*A comprehensive review run the day after the 25 Aug merge, at Lucas's request: where
everything is at, what still needs to be done, and what it takes to reach the destination
articulated in `VISION.md` and the UI/UX specifications. Every number in this report was
produced by a run on 26 Aug 2026 — `check_all.py`, `check_inheritance.py --unendorsed`,
`check_addresses.py`, `check_counts.py`, and direct reads of the code — not quoted from a
prose document. Where a claim rests on yesterday's adversarial audit rather than a fresh
run, the report says so.*

*One finding about the specs themselves, before anything else: the original UI/UX
specification bundle — the UISPEC the tokens file cites, `uploads/VISUAL-LANGUAGE.html`,
`guidelines/the-drawn-language.html`, the mockup's own readme — was never committed to
this repository and exists on no reachable disk. What survives of it in-repo is
authoritative and substantial: `docs/workbench.md` (the layer spec), `workbench/README.md`
(the product spec and its "what it will not claim" list), the verbatim Graphic Standard №
1 in `workbench/app/src/theme/tokens.css`, the P1–P8 principle statements quoted in the 19
component headers, the per-surface intent in the 11 surface headers, and the 20 executable
assertions in `workbench/app/e2e/walk.mjs`. This review audits against those. If the
original bundle still exists on Lucas's machine, committing it under `docs/` would close
the one gap this review could not: nobody can any longer check the derived spec against
its source.*

---

## I — Where everything is at

### The phases

| Phase | State | The one-line truth |
|---|---|---|
| 0 — Consolidation | Complete | |
| 1 — Executable constraints | Complete | 660/660 migrated, 61.5% of hard ones tested (bar was ≥60%) |
| 2 — Composition | Complete | CP-SAT placement with named conflict sets; the heuristic is still the default engine everywhere (OQ 54) |
| 3 — The elevation | Complete | WP-3.2 evaluates 83 of a named 100 photograph-measurable faults, disclosed |
| 4 — Breadth | In progress | 4.1–4.3, 4.5, 4.6 complete · **4.4 environment-blocked** · 4.7 unstarted (scope-only by design) |
| 5 — Platform | In progress | 5.1 (DXF/IFC), 5.2 (the workbench), 5.5 (ingestion) complete · **5.3 and 5.4 unstarted** |

### The corpus, counted fresh

164 style nodes · 476 lineage edges · 97 slots (ontology 0.7.0) · 40 massings · 60 rooms ·
17 groupings · 21 partis (129 of 132 styles native, 0 uncovered) · 57 proportion packs
carrying 262 recorded conflicts-with-building-today · 209 faults · 159 kits · 322 image
records, 0 sourced · 14 reference plans · 24 MCP tools. `check_counts.py`: 22 count claims
across 5 files, 0 stale.

**The suite, run fresh for this review:** `check_all.py` — 27 of 30 checks OK, 3 reported
N/EV (could not evaluate, correctly not counted as passes) for the optional libraries this
container lacked. This review then installed those libraries and evaluated all three: the
DXF selftest round-trips both plans identically (116 findings carried and returned), the
IFC selftest's acceptance surface is present on both plans, and the workbench suite runs
**91 passed** against a freshly built frontend — including `test_example_plan_no_traversal`,
the one WP-5.1 flagged as needing `app/dist` to exist. `tests/` collects 762 (743 passed,
19 skipped where a dependency stays optional). Nothing red anywhere.

### The pipeline, stage by stage

Brief in → house out currently runs: `compose.py` (brief → N ranked contrasting candidates
with a decision log and `trades_away`, `plan_check.py`'s five layers as the fitness
function) → `geometry.py`/`geometry_cp.py` (placement, hill-climb search or CP-SAT proof)
→ `structure.py` (walls, bearing, storeys, stairs) → `roof.py` → `elevation.py` → four SVG
renderers drawing only from the record → `export_dxf.py` (four sheet kinds, the record
riding as XDATA) and `export_ifc.py` (IFC4). Backwards: `ingest_dxf.py` and the
Transcription surface take a drafter's drawing to a candidate record with its gaps named.
All of it is reachable three ways — CLI, the 11-surface workbench, and 24 MCP tools —
through one `mcp_server/core.py`.

What does **not** exist at any stage: a details library, generated guidelines, a costing
layer, elevations for faces outside the classical-front family (they refuse rather than
guess, correctly), IFC solids beyond the plain gable family (hip/gambrel/cross ship an
`IfcRoof` with properties and a `geometry_note`, not geometry), any interactive 3D or
perspective view, and construction details. Each absence is stated in the product rather
than hidden, which is the house style and correct.

### The implementation surface

Zero TODO/FIXME/stub markers anywhere in `build/`, `mcp_server/`, `workbench/`, or
`tests/` — this codebase records its limitations in prose and refusal objects, so the gap
list in this report is the real one, not a grep. CI exists (`.github/workflows/ci.yml`,
two jobs). The workbench is 11 live surfaces over a FastAPI skin on `core.py`, with the
19-component design system, SSE compose jobs, the AI rail with typed refusal/unjudged
cards, and the MCP tools mounted at `/mcp` behind the same gate.

---

## II — Distance to the vision (`VISION.md`)

### §V, the compiler: **built end to end for 2-D documents**

Every row of the compiler table has a real implementation behind it — language spec
(schemas), linters (30 checks), type checker (`plan_check.py`), front end
(`compose.py` + the geometry engines), IR (the plan record with counted compromises),
back end (structure/roof/elevation), object code (SVG/DXF/IFC), runtime (server + MCP +
workbench). The sentence that is not yet true is in the object code row: **"drawings a
builder can price"** — nothing prices anything (WP-5.4, deliberately partner-gated), and
"permit" remains advisory model text by explicit design (§X).

### §VII, the commitments, audited one by one

| Commitment | Verdict | Evidence |
|---|---|---|
| Unjudged is not passed | **Structurally met; breached live in one layer** | The three-state discipline is real in every checker, the workbench, and the rail. But OQ 52: `elevation.py` states dormer counts, chimney dimensions, gutter outlets and raking-cornice counts it never measured, and the fault corpus convicts **both shipped reference plans** on them. Worse than unjudged-as-passed: `core.py`'s fault bucketing drops `status: "error"` from every bucket — unjudged as *absent*. |
| A rule the sources don't determine is deferred, never invented | Met | 295 constraints at `scope: judgment`; judgment slots render as offered-back, not hidden |
| Sources, or an honest mark | Met | 0 silent editorial parameters (OQ 18's note half); `invented` is 14 of 1,569 and shouts |
| Prose stays beside the test | Met | Verified pattern-wide by `check_constraints.py` |
| Open questions numbered, not silently decided | Met | 63 entries, 18 open, list derived from the file by a test |
| Findings matter as much as code | Met, with two lapses | 25 reports; but WP-2.4 and the deployment work shipped without one — see §VI |
| The drawing is a render of the data | Met | `derive.js` is a line-for-line port of `render_plan.py`; the two stated departures are printed on the plate |
| Several candidates, never one, never "good" | Met, structurally | No crowning anywhere; `trades_away` beside every score |
| The generator refuses, and refusals are content | Met | `RefusalCard` is a first-class component; refusals in the decision log |
| Compromises are counted and reported | **Half met** | Counted, yes — the tally is honest. "At its location" (P7) is not: `geometry.solve()` records no positions, so `RelaxationMarker` has nothing to place (OQ 33). |

### §XI, the horizon

1. *Proof, not preference* — **delivered** (WP-2.3, CP-SAT, named minimized conflict
   sets), with the qualifier that the proof engine is opt-in and the search remains the
   default everywhere (OQ 54).
2. *Leaving the system* — **half delivered**: drawings and IFC yes; the details library
   and generated guidelines no (WP-5.3).
3. *Reading drawings* — **delivered** (WP-5.5).
4. *Peer trunks* — **unstarted** (WP-4.7, scope-only by design).
5. *Cost as a first-class layer* — **deferred on purpose**, waiting on a partner's
   numbers (WP-5.4).

### §XII, the success statement, clause by clause

"A brief goes in one end and a drawing comes out the other" — **true today.** "That a
builder can price" — **false** (no cost layer). "A drafter can open" — **true** (DXF with
a proven round-trip). "An inspector can pass" — **advisory by design**, and the product
says so everywhere it could be misread. "A classicist can criticise on the merits" —
true for the front elevation family; other faces refuse. "Says *I don't know* often
enough to be trusted" — structurally yes, and OQ 52 is the one live counterexample, which
is exactly why it is the most urgent item in this review. "Every number traced to who said
it and why" — true for the corpus (1,556 kit parameters, 74.6% measured, every editorial
one marked); not yet true for the five numbers `elevation.py` invents.

### PLAN-OF-ACTION §7, "what finished looks like"

The Tidewater Georgian acceptance paragraph is **nearly reachable end to end**: kit at the
declared date ✓, native partis the lot can hold ✓, four candidates with entrance on the
stated front ✓, bay-grid placement with walls and a section ✓, five-bay Gibbs front with
sash lights correct for the date and one head datum per storey ✓, the garage hyphened at a
70% ridge ✓, DXF out ✓, decision log ✓. The three honest asterisks: the fault sweep
reports 209 faults but convicts on some it never measured (OQ 52); the decision log is
prose lines, not the `{field, chose, because}` records the UI was designed for (OQ 34);
and the placement that ships by default is the search, not the proof (OQ 54).

---

## III — Distance to the UI/UX spec

### The principles, P1–P8

| Principle | Verdict |
|---|---|
| P1 — three states, unjudged is a form not a colour | **Met.** `JudgmentMark`, the hatched chip in the masthead, the three-source could-not-evaluate panel |
| P2 — the cascade is a first-class object; a source chip on every number | **Met.** `ProvenanceTrace`, `SourceChip`, the Kit surface's source column |
| P3 — a refusal is content, not an error | **Met.** `RefusalCard` everywhere a generator can decline |
| P4 — rank, never crown; score and rightness are different axes | **Met.** `CandidateColumn`; `trades_away` never behind a disclosure |
| P5 — style exception above the general rule | **Met.** `FaultCard`; verified in the surface |
| P6 — the sheet draws only from the record | **Met.** Two stated departures, printed on the plate |
| P7 — a compromise is counted AND appears on the drawing, at its location | **Unmet, knowingly.** Only the tally ships; `RelaxationMarker` exists with nothing to position it. OQ 33's fix (`{level, x_ft, y_ft, off_ft}` per relaxation) is additive and would serve `render_plan.py` too. |
| P8 — two severity axes, three fix tiers named | **Met.** |

### The surfaces

All 11 specified surfaces are live and carry their spec intent in their headers. Two
inventory findings:

- **Surface ① — the Console with its corpus-health strip — is specified in the component
  layer (`ToolTrace.jsx` names it) and absent from the product.** The rail runs ②–⑪ with ⑧
  used twice. Either build it or strike it from the component header; at present the spec
  and the product disagree silently.
- The **conflict-set panel is still marked "forthcoming (WP-2.3)"** on Brief Intake and
  the Plan Workbench — and WP-2.3 shipped on 25 Aug. `geometry_cp.py` produces named,
  minimized conflict sets today; the UI never learned. This is the single cheapest
  high-value UI item on the board, and the e2e walk currently *asserts the stale marker*
  (`walk.mjs:93`), so the fix must move the assertion with it.

### The known spec-vs-product gaps, all recorded as OQs

OQ 32 (findings have no server-minted id — the client hash breaks silently on rewording),
OQ 33 (P7 above), OQ 34 (`DecisionLogEntry` renders a `{field, chose, because}` shape the
composer's prose does not have). All three fixes are additive; all three need a ruling
that has not come.

### Numbers the chrome asserts that the data outgrew

The post-merge commit ("three workbench pins the Phase 4 data outgrew") caught some of
this class; two more were live when this review ran, both now fixed (§VI): the rail's
hardcoded **"36 packs"** against 57 on disk — now summed live from `/api/overview` — and
the Export surface's **"158 recorded pack conflicts"** against 262 (the WP-4.6 packs grew
it), pinned stale by `walk.mjs` as well. The Export surface also still carried a
**"forthcoming" card for drawing-to-record ingestion**, which shipped as the Transcription
surface in the same codebase — now updated. Left alone, deliberately: "9 sections" and
"5 sheets" (both accurate), and the elevation disclosure "83 of the 177 applicable"
(accurate, and the honest form of WP-3.2's shortfall).

### The visual language

Graphic Standard № 1 is implemented as written — single theme, duty-exclusive colour, one
serif and one mono, 26–30px rows — and `svg_theme.py`'s hex map is pinned *total* by test
so a renderer colour cannot ship half-dark.

---

## IV — Live wrongness, ranked above absence

These four are not missing features; they are the system saying something untrue today.

1. **OQ 52 — the elevation layer invents measurements and the critic convicts on them.**
   `roof.py:449` refuses to judge dormers; `elevation.py:563` overwrites that refusal with
   `dormer_count: 0`, so "Dormers Off the Rhythm" fires PRESENT/serious on houses with no
   dormers modelled. Five chimney dimensions are stated as constants beside a correctly
   absent count, and `vestigial-chimney-chase` is adjudicated from their ratio — a
   fabricated failure beside a fabricated pass. `gutter_outlets: 2` convicts both plans of
   a gutter fault when nothing in the corpus models a gutter. And `core.py`'s bucketing
   loses `status: "error"` results entirely. The fix shape is already written in the OQ
   entry (emit no key where nothing was modelled; give error its own bucket; one test
   asserting every fault's named measurements are produced or reported could-not-judge).
   It moves pinned counts on both reference plans, which is why it needs its own package
   rather than a drive-by — but every day it stands, the fault corpus is generating false
   convictions, which is the reputational core of the product.
2. **OQ 53 — pack resolution is units-blind.** `resolve_kit.choose_pack` groups rules on
   `(dimension, quantity)` and never reads `units` (verified in the code this morning).
   68 own-binding addresses agree on all three and disagree on units — up to 36-fold —
   and in two live cases (`craftsman`, `craftsman-bungalow`, slot `casing`) a ratio rule
   wins over inch peers: 0.1667 where 3.5 in was meant. The two named cases are fixable
   alone; the address-key question (which of the 68 are one quantity in two clothings,
   needing conversion, and which are two quantities, needing separation) needs the read.
3. **OQ 55 — the open-void guarantee did not survive the merge.** It closed with the
   guarantee stated in both engines; the engine that stated it as a hard constraint
   (`build/solver.py`) is the one that was deleted. `geometry_cp.py` contains zero
   occurrences of `_void` (verified). What remains is the heuristic's 40-point charge,
   which a candidate can buy its way out of. The accounting survived; the placement
   guarantee did not. `tests/test_voids.py` pins the lapse honestly.
4. **OQ 54 — the default engine under-places and no layer of the critic sees it.** The
   search places the spec Colonial's dining room 26% below its band on every seed, the
   record still reads 12×12, and `plan_check.py` never reads `room.geometry`. The proof
   engine exists and is dispatched from the same `solve()` — but every caller defaults to
   the search, including the workbench's Drawing Set (`corpus.py:182`, `engine="heuristic"`
   hardcoded). `geometry_report.under_band` now reports it; nothing surfaces it.

---

## V — The road to the destination, in order

The order below keeps faith with the documents' own sequence and adds one judgment this
review is prepared to defend: **truth repairs before breadth** — items that make the
system wrong (IV) outrank items that make it smaller than intended.

1. **OQ 52 as a work package.** The fix shape is written; the cost is moving pinned
   expectations on two reference plans, honestly. Fold in OQ 53's two live casing
   dimensions (fixable without the larger address-key ruling). *Needs: a session, no
   ruling — the OQ entries already state the shape.*
2. **OQ 51's adjudication backlog — the ruled next package.** 294 role gaps, 233
   unendorsed, 3,367 inherited pack-arrivals (re-verified this morning; all three
   ratcheted). Work `--unendorsed` in leverage order: `storey-graduation` 38,
   `opening-proportion` 23, `trim-classical` 16, `chambers-ionic` 15, `facade-gable` 14,
   `sash-light` 12, `brick-course` 11. Adjudicating one pack settles every node under it;
   when unendorsed approaches zero, flip inheritance to opt-in. *Needs: authoring
   sessions. Already ruled.*
3. **WP-4.4's offline half.** Give the 322 asset records their `provenance.building`
   names — no network required, and without it every future harvest query degrades to a
   style-name search. *Needs: a session.*
4. **The cheap UI truth items, one small package:** wire the conflict-set panel (the
   engine already produces the sets; move `walk.mjs:93` with it); decide Surface ① (build
   the Console or strike it from `ToolTrace.jsx`); surface `under_band` in the workbench
   findings; consider `engine="auto"` for the Drawing Set. *Needs: one ruling on ①.*
5. **WP-5.3 — generated guidelines, details library, modelling conventions.** The raw
   material is rich (262 pack conflicts, 209 faults with three-tier fixes, 1,556 kit
   parameters) and generatable so it cannot drift. This is the largest remaining named
   deliverable and what a plan-development lead would judge next. *Needs: sessions;
   deferred behind Phase 4 breadth by choice, and that choice can now be revisited since
   breadth closed.*
6. **Rulings queue for Lucas, cheapest first:** OQ 32 (mint finding ids — additive), OQ
   33 (position relaxations — additive, completes P7), OQ 34 (structured decisions), OQ
   38 (four unranked pack ties in the Georgian kit that decide real dimensions), OQ 37
   (the 104-wide fault tie cut), OQ 39 (vertical opening data), OQ 41 (the 2–3.2 ft door
   band that proves but never draws), OQ 40 (the massing-aware footprint — the structural
   fix behind wings), OQ 36 (job registry vs replicas — only if deployment scales).
7. **Environment-unblocks, when the network allows:** WP-4.4's harvest (`www.loc.gov` +
   `tile.loc.gov`), then OQ 7–11 and OQ 18's source half against legible facsimiles —
   starting with the 23 bare single figures, not the 82 categorical calls. None may be
   closed from a secondary source; the standing rule holds.
8. **Partner-gated and scope-only, unchanged:** WP-5.4 (cost — do not author numbers
   without a partner) and WP-4.7 (non-Western trunks, scoping note plus two trial nodes).

What "arrival" means, concretely: when 1–5 are done, PLAN-OF-ACTION §7's paragraph is
true without asterisks except cost and jurisdiction — which are the two clauses the
vision itself gates on a partnership. The system would then be at its stated destination
for a single-partner pilot: brief in, four honest candidates out, drawings a drafter can
open, a guidelines book per style, and a critique whose every conviction was actually
measured.

---

## VI — Doc drift: fixed here, and left with reasons

**Fixed in this branch** (each a claim the tree contradicted):

- `STATE-OF-THE-PROJECT.md`: rooms 58 → 60 (Parts I–II) and the parti figures in Part II;
  Part I's grammar paragraph (36 packs → 57; "158 conflicts … with ranked honest and
  dishonest substitutions" → 262, with the substitution structure honestly named as not yet
  held); facade-role count 56 → 46 and nodes bound 131 → 132 (Part III); Part IV's three
  built-but-listed-unstarted items
  (export, human interface, ingestion) struck through with dates; the CI item (CI exists;
  762 collected tests, not 304); Part V item 3's "none of it exists"; the commit-count
  parenthetical; the appendix row crediting `solver.py` — the file is `geometry_cp.py`,
  and the row now also carries OQ 55's lapse; Part IV's "158 pack conflicts with ranked
  substitutions" (262, and no substitution structure exists in the corpus — the WP-5.2
  audit established that).
- `CLAUDE.md`: three `build/solver.py` references → `build/geometry_cp.py`; the WP-2.3
  report filename corrected to `wp-2.3-the-real-solver.md`.
- `requirements.txt`: the ortools comment named `build/solver.py`.
- `PLAN-OF-ACTION.md`: the progress-board date; the duplicated item 7; item 6's
  mid-package facade figure; the "three open questions want a ruling" paragraph (all
  three since closed, marked so).
- `README.md`: the resurrected "nothing selects on it yet" line under date-conditional
  resolution — WP-1.3 wired `--date` selection; this is the second time this line has
  been repaired, the merge having undone the first (the WP-5.1 report records the first).
- `CHANGELOG.md`: entries appended for WP-4.3, WP-4.5, WP-4.6, WP-5.1, WP-5.2, WP-5.5 and
  the 25 Aug merge (including the solver supersession and OQ 55's partial reopening).
  The existing WP-2.3 entry was left as written — it is a record of what that session
  built, and the merge entry says what survived.
- `workbench/app/src/Chrome.jsx`: "36 packs" now summed live from `/api/overview`'s
  `proportion_packs`, joining the counts that cannot drift.
- `workbench/app/src/surfaces/ExportDetails.jsx`: "158 recorded pack conflicts" → 262;
  the ingestion "forthcoming" card now states that WP-5.5 shipped and points at the
  Transcription surface. `walk.mjs`'s matching pin moved with the count.

**Left, with the reason:**

- The WP-2.3 "forthcoming" conflict-set markers on Brief Intake and the Plan Workbench —
  the UI wiring genuinely does not exist, so the marker is currently true; the fix is
  item 4 of §V, not a text edit.
- `ToolTrace.jsx`'s reference to the Console — needs the Surface ① ruling first.
- The missing `docs/reports/` entries for WP-2.4 and the deployment work — a genuine
  breach of the every-package-ends-with-a-report rule, but backfilling a report two
  sessions after the fact would be a reconstruction, not a record. Named here instead.
- `build/migrate_constraints_wp1_1.py` — a completed one-off migration still in the tree;
  removing project history is not this review's call.
- Every count and status inside historical WP reports — reports are records of their
  moment and are never retro-edited.

---

## VII — What this review deliberately did not do

- **It adjudicated nothing.** Not one of OQ 51's 233 unendorsed gaps was worked; that is
  the next package, ruled, and it deserves sessions that read packs rather than a review
  that skims them.
- **It fixed no live defect.** OQ 52, 53, 54, 55 are described, not patched — each moves
  pinned expectations or needs a formulation decision, and a review that quietly moved
  reference-corpus counts would be the exact failure mode OQ 52 documents.
- **It verified nothing that needs the network.** The environment still refuses
  `loc.gov`, `archive.org`, and `hathitrust`; every blocked item is carried as blocked.
- **It did not re-run the Playwright walk** (the repo does not vendor Playwright); the
  `walk.mjs` edits were verified by keeping every asserted string in sync by hand.
- **It raised no new open questions.** Everything found was either already numbered,
  mechanical (fixed in §VI), or a judgment named in §V's rulings queue. The one candidate
  — the uncommitted UI/UX spec bundle — is recorded in this report's preamble as a
  request to Lucas rather than an OQ, since only Lucas can say whether the bundle still
  exists.
