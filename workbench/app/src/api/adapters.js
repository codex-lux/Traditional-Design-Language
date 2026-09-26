/* What counts as an answer, for the two documents the whole app reads once (WP-14.8).

   `api/fetchOnce.js` hands every body to an adapter and treats a throw as a FAILED read. These
   are the two adapters, pure so `src/fetchOnce.test.mjs` drives them: a body that is not the
   served shape is a failure with a reason, never an empty success — a glossary that defines
   nothing, or a search index that names nothing, would read exactly like a corpus with no words
   in it, and every link and definition on the page would then say so falsely. */
import { indexTerms } from '../glossary/lookup.js';
import { nameIndex } from '../names/names.js';

/* GET /api/glossary (PRD §C.1) → the frozen lookup `glossary/lookup.js` builds. */
export function adaptGlossary(body) {
  if (!body || typeof body !== 'object' || !Array.isArray(body.terms)) {
    throw new Error('GET /api/glossary answered without a terms list');
  }
  /* The payload states its own count (PRD §C.1). A body whose list disagrees with it was cut
     short somewhere between the corpus and here, and a lookup built from it would call the
     missing words "no entry" -- a gap in the records, which is the wrong place to send a reader
     for a fault in the transport. */
  if (typeof body.count === 'number' && body.count !== body.terms.length) {
    throw new Error(`GET /api/glossary answered ${body.terms.length} terms under a count of ${body.count}`);
  }
  return indexTerms(body);
}

/* GET /api/search/index → the cite → entry map `names/names.js` reads names from. */
export function adaptSearchIndex(body) {
  if (!body || typeof body !== 'object' || !Array.isArray(body.entries)) {
    throw new Error('GET /api/search/index answered without an entries list');
  }
  return nameIndex(body.entries);
}
