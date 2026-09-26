/* Compare — two styles side by side (WP-14.26, tranche 2 PRD §B.1, §C.7).

   `#/compare/<a>/<b>[/<section>]`. The family tree's shift-click comparison printed
   `/api/styles/compare` into a side panel -- falling back to `JSON.stringify` for an entry it did
   not recognise -- and compared nothing about the two KITS, which is where two styles a reader
   confuses actually part. This page is the comparison as a place: an address, a trail, and four
   sections read down the page, each a dossier section and worded by that section's record.

   - IDENTIFY: how the corpus tells the two apart -- each style's own disambiguation of the other,
     its author named -- then both styles' tells, whether either descends from the other, and the
     ancestors they share.
   - KIT: only the slots where the two RESOLVED kits differ, each with both bindings, both variant
     sets and both sources. The rows are `/api/compare`'s, which are the difference of the two
     `/api/kit` payloads (`workbench/server/tests/test_compare_route.py`), so this page cannot hold
     a third answer about either kit. A slot the two answer alike from different sources is drawn
     apart, under the `kit-same-answer` record's word, rather than dropped or mixed in.
   - PROPORTIONS: each style's packs by provenance, drawn by the dossier's own `PackLists`.
   - PLANS: each style's partis with their nativity, as the dossier's Plan types serves them.

   Every word is a record's: the sections' `section-*`, the columns' `binding`, `variant-status-*`
   and `cascade-source`, `compare-with`, `diagnostic-tell`, `edge-descends-from`,
   `shared-ancestry`. Every figure is the payload's. The decisions are `compare/view.js`'s. */
import React from 'react';
import { api } from '../api/client.js';
import { useGlossary } from '../api/useGlossary.js';
import { termView } from '../glossary/termView.js';
import { Term } from '../components/Term.jsx';
import { RecordLink } from '../components/RecordLink.jsx';
import { StylePicker } from '../components/StylePicker.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { Section, SectionWord, prose, quiet, data } from '../dossier/parts.jsx';
import { PackLists } from '../dossier/ProportionsSection.jsx';
import { NATIVITY_TERMS } from '../candidateOrder.js';
import {
  COMPARE_SECTIONS, compareSectionOf, compareSectionHref, kitGroups, authorOf, stylesOf,
} from '../compare/view.js';

const quietText = { font: 'var(--type-body)', color: 'var(--ink-2)' };
const two = { display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '0 28px' };
const mono = { fontFamily: 'var(--mono)', fontSize: 12 };

/* A record's word as plain text, for the one place a `Term` cannot sit: an input's label. */
function useWord(id) {
  const v = termView(useGlossary(), { id });
  return v.state === 'ready' ? v.word : undefined;
}

function StyleName({ id, name }) {
  return <RecordLink cite={'style:' + id}>{name || undefined}</RecordLink>;
}

/* ── identify ──────────────────────────────────────────────────────────────────────────────── */
function Identify({ a, b, identify }) {
  const idf = identify || {};
  const names = { [a]: idf.a && idf.a.name, [b]: idf.b && idf.b.name };
  const dis = idf.explicit_disambiguation;
  const shared = Array.isArray(idf.shared_ancestry) ? idf.shared_ancestry : [];
  return (
    <>
      {Array.isArray(dis) ? dis.map((d, i) => {
        const by = authorOf(d, a, b);
        return (
          <div key={i} data-disambiguation-by={by || undefined} style={{ marginBottom: 12 }}>
            {by && <div style={data}><StyleName id={by} name={names[by]} /></div>}
            <p style={prose}>{d.difference || d.note || d.tell}</p>
          </div>
        );
      }) : (typeof dis === 'string' && <p style={quiet} data-disambiguation-none="">{dis}</p>)}
      <div style={{ ...two, marginTop: 16 }}>
        {[[a, idf.tells_a], [b, idf.tells_b]].map(([sid, tells]) => (
          <Section key={sid} data-tells-of={sid}
            eyebrow={<><Term id="diagnostic-tell" /> · <StyleName id={sid} name={names[sid]} /></>}>
            {(tells || []).map((t, i) => (
              <p key={i} style={{ ...quiet, marginBottom: 7 }}>{typeof t === 'string' ? t : t.tell || t.statement}</p>
            ))}
          </Section>
        ))}
      </div>
      {(idf.a_descends_from_b || idf.b_descends_from_a) && (
        <p data-descent="" style={{ ...quiet, marginBottom: 14 }}>
          {idf.a_descends_from_b
            ? <><StyleName id={a} name={names[a]} /> <Term id="edge-descends-from" /> <StyleName id={b} name={names[b]} /></>
            : <><StyleName id={b} name={names[b]} /> <Term id="edge-descends-from" /> <StyleName id={a} name={names[a]} /></>}
        </p>
      )}
      {shared.length > 0 && (
        <Section eyebrow={<><Term id="shared-ancestry" /> · {shared.length}</>} data-shared-ancestry={shared.length}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px 16px' }}>
            {shared.map((sid) => <span key={sid}><RecordLink cite={'style:' + sid} /></span>)}
          </div>
        </Section>
      )}
    </>
  );
}

/* ── kit ───────────────────────────────────────────────────────────────────────────────────── */
function KitCell({ side, differs }) {
  const on = (f) => (differs.includes(f) ? { color: 'var(--ink)' } : { color: 'var(--ink-2)' });
  return (
    <div style={{ font: 'var(--fw-reg) 13px/1.5 var(--body)' }}>
      <div style={on('binding')} data-field="binding">
        {side.binding ? <Term field="kit.binding" value={side.binding} /> : null}
      </div>
      {side.canonical.length > 0 && (
        <div style={{ ...mono, ...on('canonical') }} data-field="canonical">{side.canonical.join(' · ')}</div>
      )}
      {side.forbidden.length > 0 && (
        <div style={{ ...mono, ...on('forbidden') }} data-field="forbidden">
          <Term id="variant-status-forbidden" /> {side.forbidden.join(' · ')}
        </div>
      )}
      <div style={{ ...data, ...on('source') }} data-field="source">{side.source || '—'}</div>
    </div>
  );
}

function KitRows({ rows }) {
  return rows.map((r) => (
    <div key={r.slot} data-kit-row={r.slot} data-differs-on={r.differs_on.join(' ')}
      style={{ display: 'grid', gridTemplateColumns: '190px minmax(0, 1fr) minmax(0, 1fr)', gap: '0 22px',
        padding: '7px 0', borderTop: '1px solid var(--rule-soft)' }}>
      <div style={{ font: 'var(--fw-reg) 13.5px/1.35 var(--serif)' }}>
        <RecordLink cite={'slot:' + r.slot}>{r.name || undefined}</RecordLink>
      </div>
      <KitCell side={r.a} differs={r.differs_on} />
      <KitCell side={r.b} differs={r.differs_on} />
    </div>
  ));
}

function KitHead({ a, b, names }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '190px minmax(0, 1fr) minmax(0, 1fr)', gap: '0 22px',
      padding: '0 0 5px' }}>
      <Eyebrow as="span"><Term id="slot" /></Eyebrow>
      {[a, b].map((sid) => (
        <span key={sid} style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
          <StyleName id={sid} name={names[sid]} />
          <span style={{ display: 'block' }}>
            <Term id="binding" /> · <Term id="variant-status-canonical" /> · <Term id="variant-status-forbidden" /> · <Term id="cascade-source" />
          </span>
        </span>
      ))}
    </div>
  );
}

function Kit({ a, b, kit, names }) {
  const g = kitGroups(kit);
  return (
    <>
      <KitHead a={a} b={b} names={names} />
      <div data-kit-answer={g.answer.length}><KitRows rows={g.answer} /></div>
      {g.source.length > 0 && (
        <Section style={{ marginTop: 22 }} data-kit-source-only={g.source.length}
          eyebrow={<><Term id="kit-same-answer" /> · {g.source.length}</>}>
          <KitRows rows={g.source} />
        </Section>
      )}
    </>
  );
}

/* ── plans ─────────────────────────────────────────────────────────────────────────────────── */
function Plans({ partis, styleId }) {
  return (partis || []).map((p) => (
    <div key={p.id} data-parti={p.id} data-nativity={p.nativity || undefined}
      style={{ display: 'flex', gap: 10, alignItems: 'baseline', padding: '3px 0', flexWrap: 'wrap' }}>
      <span style={{ font: 'var(--fw-reg) 14px/1.4 var(--serif)' }}>
        <RecordLink cite={'parti:' + p.id} ctx={{ style: styleId }}>{p.name || undefined}</RecordLink>
      </span>
      {NATIVITY_TERMS[p.nativity] && <Term id={NATIVITY_TERMS[p.nativity]} />}
    </div>
  ));
}

/* ── the page ──────────────────────────────────────────────────────────────────────────────── */
export function Compare({ selection, setSelection }) {
  const { a, b } = stylesOf(selection);
  const section = compareSectionOf(selection);
  const [payload, setPayload] = React.useState(null);
  const [error, setError] = React.useState(null);
  const scroller = React.useRef(null);
  const withWord = useWord('compare-with');

  React.useEffect(() => {
    setPayload(null); setError(null);
    if (!a || !b) return undefined;
    let live = true;
    api.compare(a, b).then((p) => { if (live) setPayload(p); }).catch((e) => { if (live) setError(e); });
    return () => { live = false; };
  }, [a, b]);

  // The section the address names is the one scrolled to, once there is a page to scroll.
  React.useEffect(() => {
    const box = scroller.current;
    if (!payload || !box) return;
    const el = box.querySelector(`[data-compare-section="${section}"]`);
    if (el && section !== COMPARE_SECTIONS[0]) el.scrollIntoView({ block: 'start' });
    else box.scrollTop = 0;
  }, [payload, section]);

  const pickA = (v) => setSelection && setSelection({ style: v || null });
  const pickB = (v) => setSelection && setSelection({ compare: v || null });
  const idf = payload ? payload.identify || {} : {};
  const names = { [a]: idf.a && idf.a.name, [b]: idf.b && idf.b.name };
  const missing = error && error.body && error.body.detail && Array.isArray(error.body.detail.missing)
    ? error.body.detail.missing : null;

  return (
    <div data-compare={a && b ? `${a}/${b}` : ''} style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <header data-compare-head="" style={{ flex: 'none', padding: '14px 26px 10px', borderBottom: '1px solid var(--rule)' }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <StylePicker value={a || ''} width={230} onChange={pickA} />
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}><Term id="compare-with" /></span>
          <StylePicker value={b || ''} width={230} label={withWord} onChange={pickB} />
        </div>
        {a && b && (
          <h2 style={{ font: 'var(--fw-reg) var(--fs-d2, 26px)/1.15 var(--display)', letterSpacing: 'var(--tr-display)',
            margin: '10px 0 2px' }}>
            <StyleName id={a} name={names[a]} /> · <StyleName id={b} name={names[b]} />
          </h2>
        )}
      </header>

      {a && b && (
        <nav aria-label="compare sections" data-compare-strip=""
          style={{ flex: 'none', display: 'flex', gap: 2, padding: '0 20px', borderBottom: '1px solid var(--rule)',
            overflowX: 'auto', background: 'var(--paper)' }}>
          {COMPARE_SECTIONS.map((id) => {
            const on = id === section;
            return (
              <a key={id} href={compareSectionHref(a, b, id)} aria-current={on ? 'page' : undefined}
                data-compare-section-link={id}
                style={{ padding: '8px 10px 7px', whiteSpace: 'nowrap', textDecoration: 'none',
                  color: on ? 'var(--ink)' : 'var(--ink-2)',
                  borderBottom: on ? '2px solid var(--gilt-deep)' : '2px solid transparent',
                  font: (on ? 'var(--fw-med)' : 'var(--fw-reg)') + ' 13px/1.3 var(--body)' }}>
                <SectionWord id={id} />
              </a>
            );
          })}
        </nav>
      )}

      <div ref={scroller} data-compare-scroller="" style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '20px 26px 60px' }}>
        {error && (
          <div data-compare-missing={missing ? missing.join(' ') : ''}>
            {missing
              ? missing.map((m) => <p key={m} style={quietText}>The corpus holds no style <code>{m}</code>.</p>)
              : <p style={quietText}>The comparison could not be read.</p>}
          </div>
        )}
        {a && b && !payload && !error && <p style={data}>reading the comparison…</p>}
        {payload && (
          <>
            <Section data-compare-section="identify" eyebrow={<SectionWord id="identify" />}>
              <Identify a={a} b={b} identify={payload.identify} />
            </Section>
            <Section data-compare-section="kit" data-kit-rows={(payload.kit.rows || []).length}
              data-kit-compared={payload.kit.slots_compared}
              eyebrow={<><SectionWord id="kit" /> · {(payload.kit.rows || []).length}</>}>
              <Kit a={a} b={b} kit={payload.kit} names={names} />
            </Section>
            <Section data-compare-section="proportions" eyebrow={<SectionWord id="proportions" />}>
              <div style={two}>
                {['a', 'b'].map((side) => {
                  const sid = side === 'a' ? a : b;
                  return (
                    <div key={side} data-packs-of={sid}>
                      <p style={{ ...data, margin: '0 0 8px' }}><StyleName id={sid} name={names[sid]} /></p>
                      <PackLists payload={payload.proportions[side]} styleId={sid} />
                    </div>
                  );
                })}
              </div>
            </Section>
            <Section data-compare-section="plans" eyebrow={<SectionWord id="plans" />}>
              <div style={two}>
                {['a', 'b'].map((side) => {
                  const sid = side === 'a' ? a : b;
                  const partis = payload.plans[side] || [];
                  return (
                    <div key={side} data-plans-of={sid} data-plan-count={partis.length}>
                      <p style={{ ...data, margin: '0 0 8px' }}>
                        <StyleName id={sid} name={names[sid]} /> · <Term id="parti" /> · {partis.length}
                      </p>
                      <Plans partis={partis} styleId={sid} />
                    </div>
                  );
                })}
              </div>
            </Section>
          </>
        )}
      </div>
    </div>
  );
}
