/* WHAT THE FRONT DOOR SAYS, AS DATA, AND WHERE EACH WORD OF IT COMES FROM (WP-14.14).

   Phase 14's first finding was that nothing said what this is: the landing's one paragraph was
   `core.overview().what_this_is`, written to an AI agent ("Built to be consulted mid-conversation
   while advising a human on a real house"), and the rest was eleven app-written doors. The front
   door is built from two sources now and no third:

     GLOSSARY RECORDS   `about-tdl` — what this is (its definition), who it is for (its three
                        practitioner readers, VISION's own, the homeowner left out on purpose by
                        the record), and what it is not; `guided-example` — the worked house, its
                        citations, and where it stops; the rank records, which name the inventory.
     LIVE COUNTS        `/api/overview`'s `counts` — never a figure written here.

   Each function below turns one of those into what the page draws, and says what it could not
   read rather than filling the gap: a record the glossary does not hold comes back `missing` with
   its id, so the page prints `noEntry(id)` visibly, and a glossary that has not answered yet is
   `loading`, never an empty success.

   THE WORKED EXAMPLE STOPS WHERE THE CORPUS DOES. The guided example's plan is refused at
   placement (`oq/the-worked-house-has-no-plan-that-places`), so the example runs from the style's
   dossier to the example brief and no further. Where it stops is said in the record's own words —
   `guided-example`'s `more` — and this file hands that sentence through untouched; it writes no
   tour, no promise and no substitute.

   Pure: no React, no DOM, no fetch. `src/frontDoor.test.mjs` drives it on the glossary records
   read from `glossary/*.json`. */
import { isMissing } from '../glossary/lookup.js';
import { parseCite } from '../citations.js';
import { flatItems } from '../nav/navModel.js';

const isObj = (v) => Boolean(v) && typeof v === 'object' && !Array.isArray(v);
const str = (v) => (typeof v === 'string' && v.trim() ? v.trim() : null);
const strs = (v) => (Array.isArray(v) ? v.map(str).filter(Boolean) : []);
const num = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : null);

const LOADING = Object.freeze({ state: 'loading' });

/* `about-tdl`: the term, the one-sentence definition, the readers, what it is not. */
export function aboutView(lookup) {
  if (!lookup || typeof lookup.term !== 'function') return LOADING;
  const rec = lookup.term('about-tdl');
  if (isMissing(rec)) return { state: 'missing', missing: rec.missing };
  const readers = (Array.isArray(rec.readers) ? rec.readers : [])
    .filter((r) => isObj(r) && str(r.who) && str(r.line))
    .map((r) => ({ who: str(r.who), line: str(r.line) }));
  return {
    state: 'ready',
    term: str(rec.term),
    definition: str(rec.definition),
    readers,
    isNot: strs(rec.is_not),
  };
}

/* `guided-example`: its word, its definition, the citations it names (in its order), the first
   style and the first brief among them, and `more` — the sentence that says where it stops, or
   null where the record carries none (nothing is put in its place). */
export function guidedView(lookup) {
  if (!lookup || typeof lookup.term !== 'function') return LOADING;
  const rec = lookup.term('guided-example');
  if (isMissing(rec)) return { state: 'missing', missing: rec.missing };
  const cites = strs(rec.see).filter((c) => parseCite(c));
  const first = (kind) => cites.find((c) => {
    const p = parseCite(c);
    return p.kind === kind && !p.fragment;
  }) || null;
  const briefCite = first('brief');
  return {
    state: 'ready',
    word: str(rec.term),
    definition: str(rec.definition),
    more: str(rec.more),
    cites,
    styleCite: first('style'),
    briefCite,
    briefId: briefCite ? parseCite(briefCite).id : null,
  };
}

/* One row per key of `counts.by_rank`, figure as served, named by the record that binds that rank
   (`style.rank`, read through `by_field`), in the order those records state. A rank the glossary
   has no record for is still a row — the figure is the API's and is not dropped — and is named as
   missing. With no `by_rank` there are no rows, never zeros. */
export function rankRows(counts, lookup) {
  const by = isObj(counts) && isObj(counts.by_rank) ? counts.by_rank : null;
  if (!by) return [];
  const rows = Object.keys(by).filter((k) => num(by[k]) !== null).map((key) => {
    const rec = lookup && typeof lookup.termFor === 'function' ? lookup.termFor('style.rank', key) : null;
    const known = rec && !isMissing(rec);
    return {
      key,
      figure: by[key],
      termId: known ? rec.id : null,
      missing: rec && isMissing(rec) ? rec.missing : null,
      order: known && num(rec.order) !== null ? rec.order : Infinity,
    };
  });
  rows.sort((a, b) => (a.order - b.order) || (a.key < b.key ? -1 : a.key > b.key ? 1 : 0));
  return rows.map(({ order, ...r }) => r);
}

/* The sum of a count object's figures (`counts.proportion_packs` is by kind), or null. */
export function total(o) {
  if (!isObj(o)) return null;
  const vals = Object.values(o).map(num).filter((v) => v !== null);
  return vals.length ? vals.reduce((a, b) => a + b, 0) : null;
}

/* The two entrances are two of the site map's own items — Find a style and the first house step —
   and the style in hand, which is OFFERED as a link beside the first and never applied (§F.4).
   Picked out of the model by item id; nothing about them is restated here. */
export function entranceItems(model) {
  const items = flatItems(model);
  const pick = (id) => items.find((it) => it.id === id) || null;
  return { style: pick('style'), inHand: pick('in-hand'), brief: pick('brief') };
}

/* Where the house on hand stands, if anywhere: the journey's own `resume` (PRD §G), named by the
   site map's item for that step's surface, with the journey's words for it. Null where the journey
   says there is nothing to resume. */
export function resumeView(journey, model) {
  const r = isObj(journey) && isObj(journey.resume) ? journey.resume : null;
  if (!r) return null;
  const step = (Array.isArray(journey.steps) ? journey.steps : []).find((s) => isObj(s) && s.id === r.id);
  if (!step) return null;
  const item = flatItems(model).find((it) => it.surface === step.surface && it.step === r.n) || null;
  return {
    id: r.id,
    n: r.n,
    href: item ? item.href : r.href,
    label: item ? item.label : null,
    missing: item ? item.missing : null,
    termId: item ? item.termId : null,
    words: str(step.words),
    plan: r.id === 'plan',
  };
}
