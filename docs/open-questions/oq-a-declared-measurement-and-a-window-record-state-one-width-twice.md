# oq/a-declared-measurement-and-a-window-record-state-one-width-twice — the plan says how wide its windows are in two places that nothing holds together

*Status: OPEN · Raised in: WP-9.2 (1 Sep 2026)*

**The finding.** A plan record states a window's width twice. `measurements.window_opening_width_in`
is a declared figure the fault corpus reads (`window-squarer-than-the-style-permits` divides it
by the height); `levels[].rooms[].windows[].width_ft` is the per-room record the placement
seats and the renderers draw. Both shipped plans declare both. Nothing compares them, and
nothing derives one from the other: `plan_check` reads the measurement, `openings.place` reads
the window record, and a house can be convicted of a squat window on a figure no drawn
window has.

**How it surfaced.** `narrow-the-window-and-keep-the-height` executes the fault's own cheap fix
(*"Narrow the window and keep the height"*). Written naively it would move the measurement
and leave every drawn window as it was — clearing the fault on paper while the sheet still
showed the window the fault was about, which is the silent-overwrite class WP-6.2 removed. So
the move writes the measurement AND every `windows[].width_ft` in one application, and
`check_moves.py`'s allow-list admits both paths for it. That is the loop keeping the two
records together by hand, once, for one move; it is not the record keeping itself together.

**What is asked.**

1. Should `window_opening_width_in` be DERIVED from the window records (the widest, the
   modal, or the principal-room's) rather than declared beside them — the way
   `elevation.py` derives most of what the fault corpus reads — so that a declared figure
   cannot disagree with the drawn one? If so, a plan declaring it becomes a
   `drawn-vs-declared` finding rather than a fact.
2. If both stay, should `plan_check` compare them and report the disagreement, as the drawn
   layer already does for a room's declared and drawn area?
3. The same shape exists for `window_opening_height_in` against `window_head_ft` and a room's
   `window_sill_ft`, and for `porch_clear_depth_ft` against the porch room's own dimensions.
   Which measurement names in the shipped plans are second statements of a field the record
   already carries? Nobody has counted.

**What is not asked.** Whether a measurement the plan did not declare may be written by the
loop — that is refused by the ruling recorded in `oq/the-revision-loops-authority-over-topology`
and by `moves/registry.json`'s `refusals` block, and stays refused.
