/* The citation grammar: kind:id(#fragment)?  —  one router for the whole product.
   Rail chips, finding rule refs and cross-surface links all come through here, so a
   citation anywhere navigates the canvas the same way. */

export function parseCite(ref) {
  const m = /^([a-z]+):([A-Za-z0-9_-]+)(?:#([A-Za-z0-9_-]+))?$/.exec(ref || '');
  if (!m) return null;
  return { kind: m[1], id: m[2], fragment: m[3] || null };
}

/* Returns {surface, selection} — App owns applying it. */
export function routeCite(ref) {
  const c = parseCite(ref);
  if (!c) return null;
  switch (c.kind) {
    case 'style': return { surface: 'phylogeny', selection: { style: c.id } };
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
