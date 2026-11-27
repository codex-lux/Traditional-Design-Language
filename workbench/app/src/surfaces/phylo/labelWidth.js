/* THE FAMILY TREE'S NAME COLUMN GIVES WAY IN A NARROW PANE (WP-18.5, 27 Nov 2026).

   It is 260 px so that a tradition's name clears its own lane rule. With the assistant open at
   1280 px the chart's pane is about 340 px, and a fixed 260 left the time axis 76 px: the axis's
   two captions and the peer-trunk note ran out of the pane, and the chart scrolled sideways 95 px
   inside. The column is a share of the chart it stands in, between a floor and that 260.

   A leaf, so the arithmetic is under `node --test` without a bundle. Unmeasured (no width yet, or
   a width that is not a number) it is the 260: a first paint is the wide chart's. */
export const LABEL_MAX = 260;
export const LABEL_MIN = 150;
export const LABEL_SHARE = 0.36;

export function labelWidth(chartW) {
  if (!Number.isFinite(chartW) || chartW <= 0) return LABEL_MAX;
  return Math.max(LABEL_MIN, Math.min(LABEL_MAX, Math.round(chartW * LABEL_SHARE)));
}
