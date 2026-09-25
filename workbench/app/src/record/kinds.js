/* THE RECORD PAGES, AS DATA (WP-14.23, tranche 2 PRD §B, §C.6).

   Five kinds of corpus record have a page of their own: a slot, in the Elements index, and the
   four plan-type records -- a room type, a massing, a grouping and a parti. Each row says, for one
   kind, which surface shows it, which selection key names the record on that surface, which
   citation kind names it, and which glossary record says what kind of thing it is. It holds ids,
   never words: every word a reader sees is a glossary record's `term` or a record's own name.

   The router (`SURFACE_PATHS`), the citation grammar (`routeCite`/`citeFor`), the site map
   (`navModel.UNDER`) and the crumbs each carry their half of these facts in their own form, and
   `src/record.test.mjs` holds every one of them to this table, so a kind added in one place and
   not the others fails a test rather than a reader.

   Pure: no React, no DOM, no fetch. */

const kind = (surface, key, cite, termId) => Object.freeze({ surface, key, cite, termId });

/* The slot first: it is the Elements index's own record. */
export const SLOT_KIND = kind('elements', 'slot', 'slot', 'slot');

/* The four plan-type kinds, in the order a house is described from the outside in: the massing
   (the shape), the parti (the diagram), the grouping (a cluster of rooms) and the room. */
export const RECORD_KINDS = Object.freeze([
  kind('massing', 'massing', 'massing', 'massing'),
  kind('parti', 'parti', 'parti', 'parti'),
  kind('grouping', 'grouping', 'grouping', 'grouping'),
  kind('room', 'roomType', 'room', 'room'),
]);

/* Every kind with a page, the slot included. */
export const PAGE_KINDS = Object.freeze([SLOT_KIND, ...RECORD_KINDS]);

/* The row for a surface, or null. */
export function kindOfSurface(surface) {
  return PAGE_KINDS.find((k) => k.surface === surface) || null;
}

/* The row for a citation kind, or null. */
export function kindOfCite(citeKind) {
  return PAGE_KINDS.find((k) => k.cite === citeKind) || null;
}

/* The record id a selection names on its kind's surface, or null for the bare index. */
export function recordIdOf(k, selection) {
  if (!k || !selection || typeof selection !== 'object') return null;
  const v = selection[k.key];
  return typeof v === 'string' && v.trim() ? v.trim() : null;
}
