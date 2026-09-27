/* THE FAULT CORPUS READ FOR ONE STYLE, IN THE DOSSIER'S THREE GROUPS (WP-14.27, PRD §C.12).

   With a style in view the Fault Corpus listed all of the corpus's faults in one run and let
   the card say which licence the style earns -- so a reader who arrived from a style's dossier by
   "N more, written for every house" found those N nowhere in particular, and the faults the
   corpus reads for that style by name were interleaved with every universal one. The list groups
   now, three ways, in the order they matter to a reader of that style:

     here        the faults the corpus reads for this style by name: an exception it earns or is
                 refused, an inversion, or a severity its record states for it
     lineage     the faults written for this style, an ancestor or a family it is filed under,
                 rather than for every house
     universal   the rest of the faults that apply to it, written for every house

   THE PARTITION IS THE SERVER'S AND NOTHING HERE RE-DERIVES IT. `corpus.dossier_faults` is the
   one spelling (served as the dossier payload's `faults`, the same object the dossier's Faults
   section reads); it names the first two groups and COUNTS the third, because the dossier links
   to this page for the universal faults rather than listing them. So the universal group is the
   style's own fault list (`/api/faults?style=`, the call the partition is itself taken over) less
   the two named groups -- a set difference, not a rule -- and it is held to the partition's own
   count: where the two disagree the grouping is NOT drawn, because a group whose membership and
   whose served count differ is a list that has stopped meaning what its heading says.

   Each group's heading is its glossary record (`fault-group-*`); the ids are held to the records
   by `everyPick.test.mjs`, because a Term reached through this table is not a literal the
   glossary scanner can see.

   Pure; imports nothing. */

export const FAULT_GROUPS = Object.freeze([
  Object.freeze({ id: 'here', term: 'fault-group-here' }),
  Object.freeze({ id: 'lineage', term: 'fault-group-lineage' }),
  Object.freeze({ id: 'universal', term: 'fault-group-universal' }),
]);

const ids = (xs) => (Array.isArray(xs) ? xs.filter((x) => typeof x === 'string' && x) : null);

/** The style's faults in the partition's three groups, or `{ state: 'unjudged', reason }`.
 *  `partition` is the dossier payload's `faults` ({ verdict_here, lineage, universal_count,
 *  matches }); `styleIds` the ids `/api/faults?style=` returned for the same style. */
export function faultGroups(partition, styleIds) {
  const here = ids(partition && partition.verdict_here);
  const lineage = ids(partition && partition.lineage);
  const list = ids(styleIds);
  if (!here || !lineage || !list) {
    return { state: 'unjudged', reason: 'the partition or the style\'s fault list was not served' };
  }
  const named = new Set([...here, ...lineage]);
  const universal = list.filter((id) => !named.has(id));
  const listed = new Set(list);
  const strays = [...named].filter((id) => !listed.has(id));
  if (strays.length || universal.length !== partition.universal_count
      || list.length !== partition.matches) {
    return { state: 'unjudged',
      reason: `the partition names ${here.length + lineage.length} and counts `
        + `${partition.universal_count} of ${partition.matches}, and the style's list holds `
        + `${list.length}${strays.length ? `, not holding ${strays.join(', ')}` : ''}` };
  }
  return { state: 'ready', here, lineage, universal };
}

/** The rows of `list` (already narrowed by the page's other filters, in the page's own order)
 *  under each group that holds any: [{ id, term, rows }]. A group the filters have emptied is
 *  omitted, as the dossier omits an empty section. */
export function groupRows(list, groups) {
  if (!groups || groups.state !== 'ready') return null;
  return FAULT_GROUPS.map((g) => {
    const member = new Set(groups[g.id]);
    return { id: g.id, term: g.term, rows: (list || []).filter((f) => f && member.has(f.id)) };
  }).filter((g) => g.rows.length > 0);
}

/** Every fault id the style reads, whichever group holds it. */
export function styleFaultIds(groups) {
  if (!groups || groups.state !== 'ready') return null;
  return new Set([...groups.here, ...groups.lineage, ...groups.universal]);
}
