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
   leading key (a slot with no style: #/style/-/kit/door-main-entry).

   `style` carries a dossier SECTION after the style (#/style/craftsman/lineage) and a slot
   after that, honoured only in the kit section (#/style/craftsman/kit/cornice) — PRD phase 14,
   §E.1-§E.2. The section ids are citations.js's DOSSIER_SECTIONS; nothing here checks a
   segment against them, because a URL is written down and read back, not judged: the surface
   decides what an unknown section shows, and citeFor refuses to cite one.

   `glossary` is the address of the glossary and of one term in it (#/glossary,
   #/glossary/judgment-unjudged); `term:<id>` is the citation that lands there. Which component
   draws it is App's business, not this table's.

   There is no `kit` surface (WP-14.12): the kit is a SECTION of the style's dossier now
   (#/style/<id>/kit/<slot>), and `#/kit/...` is an alias, read by LEGACY_PATHS below and never
   written. */
export const SURFACE_PATHS = {
  overview: { path: '', keys: [] },
  phylogeny: { path: 'phylogeny', keys: ['style'] },
  style: { path: 'style', keys: ['style', 'section', 'slot'] },
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

/* ADDRESSES THAT WERE PLACES AND ARE ALIASES NOW (WP-14.12, PRD §E.1).

   `#/kit/<style>/<slot>` has been the Kit surface's address since WP-5.6 made places URLs, and
   it is in commit messages, reports, the walk and every link a reader has kept. The kit moved into the
   style's dossier, so the old address is READ — positionally, with the same `-` placeholder — as
   the dossier's kit section, and never WRITTEN: `formatHash` answers the canonical form for it,
   and `state/nav.js` rewrites a legacy hash in the address bar by `replaceState`, as it rewrites a
   `#/cite/` link, so a refresh or a copied link carries the new address.

   `section: 'kit'` is set ONLY when a style or a slot is present. A bare `#/kit` named no style
   (it used to show Tidewater's kit, a default the URL never said), and its honest reading is the
   Styles index rather than the kit of a style nobody chose.

   `keys` are the legacy path's positional keys; `to` is the surface it now names; `section` the
   dossier section it opens. A table, so a second retired address is one row and not a branch. */
export const LEGACY_PATHS = Object.freeze({
  kit: Object.freeze({ keys: Object.freeze(['style', 'slot']), to: 'style', section: 'kit' }),
});

const legacyOf = (key) => (typeof key === 'string' && Object.prototype.hasOwnProperty.call(LEGACY_PATHS, key)
  ? LEGACY_PATHS[key] : null);

/* A legacy selection → the canonical one: the legacy keys kept, and the section added where the
   legacy address named a record at all. */
function fromLegacy(legacy, selection) {
  const sel = { ...(selection || {}) };
  delete sel.section;
  const named = legacy.keys.some((k) => sel[k] != null && sel[k] !== '');
  return named ? { ...sel, section: legacy.section } : sel;
}

/* Does this hash open with a retired path? `nav.canonicalize` asks, and rewrites it. */
export function isLegacyHash(hash) {
  const raw = String(hash || '').replace(/^#/, '');
  const first = raw.split('?')[0].split('/').filter((s) => s !== '')[0];
  return legacyOf(first) !== null;
}

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

/* '#/style/tidewater-georgian/kit/door-main-entry?group=openings'
     → {surface:'style', selection:{style, section:'kit', slot}, params:{group}}
   A legacy '#/kit/tidewater-georgian/door-main-entry' reads as the same place (LEGACY_PATHS).
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
      // A citation's own params (a brief's `example`) win over the link's query, as its own
      // selection keys win over a carried context.
      return { surface: target.surface, selection: target.selection || {},
        params: { ...query, ...(target.params || {}) } };
    }
    return { surface: DEFAULT_SURFACE, selection: {}, params: {} };
  }

  const legacy = legacyOf(segments[0]);
  const surface = legacy ? legacy.to : (BY_PATH[segments[0] || ''] || DEFAULT_SURFACE);
  const spec = SURFACE_PATHS[surface];
  let selection = {};

  (legacy ? legacy.keys : spec.keys).forEach((key, i) => {
    const seg = segments[i + 1];
    if (seg == null || seg === ABSENT) return;
    const v = coerce(key, decodeURIComponent(seg));
    if (v !== undefined) selection[key] = v;
  });
  if (legacy) selection = fromLegacy(legacy, selection);

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

/* A retired surface id is written as the place it now names: `formatHash('kit', {style, slot})`
   is the dossier's kit section. Nothing in the app should still say `kit`, but a caller that does
   (a rail item, a door, a palette entry) lands where the reader meant rather than on the Overview,
   and the address it writes is the canonical one. */
export function formatHash(surface, selection, params) {
  const legacy = legacyOf(surface);
  const sel = legacy ? fromLegacy(legacy, selection) : (selection || {});
  const target = legacy ? legacy.to : surface;
  const spec = SURFACE_PATHS[target] ? target : DEFAULT_SURFACE;
  const { path, keys } = SURFACE_PATHS[spec];

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

/* The address a legacy hash is rewritten to, or null for one that is not legacy. The query rides
   along as it was, filters included: `#/kit/craftsman?q=porch` was the kit filtered to porch, and
   so is the address it becomes. */
export function canonicalHash(hash) {
  if (!isLegacyHash(hash)) return null;
  const p = parseHash(hash);
  return formatHash(p.surface, p.selection, p.params);
}

/* The citation that names the current place, or null where none does. */
export function citeForPlace(surface, selection, params) {
  return citeFor(surface, selection, params);
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
  return t ? formatHash(t.surface, t.selection, t.params || {}) : null;
}
