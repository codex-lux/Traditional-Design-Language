/* A STYLE'S PERIOD, DRAWN AS A BAR (Phase 17, WP-17.9; board 7).

   The style record states its period as four soft dates and a list of revivals
   (`schema/style-node.schema.json`'s `period`). The dossier printed none of them as a figure; the
   board draws them on one axis: origin to floruit as a thin lead-in, the floruit as the body,
   floruit to decline as a fading tail, and each revival as its own short bar further along.

   A DATE THE RECORD DOES NOT STATE IS NOT DRAWN AND IS SAID. `origin` and `decline_end` may be null
   and are on 27 and 52 of the corpus's records; where one is missing its segment is absent and the
   segment is listed in `unstated`, so the bar never interpolates a date the corpus declines to
   give. The axis spans the stated dates with a margin. Pure. */
const num = (v) => (Number.isInteger(v) ? v : null);

export function periodBar(period) {
  const p = period && typeof period === 'object' ? period : {};
  const fs = num(p.floruit_start), fe = num(p.floruit_end);
  if (fs === null || fe === null) return null;
  const origin = num(p.origin), decline = num(p.decline_end);
  const revivals = (Array.isArray(p.revival_periods) ? p.revival_periods : [])
    .filter((r) => num(r.start) !== null && num(r.end) !== null);
  const years = [fs, fe, origin, decline, ...revivals.flatMap((r) => [r.start, r.end])].filter((y) => y !== null);
  const lo = Math.min(...years), hi = Math.max(...years);
  const pad = Math.max(10, Math.round((hi - lo) * 0.06));
  const from = lo - pad, to = hi + pad;
  const at = (y) => (y - from) / (to - from);
  const seg = (id, a, b) => ({ id, from: a, to: b, x0: at(a), x1: at(b) });
  const segments = [];
  if (origin !== null && origin < fs) segments.push(seg('origin', origin, fs));
  segments.push(seg('floruit', fs, fe));
  if (decline !== null && decline > fe) segments.push(seg('decline', fe, decline));
  revivals.forEach((r) => segments.push({ ...seg('revival', r.start, r.end), node: r.revival_node || null }));
  const unstated = [origin === null && 'origin', decline === null && 'decline'].filter(Boolean);
  return { from, to, circa: p.circa !== false, segments, unstated };
}
