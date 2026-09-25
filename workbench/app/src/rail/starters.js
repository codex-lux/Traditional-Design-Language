/* THE QUESTIONS A PAGE OFFERS ITS ASSISTANT (WP-14.22, PRD tranche 2 §C.8, §C.10).

   Each page's `surface-*` glossary record carries an `ask`: one to three questions a reader on
   that page might put to the assistant, authored by WP-14.17 and held by
   build/check_glossary.py to the schema's own rules (each ends with a question mark, runs to
   twenty words at most, and is held to the same hygiene as a definition). The pane shows them
   VERBATIM as buttons that fill the input and never send on their
   own. This file decides which questions a page has and writes none of them -- a starter
   question typed here would be the app writing copy, which Phase 14 forbids -- so every string
   it returns is a record's, unchanged, and `starters.test.mjs` holds them to the files on disk.

   NOTHING IS SHOWN WHILE THE GLOSSARY LOADS, and nothing where it failed or holds no record for
   the page. Those are three different facts, but none of them is a question to offer: a page
   whose questions are one round trip away shows none rather than a placeholder, and a page with
   no record shows none rather than somebody else's. The pane head already says, through
   `termView`, which of the three states the glossary is in.

   Pure: no React, no DOM, and nothing from node_modules, so the test drives it under
   `node --test` with the records themselves. */
import { isMissing } from '../glossary/lookup.js';

/* The record a surface's questions live on: the page's own `surface-*` record. The style surface
   takes `surface-style` in every place, dossier sections included -- no section record carries
   an `ask` (the schema allows one; none is authored), and borrowing another page's questions for
   a section would be answering a question about a different page. */
export function starterRecordId(surface) {
  return typeof surface === 'string' && surface ? `surface-${surface}` : null;
}

/* glossary = useGlossary()'s answer { status, lookup }; surface = the page's surface id.
   Returns the record's `ask`, verbatim and in its order, or [] -- never a guess. */
export function startersFor(glossary, surface) {
  if (!glossary || glossary.status !== 'ready' || !glossary.lookup) return [];
  const id = starterRecordId(surface);
  if (!id) return [];
  const rec = glossary.lookup.term(id);
  if (!rec || typeof rec !== 'object' || isMissing(rec)) return [];
  const block = rec.surface && typeof rec.surface === 'object' ? rec.surface : null;
  const ask = block && Array.isArray(block.ask) ? block.ask : [];
  return ask.filter((q) => typeof q === 'string' && q.trim() !== '');
}
