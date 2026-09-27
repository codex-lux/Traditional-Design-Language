/* THE GLOSSARY, INDEXED FOR READING — AND NOT ONE WORD OF ITS OWN (WP-14.6, PRD §I.2).

   Ruled 24 Sep 2026: every definition the workbench shows is a glossary RECORD, and the app writes
   none. This is the reader every surface asks: `indexTerms(payload)` takes `GET /api/glossary`'s
   body and returns a frozen lookup; `useGlossary()` (WP-14.8) fetches it once and hands it out.

   A MISSING RECORD IS AN ANSWER, NOT AN EMPTY STRING. `term(id)` returns the record or
   `{ missing: id }` — never `undefined` (which a caller would render as nothing, reading like a word
   with no meaning) and never a fallback gloss (which would be the app writing a definition, the one
   thing the ruling forbids). `components/Term.jsx` renders `{missing}` visibly as `noEntry(id)`, and
   `glossary.test.mjs` makes every literal id in the app resolve, so that branch is unreachable
   from shipped code and loud where it is not. `termFor(field, value)` answers the same way, naming
   the field and value it could not find.

   No strings of its own: there is no word, label or sentence in this file, and
   `lookup.test.mjs` reads the source to keep it so. Pure; imports nothing. */

const has = (o, k) => Object.prototype.hasOwnProperty.call(o, k);

const missing = (id) => Object.freeze({ missing: id });

/* A record this lookup could not find. */
export function isMissing(rec) {
  return Boolean(rec) && typeof rec === 'object' && typeof rec.missing === 'string';
}

export function indexTerms(payload) {
  const body = payload && typeof payload === 'object' ? payload : {};
  const terms = Array.isArray(body.terms)
    ? body.terms.filter((t) => t && typeof t === 'object' && typeof t.id === 'string')
    : [];
  const byId = new Map();
  for (const t of terms) if (!byId.has(t.id)) byId.set(t.id, t);
  const byField = body.by_field && typeof body.by_field === 'object' ? body.by_field : {};

  const term = (id) => byId.get(id) || missing(id);

  return Object.freeze({
    version: typeof body.version === 'string' ? body.version : null,
    count: byId.size,
    has: (id) => byId.has(id),
    term,
    /* Through `by_field`, the server's map read off the records' own `binds`. A value the map does
       not carry is missing under `field:value`; a value the map carries whose record is absent is
       missing under that record's id, because that is the record somebody has to write. */
    termFor(field, value) {
      const map = has(byField, field) && byField[field] && typeof byField[field] === 'object'
        ? byField[field] : null;
      const id = map && has(map, value) ? map[value] : null;
      return typeof id === 'string' ? term(id) : missing(`${field}:${value}`);
    },
    /* The records a word is not to be confused with, in the order the record declares them. A
       declared id with no record comes back as `{missing}` in its place rather than being dropped,
       so a popover can say there is a confusable it cannot show. A term that is itself missing has
       no declaration to read and yields none. */
    confusables(id) {
      const t = byId.get(id);
      const ids = t && Array.isArray(t.confusable_with) ? t.confusable_with : [];
      return ids.map(term);
    },
    /* Every record of one family, in the payload's order (which the server sorts by the schema's
       family order, then `order`, then id). A second record under an id already seen is not a
       second term: `term(id)` answers with the first, and so does this. */
    family(name) {
      const seen = new Set();
      return terms.filter((t) => {
        if (t.family !== name || byId.get(t.id) !== t || seen.has(t.id)) return false;
        seen.add(t.id);
        return true;
      });
    },
    /* Every family the payload names, in `by_family`'s order — which the server writes in the
       schema's enum order, so the Glossary index lists families the way the schema declares
       them rather than in an order this file would have to invent (WP-14.8). A family with no
       records is still named: whether to show an empty group is the reader's decision, not the
       index's. A payload with no `by_family` names none, and a family is never guessed from
       the records' own `family` fields, because that would drop the schema's order. */
    families() {
      const bf = body.by_family && typeof body.by_family === 'object' && !Array.isArray(body.by_family)
        ? body.by_family : {};
      return Object.keys(bf).filter((k) => Array.isArray(bf[k]));
    },
  });
}
