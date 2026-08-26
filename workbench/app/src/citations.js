/* The citation grammar: kind:id(#fragment)?  —  one router for the whole product.
   Rail chips, finding rule refs and cross-surface links all come through here, so a
   citation anywhere navigates the canvas the same way.

   The id character class must stay identical to REF_RE in workbench/server/citations.py.
   It was not: the server allowed dots (its comment says why — constraint ids are
   style-id.cNN) and this half did not, so all 660 constraint ids validated on the server,
   streamed as citations, and then parsed to null here. Every `constraint:` chip the rail
   ever drew navigated nowhere, silently. WP-5.6 widened this class to match. */

export function parseCite(ref) {
  const m = /^([a-z]+):([A-Za-z0-9_.-]+)(?:#([A-Za-z0-9_-]+))?$/.exec(ref || '');
  if (!m) return null;
  return { kind: m[1], id: m[2], fragment: m[3] || null };
}

/* Returns {surface, selection} — App owns applying it. */
export function routeCite(ref) {
  const c = parseCite(ref);
  if (!c) return null;
  switch (c.kind) {
    // the full record beats the graph panel now that surface ③ exists;
    // the phylogeny stays one rail-click away and links back
    case 'style': return { surface: 'style', selection: { style: c.id } };
    case 'kit': return { surface: 'kit', selection: { style: c.id, slot: c.fragment } };
    case 'slot': return { surface: 'kit', selection: { slot: c.id } };
    case 'fault': return { surface: 'faults', selection: { fault: c.id } };
    case 'pack': return { surface: 'proportions', selection: { pack: c.id } };
    case 'candidate': return { surface: 'candidates', selection: { candidate: Number(c.id) } };
    case 'finding': return { surface: 'workbench', selection: { finding: c.id } };
    case 'plan': return { surface: 'workbench', selection: { room: c.id } };
    case 'constraint': return { surface: 'workbench', selection: { constraint: c.id } };
    case 'room': return { surface: 'workbench', selection: { roomType: c.id } };
    case 'massing': return { surface: 'phylogeny', selection: { massing: c.id } };
    case 'parti': return { surface: 'candidates', selection: { parti: c.id } };
    case 'grouping': return { surface: 'workbench', selection: { grouping: c.id } };
    case 'brief': return { surface: 'brief', selection: {} };
    case 'asset': return { surface: 'faults', selection: { asset: c.id } };
    default: return null;
  }
}

/* The inverse: what citation names this place? Lives beside routeCite so the two
   directions cannot drift — the URL scheme (router.js) is a serialization of exactly
   these pairs, and e2e/router-unit.mjs pins routeCite → citeFor as an identity for
   every kind but one.

   That one is `brief`: routeCite discards the id (there is a single brief), so no
   citation can be recovered from the surface. It returns null rather than inventing one.
   Where a surface holds several citable keys at once the most specific wins. */
export function citeFor(surface, selection) {
  const s = selection || {};
  switch (surface) {
    case 'style': return s.style ? 'style:' + s.style : null;
    case 'kit':
      if (s.style) return 'kit:' + s.style + (s.slot ? '#' + s.slot : '');
      return s.slot ? 'slot:' + s.slot : null;
    case 'faults':
      if (s.fault) return 'fault:' + s.fault;
      return s.asset ? 'asset:' + s.asset : null;
    case 'proportions': return s.pack ? 'pack:' + s.pack : null;
    case 'candidates':
      if (s.parti) return 'parti:' + s.parti;
      return s.candidate != null ? 'candidate:' + s.candidate : null;
    case 'phylogeny':
      // A style on the phylogeny is not `style:` — that citation routes to the full
      // record by a decision recorded above. Only the massing has an exact inverse here.
      return s.massing ? 'massing:' + s.massing : null;
    case 'workbench':
      if (s.finding) return 'finding:' + s.finding;
      if (s.constraint) return 'constraint:' + s.constraint;
      if (s.room) return 'plan:' + s.room;
      if (s.roomType) return 'room:' + s.roomType;
      return s.grouping ? 'grouping:' + s.grouping : null;
    default: return null;
  }
}
