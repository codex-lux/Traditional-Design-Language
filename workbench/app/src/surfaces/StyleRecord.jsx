/* Surface ③ — the Style Record, live. Everything the corpus knows about one taxon,
   at the depth the reader asks for. Tells and distinguished_from get more room than
   the description — they are the job ("is this Federal or Greek Revival?").
   Constraints render in three states and the judgment rows are offered back to the
   human, not hidden. Every id on the page is a citation target. */
import React from 'react';
import { api } from '../api/client.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { EdgeGlyph } from '../components/EdgeGlyph.jsx';
import { VariantPill } from '../components/VariantPill.jsx';
import { JudgmentMark } from '../components/JudgmentMark.jsx';
import { FilterStrip, Chip } from '../Chrome.jsx';

const ALL_SECTIONS = 'summary,description,characteristics,lineage,proportion,massing,constraints,exemplars,sources';
const CARRIES = { descends_from: 1, regional_of: 1 };

function Section({ eyebrow, children, style }) {
  return (
    <section style={{ marginBottom: 26, ...style }}>
      <Eyebrow style={{ marginBottom: 9 }}>{eyebrow}</Eyebrow>
      {children}
    </section>
  );
}

const prose = { font: 'var(--fw-reg) 14px/1.62 var(--body)', color: 'var(--ink)', margin: '0 0 10px', maxWidth: '74ch' };
const quiet = { font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)', margin: 0, maxWidth: '72ch' };

export function StyleRecord({ onCite, selection, go, setSelection }) {
  const [styleId, setStyleId] = React.useState(selection?.style || 'tidewater-georgian');
  const [styleOptions, setStyleOptions] = React.useState([]);
  const [rec, setRec] = React.useState(null);
  const [constraintFilter, setConstraintFilter] = React.useState(null);

  React.useEffect(() => {
    api.styles({ limit: 200 }).then((r) => setStyleOptions((r.results || []).map((s) => s.id).sort()));
  }, []);
  React.useEffect(() => { if (selection?.style) setStyleId(selection.style); }, [selection?.style]);
  React.useEffect(() => {
    setRec(null);
    api.style(styleId, ALL_SECTIONS).then(setRec).catch(() => setRec(null));
  }, [styleId]);

  if (!rec) {
    return <div style={{ padding: 24, font: 'var(--type-body)', color: 'var(--ink-3)' }}>reading the record…</div>;
  }

  const s = rec.summary || {};
  const desc = rec.description || {};
  const constraints = rec.constraints || [];
  const tested = constraints.filter((c) => c.test);
  const untested = constraints.filter((c) => !c.test && c.scope !== 'judgment');
  const judgment = constraints.filter((c) => !c.test && c.scope === 'judgment');
  const shownConstraints = constraintFilter === 'tested' ? tested
    : constraintFilter === 'untested' ? untested
    : constraintFilter === 'judgment' ? judgment : constraints;

  // three deliberately unbound nodes — a named exception, not a hole (OQ 29)
  const unbound = ['egyptian-revival', 'moorish-andalusian', 'mudejar'].includes(styleId);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip right={
        <span style={{ display: 'flex', gap: 10 }}>
          <Chip onClick={() => onCite && onCite('kit:' + styleId)}>resolve the kit ④</Chip>
          <Chip onClick={() => { setSelection && setSelection({ style: styleId }); go && go('phylogeny'); }}>
            place in the phylogeny ②
          </Chip>
        </span>
      }>
        <Eyebrow as="span">style record</Eyebrow>
        <select value={styleId} onChange={(e) => setStyleId(e.target.value)}
          style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', background: 'var(--paper-mat)',
            border: '1px solid var(--rule)', padding: '2px 6px', maxWidth: 230 }}>
          {styleOptions.map((x) => <option key={x} value={x}>{x}</option>)}
        </select>
      </FilterStrip>

      <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '20px 26px 40px' }}>
        <div style={{ display: 'flex', gap: 34, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          {/* identity, description, tells, distinguished-from */}
          <div style={{ flex: '1 1 480px', minWidth: 420, maxWidth: 720 }}>
            <Eyebrow>{s.rank}{s.in ? ` · in ${s.in}` : ''} · {s.years}</Eyebrow>
            <h2 style={{ font: 'var(--fw-reg) var(--fs-d1, 34px)/1.08 var(--display)',
              letterSpacing: 'var(--tr-display)', margin: '8px 0 4px' }}>{s.name}</h2>
            <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', marginBottom: 4 }}>
              {rec.id} · {(s.regions || []).join(' · ')}
            </div>
            {desc.short && <p style={{ ...prose, fontStyle: 'italic', color: 'var(--ink-2)', marginTop: 10 }}>{desc.short}</p>}
            {desc.long && String(desc.long).split(/\n\n+/).map((p, i) => <p key={i} style={prose}>{p}</p>)}

            {(rec.diagnostic_tells || []).length > 0 && (
              <Section eyebrow={`diagnostic tells · ${rec.diagnostic_tells.length}`} style={{ marginTop: 24 }}>
                {rec.diagnostic_tells.map((t, i) => (
                  <p key={i} style={{ ...prose, paddingLeft: 14, borderLeft: '2px solid var(--gilt-deep)',
                    marginBottom: 9 }}>{typeof t === 'string' ? t : t.tell || t.statement}</p>
                ))}
              </Section>
            )}

            {(rec.distinguished_from || []).length > 0 && (
              <Section eyebrow="distinguished from · the nearest neighbours">
                {rec.distinguished_from.map((d, i) => {
                  const isMassing = String(d.node || '').startsWith('massing:');
                  return (
                    <div key={i} style={{ border: '1px solid var(--rule)', background: 'var(--paper-deep)',
                      padding: '11px 13px', marginBottom: 11 }}>
                      <button type="button"
                        onClick={() => !isMassing && onCite && onCite('style:' + d.node)}
                        style={{ font: 'var(--fw-reg) 15px/1.2 var(--display)', color: 'var(--ink)',
                          marginBottom: 6, display: 'block', textAlign: 'left',
                          cursor: isMassing ? 'default' : 'pointer' }}>
                        {d.node}
                        {isMassing && (
                          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', marginLeft: 8 }}>
                            a massing, not a style — separate namespaces
                          </span>
                        )}
                      </button>
                      <p style={quiet}>{d.difference}</p>
                    </div>
                  );
                })}
              </Section>
            )}

            {(rec.defining_characteristics || []).length > 0 && (
              <Section eyebrow={`defining characteristics · ${rec.defining_characteristics.length}`}>
                {rec.defining_characteristics.map((c, i) => (
                  <p key={i} style={{ ...quiet, marginBottom: 7 }}>· {c}</p>
                ))}
              </Section>
            )}
          </div>

          {/* the working columns */}
          <div style={{ flex: '1 1 400px', minWidth: 380, maxWidth: 560 }}>
            <Section eyebrow={`constraints · ${tested.length} tested · ${untested.length} untested · ${judgment.length} yours to judge`}>
              <div style={{ display: 'flex', gap: 6, marginBottom: 10 }}>
                {[['tested', tested.length], ['untested', untested.length], ['judgment', judgment.length]].map(([k, n]) => (
                  <Chip key={k} on={constraintFilter === k}
                    onClick={() => setConstraintFilter(constraintFilter === k ? null : k)}>{k} {n}</Chip>
                ))}
              </div>
              {shownConstraints.map((c) => (
                <div key={c.id} style={{ marginBottom: 12, paddingBottom: 10,
                  borderBottom: '1px solid var(--rule-soft)' }}>
                  {c.scope === 'judgment' ? (
                    <JudgmentMark state="unjudged" label={c.statement}
                      reason={`${c.id} · scope: judgment — the sources do not determine this; the tool puts it to you rather than deciding`} />
                  ) : (
                    <div>
                      <p style={{ ...prose, marginBottom: 4 }}>{c.statement}</p>
                      <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
                        {c.id} · {c.kind} · {c.severity} · {c.scope} ·{' '}
                        <span style={{ color: c.test ? 'var(--ink-2)' : 'var(--ink-4)',
                          border: '1px solid var(--rule)', padding: '0 5px' }}>
                          {c.test ? 'executable' : 'no test yet'}
                        </span>
                      </span>
                    </div>
                  )}
                </div>
              ))}
              <p style={{ ...quiet, color: 'var(--ink-3)', marginTop: 6 }}>
                A test never replaces the statement — the sentence is what a person argues
                with. A hatched row is a judgment the corpus refuses to invent; corpus-wide,
                295 of 660 constraints are that kind.
              </p>
            </Section>

            {(rec.massing_affinities || []).length > 0 && (
              <Section eyebrow="massing affinities · massing is not style">
                <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
                  {rec.massing_affinities.map((m) => (
                    <VariantPill key={m.massing} ladder="affinity" name={'massing:' + m.massing}
                      status={m.affinity} title={m.note} />
                  ))}
                </div>
              </Section>
            )}

            {rec.proportional_system && (
              <Section eyebrow="proportional system">
                <p style={prose}>{rec.proportional_system.governing_logic}</p>
                {(rec.proportional_system.typical_ratios || []).map((r, i) => (
                  <p key={i} style={{ ...quiet, fontFamily: 'var(--mono)', fontSize: 12, marginBottom: 5 }}>{r}</p>
                ))}
                {unbound ? (
                  <div style={{ border: '1px solid var(--rule)', padding: '9px 11px', marginTop: 10,
                    backgroundImage: 'var(--hatch-45)' }}>
                    <p style={{ ...quiet, background: 'var(--paper)', padding: '3px 7px', display: 'inline-block' }}>
                      Deliberately unbound to any proportion pack — a named exception, not a hole
                      (OQ 29). No pack in the library encodes this system's setting-out; binding
                      the wrong one would be worse than binding none.
                    </p>
                  </div>
                ) : (rec.proportion_packs || []).map((p) => (
                  <div key={p.pack + (p.role || '')} title={p.note}
                    style={{ display: 'flex', gap: 10, alignItems: 'baseline', padding: '2px 0' }}>
                    <button type="button" onClick={() => onCite && onCite('pack:' + p.pack)}
                      style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)',
                        borderBottom: '1px solid var(--link-underline)' }}>{p.pack}</button>
                    <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)' }}>{p.role}</span>
                  </div>
                ))}
              </Section>
            )}

            {(rec.lineage || []).length > 0 && (
              <Section eyebrow="lineage · carries ≠ claims">
                {rec.lineage.map((e, i) => (
                  <div key={i} style={{ marginBottom: 10 }}>
                    <EdgeGlyph type={e.type} width={44} to={e.target} note={e.note} />
                  </div>
                ))}
                {(rec.descendants || []).length > 0 && (
                  <p style={{ ...quiet, marginTop: 8 }}>
                    Descendants:{' '}
                    {rec.descendants.map((d, i) => (
                      <React.Fragment key={d.id}>
                        {i > 0 && ' · '}
                        <button type="button" onClick={() => setStyleId(d.id)}
                          style={{ font: 'var(--type-data-s)',
                            color: CARRIES[d.type] ? 'var(--gilt-deep)' : 'var(--ink-3)' }}>
                          {d.id} ({d.type})
                        </button>
                      </React.Fragment>
                    ))}
                  </p>
                )}
              </Section>
            )}

            {(rec.exemplars || []).length > 0 && (
              <Section eyebrow={`exemplars · ${rec.exemplars.length} real buildings`}>
                {rec.exemplars.map((e, i) => (
                  <p key={i} style={{ ...quiet, marginBottom: 8 }}>
                    <span style={{ color: 'var(--ink)' }}>{e.name}</span>
                    {e.location ? ` — ${e.location}` : ''}{e.year ? `, ${e.year}` : ''}
                    {e.note ? <span style={{ display: 'block', color: 'var(--ink-3)' }}>{e.note}</span> : null}
                  </p>
                ))}
              </Section>
            )}

            {(rec.sources || []).length > 0 && (
              <Section eyebrow="sources">
                {rec.sources.map((src, i) => (
                  <p key={i} style={{ ...quiet, fontSize: 12.5, marginBottom: 5 }}>{src}</p>
                ))}
              </Section>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
