/* The phylogeny, on the ground.

   The tree answers "what descends from what". This answers "where did it arise, and where
   did it travel" — the same graph, the same edges, the same tradition hues, read
   geographically. Lineage arcs are the dependencies: an arc from an ancestor's hearth to a
   descendant's is a transmission of building practice across water or land.

   THREE HONESTIES, because a map is the easiest drawing to lie with:

   1. The corpus holds no coordinates. Every point here comes from src/data/gazetteer.js,
      which is interface furniture keyed on the prose region names the records DO carry.
      A style naming no region this gazetteer knows is listed as unlocated, never nudged
      onto a continent to keep the picture tidy.

   2. Precision is drawn, not hidden. Half the corpus names only a country — "England",
      "United States nationwide" — which is not a hearth, and a firm dot would invent one.
      Those are drawn as hollow hatched rings, the same hatch the product uses everywhere
      for "not judged", and the legend counts them.

   3. Coincident styles cluster rather than overlap. Twenty-five traditions sharing
      "England" is a fact about the records, not about England, so the mark carries the
      count and the panel names them.

   No tiles, no map library, no network. The basemap is a vendored public-domain outline
   drawn in the same hairline the drawing set uses. */
import React from 'react';
import { placeStyle, statesNoHearth } from '../../data/gazetteer.js';
import { COASTLINES } from '../../data/coastlines.js';
import { Eyebrow } from '../../components/Eyebrow.jsx';

/* Equirectangular, and deliberately so: it is the projection the coastline asset is
   stored in, it keeps the transform to two subtractions, and at this scale — a diagram of
   where traditions arose — an equal-area projection would buy accuracy nobody reads. */
const project = (lat, lon) => ({ x: lon, y: -lat });

/* The North Atlantic, which is where all five traditions are. The box is wide and short
   and the panel beside it is nearly square, so `meet` letterboxes it into extra ocean top
   and bottom — that is the honest trade: both coasts of the Atlantic have to be on screen
   at once for a transmission arc to mean anything. */
const HOME = { x: -114, y: -60, w: 134, h: 43 };
const MIN_W = 6, MAX_W = 300;

const PRECISION_NOTE = {
  locality: 'a place you could walk across',
  region: 'a named region, a hundred miles wide',
  country: 'a whole country — no hearth to place it at',
};

export function MapView({
  rows, edges, sel, compare, onPick, traditionHue, lit, carries, showClaims, rankFilter,
}) {
  const [view, setView] = React.useState(HOME);
  const [hover, setHover] = React.useState(null);
  const svgRef = React.useRef(null);
  const drag = React.useRef(null);

  /* Place every row once. rows already carries the rank filter the tree applies. */
  const { clusters, byId, unlocated, counts, abstract } = React.useMemo(() => {
    const cl = new Map();
    const by = {};
    const un = [];
    const c = { locality: 0, region: 0, country: 0 };
    // How many of the coarse marks are coarse because the corpus says so — a family or a
    // tradition is an abstraction over styles and has no birthplace, and two styles say in
    // their own hearth that they have none ("No design hearth", "Streetcar suburbs
    // nationwide"). Reporting those as a shortcoming of the drawing would be a lie about
    // the records.
    let abstract = 0;
    rows.forEach((r) => {
      // regions AND hearth: the prose is finer than the list, and reading only the list
      // put Craftsman in the middle of Kansas while its record said Pasadena (OQ 65).
      const p = placeStyle(r.regions, r.hearth);
      if (!p) { un.push(r); return; }
      c[p.precision] += 1;
      if (p.precision === 'country'
        && (r.rank === 'family' || r.rank === 'tradition' || statesNoHearth(r.hearth))) {
        abstract += 1;
      }
      const key = `${p.lat},${p.lon}`;
      if (!cl.has(key)) {
        cl.set(key, { key, ...p, ...project(p.lat, p.lon), members: [] });
      }
      const cluster = cl.get(key);
      cluster.members.push(r);
      by[r.id] = cluster;
      // A cluster is as precise as its most precise member.
      if (p.precision === 'locality') cluster.precision = 'locality';
    });
    return { clusters: [...cl.values()], byId: by, unlocated: un, counts: c, abstract };
  }, [rows]);

  /* Arcs, from the same edge set the tree draws, between placed endpoints. An edge whose
     ends share a hearth has nowhere to go on a map; it is counted, not faked. */
  const { arcs, sameHearth } = React.useMemo(() => {
    const out = [];
    let same = 0;
    edges.forEach((e, i) => {
      const a = byId[e.from], b = byId[e.to];
      if (!a || !b) return;
      if (a.key === b.key) { same += 1; return; }
      out.push({ i, e, a, b, carries: !!carries[e.type] });
    });
    return { arcs: out, sameHearth: same };
  }, [edges, byId, carries]);

  const zoom = (factor, cx, cy) => {
    setView((v) => {
      const w = Math.min(MAX_W, Math.max(MIN_W, v.w * factor));
      const h = w * (v.h / v.w);
      // keep the point under the cursor still
      const fx = (cx - v.x) / v.w, fy = (cy - v.y) / v.h;
      return { x: cx - fx * w, y: cy - fy * h, w, h };
    });
  };

  const toWorld = (ev) => {
    const svg = svgRef.current;
    if (!svg) return { x: 0, y: 0 };
    const r = svg.getBoundingClientRect();
    return {
      x: view.x + ((ev.clientX - r.left) / r.width) * view.w,
      y: view.y + ((ev.clientY - r.top) / r.height) * view.h,
    };
  };

  const onWheel = (ev) => {
    ev.preventDefault();
    const p = toWorld(ev);
    zoom(ev.deltaY > 0 ? 1.18 : 1 / 1.18, p.x, p.y);
  };

  const onPointerDown = (ev) => {
    drag.current = { start: toWorld(ev), view, moved: false, id: ev.pointerId };
    // NOT setPointerCapture. Capturing on the <svg> retargets the compatibility mouse events
    // and the subsequent `click` to the capture element (Pointer Events L3), so the click
    // never reached the <g> of the mark under the cursor and selecting a hearth was
    // impossible — while panning still worked, which is why it looked fine. An adversarial
    // audit caught it; the e2e walk loaded the map but never clicked a mark. Panning below
    // works off the pointermove stream and does not need capture inside one element.
  };
  const onPointerMove = (ev) => {
    if (!drag.current) return;
    drag.current.moved = true;
    const svg = svgRef.current;
    const r = svg.getBoundingClientRect();
    const dx = ((ev.clientX - r.left) / r.width) * view.w;
    const dy = ((ev.clientY - r.top) / r.height) * view.h;
    const { start, view: v0 } = drag.current;
    setView({ ...view, x: v0.x + (start.x - (v0.x + dx)), y: v0.y + (start.y - (v0.y + dy)) });
  };
  // A drag must not also select whatever mark it started on.
  const draggedRef = React.useRef(false);
  const onPointerUp = () => {
    draggedRef.current = !!(drag.current && drag.current.moved);
    drag.current = null;
  };
  const pickFromMap = (ev, id) => {
    if (draggedRef.current) { draggedRef.current = false; return; }
    onPick(ev, id);
  };

  /* Clicking a cluster used to select `members[0]` and nothing else, so of the 25 styles
     sharing the England mark, 24 were unreachable from the map — every click re-selected the
     same one and looked like a dead control. Clicking now steps to the next member, so a
     cluster is a way in to all of them; the hover panel names them so the order is visible
     rather than guessed at. */
  const nextInCluster = (c) => {
    if (c.members.length === 1) return c.members[0].id;
    const at = c.members.findIndex((m) => m.id === sel);
    return c.members[(at + 1) % c.members.length].id;
  };

  // A degree is this many user units; marks are sized in degrees so they hold their
  // screen size as the view scales.
  const u = view.w / 100;
  const rFor = (cluster) => {
    const base = cluster.precision === 'country' ? 1.5 : cluster.precision === 'region' ? 1.15 : 0.85;
    return (base + Math.min(1.6, Math.sqrt(cluster.members.length) * 0.32)) * u;
  };

  const selCluster = byId[sel];

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0,
      position: 'relative' }}>
      <svg ref={svgRef} role="img"
        aria-label={`${clusters.length} hearths carrying ${rows.length - unlocated.length} styles, `
          + `with ${arcs.length} lineage arcs drawn between them`}
        viewBox={`${view.x} ${view.y} ${view.w} ${view.h}`}
        onWheel={onWheel} onPointerDown={onPointerDown} onPointerMove={onPointerMove}
        onPointerUp={onPointerUp} onPointerCancel={onPointerUp}
        style={{ flex: 1, minHeight: 0, width: '100%', background: 'var(--paper-lit)',
          cursor: drag.current ? 'grabbing' : 'grab', touchAction: 'none' }}>

        {/* the graticule, every ten degrees — a plate, not a chart */}
        <g stroke="var(--rule-soft)" strokeWidth={0.06 * u} fill="none" vectorEffect="non-scaling-stroke">
          {Array.from({ length: 19 }, (_, i) => -90 + i * 10).map((lat) => (
            <line key={'p' + lat} x1={-180} y1={-lat} x2={180} y2={-lat} />
          ))}
          {Array.from({ length: 37 }, (_, i) => -180 + i * 10).map((lon) => (
            <line key={'m' + lon} x1={lon} y1={-90} x2={lon} y2={90} />
          ))}
        </g>

        {/* land */}
        <g fill="var(--paper-deep)" stroke="var(--rule)" strokeWidth={0.7}
          vectorEffect="non-scaling-stroke" strokeLinejoin="round">
          {COASTLINES.map((d, i) => <path key={i} d={d} />)}
        </g>

        {/* lineage arcs, under the marks. Same semantics as the tree: a cascade-carrying
            edge is solid and heavier, a claim is dashed and lighter. */}
        <g fill="none" vectorEffect="non-scaling-stroke">
          {arcs.map(({ i, e, a, b, carries: cc }) => {
            const isLit = lit(e.from) && lit(e.to);
            if (!isLit) return null;
            // A quadratic bowed perpendicular to the run — arcs that would otherwise lie
            // on top of one another separate, and the bow reads as a crossing.
            const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
            const dx = b.x - a.x, dy = b.y - a.y;
            const len = Math.hypot(dx, dy) || 1;
            const bow = Math.min(len * 0.22, 9);
            const cx = mx - (dy / len) * bow, cy = my + (dx / len) * bow;
            return (
              <path key={i} d={`M${a.x},${a.y} Q${cx},${cy} ${b.x},${b.y}`}
                stroke={cc ? 'var(--edge-carries)' : 'var(--edge-claims)'}
                strokeWidth={cc ? 1.5 : 0.8}
                strokeDasharray={cc ? 'none' : '3 3'}
                opacity={cc ? 0.75 : 0.5} />
            );
          })}
        </g>

        {/* hearths */}
        <g>
          {clusters.map((c) => {
            const anyLit = c.members.some((m) => lit(m.id));
            const holdsSel = c.members.some((m) => m.id === sel || m.id === compare);
            const hue = traditionHue(c.members[0]);
            const r = rFor(c);
            const coarse = c.precision === 'country';
            return (
              <g key={c.key} onMouseEnter={() => setHover(c)} onMouseLeave={() => setHover(null)}
                onClick={(ev) => pickFromMap(ev, nextInCluster(c))}
                style={{ cursor: 'pointer' }}>
                {/* A country-precision mark is hollow and hatched: the record named a
                    nation, not a hearth, and a filled dot would claim one. */}
                <circle cx={c.x} cy={c.y} r={r}
                  fill={coarse ? 'none' : hue}
                  stroke={holdsSel ? 'var(--ink)' : hue}
                  strokeWidth={holdsSel ? 1.8 : (coarse ? 1.2 : 0.7)}
                  strokeDasharray={coarse ? '2 1.6' : 'none'}
                  vectorEffect="non-scaling-stroke"
                  opacity={holdsSel ? 1 : (anyLit ? 0.85 : 0.28)} />
                {c.members.length > 1 && (
                  <text x={c.x} y={c.y + r * 0.36} textAnchor="middle"
                    style={{ font: `${r * 0.95}px var(--mono)`, fill: coarse ? 'var(--ink-2)' : 'var(--paper)',
                      pointerEvents: 'none', opacity: anyLit ? 1 : 0.45 }}>
                    {c.members.length}
                  </text>
                )}
              </g>
            );
          })}
        </g>

        {/* the selected hearth, named on the plate */}
        {selCluster && (
          <text x={selCluster.x} y={selCluster.y - rFor(selCluster) - 0.9 * u} textAnchor="middle"
            style={{ font: `${1.5 * u}px var(--display)`, fill: 'var(--ink)', pointerEvents: 'none' }}>
            {selCluster.region}
          </text>
        )}
      </svg>

      {/* the legend, which is mostly a statement of what the marks do not know */}
      <div style={{ flex: 'none', borderTop: '1px solid var(--rule)', background: 'var(--paper)',
        padding: '9px 14px 11px', display: 'flex', gap: 26, alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <div>
          <Eyebrow style={{ marginBottom: 6 }}>how firmly each is placed</Eyebrow>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            {['locality', 'region', 'country'].map((p) => (
              <span key={p} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                <svg width="13" height="13" aria-hidden="true">
                  <circle cx="6.5" cy="6.5" r="4.6" fill={p === 'country' ? 'none' : 'var(--ink-3)'}
                    stroke="var(--ink-3)" strokeWidth={p === 'country' ? 1.3 : 0.7}
                    strokeDasharray={p === 'country' ? '2 1.6' : 'none'} />
                </svg>
                <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-2)' }}>
                  {counts[p]} {p}
                </span>
                <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>
                  · {PRECISION_NOTE[p]}
                </span>
              </span>
            ))}
          </div>
        </div>

        <div style={{ flex: 1, minWidth: 260 }}>
          <Eyebrow style={{ marginBottom: 6 }}>what this drawing does not know</Eyebrow>
          <p style={{ font: 'var(--fw-reg) 12px/1.5 var(--body)', color: 'var(--ink-3)',
            margin: 0, maxWidth: '74ch' }}>
            The corpus records where a style arose in prose, not coordinates. These points
            come from a gazetteer in the interface, keyed on the region and hearth names the
            records use — they are accurate to the size of the thing named and no better,
            and none of them is a source.
            {abstract > 0 && (
              <> {abstract} of the {counts.country} country-wide marks are country-wide
                because the corpus says so rather than because this drawing failed: a family
                or a tradition is an abstraction over styles and has no birthplace, and a
                style whose hearth reads "no design hearth" is telling you something true.</>
            )}
            {sameHearth > 0 && (
              <> {sameHearth} lineage {sameHearth === 1 ? 'edge is' : 'edges are'} not drawn:
                both ends share a hearth, so the transmission happened inside one place and
                has no line to occupy.</>
            )}
            {unlocated.length > 0 && (
              <> {unlocated.length} {unlocated.length === 1 ? 'style names' : 'styles name'} no
                region the gazetteer knows, and {unlocated.length === 1 ? 'is' : 'are'} listed
                below rather than placed: {unlocated.map((r) => r.id).join(', ')}.</>
            )}
          </p>
        </div>

        <div style={{ flex: 'none', display: 'flex', gap: 10, alignItems: 'center' }}>
          <button type="button" onClick={() => setView(HOME)}
            style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)',
              borderBottom: '1px solid var(--link-underline)' }}>reset the view</button>
          <span style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)' }}>drag · scroll to zoom</span>
        </div>
      </div>

      {/* what is under the cursor — anchored inside the map, not to the window, or it
          sits on top of the left rail */}
      {hover && (
        <div style={{ position: 'absolute', left: 12, top: 12, zIndex: 30, maxWidth: 300,
          background: 'var(--paper)', border: '1px solid var(--rule)', padding: '9px 11px',
          pointerEvents: 'none' }}>
          <Eyebrow tone="secondary" as="span">{hover.region}</Eyebrow>
          <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', margin: '3px 0 6px' }}>
            {hover.precision} · {PRECISION_NOTE[hover.precision]}
          </div>
          {hover.members.slice(0, 9).map((m) => (
            <div key={m.id} style={{ font: 'var(--fw-reg) 12.5px/1.45 var(--body)', color: 'var(--ink-2)' }}>
              {m.name}
            </div>
          ))}
          {hover.members.length > 9 && (
            <div style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', marginTop: 3 }}>
              and {hover.members.length - 9} more
            </div>
          )}
        </div>
      )}
    </div>
  );
}
