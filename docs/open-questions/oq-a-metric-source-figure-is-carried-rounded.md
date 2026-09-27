# oq/a-metric-source-figure-is-carried-rounded — six measured kit figures round the millimetres their notes quote

*Status: OPEN · Raised in: WP-14.5, the source leg (27 September 2026)*

**Census N3 reads 66 measured kit parameters that the elevation reads and whose note states a
figure about them. 60 agree and 6 disagree, and all six disagree for the same reason.** The note
quotes a metric figure, and the parameter carries its conversion rounded to a tenth of a foot or
to a whole inch. The largest difference is 1.6 per cent.

| kit | slot · parameter | the note | exact | the record |
|---|---|---|---|---|
| `cotswold-vernacular` | `window_lite_pattern` · `light_height` | 600–900 mm | 1.97–2.95 ft | 2.0–3.0 ft |
| `cotswold-vernacular` | `window_lite_pattern` · `light_width` | 300–450 mm | 0.98–1.48 ft | 1.0–1.5 ft |
| `english-cottage-vernacular` | `window_proportion` · `opening_height` | 700–1200 mm | 2.30–3.94 ft | 2.3–3.9 ft |
| `english-cottage-vernacular` | `window_proportion` · `opening_width` | 600–1000 mm | 1.97–3.28 ft | 2.0–3.3 ft |
| `spanish-classical` | `door_surround` · `relief_depth_max` | 600 mm, *"converted to inches"* | 23.62 in | 24 in |
| `swiss-chalet` | `porch_depth` · `gallery_depth` | 1.0–1.5 m | 3.28–4.92 ft | 3.3–4.9 ft |

- **The stakes are small.** On a drawing, no edge moves by more than about four tenths of an inch.
- **Why it is a question and not a tolerance change.** The census compares at the notes' own
  precision: 0.01 of the unit, or half a per cent, whichever is larger. That is the rule every
  other check here keeps. Widening it until these six agree is the move this corpus refuses,
  loosening a guard until the reds go away.

## Two readings

1. **The source states a figure, so the parameter should carry its exact conversion.** That means
   six data edits and six figures moving by less than a centimetre. It is the craftsman casing's
   precedent in WP-14.5, where the record was corrected to the figure its own note cited.
2. **A rounded band is the honest transcription at the kit's precision.** The kits carry bands to a
   tenth of a foot throughout. On this reading the check should compare a converted band at the
   precision the parameter is written to. That is a rule about the instrument and needs a ruling,
   because it would apply to every parameter and not only to these six.

What decides between them is whether any drawing, check or fault reads these six figures to
better than a tenth of a foot. That has not been measured. All six are among the parameters the
elevation reads, which is why N3 holds them at all.

## Where it lives

- Census N3.
- `build/note_figures.json` (the `kits` table).
- The four kits named above.
