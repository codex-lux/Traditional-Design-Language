# oq/a-furniture-footprint-is-sometimes-one-and-sometimes-the-group — 38 items name a count and nothing says what the rectangle means

*Status: OPEN · Raised in: WP-11.3, the furniture pass (4 September 2026)*

**OPEN — `footprint_in` states one piece for some items and the whole group for others, and no
field distinguishes them.** Thirty-eight of the 278 furniture items name a count in their own
`item` string, and the footprints beside those names do not mean the same thing:

| record | item | `footprint_in` | what it is |
|---|---|---|---|
| `rooms/drawing-room.json` | "sofas, pair, facing" | `[84, 34]` | ONE sofa |
| `rooms/bedroom.json` | "twin beds, pair" | `[100, 80]` | BOTH beds and the 24 in between them, per its own note |
| `rooms/parlor.json` | "six to eight side chairs, set against the walls" | `[20, 20]` | ONE chair |
| `rooms/entry-porch.json` | "two chairs and a small table" | `[72, 30]` | the GROUP |
| `rooms/living-room.json` | "end tables, pair" | `[24, 24]` | ONE table |
| `rooms/laundry.json` | "stacked pair" | `[27, 34]` | one appliance, stacked |

**It did not matter until something drew it.** `plan_check.furniture_shortfalls` asks whether the
room can hold the rectangle, and that question is answerable either way — a room that holds the
group holds one of them. WP-11.3 draws the rectangle, and there the two readings are a parlor
with one chair in it or a parlor with seven, from the same record.

**What WP-11.3 does, which is the conservative reading and not an answer.** It draws exactly what
the record states, ONCE, and the plate says an item naming a count is drawn once. A parlor gets
one chair where its own record says six to eight, and the sheet admits that rather than inventing
the other five. This is "unjudged is not passed" applied to a cardinality: the count is not
known, so it is not asserted.

**What a ruling has to settle.** Whether to author a `count` on the 38 (and, separately, whether
`footprint_in` on those items means the unit or the group — the two are independent, and
`twin beds, pair` shows they can disagree); or to leave the drawing as it is and treat the
catalogue's footprint as always meaning one drawable piece, which would make `twin beds, pair`
and `two chairs and a small table` wrong in the other direction; or to split the offending items
into separate records, which is the largest change and the only one that removes the ambiguity
rather than labelling it.

**The trap, and it is the one this corpus meets most often.** A count is derivable from the item
string by regex — "pair", "two", "six to eight" — and that is exactly the shape of guess
`plan_check` had been making about `placement` until WP-7.2 authored all 278 and deleted it, and
exactly what WP-11.3 refused again when it authored `kind` rather than pattern-matching the
names. Deriving the count from the name would be the third instance. Whatever is ruled, the
answer belongs in the record beside the item.
