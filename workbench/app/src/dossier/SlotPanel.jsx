/* One slot across every style — `#/elements/<slot>`, the slot's record page (WP-14.23, tranche 2
   §B.1; built at WP-14.12 as the interim page under `#/style/-/kit/<slot>`, which is now read as
   this address and rewritten).

   A `slot:` citation names a slot and no style, and until WP-14.12 it opened Tidewater
   Georgian's kit -- a style the citation never named -- because the Kit surface defaulted one.
   It lands here: the slot's own record from `GET /api/slots/{id}`, the styles whose RESOLVED kit
   specifies it and those whose resolved kit forbids it (`bindings`, read after the lineage
   cascade), and the faults written on it. Each style is a link to THAT style's kit opened at this
   slot (`kit:<style>#<slot>`), and a StylePicker opens it in any other style's kit.

   WP-14.23 moved the style lists off `specified_by_styles`, which `core.get_slot` reads from each
   node's OWN kit file and in which a style that FORBIDS the slot is listed as specifying it; that
   field is `tdl_get_slot`'s and is left byte-stable
   (`oq/the-slot-tool-lists-a-style-that-forbids-a-slot-as-specifying-it`). */
import React from 'react';
import { api } from '../api/client.js';
import { nav } from '../state/nav.js';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { StylePicker } from '../components/StylePicker.jsx';
import { FilterStrip } from '../Chrome.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { Section, prose, quiet, data } from './parts.jsx';

export function SlotPanel({ slot }) {
  const [rec, setRec] = React.useState(null);
  const [error, setError] = React.useState(null);
  React.useEffect(() => {
    setRec(null); setError(null);
    api.slot(slot).then(setRec).catch((e) => setError(e));
  }, [slot]);

  const s = rec && rec.slot ? rec.slot : null;
  const bound = rec && rec.bindings ? rec.bindings : {};
  const by = Array.isArray(bound.specified) ? bound.specified : [];
  const forbids = Array.isArray(bound.forbidden) ? bound.forbidden : [];
  const faults = rec ? rec.faults_on_this_slot || [] : [];
  return (
    <div data-slot-panel={slot} data-record-page={'slot:' + slot} style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip>
        <Eyebrow as="span"><Term id="slot" /></Eyebrow>
        <StylePicker value="" allowNone noneLabel="open it in a style’s kit" width={240}
          label="Which style's kit to open this slot in"
          onChange={(v) => { if (v) nav.cite('kit:' + v + '#' + slot); }} />
      </FilterStrip>
      <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '20px 26px 40px' }}>
        {error && (
          <p style={quiet}>
            {error.status === 404 ? <>The ontology holds no slot <code>{slot}</code>.</> : <>The slot could not be read.</>}
          </p>
        )}
        {!rec && !error && <p style={data}>reading the slot…</p>}
        {s && (
          <div style={{ maxWidth: 760 }}>
            <h2 data-record-head={s.id} style={{ font: 'var(--fw-reg) var(--fs-d2, 28px)/1.1 var(--display)', letterSpacing: 'var(--tr-display)',
              margin: '0 0 4px' }}>
              {s.name || s.id}<span className="tdl-record-note">{s.id}</span>
            </h2>
            <p style={{ ...data, margin: '0 0 12px' }}>
              {[s.cardinality, s.value_type, s.derives_from_module].filter(Boolean).join(' · ')}
            </p>
            {s.note && <p style={prose}>{s.note}</p>}
            {rec.note && <p style={{ ...quiet, fontStyle: 'italic', margin: '0 0 18px' }}>{rec.note}</p>}

            <Section eyebrow={<><Term id="binding-specified" /> · {by.length}</>} data-specified-by={by.length}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 16px' }}>
                {by.map((id) => (
                  <span key={id} data-specifying-style={id}>
                    <RecordLink cite={'kit:' + id + '#' + slot} />
                  </span>
                ))}
              </div>
            </Section>

            {forbids.length > 0 && (
              <Section eyebrow={<><Term id="binding-forbidden" /> · {forbids.length}</>} data-forbidden-by={forbids.length}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 16px' }}>
                  {forbids.map((id) => (
                    <span key={id} data-forbidding-style={id}>
                      <RecordLink cite={'kit:' + id + '#' + slot} />
                    </span>
                  ))}
                </div>
              </Section>
            )}

            {faults.length > 0 && (
              <Section eyebrow={<><Term id="fault" /> · {faults.length}</>}>
                {faults.map((f) => (
                  <div key={f.id} data-slot-fault={f.id} style={{ display: 'flex', gap: 10, alignItems: 'baseline', padding: '3px 0' }}>
                    <span style={{ ...data, width: 64, flex: 'none' }}>
                      {f.severity ? <Term field="fault.severity" value={f.severity} /> : null}
                    </span>
                    <RecordLink cite={'fault:' + f.id}>{f.name || f.id}</RecordLink>
                  </div>
                ))}
              </Section>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
