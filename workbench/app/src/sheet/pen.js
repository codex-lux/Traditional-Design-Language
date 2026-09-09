/* The pen — Graphic Standard No. 1's five weights, in one place.

   WHY THIS FILE EXISTS. `tokens.css` has carried the ladder since WP-5.2 —

     --lw-construction .7px   grids, extensions, guides: left visible
     --lw-fine        1.05px  furniture, fixtures, hatching, stairs
     --lw-medium      1.6px   openings, trim, unseen edges
     --lw-heavy       2.4px   profile: where mass meets air
     --lw-cut         3px     the knife of plan & section; bounds all poche

   — with the rule that weight and tone fall together ("a lighter line is drawn lighter in
   tone as well as width, the way graphite actually behaves"), and `Sheet.jsx` used NOT ONE
   of them. Every stroke width in that file was an inline literal: 2.6 for the cut line,
   1.4 for a partition and a door leaf, .8 for a swing arc, .45 for a triangle. Nineteen
   numbers, none of them the standard's five, in a system whose entire grammar is line
   weight.

   THESE ARE `style` OBJECTS AND NOT ATTRIBUTES, AND THAT IS THE WHOLE MECHANICAL POINT.
   `var(--lw-cut)` does not resolve inside an SVG presentation attribute — `strokeWidth="var(…)"`
   is an invalid attribute value and the browser drops it, which would have made every stroke
   on the sheet fall back to 1px in silence. It resolves in a style declaration. So a mark
   spreads `style={PEN.cut}` and never `strokeWidth=`.

   `vectorEffect="non-scaling-stroke"` stays an ATTRIBUTE on every mark. It is not a weight,
   it is what makes a weight a weight — "a pen is a pen" — and `e2e/walk.mjs`'s pen check reads
   COMPUTED style, so it is indifferent to which of the two carries it. */

const w = (weight, ink) => ({ stroke: `var(--draw-${ink})`, strokeWidth: `var(--lw-${weight})`,
                              fill: 'none' });

export const PEN = {
  /* the knife of plan and section; bounds all poche */
  cut: w('cut', 'cut'),
  /* profile — where mass meets air */
  profile: w('heavy', 'profile'),
  /* openings, trim, unseen edges */
  medium: w('medium', 'seen'),
  /* furniture, fixtures, hatching, stairs */
  fine: w('fine', 'fine'),
  /* grids, extensions, guides: left visible */
  construction: w('construction', 'grid'),
  /* dimensioning has its own ink in the standard and the construction weight */
  dim: { stroke: 'var(--draw-dim)', strokeWidth: 'var(--lw-construction)', fill: 'none' },
};

/* A mark whose INK is a duty rather than a weight — the drag handle in gilt, a selected room
   in salmon. The weight still comes from the ladder; only the tone is stated, and it has to be
   one of the standard's named duties rather than a colour someone liked. */
export function inked(pen, token) {
  return { ...pen, stroke: `var(--${token})` };
}

/* Poche: the wall is a body. Masonry at working scale is salmon flesh in a coal skin;
   a partition is the pale warm field. Both are bounded by the cut line, which is what
   `--lw-cut`'s own note in the standard means by "bounds all poche". */
export const POCHE = {
  masonry: { ...PEN.cut, fill: 'var(--poche-masonry)' },
  partition: { ...PEN.cut, fill: 'var(--poche-partition)' },
};

export const DASH = {
  hidden: '7 4',
  centre: '14 4 2.5 4',
  extent: '1.5 5',
};
