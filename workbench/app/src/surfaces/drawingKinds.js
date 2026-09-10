/* The flat plates the Drawing Set can draw — in ONE place, because two files count them.

   WP-12.4. `Chrome.jsx` printed `meta: '5 sheets'` as a typed literal while the real five
   lived in `DrawingSet.jsx`, module-private, and Chrome cannot import from DrawingSet (that
   file imports Chrome). CLAUDE.md names this class directly: a number written into JSX is how
   the Kit's header came to claim 95 slots against an ontology holding 97. The count is derived
   from this list now, and adding a plate moves both readers.

   The model is NOT in this list: it is not a flat plate, it is the thing the plates are of. */
export const KINDS = [
  // "front elevation" until WP-12.0 gave the surface its face chips: the sheet chip picks
  // the KIND and the face chip picks the face, and calling the kind "front" would contradict
  // the reader who has just asked for the north.
  { id: 'elevation', label: 'elevation' },
  { id: 'section', label: 'section' },
  { id: 'bearing', label: 'bearing lines' },
  { id: 'roof', label: 'roof plan' },
  { id: 'plan', label: 'solved plan' },
];
