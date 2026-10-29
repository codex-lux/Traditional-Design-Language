/* WHO BINDS A SLOT ACROSS EVERY STYLE, AS A BAR (Phase 17, WP-17.13; board 12).

   The slot route serves four parts that partition the styles (`corpus.slot`'s `bindings`):
   specified (some of which a later node extended), forbidden, and open. This leaf turns them into
   four segments that sum to the whole -- specified by one writer, extended, forbidden, open -- each
   with its count and its share. The counts are the route's; nothing here counts styles. A payload
   missing any part draws no bar, because three parts of four would read as the whole. Pure. */
export const BINDING_PARTS = Object.freeze(['specified', 'extends', 'forbidden', 'open']);

export function bindingBar(bindings) {
  const b = bindings && typeof bindings === 'object' ? bindings : null;
  if (!b || !BINDING_PARTS.every((k) => Array.isArray(b[k])) || !Number.isInteger(b.of) || b.of <= 0) return null;
  const n = {
    specified: b.specified.length - b.extends.length,
    extends: b.extends.length,
    forbidden: b.forbidden.length,
    open: b.open.length,
  };
  return BINDING_PARTS.map((k) => ({ id: k, n: n[k], share: n[k] / b.of }));
}
