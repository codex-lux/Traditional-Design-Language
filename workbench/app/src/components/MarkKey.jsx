/* THE PRODUCT KEY: EVERY MARK THE WORKBENCH DRAWS, IN ITS OWN FORM, BESIDE THE ONE WORD IT MEANS
   (WP-14.29, PRD tranche 2 §D; ruled 25 Sep 2026, "one meaning per hatch, one product key").

   A key says what a mark MEANS, so it could not be written while the unjudged hatch meant five
   things and the 45° hatch six (`oq/one-duty-per-hatch`). Each mark has one meaning now, carried
   by one `--mark-*` token in `theme/tokens.css` and named by exactly one glossary record whose
   `mark` is that token (`build/check_glossary.py` rule 13). This component is that list drawn:
   it READS THE RECORDS -- every record carrying a `mark`, grouped under its family's own record,
   in the order the server sorts them -- and draws each token through `MarkGlyph` beside the
   record's term and definition. It writes no word of its own and holds no list of marks: a
   mark added to the stylesheet and the glossary appears here without this file changing, and a
   record with no mark does not.

   The glyph is decorative (`aria-hidden`); the term beside it is the mark's name for every
   reader, and a link to the term's own page. Loading draws its WORD, because that is its form.

   It stands on the Glossary page and the `?` card links to it (`#/glossary?family=mark`). */
import React from 'react';
import { useGlossary } from '../api/useGlossary.js';
import { formatHash } from '../router.js';
import { MarkGlyph } from './MarkGlyph.jsx';
import { Term } from './Term.jsx';
import { markKeyGroups } from '../marks.js';

export function MarkKey() {
  const glossary = useGlossary();
  const headId = 'tdl-mark-key-head';
  if (glossary.status !== 'ready' || !glossary.lookup) {
    return <section className="tdl-mark-key" data-mark-key="" aria-busy={glossary.status === 'loading' ? 'true' : undefined} />;
  }
  const groups = markKeyGroups(glossary.lookup);
  return (
    <section className="tdl-mark-key" data-mark-key="" aria-labelledby={headId}>
      <h2 id={headId} className="tdl-glossary-family-name"><Term id="key-to-the-marks" /></h2>
      {groups.map((g) => (
        <div key={g.family} className="tdl-mark-key-group" data-mark-key-family={g.family}>
          <h3 className="tdl-mark-key-family"><Term field="glossary.family" value={g.family} /></h3>
          <dl className="tdl-mark-key-list">
            {g.rows.map((rec) => (
              <div key={rec.id} className="tdl-mark-key-row" data-mark-row={rec.mark} data-mark-term={rec.id}>
                <dt>
                  <span className="tdl-mark-key-specimen" aria-hidden="true">
                    <MarkGlyph token={rec.mark} size={14}>{rec.term}</MarkGlyph>
                  </span>
                  <a href={formatHash('glossary', { term: rec.id })} data-mark-word="">{rec.term}</a>
                </dt>
                <dd>{rec.definition}</dd>
              </div>
            ))}
          </dl>
        </div>
      ))}
    </section>
  );
}

export default MarkKey;
