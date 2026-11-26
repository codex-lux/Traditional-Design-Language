/* A LINK, OPENED COLD, SAYS WHAT IT HAS OPENED INTO (WP-14.13, PRD §I.12).

   A colleague handed `#/style/tidewater-georgian/kit/cornice` lands on a slot's figures inside a
   kit inside a style inside a family, in a product whose name they have never read, with no
   route back to where it starts. This is the one thing said to them: what this is — the
   `about-tdl` record's own term and definition, the same sentence the Gate shows — where they
   are, and two ways to begin, the front door and the guided example, each named by its glossary
   record. And a way to say "I know" that is remembered.

   ONE LINE SINCE 26 NOV 2026 ("reader first"). It was three: the sentence, a second trail of
   crumbs under the top bar's own, and the ways in. Where the reader is, is said once, by the
   top bar directly above this line; the banner keeps the sentence and the two ways to begin.

   ONCE PER BROWSER. It shows only when the first place this page loaded was not the front door
   and `prefs.seen['front-door']` is unset; dismissing it, or visiting the front door, sets that
   flag (state/prefs.js), so it never shows again in this browser. It is per-browser memory and
   decides nothing about what the URL shows: the page under it is the page the link named.

   Every word it shows but one is a record's. "Dismiss" is the banner's furniture, not a
   definition of anything. */
import React from 'react';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { guidedExampleStyle, wordFor } from '../nav/navModel.js';
import { formatHash } from '../router.js';

export function ColdLinkBanner({ onDismiss }) {
  const glossary = useGlossary();
  if (glossary.status === 'loading') return null;
  const about = termView(glossary, { id: 'about-tdl' });
  const lookup = glossary.lookup;
  const front = wordFor(lookup, 'surface-overview');
  const guided = wordFor(lookup, 'guided-example');
  const guidedStyle = guidedExampleStyle(lookup);
  const word = (w, id) => w.label || termView(glossary, { id }).text || id;

  return (
    <section data-cold-link="" className="tdl-cold-link" aria-label={about.state === 'ready' ? about.word : 'about-tdl'}>
      <p className="tdl-cold-link-about" title={about.state === 'ready' ? about.definition : undefined}>
        {about.state === 'ready'
          ? <><strong>{about.word}</strong> — {about.definition}</>
          : about.text}
      </p>
      <div className="tdl-cold-link-ways">
        <a href={formatHash('overview', {}, {})} data-cold-link-front="">{word(front, 'surface-overview')}</a>
        {guidedStyle && (
          <a href={formatHash('style', { style: guidedStyle }, {})} data-cold-link-guided="">
            {word(guided, 'guided-example')}
          </a>
        )}
        <button type="button" onClick={onDismiss} data-cold-link-dismiss="" className="tdl-chrome-btn"
          style={{ font: 'var(--type-data-s)', color: 'var(--text-secondary)', padding: '1px 7px',
            border: '1px solid var(--border-hairline)' }}>
          Dismiss
        </button>
      </div>
    </section>
  );
}
