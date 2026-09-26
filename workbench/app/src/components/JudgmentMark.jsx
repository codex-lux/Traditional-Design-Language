/* P1 — the most important mark in the system, and until WP-14.29 it drew four things with one
   square. The hatched square meant could-not-evaluate, yours-to-decide AND not-applicable at
   once (`oq/one-duty-per-hatch`), which are three of the four states the corpus insists must
   never collapse, and the words that told them apart sat in a map the square's `aria-hidden`
   kept from every screen reader.

   SIX STATES NOW, EACH ITS OWN FORM AND ITS OWN RECORD (PRD tranche 2 §D, `marks.js`):
     pass            a filled square in the passed ink           judgment-passed
     fail            a filled square in the failed ink           judgment-failed
     unjudged        the hatched square: could not evaluate      judgment-unjudged
     yours-to-judge  an open square outlined in gilt, no hatch   judgment-yours-to-judge
     not-applicable  an em rule and no square                    judgment-not-applicable
     refused         a heavy brick outline                       judgment-refused
   `pass`, `fail` and `unjudged` are `judgment.js`'s `JUDGMENT_MARK` values, so every existing
   caller is unchanged; a state this component does not know is drawn UNJUDGED, which is the one
   direction a wrong state may fall -- never into a verdict.

   THE WORD IS THE RECORD'S AND IT ALWAYS REACHES ASSISTIVE TECH. Passed and failed differ in
   colour, and a verdict is never told by colour alone: the glyph is hidden and the state's own
   glossary term stands beside it -- visibly, as a `Term` that opens its definition, wherever the
   mark carries a label, and as visually hidden text on the bare glyph. `showWord={false}` hides
   the visible word where the row already names its state (the dossier's constraint rows), and
   the word is still there for a screen reader. While the glossary loads the mark says nothing
   and is `aria-busy`; it never prints a word of its own. */
import React from 'react';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { JUDGMENT_MARKS } from '../marks.js';
import { MarkGlyph } from './MarkGlyph.jsx';
import { Term } from './Term.jsx';

/* The verdicts proper, whose label reads in full ink; the three that are not a verdict read in
   the secondary ink, as the unjudged label always did. */
const VERDICTS = new Set(['pass', 'fail', 'refused']);

function JudgmentMark({
  state,
  size = 13,
  label,
  reason,
  showWord = true,
  style
}) {
  const known = Object.prototype.hasOwnProperty.call(JUDGMENT_MARKS, state) ? state : 'unjudged';
  const mark = JUDGMENT_MARKS[known];
  const glossary = useGlossary();
  const view = termView(glossary, { id: mark.record });
  const word = view.state === 'ready' ? view.word : (view.text || '');
  const busy = view.state === 'loading' ? 'true' : undefined;
  const glyph = <MarkGlyph token={mark.token} size={size} />;

  if (!label) {
    return (
      <span data-judgment-mark={known} title={reason || word || undefined} aria-busy={busy}
        style={{ display: 'inline-flex', alignItems: 'center', ...style }}>
        {glyph}
        <span className="tdl-sr-only" data-judgment-word="">{word}</span>
      </span>
    );
  }
  return (
    <span data-judgment-mark={known} aria-busy={busy}
      style={{ display: 'inline-flex', alignItems: 'flex-start', gap: 8, ...style }}>
      <span style={{ display: 'flex', alignItems: 'center', height: 20 }}>{glyph}</span>
      <span>
        {showWord
          ? (
            <span data-judgment-word="" style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)',
              marginRight: 7 }}>
              <Term id={mark.record} />
            </span>
          )
          : <span className="tdl-sr-only" data-judgment-word="">{word}</span>}
        <span style={{
          font: 'var(--fw-med) 13px/1.5 var(--body)',
          color: VERDICTS.has(known) ? 'var(--ink)' : 'var(--ink-2)'
        }}>{label}</span>
        {reason && (
          <span style={{
            display: 'block',
            font: 'var(--fw-reg) 12.5px/1.5 var(--body)',
            color: 'var(--ink-2)',
            maxWidth: 'var(--measure-note)'
          }}>{reason}</span>
        )}
      </span>
    </span>
  );
}

export default JudgmentMark;
export { JudgmentMark };
