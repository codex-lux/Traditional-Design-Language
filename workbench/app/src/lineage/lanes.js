/* THE FAMILY TREE IN LANES, AND ITS ONE KNOWN CHRONOLOGY EXCEPTION (Phase 17, WP-17.12; board 10).

   `lanesOf(rows)` groups the taxa by the tradition each descends from (`styles/taxa.js`'s
   `traditionOf`, already on each row as `tradition`), in the order `laneOrder` gives -- the
   traditions' own hue order -- each lane in date order, and a taxon whose tradition is unknown in
   a remainder lane at the end rather than dropped.

   `chronologyExceptions(taxa, edges)` is `build/validate.py`'s own chronology warning, ported: a
   `descends_from` or `regional_of` edge whose descendant's floruit starts more than twenty-five
   years before its ancestor's. The validator WARNS on it and the tree had no way to show it; the
   rule is the validator's, and `tests/test_chronology_parity.py` holds the two to one answer.

   Pure. */
export const CHRONOLOGY_SLACK_YEARS = 25;
const KIN = new Set(['descends_from', 'regional_of']);

export function lanesOf(rows, laneOrder) {
  const order = Array.isArray(laneOrder) ? laneOrder : [];
  const lanes = order.map((id) => ({ id, rows: [] }));
  const rest = { id: null, rows: [] };
  const at = new Map(lanes.map((l) => [l.id, l]));
  for (const r of rows || []) (at.get(r.tradition) || rest).rows.push(r);
  for (const l of [...lanes, rest]) l.rows.sort((a, b) => (a.from - b.from) || String(a.id).localeCompare(String(b.id)));
  return rest.rows.length ? [...lanes, rest] : lanes;
}

/* The edges that break the chronology, each `{from, to, from_start, to_start}`. `from` is the
   descendant and `to` the ancestor, as `/api/phylogeny` writes them. */
export function chronologyExceptions(taxa, edges) {
  const by = new Map((taxa || []).map((t) => [t.id, t]));
  const out = [];
  for (const e of edges || []) {
    if (!KIN.has(e.type)) continue;
    const a = by.get(e.from), b = by.get(e.to);
    if (!a || !b || !Number.isFinite(a.floruit_start) || !Number.isFinite(b.floruit_start)) continue;
    if (a.floruit_start < b.floruit_start - CHRONOLOGY_SLACK_YEARS) {
      out.push({ from: e.from, to: e.to, from_start: a.floruit_start, to_start: b.floruit_start });
    }
  }
  return out;
}
