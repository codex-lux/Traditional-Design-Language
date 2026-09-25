/* Surface ⑤ — Brief Intake. Captures what the composer needs and makes the SILENCES
   visible before they become assumptions: every field left blank is named as a
   decision the composer will take and report. The household stays prose — it is the
   most design-relevant sentence in the file. Feasibility is advisory, computed live,
   and never implies feasibility was proved (the conflict-set display waits on WP-2.3).

   WP-14.10 (PRD §E, §F.4, §G.1): step one of the house journey, which used to break. The budget
   tiers are the brief schema's own enum, read from `GET /api/schema/brief` -- three of the four
   this form offered were off that list and refused the whole brief at compose. The style is
   chosen with the `StylePicker` every other surface uses, and is never a constant here: it
   arrives from `?style=`, from the picker, or from the reader's own draft. `?example=<name>`
   loads a shipped brief by name. Compose is a real button. And the compose stream is handed
   `journey/sessionWrites.js`'s one handler set, the same the Candidate Set hands its own, so a
   failed job is recorded where the journey reads it. */
import React from 'react';
import { api, jobEvents } from '../api/client.js';
import { useStyles } from '../api/useStyles.js';
import { session } from '../state/session.js';
import { nav } from '../state/nav.js';
import { formatHash } from '../router.js';
import { errorText } from '../sheet/refusal.js';
import { composeStart, composeHandlers } from '../journey/sessionWrites.js';
import { briefFrom, budgetTiers, offSchemaTier, exampleId, briefReady } from '../journey/briefForm.js';
import { StylePicker } from '../components/StylePicker.jsx';
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
  const place = React.useSyncExternalStore(nav.subscribe, nav.get);
  // merge over defaults: a brief persisted by an older shape must never crash the form
  const [brief, setBrief] = React.useState(() => briefFrom(s.brief));
  /* One list, one order — the shared hook, not a fourth private copy. Three surfaces kept
     calling api.styles({limit: 200}) sorted by id while useStyles asked for 250 sorted by
     name: two cache entries, two round trips and two orderings of the same 164 styles,
     depending which surface you were standing on. The hook's own header claimed it had
     replaced six surfaces; it had replaced three. Found by an adversarial audit. */
  const { styles: styleRecords } = useStyles();
  // a style is shown by its NAME; the id is what the brief carries
  const styleName = (id) => (styleRecords.find((r) => r.id === id) || {}).name || id;
  const [partis, setPartis] = React.useState(null);
  const [rooms, setRooms] = React.useState([]);
  const [composing, setComposing] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [schema, setSchema] = React.useState({ state: 'loading' });
  const [examples, setExamples] = React.useState([]);
  const [exampleError, setExampleError] = React.useState(null);
  const unsubRef = React.useRef(null);

  /* Close the stream when this surface goes away. compose() calls go('candidates'), which
     now UNMOUNTS Brief Intake — so the ref holding the only handle on the EventSource was
     garbage and the connection could never be closed. Each compose-and-return leaked one
     open stream, and browsers allow six per origin, after which every other fetch in the app
     stalls. The in-mount guard below only ever worked within a single mount, and the
     component no longer survives one compose. Found by an adversarial audit. */
  React.useEffect(() => () => { if (unsubRef.current) unsubRef.current(); }, []);

  React.useEffect(() => {
    api.rooms({ limit: 60 }).then((r) => setRooms((r.results || r.rooms || []).map((x) => x.id)));
  }, []);
  React.useEffect(() => {
    if (!brief.style) { setPartis(null); return; }
    api.partis({ style: brief.style }).then(setPartis).catch(() => setPartis(null));
  }, [brief.style]);

  /* THE SCHEMA SAYS WHAT A BUDGET TIER IS, and names the shipped example briefs. Each example is
     then read once for its own `name`, because a reader is offered a brief by what it is called
     and the schema payload carries file names only. An example that cannot be read is offered by
     its id rather than dropped. */
  React.useEffect(() => {
    let live = true;
    api.briefSchema().then((payload) => {
      if (!live) return;
      setSchema({ state: 'ready', tiers: budgetTiers(payload) });
      const ids = (Array.isArray(payload && payload.examples) ? payload.examples : [])
        .map(exampleId).filter(Boolean);
      Promise.all(ids.map((id) => api.exampleBrief(id)
        .then((rec) => ({ id, name: (rec && typeof rec.name === 'string' && rec.name) || null }))
        .catch(() => ({ id, name: null }))))
        .then((xs) => { if (live) setExamples(xs); });
    }).catch((e) => { if (live) setSchema({ state: 'failed', reason: errorText(e) }); });
    return () => { live = false; };
  }, []);

  /* `?style=` SEEDS THE BRIEF (PRD §E). A style arriving in the address is the reader's, and it
     is applied when the ADDRESS changes -- not whenever the two differ, which would undo every
     pick the reader makes in the picker below while the address still names the old one. */
  const urlStyle = place.selection.style || null;
  React.useEffect(() => {
    if (urlStyle) setBrief((b) => (b.style === urlStyle ? b : { ...b, style: urlStyle }));
  }, [urlStyle]);

  /* `?example=<name>` LOADS A SHIPPED BRIEF, once. The parameter is an act rather than a place --
     once loaded the brief is the reader's to edit -- so it leaves the address when it has done
     its work, and a refresh keeps the edits rather than loading the example over them. The
     address then names the example's style, so it and the form agree. */
  const urlExample = place.params.example || null;
  React.useEffect(() => {
    if (!urlExample) return undefined;
    let live = true;
    setExampleError(null);
    api.exampleBrief(urlExample).then((rec) => {
      if (!live) return;
      setBrief(briefFrom(rec));
      nav.select({ style: (rec && rec.style) || null }, { replace: true });
      nav.setParams({ example: null });
    }).catch((e) => { if (live) setExampleError({ id: urlExample, reason: errorText(e) }); });
    return () => { live = false; };
  }, [urlExample]);

  // the picker writes the address too, so what the address says and what the form shows agree
  const pickStyle = (v) => {
    setBrief((b) => ({ ...b, style: v || '' }));
    nav.select({ style: v || null }, { replace: true });
  };
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
      /* The compose is accepted, so everything the last one said is cleared at once -- result,
         progress, a recorded failure -- and the new job named (PRD §G.1). Written AFTER the
         server accepts rather than before, so a brief the schema refuses leaves the candidates
         the last brief produced standing, which is what they still are. */
      session.set(composeStart(job_id));
      if (unsubRef.current) unsubRef.current();   // a superseded compose drops its stream
      // The one handler set (journey/sessionWrites.js): the session is told every event, a
      // failure included; what follows each is this form's own spinner and nothing more. No
      // navigation here: yanking the user to the Candidate Set minutes later, from wherever
      // they are, is worse than letting the rail chip or the nav take them — the immediate
      // go() below already lands them there once.
      unsubRef.current = jobEvents(job_id, composeHandlers(session, job_id, {
        done: () => setComposing(false),
        error: (d) => { setError(d && d.error); setComposing(false); },
      }));
      go('candidates');
    } catch (e) {
      setError(e.body?.detail?.detail || e.body?.detail?.error || e.message);
      setComposing(false);
    }
  }

  const ready = briefReady(brief);
  const tiers = schema.state === 'ready' ? schema.tiers : null;
  const offTier = offSchemaTier(tiers, brief.context.budget_tier);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip right={
        /* An act, so a button: not a Chip, which is a filter and announces itself as a toggle.
           Disabled until the brief states the two fields its schema requires -- the same test
           the journey's brief step makes -- and the strip beside it says which two. */
        <button type="button" data-compose="" onClick={compose} disabled={composing || !ready}
          aria-busy={composing || undefined}
          style={{ font: 'var(--type-data-s)', padding: '3px 10px', whiteSpace: 'nowrap',
            border: '1px solid ' + (composing || !ready ? 'var(--rule)' : 'var(--gilt-deep)'),
            color: composing || !ready ? 'var(--text-disabled)' : 'var(--gilt-deep)',
            background: 'transparent', cursor: composing || !ready ? 'default' : 'pointer' }}>
          {composing ? 'composing…' : `compose ${brief.candidates || 4} candidates`}
        </button>
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
        {exampleError && (
          <div data-example-error={exampleError.id}
            style={{ border: '1px solid var(--sev-serious)', padding: '10px 12px', marginBottom: 16,
              font: 'var(--fw-reg) 13px/1.5 var(--body)', color: 'var(--ink)' }}>
            The example brief <code>{exampleError.id}</code> could not be read: {exampleError.reason}
          </div>
        )}

        <div style={{ display: 'flex', gap: 28, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          {/* the brief */}
          <div style={{ flex: '1 1 420px', minWidth: 380, maxWidth: 560 }}>
            <Eyebrow style={{ marginBottom: 12 }}>the brief</Eyebrow>
            {examples.length > 0 && (
              <p data-example-briefs="" style={{ font: 'var(--fw-reg) 13px/1.5 var(--body)', color: 'var(--ink-2)',
                margin: '-4px 0 14px' }}>
                or start from an example:{' '}
                {examples.map((x, i) => (
                  <React.Fragment key={x.id}>
                    {i > 0 && ' · '}
                    <a href={formatHash('brief', {}, { example: x.id })} data-example-brief={x.id}>
                      {x.name || <code>{x.id}</code>}
                    </a>
                  </React.Fragment>
                ))}
              </p>
            )}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div>
                <span style={label}>name</span>
                <input style={input} value={brief.name}
                  onChange={(e) => { set('name', e.target.value); set('id', e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, '-') || 'new-brief'); }} />
              </div>
              <div>
                <span style={label}>style · required</span>
                <StylePicker value={brief.style} onChange={pickStyle} label="style" width={232} />
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
                {/* The schema's own enum and nothing else. A tier an older draft carries that the
                    schema does not admit is shown as what it is -- the server would refuse it --
                    rather than dropped from the reader's brief without a word. */}
                <select style={input} data-field="budget_tier" value={brief.context.budget_tier ?? ''}
                  onChange={(e) => setCtx('budget_tier', e.target.value || null)}>
                  <option value="">unstated</option>
                  {(tiers || []).map((b) => <option key={b} value={b} data-tier={b}>{b}</option>)}
                  {offTier && <option value={offTier} data-off-schema={offTier}>{offTier} — not in the brief schema</option>}
                </select>
                {schema.state === 'failed' && (
                  <span data-tiers-unread="" style={{ display: 'block', font: 'var(--type-data-s)', color: 'var(--ink-2)', marginTop: 4 }}>
                    the tiers could not be read: {schema.reason}
                  </span>
                )}
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
                <JudgmentMark state="unjudged" label="native partis unknown"
                  reason={brief.style ? 'reading the corpus…' : 'no style is chosen yet'} />
              ) : native.length === 0 ? (
                <Advisory tone="limit"
                  label={`${styleName(brief.style)} has no native parti — the composer will borrow diagrams`}
                  detail="Three of the corpus's 132 styles and variants have none — egyptian-revival, new-urbanist-traditional and tuscan-vernacular — and every candidate here will carry the NOT-native label. This is one of the three, not the norm: WP-4.5 took native coverage from 93 uncovered to 0, and this panel claimed the pre-WP-4.5 figure until 26 Aug 2026." />
              ) : (
                <Advisory
                  label={`${native.length} parti${native.length === 1 ? '' : 's'} native to ${styleName(brief.style)}`}
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
