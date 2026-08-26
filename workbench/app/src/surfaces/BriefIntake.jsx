/* Surface ⑤ — Brief Intake. Captures what the composer needs and makes the SILENCES
   visible before they become assumptions: every field left blank is named as a
   decision the composer will take and report. The household stays prose — it is the
   most design-relevant sentence in the file. Feasibility is advisory, computed live,
   and never implies feasibility was proved (the conflict-set display waits on WP-2.3). */
import React from 'react';
import { api, jobEvents } from '../api/client.js';
import { session } from '../state/session.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { JudgmentMark } from '../components/JudgmentMark.jsx';
import { FilterStrip, Chip } from '../Chrome.jsx';

const COMPASS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];

/* An advisory fact, deliberately NOT a JudgmentMark: pass/fail belongs to evaluation
   against a plan, and this surface promises never to imply feasibility was proved.
   tone="limit" marks a corpus limit or out-of-band fact in ink, not in a verdict hue. */
function Advisory({ label, detail, tone }) {
  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
      <span aria-hidden="true" style={{ width: 9, height: 9, flex: 'none', marginTop: 4,
        border: '1px solid var(--ink-3)',
        background: tone === 'limit' ? 'transparent' : 'var(--ink-3)' }} />
      <span>
        <span style={{ font: 'var(--fw-reg) 13px/1.5 var(--body)',
          color: tone === 'limit' ? 'var(--ink)' : 'var(--ink-2)' }}>{label}</span>
        {detail && <span style={{ display: 'block', font: 'var(--fw-reg) 12px/1.5 var(--body)',
          color: 'var(--ink-3)' }}>{detail}</span>}
      </span>
    </div>
  );
}

const label = { font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)',
  textTransform: 'uppercase', color: 'var(--ink-3)', display: 'block', marginBottom: 5 };
const input = { background: 'var(--paper-mat)', border: '1px solid var(--rule-soft)',
  color: 'var(--ink)', font: 'var(--type-data)', padding: '5px 8px', width: '100%' };

export function BriefIntake({ go }) {
  const s = React.useSyncExternalStore(session.subscribe, session.get);
  const defaults = {
    id: 'new-brief', name: '', style: 'tidewater-georgian',
    target_area_sf: 3200, bedrooms: 4, bathrooms: 3.5,
    must_have: [], context: {}, household: '', candidates: 4,
  };
  // merge over defaults: a brief persisted by an older shape must never crash the form
  const [brief, setBrief] = React.useState(
    { ...defaults, ...(s.brief || {}), context: { ...(s.brief?.context || {}) } });
  const [styleOptions, setStyleOptions] = React.useState([]);
  const [partis, setPartis] = React.useState(null);
  const [rooms, setRooms] = React.useState([]);
  const [composing, setComposing] = React.useState(false);
  const [error, setError] = React.useState(null);
  const unsubRef = React.useRef(null);

  React.useEffect(() => {
    api.styles({ limit: 200 }).then((r) => setStyleOptions((r.results || []).map((x) => x.id).sort()));
    api.rooms({ limit: 60 }).then((r) => setRooms((r.results || r.rooms || []).map((x) => x.id)));
  }, []);
  React.useEffect(() => {
    if (!brief.style) return;
    api.partis({ style: brief.style }).then(setPartis).catch(() => setPartis(null));
  }, [brief.style]);
  React.useEffect(() => { session.set({ brief }); }, [brief]);

  const set = (k, v) => setBrief((b) => ({ ...b, [k]: v }));
  const setCtx = (k, v) => setBrief((b) => ({ ...b, context: { ...b.context, [k]: v } }));

  // Feasibility, all advisory
  const native = partis?.partis || [];
  const areaHit = native.filter((p) => p.area_range_sf
    && brief.target_area_sf >= p.area_range_sf[0] && brief.target_area_sf <= p.area_range_sf[1]);
  const bedHit = native.filter((p) => p.bedroom_range
    && brief.bedrooms >= p.bedroom_range[0] && brief.bedrooms <= p.bedroom_range[1]);
  const silent = [
    !brief.context.lot_width_ft && 'lot width', !brief.context.climate_zone && 'climate zone',
    !brief.context.entrance_faces && 'entrance orientation', !brief.storeys && 'storeys',
    !brief.massing && 'massing', !brief.context.budget_tier && 'budget tier',
  ].filter(Boolean);

  async function compose() {
    setError(null);
    setComposing(true);
    session.set({ result: null, progress: [] });
    const clean = JSON.parse(JSON.stringify(brief, (k, v) =>
      (v === '' || v === null || (Array.isArray(v) && !v.length)
        || (typeof v === 'object' && v && !Array.isArray(v) && !Object.keys(v).length)) ? undefined : v));
    // `min="1"` on the number input is decorative here — submit is a Chip, not a form, so
    // the browser never enforces it, and an empty field reads back as 0. The brief schema
    // gained `minimum: 1` on candidates, so 0 now refuses the WHOLE brief with a validation
    // error about a field the user was not thinking about. It was already ignored on the
    // wire (the count travels as its own argument), so drop it rather than refuse on it.
    const wanted = Number(brief.candidates);
    if (!Number.isFinite(wanted) || wanted < 1) delete clean.candidates;
    try {
      const { job_id } = await api.compose(clean, wanted >= 1 ? wanted : 4);
      session.set({ jobId: job_id });
      if (unsubRef.current) unsubRef.current();   // a superseded compose drops its stream
      unsubRef.current = jobEvents(job_id, {
        stage: (d) => session.pushProgress(d),
        candidate: (d) => session.pushProgress(d),
        // no navigation here: yanking the user to the Candidate Set minutes later,
        // from wherever they are, is worse than letting the rail chip or the nav
        // take them — the immediate go() below already lands them there once
        done: (d) => { session.set({ result: d }); setComposing(false); },
        error: (d) => { setError(d.error); setComposing(false); },
      });
      go('candidates');
    } catch (e) {
      setError(e.body?.detail?.detail || e.body?.detail?.error || e.message);
      setComposing(false);
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip right={
        <Chip on={composing} onClick={composing ? undefined : compose}>
          {composing ? 'composing…' : `compose ${brief.candidates || 4} candidates`}
        </Chip>
      }>
        <Eyebrow as="span">brief intake</Eyebrow>
        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
          only style and target area are required — everything else absent becomes a logged decision
        </span>
      </FilterStrip>

      <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '20px 24px 34px' }}>
        {error && (
          <div style={{ border: '1px solid var(--sev-serious)', padding: '10px 12px', marginBottom: 16,
            font: 'var(--fw-reg) 13px/1.5 var(--body)', color: 'var(--ink)' }}>
            The brief was refused: {String(error)}
          </div>
        )}

        <div style={{ display: 'flex', gap: 28, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          {/* the brief */}
          <div style={{ flex: '1 1 420px', minWidth: 380, maxWidth: 560 }}>
            <Eyebrow style={{ marginBottom: 12 }}>the brief</Eyebrow>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div>
                <span style={label}>name</span>
                <input style={input} value={brief.name}
                  onChange={(e) => { set('name', e.target.value); set('id', e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, '-') || 'new-brief'); }} />
              </div>
              <div>
                <span style={label}>style · required</span>
                <select style={input} value={brief.style} onChange={(e) => set('style', e.target.value)}>
                  {styleOptions.map((x) => <option key={x} value={x}>{x}</option>)}
                </select>
              </div>
              <div>
                <span style={label}>target area, sf · required</span>
                <input style={input} type="number" step="50" value={brief.target_area_sf}
                  onChange={(e) => set('target_area_sf', +e.target.value)} />
              </div>
              <div>
                <span style={label}>candidates</span>
                <input style={input} type="number" min="1" max="8" value={brief.candidates}
                  onChange={(e) => set('candidates', e.target.value === '' ? null : +e.target.value)} />
              </div>
              <div>
                <span style={label}>bedrooms</span>
                <input style={input} type="number" min="1" max="8" value={brief.bedrooms ?? ''}
                  onChange={(e) => set('bedrooms', e.target.value === '' ? null : +e.target.value)} />
              </div>
              <div>
                <span style={label}>bathrooms</span>
                <input style={input} type="number" step="0.5" value={brief.bathrooms ?? ''}
                  onChange={(e) => set('bathrooms', e.target.value === '' ? null : +e.target.value)} />
              </div>
            </div>

            <div style={{ marginTop: 16 }}>
              <span style={label}>must have · room types the composer will not drop</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {(brief.must_have || []).map((m) => (
                  <Chip key={m} on onClick={() => set('must_have', brief.must_have.filter((x) => x !== m))}>{m} ×</Chip>
                ))}
                <select style={{ ...input, width: 180 }} value=""
                  onChange={(e) => e.target.value && set('must_have', [...(brief.must_have || []), e.target.value])}>
                  <option value="">add a room type…</option>
                  {rooms.filter((r) => !(brief.must_have || []).includes(r)).map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </div>
            </div>

            <div style={{ marginTop: 18 }}>
              <span style={label}>the household · prose, and it stays prose</span>
              <textarea rows={4} style={{ ...input, font: 'var(--type-prose)', lineHeight: 1.6 }}
                placeholder="Who lives here and how they use a house — the thing that decides whether the dining room gets built and never used."
                value={brief.household}
                onChange={(e) => set('household', e.target.value)} />
            </div>
          </div>

          {/* the site */}
          <div style={{ flex: '0 1 340px', minWidth: 300 }}>
            <Eyebrow style={{ marginBottom: 12 }}>the site</Eyebrow>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div>
                <span style={label}>lot width, ft</span>
                <input style={input} type="number" value={brief.context.lot_width_ft ?? ''}
                  onChange={(e) => setCtx('lot_width_ft', e.target.value === '' ? null : +e.target.value)} />
              </div>
              <div>
                <span style={label}>lot depth, ft</span>
                <input style={input} type="number" value={brief.context.lot_depth_ft ?? ''}
                  onChange={(e) => setCtx('lot_depth_ft', e.target.value === '' ? null : +e.target.value)} />
              </div>
              <div>
                <span style={label}>climate zone</span>
                <input style={input} placeholder="3A" value={brief.context.climate_zone ?? ''}
                  onChange={(e) => setCtx('climate_zone', e.target.value || null)} />
              </div>
              <div>
                <span style={label}>budget tier</span>
                <select style={input} value={brief.context.budget_tier ?? ''}
                  onChange={(e) => setCtx('budget_tier', e.target.value || null)}>
                  <option value="">unstated</option>
                  {['entry', 'move-up', 'custom', 'estate'].map((b) => <option key={b} value={b}>{b}</option>)}
                </select>
              </div>
            </div>

            <div style={{ marginTop: 14 }}>
              <span style={label}>entrance faces · a compass, diagonals allowed</span>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 4 }}>
                {COMPASS.map((d) => (
                  <Chip key={d} on={brief.context.entrance_faces === d}
                    onClick={() => setCtx('entrance_faces', brief.context.entrance_faces === d ? null : d)}>{d}</Chip>
                ))}
              </div>
            </div>

            <div style={{ marginTop: 14 }}>
              <span style={label}>jurisdiction · advisory, never compliance</span>
              <input style={input} placeholder="IRC model text, advisory"
                value={brief.context.jurisdiction ?? ''}
                onChange={(e) => setCtx('jurisdiction', e.target.value || null)} />
            </div>
          </div>

          {/* feasibility, advisory */}
          <div style={{ flex: '0 1 330px', minWidth: 300 }}>
            <Eyebrow style={{ marginBottom: 12 }}>feasibility · advisory, computed as you type</Eyebrow>

            <div style={{ marginBottom: 12 }}>
              {partis === null ? (
                <JudgmentMark state="unjudged" label="native partis unknown" reason="reading the corpus…" />
              ) : native.length === 0 ? (
                <Advisory tone="limit"
                  label={`${brief.style} has no native parti — the composer will borrow diagrams`}
                  detail="Three of the corpus's 132 styles and variants have none — egyptian-revival, new-urbanist-traditional and tuscan-vernacular — and every candidate here will carry the NOT-native label. This is one of the three, not the norm: WP-4.5 took native coverage from 93 uncovered to 0, and this panel claimed the pre-WP-4.5 figure until 26 Aug 2026." />
              ) : (
                <Advisory
                  label={`${native.length} parti${native.length === 1 ? '' : 's'} native to ${brief.style}`}
                  detail={native.map((p) => p.name).join(' · ')} />
              )}
            </div>

            {native.length > 0 && (
              <div style={{ marginBottom: 12 }}>
                {areaHit.length > 0
                  ? <Advisory label={`${brief.target_area_sf?.toLocaleString()} sf sits inside ${areaHit.length} native area band${areaHit.length === 1 ? '' : 's'}`} />
                  : <Advisory tone="limit"
                      label={`${brief.target_area_sf?.toLocaleString()} sf is outside every native parti's area band`}
                      detail={native.map((p) => `${p.name}: ${p.area_range_sf?.[0]}–${p.area_range_sf?.[1]} sf`).join(' · ')} />}
              </div>
            )}
            {native.length > 0 && brief.bedrooms != null && (
              <div style={{ marginBottom: 12 }}>
                {bedHit.length > 0
                  ? <Advisory label={`${brief.bedrooms} bedrooms fits ${bedHit.length} native diagram${bedHit.length === 1 ? '' : 's'}`} />
                  : <Advisory tone="limit" label={`${brief.bedrooms} bedrooms is outside the native bedroom ranges`} />}
              </div>
            )}

            <div style={{ marginTop: 16, borderTop: '1px solid var(--rule)', paddingTop: 12 }}>
              <Eyebrow style={{ marginBottom: 8 }}>
                {silent.length} field{silent.length === 1 ? '' : 's'} unstated
              </Eyebrow>
              <p style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)', margin: 0 }}>
                {silent.length
                  ? `Left blank — ${silent.join(', ')} — each becomes a composer decision, reported in the
                     decision log. An assumption, not a fact.`
                  : 'Everything the composer reads is stated.'}
              </p>
            </div>

            <div style={{ marginTop: 14, border: '1px solid var(--rule)', padding: '9px 11px',
              backgroundImage: 'var(--hatch-45)' }}>
              <span style={{ background: 'var(--paper)', display: 'inline-block', padding: '2px 6px' }}>
                <Eyebrow as="span" tone="quiet">conflict set · on the bench, not here</Eyebrow>
              </span>
              <p style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--ink-3)',
                margin: '6px 0 0', background: 'var(--paper)', padding: '2px 6px' }}>
                The CP-SAT solver landed (WP-2.3): where a plan&rsquo;s declared facts cannot all hold,
                it names the minimal set that conflicts. It proves a PLAN, though, not a brief — so the
                naming happens on the Plan Workbench, under <em>prove placement</em>, once a candidate
                exists. The feasibility note above this stays what it says it is: advisory arithmetic on
                area and lot, and never a proof.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
