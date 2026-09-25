/* WHAT A PACK PAGE SAYS, IN WHAT ORDER, DECIDED WITHOUT REACT (WP-14.9, PRD §E.4, §H.1-§H.2, §I.9).

   Lucas read the Proportions surface on `trim-classical` and found "a bunch of text": the page
   opened on INVARIANTS · PROVED AGAINST THE DATA, drew nothing, and put the pack's own conflicts
   at the foot. A practitioner reads a pack the other way round -- what it is, the drawing, what
   goes wrong with it today, the figures at MY building, whose figures they are, who uses the
   pack, where it comes from, and only then how it was checked. This module is that order and
   every other decision the page makes about a payload, as pure functions, so each is driven under
   `node --test` and `surfaces/Proportions.jsx` is left to draw.

   THE ORDER IS ONE LIST, `PAGE_SECTIONS`, AND THE PAGE RENDERS BY WALKING IT. `pageSections()`
   is the only thing that decides which sections a payload shows; a section it leaves out has
   nothing to show, and the proof is never left out -- it is FOLDED (per-browser memory,
   `state/prefs.js`'s `proof` key) and counted, because a check that is hidden is not a check
   that is absent.

   UNJUDGED IS ITS OWN STATE. An invariant's `holds: null` is what the engine writes when it
   could not evaluate one (`proportion_engine.py`), and a rule `out_of_calibration` or
   `scope_unjudged` has a figure and no verdict on it; `judgment.js` is the one reading of all of
   them and nothing here collapses the third state into either of the others.

   COUNTS ARE THE PAYLOAD'S. Nothing in this file states how many of anything a pack has.

   Pure; imports only the router's address writer, the corpus's notation and the verdict leaf. */
import { formatHash } from '../router.js';
import { feetInches16 } from '../fmt.js';
import { judgmentOf, JUDGMENT_MARK, JUDGMENT_STATES } from '../judgment.js';

/* The page, top to bottom. Appended, never reordered: the walk and `proportionsPage.test.mjs`
   hold the plate before the proof. */
export const PAGE_SECTIONS = Object.freeze([
  'head', 'plate', 'conflicts', 'rules', 'authorities', 'used-by', 'sources', 'proof',
]);

/* The `folds` key for "How this was checked" (PRD §I.10). */
export const PROOF_FOLD = 'proof';

/* The query keys this surface honours besides the pack (PRD §E.4). The three measures are a
   READING of the pack, not a narrowing of the list, which is what `widens` tells the strip's
   "N narrowing · clear" (`filters/useFilters.js`). `style` is a selection key and rides in the
   router's selection; it is listed so the strip can clear it. */
export const FILTER_SPEC = Object.freeze({
  q: Object.freeze({ type: 'text' }),
  ceiling: Object.freeze({ widens: true }),
  opening: Object.freeze({ widens: true }),
  diameter: Object.freeze({ widens: true }),
});

/* The column diameter an order pack is dimensioned at when the address names none: the
   authorities route's own default (`app.py`), so the plate and the comparison beside it are
   drawn at one diameter. */
export const DEFAULT_DIAMETER_IN = 12;

/* The ranges the three sliders offer. A value in the address outside them is still what is
   READ (the URL decides); the slider merely shows its nearest end. */
export const RANGES = Object.freeze({
  diameter: Object.freeze({ min: 6, max: 36, step: 1 }),
  ceiling: Object.freeze({ min: 84, max: 144, step: 2 }),
  opening: Object.freeze({ min: 18, max: 96, step: 2 }),
});

/* A measure from the address → a finite positive number, or null. A malformed value is not a
   measure, and reading it as 0 would dimension a pack at nothing. */
export function measureParam(raw) {
  if (raw == null || raw === '') return null;
  const n = typeof raw === 'number' ? raw : Number(String(raw).trim());
  return Number.isFinite(n) && n > 0 ? n : null;
}

/* What the request asks for: the address's measures, and for an order pack a diameter (the
   route default where the address names none). A measure the address does not name is NOT sent,
   so a pack whose module is bound to the ceiling is dimensioned at its own default (PRD §E.4). */
export function requestFor({ isOrder, params }) {
  const p = params || {};
  const out = { members: true };
  if (isOrder) out.column_diameter = measureParam(p.diameter) ?? DEFAULT_DIAMETER_IN;
  const ceiling = measureParam(p.ceiling);
  const opening = measureParam(p.opening);
  if (ceiling !== null) out.ceiling_height = ceiling;
  if (opening !== null) out.opening_width = opening;
  return out;
}

/* Where a slider rests: the address's value, else what the payload was dimensioned at, else the
   stated fallback -- clamped to the slider's own range, since a range input cannot show more. */
export function sliderAt(key, params, served, fallback) {
  const r = RANGES[key];
  const v = measureParam((params || {})[key]) ?? measureParam(served) ?? fallback;
  return Math.min(r.max, Math.max(r.min, v));
}

/* Which plate a payload asks for. `drawing` is the server's word (PRD §H.1): "stack" is the order
   plate, "assemblies" the wall-datum plate, and null a pack with nothing to draw -- refused out
   loud, never a picture of something the record does not hold. */
export function plateKind(data) {
  const d = data && data.drawing;
  if (d === 'stack') return 'stack';
  if (d === 'assemblies') return 'assemblies';
  return 'none';
}

/* The faces a served assembly draws. Equal to its members except where side-by-side members
   draw only the first (`sums_check: false`, PRD §0.1 #4), so the plate's band count is read from
   here and never from the member lists. */
export function faceCount(assemblies) {
  return (Array.isArray(assemblies) ? assemblies : []).reduce((n, a) => {
    const faces = a && a.geometry && Array.isArray(a.geometry.faces) ? a.geometry.faces : [];
    return n + faces.length;
  }, 0);
}

/* The sections a payload shows, in PAGE_SECTIONS order. `authorities` is the comparison rows
   (an order pack's, or none). The head, the plate and the proof are always shown: the plate
   SAYS when there is nothing to draw, and the proof is folded, never removed. */
export function pageSections(data, { authorities } = {}) {
  if (!data) return [];
  const has = {
    head: true,
    plate: true,
    conflicts: Array.isArray(data.conflicts) && data.conflicts.length > 0,
    rules: Array.isArray(data.derived_rules) && data.derived_rules.length > 0,
    authorities: Array.isArray(authorities) && authorities.length > 0,
    'used-by': Boolean(data.used_by && typeof data.used_by === 'object'),
    sources: authorityLines(data).length > 0,
    proof: true,
  };
  return PAGE_SECTIONS.filter((s) => has[s]);
}

/* The pack's authority statements: the pack's own, then any assembly's that differs from it (an
   overlay states some assemblies itself). Payload words, deduplicated, in order. */
export function authorityLines(data) {
  const out = [];
  const add = (s) => { if (typeof s === 'string' && s.trim() && !out.includes(s)) out.push(s); };
  if (data) {
    add(data.authority);
    for (const a of Array.isArray(data.assemblies) ? data.assemblies : []) add(a && a.authority);
  }
  return out;
}

/* A pack's authority in the words the index prints under its name. TWO ROUTES SERVE TWO SHAPES
   UNDER ONE KEY: `GET /api/proportions/<id>` gives `authority` as the record's `source` string,
   and the list `GET /api/proportions` gives the pack's whole authority record -- `source`,
   `author`, `year`, `strength`, `note`, sometimes `url`. The index rendered the list's object as
   a React child and the whole surface went blank (React error #31, found by opening the page).
   Who and when, from the record's own fields: the author where one is stated (54 of 57) and the
   source otherwise, then the year -- never a word the record does not carry. */
export function authorityWords(a) {
  if (typeof a === 'string') return a.trim();
  if (!a || typeof a !== 'object') return '';
  const who = (typeof a.author === 'string' && a.author.trim())
    || (typeof a.source === 'string' && a.source.trim()) || '';
  const year = Number.isFinite(a.year) ? String(a.year) : '';
  return [who, year].filter(Boolean).join(', ');
}

/* ─────────────────────────────── the proof ─────────────────────────────── */

/* An invariant's `holds` → the `JudgmentMark` state. The ONE reading (PRD §I.9): `null` is
   unjudged and never a fail. */
export function invariantMark(holds) {
  return JUDGMENT_MARK[judgmentOf(holds)];
}

/* How many invariants each verdict holds, all three counted -- the fold's summary line. */
export function invariantTally(invariants) {
  const t = Object.fromEntries(JUDGMENT_STATES.map((s) => [s, 0]));
  for (const iv of Array.isArray(invariants) ? invariants : []) t[judgmentOf(iv && iv.holds)] += 1;
  return t;
}

/* Is "How this was checked" open? Only when the reader opened it: folded by default. */
export function proofOpen(fold) {
  return fold === true;
}

/* ─────────────────────────────── the rules ─────────────────────────────── */

/* A derived rule's verdict on its own range. A rule the sources leave to the reader
   (`judgment`), one the engine could not evaluate (`error`, no value), and one worked outside
   the rooms it was calibrated for or whose scope could not be judged all have NO verdict --
   `out_of_calibration` and `scope_unjudged` read as not judged (PRD §J.4). */
export function ruleState(r) {
  const rule = r || {};
  if (rule.judgment || rule.error || rule.value == null) return 'unjudged';
  if (rule.out_of_calibration || rule.scope_unjudged) return 'unjudged';
  return judgmentOf(rule.in_range);
}

/* A figure in the corpus's notation: inches as feet-inches to a sixteenth, anything else as the
   number and its unit. */
export function figureWords(value, units) {
  if (value == null) return null;
  if (units === 'in' && typeof value === 'number') return feetInches16(value);
  return units ? `${value} ${units}` : String(value);
}

export function rangeWords(r) {
  const range = r && Array.isArray(r.range) ? r.range : null;
  if (!range || range.length !== 2) return null;
  return `${figureWords(range[0], r.units)} – ${figureWords(range[1], r.units)}`;
}

/* ─────────────────────────────── who uses it ─────────────────────────────── */

/* `used_by` (PRD §H.2) → the groups the page lists, each with the glossary record that names the
   relation, in the order a reader asks: who binds it, who asked for it, who merely receives it,
   and who the pack names without reaching. Empty groups are left out. `applies_to_only` has no
   glossary record of its own (`term: null`); the page names the field it reads. */
export function usedByGroups(usedBy) {
  const u = usedBy && typeof usedBy === 'object' ? usedBy : {};
  const delivered = Array.isArray(u.delivered) ? u.delivered : [];
  const groups = [
    { key: 'own', term: 'pack-own', rows: (u.own || []).map((style) => ({ style })) },
    { key: 'opted-in', term: 'pack-opted-in',
      rows: delivered.filter((d) => d && d.opted_in).map((d) => ({ style: d.style, from: d.from, role: d.role })) },
    { key: 'delivered', term: 'pack-delivered',
      rows: delivered.filter((d) => d && !d.opted_in).map((d) => ({ style: d.style, from: d.from, role: d.role })) },
    { key: 'applies-to-only', term: null, rows: (u.applies_to_only || []).map((style) => ({ style })) },
  ];
  return groups.filter((g) => g.rows.length > 0);
}

/* The relation between the style a reader holds (`?style=`) and this pack, read off
   `GET /api/styles/<style>/packs` (PRD §H.3) -- five provenances, each a glossary record, or
   'none' where the pack reaches the style by no route. */
const REACH = Object.freeze([
  ['own', 'pack-own'], ['opted_in', 'pack-opted-in'], ['withheld', 'pack-withheld'],
  ['declined', 'pack-declined'],
]);

export function reachOf(stylePacks, packId) {
  const sp = stylePacks && typeof stylePacks === 'object' ? stylePacks : null;
  if (!sp || !packId) return null;
  for (const [key, term] of REACH) {
    const hit = (sp[key] || []).find((c) => c && c.pack === packId);
    if (hit) return { relation: key, term, from: hit.from || null, fromName: hit.from_name || null };
  }
  for (const g of sp.delivered || []) {
    if ((g.packs || []).some((c) => c && c.pack === packId)) {
      return { relation: 'delivered', term: 'pack-delivered', from: g.from || null, fromName: g.from_name || null };
    }
  }
  return { relation: 'none', term: null, from: null, fromName: null };
}

/* The pack ids a style receives (own, opted in, delivered) -- what `?style=` narrows the index
   to. Withheld and declined packs do not reach the style, so they are not its packs. */
export function packsOfStyle(stylePacks) {
  const sp = stylePacks && typeof stylePacks === 'object' ? stylePacks : {};
  const ids = new Set();
  for (const c of [...(sp.own || []), ...(sp.opted_in || [])]) if (c && c.pack) ids.add(c.pack);
  for (const g of sp.delivered || []) for (const c of g.packs || []) if (c && c.pack) ids.add(c.pack);
  return ids;
}

/* ─────────────────────────────── the list ─────────────────────────────── */

/* The pack list (`GET /api/proportions`, already in the server's kind order) → groups by kind,
   in first-appearance order. `keep` is the pack on screen, which survives any filter: a plate
   drawn for a pack whose row the list has hidden is a lie about where you are. `only` narrows to
   a style's packs. `words(kind)` is the glossary's word for a kind, so a reader typing the word
   they see finds it. */
export function packGroups(packs, { q = '', keep = null, only = null, words = null, matches } = {}) {
  const list = Array.isArray(packs) ? packs : [];
  const groups = [];
  for (const p of list) {
    if (!p || !p.id) continue;
    const on = p.id === keep;
    if (!on && only && !only.has(p.id)) continue;
    const kindWord = words ? words(p.kind) : null;
    const authority = authorityWords(p.authority);
    const hit = !q || (matches ? matches({ ...p, kindWord, authority }, q, ['id', 'name', 'kind', 'kindWord', 'authority'])
      : [p.id, p.name, p.kind, kindWord, authority].some((s) => typeof s === 'string'
        && s.toLowerCase().includes(String(q).toLowerCase())));
    if (!on && !hit) continue;
    let g = groups.find((x) => x.kind === p.kind);
    if (!g) { g = { kind: p.kind, packs: [] }; groups.push(g); }
    g.packs.push(p);
  }
  return groups;
}

/* The address of a pack on this surface, keeping the reader's measures, filter and style: a pack
   click is a different record on the same page, not a new page (`nav.select`). */
export function packHref(packId, selection, params) {
  return formatHash('proportions', { ...(selection || {}), pack: packId }, params || {});
}

/* An assembly's name. The record gives an assembly an id and nothing else, so the page shows
   the id as words -- the same characters, never a name made up for it. */
export function assemblyWords(id) {
  return typeof id === 'string' ? id.replace(/_/g, ' ') : '';
}

/* The authorities route's order for an order pack: `<authority>-<order>` → `<order>`. */
export function orderOf(packId) {
  return typeof packId === 'string' && packId.includes('-') ? packId.split('-').slice(1).join('-') : null;
}
