# oq/the-dxf-draws-its-own-windows — a downloaded DXF is a different drawing of the same house, today

*Status: CLOSED 27 Sep 2026 · Raised in: WP-11.15's adversarial audit (8 September 2026)*

**On the shipped, untagged `tidewater-georgian-careful`, the DXF draws 16 windows on the ground
floor and the sheet draws 15.** This is not gated on a `block` tag and not a consequence of any
recent package: it is live on the corpus as it stands.

## The measurement

Taken directly, `engine="heuristic"`, on the record as committed:

| surface | ground-floor windows |
|---|---|
| `render_plan.derive_openings` (the sheet, and `derive.js` with it) | **15** |
| `export_dxf.export_plan_dxf` (the download) | **16** |

## The cause: a fifth spelling of where a window goes

`build/export_dxf.py:290-309` does not read the openings the placement produced. It re-derives
them:

```python
cnt = win.get("count") or 1
for k in range(cnt):
    t = (k + 1) / (cnt + 1)                       # evenly spaced across the ROOM
    if wall == "S" and g["y_ft"] <= 0.6:          # boundary against the FOOTPRINT
```

Two independent departures from the record in four lines:

1. **It spaces windows evenly** (`t = (k+1)/(cnt+1)`) instead of reading `positions_ft`, which
   `openings.place` wrote and which both renderers read. WP-6.2 put those on the record precisely
   so each renderer would stop inventing one.
2. **It tests the boundary against the footprint**, which is the defect WP-11.14 removed from the
   two renderers — so on a tagged record it will also drop every window on a dependency or hyphen.

## Why this is the WP-6.4 finding surviving

WP-6.4 found that a reader looking at a CP-proved sheet **downloaded a DXF of a different
placement of the same house**, and fixed it at the placement level: `corpus._placed()` places once
and every sheet takes it. That fix made the two surfaces agree about *where the rooms are*. It did
not make them agree about *where the windows are*, because the DXF never consulted the opening
records at all. One building, two window schedules, still.

`openings.required_wall_ft` is the precedent for the fix — one arithmetic, several callers — and
this is the fifth place the question "where does this opening sit" is answered.

## What must be ruled

1. **Does the exporter read `positions_ft`, or is even spacing a deliberate CAD convention?** The
   record's positions come from a placement that avoids doors and obstructions; even spacing does
   not. Nothing in the corpus states that a DXF should differ, and the plate does not say so.
2. **What happens to a window the placement REFUSED?** The sheet counts it (`offFootprint`) and
   says so in the schedule. The DXF currently draws its own, which means the download can show a
   window the sheet explicitly declined to draw — the more serious direction.
3. **The same file's boundary test needs WP-11.14's `edge_ft` treatment** before any plan carries
   a `block` tag, or the DXF will silently drop every dependency window.

## Why it was not fixed in WP-11.15

That package's subject is a span published over a storey that does not exist, and its guarantee is
that no shipped output moves. Fixing this **moves the DXF for both shipped reference plans**, which
is a second thing, in a second subsystem, needing its own before-and-after. WP-11.9's rule applies:
a package that does two things can only be reasoned about as one.

**Do not fix it by making the sheet match the DXF.** The sheet reads the record; the DXF invents.
The record is the authority, and the direction of the fix is not symmetric.

## Closed, 27 Sep 2026: the DXF draws the sheet's windows (the adversarial audit of Phase 14)

Auditor D re-measured this question on the audit's own tree and found its figures stale. The
Tidewater record it cites is refused now, so it cannot be exported. On the twelve drawable
reference plans five differed in COUNT alone: bad-07 4 against 2, good-01 9 against 8, good-02 12
against 9, good-04 5 against 2, good-05 12 against 11. Held line by line at a tolerance of one
foot, across all sixteen records exported from their placement, the unfixed exporter disagreed
with the sheet on **8 of 16 plans**. It drew **19** units the sheet refuses or places elsewhere,
and missed **12** units the sheet draws.

**The fix reads the sheet's own derivation and invents nothing.** `export_plan_dxf` draws exactly
the windows `render_plan.derive_openings` gives the sheet (through `openings_of_level`). Each
stands at the sheet's `at_ft` along the wall, on the room's own face (`edge_ft`, which is question
3 above). It looks up only each unit's identity in the record, meaning which window of the room
and which unit of its count, because the XDATA carries that and `import_dxf` holds the drawing to
the record by it. A unit the sheet does not draw is not drawn (question 2). It is listed as
`windows_not_drawn` with the record's own reason, and a note under the plan counts it. After the
fix the comparison is 0 and 0 on all sixteen, and the round trip reads every drawn line back.
`tests/test_dxf_windows_are_the_sheets.py` is the guard. It fails on the unfixed exporter, both on
the lines and on the unsaid units.

**Question 1 was not ruled; it was answered by a ruling that already stood.** The question asked
whether even spacing might be a deliberate CAD convention. Nothing in the corpus says so, and
WP-6.4's ruled rule, *"one drawing set is one building or it is nothing"*, says the opposite. The
same audit applied it to the IFC export's windows and doors (D-F7), which had the identical
defect. No new ruling was taken here. If a CAD convention that departs from the record is ever
wanted, it is a new question, and this entry is its precedent.

The same change found a second defect in the file, and it too is fixed. The notes under the DXF
plan were set at fixed multiples of the title height, 7 in apart for 8 in text. The no-module
note the audit's D-F9 added and the undrawn-doors note therefore printed through one another. They
are now set one below another.
