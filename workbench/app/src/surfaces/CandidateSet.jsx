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
import { session } from '../state/session.js';
import { planDoc } from '../state/planDoc.js';
import { CandidateColumn } from '../components/CandidateColumn.jsx';
import { RefusalCard } from '../components/RefusalCard.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { nav } from '../state/nav.js';
import { Spotlight } from '../components/Spotlight.jsx';
import { FilterStrip, Chip, ChipGroup, ActionChip } from '../Chrome.jsx';
import { ORDERS, order, isNative } from '../candidateOrder.js';
import { revisedLine, revisedEventLine } from '../revision.js';

/* `what` — the sentence saying what an axis measures — rides on the RESULT once rather than
   on eight rows per candidate, because it is constant across a run and the MCP tool bills a
   model for the payload. Merged back onto the rows here so the column stays a pure function
   of its own candidate, and defaulted so a result composed before this shipped still renders. */
function adaptCandidate(c, i, nativePartis, axisWhat) {
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
    if (s.jobId && !s.result) {
      api.job(s.jobId).then((j) => {
        if (j.status === 'done') {
          session.set({ result: j.result });
        } else if (j.status === 'error') {
          session.set({ jobId: null });
        } else {
          jobEvents(s.jobId, {
            stage: (d) => session.pushProgress(d),
            candidate: (d) => session.pushProgress(d),
            // WP-9.3: the loop's second word on a candidate. Dropped on the floor since
            // WP-9.2 -- jobEvents subscribes only to the names it is handed.
            revised: (d) => session.pushProgress({ ...d, revised: true }),
            done: (d) => session.set({ result: d }),
            error: () => {},
          });
        }
      }).catch((e) => {
        // only forget the job when the server says it no longer exists —
        // a transient network failure must not strand a live job
        if (e.status === 404) session.set({ jobId: null });
      });
    }
  }, [s.jobId]);

  React.useEffect(() => {
    const style = result?.style || s.brief?.style;
    if (!style) return;
    api.partis({ style }).then((r) => setNativePartis(new Set((r.partis || []).map((p) => p.id))))
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
    const n = cands.findIndex((x) => x.id === c.id);
    const plan = await api.candidatePlan(s.jobId, n);
    planDoc.load(plan);
    go('workbench');
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <Spotlight kind="parti" id={selection?.parti}
        note="a plan diagram — the candidates below name the parti each was composed from"
        onDismiss={() => nav.select({ parti: null })} />
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
            <Eyebrow>brief · {result.brief}</Eyebrow>
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
              <button type="button" onClick={() => openInWorkbench(c)}
                style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)', marginTop: 14 }}>
                open in the workbench
              </button>
            </CandidateColumn>
          ))}
        </div>

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
