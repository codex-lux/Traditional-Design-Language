/* Surface ⑦ — the Plan Workbench, live. The drawing with the critique on it.
   The plan record is a document the browser owns; every edit gesture mutates the
   record (never the geometry), a debounced evaluate round-trip re-runs the validator
   and the placement solver together, and findings appear and clear against a diff of
   derived keys. Unjudged is not passed: the could-not-evaluate panel draws from three
   kept-distinct sources and is styled as neither verdict. */
import React from 'react';
import { api } from '../api/client.js';
import { planDoc, mutations } from '../state/planDoc.js';
import { FindingRow } from '../components/FindingRow.jsx';
import { SeverityTally } from '../components/SeverityTally.jsx';
import { JudgmentMark } from '../components/JudgmentMark.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { Sheet } from '../sheet/Sheet.jsx';
import { FilterStrip, Chip } from '../Chrome.jsx';

/* Findings carry no ids; a stable client key makes rows diffable and citable. */
function findingKey(f) {
  const s = `${f.layer}|${f.statement}|${f.room || ''}`;
  let h = 0;
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  return 'f' + (h >>> 0).toString(36);
}

function adaptFinding(f) {
  const isFault = f.layer === 'fault';
  // only offer the assertion where the statement names the other room in the form
  // the resolver can actually parse — a button that no-ops is worse than none
  const assertable = (f.layer === 'adjacency' || f.layer === 'privacy')
    && /adjoins .+?, which it should not/i.test(f.statement)
    ? 'not-visible-from' : null;
  return {
    id: findingKey(f),
    severity: f.severity, layer: f.layer, statement: f.statement,
    at: f.room, why: isFault ? undefined : f.rule, fix: f.fix,
    rule_ref: isFault && f.rule ? 'fault:' + f.rule : undefined,
    assertable, raw: f,
  };
}

export function PlanWorkbench({ onCite, selection, lastEval, setLastEval }) {
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);
  const [level, setLevel] = React.useState(0);
  const [ghost, setGhost] = React.useState(true);
  const [ov, setOv] = React.useState({ daylight: false, wet: false, privacy: false });
  const [sev, setSev] = React.useState(null);
  const [layer, setLayer] = React.useState(null);
  const [room, setRoom] = React.useState(selection?.room || null);
  const [openId, setOpenId] = React.useState(null);
  const [strict, setStrict] = React.useState(false);
  const [seeds, setSeeds] = React.useState(250);
  const [busy, setBusy] = React.useState(false);
  const [styleOptions, setStyleOptions] = React.useState([]);
  const [examples, setExamples] = React.useState([]);
  const [prevKeys, setPrevKeys] = React.useState(null);
  const [evalError, setEvalError] = React.useState(null);
  const evalRef = React.useRef(0);
  const lastFindingsRef = React.useRef(null);   // keys of the last APPLIED evaluation

  React.useEffect(() => {
    api.styles({ limit: 200 }).then((r) => setStyleOptions((r.results || []).map((s) => s.id).sort()));
    api.planSchema().then((r) => setExamples((r.examples || []).map((e) => e.replace(/\.json$/, ''))));
  }, []);
  React.useEffect(() => {
    if (selection?.room) setRoom(selection.room);
    if (selection?.finding) setOpenId(selection.finding);
  }, [selection?.room, selection?.finding]);

  const runEvaluate = React.useCallback((p, opts = {}) => {
    if (!p) return;
    const seq = ++evalRef.current;
    setBusy(true);
    api.evaluate(p, { strict, place: true, candidates: opts.candidates ?? seeds,
      engine: opts.engine })
      .then((res) => {
        if (seq !== evalRef.current) return;
        // updaters stay pure: the previous run's keys live in a ref, and both
        // state sets happen at this level (the seq guard already serializes)
        setPrevKeys(lastFindingsRef.current);
        lastFindingsRef.current = res?.check?.findings
          ? new Set(res.check.findings.map((f) => findingKey(f)))
          : null;
        setEvalError(res?.check?.error || null);
        setLastEval(res);
      })
      .catch((e) => {
        if (seq !== evalRef.current) return;
        // a silent catch would leave the OLD verdict rendered against a NEW
        // record — the one failure mode this product must never have
        setEvalError(e.body?.detail?.error || e.message || 'evaluation failed');
      })
      .finally(() => { if (seq === evalRef.current) setBusy(false); });
  }, [strict, seeds, setLastEval]);

  // debounced re-evaluate on any plan-record change
  React.useEffect(() => {
    if (!plan) return;
    const t = setTimeout(() => runEvaluate(plan), 400);
    return () => clearTimeout(t);
  }, [plan, strict, runEvaluate]);

  if (!plan) {
    return (
      <div style={{ padding: '26px 30px', maxWidth: 720 }}>
        <Eyebrow>no plan on the bench</Eyebrow>
        <h2 style={{ font: 'var(--fw-reg) var(--fs-d2)/1.1 var(--display)', margin: '8px 0 10px' }}>
          Load a plan record
        </h2>
        <p style={{ font: 'var(--fw-reg) 14px/1.6 var(--body)', color: 'var(--ink-2)', margin: '0 0 16px' }}>
          Open one of the corpus's example plans, compose candidates from a brief (⑤ → ⑥),
          or paste a record. The drawing is a render of the record — nothing is drawn that
          is not in it.
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {examples.map((e) => (
            <Chip key={e} onClick={() => api.examplePlan(e).then((p) => planDoc.load(p))}>{e}</Chip>
          ))}
        </div>
        <label style={{ display: 'block', marginTop: 18, font: 'var(--type-data-s)', color: 'var(--ink-3)' }}>
          …or paste a plan record JSON
          <textarea rows={4} style={{ display: 'block', width: '100%', marginTop: 6,
            background: 'var(--paper-mat)', border: '1px solid var(--rule-soft)', color: 'var(--ink)',
            font: 'var(--type-data-s)', padding: 8 }}
            onBlur={(e) => { try { planDoc.load(JSON.parse(e.target.value)); } catch { /* not JSON yet */ } }} />
        </label>
      </div>
    );
  }

  const check = lastEval?.check;
  const placement = lastEval?.placement;
  const findings = (check?.findings || []).map(adaptFinding);
  const counts = check?.counts || {};
  const shown = findings.filter((f) =>
    (!sev || f.severity === sev) && (!layer || f.layer === layer) && (!room || f.at === room));
  const layers = [...new Set(findings.map((f) => f.layer))];
  const byLayer = layers.map((l) => ({ layer: l, rows: shown.filter((f) => f.layer === l) }))
    .filter((g) => g.rows.length);
  const newKeys = prevKeys ? findings.filter((f) => !prevKeys.has(f.id)).length : 0;

  const unjudgedConstraints = findings.filter((f) =>
    f.layer === 'style' && /cannot evaluate|check by hand/i.test(f.statement));
  const faultUnjudged = lastEval?.fault_unjudged || [];
  const cs = check?.constraint_summary;
  const relax = placement?.geometry_report?.relaxations;
  // OQ 54. The search may place a room below the floor of its own catalogue band, charging
  // itself 12 points and winning anyway — and the plan RECORD still declares the full size, so
  // the trade is invisible to every layer of the critic downstream. geometry.py reports it; this
  // is the surface that shows it. The CP engine refuses the trade outright, so proving a
  // placement is the fix as well as the diagnosis.
  const underBand = placement?.geometry_report?.under_band;
  const levelIndices = (plan.levels || []).map((l) => l.index ?? 0);
  const declared = plan.adjacencies || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip right={
        <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>candidates {seeds}</span>
          <input type="range" min="40" max="800" step="40" value={seeds}
            onChange={(e) => setSeeds(+e.target.value)} style={{ width: 84, accentColor: 'var(--gilt-deep)' }} />
          <Chip on={busy} onClick={() => runEvaluate(plan)} title="the solver is a hill-climb; results differ across runs">
            {busy ? 're-solving…' : 're-solve'}
          </Chip>
          <Chip onClick={() => planDoc.undo()} title="undo the last record edit">undo</Chip>
        </span>
      }>
        <Eyebrow as="span">style</Eyebrow>
        <select value={plan.style} onChange={(e) => planDoc.update(mutations.setStyle(e.target.value))}
          title="same plan, different rules — findings appear and clear"
          style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)', background: 'var(--paper-mat)',
            border: '1px solid var(--rule)', padding: '2px 6px', maxWidth: 200 }}>
          {[plan.style, ...styleOptions.filter((s) => s !== plan.style)].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <Eyebrow as="span">level</Eyebrow>
        {levelIndices.map((i) => (
          <Chip key={i} on={level === i} onClick={() => setLevel(i)}>
            {(plan.levels.find((l) => (l.index ?? 0) === i) || {}).name || 'level ' + i}
          </Chip>
        ))}
        <Chip on={ghost} onClick={() => setGhost(!ghost)}>ghost below</Chip>
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <Eyebrow as="span">overlays</Eyebrow>
        <Chip on={ov.daylight} tone="var(--green-deep)" onClick={() => setOv({ ...ov, daylight: !ov.daylight })}>daylight reach</Chip>
        <Chip on={ov.wet} tone="var(--blue-deep)" onClick={() => setOv({ ...ov, wet: !ov.wet })}>wet stacks</Chip>
        <Chip on={ov.privacy} tone="var(--sepia)" onClick={() => setOv({ ...ov, privacy: !ov.privacy })}>privacy gradient</Chip>
        <Chip on={strict} onClick={() => setStrict(!strict)}
          title="the completeness layer: treat absent room types as failures (--strict)">strict</Chip>
        <Chip onClick={() => runEvaluate(plan, { engine: 'cp' })}
          title="WP-2.3: prove the placement with CP-SAT — hard constraints on the record's declared facts, a named conflict set if they cannot all hold. Takes seconds; per-drag re-scores stay on the fast search.">
          prove placement (CP-SAT)</Chip>
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {/* the critique */}
        <div style={{ width: 430, flex: 'none', borderRight: '1px solid var(--rule)', display: 'flex',
          flexDirection: 'column', minHeight: 0 }}>
          <div style={{ padding: '12px 12px 10px', borderBottom: '1px solid var(--rule)' }}>
            <SeverityTally counts={counts} active={sev} onSelect={setSev} />
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginTop: 10 }}>
              {layers.map((l) => {
                const n = findings.filter((f) => f.layer === l).length;
                return <Chip key={l} on={layer === l} onClick={() => setLayer(layer === l ? null : l)}>{l} {n}</Chip>;
              })}
            </div>
            {(room || sev || layer) && (
              <button type="button" onClick={() => { setRoom(null); setSev(null); setLayer(null); }}
                style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)', marginTop: 9 }}>clear filters</button>
            )}
            {newKeys > 0 && (
              <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', marginTop: 7 }}>
                {newKeys} finding{newKeys === 1 ? '' : 's'} new since the last evaluation
              </div>
            )}
          </div>

          <div style={{ flex: 1, overflow: 'auto', minHeight: 0, opacity: busy ? 0.6 : 1,
            transition: 'opacity .2s' }}>
            {byLayer.map((g) => (
              <div key={g.layer}>
                <div style={{ position: 'sticky', top: 0, zIndex: 1, background: 'var(--paper-deep)',
                  borderBottom: '1px solid var(--rule)', padding: '5px 10px', display: 'flex',
                  justifyContent: 'space-between' }}>
                  <Eyebrow tone="secondary" as="span">{g.layer}</Eyebrow>
                  <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>{g.rows.length}</span>
                </div>
                {g.rows.map((f) => (
                  <FindingRow key={f.id} finding={f} dense expanded={openId === f.id}
                    onToggle={() => setOpenId(openId === f.id ? null : f.id)}
                    onLocate={f.at ? () => setRoom(f.at) : undefined}
                    onCite={f.rule_ref ? () => onCite && onCite(f.rule_ref) : undefined}
                    onAssert={f.assertable && f.at ? () => {
                      // The statement names the other room by display NAME; the record
                      // wants its id. Resolve by matching names across the record's own
                      // rooms — and never assert at all if no room matches.
                      const m = /adjoins (.+?), which/.exec(f.statement);
                      const otherName = m && m[1].trim().toLowerCase();
                      let otherId = null;
                      for (const lv of plan.levels || []) {
                        for (const r of lv.rooms || []) {
                          if ((r.name || '').toLowerCase() === otherName) otherId = r.id;
                        }
                      }
                      if (!otherId || otherId === f.at) return;
                      planDoc.update(mutations.assertRelation(f.at, otherId, 'not-visible-from'));
                    } : undefined} />
                ))}
              </div>
            ))}

            <div style={{ borderTop: '2px solid var(--rule)', padding: '12px 12px 16px' }}>
              <Eyebrow style={{ marginBottom: 9 }}>
                could not evaluate
                {cs ? ` · ${cs.unjudged} of this style's constraints` : ''}
                {faultUnjudged.length ? ` · ${faultUnjudged.length} faults` : ''}
              </Eyebrow>
              {unjudgedConstraints.map((u) => (
                <div key={u.id} style={{ marginBottom: 10 }}>
                  <JudgmentMark state="unjudged" label={u.statement} reason={u.why || 'scope: judgment'} />
                </div>
              ))}
              {faultUnjudged.slice(0, 8).map((u) => (
                <div key={u.fault} style={{ marginBottom: 10 }}>
                  <JudgmentMark state="unjudged" label={u.name}
                    reason={'needs ' + (u.needs || []).join(', ')} />
                </div>
              ))}
              {faultUnjudged.length > 8 && (
                <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', marginBottom: 8 }}>
                  and {faultUnjudged.length - 8} more faults beyond evaluation on this record
                </div>
              )}
              <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)', margin: '4px 0 0' }}>
                Unjudged is not passed. 295 of the corpus's 660 style constraints carry no test at all.
              </p>
            </div>

            {declared.length > 0 && (
              <div style={{ borderTop: '1px solid var(--rule)', padding: '12px', background: 'var(--paper-mat)' }}>
                <Eyebrow style={{ marginBottom: 8 }}>you asserted</Eyebrow>
                {declared.map((a, i) => (
                  <p key={i} style={{ fontFamily: 'var(--serif)', fontStyle: 'italic', fontSize: 15,
                    lineHeight: 1.5, color: 'var(--ink-2)', margin: '0 0 6px', display: 'flex', gap: 8 }}>
                    <span style={{ flex: 1 }}>{a.a} — {a.relation} — {a.b}</span>
                    <button type="button" onClick={() => planDoc.update(mutations.revokeRelation(i))}
                      style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)' }}>revoke</button>
                  </p>
                ))}
                <p style={{ font: 'var(--fw-reg) 12px/1.5 var(--body)', color: 'var(--ink-4)', margin: 0 }}>
                  An assertion clears a finding only if the validator clears it.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* the sheet */}
        <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '20px 26px 30px',
          background: 'var(--paper)' }}>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between',
            gap: 20, marginBottom: 14 }}>
            <div>
              <Eyebrow>
                {(plan.levels.find((l) => (l.index ?? 0) === level) || {}).name || 'level ' + level}
                {' '}· both levels solved together
              </Eyebrow>
              <div style={{ font: 'var(--type-data-s)',
                color: evalError ? 'var(--sev-serious)' : 'var(--ink-2)', marginTop: 6 }}>
                {evalError
                  ? `not evaluated: ${evalError} — what is shown below is the LAST successful evaluation`
                  : relax
                    ? `${relax.count} cut(s) off the bay line` +
                      (relax.count ? ` · worst ${relax.max_off_grid_ft} ft — each is a joist run that does not land on a bearing wall` : '')
                    : lastEval?.placement_error
                      ? 'placement failed: ' + lastEval.placement_error
                      : 'placing…'}
              </div>
            </div>
            {check && (
              <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
                check {lastEval.timing_ms?.check} ms · place {lastEval.timing_ms?.place ?? '—'} ms
              </div>
            )}
          </div>

          {/* WP-2.3: the solver's named conflict set. When CP-SAT proves the
              record's declared facts cannot all hold, the drawing below is the
              labelled least-bad relaxation and this panel says exactly which
              requirements conflict — the thing a plan-development partner most
              needs to hear early, stated, never silently softened. */}
          {placement?.geometry_report?.infeasible && (
            <div style={{ maxWidth: 1000, border: '1px solid var(--sev-serious)',
              padding: '10px 14px', margin: '0 0 14px' }}>
              <Eyebrow tone="secondary">
                infeasible as declared — proven ({placement.geometry_report.infeasible.conflicts.length} conflict{placement.geometry_report.infeasible.conflicts.length === 1 ? '' : 's'})
              </Eyebrow>
              <ul style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-2)',
                margin: '6px 0 0', paddingLeft: 18 }}>
                {placement.geometry_report.infeasible.conflicts.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
              <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', margin: '8px 0 0' }}>
                {placement.geometry_report.infeasible.note} The drawing below is the
                heuristic's least-bad relaxation, labelled — not a solution.
              </p>
            </div>
          )}
          {underBand?.count > 0 && (
            <div style={{ maxWidth: 1000, border: '1px solid var(--rule)',
              borderLeft: '3px solid var(--sepia)', padding: '10px 14px', margin: '0 0 14px' }}>
              <Eyebrow tone="secondary">
                {underBand.count} room{underBand.count === 1 ? '' : 's'} placed below
                {' '}its own band
              </Eyebrow>
              <ul style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-2)',
                margin: '6px 0 0', paddingLeft: 18 }}>
                {underBand.rooms.map((r) => (
                  <li key={r.room}>
                    <strong>{r.name}</strong> drawn at {r.placed_sf} sf against the{' '}
                    {r.band_floor_sf} sf floor of the {r.type} band — {r.short_by_pct}% short.
                  </li>
                ))}
              </ul>
              <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', margin: '8px 0 0' }}>
                The record still declares the full size; only the placement is short, and nothing
                downstream reads these coordinates — so without this panel the trade is invisible.
                A room below its band is a defect that survives the life of the building.
                {' '}<em>Prove placement</em> refuses the trade outright.
              </p>
            </div>
          )}
          {placement?.geometry_report?.solver?.refinements?.length > 0 && (
            <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', margin: '0 0 10px' }}>
              solver refinements ({placement.geometry_report.solver.refinements.length}):{' '}
              {placement.geometry_report.solver.refinements.slice(0, 2).join(' · ')}
              {placement.geometry_report.solver.refinements.length > 2 ? ' · …' : ''}
            </p>
          )}
          {placement && (
            <div style={{ maxWidth: 1000, opacity: busy ? 0.45 : 1, transition: 'opacity .3s' }}>
              <Sheet plan={plan} placement={placement} levelIndex={level}
                overlays={{ ...ov, meta: lastEval?.rooms_meta }}
                ghost={(() => {   // ghost the nearest level BELOW the one in view
                  if (!ghost) return null;
                  const below = levelIndices.filter((i) => i < level);
                  return below.length ? Math.max(...below) : null;
                })()}
                selectedRoom={room}
                onPickRoom={(r) => { setRoom(room === r.id ? null : r.id); setLayer(null); }}
                onResizeRoom={(r, axis, size) => {
                  // The record declares width_ft as the SHORT dimension; the placed rect
                  // may have either orientation. Map the dragged axis onto whichever
                  // declared field the solver used for that direction, then re-evaluate.
                  const rec = r.record;
                  const placedX = r.w, placedY = r.h;
                  const xIsWidth = Math.abs((rec.width_ft || 0) - placedX) <=
                                   Math.abs((rec.length_ft || 0) - placedX);
                  const field = axis === 'x'
                    ? (xIsWidth ? 'width_ft' : 'length_ft')
                    : (xIsWidth ? 'length_ft' : 'width_ft');
                  const lvIdx = plan.levels.findIndex((l) => (l.index ?? 0) === level);
                  planDoc.update(mutations.resizeRoom(lvIdx, r.id, { [field]: size }));
                }}
                title={plan.name || plan.id}
                subtitle={((plan.levels.find((l) => (l.index ?? 0) === level) || {}).name
                    || `level ${level}`) + ' plan' + (placement.footprint
                  ? ` · ${placement.footprint.bays} bays of ${placement.footprint.bay_module_ft}′ · clear dimensions`
                  : '')}
                styleName={plan.style} />
            </div>
          )}

          <p style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-3)',
            margin: '16px 0 0', maxWidth: '76ch' }}>
            Each edit re-scores on the fast search, which is a hill-climb and not an optimiser: it is
            seconds-cheap and not deterministic across runs, so nothing it draws asserts that feasibility
            was proved. <em>Prove placement (CP-SAT)</em> above is the act that proves it — hard
            constraints on the record's own declared facts, and a named conflict set above when they
            cannot all hold. The search also trades a room's size away when it must, and says so under
            the drawing rather than silently (OQ 54). A plan with no fatal findings is still not
            therefore good.
          </p>
        </div>
      </div>
    </div>
  );
}
