/* Surface ⑦ — the Plan Workbench, live. The drawing with the critique on it.
   The plan record is a document the browser owns; every edit gesture mutates the
   record (never the geometry), a debounced evaluate round-trip re-runs the validator
   and the placement solver together, and findings appear and clear against a diff of
   derived keys. Unjudged is not passed: the could-not-evaluate panel draws from three
   kept-distinct sources and is styled as neither verdict. */
import React from 'react';
import { api, jobEvents } from '../api/client.js';
import { useStyles } from '../api/useStyles.js';
import { planDoc, mutations } from '../state/planDoc.js';
import { FindingRow } from '../components/FindingRow.jsx';
import { SeverityTally } from '../components/SeverityTally.jsx';
import { JudgmentMark } from '../components/JudgmentMark.jsx';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { Sheet } from '../sheet/Sheet.jsx';
import { nav } from '../state/nav.js';
import { Spotlight } from '../components/Spotlight.jsx';
import { FilterStrip, Chip, ChipGroup, ActionChip, FilterGroup } from '../Chrome.jsx';
import { StylePicker } from '../components/StylePicker.jsx';
import { PlateViewer } from '../components/PlateViewer.jsx';
import { PullPane } from '../components/PullPane.jsx';
import { RevisionPanel } from '../components/RevisionPanel.jsx';
import { classesById, engineLabel, classTag, CLASSES } from '../revision.js';

/* Findings carry a server-minted id now (OQ 32) — built from the layer, the room and the rule
   or fault id, which are what a finding is ABOUT. The hash below is the old client-side key and
   survives only as a fallback for a response from a server older than that change. It hashed the
   STATEMENT, so improving the wording of a finding silently broke every open row, every citation
   and every diff: the UI reported one finding cleared and another opened when nothing had changed
   but an adjective. Prefer f.id; never reintroduce the hash as the primary. */
// WHY A COULD-NOT-EVALUATE FAULT COULD NOT BE EVALUATED. Three shapes reach this list and
// only one of them is "a number is missing":
//   needs[]              -- the historical case: name the measurements.
//   errors[]             -- a test raised; say so, never render it as a missing number.
//   exception_unjudged   -- WP-8.4: this style carries an exception whose own bounds_test would
//                           REPLACE the fault's primary test, and whose condition could not be
//                           resolved, so the two rules disagree about this house and nobody can
//                           say which governs. `needs` is EMPTY by construction here, and the
//                           bench used to render the bare word "needs" for it -- an unjudged
//                           whose reason is on the record and not on the screen, which reads to
//                           the user exactly like a bug in the bench.
function unjudgedReason(u) {
  const x = u.exception_unjudged
  if (x) {
    return 'the ' + (x.style || 'style') + ' exception could not be judged (' +
      (x.because || 'no reason given') + '), and its own test says ' +
      (x.under_the_exception || '?') + ' where the general rule says ' +
      (x.under_the_general_rule || '?')
  }
  if (u.errors && u.errors.length) return 'a test errored: ' + u.errors.join('; ')
  const n = u.needs || []
  return n.length ? 'needs ' + n.join(', ') : 'no test of this fault could be evaluated'
}

// the analyst's five classes, as the strip names them (the row's tag is the long form)
const CLASS_SHORT = { actionable: 'a move answers', placement: "the engine's",
  critic_suspect: "the critic's own", architect: "the architect's", advisory: 'advisory' };

function findingKey(f) {
  if (f.id) return f.id;
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
    // WP-9.1: every drawn finding carries the engine that placed the house it was read from
    engine: f.engine,
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
  /* One list, one order — the shared hook, not a fourth private copy. Three surfaces kept
     calling api.styles({limit: 200}) sorted by id while useStyles asked for 250 sorted by
     name: two cache entries, two round trips and two orderings of the same 164 styles,
     depending which surface you were standing on. The hook's own header claimed it had
     replaced six surfaces; it had replaced three. Found by an adversarial audit. */
  const { styles: styleRecords } = useStyles();
  const styleOptions = React.useMemo(() => styleRecords.map((s) => s.id), [styleRecords]);
  const [examples, setExamples] = React.useState([]);
  const [prevKeys, setPrevKeys] = React.useState(null);
  const [evalError, setEvalError] = React.useState(null);
  const evalRef = React.useRef(0);
  const lastFindingsRef = React.useRef(null);   // keys of the last APPLIED evaluation
  /* WP-9.3: the analyst and the loop. `assessment` is the last critique, keyed by finding
     id AND by the evaluation it was taken against (appliedSeq): the debounce re-evaluates
     on every record change, and a class that labelled a finding of an EARLIER evaluation
     would be a verdict about a house that is no longer on the sheet. `live` is the
     in-flight revise job's rounds; it is cleared on done, on error, and whenever the plan
     changes underneath it, so the panel is the record's own `revision_report` and undo
     takes it away. */
  const appliedSeqRef = React.useRef(0);
  const [assessment, setAssessment] = React.useState(null);
  const [critiquing, setCritiquing] = React.useState(false);
  const [live, setLive] = React.useState([]);
  const [revising, setRevising] = React.useState(null);      // null | 'submitting' | 'submitted' | 'running'
  const [reviseError, setReviseError] = React.useState(null);
  const reviseUnsub = React.useRef(null);

  React.useEffect(() => {
    api.planSchema().then((r) => setExamples((r.examples || []).map((e) => e.replace(/\.json$/, ''))));
  }, []);
  React.useEffect(() => {
/* The URL owns this, so an ABSENT selection must reset to the default rather than leave the
   last one showing. Guarding the sync with `if (selection?.x)` meant pressing Back to a bare
   #/workbench left the panel displaying the record you had just left — the address bar and the
   screen disagreeing, which is the one thing the router exists to prevent. Found by an
   adversarial audit. */
    setRoom(selection?.room || null);
    setOpenId(selection?.finding || null);
  }, [selection?.room, selection?.finding]);

  // set by a wall drag, read once by the debounce below: it decides which engine the
  // next evaluate asks for, because a gesture cannot wait for a proof
  const draggingRef = React.useRef(false);

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
        appliedSeqRef.current = seq;
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

  /* WP-9.3: the analyst, on demand. Not per edit: evaluate is this server's bound (the
     infrastructure audit), and a classification is asked for the way a proof is. `auto`
     rather than the last evaluation's engine: the route accepts heuristic|cp|auto and the
     placement reports cp-sat, and the solve cache makes the critique's placement the
     sheet's when both asked for auto at the same candidate count. */
  const runCritique = React.useCallback(() => {
    const forSeq = appliedSeqRef.current;
    setCritiquing(true);
    setReviseError(null);
    api.critique(plan, { engine: 'auto', candidates: seeds })
      .then((res) => setAssessment({
        forSeq, byId: classesById(res.assessment), counts: res.counts_by_class || {},
        engine: res.engine?.ran, key: res.key,
        couldNot: res.could_not_evaluate?.findings?.length || 0,
      }))
      .catch((e) => setReviseError('critique: ' + (e.body?.detail?.error || e.message || 'failed')))
      .finally(() => setCritiquing(false));
  }, [plan, seeds]);

  /* The loop, as a job. Two chips, honest about cost: the search (rounds 6, 60 s) and the
     proof-backed loop (rounds 4, 120 s). The revised record comes back STRIPPED of its
     placement and is loaded through planDoc.load -- one undo step -- so the debounce
     re-solves it as it does every load, and the panel says so. If the record changed
     underneath the job, the revision is NOT applied: loading it would overwrite an edit
     the reader made while waiting. */
  const runRevise = React.useCallback((opts) => {
    const submitted = plan;
    setReviseError(null);
    setLive([]);
    setRevising('submitting');
    let polling = null;
    const finish = (job_id) => {
      api.jobPlan(job_id)
        .then((revised) => {
          if (planDoc.get() !== submitted) {
            setReviseError('the record changed while the loop ran — the revision was not applied');
          } else {
            planDoc.load(revised);
          }
        })
        .catch((e) => setReviseError('revise: ' + (e.body?.detail?.error || e.message || 'could not fetch the revised record')))
        .finally(() => { setLive([]); setRevising(null); });
    };
    /* A dropped stream is not a failed job. jobEvents suppresses EventSource's own reconnect
       and reports 'stream closed'; the loop keeps running and its result is held server-side
       for 30 minutes, so the bench POLLS the job until it ends rather than discarding minutes
       of the one worker's time (the session's audit). A page refresh still abandons the job:
       the record-changed check above is object identity and cannot survive one. */
    const pollUntilDone = (job_id) => {
      setRevising('running');
      const tick = () => api.job(job_id).then((j) => {
        if (j.status === 'done') finish(job_id);
        else if (j.status === 'error') { setReviseError('revise: ' + (j.error || 'failed')); setLive([]); setRevising(null); }
        else polling = setTimeout(tick, 3000);
      }).catch((e) => { setReviseError('revise: ' + (e.message || 'lost the job')); setLive([]); setRevising(null); });
      polling = setTimeout(tick, 3000);
    };
    api.revise(plan, { candidates: seeds, ...opts })
      .then(({ job_id }) => {
        setRevising('submitted');
        if (reviseUnsub.current) reviseUnsub.current();
        const unsub = jobEvents(job_id, {
          stage: () => setRevising('running'),
          round: (d) => { setRevising('running'); setLive((l) => [...l, d]); },
          done: () => finish(job_id),
          error: (d) => {
            if (d && d.error === 'stream closed') { pollUntilDone(job_id); return; }
            setReviseError('revise: ' + (d.error || 'failed')); setLive([]); setRevising(null);
          },
        });
        reviseUnsub.current = () => { unsub(); if (polling) clearTimeout(polling); };
      })
      .catch((e) => { setReviseError('revise: ' + (e.body?.detail?.error || e.message || 'failed')); setRevising(null); });
  }, [plan, seeds]);
  React.useEffect(() => () => { if (reviseUnsub.current) reviseUnsub.current(); }, []);
  // the plan changed underneath the panel (an edit, an undo, a load): the live rounds are
  // no longer about this record
  React.useEffect(() => { setLive([]); }, [plan]);

  /* Debounced re-evaluate on any plan-record change, on the engine that suits WHAT
     CHANGED THE RECORD.

     WP-6.3 flipped the server's default from the hill-climb to `auto`, because the sheet a
     reader judges a house by was coming from the weaker engine — on the shipped Tidewater
     plan the hill-climb draws a kitchen with none of its five interior doors and strands
     three rooms, and CP-SAT draws all of them and strands none. But a CP proof takes
     SECONDS and this fires 400 ms behind every wall drag, so left alone the flip made the
     handle unusable: e2e/walk.mjs failed four interaction checks at once.

     A settle TIMER was tried first and was worse — a second render landing mid-gesture
     replaces the handle element under the pointer and the drag dies. So the choice is made
     by provenance instead: a wall drag asks for the fast engine BY NAME, and every other
     way the record can change (a style switch, a load, an undo) takes the good one. The
     drag is the only interaction with a hand on it, and it is the only one that cannot
     afford the wait. */
  React.useEffect(() => {
    if (!plan) return;
    const dragged = draggingRef.current;
    draggingRef.current = false;
    const t = setTimeout(
      () => runEvaluate(plan, dragged ? { engine: 'heuristic' } : {}), 400);
    return () => clearTimeout(t);
  }, [plan, strict, runEvaluate]);

  if (!plan) {
    return (
      <div style={{ padding: '26px 30px', maxWidth: 720 }}>
        {/* A room or grouping searched from the palette lands HERE, on the empty bench —
            which is precisely where its acknowledgement was missing. */}
        <Spotlight kind={selection?.roomType ? 'room' : 'grouping'}
          id={selection?.roomType || selection?.grouping}
          note={selection?.roomType
            ? 'a room type from the catalogue — the bench places rooms, it does not hold the catalogue entry'
            : 'a grouping from the catalogue — a plan is composed from groupings, the bench does not display one'}
          onDismiss={() => nav.select({ roomType: null, grouping: null })} />
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
  const assessmentStale = !!assessment && assessment.forSeq !== appliedSeqRef.current;
  const classOf = (id) => (assessment && !assessmentStale ? assessment.byId.get(id) : null);
  const statements = Object.fromEntries(findings.map((f) => [f.id, f.statement]));
  const nonInfo = findings.filter((f) => f.severity !== 'info').length;
  const classified = assessment ? CLASSES.reduce((n, c) => n + (assessment.counts[c] || 0), 0) : 0;

  const unjudgedConstraints = findings.filter((f) =>
    f.layer === 'style' && /cannot evaluate|check by hand/i.test(f.statement));
  const faultUnjudged = lastEval?.fault_unjudged || [];
  // THE FOURTH STATE (WP-5.13), which reached this surface only after the WP-5.14 audit went
  // looking. A fault whose every test declined its `applies_when` precondition appears in no
  // other list, so leaving it out of the bench reproduced here the exact collapse the state was
  // invented to prevent: absent from every list reads as clear.
  const faultNotApplicable = lastEval?.fault_not_applicable || [];
  const cs = check?.constraint_summary;
  const relax = placement?.geometry_report?.relaxations;
  /* WHICH ENGINE ACTUALLY DREW THIS, read from the record rather than asserted. Until
     WP-6.3 the paragraph under the sheet said flatly that "each edit re-scores on the fast
     search, which is a hill-climb and not an optimiser" and that "nothing it draws asserts
     that feasibility was proved" — true when the default was the hill-climb, and false the
     moment the default became `auto`. A caption that names the wrong engine is worse than
     one that names none: a reader cannot tell a proof from a search, which is the one
     distinction this surface exists to keep. `reason` is present when `auto` FELL BACK, and
     that is the case worth saying out loud. */
  const solver = placement?.geometry_report?.solver;
  const proved = solver?.engine === 'cp-sat';
  /* WP-11.8 (`oq/a-proof-of-feasibility-is-not-a-proof-of-composition`, ruled 4 Sep 2026): a
     CP-SAT placement outranks a hill-climb placement on FEASIBILITY and on nothing else. Phase A
     proves the hard set; phase B carries every compositional term the corpus has, and when it
     times out `objective` is null and the drawn house is whatever the solver reached first — no
     term for the front, the axis, the mirror pair or the stack was evaluated on it. This
     paragraph said "proved, not searched" over exactly that placement, which is the bench half of
     the diagnosis's J2. `alternative` carries the search's placement with BOTH its numbers: its
     demerit score AND the count of declared facts it breaks, judged against the same downgrade
     list, because a lower score alone reads as a better house and on `spec-builder-colonial` is
     bought with sixteen broken facts. */
  const objectiveRan = !(proved && (solver?.objective === null || solver?.objective === undefined));
  const alternative = solver?.alternative;
  const fellBack = solver?.engine === 'heuristic' && solver?.reason
    && solver.reason !== 'requested';
  // OQ 54. The search may place a room below the floor of its own catalogue band, charging
  // itself 12 points and winning anyway — and the plan RECORD still declares the full size, so
  // the trade is invisible to every layer of the critic downstream. geometry.py reports it; this
  // is the surface that shows it. The CP engine refuses the trade outright, so proving a
  // placement is the fix as well as the diagnosis.
  const underBand = placement?.geometry_report?.under_band;
  /* WP-11.1 — WHAT THE PLACEMENT GAVE UP, computed in build/disclosures.py and rendered here
     rather than re-derived. The paragraph under the sheet used to tell a reader that where a
     set of the record's declared facts could not all hold, "the ones it had to give up are
     named above rather than dropped" — and nothing above named them. On the shipped Tidewater
     plan that is sixteen declared exterior walls, both ends of the centre passage among them,
     with the compositional objective never evaluated. The list is the server's; this surface
     may not compute its own, or the two spellings drift the way the citation grammar's three
     did. */
  const disclosures = placement?.disclosures || [];
  const gaveUp = disclosures.filter((d) => d.id !== 'engine' && d.id !== 'relaxations');
  const TONE = { iron: 'var(--sev-fatal)', copper: 'var(--sepia)', verd: 'var(--verd)' };
  const levelIndices = (plan.levels || []).map((l) => l.index ?? 0);
  const declared = plan.adjacencies || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      {/* The strip holds what you are LOOKING AT — the style, the level, the ghost. Two
          folds hold the rest: what is drawn over the plan, and what the solver is asked to
          do. It carried eight axes in one row before, which meant the three you steer by
          were the same size and weight as the five you touch once an hour. */}
      <Spotlight kind={selection?.roomType ? 'room' : 'grouping'}
        id={selection?.roomType || selection?.grouping}
        note={selection?.roomType
          ? 'a room type from the catalogue — the plan below places rooms, it does not hold the catalogue entry'
          : 'a grouping from the catalogue — the plan below is composed from groupings, it does not display one'}
        onDismiss={() => nav.select({ roomType: null, grouping: null })} />
      <FilterStrip right={
        <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <FilterGroup label="solver" active={strict ? 1 : 0} summary={strict ? 'strict' : ''}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 9 }}>
              <Chip on={strict} onClick={() => setStrict(!strict)}
                title="the completeness layer: treat absent room types as failures (--strict)">strict</Chip>
              <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>candidates {seeds}</span>
              <input type="range" min="40" max="800" step="40" value={seeds} aria-label="how many candidate placements the search tries"
                onChange={(e) => setSeeds(+e.target.value)} style={{ width: 84, accentColor: 'var(--gilt-deep)' }} />
              <ActionChip onClick={() => runEvaluate(plan, { engine: 'cp' })} affix="⊢"
                title="WP-2.3: prove the placement with CP-SAT — hard constraints on the record's declared facts, a named conflict set if they cannot all hold. Takes seconds; per-drag re-scores stay on the fast search.">
                prove placement (CP-SAT)</ActionChip>
              <ActionChip onClick={runCritique} affix="?" disabled={critiquing || !!revising}
                title="WP-9.1: the analyst — place once, check, and sort every finding into what it means to a generator: a move answers it, the engine's, the critic's own invention, or the architect's. One heavy call; not run per edit.">
                {critiquing ? 'critiquing…' : 'critique'}</ActionChip>
              <ActionChip onClick={() => runRevise({ engine: 'heuristic', rounds: 6, budget_s: 60 })}
                affix="≫" disabled={!!revising}
                title="WP-9.2: the corrective revisions on the fast search — up to 6 rounds, 60 s. Accepts a round only on a strict improvement, rolls back otherwise, and loads the result as one undo step. Refusals on the search are usually the engine's noise; read the panel's engine line.">
                {revising && live.length === 0 && revising !== 'running' ? 'revise (search)…' : 'revise (search)'}</ActionChip>
              <ActionChip onClick={() => runRevise({ engine: 'auto', rounds: 4, budget_s: 120 })}
                affix="≫" disabled={!!revising}
                title="WP-9.2: the corrective revisions proof-backed — CP-SAT is asked for before any declared move; up to 4 rounds, 120 s. Minutes, not seconds; the panel shows each round as it lands.">
                revise (proof)</ActionChip>
            </span>
          </FilterGroup>
          {/* Undo stays OUT of the disclosure. The density pass tidied it in beside the
              solver settings, which put the one act a reader reaches for immediately after a
              mistake behind a click — and the e2e walk, which drags a room and undoes it,
              could not find the button at all. A thing you need when something has just gone
              wrong is not a setting. */}
          <ActionChip onClick={() => planDoc.undo()} affix="↩" title="undo the last record edit">undo</ActionChip>
          <ActionChip onClick={() => runEvaluate(plan)} affix="↻" disabled={busy}
            title={proved
              ? 'CP-SAT proved this placement; re-solving takes seconds and should return the same one'
              : 'this placement came from the hill-climb; results differ across runs'}>
            {busy ? 're-solving…' : 're-solve'}
          </ActionChip>
        </span>
      }>
        <Eyebrow as="span">style</Eyebrow>
        <StylePicker value={plan.style} onChange={(v) => planDoc.update(mutations.setStyle(v))}
          label="Judge this plan against a different style — findings appear and clear" width={190} />
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <ChipGroup label="level">
          <Eyebrow as="span">level</Eyebrow>
          {levelIndices.map((i) => (
            <Chip key={i} radio on={level === i} onClick={() => setLevel(i)}>
              {(plan.levels.find((l) => (l.index ?? 0) === i) || {}).name || 'level ' + i}
            </Chip>
          ))}
        </ChipGroup>
        <Chip on={ghost} onClick={() => setGhost(!ghost)}>ghost below</Chip>
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <FilterGroup label="overlays"
          active={(ov.daylight ? 1 : 0) + (ov.wet ? 1 : 0) + (ov.privacy ? 1 : 0)}
          summary={[ov.daylight && 'daylight', ov.wet && 'wet', ov.privacy && 'privacy']
            .filter(Boolean).join(' · ') || 'none'}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
            <Chip on={ov.daylight} tone="var(--green-deep)" onClick={() => setOv({ ...ov, daylight: !ov.daylight })}>daylight reach</Chip>
            <Chip on={ov.wet} tone="var(--blue-deep)" onClick={() => setOv({ ...ov, wet: !ov.wet })}>wet stacks</Chip>
            <Chip on={ov.privacy} tone="var(--sepia)" onClick={() => setOv({ ...ov, privacy: !ov.privacy })}>privacy gradient</Chip>
          </span>
        </FilterGroup>
      </FilterStrip>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {/* the critique */}
        <PullPane pane="workbench" side="left"
          style={{ borderRight: '1px solid var(--rule)', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '12px 12px 10px', borderBottom: '1px solid var(--rule)' }}>
            <SeverityTally counts={counts} active={sev} onSelect={setSev} />
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginTop: 10 }}>
              <ChipGroup label="finding layer">
                {layers.map((l) => {
                  const n = findings.filter((f) => f.layer === l).length;
                  return (
                    <Chip key={l} radio on={layer === l}
                      onClick={() => setLayer(layer === l ? null : l)}>{l} {n}</Chip>
                  );
                })}
              </ChipGroup>
            </div>
            {(room || sev || layer) && (
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginTop: 9 }}>
                <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)' }}>
                  {shown.length} of {findings.length} findings shown
                  {room ? ` · at ${room}` : ''}
                </span>
                <button type="button" onClick={() => { setRoom(null); setSev(null); setLayer(null); }}
                  style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)',
                    borderBottom: '1px solid var(--link-underline)' }}>clear</button>
              </div>
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
                    engineTag={f.layer === 'drawn' ? engineLabel(f.engine) : null}
                    classTag={(() => { const c = classOf(f.id); return c ? classTag(c.cls, c.item) : null; })()}
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
                  <JudgmentMark state="unjudged" label={u.name} reason={unjudgedReason(u)} />
                </div>
              ))}
              {faultNotApplicable.slice(0, 4).map((u) => (
                <div key={u.fault} style={{ marginBottom: 10 }}>
                  <JudgmentMark state="unjudged" label={u.name + ' — not applicable'}
                    reason={'every test is preconditioned on ' + (u.because || []).join(', ')
                            + ' (' + (u.required || []).join(', ') + '); none ran'} />
                </div>
              ))}
              {faultUnjudged.length > 8 && (
                <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', marginBottom: 8 }}>
                  and {faultUnjudged.length - 8} more faults beyond evaluation on this record
                </div>
              )}
              <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)', margin: '4px 0 0' }}>
                Unjudged is not passed. The counts above are this plan's; corpus-wide, 295 of
                660 style constraints carry no test at all, which is why so many land here.
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
        </PullPane>

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
                  : reviseError
                    ? `${reviseError} — the sheet below is the record as it stands`
                  : revising
                    ? (revising === 'submitting' ? 'revising: submitting…'
                      // 'submitted', not 'queued': the client cannot see the pool, only that the
                      // job exists and has not yet said `stage` -- which is what waiting behind
                      // another job looks like from here, and also what the first 50 ms look like
                      : revising === 'submitted' ? 'revising: submitted, waiting for the worker'
                        : `revising… round ${live.length ? live[live.length - 1].n : '—'}`)
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
          {gaveUp.length > 0 && (
            <div style={{ maxWidth: 1000, border: '1px solid var(--rule)',
              borderLeft: '3px solid var(--sev-fatal)', padding: '10px 14px', margin: '0 0 14px' }}>
              <Eyebrow tone="secondary">what this placement gave up</Eyebrow>
              <ul style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-2)',
                margin: '6px 0 0', paddingLeft: 18 }}>
                {gaveUp.map((d) => (
                  <li key={d.id} style={{ color: TONE[d.tone] || 'var(--ink-2)' }}>{d.text}</li>
                ))}
              </ul>
              <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', margin: '8px 0 0' }}>
                Each line is a count the placement record already carried and no surface read.
                A proof against a relaxed hard set is a proof of a different question.
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
          {/* WP-9.3: the analyst's summary. DISPLAY ONLY -- a clickable class filter would be
              per-surface filter state, which lives in the URL or not at all. data-classified
              and data-findings are two routes' counts of one placement, for the walk. */}
          {assessment && (
            <div data-panel="critique" data-classified={classified} data-findings={nonInfo}
              style={{ maxWidth: 1000, border: '1px solid var(--rule)',
                borderLeft: `3px solid ${assessmentStale ? 'var(--ink-4)' : 'var(--gilt-deep)'}`,
                padding: '10px 14px', margin: '0 0 14px', opacity: assessmentStale ? 0.7 : 1 }}>
              <Eyebrow tone="secondary">
                critique · by class{assessment.engine ? ` · ${engineLabel(assessment.engine)}` : ''}
                {assessment.key ? ` · key [${assessment.key.join(', ')}]` : ''}
              </Eyebrow>
              <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginTop: 6,
                font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
                {CLASSES.map((c) => (
                  <span key={c} style={{ color: assessment.counts[c] ? 'var(--ink-2)' : 'var(--ink-4)' }}>
                    {CLASS_SHORT[c]} {assessment.counts[c] || 0}
                  </span>
                ))}
                <span style={{ color: 'var(--ink-4)' }}>could not evaluate {assessment.couldNot}</span>
              </div>
              <p style={{ font: 'var(--type-data-s)', color: assessmentStale ? 'var(--sev-serious)' : 'var(--ink-3)', margin: '8px 0 0' }}>
                {assessmentStale
                  ? 'this critique is of an earlier evaluation — the record has changed; run it again'
                  : 'each finding row carries its class; a move answers it, or it is the engine\'s, the critic\'s own, or the architect\'s. Nothing here calls the plan good.'}
              </p>
            </div>
          )}
          <RevisionPanel report={plan.revision_report} live={live} statements={statements}
            onCiteFinding={(id) => { setOpenId(id); const f = findings.find((x) => x.id === id); if (f?.at) setRoom(f.at); }} />
          {placement?.geometry_report?.solver?.refinements?.length > 0 && (
            <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', margin: '0 0 10px' }}>
              solver refinements ({placement.geometry_report.solver.refinements.length}):{' '}
              {placement.geometry_report.solver.refinements.slice(0, 2).join(' · ')}
              {placement.geometry_report.solver.refinements.length > 2 ? ' · …' : ''}
            </p>
          )}
          {placement && (
            <div style={{ maxWidth: 1120, opacity: busy ? 0.45 : 1, transition: 'opacity .3s' }}>
              <PlateViewer label="the sheet" height="clamp(420px, 74vh, 960px)"
                note="⌘/ctrl-scroll to zoom · drag to pan · a wall handle still drags the wall">
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
                  // the next evaluate is behind a hand, so it takes the fast engine
                  draggingRef.current = true;
                  planDoc.update(mutations.resizeRoom(lvIdx, r.id, { [field]: size }));
                }}
                title={plan.name || plan.id}
                subtitle={((plan.levels.find((l) => (l.index ?? 0) === level) || {}).name
                    || `level ${level}`) + ' plan' + (placement.footprint
                  ? ` · ${placement.footprint.bays} bays of ${placement.footprint.bay_module_ft}′ · clear dimensions`
                  : '')}
                styleName={plan.style} />
              </PlateViewer>
            </div>
          )}

          <p style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-3)',
            margin: '16px 0 0', maxWidth: '76ch' }}>
            {proved
              ? <>This placement was <strong>proved feasible</strong>, not searched: CP-SAT held
                the record's own declared facts as hard constraints and returned {solver.status
                  ? solver.status.split('—')[0].trim().toLowerCase() : 'a solution'}.{' '}
                {!objectiveRan
                  ? <><strong>Its composition was not evaluated.</strong> The proof ran out of
                    budget before the compositional objective, so no term for the front, the axis
                    or the stack was scored on this drawing — it is the first feasible placement,
                    not the best one.{alternative?.verdict === 'offered'
                      ? <> The fast search places the same house at <strong>{alternative.score}</strong> demerits
                        against this drawing's {alternative.drawn_score}, and breaks{' '}
                        <strong>{alternative.hard_fact_violations}</strong> declared fact(s) this
                        one holds ({alternative.drawn_hard_fact_violations}). A lower score is not
                        on its own a better house: choosing the search is choosing a better
                        composition over a proved feasibility, and that is the choice. </>
                      : ' '}</>
                  : ' '}
                {gaveUp.length
                  ? <>Where a set of them could not all hold, the ones it had to give up are named
                    in <em>what this placement gave up</em> above — until WP-11.1 this sentence
                    claimed they were named and no surface named them. </>
                  : 'It gave nothing up. '}
                <em>Prove placement (CP-SAT)</em> above runs the same act on demand. </>
              : <>This placement came from the <strong>fast search</strong>, which is a hill-climb and
                not an optimiser: seconds-cheap, not deterministic across runs, and nothing it draws
                asserts that feasibility was proved.{fellBack
                  ? <> The proof was attempted and did not answer — <em>{solver.reason}</em>. </>
                  : ' '}<em>Prove placement (CP-SAT)</em> above is the act that proves it. </>}
            A wall drag deliberately re-scores on the fast search — a hill-climb, not an optimiser —
            because a gesture cannot wait for a proof; every other edit takes the proof where it can
            be had. Either engine trades a room's
            size away when it must, and says so under the drawing rather than silently (OQ 54). A plan
            with no fatal findings is still not therefore good.
          </p>
        </div>
      </div>
    </div>
  );
}
