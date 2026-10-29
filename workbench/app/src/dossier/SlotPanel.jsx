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
import { bindingBar } from '../elements/bindingBar.js';
/* THE BAR COUNTS WHAT EACH STYLE ENDS UP WITH, after the cascade, and its parts take their own words
   (Phase 17's audit). They were labelled with the kit's binding words, which say what a style writes
   in its OWN kit: "specified" read "the style fixes this slot itself" over a count in which 57 of the
   cornice's 86 inherit it, and "open" read "takes whatever its ancestors specify" over the styles
   where no ancestor specifies anything. */
const REACH_TERM = { specified: 'slot-reach-specified', extends: 'slot-reach-extended',
  forbidden: 'slot-reach-forbidden', open: 'slot-reach-open' };
import { BindingChip } from '../components/Chip.jsx';

// each part of the bar in its binding's own duty ink, open as the hairline it is
const BAR_INK = { specified: 'var(--bind-specified)', extends: 'var(--bind-extends)',
  forbidden: 'var(--bind-forbidden)', open: 'var(--border-hairline)' };

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
  const bar = bindingBar(bound);
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

            {/* PHASE 17 (WP-17.13): who binds it across every style, as one bar of four parts that
                sum to the whole -- the route's counts, each part in its binding's ink and word. */}
            {bar && (
              <div data-binding-bar={bar.map((p) => p.n).join(' ')} style={{ margin: '0 0 20px' }}>
                <div style={{ display: 'flex', height: 10, border: '1px solid var(--border-hairline)' }}>
                  {bar.filter((p) => p.n > 0).map((p) => (
                    <span key={p.id} data-binding-part={p.id} style={{ flex: `${p.n} 0 0`, background: BAR_INK[p.id] }} />
                  ))}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 16px', marginTop: 6 }}>
                  {bar.map((p) => (
                    <span key={p.id} style={{ display: 'inline-flex', gap: 6, alignItems: 'center' }}>
                      <BindingChip binding={p.id}><Term id={REACH_TERM[p.id]} /></BindingChip>
                      <span style={data}>{p.n}</span>
                    </span>
                  ))}
                </div>
                {bound.note && <p data-binding-note="" style={{ ...quiet, margin: '6px 0 0' }}>{bound.note}</p>}
              </div>
            )}
            <Section eyebrow={<><Term id="slot-reach-specified" /> · <Term id="slot-reach-extended" /> · {by.length}</>} data-specified-by={by.length}>
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
