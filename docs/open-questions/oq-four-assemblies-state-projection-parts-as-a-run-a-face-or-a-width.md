# oq/four-assemblies-state-projection-parts-as-a-run-a-face-or-a-width — four assemblies write a horizontal run, a face length or a pier width in the field that means a projection, and the plate draws each as a projection

*Status: OPEN · Raised in: WP-14.24 (25 September 2026)*

**Where it comes from.** `oq/casings-are-measured-across-and-drawn-upright` asked two things, and
its ruling of 25 Sep 2026 answered the first: an assembly's `axis` and `zones` are data, and
WP-14.18 and WP-14.24 have built both, so that question is closed. Its second finding was not
ruled, and closing the question would have left it with no home. In that entry's words, *"It is
not one pack"*: four assemblies write something other than a projection in `projection_parts`,
which the schema defines as *"Projection in PARTS, measured from the datum this pack's
projection_datum names"*. Its answer 2 (*"The meaning of `projection_parts` is declared too"*)
was offered beside answer 1 and was not taken.

**The four, re-read at WP-14.24 in each pack's own member note:**

- `proportions/modules/dutch-gambrel.json:36`, *"The projection_parts figure here is the
  horizontal run"* of the lower slope.
- `proportions/systems/facade-pavilion.json:78`, *"The projection_parts figure is the horizontal
  run, not an overhang."*
- `proportions/modules/stone-course.json:78`, *"The projection_parts figure is the FACE LENGTH
  rather than a projection past a datum"*.
- `proportions/systems/facade-arcade.json:46`, *"The projection_parts figure is the pier's WIDTH
  on the face"*.

The first entry's sweep was a regex over notes, so four is a floor and not a census.

**What it does today.** Every surface that reads `projection_parts` reads a projection:
`build/profiles.py`'s wall-datum geometry, and so the Proportions plate (WP-14.9) and, from
WP-14.24, the pack index's thumbnail of each pack's first assembly. So a gambrel's leaning lower
storey, a pavilion roof's run, a stone's face and an arcade pier's width are each drawn standing
off the wall by that figure. Each note flags this for a human reader (*"flagged because a reader
will otherwise take it for an overhang"*). The drawing is not a human reader.

**What would have to be ruled.**

1. **Declare the reading per assembly**, as `axis` was: a field naming what `projection_parts`
   measures on that assembly (`projection`, the default, or `run`, `face-length`, `width`), and
   a plate that draws the other readings as what they are or refuses them by name.
2. **Move the figure to a named field** on those assemblies and leave `projection_parts` meaning
   one thing everywhere. This is larger, because every reader of the field would have to be shown
   not to reach those assemblies (OQ 65 is the precedent for declaring a datum rather than
   re-deriving it).
3. **Leave it**, and caption each of the four plates as drawing a figure the pack says is not a
   projection. This is the cheapest answer and the least honest drawing.

Nothing was changed for this at WP-14.24. The four plates and their thumbnails draw exactly what
they drew before.
