/* P5 + P8. The prose-capable card. What it must never lose:
   1. THE ANSWER BEFORE THE PROOF (WP-14.11). The right way (`correct_practice`) and how to spot
      it (`detection`) come first. Every fault record carries both and the card rendered neither,
      so a practitioner who opened a named error learned what was wrong and never how to do it
      right. The order is `faults/licence.js`'s `FAULT_CARD_ORDER`, one list the walk reads too.
   2. A style's licence shows the SERVER's verdict on whether that style earns it
      (`for_this_style.exception.granted`: granted, refused or unjudged — never collapsed), above
      the general rule. It used to print the licence's own `why` whenever a style was in view,
      which read as earned for a licence the style is refused and for one nobody could judge. The
      verdict word is the glossary record's (`exception-granted`, `exception-refused`,
      `judgment-unjudged`), through `Term`.
   3. Two severity axes — how it reads, how it lives — are two axes, not one badge. How it lives
      is the record's `severity_in_use`, drawn where the record states it; until WP-14.17 that
      label sat over `frequency`, which is how OFTEN, and is labelled so now.
   4. All three fix tiers appear, named right / cheap / dishonest, because the cheap one
      is what actually gets built and naming the dishonest one is how the corpus stays honest.
   5. THE CARD WRITES NO WORD ABOUT ITS OWN PARTS (WP-14.17). Every heading, tier word and axis
      label is a glossary record, drawn through `Term` from `faults/licence.js`'s tables, which
      `src/faultCard.test.mjs` holds to `glossary/`. What the card still prints unworded is the
      fault's own content and the record's machine values (a category, a driver, a slot id). */
import React from 'react';
import { Term } from './Term.jsx';
import { RecordLink } from './RecordLink.jsx';
import { useGlossary } from '../api/useGlossary.js';
import { isMissing } from '../glossary/lookup.js';
import {
  licenceOf, faultSections, inUseOf,
  FAULT_SECTION_TERM, COST_SAVED_TERM, FIX_TIERS, FIX_TIER_TERM, FAULT_AXIS_TERM,
} from '../faults/licence.js';

const SEV = {
  fatal: 'var(--sev-fatal)',
  serious: 'var(--sev-serious)',
  minor: 'var(--sev-minor)',
};
const FIX = {
  right: 'var(--fix-right)',
  cheap: 'var(--fix-cheap)',
  dishonest: 'var(--fix-dishonest)',
};
const EYE = {
  font: 'var(--type-eyebrow)',
  letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase',
  color: 'var(--ink-2)',
};
const META = { font: 'var(--type-data-s)', color: 'var(--ink-2)' };
const PROSE = {
  font: 'var(--type-prose)', color: 'var(--ink)', maxWidth: 'var(--measure-prose)',
  margin: '7px 0 0', textWrap: 'pretty',
};
/* The licence's frame by verdict, in the standard's own tokens: gilt where it is earned, the
   plain rule where it is refused (the general rule stands), and the could-not-evaluate mark where
   nobody could say. That field is `--mark-unjudged`, the one duty the unjudged hatch carries, and
   never the hatch by name (WP-14.29, `src/marks.test.mjs`). */
const LICENCE_FRAME = {
  granted: { borderLeft: '2px solid var(--gilt-deep)', background: 'var(--paper-deep)' },
  refused: { borderLeft: '2px solid var(--ink-2)', background: 'var(--paper)' },
  unjudged: { borderLeft: '2px dashed var(--ink-2)', backgroundImage: 'var(--mark-unjudged)' },
};

/* An axis is labelled by the record for the field it reads (`FAULT_AXIS_TERM`). */
function Axis({ field, value, colour }) {
  return (
    <span style={{ display: 'inline-flex', flexDirection: 'column', gap: 3, minWidth: 92 }}>
      <span style={EYE}><Term id={FAULT_AXIS_TERM[field]} /></span>
      <span style={{ font: 'var(--type-data)', color: colour || 'var(--ink-2)' }}>{value}</span>
    </span>
  );
}

/* A section's heading: the record for its place in FAULT_CARD_ORDER. */
function Head({ section, style }) {
  return <div style={{ ...EYE, ...style }}><Term id={FAULT_SECTION_TERM[section]} /></div>;
}

/* How it lives, in the severity's own words where the value is a severity (`fault.severity`'s
   records name fatal, serious and minor); the schema's fourth value names no severity and is
   printed as the record states it, like the category and the driver, rather than drawn as a
   "no entry" or handed a word from another sense. */
function InUse({ value }) {
  const glossary = useGlossary();
  const unbound = glossary.status === 'ready' && glossary.lookup
    && isMissing(glossary.lookup.termFor('fault.severity', value));
  return unbound ? value : <Term field="fault.severity" value={value} />;
}

/* The verdict word, by literal id, so `glossary.test.mjs` holds each to a record. */
function LicenceVerdict({ state }) {
  if (state === 'granted') return <Term id="exception-granted" />;
  if (state === 'refused') return <Term id="exception-refused" />;
  return <Term id="judgment-unjudged" />;
}

function Licence({ licence }) {
  const frame = LICENCE_FRAME[licence.state] || LICENCE_FRAME.unjudged;
  return (
    <section data-fault-section="licence" data-licence={licence.state}
      style={{ margin: '16px 0 0', padding: '12px 14px', border: '1px solid var(--rule)', ...frame }}>
      <div style={{ display: 'flex', gap: 10, alignItems: 'baseline', flexWrap: 'wrap',
        background: licence.state === 'unjudged' ? 'var(--paper)' : 'transparent',
        padding: licence.state === 'unjudged' ? '2px 6px' : 0, width: 'fit-content' }}>
        <span style={{ ...EYE, color: 'var(--gilt-deep)' }}><Term id={FAULT_SECTION_TERM.licence} /></span>
        <RecordLink cite={'style:' + licence.style} />
        <span data-licence-verdict={licence.state}
          style={{ font: 'var(--type-data)', color: 'var(--ink)', border: '1px solid currentColor',
            padding: '0 6px' }}>
          <LicenceVerdict state={licence.state} />
        </span>
      </div>
      <div style={{ background: licence.state === 'unjudged' ? 'var(--paper)' : 'transparent',
        padding: licence.state === 'unjudged' ? '4px 6px' : 0, marginTop: 4 }}>
        {licence.because && (
          <p data-licence-because="" style={{ ...META, color: 'var(--ink-2)', margin: '3px 0 0' }}>
            {licence.because}
          </p>
        )}
        {licence.statement && (
          <p style={{ font: 'var(--fw-reg) 13.5px/1.55 var(--body)',
            color: licence.state === 'granted' ? 'var(--ink)' : 'var(--ink-2)', margin: '7px 0 0' }}>
            {licence.statement}
          </p>
        )}
        {licence.bounds && <div style={{ ...META, color: 'var(--ink-2)', marginTop: 7 }}>{licence.bounds}</div>}
      </div>
    </section>
  );
}

function FaultCard({ fault, styleInView, onSlot, style }) {
  const licence = licenceOf(fault, styleInView);
  const inUse = inUseOf(fault);
  const sections = {
    correct_practice: () => (
      <section key="correct_practice" data-fault-section="correct_practice" style={{ marginTop: 16 }}>
        <Head section="correct_practice" style={{ color: 'var(--fix-right)' }} />
        <p style={PROSE}>{fault.correct_practice}</p>
      </section>
    ),
    detection: () => (
      <section key="detection" data-fault-section="detection" style={{ marginTop: 16 }}>
        <Head section="detection" />
        <p style={{ ...PROSE, color: 'var(--ink-2)' }}>{fault.detection}</p>
      </section>
    ),
    licence: () => <Licence key="licence" licence={licence} />,
    symptom: () => (
      <section key="symptom" data-fault-section="symptom"
        style={{ marginTop: 18, borderTop: '1px solid var(--rule-soft)', paddingTop: 14 }}>
        <Head section="symptom" />
        <p style={PROSE}>{fault.symptom}</p>
      </section>
    ),
    cause: () => (
      <section key="cause" data-fault-section="cause" style={{ marginTop: 16 }}>
        <div style={EYE}>
          <Term id={FAULT_SECTION_TERM.cause} /> — <Term id={FAULT_AXIS_TERM['cause.driver']} />: {fault.cause.driver}
        </div>
        <p style={{ font: 'var(--fw-reg) 13.5px/1.6 var(--body)', color: 'var(--ink-2)',
          maxWidth: 'var(--measure-prose)', margin: '7px 0 0' }}>{fault.cause.explanation}</p>
        {fault.cause.cost_saved && (
          <p style={{ font: 'var(--fw-med) 13.5px/1.55 var(--body)', color: 'var(--gilt-deep)', margin: '9px 0 0' }}>
            <span style={{ ...EYE, marginRight: 8 }}><Term id={COST_SAVED_TERM} /></span>{fault.cause.cost_saved}
          </p>
        )}
      </section>
    ),
    rule_violated: () => (
      <section key="rule_violated" data-fault-section="rule_violated" style={{ marginTop: 16 }}>
        <Head section="rule_violated" />
        {fault.rule_violated.map((r, i) => (
          <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'baseline', marginTop: 7 }}>
            <span style={{ ...META, width: 168, flex: 'none' }}>{r.kind} · {r.ref}</span>
            <span style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)',
              maxWidth: 'var(--measure-note)' }}>{r.statement}</span>
          </div>
        ))}
      </section>
    ),
    fixes: () => (
      <section key="fixes" data-fault-section="fixes"
        style={{ marginTop: 18, borderTop: '1px solid var(--rule-soft)', paddingTop: 14 }}>
        <Head section="fixes" />
        {FIX_TIERS.map((tier) => (fault.fix[tier] ? (
          <div key={tier} data-fix-tier={tier} style={{ display: 'flex', gap: 12, alignItems: 'baseline', marginTop: 9 }}>
            <span style={{ font: 'var(--type-data-s)', color: FIX[tier], border: '1px solid currentColor',
              padding: '1px 6px', width: 78, flex: 'none', textAlign: 'center' }}><Term id={FIX_TIER_TERM[tier]} /></span>
            <span style={{ font: 'var(--fw-reg) 13.5px/1.6 var(--body)', color: 'var(--ink-2)',
              maxWidth: 'var(--measure-prose)' }}>{fault.fix[tier]}</span>
          </div>
        ) : null))}
      </section>
    ),
    test: () => (
      <section key="test" data-fault-section="test" style={{ marginTop: 16 }}>
        <Head section="test" />
        <pre style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', background: 'var(--paper-mat)',
          border: '1px solid var(--rule-soft)', padding: '8px 10px', marginTop: 7,
          whiteSpace: 'pre-wrap' }}>{fault.test}</pre>
      </section>
    ),
  };
  return (
    <article data-fault={fault.id} style={{ border: '1px solid var(--rule)',
      borderLeft: '2px solid ' + (SEV[fault.severity] || 'var(--ink-3)'),
      background: 'var(--paper)', padding: '18px 20px 20px', ...style }}>
      <header>
        <h3 style={{ font: 'var(--fw-reg) var(--fs-d3)/1.15 var(--display)', fontVariationSettings: '"opsz" 40',
          letterSpacing: 'var(--tr-display)', color: 'var(--ink)', margin: 0 }}>{fault.name}</h3>
        {fault.aka && fault.aka.length > 0 && (
          <div style={{ font: 'var(--fw-reg) italic 13px/1.5 var(--body)', color: 'var(--gilt-deep)',
            fontStyle: 'italic', marginTop: 4 }}>
            {fault.aka.map((a) => '“' + a + '”').join(', ')}
          </div>
        )}
        <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', margin: '14px 0 0', paddingBottom: 14,
          borderBottom: '1px solid var(--rule-soft)' }}>
          <Axis field="severity" colour={SEV[fault.severity]}
            value={fault.severity ? <Term field="fault.severity" value={fault.severity} /> : null} />
          <Axis field="frequency" value={fault.frequency} />
          {inUse && <Axis field="severity_in_use" colour={SEV[inUse]} value={<InUse value={inUse} />} />}
          <Axis field="category" value={fault.category} />
          <Axis field="cause.driver" value={fault.cause && fault.cause.driver} />
          {fault.slots && (
            <span style={{ display: 'inline-flex', flexDirection: 'column', gap: 3 }}>
              <span style={EYE}><Term id={FAULT_AXIS_TERM.slots} /></span>
              <span style={{ display: 'flex', gap: 8 }}>
                {fault.slots.map((s) => (onSlot ? (
                  <button key={s} type="button" onClick={() => onSlot(s)} className="tdl-link"
                    style={{ font: 'var(--type-data)' }}>{s}</button>
                ) : (
                  <span key={s} style={{ font: 'var(--type-data)', color: 'var(--ink-2)' }}>{s}</span>
                )))}
              </span>
            </span>
          )}
        </div>
      </header>
      {faultSections(fault, styleInView).map((k) => sections[k]())}
    </article>
  );
}

export default FaultCard;
export { FaultCard };
