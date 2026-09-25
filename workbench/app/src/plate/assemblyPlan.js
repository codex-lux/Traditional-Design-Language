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
                    because they are glossary records (`member`, `wall-plane`, `part`) and this
                    file holds no word a reader sees.

   `measure(text, px)` is the caller's -- the page measures the real face in a canvas
   (`sheet/label.js`); a test passes a stand-in -- so nothing here needs a DOM or a font.

   Pure; imports only the corpus's notation and the layout's own label placer. */
import { feetInches16 } from '../fmt.js';
import { placeLabels } from './assemblyLayout.js';

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

  const items = frame.items.map((it, i) => {
    const asm = get(it.id) || {};
    const faces = asm.geometry && Array.isArray(asm.geometry.faces) ? asm.geometry.faces : [];
    const members = membersById(asm);
    const wallX = sx(it.xIn);
    const next = frame.items[i + 1];
    const slotRight = next ? sx(next.leftIn) : sx(frame.widthIn);
    const rightX = sx(it.rightIn);
    const unconstructed = new Set((asm.unconstructed || []).map((u) => u && u.id).filter(Boolean));
    return {
      id: it.id,
      index: it.index,
      heightIn: it.heightIn,
      wallX,
      leftX: sx(it.leftIn),
      rightX,
      kneeX: rightX + KNEE_OUT,
      colX: rightX + LEADER_OUT,
      colRight: slotRight - 4,
      strip: { x: wallX - frame.wallIn * k, width: frame.wallIn * k, y: base - it.heightIn * k, height: it.heightIn * k },
      chain: { x: wallX, y0: base - it.heightIn * k - 6, y1: base + 6 },
      transform: `translate(${wallX},${base}) scale(${k},${-k})`,
      ticks: partTicks(it.heightIn, partIn).map((y) => base - y * k),
      title: { x: sx(it.leftIn), y: PAD_TOP - 12, maxW: Math.max(0, slotRight - sx(it.leftIn) - 6) },
      bands: faces.map((f) => {
        const m = members.get(f.id) || {};
        return {
          asm: it.id,
          member: f.id,
          d: typeof f.path === 'string' ? f.path : '',
          name: typeof m.name === 'string' ? m.name : f.id,
          heightIn: num(m.height_in) ?? ((num(f.y1) ?? 0) - (num(f.y0) ?? 0)),
          projectionIn: num(m.projection_in),
          unconstructed: unconstructed.has(f.id),
          anchor: { x: wallX + Math.max(0, num(f.x) ?? 0) * k,
                    y: base - (((num(f.y0) ?? 0) + (num(f.y1) ?? 0)) / 2) * k },
          bandPx: ((num(f.y1) ?? 0) - (num(f.y0) ?? 0)) * k,
        };
      }),
      undrawn: [...members.values()].filter((m) => !faces.some((f) => f.id === m.id)),
    };
  });

  /* Lettering, decided per band against its own column. */
  const letterable = (item, b) => {
    if (b.bandPx < LINE_PX) return null;
    const colW = item.colRight - item.colX - 2;
    const dims = feetInches16(b.heightIn);
    const w1 = Math.max(width(b.name, 1), width(dims, 1));
    if (!(w1 > 0) || colW <= 0) return null;
    const font = Math.min(FONT_PX, colW / w1);
    return font >= MIN_FONT_PX ? { font, lines: [b.name, dims] } : null;
  };

  const place = (allowLetters, bounded) => items.map((item) => {
    const ls = item.bands.map((b) => {
      const letter = allowLetters ? letterable(item, b) : null;
      return { item, b, letter, h: letter ? 2 * LINE_PX : LINE_PX };
    });
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
  const lowest = Math.max(base, ...placed.flatMap((p) => p.placed.map((l) => l.y + l.h / 2)));
  const extra = lowest - base;

  let numeral = 0;
  const labels = [];
  const key = [];
  for (const { item, ls, placed: pl } of placed) {
    ls.forEach((l, j) => {
      const y = pl[j].y;
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
      labels.push({
        ...entry, ...text, numeral: text.kind === 'numeral' ? numeral : null,
        x: item.colX + 2, y, h: l.h,
        leader: [[b.anchor.x, b.anchor.y], [item.kneeX, b.anchor.y], [item.colX, y]],
      });
    });
    for (const m of item.undrawn) {
      key.push({ asm: item.id, member: m.id, name: typeof m.name === 'string' ? m.name : m.id,
        words: feetInches16(num(m.height_in)), numeral: null, drawn: false });
    }
  }

  const frameBottom = base + Math.max(0, extra);
  const scale = {
    x: PAD_X, y: frameBottom + SCALE_ROW,
    barPx: frame.scale.barIn * k, words: frame.scale.words,
  };
  const legend = planLegend({ x: PAD_X, y: scale.y + KEY_ROW, words: legendWords, measure: width,
    ticks: items.some((it) => it.ticks.length > 0) });
  const plateWidth = PAD_X * 2 + frame.widthIn * k;
  const height = frameBottom + PAD_BOTTOM;
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
  };
}

/* The in-frame key: a band swatch for `member`, a chain line for `wall-plane`, a tick for
   `part` (only where the frame draws ticks). Words are the caller's; an entry whose word has not
   arrived is placed without one and says nothing. */
export function planLegend({ x, y, words = {}, measure, ticks }) {
  const entries = [];
  let cx = x;
  const add = (kind, word) => {
    const markW = kind === 'chain' ? 18 : 10;
    const wordW = word ? measure(word, 10.5) : 0;
    entries.push({ kind, x: cx, y, markW, word: word || null, wordX: cx + markW + 5 });
    cx += markW + 5 + wordW + 16;
  };
  add('member', words.member);
  add('chain', words.wallPlane);
  if (ticks) add('tick', words.part);
  return { entries, right: cx };
}
