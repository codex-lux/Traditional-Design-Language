/* Surface ⑨ — the Fault Corpus, live. Element-first: faults hang off slots, not styles.
   The list filters on the corpus's own axes; the reading pane fetches the full record
   (find_faults cards are summaries) and style exceptions render above the general rule. */
import React from 'react';
import { api } from '../api/client.js';
import { FaultCard } from '../components/FaultCard.jsx';
import { UnsourcedImageRecord } from '../components/UnsourcedImageRecord.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterStrip, Chip, ChipGroup, FilterGroup } from '../Chrome.jsx';
import { FilterInput } from '../components/FilterInput.jsx';
import { StylePicker } from '../components/StylePicker.jsx';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { matches } from '../search/match.js';

const SEV_C = { fatal: 'var(--sev-fatal)', serious: 'var(--sev-serious)', minor: 'var(--sev-minor)' };
const SPEC = { sev: {}, driver: {}, q: { type: 'text' }, style: {} };

export function FaultCorpus({ onCite, selection, setSelection }) {
  const [all, setAll] = React.useState([]);
  const [id, setId] = React.useState(selection?.fault || 'porch-too-shallow-to-inhabit');
  const [fault, setFault] = React.useState(null);
  const [assets, setAssets] = React.useState([]);

  const filters = useSurfaceFilters(SPEC);
  const { sev, driver, q } = filters.values;
  const styleInView = filters.values.style || '';

  React.useEffect(() => {
    api.faults({ limit: 250 }).then((r) => setAll(r.faults || []));
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
    (!sev || f.severity === sev)
    && (!driver || f.driver === driver)
    && matches(f, q, ['name', 'id', 'severity', 'driver', 'frequency', 'aka',
                      (r) => (r.slots || []).join(' ')]));

  const drivers = Object.entries(driverCounts).sort((a, b) => b[1] - a[1]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip filters={filters} right={
        <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Eyebrow as="span" style={{ whiteSpace: 'nowrap' }}>exceptions</Eyebrow>
          <StylePicker value={styleInView} onChange={(v) => filters.set('style', v)}
            label="Read the corpus with one style's exceptions in view" allowNone width={160}
            noneLabel="no style" />
        </span>
      }>
        <FilterInput value={q} onChange={(v) => filters.set('q', v)} count={list.length}
          label="Filter the 209 faults by name, slot, severity or driver"
          placeholder="filter 209 faults" width={180} />
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <ChipGroup label="severity">
          <Eyebrow as="span">severity</Eyebrow>
          {['fatal', 'serious', 'minor'].map((s) => (
            <Chip key={s} radio on={sev === s} tone={SEV_C[s]}
              onClick={() => filters.toggle('sev', s)}>{s} {sevCounts[s] || 0}</Chip>
          ))}
        </ChipGroup>
        {/* The nine cause drivers are a long tail nobody steers by daily — they fold, and
            the fold says which one is on so nothing hides behind it. */}
        <FilterGroup label="cause driver" active={driver ? 1 : 0} summary={driver || ''}>
          <ChipGroup label="cause driver">
            {drivers.map(([d, n]) => (
              <Chip key={d} radio on={driver === d}
                onClick={() => filters.toggle('driver', d)}>{d} {n}</Chip>
            ))}
          </ChipGroup>
        </FilterGroup>
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <div style={{ width: 330, flex: 'none', borderRight: '1px solid var(--rule)', overflow: 'auto',
          minHeight: 0 }}>
          <div style={{ padding: '11px 12px', borderBottom: '1px solid var(--rule)' }}>
            <Eyebrow>
              {all.length} solecisms · {list.length} shown here
              {list.length !== all.length && filters.activeCount > 0 ? ' · filtered' : ''}
            </Eyebrow>
            <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)', margin: '7px 0 0' }}>
              Of {all.length} cause drivers, exactly {driverCounts.ignorance || 0} {driverCounts.ignorance === 1 ? 'is' : 'are'}{' '}
              <span style={{ color: 'var(--ink-2)' }}>ignorance</span>.
              This is a system explaining an economy, not scolding a builder.
            </p>
          </div>
          {list.length === 0 && all.length > 0 && (
            <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)',
              margin: 0, padding: '14px 12px' }}>
              No fault matches. The corpus holds {all.length}; the filters above are hiding
              all of them.
            </p>
          )}
          {list.map((f) => {
            const on = f.id === id;
            return (
              /* Selecting writes the URL, so a fault you are reading is a link you can
                 send — and the citation the rail would use for it is the same string. */
              <button key={f.id} type="button"
                onClick={() => { setId(f.id); setSelection && setSelection({ fault: f.id }); }}
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
