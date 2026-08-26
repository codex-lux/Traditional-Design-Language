/* Surface ⑧ — the Drawing Set, live. Elevation, section, bearing diagram, roof plan
   and the solved plan — siblings of the workbench sheet, generated from the same
   record by the same build/ pipeline the CLI drives, re-tokenized to the Drawn
   Language (re-rendered, never redrawn). The elevation carries WP-3.2's disclosure
   permanently and without embarrassment. */
import React from 'react';
import { planDoc } from '../state/planDoc.js';
import { Eyebrow } from '../components/Eyebrow.jsx';
import { FilterStrip, Chip, ChipGroup, ActionChip } from '../Chrome.jsx';
import { PlateViewer } from '../components/PlateViewer.jsx';

const KINDS = [
  { id: 'elevation', label: 'front elevation' },
  { id: 'section', label: 'section' },
  { id: 'bearing', label: 'bearing lines' },
  { id: 'roof', label: 'roof plan' },
  { id: 'plan', label: 'solved plan' },
];

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
  const [kind, setKind] = React.useState('elevation');
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [busy, setBusy] = React.useState(false);
  const cache = React.useRef({});

  React.useEffect(() => { cache.current = {}; }, [plan]);

  React.useEffect(() => {
    if (!plan) return;
    if (cache.current[kind]) { setResult(cache.current[kind]); setError(null); return; }
    setBusy(true); setError(null); setResult(null);
    fetch(`/api/drawings/${kind}`, {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ plan }),
    }).then(async (r) => {
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail?.error || 'generation refused');
      cache.current[kind] = j;
      setResult(j);
    }).catch((e) => setError(String(e.message || e)))
      .finally(() => setBusy(false));
  }, [plan, kind]);

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
    a.download = `${plan.id}-${kind}.svg`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, flex: 1 }}>
      <FilterStrip right={
        <span style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>{plan.id} · {plan.style}</span>
          <ActionChip affix="↓" onClick={download}>download SVG</ActionChip>
        </span>
      }>
        <Eyebrow as="span">sheet</Eyebrow>
        <ChipGroup label="sheet">
          {KINDS.map((k) => (
            <Chip key={k.id} radio on={kind === k.id} onClick={() => setKind(k.id)}>{k.label}</Chip>
          ))}
        </ChipGroup>
      </FilterStrip>

      <div style={{ flex: 1, overflow: 'auto', minHeight: 0, padding: '22px 26px 34px' }}>
        {busy && <p style={{ font: 'var(--type-body)', color: 'var(--ink-3)' }}>generating from the record…</p>}
        {error && (
          <div style={{ border: '1px solid var(--rule)', borderLeft: '2px solid var(--refusal)',
            background: 'var(--paper-deep)', padding: '12px 14px', maxWidth: 640 }}>
            <Eyebrow tone="secondary" style={{ marginBottom: 6 }}>the generator refused</Eyebrow>
            <p style={{ font: 'var(--fw-reg) 13.5px/1.6 var(--body)', color: 'var(--ink)', margin: 0 }}>
              {error}
            </p>
            <p style={{ font: 'var(--fw-reg) 12.5px/1.55 var(--body)', color: 'var(--ink-3)', margin: '7px 0 0' }}>
              A refusal is content: this record does not carry what the {kind} generator
              needs, and it says so rather than inventing it.
            </p>
          </div>
        )}
        {result?.svg && (
          <div style={{ maxWidth: 1180 }}>
            <PlateViewer label={'the ' + kind} height="clamp(420px, 74vh, 960px)">
            <div style={{ background: 'var(--paper)', border: '1px solid var(--ink-2)',
              boxShadow: 'var(--shadow-plate)', padding: '16px 18px 10px' }}>
              <div dangerouslySetInnerHTML={{ __html: result.svg.replace(
                /<svg /, '<svg style="max-width:100%;height:auto" ') }} />
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
              <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', margin: '10px 0 0' }}>
                {result.relaxations.count} cut(s) off the bay line
                {result.relaxations.count ? ` · worst ${result.relaxations.max_off_grid_ft} ft` : ''}
              </p>
            )}
            {kind === 'elevation' && result.date_of_representation && (
              <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-3)', margin: '10px 0 0' }}>
                drawn for {result.date_of_representation} · glass module {result.glass_module_in}″ ·
                entrance faces {result.entrance_face}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
