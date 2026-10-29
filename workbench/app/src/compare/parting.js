/* WHERE TWO STYLES PART IN THE GRAPH (Phase 17, WP-17.13; board 13).

   Each style's kit cascade is its lineage, nearest first (`GET /api/kit/{id}/cascade`). Two styles
   part at the nearest node both cascades hold: everything above it they share, and each one's
   levels below it are its own. A pair whose cascades share nothing part at no node, which is said
   rather than drawn. Pure. */
export function partingOf(cascadeA, cascadeB) {
  const a = (cascadeA && Array.isArray(cascadeA.cascade) ? cascadeA.cascade : []).map((r) => r.id);
  const b = (cascadeB && Array.isArray(cascadeB.cascade) ? cascadeB.cascade : []).map((r) => r.id);
  if (!a.length || !b.length) return null;
  const inB = new Set(b);
  const common = a.find((id) => inB.has(id)) || null;
  return {
    common,
    aOwn: common ? a.slice(0, a.indexOf(common)) : a,
    bOwn: common ? b.slice(0, b.indexOf(common)) : b,
  };
}
