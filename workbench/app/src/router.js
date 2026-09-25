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
   written.

   THE RECORD PAGES (WP-14.23, tranche 2 PRD §B.1). `elements` is the index of the element slots
   and, with a slot, that slot's own page (#/elements/cornice); `room`, `massing`, `grouping` and
   `parti` are one record each (#/room/parlor), and each bare address is that kind's index, never
   a default record. Their one positional key is the selection key the citation already carried
   (`roomType`, because `room` names a PLACED room on the bench and `plan:` cites it), so a record
   page is the same (kind, id) pair the grammar always spoke, given a place of its own. Until they
   existed these citations landed on a surface that could not show them, under a "searched"
   banner. */
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
  elements: { path: 'elements', keys: ['slot'] },
  room: { path: 'room', keys: ['roomType'] },
  massing: { path: 'massing', keys: ['massing'] },
  grouping: { path: 'grouping', keys: ['grouping'] },
  parti: { path: 'parti', keys: ['parti'] },
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

/* PLACES THAT WERE A RECORD'S ONLY ADDRESS AND ARE ALIASES NOW (WP-14.23, tranche 2 PRD §B.3).

   Until the record pages existed, `routeCite` sent a slot, a room, a grouping, a massing and a
   parti to a surface that held the id in its selection and could not show the record: the slot
   panel under the Styles index (`#/style/-/kit/<slot>`), the bench (`#/workbench?roomType=`,
   `#/workbench?grouping=`), the family tree (`#/phylogeny?massing=`) and the candidates
   (`#/candidates?parti=`). People kept those links. Each is READ as the record page it meant and
   rewritten in the address bar by `replaceState` through `state/nav.js`, exactly as `#/kit/...`
   is, and `formatHash` writes the new address for one, so no writer mints an old one again.

   ONE ROW PER (SURFACE, KEY), NOT A BRANCH. `surface` and `key` are the old place and the
   selection key it carried; `to` the record surface, whose one path key is that same key (the
   router-unit suite holds that, so the id rides across unrenamed); `also` what else the old
   address had to hold to be that place (the slot panel was the kit SECTION with no style). A row
   applies only when the old selection holds its key, its `also`, and NOTHING ELSE: those are the
   addresses the old `routeCite` wrote, and a hand-built address naming more than one record is
   not one of them, so it is left standing rather than read as half of what it said. The old
   place's filters do not travel -- a surface boundary drops them, as `nav.go` does.

   `#/brief?parti=<id>` is NOT here: it is the parti bridge's seed (§C.5), a live place and not a
   retired one. */
const placeRow = (surface, key, to, also) => Object.freeze({ surface, key, to, also: Object.freeze(also || {}) });
export const LEGACY_PLACES = Object.freeze([
  placeRow('style', 'slot', 'elements', { section: 'kit' }),
  placeRow('workbench', 'roomType', 'room'),
  placeRow('workbench', 'grouping', 'grouping'),
  placeRow('phylogeny', 'massing', 'massing'),
  placeRow('candidates', 'parti', 'parti'),
]);

const filled = (v) => v != null && v !== '';

/* The LEGACY_PLACES row this (surface, selection) is, or null. */
export function legacyPlaceOf(surface, selection) {
  const sel = selection && typeof selection === 'object' ? selection : {};
  const held = Object.keys(sel).filter((k) => filled(sel[k]));
  for (const row of LEGACY_PLACES) {
    if (row.surface !== surface || !filled(sel[row.key])) continue;
    if (!Object.entries(row.also).every(([k, v]) => sel[k] === v)) continue;
    const allowed = new Set([row.key, ...Object.keys(row.also)]);
    if (held.every((k) => allowed.has(k))) return row;
  }
  return null;
}

/* Any place → the place the app lives at: a retired surface id (LEGACY_PATHS) read as the place
   it names, then a retired record address (LEGACY_PLACES) read as the record page. A canonical
   place comes back as it was. The one rule `parseHash` and `formatHash` both apply, and the one
   `nav/navModel.js::normalizePlace` reads, so the URL, the rail and the crumbs cannot name one
   place two ways. */
export function canonicalPlace(surface, selection, params) {
  const legacy = legacyOf(surface);
  const sel = legacy ? fromLegacy(legacy, selection) : { ...(selection || {}) };
  const target = legacy ? legacy.to : surface;
  const row = legacyPlaceOf(target, sel);
  if (row) return { surface: row.to, selection: { [row.key]: sel[row.key] }, params: {} };
  return { surface: target, selection: sel, params: { ...(params || {}) } };
}

/* Does this hash open with a retired path, or name a retired record address? `nav.canonicalize`
   asks, and rewrites it. */
export function isLegacyHash(hash) {
  const raw = String(hash || '').replace(/^#/, '');
  const first = raw.split('?')[0].split('/').filter((s) => s !== '')[0];
  if (legacyOf(first) !== null) return true;
  const p = readHash(hash);
  return legacyPlaceOf(p.surface, p.selection) !== null;
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
   A legacy '#/kit/tidewater-georgian/door-main-entry' reads as the same place (LEGACY_PATHS), and
   a retired record address as its record page (LEGACY_PLACES): '#/workbench?roomType=parlor' is
   {surface:'room', selection:{roomType:'parlor'}}. An unreadable hash resolves to the default
   surface rather than a blank screen. */
export function parseHash(hash) {
  const p = readHash(hash);
  return canonicalPlace(p.surface, p.selection, p.params);
}

/* The hash as written, a retired PATH already read as the surface it names but a retired record
   ADDRESS not yet rewritten -- which is what `isLegacyHash` needs to see. */
function readHash(hash) {
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
   and the address it writes is the canonical one. A retired record address is written the same
   way: `formatHash('workbench', {roomType})` is the room's page (WP-14.23), and a slot panel with
   its style cleared -- the dossier's picker set to none on a kit slot -- writes the slot's page. */
export function formatHash(surface, selection, params) {
  const place = canonicalPlace(surface, selection, params);
  const sel = place.selection;
  params = place.params;
  const spec = SURFACE_PATHS[place.surface] ? place.surface : DEFAULT_SURFACE;
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

/* The address a legacy hash is rewritten to, or null for one that is not legacy. A retired PATH
   keeps its query, filters included: `#/kit/craftsman?q=porch` was the kit filtered to porch, and
   so is the address it becomes. A retired record ADDRESS drops its query, because the filters
   were the old surface's and the record page reads none of them (LEGACY_PLACES). */
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
