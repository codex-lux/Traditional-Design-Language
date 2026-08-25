/* Surface ⑨ — the Fault Corpus, live. Element-first: faults hang off slots, not styles.
   The list filters on the corpus's own axes; the reading pane fetches the full record
   (find_faults cards are summaries) and style exceptions render above the general rule. */
import React from 'react';
import { api } from '../api/client.js';
import { FaultCard } from '../components/FaultCard.jsx';
import { UnsourcedImageRecord } from '../components/UnsourcedImageRecord.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterStrip, Chip } from '../Chrome.jsx';

const SEV_C = { fatal: 'var(--sev-fatal)', serious: 'var(--sev-serious)', minor: 'var(--sev-minor)' };

export function FaultCorpus({ onCite, selection }) {
  const [all, setAll] = React.useState([]);
  const [id, setId] = React.useState(selection?.fault || 'porch-too-shallow-to-inhabit');
  const [sev, setSev] = React.useState(null);
  const [driver, setDriver] = React.useState(null);
  const [styleInView, setStyleInView] = React.useState('');
  const [styleOptions, setStyleOptions] = React.useState([]);
  const [fault, setFault] = React.useState(null);
  const [assets, setAssets] = React.useState([]);

  React.useEffect(() => {
    api.faults({ limit: 250 }).then((r) => setAll(r.faults || []));
    api.styles({ rank: 'style', limit: 200 }).then((r) =>
      setStyleOptions((r.results || []).map((s) => s.id).sort()));
  }, []);

  React.useEffect(() => {
    if (selection?.fault) setId(selection.fault);
  }, [selection?.fault]);

  React.useEffect(() => {
    if (!id) return;
    api.fault(id, styleInView || undefined)
      .then((f) => setFault({
        ...f,
        fix: f.fixes,   // the card reads `fix`; the record says `fixes`
        // the card reads exception.statement + a printable bounds; the record says
        // why + a {measurement: [lo, hi]} dict
        exceptions: (f.exceptions || []).map((e) => ({
          ...e,
          statement: e.why,
          bounds: e.bounds && typeof e.bounds === 'object'
            ? Object.entries(e.bounds).map(([k, v]) =>
                `${k} ${Array.isArray(v) ? v.join('–') : v}`).join(' · ')
            : e.bounds,
        })),
        // the card typesets `test` as prose beside the statement; the record's is a
        // structured rule — render it as the sentence it encodes, note included
        test: f.test
          ? `${f.test.expression} ${f.test.direction} ${f.test.threshold} ${f.test.units}` +
            ` · measurable from a ${f.test.measurable_from}` +
            (f.test.note ? ` — ${f.test.note}` : '')
          : null,
      }))
      .catch(() => setFault(null));
    api.assets({ fault: id, limit: 4 }).then((r) => setAssets(r.assets || [])).catch(() => setAssets([]));
  }, [id, styleInView]);

  const sevCounts = all.reduce((a, f) => { a[f.severity] = (a[f.severity] || 0) + 1; return a; }, {});
  const driverCounts = all.reduce((a, f) => {
    if (f.driver) a[f.driver] = (a[f.driver] || 0) + 1;
    return a;
  }, {});
  const list = all.filter((f) =>
    (!sev || f.severity === sev) && (!driver || f.driver === driver));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip right={
        <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Eyebrow as="span">exceptions for</Eyebrow>
          <select value={styleInView} onChange={(e) => setStyleInView(e.target.value)}
            style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', background: 'var(--paper-mat)',
              border: '1px solid var(--rule)', padding: '2px 6px', maxWidth: 190 }}>
            <option value="">no style in view</option>
            {styleOptions.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </span>
      }>
        <Eyebrow as="span">severity</Eyebrow>
        {['fatal', 'serious', 'minor'].map((s) => (
          <Chip key={s} on={sev === s} tone={SEV_C[s]}
            onClick={() => setSev(sev === s ? null : s)}>{s} {sevCounts[s] || 0}</Chip>
        ))}
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <Eyebrow as="span">cause driver</Eyebrow>
        {Object.entries(driverCounts).sort((a, b) => b[1] - a[1]).map(([d, n]) => (
          <Chip key={d} on={driver === d}
            onClick={() => setDriver(driver === d ? null : d)}>{d} {n}</Chip>
        ))}
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <div style={{ width: 330, flex: 'none', borderRight: '1px solid var(--rule)', overflow: 'auto',
          minHeight: 0 }}>
          <div style={{ padding: '11px 12px', borderBottom: '1px solid var(--rule)' }}>
            <Eyebrow>{all.length} solecisms · {list.length} shown here</Eyebrow>
            <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)', margin: '7px 0 0' }}>
              Of {all.length} cause drivers, exactly {driverCounts.ignorance || 0} {driverCounts.ignorance === 1 ? 'is' : 'are'}{' '}
              <span style={{ color: 'var(--ink-2)' }}>ignorance</span>.
              This is a system explaining an economy, not scolding a builder.
            </p>
          </div>
          {list.map((f) => {
            const on = f.id === id;
            return (
              <button key={f.id} type="button" onClick={() => setId(f.id)}
                style={{ display: 'block', width: '100%', textAlign: 'left', padding: '9px 12px 11px',
                  borderBottom: '1px solid var(--rule-soft)',
                  borderLeft: '2px solid ' + (on ? 'var(--gilt-deep)' : 'transparent'),
                  background: on ? 'var(--paper-deep)' : 'transparent', transition: 'var(--t-hover)' }}>
                <div style={{ font: 'var(--fw-reg) 15px/1.25 var(--display)', fontVariationSettings: '"opsz" 24',
                  color: on ? 'var(--ink)' : 'var(--ink-2)' }}>{f.name}</div>
                <div style={{ display: 'flex', gap: 10, marginTop: 5 }}>
                  <span style={{ font: 'var(--type-data-s)', color: SEV_C[f.severity] }}>{f.severity}</span>
                  <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>{f.frequency}</span>
                  <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>{f.slots && f.slots[0]}</span>
                </div>
              </button>
            );
          })}
        </div>

        <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '18px 22px 34px' }}>
          {fault && (
            <div style={{ display: 'flex', gap: 22, alignItems: 'flex-start', flexWrap: 'wrap' }}>
              <div style={{ flex: '1 1 520px', minWidth: 460, maxWidth: 760 }}>
                <FaultCard fault={fault} styleInView={styleInView || undefined}
                  onSlot={(s) => onCite && onCite('slot:' + s)} />
              </div>
              <div style={{ flex: '0 1 268px', minWidth: 240 }}>
                <Eyebrow style={{ marginBottom: 9 }}>evidence · specified, not yet sourced</Eyebrow>
                {assets.length === 0 && (
                  <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-4)', margin: 0 }}>
                    No image records are filed against this fault yet. The corpus holds 322
                    specified records and none has a photograph — the record is the object
                    until one does.
                  </p>
                )}
                {assets.map((a, i) => (
                  <UnsourcedImageRecord key={a.id || i} style={i ? { marginTop: 14 } : undefined}
                    record={{
                      id: a.id,
                      subject: a.caption || a.subject,
                      shot_spec: typeof a.shot_spec === 'string' ? a.shot_spec : JSON.stringify(a.shot_spec),
                      alt: a.alt_text || a.alt,
                      provenance_required: typeof a.provenance === 'string' ? a.provenance
                        : a.provenance_required || 'photographer credit + permission',
                    }} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
