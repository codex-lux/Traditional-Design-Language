/* WHERE YOU ARE AND HOW TO READ IT, FROM ONE GLOSSARY RECORD (WP-14.8, PRD §I.4).

   <PageHead termId={headTermFor(place)} />

   No page in the workbench said what it was: `document.title` never changed, and the one
   component written to head a surface (`SurfaceHead`) was exported and imported by nothing.
   This is the head every page gets — mounted by the shell (WP-14.13) with the record
   `nav/navModel.js`'s `headTermFor(place)` names — and every word in it is that record's:

     the eyebrow      the record's `term`, as plain text (it names the page; it is not a word
                      to be defined on the page it names)
     the lede         `surface.what`
     the disclosure   "How to read this page": `surface.read[]`, then `surface.try` as a link,
                      worded by the glossary record where the cite is a `term:` (`wordForCite`)

   The disclosure is OPEN THE FIRST TIME this browser shows this record's head and folded after,
   and a reader's own toggle outranks both — per-browser memory in `state/prefs.js` (`seen` and
   `folds` under `head:<termId>`), NEVER the URL: a link somebody sends must not open or close a
   help panel for the person receiving it. Whether it is open is `prefs.disclosureOpen`'s rule,
   and "first visit" is read ONCE per record before this head marks the record seen, so the
   head does not fold itself on the render that shows it.

   A missing record is `noEntry(termId)` in the eyebrow, visibly; a glossary that could not be
   read says so. Neither is left blank, because a page with an empty head reads as a page that
   needs none. */
import React from 'react';
import { useGlossary } from '../api/useGlossary.js';
import { termView, wordForCite } from '../glossary/termView.js';
import { prefs, disclosureOpen } from '../state/prefs.js';
import { Eyebrow } from './Eyebrow.jsx';
import { RecordLink } from './RecordLink.jsx';

export function PageHead({ termId }) {
  const glossary = useGlossary();
  const view = termView(glossary, { id: termId });
  const store = React.useSyncExternalStore(prefs.subscribe, prefs.get);
  const key = `head:${termId}`;
  const listId = `tdl-page-head-${String(termId).replace(/[^A-Za-z0-9_-]/g, '')}`;

  // First visit, read once per record — before the effect below marks it seen.
  const [first, setFirst] = React.useState(() => ({ key, first: !prefs.isSeen(key) }));
  if (first.key !== key) setFirst({ key, first: !prefs.isSeen(key) });
  const firstVisit = first.key === key ? first.first : !prefs.isSeen(key);

  const surface = view.state === 'ready' && view.record.surface && typeof view.record.surface === 'object'
    ? view.record.surface : null;
  const read = surface && Array.isArray(surface.read) ? surface.read : [];
  const tryCite = surface && typeof surface.try === 'string' ? surface.try : null;
  const hasDisclosure = read.length > 0 || Boolean(tryCite);
  // A `term:` cite is worded from the glossary lookup already in hand (`wordForCite`); any other
  // kind is left to the name layer, which is what `undefined` children mean to a RecordLink.
  const tryWord = tryCite ? wordForCite(glossary.lookup, tryCite) : undefined;

  React.useEffect(() => {
    if (view.state === 'ready' && hasDisclosure) prefs.markSeen(key);
  }, [key, view.state, hasDisclosure]);

  const fold = Object.prototype.hasOwnProperty.call(store.folds, key) ? store.folds[key] : undefined;
  const open = disclosureOpen(fold, firstVisit);

  if (view.state !== 'ready') {
    return (
      <header className="tdl-page-head" data-page-head={termId}
        aria-busy={view.state === 'loading' ? 'true' : undefined}>
        {view.state !== 'loading' && <Eyebrow as="div" data-missing="">{view.text}</Eyebrow>}
      </header>
    );
  }

  return (
    <header className="tdl-page-head" data-page-head={termId}>
      <Eyebrow as="div">{view.word}</Eyebrow>
      {surface && surface.what && <p className="tdl-page-head-what">{surface.what}</p>}
      {hasDisclosure && (
        <>
          <button type="button" className="tdl-page-head-toggle" aria-expanded={open}
            aria-controls={listId} onClick={() => prefs.setFold(key, !open)}>
            How to read this page
          </button>
          <div id={listId} className="tdl-page-head-read" hidden={!open}>
            {read.length > 0 && (
              <ul>{read.map((line) => <li key={line}>{line}</li>)}</ul>
            )}
            {tryCite && (
              <p className="tdl-page-head-try">Try <RecordLink cite={tryCite}>{tryWord}</RecordLink></p>
            )}
          </div>
        </>
      )}
    </header>
  );
}
