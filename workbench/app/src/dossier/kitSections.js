/* A kit's rows under their slot groups (WP-18.1). Pure.

   The kit table was one alphabetical run of slot ids with the group's id repeated down a column.
   It is the ontology's groups in the ontology's order now, each a heading over its slots.

   EVERY ROW IS RETURNED EXACTLY ONCE. A row whose group the overview does not name is kept, under
   its own id, after the named groups: a slot is never dropped for want of a heading. A group with
   no row is left out, so a filter shows only the groups it keeps. */
export function kitSections(groups, rows) {
  const named = Array.isArray(groups) ? groups.filter((g) => g && typeof g.id === 'string') : [];
  const list = Array.isArray(rows) ? rows : [];
  const known = new Set(named.map((g) => g.id));
  const strays = [];
  for (const r of list) if (!known.has(r.group) && !strays.includes(r.group)) strays.push(r.group);
  return [
    ...named.map((g) => ({ id: g.id, name: g.name || g.id, rows: list.filter((r) => r.group === g.id) })),
    ...strays.map((g) => ({ id: String(g), name: String(g), rows: list.filter((r) => r.group === g) })),
  ].filter((sec) => sec.rows.length > 0);
}
