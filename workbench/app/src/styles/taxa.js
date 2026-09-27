/* THE TAXONOMY AS `member_of` STATES IT, READ ONE WAY (WP-14.6, PRD §I.7).

   A style node is FILED UNDER exactly one parent (`member_of`: a variant under its style, a style
   under its family, a family under its tradition), and that filing is a different relation from
   LINEAGE (`descends_from`, `references`, ...), which says where a style's forms came from. The
   crumbs, the dossier's "filed under this" and the Styles index are all about filing, so they read
   `member_of` and never lineage — PRD §F.3's own rule, and the reason these helpers exist apart
   from anything that walks edges.

   `Phylogeny.jsx` had its own `traditionOf` inline, with a depth cap of eight standing in for a
   cycle guard, and its own copy of the tradition hues. Both live here now: the surface imports the
   hues and `traditionOf` (WP-14.11, and `styleTree.test.mjs` asserts the import and that no second
   table is left in the file), and the walk is written once, guarded by what it has seen rather than
   by a depth: a cycle in the filing is a defect in the data, and a reader of it must stop and say
   nothing rather than loop or invent a parent.

   `byId` may be a Map or a plain object keyed by id; a taxon is a `/api/phylogeny` taxon
   (`floruit_start` at the top) or a style record (`period.floruit_start`), because both are what a
   caller holds and the fact is one fact.

   Pure; imports nothing. */

/* The tradition swatches, one token each (Graphic Standard No. 1: no new colours). */
export const TRADITION_HUES = Object.freeze({
  'classical-mediterranean': 'var(--t0)',
  'british-isles': 'var(--t1)',
  'northern-european-vernacular': 'var(--t2)',
  'iberian-mediterranean': 'var(--t3)',
  'north-american': 'var(--t4)',
});

export function taxonOf(id, byId) {
  if (typeof id !== 'string' || !byId) return null;
  if (byId instanceof Map) return byId.get(id) || null;
  return Object.prototype.hasOwnProperty.call(byId, id) ? byId[id] : null;
}

export function floruitOf(t) {
  const v = t && (t.floruit_start ?? (t.period && t.period.floruit_start));
  return typeof v === 'number' && Number.isFinite(v) ? v : null;
}

/* Siblings in the order a reader meets them: by floruit, then by id; a taxon with no date after
   every dated one, never dropped. */
export function compareTaxa(a, b) {
  const fa = floruitOf(a), fb = floruitOf(b);
  if (fa !== fb) {
    if (fa === null) return 1;
    if (fb === null) return -1;
    return fa - fb;
  }
  return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
}

/* The `member_of` ancestors of `id`, ROOT FIRST, excluding `id` itself (the dossier payload's
   `chain`). A filing that names a parent `byId` does not hold ends the chain there: what comes back
   is only what could be read. A filing that LOOPS yields no chain at all, because every taxon in a
   loop would name as its root something that is not one. */
export function memberChain(id, byId) {
  const chain = [];
  const seen = new Set([id]);
  let t = taxonOf(id, byId);
  while (t && typeof t.member_of === 'string' && t.member_of) {
    if (seen.has(t.member_of)) return [];            // a loop: no honest chain exists
    seen.add(t.member_of);
    const parent = taxonOf(t.member_of, byId);
    if (!parent) break;
    chain.unshift(parent.id);
    t = parent;
  }
  return chain;
}

/* The tradition a taxon is filed under (itself, for a tradition), or null where the filing does
   not reach one. */
export function traditionOf(id, byId) {
  const t = taxonOf(id, byId);
  if (!t) return null;
  if (t.rank === 'tradition') return t.id;
  const chain = memberChain(id, byId);
  const root = chain.length ? taxonOf(chain[0], byId) : null;
  return root && root.rank === 'tradition' ? root.id : null;
}

/* The taxa filed directly under `id`, in reading order. */
export function membersOf(id, taxa) {
  const list = Array.isArray(taxa) ? taxa : (taxa instanceof Map ? [...taxa.values()] : Object.values(taxa || {}));
  return list.filter((t) => t && t.member_of === id && t.id !== id).sort(compareTaxa);
}
