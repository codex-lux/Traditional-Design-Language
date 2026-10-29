/* WHERE TWO STYLES PART IN THE GRAPH (Phase 17, WP-17.13; board 13).

   Each style's kit cascade is its lineage, nearest first (`GET /api/kit/{id}/cascade`), flattened
   from a graph, so two cascades can hold their shared nodes in different orders. The parting node is
   the shared node nearest to BOTH: the least sum of its positions in the two cascades, ties broken
   by id. So the answer is the same whichever style is named first -- the first version took the
   first shared id in A's order, and Phase 17's audit measured A->B and B->A disagreeing on 1,003 of
   1,500 random pairs. Each style's own levels are the ids in its cascade the other's does not hold;
   nothing is claimed about what lies above the node, because in a graph the two can share some of
   it and not the rest. A pair whose cascades share nothing part at no node. Pure. */
export function partingOf(cascadeA, cascadeB) {
  const a = (cascadeA && Array.isArray(cascadeA.cascade) ? cascadeA.cascade : []).map((r) => r.id);
  const b = (cascadeB && Array.isArray(cascadeB.cascade) ? cascadeB.cascade : []).map((r) => r.id);
  if (!a.length || !b.length) return null;
  const ib = new Map(b.map((id, i) => [id, i]));
  let common = null, best = Infinity;
  a.forEach((id, i) => {
    if (!ib.has(id)) return;
    const d = i + ib.get(id);
    if (d < best || (d === best && id < common)) { best = d; common = id; }
  });
  const inA = new Set(a), inB = new Set(b);
  return { common, aOwn: a.filter((id) => !inB.has(id)), bOwn: b.filter((id) => !inA.has(id)) };
}
