/* THE WALL-DATUM PLATE: A PACK'S ASSEMBLIES DRAWN FROM THE RECORD (WP-14.9, PRD §I.6).

   Lucas read `trim-classical` on the Proportions surface and found "a bunch of text": the pack
   has three wall sections and three casings, seventy-odd profiled members, and the page drew
   none of them, because the only plate it had was the order stack. This is the other plate —
   every pack whose `drawing` is `"assemblies"` — and it is built to four refusals.

   IT CONSTRUCTS NOTHING. Each band is a face the server served (`build/profiles.py`, in model
   inches from the wall plane, y up) and it reaches the page as that face's own `path` string,
   placed by ONE `translate(…) scale(k, −k)` on its parent group — `OrderPlate`'s idiom. There is
   no arc arithmetic, no sweep flag and no curve built here: JavaScript does not know what a cyma
   is (OQ 83), and `test_grammar_agreement.py` lists this file among the surfaces that must not
   learn. The number of `path[data-asm]` it draws is the number of faces served, whatever that
   number is.

   IT WRITES NO WORD A GLOSSARY RECORD SHOULD. The in-frame key's three words are the records
   `member`, `wall-plane` and `part` (through `wordOf`, since a `Term` is a button and cannot sit
   in an SVG), the same three stand as `Term`s over the numeral key, and the foot line is the two
   records `figure-drawn-from-record` and `figure-drawn-upright`. The member names and heights on
   the leaders are the payload's, in the engine's own notation (`feetInches16`).

   IT DRAWS WHAT THE RECORD HOLDS AND NOTHING THE RECORD HOLDS ONLY AS PROSE: every assembly
   upright from the wall plane (a casing is measured ACROSS its face, and the pack says so only in
   a member note — `oq/casings-are-measured-across-and-drawn-upright`), and no 4 + 12 + 3 zone
   dimension string, because the zones are an invariant sentence and not a structure a boundary
   can be read from. Both refusals are said on the page, by the foot line and by the page.

   IT LAYS OUT NOTHING ITSELF. `plate/assemblyLayout.js` decides the frames and their scale,
   `plate/assemblyPlan.js` every pixel inside a frame (leaders, labels, numerals, ticks, the
   scale bar, the key) — both pure and driven under `node --test`. This file measures the real
   face (`sheet/label.js`), measures the pane, and draws. Each frame sits in its own loupe
   (`PlateViewer`), because a drawing the reader cannot magnify is a drawing whose dimensions do
   not exist. */
import React from 'react';
import { PlateViewer } from './PlateViewer.jsx';
import { Term } from './Term.jsx';
import { Eyebrow } from './Eyebrow.jsx';
import { useGlossary } from '../api/useGlossary.js';
import { wordOf } from '../glossary/termView.js';
import { fitLine, useFontMetrics } from '../sheet/label.js';
import { assemblyLayout } from '../plate/assemblyLayout.js';
import { planFrame, PAD_X, LINE_PX, TITLE_FONT_PX } from '../plate/assemblyPlan.js';
import { assemblyWords } from '../proportions/page.js';
import { feetInches16 } from '../fmt.js';

/* The height every frame is scaled to fill, and what the loupe's frame and scrollbar take from
   the pane's width. Both are pixels of the page, never inches of the building. */
const PLATE_H = 520;
const VIEWER_INSET = 22;

/* The real face at a size, in px: `fitLine` with an unbounded box sets the line at exactly the
   size asked, so its width is the measured advance. One measurement for the plan and the page. */
const measure = (text, px) => fitLine(String(text), 1e9, { preferred: px, min: px, track: 0 }).width;

const INK = { fill: 'var(--ink)' };
const INK2 = { fill: 'var(--ink-2)' };

function FrameSvg({ plan, name, hatchId }) {
  const titleWords = plan.items.map((it) => assemblyWords(it.id)).join(', ');
  return (
    <svg role="img" data-plate={plan.index} viewBox={`0 0 ${plan.width} ${plan.height}`}
      width="100%" style={{ display: 'block', background: 'var(--paper-lit)' }}>
      <title>{`${name}: ${titleWords}`}</title>
      <defs>
        <pattern id={hatchId} patternUnits="userSpaceOnUse" width="5" height="5"
          patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="5" vectorEffect="non-scaling-stroke"
            style={{ stroke: 'var(--hair)', strokeWidth: 0.8 }} />
        </pattern>
      </defs>
      {plan.items.map((it) => (
        <g key={it.id} data-item={it.id}>
          {/* the nominal wall behind the plane: interface furniture, not a record of any wall */}
          <rect data-furniture="wall-strip" aria-hidden="true" x={it.strip.x} y={it.strip.y}
            width={it.strip.width} height={it.strip.height}
            style={{ fill: `url(#${hatchId})`, stroke: 'none' }} />
          <g transform={it.transform}>
            {it.bands.map((b) => (
              <path key={b.member} data-asm={b.asm} data-member={b.member}
                data-unconstructed={b.unconstructed ? '' : undefined} d={b.d}
                vectorEffect="non-scaling-stroke"
                style={{ fill: 'var(--paper-lit)', stroke: 'var(--ink)', strokeWidth: 0.9,
                  strokeDasharray: b.unconstructed ? '3 2' : undefined }}>
                <title>{`${b.name} · ${feetInches16(b.heightIn)}`}</title>
              </path>
            ))}
          </g>
          {/* the wall plane every projection is measured from */}
          <line data-wall-plane="" x1={it.chain.x} y1={it.chain.y0} x2={it.chain.x} y2={it.chain.y1}
            vectorEffect="non-scaling-stroke"
            style={{ stroke: 'var(--ink-2)', strokeWidth: 0.7, strokeDasharray: '12 3 2 3' }} />
          {it.ticks.map((y, j) => (
            <line key={j} data-part-tick="" x1={it.chain.x - Math.min(6, it.strip.width)} y1={y}
              x2={it.chain.x} y2={y} vectorEffect="non-scaling-stroke"
              style={{ stroke: 'var(--draw-dim)', strokeWidth: 0.7 }} />
          ))}
          <ItemTitle it={it} />
        </g>
      ))}
      {plan.labels.map((l) => (
        <g key={`${l.asm}.${l.member}`} data-label={l.kind} data-for={`${l.asm}.${l.member}`}>
          <polyline data-leader="" points={l.leader.map((p) => p.join(',')).join(' ')}
            vectorEffect="non-scaling-stroke"
            style={{ fill: 'none', stroke: 'var(--draw-dim)', strokeWidth: 0.6 }} />
          <LabelText l={l} />
        </g>
      ))}
      <ScaleBar scale={plan.scale} />
      <Legend legend={plan.legend} />
    </svg>
  );
}

function ItemTitle({ it }) {
  const text = assemblyWords(it.id).toUpperCase();
  const fit = fitLine(text, Math.max(1, it.title.maxW), { preferred: TITLE_FONT_PX, min: 6, track: 0.14 });
  return (
    <text data-title={it.id} x={it.title.x} y={it.title.y}
      style={{ ...INK2, font: `${fit.size}px var(--serif)`, letterSpacing: `${fit.track}px` }}>
      {text}
    </text>
  );
}

/* One label: a name and its height, or a numeral the key below names. `y` is the label's
   centre, `h` its height: each line sits in its own LINE_PX band. */
function LabelText({ l }) {
  const top = l.y - l.h / 2;
  return (
    <text data-label-text="" x={l.x} style={{ font: `${l.font}px var(--serif)` }}>
      {l.lines.map((line, i) => (
        <tspan key={i} x={l.x} y={top + (i + 0.5) * LINE_PX + l.font * 0.34}
          style={i === 0 ? INK : INK2}>{line}</tspan>
      ))}
    </text>
  );
}

function ScaleBar({ scale }) {
  const { x, y, barPx, words } = scale;
  return (
    <g data-scale-bar="">
      <line x1={x} y1={y} x2={x + barPx} y2={y} vectorEffect="non-scaling-stroke"
        style={{ stroke: 'var(--ink-2)', strokeWidth: 0.9 }} />
      {[x, x + barPx].map((xx, i) => (
        <line key={i} x1={xx} y1={y - 4} x2={xx} y2={y + 4} vectorEffect="non-scaling-stroke"
          style={{ stroke: 'var(--ink-2)', strokeWidth: 0.9 }} />
      ))}
      <text x={x + barPx + 6} y={y + 3.5} style={{ ...INK2, font: '10.5px var(--serif)' }}>{words}</text>
    </g>
  );
}

function Legend({ legend }) {
  return (
    <g data-legend="">
      {legend.entries.map((e) => (
        <g key={e.kind} data-legend-entry={e.kind}>
          {e.kind === 'member' && (
            <rect x={e.x} y={e.y - 5} width={e.markW} height={8} vectorEffect="non-scaling-stroke"
              style={{ fill: 'var(--paper-lit)', stroke: 'var(--ink)', strokeWidth: 0.9 }} />
          )}
          {e.kind === 'chain' && (
            <line x1={e.x} y1={e.y - 1} x2={e.x + e.markW} y2={e.y - 1} vectorEffect="non-scaling-stroke"
              style={{ stroke: 'var(--ink-2)', strokeWidth: 0.7, strokeDasharray: '12 3 2 3' }} />
          )}
          {e.kind === 'tick' && (
            <line x1={e.x} y1={e.y - 1} x2={e.x + e.markW} y2={e.y - 1} vectorEffect="non-scaling-stroke"
              style={{ stroke: 'var(--draw-dim)', strokeWidth: 0.7 }} />
          )}
          {e.word && (
            <text x={e.wordX} y={e.y + 2.5} style={{ ...INK2, font: '10.5px var(--serif)' }}>{e.word}</text>
          )}
        </g>
      ))}
    </g>
  );
}

/* The numeral key under a frame, grouped by assembly: every member the frame gave a numeral,
   and every member a side-by-side assembly states and does not draw. */
function NumeralKey({ plan }) {
  const groups = [];
  for (const k of plan.key) {
    let g = groups.find((x) => x.asm === k.asm);
    if (!g) { g = { asm: k.asm, rows: [] }; groups.push(g); }
    g.rows.push(k);
  }
  if (!groups.length) return null;
  return (
    <div data-numeral-key={plan.index} style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 26px',
      margin: '8px 2px 0' }}>
      {groups.map((g) => (
        <div key={g.asm} style={{ minWidth: 180 }}>
          <Eyebrow as="div" style={{ marginBottom: 3 }}>{assemblyWords(g.asm)}</Eyebrow>
          {g.rows.map((r) => (
            <div key={r.member} data-key-row={r.numeral ?? 'undrawn'}
              style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', display: 'flex', gap: 8 }}>
              <span style={{ minWidth: 18, textAlign: 'right', color: 'var(--ink)' }}>{r.numeral ?? '–'}</span>
              <span style={{ fontFamily: 'var(--serif)', color: 'var(--ink)' }}>{r.name}</span>
              <span>{r.words}</span>
              {r.drawn === false && <span>· stands beside a drawn member; not drawn</span>}
              {r.unconstructed && <span>· <Term id="figure-drawn-from-record">drawn plain</Term></span>}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

export function AssemblyPlate({ data }) {
  useFontMetrics();
  const glossary = useGlossary();
  const hatchBase = React.useId().replace(/[^A-Za-z0-9_-]/g, '');
  const ref = React.useRef(null);
  const [paneW, setPaneW] = React.useState(0);

  React.useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return undefined;
    const read = () => setPaneW(el.clientWidth);
    read();
    if (typeof ResizeObserver === 'undefined') return undefined;
    const ro = new ResizeObserver(read);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const assemblies = Array.isArray(data && data.assemblies) ? data.assemblies : [];
  const byId = React.useMemo(() => new Map(assemblies.map((a) => [a.id, a])), [assemblies]);
  const box = paneW > 0
    ? { widthPx: Math.max(160, paneW - VIEWER_INSET - 2 * PAD_X), heightPx: PLATE_H } : null;
  const layout = assemblyLayout(assemblies, { box });
  const lookup = glossary.status === 'ready' ? glossary.lookup : null;
  const legendWords = lookup
    ? { member: wordOf(lookup, 'member'), wallPlane: wordOf(lookup, 'wall-plane'), part: wordOf(lookup, 'part') }
    : {};
  const plans = box
    ? layout.frames.map((f) => planFrame(f, byId, { partIn: data.part_in, measure, legendWords })).filter(Boolean)
    : [];

  return (
    <div ref={ref} data-assembly-plate={data.pack} style={{ minWidth: 0 }}>
      {plans.map((plan) => (
        <div key={plan.index} data-assembly-frame={plan.index} style={{ marginBottom: 18 }}>
          <PlateViewer label={plan.items.map((it) => assemblyWords(it.id)).join(' · ')}
            height={`${Math.ceil(plan.height) + 6}px`}>
            <FrameSvg plan={plan} name={data.name} hatchId={`hatch-${hatchBase}-${plan.index}`} />
          </PlateViewer>
          <div data-key-terms="" style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '6px 2px 0' }}>
            <Term id="member" /> · <Term id="wall-plane" /> · <Term id="part" />
          </div>
          <NumeralKey plan={plan} />
        </div>
      ))}
      {layout.unplaced.length > 0 && (
        <ul data-unplaced="" style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '4px 0 10px' }}>
          {layout.unplaced.map((u) => (
            <li key={`${u.id}-${u.index}`}>{u.id ? assemblyWords(u.id) : `#${u.index}`}: not drawn — {u.reason}</li>
          ))}
        </ul>
      )}
      <p data-foot="" style={{ font: 'italic var(--fw-reg) 13px/1.5 var(--serif)', color: 'var(--ink-2)',
        margin: '4px 2px 0' }}>
        <Term id="figure-drawn-from-record" /> · <Term id="figure-drawn-upright" />
      </p>
    </div>
  );
}

export default AssemblyPlate;
