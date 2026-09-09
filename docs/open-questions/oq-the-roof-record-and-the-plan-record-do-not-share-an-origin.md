# oq/the-roof-record-and-the-plan-record-do-not-share-an-origin — and nothing drew both until now

*Status: OPEN · Raised in: WP-12.1, building the scene record (9 September 2026)*

**`roof.py` lays the roof out from (0, 0) over the OUTSIDE footprint. `structure.py` lays the
walls out from (0, 0) over the CLEAR one. Both call their corner the origin, and the two
corners are half an exterior wall apart.**

Measured on `tidewater-georgian-careful`:

| | frame | extent |
|---|---|---|
| `wall_lines` / room rectangles | clear | 0 → 63.00 × 0 → 38.17 ft |
| `roof_outline`, `elevation_profile` | outside | 0 → 65.58 × 0 → 40.75 ft |
| `export_ifc.slab_boxes` | outside, **centred on the clear** | −1.29 → 64.29 × −1.29 → 39.46 ft |

Read literally, the roof sits **1.29 ft east and north** of the house it covers, and the IFC
slabs sit somewhere else again — correctly, as it happens, and by a convention nobody wrote
down as a convention.

## Why it has never mattered, and why it does now

No surface has ever drawn a roof and a room in one picture. `render_plan.py` draws rooms,
`render_roof.py` draws a roof plan, `render_section.py` cuts a stack of storeys, and each is a
separate plate at a separate origin, so the offset has never been visible to anybody. The two
records were only ever read one at a time.

The scene layer is the first thing that has to put them in one coordinate system, and in three
dimensions the offset becomes a roof visibly sliding off its walls. WP-12.1 resolves it by
FOLLOWING `slab_boxes` — the plan frame is the authority, because `plan.schema.json` defines
the origin as the block's SW corner, and the outside envelope is centred on it. That is a
choice this layer made to be able to draw at all, and it is the third convention in the tree
rather than the second.

## What is actually being asked

**Which record should move, and who owns the frame?** Three readings, and nothing in the corpus
settles between them:

1. **The plan frame is the authority and the roof record is wrong.** `roof.py`'s outline and
   silhouettes would be re-emitted at (−t, −t), so every consumer gets a roof over its house.
   The cost is that `render_roof.py`'s plate moves, and its own coordinates have been read and
   pinned by tests.
2. **Both are right about their own drawing and the frame belongs to the reader.** Each record
   states which footprint it was laid out over, and a consumer that combines them converts.
   That is what the scene does today, and the cost is that the conversion is a fourth place
   where a half-thickness can be got wrong.
3. **The clear/outside distinction should not be in coordinates at all.** `structure.py`'s own
   note says rooms keep clear dimensions "while the footprint becomes outside-to-outside" — the
   two frames are the record of that decision, and a single frame with the thickness carried as
   a property would remove the question rather than answer it.

## The smaller finding underneath, which is not the same question

`section.footprint` and `export_ifc.slab_boxes` disagree about the outside depth by **0.17 ft**
on the same plan — 40.58 against 40.75 — because one grows `clear_depth_ft` (38.0, rounded) and
the other grows `geometry.footprint.depth_ft` (38.17, as placed). Neither is wrong on its own
terms and both are called the outside footprint. The scene reports its own agreement figure
rather than choosing, and the residue is that 0.001–0.004 ft.

**Do not close this by rounding one to the other.** Which of the two is the depth of the house
is exactly the question, and a checker made green by a rounding is the shape this corpus
records at OQ 48.
