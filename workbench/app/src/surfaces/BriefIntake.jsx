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
   failed job is recorded where the journey reads it.

   WP-14.25 (PRD §C.5, ruled 25 Sep 2026): A BRIEF MAY NAME A PARTI, AND THE FORM CAN SAY SO NOW.
   The composer guarantees a named parti a place among the candidates (WP-14.19 built that half),
   and this form carries the name: a select listing the style's own plan types grouped by the
   nativity the server STATES -- native, lineage -- each group worded by its glossary record, and
   borrowed diagrams only behind an explicit "include borrowed", which asks the same route with
   `include_borrowed`. `?parti=` seeds it, as `?style=` seeds the style, so a plan type read on a
   dossier starts its own brief. The composer refuses an unknown parti, or one the brief's own
   massing contradicts, BY NAME and before any job starts; the form shows that refusal in its own
   words and decides nothing about it.
   THE FEASIBILITY PANEL READ EVERY LISTED PARTI AS NATIVE. It took `/api/partis`'s whole list as
   "native", right while the list held native partis alone and wrong from the day WP-14.19 listed
   lineage ones beside them: the three styles its "no native parti" advisory named in its own detail
   text now list lineage partis, so the advisory was unreachable for all three, and its count called
   lineage partis "native to" the style. It reads the served nativity now, and says each group by
   its record. And the list's LOADING state is no longer a `JudgmentMark`: a request in flight is
   not a verdict on anything, so it is `aria-busy` and nothing else until a record words it. */
import React from 'react';
import { api, jobEvents } from '../api/client.js';
import { useStyles } from '../api/useStyles.js';
import { useGlossary } from '../api/useGlossary.js';
import { session } from '../state/session.js';
import { nav } from '../state/nav.js';
import { formatHash } from '../router.js';
import { errorText } from '../sheet/refusal.js';
import { composeStart, composeHandlers } from '../journey/sessionWrites.js';
import {
  briefFrom, budgetTiers, offSchemaTier, exampleId, briefReady, composeRequest, partiOptions,
  nativityOfParti,
} from '../journey/briefForm.js';
import { NATIVITY_TERMS } from '../candidateOrder.js';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { wordOf, noGlossary } from '../glossary/termView.js';
import { StylePicker } from '../components/StylePicker.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { JudgmentMark } from '../components/JudgmentMark.jsx';
import { MarkGlyph } from '../components/MarkGlyph.jsx';
import { Term } from '../components/Term.jsx';
import { FilterStrip, Chip } from '../Chrome.jsx';

const COMPASS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];

/* Including borrowed diagrams WIDENS the list the select offers, so it is a view of the place and
   rides in the address (`useFilters.js`), never in a private `useState`. */
const BRIEF_SPEC = { borrowed: { widens: true, type: 'bool' } };

/* One read of `/api/partis` for a style, in three states and never a fourth: `loading` while the
   request is out, `ready` with the payload, `failed` with the server's own words. A failed read is
   said; it is not an empty list, which would read as a style with no plan types. */
function usePartis(style, includeBorrowed) {
  const [state, setState] = React.useState({ state: 'idle' });
  React.useEffect(() => {
    if (!style) { setState({ state: 'idle' }); return undefined; }
    let live = true;
    setState({ state: 'loading' });
    api.partis(includeBorrowed ? { style, include_borrowed: true } : { style })
      .then((payload) => { if (live) setState({ state: 'ready', payload }); })
      .catch((e) => { if (live) setState({ state: 'failed', reason: errorText(e) }); });
    return () => { live = false; };
  }, [style, includeBorrowed]);
  return state;
}

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
  const filters = useSurfaceFilters(BRIEF_SPEC);
  const includeBorrowed = !!filters.values.borrowed;
  // the style's own plan types, and the borrowed ones only where the reader asked for them
  const own = usePartis(brief.style, false);
  const wide = usePartis(includeBorrowed ? brief.style : null, true);
  const glossary = useGlossary();
  // an optgroup label is a string, so a record's word is read as one -- the record's own `term`
  const word = (id) => (glossary.status === 'ready' ? wordOf(glossary.lookup, id)
    : glossary.status === 'failed' ? noGlossary(id) : '…');
  const partiLabel = React.useId();
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

  /* `?parti=` SEEDS THE BRIEF'S PARTI (WP-14.25), on the same rule: applied when the address
     changes, so a plan type's "start a brief" link arrives holding it and a pick in the select
     below is not undone while the address still names the old one. `parti` is a selection key
     the router already carries (`router.js` SELECTION_KEYS); this file adds no route. */
  const urlParti = place.selection.parti || null;
  React.useEffect(() => {
    if (urlParti) setBrief((b) => (b.parti === urlParti ? b : { ...b, parti: urlParti }));
  }, [urlParti]);

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
      // the address names what the loaded brief names -- its style, and its parti or none
      nav.select({ style: (rec && rec.style) || null, parti: (rec && rec.parti) || null }, { replace: true });
      nav.setParams({ example: null });
    }).catch((e) => { if (live) setExampleError({ id: urlExample, reason: errorText(e) }); });
    return () => { live = false; };
  }, [urlExample]);

  // the picker writes the address too, so what the address says and what the form shows agree
  const pickStyle = (v) => {
    setBrief((b) => ({ ...b, style: v || '' }));
    nav.select({ style: v || null }, { replace: true });
  };
  const pickParti = (v) => {
    setBrief((b) => ({ ...b, parti: v || '' }));
    nav.select({ parti: v || null }, { replace: true });
  };
  React.useEffect(() => { session.set({ brief }); }, [brief]);

  const set = (k, v) => setBrief((b) => ({ ...b, [k]: v }));
  const setCtx = (k, v) => setBrief((b) => ({ ...b, context: { ...b.context, [k]: v } }));

  /* WHAT THE SELECT OFFERS, grouped by the nativity the server stated (`journey/briefForm.js`),
     with the borrowed rows only from the list asked for them. */
  const options = partiOptions(own.state === 'ready' ? own.payload : null,
    includeBorrowed && wide.state === 'ready' ? wide.payload : null, brief.parti);
  const chosenNativity = brief.parti ? nativityOfParti(options, brief.parti) : null;

  // Feasibility, all advisory. The style's OWN plan types -- native and lineage, by the nativity
  // the server stated -- and never the whole list read as native, which is what this used to do.
  const ownGroups = partiOptions(own.state === 'ready' ? own.payload : null, null, null).groups;
  const ownIds = new Set(ownGroups.flatMap((g) => g.rows.map((r) => r.id)));
  const ownRows = (own.state === 'ready' && Array.isArray(own.payload?.partis) ? own.payload.partis : [])
    .filter((p) => ownIds.has(p.id));
  const areaHit = ownRows.filter((p) => p.area_range_sf
    && brief.target_area_sf >= p.area_range_sf[0] && brief.target_area_sf <= p.area_range_sf[1]);
  const bedHit = ownRows.filter((p) => p.bedroom_range
    && brief.bedrooms >= p.bedroom_range[0] && brief.bedrooms <= p.bedroom_range[1]);
  const silent = [
    !brief.context.lot_width_ft && 'lot width', !brief.context.climate_zone && 'climate zone',
    !brief.context.entrance_faces && 'entrance orientation', !brief.storeys && 'storeys',
    !brief.massing && 'massing', !brief.context.budget_tier && 'budget tier',
  ].filter(Boolean);

  async function compose() {
    setError(null);
    setComposing(true);
    /* The brief the form posts is `journey/briefForm.js`'s `composeRequest` -- blanks dropped, a
       count that is not one or more left to the client's own default, and the `parti` the reader
       named kept (WP-14.25). It lived here as an inline expression with no test until then. */
    const req = composeRequest(brief);
    try {
      const { job_id } = await api.compose(req.brief, req.candidates ?? undefined);
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
          /* The server's own words, never ours: a brief naming a parti nobody holds, or one its own
             massing contradicts, is refused by the composer by name before any job starts. */
          <div data-brief-refused="" role="alert"
            style={{ border: '1px solid var(--sev-serious)', padding: '10px 12px', marginBottom: 16,
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

            {/* THE PARTI (WP-14.25). The style's own plan types, grouped by the nativity the server
                stated and labelled by each nativity's record; borrowed diagrams only when the reader
                includes them. Unstated, the composer chooses every diagram itself. A parti the brief
                names that no group here holds is shown as itself rather than dropped. */}
            <div style={{ marginTop: 16 }} data-parti-field=""
              aria-busy={own.state === 'loading' || (includeBorrowed && wide.state === 'loading') ? 'true' : undefined}>
              <span id={partiLabel} style={label}><Term id="parti" /></span>
              <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                <select style={{ ...input, width: 300 }} data-field="parti" aria-labelledby={partiLabel}
                  value={brief.parti || ''} disabled={!brief.style}
                  onChange={(e) => pickParti(e.target.value)}>
                  <option value="">unstated</option>
                  {options.groups.map((g) => (
                    <optgroup key={g.nativity} label={word(g.termId)} data-nativity={g.nativity}>
                      {g.rows.map((r) => (
                        <option key={r.id} value={r.id} data-parti={r.id} data-nativity={g.nativity}>{r.name}</option>
                      ))}
                    </optgroup>
                  ))}
                  {options.offList && <option value={options.offList} data-off-list={options.offList}>{options.offList}</option>}
                </select>
                {chosenNativity && (
                  <span data-parti-nativity={chosenNativity}><Term id={NATIVITY_TERMS[chosenNativity]} /></span>
                )}
                <Chip on={includeBorrowed} onClick={() => filters.set('borrowed', !includeBorrowed)}>
                  include borrowed
                </Chip>
              </div>
              {includeBorrowed && wide.state === 'failed' && (
                <span data-borrowed-unread="" style={{ display: 'block', font: 'var(--type-data-s)', color: 'var(--ink-2)', marginTop: 4 }}>
                  the borrowed plan types could not be read: {wide.reason}
                </span>
              )}
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

            {/* The style's plan types, BY THE NATIVITY THE SERVER STATED (WP-14.25). A request in
                flight is not a verdict, so the loading state is `aria-busy` and draws no square:
                since WP-14.29 it says its word, the loading mark's own record, and nothing else.
                The one JudgmentMark left is the real could-not-evaluate, with no style to read. */}
            <div style={{ marginBottom: 12 }} data-plan-types={brief.style ? own.state : 'no-style'}
              aria-busy={own.state === 'loading' ? 'true' : undefined}>
              {!brief.style ? (
                <JudgmentMark state="unjudged" label="native partis unknown" reason="no style is chosen yet" />
              ) : own.state === 'failed' ? (
                <Advisory tone="limit" label={`the plan types could not be read: ${own.reason}`} />
              ) : own.state === 'loading' ? (
                <MarkGlyph token="--mark-loading">
                  {glossary.status === 'ready' ? wordOf(glossary.lookup, 'mark-loading') : ''}
                </MarkGlyph>
              ) : own.state !== 'ready' ? null : ownGroups.length === 0 ? (
                <Advisory tone="limit"
                  label={<>{styleName(brief.style)} has no <Term id="parti-native" /> and no <Term id="parti-lineage" /> — the composer will borrow diagrams</>} />
              ) : (
                ownGroups.map((g) => (
                  <div key={g.nativity} data-nativity-group={g.nativity} style={{ marginBottom: 8 }}>
                    <Advisory label={<><Term id={g.termId} /> · {g.rows.length}</>}
                      detail={g.rows.map((r) => r.name).join(' · ')} />
                  </div>
                ))
              )}
            </div>

            {ownRows.length > 0 && (
              <div style={{ marginBottom: 12 }}>
                {areaHit.length > 0
                  ? <Advisory label={`${brief.target_area_sf?.toLocaleString()} sf sits inside ${areaHit.length} of their area band${areaHit.length === 1 ? '' : 's'}`} />
                  : <Advisory tone="limit"
                      label={`${brief.target_area_sf?.toLocaleString()} sf is outside every one of their area bands`}
                      detail={ownRows.map((p) => `${p.name}: ${p.area_range_sf?.[0]}–${p.area_range_sf?.[1]} sf`).join(' · ')} />}
              </div>
            )}
            {ownRows.length > 0 && brief.bedrooms != null && (
              <div style={{ marginBottom: 12 }}>
                {bedHit.length > 0
                  ? <Advisory label={`${brief.bedrooms} bedrooms fits ${bedHit.length} of these diagram${bedHit.length === 1 ? '' : 's'}`} />
                  : <Advisory tone="limit" label={`${brief.bedrooms} bedrooms is outside the bedroom ranges of every one`} />}
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

            {/* A POINTER, NOT A STATE (WP-14.29, PRD tranche 2 §D). The conflict set lives on the
                bench, so this is a link there and wears no hatch: it wore the falling hatch, which
                means wanted now, and nothing here is wanted -- it is somewhere else. */}
            <div data-conflict-pointer="" style={{ marginTop: 14, border: '1px solid var(--rule)',
              padding: '9px 11px' }}>
              <a href={formatHash('workbench', {}, {})} data-conflict-link="">
                <Eyebrow as="span" tone="quiet">conflict set · on the bench, not here</Eyebrow>
              </a>
              <p style={{ font: 'var(--fw-reg) 12.5px/1.5 var(--body)', color: 'var(--ink-3)',
                margin: '6px 0 0' }}>
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
