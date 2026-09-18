# oq/the-title-block-states-the-main-block-as-the-house — 1,665 sf of a 2,511 sf house

*Status: OPEN · Raised in: WP-13.7's verification pass, by looking at the sheet (16 September 2026)*

**The Tidewater sheet's title line reads `45' x 37' CLEAR · 1665 SF GROSS`. The record's own
`footprint.blocks` sum to 2,511 sf and its own `built_extent_width_ft` is 79.0 ft.** The line
understates the house by **33.7%** and its width by 34 ft — and the sheet draws the wing it is
leaving out, twelve inches to the left of the sentence.

    block            role         x        size            area
    main             main          0.0     45.0 x 37.00    1665 sf
    service-hyphen   hyphen       -7.0      7.0 x 18.00     126 sf
    service          dependency  -34.0     27.0 x 26.68     720 sf
                                                           ----
                                                           2511 sf

`render_plan.py:1278` writes `{_fmt(W)} x {_fmt(H)} CLEAR · {fp.get("area_sf","?")} SF GROSS`,
where `W, H = fp.get("width_ft"), fp.get("depth_ft")` (line 973) and `area_sf` is
`round(b["W"] * b["H"])` for the MAIN BLOCK (`geometry.py:2444`). Every figure on that line is
the main block's.

## Why now

This is the family `oq/a-massing-element-is-placed-and-nothing-below-the-placer-knows-it` records,
arriving at the most visible surface there is. It was unreachable until WP-13.5 put a real
dependency on a shipped plan: on a one-rectangle house the main block IS the building and the
line is exactly right. **It was found by rendering the sheet and looking at it**, which is this
repository's own highest-yield technique and is now nine packages running.

## What must be ruled, because two of the three figures are defensible

1. **`1665 SF GROSS` is not defensible.** Gross area of a house is the house. Whatever is decided
   about the other two, this figure is wrong by a third on a shipped plate.
2. **`45' x 37' CLEAR` may be right.** A Georgian block has a size and stating it is what a
   measured drawing does; the wing is dimensioned in the drawing. But the line does not say
   *main block*, so a reader has no way to know which it is.
3. **`5 BAYS OF 9 FT` is certainly the main block's and is certainly right** — the bay system is
   the block's and the dependency has none.

So the question is not "make it read 2,511": it is what a title block on a five-part house states,
and the answer may be two lines rather than one.

## What must not happen

- **Do not silently swap `area_sf` for the sum of the blocks.** It moves all sixteen shipped
  sheets and `CORPUS_SHEET_SHA`, which was re-pinned on 16 Sep with its movement accounted per
  file; a second unaccounted movement in the same week is how that pin stopped meaning anything
  the first time.
- **Do not state a figure the record does not carry.** There is no `gross_area_sf` on the
  footprint — `fp.get("gross_area_sf")` is `None` — so whatever is decided has to be written by
  the layer that knows the blocks, not summed in the renderer.
- **Do not read this as the container being wrong.** WP-13.5 put the service programme where the
  ruling said; the title line simply never learned that a house can have more than one mass.
