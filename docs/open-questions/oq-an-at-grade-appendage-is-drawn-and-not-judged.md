# oq/an-at-grade-appendage-is-drawn-and-not-judged — the terrace is on the sheet and held against no band

*Status: OPEN · Raised in: WP-11.10, the terrace at grade (7 September 2026)*

**OPEN — WP-11.10 places the terrace, seats the door the record has always declared to it, and
draws it. It does all of that WITHOUT giving the room a `geometry`, which is the whole mechanism
of the ruling that made the package small. The cost is exact and it is stated here rather than
absorbed: `plan_check`'s drawn layer reads `room.geometry`, so the rectangle now on the sheet is
held against no band, no area, no proportion and no furniture fit — and every other drawn
rectangle in this corpus is.**

## Why there is no geometry, which is the part not to undo

Ruled 7 September 2026: an at-grade unroofed appendage is **not a massing element**. It is a
plan-level record on `plan.threshold`'s precedent. Three filters then keep every layer below the
placer blind to it *by construction*, and each one is load-bearing:

| layer | filter | what a rectangle would do |
|---|---|---|
| `structure.wall_lines` | `placed = [r for r in level_rooms if r.get("geometry")]` | four exterior walls round a terrace, and a clear span measured across it |
| `plan_check` `rooms_unplaced` | `takes_a_rectangle(type)` | its own WP-11.6 comment names the terrace as the CORRECT `is_placed == False` case |
| `geometry._record_prep` / `blocks_record` | `is_placed(r["type"])` | terrace area inside a massing element, and `footprint.blocks` describing a rectangle no room occupies |

Writing `room.geometry` would reopen all three, and WP-11.9's six taught layers with them. It
would also be **invisible**: the drawing would look exactly the same. `tests/test_appendages.py::
test_no_appendage_room_is_given_a_rectangle_and_that_is_what_keeps_six_layers_blind` exists for
that reason, and a mutation writing the rectangle turns it red.

## What is therefore not judged

On the four placed appendages: 14 × 22, 10 × 24, 10 × 16 and 12 × 40 ft of drawn terrace, against
`rooms/terrace.json`'s own `area_sf [120, 600]`, `width_ft [10, 30]`, `length_ft [12, 40]` and its
`critical_dimension` — *"Depth. A terrace under 10 ft cannot hold a table and a passage behind the
chairs"*. Also unjudged: whether the drawn rectangle overlaps anything (a stoop, another
appendage, a lot line), and whether its furniture fits.

**Nothing is LOST by this.** Every one of those bands is already applied to the DECLARED record —
`bad-07`'s two 8 ft decks carry `serious room` and `serious furniture` findings today, exactly as
they did before the package. What is missing is the DRAWN half, and the drawn half is only ever
different from the declared one where the pass clamps a run to the element's face. On the shipped
corpus that has happened zero times of four.

## What must be ruled

1. **Does the drawn layer get a second reader, or does the appendage get a rectangle it keeps out
   of the other three?** The first is a `drawn_appendages` pass in `plan_check` reading
   `plan["appendages"]` — no new field, and the fit arithmetic already lives in ONE function
   (`plan_check.furniture_shortfalls`, WP-9.6) with two callers, so a third caller is the shape
   the corpus already uses. The second is a `geometry` on the room plus an `at_grade: true` beside
   it that the three filters test — which is a fourth thing for three readers to agree about, and
   this corpus has been bitten by that every time.
2. **Is a clamped run a finding?** A terrace the record declares at 22 ft and the placement draws
   at 15 is the OQ 52 family if it is silent. It is on the record as `figures.run_ft.clamped`
   with `need` and `have`, and no layer reads it.
3. **What holds an appendage against a lot line?** `geometry_report.lot_extent.at_grade` publishes
   the ground the appendages cover (74.0 ft against a built extent of 60.0 on
   `tidewater-georgian-careful`) and `fits_lot` is deliberately measured WITHOUT it, per WP-11.9's
   ruling 2 that the cap is on the built extent. Two numbers, and no rule yet about which a
   setback is held against.

## What is NOT the question

Whether the terrace should be a massing element — ruled, it should not, and
`oq/the-proving-engine-cannot-place-a-second-massing-element` is untouched by this package and
still gates the shipped-record dependency tags. Nor whether the appendage should be drawn: it is,
and `rooms/terrace.json`'s own note remains correct about the block.
