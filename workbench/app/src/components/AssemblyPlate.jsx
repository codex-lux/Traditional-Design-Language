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

   IT WRITES NO WORD A GLOSSARY RECORD SHOULD. The in-frame key's words are the records
   `member`, `wall-plane`, `part` and `zone` (through `wordOf`, since a `Term` is a button and
   cannot sit in an SVG), the same stand as `Term`s over the numeral key, and each frame's foot
   line is the records `figure-drawn-from-record` and, by what the frame holds,
   `figure-drawn-upright` and `figure-drawn-turned`. The member names and heights on the leaders
   are the payload's, in the engine's own notation (`feetInches16`).

   IT DRAWS WHAT THE RECORD HOLDS, AT THE PACK'S WORD (WP-14.24). Until tranche 2 a casing's
   axis and a wall's zones were in the pack only as prose, so this plate drew every assembly
   upright and no zone string, and said so. The pack now states both as data
   (`oq/casings-are-measured-across-and-drawn-upright`, ruled 25 Sep 2026; WP-14.18 declared
   them): an assembly declaring `axis: "across-from-the-jamb"` is drawn TURNED, by one `rotate`
   in `plate/assemblyPlan.js`, and one declaring `zones` carries its zone ticks and its zone
   string, the differences of its served `to_parts`. An assembly declaring neither is drawn
   upright with no string, and the frame's foot says which it is: "drawn upright" appears only
   where an assembly rises up the wall, "drawn turned" only where one runs across from the jamb.

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
import { planFrame, planThumb, PAD_X, LINE_PX, TITLE_FONT_PX } from '../plate/assemblyPlan.js';
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
        <g key={it.id} data-item={it.id} data-axis={it.turned ? 'turned' : 'upright'}>
          {/* the nominal wall behind the plane: interface furniture, not a record of any wall */}
          <rect data-furniture="wall-strip" aria-hidden="true" x={it.strip.x} y={it.strip.y}
            width={it.strip.width} height={it.strip.height}
            style={{ fill: `url(#${hatchId})`, stroke: 'none' }} />
          {/* the bands, measured as drawn: this group has no transform of its own, so its box is
              the served faces' box after the plan's one translate, rotate and scale */}
          <g data-bands={it.id}>
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
          </g>
          {/* the wall plane every projection is measured from */}
          <line data-wall-plane="" x1={it.chain.x1} y1={it.chain.y1} x2={it.chain.x2} y2={it.chain.y2}
            vectorEffect="non-scaling-stroke"
            style={{ stroke: 'var(--ink-2)', strokeWidth: 0.7, strokeDasharray: '12 3 2 3' }} />
          {it.ticks.map(([x1, y1, x2, y2], j) => (
            <line key={j} data-part-tick="" x1={x1} y1={y1} x2={x2} y2={y2}
              vectorEffect="non-scaling-stroke"
              style={{ stroke: 'var(--draw-dim)', strokeWidth: 0.7 }} />
          ))}
          {it.zones && <ZoneMarks it={it} />}
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

/* The pack's own division of an assembly: a dimension line along the wall behind the strip, a
   tick at every boundary, each zone's figure in parts beside its run (its name and inches on
   hover), and the zone string under the assembly -- in parts, then in inches. Every figure is
   `zoneString`'s reading of the served `to_parts`; nothing here computes one. */
function ZoneMarks({ it }) {
  const z = it.zones;
  const dim = { stroke: 'var(--ink-2)', strokeWidth: 0.7 };
  return (
    <g data-zones={it.id}>
      {z.line && (
        <line data-zone-line="" x1={z.line.x1} y1={z.line.y1} x2={z.line.x2} y2={z.line.y2}
          vectorEffect="non-scaling-stroke" style={dim} />
      )}
      {z.ticks.map(([x1, y1, x2, y2], j) => (
        <line key={j} data-zone-tick="" x1={x1} y1={y1} x2={x2} y2={y2}
          vectorEffect="non-scaling-stroke" style={dim} />
      ))}
      {z.figures.map((f, j) => (
        <text key={j} data-zone-figure={f.run.parts} x={f.x} y={f.y} textAnchor={f.anchor}
          style={{ ...INK2, font: `${f.font}px var(--serif)` }}>
          <title>{[f.run.name, f.run.parts, f.run.inches].filter(Boolean).join(' · ')}</title>
          {f.run.parts}
        </text>
      ))}
      {z.string && (
        <text data-zone-string={z.parts} x={z.string.x} y={z.string.y}
          style={{ ...INK, font: `${z.string.font}px var(--serif)` }}>{z.parts}</text>
      )}
      {z.inchesLine && (
        <text data-zone-inches={z.inches} x={z.inchesLine.x} y={z.inchesLine.y}
          style={{ ...INK2, font: `${z.inchesLine.font}px var(--serif)` }}>{z.inches}</text>
      )}
    </g>
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
          {e.kind === 'zone' && (
            <g>
              <line x1={e.x} y1={e.y - 1} x2={e.x + e.markW} y2={e.y - 1} vectorEffect="non-scaling-stroke"
                style={{ stroke: 'var(--ink-2)', strokeWidth: 0.7 }} />
              {[e.x, e.x + e.markW].map((xx, i) => (
                <line key={i} x1={xx} y1={e.y - 4} x2={xx} y2={e.y + 2} vectorEffect="non-scaling-stroke"
                  style={{ stroke: 'var(--ink-2)', strokeWidth: 0.7 }} />
              ))}
            </g>
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
    ? { member: wordOf(lookup, 'member'), wallPlane: wordOf(lookup, 'wall-plane'), part: wordOf(lookup, 'part'),
      zone: wordOf(lookup, 'zone') }
    : {};
  const plans = box
    ? layout.frames.map((f) => planFrame(f, byId, { partIn: data.part_in, measure, legendWords })).filter(Boolean)
    : [];

  return (
    <div ref={ref} data-assembly-plate={data.pack} style={{ minWidth: 0 }}>
      {plans.map((plan) => (
        <div key={plan.index} data-assembly-frame={plan.index} style={{ marginBottom: 18 }}>
          {/* The loupe's label is short on purpose: `PlateViewer` sets it `flex: none` in one
              row with its zoom keys, and the three assembly names pushed −, +, fit and 1:1 off
              the pane at 1440 px. The names are on the plate, over each section. */}
          <PlateViewer label="the plate"
            height={`${Math.ceil(plan.height) + 6}px`}>
            <FrameSvg plan={plan} name={data.name} hatchId={`hatch-${hatchBase}-${plan.index}`} />
          </PlateViewer>
          <div data-key-terms="" style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '6px 2px 0' }}>
            <Term id="member" /> · <Term id="wall-plane" /> · <Term id="part" />
            {plan.items.some((it) => it.zones) && <> · <Term id="zone" /></>}
          </div>
          <NumeralKey plan={plan} />
          <FrameFoot plan={plan} />
        </div>
      ))}
      {layout.unplaced.length > 0 && (
        <ul data-unplaced="" style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)', margin: '4px 0 10px' }}>
          {layout.unplaced.map((u) => (
            <li key={`${u.id}-${u.index}`}>{u.id ? assemblyWords(u.id) : `#${u.index}`}: not drawn — {u.reason}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

/* A frame's foot: drawn from the record, and how each of its assemblies runs on the sheet —
   "drawn upright" only where one rises up the wall (no axis declared, or `up-the-wall`), "drawn
   turned" only where one runs across from the jamb. Both are glossary records; `data-captions`
   names which, for the walk. */
function FrameFoot({ plan }) {
  const { upright, turned } = plan.orientations;
  const captions = [upright && 'upright', turned && 'turned'].filter(Boolean).join(' ');
  return (
    <p data-foot={plan.index} data-captions={captions}
      style={{ font: 'italic var(--fw-reg) 13px/1.5 var(--serif)', color: 'var(--ink-2)', margin: '4px 2px 0' }}>
      <Term id="figure-drawn-from-record" />
      {upright && <> · <Term id="figure-drawn-upright" /></>}
      {turned && <> · <Term id="figure-drawn-turned" /></>}
    </p>
  );
}

/* A PACK'S FIRST ASSEMBLY, SMALL, FOR THE PACK INDEX (WP-14.24, PRD tranche 2 §C.9, §0.3 default
   6). `thumb` is the list route's (`corpus._pack_thumb`): the first assembly the pack's own plate
   draws, at the wall datum, served whole. `planThumb` fits it in the box under the same one
   transform the plate uses, turned where the record turns it, and this draws its paths and
   nothing else -- no curve, no word but the assembly's own id. A pack whose list row carries no
   thumbnail (a stacked order, drawn on its column's axis; or a pack with no assembly) gets none. */
export const THUMB_W = 40;
export const THUMB_H = 52;

export function AssemblyThumb({ pack, thumb }) {
  const asm = thumb && typeof thumb === 'object'
    ? { id: thumb.assembly, height_in: thumb.height_in, axis: thumb.axis, geometry: thumb.geometry } : null;
  const plan = asm ? planThumb(asm, { widthPx: THUMB_W, heightPx: THUMB_H }) : null;
  if (!plan) return null;
  return (
    <svg role="img" data-thumb={pack} data-thumb-assembly={thumb.assembly}
      data-axis={plan.turned ? 'turned' : 'upright'} viewBox={`0 0 ${THUMB_W} ${THUMB_H}`}
      width={THUMB_W} height={THUMB_H}
      style={{ display: 'block', flex: 'none', background: 'var(--paper-lit)', border: '1px solid var(--rule-soft)' }}>
      <title>{assemblyWords(thumb.assembly)}</title>
      <g data-thumb-bands="">
        <g transform={plan.transform}>
          {plan.paths.map((p) => (
            <path key={p.member} data-thumb-member={p.member} d={p.d} vectorEffect="non-scaling-stroke"
              style={{ fill: 'var(--paper-lit)', stroke: 'var(--ink)', strokeWidth: 0.6 }} />
          ))}
        </g>
      </g>
    </svg>
  );
}

export default AssemblyPlate;
