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

/* EVERY WORD THE CARD PRINTS ABOUT ITS OWN PARTS IS A GLOSSARY RECORD (WP-14.17, tranche 2's PRD
   §A.3). The card typed its headings ("the right way", "how to spot it", "rule violated"…), its
   tier words and its axis labels, and two of them explained themselves in words nothing checked
   ("fix — three tiers, named plainly", "test — beside the statement, never instead of it"). Each
   is a record now, named here BY ID, one table the card draws through `Term` and
   `src/faultCard.test.mjs` holds to `glossary/` both ways. The ids are data rather than literals
   in the card because the card draws its sections in `FAULT_CARD_ORDER`, so the table is keyed by
   that order's own words. */
export const FAULT_SECTION_TERM = Object.freeze({
  correct_practice: 'fault-section-correct-practice',
  detection: 'fault-section-detection',
  licence: 'exception',                     // the licence's heading was already a record
  symptom: 'fault-section-symptom',
  cause: 'fault-section-cause',
  rule_violated: 'fault-section-rule-violated',
  fixes: 'fault-section-fix',
  test: 'fault-section-test',
});

/* The cause's own line, under the cause heading. */
export const COST_SAVED_TERM = 'fault-section-cost-saved';

/* The fix tiers in the order the card reads them, which is `schema/fault.schema.json`'s own
   `fixes` order (the test holds the two to each other), and the record naming each. */
export const FIX_TIERS = Object.freeze(['right', 'cheap', 'dishonest']);
export const FIX_TIER_TERM = Object.freeze({
  right: 'fix-tier-right', cheap: 'fix-tier-cheap', dishonest: 'fix-tier-dishonest',
});

/* The card's header axes, keyed by the field of the fault record each one reads (`cause.driver`
   is the cause's own field), in the order the header draws them.

   THE SECOND SEVERITY AXIS WAS DRAWN OVER THE WRONG FIELD. The card's own opening note says "two
   severity axes — how it reads, how it lives — are two axes, not one badge", and `how it lives`
   is the schema's `severity_in_use`: *"A stack with nowhere to land is invisible in a photograph
   and fatal in occupation."* The label sat over `frequency` (endemic … rare), which is a
   different question — how OFTEN a fault occurs. Naming each label's record made the mismatch
   visible: `frequency` takes its own word now (`how often`), and `how it lives` is drawn over
   `severity_in_use` wherever a fault states one. */
export const FAULT_AXES = Object.freeze([
  'severity', 'frequency', 'severity_in_use', 'category', 'cause.driver', 'slots',
]);
export const FAULT_AXIS_TERM = Object.freeze({
  severity: 'fault-axis-how-it-reads',
  frequency: 'fault-axis-frequency',
  severity_in_use: 'fault-axis-how-it-lives',
  category: 'fault-axis-category',
  'cause.driver': 'fault-axis-driver',
  slots: 'fault-axis-filed-against',
});

/* The in-use severity where the record states one, or null: a fault that says nothing about how
   it lives is not drawn as though it had said "minor". */
export function inUseOf(fault) {
  const f = obj(fault);
  const v = f ? f.severity_in_use : null;
  return typeof v === 'string' && v ? v : null;
}

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
