/* THE STYLES INDEX AS AN OUTLINE, IN THE ORDER THE CORPUS FILES ITS NODES (WP-14.6, PRD §I.7).

   A port of `build/render_html.py`'s ordered row list (the block under `# ordered row list`), which
   has drawn the static taxonomy plate since before the workbench existed: traditions in a fixed
   order, each tradition's families by floruit, each family's styles, each style's variants. That
   port hard-codes three levels; this one RECURSES down `member_of`, so a node filed at any depth is
   placed under its parent and a fourth rank would not silently fall out of the index.

   WHY IT EXISTS: the Phylogeny indents by RANK and sorts by DATE, so a row's indentation and the row
   above it disagree — measured at WP-14.0, 111 of 159 rows sat under a row that was not their
   parent. Here each row's nearest shallower row IS its `member_of` parent, by construction, and
   `styleTree.test.mjs` asserts it over every node in `styles/`.

   Traditions come in `overview.traditions` order (`mcp_server/core.py`'s own list, served on
   `/api/overview`); `traditionOrderOf(overview)` reads it off the payload. A name in that order is
   walked only where it is a ROOT (it states no `member_of`) — a filed node is placed by its parent,
   never hoisted to the top. Children go by floruit, then id (`compareTaxa`).

   ORPHANS ARE LISTED, NEVER DROPPED. A node the walk cannot reach — a `member_of` naming no node, a
   filing that loops, a tradition the order does not name — comes back in `orphans`, by id. The
   Python plate computes its orphans the same way and this is what an index owes a reader: a node
   that vanished from the only list of all nodes would read as a node the corpus does not have.

   Pure; imports only its sibling. */
import { compareTaxa } from './taxa.js';

/* The tradition ids, in the order `/api/overview` serves its tradition cards. */
export function traditionOrderOf(overview) {
  const cards = overview && Array.isArray(overview.traditions) ? overview.traditions : [];
  return cards.map((c) => (c && typeof c === 'object' ? c.id : c)).filter((id) => typeof id === 'string');
}

/* taxa, traditionOrder → { rows: [{ id, rank, depth }], orphans: [id] }. */
export function styleTree(taxa, traditionOrder) {
  const list = (Array.isArray(taxa) ? taxa : []).filter((t) => t && typeof t.id === 'string');
  const byId = new Map();
  for (const t of list) if (!byId.has(t.id)) byId.set(t.id, t);

  const children = new Map();
  for (const t of byId.values()) {
    const p = typeof t.member_of === 'string' && t.member_of ? t.member_of : null;
    if (!p || p === t.id) continue;
    if (!children.has(p)) children.set(p, []);
    children.get(p).push(t);
  }
  for (const kids of children.values()) kids.sort(compareTaxa);

  const rows = [];
  const placed = new Set();
  const walk = (t, depth) => {
    if (placed.has(t.id)) return;
    placed.add(t.id);
    rows.push({ id: t.id, rank: t.rank ?? null, depth });
    for (const c of children.get(t.id) || []) walk(c, depth + 1);
  };
  for (const id of Array.isArray(traditionOrder) ? traditionOrder : []) {
    const t = byId.get(id);
    if (t && !(typeof t.member_of === 'string' && t.member_of)) walk(t, 0);
  }

  const orphans = [...byId.keys()].filter((id) => !placed.has(id)).sort();
  return { rows, orphans };
}
