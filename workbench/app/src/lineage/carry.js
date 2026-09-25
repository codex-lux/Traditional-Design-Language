/* WHAT AN EDGE CARRIES, READ OFF THE SERVED FLAG AND NEVER OFF THE EDGE'S TYPE (WP-14.11, PRD §I.13).

   An edge between two styles says one of four things about the kit:

     member-of            the edge is FILING (`member_of`): the drawer a record is kept in, which is
                          not lineage — and not inert either, because the family a style is filed
                          under joins that style's kit cascade (`build/build.py`'s `family_of`,
                          WP-4.2). The `member-of` glossary record says both halves.
     carries-the-kit      `inherits_kit` is true and the edge names no slots: the whole kit.
     carries-named-slots  `inherits_kit` is true and the edge lists the slots it carries (OQ 58).
     carries-nothing      `inherits_kit` is anything but true: a relation of meaning, no binding.

   `inherits_kit` IS THE ONE SPELLING, and it is the SERVER's (`corpus.phylogeny`, PRD §H.6): the
   app reads the flag and never re-derives it. It had re-derived it TWICE, as the same type table in
   `components/EdgeGlyph.jsx` and `surfaces/Phylogeny.jsx` (`CARRIES = { descends_from, regional_of }`)
   — and that table is wrong on 42 `hybridizes_with` edges that carry the kit, so both surfaces told
   the reader those 42 carry nothing and listed them under "claims only". A table keyed on the TYPE
   cannot be right, because the fact is per EDGE: of 57 `hybridizes_with` edges 42 carry the kit and
   15 do not (measured 25 Sep 2026; `lineage.test.mjs` re-derives it from `styles/*.json` rather
   than trusting this sentence).

   STRICT, as `judgment.js` is: only the boolean `true` carries. A payload carrying `'true'`, `1` or
   an object in that field is not a verdict, and truthiness would turn each into one. A `slots` list
   counts only where it is a non-empty array of non-empty strings; anything else is "no list", which
   on a carrying edge means the whole kit — the schema's own reading (`style-node.schema.json`:
   "Absent means the edge carries the ancestor's whole kit").

   No word a reader sees is written here: each answer is a glossary id, and the component draws the
   record's own word through `Term`. Pure; imports nothing. */

export const FILING = 'member_of';

/* The four carry words, as glossary ids, in the order a reader meets them. */
export const CARRY_TERM_IDS = Object.freeze([
  'member-of', 'carries-the-kit', 'carries-named-slots', 'carries-nothing',
]);

/* The slots an edge names, or [] where it names none. */
export function namedSlotsOf(edge) {
  const s = edge && typeof edge === 'object' ? edge.slots : null;
  if (!Array.isArray(s) || s.length === 0) return [];
  const out = s.filter((x) => typeof x === 'string' && x);
  return out.length === s.length ? out : [];
}

/* Does this edge hand any of the ancestor's kit down? The served flag, strictly. Filing is not a
   lineage edge and carries no flag of its own; what it carries is the `member-of` record's to say. */
export function carriesKit(edge) {
  return Boolean(edge) && typeof edge === 'object' && edge.type !== FILING && edge.inherits_kit === true;
}

/* edge → the glossary id of its carry word. Never a fifth answer. */
export function carryTermOf(edge) {
  if (edge && typeof edge === 'object' && edge.type === FILING) return 'member-of';
  if (!carriesKit(edge)) return 'carries-nothing';
  return namedSlotsOf(edge).length ? 'carries-named-slots' : 'carries-the-kit';
}

/* How the line is drawn: the weight is the carry, never the type. A filing edge is dotted, a
   carrying edge solid and heavy, and anything else dashed and light. */
export function strokeOf(edge) {
  if (edge && typeof edge === 'object' && edge.type === FILING) return 'filing';
  return carriesKit(edge) ? 'carries' : 'claims';
}

/* A served `/api/phylogeny` edge (`from`, `to`) in the key names `EdgeGlyph` takes (`from`,
   `target`), carrying the served flag and slot list untouched. A style record's own lineage item
   already names its `target`. */
export function glyphEdge(e) {
  if (!e || typeof e !== 'object') return null;
  return {
    type: e.type,
    inherits_kit: e.inherits_kit,
    slots: e.slots ?? null,
    from: e.from,
    target: e.target ?? e.to,
    note: e.note,
  };
}

/* The filing edge of a taxon, as a glyph edge, or null where it is filed under nothing. */
export function filingEdgeOf(taxon) {
  const up = taxon && typeof taxon === 'object' ? taxon.member_of : null;
  if (typeof up !== 'string' || !up) return null;
  return { type: FILING, inherits_kit: null, slots: null, from: taxon.id, target: up, note: undefined };
}

/* Edges grouped by carry word, in CARRY_TERM_IDS order, each group non-empty. The grouping a
   reader sees follows the flag, so a kit-carrying co-parent is never listed with the claims. */
export function groupByCarry(edges) {
  const buckets = new Map(CARRY_TERM_IDS.map((id) => [id, []]));
  for (const e of Array.isArray(edges) ? edges : []) {
    if (!e || typeof e !== 'object') continue;
    buckets.get(carryTermOf(e)).push(e);
  }
  return CARRY_TERM_IDS.filter((id) => buckets.get(id).length)
    .map((id) => ({ carry: id, edges: buckets.get(id) }));
}
