/* The URL is a serialization of (surface, selection, params).

   The product already had one addressing scheme — the citation grammar in citations.js,
   which the rail validates against live corpus ids and which every cross-surface link
   travels through. This does not introduce a second one. A hash URL is that same pair
   written down, and `#/cite/<kind>:<id>` is the citation itself, so a machine that can
   write a citation can write a link a human can open.

   Hash rather than history API: the server serves the SPA from a catch-all route, and a
   path-based router would put deep links at the mercy of that catch-all on every deploy.
   Nothing here touches the network.

   Everything in this file is pure. e2e/router-unit.mjs runs it with no DOM. */

import { routeCite, citeFor } from './citations.js';

/* Each surface's path segment, and which selection keys ride in the path rather than
   the query. Order matters: the keys are positional. `-` stands in for an absent
   leading key (a slot with no style: #/kit/-/door-main-entry).

   `style` carries a dossier SECTION after the style (#/style/craftsman/lineage) and a slot
   after that, honoured only in the kit section (#/style/craftsman/kit/cornice) — PRD phase 14,
   §E.1-§E.2. The section ids are citations.js's DOSSIER_SECTIONS; nothing here checks a
   segment against them, because a URL is written down and read back, not judged: the surface
   decides what an unknown section shows, and citeFor refuses to cite one.

   `glossary` is the address of the glossary and of one term in it (#/glossary,
   #/glossary/judgment-unjudged); `term:<id>` is the citation that lands there. Which component
   draws it is App's business, not this table's. */
export const SURFACE_PATHS = {
  overview: { path: '', keys: [] },
  phylogeny: { path: 'phylogeny', keys: ['style'] },
  style: { path: 'style', keys: ['style', 'section', 'slot'] },
  kit: { path: 'kit', keys: ['style', 'slot'] },
  faults: { path: 'faults', keys: ['fault'] },
  proportions: { path: 'proportions', keys: ['pack'] },
  glossary: { path: 'glossary', keys: ['term'] },
  candidates: { path: 'candidates', keys: ['candidate'] },
  workbench: { path: 'workbench', keys: [] },
  brief: { path: 'brief', keys: [] },
  drawings: { path: 'drawings', keys: [] },
  export: { path: 'export', keys: [] },
  transcription: { path: 'transcription', keys: [] },
};

/* The empty path, and where an unreadable one lands. */
export const DEFAULT_SURFACE = 'overview';
const ABSENT = '-';

const BY_PATH = {};
Object.entries(SURFACE_PATHS).forEach(([id, spec]) => { BY_PATH[spec.path] = id; });

/* Selection keys are the ones routeCite() can produce. Anything else in the query
   string is a filter, and belongs to the surface rather than to the record. Keeping
   the two sets apart is what lets useSurfaceFilters own the query without ever
   standing on a selection.

   Appended, never inserted: formatHash writes query keys in THIS order, so a key added in the
   middle would reorder the query of every existing link that carries two of them, and the
   same place would stop being the same link. */
export const SELECTION_KEYS = [
  'style', 'slot', 'fault', 'pack', 'candidate', 'finding', 'plan',
  'constraint', 'room', 'roomType', 'massing', 'parti', 'grouping', 'asset',
  'section', 'term',
];
const NUMERIC_KEYS = ['candidate'];

function coerce(key, value) {
  if (value == null || value === '') return undefined;
  if (NUMERIC_KEYS.includes(key)) {
    const n = Number(value);
    return Number.isFinite(n) ? n : undefined;
  }
  return value;
}

/* '#/kit/tidewater-georgian/door-main-entry?group=openings'
     → {surface:'kit', selection:{style, slot}, params:{group}}
   An unreadable hash resolves to the default surface rather than a blank screen. */
export function parseHash(hash) {
  const raw = String(hash || '').replace(/^#/, '');
  const qAt = raw.indexOf('?');
  const pathPart = qAt === -1 ? raw : raw.slice(0, qAt);
  const queryPart = qAt === -1 ? '' : raw.slice(qAt + 1);

  const segments = pathPart.split('/').filter((s) => s !== '');
  const query = {};
  new URLSearchParams(queryPart).forEach((v, k) => { query[k] = v; });

  // #/cite/<kind>:<id> — the citation grammar, verbatim, as a URL.
  if (segments[0] === 'cite') {
    const ref = decodeURIComponent(segments.slice(1).join('/'));
    const target = routeCite(ref);
    if (target) {
      return { surface: target.surface, selection: target.selection || {}, params: query };
    }
    return { surface: DEFAULT_SURFACE, selection: {}, params: {} };
  }

  const surface = BY_PATH[segments[0] || ''] || DEFAULT_SURFACE;
  const spec = SURFACE_PATHS[surface];
  const selection = {};

  spec.keys.forEach((key, i) => {
    const seg = segments[i + 1];
    if (seg == null || seg === ABSENT) return;
    const v = coerce(key, decodeURIComponent(seg));
    if (v !== undefined) selection[key] = v;
  });

  // Selection keys a surface does not carry in its path still travel, in the query.
  const params = {};
  Object.entries(query).forEach(([k, v]) => {
    if (SELECTION_KEYS.includes(k) && !spec.keys.includes(k)) {
      const c = coerce(k, v);
      if (c !== undefined) selection[k] = c;
    } else if (!spec.keys.includes(k)) {
      params[k] = v;
    }
  });

  return { surface, selection, params };
}

export function formatHash(surface, selection, params) {
  const spec = SURFACE_PATHS[surface] ? surface : DEFAULT_SURFACE;
  const { path, keys } = SURFACE_PATHS[spec];
  const sel = selection || {};

  const segs = keys.map((k) => (sel[k] == null || sel[k] === '' ? ABSENT : encodeURIComponent(sel[k])));
  while (segs.length && segs[segs.length - 1] === ABSENT) segs.pop();   // no trailing '-'

  const query = new URLSearchParams();
  // Selection keys with nowhere in the path go to the query, in a stable order so a
  // link copied twice is the same link.
  SELECTION_KEYS.forEach((k) => {
    if (keys.includes(k)) return;
    if (sel[k] == null || sel[k] === '') return;
    query.set(k, String(sel[k]));
  });
  Object.keys(params || {}).sort().forEach((k) => {
    const v = params[k];
    if (v == null || v === '' || v === false) return;
    query.set(k, String(v));
  });

  const qs = query.toString();
  return '#/' + [path, ...segs].filter((s) => s !== '').join('/') + (qs ? '?' + qs : '');
}

/* The citation that names the current place, or null where none does. */
export function citeForPlace(surface, selection) {
  return citeFor(surface, selection);
}

/* '#/cite/style:craftsman' — the form to hand a machine, or paste in a chat. */
export function citeHref(ref) {
  return ref ? '#/cite/' + ref : null;
}

/* Context carry (PRD phase 14, §E.5). A reader studying Craftsman who follows a link from its
   dossier to a pack, a fault or the brief should arrive still holding Craftsman — and every
   hop used to drop it, because a citation names ONE record and nothing else travelled.

   This table is the whole of what may travel, per target surface, and it is §E.4's list of the
   selection keys each surface honours: the fault list reads `style` from its selection to
   choose whose exceptions it shows (FaultCorpus's filter spec), and §E.4 gives the pack page
   and the brief the same key. A surface with no entry receives nothing — a style riding into a
   place that ignores it is state in the URL that means nothing and reads as though it did.
   `style` is a SELECTION key everywhere, so the carried value is a named record in the
   address, not a filter, and survives a copied link. */
export const CONTEXT_KEYS = Object.freeze({
  proportions: Object.freeze(['style']),
  faults: Object.freeze(['style']),
  brief: Object.freeze(['style']),
});

/* {surface, selection} + ctx → a new target whose selection gains ctx[k] for each k its
   surface lists in CONTEXT_KEYS, where ctx[k] is a non-empty string and the target names no
   value of its own for k. The target always wins, since a citation that names a style means
   that style; a key not listed is dropped; a surface with no entry comes back unchanged; a
   null target stays null, so an unresolvable citation still goes nowhere. Never mutates. */
export function withContext(target, ctx) {
  if (!target) return null;
  const keys = CONTEXT_KEYS[target.surface];
  if (!keys || !ctx) return target;
  const selection = { ...(target.selection || {}) };
  keys.forEach((k) => {
    const v = ctx[k];
    if (typeof v !== 'string' || v === '') return;
    if (selection[k] != null && selection[k] !== '') return;     // the target always wins
    selection[k] = v;
  });
  return { ...target, selection };
}

/* The canonical address a citation opens, carrying the context its target honours, or null
   for a citation that resolves nowhere. The same composition nav.cite writes, so a link drawn
   as an anchor and a link followed by a click land in one place. */
export function hrefFor(cite, ctx) {
  const t = withContext(routeCite(cite), ctx);
  return t ? formatHash(t.surface, t.selection, {}) : null;
}
