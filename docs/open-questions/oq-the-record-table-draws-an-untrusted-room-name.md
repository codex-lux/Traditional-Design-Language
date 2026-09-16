# oq/the-record-table-draws-an-untrusted-room-name — and the sheet has no width for it

*Status: OPEN · Raised in: WP-13.7, the adversarial audit of Phase 13 (16 September 2026)*

**`render_plan.render` draws `WHAT THE RECORD ASKED FOR` as one `<text>` per diverged room, and
the row carries that room's `name` with no cap, no wrap and no truncation. A 2,000-character
name puts the table's ink 7,521 px outside a 2,348 px canvas, where a reader never sees it —
under a heading promising the disclosure.**

## What was measured

WP-13.x made the column pitch honest. `TABLE_COL_W` was a flat 260 px that nothing measured the
rows against, so twenty of the Tidewater sheet's twenty-four rows overprinted their neighbour's
first characters and the plate read `record 17' x 20' (+45%)ntry: drawn 5'-9" x 9'` — a table
that silently ate the front of "Butler's Pantry". The pitch is the widest row plus a gutter now,
floored at 260. That fix is right for the twenty-four real rows.

Measured here on `plans/tidewater-georgian-careful.json`, `engine="heuristic"`, by renaming one
room and reading the rendered SVG back through the renderer's own `_text_w`:

| room name | canvas | rightmost table ink | overrun |
|---|---|---|---|
| as shipped (control) | 2348.0 px | 2072.4 px | **−275.6** — fits |
| 200 characters | 2348.0 px | 1229.6 px | −1118.4 — fits; the table collapses to ONE column |
| 2,000 characters | 2348.0 px | **9869.6 px** | **+7521.6** |
| 20,000 characters | 2348.0 px | **96269.6 px** | **+93921.6** |

**And the honest pitch fix made the failure QUIETER.** At the flat 260 px a long row overprinted
— visible, ugly, and a reader could see that something was wrong. With the pitch measured from
the rows, the column count collapses to one and the long row runs cleanly off the edge, where
nobody sees it at all. The residue fails in the direction this corpus names as the dangerous one.

## It is reachable, and nothing guards it

- `schema/plan.schema.json` types a room's `name` as a bare `{"type": "string"}` — **no
  `maxLength`** — so WP-10.1's gate (`app._plan`) admits it. CLAUDE.md already records that
  `POST /api/drawings` *"takes a plan record verbatim from anyone who can reach it"*.
- `tests/test_sheet_canvas.py::test_no_drawn_rect_leaves_the_declared_canvas` reads **rects**.
  No assertion in the tree reads this block's geometry, which the pitch fix's own comment says
  in as many words.
- **Both label fitters already cap.** CLAUDE.md: *"A room name is an untrusted string and the
  label fitter was O(W³) … Both fitters cap at twelve words and chunk beyond it."* The table was
  ported from main's WP-11.1 at the 8 Sep merge and never got that treatment.

## What has to be ruled

1. **What does a plate do with a name it cannot fit?** Truncate with an elision mark — and then
   the table names a room by a string that is not its name; WRAP the row — and then the table's
   height stops being `11.0 * rows` and the canvas arithmetic moves; or CLAMP the pitch to the
   canvas and let long rows overprint again, which is the state the fix removed.
2. **Or does the RECORD refuse it?** A `maxLength` on `properties.name` answers it at the gate
   for every reader at once — the two label fitters, this table, the schedule and the DXF —
   rather than once per surface. That is the wider answer and probably the right one, and it is
   a schema change carrying a number nobody has sourced.

## What was deliberately not done

**Nothing was changed.** A clamp that binds only above the canvas width is available and is
byte-identical on all sixteen shipped sheets — no shipped name comes near it — but which of the
three behaviours is correct is a judgment about what a drawing SAYS, not a defect with one fix,
and choosing one here would put a rule on the plate that no record states. The measurement is
published instead.
