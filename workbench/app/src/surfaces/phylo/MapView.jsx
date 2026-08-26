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
   drawn in the same hairline the drawing set uses.

   AND IT SHARPENS AS YOU ZOOM, which until WP-5.7 it did not. There was one outline —
   Natural Earth 110m, simplified at 0.55 degrees — held at every scale, so magnifying the
   plate magnified its corners and a coastline became a run of visible facets. There are
   three now (`coastTiers.js`), the map fetches the one its scale can honestly show, and
   while a finer one is in flight it says what is actually on the plate rather than
   letting a facet pass for a shore. The graticule steps down with it. */
import React from 'react';
import { placeStyle, statesNoHearth } from '../../data/gazetteer.js';
import { useCoastline, visibleRings } from './coastTiers.js';
import { gridStep, ticks } from './graticule.js';
import { Eyebrow } from '../../components/Eyebrow.jsx';
import { ActionChip } from '../../Chrome.jsx';

/* Equirectangular, and deliberately so: it is the projection the coastline asset is
   stored in, it keeps the transform to two subtractions, and at this scale — a diagram of
   where traditions arose — an equal-area projection would buy accuracy nobody reads. */
const project = (lat, lon) => ({ x: lon, y: -lat });

/* The North Atlantic, which is where all five traditions are. The box is wide and short
   and the panel beside it is nearly square, so `meet` letterboxes it into extra ocean top
   and bottom — that is the honest trade: both coasts of the Atlantic have to be on screen
   at once for a transmission arc to mean anything. */
const HOME = { x: -114, cy: -38.5, w: 134 };   // cy: the latitude the view is centred on

/* A pan may not lose the world. With the outline now global and MAX_W a whole hemisphere,
   dragging far enough leaves blank paper with no way back but "reset the view". The
   centre is held inside the earth, which still allows an ocean-only view — that is a real
   place — but not an empty one. */
const clampPlace = (pl) => ({
  ...pl,
  x: Math.min(180, Math.max(-180 - pl.w, pl.x)),
  cy: Math.min(90, Math.max(-90, pl.cy)),
});

/* MIN_W was 6 and is 3: the floor on how far in the reader may go, and it is set by what
   the finest outline can honestly draw rather than by taste. Natural Earth 10m simplified
   at 0.012 degrees is about five screen pixels of error across a 1,200px pane at three
   degrees of longitude; letting the reader past that would be selling them a magnified
   guess. MAX_W is a whole hemisphere and a bit — the outline is the world now, not the
   North Atlantic clip it used to be, because a quarter of the gazetteer's places are
   outside that box. */
const MIN_W = 3, MAX_W = 340;


const ZOOM_KEY = {
  font: 'var(--type-data-s)', fontFamily: 'var(--mono)', width: 22, height: 20,
  color: 'var(--ink-3)', background: 'transparent', cursor: 'pointer',
  transition: 'var(--t-hover)',
};

/* Ask the browser for its own full screen as well as the shell's.

   The two are different wins and the reader wants both: the shell's gives back the rails
   and the masthead, the browser's gives back its tab strip, its address bar and — on the
   machine this was reported from — a bookmarks bar taller than the atlas's legend. The
   browser's may be refused (a permissions policy, an iframe, a gesture it did not count),
   and that refusal must not cost the shell's: the promise is caught and the in-app
   expansion stands on its own. */
function requestFull(onFull) {
  onFull && onFull();
  if (typeof document === 'undefined') return;
  const el = document.documentElement;
  if (el && el.requestFullscreen && !document.fullscreenElement) {
    const p = el.requestFullscreen();
    if (p && p.catch) p.catch(() => { /* the shell's full screen is the part we control */ });
  }
}

const PRECISION_NOTE = {
  locality: 'a place you could walk across',
  region: 'a named region, a hundred miles wide',
  country: 'a whole country — no hearth to place it at',
};

export function MapView({
  rows, edges, sel, compare, onPick, traditionHue, lit, carries, showClaims, rankFilter,
  full, onFull, onExitFull,
}) {
  /* `place` is {x, cy, w} — a longitude span and the point it is centred on. THE HEIGHT
     IS NOT STORED. It is derived from the pane's measured aspect, so the viewBox always
     has the pane's own shape and the SVG has no letterbox at all.

     It used to store `h` too, fixed at 134:43, against a pane nearer 4:3 — so
     `xMidYMid meet` fitted by width and painted 27.8 degrees of latitude above and below
     the box. Three separate defects followed from that one gap, and an adversarial audit
     found all three: the ring cull dropped land that was on screen (South America goes
     missing at the home view, because its bounding box misses the viewBox and not the
     plate); the graticule was cut to the viewBox and drew a floating rectangle of lines
     ending short of the paper; and `toWorld` divided by the element's height while
     multiplying by the viewBox's, so a wheel zoom moved the point under the cursor by
     three degrees a notch. Deriving the height rather than correcting three call sites is
     the fix that cannot come back: with no letterbox there is no second coordinate space
     left to get wrong. */
  const [place, setPlace] = React.useState(HOME);
  const [aspect, setAspect] = React.useState(134 / 43);
  const [hover, setHover] = React.useState(null);
  const svgRef = React.useRef(null);
  const drag = React.useRef(null);

  /* The pane's aspect, measured. A ResizeObserver rather than a one-off read: the panes
     beside this one are draggable now, so the map changes shape without the window
     changing. */
  React.useLayoutEffect(() => {
    const svg = svgRef.current;
    if (!svg || typeof ResizeObserver === 'undefined') return undefined;
    const read = () => {
      const r = svg.getBoundingClientRect();
      if (r.width > 0 && r.height > 0) setAspect(r.width / r.height);
    };
    const ro = new ResizeObserver(read);
    ro.observe(svg);
    read();
    return () => ro.disconnect();
  }, []);

  /* The viewBox. `h` follows the pane; `cy` holds the centre steady as the pane changes
     shape, so growing the map taller does not slide the drawing off the top. */
  const view = React.useMemo(() => {
    const h = place.w / (aspect || 1);
    return { x: place.x, y: place.cy - h / 2, w: place.w, h };
  }, [place, aspect]);

  /* The outline this scale deserves, the one actually on the plate, and whether the
     difference is a fetch in flight or one that failed. Three states, kept apart on
     purpose: a coarse coastline drawn where a fine one was asked for is a drawing that
     has not been evaluated at this scale, and reporting it as the fine one would be the
     same error the fault corpus exists to prevent. */
  const coast = useCoastline(view.w);
  const land = React.useMemo(() => visibleRings(coast.drawn, view), [coast.drawn, view]);

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

  /* Zoom about a point, keeping that point still. Exact now that the viewBox and the
     element are the same shape: the fractions below are the fractions on screen. */
  const zoomAbout = (factor, mx, my) => {
    const asp = aspect || 1;
    setPlace((pl) => {
      const h0 = pl.w / asp;
      const y0 = pl.cy - h0 / 2;
      const w = Math.min(MAX_W, Math.max(MIN_W, pl.w * factor));
      const h = w / asp;
      const fx = (mx - pl.x) / pl.w, fy = (my - y0) / h0;
      return clampPlace({ x: mx - fx * w, cy: (my - fy * h) + h / 2, w });
    });
  };

  /* Screen point → model point. ONE mapping, used by the drag and the wheel and nothing
     else, so there is no second copy to drift. */
  const toWorld = (clientX, clientY) => {
    const svg = svgRef.current;
    if (!svg) return { x: view.x, y: view.y };
    const r = svg.getBoundingClientRect();
    if (!r.width || !r.height) return { x: view.x, y: view.y };
    return {
      x: view.x + ((clientX - r.left) / r.width) * view.w,
      y: view.y + ((clientY - r.top) / r.height) * view.h,
    };
  };

  /* Wheel-to-zoom is a NATIVE listener, registered non-passive, and not React's onWheel.

     React attaches wheel at the root as a passive listener, so `preventDefault` inside a
     JSX onWheel handler does nothing but log "Unable to preventDefault inside passive
     event listener invocation" — the map zoomed AND the page scrolled under it, which on
     a trackpad meant the surface slid away while you were trying to get closer to it. */
  /* The handler goes through a ref so the listener can be registered once, and the ref is
     written in an EFFECT rather than in the render body: writing a ref during render
     mutates state a discarded render should not have touched. */
  const wheelRef = React.useRef(null);
  React.useEffect(() => {
    wheelRef.current = (ev) => {
      // ctrl/cmd-wheel is the browser's own page zoom, and a trackpad pinch arrives the
      // same way. Taking it would mean the reader cannot zoom the PAGE while the pointer
      // is over the map, which is not the map's call to make.
      if (ev.ctrlKey || ev.metaKey) return;
      ev.preventDefault();
      const p = toWorld(ev.clientX, ev.clientY);
      zoomAbout(ev.deltaY > 0 ? 1.18 : 1 / 1.18, p.x, p.y);
    };
  });
  React.useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return undefined;
    const onWheel = (ev) => { if (wheelRef.current) wheelRef.current(ev); };
    svg.addEventListener('wheel', onWheel, { passive: false });
    return () => svg.removeEventListener('wheel', onWheel);
  }, []);

  const onPointerDown = (ev) => {
    drag.current = { start: toWorld(ev.clientX, ev.clientY), place, moved: false, id: ev.pointerId };
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
    const here = toWorld(ev.clientX, ev.clientY);
    const { start, place: p0 } = drag.current;
    setPlace(clampPlace({ ...p0, x: p0.x + (start.x - here.x), cy: p0.cy + (start.y - here.y) }));
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

  /* Only the lines that fall inside the view, at the step the view can carry. */
  const step = gridStep(view.w);
  const meridians = ticks(view.x, view.x + view.w, step);
  const parallels = ticks(-(view.y + view.h), -view.y, step);

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0,
      position: 'relative' }}>
      {/* `preserveAspectRatio="none"`, stated rather than defaulted. The viewBox is built
          from the pane's own aspect, so `none` and the default `meet` draw the same thing
          — but `none` GUARANTEES the two coordinate spaces agree even in the frame before
          a resize is observed, where `meet` would silently reintroduce the letterbox and,
          with it, the cull and the pointer maths that read it. The cost is one frame of
          non-uniform scale during a resize; the alternative is one frame of missing
          continents. */}
      <svg ref={svgRef} role="img"
        aria-label={`${clusters.length} hearths carrying ${rows.length - unlocated.length} styles, `
          + `with ${arcs.length} lineage arcs drawn between them`}
        viewBox={`${view.x} ${view.y} ${view.w} ${view.h}`}
        onPointerDown={onPointerDown} onPointerMove={onPointerMove}
        onPointerUp={onPointerUp} onPointerCancel={onPointerUp}
        preserveAspectRatio="none"
        style={{ flex: 1, minHeight: 0, width: '100%', background: 'var(--paper-lit)',
          cursor: drag.current ? 'grabbing' : 'grab', touchAction: 'none' }}>

        {/* The graticule — a plate, not a chart. The step follows the scale and the lines
            are cut to the view: at three degrees of longitude a fixed ten-degree grid is
            no grid at all, and drawing all 56 world-spanning lines to have the viewBox
            clip 54 of them is work nobody sees. */}
        <g stroke="var(--rule-soft)" strokeWidth={0.5} fill="none">
          {parallels.map((lat) => (
            <line key={'p' + lat} x1={view.x} y1={-lat} x2={view.x + view.w} y2={-lat}
              vectorEffect="non-scaling-stroke" />
          ))}
          {meridians.map((lon) => (
            <line key={'m' + lon} x1={lon} y1={view.y} x2={lon} y2={view.y + view.h}
              vectorEffect="non-scaling-stroke" />
          ))}
        </g>

        {/* Land, at whatever tier is in hand, culled to the view by the bounding boxes
            the generator wrote beside each ring.

            `vectorEffect` IS ON THE PATH, and it has to be. It was on this <g>, and
            `vector-effect` is not an inherited property — so the 0.7 was 0.7 DEGREES of
            ink rather than 0.7 pixels, and every zoom multiplied it. At six degrees of
            longitude across the pane that is a seventy-pixel shoreline; the coastline
            stopped being a line and became a band, and the map read as a crude drawing
            when what was crude was the pen. This is the third instance in this codebase
            of a per-element SVG property set on a parent and quietly ignored — see the
            note about presentation attributes losing to class rules in CLAUDE.md. */}
        <g fill="var(--paper-deep)" stroke="var(--rule)" strokeWidth={0.7} strokeLinejoin="round">
          {land.map((i) => (
            <path key={coast.drawnName + ':' + i} d={coast.drawn.paths[i]}
              vectorEffect="non-scaling-stroke" />
          ))}
        </g>

        {/* lineage arcs, under the marks. Same semantics as the tree: a cascade-carrying
            edge is solid and heavier, a claim is dashed and lighter. */}
        {/* Same story as the land above: the vectorEffect was on this <g> and reached
            none of these paths, so a cascade-carrying arc was 1.5 DEGREES wide and the
            transatlantic transmissions were drawn as bands a hundred miles across. */}
        <g fill="none">
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
                vectorEffect="non-scaling-stroke"
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

      {/* The legend, which is mostly a statement of what the marks do not know.

          CAPPED, and scrolled past the cap. It is `flex: none` and it says a lot, so on a
          860px window it took 395px — the drawing, whose whole subject is extent, got less
          than half its own surface, and in full screen it got less than that. The prose is
          load-bearing and none of it is cut; it is the DRAWING that gets the guaranteed
          share now, and the legend that scrolls. */}
      <div style={{ flex: 'none', borderTop: '1px solid var(--rule)', background: 'var(--paper)',
        display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <div style={{ flex: '0 1 auto', padding: '9px 14px 8px', display: 'flex', gap: 26,
        alignItems: 'flex-start', flexWrap: 'wrap', overflowY: 'auto', minHeight: 0,
        maxHeight: full ? 108 : '34vh' }}>
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
          {/* What the outline itself can and cannot show, at this scale, right now. The
              three states are kept apart: drawn, still coming, and could not be had. */}
          <p style={{ font: 'var(--type-data-s)', color: 'var(--ink-4)', margin: '6px 0 0' }}>
            Coastline · {coast.drawn.source}, simplified at {coast.drawn.tolerance}° —
            {' '}{land.length} of {coast.drawn.rings} rings in view.
            {coast.pending && (
              <span style={{ color: 'var(--ink-3)' }}> Fetching the {coast.wanted.name} outline
                for this scale; what is drawn is still the {coast.drawnName} one.</span>
            )}
            {coast.failed && (
              <span style={{ color: 'var(--refusal)' }}> The {coast.wanted.name} outline could
                not be fetched ({coast.failed}), so this is the {coast.drawnName} one at a
                scale it cannot carry — the facets are the simplification, not the shore.
                {' '}
                <button type="button" onClick={coast.retry}
                  style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)',
                    borderBottom: '1px solid var(--link-underline)' }}>try again</button>
              </span>
            )}
          </p>
        </div>

      </div>

      {/* The controls are OUTSIDE the scroller, and that is the point. Capping the legend
          put them inside it, and in full screen — where the cap is tightest — the control
          that LEAVES full screen scrolled out of sight. A way out that can be scrolled
          away is not a way out. */}
      <div style={{ flex: 'none', display: 'flex', gap: 10, alignItems: 'center',
        flexWrap: 'wrap', padding: '6px 14px 9px', borderTop: '1px solid var(--rule-soft)' }}>
          {/* Zoom as buttons as well as a wheel. A trackpad with no wheel gesture, a
              touch screen and a keyboard all had no way in at all before this, and the
              one thing the reader most wants from this surface is to get closer. */}
          <span style={{ display: 'inline-flex', border: '1px solid var(--rule)' }}>
            <button type="button" onClick={() => zoomAbout(1 / 1.6, view.x + view.w / 2, place.cy)}
              disabled={view.w <= MIN_W * 1.001} aria-label="zoom in" title="Closer"
              style={ZOOM_KEY}>+</button>
            <button type="button" onClick={() => zoomAbout(1.6, view.x + view.w / 2, place.cy)}
              disabled={view.w >= MAX_W * 0.999} aria-label="zoom out" title="Further out"
              style={{ ...ZOOM_KEY, borderLeft: '1px solid var(--rule)' }}>−</button>
          </span>
          <button type="button" onClick={() => setPlace(HOME)}
            style={{ font: 'var(--type-data-s)', color: 'var(--gilt-deep)',
              borderBottom: '1px solid var(--link-underline)' }}>reset the view</button>
          {/* The whole window, temporarily. The rails and the masthead are 580px and 52px
              of instrument around a drawing whose whole errand is extent; this hands them
              back for as long as the reader wants them back, and escape ends it. */}
          {(onFull || onExitFull) && (
            <ActionChip affix={null}
              onClick={() => (full ? onExitFull && onExitFull() : requestFull(onFull))}
              title={full
                ? 'Give the instrument back — or press escape'
                : 'Give the atlas the whole window — escape brings the instrument back'}>
              {full ? '⤡ leave full screen · esc' : '⤢ full screen'}
            </ActionChip>
          )}
        <span style={{ flex: 1 }} />
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
