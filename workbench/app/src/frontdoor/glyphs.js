/* A DRAWN GLYPH FOR EACH LIBRARY CARD (Phase 17, WP-17.3).

   The board draws each of the library's five cards with a small figure in the drawing's own
   language: a gable front for the styles, an order for the proportions, a struck sash for the
   faults, a cornice profile for the elements, and the open book for the glossary. Each is a few
   strokes in a 40 by 40 box, drawn in the card's ink at the fine pen; none is a picture of any one
   record, and none carries a word. Keyed by the library row's id; an id with no glyph draws none.

   Pure geometry: path data only. */
export const GLYPHS = Object.freeze({
  // a gable front: the pitch, the eaves, a centred door and two windows
  style: ['M4 18 L20 6 L36 18', 'M7 16 V36 H33 V16', 'M17 36 V26 H23 V36', 'M10 21 H14 V26 H10 Z', 'M26 21 H30 V26 H26 Z'],
  // an order: cornice, frieze, the shaft with its entasis, and the base
  proportions: ['M9 6 H31', 'M11 9 H29', 'M12 12 H28', 'M15 12 C14 22 14 28 15 33', 'M25 12 C26 22 26 28 25 33', 'M12 33 H28', 'M10 36 H30'],
  // a sash with the error struck through it
  faults: ['M10 6 H30 V34 H10 Z', 'M10 20 H30', 'M20 6 V34', 'M6 38 L34 2'],
  // a cornice profile: the crown's ogee, the corona, the bed mould
  elements: ['M6 6 H34', 'M34 6 C30 7 30 11 26 12', 'M26 12 H24 V16 H20', 'M20 16 C18 16 18 19 16 19', 'M16 19 V34', 'M6 34 H34'],
  // an open book
  glossary: ['M20 10 C14 7 9 7 5 9 V33 C9 31 14 31 20 34', 'M20 10 C26 7 31 7 35 9 V33 C31 31 26 31 20 34', 'M20 10 V34'],
});
