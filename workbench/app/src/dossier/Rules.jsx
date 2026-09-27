/* Constraints — the style's assembly rules, each in its state (WP-14.12, PRD §D.1 row 6, §I.9).

   The constraints column of `surfaces/StyleRecord.jsx`, extracted. It sorted a constraint by
   `c.test` and `c.scope` inline and printed "executable" or "no test yet" in words of its own; the
   state is `judgment.constraintStateOf` now, the one reading, and its name is that state's
   glossary record. A judgment row keeps its mark -- the corpus declining to invent an answer is
   offered back to the reader, not hidden -- and since WP-14.29 that mark is yours-to-judge's
   gilt square and no longer the could-not-evaluate hatch; the footnote counting "295 of 660"
   corpus-wide is gone: a figure typed into a page is true the day it is typed.

   `?constraint=` selects one: it is marked, scrolled to, and its own id is a link to exactly this
   place, so a constraint citation opens on the row it names. */
import React from 'react';
import { Term } from '../components/Term.jsx';
import { JudgmentMark } from '../components/JudgmentMark.jsx';
import { formatHash } from '../router.js';
import { constraintStateOf, CONSTRAINT_STATES } from '../judgment.js';
import { Section, prose, data } from './parts.jsx';

export function Rules({ rec, styleId, selected }) {
  const constraints = rec.constraints || [];
  const tally = CONSTRAINT_STATES.map((s) => [s, constraints.filter((c) => constraintStateOf(c) === s).length])
    .filter(([, n]) => n > 0);
  const refs = React.useRef({});
  React.useEffect(() => {
    const el = selected && refs.current[selected];
    if (el && el.scrollIntoView) el.scrollIntoView({ block: 'center' });
  }, [selected, constraints.length]);

  return (
    <div data-dossier-section="rules" style={{ maxWidth: 760 }}>
      <Section eyebrow={<>{tally.map(([s, n], i) => (
        <React.Fragment key={s}>{i > 0 && ' · '}<Term id={s} /> {n}</React.Fragment>
      ))}</>}>
        {constraints.map((c) => {
          const state = constraintStateOf(c);
          const on = selected === c.id;
          return (
            <div key={c.id} ref={(el) => { refs.current[c.id] = el; }}
              data-constraint={c.id} data-constraint-state={state} data-selected={on ? '' : undefined}
              style={{ marginBottom: 12, padding: on ? '8px 10px' : '0 0 10px',
                borderBottom: '1px solid var(--rule-soft)',
                background: on ? 'var(--paper-deep)' : 'transparent',
                borderLeft: on ? '2px solid var(--gilt-deep)' : '2px solid transparent' }}>
              {state === 'judgment-yours-to-judge'
                ? <JudgmentMark state="yours-to-judge" label={c.statement} showWord={false} />
                : <p style={{ ...prose, marginBottom: 4 }}>{c.statement}</p>}
              <span style={data}>
                <a href={formatHash('style', { style: styleId, section: 'rules', constraint: c.id }, {})}
                  style={{ color: 'var(--ink-2)' }}>{c.id}</a>
                {' '}· {c.kind} · {c.severity} · {c.scope} ·{' '}
                <span style={{ border: '1px solid var(--rule)', padding: '0 5px', color: 'var(--ink-2)' }}>
                  <Term id={state} />
                </span>
              </span>
            </div>
          );
        })}
      </Section>
    </div>
  );
}
