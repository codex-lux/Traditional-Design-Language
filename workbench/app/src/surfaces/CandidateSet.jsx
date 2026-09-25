/* Surface ⑥ — the Candidate Set, live. Contrasting plans, ranked and never crowned:
   score and rightness stay on separate axes, trades-away sits beside the score at all
   times, dropped-for-the-lot diagrams get their own honest strip, and the composer's
   decisions render as what they are — assumptions, not facts.

   THE ORDER IS NAMED, ALWAYS. This surface has three of them and the ordinal in each
   column's corner is a position in the one currently chosen, not a verdict. Reading a
   column numbered 1 under "native to the style" as the winner is exactly the misreading
   the header line above the columns exists to prevent — it was possible here for as long
   as the heading said only "ranked", while the numbers under those columns ran 82, 36, 74,
   78. Those four are DEMERIT totals, the superseded lower-is-better quantity: the sequence
   looked random because it was the score order read through a different sort, and the
   largest of them was the worst plan. Nothing renders that quantity now. */
import React from 'react';
import { api, jobEvents } from '../api/client.js';
import { session, recordPlanFrom } from '../state/session.js';
import { composeHandlers, reattach, jobExpired, briefNameOf } from '../journey/sessionWrites.js';
import { JOURNEY_WORDS } from '../journey/journey.js';
import { planDoc } from '../state/planDoc.js';
import { CandidateColumn } from '../components/CandidateColumn.jsx';
import { RefusalCard } from '../components/RefusalCard.jsx';
import { ConflictSet } from '../components/ConflictSet.jsx';
import { readRefusal, refusalHeadline, errorText } from '../sheet/refusal.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { nav } from '../state/nav.js';
import { FilterStrip, Chip, ChipGroup, ActionChip } from '../Chrome.jsx';
import { ORDERS, order, isNative, nativityOf } from '../candidateOrder.js';
import { Term } from '../components/Term.jsx';
import { revisedLine, revisedEventLine } from '../revision.js';

/* `what` — the sentence saying what an axis measures — rides on the RESULT once rather than
   on eight rows per candidate, because it is constant across a run and the MCP tool bills a
   model for the payload. Merged back onto the rows here so the column stays a pure function
   of its own candidate, and defaulted so a result composed before this shipped still renders. */
function adaptCandidate(c, i, nativePartis, axisWhat) {
  // WP-14.25: the served nativity, read off the candidate or the style's own list, never an
  // id's presence in a list -- a lineage parti is on the list and is not native
  const native = isNative(c, nativePartis);
  return {
    id: 'c' + i,
    parti: c.parti, parti_name: c.parti_name,
    score: c.score ?? null,
    score_axes: (c.score_axes || []).map((a) => (
      a.what || !axisWhat?.[a.axis] ? a : { ...a, what: axisWhat[a.axis] })),
    disqualified: !!c.disqualified,
    disqualified_because: c.disqualified_because,
    score_unscored_because: c.score_unscored_because,
    score_weight_evaluated: c.score_weight_evaluated,
    score_weight_unevaluated: c.score_weight_unevaluated,
    demerits: c.demerits,
    counts: c.counts,
    fatal_n: (c.counts && c.counts.fatal) || 0,
    native,
    nativity: nativityOf(c, nativePartis),
    named_by_brief: !!c.named_by_brief,
    why: c.why_this_diagram,
    trades_away: c.trades_away,
    area: `${(c.area_sf || 0).toLocaleString()} sf (${c.area_miss_pct}% off target)`,
    footprint: c.footprint
      ? `${c.footprint.footprint_ft?.[0]} × ${c.footprint.footprint_ft?.[1]} ft`
      : '',
    bays: c.footprint?.bays,
    warnings: (c.footprint?.notes || []),
    worst: c.worst || [],
    plan_rooms: c.plan_rooms,
    /* WP-13.4. A composed candidate whose placement breaks a hard fact of the type carries the
       refusal the composer's own placer wrote; `sheet/refusal.js` reads it and this surface
       derives nothing. Until this, `open in the workbench` loaded such a candidate straight
       onto the bench, where the reader met a blank plate and a status line — the refusal was on
       the record the whole time and no surface had read it. */
    refused: readRefusal(c.refused),
    // WP-9.2/9.3: what the placed revision loop bought on this candidate. `score_before` is
    // the same instrument as `score` (both on the stripped declared record); `rank_before`
    // is the SERVER's order before revision and is labelled as such, because `rank` on
    // this surface is a position in the current order and a bare number would be read as
    // one. null everywhere when the compose ran --no-revise.
    score_before: typeof c.score_before === 'number' ? c.score_before : null,
    counts_before: c.counts_before || null,
    rank_before: c.rank_before ?? null,
    drawn_key_before: c.drawn_key_before || null,
    drawn_key_after: c.drawn_key_after || null,
    revision: c.revision || null,
    revision_skipped: c.revision_skipped || null,
    revised: !!c.revision,
    revisedLine: revisedLine(c),
    raw: c,
  };
}

export function CandidateSet({ onCite, go, selection }) {
  const s = React.useSyncExternalStore(session.subscribe, session.get);
  const [sel, setSel] = React.useState(null);
  React.useEffect(() => {   // a candidate: citation selects its column
    if (selection?.candidate != null) setSel('c' + selection.candidate);
  }, [selection?.candidate]);
  const [sort, setSort] = React.useState('score');
  const [nativePartis, setNativePartis] = React.useState(null);
  const result = s.result;
  const brief = s.brief || result?.brief_record;

  React.useEffect(() => {
    // reattach to a job that survived a refresh — including one still RUNNING
    // (the SSE endpoint supports late attach and closes with a synthetic done)
    if (!s.jobId || s.result) return undefined;
    const jobId = s.jobId;
    let live = true;
    let unsub = null;
    /* WP-14.10 (PRD §G.1). What the server says about the job is written through
       `journey/sessionWrites.js`, the one spelling of every write the house journey reads: a job
       the server gave up on is `failed` with ITS reason, a 404 is `expired`, and the stream is
       handed the same handler set Brief Intake hands its own -- so its `error` records the
       failure instead of going to `() => {}`, which is where it went until this package and why
       the Candidate Set read "composing" for ever over a job that had already failed. */
    api.job(jobId).then((j) => {
      if (!live) return;
      const next = reattach(jobId, j);
      session.set(next.patch);
      if (next.stream) unsub = jobEvents(jobId, composeHandlers(session, jobId));
    }).catch((e) => {
      // only forget the job when the server says it no longer exists —
      // a transient network failure must not strand a live job
      if (live && e.status === 404) session.set(jobExpired(jobId, errorText(e)));
    });
    /* The stream is closed when this surface goes away, for the reason Brief Intake closes its
       own: an EventSource nobody holds cannot be closed, and a reader moving between surfaces
       during a compose opened one per visit against a browser's six per origin. The job keeps
       running on the server and the next visit asks it again. */
    return () => { live = false; if (unsub) unsub(); };
  }, [s.jobId]);

  React.useEffect(() => {
    const style = result?.style || s.brief?.style;
    if (!style) return;
    // id -> the nativity the server states for it (WP-14.25); a Set of ids read every listed
    // parti as native, which was wrong from the day the list held lineage partis beside them
    api.partis({ style }).then((r) => setNativePartis(new Map((r.partis || []).map((p) => [p.id, p.nativity]))))
      .catch(() => setNativePartis(null));
  }, [result?.style, s.brief?.style]);

  if (!result) {
    return (
      <div style={{ padding: '26px 30px', maxWidth: 700 }}>
        <Eyebrow>no candidates yet</Eyebrow>
        <h2 style={{ font: 'var(--fw-reg) var(--fs-d2)/1.1 var(--display)', margin: '8px 0 10px' }}>
          Compose from a brief
        </h2>
        <p style={{ font: 'var(--fw-reg) 14px/1.6 var(--body)', color: 'var(--ink-2)', margin: '0 0 14px' }}>
          The composer returns several contrasting candidates, fatal-free first and then by
          score, and never calls one good. Start at Brief Intake.
        </p>
        {s.jobError && (
          <p data-job-error={s.jobError.state}
            style={{ font: 'var(--fw-reg) 14px/1.6 var(--body)', color: 'var(--ink)', margin: '0 0 14px' }}>
            {JOURNEY_WORDS.candidates[s.jobError.state]}
            {s.jobError.reason && <span style={{ color: 'var(--ink-2)' }}>{JOURNEY_WORDS.separator}{s.jobError.reason}</span>}
          </p>
        )}
        {s.progress.length > 0 && (
          <div style={{ border: '1px solid var(--rule)', padding: '10px 12px', marginBottom: 14 }}>
            <Eyebrow style={{ marginBottom: 6 }}>composing…</Eyebrow>
            {s.progress.map((p, i) => (
              <div key={i} style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', padding: '1px 0' }}>
                {p.stage ? `${p.stage} — ${p.note || ''}`
                  : p.revised ? revisedEventLine(p)
                  /* "tried", not "candidate N": this is the order compose() reached the
                     diagrams in, and nothing is ranked until every one is in. */
                  : `tried ${p.n}: ${p.parti_name} · score `
                    + `${typeof p.score === 'number' ? p.score + '/100' : 'not scored'}`
                    + `${p.disqualified ? ` · DISQUALIFIED, ${p.fatal} fatal` : ''}`}
              </div>
            ))}
          </div>
        )}
        <ActionChip onClick={() => go('brief')}>go to Brief Intake</ActionChip>
      </div>
    );
  }

  const axisWhat = Object.fromEntries(
    ((result.score_model || {}).axes || []).map((a) => [a.axis, a.what]));
  const cands = (result.candidates || []).map((c, i) => adaptCandidate(c, i, nativePartis, axisWhat));
  const chosen = ORDERS[sort] || ORDERS.score;
  const list = cands.slice().sort(order(chosen.cmp));
  const dropped = result.dropped_lot_infeasible || [];
  const askedFor = s.brief?.candidates || 4;

  async function openInWorkbench(c) {
    // A refused candidate is not loaded. The conflict set beside its column says what could not
    // hold; loading it would put a record on the bench that no surface there may draw, which
    // reads as the bench being broken rather than as the candidate being refused.
    if (c.refused) return;
    const n = cands.findIndex((x) => x.id === c.id);
    const plan = await api.candidatePlan(s.jobId, n);
    // where the plan came from, recorded BEFORE it is loaded (PRD §G.1): the job, the index the
    // plan was fetched at, and the brief's name where the draft in hand is the brief it names
    planDoc.load(recordPlanFrom('candidate', plan, { jobId: s.jobId, n, briefName: briefNameOf(result, s.brief) }));
    go('workbench');
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip right={
        <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
          returned {cands.length} of {askedFor} asked for
          {dropped.length ? ` · ${dropped.length} dropped for the lot` : ''}
        </span>
      }>
        <Eyebrow as="span">order by</Eyebrow>
        {/* main's ORDERS table (the orderings are data, not two hardcoded chips) inside
            this branch's radiogroup — they are mutually exclusive, and said to be. */}
        <ChipGroup label="order">
          {Object.entries(ORDERS).map(([k, o]) => (
            <Chip key={k} radio on={sort === k} onClick={() => setSort(k)}>{o.chip}</Chip>
          ))}
        </ChipGroup>
      </FilterStrip>

      <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '18px 22px 30px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between',
          gap: 24, marginBottom: 16 }}>
          <div>
            {/* The brief by NAME where the draft in hand is the brief this result names; the id
                otherwise, in the corpus's mono, because the result carries nothing else. */}
            <Eyebrow>brief · {briefNameOf(result, s.brief)
              || <code style={{ fontFamily: 'var(--mono)', textTransform: 'none' }}>{result.brief}</code>}</Eyebrow>
            <h2 style={{ font: 'var(--fw-reg) var(--fs-d2)/1.1 var(--display)', fontVariationSettings: '"opsz" 72',
              letterSpacing: 'var(--tr-display)', margin: '7px 0 0' }}>
              {cands.length} contrasting plans, <i>ranked</i>
            </h2>
            {/* The order the columns are actually in, said out loud. The ordinal in each
                column is a position in THIS order and nothing more. */}
            <p style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)',
              margin: '8px 0 0', maxWidth: '62ch' }}>
              {chosen.says} Score is out of 100 and higher is better — a weighted composite of
              eight axes, each one the share of its own checks that came back clean, so a
              bigger house is not marked down for being checked more times. Every column shows
              the whole arithmetic.
            </p>
          </div>
          {s.brief?.household && (
            <p style={{ font: 'var(--type-prose)', color: 'var(--ink-2)', margin: 0, maxWidth: '42ch',
              borderLeft: '2px solid var(--rule)', paddingLeft: 14 }}>
              {s.brief.household}
            </p>
          )}
        </div>

        <div style={{ display: 'flex', gap: 12, alignItems: 'stretch' }}>
          {list.map((c, i) => (
            <CandidateColumn key={c.id} candidate={c} rank={i + 1} selected={sel === c.id}
              onSelect={() => setSel(c.id)} style={{ minWidth: 0 }}>
              {/* WP-14.25: the diagram the brief asked for by name, worded by its own record */}
              {c.named_by_brief && (
                <span data-named-by-brief={c.parti} style={{ display: 'block', marginTop: 12 }}>
                  <Term id="named-by-the-brief" />
                </span>
              )}
              {c.refused
                ? <span data-candidate-refused={c.refused.kind}
                    style={{ display: 'block', font: 'var(--type-data-s)', color: 'var(--refusal)',
                      marginTop: 14 }}
                    title={refusalHeadline(c.refused)}>
                    refused — not loadable; the conflict set is below
                  </span>
                : <button type="button" onClick={() => openInWorkbench(c)}
                    style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)', marginTop: 14 }}>
                    open in the workbench
                  </button>}
            </CandidateColumn>
          ))}
        </div>

        {/* WHAT EACH REFUSED CANDIDATE COULD NOT HOLD, in the corpus's own words and in the same
            component the bench and the Drawing Set use — one account of one verdict, wherever a
            reader meets it. A refused candidate is DIFFERENT from a dropped one below: dropped is
            the LOT refusing a diagram before it was placed, refused is the TYPE refusing a
            placement after it was. */}
        {list.filter((c) => c.refused).map((c) => (
          <div key={'r' + c.id} style={{ marginTop: 14 }}>
            <ConflictSet refusal={c.refused} where={`candidate ${c.parti_name || c.parti}`} />
          </div>
        ))}

        {/* WP-14.25: the diagram the brief named and the set does not hold, in the composer's own
            words -- the lot dropped it, or it was never composed. Never a silence: a set lacking
            the diagram the brief asked for would otherwise read as the guarantee kept. */}
        {result.named_parti && result.named_parti.returned === false && (
          <p data-named-parti-missing={result.named_parti.parti} role="note"
            style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)', margin: '16px 0 0',
              borderLeft: '2px solid var(--refusal)', paddingLeft: 12, maxWidth: '74ch' }}>
            <Term id="named-by-the-brief" />{JOURNEY_WORDS.separator}
            <span style={{ fontFamily: 'var(--mono)', fontSize: 12 }}>{result.named_parti.parti}</span>
            {JOURNEY_WORDS.separator}{result.named_parti.why}
          </p>
        )}

        {dropped.length > 0 && (
          <div style={{ marginTop: 16, border: '1px solid var(--rule)', padding: '11px 13px',
            backgroundImage: 'var(--hatch-45)' }}>
            <span style={{ background: 'var(--paper)', display: 'inline-block', padding: '3px 7px' }}>
              <Eyebrow as="span" tone="secondary">
                {dropped.length} diagram{dropped.length === 1 ? '' : 's'} considered and dropped — the lot, not the score
              </Eyebrow>
            </span>
            {dropped.map((d) => (
              <p key={d.parti} style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)',
                margin: '7px 0 0', background: 'var(--paper)', padding: '2px 7px', display: 'inline-block' }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: 12 }}>{d.parti_name}</span> — {d.why}
              </p>
            ))}
          </div>
        )}

        <p style={{ font: 'var(--fw-reg) italic var(--fs-lede)/1.6 var(--body)', fontStyle: 'italic',
          color: 'var(--ink)', margin: '20px 0 0', maxWidth: '74ch', borderTop: '1px solid var(--rule)',
          paddingTop: 16 }}>
          A plan with no fatal findings is not therefore good. The corpus can tell you what is wrong
          and cannot tell you what is alive.
        </p>

        <div style={{ display: 'flex', gap: 26, marginTop: 26, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 460px', minWidth: 420 }}>
            {/* Named, not numbered. The column ordinal is a position in the CURRENT order
                 and `sel` is an index into the SERVER's order; before the three orderings
                 landed those agreed by construction in the default view and they no longer
                 do, so clicking the column marked 2 could open a log headed "candidate 3".
                 A parti name cannot disagree with itself. */}
            <Eyebrow>decision log · {(sel ? cands.find((x) => x.id === sel) : cands[0])?.parti_name || '—'}</Eyebrow>
            <p style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)', margin: '7px 0 10px',
              maxWidth: '64ch' }}>
              What the composer chose where the brief was silent. Read it — those are the assumptions,
              not facts.
            </p>
            {/* OQ 34: the composer now emits `decisions_structured` beside the prose — the same
                lines, each with the kind it gave itself (judgment, refusal, authored, unsolved,
                disclosure, assumption) and a field/chose DERIVED from the sentence. The prose
                statement is still what is read; the structure is what makes a judgment legible
                as a judgment at a glance. Falls back to the plain list, so a record composed
                before this shipped still renders. */}
            {(() => {
              const c = (sel ? cands.find((x) => x.id === sel) : cands[0])?.raw || {};
              const rows = c.decisions_structured
                || (c.decisions || []).map((d) => ({ statement: d, kind: 'assumption' }));
              const TONE = { judgment: 'var(--gilt-deep)', refusal: 'var(--brick)',
                unsolved: 'var(--ink-3)', disclosure: 'var(--sepia)', authored: 'var(--ink-2)',
                // WP-9.2's sixth kind: a move the loop applied, with its basis as `because`
                revision: 'var(--gilt)' };
              return rows.map((d, i) => (
                <div key={i} style={{ margin: '0 0 9px', paddingLeft: 12,
                  borderLeft: `2px solid ${TONE[d.kind] || 'var(--rule-soft)'}` }}>
                  {d.kind && d.kind !== 'assumption' && (
                    <Eyebrow as="span" tone="quiet" style={{ color: TONE[d.kind] }}>{d.kind}</Eyebrow>
                  )}
                  {d.field && (
                    <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)',
                      marginLeft: d.kind && d.kind !== 'assumption' ? 8 : 0 }}>
                      {d.field}{d.chose ? ` · ${d.chose}` : ''}
                    </span>
                  )}
                  <p style={{ font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)',
                    margin: '2px 0 0' }}>{d.statement}</p>
                </div>
              ));
            })()}
          </div>
          <div style={{ flex: '0 1 420px', minWidth: 380 }}>
            <Eyebrow style={{ marginBottom: 9 }}>how to read this</Eyebrow>
            {(result.how_to_read_this || []).map((h, i) => (
              <p key={i} style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)',
                margin: '0 0 8px' }}>{h}</p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
