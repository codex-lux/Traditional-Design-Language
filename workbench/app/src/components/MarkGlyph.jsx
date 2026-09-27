/* ONE MARK, DRAWN IN ITS OWN FORM (WP-14.29, PRD tranche 2 §D).

   `<MarkGlyph token="--mark-unjudged" />` draws a duty token as `marks.js` says that mark is
   drawn -- a filled square, an open one, a hatched one, a dashed one, a rule, a field of lines --
   and nothing else. It says nothing: the glyph is `aria-hidden`, because a square cannot be read
   aloud, and whoever draws it puts the mark's WORD beside it, from the mark's glossary record
   (`JudgmentMark` in visually hidden text or visibly, `MarkKey` as the key's own term column, the
   masthead as the count's `Term`). A glyph whose meaning reaches assistive tech only through a
   hidden square is the defect `oq/one-duty-per-hatch` named, so this component is deliberately
   unable to be the only thing on the page carrying a meaning.

   The one form with no glyph is `word`, for loading, which is not a state of anything and so
   borrows no state's square: it draws its children (the record's word) in the mark's ink, and is
   NOT hidden, because there the word is the mark.

   `data-duty` names the token on every glyph, so the browser walk can hold the paint to the
   stylesheet by property rather than by selector. */
import React from 'react';
import { MARK_FORMS, markGlyph } from '../marks.js';

export function MarkGlyph({ token, size = 13, children, style }) {
  const skin = markGlyph(token, size);
  if (!skin) return null;
  if (MARK_FORMS[token] === 'word') {
    return <span data-duty={token} style={{ ...skin, ...style }}>{children}</span>;
  }
  return <span aria-hidden="true" data-duty={token} style={{ ...skin, ...style }} />;
}

export default MarkGlyph;
