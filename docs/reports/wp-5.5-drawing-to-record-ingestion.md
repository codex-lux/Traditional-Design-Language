# WP-5.5 — Drawing-to-record ingestion

*25 August 2026. Ruling context: three calls settled with Lucas before the
build — the transcription form lives in the workbench (an eleventh surface,
following WP-5.2's approved divergence); the drafter-DXF importer extracts
candidates and a human completes them in the form (never a guessed record);
and the plan schema gains the structured `provenance` object WP-2.1 asked for,
with `style` staying required on finished records — the form holds the draft
until a human sets it, so "unknown style" needs no schema blessing.*

## What was built

- **`build/ingest_dxf.py`** — the generalization WP-5.1's `import_dxf.py`
  refused to be. An arbitrary drafter's DXF yields *candidates*: closed
  polylines as room shapes (a non-rectangular one becomes its bounding box
  and says so), text inside a candidate as its name hint, everything else
  returned unmatched. Every judgment a drawing cannot state is a **named
  gap** — room types, style, levels, openings, and the wall topology this
  extractor deliberately does not reconstruct. A TDL-emitted sheet
  short-circuits to the WP-5.1 reader and returns the complete,
  cross-checked record.
- **Units, honestly.** `$INSUNITS` trusted when stated (plausibility scored
  and noted); a silent header goes to a room-scale heuristic whose result is
  always labelled an inference; a tie — and a 10 × 8-unit room really is a
  plausible house in feet *and* metres — is a **refusal to pick**, with the
  scores returned and `--units` named as the way out.
- **Plan schema 0.2.0: `provenance`** — source, method
  (`traced`/`dxf-import`/`authored`/`multimodal-reading`), overall and
  per-field transcription confidence, `style_reasoning`, `traced_by`.
  Optional; `additionalProperties: false`; a laundered method fails
  validation. A 17-line schema diff.
- **The Transcription surface (workbench ⑪)** — trace rooms over a browser-
  local backdrop image on the half-foot grid; per-room editors for type
  (catalog datalist), windows (incl. `sill_ft`), doors (with shared-edge
  *suggestions*, never auto-written); a completeness panel that names every
  gap and keeps "check as record" / "send to the bench" / "download record"
  inert until the list is empty. The record that leaves is dims + topology +
  provenance — trace positions are working state and are dropped, the same
  shape as every record in `plans/`. Drafts survive refresh; the backdrop
  deliberately does not.
- **`POST /api/ingest/dxf`** (+ `corpus.ingest_dxf`) — a drafter's file comes
  back as candidates + gaps, a TDL sheet as the record, ambiguous units and
  unreadable files as stated 422s, the missing library as 501.
- **Tests.** 8 in `tests/test_ingest.py` (extraction, units inference and
  refusal, bounding-box honesty, TDL short-circuit, library refusal,
  provenance validation), 4 server tests (39 total), and the e2e walk now
  *traces a room by mouse-drag* and asserts the untyped room appears as a
  named gap. 330 tests in the root suite; frontend builds clean; walk green
  (27 checks).

## What was found

- **The schema has carried `sill_ft` per window since 0.1.0 — and nothing
  ever used it.** No plan in the corpus sets it; no build code read it. Found
  while wiring the window editor; WP-5.1's IFC exporter (a day old) was
  already defaulting a sill it could have read. The exporter now prefers
  `sill_ft`, the form offers it, and OQ 36 was corrected — it had claimed
  "no sill anywhere in the record," which was wrong about the schema and
  right about the corpus.
- **The units-ambiguity refusal case is real, not theoretical.** The first
  draft of the ambiguity test assumed inches and feet would tie; they never
  do (an inch-read room is doll's-house sized). Feet and metres tie — a
  10 × 8 room. The heuristic's refusal-to-pick exists precisely for the one
  collision that occurs in practice.
- **ezdxf coordinates leak numpy scalars.** `area / (w*h) >= 0.9` returns
  `np.bool_`, which survives into JSON-bound fields and fails `is False`
  checks. Caught by the test suite; cast at the boundary.
- **Containment label-matching is enough to keep titles off rooms.** "SHEET
  A-1" outside every candidate lands in `texts_unmatched` rather than
  becoming somebody's name — no heuristics about font size or layer needed
  at this scope.

## What was deliberately not done

- **No wall-topology reconstruction from LINE entities**, no window/door
  extraction from drafter linework, and **no OCR or vectorization of scanned
  images** — the human traces, and the extractor's gap list says exactly
  where its reading stops.
- **The 14 WP-2.1 reference plans keep their prose provenance.** Migrating
  `note` prose into the structured object is a judgment-bearing edit per
  record (confidence phrasing varies), left as a named follow-up rather than
  machine-translated.
- **The backdrop image is never uploaded and never persisted** — a tracing
  aid, not data; losing it on refresh loses no record content. Said in the
  UI itself.
- **Draft storage is browser-local only.** A shared draft store is workbench
  infrastructure the package did not need; the draft file downloads if it
  must travel.
- **No MCP ingest tool** — same call as WP-5.1's export: additive when an
  agent needs it.

## Open questions

None new. OQ 36 (vertical opening data) was corrected rather than extended —
see "What was found."
