/* WHAT BRIEF INTAKE OFFERS, DECIDED WITHOUT REACT (WP-14.10, PRD §E and §G.1).

   Three facts the form used to hold as literals, each of which had gone wrong:

     THE BUDGET TIERS  were written into the JSX as `entry`, `move-up`, `custom`, `estate`, while
                       `schema/brief.schema.json` admits `value`, `mid`, `custom`, `unlimited`. So
                       three of the four a reader could choose were off the schema's own list, and
                       choosing one refused the WHOLE brief at compose with a validation error
                       about a field the reader had been offered by the app. Step one of the house
                       journey broke on a word the app had supplied. The tiers are read from the
                       schema the server serves (`GET /api/schema/brief`) and from nowhere else.
     THE STYLE         defaulted to `tidewater-georgian`, so a reader arriving with no style in
                       hand was given one. PRD §F.4: the URL decides what is read, and memory only
                       offers. A style reaches the brief from `?style=`, from the picker, or from
                       the reader's own saved draft -- never from a constant in this file.
     THE EXAMPLE       had no way in. `?example=<name>` names a shipped brief in `briefs/`, which
                       the server serves by name and never by path (`/api/briefs/examples/<name>`).

   AND A FOURTH, WHICH WAS NOT A LITERAL BUT A FIELD THE FORM COULD NOT CARRY (WP-14.25).

     THE PARTI         `schema/brief.schema.json` 0.2.0 admits a `parti`, and the composer
                       guarantees the named diagram a place among the candidates (ruled 25 Sep
                       2026, built server-side by WP-14.19). The form had no field for it, so a
                       plan type read on a style's dossier could not start the brief it belongs to.
                       It arrives from `?parti=`, from the form's own select, or from the reader's
                       draft, and is empty by default: an unnamed parti is the composer choosing
                       every diagram itself, which is what the schema says an unset one means.
                       `composeRequest` is the brief the form POSTS, and it keeps `parti` -- a
                       test drops it by mutation and goes red, because a posted brief that lost the
                       diagram the reader named would compose without the guarantee and say
                       nothing.

   Pure: no React, no DOM. It imports the journey, for the one test it shares, and the candidate
   set's nativity map, so the form and the candidates word a parti's nativity from one table. */
import { journeyState } from './journey.js';
import { NATIVITY_TERMS } from '../candidateOrder.js';

/* The form's starting values. `style` and `parti` are empty on purpose -- see above -- and
   everything else is what the form has always offered. */
export const BRIEF_DEFAULTS = Object.freeze({
  id: 'new-brief', name: '', style: '', parti: '',
  target_area_sf: 3200, bedrooms: 4, bathrooms: 3.5,
  must_have: Object.freeze([]), context: Object.freeze({}), household: '', candidates: 4,
});

const isObj = (v) => Boolean(v) && typeof v === 'object' && !Array.isArray(v);

const blank = (v) => v === '' || v === null
  || (Array.isArray(v) && !v.length)
  || (isObj(v) && !Object.keys(v).length);

/* The brief the form POSTS, and the candidate count that travels beside it (WP-14.25, lifted out
   of `BriefIntake.jsx` so it can be tested). Every field the reader left blank is dropped -- an
   empty string, a null, an empty list, an empty object -- because the schema reads an ABSENT field
   as a decision for the composer and would refuse an empty string outright (`parti`'s own pattern
   admits no empty id). `candidates` goes as its own argument, and is dropped from the brief when
   it is not a count of one or more: `min="1"` on a number input is decorative outside a form, an
   emptied field reads back as 0, and the schema's `minimum: 1` would refuse the WHOLE brief over a
   field the reader was not thinking about. `candidates` comes back null where there is no count,
   so the client's own default applies and this file writes none. */
export function composeRequest(brief) {
  // the root is never dropped, however empty: an empty brief is refused by the server, by name
  const clean = JSON.parse(JSON.stringify(isObj(brief) ? brief : {},
    (k, v) => (k !== '' && blank(v) ? undefined : v)));
  const wanted = Number(isObj(brief) ? brief.candidates : NaN);
  const count = Number.isFinite(wanted) && wanted >= 1 ? wanted : null;
  if (count === null) delete clean.candidates;
  return { brief: clean, candidates: count };
}

/* WHAT THE PARTI SELECT OFFERS, GROUPED BY THE NATIVITY THE SERVER STATED (WP-14.25).

   `own` is `/api/partis?style=` -- the style's native and lineage partis, each carrying the
   `nativity` `compose.nativity` gave it. `borrowed` is the same route asked `include_borrowed`,
   and is read only where the reader has chosen to include borrowed diagrams: from it only the rows
   the server calls `borrowed` are taken, so a native row is never offered twice or under the wrong
   word. Nothing here decides a nativity. Until this package the form took the whole list as
   "native", which was right while the list held native partis alone and wrong from the day it
   listed lineage ones beside them.

   Returns the groups in the composer's own order (native, lineage, borrowed), each with the
   glossary record its word comes from, the rows each group holds, and `offList`: the parti the
   brief already names where no group holds it -- a draft or an address naming a borrowed diagram
   the reader has not asked to see, or an id nobody holds. It is SHOWN as what it is rather than
   dropped, as an off-schema budget tier is: dropping it would change the reader's brief without a
   word, and the server refuses an id it does not hold, by name, before any job starts. */
export function partiOptions(own, borrowed, current) {
  const rowsOf = (payload) => (isObj(payload) && Array.isArray(payload.partis) ? payload.partis : [])
    .filter((p) => isObj(p) && typeof p.id === 'string' && p.id);
  const all = [...rowsOf(own), ...rowsOf(borrowed).filter((p) => p.nativity === 'borrowed')];
  const seen = new Set();
  const groups = Object.keys(NATIVITY_TERMS).map((nativity) => ({
    nativity,
    termId: NATIVITY_TERMS[nativity],
    rows: all.filter((p) => p.nativity === nativity && !seen.has(p.id) && seen.add(p.id))
      .map((p) => ({ id: p.id, name: typeof p.name === 'string' && p.name ? p.name : p.id })),
  })).filter((g) => g.rows.length);
  const cur = typeof current === 'string' && current ? current : null;
  const offList = cur && !seen.has(cur) ? cur : null;
  return { groups, offList };
}

/* The served nativity of the parti the brief names, or null where no row the form holds says. */
export function nativityOfParti(options, id) {
  const g = (options && Array.isArray(options.groups) ? options.groups : [])
    .find((x) => x.rows.some((r) => r.id === id));
  return g ? g.nativity : null;
}

/* A brief the form can hold, from a saved draft or a loaded example laid over the defaults.
   A record persisted by an older shape must never crash the form, so the context is always an
   object and `must_have` always a list. */
export function briefFrom(rec, defaults = BRIEF_DEFAULTS) {
  const r = isObj(rec) ? rec : {};
  return {
    ...defaults,
    ...r,
    must_have: Array.isArray(r.must_have) ? r.must_have.slice() : [],
    context: { ...(isObj(r.context) ? r.context : {}) },
  };
}

/* The budget tiers the brief schema admits, in the schema's own order, from the payload
   `GET /api/schema/brief` answers -- or null where the payload carries no such enum, which the
   form says rather than falling back to a list of its own. */
export function budgetTiers(payload) {
  const schema = isObj(payload) && isObj(payload.schema) ? payload.schema : null;
  const bt = schema && isObj(schema.properties) && isObj(schema.properties.context)
    && isObj(schema.properties.context.properties)
    ? schema.properties.context.properties.budget_tier : null;
  const e = isObj(bt) && Array.isArray(bt.enum) ? bt.enum : null;
  return e && e.length && e.every((x) => typeof x === 'string') ? e.slice() : null;
}

/* A tier the brief already carries that the schema does not admit -- an older draft's `entry`,
   say. It is shown as what it is rather than silently dropped or silently kept: dropping it
   would change the reader's brief without a word, and keeping it unmarked is how a brief came
   to be refused for a word the app itself had offered. Null where there is nothing to say,
   including while the tiers are still unknown. */
export function offSchemaTier(tiers, current) {
  if (!Array.isArray(tiers) || typeof current !== 'string' || !current) return null;
  return tiers.includes(current) ? null : current;
}

/* A shipped example's name as `?example=` carries it: the schema payload lists files with
   their `.json`, and the route takes either. */
export function exampleId(file) {
  if (typeof file !== 'string') return null;
  const base = file.split('/').pop();
  const id = base.endsWith('.json') ? base.slice(0, -5) : base;
  return id || null;
}

/* Whether the brief states the two fields the schema requires, asked of the journey rather than
   spelled again here: the brief step's `stated` is that test (`journey.js`, PRD §G), so the
   form's Compose and the bar's step cannot disagree about whether a brief is ready. */
export function briefReady(brief) {
  const step = journeyState({ session: { brief } }).steps.find((s) => s.id === 'brief');
  return !!step && step.state === 'stated';
}
