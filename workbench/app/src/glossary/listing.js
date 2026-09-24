/* THE GLOSSARY INDEX, AS DATA (WP-14.8, PRD §E.4).

   `#/glossary` lists every record by family, the families in `by_family`'s order (the schema's)
   and the records within each in the payload's order (the server's sort: family, then `order`,
   then id). `?q=` narrows by the words a reader would type — the term, its other words (`aka`),
   its sense and its id — and never by the definition, for the reason the server keeps the
   definition out of the search haystack (PRD §C.5): a definition is full of other words, and a
   search for "slot" that matched every record whose definition mentions a slot would bury the
   one record that IS the slot. `?family=` narrows to one family.

   A family with no record matching is left out rather than drawn as an empty heading. Pure. */

const norm = (s) => String(s == null ? '' : s).toLowerCase();

export function haystackOf(rec) {
  const parts = [rec.term, rec.sense, rec.id, ...(Array.isArray(rec.aka) ? rec.aka : [])];
  return parts.filter((p) => typeof p === 'string' && p).map(norm).join('\n');
}

/* Every whitespace-separated token of `q` must appear somewhere in the record's haystack. */
export function matchesQuery(rec, q) {
  const tokens = norm(q).split(/\s+/).filter(Boolean);
  if (!tokens.length) return true;
  const hay = haystackOf(rec);
  return tokens.every((t) => hay.includes(t));
}

export function glossaryListing(lookup, { q, family } = {}) {
  if (!lookup) return [];
  const names = lookup.families();
  const only = typeof family === 'string' && family ? family : null;
  const out = [];
  for (const name of names) {
    if (only && name !== only) continue;
    const terms = lookup.family(name).filter((rec) => matchesQuery(rec, q));
    if (terms.length) out.push({ family: name, terms });
  }
  return out;
}
