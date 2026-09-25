/* Surface ⑧ — the Drawing Set, live. Elevation, section, bearing diagram, roof plan
   and the solved plan — siblings of the workbench sheet, generated from the same
   record by the same build/ pipeline the CLI drives, re-tokenized to the Drawn
   Language (re-rendered, never redrawn). The elevation carries WP-3.2's disclosure
   permanently and without embarrassment. */
import React from 'react';
import { planDoc } from '../state/planDoc.js';
import { api } from '../api/client.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterStrip, Chip, ChipGroup, ActionChip } from '../Chrome.jsx';
import { PlateViewer } from '../components/PlateViewer.jsx';
import { KINDS } from './drawingKinds.js';
import { ConflictSet } from '../components/ConflictSet.jsx';
import { engineClaim, statusHead } from '../sheet/engineClaim.js';
import { errorText, refusalFromError, placementRefusal } from '../sheet/refusal.js';
import { RoundPlate } from '../round/RoundPlate.jsx';
import { useSurfaceFilters } from '../filters/useFilters.js';
import { useGlossary } from '../api/useGlossary.js';
import { describeTerm } from '../glossary/termView.js';
import { Term } from '../components/Term.jsx';
import { JOURNEY_WORDS } from '../journey/journey.js';
import { FACES, FACE_TERM, ENTRANCE_FRONT_TERM, parseFace, parseSheet, sheetParam, drawingOpts, sheetFileName,
  faceChipWords, recordWord } from './drawingFaces.js';

/* THE ROUND'S PLACE IS A URL (§7.2), which is WP-5.6's rule and not a new one: a view with
   three overlays and an exploded model is a thing one reader sends another, and until this it
   died with the component. All four axes carry `widens: true` — none of them narrows a list,
   and `FilterStrip`'s "N narrowing" counter lies if they are counted (the Kit's `all` chip and
   the Phylogeny's map toggle are the two surfaces that taught it that).

   The encodings are the shortest thing that round-trips, and each is PARSED DEFENSIVELY: a
   hand-edited URL is an untrusted string, and a viewer that threw on one would lose the whole
   surface rather than the one control. */
const parseOv = (raw) => (raw ? String(raw).split(',').filter(Boolean) : []);
const fmtOv = (list) => (list && list.length ? list.join(',') : null);

const parseExplode = (raw) => {
  if (!raw) return { mode: 'none', k: 0 };
  const [mode, k] = String(raw).split(':');
  if (mode !== 'levels' && mode !== 'elements') return { mode: 'none', k: 0 };
  const n = parseFloat(k);
  return { mode, k: Number.isFinite(n) ? Math.max(0, Math.min(1.5, n)) : 1 };
};
const fmtExplode = (e) => (e && e.mode && e.mode !== 'none' ? `${e.mode}:${e.k}` : null);

const parseCut = (raw) => {
  if (!raw) return {};
  const [axis, at] = String(raw).split(':');
  if (axis === 'level') return { axis: 'level' };
  if (axis !== 'x' && axis !== 'y') return {};
  const n = parseFloat(at);
  return Number.isFinite(n) ? { axis, at: n } : {};
};
const fmtCut = (c) => {
  if (!c || !c.axis) return null;
  return c.axis === 'level' ? 'level' : `${c.axis}:${c.at}`;
};
import { defaultAxon } from '../round/frame.js';
import { plateKeyFor } from '../round/annotate.js';


/* WP-12.0. The compass order, not a preference: `build/elevation.py`'s own FACES tuple is
   ("S", "N", "E", "W") and the elevation record carries a face block for every one of them.
   `render_elevation(elev, path, face=…)` has taken the argument since WP-3.2 and
   `corpus.drawing` has forwarded `body.face` since WP-5.1 — and no client ever sent one, so
   the surface has been showing the entrance front and calling it "front elevation" while
   three quarters of what the generator draws had never been seen. Which face is the FRONT is
   a fact the record states (`context.entrance_faces` → `elev.entrance_face`), so the chip
   says the compass point and the caption says the role, exactly as WP-11.9 ruled for the
   plan's north: plan-N is true-N unless a bearing says otherwise.
   The four faces, and the words each chip carries, are `drawingFaces.js`'s (WP-14.27): the
   compass letter the record uses, worded by the face's own glossary record. */

const DISCLOSURE = {
  // The 83-of-177 figure this caption used to print is tidewater-georgian's own count
  // (docs/reports/wp-3.2-elevation-generator.md), and it was drawn unqualified beneath a
  // Craftsman or a Charleston elevation as though it described them. Nothing in
  // build/elevation.py emits either number, so the caption could never drift back into
  // agreement with the generator. Stated as the limit it is, without a borrowed count.
  elevation: 'The elevation generator models a part of the photograph-measurable fault ' +
    'corpus and no more; the rest have no model at this layer yet (WP-3.2, disclosed rather ' +
    'than closed by fabricating data), and what it could not measure is absent from the ' +
    'measurements rather than reported as zero. Sash lights are ' +
    'set for the declared date; the cornice is the style’s own entablature reduction at the ' +
    'real storey height.',
  section: 'Cut from the same record as the plan. Storey heights come from the ' +
    'storey-graduation pack; nothing is drawn that is not in the section record.',
  bearing: 'Every upper wall line that does not continue to a wall below is a transfer ' +
    'beam — a number a builder prices. Over-spans are flagged by the generator itself.',
  roof: 'Wing ridges step down; the pitch sits inside the style band; chimneys satisfy ' +
    'the style constraint or say so.',
  plan: 'The geometry solver’s own render — the workbench sheet redrawn by build/render_plan.py ' +
    'from the same coordinates, for the set. Relaxations are counted in the header.',
};

export function DrawingSet({ go }) {
  const plan = React.useSyncExternalStore(planDoc.subscribe, planDoc.get);
  // WP-12.4: the model is the first plate and the five flat kinds are chips beneath it, so
  // arriving at ⑧ shows the house rather than one of its faces. It costs no extra call: the
  // scene route returns the six named views' plates WITH the model, where one `api.drawing`
  // returned one plate for the same solve.
  const [scene, setScene] = React.useState(null);
  const [sceneErr, setSceneErr] = React.useState(null);
  /* THE SHEET AND THE FACE ARE THE ADDRESS'S TOO (WP-14.27). Both were `useState`, so a reload
     or a sent link showed the model whatever the reader had been looking at. Like the Round's
     four axes they WIDEN rather than narrow -- choosing a drawing hides nothing -- so they are
     not counted as filters and clear-all leaves them where they are. */
  const F = useSurfaceFilters(React.useMemo(() => ({
    view: { widens: true }, ov: { widens: true },
    explode: { widens: true }, cut: { widens: true },
    sheet: { widens: true }, face: { widens: true },
  }), []));
  const kind = parseSheet(F.values.sheet);
  const setKind = React.useCallback((k) => F.set('sheet', sheetParam(k)), [F]);
  const view = F.values.view;
  const setView = React.useCallback((v) => F.set('view', v), [F]);
  const ov = React.useMemo(() => parseOv(F.values.ov), [F.values.ov]);
  const setOv = React.useCallback((list) => F.set('ov', fmtOv(list)), [F]);
  const explode = React.useMemo(() => parseExplode(F.values.explode), [F.values.explode]);
  const setExplode = React.useCallback((e) => F.set('explode', fmtExplode(e)), [F]);
  const cut = React.useMemo(() => parseCut(F.values.cut), [F.values.cut]);
  const setCut = React.useCallback((c) => F.set('cut', fmtCut(c)), [F]);
  const [plateOn, setPlateOn] = React.useState(false);
  // null means "whichever face the record calls the entrance front" — the server's own
  // default (`face or elev["entrance_face"]`), so arriving here draws what it always drew
  // and choosing a face is an act the reader takes, and one the address keeps.
  const face = parseFace(F.values.face);
  const setFace = React.useCallback((f) => F.set('face', parseFace(f)), [F]);
  const glossary = useGlossary();
  const word = recordWord(glossary);
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [busy, setBusy] = React.useState(false);
  const cache = React.useRef({});

  React.useEffect(() => { cache.current = {}; setScene(null); setSceneErr(null); }, [plan]);

  // ONE metered call for the model and all six named views' plates (WP-12.3): seven would buy
  // a reader eight record changes an hour against a budget of sixty.
  React.useEffect(() => {
    if (!plan || kind !== 'model' || scene || sceneErr) return;
    let dead = false;
    api.scene(plan)
      .then((j) => {
        if (dead) return;
        setScene(j);
        // the default opens on the axon that shows the entrance front, and never overwrites a
        // view the URL already names — a copied link must reproduce what its sender saw
        if (!view) setView(defaultAxon(j.scene?.entrance_face));
      })
      /* THE ERROR OBJECT, NOT A STRING (WP-13.4). `String(e.body?.detail?.error || …)` threw
         away everything but the sentence, and a refused placement arrives as a 422 whose
         detail carries the whole conflict set. `sheet/refusal.js` is the one reader of it. */
      .catch((e) => { if (!dead) setSceneErr(e); });
    return () => { dead = true; };
  }, [plan, kind, scene, sceneErr]);

  // The cache key carries the face, or four faces of one house would be one entry and the
  // reader would be shown the first one they asked for whichever chip they pressed.
  const key = kind === 'elevation' ? `${kind}:${face || '-'}` : kind;

  React.useEffect(() => {
    if (!plan || kind === 'model') return;
    if (cache.current[key]) { setResult(cache.current[key]); setError(null); return; }
    // The scene response already holds `plan`, the four elevations and `roof`, keyed exactly
    // as this cache keys them (workbench/server/corpus.py::SCENE_PLATES). Only `section` and
    // `bearing` are not in it, so only those two cost a call of their own.
    const fromScene = scene && scene.plates
      ? scene.plates[kind === 'elevation' ? `elevation:${face || scene.scene?.entrance_face || 'S'}` : kind]
      : null;
    if (fromScene) {
      // the whole result the drawing route returns, so the plate keeps its disclosures
      cache.current[key] = fromScene; setResult(fromScene); setError(null); return;
    }
    setBusy(true); setError(null); setResult(null);
    api.drawing(kind, plan, drawingOpts(kind, face))
      .then((j) => { cache.current[key] = j; setResult(j); })
      .catch((e) => setError(e))
      .finally(() => setBusy(false));
  }, [plan, kind, face, key, scene]);

  /* REFUSED, NOT DRAWN (WP-13.4). A drawing route answers 422 with `corpus._placed`'s own
     return when the placement breaks a hard fact of the type, so the refusal arrives here as a
     thrown error and `sheet/refusal.js` is the one reader of it. The scene route answers the
     same way; a scene that DID come back carries its placed record, so its verdict is read off
     that record rather than re-derived. Nothing here counts a downgraded fact for itself. */
  const plateRefusal = refusalFromError(error);
  const sceneRefusal = refusalFromError(sceneErr) || placementRefusal(scene && scene.plan);
  const refusal = kind === 'model' ? sceneRefusal : plateRefusal;
  const errText = kind === 'model' ? errorText(sceneErr) : errorText(error);
  // A PLATE IS WHAT MAKES A DOWNLOAD POSSIBLE. The control was unconditional, so on the model
  // view and on every refusal it was a button that silently did nothing -- and the moment a
  // refused placement can reach this surface, a live one would be a file of a house the corpus
  // refused. It is offered only where there is a rendered plate to save.
  const downloadable = kind !== 'model' && Boolean(result && result.svg);

  if (!plan) {
    return (
      <div style={{ padding: '26px 30px', maxWidth: 640 }}>
        <Eyebrow>no plan on the bench</Eyebrow>
        <p style={{ font: 'var(--fw-reg) 14px/1.6 var(--body)', color: 'var(--ink-2)', margin: '10px 0 14px' }}>
          The drawing set is generated from the plan record on the workbench. Load or
          compose one first.
        </p>
        <ActionChip onClick={() => go('workbench')}>go to the Plan Workbench</ActionChip>
      </div>
    );
  }

  function download() {
    if (!result?.svg) return;
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([result.svg], { type: 'image/svg+xml' }));
    a.download = sheetFileName(plan.id, kind, face || result.entrance_face);
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      {/* `flex: none` and `nowrap` because the face group made this strip wider than the
          pane: without them the plan id wrapped onto a second line inside a 34 px bar and
          collided with the chips. The strip is `overflowX: auto` by design, so the right
          answer under pressure is to let it SCROLL rather than to let its contents reflow —
          the same reason the clear-all control in `Chrome.jsx` is sticky. */}
      <FilterStrip right={
        <span style={{ display: 'flex', gap: 10, alignItems: 'center', flex: 'none' }}>
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', whiteSpace: 'nowrap' }}>
            {plan.id} · {plan.style}
          </span>
          {downloadable
            ? <ActionChip affix="↓" onClick={download}>download SVG</ActionChip>
            : <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', whiteSpace: 'nowrap' }}>
                {refusal ? 'nothing to download — refused' : 'nothing to download yet'}
              </span>}
        </span>
      }>
        <Eyebrow as="span">sheet</Eyebrow>
        <ChipGroup label="sheet">
          <Chip radio on={kind === 'model'} onClick={() => setKind('model')}>the model</Chip>
          {KINDS.map((k) => (
            <Chip key={k.id} radio on={kind === k.id} onClick={() => setKind(k.id)}>{k.label}</Chip>
          ))}
        </ChipGroup>
        {kind === 'elevation' && (
          <>
            <Eyebrow as="span"><Term id={FACE_TERM} /></Eyebrow>
            <ChipGroup label={word(FACE_TERM)}>
              {FACES.map((f) => (
                <Chip key={f.id} radio
                  on={(face || result?.entrance_face) === f.id}
                  title={describeTerm(glossary, f.term).title}
                  onClick={() => setFace(f.id)}>
                  {faceChipWords(word, f.id, result?.entrance_face, JOURNEY_WORDS.separator)}
                </Chip>
              ))}
            </ChipGroup>
          </>
        )}
      </FilterStrip>

      <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '22px 26px 34px' }}>
        {busy && <p style={{ font: 'var(--type-body)', color: 'var(--ink-2)' }}>generating from the record…</p>}
        {/* THE CONFLICT SET STANDS WHERE THE PLATE WOULD BE (WP-13.4). This panel has been "the
            generator refused" since WP-5.1 and it is the natural host: what is new is that a
            refusal may now be the TYPE's rather than the record's, and it arrives with the facts
            that could not hold. The plain panel below it is for everything else -- a missing
            library, an unreadable record -- which is a different sentence and keeps its own. */}
        <ConflictSet refusal={refusal} where={'the ' + kind} />
        {!refusal && error && (
          <div style={{ border: '1px solid var(--rule)', borderLeft: '2px solid var(--refusal)',
            background: 'var(--paper-deep)', padding: '12px 14px', maxWidth: 640 }}>
            <Eyebrow tone="secondary" style={{ marginBottom: 6 }}>the generator refused</Eyebrow>
            <p style={{ font: 'var(--fw-reg) 13.5px/1.6 var(--body)', color: 'var(--ink)', margin: 0 }}>
              {errText}
            </p>
            <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-2)', margin: '7px 0 0' }}>
              A refusal is content: this record does not carry what the {kind} generator
              needs, and it says so rather than inventing it.
            </p>
          </div>
        )}
        {kind === 'model' && (
          <div style={{ maxWidth: 1180 }}>
            {sceneErr ? (
              /* A REFUSAL IS NOT A COULD-NOT-EVALUATE, and printing one as the other is the
                 fake-unjudged shape. Where the placement was refused the conflict set above says
                 so in the corpus's own words and this line does not appear at all. */
              refusal ? null : (
              <div data-round-error="" style={{ font: 'italic 13px/1.6 var(--serif)', color: 'var(--ink-2)', padding: '18px 2px' }}>
                COULD NOT EVALUATE — the scene could not be built: {errText}
              </div>
              )
            ) : sceneRefusal ? null : !scene ? (
              <div style={{ font: 'italic 13px/1.6 var(--serif)', color: 'var(--ink-2)', padding: '18px 2px' }}>
                placing the house and building the model…
              </div>
            ) : (
              <PlateViewer label="the model" height="clamp(420px, 74vh, 960px)" note="drag orbits · a named view snaps back">
                <RoundPlate
                  scene={scene.scene}
                  plates={scene.plates}
                  platesRefused={scene.plates_refused}
                  refusedPlacement={sceneRefusal}
                  plan={scene.plan}
                  meta={scene.rooms_meta}
                  view={view || defaultAxon(scene.scene?.entrance_face)}
                  onView={setView}
                  plateOn={plateOn}
                  onPlate={setPlateOn}
                  ov={ov}
                  onOv={setOv}
                  explode={explode}
                  onExplode={setExplode}
                  cut={cut}
                  onCut={setCut}
                  title={plan.name || plan.id}
                  styleName={plan.style}
                  subtitle={`${scene.scene?.parti || 'no parti named'} · ${scene.scene?.massing || 'no massing named'}`}
                  disclosures={(scene.plan?.geometry_report?.disclosures) || []}
                />
              </PlateViewer>
            )}
          </div>
        )}
        {kind !== 'model' && result?.svg && (
          <div style={{ maxWidth: 1180 }}>
            <PlateViewer label={'the ' + kind} height="clamp(420px, 74vh, 960px)">
            <div style={{ background: 'var(--paper)', border: '1px solid var(--ink-2)',
              boxShadow: 'var(--shadow-plate)', padding: '16px 18px 10px' }}>
              {/* The fit goes on the WRAPPER, not into a second `style` on the <svg>.

                  It used to be injected as `<svg style="max-width:100%;height:auto" …`
                  before the element's own attributes — and every Python renderer opens
                  with `…viewBox="…" style="background:{PAL['ground']}">`. Two `style`
                  attributes on one element: the parser keeps the first and silently drops
                  the second, so each sheet's declared ground colour never applied. Same
                  family as the presentation-attribute-loses-to-a-class-rule trap
                  CLAUDE.md records for `render_plan.py`, by duplicate attribute rather
                  than by cascade, and invisible today only because what is painted behind
                  it happens to be a near-identical vellum. Found by an adversarial audit
                  of WP-5.7; a CSS rule on the wrapper reaches the child and cannot
                  collide with anything the renderer wrote. */}
              <div className="plate-fit" dangerouslySetInnerHTML={{ __html: result.svg }} />
              <div style={{ borderTop: '1px solid var(--rule)', marginTop: 10, padding: '8px 2px 4px',
                display: 'flex', justifyContent: 'space-between', gap: 24, alignItems: 'baseline' }}>
                {/* the interpunct join makes one unbreakable word; a zero-width space
                    after each lets the title fold at a word boundary and never inside a
                    word. `nowrap` here clipped it outright, and the loupe lays the plate
                    out at the PANE's width, which is narrower still than the surface. */}
                <span style={{ font: 'var(--fw-med) 10.5px/1.4 var(--serif)', letterSpacing: '.3em',
                  textTransform: 'uppercase', color: 'var(--ink)', flex: '0 1 auto', minWidth: 0 }}>
                  {(plan.name || plan.id).split(/\s+/).join('·\u200B')}
                </span>
                <span style={{ font: 'italic var(--fw-reg) 12.5px/1.5 var(--serif)', color: 'var(--ink-2)',
                  textAlign: 'right', flex: '1 1 34ch', minWidth: '22ch' }}>
                  {DISCLOSURE[kind]}
                </span>
              </div>
            </div>
            </PlateViewer>
            {result.relaxations && (
              <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '10px 0 0' }}>
                {result.relaxations.count} cut(s) off the bay line
                {result.relaxations.count ? ` · worst ${result.relaxations.max_off_grid_ft} ft` : ''}
              </p>
            )}
            {kind === 'elevation' && result.date_of_representation && (
              <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '10px 0 0' }}>
                {(face || result.entrance_face)} elevation
                {(face || result.entrance_face) === result.entrance_face
                  ? JOURNEY_WORDS.separator + word(ENTRANCE_FRONT_TERM)
                  : `${JOURNEY_WORDS.separator}${word(ENTRANCE_FRONT_TERM)} is ${result.entrance_face}`} ·
                drawn for {result.date_of_representation} · glass module {result.glass_module_in}″
              </p>
            )}
            {/* WP-12.0: which placement this plate was drawn on, and of what input. Every
                sheet in a set now takes `corpus._placed`'s one solve, so a reader comparing
                two plates of "the same house" can tell whether the INPUT differed rather
                than guessing — WP-11.8's J6, which the plan sheet has carried and the
                elevation and roof plates could not, because they were built on a placement
                of their own. */}
            {result.solver && (
              <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '4px 0 0' }}>
                {/* Three states, not two. A ternary here would have made an ABSENT engine
                    read as "searched", which is a definite claim about a placement nobody
                    can name — the one collapse this corpus refuses first. */}
                {/* WP-13.4: `sheet/engineClaim.js` is the app's ONE reader of a solver block and
                    this was a SECOND one -- a three-state ternary on the engine's NAME, which
                    cannot tell an OPTIMAL from a FEASIBLE truncation and so had no way to say
                    "not proved at the optimum". It reads the leaf now and prints its verdict
                    beside the engine, so this plate and the bench's caption cannot disagree
                    about one record. */}
                placed by {(() => {
                  const c = engineClaim(result.solver);
                  if (!c.engine) return 'an engine this plate does not name';
                  if (c.cp) return c.proved
                    ? 'proof (CP-SAT), proved at the optimum'
                    : `CP-SAT, NOT proved at the optimum — ${statusHead(c.status) || 'no status recorded'}`;
                  return 'search (hill-climb)';
                })()}
                {result.solver.drawn_by?.input_digest
                  ? ` · input ${result.solver.drawn_by.input_digest}` : ''}
                {/* `fallback` is the drawing route's own word for the same fact `solver.reason`
                    carries; both are printed because neither is derivable from the other here. */}
                {result.solver.fallback ? ` · fell back: ${result.solver.fallback}` : ''}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
