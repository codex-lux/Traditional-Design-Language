/* WHAT A `Term` SHOWS, DECIDED WITHOUT REACT (WP-14.8, PRD §I.1).

   `components/Term.jsx` is the one definition primitive the app has, and it is built so it
   cannot be misused: it takes an id (or a bound field and value) and nothing else — no
   definition prop, no fallback gloss — and every word it shows is a glossary record's. This
   file is everything that primitive decides, as pure functions over `useGlossary()`'s answer,
   so each state can be driven under `node --test` and the component is left to draw.

   FOUR STATES, AND THE ONE A TWO-STATE READER LOSES IS THE THIRD:

     loading   the glossary has not answered yet: nothing is known, and nothing is claimed
     failed    the glossary could not be read: the word cannot be defined, and that is SAID
     missing   the glossary answered and holds no record for this id: `noEntry(id)`, visibly
     ready     the record

   `failed` and `missing` are different facts and they read differently: "no entry" is a gap in
   the records somebody must fill in `glossary/`, "unavailable" is the server, and printing one
   for the other sends a reader to the wrong place. That is this corpus's first rule — unjudged
   is not passed — applied to a word.

   THE TWO SPELLINGS ARE HERE AND ONLY HERE. `noEntry` is the PRD's "one spelling"; the rail,
   navModel and every other reader that meets a missing record import it (through `Term.jsx`,
   which re-exports it) rather than writing the words again. `noGlossary` is its sibling for
   the other state. Neither is a definition: each says which record could not be shown.

   Pure; imports only the grammar's own address writer and its own reader. */
import { citeHref } from '../router.js';
import { parseCite } from '../citations.js';
import { isMissing } from './lookup.js';

export function noEntry(id) {
  return `no entry: ${id}`;
}

export function noGlossary(id) {
  return `glossary unavailable: ${id}`;
}

/* The key a Term answers to: the id it was given, or — for a bound field and value — the
   record `by_field` names, or `field:value` where it names none (lookup.termFor's own rule). */
export function keyFor({ id, field, value } = {}) {
  if (typeof id === 'string' && id) return id;
  if (typeof field === 'string' && field) return `${field}:${value}`;
  return '';
}

function lookupRecord(lookup, { id, field, value }) {
  if (typeof id === 'string' && id) return lookup.term(id);
  if (typeof field === 'string' && field) return lookup.termFor(field, value);
  return { missing: '' };
}

/* The provenance line: the record's `kind`, as the plain word it is, then what it rests on —
   the FIRST source of a sourced record, or the files an editorial record read (`reads`, which
   the server derives from the basis; the app never parses a basis). */
export function provenanceOf(rec) {
  const kind = rec && typeof rec.kind === 'string' ? rec.kind : null;
  let items = [];
  if (kind === 'sourced' && Array.isArray(rec.sources) && rec.sources.length) items = [rec.sources[0]];
  else if (kind === 'editorial' && Array.isArray(rec.reads)) items = rec.reads.filter((r) => typeof r === 'string' && r);
  return { kind, items };
}

/* The address of a term's own page, written by the router's citation writer rather than by a
   string template here — a fourth spelling of the grammar is the one thing this phase forbids. */
export function termHref(id) {
  return citeHref(`term:${id}`);
}

/* glossary = { status, lookup, error } (useGlossary's answer); props = { id } or { field, value }. */
export function termView(glossary, props) {
  const key = keyFor(props);
  const status = glossary && glossary.status;
  if (status === 'failed') {
    return { state: 'failed', key, text: noGlossary(key), error: glossary.error || null };
  }
  if (status !== 'ready' || !glossary.lookup) return { state: 'loading', key };
  const rec = lookupRecord(glossary.lookup, props || {});
  if (isMissing(rec)) {
    const missingKey = rec.missing || key;
    return { state: 'missing', key: missingKey, text: noEntry(missingKey) };
  }
  const confusables = glossary.lookup.confusables(rec.id).map((c) => (isMissing(c)
    ? { missing: c.missing, text: noEntry(c.missing) }
    : { id: c.id, term: c.term, sense: typeof c.sense === 'string' ? c.sense : null,
      href: termHref(c.id) }));
  return {
    state: 'ready',
    key: rec.id,
    record: rec,
    word: rec.term,
    sense: typeof rec.sense === 'string' ? rec.sense : null,
    definition: rec.definition,
    analogy: typeof rec.analogy === 'string' && rec.analogy ? rec.analogy : null,
    provenance: provenanceOf(rec),
    confusables,
    moreHref: termHref(rec.id),
  };
}

/* What a control that carries a word's meaning — a rail item, a chip, a section strip, all
   anchors or buttons a `Term` may not sit inside — describes itself with: the definition as
   both its `title` and its described-by text. Loading describes nothing (and claims nothing);
   the other two say which record could not be shown. */
export function describeTerm(glossary, id) {
  const v = termView(glossary, { id });
  if (v.state === 'ready') return { state: v.state, text: v.definition, title: v.definition };
  if (v.state === 'loading') return { state: v.state, text: '', title: undefined };
  return { state: v.state, text: v.text, title: v.text };
}

/* The word a record calls itself, for a LINK to it rather than a definition of it: the record's
   `term`, or `noEntry(id)` where the lookup holds no such record — never a word written here.
   `wordForCite` is the same answer for a citation: a `term:` cite has no entry in
   `/api/search/index` (which names styles, slots, faults, packs, rooms, massings, groupings and
   partis), so `names/useNames.js` cannot word it and a `RecordLink` would print the raw cite.
   Any other kind answers `undefined`, which leaves the name layer to word it. Two surfaces link
   to a glossary record by cite (the Glossary's "See" list and PageHead's "Try"), and this is the
   one spelling both read. */
export function wordOf(lookup, id) {
  const rec = lookup.term(id);
  return isMissing(rec) ? noEntry(rec.missing) : rec.term;
}

export function wordForCite(lookup, cite) {
  const p = typeof cite === 'string' ? parseCite(cite) : null;
  return p && p.kind === 'term' ? wordOf(lookup, p.id) : undefined;
}
