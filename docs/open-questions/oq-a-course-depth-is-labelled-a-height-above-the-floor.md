# oq/a-course-depth-is-labelled-a-height-above-the-floor — two packs state a belt course's own depth under the name of its height above the floor

*Status: OPEN · Raised in: WP-16.2, the adjudication (30 September 2026)*

**Two pack rules state the depth of the course itself, under the dimension and the label that
three other packs use for the course's height above the floor.** On 77 buildable nodes one of the
two governs the slot, so the served resolved kit gives a depth of a few inches as the belt
course's height above the floor.

| pack | dimension | quantity | expression | what its own note says it is |
|---|---|---|---|---|
| `stone-course` | `height` | `belt_course_height_above_floor` | `module * 0.8` | "7 1/4 in of dressed string course" (the course's own depth) |
| `vignola-composite` | `height` | `belt_course_height_above_floor` | `module / 2` | the belt "should read as the pedestal plinth of the order above [...] Half a module is the minimum that will do that" (a band depth) |
| `brick-course` | `height` | `belt_course_height_above_floor` | `round((storey_height + part * 0.6) / part) * part` | the course line nearest the second-floor structure (a height above the floor) |
| `storey-graduation` | `height` | `belt_course_height_above_floor` | `storey_height + part * 0.6` | the belt "sits at the second-floor STRUCTURE" (a height above the floor) |
| `facade-picturesque` | `height` | `belt_course_height_above_floor` | `storey_height * 0.72` | "HEIGHT OF THE PRINCIPAL DATUM above the finished first floor" |

The corpus already has a name for the band's own depth: `belt_band_own_depth`, the dimension and
quantity `brick-course` (`part * 2`) and `facade-classical` (`part * 1.0`) use for it.

## Why nothing saw it

- `check_addresses.py` judges a collision by its LABEL. That is WP-15.6's finding, where
  sash-light and timber-bay wrote two quantities to one address under one label. These five rules
  carry one label, so the checker reads agreement.
- `resolve_kit.choose_pack` groups a slot's rows by (dimension, quantity). So a depth and a height
  compete for one quantity, and the winner is delivered under the height's name.
- The independent check of WP-16.2's neo-eclectic record found it. That record frees the belt
  course, and `stone-course`, bound on italian-villa-vernacular, takes the address over the node's
  own `facade-picturesque`, the one rule there that really is a height above the floor.

## Measured (30 September 2026, `check_inheritance.governed` over the buildable nodes)

- `stone-course` governs `belt_course` on **64 nodes**. Before WP-16.2 it was 60: the adjudication
  freed the belt course on colonial-revival, dutch-colonial-revival, garrison-revival and
  neo-eclectic, and the cascade delivered it there.
- `vignola-composite` governs it on **13**, unmoved.
- So **77 nodes** carry a course or band depth as the belt's height above the floor. `module * 0.8`
  is 7.2 in on a 9 in module, against a storey-height figure of the order of 100 in.

**No drawing reads it.** The elevation takes the belt from `brick-course` or `facade-classical`
directly (`elevation.water_table_and_belt`), whatever the governed pack
(`oq/the-elevation-reads-five-packs-whatever-the-style-binds`). The mislabel lives in the resolved
kit a reader is served: the Dossier's slot page and `tdl_resolve_kit`.

## What would have to be decided

1. Whether both rules move to `belt_band_own_depth`, OQ 48's remedy of a named dimension for the
   minority meaning. That is the corpus's precedent, and it moves the resolved belt course on all
   77 nodes. Each would then take its height from the next pack by precedence, or from none, and
   each should be read again.
2. Whether the height-above-floor address wants a guard that reads the figure rather than the
   label, for example a floor of the order of a storey. A label cannot tell a depth from a
   height, and the checker that judges by label is what let this stand.

Not done in WP-16.2: the ruling it carries out is about bans, and moving 77 resolved slots is a
package of its own.
