/* Details & Export. What works today works plainly: the plan record, the brief, the check
   report and every generated SVG leave as files. What is not built is present, disabled, and
   named as not built -- never hidden. The interface must not imply a completeness the corpus
   does not have.

   AND IT NAMES WHAT IS NOT BUILT BY WHAT IT IS, NOT BY THE PACKAGE THAT WOULD BUILD IT
   (WP-14.31). Each unbuilt card carried a work-package numeral and a description written here,
   the details card a typed "262 recorded pack conflicts", and the costing paragraph a typed
   "86 of them priced in dollars" beside a field name. A work package is the build's history and
   not something a reader can use; the two cards and the costing sentence are glossary records
   now, and the conflict figure is the sum of the pack index's own `conflicts` rows. */
import React from 'react';
import { api } from '../api/client.js';
import { planDoc } from '../state/planDoc.js';
import { session } from '../state/session.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterStrip, Chip, ChipGroup, ActionChip } from '../Chrome.jsx';
import { Term } from '../components/Term.jsx';
import { useGlossary } from '../api/useGlossary.js';
import { describeTerm } from '../glossary/termView.js';
import { formatHash } from '../router.js';
import { conflictTotal } from '../proportions/page.js';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { FACES, FACE_TERM, ENTRANCE_FRONT_TERM, parseFace, drawingOpts, cadOpts, sheetFileName,
  recordWord } from './drawingFaces.js';
import { ConflictSet } from '../components/ConflictSet.jsx';
import { evaluateRefusal, placementRefusal, sketchOf, errorText, refusalFromError, isMissingLibrary }
  from '../sheet/refusal.js';

function save(name, content, type = 'application/json') {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob(
    [typeof content === 'string' ? content : JSON.stringify(content, null, 1)], { type }));
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

const card = { border: '1px solid var(--rule)', padding: '14px 16px', flex: '1 1 300px',
  minWidth: 280, maxWidth: 420 };
const cardTitle = { font: 'var(--fw-reg) 17px/1.2 var(--display)', color: 'var(--ink)', margin: '0 0 7px' };
const cardBody = { font: 'var(--fw-reg) 13px/1.55 var(--body)', color: 'var(--ink-2)', margin: '0 0 12px' };

/* WHICH FACE AN ELEVATION LEAVES AS (WP-14.27, PRD §C.12). Export drew only the face the record
   calls the entrance front, so the other three elevations the generator draws could be looked at
   on the Drawing Set and never taken away. The face is an address param like the Drawing Set's,
   worded by the face's own record; no face is the server's default, the entrance front, and that
   chip is worded by its record rather than by a compass point this surface would have to derive. */
const EXPORT_SPEC = { face: { widens: true } };

/* The designed and unbuilt cards, each one glossary record: its term is the card's title and its
   definition the card's body. */
const NOT_BUILT = ['design-guidelines', 'details-library'];

export function ExportDetails({ lastEval }) {
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);
  const s = React.useSyncExternalStore(session.subscribe, session.get);
  const [busySvg, setBusySvg] = React.useState(null);
  const [busyCad, setBusyCad] = React.useState(null);
  const [note, setNote] = React.useState(null);
  const [refusal, setRefusal] = React.useState(null);
  const F = useSurfaceFilters(EXPORT_SPEC);
  const face = parseFace(F.values.face);
  const glossary = useGlossary();
  const word = recordWord(glossary);
  /* The pack-conflict figure is the corpus's, summed off the pack index's rows; the costing
     sentence that carried a fault count read from /api/overview (WP-14.13, after it was typed as
     "209" against a corpus of 210) is a glossary record now and names no figure at all. Unread,
     the card names no figure either. */
  const [packConflicts, setPackConflicts] = React.useState(null);
  React.useEffect(() => {
    let live = true;
    api.proportionPacks().then((j) => { if (live) setPackConflicts(conflictTotal(j)); }).catch(() => {});
    return () => { live = false; };
  }, []);

  /* NOTHING LEAVES THIS SYSTEM FROM A REFUSED PLACEMENT, AND NOTHING LEAVES IT FROM A SKETCH
     (WP-13.4). The verdict is the one the bench already holds — `/api/plan/evaluate`'s own
     `placement_refused`, or the placed record's `geometry_report.refused`, or the wall drag's
     `placement.sketch` — read through `sheet/refusal.js` and derived nowhere here. A working
     sketch is a legitimate thing to look at and is never a legitimate thing to hand a drafter,
     so it blocks an export while it does not block the bench's own plate. */
  const evalRefusal = evaluateRefusal(lastEval) || placementRefusal(lastEval?.placement);
  const sketch = sketchOf(lastEval?.placement);
  const blocked = Boolean(evalRefusal) || Boolean(sketch);
  const blockedWhy = evalRefusal
    ? 'the placement was refused — nothing may be exported from it'
    : sketch
      ? 'the bench is showing a working sketch from a wall drag — a sketch is never a file'
      : '';
  const shown = refusal || evalRefusal;

  /* THE ROUTES GO THROUGH `api/client.js` NOW, AND A REFUSAL REACHES THE READER.
     `saveSvg` was a raw fetch with `if (r.ok)` and NO else, so a 422 downloaded nothing and
     said nothing — a button that appeared to do its job and did not. `saveCad` painted every
     failure in `var(--forthcoming)`, the colour this surface reserves for what is DESIGNED AND
     NOT BUILT, so a refused house read as a missing feature. Both report through the one leaf:
     a refused placement shows its conflict set, a 501 keeps saying the server has no CAD
     library, and anything else is stated as itself. */
  async function saveSvg(kind) {
    if (!plan || blocked) return;
    setBusySvg(kind); setNote(null); setRefusal(null);
    try {
      const j = await api.drawing(kind, plan, drawingOpts(kind, face));
      save(sheetFileName(plan.id, kind, face || j.entrance_face), j.svg, 'image/svg+xml');
    } catch (e) {
      const r = refusalFromError(e);
      if (r) setRefusal(r);
      else setNote({ text: errorText(e) || 'the drawing could not be generated',
        missing: isMissingLibrary(e) });
    } finally {
      setBusySvg(null);
    }
  }

  /* WP-5.1: DXF sheets and the IFC model, generated by the same build/ modules
     the CLI drives. A refusal (missing optional library on the server, an
     elevation outside the classical-front family) is shown stated, not
     swallowed into an empty download. */
  async function saveCad(fmt, kind) {
    if (!plan || blocked) return;
    const key = kind ? `${fmt}:${kind}` : fmt;
    setBusyCad(key); setNote(null); setRefusal(null);
    try {
      const j = await api.exportCad(fmt, plan, cadOpts(fmt, kind, face));
      save(j.filename, j.text, fmt === 'dxf' ? 'application/dxf' : 'application/x-step');
    } catch (e) {
      const r = refusalFromError(e);
      if (r) setRefusal(r);
      else setNote({ text: errorText(e) || 'the export failed', missing: isMissingLibrary(e) });
    } finally {
      setBusyCad(null);
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip>
        <Eyebrow as="span">details &amp; export</Eyebrow>
        <span style={{ width: 1, height: 18, background: 'var(--rule)' }} />
        <Eyebrow as="span"><Term id={FACE_TERM} /></Eyebrow>
        <ChipGroup label={word(FACE_TERM)}>
          <Chip radio on={!face} title={describeTerm(glossary, ENTRANCE_FRONT_TERM).title}
            onClick={() => F.set('face', null)}>{word(ENTRANCE_FRONT_TERM)}</Chip>
          {FACES.map((f) => (
            <Chip key={f.id} radio on={face === f.id} title={describeTerm(glossary, f.term).title}
              onClick={() => F.set('face', f.id)}>{word(f.term)}</Chip>
          ))}
        </ChipGroup>
      </FilterStrip>

      <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '22px 26px 36px' }}>
        {/* WHAT MAY NOT LEAVE, AND WHY, BEFORE THE BUTTONS THAT WOULD HAVE SENT IT (WP-13.4).
            The conflict set is the same component the bench draws where the plate would be, so
            a reader who came here from a refused sheet meets the same words rather than a
            second account of one verdict. */}
        <ConflictSet refusal={shown} where="every export of this record" />
        {note && (
          <p data-export-note={note.missing ? 'missing-library' : 'error'}
            style={{ font: 'var(--type-data-s)',
              // the NOT-BUILT colour is for what is not built. An export that FAILED is not a
              // forthcoming feature, and painting the two the same made a refused house read
              // as a gap in the product.
              color: note.missing ? 'var(--ink-2)' : 'var(--sev-serious)',
              margin: '0 0 14px', maxWidth: '76ch' }}>
            {note.missing
              ? `not built on this server — ${note.text}`
              : `refused — ${note.text}`}
          </p>
        )}
        <Eyebrow style={{ marginBottom: 12 }}>leaves the system today</Eyebrow>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'stretch' }}>
          <div style={card}>
            <h3 style={cardTitle}>The plan record</h3>
            <p style={cardBody}>
              The IR itself — the record every drawing and finding renders from. Clear
              dimensions, declared walls, doors, assertions. JSON against
              <span style={{ fontFamily: 'var(--mono)' }}> schema/plan.schema.json</span>.
            </p>
            <ActionChip affix="↓" disabled={!plan} onClick={plan ? () => save(`${plan.id}.json`, plan) : undefined}
              title={plan ? '' : 'no plan on the bench'}>
              {plan ? `download ${plan.id}.json` : 'no plan on the bench'}
            </ActionChip>
          </div>
          <div style={card}>
            <h3 style={cardTitle}>The brief &amp; the check report</h3>
            <p style={cardBody}>
              The brief as typed, and the validator's latest full report — counts, findings,
              constraint summary and the could-not-judge list, none of it collapsed.
            </p>
            <span style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <ActionChip affix="↓" disabled={!s.brief} onClick={s.brief ? () => save(`${s.brief.id || 'brief'}.json`, s.brief) : undefined}>
                {s.brief ? 'download brief' : 'no brief drafted'}
              </ActionChip>
              <ActionChip affix="↓" disabled={!lastEval?.check} onClick={lastEval?.check ? () => save(`${plan?.id || 'plan'}-check.json`, lastEval) : undefined}>
                {lastEval?.check ? 'download check report' : 'no evaluation yet'}
              </ActionChip>
            </span>
          </div>
          <div style={card}>
            <h3 style={cardTitle}>The drawing set, as SVG</h3>
            <p style={cardBody}>
              Every sheet the generators produce, in the Drawn Language. The drawing is a
              render of the record; export re-renders, it never snapshots the screen.
            </p>
            <span style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {['plan', 'elevation', 'section', 'bearing', 'roof'].map((k) => (
                <ActionChip key={k} affix={busySvg === k ? '…' : '↓'} disabled={!plan || blocked}
                  title={blocked ? blockedWhy : ''}
                  onClick={plan && !blocked ? () => saveSvg(k) : undefined}>
                  {busySvg === k ? 'generating…' : k}
                </ActionChip>
              ))}
            </span>
          </div>
          <div style={card}>
            <h3 style={cardTitle}>DXF &amp; IFC</h3>
            <p style={cardBody}>
              Layered DXF per sheet, in inches, the record riding on the entities as XDATA —
              round-trip proven: DXF → plan record → validator gives the same findings. And an
              IFC4 model: walls, slabs, openings, roof and spaces, every product carrying its
              TDL ids in a <span style={{ fontFamily: 'var(--mono)' }}>TDL</span> property set.
            </p>
            <span style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {['plan', 'section', 'roof', 'elevation'].map((k) => (
                <ActionChip key={k} affix={busyCad === `dxf:${k}` ? '…' : '↓'}
                  disabled={!plan || blocked} title={blocked ? blockedWhy : ''}
                  onClick={plan && !blocked ? () => saveCad('dxf', k) : undefined}>
                  {busyCad === `dxf:${k}` ? 'generating…' : `${k} dxf`}
                </ActionChip>
              ))}
              <ActionChip affix={busyCad === 'ifc' ? '…' : '↓'} disabled={!plan || blocked}
                title={blocked ? blockedWhy : ''}
                onClick={plan && !blocked ? () => saveCad('ifc') : undefined}>
                {busyCad === 'ifc' ? 'generating…' : 'ifc model'}
              </ActionChip>
            </span>
            {blocked && (
              <p data-export-blocked="" style={{ font: 'var(--type-data-s)',
                color: 'var(--refusal)', margin: '10px 0 0' }}>{blockedWhy}</p>
            )}
          </div>
        </div>

        <Eyebrow style={{ margin: '28px 0 12px' }}><Term id="mark-not-built" /></Eyebrow>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'stretch' }}>
          {NOT_BUILT.map((id) => (
            <div key={id} data-not-built={id} style={{ ...card, backgroundImage: 'var(--mark-not-built)' }}>
              <div style={{ background: 'var(--paper)', padding: '8px 10px' }}>
                <h3 style={{ ...cardTitle, color: 'var(--ink-2)' }}>{word(id)}</h3>
                <p data-not-built-definition="" style={{ ...cardBody, color: 'var(--ink-2)', marginBottom: 8 }}>
                  {describeTerm(glossary, id).text}
                </p>
                {id === 'details-library' && packConflicts != null && (
                  <span data-pack-conflicts={packConflicts}
                    style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
                    <Term id="pack-conflict" /> · {packConflicts}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        <p data-transcription-pointer="" style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)',
          color: 'var(--ink-2)', margin: '16px 0 0', maxWidth: '76ch' }}>
          <a href={formatHash('transcription')}>{word('surface-transcription')}</a>
          {' — '}{describeTerm(glossary, 'surface-transcription').text}
        </p>

        <p data-no-costing="" style={{ font: 'var(--fw-reg) 12.5px/1.6 var(--body)', color: 'var(--ink-2)',
          margin: '24px 0 0', maxWidth: '76ch' }}>
          <Term id="no-costing-engine" />{' — '}{describeTerm(glossary, 'no-costing-engine').text}
        </p>
      </div>
    </div>
  );
}
