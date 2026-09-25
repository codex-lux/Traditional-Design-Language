/* THE SITE MAP, IN ONE PURE MODULE (WP-14.13, PRD §F).

   The workbench had three app-written catalogues of its own places — the rail
   (`Chrome.surfaces()`), the Overview's DOORS, and the palette's `short` lines — and they
   disagreed with each other about what the places were called, which group they were in, and
   which one to start at. This file is the one account now. The rail, the crumbs
   (`nav/crumbs.js`), the front door's two-spine map, the palette's surface entries and the
   browser walk all read `NAV` or `navModel()`, and none of them keeps a list of its own.

   IT HOLDS IDS, NEVER WORDS. `NAV` is the frozen table of §F.1 — group ids, item ids, surfaces
   and the glossary record each is called by — and every word a reader sees is that record's
   `term`, looked up here through `glossary/lookup.js`. A record the glossary does not hold comes
   back as `label: null` and `missing: <id>`, and the renderer prints `noEntry(id)` visibly: the
   app does not write a rail label, a group heading or a description, which is the ruling of
   24 September 2026 applied to the navigation.

   A META IS A FIGURE FROM THE API OR A JOURNEY WORD, AND NOTHING ELSE. The count beside "Find a
   style" is `/api/overview`'s `counts.styles`; beside Proportions, the sum of
   `counts.proportion_packs`; beside Faults, `counts.faults`; beside the Glossary, the glossary's
   own `count`; beside a house step, the words `journey/journey.js` says for that step; beside a
   dossier section, that section's `count` from the style's dossier. A figure the caller did not
   pass is `null` and nothing is printed — never a number written here, because a count in the
   app goes stale the day the corpus moves (the rail said "9 sections", the Kit "95 slots"
   against 97, the Fault Corpus "209" against 210).

   STEP NUMBERS ARE THE JOURNEY'S ORDER. A house item's `step` is its surface's index in
   `JOURNEY` plus one, so moving a step moves its number; Trace a drawing is not a step (it
   joins at the plan) and carries none.

   THE URL DECIDES WHAT IS READ; MEMORY ONLY OFFERS (§F.4). The style in hand is an item — a
   LINK to that style's dossier — and nothing here reads it into a selection or a URL. Its
   sections are listed only while that very dossier is the page shown, because a list of the
   in-hand style's sections under a different style's page would be a second place pretending
   to be this one.

   Pure: no React, no DOM, no fetch. `src/navModel.test.mjs` drives it with the glossary records
   read from `glossary/*.json`. */
import { formatHash } from '../router.js';
import { parseCite, DOSSIER_SECTIONS } from '../citations.js';
import { JOURNEY } from '../journey/journey.js';
import { isMissing } from '../glossary/lookup.js';

const item = (id, surface, termId, extra) => Object.freeze({ id, surface, termId, ...(extra || {}) });
const group = (id, termId, items) => Object.freeze({ id, termId, items: Object.freeze(items) });

/* §F.1, ids and surfaces only. `in-hand` has no record of its own: it is named by the style it
   holds. */
export const NAV = Object.freeze([
  group('start', 'nav-group-start', [
    item('overview', 'overview', 'surface-overview'),
  ]),
  group('styles', 'nav-group-styles', [
    item('style', 'style', 'surface-style'),
    item('in-hand', 'style', null),
    item('phylogeny', 'phylogeny', 'surface-phylogeny'),
  ]),
  group('a-house', 'nav-group-a-house', [
    item('brief', 'brief', 'surface-brief'),
    item('candidates', 'candidates', 'surface-candidates'),
    item('workbench', 'workbench', 'surface-workbench', {
      children: Object.freeze([item('transcription', 'transcription', 'surface-transcription')]),
    }),
    item('drawings', 'drawings', 'surface-drawings'),
    item('export', 'export', 'surface-export'),
  ]),
  group('library', 'nav-group-library', [
    item('proportions', 'proportions', 'surface-proportions'),
    item('faults', 'faults', 'surface-faults'),
    item('glossary', 'glossary', 'surface-glossary'),
  ]),
]);

/* The separator between the in-hand style's name and the guided-example term. Punctuation, not
   a word. */
const SEP = ' · ';

const isObj = (v) => Boolean(v) && typeof v === 'object' && !Array.isArray(v);
const str = (v) => (typeof v === 'string' && v.trim() ? v.trim() : null);
const num = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : null);

/* A record's word, or `{label: null, missing: id}`. With no lookup (the glossary has not
   answered) neither is known, and neither is claimed. */
export function wordFor(lookup, termId) {
  if (!termId) return { label: null, missing: null };
  if (!lookup || typeof lookup.term !== 'function') return { label: null, missing: null };
  const rec = lookup.term(termId);
  if (isMissing(rec) || !str(rec.term)) return { label: null, missing: termId };
  return { label: rec.term, missing: null };
}

/* Where the reader is, as the style surface reads it. The `kit` surface is the kit section of a
   style's dossier under its older address (`#/kit/<style>/<slot>`), which PRD §E.1 retires to
   `#/style/<style>/kit/<slot>`; until that retirement lands, and for any link still written the
   old way, it is read as the place it names so the rail, the crumbs and the head agree with the
   URL the reader will be sent to. */
export function normalizePlace(place) {
  const p = isObj(place) ? place : {};
  const surface = str(p.surface) || 'overview';
  const selection = isObj(p.selection) ? p.selection : {};
  if (surface !== 'kit') return { surface, selection };
  const sel = {};
  if (str(selection.style)) sel.style = selection.style;
  if (str(selection.slot)) sel.slot = selection.slot;
  if (sel.style || sel.slot) sel.section = 'kit';
  return { surface: 'style', selection: sel };
}

/* The section a style place is on: a DOSSIER_SECTIONS id, `identify` where none is named or the
   one named is not a section. */
export function sectionOf(selection) {
  const s = isObj(selection) ? str(selection.section) : null;
  return s && DOSSIER_SECTIONS.includes(s) ? s : 'identify';
}

/* What kind of style place this is: the index, the one-slot panel, or a dossier. §E.2's order —
   a style present is a dossier; no style, section kit and a slot is the slot panel; anything
   else is the Styles index. */
export function stylePlaceKind(selection) {
  const sel = isObj(selection) ? selection : {};
  if (str(sel.style)) return 'dossier';
  if (str(sel.section) === 'kit' && str(sel.slot)) return 'slot';
  return 'index';
}

/* The record a page's head reads (§F.2). */
export function headTermFor(place) {
  const { surface, selection } = normalizePlace(place);
  if (surface !== 'style') return `surface-${surface}`;
  const kind = stylePlaceKind(selection);
  if (kind === 'dossier') return `section-${sectionOf(selection)}`;
  if (kind === 'slot') return 'section-kit';
  return 'surface-style';
}

/* The first `style:` citation in the guided-example record's `see[]`, read with the grammar's
   own reader — or null where the record, its list or such a cite is absent. */
export function guidedExampleStyle(lookup) {
  if (!lookup || typeof lookup.term !== 'function') return null;
  const rec = lookup.term('guided-example');
  if (isMissing(rec) || !Array.isArray(rec.see)) return null;
  for (const cite of rec.see) {
    const c = parseCite(typeof cite === 'string' ? cite : '');
    if (c && c.kind === 'style' && !c.fragment) return c.id;
  }
  return null;
}

/* The in-hand item's `{id, name, guided}` (§F.2): the style this browser last read, named, or —
   when prefs holds none — the guided example. `nameOf(id)` answers a style's name or null; an
   unnamed style is shown by its id, never by a name made from it. */
export function inHandFrom(styleInHand, lookup, nameOf) {
  const held = str(styleInHand);
  const id = held || guidedExampleStyle(lookup);
  if (!id) return null;
  const name = typeof nameOf === 'function' ? str(nameOf(id)) : null;
  return { id, name, guided: !held };
}

function sumOf(o) {
  if (!isObj(o)) return null;
  const vals = Object.values(o).filter((v) => num(v) !== null);
  return vals.length ? vals.reduce((a, b) => a + b, 0) : null;
}

/* Each library and index meta, keyed by item id, from what the caller passed. */
const META = Object.freeze({
  style: ({ counts }) => num(isObj(counts) ? counts.styles : null),
  proportions: ({ counts }) => sumOf(isObj(counts) ? counts.proportion_packs : null),
  faults: ({ counts }) => num(isObj(counts) ? counts.faults : null),
  glossary: ({ glossaryCount }) => num(glossaryCount),
});

function stepOf(surface) {
  const i = JOURNEY.findIndex((j) => j.surface === surface);
  return i === -1 ? null : i + 1;
}

function journeyWords(journey, surface) {
  const steps = isObj(journey) && Array.isArray(journey.steps) ? journey.steps : [];
  const s = steps.find((x) => isObj(x) && x.surface === surface);
  return s ? str(s.words) : null;
}

/* The rail, as data (§F.2). */
export function navModel({ lookup, counts, glossaryCount, inHand, dossier, journey, place } = {}) {
  const here = normalizePlace(place);
  const sel = here.selection;
  const onStyle = here.surface === 'style';
  const styleKind = onStyle ? stylePlaceKind(sel) : null;
  const hand = isObj(inHand) && str(inHand.id) ? inHand : null;
  const onHand = Boolean(hand && onStyle && styleKind === 'dossier' && sel.style === hand.id);
  const sections = onHand && isObj(dossier) && dossier.id === hand.id && Array.isArray(dossier.sections)
    ? dossier.sections.filter((s) => isObj(s) && DOSSIER_SECTIONS.includes(s.id)) : null;
  const shownSection = onStyle ? sectionOf(sel) : null;

  const plain = (it) => {
    const { label, missing } = wordFor(lookup, it.termId);
    const meta = META[it.id] ? META[it.id]({ counts, glossaryCount })
      : (stepOf(it.surface) !== null ? journeyWords(journey, it.surface) : null);
    const current = it.id === 'style'
      ? onStyle && styleKind !== 'dossier'
      : here.surface === it.surface;
    return {
      id: it.id,
      surface: it.surface,
      href: formatHash(it.surface, {}, {}),
      termId: it.termId,
      label,
      missing,
      step: stepOf(it.surface),
      meta,
      current,
      note: null,
      children: (it.children || []).map(plain),
    };
  };

  const handItem = () => {
    const guidedWord = hand.guided ? wordFor(lookup, 'guided-example') : null;
    const name = str(hand.name) || hand.id;
    const label = guidedWord && guidedWord.label ? name + SEP + guidedWord.label : name;
    const children = (sections || []).map((s) => {
      const { label: sl, missing: sm } = wordFor(lookup, `section-${s.id}`);
      return {
        id: `in-hand:${s.id}`,
        surface: 'style',
        href: formatHash('style', s.id === 'identify' ? { style: hand.id } : { style: hand.id, section: s.id }, {}),
        termId: `section-${s.id}`,
        label: sl,
        missing: sm,
        step: null,
        meta: s.id === 'identify' ? null : num(s.count),
        current: onHand && shownSection === s.id,
        note: null,
        children: [],
      };
    });
    return {
      id: 'in-hand',
      surface: 'style',
      href: formatHash('style', { style: hand.id }, {}),
      termId: hand.guided ? 'guided-example' : null,
      label,
      missing: guidedWord && !guidedWord.label ? guidedWord.missing : null,
      step: null,
      meta: null,
      // the in-hand item itself only where no listed section is the one shown
      current: onHand && !children.some((c) => c.current),
      // names first, the id as a margin note — only where there is a name to put first
      note: str(hand.name) ? hand.id : null,
      children,
    };
  };

  const groups = NAV.map((g) => {
    const { label, missing } = wordFor(lookup, g.termId);
    const items = [];
    for (const it of g.items) {
      if (it.id === 'in-hand') { if (hand) items.push(handItem()); continue; }
      items.push(plain(it));
    }
    return { id: g.id, termId: g.termId, label, missing, items };
  });
  return { groups };
}

/* Every item of a model, children included, in rail order. */
export function flatItems(model) {
  const out = [];
  const walk = (items) => items.forEach((it) => { out.push(it); walk(it.children || []); });
  (isObj(model) && Array.isArray(model.groups) ? model.groups : []).forEach((g) => walk(g.items || []));
  return out;
}
