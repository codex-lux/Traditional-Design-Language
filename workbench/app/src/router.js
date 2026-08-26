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
   leading key (a slot with no style: #/kit/-/door-main-entry). */
export const SURFACE_PATHS = {
  phylogeny: { path: 'phylogeny', keys: ['style'] },
  style: { path: 'style', keys: ['style'] },
  kit: { path: 'kit', keys: ['style', 'slot'] },
  faults: { path: 'faults', keys: ['fault'] },
  proportions: { path: 'proportions', keys: ['pack'] },
  candidates: { path: 'candidates', keys: ['candidate'] },
  workbench: { path: '', keys: [] },
  brief: { path: 'brief', keys: [] },
  drawings: { path: 'drawings', keys: [] },
  export: { path: 'export', keys: [] },
  transcription: { path: 'transcription', keys: [] },
};

/* The empty path. Stage D of WP-5.6 moves this to the Overview surface; until that
   surface exists the landing stays where it has always been. */
export const DEFAULT_SURFACE = 'workbench';
const ABSENT = '-';

const BY_PATH = {};
Object.entries(SURFACE_PATHS).forEach(([id, spec]) => { BY_PATH[spec.path] = id; });

/* Selection keys are the ones routeCite() can produce. Anything else in the query
   string is a filter, and belongs to the surface rather than to the record. Keeping
   the two sets apart is what lets useSurfaceFilters own the query without ever
   standing on a selection. */
export const SELECTION_KEYS = [
  'style', 'slot', 'fault', 'pack', 'candidate', 'finding', 'plan',
  'constraint', 'room', 'roomType', 'massing', 'parti', 'grouping', 'asset',
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
