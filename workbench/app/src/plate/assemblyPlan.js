/* ONE FRAME OF A WALL-DATUM PLATE, LAID OUT IN PIXELS, WITHOUT REACT (WP-14.9, PRD §I.6).

   `assemblyLayout.js` (WP-14.6) decides which assemblies share a frame, where each stands and at
   what scale. This decides everything else a draughtsman puts on the sheet, so that
   `components/AssemblyPlate.jsx` only draws:

     the BANDS      one per served face, placed by a translate and a scale and NOTHING ELSE. The
                    face's `path` is Python's (`build/profiles.py`, in model inches from the wall
                    plane, y up); this file never reads a segment, an arc or an angle, because a
                    curve re-derived in JavaScript is the defect OQ 83 removed twice. The plate
                    flips y with a negative scale and SVG mirrors the arcs, which is its job.
     the WALL       a chain line at x = 0 of each assembly, the wall plane every projection is
                    measured from, and a nominal hatched strip behind it that is interface
                    furniture and not a record of any wall (oq/one-duty-per-hatch).
     the PARTS      a tick at every part of the module up the wall, where there are sixty or
                    fewer -- beyond that they are a grey smear and say nothing.
     the LEADERS    one per face, elbowed at a knee common to the whole assembly and carried to a
                    label column in the assembly's own gutter. Elbows at one knee cannot cross:
                    the horizontal runs sit at the faces' own heights and never share an x-range
                    with the slanted runs, whose two ends are in the same order.
     the LABELS     a member tall enough to letter, whose name fits the column at a readable
                    size, is lettered with its name and its height in feet-inches to a sixteenth
                    (`feetInches16`, the engine's own notation). Every other member gets a
                    numeral, and the numeral KEY below the frame names it. `placeLabels` keeps
                    them apart and inside the frame; where they cannot all fit, lettering gives
                    way to numerals first and the frame grows only as a last resort, so a label
                    is never drawn outside the frame and never over another.
     the SCALE      the frame's bar, off `assemblyLayout`'s ladder, in the same notation.
     the KEY        the in-frame key's marks and where each sits; its WORDS are the caller's,
                    because they are glossary records (`member`, `wall-plane`, `part`, `zone`)
                    and this file holds no word a reader sees.

   A TURNED ASSEMBLY (WP-14.24, PRD tranche 2 §C.9) is the same served paths under ONE more
   operation: `bandTransform` puts a `rotate(90)` between the translate and the scale, and nothing
   else changes about how a band is drawn. It hangs from its wall plane as a plan section does —
   the jamb at the item's left, the members reading outward from it left to right, the wall strip
   above the plane — so its chain line runs across the page, its part ticks stand in the strip,
   and its leaders drop from each member's outer face to a row of numerals below it. Its bands
   run side by side, so a name would run across its neighbours: every member of a turned
   assembly takes a numeral, and the key names it. `box` is each item's drawn box on the page,
   the same for either orientation, which is what lets a check say a turned casing is drawn wider
   than it is tall.

   ZONES (WP-14.24) are the pack's own division of an assembly (`zones: [{name, to_parts}]`,
   cumulative, held to the members by `build/check_orders.py`). `zoneString` is the ONE reading:
   each zone's figure is the DIFFERENCE of its `to_parts` from the one before, joined `4 + 12 + 3`
   for the Georgian wall, with each figure in inches through `feetInches16`. The plate draws a
   dimension line along the wall behind the strip, a tick at every boundary, each zone's figure
   beside its run, and the string under the assembly. An assembly with no zones draws none of it
   and no string: a division the record does not state is not drawn from its members.

   `measure(text, px)` is the caller's -- the page measures the real face in a canvas
   (`sheet/label.js`); a test passes a stand-in -- so nothing here needs a DOM or a font.

   Pure; imports only the corpus's notation and the layout's own placers. */
import { feetInches16 } from '../fmt.js';
import { placeLabels, extentOf } from './assemblyLayout.js';

export const PAD_X = 14;              // px either side of the frame
export const PAD_TOP = 34;            // px above the tallest assembly: its title
export const SCALE_ROW = 22;          // px below the frame to the scale bar
export const KEY_ROW = 20;            // px from the scale bar to the in-frame key
export const PAD_BOTTOM = SCALE_ROW + KEY_ROW + 14;
export const FONT_PX = 11;            // a lettered label, before it is fitted
export const MIN_FONT_PX = 9;         // below this a name is not lettered; it takes a numeral
export const NUMERAL_FONT_PX = 10.5;
export const LINE_PX = 13;            // one line of lettering
export const TITLE_FONT_PX = 9.5;
export const LEADER_OUT = 12;         // px from an assembly's outermost face to its label column
export const KNEE_OUT = 4;            // px from that face to the common knee of its leaders
export const MAX_PART_TICKS = 60;     // PRD §I.6: ticks along the wall only where there are this many or fewer
export const ZONE_FONT_PX = 10.5;     // a zone's figure and the zone string, before either is fitted
export const MIN_ZONE_FONT_PX = 6;    // the least a zone figure is set at; it is never left out
export const ZONE_LINE_OUT = 4;       // px from the wall strip to the zone dimension line
export const ZONE_TICK = 3;           // half a zone tick, px
export const ZONE_ROW = 2 * LINE_PX + 6;  // px under the frame for a zoned item's string, in parts and in inches

const num = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : null);

/* The member records of one assembly, by id -- a face's `id` is its member's. */
function membersById(asm) {
  const out = new Map();
  for (const m of Array.isArray(asm && asm.members) ? asm.members : []) if (m && m.id) out.set(m.id, m);
  return out;
}

/* The parts of the module up an assembly's wall, as model heights: 0, p, 2p … up to the
   assembly's height. None where the part is unstated or there would be more than MAX_PART_TICKS. */
export function partTicks(heightIn, partIn) {
  const h = num(heightIn), p = num(partIn);
  if (h === null || p === null || p <= 0 || h <= 0) return [];
  const n = Math.floor(h / p + 1e-9);
  if (n < 1 || n + 1 > MAX_PART_TICKS) return [];
  return Array.from({ length: n + 1 }, (_, j) => j * p);
}

/* The transform that places a served face on the page: its wall plane at (x, y), k pixels to the
   inch, y up. A turned assembly takes ONE `rotate` between the translate and the scale, so model
   (u, v) lands at (x + k·v, y + k·u): along its members to the right, out from the wall down the
   page. Nothing about the path itself changes. */
export function bandTransform({ x, y, k, turned = false }) {
  return turned
    ? `translate(${x},${y}) rotate(90) scale(${k},${-k})`
    : `translate(${x},${y}) scale(${k},${-k})`;
}

/* A zone figure in parts: a whole number as itself, otherwise to the thousandth. */
function partsWords(d) {
  return String(Math.round(d * 1000) / 1000);
}

/* THE ONE READING OF A SERVED ZONE LIST (see the head of this file). -> null where the record
   gives no division (absent, fewer than two, a figure that is not a number, or a run that does
   not increase -- which `check_orders.py` refuses upstream, so a malformed list is not drawn as
   a guess); else `{ parts, inches, runs }`: `parts` the differences of the served `to_parts`
   joined by " + ", `inches` the same figures in the engine's notation (null where no part is
   given), and one run per zone with its own name and both figures. */
export function zoneString(zones, partIn) {
  if (!Array.isArray(zones) || zones.length < 2) return null;
  const p = num(partIn) !== null && partIn > 0 ? partIn : null;
  const runs = [];
  let prev = 0;
  for (const z of zones) {
    const to = num(z && z.to_parts);
    if (to === null || !(to > prev)) return null;
    const d = to - prev;
    runs.push({
      name: z && typeof z.name === 'string' ? z.name : null,
      fromParts: prev,
      toParts: to,
      parts: partsWords(d),
      inches: p !== null ? feetInches16(d * p) : null,
    });
    prev = to;
  }
  return {
    parts: runs.map((r) => r.parts).join(' + '),
    inches: p !== null ? runs.map((r) => r.inches).join(' + ') : null,
    runs,
  };
}

/* frame: one of assemblyLayout(...).frames, laid out WITH a box (so it states pxPerIn).
   byId: Map or object of the served assemblies, by id. */
export function planFrame(frame, byId, { partIn = null, measure, legendWords = {} } = {}) {
  const k = frame && frame.scale ? num(frame.scale.pxPerIn) : null;
  if (!frame || k === null || k <= 0) return null;
  const get = (id) => (byId instanceof Map ? byId.get(id) : byId && byId[id]);
  const width = measure || ((t, px) => String(t).length * px * 0.5);
  const Hpx = frame.heightIn * k;
  const base = PAD_TOP + Hpx;                         // model y = 0, the floor every assembly stands on
  const sx = (xIn) => PAD_X + xIn * k;
  const wallPx = (frame.wallIn || 0) * k;

  const items = frame.items.map((it, i) => {
    const asm = get(it.id) || {};
    const faces = asm.geometry && Array.isArray(asm.geometry.faces) ? asm.geometry.faces : [];
    const members = membersById(asm);
    const turned = it.turned === true;
    const next = frame.items[i + 1];
    const slotRight = next ? sx(next.leftIn) : sx(frame.widthIn);
    const leftX = sx(it.leftIn);
    const rightX = sx(it.rightIn);
    const unconstructed = new Set((asm.unconstructed || []).map((u) => u && u.id).filter(Boolean));
    const stripPx = (num(it.stripIn) ?? frame.wallIn ?? 0) * k;

    // The wall plane on the page, and the mapping from a distance ALONG the wall (model y) and a
    // distance OUT from it (model x) to a page point -- the one place the orientation is decided.
    let wallX, planeY, at;
    if (!turned) {
      wallX = sx(it.xIn);
      planeY = null;
      at = (along, out) => [wallX + out * k, base - along * k];
    } else {
      wallX = sx(it.xIn);                             // the jamb
      planeY = PAD_TOP + (num(it.planeIn) ?? 0) * k;
      at = (along, out) => [wallX + along * k, planeY + out * k];
    }
    const minOut = num(it.minXIn) ?? 0;
    const maxOut = num(it.maxXIn) ?? 0;
    const lo = at(0, minOut), hi = at(it.heightIn, maxOut);
    const box = {
      x: Math.min(lo[0], hi[0]), y: Math.min(lo[1], hi[1]),
      width: Math.abs(hi[0] - lo[0]), height: Math.abs(hi[1] - lo[1]),
    };

    const strip = !turned
      ? { x: wallX - wallPx, width: wallPx, y: base - it.heightIn * k, height: it.heightIn * k }
      : { x: wallX, width: it.heightIn * k, y: planeY - wallPx, height: wallPx };
    const chain = !turned
      ? { x1: wallX, y1: base - it.heightIn * k - 6, x2: wallX, y2: base + 6 }
      : { x1: wallX - 6, y1: planeY, x2: wallX + it.heightIn * k + 6, y2: planeY };
    const tickLen = Math.min(6, wallPx);
    const ticks = partTicks(it.heightIn, partIn).map((t) => {
      const [px, py] = at(t, 0);
      return !turned ? [px - tickLen, py, px, py] : [px, py - tickLen, px, py];
    });

    // Leaders: upright, out to a knee right of the outermost face and on to a column in the
    // gutter; turned, down from each outer face to a knee below the deepest and on to a row.
    const outerPx = turned ? planeY + Math.max(0, maxOut) * k : null;
    const bands = faces.map((f) => {
      const m = members.get(f.id) || {};
      const y0 = num(f.y0) ?? 0, y1 = num(f.y1) ?? 0;
      const [ax, ay] = at((y0 + y1) / 2, Math.max(0, num(f.x) ?? 0));
      return {
        asm: it.id,
        member: f.id,
        d: typeof f.path === 'string' ? f.path : '',
        name: typeof m.name === 'string' ? m.name : f.id,
        heightIn: num(m.height_in) ?? (y1 - y0),
        projectionIn: num(m.projection_in),
        unconstructed: unconstructed.has(f.id),
        anchor: { x: ax, y: ay },
        bandPx: (y1 - y0) * k,
      };
    });

    const zs = zoneString(asm.zones, partIn);
    let zones = null;
    if (zs) {
      const reservePx = (num(it.zoneReserveIn) ?? 0) * k;
      const figW = Math.max(...zs.runs.map((r) => width(r.parts, 1)));
      const along = (tParts) => (num(partIn) !== null ? tParts * partIn : null);
      const canPlace = zs.runs.every((r) => along(r.toParts) !== null);
      if (!turned) {
        const lineX = wallX - stripPx - ZONE_LINE_OUT;
        const font = Math.max(MIN_ZONE_FONT_PX, Math.min(ZONE_FONT_PX, (reservePx - ZONE_LINE_OUT - 5) / figW));
        zones = {
          ...zs,
          line: canPlace ? { x1: lineX, y1: base, x2: lineX, y2: base - along(zs.runs[zs.runs.length - 1].toParts) * k } : null,
          ticks: canPlace ? [0, ...zs.runs.map((r) => r.toParts)].map((t) => {
            const y = base - along(t) * k;
            return [lineX - ZONE_TICK, y, lineX + ZONE_TICK, y];
          }) : [],
          figures: canPlace ? zs.runs.map((r) => ({
            run: r, x: lineX - ZONE_LINE_OUT, y: base - along((r.fromParts + r.toParts) / 2) * k + font * 0.34,
            anchor: 'end', font,
          })) : [],
        };
      } else {
        const lineY = planeY - stripPx - ZONE_LINE_OUT;
        const font = Math.max(MIN_ZONE_FONT_PX, Math.min(ZONE_FONT_PX, reservePx - ZONE_LINE_OUT - 3));
        zones = {
          ...zs,
          line: canPlace ? { x1: wallX, y1: lineY, x2: wallX + along(zs.runs[zs.runs.length - 1].toParts) * k, y2: lineY } : null,
          ticks: canPlace ? [0, ...zs.runs.map((r) => r.toParts)].map((t) => {
            const x = wallX + along(t) * k;
            return [x, lineY - ZONE_TICK, x, lineY + ZONE_TICK];
          }) : [],
          figures: canPlace ? zs.runs.map((r) => ({
            run: r, x: wallX + along((r.fromParts + r.toParts) / 2) * k, y: lineY - ZONE_TICK - 2,
            anchor: 'middle', font,
          })) : [],
        };
      }
    }

    return {
      id: it.id,
      index: it.index,
      heightIn: it.heightIn,
      turned,
      wallX,
      planeY,
      leftX,
      rightX,
      kneeX: turned ? null : rightX + KNEE_OUT,
      kneeY: turned ? outerPx + KNEE_OUT : null,
      colX: turned ? null : rightX + LEADER_OUT,
      rowY: turned ? outerPx + LEADER_OUT : null,
      colRight: slotRight - 4,
      box,
      strip,
      chain,
      transform: bandTransform({ x: wallX, y: turned ? planeY : base, k, turned }),
      ticks,
      title: { x: leftX, y: PAD_TOP - 12, maxW: Math.max(0, slotRight - leftX - 6) },
      bands,
      zones,
      undrawn: [...members.values()].filter((m) => !faces.some((f) => f.id === m.id)),
    };
  });

  /* Lettering, decided per band against its own column. A turned item's bands stand side by
     side, so none is lettered. */
  const letterable = (item, b) => {
    if (item.turned || b.bandPx < LINE_PX) return null;
    const colW = item.colRight - item.colX - 2;
    const dims = feetInches16(b.heightIn);
    const w1 = Math.max(width(b.name, 1), width(dims, 1));
    if (!(w1 > 0) || colW <= 0) return null;
    const font = Math.min(FONT_PX, colW / w1);
    return font >= MIN_FONT_PX ? { font, lines: [b.name, dims] } : null;
  };

  const numeralW = width('00', NUMERAL_FONT_PX) + 4;
  const place = (allowLetters, bounded) => items.map((item) => {
    const ls = item.bands.map((b) => {
      const letter = allowLetters ? letterable(item, b) : null;
      return { item, b, letter, h: letter ? 2 * LINE_PX : LINE_PX };
    });
    if (item.turned) {
      // along the row: the numerals keep the members' order, inside the item's own slot where
      // they fit and past it (never over one another) where they do not
      const { labels: at, overflow } = placeLabels(
        ls.map((l, j) => ({ id: j, y: l.b.anchor.x, h: numeralW })),
        { minGapPx: 1, top: bounded ? item.leftX : null, bottom: bounded ? item.colRight : null });
      return { item, ls, placed: at, overflow };
    }
    // The top is always a bound: nothing is lettered over the titles. The bottom is a bound
    // until the labels cannot fit above it, and then the frame grows downward to hold them.
    const { labels: at, overflow } = placeLabels(
      ls.map((l, j) => ({ id: j, y: l.b.anchor.y, h: l.h })),
      { minGapPx: 1, top: PAD_TOP, bottom: bounded ? base : null });
    return { item, ls, placed: at, overflow };
  });

  let placed = place(true, true);
  if (placed.some((p) => p.overflow)) placed = place(false, true);   // lettering gives way first
  if (placed.some((p) => p.overflow)) placed = place(false, false);  // then the frame grows
  const lowest = Math.max(base, ...placed.flatMap((p) => (p.item.turned
    ? p.placed.map(() => p.item.rowY + LINE_PX)
    : p.placed.map((l) => l.y + l.h / 2))));
  const extra = lowest - base;

  let numeral = 0;
  const labels = [];
  const key = [];
  for (const { item, ls, placed: pl } of placed) {
    ls.forEach((l, j) => {
      const { b } = l;
      const entry = {
        asm: b.asm, member: b.member, name: b.name, words: feetInches16(b.heightIn),
        unconstructed: b.unconstructed,
      };
      let text;
      if (l.letter) {
        text = { kind: 'letter', font: l.letter.font, lines: l.letter.lines };
      } else {
        numeral += 1;
        text = { kind: 'numeral', font: NUMERAL_FONT_PX, lines: [String(numeral)] };
        key.push({ ...entry, numeral });
      }
      if (item.turned) {
        const cx = pl[j].y;
        const w = width(text.lines[0], text.font);
        labels.push({
          ...entry, ...text, numeral,
          x: cx - w / 2, y: item.rowY + LINE_PX / 2, h: LINE_PX, w,
          leader: [[b.anchor.x, b.anchor.y], [b.anchor.x, item.kneeY], [cx, item.rowY]],
        });
      } else {
        const y = pl[j].y;
        labels.push({
          ...entry, ...text, numeral: text.kind === 'numeral' ? numeral : null,
          x: item.colX + 2, y, h: l.h,
          leader: [[b.anchor.x, b.anchor.y], [item.kneeX, b.anchor.y], [item.colX, y]],
        });
      }
    });
    for (const m of item.undrawn) {
      key.push({ asm: item.id, member: m.id, name: typeof m.name === 'string' ? m.name : m.id,
        words: feetInches16(num(m.height_in)), numeral: null, drawn: false });
    }
  }

  const frameBottom = base + Math.max(0, extra);
  const zoned = items.some((it) => it.zones);
  // the zone string sits under its own assembly, in its own slot, in parts and then in inches
  for (const it of items) {
    if (!it.zones) continue;
    const maxW = Math.max(1, it.colRight - it.leftX);
    const lines = [it.zones.parts, it.zones.inches].filter(Boolean);
    const w1 = Math.max(...lines.map((s) => width(s, 1)));
    const font = Math.max(MIN_ZONE_FONT_PX, Math.min(ZONE_FONT_PX, w1 > 0 ? maxW / w1 : ZONE_FONT_PX));
    it.zones.string = { x: it.leftX, y: frameBottom + LINE_PX, font };
    it.zones.inchesLine = it.zones.inches ? { x: it.leftX, y: frameBottom + 2 * LINE_PX, font } : null;
  }
  const zoneRow = zoned ? ZONE_ROW : 0;
  const scale = {
    x: PAD_X, y: frameBottom + zoneRow + SCALE_ROW,
    barPx: frame.scale.barIn * k, words: frame.scale.words,
  };
  const legend = planLegend({ x: PAD_X, y: scale.y + KEY_ROW, words: legendWords, measure: width,
    ticks: items.some((it) => it.ticks.length > 0), zones: zoned });
  const plateWidth = PAD_X * 2 + frame.widthIn * k;
  const height = frameBottom + zoneRow + PAD_BOTTOM;
  return {
    index: frame.index,
    width: Math.max(plateWidth, legend.right + PAD_X),
    height,
    top: PAD_TOP,
    base,
    pxPerIn: k,
    items,
    labels,
    key,
    scale,
    legend,
    orientations: {
      upright: items.some((it) => !it.turned),
      turned: items.some((it) => it.turned),
    },
  };
}

/* The in-frame key: a band swatch for `member`, a chain line for `wall-plane`, a tick for
   `part` (only where the frame draws ticks), a ticked dimension for `zone` (only where the frame
   draws zones). Words are the caller's; an entry whose word has not arrived is placed without one
   and says nothing. */
export function planLegend({ x, y, words = {}, measure, ticks, zones = false }) {
  const entries = [];
  let cx = x;
  const add = (kind, word) => {
    const markW = kind === 'chain' ? 18 : (kind === 'zone' ? 14 : 10);
    const wordW = word ? measure(word, 10.5) : 0;
    entries.push({ kind, x: cx, y, markW, word: word || null, wordX: cx + markW + 5 });
    cx += markW + 5 + wordW + 16;
  };
  add('member', words.member);
  add('chain', words.wallPlane);
  if (ticks) add('tick', words.part);
  if (zones) add('zone', words.zone);
  return { entries, right: cx };
}

/* ONE ASSEMBLY IN A SMALL BOX, for the pack index (WP-14.24, PRD tranche 2 §C.9 and §0.3 default
   6). `asm` is the list route's `thumb` read as an assembly -- the pack's first assembly at the
   wall datum, served whole by the server and never rebuilt here. One scale fits its drawn box
   inside `widthPx` × `heightPx`, centred, turned where the record turns it, so a thumbnail is the
   plate's first drawing made small and not a second drawing. -> null where there is nothing to
   draw: no face, or a drawn box of no size in both directions. */
export function planThumb(asm, { widthPx, heightPx }) {
  const faces = asm && asm.geometry && Array.isArray(asm.geometry.faces) ? asm.geometry.faces : [];
  const h = num(asm && asm.height_in);
  if (!faces.length || h === null || h <= 0 || !(widthPx > 0) || !(heightPx > 0)) return null;
  const e = extentOf(asm);
  const turned = e.turned === true;
  // the drawn box in model inches: across the page, then down it
  const across = turned ? h : e.maxX - e.minX;
  const down = turned ? e.maxY - e.minY : h;
  if (!(across > 0) && !(down > 0)) return null;
  const k = Math.min(across > 0 ? widthPx / across : Infinity, down > 0 ? heightPx / down : Infinity);
  const left = (widthPx - across * k) / 2;
  const top = (heightPx - down * k) / 2;
  const x = turned ? left : left - e.minX * k;         // the jamb, or the wall plane
  const y = turned ? top - e.minY * k : top + h * k;   // the wall plane, or the floor
  return {
    turned,
    pxPerIn: k,
    transform: bandTransform({ x, y, k, turned }),
    box: { x: left, y: top, width: across * k, height: down * k },
    paths: faces.map((f) => ({ member: f.id, d: typeof f.path === 'string' ? f.path : '' })),
  };
}
