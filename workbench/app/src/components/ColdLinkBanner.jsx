/* A LINK, OPENED COLD, SAYS WHAT IT HAS OPENED INTO (WP-14.13, PRD §I.12).

   A colleague handed `#/style/tidewater-georgian/kit/cornice` lands on a slot's figures inside a
   kit inside a style inside a family, in a product whose name they have never read, with no
   route back to where it starts. This is the one thing said to them: what this is — the
   `about-tdl` record's own term and definition, the same sentence the Gate shows — where they
   are, as the crumbs, and two ways to begin, the front door and the guided example, each named
   by its glossary record. And a way to say "I know" that is remembered.

   ONCE PER BROWSER. It shows only when the first place this page loaded was not the front door
   and `prefs.seen['front-door']` is unset; dismissing it, or visiting the front door, sets that
   flag (state/prefs.js), so it never shows again in this browser. It is per-browser memory and
   decides nothing about what the URL shows: the page under it is the page the link named.

   Every word it shows but three is a record's. "Dismiss", "You are at" and the list's own name
   are the banner's furniture, not a definition of anything. */
import React from 'react';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { crumbLabel } from '../nav/crumbs.js';
import { guidedExampleStyle, wordFor } from '../nav/navModel.js';
import { formatHash } from '../router.js';

export function ColdLinkBanner({ crumbs, onDismiss }) {
  const glossary = useGlossary();
  if (glossary.status === 'loading') return null;
  const about = termView(glossary, { id: 'about-tdl' });
  const lookup = glossary.lookup;
  const front = wordFor(lookup, 'surface-overview');
  const guided = wordFor(lookup, 'guided-example');
  const guidedStyle = guidedExampleStyle(lookup);
  const trail = (Array.isArray(crumbs) ? crumbs : []).map(crumbLabel).filter(Boolean);
  const word = (w, id) => w.label || termView(glossary, { id }).text || id;

  return (
    <section data-cold-link="" aria-label={about.state === 'ready' ? about.word : 'about-tdl'}
      style={{ flex: 'none', borderBottom: '1px solid var(--rule)', background: 'var(--paper-deep)',
        padding: '10px 16px', display: 'flex', alignItems: 'flex-start', gap: 18,
        font: 'var(--fw-reg) 13px/1.5 var(--body)', color: 'var(--ink)' }}>
      <div style={{ flex: 1, minWidth: 0, maxWidth: '96ch' }}>
        <p style={{ margin: 0 }}>
          {about.state === 'ready'
            ? <><strong style={{ fontWeight: 600 }}>{about.word}</strong> — {about.definition}</>
            : about.text}
        </p>
        {trail.length > 0 && (
          <p data-cold-link-trail="" style={{ margin: '4px 0 0', color: 'var(--ink-2)' }}>
            You are at: {trail.join(' › ')}
          </p>
        )}
      </div>
      <div style={{ flex: 'none', display: 'flex', alignItems: 'baseline', gap: 14, whiteSpace: 'nowrap' }}>
        <a href={formatHash('overview', {}, {})} data-cold-link-front="">{word(front, 'surface-overview')}</a>
        {guidedStyle && (
          <a href={formatHash('style', { style: guidedStyle }, {})} data-cold-link-guided="">
            {word(guided, 'guided-example')}
          </a>
        )}
        <button type="button" onClick={onDismiss} data-cold-link-dismiss=""
          style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', padding: '2px 7px',
            border: '1px solid var(--rule)' }}>
          Dismiss
        </button>
      </div>
    </section>
  );
}
