/* The sheet — a mounted plate in The Drawn Language, drawn ONLY from the plan record
   and its placement (P6): rooms, walls, bay lines, windows on exterior walls, doors
   with swing arcs, dimensions, scale bar, north arrow, lot and setback where the site
   is declared. Units are FEET; strokes are px and non-scaling — a pen is a pen.

   Model frame per build/render_plan.py: x east, y north, origin SW. Screen y is
   flipped inside <Model>. Ported from the mockup Sheet; generalised from its one
   hardcoded 64×44 plan to any footprint. */
import React from 'react';
import {
  DAYLIGHT_OPACITY, DAYLIGHT_TOKEN, PRIVACY_TOKEN, WET_OPACITY, WET_TOKEN,
  daylightReachFt, isWet, privacyOpacity,
} from './overlayRules.js';
import { elementBounds, wallOf, levelRooms, partitions, windows, doors, bayLines, litWalls,
         divergence, interpunctTitle, relaxationMarks, ft, levelAppendages, appendageRects,
         massingBlocks, levelBlocks, drawnBreasts, keyObstacles, plateNote } from './derive.js';
import { fitLabel, fitLine, useFontMetrics } from './label.js';
import { PEN, POCHE, DASH, inked } from './pen.js';
import { furnitureKeyPlan, keyCount, KEY } from './furnitureKey.js';
import { engineClaim, statusHead } from './engineClaim.js';
import { sketchOf } from './refusal.js';
import { bayLabel, breastOpening, doorFrame, exteriorDoorMark, interiorDoorMark, leafOf, pairOf,
         stairArrow, sweepFlag, windowMark } from './marks.js';

function DimRun({ from, to, at, vertical, stops }) {
  const marks = stops || [from, to];
  return (
    <g>
      {vertical
        ? <line x1={at} y1={-to} x2={at} y2={-from} style={PEN.dim} vectorEffect="non-scaling-stroke" />
        : <line x1={from} y1={at} x2={to} y2={at} style={PEN.dim} vectorEffect="non-scaling-stroke" />}
      {marks.map((m, i) => vertical
        ? <line key={'t' + i} x1={at - 0.55} y1={-m - 0.55} x2={at + 0.55} y2={-m + 0.55}
            style={inked(PEN.fine, "draw-dim")} vectorEffect="non-scaling-stroke" />
        : <line key={'t' + i} x1={m - 0.55} y1={at + 0.55} x2={m + 0.55} y2={at - 0.55}
            style={inked(PEN.fine, "draw-dim")} vectorEffect="non-scaling-stroke" />)}
      {marks.slice(0, -1).map((m, i) => {
        const mid = (m + marks[i + 1]) / 2;
        const label = ft(marks[i + 1] - m);
        return vertical
          ? <text key={'v' + i} x={at - 0.7} y={-mid} fontSize=".95" fill="var(--ink-2)"
              fontFamily="var(--serif)" letterSpacing=".14" textAnchor="middle" dominantBaseline="middle"
              transform={`rotate(-90 ${at - 0.7} ${-mid})`}>{label}</text>
          : <text key={'h' + i} x={mid} y={at - 0.8} fontSize=".95" fill="var(--ink-2)"
              fontFamily="var(--serif)" letterSpacing=".14" textAnchor="middle">{label}</text>;
      })}
    </g>
  );
}

/* One leaf and its arc, drawn from `marks.js::swingOf`'s numbers and nothing else: the hinge, the
   open tip, the far jamb and the sweep are computed there, where `marks.test.mjs` can hold them
   to the points the Python plate's leaves are held to (WP-14.6's second audit). */
function Leaf({ s }) {
  return (
    <g>
      <line x1={s.hinge[0]} y1={s.hinge[1]} x2={s.tip[0]} y2={s.tip[1]}
        style={PEN.medium} vectorEffect="non-scaling-stroke" />
      <path d={`M ${s.tip[0]} ${s.tip[1]} A ${s.len} ${s.len} 0 0 ${s.sweep} ${s.far[0]} ${s.far[1]}`}
        style={PEN.construction} vectorEffect="non-scaling-stroke" />
    </g>
  );
}

/* Jamb ticks: the reveal drawn across the wall, which is how a cased opening — an
   opening with a lining and NO leaf — is distinguished from a doorway on a plan. */
function Jambs({ A, B, vert }) {
  const t = 0.55;
  const tick = (p, i) => vert
    ? <line key={i} x1={p[0] - t} y1={p[1]} x2={p[0] + t} y2={p[1]}
        style={PEN.medium} vectorEffect="non-scaling-stroke" />
    : <line key={i} x1={p[0]} y1={p[1] - t} x2={p[0]} y2={p[1] + t}
        style={PEN.medium} vectorEffect="non-scaling-stroke" />;
  return <g>{[A, B].map(tick)}</g>;
}

/* A door opening: vellum break in the wall, then whatever the record's `type` says it is.
   WP-6.1 — until now `type` was read by NOTHING in any renderer, so the Tidewater plan's
   5 ft pair of doors between drawing room and dining room and the 6 ft cased opening into
   the stair hall were both drawn as one enormous hinged leaf with an arc to match. Those
   two marks are what a reader called "a massive door" and "no rhyme or reason". */
function DoorMark({ d }) {
  const f = doorFrame(d);
  const type = d.type || 'swing';
  const common = { 'data-door-type': type, 'data-door-w': d.w };
  const brk = <rect {...f.rect} fill="var(--paper-lit)" />;

  if (type === 'double') {
    const [a, b] = pairOf(d);
    return (
      <g {...common}>
        {brk}
        <Leaf s={a} />
        <Leaf s={b} />
      </g>
    );
  }
  if (type === 'cased-opening' || type === 'open') {
    return <g {...common}>{brk}<Jambs A={f.A} B={f.B} vert={f.vert} /></g>;
  }
  if (type === 'pocket') {
    // the leaf slides into the wall: shown as the slot it runs in, not as a swing -- past
    // the HIGH jamb on a vertical wall (B, the north one on screen) and the low on a horizontal
    const slot = f.vert
      ? { x: f.rect.x, y: f.B[1] - f.w, width: 0.7, height: f.w }
      : { x: f.A[0] - f.w, y: f.rect.y, width: f.w, height: 0.7 };
    return (
      <g {...common}>
        {brk}
        <rect {...slot} style={inked(PEN.construction, "ink-2")}
          strokeDasharray="1.4 1" vectorEffect="non-scaling-stroke" />
        <Jambs A={f.A} B={f.B} vert={f.vert} />
      </g>
    );
  }
  if (type === 'garage' || type === 'bulkhead') {
    // an overhead or a cellar door: no plan swing to draw, so the leaf is shown in its
    // closed position on the wall line and the opening is left otherwise clear
    return (
      <g {...common}>
        {brk}
        <line x1={f.A[0]} y1={f.A[1]} x2={f.B[0]} y2={f.B[1]}
          style={PEN.medium}
          strokeDasharray={type === 'bulkhead' ? '1.6 1.1' : undefined}
          vectorEffect="non-scaling-stroke" />
        <Jambs A={f.A} B={f.B} vert={f.vert} />
      </g>
    );
  }
  // a single leaf hangs from the jamb the RECORD names (WP-13.2): "low" is A, "high" is B, and
  // which one that is, where the leaf opens to and which way its arc turns are `marks.leafOf`'s
  return (
    <g {...common}>
      {brk}
      <Leaf s={leafOf(d)} />
    </g>
  );
}

/* A window: vellum break, glazing bar at fine weight, sill projecting past the jambs. The
   numbers are `marks.js::windowMark`'s. */
function WindowMark({ w, t }) {
  const { rect: r, sill, glazing } = windowMark(w, t);
  return (
    <g>
      <rect {...r} style={{ ...PEN.medium, fill: "var(--paper-lit)" }} vectorEffect="non-scaling-stroke" />
      <line x1={glazing[0]} y1={glazing[1]} x2={glazing[2]} y2={glazing[3]}
        style={PEN.fine} vectorEffect="non-scaling-stroke" />
      <line x1={sill[0]} y1={sill[1]} x2={sill[2]} y2={sill[3]}
        style={PEN.medium} vectorEffect="non-scaling-stroke" />
    </g>
  );
}

/* Drag handle on a selected room's edge. Deltas are computed in model feet via the
   SVG's own CTM; on release the new size is handed back so the WORKBENCH writes it
   into the record — the geometry itself is never edited (P6). Snaps to the half-foot,
   and harder to a bay line when within 0.75 ft of one. */
function DragHandle({ x, y, axis, room, bays, onCommit }) {
  const ref = React.useRef(null);
  const [delta, setDelta] = React.useState(0);

  function toModel(e) {
    const svg = ref.current.ownerSVGElement;
    const pt = new DOMPoint(e.clientX, e.clientY).matrixTransform(svg.getScreenCTM().inverse());
    return { x: pt.x, y: -pt.y };
  }
  function down(e) {
    e.stopPropagation();
    e.target.setPointerCapture(e.pointerId);
    const start = toModel(e);
    const px = { x: e.clientX, y: e.clientY };
    let moved = false;
    const move = (ev) => {
      if (Math.abs(ev.clientX - px.x) + Math.abs(ev.clientY - px.y) >= 3) moved = true;
      const now = toModel(ev);
      setDelta(axis === 'x' ? now.x - start.x : now.y - start.y);
    };
    const detach = () => {
      setDelta(0);
      e.target.removeEventListener('pointermove', move);
      e.target.removeEventListener('pointerup', up);
      e.target.removeEventListener('pointercancel', cancel);
      e.target.removeEventListener('lostpointercapture', cancel);
    };
    const cancel = () => detach();   // touch-scroll or capture loss: drop the drag cleanly
    const up = (ev) => {
      /* A CLICK IS NOT A RESIZE. This committed unconditionally, and with a zero delta it
         still rewrote the record twice over: `Math.round(size * 2) / 2` quantised an
         off-grid dimension to the half-foot, and the bay snap below moved it by up to
         0.75 ft — from a gesture nobody made. It also writes the PLACEMENT's dimension
         onto the DECLARED record, so a stray click baked the solver's own relaxation in
         and the sheet's △ marks quietly went away. It never fired while the handle was
         painted over by its partition; making the handle reachable made it live. */
      if (!moved) {
        try { e.target.releasePointerCapture(ev.pointerId); } catch { /* already lost */ }
        detach();
        return;
      }
      const now = toModel(ev);
      let d = axis === 'x' ? now.x - start.x : now.y - start.y;
      let size = Math.max(4, (axis === 'x' ? room.w : room.h) + d);
      size = Math.round(size * 2) / 2;
      if (axis === 'x') {
        for (const b of bays) {
          if (Math.abs(room.x + size - b) < 0.75) { size = b - room.x; break; }
        }
      }
      try { e.target.releasePointerCapture(ev.pointerId); } catch { /* already lost */ }
      detach();
      onCommit(axis, size);
    };
    e.target.addEventListener('pointermove', move);
    e.target.addEventListener('pointerup', up);
    e.target.addEventListener('pointercancel', cancel);
    e.target.addEventListener('lostpointercapture', cancel);
  }

  const hx = axis === 'x' ? x + delta : x;
  const hy = axis === 'y' ? y + delta : y;
  return (
    <g ref={ref}>
      {delta !== 0 && (axis === 'x'
        ? <line x1={hx} y1={-room.y} x2={hx} y2={-room.y - room.h}
            style={inked(PEN.medium, "gilt-deep")} strokeDasharray="2 2" vectorEffect="non-scaling-stroke" />
        : <line x1={room.x} y1={-hy} x2={room.x + room.w} y2={-hy}
            style={inked(PEN.medium, "gilt-deep")} strokeDasharray="2 2" vectorEffect="non-scaling-stroke" />)}
      <rect data-nopan="" x={hx - 0.8} y={axis === 'y' ? -hy - 0.8 : -room.y - room.h / 2 - 0.8}
        width={1.6} height={1.6}
        style={{ ...inked(PEN.medium, 'gilt-deep'), fill: 'var(--paper-lit)',
                 cursor: axis === 'x' ? 'ew-resize' : 'ns-resize' }}
        vectorEffect="non-scaling-stroke"
        onPointerDown={down} />
    </g>
  );
}

/* Room lettering, fitted to the room it names. The pad is the partition drawn on the
   room's own edge plus a hair of air: a label that touches the wall reads as running
   into it even when it stops short. A room too small for its name and its dimensions
   keeps the name — the dimension string is on the dimension lines as well, the name is
   nowhere else. */
const labelPad = (wall) => wall.partition_ft / 2 + 0.55;
const DIM_GAP = 0.42;

function layLabel(r, boxW, boxH) {
  if (boxW <= 0.5 || boxH <= 0.5) return null;
  const dim = fitLine(`${ft(r.w)} × ${ft(r.h)}`, boxW, { preferred: 0.9, min: 0.55 });
  const wantDim = Math.min(r.w, r.h) >= 5.5 && Math.max(r.w, r.h) >= 8 && dim.size >= 0.62;
  const reserve = wantDim ? dim.size * 1.15 + DIM_GAP : 0;
  const name = fitLabel(r.name.toUpperCase(), boxW, Math.max(1, boxH - reserve),
    { preferred: 1.25, min: 0.55, track: 0.3, lead: 1.24, maxLines: 3 });
  if (!name) return null;
  // the dimensions go only where the name still reads at a working size beside them
  const showDim = wantDim && name.size >= 0.7;
  return { name, dim: showDim ? dim : null,
           block: name.height + (showDim ? DIM_GAP + dim.size * 1.15 : 0) };
}

function roomLabel(r, wall) {
  const pad = labelPad(wall);
  const flat = layLabel(r, r.w - pad * 2, r.h - pad * 2);
  // A closet, a stair or a hyphen is a slot: its name will not go across it at any size
  // that can still be read, and the draughtsman's answer has always been to turn the
  // lettering to run with the room. Turned only when it earns a materially larger
  // letter — a label turned for a few percent is a label the reader has to work at.
  const turned = r.h > r.w * 1.3
    ? layLabel(r, r.h - pad * 2, r.w - pad * 2) : null;
  const useTurned = turned && (!flat || turned.name.size > flat.name.size * 1.15);
  const L = useTurned ? turned : flat;
  if (!L) return null;
  return { ...L, turned: !!useTurned, cx: r.x + r.w / 2, cy: -r.y - r.h / 2 };
}

/* The furniture key's inputs, gathered ONCE for the plate and its caption (WP-13.2): the walls
   AS DRAWN, every door leaf's swing square AS DRAWN, the stair and the chimney breasts -- all
   `derive.js::keyObstacles`, which `benchSheet.test.mjs` reads -- and each room's label through
   `roomLabel`, the one fitter, so the key knows where the name is without a second measurement of
   it. build/render_plan.py::furniture_key_plan is the same gathering in sheet px.

   WP-14.6's second audit: the walls here were `derive.partitions`' 4.5 in lines while the plate
   drew the SERVED bands, so 11 of the 146 keys fitted over the sixteen plans stood on a drawn wall
   body, all eleven on the Tidewater plan; and the key knew nothing of a breast, because the bench
   drew none. */
function keyPlanFor(rooms, wall, drs, parts, stair, levelIndex, served, breasts) {
  return furnitureKeyPlan(rooms, {
    ...keyObstacles({ drs, served, parts, stair, levelIndex, breasts }),
    labelBox: (r) => {
      const lab = roomLabel(r, wall);
      if (!lab) return null;
      const w = Math.max(lab.name.width, lab.dim ? lab.dim.width : 0);
      return lab.turned ? { w: lab.block, h: w } : { w, h: lab.block };
    },
  });
}

export function Sheet({ plan, placement, levelIndex = 0, overlays, ghost, selectedRoom,
                        onPickRoom, onResizeRoom, title, subtitle, styleName }) {
  useFontMetrics();          // re-fit every label once EB Garamond itself has arrived
  const ov = overlays || {};
  const fp = placement?.footprint || {};
  const W = fp.width_ft || 40, H = fp.depth_ft || 30;
  // THE WALL THE RECORD STATES, not two literals. `footprint.wall` is written by
  // build/openings.py::place from the plan's own declared.construction_type; a record placed
  // before plan schema 0.5.1 has none and `wallOf` says so rather than drawing a convention
  // as though it were a reading.
  const wall = wallOf(fp);
  const rooms = levelRooms(plan, placement, levelIndex);
  const parts = partitions(rooms, W, H, 0.6, wall.partition_ft);
  /* THE PLATE'S OWN WALLS (WP-14.4). `render_plan.wall_bodies` is the one spelling of the walls,
     served on the placement: each element's envelope, the joins between elements drawn once,
     the bearing lines, the partitions, and a hole for every opening. This sheet drew one ring
     round the FOOTPRINT from its own derivation -- a house with a wing was drawn with a wing and
     a hyphen that had no walls at all -- and it keeps that drawing only for a placement served
     without the plate's walls, which the note below says. */
  const served = Array.isArray(placement?.walls)
    ? (placement.walls.find((b) => (b.level ?? 0) === levelIndex) || null) : null;
  // every massing element, for the plate's FRAME: the same on every level, so a level and its
  // ghost of the other register. The FLOOR is drawn for this level's own elements (below).
  const blocks = massingBlocks(fp, W, H);
  // doors first, then windows into what the doors have left: an opening may not be drawn
  // over another opening, and on this sheet the door is the one that keeps its place
  // WP-11.10 — the at-grade appendages on THIS level, as bare rectangles for the door
  // lookup. An appendage's room carries no geometry, so without this a door the record says
  // is seated comes back "the other room is not placed on this level". The placement did not
  // SERVE them until WP-14.6's second audit, so this was empty on every plan (derive.js says more).
  const appendages = levelAppendages(placement, levelIndex);
  // WP-11.14 — which massing element each room stands in, as [x, y, W, H]. The join is
  // geometric containment, which is build/elements.py::element_of's own rule; a room in NO
  // element is ABSENT from the map, never given the main block's box, because defaulting it
  // there is the defect WP-11.9 exists to remove. With no `blocks` on the record the map is
  // empty and every reader falls back to the footprint, which is every plan in the corpus.
  // EL_TOL IS 0.5 AND IT IS build/elements.py::TOL, NOT A TASTE. The first version of this
  // block wrote 0.01 under a comment claiming it was `element_of`'s own rule -- fifty times
  // tighter than the rule it named. An audit measured the band: a room 0.01 to 0.50 ft outside
  // its block is IN its element for render_plan.py and in NO element here, so the two
  // renderers answer "which of this room's walls are exterior" differently -- the exact thing
  // WP-11.14 exists to make them answer with one function. `_absorb` is documented to grow a
  // room past its element, so the band is reachable rather than theoretical, and the frozen
  // sheet_symbols contract cannot catch it: `generate.py`'s ROOM_KEYS does not copy `block`, so
  // every frozen fixture has one element even though one shipped plan is tagged (WP-11.16).
  // WP-12.5 lifted this into derive.js::elementBounds, because the Round needed the same
  // question answered and a second copy is how the 0.01-against-0.5 tolerance split happened.
  const elBounds = elementBounds(rooms, fp);
  // the floor fields: this level's own elements, `render_plan.wall_bodies::_blocks_here`'s rule
  const floors = levelBlocks(blocks, rooms, elBounds);
  const drs = doors(rooms, W, H, 0.6, appendageRects(appendages), elBounds);
  const wins = windows(rooms, W, H, 0.6, drs.exterior, elBounds);
  const diverged = divergence(rooms);
  const divergedIds = new Set(diverged.map((d) => d.id));
  const bays = bayLines(fp);
  // plan schema 0.3.0 (WP-6.2): the stair is an object on the record, or it is absent —
  // never an empty room presented as a finished one
  const stair = placement?.stair || plan?.stair;
  // the chimney breasts the placement's own verdicts let this plate draw
  const breasts = drawnBreasts(placement, levelIndex);
  const keyPlan = keyPlanFor(rooms, wall, drs, parts, stair, levelIndex, served, breasts);  // WP-13.2
  const ghostRooms = ghost != null ? levelRooms(plan, placement, ghost) : [];
  const roomsMeta = ov.meta || {};

  const site = plan.site || plan.context || {};
  const lotW = site.lot_width_ft, lotD = site.lot_depth_ft;
  const hasLot = !!(lotW && lotD);
  const xOff = hasLot ? (site.setback_side_ft ?? Math.max(0, (lotW - W) / 2)) : 0;
  const yOff = hasLot ? (site.setback_front_ft || 0) : 0;

  // viewBox in model feet (y already negated screenward): margins for street, dims, bar
  /* WP-11.4. The stoop stands outside the entrance wall and an exterior stack outside its
     gable end, both at a negative coordinate or past `width_ft`, so the plate has to be wide
     enough to hold them. `build/render_plan.py::threshold_rects` is the same reckoning in
     the same order; a plate sized to the rooms alone cuts them off with no error anywhere. */
  const thRects = [
    ...((placement?.threshold?.steps) || []).flatMap((st) => [st.platform, st.flight].filter(Boolean)),
    ...((placement?.hearths?.stacks) || []),
    /* WP-11.10. An at-grade appendage stands OUTSIDE the block by its whole depth — fourteen
       feet of terrace east of a sixty-foot house — so the plate has to hold it or it leaves
       the sheet with no error anywhere. `build/render_plan.py::appendage_rects` is the same
       reckoning in the same list. */
    ...appendages.map((a) => a.rect),
    /* WP-14.4. Every massing element and its wall: the plate was framed on the main block, so a
       house with a west wing was drawn with the wing off the left edge of the sheet. The Python
       plate frames every placed room (`_pts` in `render_plan.render`); a block is the same
       reckoning one level up, and its envelope stands a wall's thickness outside it. */
    ...blocks.map((b) => ({ x_ft: b.x - wall.exterior_ft, y_ft: b.y - wall.exterior_ft,
      width_ft: b.w + 2 * wall.exterior_ft, depth_ft: b.h + 2 * wall.exterior_ft })),
  ];
  const outL = Math.max(0, ...thRects.map((r) => -r.x_ft));
  const outR = Math.max(0, ...thRects.map((r) => r.x_ft + r.width_ft - W));
  const outB = Math.max(0, ...thRects.map((r) => -r.y_ft));
  const outT = Math.max(0, ...thRects.map((r) => r.y_ft + r.depth_ft - H));
  // A FLOOR, AND ON THE SHIPPED PLAN IT IS NOT REACHED: an exterior stack projects 3.1 ft and
  // the flight 3.5, against margins of 11 and 9 ft that this sheet already carried for the
  // street and the dimension line. So this widening changes nothing today and is inert rather
  // than wrong -- said plainly, because a reader who mutates it and sees the walk stay green
  // should know why. build/render_plan.py's plate has no such margin and the same reckoning
  // there is load-bearing; its guard goes red on the revert.
  const mL = Math.max(11, outL + 3), mR = Math.max(15, outR + 3);
  const mT = Math.max(hasLot ? Math.max(15, lotD - H - yOff + 8) : 15, outT + 3);
  const mB = Math.max(hasLot ? Math.max(9, yOff + 7) : 9, outB + 3);
  const view = { x: -mL, y: -H - mT, w: W + mL + mR, h: H + mT + mB + 6 };
  // a zero-width space after each interpunct: the title may fold at a word boundary,
  // and never inside a word — without it 'TIDEWATER·GEORGIAN,·FIVE·BAYS,·CAREFULLY·
  // PLANNED' is one unbreakable word and the plate clips whatever does not fit
  const interpunct = interpunctTitle(title);
  const relax = placement?.geometry_report?.relaxations;
  /* WP-11.12 (OQ 98's reporting half). build/structure.py has measured the clear span since
     WP-3.1 and the search has CHARGED it since WP-7.4, and no plate had ever printed it -- the
     Tidewater upper floor is drawn with a 60 ft run and no bearing line in it. The count is a
     FLOOR and the sentence says so: `span_check` credits a bearing wall across the whole plate
     however short it runs, which is that question's unruled measurement half.
     build/render_plan.py prints the same two states in its margin schedule. */
  const spanCap = placement?.geometry_report?.span_capacity;
  const rxMarks = relaxationMarks(relax?.marks, levelIndex, W, H);
  /* WHICH ENGINE PLACED THIS, on the PLATE (WP-6.4). WP-6.3 put the disclosure in the page
     prose beside the drawing, which is the one place it cannot travel: a plate that is
     printed, screenshotted or exported leaves the prose behind, and a reader then cannot
     tell a proof from a search. The caption is the plate's own voice, so it says it here.
     `reason` is present when `auto` FELL BACK, and that is the case worth naming.
     WP-13.2: THE VERDICT IS `engineClaim.js`'s. This line read `solver.engine === 'cp-sat'` and
     printed "Placement proved" over a FEASIBLE truncation and over an `OPTIMAL (hard-only)` whose
     objective never ran -- the bench's own plate certifying what the Python plate beside it had
     stopped certifying at the same commit. It prints the plate's four states now: proved at the
     optimum (naming any declared wall set aside to get there), by CP-SAT and not proved at the
     optimum (quoting the solver's own status, and saying when the composition was not evaluated),
     searched, or nothing where no engine is recorded. */
  const claim = engineClaim(placement?.geometry_report?.solver);
  /* THE WALL DRAG'S WORKING SKETCH, ON THE PLATE (WP-13.4).

     Since 15 Sep 2026 a placement that breaks a hard fact of the type is refused and no surface
     draws it — with ONE exception, the wall drag, which asks for the hill-climb by name because
     a gesture cannot wait for a proof. `workbench/server/evaluate.py` marks that one
     `placement.sketch = {working, refused, reason}`, and this is the only sheet in the app that
     draws one.

     IT IS SAID HERE AND NOT ONLY IN THE PROSE BESIDE THE SHEET, for WP-6.4's reason: a printed,
     screenshotted or exported plate leaves the prose behind, and a reader then cannot tell a
     working sketch from a drawing. The state is read once, from the record, through the one
     leaf — the Plan Workbench reads the same function for the same placement, and neither
     derives it. */
  const sketch = sketchOf(placement);
  const engineLine = claim.verdict === 'unjudged' ? ''
    : claim.proved
      ? "Placement proved (CP-SAT) against the record's own declared facts"
        + (claim.wallsSetAside
          ? `, with ${claim.wallsSetAside} declared exterior wall${claim.wallsSetAside === 1 ? '' : 's'} set aside`
          : '')
        + '. '
      : claim.cp
        ? `Placement by CP-SAT, not proved at the optimum — ${statusHead(claim.status) || 'solver status not recorded'}. `
          + (claim.objectiveRan ? ''
            : 'The compositional objective did not run, so no term for the front, the axis or the stack was evaluated on it. ')
        : 'Placement searched, not proved — hill-climb'
          + (claim.fellBack ? `, because ${claim.reason}` : '')
          + '. ';
  // everything the plate says after the sketch and the engine (WP-14.6's second audit)
  const note = plateNote({ wall, footprint: fp, placement, levelIndex, rooms, served, relax,
                           rxMarks, spanCap, drs, wins, diverged, keyMargin: keyPlan.margin, bays });

  return (
    <div style={{ position: 'relative', background: 'var(--paper)', border: '1px solid var(--ink-2)',
      boxShadow: 'var(--shadow-plate)', padding: '18px 22px 14px' }}>
      {sketch && (
        <div data-working-sketch="" data-sketch-refused={sketch.refused ? sketch.refused.kind : ''}
          style={{ border: '1px solid var(--refusal)', padding: '6px 10px', margin: '0 0 10px',
            font: 'var(--type-eyebrow)', letterSpacing: 'var(--tr-eyebrow)',
            textTransform: 'uppercase', color: 'var(--refusal)' }}>
          working sketch — not a drawing
          <span style={{ font: 'italic var(--fw-reg) 12px/1.45 var(--serif)', letterSpacing: 0,
            textTransform: 'none', color: 'var(--ink-2)', marginLeft: 10 }}>
            {sketch.refused
              ? 'this placement was refused; it is drawn only because a wall drag asked for the '
                + 'fast search by name, and it may not be exported'
              : 'placed by the fast search behind a gesture, and it may not be exported'}
            {sketch.reason ? ` — ${sketch.reason}` : ''}
          </span>
        </div>
      )}
      <div style={{ textAlign: 'center', margin: '4px 0 2px' }}>
        <div style={{ font: 'var(--fw-med) 17px/1.35 var(--serif)', letterSpacing: 'var(--tr-drawing)',
          textTransform: 'uppercase', color: 'var(--ink)' }}>{interpunct}</div>
        <div style={{ font: 'var(--fw-reg) 11px/1.4 var(--serif)', letterSpacing: 'var(--tr-caps)',
          textTransform: 'uppercase', color: 'var(--ink-2)', marginTop: 4 }}>
          {styleName} &nbsp;·&nbsp; {subtitle}
        </div>
        <div style={{ width: 150, height: 0, borderTop: '1px solid var(--rule)', margin: '9px auto 0' }} />
      </div>

      <svg viewBox={`${view.x} ${view.y} ${view.w} ${view.h}`}
        style={{ display: 'block', width: '100%' }} role="img" aria-label={title}>
        <defs>
          <pattern id="ghosthatch" width="1.6" height="1.6" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
            {/* inside a <pattern>: pattern units, not pixels, so the ladder does not
                apply -- the same exemption walk.mjs's pen check already makes here. */}
            <line x1="0" y1="0" x2="0" y2="1.6" stroke="var(--hair)" strokeWidth=".2" />
          </pattern>
        </defs>

        {/* street, lot and setback envelope — only when the record declares a site */}
        {hasLot && (
          <g>
            <line x1={-xOff - 2} y1={yOff + 2.5} x2={lotW - xOff + 2} y2={yOff + 2.5}
              style={inked(PEN.medium, "ink-2")} vectorEffect="non-scaling-stroke" />
            <text x={-xOff - 2} y={yOff + 4.2} fontSize="1" fontFamily="var(--serif)" fill="var(--ink-2)"
              letterSpacing=".3">STREET · LOT {ft(lotW)} WIDE</text>
            <rect x={-xOff} y={-(lotD - yOff)} width={lotW} height={lotD} fill="none"
              style={PEN.construction} strokeDasharray="1.5 5" strokeLinecap="round"
              vectorEffect="non-scaling-stroke" />
            <text x={-xOff + 0.6} y={-(lotD - yOff) - 0.7} fontSize=".85" fontFamily="var(--serif)"
              fontStyle="italic" fill="var(--ink-2)">setback envelope</text>
          </g>
        )}

        {/* the construction grid — left visible, at hairline */}
        {bays.map((x) => (
          <g key={'b' + x}>
            <line x1={x} y1={-H - 3} x2={x} y2={4} style={PEN.construction} vectorEffect="non-scaling-stroke" />
            <text x={x} y={-H - 3.8} fontSize=".8" fontFamily="var(--serif)" fill="var(--hair)"
              textAnchor="middle">{bayLabel(x)}′</text>
          </g>
        ))}

        {/* ghost of the other level — dashed, at hairline */}
        {ghostRooms.length > 0 && (
          <g opacity=".9">
            {ghostRooms.map((r) => (
              <rect key={'g' + r.id} x={r.x} y={-r.y - r.h} width={r.w} height={r.h} fill="url(#ghosthatch)"
                style={PEN.construction} strokeDasharray="3 2" vectorEffect="non-scaling-stroke" />
            ))}
          </g>
        )}

        {/* interior floor: reserved vellum, one field per massing element (WP-14.4: the main
            block's alone left a wing's floor the colour of the paper round it) -- per element
            ON THIS LEVEL (WP-14.6's second audit: every element on every level drew the tagged
            Tidewater's upper plate with floor over a wing and a hyphen that have no upper storey) */}
        {floors.map((b, i) => (
          <rect key={'fl' + i} data-floor="" x={b.x} y={-b.y - b.h} width={b.w} height={b.h} fill="var(--paper-lit)" />
        ))}

        {/* analytic overlays, glazed on the sheet */}
        {/* privacy_rank runs 1-5 across rooms/, not 1-6, so dividing by 6 meant the most
            private room never reached the top of the ramp. And `|| 1` drew a room type the
            catalogue has no rank for exactly like the LEAST private one — unjudged rendered
            as evaluated, on a sheet. An unranked room is now left unglazed.
            WP-12.5 lifted the ramp into `overlayRules.js` so the Round cannot spell it a
            second way; every rank this corpus carries washes exactly as before. */}
        {ov.privacy && rooms.map((r) => {
          const op = privacyOpacity(roomsMeta[r.type]?.privacy_rank);
          if (op == null) return null;
          return <rect key={'pv' + r.id} x={r.x} y={-r.y - r.h} width={r.w} height={r.h}
            fill={`var(--${PRIVACY_TOKEN})`} opacity={op} />;
        })}
        {ov.daylight && rooms.map((r) => litWalls(r, W, H, 0.6, elBounds[r.id]).map((wall) => {
          // gated on the walls the placement actually lit — the overlay may never
          // claim daylight from a window the sheet does not draw
          // `daylightReachFt` and not `mult || 2.25`: three records state a multiplier of
          // ZERO and `||` turned that stated zero into the default (WP-12.5).
          const reach = daylightReachFt(r, roomsMeta[r.type]);
          if (!(reach > 0)) return null;
          let box;
          if (wall === 'S') box = { x: r.x, y: -r.y - Math.min(r.h, reach), width: r.w, height: Math.min(r.h, reach) };
          else if (wall === 'N') box = { x: r.x, y: -r.y - r.h, width: r.w, height: Math.min(r.h, reach) };
          else if (wall === 'W') box = { x: r.x, y: -r.y - r.h, width: Math.min(r.w, reach), height: r.h };
          else box = { x: Math.max(r.x, r.x + r.w - reach), y: -r.y - r.h, width: Math.min(r.w, reach), height: r.h };
          return <rect key={'dl' + r.id + wall} {...box} fill={`var(--${DAYLIGHT_TOKEN})`} opacity={DAYLIGHT_OPACITY} />;
        }))}
        {ov.wet && rooms.filter((r) => isWet(roomsMeta[r.type])).map((r) => (
          <g key={'wt' + r.id}>
            <rect x={r.x} y={-r.y - r.h} width={r.w} height={r.h} fill={`var(--${WET_TOKEN})`} opacity={WET_OPACITY} />
            <circle cx={r.x + r.w / 2} cy={-r.y - r.h / 2} r="1.1" style={inked(PEN.fine, "blue-deep")} vectorEffect="non-scaling-stroke" />
          </g>
        ))}

        {/* rooms — clickable, because every mark reaches its record (P6) */}
        {rooms.map((r) => {
          const sel = selectedRoom === r.id;
          // ∗ — this room is DRAWN at a size its own record does not declare. The sheet
          // has always printed the placed rectangle (it must; it is what was drawn) and
          // never said what it departed from, so a kitchen declared 16 × 20 and placed at
          // 63% of that area read as a measurement of the declared room.
          const off = divergedIds.has(r.id);
          const lab = roomLabel(r, wall);
          const decl = off && r.declared_width_ft && r.declared_length_ft
            ? ` — the record declares ${ft(r.declared_width_ft)} × ${ft(r.declared_length_ft)}`
            : '';
          return (
            <g key={r.id} data-room={r.id} data-diverged={off ? '' : undefined}
              onClick={onPickRoom ? () => onPickRoom(r) : undefined}
              style={{ cursor: onPickRoom ? 'pointer' : 'default' }}>
              <title>{`${r.name} — ${ft(r.w)} × ${ft(r.h)}${decl}`}</title>
              <rect x={r.x} y={-r.y - r.h} width={r.w} height={r.h}
                fill={sel ? 'var(--wash-salmon-1)' : 'transparent'}
                style={sel ? inked(PEN.medium, 'salmon-deep') : { stroke: 'transparent' }} vectorEffect="non-scaling-stroke" />
              {lab && (
                <g transform={lab.turned ? `rotate(-90 ${lab.cx} ${lab.cy})` : undefined}>
                  {lab.name.lines.map((ln, i) => (
                    <text key={'n' + i} x={lab.cx + lab.name.track / 2}
                      y={lab.cy - lab.block / 2 + (i + 0.5) * lab.name.lead}
                      fontSize={lab.name.size} fontFamily="var(--serif)"
                      letterSpacing={lab.name.track} fill="var(--ink)"
                      textAnchor="middle" dominantBaseline="middle">{ln}</text>
                  ))}
                  {lab.dim && (
                    <text x={lab.cx + lab.dim.track / 2}
                      y={lab.cy - lab.block / 2 + lab.name.height + DIM_GAP + lab.dim.size * 0.6}
                      fontSize={lab.dim.size} fontFamily="var(--serif)" letterSpacing={lab.dim.track}
                      fill="var(--ink-2)" textAnchor="middle" dominantBaseline="middle">{lab.dim.text}</text>
                  )}
                  {/* the ∗ sits BESIDE the fitted dimension, never inside it — a mark
                      added to the string shrinks the fit until the dimension drops out
                      of every narrow room, which is what happened to the void
                      disclosure and what the Python renderer's line is frozen against */}
                  {off && lab.dim && (
                    <text x={lab.cx + lab.dim.width / 2 + lab.dim.size * 0.45}
                      y={lab.cy - lab.block / 2 + lab.name.height + DIM_GAP + lab.dim.size * 0.6}
                      fontSize={lab.dim.size} fontFamily="var(--serif)"
                      fill="var(--gilt-deep)" dominantBaseline="middle">∗</text>
                  )}
                </g>
              )}
              {/* the divergence mark for a room too small to carry its dimension string.
                  OUTSIDE the label group on purpose: that group may be rotated -90 for a
                  slot room, and a mark placed in the room's corner inside it is rotated
                  about the label's centre and lands outside the room. e2e/walk.mjs caught
                  it twice — first under the name on a 9 x 5 cellar stair, then in the
                  corner of a 4 x 25 butler's pantry — because it measures where the glyph
                  actually is rather than where it was meant to be. */}
              {off && !(lab && lab.dim) && (
                <text x={r.x + r.w - labelPad(wall)} y={-r.y - r.h + labelPad(wall)}
                  fontSize={Math.min(0.75, r.w * 0.3, r.h * 0.3)}
                  fontFamily="var(--serif)" fill="var(--gilt-deep)"
                  textAnchor="end" dominantBaseline="hanging">∗</text>
              )}
            </g>
          );
        })}

        {/* the walls, as the plate draws them: masonry in salmon flesh, partitions in sepia,
            coal skin on both. The cut line bounds all poche. A level with no placed room gets no
            walls at all -- a ring round the footprint there is a storey nobody placed, which is
            WP-11.9's finding about the envelope (WP-14.6's second audit: bad-03's third storey). */}
        {served ? served.bands.map((b, i) => (
          <rect key={'wb' + i} data-wall={b.wall} data-t={Math.round(b.t_ft * 120) / 10}
            data-block={b.block ?? undefined}
            x={b.x_ft} y={-b.y_ft - b.depth_ft} width={b.width_ft} height={b.depth_ft}
            style={b.kind === 'masonry' ? POCHE.masonry : POCHE.partition} vectorEffect="non-scaling-stroke" />
        )) : rooms.length > 0 && (
          <g data-walls="derived">
            {parts.map((p, i) => (
              <rect key={'pt' + i} x={p.x} y={-p.y - p.h} width={p.w} height={p.h} style={POCHE.partition} vectorEffect="non-scaling-stroke" />
            ))}
            <path d={`M${-wall.exterior_ft} ${wall.exterior_ft} L${W + wall.exterior_ft} ${wall.exterior_ft} `
                     + `L${W + wall.exterior_ft} ${-H - wall.exterior_ft} L${-wall.exterior_ft} ${-H - wall.exterior_ft} Z `
                     + `M0 0 L0 ${-H} L${W} ${-H} L${W} 0 Z`}
              fillRule="evenodd" style={POCHE.masonry} vectorEffect="non-scaling-stroke" />
          </g>
        )}

        {/* THE FIRE (WP-14.6's second audit): each chimney breast the placement's verdict lets
            this plate draw, in the masonry poche -- a breast is brick, and a thin outline would
            read as a cupboard -- with its opening on the room face, as build/render_plan.py draws
            it. Drawn BEFORE the openings, as the plate does, so a window reads over the breast.
            `hearths.breasts` is served and was read by nothing here: the strip said one of three
            stated fires was not drawn and the plate drew none of the three. A refused fire is
            said in the note below, on the plate, and not drawn. */}
        {breasts.map((b) => {
          const rm = rooms.find((r) => r.id === b.room);
          const h = ((rm && rm.record && rm.record.hearth) || [])[b.index] || {};
          const op = breastOpening(b, h.width_in);
          return (
            <g key={'br' + b.room + b.index} data-breast={b.room} data-breast-wall={b.wall}>
              <rect x={b.x_ft} y={-b.y_ft - b.depth_ft} width={b.width_ft} height={b.depth_ft}
                style={POCHE.masonry} vectorEffect="non-scaling-stroke">
                {/* the attribution is part of the figure: `render_plan.py`'s title, word for word */}
                <title>{`${(rm && rm.name) || b.room}: fireplace, ${h.width_in ?? 'unstated'} in opening, breast ${b.projection_in} in — Morris 1734, judgment`}</title>
              </rect>
              {op && (
                <line x1={op[0]} y1={op[1]} x2={op[2]} y2={op[3]}
                  style={inked(PEN.medium, 'salmon-deep')} vectorEffect="non-scaling-stroke" />
              )}
            </g>
          );
        })}

        {/* openings. Windows are laid into the run the doors left, so a door is never
            painted over by a window again — but the doors are still drawn AFTER, because
            a break in the poché belongs on top of the wall it breaks. What each door is drawn
            from is `marks.js`'s, the one spelling the census's reader of the bench reads too. */}
        {wins.map((w, i) => <WindowMark key={'w' + i} w={w} t={wall.exterior_ft} />)}
        {drs.exterior.map((d, i) => (
          <DoorMark key={'ed' + i} d={exteriorDoorMark(d, wall.exterior_ft)} />
        ))}
        {drs.interior.map((d, i) => <DoorMark key={'d' + i} d={interiorDoorMark(d, wall.exterior_ft)} />)}

        {/* WP-6.2 — the stair, drawn from plan.stair and from nothing else. There has never
            been a line of stair-drawing code in this system: a stair hall was an empty
            rectangle with lettering in it, while rooms/stair-hall.json carried the flight
            itself as furniture ([120, 78] in, "dog-leg with half landing") and
            build/structure.py computed its risers into a section no plan ever saw. */}
        {stair && (stair.level ?? 0) === levelIndex && (stair.flights || []).length > 0 && (
          <g data-stair="">
            {stair.flights.map((f, i) => {
              const across = f.direction === 'E' || f.direction === 'W';
              const n = Math.max(1, f.treads || 1);
              const ticks = [];
              for (let t = 1; t < n; t++) {
                if (across) {
                  const tx = f.x_ft + f.width_ft * (t / n);
                  ticks.push(<line key={t} x1={tx} y1={-f.y_ft} x2={tx} y2={-f.y_ft - f.depth_ft}
                    style={PEN.fine} vectorEffect="non-scaling-stroke" />);
                } else {
                  const ty = f.y_ft + f.depth_ft * (t / n);
                  ticks.push(<line key={t} x1={f.x_ft} y1={-ty} x2={f.x_ft + f.width_ft} y2={-ty}
                    style={PEN.fine} vectorEffect="non-scaling-stroke" />);
                }
              }
              return (
                <g key={'fl' + i}>
                  <rect x={f.x_ft} y={-f.y_ft - f.depth_ft} width={f.width_ft} height={f.depth_ft}
                    style={PEN.fine} vectorEffect="non-scaling-stroke" />
                  {ticks}
                </g>
              );
            })}
            {/* the arrow and the riser count are LETTERING over the stair hall, not controls:
                `pointerEvents: none`, the furniture key's and the relaxation run's rule (WP-6.3,
                "an annotation must not eat the click under it"), so a click on the arrow still
                selects the room it is drawn in (WP-14.6's second audit) */}
            {(() => {
              const ar = stairArrow(stair.flights[0]);
              return ar && (
                <g data-stair-arrow={stair.flights[0].direction} pointerEvents="none">
                  <line x1={ar.shaft[0]} y1={ar.shaft[1]} x2={ar.shaft[2]} y2={ar.shaft[3]}
                    style={PEN.medium} vectorEffect="non-scaling-stroke" />
                  <path d={`M ${ar.head[0]} ${ar.head[1]} L ${ar.head[2]} ${ar.head[3]} L ${ar.head[4]} ${ar.head[5]}`}
                    fill="none" style={PEN.medium} vectorEffect="non-scaling-stroke" />
                </g>
              );
            })()}
            <text x={stair.flights[0].x_ft + stair.flights[0].width_ft / 2}
              y={-stair.flights[0].y_ft - stair.flights[0].depth_ft / 2}
              fontSize="1" fontFamily="var(--serif)" letterSpacing=".18" pointerEvents="none"
              fill="var(--gilt-deep)" textAnchor="middle" dominantBaseline="middle">
              UP {stair.risers}R
            </text>
          </g>
        )}
        {stair && (stair.level ?? 0) === levelIndex && stair.unplaced && stair.well && (
          <text data-stair="refused" x={stair.well.x_ft + stair.well.width_ft / 2}
            y={-stair.well.y_ft - stair.well.depth_ft / 2 + 1.6}
            fontSize=".85" fontFamily="var(--serif)" fill="var(--gilt-deep)"
            textAnchor="middle" dominantBaseline="middle">
            <title>{stair.unplaced.reason}</title>
            stair not drawn — see record
          </text>
        )}

        {/* WP-11.4 — the stoop and the gable-end stacks, from plan.threshold and plan.hearths
            and from nothing else. Both are BRICK, so both take the wall's own body: the same
            masonry poché and the same cut line the envelope is drawn in, because they are the
            same trade and a reader must not have to learn a second convention for a second
            brick. The STACK is on every plate because it passes through every floor; the
            STOOP only on the ground, because it is at grade. */}
        {((placement?.hearths?.stacks) || []).map((sk, i) => (
          <rect key={'sk' + i} data-stack={sk.wall} x={sk.x_ft} y={-sk.y_ft - sk.depth_ft}
            width={sk.width_ft} height={sk.depth_ft}
            style={POCHE.masonry} vectorEffect="non-scaling-stroke">
            <title>{`chimney stack, ${sk.stack_plan_in} in square${sk.stack_plan_judgment ? ' (a judgment, not a measurement)' : ''}, ${sk.side} to the ${sk.wall} gable end`}</title>
          </rect>
        ))}
        {/* WP-11.10 — the terrace at grade, from plan.appendages and from nothing else. Drawn
            OPEN: an edge in the fine pen and a name, no poche and no wash, because an at-grade
            appendage is a FLOOR and not a mass. Giving it the wall's body would say the house
            is that shape, which is the one thing `rooms/terrace.json`'s own note denies.
            `appendages` is already filtered to THIS level, so there is no `levelIndex === 0`
            guard here: an appendage is drawn on the level it stands on, and hard-coding the
            ground would hide a future one rather than refuse it. */}
        {appendages.map((ap, i) => (
          <g key={'ap' + i} data-appendage={ap.room} data-appendage-wall={ap.wall}>
            <rect x={ap.rect.x_ft} y={-ap.rect.y_ft - ap.rect.depth_ft}
              width={ap.rect.width_ft} height={ap.rect.depth_ft}
              style={PEN.fine} vectorEffect="non-scaling-stroke">
              <title>{`at grade, unroofed, appended to ${(ap.serves || []).join(', ')} on its ${ap.wall} face`}</title>
            </rect>
            {/* the name in the room voice, sized in model feet like every other room label
                on this plate, and drawn only where it fits across the appendage. There is no
                fitter here on purpose: an appendage is one rectangle with one short name, and
                a second call into `layLabel` would be a second spelling of a fit this plate
                already does for rooms that have geometry. */}
            {ap.rect.width_ft > 0.62 * ((ap.name || ap.room).length + 2) && (
              <text x={ap.rect.x_ft + ap.rect.width_ft / 2}
                y={-ap.rect.y_ft - ap.rect.depth_ft / 2}
                fontSize="1.1" fontFamily="var(--serif)" letterSpacing="0.3"
                fill="var(--ink)" textAnchor="middle" dominantBaseline="middle">
                {(ap.name || ap.room).toUpperCase()}
              </text>
            )}
          </g>
        ))}
        {levelIndex === 0 && ((placement?.threshold?.steps) || []).map((st, i) => (
          <g key={'th' + i} data-threshold={st.room}>
            {[['platform', st.platform], ['flight', st.flight]].filter(([, r]) => r).map(([part, r]) => (
              <rect key={part} data-part={part} x={r.x_ft} y={-r.y_ft - r.depth_ft}
                width={r.width_ft} height={r.depth_ft}
                style={POCHE.masonry} vectorEffect="non-scaling-stroke">
                <title>{part === 'platform' ? 'stoop platform'
                  : `${st.riser_count} risers at ${st.riser_height_in} in, treads ${st.tread_depth_in} in`}</title>
              </rect>
            ))}
            {(st.nosings || []).map((n, j) => (
              <line key={'n' + j} x1={n.line[0]} y1={-n.line[1]} x2={n.line[2]} y2={-n.line[3]}
                style={PEN.medium} vectorEffect="non-scaling-stroke" />
            ))}
          </g>
        ))}

        {/* fixtures, from room.fixture_layout and from nothing else.
            WP-11.3 put this mark on the pen ladder: it had carried `stroke="var(--ink-2)"` as
            an ATTRIBUTE and a literal `1.4 1` dash since WP-6.2, and WP-11.2 moved nineteen
            stroke widths onto PEN and walked past this one. It keeps its DASH, which is what
            tells a derived wet fixture from a derived furniture arrangement on the sheet, and
            it carries `data-fixture` so the walk can count it by what it IS rather than by the
            dash it happens to be drawn with. */}
        {rooms.map((r) => (r.fixture_layout || [])
          .filter((f) => !f.unplaced && f.x_ft != null)
          .map((f, i) => (
            <rect key={r.id + 'fx' + i} data-fixture x={f.x_ft} y={-f.y_ft - f.depth_ft}
              width={f.width_ft} height={f.depth_ft}
              style={{ ...PEN.fine, strokeDasharray: DASH.extent }}
              vectorEffect="non-scaling-stroke">
              <title>{f.item}</title>
            </rect>
          )))}

        {/* furniture, from room.furniture_layout and from nothing else (WP-11.3).
            The MARKS are on the record — build/furniture.py mapped furniture/symbols.json into
            each item's own rectangle once, at placement time — so this draws what is there and
            derives nothing. That is WP-6.2's finding applied a layer up: handing both renderers
            one position and letting each re-derive the geometry from it put them 0.7 in apart
            on the first plan it was tried on. Fine pen, SOLID; the fixtures keep the dash. */}
        {rooms.map((r) => (r.furniture_layout || [])
          .filter((f) => !f.unplaced && f.marks)
          .map((f, i) => (
            <g key={r.id + 'fu' + i} data-furniture={f.symbol || 'block'}>
              <title>{f.item}</title>
              {f.marks.map((m, j) => (m.rect ? (
                <rect key={j} x={m.rect[0]} y={-m.rect[1] - m.rect[3]}
                  width={m.rect[2]} height={m.rect[3]}
                  style={PEN.fine} vectorEffect="non-scaling-stroke" />
              ) : m.line ? (
                <line key={j} x1={m.line[0]} y1={-m.line[1]} x2={m.line[2]} y2={-m.line[3]}
                  style={PEN.fine} vectorEffect="non-scaling-stroke" />
              ) : m.circle ? (
                <circle key={j} cx={m.circle[0]} cy={-m.circle[1]} r={m.circle[2]}
                  style={PEN.fine} vectorEffect="non-scaling-stroke" />
              ) : null))}
            </g>
          )))}

        {/* the key (WP-13.2). A numeral on every mark and a key in the room, so a printed
            plate names what it draws -- the tooltip above stays, and is not a label. Fitted
            by furnitureKey.js in the room's own frame (feet from its NW corner, y down);
            this adds the room's corner and nothing else. A refused key is in the caption
            under the room's name, never silently dropped. NOT `data-furniture`: the walk
            counts those as items, and a key is lettering about an item.
            `pointerEvents: none` ON THE GROUP, because a key line lying across the middle of
            a room is lettering and not a control: the walk clicks the Drawing Room at its
            centre to raise its wall handles, and with the key's `<text>` sitting there the
            click landed on the text -- a sibling of the room's `<g>`, so nothing bubbled to
            `onPickRoom` -- and all four handle checks went red naming nothing. That is the
            relaxation mark's own defect (WP-6.3, "an annotation must not eat the click under
            it") arriving with the second annotation this sheet ever drew over a room. */}
        {rooms.map((r) => {
          const kr = keyPlan.byRoom.get(r.id);
          if (!kr) return null;
          const ox = r.x, oy = -r.y - r.h;          // the room's NW corner, screen y down
          const fit = kr.fit;
          return (
            <g key={r.id + 'key'} data-furniture-key={r.id}
              data-furniture-key-fit={fit ? (fit.turned ? 'turned' : 'flat') : 'margin'}
              pointerEvents="none">
              {kr.numerals.map((nu, i) => (
                <text key={'n' + i} data-key-numeral={nu.n} x={ox + nu.x} y={oy + nu.y}
                  fontSize={nu.size} fontFamily="var(--mono)" fill="var(--ink-2)"
                  textAnchor={nu.anchor}>{nu.n}</text>
              ))}
              {fit && kr.lines.map((line, k) => {
                const size = fit.size;
                // the record's own `of` where a counted piece states one, else the name's word
                const count = kr.entries[k].of || keyCount(kr.entries[k].item);
                if (fit.turned) {
                  // read from the foot of the sheet: each line is a column, the first leftmost
                  const tx = ox + fit.x0 + k * size * KEY.lead + 0.8 * size;
                  const ty = oy + fit.y1;
                  return (
                    <text key={'k' + k} data-key-item={kr.entries[k].n} data-count={count || undefined}
                      x={tx} y={ty} transform={`rotate(-90 ${tx} ${ty})`}
                      fontSize={size} fontFamily="var(--mono)" fill="var(--ink-2)">{line}</text>
                  );
                }
                const tx = ox + fit.x0;
                const ty = oy + fit.y0 + k * size * KEY.lead + 0.8 * size;
                return (
                  <text key={'k' + k} data-key-item={kr.entries[k].n} data-count={count || undefined}
                    x={tx} y={ty} fontSize={size} fontFamily="var(--mono)" fill="var(--ink-2)">{line}</text>
                );
              })}
            </g>
          );
        })}

        {/* dimensions — ticks, primes, never decimal feet */}
        <DimRun from={0} to={W} at={2.6} stops={[0, ...bays, W]} />
        <DimRun from={0} to={W} at={5.2} stops={[0, W]} />
        <DimRun from={0} to={H} at={W + 3} vertical stops={[0, H]} />

        {/* north — an instrument, not an ornament: screen-up is model-north */}
        <g transform={`translate(${W + 10},${-H + 2})`}>
          <circle cx="0" cy="0" r="2.6" style={PEN.medium} vectorEffect="non-scaling-stroke" />
          <line x1="0" y1="2.6" x2="0" y2="-2.6" style={PEN.fine} vectorEffect="non-scaling-stroke" />
          <path d="M0 -2.6 L-0.55 -0.6 L0.55 -0.6 Z" fill="var(--coal)" />
          <text x="0" y="-3.4" fontSize="1" fontFamily="var(--serif)" letterSpacing=".2"
            fill="var(--ink-2)" textAnchor="middle">N</text>
        </g>

        {/* P7 — a compromise is counted AND appears on the drawing, at its location (OQ 33).
            Until 26 Aug 2026 the solvers recorded a relaxation as a bare number, so this sheet
            could print an honest tally and had nothing to place a mark with: the count was true
            and the drawing was silent about where the truth applied. Each mark is a cut that
            missed the structural bay — a joist run that does not land on a bearing wall — drawn
            as a hollow triangle on the line itself, in ink and not in colour, because colour in
            this system names a material and never flags a condition. Where the mark goes is
            `relaxationMarks` in derive.js — and an unlocatable one is named in the caption
            rather than drawn somewhere plausible.

            The dashed run is `pointerEvents: none`. It is an annotation, not a control: a
            hairline drawn across a room was swallowing the click that selects the room under
            it, and an affordance defeated by a tick over it is an affordance that does not
            exist. The triangle keeps its pointer events, because it is a visible glyph with a
            tooltip of its own and clicking a mark is a thing a reader means to do. */}
        {rxMarks.drawn.map(({ mark: m, runs, at }, i) => {
          const isV = m.axis === 'x';
          const [gx, gy] = isV ? [m.at_ft, -at] : [at, -m.at_ft];
          return (
            <g key={'rx' + i}>
              {runs.map(([lo, hi], j) => {
                const [x1, y1, x2, y2] = isV
                  ? [m.at_ft, -lo, m.at_ft, -hi]
                  : [lo, -m.at_ft, hi, -m.at_ft];
                return (
                  <line key={j} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--ink-2)"
                    strokeDasharray="1.2 1.2" pointerEvents="none"
                    vectorEffect="non-scaling-stroke" />
                );
              })}
              <path d={`M ${gx} ${gy - 1.15} L ${gx + 1.0} ${gy + 0.75} L ${gx - 1.0} ${gy + 0.75} Z`}
                style={{ ...PEN.fine, fill: "var(--paper)" }}
                vectorEffect="non-scaling-stroke" />
              <title>{`${m.off_ft} ft off the bay line — this cut is a joist run that does not land on a bearing wall`}</title>
            </g>
          );
        })}

        {/* scale bar — drawn, alternating, never merely stated. ITS ZERO STANDS ON THE CLEAR FACE,
            x = 0 (WP-14.4), as `render_plan.py`'s has since WP-13.2: it stood on the sheet's left
            margin, which is nothing drawn, so a reader stepping it from its 0 to a bay line read
            the margin's width into every figure. */}
        <g data-scale-bar="" transform={`translate(0,${mB - 2.6})`}>
          {[0, 1, 2, 3].map((i) => (
            <rect key={i} x={i * 8} y="0" width="8" height=".8" fill={i % 2 ? 'none' : 'var(--ink)'}
              style={PEN.fine} vectorEffect="non-scaling-stroke" />
          ))}
          {[0, 8, 16, 24, 32].map((x) => (
            <line key={'sb' + x} x1={x} y1="-.6" x2={x} y2="1.4" style={PEN.fine} vectorEffect="non-scaling-stroke" />
          ))}
          <text x="0" y="3" fontSize=".9" fontFamily="var(--serif)" letterSpacing=".18" fill="var(--ink-2)">0</text>
          <text x="16" y="3" fontSize=".9" fontFamily="var(--serif)" letterSpacing=".18" fill="var(--ink-2)" textAnchor="middle">16</text>
          <text x="32" y="3" fontSize=".9" fontFamily="var(--serif)" letterSpacing=".18" fill="var(--ink-2)" textAnchor="middle">32 FT</text>
        </g>

        {/* Legend for the △. The mark has been drawn since WP-5.2 and named only in the
            caption's running prose, where a reader meeting it on the drawing had nothing
            to read it BY — reported as arrows that "seem to point to anything and
            everything". A symbol a drawing uses is a symbol the drawing has to define. */}
        {relax?.count ? (
          <g data-legend="relaxation" transform={`translate(0,${mB + 2.4})`}>
            <path d="M 0 -1.15 L 1.0 0.75 L -1.0 0.75 Z" fill="var(--paper)"
              style={PEN.fine} vectorEffect="non-scaling-stroke" />
            <text x="2.1" y="0.7" fontSize=".95" fontFamily="var(--serif)" letterSpacing=".1"
              fill="var(--ink-2)">a cut off the bay line — no bearing wall under it</text>
          </g>
        ) : null}

        {/* Drag a wall on the bay grid: handles on the selected room's east and north
            edges; release writes back to the record and the validator re-scores.
            LAST in the sheet, and that is the fix rather than the habit — a handle
            drawn with the rooms sat under the partition on the very wall line it was
            offered for, so `elementFromPoint` at the handle returned the partition and
            the gesture the caption promised could not be started at all. An affordance
            painted over is an affordance that does not exist. */}
        {onResizeRoom && rooms.filter((r) => r.id === selectedRoom).map((r) => (
          <g key={'h' + r.id}>
            <DragHandle x={r.x + r.w} y={r.y + r.h / 2} axis="x" room={r} bays={bays}
              onCommit={(axis, size) => onResizeRoom(r, 'x', size)} />
            <DragHandle x={r.x + r.w / 2} y={r.y + r.h} axis="y" room={r} bays={bays}
              onCommit={(axis, size) => onResizeRoom(r, 'y', size)} />
          </g>
        ))}
      </svg>

      {/* plate caption. The title takes the space it needs and the note yields: with the
          title on `flex: 0 1 auto` beside a `1 1 34ch` note, a narrow plate folded
          'TIDEWATER·GEORGIAN,·FIVE·BAYS,·CAREFULLY·PLANNED' at its interpuncts and a
          reader saw 'WATER GEORGIAN, FIVE CAREFULLY PLANNED' — a different house, with
          nothing on the sheet to say the name had been cut. */}
      <div style={{ borderTop: '1px solid var(--rule)', margin: '4px 2px 0', padding: '8px 0 4px',
        display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 24,
        flexWrap: 'wrap' }}>
        <div data-plate-title="" style={{ font: 'var(--fw-med) 10.5px/1.4 var(--serif)',
          letterSpacing: '.3em', textTransform: 'uppercase', color: 'var(--ink)',
          flex: '1 0 auto' }}>{interpunct}</div>
        <div data-plate-note="" style={{ font: 'italic var(--fw-reg) 13px/1.45 var(--serif)',
          color: 'var(--ink-2)', textAlign: 'right', flex: '1 1 34ch', minWidth: '22ch' }}>
          {/* FIRST, because it governs everything after it: a plate a reader may not measure
              from must say so before it says what engine drew it. */}
          {sketch
            ? 'A WORKING SKETCH, not a drawing — placed by the fast search behind a wall drag'
              + (sketch.refused ? ', on a placement the type’s facts refuse' : '')
              + '; it may not be exported. '
            : ''}
          {engineLine}
          {/* EVERYTHING ELSE THE PLATE SAYS IS `derive.js::plateNote`'s, sentence by sentence and
              in this order, and nothing is composed here (WP-14.6's second audit). It was all
              composed inline in this JSX, where no test under `node --test` could read it: the
              bay-module line WP-14.6 deleted without printing the served one, "the grid remains"
              beside "no bay grid is drawn", "the server sent no wall bodies" on a level the
              placement never placed, and a count of refused windows nobody printed. Each line is
              published as `data-note`, and a furniture key refused to the margin keeps its
              `data-furniture-key-margin` (WP-13.2). */}
          {note.map((n, i) => (
            <span key={n.id + (n.room || '') + i} data-note={n.id}
              data-furniture-key-margin={n.room ?? undefined}>{n.text}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

export { ft, sweepFlag };
