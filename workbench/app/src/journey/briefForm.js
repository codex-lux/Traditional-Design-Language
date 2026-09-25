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

   Pure: no React, no DOM; its one import is the journey, for the one test it shares. */
import { journeyState } from './journey.js';

/* The form's starting values. `style` is empty on purpose -- see above -- and everything else
   is what the form has always offered. */
export const BRIEF_DEFAULTS = Object.freeze({
  id: 'new-brief', name: '', style: '',
  target_area_sf: 3200, bedrooms: 4, bathrooms: 3.5,
  must_have: Object.freeze([]), context: Object.freeze({}), household: '', candidates: 4,
});

const isObj = (v) => Boolean(v) && typeof v === 'object' && !Array.isArray(v);

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
