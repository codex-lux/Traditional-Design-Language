# Ingestion — drawing to record (WP-5.5)

The path by which HABS sheets, the reference corpus and a builder's back
catalogue flow into the critic. Two entrances, one discipline: **a human makes
every judgment; extraction only ever proposes.**

## The Transcription surface (workbench ⑪)

A drawing goes in; a record comes out. Load a scanned drawing as a backdrop
(it stays in the browser — never uploaded), state its real-world width, and
trace room rectangles over it on the half-foot grid. Each room then needs what
a drawing cannot state: its type from the room catalog, its windows and doors,
its level. The **completeness panel names every gap** between the draft and a
schema-valid record — an untyped room, a duplicate id, a door to a room that
is not there, an unset style — and the export buttons stay inert until the
list is empty. Then: check it as a record (the same `/api/plan/evaluate` the
bench uses), send it to the bench, or download it.

The draft is not a record. Trace positions are working state — they derive
clear dims, `exterior_walls` (the envelope-touching test `render_plan.py`
uses) and door *suggestions* from shared edges — and the record that leaves is
dims + topology + provenance, the same shape as every record in `plans/`.
Drafts survive a refresh (localStorage); the backdrop image deliberately does
not (it is a tracing aid, not data).

## The drafter-DXF extractor

```
python3 build/ingest_dxf.py drawing.dxf [--units ft|in|mm|cm|m] [--out draft.json]
POST /api/ingest/dxf {dxf: "<file text>", units?}
```

`build/ingest_dxf.py` is the generalization WP-5.1's `import_dxf.py` refused
to be. Facing an arbitrary drafter's file it **extracts candidates**, per the
ruling — extract, then complete in the form:

- **closed polylines** become candidate room shapes, scaled to feet and
  normalized to a SW origin; a non-rectangular one is taken as its bounding
  box *and says so on the candidate*;
- **text entities** whose insert point falls inside exactly one candidate
  become its name hint; everything else (sheet titles, notes) is returned
  unmatched, never forced onto a room;
- **everything a drawing cannot state is a named gap**: room types, the
  style, levels and ceilings, windows and doors, and the wall topology this
  extractor deliberately does not reconstruct from LINE soup.

A TDL-emitted plan sheet (it carries the `TDL-META` marker) short-circuits to
`import_dxf.read_plan_dxf` and comes back a complete, cross-checked record —
the workbench sends it straight to the bench.

## Units, honestly

`$INSUNITS` is trusted when stated and plausible (a poor plausibility score is
noted, with `--units` as the override). A **silent header goes to the
room-scale heuristic**: each unit hypothesis is scored by the fraction of
candidate sides landing in a plausible room range (4–60 ft), and the result is
always labelled *"inferred by the room-scale heuristic … an inference, not a
fact of the file."* When no hypothesis clearly wins — a 10 × 8-unit room is a
plausible house in feet *and* in metres — the extractor **refuses to pick**,
returns the scores, and asks for `--units`. Unjudged is not passed, applied to
a number as basic as the unit of measure.

## Provenance (added at plan schema 0.2.0; the schema is 0.5.1 now)

*That parenthesis said 0.3.0 through the 0.4.0, 0.5.0 and 0.5.1 bumps. A version number in prose has no guard -- `check_counts.py` polices figures derived from the CORPUS and a schema version is not one -- so it is the "until X lands" class WP-6.4 records, in a heading. Corrected while bumping to 0.5.1, and named here so the next bump corrects it rather than adding to it.*

The structured provenance WP-2.1 asked for, after carrying `source_image`,
confidence and the style reasoning as prose in `note`. Optional on every
record; an ingested one should carry it:

```json
"provenance": {
  "source": "HABS VA-1234 sheet 2",
  "method": "traced | dxf-import | authored | multimodal-reading",
  "transcription_confidence": "high | medium | low",
  "field_confidence": {"levels.0.rooms.kitchen.windows": "low"},
  "style_reasoning": "five-bay symmetry, river-front pediment",
  "traced_by": "…"
}
```

The form writes it as you work — importing a DXF sets `method: dxf-import`
and seeds `source` with the filename — and the style field's reasoning box
sits beside the style picker, because a traced record's style is a judgment
and the reasoning rides with it. The 14 WP-2.1 reference plans still carry
their provenance as prose; migrating them is a follow-up, noted in the WP-5.5
report, not silently done by machine.

## What is deliberately not attempted

No OCR or auto-vectorization of scanned images — the human traces. No wall
topology from LINE entities, no window/door extraction from a drafter's
linework — placement of openings is exactly the kind of reading a drawing
rewards a human for. Each of these is stated where it bites: in the
extractor's gap list and refusals, not in silence.
