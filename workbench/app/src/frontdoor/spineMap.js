/* THE FRONT DOOR'S MAP OF THE WORKBENCH IS THE SITE MAP, DRAWN AS RULED ROWS (WP-14.14, PRD §F).

   The front door used to carry its own catalogue of places — `DOORS`, eleven buttons in three
   groups, each with a label and a line of description written in the JSX — and the rail carried
   another, and the palette a third, and the three disagreed about what the places were called,
   which group each was in, and how many groups there were (the Overview's own comment said "the
   rail groups by the same three" over a rail of five). `nav/navModel.js` is the one account now,
   and this map is a VIEW of it: one ruled row per navModel group, carrying exactly the items that
   group holds, in navModel's order, with navModel's label, href, step number and meta.

   IT KEEPS NO LIST. Every row, every item, every word and every address below is read off the
   model it is handed; nothing here names a surface, a path, a record id or a label. The one thing
   it does of its own is flatten a nested item (Trace a drawing, under the Plan step; a dossier
   section, under the style in hand) into its group's row with a `depth`, so a row reads left to
   right. `src/frontDoor.test.mjs` holds it to navModel in both directions — every item navModel
   gives appears in the map, and the map carries nothing navModel did not give — so a place added
   to the site map arrives on the front door with no edit here, and a place written here that the
   site map does not hold fails the build.

   Pure: no React, no DOM. `components/TwoSpineMap.jsx` draws what this returns. */

const isObj = (v) => Boolean(v) && typeof v === 'object' && !Array.isArray(v);

/* The fields a map entry carries, each copied from the navModel item as it is. A map entry is the
   item and its place in the row, and never a second opinion about the item. */
const FIELDS = ['id', 'surface', 'href', 'termId', 'label', 'missing', 'step', 'meta', 'current', 'note'];

function entry(item, depth, parent) {
  const out = {};
  for (const k of FIELDS) out[k] = item[k] === undefined ? null : item[k];
  out.depth = depth;
  out.parent = parent;
  return out;
}

function flatten(items, depth, parent, out) {
  for (const it of Array.isArray(items) ? items : []) {
    if (!isObj(it)) continue;
    out.push(entry(it, depth, parent));
    flatten(it.children, depth + 1, it.id, out);
  }
  return out;
}

/* navModel(...) → [{ id, termId, label, missing, items: [entry] }], one row per group. */
export function mapRows(model) {
  const groups = isObj(model) && Array.isArray(model.groups) ? model.groups : [];
  return groups.filter(isObj).map((g) => ({
    id: g.id,
    termId: g.termId,
    label: g.label === undefined ? null : g.label,
    missing: g.missing === undefined ? null : g.missing,
    items: flatten(g.items, 0, null, []),
  }));
}
