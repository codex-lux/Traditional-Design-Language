/* WHAT A FAULT CARD ANSWERS, AND IN WHAT ORDER (WP-14.11).

   Two decisions `components/FaultCard.jsx` makes, lifted out so they can be driven under
   `node --test` (the card imports React and cannot be):

   THE ORDER. A practitioner opens a named error to learn how to do the thing right and how to see
   it in a building. Every one of the 210 fault records carries `correct_practice` (the right way in
   full) and `detection` (how to spot it), and the card rendered NEITHER — a grep of the app for
   either field returned nothing (`docs/reports/ux-first-principles-2026-09-24.md`, finding 11:
   proof before answer). They come first now; then this style's licence, then the symptom, the
   cause, the rule, the fixes, and the machine test last — the answer before the proof, and the
   proof kept.

   THE LICENCE. A style's exception is a licence to do what is a fault everywhere else, and whether
   THIS style earns it is the server's verdict, not the record's say-so: `core.get_fault(id, style)`
   returns `for_this_style.exception.granted` as `granted`, `refused` or `unjudged`
   (`core.grant_exception`, WP-8.4), with its reason. The card printed the licence's own `why`
   under an "exception for" heading whenever a style was in view, so a licence the style is REFUSED
   (Pueblo Revival's adobe licence on a stuccoed frame) and one nobody could judge both read as
   earned. `licenceOf` reads the verdict and NEVER collapses it: only the served words `granted` and
   `refused` are those verdicts; a missing card, a card about another style (the fetch for the
   previous style still in hand), or any other value is `unjudged` — never granted, because an
   unjudged licence shown as earned is the fake pass in its sharpest form. Each state names its
   glossary record; the card draws the record's word through `Term`.

   Pure; imports nothing. */

export const LICENCE_STATES = Object.freeze(['granted', 'refused', 'unjudged']);

/* The glossary record naming each verdict (PRD §B: `core.grant_exception`'s three verdicts map to
   `exception-granted`, `exception-refused` and `judgment-unjudged`). */
export const LICENCE_TERM = Object.freeze({
  granted: 'exception-granted',
  refused: 'exception-refused',
  unjudged: 'judgment-unjudged',
});

/* The card's sections, in reading order. `licence` renders only where a style in view holds one. */
export const FAULT_CARD_ORDER = Object.freeze([
  'correct_practice', 'detection', 'licence', 'symptom', 'cause', 'rule_violated', 'fixes', 'test',
]);

const obj = (x) => (x && typeof x === 'object' && !Array.isArray(x) ? x : null);

/* fault → the licence this style holds against it, with the server's verdict, or null where no
   style is in view or the style holds none.

   `fault` is the served record (`GET /api/faults/{id}?style=`), whose `exceptions` array is the
   corpus's (every licence, unconditionally — `_exception_card`'s docstring says why it is left so)
   and whose `for_this_style.exception` carries the verdict for the style asked about. */
export function licenceOf(fault, styleInView) {
  const f = obj(fault);
  if (!f || typeof styleInView !== 'string' || !styleInView) return null;
  const record = (Array.isArray(f.exceptions) ? f.exceptions : [])
    .find((e) => obj(e) && e.style === styleInView) || null;
  const fts = obj(f.for_this_style);
  const card = fts ? obj(fts.exception) : null;
  const served = card && card.style === styleInView ? card : null;
  if (!record && !served) return null;
  const state = served && (served.granted === 'granted' || served.granted === 'refused')
    ? served.granted : 'unjudged';
  const rec = record || served;
  return {
    state,
    termId: LICENCE_TERM[state],
    style: styleInView,
    statement: typeof rec.statement === 'string' ? rec.statement
      : (typeof rec.why === 'string' ? rec.why : null),
    bounds: typeof rec.bounds === 'string' ? rec.bounds : null,
    because: served && typeof served.granted_because === 'string' && served.granted_because
      ? served.granted_because : null,
    unevaluated: served && Array.isArray(served.precondition_not_evaluated)
      ? served.precondition_not_evaluated.filter((k) => typeof k === 'string' && k) : [],
    served: Boolean(served),
  };
}

/* The sections this fault has, in FAULT_CARD_ORDER: a field the record leaves empty is omitted,
   never drawn as an empty heading. */
export function faultSections(fault, styleInView) {
  const f = obj(fault) || {};
  const text = (v) => typeof v === 'string' && v.trim().length > 0;
  const has = {
    correct_practice: text(f.correct_practice),
    detection: text(f.detection),
    licence: licenceOf(f, styleInView) !== null,
    symptom: text(f.symptom),
    cause: Boolean(obj(f.cause)),
    rule_violated: Array.isArray(f.rule_violated) && f.rule_violated.length > 0,
    fixes: Boolean(obj(f.fix)),
    test: Boolean(f.test),
  };
  return FAULT_CARD_ORDER.filter((k) => has[k]);
}
