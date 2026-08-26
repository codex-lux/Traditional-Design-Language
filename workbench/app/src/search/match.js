/* Scored substring matching. Not a fuzzy matcher, deliberately.

   The corpus is 665 nameable things with careful, distinct names. Edit-distance fuzz
   earns its keep over millions of noisy strings; over this it mostly invents matches —
   "cape" scoring against "escape hatch" is a worse answer than no answer, and in a corpus
   whose whole point is that the words are precise, a loose match is a small lie.

   The ladder is the same one core.find_style has always used, with one rung added: a
   name that STARTS with what you typed beats a name that merely contains it, because
   that is what typing three letters means.

   Pure. No DOM, no React. e2e/search-unit.mjs runs it on node. */

export const SCORE = {
  NAME_EXACT: 6,
  NAME_PREFIX: 4,
  ID_PREFIX: 3,
  NAME_CONTAINS: 2,
  HAY: 1,
};

/* Kinds in the order a reader wants them, not alphabetically. A style is what people
   look for most; a slot is a piece of one; a fault is a diagnosis. Ties break here so
   two equally-scored hits come back in a stable, explicable order. */
export const KIND_ORDER = [
  'surface', 'action', 'style', 'kit', 'slot', 'pack',
  'fault', 'room', 'massing', 'parti', 'grouping',
];

const kindRank = (k) => {
  const i = KIND_ORDER.indexOf(k);
  return i === -1 ? KIND_ORDER.length : i;
};

export function normalize(s) {
  return String(s == null ? '' : s).toLowerCase().trim();
}

/* → a number, or 0 for no match. Higher is better. */
export function score(entry, query) {
  const q = normalize(query);
  if (!q) return 0;
  const name = normalize(entry.name);
  const id = normalize(entry.id);
  const hay = entry.hay || (name + ' ' + id);

  if (name === q || id === q) return SCORE.NAME_EXACT;
  if (name.startsWith(q)) return SCORE.NAME_PREFIX;
  if (id.startsWith(q)) return SCORE.ID_PREFIX;
  if (name.includes(q)) return SCORE.NAME_CONTAINS;
  if (hay.includes(q)) return SCORE.HAY;

  /* Multi-word queries: every word must appear somewhere. "georgian tidewater" finds
     the same record as "tidewater georgian", which is what someone half-remembering a
     name types. One word failing means no match — this is an AND, not a bag of ORs. */
  const words = q.split(/\s+/).filter(Boolean);
  if (words.length > 1 && words.every((w) => hay.includes(w))) return SCORE.HAY;

  return 0;
}

/* → [{...entry, _score}], best first. `limit` caps the list the palette draws, not the
   search: the count of what was cut is returned so the palette can say so rather than
   implying it showed everything. */
export function search(entries, query, limit = 40) {
  const q = normalize(query);
  if (!q) return { hits: [], total: 0, cut: 0 };

  const scored = [];
  for (const e of entries || []) {
    const s = score(e, q);
    if (s > 0) scored.push({ ...e, _score: s });
  }

  scored.sort((a, b) => (
    b._score - a._score
    || kindRank(a.kind) - kindRank(b.kind)
    || normalize(a.name).length - normalize(b.name).length   // the tighter name first
    || normalize(a.name).localeCompare(normalize(b.name))
  ));

  return { hits: scored.slice(0, limit), total: scored.length, cut: Math.max(0, scored.length - limit) };
}

/* The same test, for filtering a list already on screen. Rows are arbitrary objects, so
   the caller says which fields carry words. */
export function matches(row, query, fields) {
  const q = normalize(query);
  if (!q) return true;
  const hay = (fields || [])
    .map((f) => (typeof f === 'function' ? f(row) : row[f]))
    .filter((v) => v != null)
    .map((v) => (Array.isArray(v) ? v.join(' ') : String(v)))
    .join(' ')
    .toLowerCase();
  const words = q.split(/\s+/).filter(Boolean);
  return words.every((w) => hay.includes(w));
}
