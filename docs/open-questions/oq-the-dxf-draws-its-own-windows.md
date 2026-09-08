# oq/the-dxf-draws-its-own-windows — a downloaded DXF is a different drawing of the same house, today

*Status: OPEN · Raised in: WP-11.15's adversarial audit (8 September 2026)*

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
