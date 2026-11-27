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
    <div data-slot-panel={slot} data-record-page={'slot:' + slot} className="tdl-scroll">
      <div className="tdl-page">
        {error && (
          <p style={quiet}>
            {error.status === 404 ? <>The ontology holds no slot <code>{slot}</code>.</> : <>The slot could not be read.</>}
          </p>
        )}
        {!rec && !error && <p style={data}>reading the slot…</p>}
        {s && (
          <div>
            <header className="tdl-hero tdl-rise" style={{ marginBottom: 34 }}>
              <div className="tdl-hero-kicker">
                <Term id="slot" />
                {[s.cardinality, s.value_type, s.derives_from_module].filter(Boolean).map((w) => (
                  <React.Fragment key={w}><span aria-hidden="true">·</span><span>{w}</span></React.Fragment>
                ))}
              </div>
              <h2 data-record-head={s.id} className="tdl-record-title">
                {s.name || s.id}<span className="tdl-record-id" data-record-id="">{s.id}</span>
              </h2>
              <div className="tdl-hero-acts">
                <StylePicker value="" allowNone noneLabel="open it in a style’s kit" width={280}
                  label="Which style's kit to open this slot in"
                  onChange={(v) => { if (v) nav.cite('kit:' + v + '#' + slot); }} />
              </div>
              <div className="tdl-rule-double" style={{ marginTop: 26 }} />
            </header>

            {s.note && <p className="tdl-lede">{s.note}</p>}
            {rec.note && <p style={{ ...quiet, fontStyle: 'italic', margin: '0 0 30px' }}>{rec.note}</p>}

            {/* PHASE 17 (WP-17.13): who binds it across every style, as one bar of four parts that
                sum to the whole -- the route's counts, each part in its binding's ink and word. */}
            {bar && (
              <div data-binding-bar={bar.map((p) => p.n).join(' ')} style={{ margin: '0 0 40px', maxWidth: '46rem' }}>
                <div className="tdl-bar">
                  {bar.filter((p) => p.n > 0).map((p) => (
                    <span key={p.id} data-binding-part={p.id} style={{ flex: `${p.n} 0 0`, background: BAR_INK[p.id] }} />
                  ))}
                </div>
                <div className="tdl-bar-key">
                  {bar.map((p) => (
                    <span key={p.id}>
                      <BindingChip binding={p.id}><Term id={REACH_TERM[p.id]} /></BindingChip>
                      <span style={data}>{p.n}</span>
                    </span>
                  ))}
                </div>
                {bound.note && <p data-binding-note="" style={{ ...quiet, margin: '10px 0 0' }}>{bound.note}</p>}
              </div>
            )}
            <Section eyebrow={<><Term id="slot-reach-specified" /> · <Term id="slot-reach-extended" /> · {by.length}</>} data-specified-by={by.length}>
              <div className="tdl-columns">
                {by.map((id) => (
                  <div key={id} data-specifying-style={id} className="tdl-index-row">
                    <RecordLink cite={'kit:' + id + '#' + slot} />
                  </div>
                ))}
              </div>
            </Section>

            {forbids.length > 0 && (
              <Section eyebrow={<><Term id="binding-forbidden" /> · {forbids.length}</>} data-forbidden-by={forbids.length}>
                <div className="tdl-columns">
                  {forbids.map((id) => (
                    <div key={id} data-forbidding-style={id} className="tdl-index-row">
                      <RecordLink cite={'kit:' + id + '#' + slot} />
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {faults.length > 0 && (
              <Section eyebrow={<><Term id="fault" /> · {faults.length}</>}>
                {faults.map((f) => (
                  <div key={f.id} data-slot-fault={f.id} className="tdl-reason-row" style={{ gridTemplateColumns: 'minmax(5rem, 7rem) minmax(0, 1fr)' }}>
                    <span style={data}>
                      {f.severity ? <Term field="fault.severity" value={f.severity} /> : null}
                    </span>
                    <span><RecordLink cite={'fault:' + f.id}>{f.name || f.id}</RecordLink></span>
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
