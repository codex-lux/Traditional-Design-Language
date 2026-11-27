/* WHERE YOU ARE AND HOW TO READ IT, FROM ONE GLOSSARY RECORD (WP-14.8, PRD §I.4).

   <PageHead termId={headTermFor(place)} />

   This is the head every page gets — mounted by the shell with the record
   `nav/navModel.js`'s `headTermFor(place)` names — and every word in it is that record's:

     the eyebrow      the record's `term`, as plain text (it names the page; it is not a word
                      to be defined on the page it names)
     the lede         `surface.what`
     the list         "How to read this page": `surface.read[]`, then `surface.try` as a link,
                      worded by the glossary record where the cite is a `term:` (`wordForCite`)

   IT IS FOLDED INTO THE TOP BAR, AND NEVER OPEN UNASKED (ruled 26 Nov 2026, "reader first").
   Until then it was a band above every page: the eyebrow, the lede and the list, open the first
   time a browser met the record. Measured at 1440 × 900 with the cold-link banner above it, a
   style's name began 417 px down its own page and a kit's first slot at 691. The head is one
   control in the top bar now, and its panel is a vellum card under it holding the same three
   things. Content leads the page; what explains the page is one click away. An index that
   wants its lede at display size draws it itself, from this same record (`PageHero`).

   Whether the panel is open is this component's own state and nothing else's: not the URL (a
   link somebody sends must not open a help panel for the person receiving it) and not stored
   (a panel left open would be open on the next page). It closes on Escape, on a click outside
   it, and when the page it explains is left. The panel stays in the document while folded, so a
   reader of the page's text finds the lede and the list whether or not it is shown.

   A missing record is `noEntry(termId)` in the control, visibly; a glossary that could not be
   read says so. Neither is left blank, because a page with an empty head reads as a page that
   needs none. */
import React from 'react';
import { useGlossary } from '../api/useGlossary.js';
import { termView, wordForCite } from '../glossary/termView.js';
import { Eyebrow } from './Eyebrow.jsx';
import { RecordLink } from './RecordLink.jsx';

/* The record's surface block, read once for the head and for a page's own hero. */
export function usePageHead(termId) {
  const glossary = useGlossary();
  const view = termView(glossary, { id: termId });
  const surface = view.state === 'ready' && view.record.surface && typeof view.record.surface === 'object'
    ? view.record.surface : null;
  const read = surface && Array.isArray(surface.read) ? surface.read : [];
  const tryCite = surface && typeof surface.try === 'string' ? surface.try : null;
  // A `term:` cite is worded from the glossary lookup already in hand (`wordForCite`); any other
  // kind is left to the name layer, which is what `undefined` children mean to a RecordLink.
  const tryWord = tryCite ? wordForCite(glossary.lookup, tryCite) : undefined;
  return { view, surface, read, tryCite, tryWord, what: surface && surface.what ? surface.what : null };
}

export function PageHead({ termId }) {
  const { view, read, tryCite, tryWord, what } = usePageHead(termId);
  const listId = `tdl-page-head-${String(termId).replace(/[^A-Za-z0-9_-]/g, '')}`;
  const [open, setOpen] = React.useState(false);
  const box = React.useRef(null);

  // Leaving the page folds the panel that explained it.
  React.useEffect(() => { setOpen(false); }, [termId]);
  React.useEffect(() => {
    if (!open) return undefined;
    const away = (ev) => { if (box.current && !box.current.contains(ev.target)) setOpen(false); };
    const key = (ev) => { if (ev.key === 'Escape') setOpen(false); };
    document.addEventListener('pointerdown', away);
    document.addEventListener('keydown', key);
    return () => { document.removeEventListener('pointerdown', away); document.removeEventListener('keydown', key); };
  }, [open]);

  if (view.state !== 'ready') {
    return (
      <div className="tdl-page-head" data-page-head={termId}
        aria-busy={view.state === 'loading' ? 'true' : undefined}>
        {view.state !== 'loading' && <Eyebrow as="div" data-missing="">{view.text}</Eyebrow>}
      </div>
    );
  }
  const hasPanel = Boolean(what) || read.length > 0 || Boolean(tryCite);
  if (!hasPanel) return <div className="tdl-page-head" data-page-head={termId} />;

  return (
    <div className="tdl-page-head" data-page-head={termId} ref={box}>
      <button type="button" className="tdl-page-head-toggle" aria-expanded={open}
        aria-controls={listId} onClick={() => setOpen(!open)}>
        <span className="tdl-page-head-q" aria-hidden="true">?</span>
        How to read this page
      </button>
      <div id={listId} className="tdl-vellum tdl-page-head-pop" data-ground="vellum" hidden={!open}>
        <Eyebrow as="div" tone="accent">{view.word}</Eyebrow>
        {what && <p className="tdl-page-head-what">{what}</p>}
        {(read.length > 0 || tryCite) && (
          <div className="tdl-page-head-read">
            {read.length > 0 && (
              <ul>{read.map((line) => <li key={line}>{line}</li>)}</ul>
            )}
            {tryCite && (
              <p className="tdl-page-head-try">Try <RecordLink cite={tryCite}>{tryWord}</RecordLink></p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* A PAGE'S OWN HEAD, AT DISPLAY SIZE, FROM THE SAME RECORD. An index is a page about itself, so
   its record's term is its kicker and its `surface.what` its title: the Fault Corpus opens on
   "Every named error: what it looks like, why it happens, and how to fix it." A record's page
   leads with the record's name instead and does not draw this. Nothing here is written by the
   app; while the glossary loads it draws nothing, and a missing record says so. */
export function PageHero({ termId, children, className }) {
  const { view, what } = usePageHead(termId);
  if (view.state === 'loading') return <header className={className ? `tdl-hero ${className}` : 'tdl-hero'} aria-busy="true" />;
  return (
    <header className={className ? `tdl-hero ${className}` : 'tdl-hero'} data-page-hero={termId}>
      <div className="tdl-hero-kicker" data-missing={view.state === 'ready' ? undefined : ''}>
        {view.state === 'ready' ? view.word : view.text}
      </div>
      {what && <h1 className="tdl-hero-title-2">{what}</h1>}
      {children}
    </header>
  );
}
