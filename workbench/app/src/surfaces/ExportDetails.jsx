/* Surface ⑧b — Details & Export. What works today works plainly: the plan record,
   the brief, the check report and every generated SVG leave as files. What is not
   built is present, disabled, and named with its work package — forthcoming, never
   hidden. The interface must not imply a completeness the corpus does not have. */
import React from 'react';
import { api } from '../api/client.js';
import { planDoc } from '../state/planDoc.js';
import { session } from '../state/session.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterStrip, Chip } from '../Chrome.jsx';

function save(name, content, type = 'application/json') {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob(
    [typeof content === 'string' ? content : JSON.stringify(content, null, 1)], { type }));
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

const card = { border: '1px solid var(--rule)', padding: '14px 16px', flex: '1 1 300px',
  minWidth: 280, maxWidth: 420 };
const cardTitle = { font: 'var(--fw-reg) 17px/1.2 var(--display)', color: 'var(--ink)', margin: '0 0 7px' };
const cardBody = { font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)', margin: '0 0 12px' };

export function ExportDetails({ lastEval }) {
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);
  const s = React.useSyncExternalStore(session.subscribe, session.get);
  const [busySvg, setBusySvg] = React.useState(null);

  async function saveSvg(kind) {
    if (!plan) return;
    setBusySvg(kind);
    try {
      const r = await fetch(`/api/drawings/${kind}`, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ plan }),
      });
      const j = await r.json();
      if (r.ok) save(`${plan.id}-${kind}.svg`, j.svg, 'image/svg+xml');
    } finally {
      setBusySvg(null);
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip>
        <Eyebrow as="span">details &amp; export</Eyebrow>
        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
          generated from data, so it cannot drift — and honest about what is not built
        </span>
      </FilterStrip>

      <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '22px 26px 36px' }}>
        <Eyebrow style={{ marginBottom: 12 }}>leaves the system today</Eyebrow>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'stretch' }}>
          <div style={card}>
            <h3 style={cardTitle}>The plan record</h3>
            <p style={cardBody}>
              The IR itself — the record every drawing and finding renders from. Clear
              dimensions, declared walls, doors, assertions. JSON against
              <span style={{ fontFamily: 'var(--mono)' }}> schema/plan.schema.json</span>.
            </p>
            <Chip onClick={plan ? () => save(`${plan.id}.json`, plan) : undefined}
              title={plan ? '' : 'no plan on the bench'}>
              {plan ? `download ${plan.id}.json` : 'no plan on the bench'}
            </Chip>
          </div>
          <div style={card}>
            <h3 style={cardTitle}>The brief &amp; the check report</h3>
            <p style={cardBody}>
              The brief as typed, and the validator's latest full report — counts, findings,
              constraint summary and the could-not-judge list, none of it collapsed.
            </p>
            <span style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <Chip onClick={s.brief ? () => save(`${s.brief.id || 'brief'}.json`, s.brief) : undefined}>
                {s.brief ? 'download brief' : 'no brief drafted'}
              </Chip>
              <Chip onClick={lastEval?.check ? () => save(`${plan?.id || 'plan'}-check.json`, lastEval) : undefined}>
                {lastEval?.check ? 'download check report' : 'no evaluation yet'}
              </Chip>
            </span>
          </div>
          <div style={card}>
            <h3 style={cardTitle}>The drawing set, as SVG</h3>
            <p style={cardBody}>
              Every sheet the generators produce, in the Drawn Language. The drawing is a
              render of the record; export re-renders, it never snapshots the screen.
            </p>
            <span style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {['plan', 'elevation', 'section', 'bearing', 'roof'].map((k) => (
                <Chip key={k} on={busySvg === k} onClick={plan ? () => saveSvg(k) : undefined}>
                  {busySvg === k ? 'generating…' : k}
                </Chip>
              ))}
            </span>
          </div>
        </div>

        <Eyebrow style={{ margin: '28px 0 12px' }}>forthcoming — designed, not built, and saying so</Eyebrow>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'stretch' }}>
          {[
            { t: 'DXF · IFC', wp: 'WP-5.1', body:
              'Layered DXF of plan, elevation, section and roof; an IFC model with walls, slabs, ' +
              'openings and spaces carrying TDL ids as property sets. Round-trip acceptance: ' +
              'DXF → plan record → validator gives the same findings.' },
            { t: 'Design guidelines, per style', wp: 'WP-5.3', body:
              'A generated book per style: constraints, forbidden variants, faults with their ' +
              'exceptions, pack bindings, rendered orders and details. HTML and PDF, from data, ' +
              'so it cannot drift.' },
            { t: 'The details library', wp: 'WP-5.3', body:
              'Every measured detail rendered by the engine, and all 236 recorded pack conflicts ' +
              'with their ranked honest and dishonest substitutions — the knowledge that lives ' +
              'in senior architects’ heads, written down as executable rules.' },
            { t: 'Drawing-to-record ingestion', wp: 'WP-5.5', body:
              'A structured transcription form that produces a plan record from a drawing by ' +
              'tracing, and a DXF importer for a drafter’s plan. Fourteen reference plans ' +
              'were transcribed by hand; this is the path to volume.' },
          ].map((c) => (
            <div key={c.t} style={{ ...card, backgroundImage: 'var(--hatch-45)' }}>
              <div style={{ background: 'var(--paper)', padding: '8px 10px' }}>
                <h3 style={{ ...cardTitle, color: 'var(--ink-2)' }}>{c.t}</h3>
                <p style={{ ...cardBody, color: 'var(--ink-3)', marginBottom: 8 }}>{c.body}</p>
                <span style={{ font: 'var(--type-data-s)', color: 'var(--forthcoming)' }}>
                  forthcoming — {c.wp} is not built
                </span>
              </div>
            </div>
          ))}
        </div>

        <p style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-3)',
          margin: '24px 0 0', maxWidth: '76ch' }}>
          No costing engine exists: 32 faults carry a recorded <span style={{ fontFamily: 'var(--mono)' }}>cost_saved</span>
          {' '}and nothing here prices a plan. Code findings are advisory IRC model text and are
          never rendered as compliance.
        </p>
      </div>
    </div>
  );
}
